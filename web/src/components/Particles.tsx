import { useEffect, useRef } from "react";
import { Camera, Geometry, Mesh, Program, Renderer } from "ogl";

interface ParticlesProps {
  particleCount?: number;
  particleSpread?: number;
  speed?: number;
  particleColors?: string[];
  moveParticlesOnHover?: boolean;
  particleHoverFactor?: number;
  alphaParticles?: boolean;
  particleBaseSize?: number;
  sizeRandomness?: number;
  cameraDistance?: number;
  disableRotation?: boolean;
  pixelRatio?: number;
  className?: string;
}

const DEFAULT_COLORS = ["#ffffff"];
const vertex = `
attribute vec3 position;
attribute vec4 random;
attribute vec3 color;
uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;
uniform float uSpread;
uniform float uBaseSize;
uniform float uSizeRandomness;
varying vec4 vRandom;
varying vec3 vColor;
void main() {
  vRandom = random;
  vColor = color;
  vec3 pos = position * uSpread;
  pos.z *= 10.0;
  vec4 mPos = modelMatrix * vec4(pos, 1.0);
  mPos.x += sin(uTime * random.z + 6.28 * random.w) * mix(0.1, 1.5, random.x);
  mPos.y += sin(uTime * random.y + 6.28 * random.x) * mix(0.1, 1.5, random.w);
  mPos.z += sin(uTime * random.w + 6.28 * random.y) * mix(0.1, 1.5, random.z);
  vec4 mvPos = viewMatrix * mPos;
  gl_PointSize = uSizeRandomness == 0.0 ? uBaseSize : (uBaseSize * (1.0 + uSizeRandomness * (random.x - 0.5))) / length(mvPos.xyz);
  gl_Position = projectionMatrix * mvPos;
}`;
const fragment = `
precision highp float;
uniform float uTime;
uniform float uAlphaParticles;
varying vec4 vRandom;
varying vec3 vColor;
void main() {
  vec2 uv = gl_PointCoord.xy;
  float d = length(uv - vec2(0.5));
  if (uAlphaParticles < 0.5 && d > 0.5) discard;
  float alpha = uAlphaParticles < 0.5 ? 1.0 : smoothstep(0.5, 0.4, d) * 0.8;
  gl_FragColor = vec4(vColor + 0.2 * sin(uv.yxx + uTime + vRandom.y * 6.28), alpha);
}`;

const hexToRgb = (hex: string): [number, number, number] => {
  const value = hex.replace(/^#/, "");
  const normalized = value.length === 3 ? [...value].map((char) => char + char).join("") : value;
  const color = Number.parseInt(normalized.slice(0, 6), 16);
  return [((color >> 16) & 255) / 255, ((color >> 8) & 255) / 255, (color & 255) / 255];
};

export function Particles({
  particleCount = 200,
  particleSpread = 10,
  speed = 0.1,
  particleColors = DEFAULT_COLORS,
  moveParticlesOnHover = false,
    particleHoverFactor = 1,
    alphaParticles = false,
    particleBaseSize = 100,
  sizeRandomness = 1,
  cameraDistance = 20,
  disableRotation = false,
  pixelRatio = 1,
  className = "",
}: ParticlesProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const colorsKey = particleColors.join(",");

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let renderer: Renderer;
    try {
      renderer = new Renderer({ dpr: pixelRatio, depth: false, alpha: true, antialias: true });
    } catch {
      return;
    }
    const gl = renderer.gl;
    const canvas = gl.canvas;
    container.appendChild(canvas);
    gl.clearColor(0, 0, 0, 0);

    const camera = new Camera(gl, { fov: 15 });
    camera.position.set(0, 0, cameraDistance);
    const resize = () => {
      const width = container.clientWidth;
      const height = container.clientHeight;
      if (!width || !height) return;
      renderer.setSize(width, height);
      camera.perspective({ aspect: canvas.width / Math.max(1, canvas.height) });
    };
    const observer = new ResizeObserver(resize);
    observer.observe(container);
    resize();
    const mouse = { x: 0, y: 0 };
    const onPointerMove = (event: PointerEvent) => {
      const bounds = container.getBoundingClientRect();
      mouse.x = ((event.clientX - bounds.left) / Math.max(1, bounds.width)) * 2 - 1;
      mouse.y = -(((event.clientY - bounds.top) / Math.max(1, bounds.height)) * 2 - 1);
    };
    if (moveParticlesOnHover) container.addEventListener("pointermove", onPointerMove);

    const count = Math.max(1, Math.min(1000, Math.floor(particleCount)));
    const positions = new Float32Array(count * 3);
    const randoms = new Float32Array(count * 4);
    const colors = new Float32Array(count * 3);
    const palette = particleColors.length ? particleColors : DEFAULT_COLORS;
    for (let i = 0; i < count; i++) {
      let x = 0, y = 0, z = 0, length = 0;
      do {
        x = Math.random() * 2 - 1;
        y = Math.random() * 2 - 1;
        z = Math.random() * 2 - 1;
        length = x * x + y * y + z * z;
      } while (length > 1 || length === 0);
      const radius = Math.cbrt(Math.random());
      positions.set([x * radius, y * radius, z * radius], i * 3);
      randoms.set([Math.random(), Math.random(), Math.random(), Math.random()], i * 4);
      colors.set(hexToRgb(palette[Math.floor(Math.random() * palette.length)]), i * 3);
    }

    const geometry = new Geometry(gl, {
      position: { size: 3, data: positions },
      random: { size: 4, data: randoms },
      color: { size: 3, data: colors },
    });
    const program = new Program(gl, {
      vertex,
      fragment,
      uniforms: {
        uTime: { value: 0 },
        uSpread: { value: particleSpread },
        uBaseSize: { value: particleBaseSize * pixelRatio },
        uSizeRandomness: { value: sizeRandomness },
        uAlphaParticles: { value: alphaParticles ? 1 : 0 },
      },
      transparent: true,
      depthTest: false,
      depthWrite: false,
    });
    const particles = new Mesh(gl, { mode: gl.POINTS, geometry, program });
    let frame = 0;
    let lastTime = 0;
    let elapsed = 0;
    let visible = true;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const intersection = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible && !frame) frame = requestAnimationFrame(update);
      if (!visible && frame) cancelAnimationFrame(frame);
      if (!visible) frame = 0;
    });
    intersection.observe(container);

    const update = (time: number) => {
      frame = 0;
      if (!visible || document.hidden) return;
      const delta = lastTime ? time - lastTime : 16;
      lastTime = time;
      if (!reducedMotion.matches) elapsed += delta * speed;
      program.uniforms.uTime.value = elapsed * 0.001;
      if (moveParticlesOnHover) {
        particles.position.x = -mouse.x * particleHoverFactor;
        particles.position.y = -mouse.y * particleHoverFactor;
      }
      if (!disableRotation && !reducedMotion.matches) {
        particles.rotation.x = Math.sin(elapsed * 0.0002) * 0.1;
        particles.rotation.y = Math.cos(elapsed * 0.0005) * 0.15;
        particles.rotation.z += 0.01 * speed;
      }
      renderer.render({ scene: particles, camera });
      if (!reducedMotion.matches) frame = requestAnimationFrame(update);
    };
    const onVisibility = () => {
      if (!document.hidden && visible && !frame) frame = requestAnimationFrame(update);
      if (document.hidden && frame) cancelAnimationFrame(frame);
      if (document.hidden) frame = 0;
    };
    document.addEventListener("visibilitychange", onVisibility);
    frame = requestAnimationFrame(update);

    return () => {
      if (frame) cancelAnimationFrame(frame);
      observer.disconnect();
      intersection.disconnect();
      document.removeEventListener("visibilitychange", onVisibility);
      if (moveParticlesOnHover) container.removeEventListener("pointermove", onPointerMove);
      geometry.remove();
      program.remove();
      canvas.remove();
      gl.getExtension("WEBGL_lose_context")?.loseContext();
    };
  }, [particleCount, particleSpread, speed, colorsKey, moveParticlesOnHover, particleHoverFactor, alphaParticles, particleBaseSize, sizeRandomness, cameraDistance, disableRotation, pixelRatio]);

  return <div ref={containerRef} className={`ambient-effect-canvas ${className}`} aria-hidden="true" />;
}
