var bx=Object.defineProperty;var wx=(t,s,r)=>s in t?bx(t,s,{enumerable:!0,configurable:!0,writable:!0,value:r}):t[s]=r;var fm=(t,s,r)=>wx(t,typeof s!="symbol"?s+"":s,r);(function(){const s=document.createElement("link").relList;if(s&&s.supports&&s.supports("modulepreload"))return;for(const c of document.querySelectorAll('link[rel="modulepreload"]'))o(c);new MutationObserver(c=>{for(const u of c)if(u.type==="childList")for(const h of u.addedNodes)h.tagName==="LINK"&&h.rel==="modulepreload"&&o(h)}).observe(document,{childList:!0,subtree:!0});function r(c){const u={};return c.integrity&&(u.integrity=c.integrity),c.referrerPolicy&&(u.referrerPolicy=c.referrerPolicy),c.crossOrigin==="use-credentials"?u.credentials="include":c.crossOrigin==="anonymous"?u.credentials="omit":u.credentials="same-origin",u}function o(c){if(c.ep)return;c.ep=!0;const u=r(c);fetch(c.href,u)}})();var Fl={exports:{}},Pi={},Bl={exports:{}},xe={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var gm;function kx(){if(gm)return xe;gm=1;var t=Symbol.for("react.element"),s=Symbol.for("react.portal"),r=Symbol.for("react.fragment"),o=Symbol.for("react.strict_mode"),c=Symbol.for("react.profiler"),u=Symbol.for("react.provider"),h=Symbol.for("react.context"),p=Symbol.for("react.forward_ref"),f=Symbol.for("react.suspense"),v=Symbol.for("react.memo"),g=Symbol.for("react.lazy"),x=Symbol.iterator;function b(E){return E===null||typeof E!="object"?null:(E=x&&E[x]||E["@@iterator"],typeof E=="function"?E:null)}var j={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},N=Object.assign,w={};function S(E,$,ye){this.props=E,this.context=$,this.refs=w,this.updater=ye||j}S.prototype.isReactComponent={},S.prototype.setState=function(E,$){if(typeof E!="object"&&typeof E!="function"&&E!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,E,$,"setState")},S.prototype.forceUpdate=function(E){this.updater.enqueueForceUpdate(this,E,"forceUpdate")};function B(){}B.prototype=S.prototype;function P(E,$,ye){this.props=E,this.context=$,this.refs=w,this.updater=ye||j}var D=P.prototype=new B;D.constructor=P,N(D,S.prototype),D.isPureReactComponent=!0;var V=Array.isArray,_=Object.prototype.hasOwnProperty,L={current:null},I={key:!0,ref:!0,__self:!0,__source:!0};function U(E,$,ye){var ve,ke={},O=null,le=null;if($!=null)for(ve in $.ref!==void 0&&(le=$.ref),$.key!==void 0&&(O=""+$.key),$)_.call($,ve)&&!I.hasOwnProperty(ve)&&(ke[ve]=$[ve]);var Q=arguments.length-2;if(Q===1)ke.children=ye;else if(1<Q){for(var ne=Array(Q),fe=0;fe<Q;fe++)ne[fe]=arguments[fe+2];ke.children=ne}if(E&&E.defaultProps)for(ve in Q=E.defaultProps,Q)ke[ve]===void 0&&(ke[ve]=Q[ve]);return{$$typeof:t,type:E,key:O,ref:le,props:ke,_owner:L.current}}function ce(E,$){return{$$typeof:t,type:E.type,key:$,ref:E.ref,props:E.props,_owner:E._owner}}function q(E){return typeof E=="object"&&E!==null&&E.$$typeof===t}function ge(E){var $={"=":"=0",":":"=2"};return"$"+E.replace(/[=:]/g,function(ye){return $[ye]})}var he=/\/+/g;function Y(E,$){return typeof E=="object"&&E!==null&&E.key!=null?ge(""+E.key):$.toString(36)}function we(E,$,ye,ve,ke){var O=typeof E;(O==="undefined"||O==="boolean")&&(E=null);var le=!1;if(E===null)le=!0;else switch(O){case"string":case"number":le=!0;break;case"object":switch(E.$$typeof){case t:case s:le=!0}}if(le)return le=E,ke=ke(le),E=ve===""?"."+Y(le,0):ve,V(ke)?(ye="",E!=null&&(ye=E.replace(he,"$&/")+"/"),we(ke,$,ye,"",function(fe){return fe})):ke!=null&&(q(ke)&&(ke=ce(ke,ye+(!ke.key||le&&le.key===ke.key?"":(""+ke.key).replace(he,"$&/")+"/")+E)),$.push(ke)),1;if(le=0,ve=ve===""?".":ve+":",V(E))for(var Q=0;Q<E.length;Q++){O=E[Q];var ne=ve+Y(O,Q);le+=we(O,$,ye,ne,ke)}else if(ne=b(E),typeof ne=="function")for(E=ne.call(E),Q=0;!(O=E.next()).done;)O=O.value,ne=ve+Y(O,Q++),le+=we(O,$,ye,ne,ke);else if(O==="object")throw $=String(E),Error("Objects are not valid as a React child (found: "+($==="[object Object]"?"object with keys {"+Object.keys(E).join(", ")+"}":$)+"). If you meant to render a collection of children, use an array instead.");return le}function me(E,$,ye){if(E==null)return E;var ve=[],ke=0;return we(E,ve,"","",function(O){return $.call(ye,O,ke++)}),ve}function Ce(E){if(E._status===-1){var $=E._result;$=$(),$.then(function(ye){(E._status===0||E._status===-1)&&(E._status=1,E._result=ye)},function(ye){(E._status===0||E._status===-1)&&(E._status=2,E._result=ye)}),E._status===-1&&(E._status=0,E._result=$)}if(E._status===1)return E._result.default;throw E._result}var ee={current:null},z={transition:null},Z={ReactCurrentDispatcher:ee,ReactCurrentBatchConfig:z,ReactCurrentOwner:L};function X(){throw Error("act(...) is not supported in production builds of React.")}return xe.Children={map:me,forEach:function(E,$,ye){me(E,function(){$.apply(this,arguments)},ye)},count:function(E){var $=0;return me(E,function(){$++}),$},toArray:function(E){return me(E,function($){return $})||[]},only:function(E){if(!q(E))throw Error("React.Children.only expected to receive a single React element child.");return E}},xe.Component=S,xe.Fragment=r,xe.Profiler=c,xe.PureComponent=P,xe.StrictMode=o,xe.Suspense=f,xe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Z,xe.act=X,xe.cloneElement=function(E,$,ye){if(E==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+E+".");var ve=N({},E.props),ke=E.key,O=E.ref,le=E._owner;if($!=null){if($.ref!==void 0&&(O=$.ref,le=L.current),$.key!==void 0&&(ke=""+$.key),E.type&&E.type.defaultProps)var Q=E.type.defaultProps;for(ne in $)_.call($,ne)&&!I.hasOwnProperty(ne)&&(ve[ne]=$[ne]===void 0&&Q!==void 0?Q[ne]:$[ne])}var ne=arguments.length-2;if(ne===1)ve.children=ye;else if(1<ne){Q=Array(ne);for(var fe=0;fe<ne;fe++)Q[fe]=arguments[fe+2];ve.children=Q}return{$$typeof:t,type:E.type,key:ke,ref:O,props:ve,_owner:le}},xe.createContext=function(E){return E={$$typeof:h,_currentValue:E,_currentValue2:E,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},E.Provider={$$typeof:u,_context:E},E.Consumer=E},xe.createElement=U,xe.createFactory=function(E){var $=U.bind(null,E);return $.type=E,$},xe.createRef=function(){return{current:null}},xe.forwardRef=function(E){return{$$typeof:p,render:E}},xe.isValidElement=q,xe.lazy=function(E){return{$$typeof:g,_payload:{_status:-1,_result:E},_init:Ce}},xe.memo=function(E,$){return{$$typeof:v,type:E,compare:$===void 0?null:$}},xe.startTransition=function(E){var $=z.transition;z.transition={};try{E()}finally{z.transition=$}},xe.unstable_act=X,xe.useCallback=function(E,$){return ee.current.useCallback(E,$)},xe.useContext=function(E){return ee.current.useContext(E)},xe.useDebugValue=function(){},xe.useDeferredValue=function(E){return ee.current.useDeferredValue(E)},xe.useEffect=function(E,$){return ee.current.useEffect(E,$)},xe.useId=function(){return ee.current.useId()},xe.useImperativeHandle=function(E,$,ye){return ee.current.useImperativeHandle(E,$,ye)},xe.useInsertionEffect=function(E,$){return ee.current.useInsertionEffect(E,$)},xe.useLayoutEffect=function(E,$){return ee.current.useLayoutEffect(E,$)},xe.useMemo=function(E,$){return ee.current.useMemo(E,$)},xe.useReducer=function(E,$,ye){return ee.current.useReducer(E,$,ye)},xe.useRef=function(E){return ee.current.useRef(E)},xe.useState=function(E){return ee.current.useState(E)},xe.useSyncExternalStore=function(E,$,ye){return ee.current.useSyncExternalStore(E,$,ye)},xe.useTransition=function(){return ee.current.useTransition()},xe.version="18.3.1",xe}var ym;function Hc(){return ym||(ym=1,Bl.exports=kx()),Bl.exports}/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var vm;function jx(){if(vm)return Pi;vm=1;var t=Hc(),s=Symbol.for("react.element"),r=Symbol.for("react.fragment"),o=Object.prototype.hasOwnProperty,c=t.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,u={key:!0,ref:!0,__self:!0,__source:!0};function h(p,f,v){var g,x={},b=null,j=null;v!==void 0&&(b=""+v),f.key!==void 0&&(b=""+f.key),f.ref!==void 0&&(j=f.ref);for(g in f)o.call(f,g)&&!u.hasOwnProperty(g)&&(x[g]=f[g]);if(p&&p.defaultProps)for(g in f=p.defaultProps,f)x[g]===void 0&&(x[g]=f[g]);return{$$typeof:s,type:p,key:b,ref:j,props:x,_owner:c.current}}return Pi.Fragment=r,Pi.jsx=h,Pi.jsxs=h,Pi}var xm;function Sx(){return xm||(xm=1,Fl.exports=jx()),Fl.exports}var i=Sx(),T=Hc(),Zr={},Ol={exports:{}},yt={},zl={exports:{}},Ul={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var bm;function Nx(){return bm||(bm=1,(function(t){function s(z,Z){var X=z.length;z.push(Z);e:for(;0<X;){var E=X-1>>>1,$=z[E];if(0<c($,Z))z[E]=Z,z[X]=$,X=E;else break e}}function r(z){return z.length===0?null:z[0]}function o(z){if(z.length===0)return null;var Z=z[0],X=z.pop();if(X!==Z){z[0]=X;e:for(var E=0,$=z.length,ye=$>>>1;E<ye;){var ve=2*(E+1)-1,ke=z[ve],O=ve+1,le=z[O];if(0>c(ke,X))O<$&&0>c(le,ke)?(z[E]=le,z[O]=X,E=O):(z[E]=ke,z[ve]=X,E=ve);else if(O<$&&0>c(le,X))z[E]=le,z[O]=X,E=O;else break e}}return Z}function c(z,Z){var X=z.sortIndex-Z.sortIndex;return X!==0?X:z.id-Z.id}if(typeof performance=="object"&&typeof performance.now=="function"){var u=performance;t.unstable_now=function(){return u.now()}}else{var h=Date,p=h.now();t.unstable_now=function(){return h.now()-p}}var f=[],v=[],g=1,x=null,b=3,j=!1,N=!1,w=!1,S=typeof setTimeout=="function"?setTimeout:null,B=typeof clearTimeout=="function"?clearTimeout:null,P=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function D(z){for(var Z=r(v);Z!==null;){if(Z.callback===null)o(v);else if(Z.startTime<=z)o(v),Z.sortIndex=Z.expirationTime,s(f,Z);else break;Z=r(v)}}function V(z){if(w=!1,D(z),!N)if(r(f)!==null)N=!0,Ce(_);else{var Z=r(v);Z!==null&&ee(V,Z.startTime-z)}}function _(z,Z){N=!1,w&&(w=!1,B(U),U=-1),j=!0;var X=b;try{for(D(Z),x=r(f);x!==null&&(!(x.expirationTime>Z)||z&&!ge());){var E=x.callback;if(typeof E=="function"){x.callback=null,b=x.priorityLevel;var $=E(x.expirationTime<=Z);Z=t.unstable_now(),typeof $=="function"?x.callback=$:x===r(f)&&o(f),D(Z)}else o(f);x=r(f)}if(x!==null)var ye=!0;else{var ve=r(v);ve!==null&&ee(V,ve.startTime-Z),ye=!1}return ye}finally{x=null,b=X,j=!1}}var L=!1,I=null,U=-1,ce=5,q=-1;function ge(){return!(t.unstable_now()-q<ce)}function he(){if(I!==null){var z=t.unstable_now();q=z;var Z=!0;try{Z=I(!0,z)}finally{Z?Y():(L=!1,I=null)}}else L=!1}var Y;if(typeof P=="function")Y=function(){P(he)};else if(typeof MessageChannel<"u"){var we=new MessageChannel,me=we.port2;we.port1.onmessage=he,Y=function(){me.postMessage(null)}}else Y=function(){S(he,0)};function Ce(z){I=z,L||(L=!0,Y())}function ee(z,Z){U=S(function(){z(t.unstable_now())},Z)}t.unstable_IdlePriority=5,t.unstable_ImmediatePriority=1,t.unstable_LowPriority=4,t.unstable_NormalPriority=3,t.unstable_Profiling=null,t.unstable_UserBlockingPriority=2,t.unstable_cancelCallback=function(z){z.callback=null},t.unstable_continueExecution=function(){N||j||(N=!0,Ce(_))},t.unstable_forceFrameRate=function(z){0>z||125<z?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):ce=0<z?Math.floor(1e3/z):5},t.unstable_getCurrentPriorityLevel=function(){return b},t.unstable_getFirstCallbackNode=function(){return r(f)},t.unstable_next=function(z){switch(b){case 1:case 2:case 3:var Z=3;break;default:Z=b}var X=b;b=Z;try{return z()}finally{b=X}},t.unstable_pauseExecution=function(){},t.unstable_requestPaint=function(){},t.unstable_runWithPriority=function(z,Z){switch(z){case 1:case 2:case 3:case 4:case 5:break;default:z=3}var X=b;b=z;try{return Z()}finally{b=X}},t.unstable_scheduleCallback=function(z,Z,X){var E=t.unstable_now();switch(typeof X=="object"&&X!==null?(X=X.delay,X=typeof X=="number"&&0<X?E+X:E):X=E,z){case 1:var $=-1;break;case 2:$=250;break;case 5:$=1073741823;break;case 4:$=1e4;break;default:$=5e3}return $=X+$,z={id:g++,callback:Z,priorityLevel:z,startTime:X,expirationTime:$,sortIndex:-1},X>E?(z.sortIndex=X,s(v,z),r(f)===null&&z===r(v)&&(w?(B(U),U=-1):w=!0,ee(V,X-E))):(z.sortIndex=$,s(f,z),N||j||(N=!0,Ce(_))),z},t.unstable_shouldYield=ge,t.unstable_wrapCallback=function(z){var Z=b;return function(){var X=b;b=Z;try{return z.apply(this,arguments)}finally{b=X}}}})(Ul)),Ul}var wm;function Cx(){return wm||(wm=1,zl.exports=Nx()),zl.exports}/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var km;function Tx(){if(km)return yt;km=1;var t=Hc(),s=Cx();function r(e){for(var n="https://reactjs.org/docs/error-decoder.html?invariant="+e,a=1;a<arguments.length;a++)n+="&args[]="+encodeURIComponent(arguments[a]);return"Minified React error #"+e+"; visit "+n+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var o=new Set,c={};function u(e,n){h(e,n),h(e+"Capture",n)}function h(e,n){for(c[e]=n,e=0;e<n.length;e++)o.add(n[e])}var p=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),f=Object.prototype.hasOwnProperty,v=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,g={},x={};function b(e){return f.call(x,e)?!0:f.call(g,e)?!1:v.test(e)?x[e]=!0:(g[e]=!0,!1)}function j(e,n,a,l){if(a!==null&&a.type===0)return!1;switch(typeof n){case"function":case"symbol":return!0;case"boolean":return l?!1:a!==null?!a.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function N(e,n,a,l){if(n===null||typeof n>"u"||j(e,n,a,l))return!0;if(l)return!1;if(a!==null)switch(a.type){case 3:return!n;case 4:return n===!1;case 5:return isNaN(n);case 6:return isNaN(n)||1>n}return!1}function w(e,n,a,l,d,m,y){this.acceptsBooleans=n===2||n===3||n===4,this.attributeName=l,this.attributeNamespace=d,this.mustUseProperty=a,this.propertyName=e,this.type=n,this.sanitizeURL=m,this.removeEmptyString=y}var S={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){S[e]=new w(e,0,!1,e,null,!1,!1)}),[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var n=e[0];S[n]=new w(n,1,!1,e[1],null,!1,!1)}),["contentEditable","draggable","spellCheck","value"].forEach(function(e){S[e]=new w(e,2,!1,e.toLowerCase(),null,!1,!1)}),["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){S[e]=new w(e,2,!1,e,null,!1,!1)}),"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){S[e]=new w(e,3,!1,e.toLowerCase(),null,!1,!1)}),["checked","multiple","muted","selected"].forEach(function(e){S[e]=new w(e,3,!0,e,null,!1,!1)}),["capture","download"].forEach(function(e){S[e]=new w(e,4,!1,e,null,!1,!1)}),["cols","rows","size","span"].forEach(function(e){S[e]=new w(e,6,!1,e,null,!1,!1)}),["rowSpan","start"].forEach(function(e){S[e]=new w(e,5,!1,e.toLowerCase(),null,!1,!1)});var B=/[\-:]([a-z])/g;function P(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var n=e.replace(B,P);S[n]=new w(n,1,!1,e,null,!1,!1)}),"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var n=e.replace(B,P);S[n]=new w(n,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)}),["xml:base","xml:lang","xml:space"].forEach(function(e){var n=e.replace(B,P);S[n]=new w(n,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)}),["tabIndex","crossOrigin"].forEach(function(e){S[e]=new w(e,1,!1,e.toLowerCase(),null,!1,!1)}),S.xlinkHref=new w("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1),["src","href","action","formAction"].forEach(function(e){S[e]=new w(e,1,!1,e.toLowerCase(),null,!0,!0)});function D(e,n,a,l){var d=S.hasOwnProperty(n)?S[n]:null;(d!==null?d.type!==0:l||!(2<n.length)||n[0]!=="o"&&n[0]!=="O"||n[1]!=="n"&&n[1]!=="N")&&(N(n,a,d,l)&&(a=null),l||d===null?b(n)&&(a===null?e.removeAttribute(n):e.setAttribute(n,""+a)):d.mustUseProperty?e[d.propertyName]=a===null?d.type===3?!1:"":a:(n=d.attributeName,l=d.attributeNamespace,a===null?e.removeAttribute(n):(d=d.type,a=d===3||d===4&&a===!0?"":""+a,l?e.setAttributeNS(l,n,a):e.setAttribute(n,a))))}var V=t.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,_=Symbol.for("react.element"),L=Symbol.for("react.portal"),I=Symbol.for("react.fragment"),U=Symbol.for("react.strict_mode"),ce=Symbol.for("react.profiler"),q=Symbol.for("react.provider"),ge=Symbol.for("react.context"),he=Symbol.for("react.forward_ref"),Y=Symbol.for("react.suspense"),we=Symbol.for("react.suspense_list"),me=Symbol.for("react.memo"),Ce=Symbol.for("react.lazy"),ee=Symbol.for("react.offscreen"),z=Symbol.iterator;function Z(e){return e===null||typeof e!="object"?null:(e=z&&e[z]||e["@@iterator"],typeof e=="function"?e:null)}var X=Object.assign,E;function $(e){if(E===void 0)try{throw Error()}catch(a){var n=a.stack.trim().match(/\n( *(at )?)/);E=n&&n[1]||""}return`
`+E+e}var ye=!1;function ve(e,n){if(!e||ye)return"";ye=!0;var a=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(n)if(n=function(){throw Error()},Object.defineProperty(n.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(n,[])}catch(F){var l=F}Reflect.construct(e,[],n)}else{try{n.call()}catch(F){l=F}e.call(n.prototype)}else{try{throw Error()}catch(F){l=F}e()}}catch(F){if(F&&l&&typeof F.stack=="string"){for(var d=F.stack.split(`
`),m=l.stack.split(`
`),y=d.length-1,k=m.length-1;1<=y&&0<=k&&d[y]!==m[k];)k--;for(;1<=y&&0<=k;y--,k--)if(d[y]!==m[k]){if(y!==1||k!==1)do if(y--,k--,0>k||d[y]!==m[k]){var C=`
`+d[y].replace(" at new "," at ");return e.displayName&&C.includes("<anonymous>")&&(C=C.replace("<anonymous>",e.displayName)),C}while(1<=y&&0<=k);break}}}finally{ye=!1,Error.prepareStackTrace=a}return(e=e?e.displayName||e.name:"")?$(e):""}function ke(e){switch(e.tag){case 5:return $(e.type);case 16:return $("Lazy");case 13:return $("Suspense");case 19:return $("SuspenseList");case 0:case 2:case 15:return e=ve(e.type,!1),e;case 11:return e=ve(e.type.render,!1),e;case 1:return e=ve(e.type,!0),e;default:return""}}function O(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case I:return"Fragment";case L:return"Portal";case ce:return"Profiler";case U:return"StrictMode";case Y:return"Suspense";case we:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case ge:return(e.displayName||"Context")+".Consumer";case q:return(e._context.displayName||"Context")+".Provider";case he:var n=e.render;return e=e.displayName,e||(e=n.displayName||n.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case me:return n=e.displayName||null,n!==null?n:O(e.type)||"Memo";case Ce:n=e._payload,e=e._init;try{return O(e(n))}catch{}}return null}function le(e){var n=e.type;switch(e.tag){case 24:return"Cache";case 9:return(n.displayName||"Context")+".Consumer";case 10:return(n._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=n.render,e=e.displayName||e.name||"",n.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return n;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return O(n);case 8:return n===U?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof n=="function")return n.displayName||n.name||null;if(typeof n=="string")return n}return null}function Q(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function ne(e){var n=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(n==="checkbox"||n==="radio")}function fe(e){var n=ne(e)?"checked":"value",a=Object.getOwnPropertyDescriptor(e.constructor.prototype,n),l=""+e[n];if(!e.hasOwnProperty(n)&&typeof a<"u"&&typeof a.get=="function"&&typeof a.set=="function"){var d=a.get,m=a.set;return Object.defineProperty(e,n,{configurable:!0,get:function(){return d.call(this)},set:function(y){l=""+y,m.call(this,y)}}),Object.defineProperty(e,n,{enumerable:a.enumerable}),{getValue:function(){return l},setValue:function(y){l=""+y},stopTracking:function(){e._valueTracker=null,delete e[n]}}}}function Re(e){e._valueTracker||(e._valueTracker=fe(e))}function vt(e){if(!e)return!1;var n=e._valueTracker;if(!n)return!0;var a=n.getValue(),l="";return e&&(l=ne(e)?e.checked?"true":"false":e.value),e=l,e!==a?(n.setValue(e),!0):!1}function Ht(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function Vn(e,n){var a=n.checked;return X({},n,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:a??e._wrapperState.initialChecked})}function Wi(e,n){var a=n.defaultValue==null?"":n.defaultValue,l=n.checked!=null?n.checked:n.defaultChecked;a=Q(n.value!=null?n.value:a),e._wrapperState={initialChecked:l,initialValue:a,controlled:n.type==="checkbox"||n.type==="radio"?n.checked!=null:n.value!=null}}function ju(e,n){n=n.checked,n!=null&&D(e,"checked",n,!1)}function Ha(e,n){ju(e,n);var a=Q(n.value),l=n.type;if(a!=null)l==="number"?(a===0&&e.value===""||e.value!=a)&&(e.value=""+a):e.value!==""+a&&(e.value=""+a);else if(l==="submit"||l==="reset"){e.removeAttribute("value");return}n.hasOwnProperty("value")?Ga(e,n.type,a):n.hasOwnProperty("defaultValue")&&Ga(e,n.type,Q(n.defaultValue)),n.checked==null&&n.defaultChecked!=null&&(e.defaultChecked=!!n.defaultChecked)}function Su(e,n,a){if(n.hasOwnProperty("value")||n.hasOwnProperty("defaultValue")){var l=n.type;if(!(l!=="submit"&&l!=="reset"||n.value!==void 0&&n.value!==null))return;n=""+e._wrapperState.initialValue,a||n===e.value||(e.value=n),e.defaultValue=n}a=e.name,a!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,a!==""&&(e.name=a)}function Ga(e,n,a){(n!=="number"||Ht(e.ownerDocument)!==e)&&(a==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+a&&(e.defaultValue=""+a))}var Ws=Array.isArray;function cs(e,n,a,l){if(e=e.options,n){n={};for(var d=0;d<a.length;d++)n["$"+a[d]]=!0;for(a=0;a<e.length;a++)d=n.hasOwnProperty("$"+e[a].value),e[a].selected!==d&&(e[a].selected=d),d&&l&&(e[a].defaultSelected=!0)}else{for(a=""+Q(a),n=null,d=0;d<e.length;d++){if(e[d].value===a){e[d].selected=!0,l&&(e[d].defaultSelected=!0);return}n!==null||e[d].disabled||(n=e[d])}n!==null&&(n.selected=!0)}}function Ka(e,n){if(n.dangerouslySetInnerHTML!=null)throw Error(r(91));return X({},n,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function Nu(e,n){var a=n.value;if(a==null){if(a=n.children,n=n.defaultValue,a!=null){if(n!=null)throw Error(r(92));if(Ws(a)){if(1<a.length)throw Error(r(93));a=a[0]}n=a}n==null&&(n=""),a=n}e._wrapperState={initialValue:Q(a)}}function Cu(e,n){var a=Q(n.value),l=Q(n.defaultValue);a!=null&&(a=""+a,a!==e.value&&(e.value=a),n.defaultValue==null&&e.defaultValue!==a&&(e.defaultValue=a)),l!=null&&(e.defaultValue=""+l)}function Tu(e){var n=e.textContent;n===e._wrapperState.initialValue&&n!==""&&n!==null&&(e.value=n)}function Au(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function qa(e,n){return e==null||e==="http://www.w3.org/1999/xhtml"?Au(n):e==="http://www.w3.org/2000/svg"&&n==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var Hi,Pu=(function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(n,a,l,d){MSApp.execUnsafeLocalFunction(function(){return e(n,a,l,d)})}:e})(function(e,n){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=n;else{for(Hi=Hi||document.createElement("div"),Hi.innerHTML="<svg>"+n.valueOf().toString()+"</svg>",n=Hi.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;n.firstChild;)e.appendChild(n.firstChild)}});function Hs(e,n){if(n){var a=e.firstChild;if(a&&a===e.lastChild&&a.nodeType===3){a.nodeValue=n;return}}e.textContent=n}var Gs={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},Sy=["Webkit","ms","Moz","O"];Object.keys(Gs).forEach(function(e){Sy.forEach(function(n){n=n+e.charAt(0).toUpperCase()+e.substring(1),Gs[n]=Gs[e]})});function Eu(e,n,a){return n==null||typeof n=="boolean"||n===""?"":a||typeof n!="number"||n===0||Gs.hasOwnProperty(e)&&Gs[e]?(""+n).trim():n+"px"}function Mu(e,n){e=e.style;for(var a in n)if(n.hasOwnProperty(a)){var l=a.indexOf("--")===0,d=Eu(a,n[a],l);a==="float"&&(a="cssFloat"),l?e.setProperty(a,d):e[a]=d}}var Ny=X({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function Xa(e,n){if(n){if(Ny[e]&&(n.children!=null||n.dangerouslySetInnerHTML!=null))throw Error(r(137,e));if(n.dangerouslySetInnerHTML!=null){if(n.children!=null)throw Error(r(60));if(typeof n.dangerouslySetInnerHTML!="object"||!("__html"in n.dangerouslySetInnerHTML))throw Error(r(61))}if(n.style!=null&&typeof n.style!="object")throw Error(r(62))}}function Ya(e,n){if(e.indexOf("-")===-1)return typeof n.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var Qa=null;function Ja(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var Za=null,us=null,ds=null;function _u(e){if(e=pi(e)){if(typeof Za!="function")throw Error(r(280));var n=e.stateNode;n&&(n=pr(n),Za(e.stateNode,e.type,n))}}function Du(e){us?ds?ds.push(e):ds=[e]:us=e}function Ru(){if(us){var e=us,n=ds;if(ds=us=null,_u(e),n)for(e=0;e<n.length;e++)_u(n[e])}}function Lu(e,n){return e(n)}function Iu(){}var eo=!1;function Vu(e,n,a){if(eo)return e(n,a);eo=!0;try{return Lu(e,n,a)}finally{eo=!1,(us!==null||ds!==null)&&(Iu(),Ru())}}function Ks(e,n){var a=e.stateNode;if(a===null)return null;var l=pr(a);if(l===null)return null;a=l[n];e:switch(n){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(l=!l.disabled)||(e=e.type,l=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!l;break e;default:e=!1}if(e)return null;if(a&&typeof a!="function")throw Error(r(231,n,typeof a));return a}var to=!1;if(p)try{var qs={};Object.defineProperty(qs,"passive",{get:function(){to=!0}}),window.addEventListener("test",qs,qs),window.removeEventListener("test",qs,qs)}catch{to=!1}function Cy(e,n,a,l,d,m,y,k,C){var F=Array.prototype.slice.call(arguments,3);try{n.apply(a,F)}catch(H){this.onError(H)}}var Xs=!1,Gi=null,Ki=!1,no=null,Ty={onError:function(e){Xs=!0,Gi=e}};function Ay(e,n,a,l,d,m,y,k,C){Xs=!1,Gi=null,Cy.apply(Ty,arguments)}function Py(e,n,a,l,d,m,y,k,C){if(Ay.apply(this,arguments),Xs){if(Xs){var F=Gi;Xs=!1,Gi=null}else throw Error(r(198));Ki||(Ki=!0,no=F)}}function Fn(e){var n=e,a=e;if(e.alternate)for(;n.return;)n=n.return;else{e=n;do n=e,(n.flags&4098)!==0&&(a=n.return),e=n.return;while(e)}return n.tag===3?a:null}function Fu(e){if(e.tag===13){var n=e.memoizedState;if(n===null&&(e=e.alternate,e!==null&&(n=e.memoizedState)),n!==null)return n.dehydrated}return null}function Bu(e){if(Fn(e)!==e)throw Error(r(188))}function Ey(e){var n=e.alternate;if(!n){if(n=Fn(e),n===null)throw Error(r(188));return n!==e?null:e}for(var a=e,l=n;;){var d=a.return;if(d===null)break;var m=d.alternate;if(m===null){if(l=d.return,l!==null){a=l;continue}break}if(d.child===m.child){for(m=d.child;m;){if(m===a)return Bu(d),e;if(m===l)return Bu(d),n;m=m.sibling}throw Error(r(188))}if(a.return!==l.return)a=d,l=m;else{for(var y=!1,k=d.child;k;){if(k===a){y=!0,a=d,l=m;break}if(k===l){y=!0,l=d,a=m;break}k=k.sibling}if(!y){for(k=m.child;k;){if(k===a){y=!0,a=m,l=d;break}if(k===l){y=!0,l=m,a=d;break}k=k.sibling}if(!y)throw Error(r(189))}}if(a.alternate!==l)throw Error(r(190))}if(a.tag!==3)throw Error(r(188));return a.stateNode.current===a?e:n}function Ou(e){return e=Ey(e),e!==null?zu(e):null}function zu(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var n=zu(e);if(n!==null)return n;e=e.sibling}return null}var Uu=s.unstable_scheduleCallback,$u=s.unstable_cancelCallback,My=s.unstable_shouldYield,_y=s.unstable_requestPaint,Oe=s.unstable_now,Dy=s.unstable_getCurrentPriorityLevel,so=s.unstable_ImmediatePriority,Wu=s.unstable_UserBlockingPriority,qi=s.unstable_NormalPriority,Ry=s.unstable_LowPriority,Hu=s.unstable_IdlePriority,Xi=null,Gt=null;function Ly(e){if(Gt&&typeof Gt.onCommitFiberRoot=="function")try{Gt.onCommitFiberRoot(Xi,e,void 0,(e.current.flags&128)===128)}catch{}}var Rt=Math.clz32?Math.clz32:Fy,Iy=Math.log,Vy=Math.LN2;function Fy(e){return e>>>=0,e===0?32:31-(Iy(e)/Vy|0)|0}var Yi=64,Qi=4194304;function Ys(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function Ji(e,n){var a=e.pendingLanes;if(a===0)return 0;var l=0,d=e.suspendedLanes,m=e.pingedLanes,y=a&268435455;if(y!==0){var k=y&~d;k!==0?l=Ys(k):(m&=y,m!==0&&(l=Ys(m)))}else y=a&~d,y!==0?l=Ys(y):m!==0&&(l=Ys(m));if(l===0)return 0;if(n!==0&&n!==l&&(n&d)===0&&(d=l&-l,m=n&-n,d>=m||d===16&&(m&4194240)!==0))return n;if((l&4)!==0&&(l|=a&16),n=e.entangledLanes,n!==0)for(e=e.entanglements,n&=l;0<n;)a=31-Rt(n),d=1<<a,l|=e[a],n&=~d;return l}function By(e,n){switch(e){case 1:case 2:case 4:return n+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return n+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function Oy(e,n){for(var a=e.suspendedLanes,l=e.pingedLanes,d=e.expirationTimes,m=e.pendingLanes;0<m;){var y=31-Rt(m),k=1<<y,C=d[y];C===-1?((k&a)===0||(k&l)!==0)&&(d[y]=By(k,n)):C<=n&&(e.expiredLanes|=k),m&=~k}}function io(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function Gu(){var e=Yi;return Yi<<=1,(Yi&4194240)===0&&(Yi=64),e}function ro(e){for(var n=[],a=0;31>a;a++)n.push(e);return n}function Qs(e,n,a){e.pendingLanes|=n,n!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,n=31-Rt(n),e[n]=a}function zy(e,n){var a=e.pendingLanes&~n;e.pendingLanes=n,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=n,e.mutableReadLanes&=n,e.entangledLanes&=n,n=e.entanglements;var l=e.eventTimes;for(e=e.expirationTimes;0<a;){var d=31-Rt(a),m=1<<d;n[d]=0,l[d]=-1,e[d]=-1,a&=~m}}function ao(e,n){var a=e.entangledLanes|=n;for(e=e.entanglements;a;){var l=31-Rt(a),d=1<<l;d&n|e[l]&n&&(e[l]|=n),a&=~d}}var Te=0;function Ku(e){return e&=-e,1<e?4<e?(e&268435455)!==0?16:536870912:4:1}var qu,oo,Xu,Yu,Qu,lo=!1,Zi=[],mn=null,pn=null,fn=null,Js=new Map,Zs=new Map,gn=[],Uy="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function Ju(e,n){switch(e){case"focusin":case"focusout":mn=null;break;case"dragenter":case"dragleave":pn=null;break;case"mouseover":case"mouseout":fn=null;break;case"pointerover":case"pointerout":Js.delete(n.pointerId);break;case"gotpointercapture":case"lostpointercapture":Zs.delete(n.pointerId)}}function ei(e,n,a,l,d,m){return e===null||e.nativeEvent!==m?(e={blockedOn:n,domEventName:a,eventSystemFlags:l,nativeEvent:m,targetContainers:[d]},n!==null&&(n=pi(n),n!==null&&oo(n)),e):(e.eventSystemFlags|=l,n=e.targetContainers,d!==null&&n.indexOf(d)===-1&&n.push(d),e)}function $y(e,n,a,l,d){switch(n){case"focusin":return mn=ei(mn,e,n,a,l,d),!0;case"dragenter":return pn=ei(pn,e,n,a,l,d),!0;case"mouseover":return fn=ei(fn,e,n,a,l,d),!0;case"pointerover":var m=d.pointerId;return Js.set(m,ei(Js.get(m)||null,e,n,a,l,d)),!0;case"gotpointercapture":return m=d.pointerId,Zs.set(m,ei(Zs.get(m)||null,e,n,a,l,d)),!0}return!1}function Zu(e){var n=Bn(e.target);if(n!==null){var a=Fn(n);if(a!==null){if(n=a.tag,n===13){if(n=Fu(a),n!==null){e.blockedOn=n,Qu(e.priority,function(){Xu(a)});return}}else if(n===3&&a.stateNode.current.memoizedState.isDehydrated){e.blockedOn=a.tag===3?a.stateNode.containerInfo:null;return}}}e.blockedOn=null}function er(e){if(e.blockedOn!==null)return!1;for(var n=e.targetContainers;0<n.length;){var a=uo(e.domEventName,e.eventSystemFlags,n[0],e.nativeEvent);if(a===null){a=e.nativeEvent;var l=new a.constructor(a.type,a);Qa=l,a.target.dispatchEvent(l),Qa=null}else return n=pi(a),n!==null&&oo(n),e.blockedOn=a,!1;n.shift()}return!0}function ed(e,n,a){er(e)&&a.delete(n)}function Wy(){lo=!1,mn!==null&&er(mn)&&(mn=null),pn!==null&&er(pn)&&(pn=null),fn!==null&&er(fn)&&(fn=null),Js.forEach(ed),Zs.forEach(ed)}function ti(e,n){e.blockedOn===n&&(e.blockedOn=null,lo||(lo=!0,s.unstable_scheduleCallback(s.unstable_NormalPriority,Wy)))}function ni(e){function n(d){return ti(d,e)}if(0<Zi.length){ti(Zi[0],e);for(var a=1;a<Zi.length;a++){var l=Zi[a];l.blockedOn===e&&(l.blockedOn=null)}}for(mn!==null&&ti(mn,e),pn!==null&&ti(pn,e),fn!==null&&ti(fn,e),Js.forEach(n),Zs.forEach(n),a=0;a<gn.length;a++)l=gn[a],l.blockedOn===e&&(l.blockedOn=null);for(;0<gn.length&&(a=gn[0],a.blockedOn===null);)Zu(a),a.blockedOn===null&&gn.shift()}var hs=V.ReactCurrentBatchConfig,tr=!0;function Hy(e,n,a,l){var d=Te,m=hs.transition;hs.transition=null;try{Te=1,co(e,n,a,l)}finally{Te=d,hs.transition=m}}function Gy(e,n,a,l){var d=Te,m=hs.transition;hs.transition=null;try{Te=4,co(e,n,a,l)}finally{Te=d,hs.transition=m}}function co(e,n,a,l){if(tr){var d=uo(e,n,a,l);if(d===null)Ao(e,n,l,nr,a),Ju(e,l);else if($y(d,e,n,a,l))l.stopPropagation();else if(Ju(e,l),n&4&&-1<Uy.indexOf(e)){for(;d!==null;){var m=pi(d);if(m!==null&&qu(m),m=uo(e,n,a,l),m===null&&Ao(e,n,l,nr,a),m===d)break;d=m}d!==null&&l.stopPropagation()}else Ao(e,n,l,null,a)}}var nr=null;function uo(e,n,a,l){if(nr=null,e=Ja(l),e=Bn(e),e!==null)if(n=Fn(e),n===null)e=null;else if(a=n.tag,a===13){if(e=Fu(n),e!==null)return e;e=null}else if(a===3){if(n.stateNode.current.memoizedState.isDehydrated)return n.tag===3?n.stateNode.containerInfo:null;e=null}else n!==e&&(e=null);return nr=e,null}function td(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(Dy()){case so:return 1;case Wu:return 4;case qi:case Ry:return 16;case Hu:return 536870912;default:return 16}default:return 16}}var yn=null,ho=null,sr=null;function nd(){if(sr)return sr;var e,n=ho,a=n.length,l,d="value"in yn?yn.value:yn.textContent,m=d.length;for(e=0;e<a&&n[e]===d[e];e++);var y=a-e;for(l=1;l<=y&&n[a-l]===d[m-l];l++);return sr=d.slice(e,1<l?1-l:void 0)}function ir(e){var n=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&n===13&&(e=13)):e=n,e===10&&(e=13),32<=e||e===13?e:0}function rr(){return!0}function sd(){return!1}function xt(e){function n(a,l,d,m,y){this._reactName=a,this._targetInst=d,this.type=l,this.nativeEvent=m,this.target=y,this.currentTarget=null;for(var k in e)e.hasOwnProperty(k)&&(a=e[k],this[k]=a?a(m):m[k]);return this.isDefaultPrevented=(m.defaultPrevented!=null?m.defaultPrevented:m.returnValue===!1)?rr:sd,this.isPropagationStopped=sd,this}return X(n.prototype,{preventDefault:function(){this.defaultPrevented=!0;var a=this.nativeEvent;a&&(a.preventDefault?a.preventDefault():typeof a.returnValue!="unknown"&&(a.returnValue=!1),this.isDefaultPrevented=rr)},stopPropagation:function(){var a=this.nativeEvent;a&&(a.stopPropagation?a.stopPropagation():typeof a.cancelBubble!="unknown"&&(a.cancelBubble=!0),this.isPropagationStopped=rr)},persist:function(){},isPersistent:rr}),n}var ms={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},mo=xt(ms),si=X({},ms,{view:0,detail:0}),Ky=xt(si),po,fo,ii,ar=X({},si,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:yo,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==ii&&(ii&&e.type==="mousemove"?(po=e.screenX-ii.screenX,fo=e.screenY-ii.screenY):fo=po=0,ii=e),po)},movementY:function(e){return"movementY"in e?e.movementY:fo}}),id=xt(ar),qy=X({},ar,{dataTransfer:0}),Xy=xt(qy),Yy=X({},si,{relatedTarget:0}),go=xt(Yy),Qy=X({},ms,{animationName:0,elapsedTime:0,pseudoElement:0}),Jy=xt(Qy),Zy=X({},ms,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),ev=xt(Zy),tv=X({},ms,{data:0}),rd=xt(tv),nv={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},sv={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},iv={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function rv(e){var n=this.nativeEvent;return n.getModifierState?n.getModifierState(e):(e=iv[e])?!!n[e]:!1}function yo(){return rv}var av=X({},si,{key:function(e){if(e.key){var n=nv[e.key]||e.key;if(n!=="Unidentified")return n}return e.type==="keypress"?(e=ir(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?sv[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:yo,charCode:function(e){return e.type==="keypress"?ir(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?ir(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),ov=xt(av),lv=X({},ar,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),ad=xt(lv),cv=X({},si,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:yo}),uv=xt(cv),dv=X({},ms,{propertyName:0,elapsedTime:0,pseudoElement:0}),hv=xt(dv),mv=X({},ar,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),pv=xt(mv),fv=[9,13,27,32],vo=p&&"CompositionEvent"in window,ri=null;p&&"documentMode"in document&&(ri=document.documentMode);var gv=p&&"TextEvent"in window&&!ri,od=p&&(!vo||ri&&8<ri&&11>=ri),ld=" ",cd=!1;function ud(e,n){switch(e){case"keyup":return fv.indexOf(n.keyCode)!==-1;case"keydown":return n.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function dd(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var ps=!1;function yv(e,n){switch(e){case"compositionend":return dd(n);case"keypress":return n.which!==32?null:(cd=!0,ld);case"textInput":return e=n.data,e===ld&&cd?null:e;default:return null}}function vv(e,n){if(ps)return e==="compositionend"||!vo&&ud(e,n)?(e=nd(),sr=ho=yn=null,ps=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(n.ctrlKey||n.altKey||n.metaKey)||n.ctrlKey&&n.altKey){if(n.char&&1<n.char.length)return n.char;if(n.which)return String.fromCharCode(n.which)}return null;case"compositionend":return od&&n.locale!=="ko"?null:n.data;default:return null}}var xv={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function hd(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n==="input"?!!xv[e.type]:n==="textarea"}function md(e,n,a,l){Du(l),n=dr(n,"onChange"),0<n.length&&(a=new mo("onChange","change",null,a,l),e.push({event:a,listeners:n}))}var ai=null,oi=null;function bv(e){Md(e,0)}function or(e){var n=xs(e);if(vt(n))return e}function wv(e,n){if(e==="change")return n}var pd=!1;if(p){var xo;if(p){var bo="oninput"in document;if(!bo){var fd=document.createElement("div");fd.setAttribute("oninput","return;"),bo=typeof fd.oninput=="function"}xo=bo}else xo=!1;pd=xo&&(!document.documentMode||9<document.documentMode)}function gd(){ai&&(ai.detachEvent("onpropertychange",yd),oi=ai=null)}function yd(e){if(e.propertyName==="value"&&or(oi)){var n=[];md(n,oi,e,Ja(e)),Vu(bv,n)}}function kv(e,n,a){e==="focusin"?(gd(),ai=n,oi=a,ai.attachEvent("onpropertychange",yd)):e==="focusout"&&gd()}function jv(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return or(oi)}function Sv(e,n){if(e==="click")return or(n)}function Nv(e,n){if(e==="input"||e==="change")return or(n)}function Cv(e,n){return e===n&&(e!==0||1/e===1/n)||e!==e&&n!==n}var Lt=typeof Object.is=="function"?Object.is:Cv;function li(e,n){if(Lt(e,n))return!0;if(typeof e!="object"||e===null||typeof n!="object"||n===null)return!1;var a=Object.keys(e),l=Object.keys(n);if(a.length!==l.length)return!1;for(l=0;l<a.length;l++){var d=a[l];if(!f.call(n,d)||!Lt(e[d],n[d]))return!1}return!0}function vd(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function xd(e,n){var a=vd(e);e=0;for(var l;a;){if(a.nodeType===3){if(l=e+a.textContent.length,e<=n&&l>=n)return{node:a,offset:n-e};e=l}e:{for(;a;){if(a.nextSibling){a=a.nextSibling;break e}a=a.parentNode}a=void 0}a=vd(a)}}function bd(e,n){return e&&n?e===n?!0:e&&e.nodeType===3?!1:n&&n.nodeType===3?bd(e,n.parentNode):"contains"in e?e.contains(n):e.compareDocumentPosition?!!(e.compareDocumentPosition(n)&16):!1:!1}function wd(){for(var e=window,n=Ht();n instanceof e.HTMLIFrameElement;){try{var a=typeof n.contentWindow.location.href=="string"}catch{a=!1}if(a)e=n.contentWindow;else break;n=Ht(e.document)}return n}function wo(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n&&(n==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||n==="textarea"||e.contentEditable==="true")}function Tv(e){var n=wd(),a=e.focusedElem,l=e.selectionRange;if(n!==a&&a&&a.ownerDocument&&bd(a.ownerDocument.documentElement,a)){if(l!==null&&wo(a)){if(n=l.start,e=l.end,e===void 0&&(e=n),"selectionStart"in a)a.selectionStart=n,a.selectionEnd=Math.min(e,a.value.length);else if(e=(n=a.ownerDocument||document)&&n.defaultView||window,e.getSelection){e=e.getSelection();var d=a.textContent.length,m=Math.min(l.start,d);l=l.end===void 0?m:Math.min(l.end,d),!e.extend&&m>l&&(d=l,l=m,m=d),d=xd(a,m);var y=xd(a,l);d&&y&&(e.rangeCount!==1||e.anchorNode!==d.node||e.anchorOffset!==d.offset||e.focusNode!==y.node||e.focusOffset!==y.offset)&&(n=n.createRange(),n.setStart(d.node,d.offset),e.removeAllRanges(),m>l?(e.addRange(n),e.extend(y.node,y.offset)):(n.setEnd(y.node,y.offset),e.addRange(n)))}}for(n=[],e=a;e=e.parentNode;)e.nodeType===1&&n.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof a.focus=="function"&&a.focus(),a=0;a<n.length;a++)e=n[a],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var Av=p&&"documentMode"in document&&11>=document.documentMode,fs=null,ko=null,ci=null,jo=!1;function kd(e,n,a){var l=a.window===a?a.document:a.nodeType===9?a:a.ownerDocument;jo||fs==null||fs!==Ht(l)||(l=fs,"selectionStart"in l&&wo(l)?l={start:l.selectionStart,end:l.selectionEnd}:(l=(l.ownerDocument&&l.ownerDocument.defaultView||window).getSelection(),l={anchorNode:l.anchorNode,anchorOffset:l.anchorOffset,focusNode:l.focusNode,focusOffset:l.focusOffset}),ci&&li(ci,l)||(ci=l,l=dr(ko,"onSelect"),0<l.length&&(n=new mo("onSelect","select",null,n,a),e.push({event:n,listeners:l}),n.target=fs)))}function lr(e,n){var a={};return a[e.toLowerCase()]=n.toLowerCase(),a["Webkit"+e]="webkit"+n,a["Moz"+e]="moz"+n,a}var gs={animationend:lr("Animation","AnimationEnd"),animationiteration:lr("Animation","AnimationIteration"),animationstart:lr("Animation","AnimationStart"),transitionend:lr("Transition","TransitionEnd")},So={},jd={};p&&(jd=document.createElement("div").style,"AnimationEvent"in window||(delete gs.animationend.animation,delete gs.animationiteration.animation,delete gs.animationstart.animation),"TransitionEvent"in window||delete gs.transitionend.transition);function cr(e){if(So[e])return So[e];if(!gs[e])return e;var n=gs[e],a;for(a in n)if(n.hasOwnProperty(a)&&a in jd)return So[e]=n[a];return e}var Sd=cr("animationend"),Nd=cr("animationiteration"),Cd=cr("animationstart"),Td=cr("transitionend"),Ad=new Map,Pd="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function vn(e,n){Ad.set(e,n),u(n,[e])}for(var No=0;No<Pd.length;No++){var Co=Pd[No],Pv=Co.toLowerCase(),Ev=Co[0].toUpperCase()+Co.slice(1);vn(Pv,"on"+Ev)}vn(Sd,"onAnimationEnd"),vn(Nd,"onAnimationIteration"),vn(Cd,"onAnimationStart"),vn("dblclick","onDoubleClick"),vn("focusin","onFocus"),vn("focusout","onBlur"),vn(Td,"onTransitionEnd"),h("onMouseEnter",["mouseout","mouseover"]),h("onMouseLeave",["mouseout","mouseover"]),h("onPointerEnter",["pointerout","pointerover"]),h("onPointerLeave",["pointerout","pointerover"]),u("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),u("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),u("onBeforeInput",["compositionend","keypress","textInput","paste"]),u("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),u("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),u("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var ui="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),Mv=new Set("cancel close invalid load scroll toggle".split(" ").concat(ui));function Ed(e,n,a){var l=e.type||"unknown-event";e.currentTarget=a,Py(l,n,void 0,e),e.currentTarget=null}function Md(e,n){n=(n&4)!==0;for(var a=0;a<e.length;a++){var l=e[a],d=l.event;l=l.listeners;e:{var m=void 0;if(n)for(var y=l.length-1;0<=y;y--){var k=l[y],C=k.instance,F=k.currentTarget;if(k=k.listener,C!==m&&d.isPropagationStopped())break e;Ed(d,k,F),m=C}else for(y=0;y<l.length;y++){if(k=l[y],C=k.instance,F=k.currentTarget,k=k.listener,C!==m&&d.isPropagationStopped())break e;Ed(d,k,F),m=C}}}if(Ki)throw e=no,Ki=!1,no=null,e}function _e(e,n){var a=n[Ro];a===void 0&&(a=n[Ro]=new Set);var l=e+"__bubble";a.has(l)||(_d(n,e,2,!1),a.add(l))}function To(e,n,a){var l=0;n&&(l|=4),_d(a,e,l,n)}var ur="_reactListening"+Math.random().toString(36).slice(2);function di(e){if(!e[ur]){e[ur]=!0,o.forEach(function(a){a!=="selectionchange"&&(Mv.has(a)||To(a,!1,e),To(a,!0,e))});var n=e.nodeType===9?e:e.ownerDocument;n===null||n[ur]||(n[ur]=!0,To("selectionchange",!1,n))}}function _d(e,n,a,l){switch(td(n)){case 1:var d=Hy;break;case 4:d=Gy;break;default:d=co}a=d.bind(null,n,a,e),d=void 0,!to||n!=="touchstart"&&n!=="touchmove"&&n!=="wheel"||(d=!0),l?d!==void 0?e.addEventListener(n,a,{capture:!0,passive:d}):e.addEventListener(n,a,!0):d!==void 0?e.addEventListener(n,a,{passive:d}):e.addEventListener(n,a,!1)}function Ao(e,n,a,l,d){var m=l;if((n&1)===0&&(n&2)===0&&l!==null)e:for(;;){if(l===null)return;var y=l.tag;if(y===3||y===4){var k=l.stateNode.containerInfo;if(k===d||k.nodeType===8&&k.parentNode===d)break;if(y===4)for(y=l.return;y!==null;){var C=y.tag;if((C===3||C===4)&&(C=y.stateNode.containerInfo,C===d||C.nodeType===8&&C.parentNode===d))return;y=y.return}for(;k!==null;){if(y=Bn(k),y===null)return;if(C=y.tag,C===5||C===6){l=m=y;continue e}k=k.parentNode}}l=l.return}Vu(function(){var F=m,H=Ja(a),G=[];e:{var W=Ad.get(e);if(W!==void 0){var te=mo,ie=e;switch(e){case"keypress":if(ir(a)===0)break e;case"keydown":case"keyup":te=ov;break;case"focusin":ie="focus",te=go;break;case"focusout":ie="blur",te=go;break;case"beforeblur":case"afterblur":te=go;break;case"click":if(a.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":te=id;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":te=Xy;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":te=uv;break;case Sd:case Nd:case Cd:te=Jy;break;case Td:te=hv;break;case"scroll":te=Ky;break;case"wheel":te=pv;break;case"copy":case"cut":case"paste":te=ev;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":te=ad}var ae=(n&4)!==0,ze=!ae&&e==="scroll",M=ae?W!==null?W+"Capture":null:W;ae=[];for(var A=F,R;A!==null;){R=A;var K=R.stateNode;if(R.tag===5&&K!==null&&(R=K,M!==null&&(K=Ks(A,M),K!=null&&ae.push(hi(A,K,R)))),ze)break;A=A.return}0<ae.length&&(W=new te(W,ie,null,a,H),G.push({event:W,listeners:ae}))}}if((n&7)===0){e:{if(W=e==="mouseover"||e==="pointerover",te=e==="mouseout"||e==="pointerout",W&&a!==Qa&&(ie=a.relatedTarget||a.fromElement)&&(Bn(ie)||ie[tn]))break e;if((te||W)&&(W=H.window===H?H:(W=H.ownerDocument)?W.defaultView||W.parentWindow:window,te?(ie=a.relatedTarget||a.toElement,te=F,ie=ie?Bn(ie):null,ie!==null&&(ze=Fn(ie),ie!==ze||ie.tag!==5&&ie.tag!==6)&&(ie=null)):(te=null,ie=F),te!==ie)){if(ae=id,K="onMouseLeave",M="onMouseEnter",A="mouse",(e==="pointerout"||e==="pointerover")&&(ae=ad,K="onPointerLeave",M="onPointerEnter",A="pointer"),ze=te==null?W:xs(te),R=ie==null?W:xs(ie),W=new ae(K,A+"leave",te,a,H),W.target=ze,W.relatedTarget=R,K=null,Bn(H)===F&&(ae=new ae(M,A+"enter",ie,a,H),ae.target=R,ae.relatedTarget=ze,K=ae),ze=K,te&&ie)t:{for(ae=te,M=ie,A=0,R=ae;R;R=ys(R))A++;for(R=0,K=M;K;K=ys(K))R++;for(;0<A-R;)ae=ys(ae),A--;for(;0<R-A;)M=ys(M),R--;for(;A--;){if(ae===M||M!==null&&ae===M.alternate)break t;ae=ys(ae),M=ys(M)}ae=null}else ae=null;te!==null&&Dd(G,W,te,ae,!1),ie!==null&&ze!==null&&Dd(G,ze,ie,ae,!0)}}e:{if(W=F?xs(F):window,te=W.nodeName&&W.nodeName.toLowerCase(),te==="select"||te==="input"&&W.type==="file")var oe=wv;else if(hd(W))if(pd)oe=Nv;else{oe=jv;var ue=kv}else(te=W.nodeName)&&te.toLowerCase()==="input"&&(W.type==="checkbox"||W.type==="radio")&&(oe=Sv);if(oe&&(oe=oe(e,F))){md(G,oe,a,H);break e}ue&&ue(e,W,F),e==="focusout"&&(ue=W._wrapperState)&&ue.controlled&&W.type==="number"&&Ga(W,"number",W.value)}switch(ue=F?xs(F):window,e){case"focusin":(hd(ue)||ue.contentEditable==="true")&&(fs=ue,ko=F,ci=null);break;case"focusout":ci=ko=fs=null;break;case"mousedown":jo=!0;break;case"contextmenu":case"mouseup":case"dragend":jo=!1,kd(G,a,H);break;case"selectionchange":if(Av)break;case"keydown":case"keyup":kd(G,a,H)}var de;if(vo)e:{switch(e){case"compositionstart":var pe="onCompositionStart";break e;case"compositionend":pe="onCompositionEnd";break e;case"compositionupdate":pe="onCompositionUpdate";break e}pe=void 0}else ps?ud(e,a)&&(pe="onCompositionEnd"):e==="keydown"&&a.keyCode===229&&(pe="onCompositionStart");pe&&(od&&a.locale!=="ko"&&(ps||pe!=="onCompositionStart"?pe==="onCompositionEnd"&&ps&&(de=nd()):(yn=H,ho="value"in yn?yn.value:yn.textContent,ps=!0)),ue=dr(F,pe),0<ue.length&&(pe=new rd(pe,e,null,a,H),G.push({event:pe,listeners:ue}),de?pe.data=de:(de=dd(a),de!==null&&(pe.data=de)))),(de=gv?yv(e,a):vv(e,a))&&(F=dr(F,"onBeforeInput"),0<F.length&&(H=new rd("onBeforeInput","beforeinput",null,a,H),G.push({event:H,listeners:F}),H.data=de))}Md(G,n)})}function hi(e,n,a){return{instance:e,listener:n,currentTarget:a}}function dr(e,n){for(var a=n+"Capture",l=[];e!==null;){var d=e,m=d.stateNode;d.tag===5&&m!==null&&(d=m,m=Ks(e,a),m!=null&&l.unshift(hi(e,m,d)),m=Ks(e,n),m!=null&&l.push(hi(e,m,d))),e=e.return}return l}function ys(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function Dd(e,n,a,l,d){for(var m=n._reactName,y=[];a!==null&&a!==l;){var k=a,C=k.alternate,F=k.stateNode;if(C!==null&&C===l)break;k.tag===5&&F!==null&&(k=F,d?(C=Ks(a,m),C!=null&&y.unshift(hi(a,C,k))):d||(C=Ks(a,m),C!=null&&y.push(hi(a,C,k)))),a=a.return}y.length!==0&&e.push({event:n,listeners:y})}var _v=/\r\n?/g,Dv=/\u0000|\uFFFD/g;function Rd(e){return(typeof e=="string"?e:""+e).replace(_v,`
`).replace(Dv,"")}function hr(e,n,a){if(n=Rd(n),Rd(e)!==n&&a)throw Error(r(425))}function mr(){}var Po=null,Eo=null;function Mo(e,n){return e==="textarea"||e==="noscript"||typeof n.children=="string"||typeof n.children=="number"||typeof n.dangerouslySetInnerHTML=="object"&&n.dangerouslySetInnerHTML!==null&&n.dangerouslySetInnerHTML.__html!=null}var _o=typeof setTimeout=="function"?setTimeout:void 0,Rv=typeof clearTimeout=="function"?clearTimeout:void 0,Ld=typeof Promise=="function"?Promise:void 0,Lv=typeof queueMicrotask=="function"?queueMicrotask:typeof Ld<"u"?function(e){return Ld.resolve(null).then(e).catch(Iv)}:_o;function Iv(e){setTimeout(function(){throw e})}function Do(e,n){var a=n,l=0;do{var d=a.nextSibling;if(e.removeChild(a),d&&d.nodeType===8)if(a=d.data,a==="/$"){if(l===0){e.removeChild(d),ni(n);return}l--}else a!=="$"&&a!=="$?"&&a!=="$!"||l++;a=d}while(a);ni(n)}function xn(e){for(;e!=null;e=e.nextSibling){var n=e.nodeType;if(n===1||n===3)break;if(n===8){if(n=e.data,n==="$"||n==="$!"||n==="$?")break;if(n==="/$")return null}}return e}function Id(e){e=e.previousSibling;for(var n=0;e;){if(e.nodeType===8){var a=e.data;if(a==="$"||a==="$!"||a==="$?"){if(n===0)return e;n--}else a==="/$"&&n++}e=e.previousSibling}return null}var vs=Math.random().toString(36).slice(2),Kt="__reactFiber$"+vs,mi="__reactProps$"+vs,tn="__reactContainer$"+vs,Ro="__reactEvents$"+vs,Vv="__reactListeners$"+vs,Fv="__reactHandles$"+vs;function Bn(e){var n=e[Kt];if(n)return n;for(var a=e.parentNode;a;){if(n=a[tn]||a[Kt]){if(a=n.alternate,n.child!==null||a!==null&&a.child!==null)for(e=Id(e);e!==null;){if(a=e[Kt])return a;e=Id(e)}return n}e=a,a=e.parentNode}return null}function pi(e){return e=e[Kt]||e[tn],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function xs(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(r(33))}function pr(e){return e[mi]||null}var Lo=[],bs=-1;function bn(e){return{current:e}}function De(e){0>bs||(e.current=Lo[bs],Lo[bs]=null,bs--)}function Me(e,n){bs++,Lo[bs]=e.current,e.current=n}var wn={},st=bn(wn),ht=bn(!1),On=wn;function ws(e,n){var a=e.type.contextTypes;if(!a)return wn;var l=e.stateNode;if(l&&l.__reactInternalMemoizedUnmaskedChildContext===n)return l.__reactInternalMemoizedMaskedChildContext;var d={},m;for(m in a)d[m]=n[m];return l&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=n,e.__reactInternalMemoizedMaskedChildContext=d),d}function mt(e){return e=e.childContextTypes,e!=null}function fr(){De(ht),De(st)}function Vd(e,n,a){if(st.current!==wn)throw Error(r(168));Me(st,n),Me(ht,a)}function Fd(e,n,a){var l=e.stateNode;if(n=n.childContextTypes,typeof l.getChildContext!="function")return a;l=l.getChildContext();for(var d in l)if(!(d in n))throw Error(r(108,le(e)||"Unknown",d));return X({},a,l)}function gr(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||wn,On=st.current,Me(st,e),Me(ht,ht.current),!0}function Bd(e,n,a){var l=e.stateNode;if(!l)throw Error(r(169));a?(e=Fd(e,n,On),l.__reactInternalMemoizedMergedChildContext=e,De(ht),De(st),Me(st,e)):De(ht),Me(ht,a)}var nn=null,yr=!1,Io=!1;function Od(e){nn===null?nn=[e]:nn.push(e)}function Bv(e){yr=!0,Od(e)}function kn(){if(!Io&&nn!==null){Io=!0;var e=0,n=Te;try{var a=nn;for(Te=1;e<a.length;e++){var l=a[e];do l=l(!0);while(l!==null)}nn=null,yr=!1}catch(d){throw nn!==null&&(nn=nn.slice(e+1)),Uu(so,kn),d}finally{Te=n,Io=!1}}return null}var ks=[],js=0,vr=null,xr=0,Ct=[],Tt=0,zn=null,sn=1,rn="";function Un(e,n){ks[js++]=xr,ks[js++]=vr,vr=e,xr=n}function zd(e,n,a){Ct[Tt++]=sn,Ct[Tt++]=rn,Ct[Tt++]=zn,zn=e;var l=sn;e=rn;var d=32-Rt(l)-1;l&=~(1<<d),a+=1;var m=32-Rt(n)+d;if(30<m){var y=d-d%5;m=(l&(1<<y)-1).toString(32),l>>=y,d-=y,sn=1<<32-Rt(n)+d|a<<d|l,rn=m+e}else sn=1<<m|a<<d|l,rn=e}function Vo(e){e.return!==null&&(Un(e,1),zd(e,1,0))}function Fo(e){for(;e===vr;)vr=ks[--js],ks[js]=null,xr=ks[--js],ks[js]=null;for(;e===zn;)zn=Ct[--Tt],Ct[Tt]=null,rn=Ct[--Tt],Ct[Tt]=null,sn=Ct[--Tt],Ct[Tt]=null}var bt=null,wt=null,Le=!1,It=null;function Ud(e,n){var a=Mt(5,null,null,0);a.elementType="DELETED",a.stateNode=n,a.return=e,n=e.deletions,n===null?(e.deletions=[a],e.flags|=16):n.push(a)}function $d(e,n){switch(e.tag){case 5:var a=e.type;return n=n.nodeType!==1||a.toLowerCase()!==n.nodeName.toLowerCase()?null:n,n!==null?(e.stateNode=n,bt=e,wt=xn(n.firstChild),!0):!1;case 6:return n=e.pendingProps===""||n.nodeType!==3?null:n,n!==null?(e.stateNode=n,bt=e,wt=null,!0):!1;case 13:return n=n.nodeType!==8?null:n,n!==null?(a=zn!==null?{id:sn,overflow:rn}:null,e.memoizedState={dehydrated:n,treeContext:a,retryLane:1073741824},a=Mt(18,null,null,0),a.stateNode=n,a.return=e,e.child=a,bt=e,wt=null,!0):!1;default:return!1}}function Bo(e){return(e.mode&1)!==0&&(e.flags&128)===0}function Oo(e){if(Le){var n=wt;if(n){var a=n;if(!$d(e,n)){if(Bo(e))throw Error(r(418));n=xn(a.nextSibling);var l=bt;n&&$d(e,n)?Ud(l,a):(e.flags=e.flags&-4097|2,Le=!1,bt=e)}}else{if(Bo(e))throw Error(r(418));e.flags=e.flags&-4097|2,Le=!1,bt=e}}}function Wd(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;bt=e}function br(e){if(e!==bt)return!1;if(!Le)return Wd(e),Le=!0,!1;var n;if((n=e.tag!==3)&&!(n=e.tag!==5)&&(n=e.type,n=n!=="head"&&n!=="body"&&!Mo(e.type,e.memoizedProps)),n&&(n=wt)){if(Bo(e))throw Hd(),Error(r(418));for(;n;)Ud(e,n),n=xn(n.nextSibling)}if(Wd(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(r(317));e:{for(e=e.nextSibling,n=0;e;){if(e.nodeType===8){var a=e.data;if(a==="/$"){if(n===0){wt=xn(e.nextSibling);break e}n--}else a!=="$"&&a!=="$!"&&a!=="$?"||n++}e=e.nextSibling}wt=null}}else wt=bt?xn(e.stateNode.nextSibling):null;return!0}function Hd(){for(var e=wt;e;)e=xn(e.nextSibling)}function Ss(){wt=bt=null,Le=!1}function zo(e){It===null?It=[e]:It.push(e)}var Ov=V.ReactCurrentBatchConfig;function fi(e,n,a){if(e=a.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(a._owner){if(a=a._owner,a){if(a.tag!==1)throw Error(r(309));var l=a.stateNode}if(!l)throw Error(r(147,e));var d=l,m=""+e;return n!==null&&n.ref!==null&&typeof n.ref=="function"&&n.ref._stringRef===m?n.ref:(n=function(y){var k=d.refs;y===null?delete k[m]:k[m]=y},n._stringRef=m,n)}if(typeof e!="string")throw Error(r(284));if(!a._owner)throw Error(r(290,e))}return e}function wr(e,n){throw e=Object.prototype.toString.call(n),Error(r(31,e==="[object Object]"?"object with keys {"+Object.keys(n).join(", ")+"}":e))}function Gd(e){var n=e._init;return n(e._payload)}function Kd(e){function n(M,A){if(e){var R=M.deletions;R===null?(M.deletions=[A],M.flags|=16):R.push(A)}}function a(M,A){if(!e)return null;for(;A!==null;)n(M,A),A=A.sibling;return null}function l(M,A){for(M=new Map;A!==null;)A.key!==null?M.set(A.key,A):M.set(A.index,A),A=A.sibling;return M}function d(M,A){return M=En(M,A),M.index=0,M.sibling=null,M}function m(M,A,R){return M.index=R,e?(R=M.alternate,R!==null?(R=R.index,R<A?(M.flags|=2,A):R):(M.flags|=2,A)):(M.flags|=1048576,A)}function y(M){return e&&M.alternate===null&&(M.flags|=2),M}function k(M,A,R,K){return A===null||A.tag!==6?(A=_l(R,M.mode,K),A.return=M,A):(A=d(A,R),A.return=M,A)}function C(M,A,R,K){var oe=R.type;return oe===I?H(M,A,R.props.children,K,R.key):A!==null&&(A.elementType===oe||typeof oe=="object"&&oe!==null&&oe.$$typeof===Ce&&Gd(oe)===A.type)?(K=d(A,R.props),K.ref=fi(M,A,R),K.return=M,K):(K=Hr(R.type,R.key,R.props,null,M.mode,K),K.ref=fi(M,A,R),K.return=M,K)}function F(M,A,R,K){return A===null||A.tag!==4||A.stateNode.containerInfo!==R.containerInfo||A.stateNode.implementation!==R.implementation?(A=Dl(R,M.mode,K),A.return=M,A):(A=d(A,R.children||[]),A.return=M,A)}function H(M,A,R,K,oe){return A===null||A.tag!==7?(A=Yn(R,M.mode,K,oe),A.return=M,A):(A=d(A,R),A.return=M,A)}function G(M,A,R){if(typeof A=="string"&&A!==""||typeof A=="number")return A=_l(""+A,M.mode,R),A.return=M,A;if(typeof A=="object"&&A!==null){switch(A.$$typeof){case _:return R=Hr(A.type,A.key,A.props,null,M.mode,R),R.ref=fi(M,null,A),R.return=M,R;case L:return A=Dl(A,M.mode,R),A.return=M,A;case Ce:var K=A._init;return G(M,K(A._payload),R)}if(Ws(A)||Z(A))return A=Yn(A,M.mode,R,null),A.return=M,A;wr(M,A)}return null}function W(M,A,R,K){var oe=A!==null?A.key:null;if(typeof R=="string"&&R!==""||typeof R=="number")return oe!==null?null:k(M,A,""+R,K);if(typeof R=="object"&&R!==null){switch(R.$$typeof){case _:return R.key===oe?C(M,A,R,K):null;case L:return R.key===oe?F(M,A,R,K):null;case Ce:return oe=R._init,W(M,A,oe(R._payload),K)}if(Ws(R)||Z(R))return oe!==null?null:H(M,A,R,K,null);wr(M,R)}return null}function te(M,A,R,K,oe){if(typeof K=="string"&&K!==""||typeof K=="number")return M=M.get(R)||null,k(A,M,""+K,oe);if(typeof K=="object"&&K!==null){switch(K.$$typeof){case _:return M=M.get(K.key===null?R:K.key)||null,C(A,M,K,oe);case L:return M=M.get(K.key===null?R:K.key)||null,F(A,M,K,oe);case Ce:var ue=K._init;return te(M,A,R,ue(K._payload),oe)}if(Ws(K)||Z(K))return M=M.get(R)||null,H(A,M,K,oe,null);wr(A,K)}return null}function ie(M,A,R,K){for(var oe=null,ue=null,de=A,pe=A=0,Ze=null;de!==null&&pe<R.length;pe++){de.index>pe?(Ze=de,de=null):Ze=de.sibling;var Se=W(M,de,R[pe],K);if(Se===null){de===null&&(de=Ze);break}e&&de&&Se.alternate===null&&n(M,de),A=m(Se,A,pe),ue===null?oe=Se:ue.sibling=Se,ue=Se,de=Ze}if(pe===R.length)return a(M,de),Le&&Un(M,pe),oe;if(de===null){for(;pe<R.length;pe++)de=G(M,R[pe],K),de!==null&&(A=m(de,A,pe),ue===null?oe=de:ue.sibling=de,ue=de);return Le&&Un(M,pe),oe}for(de=l(M,de);pe<R.length;pe++)Ze=te(de,M,pe,R[pe],K),Ze!==null&&(e&&Ze.alternate!==null&&de.delete(Ze.key===null?pe:Ze.key),A=m(Ze,A,pe),ue===null?oe=Ze:ue.sibling=Ze,ue=Ze);return e&&de.forEach(function(Mn){return n(M,Mn)}),Le&&Un(M,pe),oe}function ae(M,A,R,K){var oe=Z(R);if(typeof oe!="function")throw Error(r(150));if(R=oe.call(R),R==null)throw Error(r(151));for(var ue=oe=null,de=A,pe=A=0,Ze=null,Se=R.next();de!==null&&!Se.done;pe++,Se=R.next()){de.index>pe?(Ze=de,de=null):Ze=de.sibling;var Mn=W(M,de,Se.value,K);if(Mn===null){de===null&&(de=Ze);break}e&&de&&Mn.alternate===null&&n(M,de),A=m(Mn,A,pe),ue===null?oe=Mn:ue.sibling=Mn,ue=Mn,de=Ze}if(Se.done)return a(M,de),Le&&Un(M,pe),oe;if(de===null){for(;!Se.done;pe++,Se=R.next())Se=G(M,Se.value,K),Se!==null&&(A=m(Se,A,pe),ue===null?oe=Se:ue.sibling=Se,ue=Se);return Le&&Un(M,pe),oe}for(de=l(M,de);!Se.done;pe++,Se=R.next())Se=te(de,M,pe,Se.value,K),Se!==null&&(e&&Se.alternate!==null&&de.delete(Se.key===null?pe:Se.key),A=m(Se,A,pe),ue===null?oe=Se:ue.sibling=Se,ue=Se);return e&&de.forEach(function(xx){return n(M,xx)}),Le&&Un(M,pe),oe}function ze(M,A,R,K){if(typeof R=="object"&&R!==null&&R.type===I&&R.key===null&&(R=R.props.children),typeof R=="object"&&R!==null){switch(R.$$typeof){case _:e:{for(var oe=R.key,ue=A;ue!==null;){if(ue.key===oe){if(oe=R.type,oe===I){if(ue.tag===7){a(M,ue.sibling),A=d(ue,R.props.children),A.return=M,M=A;break e}}else if(ue.elementType===oe||typeof oe=="object"&&oe!==null&&oe.$$typeof===Ce&&Gd(oe)===ue.type){a(M,ue.sibling),A=d(ue,R.props),A.ref=fi(M,ue,R),A.return=M,M=A;break e}a(M,ue);break}else n(M,ue);ue=ue.sibling}R.type===I?(A=Yn(R.props.children,M.mode,K,R.key),A.return=M,M=A):(K=Hr(R.type,R.key,R.props,null,M.mode,K),K.ref=fi(M,A,R),K.return=M,M=K)}return y(M);case L:e:{for(ue=R.key;A!==null;){if(A.key===ue)if(A.tag===4&&A.stateNode.containerInfo===R.containerInfo&&A.stateNode.implementation===R.implementation){a(M,A.sibling),A=d(A,R.children||[]),A.return=M,M=A;break e}else{a(M,A);break}else n(M,A);A=A.sibling}A=Dl(R,M.mode,K),A.return=M,M=A}return y(M);case Ce:return ue=R._init,ze(M,A,ue(R._payload),K)}if(Ws(R))return ie(M,A,R,K);if(Z(R))return ae(M,A,R,K);wr(M,R)}return typeof R=="string"&&R!==""||typeof R=="number"?(R=""+R,A!==null&&A.tag===6?(a(M,A.sibling),A=d(A,R),A.return=M,M=A):(a(M,A),A=_l(R,M.mode,K),A.return=M,M=A),y(M)):a(M,A)}return ze}var Ns=Kd(!0),qd=Kd(!1),kr=bn(null),jr=null,Cs=null,Uo=null;function $o(){Uo=Cs=jr=null}function Wo(e){var n=kr.current;De(kr),e._currentValue=n}function Ho(e,n,a){for(;e!==null;){var l=e.alternate;if((e.childLanes&n)!==n?(e.childLanes|=n,l!==null&&(l.childLanes|=n)):l!==null&&(l.childLanes&n)!==n&&(l.childLanes|=n),e===a)break;e=e.return}}function Ts(e,n){jr=e,Uo=Cs=null,e=e.dependencies,e!==null&&e.firstContext!==null&&((e.lanes&n)!==0&&(pt=!0),e.firstContext=null)}function At(e){var n=e._currentValue;if(Uo!==e)if(e={context:e,memoizedValue:n,next:null},Cs===null){if(jr===null)throw Error(r(308));Cs=e,jr.dependencies={lanes:0,firstContext:e}}else Cs=Cs.next=e;return n}var $n=null;function Go(e){$n===null?$n=[e]:$n.push(e)}function Xd(e,n,a,l){var d=n.interleaved;return d===null?(a.next=a,Go(n)):(a.next=d.next,d.next=a),n.interleaved=a,an(e,l)}function an(e,n){e.lanes|=n;var a=e.alternate;for(a!==null&&(a.lanes|=n),a=e,e=e.return;e!==null;)e.childLanes|=n,a=e.alternate,a!==null&&(a.childLanes|=n),a=e,e=e.return;return a.tag===3?a.stateNode:null}var jn=!1;function Ko(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function Yd(e,n){e=e.updateQueue,n.updateQueue===e&&(n.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function on(e,n){return{eventTime:e,lane:n,tag:0,payload:null,callback:null,next:null}}function Sn(e,n,a){var l=e.updateQueue;if(l===null)return null;if(l=l.shared,(je&2)!==0){var d=l.pending;return d===null?n.next=n:(n.next=d.next,d.next=n),l.pending=n,an(e,a)}return d=l.interleaved,d===null?(n.next=n,Go(l)):(n.next=d.next,d.next=n),l.interleaved=n,an(e,a)}function Sr(e,n,a){if(n=n.updateQueue,n!==null&&(n=n.shared,(a&4194240)!==0)){var l=n.lanes;l&=e.pendingLanes,a|=l,n.lanes=a,ao(e,a)}}function Qd(e,n){var a=e.updateQueue,l=e.alternate;if(l!==null&&(l=l.updateQueue,a===l)){var d=null,m=null;if(a=a.firstBaseUpdate,a!==null){do{var y={eventTime:a.eventTime,lane:a.lane,tag:a.tag,payload:a.payload,callback:a.callback,next:null};m===null?d=m=y:m=m.next=y,a=a.next}while(a!==null);m===null?d=m=n:m=m.next=n}else d=m=n;a={baseState:l.baseState,firstBaseUpdate:d,lastBaseUpdate:m,shared:l.shared,effects:l.effects},e.updateQueue=a;return}e=a.lastBaseUpdate,e===null?a.firstBaseUpdate=n:e.next=n,a.lastBaseUpdate=n}function Nr(e,n,a,l){var d=e.updateQueue;jn=!1;var m=d.firstBaseUpdate,y=d.lastBaseUpdate,k=d.shared.pending;if(k!==null){d.shared.pending=null;var C=k,F=C.next;C.next=null,y===null?m=F:y.next=F,y=C;var H=e.alternate;H!==null&&(H=H.updateQueue,k=H.lastBaseUpdate,k!==y&&(k===null?H.firstBaseUpdate=F:k.next=F,H.lastBaseUpdate=C))}if(m!==null){var G=d.baseState;y=0,H=F=C=null,k=m;do{var W=k.lane,te=k.eventTime;if((l&W)===W){H!==null&&(H=H.next={eventTime:te,lane:0,tag:k.tag,payload:k.payload,callback:k.callback,next:null});e:{var ie=e,ae=k;switch(W=n,te=a,ae.tag){case 1:if(ie=ae.payload,typeof ie=="function"){G=ie.call(te,G,W);break e}G=ie;break e;case 3:ie.flags=ie.flags&-65537|128;case 0:if(ie=ae.payload,W=typeof ie=="function"?ie.call(te,G,W):ie,W==null)break e;G=X({},G,W);break e;case 2:jn=!0}}k.callback!==null&&k.lane!==0&&(e.flags|=64,W=d.effects,W===null?d.effects=[k]:W.push(k))}else te={eventTime:te,lane:W,tag:k.tag,payload:k.payload,callback:k.callback,next:null},H===null?(F=H=te,C=G):H=H.next=te,y|=W;if(k=k.next,k===null){if(k=d.shared.pending,k===null)break;W=k,k=W.next,W.next=null,d.lastBaseUpdate=W,d.shared.pending=null}}while(!0);if(H===null&&(C=G),d.baseState=C,d.firstBaseUpdate=F,d.lastBaseUpdate=H,n=d.shared.interleaved,n!==null){d=n;do y|=d.lane,d=d.next;while(d!==n)}else m===null&&(d.shared.lanes=0);Gn|=y,e.lanes=y,e.memoizedState=G}}function Jd(e,n,a){if(e=n.effects,n.effects=null,e!==null)for(n=0;n<e.length;n++){var l=e[n],d=l.callback;if(d!==null){if(l.callback=null,l=a,typeof d!="function")throw Error(r(191,d));d.call(l)}}}var gi={},qt=bn(gi),yi=bn(gi),vi=bn(gi);function Wn(e){if(e===gi)throw Error(r(174));return e}function qo(e,n){switch(Me(vi,n),Me(yi,e),Me(qt,gi),e=n.nodeType,e){case 9:case 11:n=(n=n.documentElement)?n.namespaceURI:qa(null,"");break;default:e=e===8?n.parentNode:n,n=e.namespaceURI||null,e=e.tagName,n=qa(n,e)}De(qt),Me(qt,n)}function As(){De(qt),De(yi),De(vi)}function Zd(e){Wn(vi.current);var n=Wn(qt.current),a=qa(n,e.type);n!==a&&(Me(yi,e),Me(qt,a))}function Xo(e){yi.current===e&&(De(qt),De(yi))}var Ie=bn(0);function Cr(e){for(var n=e;n!==null;){if(n.tag===13){var a=n.memoizedState;if(a!==null&&(a=a.dehydrated,a===null||a.data==="$?"||a.data==="$!"))return n}else if(n.tag===19&&n.memoizedProps.revealOrder!==void 0){if((n.flags&128)!==0)return n}else if(n.child!==null){n.child.return=n,n=n.child;continue}if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return null;n=n.return}n.sibling.return=n.return,n=n.sibling}return null}var Yo=[];function Qo(){for(var e=0;e<Yo.length;e++)Yo[e]._workInProgressVersionPrimary=null;Yo.length=0}var Tr=V.ReactCurrentDispatcher,Jo=V.ReactCurrentBatchConfig,Hn=0,Ve=null,Ge=null,Qe=null,Ar=!1,xi=!1,bi=0,zv=0;function it(){throw Error(r(321))}function Zo(e,n){if(n===null)return!1;for(var a=0;a<n.length&&a<e.length;a++)if(!Lt(e[a],n[a]))return!1;return!0}function el(e,n,a,l,d,m){if(Hn=m,Ve=n,n.memoizedState=null,n.updateQueue=null,n.lanes=0,Tr.current=e===null||e.memoizedState===null?Hv:Gv,e=a(l,d),xi){m=0;do{if(xi=!1,bi=0,25<=m)throw Error(r(301));m+=1,Qe=Ge=null,n.updateQueue=null,Tr.current=Kv,e=a(l,d)}while(xi)}if(Tr.current=Mr,n=Ge!==null&&Ge.next!==null,Hn=0,Qe=Ge=Ve=null,Ar=!1,n)throw Error(r(300));return e}function tl(){var e=bi!==0;return bi=0,e}function Xt(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return Qe===null?Ve.memoizedState=Qe=e:Qe=Qe.next=e,Qe}function Pt(){if(Ge===null){var e=Ve.alternate;e=e!==null?e.memoizedState:null}else e=Ge.next;var n=Qe===null?Ve.memoizedState:Qe.next;if(n!==null)Qe=n,Ge=e;else{if(e===null)throw Error(r(310));Ge=e,e={memoizedState:Ge.memoizedState,baseState:Ge.baseState,baseQueue:Ge.baseQueue,queue:Ge.queue,next:null},Qe===null?Ve.memoizedState=Qe=e:Qe=Qe.next=e}return Qe}function wi(e,n){return typeof n=="function"?n(e):n}function nl(e){var n=Pt(),a=n.queue;if(a===null)throw Error(r(311));a.lastRenderedReducer=e;var l=Ge,d=l.baseQueue,m=a.pending;if(m!==null){if(d!==null){var y=d.next;d.next=m.next,m.next=y}l.baseQueue=d=m,a.pending=null}if(d!==null){m=d.next,l=l.baseState;var k=y=null,C=null,F=m;do{var H=F.lane;if((Hn&H)===H)C!==null&&(C=C.next={lane:0,action:F.action,hasEagerState:F.hasEagerState,eagerState:F.eagerState,next:null}),l=F.hasEagerState?F.eagerState:e(l,F.action);else{var G={lane:H,action:F.action,hasEagerState:F.hasEagerState,eagerState:F.eagerState,next:null};C===null?(k=C=G,y=l):C=C.next=G,Ve.lanes|=H,Gn|=H}F=F.next}while(F!==null&&F!==m);C===null?y=l:C.next=k,Lt(l,n.memoizedState)||(pt=!0),n.memoizedState=l,n.baseState=y,n.baseQueue=C,a.lastRenderedState=l}if(e=a.interleaved,e!==null){d=e;do m=d.lane,Ve.lanes|=m,Gn|=m,d=d.next;while(d!==e)}else d===null&&(a.lanes=0);return[n.memoizedState,a.dispatch]}function sl(e){var n=Pt(),a=n.queue;if(a===null)throw Error(r(311));a.lastRenderedReducer=e;var l=a.dispatch,d=a.pending,m=n.memoizedState;if(d!==null){a.pending=null;var y=d=d.next;do m=e(m,y.action),y=y.next;while(y!==d);Lt(m,n.memoizedState)||(pt=!0),n.memoizedState=m,n.baseQueue===null&&(n.baseState=m),a.lastRenderedState=m}return[m,l]}function eh(){}function th(e,n){var a=Ve,l=Pt(),d=n(),m=!Lt(l.memoizedState,d);if(m&&(l.memoizedState=d,pt=!0),l=l.queue,il(ih.bind(null,a,l,e),[e]),l.getSnapshot!==n||m||Qe!==null&&Qe.memoizedState.tag&1){if(a.flags|=2048,ki(9,sh.bind(null,a,l,d,n),void 0,null),Je===null)throw Error(r(349));(Hn&30)!==0||nh(a,n,d)}return d}function nh(e,n,a){e.flags|=16384,e={getSnapshot:n,value:a},n=Ve.updateQueue,n===null?(n={lastEffect:null,stores:null},Ve.updateQueue=n,n.stores=[e]):(a=n.stores,a===null?n.stores=[e]:a.push(e))}function sh(e,n,a,l){n.value=a,n.getSnapshot=l,rh(n)&&ah(e)}function ih(e,n,a){return a(function(){rh(n)&&ah(e)})}function rh(e){var n=e.getSnapshot;e=e.value;try{var a=n();return!Lt(e,a)}catch{return!0}}function ah(e){var n=an(e,1);n!==null&&Ot(n,e,1,-1)}function oh(e){var n=Xt();return typeof e=="function"&&(e=e()),n.memoizedState=n.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:wi,lastRenderedState:e},n.queue=e,e=e.dispatch=Wv.bind(null,Ve,e),[n.memoizedState,e]}function ki(e,n,a,l){return e={tag:e,create:n,destroy:a,deps:l,next:null},n=Ve.updateQueue,n===null?(n={lastEffect:null,stores:null},Ve.updateQueue=n,n.lastEffect=e.next=e):(a=n.lastEffect,a===null?n.lastEffect=e.next=e:(l=a.next,a.next=e,e.next=l,n.lastEffect=e)),e}function lh(){return Pt().memoizedState}function Pr(e,n,a,l){var d=Xt();Ve.flags|=e,d.memoizedState=ki(1|n,a,void 0,l===void 0?null:l)}function Er(e,n,a,l){var d=Pt();l=l===void 0?null:l;var m=void 0;if(Ge!==null){var y=Ge.memoizedState;if(m=y.destroy,l!==null&&Zo(l,y.deps)){d.memoizedState=ki(n,a,m,l);return}}Ve.flags|=e,d.memoizedState=ki(1|n,a,m,l)}function ch(e,n){return Pr(8390656,8,e,n)}function il(e,n){return Er(2048,8,e,n)}function uh(e,n){return Er(4,2,e,n)}function dh(e,n){return Er(4,4,e,n)}function hh(e,n){if(typeof n=="function")return e=e(),n(e),function(){n(null)};if(n!=null)return e=e(),n.current=e,function(){n.current=null}}function mh(e,n,a){return a=a!=null?a.concat([e]):null,Er(4,4,hh.bind(null,n,e),a)}function rl(){}function ph(e,n){var a=Pt();n=n===void 0?null:n;var l=a.memoizedState;return l!==null&&n!==null&&Zo(n,l[1])?l[0]:(a.memoizedState=[e,n],e)}function fh(e,n){var a=Pt();n=n===void 0?null:n;var l=a.memoizedState;return l!==null&&n!==null&&Zo(n,l[1])?l[0]:(e=e(),a.memoizedState=[e,n],e)}function gh(e,n,a){return(Hn&21)===0?(e.baseState&&(e.baseState=!1,pt=!0),e.memoizedState=a):(Lt(a,n)||(a=Gu(),Ve.lanes|=a,Gn|=a,e.baseState=!0),n)}function Uv(e,n){var a=Te;Te=a!==0&&4>a?a:4,e(!0);var l=Jo.transition;Jo.transition={};try{e(!1),n()}finally{Te=a,Jo.transition=l}}function yh(){return Pt().memoizedState}function $v(e,n,a){var l=An(e);if(a={lane:l,action:a,hasEagerState:!1,eagerState:null,next:null},vh(e))xh(n,a);else if(a=Xd(e,n,a,l),a!==null){var d=ct();Ot(a,e,l,d),bh(a,n,l)}}function Wv(e,n,a){var l=An(e),d={lane:l,action:a,hasEagerState:!1,eagerState:null,next:null};if(vh(e))xh(n,d);else{var m=e.alternate;if(e.lanes===0&&(m===null||m.lanes===0)&&(m=n.lastRenderedReducer,m!==null))try{var y=n.lastRenderedState,k=m(y,a);if(d.hasEagerState=!0,d.eagerState=k,Lt(k,y)){var C=n.interleaved;C===null?(d.next=d,Go(n)):(d.next=C.next,C.next=d),n.interleaved=d;return}}catch{}finally{}a=Xd(e,n,d,l),a!==null&&(d=ct(),Ot(a,e,l,d),bh(a,n,l))}}function vh(e){var n=e.alternate;return e===Ve||n!==null&&n===Ve}function xh(e,n){xi=Ar=!0;var a=e.pending;a===null?n.next=n:(n.next=a.next,a.next=n),e.pending=n}function bh(e,n,a){if((a&4194240)!==0){var l=n.lanes;l&=e.pendingLanes,a|=l,n.lanes=a,ao(e,a)}}var Mr={readContext:At,useCallback:it,useContext:it,useEffect:it,useImperativeHandle:it,useInsertionEffect:it,useLayoutEffect:it,useMemo:it,useReducer:it,useRef:it,useState:it,useDebugValue:it,useDeferredValue:it,useTransition:it,useMutableSource:it,useSyncExternalStore:it,useId:it,unstable_isNewReconciler:!1},Hv={readContext:At,useCallback:function(e,n){return Xt().memoizedState=[e,n===void 0?null:n],e},useContext:At,useEffect:ch,useImperativeHandle:function(e,n,a){return a=a!=null?a.concat([e]):null,Pr(4194308,4,hh.bind(null,n,e),a)},useLayoutEffect:function(e,n){return Pr(4194308,4,e,n)},useInsertionEffect:function(e,n){return Pr(4,2,e,n)},useMemo:function(e,n){var a=Xt();return n=n===void 0?null:n,e=e(),a.memoizedState=[e,n],e},useReducer:function(e,n,a){var l=Xt();return n=a!==void 0?a(n):n,l.memoizedState=l.baseState=n,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:n},l.queue=e,e=e.dispatch=$v.bind(null,Ve,e),[l.memoizedState,e]},useRef:function(e){var n=Xt();return e={current:e},n.memoizedState=e},useState:oh,useDebugValue:rl,useDeferredValue:function(e){return Xt().memoizedState=e},useTransition:function(){var e=oh(!1),n=e[0];return e=Uv.bind(null,e[1]),Xt().memoizedState=e,[n,e]},useMutableSource:function(){},useSyncExternalStore:function(e,n,a){var l=Ve,d=Xt();if(Le){if(a===void 0)throw Error(r(407));a=a()}else{if(a=n(),Je===null)throw Error(r(349));(Hn&30)!==0||nh(l,n,a)}d.memoizedState=a;var m={value:a,getSnapshot:n};return d.queue=m,ch(ih.bind(null,l,m,e),[e]),l.flags|=2048,ki(9,sh.bind(null,l,m,a,n),void 0,null),a},useId:function(){var e=Xt(),n=Je.identifierPrefix;if(Le){var a=rn,l=sn;a=(l&~(1<<32-Rt(l)-1)).toString(32)+a,n=":"+n+"R"+a,a=bi++,0<a&&(n+="H"+a.toString(32)),n+=":"}else a=zv++,n=":"+n+"r"+a.toString(32)+":";return e.memoizedState=n},unstable_isNewReconciler:!1},Gv={readContext:At,useCallback:ph,useContext:At,useEffect:il,useImperativeHandle:mh,useInsertionEffect:uh,useLayoutEffect:dh,useMemo:fh,useReducer:nl,useRef:lh,useState:function(){return nl(wi)},useDebugValue:rl,useDeferredValue:function(e){var n=Pt();return gh(n,Ge.memoizedState,e)},useTransition:function(){var e=nl(wi)[0],n=Pt().memoizedState;return[e,n]},useMutableSource:eh,useSyncExternalStore:th,useId:yh,unstable_isNewReconciler:!1},Kv={readContext:At,useCallback:ph,useContext:At,useEffect:il,useImperativeHandle:mh,useInsertionEffect:uh,useLayoutEffect:dh,useMemo:fh,useReducer:sl,useRef:lh,useState:function(){return sl(wi)},useDebugValue:rl,useDeferredValue:function(e){var n=Pt();return Ge===null?n.memoizedState=e:gh(n,Ge.memoizedState,e)},useTransition:function(){var e=sl(wi)[0],n=Pt().memoizedState;return[e,n]},useMutableSource:eh,useSyncExternalStore:th,useId:yh,unstable_isNewReconciler:!1};function Vt(e,n){if(e&&e.defaultProps){n=X({},n),e=e.defaultProps;for(var a in e)n[a]===void 0&&(n[a]=e[a]);return n}return n}function al(e,n,a,l){n=e.memoizedState,a=a(l,n),a=a==null?n:X({},n,a),e.memoizedState=a,e.lanes===0&&(e.updateQueue.baseState=a)}var _r={isMounted:function(e){return(e=e._reactInternals)?Fn(e)===e:!1},enqueueSetState:function(e,n,a){e=e._reactInternals;var l=ct(),d=An(e),m=on(l,d);m.payload=n,a!=null&&(m.callback=a),n=Sn(e,m,d),n!==null&&(Ot(n,e,d,l),Sr(n,e,d))},enqueueReplaceState:function(e,n,a){e=e._reactInternals;var l=ct(),d=An(e),m=on(l,d);m.tag=1,m.payload=n,a!=null&&(m.callback=a),n=Sn(e,m,d),n!==null&&(Ot(n,e,d,l),Sr(n,e,d))},enqueueForceUpdate:function(e,n){e=e._reactInternals;var a=ct(),l=An(e),d=on(a,l);d.tag=2,n!=null&&(d.callback=n),n=Sn(e,d,l),n!==null&&(Ot(n,e,l,a),Sr(n,e,l))}};function wh(e,n,a,l,d,m,y){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(l,m,y):n.prototype&&n.prototype.isPureReactComponent?!li(a,l)||!li(d,m):!0}function kh(e,n,a){var l=!1,d=wn,m=n.contextType;return typeof m=="object"&&m!==null?m=At(m):(d=mt(n)?On:st.current,l=n.contextTypes,m=(l=l!=null)?ws(e,d):wn),n=new n(a,m),e.memoizedState=n.state!==null&&n.state!==void 0?n.state:null,n.updater=_r,e.stateNode=n,n._reactInternals=e,l&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=d,e.__reactInternalMemoizedMaskedChildContext=m),n}function jh(e,n,a,l){e=n.state,typeof n.componentWillReceiveProps=="function"&&n.componentWillReceiveProps(a,l),typeof n.UNSAFE_componentWillReceiveProps=="function"&&n.UNSAFE_componentWillReceiveProps(a,l),n.state!==e&&_r.enqueueReplaceState(n,n.state,null)}function ol(e,n,a,l){var d=e.stateNode;d.props=a,d.state=e.memoizedState,d.refs={},Ko(e);var m=n.contextType;typeof m=="object"&&m!==null?d.context=At(m):(m=mt(n)?On:st.current,d.context=ws(e,m)),d.state=e.memoizedState,m=n.getDerivedStateFromProps,typeof m=="function"&&(al(e,n,m,a),d.state=e.memoizedState),typeof n.getDerivedStateFromProps=="function"||typeof d.getSnapshotBeforeUpdate=="function"||typeof d.UNSAFE_componentWillMount!="function"&&typeof d.componentWillMount!="function"||(n=d.state,typeof d.componentWillMount=="function"&&d.componentWillMount(),typeof d.UNSAFE_componentWillMount=="function"&&d.UNSAFE_componentWillMount(),n!==d.state&&_r.enqueueReplaceState(d,d.state,null),Nr(e,a,d,l),d.state=e.memoizedState),typeof d.componentDidMount=="function"&&(e.flags|=4194308)}function Ps(e,n){try{var a="",l=n;do a+=ke(l),l=l.return;while(l);var d=a}catch(m){d=`
Error generating stack: `+m.message+`
`+m.stack}return{value:e,source:n,stack:d,digest:null}}function ll(e,n,a){return{value:e,source:null,stack:a??null,digest:n??null}}function cl(e,n){try{console.error(n.value)}catch(a){setTimeout(function(){throw a})}}var qv=typeof WeakMap=="function"?WeakMap:Map;function Sh(e,n,a){a=on(-1,a),a.tag=3,a.payload={element:null};var l=n.value;return a.callback=function(){Br||(Br=!0,Sl=l),cl(e,n)},a}function Nh(e,n,a){a=on(-1,a),a.tag=3;var l=e.type.getDerivedStateFromError;if(typeof l=="function"){var d=n.value;a.payload=function(){return l(d)},a.callback=function(){cl(e,n)}}var m=e.stateNode;return m!==null&&typeof m.componentDidCatch=="function"&&(a.callback=function(){cl(e,n),typeof l!="function"&&(Cn===null?Cn=new Set([this]):Cn.add(this));var y=n.stack;this.componentDidCatch(n.value,{componentStack:y!==null?y:""})}),a}function Ch(e,n,a){var l=e.pingCache;if(l===null){l=e.pingCache=new qv;var d=new Set;l.set(n,d)}else d=l.get(n),d===void 0&&(d=new Set,l.set(n,d));d.has(a)||(d.add(a),e=lx.bind(null,e,n,a),n.then(e,e))}function Th(e){do{var n;if((n=e.tag===13)&&(n=e.memoizedState,n=n!==null?n.dehydrated!==null:!0),n)return e;e=e.return}while(e!==null);return null}function Ah(e,n,a,l,d){return(e.mode&1)===0?(e===n?e.flags|=65536:(e.flags|=128,a.flags|=131072,a.flags&=-52805,a.tag===1&&(a.alternate===null?a.tag=17:(n=on(-1,1),n.tag=2,Sn(a,n,1))),a.lanes|=1),e):(e.flags|=65536,e.lanes=d,e)}var Xv=V.ReactCurrentOwner,pt=!1;function lt(e,n,a,l){n.child=e===null?qd(n,null,a,l):Ns(n,e.child,a,l)}function Ph(e,n,a,l,d){a=a.render;var m=n.ref;return Ts(n,d),l=el(e,n,a,l,m,d),a=tl(),e!==null&&!pt?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~d,ln(e,n,d)):(Le&&a&&Vo(n),n.flags|=1,lt(e,n,l,d),n.child)}function Eh(e,n,a,l,d){if(e===null){var m=a.type;return typeof m=="function"&&!Ml(m)&&m.defaultProps===void 0&&a.compare===null&&a.defaultProps===void 0?(n.tag=15,n.type=m,Mh(e,n,m,l,d)):(e=Hr(a.type,null,l,n,n.mode,d),e.ref=n.ref,e.return=n,n.child=e)}if(m=e.child,(e.lanes&d)===0){var y=m.memoizedProps;if(a=a.compare,a=a!==null?a:li,a(y,l)&&e.ref===n.ref)return ln(e,n,d)}return n.flags|=1,e=En(m,l),e.ref=n.ref,e.return=n,n.child=e}function Mh(e,n,a,l,d){if(e!==null){var m=e.memoizedProps;if(li(m,l)&&e.ref===n.ref)if(pt=!1,n.pendingProps=l=m,(e.lanes&d)!==0)(e.flags&131072)!==0&&(pt=!0);else return n.lanes=e.lanes,ln(e,n,d)}return ul(e,n,a,l,d)}function _h(e,n,a){var l=n.pendingProps,d=l.children,m=e!==null?e.memoizedState:null;if(l.mode==="hidden")if((n.mode&1)===0)n.memoizedState={baseLanes:0,cachePool:null,transitions:null},Me(Ms,kt),kt|=a;else{if((a&1073741824)===0)return e=m!==null?m.baseLanes|a:a,n.lanes=n.childLanes=1073741824,n.memoizedState={baseLanes:e,cachePool:null,transitions:null},n.updateQueue=null,Me(Ms,kt),kt|=e,null;n.memoizedState={baseLanes:0,cachePool:null,transitions:null},l=m!==null?m.baseLanes:a,Me(Ms,kt),kt|=l}else m!==null?(l=m.baseLanes|a,n.memoizedState=null):l=a,Me(Ms,kt),kt|=l;return lt(e,n,d,a),n.child}function Dh(e,n){var a=n.ref;(e===null&&a!==null||e!==null&&e.ref!==a)&&(n.flags|=512,n.flags|=2097152)}function ul(e,n,a,l,d){var m=mt(a)?On:st.current;return m=ws(n,m),Ts(n,d),a=el(e,n,a,l,m,d),l=tl(),e!==null&&!pt?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~d,ln(e,n,d)):(Le&&l&&Vo(n),n.flags|=1,lt(e,n,a,d),n.child)}function Rh(e,n,a,l,d){if(mt(a)){var m=!0;gr(n)}else m=!1;if(Ts(n,d),n.stateNode===null)Rr(e,n),kh(n,a,l),ol(n,a,l,d),l=!0;else if(e===null){var y=n.stateNode,k=n.memoizedProps;y.props=k;var C=y.context,F=a.contextType;typeof F=="object"&&F!==null?F=At(F):(F=mt(a)?On:st.current,F=ws(n,F));var H=a.getDerivedStateFromProps,G=typeof H=="function"||typeof y.getSnapshotBeforeUpdate=="function";G||typeof y.UNSAFE_componentWillReceiveProps!="function"&&typeof y.componentWillReceiveProps!="function"||(k!==l||C!==F)&&jh(n,y,l,F),jn=!1;var W=n.memoizedState;y.state=W,Nr(n,l,y,d),C=n.memoizedState,k!==l||W!==C||ht.current||jn?(typeof H=="function"&&(al(n,a,H,l),C=n.memoizedState),(k=jn||wh(n,a,k,l,W,C,F))?(G||typeof y.UNSAFE_componentWillMount!="function"&&typeof y.componentWillMount!="function"||(typeof y.componentWillMount=="function"&&y.componentWillMount(),typeof y.UNSAFE_componentWillMount=="function"&&y.UNSAFE_componentWillMount()),typeof y.componentDidMount=="function"&&(n.flags|=4194308)):(typeof y.componentDidMount=="function"&&(n.flags|=4194308),n.memoizedProps=l,n.memoizedState=C),y.props=l,y.state=C,y.context=F,l=k):(typeof y.componentDidMount=="function"&&(n.flags|=4194308),l=!1)}else{y=n.stateNode,Yd(e,n),k=n.memoizedProps,F=n.type===n.elementType?k:Vt(n.type,k),y.props=F,G=n.pendingProps,W=y.context,C=a.contextType,typeof C=="object"&&C!==null?C=At(C):(C=mt(a)?On:st.current,C=ws(n,C));var te=a.getDerivedStateFromProps;(H=typeof te=="function"||typeof y.getSnapshotBeforeUpdate=="function")||typeof y.UNSAFE_componentWillReceiveProps!="function"&&typeof y.componentWillReceiveProps!="function"||(k!==G||W!==C)&&jh(n,y,l,C),jn=!1,W=n.memoizedState,y.state=W,Nr(n,l,y,d);var ie=n.memoizedState;k!==G||W!==ie||ht.current||jn?(typeof te=="function"&&(al(n,a,te,l),ie=n.memoizedState),(F=jn||wh(n,a,F,l,W,ie,C)||!1)?(H||typeof y.UNSAFE_componentWillUpdate!="function"&&typeof y.componentWillUpdate!="function"||(typeof y.componentWillUpdate=="function"&&y.componentWillUpdate(l,ie,C),typeof y.UNSAFE_componentWillUpdate=="function"&&y.UNSAFE_componentWillUpdate(l,ie,C)),typeof y.componentDidUpdate=="function"&&(n.flags|=4),typeof y.getSnapshotBeforeUpdate=="function"&&(n.flags|=1024)):(typeof y.componentDidUpdate!="function"||k===e.memoizedProps&&W===e.memoizedState||(n.flags|=4),typeof y.getSnapshotBeforeUpdate!="function"||k===e.memoizedProps&&W===e.memoizedState||(n.flags|=1024),n.memoizedProps=l,n.memoizedState=ie),y.props=l,y.state=ie,y.context=C,l=F):(typeof y.componentDidUpdate!="function"||k===e.memoizedProps&&W===e.memoizedState||(n.flags|=4),typeof y.getSnapshotBeforeUpdate!="function"||k===e.memoizedProps&&W===e.memoizedState||(n.flags|=1024),l=!1)}return dl(e,n,a,l,m,d)}function dl(e,n,a,l,d,m){Dh(e,n);var y=(n.flags&128)!==0;if(!l&&!y)return d&&Bd(n,a,!1),ln(e,n,m);l=n.stateNode,Xv.current=n;var k=y&&typeof a.getDerivedStateFromError!="function"?null:l.render();return n.flags|=1,e!==null&&y?(n.child=Ns(n,e.child,null,m),n.child=Ns(n,null,k,m)):lt(e,n,k,m),n.memoizedState=l.state,d&&Bd(n,a,!0),n.child}function Lh(e){var n=e.stateNode;n.pendingContext?Vd(e,n.pendingContext,n.pendingContext!==n.context):n.context&&Vd(e,n.context,!1),qo(e,n.containerInfo)}function Ih(e,n,a,l,d){return Ss(),zo(d),n.flags|=256,lt(e,n,a,l),n.child}var hl={dehydrated:null,treeContext:null,retryLane:0};function ml(e){return{baseLanes:e,cachePool:null,transitions:null}}function Vh(e,n,a){var l=n.pendingProps,d=Ie.current,m=!1,y=(n.flags&128)!==0,k;if((k=y)||(k=e!==null&&e.memoizedState===null?!1:(d&2)!==0),k?(m=!0,n.flags&=-129):(e===null||e.memoizedState!==null)&&(d|=1),Me(Ie,d&1),e===null)return Oo(n),e=n.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?((n.mode&1)===0?n.lanes=1:e.data==="$!"?n.lanes=8:n.lanes=1073741824,null):(y=l.children,e=l.fallback,m?(l=n.mode,m=n.child,y={mode:"hidden",children:y},(l&1)===0&&m!==null?(m.childLanes=0,m.pendingProps=y):m=Gr(y,l,0,null),e=Yn(e,l,a,null),m.return=n,e.return=n,m.sibling=e,n.child=m,n.child.memoizedState=ml(a),n.memoizedState=hl,e):pl(n,y));if(d=e.memoizedState,d!==null&&(k=d.dehydrated,k!==null))return Yv(e,n,y,l,k,d,a);if(m){m=l.fallback,y=n.mode,d=e.child,k=d.sibling;var C={mode:"hidden",children:l.children};return(y&1)===0&&n.child!==d?(l=n.child,l.childLanes=0,l.pendingProps=C,n.deletions=null):(l=En(d,C),l.subtreeFlags=d.subtreeFlags&14680064),k!==null?m=En(k,m):(m=Yn(m,y,a,null),m.flags|=2),m.return=n,l.return=n,l.sibling=m,n.child=l,l=m,m=n.child,y=e.child.memoizedState,y=y===null?ml(a):{baseLanes:y.baseLanes|a,cachePool:null,transitions:y.transitions},m.memoizedState=y,m.childLanes=e.childLanes&~a,n.memoizedState=hl,l}return m=e.child,e=m.sibling,l=En(m,{mode:"visible",children:l.children}),(n.mode&1)===0&&(l.lanes=a),l.return=n,l.sibling=null,e!==null&&(a=n.deletions,a===null?(n.deletions=[e],n.flags|=16):a.push(e)),n.child=l,n.memoizedState=null,l}function pl(e,n){return n=Gr({mode:"visible",children:n},e.mode,0,null),n.return=e,e.child=n}function Dr(e,n,a,l){return l!==null&&zo(l),Ns(n,e.child,null,a),e=pl(n,n.pendingProps.children),e.flags|=2,n.memoizedState=null,e}function Yv(e,n,a,l,d,m,y){if(a)return n.flags&256?(n.flags&=-257,l=ll(Error(r(422))),Dr(e,n,y,l)):n.memoizedState!==null?(n.child=e.child,n.flags|=128,null):(m=l.fallback,d=n.mode,l=Gr({mode:"visible",children:l.children},d,0,null),m=Yn(m,d,y,null),m.flags|=2,l.return=n,m.return=n,l.sibling=m,n.child=l,(n.mode&1)!==0&&Ns(n,e.child,null,y),n.child.memoizedState=ml(y),n.memoizedState=hl,m);if((n.mode&1)===0)return Dr(e,n,y,null);if(d.data==="$!"){if(l=d.nextSibling&&d.nextSibling.dataset,l)var k=l.dgst;return l=k,m=Error(r(419)),l=ll(m,l,void 0),Dr(e,n,y,l)}if(k=(y&e.childLanes)!==0,pt||k){if(l=Je,l!==null){switch(y&-y){case 4:d=2;break;case 16:d=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:d=32;break;case 536870912:d=268435456;break;default:d=0}d=(d&(l.suspendedLanes|y))!==0?0:d,d!==0&&d!==m.retryLane&&(m.retryLane=d,an(e,d),Ot(l,e,d,-1))}return El(),l=ll(Error(r(421))),Dr(e,n,y,l)}return d.data==="$?"?(n.flags|=128,n.child=e.child,n=cx.bind(null,e),d._reactRetry=n,null):(e=m.treeContext,wt=xn(d.nextSibling),bt=n,Le=!0,It=null,e!==null&&(Ct[Tt++]=sn,Ct[Tt++]=rn,Ct[Tt++]=zn,sn=e.id,rn=e.overflow,zn=n),n=pl(n,l.children),n.flags|=4096,n)}function Fh(e,n,a){e.lanes|=n;var l=e.alternate;l!==null&&(l.lanes|=n),Ho(e.return,n,a)}function fl(e,n,a,l,d){var m=e.memoizedState;m===null?e.memoizedState={isBackwards:n,rendering:null,renderingStartTime:0,last:l,tail:a,tailMode:d}:(m.isBackwards=n,m.rendering=null,m.renderingStartTime=0,m.last=l,m.tail=a,m.tailMode=d)}function Bh(e,n,a){var l=n.pendingProps,d=l.revealOrder,m=l.tail;if(lt(e,n,l.children,a),l=Ie.current,(l&2)!==0)l=l&1|2,n.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=n.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Fh(e,a,n);else if(e.tag===19)Fh(e,a,n);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===n)break e;for(;e.sibling===null;){if(e.return===null||e.return===n)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}l&=1}if(Me(Ie,l),(n.mode&1)===0)n.memoizedState=null;else switch(d){case"forwards":for(a=n.child,d=null;a!==null;)e=a.alternate,e!==null&&Cr(e)===null&&(d=a),a=a.sibling;a=d,a===null?(d=n.child,n.child=null):(d=a.sibling,a.sibling=null),fl(n,!1,d,a,m);break;case"backwards":for(a=null,d=n.child,n.child=null;d!==null;){if(e=d.alternate,e!==null&&Cr(e)===null){n.child=d;break}e=d.sibling,d.sibling=a,a=d,d=e}fl(n,!0,a,null,m);break;case"together":fl(n,!1,null,null,void 0);break;default:n.memoizedState=null}return n.child}function Rr(e,n){(n.mode&1)===0&&e!==null&&(e.alternate=null,n.alternate=null,n.flags|=2)}function ln(e,n,a){if(e!==null&&(n.dependencies=e.dependencies),Gn|=n.lanes,(a&n.childLanes)===0)return null;if(e!==null&&n.child!==e.child)throw Error(r(153));if(n.child!==null){for(e=n.child,a=En(e,e.pendingProps),n.child=a,a.return=n;e.sibling!==null;)e=e.sibling,a=a.sibling=En(e,e.pendingProps),a.return=n;a.sibling=null}return n.child}function Qv(e,n,a){switch(n.tag){case 3:Lh(n),Ss();break;case 5:Zd(n);break;case 1:mt(n.type)&&gr(n);break;case 4:qo(n,n.stateNode.containerInfo);break;case 10:var l=n.type._context,d=n.memoizedProps.value;Me(kr,l._currentValue),l._currentValue=d;break;case 13:if(l=n.memoizedState,l!==null)return l.dehydrated!==null?(Me(Ie,Ie.current&1),n.flags|=128,null):(a&n.child.childLanes)!==0?Vh(e,n,a):(Me(Ie,Ie.current&1),e=ln(e,n,a),e!==null?e.sibling:null);Me(Ie,Ie.current&1);break;case 19:if(l=(a&n.childLanes)!==0,(e.flags&128)!==0){if(l)return Bh(e,n,a);n.flags|=128}if(d=n.memoizedState,d!==null&&(d.rendering=null,d.tail=null,d.lastEffect=null),Me(Ie,Ie.current),l)break;return null;case 22:case 23:return n.lanes=0,_h(e,n,a)}return ln(e,n,a)}var Oh,gl,zh,Uh;Oh=function(e,n){for(var a=n.child;a!==null;){if(a.tag===5||a.tag===6)e.appendChild(a.stateNode);else if(a.tag!==4&&a.child!==null){a.child.return=a,a=a.child;continue}if(a===n)break;for(;a.sibling===null;){if(a.return===null||a.return===n)return;a=a.return}a.sibling.return=a.return,a=a.sibling}},gl=function(){},zh=function(e,n,a,l){var d=e.memoizedProps;if(d!==l){e=n.stateNode,Wn(qt.current);var m=null;switch(a){case"input":d=Vn(e,d),l=Vn(e,l),m=[];break;case"select":d=X({},d,{value:void 0}),l=X({},l,{value:void 0}),m=[];break;case"textarea":d=Ka(e,d),l=Ka(e,l),m=[];break;default:typeof d.onClick!="function"&&typeof l.onClick=="function"&&(e.onclick=mr)}Xa(a,l);var y;a=null;for(F in d)if(!l.hasOwnProperty(F)&&d.hasOwnProperty(F)&&d[F]!=null)if(F==="style"){var k=d[F];for(y in k)k.hasOwnProperty(y)&&(a||(a={}),a[y]="")}else F!=="dangerouslySetInnerHTML"&&F!=="children"&&F!=="suppressContentEditableWarning"&&F!=="suppressHydrationWarning"&&F!=="autoFocus"&&(c.hasOwnProperty(F)?m||(m=[]):(m=m||[]).push(F,null));for(F in l){var C=l[F];if(k=d!=null?d[F]:void 0,l.hasOwnProperty(F)&&C!==k&&(C!=null||k!=null))if(F==="style")if(k){for(y in k)!k.hasOwnProperty(y)||C&&C.hasOwnProperty(y)||(a||(a={}),a[y]="");for(y in C)C.hasOwnProperty(y)&&k[y]!==C[y]&&(a||(a={}),a[y]=C[y])}else a||(m||(m=[]),m.push(F,a)),a=C;else F==="dangerouslySetInnerHTML"?(C=C?C.__html:void 0,k=k?k.__html:void 0,C!=null&&k!==C&&(m=m||[]).push(F,C)):F==="children"?typeof C!="string"&&typeof C!="number"||(m=m||[]).push(F,""+C):F!=="suppressContentEditableWarning"&&F!=="suppressHydrationWarning"&&(c.hasOwnProperty(F)?(C!=null&&F==="onScroll"&&_e("scroll",e),m||k===C||(m=[])):(m=m||[]).push(F,C))}a&&(m=m||[]).push("style",a);var F=m;(n.updateQueue=F)&&(n.flags|=4)}},Uh=function(e,n,a,l){a!==l&&(n.flags|=4)};function ji(e,n){if(!Le)switch(e.tailMode){case"hidden":n=e.tail;for(var a=null;n!==null;)n.alternate!==null&&(a=n),n=n.sibling;a===null?e.tail=null:a.sibling=null;break;case"collapsed":a=e.tail;for(var l=null;a!==null;)a.alternate!==null&&(l=a),a=a.sibling;l===null?n||e.tail===null?e.tail=null:e.tail.sibling=null:l.sibling=null}}function rt(e){var n=e.alternate!==null&&e.alternate.child===e.child,a=0,l=0;if(n)for(var d=e.child;d!==null;)a|=d.lanes|d.childLanes,l|=d.subtreeFlags&14680064,l|=d.flags&14680064,d.return=e,d=d.sibling;else for(d=e.child;d!==null;)a|=d.lanes|d.childLanes,l|=d.subtreeFlags,l|=d.flags,d.return=e,d=d.sibling;return e.subtreeFlags|=l,e.childLanes=a,n}function Jv(e,n,a){var l=n.pendingProps;switch(Fo(n),n.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return rt(n),null;case 1:return mt(n.type)&&fr(),rt(n),null;case 3:return l=n.stateNode,As(),De(ht),De(st),Qo(),l.pendingContext&&(l.context=l.pendingContext,l.pendingContext=null),(e===null||e.child===null)&&(br(n)?n.flags|=4:e===null||e.memoizedState.isDehydrated&&(n.flags&256)===0||(n.flags|=1024,It!==null&&(Tl(It),It=null))),gl(e,n),rt(n),null;case 5:Xo(n);var d=Wn(vi.current);if(a=n.type,e!==null&&n.stateNode!=null)zh(e,n,a,l,d),e.ref!==n.ref&&(n.flags|=512,n.flags|=2097152);else{if(!l){if(n.stateNode===null)throw Error(r(166));return rt(n),null}if(e=Wn(qt.current),br(n)){l=n.stateNode,a=n.type;var m=n.memoizedProps;switch(l[Kt]=n,l[mi]=m,e=(n.mode&1)!==0,a){case"dialog":_e("cancel",l),_e("close",l);break;case"iframe":case"object":case"embed":_e("load",l);break;case"video":case"audio":for(d=0;d<ui.length;d++)_e(ui[d],l);break;case"source":_e("error",l);break;case"img":case"image":case"link":_e("error",l),_e("load",l);break;case"details":_e("toggle",l);break;case"input":Wi(l,m),_e("invalid",l);break;case"select":l._wrapperState={wasMultiple:!!m.multiple},_e("invalid",l);break;case"textarea":Nu(l,m),_e("invalid",l)}Xa(a,m),d=null;for(var y in m)if(m.hasOwnProperty(y)){var k=m[y];y==="children"?typeof k=="string"?l.textContent!==k&&(m.suppressHydrationWarning!==!0&&hr(l.textContent,k,e),d=["children",k]):typeof k=="number"&&l.textContent!==""+k&&(m.suppressHydrationWarning!==!0&&hr(l.textContent,k,e),d=["children",""+k]):c.hasOwnProperty(y)&&k!=null&&y==="onScroll"&&_e("scroll",l)}switch(a){case"input":Re(l),Su(l,m,!0);break;case"textarea":Re(l),Tu(l);break;case"select":case"option":break;default:typeof m.onClick=="function"&&(l.onclick=mr)}l=d,n.updateQueue=l,l!==null&&(n.flags|=4)}else{y=d.nodeType===9?d:d.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=Au(a)),e==="http://www.w3.org/1999/xhtml"?a==="script"?(e=y.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof l.is=="string"?e=y.createElement(a,{is:l.is}):(e=y.createElement(a),a==="select"&&(y=e,l.multiple?y.multiple=!0:l.size&&(y.size=l.size))):e=y.createElementNS(e,a),e[Kt]=n,e[mi]=l,Oh(e,n,!1,!1),n.stateNode=e;e:{switch(y=Ya(a,l),a){case"dialog":_e("cancel",e),_e("close",e),d=l;break;case"iframe":case"object":case"embed":_e("load",e),d=l;break;case"video":case"audio":for(d=0;d<ui.length;d++)_e(ui[d],e);d=l;break;case"source":_e("error",e),d=l;break;case"img":case"image":case"link":_e("error",e),_e("load",e),d=l;break;case"details":_e("toggle",e),d=l;break;case"input":Wi(e,l),d=Vn(e,l),_e("invalid",e);break;case"option":d=l;break;case"select":e._wrapperState={wasMultiple:!!l.multiple},d=X({},l,{value:void 0}),_e("invalid",e);break;case"textarea":Nu(e,l),d=Ka(e,l),_e("invalid",e);break;default:d=l}Xa(a,d),k=d;for(m in k)if(k.hasOwnProperty(m)){var C=k[m];m==="style"?Mu(e,C):m==="dangerouslySetInnerHTML"?(C=C?C.__html:void 0,C!=null&&Pu(e,C)):m==="children"?typeof C=="string"?(a!=="textarea"||C!=="")&&Hs(e,C):typeof C=="number"&&Hs(e,""+C):m!=="suppressContentEditableWarning"&&m!=="suppressHydrationWarning"&&m!=="autoFocus"&&(c.hasOwnProperty(m)?C!=null&&m==="onScroll"&&_e("scroll",e):C!=null&&D(e,m,C,y))}switch(a){case"input":Re(e),Su(e,l,!1);break;case"textarea":Re(e),Tu(e);break;case"option":l.value!=null&&e.setAttribute("value",""+Q(l.value));break;case"select":e.multiple=!!l.multiple,m=l.value,m!=null?cs(e,!!l.multiple,m,!1):l.defaultValue!=null&&cs(e,!!l.multiple,l.defaultValue,!0);break;default:typeof d.onClick=="function"&&(e.onclick=mr)}switch(a){case"button":case"input":case"select":case"textarea":l=!!l.autoFocus;break e;case"img":l=!0;break e;default:l=!1}}l&&(n.flags|=4)}n.ref!==null&&(n.flags|=512,n.flags|=2097152)}return rt(n),null;case 6:if(e&&n.stateNode!=null)Uh(e,n,e.memoizedProps,l);else{if(typeof l!="string"&&n.stateNode===null)throw Error(r(166));if(a=Wn(vi.current),Wn(qt.current),br(n)){if(l=n.stateNode,a=n.memoizedProps,l[Kt]=n,(m=l.nodeValue!==a)&&(e=bt,e!==null))switch(e.tag){case 3:hr(l.nodeValue,a,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&hr(l.nodeValue,a,(e.mode&1)!==0)}m&&(n.flags|=4)}else l=(a.nodeType===9?a:a.ownerDocument).createTextNode(l),l[Kt]=n,n.stateNode=l}return rt(n),null;case 13:if(De(Ie),l=n.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(Le&&wt!==null&&(n.mode&1)!==0&&(n.flags&128)===0)Hd(),Ss(),n.flags|=98560,m=!1;else if(m=br(n),l!==null&&l.dehydrated!==null){if(e===null){if(!m)throw Error(r(318));if(m=n.memoizedState,m=m!==null?m.dehydrated:null,!m)throw Error(r(317));m[Kt]=n}else Ss(),(n.flags&128)===0&&(n.memoizedState=null),n.flags|=4;rt(n),m=!1}else It!==null&&(Tl(It),It=null),m=!0;if(!m)return n.flags&65536?n:null}return(n.flags&128)!==0?(n.lanes=a,n):(l=l!==null,l!==(e!==null&&e.memoizedState!==null)&&l&&(n.child.flags|=8192,(n.mode&1)!==0&&(e===null||(Ie.current&1)!==0?Ke===0&&(Ke=3):El())),n.updateQueue!==null&&(n.flags|=4),rt(n),null);case 4:return As(),gl(e,n),e===null&&di(n.stateNode.containerInfo),rt(n),null;case 10:return Wo(n.type._context),rt(n),null;case 17:return mt(n.type)&&fr(),rt(n),null;case 19:if(De(Ie),m=n.memoizedState,m===null)return rt(n),null;if(l=(n.flags&128)!==0,y=m.rendering,y===null)if(l)ji(m,!1);else{if(Ke!==0||e!==null&&(e.flags&128)!==0)for(e=n.child;e!==null;){if(y=Cr(e),y!==null){for(n.flags|=128,ji(m,!1),l=y.updateQueue,l!==null&&(n.updateQueue=l,n.flags|=4),n.subtreeFlags=0,l=a,a=n.child;a!==null;)m=a,e=l,m.flags&=14680066,y=m.alternate,y===null?(m.childLanes=0,m.lanes=e,m.child=null,m.subtreeFlags=0,m.memoizedProps=null,m.memoizedState=null,m.updateQueue=null,m.dependencies=null,m.stateNode=null):(m.childLanes=y.childLanes,m.lanes=y.lanes,m.child=y.child,m.subtreeFlags=0,m.deletions=null,m.memoizedProps=y.memoizedProps,m.memoizedState=y.memoizedState,m.updateQueue=y.updateQueue,m.type=y.type,e=y.dependencies,m.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),a=a.sibling;return Me(Ie,Ie.current&1|2),n.child}e=e.sibling}m.tail!==null&&Oe()>_s&&(n.flags|=128,l=!0,ji(m,!1),n.lanes=4194304)}else{if(!l)if(e=Cr(y),e!==null){if(n.flags|=128,l=!0,a=e.updateQueue,a!==null&&(n.updateQueue=a,n.flags|=4),ji(m,!0),m.tail===null&&m.tailMode==="hidden"&&!y.alternate&&!Le)return rt(n),null}else 2*Oe()-m.renderingStartTime>_s&&a!==1073741824&&(n.flags|=128,l=!0,ji(m,!1),n.lanes=4194304);m.isBackwards?(y.sibling=n.child,n.child=y):(a=m.last,a!==null?a.sibling=y:n.child=y,m.last=y)}return m.tail!==null?(n=m.tail,m.rendering=n,m.tail=n.sibling,m.renderingStartTime=Oe(),n.sibling=null,a=Ie.current,Me(Ie,l?a&1|2:a&1),n):(rt(n),null);case 22:case 23:return Pl(),l=n.memoizedState!==null,e!==null&&e.memoizedState!==null!==l&&(n.flags|=8192),l&&(n.mode&1)!==0?(kt&1073741824)!==0&&(rt(n),n.subtreeFlags&6&&(n.flags|=8192)):rt(n),null;case 24:return null;case 25:return null}throw Error(r(156,n.tag))}function Zv(e,n){switch(Fo(n),n.tag){case 1:return mt(n.type)&&fr(),e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 3:return As(),De(ht),De(st),Qo(),e=n.flags,(e&65536)!==0&&(e&128)===0?(n.flags=e&-65537|128,n):null;case 5:return Xo(n),null;case 13:if(De(Ie),e=n.memoizedState,e!==null&&e.dehydrated!==null){if(n.alternate===null)throw Error(r(340));Ss()}return e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 19:return De(Ie),null;case 4:return As(),null;case 10:return Wo(n.type._context),null;case 22:case 23:return Pl(),null;case 24:return null;default:return null}}var Lr=!1,at=!1,ex=typeof WeakSet=="function"?WeakSet:Set,se=null;function Es(e,n){var a=e.ref;if(a!==null)if(typeof a=="function")try{a(null)}catch(l){Fe(e,n,l)}else a.current=null}function yl(e,n,a){try{a()}catch(l){Fe(e,n,l)}}var $h=!1;function tx(e,n){if(Po=tr,e=wd(),wo(e)){if("selectionStart"in e)var a={start:e.selectionStart,end:e.selectionEnd};else e:{a=(a=e.ownerDocument)&&a.defaultView||window;var l=a.getSelection&&a.getSelection();if(l&&l.rangeCount!==0){a=l.anchorNode;var d=l.anchorOffset,m=l.focusNode;l=l.focusOffset;try{a.nodeType,m.nodeType}catch{a=null;break e}var y=0,k=-1,C=-1,F=0,H=0,G=e,W=null;t:for(;;){for(var te;G!==a||d!==0&&G.nodeType!==3||(k=y+d),G!==m||l!==0&&G.nodeType!==3||(C=y+l),G.nodeType===3&&(y+=G.nodeValue.length),(te=G.firstChild)!==null;)W=G,G=te;for(;;){if(G===e)break t;if(W===a&&++F===d&&(k=y),W===m&&++H===l&&(C=y),(te=G.nextSibling)!==null)break;G=W,W=G.parentNode}G=te}a=k===-1||C===-1?null:{start:k,end:C}}else a=null}a=a||{start:0,end:0}}else a=null;for(Eo={focusedElem:e,selectionRange:a},tr=!1,se=n;se!==null;)if(n=se,e=n.child,(n.subtreeFlags&1028)!==0&&e!==null)e.return=n,se=e;else for(;se!==null;){n=se;try{var ie=n.alternate;if((n.flags&1024)!==0)switch(n.tag){case 0:case 11:case 15:break;case 1:if(ie!==null){var ae=ie.memoizedProps,ze=ie.memoizedState,M=n.stateNode,A=M.getSnapshotBeforeUpdate(n.elementType===n.type?ae:Vt(n.type,ae),ze);M.__reactInternalSnapshotBeforeUpdate=A}break;case 3:var R=n.stateNode.containerInfo;R.nodeType===1?R.textContent="":R.nodeType===9&&R.documentElement&&R.removeChild(R.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(r(163))}}catch(K){Fe(n,n.return,K)}if(e=n.sibling,e!==null){e.return=n.return,se=e;break}se=n.return}return ie=$h,$h=!1,ie}function Si(e,n,a){var l=n.updateQueue;if(l=l!==null?l.lastEffect:null,l!==null){var d=l=l.next;do{if((d.tag&e)===e){var m=d.destroy;d.destroy=void 0,m!==void 0&&yl(n,a,m)}d=d.next}while(d!==l)}}function Ir(e,n){if(n=n.updateQueue,n=n!==null?n.lastEffect:null,n!==null){var a=n=n.next;do{if((a.tag&e)===e){var l=a.create;a.destroy=l()}a=a.next}while(a!==n)}}function vl(e){var n=e.ref;if(n!==null){var a=e.stateNode;switch(e.tag){case 5:e=a;break;default:e=a}typeof n=="function"?n(e):n.current=e}}function Wh(e){var n=e.alternate;n!==null&&(e.alternate=null,Wh(n)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(n=e.stateNode,n!==null&&(delete n[Kt],delete n[mi],delete n[Ro],delete n[Vv],delete n[Fv])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function Hh(e){return e.tag===5||e.tag===3||e.tag===4}function Gh(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||Hh(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function xl(e,n,a){var l=e.tag;if(l===5||l===6)e=e.stateNode,n?a.nodeType===8?a.parentNode.insertBefore(e,n):a.insertBefore(e,n):(a.nodeType===8?(n=a.parentNode,n.insertBefore(e,a)):(n=a,n.appendChild(e)),a=a._reactRootContainer,a!=null||n.onclick!==null||(n.onclick=mr));else if(l!==4&&(e=e.child,e!==null))for(xl(e,n,a),e=e.sibling;e!==null;)xl(e,n,a),e=e.sibling}function bl(e,n,a){var l=e.tag;if(l===5||l===6)e=e.stateNode,n?a.insertBefore(e,n):a.appendChild(e);else if(l!==4&&(e=e.child,e!==null))for(bl(e,n,a),e=e.sibling;e!==null;)bl(e,n,a),e=e.sibling}var et=null,Ft=!1;function Nn(e,n,a){for(a=a.child;a!==null;)Kh(e,n,a),a=a.sibling}function Kh(e,n,a){if(Gt&&typeof Gt.onCommitFiberUnmount=="function")try{Gt.onCommitFiberUnmount(Xi,a)}catch{}switch(a.tag){case 5:at||Es(a,n);case 6:var l=et,d=Ft;et=null,Nn(e,n,a),et=l,Ft=d,et!==null&&(Ft?(e=et,a=a.stateNode,e.nodeType===8?e.parentNode.removeChild(a):e.removeChild(a)):et.removeChild(a.stateNode));break;case 18:et!==null&&(Ft?(e=et,a=a.stateNode,e.nodeType===8?Do(e.parentNode,a):e.nodeType===1&&Do(e,a),ni(e)):Do(et,a.stateNode));break;case 4:l=et,d=Ft,et=a.stateNode.containerInfo,Ft=!0,Nn(e,n,a),et=l,Ft=d;break;case 0:case 11:case 14:case 15:if(!at&&(l=a.updateQueue,l!==null&&(l=l.lastEffect,l!==null))){d=l=l.next;do{var m=d,y=m.destroy;m=m.tag,y!==void 0&&((m&2)!==0||(m&4)!==0)&&yl(a,n,y),d=d.next}while(d!==l)}Nn(e,n,a);break;case 1:if(!at&&(Es(a,n),l=a.stateNode,typeof l.componentWillUnmount=="function"))try{l.props=a.memoizedProps,l.state=a.memoizedState,l.componentWillUnmount()}catch(k){Fe(a,n,k)}Nn(e,n,a);break;case 21:Nn(e,n,a);break;case 22:a.mode&1?(at=(l=at)||a.memoizedState!==null,Nn(e,n,a),at=l):Nn(e,n,a);break;default:Nn(e,n,a)}}function qh(e){var n=e.updateQueue;if(n!==null){e.updateQueue=null;var a=e.stateNode;a===null&&(a=e.stateNode=new ex),n.forEach(function(l){var d=ux.bind(null,e,l);a.has(l)||(a.add(l),l.then(d,d))})}}function Bt(e,n){var a=n.deletions;if(a!==null)for(var l=0;l<a.length;l++){var d=a[l];try{var m=e,y=n,k=y;e:for(;k!==null;){switch(k.tag){case 5:et=k.stateNode,Ft=!1;break e;case 3:et=k.stateNode.containerInfo,Ft=!0;break e;case 4:et=k.stateNode.containerInfo,Ft=!0;break e}k=k.return}if(et===null)throw Error(r(160));Kh(m,y,d),et=null,Ft=!1;var C=d.alternate;C!==null&&(C.return=null),d.return=null}catch(F){Fe(d,n,F)}}if(n.subtreeFlags&12854)for(n=n.child;n!==null;)Xh(n,e),n=n.sibling}function Xh(e,n){var a=e.alternate,l=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(Bt(n,e),Yt(e),l&4){try{Si(3,e,e.return),Ir(3,e)}catch(ae){Fe(e,e.return,ae)}try{Si(5,e,e.return)}catch(ae){Fe(e,e.return,ae)}}break;case 1:Bt(n,e),Yt(e),l&512&&a!==null&&Es(a,a.return);break;case 5:if(Bt(n,e),Yt(e),l&512&&a!==null&&Es(a,a.return),e.flags&32){var d=e.stateNode;try{Hs(d,"")}catch(ae){Fe(e,e.return,ae)}}if(l&4&&(d=e.stateNode,d!=null)){var m=e.memoizedProps,y=a!==null?a.memoizedProps:m,k=e.type,C=e.updateQueue;if(e.updateQueue=null,C!==null)try{k==="input"&&m.type==="radio"&&m.name!=null&&ju(d,m),Ya(k,y);var F=Ya(k,m);for(y=0;y<C.length;y+=2){var H=C[y],G=C[y+1];H==="style"?Mu(d,G):H==="dangerouslySetInnerHTML"?Pu(d,G):H==="children"?Hs(d,G):D(d,H,G,F)}switch(k){case"input":Ha(d,m);break;case"textarea":Cu(d,m);break;case"select":var W=d._wrapperState.wasMultiple;d._wrapperState.wasMultiple=!!m.multiple;var te=m.value;te!=null?cs(d,!!m.multiple,te,!1):W!==!!m.multiple&&(m.defaultValue!=null?cs(d,!!m.multiple,m.defaultValue,!0):cs(d,!!m.multiple,m.multiple?[]:"",!1))}d[mi]=m}catch(ae){Fe(e,e.return,ae)}}break;case 6:if(Bt(n,e),Yt(e),l&4){if(e.stateNode===null)throw Error(r(162));d=e.stateNode,m=e.memoizedProps;try{d.nodeValue=m}catch(ae){Fe(e,e.return,ae)}}break;case 3:if(Bt(n,e),Yt(e),l&4&&a!==null&&a.memoizedState.isDehydrated)try{ni(n.containerInfo)}catch(ae){Fe(e,e.return,ae)}break;case 4:Bt(n,e),Yt(e);break;case 13:Bt(n,e),Yt(e),d=e.child,d.flags&8192&&(m=d.memoizedState!==null,d.stateNode.isHidden=m,!m||d.alternate!==null&&d.alternate.memoizedState!==null||(jl=Oe())),l&4&&qh(e);break;case 22:if(H=a!==null&&a.memoizedState!==null,e.mode&1?(at=(F=at)||H,Bt(n,e),at=F):Bt(n,e),Yt(e),l&8192){if(F=e.memoizedState!==null,(e.stateNode.isHidden=F)&&!H&&(e.mode&1)!==0)for(se=e,H=e.child;H!==null;){for(G=se=H;se!==null;){switch(W=se,te=W.child,W.tag){case 0:case 11:case 14:case 15:Si(4,W,W.return);break;case 1:Es(W,W.return);var ie=W.stateNode;if(typeof ie.componentWillUnmount=="function"){l=W,a=W.return;try{n=l,ie.props=n.memoizedProps,ie.state=n.memoizedState,ie.componentWillUnmount()}catch(ae){Fe(l,a,ae)}}break;case 5:Es(W,W.return);break;case 22:if(W.memoizedState!==null){Jh(G);continue}}te!==null?(te.return=W,se=te):Jh(G)}H=H.sibling}e:for(H=null,G=e;;){if(G.tag===5){if(H===null){H=G;try{d=G.stateNode,F?(m=d.style,typeof m.setProperty=="function"?m.setProperty("display","none","important"):m.display="none"):(k=G.stateNode,C=G.memoizedProps.style,y=C!=null&&C.hasOwnProperty("display")?C.display:null,k.style.display=Eu("display",y))}catch(ae){Fe(e,e.return,ae)}}}else if(G.tag===6){if(H===null)try{G.stateNode.nodeValue=F?"":G.memoizedProps}catch(ae){Fe(e,e.return,ae)}}else if((G.tag!==22&&G.tag!==23||G.memoizedState===null||G===e)&&G.child!==null){G.child.return=G,G=G.child;continue}if(G===e)break e;for(;G.sibling===null;){if(G.return===null||G.return===e)break e;H===G&&(H=null),G=G.return}H===G&&(H=null),G.sibling.return=G.return,G=G.sibling}}break;case 19:Bt(n,e),Yt(e),l&4&&qh(e);break;case 21:break;default:Bt(n,e),Yt(e)}}function Yt(e){var n=e.flags;if(n&2){try{e:{for(var a=e.return;a!==null;){if(Hh(a)){var l=a;break e}a=a.return}throw Error(r(160))}switch(l.tag){case 5:var d=l.stateNode;l.flags&32&&(Hs(d,""),l.flags&=-33);var m=Gh(e);bl(e,m,d);break;case 3:case 4:var y=l.stateNode.containerInfo,k=Gh(e);xl(e,k,y);break;default:throw Error(r(161))}}catch(C){Fe(e,e.return,C)}e.flags&=-3}n&4096&&(e.flags&=-4097)}function nx(e,n,a){se=e,Yh(e)}function Yh(e,n,a){for(var l=(e.mode&1)!==0;se!==null;){var d=se,m=d.child;if(d.tag===22&&l){var y=d.memoizedState!==null||Lr;if(!y){var k=d.alternate,C=k!==null&&k.memoizedState!==null||at;k=Lr;var F=at;if(Lr=y,(at=C)&&!F)for(se=d;se!==null;)y=se,C=y.child,y.tag===22&&y.memoizedState!==null?Zh(d):C!==null?(C.return=y,se=C):Zh(d);for(;m!==null;)se=m,Yh(m),m=m.sibling;se=d,Lr=k,at=F}Qh(e)}else(d.subtreeFlags&8772)!==0&&m!==null?(m.return=d,se=m):Qh(e)}}function Qh(e){for(;se!==null;){var n=se;if((n.flags&8772)!==0){var a=n.alternate;try{if((n.flags&8772)!==0)switch(n.tag){case 0:case 11:case 15:at||Ir(5,n);break;case 1:var l=n.stateNode;if(n.flags&4&&!at)if(a===null)l.componentDidMount();else{var d=n.elementType===n.type?a.memoizedProps:Vt(n.type,a.memoizedProps);l.componentDidUpdate(d,a.memoizedState,l.__reactInternalSnapshotBeforeUpdate)}var m=n.updateQueue;m!==null&&Jd(n,m,l);break;case 3:var y=n.updateQueue;if(y!==null){if(a=null,n.child!==null)switch(n.child.tag){case 5:a=n.child.stateNode;break;case 1:a=n.child.stateNode}Jd(n,y,a)}break;case 5:var k=n.stateNode;if(a===null&&n.flags&4){a=k;var C=n.memoizedProps;switch(n.type){case"button":case"input":case"select":case"textarea":C.autoFocus&&a.focus();break;case"img":C.src&&(a.src=C.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(n.memoizedState===null){var F=n.alternate;if(F!==null){var H=F.memoizedState;if(H!==null){var G=H.dehydrated;G!==null&&ni(G)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(r(163))}at||n.flags&512&&vl(n)}catch(W){Fe(n,n.return,W)}}if(n===e){se=null;break}if(a=n.sibling,a!==null){a.return=n.return,se=a;break}se=n.return}}function Jh(e){for(;se!==null;){var n=se;if(n===e){se=null;break}var a=n.sibling;if(a!==null){a.return=n.return,se=a;break}se=n.return}}function Zh(e){for(;se!==null;){var n=se;try{switch(n.tag){case 0:case 11:case 15:var a=n.return;try{Ir(4,n)}catch(C){Fe(n,a,C)}break;case 1:var l=n.stateNode;if(typeof l.componentDidMount=="function"){var d=n.return;try{l.componentDidMount()}catch(C){Fe(n,d,C)}}var m=n.return;try{vl(n)}catch(C){Fe(n,m,C)}break;case 5:var y=n.return;try{vl(n)}catch(C){Fe(n,y,C)}}}catch(C){Fe(n,n.return,C)}if(n===e){se=null;break}var k=n.sibling;if(k!==null){k.return=n.return,se=k;break}se=n.return}}var sx=Math.ceil,Vr=V.ReactCurrentDispatcher,wl=V.ReactCurrentOwner,Et=V.ReactCurrentBatchConfig,je=0,Je=null,We=null,tt=0,kt=0,Ms=bn(0),Ke=0,Ni=null,Gn=0,Fr=0,kl=0,Ci=null,ft=null,jl=0,_s=1/0,cn=null,Br=!1,Sl=null,Cn=null,Or=!1,Tn=null,zr=0,Ti=0,Nl=null,Ur=-1,$r=0;function ct(){return(je&6)!==0?Oe():Ur!==-1?Ur:Ur=Oe()}function An(e){return(e.mode&1)===0?1:(je&2)!==0&&tt!==0?tt&-tt:Ov.transition!==null?($r===0&&($r=Gu()),$r):(e=Te,e!==0||(e=window.event,e=e===void 0?16:td(e.type)),e)}function Ot(e,n,a,l){if(50<Ti)throw Ti=0,Nl=null,Error(r(185));Qs(e,a,l),((je&2)===0||e!==Je)&&(e===Je&&((je&2)===0&&(Fr|=a),Ke===4&&Pn(e,tt)),gt(e,l),a===1&&je===0&&(n.mode&1)===0&&(_s=Oe()+500,yr&&kn()))}function gt(e,n){var a=e.callbackNode;Oy(e,n);var l=Ji(e,e===Je?tt:0);if(l===0)a!==null&&$u(a),e.callbackNode=null,e.callbackPriority=0;else if(n=l&-l,e.callbackPriority!==n){if(a!=null&&$u(a),n===1)e.tag===0?Bv(tm.bind(null,e)):Od(tm.bind(null,e)),Lv(function(){(je&6)===0&&kn()}),a=null;else{switch(Ku(l)){case 1:a=so;break;case 4:a=Wu;break;case 16:a=qi;break;case 536870912:a=Hu;break;default:a=qi}a=cm(a,em.bind(null,e))}e.callbackPriority=n,e.callbackNode=a}}function em(e,n){if(Ur=-1,$r=0,(je&6)!==0)throw Error(r(327));var a=e.callbackNode;if(Ds()&&e.callbackNode!==a)return null;var l=Ji(e,e===Je?tt:0);if(l===0)return null;if((l&30)!==0||(l&e.expiredLanes)!==0||n)n=Wr(e,l);else{n=l;var d=je;je|=2;var m=sm();(Je!==e||tt!==n)&&(cn=null,_s=Oe()+500,qn(e,n));do try{ax();break}catch(k){nm(e,k)}while(!0);$o(),Vr.current=m,je=d,We!==null?n=0:(Je=null,tt=0,n=Ke)}if(n!==0){if(n===2&&(d=io(e),d!==0&&(l=d,n=Cl(e,d))),n===1)throw a=Ni,qn(e,0),Pn(e,l),gt(e,Oe()),a;if(n===6)Pn(e,l);else{if(d=e.current.alternate,(l&30)===0&&!ix(d)&&(n=Wr(e,l),n===2&&(m=io(e),m!==0&&(l=m,n=Cl(e,m))),n===1))throw a=Ni,qn(e,0),Pn(e,l),gt(e,Oe()),a;switch(e.finishedWork=d,e.finishedLanes=l,n){case 0:case 1:throw Error(r(345));case 2:Xn(e,ft,cn);break;case 3:if(Pn(e,l),(l&130023424)===l&&(n=jl+500-Oe(),10<n)){if(Ji(e,0)!==0)break;if(d=e.suspendedLanes,(d&l)!==l){ct(),e.pingedLanes|=e.suspendedLanes&d;break}e.timeoutHandle=_o(Xn.bind(null,e,ft,cn),n);break}Xn(e,ft,cn);break;case 4:if(Pn(e,l),(l&4194240)===l)break;for(n=e.eventTimes,d=-1;0<l;){var y=31-Rt(l);m=1<<y,y=n[y],y>d&&(d=y),l&=~m}if(l=d,l=Oe()-l,l=(120>l?120:480>l?480:1080>l?1080:1920>l?1920:3e3>l?3e3:4320>l?4320:1960*sx(l/1960))-l,10<l){e.timeoutHandle=_o(Xn.bind(null,e,ft,cn),l);break}Xn(e,ft,cn);break;case 5:Xn(e,ft,cn);break;default:throw Error(r(329))}}}return gt(e,Oe()),e.callbackNode===a?em.bind(null,e):null}function Cl(e,n){var a=Ci;return e.current.memoizedState.isDehydrated&&(qn(e,n).flags|=256),e=Wr(e,n),e!==2&&(n=ft,ft=a,n!==null&&Tl(n)),e}function Tl(e){ft===null?ft=e:ft.push.apply(ft,e)}function ix(e){for(var n=e;;){if(n.flags&16384){var a=n.updateQueue;if(a!==null&&(a=a.stores,a!==null))for(var l=0;l<a.length;l++){var d=a[l],m=d.getSnapshot;d=d.value;try{if(!Lt(m(),d))return!1}catch{return!1}}}if(a=n.child,n.subtreeFlags&16384&&a!==null)a.return=n,n=a;else{if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return!0;n=n.return}n.sibling.return=n.return,n=n.sibling}}return!0}function Pn(e,n){for(n&=~kl,n&=~Fr,e.suspendedLanes|=n,e.pingedLanes&=~n,e=e.expirationTimes;0<n;){var a=31-Rt(n),l=1<<a;e[a]=-1,n&=~l}}function tm(e){if((je&6)!==0)throw Error(r(327));Ds();var n=Ji(e,0);if((n&1)===0)return gt(e,Oe()),null;var a=Wr(e,n);if(e.tag!==0&&a===2){var l=io(e);l!==0&&(n=l,a=Cl(e,l))}if(a===1)throw a=Ni,qn(e,0),Pn(e,n),gt(e,Oe()),a;if(a===6)throw Error(r(345));return e.finishedWork=e.current.alternate,e.finishedLanes=n,Xn(e,ft,cn),gt(e,Oe()),null}function Al(e,n){var a=je;je|=1;try{return e(n)}finally{je=a,je===0&&(_s=Oe()+500,yr&&kn())}}function Kn(e){Tn!==null&&Tn.tag===0&&(je&6)===0&&Ds();var n=je;je|=1;var a=Et.transition,l=Te;try{if(Et.transition=null,Te=1,e)return e()}finally{Te=l,Et.transition=a,je=n,(je&6)===0&&kn()}}function Pl(){kt=Ms.current,De(Ms)}function qn(e,n){e.finishedWork=null,e.finishedLanes=0;var a=e.timeoutHandle;if(a!==-1&&(e.timeoutHandle=-1,Rv(a)),We!==null)for(a=We.return;a!==null;){var l=a;switch(Fo(l),l.tag){case 1:l=l.type.childContextTypes,l!=null&&fr();break;case 3:As(),De(ht),De(st),Qo();break;case 5:Xo(l);break;case 4:As();break;case 13:De(Ie);break;case 19:De(Ie);break;case 10:Wo(l.type._context);break;case 22:case 23:Pl()}a=a.return}if(Je=e,We=e=En(e.current,null),tt=kt=n,Ke=0,Ni=null,kl=Fr=Gn=0,ft=Ci=null,$n!==null){for(n=0;n<$n.length;n++)if(a=$n[n],l=a.interleaved,l!==null){a.interleaved=null;var d=l.next,m=a.pending;if(m!==null){var y=m.next;m.next=d,l.next=y}a.pending=l}$n=null}return e}function nm(e,n){do{var a=We;try{if($o(),Tr.current=Mr,Ar){for(var l=Ve.memoizedState;l!==null;){var d=l.queue;d!==null&&(d.pending=null),l=l.next}Ar=!1}if(Hn=0,Qe=Ge=Ve=null,xi=!1,bi=0,wl.current=null,a===null||a.return===null){Ke=1,Ni=n,We=null;break}e:{var m=e,y=a.return,k=a,C=n;if(n=tt,k.flags|=32768,C!==null&&typeof C=="object"&&typeof C.then=="function"){var F=C,H=k,G=H.tag;if((H.mode&1)===0&&(G===0||G===11||G===15)){var W=H.alternate;W?(H.updateQueue=W.updateQueue,H.memoizedState=W.memoizedState,H.lanes=W.lanes):(H.updateQueue=null,H.memoizedState=null)}var te=Th(y);if(te!==null){te.flags&=-257,Ah(te,y,k,m,n),te.mode&1&&Ch(m,F,n),n=te,C=F;var ie=n.updateQueue;if(ie===null){var ae=new Set;ae.add(C),n.updateQueue=ae}else ie.add(C);break e}else{if((n&1)===0){Ch(m,F,n),El();break e}C=Error(r(426))}}else if(Le&&k.mode&1){var ze=Th(y);if(ze!==null){(ze.flags&65536)===0&&(ze.flags|=256),Ah(ze,y,k,m,n),zo(Ps(C,k));break e}}m=C=Ps(C,k),Ke!==4&&(Ke=2),Ci===null?Ci=[m]:Ci.push(m),m=y;do{switch(m.tag){case 3:m.flags|=65536,n&=-n,m.lanes|=n;var M=Sh(m,C,n);Qd(m,M);break e;case 1:k=C;var A=m.type,R=m.stateNode;if((m.flags&128)===0&&(typeof A.getDerivedStateFromError=="function"||R!==null&&typeof R.componentDidCatch=="function"&&(Cn===null||!Cn.has(R)))){m.flags|=65536,n&=-n,m.lanes|=n;var K=Nh(m,k,n);Qd(m,K);break e}}m=m.return}while(m!==null)}rm(a)}catch(oe){n=oe,We===a&&a!==null&&(We=a=a.return);continue}break}while(!0)}function sm(){var e=Vr.current;return Vr.current=Mr,e===null?Mr:e}function El(){(Ke===0||Ke===3||Ke===2)&&(Ke=4),Je===null||(Gn&268435455)===0&&(Fr&268435455)===0||Pn(Je,tt)}function Wr(e,n){var a=je;je|=2;var l=sm();(Je!==e||tt!==n)&&(cn=null,qn(e,n));do try{rx();break}catch(d){nm(e,d)}while(!0);if($o(),je=a,Vr.current=l,We!==null)throw Error(r(261));return Je=null,tt=0,Ke}function rx(){for(;We!==null;)im(We)}function ax(){for(;We!==null&&!My();)im(We)}function im(e){var n=lm(e.alternate,e,kt);e.memoizedProps=e.pendingProps,n===null?rm(e):We=n,wl.current=null}function rm(e){var n=e;do{var a=n.alternate;if(e=n.return,(n.flags&32768)===0){if(a=Jv(a,n,kt),a!==null){We=a;return}}else{if(a=Zv(a,n),a!==null){a.flags&=32767,We=a;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{Ke=6,We=null;return}}if(n=n.sibling,n!==null){We=n;return}We=n=e}while(n!==null);Ke===0&&(Ke=5)}function Xn(e,n,a){var l=Te,d=Et.transition;try{Et.transition=null,Te=1,ox(e,n,a,l)}finally{Et.transition=d,Te=l}return null}function ox(e,n,a,l){do Ds();while(Tn!==null);if((je&6)!==0)throw Error(r(327));a=e.finishedWork;var d=e.finishedLanes;if(a===null)return null;if(e.finishedWork=null,e.finishedLanes=0,a===e.current)throw Error(r(177));e.callbackNode=null,e.callbackPriority=0;var m=a.lanes|a.childLanes;if(zy(e,m),e===Je&&(We=Je=null,tt=0),(a.subtreeFlags&2064)===0&&(a.flags&2064)===0||Or||(Or=!0,cm(qi,function(){return Ds(),null})),m=(a.flags&15990)!==0,(a.subtreeFlags&15990)!==0||m){m=Et.transition,Et.transition=null;var y=Te;Te=1;var k=je;je|=4,wl.current=null,tx(e,a),Xh(a,e),Tv(Eo),tr=!!Po,Eo=Po=null,e.current=a,nx(a),_y(),je=k,Te=y,Et.transition=m}else e.current=a;if(Or&&(Or=!1,Tn=e,zr=d),m=e.pendingLanes,m===0&&(Cn=null),Ly(a.stateNode),gt(e,Oe()),n!==null)for(l=e.onRecoverableError,a=0;a<n.length;a++)d=n[a],l(d.value,{componentStack:d.stack,digest:d.digest});if(Br)throw Br=!1,e=Sl,Sl=null,e;return(zr&1)!==0&&e.tag!==0&&Ds(),m=e.pendingLanes,(m&1)!==0?e===Nl?Ti++:(Ti=0,Nl=e):Ti=0,kn(),null}function Ds(){if(Tn!==null){var e=Ku(zr),n=Et.transition,a=Te;try{if(Et.transition=null,Te=16>e?16:e,Tn===null)var l=!1;else{if(e=Tn,Tn=null,zr=0,(je&6)!==0)throw Error(r(331));var d=je;for(je|=4,se=e.current;se!==null;){var m=se,y=m.child;if((se.flags&16)!==0){var k=m.deletions;if(k!==null){for(var C=0;C<k.length;C++){var F=k[C];for(se=F;se!==null;){var H=se;switch(H.tag){case 0:case 11:case 15:Si(8,H,m)}var G=H.child;if(G!==null)G.return=H,se=G;else for(;se!==null;){H=se;var W=H.sibling,te=H.return;if(Wh(H),H===F){se=null;break}if(W!==null){W.return=te,se=W;break}se=te}}}var ie=m.alternate;if(ie!==null){var ae=ie.child;if(ae!==null){ie.child=null;do{var ze=ae.sibling;ae.sibling=null,ae=ze}while(ae!==null)}}se=m}}if((m.subtreeFlags&2064)!==0&&y!==null)y.return=m,se=y;else e:for(;se!==null;){if(m=se,(m.flags&2048)!==0)switch(m.tag){case 0:case 11:case 15:Si(9,m,m.return)}var M=m.sibling;if(M!==null){M.return=m.return,se=M;break e}se=m.return}}var A=e.current;for(se=A;se!==null;){y=se;var R=y.child;if((y.subtreeFlags&2064)!==0&&R!==null)R.return=y,se=R;else e:for(y=A;se!==null;){if(k=se,(k.flags&2048)!==0)try{switch(k.tag){case 0:case 11:case 15:Ir(9,k)}}catch(oe){Fe(k,k.return,oe)}if(k===y){se=null;break e}var K=k.sibling;if(K!==null){K.return=k.return,se=K;break e}se=k.return}}if(je=d,kn(),Gt&&typeof Gt.onPostCommitFiberRoot=="function")try{Gt.onPostCommitFiberRoot(Xi,e)}catch{}l=!0}return l}finally{Te=a,Et.transition=n}}return!1}function am(e,n,a){n=Ps(a,n),n=Sh(e,n,1),e=Sn(e,n,1),n=ct(),e!==null&&(Qs(e,1,n),gt(e,n))}function Fe(e,n,a){if(e.tag===3)am(e,e,a);else for(;n!==null;){if(n.tag===3){am(n,e,a);break}else if(n.tag===1){var l=n.stateNode;if(typeof n.type.getDerivedStateFromError=="function"||typeof l.componentDidCatch=="function"&&(Cn===null||!Cn.has(l))){e=Ps(a,e),e=Nh(n,e,1),n=Sn(n,e,1),e=ct(),n!==null&&(Qs(n,1,e),gt(n,e));break}}n=n.return}}function lx(e,n,a){var l=e.pingCache;l!==null&&l.delete(n),n=ct(),e.pingedLanes|=e.suspendedLanes&a,Je===e&&(tt&a)===a&&(Ke===4||Ke===3&&(tt&130023424)===tt&&500>Oe()-jl?qn(e,0):kl|=a),gt(e,n)}function om(e,n){n===0&&((e.mode&1)===0?n=1:(n=Qi,Qi<<=1,(Qi&130023424)===0&&(Qi=4194304)));var a=ct();e=an(e,n),e!==null&&(Qs(e,n,a),gt(e,a))}function cx(e){var n=e.memoizedState,a=0;n!==null&&(a=n.retryLane),om(e,a)}function ux(e,n){var a=0;switch(e.tag){case 13:var l=e.stateNode,d=e.memoizedState;d!==null&&(a=d.retryLane);break;case 19:l=e.stateNode;break;default:throw Error(r(314))}l!==null&&l.delete(n),om(e,a)}var lm;lm=function(e,n,a){if(e!==null)if(e.memoizedProps!==n.pendingProps||ht.current)pt=!0;else{if((e.lanes&a)===0&&(n.flags&128)===0)return pt=!1,Qv(e,n,a);pt=(e.flags&131072)!==0}else pt=!1,Le&&(n.flags&1048576)!==0&&zd(n,xr,n.index);switch(n.lanes=0,n.tag){case 2:var l=n.type;Rr(e,n),e=n.pendingProps;var d=ws(n,st.current);Ts(n,a),d=el(null,n,l,e,d,a);var m=tl();return n.flags|=1,typeof d=="object"&&d!==null&&typeof d.render=="function"&&d.$$typeof===void 0?(n.tag=1,n.memoizedState=null,n.updateQueue=null,mt(l)?(m=!0,gr(n)):m=!1,n.memoizedState=d.state!==null&&d.state!==void 0?d.state:null,Ko(n),d.updater=_r,n.stateNode=d,d._reactInternals=n,ol(n,l,e,a),n=dl(null,n,l,!0,m,a)):(n.tag=0,Le&&m&&Vo(n),lt(null,n,d,a),n=n.child),n;case 16:l=n.elementType;e:{switch(Rr(e,n),e=n.pendingProps,d=l._init,l=d(l._payload),n.type=l,d=n.tag=hx(l),e=Vt(l,e),d){case 0:n=ul(null,n,l,e,a);break e;case 1:n=Rh(null,n,l,e,a);break e;case 11:n=Ph(null,n,l,e,a);break e;case 14:n=Eh(null,n,l,Vt(l.type,e),a);break e}throw Error(r(306,l,""))}return n;case 0:return l=n.type,d=n.pendingProps,d=n.elementType===l?d:Vt(l,d),ul(e,n,l,d,a);case 1:return l=n.type,d=n.pendingProps,d=n.elementType===l?d:Vt(l,d),Rh(e,n,l,d,a);case 3:e:{if(Lh(n),e===null)throw Error(r(387));l=n.pendingProps,m=n.memoizedState,d=m.element,Yd(e,n),Nr(n,l,null,a);var y=n.memoizedState;if(l=y.element,m.isDehydrated)if(m={element:l,isDehydrated:!1,cache:y.cache,pendingSuspenseBoundaries:y.pendingSuspenseBoundaries,transitions:y.transitions},n.updateQueue.baseState=m,n.memoizedState=m,n.flags&256){d=Ps(Error(r(423)),n),n=Ih(e,n,l,a,d);break e}else if(l!==d){d=Ps(Error(r(424)),n),n=Ih(e,n,l,a,d);break e}else for(wt=xn(n.stateNode.containerInfo.firstChild),bt=n,Le=!0,It=null,a=qd(n,null,l,a),n.child=a;a;)a.flags=a.flags&-3|4096,a=a.sibling;else{if(Ss(),l===d){n=ln(e,n,a);break e}lt(e,n,l,a)}n=n.child}return n;case 5:return Zd(n),e===null&&Oo(n),l=n.type,d=n.pendingProps,m=e!==null?e.memoizedProps:null,y=d.children,Mo(l,d)?y=null:m!==null&&Mo(l,m)&&(n.flags|=32),Dh(e,n),lt(e,n,y,a),n.child;case 6:return e===null&&Oo(n),null;case 13:return Vh(e,n,a);case 4:return qo(n,n.stateNode.containerInfo),l=n.pendingProps,e===null?n.child=Ns(n,null,l,a):lt(e,n,l,a),n.child;case 11:return l=n.type,d=n.pendingProps,d=n.elementType===l?d:Vt(l,d),Ph(e,n,l,d,a);case 7:return lt(e,n,n.pendingProps,a),n.child;case 8:return lt(e,n,n.pendingProps.children,a),n.child;case 12:return lt(e,n,n.pendingProps.children,a),n.child;case 10:e:{if(l=n.type._context,d=n.pendingProps,m=n.memoizedProps,y=d.value,Me(kr,l._currentValue),l._currentValue=y,m!==null)if(Lt(m.value,y)){if(m.children===d.children&&!ht.current){n=ln(e,n,a);break e}}else for(m=n.child,m!==null&&(m.return=n);m!==null;){var k=m.dependencies;if(k!==null){y=m.child;for(var C=k.firstContext;C!==null;){if(C.context===l){if(m.tag===1){C=on(-1,a&-a),C.tag=2;var F=m.updateQueue;if(F!==null){F=F.shared;var H=F.pending;H===null?C.next=C:(C.next=H.next,H.next=C),F.pending=C}}m.lanes|=a,C=m.alternate,C!==null&&(C.lanes|=a),Ho(m.return,a,n),k.lanes|=a;break}C=C.next}}else if(m.tag===10)y=m.type===n.type?null:m.child;else if(m.tag===18){if(y=m.return,y===null)throw Error(r(341));y.lanes|=a,k=y.alternate,k!==null&&(k.lanes|=a),Ho(y,a,n),y=m.sibling}else y=m.child;if(y!==null)y.return=m;else for(y=m;y!==null;){if(y===n){y=null;break}if(m=y.sibling,m!==null){m.return=y.return,y=m;break}y=y.return}m=y}lt(e,n,d.children,a),n=n.child}return n;case 9:return d=n.type,l=n.pendingProps.children,Ts(n,a),d=At(d),l=l(d),n.flags|=1,lt(e,n,l,a),n.child;case 14:return l=n.type,d=Vt(l,n.pendingProps),d=Vt(l.type,d),Eh(e,n,l,d,a);case 15:return Mh(e,n,n.type,n.pendingProps,a);case 17:return l=n.type,d=n.pendingProps,d=n.elementType===l?d:Vt(l,d),Rr(e,n),n.tag=1,mt(l)?(e=!0,gr(n)):e=!1,Ts(n,a),kh(n,l,d),ol(n,l,d,a),dl(null,n,l,!0,e,a);case 19:return Bh(e,n,a);case 22:return _h(e,n,a)}throw Error(r(156,n.tag))};function cm(e,n){return Uu(e,n)}function dx(e,n,a,l){this.tag=e,this.key=a,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=n,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=l,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function Mt(e,n,a,l){return new dx(e,n,a,l)}function Ml(e){return e=e.prototype,!(!e||!e.isReactComponent)}function hx(e){if(typeof e=="function")return Ml(e)?1:0;if(e!=null){if(e=e.$$typeof,e===he)return 11;if(e===me)return 14}return 2}function En(e,n){var a=e.alternate;return a===null?(a=Mt(e.tag,n,e.key,e.mode),a.elementType=e.elementType,a.type=e.type,a.stateNode=e.stateNode,a.alternate=e,e.alternate=a):(a.pendingProps=n,a.type=e.type,a.flags=0,a.subtreeFlags=0,a.deletions=null),a.flags=e.flags&14680064,a.childLanes=e.childLanes,a.lanes=e.lanes,a.child=e.child,a.memoizedProps=e.memoizedProps,a.memoizedState=e.memoizedState,a.updateQueue=e.updateQueue,n=e.dependencies,a.dependencies=n===null?null:{lanes:n.lanes,firstContext:n.firstContext},a.sibling=e.sibling,a.index=e.index,a.ref=e.ref,a}function Hr(e,n,a,l,d,m){var y=2;if(l=e,typeof e=="function")Ml(e)&&(y=1);else if(typeof e=="string")y=5;else e:switch(e){case I:return Yn(a.children,d,m,n);case U:y=8,d|=8;break;case ce:return e=Mt(12,a,n,d|2),e.elementType=ce,e.lanes=m,e;case Y:return e=Mt(13,a,n,d),e.elementType=Y,e.lanes=m,e;case we:return e=Mt(19,a,n,d),e.elementType=we,e.lanes=m,e;case ee:return Gr(a,d,m,n);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case q:y=10;break e;case ge:y=9;break e;case he:y=11;break e;case me:y=14;break e;case Ce:y=16,l=null;break e}throw Error(r(130,e==null?e:typeof e,""))}return n=Mt(y,a,n,d),n.elementType=e,n.type=l,n.lanes=m,n}function Yn(e,n,a,l){return e=Mt(7,e,l,n),e.lanes=a,e}function Gr(e,n,a,l){return e=Mt(22,e,l,n),e.elementType=ee,e.lanes=a,e.stateNode={isHidden:!1},e}function _l(e,n,a){return e=Mt(6,e,null,n),e.lanes=a,e}function Dl(e,n,a){return n=Mt(4,e.children!==null?e.children:[],e.key,n),n.lanes=a,n.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},n}function mx(e,n,a,l,d){this.tag=n,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=ro(0),this.expirationTimes=ro(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=ro(0),this.identifierPrefix=l,this.onRecoverableError=d,this.mutableSourceEagerHydrationData=null}function Rl(e,n,a,l,d,m,y,k,C){return e=new mx(e,n,a,k,C),n===1?(n=1,m===!0&&(n|=8)):n=0,m=Mt(3,null,null,n),e.current=m,m.stateNode=e,m.memoizedState={element:l,isDehydrated:a,cache:null,transitions:null,pendingSuspenseBoundaries:null},Ko(m),e}function px(e,n,a){var l=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:L,key:l==null?null:""+l,children:e,containerInfo:n,implementation:a}}function um(e){if(!e)return wn;e=e._reactInternals;e:{if(Fn(e)!==e||e.tag!==1)throw Error(r(170));var n=e;do{switch(n.tag){case 3:n=n.stateNode.context;break e;case 1:if(mt(n.type)){n=n.stateNode.__reactInternalMemoizedMergedChildContext;break e}}n=n.return}while(n!==null);throw Error(r(171))}if(e.tag===1){var a=e.type;if(mt(a))return Fd(e,a,n)}return n}function dm(e,n,a,l,d,m,y,k,C){return e=Rl(a,l,!0,e,d,m,y,k,C),e.context=um(null),a=e.current,l=ct(),d=An(a),m=on(l,d),m.callback=n??null,Sn(a,m,d),e.current.lanes=d,Qs(e,d,l),gt(e,l),e}function Kr(e,n,a,l){var d=n.current,m=ct(),y=An(d);return a=um(a),n.context===null?n.context=a:n.pendingContext=a,n=on(m,y),n.payload={element:e},l=l===void 0?null:l,l!==null&&(n.callback=l),e=Sn(d,n,y),e!==null&&(Ot(e,d,y,m),Sr(e,d,y)),y}function qr(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function hm(e,n){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var a=e.retryLane;e.retryLane=a!==0&&a<n?a:n}}function Ll(e,n){hm(e,n),(e=e.alternate)&&hm(e,n)}function fx(){return null}var mm=typeof reportError=="function"?reportError:function(e){console.error(e)};function Il(e){this._internalRoot=e}Xr.prototype.render=Il.prototype.render=function(e){var n=this._internalRoot;if(n===null)throw Error(r(409));Kr(e,n,null,null)},Xr.prototype.unmount=Il.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var n=e.containerInfo;Kn(function(){Kr(null,e,null,null)}),n[tn]=null}};function Xr(e){this._internalRoot=e}Xr.prototype.unstable_scheduleHydration=function(e){if(e){var n=Yu();e={blockedOn:null,target:e,priority:n};for(var a=0;a<gn.length&&n!==0&&n<gn[a].priority;a++);gn.splice(a,0,e),a===0&&Zu(e)}};function Vl(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function Yr(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function pm(){}function gx(e,n,a,l,d){if(d){if(typeof l=="function"){var m=l;l=function(){var F=qr(y);m.call(F)}}var y=dm(n,l,e,0,null,!1,!1,"",pm);return e._reactRootContainer=y,e[tn]=y.current,di(e.nodeType===8?e.parentNode:e),Kn(),y}for(;d=e.lastChild;)e.removeChild(d);if(typeof l=="function"){var k=l;l=function(){var F=qr(C);k.call(F)}}var C=Rl(e,0,!1,null,null,!1,!1,"",pm);return e._reactRootContainer=C,e[tn]=C.current,di(e.nodeType===8?e.parentNode:e),Kn(function(){Kr(n,C,a,l)}),C}function Qr(e,n,a,l,d){var m=a._reactRootContainer;if(m){var y=m;if(typeof d=="function"){var k=d;d=function(){var C=qr(y);k.call(C)}}Kr(n,y,e,d)}else y=gx(a,n,e,d,l);return qr(y)}qu=function(e){switch(e.tag){case 3:var n=e.stateNode;if(n.current.memoizedState.isDehydrated){var a=Ys(n.pendingLanes);a!==0&&(ao(n,a|1),gt(n,Oe()),(je&6)===0&&(_s=Oe()+500,kn()))}break;case 13:Kn(function(){var l=an(e,1);if(l!==null){var d=ct();Ot(l,e,1,d)}}),Ll(e,1)}},oo=function(e){if(e.tag===13){var n=an(e,134217728);if(n!==null){var a=ct();Ot(n,e,134217728,a)}Ll(e,134217728)}},Xu=function(e){if(e.tag===13){var n=An(e),a=an(e,n);if(a!==null){var l=ct();Ot(a,e,n,l)}Ll(e,n)}},Yu=function(){return Te},Qu=function(e,n){var a=Te;try{return Te=e,n()}finally{Te=a}},Za=function(e,n,a){switch(n){case"input":if(Ha(e,a),n=a.name,a.type==="radio"&&n!=null){for(a=e;a.parentNode;)a=a.parentNode;for(a=a.querySelectorAll("input[name="+JSON.stringify(""+n)+'][type="radio"]'),n=0;n<a.length;n++){var l=a[n];if(l!==e&&l.form===e.form){var d=pr(l);if(!d)throw Error(r(90));vt(l),Ha(l,d)}}}break;case"textarea":Cu(e,a);break;case"select":n=a.value,n!=null&&cs(e,!!a.multiple,n,!1)}},Lu=Al,Iu=Kn;var yx={usingClientEntryPoint:!1,Events:[pi,xs,pr,Du,Ru,Al]},Ai={findFiberByHostInstance:Bn,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},vx={bundleType:Ai.bundleType,version:Ai.version,rendererPackageName:Ai.rendererPackageName,rendererConfig:Ai.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:V.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=Ou(e),e===null?null:e.stateNode},findFiberByHostInstance:Ai.findFiberByHostInstance||fx,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Jr=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Jr.isDisabled&&Jr.supportsFiber)try{Xi=Jr.inject(vx),Gt=Jr}catch{}}return yt.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=yx,yt.createPortal=function(e,n){var a=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!Vl(n))throw Error(r(200));return px(e,n,null,a)},yt.createRoot=function(e,n){if(!Vl(e))throw Error(r(299));var a=!1,l="",d=mm;return n!=null&&(n.unstable_strictMode===!0&&(a=!0),n.identifierPrefix!==void 0&&(l=n.identifierPrefix),n.onRecoverableError!==void 0&&(d=n.onRecoverableError)),n=Rl(e,1,!1,null,null,a,!1,l,d),e[tn]=n.current,di(e.nodeType===8?e.parentNode:e),new Il(n)},yt.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var n=e._reactInternals;if(n===void 0)throw typeof e.render=="function"?Error(r(188)):(e=Object.keys(e).join(","),Error(r(268,e)));return e=Ou(n),e=e===null?null:e.stateNode,e},yt.flushSync=function(e){return Kn(e)},yt.hydrate=function(e,n,a){if(!Yr(n))throw Error(r(200));return Qr(null,e,n,!0,a)},yt.hydrateRoot=function(e,n,a){if(!Vl(e))throw Error(r(405));var l=a!=null&&a.hydratedSources||null,d=!1,m="",y=mm;if(a!=null&&(a.unstable_strictMode===!0&&(d=!0),a.identifierPrefix!==void 0&&(m=a.identifierPrefix),a.onRecoverableError!==void 0&&(y=a.onRecoverableError)),n=dm(n,null,e,1,a??null,d,!1,m,y),e[tn]=n.current,di(e),l)for(e=0;e<l.length;e++)a=l[e],d=a._getVersion,d=d(a._source),n.mutableSourceEagerHydrationData==null?n.mutableSourceEagerHydrationData=[a,d]:n.mutableSourceEagerHydrationData.push(a,d);return new Xr(n)},yt.render=function(e,n,a){if(!Yr(n))throw Error(r(200));return Qr(null,e,n,!1,a)},yt.unmountComponentAtNode=function(e){if(!Yr(e))throw Error(r(40));return e._reactRootContainer?(Kn(function(){Qr(null,null,e,!1,function(){e._reactRootContainer=null,e[tn]=null})}),!0):!1},yt.unstable_batchedUpdates=Al,yt.unstable_renderSubtreeIntoContainer=function(e,n,a,l){if(!Yr(a))throw Error(r(200));if(e==null||e._reactInternals===void 0)throw Error(r(38));return Qr(e,n,a,!1,l)},yt.version="18.3.1-next-f1338f8080-20240426",yt}var jm;function Ax(){if(jm)return Ol.exports;jm=1;function t(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(t)}catch(s){console.error(s)}}return t(),Ol.exports=Tx(),Ol.exports}var Sm;function Px(){if(Sm)return Zr;Sm=1;var t=Ax();return Zr.createRoot=t.createRoot,Zr.hydrateRoot=t.hydrateRoot,Zr}var Ex=Px();class Mx extends Error{constructor(r,o){super(r);fm(this,"status");this.status=o}}async function Ae(t,s){const r=await fetch(t,{...s,credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json",...s==null?void 0:s.headers}}),o=await r.json().catch(()=>({}));if(!r.ok)throw new Mx(o.error||r.statusText||"Request failed",r.status);return o}const va=()=>Ae("/auth/status"),_x=()=>Ae("/api/config"),xa=()=>Ae("/api/botstats"),Dx=()=>Ae("/api/team"),Rx=t=>Ae(`/api/team/${t}`),mc=()=>Ae("/api/staff/me"),Lx=(t,s)=>Ae("/api/staff/profile",{method:"POST",headers:s?{"X-CSRF-Token":s}:void 0,body:JSON.stringify(t)}),Ix=(t,s)=>Ae("/api/staff/global-profile",{method:"POST",headers:s?{"X-CSRF-Token":s}:void 0,body:JSON.stringify(t)}),Vx=()=>Ae("/api/commands"),pc=()=>Ae("/api/guilds"),Nm=()=>Ae("/api/me/overview"),Fx=t=>Ae(`/api/guild/${t}/overview`),Bx=t=>Ae(`/api/guild/${t}/levels`),Cm=t=>Ae(`/api/guild/${t}/config`),$l=t=>Ae(`/api/guild/${t}/resources`),Ox=t=>Ae(`/api/guild/${t}/applications`),zx=(t,s,r)=>Ae(`/api/guild/${t}/applications`,{method:"POST",headers:r?{"X-CSRF-Token":r}:void 0,body:JSON.stringify(s)}),Ux=(t,s,r,o)=>Ae(`/api/guild/${t}/applications/${s}`,{method:"PUT",headers:o?{"X-CSRF-Token":o}:void 0,body:JSON.stringify(r)}),$x=(t,s,r,o)=>Ae(`/api/guild/${t}/applications/${s}/status`,{method:"POST",headers:o?{"X-CSRF-Token":o}:void 0,body:JSON.stringify({status:r})}),Wx=(t,s,r)=>Ae(`/api/guild/${t}/applications/${s}`,{method:"DELETE",headers:r?{"X-CSRF-Token":r}:void 0}),Hx=(t,s)=>Ae(`/api/guild/${t}/applications/${s}/submissions`),Gx=(t,s,r,o,c)=>Ae(`/api/guild/${t}/applications/${s}/submissions/${r}/review`,{method:"POST",headers:c?{"X-CSRF-Token":c}:void 0,body:JSON.stringify({status:o})}),Kx=t=>Ae(`/api/applications/${t}`),qx=(t,s)=>Ae(`/api/applications/${t}/${s}`),Xx=(t,s,r,o)=>Ae(`/api/applications/${t}/${s}/submit`,{method:"POST",headers:o?{"X-CSRF-Token":o}:void 0,body:JSON.stringify({answers:r})});function Ia(t,s,r,o){return Ae(`/api/guild/${t}/config/${s}`,{method:"POST",headers:o?{"X-CSRF-Token":o}:void 0,body:JSON.stringify(r)})}function Yx(t,s,r){return Ae(`/api/guild/${t}/config/profile`,{method:"POST",headers:r?{"X-CSRF-Token":r}:void 0,body:JSON.stringify(s)})}function rf(t){return t.replace(/\/+$/,"")||"/"}function Tm(t=window.location.pathname){const s=rf(t);return s==="/commands"?"commands":s==="/docs"?"docs":s.startsWith("/docs/")?"docs-detail":s==="/dashboard/staff"||s==="/dashboard/staff/"?"staff":s.startsWith("/apply/")?"application":s==="/dashboard"||s.startsWith("/dashboard/")?"dashboard":s==="/team"?"team":s==="/support"?"support":s==="/discord"?"discord":s.startsWith("/team/")?"team-member":s==="/privacy"?"privacy":s==="/terms"?"terms":s==="/community"?"community":s==="/donate"||s.startsWith("/donate")?"donate":s==="/transcript"||s.startsWith("/transcript/")?"transcript":s==="/changelog"?"changelog":s.startsWith("/changelog/")?"changelog-detail":"home"}function Rs(t,s="overview"){return t?`/dashboard/${t}/${s}`:"/dashboard"}function fc(){return"/dashboard/servers"}function Am(){const t=rf(window.location.pathname).split("/").filter(Boolean),s=["overview","leveling","moderation","server","applications","ai","customization"];return t[1]==="servers"?{view:"servers",guildId:null,section:"overview"}:!t[1]||t[1]==="staff"?{view:"overview",guildId:null,section:"overview"}:{view:"guild",guildId:t[1]||null,section:s.includes(t[2])?t[2]:"overview"}}function be(t){t.startsWith("/")&&(window.history.pushState({},"",t),window.dispatchEvent(new PopStateEvent("popstate")),window.scrollTo({top:0,behavior:"smooth"}))}let Pm=null,Wl=null;function Ln(){const[t,s]=T.useState(Pm);return T.useEffect(()=>{Wl||(Wl=_x().then(r=>Pm=r)),Wl.then(s).catch(()=>{})},[]),t}function af({onNavigate:t}){const s=Ln();return i.jsxs("a",{className:"brand",href:"/",onClick:r=>{r.preventDefault(),t?t():be("/")},children:[i.jsx("span",{className:"brand-mark",children:s!=null&&s.bot_avatar_url?i.jsx("img",{src:s.bot_avatar_url,alt:"Niko"}):"n"}),i.jsx("span",{children:"niko"})]})}function Nt(){return i.jsxs("footer",{className:"site-footer",children:[i.jsx(af,{}),i.jsx("span",{children:"Built for communities that care."}),i.jsxs("div",{children:[i.jsx("a",{href:"/privacy",onClick:t=>{t.preventDefault(),be("/privacy")},children:"Privacy"}),i.jsx("a",{href:"/terms",onClick:t=>{t.preventDefault(),be("/terms")},children:"Terms"}),i.jsx("a",{href:"/community",onClick:t=>{t.preventDefault(),be("/community")},children:"Community Policy"}),i.jsx("a",{href:"/support",onClick:t=>{t.preventDefault(),be("/support")},children:"Support"})]})]})}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Qx=t=>t==null?void 0:t.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase();/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */function Jx(t,s,r=[]){if(s==null)throw new Error("[lucide]: iconNode is required when icon name is used");return{name:Qx(t),size:24,node:s,...r.length>0?{aliases:r}:{}}}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Zx=t=>{let s="",r=!1;for(const o of t){if(o==="-"||o==="_"||o<=" "){r=s.length>0;continue}s.length===0?s+=o.toLowerCase():s+=r?o.toUpperCase():o,r=!1}return s};/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const eb=t=>{const s=Zx(t);return s.charAt(0).toUpperCase()+s.slice(1)};/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const gc=(...t)=>t.filter((s,r,o)=>!!s&&s.trim()!==""&&o.indexOf(s)===r).join(" ").trim();/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Qn={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor","stroke-width":2,"stroke-linecap":"round","stroke-linejoin":"round"};/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */function Hl(t){return t!=null}function tb(t,s={}){var b,j;const r=s.attributeNames??{},o=N=>r[N]??N,c=t.size??t.width??Qn.width,u=t.size??t.height??Qn.height,h=((b=t.aliases)==null?void 0:b.filter(N=>typeof N=="string"&&N.trim()!=="").map(N=>`lucide-${N}`))??[],p=[...t.name?[`lucide-${t.name}`]:[],...h],f=((j=s.className)==null?void 0:j.split(" ").filter(Boolean))??[],v=s.includeDefaultClasses===!1?gc(...f):gc("lucide",...p,...f),g=s.absoluteStrokeWidth?Number(s.strokeWidth??Qn["stroke-width"])*Number(t.size??t.width??Qn.width)/Number(s.size??s.width??Qn.width):s.strokeWidth??Qn["stroke-width"];return["svg",{...Object.entries(Qn).reduce((N,[w,S])=>(N[o(w)]=S,N),{}),..."color"in s&&s.color&&{[o("stroke")]:s.color},..."size"in s&&Hl(s.size)&&{[o("width")]:s.size,[o("height")]:s.size},..."width"in s&&Hl(s.width)&&{[o("width")]:s.width},..."height"in s&&Hl(s.height)&&{[o("height")]:s.height},[o("stroke-width")]:g,...v&&{[o("class")]:v},[o("viewBox")]:`0 0 ${c} ${u}`,...s.hasA11yProp===!1?{[o("aria-hidden")]:"true"}:{},..."attributes"in s&&s.attributes},t.node.map(N=>{const[w,S,B]=N,P=s.nonScalingStroke?{[o("vector-effect")]:"non-scaling-stroke",...S}:S;return B?[w,P,B]:[w,P]})]}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */function nb(t,s={}){return tb(t,{...s,attributeNames:{...s.attributeNames,class:"className","stroke-width":"strokeWidth","stroke-linecap":"strokeLinecap","stroke-linejoin":"strokeLinejoin","vector-effect":"vectorEffect"}})}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const sb=t=>{for(const s in t)if(s.startsWith("aria-")||s==="role"||s==="title")return!0;return!1},ib=T.createContext({}),rb=()=>T.useContext(ib),ab=T.forwardRef(({color:t,size:s,width:r,height:o,strokeWidth:c,absoluteStrokeWidth:u,nonScalingStroke:h,className:p="",children:f,iconNode:v=[],icon:g={node:v,aliases:[],size:24},...x},b)=>{const{size:j=24,strokeWidth:N=2,absoluteStrokeWidth:w=!1,nonScalingStroke:S=!1,color:B="currentColor",className:P=""}=rb()??{},D=!!f||sb(x),[V,_,L=[]]=nb(g,{color:t??B,width:r??s??j,height:o??s??j,strokeWidth:c??N,absoluteStrokeWidth:u??w,nonScalingStroke:h??S,className:gc(P,p),hasA11yProp:D,attributes:x});return T.createElement(V,{ref:b,..._},[...L.map(([I,U])=>T.createElement(I,U)),...Array.isArray(f)?f:[f]])});/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */function $e(t,s=[],r=[]){const o=typeof t=="string"?Jx(t,s,r):t,c=T.forwardRef(({className:u,...h},p)=>T.createElement(ab,{ref:p,icon:o,className:u,...h}));return o.name&&(c.displayName=eb(o.name)),c}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const of={name:"activity",size:24,node:[["path",{d:"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2",key:"169zse"}]]};of.node;const ob=$e(of);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const lf={name:"arrow-right",size:24,node:[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]]};lf.node;const lb=$e(lf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const cf={name:"book-open",size:24,node:[["path",{d:"M12 5v16",key:"1f6ucr"}],["path",{d:"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z",key:"1fyvmf"}]]};cf.node;const Em=$e(cf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const uf={name:"chart-column",size:24,node:[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],aliases:["bar-chart-3"]};uf.node;const ca=$e(uf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const df={name:"external-link",size:24,node:[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]]};df.node;const cb=$e(df);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const hf={name:"hash",size:24,node:[["line",{x1:"4",x2:"20",y1:"9",y2:"9",key:"4lhtct"}],["line",{x1:"4",x2:"20",y1:"15",y2:"15",key:"vyu0kd"}],["line",{x1:"10",x2:"8",y1:"3",y2:"21",key:"1ggp8o"}],["line",{x1:"16",x2:"14",y1:"3",y2:"21",key:"weycgp"}]]};hf.node;const ub=$e(hf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const mf={name:"layout-grid",size:24,node:[["rect",{width:"7",height:"7",x:"3",y:"3",rx:"1",key:"1g98yp"}],["rect",{width:"7",height:"7",x:"14",y:"3",rx:"1",key:"6d4xhi"}],["rect",{width:"7",height:"7",x:"14",y:"14",rx:"1",key:"nxv5o0"}],["rect",{width:"7",height:"7",x:"3",y:"14",rx:"1",key:"1bb6yr"}]]};mf.node;const yc=$e(mf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const pf={name:"link-2",size:24,node:[["path",{d:"M9 17H7A5 5 0 0 1 7 7h2",key:"8i5ue5"}],["path",{d:"M15 7h2a5 5 0 1 1 0 10h-2",key:"1b9ql8"}],["line",{x1:"8",x2:"16",y1:"12",y2:"12",key:"1jonct"}]]};pf.node;const db=$e(pf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ff={name:"lock-keyhole",size:24,node:[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]]};ff.node;const hb=$e(ff);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const gf={name:"log-out",size:24,node:[["path",{d:"m16 17 5-5-5-5",key:"1bji2h"}],["path",{d:"M21 12H9",key:"dn1m92"}],["path",{d:"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4",key:"1uf3rs"}]]};gf.node;const mb=$e(gf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const yf={name:"menu",size:24,node:[["path",{d:"M4 5h16",key:"1tepv9"}],["path",{d:"M4 12h16",key:"1lakjw"}],["path",{d:"M4 19h16",key:"1djgab"}]]};yf.node;const pb=$e(yf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const vf={name:"message-circle",size:24,node:[["path",{d:"M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719",key:"1sd12s"}]]};vf.node;const fb=$e(vf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const xf={name:"minus",size:24,node:[["path",{d:"M5 12h14",key:"1ays0h"}]]};xf.node;const gb=$e(xf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const bf={name:"plus",size:24,node:[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"M12 5v14",key:"s699le"}]]};bf.node;const yb=$e(bf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const wf={name:"search",size:24,node:[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]]};wf.node;const vb=$e(wf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kf={name:"settings",size:24,node:[["path",{d:"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915",key:"1i5ecw"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]]};kf.node;const ea=$e(kf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jf={name:"shield",size:24,node:[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}]]};jf.node;const Gl=$e(jf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Sf={name:"sparkles",size:24,node:[["path",{d:"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",key:"1s2grr"}],["path",{d:"M20 2v4",key:"1rf3ol"}],["path",{d:"M22 4h-4",key:"gwowj6"}],["circle",{cx:"4",cy:"20",r:"2",key:"6kqj1y"}]],aliases:["stars"]};Sf.node;const ta=$e(Sf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Nf={name:"terminal",size:24,node:[["path",{d:"M12 19h8",key:"baeox8"}],["path",{d:"m4 17 6-6-6-6",key:"1yngyt"}]]};Nf.node;const xb=$e(Nf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Cf={name:"users",size:24,node:[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["path",{d:"M16 3.128a4 4 0 0 1 0 7.744",key:"16gr8j"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}]]};Cf.node;const vc=$e(Cf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Tf={name:"x",size:24,node:[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]]};Tf.node;const bb=$e(Tf),wb={arrow:lb,grid:yc,terminal:xb,chart:ca,shield:Gl,spark:ta,users:vc,link:db,settings:ea,book:Em,external:cb,menu:pb,message:fb,close:bb,minus:gb,plus:yb,lock:hb,logout:mb,search:vb,doc:Em,utility:ea,icon_home:yc,icon_settings:ea,icon_economy:ca,icon_leveling:ca,icon_moderation:Gl,icon_automod:Gl,icon_heart:ta,icon_utility:ea,icon_bot:vc,icon_ai:ta,icon_lightbulb:ta};function J({name:t,size:s,className:r=""}){const o=wb[t]||yc;return i.jsx(o,{className:`icon ${r}`.trim(),"aria-hidden":"true",focusable:"false",strokeWidth:1.8,style:s?{width:s,height:s}:void 0})}const Mm=[{label:"Home",path:"/",page:"home"},{label:"Commands",path:"/commands",page:"commands"},{label:"Docs",path:"/docs",page:"docs"},{label:"Team",path:"/team",page:"team"},{label:"Changelog",path:"/changelog",page:"changelog"}];function Ue({page:t}){const s=Ln(),r=t==="dashboard",[o,c]=T.useState(!1),u=h=>p=>{p.preventDefault(),c(!1),be(h)};return i.jsxs("header",{className:`site-header${r?" dashboard-header":""}`,children:[i.jsx(af,{onNavigate:()=>c(!1)}),!r&&i.jsx("nav",{className:"site-nav","aria-label":"Main navigation",children:Mm.map(h=>i.jsx("a",{className:t===h.page?"active":"","aria-current":t===h.page?"page":void 0,href:h.path,onClick:u(h.path),children:h.label},h.path))}),i.jsx("div",{className:"header-actions",children:r?i.jsxs("div",{className:"dashboard-menu",children:[i.jsxs("button",{className:"button button-small button-muted dashboard-menu-trigger",type:"button","aria-expanded":o,"aria-controls":"dashboard-navigation-menu",onClick:()=>c(h=>!h),children:[i.jsx(J,{name:o?"close":"menu"}),i.jsx("span",{children:"Menu"})]}),o&&i.jsxs("nav",{id:"dashboard-navigation-menu",className:"dashboard-menu-popover","aria-label":"Dashboard navigation",children:[i.jsx("span",{className:"dashboard-menu-label",children:"Navigate"}),Mm.map(h=>i.jsx("a",{href:h.path,onClick:u(h.path),children:h.label},h.path)),i.jsx("a",{className:"dashboard-menu-current",href:"/dashboard","aria-current":"page",onClick:u("/dashboard"),children:"Dashboard"})]})]}):i.jsxs(i.Fragment,{children:[i.jsxs("a",{className:"button button-small button-muted dashboard-link",href:"/dashboard",onClick:u("/dashboard"),children:["Dashboard ",i.jsx(J,{name:"arrow"})]}),i.jsx("a",{className:"button button-small button-primary",href:(s==null?void 0:s.invite_url)||"#",target:"_blank",rel:"noreferrer",children:"Add to Discord"})]})})]})}const _m=typeof navigator<"u"?(navigator.language||"en").slice(0,2):"en";function xc(t){const s=t.description;if(typeof s=="string")return s;if(s&&typeof s=="object"){const r=s;if(r[_m])return r[_m];if(r.en)return r.en;const o=Object.values(r).find(c=>typeof c=="string"&&c.length>0);if(o)return o}return"A Niko command for your server."}const kb=[{value:"all",label:"All commands"},{value:"slash",label:"Slash"},{value:"prefix",label:"Prefix"},{value:"hybrid",label:"Hybrid"},{value:"context",label:"Context menus"}],ba={slash:"Slash command",prefix:"Prefix command",hybrid:"Hybrid command",context:"Context menu"};function ts(t){return t.type&&t.type in ba?t.type:"slash"}function jb(t){return t.context_type==="user"?"Right-click a user":"Right-click a message"}function Af(t){const s=ts(t);return s==="slash"?i.jsxs("code",{children:["/",t.name]}):s==="prefix"?i.jsxs("code",{children:[".",t.name]}):s==="hybrid"?i.jsxs(i.Fragment,{children:[i.jsxs("code",{children:["/",t.name]}),i.jsx("span",{className:"command-or",children:"or"}),i.jsxs("code",{children:[".",t.name]})]}):i.jsxs("code",{className:"context-invocation",children:[jb(t)," · ",t.name]})}function Dm(t){return t!=null&&t.length?t:["Not specified"]}function Sb({command:t,onClose:s}){T.useEffect(()=>{const h=p=>{p.key==="Escape"&&s()};return document.addEventListener("keydown",h),()=>document.removeEventListener("keydown",h)},[s]);const r=t.parameters||[],o=t.subcommands||[],c=Dm(t.aliases),u=Dm(t.permissions);return i.jsx("div",{className:"command-dialog-backdrop",role:"presentation",onMouseDown:h=>{h.currentTarget===h.target&&s()},children:i.jsxs("section",{className:"command-dialog",role:"dialog","aria-modal":"true","aria-labelledby":"command-dialog-title",children:[i.jsxs("header",{className:"command-dialog-header",children:[i.jsxs("div",{children:[i.jsxs("div",{className:"command-dialog-kicker",children:[t.category," · ",ba[ts(t)]]}),i.jsx("h2",{id:"command-dialog-title",children:Af(t)})]}),i.jsx("button",{className:"dialog-close",type:"button",onClick:s,"aria-label":"Close command details",title:"Close command details",children:i.jsx(J,{name:"close"})})]}),i.jsxs("div",{className:"command-dialog-body",children:[i.jsx("p",{className:"command-dialog-description",children:xc(t)}),i.jsxs("div",{className:"command-detail-grid",children:[i.jsxs("section",{className:"command-detail-section command-detail-wide",children:[i.jsx("h3",{children:"Usage"}),i.jsx("code",{className:"command-usage",children:t.usage||`${ts(t)==="context"?t.name:`/${t.name}`}`})]}),i.jsxs("section",{className:"command-detail-section",children:[i.jsx("h3",{children:"Permissions"}),i.jsx("ul",{className:"command-detail-list",children:u.map(h=>i.jsx("li",{children:h},h))})]}),i.jsxs("section",{className:"command-detail-section",children:[i.jsx("h3",{children:"Aliases"}),i.jsx("ul",{className:"command-detail-list",children:c.map(h=>i.jsx("li",{children:i.jsx("code",{children:h==="Not specified"?h:`.${h}`})},h))})]})]}),!!r.length&&i.jsxs("section",{className:"command-detail-section command-parameters",children:[i.jsx("h3",{children:"Parameters"}),i.jsx("div",{className:"command-parameter-list",children:r.map(h=>i.jsxs("div",{className:"command-parameter",children:[i.jsxs("div",{className:"command-parameter-title",children:[i.jsx("code",{children:h.name}),i.jsxs("span",{children:[h.required?"Required":"Optional"," · ",h.type]})]}),i.jsx("p",{children:h.description||"No description provided."})]},h.name))})]}),!!o.length&&i.jsxs("section",{className:"command-detail-section",children:[i.jsx("h3",{children:"Subcommands"}),i.jsx("div",{className:"subcommand-list",children:o.map(h=>i.jsxs("code",{children:[t.name," ",h]},h))})]})]}),i.jsxs("footer",{className:"command-dialog-footer",children:[i.jsx("span",{children:"Command registry details are generated from the live bot."}),i.jsx("button",{className:"button button-primary button-small",type:"button",onClick:s,children:"Done"})]})]})})}function Nb(){const[t,s]=T.useState([]),[r,o]=T.useState(null),[c,u]=T.useState(""),[h,p]=T.useState("all"),[f,v]=T.useState("all"),[g,x]=T.useState(!0),[b,j]=T.useState("");T.useEffect(()=>{Vx().then(s).catch(()=>j("The command registry is unavailable right now.")).finally(()=>x(!1))},[]),T.useEffect(()=>{if(!r)return;const S=document.body.style.overflow;return document.body.style.overflow="hidden",()=>{document.body.style.overflow=S}},[r]);const N=T.useMemo(()=>["all",...Array.from(new Set(t.map(S=>S.category))).sort()],[t]),w=t.filter(S=>{const B=`${S.name} ${xc(S)} ${S.category} ${ba[ts(S)]} ${S.context_type||""} ${(S.aliases||[]).join(" ")}`.toLowerCase();return(f==="all"||ts(S)===f)&&(h==="all"||S.category===h)&&B.includes(c.trim().toLowerCase())});return i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"commands"}),i.jsxs("main",{className:"shell page-main",children:[i.jsxs("div",{className:"page-heading",children:[i.jsx("div",{className:"eyebrow",children:"Reference library"}),i.jsxs("h1",{children:["Everything Niko",i.jsx("br",{}),i.jsx("em",{children:"knows how to do."})]}),i.jsx("p",{children:"Browse slash, prefix, hybrid, and context commands from the live bot registry. Select any command for permissions, aliases, parameters, usage, and subcommands."})]}),i.jsxs("div",{className:"command-toolbar",children:[i.jsxs("label",{className:"search-field",children:[i.jsx("span",{"aria-hidden":"true",children:"⌕"}),i.jsx("input",{value:c,onChange:S=>u(S.target.value),placeholder:"Search commands","aria-label":"Search commands"})]}),i.jsxs("div",{className:"command-filters",children:[i.jsx("div",{className:"filter-list","aria-label":"Command types",children:kb.map(S=>i.jsx("button",{type:"button",className:f===S.value?"filter active":"filter","aria-pressed":f===S.value,onClick:()=>v(S.value),children:S.label},S.value))}),i.jsx("div",{className:"filter-list","aria-label":"Command categories",children:N.map(S=>i.jsx("button",{type:"button",className:h===S?"filter active":"filter","aria-pressed":h===S,onClick:()=>p(S),children:S==="all"?"All categories":S},S))})]})]}),i.jsxs("div",{className:"command-meta",children:[i.jsx("strong",{children:g?"…":w.length})," commands ",i.jsx("span",{children:"·"})," live bot registry ",i.jsx("span",{children:"·"})," select a card for details"]}),b&&i.jsxs("div",{className:"inline-error",role:"alert",children:[i.jsx("strong",{children:"Could not load commands"}),i.jsx("span",{children:b})]}),i.jsxs("div",{className:"commands-grid",children:[w.map(S=>i.jsxs("button",{className:"command-card",type:"button",onClick:()=>o(S),"aria-label":`View details for ${S.name}`,children:[i.jsxs("span",{className:"command-card-head",children:[i.jsx("span",{className:"command-name",children:Af(S)}),i.jsx("span",{className:"command-type",children:ba[ts(S)]})]}),i.jsx("span",{className:"command-card-description",children:xc(S)}),i.jsxs("span",{className:"command-card-footer",children:[i.jsx("span",{className:"category-tag",children:S.category}),i.jsxs("span",{className:"command-expand",children:[i.jsx("span",{children:"Details"}),i.jsx(J,{name:"arrow",size:14})]})]})]},`${ts(S)}-${S.context_type||""}-${S.category}-${S.name}`)),!g&&!b&&!w.length&&i.jsx("div",{className:"empty-state",children:"No commands match that search."})]})]}),i.jsx(Nt,{}),r&&i.jsx(Sb,{command:r,onClose:()=>o(null)})]})}function Ne(t){return t==null?"—":new Intl.NumberFormat("en-US",{notation:t>9999?"compact":"standard"}).format(t)}function Pf(t){return(t==null?void 0:t.global_name)||(t==null?void 0:t.username)||"there"}function Ef(t){return t.split(/\s+/).map(s=>s[0]).join("").slice(0,2).toUpperCase()}function Gc({guild:t,className:s="guild-avatar"}){return i.jsx("span",{className:s,"aria-hidden":"true",children:t.icon_url?i.jsx("img",{src:t.icon_url,alt:""}):t.name.slice(0,1).toUpperCase()})}function Mf({user:t,className:s="avatar"}){const r=t.avatar?`https://cdn.discordapp.com/avatars/${t.id}/${t.avatar}.${t.avatar.startsWith("a_")?"gif":"png"}?size=64`:null;return i.jsx("span",{className:s,"aria-hidden":"true",children:r?i.jsx("img",{src:r,alt:""}):Ef(t.global_name||t.username||"Niko")})}function Cb({name:t,avatarUrl:s,className:r="member-avatar"}){return i.jsx("span",{className:r,"aria-hidden":"true",children:s?i.jsx("img",{src:s,alt:""}):Ef(t)})}const Tb=[["overview","Overview","grid","At a glance"],["leveling","Leveling","spark","Reward participation"],["moderation","Moderation","shield","Keep things steady"],["server","Server","settings","Manage server features"],["applications","Applications","users","Staff role openings"],["ai","AI controls","settings","Shape Niko’s voice"],["customization","Customization","paint","Niko’s server identity"]];function _f({user:t,guilds:s,selectedGuild:r,view:o,section:c,stats:u,onHome:h,onServers:p,onGuildChange:f,onSectionChange:v,onRefresh:g,refreshing:x,staffRole:b,children:j}){const N=s.filter(P=>P.installed!==!1),w=(P=!1)=>i.jsx("nav",{className:P?"dash-nav dash-nav-mobile":"dash-nav","aria-label":"Server settings",children:Tb.map(([D,V,_])=>i.jsxs("button",{className:o==="guild"&&c===D?"active":"","aria-current":o==="guild"&&c===D?"page":void 0,onClick:()=>v(D),children:[i.jsx(J,{name:_}),i.jsx("span",{children:V})]},D))}),S=(P=!1)=>i.jsxs("nav",{className:P?"dash-nav dash-primary-nav dash-nav-mobile":"dash-nav dash-primary-nav","aria-label":"Dashboard",children:[i.jsxs("button",{className:o==="overview"?"active":"","aria-current":o==="overview"?"page":void 0,onClick:h,children:[i.jsx(J,{name:"grid"}),i.jsx("span",{children:"My overview"})]}),i.jsxs("button",{className:o==="servers"?"active":"","aria-current":o==="servers"?"page":void 0,onClick:p,children:[i.jsx(J,{name:"users"}),i.jsx("span",{children:"My servers"})]}),b&&i.jsxs("button",{onClick:()=>be("/dashboard/staff"),children:[i.jsx(J,{name:"shield"}),i.jsx("span",{children:"Staff workspace"})]})]}),B=()=>i.jsxs("div",{className:"dash-top-actions",children:[o==="guild"?i.jsxs("label",{className:"guild-switcher",children:[i.jsx("span",{className:"sr-only",children:"Switch server"}),i.jsxs("select",{value:(r==null?void 0:r.id)||"",onChange:P=>{const D=N.find(V=>V.id===P.target.value);D&&f(D)},children:[i.jsx("option",{value:"",disabled:!0,children:"Switch server"}),N.map(P=>i.jsx("option",{value:P.id,children:P.name},P.id))]})]}):i.jsxs("button",{className:"button button-muted button-small top-action",onClick:p,children:[i.jsx(J,{name:"users"})," Browse servers"]}),i.jsxs("button",{className:"button button-muted button-small top-action refresh-action",onClick:g,disabled:x,"aria-label":"Refresh dashboard data",children:[i.jsx(J,{name:"spark"})," ",x?"Refreshing…":"Refresh data"]}),o==="guild"&&i.jsxs("span",{className:"connection-chip",children:[i.jsx("span",{className:"status-dot"})," Connected"]}),i.jsxs("div",{className:"user-pill",children:[i.jsx(Mf,{user:t}),i.jsx("span",{children:Pf(t)})]}),i.jsx("a",{className:"logout-button",href:"/auth/logout","aria-label":"Log out",title:"Log out",children:i.jsx(J,{name:"logout"})})]});return i.jsxs("div",{className:"dashboard-layout",children:[i.jsxs("aside",{className:"dash-sidebar",children:[i.jsx("div",{className:"dash-mobile-controls",children:B()}),i.jsxs("div",{className:"side-rail-heading",children:[i.jsx("span",{className:"side-label",children:"Workspace"}),i.jsxs("span",{className:"rail-status",children:[i.jsx("span",{className:"status-dot"})," Live"]})]}),S(),o==="guild"&&r&&i.jsxs(i.Fragment,{children:[i.jsx("div",{className:"side-label side-label-settings",children:"Current server"}),i.jsxs("div",{className:"side-guild",children:[i.jsx(Gc,{guild:r}),i.jsxs("span",{children:[i.jsx("strong",{children:r.name}),i.jsx("small",{children:"Live configuration"})]}),i.jsx("span",{className:"guild-presence",title:"Niko is connected",children:i.jsx("span",{className:"status-dot"})})]}),i.jsxs("div",{className:"side-settings-caption",children:[i.jsx("span",{children:"Settings map"}),i.jsx("small",{children:"Pick a room to tune"})]}),w()]}),i.jsxs("div",{className:"sidebar-bottom",children:[i.jsxs("span",{className:"online-label",children:[i.jsx("span",{className:"status-dot"})," Niko is online"]}),i.jsxs("small",{children:[Ne(u==null?void 0:u.guild_count)," connected servers · v",(u==null?void 0:u.version)||"1.0"]}),i.jsxs("a",{href:"/",onClick:P=>{P.preventDefault(),be("/")},children:["Back to public site ",i.jsx(J,{name:"arrow"})]})]})]}),i.jsxs("div",{className:"dash-content",children:[i.jsx(Ue,{page:"dashboard"}),i.jsx("div",{className:"dash-contextbar",children:B()}),i.jsx("div",{className:"mobile-primary-bar",children:S(!0)}),o==="guild"&&i.jsx("div",{className:"mobile-section-bar",children:w(!0)}),i.jsx("main",{className:"dash-main",children:j})]})]})}const Df=T.createContext({});function Ab(t){const s=T.useRef(null);return s.current===null&&(s.current=t()),s.current}const Pb=typeof window<"u",Eb=Pb?T.useLayoutEffect:T.useEffect,Kc=T.createContext(null);function qc(t,s){t.indexOf(s)===-1&&t.push(s)}function wa(t,s){const r=t.indexOf(s);r>-1&&t.splice(r,1)}const Wt=(t,s,r)=>r>s?s:r<t?t:r;let Va=()=>{};const dn={},Xc=t=>/^-?(?:\d+(?:\.\d+)?|\.\d+)$/u.test(t),Rf=t=>typeof t=="object"&&t!==null,Yc=t=>/^0[^.\s]+$/u.test(t);function Lf(t){let s;return()=>(s===void 0&&(s=t()),s)}const $t=t=>t,Oi=(...t)=>t.reduce((s,r)=>o=>r(s(o))),Li=(t,s,r)=>{const o=s-t;return o?(r-t)/o:1};class ka{constructor(){this.subscriptions=[]}add(s){return qc(this.subscriptions,s),()=>this.remove(s)}remove(s){wa(this.subscriptions,s)}notify(s,r,o){const c=this.subscriptions.length;if(c)if(c===1)this.subscriptions[0](s,r,o);else for(let u=0;u<c;u++){const h=this.subscriptions[u];h&&h(s,r,o)}}getSize(){return this.subscriptions.length}clear(){this.subscriptions.length=0}}const Dt=t=>t*1e3,jt=t=>t/1e3,If=(t,s)=>s?t*(1e3/s):0,Vf=(t,s,r)=>(((1-3*r+3*s)*t+(3*r-6*s))*t+3*s)*t,Mb=1e-7,_b=12;function Db(t,s,r,o,c){let u,h,p=0;do h=s+(r-s)/2,u=Vf(h,o,c)-t,u>0?r=h:s=h;while(Math.abs(u)>Mb&&++p<_b);return h}function zi(t,s,r,o){if(t===s&&r===o)return $t;const c=u=>Db(u,0,1,t,r);return u=>u===0||u===1?u:Vf(c(u),s,o)}const Ff=t=>s=>s<=.5?t(2*s)/2:(2-t(2*(1-s)))/2,Bf=t=>s=>1-t(1-s),Of=zi(.33,1.53,.69,.99),Qc=Bf(Of),zf=Ff(Qc),Uf=t=>t>=1?1:(t*=2)<1?.5*Qc(t):.5*(2-Math.pow(2,-10*(t-1))),Jc=t=>1-Math.sin(Math.acos(t)),$f=Bf(Jc),Wf=Ff(Jc),Rb=zi(.42,0,1,1),Lb=zi(0,0,.58,1),Hf=zi(.42,0,.58,1),Ib=t=>Array.isArray(t)&&typeof t[0]!="number",Gf=t=>Array.isArray(t)&&typeof t[0]=="number",Vb={linear:$t,easeIn:Rb,easeInOut:Hf,easeOut:Lb,circIn:Jc,circInOut:Wf,circOut:$f,backIn:Qc,backInOut:zf,backOut:Of,anticipate:Uf},Fb=t=>typeof t=="string",Rm=t=>{if(Gf(t)){Va(t.length===4);const[s,r,o,c]=t;return zi(s,r,o,c)}else if(Fb(t))return Vb[t];return t},na=["setup","read","resolveKeyframes","preUpdate","update","preRender","render","postRender"];function Bb(t){let s=new Set,r=new Set,o=!1,c=!1;const u=new Set;let h={delta:0,timestamp:0,isProcessing:!1};function p(v){u.has(v)&&(r.add(v),t()),v(h)}const f={schedule:(v,g=!1,x=!1)=>{const j=x&&o?s:r;return g&&u.add(v),j.add(v),v},cancel:v=>{r.delete(v),u.delete(v)},process:v=>{if(h=v,o){c=!0;return}o=!0;const g=s;s=r,r=g,s.forEach(p),s.clear(),o=!1,c&&(c=!1,f.process(v))}};return f}const Ob=40;function Kf(t,s){let r=!1,o=!0;const c={delta:0,timestamp:0,isProcessing:!1},u=()=>r=!0,h=na.reduce((D,V)=>(D[V]=Bb(u),D),{}),{setup:p,read:f,resolveKeyframes:v,preUpdate:g,update:x,preRender:b,render:j,postRender:N}=h,w=()=>{const D=dn.useManualTiming,V=D?c.timestamp:performance.now();r=!1,D||(c.delta=o?1e3/60:Math.max(Math.min(V-c.timestamp,Ob),1)),c.timestamp=V,c.isProcessing=!0,p.process(c),f.process(c),v.process(c),g.process(c),x.process(c),b.process(c),j.process(c),N.process(c),c.isProcessing=!1,r&&s&&(o=!1,t(w))},S=()=>{r=!0,o=!0,c.isProcessing||t(w)};return{schedule:na.reduce((D,V)=>{const _=h[V];return D[V]=(L,I=!1,U=!1)=>(r||S(),_.schedule(L,I,U)),D},{}),cancel:D=>{for(let V=0;V<na.length;V++)h[na[V]].cancel(D)},state:c,steps:h}}const{schedule:Ee,cancel:Rn,state:Xe,steps:Kl}=Kf(typeof requestAnimationFrame<"u"?requestAnimationFrame:$t,!0);let ua;function zb(){ua=void 0}const ot={now:()=>(ua===void 0&&ot.set(Xe.isProcessing||dn.useManualTiming?Xe.timestamp:performance.now()),ua),set:t=>{ua=t,queueMicrotask(zb)}},Bs=t=>Math.round(t*1e5)/1e5,qf=t=>s=>typeof s=="string"&&s.startsWith(t),Xf=qf("--"),Ub=qf("var(--"),Zc=t=>Ub(t)?$b.test(t.split("/*")[0].trim()):!1,$b=/var\(--(?:[\w-]+\s*|[\w-]+\s*,(?:\s*[^)(\s]|\s*\((?:[^)(]|\([^)(]*\))*\))+\s*)\)$/iu;function Lm(t){return typeof t!="string"?!1:t.split("/*")[0].includes("var(--")}const zs={test:t=>typeof t=="number",parse:parseFloat,transform:t=>t},Ii={...zs,transform:t=>Wt(0,1,t)},sa={...zs,default:1},eu=/-?(?:\d+(?:\.\d+)?|\.\d+)/gu;function Wb(t){return t==null}const Hb=/^(?:#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\))$/iu,tu=(t,s)=>r=>!!(typeof r=="string"&&Hb.test(r)&&r.startsWith(t)||s&&!Wb(r)&&Object.prototype.hasOwnProperty.call(r,s)),Yf=(t,s,r)=>o=>{if(typeof o!="string")return o;const[c,u,h,p]=o.match(eu);return{[t]:parseFloat(c),[s]:parseFloat(u),[r]:parseFloat(h),alpha:p!==void 0?parseFloat(p):1}},Gb=t=>Wt(0,255,t),ql={...zs,transform:t=>Math.round(Gb(t))},ns={test:tu("rgb","red"),parse:Yf("red","green","blue"),transform:({red:t,green:s,blue:r,alpha:o=1})=>"rgba("+ql.transform(t)+", "+ql.transform(s)+", "+ql.transform(r)+", "+Bs(Ii.transform(o))+")"};function Kb(t){let s="",r="",o="",c="";return t.length>5?(s=t.substring(1,3),r=t.substring(3,5),o=t.substring(5,7),c=t.substring(7,9)):(s=t.substring(1,2),r=t.substring(2,3),o=t.substring(3,4),c=t.substring(4,5),s+=s,r+=r,o+=o,c+=c),{red:parseInt(s,16),green:parseInt(r,16),blue:parseInt(o,16),alpha:c?parseInt(c,16)/255:1}}const bc={test:tu("#"),parse:Kb,transform:ns.transform},Ui=t=>({test:s=>typeof s=="string"&&s.endsWith(t)&&s.split(" ").length===1,parse:parseFloat,transform:s=>`${s}${t}`}),un=Ui("deg"),en=Ui("%"),re=Ui("px"),qb=Ui("vh"),Xb=Ui("vw"),Im={...en,parse:t=>en.parse(t)/100,transform:t=>en.transform(t*100)},Is={test:tu("hsl","hue"),parse:Yf("hue","saturation","lightness"),transform:({hue:t,saturation:s,lightness:r,alpha:o=1})=>"hsla("+Math.round(t)+", "+en.transform(Bs(s))+", "+en.transform(Bs(r))+", "+Bs(Ii.transform(o))+")"},Ye={test:t=>ns.test(t)||bc.test(t)||Is.test(t),parse:t=>ns.test(t)?ns.parse(t):Is.test(t)?Is.parse(t):bc.parse(t),transform:t=>typeof t=="string"?t:t.hasOwnProperty("red")?ns.transform(t):Is.transform(t),getAnimatableNone:t=>{const s=Ye.parse(t);return s.alpha=0,Ye.transform(s)}},Yb=/(?:#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\))/giu,Qf=new RegExp(eu.source),Jf=new RegExp(Yb.source,"i");function Qb(t){return isNaN(t)&&typeof t=="string"&&(Qf.test(t)||Jf.test(t))}const Zf="number",eg="color",Jb="var",Zb="var(",Vm="${}",ew=/var\s*\(\s*--(?:[\w-]+\s*|[\w-]+\s*,(?:\s*[^)(\s]|\s*\((?:[^)(]|\([^)(]*\))*\))+\s*)\)|#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\)|-?(?:\d+(?:\.\d+)?|\.\d+)/giu;function tw(t){const s=t.toString();return Qf.test(s)||Jf.test(s)}function Vi(t){const s=t.toString(),r=[],o={color:[],number:[],var:[]},c=[];let u=0;const p=s.replace(ew,f=>(Ye.test(f)?(o.color.push(u),c.push(eg),r.push(Ye.parse(f))):f.startsWith(Zb)?(o.var.push(u),c.push(Jb),r.push(f)):(o.number.push(u),c.push(Zf),r.push(parseFloat(f))),++u,Vm)).split(Vm);return{values:r,split:p,indexes:o,types:c}}function nw(t){return Vi(t).values}function tg({split:t,types:s}){const r=t.length;return o=>{let c="";for(let u=0;u<r;u++)if(c+=t[u],o[u]!==void 0){const h=s[u];h===Zf?c+=Bs(o[u]):h===eg?c+=Ye.transform(o[u]):c+=o[u]}return c}}function sw(t){return tg(Vi(t))}const iw=t=>typeof t=="number"?0:Ye.test(t)?Ye.getAnimatableNone(t):t,rw=(t,s)=>typeof t=="number"?s!=null&&s.trim().endsWith("/")?t:0:iw(t);function aw(t){const s=Vi(t);return tg(s)(s.values.map((o,c)=>rw(o,s.split[c])))}const St={test:Qb,parse:nw,createTransformer:sw,getAnimatableNone:aw};function Xl(t,s,r){return r<0&&(r+=1),r>1&&(r-=1),r<1/6?t+(s-t)*6*r:r<1/2?s:r<2/3?t+(s-t)*(2/3-r)*6:t}function ow({hue:t,saturation:s,lightness:r,alpha:o}){t/=360,s/=100,r/=100;let c=0,u=0,h=0;if(!s)c=u=h=r;else{const p=r<.5?r*(1+s):r+s-r*s,f=2*r-p;c=Xl(f,p,t+1/3),u=Xl(f,p,t),h=Xl(f,p,t-1/3)}return{red:Math.round(c*255),green:Math.round(u*255),blue:Math.round(h*255),alpha:o}}function ja(t,s){return r=>r>0?s:t}const Pe=(t,s,r)=>t+(s-t)*r,Yl=(t,s,r)=>{const o=t*t,c=r*(s*s-o)+o;return c<0?0:Math.sqrt(c)},lw=[bc,ns,Is],cw=t=>lw.find(s=>s.test(t));function Fm(t){const s=cw(t);if(!s)return!1;let r=s.parse(t);return s===Is&&(r=ow(r)),r}const Bm=(t,s)=>{const r=Fm(t),o=Fm(s);if(!r||!o)return ja(t,s);const c={...r};return u=>(c.red=Yl(r.red,o.red,u),c.green=Yl(r.green,o.green,u),c.blue=Yl(r.blue,o.blue,u),c.alpha=Pe(r.alpha,o.alpha,u),ns.transform(c))},wc=new Set(["none","hidden"]);function uw(t,s){return wc.has(t)?r=>r<=0?t:s:r=>r>=1?s:t}function dw(t,s){return r=>Pe(t,s,r)}function nu(t){return typeof t=="number"?dw:typeof t=="string"?Zc(t)?ja:Ye.test(t)?Bm:pw:Array.isArray(t)?ng:typeof t=="object"?Ye.test(t)?Bm:hw:ja}function ng(t,s){const r=[...t],o=r.length,c=t.map((u,h)=>nu(u)(u,s[h]));return u=>{for(let h=0;h<o;h++)r[h]=c[h](u);return r}}function hw(t,s){const r={...t,...s},o={};for(const c in r)t[c]!==void 0&&s[c]!==void 0&&(o[c]=nu(t[c])(t[c],s[c]));return c=>{for(const u in o)r[u]=o[u](c);return r}}function mw(t,s){const r=[],o={color:0,var:0,number:0};for(let c=0;c<s.values.length;c++){const u=s.types[c],h=t.indexes[u][o[u]],p=t.values[h]??0;r[c]=p,o[u]++}return r}const pw=(t,s)=>{const r=St.createTransformer(s),o=Vi(t),c=Vi(s);return o.indexes.var.length===c.indexes.var.length&&o.indexes.color.length===c.indexes.color.length&&o.indexes.number.length>=c.indexes.number.length?wc.has(t)&&!c.values.length||wc.has(s)&&!o.values.length?uw(t,s):Oi(ng(mw(o,c),c.values),r):ja(t,s)},Om=/^(-?(?:\d+(?:\.\d*)?|\.\d+))([a-z%]*)$/iu;function fw(t,s){const r=Om.exec(t);if(!r)return;const o=Om.exec(s);if(!o||r[2]!==o[2])return;const c=r[2],u=parseFloat(r[1]),h=parseFloat(o[1]);return p=>Bs(Pe(u,h,p))+c}function su(t,s,r){if(typeof t=="number"&&typeof s=="number"&&typeof r=="number")return Pe(t,s,r);if(typeof t=="string"&&typeof s=="string"){const c=fw(t,s);if(c)return c}return nu(t)(t,s)}const gw=t=>{const s=({timestamp:r})=>t(r);return{start:(r=!0)=>Ee.update(s,r),stop:()=>Rn(s),now:()=>Xe.isProcessing?Xe.timestamp:ot.now()}},sg=(t,s,r=10)=>{let o="";const c=Math.max(Math.round(s/r),2);for(let u=0;u<c;u++)o+=Math.round(t(u/(c-1))*1e4)/1e4+", ";return`linear(${o.substring(0,o.length-2)})`},iu=2e4;function ru(t,s=50,r=iu,o){let c=0,u=t.next(c);for(;!u.done&&c<r;)c+=s,u=t.next(c);return c>=r?1/0:c}function yw(t,s=100,r){const o=r({...t,keyframes:[0,s]}),c=Math.min(ru(o),iu);return{type:"keyframes",ease:u=>o.next(c*u).value/s,duration:jt(c)}}const Be={stiffness:100,damping:10,mass:1,velocity:0,duration:800,bounce:.3,visualDuration:.3,restSpeed:{granular:.01,default:2},restDelta:{granular:.005,default:.5},minDuration:.01,maxDuration:10,minDamping:.05,maxDamping:1};function kc(t,s){return t*Math.sqrt(1-s*s)}const vw=12;function xw(t,s,r){let o=r;for(let c=1;c<vw;c++)o=o-t(o)/s(o);return o}const Ql=.001;function bw({duration:t=Be.duration,bounce:s=Be.bounce,velocity:r=Be.velocity,mass:o=Be.mass}){let c,u,h=1-s;h=Wt(Be.minDamping,Be.maxDamping,h),t=Wt(Be.minDuration,Be.maxDuration,jt(t)),h<1?(c=v=>{const g=v*h,x=g*t,b=g-r,j=kc(v,h),N=Math.exp(-x);return Ql-b/j*N},u=v=>{const x=v*h*t,b=x*r+r,j=h*h*v*v*t,N=Math.exp(-x),w=kc(v*v,h);return(-c(v)+Ql>0?-1:1)*((b-j)*N)/w}):(c=v=>{const g=Math.exp(-v*t),x=(v-r)*t+1;return-Ql+g*x},u=v=>{const g=Math.exp(-v*t),x=(r-v)*(t*t);return g*x});const p=5/t,f=xw(c,u,p);if(t=Dt(t),isNaN(f))return{stiffness:Be.stiffness,damping:Be.damping,duration:t};{const v=f*f*o;return{stiffness:v,damping:h*2*Math.sqrt(o*v),duration:t}}}const ig=["duration","bounce"],rg=["stiffness","damping","mass"];function Sa(t,s){return s.some(r=>t[r]!==void 0)}function ww(t){let s={velocity:Be.velocity,stiffness:Be.stiffness,damping:Be.damping,mass:Be.mass,isResolvedFromDuration:!1,...t};if(!Sa(t,rg)&&Sa(t,ig))if(s.velocity=0,t.visualDuration){const r=t.visualDuration,o=2*Math.PI/(r*1.2),c=o*o,u=2*Wt(.05,1,1-(t.bounce||0))*Math.sqrt(c);s={...s,mass:Be.mass,stiffness:c,damping:u}}else{const r=bw({...t,velocity:0});s={...s,...r,mass:Be.mass},s.isResolvedFromDuration=!0}return s}function Na(t=Be.visualDuration,s=Be.bounce){const r=typeof t!="object"?{visualDuration:t,keyframes:[0,1],bounce:s}:t,o=r.keyframes[0],c=r.keyframes[r.keyframes.length-1],u={done:!1,value:o},{stiffness:h,damping:p,mass:f,duration:v,velocity:g,isResolvedFromDuration:x}=ww({...r,velocity:-jt(r.velocity||0)}),b=p/(2*Math.sqrt(h*f)),j=jt(Math.sqrt(h/f)),N=b*j,w={target:c,delta:c-o,velocity:g||0,restSpeed:0,restDelta:0},S=()=>{const I=Math.abs(w.delta)<5;w.restSpeed=r.restSpeed||(I?Be.restSpeed.granular:Be.restSpeed.default),w.restDelta=r.restDelta||(I?Be.restDelta.granular:Be.restDelta.default)};S();let B,P,D;if(b<1){const I=kc(j,b),U={A:0,sinC:0,cosC:0,t:-1,env:0,sin:0,cos:0};D=()=>{U.A=(w.velocity+N*w.delta)/I,U.sinC=N*U.A+w.delta*I,U.cosC=N*w.delta-U.A*I};const ce=q=>{q!==U.t&&(U.t=q,U.env=Math.exp(-N*q),U.sin=Math.sin(I*q),U.cos=Math.cos(I*q))};B=q=>(ce(q),w.target-U.env*(U.A*U.sin+w.delta*U.cos)),P=q=>(ce(q),U.env*(U.sinC*U.sin+U.cosC*U.cos))}else if(b===1){B=U=>w.target-Math.exp(-j*U)*(w.delta+(w.velocity+j*w.delta)*U);const I={C:0};D=()=>{I.C=w.velocity+j*w.delta},P=U=>Math.exp(-j*U)*(j*I.C*U-w.velocity)}else{const I=j*Math.sqrt(b*b-1);B=ce=>{const q=Math.exp(-N*ce),ge=Math.min(I*ce,300);return w.target-q*((w.velocity+N*w.delta)*Math.sinh(ge)+I*w.delta*Math.cosh(ge))/I};const U={P:0,sinh:0,cosh:0};D=()=>{U.P=(w.velocity+N*w.delta)/I,U.sinh=N*U.P-w.delta*I,U.cosh=N*w.delta-U.P*I},P=ce=>{const q=Math.exp(-N*ce),ge=Math.min(I*ce,300);return q*(U.sinh*Math.sinh(ge)+U.cosh*Math.cosh(ge))}}D();const V=!Sa(r,rg)&&Sa(r,ig),_=x&&v||null,L={calculatedDuration:_,retarget:(I,U)=>{w.target=I[I.length-1],w.delta=w.target-I[0],w.velocity=V?0:-jt(U),r.restSpeed&&r.restDelta||S(),L.calculatedDuration=_,u.done=!1,D()},velocity:I=>Dt(P(I)),next:I=>{const U=B(I);if(x)u.done=I>=v;else{const ce=Dt(P(I));u.done=Math.abs(ce)<=w.restSpeed&&Math.abs(w.target-U)<=w.restDelta}return u.value=u.done?w.target:U,u},toString:()=>{const I=Math.min(ru(L),iu),U=sg(ce=>L.next(I*ce).value,I,30);return I+"ms "+U},toTransition:()=>{}};return L}Na.applyToOptions=t=>{const s=yw(t,100,Na);return t.ease=s.ease,t.duration=Dt(s.duration),t.type="keyframes",t};function jc({keyframes:t,velocity:s=0,power:r=.8,timeConstant:o=325,bounceDamping:c=10,bounceStiffness:u=500,modifyTarget:h,min:p,max:f,restDelta:v=.5,restSpeed:g}){const x=t[0],b={done:!1,value:x},j=I=>I<p||I>f,N=I=>p===void 0?f:f===void 0||Math.abs(p-I)<Math.abs(f-I)?p:f;let w=r*s;const S=x+w,B=h===void 0?S:h(S);B!==S&&(w=B-x);const P=I=>-w*Math.exp(-I/o),D=I=>{const U=P(I);b.done=Math.abs(U)<=v,b.value=b.done?B:B+U};let V,_;const L=I=>{j(b.value)&&(V=I,_=Na({keyframes:[b.value,N(b.value)],velocity:-P(I)/o*1e3,damping:c,stiffness:u,restDelta:v,restSpeed:g}))};return L(0),{calculatedDuration:null,next:I=>{let U=!1;return!_&&V===void 0&&(U=!0,D(I),L(I)),V!==void 0&&I>=V?_.next(I-V):(!U&&D(I),b)}}}function kw(t,s,r){const o=[],c=r||dn.mix||su,u=t.length-1;for(let h=0;h<u;h++){let p=c(t[h],t[h+1]);if(s){const f=Array.isArray(s)?s[h]||$t:s;p=Oi(f,p)}o.push(p)}return o}function jw(t,s,{clamp:r=!0,ease:o,mixer:c}={}){const u=t.length;if(Va(u===s.length),u===1)return()=>s[0];if(u===2&&s[0]===s[1])return()=>s[1];const h=t[0]===t[1];t[0]>t[u-1]&&(t=[...t].reverse(),s=[...s].reverse());const p=kw(s,o,c),f=p.length,v=g=>{if(h&&g<t[0])return s[0];let x=0;if(f>1)for(;x<t.length-2&&!(g<t[x+1]);x++);const b=Li(t[x],t[x+1],g);return p[x](b)};return r?g=>v(Wt(t[0],t[u-1],g)):v}function Sw(t,s){const r=t[t.length-1];for(let o=1;o<=s;o++){const c=Li(0,s,o);t.push(Pe(r,1,c))}}function Nw(t){const s=[0];return Sw(s,t.length-1),s}function Cw(t,s){return t.map(r=>r*s)}function Tw(t,s){return t.map(()=>s||Hf).splice(0,t.length-1)}function _i({duration:t=300,keyframes:s,times:r,ease:o="easeInOut"}){const c=Ib(o)?o.map(Rm):Rm(o),u={done:!1,value:s[0]};if(s.length===2&&!Array.isArray(c)&&(!r||r.length!==2||r[0]===0&&r[1]===1)){const[f,v]=s,g=f===v?void 0:(dn.mix||su)(f,v);return{calculatedDuration:t,next:x=>(u.value=g?g(c(t>0?Wt(0,1,x/t):1)):v,u.done=x>=t,u)}}const h=Cw(r&&r.length===s.length?r:Nw(s),t),p=jw(h,s,{ease:Array.isArray(c)?c:Tw(s,c)});return{calculatedDuration:t,next:f=>(u.value=p(f),u.done=f>=t,u)}}const Aw=5;function Pw(t,s,r){const o=Math.max(s-Aw,0);return If(r-t(o),s-o)}function Ew(t,s,r=0){return s<=0?r:t.velocity?t.velocity(s):Pw(o=>t.next(o).value,s,t.next(s).value)}const Mw=t=>t!==null;function Fa(t,{repeat:s,repeatType:r="loop"},o,c=1){const u=t.filter(Mw),p=c<0||s&&r!=="loop"&&s%2===1?0:u.length-1;return!p||o===void 0?u[p]:o}const _w={decay:jc,inertia:jc,tween:_i,keyframes:_i,spring:Na};function ag(t){typeof t.type=="string"&&(t.type=_w[t.type])}function og(t,s){return{kind:t,animation:s,timestamp:ot.now(),frameTimestamp:Xe.timestamp,frameIsProcessing:Xe.isProcessing}}function lg(t,s,r){const o=globalThis.__MOTION_INSPECT__;if(o)try{o({...og("animation-start",t),options:r?{...s,...r}:s})}catch{}}function Dw(t,s){const r=globalThis.__MOTION_INSPECT__;if(r)try{r({...og("layout-animation-start",t),node:s})}catch{}}class au{constructor(){this.isResolved=!1}get finished(){return this._finished||(this._finished=this.isResolved?Promise.resolve():new Promise(s=>{this._resolve=s})),this._finished}updateFinished(){this._finished=this._resolve=void 0,this.isResolved=!1}notifyFinished(){var s;this.isResolved=!0,(s=this._resolve)==null||s.call(this)}then(s,r){return this.finished.then(s,r)}}const Rw=t=>t/100;class Ca extends au{constructor(s){super(),this.state="idle",this.startTime=null,this.isStopped=!1,this.currentTime=0,this.holdTime=null,this.playbackSpeed=1,this.delayState={done:!1,value:void 0},this.stop=()=>{var o,c;const{motionValue:r}=this.options;r&&r.updatedAt!==ot.now()&&this.tick(ot.now()),this.isStopped=!0,this.state!=="idle"&&(this.teardown(),(c=(o=this.options).onStop)==null||c.call(o))},this.options=s,this.initAnimation(),this.play(),s.autoplay===!1&&this.pause(),lg(this,this.options)}initAnimation(){const{options:s}=this;ag(s);const{type:r=_i,repeat:o=0,repeatDelay:c=0,repeatType:u,velocity:h=0}=s;let{keyframes:p}=s;const f=r||_i;f!==_i&&typeof p[0]!="number"&&(this.mixKeyframes=Oi(Rw,su(p[0],p[1])),p=[0,100]);const v=f(p===s.keyframes?s:{...s,keyframes:p});u==="mirror"&&(this.mirroredGenerator=f({...s,keyframes:[...p].reverse(),velocity:-h})),v.calculatedDuration===null&&(v.calculatedDuration=ru(v));const{calculatedDuration:g}=v;this.calculatedDuration=g,this.resolvedDuration=g+c,this.totalDuration=this.resolvedDuration*(o+1)-c,this.generator=v}updateTime(s){const r=Math.round(s-this.startTime)*this.playbackSpeed;this.holdTime!==null?this.currentTime=this.holdTime:this.currentTime=r}tick(s,r=!1){const{generator:o,totalDuration:c,mixKeyframes:u,mirroredGenerator:h,resolvedDuration:p,calculatedDuration:f}=this;if(this.startTime===null)return o.next(0);const{delay:v=0,keyframes:g,repeat:x,repeatType:b,repeatDelay:j,type:N,onUpdate:w,finalKeyframe:S}=this.options;this.speed>0?this.startTime=Math.min(this.startTime,s):this.speed<0&&(this.startTime=Math.min(s-c/this.speed,this.startTime)),r?this.currentTime=s:this.updateTime(s);const B=this.currentTime-v*(this.playbackSpeed>=0?1:-1),P=this.playbackSpeed>=0?B<0:B>c;this.currentTime=Math.max(B,0),this.state==="finished"&&this.holdTime===null&&(this.currentTime=c);let D=this.currentTime,V=o;if(x){const U=Math.min(this.currentTime,c)/p;let ce=Math.floor(U),q=U%1;!q&&U>=1&&(q=1),q===1&&ce--,ce=Math.min(ce,x+1),!!(ce%2)&&(b==="reverse"?(q=1-q,j&&(q-=j/p)):b==="mirror"&&(V=h)),D=Wt(0,1,q)*p}let _;P?(this.delayState.value=g[0],_=this.delayState):_=V.next(D),u&&!P&&(_.value=u(_.value));let{done:L}=_;!P&&f!==null&&(L=this.playbackSpeed>=0?this.currentTime>=c:this.currentTime<=0);const I=this.holdTime===null&&(this.state==="finished"||this.state==="running"&&L);return I&&N!==jc&&(_.value=Fa(g,this.options,S,this.speed)),w&&w(_.value),I&&this.finish(),_}then(s,r){return this.finished.then(s,r)}get duration(){return jt(this.calculatedDuration)}get iterationDuration(){const{delay:s=0}=this.options||{};return this.duration+jt(s)}get time(){return jt(this.currentTime)}set time(s){s=Dt(s),this.currentTime=s,this.startTime===null||this.holdTime!==null||this.playbackSpeed===0?this.holdTime=s:this.driver&&(this.startTime=this.driver.now()-s/this.playbackSpeed),this.driver?this.driver.start(!1):(this.startTime=0,this.state="paused",this.holdTime=s,this.tick(s))}getGeneratorVelocity(){return Ew(this.generator,this.currentTime,this.options.velocity)}get speed(){return this.playbackSpeed}set speed(s){const r=this.playbackSpeed!==s;r&&this.driver&&this.updateTime(ot.now()),this.playbackSpeed=s,r&&this.driver&&(this.time=jt(this.currentTime))}play(){var c,u;if(this.isStopped)return;const{driver:s=gw,startTime:r}=this.options;this.driver||(this.driver=s(h=>this.tick(h))),(u=(c=this.options).onPlay)==null||u.call(c);const o=this.driver.now();this.state==="finished"?(this.updateFinished(),this.startTime=o):this.holdTime!==null?this.startTime=o-this.holdTime:this.startTime||(this.startTime=r??o),this.state==="finished"&&this.speed<0&&(this.startTime+=this.calculatedDuration),this.holdTime=null,this.state="running",this.driver.start()}pause(){this.state="paused",this.updateTime(ot.now()),this.holdTime=this.currentTime}complete(){this.state!=="running"&&this.play(),this.state="finished",this.holdTime=null}finish(){var s,r;this.notifyFinished(),this.teardown(),this.state="finished",(r=(s=this.options).onComplete)==null||r.call(s)}cancel(){var s,r;this.holdTime=null,this.startTime=0,this.tick(0),this.teardown(),(r=(s=this.options).onCancel)==null||r.call(s)}teardown(){this.state="idle",this.stopDriver(),this.startTime=this.holdTime=null}stopDriver(){this.driver&&(this.driver.stop(),this.driver=void 0)}sample(s){return this.startTime=0,this.tick(s,!0)}attachTimeline(s){var r;return this.options.allowFlatten&&(this.options.type="keyframes",this.options.ease="linear",this.initAnimation()),(r=this.driver)==null||r.stop(),s.observe(this)}}const Lw=new Set(["brightness","contrast","saturate","opacity"]);function Iw(t){const[s,r]=t.slice(0,-1).split("(");if(s==="drop-shadow")return t;const[o]=r.match(eu)||[];if(!o)return t;const c=r.replace(o,"");let u=Lw.has(s)?1:0;return o!==r&&(u*=100),s+"("+u+c+")"}const Vw=/\b([a-z-]*)\(.*?\)/gu,Sc={...St,getAnimatableNone:t=>{const s=t.match(Vw);return s?s.map(Iw).join(" "):t}},Nc={...St,getAnimatableNone:t=>{const s=St.parse(t);return St.createTransformer(t)(s.map(o=>typeof o=="number"?0:typeof o=="object"?{...o,alpha:1}:o))}},zm={...zs,transform:Math.round},Fw={rotate:un,pathRotation:un,rotateX:un,rotateY:un,rotateZ:un,scale:sa,scaleX:sa,scaleY:sa,scaleZ:sa,skew:un,skewX:un,skewY:un,distance:re,translateX:re,translateY:re,translateZ:re,x:re,y:re,z:re,perspective:re,transformPerspective:re,opacity:Ii,originX:Im,originY:Im,originZ:re},Ta={borderWidth:re,borderTopWidth:re,borderRightWidth:re,borderBottomWidth:re,borderLeftWidth:re,borderRadius:re,borderTopLeftRadius:re,borderTopRightRadius:re,borderBottomRightRadius:re,borderBottomLeftRadius:re,width:re,maxWidth:re,height:re,maxHeight:re,top:re,right:re,bottom:re,left:re,inset:re,insetBlock:re,insetBlockStart:re,insetBlockEnd:re,insetInline:re,insetInlineStart:re,insetInlineEnd:re,padding:re,paddingTop:re,paddingRight:re,paddingBottom:re,paddingLeft:re,paddingBlock:re,paddingBlockStart:re,paddingBlockEnd:re,paddingInline:re,paddingInlineStart:re,paddingInlineEnd:re,margin:re,marginTop:re,marginRight:re,marginBottom:re,marginLeft:re,marginBlock:re,marginBlockStart:re,marginBlockEnd:re,marginInline:re,marginInlineStart:re,marginInlineEnd:re,fontSize:re,backgroundPositionX:re,backgroundPositionY:re,...Fw,zIndex:zm,fillOpacity:Ii,strokeOpacity:Ii,numOctaves:zm},Bw={...Ta,color:Ye,backgroundColor:Ye,outlineColor:Ye,fill:Ye,stroke:Ye,borderColor:Ye,borderTopColor:Ye,borderRightColor:Ye,borderBottomColor:Ye,borderLeftColor:Ye,filter:Sc,WebkitFilter:Sc,mask:Nc,WebkitMask:Nc},cg=t=>Bw[t],Ow=new Set([Sc,Nc]);function ou(t,s){let r=cg(t);return Ow.has(r)||(r=St),r.getAnimatableNone?r.getAnimatableNone(s):void 0}function zw(t){for(let s=1;s<t.length;s++)t[s]??(t[s]=t[s-1])}const ss=t=>t*180/Math.PI,Cc=t=>{const s=ss(Math.atan2(t[1],t[0]));return Tc(s)},Uw={x:4,y:5,translateX:4,translateY:5,scaleX:0,scaleY:3,scale:t=>(Math.abs(t[0])+Math.abs(t[3]))/2,rotate:Cc,rotateZ:Cc,skewX:t=>ss(Math.atan(t[1])),skewY:t=>ss(Math.atan(t[2])),skew:t=>(Math.abs(t[1])+Math.abs(t[2]))/2},Tc=t=>(t=t%360,t<0&&(t+=360),t),Um=Cc,$m=t=>Math.sqrt(t[0]*t[0]+t[1]*t[1]),Wm=t=>Math.sqrt(t[4]*t[4]+t[5]*t[5]),$w={x:12,y:13,z:14,translateX:12,translateY:13,translateZ:14,scaleX:$m,scaleY:Wm,scale:t=>($m(t)+Wm(t))/2,rotateX:t=>Tc(ss(Math.atan2(t[6],t[5]))),rotateY:t=>Tc(ss(Math.atan2(-t[2],t[0]))),rotateZ:Um,rotate:Um,skewX:t=>ss(Math.atan(t[4])),skewY:t=>ss(Math.atan(t[1])),skew:t=>(Math.abs(t[1])+Math.abs(t[4]))/2};function Ac(t){return t.includes("scale")?1:0}function Pc(t,s){if(!t||t==="none")return Ac(s);const r=t.match(/^matrix3d\(([-\d.e\s,]+)\)$/u);let o,c;if(r)o=$w,c=r;else{const p=t.match(/^matrix\(([-\d.e\s,]+)\)$/u);o=Uw,c=p}if(!c)return Ac(s);const u=o[s],h=c[1].split(",").map(Hw);return typeof u=="function"?u(h):h[u]}const Ww=(t,s)=>{const{transform:r="none"}=getComputedStyle(t);return Pc(r,s)};function Hw(t){return parseFloat(t.trim())}const Us=["transformPerspective","x","y","z","translateX","translateY","translateZ","scale","scaleX","scaleY","rotate","rotateX","rotateY","rotateZ","skew","skewX","skewY"],$s=new Set([...Us,"pathRotation"]),Hm=t=>t===zs||t===re,Gw=new Set(["x","y","z"]),Kw=Us.filter(t=>!Gw.has(t));function qw(t){const s=[];return Kw.forEach(r=>{const o=t.getValue(r);if(o!==void 0){const c=o.get(),u=r.startsWith("scale")?1:0;if(c===u)return;s.push([r,c]),o.set(u)}}),s}const Xw=new Set(["bottom","right"]);function Gm(t,s,r,o,c,u){const h=parseFloat(t);if(!isNaN(h))return h;const{min:p,max:f}=s()[r],v=f-p;return u==="border-box"?v:v-parseFloat(o)-parseFloat(c)}const rs={width:({width:t,paddingLeft:s="0",paddingRight:r="0",boxSizing:o},c)=>Gm(t,c,"x",s,r,o),height:({height:t,paddingTop:s="0",paddingBottom:r="0",boxSizing:o},c)=>Gm(t,c,"y",s,r,o),top:({top:t})=>parseFloat(t),left:({left:t})=>parseFloat(t),bottom:({top:t},s)=>{const{y:r}=s();return parseFloat(t)+(r.max-r.min)},right:({left:t},s)=>{const{x:r}=s();return parseFloat(t)+(r.max-r.min)},x:({transform:t})=>Pc(t,"x"),y:({transform:t})=>Pc(t,"y")};rs.translateX=rs.x;rs.translateY=rs.y;const as=new Set;let Ec=!1,Mc=!1,_c=!1;function ug(){if(Mc){const t=[],s=new Set,r=new Set;as.forEach(c=>{c.needsMeasurement&&(t.push(c),s.add(c.element),Xw.has(c.name)&&r.add(c.element))});const o=new Map;r.forEach(c=>{const u=qw(c);u.length&&(o.set(c,u),c.render())}),t.forEach(c=>c.measureInitialState()),s.forEach(c=>{c.render();const u=o.get(c);u&&u.forEach(([h,p])=>{var f;(f=c.getValue(h))==null||f.set(p)})}),t.forEach(c=>c.measureEndState()),t.forEach(c=>{c.suspendedScrollY!==void 0&&window.scrollTo(0,c.suspendedScrollY)})}Mc=!1,Ec=!1,as.forEach(t=>t.complete(_c)),as.clear()}function dg(){as.forEach(t=>{t.readKeyframes(),t.needsMeasurement&&(Mc=!0)})}function Yw(){_c=!0,dg(),ug(),_c=!1}function Qw(t,s,r){if(typeof t=="string"){if(Xc(t)||Yc(t))return parseFloat(t);if(!St.test(t)&&St.test(r))return ou(s,r)}return t??void 0}class lu{constructor(s,r,o,c,u,h=!1){this.state="pending",this.isAsync=!1,this.needsMeasurement=!1,this.unresolvedKeyframes=[...s],this.onComplete=r,this.name=o,this.motionValue=c,this.element=u,this.isAsync=h}scheduleResolve(){this.state="scheduled",this.isAsync?(as.add(this),Ec||(Ec=!0,Ee.read(dg),Ee.resolveKeyframes(ug))):(this.readKeyframes(),this.complete())}readKeyframes(){const{unresolvedKeyframes:s,name:r,element:o,motionValue:c}=this;if(s[0]===null){const u=c==null?void 0:c.get(),h=s[s.length-1];if(u!==void 0)s[0]=u;else if(o&&r){const p=Qw(o.readValue(r,h),r,h);p!==void 0&&(s[0]=p)}s[0]===void 0&&(s[0]=h),c&&u===void 0&&c.set(s[0])}zw(s)}setFinalKeyframe(){}measureInitialState(){}renderEndStyles(){}measureEndState(){}complete(s=!1){this.state="complete",this.onComplete(this.unresolvedKeyframes,this.finalKeyframe,s),as.delete(this)}cancel(){this.state==="scheduled"&&(as.delete(this),this.state="pending")}resume(){this.state==="pending"&&this.scheduleResolve()}}const Jw=t=>t.startsWith("--");function hg(t,s,r){Jw(s)?t.style.setProperty(s,r):t.style[s]=r}const Zw={};function mg(t,s){const r=Lf(t);return()=>Zw[s]??r()}const ek=mg(()=>window.ScrollTimeline!==void 0,"scrollTimeline"),pg=mg(()=>{try{document.createElement("div").animate({opacity:0},{easing:"linear(0, 1)"})}catch{return!1}return!0},"linearEasing"),Mi=([t,s,r,o])=>`cubic-bezier(${t}, ${s}, ${r}, ${o})`,Km={linear:"linear",ease:"ease",easeIn:"ease-in",easeOut:"ease-out",easeInOut:"ease-in-out",circIn:Mi([0,.65,.55,1]),circOut:Mi([.55,0,1,.45]),backIn:Mi([.31,.01,.66,-.59]),backOut:Mi([.33,1.53,.69,.99])};function fg(t,s){if(t)return typeof t=="function"?pg()?sg(t,s):"ease-out":Gf(t)?Mi(t):Array.isArray(t)?t.map(r=>fg(r,s)||Km.easeOut):Km[t]}function tk(t,s,r,{delay:o=0,duration:c=300,repeat:u=0,repeatType:h="loop",ease:p="easeOut",times:f}={},v=void 0){const g={[s]:r};f&&(g.offset=f);const x=fg(p,c);Array.isArray(x)&&(g.easing=x);const b={delay:o,duration:c,easing:Array.isArray(x)?"linear":x,fill:"both",iterations:u+1,direction:h==="reverse"?"alternate":"normal"};return v&&(b.pseudoElement=v),t.animate(g,b)}function gg(t){return typeof t=="function"&&"applyToOptions"in t}function nk({type:t,...s}){return gg(t)&&pg()?t.applyToOptions(s):(s.duration??(s.duration=300),s.ease??(s.ease="easeOut"),s)}class yg extends au{constructor(s){if(super(),this.finishedTime=null,this.isStopped=!1,this.manualStartTime=null,!s)return;const{element:r,name:o,keyframes:c,pseudoElement:u,allowFlatten:h=!1,finalKeyframe:p,onComplete:f}=s;this.isPseudoElement=!!u,this.allowFlatten=h,this.options=s,Va(typeof s.type!="string");const v=nk(s);this.animation=tk(r,o,c,v,u),v.autoplay===!1&&this.animation.pause(),this.animation.onfinish=()=>{if(this.finishedTime=this.time,!u){const g=Fa(c,this.options,p,this.speed);this.updateMotionValue&&this.updateMotionValue(g),hg(r,o,g),this.animation.cancel()}f==null||f(),this.notifyFinished()},lg(this,s,v)}play(){this.isStopped||(this.manualStartTime=null,this.animation.play(),this.state==="finished"&&this.updateFinished())}pause(){this.animation.pause()}complete(){var s,r;(r=(s=this.animation).finish)==null||r.call(s)}cancel(){try{this.animation.cancel()}catch{}}stop(){if(this.isStopped)return;this.isStopped=!0;const{state:s}=this;s==="idle"||s==="finished"||(this.updateMotionValue?this.updateMotionValue():this.commitStyles(),this.isPseudoElement||this.cancel())}commitStyles(){var r,o,c;const s=(r=this.options)==null?void 0:r.element;!this.isPseudoElement&&(s!=null&&s.isConnected)&&((c=(o=this.animation).commitStyles)==null||c.call(o))}get duration(){var r,o;const s=((o=(r=this.animation.effect)==null?void 0:r.getComputedTiming)==null?void 0:o.call(r).duration)||0;return jt(Number(s))}get iterationDuration(){const{delay:s=0}=this.options||{};return this.duration+jt(s)}get time(){return jt(Number(this.animation.currentTime)||0)}set time(s){const r=this.finishedTime!==null;this.manualStartTime=null,this.finishedTime=null,this.animation.currentTime=Dt(s),r&&this.animation.pause()}get speed(){return this.animation.playbackRate}set speed(s){s<0&&(this.finishedTime=null),this.animation.playbackRate=s}get state(){return this.finishedTime!==null?"finished":this.animation.playState}get startTime(){return this.manualStartTime??Number(this.animation.startTime)}set startTime(s){this.manualStartTime=this.animation.startTime=s}attachTimeline({timeline:s,rangeStart:r,rangeEnd:o,observe:c}){var u;return this.allowFlatten&&((u=this.animation.effect)==null||u.updateTiming({easing:"linear"})),this.animation.onfinish=null,s&&ek()?(this.animation.timeline=s,r&&(this.animation.rangeStart=r),o&&(this.animation.rangeEnd=o),$t):c(this)}}const vg={anticipate:Uf,backInOut:zf,circInOut:Wf};function sk(t){return t in vg}function ik(t){typeof t.ease=="string"&&sk(t.ease)&&(t.ease=vg[t.ease])}const Jl=10;class rk extends yg{constructor(s){ik(s),ag(s),super(s),s.startTime!==void 0&&s.autoplay!==!1&&(this.startTime=s.startTime),this.options=s}updateMotionValue(s){const{motionValue:r,onUpdate:o,onComplete:c,element:u,...h}=this.options;if(!r)return;if(s!==void 0){r.set(s);return}const p=new Ca({...h,autoplay:!1}),f=Math.max(Jl,ot.now()-this.startTime),v=Wt(0,Jl,f-Jl),g=p.sample(f).value,{name:x}=this.options;u&&x&&hg(u,x,g),r.setWithVelocity(p.sample(Math.max(0,f-v)).value,g,v),p.stop()}}const qm=(t,s)=>s==="zIndex"?!1:!!(typeof t=="number"||Array.isArray(t)||typeof t=="string"&&(St.test(t)||t==="0")&&!t.startsWith("url("));function ak(t){const s=t[0];if(t.length===1)return!0;for(let r=0;r<t.length;r++)if(t[r]!==s)return!0}function ok(t,s,r,o){const c=t[0];if(c===null)return!1;if(s==="display"||s==="visibility")return!0;const u=t[t.length-1],h=qm(c,s),p=qm(u,s);return!h||!p?!1:ak(t)||(r==="spring"||gg(r))&&o}function Dc(t){t.duration=0,t.type="keyframes"}const Rc=new Set(["opacity","clipPath","filter","transform","backgroundColor"]),lk=/^(?:oklch|oklab|lab|lch|color|color-mix|light-dark)\(/;function ck(t){for(let s=0;s<t.length;s++)if(typeof t[s]=="string"&&lk.test(t[s]))return!0;return!1}const Xm=new Set(["color","backgroundColor","outlineColor","fill","stroke","borderColor","borderTopColor","borderRightColor","borderBottomColor","borderLeftColor"]),uk=Lf(()=>Object.hasOwnProperty.call(Element.prototype,"animate"));function dk(t){var x;const{motionValue:s,name:r,repeatDelay:o,repeatType:c,damping:u,type:h,keyframes:p}=t;if(!r||!(Rc.has(r)||Xm.has(r)))return!1;const f=(x=s==null?void 0:s.owner)==null?void 0:x.current;if(!(f instanceof HTMLElement)&&!(f instanceof SVGElement))return!1;const{onUpdate:v,transformTemplate:g}=s.owner.getProps();return uk()&&(Rc.has(r)||Xm.has(r)&&ck(p))&&(r!=="transform"||!g)&&!v&&!o&&c!=="mirror"&&u!==0&&h!=="inertia"}const hk=40;class mk extends au{constructor(s){var f;super(),this.stop=()=>{var v,g;this._animation&&(this._animation.stop(),(v=this.stopTimeline)==null||v.call(this)),(g=this.keyframeResolver)==null||g.cancel()},this.createdAt=ot.now();const{keyframes:r,name:o,motionValue:c,element:u}=s,h=s;h.autoplay??(h.autoplay=!0),h.delay??(h.delay=0),h.type??(h.type="keyframes"),h.repeat??(h.repeat=0),h.repeatDelay??(h.repeatDelay=0),h.repeatType??(h.repeatType="loop");const p=(u==null?void 0:u.KeyframeResolver)||lu;this.keyframeResolver=new p(r,(v,g,x)=>this.onKeyframesResolved(v,g,h,!x),o,c,u),(f=this.keyframeResolver)==null||f.scheduleResolve()}onKeyframesResolved(s,r,o,c){var S,B;this.keyframeResolver=void 0;const{name:u,type:h,velocity:p,delay:f,isHandoff:v,onUpdate:g}=o;this.resolvedAt=ot.now();let x=!0;ok(s,u,h,p)||(x=!1,(dn.instantAnimations||!f)&&(g==null||g(Fa(s,o,r))),s[0]=s[s.length-1],Dc(o),o.repeat=0);const b=c?this.resolvedAt?this.resolvedAt-this.createdAt>hk?this.resolvedAt:this.createdAt:this.createdAt:void 0,{onComplete:j}=o;o.startTime??(o.startTime=b),o.finalKeyframe=r,o.keyframes=s,o.onComplete=()=>{j==null||j(),this.notifyFinished()};const N=x&&!v&&dk(o);let w;if(N){o.element=(B=(S=o.motionValue)==null?void 0:S.owner)==null?void 0:B.current;try{w=new rk(o)}catch{w=new Ca(o)}}else w=new Ca(o);this.pendingTimeline&&(this.stopTimeline=w.attachTimeline(this.pendingTimeline),this.pendingTimeline=void 0),this._animation=w}get finished(){return this._animation?this._animation.finished:super.finished}then(s,r){return this.finished.finally(s).then(()=>{})}get animation(){var s;return this._animation||((s=this.keyframeResolver)==null||s.resume(),Yw()),this._animation}get duration(){return this.animation.duration}get iterationDuration(){return this.animation.iterationDuration}get time(){return this.animation.time}set time(s){this.animation.time=s}get speed(){return this.animation.speed}get state(){return this.animation.state}set speed(s){this.animation.speed=s}get startTime(){return this.animation.startTime}attachTimeline(s){return this._animation?this.stopTimeline=this.animation.attachTimeline(s):this.pendingTimeline=s,()=>this.stop()}play(){this.animation.play()}pause(){this.animation.pause()}complete(){this.animation.complete()}cancel(){var s;this._animation&&this.animation.cancel(),(s=this.keyframeResolver)==null||s.cancel()}}function xg(t,s,r,o=0,c=1){const u=Array.from(t).sort((v,g)=>v.sortNodePosition(g)).indexOf(s),h=t.size,p=(h-1)*o;return typeof r=="function"?r(u,h):c===1?u*o:p-u*o}const Ym=30,pk=t=>!isNaN(parseFloat(t));class fk{constructor(s,r={}){this.canTrackVelocity=null,this.events={},this.updateAndNotify=o=>{const c=ot.now();if(this.updatedAt!==c&&this.setPrevFrameValue(),this.prev=this.current,this.setCurrent(o),this.current!==this.prev&&(this.notifyChange(),this.dependents))for(const u of this.dependents)u.dirty()},this.hasAnimated=!1,this.setCurrent(s),this.owner=r.owner}setCurrent(s){this.current=s,this.updatedAt=ot.now(),this.canTrackVelocity===null&&s!==void 0&&(this.canTrackVelocity=pk(this.current))}setPrevFrameValue(s=this.current){this.prevFrameValue=s,this.prevUpdatedAt=this.updatedAt}onChange(s){return this.on("change",s)}on(s,r){var o;return s==="change"?this.onChangeSubscribe(r):((o=this.events)[s]||(o[s]=new ka)).add(r)}onChangeSubscribe(s){const{events:r}=this;return!r.change&&!this.changeSubscriber?this.changeSubscriber=s:(r.change||(r.change=new ka,r.change.add(this.changeSubscriber),this.changeSubscriber=void 0),r.change.add(s)),()=>{var o;this.changeSubscriber===s?this.changeSubscriber=void 0:(o=r.change)==null||o.remove(s),this.stopIfUnobserved()}}stopIfUnobserved(){Ee.read(()=>{var s;!this.changeSubscriber&&!((s=this.events.change)!=null&&s.getSize())&&this.stop()})}clearListeners(){this.changeSubscriber=void 0;for(const s in this.events)this.events[s].clear()}attach(s,r){this.passiveEffect=s,this.stopPassiveEffect=r}set(s){this.passiveEffect?this.passiveEffect(s,this.updateAndNotify):this.updateAndNotify(s)}setWithVelocity(s,r,o){this.set(r),this.prev=void 0,this.prevFrameValue=s,this.prevUpdatedAt=this.updatedAt-o}jump(s,r=!0){this.updateAndNotify(s),this.prev=s,this.prevUpdatedAt=this.prevFrameValue=void 0,r&&this.stop(),this.stopPassiveEffect&&this.stopPassiveEffect()}dirty(){this.notifyChange()}notifyChange(){var o;const{current:s,changeSubscriber:r}=this;r?r(s):(o=this.events.change)==null||o.notify(s)}addDependent(s){this.dependents||(this.dependents=new Set),this.dependents.add(s)}removeDependent(s){this.dependents&&this.dependents.delete(s)}get(){return this.current}getPrevious(){return this.prev}getVelocity(){const s=ot.now();if(!this.canTrackVelocity||this.prevFrameValue===void 0||s-this.updatedAt>Ym)return 0;const r=Math.min(this.updatedAt-this.prevUpdatedAt,Ym);return If(parseFloat(this.current)-parseFloat(this.prevFrameValue),r)}start(s){return this.stop(),new Promise(r=>{var u;this.hasAnimated=!0;let o=!1,c;c=s(()=>{var h;o=!0,(h=this.events.animationComplete)==null||h.notify(),this.animation===c&&this.clearAnimation(),r()}),o||(this.animation=c),(u=this.events.animationStart)==null||u.notify()})}stop(){this.animation&&(this.animation.stop(),this.events.animationCancel&&this.events.animationCancel.notify()),this.clearAnimation()}isAnimating(){return!!this.animation}clearAnimation(){this.animation=void 0}destroy(){var s,r;(s=this.dependents)==null||s.clear(),(r=this.events.destroy)==null||r.notify(),this.clearListeners(),this.stop(),this.stopPassiveEffect&&this.stopPassiveEffect()}}function Os(t,s){return new fk(t,s)}function bg(t,s){if(t!=null&&t.inherit&&s){const{inherit:r,...o}=t;return{...s,...o}}return t}function cu(t,s){const r=(t==null?void 0:t[s])??(t==null?void 0:t.default)??t;return r!==t?bg(r,t):r}const gk={type:"spring",stiffness:500,damping:25,restSpeed:10},yk=t=>({type:"spring",stiffness:550,damping:t===0?2*Math.sqrt(550):30,restSpeed:10}),vk={type:"keyframes",duration:.8},xk={type:"keyframes",ease:[.25,.1,.35,1],duration:.3},bk=(t,{keyframes:s})=>s.length>2?vk:$s.has(t)?t.startsWith("scale")?yk(s[1]):gk:xk,wk=new Set(["when","delay","delayChildren","staggerChildren","staggerDirection","repeat","repeatType","repeatDelay","from","elapsed"]);function kk(t){for(const s in t)if(!wk.has(s))return!0;return!1}const uu=(t,s,r,o={},c,u)=>h=>{const p=cu(o,t)||{},f=p.delay||o.delay||0;let{elapsed:v=0}=o;v=v-Dt(f);const g={keyframes:Array.isArray(r)?r:[null,r],ease:"easeOut",velocity:s.getVelocity(),...p,delay:-v,onUpdate:b=>{s.set(b),p.onUpdate&&p.onUpdate(b)},onComplete:()=>{h(),p.onComplete&&p.onComplete()},name:t,motionValue:s,element:u?void 0:c};kk(p)||Object.assign(g,bk(t,g)),g.duration&&(g.duration=Dt(g.duration)),g.repeatDelay&&(g.repeatDelay=Dt(g.repeatDelay)),g.from!==void 0&&(g.keyframes[0]=g.from);let x=!1;if((g.type===!1||g.duration===0&&!g.repeatDelay)&&(Dc(g),g.delay===0&&(x=!0)),(dn.instantAnimations||dn.skipAnimations||c!=null&&c.shouldSkipAnimations||p.skipAnimations)&&(x=!0,Dc(g),g.delay=0),g.allowFlatten=!p.type&&!p.ease,x&&!u&&s.get()!==void 0){const b=Fa(g.keyframes,p);if(b!==void 0){Ee.update(()=>{g.onUpdate(b),g.onComplete()});return}}return p.isSync?new Ca(g):new mk(g)},jk=/^var\(--(?:([\w-]+)|([\w-]+), ?([a-zA-Z\d ()%#.,-]+))\)/u;function Sk(t){const s=jk.exec(t);if(!s)return[,];const[,r,o,c]=s;return[`--${r??o}`,c]}function wg(t,s,r=1){const[o,c]=Sk(t);if(!o)return;const u=window.getComputedStyle(s).getPropertyValue(o);if(u){const h=u.trim();return Xc(h)?parseFloat(h):h}return Zc(c)?wg(c,s,r+1):c}function Qm(t){const s=[{},{}];return t==null||t.values.forEach((r,o)=>{s[0][o]=r.get(),s[1][o]=r.getVelocity()}),s}function du(t,s,r,o){if(typeof s=="function"){const[c,u]=Qm(o);s=s(r!==void 0?r:t.custom,c,u)}if(typeof s=="string"&&(s=t.variants&&t.variants[s]),typeof s=="function"){const[c,u]=Qm(o);s=s(r!==void 0?r:t.custom,c,u)}return s}function os(t,s,r){const o=t.getProps();return du(o,s,r!==void 0?r:o.custom,t)}const kg=new Set(["width","height","top","left","right","bottom",...Us]),Lc=t=>Array.isArray(t);function Nk(t,s,r){t.hasValue(s)?t.getValue(s).set(r):t.addValue(s,Os(r))}function Ck(t){return Lc(t)?t[t.length-1]||0:t}function Tk(t,s){const r=os(t,s);let{transitionEnd:o={},transition:c={},...u}=r||{};u={...u,...o};for(const h in u){const p=Ck(u[h]);Nk(t,h,p)}}const nt=t=>!!(t&&t.getVelocity);function Ak(t){return!!(nt(t)&&t.add)}function Ic(t,s){const r=t.getValue("willChange");if(Ak(r))return r.add(s);if(!r&&dn.WillChange){const o=new dn.WillChange("auto");t.addValue("willChange",o),o.add(s)}}function hu(t){return t.replace(/([A-Z])/g,s=>`-${s.toLowerCase()}`)}const Pk="framerAppearId",jg="data-"+hu(Pk);function Sg(t){return t.props[jg]}const Ek=typeof window<"u";function Mk({protectedKeys:t,needsAnimating:s},r){const o=t.hasOwnProperty(r)&&s[r]!==!0;return s[r]=!1,o}function Ng(t,s,{delay:r=0,transitionOverride:o,type:c}={}){let{transition:u,transitionEnd:h,...p}=s;const f=t.getDefaultTransition();u=u?bg(u,f):f;const v=u==null?void 0:u.reduceMotion,g=u==null?void 0:u.skipAnimations;o&&(u=o);const x=[],b=c&&t.animationState&&t.animationState.getState()[c],j=u==null?void 0:u.path;j&&j.animateVisualElement(t,p,u,r,x);for(const N in p){const w=t.getValue(N,t.latestValues[N]??null),S=p[N];if(S===void 0||b&&Mk(b,N))continue;const B={delay:r,...cu(u||{},N)};g&&(B.skipAnimations=!0);const P=w.get();if(P!==void 0&&!w.isAnimating()&&!Array.isArray(S)&&S===P&&!B.velocity){Ee.update(()=>w.set(S));continue}let D=!1;if(Ek&&window.MotionHandoffAnimation){const L=Sg(t);if(L){const I=window.MotionHandoffAnimation(L,N,Ee);I!==null&&(B.startTime=I,D=!0)}}Ic(t,N);const V=v??t.shouldReduceMotion;w.start(uu(N,w,S,V&&kg.has(N)?{type:!1}:B,t,D));const _=w.animation;_&&x.push(_)}if(h){const N=()=>Ee.update(()=>{h&&Tk(t,h)});x.length?Promise.all(x).then(N):N()}return x}function Vc(t,s,r={}){var f;const o=os(t,s,r.type==="exit"?(f=t.presenceContext)==null?void 0:f.custom:void 0);let{transition:c=t.getDefaultTransition()||{}}=o||{};r.transitionOverride&&(c=r.transitionOverride);const u=o?()=>Promise.all(Ng(t,o,r)):()=>Promise.resolve(),h=t.variantChildren&&t.variantChildren.size?(v=0)=>{const{delayChildren:g=0,staggerChildren:x,staggerDirection:b}=c;return _k(t,s,v,g,x,b,r)}:()=>Promise.resolve(),{when:p}=c;if(p){const[v,g]=p==="beforeChildren"?[u,h]:[h,u];return v().then(()=>g())}else return Promise.all([u(),h(r.delay)])}function _k(t,s,r=0,o=0,c=0,u=1,h){const p=[];for(const f of t.variantChildren)f.notify("AnimationStart",s),p.push(Vc(f,s,{...h,delay:r+(typeof o=="function"?0:o)+xg(t.variantChildren,f,o,c,u)}).then(()=>f.notify("AnimationComplete",s)));return Promise.all(p)}function Dk(t,s,r={}){t.notify("AnimationStart",s);let o;if(Array.isArray(s)){const c=s.map(u=>Vc(t,u,r));o=Promise.all(c)}else if(typeof s=="string")o=Vc(t,s,r);else{const c=typeof s=="function"?os(t,s,r.custom):s;o=Promise.all(Ng(t,c,r))}return o.then(()=>{t.notify("AnimationComplete",s)})}const Rk={test:t=>t==="auto",parse:t=>t},Lk=t=>s=>s.test(t),Ik=[zs,re,en,un,Xb,qb,Rk],Jm=t=>Ik.find(Lk(t));function Vk(t){return typeof t=="number"?t===0:t!==null?t==="none"||t==="0"||Yc(t):!0}const Fk=new Set(["auto","none","0"]);function Bk(t,s,r){let o=0,c;for(;o<t.length&&!c;){const u=t[o];typeof u=="string"&&!Fk.has(u)&&tw(u)&&(c=t[o]),o++}if(c&&r)for(const u of s)t[u]!==c&&(t[u]=ou(r,c))}class Ok extends lu{constructor(s,r,o,c,u){super(s,r,o,c,u,!0)}readKeyframes(){const{unresolvedKeyframes:s,element:r,name:o}=this;if(!r||!r.current)return;super.readKeyframes();for(let g=0;g<s.length;g++){let x=s[g];if(typeof x=="string"&&(x=x.trim(),Zc(x))){const b=wg(x,r.current);b!==void 0&&(s[g]=b),g===s.length-1&&(this.finalKeyframe=x)}}if(this.resolveNoneKeyframes(),!kg.has(o)||s.length!==2)return;const[c,u]=s;if(typeof c=="number"&&typeof u=="number")return;const h=Jm(c),p=Jm(u),f=Lm(c),v=Lm(u);if(f!==v&&rs[o]){this.needsMeasurement=!0;return}if(h!==p)if(Hm(h)&&Hm(p))for(let g=0;g<s.length;g++){const x=s[g];typeof x=="string"&&(s[g]=parseFloat(x))}else rs[o]&&(this.needsMeasurement=!0)}resolveNoneKeyframes(){const{unresolvedKeyframes:s,name:r}=this,o=[];for(let c=0;c<s.length;c++)(s[c]===null||Vk(s[c]))&&o.push(c);o.length&&Bk(s,o,r)}measure(){const{element:s,name:r}=this;return rs[r](window.getComputedStyle(s.current),()=>s.measureViewportBox())}measureInitialState(){var u;const{element:s,unresolvedKeyframes:r,name:o}=this;if(!s||!s.current)return;o==="height"&&(this.suspendedScrollY=window.pageYOffset),this.measuredOrigin=this.measure(),r[0]=this.measuredOrigin;const c=r[r.length-1];c!==void 0&&((u=this.motionValue)==null||u.jump(c,!1))}measureEndState(){var u,h;const{element:s,unresolvedKeyframes:r}=this;if(!s||!s.current)return;(u=this.motionValue)==null||u.jump(this.measuredOrigin,!1);const o=r.length-1,c=r[o];r[o]=this.measure(),c!==null&&this.finalKeyframe===void 0&&(this.finalKeyframe=c),(h=this.removedTransforms)!=null&&h.length&&this.removedTransforms.forEach(([p,f])=>{s.getValue(p).set(f)}),this.resolveNoneKeyframes()}}const mu=["borderTopLeftRadius","borderTopRightRadius","borderBottomRightRadius","borderBottomLeftRadius"];function zk(t){return Rf(t)&&"offsetHeight"in t&&!("ownerSVGElement"in t)}function pu(t){return Rf(t)&&"ownerSVGElement"in t}const Fc=(t,s)=>s&&typeof t=="number"?s.transform(t):t;function Cg(t,s,r){if(t==null)return[];if(t instanceof EventTarget)return[t];if(typeof t=="string"){let o=document;const c=(r==null?void 0:r[t])??o.querySelectorAll(t);return c?Array.from(c):[]}return Array.from(t).filter(o=>o!=null)}const Uk={x:"translateX",y:"translateY",z:"translateZ",transformPerspective:"perspective"},$k=Us.length;function Wk(t,s,r){let o="",c=!0;for(let h=0;h<$k;h++){const p=Us[h],f=t[p];if(f===void 0)continue;let v=!0;if(typeof f=="number")v=f===(p.startsWith("scale")?1:0);else{const g=parseFloat(f);v=p.startsWith("scale")?g===1:g===0}if(!v||r){const g=Fc(f,Ta[p]);if(!v){c=!1;const x=Uk[p]||p;o+=`${x}(${g}) `}r&&(s[p]=g)}}const u=t.pathRotation;return u&&(c=!1,o+=`rotate(${Fc(u,Ta.pathRotation)}) `),o=o.trim(),r?o=r(s,c?"":o):c&&(o="none"),o}function fu(t,s,r){const{style:o,vars:c,transformOrigin:u}=t;let h=!1,p=!1;for(const f in s){const v=s[f];if($s.has(f)){h=!0;continue}else if(Xf(f)){c[f]=v;continue}else{const g=Fc(v,Ta[f]);f.startsWith("origin")?(p=!0,u[f]=g):o[f]=g}}if(s.transform||(h||r?o.transform=Wk(s,t.transform,r):o.transform&&(o.transform="none")),p){const{originX:f="50%",originY:v="50%",originZ:g=0}=u;o.transformOrigin=`${f} ${v} ${g}`}}const Hk={offset:"stroke-dashoffset",array:"stroke-dasharray"},Gk={offset:"strokeDashoffset",array:"strokeDasharray"};function Kk(t,s,r=1,o=0,c=!0){t.pathLength=1;const u=c?Hk:Gk;t[u.offset]=`${-o}`,t[u.array]=`${s} ${r}`}const Tg=["transform","opacity","offsetDistance","offsetPath","offsetRotate","offsetAnchor"];function Ag(t,{attrX:s,attrY:r,attrScale:o,pathLength:c,pathSpacing:u=1,pathOffset:h=0,...p},f,v,g){if(fu(t,p,v),f){t.style.viewBox&&(t.attrs.viewBox=t.style.viewBox);return}t.attrs=t.style,t.style={};const{attrs:x,style:b}=t;for(const j of Tg)x[j]!==void 0&&(b[j]=x[j],delete x[j]);(b.transform||x.transformOrigin)&&(b.transformOrigin=x.transformOrigin??"50% 50%",delete x.transformOrigin),b.transform&&(b.transformBox=(g==null?void 0:g.transformBox)??"fill-box",delete x.transformBox),s!==void 0&&(x.x=s),r!==void 0&&(x.y=r),o!==void 0&&(x.scale=o),c!==void 0&&Kk(x,c,u,h,!1)}function Pg({top:t,left:s,right:r,bottom:o}){return{x:{min:s,max:r},y:{min:t,max:o}}}function qk({x:t,y:s}){return{top:s.min,right:t.max,bottom:s.max,left:t.min}}function Xk(t,s){if(!s)return t;const r=s({x:t.left,y:t.top}),o=s({x:t.right,y:t.bottom});return{top:r.y,left:r.x,bottom:o.y,right:o.x}}function Zl(t){return t===void 0||t===1}function Bc({scale:t,scaleX:s,scaleY:r}){return!Zl(t)||!Zl(s)||!Zl(r)}function Zn(t){return Bc(t)||Eg(t)||t.z||t.rotate||t.rotateX||t.rotateY||t.skewX||t.skewY}function Eg(t){return Zm(t.x)||Zm(t.y)}function Zm(t){return t&&t!=="0%"}function Aa(t,s,r){const o=t-r,c=s*o;return r+c}function ep(t,s,r,o,c){return c!==void 0&&(t=Aa(t,c,o)),Aa(t,r,o)+s}function Oc(t,s=0,r=1,o,c){t.min=ep(t.min,s,r,o,c),t.max=ep(t.max,s,r,o,c)}function Mg(t,{x:s,y:r}){Oc(t.x,s.translate,s.scale,s.originPoint),Oc(t.y,r.translate,r.scale,r.originPoint)}const tp=.999999999999,np=1.0000000000001;function Yk(t,s,r,o=!1){var p;const c=r.length;if(!c)return;s.x=s.y=1;let u,h;for(let f=0;f<c;f++){u=r[f],h=u.projectionDelta;const{visualElement:v}=u.options;v&&v.props.style&&v.props.style.display==="contents"||(o&&u.options.layoutScroll&&u.scroll&&u!==u.root&&(Jt(t.x,-u.scroll.offset.x),Jt(t.y,-u.scroll.offset.y)),h&&(s.x*=h.x.scale,s.y*=h.y.scale,Mg(t,h)),o&&Zn(u.latestValues)&&da(t,u.latestValues,(p=u.layout)==null?void 0:p.layoutBox))}s.x<np&&s.x>tp&&(s.x=1),s.y<np&&s.y>tp&&(s.y=1)}function Jt(t,s){t.min+=s,t.max+=s}function sp(t,s,r,o,c=.5){const u=Pe(t.min,t.max,c);Oc(t,s,r,u,o)}function ip(t,s){return typeof t=="string"?parseFloat(t)/100*(s.max-s.min):t}function da(t,s,r){const o=r??t;sp(t.x,ip(s.x,o.x),s.scaleX,s.scale,s.originX),sp(t.y,ip(s.y,o.y),s.scaleY,s.scale,s.originY)}function _g(t,s){return Pg(Xk(t.getBoundingClientRect(),s))}function Qk(t,s,r){const o=_g(t,r),{scroll:c}=s;return c&&(Jt(o.x,c.offset.x),Jt(o.y,c.offset.y)),o}const{schedule:gu}=Kf(queueMicrotask,!1),Ut={x:!1,y:!1};function Dg(){return Ut.x||Ut.y}function Jk(t){return t==="x"||t==="y"?Ut[t]?null:(Ut[t]=!0,()=>{Ut[t]=!1}):Ut.x||Ut.y?null:(Ut.x=Ut.y=!0,()=>{Ut.x=Ut.y=!1})}function Rg(t,s){const r=Cg(t),o=new AbortController,c={passive:!0,...s,signal:o.signal};return[r,c,()=>o.abort()]}function Zk(t){return!(t.pointerType==="touch"||Dg())}function e0(t,s,r={}){const[o,c,u]=Rg(t,r);return o.forEach(h=>{let p=!1,f=!1,v;const g=()=>{h.removeEventListener("pointerleave",N)},x=S=>{v&&(v(S),v=void 0),g()},b=S=>{p=!1,window.removeEventListener("pointerup",b),window.removeEventListener("pointercancel",b),f&&(f=!1,x(S))},j=()=>{p=!0,window.addEventListener("pointerup",b,c),window.addEventListener("pointercancel",b,c)},N=S=>{if(S.pointerType!=="touch"){if(p){f=!0;return}x(S)}},w=S=>{if(!Zk(S))return;f=!1;const B=s(h,S);typeof B=="function"&&(v=B,h.addEventListener("pointerleave",N,c))};h.addEventListener("pointerenter",w,c),h.addEventListener("pointerdown",j,c)}),u}const Lg=(t,s)=>s?t===s?!0:Lg(t,s.parentElement):!1,yu=t=>t.pointerType==="mouse"?typeof t.button!="number"||t.button<=0:t.isPrimary!==!1,t0=new Set(["BUTTON","INPUT","SELECT","TEXTAREA","A"]);function n0(t){return t0.has(t.tagName)||t.isContentEditable===!0}const s0=new Set(["INPUT","SELECT","TEXTAREA"]);function i0(t){return s0.has(t.tagName)||t.isContentEditable===!0}const ha=new WeakSet;function rp(t){return s=>{s.key==="Enter"&&t(s)}}function ec(t,s){t.dispatchEvent(new PointerEvent("pointer"+s,{isPrimary:!0,bubbles:!0}))}const r0=(t,s)=>{const r=t.currentTarget;if(!r)return;const o=rp(()=>{if(ha.has(r))return;ec(r,"down");const c=rp(()=>{ec(r,"up")}),u=()=>ec(r,"cancel");r.addEventListener("keyup",c,s),r.addEventListener("blur",u,s)});r.addEventListener("keydown",o,s),r.addEventListener("blur",()=>r.removeEventListener("keydown",o),s)};function ap(t){return yu(t)&&!Dg()}const op=new WeakSet;function a0(t,s,r={}){const[o,c,u]=Rg(t,r),h=p=>{const f=p.currentTarget;if(!ap(p)||op.has(p))return;ha.add(f),r.stopPropagation&&op.add(p);const v=s(f,p),g={...c,capture:!0},x=(N,w)=>{window.removeEventListener("pointerup",b,g),window.removeEventListener("pointercancel",j,g),ha.has(f)&&ha.delete(f),ap(N)&&typeof v=="function"&&v(N,{success:w})},b=N=>{x(N,f===window||f===document||r.useGlobalTarget||Lg(f,N.target))},j=N=>{x(N,!1)};window.addEventListener("pointerup",b,g),window.addEventListener("pointercancel",j,g)};return o.forEach(p=>{(r.useGlobalTarget?window:p).addEventListener("pointerdown",h,c),zk(p)&&(p.addEventListener("focus",v=>r0(v,c)),!n0(p)&&!p.hasAttribute("tabindex")&&(p.tabIndex=0))}),u}const ma=new WeakMap;let _n;const Ig=(t,s,r)=>(o,c)=>c&&c[0]?c[0][t+"Size"]:pu(o)&&"getBBox"in o?o.getBBox()[s]:o[r],o0=Ig("inline","width","offsetWidth"),l0=Ig("block","height","offsetHeight");function c0({target:t,borderBoxSize:s}){var r;(r=ma.get(t))==null||r.forEach(o=>{o(t,{get width(){return o0(t,s)},get height(){return l0(t,s)}})})}function u0(t){t.forEach(c0)}function d0(){typeof ResizeObserver>"u"||(_n=new ResizeObserver(u0))}function h0(t,s){_n||d0();const r=Cg(t);return r.forEach(o=>{let c=ma.get(o);c||(c=new Set,ma.set(o,c)),c.add(s),_n==null||_n.observe(o)}),()=>{r.forEach(o=>{const c=ma.get(o);c==null||c.delete(s),c!=null&&c.size||_n==null||_n.unobserve(o)})}}const pa=new Set;let Vs;function m0(){Vs=()=>{const t={get width(){return window.innerWidth},get height(){return window.innerHeight}};pa.forEach(s=>s(t))},window.addEventListener("resize",Vs)}function p0(t){return pa.add(t),Vs||m0(),()=>{pa.delete(t),!pa.size&&typeof Vs=="function"&&(window.removeEventListener("resize",Vs),Vs=void 0)}}function lp(t,s){return typeof t=="function"?p0(t):h0(t,s)}function f0(t){return pu(t)&&t.tagName==="svg"}const cp=()=>({translate:0,scale:1,origin:0,originPoint:0}),Fs=()=>({x:cp(),y:cp()}),up=()=>({min:0,max:0}),qe=()=>({x:up(),y:up()}),g0=new WeakMap;function Ba(t){return t!==null&&typeof t=="object"&&typeof t.start=="function"}function Fi(t){return typeof t=="string"||Array.isArray(t)}const vu=["animate","whileInView","whileFocus","whileHover","whileTap","whileDrag","exit"],Pa=["initial",...vu];function Oa(t){if(Ba(t.animate))return!0;for(let s=0;s<Pa.length;s++)if(Fi(t[Pa[s]]))return!0;return!1}function Vg(t){return!!(Oa(t)||t.variants)}function y0(t,s,r){for(const o in s){const c=s[o],u=r[o];if(nt(c))t.addValue(o,c);else if(nt(u))t.addValue(o,Os(c,{owner:t}));else if(u!==c)if(t.hasValue(o)){const h=t.getValue(o);h.liveStyle===!0?h.jump(c):h.hasAnimated||h.set(c)}else{const h=t.getStaticValue(o);t.addValue(o,Os(h!==void 0?h:c,{owner:t}))}}for(const o in r)s[o]===void 0&&t.removeValue(o);return s}const Ea={current:null},xu={current:!1},v0=typeof window<"u";function Fg(){if(xu.current=!0,!!v0)if(window.matchMedia){const t=window.matchMedia("(prefers-reduced-motion)"),s=()=>Ea.current=t.matches;t.addEventListener("change",s),s()}else Ea.current=!1}const dp=["AnimationStart","AnimationComplete","Update","BeforeLayoutMeasure","LayoutMeasure","LayoutAnimationStart","LayoutAnimationComplete"];let Ma={};function Bg(t){Ma=t}function x0(){return Ma}class b0{scrapeMotionValuesFromProps(s,r,o){return{}}constructor({parent:s,props:r,presenceContext:o,reducedMotionConfig:c,skipAnimations:u,blockInitialAnimation:h,visualState:p},f={}){this.current=null,this.children=new Set,this.isVariantNode=!1,this.isControllingVariants=!1,this.shouldReduceMotion=null,this.shouldSkipAnimations=!1,this.values=new Map,this.KeyframeResolver=lu,this.features={},this.valueSubscriptions=new Map,this.prevMotionValues={},this.hasBeenMounted=!1,this.events={},this.propEventSubscriptions={},this.notifyUpdate=()=>this.notify("Update",this.latestValues),this.render=()=>{this.current&&(this.triggerBuild(),this.renderInstance(this.current,this.renderState,this.props.style,this.projection))},this.renderScheduledAt=0,this.scheduleRender=()=>{const j=ot.now();this.renderScheduledAt<j&&(this.renderScheduledAt=j,Ee.render(this.render,!1,!0))};const{latestValues:v,renderState:g}=p;this.latestValues=v,this.baseTarget={...v},this.initialValues=r.initial?{...v}:{},this.renderState=g,this.parent=s,this.props=r,this.presenceContext=o,this.depth=s?s.depth+1:0,this.reducedMotionConfig=c,this.skipAnimationsConfig=u,this.options=f,this.blockInitialAnimation=!!h,this.isControllingVariants=Oa(r),this.isVariantNode=Vg(r),this.isVariantNode&&(this.variantChildren=new Set),this.manuallyAnimateOnMount=!!(s&&s.current);const{willChange:x,...b}=this.scrapeMotionValuesFromProps(r,{},this);for(const j in b){const N=b[j];v[j]!==void 0&&nt(N)&&N.set(v[j])}}mount(s){var r,o;if(this.hasBeenMounted)for(const c in this.initialValues)(r=this.values.get(c))==null||r.jump(this.initialValues[c]),this.latestValues[c]=this.initialValues[c];this.current=s,g0.set(s,this),this.projection&&!this.projection.instance&&this.projection.mount(s),this.parent&&this.isVariantNode&&!this.isControllingVariants&&(this.removeFromVariantTree=this.parent.addVariantChild(this)),this.values.forEach((c,u)=>this.bindToMotionValue(u,c)),this.reducedMotionConfig==="never"?this.shouldReduceMotion=!1:this.reducedMotionConfig==="always"?this.shouldReduceMotion=!0:(xu.current||Fg(),this.shouldReduceMotion=Ea.current),this.shouldSkipAnimations=this.skipAnimationsConfig??!1,(o=this.parent)==null||o.addChild(this),this.update(this.props,this.presenceContext),this.hasBeenMounted=!0}unmount(){var s;this.projection&&this.projection.unmount(),Rn(this.notifyUpdate),Rn(this.render),this.valueSubscriptions.forEach(r=>r()),this.valueSubscriptions.clear(),this.removeFromVariantTree&&this.removeFromVariantTree(),(s=this.parent)==null||s.removeChild(this);for(const r in this.events)this.events[r].clear();for(const r in this.features){const o=this.features[r];o&&(o.unmount(),o.isMounted=!1)}this.current=null}addChild(s){this.children.add(s),this.enteringChildren??(this.enteringChildren=new Set),this.enteringChildren.add(s)}removeChild(s){this.children.delete(s),this.enteringChildren&&this.enteringChildren.delete(s)}bindToMotionValue(s,r){if(this.valueSubscriptions.has(s)&&this.valueSubscriptions.get(s)(),r.accelerate&&Rc.has(s)&&this.current instanceof HTMLElement){const{factory:h,keyframes:p,times:f,ease:v,duration:g}=r.accelerate,x=new yg({element:this.current,name:s,keyframes:p,times:f,ease:v,duration:Dt(g)}),b=h(x);this.valueSubscriptions.set(s,()=>{b(),x.cancel()});return}const o=$s.has(s);o&&this.onBindTransform&&this.onBindTransform();const c=r.on("change",h=>{this.latestValues[s]=h,this.props.onUpdate&&Ee.preRender(this.notifyUpdate),o&&this.projection&&(this.projection.isTransformDirty=!0),this.scheduleRender()});let u;typeof window<"u"&&window.MotionCheckAppearSync&&(u=window.MotionCheckAppearSync(this,s,r)),this.valueSubscriptions.set(s,()=>{c(),u&&u()})}sortNodePosition(s){return!this.current||!this.sortInstanceNodePosition||this.type!==s.type?0:this.sortInstanceNodePosition(this.current,s.current)}updateFeatures(){let s="animation";for(s in Ma){const r=Ma[s];if(!r)continue;const{isEnabled:o,Feature:c}=r;if(!this.features[s]&&c&&o(this.props)&&(this.features[s]=new c(this)),this.features[s]){const u=this.features[s];u.isMounted?u.update():(u.mount(),u.isMounted=!0)}}}triggerBuild(){this.build(this.renderState,this.latestValues,this.props)}measureViewportBox(){return this.current?this.measureInstanceViewportBox(this.current,this.props):qe()}getStaticValue(s){return this.latestValues[s]}setStaticValue(s,r){this.latestValues[s]=r}update(s,r){(s.transformTemplate||this.props.transformTemplate)&&this.scheduleRender(),this.prevProps=this.props,this.props=s,this.prevPresenceContext=this.presenceContext,this.presenceContext=r;for(let o=0;o<dp.length;o++){const c=dp[o];this.propEventSubscriptions[c]&&(this.propEventSubscriptions[c](),delete this.propEventSubscriptions[c]);const u="on"+c,h=s[u];h&&(this.propEventSubscriptions[c]=this.on(c,h))}this.prevMotionValues=y0(this,this.scrapeMotionValuesFromProps(s,this.prevProps||{},this),this.prevMotionValues),this.handleChildMotionValue&&this.handleChildMotionValue()}getProps(){return this.props}getVariant(s){return this.props.variants?this.props.variants[s]:void 0}getDefaultTransition(){return this.props.transition}getTransformPagePoint(){return this.props.transformPagePoint}getClosestVariantNode(){return this.isVariantNode?this:this.parent?this.parent.getClosestVariantNode():void 0}addVariantChild(s){const r=this.getClosestVariantNode();if(r)return r.variantChildren&&r.variantChildren.add(s),()=>r.variantChildren.delete(s)}addValue(s,r){const o=this.values.get(s);r!==o&&(o&&this.removeValue(s),this.bindToMotionValue(s,r),this.values.set(s,r),this.latestValues[s]=r.get())}removeValue(s){this.values.delete(s);const r=this.valueSubscriptions.get(s);r&&(r(),this.valueSubscriptions.delete(s)),delete this.latestValues[s],this.removeValueFromRenderState(s,this.renderState)}hasValue(s){return this.values.has(s)}getValue(s,r){if(this.props.values&&this.props.values[s])return this.props.values[s];let o=this.values.get(s);return o===void 0&&r!==void 0&&(o=Os(r===null?void 0:r,{owner:this}),this.addValue(s,o)),o}readValue(s,r){let o=this.latestValues[s]!==void 0||!this.current?this.latestValues[s]:this.getBaseTargetFromProps(this.props,s)??this.readValueFromInstance(this.current,s,this.options);return o!=null&&(typeof o=="string"&&(Xc(o)||Yc(o))?o=parseFloat(o):typeof o!="number"&&!St.test(o)&&St.test(r)&&(o=ou(s,r)),this.setBaseTarget(s,nt(o)?o.get():o)),nt(o)?o.get():o}setBaseTarget(s,r){this.baseTarget[s]=r}getBaseTarget(s){var u;const{initial:r}=this.props;let o;if(typeof r=="string"||typeof r=="object"){const h=du(this.props,r,(u=this.presenceContext)==null?void 0:u.custom);h&&(o=h[s])}if(r&&o!==void 0)return o;const c=this.getBaseTargetFromProps(this.props,s);return c!==void 0&&!nt(c)?c:this.initialValues[s]!==void 0&&o===void 0?void 0:this.baseTarget[s]}on(s,r){return this.events[s]||(this.events[s]=new ka),this.events[s].add(r)}notify(s,...r){this.events[s]&&this.events[s].notify(...r)}scheduleRenderMicrotask(){gu.render(this.render)}}class Og extends b0{constructor(){super(...arguments),this.KeyframeResolver=Ok}sortInstanceNodePosition(s,r){return s.compareDocumentPosition(r)&2?1:-1}getBaseTargetFromProps(s,r){const o=s.style;return o?o[r]:void 0}removeValueFromRenderState(s,{vars:r,style:o}){delete r[s],delete o[s]}handleChildMotionValue(){this.childSubscription&&(this.childSubscription(),delete this.childSubscription);const{children:s}=this.props;nt(s)&&(this.childSubscription=s.on("change",r=>{this.current&&(this.current.textContent=`${r}`)}))}}class In{constructor(s){this.isMounted=!1,this.node=s}update(){}}function zg(t,{style:s,vars:r},o,c){const u=t.style;let h;for(h in s)u[h]=s[h];c==null||c.applyProjectionStyles(u,o);for(h in r)u.setProperty(h,r[h])}function hp(t,s){return s.max===s.min?0:t/(s.max-s.min)*100}const Ei={correct:(t,s)=>{if(!s.target)return t;if(typeof t=="string")if(re.test(t))t=parseFloat(t);else return t;const r=hp(t,s.target.x),o=hp(t,s.target.y);return`${r}% ${o}%`}},w0={correct:(t,{treeScale:s,projectionDelta:r})=>{const o=t,c=St.parse(t);if(c.length>5)return o;const u=St.createTransformer(t),h=typeof c[0]!="number"?1:0,p=r.x.scale*s.x,f=r.y.scale*s.y;c[0+h]/=p,c[1+h]/=f;const v=Pe(p,f,.5);return typeof c[2+h]=="number"&&(c[2+h]/=v),typeof c[3+h]=="number"&&(c[3+h]/=v),u(c)}},zc={borderRadius:{...Ei,applyTo:[...mu]},borderTopLeftRadius:Ei,borderTopRightRadius:Ei,borderBottomLeftRadius:Ei,borderBottomRightRadius:Ei,boxShadow:w0};function Ug(t,{layout:s,layoutId:r}){return $s.has(t)||t.startsWith("origin")||(s||r!==void 0)&&(!!zc[t]||t==="opacity")}function bu(t,s,r){var h;const o=t.style,c=s==null?void 0:s.style,u={};if(!o)return u;for(const p in o)(nt(o[p])||c&&nt(c[p])||Ug(p,t)||((h=r==null?void 0:r.getValue(p))==null?void 0:h.liveStyle)!==void 0)&&(u[p]=o[p]);return u}function k0(t){return window.getComputedStyle(t)}class j0 extends Og{constructor(){super(...arguments),this.type="html",this.renderInstance=zg}mount(s){Va(!!s.style),super.mount(s)}readValueFromInstance(s,r){var o;if($s.has(r))return(o=this.projection)!=null&&o.isProjecting?Ac(r):Ww(s,r);{const c=k0(s),u=(Xf(r)?c.getPropertyValue(r):c[r])||0;return typeof u=="string"?u.trim():u}}measureInstanceViewportBox(s,{transformPagePoint:r}){return _g(s,r)}build(s,r,o){fu(s,r,o.transformTemplate)}scrapeMotionValuesFromProps(s,r,o){return bu(s,r,o)}}const $g=new Set(["baseFrequency","diffuseConstant","kernelMatrix","kernelUnitLength","keySplines","keyTimes","limitingConeAngle","markerHeight","markerWidth","numOctaves","targetX","targetY","surfaceScale","specularConstant","specularExponent","stdDeviation","tableValues","viewBox","gradientTransform","pathLength","startOffset","textLength","lengthAdjust"]),Wg=t=>typeof t=="string"&&t.toLowerCase()==="svg";function S0(t,s,r,o){zg(t,s,void 0,o);for(const c in s.attrs)t.setAttribute($g.has(c)?c:hu(c),s.attrs[c])}function Hg(t,s,r){const o=bu(t,s,r);for(const c in t)if(nt(t[c])||nt(s[c])){const u=Us.indexOf(c)!==-1?"attr"+c.charAt(0).toUpperCase()+c.substring(1):c;o[u]=t[c]}return o}class N0 extends Og{constructor(){super(...arguments),this.type="svg",this.isSVGTag=!1,this.measureInstanceViewportBox=qe}getBaseTargetFromProps(s,r){return s[r]}readValueFromInstance(s,r){if($s.has(r)){const o=cg(r);return o&&o.default||0}if(Tg.includes(r)){const c=getComputedStyle(s)[r];if(typeof c=="string"&&c)return c.trim()}return r=$g.has(r)?r:hu(r),s.getAttribute(r)}scrapeMotionValuesFromProps(s,r,o){return Hg(s,r,o)}build(s,r,o){Ag(s,r,this.isSVGTag,o.transformTemplate,o.style)}renderInstance(s,r,o,c){S0(s,r,o,c)}mount(s){this.isSVGTag=Wg(s.tagName),super.mount(s)}}const C0=Pa.length;function Gg(t){if(!t)return;if(!t.isControllingVariants){const r=t.parent?Gg(t.parent)||{}:{};return t.props.initial!==void 0&&(r.initial=t.props.initial),r}const s={};for(let r=0;r<C0;r++){const o=Pa[r],c=t.props[o];(Fi(c)||c===!1)&&(s[o]=c)}return s}function Kg(t,s){if(!Array.isArray(s))return!1;const r=s.length;if(r!==t.length)return!1;for(let o=0;o<r;o++)if(s[o]!==t[o])return!1;return!0}const T0=[...vu].reverse(),A0=vu.length;function P0(t){return s=>Promise.all(s.map(({animation:r,options:o})=>Dk(t,r,o)))}function E0(t){let s=P0(t),r=mp(),o=!0,c=!1;const u=v=>(g,x)=>{var j;const b=os(t,x,v==="exit"?(j=t.presenceContext)==null?void 0:j.custom:void 0);if(b){const{transition:N,transitionEnd:w,...S}=b;g={...g,...S,...w}}return g};function h(v){s=v(t)}function p(v){const{props:g}=t,x=Gg(t.parent)||{},b=[],j=new Set;let N={},w=1/0;for(let B=0;B<A0;B++){const P=T0[B],D=r[P],V=g[P]!==void 0?g[P]:x[P],_=Fi(V),L=P===v?D.isActive:null;L===!1&&(w=B);let I=V===x[P]&&V!==g[P]&&_;if(I&&(o||c)&&t.manuallyAnimateOnMount&&(I=!1),D.protectedKeys={...N},!D.isActive&&L===null||!V&&!D.prevProp||Ba(V)||typeof V=="boolean")continue;if(P==="exit"&&D.isActive&&L!==!0){D.prevResolvedValues&&(N={...N,...D.prevResolvedValues});continue}const U=M0(D.prevProp,V);let ce=U||P===v&&D.isActive&&!I&&_||B>w&&_,q=!1;const ge=Array.isArray(V)?V:[V];let he=ge.reduce(u(P),{});L===!1&&(he={});const{prevResolvedValues:Y={}}=D,we={...Y,...he},me=z=>{ce=!0,j.has(z)&&(q=!0,j.delete(z)),D.needsAnimating[z]=!0;const Z=t.getValue(z);Z&&(Z.liveStyle=!1)};for(const z in we){const Z=he[z],X=Y[z];if(N.hasOwnProperty(z))continue;let E=!1;Lc(Z)&&Lc(X)?E=!Kg(Z,X)||U:E=Z!==X,E?Z!=null?me(z):j.add(z):Z!==void 0&&j.has(z)?me(z):D.protectedKeys[z]=!0}D.prevProp=V,D.prevResolvedValues=he,D.isActive&&(N={...N,...he}),(o||c)&&t.blockInitialAnimation&&(ce=!1);const Ce=I&&U;ce&&(!Ce||q)&&b.push(...ge.map(z=>{const Z={type:P};if(typeof z=="string"&&(o||c)&&!Ce&&t.manuallyAnimateOnMount&&t.parent){const{parent:X}=t,E=os(X,z);if(X.enteringChildren&&E){const{delayChildren:$}=E.transition||{};Z.delay=xg(X.enteringChildren,t,$)}}return{animation:z,options:Z}}))}if(j.size){const B={};if(typeof g.initial!="boolean"){const P=os(t,Array.isArray(g.initial)?g.initial[0]:g.initial);P&&P.transition&&(B.transition=P.transition)}j.forEach(P=>{const D=t.getBaseTarget(P),V=t.getValue(P);V&&(V.liveStyle=!0),B[P]=D??null}),b.push({animation:B})}let S=!!b.length;return o&&(g.initial===!1||g.initial===g.animate)&&!t.manuallyAnimateOnMount&&(S=!1),o=!1,c=!1,S?s(b):Promise.resolve()}function f(v,g){var b;if(r[v].isActive===g)return Promise.resolve();(b=t.variantChildren)==null||b.forEach(j=>{var N;return(N=j.animationState)==null?void 0:N.setActive(v,g)}),r[v].isActive=g;const x=p(v);for(const j in r)r[j].protectedKeys={};return x}return{animateChanges:p,setActive:f,setAnimateFunction:h,getState:()=>r,reset:()=>{r=mp(),c=!0}}}function M0(t,s){return typeof s=="string"?s!==t:Array.isArray(s)?!Kg(s,t):!1}function Jn(t=!1){return{isActive:t,protectedKeys:{},needsAnimating:{},prevResolvedValues:{}}}function mp(){return{animate:Jn(!0),whileInView:Jn(),whileHover:Jn(),whileTap:Jn(),whileDrag:Jn(),whileFocus:Jn(),exit:Jn()}}function Uc(t,s){t.min=s.min,t.max=s.max}function zt(t,s){Uc(t.x,s.x),Uc(t.y,s.y)}function pp(t,s){t.translate=s.translate,t.scale=s.scale,t.originPoint=s.originPoint,t.origin=s.origin}const qg=1e-4,_0=1-qg,D0=1+qg,Xg=.01,R0=0-Xg,L0=0+Xg;function dt(t){return t.max-t.min}function I0(t,s,r){return Math.abs(t-s)<=r}function fp(t,s,r,o=.5){t.origin=o,t.originPoint=Pe(s.min,s.max,t.origin),t.scale=dt(r)/dt(s),t.translate=Pe(r.min,r.max,t.origin)-t.originPoint,(t.scale>=_0&&t.scale<=D0||isNaN(t.scale))&&(t.scale=1),(t.translate>=R0&&t.translate<=L0||isNaN(t.translate))&&(t.translate=0)}function Di(t,s,r,o){fp(t.x,s.x,r.x,o?o.originX:void 0),fp(t.y,s.y,r.y,o?o.originY:void 0)}function gp(t,s,r,o=0){const c=o?Pe(r.min,r.max,o):r.min;t.min=c+s.min,t.max=t.min+dt(s)}function V0(t,s,r,o){gp(t.x,s.x,r.x,o==null?void 0:o.x),gp(t.y,s.y,r.y,o==null?void 0:o.y)}function yp(t,s,r,o=0){const c=o?Pe(r.min,r.max,o):r.min;t.min=s.min-c,t.max=t.min+dt(s)}function _a(t,s,r,o){yp(t.x,s.x,r.x,o==null?void 0:o.x),yp(t.y,s.y,r.y,o==null?void 0:o.y)}function vp(t,s,r,o,c){return t-=s,t=Aa(t,1/r,o),c!==void 0&&(t=Aa(t,1/c,o)),t}function F0(t,s=0,r=1,o=.5,c,u=t,h=t){if(en.test(s)&&(s=parseFloat(s),s=Pe(h.min,h.max,s/100)-h.min),typeof s!="number")return;let p=Pe(u.min,u.max,o);t===u&&(p-=s),t.min=vp(t.min,s,r,p,c),t.max=vp(t.max,s,r,p,c)}function xp(t,s,[r,o,c],u,h){F0(t,s[r],s[o],s[c],s.scale,u,h)}const B0=["x","scaleX","originX"],O0=["y","scaleY","originY"];function bp(t,s,r,o){xp(t.x,s,B0,r?r.x:void 0,o?o.x:void 0),xp(t.y,s,O0,r?r.y:void 0,o?o.y:void 0)}function wp(t){return t.translate===0&&t.scale===1}function Yg(t){return wp(t.x)&&wp(t.y)}function kp(t,s){return t.min===s.min&&t.max===s.max}function z0(t,s){return kp(t.x,s.x)&&kp(t.y,s.y)}function jp(t,s){return Math.round(t.min)===Math.round(s.min)&&Math.round(t.max)===Math.round(s.max)}function Qg(t,s){return jp(t.x,s.x)&&jp(t.y,s.y)}function Sp(t){return dt(t.x)/dt(t.y)}function Np(t,s){return t.translate===s.translate&&t.scale===s.scale&&t.originPoint===s.originPoint}function Qt(t){return[t("x"),t("y")]}function U0(t,s,r){let o="";const c=t.x.translate/s.x,u=t.y.translate/s.y,h=(r==null?void 0:r.z)||0;if((c||u||h)&&(o=`translate3d(${c}px, ${u}px, ${h}px) `),(s.x!==1||s.y!==1)&&(o+=`scale(${1/s.x}, ${1/s.y}) `),r){const{transformPerspective:v,rotate:g,pathRotation:x,rotateX:b,rotateY:j,skewX:N,skewY:w}=r;v&&(o=`perspective(${v}px) ${o}`),g&&(o+=`rotate(${g}deg) `),x&&(o+=`rotate(${x}deg) `),b&&(o+=`rotateX(${b}deg) `),j&&(o+=`rotateY(${j}deg) `),N&&(o+=`skewX(${N}deg) `),w&&(o+=`skewY(${w}deg) `)}const p=t.x.scale*s.x,f=t.y.scale*s.y;return(p!==1||f!==1)&&(o+=`scale(${p}, ${f})`),o||"none"}const $0=mu.length,Cp=t=>typeof t=="string"?parseFloat(t):t,Tp=t=>typeof t=="number"||re.test(t);function W0(t,s,r,o,c,u){c?(t.opacity=Pe(0,r.opacity??1,H0(o)),t.opacityExit=Pe(s.opacity??1,0,G0(o))):u&&(t.opacity=Pe(s.opacity??1,r.opacity??1,o));for(let h=0;h<$0;h++){const p=mu[h];let f=Ap(s,p),v=Ap(r,p);if(f===void 0&&v===void 0)continue;f||(f=0),v||(v=0),f===0||v===0||Tp(f)===Tp(v)?(t[p]=Math.max(Pe(Cp(f),Cp(v),o),0),(en.test(v)||en.test(f))&&(t[p]+="%")):t[p]=v}(s.rotate||r.rotate)&&(t.rotate=Pe(s.rotate||0,r.rotate||0,o))}function Ap(t,s){return t[s]!==void 0?t[s]:t.borderRadius}const H0=Jg(0,.5,$f),G0=Jg(.5,.95,$t);function Jg(t,s,r){return o=>o<t?0:o>s?1:r(Li(t,s,o))}function K0(t,s,r){const o=nt(t)?t:Os(t);return o.start(uu("",o,s,r)),o.animation}function Bi(t,s,r,o={passive:!0}){return t.addEventListener(s,r,o),()=>t.removeEventListener(s,r,o)}const q0=(t,s)=>t.depth-s.depth;class X0{constructor(){this.children=[],this.isDirty=!1}add(s){qc(this.children,s),this.isDirty=!0}remove(s){wa(this.children,s),this.isDirty=!0}forEach(s){this.isDirty&&this.children.sort(q0),this.isDirty=!1,this.children.forEach(s)}}function Y0(t,s){const r=ot.now(),o=({timestamp:c})=>{const u=c-r;u>=s&&(Rn(o),t(u-s))};return Ee.setup(o,!0),()=>Rn(o)}function fa(t){return nt(t)?t.get():t}class Q0{constructor(){this.members=[]}add(s){qc(this.members,s);for(let r=this.members.length-1;r>=0;r--){const o=this.members[r];if(o===s||o===this.lead||o===this.prevLead)continue;const c=o.instance;(!c||c.isConnected===!1)&&!o.snapshot&&(wa(this.members,o),o.unmount())}s.scheduleRender()}remove(s){if(wa(this.members,s),s===this.prevLead&&(this.prevLead=void 0),s===this.lead){const r=this.members[this.members.length-1];r&&this.promote(r)}}relegate(s){var r;for(let o=this.members.indexOf(s)-1;o>=0;o--){const c=this.members[o];if(c.isPresent!==!1&&((r=c.instance)==null?void 0:r.isConnected)!==!1)return this.promote(c),!0}return!1}promote(s,r){var c;const o=this.lead;if(s!==o&&(this.prevLead=o,this.lead=s,s.show(),o)){o.updateSnapshot(),s.scheduleRender();const{layoutDependency:u}=o.options,{layoutDependency:h}=s.options;(u===void 0||u!==h)&&(s.resumeFrom=o,r&&(o.preserveOpacity=!0),o.snapshot&&(s.snapshot=o.snapshot,s.snapshot.latestValues=o.animationValues||o.latestValues),(c=s.root)!=null&&c.isUpdating&&(s.isLayoutDirty=!0)),s.options.crossfade===!1&&o.hide()}}exitAnimationComplete(){this.members.forEach(s=>{var r,o,c,u,h;(o=(r=s.options).onExitComplete)==null||o.call(r),(h=(c=s.resumingFrom)==null?void 0:(u=c.options).onExitComplete)==null||h.call(u)})}scheduleRender(){this.members.forEach(s=>s.instance&&s.scheduleRender(!1))}removeLeadSnapshot(){var s;(s=this.lead)!=null&&s.snapshot&&(this.lead.snapshot=void 0)}}const ga={hasAnimatedSinceResize:!0,hasEverUpdated:!1},tc=["","X","Y","Z"],J0=1e3;let Z0=0;function nc(t,s,r,o){const{latestValues:c}=s;c[t]&&(r[t]=c[t],s.setStaticValue(t,0),o&&(o[t]=0))}function Zg(t){if(t.hasCheckedOptimisedAppear=!0,t.root===t)return;const{visualElement:s}=t.options;if(!s)return;const r=Sg(s);if(window.MotionHasOptimisedAnimation(r,"transform")){const{layout:c,layoutId:u}=t.options;window.MotionCancelOptimisedAnimation(r,"transform",Ee,!(c||u))}const{parent:o}=t;o&&!o.hasCheckedOptimisedAppear&&Zg(o)}function ey({attachResizeListener:t,defaultParent:s,measureScroll:r,checkIsScrollRoot:o,resetTransform:c}){return class{constructor(h={},p=s==null?void 0:s()){this.id=Z0++,this.animationId=0,this.animationCommitId=0,this.children=new Set,this.options={},this.isTreeAnimating=!1,this.isAnimationBlocked=!1,this.isLayoutDirty=!1,this.isProjectionDirty=!1,this.isSharedProjectionDirty=!1,this.isTransformDirty=!1,this.updateManuallyBlocked=!1,this.updateBlockedByResize=!1,this.isUpdating=!1,this.isSVG=!1,this.needsReset=!1,this.shouldResetTransform=!1,this.hasCheckedOptimisedAppear=!1,this.treeScale={x:1,y:1},this.eventHandlers=new Map,this.hasTreeAnimated=!1,this.layoutVersion=0,this.updateScheduled=!1,this.scheduleUpdate=()=>this.update(),this.projectionUpdateScheduled=!1,this.checkUpdateFailed=()=>{this.isUpdating&&(this.isUpdating=!1,this.clearAllSnapshots())},this.updateProjection=()=>{this.projectionUpdateScheduled=!1,this.nodes.forEach(nj),this.nodes.forEach(lj),this.nodes.forEach(cj),this.nodes.forEach(sj)},this.resolvedRelativeTargetAt=0,this.linkedParentVersion=0,this.hasProjected=!1,this.isVisible=!0,this.animationProgress=0,this.sharedNodes=new Map,this.latestValues=h,this.root=p?p.root||p:this,this.path=p?[...p.path,p]:[],this.parent=p,this.depth=p?p.depth+1:0;for(let f=0;f<this.path.length;f++)this.path[f].shouldResetTransform=!0;this.root===this&&(this.nodes=new X0)}addEventListener(h,p){return this.eventHandlers.has(h)||this.eventHandlers.set(h,new ka),this.eventHandlers.get(h).add(p)}notifyListeners(h,...p){const f=this.eventHandlers.get(h);f&&f.notify(...p)}hasListeners(h){return this.eventHandlers.has(h)}mount(h){if(this.instance)return;this.isSVG=pu(h)&&!f0(h),this.instance=h;const{layoutId:p,layout:f,visualElement:v}=this.options;if(v&&!v.current&&v.mount(h),this.root.nodes.add(this),this.parent&&this.parent.children.add(this),this.root.hasTreeAnimated&&(f||p)&&(this.isLayoutDirty=!0),t){let g,x=0;const b=()=>this.root.updateBlockedByResize=!1;Ee.read(()=>{x=window.innerWidth}),t(h,()=>{const j=window.innerWidth;j!==x&&(x=j,this.root.updateBlockedByResize=!0,g&&g(),g=Y0(b,250),ga.hasAnimatedSinceResize&&(ga.hasAnimatedSinceResize=!1,this.nodes.forEach(Mp)))})}p&&this.root.registerSharedNode(p,this),this.options.animate!==!1&&v&&(p||f)&&this.addEventListener("didUpdate",({delta:g,hasLayoutChanged:x,hasRelativeLayoutChanged:b,layout:j})=>{if(this.isTreeAnimationBlocked()){this.target=void 0,this.relativeTarget=void 0;return}const N=this.options.transition||v.getDefaultTransition()||pj,{onLayoutAnimationStart:w,onLayoutAnimationComplete:S}=v.getProps(),B=!this.targetLayout||!Qg(this.targetLayout,j),P=!x&&b;if(this.options.layoutRoot||this.resumeFrom||P||x&&(B||!this.currentAnimation)){this.resumeFrom&&(this.resumingFrom=this.resumeFrom,this.resumingFrom.resumingFrom=void 0);const D={...cu(N,"layout"),onPlay:w,onComplete:S};(v.shouldReduceMotion||this.options.layoutRoot)&&(D.delay=0,D.type=!1),this.startAnimation(D),this.setAnimationOrigin(g,P,D.path)}else x||Mp(this),this.isLead()&&this.options.onExitComplete&&this.options.onExitComplete();this.targetLayout=j})}unmount(){this.options.layoutId&&this.willUpdate(),this.root.nodes.remove(this);const h=this.getStack();h&&h.remove(this),this.parent&&this.parent.children.delete(this),this.instance=void 0,this.eventHandlers.clear(),Rn(this.updateProjection)}blockUpdate(){this.updateManuallyBlocked=!0}unblockUpdate(){this.updateManuallyBlocked=!1}isUpdateBlocked(){return this.updateManuallyBlocked||this.updateBlockedByResize}isTreeAnimationBlocked(){return this.isAnimationBlocked||this.parent&&this.parent.isTreeAnimationBlocked()||!1}startUpdate(){this.isUpdateBlocked()||(this.isUpdating=!0,this.nodes&&this.nodes.forEach(uj),this.animationId++)}getTransformTemplate(){const{visualElement:h}=this.options;return h&&h.getProps().transformTemplate}willUpdate(h=!0){if(this.root.hasTreeAnimated=!0,this.root.isUpdateBlocked()){this.options.onExitComplete&&this.options.onExitComplete();return}if(window.MotionCancelOptimisedAnimation&&!this.hasCheckedOptimisedAppear&&Zg(this),!this.root.isUpdating&&this.root.startUpdate(),this.isLayoutDirty)return;this.isLayoutDirty=!0;for(let g=0;g<this.path.length;g++){const x=this.path[g];x.shouldResetTransform=!0,(typeof x.latestValues.x=="string"||typeof x.latestValues.y=="string")&&(x.isLayoutDirty=!0),x.updateScroll("snapshot"),x.options.layoutRoot&&x.willUpdate(!1)}const{layoutId:p,layout:f}=this.options;if(p===void 0&&!f)return;const v=this.getTransformTemplate();this.prevTransformTemplateValue=v?v(this.latestValues,""):void 0,this.updateSnapshot(),h&&this.notifyListeners("willUpdate")}update(){if(this.updateScheduled=!1,this.isUpdateBlocked()){const f=this.updateBlockedByResize;this.unblockUpdate(),this.updateBlockedByResize=!1,this.clearAllSnapshots(),f&&this.nodes.forEach(rj),this.nodes.forEach(Pp);return}if(this.animationId<=this.animationCommitId){this.nodes.forEach(Ep);return}this.animationCommitId=this.animationId,this.isUpdating?(this.isUpdating=!1,this.nodes.forEach(aj),this.nodes.forEach(oj),this.nodes.forEach(ej),this.nodes.forEach(tj)):this.nodes.forEach(Ep),this.clearAllSnapshots();const p=ot.now();Xe.delta=Wt(0,1e3/60,p-Xe.timestamp),Xe.timestamp=p,Xe.isProcessing=!0,Kl.update.process(Xe),Kl.preRender.process(Xe),Kl.render.process(Xe),Xe.isProcessing=!1}didUpdate(){this.updateScheduled||(this.updateScheduled=!0,gu.read(this.scheduleUpdate))}clearAllSnapshots(){this.nodes.forEach(ij),this.sharedNodes.forEach(dj)}scheduleUpdateProjection(){this.projectionUpdateScheduled||(this.projectionUpdateScheduled=!0,Ee.preRender(this.updateProjection,!1,!0))}scheduleCheckAfterUnmount(){Ee.postRender(()=>{this.isLayoutDirty?this.root.didUpdate():this.root.checkUpdateFailed()})}updateSnapshot(){this.snapshot||!this.instance||(this.snapshot=this.measure(),this.snapshot&&!dt(this.snapshot.measuredBox.x)&&!dt(this.snapshot.measuredBox.y)&&(this.snapshot=void 0))}updateLayout(){if(!this.instance||(this.updateScroll(),!(this.options.alwaysMeasureLayout&&this.isLead())&&!this.isLayoutDirty))return;if(this.resumeFrom&&!this.resumeFrom.instance)for(let f=0;f<this.path.length;f++)this.path[f].updateScroll();const h=this.layout;this.layout=this.measure(!1),this.layoutVersion++,this.layoutCorrected||(this.layoutCorrected=qe()),this.isLayoutDirty=!1,this.projectionDelta=void 0,this.notifyListeners("measure",this.layout.layoutBox);const{visualElement:p}=this.options;p&&p.notify("LayoutMeasure",this.layout.layoutBox,h?h.layoutBox:void 0)}updateScroll(h="measure"){let p=!!(this.options.layoutScroll&&this.instance);if(this.scroll&&this.scroll.animationId===this.root.animationId&&this.scroll.phase===h&&(p=!1),p&&this.instance){const f=o(this.instance);this.scroll={animationId:this.root.animationId,phase:h,isRoot:f,offset:r(this.instance),wasRoot:this.scroll?this.scroll.isRoot:f}}}resetTransform(){if(!c)return;const h=this.isLayoutDirty||this.shouldResetTransform||this.options.alwaysMeasureLayout,p=this.projectionDelta&&!Yg(this.projectionDelta),f=this.getTransformTemplate(),v=f?f(this.latestValues,""):void 0,g=v!==this.prevTransformTemplateValue;h&&this.instance&&(p||Zn(this.latestValues)||g)&&(c(this.instance,v),this.shouldResetTransform=!1,this.scheduleRender())}measure(h=!0){const p=this.measurePageBox();let f=this.removeElementScroll(p);return h&&(f=this.removeTransform(f)),fj(f),{animationId:this.root.animationId,measuredBox:p,layoutBox:f,latestValues:{},source:this.id}}measurePageBox(){var v;const{visualElement:h}=this.options;if(!h)return qe();const p=h.measureViewportBox();if(!(((v=this.scroll)==null?void 0:v.wasRoot)||this.path.some(gj))){const{scroll:g}=this.root;g&&(Jt(p.x,g.offset.x),Jt(p.y,g.offset.y))}return p}removeElementScroll(h){var f;const p=qe();if(zt(p,h),(f=this.scroll)!=null&&f.wasRoot)return p;for(let v=0;v<this.path.length;v++){const g=this.path[v],{scroll:x,options:b}=g;g!==this.root&&x&&b.layoutScroll&&(x.wasRoot&&zt(p,h),Jt(p.x,x.offset.x),Jt(p.y,x.offset.y))}return p}applyTransform(h,p=!1,f){var g,x;const v=f||qe();zt(v,h);for(let b=0;b<this.path.length;b++){const j=this.path[b];!p&&j.options.layoutScroll&&j.scroll&&j!==j.root&&(Jt(v.x,-j.scroll.offset.x),Jt(v.y,-j.scroll.offset.y)),Zn(j.latestValues)&&da(v,j.latestValues,(g=j.layout)==null?void 0:g.layoutBox)}return Zn(this.latestValues)&&da(v,this.latestValues,(x=this.layout)==null?void 0:x.layoutBox),v}removeTransform(h){var f;const p=qe();zt(p,h);for(let v=0;v<this.path.length;v++){const g=this.path[v];if(!Zn(g.latestValues))continue;let x;g.instance&&(Bc(g.latestValues)&&g.updateSnapshot(),x=qe(),zt(x,g.measurePageBox())),bp(p,g.latestValues,(f=g.snapshot)==null?void 0:f.layoutBox,x)}return Zn(this.latestValues)&&bp(p,this.latestValues),p}setTargetDelta(h){this.targetDelta=h,this.root.scheduleUpdateProjection(),this.isProjectionDirty=!0}setOptions(h){this.options={...this.options,...h,crossfade:h.crossfade!==void 0?h.crossfade:!0}}clearMeasurements(){this.scroll=void 0,this.layout=void 0,this.snapshot=void 0,this.prevTransformTemplateValue=void 0,this.targetDelta=void 0,this.target=void 0,this.isLayoutDirty=!1}forceRelativeParentToResolveTarget(){this.relativeParent&&this.relativeParent.resolvedRelativeTargetAt!==Xe.timestamp&&this.relativeParent.resolveTargetDelta(!0)}resolveTargetDelta(h=!1){var j;const p=this.getLead();this.isProjectionDirty||(this.isProjectionDirty=p.isProjectionDirty),this.isTransformDirty||(this.isTransformDirty=p.isTransformDirty),this.isSharedProjectionDirty||(this.isSharedProjectionDirty=p.isSharedProjectionDirty);const f=!!this.resumingFrom||this!==p;if(!(h||f&&this.isSharedProjectionDirty||this.isProjectionDirty||(j=this.parent)!=null&&j.isProjectionDirty||this.attemptToResolveRelativeTarget||this.root.updateBlockedByResize))return;const{layout:g,layoutId:x}=this.options;if(!this.layout||!(g||x))return;this.resolvedRelativeTargetAt=Xe.timestamp;const b=this.getClosestProjectingParent();b&&this.linkedParentVersion!==b.layoutVersion&&!b.options.layoutRoot&&this.removeRelativeTarget(),!this.targetDelta&&!this.relativeTarget&&(this.options.layoutAnchor!==!1&&b&&b.layout?this.createRelativeTarget(b,this.layout.layoutBox,b.layout.layoutBox):this.removeRelativeTarget()),!(!this.relativeTarget&&!this.targetDelta)&&(this.target||(this.target=qe(),this.targetWithTransforms=qe()),this.relativeTarget&&this.relativeTargetOrigin&&this.relativeParent&&this.relativeParent.target?(this.forceRelativeParentToResolveTarget(),V0(this.target,this.relativeTarget,this.relativeParent.target,this.options.layoutAnchor||void 0)):this.targetDelta?(this.resumingFrom?this.applyTransform(this.layout.layoutBox,!1,this.target):zt(this.target,this.layout.layoutBox),Mg(this.target,this.targetDelta)):zt(this.target,this.layout.layoutBox),this.attemptToResolveRelativeTarget&&(this.attemptToResolveRelativeTarget=!1,this.options.layoutAnchor!==!1&&b&&!!b.resumingFrom==!!this.resumingFrom&&!b.options.layoutScroll&&b.target&&this.animationProgress!==1?this.createRelativeTarget(b,this.target,b.target):this.relativeParent=this.relativeTarget=void 0))}getClosestProjectingParent(){if(!(!this.parent||Bc(this.parent.latestValues)||Eg(this.parent.latestValues)))return this.parent.isProjecting()?this.parent:this.parent.getClosestProjectingParent()}isProjecting(){return!!((this.relativeTarget||this.targetDelta||this.options.layoutRoot)&&this.layout)}createRelativeTarget(h,p,f){this.relativeParent=h,this.linkedParentVersion=h.layoutVersion,this.forceRelativeParentToResolveTarget(),this.relativeTarget=qe(),this.relativeTargetOrigin=qe(),_a(this.relativeTargetOrigin,p,f,this.options.layoutAnchor||void 0),zt(this.relativeTarget,this.relativeTargetOrigin)}removeRelativeTarget(){this.relativeParent=this.relativeTarget=void 0}calcProjection(){var N;const h=this.getLead(),p=!!this.resumingFrom||this!==h;let f=!0;if((this.isProjectionDirty||(N=this.parent)!=null&&N.isProjectionDirty)&&(f=!1),p&&(this.isSharedProjectionDirty||this.isTransformDirty)&&(f=!1),this.resolvedRelativeTargetAt===Xe.timestamp&&(f=!1),f)return;const{layout:v,layoutId:g}=this.options;if(this.isTreeAnimating=!!(this.parent&&this.parent.isTreeAnimating||this.currentAnimation||this.pendingAnimation),this.isTreeAnimating||(this.targetDelta=this.relativeTarget=void 0),!this.layout||!(v||g))return;zt(this.layoutCorrected,this.layout.layoutBox);const x=this.treeScale.x,b=this.treeScale.y;Yk(this.layoutCorrected,this.treeScale,this.path,p),h.layout&&!h.target&&(this.treeScale.x!==1||this.treeScale.y!==1)&&(h.target=h.layout.layoutBox,h.targetWithTransforms=qe());const{target:j}=h;if(!j){this.prevProjectionDelta&&(this.createProjectionDeltas(),this.scheduleRender());return}!this.projectionDelta||!this.prevProjectionDelta?this.createProjectionDeltas():(pp(this.prevProjectionDelta.x,this.projectionDelta.x),pp(this.prevProjectionDelta.y,this.projectionDelta.y)),Di(this.projectionDelta,this.layoutCorrected,j,this.latestValues),(this.treeScale.x!==x||this.treeScale.y!==b||!Np(this.projectionDelta.x,this.prevProjectionDelta.x)||!Np(this.projectionDelta.y,this.prevProjectionDelta.y))&&(this.hasProjected=!0,this.scheduleRender(),this.notifyListeners("projectionUpdate",j))}hide(){this.isVisible=!1}show(){this.isVisible=!0}scheduleRender(h=!0){var p;if((p=this.options.visualElement)==null||p.scheduleRender(),h){const f=this.getStack();f&&f.scheduleRender()}this.resumingFrom&&!this.resumingFrom.instance&&(this.resumingFrom=void 0)}createProjectionDeltas(){this.prevProjectionDelta=Fs(),this.projectionDelta=Fs(),this.projectionDeltaWithTransform=Fs()}setAnimationOrigin(h,p=!1,f){const v=this.snapshot,g=v?v.latestValues:{},x={...this.latestValues},b=Fs();(!this.relativeParent||!this.relativeParent.options.layoutRoot)&&(this.relativeTarget=this.relativeTargetOrigin=void 0),this.attemptToResolveRelativeTarget=!p;const j=qe(),N=v?v.source:void 0,w=this.layout?this.layout.source:void 0,S=N!==w,B=this.getStack(),P=!B||B.members.length<=1,D=!!(S&&!P&&this.options.crossfade===!0&&!this.path.some(mj));this.animationProgress=0;let V;const _=f==null?void 0:f.interpolateProjection(h);this.mixTargetDelta=L=>{const I=L/1e3,U=_==null?void 0:_(I);U?(b.x.translate=U.x,b.x.scale=Pe(h.x.scale,1,I),b.x.origin=h.x.origin,b.x.originPoint=h.x.originPoint,b.y.translate=U.y,b.y.scale=Pe(h.y.scale,1,I),b.y.origin=h.y.origin,b.y.originPoint=h.y.originPoint):(_p(b.x,h.x,I),_p(b.y,h.y,I)),this.setTargetDelta(b),this.relativeTarget&&this.relativeTargetOrigin&&this.layout&&this.relativeParent&&this.relativeParent.layout&&(_a(j,this.layout.layoutBox,this.relativeParent.layout.layoutBox,this.options.layoutAnchor||void 0),hj(this.relativeTarget,this.relativeTargetOrigin,j,I),V&&z0(this.relativeTarget,V)&&(this.isProjectionDirty=!1),V||(V=qe()),zt(V,this.relativeTarget)),S&&(this.animationValues=x,W0(x,g,this.latestValues,I,D,P)),U&&U.rotate!==void 0&&(this.animationValues||(this.animationValues=x),this.animationValues.pathRotation=U.rotate),this.root.scheduleUpdateProjection(),this.scheduleRender(),this.animationProgress=I},this.mixTargetDelta(this.options.layoutRoot?1e3:0)}startAnimation(h){var p,f,v;this.notifyListeners("animationStart"),(p=this.currentAnimation)==null||p.stop(),(v=(f=this.resumingFrom)==null?void 0:f.currentAnimation)==null||v.stop(),this.pendingAnimation&&(Rn(this.pendingAnimation),this.pendingAnimation=void 0),this.pendingAnimation=Ee.update(()=>{ga.hasAnimatedSinceResize=!0,this.motionValue||(this.motionValue=Os(0)),this.motionValue.jump(0,!1),this.currentAnimation=K0(this.motionValue,[0,1e3],{...h,velocity:0,isSync:!0,onUpdate:g=>{this.mixTargetDelta(g),h.onUpdate&&h.onUpdate(g)},onComplete:()=>{h.onComplete&&h.onComplete(),this.completeAnimation()}}),Dw(this.currentAnimation,this),this.resumingFrom&&(this.resumingFrom.currentAnimation=this.currentAnimation),this.pendingAnimation=void 0})}completeAnimation(){this.resumingFrom&&(this.resumingFrom.currentAnimation=void 0,this.resumingFrom.preserveOpacity=void 0);const h=this.getStack();h&&h.exitAnimationComplete(),this.resumingFrom=this.currentAnimation=this.animationValues=void 0,this.notifyListeners("animationComplete")}finishAnimation(){this.currentAnimation&&(this.mixTargetDelta&&this.mixTargetDelta(J0),this.currentAnimation.stop()),this.completeAnimation()}applyTransformsToTarget(){const h=this.getLead(),{targetWithTransforms:p,layout:f,latestValues:v}=h;let{target:g}=h;if(!(!p||!g||!f)){if(this!==h&&this.layout&&f&&ty(this.options.animationType,this.layout.layoutBox,f.layoutBox)){g=this.target||qe();const x=dt(this.layout.layoutBox.x);g.x.min=h.target.x.min,g.x.max=g.x.min+x;const b=dt(this.layout.layoutBox.y);g.y.min=h.target.y.min,g.y.max=g.y.min+b}zt(p,g),da(p,v),Di(this.projectionDeltaWithTransform,this.layoutCorrected,p,v)}}registerSharedNode(h,p){this.sharedNodes.has(h)||this.sharedNodes.set(h,new Q0),this.sharedNodes.get(h).add(p);const v=p.options.initialPromotionConfig;p.promote({transition:v?v.transition:void 0,preserveFollowOpacity:v&&v.shouldPreserveFollowOpacity?v.shouldPreserveFollowOpacity(p):void 0})}isLead(){const h=this.getStack();return h?h.lead===this:!0}getLead(){var p;const{layoutId:h}=this.options;return h?((p=this.getStack())==null?void 0:p.lead)||this:this}getPrevLead(){var p;const{layoutId:h}=this.options;return h?(p=this.getStack())==null?void 0:p.prevLead:void 0}getStack(){const{layoutId:h}=this.options;if(h)return this.root.sharedNodes.get(h)}promote({needsReset:h,transition:p,preserveFollowOpacity:f}={}){const v=this.getStack();v&&v.promote(this,f),h&&(this.projectionDelta=void 0,this.needsReset=!0),p&&this.setOptions({transition:p})}relegate(){const h=this.getStack();return h?h.relegate(this):!1}resetSkewAndRotation(){const{visualElement:h}=this.options;if(!h)return;let p=!1;const{latestValues:f}=h;if((f.z||f.rotate||f.rotateX||f.rotateY||f.rotateZ||f.skewX||f.skewY)&&(p=!0),!p)return;const v={};f.z&&nc("z",h,v,this.animationValues);for(let g=0;g<tc.length;g++)nc(`rotate${tc[g]}`,h,v,this.animationValues),nc(`skew${tc[g]}`,h,v,this.animationValues);h.render();for(const g in v)h.setStaticValue(g,v[g]),this.animationValues&&(this.animationValues[g]=v[g]);h.scheduleRender()}applyProjectionStyles(h,p){if(!this.instance||this.isSVG)return;if(!this.isVisible){h.visibility="hidden";return}const f=this.getTransformTemplate();if(this.needsReset){this.needsReset=!1,h.visibility="",h.opacity="",h.pointerEvents=fa(p==null?void 0:p.pointerEvents)||"",h.transform=f?f(this.latestValues,""):"none";return}const v=this.getLead();if(!this.projectionDelta||!this.layout||!v.target){this.options.layoutId&&(h.opacity=this.latestValues.opacity!==void 0?this.latestValues.opacity:1,h.pointerEvents=fa(p==null?void 0:p.pointerEvents)||""),this.hasProjected&&!Zn(this.latestValues)&&(h.transform=f?f({},""):"none",this.hasProjected=!1);return}h.visibility="";const g=v.animationValues||v.latestValues;this.applyTransformsToTarget();let x=U0(this.projectionDeltaWithTransform,this.treeScale,g);f&&(x=f(g,x)),h.transform=x;const{x:b,y:j}=this.projectionDelta;h.transformOrigin=`${b.origin*100}% ${j.origin*100}% 0`,v.animationValues?h.opacity=v===this?g.opacity??this.latestValues.opacity??1:this.preserveOpacity?this.latestValues.opacity:g.opacityExit:h.opacity=v===this?g.opacity!==void 0?g.opacity:"":g.opacityExit!==void 0?g.opacityExit:0;for(const N in zc){if(g[N]===void 0)continue;const{correct:w,applyTo:S,isCSSVariable:B}=zc[N],P=x==="none"?g[N]:w(g[N],v);if(S){const D=S.length;for(let V=0;V<D;V++)h[S[V]]=P}else B?this.options.visualElement.renderState.vars[N]=P:h[N]=P}this.options.layoutId&&(h.pointerEvents=v===this?fa(p==null?void 0:p.pointerEvents)||"":"none")}clearSnapshot(){this.resumeFrom=this.snapshot=void 0}resetTree(){this.root.nodes.forEach(h=>{var p;return(p=h.currentAnimation)==null?void 0:p.stop()}),this.root.nodes.forEach(Pp),this.root.sharedNodes.clear()}}}function ej(t){t.updateLayout()}function tj(t){var r;const s=((r=t.resumeFrom)==null?void 0:r.snapshot)||t.snapshot;if(t.isLead()&&t.layout&&s&&t.hasListeners("didUpdate")){const{layoutBox:o,measuredBox:c}=t.layout,{animationType:u}=t.options,h=s.source!==t.layout.source;if(u==="size")Qt(x=>{const b=h?s.measuredBox[x]:s.layoutBox[x],j=dt(b);b.min=o[x].min,b.max=b.min+j});else if(u==="x"||u==="y"){const x=u==="x"?"y":"x";Uc(h?s.measuredBox[x]:s.layoutBox[x],o[x])}else ty(u,s.layoutBox,o)&&Qt(x=>{const b=h?s.measuredBox[x]:s.layoutBox[x],j=dt(o[x]);b.max=b.min+j,t.relativeTarget&&!t.currentAnimation&&(t.isProjectionDirty=!0,t.relativeTarget[x].max=t.relativeTarget[x].min+j)});const p=Fs();Di(p,o,s.layoutBox);const f=Fs();h?Di(f,t.applyTransform(c,!0),s.measuredBox):Di(f,o,s.layoutBox);const v=!Yg(p);let g=!1;if(!t.resumeFrom){const x=t.getClosestProjectingParent();if(x&&!x.resumeFrom){const{snapshot:b,layout:j}=x;if(b&&j){const N=t.options.layoutAnchor||void 0,w=qe();_a(w,s.layoutBox,b.layoutBox,N);const S=qe();_a(S,o,j.layoutBox,N),Qg(w,S)||(g=!0),x.options.layoutRoot&&(t.relativeTarget=S,t.relativeTargetOrigin=w,t.relativeParent=x)}}}t.notifyListeners("didUpdate",{layout:o,snapshot:s,delta:f,layoutDelta:p,hasLayoutChanged:v,hasRelativeLayoutChanged:g})}else if(t.isLead()){const{onExitComplete:o}=t.options;o&&o()}t.options.transition=void 0}function nj(t){t.parent&&(t.isProjecting()||(t.isProjectionDirty=t.parent.isProjectionDirty),t.isSharedProjectionDirty||(t.isSharedProjectionDirty=!!(t.isProjectionDirty||t.parent.isProjectionDirty||t.parent.isSharedProjectionDirty)),t.isTransformDirty||(t.isTransformDirty=t.parent.isTransformDirty))}function sj(t){t.isProjectionDirty=t.isSharedProjectionDirty=t.isTransformDirty=!1}function ij(t){t.clearSnapshot()}function Pp(t){t.clearMeasurements()}function rj(t){t.isLayoutDirty=!0,t.updateLayout()}function Ep(t){t.isLayoutDirty=!1}function aj(t){t.isAnimationBlocked&&t.layout&&!t.isLayoutDirty&&(t.snapshot=t.layout,t.isLayoutDirty=!0)}function oj(t){const{visualElement:s}=t.options;s&&s.getProps().onBeforeLayoutMeasure&&s.notify("BeforeLayoutMeasure"),t.resetTransform()}function Mp(t){t.finishAnimation(),t.targetDelta=t.relativeTarget=t.target=void 0,t.isProjectionDirty=!0}function lj(t){t.resolveTargetDelta()}function cj(t){t.calcProjection()}function uj(t){t.resetSkewAndRotation()}function dj(t){t.removeLeadSnapshot()}function _p(t,s,r){t.translate=Pe(s.translate,0,r),t.scale=Pe(s.scale,1,r),t.origin=s.origin,t.originPoint=s.originPoint}function Dp(t,s,r,o){t.min=Pe(s.min,r.min,o),t.max=Pe(s.max,r.max,o)}function hj(t,s,r,o){Dp(t.x,s.x,r.x,o),Dp(t.y,s.y,r.y,o)}function mj(t){return t.animationValues&&t.animationValues.opacityExit!==void 0}const pj={duration:.45,ease:[.4,0,.1,1]},Rp=t=>typeof navigator<"u"&&navigator.userAgent&&navigator.userAgent.toLowerCase().includes(t),Lp=Rp("applewebkit/")&&!Rp("chrome/")?Math.round:$t;function Ip(t){t.min=Lp(t.min),t.max=Lp(t.max)}function fj(t){Ip(t.x),Ip(t.y)}function ty(t,s,r){return t==="position"||t==="preserve-aspect"&&!I0(Sp(s),Sp(r),.2)}function gj(t){var s;return t!==t.root&&((s=t.scroll)==null?void 0:s.wasRoot)}const yj=ey({attachResizeListener:(t,s)=>Bi(t,"resize",s),measureScroll:()=>{var t,s;return{x:document.documentElement.scrollLeft||((t=document.body)==null?void 0:t.scrollLeft)||0,y:document.documentElement.scrollTop||((s=document.body)==null?void 0:s.scrollTop)||0}},checkIsScrollRoot:()=>!0}),sc={current:void 0},ny=ey({measureScroll:t=>({x:t.scrollLeft,y:t.scrollTop}),defaultParent:()=>{if(!sc.current){const t=new yj({});t.mount(window),t.setOptions({layoutScroll:!0}),sc.current=t}return sc.current},resetTransform:(t,s)=>{t.style.transform=s!==void 0?s:"none"},checkIsScrollRoot:t=>window.getComputedStyle(t).position==="fixed"}),sy=T.createContext({transformPagePoint:t=>t,isStatic:!1,reducedMotion:"never"});function vj(t=!0){const s=T.useContext(Kc);if(s===null)return[!0,null];const{isPresent:r,onExitComplete:o,register:c}=s,u=T.useId();T.useEffect(()=>{if(t)return c(u)},[t]);const h=T.useCallback(()=>t&&o&&o(u),[u,o,t]);return!r&&o?[!1,h]:[!0]}const iy=T.createContext({strict:!1}),Vp={animation:["animate","variants","whileHover","whileTap","exit","whileInView","whileFocus","whileDrag"],exit:["exit"],drag:["drag","dragControls"],focus:["whileFocus"],hover:["whileHover","onHoverStart","onHoverEnd"],tap:["whileTap","onTap","onTapStart","onTapCancel"],pan:["onPan","onPanStart","onPanSessionStart","onPanEnd"],inView:["whileInView","onViewportEnter","onViewportLeave"],layout:["layout","layoutId"]};let Fp=!1;function xj(){if(Fp)return;const t={};for(const s in Vp)t[s]={isEnabled:r=>Vp[s].some(o=>!!r[o])};Bg(t),Fp=!0}function ry(){return xj(),x0()}function bj(t){const s=ry();for(const r in t)s[r]={...s[r],...t[r]};Bg(s)}const za=T.createContext({});function wj(t,s){if(Oa(t)){const{initial:r,animate:o}=t;return{initial:r===!1||Fi(r)?r:void 0,animate:Fi(o)?o:void 0}}return t.inherit!==!1?s:{}}function kj(t){const{initial:s,animate:r}=wj(t,T.useContext(za));return T.useMemo(()=>({initial:s,animate:r}),[Bp(s),Bp(r)])}function Bp(t){return Array.isArray(t)?t.join(" "):t}const wu=()=>({style:{},transform:{},transformOrigin:{},vars:{}});function ay(t,s,r){for(const o in s)!nt(s[o])&&!Ug(o,r)&&(t[o]=s[o])}function jj({transformTemplate:t},s){return T.useMemo(()=>{const r=wu();return fu(r,s,t),Object.assign({},r.vars,r.style)},[s])}function Sj(t,s){const r=t.style||{},o={};return ay(o,r,t),Object.assign(o,jj(t,s)),o}function Nj(t,s){const r={},o=Sj(t,s);return t.drag&&t.dragListener!==!1&&(r.draggable=!1,o.userSelect=o.WebkitUserSelect=o.WebkitTouchCallout="none",o.touchAction=t.drag===!0?"none":`pan-${t.drag==="x"?"y":"x"}`),t.tabIndex===void 0&&(t.onTap||t.onTapStart||t.whileTap)&&(r.tabIndex=0),r.style=o,r}const oy=()=>({...wu(),attrs:{}});function Cj(t,s,r,o){const c=T.useMemo(()=>{const u=oy();return Ag(u,s,Wg(o),t.transformTemplate,t.style),{...u.attrs,style:{...u.style}}},[s]);if(t.style){const u={};ay(u,t.style,t),c.style={...u,...c.style}}return c}const Tj=new Set(["animate","exit","variants","initial","style","values","variants","transition","transformTemplate","custom","inherit","onBeforeLayoutMeasure","onAnimationStart","onAnimationComplete","onUpdate","onDragStart","onDrag","onDragEnd","onMeasureDragConstraints","onDirectionLock","onDragTransitionEnd","_dragX","_dragY","onHoverStart","onHoverEnd","onViewportEnter","onViewportLeave","globalTapTarget","propagate","ignoreStrict","viewport"]);function Da(t){return t.startsWith("while")||t.startsWith("drag")&&t!=="draggable"||t.startsWith("layout")||t.startsWith("onTap")||t.startsWith("onPan")||t.startsWith("onLayout")||Tj.has(t)}function Aj(t,s){return t.startsWith("on")?!Da(t):(s==null?void 0:s(t))??!Da(t)}function Pj(t,s,r,o){const c={};for(const u in t)u==="values"&&typeof t.values=="object"||nt(t[u])||(Aj(u,o)||r===!0&&Da(u)||!s&&!Da(u)||t.draggable&&u.startsWith("onDrag"))&&(c[u]=t[u]);return c}const Ej=["animate","circle","defs","desc","ellipse","g","image","line","filter","marker","mask","metadata","path","pattern","polygon","polyline","rect","stop","switch","symbol","svg","text","tspan","use","view"];function ku(t){return typeof t!="string"||t.includes("-")?!1:!!(Ej.indexOf(t)>-1||/[A-Z]/u.test(t))}function Mj(t,s,r,{latestValues:o},c,u=!1,h,p){const v=(h??ku(t)?Cj:Nj)(s,o,c,t),g=Pj(s,typeof t=="string",u,p),x=t!==T.Fragment?{...g,...v,ref:r}:{},{children:b}=s,j=T.useMemo(()=>nt(b)?b.get():b,[b]);return T.createElement(t,{...x,children:j})}function _j({scrapeMotionValuesFromProps:t,createRenderState:s},r,o,c){return{latestValues:Dj(r,o,c,t),renderState:s()}}function Dj(t,s,r,o){const c={},u=o(t,{});for(const b in u)c[b]=fa(u[b]);let{initial:h,animate:p}=t;const f=Oa(t),v=Vg(t);s&&v&&!f&&t.inherit!==!1&&(h===void 0&&(h=s.initial),p===void 0&&(p=s.animate));let g=r?r.initial===!1:!1;g=g||h===!1;const x=g?p:h;if(x&&typeof x!="boolean"&&!Ba(x)){const b=Array.isArray(x)?x:[x];for(let j=0;j<b.length;j++){const N=du(t,b[j]);if(N){const{transitionEnd:w,transition:S,...B}=N;for(const P in B){let D=B[P];if(Array.isArray(D)){const V=g?D.length-1:0;D=D[V]}D!==null&&(c[P]=D)}for(const P in w)c[P]=w[P]}}}return c}const ly=t=>(s,r)=>{const o=T.useContext(za),c=T.useContext(Kc),u=()=>_j(t,s,o,c);return r?u():Ab(u)},Rj=ly({scrapeMotionValuesFromProps:bu,createRenderState:wu}),Lj=ly({scrapeMotionValuesFromProps:Hg,createRenderState:oy}),Ij=Symbol.for("motionComponentSymbol");function Vj(t,s,r){const o=T.useRef(r);T.useInsertionEffect(()=>{o.current=r});const c=T.useRef(null);return T.useCallback(u=>{var p;u&&((p=t.onMount)==null||p.call(t,u)),s&&(u?s.mount(u):s.unmount());const h=o.current;if(typeof h=="function")if(u){const f=h(u);typeof f=="function"&&(c.current=f)}else c.current?(c.current(),c.current=null):h(u);else h&&(h.current=u)},[s])}const cy=T.createContext({});function Ls(t){return t&&typeof t=="object"&&Object.prototype.hasOwnProperty.call(t,"current")}function Fj(t,s,r,o,c,u){var D,V;const{visualElement:h}=T.useContext(za),p=T.useContext(iy),f=T.useContext(Kc),v=T.useContext(sy),g=v.reducedMotion,x=v.skipAnimations,b=T.useRef(null),j=T.useRef(!1);o=o||p.renderer,!b.current&&o&&(b.current=o(t,{visualState:s,parent:h,props:r,presenceContext:f,blockInitialAnimation:f?f.initial===!1:!1,reducedMotionConfig:g,skipAnimations:x,isSVG:u}),j.current&&b.current&&(b.current.manuallyAnimateOnMount=!0));const N=b.current,w=T.useContext(cy);N&&!N.projection&&c&&(N.type==="html"||N.type==="svg")&&Bj(b.current,r,c,w);const S=T.useRef(!1);T.useInsertionEffect(()=>{N&&S.current&&N.update(r,f)});const B=r[jg],P=T.useRef(!!B&&typeof window<"u"&&!((D=window.MotionHandoffIsComplete)!=null&&D.call(window,B))&&((V=window.MotionHasOptimisedAnimation)==null?void 0:V.call(window,B)));return Eb(()=>{j.current=!0,N&&(S.current=!0,window.MotionIsMounted=!0,N.updateFeatures(),N.scheduleRenderMicrotask(),P.current&&N.animationState&&N.animationState.animateChanges())}),T.useEffect(()=>{N&&(!P.current&&N.animationState&&N.animationState.animateChanges(),P.current&&(queueMicrotask(()=>{var _;(_=window.MotionHandoffMarkAsComplete)==null||_.call(window,B)}),P.current=!1),N.enteringChildren=void 0)}),N}function Bj(t,s,r,o){const{layoutId:c,layout:u,drag:h,dragConstraints:p,layoutScroll:f,layoutRoot:v,layoutAnchor:g,layoutCrossfade:x}=s;t.projection=new r(t.latestValues,s["data-framer-portal-id"]?void 0:uy(t.parent)),t.projection.setOptions({layoutId:c,layout:u,alwaysMeasureLayout:!!h||p&&Ls(p),visualElement:t,animationType:typeof u=="string"?u:"both",initialPromotionConfig:o,crossfade:x,layoutScroll:f,layoutRoot:v,layoutAnchor:g})}function uy(t){if(t)return t.options.allowProjection!==!1?t.projection:uy(t.parent)}function ic(t,{forwardMotionProps:s=!1,type:r}={},o,c){o&&bj(o);const u=r?r==="svg":ku(t),h=u?Lj:Rj;function p(v,g){let x;const b={...T.useContext(sy),...v,layoutId:Oj(v)},{isStatic:j,isValidProp:N}=b,w=kj(v),S=h(v,j);if(!j&&typeof window<"u"){zj();const B=Uj(b);x=B.MeasureLayout,w.visualElement=Fj(t,S,b,c,B.ProjectionNode,u)}return i.jsxs(za.Provider,{value:w,children:[x&&w.visualElement?i.jsx(x,{visualElement:w.visualElement,...b}):null,Mj(t,v,Vj(S,w.visualElement,g),S,j,s,u,N)]})}p.displayName=`motion.${typeof t=="string"?t:`create(${t.displayName??t.name??""})`}`;const f=T.forwardRef(p);return f[Ij]=t,f}function Oj({layoutId:t}){const s=T.useContext(Df).id;return s&&t!==void 0?s+"-"+t:t}function zj(t,s){T.useContext(iy).strict}function Uj(t){const s=ry(),{drag:r,layout:o}=s;if(!r&&!o)return{};const c={...r,...o};return{MeasureLayout:r!=null&&r.isEnabled(t)||o!=null&&o.isEnabled(t)?c.MeasureLayout:void 0,ProjectionNode:c.ProjectionNode}}function $j(t,s){if(typeof Proxy>"u")return ic;const r=new Map,o=(u,h)=>ic(u,h,t,s),c=(u,h)=>o(u,h);return new Proxy(c,{get:(u,h)=>h==="create"?o:(r.has(h)||r.set(h,ic(h,void 0,t,s)),r.get(h))})}const Wj=(t,s)=>s.isSVG??ku(t)?new N0(s):new j0(s,{allowProjection:t!==T.Fragment});class Hj extends In{constructor(s){super(s),s.animationState||(s.animationState=E0(s))}updateAnimationControlsSubscription(){const{animate:s}=this.node.getProps();Ba(s)&&(this.unmountControls=s.subscribe(this.node))}mount(){this.updateAnimationControlsSubscription()}update(){const{animate:s}=this.node.getProps(),{animate:r}=this.node.prevProps||{};s!==r&&this.updateAnimationControlsSubscription()}unmount(){var s;this.node.animationState.reset(),(s=this.unmountControls)==null||s.call(this)}}let Gj=0;class Kj extends In{constructor(){super(...arguments),this.id=Gj++,this.isExitComplete=!1}update(){var u;if(!this.node.presenceContext)return;const{isPresent:s,onExitComplete:r}=this.node.presenceContext,{isPresent:o}=this.node.prevPresenceContext||{};if(!this.node.animationState||s===o)return;if(s&&o===!1){if(this.isExitComplete){const{initial:h,custom:p}=this.node.getProps();if(typeof h=="string"||typeof h=="object"&&h!==null&&!Array.isArray(h)){const f=os(this.node,h,p);if(f){const{transition:v,transitionEnd:g,...x}=f;for(const b in x)(u=this.node.getValue(b))==null||u.jump(x[b])}}this.node.animationState.reset(),this.node.animationState.animateChanges()}else this.node.animationState.setActive("exit",!1);this.isExitComplete=!1;return}const c=this.node.animationState.setActive("exit",!s);r&&!s&&c.then(()=>{this.isExitComplete=!0,r(this.id)})}mount(){const{register:s,onExitComplete:r}=this.node.presenceContext||{};r&&r(this.id),s&&(this.unmount=s(this.id))}unmount(){}}const qj={animation:{Feature:Hj},exit:{Feature:Kj}};function $i(t){return{point:{x:t.pageX,y:t.pageY}}}const Xj=t=>s=>yu(s)&&t(s,$i(s));function Ri(t,s,r,o){return Bi(t,s,Xj(r),o)}const dy=({current:t})=>t?t.ownerDocument.defaultView:null,Op=(t,s)=>Math.abs(t-s);function Yj(t,s){const r=Op(t.x,s.x),o=Op(t.y,s.y);return Math.sqrt(r**2+o**2)}const zp=new Set(["auto","scroll"]);class hy{constructor(s,r,{transformPagePoint:o,contextWindow:c=window,dragSnapToOrigin:u=!1,distanceThreshold:h=3,element:p}={}){if(this.startEvent=null,this.lastMoveEvent=null,this.lastMoveEventInfo=null,this.lastRawMoveEventInfo=null,this.handlers={},this.contextWindow=window,this.scrollPositions=new Map,this.removeScrollListeners=null,this.onElementScroll=N=>{this.handleScroll(N.target)},this.onWindowScroll=()=>{this.handleScroll(window)},this.updatePoint=()=>{if(!(this.lastMoveEvent&&this.lastMoveEventInfo))return;this.lastRawMoveEventInfo&&(this.lastMoveEventInfo=ia(this.lastRawMoveEventInfo,this.transformPagePoint));const N=rc(this.lastMoveEventInfo,this.history),w=this.startEvent!==null,S=Yj(N.offset,{x:0,y:0})>=this.distanceThreshold;if(!w&&!S)return;const{point:B}=N,{timestamp:P}=Xe;this.history.push({...B,timestamp:P});const{onStart:D,onMove:V}=this.handlers;w||(D&&D(this.lastMoveEvent,N),this.startEvent=this.lastMoveEvent),V&&V(this.lastMoveEvent,N)},this.handlePointerMove=(N,w)=>{this.lastMoveEvent=N,this.lastRawMoveEventInfo=w,this.lastMoveEventInfo=ia(w,this.transformPagePoint),Ee.update(this.updatePoint,!0)},this.handlePointerUp=(N,w)=>{this.end();const{onEnd:S,onSessionEnd:B,resumeAnimation:P}=this.handlers;if((this.dragSnapToOrigin||!this.startEvent)&&P&&P(),!(this.lastMoveEvent&&this.lastMoveEventInfo))return;const D=rc(N.type==="pointercancel"?this.lastMoveEventInfo:ia(w,this.transformPagePoint),this.history);this.startEvent&&S&&S(N,D),B&&B(N,D)},!yu(s))return;this.dragSnapToOrigin=u,this.handlers=r,this.transformPagePoint=o,this.distanceThreshold=h,this.contextWindow=c||window;const f=$i(s),v=ia(f,this.transformPagePoint),{point:g}=v,{timestamp:x}=Xe;this.history=[{...g,timestamp:x}];const{onSessionStart:b}=r;b&&b(s,rc(v,this.history));const j={passive:!0,capture:!0};this.removeListeners=Oi(Ri(this.contextWindow,"pointermove",this.handlePointerMove,j),Ri(this.contextWindow,"pointerup",this.handlePointerUp,j),Ri(this.contextWindow,"pointercancel",this.handlePointerUp,j)),p&&this.startScrollTracking(p)}startScrollTracking(s){let r=s.parentElement;for(;r;){const o=getComputedStyle(r);(zp.has(o.overflowX)||zp.has(o.overflowY))&&this.scrollPositions.set(r,{x:r.scrollLeft,y:r.scrollTop}),r=r.parentElement}this.scrollPositions.set(window,{x:window.scrollX,y:window.scrollY}),window.addEventListener("scroll",this.onElementScroll,{capture:!0}),window.addEventListener("scroll",this.onWindowScroll),this.removeScrollListeners=()=>{window.removeEventListener("scroll",this.onElementScroll,{capture:!0}),window.removeEventListener("scroll",this.onWindowScroll)}}handleScroll(s){const r=this.scrollPositions.get(s);if(!r)return;const o=s===window,c=o?{x:window.scrollX,y:window.scrollY}:{x:s.scrollLeft,y:s.scrollTop},u={x:c.x-r.x,y:c.y-r.y};u.x===0&&u.y===0||(o?this.lastMoveEventInfo&&(this.lastMoveEventInfo.point.x+=u.x,this.lastMoveEventInfo.point.y+=u.y):this.history.length>0&&(this.history[0].x-=u.x,this.history[0].y-=u.y),this.scrollPositions.set(s,c),Ee.update(this.updatePoint,!0))}updateHandlers(s){this.handlers=s}end(){this.removeListeners&&this.removeListeners(),this.removeScrollListeners&&this.removeScrollListeners(),this.scrollPositions.clear(),Rn(this.updatePoint)}}function ia(t,s){return s?{point:s(t.point)}:t}function Up(t,s){return{x:t.x-s.x,y:t.y-s.y}}function rc({point:t},s){return{point:t,delta:Up(t,my(s)),offset:Up(t,Qj(s)),velocity:Jj(s,.1)}}function Qj(t){return t[0]}function my(t){return t[t.length-1]}function Jj(t,s){if(t.length<2)return{x:0,y:0};let r=t.length-1,o=null;const c=my(t);for(;r>=0&&(o=t[r],!(c.timestamp-o.timestamp>Dt(s)));)r--;if(!o)return{x:0,y:0};o===t[0]&&t.length>2&&c.timestamp-o.timestamp>Dt(s)*2&&(o=t[1]);const u=jt(c.timestamp-o.timestamp);if(u===0)return{x:0,y:0};const h={x:(c.x-o.x)/u,y:(c.y-o.y)/u};return h.x===1/0&&(h.x=0),h.y===1/0&&(h.y=0),h}function Zj(t,{min:s,max:r},o){return s!==void 0&&t<s?t=o?Pe(s,t,o.min):Math.max(t,s):r!==void 0&&t>r&&(t=o?Pe(r,t,o.max):Math.min(t,r)),t}function $p(t,s,r){return{min:s!==void 0?t.min+s:void 0,max:r!==void 0?t.max+r-(t.max-t.min):void 0}}function e1(t,{top:s,left:r,bottom:o,right:c}){return{x:$p(t.x,r,c),y:$p(t.y,s,o)}}function Wp(t,s){let r=s.min-t.min,o=s.max-t.max;return s.max-s.min<t.max-t.min&&([r,o]=[o,r]),{min:r,max:o}}function t1(t,s){return{x:Wp(t.x,s.x),y:Wp(t.y,s.y)}}function n1(t,s){let r=.5;const o=dt(t),c=dt(s);return c>o?r=Li(s.min,s.max-o,t.min):o>c&&(r=Li(t.min,t.max-c,s.min)),Wt(0,1,r)}function s1(t,s){const r={};return s.min!==void 0&&(r.min=s.min-t.min),s.max!==void 0&&(r.max=s.max-t.min),r}const $c=.35;function i1(t=$c){return t===!1?t=0:t===!0&&(t=$c),{x:Hp(t,"left","right"),y:Hp(t,"top","bottom")}}function Hp(t,s,r){return{min:Gp(t,s),max:Gp(t,r)}}function Gp(t,s){return typeof t=="number"?t:t[s]||0}const r1=new WeakMap;class a1{constructor(s){this.openDragLock=null,this.isDragging=!1,this.currentDirection=null,this.originPoint={x:0,y:0},this.constraints=!1,this.hasMutatedConstraints=!1,this.elastic=qe(),this.latestPointerEvent=null,this.latestPanInfo=null,this.visualElement=s}start(s,{snapToCursor:r=!1,distanceThreshold:o}={}){const{presenceContext:c}=this.visualElement;if(c&&c.isPresent===!1)return;const u=x=>{r&&this.snapToCursor($i(x).point),this.stopAnimation()},h=(x,b)=>{const{drag:j,dragPropagation:N,onDragStart:w}=this.getProps();if(j&&!N&&(this.openDragLock&&this.openDragLock(),this.openDragLock=Jk(j),!this.openDragLock))return;this.latestPointerEvent=x,this.latestPanInfo=b,this.isDragging=!0,this.currentDirection=null,this.resolveConstraints(),this.visualElement.projection&&(this.visualElement.projection.isAnimationBlocked=!0,this.visualElement.projection.target=void 0),Qt(B=>{let P=this.getAxisMotionValue(B).get()||0;if(en.test(P)){const{projection:D}=this.visualElement;if(D&&D.layout){const V=D.layout.layoutBox[B];V&&(P=dt(V)*(parseFloat(P)/100))}}this.originPoint[B]=P}),w&&Ee.update(()=>w(x,b),!1,!0),Ic(this.visualElement,"transform");const{animationState:S}=this.visualElement;S&&S.setActive("whileDrag",!0)},p=(x,b)=>{this.latestPointerEvent=x,this.latestPanInfo=b;const{dragPropagation:j,dragDirectionLock:N,onDirectionLock:w,onDrag:S}=this.getProps();if(!j&&!this.openDragLock)return;const{offset:B}=b;if(N&&this.currentDirection===null){this.currentDirection=l1(B),this.currentDirection!==null&&w&&w(this.currentDirection);return}this.updateAxis("x",b.point,B),this.updateAxis("y",b.point,B),this.visualElement.render(),S&&Ee.update(()=>S(x,b),!1,!0)},f=(x,b)=>{this.latestPointerEvent=x,this.latestPanInfo=b,this.stop(x,b),this.latestPointerEvent=null,this.latestPanInfo=null},v=()=>{const{dragSnapToOrigin:x}=this.getProps();(x||this.constraints)&&this.startAnimation({x:0,y:0})},{dragSnapToOrigin:g}=this.getProps();this.panSession=new hy(s,{onSessionStart:u,onStart:h,onMove:p,onSessionEnd:f,resumeAnimation:v},{transformPagePoint:this.visualElement.getTransformPagePoint(),dragSnapToOrigin:g,distanceThreshold:o,contextWindow:dy(this.visualElement),element:this.visualElement.current})}stop(s,r){const o=s||this.latestPointerEvent,c=r||this.latestPanInfo,u=this.isDragging;if(this.cancel(),!u||!c||!o)return;const{velocity:h}=c;this.startAnimation(h);const{onDragEnd:p}=this.getProps();p&&Ee.postRender(()=>p(o,c))}cancel(){this.isDragging=!1;const{projection:s,animationState:r}=this.visualElement;s&&(s.isAnimationBlocked=!1),this.endPanSession();const{dragPropagation:o}=this.getProps();!o&&this.openDragLock&&(this.openDragLock(),this.openDragLock=null),r&&r.setActive("whileDrag",!1)}endPanSession(){this.panSession&&this.panSession.end(),this.panSession=void 0}updateAxis(s,r,o){const{drag:c}=this.getProps();if(!o||!ra(s,c,this.currentDirection))return;const u=this.getAxisMotionValue(s);let h=this.originPoint[s]+o[s];this.constraints&&this.constraints[s]&&(h=Zj(h,this.constraints[s],this.elastic[s])),u.set(h)}resolveConstraints(){var u;const{dragConstraints:s,dragElastic:r}=this.getProps(),o=this.visualElement.projection&&!this.visualElement.projection.layout?this.visualElement.projection.measure(!1):(u=this.visualElement.projection)==null?void 0:u.layout,c=this.constraints;s&&Ls(s)?this.constraints||(this.constraints=this.resolveRefConstraints()):s&&o?this.constraints=e1(o.layoutBox,s):this.constraints=!1,this.elastic=i1(r),c!==this.constraints&&!Ls(s)&&o&&this.constraints&&!this.hasMutatedConstraints&&Qt(h=>{this.constraints!==!1&&this.getAxisMotionValue(h)&&(this.constraints[h]=s1(o.layoutBox[h],this.constraints[h]))})}resolveRefConstraints(){const{dragConstraints:s,onMeasureDragConstraints:r}=this.getProps();if(!s||!Ls(s))return!1;const o=s.current,{projection:c}=this.visualElement;if(!c||!c.layout)return!1;c.root&&(c.root.scroll=void 0,c.root.updateScroll());const u=Qk(o,c.root,this.visualElement.getTransformPagePoint());let h=t1(c.layout.layoutBox,u);if(r){const p=r(qk(h));this.hasMutatedConstraints=!!p,p&&(h=Pg(p))}return h}startAnimation(s){const{drag:r,dragMomentum:o,dragElastic:c,dragTransition:u,dragSnapToOrigin:h,onDragTransitionEnd:p}=this.getProps(),f=this.constraints||{},v=Qt(g=>{if(!ra(g,r,this.currentDirection))return;let x=f&&f[g]||{};(h===!0||h===g)&&(x={min:0,max:0});const b=c?200:1e6,j=c?40:1e7,N={type:"inertia",velocity:o?s[g]:0,bounceStiffness:b,bounceDamping:j,timeConstant:750,restDelta:1,restSpeed:10,...u,...x};return this.startAxisValueAnimation(g,N)});return Promise.all(v).then(p)}startAxisValueAnimation(s,r){const o=this.getAxisMotionValue(s);return Ic(this.visualElement,s),o.start(uu(s,o,0,r,this.visualElement,!1))}stopAnimation(){Qt(s=>this.getAxisMotionValue(s).stop())}getAxisMotionValue(s){const r=`_drag${s.toUpperCase()}`,c=this.visualElement.getProps()[r];return c||this.visualElement.getValue(s,this.visualElement.latestValues[s]??0)}snapToCursor(s){Qt(r=>{const{drag:o}=this.getProps();if(!ra(r,o,this.currentDirection))return;const{projection:c}=this.visualElement,u=this.getAxisMotionValue(r);if(c&&c.layout){const{min:h,max:p}=c.layout.layoutBox[r],f=u.get()||0;u.set(s[r]-Pe(h,p,.5)+f)}})}scalePositionWithinConstraints(){if(!this.visualElement.current)return;const{drag:s,dragConstraints:r}=this.getProps(),{projection:o}=this.visualElement;if(!Ls(r)||!o||!this.constraints)return;this.stopAnimation();const c={x:0,y:0};Qt(h=>{const p=this.getAxisMotionValue(h);if(p&&this.constraints!==!1){const f=p.get();c[h]=n1({min:f,max:f},this.constraints[h])}});const{transformTemplate:u}=this.visualElement.getProps();this.visualElement.current.style.transform=u?u({},""):"none",o.root&&o.root.updateScroll(),o.updateLayout(),this.constraints=!1,this.resolveConstraints(),Qt(h=>{if(!ra(h,s,null))return;const p=this.getAxisMotionValue(h),{min:f,max:v}=this.constraints[h];p.set(Pe(f,v,c[h]))}),this.visualElement.render()}addListeners(){if(!this.visualElement.current)return;r1.set(this.visualElement,this);const s=this.visualElement.current,r=Ri(s,"pointerdown",v=>{const{drag:g,dragListener:x=!0}=this.getProps(),b=v.target,j=b!==s&&i0(b);g&&x&&!j&&this.start(v)});let o;const c=()=>{const{dragConstraints:v}=this.getProps();Ls(v)&&v.current&&(this.constraints=this.resolveRefConstraints(),o||(o=o1(s,v.current,()=>this.scalePositionWithinConstraints())))},{projection:u}=this.visualElement,h=u.addEventListener("measure",c);u&&!u.layout&&(u.root&&u.root.updateScroll(),u.updateLayout()),Ee.read(c);const p=Bi(window,"resize",()=>this.scalePositionWithinConstraints()),f=u.addEventListener("didUpdate",(({delta:v,hasLayoutChanged:g})=>{this.isDragging&&g&&(Qt(x=>{const b=this.getAxisMotionValue(x);b&&(this.originPoint[x]+=v[x].translate,b.set(b.get()+v[x].translate))}),this.visualElement.render())}));return()=>{p(),r(),h(),f&&f(),o&&o()}}getProps(){const s=this.visualElement.getProps(),{drag:r=!1,dragDirectionLock:o=!1,dragPropagation:c=!1,dragConstraints:u=!1,dragElastic:h=$c,dragMomentum:p=!0}=s;return{...s,drag:r,dragDirectionLock:o,dragPropagation:c,dragConstraints:u,dragElastic:h,dragMomentum:p}}}function Kp(t){let s=!0;return()=>{if(s){s=!1;return}t()}}function o1(t,s,r){const o=lp(t,Kp(r)),c=lp(s,Kp(r));return()=>{o(),c()}}function ra(t,s,r){return(s===!0||s===t)&&(r===null||r===t)}function l1(t,s=10){let r=null;return Math.abs(t.y)>s?r="y":Math.abs(t.x)>s&&(r="x"),r}class c1 extends In{constructor(s){super(s),this.removeGroupControls=$t,this.removeListeners=$t,this.controls=new a1(s)}mount(){const{dragControls:s}=this.node.getProps();s&&(this.removeGroupControls=s.subscribe(this.controls)),this.removeListeners=this.controls.addListeners()||$t}update(){const{dragControls:s}=this.node.getProps(),{dragControls:r}=this.node.prevProps||{};s!==r&&(this.removeGroupControls(),s&&(this.removeGroupControls=s.subscribe(this.controls)))}unmount(){this.removeGroupControls(),this.removeListeners(),this.controls.isDragging||this.controls.endPanSession()}}const ac=t=>(s,r)=>{t&&Ee.update(()=>t(s,r),!1,!0)};class u1 extends In{constructor(){super(...arguments),this.removePointerDownListener=$t}onPointerDown(s){this.session=new hy(s,this.createPanHandlers(),{transformPagePoint:this.node.getTransformPagePoint(),contextWindow:dy(this.node)})}createPanHandlers(){const{onPanSessionStart:s,onPanStart:r,onPan:o,onPanEnd:c}=this.node.getProps();return{onSessionStart:ac(s),onStart:ac(r),onMove:ac(o),onEnd:(u,h)=>{delete this.session,c&&Ee.postRender(()=>c(u,h))}}}mount(){this.removePointerDownListener=Ri(this.node.current,"pointerdown",s=>this.onPointerDown(s))}update(){this.session&&this.session.updateHandlers(this.createPanHandlers())}unmount(){this.removePointerDownListener(),this.session&&this.session.end()}}let oc=!1;class d1 extends T.Component{componentDidMount(){const{visualElement:s,layoutGroup:r,switchLayoutGroup:o,layoutId:c}=this.props,{projection:u}=s;u&&(r.group&&r.group.add(u),o&&o.register&&c&&o.register(u),oc&&u.root.didUpdate(),u.addEventListener("animationComplete",()=>{this.safeToRemove()}),u.setOptions({...u.options,layoutDependency:this.props.layoutDependency,onExitComplete:()=>this.safeToRemove()})),ga.hasEverUpdated=!0}getSnapshotBeforeUpdate(s){const{layoutDependency:r,visualElement:o,drag:c,isPresent:u}=this.props,{projection:h}=o;return h&&(h.isPresent=u,s.layoutDependency!==r&&h.setOptions({...h.options,layoutDependency:r}),oc=!0,c||s.layoutDependency!==r||r===void 0||s.isPresent!==u?h.willUpdate():this.safeToRemove(),s.isPresent!==u&&(u?h.promote():h.relegate()||Ee.postRender(()=>{const p=h.getStack();(!p||!p.members.length)&&this.safeToRemove()}))),null}componentDidUpdate(){const{visualElement:s,layoutAnchor:r}=this.props,{projection:o}=s;o&&(o.options.layoutAnchor=r,o.root.didUpdate(),gu.postRender(()=>{!o.currentAnimation&&o.isLead()&&this.safeToRemove()}))}componentWillUnmount(){const{visualElement:s,layoutGroup:r,switchLayoutGroup:o}=this.props,{projection:c}=s;oc=!0,c&&(c.scheduleCheckAfterUnmount(),r&&r.group&&r.group.remove(c),o&&o.deregister&&o.deregister(c))}safeToRemove(){const{safeToRemove:s}=this.props;s&&s()}render(){return null}}function py(t){const[s,r]=vj(),o=T.useContext(Df);return i.jsx(d1,{...t,layoutGroup:o,switchLayoutGroup:T.useContext(cy),isPresent:s,safeToRemove:r})}const h1={pan:{Feature:u1},drag:{Feature:c1,ProjectionNode:ny,MeasureLayout:py}};function qp(t,s,r){const{props:o}=t;t.animationState&&o.whileHover&&t.animationState.setActive("whileHover",r==="Start");const c="onHover"+r,u=o[c];u&&Ee.postRender(()=>u(s,$i(s)))}class m1 extends In{mount(){const{current:s}=this.node;s&&(this.unmount=e0(s,(r,o)=>(qp(this.node,o,"Start"),c=>qp(this.node,c,"End"))))}unmount(){}}class p1 extends In{constructor(){super(...arguments),this.isActive=!1}onFocus(){let s=!1;try{s=this.node.current.matches(":focus-visible")}catch{s=!0}!s||!this.node.animationState||(this.node.animationState.setActive("whileFocus",!0),this.isActive=!0)}onBlur(){!this.isActive||!this.node.animationState||(this.node.animationState.setActive("whileFocus",!1),this.isActive=!1)}mount(){this.unmount=Oi(Bi(this.node.current,"focus",()=>this.onFocus()),Bi(this.node.current,"blur",()=>this.onBlur()))}unmount(){}}function Xp(t,s,r){const{props:o}=t;if(t.current instanceof HTMLButtonElement&&t.current.disabled)return;t.animationState&&o.whileTap&&t.animationState.setActive("whileTap",r==="Start");const c="onTap"+(r==="End"?"":r),u=o[c];u&&Ee.postRender(()=>u(s,$i(s)))}class f1 extends In{mount(){const{current:s}=this.node;if(!s)return;const{globalTapTarget:r,propagate:o}=this.node.props;this.unmount=a0(s,(c,u)=>(Xp(this.node,u,"Start"),(h,{success:p})=>Xp(this.node,h,p?"End":"Cancel")),{useGlobalTarget:r,stopPropagation:(o==null?void 0:o.tap)===!1})}unmount(){}}const Wc=new WeakMap,lc=new WeakMap,g1=t=>{const s=Wc.get(t.target);s&&s(t)},y1=t=>{t.forEach(g1)};function v1({root:t,...s}){const r=t||document;lc.has(r)||lc.set(r,{});const o=lc.get(r),c=JSON.stringify(s);return o[c]||(o[c]=new IntersectionObserver(y1,{root:t,...s})),o[c]}function x1(t,s,r){const o=v1(s);return Wc.set(t,r),o.observe(t),()=>{Wc.delete(t),o.unobserve(t)}}const b1={some:0,all:1};class w1 extends In{constructor(){super(...arguments),this.hasEnteredView=!1,this.isInView=!1}startObserver(){var f;(f=this.stopObserver)==null||f.call(this);const{viewport:s={}}=this.node.getProps(),{root:r,margin:o,amount:c="some",once:u}=s,h={root:r?r.current:void 0,rootMargin:o,threshold:typeof c=="number"?c:b1[c]},p=v=>{const{isIntersecting:g}=v;if(this.isInView===g||(this.isInView=g,u&&!g&&this.hasEnteredView))return;g&&(this.hasEnteredView=!0),this.node.animationState&&this.node.animationState.setActive("whileInView",g);const{onViewportEnter:x,onViewportLeave:b}=this.node.getProps(),j=g?x:b;j&&j(v)};this.stopObserver=x1(this.node.current,h,p)}mount(){this.startObserver()}update(){if(typeof IntersectionObserver>"u")return;const{props:s,prevProps:r}=this.node;["amount","margin","root"].some(k1(s,r))&&this.startObserver()}unmount(){var s;(s=this.stopObserver)==null||s.call(this),this.hasEnteredView=!1,this.isInView=!1}}function k1({viewport:t={}},{viewport:s={}}={}){return r=>t[r]!==s[r]}const j1={inView:{Feature:w1},tap:{Feature:f1},focus:{Feature:p1},hover:{Feature:m1}},S1={layout:{ProjectionNode:ny,MeasureLayout:py}},N1={...qj,...j1,...h1,...S1},C1=$j(N1,Wj);function T1(){!xu.current&&Fg();const[t]=T.useState(Ea.current);return t}const Yp=C1,A1={type:"spring",stiffness:620,damping:42,mass:.35},P1={type:"spring",stiffness:460,damping:38,mass:.8},E1=typeof window>"u"?T.useEffect:T.useLayoutEffect;function M1({items:t,value:s,defaultValue:r,onValueChange:o,activation:c="automatic"}){const u=T.useId(),h=T.useRef(new Map),p=T.useRef(1),[f,v]=T.useState(()=>{var P,D;return r??((P=t.find(V=>!V.disabled))==null?void 0:P.value)??((D=t[0])==null?void 0:D.value)??""}),g=s??f,x=T.useRef(o);x.current=o;const b=T.useCallback(P=>{var _;if(P===g||!t.some(L=>L.value===P&&!L.disabled))return;const D=t.findIndex(L=>L.value===g),V=t.findIndex(L=>L.value===P);p.current=V<D?-1:1,s===void 0&&v(P),(_=x.current)==null||_.call(x,P)},[s,t,g]),j=T.useCallback(P=>{var V;const D=t[P];D&&((V=h.current.get(D.value))==null||V.focus())},[t]),N=T.useCallback((P,D)=>{const V=t.length;if(!V)return 0;let _=P;for(let L=0;L<V;L+=1)if(_=(_+D+V)%V,!t[_].disabled)return _;return P},[t]),w=T.useCallback(P=>{const D=t.map((V,_)=>_);return P&&D.reverse(),D.find(V=>!t[V].disabled)??0},[t]),S=T.useCallback((P,D)=>({id:`${u}-tab-${P.value}`,role:"tab",type:"button","aria-selected":P.value===g,"aria-controls":`${u}-panel-${P.value}`,"aria-disabled":P.disabled?!0:void 0,tabIndex:P.value===g?0:-1,ref:V=>{V?h.current.set(P.value,V):h.current.delete(P.value)},onClick:()=>{P.disabled||b(P.value)},onKeyDown:V=>{if(V.key==="ArrowRight"||V.key==="ArrowLeft"){V.preventDefault();const _=N(D,V.key==="ArrowRight"?1:-1);j(_),c==="automatic"&&b(t[_].value)}else if(V.key==="Home"||V.key==="End"){V.preventDefault();const _=w(V.key==="End");j(_),c==="automatic"&&b(t[_].value)}else(V.key==="Enter"||V.key===" ")&&(V.preventDefault(),P.disabled||b(P.value))}}),[c,u,w,j,t,N,b,g]),B=T.useCallback(P=>({id:`${u}-panel-${P}`,role:"tabpanel","aria-labelledby":`${u}-tab-${P}`,tabIndex:0}),[u]);return{value:g,select:b,direction:p.current,tabListProps:{role:"tablist","aria-orientation":"horizontal"},getTabProps:S,getPanelProps:B}}function _1({items:t,value:s,defaultValue:r,onValueChange:o,activation:c="automatic",renderPanel:u,label:h="Tabs",panelClassName:p="",className:f=""}){const v=M1({items:t,value:s,defaultValue:r,onValueChange:o,activation:c}),g=T1(),x=T.useRef(null),b=T.useRef([]),[j,N]=T.useState({x:0,width:0,ready:!1}),w=t.findIndex(S=>S.value===v.value);return E1(()=>{const S=b.current[w],B=x.current;if(!S||!B)return;const P=()=>N(V=>V.x===S.offsetLeft&&V.width===S.offsetWidth&&V.ready?V:{x:S.offsetLeft,width:S.offsetWidth,ready:!0});P();const D=new ResizeObserver(P);return D.observe(B),()=>D.disconnect()},[t,w]),i.jsxs("div",{className:`stats-tabs ${f}`,children:[i.jsxs("div",{...v.tabListProps,ref:x,"aria-label":h,className:"stats-tabs-list",children:[i.jsx(Yp.span,{layout:!0,"aria-hidden":"true",className:"stats-tabs-indicator",style:{left:j.x,width:j.width,opacity:j.ready?1:0},transition:g?{duration:0}:A1}),t.map((S,B)=>{const P=S.value===v.value,{ref:D,...V}=v.getTabProps(S,B);return i.jsx("button",{...V,ref:_=>{D(_),b.current[B]=_},className:`stats-tab${P?" selected":""}${S.disabled?" disabled":""}`,children:S.label},S.value)})]}),u&&i.jsx(Yp.div,{custom:v.direction,...v.getPanelProps(v.value),initial:g?!1:{opacity:0,x:v.direction*12},animate:{opacity:1,x:0},transition:g?{duration:0}:P1,className:`stats-tab-panel ${p}`,children:u(v.value)},v.value)]})}const D1=[{value:"messages",label:"Messages"},{value:"members",label:"Members"},{value:"layout",label:"Server layout"}];function fy(t){return new Intl.DateTimeFormat(void 0,{weekday:"short"}).format(new Date(`${t}T12:00:00`))}function R1({stats:t}){const s=t.activity.map(u=>u.messages),r=Math.max(1,...s),o=s.map((u,h)=>{const p=s.length>1?12+h*276/(s.length-1):150,f=102-u/r*78;return`${p},${f}`}).join(" "),c=`12,104 ${o} 288,104`;return i.jsxs("div",{className:"server-chart-wrap",children:[i.jsxs("div",{className:"server-chart-heading",children:[i.jsxs("div",{children:[i.jsx("span",{children:"Daily messages"}),i.jsx("strong",{children:Ne(s.reduce((u,h)=>u+h,0))})]}),i.jsx("small",{children:"Last 14 days"})]}),i.jsxs("svg",{className:"server-line-chart",viewBox:"0 0 300 122",role:"img","aria-label":"Daily messages over the last fourteen days",children:[i.jsx("defs",{children:i.jsxs("linearGradient",{id:"message-area-fill",x1:"0",x2:"0",y1:"0",y2:"1",children:[i.jsx("stop",{offset:"0%",stopColor:"var(--accent)",stopOpacity:".24"}),i.jsx("stop",{offset:"100%",stopColor:"var(--accent)",stopOpacity:"0"})]})}),[24,50,76,104].map(u=>i.jsx("line",{x1:"12",x2:"288",y1:u,y2:u,className:"server-chart-gridline"},u)),i.jsx("polygon",{points:c,fill:"url(#message-area-fill)"}),i.jsx("polyline",{points:o,className:"server-chart-line"}),t.activity.map((u,h)=>{const p=s.length>1?12+h*276/(s.length-1):150,f=102-u.messages/r*78;return i.jsx("circle",{cx:p,cy:f,r:"2.7",className:"server-chart-point",children:i.jsx("title",{children:`${u.date}: ${Ne(u.messages)} messages`})},u.date)})]}),i.jsx("div",{className:"server-chart-days",children:t.activity.filter((u,h)=>h%2===0).map(u=>i.jsx("span",{children:fy(u.date)},u.date))})]})}function L1({stats:t}){const s=Math.max(1,...t.activity.flatMap(r=>[r.joins,r.leaves]));return i.jsxs("div",{className:"server-chart-wrap",children:[i.jsxs("div",{className:"server-chart-heading",children:[i.jsxs("div",{children:[i.jsx("span",{children:"Member changes"}),i.jsxs("strong",{children:[Ne(t.activity.reduce((r,o)=>r+o.joins,0))," joined"]})]}),i.jsx("small",{children:"Last 14 days"})]}),i.jsx("div",{className:"server-member-chart",role:"img","aria-label":"Daily member joins and departures over the last fourteen days",children:t.activity.map(r=>i.jsxs("div",{className:"server-member-day",title:`${r.date}: ${r.joins} joined, ${r.leaves} left`,children:[i.jsxs("div",{className:"server-member-bars",children:[i.jsx("i",{className:"join-bar",style:{height:`${Math.max(r.joins?5:0,r.joins/s*76)}%`}}),i.jsx("i",{className:"leave-bar",style:{height:`${Math.max(r.leaves?5:0,r.leaves/s*76)}%`}})]}),i.jsx("span",{children:fy(r.date).slice(0,1)})]},r.date))}),i.jsxs("div",{className:"server-chart-legend",children:[i.jsxs("span",{children:[i.jsx("i",{className:"join-key"})," Joined ",i.jsx("b",{children:Ne(t.activity.reduce((r,o)=>r+o.joins,0))})]}),i.jsxs("span",{children:[i.jsx("i",{className:"leave-key"})," Left ",i.jsx("b",{children:Ne(t.activity.reduce((r,o)=>r+o.leaves,0))})]})]})]})}function I1({stats:t}){const s=Math.max(t.member_count,t.channel_count,t.role_count,1),r=[{label:"Members",value:t.member_count,color:"members"},{label:"Channels",value:t.channel_count,color:"channels"},{label:"Roles",value:t.role_count,color:"roles"}];return i.jsxs("div",{className:"server-layout-chart",children:[i.jsxs("div",{className:"server-layout-total",children:[i.jsx("span",{children:"Community size"}),i.jsx("strong",{children:Ne(t.member_count)}),i.jsx("small",{children:"members currently in this server"})]}),i.jsx("div",{className:"server-layout-bars",children:r.map(o=>i.jsxs("div",{className:"server-layout-row",children:[i.jsxs("div",{children:[i.jsx("span",{children:o.label}),i.jsx("strong",{children:Ne(o.value)})]}),i.jsx("div",{className:"server-layout-track",children:i.jsx("i",{className:`layout-${o.color}`,style:{width:`${Math.max(o.value?4:0,o.value/s*100)}%`}})})]},o.label))})]})}function V1({stats:t}){const[s,r]=T.useState("messages"),o=T.useMemo(()=>({messages:t.activity.reduce((u,h)=>u+h.messages,0),joins:t.activity.reduce((u,h)=>u+h.joins,0)}),[t.activity]),c=s==="members"?i.jsx(L1,{stats:t}):s==="layout"?i.jsx(I1,{stats:t}):i.jsx(R1,{stats:t});return i.jsxs("section",{className:"dash-panel server-stats-card","aria-label":"Server statistics",children:[i.jsxs("div",{className:"panel-heading server-stats-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Community analytics"}),i.jsx("h3",{children:"Server pulse"}),i.jsx("p",{children:"Daily activity tracked by Niko · last 14 days"})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(ob,{})})]}),i.jsxs("div",{className:"server-stat-metrics",children:[i.jsxs("div",{children:[i.jsx(vc,{}),i.jsx("span",{children:"Members"}),i.jsx("strong",{children:Ne(t.member_count)})]}),i.jsxs("div",{children:[i.jsx(ca,{}),i.jsx("span",{children:"Messages · 14d"}),i.jsx("strong",{children:Ne(o.messages)})]}),i.jsxs("div",{children:[i.jsx(ub,{}),i.jsx("span",{children:"New members · 14d"}),i.jsx("strong",{children:Ne(o.joins)})]})]}),i.jsx(_1,{items:D1,value:s,onValueChange:r,label:"Server statistics",renderPanel:()=>c}),i.jsx("div",{className:"server-stats-footnote",children:"Activity is collected from the moment tracking is enabled."})]})}function hn({eyebrow:t,title:s,text:r}){return i.jsxs("div",{className:"dash-heading",children:[i.jsxs("div",{className:"heading-meta",children:[i.jsx("div",{className:"eyebrow",children:t}),i.jsx("span",{className:"heading-context",children:"NIKO / CONTROL ROOM"})]}),i.jsx("h2",{children:s}),i.jsx("p",{children:r})]})}function Zt({label:t,value:s,note:r,accent:o=""}){return i.jsxs("div",{className:`dash-stat ${o}`,children:[i.jsx("span",{children:t}),i.jsx("strong",{children:s}),i.jsx("small",{children:r})]})}function F1({user:t,overview:s,guilds:r,onServers:o,onManage:c}){const u=r.filter(h=>h.installed!==!1);return i.jsxs(i.Fragment,{children:[i.jsx(hn,{eyebrow:"Personal overview",title:"Your Niko snapshot.",text:"Keep an eye on your progress, then jump into a server when you’re ready to tune the room."}),i.jsxs("div",{className:"overview-intro",children:[i.jsxs("div",{className:"profile-card",children:[i.jsx(Mf,{user:t,className:"profile-avatar"}),i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Signed in as"}),i.jsx("h3",{children:Pf(t)}),i.jsx("p",{children:"Personal economy profile"})]})]}),i.jsxs("button",{className:"button button-primary",onClick:o,children:["Manage a server ",i.jsx(J,{name:"arrow"})]})]}),i.jsxs("div",{className:"dash-stats overview-stats",children:[i.jsx(Zt,{label:"Net worth",value:Ne(s==null?void 0:s.net_worth),note:"Across your Niko profile",accent:"accent-orange"}),i.jsx(Zt,{label:"In your wallet",value:Ne(s==null?void 0:s.balance),note:"Ready to spend",accent:"accent-violet"}),i.jsx(Zt,{label:"In your vault",value:Ne(s==null?void 0:s.bank),note:"Saved for later",accent:"accent-blue"}),i.jsx(Zt,{label:"Current level",value:Ne(s==null?void 0:s.level),note:s!=null&&s.job?`Working as a ${s.job}`:"Keep showing up",accent:"accent-green"})]}),i.jsxs("div",{className:"dash-columns overview-columns",children:[i.jsxs("section",{className:"dash-panel",children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Progress"}),i.jsx("h3",{children:"Your momentum"})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(J,{name:"spark"})})]}),i.jsxs("div",{className:"metric-list",children:[i.jsxs("div",{children:[i.jsx("span",{children:"Daily streak"}),i.jsxs("strong",{children:[Ne(s==null?void 0:s.daily_streak)," ",i.jsx("small",{children:"days"})]})]}),i.jsxs("div",{children:[i.jsx("span",{children:"Achievements"}),i.jsxs("strong",{children:[Ne(s==null?void 0:s.achievements)," ",i.jsx("small",{children:"unlocked"})]})]}),i.jsxs("div",{children:[i.jsx("span",{children:"Total earned"}),i.jsxs("strong",{children:[Ne(s==null?void 0:s.total_earned)," ",i.jsx("small",{children:"coins"})]})]}),i.jsxs("div",{children:[i.jsx("span",{children:"Economy standing"}),i.jsxs("strong",{children:[s!=null&&s.economy_rank?`#${Ne(s.economy_rank)}`:"—"," ",i.jsx("small",{children:s!=null&&s.economy_profiles?`of ${Ne(s.economy_profiles)}`:""})]})]})]})]}),i.jsxs("section",{className:"dash-panel",children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Quick access"}),i.jsx("h3",{children:"Your servers"})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(J,{name:"users"})})]}),i.jsxs("div",{className:"mini-server-list",children:[u.slice(0,4).map(h=>i.jsxs("button",{onClick:()=>c(h),children:[i.jsx(Gc,{guild:h}),i.jsx("span",{children:h.name}),i.jsx(J,{name:"arrow"})]},h.id)),!u.length&&i.jsx("p",{className:"empty-state compact",children:"Add Niko to a server to start managing it."})]}),i.jsxs("button",{className:"text-link overview-link",onClick:o,children:["View all servers ",i.jsx(J,{name:"arrow"})]})]})]})]})}function Qp({guild:t,onManage:s}){const r=t.installed!==!1;return i.jsxs("article",{className:"server-card",children:[i.jsxs("div",{className:"server-card-heading",children:[i.jsx(Gc,{guild:t,className:"server-avatar"}),i.jsx("span",{className:"server-status",children:r?"Niko is installed":"Ready to add"})]}),i.jsx("h3",{children:t.name}),i.jsx("p",{children:r?"Open the dashboard to manage Niko’s features and settings.":"You have permission to manage this server. Add Niko to unlock its controls."}),r?i.jsxs("button",{className:"button button-muted button-small",onClick:()=>s(t),children:["Open settings ",i.jsx(J,{name:"arrow"})]}):i.jsxs("a",{className:"button button-primary button-small",href:t.invite_url||"#",target:"_blank",rel:"noreferrer",children:["Add Niko ",i.jsx(J,{name:"external"})]})]})}function B1({guilds:t,onManage:s}){const r=t.filter(c=>c.installed!==!1),o=t.filter(c=>c.installed===!1);return i.jsxs(i.Fragment,{children:[i.jsx(hn,{eyebrow:"Servers",title:"Choose where to work.",text:"Manage servers with Niko already installed, or add Niko to another server you can administer."}),i.jsxs("div",{className:"server-summary",children:[i.jsxs("div",{children:[i.jsx("strong",{children:Ne(r.length)}),i.jsx("span",{children:"Connected to Niko"})]}),i.jsxs("div",{children:[i.jsx("strong",{children:Ne(o.length)}),i.jsx("span",{children:"Ready to add"})]}),i.jsxs("div",{className:"server-summary-note",children:[i.jsx(J,{name:"shield"}),i.jsx("span",{children:"Only servers where you have Manage Server access are shown."})]})]}),i.jsxs("section",{className:"server-section",children:[i.jsxs("div",{className:"section-heading-row",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Connected"}),i.jsx("h3",{children:"Manage a server"})]}),i.jsx("span",{className:"section-count",children:r.length})]}),i.jsxs("div",{className:"server-grid",children:[r.map(c=>i.jsx(Qp,{guild:c,onManage:s},c.id)),!r.length&&i.jsxs("div",{className:"empty-state",children:[i.jsx("strong",{children:"No connected servers yet."}),i.jsx("span",{children:"Add Niko below, then come back here to manage it."})]})]})]}),i.jsxs("section",{className:"server-section",children:[i.jsxs("div",{className:"section-heading-row",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Available to you"}),i.jsx("h3",{children:"Add Niko to a server"})]}),i.jsx("span",{className:"section-count",children:o.length})]}),i.jsxs("div",{className:"server-grid",children:[o.map(c=>i.jsx(Qp,{guild:c,onManage:s},c.id)),!o.length&&i.jsx("div",{className:"server-note",children:"Niko is already installed in every server you can manage."})]})]})]})}function gy({rows:t}){return i.jsxs("div",{className:"rank-list",children:[t.slice(0,5).map((s,r)=>i.jsxs("div",{className:"rank-row",children:[i.jsx("span",{className:`rank rank-${r+1}`,children:String(r+1).padStart(2,"0")}),i.jsxs("span",{className:"rank-user",children:[i.jsx(Cb,{name:s.display_name||s.username||"Unknown member",avatarUrl:s.avatar_url}),i.jsxs("span",{children:[i.jsx("strong",{children:s.display_name||s.username||"Unknown member"}),s.username&&s.display_name&&i.jsxs("small",{children:["@",s.username]})]})]}),i.jsxs("strong",{children:["Level ",Ne(s.level),i.jsxs("small",{children:[Ne(s.xp)," xp"]})]})]},`${s.user_id}-${r}`)),!t.length&&i.jsx("div",{className:"empty-state compact",children:"No data recorded yet."})]})}function O1({overview:t}){return i.jsxs(i.Fragment,{children:[i.jsxs("div",{className:"guild-welcome",children:[i.jsxs("div",{children:[i.jsx("span",{className:"welcome-mark",children:i.jsx(J,{name:"grid"})}),i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Server pulse"}),i.jsx("strong",{children:"Here’s what needs your attention."})]})]}),i.jsxs("span",{className:"welcome-time",children:["LIVE SIGNALS ",i.jsx("span",{className:"status-dot"})]})]}),i.jsx(hn,{eyebrow:"Overview",title:"A quick read on your room.",text:"The important signals, without making you hunt for them."}),i.jsxs("div",{className:"dash-stats guild-overview-stats",children:[i.jsx(Zt,{label:"Warnings logged",value:Ne(t.moderation.warn_count),note:"For this server",accent:"accent-blue"}),i.jsx(Zt,{label:"Automod",value:t.moderation.automod_active?"Active":"Quiet",note:"Protection status",accent:"accent-green"}),i.jsx(Zt,{label:"Level leaders",value:Ne(t.leveling.top.length),note:"Members with recorded XP",accent:"accent-violet"})]}),i.jsx(V1,{stats:t.server}),i.jsxs("div",{className:"dash-columns overview-columns",children:[i.jsxs("section",{className:"dash-panel",children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Community energy"}),i.jsx("h3",{children:"Top XP"})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(J,{name:"spark"})})]}),i.jsx(gy,{rows:t.leveling.top})]}),i.jsxs("section",{className:"dash-panel",children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Server controls"}),i.jsx("h3",{children:"Manage the room"})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(J,{name:"settings"})})]}),i.jsxs("div",{className:"server-controls-body",children:[i.jsx("p",{children:"Use Server settings for prefixes, welcome messages, logs, and ticket panels."}),i.jsxs("span",{className:"text-link",children:["Open server settings ",i.jsx(J,{name:"arrow"})]})]})]})]})]})}function z1({rows:t,config:s,resources:r,csrfToken:o,guildId:c}){var u,h,p;return i.jsxs(i.Fragment,{children:[i.jsx(hn,{eyebrow:"Leveling",title:"Momentum people can see.",text:"Track the members turning up, and tune the pace to fit your server."}),i.jsxs("div",{className:"dash-stats",children:[i.jsx(Zt,{label:"Top level",value:String(((u=t[0])==null?void 0:u.level)||0),note:((h=t[0])==null?void 0:h.display_name)||((p=t[0])==null?void 0:p.username)||"No members yet",accent:"accent-violet"}),i.jsx(Zt,{label:"XP multiplier",value:`${(s==null?void 0:s.leveling.xp_multiplier)||1}×`,note:(s==null?void 0:s.leveling.xp_enabled)===!1?"XP disabled":"Currently active",accent:"accent-blue"}),i.jsx(Zt,{label:"Cooldown",value:`${(s==null?void 0:s.leveling.xp_cooldown)||0}s`,note:"Between XP awards",accent:"accent-green"})]}),i.jsxs("section",{className:"dash-panel",children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Leaderboard"}),i.jsx("h3",{children:"XP leaders"})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(J,{name:"spark"})})]}),i.jsx(gy,{rows:t})]}),i.jsx(H1,{guildId:c,config:s,resources:r,csrfToken:o})]})}const Ua={saving:!1,message:"",error:""};function ut({label:t,hint:s,children:r}){return i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:t}),r,s&&i.jsx("small",{children:s})]})}function U1(t,s){const r=s?String(s):"",o=(t==null?void 0:t.channels)||[];return!r||o.some(c=>String(c.id)===r)?o:[{id:r,name:`Saved channel · ${r}`},...o]}function $a({icon:t,label:s,title:r,text:o,className:c}){return i.jsxs("div",{className:`settings-intro${c?` ${c}`:""}`,children:[i.jsx("span",{className:"settings-intro-icon",children:i.jsx(J,{name:t})}),i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:s}),i.jsx("strong",{children:r}),i.jsx("p",{children:o})]}),i.jsxs("span",{className:"settings-intro-state",children:[i.jsx("span",{className:"status-dot"})," Per server"]})]})}function ls({label:t,title:s,detail:r,icon:o}){return i.jsxs("div",{className:"panel-heading settings-section-title",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:t}),i.jsx("h3",{children:s}),r&&i.jsx("p",{children:r})]}),o&&i.jsx("span",{className:"panel-icon",children:i.jsx(J,{name:o})})]})}function Wa({state:t}){return i.jsxs("div",{className:"setting-footer",children:[t.error?i.jsx("span",{className:"form-error",role:"alert",children:t.error}):i.jsx("span",{role:"status",children:t.message||"Changes apply to this server."}),i.jsx("button",{className:"button button-primary",type:"submit",disabled:t.saving,children:t.saving?"Saving…":"Save changes"})]})}function $1({guildId:t,config:s,csrfToken:r}){var b,j,N;const[o,c]=T.useState({}),[u,h]=T.useState(Ua);T.useEffect(()=>{const w=(s==null?void 0:s.moderation)||{};c({automod:{...w.automod||{}},spam_threshold:w.spam_threshold??6,spam_interval:w.spam_interval??7,max_mentions:w.max_mentions??5,antinuke:{...w.antinuke||{}},antiraid:{...w.antiraid||{}},antiraid_ext:{...w.antiraid_ext||{}}})},[s]);const p=(w,S,B)=>c(P=>({...P,[w]:{...P[w],[S]:B}})),f=w=>{w.preventDefault(),h({saving:!0,message:"",error:""}),Ia(t,"automod",o,r).then(S=>{const B=S.config||{};c({automod:{...B.automod||{}},spam_threshold:B.spam_threshold??6,spam_interval:B.spam_interval??7,max_mentions:B.max_mentions??5,antinuke:{...B.antinuke||{}},antiraid:{...B.antiraid||{}},antiraid_ext:{...B.antiraid_ext||{}}}),h({saving:!1,message:"Moderation settings saved to Niko.",error:""})}).catch(S=>h({saving:!1,message:"",error:S instanceof Error?S.message:"Could not save settings."}))},v=[["antispam","Anti-spam","Detect repeated messages"],["antilink","Invite links","Remove Discord invite links"],["badwords","Blocked words","Filter words from the server list"],["massmention","Mass mentions","Limit mention floods"],["scam_image_filter","Scam image filter","Delete known MrBeast scam images"],["nsfw_image_filter","NSFW image filter","AI-detect and delete NSFW images (requires NSFW_API_URL)"],["antinuke","Anti-nuke","Protect channels and roles"],["antiraid","Join raid protection","React to sudden join waves"],["antiraid_ext","External app protection","Detect user-installed app abuse"]],g=new Set(["scam_image_filter"]),x=v.filter(([w])=>{var S;return!!((S=o.automod)!=null&&S[w])}).length;return i.jsxs(i.Fragment,{children:[i.jsx(hn,{eyebrow:"Moderation",title:"Keep the room feeling good.",text:"Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration."}),i.jsx($a,{icon:"shield",label:"Protection desk",title:`${x} of ${v.length} safeguards active`,text:"Start with the essentials, then tune thresholds below when you know the room’s rhythm."}),i.jsxs("form",{onSubmit:f,className:"settings-stack",children:[i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(ls,{label:"Protection rules",title:"AutoMod modules",detail:"Toggle only the responses you want Niko to handle.",icon:"shield"}),i.jsxs("div",{className:"setting-list",children:[v.map(([w,S,B])=>{var P;return i.jsxs("label",{className:"setting-row",children:[i.jsxs("span",{children:[i.jsxs("strong",{children:[S,g.has(w)&&i.jsx("em",{className:"setting-flag-experimental",children:"experimental"})]}),i.jsx("small",{children:B})]}),i.jsx("input",{type:"checkbox",checked:!!((P=o.automod)!=null&&P[w]),onChange:D=>p("automod",w,D.target.checked)}),i.jsx("i",{"aria-hidden":"true"})]},w)}),g.size>0&&i.jsx("p",{className:"setting-note",children:"⚠️ The scam image filter is still in early testing and may have some reliability issues."})]})]}),i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(ls,{label:"Thresholds",title:"Choose when protection steps in",detail:"These limits apply across the server."}),i.jsxs("div",{className:"form-grid",children:[i.jsx(ut,{label:"Spam messages",hint:"Messages inside the spam interval",children:i.jsx("input",{type:"number",min:"1",max:"100",value:o.spam_threshold??6,onChange:w=>c({...o,spam_threshold:w.target.value})})}),i.jsx(ut,{label:"Spam interval (seconds)",children:i.jsx("input",{type:"number",min:"1",max:"3600",value:o.spam_interval??7,onChange:w=>c({...o,spam_interval:w.target.value})})}),i.jsx(ut,{label:"Maximum mentions",children:i.jsx("input",{type:"number",min:"1",max:"100",value:o.max_mentions??5,onChange:w=>c({...o,max_mentions:w.target.value})})}),i.jsx(ut,{label:"Anti-raid joins",hint:"Joins inside the join interval",children:i.jsx("input",{type:"number",min:"1",max:"1000",value:((b=o.antiraid)==null?void 0:b.join_threshold)??10,onChange:w=>p("antiraid","join_threshold",w.target.value)})}),i.jsx(ut,{label:"Anti-raid interval (seconds)",children:i.jsx("input",{type:"number",min:"1",max:"3600",value:((j=o.antiraid)==null?void 0:j.join_interval)??10,onChange:w=>p("antiraid","join_interval",w.target.value)})}),i.jsx(ut,{label:"Anti-raid action",children:i.jsxs("select",{value:((N=o.antiraid)==null?void 0:N.action)??"kick",onChange:w=>p("antiraid","action",w.target.value),children:[i.jsx("option",{value:"kick",children:"Kick"}),i.jsx("option",{value:"ban",children:"Ban"}),i.jsx("option",{value:"softban",children:"Soft-ban"}),i.jsx("option",{value:"slowmode",children:"Slowmode"}),i.jsx("option",{value:"lockdown",children:"Lockdown"})]})})]}),i.jsx(Wa,{state:u})]})]})]})}function W1({guildId:t,config:s,csrfToken:r}){var j,N;const[o,c]=T.useState({ai_name:"Niko",personality:"cafe",enabled:!0,ai_actions_experiment:!1,better_context_experiment:!1,multimodal_experiment:!1}),[u,h]=T.useState(Ua),[p,f]=T.useState(null),v=w=>w===!0||w==="True",g=w=>c({ai_name:w.ai_name||"Niko",personality:w.personality==="normal"?"normal":"cafe",enabled:w.enabled!=="False"&&w.enabled!==!1,ai_actions_experiment:v(w.ai_actions_experiment),better_context_experiment:v(w.better_context_experiment),multimodal_experiment:v(w.multimodal_experiment)});T.useEffect(()=>g((s==null?void 0:s.ai)||{}),[s]);const x=w=>{w.preventDefault(),h({saving:!0,message:"",error:""}),Ia(t,"ai",o,r).then(S=>{g(S.config||{}),h({saving:!1,message:"AI settings saved.",error:""})}).catch(S=>h({saving:!1,message:"",error:S instanceof Error?S.message:"Could not save settings."}))},b=[{key:"better_context_experiment",title:"Better context",hint:"Use the last five channel messages",info:"Adds recent conversation and replied-to message context so responses understand ongoing discussions more naturally. It is useful for follow-ups, but sends more conversation context to the AI provider."},{key:"ai_actions_experiment",title:"AI actions",hint:"Allow confirmed actions requested in chat",info:"Lets the AI propose polls and server actions such as moderation or channel management. Every action requires confirmation and is still limited by Discord permissions."},{key:"multimodal_experiment",title:"Multimodal conversation",hint:"Understand images and voice in AI replies",info:"Allows Niko to inspect image attachments and use voice-message transcriptions as context when the AI is already triggered by name, ping, or the ai command. Attachments never start a conversation on their own. Media is processed only while enabled and provider usage costs may apply."}];return i.jsxs(i.Fragment,{children:[i.jsx(hn,{eyebrow:"AI controls",title:"Give your AI the right tone.",text:"Configure the AI identity, personality, and opt-in experiments for this server."}),i.jsx($a,{icon:"settings",label:"Conversation desk",title:o.enabled?`${o.ai_name} is ready to respond`:`${o.ai_name} is staying quiet`,text:"All settings apply only to this server."}),i.jsxs("form",{onSubmit:x,className:"settings-stack",children:[i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(ls,{label:"Conversation",title:"Core settings",detail:"Decide when the AI joins the conversation.",icon:"settings"}),i.jsx("div",{className:"form-grid",children:i.jsx(ut,{label:"AI name",hint:"1–32 characters; this is also the mention trigger",children:i.jsx("input",{value:o.ai_name,maxLength:32,onChange:w=>c({...o,ai_name:w.target.value})})})}),i.jsxs("label",{className:"setting-row",children:[i.jsxs("span",{children:[i.jsx("strong",{children:"Enable AI chat"}),i.jsx("small",{children:"Respond when the configured name is mentioned"})]}),i.jsx("input",{type:"checkbox",checked:o.enabled,onChange:w=>c({...o,enabled:w.target.checked})}),i.jsx("i",{"aria-hidden":"true"})]}),i.jsxs("div",{className:"personality-options",children:[i.jsxs("button",{type:"button",className:o.personality==="cafe"?"personality active":"personality",onClick:()=>c({...o,personality:"cafe"}),children:[i.jsx("span",{className:"personality-mark",children:"n"}),i.jsxs("span",{children:[i.jsx("strong",{children:"Café"}),i.jsx("small",{children:"Warm, playful, familiar"})]})]}),i.jsxs("button",{type:"button",className:o.personality==="normal"?"personality active":"personality",onClick:()=>c({...o,personality:"normal"}),children:[i.jsx("span",{className:"personality-mark",children:"—"}),i.jsxs("span",{children:[i.jsx("strong",{children:"Normal"}),i.jsx("small",{children:"Clear and straightforward"})]})]})]})]}),i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(ls,{label:"Experiments",title:"Optional capabilities",detail:"Each experiment includes a learn-more explanation before you enable it."}),b.map(w=>i.jsxs("div",{className:"setting-row experiment-row",children:[i.jsxs("span",{children:[i.jsx("strong",{children:w.title}),i.jsx("small",{children:w.hint})]}),i.jsxs("div",{className:"experiment-actions",children:[i.jsx("button",{type:"button",className:"button button-secondary",onClick:()=>f(w.key),children:"Learn more"}),i.jsxs("label",{className:"toggle-control","aria-label":`Enable ${w.title}`,children:[i.jsx("input",{type:"checkbox",checked:o[w.key],onChange:S=>c({...o,[w.key]:S.target.checked})}),i.jsx("i",{"aria-hidden":"true"})]})]})]},w.key)),i.jsx(Wa,{state:u})]})]}),p&&i.jsx("div",{className:"modal-backdrop",role:"presentation",onClick:()=>f(null),children:i.jsxs("div",{className:"modal-card",role:"dialog","aria-modal":"true","aria-labelledby":"ai-experiment-title",onClick:w=>w.stopPropagation(),children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"AI experiment"}),i.jsx("h3",{id:"ai-experiment-title",children:(j=b.find(w=>w.key===p))==null?void 0:j.title})]}),i.jsx("button",{type:"button",className:"button button-secondary",onClick:()=>f(null),children:"Close"})]}),i.jsx("p",{children:(N=b.find(w=>w.key===p))==null?void 0:N.info})]})})]})}function H1({guildId:t,config:s,resources:r,csrfToken:o}){const c=(s==null?void 0:s.leveling)||{},[u,h]=T.useState({xp_enabled:!0,xp_multiplier:1,xp_cooldown:0,level_up_channel:"",level_up_message:""}),[p,f]=T.useState(Ua);T.useEffect(()=>h({xp_enabled:c.xp_enabled!==!1,xp_multiplier:c.xp_multiplier??1,xp_cooldown:c.xp_cooldown??0,level_up_channel:c.level_up_channel?String(c.level_up_channel):"",level_up_message:c.level_up_message||""}),[s]);const v=x=>{x.preventDefault(),f({saving:!0,message:"",error:""}),Ia(t,"leveling",u,o).then(b=>{const j=b.config||{};h({xp_enabled:j.xp_enabled!==!1,xp_multiplier:j.xp_multiplier??1,xp_cooldown:j.xp_cooldown??0,level_up_channel:j.level_up_channel?String(j.level_up_channel):"",level_up_message:j.level_up_message||""}),f({saving:!1,message:"Leveling settings saved to Niko.",error:""})}).catch(b=>f({saving:!1,message:"",error:b instanceof Error?b.message:"Could not save settings."}))},g=U1(r,u.level_up_channel);return i.jsxs(i.Fragment,{children:[i.jsx($a,{className:"leveling-settings-intro",icon:"spark",label:"Participation desk",title:u.xp_enabled?"XP is flowing":"XP is paused",text:"Set a pace that rewards regulars without turning every message into a transaction."}),i.jsx("form",{onSubmit:v,className:"settings-stack",children:i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(ls,{label:"Leveling settings",title:"Shape the pace",detail:"These controls apply to every member in this server.",icon:"spark"}),i.jsxs("label",{className:"setting-row",children:[i.jsxs("span",{children:[i.jsx("strong",{children:"Enable XP"}),i.jsx("small",{children:"Track activity and award levels"})]}),i.jsx("input",{type:"checkbox",checked:u.xp_enabled,onChange:x=>h({...u,xp_enabled:x.target.checked})}),i.jsx("i",{"aria-hidden":"true"})]}),i.jsxs("div",{className:"form-grid",children:[i.jsx(ut,{label:"XP multiplier",hint:"From 0.1× to 10×",children:i.jsx("input",{type:"number",min:"0.1",max:"10",step:"0.1",value:u.xp_multiplier,onChange:x=>h({...u,xp_multiplier:x.target.value})})}),i.jsx(ut,{label:"Cooldown (seconds)",hint:"0 disables the cooldown",children:i.jsx("input",{type:"number",min:"0",max:"86400",value:u.xp_cooldown,onChange:x=>h({...u,xp_cooldown:x.target.value})})}),i.jsx(ut,{label:"Level-up channel",children:i.jsxs("select",{value:u.level_up_channel,onChange:x=>h({...u,level_up_channel:x.target.value}),children:[i.jsx("option",{value:"",children:"Same channel"}),g.map(x=>i.jsxs("option",{value:x.id,children:["#",x.name]},x.id))]})}),i.jsx(ut,{label:"Level-up message",hint:"Use {mention}, {level}, {name}, or {guild}",children:i.jsx("textarea",{rows:3,maxLength:1e3,value:u.level_up_message,onChange:x=>h({...u,level_up_message:x.target.value}),placeholder:"Leave blank for Niko's default message"})})]}),i.jsx(Wa,{state:p})]})})]})}function G1({guildId:t,config:s,csrfToken:r}){var v;const o=((v=s==null?void 0:s.server)==null?void 0:v.profile)||{},[c,u]=T.useState({display_name:o.display_name||"",bio:o.bio||"",avatar_url:o.avatar_url||"",banner_url:o.banner_url||""}),[h,p]=T.useState(Ua);T.useEffect(()=>{var x;const g=((x=s==null?void 0:s.server)==null?void 0:x.profile)||{};u({display_name:g.display_name||"",bio:g.bio||"",avatar_url:g.avatar_url||"",banner_url:g.banner_url||""})},[s]);const f=g=>{g.preventDefault(),p({saving:!0,message:"",error:""}),Yx(t,{display_name:c.display_name||null,bio:c.bio||null,avatar_url:c.avatar_url||null,banner_url:c.banner_url||null},r).then(x=>{const b=x.profile||{};u({display_name:b.display_name||"",bio:b.bio||"",avatar_url:b.avatar_url||"",banner_url:b.banner_url||""}),p({saving:!1,message:"Bot profile updated.",error:""})}).catch(x=>p({saving:!1,message:"",error:x instanceof Error?x.message:"Could not save profile."}))};return i.jsxs(i.Fragment,{children:[i.jsx(hn,{eyebrow:"Customization",title:"Niko's server presence.",text:"Change how Niko appears in this server. Display name, avatar, banner, and bio are all per-server."}),i.jsx($a,{icon:"paint",label:"Identity desk",title:"Server-specific identity",text:"Each server can have its own Niko persona. Changes apply only to this server."}),i.jsxs("form",{onSubmit:f,className:"settings-stack",children:[i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(ls,{label:"Display name",title:"How Niko appears",detail:"Set the name members see for Niko in this server. Leave blank to use the default.",icon:"settings"}),i.jsxs("div",{className:"form-grid",children:[i.jsx(ut,{label:"Display name",hint:"32 characters or fewer",children:i.jsx("input",{value:c.display_name,maxLength:32,onChange:g=>u({...c,display_name:g.target.value}),placeholder:"Niko"})}),i.jsx(ut,{label:"Bio",hint:"190 characters or fewer",children:i.jsx("input",{value:c.bio,maxLength:190,onChange:g=>u({...c,bio:g.target.value}),placeholder:"A warm Discord companion"})})]})]}),i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(ls,{label:"Server avatar & banner",title:"Visual identity",detail:"Provide HTTPS image URLs. Images are uploaded to Discord when saved.",icon:"paint"}),i.jsxs("div",{className:"form-grid",children:[i.jsx(ut,{label:"Avatar URL",hint:"Square image, 512×512 recommended",children:i.jsx("input",{type:"url",value:c.avatar_url,onChange:g=>u({...c,avatar_url:g.target.value}),placeholder:"https://cdn.example.com/avatar.png"})}),i.jsx(ut,{label:"Banner URL",hint:"Wide image, 960×540 recommended",children:i.jsx("input",{type:"url",value:c.banner_url,onChange:g=>u({...c,banner_url:g.target.value}),placeholder:"https://cdn.example.com/banner.png"})})]}),i.jsx("p",{className:"form-hint",children:"Images are fetched, validated, and uploaded to Discord. Maximum 8 MB each. Supported formats: PNG, JPG, GIF."})]}),i.jsx(Wa,{state:h})]})]})}const K1={saving:!1,message:"",error:""};function _t({label:t,hint:s,children:r}){return i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:t}),r,s&&i.jsx("small",{children:s})]})}function Jp({label:t,hint:s,options:r,placeholder:o,onChange:c}){return i.jsxs("div",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:t}),i.jsx("div",{className:"settings-option-list",children:r.map((u,h)=>i.jsxs("div",{className:"settings-option-row",children:[i.jsx("input",{"aria-label":`${t} ${h+1}`,value:u,maxLength:100,onChange:p=>c(r.map((f,v)=>v===h?p.target.value:f)),placeholder:`${o} ${h+1}`}),i.jsx("button",{type:"button",className:"settings-option-remove",onClick:()=>c(r.filter((p,f)=>f!==h)),"aria-label":`Remove ${t.toLowerCase()} ${h+1}`,children:"Remove"})]},`${t}-${h}`))}),i.jsx("button",{type:"button",className:"button button-muted button-small settings-option-add",onClick:()=>c([...r,""]),children:"＋ Add option"}),i.jsx("small",{children:s})]})}function aa({label:t,title:s,detail:r,icon:o}){return i.jsxs("div",{className:"panel-heading settings-section-title",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:t}),i.jsx("h3",{children:s}),i.jsx("p",{children:r})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(J,{name:o})})]})}function q1({state:t}){return i.jsxs("div",{className:"setting-footer",children:[t.error?i.jsx("span",{className:"form-error",role:"alert",children:t.error}):i.jsx("span",{role:"status",children:t.message||"Changes apply to this server."}),i.jsx("button",{className:"button button-primary",type:"submit",disabled:t.saving,children:t.saving?"Saving...":"Save server settings"})]})}const X1=[["moderation","Moderation"],["automod","AutoMod"],["messages","Messages"],["channels","Channels"],["members","Members"],["captcha","Captcha"],["invites","Invites"],["roles","Roles"],["server","Server"],["voice","Voice"]];function Y1(t,s){var r;return s?((r=t==null?void 0:t.channels.find(o=>String(o.id)===String(s)))==null?void 0:r.name)||`Saved channel · ${s}`:"Not set"}function Zp(t){const s=t.replace(/^#/,"");return/^[0-9a-fA-F]{6}$/.test(s)?`#${s}`:"#5865F2"}function oa(t,s){const r=s?String(s):"",o=(t==null?void 0:t.channels)||[];return!r||o.some(c=>String(c.id)===r)?o:[{id:r,name:`Saved channel · ${r}`},...o]}function ef(t,s=[]){const r=(t==null?void 0:t.roles)||[],o=new Set(r.map(u=>String(u.id)));return[...s.map(String).filter((u,h,p)=>u&&!o.has(u)&&p.indexOf(u)===h).map(u=>({id:u,name:`Unavailable role (${u})`})),...r]}function cc(t){var o,c;const s=(t==null?void 0:t.onboarding)||{},r=(t==null?void 0:t.tickets)||{};return{prefixes:(o=t==null?void 0:t.prefixes)!=null&&o.length?[...t.prefixes]:["."],welcome_channel:s.welcome_channel?String(s.welcome_channel):"",welcome_title:s.welcome_title||"",welcome_description:s.welcome_description||"",welcome_color:s.welcome_color===null||s.welcome_color===void 0?"5865F2":s.welcome_color.toString(16).padStart(6,"0"),welcome_image:s.welcome_image||"",rules_channel:s.rules_channel?String(s.rules_channel):"",rules_text:s.rules_text||"",rules_role_id:s.rules_role_id?String(s.rules_role_id):"",logging:Object.fromEntries(Object.entries((t==null?void 0:t.logging)||{}).map(([u,h])=>[u,h==null?"":String(h)])),disabled_logging:[...((c=t==null?void 0:t.logging)==null?void 0:c.disabled)||[]].map(String),panel_title:r.panel_title||"",panel_description:r.panel_description||"",panel_categories:[...r.panel_categories||[]],panel_channel_id:r.panel_channel_id?String(r.panel_channel_id):"",support_roles:[...r.support_roles||[]].map(String)}}function Q1({guildId:t,config:s,resources:r,csrfToken:o}){const[c,u]=T.useState(()=>cc(s==null?void 0:s.server)),[h,p]=T.useState(K1),[f,v]=T.useState(!1);T.useEffect(()=>{s!=null&&s.server&&u(cc(s.server))},[s]);const g=(_,L)=>u(I=>({...I,[_]:L})),x=_=>g("welcome_color",_.replace(/^#/,"").replace(/[^0-9a-fA-F]/g,"").slice(0,6)),b=(_,L)=>u(I=>({...I,logging:{...I.logging,[_]:L}})),j=_=>u(L=>({...L,disabled_logging:L.disabled_logging.includes(_)?L.disabled_logging.filter(I=>I!==_):[...L.disabled_logging,_]})),N=_=>{_.preventDefault(),p({saving:!0,message:"",error:""});const L=c.prefixes.map(U=>U.trim()).filter(Boolean),I=c.panel_categories.map(U=>U.trim()).filter(Boolean);Ia(t,"server",{prefixes:L,onboarding:{welcome_channel:c.welcome_channel,welcome_title:c.welcome_title,welcome_description:c.welcome_description,welcome_color:c.welcome_color,welcome_image:c.welcome_image,rules_channel:c.rules_channel,rules_text:c.rules_text,rules_role_id:c.rules_role_id},logging:{...c.logging,disabled:c.disabled_logging},tickets:{panel_title:c.panel_title,panel_description:c.panel_description,panel_categories:I,panel_channel_id:c.panel_channel_id,support_roles:c.support_roles}},o).then(U=>{u(cc(U.config)),p({saving:!1,message:"Server settings saved to Niko.",error:""})}).catch(U=>p({saving:!1,message:"",error:U instanceof Error?U.message:"Could not save server settings."}))},w=c.welcome_channel,S=c.panel_channel_id,B=oa(r,c.welcome_channel),P=oa(r,c.rules_channel),D=oa(r,c.panel_channel_id),V=ef(r,c.support_roles);return i.jsxs(i.Fragment,{children:[i.jsx(hn,{eyebrow:"Server settings",title:"Make Niko fit your room.",text:"Manage the settings that shape how Niko behaves in this server. Economy balances remain global to each user and are not configured here."}),i.jsxs("div",{className:"settings-intro",children:[i.jsx("span",{className:"settings-intro-icon",children:i.jsx(J,{name:"settings"})}),i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Server control room"}),i.jsxs("strong",{children:[c.prefixes.filter(_=>_.trim()).length," command prefixes configured"]}),i.jsx("p",{children:"Welcome flows, log destinations, and ticket panels all live here."})]}),i.jsxs("span",{className:"settings-intro-state",children:[i.jsx("span",{className:"status-dot"})," Per server"]})]}),i.jsxs("form",{onSubmit:N,className:"settings-stack server-settings-stack",children:[i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(aa,{label:"Commands",title:"Prefixes",detail:"Add each command prefix separately. Niko will respond to all configured prefixes.",icon:"terminal"}),i.jsx(Jp,{label:"Command prefixes",hint:"The default prefix is .",options:c.prefixes,placeholder:"Prefix",onChange:_=>g("prefixes",_)})]}),i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(aa,{label:"Welcome flow",title:"Welcome and rules",detail:"Choose where new members see your welcome message and rules.",icon:"users"}),i.jsxs("div",{className:"form-grid",children:[i.jsx(_t,{label:"Welcome channel",children:i.jsxs("select",{value:w,onChange:_=>g("welcome_channel",_.target.value),children:[i.jsx("option",{value:"",children:"Disabled"}),B.map(_=>i.jsxs("option",{value:_.id,children:["#",_.name]},_.id))]})}),i.jsx(_t,{label:"Welcome title",children:i.jsx("input",{value:c.welcome_title,maxLength:200,onChange:_=>g("welcome_title",_.target.value),placeholder:"Welcome to the server"})}),i.jsx(_t,{label:"Welcome message",hint:"Supports {user} and {name}",children:i.jsx("textarea",{rows:4,maxLength:2e3,value:c.welcome_description,onChange:_=>g("welcome_description",_.target.value),placeholder:"Welcome {user}!"})}),i.jsx(_t,{label:"Accent color",hint:"Hex color, for example 5865F2",children:i.jsxs("div",{className:"color-picker",children:[i.jsxs("div",{className:"color-field-control",children:[i.jsx("button",{type:"button",className:"color-preview",style:{backgroundColor:Zp(c.welcome_color)},onClick:()=>v(_=>!_),"aria-label":"Choose welcome accent color","aria-expanded":f}),i.jsx("input",{value:c.welcome_color,maxLength:6,onChange:_=>x(_.target.value),placeholder:"5865F2"})]}),f&&i.jsxs("div",{className:"color-picker-popover",role:"dialog","aria-label":"Choose accent color",children:[i.jsxs("div",{className:"color-picker-header",children:[i.jsx("strong",{children:"Choose color"}),i.jsx("button",{type:"button",className:"color-picker-close",onClick:()=>v(!1),"aria-label":"Close color picker",children:"×"})]}),i.jsx("input",{className:"color-picker-native",type:"color",value:Zp(c.welcome_color),onChange:_=>x(_.target.value)}),i.jsxs("div",{className:"color-picker-value",children:[i.jsx("span",{children:"#"}),i.jsx("input",{value:c.welcome_color.replace(/^#/,""),maxLength:6,onChange:_=>x(_.target.value),placeholder:"5865F2"})]})]})]})}),i.jsx(_t,{label:"Welcome image URL",children:i.jsx("input",{type:"url",value:c.welcome_image,onChange:_=>g("welcome_image",_.target.value),placeholder:"https://..."})}),i.jsx(_t,{label:"Rules channel",children:i.jsxs("select",{value:c.rules_channel,onChange:_=>g("rules_channel",_.target.value),children:[i.jsx("option",{value:"",children:"Not configured"}),P.map(_=>i.jsxs("option",{value:_.id,children:["#",_.name]},_.id))]})}),i.jsx(_t,{label:"Rules text",children:i.jsx("textarea",{rows:4,maxLength:2e3,value:c.rules_text,onChange:_=>g("rules_text",_.target.value),placeholder:"Write the rules members should acknowledge."})}),i.jsx(_t,{label:"Role after rules acknowledgment",children:i.jsxs("select",{value:c.rules_role_id,onChange:_=>g("rules_role_id",_.target.value),children:[i.jsx("option",{value:"",children:"No role"}),ef(r,c.rules_role_id?[c.rules_role_id]:[]).map(_=>i.jsxs("option",{value:_.id,children:["@",_.name]},_.id))]})})]})]}),i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(aa,{label:"Audit trail",title:"Logging destinations",detail:"Pick a channel for each event type and disable categories you do not need.",icon:"book"}),i.jsx("div",{className:"server-logging-list",children:X1.map(([_,L])=>{const I=oa(r,c.logging[_]);return i.jsxs("div",{className:"server-logging-row",children:[i.jsxs("label",{className:"form-field",children:[i.jsxs("span",{className:"form-label",children:[L," logs"]}),i.jsxs("select",{value:String(c.logging[_]||""),onChange:U=>b(_,U.target.value),children:[i.jsx("option",{value:"",children:"Not set"}),I.map(U=>i.jsxs("option",{value:U.id,children:["#",U.name]},U.id))]})]}),i.jsxs("label",{className:"setting-row compact-setting-row",children:[i.jsxs("span",{children:[i.jsx("strong",{children:"Enabled"}),i.jsx("small",{children:Y1(r,c.logging[_])})]}),i.jsx("input",{type:"checkbox",checked:!c.disabled_logging.includes(_),onChange:()=>j(_)}),i.jsx("i",{"aria-hidden":"true"})]})]},_)})})]}),i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(aa,{label:"Support desk",title:"Ticket panel",detail:"Configure the public panel and decide who can handle tickets.",icon:"users"}),i.jsxs("div",{className:"form-grid",children:[i.jsx(_t,{label:"Panel title",children:i.jsx("input",{value:c.panel_title,maxLength:200,onChange:_=>g("panel_title",_.target.value),placeholder:"Open a Ticket"})}),i.jsx(_t,{label:"Panel channel",children:i.jsxs("select",{value:S,onChange:_=>g("panel_channel_id",_.target.value),children:[i.jsx("option",{value:"",children:"Keep current panel channel"}),D.map(_=>i.jsxs("option",{value:_.id,children:["#",_.name]},_.id))]})}),i.jsx(_t,{label:"Panel description",children:i.jsx("textarea",{rows:4,maxLength:2e3,value:c.panel_description,onChange:_=>g("panel_description",_.target.value),placeholder:"Tell members what the ticket panel is for."})}),i.jsx("div",{className:"form-grid-wide",children:i.jsx(Jp,{label:"Ticket categories",hint:"Add a separate category for each ticket option.",options:c.panel_categories,placeholder:"Category",onChange:_=>g("panel_categories",_)})}),i.jsx(_t,{label:"Support roles",hint:"Hold Ctrl/Cmd to select more than one",children:i.jsx("select",{multiple:!0,value:c.support_roles,onChange:_=>g("support_roles",Array.from(_.target.selectedOptions,L=>L.value)),children:V.map(_=>i.jsxs("option",{value:_.id,children:["@",_.name]},_.id))})})]}),i.jsx("p",{className:"form-hint",children:"Saving panel settings updates the existing posted panel when Niko can find its saved message."})]}),i.jsx(q1,{state:h})]})]})}const uc=()=>({id:crypto.randomUUID(),prompt:"",required:!0,type:"paragraph",options:["",""]});function J1({guildId:t,resources:s,csrfToken:r}){const[o,c]=T.useState([]),[u,h]=T.useState(""),[p,f]=T.useState(""),[v,g]=T.useState(""),[x,b]=T.useState([]),[j,N]=T.useState([uc()]),[w,S]=T.useState(null),[B,P]=T.useState(!0),[D,V]=T.useState(!1),[_,L]=T.useState(""),[I,U]=T.useState(""),[ce,q]=T.useState(null),[ge,he]=T.useState([]),[Y,we]=T.useState(null),[me,Ce]=T.useState(""),ee=T.useCallback(()=>Ox(t).then(c),[t]);T.useEffect(()=>{P(!0),ee().catch(O=>L(O instanceof Error?O.message:"Applications could not be loaded.")).finally(()=>P(!1))},[ee]);const z=()=>{S(null),h(""),f(""),g(""),b([]),N([uc()])},Z=O=>{var le;S(O.id),h(O.title),f(O.description||""),g(O.role_id),b(O.eligible_role_ids||[]),N(O.questions.map(Q=>{var ne;return{id:Q.id,prompt:Q.prompt,required:Q.required,type:Q.type||"paragraph",options:(ne=Q.options)!=null&&ne.length?[...Q.options]:["",""]}})),L(""),U(""),(le=document.querySelector(".applications-editor"))==null||le.scrollIntoView({behavior:"smooth",block:"start"})},X=O=>{if(O.preventDefault(),j.some(fe=>["single_choice","multi_choice"].includes(fe.type)&&(fe.options.filter(Re=>Re.trim()).length<2||fe.options.some(Re=>!Re.trim())))){L("Each choice question needs at least two non-empty options.");return}V(!0),L(""),U("");const Q={title:u,description:p,role_id:v,eligible_role_ids:x,questions:j.map(({id:fe,prompt:Re,required:vt,type:Ht,options:Vn})=>({id:fe,prompt:Re,required:vt,type:Ht,options:Vn.map(Wi=>Wi.trim()).filter(Boolean)}))};(w?Ux(t,w,Q,r):zx(t,Q,r)).then(({application:fe})=>{c(Re=>w?Re.map(vt=>vt.id===fe.id?fe:vt):[fe,...Re]),z(),U(w?"Application updated. Its link and saved responses are unchanged.":"Application created. Its link is ready to share.")}).catch(fe=>L(fe instanceof Error?fe.message:"Application could not be saved.")).finally(()=>V(!1))},E=O=>{window.confirm(`Delete “${O.title}” and permanently remove its ${O.submission_count} response${O.submission_count===1?"":"s"}? This cannot be undone.`)&&Wx(t,O.id,r).then(()=>{c(le=>le.filter(Q=>Q.id!==O.id)),ce===O.id&&q(null),U("Application and its responses deleted."),L("")}).catch(le=>L(le instanceof Error?le.message:"Application could not be deleted."))},$=O=>{const le=O.status==="open"?"closed":"open";$x(t,O.id,le,r).then(()=>{c(Q=>Q.map(ne=>ne.id===O.id?{...ne,status:le}:ne)),U(le==="open"?"Opening reopened. The same link is active again.":"Opening closed. Its link and responses are preserved."),L("")}).catch(Q=>L(Q instanceof Error?Q.message:"Application status could not be changed."))},ye=O=>{if(ce===O.id){q(null);return}q(O.id),he([]),Hx(t,O.id).then(le=>he(le.submissions)).catch(le=>L(le instanceof Error?le.message:"Responses could not be loaded."))},ve=(O,le,Q)=>{Y||(we(le.user_id),L(""),U(""),Gx(t,O,le.user_id,Q,r).then(ne=>{he(fe=>fe.map(Re=>Re.user_id===le.user_id?{...Re,review_status:ne.review_status,reviewed_by:ne.reviewed_by,reviewed_at:ne.reviewed_at}:Re)),U(`Response ${Q}.`)}).catch(ne=>L(ne instanceof Error?ne.message:"Response review could not be saved.")).finally(()=>we(null)))},ke=async O=>{const le=`${window.location.origin}/apply/${t}/${O.id}`;try{await navigator.clipboard.writeText(le),Ce(O.id),window.setTimeout(()=>Ce(""),1800)}catch{L("Could not copy the link. Open it in a new tab and copy the address instead.")}};return i.jsxs(i.Fragment,{children:[i.jsx(hn,{eyebrow:"People · applications",title:"Build your next team.",text:"Keep separate role openings active at once. Close an opening when hiring pauses, then reopen the same link next time—past responses and one-time submissions stay attached."}),i.jsxs("div",{className:"applications-intro",children:[i.jsx("span",{className:"applications-intro-icon",children:i.jsx(J,{name:"users"})}),i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Hiring desk"}),i.jsxs("strong",{children:[o.filter(O=>O.status==="open").length," open · ",o.length," saved openings"]}),i.jsx("p",{children:"Each opening has its own stable public link and response archive."})]}),i.jsxs("a",{href:`/apply/${t}`,target:"_blank",rel:"noreferrer",className:"button button-muted button-small",children:["Preview server link ",i.jsx(J,{name:"arrow"})]})]}),_&&i.jsx("div",{className:"notice warning",role:"alert",children:_}),I&&i.jsx("div",{className:"notice applications-success",role:"status",children:I}),i.jsxs("section",{className:"applications-layout",children:[i.jsxs("form",{className:"dash-panel applications-editor",onSubmit:X,children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:w?"Edit opening":"New opening"}),i.jsx("h3",{children:w?"Update role application":"Create a role application"}),i.jsx("p",{children:w?"Changes apply to the existing link. Previously submitted answers remain attached.":"One saved opening per role and hiring round. Reopen it later to reuse its URL."})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(J,{name:w?"settings":"plus"})})]}),i.jsxs("div",{className:"form-grid applications-fields",children:[i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Opening title"}),i.jsx("input",{required:!0,maxLength:100,value:u,onChange:O=>h(O.target.value),placeholder:"Community moderator"})]}),i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Discord role"}),i.jsxs("select",{required:!0,value:v,onChange:O=>g(O.target.value),children:[i.jsx("option",{value:"",children:"Choose the role you’re hiring for"}),((s==null?void 0:s.roles)||[]).map(O=>i.jsxs("option",{value:O.id,children:["@",O.name]},O.id))]})]}),i.jsxs("label",{className:"form-field application-description",children:[i.jsx("span",{className:"form-label",children:"About this opening"}),i.jsx("textarea",{rows:3,maxLength:2e3,value:p,onChange:O=>f(O.target.value),placeholder:"Share what the role involves and who you’re looking for."})]}),i.jsxs("label",{className:"form-field application-role-gates",children:[i.jsx("span",{className:"form-label",children:"Eligibility role gates"}),i.jsx("select",{multiple:!0,value:x,onChange:O=>b(Array.from(O.target.selectedOptions,le=>le.value)),children:((s==null?void 0:s.roles)||[]).map(O=>i.jsxs("option",{value:O.id,children:["@",O.name]},O.id))}),i.jsx("small",{children:"Applicants need at least one selected role. Leave empty to allow any server member."})]})]}),i.jsxs("div",{className:"application-question-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"form-label",children:"Application questions"}),i.jsx("small",{children:"Ask up to 12 questions. Required answers must be completed."})]}),i.jsx("button",{type:"button",className:"button button-muted button-small",onClick:()=>N(O=>O.length<12?[...O,uc()]:O),disabled:j.length>=12,children:"＋ Add question"})]}),i.jsx("div",{className:"application-question-list",children:j.map((O,le)=>i.jsxs("div",{className:"application-question",children:[i.jsxs("label",{className:"form-field",children:[i.jsxs("span",{className:"form-label",children:["Question ",le+1]}),i.jsx("input",{required:!0,maxLength:240,value:O.prompt,onChange:Q=>N(ne=>ne.map(fe=>fe.id===O.id?{...fe,prompt:Q.target.value}:fe)),placeholder:"Why would you be a good fit?"})]}),i.jsxs("label",{className:"form-field application-type-field",children:[i.jsx("span",{className:"form-label",children:"Answer type"}),i.jsxs("select",{value:O.type,onChange:Q=>N(ne=>ne.map(fe=>fe.id===O.id?{...fe,type:Q.target.value}:fe)),children:[i.jsx("option",{value:"short_text",children:"Short text"}),i.jsx("option",{value:"paragraph",children:"Long answer"}),i.jsx("option",{value:"single_choice",children:"Choose one"}),i.jsx("option",{value:"multi_choice",children:"Choose many"}),i.jsx("option",{value:"yes_no",children:"Yes / no"}),i.jsx("option",{value:"date",children:"Date"})]})]}),["single_choice","multi_choice"].includes(O.type)&&i.jsxs("div",{className:"application-options-field",children:[i.jsxs("span",{className:"form-label",children:["Options ",i.jsx("small",{children:"At least two choices"})]}),i.jsx("div",{className:"application-option-list",children:O.options.map((Q,ne)=>i.jsxs("div",{className:"application-option-row",children:[i.jsx("input",{required:!0,maxLength:100,"aria-label":`Question ${le+1}, option ${ne+1}`,value:Q,onChange:fe=>N(Re=>Re.map(vt=>vt.id===O.id?{...vt,options:vt.options.map((Ht,Vn)=>Vn===ne?fe.target.value:Ht)}:vt)),placeholder:`Option ${ne+1}`}),i.jsx("button",{type:"button",className:"application-option-remove",onClick:()=>N(fe=>fe.map(Re=>Re.id===O.id?{...Re,options:Re.options.filter((vt,Ht)=>Ht!==ne)}:Re)),disabled:O.options.length<=2,"aria-label":`Remove option ${ne+1}`,children:"Remove"})]},`${O.id}-${ne}`))}),i.jsx("button",{type:"button",className:"button button-muted button-small application-option-add",onClick:()=>N(Q=>Q.map(ne=>ne.id===O.id&&ne.options.length<20?{...ne,options:[...ne.options,""]}:ne)),disabled:O.options.length>=20,children:"＋ Add option"})]}),i.jsxs("label",{className:"application-required",children:[i.jsx("input",{type:"checkbox",checked:O.required,onChange:Q=>N(ne=>ne.map(fe=>fe.id===O.id?{...fe,required:Q.target.checked}:fe))})," Required"]}),j.length>1&&i.jsx("button",{type:"button",className:"application-remove-question",onClick:()=>N(Q=>Q.filter(ne=>ne.id!==O.id)),"aria-label":`Remove question ${le+1}`,children:"×"})]},O.id))}),i.jsxs("div",{className:"setting-footer",children:[i.jsx("span",{children:w?"The share link and existing responses are kept.":"Your public application link requires Discord sign-in and server membership."}),i.jsxs("div",{className:"application-editor-actions",children:[w&&i.jsx("button",{className:"button button-muted",type:"button",onClick:z,disabled:D,children:"Cancel edit"}),i.jsx("button",{className:"button button-primary",type:"submit",disabled:D||!(s!=null&&s.roles.length),children:D?"Saving…":w?"Save changes":"Create opening"})]})]})]}),i.jsxs("aside",{className:"applications-aside dash-panel",children:[i.jsx("span",{className:"panel-kicker",children:"Applicant checks"}),i.jsx("h3",{children:"Fair, verified submissions."}),i.jsx("p",{children:"Niko confirms membership directly with Discord before showing or submitting a form. Selected role gates are checked against the applicant’s current server roles."}),i.jsxs("div",{className:"applications-check",children:[i.jsx("span",{children:"01"}),i.jsxs("div",{children:[i.jsx("strong",{children:"Discord identity"}),i.jsx("small",{children:"One verified account per response"})]})]}),i.jsxs("div",{className:"applications-check",children:[i.jsx("span",{children:"02"}),i.jsxs("div",{children:[i.jsx("strong",{children:"Server membership"}),i.jsx("small",{children:"Bot-verified at form load and submit"})]})]}),i.jsxs("div",{className:"applications-check",children:[i.jsx("span",{children:"03"}),i.jsxs("div",{children:[i.jsx("strong",{children:"One application per opening"}),i.jsx("small",{children:"Reopening never clears old submissions"})]})]})]})]}),i.jsxs("section",{className:"applications-list-section",children:[i.jsxs("div",{className:"section-heading-row",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Opening library"}),i.jsx("h3",{children:"Applications & responses"})]}),i.jsxs("span",{className:"section-count",children:[o.length," total"]})]}),B?i.jsx("div",{className:"empty-state",children:"Loading saved applications…"}):o.length===0?i.jsx("div",{className:"empty-state",children:"No applications yet. Create your first role opening above."}):i.jsx("div",{className:"applications-list",children:o.map(O=>{var le;return i.jsxs("article",{className:"application-card dash-panel",children:[i.jsxs("div",{className:"application-card-main",children:[i.jsx("div",{className:`application-status ${O.status}`,children:O.status==="open"?"Open":"Closed"}),i.jsx("h4",{children:O.title}),i.jsx("p",{children:O.description||"A role application for this server."}),i.jsxs("div",{className:"application-meta",children:[i.jsx("span",{children:((le=s==null?void 0:s.roles.find(Q=>Q.id===O.role_id))==null?void 0:le.name)||`Role ${O.role_id}`}),i.jsxs("span",{children:[O.submission_count," ",O.submission_count===1?"response":"responses"]}),i.jsx("span",{children:O.eligible_role_ids.length?`${O.eligible_role_ids.length} eligibility role${O.eligible_role_ids.length===1?"":"s"}`:"Open to all members"})]})]}),i.jsxs("div",{className:"application-card-actions",children:[i.jsxs("button",{className:"button button-muted button-small",onClick:()=>void ke(O),children:[i.jsx(J,{name:"link"})," ",me===O.id?"Copied":"Copy link"]}),i.jsxs("button",{className:"button button-muted button-small",onClick:()=>ye(O),children:[i.jsx(J,{name:"book"})," ",ce===O.id?"Hide responses":"Responses"]}),i.jsx("button",{className:"button button-muted button-small",onClick:()=>Z(O),children:"Edit"}),i.jsx("button",{className:`button button-small ${O.status==="open"?"button-muted":"button-primary"}`,onClick:()=>$(O),children:O.status==="open"?"Close opening":"Reopen"}),i.jsx("button",{className:"button button-small application-delete-button",onClick:()=>E(O),children:"Delete"})]}),ce===O.id&&i.jsx("div",{className:"application-response-list",children:ge.length===0?i.jsx("div",{className:"empty-state compact",children:"No responses yet, or loading…"}):ge.map(Q=>i.jsxs("details",{className:"application-response",children:[i.jsxs("summary",{children:[i.jsxs("span",{className:"application-response-identity",children:[Q.avatar_url&&i.jsx("img",{src:Q.avatar_url,alt:""}),i.jsx("strong",{children:Q.display_name})]}),i.jsx("time",{children:Q.submitted_at?new Date(`${Q.submitted_at}Z`).toLocaleString():"Submitted"})]}),i.jsx("div",{className:"application-answers",children:Q.answers.map(ne=>i.jsxs("div",{children:[i.jsx("strong",{children:ne.prompt}),i.jsx("p",{children:Array.isArray(ne.answer)?ne.answer.join(", ")||"No answer provided.":ne.answer||"No answer provided."})]},ne.question_id))}),i.jsxs("footer",{className:"application-review-footer",children:[i.jsx("span",{className:`application-review-status ${Q.review_status}`,role:"status",children:Q.review_status==="pending"?"Awaiting review":Q.review_status==="approved"?"Approved":"Denied"}),i.jsxs("div",{className:"application-review-actions",children:[i.jsx("button",{type:"button",className:`button button-small application-review-approve${Q.review_status==="approved"?" is-selected":""}`,onClick:()=>ve(O.id,Q,"approved"),disabled:Y!==null,"aria-pressed":Q.review_status==="approved",children:"Approve"}),i.jsx("button",{type:"button",className:`button button-small application-review-deny${Q.review_status==="denied"?" is-selected":""}`,onClick:()=>ve(O.id,Q,"denied"),disabled:Y!==null,"aria-pressed":Q.review_status==="denied",children:"Deny"})]})]})]},Q.user_id))})]},O.id)})})]})]})}function Z1({auth:t}){const s=Ln();return i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"dashboard"}),i.jsx("main",{className:"auth-page",children:i.jsxs("div",{className:"auth-card",children:[i.jsx("span",{className:"auth-mark",children:"n"}),i.jsx("div",{className:"eyebrow",children:"Private workspace"}),i.jsxs("h1",{children:["Settle in, ",i.jsx("em",{children:"admin."})]}),i.jsx("p",{children:"Sign in with Discord to see your Niko profile and manage the servers you look after."}),t.oauth_available?i.jsxs("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard",children:[i.jsx(J,{name:"lock"})," Continue with Discord ",i.jsx(J,{name:"arrow"})]}):i.jsxs("div",{className:"notice warning",children:["Discord login is not configured yet. Add ",i.jsx("code",{children:"DISCORD_CLIENT_SECRET"})," to the environment and restart the bot."]}),!s&&i.jsx("p",{className:"form-hint",children:"The public bot configuration is still loading."}),i.jsx("a",{className:"back-link",href:"/",onClick:r=>{r.preventDefault(),be("/")},children:"Return to public site"})]})})]})}function eS({section:t,guild:s,stats:r,csrfToken:o,refreshToken:c}){const[u,h]=T.useState(null),[p,f]=T.useState([]),[v,g]=T.useState(null),[x,b]=T.useState(null),[j,N]=T.useState(!0),[w,S]=T.useState("");return T.useEffect(()=>{N(!0),S(""),(t==="overview"?Fx(s.id).then(h):t==="leveling"?Promise.all([Bx(s.id),Cm(s.id),$l(s.id)]).then(([P,D,V])=>{f(P),g(D),b(V)}):t==="applications"?$l(s.id).then(b):Promise.all([Cm(s.id),$l(s.id)]).then(([P,D])=>{g(P),b(D)})).catch(P=>S(P instanceof Error?P.message:"This server could not be loaded.")).finally(()=>N(!1))},[s.id,t,c]),j?i.jsxs("div",{className:"section-loading section-skeleton",role:"status","aria-label":`Loading ${t}`,children:[i.jsx("div",{className:"skeleton-title"}),i.jsx("div",{className:"skeleton-copy"}),i.jsxs("div",{className:"skeleton-grid",children:[i.jsx("i",{}),i.jsx("i",{}),i.jsx("i",{})]}),i.jsxs("span",{children:["Loading ",t,"..."]})]}):w?i.jsxs("div",{className:"inline-error",role:"alert",children:[i.jsx("strong",{children:"Couldn’t load this page."}),i.jsx("span",{children:w}),i.jsx("button",{className:"button button-muted",onClick:()=>window.location.reload(),children:"Try again"})]}):t==="overview"&&u?i.jsx(O1,{overview:u}):t==="leveling"?i.jsx(z1,{guildId:s.id,rows:p,config:v,resources:x,csrfToken:o}):t==="moderation"?i.jsx($1,{guildId:s.id,config:v,csrfToken:o}):t==="server"?i.jsx(Q1,{guildId:s.id,config:v,resources:x,csrfToken:o}):t==="applications"?i.jsx(J1,{guildId:s.id,resources:x,csrfToken:o}):t==="customization"?i.jsx(G1,{guildId:s.id,config:v,csrfToken:o}):i.jsx(W1,{guildId:s.id,config:v,csrfToken:o})}function tS(){return i.jsxs("div",{className:"section-loading section-skeleton dashboard-loading",role:"status",children:[i.jsx("div",{className:"skeleton-title"}),i.jsx("div",{className:"skeleton-copy"}),i.jsxs("div",{className:"skeleton-grid",children:[i.jsx("i",{}),i.jsx("i",{}),i.jsx("i",{})]}),i.jsx("span",{children:"Preparing your dashboard..."})]})}function nS(){Ln();const[t,s]=T.useState(Am),[r,o]=T.useState(null),[c,u]=T.useState(null),[h,p]=T.useState(null),[f,v]=T.useState([]),[g,x]=T.useState(null),[b,j]=T.useState(!0),[N,w]=T.useState(""),[S,B]=T.useState(0),[P,D]=T.useState(!1),[V,_]=T.useState(null);if(T.useEffect(()=>{const Y=()=>s(Am());return window.addEventListener("popstate",Y),()=>window.removeEventListener("popstate",Y)},[]),T.useEffect(()=>{j(!0),Promise.all([va(),xa()]).then(([Y,we])=>(o(Y),u(we),Y.authenticated?Promise.all([Nm(),pc(),mc().catch(()=>null)]).then(([me,Ce,ee])=>{p(me),v(Ce),_((ee==null?void 0:ee.role)||null)}):null)).catch(Y=>w(Y instanceof Error?Y.message:"Dashboard unavailable")).finally(()=>j(!1))},[]),T.useEffect(()=>{if(t.view!=="guild"){x(null);return}const Y=f.find(we=>we.id===t.guildId&&we.installed!==!1);Y?(x(Y),localStorage.setItem("niko-guild",Y.id)):t.guildId&&f.length&&be(fc())},[f,t.guildId,t.view]),b||!r)return i.jsxs("div",{className:"dashboard-state",children:[i.jsx("div",{className:"loading-ring"}),i.jsx("p",{children:"Connecting to Niko…"})]});if(N)return i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"dashboard"}),i.jsx("main",{className:"auth-page",children:i.jsxs("div",{className:"auth-card",children:[i.jsx("span",{className:"auth-mark",children:"!"}),i.jsx("div",{className:"eyebrow",children:"Connection issue"}),i.jsxs("h1",{children:["Couldn’t load",i.jsx("br",{}),i.jsx("em",{children:"your workspace."})]}),i.jsx("p",{children:N}),i.jsxs("button",{className:"button button-primary",onClick:()=>window.location.reload(),children:["Try again ",i.jsx(J,{name:"arrow"})]})]})})]});if(!r.authenticated)return i.jsx(Z1,{auth:r});const L=Y=>{Y.installed!==!1&&(localStorage.setItem("niko-guild",Y.id),be(Rs(Y.id,t.section)))},I=Y=>{Y.installed!==!1&&(localStorage.setItem("niko-guild",Y.id),be(Rs(Y.id,"overview")))},U=Y=>{be(g?Rs(g.id,Y):Rs())},ce=()=>be(Rs()),q=()=>be(fc()),ge=async()=>{if(!P){D(!0);try{const[Y,we]=await Promise.all([va(),xa()]);if(o(Y),u(we),Y.authenticated){const[me,Ce,ee]=await Promise.all([Nm(),pc(),mc().catch(()=>null)]);p(me),v(Ce),_((ee==null?void 0:ee.role)||null)}B(me=>me+1),w("")}catch(Y){w(Y instanceof Error?Y.message:"Dashboard refresh failed")}finally{D(!1)}}};let he;return t.view==="servers"?he=i.jsx(B1,{guilds:f,onManage:I}):t.view==="guild"?he=g?i.jsx(eS,{section:t.section,guild:g,stats:c,csrfToken:r.csrf_token,refreshToken:S},`${g.id}-${t.section}`):i.jsx(tS,{}):he=i.jsx(F1,{user:r.user,overview:h,guilds:f,onServers:q,onManage:I}),i.jsx(_f,{user:r.user,guilds:f,selectedGuild:g,view:t.view,section:t.section,stats:c,onHome:ce,onServers:q,onGuildChange:L,onSectionChange:U,onRefresh:ge,refreshing:P,staffRole:V,children:he})}function sS({value:t,onChange:s,placeholder:r="Search documentation...",onFocus:o,onBlur:c}){const[u,h]=T.useState(!1),p=T.useRef(null),[f,v]=T.useState(!1);T.useEffect(()=>{const N=w=>{var S;(w.metaKey||w.ctrlKey)&&w.key==="k"&&(w.preventDefault(),(S=p.current)==null||S.focus())};return document.addEventListener("keydown",N),()=>document.removeEventListener("keydown",N)},[]);const g=()=>{h(!0),v(!0),o==null||o()},x=()=>{h(!1),setTimeout(()=>v(!1),200),c==null||c()},b=N=>{s(N.target.value)},j=N=>{var w;N.key==="Escape"&&((w=p.current)==null||w.blur())};return i.jsxs("div",{className:`doc-search-bar ${f?"expanded":""}`,children:[i.jsxs("div",{className:"search-input-wrapper",children:[i.jsx(J,{name:"search",className:"search-icon"}),i.jsx("input",{ref:p,type:"text",value:t,onChange:b,onFocus:g,onBlur:x,onKeyDown:j,placeholder:r,className:"search-input","aria-label":"Search documentation"}),i.jsxs("kbd",{className:"search-shortcut",children:[i.jsx("span",{className:"shortcut-key",children:"⌘"}),"K"]})]}),i.jsxs("div",{className:"search-hint",children:["Press ",i.jsx("kbd",{children:"⌘K"})," to focus search"]})]})}function iS({selectedCategory:t,onSelectCategory:s,sections:r,allCategoriesLabel:o="All Categories"}){return i.jsx("div",{className:"doc-filters",children:i.jsxs("div",{className:"filter-tabs",role:"tablist","aria-label":"Filter by category",children:[i.jsx("button",{role:"tab","aria-selected":t==="",className:`filter-tab ${t===""?"active":""}`,onClick:()=>s(""),children:o}),r.map(c=>i.jsxs("button",{role:"tab","aria-selected":t===c.id,className:`filter-tab ${t===c.id?"active":""}`,onClick:()=>s(c.id),children:[i.jsx(J,{name:c.icon,size:14}),i.jsx("span",{children:c.label})]},c.id))]})})}function dc({doc:t,variant:s="default"}){const r="page"in t?t.page:t,[o,c]=T.useState(!1),u=f=>{f.preventDefault(),be(`/docs/${r.slug}`)},h=f=>{(f.key==="Enter"||f.key===" ")&&(f.preventDefault(),be(`/docs/${r.slug}`))};if(s==="compact")return i.jsx("a",{href:`/docs/${r.slug}`,onClick:u,onKeyDown:h,className:"doc-card-compact",tabIndex:0,role:"button",children:i.jsxs("div",{className:"compact-content",children:[i.jsx("span",{className:"compact-title",children:r.title}),i.jsx("span",{className:"compact-excerpt",children:r.excerpt})]})});const p="highlights"in t?t.highlights:[];return i.jsx("article",{className:`doc-card ${s==="highlighted"?"highlighted":""}`,children:i.jsxs("div",{className:`doc-card-content ${o?"loaded":""}`,children:[i.jsxs("div",{className:"doc-card-header",children:[i.jsx("span",{className:"doc-category",children:r.category.replace(/-/g," ")}),i.jsxs("span",{className:"doc-order",children:["#",r.order]})]}),i.jsx("h3",{className:"doc-title",children:r.title}),i.jsx("p",{className:"doc-excerpt",children:r.excerpt}),p.length>0&&i.jsx("div",{className:"doc-highlights",children:p.slice(0,2).map((f,v)=>i.jsxs("p",{className:"highlight-snippet",children:[f.slice(0,150),f.length>150?"...":""]},v))}),i.jsxs("div",{className:"doc-card-footer",children:[i.jsx("div",{className:"doc-tags",children:r.tags.slice(0,3).map(f=>i.jsxs("span",{className:"doc-tag",children:["#",f]},f))}),i.jsxs("a",{href:`/docs/${r.slug}`,onClick:u,onKeyDown:h,className:"doc-read-more",children:["Read more ",i.jsx(J,{name:"arrow",size:14})]})]})]})})}const He=[{slug:"welcome",title:"Welcome to Niko",category:"getting-started",excerpt:"New to Niko? Start here to understand what the bot can do for your server.",tags:["introduction","overview","beginner"],order:1,content:`
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
    `}];function rS(t){return He.find(s=>s.slug===t)}const Dn=[{id:"getting-started",label:"Getting Started",description:"New to Niko? Start here.",icon:"icon_home",count:He.filter(t=>t.category==="getting-started").length},{id:"setup",label:"Setup",description:"Configure Niko for your server.",icon:"icon_settings",count:He.filter(t=>t.category==="setup").length},{id:"economy",label:"Economy",description:"Money, jobs, banking, and more.",icon:"icon_economy",count:He.filter(t=>t.category==="economy").length},{id:"leveling",label:"Leveling",description:"XP, levels, and rankings.",icon:"icon_leveling",count:He.filter(t=>t.category==="leveling").length},{id:"moderation",label:"Moderation",description:"Moderation tools and commands.",icon:"icon_moderation",count:He.filter(t=>t.category==="moderation").length},{id:"automod",label:"AutoMod",description:"Automated moderation features.",icon:"icon_automod",count:He.filter(t=>t.category==="automod").length},{id:"logging",label:"Logging",description:"Server event logging.",icon:"icon_settings",count:He.filter(t=>t.category==="logging").length},{id:"social",label:"Social",description:"Community engagement features.",icon:"icon_heart",count:He.filter(t=>t.category==="social").length},{id:"utility",label:"Utility",description:"Helpful tools and utilities.",icon:"icon_utility",count:He.filter(t=>t.category==="utility").length},{id:"voice",label:"Voice",description:"Voice and music features.",icon:"icon_bot",count:He.filter(t=>t.category==="voice").length},{id:"ai",label:"AI",description:"AI-powered features.",icon:"icon_ai",count:He.filter(t=>t.category==="ai").length},{id:"dashboard",label:"Dashboard",description:"Web dashboard guides.",icon:"icon_settings",count:He.filter(t=>t.category==="dashboard").length},{id:"tips",label:"Tips",description:"Tips and best practices.",icon:"icon_lightbulb",count:He.filter(t=>t.category==="tips").length}];function yy(){const[t,s]=T.useState({query:"",category:"",tags:[]}),r=T.useCallback(f=>{s(v=>({...v,query:f.toLowerCase(),tags:[]}))},[]),o=T.useCallback(f=>{s(v=>({...v,category:f,tags:[]}))},[]),c=T.useCallback(f=>{s(v=>{const g=v.tags.includes(f)?v.tags.filter(x=>x!==f):[...v.tags,f];return{...v,tags:g,query:""}})},[]),u=T.useCallback(()=>{s({query:"",category:"",tags:[]})},[]),h=T.useMemo(()=>{const{query:f,category:v,tags:g}=t;if(!f&&!v&&g.length===0)return He.map(b=>({page:b,score:1,highlights:[]}));const x=[];for(const b of He)if(!(v&&b.category!==v)&&!(g.length>0&&!g.some(j=>b.tags.includes(j))))if(f){const j=aS(b,f);if(j===0)continue;const N=oS(b,f);x.push({page:b,score:j,highlights:N})}else x.push({page:b,score:1,highlights:[]});return x.sort((b,j)=>j.score!==b.score?j.score-b.score:b.page.order-j.page.order),x},[t]),p=t.query!==""||t.category!==""||t.tags.length>0;return{filters:t,setQuery:r,setCategory:o,toggleTag:c,clearFilters:u,results:h,hasActiveFilters:p,resultCount:h.length}}function aS(t,s){let r=0;const o=s.toLowerCase();t.title.toLowerCase()===o?r+=100:t.title.toLowerCase().includes(o)&&(r+=50),t.excerpt.toLowerCase().includes(o)&&(r+=25),t.content.toLowerCase().includes(o)&&(r+=10);for(const c of t.tags)c.toLowerCase().includes(o)&&(r+=15);return t.category.toLowerCase().includes(o)&&(r+=5),r}function oS(t,s){const r=[],o=s.toLowerCase(),c=3;if(t.title.toLowerCase().includes(o)&&(r.push(t.title),r.length>=c)||t.excerpt.toLowerCase().includes(o)&&(r.push(t.excerpt),r.length>=c))return r;const u=t.content.split(`
`).filter(h=>h.trim());for(const h of u)if(h.toLowerCase().includes(o)){const p=h.replace(/#{1,6}\s?/g,"").trim();if(p.length>10&&(r.push(p),r.length>=c))break}return r}function lS(){return T.useMemo(()=>{const s={};return He.forEach(r=>{r.tags.forEach(o=>{s[o]=(s[o]||0)+1})}),Object.entries(s).map(([r,o])=>({tag:r,count:o})).sort((r,o)=>o.count-r.count)},[])}function cS({slug:t}){var f,v;const{setCategory:s,clearFilters:r}=yy();T.useEffect(()=>{window.location.hash!==`#/docs/${t}`&&window.history.replaceState(null,"",`#/docs/${t}`)},[t]);const o=rS(t);if(!o)return i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"docs"}),i.jsx("main",{className:"shell page-main docs-page",children:i.jsxs("div",{className:"docs-not-found",children:[i.jsx(J,{name:"doc",size:48,className:"not-found-icon"}),i.jsx("h1",{children:"Page Not Found"}),i.jsxs("p",{children:[`We couldn't find documentation for "`,t,'".']}),i.jsxs("div",{className:"not-found-actions",children:[i.jsx("button",{onClick:()=>be("/docs"),children:"Browse all documentation"}),i.jsx("button",{onClick:()=>{be("/docs"),r()},children:"Clear filters"})]})]})}),i.jsx(Nt,{})]});const c=g=>{const x=[],b=/(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*)/g;let j=0,N,w=0;for(;(N=b.exec(g))!==null;){N.index>j&&x.push(g.slice(j,N.index));const S=N[0];if(S.startsWith("`")&&S.endsWith("`")&&S.length>2)x.push(i.jsx("code",{className:"doc-inline-code",children:S.slice(1,-1)},w++));else if(S.startsWith("[")){const B=S.match(/^\[([^\]]+)\]\(([^)]+)\)$/);B?x.push(i.jsx("a",{href:B[2],target:"_blank",rel:"noreferrer",children:c(B[1])},w++)):x.push(S)}else S.startsWith("**")?x.push(i.jsx("strong",{children:c(S.slice(2,-2))},w++)):S.startsWith("*")?x.push(i.jsx("em",{children:c(S.slice(1,-1))},w++)):x.push(S);j=N.index+S.length}return j<g.length&&x.push(g.slice(j)),x},h=(g=>{const x=g.split(`
`),b=[];let j=0,N=null,w=[];const S=()=>{if(w.length===0)return;const P=N==="ol"?"ol":"ul";b.push(i.jsx(P,{className:`doc-content-list ${N==="ol"?"doc-content-list-ol":""}`,children:w.map((D,V)=>i.jsx("li",{children:c(D)},V))},`list-${b.length}`)),w=[],N=null},B=()=>{var V;const P=b[b.length-1];T.isValidElement(P)&&((V=P.props)==null?void 0:V.className)==="doc-content-spacer"||b.push(i.jsx("div",{className:"doc-content-spacer"},`spacer-${b.length}`))};for(;j<x.length;){const D=x[j].trim();if(!D){S(),B(),j+=1;continue}if(D.startsWith("```")){S();const L=[];let I=j+1;for(;I<x.length&&x[I].trim()!=="```";)L.push(x[I]),I+=1;b.push(i.jsx("pre",{className:"doc-code-block",children:i.jsx("code",{children:L.join(`
`)})},`code-${j}`)),j=I+1;continue}if(D.startsWith("|")){S();const L=[];let I=j;for(;I<x.length&&x[I].trim().startsWith("|");){const ge=x[I].trim().replace(/^\|/,"").replace(/\|$/,"").split("|").map(he=>he.trim());L.push(ge),I+=1}const U=L.length>1&&L[1].every(ge=>/^:?-{2,}:?$/.test(ge.replace(/\s+/g,""))),ce=L[0],q=U?L.slice(2):L.slice(1);ce.length>1&&b.push(i.jsxs("table",{className:"doc-table",children:[i.jsx("thead",{children:i.jsx("tr",{children:ce.map((ge,he)=>i.jsx("th",{children:c(ge)},he))})}),i.jsx("tbody",{children:q.map((ge,he)=>i.jsx("tr",{children:ge.map((Y,we)=>i.jsx("td",{children:c(Y)},we))},he))})]},`table-${j}`)),j=I;continue}if(D.startsWith("### ")){S(),b.push(i.jsx("h4",{className:"doc-heading doc-heading-h4",children:D.slice(4)},`h-${j}`)),j+=1;continue}if(D.startsWith("## ")){S(),b.push(i.jsx("h3",{className:"doc-heading doc-heading-h3",children:D.slice(3)},`h-${j}`)),j+=1;continue}if(D.startsWith("# ")){S(),b.push(i.jsx("h2",{className:"doc-heading doc-heading-h2",children:D.slice(2)},`h-${j}`)),j+=1;continue}if(D.startsWith("> ")){S(),b.push(i.jsx("blockquote",{className:"doc-blockquote",children:c(D.slice(2))},`q-${j}`)),j+=1;continue}const V=D.match(/^[-*]\s+(.*)$/);if(V){N!=="ul"&&S(),N="ul",w.push(V[1]),j+=1;continue}const _=D.match(/^\d+\.\s+(.*)$/);if(_){N!=="ol"&&S(),N="ol",w.push(_[1]),j+=1;continue}S(),b.push(i.jsx("p",{className:"doc-paragraph",children:c(D)},`p-${j}`)),j+=1}return S(),b})(o.content),p=h.filter(g=>T.isValidElement(g)&&(g.type==="h2"||g.type==="h3"));return i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"docs"}),i.jsxs("main",{className:"shell page-main docs-page docs-detail-page",children:[i.jsx("div",{className:"docs-detail-back",children:i.jsxs("button",{onClick:()=>be("/docs"),className:"back-button",children:[i.jsx(J,{name:"arrow",size:16}),"Back to Documentation"]})}),i.jsxs("header",{className:"doc-article-header",children:[i.jsxs("div",{className:"doc-article-meta",children:[i.jsx("span",{className:"doc-category-badge",children:((f=Dn.find(g=>g.id===o.category))==null?void 0:f.label)||o.category}),i.jsxs("span",{className:"doc-order-badge",children:["Article #",o.order]})]}),i.jsx("h1",{className:"doc-article-title",children:o.title}),i.jsx("p",{className:"doc-article-excerpt",children:o.excerpt}),i.jsx("div",{className:"doc-article-tags",children:o.tags.map(g=>i.jsxs("span",{className:"doc-tag-pill",children:["#",g]},g))})]}),i.jsx("article",{className:"doc-article-content",children:h}),i.jsx("footer",{className:"doc-article-footer",children:i.jsx("div",{className:"doc-nav-container",children:i.jsxs("div",{className:"doc-nav-col",children:[i.jsx("span",{className:"doc-nav-label",children:"Category"}),i.jsxs("button",{className:"doc-nav-link",onClick:()=>{s(o.category),be("/docs")},children:[i.jsx(J,{name:"arrow",size:14}),"View all ",(v=Dn.find(g=>g.id===o.category))==null?void 0:v.label]})]})})}),p.length>0&&i.jsxs("aside",{className:"doc-toc",children:[i.jsxs("div",{className:"toc-title",children:[i.jsx(J,{name:"utility",size:16}),i.jsx("span",{children:"On this page"})]}),i.jsx("nav",{className:"toc-nav",children:p.map((g,x)=>{var j;const b=(j=g.props.className)==null?void 0:j.includes("doc-heading-h2");return i.jsx("a",{href:`#${b?"h2-":"h3-"}-${x}`,className:`toc-link ${b?"toc-h2":"toc-h3"}`,children:g.props.children},x)})})]})]}),i.jsx(Nt,{})]})}function uS(){var V,_;const[t,s]=T.useState(!1),[r,o]=T.useState(""),[c,u]=T.useState(!1),{filters:h,setQuery:p,setCategory:f,toggleTag:v,clearFilters:g,results:x,hasActiveFilters:b,resultCount:j}=yy(),N=lS();T.useEffect(()=>{const L=()=>{const I=window.location.hash.slice(1);if(I.startsWith("#/docs/")){const U=I.replace("#/docs/",""),ce=He.find(q=>q.slug===U);ce&&(o(ce.category),f(ce.category))}};return L(),window.addEventListener("hashchange",L),()=>window.removeEventListener("hashchange",L)},[]);const w=()=>{u(!0)},S=L=>{o(L),f(L),s(!1)},B=()=>{h.query||u(!1)},P=L=>{be(`/docs/${L}`),p(""),u(!1)},D=T.useMemo(()=>{const L={};return x.forEach(I=>{const U=I.page.category;L[U]||(L[U]=[]),L[U].push(I)}),L},[x]);return i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"docs"}),i.jsxs("main",{className:"shell page-main docs-page",children:[i.jsx("div",{className:"docs-hero",children:i.jsxs("div",{className:"docs-hero-content",children:[i.jsx("div",{className:"eyebrow docs-eyebrow",children:"Documentation Center"}),i.jsxs("h1",{className:"docs-title",children:["Everything you need to know about",i.jsx("br",{}),i.jsx("span",{className:"title-accent",children:"using Niko"})]}),i.jsx("p",{className:"docs-subtitle",children:"Comprehensive guides, command references, and tips to help you get the most out of your server bot."})]})}),i.jsx("div",{className:`docs-search-section ${c?"active":""}`,children:i.jsxs("div",{className:"docs-search-container",children:[i.jsx(sS,{value:h.query,onChange:p,placeholder:"Search documentation, commands, guides...",onFocus:w,onBlur:B}),c&&h.query&&x.length>0&&i.jsxs("div",{className:"search-results-dropdown",children:[i.jsxs("div",{className:"search-results-header",children:[i.jsxs("span",{className:"results-count",children:[j," ",j===1?"result":"results"]}),i.jsx("button",{className:"clear-search-btn",onClick:()=>{p(""),g(),o("")},children:"Clear"})]}),i.jsx("div",{className:"search-results-list",children:x.slice(0,8).map((L,I)=>i.jsxs("button",{className:"search-result-item",onClick:()=>P(L.page.slug),onMouseEnter:()=>{},children:[i.jsx("div",{className:"result-icon",children:i.jsx(J,{name:"doc",size:18})}),i.jsxs("div",{className:"result-content",children:[i.jsx("div",{className:"result-title",children:L.page.title}),i.jsx("div",{className:"result-excerpt",children:L.page.excerpt}),L.highlights.length>0&&i.jsxs("div",{className:"result-highlight",children:[L.highlights[0].slice(0,100),"..."]})]}),i.jsx(J,{name:"arrow",size:14,className:"result-arrow"})]},L.page.slug))}),x.length>8&&i.jsx("div",{className:"search-results-footer",children:i.jsxs("span",{children:["Showing 8 of ",x.length," results. Browse all docs below."]})})]})]})}),i.jsxs("div",{className:"docs-mobile-nav",children:[i.jsx("button",{className:"mobile-menu-toggle",onClick:()=>s(!t),"aria-label":"Toggle documentation menu",children:i.jsx(J,{name:"utility",size:20})}),t&&i.jsxs("div",{className:"mobile-nav-panel",children:[i.jsxs("div",{className:"mobile-nav-header",children:[i.jsx("h3",{children:"Documentation"}),i.jsx("button",{className:"close-menu-btn",onClick:()=>s(!1),"aria-label":"Close menu",children:i.jsx(J,{name:"utility",size:16,className:"rotated"})})]}),i.jsx("div",{className:"mobile-nav-sections",children:Dn.map(L=>i.jsxs("button",{className:`mobile-nav-item ${r===L.id?"active":""}`,onClick:()=>{S(L.id)},children:[i.jsx(J,{name:L.icon,size:18}),i.jsx("span",{className:"mobile-section-label",children:L.label}),i.jsx("span",{className:"mobile-section-count",children:L.count})]},L.id))})]})]}),N.length>0&&!b&&i.jsxs("div",{className:"docs-tags-cloud",children:[i.jsxs("div",{className:"tags-cloud-title",children:[i.jsx(J,{name:"utility",size:16}),i.jsx("span",{children:"Popular Topics"})]}),i.jsx("div",{className:"tags-cloud-list",children:N.slice(0,15).map(({tag:L,count:I})=>i.jsxs("button",{className:"tag-cloud-item",onClick:()=>v(L),style:{fontSize:`${.75+Math.min(I/4,1)}rem`},children:["#",L,i.jsx("span",{className:"tag-count",children:I})]},L))})]}),i.jsx("div",{className:"docs-category-filters",children:i.jsx(iS,{selectedCategory:h.category,onSelectCategory:S,sections:Dn})}),b&&i.jsxs("div",{className:"docs-results-header",children:[i.jsxs("div",{className:"results-info",children:[i.jsxs("span",{className:"results-count-large",children:[j," ",j===1?"article":"articles"]}),h.query&&i.jsxs("span",{className:"search-query-display",children:['for "',i.jsx("strong",{children:h.query}),'"']})]}),i.jsxs("button",{className:"clear-all-btn",onClick:()=>{g(),o("")},disabled:!b,children:[i.jsx(J,{name:"utility",size:14}),"Clear all filters"]})]}),i.jsx("div",{className:"docs-content",children:b?i.jsx("div",{className:"search-results-view",children:Object.entries(D).map(([L,I])=>{var U;return i.jsxs("section",{className:"results-category",children:[i.jsx("h2",{className:"category-title",children:((U=Dn.find(ce=>ce.id===L))==null?void 0:U.label)||L}),i.jsx("div",{className:"category-results-grid",children:I.map(ce=>i.jsx(dc,{doc:ce,variant:"highlighted"},ce.page.slug))})]},L)})}):r?i.jsxs("div",{className:"category-view",children:[i.jsxs("div",{className:"category-header",children:[i.jsx("h2",{className:"category-page-title",children:((V=Dn.find(L=>L.id===r))==null?void 0:V.label)||r}),i.jsx("p",{className:"category-description",children:(_=Dn.find(L=>L.id===r))==null?void 0:_.description})]}),i.jsx("div",{className:"category-articles",children:He.filter(L=>L.category===r).sort((L,I)=>L.order-I.order).map(L=>i.jsx(dc,{doc:L},L.slug))})]}):i.jsx("div",{className:"all-categories-view",children:Dn.map(L=>i.jsxs("section",{className:"docs-section",id:`section-${L.id}`,children:[i.jsxs("div",{className:"section-header",children:[i.jsx("div",{className:"section-icon",children:i.jsx(J,{name:L.icon,size:28})}),i.jsxs("div",{className:"section-info",children:[i.jsx("h2",{className:"section-title",children:L.label}),i.jsx("p",{className:"section-description",children:L.description})]}),i.jsx("span",{className:"section-count",children:L.count})]}),i.jsx("div",{className:"section-articles",children:He.filter(I=>I.category===L.id).sort((I,U)=>I.order-U.order).map(I=>i.jsx(dc,{doc:I},I.slug))})]},L.id))})}),i.jsxs("div",{className:"docs-footer-note",children:[i.jsx(J,{name:"book",size:20}),i.jsxs("div",{children:[i.jsx("strong",{children:"Want more detail?"}),i.jsxs("p",{children:["The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in the"," ",i.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"docs/"})," ","folder."]})]})]})]}),i.jsx(Nt,{})]})}function dS(){const t=Ln(),[s,r]=T.useState(null);T.useEffect(()=>{xa().then(r).catch(()=>{})},[]);const o=[["spark","AI that remembers","Thoughtful conversation with a cozy personality and controls that respect your community."],["chart","A living economy","Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],["shield","Confident moderation","Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],["users","Community rituals","Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."]];return i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"home"}),i.jsxs("main",{children:[i.jsxs("section",{className:"hero shell",children:[i.jsxs("div",{className:"hero-copy",children:[i.jsxs("div",{className:"eyebrow",children:[i.jsx("span",{className:"status-dot"})," Discord companion · online"]}),i.jsxs("div",{className:"hero-identity",children:[i.jsx("span",{className:"hero-avatar",children:t!=null&&t.bot_avatar_url?i.jsx("img",{src:t.bot_avatar_url,alt:"Niko"}):"n"}),i.jsxs("span",{children:[i.jsx("strong",{children:"Niko"}),i.jsx("small",{children:"Your server’s calm, capable co-pilot"})]})]}),i.jsxs("h1",{children:["Useful tools for a ",i.jsx("em",{children:"better server."})]}),i.jsx("p",{children:"Niko handles the everyday work of running a Discord community, so your moderators can focus on the people in it."}),i.jsxs("div",{className:"hero-buttons",children:[i.jsxs("a",{className:"button button-primary",href:(t==null?void 0:t.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Invite Niko ",i.jsx(J,{name:"arrow"})]}),i.jsx("a",{className:"button button-muted",href:"/commands",onClick:c=>{c.preventDefault(),be("/commands")},children:"Explore commands"})]}),i.jsxs("div",{className:"stats-strip",children:[i.jsxs("div",{children:[i.jsx("strong",{children:Ne(s==null?void 0:s.guild_count)}),i.jsx("span",{children:"servers"})]}),i.jsxs("div",{children:[i.jsx("strong",{children:Ne(s==null?void 0:s.user_count)}),i.jsx("span",{children:"members"})]}),i.jsxs("div",{children:[i.jsx("strong",{children:Ne(s==null?void 0:s.command_count)}),i.jsx("span",{children:"commands"})]})]})]}),i.jsx("div",{className:"hero-art","aria-label":"A preview of Niko's server workspace",children:i.jsxs("div",{className:"workspace-preview",children:[i.jsxs("div",{className:"workspace-preview-top",children:[i.jsxs("span",{className:"preview-dots",children:[i.jsx("i",{}),i.jsx("i",{}),i.jsx("i",{})]}),i.jsx("span",{children:"server workspace"}),i.jsxs("span",{className:"preview-status",children:[i.jsx("span",{className:"status-dot"})," live"]})]}),i.jsxs("div",{className:"preview-body",children:[i.jsxs("div",{className:"preview-sidebar",children:[i.jsx("span",{className:"preview-label",children:"NIKO"}),i.jsx("b",{children:"Overview"}),i.jsx("span",{children:"Economy"}),i.jsx("span",{children:"Leveling"}),i.jsx("span",{children:"Moderation"}),i.jsx("span",{children:"AI controls"})]}),i.jsxs("div",{className:"preview-main",children:[i.jsx("span",{className:"preview-label",children:"SERVER SNAPSHOT"}),i.jsx("strong",{children:"Everything in one place."}),i.jsxs("div",{className:"preview-stats",children:[i.jsxs("span",{children:[i.jsx("b",{children:Ne(s==null?void 0:s.user_count)}),i.jsx("small",{children:"members"})]}),i.jsxs("span",{children:[i.jsx("b",{children:Ne(s==null?void 0:s.command_count)}),i.jsx("small",{children:"commands"})]})]}),i.jsxs("div",{className:"preview-line",children:[i.jsx("i",{}),i.jsx("i",{}),i.jsx("i",{})]})]})]})]})})]}),i.jsxs("section",{className:"shell intro-section",children:[i.jsx("div",{className:"section-kicker",children:"Why Niko"}),i.jsxs("div",{className:"intro-grid",children:[i.jsxs("h2",{children:["The good kind of",i.jsx("br",{}),i.jsx("em",{children:"always-on."})]}),i.jsx("p",{children:"Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile."})]})]}),i.jsx("section",{className:"shell feature-grid",children:o.map(([c,u,h])=>i.jsxs("article",{className:"feature-card",children:[i.jsx("span",{className:"feature-icon",children:i.jsx(J,{name:c})}),i.jsx("h3",{children:u}),i.jsx("p",{children:h}),i.jsxs("a",{href:"/docs",onClick:p=>{p.preventDefault(),be("/docs")},children:["Learn more ",i.jsx(J,{name:"arrow"})]})]},u))}),i.jsxs("section",{className:"shell callout",children:[i.jsxs("div",{children:[i.jsx("div",{className:"section-kicker",children:"Ready when you are"}),i.jsxs("h2",{children:["A calmer, cleverer home",i.jsx("br",{}),"for your community."]})]}),i.jsxs("a",{className:"button button-primary",href:(t==null?void 0:t.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Bring Niko in ",i.jsx(J,{name:"arrow"})]})]})]}),i.jsx(Nt,{})]})}const hS=[{code:"USDT",label:"Tether"},{code:"ETH",label:"Ethereum"},{code:"BTC",label:"Bitcoin"},{code:"BNB",label:"BNB"},{code:"LTC",label:"Litecoin"},{code:"DOGE",label:"Dogecoin"},{code:"TRX",label:"TRON"},{code:"XMR",label:"Monero"}];function mS(){const s=new URLSearchParams(window.location.search).get("token")||"",[r,o]=T.useState("5"),[c,u]=T.useState("USDT"),[h,p]=T.useState(!1),[f,v]=T.useState(""),[g,x]=T.useState(null),[b,j]=T.useState(null),[N,w]=T.useState(!1);T.useEffect(()=>{s||w(!0)},[s]),T.useEffect(()=>{if(!(g!=null&&g.status_url)||g.paid)return;const B=setInterval(async()=>{try{const P=await Ae(g.status_url);j(P),P.paid&&clearInterval(B)}catch{}},5e3);return()=>clearInterval(B)},[g]);const S=async B=>{B.preventDefault(),p(!0),v("");try{const P=await Ae("/api/donations/invoice",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:s,amount:parseFloat(r),currency:c})});x(P),P.error&&(v(P.error),x(null))}catch(P){v(P instanceof Error?P.message:"Could not create invoice.")}finally{p(!1)}};return N?i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"home"}),i.jsx("main",{className:"auth-page",children:i.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[i.jsx("span",{className:"auth-mark",children:"!"}),i.jsx("div",{className:"eyebrow",children:"Invalid donation link"}),i.jsxs("h1",{children:["This link is ",i.jsx("em",{children:"invalid."})]}),i.jsxs("p",{children:["The donation link is missing or has expired. Use the"," ",i.jsx("code",{children:"/donate"})," command in Discord to generate a new one."]}),i.jsx("button",{className:"button button-primary full-width",onClick:()=>be("/"),children:"Return home"})]})})]}):b!=null&&b.paid?i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"home"}),i.jsx("main",{className:"auth-page",children:i.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[i.jsx("span",{className:"auth-mark",children:"✓"}),i.jsx("div",{className:"eyebrow",children:"Payment confirmed"}),i.jsxs("h1",{children:["Thank you ",i.jsx("em",{children:"for supporting!"})]}),i.jsx("p",{children:"Your donation has been confirmed. You will receive the Supporter badge shortly."}),i.jsx("button",{className:"button button-primary full-width",onClick:()=>be("/"),children:"Return home"})]})})]}):i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"home"}),i.jsx("main",{className:"page-main",children:i.jsx("div",{className:"shell",children:i.jsxs("div",{className:"page-heading",style:{maxWidth:500,margin:"0 auto"},children:[i.jsx("div",{className:"eyebrow",style:{marginBottom:15},children:"Support Niko"}),i.jsxs("h1",{children:["Keep Niko ",i.jsx("em",{children:"running."})]}),i.jsx("p",{style:{color:"var(--muted)",marginBottom:30},children:"Your donation helps cover hosting costs and keeps Niko running for all servers. Choose an amount and cryptocurrency below."}),g!=null&&g.pay_link?i.jsxs("div",{className:"dash-panel",style:{marginBottom:24},children:[i.jsx("div",{className:"panel-heading",children:i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Invoice created"}),i.jsx("h3",{children:"Complete your payment"})]})}),i.jsxs("p",{style:{color:"var(--muted)",fontSize:12,marginBottom:16},children:["Amount: ",i.jsxs("strong",{children:["$",parseFloat(r).toFixed(2)," USD"]})," in"," ",i.jsx("strong",{children:c})]}),i.jsxs("p",{style:{color:"var(--dim)",fontSize:10,marginBottom:16},children:["Track ID: ",i.jsx("code",{children:g.track_id})," · Expires in 60 minutes"]}),i.jsxs("a",{className:"button button-primary",href:g.pay_link,target:"_blank",rel:"noopener noreferrer",children:["Pay now ",i.jsx(J,{name:"arrow"})]}),i.jsx("p",{style:{color:"var(--dim)",fontSize:10,marginTop:12},children:"Payment will be confirmed automatically once the transaction is processed on-chain."})]}):i.jsxs("form",{onSubmit:S,className:"dash-panel",style:{marginBottom:24},children:[i.jsxs("div",{className:"form-grid",children:[i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Amount (USD)"}),i.jsx("input",{type:"number",min:"1",max:"10000",step:"0.01",value:r,onChange:B=>o(B.target.value)}),i.jsx("small",{children:"Minimum $1.00, maximum $10,000.00"})]}),i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Cryptocurrency"}),i.jsx("select",{value:c,onChange:B=>u(B.target.value),children:hS.map(B=>i.jsxs("option",{value:B.code,children:[B.label," (",B.code,")"]},B.code))})]})]}),f&&i.jsx("p",{className:"form-error",style:{marginTop:12},role:"alert",children:f}),i.jsx("div",{style:{marginTop:16},children:i.jsx("button",{className:"button button-primary",type:"submit",disabled:h,children:h?"Creating invoice…":"Create invoice"})})]}),i.jsxs("div",{className:"docs-footer-note",style:{marginTop:20},children:[i.jsx("strong",{children:"How it works"}),i.jsx("p",{children:'1. Choose an amount and currency above · 2. Click "Pay now" to open the payment page · 3. Send crypto to the displayed address · 4. Payment is confirmed automatically once processed on-chain'})]})]})})})]})}const pS="1 October 2026",fS={privacy:{title:"Privacy policy",intro:"Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",sections:[["Information we use","User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature. The dashboard stores daily aggregate message, join, and leave counts without message text or member IDs."],["Scam-image filter (experimental)","When a member reports a message through the right-click scam report, the reported images and message context are sent to Niko staff for review. On confirmation, a perceptual hash (a compact numeric fingerprint) and a copy of the image are stored so similar images can be detected and removed automatically. Nothing is stored for servers without the filter enabled."],["Social notifier","If a server follows social accounts, only the account name, platform, last-seen post ID, and target channel are stored."],["How it is used","Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],["Storage and retention","Data is stored by the server hosting Niko in a database (SQLite or MongoDB, depending on deployment). Economy, leveling, and configuration data remain until removed. Daily server activity totals are retained as aggregates. AI conversation history is limited and can be cleared with /clearhistory."],["Third-party services","When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Other features may contact their respective services (social platforms for the notifier, Google Translate for translations); only the minimum data needed for the feature is shared."],["Your choices","Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."]]},terms:{title:"Terms of service",intro:"By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",sections:[["Permitted use","Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],["Availability","Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],["Moderation","The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],["AI content","AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],["Virtual items","In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],["Contact","Questions or concerns can be sent through the Niko support server."]]},community:{title:"Community policy",intro:"These community expectations apply to every server that uses Niko. By adding the bot to a server, the server's owners and administrators agree to uphold these standards.",sections:[["Purpose","Niko is a community companion for Discord servers of all kinds. To keep the platform safe for everyone, all servers using Niko must follow the expectations below in addition to Discord's Terms of Service and Community Guidelines."],["Discrimination and harassment","Servers must not permit or promote discrimination, harassment, or hate speech targeting people based on race, ethnicity, national origin, religion, disability, gender, gender identity or expression, sexual orientation, age, veteran status, or any other protected identity characteristic."],["Illegal and malicious content","Servers must not create, host, share, or distribute illegal or malicious content. This includes, but is not limited to: child sexual abuse material (CSAM), malware and other malicious software, gore or shock content, pirated media and/or software, content that facilitates violence or terrorism, scams and phishing, and any other content that is illegal under applicable law."],["Other prohibited conduct","Servers must not use Niko to facilitate doxxing, targeted harassment campaigns, sextortion, trafficking, or the sexualization of minors in any form."],["Enforcement and investigations","When a server is reported or flagged for potentially violating this policy, Niko will send a warning notice to the server. The notice is followed by an investigation by Niko staff. Servers that cooperate in good faith and are found not to be breaking the policies will not receive any further action."],["Obstruction of investigations","Banning, kicking, or otherwise removing the staff member(s) sent to investigate, or hiding, deleting, or tampering with potential evidence, is treated as an admission of guilt. Doing so will result in the server — and any users who are involved — being permanently blacklisted from further use of Niko, in addition to any other action the investigation warrants."],["Reporting","If you believe a server using Niko is violating this policy, report it through the Niko support server. Reports are reviewed by staff and handled confidentially."]]}};function hc({type:t}){const s=fS[t];return i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:t}),i.jsxs("main",{className:"shell page-main legal-page",children:[i.jsxs("div",{className:"page-heading",children:[i.jsx("div",{className:"eyebrow",children:"Niko legal"}),i.jsx("h1",{children:s.title}),i.jsx("p",{children:s.intro}),i.jsxs("small",{children:["Effective date: ",pS]})]}),i.jsx("div",{className:"legal-copy",children:s.sections.map(([r,o])=>i.jsxs("section",{children:[i.jsx("h2",{children:r}),i.jsx("p",{children:o})]},r))})]}),i.jsx(Nt,{})]})}const gS=[{key:"txt",label:"TXT",icon:"📄"},{key:"html",label:"HTML",icon:"🌐"},{key:"csv",label:"CSV",icon:"📊"},{key:"json",label:"JSON",icon:"{ }"}],vy=t=>typeof t!="number"||t<0||t>16777215?"":`#${t.toString(16).padStart(6,"0")}`,is=t=>(t==null?void 0:t.url)||(t==null?void 0:t.proxy_url)||"",xy=t=>/\.(?:png|jpe?g|gif|webp|bmp|svg)(?:[?#]|$)/i.test(t)||t.startsWith("data:image/"),by=t=>/\.(?:mp4|webm|mov|m4v|ogg)(?:[?#]|$)/i.test(t)||t.startsWith("data:video/"),yS=t=>t.url?t.url:t.id?`https://cdn.discordapp.com/stickers/${t.id}.${t.format_type===4?"gif":"png"}`:"";function vS(t){var r;const s=is(t);return s?(r=t==null?void 0:t.content_type)!=null&&r.startsWith("video/")?!0:by(s):!1}const tf=new RegExp("(`[^`\\n]+`)|(\\[([^\\]\\n]+)\\]\\((https?:\\/\\/[^\\s)\\] ]+)\\))|(\\*\\*)|(?<!\\*)\\*(?!\\*)|(~~)","g"),xS=/(https?:\/\/[^\s<>)]+)/g,nf={bold:"**",italic:"*",strike:"~~"},bS=new Set(["t","T","d","D","f","F","R"]);function wS(t,s){if(!Number.isFinite(t)||!bS.has(s))return null;const r=new Date(t*1e3);if(Number.isNaN(r.getTime()))return null;if(s==="R"){const c=t-Math.floor(Date.now()/1e3),u=Math.abs(c),h=u<60?"second":u<3600?"minute":u<86400?"hour":u<604800?"day":u<2592e3?"week":u<31536e3?"month":"year",p=h==="second"?1:h==="minute"?60:h==="hour"?3600:h==="day"?86400:h==="week"?604800:h==="month"?2592e3:31536e3;return new Intl.RelativeTimeFormat(void 0,{numeric:"always"}).format(Math.round(c/p),h)}const o={...s==="t"||s==="T"?{hour:"numeric",minute:"2-digit"}:{},...s==="T"?{second:"2-digit"}:{},...s==="d"?{year:"numeric",month:"2-digit",day:"2-digit"}:{},...s==="D"?{year:"numeric",month:"long",day:"numeric"}:{},...s==="f"?{year:"numeric",month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}:{},...s==="F"?{weekday:"long",year:"numeric",month:"long",day:"numeric",hour:"numeric",minute:"2-digit"}:{}};return new Intl.DateTimeFormat(void 0,o).format(r)}function kS(t){const s=[];let r=0,o;const c=u=>{if(!u)return;const h=u.split(/(<a?:[A-Za-z0-9_~]+:\d+>|<t:-?\d+:[tTdDfFR]>)/g);for(const p of h){if(!p)continue;const f=p.match(/^<(a?):([A-Za-z0-9_~]+):(\d+)>$/);if(f){s.push({type:"emoji",name:f[2],id:f[3],animated:f[1]==="a"});continue}const v=p.match(/^<t:(-?\d+):([tTdDfFR])>$/);if(v){s.push({type:"timestamp",unix:Number(v[1]),style:v[2],raw:p});continue}const g=p.split(xS);for(let x=0;x<g.length;x++)g[x]&&(x%2===1?s.push({type:"link",text:g[x],url:g[x]}):s.push({type:"text",text:g[x]}))}};for(tf.lastIndex=0;(o=tf.exec(t))!==null;)o.index>r&&c(t.slice(r,o.index)),o[1]!==void 0?s.push({type:"code",text:o[1].slice(1,-1)}):o[2]!==void 0?s.push({type:"link",text:o[3],url:o[4]}):o[5]!==void 0?s.push({type:"marker",fmt:"bold"}):o[6]!==void 0?s.push({type:"marker",fmt:"italic"}):o[7]!==void 0&&s.push({type:"marker",fmt:"strike"}),r=o.index+o[0].length;return r<t.length&&c(t.slice(r)),s}function jS(t){const s=[],r=[],o=new Set,c=u=>{r.length>0?r[r.length-1].children.push(u):s.push(u)};for(const u of kS(t))if(u.type==="text")c({kind:"text",text:u.text});else if(u.type==="code")c({kind:"code",text:u.text});else if(u.type==="link")c({kind:"link",text:u.text,url:u.url});else if(u.type==="emoji")c({kind:"emoji",name:u.name,id:u.id,animated:u.animated});else if(u.type==="timestamp")c({kind:"timestamp",unix:u.unix,style:u.style,raw:u.raw});else if(u.type==="marker")if(o.has(u.fmt)){const h=r.map(v=>v.fmt).lastIndexOf(u.fmt),p=r.splice(h);p.forEach(v=>o.delete(v.fmt));const f={kind:"fmt",fmt:u.fmt,children:[...p[0].children]};for(const v of p.slice(1))f.children.push({kind:"text",text:nf[v.fmt]??""}),f.children.push(...v.children);c(f)}else r.push({fmt:u.fmt,children:[]}),o.add(u.fmt);if(r.length>0)for(const u of r){c({kind:"text",text:nf[u.fmt]??""});for(const h of u.children)c(h)}return s}const wy=(t,s)=>t.map((r,o)=>{const c=`${s}-${o}`;switch(r.kind){case"text":return i.jsx("span",{children:r.text},c);case"code":return i.jsx("code",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:4,padding:"0 5px",color:"#f2b8c2",fontFamily:"monospace",fontSize:"0.92em"},children:r.text},c);case"emoji":return i.jsx("img",{src:`https://cdn.discordapp.com/emojis/${r.id}.${r.animated?"gif":"png"}`,alt:`:${r.name}:`,title:`:${r.name}:`,style:{width:22,height:22,objectFit:"contain",verticalAlign:"-0.35em",display:"inline-block"},onError:u=>{u.currentTarget.alt=`:${r.name}:`}},c);case"timestamp":{const u=wS(r.unix,r.style);return u?i.jsx("time",{dateTime:new Date(r.unix*1e3).toISOString(),title:r.raw,children:u},c):i.jsx("span",{children:r.raw},c)}case"link":return i.jsx("a",{href:r.url,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",textDecoration:"none"},onMouseEnter:u=>{u.currentTarget.style.textDecoration="underline"},onMouseLeave:u=>{u.currentTarget.style.textDecoration="none"},children:r.text},c);case"fmt":{const u={};return r.fmt==="bold"&&(u.fontWeight=700),r.fmt==="italic"&&(u.fontStyle="italic"),r.fmt==="strike"&&(u.textDecoration="line-through"),i.jsx("span",{style:u,children:wy(r.children,c)},c)}}}),la=t=>wy(jS(t),"md");function es({text:t,muted:s}){const r=t.split(`
`),o=[];return r.forEach((c,u)=>{const h=c.trimStart(),f=u===r.length-1?null:i.jsx("br",{},`br${u}`);h.startsWith("-# ")?o.push(i.jsxs("span",{style:{color:s?"#6d737a":"#949ba4",fontSize:12},children:[la(h.slice(3)),f]},u)):/^#{1,4}\s/.test(h)?o.push(i.jsxs("span",{style:{color:"#f2f3f5",fontWeight:700,fontSize:16},children:[la(h),f]},u)):h.startsWith("> ")?o.push(i.jsxs("span",{style:{display:"inline-block",color:"#b5bac1",borderLeft:"3px solid #4e5058",paddingLeft:8},children:[la(h.slice(2)),f]},u)):h.startsWith("```")?o.push(i.jsxs("pre",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:6,padding:"10px 12px",overflowX:"auto",whiteSpace:"pre-wrap",wordBreak:"break-word",fontFamily:"monospace",fontSize:12.5,color:"#dbdee1",margin:"2px 0"},children:[h.replace(/^```[a-zA-Z]*/,"").replace(/```$/,""),f]},u)):o.push(i.jsxs("span",{children:[la(c),f]},u))}),i.jsx("span",{style:{whiteSpace:"pre-wrap",wordBreak:"break-word"},children:o})}function SS({embed:t}){const s=vy(t.color)||"#5865f2",r=t.author,o=t.footer,c=is(t.thumbnail),u=is(t.image);return i.jsxs("div",{style:{display:"flex",gap:12,maxWidth:560,marginTop:8,background:"#2b2d31",border:"1px solid #3f4147",borderLeft:`4px solid ${s}`,borderRadius:6,padding:"10px 12px"},children:[i.jsxs("div",{style:{flex:1,minWidth:0},children:[(r==null?void 0:r.name)&&i.jsxs("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:4},children:[r.icon_url&&i.jsx("img",{src:r.icon_url||r.proxy_icon_url,alt:"",style:{width:18,height:18,borderRadius:"50%",verticalAlign:"-4px",marginRight:6}}),r.name]}),t.title&&i.jsx("div",{style:{color:"#00a8fc",fontWeight:600,margin:"2px 0 4px",fontSize:14},children:t.url?i.jsx("a",{href:t.url,target:"_blank",rel:"noopener noreferrer",style:{color:"inherit",textDecoration:"none"},children:i.jsx(es,{text:t.title})}):i.jsx(es,{text:t.title})}),t.description&&i.jsx("div",{style:{color:"#dbdee1",fontSize:13,lineHeight:1.5},children:i.jsx(es,{text:t.description})}),t.fields&&t.fields.length>0&&i.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:"6px 12px",marginTop:8},children:t.fields.map((h,p)=>i.jsxs("div",{style:{flex:h.inline?"0 1 45%":"1 1 100%",minWidth:0,marginBottom:4},children:[h.name&&i.jsx("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:2},children:i.jsx(es,{text:h.name})}),h.value&&i.jsx("div",{style:{color:"#dbdee1",fontSize:13},children:i.jsx(es,{text:h.value})})]},p))}),u&&i.jsx("a",{href:u,target:"_blank",rel:"noopener noreferrer",style:{display:"block",marginTop:8},children:i.jsx("img",{src:u,alt:"",style:{maxWidth:"100%",maxHeight:300,borderRadius:4,display:"block"},onError:h=>{h.currentTarget.style.display="none"}})}),((o==null?void 0:o.text)||t.timestamp)&&i.jsxs("div",{style:{display:"flex",alignItems:"center",gap:6,marginTop:6,color:"#949ba4",fontSize:11},children:[(o==null?void 0:o.icon_url)&&i.jsx("img",{src:o.icon_url||o.proxy_icon_url,alt:"",style:{width:16,height:16,borderRadius:"50%"}}),(o==null?void 0:o.text)&&i.jsx("span",{children:o.text}),t.timestamp&&i.jsx("span",{children:String(t.timestamp).replace("T"," ").replace("+00:00"," UTC")})]})]}),c&&i.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:i.jsx("img",{src:c,alt:"",style:{width:80,height:80,borderRadius:6,objectFit:"cover"},onError:h=>{h.currentTarget.style.display="none"}})})]})}function ya({component:t}){switch(t.type){case 17:{const s=vy(t.accent_color);return i.jsxs("div",{style:{display:"flex",overflow:"hidden",maxWidth:560,marginTop:8,background:"#2b2d31",border:`1px solid ${s||"#3f4147"}`,borderRadius:12},children:[s&&i.jsx("div",{style:{flex:"0 0 4px",background:s}}),i.jsx("div",{style:{flex:1,minWidth:0,padding:"6px 12px 8px"},children:(t.components||[]).map((r,o)=>i.jsx(ya,{component:r},o))})]})}case 1:return i.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,margin:"6px 0"},children:(t.components||[]).map((s,r)=>i.jsx(ya,{component:s},r))});case 2:{const s=t.emoji,r=`${(s==null?void 0:s.name)??""}${t.label?` ${t.label}`:""}`.trim();return t.style===5&&!!t.url?i.jsx("a",{href:t.url,target:"_blank",rel:"noopener noreferrer",style:{display:"inline-block",padding:"3px 14px",background:"#5865f2",borderRadius:4,color:"#fff",fontSize:13,fontWeight:600,textDecoration:"none"},children:r||"Button"}):i.jsx("span",{style:{display:"inline-block",padding:"3px 14px",background:"#4e5058",borderRadius:4,color:t.disabled?"#8a8e96":"#f2f3f5",fontSize:13,cursor:t.disabled?"not-allowed":"default",opacity:t.disabled?.55:1},children:r||"Button"})}case 9:{const s=[...t.components||[]];return t.accessory&&s.push(t.accessory),i.jsx("div",{style:{display:"flex",alignItems:"center",gap:10,margin:"4px 0"},children:s.map((r,o)=>i.jsx(ya,{component:r},o))})}case 10:return i.jsx("div",{style:{color:"#dbdee1",fontSize:14,lineHeight:1.5,margin:"4px 0",wordBreak:"break-word"},children:i.jsx(es,{text:t.content||""})});case 18:return i.jsx("div",{style:{color:"#f2f3f5",fontWeight:700,textTransform:"uppercase",letterSpacing:"0.04em",fontSize:12,margin:"4px 0"},children:t.content});case 14:return i.jsx("div",{style:{margin:t.divider===!1?"6px 0":"9px 0",...t.divider===!1?{}:{borderTop:"1px solid #3f4147"}}});case 11:{const s=is(t.media);return s?i.jsx("a",{href:s,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:i.jsx("img",{src:s,alt:t.description||"",style:{width:40,height:40,borderRadius:"50%",objectFit:"cover",display:"block"},onError:r=>{r.currentTarget.style.display="none"}})}):null}case 12:{const r=(t.items||[]).filter(o=>is(o.media));return r.length===0?null:i.jsx("div",{style:{display:"grid",gridTemplateColumns:`repeat(auto-fill, minmax(${Math.min(220,Math.max(140,Math.floor(560/Math.max(1,r.length))))}px, 1fr))`,gap:6,margin:"6px 0"},children:r.map((o,c)=>{const u=is(o.media),h=o.description;return vS(o.media)?i.jsxs("figure",{style:{margin:0},children:[i.jsx("video",{src:u,controls:!0,preload:"metadata",style:{width:"100%",maxHeight:260,borderRadius:6,background:"#1e1f22"}}),h&&i.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:h})]},c):xy(u)?i.jsxs("figure",{style:{margin:0},children:[i.jsx("a",{href:u,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:i.jsx("img",{src:u,alt:h||"",style:{width:"100%",maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:p=>{p.currentTarget.style.display="none"}})}),h&&i.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:h})]},c):i.jsxs("a",{href:u,target:"_blank",rel:"noopener noreferrer",style:{display:"flex",alignItems:"center",gap:6,padding:"6px 10px",background:"#383a40",borderRadius:6,color:"#dbdee1",fontSize:12,textDecoration:"none"},children:["📎 ",h||"Attachment"]},c)})})}case 13:{const s=is(t.media)||t.url||"";return s?i.jsxs("a",{href:s,target:"_blank",rel:"noopener noreferrer",style:{display:"block",margin:"4px 0",color:"#00a8fc",fontSize:12.5,textDecoration:"none"},children:["📎 ",t.label||"Attachment"]}):null}default:return null}}function NS({components:t}){return i.jsx(i.Fragment,{children:t.map((s,r)=>i.jsx(ya,{component:s},r))})}function CS({text:t}){return i.jsx(es,{text:t})}function TS({msg:t}){const s=!!(t.attachments&&t.attachments.length>0||t.embeds&&t.embeds.length>0||t.components&&t.components.length>0||t.stickers&&t.stickers.length>0);return i.jsxs("div",{style:{padding:"10px 16px",borderBottom:"1px solid #2b2d31",fontSize:14,lineHeight:1.6},children:[i.jsxs("div",{style:{marginBottom:2},children:[i.jsx("span",{style:{color:"#949ba4",fontSize:11,fontFamily:"monospace"},children:t.timestamp})," ",i.jsx("span",{style:{color:"#f2f3f5",fontWeight:600},children:t.author})," ",i.jsxs("span",{style:{color:"#949ba4",fontSize:11},children:["(",t.author_id,")"]})]}),t.content?i.jsx("div",{style:{color:"#dbdee1"},children:i.jsx(CS,{text:t.content})}):s?null:i.jsx("div",{style:{color:"#6d737a",fontStyle:"italic",fontSize:13},children:"Message content unavailable"}),t.attachments&&t.attachments.length>0&&i.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:4},children:t.attachments.map((r,o)=>by(r)?i.jsx("video",{src:r,controls:!0,preload:"metadata",style:{maxWidth:360,maxHeight:260,borderRadius:6,background:"#1e1f22"}},o):xy(r)?i.jsx("a",{href:r,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:i.jsx("img",{src:r,alt:"",style:{maxWidth:300,maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:c=>{const u=c.currentTarget;u.style.display="none"}})},o):i.jsx("a",{href:r,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",fontSize:12,textDecoration:"none"},children:"📎 Attachment"},o))}),t.embeds&&t.embeds.length>0&&i.jsx(i.Fragment,{children:t.embeds.map((r,o)=>i.jsx(SS,{embed:r},o))}),t.stickers&&t.stickers.length>0&&i.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:8},children:t.stickers.map((r,o)=>{const c=yS(r);return c?i.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:i.jsx("img",{src:c,alt:r.name||"Discord sticker",title:r.name||"Discord sticker",style:{width:160,maxWidth:"100%",maxHeight:160,objectFit:"contain",display:"block"}})},o):null})}),t.components&&t.components.length>0&&i.jsx(NS,{components:t.components})]})}function AS({transcriptId:t}){const[s,r]=T.useState(null),[o,c]=T.useState(!0),[u,h]=T.useState("");T.useEffect(()=>{c(!0),h(""),fetch(`/api/transcript/${t}`).then(f=>{if(!f.ok)throw new Error("Transcript not found");return f.json()}).then(f=>{r(f),c(!1)}).catch(f=>{h(f.message||"Failed to load transcript"),c(!1)})},[t]);const p=f=>{window.open(`/api/transcript/${t}/download?format=${f}`,"_blank")};return o?i.jsx("div",{className:"page-main",children:i.jsx("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:i.jsx("div",{style:{color:"var(--muted)",fontSize:14},children:"Loading transcript…"})})}):u||!s?i.jsx("div",{className:"page-main",children:i.jsxs("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:[i.jsx("h2",{style:{marginBottom:12},children:"Transcript not found"}),i.jsx("p",{style:{color:"var(--muted)"},children:u||"This transcript doesn't exist or has been deleted."})]})}):i.jsx("div",{className:"page-main",children:i.jsxs("div",{className:"shell",style:{maxWidth:800},children:[i.jsx("div",{style:{background:"var(--surface)",border:"1px solid var(--line)",borderRadius:8,padding:24,marginBottom:20},children:i.jsxs("div",{style:{display:"flex",alignItems:"flex-start",justifyContent:"space-between",gap:16,flexWrap:"wrap"},children:[i.jsxs("div",{children:[i.jsx("div",{className:"eyebrow",style:{marginBottom:8},children:"Ticket Transcript"}),i.jsxs("h1",{style:{fontSize:24,letterSpacing:"-0.04em",margin:0},children:["#",s.channel_name]}),i.jsxs("div",{style:{color:"var(--muted)",fontSize:13,marginTop:6},children:[s.category," · ",s.message_count," messages · ",s.created_at]})]}),i.jsx("div",{style:{display:"flex",gap:8,flexWrap:"wrap"},children:gS.map(f=>i.jsxs("button",{className:"button button-small button-muted",onClick:()=>p(f.key),style:{minWidth:70},children:[i.jsx("span",{children:f.icon}),i.jsx("span",{children:f.label})]},f.key))})]})}),i.jsxs("div",{style:{background:"#1e1f22",border:"1px solid #3f4147",borderRadius:8,overflow:"hidden"},children:[s.messages.map((f,v)=>i.jsx(TS,{msg:f},v)),s.messages.length===0&&i.jsx("div",{style:{padding:40,textAlign:"center",color:"#949ba4"},children:"No messages in this transcript."})]}),i.jsxs("div",{style:{marginTop:16,padding:"12px 0",textAlign:"center",color:"var(--dim)",fontSize:12},children:["Transcript ID: ",i.jsx("code",{style:{fontFamily:"monospace"},children:t})]})]})})}const Ra=[{slug:"scam-image-filter",title:"Scam Image Filter (Experimental)",date:"2026-10-01",tags:["automod","scam","images","experimental","dashboard","discord"],summary:"A community-driven image filter that catches known MrBeast scam images: members report suspicious messages, Niko staff verify them, and confirmed images are then detected and removed automatically — with a feedback loop that lets servers flag false positives to improve accuracy. The feature is still in early testing and may have some reliability issues.",highlights:[{title:"One-Click Reporting",description:"Anyone can right-click a suspicious message and choose “Report MrBeast Scam”. The message's image assets, author, server, and a jump link are forwarded to the scam review queue in Niko's private staff server.",icon:"users"},{title:"Perceptual Hash Detection",description:"Confirmed images are fingerprinted with a 64-bit difference hash and compared by visual similarity, so resized, re-compressed, and re-encoded copies of a known scam image are still caught — even when the file itself is different.",icon:"shield"},{title:"Staff-Verified Review Queue",description:"Nothing enters the filter automatically. Niko staff review each report and press Confirm Scam (or Reject). Multi-image reports store a fingerprint for every image, and confirmations work offline because hashes are captured at report time.",icon:"utility"},{title:"False-Positive Feedback Loop",description:"Every removal is logged to the server's automod log channel with the original images and a “Report False Positive” button. Reports land back in the staff queue where a “Remove From Filter” action deletes the hash, steadily improving accuracy.",icon:"message"}],changes:[{category:"added",items:["“🚩 Report MrBeast Scam” message context-menu command that forwards image assets and context to the staff-only review channel","Persistent Confirm Scam / Reject buttons on review reports that survive bot restarts, restricted to Niko staff","Perceptual image fingerprinting (64-bit dHash with Hamming-distance matching) so re-encoded and resized scam variants are detected","Automatic deletion of messages matching confirmed scam hashes in servers that enable the filter, with per-hash deletion counters","Automod log channel entry for every removal, including the original image gallery and a Report False Positive button","False-positive review cards with a Remove From Filter action so mis-detections can be pulled from the database","Per-guild Scam Images toggle in the /automod command panel (all languages) and the dashboard's AutoMod modules","Experimental badge and early-testing warning on both the command panel and the dashboard","Dedicated database tables for confirmed scam hashes and report history, with counter tracking for deletions and false positives"]},{category:"improved",items:["Application-command error routing so every slash and context-menu failure now replies to the user instead of failing silently","Automod log delivery works identically on both SQLite and MongoDB deployments","Attachments no longer wake the AI on their own — images and voice only add context when Niko is triggered by name, ping, or command"]}],commits:[]},{slug:"staff-applications",title:"Staff Applications",date:"2026-09-29",tags:["applications","staff","dashboard","discord"],summary:"Guild dashboards can now manage multiple staff role openings with shareable web forms, Discord membership and eligibility checks, and reusable application links.",highlights:[{title:"Multiple Role Openings",description:"Create a separate application for each role, add custom questions, and optionally limit applications to members with selected server roles.",icon:"users"},{title:"Reusable Application Links",description:"Close an opening when hiring pauses and reopen it later with the same link. Earlier responses remain saved, and each Discord account can apply only once per opening.",icon:"utility"},{title:"Verified Applicant Forms",description:"Applicants sign in with Discord, and Niko verifies server membership and role eligibility before accepting a response. Managers can review submissions in the guild dashboard.",icon:"shield"}],changes:[{category:"added",items:["Guild dashboard tab to create and manage staff application openings","Custom application questions and optional role-based eligibility gates","Public Discord-authenticated application forms with bot-verified server membership","Stable per-opening application links, close/reopen controls, and response review","Database-enforced one-submission-per-user limit for each opening"]}],commits:[]},{slug:"server-logging-onboarding-updates",title:"Logging Reliability & Onboarding Rules",date:"2026-09-29",tags:["logging","onboarding","dashboard"],summary:"Server event logs are less likely to be delayed during busy periods, and onboarding now gives communities more room to share their rules with new members.",highlights:[{title:"More Reliable Server Logs",description:"Server event logs are less likely to be delayed during busy periods, helping moderation and activity updates stay easier to follow.",icon:"utility"},{title:"Longer Onboarding Rules",description:"Server rules in onboarding can now be up to 4,000 characters, making it easier to share complete guidelines with new members.",icon:"doc"}],changes:[{category:"improved",items:["Server event log delivery reliability during busy periods","Onboarding rules support for up to 4,000 characters"]}],commits:[]},{slug:"uwulock-starboard-overhaul",title:"UwU Lock Rebuilt & Starboard Persistence",date:"2026-09-25",version:"2.11.0",tags:["uwulock","starboard","database","fun","social"],summary:"The UwU Lock command has been completely rebuilt around the main database with immediate webhook reposts, reliable message transforms, and full Starboard integration — with proper author attribution that persists cleanly across restarts.",highlights:[{title:"Instant Webhook Transforms",description:"Locked users' messages are now deleted and immediately reposted via a shared per-channel webhook with their display name and avatar, including attachments, embeds, and stickers, with thread support and a guard against double-processing.",icon:"spark"},{title:"Real Author on the Starboard",description:"When a uwu-ified webhook message is starred, the Starboard resolves the original author from persistent attribution and renders their name, avatar, and original timestamp — not the webhook — in a clean Section with Thumbnail layout.",icon:"users"},{title:"Survives Restarts",description:"Both UwU Lock rules and Starboard configuration now live in the main database, loaded on startup via cog_load with automatic migration from the legacy JSON files and stale-webhook healing.",icon:"settings"}],changes:[{category:"added",items:["Main-database tables uwulock_config and uwulock_messages for lock rules and author attribution","Main-database tables starboard_config and starboard_messages for channel, threshold, emoji and post mappings","Automatic migration of legacy data/uwulock.json and data/starboard.json into the primary database with .migrated backups","Per-channel webhook reuse with stale-webhook detection via fetch and shared-webhook protection on removal","Thread-aware webhook sending with AllowedMentions.none and wait:true repost handling","UwU attribution storage (author name, avatar, original timestamp) for every transformed message","Starboard Section + Thumbnail rendering for uwu-locked messages with correct original author credit","Explicit UwU lock hook in events.on_message before AI triggers with a 2,000-entry dedup guard and fallback listener"]},{category:"improved",items:["UwU Lock now deletes the original message immediately instead of queuing for a background task","Attachment, embed, and sticker handling with text truncation and text-only fallback on send failure","Permission checks for Manage Messages and Manage Webhooks with localized failure messaging","Starboard reaction handling now distinguishes webhook reposts via database attribution","Starboard message edits and sends now use AllowedMentions.none for cleaner output","Webhook Channel resolution for threads via parent channel with robust create_webhook flow"]},{category:"fixed",items:["UwU Lock not creating the webhook or showing any sign it saw the message","Webhook created but original message not deleted and no new message sent","UwU transforms silently failing due to queue delay and background-task errors","Starboard not displaying correct author for uwu-locked webhook messages","Starboard and UwU Lock losing all state after a restart despite being stored","Stale or deleted webhooks leaving lock rules in a broken state"]},{category:"migrated",items:["UwU Lock from data/uwulock.json file storage to the primary database","Starboard configuration and starred post IDs from data/starboard.json to the primary database"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Added",value:"8",detail:"new persistence features",color:"#66866f"},{label:"Improved",value:"6",detail:"reliability upgrades",color:"#4a7fb5"},{label:"Fixed",value:"6",detail:"workflow bugs",color:"#d96545"}]},commits:[]},{slug:"guild-server-pulse-stats",title:"Guild Server Pulse Stats",date:"2026-09-24",tags:["dashboard","guild","analytics","stats"],summary:"Guild settings now include a Server pulse analytics card with an at-a-glance view of server size and recent community activity.",highlights:[{title:"Server Activity at a Glance",description:"The card summarizes member count, messages, and new members over the last 14 days, with interactive views for message trends, member joins and departures, and the server's members, channels, and roles.",icon:"chart"},{title:"Community Analytics",description:"Daily activity charts make it easier to spot changes in conversation and membership, with activity tracking noted from the time it is enabled.",icon:"users"}],changes:[{category:"added",items:["Server pulse analytics card in guild settings","14-day daily message activity and member join/leave charts","Server layout view for member, channel, and role counts"]}],commits:[]},{slug:"team-page-ai-name-config",title:"Team Profiles & Custom AI Names",date:"2026-09-22",version:"2.10.0",tags:["team","staff","dashboard","ai","website"],summary:"Niko's public website now introduces the people behind the bot, while server owners can give their AI a custom name and manage its experimental capabilities from the dashboard.",highlights:[{title:"Meet the Niko Team",description:"The new Team page showcases owners, developers, moderators, support staff, and other persisted staff roles with Discord-synced identities, presence, activities, bios, and profile pages.",icon:"users"},{title:"Choose Your AI's Name",description:"Server administrators can configure the AI's display name from the dashboard or the AI configuration command. The chosen name is used for mention detection and reply identity in that server.",icon:"spark"},{title:"Staff Public Listings",description:"Staff members can customize their public bio, banner, and visibility while their name and avatar remain synchronized with Discord.",icon:"settings"}],changes:[{category:"added",items:["Public Team page with persisted staff roles and linked staff profiles","Discord-synced staff presence, current activities, Spotify, streaming, and custom status display","Staff self-service controls for public bio, banner, and Team page visibility","Configurable per-server AI name in the dashboard and AI configuration command","Dashboard controls for AI Actions, Better Context, and Multimodal Conversation experiments","Learn-more dialogs explaining each AI experiment"]},{category:"improved",items:["Dashboard staff workspace navigation and responsive layout","Team profile cards and profile-page activity presentation","AI configuration persistence through the shared database","Public page metadata and favicon handling during the website build"]},{category:"fixed",items:["Team presence labels showing online staff as away","Spotify and streaming activities being hidden behind custom statuses","Staff profile updates being rejected for authorized owners","Staff profile avatars being clipped by profile banners"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Team",value:"1",detail:"new public experience",color:"#66866f"},{label:"AI",value:"4",detail:"new configuration controls",color:"#d96545"},{label:"Profiles",value:"3",detail:"public staff controls",color:"#4a7fb5"}]},commits:[]},{slug:"september-platform-updates",title:"September Platform Updates",date:"2026-09-21",version:"2.9.0",tags:["dashboard","ai","tickets","music","website"],summary:"A broad set of public improvements landed across Niko: richer ticket transcripts, a multimodal AI experiment, more reliable music playback, a redesigned dashboard experience, persistent giveaways and suggestions, and a refreshed public website with dynamic social previews.",highlights:[{title:"More Natural AI Conversations",description:"The new opt-in Multimodal Conversation experiment can understand image attachments and transcribe voice messages before generating a reply, while safely falling back to text when media processing is unavailable.",icon:"spark"},{title:"Richer Ticket Transcripts",description:"Transcript pages and HTML downloads now render Discord custom emojis, stickers, and dynamic timestamps such as <t:1788800225:f> in a more faithful format.",icon:"doc"},{title:"Dashboard & Website Refresh",description:"Dashboard navigation and mobile layouts were refined, documentation was expanded, and public routes now receive route-specific Open Graph cards generated during the build.",icon:"settings"},{title:"Reliable Long-Running Features",description:"Giveaways and suggestions now restore their state from the main database at startup, while music nodes are rescanned periodically to keep playback available.",icon:"utility"}],changes:[{category:"added",items:["Opt-in Multimodal Conversation AI experiment for image understanding and voice-message transcription","Official update notification system with a configurable server notification channel","Discord custom emoji and sticker rendering in ticket transcript pages and HTML downloads","Dynamic Discord timestamp rendering in ticket transcripts","Persistent suggestion configuration and voting buttons restored from the main database","Automatic hourly Lavalink node rescans with a hardcoded fallback node catalog","Additional economy SVG card API endpoints","Community Policy page on the public website","Route-specific Open Graph metadata and generated social preview cards"]},{category:"improved",items:["Dashboard navigation consistency and mobile layout","Dashboard page layout and visual polish","Music connection reliability, autoplay, Spotify playback, and node recovery","Giveaway persistence and startup restoration for MongoDB-backed data","Onboarding setup handling and configuration persistence","Poll command design and interaction flow","Ticket transcript HTML download formatting","Economy image-card font rendering, SVG output, and emoji support","Documentation pages and public website frontend"]},{category:"fixed",items:["Giveaways losing their live buttons after a restart or extended runtime","Suggestion buttons and configuration not surviving process restarts","Ticket transcript rendering for custom media and dynamic timestamps","Lavalink connection failures and stale music nodes","Broken SVG card and SVG endpoint output","Status panel polling noise and retired image-model defaults"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Added",value:"9",detail:"new capabilities",color:"#66866f"},{label:"Improved",value:"9",detail:"upgraded systems",color:"#4a7fb5"},{label:"Fixed",value:"6",detail:"reliability issues",color:"#d96545"}]},commits:["ac102df Fixed the Open Graph image cards","33aaf12 Added dynamic Open Graph tags to the website","3153e28 Rebuilt the frontend","bab665e Added a new Lavalink node","ee44a5e Improved the music cog","bc61e34 Released the new Multimodal Conversation AI experiment","c46af7d Fixed the suggestion system persistence","25703ca Added a broadcast system for official updates and announcements","265bdb2 Added dynamic timestamp rendering inside ticket transcripts","d8005db Added custom emoji and sticker rendering to ticket transcripts","e561d84 Fixed the dashboards navbar","a0bab78 Improved the dashboards mobile layout","fb2f5aa Patched giveaway persistence for MongoDB compatibility","d77779e Fixed several dashboard flaws","b8e06a5 Improved the dashboard pages","3708207 Patched issues in the giveaway and onboarding cogs","d58bb37 Redesigned the poll command","bb523e3 Added a Community Policy page","5b34c7c Updated the documentation pages","3a52fc2 Added new economy card API endpoints","df3ea25 Fixed an issue in the SVG endpoints","39b7340 Fixed an error in the SVG cards","9e3483e Replaced HTML entities with valid XML numeric character references in economy cards"]},{slug:"economy-leveling-overhaul",title:"Economy Items, Leveling Cards & Subcommands",date:"2026-09-08",version:"2.8.0",tags:["economy","leveling","shop","image-cards"],summary:"The economy shop expanded with four new consumable items that affect gameplay — Rigged Coin, Streak Insurance, Double Down Token, and Lucky Horseshoe — plus daily streak milestone bonuses at 7, 14, 30, 60, and 90 days. The leveling system now renders rank cards and leaderboards as customizable image cards, and all leveling commands live under a single `/leveling` group with subcommands.",highlights:[{title:"New Shop Items",description:"Four new consumables: Rigged Coin (60/40 coinflip odds), Streak Insurance (protects daily streak for one missed day), Double Down Token (1.5x gambling payout), and Lucky Horseshoe (+10% work reward).",icon:"chart"},{title:"Leveling Image Cards",description:"Rank cards and the leaderboard now render as styled images with avatar, level, XP bar, and rank. Server admins can customize the card accent color and background gradient.",icon:"spark"},{title:"Leveling Subcommands",description:"All leveling commands reorganized under `/leveling` with `rank`, `leaderboard`, `panel`, and `config` subcommands. The leaderboard now has interactive pagination buttons.",icon:"settings"},{title:"Daily Streak Milestones",description:"Hitting 7, 14, 30, 60, or 90-day daily streaks now awards bonus items from the shop (Espresso Shots, Lockpicks, Lucky Charms, Rob Shields) along with a coin bonus.",icon:"utility"}],changes:[{category:"added",items:["Coinflip command with heads/tails call and double-or-nothing payout","Rigged Coin shop item — gives 60/40 coinflip odds for one use","Streak Insurance shop item — protects daily streak if you miss one day","Double Down Token shop item — next gambling win pays 1.5x","Lucky Horseshoe shop item — next work reward gets +10%","Daily streak milestone bonuses at 7/14/30/60/90 days with item rewards","Image card rendering for `/leveling rank` with customizable accent and background","Image card rendering for the leveling leaderboard","Inventory display as an image card in the shop command","Twemoji emoji rendering in economy card images","Pagination buttons (◀ ▶) on the leveling leaderboard","Card customization fields in the database: card_accent, card_bg_top, card_bg_bottom"]},{category:"improved",items:["Leveling commands restructured as `/leveling rank`, `leaderboard`, `panel`, `config` subcommands","Shop command visual layout with better font rendering on economy image cards","Crime and rob commands now check for gambling_boost effect for 1.5x payout","HTML download format for ticket transcripts","Dashboard UI refinements"]},{category:"fixed",items:["Command name conflicts between leveling and other cogs","Missing import in leveling cog after image card addition","Duplicate command alias in leveling system","Command name conflict in the gambling cog"]}],chart:{type:"bar",title:"New Shop Items & Their Effects",data:[{label:"Rigged Coin",value:3e3,color:"#c9a84c"},{label:"Streak Insurance",value:4e3,color:"#4a7fb5"},{label:"Double Down Token",value:5e3,color:"#d96545"},{label:"Lucky Horseshoe",value:2500,color:"#66866f"}]},commits:["41d86fb Expanded the gambling and economy system","bd6a09c Added image cards to the leveling system","5307bb1 Moved the leveling commands to the levels subcommand","dafd224 Added an image card to the inventory command","49fc83b Added emoji rendering to the shop command","0aca6ba Improved the shop command","30c9735 Added better font rendering to the economy system image cards","2b96835 Fixed a command name conflict","158ad8f Fixed a command name conflict in the gambling cog","d465598 Fixed a missing import","1f24ffb Fixed a duplicate command alias"]},{slug:"database-migration",title:"Database Migration to MongoDB",date:"2026-09-03",version:"2.7.0",tags:["database","mongodb","migration","infrastructure"],summary:"Every major system has been migrated from SQLite to MongoDB. The migration covered economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and the blacklist — with a custom interpreter that translates SQLite-style writes to MongoDB operations.",highlights:[{title:"Full MongoDB Migration",description:"Economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and blacklist now all store data in MongoDB instead of SQLite.",icon:"settings"},{title:"Slash Command Sync Safeguard",description:"A new check prevents redundant Discord API calls when all commands are already registered, reducing rate-limit issues on startup.",icon:"utility"},{title:"Proxy Integration",description:"A new proxy manager reduces downtime on shared hosting environments by routing API requests through a proxy layer.",icon:"shield"}],changes:[{category:"migrated",items:["Economy system — balances, banks, jobs, achievements, inventory","Leveling system — XP, levels, role rewards, card customization","Moderation system — warnings, mutes, automod config","Ticket system — panels, transcripts, support roles","Birthday system — dates, channels, messages","AFK system — status, timestamps","Sticky messages — content, channels","Blacklist — users, words, filters"]},{category:"added",items:["MongoDB interpreter that translates SQLite-style writes to proper MongoDB operations","Proxy manager for shared hosting reliability","Slash command sync safeguard to prevent redundant API calls","Context menu command support in the sync utility"]},{category:"fixed",items:["MongoDB interpreter not translating all SQLite write patterns correctly","Economy interest calculation after migration","Birthday system data persistence","Several database connection issues across various cogs","Leveling database initialization issue"]}],chart:{type:"donut",title:"Systems Migrated to MongoDB",centerLabel:"8 systems",data:[{label:"Economy",value:1,color:"#d96545"},{label:"Leveling",value:1,color:"#66866f"},{label:"Moderation",value:1,color:"#4a7fb5"},{label:"Tickets",value:1,color:"#c9a84c"},{label:"Birthdays",value:1,color:"#b07cc6"},{label:"AFK",value:1,color:"#e0976e"},{label:"Sticky Msgs",value:1,color:"#7ca898"},{label:"Blacklist",value:1,color:"#8c918e"}]},commits:["c07f9b1 Fixed the MongoDB interpreter to properly translate all SQLite database writes","0d3aca5 Migrated the blacklist to the main database","954ebac Migrated the birthday system to the main database","5013d54 Migrated the warns and mutes to use the main database","f29c217 Migrated the afk system to the main database","5732b48 Migrated the sticky messages to use the main database","b0524f1 Migrated the ticket system to the main database","70e6d7a Fixed the sync util to support context commands and slash groups","2c01817 Added a safeguard to prevent slash command syncs when all commands are already present","121afcf Added a proxy integration to reduce downtime on shared hosting","9f2f1fd Fixed several database issues across various cogs"]},{slug:"ticket-system-transcripts",title:"Ticket Transcripts & VoiceMaster",date:"2026-09-03",version:"2.6.0",tags:["tickets","transcripts","voicemaster"],summary:"The ticket system gained a web-based transcript viewer that renders ticket conversations as styled HTML pages. The VoiceMaster was also improved with better reliability and database usage. Ticket transcripts can now be downloaded as HTML or viewed online.",highlights:[{title:"Web Transcript Viewer",description:"Ticket transcripts are now rendered as styled HTML pages that can be viewed online. The HTML download format was also improved for better readability.",icon:"doc"},{title:"VoiceMaster Reliability",description:"The VoiceMaster (temporary voice channels) was improved with better database usage and reliability fixes.",icon:"utility"},{title:"Donation Dashboard Page",description:"A new customization page in the dashboard lets server admins configure donation settings without using commands.",icon:"settings"}],changes:[{category:"added",items:["Web-based ticket transcript viewer with styled HTML output","Ticket transcript database table for storing transcripts online","Dashboard customization page for donation system settings"]},{category:"improved",items:["HTML download format for ticket transcripts","VoiceMaster reliability and database usage patterns","Ticket system persistence and data handling"]},{category:"fixed",items:["Ticket transcript pages rendering incorrectly","Ticket system data loss on restart","Ticket transcript generation issues","Ticket transcript page display bugs"]}],commits:["e953321 Added a new web transcript feature to the ticket system","aa0b73b Improved the donation system and added a customization page to the dashboard","3255385 Improved the html download format for the ticket transcripts","45f1fb0 Fixed the ticket system persistence","ef4e057 Added the ticket system database migrations","d4e0bc8 Fixed the ticket transcripts","4bf5e04 Fixed an issue with the ticket transcript pages","e8dbcb0 Improved the VoiceMaster reliability and improved the database usage"]},{slug:"roleplay-music-status",title:"Roleplay, Music & Status Rotation",date:"2026-09-05",version:"2.5.0",tags:["roleplay","music","status","social"],summary:"The roleplay cog was completely rewritten to use nekos.best API GIFs with CV2 layout messages and a persistent 'hug back' button. The music cog was restructured with a ghost queue feature and fixed autoplay/Spotify playback. A status message rotation system was added with a configurable timer.",highlights:[{title:"Roleplay Rewrite",description:"The roleplay cog now fetches SFW reaction GIFs from nekos.best, renders them in styled CV2 containers, and includes a 'hug back' button that persists across restarts. A single user context menu replaces individual action menus to stay under Discord's 15-command cap.",icon:"users"},{title:"Music Ghost Queue",description:"A new ghost queue feature lets songs be queued even when nothing is currently playing. Autoplay and Spotify playback were also fixed.",icon:"utility"},{title:"Status Rotation",description:"The bot now rotates through configurable status messages on a timer (default 30s interval), with activity types and a VR device presence.",icon:"spark"}],changes:[{category:"added",items:["Status message rotation with configurable interval and activity types","Persistent status panel command for the support server (owner only)","Roleplay block feature to prevent specific users from being targeted","Ghost queue feature — queue songs even when nothing is playing","User context menu for roleplay actions (replaces per-action menus)","YouTube channel name validation for notification system"]},{category:"improved",items:["Roleplay cog complete rewrite — nekos.best GIFs, CV2 layouts, persistent buttons","Social media notification emoji formatting (Bluesky, Reddit, TikTok, Twitch icons)","Music node connection system and autoplay reliability","Spotify playback quality","Music cog restructured with better error handling"]},{category:"fixed",items:["Status rotator startup errors and activity conflicts","on_ready event error handling and reliability","Lavalink connection bug","Roleplay prefix command handling","Bluesky and Reddit notification delivery issues"]}],commits:["0c58178 Redesigned the roleplay cog","6c4ee09 Fixed the roleplay prefix commands","f1f8591 Added a roleplay block feature","e01e3e4 Added status message rotation","5e63e1d Added a persistent status panel","ae7501a Restructured the music cog","526813e Added a new ghost queue feature to the music cog","6524da1 Improved the music node connection system, fixed the autoplay, and fixed the Spotify playback","4264677 Fixed a lavalink connection bug","d62ead8 Improved the social media notification system's emojis","0f0305d Improved the social media notification formatting","42069d4 Added proper channel name validation to the YouTube notification system"]},{slug:"moderation-logging-dashboard",title:"Logging, Moderation & Documentation",date:"2026-09-07",version:"2.4.0",tags:["logging","moderation","documentation","dashboard"],summary:"Logging got two major improvements: deleted message logs now show image attachments in a MediaGallery component, and the Member category now tracks avatar changes using a Section with Thumbnail accessory. The documentation page was fully rebuilt with search, filters, and a card-based layout.",highlights:[{title:"Image Attachments in Logs",description:"Deleted message logs now render attached images in a MediaGallery component inside the log container, so moderators can see what was posted without leaving Discord.",icon:"chart"},{title:"Avatar Change Tracking",description:"The Member logging category now detects avatar changes (global and server avatars) and displays them in a Section with a Thumbnail accessory showing the new avatar.",icon:"users"},{title:"Documentation Redesign",description:"The documentation page was rebuilt from scratch with a search bar, category filters, tag cloud, card-based layout, and individual article pages with table of contents.",icon:"doc"}],changes:[{category:"added",items:["Image attachments rendered in deleted message logs via MediaGallery","Avatar change detection in Member logging with Section + Thumbnail display","Startup economy cache that loads all users into memory for accurate leaderboards","Error handler for role menu post buttons","Full-text search with result highlighting in documentation","Category filters and tag cloud in documentation","Individual documentation article pages with table of contents"]},{category:"improved",items:["Logging system now supports media_urls, thumbnail_url, and files parameters","Commands page expanded with better organization","Dashboard UI refinements","Economy interest feature — skips malformed records with non-integer user IDs"]},{category:"fixed",items:["Logging command issues","Documentation command references","Status device detection issue","Status rotator conflicts between multiple status types","on_ready event reliability with proper error handling"]}],commits:["722a34f Added avatar updates to the logging cogs Member logs","1d82ea1 Moved file attachments inside the main log message for the deleted message logs","358d537 Added a startup economy cache to fix the leaderboard","566e0c4 Improved the dashboard","132bcbb Fully redesigned the documentation page","4f7a89a Improved the commands page","6d953b6 Fixed the logging command","a202687 Fixed some documentation issues","49d22ad Fixed the documentation command references","52de287 Added an error handler to the post role menu button"]},{slug:"website-launch-donation",title:"Website, Donation System & API",date:"2026-09-02",version:"2.3.0",tags:["website","donations","api"],summary:"The public website and documentation portal launched with a React + Vite frontend, documentation center with search, and a commands reference page. The donation system gained a dashboard customization page, and the Flask API backend was fixed to use proper database calls.",highlights:[{title:"Public Website",description:"A complete public website built with React and Vite featuring a landing page, documentation center, command reference, dashboard, and legal pages.",icon:"spark"},{title:"Documentation Center",description:"The documentation page was redesigned with a card-based layout, individual article pages, and a modern visual design matching the bot's aesthetic.",icon:"doc"},{title:"Donation Dashboard",description:"Server admins can now configure donation settings through a new dashboard page instead of relying solely on commands.",icon:"settings"}],changes:[{category:"added",items:["Public website with landing page, documentation center, and command reference","Donation system customization page in the dashboard","Ticket transcript viewer web page","Donate page with Oxapay integration"]},{category:"improved",items:["Flask API to use proper database calls instead of direct SQLite access","Website commands page with expanded details","Database layer reliability for production"]},{category:"fixed",items:["Flask API database call issues","Several database-related bugs across cogs","node_modules folder accidentally committed to repository"]}],commits:["132bcbb Fully redesigned the documentation page","aa0b73b Improved the donation system and added a customization page to the dashboard","bd5e3be Expanded the website's commands page","e266644 Fixed the flask API to use the proper database calls","e99ed47 Fixed several database related issues","c783514 Minor API fixes and improvements","0df4478 Added the node_modules folder to the gitignore file"]}];function PS(t){return Ra.find(s=>s.slug===t)}function ES(){const t=new Set;return Ra.forEach(s=>s.tags.forEach(r=>t.add(r))),Array.from(t).sort()}function MS(){const[t,s]=T.useState(""),r=ES(),o=t?Ra.filter(c=>c.tags.includes(t)):Ra;return i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"home"}),i.jsxs("main",{className:"shell page-main changelog-page",children:[i.jsxs("div",{className:"changelog-hero",children:[i.jsxs("div",{className:"eyebrow",children:[i.jsx("span",{className:"status-dot"})," What's new"]}),i.jsxs("h1",{className:"changelog-title",children:["Changelog",i.jsx("br",{}),i.jsx("span",{className:"title-accent",children:"& updates"})]}),i.jsx("p",{className:"changelog-subtitle",children:"A record of every improvement, fix, and new feature added to Niko. Grouped by release for clarity."})]}),i.jsxs("div",{className:"changelog-tags",children:[i.jsx("button",{className:`changelog-tag-btn ${t===""?"active":""}`,onClick:()=>s(""),children:"All"}),r.slice(0,12).map(c=>i.jsx("button",{className:`changelog-tag-btn ${t===c?"active":""}`,onClick:()=>s(c),children:c},c))]}),i.jsx("div",{className:"changelog-timeline",children:o.map((c,u)=>i.jsxs("article",{className:"changelog-entry",children:[i.jsxs("div",{className:"changelog-entry-date-col",children:[i.jsx("div",{className:"changelog-date-dot"}),u<o.length-1&&i.jsx("div",{className:"changelog-date-line"})]}),i.jsxs("div",{className:"changelog-entry-card",children:[i.jsxs("div",{className:"changelog-entry-header",children:[i.jsxs("div",{className:"changelog-entry-meta",children:[i.jsx("time",{className:"changelog-entry-date",children:new Date(c.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),c.version&&i.jsxs("span",{className:"changelog-version",children:["v",c.version]})]}),i.jsx("h2",{className:"changelog-entry-title",children:c.title}),i.jsx("p",{className:"changelog-entry-summary",children:c.summary})]}),i.jsx("div",{className:"changelog-entry-highlights",children:c.highlights.slice(0,2).map(h=>i.jsxs("div",{className:"changelog-highlight-mini",children:[i.jsx("span",{className:"highlight-mini-icon",children:i.jsx(J,{name:h.icon,size:16})}),i.jsxs("div",{children:[i.jsx("strong",{children:h.title}),i.jsxs("p",{children:[h.description.slice(0,120),"..."]})]})]},h.title))}),i.jsx("div",{className:"changelog-entry-tags",children:c.tags.map(h=>i.jsx("span",{className:"changelog-tag",children:h},h))}),i.jsxs("button",{className:"changelog-read-more",onClick:()=>{be(`/changelog/${c.slug}`)},children:["Read full release notes ",i.jsx(J,{name:"arrow",size:14})]})]})]},c.slug))}),o.length===0&&i.jsxs("div",{className:"changelog-empty",children:[i.jsx(J,{name:"doc",size:40}),i.jsx("p",{children:"No changelog entries match this filter."})]})]}),i.jsx(Nt,{})]})}function _S({slug:t}){const s=PS(t);return s?i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"home"}),i.jsxs("main",{className:"shell page-main changelog-page changelog-detail",children:[i.jsx("div",{className:"changelog-back",children:i.jsxs("button",{onClick:()=>be("/changelog"),className:"back-button",children:[i.jsx(J,{name:"arrow",size:16}),"Back to Changelog"]})}),i.jsxs("header",{className:"changelog-detail-header",children:[i.jsxs("div",{className:"changelog-detail-meta",children:[i.jsx("time",{children:new Date(s.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),s.version&&i.jsxs("span",{className:"changelog-version",children:["v",s.version]})]}),i.jsx("h1",{children:s.title}),i.jsx("p",{className:"changelog-detail-summary",children:s.summary}),i.jsx("div",{className:"changelog-detail-tags",children:s.tags.map(r=>i.jsx("span",{className:"changelog-tag",children:r},r))})]}),i.jsxs("section",{className:"changelog-highlights-section",children:[i.jsx("h2",{className:"changelog-section-heading",children:"Highlights"}),i.jsx("div",{className:"changelog-highlights-grid",children:s.highlights.map(r=>i.jsxs("div",{className:"changelog-highlight-card",children:[i.jsx("span",{className:"highlight-icon",children:i.jsx(J,{name:r.icon,size:22})}),i.jsx("h3",{children:r.title}),i.jsx("p",{children:r.description})]},r.title))})]}),s.chart&&i.jsx(DS,{chart:s.chart}),i.jsxs("section",{className:"changelog-changes-section",children:[i.jsx("h2",{className:"changelog-section-heading",children:"All Changes"}),i.jsx("div",{className:"changelog-changes-grid",children:s.changes.map(r=>i.jsxs("div",{className:`changelog-change-group changelog-change-${r.category}`,children:[i.jsx("h3",{className:"change-group-title",children:i.jsx("span",{className:`change-badge change-badge-${r.category}`,children:r.category})}),i.jsx("ul",{children:r.items.map((o,c)=>i.jsx("li",{children:o},c))})]},r.category))})]}),s.commits.length>0&&i.jsxs("section",{className:"changelog-commits-section",children:[i.jsx("h2",{className:"changelog-section-heading",children:"Commits"}),i.jsx("div",{className:"changelog-commits-list",children:s.commits.map(r=>{const[o,...c]=r.split(" ");return i.jsxs("div",{className:"changelog-commit",children:[i.jsx("code",{className:"commit-hash",children:o.slice(0,7)}),i.jsx("span",{className:"commit-msg",children:c.join(" ")})]},o)})})]}),i.jsx("nav",{className:"changelog-detail-nav",children:i.jsxs("button",{onClick:()=>be("/changelog"),children:[i.jsx(J,{name:"arrow",size:14}),"All releases"]})})]}),i.jsx(Nt,{})]}):i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"home"}),i.jsx("main",{className:"shell page-main changelog-page",children:i.jsxs("div",{className:"changelog-not-found",children:[i.jsx(J,{name:"doc",size:48}),i.jsx("h1",{children:"Entry Not Found"}),i.jsxs("p",{children:[`We couldn't find a changelog entry for "`,t,'".']}),i.jsx("button",{onClick:()=>be("/changelog"),children:"View all changelog entries"})]})}),i.jsx(Nt,{})]})}function DS({chart:t}){return i.jsxs("section",{className:"changelog-chart-section",children:[i.jsx("h2",{className:"changelog-section-heading",children:t.title}),i.jsxs("div",{className:"changelog-chart-container",children:[t.type==="bar"&&i.jsx(RS,{chart:t}),t.type==="pie"&&i.jsx(LS,{chart:t}),t.type==="donut"&&i.jsx(IS,{chart:t}),t.type==="line"&&i.jsx(VS,{chart:t}),t.type==="timeline"&&i.jsx(FS,{chart:t}),t.type==="comparison"&&i.jsx(OS,{chart:t}),t.type==="metrics"&&i.jsx(BS,{chart:t})]})]})}function RS({chart:t}){const s=Math.max(...t.data.map(r=>r.value));return i.jsx("div",{className:"chart-bar",children:t.data.map(r=>i.jsxs("div",{className:"chart-bar-row",children:[i.jsx("span",{className:"chart-bar-label",children:r.label}),i.jsxs("div",{className:"chart-bar-track",children:[i.jsx("div",{className:"chart-bar-fill",style:{width:`${r.value/s*100}%`,background:r.color||"var(--accent)"}}),i.jsx("span",{className:"chart-bar-value",children:r.value})]})]},r.label))})}function LS({chart:t}){const s=t.data.reduce((u,h)=>u+h.value,0);let r=0;const c=t.data.map(u=>{const h=r/s*360;r+=u.value;const p=r/s*360;return{...u,start:h,end:p}}).map(u=>{const h=u.start/360*100,p=u.end/360*100;return`${u.color||"#d96545"} ${h}% ${p}%`}).join(", ");return i.jsxs("div",{className:"chart-pie-wrapper",children:[i.jsx("div",{className:"chart-pie",style:{background:`conic-gradient(${c})`}}),i.jsx("div",{className:"chart-pie-legend",children:t.data.map(u=>i.jsxs("div",{className:"chart-legend-item",children:[i.jsx("span",{className:"chart-legend-dot",style:{background:u.color||"var(--accent)"}}),i.jsx("span",{className:"chart-legend-label",children:u.label})]},u.label))})]})}function IS({chart:t}){const s=t.data.reduce((o,c)=>o+c.value,0),r=t.data.reduce((o,c)=>{const u=o.current/s*100,h=(o.current+c.value)/s*100;return o.css+=`${c.color||"#d96545"} ${u}% ${h}%, `,o.current+=c.value,o},{css:"",current:0}).css.slice(0,-2);return i.jsxs("div",{className:"chart-donut-wrapper",children:[i.jsx("div",{className:"chart-donut",style:{background:`conic-gradient(${r})`},children:i.jsx("span",{children:t.centerLabel||s})}),i.jsx("div",{className:"chart-pie-legend",children:t.data.map(o=>i.jsxs("div",{className:"chart-legend-item",children:[i.jsx("span",{className:"chart-legend-dot",style:{background:o.color||"var(--accent)"}}),i.jsx("span",{className:"chart-legend-label",children:o.label})]},o.label))})]})}function VS({chart:t}){const s=Math.max(...t.data.map(o=>o.value),1),r=t.data.map((o,c)=>{const u=t.data.length===1?50:c/(t.data.length-1)*100,h=100-o.value/s*82-9;return`${u},${h}`}).join(" ");return i.jsxs("div",{className:"chart-line-wrapper",children:[i.jsxs("svg",{className:"chart-line",viewBox:"0 0 100 100",preserveAspectRatio:"none",role:"img","aria-label":t.title,children:[i.jsx("polyline",{points:r,fill:"none",stroke:"var(--accent)",strokeWidth:"3",vectorEffect:"non-scaling-stroke"}),t.data.map((o,c)=>{const u=t.data.length===1?50:c/(t.data.length-1)*100,h=100-o.value/s*82-9;return i.jsx("circle",{cx:u,cy:h,r:"3",fill:"var(--accent)",vectorEffect:"non-scaling-stroke"},o.label)})]}),i.jsx("div",{className:"chart-line-labels",children:t.data.map(o=>i.jsx("span",{children:o.label},o.label))})]})}function FS({chart:t}){const s=Math.max(...t.data.map(r=>r.value),1);return i.jsx("div",{className:"chart-timeline",children:t.data.map(r=>i.jsxs("div",{className:"chart-timeline-item",children:[i.jsx("div",{className:"chart-timeline-marker",style:{background:r.color||"var(--accent)"}}),i.jsxs("div",{className:"chart-timeline-content",children:[i.jsx("strong",{children:r.label}),i.jsx("div",{className:"chart-timeline-track",children:i.jsx("div",{className:"chart-timeline-fill",style:{width:`${r.value/s*100}%`,background:r.color||"var(--accent)"}})}),r.detail&&i.jsx("span",{children:r.detail})]})]},r.label))})}function BS({chart:t}){return i.jsx("div",{className:"chart-metrics",children:t.data.map(s=>i.jsxs("div",{className:"chart-metric",style:{borderTopColor:s.color||"var(--accent)"},children:[i.jsx("span",{className:"chart-metric-label",children:s.label}),i.jsx("strong",{children:s.value}),s.detail&&i.jsx("small",{children:s.detail})]},s.label))})}function OS({chart:t}){const s=Math.max(...t.before.concat(t.after).map(o=>o.value),1),r=(o,c,u)=>i.jsxs("div",{className:"chart-comparison-col",children:[i.jsx("h4",{className:`comparison-label ${u}`,children:o}),c.map(h=>i.jsxs("div",{className:"chart-bar-row",children:[i.jsx("span",{className:"chart-bar-label",children:h.label}),i.jsxs("div",{className:"chart-bar-track",children:[i.jsx("div",{className:"chart-bar-fill",style:{width:`${h.value/s*100}%`,background:h.color||"var(--accent)"}}),i.jsx("span",{className:"chart-bar-value",children:h.value})]})]},h.label))]});return i.jsxs("div",{className:"chart-comparison",children:[r("Before",t.before,"comparison-before"),i.jsx("div",{className:"chart-comparison-divider",children:i.jsx(J,{name:"arrow",size:20})}),r("After",t.after,"comparison-after")]})}function La(t){return t.avatar_url}function zS(t){return`https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/svg/${Array.from(t).map(r=>r.codePointAt(0).toString(16)).join("-")}.svg`}function US({emoji:t}){return t?t.kind==="custom"?i.jsx("img",{className:"presence-emoji",src:`https://cdn.discordapp.com/emojis/${t.value}.${t.animated?"gif":"png"}?size=18`,alt:t.name||"custom emoji"}):i.jsx("img",{className:"presence-emoji",src:zS(t.value),alt:t.name||t.value}):null}function $S(t){return{playing:"Playing",listening:"Listening to",watching:"Watching",streaming:"Streaming",competing:"Competing in"}[t]||(t?`${t.charAt(0).toUpperCase()}${t.slice(1)}`:"Activity")}function WS({activity:t}){const s=t.kind==="spotify",r=s?"Listening on Spotify":$S(t.type),o=s?t.details||"Spotify":t.name,c=(s?[t.state]:[t.details,t.state]).filter(h=>!!(h&&h!==o)),u=i.jsxs("span",{className:`activity-card activity-${t.kind}`,children:[t.image_url&&i.jsx("img",{className:"activity-art",src:t.image_url,alt:""}),i.jsxs("span",{className:"activity-copy",children:[i.jsx("strong",{children:r}),i.jsx("span",{children:o}),c.map((h,p)=>i.jsx("small",{children:h},`${h}-${p}`))]})]});return t.url?i.jsx("a",{className:"presence-activity",href:t.url,target:"_blank",rel:"noreferrer",children:u}):i.jsx("span",{className:"presence-activity",children:u})}function HS(t){return t.status_label||{online:"Online",idle:"Idle",dnd:"Do Not Disturb",offline:"Offline"}[t.status||"offline"]||"Offline"}function GS({member:t}){const s=t.custom_status,r=t.activities||[],o=!!(s!=null&&s.text||s!=null&&s.emoji);return!o&&!r.length?null:i.jsxs("span",{className:"presence-stack",children:[o&&i.jsxs("span",{className:"presence-line",children:[i.jsx(US,{emoji:s==null?void 0:s.emoji}),(s==null?void 0:s.text)||"Custom status"]}),r.length>0&&i.jsx("span",{className:"presence-line activity-list",children:r.map((c,u)=>i.jsx(WS,{activity:c},`${c.kind}-${c.name}-${u}`))})]})}const ky=`
.team-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));align-items:start;gap:14px;margin-top:58px}.team-card{display:flex;flex-direction:column;min-width:0;overflow:hidden;padding:0;color:var(--ink);text-align:left;background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow-soft)}.team-card:hover{border-color:#dfaa98;transform:translateY(-2px)}.team-card-art,.team-profile-banner{min-height:105px;background:linear-gradient(135deg,var(--callout),var(--surface-muted));background-size:cover;background-position:center}.team-card-body{display:flex;align-items:flex-start;flex:1;min-width:0;gap:14px;padding:18px}.team-card-body>div:last-child{min-width:0}.team-card h2,.team-card p{overflow-wrap:anywhere}.team-avatar,.team-profile-avatar{display:grid;place-items:center;flex:0 0 auto;overflow:hidden;color:#fffaf5;background:var(--accent);border-radius:50%;font-weight:800;object-fit:cover}.team-avatar{width:56px;height:56px;margin-top:-39px;border:3px solid var(--surface)}.team-role{color:var(--accent-dark);text-transform:uppercase;letter-spacing:.1em;font:700 9px "Space Mono",monospace}.team-card h2{margin:5px 0 6px;font-size:17px}.team-card p{margin:0 0 10px;color:var(--muted);font-size:11px;line-height:1.6}.team-status{color:var(--dim);font-size:10px}.presence-stack{display:block}.presence-stack>.presence-line+.presence-line{margin-top:12px}.presence-line{display:flex;align-items:center;flex-wrap:wrap;gap:7px;margin-top:7px;color:var(--muted);font-size:10px}.presence-activity{display:inline-flex;align-items:center;gap:4px;color:inherit}.presence-activity:hover{text-decoration:none}.activity-card{display:flex;align-items:center;min-width:0;gap:8px;padding:7px 9px;background:var(--surface-muted);border:1px solid var(--line);border-radius:8px;text-align:left}.activity-art{width:30px;height:30px;flex:0 0 auto;border-radius:5px;object-fit:cover}.activity-copy{display:flex;min-width:0;flex-direction:column;gap:1px}.activity-copy strong{color:var(--accent-dark);font-size:9px;text-transform:uppercase;letter-spacing:.06em}.activity-copy span,.activity-copy small{overflow:hidden;max-width:210px;text-overflow:ellipsis;white-space:nowrap}.activity-copy span{color:var(--ink);font-size:10px}.activity-copy small{color:var(--dim);font-size:9px}.presence-emoji{width:18px;height:18px;object-fit:contain;vertical-align:middle}.is-online{color:var(--sage)}.team-profile-page{max-width:760px}.team-back{width:auto;margin:0 0 18px;border:0;background:transparent}.team-profile-banner{min-height:220px;border:1px solid var(--line);border-radius:14px 14px 0 0}.team-profile-card{padding:0 34px 38px;text-align:center;background:var(--surface);border:1px solid var(--line);border-top:0;border-radius:0 0 14px 14px;box-shadow:var(--shadow-soft)}.team-profile-avatar{width:100px;height:100px;margin:-50px auto 6px;border:5px solid var(--surface);font-size:32px;transform:translateY(-20px)}.team-profile-card h1{margin:8px 0 5px;font-size:34px;letter-spacing:-.07em}.team-profile-handle{color:var(--dim);font-size:11px}.team-profile-bio{max-width:560px;margin:27px auto 0;color:var(--muted);line-height:1.8}.team-profile-links{display:flex;justify-content:center;flex-wrap:wrap;gap:9px;margin:20px auto 0}.team-profile-links a{display:inline-flex;align-items:center;gap:7px;padding:9px 13px;color:var(--accent-dark);background:var(--surface-muted);border:1px solid var(--line);border-radius:999px;font-size:11px;font-weight:700;transition:background .18s,border-color .18s,transform .18s}.team-profile-links a:hover{background:var(--filter-active);border-color:var(--filter-border);transform:translateY(-1px)}.team-activity{display:block;width:min(100%,560px);margin:20px auto 0;padding:12px;color:var(--muted);background:var(--surface-muted);border:1px solid var(--line);border-radius:12px;font-size:10px;text-align:left}.team-activity .presence-line{margin-top:0}.team-activity .activity-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));align-items:stretch}.team-activity .activity-card{height:100%;width:100%}@media(max-width:800px){.team-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.team-grid{grid-template-columns:1fr;margin-top:38px}.team-profile-card{padding-left:18px;padding-right:18px}.team-profile-banner{min-height:150px}}`,jy=5e3;function KS(){const[t,s]=T.useState([]);return T.useEffect(()=>{let r=!0;const o=()=>{Dx().then(h=>{r&&s(h)}).catch(()=>{})},c=()=>{document.visibilityState==="visible"&&o()};o();const u=window.setInterval(()=>{document.visibilityState==="visible"&&o()},jy);return document.addEventListener("visibilitychange",c),()=>{r=!1,window.clearInterval(u),document.removeEventListener("visibilitychange",c)}},[]),i.jsxs(i.Fragment,{children:[i.jsx("style",{children:ky}),i.jsx(Ue,{page:"team"}),i.jsxs("main",{className:"shell page-main",children:[i.jsxs("div",{className:"page-heading",children:[i.jsx("div",{className:"eyebrow",children:"The people behind Niko"}),i.jsx("h1",{children:"Meet the team."}),i.jsx("p",{children:"A small group of builders, moderators, and creative minds keeping Niko friendly, useful, and moving forward."})]}),i.jsxs("div",{className:"team-grid",children:[t.map(r=>i.jsxs("button",{className:"team-card",onClick:()=>be(`/team/${r.id}`),children:[i.jsx("div",{className:"team-card-art",style:r.public_banner_url?{backgroundImage:`url(${r.public_banner_url})`}:void 0}),i.jsxs("div",{className:"team-card-body",children:[La(r)?i.jsx("img",{className:"team-avatar",src:La(r),alt:""}):i.jsx("span",{className:"team-avatar team-avatar-fallback",children:r.name.slice(0,1)}),i.jsxs("div",{children:[i.jsx("span",{className:"team-role",children:r.role_label}),i.jsx("h2",{children:r.name}),i.jsx("p",{children:r.bio||"Part of the Niko team."})]})]})]},r.id)),!t.length&&i.jsx("div",{className:"empty-state",children:"The team roster is being prepared."})]})]}),i.jsx(Nt,{})]})}function qS({id:t}){const[s,r]=T.useState(null),[o,c]=T.useState("");return T.useEffect(()=>{let u=!0;const h=(v=!1)=>{Rx(t).then(g=>{u&&(r(g),c(""))}).catch(g=>{u&&v&&c(g instanceof Error?g.message:"Team member not found.")})},p=()=>{document.visibilityState==="visible"&&h()};h(!0);const f=window.setInterval(()=>{document.visibilityState==="visible"&&h()},jy);return document.addEventListener("visibilitychange",p),()=>{u=!1,window.clearInterval(f),document.removeEventListener("visibilitychange",p)}},[t]),i.jsxs(i.Fragment,{children:[i.jsx("style",{children:ky}),i.jsx(Ue,{page:"team"}),i.jsx("main",{className:"shell page-main team-profile-page",children:o?i.jsx("div",{className:"empty-state",children:o}):s?i.jsxs(i.Fragment,{children:[i.jsx("button",{className:"back-link team-back",onClick:()=>be("/team"),children:"← Back to team"}),i.jsx("div",{className:"team-profile-banner",style:s.public_banner_url?{backgroundImage:`url(${s.public_banner_url})`}:void 0}),i.jsxs("section",{className:"team-profile-card",children:[La(s)?i.jsx("img",{className:"team-profile-avatar",src:La(s),alt:""}):i.jsx("span",{className:"team-profile-avatar team-avatar-fallback",children:s.name.slice(0,1)}),i.jsx("div",{className:"team-role",children:s.role_label}),i.jsx("h1",{children:s.name}),i.jsxs("p",{className:"team-profile-handle",children:[s.username?`@${s.username}`:"Niko staff"," · ",i.jsx("span",{className:`status-${s.status||"offline"} ${s.status==="online"?"is-online":""}`,children:HS(s)})]}),i.jsx("p",{className:"team-profile-bio",children:s.bio||"This team member has not added an extended introduction yet."}),(s.public_links||[]).length>0&&i.jsx("nav",{className:"team-profile-links","aria-label":`${s.name}'s links`,children:(s.public_links||[]).map((u,h)=>i.jsxs("a",{href:u.url,target:"_blank",rel:"noopener noreferrer",children:[u.label||u.type," ",i.jsx("span",{"aria-hidden":"true",children:"↗"})]},`${u.type}-${h}`))}),i.jsxs("div",{className:"team-activity",children:[i.jsx(GS,{member:s}),!s.custom_status&&!(s.activities||[]).length&&"No current activity"]})]})]}):i.jsx("div",{className:"section-loading",children:"Loading profile…"})}),i.jsx(Nt,{})]})}const XS=[["website","Website"],["github","GitHub"],["instagram","Instagram"],["x","X"],["tiktok","TikTok"],["youtube","YouTube"],["twitch","Twitch"],["bluesky","Bluesky"],["linkedin","LinkedIn"],["reddit","Reddit"],["mastodon","Mastodon"],["facebook","Facebook"],["discord","Discord"],["other","Other"]];function YS(){const[t,s]=T.useState(null),[r,o]=T.useState(null),[c,u]=T.useState(null),[h,p]=T.useState([]),[f,v]=T.useState({public_bio:"",public_banner_url:"",public_visible:!0}),[g,x]=T.useState([]),[b,j]=T.useState({avatar_url:"",banner_url:""}),[N,w]=T.useState(""),[S,B]=T.useState(""),[P,D]=T.useState(!1),[V,_]=T.useState(!1);if(T.useEffect(()=>{Promise.all([va(),mc(),xa(),pc()]).then(([ee,z,Z,X])=>{s(ee),o(z),u(Z),p(X),v({public_bio:z.profile.bio||"",public_banner_url:z.profile.public_banner_url||"",public_visible:z.profile.visible!==!1}),x(z.profile.public_links||[])}).catch(ee=>B(ee instanceof Error?ee.message:"Staff access unavailable."))},[]),!t||!r&&!S)return i.jsxs("div",{className:"dashboard-state",children:[i.jsx("div",{className:"loading-ring"}),i.jsx("p",{children:"Checking staff access…"})]});if(S||!r||!t.authenticated)return i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"dashboard"}),i.jsx("main",{className:"auth-page",children:i.jsxs("div",{className:"auth-card",children:[i.jsx("div",{className:"eyebrow",children:"Staff workspace"}),i.jsx("h1",{children:"Private team area."}),i.jsx("p",{children:t!=null&&t.authenticated?S||"This area is only available to official Niko staff.":"Sign in with Discord to continue."}),!(t!=null&&t.authenticated)&&i.jsx("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard/staff",children:"Continue with Discord"}),i.jsx("button",{className:"back-link",onClick:()=>be("/dashboard"),children:"Return to dashboard"})]})})]});const L=t.user,I=`https://cdn.discordapp.com/embed/avatars/${Number(BigInt(L.id)%5n)}.png`,U=L.avatar?`https://cdn.discordapp.com/avatars/${L.id}/${L.avatar}.png?size=128`:I,ce=["owner","head_admin","graphic_designer"].includes(r.role),q=(ee,z)=>v(Z=>({...Z,[ee]:z})),ge=()=>x(ee=>ee.length<10?[...ee,{type:"",url:""}]:ee),he=(ee,z,Z)=>{x(X=>X.map((E,$)=>$===ee?{...E,[z]:Z}:E))},Y=ee=>x(z=>z.filter((Z,X)=>X!==ee)),we=async()=>{if(P)return;const ee=g.filter(z=>z.type.trim()||z.url.trim());if(ee.some(z=>!z.type.trim()||!z.url.trim())){B("Choose a link type and enter its URL, or remove the unfinished link."),w("");return}D(!0),B(""),w("");try{await Lx({...f,public_links:ee},t.csrf_token),w("Your public team listing was saved.")}catch(z){B(z instanceof Error?z.message:"Could not save listing.")}finally{D(!1)}},me=async()=>{if(!V){_(!0),B(""),w("");try{await Ix(b,t.csrf_token),w("Niko's global profile was updated.")}catch(ee){B(ee instanceof Error?ee.message:"Could not update global profile.")}finally{_(!1)}}},Ce=i.jsxs("div",{className:"staff-page",children:[i.jsxs("header",{className:"staff-heading",children:[i.jsxs("div",{children:[i.jsx("div",{className:"eyebrow",children:"Staff workspace"}),i.jsx("h1",{children:"Shape your presence."}),i.jsxs("p",{children:["Manage the public details granted to your ",i.jsx("strong",{children:r.role_label})," role. Your name and avatar always come directly from Discord."]})]}),i.jsxs("div",{className:"staff-role-card",children:[i.jsx("span",{className:"staff-role-mark",children:i.jsx("img",{src:U,alt:"Your Discord profile",onError:ee=>{ee.currentTarget.onerror=null,ee.currentTarget.src=I}})}),i.jsxs("span",{children:[i.jsx("small",{children:"Signed in as"}),i.jsx("strong",{children:r.role_label})]})]})]}),i.jsxs("div",{className:"staff-layout",children:[i.jsxs("section",{className:"staff-panel staff-panel-main",children:[i.jsxs("div",{className:"staff-panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Public listing"}),i.jsx("h2",{children:"How the team sees you"}),i.jsx("p",{children:"Keep your introduction current while Discord remains the source of truth for your identity."})]}),i.jsx("span",{className:"staff-step",children:"01"})]}),i.jsxs("div",{className:"staff-fields",children:[i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Banner URL"}),i.jsx("input",{type:"url",value:f.public_banner_url,onChange:ee=>q("public_banner_url",ee.target.value),placeholder:"https://…"}),i.jsx("small",{children:"Use a publicly reachable image. Leave blank for no banner."})]}),i.jsxs("section",{className:"staff-links-section","aria-labelledby":"staff-links-heading",children:[i.jsxs("div",{className:"staff-links-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"form-label",id:"staff-links-heading",children:"Links"}),i.jsx("small",{children:"Add up to 10 links. They appear on your profile, not the team overview card."})]}),i.jsxs("span",{className:"staff-links-count",children:[g.length,"/10"]})]}),i.jsx("div",{className:"staff-link-list",children:g.map((ee,z)=>i.jsxs("div",{className:"staff-link-row",children:[i.jsxs("label",{className:"form-field staff-link-type",children:[i.jsxs("span",{className:"sr-only",children:["Link ",z+1," type"]}),i.jsxs("select",{value:ee.type,onChange:Z=>he(z,"type",Z.target.value),children:[i.jsx("option",{value:"",children:"Choose link type…"}),XS.map(([Z,X])=>i.jsx("option",{value:Z,children:X},Z))]})]}),i.jsxs("label",{className:"form-field staff-link-url",children:[i.jsxs("span",{className:"sr-only",children:["Link ",z+1," URL"]}),i.jsx("input",{type:"url",value:ee.url,onChange:Z=>he(z,"url",Z.target.value),placeholder:"https://…"})]}),i.jsx("button",{type:"button",className:"staff-link-remove",onClick:()=>Y(z),"aria-label":`Remove link ${z+1}`,children:"Remove"})]},`profile-link-${z}`))}),i.jsx("button",{type:"button",className:"button button-muted staff-add-link",onClick:ge,disabled:g.length>=10,children:"＋ Add link"})]}),i.jsxs("label",{className:"form-field staff-bio-field",children:[i.jsx("span",{className:"form-label",children:"Extended introduction"}),i.jsx("textarea",{value:f.public_bio,onChange:ee=>q("public_bio",ee.target.value),maxLength:1200,placeholder:"Tell the community what you do…"}),i.jsxs("small",{children:[f.public_bio.length,"/1200 characters"]})]})]}),i.jsxs("label",{className:"setting-row staff-visibility",children:[i.jsxs("span",{children:[i.jsx("strong",{children:"Show me on the public Team page"}),i.jsx("small",{children:"Hide your listing without removing your staff access."})]}),i.jsx("input",{type:"checkbox",checked:f.public_visible,onChange:ee=>q("public_visible",ee.target.checked)}),i.jsx("i",{})]}),i.jsxs("div",{className:"staff-panel-footer",children:[i.jsx("span",{children:"Changes apply immediately to your public profile."}),i.jsx("button",{type:"button",className:"button button-primary",onClick:we,disabled:P,children:P?"Saving…":"Save public listing"})]})]}),i.jsxs("aside",{className:"staff-sidebar-card",children:[i.jsx("span",{className:"panel-kicker",children:"Profile rules"}),i.jsx("h3",{children:"Stay consistent with Discord"}),i.jsx("p",{children:"Your global display name and profile picture sync automatically, so updates made in Discord are reflected here without another form."}),i.jsxs("div",{className:"staff-rule",children:[i.jsx("span",{children:"Identity"}),i.jsx("strong",{children:"Discord synced"})]}),i.jsxs("div",{className:"staff-rule",children:[i.jsx("span",{children:"Editable"}),i.jsx("strong",{children:"Bio · banner · links · visibility"})]})]})]}),ce&&i.jsxs("section",{className:"staff-panel staff-global-panel",children:[i.jsxs("div",{className:"staff-panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Graphic direction"}),i.jsx("h2",{children:"Global Niko profile"}),i.jsx("p",{children:"Reserved for Graphic Designers, Head Admins, and owners. Paste publicly reachable image URLs."})]}),i.jsx("span",{className:"staff-step",children:"02"})]}),i.jsxs("div",{className:"staff-fields staff-fields-two",children:[i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Bot avatar URL"}),i.jsx("input",{value:b.avatar_url,onChange:ee=>j({...b,avatar_url:ee.target.value}),placeholder:"https://…"})]}),i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Bot banner URL"}),i.jsx("input",{value:b.banner_url,onChange:ee=>j({...b,banner_url:ee.target.value}),placeholder:"https://…"})]})]}),i.jsxs("div",{className:"staff-panel-footer",children:[i.jsx("span",{children:"Updates the bot-wide Discord profile."}),i.jsx("button",{type:"button",className:"button button-primary",onClick:me,disabled:V,children:V?"Updating…":"Update global profile"})]})]}),N&&i.jsx("div",{className:"notice",children:N}),S&&i.jsx("div",{className:"notice warning",children:S})]});return i.jsx(_f,{user:t.user,guilds:h,selectedGuild:null,view:"overview",section:"overview",stats:c,staffRole:r.role,onHome:()=>be(Rs()),onServers:()=>be(fc()),onGuildChange:()=>{},onSectionChange:()=>{},onRefresh:()=>window.location.reload(),refreshing:!1,children:Ce})}function QS(){var U,ce;const[t,s]=T.useState(null),[r,o]=T.useState(null),[c,u]=T.useState([]),[h,p]=T.useState({}),[f,v]=T.useState(!0),[g,x]=T.useState(""),[b,j]=T.useState(!1),[N,w]=T.useState(!1),S=Ln(),B=window.location.pathname.split("/").filter(Boolean),P=B[1]||"",D=B[2]||"",V=window.location.pathname;T.useEffect(()=>{let q=!0;return v(!0),x(""),va().then(ge=>{if(q&&(s(ge),!!ge.authenticated))return D?qx(P,D).then(he=>{q&&o(he)}):Kx(P).then(he=>{q&&u(he.openings)})}).catch(ge=>{q&&x(ge instanceof Error?ge.message:"The application could not be loaded.")}).finally(()=>{q&&v(!1)}),()=>{q=!1}},[P,D]);const _=q=>{if(q.preventDefault(),!r)return;const ge=r.questions.find(he=>{if(!he.required)return!1;const Y=h[he.id];return Array.isArray(Y)?Y.length===0:!(Y!=null&&Y.trim())});if(ge){x(`Please answer: ${ge.prompt}`);return}w(!0),x(""),Xx(P,r.id,h,t==null?void 0:t.csrf_token).then(()=>j(!0)).catch(he=>x(he instanceof Error?he.message:"Your application could not be submitted.")).finally(()=>w(!1))},L=`/auth/login?next=${encodeURIComponent(V)}`,I=(r==null?void 0:r.guild_name)||"the server";return i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"dashboard"}),i.jsx("main",{className:"application-public-page",children:i.jsxs("div",{className:"application-public-shell",children:[i.jsx("a",{className:"application-back-link",href:"/",onClick:q=>{q.preventDefault(),be("/")},children:"← Back to Niko"}),i.jsxs("div",{className:"application-public-brand",children:[i.jsx("span",{className:"application-public-mark",children:"n"}),i.jsxs("span",{children:["TEAM APPLICATIONS ",i.jsx("small",{children:"POWERED BY NIKO"})]})]}),i.jsx("div",{className:"application-public-card",children:f?i.jsxs("div",{className:"application-public-state",children:[i.jsx("div",{className:"loading-ring"}),i.jsx("p",{children:"Checking your sign-in and server access…"})]}):t!=null&&t.authenticated?b?i.jsxs("div",{className:"application-public-state",children:[i.jsx("div",{className:"application-success-mark",children:"✓"}),i.jsx("span",{className:"panel-kicker",children:"Application received"}),i.jsx("h1",{children:"Thanks for stepping up."}),i.jsxs("p",{children:["Your answers were sent to ",I,". You can only apply once to this opening."]}),i.jsxs("a",{className:"button button-muted",href:`/apply/${P}`,children:["View other openings ",i.jsx(J,{name:"arrow"})]})]}):g&&!r&&c.length===0?i.jsxs("div",{className:"application-public-state",children:[i.jsx("div",{className:"application-public-symbol",children:i.jsx(J,{name:"shield"})}),i.jsx("span",{className:"panel-kicker",children:"Access check"}),i.jsx("h1",{children:"We couldn’t open this application."}),i.jsx("p",{children:g}),i.jsx("a",{className:"button button-muted",href:"/",children:"Return home"})]}):r!=null&&r.already_submitted?i.jsxs("div",{className:"application-public-state",children:[i.jsx("div",{className:"application-success-mark",children:"✓"}),i.jsx("span",{className:"panel-kicker",children:"Already submitted"}),i.jsx("h1",{children:"Your application is on file."}),i.jsxs("p",{children:["You’ve already submitted an application for ",r.title,". Reopening it later won’t allow a second submission."]}),i.jsxs("a",{className:"button button-muted",href:`/apply/${P}`,children:["View other openings ",i.jsx(J,{name:"arrow"})]})]}):r?i.jsxs(i.Fragment,{children:[i.jsxs("div",{className:"application-public-topline",children:[i.jsx("span",{className:"application-status open",children:"Accepting applications"}),i.jsx("span",{className:"application-server-tag",children:I})]}),i.jsxs("div",{className:"application-public-heading",children:[i.jsxs("span",{className:"panel-kicker",children:["STAFF APPLICATION · ",r.role_name||"ROLE OPENING"]}),i.jsx("h1",{children:r.title}),i.jsx("p",{children:r.description||"Complete the questions below to apply for this opening."})]}),i.jsxs("div",{className:"application-verified",children:[i.jsx("span",{className:"application-verified-icon",children:i.jsx(J,{name:"shield"})}),i.jsxs("span",{children:[i.jsx("strong",{children:"Membership verified"}),i.jsxs("small",{children:["Signed in as ",((U=t.user)==null?void 0:U.global_name)||((ce=t.user)==null?void 0:ce.username)||"your Discord account",". Niko checked your server roles."]})]}),i.jsx("a",{href:"/auth/logout",children:"Switch account"})]}),i.jsxs("form",{className:"application-public-form",onSubmit:_,children:[r.questions.map((q,ge)=>{const he=q.type||"paragraph",Y=h[q.id]??(he==="multi_choice"?[]:""),we=me=>p(Ce=>({...Ce,[q.id]:me}));return i.jsxs("fieldset",{className:"form-field application-answer-field",children:[i.jsxs("legend",{children:[i.jsx("span",{className:"application-question-count",children:String(ge+1).padStart(2,"0")}),i.jsxs("span",{className:"form-label",children:[q.prompt,q.required&&i.jsx("i",{children:"Required"})]})]}),he==="short_text"?i.jsx("input",{type:"text",required:q.required,maxLength:200,value:typeof Y=="string"?Y:"",onChange:me=>we(me.target.value),placeholder:"Your answer"}):he==="single_choice"?i.jsx("div",{className:"application-choice-list application-single-choice",children:(q.options||[]).map(me=>i.jsxs("label",{className:Y===me?"is-selected":"",children:[i.jsx("input",{type:"radio",name:q.id,required:q.required&&!Y,checked:Y===me,onChange:()=>we(me)}),i.jsx("span",{children:me})]},me))}):he==="multi_choice"?i.jsx("div",{className:"application-choice-list application-multi-choice",children:(q.options||[]).map(me=>i.jsxs("label",{className:Array.isArray(Y)&&Y.includes(me)?"is-selected":"",children:[i.jsx("input",{type:"checkbox",checked:Array.isArray(Y)&&Y.includes(me),onChange:Ce=>we(Ce.target.checked?[...Array.isArray(Y)?Y:[],me]:(Array.isArray(Y)?Y:[]).filter(ee=>ee!==me))}),i.jsx("span",{children:me})]},me))}):he==="yes_no"?i.jsx("div",{className:"application-choice-list application-yes-no",children:["yes","no"].map(me=>i.jsxs("label",{className:Y===me?"is-selected":"",children:[i.jsx("input",{type:"radio",name:q.id,required:q.required&&!Y,checked:Y===me,onChange:()=>we(me)}),i.jsx("span",{children:me==="yes"?"Yes":"No"})]},me))}):he==="date"?i.jsx("input",{type:"date",required:q.required,value:typeof Y=="string"?Y:"",onChange:me=>we(me.target.value)}):i.jsxs(i.Fragment,{children:[i.jsx("textarea",{required:q.required,maxLength:4e3,rows:4,value:typeof Y=="string"?Y:"",onChange:me=>we(me.target.value),placeholder:"Write your answer here…"}),i.jsxs("small",{children:[(typeof Y=="string"?Y:"").length,"/4000 characters"]})]})]},q.id)}),g&&i.jsx("div",{className:"notice warning",role:"alert",children:g}),i.jsxs("div",{className:"application-submit-footer",children:[i.jsx("span",{children:"Your submission is private to this server’s application managers."}),i.jsxs("button",{type:"submit",className:"button button-primary",disabled:N,children:[N?"Sending…":"Submit application"," ",i.jsx(J,{name:"arrow"})]})]})]})]}):c.length>0?i.jsxs("div",{className:"application-public-state application-opening-state",children:[i.jsxs("span",{className:"panel-kicker",children:[I," · open roles"]}),i.jsx("h1",{children:"Choose your opening."}),i.jsx("p",{children:"Select an eligible team role to start your application."}),i.jsx("div",{className:"public-opening-list",children:c.map(q=>i.jsxs("article",{className:"public-opening-card",children:[i.jsxs("div",{children:[i.jsx("span",{className:`application-status ${q.already_submitted?"closed":q.eligible?"open":"closed"}`,children:q.already_submitted?"Already applied":q.eligible?"Eligible":"Role required"}),i.jsx("h2",{children:q.title}),i.jsx("p",{children:q.description||`Apply for ${q.role_name||"this role"}.`})]}),q.eligible&&!q.already_submitted&&i.jsxs("a",{className:"button button-primary",href:`/apply/${P}/${q.id}`,children:["Apply ",i.jsx(J,{name:"arrow"})]})]},q.id))})]}):i.jsxs("div",{className:"application-public-state",children:[i.jsx("div",{className:"application-public-symbol",children:i.jsx(J,{name:"users"})}),i.jsx("span",{className:"panel-kicker",children:"Nothing open just yet"}),i.jsx("h1",{children:"No openings available."}),i.jsx("p",{children:g||"This server doesn’t have any open staff applications right now."}),i.jsx("a",{className:"button button-muted",href:"/",children:"Return home"})]}):i.jsxs("div",{className:"application-public-state",children:[i.jsx("div",{className:"application-public-symbol",children:i.jsx(J,{name:"lock"})}),i.jsx("span",{className:"panel-kicker",children:"A safe, verified application"}),i.jsx("h1",{children:"Sign in to continue."}),i.jsx("p",{children:"Use your Discord account to confirm that you’re a member of this server and eligible for its openings."}),t!=null&&t.oauth_available?i.jsxs("a",{className:"button button-primary",href:L,children:["Continue with Discord ",i.jsx(J,{name:"arrow"})]}):i.jsx("p",{className:"form-error",children:"Discord sign-in isn’t available right now."})]})}),i.jsxs("footer",{className:"application-public-footer",children:[i.jsx("span",{children:"Identity and server roles verified by Discord."}),(S==null?void 0:S.bot_avatar_url)&&i.jsx("img",{src:S.bot_avatar_url,alt:"Niko"})]})]})})]})}const sf=[{question:"How do I invite Niko to my server?",answer:"Use the Add to Discord button in the site header to start the invite flow. You’ll need permission to add apps to the server."},{question:"Where can I find setup instructions and command help?",answer:"The documentation library includes setup guides, feature walkthroughs, and a searchable command reference."},{question:"Why isn’t a command or feature working?",answer:"Check that Niko is online and has the permissions needed in the channel. If the issue continues, share the command name and a short description in the support server."},{question:"How do I report a bug or request a feature?",answer:"Join the support server and post in the appropriate help or feedback channel. Include steps to reproduce bugs, and never share passwords or private tokens."},{question:"How can I request deletion of my data?",answer:"Contact the Niko team through the support server and include your Discord user ID so staff can locate the relevant data."}];function JS(){var c;const t=Ln(),s=(c=t==null?void 0:t.support_server_url)==null?void 0:c.trim(),[r,o]=T.useState(0);return i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"support"}),i.jsxs("main",{className:"shell page-main support-page",children:[i.jsxs("section",{className:"support-hero",children:[i.jsx("div",{className:"eyebrow",children:"Niko support"}),i.jsxs("h1",{children:["Let’s get you ",i.jsx("em",{children:"unstuck."})]}),i.jsx("p",{children:"Browse quick answers, explore the guides, or talk with the community and Niko team."}),i.jsxs("div",{className:"support-actions",children:[i.jsxs("a",{className:"button button-primary",href:"/docs",children:["Browse documentation ",i.jsx(J,{name:"arrow"})]}),s&&i.jsxs("a",{className:"button button-muted",href:"/discord",children:["Join the support server ",i.jsx(J,{name:"arrow"})]})]})]}),i.jsxs("section",{className:"support-faq","aria-labelledby":"support-faq-title",children:[i.jsxs("div",{className:"support-section-heading",children:[i.jsxs("div",{children:[i.jsx("div",{className:"eyebrow",children:"Quick answers"}),i.jsx("h2",{id:"support-faq-title",children:"Frequently asked questions"})]}),i.jsxs("span",{className:"support-faq-count",children:[sf.length," helpful guides"]})]}),i.jsx("div",{className:"support-faq-list",children:sf.map((u,h)=>{const p=r===h,f=`support-faq-answer-${h}`;return i.jsxs("article",{className:`support-faq-item${p?" is-open":""}`,children:[i.jsx("h3",{children:i.jsxs("button",{type:"button","aria-expanded":p,"aria-controls":f,onClick:()=>o(p?null:h),children:[i.jsxs("span",{className:"support-faq-question",children:[i.jsx("span",{className:"support-faq-number",children:String(h+1).padStart(2,"0")}),u.question]}),i.jsx("span",{className:"support-faq-toggle",children:i.jsx(J,{name:p?"minus":"plus"})})]})}),i.jsx("div",{id:f,className:"support-faq-answer","aria-hidden":!p,children:i.jsx("div",{className:"support-faq-answer-inner",children:i.jsxs("p",{children:[u.answer,h===1&&i.jsxs(i.Fragment,{children:[" ",i.jsxs("a",{href:"/docs",tabIndex:p?0:-1,children:["Open the docs ",i.jsx("span",{"aria-hidden":"true",children:"↗"})]}),"."]})]})})})]},u.question)})})]}),i.jsxs("aside",{className:"support-contact-card",children:[i.jsx("div",{className:"support-contact-mark",children:i.jsx(J,{name:"message"})}),i.jsxs("div",{children:[i.jsx("div",{className:"eyebrow",children:"Need a hand?"}),i.jsx("h2",{children:"Find us in the community."}),i.jsx("p",{children:"Get help from other Niko users and the staff team in the official support server."})]}),s?i.jsxs("a",{className:"button button-primary",href:"/discord",children:["Open support server ",i.jsx(J,{name:"arrow"})]}):i.jsx("p",{className:"support-missing-link",role:"status",children:"The support server link isn’t available right now. Please check back later."})]})]}),i.jsx(Nt,{})]})}function ZS(){var r;const t=Ln(),s=(r=t==null?void 0:t.support_server_url)==null?void 0:r.trim();return T.useEffect(()=>{s&&window.location.replace(s)},[s]),t?s?i.jsxs("main",{className:"discord-redirect-state",children:[i.jsx("div",{className:"loading-ring"}),i.jsx("p",{children:"Taking you to the Niko support server…"}),i.jsx("a",{href:s,children:"Continue if you aren’t redirected"})]}):i.jsxs(i.Fragment,{children:[i.jsx(Ue,{page:"support"}),i.jsxs("main",{className:"shell page-main discord-redirect-missing",children:[i.jsx("div",{className:"eyebrow",children:"Niko support"}),i.jsx("h1",{children:"We couldn’t find the support link."}),i.jsx("p",{children:"The official support server link isn’t configured right now. Please check back later."}),i.jsx("a",{className:"button button-primary",href:"/support",children:"Visit support"})]}),i.jsx(Nt,{})]}):i.jsxs("main",{className:"discord-redirect-state",children:[i.jsx("div",{className:"loading-ring"}),i.jsx("p",{children:"Checking the Niko support link…"})]})}function eN(){const[t,s]=T.useState(Tm);if(T.useEffect(()=>{const r=()=>s(Tm());return window.addEventListener("popstate",r),()=>window.removeEventListener("popstate",r)},[]),t==="commands")return i.jsx(Nb,{});if(t==="docs-detail"){const r=window.location.pathname.split("/"),o=r[r.length-1];return i.jsx(cS,{slug:o})}if(t==="docs")return i.jsx(uS,{});if(t==="staff")return i.jsx(YS,{});if(t==="application")return i.jsx(QS,{});if(t==="dashboard")return i.jsx(nS,{});if(t==="team")return i.jsx(KS,{});if(t==="team-member")return i.jsx(qS,{id:window.location.pathname.split("/").filter(Boolean)[1]||""});if(t==="support")return i.jsx(JS,{});if(t==="discord")return i.jsx(ZS,{});if(t==="privacy")return i.jsx(hc,{type:"privacy"});if(t==="terms")return i.jsx(hc,{type:"terms"});if(t==="community")return i.jsx(hc,{type:"community"});if(t==="donate")return i.jsx(mS,{});if(t==="transcript"){const o=window.location.pathname.split("/").filter(Boolean)[1]||"";return i.jsx(AS,{transcriptId:o})}if(t==="changelog")return i.jsx(MS,{});if(t==="changelog-detail"){const r=window.location.pathname.split("/"),o=r[r.length-1];return i.jsx(_S,{slug:o})}return i.jsx(dS,{})}"serviceWorker"in navigator&&window.addEventListener("load",()=>{navigator.serviceWorker.register("/service-worker.js").catch(t=>{console.warn("Niko app support could not be initialized.",t)})});Ex.createRoot(document.getElementById("root")).render(i.jsx(T.StrictMode,{children:i.jsx(eN,{})}));
