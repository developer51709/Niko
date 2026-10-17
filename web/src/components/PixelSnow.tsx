import { useEffect, useRef, useState, type HTMLAttributes } from "react";

export type PixelSnowVariant = "snowflake" | "square" | "round";
export interface PixelSnowProps extends HTMLAttributes<HTMLDivElement> {
  color?: string;
  variant?: PixelSnowVariant;
  density?: number;
  speed?: number;
  wind?: number;
  sway?: number;
  flakeSize?: number;
  pixelSize?: number;
  depth?: number;
  brightness?: number;
  glow?: number;
  twinkle?: number;
  accumulate?: boolean;
  mouseInteraction?: boolean;
  intro?: boolean;
  fade?: number;
  opacity?: number;
  lightMode?: boolean;
  paused?: boolean;
  dpr?: number;
}

const vertex = `#version 300 es
in vec2 aPosition;
void main(){gl_Position=vec4(aPosition,0.0,1.0);}`;
const fragment = `#version 300 es
precision highp float;
uniform vec2 uResolution;
uniform float uTime;
uniform vec3 uColor;
uniform float uPixel;
uniform float uOpacity;
uniform float uDensity;
uniform float uWind;
uniform float uSway;
uniform float uGlow;
uniform float uTwinkle;
out vec4 outColor;
float hash(vec2 p){p=fract(p*vec2(123.34,456.21));p+=dot(p,p+45.32);return fract(p.x*p.y);}
void main(){
  vec2 p=gl_FragCoord.xy;
  float cellSize=max(1.0,uPixel);
  vec2 pixel=floor(p/cellSize);
  float columns=max(1.0,floor(uResolution.x/cellSize/9.0));
  float rows=max(1.0,floor(uResolution.y/cellSize/9.0));
  pixel.y+=uTime*4.0;
  pixel.x-=uTime*uWind*0.8+sin(uTime*0.7+pixel.y*0.03)*uSway;
  vec2 tile=floor(pixel/9.0);
  vec2 local=mod(pixel,9.0);
  vec2 drifted=vec2(mod(tile.x,columns),mod(tile.y,rows));
  float visible=step(hash(floor(drifted)),uDensity);
  float row=floor(local.y);
  float col=floor(local.x);
  float on=0.0;
  if(row==0.0||row==8.0) on=step(abs(col-4.0),0.1);
  else if(row==1.0||row==7.0) on=max(step(abs(col-1.0),0.1),max(step(abs(col-4.0),0.1),step(abs(col-7.0),0.1)));
  else if(row==2.0||row==6.0) on=max(step(abs(col-2.0),0.1),max(step(abs(col-4.0),0.1),step(abs(col-6.0),0.1)));
  else if(row==3.0||row==5.0) on=max(step(abs(col-3.0),0.1),max(step(abs(col-4.0),0.1),step(abs(col-5.0),0.1)));
  else on=1.0;
  float seed=hash(drifted);
  float sparkle=1.0-uTwinkle+uTwinkle*(0.72+0.28*sin(uTime*2.0+seed*6.2831));
  float center=step(abs(col-4.0),0.1)*step(abs(row-4.0),0.1);
  float halo=exp(-length(local-vec2(4.0))*0.6)*uGlow*0.12;
  float alpha=clamp((on*sparkle+halo)*uOpacity*visible,0.0,0.95);
  vec3 color=mix(uColor,uColor*1.3,center*0.25);
  outColor=vec4(color*alpha,alpha);
}`;

function compile(gl: WebGL2RenderingContext, type: number, source: string) {
  const shader = gl.createShader(type);
  if (!shader) return null;
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    gl.deleteShader(shader);
    return null;
  }
  return shader;
}

export default function PixelSnow({
  color = "#ffffff",
  density = 0.5,
  speed = 1,
  wind = 0.25,
  sway = 0.5,
  flakeSize = 1,
  pixelSize = 3,
  depth = 0.6,
  brightness = 1,
  glow = 0.8,
  twinkle = 0.35,
  accumulate = false,
  mouseInteraction = true,
  intro = true,
  fade = 0,
  opacity = 1,
  lightMode = false,
  paused = false,
  dpr,
  variant = "snowflake",
  className = "",
  ...rest
}: PixelSnowProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [holidaySettings] = useState(() => ({ color, density, speed, wind, sway, flakeSize, pixelSize, depth, brightness, glow, twinkle, accumulate, mouseInteraction, intro, fade, opacity, lightMode, paused, dpr, variant }));
  const settingsRef = useRef(holidaySettings);
  settingsRef.current = { color, density, speed, wind, sway, flakeSize, pixelSize, depth, brightness, glow, twinkle, accumulate, mouseInteraction, intro, fade, opacity, lightMode, paused, dpr, variant };

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    const gl = canvas?.getContext("webgl2", { alpha: true, antialias: false, depth: false, premultipliedAlpha: true });
    if (!container || !canvas || !gl) return undefined;
    const vs = compile(gl, gl.VERTEX_SHADER, vertex);
    const fs = compile(gl, gl.FRAGMENT_SHADER, fragment);
    const program = gl.createProgram();
    if (!vs || !fs || !program) {
      if (vs) gl.deleteShader(vs);
      if (fs) gl.deleteShader(fs);
      if (program) gl.deleteProgram(program);
      return undefined;
    }
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    gl.deleteShader(vs);
    gl.deleteShader(fs);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      gl.deleteProgram(program);
      return undefined;
    }
    const buffer = gl.createBuffer();
    const vao = gl.createVertexArray();
    if (!buffer || !vao) {
      if (buffer) gl.deleteBuffer(buffer);
      if (vao) gl.deleteVertexArray(vao);
      gl.deleteProgram(program);
      return undefined;
    }
    gl.bindVertexArray(vao);
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const position = gl.getAttribLocation(program, "aPosition");
    gl.enableVertexAttribArray(position);
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
    const uniforms = {
      resolution: gl.getUniformLocation(program, "uResolution"),
      time: gl.getUniformLocation(program, "uTime"),
      color: gl.getUniformLocation(program, "uColor"),
      pixel: gl.getUniformLocation(program, "uPixel"),
      opacity: gl.getUniformLocation(program, "uOpacity"),
      density: gl.getUniformLocation(program, "uDensity"),
      wind: gl.getUniformLocation(program, "uWind"),
      sway: gl.getUniformLocation(program, "uSway"),
      glow: gl.getUniformLocation(program, "uGlow"),
      twinkle: gl.getUniformLocation(program, "uTwinkle"),
    };
    let ratio = 1;
    let raf = 0;
    let previous = 0;
    let elapsed = 0;
    let visible = true;
    const rgb = document.createElement("canvas").getContext("2d");
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const resize = () => {
      const settings = settingsRef.current;
      const width = Math.max(1, container.clientWidth);
      const height = Math.max(1, container.clientHeight);
      ratio = Math.min(settings.dpr || window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
      gl.viewport(0, 0, canvas.width, canvas.height);
      render(elapsed);
    };
    const render = (time: number) => {
      const settings = settingsRef.current;
      if (rgb) {
        rgb.fillStyle = settings.color;
        const value = rgb.fillStyle;
        const hex = value.startsWith("#") ? value.slice(1) : "ffffff";
        const colorValue = Number.parseInt(hex.length === 3 ? [...hex].map((part) => part + part).join("") : hex, 16);
        gl.useProgram(program);
        gl.bindVertexArray(vao);
        gl.uniform2f(uniforms.resolution, canvas.width, canvas.height);
        gl.uniform1f(uniforms.time, time);
        gl.uniform3f(uniforms.color, ((colorValue >> 16) & 255) / 255 * settings.brightness, ((colorValue >> 8) & 255) / 255 * settings.brightness, (colorValue & 255) / 255 * settings.brightness);
        gl.uniform1f(uniforms.pixel, Math.max(1, settings.pixelSize) * ratio * Math.max(0.5, settings.flakeSize));
        gl.uniform1f(uniforms.opacity, Math.max(0, Math.min(1, settings.opacity)));
        gl.uniform1f(uniforms.density, Math.max(0, Math.min(1, settings.density)));
        gl.uniform1f(uniforms.wind, settings.wind);
        gl.uniform1f(uniforms.sway, settings.sway);
        gl.uniform1f(uniforms.glow, settings.glow);
        gl.uniform1f(uniforms.twinkle, settings.twinkle);
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
        gl.clearColor(0, 0, 0, 0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      }
    };
    const tick = (now: number) => {
      raf = 0;
      if (!visible || document.hidden) return;
      const delta = previous ? Math.min(0.05, (now - previous) / 1000) : 1 / 60;
      previous = now;
      const settings = settingsRef.current;
      if (!reduceMotion.matches && !settings.paused) elapsed += delta * settings.speed;
      render(elapsed);
      if (!reduceMotion.matches && !settings.paused) raf = requestAnimationFrame(tick);
    };
    const wake = () => {
      if (!raf && visible && !document.hidden && !settingsRef.current.paused) raf = requestAnimationFrame(tick);
    };
    const resizeObserver = new ResizeObserver(resize);
    const intersection = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible) wake();
      else if (raf) cancelAnimationFrame(raf);
      if (!visible) raf = 0;
    });
    resizeObserver.observe(container);
    intersection.observe(container);
    const onVisibility = () => {
      previous = 0;
      if (document.hidden && raf) cancelAnimationFrame(raf);
      if (document.hidden) raf = 0;
      else wake();
    };
    document.addEventListener("visibilitychange", onVisibility);
    resize();
    wake();
    return () => {
      if (raf) cancelAnimationFrame(raf);
      resizeObserver.disconnect();
      intersection.disconnect();
      document.removeEventListener("visibilitychange", onVisibility);
      gl.deleteBuffer(buffer);
      gl.deleteVertexArray(vao);
      gl.deleteProgram(program);
      gl.getExtension("WEBGL_lose_context")?.loseContext();
    };
  }, []);

  return <div ref={containerRef} className={`ambient-effect-canvas ${className}`} aria-hidden="true" {...rest}><canvas ref={canvasRef} className="ambient-effect-canvas" /></div>;
}
