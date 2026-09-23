var qv=Object.defineProperty;var Qv=(t,s,i)=>s in t?qv(t,s,{enumerable:!0,configurable:!0,writable:!0,value:i}):t[s]=i;var dm=(t,s,i)=>Qv(t,typeof s!="symbol"?s+"":s,i);(function(){const s=document.createElement("link").relList;if(s&&s.supports&&s.supports("modulepreload"))return;for(const c of document.querySelectorAll('link[rel="modulepreload"]'))o(c);new MutationObserver(c=>{for(const d of c)if(d.type==="childList")for(const h of d.addedNodes)h.tagName==="LINK"&&h.rel==="modulepreload"&&o(h)}).observe(document,{childList:!0,subtree:!0});function i(c){const d={};return c.integrity&&(d.integrity=c.integrity),c.referrerPolicy&&(d.referrerPolicy=c.referrerPolicy),c.crossOrigin==="use-credentials"?d.credentials="include":c.crossOrigin==="anonymous"?d.credentials="omit":d.credentials="same-origin",d}function o(c){if(c.ep)return;c.ep=!0;const d=i(c);fetch(c.href,d)}})();var Rl={exports:{}},jr={},Ll={exports:{}},ue={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var hm;function Jv(){if(hm)return ue;hm=1;var t=Symbol.for("react.element"),s=Symbol.for("react.portal"),i=Symbol.for("react.fragment"),o=Symbol.for("react.strict_mode"),c=Symbol.for("react.profiler"),d=Symbol.for("react.provider"),h=Symbol.for("react.context"),f=Symbol.for("react.forward_ref"),p=Symbol.for("react.suspense"),v=Symbol.for("react.memo"),g=Symbol.for("react.lazy"),x=Symbol.iterator;function w(E){return E===null||typeof E!="object"?null:(E=x&&E[x]||E["@@iterator"],typeof E=="function"?E:null)}var k={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},S=Object.assign,j={};function N(E,z,ce){this.props=E,this.context=z,this.refs=j,this.updater=ce||k}N.prototype.isReactComponent={},N.prototype.setState=function(E,z){if(typeof E!="object"&&typeof E!="function"&&E!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,E,z,"setState")},N.prototype.forceUpdate=function(E){this.updater.enqueueForceUpdate(this,E,"forceUpdate")};function B(){}B.prototype=N.prototype;function M(E,z,ce){this.props=E,this.context=z,this.refs=j,this.updater=ce||k}var L=M.prototype=new B;L.constructor=M,S(L,N.prototype),L.isPureReactComponent=!0;var I=Array.isArray,D=Object.prototype.hasOwnProperty,F={current:null},V={key:!0,ref:!0,__self:!0,__source:!0};function O(E,z,ce){var de,fe={},pe=null,Ne=null;if(z!=null)for(de in z.ref!==void 0&&(Ne=z.ref),z.key!==void 0&&(pe=""+z.key),z)D.call(z,de)&&!V.hasOwnProperty(de)&&(fe[de]=z[de]);var we=arguments.length-2;if(we===1)fe.children=ce;else if(1<we){for(var Ee=Array(we),yt=0;yt<we;yt++)Ee[yt]=arguments[yt+2];fe.children=Ee}if(E&&E.defaultProps)for(de in we=E.defaultProps,we)fe[de]===void 0&&(fe[de]=we[de]);return{$$typeof:t,type:E,key:pe,ref:Ne,props:fe,_owner:F.current}}function oe(E,z){return{$$typeof:t,type:E.type,key:z,ref:E.ref,props:E.props,_owner:E._owner}}function le(E){return typeof E=="object"&&E!==null&&E.$$typeof===t}function xe(E){var z={"=":"=0",":":"=2"};return"$"+E.replace(/[=:]/g,function(ce){return z[ce]})}var se=/\/+/g;function ne(E,z){return typeof E=="object"&&E!==null&&E.key!=null?xe(""+E.key):z.toString(36)}function Se(E,z,ce,de,fe){var pe=typeof E;(pe==="undefined"||pe==="boolean")&&(E=null);var Ne=!1;if(E===null)Ne=!0;else switch(pe){case"string":case"number":Ne=!0;break;case"object":switch(E.$$typeof){case t:case s:Ne=!0}}if(Ne)return Ne=E,fe=fe(Ne),E=de===""?"."+ne(Ne,0):de,I(fe)?(ce="",E!=null&&(ce=E.replace(se,"$&/")+"/"),Se(fe,z,ce,"",function(yt){return yt})):fe!=null&&(le(fe)&&(fe=oe(fe,ce+(!fe.key||Ne&&Ne.key===fe.key?"":(""+fe.key).replace(se,"$&/")+"/")+E)),z.push(fe)),1;if(Ne=0,de=de===""?".":de+":",I(E))for(var we=0;we<E.length;we++){pe=E[we];var Ee=de+ne(pe,we);Ne+=Se(pe,z,ce,Ee,fe)}else if(Ee=w(E),typeof Ee=="function")for(E=Ee.call(E),we=0;!(pe=E.next()).done;)pe=pe.value,Ee=de+ne(pe,we++),Ne+=Se(pe,z,ce,Ee,fe);else if(pe==="object")throw z=String(E),Error("Objects are not valid as a React child (found: "+(z==="[object Object]"?"object with keys {"+Object.keys(E).join(", ")+"}":z)+"). If you meant to render a collection of children, use an array instead.");return Ne}function Le(E,z,ce){if(E==null)return E;var de=[],fe=0;return Se(E,de,"","",function(pe){return z.call(ce,pe,fe++)}),de}function Ie(E){if(E._status===-1){var z=E._result;z=z(),z.then(function(ce){(E._status===0||E._status===-1)&&(E._status=1,E._result=ce)},function(ce){(E._status===0||E._status===-1)&&(E._status=2,E._result=ce)}),E._status===-1&&(E._status=0,E._result=z)}if(E._status===1)return E._result.default;throw E._result}var ye={current:null},H={transition:null},J={ReactCurrentDispatcher:ye,ReactCurrentBatchConfig:H,ReactCurrentOwner:F};function K(){throw Error("act(...) is not supported in production builds of React.")}return ue.Children={map:Le,forEach:function(E,z,ce){Le(E,function(){z.apply(this,arguments)},ce)},count:function(E){var z=0;return Le(E,function(){z++}),z},toArray:function(E){return Le(E,function(z){return z})||[]},only:function(E){if(!le(E))throw Error("React.Children.only expected to receive a single React element child.");return E}},ue.Component=N,ue.Fragment=i,ue.Profiler=c,ue.PureComponent=M,ue.StrictMode=o,ue.Suspense=p,ue.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=J,ue.act=K,ue.cloneElement=function(E,z,ce){if(E==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+E+".");var de=S({},E.props),fe=E.key,pe=E.ref,Ne=E._owner;if(z!=null){if(z.ref!==void 0&&(pe=z.ref,Ne=F.current),z.key!==void 0&&(fe=""+z.key),E.type&&E.type.defaultProps)var we=E.type.defaultProps;for(Ee in z)D.call(z,Ee)&&!V.hasOwnProperty(Ee)&&(de[Ee]=z[Ee]===void 0&&we!==void 0?we[Ee]:z[Ee])}var Ee=arguments.length-2;if(Ee===1)de.children=ce;else if(1<Ee){we=Array(Ee);for(var yt=0;yt<Ee;yt++)we[yt]=arguments[yt+2];de.children=we}return{$$typeof:t,type:E.type,key:fe,ref:pe,props:de,_owner:Ne}},ue.createContext=function(E){return E={$$typeof:h,_currentValue:E,_currentValue2:E,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},E.Provider={$$typeof:d,_context:E},E.Consumer=E},ue.createElement=O,ue.createFactory=function(E){var z=O.bind(null,E);return z.type=E,z},ue.createRef=function(){return{current:null}},ue.forwardRef=function(E){return{$$typeof:f,render:E}},ue.isValidElement=le,ue.lazy=function(E){return{$$typeof:g,_payload:{_status:-1,_result:E},_init:Ie}},ue.memo=function(E,z){return{$$typeof:v,type:E,compare:z===void 0?null:z}},ue.startTransition=function(E){var z=H.transition;H.transition={};try{E()}finally{H.transition=z}},ue.unstable_act=K,ue.useCallback=function(E,z){return ye.current.useCallback(E,z)},ue.useContext=function(E){return ye.current.useContext(E)},ue.useDebugValue=function(){},ue.useDeferredValue=function(E){return ye.current.useDeferredValue(E)},ue.useEffect=function(E,z){return ye.current.useEffect(E,z)},ue.useId=function(){return ye.current.useId()},ue.useImperativeHandle=function(E,z,ce){return ye.current.useImperativeHandle(E,z,ce)},ue.useInsertionEffect=function(E,z){return ye.current.useInsertionEffect(E,z)},ue.useLayoutEffect=function(E,z){return ye.current.useLayoutEffect(E,z)},ue.useMemo=function(E,z){return ye.current.useMemo(E,z)},ue.useReducer=function(E,z,ce){return ye.current.useReducer(E,z,ce)},ue.useRef=function(E){return ye.current.useRef(E)},ue.useState=function(E){return ye.current.useState(E)},ue.useSyncExternalStore=function(E,z,ce){return ye.current.useSyncExternalStore(E,z,ce)},ue.useTransition=function(){return ye.current.useTransition()},ue.version="18.3.1",ue}var mm;function Bc(){return mm||(mm=1,Ll.exports=Jv()),Ll.exports}/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var fm;function Zv(){if(fm)return jr;fm=1;var t=Bc(),s=Symbol.for("react.element"),i=Symbol.for("react.fragment"),o=Object.prototype.hasOwnProperty,c=t.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,d={key:!0,ref:!0,__self:!0,__source:!0};function h(f,p,v){var g,x={},w=null,k=null;v!==void 0&&(w=""+v),p.key!==void 0&&(w=""+p.key),p.ref!==void 0&&(k=p.ref);for(g in p)o.call(p,g)&&!d.hasOwnProperty(g)&&(x[g]=p[g]);if(f&&f.defaultProps)for(g in p=f.defaultProps,p)x[g]===void 0&&(x[g]=p[g]);return{$$typeof:s,type:f,key:w,ref:k,props:x,_owner:c.current}}return jr.Fragment=i,jr.jsx=h,jr.jsxs=h,jr}var pm;function ex(){return pm||(pm=1,Rl.exports=Zv()),Rl.exports}var r=ex(),P=Bc(),Yi={},Il={exports:{}},pt={},Vl={exports:{}},Fl={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var gm;function tx(){return gm||(gm=1,(function(t){function s(H,J){var K=H.length;H.push(J);e:for(;0<K;){var E=K-1>>>1,z=H[E];if(0<c(z,J))H[E]=J,H[K]=z,K=E;else break e}}function i(H){return H.length===0?null:H[0]}function o(H){if(H.length===0)return null;var J=H[0],K=H.pop();if(K!==J){H[0]=K;e:for(var E=0,z=H.length,ce=z>>>1;E<ce;){var de=2*(E+1)-1,fe=H[de],pe=de+1,Ne=H[pe];if(0>c(fe,K))pe<z&&0>c(Ne,fe)?(H[E]=Ne,H[pe]=K,E=pe):(H[E]=fe,H[de]=K,E=de);else if(pe<z&&0>c(Ne,K))H[E]=Ne,H[pe]=K,E=pe;else break e}}return J}function c(H,J){var K=H.sortIndex-J.sortIndex;return K!==0?K:H.id-J.id}if(typeof performance=="object"&&typeof performance.now=="function"){var d=performance;t.unstable_now=function(){return d.now()}}else{var h=Date,f=h.now();t.unstable_now=function(){return h.now()-f}}var p=[],v=[],g=1,x=null,w=3,k=!1,S=!1,j=!1,N=typeof setTimeout=="function"?setTimeout:null,B=typeof clearTimeout=="function"?clearTimeout:null,M=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function L(H){for(var J=i(v);J!==null;){if(J.callback===null)o(v);else if(J.startTime<=H)o(v),J.sortIndex=J.expirationTime,s(p,J);else break;J=i(v)}}function I(H){if(j=!1,L(H),!S)if(i(p)!==null)S=!0,Ie(D);else{var J=i(v);J!==null&&ye(I,J.startTime-H)}}function D(H,J){S=!1,j&&(j=!1,B(O),O=-1),k=!0;var K=w;try{for(L(J),x=i(p);x!==null&&(!(x.expirationTime>J)||H&&!xe());){var E=x.callback;if(typeof E=="function"){x.callback=null,w=x.priorityLevel;var z=E(x.expirationTime<=J);J=t.unstable_now(),typeof z=="function"?x.callback=z:x===i(p)&&o(p),L(J)}else o(p);x=i(p)}if(x!==null)var ce=!0;else{var de=i(v);de!==null&&ye(I,de.startTime-J),ce=!1}return ce}finally{x=null,w=K,k=!1}}var F=!1,V=null,O=-1,oe=5,le=-1;function xe(){return!(t.unstable_now()-le<oe)}function se(){if(V!==null){var H=t.unstable_now();le=H;var J=!0;try{J=V(!0,H)}finally{J?ne():(F=!1,V=null)}}else F=!1}var ne;if(typeof M=="function")ne=function(){M(se)};else if(typeof MessageChannel<"u"){var Se=new MessageChannel,Le=Se.port2;Se.port1.onmessage=se,ne=function(){Le.postMessage(null)}}else ne=function(){N(se,0)};function Ie(H){V=H,F||(F=!0,ne())}function ye(H,J){O=N(function(){H(t.unstable_now())},J)}t.unstable_IdlePriority=5,t.unstable_ImmediatePriority=1,t.unstable_LowPriority=4,t.unstable_NormalPriority=3,t.unstable_Profiling=null,t.unstable_UserBlockingPriority=2,t.unstable_cancelCallback=function(H){H.callback=null},t.unstable_continueExecution=function(){S||k||(S=!0,Ie(D))},t.unstable_forceFrameRate=function(H){0>H||125<H?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):oe=0<H?Math.floor(1e3/H):5},t.unstable_getCurrentPriorityLevel=function(){return w},t.unstable_getFirstCallbackNode=function(){return i(p)},t.unstable_next=function(H){switch(w){case 1:case 2:case 3:var J=3;break;default:J=w}var K=w;w=J;try{return H()}finally{w=K}},t.unstable_pauseExecution=function(){},t.unstable_requestPaint=function(){},t.unstable_runWithPriority=function(H,J){switch(H){case 1:case 2:case 3:case 4:case 5:break;default:H=3}var K=w;w=H;try{return J()}finally{w=K}},t.unstable_scheduleCallback=function(H,J,K){var E=t.unstable_now();switch(typeof K=="object"&&K!==null?(K=K.delay,K=typeof K=="number"&&0<K?E+K:E):K=E,H){case 1:var z=-1;break;case 2:z=250;break;case 5:z=1073741823;break;case 4:z=1e4;break;default:z=5e3}return z=K+z,H={id:g++,callback:J,priorityLevel:H,startTime:K,expirationTime:z,sortIndex:-1},K>E?(H.sortIndex=K,s(v,H),i(p)===null&&H===i(v)&&(j?(B(O),O=-1):j=!0,ye(I,K-E))):(H.sortIndex=z,s(p,H),S||k||(S=!0,Ie(D))),H},t.unstable_shouldYield=xe,t.unstable_wrapCallback=function(H){var J=w;return function(){var K=w;w=J;try{return H.apply(this,arguments)}finally{w=K}}}})(Fl)),Fl}var ym;function nx(){return ym||(ym=1,Vl.exports=tx()),Vl.exports}/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var vm;function sx(){if(vm)return pt;vm=1;var t=Bc(),s=nx();function i(e){for(var n="https://reactjs.org/docs/error-decoder.html?invariant="+e,a=1;a<arguments.length;a++)n+="&args[]="+encodeURIComponent(arguments[a]);return"Minified React error #"+e+"; visit "+n+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var o=new Set,c={};function d(e,n){h(e,n),h(e+"Capture",n)}function h(e,n){for(c[e]=n,e=0;e<n.length;e++)o.add(n[e])}var f=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),p=Object.prototype.hasOwnProperty,v=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,g={},x={};function w(e){return p.call(x,e)?!0:p.call(g,e)?!1:v.test(e)?x[e]=!0:(g[e]=!0,!1)}function k(e,n,a,l){if(a!==null&&a.type===0)return!1;switch(typeof n){case"function":case"symbol":return!0;case"boolean":return l?!1:a!==null?!a.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function S(e,n,a,l){if(n===null||typeof n>"u"||k(e,n,a,l))return!0;if(l)return!1;if(a!==null)switch(a.type){case 3:return!n;case 4:return n===!1;case 5:return isNaN(n);case 6:return isNaN(n)||1>n}return!1}function j(e,n,a,l,u,m,y){this.acceptsBooleans=n===2||n===3||n===4,this.attributeName=l,this.attributeNamespace=u,this.mustUseProperty=a,this.propertyName=e,this.type=n,this.sanitizeURL=m,this.removeEmptyString=y}var N={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){N[e]=new j(e,0,!1,e,null,!1,!1)}),[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var n=e[0];N[n]=new j(n,1,!1,e[1],null,!1,!1)}),["contentEditable","draggable","spellCheck","value"].forEach(function(e){N[e]=new j(e,2,!1,e.toLowerCase(),null,!1,!1)}),["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){N[e]=new j(e,2,!1,e,null,!1,!1)}),"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){N[e]=new j(e,3,!1,e.toLowerCase(),null,!1,!1)}),["checked","multiple","muted","selected"].forEach(function(e){N[e]=new j(e,3,!0,e,null,!1,!1)}),["capture","download"].forEach(function(e){N[e]=new j(e,4,!1,e,null,!1,!1)}),["cols","rows","size","span"].forEach(function(e){N[e]=new j(e,6,!1,e,null,!1,!1)}),["rowSpan","start"].forEach(function(e){N[e]=new j(e,5,!1,e.toLowerCase(),null,!1,!1)});var B=/[\-:]([a-z])/g;function M(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var n=e.replace(B,M);N[n]=new j(n,1,!1,e,null,!1,!1)}),"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var n=e.replace(B,M);N[n]=new j(n,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)}),["xml:base","xml:lang","xml:space"].forEach(function(e){var n=e.replace(B,M);N[n]=new j(n,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)}),["tabIndex","crossOrigin"].forEach(function(e){N[e]=new j(e,1,!1,e.toLowerCase(),null,!1,!1)}),N.xlinkHref=new j("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1),["src","href","action","formAction"].forEach(function(e){N[e]=new j(e,1,!1,e.toLowerCase(),null,!0,!0)});function L(e,n,a,l){var u=N.hasOwnProperty(n)?N[n]:null;(u!==null?u.type!==0:l||!(2<n.length)||n[0]!=="o"&&n[0]!=="O"||n[1]!=="n"&&n[1]!=="N")&&(S(n,a,u,l)&&(a=null),l||u===null?w(n)&&(a===null?e.removeAttribute(n):e.setAttribute(n,""+a)):u.mustUseProperty?e[u.propertyName]=a===null?u.type===3?!1:"":a:(n=u.attributeName,l=u.attributeNamespace,a===null?e.removeAttribute(n):(u=u.type,a=u===3||u===4&&a===!0?"":""+a,l?e.setAttributeNS(l,n,a):e.setAttribute(n,a))))}var I=t.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,D=Symbol.for("react.element"),F=Symbol.for("react.portal"),V=Symbol.for("react.fragment"),O=Symbol.for("react.strict_mode"),oe=Symbol.for("react.profiler"),le=Symbol.for("react.provider"),xe=Symbol.for("react.context"),se=Symbol.for("react.forward_ref"),ne=Symbol.for("react.suspense"),Se=Symbol.for("react.suspense_list"),Le=Symbol.for("react.memo"),Ie=Symbol.for("react.lazy"),ye=Symbol.for("react.offscreen"),H=Symbol.iterator;function J(e){return e===null||typeof e!="object"?null:(e=H&&e[H]||e["@@iterator"],typeof e=="function"?e:null)}var K=Object.assign,E;function z(e){if(E===void 0)try{throw Error()}catch(a){var n=a.stack.trim().match(/\n( *(at )?)/);E=n&&n[1]||""}return`
`+E+e}var ce=!1;function de(e,n){if(!e||ce)return"";ce=!0;var a=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(n)if(n=function(){throw Error()},Object.defineProperty(n.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(n,[])}catch(R){var l=R}Reflect.construct(e,[],n)}else{try{n.call()}catch(R){l=R}e.call(n.prototype)}else{try{throw Error()}catch(R){l=R}e()}}catch(R){if(R&&l&&typeof R.stack=="string"){for(var u=R.stack.split(`
`),m=l.stack.split(`
`),y=u.length-1,b=m.length-1;1<=y&&0<=b&&u[y]!==m[b];)b--;for(;1<=y&&0<=b;y--,b--)if(u[y]!==m[b]){if(y!==1||b!==1)do if(y--,b--,0>b||u[y]!==m[b]){var C=`
`+u[y].replace(" at new "," at ");return e.displayName&&C.includes("<anonymous>")&&(C=C.replace("<anonymous>",e.displayName)),C}while(1<=y&&0<=b);break}}}finally{ce=!1,Error.prepareStackTrace=a}return(e=e?e.displayName||e.name:"")?z(e):""}function fe(e){switch(e.tag){case 5:return z(e.type);case 16:return z("Lazy");case 13:return z("Suspense");case 19:return z("SuspenseList");case 0:case 2:case 15:return e=de(e.type,!1),e;case 11:return e=de(e.type.render,!1),e;case 1:return e=de(e.type,!0),e;default:return""}}function pe(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case V:return"Fragment";case F:return"Portal";case oe:return"Profiler";case O:return"StrictMode";case ne:return"Suspense";case Se:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case xe:return(e.displayName||"Context")+".Consumer";case le:return(e._context.displayName||"Context")+".Provider";case se:var n=e.render;return e=e.displayName,e||(e=n.displayName||n.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case Le:return n=e.displayName||null,n!==null?n:pe(e.type)||"Memo";case Ie:n=e._payload,e=e._init;try{return pe(e(n))}catch{}}return null}function Ne(e){var n=e.type;switch(e.tag){case 24:return"Cache";case 9:return(n.displayName||"Context")+".Consumer";case 10:return(n._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=n.render,e=e.displayName||e.name||"",n.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return n;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return pe(n);case 8:return n===O?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof n=="function")return n.displayName||n.name||null;if(typeof n=="string")return n}return null}function we(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function Ee(e){var n=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(n==="checkbox"||n==="radio")}function yt(e){var n=Ee(e)?"checked":"value",a=Object.getOwnPropertyDescriptor(e.constructor.prototype,n),l=""+e[n];if(!e.hasOwnProperty(n)&&typeof a<"u"&&typeof a.get=="function"&&typeof a.set=="function"){var u=a.get,m=a.set;return Object.defineProperty(e,n,{configurable:!0,get:function(){return u.call(this)},set:function(y){l=""+y,m.call(this,y)}}),Object.defineProperty(e,n,{enumerable:a.enumerable}),{getValue:function(){return l},setValue:function(y){l=""+y},stopTracking:function(){e._valueTracker=null,delete e[n]}}}}function Br(e){e._valueTracker||(e._valueTracker=yt(e))}function yu(e){if(!e)return!1;var n=e._valueTracker;if(!n)return!0;var a=n.getValue(),l="";return e&&(l=Ee(e)?e.checked?"true":"false":e.value),e=l,e!==a?(n.setValue(e),!0):!1}function Or(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function Oa(e,n){var a=n.checked;return K({},n,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:a??e._wrapperState.initialChecked})}function vu(e,n){var a=n.defaultValue==null?"":n.defaultValue,l=n.checked!=null?n.checked:n.defaultChecked;a=we(n.value!=null?n.value:a),e._wrapperState={initialChecked:l,initialValue:a,controlled:n.type==="checkbox"||n.type==="radio"?n.checked!=null:n.value!=null}}function xu(e,n){n=n.checked,n!=null&&L(e,"checked",n,!1)}function za(e,n){xu(e,n);var a=we(n.value),l=n.type;if(a!=null)l==="number"?(a===0&&e.value===""||e.value!=a)&&(e.value=""+a):e.value!==""+a&&(e.value=""+a);else if(l==="submit"||l==="reset"){e.removeAttribute("value");return}n.hasOwnProperty("value")?Ua(e,n.type,a):n.hasOwnProperty("defaultValue")&&Ua(e,n.type,we(n.defaultValue)),n.checked==null&&n.defaultChecked!=null&&(e.defaultChecked=!!n.defaultChecked)}function wu(e,n,a){if(n.hasOwnProperty("value")||n.hasOwnProperty("defaultValue")){var l=n.type;if(!(l!=="submit"&&l!=="reset"||n.value!==void 0&&n.value!==null))return;n=""+e._wrapperState.initialValue,a||n===e.value||(e.value=n),e.defaultValue=n}a=e.name,a!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,a!==""&&(e.name=a)}function Ua(e,n,a){(n!=="number"||Or(e.ownerDocument)!==e)&&(a==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+a&&(e.defaultValue=""+a))}var Fs=Array.isArray;function ss(e,n,a,l){if(e=e.options,n){n={};for(var u=0;u<a.length;u++)n["$"+a[u]]=!0;for(a=0;a<e.length;a++)u=n.hasOwnProperty("$"+e[a].value),e[a].selected!==u&&(e[a].selected=u),u&&l&&(e[a].defaultSelected=!0)}else{for(a=""+we(a),n=null,u=0;u<e.length;u++){if(e[u].value===a){e[u].selected=!0,l&&(e[u].defaultSelected=!0);return}n!==null||e[u].disabled||(n=e[u])}n!==null&&(n.selected=!0)}}function Wa(e,n){if(n.dangerouslySetInnerHTML!=null)throw Error(i(91));return K({},n,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function bu(e,n){var a=n.value;if(a==null){if(a=n.children,n=n.defaultValue,a!=null){if(n!=null)throw Error(i(92));if(Fs(a)){if(1<a.length)throw Error(i(93));a=a[0]}n=a}n==null&&(n=""),a=n}e._wrapperState={initialValue:we(a)}}function ku(e,n){var a=we(n.value),l=we(n.defaultValue);a!=null&&(a=""+a,a!==e.value&&(e.value=a),n.defaultValue==null&&e.defaultValue!==a&&(e.defaultValue=a)),l!=null&&(e.defaultValue=""+l)}function ju(e){var n=e.textContent;n===e._wrapperState.initialValue&&n!==""&&n!==null&&(e.value=n)}function Su(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function $a(e,n){return e==null||e==="http://www.w3.org/1999/xhtml"?Su(n):e==="http://www.w3.org/2000/svg"&&n==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var zr,Nu=(function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(n,a,l,u){MSApp.execUnsafeLocalFunction(function(){return e(n,a,l,u)})}:e})(function(e,n){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=n;else{for(zr=zr||document.createElement("div"),zr.innerHTML="<svg>"+n.valueOf().toString()+"</svg>",n=zr.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;n.firstChild;)e.appendChild(n.firstChild)}});function Bs(e,n){if(n){var a=e.firstChild;if(a&&a===e.lastChild&&a.nodeType===3){a.nodeValue=n;return}}e.textContent=n}var Os={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},ey=["Webkit","ms","Moz","O"];Object.keys(Os).forEach(function(e){ey.forEach(function(n){n=n+e.charAt(0).toUpperCase()+e.substring(1),Os[n]=Os[e]})});function Cu(e,n,a){return n==null||typeof n=="boolean"||n===""?"":a||typeof n!="number"||n===0||Os.hasOwnProperty(e)&&Os[e]?(""+n).trim():n+"px"}function Tu(e,n){e=e.style;for(var a in n)if(n.hasOwnProperty(a)){var l=a.indexOf("--")===0,u=Cu(a,n[a],l);a==="float"&&(a="cssFloat"),l?e.setProperty(a,u):e[a]=u}}var ty=K({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function Ha(e,n){if(n){if(ty[e]&&(n.children!=null||n.dangerouslySetInnerHTML!=null))throw Error(i(137,e));if(n.dangerouslySetInnerHTML!=null){if(n.children!=null)throw Error(i(60));if(typeof n.dangerouslySetInnerHTML!="object"||!("__html"in n.dangerouslySetInnerHTML))throw Error(i(61))}if(n.style!=null&&typeof n.style!="object")throw Error(i(62))}}function Ga(e,n){if(e.indexOf("-")===-1)return typeof n.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var Ka=null;function Xa(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var Ya=null,rs=null,is=null;function Pu(e){if(e=lr(e)){if(typeof Ya!="function")throw Error(i(280));var n=e.stateNode;n&&(n=ui(n),Ya(e.stateNode,e.type,n))}}function Eu(e){rs?is?is.push(e):is=[e]:rs=e}function Mu(){if(rs){var e=rs,n=is;if(is=rs=null,Pu(e),n)for(e=0;e<n.length;e++)Pu(n[e])}}function Au(e,n){return e(n)}function _u(){}var qa=!1;function Du(e,n,a){if(qa)return e(n,a);qa=!0;try{return Au(e,n,a)}finally{qa=!1,(rs!==null||is!==null)&&(_u(),Mu())}}function zs(e,n){var a=e.stateNode;if(a===null)return null;var l=ui(a);if(l===null)return null;a=l[n];e:switch(n){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(l=!l.disabled)||(e=e.type,l=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!l;break e;default:e=!1}if(e)return null;if(a&&typeof a!="function")throw Error(i(231,n,typeof a));return a}var Qa=!1;if(f)try{var Us={};Object.defineProperty(Us,"passive",{get:function(){Qa=!0}}),window.addEventListener("test",Us,Us),window.removeEventListener("test",Us,Us)}catch{Qa=!1}function ny(e,n,a,l,u,m,y,b,C){var R=Array.prototype.slice.call(arguments,3);try{n.apply(a,R)}catch(W){this.onError(W)}}var Ws=!1,Ur=null,Wr=!1,Ja=null,sy={onError:function(e){Ws=!0,Ur=e}};function ry(e,n,a,l,u,m,y,b,C){Ws=!1,Ur=null,ny.apply(sy,arguments)}function iy(e,n,a,l,u,m,y,b,C){if(ry.apply(this,arguments),Ws){if(Ws){var R=Ur;Ws=!1,Ur=null}else throw Error(i(198));Wr||(Wr=!0,Ja=R)}}function Dn(e){var n=e,a=e;if(e.alternate)for(;n.return;)n=n.return;else{e=n;do n=e,(n.flags&4098)!==0&&(a=n.return),e=n.return;while(e)}return n.tag===3?a:null}function Ru(e){if(e.tag===13){var n=e.memoizedState;if(n===null&&(e=e.alternate,e!==null&&(n=e.memoizedState)),n!==null)return n.dehydrated}return null}function Lu(e){if(Dn(e)!==e)throw Error(i(188))}function ay(e){var n=e.alternate;if(!n){if(n=Dn(e),n===null)throw Error(i(188));return n!==e?null:e}for(var a=e,l=n;;){var u=a.return;if(u===null)break;var m=u.alternate;if(m===null){if(l=u.return,l!==null){a=l;continue}break}if(u.child===m.child){for(m=u.child;m;){if(m===a)return Lu(u),e;if(m===l)return Lu(u),n;m=m.sibling}throw Error(i(188))}if(a.return!==l.return)a=u,l=m;else{for(var y=!1,b=u.child;b;){if(b===a){y=!0,a=u,l=m;break}if(b===l){y=!0,l=u,a=m;break}b=b.sibling}if(!y){for(b=m.child;b;){if(b===a){y=!0,a=m,l=u;break}if(b===l){y=!0,l=m,a=u;break}b=b.sibling}if(!y)throw Error(i(189))}}if(a.alternate!==l)throw Error(i(190))}if(a.tag!==3)throw Error(i(188));return a.stateNode.current===a?e:n}function Iu(e){return e=ay(e),e!==null?Vu(e):null}function Vu(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var n=Vu(e);if(n!==null)return n;e=e.sibling}return null}var Fu=s.unstable_scheduleCallback,Bu=s.unstable_cancelCallback,oy=s.unstable_shouldYield,ly=s.unstable_requestPaint,Ve=s.unstable_now,cy=s.unstable_getCurrentPriorityLevel,Za=s.unstable_ImmediatePriority,Ou=s.unstable_UserBlockingPriority,$r=s.unstable_NormalPriority,uy=s.unstable_LowPriority,zu=s.unstable_IdlePriority,Hr=null,Wt=null;function dy(e){if(Wt&&typeof Wt.onCommitFiberRoot=="function")try{Wt.onCommitFiberRoot(Hr,e,void 0,(e.current.flags&128)===128)}catch{}}var At=Math.clz32?Math.clz32:fy,hy=Math.log,my=Math.LN2;function fy(e){return e>>>=0,e===0?32:31-(hy(e)/my|0)|0}var Gr=64,Kr=4194304;function $s(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function Xr(e,n){var a=e.pendingLanes;if(a===0)return 0;var l=0,u=e.suspendedLanes,m=e.pingedLanes,y=a&268435455;if(y!==0){var b=y&~u;b!==0?l=$s(b):(m&=y,m!==0&&(l=$s(m)))}else y=a&~u,y!==0?l=$s(y):m!==0&&(l=$s(m));if(l===0)return 0;if(n!==0&&n!==l&&(n&u)===0&&(u=l&-l,m=n&-n,u>=m||u===16&&(m&4194240)!==0))return n;if((l&4)!==0&&(l|=a&16),n=e.entangledLanes,n!==0)for(e=e.entanglements,n&=l;0<n;)a=31-At(n),u=1<<a,l|=e[a],n&=~u;return l}function py(e,n){switch(e){case 1:case 2:case 4:return n+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return n+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function gy(e,n){for(var a=e.suspendedLanes,l=e.pingedLanes,u=e.expirationTimes,m=e.pendingLanes;0<m;){var y=31-At(m),b=1<<y,C=u[y];C===-1?((b&a)===0||(b&l)!==0)&&(u[y]=py(b,n)):C<=n&&(e.expiredLanes|=b),m&=~b}}function eo(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function Uu(){var e=Gr;return Gr<<=1,(Gr&4194240)===0&&(Gr=64),e}function to(e){for(var n=[],a=0;31>a;a++)n.push(e);return n}function Hs(e,n,a){e.pendingLanes|=n,n!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,n=31-At(n),e[n]=a}function yy(e,n){var a=e.pendingLanes&~n;e.pendingLanes=n,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=n,e.mutableReadLanes&=n,e.entangledLanes&=n,n=e.entanglements;var l=e.eventTimes;for(e=e.expirationTimes;0<a;){var u=31-At(a),m=1<<u;n[u]=0,l[u]=-1,e[u]=-1,a&=~m}}function no(e,n){var a=e.entangledLanes|=n;for(e=e.entanglements;a;){var l=31-At(a),u=1<<l;u&n|e[l]&n&&(e[l]|=n),a&=~u}}var be=0;function Wu(e){return e&=-e,1<e?4<e?(e&268435455)!==0?16:536870912:4:1}var $u,so,Hu,Gu,Ku,ro=!1,Yr=[],cn=null,un=null,dn=null,Gs=new Map,Ks=new Map,hn=[],vy="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function Xu(e,n){switch(e){case"focusin":case"focusout":cn=null;break;case"dragenter":case"dragleave":un=null;break;case"mouseover":case"mouseout":dn=null;break;case"pointerover":case"pointerout":Gs.delete(n.pointerId);break;case"gotpointercapture":case"lostpointercapture":Ks.delete(n.pointerId)}}function Xs(e,n,a,l,u,m){return e===null||e.nativeEvent!==m?(e={blockedOn:n,domEventName:a,eventSystemFlags:l,nativeEvent:m,targetContainers:[u]},n!==null&&(n=lr(n),n!==null&&so(n)),e):(e.eventSystemFlags|=l,n=e.targetContainers,u!==null&&n.indexOf(u)===-1&&n.push(u),e)}function xy(e,n,a,l,u){switch(n){case"focusin":return cn=Xs(cn,e,n,a,l,u),!0;case"dragenter":return un=Xs(un,e,n,a,l,u),!0;case"mouseover":return dn=Xs(dn,e,n,a,l,u),!0;case"pointerover":var m=u.pointerId;return Gs.set(m,Xs(Gs.get(m)||null,e,n,a,l,u)),!0;case"gotpointercapture":return m=u.pointerId,Ks.set(m,Xs(Ks.get(m)||null,e,n,a,l,u)),!0}return!1}function Yu(e){var n=Rn(e.target);if(n!==null){var a=Dn(n);if(a!==null){if(n=a.tag,n===13){if(n=Ru(a),n!==null){e.blockedOn=n,Ku(e.priority,function(){Hu(a)});return}}else if(n===3&&a.stateNode.current.memoizedState.isDehydrated){e.blockedOn=a.tag===3?a.stateNode.containerInfo:null;return}}}e.blockedOn=null}function qr(e){if(e.blockedOn!==null)return!1;for(var n=e.targetContainers;0<n.length;){var a=ao(e.domEventName,e.eventSystemFlags,n[0],e.nativeEvent);if(a===null){a=e.nativeEvent;var l=new a.constructor(a.type,a);Ka=l,a.target.dispatchEvent(l),Ka=null}else return n=lr(a),n!==null&&so(n),e.blockedOn=a,!1;n.shift()}return!0}function qu(e,n,a){qr(e)&&a.delete(n)}function wy(){ro=!1,cn!==null&&qr(cn)&&(cn=null),un!==null&&qr(un)&&(un=null),dn!==null&&qr(dn)&&(dn=null),Gs.forEach(qu),Ks.forEach(qu)}function Ys(e,n){e.blockedOn===n&&(e.blockedOn=null,ro||(ro=!0,s.unstable_scheduleCallback(s.unstable_NormalPriority,wy)))}function qs(e){function n(u){return Ys(u,e)}if(0<Yr.length){Ys(Yr[0],e);for(var a=1;a<Yr.length;a++){var l=Yr[a];l.blockedOn===e&&(l.blockedOn=null)}}for(cn!==null&&Ys(cn,e),un!==null&&Ys(un,e),dn!==null&&Ys(dn,e),Gs.forEach(n),Ks.forEach(n),a=0;a<hn.length;a++)l=hn[a],l.blockedOn===e&&(l.blockedOn=null);for(;0<hn.length&&(a=hn[0],a.blockedOn===null);)Yu(a),a.blockedOn===null&&hn.shift()}var as=I.ReactCurrentBatchConfig,Qr=!0;function by(e,n,a,l){var u=be,m=as.transition;as.transition=null;try{be=1,io(e,n,a,l)}finally{be=u,as.transition=m}}function ky(e,n,a,l){var u=be,m=as.transition;as.transition=null;try{be=4,io(e,n,a,l)}finally{be=u,as.transition=m}}function io(e,n,a,l){if(Qr){var u=ao(e,n,a,l);if(u===null)So(e,n,l,Jr,a),Xu(e,l);else if(xy(u,e,n,a,l))l.stopPropagation();else if(Xu(e,l),n&4&&-1<vy.indexOf(e)){for(;u!==null;){var m=lr(u);if(m!==null&&$u(m),m=ao(e,n,a,l),m===null&&So(e,n,l,Jr,a),m===u)break;u=m}u!==null&&l.stopPropagation()}else So(e,n,l,null,a)}}var Jr=null;function ao(e,n,a,l){if(Jr=null,e=Xa(l),e=Rn(e),e!==null)if(n=Dn(e),n===null)e=null;else if(a=n.tag,a===13){if(e=Ru(n),e!==null)return e;e=null}else if(a===3){if(n.stateNode.current.memoizedState.isDehydrated)return n.tag===3?n.stateNode.containerInfo:null;e=null}else n!==e&&(e=null);return Jr=e,null}function Qu(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(cy()){case Za:return 1;case Ou:return 4;case $r:case uy:return 16;case zu:return 536870912;default:return 16}default:return 16}}var mn=null,oo=null,Zr=null;function Ju(){if(Zr)return Zr;var e,n=oo,a=n.length,l,u="value"in mn?mn.value:mn.textContent,m=u.length;for(e=0;e<a&&n[e]===u[e];e++);var y=a-e;for(l=1;l<=y&&n[a-l]===u[m-l];l++);return Zr=u.slice(e,1<l?1-l:void 0)}function ei(e){var n=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&n===13&&(e=13)):e=n,e===10&&(e=13),32<=e||e===13?e:0}function ti(){return!0}function Zu(){return!1}function vt(e){function n(a,l,u,m,y){this._reactName=a,this._targetInst=u,this.type=l,this.nativeEvent=m,this.target=y,this.currentTarget=null;for(var b in e)e.hasOwnProperty(b)&&(a=e[b],this[b]=a?a(m):m[b]);return this.isDefaultPrevented=(m.defaultPrevented!=null?m.defaultPrevented:m.returnValue===!1)?ti:Zu,this.isPropagationStopped=Zu,this}return K(n.prototype,{preventDefault:function(){this.defaultPrevented=!0;var a=this.nativeEvent;a&&(a.preventDefault?a.preventDefault():typeof a.returnValue!="unknown"&&(a.returnValue=!1),this.isDefaultPrevented=ti)},stopPropagation:function(){var a=this.nativeEvent;a&&(a.stopPropagation?a.stopPropagation():typeof a.cancelBubble!="unknown"&&(a.cancelBubble=!0),this.isPropagationStopped=ti)},persist:function(){},isPersistent:ti}),n}var os={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},lo=vt(os),Qs=K({},os,{view:0,detail:0}),jy=vt(Qs),co,uo,Js,ni=K({},Qs,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:mo,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==Js&&(Js&&e.type==="mousemove"?(co=e.screenX-Js.screenX,uo=e.screenY-Js.screenY):uo=co=0,Js=e),co)},movementY:function(e){return"movementY"in e?e.movementY:uo}}),ed=vt(ni),Sy=K({},ni,{dataTransfer:0}),Ny=vt(Sy),Cy=K({},Qs,{relatedTarget:0}),ho=vt(Cy),Ty=K({},os,{animationName:0,elapsedTime:0,pseudoElement:0}),Py=vt(Ty),Ey=K({},os,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),My=vt(Ey),Ay=K({},os,{data:0}),td=vt(Ay),_y={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},Dy={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},Ry={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function Ly(e){var n=this.nativeEvent;return n.getModifierState?n.getModifierState(e):(e=Ry[e])?!!n[e]:!1}function mo(){return Ly}var Iy=K({},Qs,{key:function(e){if(e.key){var n=_y[e.key]||e.key;if(n!=="Unidentified")return n}return e.type==="keypress"?(e=ei(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?Dy[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:mo,charCode:function(e){return e.type==="keypress"?ei(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?ei(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),Vy=vt(Iy),Fy=K({},ni,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),nd=vt(Fy),By=K({},Qs,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:mo}),Oy=vt(By),zy=K({},os,{propertyName:0,elapsedTime:0,pseudoElement:0}),Uy=vt(zy),Wy=K({},ni,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),$y=vt(Wy),Hy=[9,13,27,32],fo=f&&"CompositionEvent"in window,Zs=null;f&&"documentMode"in document&&(Zs=document.documentMode);var Gy=f&&"TextEvent"in window&&!Zs,sd=f&&(!fo||Zs&&8<Zs&&11>=Zs),rd=" ",id=!1;function ad(e,n){switch(e){case"keyup":return Hy.indexOf(n.keyCode)!==-1;case"keydown":return n.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function od(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var ls=!1;function Ky(e,n){switch(e){case"compositionend":return od(n);case"keypress":return n.which!==32?null:(id=!0,rd);case"textInput":return e=n.data,e===rd&&id?null:e;default:return null}}function Xy(e,n){if(ls)return e==="compositionend"||!fo&&ad(e,n)?(e=Ju(),Zr=oo=mn=null,ls=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(n.ctrlKey||n.altKey||n.metaKey)||n.ctrlKey&&n.altKey){if(n.char&&1<n.char.length)return n.char;if(n.which)return String.fromCharCode(n.which)}return null;case"compositionend":return sd&&n.locale!=="ko"?null:n.data;default:return null}}var Yy={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function ld(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n==="input"?!!Yy[e.type]:n==="textarea"}function cd(e,n,a,l){Eu(l),n=oi(n,"onChange"),0<n.length&&(a=new lo("onChange","change",null,a,l),e.push({event:a,listeners:n}))}var er=null,tr=null;function qy(e){Td(e,0)}function si(e){var n=ms(e);if(yu(n))return e}function Qy(e,n){if(e==="change")return n}var ud=!1;if(f){var po;if(f){var go="oninput"in document;if(!go){var dd=document.createElement("div");dd.setAttribute("oninput","return;"),go=typeof dd.oninput=="function"}po=go}else po=!1;ud=po&&(!document.documentMode||9<document.documentMode)}function hd(){er&&(er.detachEvent("onpropertychange",md),tr=er=null)}function md(e){if(e.propertyName==="value"&&si(tr)){var n=[];cd(n,tr,e,Xa(e)),Du(qy,n)}}function Jy(e,n,a){e==="focusin"?(hd(),er=n,tr=a,er.attachEvent("onpropertychange",md)):e==="focusout"&&hd()}function Zy(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return si(tr)}function ev(e,n){if(e==="click")return si(n)}function tv(e,n){if(e==="input"||e==="change")return si(n)}function nv(e,n){return e===n&&(e!==0||1/e===1/n)||e!==e&&n!==n}var _t=typeof Object.is=="function"?Object.is:nv;function nr(e,n){if(_t(e,n))return!0;if(typeof e!="object"||e===null||typeof n!="object"||n===null)return!1;var a=Object.keys(e),l=Object.keys(n);if(a.length!==l.length)return!1;for(l=0;l<a.length;l++){var u=a[l];if(!p.call(n,u)||!_t(e[u],n[u]))return!1}return!0}function fd(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function pd(e,n){var a=fd(e);e=0;for(var l;a;){if(a.nodeType===3){if(l=e+a.textContent.length,e<=n&&l>=n)return{node:a,offset:n-e};e=l}e:{for(;a;){if(a.nextSibling){a=a.nextSibling;break e}a=a.parentNode}a=void 0}a=fd(a)}}function gd(e,n){return e&&n?e===n?!0:e&&e.nodeType===3?!1:n&&n.nodeType===3?gd(e,n.parentNode):"contains"in e?e.contains(n):e.compareDocumentPosition?!!(e.compareDocumentPosition(n)&16):!1:!1}function yd(){for(var e=window,n=Or();n instanceof e.HTMLIFrameElement;){try{var a=typeof n.contentWindow.location.href=="string"}catch{a=!1}if(a)e=n.contentWindow;else break;n=Or(e.document)}return n}function yo(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n&&(n==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||n==="textarea"||e.contentEditable==="true")}function sv(e){var n=yd(),a=e.focusedElem,l=e.selectionRange;if(n!==a&&a&&a.ownerDocument&&gd(a.ownerDocument.documentElement,a)){if(l!==null&&yo(a)){if(n=l.start,e=l.end,e===void 0&&(e=n),"selectionStart"in a)a.selectionStart=n,a.selectionEnd=Math.min(e,a.value.length);else if(e=(n=a.ownerDocument||document)&&n.defaultView||window,e.getSelection){e=e.getSelection();var u=a.textContent.length,m=Math.min(l.start,u);l=l.end===void 0?m:Math.min(l.end,u),!e.extend&&m>l&&(u=l,l=m,m=u),u=pd(a,m);var y=pd(a,l);u&&y&&(e.rangeCount!==1||e.anchorNode!==u.node||e.anchorOffset!==u.offset||e.focusNode!==y.node||e.focusOffset!==y.offset)&&(n=n.createRange(),n.setStart(u.node,u.offset),e.removeAllRanges(),m>l?(e.addRange(n),e.extend(y.node,y.offset)):(n.setEnd(y.node,y.offset),e.addRange(n)))}}for(n=[],e=a;e=e.parentNode;)e.nodeType===1&&n.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof a.focus=="function"&&a.focus(),a=0;a<n.length;a++)e=n[a],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var rv=f&&"documentMode"in document&&11>=document.documentMode,cs=null,vo=null,sr=null,xo=!1;function vd(e,n,a){var l=a.window===a?a.document:a.nodeType===9?a:a.ownerDocument;xo||cs==null||cs!==Or(l)||(l=cs,"selectionStart"in l&&yo(l)?l={start:l.selectionStart,end:l.selectionEnd}:(l=(l.ownerDocument&&l.ownerDocument.defaultView||window).getSelection(),l={anchorNode:l.anchorNode,anchorOffset:l.anchorOffset,focusNode:l.focusNode,focusOffset:l.focusOffset}),sr&&nr(sr,l)||(sr=l,l=oi(vo,"onSelect"),0<l.length&&(n=new lo("onSelect","select",null,n,a),e.push({event:n,listeners:l}),n.target=cs)))}function ri(e,n){var a={};return a[e.toLowerCase()]=n.toLowerCase(),a["Webkit"+e]="webkit"+n,a["Moz"+e]="moz"+n,a}var us={animationend:ri("Animation","AnimationEnd"),animationiteration:ri("Animation","AnimationIteration"),animationstart:ri("Animation","AnimationStart"),transitionend:ri("Transition","TransitionEnd")},wo={},xd={};f&&(xd=document.createElement("div").style,"AnimationEvent"in window||(delete us.animationend.animation,delete us.animationiteration.animation,delete us.animationstart.animation),"TransitionEvent"in window||delete us.transitionend.transition);function ii(e){if(wo[e])return wo[e];if(!us[e])return e;var n=us[e],a;for(a in n)if(n.hasOwnProperty(a)&&a in xd)return wo[e]=n[a];return e}var wd=ii("animationend"),bd=ii("animationiteration"),kd=ii("animationstart"),jd=ii("transitionend"),Sd=new Map,Nd="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function fn(e,n){Sd.set(e,n),d(n,[e])}for(var bo=0;bo<Nd.length;bo++){var ko=Nd[bo],iv=ko.toLowerCase(),av=ko[0].toUpperCase()+ko.slice(1);fn(iv,"on"+av)}fn(wd,"onAnimationEnd"),fn(bd,"onAnimationIteration"),fn(kd,"onAnimationStart"),fn("dblclick","onDoubleClick"),fn("focusin","onFocus"),fn("focusout","onBlur"),fn(jd,"onTransitionEnd"),h("onMouseEnter",["mouseout","mouseover"]),h("onMouseLeave",["mouseout","mouseover"]),h("onPointerEnter",["pointerout","pointerover"]),h("onPointerLeave",["pointerout","pointerover"]),d("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),d("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),d("onBeforeInput",["compositionend","keypress","textInput","paste"]),d("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),d("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),d("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var rr="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),ov=new Set("cancel close invalid load scroll toggle".split(" ").concat(rr));function Cd(e,n,a){var l=e.type||"unknown-event";e.currentTarget=a,iy(l,n,void 0,e),e.currentTarget=null}function Td(e,n){n=(n&4)!==0;for(var a=0;a<e.length;a++){var l=e[a],u=l.event;l=l.listeners;e:{var m=void 0;if(n)for(var y=l.length-1;0<=y;y--){var b=l[y],C=b.instance,R=b.currentTarget;if(b=b.listener,C!==m&&u.isPropagationStopped())break e;Cd(u,b,R),m=C}else for(y=0;y<l.length;y++){if(b=l[y],C=b.instance,R=b.currentTarget,b=b.listener,C!==m&&u.isPropagationStopped())break e;Cd(u,b,R),m=C}}}if(Wr)throw e=Ja,Wr=!1,Ja=null,e}function Te(e,n){var a=n[Mo];a===void 0&&(a=n[Mo]=new Set);var l=e+"__bubble";a.has(l)||(Pd(n,e,2,!1),a.add(l))}function jo(e,n,a){var l=0;n&&(l|=4),Pd(a,e,l,n)}var ai="_reactListening"+Math.random().toString(36).slice(2);function ir(e){if(!e[ai]){e[ai]=!0,o.forEach(function(a){a!=="selectionchange"&&(ov.has(a)||jo(a,!1,e),jo(a,!0,e))});var n=e.nodeType===9?e:e.ownerDocument;n===null||n[ai]||(n[ai]=!0,jo("selectionchange",!1,n))}}function Pd(e,n,a,l){switch(Qu(n)){case 1:var u=by;break;case 4:u=ky;break;default:u=io}a=u.bind(null,n,a,e),u=void 0,!Qa||n!=="touchstart"&&n!=="touchmove"&&n!=="wheel"||(u=!0),l?u!==void 0?e.addEventListener(n,a,{capture:!0,passive:u}):e.addEventListener(n,a,!0):u!==void 0?e.addEventListener(n,a,{passive:u}):e.addEventListener(n,a,!1)}function So(e,n,a,l,u){var m=l;if((n&1)===0&&(n&2)===0&&l!==null)e:for(;;){if(l===null)return;var y=l.tag;if(y===3||y===4){var b=l.stateNode.containerInfo;if(b===u||b.nodeType===8&&b.parentNode===u)break;if(y===4)for(y=l.return;y!==null;){var C=y.tag;if((C===3||C===4)&&(C=y.stateNode.containerInfo,C===u||C.nodeType===8&&C.parentNode===u))return;y=y.return}for(;b!==null;){if(y=Rn(b),y===null)return;if(C=y.tag,C===5||C===6){l=m=y;continue e}b=b.parentNode}}l=l.return}Du(function(){var R=m,W=Xa(a),$=[];e:{var U=Sd.get(e);if(U!==void 0){var X=lo,q=e;switch(e){case"keypress":if(ei(a)===0)break e;case"keydown":case"keyup":X=Vy;break;case"focusin":q="focus",X=ho;break;case"focusout":q="blur",X=ho;break;case"beforeblur":case"afterblur":X=ho;break;case"click":if(a.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":X=ed;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":X=Ny;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":X=Oy;break;case wd:case bd:case kd:X=Py;break;case jd:X=Uy;break;case"scroll":X=jy;break;case"wheel":X=$y;break;case"copy":case"cut":case"paste":X=My;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":X=nd}var Z=(n&4)!==0,Fe=!Z&&e==="scroll",A=Z?U!==null?U+"Capture":null:U;Z=[];for(var T=R,_;T!==null;){_=T;var G=_.stateNode;if(_.tag===5&&G!==null&&(_=G,A!==null&&(G=zs(T,A),G!=null&&Z.push(ar(T,G,_)))),Fe)break;T=T.return}0<Z.length&&(U=new X(U,q,null,a,W),$.push({event:U,listeners:Z}))}}if((n&7)===0){e:{if(U=e==="mouseover"||e==="pointerover",X=e==="mouseout"||e==="pointerout",U&&a!==Ka&&(q=a.relatedTarget||a.fromElement)&&(Rn(q)||q[Jt]))break e;if((X||U)&&(U=W.window===W?W:(U=W.ownerDocument)?U.defaultView||U.parentWindow:window,X?(q=a.relatedTarget||a.toElement,X=R,q=q?Rn(q):null,q!==null&&(Fe=Dn(q),q!==Fe||q.tag!==5&&q.tag!==6)&&(q=null)):(X=null,q=R),X!==q)){if(Z=ed,G="onMouseLeave",A="onMouseEnter",T="mouse",(e==="pointerout"||e==="pointerover")&&(Z=nd,G="onPointerLeave",A="onPointerEnter",T="pointer"),Fe=X==null?U:ms(X),_=q==null?U:ms(q),U=new Z(G,T+"leave",X,a,W),U.target=Fe,U.relatedTarget=_,G=null,Rn(W)===R&&(Z=new Z(A,T+"enter",q,a,W),Z.target=_,Z.relatedTarget=Fe,G=Z),Fe=G,X&&q)t:{for(Z=X,A=q,T=0,_=Z;_;_=ds(_))T++;for(_=0,G=A;G;G=ds(G))_++;for(;0<T-_;)Z=ds(Z),T--;for(;0<_-T;)A=ds(A),_--;for(;T--;){if(Z===A||A!==null&&Z===A.alternate)break t;Z=ds(Z),A=ds(A)}Z=null}else Z=null;X!==null&&Ed($,U,X,Z,!1),q!==null&&Fe!==null&&Ed($,Fe,q,Z,!0)}}e:{if(U=R?ms(R):window,X=U.nodeName&&U.nodeName.toLowerCase(),X==="select"||X==="input"&&U.type==="file")var te=Qy;else if(ld(U))if(ud)te=tv;else{te=Zy;var re=Jy}else(X=U.nodeName)&&X.toLowerCase()==="input"&&(U.type==="checkbox"||U.type==="radio")&&(te=ev);if(te&&(te=te(e,R))){cd($,te,a,W);break e}re&&re(e,U,R),e==="focusout"&&(re=U._wrapperState)&&re.controlled&&U.type==="number"&&Ua(U,"number",U.value)}switch(re=R?ms(R):window,e){case"focusin":(ld(re)||re.contentEditable==="true")&&(cs=re,vo=R,sr=null);break;case"focusout":sr=vo=cs=null;break;case"mousedown":xo=!0;break;case"contextmenu":case"mouseup":case"dragend":xo=!1,vd($,a,W);break;case"selectionchange":if(rv)break;case"keydown":case"keyup":vd($,a,W)}var ie;if(fo)e:{switch(e){case"compositionstart":var ae="onCompositionStart";break e;case"compositionend":ae="onCompositionEnd";break e;case"compositionupdate":ae="onCompositionUpdate";break e}ae=void 0}else ls?ad(e,a)&&(ae="onCompositionEnd"):e==="keydown"&&a.keyCode===229&&(ae="onCompositionStart");ae&&(sd&&a.locale!=="ko"&&(ls||ae!=="onCompositionStart"?ae==="onCompositionEnd"&&ls&&(ie=Ju()):(mn=W,oo="value"in mn?mn.value:mn.textContent,ls=!0)),re=oi(R,ae),0<re.length&&(ae=new td(ae,e,null,a,W),$.push({event:ae,listeners:re}),ie?ae.data=ie:(ie=od(a),ie!==null&&(ae.data=ie)))),(ie=Gy?Ky(e,a):Xy(e,a))&&(R=oi(R,"onBeforeInput"),0<R.length&&(W=new td("onBeforeInput","beforeinput",null,a,W),$.push({event:W,listeners:R}),W.data=ie))}Td($,n)})}function ar(e,n,a){return{instance:e,listener:n,currentTarget:a}}function oi(e,n){for(var a=n+"Capture",l=[];e!==null;){var u=e,m=u.stateNode;u.tag===5&&m!==null&&(u=m,m=zs(e,a),m!=null&&l.unshift(ar(e,m,u)),m=zs(e,n),m!=null&&l.push(ar(e,m,u))),e=e.return}return l}function ds(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function Ed(e,n,a,l,u){for(var m=n._reactName,y=[];a!==null&&a!==l;){var b=a,C=b.alternate,R=b.stateNode;if(C!==null&&C===l)break;b.tag===5&&R!==null&&(b=R,u?(C=zs(a,m),C!=null&&y.unshift(ar(a,C,b))):u||(C=zs(a,m),C!=null&&y.push(ar(a,C,b)))),a=a.return}y.length!==0&&e.push({event:n,listeners:y})}var lv=/\r\n?/g,cv=/\u0000|\uFFFD/g;function Md(e){return(typeof e=="string"?e:""+e).replace(lv,`
`).replace(cv,"")}function li(e,n,a){if(n=Md(n),Md(e)!==n&&a)throw Error(i(425))}function ci(){}var No=null,Co=null;function To(e,n){return e==="textarea"||e==="noscript"||typeof n.children=="string"||typeof n.children=="number"||typeof n.dangerouslySetInnerHTML=="object"&&n.dangerouslySetInnerHTML!==null&&n.dangerouslySetInnerHTML.__html!=null}var Po=typeof setTimeout=="function"?setTimeout:void 0,uv=typeof clearTimeout=="function"?clearTimeout:void 0,Ad=typeof Promise=="function"?Promise:void 0,dv=typeof queueMicrotask=="function"?queueMicrotask:typeof Ad<"u"?function(e){return Ad.resolve(null).then(e).catch(hv)}:Po;function hv(e){setTimeout(function(){throw e})}function Eo(e,n){var a=n,l=0;do{var u=a.nextSibling;if(e.removeChild(a),u&&u.nodeType===8)if(a=u.data,a==="/$"){if(l===0){e.removeChild(u),qs(n);return}l--}else a!=="$"&&a!=="$?"&&a!=="$!"||l++;a=u}while(a);qs(n)}function pn(e){for(;e!=null;e=e.nextSibling){var n=e.nodeType;if(n===1||n===3)break;if(n===8){if(n=e.data,n==="$"||n==="$!"||n==="$?")break;if(n==="/$")return null}}return e}function _d(e){e=e.previousSibling;for(var n=0;e;){if(e.nodeType===8){var a=e.data;if(a==="$"||a==="$!"||a==="$?"){if(n===0)return e;n--}else a==="/$"&&n++}e=e.previousSibling}return null}var hs=Math.random().toString(36).slice(2),$t="__reactFiber$"+hs,or="__reactProps$"+hs,Jt="__reactContainer$"+hs,Mo="__reactEvents$"+hs,mv="__reactListeners$"+hs,fv="__reactHandles$"+hs;function Rn(e){var n=e[$t];if(n)return n;for(var a=e.parentNode;a;){if(n=a[Jt]||a[$t]){if(a=n.alternate,n.child!==null||a!==null&&a.child!==null)for(e=_d(e);e!==null;){if(a=e[$t])return a;e=_d(e)}return n}e=a,a=e.parentNode}return null}function lr(e){return e=e[$t]||e[Jt],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function ms(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(i(33))}function ui(e){return e[or]||null}var Ao=[],fs=-1;function gn(e){return{current:e}}function Pe(e){0>fs||(e.current=Ao[fs],Ao[fs]=null,fs--)}function Ce(e,n){fs++,Ao[fs]=e.current,e.current=n}var yn={},tt=gn(yn),ut=gn(!1),Ln=yn;function ps(e,n){var a=e.type.contextTypes;if(!a)return yn;var l=e.stateNode;if(l&&l.__reactInternalMemoizedUnmaskedChildContext===n)return l.__reactInternalMemoizedMaskedChildContext;var u={},m;for(m in a)u[m]=n[m];return l&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=n,e.__reactInternalMemoizedMaskedChildContext=u),u}function dt(e){return e=e.childContextTypes,e!=null}function di(){Pe(ut),Pe(tt)}function Dd(e,n,a){if(tt.current!==yn)throw Error(i(168));Ce(tt,n),Ce(ut,a)}function Rd(e,n,a){var l=e.stateNode;if(n=n.childContextTypes,typeof l.getChildContext!="function")return a;l=l.getChildContext();for(var u in l)if(!(u in n))throw Error(i(108,Ne(e)||"Unknown",u));return K({},a,l)}function hi(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||yn,Ln=tt.current,Ce(tt,e),Ce(ut,ut.current),!0}function Ld(e,n,a){var l=e.stateNode;if(!l)throw Error(i(169));a?(e=Rd(e,n,Ln),l.__reactInternalMemoizedMergedChildContext=e,Pe(ut),Pe(tt),Ce(tt,e)):Pe(ut),Ce(ut,a)}var Zt=null,mi=!1,_o=!1;function Id(e){Zt===null?Zt=[e]:Zt.push(e)}function pv(e){mi=!0,Id(e)}function vn(){if(!_o&&Zt!==null){_o=!0;var e=0,n=be;try{var a=Zt;for(be=1;e<a.length;e++){var l=a[e];do l=l(!0);while(l!==null)}Zt=null,mi=!1}catch(u){throw Zt!==null&&(Zt=Zt.slice(e+1)),Fu(Za,vn),u}finally{be=n,_o=!1}}return null}var gs=[],ys=0,fi=null,pi=0,St=[],Nt=0,In=null,en=1,tn="";function Vn(e,n){gs[ys++]=pi,gs[ys++]=fi,fi=e,pi=n}function Vd(e,n,a){St[Nt++]=en,St[Nt++]=tn,St[Nt++]=In,In=e;var l=en;e=tn;var u=32-At(l)-1;l&=~(1<<u),a+=1;var m=32-At(n)+u;if(30<m){var y=u-u%5;m=(l&(1<<y)-1).toString(32),l>>=y,u-=y,en=1<<32-At(n)+u|a<<u|l,tn=m+e}else en=1<<m|a<<u|l,tn=e}function Do(e){e.return!==null&&(Vn(e,1),Vd(e,1,0))}function Ro(e){for(;e===fi;)fi=gs[--ys],gs[ys]=null,pi=gs[--ys],gs[ys]=null;for(;e===In;)In=St[--Nt],St[Nt]=null,tn=St[--Nt],St[Nt]=null,en=St[--Nt],St[Nt]=null}var xt=null,wt=null,Me=!1,Dt=null;function Fd(e,n){var a=Et(5,null,null,0);a.elementType="DELETED",a.stateNode=n,a.return=e,n=e.deletions,n===null?(e.deletions=[a],e.flags|=16):n.push(a)}function Bd(e,n){switch(e.tag){case 5:var a=e.type;return n=n.nodeType!==1||a.toLowerCase()!==n.nodeName.toLowerCase()?null:n,n!==null?(e.stateNode=n,xt=e,wt=pn(n.firstChild),!0):!1;case 6:return n=e.pendingProps===""||n.nodeType!==3?null:n,n!==null?(e.stateNode=n,xt=e,wt=null,!0):!1;case 13:return n=n.nodeType!==8?null:n,n!==null?(a=In!==null?{id:en,overflow:tn}:null,e.memoizedState={dehydrated:n,treeContext:a,retryLane:1073741824},a=Et(18,null,null,0),a.stateNode=n,a.return=e,e.child=a,xt=e,wt=null,!0):!1;default:return!1}}function Lo(e){return(e.mode&1)!==0&&(e.flags&128)===0}function Io(e){if(Me){var n=wt;if(n){var a=n;if(!Bd(e,n)){if(Lo(e))throw Error(i(418));n=pn(a.nextSibling);var l=xt;n&&Bd(e,n)?Fd(l,a):(e.flags=e.flags&-4097|2,Me=!1,xt=e)}}else{if(Lo(e))throw Error(i(418));e.flags=e.flags&-4097|2,Me=!1,xt=e}}}function Od(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;xt=e}function gi(e){if(e!==xt)return!1;if(!Me)return Od(e),Me=!0,!1;var n;if((n=e.tag!==3)&&!(n=e.tag!==5)&&(n=e.type,n=n!=="head"&&n!=="body"&&!To(e.type,e.memoizedProps)),n&&(n=wt)){if(Lo(e))throw zd(),Error(i(418));for(;n;)Fd(e,n),n=pn(n.nextSibling)}if(Od(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(i(317));e:{for(e=e.nextSibling,n=0;e;){if(e.nodeType===8){var a=e.data;if(a==="/$"){if(n===0){wt=pn(e.nextSibling);break e}n--}else a!=="$"&&a!=="$!"&&a!=="$?"||n++}e=e.nextSibling}wt=null}}else wt=xt?pn(e.stateNode.nextSibling):null;return!0}function zd(){for(var e=wt;e;)e=pn(e.nextSibling)}function vs(){wt=xt=null,Me=!1}function Vo(e){Dt===null?Dt=[e]:Dt.push(e)}var gv=I.ReactCurrentBatchConfig;function cr(e,n,a){if(e=a.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(a._owner){if(a=a._owner,a){if(a.tag!==1)throw Error(i(309));var l=a.stateNode}if(!l)throw Error(i(147,e));var u=l,m=""+e;return n!==null&&n.ref!==null&&typeof n.ref=="function"&&n.ref._stringRef===m?n.ref:(n=function(y){var b=u.refs;y===null?delete b[m]:b[m]=y},n._stringRef=m,n)}if(typeof e!="string")throw Error(i(284));if(!a._owner)throw Error(i(290,e))}return e}function yi(e,n){throw e=Object.prototype.toString.call(n),Error(i(31,e==="[object Object]"?"object with keys {"+Object.keys(n).join(", ")+"}":e))}function Ud(e){var n=e._init;return n(e._payload)}function Wd(e){function n(A,T){if(e){var _=A.deletions;_===null?(A.deletions=[T],A.flags|=16):_.push(T)}}function a(A,T){if(!e)return null;for(;T!==null;)n(A,T),T=T.sibling;return null}function l(A,T){for(A=new Map;T!==null;)T.key!==null?A.set(T.key,T):A.set(T.index,T),T=T.sibling;return A}function u(A,T){return A=Cn(A,T),A.index=0,A.sibling=null,A}function m(A,T,_){return A.index=_,e?(_=A.alternate,_!==null?(_=_.index,_<T?(A.flags|=2,T):_):(A.flags|=2,T)):(A.flags|=1048576,T)}function y(A){return e&&A.alternate===null&&(A.flags|=2),A}function b(A,T,_,G){return T===null||T.tag!==6?(T=Pl(_,A.mode,G),T.return=A,T):(T=u(T,_),T.return=A,T)}function C(A,T,_,G){var te=_.type;return te===V?W(A,T,_.props.children,G,_.key):T!==null&&(T.elementType===te||typeof te=="object"&&te!==null&&te.$$typeof===Ie&&Ud(te)===T.type)?(G=u(T,_.props),G.ref=cr(A,T,_),G.return=A,G):(G=zi(_.type,_.key,_.props,null,A.mode,G),G.ref=cr(A,T,_),G.return=A,G)}function R(A,T,_,G){return T===null||T.tag!==4||T.stateNode.containerInfo!==_.containerInfo||T.stateNode.implementation!==_.implementation?(T=El(_,A.mode,G),T.return=A,T):(T=u(T,_.children||[]),T.return=A,T)}function W(A,T,_,G,te){return T===null||T.tag!==7?(T=Hn(_,A.mode,G,te),T.return=A,T):(T=u(T,_),T.return=A,T)}function $(A,T,_){if(typeof T=="string"&&T!==""||typeof T=="number")return T=Pl(""+T,A.mode,_),T.return=A,T;if(typeof T=="object"&&T!==null){switch(T.$$typeof){case D:return _=zi(T.type,T.key,T.props,null,A.mode,_),_.ref=cr(A,null,T),_.return=A,_;case F:return T=El(T,A.mode,_),T.return=A,T;case Ie:var G=T._init;return $(A,G(T._payload),_)}if(Fs(T)||J(T))return T=Hn(T,A.mode,_,null),T.return=A,T;yi(A,T)}return null}function U(A,T,_,G){var te=T!==null?T.key:null;if(typeof _=="string"&&_!==""||typeof _=="number")return te!==null?null:b(A,T,""+_,G);if(typeof _=="object"&&_!==null){switch(_.$$typeof){case D:return _.key===te?C(A,T,_,G):null;case F:return _.key===te?R(A,T,_,G):null;case Ie:return te=_._init,U(A,T,te(_._payload),G)}if(Fs(_)||J(_))return te!==null?null:W(A,T,_,G,null);yi(A,_)}return null}function X(A,T,_,G,te){if(typeof G=="string"&&G!==""||typeof G=="number")return A=A.get(_)||null,b(T,A,""+G,te);if(typeof G=="object"&&G!==null){switch(G.$$typeof){case D:return A=A.get(G.key===null?_:G.key)||null,C(T,A,G,te);case F:return A=A.get(G.key===null?_:G.key)||null,R(T,A,G,te);case Ie:var re=G._init;return X(A,T,_,re(G._payload),te)}if(Fs(G)||J(G))return A=A.get(_)||null,W(T,A,G,te,null);yi(T,G)}return null}function q(A,T,_,G){for(var te=null,re=null,ie=T,ae=T=0,Ye=null;ie!==null&&ae<_.length;ae++){ie.index>ae?(Ye=ie,ie=null):Ye=ie.sibling;var ge=U(A,ie,_[ae],G);if(ge===null){ie===null&&(ie=Ye);break}e&&ie&&ge.alternate===null&&n(A,ie),T=m(ge,T,ae),re===null?te=ge:re.sibling=ge,re=ge,ie=Ye}if(ae===_.length)return a(A,ie),Me&&Vn(A,ae),te;if(ie===null){for(;ae<_.length;ae++)ie=$(A,_[ae],G),ie!==null&&(T=m(ie,T,ae),re===null?te=ie:re.sibling=ie,re=ie);return Me&&Vn(A,ae),te}for(ie=l(A,ie);ae<_.length;ae++)Ye=X(ie,A,ae,_[ae],G),Ye!==null&&(e&&Ye.alternate!==null&&ie.delete(Ye.key===null?ae:Ye.key),T=m(Ye,T,ae),re===null?te=Ye:re.sibling=Ye,re=Ye);return e&&ie.forEach(function(Tn){return n(A,Tn)}),Me&&Vn(A,ae),te}function Z(A,T,_,G){var te=J(_);if(typeof te!="function")throw Error(i(150));if(_=te.call(_),_==null)throw Error(i(151));for(var re=te=null,ie=T,ae=T=0,Ye=null,ge=_.next();ie!==null&&!ge.done;ae++,ge=_.next()){ie.index>ae?(Ye=ie,ie=null):Ye=ie.sibling;var Tn=U(A,ie,ge.value,G);if(Tn===null){ie===null&&(ie=Ye);break}e&&ie&&Tn.alternate===null&&n(A,ie),T=m(Tn,T,ae),re===null?te=Tn:re.sibling=Tn,re=Tn,ie=Ye}if(ge.done)return a(A,ie),Me&&Vn(A,ae),te;if(ie===null){for(;!ge.done;ae++,ge=_.next())ge=$(A,ge.value,G),ge!==null&&(T=m(ge,T,ae),re===null?te=ge:re.sibling=ge,re=ge);return Me&&Vn(A,ae),te}for(ie=l(A,ie);!ge.done;ae++,ge=_.next())ge=X(ie,A,ae,ge.value,G),ge!==null&&(e&&ge.alternate!==null&&ie.delete(ge.key===null?ae:ge.key),T=m(ge,T,ae),re===null?te=ge:re.sibling=ge,re=ge);return e&&ie.forEach(function(Yv){return n(A,Yv)}),Me&&Vn(A,ae),te}function Fe(A,T,_,G){if(typeof _=="object"&&_!==null&&_.type===V&&_.key===null&&(_=_.props.children),typeof _=="object"&&_!==null){switch(_.$$typeof){case D:e:{for(var te=_.key,re=T;re!==null;){if(re.key===te){if(te=_.type,te===V){if(re.tag===7){a(A,re.sibling),T=u(re,_.props.children),T.return=A,A=T;break e}}else if(re.elementType===te||typeof te=="object"&&te!==null&&te.$$typeof===Ie&&Ud(te)===re.type){a(A,re.sibling),T=u(re,_.props),T.ref=cr(A,re,_),T.return=A,A=T;break e}a(A,re);break}else n(A,re);re=re.sibling}_.type===V?(T=Hn(_.props.children,A.mode,G,_.key),T.return=A,A=T):(G=zi(_.type,_.key,_.props,null,A.mode,G),G.ref=cr(A,T,_),G.return=A,A=G)}return y(A);case F:e:{for(re=_.key;T!==null;){if(T.key===re)if(T.tag===4&&T.stateNode.containerInfo===_.containerInfo&&T.stateNode.implementation===_.implementation){a(A,T.sibling),T=u(T,_.children||[]),T.return=A,A=T;break e}else{a(A,T);break}else n(A,T);T=T.sibling}T=El(_,A.mode,G),T.return=A,A=T}return y(A);case Ie:return re=_._init,Fe(A,T,re(_._payload),G)}if(Fs(_))return q(A,T,_,G);if(J(_))return Z(A,T,_,G);yi(A,_)}return typeof _=="string"&&_!==""||typeof _=="number"?(_=""+_,T!==null&&T.tag===6?(a(A,T.sibling),T=u(T,_),T.return=A,A=T):(a(A,T),T=Pl(_,A.mode,G),T.return=A,A=T),y(A)):a(A,T)}return Fe}var xs=Wd(!0),$d=Wd(!1),vi=gn(null),xi=null,ws=null,Fo=null;function Bo(){Fo=ws=xi=null}function Oo(e){var n=vi.current;Pe(vi),e._currentValue=n}function zo(e,n,a){for(;e!==null;){var l=e.alternate;if((e.childLanes&n)!==n?(e.childLanes|=n,l!==null&&(l.childLanes|=n)):l!==null&&(l.childLanes&n)!==n&&(l.childLanes|=n),e===a)break;e=e.return}}function bs(e,n){xi=e,Fo=ws=null,e=e.dependencies,e!==null&&e.firstContext!==null&&((e.lanes&n)!==0&&(ht=!0),e.firstContext=null)}function Ct(e){var n=e._currentValue;if(Fo!==e)if(e={context:e,memoizedValue:n,next:null},ws===null){if(xi===null)throw Error(i(308));ws=e,xi.dependencies={lanes:0,firstContext:e}}else ws=ws.next=e;return n}var Fn=null;function Uo(e){Fn===null?Fn=[e]:Fn.push(e)}function Hd(e,n,a,l){var u=n.interleaved;return u===null?(a.next=a,Uo(n)):(a.next=u.next,u.next=a),n.interleaved=a,nn(e,l)}function nn(e,n){e.lanes|=n;var a=e.alternate;for(a!==null&&(a.lanes|=n),a=e,e=e.return;e!==null;)e.childLanes|=n,a=e.alternate,a!==null&&(a.childLanes|=n),a=e,e=e.return;return a.tag===3?a.stateNode:null}var xn=!1;function Wo(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function Gd(e,n){e=e.updateQueue,n.updateQueue===e&&(n.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function sn(e,n){return{eventTime:e,lane:n,tag:0,payload:null,callback:null,next:null}}function wn(e,n,a){var l=e.updateQueue;if(l===null)return null;if(l=l.shared,(me&2)!==0){var u=l.pending;return u===null?n.next=n:(n.next=u.next,u.next=n),l.pending=n,nn(e,a)}return u=l.interleaved,u===null?(n.next=n,Uo(l)):(n.next=u.next,u.next=n),l.interleaved=n,nn(e,a)}function wi(e,n,a){if(n=n.updateQueue,n!==null&&(n=n.shared,(a&4194240)!==0)){var l=n.lanes;l&=e.pendingLanes,a|=l,n.lanes=a,no(e,a)}}function Kd(e,n){var a=e.updateQueue,l=e.alternate;if(l!==null&&(l=l.updateQueue,a===l)){var u=null,m=null;if(a=a.firstBaseUpdate,a!==null){do{var y={eventTime:a.eventTime,lane:a.lane,tag:a.tag,payload:a.payload,callback:a.callback,next:null};m===null?u=m=y:m=m.next=y,a=a.next}while(a!==null);m===null?u=m=n:m=m.next=n}else u=m=n;a={baseState:l.baseState,firstBaseUpdate:u,lastBaseUpdate:m,shared:l.shared,effects:l.effects},e.updateQueue=a;return}e=a.lastBaseUpdate,e===null?a.firstBaseUpdate=n:e.next=n,a.lastBaseUpdate=n}function bi(e,n,a,l){var u=e.updateQueue;xn=!1;var m=u.firstBaseUpdate,y=u.lastBaseUpdate,b=u.shared.pending;if(b!==null){u.shared.pending=null;var C=b,R=C.next;C.next=null,y===null?m=R:y.next=R,y=C;var W=e.alternate;W!==null&&(W=W.updateQueue,b=W.lastBaseUpdate,b!==y&&(b===null?W.firstBaseUpdate=R:b.next=R,W.lastBaseUpdate=C))}if(m!==null){var $=u.baseState;y=0,W=R=C=null,b=m;do{var U=b.lane,X=b.eventTime;if((l&U)===U){W!==null&&(W=W.next={eventTime:X,lane:0,tag:b.tag,payload:b.payload,callback:b.callback,next:null});e:{var q=e,Z=b;switch(U=n,X=a,Z.tag){case 1:if(q=Z.payload,typeof q=="function"){$=q.call(X,$,U);break e}$=q;break e;case 3:q.flags=q.flags&-65537|128;case 0:if(q=Z.payload,U=typeof q=="function"?q.call(X,$,U):q,U==null)break e;$=K({},$,U);break e;case 2:xn=!0}}b.callback!==null&&b.lane!==0&&(e.flags|=64,U=u.effects,U===null?u.effects=[b]:U.push(b))}else X={eventTime:X,lane:U,tag:b.tag,payload:b.payload,callback:b.callback,next:null},W===null?(R=W=X,C=$):W=W.next=X,y|=U;if(b=b.next,b===null){if(b=u.shared.pending,b===null)break;U=b,b=U.next,U.next=null,u.lastBaseUpdate=U,u.shared.pending=null}}while(!0);if(W===null&&(C=$),u.baseState=C,u.firstBaseUpdate=R,u.lastBaseUpdate=W,n=u.shared.interleaved,n!==null){u=n;do y|=u.lane,u=u.next;while(u!==n)}else m===null&&(u.shared.lanes=0);zn|=y,e.lanes=y,e.memoizedState=$}}function Xd(e,n,a){if(e=n.effects,n.effects=null,e!==null)for(n=0;n<e.length;n++){var l=e[n],u=l.callback;if(u!==null){if(l.callback=null,l=a,typeof u!="function")throw Error(i(191,u));u.call(l)}}}var ur={},Ht=gn(ur),dr=gn(ur),hr=gn(ur);function Bn(e){if(e===ur)throw Error(i(174));return e}function $o(e,n){switch(Ce(hr,n),Ce(dr,e),Ce(Ht,ur),e=n.nodeType,e){case 9:case 11:n=(n=n.documentElement)?n.namespaceURI:$a(null,"");break;default:e=e===8?n.parentNode:n,n=e.namespaceURI||null,e=e.tagName,n=$a(n,e)}Pe(Ht),Ce(Ht,n)}function ks(){Pe(Ht),Pe(dr),Pe(hr)}function Yd(e){Bn(hr.current);var n=Bn(Ht.current),a=$a(n,e.type);n!==a&&(Ce(dr,e),Ce(Ht,a))}function Ho(e){dr.current===e&&(Pe(Ht),Pe(dr))}var Ae=gn(0);function ki(e){for(var n=e;n!==null;){if(n.tag===13){var a=n.memoizedState;if(a!==null&&(a=a.dehydrated,a===null||a.data==="$?"||a.data==="$!"))return n}else if(n.tag===19&&n.memoizedProps.revealOrder!==void 0){if((n.flags&128)!==0)return n}else if(n.child!==null){n.child.return=n,n=n.child;continue}if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return null;n=n.return}n.sibling.return=n.return,n=n.sibling}return null}var Go=[];function Ko(){for(var e=0;e<Go.length;e++)Go[e]._workInProgressVersionPrimary=null;Go.length=0}var ji=I.ReactCurrentDispatcher,Xo=I.ReactCurrentBatchConfig,On=0,_e=null,ze=null,Ke=null,Si=!1,mr=!1,fr=0,yv=0;function nt(){throw Error(i(321))}function Yo(e,n){if(n===null)return!1;for(var a=0;a<n.length&&a<e.length;a++)if(!_t(e[a],n[a]))return!1;return!0}function qo(e,n,a,l,u,m){if(On=m,_e=n,n.memoizedState=null,n.updateQueue=null,n.lanes=0,ji.current=e===null||e.memoizedState===null?bv:kv,e=a(l,u),mr){m=0;do{if(mr=!1,fr=0,25<=m)throw Error(i(301));m+=1,Ke=ze=null,n.updateQueue=null,ji.current=jv,e=a(l,u)}while(mr)}if(ji.current=Ti,n=ze!==null&&ze.next!==null,On=0,Ke=ze=_e=null,Si=!1,n)throw Error(i(300));return e}function Qo(){var e=fr!==0;return fr=0,e}function Gt(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return Ke===null?_e.memoizedState=Ke=e:Ke=Ke.next=e,Ke}function Tt(){if(ze===null){var e=_e.alternate;e=e!==null?e.memoizedState:null}else e=ze.next;var n=Ke===null?_e.memoizedState:Ke.next;if(n!==null)Ke=n,ze=e;else{if(e===null)throw Error(i(310));ze=e,e={memoizedState:ze.memoizedState,baseState:ze.baseState,baseQueue:ze.baseQueue,queue:ze.queue,next:null},Ke===null?_e.memoizedState=Ke=e:Ke=Ke.next=e}return Ke}function pr(e,n){return typeof n=="function"?n(e):n}function Jo(e){var n=Tt(),a=n.queue;if(a===null)throw Error(i(311));a.lastRenderedReducer=e;var l=ze,u=l.baseQueue,m=a.pending;if(m!==null){if(u!==null){var y=u.next;u.next=m.next,m.next=y}l.baseQueue=u=m,a.pending=null}if(u!==null){m=u.next,l=l.baseState;var b=y=null,C=null,R=m;do{var W=R.lane;if((On&W)===W)C!==null&&(C=C.next={lane:0,action:R.action,hasEagerState:R.hasEagerState,eagerState:R.eagerState,next:null}),l=R.hasEagerState?R.eagerState:e(l,R.action);else{var $={lane:W,action:R.action,hasEagerState:R.hasEagerState,eagerState:R.eagerState,next:null};C===null?(b=C=$,y=l):C=C.next=$,_e.lanes|=W,zn|=W}R=R.next}while(R!==null&&R!==m);C===null?y=l:C.next=b,_t(l,n.memoizedState)||(ht=!0),n.memoizedState=l,n.baseState=y,n.baseQueue=C,a.lastRenderedState=l}if(e=a.interleaved,e!==null){u=e;do m=u.lane,_e.lanes|=m,zn|=m,u=u.next;while(u!==e)}else u===null&&(a.lanes=0);return[n.memoizedState,a.dispatch]}function Zo(e){var n=Tt(),a=n.queue;if(a===null)throw Error(i(311));a.lastRenderedReducer=e;var l=a.dispatch,u=a.pending,m=n.memoizedState;if(u!==null){a.pending=null;var y=u=u.next;do m=e(m,y.action),y=y.next;while(y!==u);_t(m,n.memoizedState)||(ht=!0),n.memoizedState=m,n.baseQueue===null&&(n.baseState=m),a.lastRenderedState=m}return[m,l]}function qd(){}function Qd(e,n){var a=_e,l=Tt(),u=n(),m=!_t(l.memoizedState,u);if(m&&(l.memoizedState=u,ht=!0),l=l.queue,el(eh.bind(null,a,l,e),[e]),l.getSnapshot!==n||m||Ke!==null&&Ke.memoizedState.tag&1){if(a.flags|=2048,gr(9,Zd.bind(null,a,l,u,n),void 0,null),Xe===null)throw Error(i(349));(On&30)!==0||Jd(a,n,u)}return u}function Jd(e,n,a){e.flags|=16384,e={getSnapshot:n,value:a},n=_e.updateQueue,n===null?(n={lastEffect:null,stores:null},_e.updateQueue=n,n.stores=[e]):(a=n.stores,a===null?n.stores=[e]:a.push(e))}function Zd(e,n,a,l){n.value=a,n.getSnapshot=l,th(n)&&nh(e)}function eh(e,n,a){return a(function(){th(n)&&nh(e)})}function th(e){var n=e.getSnapshot;e=e.value;try{var a=n();return!_t(e,a)}catch{return!0}}function nh(e){var n=nn(e,1);n!==null&&Vt(n,e,1,-1)}function sh(e){var n=Gt();return typeof e=="function"&&(e=e()),n.memoizedState=n.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:pr,lastRenderedState:e},n.queue=e,e=e.dispatch=wv.bind(null,_e,e),[n.memoizedState,e]}function gr(e,n,a,l){return e={tag:e,create:n,destroy:a,deps:l,next:null},n=_e.updateQueue,n===null?(n={lastEffect:null,stores:null},_e.updateQueue=n,n.lastEffect=e.next=e):(a=n.lastEffect,a===null?n.lastEffect=e.next=e:(l=a.next,a.next=e,e.next=l,n.lastEffect=e)),e}function rh(){return Tt().memoizedState}function Ni(e,n,a,l){var u=Gt();_e.flags|=e,u.memoizedState=gr(1|n,a,void 0,l===void 0?null:l)}function Ci(e,n,a,l){var u=Tt();l=l===void 0?null:l;var m=void 0;if(ze!==null){var y=ze.memoizedState;if(m=y.destroy,l!==null&&Yo(l,y.deps)){u.memoizedState=gr(n,a,m,l);return}}_e.flags|=e,u.memoizedState=gr(1|n,a,m,l)}function ih(e,n){return Ni(8390656,8,e,n)}function el(e,n){return Ci(2048,8,e,n)}function ah(e,n){return Ci(4,2,e,n)}function oh(e,n){return Ci(4,4,e,n)}function lh(e,n){if(typeof n=="function")return e=e(),n(e),function(){n(null)};if(n!=null)return e=e(),n.current=e,function(){n.current=null}}function ch(e,n,a){return a=a!=null?a.concat([e]):null,Ci(4,4,lh.bind(null,n,e),a)}function tl(){}function uh(e,n){var a=Tt();n=n===void 0?null:n;var l=a.memoizedState;return l!==null&&n!==null&&Yo(n,l[1])?l[0]:(a.memoizedState=[e,n],e)}function dh(e,n){var a=Tt();n=n===void 0?null:n;var l=a.memoizedState;return l!==null&&n!==null&&Yo(n,l[1])?l[0]:(e=e(),a.memoizedState=[e,n],e)}function hh(e,n,a){return(On&21)===0?(e.baseState&&(e.baseState=!1,ht=!0),e.memoizedState=a):(_t(a,n)||(a=Uu(),_e.lanes|=a,zn|=a,e.baseState=!0),n)}function vv(e,n){var a=be;be=a!==0&&4>a?a:4,e(!0);var l=Xo.transition;Xo.transition={};try{e(!1),n()}finally{be=a,Xo.transition=l}}function mh(){return Tt().memoizedState}function xv(e,n,a){var l=Sn(e);if(a={lane:l,action:a,hasEagerState:!1,eagerState:null,next:null},fh(e))ph(n,a);else if(a=Hd(e,n,a,l),a!==null){var u=ot();Vt(a,e,l,u),gh(a,n,l)}}function wv(e,n,a){var l=Sn(e),u={lane:l,action:a,hasEagerState:!1,eagerState:null,next:null};if(fh(e))ph(n,u);else{var m=e.alternate;if(e.lanes===0&&(m===null||m.lanes===0)&&(m=n.lastRenderedReducer,m!==null))try{var y=n.lastRenderedState,b=m(y,a);if(u.hasEagerState=!0,u.eagerState=b,_t(b,y)){var C=n.interleaved;C===null?(u.next=u,Uo(n)):(u.next=C.next,C.next=u),n.interleaved=u;return}}catch{}finally{}a=Hd(e,n,u,l),a!==null&&(u=ot(),Vt(a,e,l,u),gh(a,n,l))}}function fh(e){var n=e.alternate;return e===_e||n!==null&&n===_e}function ph(e,n){mr=Si=!0;var a=e.pending;a===null?n.next=n:(n.next=a.next,a.next=n),e.pending=n}function gh(e,n,a){if((a&4194240)!==0){var l=n.lanes;l&=e.pendingLanes,a|=l,n.lanes=a,no(e,a)}}var Ti={readContext:Ct,useCallback:nt,useContext:nt,useEffect:nt,useImperativeHandle:nt,useInsertionEffect:nt,useLayoutEffect:nt,useMemo:nt,useReducer:nt,useRef:nt,useState:nt,useDebugValue:nt,useDeferredValue:nt,useTransition:nt,useMutableSource:nt,useSyncExternalStore:nt,useId:nt,unstable_isNewReconciler:!1},bv={readContext:Ct,useCallback:function(e,n){return Gt().memoizedState=[e,n===void 0?null:n],e},useContext:Ct,useEffect:ih,useImperativeHandle:function(e,n,a){return a=a!=null?a.concat([e]):null,Ni(4194308,4,lh.bind(null,n,e),a)},useLayoutEffect:function(e,n){return Ni(4194308,4,e,n)},useInsertionEffect:function(e,n){return Ni(4,2,e,n)},useMemo:function(e,n){var a=Gt();return n=n===void 0?null:n,e=e(),a.memoizedState=[e,n],e},useReducer:function(e,n,a){var l=Gt();return n=a!==void 0?a(n):n,l.memoizedState=l.baseState=n,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:n},l.queue=e,e=e.dispatch=xv.bind(null,_e,e),[l.memoizedState,e]},useRef:function(e){var n=Gt();return e={current:e},n.memoizedState=e},useState:sh,useDebugValue:tl,useDeferredValue:function(e){return Gt().memoizedState=e},useTransition:function(){var e=sh(!1),n=e[0];return e=vv.bind(null,e[1]),Gt().memoizedState=e,[n,e]},useMutableSource:function(){},useSyncExternalStore:function(e,n,a){var l=_e,u=Gt();if(Me){if(a===void 0)throw Error(i(407));a=a()}else{if(a=n(),Xe===null)throw Error(i(349));(On&30)!==0||Jd(l,n,a)}u.memoizedState=a;var m={value:a,getSnapshot:n};return u.queue=m,ih(eh.bind(null,l,m,e),[e]),l.flags|=2048,gr(9,Zd.bind(null,l,m,a,n),void 0,null),a},useId:function(){var e=Gt(),n=Xe.identifierPrefix;if(Me){var a=tn,l=en;a=(l&~(1<<32-At(l)-1)).toString(32)+a,n=":"+n+"R"+a,a=fr++,0<a&&(n+="H"+a.toString(32)),n+=":"}else a=yv++,n=":"+n+"r"+a.toString(32)+":";return e.memoizedState=n},unstable_isNewReconciler:!1},kv={readContext:Ct,useCallback:uh,useContext:Ct,useEffect:el,useImperativeHandle:ch,useInsertionEffect:ah,useLayoutEffect:oh,useMemo:dh,useReducer:Jo,useRef:rh,useState:function(){return Jo(pr)},useDebugValue:tl,useDeferredValue:function(e){var n=Tt();return hh(n,ze.memoizedState,e)},useTransition:function(){var e=Jo(pr)[0],n=Tt().memoizedState;return[e,n]},useMutableSource:qd,useSyncExternalStore:Qd,useId:mh,unstable_isNewReconciler:!1},jv={readContext:Ct,useCallback:uh,useContext:Ct,useEffect:el,useImperativeHandle:ch,useInsertionEffect:ah,useLayoutEffect:oh,useMemo:dh,useReducer:Zo,useRef:rh,useState:function(){return Zo(pr)},useDebugValue:tl,useDeferredValue:function(e){var n=Tt();return ze===null?n.memoizedState=e:hh(n,ze.memoizedState,e)},useTransition:function(){var e=Zo(pr)[0],n=Tt().memoizedState;return[e,n]},useMutableSource:qd,useSyncExternalStore:Qd,useId:mh,unstable_isNewReconciler:!1};function Rt(e,n){if(e&&e.defaultProps){n=K({},n),e=e.defaultProps;for(var a in e)n[a]===void 0&&(n[a]=e[a]);return n}return n}function nl(e,n,a,l){n=e.memoizedState,a=a(l,n),a=a==null?n:K({},n,a),e.memoizedState=a,e.lanes===0&&(e.updateQueue.baseState=a)}var Pi={isMounted:function(e){return(e=e._reactInternals)?Dn(e)===e:!1},enqueueSetState:function(e,n,a){e=e._reactInternals;var l=ot(),u=Sn(e),m=sn(l,u);m.payload=n,a!=null&&(m.callback=a),n=wn(e,m,u),n!==null&&(Vt(n,e,u,l),wi(n,e,u))},enqueueReplaceState:function(e,n,a){e=e._reactInternals;var l=ot(),u=Sn(e),m=sn(l,u);m.tag=1,m.payload=n,a!=null&&(m.callback=a),n=wn(e,m,u),n!==null&&(Vt(n,e,u,l),wi(n,e,u))},enqueueForceUpdate:function(e,n){e=e._reactInternals;var a=ot(),l=Sn(e),u=sn(a,l);u.tag=2,n!=null&&(u.callback=n),n=wn(e,u,l),n!==null&&(Vt(n,e,l,a),wi(n,e,l))}};function yh(e,n,a,l,u,m,y){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(l,m,y):n.prototype&&n.prototype.isPureReactComponent?!nr(a,l)||!nr(u,m):!0}function vh(e,n,a){var l=!1,u=yn,m=n.contextType;return typeof m=="object"&&m!==null?m=Ct(m):(u=dt(n)?Ln:tt.current,l=n.contextTypes,m=(l=l!=null)?ps(e,u):yn),n=new n(a,m),e.memoizedState=n.state!==null&&n.state!==void 0?n.state:null,n.updater=Pi,e.stateNode=n,n._reactInternals=e,l&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=u,e.__reactInternalMemoizedMaskedChildContext=m),n}function xh(e,n,a,l){e=n.state,typeof n.componentWillReceiveProps=="function"&&n.componentWillReceiveProps(a,l),typeof n.UNSAFE_componentWillReceiveProps=="function"&&n.UNSAFE_componentWillReceiveProps(a,l),n.state!==e&&Pi.enqueueReplaceState(n,n.state,null)}function sl(e,n,a,l){var u=e.stateNode;u.props=a,u.state=e.memoizedState,u.refs={},Wo(e);var m=n.contextType;typeof m=="object"&&m!==null?u.context=Ct(m):(m=dt(n)?Ln:tt.current,u.context=ps(e,m)),u.state=e.memoizedState,m=n.getDerivedStateFromProps,typeof m=="function"&&(nl(e,n,m,a),u.state=e.memoizedState),typeof n.getDerivedStateFromProps=="function"||typeof u.getSnapshotBeforeUpdate=="function"||typeof u.UNSAFE_componentWillMount!="function"&&typeof u.componentWillMount!="function"||(n=u.state,typeof u.componentWillMount=="function"&&u.componentWillMount(),typeof u.UNSAFE_componentWillMount=="function"&&u.UNSAFE_componentWillMount(),n!==u.state&&Pi.enqueueReplaceState(u,u.state,null),bi(e,a,u,l),u.state=e.memoizedState),typeof u.componentDidMount=="function"&&(e.flags|=4194308)}function js(e,n){try{var a="",l=n;do a+=fe(l),l=l.return;while(l);var u=a}catch(m){u=`
Error generating stack: `+m.message+`
`+m.stack}return{value:e,source:n,stack:u,digest:null}}function rl(e,n,a){return{value:e,source:null,stack:a??null,digest:n??null}}function il(e,n){try{console.error(n.value)}catch(a){setTimeout(function(){throw a})}}var Sv=typeof WeakMap=="function"?WeakMap:Map;function wh(e,n,a){a=sn(-1,a),a.tag=3,a.payload={element:null};var l=n.value;return a.callback=function(){Li||(Li=!0,wl=l),il(e,n)},a}function bh(e,n,a){a=sn(-1,a),a.tag=3;var l=e.type.getDerivedStateFromError;if(typeof l=="function"){var u=n.value;a.payload=function(){return l(u)},a.callback=function(){il(e,n)}}var m=e.stateNode;return m!==null&&typeof m.componentDidCatch=="function"&&(a.callback=function(){il(e,n),typeof l!="function"&&(kn===null?kn=new Set([this]):kn.add(this));var y=n.stack;this.componentDidCatch(n.value,{componentStack:y!==null?y:""})}),a}function kh(e,n,a){var l=e.pingCache;if(l===null){l=e.pingCache=new Sv;var u=new Set;l.set(n,u)}else u=l.get(n),u===void 0&&(u=new Set,l.set(n,u));u.has(a)||(u.add(a),e=Fv.bind(null,e,n,a),n.then(e,e))}function jh(e){do{var n;if((n=e.tag===13)&&(n=e.memoizedState,n=n!==null?n.dehydrated!==null:!0),n)return e;e=e.return}while(e!==null);return null}function Sh(e,n,a,l,u){return(e.mode&1)===0?(e===n?e.flags|=65536:(e.flags|=128,a.flags|=131072,a.flags&=-52805,a.tag===1&&(a.alternate===null?a.tag=17:(n=sn(-1,1),n.tag=2,wn(a,n,1))),a.lanes|=1),e):(e.flags|=65536,e.lanes=u,e)}var Nv=I.ReactCurrentOwner,ht=!1;function at(e,n,a,l){n.child=e===null?$d(n,null,a,l):xs(n,e.child,a,l)}function Nh(e,n,a,l,u){a=a.render;var m=n.ref;return bs(n,u),l=qo(e,n,a,l,m,u),a=Qo(),e!==null&&!ht?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~u,rn(e,n,u)):(Me&&a&&Do(n),n.flags|=1,at(e,n,l,u),n.child)}function Ch(e,n,a,l,u){if(e===null){var m=a.type;return typeof m=="function"&&!Tl(m)&&m.defaultProps===void 0&&a.compare===null&&a.defaultProps===void 0?(n.tag=15,n.type=m,Th(e,n,m,l,u)):(e=zi(a.type,null,l,n,n.mode,u),e.ref=n.ref,e.return=n,n.child=e)}if(m=e.child,(e.lanes&u)===0){var y=m.memoizedProps;if(a=a.compare,a=a!==null?a:nr,a(y,l)&&e.ref===n.ref)return rn(e,n,u)}return n.flags|=1,e=Cn(m,l),e.ref=n.ref,e.return=n,n.child=e}function Th(e,n,a,l,u){if(e!==null){var m=e.memoizedProps;if(nr(m,l)&&e.ref===n.ref)if(ht=!1,n.pendingProps=l=m,(e.lanes&u)!==0)(e.flags&131072)!==0&&(ht=!0);else return n.lanes=e.lanes,rn(e,n,u)}return al(e,n,a,l,u)}function Ph(e,n,a){var l=n.pendingProps,u=l.children,m=e!==null?e.memoizedState:null;if(l.mode==="hidden")if((n.mode&1)===0)n.memoizedState={baseLanes:0,cachePool:null,transitions:null},Ce(Ns,bt),bt|=a;else{if((a&1073741824)===0)return e=m!==null?m.baseLanes|a:a,n.lanes=n.childLanes=1073741824,n.memoizedState={baseLanes:e,cachePool:null,transitions:null},n.updateQueue=null,Ce(Ns,bt),bt|=e,null;n.memoizedState={baseLanes:0,cachePool:null,transitions:null},l=m!==null?m.baseLanes:a,Ce(Ns,bt),bt|=l}else m!==null?(l=m.baseLanes|a,n.memoizedState=null):l=a,Ce(Ns,bt),bt|=l;return at(e,n,u,a),n.child}function Eh(e,n){var a=n.ref;(e===null&&a!==null||e!==null&&e.ref!==a)&&(n.flags|=512,n.flags|=2097152)}function al(e,n,a,l,u){var m=dt(a)?Ln:tt.current;return m=ps(n,m),bs(n,u),a=qo(e,n,a,l,m,u),l=Qo(),e!==null&&!ht?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~u,rn(e,n,u)):(Me&&l&&Do(n),n.flags|=1,at(e,n,a,u),n.child)}function Mh(e,n,a,l,u){if(dt(a)){var m=!0;hi(n)}else m=!1;if(bs(n,u),n.stateNode===null)Mi(e,n),vh(n,a,l),sl(n,a,l,u),l=!0;else if(e===null){var y=n.stateNode,b=n.memoizedProps;y.props=b;var C=y.context,R=a.contextType;typeof R=="object"&&R!==null?R=Ct(R):(R=dt(a)?Ln:tt.current,R=ps(n,R));var W=a.getDerivedStateFromProps,$=typeof W=="function"||typeof y.getSnapshotBeforeUpdate=="function";$||typeof y.UNSAFE_componentWillReceiveProps!="function"&&typeof y.componentWillReceiveProps!="function"||(b!==l||C!==R)&&xh(n,y,l,R),xn=!1;var U=n.memoizedState;y.state=U,bi(n,l,y,u),C=n.memoizedState,b!==l||U!==C||ut.current||xn?(typeof W=="function"&&(nl(n,a,W,l),C=n.memoizedState),(b=xn||yh(n,a,b,l,U,C,R))?($||typeof y.UNSAFE_componentWillMount!="function"&&typeof y.componentWillMount!="function"||(typeof y.componentWillMount=="function"&&y.componentWillMount(),typeof y.UNSAFE_componentWillMount=="function"&&y.UNSAFE_componentWillMount()),typeof y.componentDidMount=="function"&&(n.flags|=4194308)):(typeof y.componentDidMount=="function"&&(n.flags|=4194308),n.memoizedProps=l,n.memoizedState=C),y.props=l,y.state=C,y.context=R,l=b):(typeof y.componentDidMount=="function"&&(n.flags|=4194308),l=!1)}else{y=n.stateNode,Gd(e,n),b=n.memoizedProps,R=n.type===n.elementType?b:Rt(n.type,b),y.props=R,$=n.pendingProps,U=y.context,C=a.contextType,typeof C=="object"&&C!==null?C=Ct(C):(C=dt(a)?Ln:tt.current,C=ps(n,C));var X=a.getDerivedStateFromProps;(W=typeof X=="function"||typeof y.getSnapshotBeforeUpdate=="function")||typeof y.UNSAFE_componentWillReceiveProps!="function"&&typeof y.componentWillReceiveProps!="function"||(b!==$||U!==C)&&xh(n,y,l,C),xn=!1,U=n.memoizedState,y.state=U,bi(n,l,y,u);var q=n.memoizedState;b!==$||U!==q||ut.current||xn?(typeof X=="function"&&(nl(n,a,X,l),q=n.memoizedState),(R=xn||yh(n,a,R,l,U,q,C)||!1)?(W||typeof y.UNSAFE_componentWillUpdate!="function"&&typeof y.componentWillUpdate!="function"||(typeof y.componentWillUpdate=="function"&&y.componentWillUpdate(l,q,C),typeof y.UNSAFE_componentWillUpdate=="function"&&y.UNSAFE_componentWillUpdate(l,q,C)),typeof y.componentDidUpdate=="function"&&(n.flags|=4),typeof y.getSnapshotBeforeUpdate=="function"&&(n.flags|=1024)):(typeof y.componentDidUpdate!="function"||b===e.memoizedProps&&U===e.memoizedState||(n.flags|=4),typeof y.getSnapshotBeforeUpdate!="function"||b===e.memoizedProps&&U===e.memoizedState||(n.flags|=1024),n.memoizedProps=l,n.memoizedState=q),y.props=l,y.state=q,y.context=C,l=R):(typeof y.componentDidUpdate!="function"||b===e.memoizedProps&&U===e.memoizedState||(n.flags|=4),typeof y.getSnapshotBeforeUpdate!="function"||b===e.memoizedProps&&U===e.memoizedState||(n.flags|=1024),l=!1)}return ol(e,n,a,l,m,u)}function ol(e,n,a,l,u,m){Eh(e,n);var y=(n.flags&128)!==0;if(!l&&!y)return u&&Ld(n,a,!1),rn(e,n,m);l=n.stateNode,Nv.current=n;var b=y&&typeof a.getDerivedStateFromError!="function"?null:l.render();return n.flags|=1,e!==null&&y?(n.child=xs(n,e.child,null,m),n.child=xs(n,null,b,m)):at(e,n,b,m),n.memoizedState=l.state,u&&Ld(n,a,!0),n.child}function Ah(e){var n=e.stateNode;n.pendingContext?Dd(e,n.pendingContext,n.pendingContext!==n.context):n.context&&Dd(e,n.context,!1),$o(e,n.containerInfo)}function _h(e,n,a,l,u){return vs(),Vo(u),n.flags|=256,at(e,n,a,l),n.child}var ll={dehydrated:null,treeContext:null,retryLane:0};function cl(e){return{baseLanes:e,cachePool:null,transitions:null}}function Dh(e,n,a){var l=n.pendingProps,u=Ae.current,m=!1,y=(n.flags&128)!==0,b;if((b=y)||(b=e!==null&&e.memoizedState===null?!1:(u&2)!==0),b?(m=!0,n.flags&=-129):(e===null||e.memoizedState!==null)&&(u|=1),Ce(Ae,u&1),e===null)return Io(n),e=n.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?((n.mode&1)===0?n.lanes=1:e.data==="$!"?n.lanes=8:n.lanes=1073741824,null):(y=l.children,e=l.fallback,m?(l=n.mode,m=n.child,y={mode:"hidden",children:y},(l&1)===0&&m!==null?(m.childLanes=0,m.pendingProps=y):m=Ui(y,l,0,null),e=Hn(e,l,a,null),m.return=n,e.return=n,m.sibling=e,n.child=m,n.child.memoizedState=cl(a),n.memoizedState=ll,e):ul(n,y));if(u=e.memoizedState,u!==null&&(b=u.dehydrated,b!==null))return Cv(e,n,y,l,b,u,a);if(m){m=l.fallback,y=n.mode,u=e.child,b=u.sibling;var C={mode:"hidden",children:l.children};return(y&1)===0&&n.child!==u?(l=n.child,l.childLanes=0,l.pendingProps=C,n.deletions=null):(l=Cn(u,C),l.subtreeFlags=u.subtreeFlags&14680064),b!==null?m=Cn(b,m):(m=Hn(m,y,a,null),m.flags|=2),m.return=n,l.return=n,l.sibling=m,n.child=l,l=m,m=n.child,y=e.child.memoizedState,y=y===null?cl(a):{baseLanes:y.baseLanes|a,cachePool:null,transitions:y.transitions},m.memoizedState=y,m.childLanes=e.childLanes&~a,n.memoizedState=ll,l}return m=e.child,e=m.sibling,l=Cn(m,{mode:"visible",children:l.children}),(n.mode&1)===0&&(l.lanes=a),l.return=n,l.sibling=null,e!==null&&(a=n.deletions,a===null?(n.deletions=[e],n.flags|=16):a.push(e)),n.child=l,n.memoizedState=null,l}function ul(e,n){return n=Ui({mode:"visible",children:n},e.mode,0,null),n.return=e,e.child=n}function Ei(e,n,a,l){return l!==null&&Vo(l),xs(n,e.child,null,a),e=ul(n,n.pendingProps.children),e.flags|=2,n.memoizedState=null,e}function Cv(e,n,a,l,u,m,y){if(a)return n.flags&256?(n.flags&=-257,l=rl(Error(i(422))),Ei(e,n,y,l)):n.memoizedState!==null?(n.child=e.child,n.flags|=128,null):(m=l.fallback,u=n.mode,l=Ui({mode:"visible",children:l.children},u,0,null),m=Hn(m,u,y,null),m.flags|=2,l.return=n,m.return=n,l.sibling=m,n.child=l,(n.mode&1)!==0&&xs(n,e.child,null,y),n.child.memoizedState=cl(y),n.memoizedState=ll,m);if((n.mode&1)===0)return Ei(e,n,y,null);if(u.data==="$!"){if(l=u.nextSibling&&u.nextSibling.dataset,l)var b=l.dgst;return l=b,m=Error(i(419)),l=rl(m,l,void 0),Ei(e,n,y,l)}if(b=(y&e.childLanes)!==0,ht||b){if(l=Xe,l!==null){switch(y&-y){case 4:u=2;break;case 16:u=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:u=32;break;case 536870912:u=268435456;break;default:u=0}u=(u&(l.suspendedLanes|y))!==0?0:u,u!==0&&u!==m.retryLane&&(m.retryLane=u,nn(e,u),Vt(l,e,u,-1))}return Cl(),l=rl(Error(i(421))),Ei(e,n,y,l)}return u.data==="$?"?(n.flags|=128,n.child=e.child,n=Bv.bind(null,e),u._reactRetry=n,null):(e=m.treeContext,wt=pn(u.nextSibling),xt=n,Me=!0,Dt=null,e!==null&&(St[Nt++]=en,St[Nt++]=tn,St[Nt++]=In,en=e.id,tn=e.overflow,In=n),n=ul(n,l.children),n.flags|=4096,n)}function Rh(e,n,a){e.lanes|=n;var l=e.alternate;l!==null&&(l.lanes|=n),zo(e.return,n,a)}function dl(e,n,a,l,u){var m=e.memoizedState;m===null?e.memoizedState={isBackwards:n,rendering:null,renderingStartTime:0,last:l,tail:a,tailMode:u}:(m.isBackwards=n,m.rendering=null,m.renderingStartTime=0,m.last=l,m.tail=a,m.tailMode=u)}function Lh(e,n,a){var l=n.pendingProps,u=l.revealOrder,m=l.tail;if(at(e,n,l.children,a),l=Ae.current,(l&2)!==0)l=l&1|2,n.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=n.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Rh(e,a,n);else if(e.tag===19)Rh(e,a,n);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===n)break e;for(;e.sibling===null;){if(e.return===null||e.return===n)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}l&=1}if(Ce(Ae,l),(n.mode&1)===0)n.memoizedState=null;else switch(u){case"forwards":for(a=n.child,u=null;a!==null;)e=a.alternate,e!==null&&ki(e)===null&&(u=a),a=a.sibling;a=u,a===null?(u=n.child,n.child=null):(u=a.sibling,a.sibling=null),dl(n,!1,u,a,m);break;case"backwards":for(a=null,u=n.child,n.child=null;u!==null;){if(e=u.alternate,e!==null&&ki(e)===null){n.child=u;break}e=u.sibling,u.sibling=a,a=u,u=e}dl(n,!0,a,null,m);break;case"together":dl(n,!1,null,null,void 0);break;default:n.memoizedState=null}return n.child}function Mi(e,n){(n.mode&1)===0&&e!==null&&(e.alternate=null,n.alternate=null,n.flags|=2)}function rn(e,n,a){if(e!==null&&(n.dependencies=e.dependencies),zn|=n.lanes,(a&n.childLanes)===0)return null;if(e!==null&&n.child!==e.child)throw Error(i(153));if(n.child!==null){for(e=n.child,a=Cn(e,e.pendingProps),n.child=a,a.return=n;e.sibling!==null;)e=e.sibling,a=a.sibling=Cn(e,e.pendingProps),a.return=n;a.sibling=null}return n.child}function Tv(e,n,a){switch(n.tag){case 3:Ah(n),vs();break;case 5:Yd(n);break;case 1:dt(n.type)&&hi(n);break;case 4:$o(n,n.stateNode.containerInfo);break;case 10:var l=n.type._context,u=n.memoizedProps.value;Ce(vi,l._currentValue),l._currentValue=u;break;case 13:if(l=n.memoizedState,l!==null)return l.dehydrated!==null?(Ce(Ae,Ae.current&1),n.flags|=128,null):(a&n.child.childLanes)!==0?Dh(e,n,a):(Ce(Ae,Ae.current&1),e=rn(e,n,a),e!==null?e.sibling:null);Ce(Ae,Ae.current&1);break;case 19:if(l=(a&n.childLanes)!==0,(e.flags&128)!==0){if(l)return Lh(e,n,a);n.flags|=128}if(u=n.memoizedState,u!==null&&(u.rendering=null,u.tail=null,u.lastEffect=null),Ce(Ae,Ae.current),l)break;return null;case 22:case 23:return n.lanes=0,Ph(e,n,a)}return rn(e,n,a)}var Ih,hl,Vh,Fh;Ih=function(e,n){for(var a=n.child;a!==null;){if(a.tag===5||a.tag===6)e.appendChild(a.stateNode);else if(a.tag!==4&&a.child!==null){a.child.return=a,a=a.child;continue}if(a===n)break;for(;a.sibling===null;){if(a.return===null||a.return===n)return;a=a.return}a.sibling.return=a.return,a=a.sibling}},hl=function(){},Vh=function(e,n,a,l){var u=e.memoizedProps;if(u!==l){e=n.stateNode,Bn(Ht.current);var m=null;switch(a){case"input":u=Oa(e,u),l=Oa(e,l),m=[];break;case"select":u=K({},u,{value:void 0}),l=K({},l,{value:void 0}),m=[];break;case"textarea":u=Wa(e,u),l=Wa(e,l),m=[];break;default:typeof u.onClick!="function"&&typeof l.onClick=="function"&&(e.onclick=ci)}Ha(a,l);var y;a=null;for(R in u)if(!l.hasOwnProperty(R)&&u.hasOwnProperty(R)&&u[R]!=null)if(R==="style"){var b=u[R];for(y in b)b.hasOwnProperty(y)&&(a||(a={}),a[y]="")}else R!=="dangerouslySetInnerHTML"&&R!=="children"&&R!=="suppressContentEditableWarning"&&R!=="suppressHydrationWarning"&&R!=="autoFocus"&&(c.hasOwnProperty(R)?m||(m=[]):(m=m||[]).push(R,null));for(R in l){var C=l[R];if(b=u!=null?u[R]:void 0,l.hasOwnProperty(R)&&C!==b&&(C!=null||b!=null))if(R==="style")if(b){for(y in b)!b.hasOwnProperty(y)||C&&C.hasOwnProperty(y)||(a||(a={}),a[y]="");for(y in C)C.hasOwnProperty(y)&&b[y]!==C[y]&&(a||(a={}),a[y]=C[y])}else a||(m||(m=[]),m.push(R,a)),a=C;else R==="dangerouslySetInnerHTML"?(C=C?C.__html:void 0,b=b?b.__html:void 0,C!=null&&b!==C&&(m=m||[]).push(R,C)):R==="children"?typeof C!="string"&&typeof C!="number"||(m=m||[]).push(R,""+C):R!=="suppressContentEditableWarning"&&R!=="suppressHydrationWarning"&&(c.hasOwnProperty(R)?(C!=null&&R==="onScroll"&&Te("scroll",e),m||b===C||(m=[])):(m=m||[]).push(R,C))}a&&(m=m||[]).push("style",a);var R=m;(n.updateQueue=R)&&(n.flags|=4)}},Fh=function(e,n,a,l){a!==l&&(n.flags|=4)};function yr(e,n){if(!Me)switch(e.tailMode){case"hidden":n=e.tail;for(var a=null;n!==null;)n.alternate!==null&&(a=n),n=n.sibling;a===null?e.tail=null:a.sibling=null;break;case"collapsed":a=e.tail;for(var l=null;a!==null;)a.alternate!==null&&(l=a),a=a.sibling;l===null?n||e.tail===null?e.tail=null:e.tail.sibling=null:l.sibling=null}}function st(e){var n=e.alternate!==null&&e.alternate.child===e.child,a=0,l=0;if(n)for(var u=e.child;u!==null;)a|=u.lanes|u.childLanes,l|=u.subtreeFlags&14680064,l|=u.flags&14680064,u.return=e,u=u.sibling;else for(u=e.child;u!==null;)a|=u.lanes|u.childLanes,l|=u.subtreeFlags,l|=u.flags,u.return=e,u=u.sibling;return e.subtreeFlags|=l,e.childLanes=a,n}function Pv(e,n,a){var l=n.pendingProps;switch(Ro(n),n.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return st(n),null;case 1:return dt(n.type)&&di(),st(n),null;case 3:return l=n.stateNode,ks(),Pe(ut),Pe(tt),Ko(),l.pendingContext&&(l.context=l.pendingContext,l.pendingContext=null),(e===null||e.child===null)&&(gi(n)?n.flags|=4:e===null||e.memoizedState.isDehydrated&&(n.flags&256)===0||(n.flags|=1024,Dt!==null&&(jl(Dt),Dt=null))),hl(e,n),st(n),null;case 5:Ho(n);var u=Bn(hr.current);if(a=n.type,e!==null&&n.stateNode!=null)Vh(e,n,a,l,u),e.ref!==n.ref&&(n.flags|=512,n.flags|=2097152);else{if(!l){if(n.stateNode===null)throw Error(i(166));return st(n),null}if(e=Bn(Ht.current),gi(n)){l=n.stateNode,a=n.type;var m=n.memoizedProps;switch(l[$t]=n,l[or]=m,e=(n.mode&1)!==0,a){case"dialog":Te("cancel",l),Te("close",l);break;case"iframe":case"object":case"embed":Te("load",l);break;case"video":case"audio":for(u=0;u<rr.length;u++)Te(rr[u],l);break;case"source":Te("error",l);break;case"img":case"image":case"link":Te("error",l),Te("load",l);break;case"details":Te("toggle",l);break;case"input":vu(l,m),Te("invalid",l);break;case"select":l._wrapperState={wasMultiple:!!m.multiple},Te("invalid",l);break;case"textarea":bu(l,m),Te("invalid",l)}Ha(a,m),u=null;for(var y in m)if(m.hasOwnProperty(y)){var b=m[y];y==="children"?typeof b=="string"?l.textContent!==b&&(m.suppressHydrationWarning!==!0&&li(l.textContent,b,e),u=["children",b]):typeof b=="number"&&l.textContent!==""+b&&(m.suppressHydrationWarning!==!0&&li(l.textContent,b,e),u=["children",""+b]):c.hasOwnProperty(y)&&b!=null&&y==="onScroll"&&Te("scroll",l)}switch(a){case"input":Br(l),wu(l,m,!0);break;case"textarea":Br(l),ju(l);break;case"select":case"option":break;default:typeof m.onClick=="function"&&(l.onclick=ci)}l=u,n.updateQueue=l,l!==null&&(n.flags|=4)}else{y=u.nodeType===9?u:u.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=Su(a)),e==="http://www.w3.org/1999/xhtml"?a==="script"?(e=y.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof l.is=="string"?e=y.createElement(a,{is:l.is}):(e=y.createElement(a),a==="select"&&(y=e,l.multiple?y.multiple=!0:l.size&&(y.size=l.size))):e=y.createElementNS(e,a),e[$t]=n,e[or]=l,Ih(e,n,!1,!1),n.stateNode=e;e:{switch(y=Ga(a,l),a){case"dialog":Te("cancel",e),Te("close",e),u=l;break;case"iframe":case"object":case"embed":Te("load",e),u=l;break;case"video":case"audio":for(u=0;u<rr.length;u++)Te(rr[u],e);u=l;break;case"source":Te("error",e),u=l;break;case"img":case"image":case"link":Te("error",e),Te("load",e),u=l;break;case"details":Te("toggle",e),u=l;break;case"input":vu(e,l),u=Oa(e,l),Te("invalid",e);break;case"option":u=l;break;case"select":e._wrapperState={wasMultiple:!!l.multiple},u=K({},l,{value:void 0}),Te("invalid",e);break;case"textarea":bu(e,l),u=Wa(e,l),Te("invalid",e);break;default:u=l}Ha(a,u),b=u;for(m in b)if(b.hasOwnProperty(m)){var C=b[m];m==="style"?Tu(e,C):m==="dangerouslySetInnerHTML"?(C=C?C.__html:void 0,C!=null&&Nu(e,C)):m==="children"?typeof C=="string"?(a!=="textarea"||C!=="")&&Bs(e,C):typeof C=="number"&&Bs(e,""+C):m!=="suppressContentEditableWarning"&&m!=="suppressHydrationWarning"&&m!=="autoFocus"&&(c.hasOwnProperty(m)?C!=null&&m==="onScroll"&&Te("scroll",e):C!=null&&L(e,m,C,y))}switch(a){case"input":Br(e),wu(e,l,!1);break;case"textarea":Br(e),ju(e);break;case"option":l.value!=null&&e.setAttribute("value",""+we(l.value));break;case"select":e.multiple=!!l.multiple,m=l.value,m!=null?ss(e,!!l.multiple,m,!1):l.defaultValue!=null&&ss(e,!!l.multiple,l.defaultValue,!0);break;default:typeof u.onClick=="function"&&(e.onclick=ci)}switch(a){case"button":case"input":case"select":case"textarea":l=!!l.autoFocus;break e;case"img":l=!0;break e;default:l=!1}}l&&(n.flags|=4)}n.ref!==null&&(n.flags|=512,n.flags|=2097152)}return st(n),null;case 6:if(e&&n.stateNode!=null)Fh(e,n,e.memoizedProps,l);else{if(typeof l!="string"&&n.stateNode===null)throw Error(i(166));if(a=Bn(hr.current),Bn(Ht.current),gi(n)){if(l=n.stateNode,a=n.memoizedProps,l[$t]=n,(m=l.nodeValue!==a)&&(e=xt,e!==null))switch(e.tag){case 3:li(l.nodeValue,a,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&li(l.nodeValue,a,(e.mode&1)!==0)}m&&(n.flags|=4)}else l=(a.nodeType===9?a:a.ownerDocument).createTextNode(l),l[$t]=n,n.stateNode=l}return st(n),null;case 13:if(Pe(Ae),l=n.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(Me&&wt!==null&&(n.mode&1)!==0&&(n.flags&128)===0)zd(),vs(),n.flags|=98560,m=!1;else if(m=gi(n),l!==null&&l.dehydrated!==null){if(e===null){if(!m)throw Error(i(318));if(m=n.memoizedState,m=m!==null?m.dehydrated:null,!m)throw Error(i(317));m[$t]=n}else vs(),(n.flags&128)===0&&(n.memoizedState=null),n.flags|=4;st(n),m=!1}else Dt!==null&&(jl(Dt),Dt=null),m=!0;if(!m)return n.flags&65536?n:null}return(n.flags&128)!==0?(n.lanes=a,n):(l=l!==null,l!==(e!==null&&e.memoizedState!==null)&&l&&(n.child.flags|=8192,(n.mode&1)!==0&&(e===null||(Ae.current&1)!==0?Ue===0&&(Ue=3):Cl())),n.updateQueue!==null&&(n.flags|=4),st(n),null);case 4:return ks(),hl(e,n),e===null&&ir(n.stateNode.containerInfo),st(n),null;case 10:return Oo(n.type._context),st(n),null;case 17:return dt(n.type)&&di(),st(n),null;case 19:if(Pe(Ae),m=n.memoizedState,m===null)return st(n),null;if(l=(n.flags&128)!==0,y=m.rendering,y===null)if(l)yr(m,!1);else{if(Ue!==0||e!==null&&(e.flags&128)!==0)for(e=n.child;e!==null;){if(y=ki(e),y!==null){for(n.flags|=128,yr(m,!1),l=y.updateQueue,l!==null&&(n.updateQueue=l,n.flags|=4),n.subtreeFlags=0,l=a,a=n.child;a!==null;)m=a,e=l,m.flags&=14680066,y=m.alternate,y===null?(m.childLanes=0,m.lanes=e,m.child=null,m.subtreeFlags=0,m.memoizedProps=null,m.memoizedState=null,m.updateQueue=null,m.dependencies=null,m.stateNode=null):(m.childLanes=y.childLanes,m.lanes=y.lanes,m.child=y.child,m.subtreeFlags=0,m.deletions=null,m.memoizedProps=y.memoizedProps,m.memoizedState=y.memoizedState,m.updateQueue=y.updateQueue,m.type=y.type,e=y.dependencies,m.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),a=a.sibling;return Ce(Ae,Ae.current&1|2),n.child}e=e.sibling}m.tail!==null&&Ve()>Cs&&(n.flags|=128,l=!0,yr(m,!1),n.lanes=4194304)}else{if(!l)if(e=ki(y),e!==null){if(n.flags|=128,l=!0,a=e.updateQueue,a!==null&&(n.updateQueue=a,n.flags|=4),yr(m,!0),m.tail===null&&m.tailMode==="hidden"&&!y.alternate&&!Me)return st(n),null}else 2*Ve()-m.renderingStartTime>Cs&&a!==1073741824&&(n.flags|=128,l=!0,yr(m,!1),n.lanes=4194304);m.isBackwards?(y.sibling=n.child,n.child=y):(a=m.last,a!==null?a.sibling=y:n.child=y,m.last=y)}return m.tail!==null?(n=m.tail,m.rendering=n,m.tail=n.sibling,m.renderingStartTime=Ve(),n.sibling=null,a=Ae.current,Ce(Ae,l?a&1|2:a&1),n):(st(n),null);case 22:case 23:return Nl(),l=n.memoizedState!==null,e!==null&&e.memoizedState!==null!==l&&(n.flags|=8192),l&&(n.mode&1)!==0?(bt&1073741824)!==0&&(st(n),n.subtreeFlags&6&&(n.flags|=8192)):st(n),null;case 24:return null;case 25:return null}throw Error(i(156,n.tag))}function Ev(e,n){switch(Ro(n),n.tag){case 1:return dt(n.type)&&di(),e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 3:return ks(),Pe(ut),Pe(tt),Ko(),e=n.flags,(e&65536)!==0&&(e&128)===0?(n.flags=e&-65537|128,n):null;case 5:return Ho(n),null;case 13:if(Pe(Ae),e=n.memoizedState,e!==null&&e.dehydrated!==null){if(n.alternate===null)throw Error(i(340));vs()}return e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 19:return Pe(Ae),null;case 4:return ks(),null;case 10:return Oo(n.type._context),null;case 22:case 23:return Nl(),null;case 24:return null;default:return null}}var Ai=!1,rt=!1,Mv=typeof WeakSet=="function"?WeakSet:Set,Y=null;function Ss(e,n){var a=e.ref;if(a!==null)if(typeof a=="function")try{a(null)}catch(l){De(e,n,l)}else a.current=null}function ml(e,n,a){try{a()}catch(l){De(e,n,l)}}var Bh=!1;function Av(e,n){if(No=Qr,e=yd(),yo(e)){if("selectionStart"in e)var a={start:e.selectionStart,end:e.selectionEnd};else e:{a=(a=e.ownerDocument)&&a.defaultView||window;var l=a.getSelection&&a.getSelection();if(l&&l.rangeCount!==0){a=l.anchorNode;var u=l.anchorOffset,m=l.focusNode;l=l.focusOffset;try{a.nodeType,m.nodeType}catch{a=null;break e}var y=0,b=-1,C=-1,R=0,W=0,$=e,U=null;t:for(;;){for(var X;$!==a||u!==0&&$.nodeType!==3||(b=y+u),$!==m||l!==0&&$.nodeType!==3||(C=y+l),$.nodeType===3&&(y+=$.nodeValue.length),(X=$.firstChild)!==null;)U=$,$=X;for(;;){if($===e)break t;if(U===a&&++R===u&&(b=y),U===m&&++W===l&&(C=y),(X=$.nextSibling)!==null)break;$=U,U=$.parentNode}$=X}a=b===-1||C===-1?null:{start:b,end:C}}else a=null}a=a||{start:0,end:0}}else a=null;for(Co={focusedElem:e,selectionRange:a},Qr=!1,Y=n;Y!==null;)if(n=Y,e=n.child,(n.subtreeFlags&1028)!==0&&e!==null)e.return=n,Y=e;else for(;Y!==null;){n=Y;try{var q=n.alternate;if((n.flags&1024)!==0)switch(n.tag){case 0:case 11:case 15:break;case 1:if(q!==null){var Z=q.memoizedProps,Fe=q.memoizedState,A=n.stateNode,T=A.getSnapshotBeforeUpdate(n.elementType===n.type?Z:Rt(n.type,Z),Fe);A.__reactInternalSnapshotBeforeUpdate=T}break;case 3:var _=n.stateNode.containerInfo;_.nodeType===1?_.textContent="":_.nodeType===9&&_.documentElement&&_.removeChild(_.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(i(163))}}catch(G){De(n,n.return,G)}if(e=n.sibling,e!==null){e.return=n.return,Y=e;break}Y=n.return}return q=Bh,Bh=!1,q}function vr(e,n,a){var l=n.updateQueue;if(l=l!==null?l.lastEffect:null,l!==null){var u=l=l.next;do{if((u.tag&e)===e){var m=u.destroy;u.destroy=void 0,m!==void 0&&ml(n,a,m)}u=u.next}while(u!==l)}}function _i(e,n){if(n=n.updateQueue,n=n!==null?n.lastEffect:null,n!==null){var a=n=n.next;do{if((a.tag&e)===e){var l=a.create;a.destroy=l()}a=a.next}while(a!==n)}}function fl(e){var n=e.ref;if(n!==null){var a=e.stateNode;switch(e.tag){case 5:e=a;break;default:e=a}typeof n=="function"?n(e):n.current=e}}function Oh(e){var n=e.alternate;n!==null&&(e.alternate=null,Oh(n)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(n=e.stateNode,n!==null&&(delete n[$t],delete n[or],delete n[Mo],delete n[mv],delete n[fv])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function zh(e){return e.tag===5||e.tag===3||e.tag===4}function Uh(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||zh(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function pl(e,n,a){var l=e.tag;if(l===5||l===6)e=e.stateNode,n?a.nodeType===8?a.parentNode.insertBefore(e,n):a.insertBefore(e,n):(a.nodeType===8?(n=a.parentNode,n.insertBefore(e,a)):(n=a,n.appendChild(e)),a=a._reactRootContainer,a!=null||n.onclick!==null||(n.onclick=ci));else if(l!==4&&(e=e.child,e!==null))for(pl(e,n,a),e=e.sibling;e!==null;)pl(e,n,a),e=e.sibling}function gl(e,n,a){var l=e.tag;if(l===5||l===6)e=e.stateNode,n?a.insertBefore(e,n):a.appendChild(e);else if(l!==4&&(e=e.child,e!==null))for(gl(e,n,a),e=e.sibling;e!==null;)gl(e,n,a),e=e.sibling}var Qe=null,Lt=!1;function bn(e,n,a){for(a=a.child;a!==null;)Wh(e,n,a),a=a.sibling}function Wh(e,n,a){if(Wt&&typeof Wt.onCommitFiberUnmount=="function")try{Wt.onCommitFiberUnmount(Hr,a)}catch{}switch(a.tag){case 5:rt||Ss(a,n);case 6:var l=Qe,u=Lt;Qe=null,bn(e,n,a),Qe=l,Lt=u,Qe!==null&&(Lt?(e=Qe,a=a.stateNode,e.nodeType===8?e.parentNode.removeChild(a):e.removeChild(a)):Qe.removeChild(a.stateNode));break;case 18:Qe!==null&&(Lt?(e=Qe,a=a.stateNode,e.nodeType===8?Eo(e.parentNode,a):e.nodeType===1&&Eo(e,a),qs(e)):Eo(Qe,a.stateNode));break;case 4:l=Qe,u=Lt,Qe=a.stateNode.containerInfo,Lt=!0,bn(e,n,a),Qe=l,Lt=u;break;case 0:case 11:case 14:case 15:if(!rt&&(l=a.updateQueue,l!==null&&(l=l.lastEffect,l!==null))){u=l=l.next;do{var m=u,y=m.destroy;m=m.tag,y!==void 0&&((m&2)!==0||(m&4)!==0)&&ml(a,n,y),u=u.next}while(u!==l)}bn(e,n,a);break;case 1:if(!rt&&(Ss(a,n),l=a.stateNode,typeof l.componentWillUnmount=="function"))try{l.props=a.memoizedProps,l.state=a.memoizedState,l.componentWillUnmount()}catch(b){De(a,n,b)}bn(e,n,a);break;case 21:bn(e,n,a);break;case 22:a.mode&1?(rt=(l=rt)||a.memoizedState!==null,bn(e,n,a),rt=l):bn(e,n,a);break;default:bn(e,n,a)}}function $h(e){var n=e.updateQueue;if(n!==null){e.updateQueue=null;var a=e.stateNode;a===null&&(a=e.stateNode=new Mv),n.forEach(function(l){var u=Ov.bind(null,e,l);a.has(l)||(a.add(l),l.then(u,u))})}}function It(e,n){var a=n.deletions;if(a!==null)for(var l=0;l<a.length;l++){var u=a[l];try{var m=e,y=n,b=y;e:for(;b!==null;){switch(b.tag){case 5:Qe=b.stateNode,Lt=!1;break e;case 3:Qe=b.stateNode.containerInfo,Lt=!0;break e;case 4:Qe=b.stateNode.containerInfo,Lt=!0;break e}b=b.return}if(Qe===null)throw Error(i(160));Wh(m,y,u),Qe=null,Lt=!1;var C=u.alternate;C!==null&&(C.return=null),u.return=null}catch(R){De(u,n,R)}}if(n.subtreeFlags&12854)for(n=n.child;n!==null;)Hh(n,e),n=n.sibling}function Hh(e,n){var a=e.alternate,l=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(It(n,e),Kt(e),l&4){try{vr(3,e,e.return),_i(3,e)}catch(Z){De(e,e.return,Z)}try{vr(5,e,e.return)}catch(Z){De(e,e.return,Z)}}break;case 1:It(n,e),Kt(e),l&512&&a!==null&&Ss(a,a.return);break;case 5:if(It(n,e),Kt(e),l&512&&a!==null&&Ss(a,a.return),e.flags&32){var u=e.stateNode;try{Bs(u,"")}catch(Z){De(e,e.return,Z)}}if(l&4&&(u=e.stateNode,u!=null)){var m=e.memoizedProps,y=a!==null?a.memoizedProps:m,b=e.type,C=e.updateQueue;if(e.updateQueue=null,C!==null)try{b==="input"&&m.type==="radio"&&m.name!=null&&xu(u,m),Ga(b,y);var R=Ga(b,m);for(y=0;y<C.length;y+=2){var W=C[y],$=C[y+1];W==="style"?Tu(u,$):W==="dangerouslySetInnerHTML"?Nu(u,$):W==="children"?Bs(u,$):L(u,W,$,R)}switch(b){case"input":za(u,m);break;case"textarea":ku(u,m);break;case"select":var U=u._wrapperState.wasMultiple;u._wrapperState.wasMultiple=!!m.multiple;var X=m.value;X!=null?ss(u,!!m.multiple,X,!1):U!==!!m.multiple&&(m.defaultValue!=null?ss(u,!!m.multiple,m.defaultValue,!0):ss(u,!!m.multiple,m.multiple?[]:"",!1))}u[or]=m}catch(Z){De(e,e.return,Z)}}break;case 6:if(It(n,e),Kt(e),l&4){if(e.stateNode===null)throw Error(i(162));u=e.stateNode,m=e.memoizedProps;try{u.nodeValue=m}catch(Z){De(e,e.return,Z)}}break;case 3:if(It(n,e),Kt(e),l&4&&a!==null&&a.memoizedState.isDehydrated)try{qs(n.containerInfo)}catch(Z){De(e,e.return,Z)}break;case 4:It(n,e),Kt(e);break;case 13:It(n,e),Kt(e),u=e.child,u.flags&8192&&(m=u.memoizedState!==null,u.stateNode.isHidden=m,!m||u.alternate!==null&&u.alternate.memoizedState!==null||(xl=Ve())),l&4&&$h(e);break;case 22:if(W=a!==null&&a.memoizedState!==null,e.mode&1?(rt=(R=rt)||W,It(n,e),rt=R):It(n,e),Kt(e),l&8192){if(R=e.memoizedState!==null,(e.stateNode.isHidden=R)&&!W&&(e.mode&1)!==0)for(Y=e,W=e.child;W!==null;){for($=Y=W;Y!==null;){switch(U=Y,X=U.child,U.tag){case 0:case 11:case 14:case 15:vr(4,U,U.return);break;case 1:Ss(U,U.return);var q=U.stateNode;if(typeof q.componentWillUnmount=="function"){l=U,a=U.return;try{n=l,q.props=n.memoizedProps,q.state=n.memoizedState,q.componentWillUnmount()}catch(Z){De(l,a,Z)}}break;case 5:Ss(U,U.return);break;case 22:if(U.memoizedState!==null){Xh($);continue}}X!==null?(X.return=U,Y=X):Xh($)}W=W.sibling}e:for(W=null,$=e;;){if($.tag===5){if(W===null){W=$;try{u=$.stateNode,R?(m=u.style,typeof m.setProperty=="function"?m.setProperty("display","none","important"):m.display="none"):(b=$.stateNode,C=$.memoizedProps.style,y=C!=null&&C.hasOwnProperty("display")?C.display:null,b.style.display=Cu("display",y))}catch(Z){De(e,e.return,Z)}}}else if($.tag===6){if(W===null)try{$.stateNode.nodeValue=R?"":$.memoizedProps}catch(Z){De(e,e.return,Z)}}else if(($.tag!==22&&$.tag!==23||$.memoizedState===null||$===e)&&$.child!==null){$.child.return=$,$=$.child;continue}if($===e)break e;for(;$.sibling===null;){if($.return===null||$.return===e)break e;W===$&&(W=null),$=$.return}W===$&&(W=null),$.sibling.return=$.return,$=$.sibling}}break;case 19:It(n,e),Kt(e),l&4&&$h(e);break;case 21:break;default:It(n,e),Kt(e)}}function Kt(e){var n=e.flags;if(n&2){try{e:{for(var a=e.return;a!==null;){if(zh(a)){var l=a;break e}a=a.return}throw Error(i(160))}switch(l.tag){case 5:var u=l.stateNode;l.flags&32&&(Bs(u,""),l.flags&=-33);var m=Uh(e);gl(e,m,u);break;case 3:case 4:var y=l.stateNode.containerInfo,b=Uh(e);pl(e,b,y);break;default:throw Error(i(161))}}catch(C){De(e,e.return,C)}e.flags&=-3}n&4096&&(e.flags&=-4097)}function _v(e,n,a){Y=e,Gh(e)}function Gh(e,n,a){for(var l=(e.mode&1)!==0;Y!==null;){var u=Y,m=u.child;if(u.tag===22&&l){var y=u.memoizedState!==null||Ai;if(!y){var b=u.alternate,C=b!==null&&b.memoizedState!==null||rt;b=Ai;var R=rt;if(Ai=y,(rt=C)&&!R)for(Y=u;Y!==null;)y=Y,C=y.child,y.tag===22&&y.memoizedState!==null?Yh(u):C!==null?(C.return=y,Y=C):Yh(u);for(;m!==null;)Y=m,Gh(m),m=m.sibling;Y=u,Ai=b,rt=R}Kh(e)}else(u.subtreeFlags&8772)!==0&&m!==null?(m.return=u,Y=m):Kh(e)}}function Kh(e){for(;Y!==null;){var n=Y;if((n.flags&8772)!==0){var a=n.alternate;try{if((n.flags&8772)!==0)switch(n.tag){case 0:case 11:case 15:rt||_i(5,n);break;case 1:var l=n.stateNode;if(n.flags&4&&!rt)if(a===null)l.componentDidMount();else{var u=n.elementType===n.type?a.memoizedProps:Rt(n.type,a.memoizedProps);l.componentDidUpdate(u,a.memoizedState,l.__reactInternalSnapshotBeforeUpdate)}var m=n.updateQueue;m!==null&&Xd(n,m,l);break;case 3:var y=n.updateQueue;if(y!==null){if(a=null,n.child!==null)switch(n.child.tag){case 5:a=n.child.stateNode;break;case 1:a=n.child.stateNode}Xd(n,y,a)}break;case 5:var b=n.stateNode;if(a===null&&n.flags&4){a=b;var C=n.memoizedProps;switch(n.type){case"button":case"input":case"select":case"textarea":C.autoFocus&&a.focus();break;case"img":C.src&&(a.src=C.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(n.memoizedState===null){var R=n.alternate;if(R!==null){var W=R.memoizedState;if(W!==null){var $=W.dehydrated;$!==null&&qs($)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(i(163))}rt||n.flags&512&&fl(n)}catch(U){De(n,n.return,U)}}if(n===e){Y=null;break}if(a=n.sibling,a!==null){a.return=n.return,Y=a;break}Y=n.return}}function Xh(e){for(;Y!==null;){var n=Y;if(n===e){Y=null;break}var a=n.sibling;if(a!==null){a.return=n.return,Y=a;break}Y=n.return}}function Yh(e){for(;Y!==null;){var n=Y;try{switch(n.tag){case 0:case 11:case 15:var a=n.return;try{_i(4,n)}catch(C){De(n,a,C)}break;case 1:var l=n.stateNode;if(typeof l.componentDidMount=="function"){var u=n.return;try{l.componentDidMount()}catch(C){De(n,u,C)}}var m=n.return;try{fl(n)}catch(C){De(n,m,C)}break;case 5:var y=n.return;try{fl(n)}catch(C){De(n,y,C)}}}catch(C){De(n,n.return,C)}if(n===e){Y=null;break}var b=n.sibling;if(b!==null){b.return=n.return,Y=b;break}Y=n.return}}var Dv=Math.ceil,Di=I.ReactCurrentDispatcher,yl=I.ReactCurrentOwner,Pt=I.ReactCurrentBatchConfig,me=0,Xe=null,Be=null,Je=0,bt=0,Ns=gn(0),Ue=0,xr=null,zn=0,Ri=0,vl=0,wr=null,mt=null,xl=0,Cs=1/0,an=null,Li=!1,wl=null,kn=null,Ii=!1,jn=null,Vi=0,br=0,bl=null,Fi=-1,Bi=0;function ot(){return(me&6)!==0?Ve():Fi!==-1?Fi:Fi=Ve()}function Sn(e){return(e.mode&1)===0?1:(me&2)!==0&&Je!==0?Je&-Je:gv.transition!==null?(Bi===0&&(Bi=Uu()),Bi):(e=be,e!==0||(e=window.event,e=e===void 0?16:Qu(e.type)),e)}function Vt(e,n,a,l){if(50<br)throw br=0,bl=null,Error(i(185));Hs(e,a,l),((me&2)===0||e!==Xe)&&(e===Xe&&((me&2)===0&&(Ri|=a),Ue===4&&Nn(e,Je)),ft(e,l),a===1&&me===0&&(n.mode&1)===0&&(Cs=Ve()+500,mi&&vn()))}function ft(e,n){var a=e.callbackNode;gy(e,n);var l=Xr(e,e===Xe?Je:0);if(l===0)a!==null&&Bu(a),e.callbackNode=null,e.callbackPriority=0;else if(n=l&-l,e.callbackPriority!==n){if(a!=null&&Bu(a),n===1)e.tag===0?pv(Qh.bind(null,e)):Id(Qh.bind(null,e)),dv(function(){(me&6)===0&&vn()}),a=null;else{switch(Wu(l)){case 1:a=Za;break;case 4:a=Ou;break;case 16:a=$r;break;case 536870912:a=zu;break;default:a=$r}a=im(a,qh.bind(null,e))}e.callbackPriority=n,e.callbackNode=a}}function qh(e,n){if(Fi=-1,Bi=0,(me&6)!==0)throw Error(i(327));var a=e.callbackNode;if(Ts()&&e.callbackNode!==a)return null;var l=Xr(e,e===Xe?Je:0);if(l===0)return null;if((l&30)!==0||(l&e.expiredLanes)!==0||n)n=Oi(e,l);else{n=l;var u=me;me|=2;var m=Zh();(Xe!==e||Je!==n)&&(an=null,Cs=Ve()+500,Wn(e,n));do try{Iv();break}catch(b){Jh(e,b)}while(!0);Bo(),Di.current=m,me=u,Be!==null?n=0:(Xe=null,Je=0,n=Ue)}if(n!==0){if(n===2&&(u=eo(e),u!==0&&(l=u,n=kl(e,u))),n===1)throw a=xr,Wn(e,0),Nn(e,l),ft(e,Ve()),a;if(n===6)Nn(e,l);else{if(u=e.current.alternate,(l&30)===0&&!Rv(u)&&(n=Oi(e,l),n===2&&(m=eo(e),m!==0&&(l=m,n=kl(e,m))),n===1))throw a=xr,Wn(e,0),Nn(e,l),ft(e,Ve()),a;switch(e.finishedWork=u,e.finishedLanes=l,n){case 0:case 1:throw Error(i(345));case 2:$n(e,mt,an);break;case 3:if(Nn(e,l),(l&130023424)===l&&(n=xl+500-Ve(),10<n)){if(Xr(e,0)!==0)break;if(u=e.suspendedLanes,(u&l)!==l){ot(),e.pingedLanes|=e.suspendedLanes&u;break}e.timeoutHandle=Po($n.bind(null,e,mt,an),n);break}$n(e,mt,an);break;case 4:if(Nn(e,l),(l&4194240)===l)break;for(n=e.eventTimes,u=-1;0<l;){var y=31-At(l);m=1<<y,y=n[y],y>u&&(u=y),l&=~m}if(l=u,l=Ve()-l,l=(120>l?120:480>l?480:1080>l?1080:1920>l?1920:3e3>l?3e3:4320>l?4320:1960*Dv(l/1960))-l,10<l){e.timeoutHandle=Po($n.bind(null,e,mt,an),l);break}$n(e,mt,an);break;case 5:$n(e,mt,an);break;default:throw Error(i(329))}}}return ft(e,Ve()),e.callbackNode===a?qh.bind(null,e):null}function kl(e,n){var a=wr;return e.current.memoizedState.isDehydrated&&(Wn(e,n).flags|=256),e=Oi(e,n),e!==2&&(n=mt,mt=a,n!==null&&jl(n)),e}function jl(e){mt===null?mt=e:mt.push.apply(mt,e)}function Rv(e){for(var n=e;;){if(n.flags&16384){var a=n.updateQueue;if(a!==null&&(a=a.stores,a!==null))for(var l=0;l<a.length;l++){var u=a[l],m=u.getSnapshot;u=u.value;try{if(!_t(m(),u))return!1}catch{return!1}}}if(a=n.child,n.subtreeFlags&16384&&a!==null)a.return=n,n=a;else{if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return!0;n=n.return}n.sibling.return=n.return,n=n.sibling}}return!0}function Nn(e,n){for(n&=~vl,n&=~Ri,e.suspendedLanes|=n,e.pingedLanes&=~n,e=e.expirationTimes;0<n;){var a=31-At(n),l=1<<a;e[a]=-1,n&=~l}}function Qh(e){if((me&6)!==0)throw Error(i(327));Ts();var n=Xr(e,0);if((n&1)===0)return ft(e,Ve()),null;var a=Oi(e,n);if(e.tag!==0&&a===2){var l=eo(e);l!==0&&(n=l,a=kl(e,l))}if(a===1)throw a=xr,Wn(e,0),Nn(e,n),ft(e,Ve()),a;if(a===6)throw Error(i(345));return e.finishedWork=e.current.alternate,e.finishedLanes=n,$n(e,mt,an),ft(e,Ve()),null}function Sl(e,n){var a=me;me|=1;try{return e(n)}finally{me=a,me===0&&(Cs=Ve()+500,mi&&vn())}}function Un(e){jn!==null&&jn.tag===0&&(me&6)===0&&Ts();var n=me;me|=1;var a=Pt.transition,l=be;try{if(Pt.transition=null,be=1,e)return e()}finally{be=l,Pt.transition=a,me=n,(me&6)===0&&vn()}}function Nl(){bt=Ns.current,Pe(Ns)}function Wn(e,n){e.finishedWork=null,e.finishedLanes=0;var a=e.timeoutHandle;if(a!==-1&&(e.timeoutHandle=-1,uv(a)),Be!==null)for(a=Be.return;a!==null;){var l=a;switch(Ro(l),l.tag){case 1:l=l.type.childContextTypes,l!=null&&di();break;case 3:ks(),Pe(ut),Pe(tt),Ko();break;case 5:Ho(l);break;case 4:ks();break;case 13:Pe(Ae);break;case 19:Pe(Ae);break;case 10:Oo(l.type._context);break;case 22:case 23:Nl()}a=a.return}if(Xe=e,Be=e=Cn(e.current,null),Je=bt=n,Ue=0,xr=null,vl=Ri=zn=0,mt=wr=null,Fn!==null){for(n=0;n<Fn.length;n++)if(a=Fn[n],l=a.interleaved,l!==null){a.interleaved=null;var u=l.next,m=a.pending;if(m!==null){var y=m.next;m.next=u,l.next=y}a.pending=l}Fn=null}return e}function Jh(e,n){do{var a=Be;try{if(Bo(),ji.current=Ti,Si){for(var l=_e.memoizedState;l!==null;){var u=l.queue;u!==null&&(u.pending=null),l=l.next}Si=!1}if(On=0,Ke=ze=_e=null,mr=!1,fr=0,yl.current=null,a===null||a.return===null){Ue=1,xr=n,Be=null;break}e:{var m=e,y=a.return,b=a,C=n;if(n=Je,b.flags|=32768,C!==null&&typeof C=="object"&&typeof C.then=="function"){var R=C,W=b,$=W.tag;if((W.mode&1)===0&&($===0||$===11||$===15)){var U=W.alternate;U?(W.updateQueue=U.updateQueue,W.memoizedState=U.memoizedState,W.lanes=U.lanes):(W.updateQueue=null,W.memoizedState=null)}var X=jh(y);if(X!==null){X.flags&=-257,Sh(X,y,b,m,n),X.mode&1&&kh(m,R,n),n=X,C=R;var q=n.updateQueue;if(q===null){var Z=new Set;Z.add(C),n.updateQueue=Z}else q.add(C);break e}else{if((n&1)===0){kh(m,R,n),Cl();break e}C=Error(i(426))}}else if(Me&&b.mode&1){var Fe=jh(y);if(Fe!==null){(Fe.flags&65536)===0&&(Fe.flags|=256),Sh(Fe,y,b,m,n),Vo(js(C,b));break e}}m=C=js(C,b),Ue!==4&&(Ue=2),wr===null?wr=[m]:wr.push(m),m=y;do{switch(m.tag){case 3:m.flags|=65536,n&=-n,m.lanes|=n;var A=wh(m,C,n);Kd(m,A);break e;case 1:b=C;var T=m.type,_=m.stateNode;if((m.flags&128)===0&&(typeof T.getDerivedStateFromError=="function"||_!==null&&typeof _.componentDidCatch=="function"&&(kn===null||!kn.has(_)))){m.flags|=65536,n&=-n,m.lanes|=n;var G=bh(m,b,n);Kd(m,G);break e}}m=m.return}while(m!==null)}tm(a)}catch(te){n=te,Be===a&&a!==null&&(Be=a=a.return);continue}break}while(!0)}function Zh(){var e=Di.current;return Di.current=Ti,e===null?Ti:e}function Cl(){(Ue===0||Ue===3||Ue===2)&&(Ue=4),Xe===null||(zn&268435455)===0&&(Ri&268435455)===0||Nn(Xe,Je)}function Oi(e,n){var a=me;me|=2;var l=Zh();(Xe!==e||Je!==n)&&(an=null,Wn(e,n));do try{Lv();break}catch(u){Jh(e,u)}while(!0);if(Bo(),me=a,Di.current=l,Be!==null)throw Error(i(261));return Xe=null,Je=0,Ue}function Lv(){for(;Be!==null;)em(Be)}function Iv(){for(;Be!==null&&!oy();)em(Be)}function em(e){var n=rm(e.alternate,e,bt);e.memoizedProps=e.pendingProps,n===null?tm(e):Be=n,yl.current=null}function tm(e){var n=e;do{var a=n.alternate;if(e=n.return,(n.flags&32768)===0){if(a=Pv(a,n,bt),a!==null){Be=a;return}}else{if(a=Ev(a,n),a!==null){a.flags&=32767,Be=a;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{Ue=6,Be=null;return}}if(n=n.sibling,n!==null){Be=n;return}Be=n=e}while(n!==null);Ue===0&&(Ue=5)}function $n(e,n,a){var l=be,u=Pt.transition;try{Pt.transition=null,be=1,Vv(e,n,a,l)}finally{Pt.transition=u,be=l}return null}function Vv(e,n,a,l){do Ts();while(jn!==null);if((me&6)!==0)throw Error(i(327));a=e.finishedWork;var u=e.finishedLanes;if(a===null)return null;if(e.finishedWork=null,e.finishedLanes=0,a===e.current)throw Error(i(177));e.callbackNode=null,e.callbackPriority=0;var m=a.lanes|a.childLanes;if(yy(e,m),e===Xe&&(Be=Xe=null,Je=0),(a.subtreeFlags&2064)===0&&(a.flags&2064)===0||Ii||(Ii=!0,im($r,function(){return Ts(),null})),m=(a.flags&15990)!==0,(a.subtreeFlags&15990)!==0||m){m=Pt.transition,Pt.transition=null;var y=be;be=1;var b=me;me|=4,yl.current=null,Av(e,a),Hh(a,e),sv(Co),Qr=!!No,Co=No=null,e.current=a,_v(a),ly(),me=b,be=y,Pt.transition=m}else e.current=a;if(Ii&&(Ii=!1,jn=e,Vi=u),m=e.pendingLanes,m===0&&(kn=null),dy(a.stateNode),ft(e,Ve()),n!==null)for(l=e.onRecoverableError,a=0;a<n.length;a++)u=n[a],l(u.value,{componentStack:u.stack,digest:u.digest});if(Li)throw Li=!1,e=wl,wl=null,e;return(Vi&1)!==0&&e.tag!==0&&Ts(),m=e.pendingLanes,(m&1)!==0?e===bl?br++:(br=0,bl=e):br=0,vn(),null}function Ts(){if(jn!==null){var e=Wu(Vi),n=Pt.transition,a=be;try{if(Pt.transition=null,be=16>e?16:e,jn===null)var l=!1;else{if(e=jn,jn=null,Vi=0,(me&6)!==0)throw Error(i(331));var u=me;for(me|=4,Y=e.current;Y!==null;){var m=Y,y=m.child;if((Y.flags&16)!==0){var b=m.deletions;if(b!==null){for(var C=0;C<b.length;C++){var R=b[C];for(Y=R;Y!==null;){var W=Y;switch(W.tag){case 0:case 11:case 15:vr(8,W,m)}var $=W.child;if($!==null)$.return=W,Y=$;else for(;Y!==null;){W=Y;var U=W.sibling,X=W.return;if(Oh(W),W===R){Y=null;break}if(U!==null){U.return=X,Y=U;break}Y=X}}}var q=m.alternate;if(q!==null){var Z=q.child;if(Z!==null){q.child=null;do{var Fe=Z.sibling;Z.sibling=null,Z=Fe}while(Z!==null)}}Y=m}}if((m.subtreeFlags&2064)!==0&&y!==null)y.return=m,Y=y;else e:for(;Y!==null;){if(m=Y,(m.flags&2048)!==0)switch(m.tag){case 0:case 11:case 15:vr(9,m,m.return)}var A=m.sibling;if(A!==null){A.return=m.return,Y=A;break e}Y=m.return}}var T=e.current;for(Y=T;Y!==null;){y=Y;var _=y.child;if((y.subtreeFlags&2064)!==0&&_!==null)_.return=y,Y=_;else e:for(y=T;Y!==null;){if(b=Y,(b.flags&2048)!==0)try{switch(b.tag){case 0:case 11:case 15:_i(9,b)}}catch(te){De(b,b.return,te)}if(b===y){Y=null;break e}var G=b.sibling;if(G!==null){G.return=b.return,Y=G;break e}Y=b.return}}if(me=u,vn(),Wt&&typeof Wt.onPostCommitFiberRoot=="function")try{Wt.onPostCommitFiberRoot(Hr,e)}catch{}l=!0}return l}finally{be=a,Pt.transition=n}}return!1}function nm(e,n,a){n=js(a,n),n=wh(e,n,1),e=wn(e,n,1),n=ot(),e!==null&&(Hs(e,1,n),ft(e,n))}function De(e,n,a){if(e.tag===3)nm(e,e,a);else for(;n!==null;){if(n.tag===3){nm(n,e,a);break}else if(n.tag===1){var l=n.stateNode;if(typeof n.type.getDerivedStateFromError=="function"||typeof l.componentDidCatch=="function"&&(kn===null||!kn.has(l))){e=js(a,e),e=bh(n,e,1),n=wn(n,e,1),e=ot(),n!==null&&(Hs(n,1,e),ft(n,e));break}}n=n.return}}function Fv(e,n,a){var l=e.pingCache;l!==null&&l.delete(n),n=ot(),e.pingedLanes|=e.suspendedLanes&a,Xe===e&&(Je&a)===a&&(Ue===4||Ue===3&&(Je&130023424)===Je&&500>Ve()-xl?Wn(e,0):vl|=a),ft(e,n)}function sm(e,n){n===0&&((e.mode&1)===0?n=1:(n=Kr,Kr<<=1,(Kr&130023424)===0&&(Kr=4194304)));var a=ot();e=nn(e,n),e!==null&&(Hs(e,n,a),ft(e,a))}function Bv(e){var n=e.memoizedState,a=0;n!==null&&(a=n.retryLane),sm(e,a)}function Ov(e,n){var a=0;switch(e.tag){case 13:var l=e.stateNode,u=e.memoizedState;u!==null&&(a=u.retryLane);break;case 19:l=e.stateNode;break;default:throw Error(i(314))}l!==null&&l.delete(n),sm(e,a)}var rm;rm=function(e,n,a){if(e!==null)if(e.memoizedProps!==n.pendingProps||ut.current)ht=!0;else{if((e.lanes&a)===0&&(n.flags&128)===0)return ht=!1,Tv(e,n,a);ht=(e.flags&131072)!==0}else ht=!1,Me&&(n.flags&1048576)!==0&&Vd(n,pi,n.index);switch(n.lanes=0,n.tag){case 2:var l=n.type;Mi(e,n),e=n.pendingProps;var u=ps(n,tt.current);bs(n,a),u=qo(null,n,l,e,u,a);var m=Qo();return n.flags|=1,typeof u=="object"&&u!==null&&typeof u.render=="function"&&u.$$typeof===void 0?(n.tag=1,n.memoizedState=null,n.updateQueue=null,dt(l)?(m=!0,hi(n)):m=!1,n.memoizedState=u.state!==null&&u.state!==void 0?u.state:null,Wo(n),u.updater=Pi,n.stateNode=u,u._reactInternals=n,sl(n,l,e,a),n=ol(null,n,l,!0,m,a)):(n.tag=0,Me&&m&&Do(n),at(null,n,u,a),n=n.child),n;case 16:l=n.elementType;e:{switch(Mi(e,n),e=n.pendingProps,u=l._init,l=u(l._payload),n.type=l,u=n.tag=Uv(l),e=Rt(l,e),u){case 0:n=al(null,n,l,e,a);break e;case 1:n=Mh(null,n,l,e,a);break e;case 11:n=Nh(null,n,l,e,a);break e;case 14:n=Ch(null,n,l,Rt(l.type,e),a);break e}throw Error(i(306,l,""))}return n;case 0:return l=n.type,u=n.pendingProps,u=n.elementType===l?u:Rt(l,u),al(e,n,l,u,a);case 1:return l=n.type,u=n.pendingProps,u=n.elementType===l?u:Rt(l,u),Mh(e,n,l,u,a);case 3:e:{if(Ah(n),e===null)throw Error(i(387));l=n.pendingProps,m=n.memoizedState,u=m.element,Gd(e,n),bi(n,l,null,a);var y=n.memoizedState;if(l=y.element,m.isDehydrated)if(m={element:l,isDehydrated:!1,cache:y.cache,pendingSuspenseBoundaries:y.pendingSuspenseBoundaries,transitions:y.transitions},n.updateQueue.baseState=m,n.memoizedState=m,n.flags&256){u=js(Error(i(423)),n),n=_h(e,n,l,a,u);break e}else if(l!==u){u=js(Error(i(424)),n),n=_h(e,n,l,a,u);break e}else for(wt=pn(n.stateNode.containerInfo.firstChild),xt=n,Me=!0,Dt=null,a=$d(n,null,l,a),n.child=a;a;)a.flags=a.flags&-3|4096,a=a.sibling;else{if(vs(),l===u){n=rn(e,n,a);break e}at(e,n,l,a)}n=n.child}return n;case 5:return Yd(n),e===null&&Io(n),l=n.type,u=n.pendingProps,m=e!==null?e.memoizedProps:null,y=u.children,To(l,u)?y=null:m!==null&&To(l,m)&&(n.flags|=32),Eh(e,n),at(e,n,y,a),n.child;case 6:return e===null&&Io(n),null;case 13:return Dh(e,n,a);case 4:return $o(n,n.stateNode.containerInfo),l=n.pendingProps,e===null?n.child=xs(n,null,l,a):at(e,n,l,a),n.child;case 11:return l=n.type,u=n.pendingProps,u=n.elementType===l?u:Rt(l,u),Nh(e,n,l,u,a);case 7:return at(e,n,n.pendingProps,a),n.child;case 8:return at(e,n,n.pendingProps.children,a),n.child;case 12:return at(e,n,n.pendingProps.children,a),n.child;case 10:e:{if(l=n.type._context,u=n.pendingProps,m=n.memoizedProps,y=u.value,Ce(vi,l._currentValue),l._currentValue=y,m!==null)if(_t(m.value,y)){if(m.children===u.children&&!ut.current){n=rn(e,n,a);break e}}else for(m=n.child,m!==null&&(m.return=n);m!==null;){var b=m.dependencies;if(b!==null){y=m.child;for(var C=b.firstContext;C!==null;){if(C.context===l){if(m.tag===1){C=sn(-1,a&-a),C.tag=2;var R=m.updateQueue;if(R!==null){R=R.shared;var W=R.pending;W===null?C.next=C:(C.next=W.next,W.next=C),R.pending=C}}m.lanes|=a,C=m.alternate,C!==null&&(C.lanes|=a),zo(m.return,a,n),b.lanes|=a;break}C=C.next}}else if(m.tag===10)y=m.type===n.type?null:m.child;else if(m.tag===18){if(y=m.return,y===null)throw Error(i(341));y.lanes|=a,b=y.alternate,b!==null&&(b.lanes|=a),zo(y,a,n),y=m.sibling}else y=m.child;if(y!==null)y.return=m;else for(y=m;y!==null;){if(y===n){y=null;break}if(m=y.sibling,m!==null){m.return=y.return,y=m;break}y=y.return}m=y}at(e,n,u.children,a),n=n.child}return n;case 9:return u=n.type,l=n.pendingProps.children,bs(n,a),u=Ct(u),l=l(u),n.flags|=1,at(e,n,l,a),n.child;case 14:return l=n.type,u=Rt(l,n.pendingProps),u=Rt(l.type,u),Ch(e,n,l,u,a);case 15:return Th(e,n,n.type,n.pendingProps,a);case 17:return l=n.type,u=n.pendingProps,u=n.elementType===l?u:Rt(l,u),Mi(e,n),n.tag=1,dt(l)?(e=!0,hi(n)):e=!1,bs(n,a),vh(n,l,u),sl(n,l,u,a),ol(null,n,l,!0,e,a);case 19:return Lh(e,n,a);case 22:return Ph(e,n,a)}throw Error(i(156,n.tag))};function im(e,n){return Fu(e,n)}function zv(e,n,a,l){this.tag=e,this.key=a,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=n,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=l,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function Et(e,n,a,l){return new zv(e,n,a,l)}function Tl(e){return e=e.prototype,!(!e||!e.isReactComponent)}function Uv(e){if(typeof e=="function")return Tl(e)?1:0;if(e!=null){if(e=e.$$typeof,e===se)return 11;if(e===Le)return 14}return 2}function Cn(e,n){var a=e.alternate;return a===null?(a=Et(e.tag,n,e.key,e.mode),a.elementType=e.elementType,a.type=e.type,a.stateNode=e.stateNode,a.alternate=e,e.alternate=a):(a.pendingProps=n,a.type=e.type,a.flags=0,a.subtreeFlags=0,a.deletions=null),a.flags=e.flags&14680064,a.childLanes=e.childLanes,a.lanes=e.lanes,a.child=e.child,a.memoizedProps=e.memoizedProps,a.memoizedState=e.memoizedState,a.updateQueue=e.updateQueue,n=e.dependencies,a.dependencies=n===null?null:{lanes:n.lanes,firstContext:n.firstContext},a.sibling=e.sibling,a.index=e.index,a.ref=e.ref,a}function zi(e,n,a,l,u,m){var y=2;if(l=e,typeof e=="function")Tl(e)&&(y=1);else if(typeof e=="string")y=5;else e:switch(e){case V:return Hn(a.children,u,m,n);case O:y=8,u|=8;break;case oe:return e=Et(12,a,n,u|2),e.elementType=oe,e.lanes=m,e;case ne:return e=Et(13,a,n,u),e.elementType=ne,e.lanes=m,e;case Se:return e=Et(19,a,n,u),e.elementType=Se,e.lanes=m,e;case ye:return Ui(a,u,m,n);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case le:y=10;break e;case xe:y=9;break e;case se:y=11;break e;case Le:y=14;break e;case Ie:y=16,l=null;break e}throw Error(i(130,e==null?e:typeof e,""))}return n=Et(y,a,n,u),n.elementType=e,n.type=l,n.lanes=m,n}function Hn(e,n,a,l){return e=Et(7,e,l,n),e.lanes=a,e}function Ui(e,n,a,l){return e=Et(22,e,l,n),e.elementType=ye,e.lanes=a,e.stateNode={isHidden:!1},e}function Pl(e,n,a){return e=Et(6,e,null,n),e.lanes=a,e}function El(e,n,a){return n=Et(4,e.children!==null?e.children:[],e.key,n),n.lanes=a,n.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},n}function Wv(e,n,a,l,u){this.tag=n,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=to(0),this.expirationTimes=to(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=to(0),this.identifierPrefix=l,this.onRecoverableError=u,this.mutableSourceEagerHydrationData=null}function Ml(e,n,a,l,u,m,y,b,C){return e=new Wv(e,n,a,b,C),n===1?(n=1,m===!0&&(n|=8)):n=0,m=Et(3,null,null,n),e.current=m,m.stateNode=e,m.memoizedState={element:l,isDehydrated:a,cache:null,transitions:null,pendingSuspenseBoundaries:null},Wo(m),e}function $v(e,n,a){var l=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:F,key:l==null?null:""+l,children:e,containerInfo:n,implementation:a}}function am(e){if(!e)return yn;e=e._reactInternals;e:{if(Dn(e)!==e||e.tag!==1)throw Error(i(170));var n=e;do{switch(n.tag){case 3:n=n.stateNode.context;break e;case 1:if(dt(n.type)){n=n.stateNode.__reactInternalMemoizedMergedChildContext;break e}}n=n.return}while(n!==null);throw Error(i(171))}if(e.tag===1){var a=e.type;if(dt(a))return Rd(e,a,n)}return n}function om(e,n,a,l,u,m,y,b,C){return e=Ml(a,l,!0,e,u,m,y,b,C),e.context=am(null),a=e.current,l=ot(),u=Sn(a),m=sn(l,u),m.callback=n??null,wn(a,m,u),e.current.lanes=u,Hs(e,u,l),ft(e,l),e}function Wi(e,n,a,l){var u=n.current,m=ot(),y=Sn(u);return a=am(a),n.context===null?n.context=a:n.pendingContext=a,n=sn(m,y),n.payload={element:e},l=l===void 0?null:l,l!==null&&(n.callback=l),e=wn(u,n,y),e!==null&&(Vt(e,u,y,m),wi(e,u,y)),y}function $i(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function lm(e,n){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var a=e.retryLane;e.retryLane=a!==0&&a<n?a:n}}function Al(e,n){lm(e,n),(e=e.alternate)&&lm(e,n)}function Hv(){return null}var cm=typeof reportError=="function"?reportError:function(e){console.error(e)};function _l(e){this._internalRoot=e}Hi.prototype.render=_l.prototype.render=function(e){var n=this._internalRoot;if(n===null)throw Error(i(409));Wi(e,n,null,null)},Hi.prototype.unmount=_l.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var n=e.containerInfo;Un(function(){Wi(null,e,null,null)}),n[Jt]=null}};function Hi(e){this._internalRoot=e}Hi.prototype.unstable_scheduleHydration=function(e){if(e){var n=Gu();e={blockedOn:null,target:e,priority:n};for(var a=0;a<hn.length&&n!==0&&n<hn[a].priority;a++);hn.splice(a,0,e),a===0&&Yu(e)}};function Dl(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function Gi(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function um(){}function Gv(e,n,a,l,u){if(u){if(typeof l=="function"){var m=l;l=function(){var R=$i(y);m.call(R)}}var y=om(n,l,e,0,null,!1,!1,"",um);return e._reactRootContainer=y,e[Jt]=y.current,ir(e.nodeType===8?e.parentNode:e),Un(),y}for(;u=e.lastChild;)e.removeChild(u);if(typeof l=="function"){var b=l;l=function(){var R=$i(C);b.call(R)}}var C=Ml(e,0,!1,null,null,!1,!1,"",um);return e._reactRootContainer=C,e[Jt]=C.current,ir(e.nodeType===8?e.parentNode:e),Un(function(){Wi(n,C,a,l)}),C}function Ki(e,n,a,l,u){var m=a._reactRootContainer;if(m){var y=m;if(typeof u=="function"){var b=u;u=function(){var C=$i(y);b.call(C)}}Wi(n,y,e,u)}else y=Gv(a,n,e,u,l);return $i(y)}$u=function(e){switch(e.tag){case 3:var n=e.stateNode;if(n.current.memoizedState.isDehydrated){var a=$s(n.pendingLanes);a!==0&&(no(n,a|1),ft(n,Ve()),(me&6)===0&&(Cs=Ve()+500,vn()))}break;case 13:Un(function(){var l=nn(e,1);if(l!==null){var u=ot();Vt(l,e,1,u)}}),Al(e,1)}},so=function(e){if(e.tag===13){var n=nn(e,134217728);if(n!==null){var a=ot();Vt(n,e,134217728,a)}Al(e,134217728)}},Hu=function(e){if(e.tag===13){var n=Sn(e),a=nn(e,n);if(a!==null){var l=ot();Vt(a,e,n,l)}Al(e,n)}},Gu=function(){return be},Ku=function(e,n){var a=be;try{return be=e,n()}finally{be=a}},Ya=function(e,n,a){switch(n){case"input":if(za(e,a),n=a.name,a.type==="radio"&&n!=null){for(a=e;a.parentNode;)a=a.parentNode;for(a=a.querySelectorAll("input[name="+JSON.stringify(""+n)+'][type="radio"]'),n=0;n<a.length;n++){var l=a[n];if(l!==e&&l.form===e.form){var u=ui(l);if(!u)throw Error(i(90));yu(l),za(l,u)}}}break;case"textarea":ku(e,a);break;case"select":n=a.value,n!=null&&ss(e,!!a.multiple,n,!1)}},Au=Sl,_u=Un;var Kv={usingClientEntryPoint:!1,Events:[lr,ms,ui,Eu,Mu,Sl]},kr={findFiberByHostInstance:Rn,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},Xv={bundleType:kr.bundleType,version:kr.version,rendererPackageName:kr.rendererPackageName,rendererConfig:kr.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:I.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=Iu(e),e===null?null:e.stateNode},findFiberByHostInstance:kr.findFiberByHostInstance||Hv,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Xi=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Xi.isDisabled&&Xi.supportsFiber)try{Hr=Xi.inject(Xv),Wt=Xi}catch{}}return pt.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Kv,pt.createPortal=function(e,n){var a=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!Dl(n))throw Error(i(200));return $v(e,n,null,a)},pt.createRoot=function(e,n){if(!Dl(e))throw Error(i(299));var a=!1,l="",u=cm;return n!=null&&(n.unstable_strictMode===!0&&(a=!0),n.identifierPrefix!==void 0&&(l=n.identifierPrefix),n.onRecoverableError!==void 0&&(u=n.onRecoverableError)),n=Ml(e,1,!1,null,null,a,!1,l,u),e[Jt]=n.current,ir(e.nodeType===8?e.parentNode:e),new _l(n)},pt.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var n=e._reactInternals;if(n===void 0)throw typeof e.render=="function"?Error(i(188)):(e=Object.keys(e).join(","),Error(i(268,e)));return e=Iu(n),e=e===null?null:e.stateNode,e},pt.flushSync=function(e){return Un(e)},pt.hydrate=function(e,n,a){if(!Gi(n))throw Error(i(200));return Ki(null,e,n,!0,a)},pt.hydrateRoot=function(e,n,a){if(!Dl(e))throw Error(i(405));var l=a!=null&&a.hydratedSources||null,u=!1,m="",y=cm;if(a!=null&&(a.unstable_strictMode===!0&&(u=!0),a.identifierPrefix!==void 0&&(m=a.identifierPrefix),a.onRecoverableError!==void 0&&(y=a.onRecoverableError)),n=om(n,null,e,1,a??null,u,!1,m,y),e[Jt]=n.current,ir(e),l)for(e=0;e<l.length;e++)a=l[e],u=a._getVersion,u=u(a._source),n.mutableSourceEagerHydrationData==null?n.mutableSourceEagerHydrationData=[a,u]:n.mutableSourceEagerHydrationData.push(a,u);return new Hi(n)},pt.render=function(e,n,a){if(!Gi(n))throw Error(i(200));return Ki(null,e,n,!1,a)},pt.unmountComponentAtNode=function(e){if(!Gi(e))throw Error(i(40));return e._reactRootContainer?(Un(function(){Ki(null,null,e,!1,function(){e._reactRootContainer=null,e[Jt]=null})}),!0):!1},pt.unstable_batchedUpdates=Sl,pt.unstable_renderSubtreeIntoContainer=function(e,n,a,l){if(!Gi(a))throw Error(i(200));if(e==null||e._reactInternals===void 0)throw Error(i(38));return Ki(e,n,a,!1,l)},pt.version="18.3.1-next-f1338f8080-20240426",pt}var xm;function rx(){if(xm)return Il.exports;xm=1;function t(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(t)}catch(s){console.error(s)}}return t(),Il.exports=sx(),Il.exports}var wm;function ix(){if(wm)return Yi;wm=1;var t=rx();return Yi.createRoot=t.createRoot,Yi.hydrateRoot=t.hydrateRoot,Yi}var ax=ix();class ox extends Error{constructor(i,o){super(i);dm(this,"status");this.status=o}}async function Ge(t,s){const i=await fetch(t,{...s,credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json",...s==null?void 0:s.headers}}),o=await i.json().catch(()=>({}));if(!i.ok)throw new ox(o.error||i.statusText||"Request failed",i.status);return o}const oc=()=>Ge("/auth/status"),lx=()=>Ge("/api/config"),fa=()=>Ge("/api/botstats"),cx=()=>Ge("/api/team"),ux=t=>Ge(`/api/team/${t}`),lc=()=>Ge("/api/staff/me"),dx=(t,s)=>Ge("/api/staff/profile",{method:"POST",headers:s?{"X-CSRF-Token":s}:void 0,body:JSON.stringify(t)}),hx=(t,s)=>Ge("/api/staff/global-profile",{method:"POST",headers:s?{"X-CSRF-Token":s}:void 0,body:JSON.stringify(t)}),mx=()=>Ge("/api/commands"),cc=()=>Ge("/api/guilds"),bm=()=>Ge("/api/me/overview"),fx=t=>Ge(`/api/guild/${t}/overview`),px=t=>Ge(`/api/guild/${t}/levels`),km=t=>Ge(`/api/guild/${t}/config`),jm=t=>Ge(`/api/guild/${t}/resources`);function Aa(t,s,i,o){return Ge(`/api/guild/${t}/config/${s}`,{method:"POST",headers:o?{"X-CSRF-Token":o}:void 0,body:JSON.stringify(i)})}function gx(t,s,i){return Ge(`/api/guild/${t}/config/profile`,{method:"POST",headers:i?{"X-CSRF-Token":i}:void 0,body:JSON.stringify(s)})}function tp(t){return t.replace(/\/+$/,"")||"/"}function Sm(t=window.location.pathname){const s=tp(t);return s==="/commands"?"commands":s==="/docs"?"docs":s.startsWith("/docs/")?"docs-detail":s==="/dashboard/staff"||s==="/dashboard/staff/"?"staff":s==="/dashboard"||s.startsWith("/dashboard/")?"dashboard":s==="/team"?"team":s.startsWith("/team/")?"team-member":s==="/privacy"?"privacy":s==="/terms"?"terms":s==="/community"?"community":s==="/donate"||s.startsWith("/donate")?"donate":s==="/transcript"||s.startsWith("/transcript/")?"transcript":s==="/changelog"?"changelog":s.startsWith("/changelog/")?"changelog-detail":"home"}function Ps(t,s="overview"){return t?`/dashboard/${t}/${s}`:"/dashboard"}function uc(){return"/dashboard/servers"}function Nm(){const t=tp(window.location.pathname).split("/").filter(Boolean),s=["overview","leveling","moderation","server","ai","customization"];return t[1]==="servers"?{view:"servers",guildId:null,section:"overview"}:!t[1]||t[1]==="staff"?{view:"overview",guildId:null,section:"overview"}:{view:"guild",guildId:t[1]||null,section:s.includes(t[2])?t[2]:"overview"}}function he(t){t.startsWith("/")&&(window.history.pushState({},"",t),window.dispatchEvent(new PopStateEvent("popstate")),window.scrollTo({top:0,behavior:"smooth"}))}let Cm=null,Bl=null;function Rr(){const[t,s]=P.useState(Cm);return P.useEffect(()=>{Bl||(Bl=lx().then(i=>Cm=i)),Bl.then(s).catch(()=>{})},[]),t}function np({onNavigate:t}){const s=Rr();return r.jsxs("a",{className:"brand",href:"/",onClick:i=>{i.preventDefault(),t?t():he("/")},children:[r.jsx("span",{className:"brand-mark",children:s!=null&&s.bot_avatar_url?r.jsx("img",{src:s.bot_avatar_url,alt:"Niko"}):"n"}),r.jsx("span",{children:"niko"})]})}function zt(){return r.jsxs("footer",{className:"site-footer",children:[r.jsx(np,{}),r.jsx("span",{children:"Built for communities that care."}),r.jsxs("div",{children:[r.jsx("a",{href:"/changelog",onClick:t=>{t.preventDefault(),he("/changelog")},children:"Changelog"}),r.jsx("a",{href:"/privacy",onClick:t=>{t.preventDefault(),he("/privacy")},children:"Privacy"}),r.jsx("a",{href:"/terms",onClick:t=>{t.preventDefault(),he("/terms")},children:"Terms"}),r.jsx("a",{href:"/community",onClick:t=>{t.preventDefault(),he("/community")},children:"Community Policy"}),r.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"GitHub"})]})]})}/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const sp=(...t)=>t.filter((s,i,o)=>!!s&&s.trim()!==""&&o.indexOf(s)===i).join(" ").trim();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const yx=t=>t.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const vx=t=>t.replace(/^([A-Z])|[\s-_]+(\w)/g,(s,i,o)=>o?o.toUpperCase():i.toLowerCase());/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Tm=t=>{const s=vx(t);return s.charAt(0).toUpperCase()+s.slice(1)};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var Ol={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const xx=t=>{for(const s in t)if(s.startsWith("aria-")||s==="role"||s==="title")return!0;return!1},wx=P.createContext({}),bx=()=>P.useContext(wx),kx=P.forwardRef(({color:t,size:s,strokeWidth:i,absoluteStrokeWidth:o,className:c="",children:d,iconNode:h,...f},p)=>{const{size:v=24,strokeWidth:g=2,absoluteStrokeWidth:x=!1,color:w="currentColor",className:k=""}=bx()??{},S=o??x?Number(i??g)*24/Number(s??v):i??g;return P.createElement("svg",{ref:p,...Ol,width:s??v??Ol.width,height:s??v??Ol.height,stroke:t??w,strokeWidth:S,className:sp("lucide",k,c),...!d&&!xx(f)&&{"aria-hidden":"true"},...f},[...h.map(([j,N])=>P.createElement(j,N)),...Array.isArray(d)?d:[d]])});/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const et=(t,s)=>{const i=P.forwardRef(({className:o,...c},d)=>P.createElement(kx,{ref:d,iconNode:s,className:sp(`lucide-${yx(Tm(t))}`,`lucide-${t}`,o),...c}));return i.displayName=Tm(t),i};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jx=[["path",{d:"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2",key:"169zse"}]],Sx=et("activity",jx);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Nx=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]],Cx=et("arrow-right",Nx);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Tx=[["path",{d:"M12 5v16",key:"1f6ucr"}],["path",{d:"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z",key:"1fyvmf"}]],Pm=et("book-open",Tx);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Px=[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],ia=et("chart-column",Px);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ex=[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]],Mx=et("external-link",Ex);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ax=[["line",{x1:"4",x2:"20",y1:"9",y2:"9",key:"4lhtct"}],["line",{x1:"4",x2:"20",y1:"15",y2:"15",key:"vyu0kd"}],["line",{x1:"10",x2:"8",y1:"3",y2:"21",key:"1ggp8o"}],["line",{x1:"16",x2:"14",y1:"3",y2:"21",key:"weycgp"}]],_x=et("hash",Ax);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Dx=[["rect",{width:"7",height:"7",x:"3",y:"3",rx:"1",key:"1g98yp"}],["rect",{width:"7",height:"7",x:"14",y:"3",rx:"1",key:"6d4xhi"}],["rect",{width:"7",height:"7",x:"14",y:"14",rx:"1",key:"nxv5o0"}],["rect",{width:"7",height:"7",x:"3",y:"14",rx:"1",key:"1bb6yr"}]],dc=et("layout-grid",Dx);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Rx=[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]],Lx=et("lock-keyhole",Rx);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ix=[["path",{d:"m16 17 5-5-5-5",key:"1bji2h"}],["path",{d:"M21 12H9",key:"dn1m92"}],["path",{d:"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4",key:"1uf3rs"}]],Vx=et("log-out",Ix);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Fx=[["path",{d:"M4 5h16",key:"1tepv9"}],["path",{d:"M4 12h16",key:"1lakjw"}],["path",{d:"M4 19h16",key:"1djgab"}]],Bx=et("menu",Fx);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ox=[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]],zx=et("search",Ox);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ux=[["path",{d:"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915",key:"1i5ecw"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]],qi=et("settings",Ux);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Wx=[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}]],zl=et("shield",Wx);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const $x=[["path",{d:"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",key:"1s2grr"}],["path",{d:"M20 2v4",key:"1rf3ol"}],["path",{d:"M22 4h-4",key:"gwowj6"}],["circle",{cx:"4",cy:"20",r:"2",key:"6kqj1y"}]],Qi=et("sparkles",$x);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Hx=[["path",{d:"M12 19h8",key:"baeox8"}],["path",{d:"m4 17 6-6-6-6",key:"1yngyt"}]],Gx=et("terminal",Hx);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Kx=[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["path",{d:"M16 3.128a4 4 0 0 1 0 7.744",key:"16gr8j"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}]],hc=et("users",Kx);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Xx=[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]],Yx=et("x",Xx),qx={arrow:Cx,grid:dc,terminal:Gx,chart:ia,shield:zl,spark:Qi,users:hc,settings:qi,book:Pm,external:Mx,menu:Bx,close:Yx,lock:Lx,logout:Vx,search:zx,doc:Pm,utility:qi,icon_home:dc,icon_settings:qi,icon_economy:ia,icon_leveling:ia,icon_moderation:zl,icon_automod:zl,icon_heart:Qi,icon_utility:qi,icon_bot:hc,icon_ai:Qi,icon_lightbulb:Qi};function ee({name:t,size:s,className:i=""}){const o=qx[t]||dc;return r.jsx(o,{className:`icon ${i}`.trim(),"aria-hidden":"true",focusable:"false",strokeWidth:1.8,style:s?{width:s,height:s}:void 0})}const Em=[{label:"Home",path:"/",page:"home"},{label:"Commands",path:"/commands",page:"commands"},{label:"Docs",path:"/docs",page:"docs"},{label:"Team",path:"/team",page:"team"},{label:"Changelog",path:"/changelog",page:"changelog"}];function qe({page:t}){const s=Rr(),i=t==="dashboard",[o,c]=P.useState(!1),d=h=>f=>{f.preventDefault(),c(!1),he(h)};return r.jsxs("header",{className:`site-header${i?" dashboard-header":""}`,children:[r.jsx(np,{onNavigate:()=>c(!1)}),!i&&r.jsx("nav",{className:"site-nav","aria-label":"Main navigation",children:Em.map(h=>r.jsx("a",{className:t===h.page?"active":"","aria-current":t===h.page?"page":void 0,href:h.path,onClick:d(h.path),children:h.label},h.path))}),r.jsx("div",{className:"header-actions",children:i?r.jsxs("div",{className:"dashboard-menu",children:[r.jsxs("button",{className:"button button-small button-muted dashboard-menu-trigger",type:"button","aria-expanded":o,"aria-controls":"dashboard-navigation-menu",onClick:()=>c(h=>!h),children:[r.jsx(ee,{name:o?"close":"menu"}),r.jsx("span",{children:"Menu"})]}),o&&r.jsxs("nav",{id:"dashboard-navigation-menu",className:"dashboard-menu-popover","aria-label":"Dashboard navigation",children:[r.jsx("span",{className:"dashboard-menu-label",children:"Navigate"}),Em.map(h=>r.jsx("a",{href:h.path,onClick:d(h.path),children:h.label},h.path)),r.jsx("a",{className:"dashboard-menu-current",href:"/dashboard","aria-current":"page",onClick:d("/dashboard"),children:"Dashboard"})]})]}):r.jsxs(r.Fragment,{children:[r.jsxs("a",{className:"button button-small button-muted dashboard-link",href:"/dashboard",onClick:d("/dashboard"),children:["Dashboard ",r.jsx(ee,{name:"arrow"})]}),r.jsx("a",{className:"button button-small button-primary",href:(s==null?void 0:s.invite_url)||"#",target:"_blank",rel:"noreferrer",children:"Add to Discord"})]})})]})}const Mm=typeof navigator<"u"?(navigator.language||"en").slice(0,2):"en";function mc(t){const s=t.description;if(typeof s=="string")return s;if(s&&typeof s=="object"){const i=s;if(i[Mm])return i[Mm];if(i.en)return i.en;const o=Object.values(i).find(c=>typeof c=="string"&&c.length>0);if(o)return o}return"A Niko command for your server."}const Qx=[{value:"all",label:"All commands"},{value:"slash",label:"Slash"},{value:"prefix",label:"Prefix"},{value:"hybrid",label:"Hybrid"},{value:"context",label:"Context menus"}],pa={slash:"Slash command",prefix:"Prefix command",hybrid:"Hybrid command",context:"Context menu"};function Yn(t){return t.type&&t.type in pa?t.type:"slash"}function Jx(t){return t.context_type==="user"?"Right-click a user":"Right-click a message"}function rp(t){const s=Yn(t);return s==="slash"?r.jsxs("code",{children:["/",t.name]}):s==="prefix"?r.jsxs("code",{children:[".",t.name]}):s==="hybrid"?r.jsxs(r.Fragment,{children:[r.jsxs("code",{children:["/",t.name]}),r.jsx("span",{className:"command-or",children:"or"}),r.jsxs("code",{children:[".",t.name]})]}):r.jsxs("code",{className:"context-invocation",children:[Jx(t)," · ",t.name]})}function Am(t){return t!=null&&t.length?t:["Not specified"]}function Zx({command:t,onClose:s}){P.useEffect(()=>{const h=f=>{f.key==="Escape"&&s()};return document.addEventListener("keydown",h),()=>document.removeEventListener("keydown",h)},[s]);const i=t.parameters||[],o=t.subcommands||[],c=Am(t.aliases),d=Am(t.permissions);return r.jsx("div",{className:"command-dialog-backdrop",role:"presentation",onMouseDown:h=>{h.currentTarget===h.target&&s()},children:r.jsxs("section",{className:"command-dialog",role:"dialog","aria-modal":"true","aria-labelledby":"command-dialog-title",children:[r.jsxs("header",{className:"command-dialog-header",children:[r.jsxs("div",{children:[r.jsxs("div",{className:"command-dialog-kicker",children:[t.category," · ",pa[Yn(t)]]}),r.jsx("h2",{id:"command-dialog-title",children:rp(t)})]}),r.jsx("button",{className:"dialog-close",type:"button",onClick:s,"aria-label":"Close command details",title:"Close command details",children:r.jsx(ee,{name:"close"})})]}),r.jsxs("div",{className:"command-dialog-body",children:[r.jsx("p",{className:"command-dialog-description",children:mc(t)}),r.jsxs("div",{className:"command-detail-grid",children:[r.jsxs("section",{className:"command-detail-section command-detail-wide",children:[r.jsx("h3",{children:"Usage"}),r.jsx("code",{className:"command-usage",children:t.usage||`${Yn(t)==="context"?t.name:`/${t.name}`}`})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Permissions"}),r.jsx("ul",{className:"command-detail-list",children:d.map(h=>r.jsx("li",{children:h},h))})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Aliases"}),r.jsx("ul",{className:"command-detail-list",children:c.map(h=>r.jsx("li",{children:r.jsx("code",{children:h==="Not specified"?h:`.${h}`})},h))})]})]}),!!i.length&&r.jsxs("section",{className:"command-detail-section command-parameters",children:[r.jsx("h3",{children:"Parameters"}),r.jsx("div",{className:"command-parameter-list",children:i.map(h=>r.jsxs("div",{className:"command-parameter",children:[r.jsxs("div",{className:"command-parameter-title",children:[r.jsx("code",{children:h.name}),r.jsxs("span",{children:[h.required?"Required":"Optional"," · ",h.type]})]}),r.jsx("p",{children:h.description||"No description provided."})]},h.name))})]}),!!o.length&&r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Subcommands"}),r.jsx("div",{className:"subcommand-list",children:o.map(h=>r.jsxs("code",{children:[t.name," ",h]},h))})]})]}),r.jsxs("footer",{className:"command-dialog-footer",children:[r.jsx("span",{children:"Command registry details are generated from the live bot."}),r.jsx("button",{className:"button button-primary button-small",type:"button",onClick:s,children:"Done"})]})]})})}function ew(){const[t,s]=P.useState([]),[i,o]=P.useState(null),[c,d]=P.useState(""),[h,f]=P.useState("all"),[p,v]=P.useState("all"),[g,x]=P.useState(!0),[w,k]=P.useState("");P.useEffect(()=>{mx().then(s).catch(()=>k("The command registry is unavailable right now.")).finally(()=>x(!1))},[]),P.useEffect(()=>{if(!i)return;const N=document.body.style.overflow;return document.body.style.overflow="hidden",()=>{document.body.style.overflow=N}},[i]);const S=P.useMemo(()=>["all",...Array.from(new Set(t.map(N=>N.category))).sort()],[t]),j=t.filter(N=>{const B=`${N.name} ${mc(N)} ${N.category} ${pa[Yn(N)]} ${N.context_type||""} ${(N.aliases||[]).join(" ")}`.toLowerCase();return(p==="all"||Yn(N)===p)&&(h==="all"||N.category===h)&&B.includes(c.trim().toLowerCase())});return r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"commands"}),r.jsxs("main",{className:"shell page-main",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Reference library"}),r.jsxs("h1",{children:["Everything Niko",r.jsx("br",{}),r.jsx("em",{children:"knows how to do."})]}),r.jsx("p",{children:"Browse slash, prefix, hybrid, and context commands from the live bot registry. Select any command for permissions, aliases, parameters, usage, and subcommands."})]}),r.jsxs("div",{className:"command-toolbar",children:[r.jsxs("label",{className:"search-field",children:[r.jsx("span",{"aria-hidden":"true",children:"⌕"}),r.jsx("input",{value:c,onChange:N=>d(N.target.value),placeholder:"Search commands","aria-label":"Search commands"})]}),r.jsxs("div",{className:"command-filters",children:[r.jsx("div",{className:"filter-list","aria-label":"Command types",children:Qx.map(N=>r.jsx("button",{type:"button",className:p===N.value?"filter active":"filter","aria-pressed":p===N.value,onClick:()=>v(N.value),children:N.label},N.value))}),r.jsx("div",{className:"filter-list","aria-label":"Command categories",children:S.map(N=>r.jsx("button",{type:"button",className:h===N?"filter active":"filter","aria-pressed":h===N,onClick:()=>f(N),children:N==="all"?"All categories":N},N))})]})]}),r.jsxs("div",{className:"command-meta",children:[r.jsx("strong",{children:g?"…":j.length})," commands ",r.jsx("span",{children:"·"})," live bot registry ",r.jsx("span",{children:"·"})," select a card for details"]}),w&&r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Could not load commands"}),r.jsx("span",{children:w})]}),r.jsxs("div",{className:"commands-grid",children:[j.map(N=>r.jsxs("button",{className:"command-card",type:"button",onClick:()=>o(N),"aria-label":`View details for ${N.name}`,children:[r.jsxs("span",{className:"command-card-head",children:[r.jsx("span",{className:"command-name",children:rp(N)}),r.jsx("span",{className:"command-type",children:pa[Yn(N)]})]}),r.jsx("span",{className:"command-card-description",children:mc(N)}),r.jsxs("span",{className:"command-card-footer",children:[r.jsx("span",{className:"category-tag",children:N.category}),r.jsxs("span",{className:"command-expand",children:[r.jsx("span",{children:"Details"}),r.jsx(ee,{name:"arrow",size:14})]})]})]},`${Yn(N)}-${N.context_type||""}-${N.category}-${N.name}`)),!g&&!w&&!j.length&&r.jsx("div",{className:"empty-state",children:"No commands match that search."})]})]}),r.jsx(zt,{}),i&&r.jsx(Zx,{command:i,onClose:()=>o(null)})]})}function ve(t){return t==null?"—":new Intl.NumberFormat("en-US",{notation:t>9999?"compact":"standard"}).format(t)}function ip(t){return(t==null?void 0:t.global_name)||(t==null?void 0:t.username)||"there"}function ap(t){return t.split(/\s+/).map(s=>s[0]).join("").slice(0,2).toUpperCase()}function Oc({guild:t,className:s="guild-avatar"}){return r.jsx("span",{className:s,"aria-hidden":"true",children:t.icon_url?r.jsx("img",{src:t.icon_url,alt:""}):t.name.slice(0,1).toUpperCase()})}function op({user:t,className:s="avatar"}){const i=t.avatar?`https://cdn.discordapp.com/avatars/${t.id}/${t.avatar}.${t.avatar.startsWith("a_")?"gif":"png"}?size=64`:null;return r.jsx("span",{className:s,"aria-hidden":"true",children:i?r.jsx("img",{src:i,alt:""}):ap(t.global_name||t.username||"Niko")})}function tw({name:t,avatarUrl:s,className:i="member-avatar"}){return r.jsx("span",{className:i,"aria-hidden":"true",children:s?r.jsx("img",{src:s,alt:""}):ap(t)})}const nw=[["overview","Overview","grid","At a glance"],["leveling","Leveling","spark","Reward participation"],["moderation","Moderation","shield","Keep things steady"],["server","Server","settings","Manage server features"],["ai","AI controls","settings","Shape Niko’s voice"],["customization","Customization","paint","Niko’s server identity"]];function lp({user:t,guilds:s,selectedGuild:i,view:o,section:c,stats:d,onHome:h,onServers:f,onGuildChange:p,onSectionChange:v,onRefresh:g,refreshing:x,staffRole:w,children:k}){const S=s.filter(M=>M.installed!==!1),j=(M=!1)=>r.jsx("nav",{className:M?"dash-nav dash-nav-mobile":"dash-nav","aria-label":"Server settings",children:nw.map(([L,I,D])=>r.jsxs("button",{className:o==="guild"&&c===L?"active":"","aria-current":o==="guild"&&c===L?"page":void 0,onClick:()=>v(L),children:[r.jsx(ee,{name:D}),r.jsx("span",{children:I})]},L))}),N=(M=!1)=>r.jsxs("nav",{className:M?"dash-nav dash-primary-nav dash-nav-mobile":"dash-nav dash-primary-nav","aria-label":"Dashboard",children:[r.jsxs("button",{className:o==="overview"?"active":"","aria-current":o==="overview"?"page":void 0,onClick:h,children:[r.jsx(ee,{name:"grid"}),r.jsx("span",{children:"My overview"})]}),r.jsxs("button",{className:o==="servers"?"active":"","aria-current":o==="servers"?"page":void 0,onClick:f,children:[r.jsx(ee,{name:"users"}),r.jsx("span",{children:"My servers"})]}),w&&r.jsxs("button",{onClick:()=>he("/dashboard/staff"),children:[r.jsx(ee,{name:"shield"}),r.jsx("span",{children:"Staff workspace"})]})]}),B=()=>r.jsxs("div",{className:"dash-top-actions",children:[o==="guild"?r.jsxs("label",{className:"guild-switcher",children:[r.jsx("span",{className:"sr-only",children:"Switch server"}),r.jsxs("select",{value:(i==null?void 0:i.id)||"",onChange:M=>{const L=S.find(I=>I.id===M.target.value);L&&p(L)},children:[r.jsx("option",{value:"",disabled:!0,children:"Switch server"}),S.map(M=>r.jsx("option",{value:M.id,children:M.name},M.id))]})]}):r.jsxs("button",{className:"button button-muted button-small top-action",onClick:f,children:[r.jsx(ee,{name:"users"})," Browse servers"]}),r.jsxs("button",{className:"button button-muted button-small top-action refresh-action",onClick:g,disabled:x,"aria-label":"Refresh dashboard data",children:[r.jsx(ee,{name:"spark"})," ",x?"Refreshing…":"Refresh data"]}),o==="guild"&&r.jsxs("span",{className:"connection-chip",children:[r.jsx("span",{className:"status-dot"})," Connected"]}),r.jsxs("div",{className:"user-pill",children:[r.jsx(op,{user:t}),r.jsx("span",{children:ip(t)})]}),r.jsx("a",{className:"logout-button",href:"/auth/logout","aria-label":"Log out",title:"Log out",children:r.jsx(ee,{name:"logout"})})]});return r.jsxs("div",{className:"dashboard-layout",children:[r.jsxs("aside",{className:"dash-sidebar",children:[r.jsx("div",{className:"dash-mobile-controls",children:B()}),r.jsxs("div",{className:"side-rail-heading",children:[r.jsx("span",{className:"side-label",children:"Workspace"}),r.jsxs("span",{className:"rail-status",children:[r.jsx("span",{className:"status-dot"})," Live"]})]}),N(),o==="guild"&&i&&r.jsxs(r.Fragment,{children:[r.jsx("div",{className:"side-label side-label-settings",children:"Current server"}),r.jsxs("div",{className:"side-guild",children:[r.jsx(Oc,{guild:i}),r.jsxs("span",{children:[r.jsx("strong",{children:i.name}),r.jsx("small",{children:"Live configuration"})]}),r.jsx("span",{className:"guild-presence",title:"Niko is connected",children:r.jsx("span",{className:"status-dot"})})]}),r.jsxs("div",{className:"side-settings-caption",children:[r.jsx("span",{children:"Settings map"}),r.jsx("small",{children:"Pick a room to tune"})]}),j()]}),r.jsxs("div",{className:"sidebar-bottom",children:[r.jsxs("span",{className:"online-label",children:[r.jsx("span",{className:"status-dot"})," Niko is online"]}),r.jsxs("small",{children:[ve(d==null?void 0:d.guild_count)," connected servers · v",(d==null?void 0:d.version)||"1.0"]}),r.jsxs("a",{href:"/",onClick:M=>{M.preventDefault(),he("/")},children:["Back to public site ",r.jsx(ee,{name:"arrow"})]})]})]}),r.jsxs("div",{className:"dash-content",children:[r.jsx(qe,{page:"dashboard"}),r.jsx("div",{className:"dash-contextbar",children:B()}),r.jsx("div",{className:"mobile-primary-bar",children:N(!0)}),o==="guild"&&r.jsx("div",{className:"mobile-section-bar",children:j(!0)}),r.jsx("main",{className:"dash-main",children:k})]})]})}const cp=P.createContext({});function sw(t){const s=P.useRef(null);return s.current===null&&(s.current=t()),s.current}const rw=typeof window<"u",iw=rw?P.useLayoutEffect:P.useEffect,zc=P.createContext(null);function Uc(t,s){t.indexOf(s)===-1&&t.push(s)}function ga(t,s){const i=t.indexOf(s);i>-1&&t.splice(i,1)}const Ut=(t,s,i)=>i>s?s:i<t?t:i;let _a=()=>{};const ln={},Wc=t=>/^-?(?:\d+(?:\.\d+)?|\.\d+)$/u.test(t),up=t=>typeof t=="object"&&t!==null,$c=t=>/^0[^.\s]+$/u.test(t);function dp(t){let s;return()=>(s===void 0&&(s=t()),s)}const Ot=t=>t,Lr=(...t)=>t.reduce((s,i)=>o=>i(s(o))),Er=(t,s,i)=>{const o=s-t;return o?(i-t)/o:1};class ya{constructor(){this.subscriptions=[]}add(s){return Uc(this.subscriptions,s),()=>this.remove(s)}remove(s){ga(this.subscriptions,s)}notify(s,i,o){const c=this.subscriptions.length;if(c)if(c===1)this.subscriptions[0](s,i,o);else for(let d=0;d<c;d++){const h=this.subscriptions[d];h&&h(s,i,o)}}getSize(){return this.subscriptions.length}clear(){this.subscriptions.length=0}}const Mt=t=>t*1e3,kt=t=>t/1e3,hp=(t,s)=>s?t*(1e3/s):0,mp=(t,s,i)=>(((1-3*i+3*s)*t+(3*i-6*s))*t+3*s)*t,aw=1e-7,ow=12;function lw(t,s,i,o,c){let d,h,f=0;do h=s+(i-s)/2,d=mp(h,o,c)-t,d>0?i=h:s=h;while(Math.abs(d)>aw&&++f<ow);return h}function Ir(t,s,i,o){if(t===s&&i===o)return Ot;const c=d=>lw(d,0,1,t,i);return d=>d===0||d===1?d:mp(c(d),s,o)}const fp=t=>s=>s<=.5?t(2*s)/2:(2-t(2*(1-s)))/2,pp=t=>s=>1-t(1-s),gp=Ir(.33,1.53,.69,.99),Hc=pp(gp),yp=fp(Hc),vp=t=>t>=1?1:(t*=2)<1?.5*Hc(t):.5*(2-Math.pow(2,-10*(t-1))),Gc=t=>1-Math.sin(Math.acos(t)),xp=pp(Gc),wp=fp(Gc),cw=Ir(.42,0,1,1),uw=Ir(0,0,.58,1),bp=Ir(.42,0,.58,1),dw=t=>Array.isArray(t)&&typeof t[0]!="number",kp=t=>Array.isArray(t)&&typeof t[0]=="number",hw={linear:Ot,easeIn:cw,easeInOut:bp,easeOut:uw,circIn:Gc,circInOut:wp,circOut:xp,backIn:Hc,backInOut:yp,backOut:gp,anticipate:vp},mw=t=>typeof t=="string",_m=t=>{if(kp(t)){_a(t.length===4);const[s,i,o,c]=t;return Ir(s,i,o,c)}else if(mw(t))return hw[t];return t},Ji=["setup","read","resolveKeyframes","preUpdate","update","preRender","render","postRender"];function fw(t){let s=new Set,i=new Set,o=!1,c=!1;const d=new Set;let h={delta:0,timestamp:0,isProcessing:!1};function f(v){d.has(v)&&(i.add(v),t()),v(h)}const p={schedule:(v,g=!1,x=!1)=>{const k=x&&o?s:i;return g&&d.add(v),k.add(v),v},cancel:v=>{i.delete(v),d.delete(v)},process:v=>{if(h=v,o){c=!0;return}o=!0;const g=s;s=i,i=g,s.forEach(f),s.clear(),o=!1,c&&(c=!1,p.process(v))}};return p}const pw=40;function jp(t,s){let i=!1,o=!0;const c={delta:0,timestamp:0,isProcessing:!1},d=()=>i=!0,h=Ji.reduce((L,I)=>(L[I]=fw(d),L),{}),{setup:f,read:p,resolveKeyframes:v,preUpdate:g,update:x,preRender:w,render:k,postRender:S}=h,j=()=>{const L=ln.useManualTiming,I=L?c.timestamp:performance.now();i=!1,L||(c.delta=o?1e3/60:Math.max(Math.min(I-c.timestamp,pw),1)),c.timestamp=I,c.isProcessing=!0,f.process(c),p.process(c),v.process(c),g.process(c),x.process(c),w.process(c),k.process(c),S.process(c),c.isProcessing=!1,i&&s&&(o=!1,t(j))},N=()=>{i=!0,o=!0,c.isProcessing||t(j)};return{schedule:Ji.reduce((L,I)=>{const D=h[I];return L[I]=(F,V=!1,O=!1)=>(i||N(),D.schedule(F,V,O)),L},{}),cancel:L=>{for(let I=0;I<Ji.length;I++)h[Ji[I]].cancel(L)},state:c,steps:h}}const{schedule:je,cancel:Mn,state:$e,steps:Ul}=jp(typeof requestAnimationFrame<"u"?requestAnimationFrame:Ot,!0);let aa;function gw(){aa=void 0}const it={now:()=>(aa===void 0&&it.set($e.isProcessing||ln.useManualTiming?$e.timestamp:performance.now()),aa),set:t=>{aa=t,queueMicrotask(gw)}},Ds=t=>Math.round(t*1e5)/1e5,Sp=t=>s=>typeof s=="string"&&s.startsWith(t),Np=Sp("--"),yw=Sp("var(--"),Kc=t=>yw(t)?vw.test(t.split("/*")[0].trim()):!1,vw=/var\(--(?:[\w-]+\s*|[\w-]+\s*,(?:\s*[^)(\s]|\s*\((?:[^)(]|\([^)(]*\))*\))+\s*)\)$/iu;function Dm(t){return typeof t!="string"?!1:t.split("/*")[0].includes("var(--")}const Ls={test:t=>typeof t=="number",parse:parseFloat,transform:t=>t},Mr={...Ls,transform:t=>Ut(0,1,t)},Zi={...Ls,default:1},Xc=/-?(?:\d+(?:\.\d+)?|\.\d+)/gu;function xw(t){return t==null}const ww=/^(?:#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\))$/iu,Yc=(t,s)=>i=>!!(typeof i=="string"&&ww.test(i)&&i.startsWith(t)||s&&!xw(i)&&Object.prototype.hasOwnProperty.call(i,s)),Cp=(t,s,i)=>o=>{if(typeof o!="string")return o;const[c,d,h,f]=o.match(Xc);return{[t]:parseFloat(c),[s]:parseFloat(d),[i]:parseFloat(h),alpha:f!==void 0?parseFloat(f):1}},bw=t=>Ut(0,255,t),Wl={...Ls,transform:t=>Math.round(bw(t))},qn={test:Yc("rgb","red"),parse:Cp("red","green","blue"),transform:({red:t,green:s,blue:i,alpha:o=1})=>"rgba("+Wl.transform(t)+", "+Wl.transform(s)+", "+Wl.transform(i)+", "+Ds(Mr.transform(o))+")"};function kw(t){let s="",i="",o="",c="";return t.length>5?(s=t.substring(1,3),i=t.substring(3,5),o=t.substring(5,7),c=t.substring(7,9)):(s=t.substring(1,2),i=t.substring(2,3),o=t.substring(3,4),c=t.substring(4,5),s+=s,i+=i,o+=o,c+=c),{red:parseInt(s,16),green:parseInt(i,16),blue:parseInt(o,16),alpha:c?parseInt(c,16)/255:1}}const fc={test:Yc("#"),parse:kw,transform:qn.transform},Vr=t=>({test:s=>typeof s=="string"&&s.endsWith(t)&&s.split(" ").length===1,parse:parseFloat,transform:s=>`${s}${t}`}),on=Vr("deg"),Qt=Vr("%"),Q=Vr("px"),jw=Vr("vh"),Sw=Vr("vw"),Rm={...Qt,parse:t=>Qt.parse(t)/100,transform:t=>Qt.transform(t*100)},Ms={test:Yc("hsl","hue"),parse:Cp("hue","saturation","lightness"),transform:({hue:t,saturation:s,lightness:i,alpha:o=1})=>"hsla("+Math.round(t)+", "+Qt.transform(Ds(s))+", "+Qt.transform(Ds(i))+", "+Ds(Mr.transform(o))+")"},He={test:t=>qn.test(t)||fc.test(t)||Ms.test(t),parse:t=>qn.test(t)?qn.parse(t):Ms.test(t)?Ms.parse(t):fc.parse(t),transform:t=>typeof t=="string"?t:t.hasOwnProperty("red")?qn.transform(t):Ms.transform(t),getAnimatableNone:t=>{const s=He.parse(t);return s.alpha=0,He.transform(s)}},Nw=/(?:#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\))/giu,Tp=new RegExp(Xc.source),Pp=new RegExp(Nw.source,"i");function Cw(t){return isNaN(t)&&typeof t=="string"&&(Tp.test(t)||Pp.test(t))}const Ep="number",Mp="color",Tw="var",Pw="var(",Lm="${}",Ew=/var\s*\(\s*--(?:[\w-]+\s*|[\w-]+\s*,(?:\s*[^)(\s]|\s*\((?:[^)(]|\([^)(]*\))*\))+\s*)\)|#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\)|-?(?:\d+(?:\.\d+)?|\.\d+)/giu;function Mw(t){const s=t.toString();return Tp.test(s)||Pp.test(s)}function Ar(t){const s=t.toString(),i=[],o={color:[],number:[],var:[]},c=[];let d=0;const f=s.replace(Ew,p=>(He.test(p)?(o.color.push(d),c.push(Mp),i.push(He.parse(p))):p.startsWith(Pw)?(o.var.push(d),c.push(Tw),i.push(p)):(o.number.push(d),c.push(Ep),i.push(parseFloat(p))),++d,Lm)).split(Lm);return{values:i,split:f,indexes:o,types:c}}function Aw(t){return Ar(t).values}function Ap({split:t,types:s}){const i=t.length;return o=>{let c="";for(let d=0;d<i;d++)if(c+=t[d],o[d]!==void 0){const h=s[d];h===Ep?c+=Ds(o[d]):h===Mp?c+=He.transform(o[d]):c+=o[d]}return c}}function _w(t){return Ap(Ar(t))}const Dw=t=>typeof t=="number"?0:He.test(t)?He.getAnimatableNone(t):t,Rw=(t,s)=>typeof t=="number"?s!=null&&s.trim().endsWith("/")?t:0:Dw(t);function Lw(t){const s=Ar(t);return Ap(s)(s.values.map((o,c)=>Rw(o,s.split[c])))}const jt={test:Cw,parse:Aw,createTransformer:_w,getAnimatableNone:Lw};function $l(t,s,i){return i<0&&(i+=1),i>1&&(i-=1),i<1/6?t+(s-t)*6*i:i<1/2?s:i<2/3?t+(s-t)*(2/3-i)*6:t}function Iw({hue:t,saturation:s,lightness:i,alpha:o}){t/=360,s/=100,i/=100;let c=0,d=0,h=0;if(!s)c=d=h=i;else{const f=i<.5?i*(1+s):i+s-i*s,p=2*i-f;c=$l(p,f,t+1/3),d=$l(p,f,t),h=$l(p,f,t-1/3)}return{red:Math.round(c*255),green:Math.round(d*255),blue:Math.round(h*255),alpha:o}}function va(t,s){return i=>i>0?s:t}const ke=(t,s,i)=>t+(s-t)*i,Hl=(t,s,i)=>{const o=t*t,c=i*(s*s-o)+o;return c<0?0:Math.sqrt(c)},Vw=[fc,qn,Ms],Fw=t=>Vw.find(s=>s.test(t));function Im(t){const s=Fw(t);if(!s)return!1;let i=s.parse(t);return s===Ms&&(i=Iw(i)),i}const Vm=(t,s)=>{const i=Im(t),o=Im(s);if(!i||!o)return va(t,s);const c={...i};return d=>(c.red=Hl(i.red,o.red,d),c.green=Hl(i.green,o.green,d),c.blue=Hl(i.blue,o.blue,d),c.alpha=ke(i.alpha,o.alpha,d),qn.transform(c))},pc=new Set(["none","hidden"]);function Bw(t,s){return pc.has(t)?i=>i<=0?t:s:i=>i>=1?s:t}function Ow(t,s){return i=>ke(t,s,i)}function qc(t){return typeof t=="number"?Ow:typeof t=="string"?Kc(t)?va:He.test(t)?Vm:Ww:Array.isArray(t)?_p:typeof t=="object"?He.test(t)?Vm:zw:va}function _p(t,s){const i=[...t],o=i.length,c=t.map((d,h)=>qc(d)(d,s[h]));return d=>{for(let h=0;h<o;h++)i[h]=c[h](d);return i}}function zw(t,s){const i={...t,...s},o={};for(const c in i)t[c]!==void 0&&s[c]!==void 0&&(o[c]=qc(t[c])(t[c],s[c]));return c=>{for(const d in o)i[d]=o[d](c);return i}}function Uw(t,s){const i=[],o={color:0,var:0,number:0};for(let c=0;c<s.values.length;c++){const d=s.types[c],h=t.indexes[d][o[d]],f=t.values[h]??0;i[c]=f,o[d]++}return i}const Ww=(t,s)=>{const i=jt.createTransformer(s),o=Ar(t),c=Ar(s);return o.indexes.var.length===c.indexes.var.length&&o.indexes.color.length===c.indexes.color.length&&o.indexes.number.length>=c.indexes.number.length?pc.has(t)&&!c.values.length||pc.has(s)&&!o.values.length?Bw(t,s):Lr(_p(Uw(o,c),c.values),i):va(t,s)},Fm=/^(-?(?:\d+(?:\.\d*)?|\.\d+))([a-z%]*)$/iu;function $w(t,s){const i=Fm.exec(t);if(!i)return;const o=Fm.exec(s);if(!o||i[2]!==o[2])return;const c=i[2],d=parseFloat(i[1]),h=parseFloat(o[1]);return f=>Ds(ke(d,h,f))+c}function Qc(t,s,i){if(typeof t=="number"&&typeof s=="number"&&typeof i=="number")return ke(t,s,i);if(typeof t=="string"&&typeof s=="string"){const c=$w(t,s);if(c)return c}return qc(t)(t,s)}const Hw=t=>{const s=({timestamp:i})=>t(i);return{start:(i=!0)=>je.update(s,i),stop:()=>Mn(s),now:()=>$e.isProcessing?$e.timestamp:it.now()}},Dp=(t,s,i=10)=>{let o="";const c=Math.max(Math.round(s/i),2);for(let d=0;d<c;d++)o+=Math.round(t(d/(c-1))*1e4)/1e4+", ";return`linear(${o.substring(0,o.length-2)})`},Jc=2e4;function Zc(t,s=50,i=Jc,o){let c=0,d=t.next(c);for(;!d.done&&c<i;)c+=s,d=t.next(c);return c>=i?1/0:c}function Gw(t,s=100,i){const o=i({...t,keyframes:[0,s]}),c=Math.min(Zc(o),Jc);return{type:"keyframes",ease:d=>o.next(c*d).value/s,duration:kt(c)}}const Re={stiffness:100,damping:10,mass:1,velocity:0,duration:800,bounce:.3,visualDuration:.3,restSpeed:{granular:.01,default:2},restDelta:{granular:.005,default:.5},minDuration:.01,maxDuration:10,minDamping:.05,maxDamping:1};function gc(t,s){return t*Math.sqrt(1-s*s)}const Kw=12;function Xw(t,s,i){let o=i;for(let c=1;c<Kw;c++)o=o-t(o)/s(o);return o}const Gl=.001;function Yw({duration:t=Re.duration,bounce:s=Re.bounce,velocity:i=Re.velocity,mass:o=Re.mass}){let c,d,h=1-s;h=Ut(Re.minDamping,Re.maxDamping,h),t=Ut(Re.minDuration,Re.maxDuration,kt(t)),h<1?(c=v=>{const g=v*h,x=g*t,w=g-i,k=gc(v,h),S=Math.exp(-x);return Gl-w/k*S},d=v=>{const x=v*h*t,w=x*i+i,k=h*h*v*v*t,S=Math.exp(-x),j=gc(v*v,h);return(-c(v)+Gl>0?-1:1)*((w-k)*S)/j}):(c=v=>{const g=Math.exp(-v*t),x=(v-i)*t+1;return-Gl+g*x},d=v=>{const g=Math.exp(-v*t),x=(i-v)*(t*t);return g*x});const f=5/t,p=Xw(c,d,f);if(t=Mt(t),isNaN(p))return{stiffness:Re.stiffness,damping:Re.damping,duration:t};{const v=p*p*o;return{stiffness:v,damping:h*2*Math.sqrt(o*v),duration:t}}}const Rp=["duration","bounce"],Lp=["stiffness","damping","mass"];function xa(t,s){return s.some(i=>t[i]!==void 0)}function qw(t){let s={velocity:Re.velocity,stiffness:Re.stiffness,damping:Re.damping,mass:Re.mass,isResolvedFromDuration:!1,...t};if(!xa(t,Lp)&&xa(t,Rp))if(s.velocity=0,t.visualDuration){const i=t.visualDuration,o=2*Math.PI/(i*1.2),c=o*o,d=2*Ut(.05,1,1-(t.bounce||0))*Math.sqrt(c);s={...s,mass:Re.mass,stiffness:c,damping:d}}else{const i=Yw({...t,velocity:0});s={...s,...i,mass:Re.mass},s.isResolvedFromDuration=!0}return s}function wa(t=Re.visualDuration,s=Re.bounce){const i=typeof t!="object"?{visualDuration:t,keyframes:[0,1],bounce:s}:t,o=i.keyframes[0],c=i.keyframes[i.keyframes.length-1],d={done:!1,value:o},{stiffness:h,damping:f,mass:p,duration:v,velocity:g,isResolvedFromDuration:x}=qw({...i,velocity:-kt(i.velocity||0)}),w=f/(2*Math.sqrt(h*p)),k=kt(Math.sqrt(h/p)),S=w*k,j={target:c,delta:c-o,velocity:g||0,restSpeed:0,restDelta:0},N=()=>{const V=Math.abs(j.delta)<5;j.restSpeed=i.restSpeed||(V?Re.restSpeed.granular:Re.restSpeed.default),j.restDelta=i.restDelta||(V?Re.restDelta.granular:Re.restDelta.default)};N();let B,M,L;if(w<1){const V=gc(k,w),O={A:0,sinC:0,cosC:0,t:-1,env:0,sin:0,cos:0};L=()=>{O.A=(j.velocity+S*j.delta)/V,O.sinC=S*O.A+j.delta*V,O.cosC=S*j.delta-O.A*V};const oe=le=>{le!==O.t&&(O.t=le,O.env=Math.exp(-S*le),O.sin=Math.sin(V*le),O.cos=Math.cos(V*le))};B=le=>(oe(le),j.target-O.env*(O.A*O.sin+j.delta*O.cos)),M=le=>(oe(le),O.env*(O.sinC*O.sin+O.cosC*O.cos))}else if(w===1){B=O=>j.target-Math.exp(-k*O)*(j.delta+(j.velocity+k*j.delta)*O);const V={C:0};L=()=>{V.C=j.velocity+k*j.delta},M=O=>Math.exp(-k*O)*(k*V.C*O-j.velocity)}else{const V=k*Math.sqrt(w*w-1);B=oe=>{const le=Math.exp(-S*oe),xe=Math.min(V*oe,300);return j.target-le*((j.velocity+S*j.delta)*Math.sinh(xe)+V*j.delta*Math.cosh(xe))/V};const O={P:0,sinh:0,cosh:0};L=()=>{O.P=(j.velocity+S*j.delta)/V,O.sinh=S*O.P-j.delta*V,O.cosh=S*j.delta-O.P*V},M=oe=>{const le=Math.exp(-S*oe),xe=Math.min(V*oe,300);return le*(O.sinh*Math.sinh(xe)+O.cosh*Math.cosh(xe))}}L();const I=!xa(i,Lp)&&xa(i,Rp),D=x&&v||null,F={calculatedDuration:D,retarget:(V,O)=>{j.target=V[V.length-1],j.delta=j.target-V[0],j.velocity=I?0:-kt(O),i.restSpeed&&i.restDelta||N(),F.calculatedDuration=D,d.done=!1,L()},velocity:V=>Mt(M(V)),next:V=>{const O=B(V);if(x)d.done=V>=v;else{const oe=Mt(M(V));d.done=Math.abs(oe)<=j.restSpeed&&Math.abs(j.target-O)<=j.restDelta}return d.value=d.done?j.target:O,d},toString:()=>{const V=Math.min(Zc(F),Jc),O=Dp(oe=>F.next(V*oe).value,V,30);return V+"ms "+O},toTransition:()=>{}};return F}wa.applyToOptions=t=>{const s=Gw(t,100,wa);return t.ease=s.ease,t.duration=Mt(s.duration),t.type="keyframes",t};function yc({keyframes:t,velocity:s=0,power:i=.8,timeConstant:o=325,bounceDamping:c=10,bounceStiffness:d=500,modifyTarget:h,min:f,max:p,restDelta:v=.5,restSpeed:g}){const x=t[0],w={done:!1,value:x},k=V=>V<f||V>p,S=V=>f===void 0?p:p===void 0||Math.abs(f-V)<Math.abs(p-V)?f:p;let j=i*s;const N=x+j,B=h===void 0?N:h(N);B!==N&&(j=B-x);const M=V=>-j*Math.exp(-V/o),L=V=>{const O=M(V);w.done=Math.abs(O)<=v,w.value=w.done?B:B+O};let I,D;const F=V=>{k(w.value)&&(I=V,D=wa({keyframes:[w.value,S(w.value)],velocity:-M(V)/o*1e3,damping:c,stiffness:d,restDelta:v,restSpeed:g}))};return F(0),{calculatedDuration:null,next:V=>{let O=!1;return!D&&I===void 0&&(O=!0,L(V),F(V)),I!==void 0&&V>=I?D.next(V-I):(!O&&L(V),w)}}}function Qw(t,s,i){const o=[],c=i||ln.mix||Qc,d=t.length-1;for(let h=0;h<d;h++){let f=c(t[h],t[h+1]);if(s){const p=Array.isArray(s)?s[h]||Ot:s;f=Lr(p,f)}o.push(f)}return o}function Jw(t,s,{clamp:i=!0,ease:o,mixer:c}={}){const d=t.length;if(_a(d===s.length),d===1)return()=>s[0];if(d===2&&s[0]===s[1])return()=>s[1];const h=t[0]===t[1];t[0]>t[d-1]&&(t=[...t].reverse(),s=[...s].reverse());const f=Qw(s,o,c),p=f.length,v=g=>{if(h&&g<t[0])return s[0];let x=0;if(p>1)for(;x<t.length-2&&!(g<t[x+1]);x++);const w=Er(t[x],t[x+1],g);return f[x](w)};return i?g=>v(Ut(t[0],t[d-1],g)):v}function Zw(t,s){const i=t[t.length-1];for(let o=1;o<=s;o++){const c=Er(0,s,o);t.push(ke(i,1,c))}}function eb(t){const s=[0];return Zw(s,t.length-1),s}function tb(t,s){return t.map(i=>i*s)}function nb(t,s){return t.map(()=>s||bp).splice(0,t.length-1)}function Cr({duration:t=300,keyframes:s,times:i,ease:o="easeInOut"}){const c=dw(o)?o.map(_m):_m(o),d={done:!1,value:s[0]};if(s.length===2&&!Array.isArray(c)&&(!i||i.length!==2||i[0]===0&&i[1]===1)){const[p,v]=s,g=p===v?void 0:(ln.mix||Qc)(p,v);return{calculatedDuration:t,next:x=>(d.value=g?g(c(t>0?Ut(0,1,x/t):1)):v,d.done=x>=t,d)}}const h=tb(i&&i.length===s.length?i:eb(s),t),f=Jw(h,s,{ease:Array.isArray(c)?c:nb(s,c)});return{calculatedDuration:t,next:p=>(d.value=f(p),d.done=p>=t,d)}}const sb=5;function rb(t,s,i){const o=Math.max(s-sb,0);return hp(i-t(o),s-o)}function ib(t,s,i=0){return s<=0?i:t.velocity?t.velocity(s):rb(o=>t.next(o).value,s,t.next(s).value)}const ab=t=>t!==null;function Da(t,{repeat:s,repeatType:i="loop"},o,c=1){const d=t.filter(ab),f=c<0||s&&i!=="loop"&&s%2===1?0:d.length-1;return!f||o===void 0?d[f]:o}const ob={decay:yc,inertia:yc,tween:Cr,keyframes:Cr,spring:wa};function Ip(t){typeof t.type=="string"&&(t.type=ob[t.type])}function Vp(t,s){return{kind:t,animation:s,timestamp:it.now(),frameTimestamp:$e.timestamp,frameIsProcessing:$e.isProcessing}}function Fp(t,s,i){const o=globalThis.__MOTION_INSPECT__;if(o)try{o({...Vp("animation-start",t),options:i?{...s,...i}:s})}catch{}}function lb(t,s){const i=globalThis.__MOTION_INSPECT__;if(i)try{i({...Vp("layout-animation-start",t),node:s})}catch{}}class eu{constructor(){this.isResolved=!1}get finished(){return this._finished||(this._finished=this.isResolved?Promise.resolve():new Promise(s=>{this._resolve=s})),this._finished}updateFinished(){this._finished=this._resolve=void 0,this.isResolved=!1}notifyFinished(){var s;this.isResolved=!0,(s=this._resolve)==null||s.call(this)}then(s,i){return this.finished.then(s,i)}}const cb=t=>t/100;class ba extends eu{constructor(s){super(),this.state="idle",this.startTime=null,this.isStopped=!1,this.currentTime=0,this.holdTime=null,this.playbackSpeed=1,this.delayState={done:!1,value:void 0},this.stop=()=>{var o,c;const{motionValue:i}=this.options;i&&i.updatedAt!==it.now()&&this.tick(it.now()),this.isStopped=!0,this.state!=="idle"&&(this.teardown(),(c=(o=this.options).onStop)==null||c.call(o))},this.options=s,this.initAnimation(),this.play(),s.autoplay===!1&&this.pause(),Fp(this,this.options)}initAnimation(){const{options:s}=this;Ip(s);const{type:i=Cr,repeat:o=0,repeatDelay:c=0,repeatType:d,velocity:h=0}=s;let{keyframes:f}=s;const p=i||Cr;p!==Cr&&typeof f[0]!="number"&&(this.mixKeyframes=Lr(cb,Qc(f[0],f[1])),f=[0,100]);const v=p(f===s.keyframes?s:{...s,keyframes:f});d==="mirror"&&(this.mirroredGenerator=p({...s,keyframes:[...f].reverse(),velocity:-h})),v.calculatedDuration===null&&(v.calculatedDuration=Zc(v));const{calculatedDuration:g}=v;this.calculatedDuration=g,this.resolvedDuration=g+c,this.totalDuration=this.resolvedDuration*(o+1)-c,this.generator=v}updateTime(s){const i=Math.round(s-this.startTime)*this.playbackSpeed;this.holdTime!==null?this.currentTime=this.holdTime:this.currentTime=i}tick(s,i=!1){const{generator:o,totalDuration:c,mixKeyframes:d,mirroredGenerator:h,resolvedDuration:f,calculatedDuration:p}=this;if(this.startTime===null)return o.next(0);const{delay:v=0,keyframes:g,repeat:x,repeatType:w,repeatDelay:k,type:S,onUpdate:j,finalKeyframe:N}=this.options;this.speed>0?this.startTime=Math.min(this.startTime,s):this.speed<0&&(this.startTime=Math.min(s-c/this.speed,this.startTime)),i?this.currentTime=s:this.updateTime(s);const B=this.currentTime-v*(this.playbackSpeed>=0?1:-1),M=this.playbackSpeed>=0?B<0:B>c;this.currentTime=Math.max(B,0),this.state==="finished"&&this.holdTime===null&&(this.currentTime=c);let L=this.currentTime,I=o;if(x){const O=Math.min(this.currentTime,c)/f;let oe=Math.floor(O),le=O%1;!le&&O>=1&&(le=1),le===1&&oe--,oe=Math.min(oe,x+1),!!(oe%2)&&(w==="reverse"?(le=1-le,k&&(le-=k/f)):w==="mirror"&&(I=h)),L=Ut(0,1,le)*f}let D;M?(this.delayState.value=g[0],D=this.delayState):D=I.next(L),d&&!M&&(D.value=d(D.value));let{done:F}=D;!M&&p!==null&&(F=this.playbackSpeed>=0?this.currentTime>=c:this.currentTime<=0);const V=this.holdTime===null&&(this.state==="finished"||this.state==="running"&&F);return V&&S!==yc&&(D.value=Da(g,this.options,N,this.speed)),j&&j(D.value),V&&this.finish(),D}then(s,i){return this.finished.then(s,i)}get duration(){return kt(this.calculatedDuration)}get iterationDuration(){const{delay:s=0}=this.options||{};return this.duration+kt(s)}get time(){return kt(this.currentTime)}set time(s){s=Mt(s),this.currentTime=s,this.startTime===null||this.holdTime!==null||this.playbackSpeed===0?this.holdTime=s:this.driver&&(this.startTime=this.driver.now()-s/this.playbackSpeed),this.driver?this.driver.start(!1):(this.startTime=0,this.state="paused",this.holdTime=s,this.tick(s))}getGeneratorVelocity(){return ib(this.generator,this.currentTime,this.options.velocity)}get speed(){return this.playbackSpeed}set speed(s){const i=this.playbackSpeed!==s;i&&this.driver&&this.updateTime(it.now()),this.playbackSpeed=s,i&&this.driver&&(this.time=kt(this.currentTime))}play(){var c,d;if(this.isStopped)return;const{driver:s=Hw,startTime:i}=this.options;this.driver||(this.driver=s(h=>this.tick(h))),(d=(c=this.options).onPlay)==null||d.call(c);const o=this.driver.now();this.state==="finished"?(this.updateFinished(),this.startTime=o):this.holdTime!==null?this.startTime=o-this.holdTime:this.startTime||(this.startTime=i??o),this.state==="finished"&&this.speed<0&&(this.startTime+=this.calculatedDuration),this.holdTime=null,this.state="running",this.driver.start()}pause(){this.state="paused",this.updateTime(it.now()),this.holdTime=this.currentTime}complete(){this.state!=="running"&&this.play(),this.state="finished",this.holdTime=null}finish(){var s,i;this.notifyFinished(),this.teardown(),this.state="finished",(i=(s=this.options).onComplete)==null||i.call(s)}cancel(){var s,i;this.holdTime=null,this.startTime=0,this.tick(0),this.teardown(),(i=(s=this.options).onCancel)==null||i.call(s)}teardown(){this.state="idle",this.stopDriver(),this.startTime=this.holdTime=null}stopDriver(){this.driver&&(this.driver.stop(),this.driver=void 0)}sample(s){return this.startTime=0,this.tick(s,!0)}attachTimeline(s){var i;return this.options.allowFlatten&&(this.options.type="keyframes",this.options.ease="linear",this.initAnimation()),(i=this.driver)==null||i.stop(),s.observe(this)}}const ub=new Set(["brightness","contrast","saturate","opacity"]);function db(t){const[s,i]=t.slice(0,-1).split("(");if(s==="drop-shadow")return t;const[o]=i.match(Xc)||[];if(!o)return t;const c=i.replace(o,"");let d=ub.has(s)?1:0;return o!==i&&(d*=100),s+"("+d+c+")"}const hb=/\b([a-z-]*)\(.*?\)/gu,vc={...jt,getAnimatableNone:t=>{const s=t.match(hb);return s?s.map(db).join(" "):t}},xc={...jt,getAnimatableNone:t=>{const s=jt.parse(t);return jt.createTransformer(t)(s.map(o=>typeof o=="number"?0:typeof o=="object"?{...o,alpha:1}:o))}},Bm={...Ls,transform:Math.round},mb={rotate:on,pathRotation:on,rotateX:on,rotateY:on,rotateZ:on,scale:Zi,scaleX:Zi,scaleY:Zi,scaleZ:Zi,skew:on,skewX:on,skewY:on,distance:Q,translateX:Q,translateY:Q,translateZ:Q,x:Q,y:Q,z:Q,perspective:Q,transformPerspective:Q,opacity:Mr,originX:Rm,originY:Rm,originZ:Q},ka={borderWidth:Q,borderTopWidth:Q,borderRightWidth:Q,borderBottomWidth:Q,borderLeftWidth:Q,borderRadius:Q,borderTopLeftRadius:Q,borderTopRightRadius:Q,borderBottomRightRadius:Q,borderBottomLeftRadius:Q,width:Q,maxWidth:Q,height:Q,maxHeight:Q,top:Q,right:Q,bottom:Q,left:Q,inset:Q,insetBlock:Q,insetBlockStart:Q,insetBlockEnd:Q,insetInline:Q,insetInlineStart:Q,insetInlineEnd:Q,padding:Q,paddingTop:Q,paddingRight:Q,paddingBottom:Q,paddingLeft:Q,paddingBlock:Q,paddingBlockStart:Q,paddingBlockEnd:Q,paddingInline:Q,paddingInlineStart:Q,paddingInlineEnd:Q,margin:Q,marginTop:Q,marginRight:Q,marginBottom:Q,marginLeft:Q,marginBlock:Q,marginBlockStart:Q,marginBlockEnd:Q,marginInline:Q,marginInlineStart:Q,marginInlineEnd:Q,fontSize:Q,backgroundPositionX:Q,backgroundPositionY:Q,...mb,zIndex:Bm,fillOpacity:Mr,strokeOpacity:Mr,numOctaves:Bm},fb={...ka,color:He,backgroundColor:He,outlineColor:He,fill:He,stroke:He,borderColor:He,borderTopColor:He,borderRightColor:He,borderBottomColor:He,borderLeftColor:He,filter:vc,WebkitFilter:vc,mask:xc,WebkitMask:xc},Bp=t=>fb[t],pb=new Set([vc,xc]);function tu(t,s){let i=Bp(t);return pb.has(i)||(i=jt),i.getAnimatableNone?i.getAnimatableNone(s):void 0}function gb(t){for(let s=1;s<t.length;s++)t[s]??(t[s]=t[s-1])}const Qn=t=>t*180/Math.PI,wc=t=>{const s=Qn(Math.atan2(t[1],t[0]));return bc(s)},yb={x:4,y:5,translateX:4,translateY:5,scaleX:0,scaleY:3,scale:t=>(Math.abs(t[0])+Math.abs(t[3]))/2,rotate:wc,rotateZ:wc,skewX:t=>Qn(Math.atan(t[1])),skewY:t=>Qn(Math.atan(t[2])),skew:t=>(Math.abs(t[1])+Math.abs(t[2]))/2},bc=t=>(t=t%360,t<0&&(t+=360),t),Om=wc,zm=t=>Math.sqrt(t[0]*t[0]+t[1]*t[1]),Um=t=>Math.sqrt(t[4]*t[4]+t[5]*t[5]),vb={x:12,y:13,z:14,translateX:12,translateY:13,translateZ:14,scaleX:zm,scaleY:Um,scale:t=>(zm(t)+Um(t))/2,rotateX:t=>bc(Qn(Math.atan2(t[6],t[5]))),rotateY:t=>bc(Qn(Math.atan2(-t[2],t[0]))),rotateZ:Om,rotate:Om,skewX:t=>Qn(Math.atan(t[4])),skewY:t=>Qn(Math.atan(t[1])),skew:t=>(Math.abs(t[1])+Math.abs(t[4]))/2};function kc(t){return t.includes("scale")?1:0}function jc(t,s){if(!t||t==="none")return kc(s);const i=t.match(/^matrix3d\(([-\d.e\s,]+)\)$/u);let o,c;if(i)o=vb,c=i;else{const f=t.match(/^matrix\(([-\d.e\s,]+)\)$/u);o=yb,c=f}if(!c)return kc(s);const d=o[s],h=c[1].split(",").map(wb);return typeof d=="function"?d(h):h[d]}const xb=(t,s)=>{const{transform:i="none"}=getComputedStyle(t);return jc(i,s)};function wb(t){return parseFloat(t.trim())}const Is=["transformPerspective","x","y","z","translateX","translateY","translateZ","scale","scaleX","scaleY","rotate","rotateX","rotateY","rotateZ","skew","skewX","skewY"],Vs=new Set([...Is,"pathRotation"]),Wm=t=>t===Ls||t===Q,bb=new Set(["x","y","z"]),kb=Is.filter(t=>!bb.has(t));function jb(t){const s=[];return kb.forEach(i=>{const o=t.getValue(i);if(o!==void 0){const c=o.get(),d=i.startsWith("scale")?1:0;if(c===d)return;s.push([i,c]),o.set(d)}}),s}const Sb=new Set(["bottom","right"]);function $m(t,s,i,o,c,d){const h=parseFloat(t);if(!isNaN(h))return h;const{min:f,max:p}=s()[i],v=p-f;return d==="border-box"?v:v-parseFloat(o)-parseFloat(c)}const Zn={width:({width:t,paddingLeft:s="0",paddingRight:i="0",boxSizing:o},c)=>$m(t,c,"x",s,i,o),height:({height:t,paddingTop:s="0",paddingBottom:i="0",boxSizing:o},c)=>$m(t,c,"y",s,i,o),top:({top:t})=>parseFloat(t),left:({left:t})=>parseFloat(t),bottom:({top:t},s)=>{const{y:i}=s();return parseFloat(t)+(i.max-i.min)},right:({left:t},s)=>{const{x:i}=s();return parseFloat(t)+(i.max-i.min)},x:({transform:t})=>jc(t,"x"),y:({transform:t})=>jc(t,"y")};Zn.translateX=Zn.x;Zn.translateY=Zn.y;const es=new Set;let Sc=!1,Nc=!1,Cc=!1;function Op(){if(Nc){const t=[],s=new Set,i=new Set;es.forEach(c=>{c.needsMeasurement&&(t.push(c),s.add(c.element),Sb.has(c.name)&&i.add(c.element))});const o=new Map;i.forEach(c=>{const d=jb(c);d.length&&(o.set(c,d),c.render())}),t.forEach(c=>c.measureInitialState()),s.forEach(c=>{c.render();const d=o.get(c);d&&d.forEach(([h,f])=>{var p;(p=c.getValue(h))==null||p.set(f)})}),t.forEach(c=>c.measureEndState()),t.forEach(c=>{c.suspendedScrollY!==void 0&&window.scrollTo(0,c.suspendedScrollY)})}Nc=!1,Sc=!1,es.forEach(t=>t.complete(Cc)),es.clear()}function zp(){es.forEach(t=>{t.readKeyframes(),t.needsMeasurement&&(Nc=!0)})}function Nb(){Cc=!0,zp(),Op(),Cc=!1}function Cb(t,s,i){if(typeof t=="string"){if(Wc(t)||$c(t))return parseFloat(t);if(!jt.test(t)&&jt.test(i))return tu(s,i)}return t??void 0}class nu{constructor(s,i,o,c,d,h=!1){this.state="pending",this.isAsync=!1,this.needsMeasurement=!1,this.unresolvedKeyframes=[...s],this.onComplete=i,this.name=o,this.motionValue=c,this.element=d,this.isAsync=h}scheduleResolve(){this.state="scheduled",this.isAsync?(es.add(this),Sc||(Sc=!0,je.read(zp),je.resolveKeyframes(Op))):(this.readKeyframes(),this.complete())}readKeyframes(){const{unresolvedKeyframes:s,name:i,element:o,motionValue:c}=this;if(s[0]===null){const d=c==null?void 0:c.get(),h=s[s.length-1];if(d!==void 0)s[0]=d;else if(o&&i){const f=Cb(o.readValue(i,h),i,h);f!==void 0&&(s[0]=f)}s[0]===void 0&&(s[0]=h),c&&d===void 0&&c.set(s[0])}gb(s)}setFinalKeyframe(){}measureInitialState(){}renderEndStyles(){}measureEndState(){}complete(s=!1){this.state="complete",this.onComplete(this.unresolvedKeyframes,this.finalKeyframe,s),es.delete(this)}cancel(){this.state==="scheduled"&&(es.delete(this),this.state="pending")}resume(){this.state==="pending"&&this.scheduleResolve()}}const Tb=t=>t.startsWith("--");function Up(t,s,i){Tb(s)?t.style.setProperty(s,i):t.style[s]=i}const Pb={};function Wp(t,s){const i=dp(t);return()=>Pb[s]??i()}const Eb=Wp(()=>window.ScrollTimeline!==void 0,"scrollTimeline"),$p=Wp(()=>{try{document.createElement("div").animate({opacity:0},{easing:"linear(0, 1)"})}catch{return!1}return!0},"linearEasing"),Nr=([t,s,i,o])=>`cubic-bezier(${t}, ${s}, ${i}, ${o})`,Hm={linear:"linear",ease:"ease",easeIn:"ease-in",easeOut:"ease-out",easeInOut:"ease-in-out",circIn:Nr([0,.65,.55,1]),circOut:Nr([.55,0,1,.45]),backIn:Nr([.31,.01,.66,-.59]),backOut:Nr([.33,1.53,.69,.99])};function Hp(t,s){if(t)return typeof t=="function"?$p()?Dp(t,s):"ease-out":kp(t)?Nr(t):Array.isArray(t)?t.map(i=>Hp(i,s)||Hm.easeOut):Hm[t]}function Mb(t,s,i,{delay:o=0,duration:c=300,repeat:d=0,repeatType:h="loop",ease:f="easeOut",times:p}={},v=void 0){const g={[s]:i};p&&(g.offset=p);const x=Hp(f,c);Array.isArray(x)&&(g.easing=x);const w={delay:o,duration:c,easing:Array.isArray(x)?"linear":x,fill:"both",iterations:d+1,direction:h==="reverse"?"alternate":"normal"};return v&&(w.pseudoElement=v),t.animate(g,w)}function Gp(t){return typeof t=="function"&&"applyToOptions"in t}function Ab({type:t,...s}){return Gp(t)&&$p()?t.applyToOptions(s):(s.duration??(s.duration=300),s.ease??(s.ease="easeOut"),s)}class Kp extends eu{constructor(s){if(super(),this.finishedTime=null,this.isStopped=!1,this.manualStartTime=null,!s)return;const{element:i,name:o,keyframes:c,pseudoElement:d,allowFlatten:h=!1,finalKeyframe:f,onComplete:p}=s;this.isPseudoElement=!!d,this.allowFlatten=h,this.options=s,_a(typeof s.type!="string");const v=Ab(s);this.animation=Mb(i,o,c,v,d),v.autoplay===!1&&this.animation.pause(),this.animation.onfinish=()=>{if(this.finishedTime=this.time,!d){const g=Da(c,this.options,f,this.speed);this.updateMotionValue&&this.updateMotionValue(g),Up(i,o,g),this.animation.cancel()}p==null||p(),this.notifyFinished()},Fp(this,s,v)}play(){this.isStopped||(this.manualStartTime=null,this.animation.play(),this.state==="finished"&&this.updateFinished())}pause(){this.animation.pause()}complete(){var s,i;(i=(s=this.animation).finish)==null||i.call(s)}cancel(){try{this.animation.cancel()}catch{}}stop(){if(this.isStopped)return;this.isStopped=!0;const{state:s}=this;s==="idle"||s==="finished"||(this.updateMotionValue?this.updateMotionValue():this.commitStyles(),this.isPseudoElement||this.cancel())}commitStyles(){var i,o,c;const s=(i=this.options)==null?void 0:i.element;!this.isPseudoElement&&(s!=null&&s.isConnected)&&((c=(o=this.animation).commitStyles)==null||c.call(o))}get duration(){var i,o;const s=((o=(i=this.animation.effect)==null?void 0:i.getComputedTiming)==null?void 0:o.call(i).duration)||0;return kt(Number(s))}get iterationDuration(){const{delay:s=0}=this.options||{};return this.duration+kt(s)}get time(){return kt(Number(this.animation.currentTime)||0)}set time(s){const i=this.finishedTime!==null;this.manualStartTime=null,this.finishedTime=null,this.animation.currentTime=Mt(s),i&&this.animation.pause()}get speed(){return this.animation.playbackRate}set speed(s){s<0&&(this.finishedTime=null),this.animation.playbackRate=s}get state(){return this.finishedTime!==null?"finished":this.animation.playState}get startTime(){return this.manualStartTime??Number(this.animation.startTime)}set startTime(s){this.manualStartTime=this.animation.startTime=s}attachTimeline({timeline:s,rangeStart:i,rangeEnd:o,observe:c}){var d;return this.allowFlatten&&((d=this.animation.effect)==null||d.updateTiming({easing:"linear"})),this.animation.onfinish=null,s&&Eb()?(this.animation.timeline=s,i&&(this.animation.rangeStart=i),o&&(this.animation.rangeEnd=o),Ot):c(this)}}const Xp={anticipate:vp,backInOut:yp,circInOut:wp};function _b(t){return t in Xp}function Db(t){typeof t.ease=="string"&&_b(t.ease)&&(t.ease=Xp[t.ease])}const Kl=10;class Rb extends Kp{constructor(s){Db(s),Ip(s),super(s),s.startTime!==void 0&&s.autoplay!==!1&&(this.startTime=s.startTime),this.options=s}updateMotionValue(s){const{motionValue:i,onUpdate:o,onComplete:c,element:d,...h}=this.options;if(!i)return;if(s!==void 0){i.set(s);return}const f=new ba({...h,autoplay:!1}),p=Math.max(Kl,it.now()-this.startTime),v=Ut(0,Kl,p-Kl),g=f.sample(p).value,{name:x}=this.options;d&&x&&Up(d,x,g),i.setWithVelocity(f.sample(Math.max(0,p-v)).value,g,v),f.stop()}}const Gm=(t,s)=>s==="zIndex"?!1:!!(typeof t=="number"||Array.isArray(t)||typeof t=="string"&&(jt.test(t)||t==="0")&&!t.startsWith("url("));function Lb(t){const s=t[0];if(t.length===1)return!0;for(let i=0;i<t.length;i++)if(t[i]!==s)return!0}function Ib(t,s,i,o){const c=t[0];if(c===null)return!1;if(s==="display"||s==="visibility")return!0;const d=t[t.length-1],h=Gm(c,s),f=Gm(d,s);return!h||!f?!1:Lb(t)||(i==="spring"||Gp(i))&&o}function Tc(t){t.duration=0,t.type="keyframes"}const Pc=new Set(["opacity","clipPath","filter","transform","backgroundColor"]),Vb=/^(?:oklch|oklab|lab|lch|color|color-mix|light-dark)\(/;function Fb(t){for(let s=0;s<t.length;s++)if(typeof t[s]=="string"&&Vb.test(t[s]))return!0;return!1}const Km=new Set(["color","backgroundColor","outlineColor","fill","stroke","borderColor","borderTopColor","borderRightColor","borderBottomColor","borderLeftColor"]),Bb=dp(()=>Object.hasOwnProperty.call(Element.prototype,"animate"));function Ob(t){var x;const{motionValue:s,name:i,repeatDelay:o,repeatType:c,damping:d,type:h,keyframes:f}=t;if(!i||!(Pc.has(i)||Km.has(i)))return!1;const p=(x=s==null?void 0:s.owner)==null?void 0:x.current;if(!(p instanceof HTMLElement)&&!(p instanceof SVGElement))return!1;const{onUpdate:v,transformTemplate:g}=s.owner.getProps();return Bb()&&(Pc.has(i)||Km.has(i)&&Fb(f))&&(i!=="transform"||!g)&&!v&&!o&&c!=="mirror"&&d!==0&&h!=="inertia"}const zb=40;class Ub extends eu{constructor(s){var p;super(),this.stop=()=>{var v,g;this._animation&&(this._animation.stop(),(v=this.stopTimeline)==null||v.call(this)),(g=this.keyframeResolver)==null||g.cancel()},this.createdAt=it.now();const{keyframes:i,name:o,motionValue:c,element:d}=s,h=s;h.autoplay??(h.autoplay=!0),h.delay??(h.delay=0),h.type??(h.type="keyframes"),h.repeat??(h.repeat=0),h.repeatDelay??(h.repeatDelay=0),h.repeatType??(h.repeatType="loop");const f=(d==null?void 0:d.KeyframeResolver)||nu;this.keyframeResolver=new f(i,(v,g,x)=>this.onKeyframesResolved(v,g,h,!x),o,c,d),(p=this.keyframeResolver)==null||p.scheduleResolve()}onKeyframesResolved(s,i,o,c){var N,B;this.keyframeResolver=void 0;const{name:d,type:h,velocity:f,delay:p,isHandoff:v,onUpdate:g}=o;this.resolvedAt=it.now();let x=!0;Ib(s,d,h,f)||(x=!1,(ln.instantAnimations||!p)&&(g==null||g(Da(s,o,i))),s[0]=s[s.length-1],Tc(o),o.repeat=0);const w=c?this.resolvedAt?this.resolvedAt-this.createdAt>zb?this.resolvedAt:this.createdAt:this.createdAt:void 0,{onComplete:k}=o;o.startTime??(o.startTime=w),o.finalKeyframe=i,o.keyframes=s,o.onComplete=()=>{k==null||k(),this.notifyFinished()};const S=x&&!v&&Ob(o);let j;if(S){o.element=(B=(N=o.motionValue)==null?void 0:N.owner)==null?void 0:B.current;try{j=new Rb(o)}catch{j=new ba(o)}}else j=new ba(o);this.pendingTimeline&&(this.stopTimeline=j.attachTimeline(this.pendingTimeline),this.pendingTimeline=void 0),this._animation=j}get finished(){return this._animation?this._animation.finished:super.finished}then(s,i){return this.finished.finally(s).then(()=>{})}get animation(){var s;return this._animation||((s=this.keyframeResolver)==null||s.resume(),Nb()),this._animation}get duration(){return this.animation.duration}get iterationDuration(){return this.animation.iterationDuration}get time(){return this.animation.time}set time(s){this.animation.time=s}get speed(){return this.animation.speed}get state(){return this.animation.state}set speed(s){this.animation.speed=s}get startTime(){return this.animation.startTime}attachTimeline(s){return this._animation?this.stopTimeline=this.animation.attachTimeline(s):this.pendingTimeline=s,()=>this.stop()}play(){this.animation.play()}pause(){this.animation.pause()}complete(){this.animation.complete()}cancel(){var s;this._animation&&this.animation.cancel(),(s=this.keyframeResolver)==null||s.cancel()}}function Yp(t,s,i,o=0,c=1){const d=Array.from(t).sort((v,g)=>v.sortNodePosition(g)).indexOf(s),h=t.size,f=(h-1)*o;return typeof i=="function"?i(d,h):c===1?d*o:f-d*o}const Xm=30,Wb=t=>!isNaN(parseFloat(t));class $b{constructor(s,i={}){this.canTrackVelocity=null,this.events={},this.updateAndNotify=o=>{const c=it.now();if(this.updatedAt!==c&&this.setPrevFrameValue(),this.prev=this.current,this.setCurrent(o),this.current!==this.prev&&(this.notifyChange(),this.dependents))for(const d of this.dependents)d.dirty()},this.hasAnimated=!1,this.setCurrent(s),this.owner=i.owner}setCurrent(s){this.current=s,this.updatedAt=it.now(),this.canTrackVelocity===null&&s!==void 0&&(this.canTrackVelocity=Wb(this.current))}setPrevFrameValue(s=this.current){this.prevFrameValue=s,this.prevUpdatedAt=this.updatedAt}onChange(s){return this.on("change",s)}on(s,i){var o;return s==="change"?this.onChangeSubscribe(i):((o=this.events)[s]||(o[s]=new ya)).add(i)}onChangeSubscribe(s){const{events:i}=this;return!i.change&&!this.changeSubscriber?this.changeSubscriber=s:(i.change||(i.change=new ya,i.change.add(this.changeSubscriber),this.changeSubscriber=void 0),i.change.add(s)),()=>{var o;this.changeSubscriber===s?this.changeSubscriber=void 0:(o=i.change)==null||o.remove(s),this.stopIfUnobserved()}}stopIfUnobserved(){je.read(()=>{var s;!this.changeSubscriber&&!((s=this.events.change)!=null&&s.getSize())&&this.stop()})}clearListeners(){this.changeSubscriber=void 0;for(const s in this.events)this.events[s].clear()}attach(s,i){this.passiveEffect=s,this.stopPassiveEffect=i}set(s){this.passiveEffect?this.passiveEffect(s,this.updateAndNotify):this.updateAndNotify(s)}setWithVelocity(s,i,o){this.set(i),this.prev=void 0,this.prevFrameValue=s,this.prevUpdatedAt=this.updatedAt-o}jump(s,i=!0){this.updateAndNotify(s),this.prev=s,this.prevUpdatedAt=this.prevFrameValue=void 0,i&&this.stop(),this.stopPassiveEffect&&this.stopPassiveEffect()}dirty(){this.notifyChange()}notifyChange(){var o;const{current:s,changeSubscriber:i}=this;i?i(s):(o=this.events.change)==null||o.notify(s)}addDependent(s){this.dependents||(this.dependents=new Set),this.dependents.add(s)}removeDependent(s){this.dependents&&this.dependents.delete(s)}get(){return this.current}getPrevious(){return this.prev}getVelocity(){const s=it.now();if(!this.canTrackVelocity||this.prevFrameValue===void 0||s-this.updatedAt>Xm)return 0;const i=Math.min(this.updatedAt-this.prevUpdatedAt,Xm);return hp(parseFloat(this.current)-parseFloat(this.prevFrameValue),i)}start(s){return this.stop(),new Promise(i=>{var d;this.hasAnimated=!0;let o=!1,c;c=s(()=>{var h;o=!0,(h=this.events.animationComplete)==null||h.notify(),this.animation===c&&this.clearAnimation(),i()}),o||(this.animation=c),(d=this.events.animationStart)==null||d.notify()})}stop(){this.animation&&(this.animation.stop(),this.events.animationCancel&&this.events.animationCancel.notify()),this.clearAnimation()}isAnimating(){return!!this.animation}clearAnimation(){this.animation=void 0}destroy(){var s,i;(s=this.dependents)==null||s.clear(),(i=this.events.destroy)==null||i.notify(),this.clearListeners(),this.stop(),this.stopPassiveEffect&&this.stopPassiveEffect()}}function Rs(t,s){return new $b(t,s)}function qp(t,s){if(t!=null&&t.inherit&&s){const{inherit:i,...o}=t;return{...s,...o}}return t}function su(t,s){const i=(t==null?void 0:t[s])??(t==null?void 0:t.default)??t;return i!==t?qp(i,t):i}const Hb={type:"spring",stiffness:500,damping:25,restSpeed:10},Gb=t=>({type:"spring",stiffness:550,damping:t===0?2*Math.sqrt(550):30,restSpeed:10}),Kb={type:"keyframes",duration:.8},Xb={type:"keyframes",ease:[.25,.1,.35,1],duration:.3},Yb=(t,{keyframes:s})=>s.length>2?Kb:Vs.has(t)?t.startsWith("scale")?Gb(s[1]):Hb:Xb,qb=new Set(["when","delay","delayChildren","staggerChildren","staggerDirection","repeat","repeatType","repeatDelay","from","elapsed"]);function Qb(t){for(const s in t)if(!qb.has(s))return!0;return!1}const ru=(t,s,i,o={},c,d)=>h=>{const f=su(o,t)||{},p=f.delay||o.delay||0;let{elapsed:v=0}=o;v=v-Mt(p);const g={keyframes:Array.isArray(i)?i:[null,i],ease:"easeOut",velocity:s.getVelocity(),...f,delay:-v,onUpdate:w=>{s.set(w),f.onUpdate&&f.onUpdate(w)},onComplete:()=>{h(),f.onComplete&&f.onComplete()},name:t,motionValue:s,element:d?void 0:c};Qb(f)||Object.assign(g,Yb(t,g)),g.duration&&(g.duration=Mt(g.duration)),g.repeatDelay&&(g.repeatDelay=Mt(g.repeatDelay)),g.from!==void 0&&(g.keyframes[0]=g.from);let x=!1;if((g.type===!1||g.duration===0&&!g.repeatDelay)&&(Tc(g),g.delay===0&&(x=!0)),(ln.instantAnimations||ln.skipAnimations||c!=null&&c.shouldSkipAnimations||f.skipAnimations)&&(x=!0,Tc(g),g.delay=0),g.allowFlatten=!f.type&&!f.ease,x&&!d&&s.get()!==void 0){const w=Da(g.keyframes,f);if(w!==void 0){je.update(()=>{g.onUpdate(w),g.onComplete()});return}}return f.isSync?new ba(g):new Ub(g)},Jb=/^var\(--(?:([\w-]+)|([\w-]+), ?([a-zA-Z\d ()%#.,-]+))\)/u;function Zb(t){const s=Jb.exec(t);if(!s)return[,];const[,i,o,c]=s;return[`--${i??o}`,c]}function Qp(t,s,i=1){const[o,c]=Zb(t);if(!o)return;const d=window.getComputedStyle(s).getPropertyValue(o);if(d){const h=d.trim();return Wc(h)?parseFloat(h):h}return Kc(c)?Qp(c,s,i+1):c}function Ym(t){const s=[{},{}];return t==null||t.values.forEach((i,o)=>{s[0][o]=i.get(),s[1][o]=i.getVelocity()}),s}function iu(t,s,i,o){if(typeof s=="function"){const[c,d]=Ym(o);s=s(i!==void 0?i:t.custom,c,d)}if(typeof s=="string"&&(s=t.variants&&t.variants[s]),typeof s=="function"){const[c,d]=Ym(o);s=s(i!==void 0?i:t.custom,c,d)}return s}function ts(t,s,i){const o=t.getProps();return iu(o,s,i!==void 0?i:o.custom,t)}const Jp=new Set(["width","height","top","left","right","bottom",...Is]),Ec=t=>Array.isArray(t);function e0(t,s,i){t.hasValue(s)?t.getValue(s).set(i):t.addValue(s,Rs(i))}function t0(t){return Ec(t)?t[t.length-1]||0:t}function n0(t,s){const i=ts(t,s);let{transitionEnd:o={},transition:c={},...d}=i||{};d={...d,...o};for(const h in d){const f=t0(d[h]);e0(t,h,f)}}const Ze=t=>!!(t&&t.getVelocity);function s0(t){return!!(Ze(t)&&t.add)}function Mc(t,s){const i=t.getValue("willChange");if(s0(i))return i.add(s);if(!i&&ln.WillChange){const o=new ln.WillChange("auto");t.addValue("willChange",o),o.add(s)}}function au(t){return t.replace(/([A-Z])/g,s=>`-${s.toLowerCase()}`)}const r0="framerAppearId",Zp="data-"+au(r0);function eg(t){return t.props[Zp]}const i0=typeof window<"u";function a0({protectedKeys:t,needsAnimating:s},i){const o=t.hasOwnProperty(i)&&s[i]!==!0;return s[i]=!1,o}function tg(t,s,{delay:i=0,transitionOverride:o,type:c}={}){let{transition:d,transitionEnd:h,...f}=s;const p=t.getDefaultTransition();d=d?qp(d,p):p;const v=d==null?void 0:d.reduceMotion,g=d==null?void 0:d.skipAnimations;o&&(d=o);const x=[],w=c&&t.animationState&&t.animationState.getState()[c],k=d==null?void 0:d.path;k&&k.animateVisualElement(t,f,d,i,x);for(const S in f){const j=t.getValue(S,t.latestValues[S]??null),N=f[S];if(N===void 0||w&&a0(w,S))continue;const B={delay:i,...su(d||{},S)};g&&(B.skipAnimations=!0);const M=j.get();if(M!==void 0&&!j.isAnimating()&&!Array.isArray(N)&&N===M&&!B.velocity){je.update(()=>j.set(N));continue}let L=!1;if(i0&&window.MotionHandoffAnimation){const F=eg(t);if(F){const V=window.MotionHandoffAnimation(F,S,je);V!==null&&(B.startTime=V,L=!0)}}Mc(t,S);const I=v??t.shouldReduceMotion;j.start(ru(S,j,N,I&&Jp.has(S)?{type:!1}:B,t,L));const D=j.animation;D&&x.push(D)}if(h){const S=()=>je.update(()=>{h&&n0(t,h)});x.length?Promise.all(x).then(S):S()}return x}function Ac(t,s,i={}){var p;const o=ts(t,s,i.type==="exit"?(p=t.presenceContext)==null?void 0:p.custom:void 0);let{transition:c=t.getDefaultTransition()||{}}=o||{};i.transitionOverride&&(c=i.transitionOverride);const d=o?()=>Promise.all(tg(t,o,i)):()=>Promise.resolve(),h=t.variantChildren&&t.variantChildren.size?(v=0)=>{const{delayChildren:g=0,staggerChildren:x,staggerDirection:w}=c;return o0(t,s,v,g,x,w,i)}:()=>Promise.resolve(),{when:f}=c;if(f){const[v,g]=f==="beforeChildren"?[d,h]:[h,d];return v().then(()=>g())}else return Promise.all([d(),h(i.delay)])}function o0(t,s,i=0,o=0,c=0,d=1,h){const f=[];for(const p of t.variantChildren)p.notify("AnimationStart",s),f.push(Ac(p,s,{...h,delay:i+(typeof o=="function"?0:o)+Yp(t.variantChildren,p,o,c,d)}).then(()=>p.notify("AnimationComplete",s)));return Promise.all(f)}function l0(t,s,i={}){t.notify("AnimationStart",s);let o;if(Array.isArray(s)){const c=s.map(d=>Ac(t,d,i));o=Promise.all(c)}else if(typeof s=="string")o=Ac(t,s,i);else{const c=typeof s=="function"?ts(t,s,i.custom):s;o=Promise.all(tg(t,c,i))}return o.then(()=>{t.notify("AnimationComplete",s)})}const c0={test:t=>t==="auto",parse:t=>t},u0=t=>s=>s.test(t),d0=[Ls,Q,Qt,on,Sw,jw,c0],qm=t=>d0.find(u0(t));function h0(t){return typeof t=="number"?t===0:t!==null?t==="none"||t==="0"||$c(t):!0}const m0=new Set(["auto","none","0"]);function f0(t,s,i){let o=0,c;for(;o<t.length&&!c;){const d=t[o];typeof d=="string"&&!m0.has(d)&&Mw(d)&&(c=t[o]),o++}if(c&&i)for(const d of s)t[d]!==c&&(t[d]=tu(i,c))}class p0 extends nu{constructor(s,i,o,c,d){super(s,i,o,c,d,!0)}readKeyframes(){const{unresolvedKeyframes:s,element:i,name:o}=this;if(!i||!i.current)return;super.readKeyframes();for(let g=0;g<s.length;g++){let x=s[g];if(typeof x=="string"&&(x=x.trim(),Kc(x))){const w=Qp(x,i.current);w!==void 0&&(s[g]=w),g===s.length-1&&(this.finalKeyframe=x)}}if(this.resolveNoneKeyframes(),!Jp.has(o)||s.length!==2)return;const[c,d]=s;if(typeof c=="number"&&typeof d=="number")return;const h=qm(c),f=qm(d),p=Dm(c),v=Dm(d);if(p!==v&&Zn[o]){this.needsMeasurement=!0;return}if(h!==f)if(Wm(h)&&Wm(f))for(let g=0;g<s.length;g++){const x=s[g];typeof x=="string"&&(s[g]=parseFloat(x))}else Zn[o]&&(this.needsMeasurement=!0)}resolveNoneKeyframes(){const{unresolvedKeyframes:s,name:i}=this,o=[];for(let c=0;c<s.length;c++)(s[c]===null||h0(s[c]))&&o.push(c);o.length&&f0(s,o,i)}measure(){const{element:s,name:i}=this;return Zn[i](window.getComputedStyle(s.current),()=>s.measureViewportBox())}measureInitialState(){var d;const{element:s,unresolvedKeyframes:i,name:o}=this;if(!s||!s.current)return;o==="height"&&(this.suspendedScrollY=window.pageYOffset),this.measuredOrigin=this.measure(),i[0]=this.measuredOrigin;const c=i[i.length-1];c!==void 0&&((d=this.motionValue)==null||d.jump(c,!1))}measureEndState(){var d,h;const{element:s,unresolvedKeyframes:i}=this;if(!s||!s.current)return;(d=this.motionValue)==null||d.jump(this.measuredOrigin,!1);const o=i.length-1,c=i[o];i[o]=this.measure(),c!==null&&this.finalKeyframe===void 0&&(this.finalKeyframe=c),(h=this.removedTransforms)!=null&&h.length&&this.removedTransforms.forEach(([f,p])=>{s.getValue(f).set(p)}),this.resolveNoneKeyframes()}}const ou=["borderTopLeftRadius","borderTopRightRadius","borderBottomRightRadius","borderBottomLeftRadius"];function g0(t){return up(t)&&"offsetHeight"in t&&!("ownerSVGElement"in t)}function lu(t){return up(t)&&"ownerSVGElement"in t}const _c=(t,s)=>s&&typeof t=="number"?s.transform(t):t;function ng(t,s,i){if(t==null)return[];if(t instanceof EventTarget)return[t];if(typeof t=="string"){let o=document;const c=(i==null?void 0:i[t])??o.querySelectorAll(t);return c?Array.from(c):[]}return Array.from(t).filter(o=>o!=null)}const y0={x:"translateX",y:"translateY",z:"translateZ",transformPerspective:"perspective"},v0=Is.length;function x0(t,s,i){let o="",c=!0;for(let h=0;h<v0;h++){const f=Is[h],p=t[f];if(p===void 0)continue;let v=!0;if(typeof p=="number")v=p===(f.startsWith("scale")?1:0);else{const g=parseFloat(p);v=f.startsWith("scale")?g===1:g===0}if(!v||i){const g=_c(p,ka[f]);if(!v){c=!1;const x=y0[f]||f;o+=`${x}(${g}) `}i&&(s[f]=g)}}const d=t.pathRotation;return d&&(c=!1,o+=`rotate(${_c(d,ka.pathRotation)}) `),o=o.trim(),i?o=i(s,c?"":o):c&&(o="none"),o}function cu(t,s,i){const{style:o,vars:c,transformOrigin:d}=t;let h=!1,f=!1;for(const p in s){const v=s[p];if(Vs.has(p)){h=!0;continue}else if(Np(p)){c[p]=v;continue}else{const g=_c(v,ka[p]);p.startsWith("origin")?(f=!0,d[p]=g):o[p]=g}}if(s.transform||(h||i?o.transform=x0(s,t.transform,i):o.transform&&(o.transform="none")),f){const{originX:p="50%",originY:v="50%",originZ:g=0}=d;o.transformOrigin=`${p} ${v} ${g}`}}const w0={offset:"stroke-dashoffset",array:"stroke-dasharray"},b0={offset:"strokeDashoffset",array:"strokeDasharray"};function k0(t,s,i=1,o=0,c=!0){t.pathLength=1;const d=c?w0:b0;t[d.offset]=`${-o}`,t[d.array]=`${s} ${i}`}const sg=["transform","opacity","offsetDistance","offsetPath","offsetRotate","offsetAnchor"];function rg(t,{attrX:s,attrY:i,attrScale:o,pathLength:c,pathSpacing:d=1,pathOffset:h=0,...f},p,v,g){if(cu(t,f,v),p){t.style.viewBox&&(t.attrs.viewBox=t.style.viewBox);return}t.attrs=t.style,t.style={};const{attrs:x,style:w}=t;for(const k of sg)x[k]!==void 0&&(w[k]=x[k],delete x[k]);(w.transform||x.transformOrigin)&&(w.transformOrigin=x.transformOrigin??"50% 50%",delete x.transformOrigin),w.transform&&(w.transformBox=(g==null?void 0:g.transformBox)??"fill-box",delete x.transformBox),s!==void 0&&(x.x=s),i!==void 0&&(x.y=i),o!==void 0&&(x.scale=o),c!==void 0&&k0(x,c,d,h,!1)}function ig({top:t,left:s,right:i,bottom:o}){return{x:{min:s,max:i},y:{min:t,max:o}}}function j0({x:t,y:s}){return{top:s.min,right:t.max,bottom:s.max,left:t.min}}function S0(t,s){if(!s)return t;const i=s({x:t.left,y:t.top}),o=s({x:t.right,y:t.bottom});return{top:i.y,left:i.x,bottom:o.y,right:o.x}}function Xl(t){return t===void 0||t===1}function Dc({scale:t,scaleX:s,scaleY:i}){return!Xl(t)||!Xl(s)||!Xl(i)}function Kn(t){return Dc(t)||ag(t)||t.z||t.rotate||t.rotateX||t.rotateY||t.skewX||t.skewY}function ag(t){return Qm(t.x)||Qm(t.y)}function Qm(t){return t&&t!=="0%"}function ja(t,s,i){const o=t-i,c=s*o;return i+c}function Jm(t,s,i,o,c){return c!==void 0&&(t=ja(t,c,o)),ja(t,i,o)+s}function Rc(t,s=0,i=1,o,c){t.min=Jm(t.min,s,i,o,c),t.max=Jm(t.max,s,i,o,c)}function og(t,{x:s,y:i}){Rc(t.x,s.translate,s.scale,s.originPoint),Rc(t.y,i.translate,i.scale,i.originPoint)}const Zm=.999999999999,ef=1.0000000000001;function N0(t,s,i,o=!1){var f;const c=i.length;if(!c)return;s.x=s.y=1;let d,h;for(let p=0;p<c;p++){d=i[p],h=d.projectionDelta;const{visualElement:v}=d.options;v&&v.props.style&&v.props.style.display==="contents"||(o&&d.options.layoutScroll&&d.scroll&&d!==d.root&&(Yt(t.x,-d.scroll.offset.x),Yt(t.y,-d.scroll.offset.y)),h&&(s.x*=h.x.scale,s.y*=h.y.scale,og(t,h)),o&&Kn(d.latestValues)&&oa(t,d.latestValues,(f=d.layout)==null?void 0:f.layoutBox))}s.x<ef&&s.x>Zm&&(s.x=1),s.y<ef&&s.y>Zm&&(s.y=1)}function Yt(t,s){t.min+=s,t.max+=s}function tf(t,s,i,o,c=.5){const d=ke(t.min,t.max,c);Rc(t,s,i,d,o)}function nf(t,s){return typeof t=="string"?parseFloat(t)/100*(s.max-s.min):t}function oa(t,s,i){const o=i??t;tf(t.x,nf(s.x,o.x),s.scaleX,s.scale,s.originX),tf(t.y,nf(s.y,o.y),s.scaleY,s.scale,s.originY)}function lg(t,s){return ig(S0(t.getBoundingClientRect(),s))}function C0(t,s,i){const o=lg(t,i),{scroll:c}=s;return c&&(Yt(o.x,c.offset.x),Yt(o.y,c.offset.y)),o}const{schedule:uu}=jp(queueMicrotask,!1),Bt={x:!1,y:!1};function cg(){return Bt.x||Bt.y}function T0(t){return t==="x"||t==="y"?Bt[t]?null:(Bt[t]=!0,()=>{Bt[t]=!1}):Bt.x||Bt.y?null:(Bt.x=Bt.y=!0,()=>{Bt.x=Bt.y=!1})}function ug(t,s){const i=ng(t),o=new AbortController,c={passive:!0,...s,signal:o.signal};return[i,c,()=>o.abort()]}function P0(t){return!(t.pointerType==="touch"||cg())}function E0(t,s,i={}){const[o,c,d]=ug(t,i);return o.forEach(h=>{let f=!1,p=!1,v;const g=()=>{h.removeEventListener("pointerleave",S)},x=N=>{v&&(v(N),v=void 0),g()},w=N=>{f=!1,window.removeEventListener("pointerup",w),window.removeEventListener("pointercancel",w),p&&(p=!1,x(N))},k=()=>{f=!0,window.addEventListener("pointerup",w,c),window.addEventListener("pointercancel",w,c)},S=N=>{if(N.pointerType!=="touch"){if(f){p=!0;return}x(N)}},j=N=>{if(!P0(N))return;p=!1;const B=s(h,N);typeof B=="function"&&(v=B,h.addEventListener("pointerleave",S,c))};h.addEventListener("pointerenter",j,c),h.addEventListener("pointerdown",k,c)}),d}const dg=(t,s)=>s?t===s?!0:dg(t,s.parentElement):!1,du=t=>t.pointerType==="mouse"?typeof t.button!="number"||t.button<=0:t.isPrimary!==!1,M0=new Set(["BUTTON","INPUT","SELECT","TEXTAREA","A"]);function A0(t){return M0.has(t.tagName)||t.isContentEditable===!0}const _0=new Set(["INPUT","SELECT","TEXTAREA"]);function D0(t){return _0.has(t.tagName)||t.isContentEditable===!0}const la=new WeakSet;function sf(t){return s=>{s.key==="Enter"&&t(s)}}function Yl(t,s){t.dispatchEvent(new PointerEvent("pointer"+s,{isPrimary:!0,bubbles:!0}))}const R0=(t,s)=>{const i=t.currentTarget;if(!i)return;const o=sf(()=>{if(la.has(i))return;Yl(i,"down");const c=sf(()=>{Yl(i,"up")}),d=()=>Yl(i,"cancel");i.addEventListener("keyup",c,s),i.addEventListener("blur",d,s)});i.addEventListener("keydown",o,s),i.addEventListener("blur",()=>i.removeEventListener("keydown",o),s)};function rf(t){return du(t)&&!cg()}const af=new WeakSet;function L0(t,s,i={}){const[o,c,d]=ug(t,i),h=f=>{const p=f.currentTarget;if(!rf(f)||af.has(f))return;la.add(p),i.stopPropagation&&af.add(f);const v=s(p,f),g={...c,capture:!0},x=(S,j)=>{window.removeEventListener("pointerup",w,g),window.removeEventListener("pointercancel",k,g),la.has(p)&&la.delete(p),rf(S)&&typeof v=="function"&&v(S,{success:j})},w=S=>{x(S,p===window||p===document||i.useGlobalTarget||dg(p,S.target))},k=S=>{x(S,!1)};window.addEventListener("pointerup",w,g),window.addEventListener("pointercancel",k,g)};return o.forEach(f=>{(i.useGlobalTarget?window:f).addEventListener("pointerdown",h,c),g0(f)&&(f.addEventListener("focus",v=>R0(v,c)),!A0(f)&&!f.hasAttribute("tabindex")&&(f.tabIndex=0))}),d}const ca=new WeakMap;let Pn;const hg=(t,s,i)=>(o,c)=>c&&c[0]?c[0][t+"Size"]:lu(o)&&"getBBox"in o?o.getBBox()[s]:o[i],I0=hg("inline","width","offsetWidth"),V0=hg("block","height","offsetHeight");function F0({target:t,borderBoxSize:s}){var i;(i=ca.get(t))==null||i.forEach(o=>{o(t,{get width(){return I0(t,s)},get height(){return V0(t,s)}})})}function B0(t){t.forEach(F0)}function O0(){typeof ResizeObserver>"u"||(Pn=new ResizeObserver(B0))}function z0(t,s){Pn||O0();const i=ng(t);return i.forEach(o=>{let c=ca.get(o);c||(c=new Set,ca.set(o,c)),c.add(s),Pn==null||Pn.observe(o)}),()=>{i.forEach(o=>{const c=ca.get(o);c==null||c.delete(s),c!=null&&c.size||Pn==null||Pn.unobserve(o)})}}const ua=new Set;let As;function U0(){As=()=>{const t={get width(){return window.innerWidth},get height(){return window.innerHeight}};ua.forEach(s=>s(t))},window.addEventListener("resize",As)}function W0(t){return ua.add(t),As||U0(),()=>{ua.delete(t),!ua.size&&typeof As=="function"&&(window.removeEventListener("resize",As),As=void 0)}}function of(t,s){return typeof t=="function"?W0(t):z0(t,s)}function $0(t){return lu(t)&&t.tagName==="svg"}const lf=()=>({translate:0,scale:1,origin:0,originPoint:0}),_s=()=>({x:lf(),y:lf()}),cf=()=>({min:0,max:0}),We=()=>({x:cf(),y:cf()}),H0=new WeakMap;function Ra(t){return t!==null&&typeof t=="object"&&typeof t.start=="function"}function _r(t){return typeof t=="string"||Array.isArray(t)}const hu=["animate","whileInView","whileFocus","whileHover","whileTap","whileDrag","exit"],Sa=["initial",...hu];function La(t){if(Ra(t.animate))return!0;for(let s=0;s<Sa.length;s++)if(_r(t[Sa[s]]))return!0;return!1}function mg(t){return!!(La(t)||t.variants)}function G0(t,s,i){for(const o in s){const c=s[o],d=i[o];if(Ze(c))t.addValue(o,c);else if(Ze(d))t.addValue(o,Rs(c,{owner:t}));else if(d!==c)if(t.hasValue(o)){const h=t.getValue(o);h.liveStyle===!0?h.jump(c):h.hasAnimated||h.set(c)}else{const h=t.getStaticValue(o);t.addValue(o,Rs(h!==void 0?h:c,{owner:t}))}}for(const o in i)s[o]===void 0&&t.removeValue(o);return s}const Na={current:null},mu={current:!1},K0=typeof window<"u";function fg(){if(mu.current=!0,!!K0)if(window.matchMedia){const t=window.matchMedia("(prefers-reduced-motion)"),s=()=>Na.current=t.matches;t.addEventListener("change",s),s()}else Na.current=!1}const uf=["AnimationStart","AnimationComplete","Update","BeforeLayoutMeasure","LayoutMeasure","LayoutAnimationStart","LayoutAnimationComplete"];let Ca={};function pg(t){Ca=t}function X0(){return Ca}class Y0{scrapeMotionValuesFromProps(s,i,o){return{}}constructor({parent:s,props:i,presenceContext:o,reducedMotionConfig:c,skipAnimations:d,blockInitialAnimation:h,visualState:f},p={}){this.current=null,this.children=new Set,this.isVariantNode=!1,this.isControllingVariants=!1,this.shouldReduceMotion=null,this.shouldSkipAnimations=!1,this.values=new Map,this.KeyframeResolver=nu,this.features={},this.valueSubscriptions=new Map,this.prevMotionValues={},this.hasBeenMounted=!1,this.events={},this.propEventSubscriptions={},this.notifyUpdate=()=>this.notify("Update",this.latestValues),this.render=()=>{this.current&&(this.triggerBuild(),this.renderInstance(this.current,this.renderState,this.props.style,this.projection))},this.renderScheduledAt=0,this.scheduleRender=()=>{const k=it.now();this.renderScheduledAt<k&&(this.renderScheduledAt=k,je.render(this.render,!1,!0))};const{latestValues:v,renderState:g}=f;this.latestValues=v,this.baseTarget={...v},this.initialValues=i.initial?{...v}:{},this.renderState=g,this.parent=s,this.props=i,this.presenceContext=o,this.depth=s?s.depth+1:0,this.reducedMotionConfig=c,this.skipAnimationsConfig=d,this.options=p,this.blockInitialAnimation=!!h,this.isControllingVariants=La(i),this.isVariantNode=mg(i),this.isVariantNode&&(this.variantChildren=new Set),this.manuallyAnimateOnMount=!!(s&&s.current);const{willChange:x,...w}=this.scrapeMotionValuesFromProps(i,{},this);for(const k in w){const S=w[k];v[k]!==void 0&&Ze(S)&&S.set(v[k])}}mount(s){var i,o;if(this.hasBeenMounted)for(const c in this.initialValues)(i=this.values.get(c))==null||i.jump(this.initialValues[c]),this.latestValues[c]=this.initialValues[c];this.current=s,H0.set(s,this),this.projection&&!this.projection.instance&&this.projection.mount(s),this.parent&&this.isVariantNode&&!this.isControllingVariants&&(this.removeFromVariantTree=this.parent.addVariantChild(this)),this.values.forEach((c,d)=>this.bindToMotionValue(d,c)),this.reducedMotionConfig==="never"?this.shouldReduceMotion=!1:this.reducedMotionConfig==="always"?this.shouldReduceMotion=!0:(mu.current||fg(),this.shouldReduceMotion=Na.current),this.shouldSkipAnimations=this.skipAnimationsConfig??!1,(o=this.parent)==null||o.addChild(this),this.update(this.props,this.presenceContext),this.hasBeenMounted=!0}unmount(){var s;this.projection&&this.projection.unmount(),Mn(this.notifyUpdate),Mn(this.render),this.valueSubscriptions.forEach(i=>i()),this.valueSubscriptions.clear(),this.removeFromVariantTree&&this.removeFromVariantTree(),(s=this.parent)==null||s.removeChild(this);for(const i in this.events)this.events[i].clear();for(const i in this.features){const o=this.features[i];o&&(o.unmount(),o.isMounted=!1)}this.current=null}addChild(s){this.children.add(s),this.enteringChildren??(this.enteringChildren=new Set),this.enteringChildren.add(s)}removeChild(s){this.children.delete(s),this.enteringChildren&&this.enteringChildren.delete(s)}bindToMotionValue(s,i){if(this.valueSubscriptions.has(s)&&this.valueSubscriptions.get(s)(),i.accelerate&&Pc.has(s)&&this.current instanceof HTMLElement){const{factory:h,keyframes:f,times:p,ease:v,duration:g}=i.accelerate,x=new Kp({element:this.current,name:s,keyframes:f,times:p,ease:v,duration:Mt(g)}),w=h(x);this.valueSubscriptions.set(s,()=>{w(),x.cancel()});return}const o=Vs.has(s);o&&this.onBindTransform&&this.onBindTransform();const c=i.on("change",h=>{this.latestValues[s]=h,this.props.onUpdate&&je.preRender(this.notifyUpdate),o&&this.projection&&(this.projection.isTransformDirty=!0),this.scheduleRender()});let d;typeof window<"u"&&window.MotionCheckAppearSync&&(d=window.MotionCheckAppearSync(this,s,i)),this.valueSubscriptions.set(s,()=>{c(),d&&d()})}sortNodePosition(s){return!this.current||!this.sortInstanceNodePosition||this.type!==s.type?0:this.sortInstanceNodePosition(this.current,s.current)}updateFeatures(){let s="animation";for(s in Ca){const i=Ca[s];if(!i)continue;const{isEnabled:o,Feature:c}=i;if(!this.features[s]&&c&&o(this.props)&&(this.features[s]=new c(this)),this.features[s]){const d=this.features[s];d.isMounted?d.update():(d.mount(),d.isMounted=!0)}}}triggerBuild(){this.build(this.renderState,this.latestValues,this.props)}measureViewportBox(){return this.current?this.measureInstanceViewportBox(this.current,this.props):We()}getStaticValue(s){return this.latestValues[s]}setStaticValue(s,i){this.latestValues[s]=i}update(s,i){(s.transformTemplate||this.props.transformTemplate)&&this.scheduleRender(),this.prevProps=this.props,this.props=s,this.prevPresenceContext=this.presenceContext,this.presenceContext=i;for(let o=0;o<uf.length;o++){const c=uf[o];this.propEventSubscriptions[c]&&(this.propEventSubscriptions[c](),delete this.propEventSubscriptions[c]);const d="on"+c,h=s[d];h&&(this.propEventSubscriptions[c]=this.on(c,h))}this.prevMotionValues=G0(this,this.scrapeMotionValuesFromProps(s,this.prevProps||{},this),this.prevMotionValues),this.handleChildMotionValue&&this.handleChildMotionValue()}getProps(){return this.props}getVariant(s){return this.props.variants?this.props.variants[s]:void 0}getDefaultTransition(){return this.props.transition}getTransformPagePoint(){return this.props.transformPagePoint}getClosestVariantNode(){return this.isVariantNode?this:this.parent?this.parent.getClosestVariantNode():void 0}addVariantChild(s){const i=this.getClosestVariantNode();if(i)return i.variantChildren&&i.variantChildren.add(s),()=>i.variantChildren.delete(s)}addValue(s,i){const o=this.values.get(s);i!==o&&(o&&this.removeValue(s),this.bindToMotionValue(s,i),this.values.set(s,i),this.latestValues[s]=i.get())}removeValue(s){this.values.delete(s);const i=this.valueSubscriptions.get(s);i&&(i(),this.valueSubscriptions.delete(s)),delete this.latestValues[s],this.removeValueFromRenderState(s,this.renderState)}hasValue(s){return this.values.has(s)}getValue(s,i){if(this.props.values&&this.props.values[s])return this.props.values[s];let o=this.values.get(s);return o===void 0&&i!==void 0&&(o=Rs(i===null?void 0:i,{owner:this}),this.addValue(s,o)),o}readValue(s,i){let o=this.latestValues[s]!==void 0||!this.current?this.latestValues[s]:this.getBaseTargetFromProps(this.props,s)??this.readValueFromInstance(this.current,s,this.options);return o!=null&&(typeof o=="string"&&(Wc(o)||$c(o))?o=parseFloat(o):typeof o!="number"&&!jt.test(o)&&jt.test(i)&&(o=tu(s,i)),this.setBaseTarget(s,Ze(o)?o.get():o)),Ze(o)?o.get():o}setBaseTarget(s,i){this.baseTarget[s]=i}getBaseTarget(s){var d;const{initial:i}=this.props;let o;if(typeof i=="string"||typeof i=="object"){const h=iu(this.props,i,(d=this.presenceContext)==null?void 0:d.custom);h&&(o=h[s])}if(i&&o!==void 0)return o;const c=this.getBaseTargetFromProps(this.props,s);return c!==void 0&&!Ze(c)?c:this.initialValues[s]!==void 0&&o===void 0?void 0:this.baseTarget[s]}on(s,i){return this.events[s]||(this.events[s]=new ya),this.events[s].add(i)}notify(s,...i){this.events[s]&&this.events[s].notify(...i)}scheduleRenderMicrotask(){uu.render(this.render)}}class gg extends Y0{constructor(){super(...arguments),this.KeyframeResolver=p0}sortInstanceNodePosition(s,i){return s.compareDocumentPosition(i)&2?1:-1}getBaseTargetFromProps(s,i){const o=s.style;return o?o[i]:void 0}removeValueFromRenderState(s,{vars:i,style:o}){delete i[s],delete o[s]}handleChildMotionValue(){this.childSubscription&&(this.childSubscription(),delete this.childSubscription);const{children:s}=this.props;Ze(s)&&(this.childSubscription=s.on("change",i=>{this.current&&(this.current.textContent=`${i}`)}))}}class An{constructor(s){this.isMounted=!1,this.node=s}update(){}}function yg(t,{style:s,vars:i},o,c){const d=t.style;let h;for(h in s)d[h]=s[h];c==null||c.applyProjectionStyles(d,o);for(h in i)d.setProperty(h,i[h])}function df(t,s){return s.max===s.min?0:t/(s.max-s.min)*100}const Sr={correct:(t,s)=>{if(!s.target)return t;if(typeof t=="string")if(Q.test(t))t=parseFloat(t);else return t;const i=df(t,s.target.x),o=df(t,s.target.y);return`${i}% ${o}%`}},q0={correct:(t,{treeScale:s,projectionDelta:i})=>{const o=t,c=jt.parse(t);if(c.length>5)return o;const d=jt.createTransformer(t),h=typeof c[0]!="number"?1:0,f=i.x.scale*s.x,p=i.y.scale*s.y;c[0+h]/=f,c[1+h]/=p;const v=ke(f,p,.5);return typeof c[2+h]=="number"&&(c[2+h]/=v),typeof c[3+h]=="number"&&(c[3+h]/=v),d(c)}},Lc={borderRadius:{...Sr,applyTo:[...ou]},borderTopLeftRadius:Sr,borderTopRightRadius:Sr,borderBottomLeftRadius:Sr,borderBottomRightRadius:Sr,boxShadow:q0};function vg(t,{layout:s,layoutId:i}){return Vs.has(t)||t.startsWith("origin")||(s||i!==void 0)&&(!!Lc[t]||t==="opacity")}function fu(t,s,i){var h;const o=t.style,c=s==null?void 0:s.style,d={};if(!o)return d;for(const f in o)(Ze(o[f])||c&&Ze(c[f])||vg(f,t)||((h=i==null?void 0:i.getValue(f))==null?void 0:h.liveStyle)!==void 0)&&(d[f]=o[f]);return d}function Q0(t){return window.getComputedStyle(t)}class J0 extends gg{constructor(){super(...arguments),this.type="html",this.renderInstance=yg}mount(s){_a(!!s.style),super.mount(s)}readValueFromInstance(s,i){var o;if(Vs.has(i))return(o=this.projection)!=null&&o.isProjecting?kc(i):xb(s,i);{const c=Q0(s),d=(Np(i)?c.getPropertyValue(i):c[i])||0;return typeof d=="string"?d.trim():d}}measureInstanceViewportBox(s,{transformPagePoint:i}){return lg(s,i)}build(s,i,o){cu(s,i,o.transformTemplate)}scrapeMotionValuesFromProps(s,i,o){return fu(s,i,o)}}const xg=new Set(["baseFrequency","diffuseConstant","kernelMatrix","kernelUnitLength","keySplines","keyTimes","limitingConeAngle","markerHeight","markerWidth","numOctaves","targetX","targetY","surfaceScale","specularConstant","specularExponent","stdDeviation","tableValues","viewBox","gradientTransform","pathLength","startOffset","textLength","lengthAdjust"]),wg=t=>typeof t=="string"&&t.toLowerCase()==="svg";function Z0(t,s,i,o){yg(t,s,void 0,o);for(const c in s.attrs)t.setAttribute(xg.has(c)?c:au(c),s.attrs[c])}function bg(t,s,i){const o=fu(t,s,i);for(const c in t)if(Ze(t[c])||Ze(s[c])){const d=Is.indexOf(c)!==-1?"attr"+c.charAt(0).toUpperCase()+c.substring(1):c;o[d]=t[c]}return o}class ek extends gg{constructor(){super(...arguments),this.type="svg",this.isSVGTag=!1,this.measureInstanceViewportBox=We}getBaseTargetFromProps(s,i){return s[i]}readValueFromInstance(s,i){if(Vs.has(i)){const o=Bp(i);return o&&o.default||0}if(sg.includes(i)){const c=getComputedStyle(s)[i];if(typeof c=="string"&&c)return c.trim()}return i=xg.has(i)?i:au(i),s.getAttribute(i)}scrapeMotionValuesFromProps(s,i,o){return bg(s,i,o)}build(s,i,o){rg(s,i,this.isSVGTag,o.transformTemplate,o.style)}renderInstance(s,i,o,c){Z0(s,i,o,c)}mount(s){this.isSVGTag=wg(s.tagName),super.mount(s)}}const tk=Sa.length;function kg(t){if(!t)return;if(!t.isControllingVariants){const i=t.parent?kg(t.parent)||{}:{};return t.props.initial!==void 0&&(i.initial=t.props.initial),i}const s={};for(let i=0;i<tk;i++){const o=Sa[i],c=t.props[o];(_r(c)||c===!1)&&(s[o]=c)}return s}function jg(t,s){if(!Array.isArray(s))return!1;const i=s.length;if(i!==t.length)return!1;for(let o=0;o<i;o++)if(s[o]!==t[o])return!1;return!0}const nk=[...hu].reverse(),sk=hu.length;function rk(t){return s=>Promise.all(s.map(({animation:i,options:o})=>l0(t,i,o)))}function ik(t){let s=rk(t),i=hf(),o=!0,c=!1;const d=v=>(g,x)=>{var k;const w=ts(t,x,v==="exit"?(k=t.presenceContext)==null?void 0:k.custom:void 0);if(w){const{transition:S,transitionEnd:j,...N}=w;g={...g,...N,...j}}return g};function h(v){s=v(t)}function f(v){const{props:g}=t,x=kg(t.parent)||{},w=[],k=new Set;let S={},j=1/0;for(let B=0;B<sk;B++){const M=nk[B],L=i[M],I=g[M]!==void 0?g[M]:x[M],D=_r(I),F=M===v?L.isActive:null;F===!1&&(j=B);let V=I===x[M]&&I!==g[M]&&D;if(V&&(o||c)&&t.manuallyAnimateOnMount&&(V=!1),L.protectedKeys={...S},!L.isActive&&F===null||!I&&!L.prevProp||Ra(I)||typeof I=="boolean")continue;if(M==="exit"&&L.isActive&&F!==!0){L.prevResolvedValues&&(S={...S,...L.prevResolvedValues});continue}const O=ak(L.prevProp,I);let oe=O||M===v&&L.isActive&&!V&&D||B>j&&D,le=!1;const xe=Array.isArray(I)?I:[I];let se=xe.reduce(d(M),{});F===!1&&(se={});const{prevResolvedValues:ne={}}=L,Se={...ne,...se},Le=H=>{oe=!0,k.has(H)&&(le=!0,k.delete(H)),L.needsAnimating[H]=!0;const J=t.getValue(H);J&&(J.liveStyle=!1)};for(const H in Se){const J=se[H],K=ne[H];if(S.hasOwnProperty(H))continue;let E=!1;Ec(J)&&Ec(K)?E=!jg(J,K)||O:E=J!==K,E?J!=null?Le(H):k.add(H):J!==void 0&&k.has(H)?Le(H):L.protectedKeys[H]=!0}L.prevProp=I,L.prevResolvedValues=se,L.isActive&&(S={...S,...se}),(o||c)&&t.blockInitialAnimation&&(oe=!1);const Ie=V&&O;oe&&(!Ie||le)&&w.push(...xe.map(H=>{const J={type:M};if(typeof H=="string"&&(o||c)&&!Ie&&t.manuallyAnimateOnMount&&t.parent){const{parent:K}=t,E=ts(K,H);if(K.enteringChildren&&E){const{delayChildren:z}=E.transition||{};J.delay=Yp(K.enteringChildren,t,z)}}return{animation:H,options:J}}))}if(k.size){const B={};if(typeof g.initial!="boolean"){const M=ts(t,Array.isArray(g.initial)?g.initial[0]:g.initial);M&&M.transition&&(B.transition=M.transition)}k.forEach(M=>{const L=t.getBaseTarget(M),I=t.getValue(M);I&&(I.liveStyle=!0),B[M]=L??null}),w.push({animation:B})}let N=!!w.length;return o&&(g.initial===!1||g.initial===g.animate)&&!t.manuallyAnimateOnMount&&(N=!1),o=!1,c=!1,N?s(w):Promise.resolve()}function p(v,g){var w;if(i[v].isActive===g)return Promise.resolve();(w=t.variantChildren)==null||w.forEach(k=>{var S;return(S=k.animationState)==null?void 0:S.setActive(v,g)}),i[v].isActive=g;const x=f(v);for(const k in i)i[k].protectedKeys={};return x}return{animateChanges:f,setActive:p,setAnimateFunction:h,getState:()=>i,reset:()=>{i=hf(),c=!0}}}function ak(t,s){return typeof s=="string"?s!==t:Array.isArray(s)?!jg(s,t):!1}function Gn(t=!1){return{isActive:t,protectedKeys:{},needsAnimating:{},prevResolvedValues:{}}}function hf(){return{animate:Gn(!0),whileInView:Gn(),whileHover:Gn(),whileTap:Gn(),whileDrag:Gn(),whileFocus:Gn(),exit:Gn()}}function Ic(t,s){t.min=s.min,t.max=s.max}function Ft(t,s){Ic(t.x,s.x),Ic(t.y,s.y)}function mf(t,s){t.translate=s.translate,t.scale=s.scale,t.originPoint=s.originPoint,t.origin=s.origin}const Sg=1e-4,ok=1-Sg,lk=1+Sg,Ng=.01,ck=0-Ng,uk=0+Ng;function ct(t){return t.max-t.min}function dk(t,s,i){return Math.abs(t-s)<=i}function ff(t,s,i,o=.5){t.origin=o,t.originPoint=ke(s.min,s.max,t.origin),t.scale=ct(i)/ct(s),t.translate=ke(i.min,i.max,t.origin)-t.originPoint,(t.scale>=ok&&t.scale<=lk||isNaN(t.scale))&&(t.scale=1),(t.translate>=ck&&t.translate<=uk||isNaN(t.translate))&&(t.translate=0)}function Tr(t,s,i,o){ff(t.x,s.x,i.x,o?o.originX:void 0),ff(t.y,s.y,i.y,o?o.originY:void 0)}function pf(t,s,i,o=0){const c=o?ke(i.min,i.max,o):i.min;t.min=c+s.min,t.max=t.min+ct(s)}function hk(t,s,i,o){pf(t.x,s.x,i.x,o==null?void 0:o.x),pf(t.y,s.y,i.y,o==null?void 0:o.y)}function gf(t,s,i,o=0){const c=o?ke(i.min,i.max,o):i.min;t.min=s.min-c,t.max=t.min+ct(s)}function Ta(t,s,i,o){gf(t.x,s.x,i.x,o==null?void 0:o.x),gf(t.y,s.y,i.y,o==null?void 0:o.y)}function yf(t,s,i,o,c){return t-=s,t=ja(t,1/i,o),c!==void 0&&(t=ja(t,1/c,o)),t}function mk(t,s=0,i=1,o=.5,c,d=t,h=t){if(Qt.test(s)&&(s=parseFloat(s),s=ke(h.min,h.max,s/100)-h.min),typeof s!="number")return;let f=ke(d.min,d.max,o);t===d&&(f-=s),t.min=yf(t.min,s,i,f,c),t.max=yf(t.max,s,i,f,c)}function vf(t,s,[i,o,c],d,h){mk(t,s[i],s[o],s[c],s.scale,d,h)}const fk=["x","scaleX","originX"],pk=["y","scaleY","originY"];function xf(t,s,i,o){vf(t.x,s,fk,i?i.x:void 0,o?o.x:void 0),vf(t.y,s,pk,i?i.y:void 0,o?o.y:void 0)}function wf(t){return t.translate===0&&t.scale===1}function Cg(t){return wf(t.x)&&wf(t.y)}function bf(t,s){return t.min===s.min&&t.max===s.max}function gk(t,s){return bf(t.x,s.x)&&bf(t.y,s.y)}function kf(t,s){return Math.round(t.min)===Math.round(s.min)&&Math.round(t.max)===Math.round(s.max)}function Tg(t,s){return kf(t.x,s.x)&&kf(t.y,s.y)}function jf(t){return ct(t.x)/ct(t.y)}function Sf(t,s){return t.translate===s.translate&&t.scale===s.scale&&t.originPoint===s.originPoint}function Xt(t){return[t("x"),t("y")]}function yk(t,s,i){let o="";const c=t.x.translate/s.x,d=t.y.translate/s.y,h=(i==null?void 0:i.z)||0;if((c||d||h)&&(o=`translate3d(${c}px, ${d}px, ${h}px) `),(s.x!==1||s.y!==1)&&(o+=`scale(${1/s.x}, ${1/s.y}) `),i){const{transformPerspective:v,rotate:g,pathRotation:x,rotateX:w,rotateY:k,skewX:S,skewY:j}=i;v&&(o=`perspective(${v}px) ${o}`),g&&(o+=`rotate(${g}deg) `),x&&(o+=`rotate(${x}deg) `),w&&(o+=`rotateX(${w}deg) `),k&&(o+=`rotateY(${k}deg) `),S&&(o+=`skewX(${S}deg) `),j&&(o+=`skewY(${j}deg) `)}const f=t.x.scale*s.x,p=t.y.scale*s.y;return(f!==1||p!==1)&&(o+=`scale(${f}, ${p})`),o||"none"}const vk=ou.length,Nf=t=>typeof t=="string"?parseFloat(t):t,Cf=t=>typeof t=="number"||Q.test(t);function xk(t,s,i,o,c,d){c?(t.opacity=ke(0,i.opacity??1,wk(o)),t.opacityExit=ke(s.opacity??1,0,bk(o))):d&&(t.opacity=ke(s.opacity??1,i.opacity??1,o));for(let h=0;h<vk;h++){const f=ou[h];let p=Tf(s,f),v=Tf(i,f);if(p===void 0&&v===void 0)continue;p||(p=0),v||(v=0),p===0||v===0||Cf(p)===Cf(v)?(t[f]=Math.max(ke(Nf(p),Nf(v),o),0),(Qt.test(v)||Qt.test(p))&&(t[f]+="%")):t[f]=v}(s.rotate||i.rotate)&&(t.rotate=ke(s.rotate||0,i.rotate||0,o))}function Tf(t,s){return t[s]!==void 0?t[s]:t.borderRadius}const wk=Pg(0,.5,xp),bk=Pg(.5,.95,Ot);function Pg(t,s,i){return o=>o<t?0:o>s?1:i(Er(t,s,o))}function kk(t,s,i){const o=Ze(t)?t:Rs(t);return o.start(ru("",o,s,i)),o.animation}function Dr(t,s,i,o={passive:!0}){return t.addEventListener(s,i,o),()=>t.removeEventListener(s,i,o)}const jk=(t,s)=>t.depth-s.depth;class Sk{constructor(){this.children=[],this.isDirty=!1}add(s){Uc(this.children,s),this.isDirty=!0}remove(s){ga(this.children,s),this.isDirty=!0}forEach(s){this.isDirty&&this.children.sort(jk),this.isDirty=!1,this.children.forEach(s)}}function Nk(t,s){const i=it.now(),o=({timestamp:c})=>{const d=c-i;d>=s&&(Mn(o),t(d-s))};return je.setup(o,!0),()=>Mn(o)}function da(t){return Ze(t)?t.get():t}class Ck{constructor(){this.members=[]}add(s){Uc(this.members,s);for(let i=this.members.length-1;i>=0;i--){const o=this.members[i];if(o===s||o===this.lead||o===this.prevLead)continue;const c=o.instance;(!c||c.isConnected===!1)&&!o.snapshot&&(ga(this.members,o),o.unmount())}s.scheduleRender()}remove(s){if(ga(this.members,s),s===this.prevLead&&(this.prevLead=void 0),s===this.lead){const i=this.members[this.members.length-1];i&&this.promote(i)}}relegate(s){var i;for(let o=this.members.indexOf(s)-1;o>=0;o--){const c=this.members[o];if(c.isPresent!==!1&&((i=c.instance)==null?void 0:i.isConnected)!==!1)return this.promote(c),!0}return!1}promote(s,i){var c;const o=this.lead;if(s!==o&&(this.prevLead=o,this.lead=s,s.show(),o)){o.updateSnapshot(),s.scheduleRender();const{layoutDependency:d}=o.options,{layoutDependency:h}=s.options;(d===void 0||d!==h)&&(s.resumeFrom=o,i&&(o.preserveOpacity=!0),o.snapshot&&(s.snapshot=o.snapshot,s.snapshot.latestValues=o.animationValues||o.latestValues),(c=s.root)!=null&&c.isUpdating&&(s.isLayoutDirty=!0)),s.options.crossfade===!1&&o.hide()}}exitAnimationComplete(){this.members.forEach(s=>{var i,o,c,d,h;(o=(i=s.options).onExitComplete)==null||o.call(i),(h=(c=s.resumingFrom)==null?void 0:(d=c.options).onExitComplete)==null||h.call(d)})}scheduleRender(){this.members.forEach(s=>s.instance&&s.scheduleRender(!1))}removeLeadSnapshot(){var s;(s=this.lead)!=null&&s.snapshot&&(this.lead.snapshot=void 0)}}const ha={hasAnimatedSinceResize:!0,hasEverUpdated:!1},ql=["","X","Y","Z"],Tk=1e3;let Pk=0;function Ql(t,s,i,o){const{latestValues:c}=s;c[t]&&(i[t]=c[t],s.setStaticValue(t,0),o&&(o[t]=0))}function Eg(t){if(t.hasCheckedOptimisedAppear=!0,t.root===t)return;const{visualElement:s}=t.options;if(!s)return;const i=eg(s);if(window.MotionHasOptimisedAnimation(i,"transform")){const{layout:c,layoutId:d}=t.options;window.MotionCancelOptimisedAnimation(i,"transform",je,!(c||d))}const{parent:o}=t;o&&!o.hasCheckedOptimisedAppear&&Eg(o)}function Mg({attachResizeListener:t,defaultParent:s,measureScroll:i,checkIsScrollRoot:o,resetTransform:c}){return class{constructor(h={},f=s==null?void 0:s()){this.id=Pk++,this.animationId=0,this.animationCommitId=0,this.children=new Set,this.options={},this.isTreeAnimating=!1,this.isAnimationBlocked=!1,this.isLayoutDirty=!1,this.isProjectionDirty=!1,this.isSharedProjectionDirty=!1,this.isTransformDirty=!1,this.updateManuallyBlocked=!1,this.updateBlockedByResize=!1,this.isUpdating=!1,this.isSVG=!1,this.needsReset=!1,this.shouldResetTransform=!1,this.hasCheckedOptimisedAppear=!1,this.treeScale={x:1,y:1},this.eventHandlers=new Map,this.hasTreeAnimated=!1,this.layoutVersion=0,this.updateScheduled=!1,this.scheduleUpdate=()=>this.update(),this.projectionUpdateScheduled=!1,this.checkUpdateFailed=()=>{this.isUpdating&&(this.isUpdating=!1,this.clearAllSnapshots())},this.updateProjection=()=>{this.projectionUpdateScheduled=!1,this.nodes.forEach(Ak),this.nodes.forEach(Vk),this.nodes.forEach(Fk),this.nodes.forEach(_k)},this.resolvedRelativeTargetAt=0,this.linkedParentVersion=0,this.hasProjected=!1,this.isVisible=!0,this.animationProgress=0,this.sharedNodes=new Map,this.latestValues=h,this.root=f?f.root||f:this,this.path=f?[...f.path,f]:[],this.parent=f,this.depth=f?f.depth+1:0;for(let p=0;p<this.path.length;p++)this.path[p].shouldResetTransform=!0;this.root===this&&(this.nodes=new Sk)}addEventListener(h,f){return this.eventHandlers.has(h)||this.eventHandlers.set(h,new ya),this.eventHandlers.get(h).add(f)}notifyListeners(h,...f){const p=this.eventHandlers.get(h);p&&p.notify(...f)}hasListeners(h){return this.eventHandlers.has(h)}mount(h){if(this.instance)return;this.isSVG=lu(h)&&!$0(h),this.instance=h;const{layoutId:f,layout:p,visualElement:v}=this.options;if(v&&!v.current&&v.mount(h),this.root.nodes.add(this),this.parent&&this.parent.children.add(this),this.root.hasTreeAnimated&&(p||f)&&(this.isLayoutDirty=!0),t){let g,x=0;const w=()=>this.root.updateBlockedByResize=!1;je.read(()=>{x=window.innerWidth}),t(h,()=>{const k=window.innerWidth;k!==x&&(x=k,this.root.updateBlockedByResize=!0,g&&g(),g=Nk(w,250),ha.hasAnimatedSinceResize&&(ha.hasAnimatedSinceResize=!1,this.nodes.forEach(Mf)))})}f&&this.root.registerSharedNode(f,this),this.options.animate!==!1&&v&&(f||p)&&this.addEventListener("didUpdate",({delta:g,hasLayoutChanged:x,hasRelativeLayoutChanged:w,layout:k})=>{if(this.isTreeAnimationBlocked()){this.target=void 0,this.relativeTarget=void 0;return}const S=this.options.transition||v.getDefaultTransition()||Wk,{onLayoutAnimationStart:j,onLayoutAnimationComplete:N}=v.getProps(),B=!this.targetLayout||!Tg(this.targetLayout,k),M=!x&&w;if(this.options.layoutRoot||this.resumeFrom||M||x&&(B||!this.currentAnimation)){this.resumeFrom&&(this.resumingFrom=this.resumeFrom,this.resumingFrom.resumingFrom=void 0);const L={...su(S,"layout"),onPlay:j,onComplete:N};(v.shouldReduceMotion||this.options.layoutRoot)&&(L.delay=0,L.type=!1),this.startAnimation(L),this.setAnimationOrigin(g,M,L.path)}else x||Mf(this),this.isLead()&&this.options.onExitComplete&&this.options.onExitComplete();this.targetLayout=k})}unmount(){this.options.layoutId&&this.willUpdate(),this.root.nodes.remove(this);const h=this.getStack();h&&h.remove(this),this.parent&&this.parent.children.delete(this),this.instance=void 0,this.eventHandlers.clear(),Mn(this.updateProjection)}blockUpdate(){this.updateManuallyBlocked=!0}unblockUpdate(){this.updateManuallyBlocked=!1}isUpdateBlocked(){return this.updateManuallyBlocked||this.updateBlockedByResize}isTreeAnimationBlocked(){return this.isAnimationBlocked||this.parent&&this.parent.isTreeAnimationBlocked()||!1}startUpdate(){this.isUpdateBlocked()||(this.isUpdating=!0,this.nodes&&this.nodes.forEach(Bk),this.animationId++)}getTransformTemplate(){const{visualElement:h}=this.options;return h&&h.getProps().transformTemplate}willUpdate(h=!0){if(this.root.hasTreeAnimated=!0,this.root.isUpdateBlocked()){this.options.onExitComplete&&this.options.onExitComplete();return}if(window.MotionCancelOptimisedAnimation&&!this.hasCheckedOptimisedAppear&&Eg(this),!this.root.isUpdating&&this.root.startUpdate(),this.isLayoutDirty)return;this.isLayoutDirty=!0;for(let g=0;g<this.path.length;g++){const x=this.path[g];x.shouldResetTransform=!0,(typeof x.latestValues.x=="string"||typeof x.latestValues.y=="string")&&(x.isLayoutDirty=!0),x.updateScroll("snapshot"),x.options.layoutRoot&&x.willUpdate(!1)}const{layoutId:f,layout:p}=this.options;if(f===void 0&&!p)return;const v=this.getTransformTemplate();this.prevTransformTemplateValue=v?v(this.latestValues,""):void 0,this.updateSnapshot(),h&&this.notifyListeners("willUpdate")}update(){if(this.updateScheduled=!1,this.isUpdateBlocked()){const p=this.updateBlockedByResize;this.unblockUpdate(),this.updateBlockedByResize=!1,this.clearAllSnapshots(),p&&this.nodes.forEach(Rk),this.nodes.forEach(Pf);return}if(this.animationId<=this.animationCommitId){this.nodes.forEach(Ef);return}this.animationCommitId=this.animationId,this.isUpdating?(this.isUpdating=!1,this.nodes.forEach(Lk),this.nodes.forEach(Ik),this.nodes.forEach(Ek),this.nodes.forEach(Mk)):this.nodes.forEach(Ef),this.clearAllSnapshots();const f=it.now();$e.delta=Ut(0,1e3/60,f-$e.timestamp),$e.timestamp=f,$e.isProcessing=!0,Ul.update.process($e),Ul.preRender.process($e),Ul.render.process($e),$e.isProcessing=!1}didUpdate(){this.updateScheduled||(this.updateScheduled=!0,uu.read(this.scheduleUpdate))}clearAllSnapshots(){this.nodes.forEach(Dk),this.sharedNodes.forEach(Ok)}scheduleUpdateProjection(){this.projectionUpdateScheduled||(this.projectionUpdateScheduled=!0,je.preRender(this.updateProjection,!1,!0))}scheduleCheckAfterUnmount(){je.postRender(()=>{this.isLayoutDirty?this.root.didUpdate():this.root.checkUpdateFailed()})}updateSnapshot(){this.snapshot||!this.instance||(this.snapshot=this.measure(),this.snapshot&&!ct(this.snapshot.measuredBox.x)&&!ct(this.snapshot.measuredBox.y)&&(this.snapshot=void 0))}updateLayout(){if(!this.instance||(this.updateScroll(),!(this.options.alwaysMeasureLayout&&this.isLead())&&!this.isLayoutDirty))return;if(this.resumeFrom&&!this.resumeFrom.instance)for(let p=0;p<this.path.length;p++)this.path[p].updateScroll();const h=this.layout;this.layout=this.measure(!1),this.layoutVersion++,this.layoutCorrected||(this.layoutCorrected=We()),this.isLayoutDirty=!1,this.projectionDelta=void 0,this.notifyListeners("measure",this.layout.layoutBox);const{visualElement:f}=this.options;f&&f.notify("LayoutMeasure",this.layout.layoutBox,h?h.layoutBox:void 0)}updateScroll(h="measure"){let f=!!(this.options.layoutScroll&&this.instance);if(this.scroll&&this.scroll.animationId===this.root.animationId&&this.scroll.phase===h&&(f=!1),f&&this.instance){const p=o(this.instance);this.scroll={animationId:this.root.animationId,phase:h,isRoot:p,offset:i(this.instance),wasRoot:this.scroll?this.scroll.isRoot:p}}}resetTransform(){if(!c)return;const h=this.isLayoutDirty||this.shouldResetTransform||this.options.alwaysMeasureLayout,f=this.projectionDelta&&!Cg(this.projectionDelta),p=this.getTransformTemplate(),v=p?p(this.latestValues,""):void 0,g=v!==this.prevTransformTemplateValue;h&&this.instance&&(f||Kn(this.latestValues)||g)&&(c(this.instance,v),this.shouldResetTransform=!1,this.scheduleRender())}measure(h=!0){const f=this.measurePageBox();let p=this.removeElementScroll(f);return h&&(p=this.removeTransform(p)),$k(p),{animationId:this.root.animationId,measuredBox:f,layoutBox:p,latestValues:{},source:this.id}}measurePageBox(){var v;const{visualElement:h}=this.options;if(!h)return We();const f=h.measureViewportBox();if(!(((v=this.scroll)==null?void 0:v.wasRoot)||this.path.some(Hk))){const{scroll:g}=this.root;g&&(Yt(f.x,g.offset.x),Yt(f.y,g.offset.y))}return f}removeElementScroll(h){var p;const f=We();if(Ft(f,h),(p=this.scroll)!=null&&p.wasRoot)return f;for(let v=0;v<this.path.length;v++){const g=this.path[v],{scroll:x,options:w}=g;g!==this.root&&x&&w.layoutScroll&&(x.wasRoot&&Ft(f,h),Yt(f.x,x.offset.x),Yt(f.y,x.offset.y))}return f}applyTransform(h,f=!1,p){var g,x;const v=p||We();Ft(v,h);for(let w=0;w<this.path.length;w++){const k=this.path[w];!f&&k.options.layoutScroll&&k.scroll&&k!==k.root&&(Yt(v.x,-k.scroll.offset.x),Yt(v.y,-k.scroll.offset.y)),Kn(k.latestValues)&&oa(v,k.latestValues,(g=k.layout)==null?void 0:g.layoutBox)}return Kn(this.latestValues)&&oa(v,this.latestValues,(x=this.layout)==null?void 0:x.layoutBox),v}removeTransform(h){var p;const f=We();Ft(f,h);for(let v=0;v<this.path.length;v++){const g=this.path[v];if(!Kn(g.latestValues))continue;let x;g.instance&&(Dc(g.latestValues)&&g.updateSnapshot(),x=We(),Ft(x,g.measurePageBox())),xf(f,g.latestValues,(p=g.snapshot)==null?void 0:p.layoutBox,x)}return Kn(this.latestValues)&&xf(f,this.latestValues),f}setTargetDelta(h){this.targetDelta=h,this.root.scheduleUpdateProjection(),this.isProjectionDirty=!0}setOptions(h){this.options={...this.options,...h,crossfade:h.crossfade!==void 0?h.crossfade:!0}}clearMeasurements(){this.scroll=void 0,this.layout=void 0,this.snapshot=void 0,this.prevTransformTemplateValue=void 0,this.targetDelta=void 0,this.target=void 0,this.isLayoutDirty=!1}forceRelativeParentToResolveTarget(){this.relativeParent&&this.relativeParent.resolvedRelativeTargetAt!==$e.timestamp&&this.relativeParent.resolveTargetDelta(!0)}resolveTargetDelta(h=!1){var k;const f=this.getLead();this.isProjectionDirty||(this.isProjectionDirty=f.isProjectionDirty),this.isTransformDirty||(this.isTransformDirty=f.isTransformDirty),this.isSharedProjectionDirty||(this.isSharedProjectionDirty=f.isSharedProjectionDirty);const p=!!this.resumingFrom||this!==f;if(!(h||p&&this.isSharedProjectionDirty||this.isProjectionDirty||(k=this.parent)!=null&&k.isProjectionDirty||this.attemptToResolveRelativeTarget||this.root.updateBlockedByResize))return;const{layout:g,layoutId:x}=this.options;if(!this.layout||!(g||x))return;this.resolvedRelativeTargetAt=$e.timestamp;const w=this.getClosestProjectingParent();w&&this.linkedParentVersion!==w.layoutVersion&&!w.options.layoutRoot&&this.removeRelativeTarget(),!this.targetDelta&&!this.relativeTarget&&(this.options.layoutAnchor!==!1&&w&&w.layout?this.createRelativeTarget(w,this.layout.layoutBox,w.layout.layoutBox):this.removeRelativeTarget()),!(!this.relativeTarget&&!this.targetDelta)&&(this.target||(this.target=We(),this.targetWithTransforms=We()),this.relativeTarget&&this.relativeTargetOrigin&&this.relativeParent&&this.relativeParent.target?(this.forceRelativeParentToResolveTarget(),hk(this.target,this.relativeTarget,this.relativeParent.target,this.options.layoutAnchor||void 0)):this.targetDelta?(this.resumingFrom?this.applyTransform(this.layout.layoutBox,!1,this.target):Ft(this.target,this.layout.layoutBox),og(this.target,this.targetDelta)):Ft(this.target,this.layout.layoutBox),this.attemptToResolveRelativeTarget&&(this.attemptToResolveRelativeTarget=!1,this.options.layoutAnchor!==!1&&w&&!!w.resumingFrom==!!this.resumingFrom&&!w.options.layoutScroll&&w.target&&this.animationProgress!==1?this.createRelativeTarget(w,this.target,w.target):this.relativeParent=this.relativeTarget=void 0))}getClosestProjectingParent(){if(!(!this.parent||Dc(this.parent.latestValues)||ag(this.parent.latestValues)))return this.parent.isProjecting()?this.parent:this.parent.getClosestProjectingParent()}isProjecting(){return!!((this.relativeTarget||this.targetDelta||this.options.layoutRoot)&&this.layout)}createRelativeTarget(h,f,p){this.relativeParent=h,this.linkedParentVersion=h.layoutVersion,this.forceRelativeParentToResolveTarget(),this.relativeTarget=We(),this.relativeTargetOrigin=We(),Ta(this.relativeTargetOrigin,f,p,this.options.layoutAnchor||void 0),Ft(this.relativeTarget,this.relativeTargetOrigin)}removeRelativeTarget(){this.relativeParent=this.relativeTarget=void 0}calcProjection(){var S;const h=this.getLead(),f=!!this.resumingFrom||this!==h;let p=!0;if((this.isProjectionDirty||(S=this.parent)!=null&&S.isProjectionDirty)&&(p=!1),f&&(this.isSharedProjectionDirty||this.isTransformDirty)&&(p=!1),this.resolvedRelativeTargetAt===$e.timestamp&&(p=!1),p)return;const{layout:v,layoutId:g}=this.options;if(this.isTreeAnimating=!!(this.parent&&this.parent.isTreeAnimating||this.currentAnimation||this.pendingAnimation),this.isTreeAnimating||(this.targetDelta=this.relativeTarget=void 0),!this.layout||!(v||g))return;Ft(this.layoutCorrected,this.layout.layoutBox);const x=this.treeScale.x,w=this.treeScale.y;N0(this.layoutCorrected,this.treeScale,this.path,f),h.layout&&!h.target&&(this.treeScale.x!==1||this.treeScale.y!==1)&&(h.target=h.layout.layoutBox,h.targetWithTransforms=We());const{target:k}=h;if(!k){this.prevProjectionDelta&&(this.createProjectionDeltas(),this.scheduleRender());return}!this.projectionDelta||!this.prevProjectionDelta?this.createProjectionDeltas():(mf(this.prevProjectionDelta.x,this.projectionDelta.x),mf(this.prevProjectionDelta.y,this.projectionDelta.y)),Tr(this.projectionDelta,this.layoutCorrected,k,this.latestValues),(this.treeScale.x!==x||this.treeScale.y!==w||!Sf(this.projectionDelta.x,this.prevProjectionDelta.x)||!Sf(this.projectionDelta.y,this.prevProjectionDelta.y))&&(this.hasProjected=!0,this.scheduleRender(),this.notifyListeners("projectionUpdate",k))}hide(){this.isVisible=!1}show(){this.isVisible=!0}scheduleRender(h=!0){var f;if((f=this.options.visualElement)==null||f.scheduleRender(),h){const p=this.getStack();p&&p.scheduleRender()}this.resumingFrom&&!this.resumingFrom.instance&&(this.resumingFrom=void 0)}createProjectionDeltas(){this.prevProjectionDelta=_s(),this.projectionDelta=_s(),this.projectionDeltaWithTransform=_s()}setAnimationOrigin(h,f=!1,p){const v=this.snapshot,g=v?v.latestValues:{},x={...this.latestValues},w=_s();(!this.relativeParent||!this.relativeParent.options.layoutRoot)&&(this.relativeTarget=this.relativeTargetOrigin=void 0),this.attemptToResolveRelativeTarget=!f;const k=We(),S=v?v.source:void 0,j=this.layout?this.layout.source:void 0,N=S!==j,B=this.getStack(),M=!B||B.members.length<=1,L=!!(N&&!M&&this.options.crossfade===!0&&!this.path.some(Uk));this.animationProgress=0;let I;const D=p==null?void 0:p.interpolateProjection(h);this.mixTargetDelta=F=>{const V=F/1e3,O=D==null?void 0:D(V);O?(w.x.translate=O.x,w.x.scale=ke(h.x.scale,1,V),w.x.origin=h.x.origin,w.x.originPoint=h.x.originPoint,w.y.translate=O.y,w.y.scale=ke(h.y.scale,1,V),w.y.origin=h.y.origin,w.y.originPoint=h.y.originPoint):(Af(w.x,h.x,V),Af(w.y,h.y,V)),this.setTargetDelta(w),this.relativeTarget&&this.relativeTargetOrigin&&this.layout&&this.relativeParent&&this.relativeParent.layout&&(Ta(k,this.layout.layoutBox,this.relativeParent.layout.layoutBox,this.options.layoutAnchor||void 0),zk(this.relativeTarget,this.relativeTargetOrigin,k,V),I&&gk(this.relativeTarget,I)&&(this.isProjectionDirty=!1),I||(I=We()),Ft(I,this.relativeTarget)),N&&(this.animationValues=x,xk(x,g,this.latestValues,V,L,M)),O&&O.rotate!==void 0&&(this.animationValues||(this.animationValues=x),this.animationValues.pathRotation=O.rotate),this.root.scheduleUpdateProjection(),this.scheduleRender(),this.animationProgress=V},this.mixTargetDelta(this.options.layoutRoot?1e3:0)}startAnimation(h){var f,p,v;this.notifyListeners("animationStart"),(f=this.currentAnimation)==null||f.stop(),(v=(p=this.resumingFrom)==null?void 0:p.currentAnimation)==null||v.stop(),this.pendingAnimation&&(Mn(this.pendingAnimation),this.pendingAnimation=void 0),this.pendingAnimation=je.update(()=>{ha.hasAnimatedSinceResize=!0,this.motionValue||(this.motionValue=Rs(0)),this.motionValue.jump(0,!1),this.currentAnimation=kk(this.motionValue,[0,1e3],{...h,velocity:0,isSync:!0,onUpdate:g=>{this.mixTargetDelta(g),h.onUpdate&&h.onUpdate(g)},onComplete:()=>{h.onComplete&&h.onComplete(),this.completeAnimation()}}),lb(this.currentAnimation,this),this.resumingFrom&&(this.resumingFrom.currentAnimation=this.currentAnimation),this.pendingAnimation=void 0})}completeAnimation(){this.resumingFrom&&(this.resumingFrom.currentAnimation=void 0,this.resumingFrom.preserveOpacity=void 0);const h=this.getStack();h&&h.exitAnimationComplete(),this.resumingFrom=this.currentAnimation=this.animationValues=void 0,this.notifyListeners("animationComplete")}finishAnimation(){this.currentAnimation&&(this.mixTargetDelta&&this.mixTargetDelta(Tk),this.currentAnimation.stop()),this.completeAnimation()}applyTransformsToTarget(){const h=this.getLead(),{targetWithTransforms:f,layout:p,latestValues:v}=h;let{target:g}=h;if(!(!f||!g||!p)){if(this!==h&&this.layout&&p&&Ag(this.options.animationType,this.layout.layoutBox,p.layoutBox)){g=this.target||We();const x=ct(this.layout.layoutBox.x);g.x.min=h.target.x.min,g.x.max=g.x.min+x;const w=ct(this.layout.layoutBox.y);g.y.min=h.target.y.min,g.y.max=g.y.min+w}Ft(f,g),oa(f,v),Tr(this.projectionDeltaWithTransform,this.layoutCorrected,f,v)}}registerSharedNode(h,f){this.sharedNodes.has(h)||this.sharedNodes.set(h,new Ck),this.sharedNodes.get(h).add(f);const v=f.options.initialPromotionConfig;f.promote({transition:v?v.transition:void 0,preserveFollowOpacity:v&&v.shouldPreserveFollowOpacity?v.shouldPreserveFollowOpacity(f):void 0})}isLead(){const h=this.getStack();return h?h.lead===this:!0}getLead(){var f;const{layoutId:h}=this.options;return h?((f=this.getStack())==null?void 0:f.lead)||this:this}getPrevLead(){var f;const{layoutId:h}=this.options;return h?(f=this.getStack())==null?void 0:f.prevLead:void 0}getStack(){const{layoutId:h}=this.options;if(h)return this.root.sharedNodes.get(h)}promote({needsReset:h,transition:f,preserveFollowOpacity:p}={}){const v=this.getStack();v&&v.promote(this,p),h&&(this.projectionDelta=void 0,this.needsReset=!0),f&&this.setOptions({transition:f})}relegate(){const h=this.getStack();return h?h.relegate(this):!1}resetSkewAndRotation(){const{visualElement:h}=this.options;if(!h)return;let f=!1;const{latestValues:p}=h;if((p.z||p.rotate||p.rotateX||p.rotateY||p.rotateZ||p.skewX||p.skewY)&&(f=!0),!f)return;const v={};p.z&&Ql("z",h,v,this.animationValues);for(let g=0;g<ql.length;g++)Ql(`rotate${ql[g]}`,h,v,this.animationValues),Ql(`skew${ql[g]}`,h,v,this.animationValues);h.render();for(const g in v)h.setStaticValue(g,v[g]),this.animationValues&&(this.animationValues[g]=v[g]);h.scheduleRender()}applyProjectionStyles(h,f){if(!this.instance||this.isSVG)return;if(!this.isVisible){h.visibility="hidden";return}const p=this.getTransformTemplate();if(this.needsReset){this.needsReset=!1,h.visibility="",h.opacity="",h.pointerEvents=da(f==null?void 0:f.pointerEvents)||"",h.transform=p?p(this.latestValues,""):"none";return}const v=this.getLead();if(!this.projectionDelta||!this.layout||!v.target){this.options.layoutId&&(h.opacity=this.latestValues.opacity!==void 0?this.latestValues.opacity:1,h.pointerEvents=da(f==null?void 0:f.pointerEvents)||""),this.hasProjected&&!Kn(this.latestValues)&&(h.transform=p?p({},""):"none",this.hasProjected=!1);return}h.visibility="";const g=v.animationValues||v.latestValues;this.applyTransformsToTarget();let x=yk(this.projectionDeltaWithTransform,this.treeScale,g);p&&(x=p(g,x)),h.transform=x;const{x:w,y:k}=this.projectionDelta;h.transformOrigin=`${w.origin*100}% ${k.origin*100}% 0`,v.animationValues?h.opacity=v===this?g.opacity??this.latestValues.opacity??1:this.preserveOpacity?this.latestValues.opacity:g.opacityExit:h.opacity=v===this?g.opacity!==void 0?g.opacity:"":g.opacityExit!==void 0?g.opacityExit:0;for(const S in Lc){if(g[S]===void 0)continue;const{correct:j,applyTo:N,isCSSVariable:B}=Lc[S],M=x==="none"?g[S]:j(g[S],v);if(N){const L=N.length;for(let I=0;I<L;I++)h[N[I]]=M}else B?this.options.visualElement.renderState.vars[S]=M:h[S]=M}this.options.layoutId&&(h.pointerEvents=v===this?da(f==null?void 0:f.pointerEvents)||"":"none")}clearSnapshot(){this.resumeFrom=this.snapshot=void 0}resetTree(){this.root.nodes.forEach(h=>{var f;return(f=h.currentAnimation)==null?void 0:f.stop()}),this.root.nodes.forEach(Pf),this.root.sharedNodes.clear()}}}function Ek(t){t.updateLayout()}function Mk(t){var i;const s=((i=t.resumeFrom)==null?void 0:i.snapshot)||t.snapshot;if(t.isLead()&&t.layout&&s&&t.hasListeners("didUpdate")){const{layoutBox:o,measuredBox:c}=t.layout,{animationType:d}=t.options,h=s.source!==t.layout.source;if(d==="size")Xt(x=>{const w=h?s.measuredBox[x]:s.layoutBox[x],k=ct(w);w.min=o[x].min,w.max=w.min+k});else if(d==="x"||d==="y"){const x=d==="x"?"y":"x";Ic(h?s.measuredBox[x]:s.layoutBox[x],o[x])}else Ag(d,s.layoutBox,o)&&Xt(x=>{const w=h?s.measuredBox[x]:s.layoutBox[x],k=ct(o[x]);w.max=w.min+k,t.relativeTarget&&!t.currentAnimation&&(t.isProjectionDirty=!0,t.relativeTarget[x].max=t.relativeTarget[x].min+k)});const f=_s();Tr(f,o,s.layoutBox);const p=_s();h?Tr(p,t.applyTransform(c,!0),s.measuredBox):Tr(p,o,s.layoutBox);const v=!Cg(f);let g=!1;if(!t.resumeFrom){const x=t.getClosestProjectingParent();if(x&&!x.resumeFrom){const{snapshot:w,layout:k}=x;if(w&&k){const S=t.options.layoutAnchor||void 0,j=We();Ta(j,s.layoutBox,w.layoutBox,S);const N=We();Ta(N,o,k.layoutBox,S),Tg(j,N)||(g=!0),x.options.layoutRoot&&(t.relativeTarget=N,t.relativeTargetOrigin=j,t.relativeParent=x)}}}t.notifyListeners("didUpdate",{layout:o,snapshot:s,delta:p,layoutDelta:f,hasLayoutChanged:v,hasRelativeLayoutChanged:g})}else if(t.isLead()){const{onExitComplete:o}=t.options;o&&o()}t.options.transition=void 0}function Ak(t){t.parent&&(t.isProjecting()||(t.isProjectionDirty=t.parent.isProjectionDirty),t.isSharedProjectionDirty||(t.isSharedProjectionDirty=!!(t.isProjectionDirty||t.parent.isProjectionDirty||t.parent.isSharedProjectionDirty)),t.isTransformDirty||(t.isTransformDirty=t.parent.isTransformDirty))}function _k(t){t.isProjectionDirty=t.isSharedProjectionDirty=t.isTransformDirty=!1}function Dk(t){t.clearSnapshot()}function Pf(t){t.clearMeasurements()}function Rk(t){t.isLayoutDirty=!0,t.updateLayout()}function Ef(t){t.isLayoutDirty=!1}function Lk(t){t.isAnimationBlocked&&t.layout&&!t.isLayoutDirty&&(t.snapshot=t.layout,t.isLayoutDirty=!0)}function Ik(t){const{visualElement:s}=t.options;s&&s.getProps().onBeforeLayoutMeasure&&s.notify("BeforeLayoutMeasure"),t.resetTransform()}function Mf(t){t.finishAnimation(),t.targetDelta=t.relativeTarget=t.target=void 0,t.isProjectionDirty=!0}function Vk(t){t.resolveTargetDelta()}function Fk(t){t.calcProjection()}function Bk(t){t.resetSkewAndRotation()}function Ok(t){t.removeLeadSnapshot()}function Af(t,s,i){t.translate=ke(s.translate,0,i),t.scale=ke(s.scale,1,i),t.origin=s.origin,t.originPoint=s.originPoint}function _f(t,s,i,o){t.min=ke(s.min,i.min,o),t.max=ke(s.max,i.max,o)}function zk(t,s,i,o){_f(t.x,s.x,i.x,o),_f(t.y,s.y,i.y,o)}function Uk(t){return t.animationValues&&t.animationValues.opacityExit!==void 0}const Wk={duration:.45,ease:[.4,0,.1,1]},Df=t=>typeof navigator<"u"&&navigator.userAgent&&navigator.userAgent.toLowerCase().includes(t),Rf=Df("applewebkit/")&&!Df("chrome/")?Math.round:Ot;function Lf(t){t.min=Rf(t.min),t.max=Rf(t.max)}function $k(t){Lf(t.x),Lf(t.y)}function Ag(t,s,i){return t==="position"||t==="preserve-aspect"&&!dk(jf(s),jf(i),.2)}function Hk(t){var s;return t!==t.root&&((s=t.scroll)==null?void 0:s.wasRoot)}const Gk=Mg({attachResizeListener:(t,s)=>Dr(t,"resize",s),measureScroll:()=>{var t,s;return{x:document.documentElement.scrollLeft||((t=document.body)==null?void 0:t.scrollLeft)||0,y:document.documentElement.scrollTop||((s=document.body)==null?void 0:s.scrollTop)||0}},checkIsScrollRoot:()=>!0}),Jl={current:void 0},_g=Mg({measureScroll:t=>({x:t.scrollLeft,y:t.scrollTop}),defaultParent:()=>{if(!Jl.current){const t=new Gk({});t.mount(window),t.setOptions({layoutScroll:!0}),Jl.current=t}return Jl.current},resetTransform:(t,s)=>{t.style.transform=s!==void 0?s:"none"},checkIsScrollRoot:t=>window.getComputedStyle(t).position==="fixed"}),Dg=P.createContext({transformPagePoint:t=>t,isStatic:!1,reducedMotion:"never"});function Kk(t=!0){const s=P.useContext(zc);if(s===null)return[!0,null];const{isPresent:i,onExitComplete:o,register:c}=s,d=P.useId();P.useEffect(()=>{if(t)return c(d)},[t]);const h=P.useCallback(()=>t&&o&&o(d),[d,o,t]);return!i&&o?[!1,h]:[!0]}const Rg=P.createContext({strict:!1}),If={animation:["animate","variants","whileHover","whileTap","exit","whileInView","whileFocus","whileDrag"],exit:["exit"],drag:["drag","dragControls"],focus:["whileFocus"],hover:["whileHover","onHoverStart","onHoverEnd"],tap:["whileTap","onTap","onTapStart","onTapCancel"],pan:["onPan","onPanStart","onPanSessionStart","onPanEnd"],inView:["whileInView","onViewportEnter","onViewportLeave"],layout:["layout","layoutId"]};let Vf=!1;function Xk(){if(Vf)return;const t={};for(const s in If)t[s]={isEnabled:i=>If[s].some(o=>!!i[o])};pg(t),Vf=!0}function Lg(){return Xk(),X0()}function Yk(t){const s=Lg();for(const i in t)s[i]={...s[i],...t[i]};pg(s)}const Ia=P.createContext({});function qk(t,s){if(La(t)){const{initial:i,animate:o}=t;return{initial:i===!1||_r(i)?i:void 0,animate:_r(o)?o:void 0}}return t.inherit!==!1?s:{}}function Qk(t){const{initial:s,animate:i}=qk(t,P.useContext(Ia));return P.useMemo(()=>({initial:s,animate:i}),[Ff(s),Ff(i)])}function Ff(t){return Array.isArray(t)?t.join(" "):t}const pu=()=>({style:{},transform:{},transformOrigin:{},vars:{}});function Ig(t,s,i){for(const o in s)!Ze(s[o])&&!vg(o,i)&&(t[o]=s[o])}function Jk({transformTemplate:t},s){return P.useMemo(()=>{const i=pu();return cu(i,s,t),Object.assign({},i.vars,i.style)},[s])}function Zk(t,s){const i=t.style||{},o={};return Ig(o,i,t),Object.assign(o,Jk(t,s)),o}function ej(t,s){const i={},o=Zk(t,s);return t.drag&&t.dragListener!==!1&&(i.draggable=!1,o.userSelect=o.WebkitUserSelect=o.WebkitTouchCallout="none",o.touchAction=t.drag===!0?"none":`pan-${t.drag==="x"?"y":"x"}`),t.tabIndex===void 0&&(t.onTap||t.onTapStart||t.whileTap)&&(i.tabIndex=0),i.style=o,i}const Vg=()=>({...pu(),attrs:{}});function tj(t,s,i,o){const c=P.useMemo(()=>{const d=Vg();return rg(d,s,wg(o),t.transformTemplate,t.style),{...d.attrs,style:{...d.style}}},[s]);if(t.style){const d={};Ig(d,t.style,t),c.style={...d,...c.style}}return c}const nj=new Set(["animate","exit","variants","initial","style","values","variants","transition","transformTemplate","custom","inherit","onBeforeLayoutMeasure","onAnimationStart","onAnimationComplete","onUpdate","onDragStart","onDrag","onDragEnd","onMeasureDragConstraints","onDirectionLock","onDragTransitionEnd","_dragX","_dragY","onHoverStart","onHoverEnd","onViewportEnter","onViewportLeave","globalTapTarget","propagate","ignoreStrict","viewport"]);function Pa(t){return t.startsWith("while")||t.startsWith("drag")&&t!=="draggable"||t.startsWith("layout")||t.startsWith("onTap")||t.startsWith("onPan")||t.startsWith("onLayout")||nj.has(t)}function sj(t,s){return t.startsWith("on")?!Pa(t):(s==null?void 0:s(t))??!Pa(t)}function rj(t,s,i,o){const c={};for(const d in t)d==="values"&&typeof t.values=="object"||Ze(t[d])||(sj(d,o)||i===!0&&Pa(d)||!s&&!Pa(d)||t.draggable&&d.startsWith("onDrag"))&&(c[d]=t[d]);return c}const ij=["animate","circle","defs","desc","ellipse","g","image","line","filter","marker","mask","metadata","path","pattern","polygon","polyline","rect","stop","switch","symbol","svg","text","tspan","use","view"];function gu(t){return typeof t!="string"||t.includes("-")?!1:!!(ij.indexOf(t)>-1||/[A-Z]/u.test(t))}function aj(t,s,i,{latestValues:o},c,d=!1,h,f){const v=(h??gu(t)?tj:ej)(s,o,c,t),g=rj(s,typeof t=="string",d,f),x=t!==P.Fragment?{...g,...v,ref:i}:{},{children:w}=s,k=P.useMemo(()=>Ze(w)?w.get():w,[w]);return P.createElement(t,{...x,children:k})}function oj({scrapeMotionValuesFromProps:t,createRenderState:s},i,o,c){return{latestValues:lj(i,o,c,t),renderState:s()}}function lj(t,s,i,o){const c={},d=o(t,{});for(const w in d)c[w]=da(d[w]);let{initial:h,animate:f}=t;const p=La(t),v=mg(t);s&&v&&!p&&t.inherit!==!1&&(h===void 0&&(h=s.initial),f===void 0&&(f=s.animate));let g=i?i.initial===!1:!1;g=g||h===!1;const x=g?f:h;if(x&&typeof x!="boolean"&&!Ra(x)){const w=Array.isArray(x)?x:[x];for(let k=0;k<w.length;k++){const S=iu(t,w[k]);if(S){const{transitionEnd:j,transition:N,...B}=S;for(const M in B){let L=B[M];if(Array.isArray(L)){const I=g?L.length-1:0;L=L[I]}L!==null&&(c[M]=L)}for(const M in j)c[M]=j[M]}}}return c}const Fg=t=>(s,i)=>{const o=P.useContext(Ia),c=P.useContext(zc),d=()=>oj(t,s,o,c);return i?d():sw(d)},cj=Fg({scrapeMotionValuesFromProps:fu,createRenderState:pu}),uj=Fg({scrapeMotionValuesFromProps:bg,createRenderState:Vg}),dj=Symbol.for("motionComponentSymbol");function hj(t,s,i){const o=P.useRef(i);P.useInsertionEffect(()=>{o.current=i});const c=P.useRef(null);return P.useCallback(d=>{var f;d&&((f=t.onMount)==null||f.call(t,d)),s&&(d?s.mount(d):s.unmount());const h=o.current;if(typeof h=="function")if(d){const p=h(d);typeof p=="function"&&(c.current=p)}else c.current?(c.current(),c.current=null):h(d);else h&&(h.current=d)},[s])}const Bg=P.createContext({});function Es(t){return t&&typeof t=="object"&&Object.prototype.hasOwnProperty.call(t,"current")}function mj(t,s,i,o,c,d){var L,I;const{visualElement:h}=P.useContext(Ia),f=P.useContext(Rg),p=P.useContext(zc),v=P.useContext(Dg),g=v.reducedMotion,x=v.skipAnimations,w=P.useRef(null),k=P.useRef(!1);o=o||f.renderer,!w.current&&o&&(w.current=o(t,{visualState:s,parent:h,props:i,presenceContext:p,blockInitialAnimation:p?p.initial===!1:!1,reducedMotionConfig:g,skipAnimations:x,isSVG:d}),k.current&&w.current&&(w.current.manuallyAnimateOnMount=!0));const S=w.current,j=P.useContext(Bg);S&&!S.projection&&c&&(S.type==="html"||S.type==="svg")&&fj(w.current,i,c,j);const N=P.useRef(!1);P.useInsertionEffect(()=>{S&&N.current&&S.update(i,p)});const B=i[Zp],M=P.useRef(!!B&&typeof window<"u"&&!((L=window.MotionHandoffIsComplete)!=null&&L.call(window,B))&&((I=window.MotionHasOptimisedAnimation)==null?void 0:I.call(window,B)));return iw(()=>{k.current=!0,S&&(N.current=!0,window.MotionIsMounted=!0,S.updateFeatures(),S.scheduleRenderMicrotask(),M.current&&S.animationState&&S.animationState.animateChanges())}),P.useEffect(()=>{S&&(!M.current&&S.animationState&&S.animationState.animateChanges(),M.current&&(queueMicrotask(()=>{var D;(D=window.MotionHandoffMarkAsComplete)==null||D.call(window,B)}),M.current=!1),S.enteringChildren=void 0)}),S}function fj(t,s,i,o){const{layoutId:c,layout:d,drag:h,dragConstraints:f,layoutScroll:p,layoutRoot:v,layoutAnchor:g,layoutCrossfade:x}=s;t.projection=new i(t.latestValues,s["data-framer-portal-id"]?void 0:Og(t.parent)),t.projection.setOptions({layoutId:c,layout:d,alwaysMeasureLayout:!!h||f&&Es(f),visualElement:t,animationType:typeof d=="string"?d:"both",initialPromotionConfig:o,crossfade:x,layoutScroll:p,layoutRoot:v,layoutAnchor:g})}function Og(t){if(t)return t.options.allowProjection!==!1?t.projection:Og(t.parent)}function Zl(t,{forwardMotionProps:s=!1,type:i}={},o,c){o&&Yk(o);const d=i?i==="svg":gu(t),h=d?uj:cj;function f(v,g){let x;const w={...P.useContext(Dg),...v,layoutId:pj(v)},{isStatic:k,isValidProp:S}=w,j=Qk(v),N=h(v,k);if(!k&&typeof window<"u"){gj();const B=yj(w);x=B.MeasureLayout,j.visualElement=mj(t,N,w,c,B.ProjectionNode,d)}return r.jsxs(Ia.Provider,{value:j,children:[x&&j.visualElement?r.jsx(x,{visualElement:j.visualElement,...w}):null,aj(t,v,hj(N,j.visualElement,g),N,k,s,d,S)]})}f.displayName=`motion.${typeof t=="string"?t:`create(${t.displayName??t.name??""})`}`;const p=P.forwardRef(f);return p[dj]=t,p}function pj({layoutId:t}){const s=P.useContext(cp).id;return s&&t!==void 0?s+"-"+t:t}function gj(t,s){P.useContext(Rg).strict}function yj(t){const s=Lg(),{drag:i,layout:o}=s;if(!i&&!o)return{};const c={...i,...o};return{MeasureLayout:i!=null&&i.isEnabled(t)||o!=null&&o.isEnabled(t)?c.MeasureLayout:void 0,ProjectionNode:c.ProjectionNode}}function vj(t,s){if(typeof Proxy>"u")return Zl;const i=new Map,o=(d,h)=>Zl(d,h,t,s),c=(d,h)=>o(d,h);return new Proxy(c,{get:(d,h)=>h==="create"?o:(i.has(h)||i.set(h,Zl(h,void 0,t,s)),i.get(h))})}const xj=(t,s)=>s.isSVG??gu(t)?new ek(s):new J0(s,{allowProjection:t!==P.Fragment});class wj extends An{constructor(s){super(s),s.animationState||(s.animationState=ik(s))}updateAnimationControlsSubscription(){const{animate:s}=this.node.getProps();Ra(s)&&(this.unmountControls=s.subscribe(this.node))}mount(){this.updateAnimationControlsSubscription()}update(){const{animate:s}=this.node.getProps(),{animate:i}=this.node.prevProps||{};s!==i&&this.updateAnimationControlsSubscription()}unmount(){var s;this.node.animationState.reset(),(s=this.unmountControls)==null||s.call(this)}}let bj=0;class kj extends An{constructor(){super(...arguments),this.id=bj++,this.isExitComplete=!1}update(){var d;if(!this.node.presenceContext)return;const{isPresent:s,onExitComplete:i}=this.node.presenceContext,{isPresent:o}=this.node.prevPresenceContext||{};if(!this.node.animationState||s===o)return;if(s&&o===!1){if(this.isExitComplete){const{initial:h,custom:f}=this.node.getProps();if(typeof h=="string"||typeof h=="object"&&h!==null&&!Array.isArray(h)){const p=ts(this.node,h,f);if(p){const{transition:v,transitionEnd:g,...x}=p;for(const w in x)(d=this.node.getValue(w))==null||d.jump(x[w])}}this.node.animationState.reset(),this.node.animationState.animateChanges()}else this.node.animationState.setActive("exit",!1);this.isExitComplete=!1;return}const c=this.node.animationState.setActive("exit",!s);i&&!s&&c.then(()=>{this.isExitComplete=!0,i(this.id)})}mount(){const{register:s,onExitComplete:i}=this.node.presenceContext||{};i&&i(this.id),s&&(this.unmount=s(this.id))}unmount(){}}const jj={animation:{Feature:wj},exit:{Feature:kj}};function Fr(t){return{point:{x:t.pageX,y:t.pageY}}}const Sj=t=>s=>du(s)&&t(s,Fr(s));function Pr(t,s,i,o){return Dr(t,s,Sj(i),o)}const zg=({current:t})=>t?t.ownerDocument.defaultView:null,Bf=(t,s)=>Math.abs(t-s);function Nj(t,s){const i=Bf(t.x,s.x),o=Bf(t.y,s.y);return Math.sqrt(i**2+o**2)}const Of=new Set(["auto","scroll"]);class Ug{constructor(s,i,{transformPagePoint:o,contextWindow:c=window,dragSnapToOrigin:d=!1,distanceThreshold:h=3,element:f}={}){if(this.startEvent=null,this.lastMoveEvent=null,this.lastMoveEventInfo=null,this.lastRawMoveEventInfo=null,this.handlers={},this.contextWindow=window,this.scrollPositions=new Map,this.removeScrollListeners=null,this.onElementScroll=S=>{this.handleScroll(S.target)},this.onWindowScroll=()=>{this.handleScroll(window)},this.updatePoint=()=>{if(!(this.lastMoveEvent&&this.lastMoveEventInfo))return;this.lastRawMoveEventInfo&&(this.lastMoveEventInfo=ea(this.lastRawMoveEventInfo,this.transformPagePoint));const S=ec(this.lastMoveEventInfo,this.history),j=this.startEvent!==null,N=Nj(S.offset,{x:0,y:0})>=this.distanceThreshold;if(!j&&!N)return;const{point:B}=S,{timestamp:M}=$e;this.history.push({...B,timestamp:M});const{onStart:L,onMove:I}=this.handlers;j||(L&&L(this.lastMoveEvent,S),this.startEvent=this.lastMoveEvent),I&&I(this.lastMoveEvent,S)},this.handlePointerMove=(S,j)=>{this.lastMoveEvent=S,this.lastRawMoveEventInfo=j,this.lastMoveEventInfo=ea(j,this.transformPagePoint),je.update(this.updatePoint,!0)},this.handlePointerUp=(S,j)=>{this.end();const{onEnd:N,onSessionEnd:B,resumeAnimation:M}=this.handlers;if((this.dragSnapToOrigin||!this.startEvent)&&M&&M(),!(this.lastMoveEvent&&this.lastMoveEventInfo))return;const L=ec(S.type==="pointercancel"?this.lastMoveEventInfo:ea(j,this.transformPagePoint),this.history);this.startEvent&&N&&N(S,L),B&&B(S,L)},!du(s))return;this.dragSnapToOrigin=d,this.handlers=i,this.transformPagePoint=o,this.distanceThreshold=h,this.contextWindow=c||window;const p=Fr(s),v=ea(p,this.transformPagePoint),{point:g}=v,{timestamp:x}=$e;this.history=[{...g,timestamp:x}];const{onSessionStart:w}=i;w&&w(s,ec(v,this.history));const k={passive:!0,capture:!0};this.removeListeners=Lr(Pr(this.contextWindow,"pointermove",this.handlePointerMove,k),Pr(this.contextWindow,"pointerup",this.handlePointerUp,k),Pr(this.contextWindow,"pointercancel",this.handlePointerUp,k)),f&&this.startScrollTracking(f)}startScrollTracking(s){let i=s.parentElement;for(;i;){const o=getComputedStyle(i);(Of.has(o.overflowX)||Of.has(o.overflowY))&&this.scrollPositions.set(i,{x:i.scrollLeft,y:i.scrollTop}),i=i.parentElement}this.scrollPositions.set(window,{x:window.scrollX,y:window.scrollY}),window.addEventListener("scroll",this.onElementScroll,{capture:!0}),window.addEventListener("scroll",this.onWindowScroll),this.removeScrollListeners=()=>{window.removeEventListener("scroll",this.onElementScroll,{capture:!0}),window.removeEventListener("scroll",this.onWindowScroll)}}handleScroll(s){const i=this.scrollPositions.get(s);if(!i)return;const o=s===window,c=o?{x:window.scrollX,y:window.scrollY}:{x:s.scrollLeft,y:s.scrollTop},d={x:c.x-i.x,y:c.y-i.y};d.x===0&&d.y===0||(o?this.lastMoveEventInfo&&(this.lastMoveEventInfo.point.x+=d.x,this.lastMoveEventInfo.point.y+=d.y):this.history.length>0&&(this.history[0].x-=d.x,this.history[0].y-=d.y),this.scrollPositions.set(s,c),je.update(this.updatePoint,!0))}updateHandlers(s){this.handlers=s}end(){this.removeListeners&&this.removeListeners(),this.removeScrollListeners&&this.removeScrollListeners(),this.scrollPositions.clear(),Mn(this.updatePoint)}}function ea(t,s){return s?{point:s(t.point)}:t}function zf(t,s){return{x:t.x-s.x,y:t.y-s.y}}function ec({point:t},s){return{point:t,delta:zf(t,Wg(s)),offset:zf(t,Cj(s)),velocity:Tj(s,.1)}}function Cj(t){return t[0]}function Wg(t){return t[t.length-1]}function Tj(t,s){if(t.length<2)return{x:0,y:0};let i=t.length-1,o=null;const c=Wg(t);for(;i>=0&&(o=t[i],!(c.timestamp-o.timestamp>Mt(s)));)i--;if(!o)return{x:0,y:0};o===t[0]&&t.length>2&&c.timestamp-o.timestamp>Mt(s)*2&&(o=t[1]);const d=kt(c.timestamp-o.timestamp);if(d===0)return{x:0,y:0};const h={x:(c.x-o.x)/d,y:(c.y-o.y)/d};return h.x===1/0&&(h.x=0),h.y===1/0&&(h.y=0),h}function Pj(t,{min:s,max:i},o){return s!==void 0&&t<s?t=o?ke(s,t,o.min):Math.max(t,s):i!==void 0&&t>i&&(t=o?ke(i,t,o.max):Math.min(t,i)),t}function Uf(t,s,i){return{min:s!==void 0?t.min+s:void 0,max:i!==void 0?t.max+i-(t.max-t.min):void 0}}function Ej(t,{top:s,left:i,bottom:o,right:c}){return{x:Uf(t.x,i,c),y:Uf(t.y,s,o)}}function Wf(t,s){let i=s.min-t.min,o=s.max-t.max;return s.max-s.min<t.max-t.min&&([i,o]=[o,i]),{min:i,max:o}}function Mj(t,s){return{x:Wf(t.x,s.x),y:Wf(t.y,s.y)}}function Aj(t,s){let i=.5;const o=ct(t),c=ct(s);return c>o?i=Er(s.min,s.max-o,t.min):o>c&&(i=Er(t.min,t.max-c,s.min)),Ut(0,1,i)}function _j(t,s){const i={};return s.min!==void 0&&(i.min=s.min-t.min),s.max!==void 0&&(i.max=s.max-t.min),i}const Vc=.35;function Dj(t=Vc){return t===!1?t=0:t===!0&&(t=Vc),{x:$f(t,"left","right"),y:$f(t,"top","bottom")}}function $f(t,s,i){return{min:Hf(t,s),max:Hf(t,i)}}function Hf(t,s){return typeof t=="number"?t:t[s]||0}const Rj=new WeakMap;class Lj{constructor(s){this.openDragLock=null,this.isDragging=!1,this.currentDirection=null,this.originPoint={x:0,y:0},this.constraints=!1,this.hasMutatedConstraints=!1,this.elastic=We(),this.latestPointerEvent=null,this.latestPanInfo=null,this.visualElement=s}start(s,{snapToCursor:i=!1,distanceThreshold:o}={}){const{presenceContext:c}=this.visualElement;if(c&&c.isPresent===!1)return;const d=x=>{i&&this.snapToCursor(Fr(x).point),this.stopAnimation()},h=(x,w)=>{const{drag:k,dragPropagation:S,onDragStart:j}=this.getProps();if(k&&!S&&(this.openDragLock&&this.openDragLock(),this.openDragLock=T0(k),!this.openDragLock))return;this.latestPointerEvent=x,this.latestPanInfo=w,this.isDragging=!0,this.currentDirection=null,this.resolveConstraints(),this.visualElement.projection&&(this.visualElement.projection.isAnimationBlocked=!0,this.visualElement.projection.target=void 0),Xt(B=>{let M=this.getAxisMotionValue(B).get()||0;if(Qt.test(M)){const{projection:L}=this.visualElement;if(L&&L.layout){const I=L.layout.layoutBox[B];I&&(M=ct(I)*(parseFloat(M)/100))}}this.originPoint[B]=M}),j&&je.update(()=>j(x,w),!1,!0),Mc(this.visualElement,"transform");const{animationState:N}=this.visualElement;N&&N.setActive("whileDrag",!0)},f=(x,w)=>{this.latestPointerEvent=x,this.latestPanInfo=w;const{dragPropagation:k,dragDirectionLock:S,onDirectionLock:j,onDrag:N}=this.getProps();if(!k&&!this.openDragLock)return;const{offset:B}=w;if(S&&this.currentDirection===null){this.currentDirection=Vj(B),this.currentDirection!==null&&j&&j(this.currentDirection);return}this.updateAxis("x",w.point,B),this.updateAxis("y",w.point,B),this.visualElement.render(),N&&je.update(()=>N(x,w),!1,!0)},p=(x,w)=>{this.latestPointerEvent=x,this.latestPanInfo=w,this.stop(x,w),this.latestPointerEvent=null,this.latestPanInfo=null},v=()=>{const{dragSnapToOrigin:x}=this.getProps();(x||this.constraints)&&this.startAnimation({x:0,y:0})},{dragSnapToOrigin:g}=this.getProps();this.panSession=new Ug(s,{onSessionStart:d,onStart:h,onMove:f,onSessionEnd:p,resumeAnimation:v},{transformPagePoint:this.visualElement.getTransformPagePoint(),dragSnapToOrigin:g,distanceThreshold:o,contextWindow:zg(this.visualElement),element:this.visualElement.current})}stop(s,i){const o=s||this.latestPointerEvent,c=i||this.latestPanInfo,d=this.isDragging;if(this.cancel(),!d||!c||!o)return;const{velocity:h}=c;this.startAnimation(h);const{onDragEnd:f}=this.getProps();f&&je.postRender(()=>f(o,c))}cancel(){this.isDragging=!1;const{projection:s,animationState:i}=this.visualElement;s&&(s.isAnimationBlocked=!1),this.endPanSession();const{dragPropagation:o}=this.getProps();!o&&this.openDragLock&&(this.openDragLock(),this.openDragLock=null),i&&i.setActive("whileDrag",!1)}endPanSession(){this.panSession&&this.panSession.end(),this.panSession=void 0}updateAxis(s,i,o){const{drag:c}=this.getProps();if(!o||!ta(s,c,this.currentDirection))return;const d=this.getAxisMotionValue(s);let h=this.originPoint[s]+o[s];this.constraints&&this.constraints[s]&&(h=Pj(h,this.constraints[s],this.elastic[s])),d.set(h)}resolveConstraints(){var d;const{dragConstraints:s,dragElastic:i}=this.getProps(),o=this.visualElement.projection&&!this.visualElement.projection.layout?this.visualElement.projection.measure(!1):(d=this.visualElement.projection)==null?void 0:d.layout,c=this.constraints;s&&Es(s)?this.constraints||(this.constraints=this.resolveRefConstraints()):s&&o?this.constraints=Ej(o.layoutBox,s):this.constraints=!1,this.elastic=Dj(i),c!==this.constraints&&!Es(s)&&o&&this.constraints&&!this.hasMutatedConstraints&&Xt(h=>{this.constraints!==!1&&this.getAxisMotionValue(h)&&(this.constraints[h]=_j(o.layoutBox[h],this.constraints[h]))})}resolveRefConstraints(){const{dragConstraints:s,onMeasureDragConstraints:i}=this.getProps();if(!s||!Es(s))return!1;const o=s.current,{projection:c}=this.visualElement;if(!c||!c.layout)return!1;c.root&&(c.root.scroll=void 0,c.root.updateScroll());const d=C0(o,c.root,this.visualElement.getTransformPagePoint());let h=Mj(c.layout.layoutBox,d);if(i){const f=i(j0(h));this.hasMutatedConstraints=!!f,f&&(h=ig(f))}return h}startAnimation(s){const{drag:i,dragMomentum:o,dragElastic:c,dragTransition:d,dragSnapToOrigin:h,onDragTransitionEnd:f}=this.getProps(),p=this.constraints||{},v=Xt(g=>{if(!ta(g,i,this.currentDirection))return;let x=p&&p[g]||{};(h===!0||h===g)&&(x={min:0,max:0});const w=c?200:1e6,k=c?40:1e7,S={type:"inertia",velocity:o?s[g]:0,bounceStiffness:w,bounceDamping:k,timeConstant:750,restDelta:1,restSpeed:10,...d,...x};return this.startAxisValueAnimation(g,S)});return Promise.all(v).then(f)}startAxisValueAnimation(s,i){const o=this.getAxisMotionValue(s);return Mc(this.visualElement,s),o.start(ru(s,o,0,i,this.visualElement,!1))}stopAnimation(){Xt(s=>this.getAxisMotionValue(s).stop())}getAxisMotionValue(s){const i=`_drag${s.toUpperCase()}`,c=this.visualElement.getProps()[i];return c||this.visualElement.getValue(s,this.visualElement.latestValues[s]??0)}snapToCursor(s){Xt(i=>{const{drag:o}=this.getProps();if(!ta(i,o,this.currentDirection))return;const{projection:c}=this.visualElement,d=this.getAxisMotionValue(i);if(c&&c.layout){const{min:h,max:f}=c.layout.layoutBox[i],p=d.get()||0;d.set(s[i]-ke(h,f,.5)+p)}})}scalePositionWithinConstraints(){if(!this.visualElement.current)return;const{drag:s,dragConstraints:i}=this.getProps(),{projection:o}=this.visualElement;if(!Es(i)||!o||!this.constraints)return;this.stopAnimation();const c={x:0,y:0};Xt(h=>{const f=this.getAxisMotionValue(h);if(f&&this.constraints!==!1){const p=f.get();c[h]=Aj({min:p,max:p},this.constraints[h])}});const{transformTemplate:d}=this.visualElement.getProps();this.visualElement.current.style.transform=d?d({},""):"none",o.root&&o.root.updateScroll(),o.updateLayout(),this.constraints=!1,this.resolveConstraints(),Xt(h=>{if(!ta(h,s,null))return;const f=this.getAxisMotionValue(h),{min:p,max:v}=this.constraints[h];f.set(ke(p,v,c[h]))}),this.visualElement.render()}addListeners(){if(!this.visualElement.current)return;Rj.set(this.visualElement,this);const s=this.visualElement.current,i=Pr(s,"pointerdown",v=>{const{drag:g,dragListener:x=!0}=this.getProps(),w=v.target,k=w!==s&&D0(w);g&&x&&!k&&this.start(v)});let o;const c=()=>{const{dragConstraints:v}=this.getProps();Es(v)&&v.current&&(this.constraints=this.resolveRefConstraints(),o||(o=Ij(s,v.current,()=>this.scalePositionWithinConstraints())))},{projection:d}=this.visualElement,h=d.addEventListener("measure",c);d&&!d.layout&&(d.root&&d.root.updateScroll(),d.updateLayout()),je.read(c);const f=Dr(window,"resize",()=>this.scalePositionWithinConstraints()),p=d.addEventListener("didUpdate",(({delta:v,hasLayoutChanged:g})=>{this.isDragging&&g&&(Xt(x=>{const w=this.getAxisMotionValue(x);w&&(this.originPoint[x]+=v[x].translate,w.set(w.get()+v[x].translate))}),this.visualElement.render())}));return()=>{f(),i(),h(),p&&p(),o&&o()}}getProps(){const s=this.visualElement.getProps(),{drag:i=!1,dragDirectionLock:o=!1,dragPropagation:c=!1,dragConstraints:d=!1,dragElastic:h=Vc,dragMomentum:f=!0}=s;return{...s,drag:i,dragDirectionLock:o,dragPropagation:c,dragConstraints:d,dragElastic:h,dragMomentum:f}}}function Gf(t){let s=!0;return()=>{if(s){s=!1;return}t()}}function Ij(t,s,i){const o=of(t,Gf(i)),c=of(s,Gf(i));return()=>{o(),c()}}function ta(t,s,i){return(s===!0||s===t)&&(i===null||i===t)}function Vj(t,s=10){let i=null;return Math.abs(t.y)>s?i="y":Math.abs(t.x)>s&&(i="x"),i}class Fj extends An{constructor(s){super(s),this.removeGroupControls=Ot,this.removeListeners=Ot,this.controls=new Lj(s)}mount(){const{dragControls:s}=this.node.getProps();s&&(this.removeGroupControls=s.subscribe(this.controls)),this.removeListeners=this.controls.addListeners()||Ot}update(){const{dragControls:s}=this.node.getProps(),{dragControls:i}=this.node.prevProps||{};s!==i&&(this.removeGroupControls(),s&&(this.removeGroupControls=s.subscribe(this.controls)))}unmount(){this.removeGroupControls(),this.removeListeners(),this.controls.isDragging||this.controls.endPanSession()}}const tc=t=>(s,i)=>{t&&je.update(()=>t(s,i),!1,!0)};class Bj extends An{constructor(){super(...arguments),this.removePointerDownListener=Ot}onPointerDown(s){this.session=new Ug(s,this.createPanHandlers(),{transformPagePoint:this.node.getTransformPagePoint(),contextWindow:zg(this.node)})}createPanHandlers(){const{onPanSessionStart:s,onPanStart:i,onPan:o,onPanEnd:c}=this.node.getProps();return{onSessionStart:tc(s),onStart:tc(i),onMove:tc(o),onEnd:(d,h)=>{delete this.session,c&&je.postRender(()=>c(d,h))}}}mount(){this.removePointerDownListener=Pr(this.node.current,"pointerdown",s=>this.onPointerDown(s))}update(){this.session&&this.session.updateHandlers(this.createPanHandlers())}unmount(){this.removePointerDownListener(),this.session&&this.session.end()}}let nc=!1;class Oj extends P.Component{componentDidMount(){const{visualElement:s,layoutGroup:i,switchLayoutGroup:o,layoutId:c}=this.props,{projection:d}=s;d&&(i.group&&i.group.add(d),o&&o.register&&c&&o.register(d),nc&&d.root.didUpdate(),d.addEventListener("animationComplete",()=>{this.safeToRemove()}),d.setOptions({...d.options,layoutDependency:this.props.layoutDependency,onExitComplete:()=>this.safeToRemove()})),ha.hasEverUpdated=!0}getSnapshotBeforeUpdate(s){const{layoutDependency:i,visualElement:o,drag:c,isPresent:d}=this.props,{projection:h}=o;return h&&(h.isPresent=d,s.layoutDependency!==i&&h.setOptions({...h.options,layoutDependency:i}),nc=!0,c||s.layoutDependency!==i||i===void 0||s.isPresent!==d?h.willUpdate():this.safeToRemove(),s.isPresent!==d&&(d?h.promote():h.relegate()||je.postRender(()=>{const f=h.getStack();(!f||!f.members.length)&&this.safeToRemove()}))),null}componentDidUpdate(){const{visualElement:s,layoutAnchor:i}=this.props,{projection:o}=s;o&&(o.options.layoutAnchor=i,o.root.didUpdate(),uu.postRender(()=>{!o.currentAnimation&&o.isLead()&&this.safeToRemove()}))}componentWillUnmount(){const{visualElement:s,layoutGroup:i,switchLayoutGroup:o}=this.props,{projection:c}=s;nc=!0,c&&(c.scheduleCheckAfterUnmount(),i&&i.group&&i.group.remove(c),o&&o.deregister&&o.deregister(c))}safeToRemove(){const{safeToRemove:s}=this.props;s&&s()}render(){return null}}function $g(t){const[s,i]=Kk(),o=P.useContext(cp);return r.jsx(Oj,{...t,layoutGroup:o,switchLayoutGroup:P.useContext(Bg),isPresent:s,safeToRemove:i})}const zj={pan:{Feature:Bj},drag:{Feature:Fj,ProjectionNode:_g,MeasureLayout:$g}};function Kf(t,s,i){const{props:o}=t;t.animationState&&o.whileHover&&t.animationState.setActive("whileHover",i==="Start");const c="onHover"+i,d=o[c];d&&je.postRender(()=>d(s,Fr(s)))}class Uj extends An{mount(){const{current:s}=this.node;s&&(this.unmount=E0(s,(i,o)=>(Kf(this.node,o,"Start"),c=>Kf(this.node,c,"End"))))}unmount(){}}class Wj extends An{constructor(){super(...arguments),this.isActive=!1}onFocus(){let s=!1;try{s=this.node.current.matches(":focus-visible")}catch{s=!0}!s||!this.node.animationState||(this.node.animationState.setActive("whileFocus",!0),this.isActive=!0)}onBlur(){!this.isActive||!this.node.animationState||(this.node.animationState.setActive("whileFocus",!1),this.isActive=!1)}mount(){this.unmount=Lr(Dr(this.node.current,"focus",()=>this.onFocus()),Dr(this.node.current,"blur",()=>this.onBlur()))}unmount(){}}function Xf(t,s,i){const{props:o}=t;if(t.current instanceof HTMLButtonElement&&t.current.disabled)return;t.animationState&&o.whileTap&&t.animationState.setActive("whileTap",i==="Start");const c="onTap"+(i==="End"?"":i),d=o[c];d&&je.postRender(()=>d(s,Fr(s)))}class $j extends An{mount(){const{current:s}=this.node;if(!s)return;const{globalTapTarget:i,propagate:o}=this.node.props;this.unmount=L0(s,(c,d)=>(Xf(this.node,d,"Start"),(h,{success:f})=>Xf(this.node,h,f?"End":"Cancel")),{useGlobalTarget:i,stopPropagation:(o==null?void 0:o.tap)===!1})}unmount(){}}const Fc=new WeakMap,sc=new WeakMap,Hj=t=>{const s=Fc.get(t.target);s&&s(t)},Gj=t=>{t.forEach(Hj)};function Kj({root:t,...s}){const i=t||document;sc.has(i)||sc.set(i,{});const o=sc.get(i),c=JSON.stringify(s);return o[c]||(o[c]=new IntersectionObserver(Gj,{root:t,...s})),o[c]}function Xj(t,s,i){const o=Kj(s);return Fc.set(t,i),o.observe(t),()=>{Fc.delete(t),o.unobserve(t)}}const Yj={some:0,all:1};class qj extends An{constructor(){super(...arguments),this.hasEnteredView=!1,this.isInView=!1}startObserver(){var p;(p=this.stopObserver)==null||p.call(this);const{viewport:s={}}=this.node.getProps(),{root:i,margin:o,amount:c="some",once:d}=s,h={root:i?i.current:void 0,rootMargin:o,threshold:typeof c=="number"?c:Yj[c]},f=v=>{const{isIntersecting:g}=v;if(this.isInView===g||(this.isInView=g,d&&!g&&this.hasEnteredView))return;g&&(this.hasEnteredView=!0),this.node.animationState&&this.node.animationState.setActive("whileInView",g);const{onViewportEnter:x,onViewportLeave:w}=this.node.getProps(),k=g?x:w;k&&k(v)};this.stopObserver=Xj(this.node.current,h,f)}mount(){this.startObserver()}update(){if(typeof IntersectionObserver>"u")return;const{props:s,prevProps:i}=this.node;["amount","margin","root"].some(Qj(s,i))&&this.startObserver()}unmount(){var s;(s=this.stopObserver)==null||s.call(this),this.hasEnteredView=!1,this.isInView=!1}}function Qj({viewport:t={}},{viewport:s={}}={}){return i=>t[i]!==s[i]}const Jj={inView:{Feature:qj},tap:{Feature:$j},focus:{Feature:Wj},hover:{Feature:Uj}},Zj={layout:{ProjectionNode:_g,MeasureLayout:$g}},e1={...jj,...Jj,...zj,...Zj},t1=vj(e1,xj);function n1(){!mu.current&&fg();const[t]=P.useState(Na.current);return t}const Yf=t1,s1={type:"spring",stiffness:620,damping:42,mass:.35},r1={type:"spring",stiffness:460,damping:38,mass:.8},i1=typeof window>"u"?P.useEffect:P.useLayoutEffect;function a1({items:t,value:s,defaultValue:i,onValueChange:o,activation:c="automatic"}){const d=P.useId(),h=P.useRef(new Map),f=P.useRef(1),[p,v]=P.useState(()=>{var M,L;return i??((M=t.find(I=>!I.disabled))==null?void 0:M.value)??((L=t[0])==null?void 0:L.value)??""}),g=s??p,x=P.useRef(o);x.current=o;const w=P.useCallback(M=>{var D;if(M===g||!t.some(F=>F.value===M&&!F.disabled))return;const L=t.findIndex(F=>F.value===g),I=t.findIndex(F=>F.value===M);f.current=I<L?-1:1,s===void 0&&v(M),(D=x.current)==null||D.call(x,M)},[s,t,g]),k=P.useCallback(M=>{var I;const L=t[M];L&&((I=h.current.get(L.value))==null||I.focus())},[t]),S=P.useCallback((M,L)=>{const I=t.length;if(!I)return 0;let D=M;for(let F=0;F<I;F+=1)if(D=(D+L+I)%I,!t[D].disabled)return D;return M},[t]),j=P.useCallback(M=>{const L=t.map((I,D)=>D);return M&&L.reverse(),L.find(I=>!t[I].disabled)??0},[t]),N=P.useCallback((M,L)=>({id:`${d}-tab-${M.value}`,role:"tab",type:"button","aria-selected":M.value===g,"aria-controls":`${d}-panel-${M.value}`,"aria-disabled":M.disabled?!0:void 0,tabIndex:M.value===g?0:-1,ref:I=>{I?h.current.set(M.value,I):h.current.delete(M.value)},onClick:()=>{M.disabled||w(M.value)},onKeyDown:I=>{if(I.key==="ArrowRight"||I.key==="ArrowLeft"){I.preventDefault();const D=S(L,I.key==="ArrowRight"?1:-1);k(D),c==="automatic"&&w(t[D].value)}else if(I.key==="Home"||I.key==="End"){I.preventDefault();const D=j(I.key==="End");k(D),c==="automatic"&&w(t[D].value)}else(I.key==="Enter"||I.key===" ")&&(I.preventDefault(),M.disabled||w(M.value))}}),[c,d,j,k,t,S,w,g]),B=P.useCallback(M=>({id:`${d}-panel-${M}`,role:"tabpanel","aria-labelledby":`${d}-tab-${M}`,tabIndex:0}),[d]);return{value:g,select:w,direction:f.current,tabListProps:{role:"tablist","aria-orientation":"horizontal"},getTabProps:N,getPanelProps:B}}function o1({items:t,value:s,defaultValue:i,onValueChange:o,activation:c="automatic",renderPanel:d,label:h="Tabs",panelClassName:f="",className:p=""}){const v=a1({items:t,value:s,defaultValue:i,onValueChange:o,activation:c}),g=n1(),x=P.useRef(null),w=P.useRef([]),[k,S]=P.useState({x:0,width:0,ready:!1}),j=t.findIndex(N=>N.value===v.value);return i1(()=>{const N=w.current[j],B=x.current;if(!N||!B)return;const M=()=>S(I=>I.x===N.offsetLeft&&I.width===N.offsetWidth&&I.ready?I:{x:N.offsetLeft,width:N.offsetWidth,ready:!0});M();const L=new ResizeObserver(M);return L.observe(B),()=>L.disconnect()},[t,j]),r.jsxs("div",{className:`stats-tabs ${p}`,children:[r.jsxs("div",{...v.tabListProps,ref:x,"aria-label":h,className:"stats-tabs-list",children:[r.jsx(Yf.span,{layout:!0,"aria-hidden":"true",className:"stats-tabs-indicator",style:{left:k.x,width:k.width,opacity:k.ready?1:0},transition:g?{duration:0}:s1}),t.map((N,B)=>{const M=N.value===v.value,{ref:L,...I}=v.getTabProps(N,B);return r.jsx("button",{...I,ref:D=>{L(D),w.current[B]=D},className:`stats-tab${M?" selected":""}${N.disabled?" disabled":""}`,children:N.label},N.value)})]}),d&&r.jsx(Yf.div,{custom:v.direction,...v.getPanelProps(v.value),initial:g?!1:{opacity:0,x:v.direction*12},animate:{opacity:1,x:0},transition:g?{duration:0}:r1,className:`stats-tab-panel ${f}`,children:d(v.value)},v.value)]})}const l1=[{value:"messages",label:"Messages"},{value:"members",label:"Members"},{value:"layout",label:"Server layout"}];function Hg(t){return new Intl.DateTimeFormat(void 0,{weekday:"short"}).format(new Date(`${t}T12:00:00`))}function c1({stats:t}){const s=t.activity.map(d=>d.messages),i=Math.max(1,...s),o=s.map((d,h)=>{const f=s.length>1?12+h*276/(s.length-1):150,p=102-d/i*78;return`${f},${p}`}).join(" "),c=`12,104 ${o} 288,104`;return r.jsxs("div",{className:"server-chart-wrap",children:[r.jsxs("div",{className:"server-chart-heading",children:[r.jsxs("div",{children:[r.jsx("span",{children:"Daily messages"}),r.jsx("strong",{children:ve(s.reduce((d,h)=>d+h,0))})]}),r.jsx("small",{children:"Last 14 days"})]}),r.jsxs("svg",{className:"server-line-chart",viewBox:"0 0 300 122",role:"img","aria-label":"Daily messages over the last fourteen days",children:[r.jsx("defs",{children:r.jsxs("linearGradient",{id:"message-area-fill",x1:"0",x2:"0",y1:"0",y2:"1",children:[r.jsx("stop",{offset:"0%",stopColor:"var(--accent)",stopOpacity:".24"}),r.jsx("stop",{offset:"100%",stopColor:"var(--accent)",stopOpacity:"0"})]})}),[24,50,76,104].map(d=>r.jsx("line",{x1:"12",x2:"288",y1:d,y2:d,className:"server-chart-gridline"},d)),r.jsx("polygon",{points:c,fill:"url(#message-area-fill)"}),r.jsx("polyline",{points:o,className:"server-chart-line"}),t.activity.map((d,h)=>{const f=s.length>1?12+h*276/(s.length-1):150,p=102-d.messages/i*78;return r.jsx("circle",{cx:f,cy:p,r:"2.7",className:"server-chart-point",children:r.jsx("title",{children:`${d.date}: ${ve(d.messages)} messages`})},d.date)})]}),r.jsx("div",{className:"server-chart-days",children:t.activity.filter((d,h)=>h%2===0).map(d=>r.jsx("span",{children:Hg(d.date)},d.date))})]})}function u1({stats:t}){const s=Math.max(1,...t.activity.flatMap(i=>[i.joins,i.leaves]));return r.jsxs("div",{className:"server-chart-wrap",children:[r.jsxs("div",{className:"server-chart-heading",children:[r.jsxs("div",{children:[r.jsx("span",{children:"Member changes"}),r.jsxs("strong",{children:[ve(t.activity.reduce((i,o)=>i+o.joins,0))," joined"]})]}),r.jsx("small",{children:"Last 14 days"})]}),r.jsx("div",{className:"server-member-chart",role:"img","aria-label":"Daily member joins and departures over the last fourteen days",children:t.activity.map(i=>r.jsxs("div",{className:"server-member-day",title:`${i.date}: ${i.joins} joined, ${i.leaves} left`,children:[r.jsxs("div",{className:"server-member-bars",children:[r.jsx("i",{className:"join-bar",style:{height:`${Math.max(i.joins?5:0,i.joins/s*76)}%`}}),r.jsx("i",{className:"leave-bar",style:{height:`${Math.max(i.leaves?5:0,i.leaves/s*76)}%`}})]}),r.jsx("span",{children:Hg(i.date).slice(0,1)})]},i.date))}),r.jsxs("div",{className:"server-chart-legend",children:[r.jsxs("span",{children:[r.jsx("i",{className:"join-key"})," Joined ",r.jsx("b",{children:ve(t.activity.reduce((i,o)=>i+o.joins,0))})]}),r.jsxs("span",{children:[r.jsx("i",{className:"leave-key"})," Left ",r.jsx("b",{children:ve(t.activity.reduce((i,o)=>i+o.leaves,0))})]})]})]})}function d1({stats:t}){const s=Math.max(t.member_count,t.channel_count,t.role_count,1),i=[{label:"Members",value:t.member_count,color:"members"},{label:"Channels",value:t.channel_count,color:"channels"},{label:"Roles",value:t.role_count,color:"roles"}];return r.jsxs("div",{className:"server-layout-chart",children:[r.jsxs("div",{className:"server-layout-total",children:[r.jsx("span",{children:"Community size"}),r.jsx("strong",{children:ve(t.member_count)}),r.jsx("small",{children:"members currently in this server"})]}),r.jsx("div",{className:"server-layout-bars",children:i.map(o=>r.jsxs("div",{className:"server-layout-row",children:[r.jsxs("div",{children:[r.jsx("span",{children:o.label}),r.jsx("strong",{children:ve(o.value)})]}),r.jsx("div",{className:"server-layout-track",children:r.jsx("i",{className:`layout-${o.color}`,style:{width:`${Math.max(o.value?4:0,o.value/s*100)}%`}})})]},o.label))})]})}function h1({stats:t}){const[s,i]=P.useState("messages"),o=P.useMemo(()=>({messages:t.activity.reduce((d,h)=>d+h.messages,0),joins:t.activity.reduce((d,h)=>d+h.joins,0)}),[t.activity]),c=s==="members"?r.jsx(u1,{stats:t}):s==="layout"?r.jsx(d1,{stats:t}):r.jsx(c1,{stats:t});return r.jsxs("section",{className:"dash-panel server-stats-card","aria-label":"Server statistics",children:[r.jsxs("div",{className:"panel-heading server-stats-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Community analytics"}),r.jsx("h3",{children:"Server pulse"}),r.jsx("p",{children:"Daily activity tracked by Niko · last 14 days"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(Sx,{})})]}),r.jsxs("div",{className:"server-stat-metrics",children:[r.jsxs("div",{children:[r.jsx(hc,{}),r.jsx("span",{children:"Members"}),r.jsx("strong",{children:ve(t.member_count)})]}),r.jsxs("div",{children:[r.jsx(ia,{}),r.jsx("span",{children:"Messages · 14d"}),r.jsx("strong",{children:ve(o.messages)})]}),r.jsxs("div",{children:[r.jsx(_x,{}),r.jsx("span",{children:"New members · 14d"}),r.jsx("strong",{children:ve(o.joins)})]})]}),r.jsx(o1,{items:l1,value:s,onValueChange:i,label:"Server statistics",renderPanel:()=>c}),r.jsx("div",{className:"server-stats-footnote",children:"Activity is collected from the moment tracking is enabled."})]})}function _n({eyebrow:t,title:s,text:i}){return r.jsxs("div",{className:"dash-heading",children:[r.jsxs("div",{className:"heading-meta",children:[r.jsx("div",{className:"eyebrow",children:t}),r.jsx("span",{className:"heading-context",children:"NIKO / CONTROL ROOM"})]}),r.jsx("h2",{children:s}),r.jsx("p",{children:i})]})}function qt({label:t,value:s,note:i,accent:o=""}){return r.jsxs("div",{className:`dash-stat ${o}`,children:[r.jsx("span",{children:t}),r.jsx("strong",{children:s}),r.jsx("small",{children:i})]})}function m1({user:t,overview:s,guilds:i,onServers:o,onManage:c}){const d=i.filter(h=>h.installed!==!1);return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"Personal overview",title:"Your Niko snapshot.",text:"Keep an eye on your progress, then jump into a server when you’re ready to tune the room."}),r.jsxs("div",{className:"overview-intro",children:[r.jsxs("div",{className:"profile-card",children:[r.jsx(op,{user:t,className:"profile-avatar"}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Signed in as"}),r.jsx("h3",{children:ip(t)}),r.jsx("p",{children:"Personal economy profile"})]})]}),r.jsxs("button",{className:"button button-primary",onClick:o,children:["Manage a server ",r.jsx(ee,{name:"arrow"})]})]}),r.jsxs("div",{className:"dash-stats overview-stats",children:[r.jsx(qt,{label:"Net worth",value:ve(s==null?void 0:s.net_worth),note:"Across your Niko profile",accent:"accent-orange"}),r.jsx(qt,{label:"In your wallet",value:ve(s==null?void 0:s.balance),note:"Ready to spend",accent:"accent-violet"}),r.jsx(qt,{label:"In your vault",value:ve(s==null?void 0:s.bank),note:"Saved for later",accent:"accent-blue"}),r.jsx(qt,{label:"Current level",value:ve(s==null?void 0:s.level),note:s!=null&&s.job?`Working as a ${s.job}`:"Keep showing up",accent:"accent-green"})]}),r.jsxs("div",{className:"dash-columns overview-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Progress"}),r.jsx("h3",{children:"Your momentum"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(ee,{name:"spark"})})]}),r.jsxs("div",{className:"metric-list",children:[r.jsxs("div",{children:[r.jsx("span",{children:"Daily streak"}),r.jsxs("strong",{children:[ve(s==null?void 0:s.daily_streak)," ",r.jsx("small",{children:"days"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Achievements"}),r.jsxs("strong",{children:[ve(s==null?void 0:s.achievements)," ",r.jsx("small",{children:"unlocked"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Total earned"}),r.jsxs("strong",{children:[ve(s==null?void 0:s.total_earned)," ",r.jsx("small",{children:"coins"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Economy standing"}),r.jsxs("strong",{children:[s!=null&&s.economy_rank?`#${ve(s.economy_rank)}`:"—"," ",r.jsx("small",{children:s!=null&&s.economy_profiles?`of ${ve(s.economy_profiles)}`:""})]})]})]})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Quick access"}),r.jsx("h3",{children:"Your servers"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(ee,{name:"users"})})]}),r.jsxs("div",{className:"mini-server-list",children:[d.slice(0,4).map(h=>r.jsxs("button",{onClick:()=>c(h),children:[r.jsx(Oc,{guild:h}),r.jsx("span",{children:h.name}),r.jsx(ee,{name:"arrow"})]},h.id)),!d.length&&r.jsx("p",{className:"empty-state compact",children:"Add Niko to a server to start managing it."})]}),r.jsxs("button",{className:"text-link overview-link",onClick:o,children:["View all servers ",r.jsx(ee,{name:"arrow"})]})]})]})]})}function qf({guild:t,onManage:s}){const i=t.installed!==!1;return r.jsxs("article",{className:"server-card",children:[r.jsxs("div",{className:"server-card-heading",children:[r.jsx(Oc,{guild:t,className:"server-avatar"}),r.jsx("span",{className:"server-status",children:i?"Niko is installed":"Ready to add"})]}),r.jsx("h3",{children:t.name}),r.jsx("p",{children:i?"Open the dashboard to manage Niko’s features and settings.":"You have permission to manage this server. Add Niko to unlock its controls."}),i?r.jsxs("button",{className:"button button-muted button-small",onClick:()=>s(t),children:["Open settings ",r.jsx(ee,{name:"arrow"})]}):r.jsxs("a",{className:"button button-primary button-small",href:t.invite_url||"#",target:"_blank",rel:"noreferrer",children:["Add Niko ",r.jsx(ee,{name:"external"})]})]})}function f1({guilds:t,onManage:s}){const i=t.filter(c=>c.installed!==!1),o=t.filter(c=>c.installed===!1);return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"Servers",title:"Choose where to work.",text:"Manage servers with Niko already installed, or add Niko to another server you can administer."}),r.jsxs("div",{className:"server-summary",children:[r.jsxs("div",{children:[r.jsx("strong",{children:ve(i.length)}),r.jsx("span",{children:"Connected to Niko"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:ve(o.length)}),r.jsx("span",{children:"Ready to add"})]}),r.jsxs("div",{className:"server-summary-note",children:[r.jsx(ee,{name:"shield"}),r.jsx("span",{children:"Only servers where you have Manage Server access are shown."})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Connected"}),r.jsx("h3",{children:"Manage a server"})]}),r.jsx("span",{className:"section-count",children:i.length})]}),r.jsxs("div",{className:"server-grid",children:[i.map(c=>r.jsx(qf,{guild:c,onManage:s},c.id)),!i.length&&r.jsxs("div",{className:"empty-state",children:[r.jsx("strong",{children:"No connected servers yet."}),r.jsx("span",{children:"Add Niko below, then come back here to manage it."})]})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Available to you"}),r.jsx("h3",{children:"Add Niko to a server"})]}),r.jsx("span",{className:"section-count",children:o.length})]}),r.jsxs("div",{className:"server-grid",children:[o.map(c=>r.jsx(qf,{guild:c,onManage:s},c.id)),!o.length&&r.jsx("div",{className:"server-note",children:"Niko is already installed in every server you can manage."})]})]})]})}function Gg({rows:t}){return r.jsxs("div",{className:"rank-list",children:[t.slice(0,5).map((s,i)=>r.jsxs("div",{className:"rank-row",children:[r.jsx("span",{className:`rank rank-${i+1}`,children:String(i+1).padStart(2,"0")}),r.jsxs("span",{className:"rank-user",children:[r.jsx(tw,{name:s.display_name||s.username||"Unknown member",avatarUrl:s.avatar_url}),r.jsxs("span",{children:[r.jsx("strong",{children:s.display_name||s.username||"Unknown member"}),s.username&&s.display_name&&r.jsxs("small",{children:["@",s.username]})]})]}),r.jsxs("strong",{children:["Level ",ve(s.level),r.jsxs("small",{children:[ve(s.xp)," xp"]})]})]},`${s.user_id}-${i}`)),!t.length&&r.jsx("div",{className:"empty-state compact",children:"No data recorded yet."})]})}function p1({overview:t}){return r.jsxs(r.Fragment,{children:[r.jsxs("div",{className:"guild-welcome",children:[r.jsxs("div",{children:[r.jsx("span",{className:"welcome-mark",children:r.jsx(ee,{name:"grid"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server pulse"}),r.jsx("strong",{children:"Here’s what needs your attention."})]})]}),r.jsxs("span",{className:"welcome-time",children:["LIVE SIGNALS ",r.jsx("span",{className:"status-dot"})]})]}),r.jsx(_n,{eyebrow:"Overview",title:"A quick read on your room.",text:"The important signals, without making you hunt for them."}),r.jsxs("div",{className:"dash-stats guild-overview-stats",children:[r.jsx(qt,{label:"Warnings logged",value:ve(t.moderation.warn_count),note:"For this server",accent:"accent-blue"}),r.jsx(qt,{label:"Automod",value:t.moderation.automod_active?"Active":"Quiet",note:"Protection status",accent:"accent-green"}),r.jsx(qt,{label:"Level leaders",value:ve(t.leveling.top.length),note:"Members with recorded XP",accent:"accent-violet"})]}),r.jsx(h1,{stats:t.server}),r.jsxs("div",{className:"dash-columns overview-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Community energy"}),r.jsx("h3",{children:"Top XP"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(ee,{name:"spark"})})]}),r.jsx(Gg,{rows:t.leveling.top})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server controls"}),r.jsx("h3",{children:"Manage the room"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(ee,{name:"settings"})})]}),r.jsxs("div",{className:"server-controls-body",children:[r.jsx("p",{children:"Use Server settings for prefixes, welcome messages, logs, and ticket panels."}),r.jsxs("span",{className:"text-link",children:["Open server settings ",r.jsx(ee,{name:"arrow"})]})]})]})]})]})}function g1({rows:t,config:s,resources:i,csrfToken:o,guildId:c}){var d,h,f;return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"Leveling",title:"Momentum people can see.",text:"Track the members turning up, and tune the pace to fit your server."}),r.jsxs("div",{className:"dash-stats",children:[r.jsx(qt,{label:"Top level",value:String(((d=t[0])==null?void 0:d.level)||0),note:((h=t[0])==null?void 0:h.display_name)||((f=t[0])==null?void 0:f.username)||"No members yet",accent:"accent-violet"}),r.jsx(qt,{label:"XP multiplier",value:`${(s==null?void 0:s.leveling.xp_multiplier)||1}×`,note:(s==null?void 0:s.leveling.xp_enabled)===!1?"XP disabled":"Currently active",accent:"accent-blue"}),r.jsx(qt,{label:"Cooldown",value:`${(s==null?void 0:s.leveling.xp_cooldown)||0}s`,note:"Between XP awards",accent:"accent-green"})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Leaderboard"}),r.jsx("h3",{children:"XP leaders"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(ee,{name:"spark"})})]}),r.jsx(Gg,{rows:t})]}),r.jsx(w1,{guildId:c,config:s,resources:i,csrfToken:o})]})}const Va={saving:!1,message:"",error:""};function lt({label:t,hint:s,children:i}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:t}),i,s&&r.jsx("small",{children:s})]})}function y1(t,s){const i=s?String(s):"",o=(t==null?void 0:t.channels)||[];return!i||o.some(c=>String(c.id)===i)?o:[{id:i,name:`Saved channel · ${i}`},...o]}function Fa({icon:t,label:s,title:i,text:o,className:c}){return r.jsxs("div",{className:`settings-intro${c?` ${c}`:""}`,children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(ee,{name:t})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:s}),r.jsx("strong",{children:i}),r.jsx("p",{children:o})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]})}function ns({label:t,title:s,detail:i,icon:o}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:t}),r.jsx("h3",{children:s}),i&&r.jsx("p",{children:i})]}),o&&r.jsx("span",{className:"panel-icon",children:r.jsx(ee,{name:o})})]})}function Ba({state:t}){return r.jsxs("div",{className:"setting-footer",children:[t.error?r.jsx("span",{className:"form-error",role:"alert",children:t.error}):r.jsx("span",{role:"status",children:t.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:t.saving,children:t.saving?"Saving…":"Save changes"})]})}function v1({guildId:t,config:s,csrfToken:i}){var x,w,k;const[o,c]=P.useState({}),[d,h]=P.useState(Va);P.useEffect(()=>{const S=(s==null?void 0:s.moderation)||{};c({automod:{...S.automod||{}},spam_threshold:S.spam_threshold??6,spam_interval:S.spam_interval??7,max_mentions:S.max_mentions??5,antinuke:{...S.antinuke||{}},antiraid:{...S.antiraid||{}},antiraid_ext:{...S.antiraid_ext||{}}})},[s]);const f=(S,j,N)=>c(B=>({...B,[S]:{...B[S],[j]:N}})),p=S=>{S.preventDefault(),h({saving:!0,message:"",error:""}),Aa(t,"automod",o,i).then(j=>{const N=j.config||{};c({automod:{...N.automod||{}},spam_threshold:N.spam_threshold??6,spam_interval:N.spam_interval??7,max_mentions:N.max_mentions??5,antinuke:{...N.antinuke||{}},antiraid:{...N.antiraid||{}},antiraid_ext:{...N.antiraid_ext||{}}}),h({saving:!1,message:"Moderation settings saved to Niko.",error:""})}).catch(j=>h({saving:!1,message:"",error:j instanceof Error?j.message:"Could not save settings."}))},v=[["antispam","Anti-spam","Detect repeated messages"],["antilink","Invite links","Remove Discord invite links"],["badwords","Blocked words","Filter words from the server list"],["massmention","Mass mentions","Limit mention floods"],["antinuke","Anti-nuke","Protect channels and roles"],["antiraid","Join raid protection","React to sudden join waves"],["antiraid_ext","External app protection","Detect user-installed app abuse"]],g=v.filter(([S])=>{var j;return!!((j=o.automod)!=null&&j[S])}).length;return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"Moderation",title:"Keep the room feeling good.",text:"Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration."}),r.jsx(Fa,{icon:"shield",label:"Protection desk",title:`${g} of ${v.length} safeguards active`,text:"Start with the essentials, then tune thresholds below when you know the room’s rhythm."}),r.jsxs("form",{onSubmit:p,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ns,{label:"Protection rules",title:"AutoMod modules",detail:"Toggle only the responses you want Niko to handle.",icon:"shield"}),r.jsx("div",{className:"setting-list",children:v.map(([S,j,N])=>{var B;return r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:j}),r.jsx("small",{children:N})]}),r.jsx("input",{type:"checkbox",checked:!!((B=o.automod)!=null&&B[S]),onChange:M=>f("automod",S,M.target.checked)}),r.jsx("i",{"aria-hidden":"true"})]},S)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ns,{label:"Thresholds",title:"Choose when protection steps in",detail:"These limits apply across the server."}),r.jsxs("div",{className:"form-grid",children:[r.jsx(lt,{label:"Spam messages",hint:"Messages inside the spam interval",children:r.jsx("input",{type:"number",min:"1",max:"100",value:o.spam_threshold??6,onChange:S=>c({...o,spam_threshold:S.target.value})})}),r.jsx(lt,{label:"Spam interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:o.spam_interval??7,onChange:S=>c({...o,spam_interval:S.target.value})})}),r.jsx(lt,{label:"Maximum mentions",children:r.jsx("input",{type:"number",min:"1",max:"100",value:o.max_mentions??5,onChange:S=>c({...o,max_mentions:S.target.value})})}),r.jsx(lt,{label:"Anti-raid joins",hint:"Joins inside the join interval",children:r.jsx("input",{type:"number",min:"1",max:"1000",value:((x=o.antiraid)==null?void 0:x.join_threshold)??10,onChange:S=>f("antiraid","join_threshold",S.target.value)})}),r.jsx(lt,{label:"Anti-raid interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:((w=o.antiraid)==null?void 0:w.join_interval)??10,onChange:S=>f("antiraid","join_interval",S.target.value)})}),r.jsx(lt,{label:"Anti-raid action",children:r.jsxs("select",{value:((k=o.antiraid)==null?void 0:k.action)??"kick",onChange:S=>f("antiraid","action",S.target.value),children:[r.jsx("option",{value:"kick",children:"Kick"}),r.jsx("option",{value:"ban",children:"Ban"}),r.jsx("option",{value:"softban",children:"Soft-ban"}),r.jsx("option",{value:"slowmode",children:"Slowmode"}),r.jsx("option",{value:"lockdown",children:"Lockdown"})]})})]}),r.jsx(Ba,{state:d})]})]})]})}function x1({guildId:t,config:s,csrfToken:i}){var k,S;const[o,c]=P.useState({ai_name:"Niko",personality:"cafe",enabled:!0,ai_actions_experiment:!1,better_context_experiment:!1,multimodal_experiment:!1}),[d,h]=P.useState(Va),[f,p]=P.useState(null),v=j=>j===!0||j==="True",g=j=>c({ai_name:j.ai_name||"Niko",personality:j.personality==="normal"?"normal":"cafe",enabled:j.enabled!=="False"&&j.enabled!==!1,ai_actions_experiment:v(j.ai_actions_experiment),better_context_experiment:v(j.better_context_experiment),multimodal_experiment:v(j.multimodal_experiment)});P.useEffect(()=>g((s==null?void 0:s.ai)||{}),[s]);const x=j=>{j.preventDefault(),h({saving:!0,message:"",error:""}),Aa(t,"ai",o,i).then(N=>{g(N.config||{}),h({saving:!1,message:"AI settings saved.",error:""})}).catch(N=>h({saving:!1,message:"",error:N instanceof Error?N.message:"Could not save settings."}))},w=[{key:"better_context_experiment",title:"Better context",hint:"Use the last five channel messages",info:"Adds recent conversation and replied-to message context so responses understand ongoing discussions more naturally. It is useful for follow-ups, but sends more conversation context to the AI provider."},{key:"ai_actions_experiment",title:"AI actions",hint:"Allow confirmed actions requested in chat",info:"Lets the AI propose polls and server actions such as moderation or channel management. Every action requires confirmation and is still limited by Discord permissions."},{key:"multimodal_experiment",title:"Multimodal conversation",hint:"Understand images and transcribe voice messages",info:"Allows Niko to inspect image attachments and use voice-message transcriptions as context. Media is processed only while enabled and provider usage costs may apply."}];return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"AI controls",title:"Give your AI the right tone.",text:"Configure the AI identity, personality, and opt-in experiments for this server."}),r.jsx(Fa,{icon:"settings",label:"Conversation desk",title:o.enabled?`${o.ai_name} is ready to respond`:`${o.ai_name} is staying quiet`,text:"All settings apply only to this server."}),r.jsxs("form",{onSubmit:x,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ns,{label:"Conversation",title:"Core settings",detail:"Decide when the AI joins the conversation.",icon:"settings"}),r.jsx("div",{className:"form-grid",children:r.jsx(lt,{label:"AI name",hint:"1–32 characters; this is also the mention trigger",children:r.jsx("input",{value:o.ai_name,maxLength:32,onChange:j=>c({...o,ai_name:j.target.value})})})}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable AI chat"}),r.jsx("small",{children:"Respond when the configured name is mentioned"})]}),r.jsx("input",{type:"checkbox",checked:o.enabled,onChange:j=>c({...o,enabled:j.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"personality-options",children:[r.jsxs("button",{type:"button",className:o.personality==="cafe"?"personality active":"personality",onClick:()=>c({...o,personality:"cafe"}),children:[r.jsx("span",{className:"personality-mark",children:"n"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Café"}),r.jsx("small",{children:"Warm, playful, familiar"})]})]}),r.jsxs("button",{type:"button",className:o.personality==="normal"?"personality active":"personality",onClick:()=>c({...o,personality:"normal"}),children:[r.jsx("span",{className:"personality-mark",children:"—"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Normal"}),r.jsx("small",{children:"Clear and straightforward"})]})]})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ns,{label:"Experiments",title:"Optional capabilities",detail:"Each experiment includes a learn-more explanation before you enable it."}),w.map(j=>r.jsxs("div",{className:"setting-row experiment-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:j.title}),r.jsx("small",{children:j.hint})]}),r.jsxs("div",{className:"experiment-actions",children:[r.jsx("button",{type:"button",className:"button button-secondary",onClick:()=>p(j.key),children:"Learn more"}),r.jsxs("label",{className:"toggle-control","aria-label":`Enable ${j.title}`,children:[r.jsx("input",{type:"checkbox",checked:o[j.key],onChange:N=>c({...o,[j.key]:N.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]})]})]},j.key)),r.jsx(Ba,{state:d})]})]}),f&&r.jsx("div",{className:"modal-backdrop",role:"presentation",onClick:()=>p(null),children:r.jsxs("div",{className:"modal-card",role:"dialog","aria-modal":"true","aria-labelledby":"ai-experiment-title",onClick:j=>j.stopPropagation(),children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"AI experiment"}),r.jsx("h3",{id:"ai-experiment-title",children:(k=w.find(j=>j.key===f))==null?void 0:k.title})]}),r.jsx("button",{type:"button",className:"button button-secondary",onClick:()=>p(null),children:"Close"})]}),r.jsx("p",{children:(S=w.find(j=>j.key===f))==null?void 0:S.info})]})})]})}function w1({guildId:t,config:s,resources:i,csrfToken:o}){const c=(s==null?void 0:s.leveling)||{},[d,h]=P.useState({xp_enabled:!0,xp_multiplier:1,xp_cooldown:0,level_up_channel:"",level_up_message:""}),[f,p]=P.useState(Va);P.useEffect(()=>h({xp_enabled:c.xp_enabled!==!1,xp_multiplier:c.xp_multiplier??1,xp_cooldown:c.xp_cooldown??0,level_up_channel:c.level_up_channel?String(c.level_up_channel):"",level_up_message:c.level_up_message||""}),[s]);const v=x=>{x.preventDefault(),p({saving:!0,message:"",error:""}),Aa(t,"leveling",d,o).then(w=>{const k=w.config||{};h({xp_enabled:k.xp_enabled!==!1,xp_multiplier:k.xp_multiplier??1,xp_cooldown:k.xp_cooldown??0,level_up_channel:k.level_up_channel?String(k.level_up_channel):"",level_up_message:k.level_up_message||""}),p({saving:!1,message:"Leveling settings saved to Niko.",error:""})}).catch(w=>p({saving:!1,message:"",error:w instanceof Error?w.message:"Could not save settings."}))},g=y1(i,d.level_up_channel);return r.jsxs(r.Fragment,{children:[r.jsx(Fa,{className:"leveling-settings-intro",icon:"spark",label:"Participation desk",title:d.xp_enabled?"XP is flowing":"XP is paused",text:"Set a pace that rewards regulars without turning every message into a transaction."}),r.jsx("form",{onSubmit:v,className:"settings-stack",children:r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ns,{label:"Leveling settings",title:"Shape the pace",detail:"These controls apply to every member in this server.",icon:"spark"}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable XP"}),r.jsx("small",{children:"Track activity and award levels"})]}),r.jsx("input",{type:"checkbox",checked:d.xp_enabled,onChange:x=>h({...d,xp_enabled:x.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"form-grid",children:[r.jsx(lt,{label:"XP multiplier",hint:"From 0.1× to 10×",children:r.jsx("input",{type:"number",min:"0.1",max:"10",step:"0.1",value:d.xp_multiplier,onChange:x=>h({...d,xp_multiplier:x.target.value})})}),r.jsx(lt,{label:"Cooldown (seconds)",hint:"0 disables the cooldown",children:r.jsx("input",{type:"number",min:"0",max:"86400",value:d.xp_cooldown,onChange:x=>h({...d,xp_cooldown:x.target.value})})}),r.jsx(lt,{label:"Level-up channel",children:r.jsxs("select",{value:d.level_up_channel,onChange:x=>h({...d,level_up_channel:x.target.value}),children:[r.jsx("option",{value:"",children:"Same channel"}),g.map(x=>r.jsxs("option",{value:x.id,children:["#",x.name]},x.id))]})}),r.jsx(lt,{label:"Level-up message",hint:"Use {mention}, {level}, {name}, or {guild}",children:r.jsx("textarea",{rows:3,maxLength:1e3,value:d.level_up_message,onChange:x=>h({...d,level_up_message:x.target.value}),placeholder:"Leave blank for Niko's default message"})})]}),r.jsx(Ba,{state:f})]})})]})}function b1({guildId:t,config:s,csrfToken:i}){var v;const o=((v=s==null?void 0:s.server)==null?void 0:v.profile)||{},[c,d]=P.useState({display_name:o.display_name||"",bio:o.bio||"",avatar_url:o.avatar_url||"",banner_url:o.banner_url||""}),[h,f]=P.useState(Va);P.useEffect(()=>{var x;const g=((x=s==null?void 0:s.server)==null?void 0:x.profile)||{};d({display_name:g.display_name||"",bio:g.bio||"",avatar_url:g.avatar_url||"",banner_url:g.banner_url||""})},[s]);const p=g=>{g.preventDefault(),f({saving:!0,message:"",error:""}),gx(t,{display_name:c.display_name||null,bio:c.bio||null,avatar_url:c.avatar_url||null,banner_url:c.banner_url||null},i).then(x=>{const w=x.profile||{};d({display_name:w.display_name||"",bio:w.bio||"",avatar_url:w.avatar_url||"",banner_url:w.banner_url||""}),f({saving:!1,message:"Bot profile updated.",error:""})}).catch(x=>f({saving:!1,message:"",error:x instanceof Error?x.message:"Could not save profile."}))};return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"Customization",title:"Niko's server presence.",text:"Change how Niko appears in this server. Display name, avatar, banner, and bio are all per-server."}),r.jsx(Fa,{icon:"paint",label:"Identity desk",title:"Server-specific identity",text:"Each server can have its own Niko persona. Changes apply only to this server."}),r.jsxs("form",{onSubmit:p,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ns,{label:"Display name",title:"How Niko appears",detail:"Set the name members see for Niko in this server. Leave blank to use the default.",icon:"settings"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(lt,{label:"Display name",hint:"32 characters or fewer",children:r.jsx("input",{value:c.display_name,maxLength:32,onChange:g=>d({...c,display_name:g.target.value}),placeholder:"Niko"})}),r.jsx(lt,{label:"Bio",hint:"190 characters or fewer",children:r.jsx("input",{value:c.bio,maxLength:190,onChange:g=>d({...c,bio:g.target.value}),placeholder:"A warm Discord companion"})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ns,{label:"Server avatar & banner",title:"Visual identity",detail:"Provide HTTPS image URLs. Images are uploaded to Discord when saved.",icon:"paint"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(lt,{label:"Avatar URL",hint:"Square image, 512×512 recommended",children:r.jsx("input",{type:"url",value:c.avatar_url,onChange:g=>d({...c,avatar_url:g.target.value}),placeholder:"https://cdn.example.com/avatar.png"})}),r.jsx(lt,{label:"Banner URL",hint:"Wide image, 960×540 recommended",children:r.jsx("input",{type:"url",value:c.banner_url,onChange:g=>d({...c,banner_url:g.target.value}),placeholder:"https://cdn.example.com/banner.png"})})]}),r.jsx("p",{className:"form-hint",children:"Images are fetched, validated, and uploaded to Discord. Maximum 8 MB each. Supported formats: PNG, JPG, GIF."})]}),r.jsx(Ba,{state:h})]})]})}const k1={saving:!1,message:"",error:""};function gt({label:t,hint:s,children:i}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:t}),i,s&&r.jsx("small",{children:s})]})}function na({label:t,title:s,detail:i,icon:o}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:t}),r.jsx("h3",{children:s}),r.jsx("p",{children:i})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(ee,{name:o})})]})}function j1({state:t}){return r.jsxs("div",{className:"setting-footer",children:[t.error?r.jsx("span",{className:"form-error",role:"alert",children:t.error}):r.jsx("span",{role:"status",children:t.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:t.saving,children:t.saving?"Saving...":"Save server settings"})]})}const S1=[["moderation","Moderation"],["automod","AutoMod"],["messages","Messages"],["channels","Channels"],["members","Members"],["captcha","Captcha"],["invites","Invites"],["roles","Roles"],["server","Server"],["voice","Voice"]];function N1(t,s){var i;return s?((i=t==null?void 0:t.channels.find(o=>String(o.id)===String(s)))==null?void 0:i.name)||`Saved channel · ${s}`:"Not set"}function Qf(t){const s=t.replace(/^#/,"");return/^[0-9a-fA-F]{6}$/.test(s)?`#${s}`:"#5865F2"}function sa(t,s){const i=s?String(s):"",o=(t==null?void 0:t.channels)||[];return!i||o.some(c=>String(c.id)===i)?o:[{id:i,name:`Saved channel · ${i}`},...o]}function Jf(t,s=[]){const i=(t==null?void 0:t.roles)||[],o=new Set(i.map(d=>String(d.id)));return[...s.map(String).filter((d,h,f)=>d&&!o.has(d)&&f.indexOf(d)===h).map(d=>({id:d,name:`Unavailable role (${d})`})),...i]}function rc(t){var o,c;const s=(t==null?void 0:t.onboarding)||{},i=(t==null?void 0:t.tickets)||{};return{prefixes:((o=t==null?void 0:t.prefixes)!=null&&o.length?t.prefixes:["."]).join(`
`),welcome_channel:s.welcome_channel?String(s.welcome_channel):"",welcome_title:s.welcome_title||"",welcome_description:s.welcome_description||"",welcome_color:s.welcome_color===null||s.welcome_color===void 0?"5865F2":s.welcome_color.toString(16).padStart(6,"0"),welcome_image:s.welcome_image||"",rules_channel:s.rules_channel?String(s.rules_channel):"",rules_text:s.rules_text||"",rules_role_id:s.rules_role_id?String(s.rules_role_id):"",logging:Object.fromEntries(Object.entries((t==null?void 0:t.logging)||{}).map(([d,h])=>[d,h==null?"":String(h)])),disabled_logging:[...((c=t==null?void 0:t.logging)==null?void 0:c.disabled)||[]].map(String),panel_title:i.panel_title||"",panel_description:i.panel_description||"",panel_categories:(i.panel_categories||[]).join(`
`),panel_channel_id:i.panel_channel_id?String(i.panel_channel_id):"",support_roles:[...i.support_roles||[]].map(String)}}function C1({guildId:t,config:s,resources:i,csrfToken:o}){const[c,d]=P.useState(()=>rc(s==null?void 0:s.server)),[h,f]=P.useState(k1),[p,v]=P.useState(!1);P.useEffect(()=>{s!=null&&s.server&&d(rc(s.server))},[s]);const g=(D,F)=>d(V=>({...V,[D]:F})),x=D=>g("welcome_color",D.replace(/^#/,"").replace(/[^0-9a-fA-F]/g,"").slice(0,6)),w=(D,F)=>d(V=>({...V,logging:{...V.logging,[D]:F}})),k=D=>d(F=>({...F,disabled_logging:F.disabled_logging.includes(D)?F.disabled_logging.filter(V=>V!==D):[...F.disabled_logging,D]})),S=D=>{D.preventDefault(),f({saving:!0,message:"",error:""});const F=c.prefixes.split(/\r?\n|,/).map(O=>O.trim()).filter(Boolean),V=c.panel_categories.split(/\r?\n|,/).map(O=>O.trim()).filter(Boolean);Aa(t,"server",{prefixes:F,onboarding:{welcome_channel:c.welcome_channel,welcome_title:c.welcome_title,welcome_description:c.welcome_description,welcome_color:c.welcome_color,welcome_image:c.welcome_image,rules_channel:c.rules_channel,rules_text:c.rules_text,rules_role_id:c.rules_role_id},logging:{...c.logging,disabled:c.disabled_logging},tickets:{panel_title:c.panel_title,panel_description:c.panel_description,panel_categories:V,panel_channel_id:c.panel_channel_id,support_roles:c.support_roles}},o).then(O=>{d(rc(O.config)),f({saving:!1,message:"Server settings saved to Niko.",error:""})}).catch(O=>f({saving:!1,message:"",error:O instanceof Error?O.message:"Could not save server settings."}))},j=c.welcome_channel,N=c.panel_channel_id,B=sa(i,c.welcome_channel),M=sa(i,c.rules_channel),L=sa(i,c.panel_channel_id),I=Jf(i,c.support_roles);return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"Server settings",title:"Make Niko fit your room.",text:"Manage the settings that shape how Niko behaves in this server. Economy balances remain global to each user and are not configured here."}),r.jsxs("div",{className:"settings-intro",children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(ee,{name:"settings"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server control room"}),r.jsxs("strong",{children:[c.prefixes.split(/\r?\n|,/).filter(Boolean).length||0," command prefixes configured"]}),r.jsx("p",{children:"Welcome flows, log destinations, and ticket panels all live here."})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]}),r.jsxs("form",{onSubmit:S,className:"settings-stack server-settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(na,{label:"Commands",title:"Prefixes",detail:"Use one prefix per line. Niko will respond to all of them.",icon:"terminal"}),r.jsx(gt,{label:"Command prefixes",hint:"The default prefix is .",children:r.jsx("textarea",{rows:3,maxLength:200,value:c.prefixes,onChange:D=>g("prefixes",D.target.value),placeholder:".\\n!"})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(na,{label:"Welcome flow",title:"Welcome and rules",detail:"Choose where new members see your welcome message and rules.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(gt,{label:"Welcome channel",children:r.jsxs("select",{value:j,onChange:D=>g("welcome_channel",D.target.value),children:[r.jsx("option",{value:"",children:"Disabled"}),B.map(D=>r.jsxs("option",{value:D.id,children:["#",D.name]},D.id))]})}),r.jsx(gt,{label:"Welcome title",children:r.jsx("input",{value:c.welcome_title,maxLength:200,onChange:D=>g("welcome_title",D.target.value),placeholder:"Welcome to the server"})}),r.jsx(gt,{label:"Welcome message",hint:"Supports {user} and {name}",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:c.welcome_description,onChange:D=>g("welcome_description",D.target.value),placeholder:"Welcome {user}!"})}),r.jsx(gt,{label:"Accent color",hint:"Hex color, for example 5865F2",children:r.jsxs("div",{className:"color-picker",children:[r.jsxs("div",{className:"color-field-control",children:[r.jsx("button",{type:"button",className:"color-preview",style:{backgroundColor:Qf(c.welcome_color)},onClick:()=>v(D=>!D),"aria-label":"Choose welcome accent color","aria-expanded":p}),r.jsx("input",{value:c.welcome_color,maxLength:6,onChange:D=>x(D.target.value),placeholder:"5865F2"})]}),p&&r.jsxs("div",{className:"color-picker-popover",role:"dialog","aria-label":"Choose accent color",children:[r.jsxs("div",{className:"color-picker-header",children:[r.jsx("strong",{children:"Choose color"}),r.jsx("button",{type:"button",className:"color-picker-close",onClick:()=>v(!1),"aria-label":"Close color picker",children:"×"})]}),r.jsx("input",{className:"color-picker-native",type:"color",value:Qf(c.welcome_color),onChange:D=>x(D.target.value)}),r.jsxs("div",{className:"color-picker-value",children:[r.jsx("span",{children:"#"}),r.jsx("input",{value:c.welcome_color.replace(/^#/,""),maxLength:6,onChange:D=>x(D.target.value),placeholder:"5865F2"})]})]})]})}),r.jsx(gt,{label:"Welcome image URL",children:r.jsx("input",{type:"url",value:c.welcome_image,onChange:D=>g("welcome_image",D.target.value),placeholder:"https://..."})}),r.jsx(gt,{label:"Rules channel",children:r.jsxs("select",{value:c.rules_channel,onChange:D=>g("rules_channel",D.target.value),children:[r.jsx("option",{value:"",children:"Not configured"}),M.map(D=>r.jsxs("option",{value:D.id,children:["#",D.name]},D.id))]})}),r.jsx(gt,{label:"Rules text",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:c.rules_text,onChange:D=>g("rules_text",D.target.value),placeholder:"Write the rules members should acknowledge."})}),r.jsx(gt,{label:"Role after rules acknowledgment",children:r.jsxs("select",{value:c.rules_role_id,onChange:D=>g("rules_role_id",D.target.value),children:[r.jsx("option",{value:"",children:"No role"}),Jf(i,c.rules_role_id?[c.rules_role_id]:[]).map(D=>r.jsxs("option",{value:D.id,children:["@",D.name]},D.id))]})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(na,{label:"Audit trail",title:"Logging destinations",detail:"Pick a channel for each event type and disable categories you do not need.",icon:"book"}),r.jsx("div",{className:"server-logging-list",children:S1.map(([D,F])=>{const V=sa(i,c.logging[D]);return r.jsxs("div",{className:"server-logging-row",children:[r.jsxs("label",{className:"form-field",children:[r.jsxs("span",{className:"form-label",children:[F," logs"]}),r.jsxs("select",{value:String(c.logging[D]||""),onChange:O=>w(D,O.target.value),children:[r.jsx("option",{value:"",children:"Not set"}),V.map(O=>r.jsxs("option",{value:O.id,children:["#",O.name]},O.id))]})]}),r.jsxs("label",{className:"setting-row compact-setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enabled"}),r.jsx("small",{children:N1(i,c.logging[D])})]}),r.jsx("input",{type:"checkbox",checked:!c.disabled_logging.includes(D),onChange:()=>k(D)}),r.jsx("i",{"aria-hidden":"true"})]})]},D)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(na,{label:"Support desk",title:"Ticket panel",detail:"Configure the public panel and decide who can handle tickets.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(gt,{label:"Panel title",children:r.jsx("input",{value:c.panel_title,maxLength:200,onChange:D=>g("panel_title",D.target.value),placeholder:"Open a Ticket"})}),r.jsx(gt,{label:"Panel channel",children:r.jsxs("select",{value:N,onChange:D=>g("panel_channel_id",D.target.value),children:[r.jsx("option",{value:"",children:"Keep current panel channel"}),L.map(D=>r.jsxs("option",{value:D.id,children:["#",D.name]},D.id))]})}),r.jsx(gt,{label:"Panel description",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:c.panel_description,onChange:D=>g("panel_description",D.target.value),placeholder:"Tell members what the ticket panel is for."})}),r.jsx(gt,{label:"Ticket categories",hint:"One category per line",children:r.jsx("textarea",{rows:4,value:c.panel_categories,onChange:D=>g("panel_categories",D.target.value),placeholder:"General\\nSupport\\nReports"})}),r.jsx(gt,{label:"Support roles",hint:"Hold Ctrl/Cmd to select more than one",children:r.jsx("select",{multiple:!0,value:c.support_roles,onChange:D=>g("support_roles",Array.from(D.target.selectedOptions,F=>F.value)),children:I.map(D=>r.jsxs("option",{value:D.id,children:["@",D.name]},D.id))})})]}),r.jsx("p",{className:"form-hint",children:"Saving panel settings updates the existing posted panel when Niko can find its saved message."})]}),r.jsx(j1,{state:h})]})]})}function T1({auth:t}){const s=Rr();return r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"n"}),r.jsx("div",{className:"eyebrow",children:"Private workspace"}),r.jsxs("h1",{children:["Settle in, ",r.jsx("em",{children:"admin."})]}),r.jsx("p",{children:"Sign in with Discord to see your Niko profile and manage the servers you look after."}),t.oauth_available?r.jsxs("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard",children:[r.jsx(ee,{name:"lock"})," Continue with Discord ",r.jsx(ee,{name:"arrow"})]}):r.jsxs("div",{className:"notice warning",children:["Discord login is not configured yet. Add ",r.jsx("code",{children:"DISCORD_CLIENT_SECRET"})," to the environment and restart the bot."]}),!s&&r.jsx("p",{className:"form-hint",children:"The public bot configuration is still loading."}),r.jsx("a",{className:"back-link",href:"/",onClick:i=>{i.preventDefault(),he("/")},children:"Return to public site"})]})})]})}function P1({section:t,guild:s,stats:i,csrfToken:o,refreshToken:c}){const[d,h]=P.useState(null),[f,p]=P.useState([]),[v,g]=P.useState(null),[x,w]=P.useState(null),[k,S]=P.useState(!0),[j,N]=P.useState("");return P.useEffect(()=>{S(!0),N(""),(t==="overview"?fx(s.id).then(h):t==="leveling"?Promise.all([px(s.id),km(s.id),jm(s.id)]).then(([M,L,I])=>{p(M),g(L),w(I)}):Promise.all([km(s.id),jm(s.id)]).then(([M,L])=>{g(M),w(L)})).catch(M=>N(M instanceof Error?M.message:"This server could not be loaded.")).finally(()=>S(!1))},[s.id,t,c]),k?r.jsxs("div",{className:"section-loading section-skeleton",role:"status","aria-label":`Loading ${t}`,children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsxs("span",{children:["Loading ",t,"..."]})]}):j?r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Couldn’t load this page."}),r.jsx("span",{children:j}),r.jsx("button",{className:"button button-muted",onClick:()=>window.location.reload(),children:"Try again"})]}):t==="overview"&&d?r.jsx(p1,{overview:d}):t==="leveling"?r.jsx(g1,{guildId:s.id,rows:f,config:v,resources:x,csrfToken:o}):t==="moderation"?r.jsx(v1,{guildId:s.id,config:v,csrfToken:o}):t==="server"?r.jsx(C1,{guildId:s.id,config:v,resources:x,csrfToken:o}):t==="customization"?r.jsx(b1,{guildId:s.id,config:v,csrfToken:o}):r.jsx(x1,{guildId:s.id,config:v,csrfToken:o})}function E1(){return r.jsxs("div",{className:"section-loading section-skeleton dashboard-loading",role:"status",children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"Preparing your dashboard..."})]})}function M1(){Rr();const[t,s]=P.useState(Nm),[i,o]=P.useState(null),[c,d]=P.useState(null),[h,f]=P.useState(null),[p,v]=P.useState([]),[g,x]=P.useState(null),[w,k]=P.useState(!0),[S,j]=P.useState(""),[N,B]=P.useState(0),[M,L]=P.useState(!1),[I,D]=P.useState(null);if(P.useEffect(()=>{const ne=()=>s(Nm());return window.addEventListener("popstate",ne),()=>window.removeEventListener("popstate",ne)},[]),P.useEffect(()=>{k(!0),Promise.all([oc(),fa()]).then(([ne,Se])=>(o(ne),d(Se),ne.authenticated?Promise.all([bm(),cc(),lc().catch(()=>null)]).then(([Le,Ie,ye])=>{f(Le),v(Ie),D((ye==null?void 0:ye.role)||null)}):null)).catch(ne=>j(ne instanceof Error?ne.message:"Dashboard unavailable")).finally(()=>k(!1))},[]),P.useEffect(()=>{if(t.view!=="guild"){x(null);return}const ne=p.find(Se=>Se.id===t.guildId&&Se.installed!==!1);ne?(x(ne),localStorage.setItem("niko-guild",ne.id)):t.guildId&&p.length&&he(uc())},[p,t.guildId,t.view]),w||!i)return r.jsxs("div",{className:"dashboard-state",children:[r.jsx("div",{className:"loading-ring"}),r.jsx("p",{children:"Connecting to Niko…"})]});if(S)return r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Connection issue"}),r.jsxs("h1",{children:["Couldn’t load",r.jsx("br",{}),r.jsx("em",{children:"your workspace."})]}),r.jsx("p",{children:S}),r.jsxs("button",{className:"button button-primary",onClick:()=>window.location.reload(),children:["Try again ",r.jsx(ee,{name:"arrow"})]})]})})]});if(!i.authenticated)return r.jsx(T1,{auth:i});const F=ne=>{ne.installed!==!1&&(localStorage.setItem("niko-guild",ne.id),he(Ps(ne.id,t.section)))},V=ne=>{ne.installed!==!1&&(localStorage.setItem("niko-guild",ne.id),he(Ps(ne.id,"overview")))},O=ne=>{he(g?Ps(g.id,ne):Ps())},oe=()=>he(Ps()),le=()=>he(uc()),xe=async()=>{if(!M){L(!0);try{const[ne,Se]=await Promise.all([oc(),fa()]);if(o(ne),d(Se),ne.authenticated){const[Le,Ie,ye]=await Promise.all([bm(),cc(),lc().catch(()=>null)]);f(Le),v(Ie),D((ye==null?void 0:ye.role)||null)}B(Le=>Le+1),j("")}catch(ne){j(ne instanceof Error?ne.message:"Dashboard refresh failed")}finally{L(!1)}}};let se;return t.view==="servers"?se=r.jsx(f1,{guilds:p,onManage:V}):t.view==="guild"?se=g?r.jsx(P1,{section:t.section,guild:g,stats:c,csrfToken:i.csrf_token,refreshToken:N},`${g.id}-${t.section}`):r.jsx(E1,{}):se=r.jsx(m1,{user:i.user,overview:h,guilds:p,onServers:le,onManage:V}),r.jsx(lp,{user:i.user,guilds:p,selectedGuild:g,view:t.view,section:t.section,stats:c,onHome:oe,onServers:le,onGuildChange:F,onSectionChange:O,onRefresh:xe,refreshing:M,staffRole:I,children:se})}function A1({value:t,onChange:s,placeholder:i="Search documentation...",onFocus:o,onBlur:c}){const[d,h]=P.useState(!1),f=P.useRef(null),[p,v]=P.useState(!1);P.useEffect(()=>{const S=j=>{var N;(j.metaKey||j.ctrlKey)&&j.key==="k"&&(j.preventDefault(),(N=f.current)==null||N.focus())};return document.addEventListener("keydown",S),()=>document.removeEventListener("keydown",S)},[]);const g=()=>{h(!0),v(!0),o==null||o()},x=()=>{h(!1),setTimeout(()=>v(!1),200),c==null||c()},w=S=>{s(S.target.value)},k=S=>{var j;S.key==="Escape"&&((j=f.current)==null||j.blur())};return r.jsxs("div",{className:`doc-search-bar ${p?"expanded":""}`,children:[r.jsxs("div",{className:"search-input-wrapper",children:[r.jsx(ee,{name:"search",className:"search-icon"}),r.jsx("input",{ref:f,type:"text",value:t,onChange:w,onFocus:g,onBlur:x,onKeyDown:k,placeholder:i,className:"search-input","aria-label":"Search documentation"}),r.jsxs("kbd",{className:"search-shortcut",children:[r.jsx("span",{className:"shortcut-key",children:"⌘"}),"K"]})]}),r.jsxs("div",{className:"search-hint",children:["Press ",r.jsx("kbd",{children:"⌘K"})," to focus search"]})]})}function _1({selectedCategory:t,onSelectCategory:s,sections:i,allCategoriesLabel:o="All Categories"}){return r.jsx("div",{className:"doc-filters",children:r.jsxs("div",{className:"filter-tabs",role:"tablist","aria-label":"Filter by category",children:[r.jsx("button",{role:"tab","aria-selected":t==="",className:`filter-tab ${t===""?"active":""}`,onClick:()=>s(""),children:o}),i.map(c=>r.jsxs("button",{role:"tab","aria-selected":t===c.id,className:`filter-tab ${t===c.id?"active":""}`,onClick:()=>s(c.id),children:[r.jsx(ee,{name:c.icon,size:14}),r.jsx("span",{children:c.label})]},c.id))]})})}function ic({doc:t,variant:s="default"}){const i="page"in t?t.page:t,[o,c]=P.useState(!1),d=p=>{p.preventDefault(),he(`/docs/${i.slug}`)},h=p=>{(p.key==="Enter"||p.key===" ")&&(p.preventDefault(),he(`/docs/${i.slug}`))};if(s==="compact")return r.jsx("a",{href:`/docs/${i.slug}`,onClick:d,onKeyDown:h,className:"doc-card-compact",tabIndex:0,role:"button",children:r.jsxs("div",{className:"compact-content",children:[r.jsx("span",{className:"compact-title",children:i.title}),r.jsx("span",{className:"compact-excerpt",children:i.excerpt})]})});const f="highlights"in t?t.highlights:[];return r.jsx("article",{className:`doc-card ${s==="highlighted"?"highlighted":""}`,children:r.jsxs("div",{className:`doc-card-content ${o?"loaded":""}`,children:[r.jsxs("div",{className:"doc-card-header",children:[r.jsx("span",{className:"doc-category",children:i.category.replace(/-/g," ")}),r.jsxs("span",{className:"doc-order",children:["#",i.order]})]}),r.jsx("h3",{className:"doc-title",children:i.title}),r.jsx("p",{className:"doc-excerpt",children:i.excerpt}),f.length>0&&r.jsx("div",{className:"doc-highlights",children:f.slice(0,2).map((p,v)=>r.jsxs("p",{className:"highlight-snippet",children:[p.slice(0,150),p.length>150?"...":""]},v))}),r.jsxs("div",{className:"doc-card-footer",children:[r.jsx("div",{className:"doc-tags",children:i.tags.slice(0,3).map(p=>r.jsxs("span",{className:"doc-tag",children:["#",p]},p))}),r.jsxs("a",{href:`/docs/${i.slug}`,onClick:d,onKeyDown:h,className:"doc-read-more",children:["Read more ",r.jsx(ee,{name:"arrow",size:14})]})]})]})})}const Oe=[{slug:"welcome",title:"Welcome to Niko",category:"getting-started",excerpt:"New to Niko? Start here to understand what the bot can do for your server.",tags:["introduction","overview","beginner"],order:1,content:`
# Welcome to Niko

Niko is a feature-rich Discord bot designed to help server owners and moderators build engaging communities. Whether you're running a small friend group chat or a large public server, Niko provides the tools you need.

## What Can Niko Do?

- **Economy**: A complete economy system with jobs, banking, shop, lottery, and gambling mini-games
- **Leveling**: XP-based leveling system with customizable rewards and announcements
- **Moderation**: Full-featured moderation tools including warns, mutes, kicks, bans, and logging
- **AutoMod**: Automated moderation with anti-spam, anti-link, bad word filtering, and anti-raid protection
- **Social Features**: Birthday tracking, polls, suggestions, starboard, and more
- **Voice Features**: Music playback and voice channel management
- **AI Integration**: AI-powered chat and moderation assistance
- **Dashboard**: Web dashboard for configuring your server settings

## Getting Help

- Use the \`/help\` command in Discord for quick command references
- Browse this documentation for detailed guides
- Join our support server for community help
- Check the GitHub repository for development info
    `},{slug:"invite",title:"Inviting Niko to Your Server",category:"getting-started",excerpt:"Learn how to invite Niko to your Discord server and set it up.",tags:["invite","setup","permissions"],order:2,content:`
# Inviting Niko to Your Server

Getting Niko started in your server is simple. Follow these steps to add the bot and configure it properly.

## Step 1: Invite the Bot

1. Click the "Add to Discord" button on our website
2. Select the server you want to add Niko to
3. Review the permissions requested
4. Authorize the bot

> **Note**: You need the "Manage Server" permission to invite bots to a server.

## Step 2: Essential Permissions

For Niko to work properly, ensure it has these permissions:

- **Send Messages** - For responding to commands
- **Embed Links** - For rich command responses
- **Attach Files** - For image cards and embeds
- **Manage Messages** - For moderation features
- **Manage Roles** - For role management features
- **Manage Channels** - For channel management
- **Kick Members** - For kick moderation
- **Ban Members** - For ban moderation
- **Manage Nicknames** - For nickname changes
- **Add Reactions** - For interactive buttons
- **Use Application Commands** - For slash commands

## Step 3: Position the Bot

In your server settings, make sure Niko's role is positioned appropriately:

- Above the roles it needs to manage
- Below roles with dangerous permissions (for security)
- In a position where it can add/remove roles as needed

## Troubleshooting

If Niko isn't responding:

1. Check that the bot has the correct permissions
2. Verify Niko's role is positioned correctly
3. Try using the bot's username directly in a command
4. Check if the bot is online in your server
    `},{slug:"prefix-setup",title:"Setting Up Prefix Commands",category:"setup",excerpt:"Configure how you want to interact with Niko using prefix commands.",tags:["prefix","commands","setup"],order:1,content:`
# Setting Up Prefix Commands

Niko supports both slash commands and traditional prefix commands. Here's how to set up and use them.

## Slash Commands (Recommended)

Slash commands are the modern way to interact with Discord bots:

- Type \`/\` in any channel to see available commands
- Search for commands by name
- Get instant parameter hints
- Commands work across all channels where Niko is present

## Prefix Commands

If you prefer traditional commands, Niko also supports prefix commands:

- Default prefix: \`.\` (dot) — or your server's custom prefix
- Use \`.help\` to see available commands
- Use \`.prefix\` to change prefixes with an interactive panel

## Setting a Custom Prefix

To set a custom prefix for your server:

\`\`\`
.prefix
\`\`\`

This opens an interactive panel where you can add or remove prefixes. Or use the dashboard to configure it visually.

## Command Types

- **Slash Commands** (\`/\`): Modern, contextual commands
- **Prefix Commands** (\`.\`): Traditional text commands
- **Hybrid Commands**: Both slash and prefix versions available

Most features are available through both command types.
    `},{slug:"server-configuration",title:"Server Configuration Basics",category:"setup",excerpt:"Learn the essentials of configuring Niko for your server.",tags:["configuration","settings","admin"],order:2,content:`
# Server Configuration Basics

Proper server configuration ensures Niko works the way you want. This guide covers the essential settings.

## Access Settings

There are two ways to configure Niko:

1. **Discord Commands**: Use commands like \`.automod\`, \`.logging\`, or \`/leveling config\`
2. **Web Dashboard**: Visit the dashboard at \`/dashboard\` for a visual interface

## Essential Settings to Configure

### Welcome Messages
Set up welcome messages for new members:
\`\`\`
.onboarding setup
\`\`\`

### Logging Channels
Configure where moderation and event logs are sent:
\`\`\`
.logging status
\`\`\`

### Moderation Settings
Customize moderation behavior:
\`\`\`
.automod
\`\`\`

### Leveling Settings
Configure XP and leveling:
\`\`\`
/leveling config
\`\`\`

### Ticket Settings
Set up a support ticket system with categories and support roles:
\`\`\`
.ticket setup
\`\`\`

See the [Ticket System Guide](/docs/tickets-guide) for the full setup walkthrough.

## Setting Up Categories

For larger servers, consider setting up category-specific settings:

- Different welcome channels for different sections
- Separate log channels for different moderation types
- Custom leveling rates per channel
    `},{slug:"roles-and-permissions",title:"Roles and Permissions Guide",category:"setup",excerpt:"Understand how Niko interacts with Discord roles and permissions.",tags:["roles","permissions","admin"],order:3,content:`
# Roles and Permissions Guide

Understanding how Niko works with Discord's role system is crucial for proper setup.

## How Niko Uses Roles

Niko uses Discord's permission system to determine what actions it can take:

1. **Bot Role**: The role assigned to Niko itself determines its capabilities
2. **Command Permissions**: Some commands require specific user permissions
3. **Role Management**: Niko can add/remove roles based on configuration

## Recommended Role Setup

### Bot Role Position
Place Niko's role:
- **Above** roles it needs to assign (for autoroles, verification)
- **Below** roles with administrative permissions (security best practice)
- **Above** the @everyone role

### Permission Hierarchy
Niko needs these permissions in its role:
- View Channel (all channels)
- Send Messages (text channels)
- Embed Links (for rich responses)
- Attach Files (for images)
- Add Reactions (for buttons)

Additional permissions for specific features:
- Manage Messages (moderation)
- Manage Roles (role management)
- Kick/Ban Members (moderation commands)
- Manage Channels (channel operations)

## User Permissions

Some commands require specific permissions from the user:

- **Manage Server** permission for configuration commands
- **Kick Members** for kick commands
- **Ban Members** for ban commands
- **Manage Messages** for message management

## Troubleshooting Permission Issues

If a command fails:

1. Check Niko's role position
2. Verify Niko has the required channel permissions
3. Check if the channel has overwrite permissions blocking Niko
4. Ensure the user has the required permissions for the command
    `},{slug:"tickets-guide",title:"Ticket System Guide",category:"setup",excerpt:"Set up a support ticket system with categories, support roles, and private ticket channels.",tags:["tickets","support","setup","admin"],order:4,content:`
# Ticket System Guide

Niko's ticket system lets members open private support channels when they need help. Everything is controlled from a single \`.ticket\` command group.

## How Tickets Work

1. You post a **ticket panel** in a channel (usually #support)
2. A member clicks **Create Ticket** on the panel and picks a category if you've configured any
3. Niko creates a private \`ticket-<username>\` channel visible only to that member and your support roles
4. You discuss the issue in the ticket, then close or delete it when done

## Setting Up the Panel

### Step 1: Open the Setup Panel

\`\`\`
.ticket setup
\`\`\`

Requires **Administrator** permission. This opens a panel with two buttons:

- **Configure Panel** — customize the title, description, accent color, and image
- **Post Panel Here** — post the public ticket panel in the current channel

### Step 2: Post the Panel

You can also post the panel manually at any time:

\`\`\`
.ticket panel
\`\`\`

This sends the ticket panel to the channel you run it in and remembers where it was posted.

## Managing Categories

Categories let members pick a reason for opening a ticket (e.g. "Billing", "Appeals", "Help").

\`\`\`
.ticket category add <name>
.ticket category remove <name>
.ticket category list
\`\`\`

If no categories are configured, tickets open under a default **General** category.

## Managing Support Roles

Support roles are the staff members who can see and manage tickets. Members with **Manage Channels** also count as support automatically.

\`\`\`
.ticket support add <role>
.ticket support remove <role>
.ticket support list
\`\`\`

## Working Inside a Ticket

Support members (and the ticket opener) can manage an open ticket with these commands:

| Command | Description |
|---------|-------------|
| \`.ticket add <user>\` | Grant another member access to this ticket |
| \`.ticket remove <user>\` | Revoke a member's access to this ticket |
| \`.ticket rename <name>\` | Rename the ticket channel |
| \`.ticket claim\` | Mark the ticket as claimed by you |
| \`.ticket transcript\` | Generate a web transcript of the ticket (see the [Web Transcripts](/docs/tickets-transcripts) guide) |
| \`.ticket close\` | Soft-close the ticket: members become read-only and the channel is renamed \`closed-…\` |
| \`.ticket delete [seconds]\` | Delete the ticket channel after a delay (1–30 seconds, default 5) |

## Best Practices

1. **Pick a support channel**: Keep the panel in a dedicated #support channel
2. **Add categories early**: Members understand why they're opening a ticket
3. **Assign support roles**: Make sure every staff member who should handle tickets has one
4. **Close before deleting**: Soft-close keeps a record of the conversation; generate a [web transcript](/docs/tickets-transcripts) before deleting for a permanent record
    `},{slug:"tickets-transcripts",title:"Ticket Web Transcripts",category:"setup",excerpt:"Generate shareable web transcripts of your tickets and download them as TXT, HTML, CSV, or JSON.",tags:["tickets","transcripts","records","support"],order:5,content:`
# Ticket Web Transcripts

Every ticket conversation can be turned into a permanent, shareable **web transcript** — a readable record of the entire conversation that lives outside Discord.

## Generating a Transcript

Inside an open ticket, a support member runs:

\`\`\`
.ticket transcript
\`\`\`

Niko collects the conversation (up to 2,000 messages, including attachment links), saves it to the database, and posts a result card with a **View Transcript** button.

## Viewing Online

Each transcript gets a unique short ID and its own web page:

\`\`\`
/transcript/<transcript-id>
\`\`\`

Anyone with the link can view the transcript in a clean, dark, Discord-style page with:

- Every message with its timestamp and author
- Attachment links (clickable 📎 links)
- The channel name, category, opener, and message count

## Downloading

The transcript page includes one-click download buttons in four formats:

- **TXT** — plain text log, one line per message
- **HTML** — a styled standalone page you can save or share
- **CSV** — spreadsheet-friendly rows (timestamp, author, content, attachments)
- **JSON** — structured data for archives or tools

## Good to Know

- Transcripts are stored in Niko's database, so they survive deleting the ticket channel
- If the web base URL isn't configured, Niko falls back to attaching a plain **.txt** file instead
- Transcripts include metadata about the ticket: opener, category, claim status, channel name, and creation time

## When to Use It

1. **Before deleting a ticket** — keep a permanent record of resolved issues
2. **Escalations** — share a ticket with higher staff or the server owner
3. **Audits and disputes** — a timestamped, uneditable record of exactly what was said
    `},{slug:"economy-overview",title:"Economy System Overview",category:"economy",excerpt:"Comprehensive guide to Niko's economy features including jobs, banking, shop, and more.",tags:["economy","money","jobs","banking"],order:1,content:`
# Economy System Overview

Niko features a complete economy system that lets your members earn, save, spend, and play with virtual currency.

## Core Features

### Money Basics
- **Balance**: Cash on hand for everyday spending
- **Bank**: Savings account with interest
- **Net Worth**: Total value (balance + bank)

### Earning Money
- **Work Command**: Earn coins by working a simulated job
- **Daily Bonus**: Claim a daily reward (with streak bonuses!)
- **Jobs System**: Different jobs with varying pay rates
- **Lottery**: Buy tickets and win big (with a house rake)

### Banking
- **Deposit/Withdraw**: Move money between balance and bank
- **Bank Tiers**: Higher tiers earn better interest rates
- **Daily Interest**: Money in the bank earns interest every 30 minutes

### Spending Money
- **Shop**: Buy items and upgrades
- **Gambling**: Slots, blackjack, roulette, and more
- **Gifts**: Send money to other members

## Commands

### Basic Economy
- \`balance\` or \`wallet\` - Check your money
- \`daily\` - Claim your daily reward
- \`work\` - Work to earn money
- \`deposit\` - Put money in the bank
- \`withdraw\` - Take money from the bank

### Advanced
- \`leaderboard\` - See richest members
- \`profile\` - View your full stats
- \`shop\` - Browse available items
- \`buy\` - Purchase items
- \`lottery\` - Buy lottery tickets

## Economy Leaderboards

Track the wealthiest members in your server:
- Overall net worth rankings
- Total earned rankings
- Level rankings

Leaderboards update in real-time as members earn and spend.
    `},{slug:"economy-jobs",title:"Jobs and Earning Guide",category:"economy",excerpt:"Learn about the different jobs available and how to maximize your earnings.",tags:["jobs","earning","work"],order:2,content:`
# Jobs and Earning Guide

Niko's job system lets members earn money through various simulated professions.

## Available Jobs

### Entry Level
- **Barista**: Basic coffee shop job, good for beginners
- **Dishwasher**: Entry-level kitchen work
- **Cashier**: Retail position with steady pay

### Mid Level
- **Chef**: Higher pay, requires experience
- **Manager**: Supervisory role with bonuses
- **Programmer**: Tech job with good pay

### High Level
- **Owner**: Highest paying, requires achievement
- **CEO**: Executive position

## Working

Use the \`work\` command to earn money:

\`\`\`
.work
\`\`\`

Each job has:
- **Base pay**: Fixed amount per work session
- **Cooldown**: Time before you can work again (1 hour)
- **Experience**: Work earns XP toward leveling

## Maximizing Earnings

### Tips for More Money
1. **Work consistently**: Use the daily reward and work commands
2. **Climb the job ladder**: Better jobs pay more
3. **Bank your money**: Earn interest on savings
4. **Build streaks**: Daily streaks give bonuses
5. **Buy upgrades**: Shop items can boost earnings
6. **Participate in lottery**: Small chance of big wins

### Cooldowns
- Work: 1 hour cooldown
- Daily: 24 hour cooldown
- Gambling: Varies by game

## Job Commands
- \`.job\` - See your current job
- \`.job list\` - View available jobs
- \`.job apply <job id>\` - Apply for a job
- \`.job info <job id>\` - View job details
- \`.job quit\` - Leave your current job
    `},{slug:"economy-banking",title:"Banking and Interest",category:"economy",excerpt:"Understand the banking system and how to earn passive income through interest.",tags:["banking","interest","savings"],order:3,content:`
# Banking and Interest

Niko's banking system lets you earn passive income by saving your money.

## How Banking Works

### Balance vs Bank
- **Balance**: Cash you carry (used for shopping and gambling)
- **Bank**: Savings that earn interest (more secure, earns passive income)

### Bank Tiers
Higher bank tiers earn better interest rates:

| Tier | Name | Interest Rate |
|------|------|---------------|
| 0 | Basic | 0.5% daily |
| 1 | Silver | 1% daily |
| 2 | Gold | 2% daily |
| 3 | Platinum | 3% daily |
| 4 | Diamond | 5% daily |

## Interest Calculations

Interest is calculated on your **bank balance** (up to the tier cap):

\`\`\`
Interest = min(bank_balance, tier_cap) * interest_rate
\`\`\`

Interest is distributed every 30 minutes and logged to your transaction history.

## Bank Commands

### Deposit
Move money from balance to bank:

\`\`\`
.bank deposit <amount>
\`\`\`

### Withdraw
Take money from bank to balance:

\`\`\`
.bank withdraw <amount>
\`\`\`

### Bank Info
Check your bank status:

\`\`\`
.bank
\`\`\`

### Upgrade Your Vault
Raise your bank cap and interest rate:

\`\`\`
.bank upgrade
\`\`\`

## Banking Tips

1. **Deposit regularly**: More money in bank = more interest
2. **Reach higher tiers**: Better interest rates compound faster
3. **Keep some cash**: You need balance for shopping and gambling
4. **Check daily**: Interest compounds daily, so consistent saving helps
    `},{slug:"economy-shop",title:"Shop and Items Guide",category:"economy",excerpt:"Browse and purchase items from Niko's economy shop.",tags:["shop","items","purchasing"],order:4,content:`
# Shop and Items Guide

Niko's economy shop lets members spend their hard-earned coins on useful items and upgrades.

## Shop Categories

### Consumables
Items that provide one-time effects:
- **Work Boost**: Double earnings for next work
- **Crime Boost**: Better results from crime commands
- **Rob Shield**: Protection from being robbed
- **Lottery Boost**: Extra lottery tickets

### Upgrades
Permanent or long-term improvements:
- **Bank Upgrades**: Higher interest rates
- **Income Boosters**: Better work pay
- **Lucky Charms**: Better gambling odds

### Fun Items
- **Avatars**: Custom profile pictures
- **Badges**: Display achievements
- **Effects**: Visual effects for commands

## Using the Shop

### Browse Items
\`\`\`
.shop
\`\`\`

### Buy Items
\`\`\`
.buy <item id>
\`\`\`

### View Inventory
\`\`\`
.inventory
\`\`\`

### Use Items
Some items are automatic, others need to be activated. Run \`.use\` on its own to open a menu of everything usable in your bag:
\`\`\`
.use
\`\`\`

Or pass an item id directly:
\`\`\`
.use <item id>
\`\`\`

## Shop Tips

1. **Save before buying**: Make sure you can afford it
2. **Check effects**: Some items have cooldown or usage limits
3. **Invest wisely**: Upgrades that boost earnings pay for themselves
4. **Trade items**: Some items can be traded with other members
    `},{slug:"economy-gambling",title:"Gambling and Mini-Games",category:"economy",excerpt:"Try your luck with Niko's gambling mini-games including slots, blackjack, and roulette.",tags:["gambling","slots","blackjack","roulette","casino"],order:5,content:`
# Gambling and Mini-Games

Niko offers several gambling mini-games for members who want to try their luck.

## Available Games

### Slots
Classic 3×3 slot machine game with various symbols and payout combinations.

\`\`\`
.slots play <bet>
\`\`\`

### Blackjack
Play against the dealer in this classic card game.

\`\`\`
.blackjack play <bet>
\`\`\`

### Roulette
Bet on numbers, colors, or combinations in interactive European roulette.

\`\`\`
.roulette
\`\`\`

### Lottery
Weekly lottery where members buy tickets for a chance at the pot.

\`\`\`
.lottery buy <tickets>
\`\`\`

## Gambling Commands

### General
- \`.slots\` - Slots help and payout table
- \`.slots play <bet>\` - Play slots
- \`.blackjack play <bet>\` - Play blackjack
- \`.blackjack tutorial\` - Learn how to play blackjack
- \`.roulette\` - Play roulette
- \`.lottery\` - View the current lottery pot
- \`.lottery buy <tickets>\` - Buy lottery tickets

## Responsible Gambling

> **Note**: Gambling features are for entertainment. Please gamble responsibly.

### Best Practices
1. **Set limits**: Don't bet more than you can afford to lose
2. **Know the odds**: Each game has different house edges
3. **Have fun**: Gambling should be entertainment, not income
4. **Take breaks**: If you're on a losing streak, take a break

## Lottery System

The lottery is a weekly event where:
- Members buy tickets with coins
- A random winner is selected based on ticket count
- The pot grows with each ticket sold
- The house takes a small rake (percentage)
- The winner gets the remaining pot

Lottery resets weekly with a base pot.
    `},{slug:"leveling-overview",title:"Leveling System Overview",category:"leveling",excerpt:"Learn about Niko's XP and leveling system and how to configure it.",tags:["leveling","xp","levels","rankings"],order:1,content:`
# Leveling System Overview

Niko's leveling system rewards members for participating in your server with XP, level-ups, and beautiful image cards.

## How Leveling Works

### Earning XP
Members earn XP when they send messages in enabled channels. Each message earns a random amount of XP (15–25 base), multiplied by the server's XP multiplier.

### Level Progression
Each level requires more XP than the last, following a quadratic curve:

| Level | XP Required |
|-------|-------------|
| 1 | 155 |
| 5 | 475 |
| 10 | 1,100 |
| 25 | 4,475 |
| 50 | 15,100 |

### XP Formula
The XP needed for each level uses a quadratic formula:
\`\`\`
XP for next level = 5 × level² + 50 × level + 100
\`\`\`

This means early levels are quick to earn, but higher levels take progressively more effort.

## Commands

### Check Your Level
\`\`\`
/leveling rank
/leveling rank @user
\`\`\`

This renders a beautiful image card showing:
- Your avatar and display name
- Current level with a large level badge
- XP progress bar
- Server rank

### View Leaderboard
\`\`\`
/leveling leaderboard
\`\`\`

Shows a paginated image leaderboard of the top leveled members with avatars, levels, and XP. Use the ◀ and ▶ buttons to navigate pages.

### Open Management Panel
\`\`\`
/leveling panel
\`\`\`

Opens the interactive CV2 management panel for server admins. This panel has sections for:
- **Overview** — all settings at a glance
- **XP Settings** — toggle, multiplier, cooldown
- **Announcements** — level-up channel and custom message
- **Level Roles** — assign roles at specific levels
- **Card Style** — customise the colours used in level cards

## Configuration

### Enable/Disable Leveling
\`\`\`
/leveling config toggle
\`\`\`

### Set XP Multiplier
Adjust how fast members level:

\`\`\`
/leveling config multiplier <value>
\`\`\`

### Set Cooldown
Prevent XP spam with cooldowns:

\`\`\`
/leveling config cooldown <seconds>
\`\`\`

### Level Up Channel
Choose where level-up announcements appear:

\`\`\`
/leveling config levelupchannel <channel>
\`\`\`

### Custom Level Up Messages
Level-up announcements use a customisable template:

\`\`\`
/leveling config
\`\`\`

Use \`{mention}\`, \`{level}\`, \`{name}\`, and \`{guild}\` in your message.

## Level Rewards

### Level Roles
Assign roles at specific levels:

\`\`\`
/leveling config levelrole <level> <role>
\`\`\`

When a member reaches the configured level, the role is automatically assigned.

## Card Customisation

The \`/leveling rank\` and \`/leveling leaderboard\` commands render image cards with Pillow. Server admins can customise the colours through the management panel:

- **Accent Colour** — controls borders, level numbers, and the progress bar
- **Background Top** — gradient top colour
- **Background Bottom** — gradient bottom colour
- **Reset Colours** — restore café defaults

Each guild's colours are stored independently, so different servers can have unique card themes.

## Leveling Tips

1. **Enable in all channels**: More channels = more XP opportunities
2. **Set reasonable multipliers**: Don't make leveling too fast or slow
3. **Use cooldowns**: Prevent XP grinding abuse
4. **Celebrate milestones**: Level-up announcements build engagement
5. **Reward participation**: Leveling encourages activity
6. **Customise card colours**: Match your server's branding
    `},{slug:"leveling-configuration",title:"Leveling Configuration Guide",category:"leveling",excerpt:"Detailed guide to configuring every aspect of the leveling system.",tags:["leveling","configuration","admin"],order:2,content:`
# Leveling Configuration Guide

Fine-tune the leveling system to match your server's needs.

## Basic Settings

### Enable/Disable
Toggle the entire leveling system on or off:

\`\`\`
/leveling config toggle
\`\`\`

When disabled, no XP is earned and level-up events don't fire.

### XP Multiplier
Adjust the rate at which members earn XP:

\`\`\`
/leveling config multiplier <number>
\`\`\`

- \`1.0\` = Normal speed
- \`2.0\` = Double speed
- \`0.5\` = Half speed

### XP Cooldown
Set a cooldown between XP gains from messages:

\`\`\`
/leveling config cooldown <seconds>
\`\`\`

Example: \`/leveling config cooldown 60\` gives 60 seconds between XP from messages.

## Announcements

### Level Up Channel
Set where level-up notifications are sent:

\`\`\`
/leveling config levelupchannel <channel>
\`\`\`

Placeholders in announcements:
- \`{mention}\` - Mention the member
- \`{level}\` - New level
- \`{name}\` - Display name
- \`{guild}\` - Server name

### Custom Level-Up Messages
Set a custom message template via the interactive panel:

\`\`\`
/leveling panel
\`\`\`

Navigate to **Announcements** and click **Edit Message**.

## Level Roles

### Assigning Roles
Give roles when members reach certain levels:

\`\`\`
/leveling config levelrole <level> <role mention or id>
\`\`\`

Example:
\`\`\`
/leveling config levelrole 10 @Member
/leveling config levelrole 50 @Regular
/leveling config levelrole 100 @Veteran
\`\`\`

You can also manage level roles from the interactive panel:

\`\`\`
/leveling panel
\`\`\`

Navigate to **Level Roles** to add or remove role assignments.

### Checking Progress
Members can check their stats with an image card:

\`\`\`
/leveling rank
/leveling rank @user
\`\`\`

## Card Customisation

The \`/leveling rank\` and \`/leveling leaderboard\` commands render beautiful image cards. Server admins can customise the card colours through the management panel:

\`\`\`
/leveling panel
\`\`\`

Navigate to **Card Style** to edit:

- **Accent Colour** — used for borders, level numbers, and the progress bar (hex like \`#d96545\` or \`ff5500\`)
- **Background Top** — gradient top colour
- **Background Bottom** — gradient bottom colour
- **Reset Colours** — restore café defaults

Each server's colours are stored independently, so different servers can have unique card themes.

## Resetting Leveling Data

To reset a member's leveling progress:

\`\`\`
/leveling config resetuser <member>
\`\`\`

> **Warning**: This permanently deletes that member's leveling progress!
    `},{slug:"moderation-overview",title:"Moderation Tools Overview",category:"moderation",excerpt:"Comprehensive guide to Niko's moderation features including warns, mutes, and moderation commands.",tags:["moderation","warns","mutes","kicks","bans"],order:1,content:`
# Moderation Tools Overview

Niko provides a complete set of moderation tools to help you manage your server.

## Moderation Commands

### Warning System
Issue warnings to members:

\`\`\`
.warn <user> [reason]
\`\`\`

Warnings are tracked per user and can be viewed or cleared.

### Muting
Temporarily prevent a member from speaking:

\`\`\`
.mute <user> [reason]
\`\`\`

### Unmuting
Remove a mute:

\`\`\`
.unmute <user>
\`\`\`

### Kicking
Remove a member from the server:

\`\`\`
.kick <user> [reason]
\`\`\`

### Banning
Ban a member from the server:

\`\`\`
.ban <user> [reason]
\`\`\`

### Unbanning
Unban a user by their ID:

\`\`\`
.unban <user id>
\`\`\`

### Temporary Mutes
Mute a member for a specific number of seconds:

\`\`\`
.tempmute <user> <seconds> [reason]
\`\`\`

### Nickname Changes
Change a member's nickname:

\`\`\`
.nick <user> <nickname>
\`\`\`

## Moderation Logging

All moderation actions are logged to your configured log channel. Logs include:
- Who performed the action
- Who was affected
- When it happened
- The reason given

## Moderation Commands List

| Command | Description |
|---------|-------------|
| \`warn\` | Warn a member |
| \`warnings\` | View a member's warnings |
| \`clearwarnings\` | Clear a member's warnings |
| \`mute\` | Mute a member |
| \`unmute\` | Unmute a member |
| \`tempmute\` | Temporarily mute a member |
| \`kick\` | Kick a member |
| \`ban\` | Ban a member |
| \`unban\` | Unban a user by ID |
| \`clear\` | Clear recent messages in a channel |
| \`purge\` | Purge a member's messages |
| \`slowmode\` | Set channel slowmode (seconds) |
| \`lock\` / \`unlock\` | Lock or unlock a channel |
| \`nick\` | Change a member's nickname |
| \`setmodlog\` | Open the mod-log settings panel |

## Moderation Best Practices

1. **Use reasons**: Always provide a reason for actions
2. **Document actions**: Logs help track patterns
3. **Be consistent**: Apply rules fairly
4. **Use timeouts**: Mutes are better than immediate bans for minor issues
5. **Warn first**: Give warnings before escalating to kicks/bans
    `},{slug:"moderation-warnings",title:"Warning System Guide",category:"moderation",excerpt:"Learn how to use and manage the warning system for tracking member infractions.",tags:["warns","warnings","moderation"],order:2,content:`
# Warning System Guide

The warning system helps track member infractions and establish patterns of behavior.

## Issuing Warnings

### Basic Warning
Warn a member with a reason:

\`\`\`
.warn <user> [reason]
\`\`\`

Example:
\`\`\`
.warn @User Spamming in general chat
\`\`\`

### Warnings with Evidence
It's helpful to include specific details:
- What rule was broken
- When it happened
- Any relevant context

## Viewing Warnings

### Check a User's Warnings
\`\`\`
.warnings <user>
\`\`\`

This shows:
- Total warning count
- Each warning with moderator and reason
- When each warning was issued

### Check Your Own Warnings
Members can check their own warnings:

\`\`\`
.warnings
\`\`\`

## Clearing Warnings

### Clear All Warnings
Remove all warnings from a member:

\`\`\`
.clearwarnings <user>
\`\`\`

### Clear Specific Warnings
Some configurations allow clearing specific warnings by ID.

## Warning Actions

### Automatic Actions
Configure automatic actions based on warning count:
- 3 warnings → Kick
- 5 warnings → Ban

### Manual Actions
Moderators can manually decide consequences based on warnings.

## Warning Best Practices

1. **Be specific**: Clear reasons help members understand what to fix
2. **Track patterns**: Multiple warnings show escalating issues
3. **Escalate appropriately**: Start with warnings, then mutes, then kicks/bans
4. **Document everything**: Warnings provide evidence if needed later
5. **Give second chances**: Warnings are a tool for correction, not just punishment
    `},{slug:"moderation-mutes",title:"Mute System Guide",category:"moderation",excerpt:"Understand how Niko's mute system works and how to use temporary and permanent mutes.",tags:["mutes","timeout","moderation"],order:3,content:`
# Mute System Guide

Niko's mute system allows you to temporarily silence members who are breaking rules.

## Types of Mutes

### Regular Mute
A mute until manually removed:

\`\`\`
.mute <user> [reason]
\`\`\`

### Temporary Mute
A mute that expires automatically (duration in seconds):

\`\`\`
.tempmute <user> <seconds> [reason]
\`\`\`

Duration examples:
- \`300\` - 5 minutes
- \`1800\` - 30 minutes
- \`3600\` - 1 hour
- \`86400\` - 1 day

## How Mutes Work

### Mute Role
Niko creates a "Muted" role that:
- Blocks sending messages
- Blocks speaking in voice
- Blocks adding reactions

The role is automatically applied to muted members and removed when unmuted.

### Channel Permissions
When a member is muted:
1. The Muted role is added to the member
2. Channel permissions deny message sending for the Muted role
3. Voice permissions restrict speaking

### Automatic Unmuting
Temporary mutes are automatically removed when the duration expires. Niko checks regularly for expired mutes.

## Unmuting

### Remove a Mute
\`\`\`
.unmute <user>
\`\`\`

This removes the Muted role and restores the member's permissions.

## Mute Commands

| Command | Description |
|---------|-------------|
| \`mute\` | Mute a member |
| \`tempmute\` | Temporarily mute a member (seconds) |
| \`unmute\` | Remove a mute |

## Mute Best Practices

1. **Use temporary mutes for minor issues**: They're less severe and auto-expire
2. **Set reasonable durations**: Match the severity of the infraction
3. **Provide reasons**: Helps members understand what to fix
4. **Follow up**: Check if behavior improves after unmuting
5. **Escalate if needed**: Repeated offenses may warrant kicks or bans
    `},{slug:"automod-overview",title:"AutoMod Overview",category:"automod",excerpt:"Learn about Niko's automated moderation features including anti-spam and content filtering.",tags:["automod","anti-spam","filtering","automated"],order:1,content:`
# AutoMod Overview

Niko's AutoMod system provides automated protection against common moderation issues.

## AutoMod Features

### Anti-Spam
Detects and handles spam behavior:
- Rapid message sending
- Repeated content
- Mass mentions

### Anti-Link
Controls link posting:
- Block all links
- Allow specific domains
- Warn on first link post

### Bad Word Filter
Filters inappropriate content:
- Built-in word lists
- Custom word additions
- Actions on detection (warn, mute, kick, ban)

### Mass Mention
Prevents mention spam:
- Limits mentions per message
- Blocks @everyone and @here
- Custom thresholds

### Anti-Nuke
Detects destructive actions:
- Mass channel deletion
- Mass role deletion
- Mass permission changes
- Automated responses

### Anti-Raid
Protects against raid attacks:
- Join flood detection
- New account filtering
- Automated countermeasures

## Configuring AutoMod

### Access AutoMod Settings
Open the interactive AutoMod settings panel:

\`\`\`
.automod
\`\`\`

The panel lets admins toggle each protection module and tune thresholds with buttons and menus. You can also use the dashboard for visual configuration.

### Module Toggles
Each AutoMod feature can be toggled on/off independently from the panel:

- **Anti-spam** — detect repeated messages
- **Anti-link** — remove Discord invite links
- **Blocked words** — filter words from the server list
- **Mass mentions** — limit mention floods
- **Anti-nuke** — protect channels and roles
- **Anti-raid** — react to sudden join waves
- **External app protection** — detect user-installed app abuse

## Actions

When AutoMod detects an issue, it can:
- **Warn**: Send a warning to the member
- **Delete**: Remove the offending message
- **Mute**: Temporarily mute the member
- **Kick**: Remove the member
- **Ban**: Permanently ban the member
- **Notify**: Alert moderators

## Whitelisting

Exclude trusted users and roles from AutoMod checks:

### User Whitelist
\`\`\`
.whitelist add user <user>
\`\`\`

### Role Whitelist
\`\`\`
.whitelist add role <role>
\`\`\`

### Removing Entries
\`\`\`
.whitelist remove user <user>
.whitelist remove role <role>
\`\`\`

### Blocked Words
Manage the custom blocked word list:

\`\`\`
.badwords add <word>
.badwords remove <word>
.badwords clear
\`\`\`

## AutoMod Best Practices

1. **Start conservative**: Enable features one at a time
2. **Set appropriate thresholds**: Don't be too strict or too lenient
3. **Whitelist appropriately**: Staff and bots should be whitelisted
4. **Monitor initially**: Watch how AutoMod behaves before full deployment
5. **Adjust based on feedback**: Tweak settings based on what you observe
    `},{slug:"automod-anti-spam",title:"Anti-Spam Configuration",category:"automod",excerpt:"Configure Niko's anti-spam features to keep your chat clean.",tags:["anti-spam","spam","automod"],order:2,content:`
# Anti-Spam Configuration

Niko's anti-spam system detects and handles various types of spam behavior.

## What Counts as Spam

### Message Spam
- Sending many messages quickly
- Repeated identical messages
- Rapid content posting

### Mention Spam
- Mass mentioning users
- @everyone or @here abuse
- Role mention spam

### Content Spam
- Duplicate messages
- Copied content across channels
- Excessive emoji use

## Configuration Options

Thresholds are set from the AutoMod panel (\`.automod\`) or the web dashboard:

- **Spam messages** — how many messages trigger spam detection (default: 6)
- **Spam interval** — the time window for counting messages in seconds (default: 7)
- **Maximum mentions** — mentions allowed per message (default: 5)

## Actions

When AutoMod detects an issue, it can:
- **Warn**: Send a warning to the member
- **Delete**: Remove the offending message
- **Mute**: Temporarily mute the member

## Mass Mention Protection

Enable mass mention detection from the AutoMod panel and set the threshold there. Every mention above the threshold triggers the configured response.

## Exemptions

### Whitelist Users
Specific users can be exempt:

\`\`\`
.whitelist add user <user>
\`\`\`

### Whitelist Roles
Members with a whitelisted role are exempt:

\`\`\`
.whitelist add role <role>
\`\`\`

## Testing Anti-Spam

After configuration, test with:
1. Send messages rapidly (don't overdo it)
2. Try mass mentioning
3. Verify the correct action is taken
4. Adjust thresholds if needed
    `},{slug:"automod-anti-nuke",title:"Anti-Nuke Protection",category:"automod",excerpt:"Protect your server from destructive nuke attacks with Niko's anti-nuke system.",tags:["anti-nuke","security","automod","protection"],order:3,content:`
# Anti-Nuke Protection

Niko's anti-nuke system detects and responds to destructive mass-actions that could destroy your server.

## What is a Nuke?

A "nuke" is when someone with destructive permissions performs many damaging actions quickly, such as:
- Deleting multiple channels
- Removing multiple roles
- Changing many permissions
- Mass banning members

## Anti-Nuke Detection

### Tracked Actions
Niko monitors these audit log events:
- Channel deletions
- Role deletions
- Ban actions
- Kick actions
- Webhook deletions
- Channel creations (can indicate restructuring)

### Threshold System
Set how many actions trigger a response from the AutoMod panel or dashboard. Actions counted within the time window include:

- Channel deletions
- Role deletions
- Ban actions
- Kick actions
- Webhook deletions

## Actions

Choose what happens when anti-nuke triggers:

### Strip Dangerous Roles
Remove roles with dangerous permissions from the offender.

### Kick
Kick the offending member.

### Ban
Ban the offending member.

Set the action from the AutoMod panel or dashboard:

- **Strip** — remove dangerous roles from the offender
- **Kick** — kick the offending member
- **Ban** — ban the offending member

## Response

When anti-nuke triggers:
1. The offending user is immediately actioned
2. A log is sent to your moderation log channel
3. The server owner receives a DM notification
4. Further actions from that user are suppressed for a cooldown period

## Configuration

### Enable Anti-Nuke
Toggle anti-nuke from the AutoMod panel:

\`\`\`
.automod
\`\`\`

Or use the dashboard's moderation settings. Set thresholds per action (for example, 3 channel deletions or 3 bans) and choose the response action there.

## Best Practices

1. **Enable for all servers**: Anti-nuke protects against both external attacks and compromised accounts
2. **Use "strip" as default**: Less destructive than banning, still stops the attack
3. **Set reasonable thresholds**: 3 actions in 10 seconds is usually the sweet spot
4. **Monitor audit logs**: Pay attention to anti-nuke alerts
5. **Combine with other security**: Use anti-raid and proper permission management too
    `},{slug:"automod-anti-raid",title:"Anti-Raid Protection",category:"automod",excerpt:"Configure anti-raid features to protect your server from coordinated attacks.",tags:["anti-raid","raid","security","automod"],order:4,content:`
# Anti-Raid Protection

Anti-raid protection helps defend your server from coordinated mass-join attacks.

## What is a Raid?

A raid is when many accounts join your server simultaneously, often to:
- Spam messages
- Harass members
- Destroy channels and roles
- Mass report content

## Detection Methods

### Join Flood Detection
Detects when many members join in a short period. Configure the join threshold and join interval from the AutoMod panel or dashboard:

- **Join threshold** — how many joins trigger detection (default: 10)
- **Join interval** — the time window for counting joins in seconds (default: 10)

### New Account Detection
Filter out accounts younger than a set number of days. For example, a limit of 7 days blocks accounts less than a week old.

## Actions

When a raid is detected:

### Kick
Kick the raiding members.

### Ban
Ban the raiding members.

### Slowmode
Apply slowmode to all channels.

### Lockdown
Lock all text channels.

Set the response action from the AutoMod panel or dashboard:

- **Kick** — kick the raiding members
- **Ban** — ban the raiding members
- **Slowmode** — apply slowmode to all channels
- **Lockdown** — lock all text channels

## External App Detection

Detect members abusing user-installed apps. Enable it from the AutoMod panel; configuration includes:

- Interaction threshold: How many interactions trigger detection
- Interaction window: Time window for counting
- Join age limit: Minimum account age
- Action: What to do with detected accounts

## Configuration

### Enable Anti-Raid
Toggle anti-raid from the AutoMod panel:

\`\`\`
.automod
\`\`\`

Set the join threshold, join interval, and response action there or in the dashboard's moderation settings.

## Response

When anti-raid triggers:
1. Incoming members are checked against criteria
2. Matching members are actioned (kicked/banned)
3. Channels can be slowed or locked
4. Server owner is notified
5. Moderation logs record the event

## Best Practices

1. **Enable join flood detection**: Most raids start with mass joins
2. **Set new account limits**: Many raid accounts are freshly created
3. **Use kick for initial response**: Less permanent than ban, allows investigation
4. **Combine with anti-nuke**: Defense in depth
5. **Have a response plan**: Know what to do if a raid happens
    `},{slug:"social-overview",title:"Social Features Overview",category:"social",excerpt:"Explore Niko's social features including birthdays, polls, suggestions, and more.",tags:["social","birthdays","polls","suggestions","starboard"],order:1,content:`
# Social Features Overview

Niko includes various social features to help build community engagement.

## Available Features

### Birthdays
Track and celebrate member birthdays:

\`\`\`
.birthday set MM-DD
.birthday remove
.birthday today
\`\`\`

Birthdays are stored per member and can be announced in a designated channel.

### Polls
Create polls for server decisions:

\`\`\`
.poll create <question> | <option 1> | <option 2>
.poll end <message id>
.poll results <message id>
\`\`\`

Members vote with buttons and results update in real time.

### Suggestions
Let members submit suggestions:

\`\`\`
.suggest submit <suggestion>
\`\`\`

Suggestions can be voted on and reviewed by moderators.

### Starboard
Highlight starred messages:

\`\`\`
.starboard channel <channel>
\`\`\`

Messages with enough stars are automatically posted to the starboard channel.

### Giveaways
Host giveaways for your community:

\`\`\`
.giveaway start
.giveaway reroll <message id>
\`\`\`

\`.giveaway start\` opens an interactive setup panel for the prize, duration, winners, channel, and join requirements.

### Roleplay
Express yourself with animated roleplay actions:

\`\`\`
.hug @friend
.pat @friend
\`\`\`

Available actions include hug, kiss, cuddle, pat, poke, tickle, highfive, slap, bonk, and yeet. They work with prefix commands and the right-click **Roleplay** menu. If you'd rather someone not use roleplay commands on you, block them with [\`.rpblock\`](/docs/social-roleplay-blocks).

## Configuration

Most social features are configured through:
- Discord commands
- Web dashboard

### Birthday Channel
Set where birthday announcements appear:

\`\`\`
.birthday channel <channel>
\`\`\`

### Starboard Threshold
Set how many stars trigger starboard posting:

\`\`\`
.starboard threshold <count>
\`\`\`

## Engagement Tips

1. **Use birthdays**: Celebrate community members
2. **Run regular polls**: Let members have a voice
3. **Feature suggestions**: Show you listen to feedback
4. **Star great content**: Highlight quality contributions
5. **Host giveaways**: Reward active members
    `},{slug:"social-birthdays",title:"Birthday System Guide",category:"social",excerpt:"Set up and manage the birthday tracking system for your server.",tags:["birthdays","social","celebration"],order:2,content:`
# Birthday System Guide

Niko's birthday system lets you track and celebrate member birthdays.

## Setting Your Birthday

### Add Your Birthday
\`\`\`
.birthday set MM-DD
\`\`\`

Example:
\`\`\`
.birthday set 06-15
\`\`\`

### Remove Your Birthday
\`\`\`
.birthday remove
\`\`\`

### Check Your Birthday
\`\`\`
.birthday show
\`\`\`

## Server Birthdays

### Today's Birthdays
See who has birthdays today:

\`\`\`
.birthday today
\`\`\`

### Upcoming Birthdays
See birthdays on the horizon:

\`\`\`
.birthday upcoming
\`\`\`

### Birthday Channel
Set a channel for birthday announcements:

\`\`\`
.birthday channel <channel>
\`\`\`

When someone has a birthday, Niko will announce it in this channel.

### Birthday Role
Automatically assign a role on someone's birthday:

\`\`\`
.birthday role <role>
\`\`\`

## Birthday Commands

| Command | Description |
|---------|-------------|
| \`birthday set\` | Set your birthday (MM-DD) |
| \`birthday remove\` | Remove your birthday |
| \`birthday show\` | Show a user's birthday |
| \`birthday today\` | Show today's birthdays |
| \`birthday upcoming\` | Show upcoming birthdays |
| \`birthday channel\` | Set announcement channel (admin) |
| \`birthday role\` | Set the birthday role (admin) |

## Tips

1. **Set a channel**: Dedicated birthday channel builds community
2. **Use custom messages**: Make announcements feel personal
3. **Encourage members**: Let members know they can set birthdays
4. **Celebrate monthly**: Consider a monthly birthday roundup
    `},{slug:"social-polls",title:"Poll System Guide",category:"social",excerpt:"Create and manage polls to gather community opinions.",tags:["polls","voting","social"],order:3,content:`
# Poll System Guide

Niko's poll system lets you create polls for server decisions and discussions.

## Creating Polls

### Basic Poll
Create a simple poll:

\`\`\`
.poll create <question>
\`\`\`

### Poll with Options
Create a poll with custom options:

\`\`\`
.poll create <question> | <option 1> | <option 2> | <option 3>
\`\`\`

Example:
\`\`\`
.poll create "What should our next community event be?" | "Game Night" | "Movie Watch" | "Trivia Contest"
\`\`\`

## Voting

Members vote by clicking the buttons on the poll message — vote counts update live on the poll card.

## Poll Management

### End a Poll Early
\`\`\`
.poll end <message id>
\`\`\`

### View Poll Results
\`\`\`
.poll results <message id>
\`\`\`

## Poll Features

### Vote Tracking
- Each user can only vote once per poll
- Vote counts are tracked in real-time
- Results show percentage breakdowns

## Poll Commands

| Command | Description |
|---------|-------------|
| \`poll create\` | Create a new poll |
| \`poll end\` | End a poll early |
| \`poll results\` | View poll results |

## Tips

1. **Keep it simple**: Clear questions get better responses
2. **Use appropriate options**: Cover the main possibilities
3. **Set reasonable durations**: Give enough time but not too much
4. **Follow up**: Share results and act on feedback
5. **Use for decisions**: Polls work great for community choices
    `},{slug:"social-roleplay-blocks",title:"Roleplay Blocking (rpblock & rpunblock)",category:"social",excerpt:"Stop specific members from using roleplay commands on you with .rpblock and .rpunblock.",tags:["roleplay","privacy","blocks","social"],order:4,content:`
# Roleplay Blocking (rpblock & rpunblock)

Niko's roleplay commands (hug, kiss, cuddle, pat, poke, tickle, highfive, slap, bonk, yeet) are a fun way to interact with other members — but sometimes you just don't want someone using them on you. That's what \`.rpblock\` is for.

## Blocking a Member

To stop someone from using roleplay commands on you:

\`\`\`
.rpblock @member
\`\`\`

Example:
\`\`\`
.rpblock @TrollMaster
\`\`\`

Once blocked, that member can no longer:
- Use roleplay prefix commands on you (\`.hug @you\`, \`.slap @you\`, etc.)
- Pick a roleplay action from the right-click **Roleplay** menu targeting you
- Use the "do it back" buttons on roleplay messages aimed at you

## Unblocking a Member

Changed your mind? Lift the block at any time:

\`\`\`
.rpunblock @member
\`\`\`

## How Blocks Work

- **Directional**: Blocking someone only stops *them* from using roleplay commands on *you*. You can still use roleplay commands on them (and on everyone else).
- **Across servers**: Blocks are tied to your account, so they apply everywhere Niko is used.
- **Private**: Blocks are never announced — the blocked member just sees that their roleplay action was refused.
- **Self-service**: Anyone can manage their own block list; no permissions needed.

## Error Messages

- Forgetting to mention a member: Niko reminds you to pick someone to block.
- Blocking yourself: Niko points out you can't block yourself.
- Blocking someone who's already blocked (or unblocking someone who isn't): Niko lets you know the list is already in that state.

## Tips

1. **Block early**: If someone's roleplay spam bothers you, block them right away
2. **Unblock when things cool off**: Blocks are easy to remove
3. **Tell your friends**: If someone doesn't like a particular action, respect it — the block list is there for a reason
    `},{slug:"utility-overview",title:"Utility Features Overview",category:"utility",excerpt:"Discover Niko's utility features including reminders, tags, and other helpful tools.",tags:["utility","reminders","tags","snipe","afk"],order:1,content:`
# Utility Features Overview

Niko includes various utility features that make everyday server use easier.

## Available Utilities

### Reminders
Set reminders for yourself:

\`\`\`
.reminder set <time> <message>
.reminder list
.reminder delete <id>
\`\`\`

Time formats:
- \`10m\` - 10 minutes
- \`1h\` - 1 hour
- \`1d\` - 1 day
- \`1w\` - 1 week

### Tags
Create custom tags for quick responses:

\`\`\`
.tag create <name> <content>
.tag <name>
.tag list
.tag delete <name>
\`\`\`

Tags are great for frequently used information.

### AFK
Set yourself as AFK:

\`\`\`
.afk <reason>
\`\`\`

When mentioned while AFK, Niko will let people know.

### Snipe
View recently deleted messages:

\`\`\`
.snipe
\`\`\`

### Define
Look up word definitions:

\`\`\`
.define <word>
\`\`\`

### Translate
Right-click any message → **Apps → Translate** to translate it into your language.

## Utility Commands

| Command | Description |
|---------|-------------|
| \`reminder set\` | Set a reminder |
| \`reminder list\` | View your reminders |
| \`reminder delete\` | Delete a reminder |
| \`reminder clear\` | Clear all reminders |
| \`tag create\` | Create a tag |
| \`tag\` | Use a tag |
| \`tag list\` | List all tags |
| \`afk\` | Set AFK status |
| \`snipe\` | View deleted messages |
| \`define\` | Look up a definition |

## Tips

1. **Use tags for FAQs**: Create tags for common questions
2. **Set reminders**: Never miss important events
3. **AFK when away**: Let people know you're unavailable
4. **Explore all utilities**: Many useful tools are available
    `},{slug:"utility-reminders",title:"Reminders Guide",category:"utility",excerpt:"Set up and manage reminders to never miss important events.",tags:["reminders","utility","alerts"],order:2,content:`
# Reminders Guide

Niko's reminder system helps you remember important events and tasks.

## Setting Reminders

### Basic Reminder
Set a reminder for yourself:

\`\`\`
.reminder set <time> <message>
\`\`\`

Examples:
\`\`\`
.reminder set 1h Check the server
.reminder set 30m Meeting starts
.reminder set 1d Birthday tomorrow!
.reminder set 1w Project deadline
\`\`\`

## Viewing Reminders

### Your Reminders
\`\`\`
.reminder list
\`\`\`

Shows all your active reminders with:
- Reminder ID
- Time remaining
- Message content

### Delete a Reminder
\`\`\`
.reminder delete <id>
\`\`\`

### Clear All Reminders
\`\`\`
.reminder clear
\`\`\`

## Time Formats

Niko accepts various time formats:
- \`m\` - minutes (10m, 30m, 60m)
- \`h\` - hours (1h, 2h, 12h)
- \`d\` - days (1d, 2d, 30d)
- \`w\` - weeks (1w, 2w)

Combined: \`1h30m\`, \`2d12h\`, etc.

## How Reminders Work

1. When you set a reminder, it's stored in the database
2. Niko checks for due reminders regularly
3. When a reminder is due, Niko sends it to you
4. Reminders are automatically deleted after being sent

## Reminder Tips

1. **Be specific**: Clear messages help you remember context
2. **Set multiple reminders**: Break tasks into reminders
3. **Use for recurring things**: Daily checks, weekly tasks
4. **Delete completed reminders**: Keep your list clean
5. **Set timezone-aware reminders**: Be aware of time zones if needed

## Commands

| Command | Description |
|---------|-------------|
| \`reminder set\` | Set a reminder |
| \`reminder list\` | View your reminders |
| \`reminder delete\` | Delete a reminder |
| \`reminder clear\` | Clear all reminders |
    `},{slug:"utility-tags",title:"Tags System Guide",category:"utility",excerpt:"Create and manage custom tags for quick access to frequently used information.",tags:["tags","utility","customization"],order:3,content:`
# Tags System Guide

Tags let you create custom short commands that expand to longer messages or information.

## What are Tags?

Tags are custom commands you can create for your server. When someone uses a tag, Niko responds with the tag's content.

## Creating Tags

### Basic Tag
\`\`\`
.tag create <name> <content>
\`\`\`

Example:
\`\`\`
.tag create rules Welcome to the server! Please read the rules in #rules-channel.
\`\`\`

### Tag with Embed
Tags can include formatting and even embeds for richer responses.

## Using Tags

### Call a Tag
\`\`\`
.tag <name>
\`\`\`

Example:
\`\`\`
.tag rules
\`\`\`

### List All Tags
\`\`\`
.tag list
\`\`\`

### Show a Tag's Raw Content
\`\`\`
.tag raw <name>
\`\`\`

## Managing Tags

### Edit a Tag
\`\`\`
.tag edit <name> <new content>
\`\`\`

### Delete a Tag
\`\`\`
.tag delete <name>
\`\`\`

### Tag Info
See a tag's owner, creation date, and usage count:

\`\`\`
.tag info <name>
\`\`\`

## Tag Permissions

### Who Can Use Tags
Tags are public by default. Set permissions as needed.

### Who Can Manage Tags
Tag creators can edit/delete their own tags. Administrators can manage all tags.

## Use Cases

### Server Information
- Rules summaries
- FAQ answers
- Role descriptions
- Channel purposes

### Commonly Used Text
- Welcome messages
- Event announcements
- Form templates
- Standard responses

### Fun Content
- Jokes and memes
- Quotes
- Easter eggs
- Secret messages

## Tips

1. **Keep names simple**: Easy to remember and type
2. **Use for FAQs**: Quick answers to common questions
3. **Organize with prefixes**: Group related tags (e.g., \`info-rules\`, \`info-roles\`)
4. **Regular maintenance**: Remove outdated tags
5. **Share with community**: Let members know useful tags exist
    `},{slug:"voice-overview",title:"Voice Features Overview",category:"voice",excerpt:"Learn about Niko's voice and music features.",tags:["voice","music","playback"],order:1,content:`
# Voice Features Overview

Niko includes voice features for music playback and voice channel management.

## Music Features

### Playing Music
Use the \`/play\` slash command or \`.play\` with a prefix:

\`\`\`
.play <song name or URL>
\`\`\`

Supports:
- YouTube videos
- Spotify links
- Direct URLs
- Search queries

### Music Controls
- \`/pause\` - Pause playback
- \`/resume\` - Resume playback
- \`/stop\` - Stop playback
- \`/skip\` - Skip to next song
- \`/queue\` - View play queue
- \`/nowplaying\` - See current song
- \`/loop\` - Cycle loop modes (off / track / queue)
- \`/volume\` - Set playback volume
- \`/autoplay\` - Toggle Last.fm autoplay

### Liked Songs
- \`/like\` - Like the currently playing song
- \`/liked\` - Browse your liked songs
- \`/unlike\` - Remove a song from your likes

### Other Music Features
- Ghost queue for Last.fm autoplay (keeps playing when the queue runs dry)
- Music persistence across restarts
- Now-playing panel with interactive controls

## Voice Channel Management

### Join Voice
Niko joins automatically when you use \`/play\` — no separate join command needed.

### Leave Voice
\`\`\`
/disconnect
\`\`\`

Or use \`.disconnect\` with a prefix. You can also use the disconnect button on the now-playing panel.

### Voice Settings
- \`/volume\` - Adjust playback volume (0-100)
- \`/musicstatus\` - Show or hide the listening status

## Permissions

Niko needs these permissions for voice:
- Connect to voice channels
- Speak in voice channels
- Use voice activity (if needed)

## Tips

1. **Set up voice channels**: Dedicated music channels work best
2. **Configure volume**: Use \`/volume\` to set a comfortable level
3. **Enable autoplay**: Turn on \`/autoplay\` with a Last.fm username for endless music
4. **Save favorites**: Use \`/like\` on songs you enjoy and find them later with \`/liked\`
    `},{slug:"ai-overview",title:"AI Features Overview",category:"ai",excerpt:"Explore Niko's AI-powered features for chat and moderation assistance.",tags:["ai","artificial intelligence","chat"],order:1,content:`
# AI Features Overview

Niko integrates AI capabilities to enhance moderation and provide interactive experiences.

## Available AI Features

### AI Chat
Members can interact with Niko's AI for conversations:

- **Mention Niko** — start your message with @Niko
- **Say his name** — include "niko" anywhere in the message
- **Prefix command** — use \`.ai <message>\`

The AI responds based on configured personalities and context.

### AI Moderation Assistance
AI can help with:
- Suggesting moderation actions
- Analyzing message content
- Providing context for decisions

### AI Configuration
Configure AI behavior through:
- Personality settings (café or normal mode)
- Enabled/disabled per server
- Memory of past conversations

## Configuration

All AI settings live in one interactive panel:

\`\`\`
/ai-config
\`\`\`

Or with a prefix: \`.ai-config\` (requires **Manage Server** permission)

The panel lets you:
- Enable or disable AI for this server
- Switch between café and normal personalities
- Manage per-server AI preferences

## Privacy

AI features process message content to generate responses. Be aware that:
- Messages may be sent to AI providers
- Check your privacy settings and member expectations
- You can disable AI features if preferred

## AI Commands

| Command | Description |
|---------|-------------|
| \`@Niko <message>\` or \`.ai <message>\` | Chat with the AI |
| \`/ai-config\` | Open the AI settings panel |

## Tips

1. **Test personalities**: Find what works for your community
2. **Set boundaries**: Configure what AI can and can't discuss
3. **Monitor responses**: Check AI responses for appropriateness
4. **Use for engagement**: AI chat can be fun for members
    `},{slug:"dashboard-overview",title:"Dashboard Overview",category:"dashboard",excerpt:"Learn how to use the web dashboard to configure your server.",tags:["dashboard","web","configuration"],order:1,content:`
# Dashboard Overview

The Niko web dashboard provides a visual interface for configuring your server settings.

## Accessing the Dashboard

Visit \`/dashboard\` and authenticate with Discord to access your servers.

## Dashboard Sections

### Server Overview
- Server statistics
- Quick settings access
- Recent activity

### Economy
- Leaderboards
- Economy settings
- Shop management

### Leveling
- Level settings
- XP configuration
- Level role management

### Moderation
- Moderation settings
- AutoMod configuration
- Log channel setup

### AI
- AI personality settings
- AI enable/disable
- Response configuration

## Using the Dashboard

1. **Select your server** from the dashboard home
2. **Navigate sections** using the sidebar or tabs
3. **Configure settings** with visual controls
4. **Save changes** automatically or manually

## Features

### Visual Configuration
- Toggle switches for enabling/disabling features
- Dropdowns for selecting options
- Input fields for custom values
- Channel selectors for setting channels

### Real-time Updates
Changes made in the dashboard are applied immediately to your server.

### Permission Gating
Some settings require administrator permissions to change.

## Tips

1. **Use both interfaces**: Dashboard and Discord commands both work
2. **Check permissions**: Make sure you have admin perms for changes
3. **Explore all sections**: Many features are configurable
4. **Test changes**: Verify settings work as expected
    `},{slug:"dashboard-economy",title:"Dashboard: Economy Settings",category:"dashboard",excerpt:"Configure economy settings through the web dashboard.",tags:["dashboard","economy","settings"],order:2,content:`
# Dashboard: Economy Settings

Configure your server's economy settings through the visual dashboard.

## Economy Dashboard Sections

### General Settings
- Enable/disable economy
- Starting balance for new members
- Currency name and symbol

### Jobs
- Available jobs
- Job pay rates
- Job requirements

### Banking
- Bank tier rates
- Interest rates
- Tier requirements

### Shop
- Available items
- Item prices
- Item effects

### Lottery
- Base pot amount
- Ticket price
- Draw interval

## Configuration Options

### Starting Balance
Set how much money new members start with:

\`\`\`
Default: 100 coins
\`\`\`

### Currency Display
Customize how currency appears:
- Currency name (coins, credits, etc.)
- Symbol (€, $, ₲, etc.)

### Job Configuration
Adjust job details:
- Job names and descriptions
- Pay rates per job
- Promotion requirements

### Shop Items
Manage shop inventory:
- Add/remove items
- Set prices
- Configure effects

## Saving Changes

Changes are saved automatically as you make them. You can also manually save.

## Tips

1. **Balance settings**: Adjust starting balance for your server's economy
2. **Job variety**: More jobs = more ways to earn
3. **Shop appeal**: Interesting items encourage participation
4. **Test economy**: Verify commands work with new settings
    `},{slug:"dashboard-leveling",title:"Dashboard: Leveling Settings",category:"dashboard",excerpt:"Configure leveling settings through the web dashboard.",tags:["dashboard","leveling","settings"],order:3,content:`
# Dashboard: Leveling Settings

Configure your server's leveling system through the visual dashboard.

## Leveling Dashboard Sections

### General
- Enable/disable leveling
- XP multiplier
- Message cooldown

### Channels
- Channels that give XP
- Channel-specific multipliers

### Announcements
- Level-up channel
- Custom level-up messages
- Announcement toggle

### Roles
- Level-based roles
- Role assignment levels
- Role rewards

## Configuration Options

### XP Multiplier
Adjust the rate of XP gain:

Default: 1.0 (normal speed)

### Cooldown
Set time between XP from messages:

Default: 0 seconds (no cooldown)

### Level-Up Messages
Customize level-up announcements with placeholders:
- \`{user}\` - Member name
- \`{level}\` - New level
- \`{guild}\` - Server name

### Level Roles
Assign roles at specific levels:
- Choose the level threshold
- Select the role to assign
- Multiple level roles supported

## Saving Changes

All changes are saved automatically to your server's configuration.

## Tips

1. **Set appropriate multipliers**: Match your server's activity level
2. **Use cooldowns**: Prevent XP abuse
3. **Celebrate levels**: Level-up announcements encourage participation
4. **Reward progression**: Level roles give members goals to work toward
    `},{slug:"tips-community-management",title:"Community Management Tips",category:"tips",excerpt:"Best practices for managing your community with Niko.",tags:["tips","management","community"],order:1,content:`
# Community Management Tips

Running a successful server takes planning and the right tools. Here are tips for using Niko effectively.

## Getting Started

### Plan Your Server
- Define your server's purpose
- Identify your target audience
- Plan your channel structure
- Decide on rules and guidelines

### Set Up Niko Gradually
1. Invite Niko and set basic permissions
2. Configure welcome messages
3. Set up logging channels
4. Configure moderation settings
5. Enable economy and leveling
6. Add social features

## Engagement Strategies

### Use Leveling
Leveling encourages activity by rewarding members:
- Set reasonable XP rates
- Celebrate level-ups
- Offer role rewards at milestones

### Build Economy
An active economy gives members something to do:
- Multiple ways to earn (jobs, daily, work)
- Interesting things to buy (shop)
- Safe gambling options (if appropriate)

### Social Features
Keep members engaged with:
- Birthday celebrations
- Regular polls
- Suggestion systems
- Giveaways and events

## Moderation Best Practices

### Set Clear Rules
- Make rules easy to find
- Explain consequences
- Be consistent in enforcement

### Use Moderation Tools Wisely
- Warn before punishing
- Document actions
- UseAutoMod to reduce workload
- Keep logs for reference

### Build Community Culture
- Lead by example
- Recognize positive behavior
- Address issues quickly
- Listen to member feedback

## Growth Tips

### Welcome New Members
- Set up welcome messages
- Give starter resources
- Introduce server features

### Keep Content Fresh
- Regular events
- New features and updates
- Conversations and activities

### Get Feedback
- Use suggestion systems
- Run polls for decisions
- Ask members what they want

## Common Issues and Solutions

### Low Activity
- Enable XP in all channels
- Run events and activities
- Feature member contributions
- Use social features

### Moderation Overload
- Enable AutoMod features
- Set up appropriate automation
- Train moderators
- Use logging effectively

### Economy Problems
- Adjust starting balance
- Modify job pay rates
- Add/remove shop items
- Tune gambling settings

### Member Conflicts
- Clear rules and consequences
- Consistent enforcement
- Mediation when needed
- Escalation procedures

## Resources

- Use this documentation for detailed guides
- Check the commands page for command references
- Visit the dashboard for visual configuration
- Join the support server for help
    `},{slug:"tips-getting-started",title:"Quick Start Guide",category:"tips",excerpt:"Get your server up and running with Niko in minutes.",tags:["tips","quick-start","beginner"],order:2,content:`
# Quick Start Guide

Get Niko up and running in your server quickly with this streamlined guide.

## 5-Minute Setup

### Step 1: Invite Niko
Click "Add to Discord" and select your server.

### Step 2: Check Permissions
Make sure Niko has these essential permissions:
- Send Messages
- Embed Links
- Attach Files
- Manage Messages (for moderation)
- Add Reactions (for buttons)

### Step 3: Set Up Welcome
\`\`\`
/onboarding setup
\`\`\`

Or with a prefix: \`.onboarding setup\`. Configure a welcome channel and message for new members.

### Step 4: Configure Logging
\`\`\`
/logging status
\`\`\`

Or with a prefix: \`.logging status\`. Set up log channels for moderation events.

### Step 5: Test Commands
Try a few commands to make sure everything works:
- \`.help\` - See available commands
- \`/balance\` - Check economy
- \`/leaderboard\` - See leaderboards

## Next Steps

### Enable Features
Turn on XP tracking:
\`\`\`
/leveling config toggle
\`\`\`

More leveling options (multiplier, cooldown, level-up channel, role rewards) live in \`/leveling config\` or the dashboard.

### Configure Moderation
Set up AutoMod to reduce your workload:
\`\`\`
/automod
\`\`\`

The interactive panel lets you toggle anti-spam, anti-link, bad words, mass mention, anti-nuke, and anti-raid protection in one place.

### Invite Members
Let your community know Niko is available and show them useful commands.

## Essential Commands to Know

### For Members
- \`/balance\` / \`/profile\` - Check money
- \`/daily\` - Daily reward
- \`/work\` - Earn money
- \`/leaderboard\` - See rankings
- \`/help\` - Get help

### For Moderators
- \`/warn\` - Warn a member
- \`/mute\` / \`/unmute\` - Mute management
- \`/kick\` / \`/ban\` - Removal commands
- \`/automod\` - AutoMod settings

### For Administrators
- \`/logging\` - Configure logs
- \`/onboarding\` - Welcome setup
- \`/leveling config\` - Level settings
- \`/ai-config\` - AI settings

## Troubleshooting Quick Fixes

### Bot Not Responding
1. Check bot permissions
2. Check bot role position
3. Try \`/ping\` to test

### Commands Not Working
1. Check prefix settings
2. Verify user permissions
3. Check if feature is enabled

### Economy Issues
1. Check if economy is enabled
2. Verify database is working
3. Check user has required permissions

## Getting Help

- Use \`/help\` for command references
- Browse this documentation for guides
- Visit the dashboard for visual configuration
- Join support server for assistance
    `},{slug:"giveaway-overview",title:"Giveaway System",category:"social",excerpt:"Run interactive giveaways with join requirements, timed entries, and automatic winner selection.",tags:["giveaway","contest","engagement","winners","prize"],order:5,content:`
# Giveaway System

Niko's giveaway system lets you run interactive giveaways with join requirements, timed entries, and automatic winner selection — all managed through an interactive UI panel.

## Starting a Giveaway

\`\`\`
.giveaway start
\`\`\`

This opens an interactive setup panel where you configure:

- **Prize** — What the winners receive (text)
- **Duration** — How long the giveaway runs (e.g. 1h, 2d, 30m)
- **Number of Winners** — How many people win (default: 1)
- **Channel** — Which channel to post in
- **Join Requirements** — Account age, time in server, required roles, or booster-only

All settings are configured through buttons on the panel — no need to remember command syntax.

## Duration Format

Use \`s\` (seconds), \`m\` (minutes), \`h\` (hours), or \`d\` (days):

| Format | Meaning |
|--------|---------|
| \`30m\` | 30 minutes |
| \`2h\` | 2 hours |
| \`1d\` | 1 day |
| \`12h\` | 12 hours |

## Join Requirements

You can restrict who can enter a giveaway:

- **Minimum Account Age** — New accounts can't enter
- **Minimum Time in Server** — Must have been in the server for a set duration
- **Required Roles** — Must have one or more specific roles
- **Booster Only** — Only server boosters can enter

These are configured through the interactive panel when starting a giveaway.

## Rerolling

If you need to pick a new winner:

\`\`\`
.giveaway reroll <message_id>
\`\`\`

Replace \`<message_id>\` with the ID of the giveaway message (right-click → Copy Message ID).

> **Note:** Only members with **Manage Server** permission can start and reroll giveaways.

## How It Works

1. Niko posts an interactive giveaway message with a "Join" button
2. Members click the button to enter
3. A background task checks every 15 seconds for ended giveaways
4. When time runs out, winners are randomly selected from participants
5. The giveaway message updates to show winners, and a winner announcement is sent

## Requirements

- **Manage Server** permission to start and reroll giveaways
- Bot needs **Send Messages** and **Add Reactions** permissions in the giveaway channel
    `},{slug:"social-notifier",title:"Social Media Notifier",category:"social",excerpt:"Get automatic notifications when creators post new content on YouTube, Twitter, TikTok, Bluesky, or Reddit.",tags:["notifier","youtube","twitter","tiktok","bluesky","reddit","notifications","social media"],order:6,content:`
# Social Media Notifier

The notifier system automatically tracks social media accounts and posts a notification to a Discord channel whenever new content is published. It supports YouTube, Twitter/X, TikTok, Bluesky, and Reddit.

## Supported Platforms

| Platform | What it tracks | Update interval |
|----------|---------------|-----------------|
| **YouTube** | New videos (via RSS feed) | Every 5 minutes |
| **Twitter/X** | New tweets | Every 5 minutes |
| **TikTok** | New posts | Every 5 minutes |
| **Bluesky** | New posts | Every 5 minutes |
| **Reddit** | New posts in a subreddit | Every 5 minutes |

## Opening the Setup Panel

\`\`\`
.notifier
\`\`\`

This opens an interactive panel with buttons for each platform. Click a platform button to open a modal where you enter:

- **Account/Channel Name** — The username, handle, or channel ID
- **Notification Channel** — Where to post notifications (defaults to the current channel)

> **Note:** You need **Manage Server** permission to use the notifier.

## Quick Follow Command

For faster setup, use the shortcut command:

\`\`\`
.follow <platform> <username> [#channel]
\`\`\`

**Platforms:** \`youtube\`, \`twitter\`, \`tiktok\`, \`bluesky\`, \`reddit\`

**Examples:**
\`\`\`
.follow youtube @MrBeast
.follow twitter elonmusk #social-feed
.follow reddit programming
\`\`\`

## Viewing Followed Accounts

\`\`\`
.notifier list
\`\`\`

Shows all tracked accounts with their platform, channel, and notification target.

## Unfollowing

\`\`\`
.unfollow <platform> <username>
\`\`\`

Stops tracking an account. You can also remove follows through the "View Follows" button in the setup panel.

## Testing a Follow

Before following an account, you can verify it works:

\`\`\`
.notifier test <platform> <query>
\`\`\`

This validates the account exists and shows the latest post.

## Notification Format

Notifications use Discord CV2 containers styled to match each platform's branding:

- **YouTube** — Red accent, video thumbnail, channel name
- **Twitter/X** — Blue accent, tweet text preview
- **TikTok** — Pink accent, video link
- **Bluesky** — Light blue accent, post text
- **Reddit** — Orange accent, subreddit name and post title

Each notification includes a link to view the original post.

## How It Works

1. A background task runs every 5 minutes
2. For each followed account, it fetches the latest post
3. If the post ID differs from the last-seen ID, a notification is sent
4. The last-seen ID is updated to prevent duplicate notifications
5. On first follow, the current latest post is recorded without sending a notification
    `},{slug:"social-starboard",title:"Starboard",category:"social",excerpt:"Highlight popular messages in a dedicated starboard channel based on reaction counts.",tags:["starboard","stars","highlights","popular","reactions"],order:7,content:`
# Starboard

The starboard system automatically reposts popular messages to a dedicated channel when they reach a configurable reaction threshold. It's a great way to highlight the best content in your server.

## How It Works

1. Members react to a message with the trigger emoji (default: ⭐)
2. When the reaction count reaches the threshold, the message is posted to the starboard channel
3. If the reaction count later drops below the threshold, the starboard post is removed
4. If a message is already on the starboard and gets more reactions, the post updates in place

## Setting Up the Starboard

### Set the Starboard Channel

\`\`\`
.starboard channel <channel>
\`\`\`

\`\`\`
.starboard channel #starboard
\`\`\`

### Set the Threshold

\`\`\`
.starboard threshold <number>
\`\`\`

\`\`\`
.starboard threshold 5
\`\`\`

The threshold is the number of reactions needed before a message appears on the starboard (minimum: 1, maximum: 50, default: 3).

### Set the Trigger Emoji

\`\`\`
.starboard emoji <emoji>
\`\`\`

\`\`\`
.starboard emoji ⭐
\`\`\`

### Ignore Channels

Prevent messages from certain channels from appearing on the starboard:

\`\`\`
.starboard ignore <channel>
.starboard unignore <channel>
\`\`\`

### Disable the Starboard

\`\`\`
.starboard disable
\`\`\`

### View Configuration

\`\`\`
.starboard config
\`\`\`

## Starboard Post Format

Starboard posts display:

- Star count and source channel
- Author name and relative timestamp
- Message content (truncated at 1500 characters)
- Image attachments embedded as a MediaGallery
- A "Jump to message" link

## Requirements

- **Manage Server** permission to configure the starboard
- The bot needs **Read Messages** and **Send Messages** permissions in both the source channels and the starboard channel
- Bot does **not** post messages from other bots to the starboard
    `},{slug:"social-suggestions",title:"Suggestions",category:"social",excerpt:"Let members submit suggestions with up/down voting and admin approval or denial.",tags:["suggestions","voting","feedback","community","approve","deny"],order:8,content:`
# Suggestions

The suggestions system lets server members submit ideas and feedback that can be voted on by the community. Administrators can approve or deny suggestions with optional reasons.

## Setting Up Suggestions

### Set the Suggestion Channel

\`\`\`
.suggest channel <channel>
\`\`\`

\`\`\`
.suggest channel #suggestions
\`\`\`

> **Note:** You need **Manage Server** permission to configure suggestions.

## Submitting a Suggestion

\`\`\`
.suggest submit <text>
\`\`\`

\`\`\`
.suggest submit Add a meme channel for #memes-only content
\`\`\`

Suggestions are posted in the configured suggestion channel with:
- The suggestion text
- The submitter's name
- Upvote and downvote buttons
- A suggestion ID for admin reference

## Voting

Members vote on suggestions using the buttons below each suggestion:

- 👍 **Upvote** — Supports the suggestion
- 👎 **Downvote** — Opposes the suggestion

Votes can be toggled — click the same button again to remove your vote.

## Admin Actions

### Approve a Suggestion

\`\`\`
.suggest approve <id> [reason]
\`\`\`

### Deny a Suggestion

\`\`\`
.suggest deny <id> [reason]
\`\`\`

When approved or denied, the suggestion message updates to show:
- A status indicator (Approved ✅ or Denied ❌)
- The admin who made the decision
- The reason (if provided)

Voting buttons are removed once a suggestion receives a verdict.

## Viewing Configuration

\`\`\`
.suggest config
\`\`\`

Shows the current suggestion channel and settings.

## Requirements

- **Manage Server** permission to set the channel, approve, or deny suggestions
- **Send Messages** permission to submit suggestions
- The bot needs **Read Messages** and **Send Messages** permissions in the suggestion channel
    `},{slug:"logging-overview",title:"Logging System",category:"logging",excerpt:"Comprehensive server event logging with per-category channels, rich embeds, and detailed audit trails.",tags:["logging","audit","moderation logs","member logs","message logs","channel logs","voice logs","server logs"],order:1,content:`
# Logging System

Niko's logging system provides comprehensive server event logging across multiple categories, each assignable to its own channel. Every log entry includes structured data, moderator attribution from the audit log, and rich formatting.

## Logging Categories

| Category | Events Logged |
|----------|--------------|
| **Members** | Join, leave, role changes, nickname changes, avatar updates, timeout events |
| **Messages** | Message edits, message deletions (with image attachments in MediaGallery) |
| **Moderation** | Warns, mutes, kicks, bans, unbans, nickname changes by moderators |
| **Channels** | Channel create, delete, update (name, topic, slowmode, NSFW, bitrate, user limit) |
| **Roles** | Role create, delete, update (name, color, hoist, mentionable, permissions) |
| **Server** | Server settings changes (name, description, verification, icon, banner, AFK channel) |
| **Invites** | Invite create, delete, and usage tracking on member joins |
| **Voice** | Voice channel joins, leaves, and moves |
| **Automod** | AutoMod actions (auto-delete, auto-mute, auto-ban, bad word detection) |

## Configuration

Open the interactive logging panel:

\`\`\`
.logging
\`\`\`

Click a category button to select which channel receives logs for that category. Each category can be assigned to a different channel.

### View Current Status

\`\`\`
.logging status
\`\`\`

Shows all categories, their assigned channels, and whether each is enabled or disabled.

## Log Format

All log entries use Discord CV2 containers with consistent formatting:

- **Title** — Event type (e.g. "Message Deleted", "Member Joined")
- **Body** — Structured details including user mentions, channel references, and timestamps
- **Target ID** — The affected user's ID for filtering
- **MediaGallery** — Image attachments from deleted messages are embedded directly in the log
- **Section + Thumbnail** — Avatar changes show the new avatar as a thumbnail
- **Moderator attribution** — Actions are attributed to the responsible moderator via audit log

## Member Logging

Tracks all member-related events:

- **Member Joined** — Account age, join method (invite code, vanity URL, or unknown), and invite usage
- **Member Left** — Lists the member's roles at time of departure
- **Avatar Updated** — Shows old and new avatar with Section + Thumbnail accessory
- **Role Changes** — Roles added and removed
- **Nickname Changes** — Old and new nickname, attributed to the moderator who changed it
- **Timeout Events** — Timeout applied/removed with moderator and expiry time

## Message Logging

Tracks message content changes:

- **Message Edited** — Shows before/after content with a jump link
- **Message Deleted** — Shows author, channel, content, and attachments:
  - Image attachments render in a **MediaGallery** component inside the log container
  - Non-image attachments are re-uploaded as Discord files
  - Messages with no text content show "*No text content*"

## Invite Tracking

Niko caches invite usage on startup and monitors for changes:

- **Invite Used** — Tracks which invite was used, by whom, and total uses
- **Vanity Invite Used** — Detects vanity URL joins
- **Unknown Join** — Logs joins where no invite match was found
- **Invite Created/Deleted** — Tracks invite lifecycle events

## Disabling Categories

You can disable specific logging categories through the interactive panel. Disabled categories won't send any log messages even if a channel is assigned.

## Rate Limiting

The logging system includes built-in rate limiting to prevent channel spam during mass events (e.g., mass-ban, raid scenarios). Log messages are queued and sent with controlled spacing.
    `}];function D1(t){return Oe.find(s=>s.slug===t)}const En=[{id:"getting-started",label:"Getting Started",description:"New to Niko? Start here.",icon:"icon_home",count:Oe.filter(t=>t.category==="getting-started").length},{id:"setup",label:"Setup",description:"Configure Niko for your server.",icon:"icon_settings",count:Oe.filter(t=>t.category==="setup").length},{id:"economy",label:"Economy",description:"Money, jobs, banking, and more.",icon:"icon_economy",count:Oe.filter(t=>t.category==="economy").length},{id:"leveling",label:"Leveling",description:"XP, levels, and rankings.",icon:"icon_leveling",count:Oe.filter(t=>t.category==="leveling").length},{id:"moderation",label:"Moderation",description:"Moderation tools and commands.",icon:"icon_moderation",count:Oe.filter(t=>t.category==="moderation").length},{id:"automod",label:"AutoMod",description:"Automated moderation features.",icon:"icon_automod",count:Oe.filter(t=>t.category==="automod").length},{id:"logging",label:"Logging",description:"Server event logging.",icon:"icon_settings",count:Oe.filter(t=>t.category==="logging").length},{id:"social",label:"Social",description:"Community engagement features.",icon:"icon_heart",count:Oe.filter(t=>t.category==="social").length},{id:"utility",label:"Utility",description:"Helpful tools and utilities.",icon:"icon_utility",count:Oe.filter(t=>t.category==="utility").length},{id:"voice",label:"Voice",description:"Voice and music features.",icon:"icon_bot",count:Oe.filter(t=>t.category==="voice").length},{id:"ai",label:"AI",description:"AI-powered features.",icon:"icon_ai",count:Oe.filter(t=>t.category==="ai").length},{id:"dashboard",label:"Dashboard",description:"Web dashboard guides.",icon:"icon_settings",count:Oe.filter(t=>t.category==="dashboard").length},{id:"tips",label:"Tips",description:"Tips and best practices.",icon:"icon_lightbulb",count:Oe.filter(t=>t.category==="tips").length}];function Kg(){const[t,s]=P.useState({query:"",category:"",tags:[]}),i=P.useCallback(p=>{s(v=>({...v,query:p.toLowerCase(),tags:[]}))},[]),o=P.useCallback(p=>{s(v=>({...v,category:p,tags:[]}))},[]),c=P.useCallback(p=>{s(v=>{const g=v.tags.includes(p)?v.tags.filter(x=>x!==p):[...v.tags,p];return{...v,tags:g,query:""}})},[]),d=P.useCallback(()=>{s({query:"",category:"",tags:[]})},[]),h=P.useMemo(()=>{const{query:p,category:v,tags:g}=t;if(!p&&!v&&g.length===0)return Oe.map(w=>({page:w,score:1,highlights:[]}));const x=[];for(const w of Oe)if(!(v&&w.category!==v)&&!(g.length>0&&!g.some(k=>w.tags.includes(k))))if(p){const k=R1(w,p);if(k===0)continue;const S=L1(w,p);x.push({page:w,score:k,highlights:S})}else x.push({page:w,score:1,highlights:[]});return x.sort((w,k)=>k.score!==w.score?k.score-w.score:w.page.order-k.page.order),x},[t]),f=t.query!==""||t.category!==""||t.tags.length>0;return{filters:t,setQuery:i,setCategory:o,toggleTag:c,clearFilters:d,results:h,hasActiveFilters:f,resultCount:h.length}}function R1(t,s){let i=0;const o=s.toLowerCase();t.title.toLowerCase()===o?i+=100:t.title.toLowerCase().includes(o)&&(i+=50),t.excerpt.toLowerCase().includes(o)&&(i+=25),t.content.toLowerCase().includes(o)&&(i+=10);for(const c of t.tags)c.toLowerCase().includes(o)&&(i+=15);return t.category.toLowerCase().includes(o)&&(i+=5),i}function L1(t,s){const i=[],o=s.toLowerCase(),c=3;if(t.title.toLowerCase().includes(o)&&(i.push(t.title),i.length>=c)||t.excerpt.toLowerCase().includes(o)&&(i.push(t.excerpt),i.length>=c))return i;const d=t.content.split(`
`).filter(h=>h.trim());for(const h of d)if(h.toLowerCase().includes(o)){const f=h.replace(/#{1,6}\s?/g,"").trim();if(f.length>10&&(i.push(f),i.length>=c))break}return i}function I1(){return P.useMemo(()=>{const s={};return Oe.forEach(i=>{i.tags.forEach(o=>{s[o]=(s[o]||0)+1})}),Object.entries(s).map(([i,o])=>({tag:i,count:o})).sort((i,o)=>o.count-i.count)},[])}function V1({slug:t}){var p,v;const{setCategory:s,clearFilters:i}=Kg();P.useEffect(()=>{window.location.hash!==`#/docs/${t}`&&window.history.replaceState(null,"",`#/docs/${t}`)},[t]);const o=D1(t);if(!o)return r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"docs"}),r.jsx("main",{className:"shell page-main docs-page",children:r.jsxs("div",{className:"docs-not-found",children:[r.jsx(ee,{name:"doc",size:48,className:"not-found-icon"}),r.jsx("h1",{children:"Page Not Found"}),r.jsxs("p",{children:[`We couldn't find documentation for "`,t,'".']}),r.jsxs("div",{className:"not-found-actions",children:[r.jsx("button",{onClick:()=>he("/docs"),children:"Browse all documentation"}),r.jsx("button",{onClick:()=>{he("/docs"),i()},children:"Clear filters"})]})]})}),r.jsx(zt,{})]});const c=g=>{const x=[],w=/(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*)/g;let k=0,S,j=0;for(;(S=w.exec(g))!==null;){S.index>k&&x.push(g.slice(k,S.index));const N=S[0];if(N.startsWith("`")&&N.endsWith("`")&&N.length>2)x.push(r.jsx("code",{className:"doc-inline-code",children:N.slice(1,-1)},j++));else if(N.startsWith("[")){const B=N.match(/^\[([^\]]+)\]\(([^)]+)\)$/);B?x.push(r.jsx("a",{href:B[2],target:"_blank",rel:"noreferrer",children:c(B[1])},j++)):x.push(N)}else N.startsWith("**")?x.push(r.jsx("strong",{children:c(N.slice(2,-2))},j++)):N.startsWith("*")?x.push(r.jsx("em",{children:c(N.slice(1,-1))},j++)):x.push(N);k=S.index+N.length}return k<g.length&&x.push(g.slice(k)),x},h=(g=>{const x=g.split(`
`),w=[];let k=0,S=null,j=[];const N=()=>{if(j.length===0)return;const M=S==="ol"?"ol":"ul";w.push(r.jsx(M,{className:`doc-content-list ${S==="ol"?"doc-content-list-ol":""}`,children:j.map((L,I)=>r.jsx("li",{children:c(L)},I))},`list-${w.length}`)),j=[],S=null},B=()=>{var I;const M=w[w.length-1];P.isValidElement(M)&&((I=M.props)==null?void 0:I.className)==="doc-content-spacer"||w.push(r.jsx("div",{className:"doc-content-spacer"},`spacer-${w.length}`))};for(;k<x.length;){const L=x[k].trim();if(!L){N(),B(),k+=1;continue}if(L.startsWith("```")){N();const F=[];let V=k+1;for(;V<x.length&&x[V].trim()!=="```";)F.push(x[V]),V+=1;w.push(r.jsx("pre",{className:"doc-code-block",children:r.jsx("code",{children:F.join(`
`)})},`code-${k}`)),k=V+1;continue}if(L.startsWith("|")){N();const F=[];let V=k;for(;V<x.length&&x[V].trim().startsWith("|");){const xe=x[V].trim().replace(/^\|/,"").replace(/\|$/,"").split("|").map(se=>se.trim());F.push(xe),V+=1}const O=F.length>1&&F[1].every(xe=>/^:?-{2,}:?$/.test(xe.replace(/\s+/g,""))),oe=F[0],le=O?F.slice(2):F.slice(1);oe.length>1&&w.push(r.jsxs("table",{className:"doc-table",children:[r.jsx("thead",{children:r.jsx("tr",{children:oe.map((xe,se)=>r.jsx("th",{children:c(xe)},se))})}),r.jsx("tbody",{children:le.map((xe,se)=>r.jsx("tr",{children:xe.map((ne,Se)=>r.jsx("td",{children:c(ne)},Se))},se))})]},`table-${k}`)),k=V;continue}if(L.startsWith("### ")){N(),w.push(r.jsx("h4",{className:"doc-heading doc-heading-h4",children:L.slice(4)},`h-${k}`)),k+=1;continue}if(L.startsWith("## ")){N(),w.push(r.jsx("h3",{className:"doc-heading doc-heading-h3",children:L.slice(3)},`h-${k}`)),k+=1;continue}if(L.startsWith("# ")){N(),w.push(r.jsx("h2",{className:"doc-heading doc-heading-h2",children:L.slice(2)},`h-${k}`)),k+=1;continue}if(L.startsWith("> ")){N(),w.push(r.jsx("blockquote",{className:"doc-blockquote",children:c(L.slice(2))},`q-${k}`)),k+=1;continue}const I=L.match(/^[-*]\s+(.*)$/);if(I){S!=="ul"&&N(),S="ul",j.push(I[1]),k+=1;continue}const D=L.match(/^\d+\.\s+(.*)$/);if(D){S!=="ol"&&N(),S="ol",j.push(D[1]),k+=1;continue}N(),w.push(r.jsx("p",{className:"doc-paragraph",children:c(L)},`p-${k}`)),k+=1}return N(),w})(o.content),f=h.filter(g=>P.isValidElement(g)&&(g.type==="h2"||g.type==="h3"));return r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page docs-detail-page",children:[r.jsx("div",{className:"docs-detail-back",children:r.jsxs("button",{onClick:()=>he("/docs"),className:"back-button",children:[r.jsx(ee,{name:"arrow",size:16}),"Back to Documentation"]})}),r.jsxs("header",{className:"doc-article-header",children:[r.jsxs("div",{className:"doc-article-meta",children:[r.jsx("span",{className:"doc-category-badge",children:((p=En.find(g=>g.id===o.category))==null?void 0:p.label)||o.category}),r.jsxs("span",{className:"doc-order-badge",children:["Article #",o.order]})]}),r.jsx("h1",{className:"doc-article-title",children:o.title}),r.jsx("p",{className:"doc-article-excerpt",children:o.excerpt}),r.jsx("div",{className:"doc-article-tags",children:o.tags.map(g=>r.jsxs("span",{className:"doc-tag-pill",children:["#",g]},g))})]}),r.jsx("article",{className:"doc-article-content",children:h}),r.jsx("footer",{className:"doc-article-footer",children:r.jsx("div",{className:"doc-nav-container",children:r.jsxs("div",{className:"doc-nav-col",children:[r.jsx("span",{className:"doc-nav-label",children:"Category"}),r.jsxs("button",{className:"doc-nav-link",onClick:()=>{s(o.category),he("/docs")},children:[r.jsx(ee,{name:"arrow",size:14}),"View all ",(v=En.find(g=>g.id===o.category))==null?void 0:v.label]})]})})}),f.length>0&&r.jsxs("aside",{className:"doc-toc",children:[r.jsxs("div",{className:"toc-title",children:[r.jsx(ee,{name:"utility",size:16}),r.jsx("span",{children:"On this page"})]}),r.jsx("nav",{className:"toc-nav",children:f.map((g,x)=>{var k;const w=(k=g.props.className)==null?void 0:k.includes("doc-heading-h2");return r.jsx("a",{href:`#${w?"h2-":"h3-"}-${x}`,className:`toc-link ${w?"toc-h2":"toc-h3"}`,children:g.props.children},x)})})]})]}),r.jsx(zt,{})]})}function F1(){var I,D;const[t,s]=P.useState(!1),[i,o]=P.useState(""),[c,d]=P.useState(!1),{filters:h,setQuery:f,setCategory:p,toggleTag:v,clearFilters:g,results:x,hasActiveFilters:w,resultCount:k}=Kg(),S=I1();P.useEffect(()=>{const F=()=>{const V=window.location.hash.slice(1);if(V.startsWith("#/docs/")){const O=V.replace("#/docs/",""),oe=Oe.find(le=>le.slug===O);oe&&(o(oe.category),p(oe.category))}};return F(),window.addEventListener("hashchange",F),()=>window.removeEventListener("hashchange",F)},[]);const j=()=>{d(!0)},N=F=>{o(F),p(F),s(!1)},B=()=>{h.query||d(!1)},M=F=>{he(`/docs/${F}`),f(""),d(!1)},L=P.useMemo(()=>{const F={};return x.forEach(V=>{const O=V.page.category;F[O]||(F[O]=[]),F[O].push(V)}),F},[x]);return r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page",children:[r.jsx("div",{className:"docs-hero",children:r.jsxs("div",{className:"docs-hero-content",children:[r.jsx("div",{className:"eyebrow docs-eyebrow",children:"Documentation Center"}),r.jsxs("h1",{className:"docs-title",children:["Everything you need to know about",r.jsx("br",{}),r.jsx("span",{className:"title-accent",children:"using Niko"})]}),r.jsx("p",{className:"docs-subtitle",children:"Comprehensive guides, command references, and tips to help you get the most out of your server bot."})]})}),r.jsx("div",{className:`docs-search-section ${c?"active":""}`,children:r.jsxs("div",{className:"docs-search-container",children:[r.jsx(A1,{value:h.query,onChange:f,placeholder:"Search documentation, commands, guides...",onFocus:j,onBlur:B}),c&&h.query&&x.length>0&&r.jsxs("div",{className:"search-results-dropdown",children:[r.jsxs("div",{className:"search-results-header",children:[r.jsxs("span",{className:"results-count",children:[k," ",k===1?"result":"results"]}),r.jsx("button",{className:"clear-search-btn",onClick:()=>{f(""),g(),o("")},children:"Clear"})]}),r.jsx("div",{className:"search-results-list",children:x.slice(0,8).map((F,V)=>r.jsxs("button",{className:"search-result-item",onClick:()=>M(F.page.slug),onMouseEnter:()=>{},children:[r.jsx("div",{className:"result-icon",children:r.jsx(ee,{name:"doc",size:18})}),r.jsxs("div",{className:"result-content",children:[r.jsx("div",{className:"result-title",children:F.page.title}),r.jsx("div",{className:"result-excerpt",children:F.page.excerpt}),F.highlights.length>0&&r.jsxs("div",{className:"result-highlight",children:[F.highlights[0].slice(0,100),"..."]})]}),r.jsx(ee,{name:"arrow",size:14,className:"result-arrow"})]},F.page.slug))}),x.length>8&&r.jsx("div",{className:"search-results-footer",children:r.jsxs("span",{children:["Showing 8 of ",x.length," results. Browse all docs below."]})})]})]})}),r.jsxs("div",{className:"docs-mobile-nav",children:[r.jsx("button",{className:"mobile-menu-toggle",onClick:()=>s(!t),"aria-label":"Toggle documentation menu",children:r.jsx(ee,{name:"utility",size:20})}),t&&r.jsxs("div",{className:"mobile-nav-panel",children:[r.jsxs("div",{className:"mobile-nav-header",children:[r.jsx("h3",{children:"Documentation"}),r.jsx("button",{className:"close-menu-btn",onClick:()=>s(!1),"aria-label":"Close menu",children:r.jsx(ee,{name:"utility",size:16,className:"rotated"})})]}),r.jsx("div",{className:"mobile-nav-sections",children:En.map(F=>r.jsxs("button",{className:`mobile-nav-item ${i===F.id?"active":""}`,onClick:()=>{N(F.id)},children:[r.jsx(ee,{name:F.icon,size:18}),r.jsx("span",{className:"mobile-section-label",children:F.label}),r.jsx("span",{className:"mobile-section-count",children:F.count})]},F.id))})]})]}),S.length>0&&!w&&r.jsxs("div",{className:"docs-tags-cloud",children:[r.jsxs("div",{className:"tags-cloud-title",children:[r.jsx(ee,{name:"utility",size:16}),r.jsx("span",{children:"Popular Topics"})]}),r.jsx("div",{className:"tags-cloud-list",children:S.slice(0,15).map(({tag:F,count:V})=>r.jsxs("button",{className:"tag-cloud-item",onClick:()=>v(F),style:{fontSize:`${.75+Math.min(V/4,1)}rem`},children:["#",F,r.jsx("span",{className:"tag-count",children:V})]},F))})]}),r.jsx("div",{className:"docs-category-filters",children:r.jsx(_1,{selectedCategory:h.category,onSelectCategory:N,sections:En})}),w&&r.jsxs("div",{className:"docs-results-header",children:[r.jsxs("div",{className:"results-info",children:[r.jsxs("span",{className:"results-count-large",children:[k," ",k===1?"article":"articles"]}),h.query&&r.jsxs("span",{className:"search-query-display",children:['for "',r.jsx("strong",{children:h.query}),'"']})]}),r.jsxs("button",{className:"clear-all-btn",onClick:()=>{g(),o("")},disabled:!w,children:[r.jsx(ee,{name:"utility",size:14}),"Clear all filters"]})]}),r.jsx("div",{className:"docs-content",children:w?r.jsx("div",{className:"search-results-view",children:Object.entries(L).map(([F,V])=>{var O;return r.jsxs("section",{className:"results-category",children:[r.jsx("h2",{className:"category-title",children:((O=En.find(oe=>oe.id===F))==null?void 0:O.label)||F}),r.jsx("div",{className:"category-results-grid",children:V.map(oe=>r.jsx(ic,{doc:oe,variant:"highlighted"},oe.page.slug))})]},F)})}):i?r.jsxs("div",{className:"category-view",children:[r.jsxs("div",{className:"category-header",children:[r.jsx("h2",{className:"category-page-title",children:((I=En.find(F=>F.id===i))==null?void 0:I.label)||i}),r.jsx("p",{className:"category-description",children:(D=En.find(F=>F.id===i))==null?void 0:D.description})]}),r.jsx("div",{className:"category-articles",children:Oe.filter(F=>F.category===i).sort((F,V)=>F.order-V.order).map(F=>r.jsx(ic,{doc:F},F.slug))})]}):r.jsx("div",{className:"all-categories-view",children:En.map(F=>r.jsxs("section",{className:"docs-section",id:`section-${F.id}`,children:[r.jsxs("div",{className:"section-header",children:[r.jsx("div",{className:"section-icon",children:r.jsx(ee,{name:F.icon,size:28})}),r.jsxs("div",{className:"section-info",children:[r.jsx("h2",{className:"section-title",children:F.label}),r.jsx("p",{className:"section-description",children:F.description})]}),r.jsx("span",{className:"section-count",children:F.count})]}),r.jsx("div",{className:"section-articles",children:Oe.filter(V=>V.category===F.id).sort((V,O)=>V.order-O.order).map(V=>r.jsx(ic,{doc:V},V.slug))})]},F.id))})}),r.jsxs("div",{className:"docs-footer-note",children:[r.jsx(ee,{name:"book",size:20}),r.jsxs("div",{children:[r.jsx("strong",{children:"Want more detail?"}),r.jsxs("p",{children:["The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in the"," ",r.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"docs/"})," ","folder."]})]})]})]}),r.jsx(zt,{})]})}function B1(){const t=Rr(),[s,i]=P.useState(null);P.useEffect(()=>{fa().then(i).catch(()=>{})},[]);const o=[["spark","AI that remembers","Thoughtful conversation with a cozy personality and controls that respect your community."],["chart","A living economy","Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],["shield","Confident moderation","Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],["users","Community rituals","Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."]];return r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"home"}),r.jsxs("main",{children:[r.jsxs("section",{className:"hero shell",children:[r.jsxs("div",{className:"hero-copy",children:[r.jsxs("div",{className:"eyebrow",children:[r.jsx("span",{className:"status-dot"})," Discord companion · online"]}),r.jsxs("div",{className:"hero-identity",children:[r.jsx("span",{className:"hero-avatar",children:t!=null&&t.bot_avatar_url?r.jsx("img",{src:t.bot_avatar_url,alt:"Niko"}):"n"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Niko"}),r.jsx("small",{children:"Your server’s calm, capable co-pilot"})]})]}),r.jsxs("h1",{children:["Useful tools for a ",r.jsx("em",{children:"better server."})]}),r.jsx("p",{children:"Niko handles the everyday work of running a Discord community, so your moderators can focus on the people in it."}),r.jsxs("div",{className:"hero-buttons",children:[r.jsxs("a",{className:"button button-primary",href:(t==null?void 0:t.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Invite Niko ",r.jsx(ee,{name:"arrow"})]}),r.jsx("a",{className:"button button-muted",href:"/commands",onClick:c=>{c.preventDefault(),he("/commands")},children:"Explore commands"})]}),r.jsxs("div",{className:"stats-strip",children:[r.jsxs("div",{children:[r.jsx("strong",{children:ve(s==null?void 0:s.guild_count)}),r.jsx("span",{children:"servers"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:ve(s==null?void 0:s.user_count)}),r.jsx("span",{children:"members"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:ve(s==null?void 0:s.command_count)}),r.jsx("span",{children:"commands"})]})]})]}),r.jsx("div",{className:"hero-art","aria-label":"A preview of Niko's server workspace",children:r.jsxs("div",{className:"workspace-preview",children:[r.jsxs("div",{className:"workspace-preview-top",children:[r.jsxs("span",{className:"preview-dots",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"server workspace"}),r.jsxs("span",{className:"preview-status",children:[r.jsx("span",{className:"status-dot"})," live"]})]}),r.jsxs("div",{className:"preview-body",children:[r.jsxs("div",{className:"preview-sidebar",children:[r.jsx("span",{className:"preview-label",children:"NIKO"}),r.jsx("b",{children:"Overview"}),r.jsx("span",{children:"Economy"}),r.jsx("span",{children:"Leveling"}),r.jsx("span",{children:"Moderation"}),r.jsx("span",{children:"AI controls"})]}),r.jsxs("div",{className:"preview-main",children:[r.jsx("span",{className:"preview-label",children:"SERVER SNAPSHOT"}),r.jsx("strong",{children:"Everything in one place."}),r.jsxs("div",{className:"preview-stats",children:[r.jsxs("span",{children:[r.jsx("b",{children:ve(s==null?void 0:s.user_count)}),r.jsx("small",{children:"members"})]}),r.jsxs("span",{children:[r.jsx("b",{children:ve(s==null?void 0:s.command_count)}),r.jsx("small",{children:"commands"})]})]}),r.jsxs("div",{className:"preview-line",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]})]})]})]})})]}),r.jsxs("section",{className:"shell intro-section",children:[r.jsx("div",{className:"section-kicker",children:"Why Niko"}),r.jsxs("div",{className:"intro-grid",children:[r.jsxs("h2",{children:["The good kind of",r.jsx("br",{}),r.jsx("em",{children:"always-on."})]}),r.jsx("p",{children:"Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile."})]})]}),r.jsx("section",{className:"shell feature-grid",children:o.map(([c,d,h])=>r.jsxs("article",{className:"feature-card",children:[r.jsx("span",{className:"feature-icon",children:r.jsx(ee,{name:c})}),r.jsx("h3",{children:d}),r.jsx("p",{children:h}),r.jsxs("a",{href:"/docs",onClick:f=>{f.preventDefault(),he("/docs")},children:["Learn more ",r.jsx(ee,{name:"arrow"})]})]},d))}),r.jsxs("section",{className:"shell callout",children:[r.jsxs("div",{children:[r.jsx("div",{className:"section-kicker",children:"Ready when you are"}),r.jsxs("h2",{children:["A calmer, cleverer home",r.jsx("br",{}),"for your community."]})]}),r.jsxs("a",{className:"button button-primary",href:(t==null?void 0:t.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Bring Niko in ",r.jsx(ee,{name:"arrow"})]})]})]}),r.jsx(zt,{})]})}const O1=[{code:"USDT",label:"Tether"},{code:"ETH",label:"Ethereum"},{code:"BTC",label:"Bitcoin"},{code:"BNB",label:"BNB"},{code:"LTC",label:"Litecoin"},{code:"DOGE",label:"Dogecoin"},{code:"TRX",label:"TRON"},{code:"XMR",label:"Monero"}];function z1(){const s=new URLSearchParams(window.location.search).get("token")||"",[i,o]=P.useState("5"),[c,d]=P.useState("USDT"),[h,f]=P.useState(!1),[p,v]=P.useState(""),[g,x]=P.useState(null),[w,k]=P.useState(null),[S,j]=P.useState(!1);P.useEffect(()=>{s||j(!0)},[s]),P.useEffect(()=>{if(!(g!=null&&g.status_url)||g.paid)return;const B=setInterval(async()=>{try{const M=await Ge(g.status_url);k(M),M.paid&&clearInterval(B)}catch{}},5e3);return()=>clearInterval(B)},[g]);const N=async B=>{B.preventDefault(),f(!0),v("");try{const M=await Ge("/api/donations/invoice",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:s,amount:parseFloat(i),currency:c})});x(M),M.error&&(v(M.error),x(null))}catch(M){v(M instanceof Error?M.message:"Could not create invoice.")}finally{f(!1)}};return S?r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Invalid donation link"}),r.jsxs("h1",{children:["This link is ",r.jsx("em",{children:"invalid."})]}),r.jsxs("p",{children:["The donation link is missing or has expired. Use the"," ",r.jsx("code",{children:"/donate"})," command in Discord to generate a new one."]}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>he("/"),children:"Return home"})]})})]}):w!=null&&w.paid?r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"✓"}),r.jsx("div",{className:"eyebrow",children:"Payment confirmed"}),r.jsxs("h1",{children:["Thank you ",r.jsx("em",{children:"for supporting!"})]}),r.jsx("p",{children:"Your donation has been confirmed. You will receive the Supporter badge shortly."}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>he("/"),children:"Return home"})]})})]}):r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"home"}),r.jsx("main",{className:"page-main",children:r.jsx("div",{className:"shell",children:r.jsxs("div",{className:"page-heading",style:{maxWidth:500,margin:"0 auto"},children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:15},children:"Support Niko"}),r.jsxs("h1",{children:["Keep Niko ",r.jsx("em",{children:"running."})]}),r.jsx("p",{style:{color:"var(--muted)",marginBottom:30},children:"Your donation helps cover hosting costs and keeps Niko running for all servers. Choose an amount and cryptocurrency below."}),g!=null&&g.pay_link?r.jsxs("div",{className:"dash-panel",style:{marginBottom:24},children:[r.jsx("div",{className:"panel-heading",children:r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Invoice created"}),r.jsx("h3",{children:"Complete your payment"})]})}),r.jsxs("p",{style:{color:"var(--muted)",fontSize:12,marginBottom:16},children:["Amount: ",r.jsxs("strong",{children:["$",parseFloat(i).toFixed(2)," USD"]})," in"," ",r.jsx("strong",{children:c})]}),r.jsxs("p",{style:{color:"var(--dim)",fontSize:10,marginBottom:16},children:["Track ID: ",r.jsx("code",{children:g.track_id})," · Expires in 60 minutes"]}),r.jsxs("a",{className:"button button-primary",href:g.pay_link,target:"_blank",rel:"noopener noreferrer",children:["Pay now ",r.jsx(ee,{name:"arrow"})]}),r.jsx("p",{style:{color:"var(--dim)",fontSize:10,marginTop:12},children:"Payment will be confirmed automatically once the transaction is processed on-chain."})]}):r.jsxs("form",{onSubmit:N,className:"dash-panel",style:{marginBottom:24},children:[r.jsxs("div",{className:"form-grid",children:[r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Amount (USD)"}),r.jsx("input",{type:"number",min:"1",max:"10000",step:"0.01",value:i,onChange:B=>o(B.target.value)}),r.jsx("small",{children:"Minimum $1.00, maximum $10,000.00"})]}),r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Cryptocurrency"}),r.jsx("select",{value:c,onChange:B=>d(B.target.value),children:O1.map(B=>r.jsxs("option",{value:B.code,children:[B.label," (",B.code,")"]},B.code))})]})]}),p&&r.jsx("p",{className:"form-error",style:{marginTop:12},role:"alert",children:p}),r.jsx("div",{style:{marginTop:16},children:r.jsx("button",{className:"button button-primary",type:"submit",disabled:h,children:h?"Creating invoice…":"Create invoice"})})]}),r.jsxs("div",{className:"docs-footer-note",style:{marginTop:20},children:[r.jsx("strong",{children:"How it works"}),r.jsx("p",{children:'1. Choose an amount and currency above · 2. Click "Pay now" to open the payment page · 3. Send crypto to the displayed address · 4. Payment is confirmed automatically once processed on-chain'})]})]})})})]})}const U1={privacy:{title:"Privacy policy",intro:"Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",sections:[["Information we use","User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature. The dashboard stores daily aggregate message, join, and leave counts without message text or member IDs."],["How it is used","Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],["Storage and retention","Data is stored by the server hosting Niko in local JSON and SQLite files. Economy, leveling, and configuration data remain until removed. Daily server activity totals are retained as aggregates. AI conversation history is limited and can be cleared with /clearhistory."],["Third-party services","When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Music and external lookup features may contact their respective services."],["Your choices","Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."]]},terms:{title:"Terms of service",intro:"By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",sections:[["Permitted use","Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],["Availability","Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],["Moderation","The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],["AI content","AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],["Virtual items","In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],["Contact","Questions or concerns can be sent through the Niko support server."]]},community:{title:"Community policy",intro:"These community expectations apply to every server that uses Niko. By adding the bot to a server, the server's owners and administrators agree to uphold these standards.",sections:[["Purpose","Niko is a community companion for Discord servers of all kinds. To keep the platform safe for everyone, all servers using Niko must follow the expectations below in addition to Discord's Terms of Service and Community Guidelines."],["Discrimination and harassment","Servers must not permit or promote discrimination, harassment, or hate speech targeting people based on race, ethnicity, national origin, religion, disability, gender, gender identity or expression, sexual orientation, age, veteran status, or any other protected identity characteristic."],["Illegal and malicious content","Servers must not create, host, share, or distribute illegal or malicious content. This includes, but is not limited to: child sexual abuse material (CSAM), malware and other malicious software, gore or shock content, pirated media and/or software, content that facilitates violence or terrorism, scams and phishing, and any other content that is illegal under applicable law."],["Other prohibited conduct","Servers must not use Niko to facilitate doxxing, targeted harassment campaigns, sextortion, trafficking, or the sexualization of minors in any form."],["Enforcement and investigations","When a server is reported or flagged for potentially violating this policy, Niko will send a warning notice to the server. The notice is followed by an investigation by Niko staff. Servers that cooperate in good faith and are found not to be breaking the policies will not receive any further action."],["Obstruction of investigations","Banning, kicking, or otherwise removing the staff member(s) sent to investigate, or hiding, deleting, or tampering with potential evidence, is treated as an admission of guilt. Doing so will result in the server — and any users who are involved — being permanently blacklisted from further use of Niko, in addition to any other action the investigation warrants."],["Reporting","If you believe a server using Niko is violating this policy, report it through the Niko support server. Reports are reviewed by staff and handled confidentially."]]}};function ac({type:t}){const s=U1[t];return r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:t}),r.jsxs("main",{className:"shell page-main legal-page",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Niko legal"}),r.jsx("h1",{children:s.title}),r.jsx("p",{children:s.intro}),r.jsx("small",{children:"Effective date: 1 January 2025"})]}),r.jsx("div",{className:"legal-copy",children:s.sections.map(([i,o])=>r.jsxs("section",{children:[r.jsx("h2",{children:i}),r.jsx("p",{children:o})]},i))})]}),r.jsx(zt,{})]})}const W1=[{key:"txt",label:"TXT",icon:"📄"},{key:"html",label:"HTML",icon:"🌐"},{key:"csv",label:"CSV",icon:"📊"},{key:"json",label:"JSON",icon:"{ }"}],Xg=t=>typeof t!="number"||t<0||t>16777215?"":`#${t.toString(16).padStart(6,"0")}`,Jn=t=>(t==null?void 0:t.url)||(t==null?void 0:t.proxy_url)||"",Yg=t=>/\.(?:png|jpe?g|gif|webp|bmp|svg)(?:[?#]|$)/i.test(t)||t.startsWith("data:image/"),qg=t=>/\.(?:mp4|webm|mov|m4v|ogg)(?:[?#]|$)/i.test(t)||t.startsWith("data:video/"),$1=t=>t.url?t.url:t.id?`https://cdn.discordapp.com/stickers/${t.id}.${t.format_type===4?"gif":"png"}`:"";function H1(t){var i;const s=Jn(t);return s?(i=t==null?void 0:t.content_type)!=null&&i.startsWith("video/")?!0:qg(s):!1}const Zf=new RegExp("(`[^`\\n]+`)|(\\[([^\\]\\n]+)\\]\\((https?:\\/\\/[^\\s)\\] ]+)\\))|(\\*\\*)|(?<!\\*)\\*(?!\\*)|(~~)","g"),G1=/(https?:\/\/[^\s<>)]+)/g,ep={bold:"**",italic:"*",strike:"~~"},K1=new Set(["t","T","d","D","f","F","R"]);function X1(t,s){if(!Number.isFinite(t)||!K1.has(s))return null;const i=new Date(t*1e3);if(Number.isNaN(i.getTime()))return null;if(s==="R"){const c=t-Math.floor(Date.now()/1e3),d=Math.abs(c),h=d<60?"second":d<3600?"minute":d<86400?"hour":d<604800?"day":d<2592e3?"week":d<31536e3?"month":"year",f=h==="second"?1:h==="minute"?60:h==="hour"?3600:h==="day"?86400:h==="week"?604800:h==="month"?2592e3:31536e3;return new Intl.RelativeTimeFormat(void 0,{numeric:"always"}).format(Math.round(c/f),h)}const o={...s==="t"||s==="T"?{hour:"numeric",minute:"2-digit"}:{},...s==="T"?{second:"2-digit"}:{},...s==="d"?{year:"numeric",month:"2-digit",day:"2-digit"}:{},...s==="D"?{year:"numeric",month:"long",day:"numeric"}:{},...s==="f"?{year:"numeric",month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}:{},...s==="F"?{weekday:"long",year:"numeric",month:"long",day:"numeric",hour:"numeric",minute:"2-digit"}:{}};return new Intl.DateTimeFormat(void 0,o).format(i)}function Y1(t){const s=[];let i=0,o;const c=d=>{if(!d)return;const h=d.split(/(<a?:[A-Za-z0-9_~]+:\d+>|<t:-?\d+:[tTdDfFR]>)/g);for(const f of h){if(!f)continue;const p=f.match(/^<(a?):([A-Za-z0-9_~]+):(\d+)>$/);if(p){s.push({type:"emoji",name:p[2],id:p[3],animated:p[1]==="a"});continue}const v=f.match(/^<t:(-?\d+):([tTdDfFR])>$/);if(v){s.push({type:"timestamp",unix:Number(v[1]),style:v[2],raw:f});continue}const g=f.split(G1);for(let x=0;x<g.length;x++)g[x]&&(x%2===1?s.push({type:"link",text:g[x],url:g[x]}):s.push({type:"text",text:g[x]}))}};for(Zf.lastIndex=0;(o=Zf.exec(t))!==null;)o.index>i&&c(t.slice(i,o.index)),o[1]!==void 0?s.push({type:"code",text:o[1].slice(1,-1)}):o[2]!==void 0?s.push({type:"link",text:o[3],url:o[4]}):o[5]!==void 0?s.push({type:"marker",fmt:"bold"}):o[6]!==void 0?s.push({type:"marker",fmt:"italic"}):o[7]!==void 0&&s.push({type:"marker",fmt:"strike"}),i=o.index+o[0].length;return i<t.length&&c(t.slice(i)),s}function q1(t){const s=[],i=[],o=new Set,c=d=>{i.length>0?i[i.length-1].children.push(d):s.push(d)};for(const d of Y1(t))if(d.type==="text")c({kind:"text",text:d.text});else if(d.type==="code")c({kind:"code",text:d.text});else if(d.type==="link")c({kind:"link",text:d.text,url:d.url});else if(d.type==="emoji")c({kind:"emoji",name:d.name,id:d.id,animated:d.animated});else if(d.type==="timestamp")c({kind:"timestamp",unix:d.unix,style:d.style,raw:d.raw});else if(d.type==="marker")if(o.has(d.fmt)){const h=i.map(v=>v.fmt).lastIndexOf(d.fmt),f=i.splice(h);f.forEach(v=>o.delete(v.fmt));const p={kind:"fmt",fmt:d.fmt,children:[...f[0].children]};for(const v of f.slice(1))p.children.push({kind:"text",text:ep[v.fmt]??""}),p.children.push(...v.children);c(p)}else i.push({fmt:d.fmt,children:[]}),o.add(d.fmt);if(i.length>0)for(const d of i){c({kind:"text",text:ep[d.fmt]??""});for(const h of d.children)c(h)}return s}const Qg=(t,s)=>t.map((i,o)=>{const c=`${s}-${o}`;switch(i.kind){case"text":return r.jsx("span",{children:i.text},c);case"code":return r.jsx("code",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:4,padding:"0 5px",color:"#f2b8c2",fontFamily:"monospace",fontSize:"0.92em"},children:i.text},c);case"emoji":return r.jsx("img",{src:`https://cdn.discordapp.com/emojis/${i.id}.${i.animated?"gif":"png"}`,alt:`:${i.name}:`,title:`:${i.name}:`,style:{width:22,height:22,objectFit:"contain",verticalAlign:"-0.35em",display:"inline-block"},onError:d=>{d.currentTarget.alt=`:${i.name}:`}},c);case"timestamp":{const d=X1(i.unix,i.style);return d?r.jsx("time",{dateTime:new Date(i.unix*1e3).toISOString(),title:i.raw,children:d},c):r.jsx("span",{children:i.raw},c)}case"link":return r.jsx("a",{href:i.url,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",textDecoration:"none"},onMouseEnter:d=>{d.currentTarget.style.textDecoration="underline"},onMouseLeave:d=>{d.currentTarget.style.textDecoration="none"},children:i.text},c);case"fmt":{const d={};return i.fmt==="bold"&&(d.fontWeight=700),i.fmt==="italic"&&(d.fontStyle="italic"),i.fmt==="strike"&&(d.textDecoration="line-through"),r.jsx("span",{style:d,children:Qg(i.children,c)},c)}}}),ra=t=>Qg(q1(t),"md");function Xn({text:t,muted:s}){const i=t.split(`
`),o=[];return i.forEach((c,d)=>{const h=c.trimStart(),p=d===i.length-1?null:r.jsx("br",{},`br${d}`);h.startsWith("-# ")?o.push(r.jsxs("span",{style:{color:s?"#6d737a":"#949ba4",fontSize:12},children:[ra(h.slice(3)),p]},d)):/^#{1,4}\s/.test(h)?o.push(r.jsxs("span",{style:{color:"#f2f3f5",fontWeight:700,fontSize:16},children:[ra(h),p]},d)):h.startsWith("> ")?o.push(r.jsxs("span",{style:{display:"inline-block",color:"#b5bac1",borderLeft:"3px solid #4e5058",paddingLeft:8},children:[ra(h.slice(2)),p]},d)):h.startsWith("```")?o.push(r.jsxs("pre",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:6,padding:"10px 12px",overflowX:"auto",whiteSpace:"pre-wrap",wordBreak:"break-word",fontFamily:"monospace",fontSize:12.5,color:"#dbdee1",margin:"2px 0"},children:[h.replace(/^```[a-zA-Z]*/,"").replace(/```$/,""),p]},d)):o.push(r.jsxs("span",{children:[ra(c),p]},d))}),r.jsx("span",{style:{whiteSpace:"pre-wrap",wordBreak:"break-word"},children:o})}function Q1({embed:t}){const s=Xg(t.color)||"#5865f2",i=t.author,o=t.footer,c=Jn(t.thumbnail),d=Jn(t.image);return r.jsxs("div",{style:{display:"flex",gap:12,maxWidth:560,marginTop:8,background:"#2b2d31",border:"1px solid #3f4147",borderLeft:`4px solid ${s}`,borderRadius:6,padding:"10px 12px"},children:[r.jsxs("div",{style:{flex:1,minWidth:0},children:[(i==null?void 0:i.name)&&r.jsxs("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:4},children:[i.icon_url&&r.jsx("img",{src:i.icon_url||i.proxy_icon_url,alt:"",style:{width:18,height:18,borderRadius:"50%",verticalAlign:"-4px",marginRight:6}}),i.name]}),t.title&&r.jsx("div",{style:{color:"#00a8fc",fontWeight:600,margin:"2px 0 4px",fontSize:14},children:t.url?r.jsx("a",{href:t.url,target:"_blank",rel:"noopener noreferrer",style:{color:"inherit",textDecoration:"none"},children:r.jsx(Xn,{text:t.title})}):r.jsx(Xn,{text:t.title})}),t.description&&r.jsx("div",{style:{color:"#dbdee1",fontSize:13,lineHeight:1.5},children:r.jsx(Xn,{text:t.description})}),t.fields&&t.fields.length>0&&r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:"6px 12px",marginTop:8},children:t.fields.map((h,f)=>r.jsxs("div",{style:{flex:h.inline?"0 1 45%":"1 1 100%",minWidth:0,marginBottom:4},children:[h.name&&r.jsx("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:2},children:r.jsx(Xn,{text:h.name})}),h.value&&r.jsx("div",{style:{color:"#dbdee1",fontSize:13},children:r.jsx(Xn,{text:h.value})})]},f))}),d&&r.jsx("a",{href:d,target:"_blank",rel:"noopener noreferrer",style:{display:"block",marginTop:8},children:r.jsx("img",{src:d,alt:"",style:{maxWidth:"100%",maxHeight:300,borderRadius:4,display:"block"},onError:h=>{h.currentTarget.style.display="none"}})}),((o==null?void 0:o.text)||t.timestamp)&&r.jsxs("div",{style:{display:"flex",alignItems:"center",gap:6,marginTop:6,color:"#949ba4",fontSize:11},children:[(o==null?void 0:o.icon_url)&&r.jsx("img",{src:o.icon_url||o.proxy_icon_url,alt:"",style:{width:16,height:16,borderRadius:"50%"}}),(o==null?void 0:o.text)&&r.jsx("span",{children:o.text}),t.timestamp&&r.jsx("span",{children:String(t.timestamp).replace("T"," ").replace("+00:00"," UTC")})]})]}),c&&r.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:r.jsx("img",{src:c,alt:"",style:{width:80,height:80,borderRadius:6,objectFit:"cover"},onError:h=>{h.currentTarget.style.display="none"}})})]})}function ma({component:t}){switch(t.type){case 17:{const s=Xg(t.accent_color);return r.jsxs("div",{style:{display:"flex",overflow:"hidden",maxWidth:560,marginTop:8,background:"#2b2d31",border:`1px solid ${s||"#3f4147"}`,borderRadius:12},children:[s&&r.jsx("div",{style:{flex:"0 0 4px",background:s}}),r.jsx("div",{style:{flex:1,minWidth:0,padding:"6px 12px 8px"},children:(t.components||[]).map((i,o)=>r.jsx(ma,{component:i},o))})]})}case 1:return r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,margin:"6px 0"},children:(t.components||[]).map((s,i)=>r.jsx(ma,{component:s},i))});case 2:{const s=t.emoji,i=`${(s==null?void 0:s.name)??""}${t.label?` ${t.label}`:""}`.trim();return t.style===5&&!!t.url?r.jsx("a",{href:t.url,target:"_blank",rel:"noopener noreferrer",style:{display:"inline-block",padding:"3px 14px",background:"#5865f2",borderRadius:4,color:"#fff",fontSize:13,fontWeight:600,textDecoration:"none"},children:i||"Button"}):r.jsx("span",{style:{display:"inline-block",padding:"3px 14px",background:"#4e5058",borderRadius:4,color:t.disabled?"#8a8e96":"#f2f3f5",fontSize:13,cursor:t.disabled?"not-allowed":"default",opacity:t.disabled?.55:1},children:i||"Button"})}case 9:{const s=[...t.components||[]];return t.accessory&&s.push(t.accessory),r.jsx("div",{style:{display:"flex",alignItems:"center",gap:10,margin:"4px 0"},children:s.map((i,o)=>r.jsx(ma,{component:i},o))})}case 10:return r.jsx("div",{style:{color:"#dbdee1",fontSize:14,lineHeight:1.5,margin:"4px 0",wordBreak:"break-word"},children:r.jsx(Xn,{text:t.content||""})});case 18:return r.jsx("div",{style:{color:"#f2f3f5",fontWeight:700,textTransform:"uppercase",letterSpacing:"0.04em",fontSize:12,margin:"4px 0"},children:t.content});case 14:return r.jsx("div",{style:{margin:t.divider===!1?"6px 0":"9px 0",...t.divider===!1?{}:{borderTop:"1px solid #3f4147"}}});case 11:{const s=Jn(t.media);return s?r.jsx("a",{href:s,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:r.jsx("img",{src:s,alt:t.description||"",style:{width:40,height:40,borderRadius:"50%",objectFit:"cover",display:"block"},onError:i=>{i.currentTarget.style.display="none"}})}):null}case 12:{const i=(t.items||[]).filter(o=>Jn(o.media));return i.length===0?null:r.jsx("div",{style:{display:"grid",gridTemplateColumns:`repeat(auto-fill, minmax(${Math.min(220,Math.max(140,Math.floor(560/Math.max(1,i.length))))}px, 1fr))`,gap:6,margin:"6px 0"},children:i.map((o,c)=>{const d=Jn(o.media),h=o.description;return H1(o.media)?r.jsxs("figure",{style:{margin:0},children:[r.jsx("video",{src:d,controls:!0,preload:"metadata",style:{width:"100%",maxHeight:260,borderRadius:6,background:"#1e1f22"}}),h&&r.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:h})]},c):Yg(d)?r.jsxs("figure",{style:{margin:0},children:[r.jsx("a",{href:d,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:r.jsx("img",{src:d,alt:h||"",style:{width:"100%",maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:f=>{f.currentTarget.style.display="none"}})}),h&&r.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:h})]},c):r.jsxs("a",{href:d,target:"_blank",rel:"noopener noreferrer",style:{display:"flex",alignItems:"center",gap:6,padding:"6px 10px",background:"#383a40",borderRadius:6,color:"#dbdee1",fontSize:12,textDecoration:"none"},children:["📎 ",h||"Attachment"]},c)})})}case 13:{const s=Jn(t.media)||t.url||"";return s?r.jsxs("a",{href:s,target:"_blank",rel:"noopener noreferrer",style:{display:"block",margin:"4px 0",color:"#00a8fc",fontSize:12.5,textDecoration:"none"},children:["📎 ",t.label||"Attachment"]}):null}default:return null}}function J1({components:t}){return r.jsx(r.Fragment,{children:t.map((s,i)=>r.jsx(ma,{component:s},i))})}function Z1({text:t}){return r.jsx(Xn,{text:t})}function eS({msg:t}){const s=!!(t.attachments&&t.attachments.length>0||t.embeds&&t.embeds.length>0||t.components&&t.components.length>0||t.stickers&&t.stickers.length>0);return r.jsxs("div",{style:{padding:"10px 16px",borderBottom:"1px solid #2b2d31",fontSize:14,lineHeight:1.6},children:[r.jsxs("div",{style:{marginBottom:2},children:[r.jsx("span",{style:{color:"#949ba4",fontSize:11,fontFamily:"monospace"},children:t.timestamp})," ",r.jsx("span",{style:{color:"#f2f3f5",fontWeight:600},children:t.author})," ",r.jsxs("span",{style:{color:"#949ba4",fontSize:11},children:["(",t.author_id,")"]})]}),t.content?r.jsx("div",{style:{color:"#dbdee1"},children:r.jsx(Z1,{text:t.content})}):s?null:r.jsx("div",{style:{color:"#6d737a",fontStyle:"italic",fontSize:13},children:"Message content unavailable"}),t.attachments&&t.attachments.length>0&&r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:4},children:t.attachments.map((i,o)=>qg(i)?r.jsx("video",{src:i,controls:!0,preload:"metadata",style:{maxWidth:360,maxHeight:260,borderRadius:6,background:"#1e1f22"}},o):Yg(i)?r.jsx("a",{href:i,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:r.jsx("img",{src:i,alt:"",style:{maxWidth:300,maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:c=>{const d=c.currentTarget;d.style.display="none"}})},o):r.jsx("a",{href:i,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",fontSize:12,textDecoration:"none"},children:"📎 Attachment"},o))}),t.embeds&&t.embeds.length>0&&r.jsx(r.Fragment,{children:t.embeds.map((i,o)=>r.jsx(Q1,{embed:i},o))}),t.stickers&&t.stickers.length>0&&r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:8},children:t.stickers.map((i,o)=>{const c=$1(i);return c?r.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:r.jsx("img",{src:c,alt:i.name||"Discord sticker",title:i.name||"Discord sticker",style:{width:160,maxWidth:"100%",maxHeight:160,objectFit:"contain",display:"block"}})},o):null})}),t.components&&t.components.length>0&&r.jsx(J1,{components:t.components})]})}function tS({transcriptId:t}){const[s,i]=P.useState(null),[o,c]=P.useState(!0),[d,h]=P.useState("");P.useEffect(()=>{c(!0),h(""),fetch(`/api/transcript/${t}`).then(p=>{if(!p.ok)throw new Error("Transcript not found");return p.json()}).then(p=>{i(p),c(!1)}).catch(p=>{h(p.message||"Failed to load transcript"),c(!1)})},[t]);const f=p=>{window.open(`/api/transcript/${t}/download?format=${p}`,"_blank")};return o?r.jsx("div",{className:"page-main",children:r.jsx("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:r.jsx("div",{style:{color:"var(--muted)",fontSize:14},children:"Loading transcript…"})})}):d||!s?r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:[r.jsx("h2",{style:{marginBottom:12},children:"Transcript not found"}),r.jsx("p",{style:{color:"var(--muted)"},children:d||"This transcript doesn't exist or has been deleted."})]})}):r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{maxWidth:800},children:[r.jsx("div",{style:{background:"var(--surface)",border:"1px solid var(--line)",borderRadius:8,padding:24,marginBottom:20},children:r.jsxs("div",{style:{display:"flex",alignItems:"flex-start",justifyContent:"space-between",gap:16,flexWrap:"wrap"},children:[r.jsxs("div",{children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:8},children:"Ticket Transcript"}),r.jsxs("h1",{style:{fontSize:24,letterSpacing:"-0.04em",margin:0},children:["#",s.channel_name]}),r.jsxs("div",{style:{color:"var(--muted)",fontSize:13,marginTop:6},children:[s.category," · ",s.message_count," messages · ",s.created_at]})]}),r.jsx("div",{style:{display:"flex",gap:8,flexWrap:"wrap"},children:W1.map(p=>r.jsxs("button",{className:"button button-small button-muted",onClick:()=>f(p.key),style:{minWidth:70},children:[r.jsx("span",{children:p.icon}),r.jsx("span",{children:p.label})]},p.key))})]})}),r.jsxs("div",{style:{background:"#1e1f22",border:"1px solid #3f4147",borderRadius:8,overflow:"hidden"},children:[s.messages.map((p,v)=>r.jsx(eS,{msg:p},v)),s.messages.length===0&&r.jsx("div",{style:{padding:40,textAlign:"center",color:"#949ba4"},children:"No messages in this transcript."})]}),r.jsxs("div",{style:{marginTop:16,padding:"12px 0",textAlign:"center",color:"var(--dim)",fontSize:12},children:["Transcript ID: ",r.jsx("code",{style:{fontFamily:"monospace"},children:t})]})]})})}const Ea=[{slug:"team-page-ai-name-config",title:"Team Profiles & Custom AI Names",date:"2026-09-22",version:"2.10.0",tags:["team","staff","dashboard","ai","website"],summary:"Niko's public website now introduces the people behind the bot, while server owners can give their AI a custom name and manage its experimental capabilities from the dashboard.",highlights:[{title:"Meet the Niko Team",description:"The new Team page showcases owners, developers, moderators, support staff, and other persisted staff roles with Discord-synced identities, presence, activities, bios, and profile pages.",icon:"users"},{title:"Choose Your AI's Name",description:"Server administrators can configure the AI's display name from the dashboard or the AI configuration command. The chosen name is used for mention detection and reply identity in that server.",icon:"spark"},{title:"Staff Public Listings",description:"Staff members can customize their public bio, banner, and visibility while their name and avatar remain synchronized with Discord.",icon:"settings"}],changes:[{category:"added",items:["Public Team page with persisted staff roles and linked staff profiles","Discord-synced staff presence, current activities, Spotify, streaming, and custom status display","Staff self-service controls for public bio, banner, and Team page visibility","Configurable per-server AI name in the dashboard and AI configuration command","Dashboard controls for AI Actions, Better Context, and Multimodal Conversation experiments","Learn-more dialogs explaining each AI experiment"]},{category:"improved",items:["Dashboard staff workspace navigation and responsive layout","Team profile cards and profile-page activity presentation","AI configuration persistence through the shared database","Public page metadata and favicon handling during the website build"]},{category:"fixed",items:["Team presence labels showing online staff as away","Spotify and streaming activities being hidden behind custom statuses","Staff profile updates being rejected for authorized owners","Staff profile avatars being clipped by profile banners"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Team",value:"1",detail:"new public experience",color:"#66866f"},{label:"AI",value:"4",detail:"new configuration controls",color:"#d96545"},{label:"Profiles",value:"3",detail:"public staff controls",color:"#4a7fb5"}]},commits:[]},{slug:"september-platform-updates",title:"September Platform Updates",date:"2026-09-21",version:"2.9.0",tags:["dashboard","ai","tickets","music","website"],summary:"A broad set of public improvements landed across Niko: richer ticket transcripts, a multimodal AI experiment, more reliable music playback, a redesigned dashboard experience, persistent giveaways and suggestions, and a refreshed public website with dynamic social previews.",highlights:[{title:"More Natural AI Conversations",description:"The new opt-in Multimodal Conversation experiment can understand image attachments and transcribe voice messages before generating a reply, while safely falling back to text when media processing is unavailable.",icon:"spark"},{title:"Richer Ticket Transcripts",description:"Transcript pages and HTML downloads now render Discord custom emojis, stickers, and dynamic timestamps such as <t:1788800225:f> in a more faithful format.",icon:"doc"},{title:"Dashboard & Website Refresh",description:"Dashboard navigation and mobile layouts were refined, documentation was expanded, and public routes now receive route-specific Open Graph cards generated during the build.",icon:"settings"},{title:"Reliable Long-Running Features",description:"Giveaways and suggestions now restore their state from the main database at startup, while music nodes are rescanned periodically to keep playback available.",icon:"utility"}],changes:[{category:"added",items:["Opt-in Multimodal Conversation AI experiment for image understanding and voice-message transcription","Official update notification system with a configurable server notification channel","Discord custom emoji and sticker rendering in ticket transcript pages and HTML downloads","Dynamic Discord timestamp rendering in ticket transcripts","Persistent suggestion configuration and voting buttons restored from the main database","Automatic hourly Lavalink node rescans with a hardcoded fallback node catalog","Additional economy SVG card API endpoints","Community Policy page on the public website","Route-specific Open Graph metadata and generated social preview cards"]},{category:"improved",items:["Dashboard navigation consistency and mobile layout","Dashboard page layout and visual polish","Music connection reliability, autoplay, Spotify playback, and node recovery","Giveaway persistence and startup restoration for MongoDB-backed data","Onboarding setup handling and configuration persistence","Poll command design and interaction flow","Ticket transcript HTML download formatting","Economy image-card font rendering, SVG output, and emoji support","Documentation pages and public website frontend"]},{category:"fixed",items:["Giveaways losing their live buttons after a restart or extended runtime","Suggestion buttons and configuration not surviving process restarts","Ticket transcript rendering for custom media and dynamic timestamps","Lavalink connection failures and stale music nodes","Broken SVG card and SVG endpoint output","Status panel polling noise and retired image-model defaults"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Added",value:"9",detail:"new capabilities",color:"#66866f"},{label:"Improved",value:"9",detail:"upgraded systems",color:"#4a7fb5"},{label:"Fixed",value:"6",detail:"reliability issues",color:"#d96545"}]},commits:["ac102df Fixed the Open Graph image cards","33aaf12 Added dynamic Open Graph tags to the website","3153e28 Rebuilt the frontend","bab665e Added a new Lavalink node","ee44a5e Improved the music cog","bc61e34 Released the new Multimodal Conversation AI experiment","c46af7d Fixed the suggestion system persistence","25703ca Added a broadcast system for official updates and announcements","265bdb2 Added dynamic timestamp rendering inside ticket transcripts","d8005db Added custom emoji and sticker rendering to ticket transcripts","e561d84 Fixed the dashboards navbar","a0bab78 Improved the dashboards mobile layout","fb2f5aa Patched giveaway persistence for MongoDB compatibility","d77779e Fixed several dashboard flaws","b8e06a5 Improved the dashboard pages","3708207 Patched issues in the giveaway and onboarding cogs","d58bb37 Redesigned the poll command","bb523e3 Added a Community Policy page","5b34c7c Updated the documentation pages","3a52fc2 Added new economy card API endpoints","df3ea25 Fixed an issue in the SVG endpoints","39b7340 Fixed an error in the SVG cards","9e3483e Replaced HTML entities with valid XML numeric character references in economy cards"]},{slug:"economy-leveling-overhaul",title:"Economy Items, Leveling Cards & Subcommands",date:"2026-09-08",version:"2.8.0",tags:["economy","leveling","shop","image-cards"],summary:"The economy shop expanded with four new consumable items that affect gameplay — Rigged Coin, Streak Insurance, Double Down Token, and Lucky Horseshoe — plus daily streak milestone bonuses at 7, 14, 30, 60, and 90 days. The leveling system now renders rank cards and leaderboards as customizable image cards, and all leveling commands live under a single `/leveling` group with subcommands.",highlights:[{title:"New Shop Items",description:"Four new consumables: Rigged Coin (60/40 coinflip odds), Streak Insurance (protects daily streak for one missed day), Double Down Token (1.5x gambling payout), and Lucky Horseshoe (+10% work reward).",icon:"chart"},{title:"Leveling Image Cards",description:"Rank cards and the leaderboard now render as styled images with avatar, level, XP bar, and rank. Server admins can customize the card accent color and background gradient.",icon:"spark"},{title:"Leveling Subcommands",description:"All leveling commands reorganized under `/leveling` with `rank`, `leaderboard`, `panel`, and `config` subcommands. The leaderboard now has interactive pagination buttons.",icon:"settings"},{title:"Daily Streak Milestones",description:"Hitting 7, 14, 30, 60, or 90-day daily streaks now awards bonus items from the shop (Espresso Shots, Lockpicks, Lucky Charms, Rob Shields) along with a coin bonus.",icon:"utility"}],changes:[{category:"added",items:["Coinflip command with heads/tails call and double-or-nothing payout","Rigged Coin shop item — gives 60/40 coinflip odds for one use","Streak Insurance shop item — protects daily streak if you miss one day","Double Down Token shop item — next gambling win pays 1.5x","Lucky Horseshoe shop item — next work reward gets +10%","Daily streak milestone bonuses at 7/14/30/60/90 days with item rewards","Image card rendering for `/leveling rank` with customizable accent and background","Image card rendering for the leveling leaderboard","Inventory display as an image card in the shop command","Twemoji emoji rendering in economy card images","Pagination buttons (◀ ▶) on the leveling leaderboard","Card customization fields in the database: card_accent, card_bg_top, card_bg_bottom"]},{category:"improved",items:["Leveling commands restructured as `/leveling rank`, `leaderboard`, `panel`, `config` subcommands","Shop command visual layout with better font rendering on economy image cards","Crime and rob commands now check for gambling_boost effect for 1.5x payout","HTML download format for ticket transcripts","Dashboard UI refinements"]},{category:"fixed",items:["Command name conflicts between leveling and other cogs","Missing import in leveling cog after image card addition","Duplicate command alias in leveling system","Command name conflict in the gambling cog"]}],chart:{type:"bar",title:"New Shop Items & Their Effects",data:[{label:"Rigged Coin",value:3e3,color:"#c9a84c"},{label:"Streak Insurance",value:4e3,color:"#4a7fb5"},{label:"Double Down Token",value:5e3,color:"#d96545"},{label:"Lucky Horseshoe",value:2500,color:"#66866f"}]},commits:["41d86fb Expanded the gambling and economy system","bd6a09c Added image cards to the leveling system","5307bb1 Moved the leveling commands to the levels subcommand","dafd224 Added an image card to the inventory command","49fc83b Added emoji rendering to the shop command","0aca6ba Improved the shop command","30c9735 Added better font rendering to the economy system image cards","2b96835 Fixed a command name conflict","158ad8f Fixed a command name conflict in the gambling cog","d465598 Fixed a missing import","1f24ffb Fixed a duplicate command alias"]},{slug:"database-migration",title:"Database Migration to MongoDB",date:"2026-09-03",version:"2.7.0",tags:["database","mongodb","migration","infrastructure"],summary:"Every major system has been migrated from SQLite to MongoDB. The migration covered economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and the blacklist — with a custom interpreter that translates SQLite-style writes to MongoDB operations.",highlights:[{title:"Full MongoDB Migration",description:"Economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and blacklist now all store data in MongoDB instead of SQLite.",icon:"settings"},{title:"Slash Command Sync Safeguard",description:"A new check prevents redundant Discord API calls when all commands are already registered, reducing rate-limit issues on startup.",icon:"utility"},{title:"Proxy Integration",description:"A new proxy manager reduces downtime on shared hosting environments by routing API requests through a proxy layer.",icon:"shield"}],changes:[{category:"migrated",items:["Economy system — balances, banks, jobs, achievements, inventory","Leveling system — XP, levels, role rewards, card customization","Moderation system — warnings, mutes, automod config","Ticket system — panels, transcripts, support roles","Birthday system — dates, channels, messages","AFK system — status, timestamps","Sticky messages — content, channels","Blacklist — users, words, filters"]},{category:"added",items:["MongoDB interpreter that translates SQLite-style writes to proper MongoDB operations","Proxy manager for shared hosting reliability","Slash command sync safeguard to prevent redundant API calls","Context menu command support in the sync utility"]},{category:"fixed",items:["MongoDB interpreter not translating all SQLite write patterns correctly","Economy interest calculation after migration","Birthday system data persistence","Several database connection issues across various cogs","Leveling database initialization issue"]}],chart:{type:"donut",title:"Systems Migrated to MongoDB",centerLabel:"8 systems",data:[{label:"Economy",value:1,color:"#d96545"},{label:"Leveling",value:1,color:"#66866f"},{label:"Moderation",value:1,color:"#4a7fb5"},{label:"Tickets",value:1,color:"#c9a84c"},{label:"Birthdays",value:1,color:"#b07cc6"},{label:"AFK",value:1,color:"#e0976e"},{label:"Sticky Msgs",value:1,color:"#7ca898"},{label:"Blacklist",value:1,color:"#8c918e"}]},commits:["c07f9b1 Fixed the MongoDB interpreter to properly translate all SQLite database writes","0d3aca5 Migrated the blacklist to the main database","954ebac Migrated the birthday system to the main database","5013d54 Migrated the warns and mutes to use the main database","f29c217 Migrated the afk system to the main database","5732b48 Migrated the sticky messages to use the main database","b0524f1 Migrated the ticket system to the main database","70e6d7a Fixed the sync util to support context commands and slash groups","2c01817 Added a safeguard to prevent slash command syncs when all commands are already present","121afcf Added a proxy integration to reduce downtime on shared hosting","9f2f1fd Fixed several database issues across various cogs"]},{slug:"ticket-system-transcripts",title:"Ticket Transcripts & VoiceMaster",date:"2026-09-03",version:"2.6.0",tags:["tickets","transcripts","voicemaster"],summary:"The ticket system gained a web-based transcript viewer that renders ticket conversations as styled HTML pages. The VoiceMaster was also improved with better reliability and database usage. Ticket transcripts can now be downloaded as HTML or viewed online.",highlights:[{title:"Web Transcript Viewer",description:"Ticket transcripts are now rendered as styled HTML pages that can be viewed online. The HTML download format was also improved for better readability.",icon:"doc"},{title:"VoiceMaster Reliability",description:"The VoiceMaster (temporary voice channels) was improved with better database usage and reliability fixes.",icon:"utility"},{title:"Donation Dashboard Page",description:"A new customization page in the dashboard lets server admins configure donation settings without using commands.",icon:"settings"}],changes:[{category:"added",items:["Web-based ticket transcript viewer with styled HTML output","Ticket transcript database table for storing transcripts online","Dashboard customization page for donation system settings"]},{category:"improved",items:["HTML download format for ticket transcripts","VoiceMaster reliability and database usage patterns","Ticket system persistence and data handling"]},{category:"fixed",items:["Ticket transcript pages rendering incorrectly","Ticket system data loss on restart","Ticket transcript generation issues","Ticket transcript page display bugs"]}],commits:["e953321 Added a new web transcript feature to the ticket system","aa0b73b Improved the donation system and added a customization page to the dashboard","3255385 Improved the html download format for the ticket transcripts","45f1fb0 Fixed the ticket system persistence","ef4e057 Added the ticket system database migrations","d4e0bc8 Fixed the ticket transcripts","4bf5e04 Fixed an issue with the ticket transcript pages","e8dbcb0 Improved the VoiceMaster reliability and improved the database usage"]},{slug:"roleplay-music-status",title:"Roleplay, Music & Status Rotation",date:"2026-09-05",version:"2.5.0",tags:["roleplay","music","status","social"],summary:"The roleplay cog was completely rewritten to use nekos.best API GIFs with CV2 layout messages and a persistent 'hug back' button. The music cog was restructured with a ghost queue feature and fixed autoplay/Spotify playback. A status message rotation system was added with a configurable timer.",highlights:[{title:"Roleplay Rewrite",description:"The roleplay cog now fetches SFW reaction GIFs from nekos.best, renders them in styled CV2 containers, and includes a 'hug back' button that persists across restarts. A single user context menu replaces individual action menus to stay under Discord's 15-command cap.",icon:"users"},{title:"Music Ghost Queue",description:"A new ghost queue feature lets songs be queued even when nothing is currently playing. Autoplay and Spotify playback were also fixed.",icon:"utility"},{title:"Status Rotation",description:"The bot now rotates through configurable status messages on a timer (default 30s interval), with activity types and a VR device presence.",icon:"spark"}],changes:[{category:"added",items:["Status message rotation with configurable interval and activity types","Persistent status panel command for the support server (owner only)","Roleplay block feature to prevent specific users from being targeted","Ghost queue feature — queue songs even when nothing is playing","User context menu for roleplay actions (replaces per-action menus)","YouTube channel name validation for notification system"]},{category:"improved",items:["Roleplay cog complete rewrite — nekos.best GIFs, CV2 layouts, persistent buttons","Social media notification emoji formatting (Bluesky, Reddit, TikTok, Twitch icons)","Music node connection system and autoplay reliability","Spotify playback quality","Music cog restructured with better error handling"]},{category:"fixed",items:["Status rotator startup errors and activity conflicts","on_ready event error handling and reliability","Lavalink connection bug","Roleplay prefix command handling","Bluesky and Reddit notification delivery issues"]}],commits:["0c58178 Redesigned the roleplay cog","6c4ee09 Fixed the roleplay prefix commands","f1f8591 Added a roleplay block feature","e01e3e4 Added status message rotation","5e63e1d Added a persistent status panel","ae7501a Restructured the music cog","526813e Added a new ghost queue feature to the music cog","6524da1 Improved the music node connection system, fixed the autoplay, and fixed the Spotify playback","4264677 Fixed a lavalink connection bug","d62ead8 Improved the social media notification system's emojis","0f0305d Improved the social media notification formatting","42069d4 Added proper channel name validation to the YouTube notification system"]},{slug:"moderation-logging-dashboard",title:"Logging, Moderation & Documentation",date:"2026-09-07",version:"2.4.0",tags:["logging","moderation","documentation","dashboard"],summary:"Logging got two major improvements: deleted message logs now show image attachments in a MediaGallery component, and the Member category now tracks avatar changes using a Section with Thumbnail accessory. The documentation page was fully rebuilt with search, filters, and a card-based layout.",highlights:[{title:"Image Attachments in Logs",description:"Deleted message logs now render attached images in a MediaGallery component inside the log container, so moderators can see what was posted without leaving Discord.",icon:"chart"},{title:"Avatar Change Tracking",description:"The Member logging category now detects avatar changes (global and server avatars) and displays them in a Section with a Thumbnail accessory showing the new avatar.",icon:"users"},{title:"Documentation Redesign",description:"The documentation page was rebuilt from scratch with a search bar, category filters, tag cloud, card-based layout, and individual article pages with table of contents.",icon:"doc"}],changes:[{category:"added",items:["Image attachments rendered in deleted message logs via MediaGallery","Avatar change detection in Member logging with Section + Thumbnail display","Startup economy cache that loads all users into memory for accurate leaderboards","Error handler for role menu post buttons","Full-text search with result highlighting in documentation","Category filters and tag cloud in documentation","Individual documentation article pages with table of contents"]},{category:"improved",items:["Logging system now supports media_urls, thumbnail_url, and files parameters","Commands page expanded with better organization","Dashboard UI refinements","Economy interest feature — skips malformed records with non-integer user IDs"]},{category:"fixed",items:["Logging command issues","Documentation command references","Status device detection issue","Status rotator conflicts between multiple status types","on_ready event reliability with proper error handling"]}],commits:["722a34f Added avatar updates to the logging cogs Member logs","1d82ea1 Moved file attachments inside the main log message for the deleted message logs","358d537 Added a startup economy cache to fix the leaderboard","566e0c4 Improved the dashboard","132bcbb Fully redesigned the documentation page","4f7a89a Improved the commands page","6d953b6 Fixed the logging command","a202687 Fixed some documentation issues","49d22ad Fixed the documentation command references","52de287 Added an error handler to the post role menu button"]},{slug:"website-launch-donation",title:"Website, Donation System & API",date:"2026-09-02",version:"2.3.0",tags:["website","donations","api"],summary:"The public website and documentation portal launched with a React + Vite frontend, documentation center with search, and a commands reference page. The donation system gained a dashboard customization page, and the Flask API backend was fixed to use proper database calls.",highlights:[{title:"Public Website",description:"A complete public website built with React and Vite featuring a landing page, documentation center, command reference, dashboard, and legal pages.",icon:"spark"},{title:"Documentation Center",description:"The documentation page was redesigned with a card-based layout, individual article pages, and a modern visual design matching the bot's aesthetic.",icon:"doc"},{title:"Donation Dashboard",description:"Server admins can now configure donation settings through a new dashboard page instead of relying solely on commands.",icon:"settings"}],changes:[{category:"added",items:["Public website with landing page, documentation center, and command reference","Donation system customization page in the dashboard","Ticket transcript viewer web page","Donate page with Oxapay integration"]},{category:"improved",items:["Flask API to use proper database calls instead of direct SQLite access","Website commands page with expanded details","Database layer reliability for production"]},{category:"fixed",items:["Flask API database call issues","Several database-related bugs across cogs","node_modules folder accidentally committed to repository"]}],commits:["132bcbb Fully redesigned the documentation page","aa0b73b Improved the donation system and added a customization page to the dashboard","bd5e3be Expanded the website's commands page","e266644 Fixed the flask API to use the proper database calls","e99ed47 Fixed several database related issues","c783514 Minor API fixes and improvements","0df4478 Added the node_modules folder to the gitignore file"]}];function nS(t){return Ea.find(s=>s.slug===t)}function sS(){const t=new Set;return Ea.forEach(s=>s.tags.forEach(i=>t.add(i))),Array.from(t).sort()}function rS(){const[t,s]=P.useState(""),i=sS(),o=t?Ea.filter(c=>c.tags.includes(t)):Ea;return r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"home"}),r.jsxs("main",{className:"shell page-main changelog-page",children:[r.jsxs("div",{className:"changelog-hero",children:[r.jsxs("div",{className:"eyebrow",children:[r.jsx("span",{className:"status-dot"})," What's new"]}),r.jsxs("h1",{className:"changelog-title",children:["Changelog",r.jsx("br",{}),r.jsx("span",{className:"title-accent",children:"& updates"})]}),r.jsx("p",{className:"changelog-subtitle",children:"A record of every improvement, fix, and new feature added to Niko. Grouped by release for clarity."})]}),r.jsxs("div",{className:"changelog-tags",children:[r.jsx("button",{className:`changelog-tag-btn ${t===""?"active":""}`,onClick:()=>s(""),children:"All"}),i.slice(0,12).map(c=>r.jsx("button",{className:`changelog-tag-btn ${t===c?"active":""}`,onClick:()=>s(c),children:c},c))]}),r.jsx("div",{className:"changelog-timeline",children:o.map((c,d)=>r.jsxs("article",{className:"changelog-entry",children:[r.jsxs("div",{className:"changelog-entry-date-col",children:[r.jsx("div",{className:"changelog-date-dot"}),d<o.length-1&&r.jsx("div",{className:"changelog-date-line"})]}),r.jsxs("div",{className:"changelog-entry-card",children:[r.jsxs("div",{className:"changelog-entry-header",children:[r.jsxs("div",{className:"changelog-entry-meta",children:[r.jsx("time",{className:"changelog-entry-date",children:new Date(c.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),c.version&&r.jsxs("span",{className:"changelog-version",children:["v",c.version]})]}),r.jsx("h2",{className:"changelog-entry-title",children:c.title}),r.jsx("p",{className:"changelog-entry-summary",children:c.summary})]}),r.jsx("div",{className:"changelog-entry-highlights",children:c.highlights.slice(0,2).map(h=>r.jsxs("div",{className:"changelog-highlight-mini",children:[r.jsx("span",{className:"highlight-mini-icon",children:r.jsx(ee,{name:h.icon,size:16})}),r.jsxs("div",{children:[r.jsx("strong",{children:h.title}),r.jsxs("p",{children:[h.description.slice(0,120),"..."]})]})]},h.title))}),r.jsx("div",{className:"changelog-entry-tags",children:c.tags.map(h=>r.jsx("span",{className:"changelog-tag",children:h},h))}),r.jsxs("button",{className:"changelog-read-more",onClick:()=>{he(`/changelog/${c.slug}`)},children:["Read full release notes ",r.jsx(ee,{name:"arrow",size:14})]})]})]},c.slug))}),o.length===0&&r.jsxs("div",{className:"changelog-empty",children:[r.jsx(ee,{name:"doc",size:40}),r.jsx("p",{children:"No changelog entries match this filter."})]})]}),r.jsx(zt,{})]})}function iS({slug:t}){const s=nS(t);return s?r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"home"}),r.jsxs("main",{className:"shell page-main changelog-page changelog-detail",children:[r.jsx("div",{className:"changelog-back",children:r.jsxs("button",{onClick:()=>he("/changelog"),className:"back-button",children:[r.jsx(ee,{name:"arrow",size:16}),"Back to Changelog"]})}),r.jsxs("header",{className:"changelog-detail-header",children:[r.jsxs("div",{className:"changelog-detail-meta",children:[r.jsx("time",{children:new Date(s.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),s.version&&r.jsxs("span",{className:"changelog-version",children:["v",s.version]})]}),r.jsx("h1",{children:s.title}),r.jsx("p",{className:"changelog-detail-summary",children:s.summary}),r.jsx("div",{className:"changelog-detail-tags",children:s.tags.map(i=>r.jsx("span",{className:"changelog-tag",children:i},i))})]}),r.jsxs("section",{className:"changelog-highlights-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"Highlights"}),r.jsx("div",{className:"changelog-highlights-grid",children:s.highlights.map(i=>r.jsxs("div",{className:"changelog-highlight-card",children:[r.jsx("span",{className:"highlight-icon",children:r.jsx(ee,{name:i.icon,size:22})}),r.jsx("h3",{children:i.title}),r.jsx("p",{children:i.description})]},i.title))})]}),s.chart&&r.jsx(aS,{chart:s.chart}),r.jsxs("section",{className:"changelog-changes-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"All Changes"}),r.jsx("div",{className:"changelog-changes-grid",children:s.changes.map(i=>r.jsxs("div",{className:`changelog-change-group changelog-change-${i.category}`,children:[r.jsx("h3",{className:"change-group-title",children:r.jsx("span",{className:`change-badge change-badge-${i.category}`,children:i.category})}),r.jsx("ul",{children:i.items.map((o,c)=>r.jsx("li",{children:o},c))})]},i.category))})]}),s.commits.length>0&&r.jsxs("section",{className:"changelog-commits-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"Commits"}),r.jsx("div",{className:"changelog-commits-list",children:s.commits.map(i=>{const[o,...c]=i.split(" ");return r.jsxs("div",{className:"changelog-commit",children:[r.jsx("code",{className:"commit-hash",children:o.slice(0,7)}),r.jsx("span",{className:"commit-msg",children:c.join(" ")})]},o)})})]}),r.jsx("nav",{className:"changelog-detail-nav",children:r.jsxs("button",{onClick:()=>he("/changelog"),children:[r.jsx(ee,{name:"arrow",size:14}),"All releases"]})})]}),r.jsx(zt,{})]}):r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"home"}),r.jsx("main",{className:"shell page-main changelog-page",children:r.jsxs("div",{className:"changelog-not-found",children:[r.jsx(ee,{name:"doc",size:48}),r.jsx("h1",{children:"Entry Not Found"}),r.jsxs("p",{children:[`We couldn't find a changelog entry for "`,t,'".']}),r.jsx("button",{onClick:()=>he("/changelog"),children:"View all changelog entries"})]})}),r.jsx(zt,{})]})}function aS({chart:t}){return r.jsxs("section",{className:"changelog-chart-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:t.title}),r.jsxs("div",{className:"changelog-chart-container",children:[t.type==="bar"&&r.jsx(oS,{chart:t}),t.type==="pie"&&r.jsx(lS,{chart:t}),t.type==="donut"&&r.jsx(cS,{chart:t}),t.type==="line"&&r.jsx(uS,{chart:t}),t.type==="timeline"&&r.jsx(dS,{chart:t}),t.type==="comparison"&&r.jsx(mS,{chart:t}),t.type==="metrics"&&r.jsx(hS,{chart:t})]})]})}function oS({chart:t}){const s=Math.max(...t.data.map(i=>i.value));return r.jsx("div",{className:"chart-bar",children:t.data.map(i=>r.jsxs("div",{className:"chart-bar-row",children:[r.jsx("span",{className:"chart-bar-label",children:i.label}),r.jsxs("div",{className:"chart-bar-track",children:[r.jsx("div",{className:"chart-bar-fill",style:{width:`${i.value/s*100}%`,background:i.color||"var(--accent)"}}),r.jsx("span",{className:"chart-bar-value",children:i.value})]})]},i.label))})}function lS({chart:t}){const s=t.data.reduce((d,h)=>d+h.value,0);let i=0;const c=t.data.map(d=>{const h=i/s*360;i+=d.value;const f=i/s*360;return{...d,start:h,end:f}}).map(d=>{const h=d.start/360*100,f=d.end/360*100;return`${d.color||"#d96545"} ${h}% ${f}%`}).join(", ");return r.jsxs("div",{className:"chart-pie-wrapper",children:[r.jsx("div",{className:"chart-pie",style:{background:`conic-gradient(${c})`}}),r.jsx("div",{className:"chart-pie-legend",children:t.data.map(d=>r.jsxs("div",{className:"chart-legend-item",children:[r.jsx("span",{className:"chart-legend-dot",style:{background:d.color||"var(--accent)"}}),r.jsx("span",{className:"chart-legend-label",children:d.label})]},d.label))})]})}function cS({chart:t}){const s=t.data.reduce((o,c)=>o+c.value,0),i=t.data.reduce((o,c)=>{const d=o.current/s*100,h=(o.current+c.value)/s*100;return o.css+=`${c.color||"#d96545"} ${d}% ${h}%, `,o.current+=c.value,o},{css:"",current:0}).css.slice(0,-2);return r.jsxs("div",{className:"chart-donut-wrapper",children:[r.jsx("div",{className:"chart-donut",style:{background:`conic-gradient(${i})`},children:r.jsx("span",{children:t.centerLabel||s})}),r.jsx("div",{className:"chart-pie-legend",children:t.data.map(o=>r.jsxs("div",{className:"chart-legend-item",children:[r.jsx("span",{className:"chart-legend-dot",style:{background:o.color||"var(--accent)"}}),r.jsx("span",{className:"chart-legend-label",children:o.label})]},o.label))})]})}function uS({chart:t}){const s=Math.max(...t.data.map(o=>o.value),1),i=t.data.map((o,c)=>{const d=t.data.length===1?50:c/(t.data.length-1)*100,h=100-o.value/s*82-9;return`${d},${h}`}).join(" ");return r.jsxs("div",{className:"chart-line-wrapper",children:[r.jsxs("svg",{className:"chart-line",viewBox:"0 0 100 100",preserveAspectRatio:"none",role:"img","aria-label":t.title,children:[r.jsx("polyline",{points:i,fill:"none",stroke:"var(--accent)",strokeWidth:"3",vectorEffect:"non-scaling-stroke"}),t.data.map((o,c)=>{const d=t.data.length===1?50:c/(t.data.length-1)*100,h=100-o.value/s*82-9;return r.jsx("circle",{cx:d,cy:h,r:"3",fill:"var(--accent)",vectorEffect:"non-scaling-stroke"},o.label)})]}),r.jsx("div",{className:"chart-line-labels",children:t.data.map(o=>r.jsx("span",{children:o.label},o.label))})]})}function dS({chart:t}){const s=Math.max(...t.data.map(i=>i.value),1);return r.jsx("div",{className:"chart-timeline",children:t.data.map(i=>r.jsxs("div",{className:"chart-timeline-item",children:[r.jsx("div",{className:"chart-timeline-marker",style:{background:i.color||"var(--accent)"}}),r.jsxs("div",{className:"chart-timeline-content",children:[r.jsx("strong",{children:i.label}),r.jsx("div",{className:"chart-timeline-track",children:r.jsx("div",{className:"chart-timeline-fill",style:{width:`${i.value/s*100}%`,background:i.color||"var(--accent)"}})}),i.detail&&r.jsx("span",{children:i.detail})]})]},i.label))})}function hS({chart:t}){return r.jsx("div",{className:"chart-metrics",children:t.data.map(s=>r.jsxs("div",{className:"chart-metric",style:{borderTopColor:s.color||"var(--accent)"},children:[r.jsx("span",{className:"chart-metric-label",children:s.label}),r.jsx("strong",{children:s.value}),s.detail&&r.jsx("small",{children:s.detail})]},s.label))})}function mS({chart:t}){const s=Math.max(...t.before.concat(t.after).map(o=>o.value),1),i=(o,c,d)=>r.jsxs("div",{className:"chart-comparison-col",children:[r.jsx("h4",{className:`comparison-label ${d}`,children:o}),c.map(h=>r.jsxs("div",{className:"chart-bar-row",children:[r.jsx("span",{className:"chart-bar-label",children:h.label}),r.jsxs("div",{className:"chart-bar-track",children:[r.jsx("div",{className:"chart-bar-fill",style:{width:`${h.value/s*100}%`,background:h.color||"var(--accent)"}}),r.jsx("span",{className:"chart-bar-value",children:h.value})]})]},h.label))]});return r.jsxs("div",{className:"chart-comparison",children:[i("Before",t.before,"comparison-before"),r.jsx("div",{className:"chart-comparison-divider",children:r.jsx(ee,{name:"arrow",size:20})}),i("After",t.after,"comparison-after")]})}function Ma(t){return t.avatar_url}function fS(t){return`https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/svg/${Array.from(t).map(i=>i.codePointAt(0).toString(16)).join("-")}.svg`}function pS({emoji:t}){return t?t.kind==="custom"?r.jsx("img",{className:"presence-emoji",src:`https://cdn.discordapp.com/emojis/${t.value}.${t.animated?"gif":"png"}?size=18`,alt:t.name||"custom emoji"}):r.jsx("img",{className:"presence-emoji",src:fS(t.value),alt:t.name||t.value}):null}function gS(t){return{playing:"Playing",listening:"Listening to",watching:"Watching",streaming:"Streaming",competing:"Competing in"}[t]||(t?`${t.charAt(0).toUpperCase()}${t.slice(1)}`:"Activity")}function yS({activity:t}){const s=t.kind==="spotify",i=s?"Listening on Spotify":gS(t.type),o=s?t.details||"Spotify":t.name,c=s?t.state:t.details,d=r.jsxs("span",{className:`activity-card activity-${t.kind}`,children:[t.image_url&&r.jsx("img",{className:"activity-art",src:t.image_url,alt:""}),r.jsxs("span",{className:"activity-copy",children:[r.jsx("strong",{children:i}),r.jsx("span",{children:o}),c&&r.jsx("small",{children:c})]})]});return t.url?r.jsx("a",{className:"presence-activity",href:t.url,target:"_blank",rel:"noreferrer",children:d}):r.jsx("span",{className:"presence-activity",children:d})}function vS(t){return t.status_label||{online:"Online",idle:"Idle",dnd:"Do Not Disturb",offline:"Offline"}[t.status||"offline"]||"Offline"}function xS({member:t}){const s=t.custom_status,i=t.activities||[],o=!!(s!=null&&s.text||s!=null&&s.emoji);return!o&&!i.length?null:r.jsxs("span",{className:"presence-stack",children:[o&&r.jsxs("span",{className:"presence-line",children:[r.jsx(pS,{emoji:s==null?void 0:s.emoji}),(s==null?void 0:s.text)||"Custom status"]}),i.length>0&&r.jsx("span",{className:"presence-line activity-list",children:i.map((c,d)=>r.jsx(yS,{activity:c},`${c.kind}-${c.name}-${d}`))})]})}const Jg=`
.team-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));align-items:start;gap:14px;margin-top:58px}.team-card{display:flex;flex-direction:column;min-width:0;overflow:hidden;padding:0;color:var(--ink);text-align:left;background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow-soft)}.team-card:hover{border-color:#dfaa98;transform:translateY(-2px)}.team-card-art,.team-profile-banner{min-height:105px;background:linear-gradient(135deg,var(--callout),var(--surface-muted));background-size:cover;background-position:center}.team-card-body{display:flex;align-items:flex-start;flex:1;min-width:0;gap:14px;padding:18px}.team-card-body>div:last-child{min-width:0}.team-card h2,.team-card p{overflow-wrap:anywhere}.team-avatar,.team-profile-avatar{display:grid;place-items:center;flex:0 0 auto;overflow:hidden;color:#fffaf5;background:var(--accent);border-radius:50%;font-weight:800;object-fit:cover}.team-avatar{width:56px;height:56px;margin-top:-39px;border:3px solid var(--surface)}.team-role{color:var(--accent-dark);text-transform:uppercase;letter-spacing:.1em;font:700 9px "Space Mono",monospace}.team-card h2{margin:5px 0 6px;font-size:17px}.team-card p{margin:0 0 10px;color:var(--muted);font-size:11px;line-height:1.6}.team-status{color:var(--dim);font-size:10px}.presence-stack{display:block}.presence-stack>.presence-line+.presence-line{margin-top:12px}.presence-line{display:flex;align-items:center;flex-wrap:wrap;gap:7px;margin-top:7px;color:var(--muted);font-size:10px}.presence-activity{display:inline-flex;align-items:center;gap:4px;color:inherit}.presence-activity:hover{text-decoration:none}.activity-card{display:flex;align-items:center;min-width:0;gap:8px;padding:7px 9px;background:var(--surface-muted);border:1px solid var(--line);border-radius:8px;text-align:left}.activity-art{width:30px;height:30px;flex:0 0 auto;border-radius:5px;object-fit:cover}.activity-copy{display:flex;min-width:0;flex-direction:column;gap:1px}.activity-copy strong{color:var(--accent-dark);font-size:9px;text-transform:uppercase;letter-spacing:.06em}.activity-copy span,.activity-copy small{overflow:hidden;max-width:210px;text-overflow:ellipsis;white-space:nowrap}.activity-copy span{color:var(--ink);font-size:10px}.activity-copy small{color:var(--dim);font-size:9px}.presence-emoji{width:18px;height:18px;object-fit:contain;vertical-align:middle}.is-online{color:var(--sage)}.team-profile-page{max-width:760px}.team-back{width:auto;margin:0 0 18px;border:0;background:transparent}.team-profile-banner{min-height:220px;border:1px solid var(--line);border-radius:14px 14px 0 0}.team-profile-card{padding:0 34px 38px;text-align:center;background:var(--surface);border:1px solid var(--line);border-top:0;border-radius:0 0 14px 14px;box-shadow:var(--shadow-soft)}.team-profile-avatar{width:100px;height:100px;margin:-50px auto 6px;border:5px solid var(--surface);font-size:32px;transform:translateY(-20px)}.team-profile-card h1{margin:8px 0 5px;font-size:34px;letter-spacing:-.07em}.team-profile-handle{color:var(--dim);font-size:11px}.team-profile-bio{max-width:560px;margin:27px auto 0;color:var(--muted);line-height:1.8}.team-activity{display:block;width:min(100%,560px);margin:20px auto 0;padding:12px;color:var(--muted);background:var(--surface-muted);border:1px solid var(--line);border-radius:12px;font-size:10px;text-align:left}.team-activity .presence-line{margin-top:0}.team-activity .activity-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));align-items:stretch}.team-activity .activity-card{height:100%;width:100%}@media(max-width:800px){.team-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.team-grid{grid-template-columns:1fr;margin-top:38px}.team-profile-card{padding-left:18px;padding-right:18px}.team-profile-banner{min-height:150px}}`,Zg=5e3;function wS(){const[t,s]=P.useState([]);return P.useEffect(()=>{let i=!0;const o=()=>{cx().then(h=>{i&&s(h)}).catch(()=>{})},c=()=>{document.visibilityState==="visible"&&o()};o();const d=window.setInterval(()=>{document.visibilityState==="visible"&&o()},Zg);return document.addEventListener("visibilitychange",c),()=>{i=!1,window.clearInterval(d),document.removeEventListener("visibilitychange",c)}},[]),r.jsxs(r.Fragment,{children:[r.jsx("style",{children:Jg}),r.jsx(qe,{page:"team"}),r.jsxs("main",{className:"shell page-main",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"The people behind Niko"}),r.jsx("h1",{children:"Meet the team."}),r.jsx("p",{children:"A small group of builders, moderators, and creative minds keeping Niko friendly, useful, and moving forward."})]}),r.jsxs("div",{className:"team-grid",children:[t.map(i=>r.jsxs("button",{className:"team-card",onClick:()=>he(`/team/${i.id}`),children:[r.jsx("div",{className:"team-card-art",style:i.public_banner_url?{backgroundImage:`url(${i.public_banner_url})`}:void 0}),r.jsxs("div",{className:"team-card-body",children:[Ma(i)?r.jsx("img",{className:"team-avatar",src:Ma(i),alt:""}):r.jsx("span",{className:"team-avatar team-avatar-fallback",children:i.name.slice(0,1)}),r.jsxs("div",{children:[r.jsx("span",{className:"team-role",children:i.role_label}),r.jsx("h2",{children:i.name}),r.jsx("p",{children:i.bio||"Part of the Niko team."})]})]})]},i.id)),!t.length&&r.jsx("div",{className:"empty-state",children:"The team roster is being prepared."})]})]}),r.jsx(zt,{})]})}function bS({id:t}){const[s,i]=P.useState(null),[o,c]=P.useState("");return P.useEffect(()=>{let d=!0;const h=(v=!1)=>{ux(t).then(g=>{d&&(i(g),c(""))}).catch(g=>{d&&v&&c(g instanceof Error?g.message:"Team member not found.")})},f=()=>{document.visibilityState==="visible"&&h()};h(!0);const p=window.setInterval(()=>{document.visibilityState==="visible"&&h()},Zg);return document.addEventListener("visibilitychange",f),()=>{d=!1,window.clearInterval(p),document.removeEventListener("visibilitychange",f)}},[t]),r.jsxs(r.Fragment,{children:[r.jsx("style",{children:Jg}),r.jsx(qe,{page:"team"}),r.jsx("main",{className:"shell page-main team-profile-page",children:o?r.jsx("div",{className:"empty-state",children:o}):s?r.jsxs(r.Fragment,{children:[r.jsx("button",{className:"back-link team-back",onClick:()=>he("/team"),children:"← Back to team"}),r.jsx("div",{className:"team-profile-banner",style:s.public_banner_url?{backgroundImage:`url(${s.public_banner_url})`}:void 0}),r.jsxs("section",{className:"team-profile-card",children:[Ma(s)?r.jsx("img",{className:"team-profile-avatar",src:Ma(s),alt:""}):r.jsx("span",{className:"team-profile-avatar team-avatar-fallback",children:s.name.slice(0,1)}),r.jsx("div",{className:"team-role",children:s.role_label}),r.jsx("h1",{children:s.name}),r.jsxs("p",{className:"team-profile-handle",children:[s.username?`@${s.username}`:"Niko staff"," · ",r.jsx("span",{className:`status-${s.status||"offline"} ${s.status==="online"?"is-online":""}`,children:vS(s)})]}),r.jsx("p",{className:"team-profile-bio",children:s.bio||"This team member has not added an extended introduction yet."}),r.jsxs("div",{className:"team-activity",children:[r.jsx(xS,{member:s}),!s.custom_status&&!(s.activities||[]).length&&"No current activity"]})]})]}):r.jsx("div",{className:"section-loading",children:"Loading profile…"})}),r.jsx(zt,{})]})}function kS(){const[t,s]=P.useState(null),[i,o]=P.useState(null),[c,d]=P.useState(null),[h,f]=P.useState([]),[p,v]=P.useState({public_bio:"",public_banner_url:"",public_visible:!0}),[g,x]=P.useState({avatar_url:"",banner_url:""}),[w,k]=P.useState(""),[S,j]=P.useState(""),[N,B]=P.useState(!1),[M,L]=P.useState(!1);if(P.useEffect(()=>{Promise.all([oc(),lc(),fa(),cc()]).then(([se,ne,Se,Le])=>{s(se),o(ne),d(Se),f(Le),v({public_bio:ne.profile.bio||"",public_banner_url:ne.profile.public_banner_url||"",public_visible:ne.profile.visible!==!1})}).catch(se=>j(se instanceof Error?se.message:"Staff access unavailable."))},[]),!t||!i&&!S)return r.jsxs("div",{className:"dashboard-state",children:[r.jsx("div",{className:"loading-ring"}),r.jsx("p",{children:"Checking staff access…"})]});if(S||!i||!t.authenticated)return r.jsxs(r.Fragment,{children:[r.jsx(qe,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("div",{className:"eyebrow",children:"Staff workspace"}),r.jsx("h1",{children:"Private team area."}),r.jsx("p",{children:t!=null&&t.authenticated?S||"This area is only available to official Niko staff.":"Sign in with Discord to continue."}),!(t!=null&&t.authenticated)&&r.jsx("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard/staff",children:"Continue with Discord"}),r.jsx("button",{className:"back-link",onClick:()=>he("/dashboard"),children:"Return to dashboard"})]})})]});const I=t.user,D=`https://cdn.discordapp.com/embed/avatars/${Number(BigInt(I.id)%5n)}.png`,F=I.avatar?`https://cdn.discordapp.com/avatars/${I.id}/${I.avatar}.png?size=128`:D,V=["owner","head_admin","graphic_designer"].includes(i.role),O=(se,ne)=>v(Se=>({...Se,[se]:ne})),oe=async()=>{if(!N){B(!0),j(""),k("");try{await dx(p,t.csrf_token),k("Your public team listing was saved.")}catch(se){j(se instanceof Error?se.message:"Could not save listing.")}finally{B(!1)}}},le=async()=>{if(!M){L(!0),j(""),k("");try{await hx(g,t.csrf_token),k("Niko's global profile was updated.")}catch(se){j(se instanceof Error?se.message:"Could not update global profile.")}finally{L(!1)}}},xe=r.jsxs("div",{className:"staff-page",children:[r.jsxs("header",{className:"staff-heading",children:[r.jsxs("div",{children:[r.jsx("div",{className:"eyebrow",children:"Staff workspace"}),r.jsx("h1",{children:"Shape your presence."}),r.jsxs("p",{children:["Manage the public details granted to your ",r.jsx("strong",{children:i.role_label})," role. Your name and avatar always come directly from Discord."]})]}),r.jsxs("div",{className:"staff-role-card",children:[r.jsx("span",{className:"staff-role-mark",children:r.jsx("img",{src:F,alt:"Your Discord profile",onError:se=>{se.currentTarget.onerror=null,se.currentTarget.src=D}})}),r.jsxs("span",{children:[r.jsx("small",{children:"Signed in as"}),r.jsx("strong",{children:i.role_label})]})]})]}),r.jsxs("div",{className:"staff-layout",children:[r.jsxs("section",{className:"staff-panel staff-panel-main",children:[r.jsxs("div",{className:"staff-panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Public listing"}),r.jsx("h2",{children:"How the team sees you"}),r.jsx("p",{children:"Keep your introduction current while Discord remains the source of truth for your identity."})]}),r.jsx("span",{className:"staff-step",children:"01"})]}),r.jsxs("div",{className:"staff-fields",children:[r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Banner URL"}),r.jsx("input",{value:p.public_banner_url,onChange:se=>O("public_banner_url",se.target.value),placeholder:"https://…"}),r.jsx("small",{children:"Use a publicly reachable image. Leave blank for no banner."})]}),r.jsxs("label",{className:"form-field staff-bio-field",children:[r.jsx("span",{className:"form-label",children:"Extended introduction"}),r.jsx("textarea",{value:p.public_bio,onChange:se=>O("public_bio",se.target.value),maxLength:1200,placeholder:"Tell the community what you do…"}),r.jsxs("small",{children:[p.public_bio.length,"/1200 characters"]})]})]}),r.jsxs("label",{className:"setting-row staff-visibility",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Show me on the public Team page"}),r.jsx("small",{children:"Hide your listing without removing your staff access."})]}),r.jsx("input",{type:"checkbox",checked:p.public_visible,onChange:se=>O("public_visible",se.target.checked)}),r.jsx("i",{})]}),r.jsxs("div",{className:"staff-panel-footer",children:[r.jsx("span",{children:"Changes apply immediately to your public profile."}),r.jsx("button",{type:"button",className:"button button-primary",onClick:oe,disabled:N,children:N?"Saving…":"Save public listing"})]})]}),r.jsxs("aside",{className:"staff-sidebar-card",children:[r.jsx("span",{className:"panel-kicker",children:"Profile rules"}),r.jsx("h3",{children:"Stay consistent with Discord"}),r.jsx("p",{children:"Your global display name and profile picture sync automatically, so updates made in Discord are reflected here without another form."}),r.jsxs("div",{className:"staff-rule",children:[r.jsx("span",{children:"Identity"}),r.jsx("strong",{children:"Discord synced"})]}),r.jsxs("div",{className:"staff-rule",children:[r.jsx("span",{children:"Editable"}),r.jsx("strong",{children:"Bio · banner · visibility"})]})]})]}),V&&r.jsxs("section",{className:"staff-panel staff-global-panel",children:[r.jsxs("div",{className:"staff-panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Graphic direction"}),r.jsx("h2",{children:"Global Niko profile"}),r.jsx("p",{children:"Reserved for Graphic Designers, Head Admins, and owners. Paste publicly reachable image URLs."})]}),r.jsx("span",{className:"staff-step",children:"02"})]}),r.jsxs("div",{className:"staff-fields staff-fields-two",children:[r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Bot avatar URL"}),r.jsx("input",{value:g.avatar_url,onChange:se=>x({...g,avatar_url:se.target.value}),placeholder:"https://…"})]}),r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Bot banner URL"}),r.jsx("input",{value:g.banner_url,onChange:se=>x({...g,banner_url:se.target.value}),placeholder:"https://…"})]})]}),r.jsxs("div",{className:"staff-panel-footer",children:[r.jsx("span",{children:"Updates the bot-wide Discord profile."}),r.jsx("button",{type:"button",className:"button button-primary",onClick:le,disabled:M,children:M?"Updating…":"Update global profile"})]})]}),w&&r.jsx("div",{className:"notice",children:w}),S&&r.jsx("div",{className:"notice warning",children:S})]});return r.jsx(lp,{user:t.user,guilds:h,selectedGuild:null,view:"overview",section:"overview",stats:c,staffRole:i.role,onHome:()=>he(Ps()),onServers:()=>he(uc()),onGuildChange:()=>{},onSectionChange:()=>{},onRefresh:()=>window.location.reload(),refreshing:!1,children:xe})}function jS(){const[t,s]=P.useState(Sm);if(P.useEffect(()=>{const i=()=>s(Sm());return window.addEventListener("popstate",i),()=>window.removeEventListener("popstate",i)},[]),t==="commands")return r.jsx(ew,{});if(t==="docs-detail"){const i=window.location.pathname.split("/"),o=i[i.length-1];return r.jsx(V1,{slug:o})}if(t==="docs")return r.jsx(F1,{});if(t==="staff")return r.jsx(kS,{});if(t==="dashboard")return r.jsx(M1,{});if(t==="team")return r.jsx(wS,{});if(t==="team-member")return r.jsx(bS,{id:window.location.pathname.split("/").filter(Boolean)[1]||""});if(t==="privacy")return r.jsx(ac,{type:"privacy"});if(t==="terms")return r.jsx(ac,{type:"terms"});if(t==="community")return r.jsx(ac,{type:"community"});if(t==="donate")return r.jsx(z1,{});if(t==="transcript"){const o=window.location.pathname.split("/").filter(Boolean)[1]||"";return r.jsx(tS,{transcriptId:o})}if(t==="changelog")return r.jsx(rS,{});if(t==="changelog-detail"){const i=window.location.pathname.split("/"),o=i[i.length-1];return r.jsx(iS,{slug:o})}return r.jsx(B1,{})}ax.createRoot(document.getElementById("root")).render(r.jsx(P.StrictMode,{children:r.jsx(jS,{})}));
