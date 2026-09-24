var yx=Object.defineProperty;var vx=(t,s,i)=>s in t?yx(t,s,{enumerable:!0,configurable:!0,writable:!0,value:i}):t[s]=i;var mm=(t,s,i)=>vx(t,typeof s!="symbol"?s+"":s,i);(function(){const s=document.createElement("link").relList;if(s&&s.supports&&s.supports("modulepreload"))return;for(const c of document.querySelectorAll('link[rel="modulepreload"]'))o(c);new MutationObserver(c=>{for(const d of c)if(d.type==="childList")for(const h of d.addedNodes)h.tagName==="LINK"&&h.rel==="modulepreload"&&o(h)}).observe(document,{childList:!0,subtree:!0});function i(c){const d={};return c.integrity&&(d.integrity=c.integrity),c.referrerPolicy&&(d.referrerPolicy=c.referrerPolicy),c.crossOrigin==="use-credentials"?d.credentials="include":c.crossOrigin==="anonymous"?d.credentials="omit":d.credentials="same-origin",d}function o(c){if(c.ep)return;c.ep=!0;const d=i(c);fetch(c.href,d)}})();var Ll={exports:{}},Nr={},Il={exports:{}},ue={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var fm;function xx(){if(fm)return ue;fm=1;var t=Symbol.for("react.element"),s=Symbol.for("react.portal"),i=Symbol.for("react.fragment"),o=Symbol.for("react.strict_mode"),c=Symbol.for("react.profiler"),d=Symbol.for("react.provider"),h=Symbol.for("react.context"),f=Symbol.for("react.forward_ref"),p=Symbol.for("react.suspense"),v=Symbol.for("react.memo"),g=Symbol.for("react.lazy"),x=Symbol.iterator;function w(M){return M===null||typeof M!="object"?null:(M=x&&M[x]||M["@@iterator"],typeof M=="function"?M:null)}var j={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},k=Object.assign,S={};function N(M,U,ce){this.props=M,this.context=U,this.refs=S,this.updater=ce||j}N.prototype.isReactComponent={},N.prototype.setState=function(M,U){if(typeof M!="object"&&typeof M!="function"&&M!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,M,U,"setState")},N.prototype.forceUpdate=function(M){this.updater.enqueueForceUpdate(this,M,"forceUpdate")};function B(){}B.prototype=N.prototype;function E(M,U,ce){this.props=M,this.context=U,this.refs=S,this.updater=ce||j}var R=E.prototype=new B;R.constructor=E,k(R,N.prototype),R.isPureReactComponent=!0;var I=Array.isArray,D=Object.prototype.hasOwnProperty,F={current:null},V={key:!0,ref:!0,__self:!0,__source:!0};function z(M,U,ce){var de,fe={},pe=null,Se=null;if(U!=null)for(de in U.ref!==void 0&&(Se=U.ref),U.key!==void 0&&(pe=""+U.key),U)D.call(U,de)&&!V.hasOwnProperty(de)&&(fe[de]=U[de]);var we=arguments.length-2;if(we===1)fe.children=ce;else if(1<we){for(var Me=Array(we),yt=0;yt<we;yt++)Me[yt]=arguments[yt+2];fe.children=Me}if(M&&M.defaultProps)for(de in we=M.defaultProps,we)fe[de]===void 0&&(fe[de]=we[de]);return{$$typeof:t,type:M,key:pe,ref:Se,props:fe,_owner:F.current}}function oe(M,U){return{$$typeof:t,type:M.type,key:U,ref:M.ref,props:M.props,_owner:M._owner}}function le(M){return typeof M=="object"&&M!==null&&M.$$typeof===t}function xe(M){var U={"=":"=0",":":"=2"};return"$"+M.replace(/[=:]/g,function(ce){return U[ce]})}var ve=/\/+/g;function ie(M,U){return typeof M=="object"&&M!==null&&M.key!=null?xe(""+M.key):U.toString(36)}function Pe(M,U,ce,de,fe){var pe=typeof M;(pe==="undefined"||pe==="boolean")&&(M=null);var Se=!1;if(M===null)Se=!0;else switch(pe){case"string":case"number":Se=!0;break;case"object":switch(M.$$typeof){case t:case s:Se=!0}}if(Se)return Se=M,fe=fe(Se),M=de===""?"."+ie(Se,0):de,I(fe)?(ce="",M!=null&&(ce=M.replace(ve,"$&/")+"/"),Pe(fe,U,ce,"",function(yt){return yt})):fe!=null&&(le(fe)&&(fe=oe(fe,ce+(!fe.key||Se&&Se.key===fe.key?"":(""+fe.key).replace(ve,"$&/")+"/")+M)),U.push(fe)),1;if(Se=0,de=de===""?".":de+":",I(M))for(var we=0;we<M.length;we++){pe=M[we];var Me=de+ie(pe,we);Se+=Pe(pe,U,ce,Me,fe)}else if(Me=w(M),typeof Me=="function")for(M=Me.call(M),we=0;!(pe=M.next()).done;)pe=pe.value,Me=de+ie(pe,we++),Se+=Pe(pe,U,ce,Me,fe);else if(pe==="object")throw U=String(M),Error("Objects are not valid as a React child (found: "+(U==="[object Object]"?"object with keys {"+Object.keys(M).join(", ")+"}":U)+"). If you meant to render a collection of children, use an array instead.");return Se}function Ie(M,U,ce){if(M==null)return M;var de=[],fe=0;return Pe(M,de,"","",function(pe){return U.call(ce,pe,fe++)}),de}function Ae(M){if(M._status===-1){var U=M._result;U=U(),U.then(function(ce){(M._status===0||M._status===-1)&&(M._status=1,M._result=ce)},function(ce){(M._status===0||M._status===-1)&&(M._status=2,M._result=ce)}),M._status===-1&&(M._status=0,M._result=U)}if(M._status===1)return M._result.default;throw M._result}var Y={current:null},O={transition:null},q={ReactCurrentDispatcher:Y,ReactCurrentBatchConfig:O,ReactCurrentOwner:F};function K(){throw Error("act(...) is not supported in production builds of React.")}return ue.Children={map:Ie,forEach:function(M,U,ce){Ie(M,function(){U.apply(this,arguments)},ce)},count:function(M){var U=0;return Ie(M,function(){U++}),U},toArray:function(M){return Ie(M,function(U){return U})||[]},only:function(M){if(!le(M))throw Error("React.Children.only expected to receive a single React element child.");return M}},ue.Component=N,ue.Fragment=i,ue.Profiler=c,ue.PureComponent=E,ue.StrictMode=o,ue.Suspense=p,ue.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=q,ue.act=K,ue.cloneElement=function(M,U,ce){if(M==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+M+".");var de=k({},M.props),fe=M.key,pe=M.ref,Se=M._owner;if(U!=null){if(U.ref!==void 0&&(pe=U.ref,Se=F.current),U.key!==void 0&&(fe=""+U.key),M.type&&M.type.defaultProps)var we=M.type.defaultProps;for(Me in U)D.call(U,Me)&&!V.hasOwnProperty(Me)&&(de[Me]=U[Me]===void 0&&we!==void 0?we[Me]:U[Me])}var Me=arguments.length-2;if(Me===1)de.children=ce;else if(1<Me){we=Array(Me);for(var yt=0;yt<Me;yt++)we[yt]=arguments[yt+2];de.children=we}return{$$typeof:t,type:M.type,key:fe,ref:pe,props:de,_owner:Se}},ue.createContext=function(M){return M={$$typeof:h,_currentValue:M,_currentValue2:M,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},M.Provider={$$typeof:d,_context:M},M.Consumer=M},ue.createElement=z,ue.createFactory=function(M){var U=z.bind(null,M);return U.type=M,U},ue.createRef=function(){return{current:null}},ue.forwardRef=function(M){return{$$typeof:f,render:M}},ue.isValidElement=le,ue.lazy=function(M){return{$$typeof:g,_payload:{_status:-1,_result:M},_init:Ae}},ue.memo=function(M,U){return{$$typeof:v,type:M,compare:U===void 0?null:U}},ue.startTransition=function(M){var U=O.transition;O.transition={};try{M()}finally{O.transition=U}},ue.unstable_act=K,ue.useCallback=function(M,U){return Y.current.useCallback(M,U)},ue.useContext=function(M){return Y.current.useContext(M)},ue.useDebugValue=function(){},ue.useDeferredValue=function(M){return Y.current.useDeferredValue(M)},ue.useEffect=function(M,U){return Y.current.useEffect(M,U)},ue.useId=function(){return Y.current.useId()},ue.useImperativeHandle=function(M,U,ce){return Y.current.useImperativeHandle(M,U,ce)},ue.useInsertionEffect=function(M,U){return Y.current.useInsertionEffect(M,U)},ue.useLayoutEffect=function(M,U){return Y.current.useLayoutEffect(M,U)},ue.useMemo=function(M,U){return Y.current.useMemo(M,U)},ue.useReducer=function(M,U,ce){return Y.current.useReducer(M,U,ce)},ue.useRef=function(M){return Y.current.useRef(M)},ue.useState=function(M){return Y.current.useState(M)},ue.useSyncExternalStore=function(M,U,ce){return Y.current.useSyncExternalStore(M,U,ce)},ue.useTransition=function(){return Y.current.useTransition()},ue.version="18.3.1",ue}var pm;function zc(){return pm||(pm=1,Il.exports=xx()),Il.exports}/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var gm;function wx(){if(gm)return Nr;gm=1;var t=zc(),s=Symbol.for("react.element"),i=Symbol.for("react.fragment"),o=Object.prototype.hasOwnProperty,c=t.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,d={key:!0,ref:!0,__self:!0,__source:!0};function h(f,p,v){var g,x={},w=null,j=null;v!==void 0&&(w=""+v),p.key!==void 0&&(w=""+p.key),p.ref!==void 0&&(j=p.ref);for(g in p)o.call(p,g)&&!d.hasOwnProperty(g)&&(x[g]=p[g]);if(f&&f.defaultProps)for(g in p=f.defaultProps,p)x[g]===void 0&&(x[g]=p[g]);return{$$typeof:s,type:f,key:w,ref:j,props:x,_owner:c.current}}return Nr.Fragment=i,Nr.jsx=h,Nr.jsxs=h,Nr}var ym;function bx(){return ym||(ym=1,Ll.exports=wx()),Ll.exports}var r=bx(),P=zc(),Yi={},Vl={exports:{}},pt={},Fl={exports:{}},Bl={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var vm;function kx(){return vm||(vm=1,(function(t){function s(O,q){var K=O.length;O.push(q);e:for(;0<K;){var M=K-1>>>1,U=O[M];if(0<c(U,q))O[M]=q,O[K]=U,K=M;else break e}}function i(O){return O.length===0?null:O[0]}function o(O){if(O.length===0)return null;var q=O[0],K=O.pop();if(K!==q){O[0]=K;e:for(var M=0,U=O.length,ce=U>>>1;M<ce;){var de=2*(M+1)-1,fe=O[de],pe=de+1,Se=O[pe];if(0>c(fe,K))pe<U&&0>c(Se,fe)?(O[M]=Se,O[pe]=K,M=pe):(O[M]=fe,O[de]=K,M=de);else if(pe<U&&0>c(Se,K))O[M]=Se,O[pe]=K,M=pe;else break e}}return q}function c(O,q){var K=O.sortIndex-q.sortIndex;return K!==0?K:O.id-q.id}if(typeof performance=="object"&&typeof performance.now=="function"){var d=performance;t.unstable_now=function(){return d.now()}}else{var h=Date,f=h.now();t.unstable_now=function(){return h.now()-f}}var p=[],v=[],g=1,x=null,w=3,j=!1,k=!1,S=!1,N=typeof setTimeout=="function"?setTimeout:null,B=typeof clearTimeout=="function"?clearTimeout:null,E=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function R(O){for(var q=i(v);q!==null;){if(q.callback===null)o(v);else if(q.startTime<=O)o(v),q.sortIndex=q.expirationTime,s(p,q);else break;q=i(v)}}function I(O){if(S=!1,R(O),!k)if(i(p)!==null)k=!0,Ae(D);else{var q=i(v);q!==null&&Y(I,q.startTime-O)}}function D(O,q){k=!1,S&&(S=!1,B(z),z=-1),j=!0;var K=w;try{for(R(q),x=i(p);x!==null&&(!(x.expirationTime>q)||O&&!xe());){var M=x.callback;if(typeof M=="function"){x.callback=null,w=x.priorityLevel;var U=M(x.expirationTime<=q);q=t.unstable_now(),typeof U=="function"?x.callback=U:x===i(p)&&o(p),R(q)}else o(p);x=i(p)}if(x!==null)var ce=!0;else{var de=i(v);de!==null&&Y(I,de.startTime-q),ce=!1}return ce}finally{x=null,w=K,j=!1}}var F=!1,V=null,z=-1,oe=5,le=-1;function xe(){return!(t.unstable_now()-le<oe)}function ve(){if(V!==null){var O=t.unstable_now();le=O;var q=!0;try{q=V(!0,O)}finally{q?ie():(F=!1,V=null)}}else F=!1}var ie;if(typeof E=="function")ie=function(){E(ve)};else if(typeof MessageChannel<"u"){var Pe=new MessageChannel,Ie=Pe.port2;Pe.port1.onmessage=ve,ie=function(){Ie.postMessage(null)}}else ie=function(){N(ve,0)};function Ae(O){V=O,F||(F=!0,ie())}function Y(O,q){z=N(function(){O(t.unstable_now())},q)}t.unstable_IdlePriority=5,t.unstable_ImmediatePriority=1,t.unstable_LowPriority=4,t.unstable_NormalPriority=3,t.unstable_Profiling=null,t.unstable_UserBlockingPriority=2,t.unstable_cancelCallback=function(O){O.callback=null},t.unstable_continueExecution=function(){k||j||(k=!0,Ae(D))},t.unstable_forceFrameRate=function(O){0>O||125<O?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):oe=0<O?Math.floor(1e3/O):5},t.unstable_getCurrentPriorityLevel=function(){return w},t.unstable_getFirstCallbackNode=function(){return i(p)},t.unstable_next=function(O){switch(w){case 1:case 2:case 3:var q=3;break;default:q=w}var K=w;w=q;try{return O()}finally{w=K}},t.unstable_pauseExecution=function(){},t.unstable_requestPaint=function(){},t.unstable_runWithPriority=function(O,q){switch(O){case 1:case 2:case 3:case 4:case 5:break;default:O=3}var K=w;w=O;try{return q()}finally{w=K}},t.unstable_scheduleCallback=function(O,q,K){var M=t.unstable_now();switch(typeof K=="object"&&K!==null?(K=K.delay,K=typeof K=="number"&&0<K?M+K:M):K=M,O){case 1:var U=-1;break;case 2:U=250;break;case 5:U=1073741823;break;case 4:U=1e4;break;default:U=5e3}return U=K+U,O={id:g++,callback:q,priorityLevel:O,startTime:K,expirationTime:U,sortIndex:-1},K>M?(O.sortIndex=K,s(v,O),i(p)===null&&O===i(v)&&(S?(B(z),z=-1):S=!0,Y(I,K-M))):(O.sortIndex=U,s(p,O),k||j||(k=!0,Ae(D))),O},t.unstable_shouldYield=xe,t.unstable_wrapCallback=function(O){var q=w;return function(){var K=w;w=q;try{return O.apply(this,arguments)}finally{w=K}}}})(Bl)),Bl}var xm;function jx(){return xm||(xm=1,Fl.exports=kx()),Fl.exports}/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var wm;function Sx(){if(wm)return pt;wm=1;var t=zc(),s=jx();function i(e){for(var n="https://reactjs.org/docs/error-decoder.html?invariant="+e,a=1;a<arguments.length;a++)n+="&args[]="+encodeURIComponent(arguments[a]);return"Minified React error #"+e+"; visit "+n+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var o=new Set,c={};function d(e,n){h(e,n),h(e+"Capture",n)}function h(e,n){for(c[e]=n,e=0;e<n.length;e++)o.add(n[e])}var f=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),p=Object.prototype.hasOwnProperty,v=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,g={},x={};function w(e){return p.call(x,e)?!0:p.call(g,e)?!1:v.test(e)?x[e]=!0:(g[e]=!0,!1)}function j(e,n,a,l){if(a!==null&&a.type===0)return!1;switch(typeof n){case"function":case"symbol":return!0;case"boolean":return l?!1:a!==null?!a.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function k(e,n,a,l){if(n===null||typeof n>"u"||j(e,n,a,l))return!0;if(l)return!1;if(a!==null)switch(a.type){case 3:return!n;case 4:return n===!1;case 5:return isNaN(n);case 6:return isNaN(n)||1>n}return!1}function S(e,n,a,l,u,m,y){this.acceptsBooleans=n===2||n===3||n===4,this.attributeName=l,this.attributeNamespace=u,this.mustUseProperty=a,this.propertyName=e,this.type=n,this.sanitizeURL=m,this.removeEmptyString=y}var N={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){N[e]=new S(e,0,!1,e,null,!1,!1)}),[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var n=e[0];N[n]=new S(n,1,!1,e[1],null,!1,!1)}),["contentEditable","draggable","spellCheck","value"].forEach(function(e){N[e]=new S(e,2,!1,e.toLowerCase(),null,!1,!1)}),["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){N[e]=new S(e,2,!1,e,null,!1,!1)}),"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){N[e]=new S(e,3,!1,e.toLowerCase(),null,!1,!1)}),["checked","multiple","muted","selected"].forEach(function(e){N[e]=new S(e,3,!0,e,null,!1,!1)}),["capture","download"].forEach(function(e){N[e]=new S(e,4,!1,e,null,!1,!1)}),["cols","rows","size","span"].forEach(function(e){N[e]=new S(e,6,!1,e,null,!1,!1)}),["rowSpan","start"].forEach(function(e){N[e]=new S(e,5,!1,e.toLowerCase(),null,!1,!1)});var B=/[\-:]([a-z])/g;function E(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var n=e.replace(B,E);N[n]=new S(n,1,!1,e,null,!1,!1)}),"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var n=e.replace(B,E);N[n]=new S(n,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)}),["xml:base","xml:lang","xml:space"].forEach(function(e){var n=e.replace(B,E);N[n]=new S(n,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)}),["tabIndex","crossOrigin"].forEach(function(e){N[e]=new S(e,1,!1,e.toLowerCase(),null,!1,!1)}),N.xlinkHref=new S("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1),["src","href","action","formAction"].forEach(function(e){N[e]=new S(e,1,!1,e.toLowerCase(),null,!0,!0)});function R(e,n,a,l){var u=N.hasOwnProperty(n)?N[n]:null;(u!==null?u.type!==0:l||!(2<n.length)||n[0]!=="o"&&n[0]!=="O"||n[1]!=="n"&&n[1]!=="N")&&(k(n,a,u,l)&&(a=null),l||u===null?w(n)&&(a===null?e.removeAttribute(n):e.setAttribute(n,""+a)):u.mustUseProperty?e[u.propertyName]=a===null?u.type===3?!1:"":a:(n=u.attributeName,l=u.attributeNamespace,a===null?e.removeAttribute(n):(u=u.type,a=u===3||u===4&&a===!0?"":""+a,l?e.setAttributeNS(l,n,a):e.setAttribute(n,a))))}var I=t.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,D=Symbol.for("react.element"),F=Symbol.for("react.portal"),V=Symbol.for("react.fragment"),z=Symbol.for("react.strict_mode"),oe=Symbol.for("react.profiler"),le=Symbol.for("react.provider"),xe=Symbol.for("react.context"),ve=Symbol.for("react.forward_ref"),ie=Symbol.for("react.suspense"),Pe=Symbol.for("react.suspense_list"),Ie=Symbol.for("react.memo"),Ae=Symbol.for("react.lazy"),Y=Symbol.for("react.offscreen"),O=Symbol.iterator;function q(e){return e===null||typeof e!="object"?null:(e=O&&e[O]||e["@@iterator"],typeof e=="function"?e:null)}var K=Object.assign,M;function U(e){if(M===void 0)try{throw Error()}catch(a){var n=a.stack.trim().match(/\n( *(at )?)/);M=n&&n[1]||""}return`
`+M+e}var ce=!1;function de(e,n){if(!e||ce)return"";ce=!0;var a=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(n)if(n=function(){throw Error()},Object.defineProperty(n.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(n,[])}catch(L){var l=L}Reflect.construct(e,[],n)}else{try{n.call()}catch(L){l=L}e.call(n.prototype)}else{try{throw Error()}catch(L){l=L}e()}}catch(L){if(L&&l&&typeof L.stack=="string"){for(var u=L.stack.split(`
`),m=l.stack.split(`
`),y=u.length-1,b=m.length-1;1<=y&&0<=b&&u[y]!==m[b];)b--;for(;1<=y&&0<=b;y--,b--)if(u[y]!==m[b]){if(y!==1||b!==1)do if(y--,b--,0>b||u[y]!==m[b]){var C=`
`+u[y].replace(" at new "," at ");return e.displayName&&C.includes("<anonymous>")&&(C=C.replace("<anonymous>",e.displayName)),C}while(1<=y&&0<=b);break}}}finally{ce=!1,Error.prepareStackTrace=a}return(e=e?e.displayName||e.name:"")?U(e):""}function fe(e){switch(e.tag){case 5:return U(e.type);case 16:return U("Lazy");case 13:return U("Suspense");case 19:return U("SuspenseList");case 0:case 2:case 15:return e=de(e.type,!1),e;case 11:return e=de(e.type.render,!1),e;case 1:return e=de(e.type,!0),e;default:return""}}function pe(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case V:return"Fragment";case F:return"Portal";case oe:return"Profiler";case z:return"StrictMode";case ie:return"Suspense";case Pe:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case xe:return(e.displayName||"Context")+".Consumer";case le:return(e._context.displayName||"Context")+".Provider";case ve:var n=e.render;return e=e.displayName,e||(e=n.displayName||n.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case Ie:return n=e.displayName||null,n!==null?n:pe(e.type)||"Memo";case Ae:n=e._payload,e=e._init;try{return pe(e(n))}catch{}}return null}function Se(e){var n=e.type;switch(e.tag){case 24:return"Cache";case 9:return(n.displayName||"Context")+".Consumer";case 10:return(n._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=n.render,e=e.displayName||e.name||"",n.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return n;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return pe(n);case 8:return n===z?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof n=="function")return n.displayName||n.name||null;if(typeof n=="string")return n}return null}function we(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function Me(e){var n=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(n==="checkbox"||n==="radio")}function yt(e){var n=Me(e)?"checked":"value",a=Object.getOwnPropertyDescriptor(e.constructor.prototype,n),l=""+e[n];if(!e.hasOwnProperty(n)&&typeof a<"u"&&typeof a.get=="function"&&typeof a.set=="function"){var u=a.get,m=a.set;return Object.defineProperty(e,n,{configurable:!0,get:function(){return u.call(this)},set:function(y){l=""+y,m.call(this,y)}}),Object.defineProperty(e,n,{enumerable:a.enumerable}),{getValue:function(){return l},setValue:function(y){l=""+y},stopTracking:function(){e._valueTracker=null,delete e[n]}}}}function Or(e){e._valueTracker||(e._valueTracker=yt(e))}function xu(e){if(!e)return!1;var n=e._valueTracker;if(!n)return!0;var a=n.getValue(),l="";return e&&(l=Me(e)?e.checked?"true":"false":e.value),e=l,e!==a?(n.setValue(e),!0):!1}function zr(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function za(e,n){var a=n.checked;return K({},n,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:a??e._wrapperState.initialChecked})}function wu(e,n){var a=n.defaultValue==null?"":n.defaultValue,l=n.checked!=null?n.checked:n.defaultChecked;a=we(n.value!=null?n.value:a),e._wrapperState={initialChecked:l,initialValue:a,controlled:n.type==="checkbox"||n.type==="radio"?n.checked!=null:n.value!=null}}function bu(e,n){n=n.checked,n!=null&&R(e,"checked",n,!1)}function Ua(e,n){bu(e,n);var a=we(n.value),l=n.type;if(a!=null)l==="number"?(a===0&&e.value===""||e.value!=a)&&(e.value=""+a):e.value!==""+a&&(e.value=""+a);else if(l==="submit"||l==="reset"){e.removeAttribute("value");return}n.hasOwnProperty("value")?Wa(e,n.type,a):n.hasOwnProperty("defaultValue")&&Wa(e,n.type,we(n.defaultValue)),n.checked==null&&n.defaultChecked!=null&&(e.defaultChecked=!!n.defaultChecked)}function ku(e,n,a){if(n.hasOwnProperty("value")||n.hasOwnProperty("defaultValue")){var l=n.type;if(!(l!=="submit"&&l!=="reset"||n.value!==void 0&&n.value!==null))return;n=""+e._wrapperState.initialValue,a||n===e.value||(e.value=n),e.defaultValue=n}a=e.name,a!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,a!==""&&(e.name=a)}function Wa(e,n,a){(n!=="number"||zr(e.ownerDocument)!==e)&&(a==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+a&&(e.defaultValue=""+a))}var Os=Array.isArray;function is(e,n,a,l){if(e=e.options,n){n={};for(var u=0;u<a.length;u++)n["$"+a[u]]=!0;for(a=0;a<e.length;a++)u=n.hasOwnProperty("$"+e[a].value),e[a].selected!==u&&(e[a].selected=u),u&&l&&(e[a].defaultSelected=!0)}else{for(a=""+we(a),n=null,u=0;u<e.length;u++){if(e[u].value===a){e[u].selected=!0,l&&(e[u].defaultSelected=!0);return}n!==null||e[u].disabled||(n=e[u])}n!==null&&(n.selected=!0)}}function $a(e,n){if(n.dangerouslySetInnerHTML!=null)throw Error(i(91));return K({},n,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function ju(e,n){var a=n.value;if(a==null){if(a=n.children,n=n.defaultValue,a!=null){if(n!=null)throw Error(i(92));if(Os(a)){if(1<a.length)throw Error(i(93));a=a[0]}n=a}n==null&&(n=""),a=n}e._wrapperState={initialValue:we(a)}}function Su(e,n){var a=we(n.value),l=we(n.defaultValue);a!=null&&(a=""+a,a!==e.value&&(e.value=a),n.defaultValue==null&&e.defaultValue!==a&&(e.defaultValue=a)),l!=null&&(e.defaultValue=""+l)}function Nu(e){var n=e.textContent;n===e._wrapperState.initialValue&&n!==""&&n!==null&&(e.value=n)}function Cu(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function Ha(e,n){return e==null||e==="http://www.w3.org/1999/xhtml"?Cu(n):e==="http://www.w3.org/2000/svg"&&n==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var Ur,Tu=(function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(n,a,l,u){MSApp.execUnsafeLocalFunction(function(){return e(n,a,l,u)})}:e})(function(e,n){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=n;else{for(Ur=Ur||document.createElement("div"),Ur.innerHTML="<svg>"+n.valueOf().toString()+"</svg>",n=Ur.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;n.firstChild;)e.appendChild(n.firstChild)}});function zs(e,n){if(n){var a=e.firstChild;if(a&&a===e.lastChild&&a.nodeType===3){a.nodeValue=n;return}}e.textContent=n}var Us={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},by=["Webkit","ms","Moz","O"];Object.keys(Us).forEach(function(e){by.forEach(function(n){n=n+e.charAt(0).toUpperCase()+e.substring(1),Us[n]=Us[e]})});function Pu(e,n,a){return n==null||typeof n=="boolean"||n===""?"":a||typeof n!="number"||n===0||Us.hasOwnProperty(e)&&Us[e]?(""+n).trim():n+"px"}function Mu(e,n){e=e.style;for(var a in n)if(n.hasOwnProperty(a)){var l=a.indexOf("--")===0,u=Pu(a,n[a],l);a==="float"&&(a="cssFloat"),l?e.setProperty(a,u):e[a]=u}}var ky=K({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function Ga(e,n){if(n){if(ky[e]&&(n.children!=null||n.dangerouslySetInnerHTML!=null))throw Error(i(137,e));if(n.dangerouslySetInnerHTML!=null){if(n.children!=null)throw Error(i(60));if(typeof n.dangerouslySetInnerHTML!="object"||!("__html"in n.dangerouslySetInnerHTML))throw Error(i(61))}if(n.style!=null&&typeof n.style!="object")throw Error(i(62))}}function Ka(e,n){if(e.indexOf("-")===-1)return typeof n.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var qa=null;function Xa(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var Ya=null,as=null,os=null;function Eu(e){if(e=ur(e)){if(typeof Ya!="function")throw Error(i(280));var n=e.stateNode;n&&(n=di(n),Ya(e.stateNode,e.type,n))}}function Au(e){as?os?os.push(e):os=[e]:as=e}function _u(){if(as){var e=as,n=os;if(os=as=null,Eu(e),n)for(e=0;e<n.length;e++)Eu(n[e])}}function Du(e,n){return e(n)}function Ru(){}var Qa=!1;function Lu(e,n,a){if(Qa)return e(n,a);Qa=!0;try{return Du(e,n,a)}finally{Qa=!1,(as!==null||os!==null)&&(Ru(),_u())}}function Ws(e,n){var a=e.stateNode;if(a===null)return null;var l=di(a);if(l===null)return null;a=l[n];e:switch(n){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(l=!l.disabled)||(e=e.type,l=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!l;break e;default:e=!1}if(e)return null;if(a&&typeof a!="function")throw Error(i(231,n,typeof a));return a}var Ja=!1;if(f)try{var $s={};Object.defineProperty($s,"passive",{get:function(){Ja=!0}}),window.addEventListener("test",$s,$s),window.removeEventListener("test",$s,$s)}catch{Ja=!1}function jy(e,n,a,l,u,m,y,b,C){var L=Array.prototype.slice.call(arguments,3);try{n.apply(a,L)}catch($){this.onError($)}}var Hs=!1,Wr=null,$r=!1,Za=null,Sy={onError:function(e){Hs=!0,Wr=e}};function Ny(e,n,a,l,u,m,y,b,C){Hs=!1,Wr=null,jy.apply(Sy,arguments)}function Cy(e,n,a,l,u,m,y,b,C){if(Ny.apply(this,arguments),Hs){if(Hs){var L=Wr;Hs=!1,Wr=null}else throw Error(i(198));$r||($r=!0,Za=L)}}function Dn(e){var n=e,a=e;if(e.alternate)for(;n.return;)n=n.return;else{e=n;do n=e,(n.flags&4098)!==0&&(a=n.return),e=n.return;while(e)}return n.tag===3?a:null}function Iu(e){if(e.tag===13){var n=e.memoizedState;if(n===null&&(e=e.alternate,e!==null&&(n=e.memoizedState)),n!==null)return n.dehydrated}return null}function Vu(e){if(Dn(e)!==e)throw Error(i(188))}function Ty(e){var n=e.alternate;if(!n){if(n=Dn(e),n===null)throw Error(i(188));return n!==e?null:e}for(var a=e,l=n;;){var u=a.return;if(u===null)break;var m=u.alternate;if(m===null){if(l=u.return,l!==null){a=l;continue}break}if(u.child===m.child){for(m=u.child;m;){if(m===a)return Vu(u),e;if(m===l)return Vu(u),n;m=m.sibling}throw Error(i(188))}if(a.return!==l.return)a=u,l=m;else{for(var y=!1,b=u.child;b;){if(b===a){y=!0,a=u,l=m;break}if(b===l){y=!0,l=u,a=m;break}b=b.sibling}if(!y){for(b=m.child;b;){if(b===a){y=!0,a=m,l=u;break}if(b===l){y=!0,l=m,a=u;break}b=b.sibling}if(!y)throw Error(i(189))}}if(a.alternate!==l)throw Error(i(190))}if(a.tag!==3)throw Error(i(188));return a.stateNode.current===a?e:n}function Fu(e){return e=Ty(e),e!==null?Bu(e):null}function Bu(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var n=Bu(e);if(n!==null)return n;e=e.sibling}return null}var Ou=s.unstable_scheduleCallback,zu=s.unstable_cancelCallback,Py=s.unstable_shouldYield,My=s.unstable_requestPaint,Ve=s.unstable_now,Ey=s.unstable_getCurrentPriorityLevel,eo=s.unstable_ImmediatePriority,Uu=s.unstable_UserBlockingPriority,Hr=s.unstable_NormalPriority,Ay=s.unstable_LowPriority,Wu=s.unstable_IdlePriority,Gr=null,Wt=null;function _y(e){if(Wt&&typeof Wt.onCommitFiberRoot=="function")try{Wt.onCommitFiberRoot(Gr,e,void 0,(e.current.flags&128)===128)}catch{}}var _t=Math.clz32?Math.clz32:Ly,Dy=Math.log,Ry=Math.LN2;function Ly(e){return e>>>=0,e===0?32:31-(Dy(e)/Ry|0)|0}var Kr=64,qr=4194304;function Gs(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function Xr(e,n){var a=e.pendingLanes;if(a===0)return 0;var l=0,u=e.suspendedLanes,m=e.pingedLanes,y=a&268435455;if(y!==0){var b=y&~u;b!==0?l=Gs(b):(m&=y,m!==0&&(l=Gs(m)))}else y=a&~u,y!==0?l=Gs(y):m!==0&&(l=Gs(m));if(l===0)return 0;if(n!==0&&n!==l&&(n&u)===0&&(u=l&-l,m=n&-n,u>=m||u===16&&(m&4194240)!==0))return n;if((l&4)!==0&&(l|=a&16),n=e.entangledLanes,n!==0)for(e=e.entanglements,n&=l;0<n;)a=31-_t(n),u=1<<a,l|=e[a],n&=~u;return l}function Iy(e,n){switch(e){case 1:case 2:case 4:return n+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return n+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function Vy(e,n){for(var a=e.suspendedLanes,l=e.pingedLanes,u=e.expirationTimes,m=e.pendingLanes;0<m;){var y=31-_t(m),b=1<<y,C=u[y];C===-1?((b&a)===0||(b&l)!==0)&&(u[y]=Iy(b,n)):C<=n&&(e.expiredLanes|=b),m&=~b}}function to(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function $u(){var e=Kr;return Kr<<=1,(Kr&4194240)===0&&(Kr=64),e}function no(e){for(var n=[],a=0;31>a;a++)n.push(e);return n}function Ks(e,n,a){e.pendingLanes|=n,n!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,n=31-_t(n),e[n]=a}function Fy(e,n){var a=e.pendingLanes&~n;e.pendingLanes=n,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=n,e.mutableReadLanes&=n,e.entangledLanes&=n,n=e.entanglements;var l=e.eventTimes;for(e=e.expirationTimes;0<a;){var u=31-_t(a),m=1<<u;n[u]=0,l[u]=-1,e[u]=-1,a&=~m}}function so(e,n){var a=e.entangledLanes|=n;for(e=e.entanglements;a;){var l=31-_t(a),u=1<<l;u&n|e[l]&n&&(e[l]|=n),a&=~u}}var be=0;function Hu(e){return e&=-e,1<e?4<e?(e&268435455)!==0?16:536870912:4:1}var Gu,ro,Ku,qu,Xu,io=!1,Yr=[],cn=null,un=null,dn=null,qs=new Map,Xs=new Map,hn=[],By="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function Yu(e,n){switch(e){case"focusin":case"focusout":cn=null;break;case"dragenter":case"dragleave":un=null;break;case"mouseover":case"mouseout":dn=null;break;case"pointerover":case"pointerout":qs.delete(n.pointerId);break;case"gotpointercapture":case"lostpointercapture":Xs.delete(n.pointerId)}}function Ys(e,n,a,l,u,m){return e===null||e.nativeEvent!==m?(e={blockedOn:n,domEventName:a,eventSystemFlags:l,nativeEvent:m,targetContainers:[u]},n!==null&&(n=ur(n),n!==null&&ro(n)),e):(e.eventSystemFlags|=l,n=e.targetContainers,u!==null&&n.indexOf(u)===-1&&n.push(u),e)}function Oy(e,n,a,l,u){switch(n){case"focusin":return cn=Ys(cn,e,n,a,l,u),!0;case"dragenter":return un=Ys(un,e,n,a,l,u),!0;case"mouseover":return dn=Ys(dn,e,n,a,l,u),!0;case"pointerover":var m=u.pointerId;return qs.set(m,Ys(qs.get(m)||null,e,n,a,l,u)),!0;case"gotpointercapture":return m=u.pointerId,Xs.set(m,Ys(Xs.get(m)||null,e,n,a,l,u)),!0}return!1}function Qu(e){var n=Rn(e.target);if(n!==null){var a=Dn(n);if(a!==null){if(n=a.tag,n===13){if(n=Iu(a),n!==null){e.blockedOn=n,Xu(e.priority,function(){Ku(a)});return}}else if(n===3&&a.stateNode.current.memoizedState.isDehydrated){e.blockedOn=a.tag===3?a.stateNode.containerInfo:null;return}}}e.blockedOn=null}function Qr(e){if(e.blockedOn!==null)return!1;for(var n=e.targetContainers;0<n.length;){var a=oo(e.domEventName,e.eventSystemFlags,n[0],e.nativeEvent);if(a===null){a=e.nativeEvent;var l=new a.constructor(a.type,a);qa=l,a.target.dispatchEvent(l),qa=null}else return n=ur(a),n!==null&&ro(n),e.blockedOn=a,!1;n.shift()}return!0}function Ju(e,n,a){Qr(e)&&a.delete(n)}function zy(){io=!1,cn!==null&&Qr(cn)&&(cn=null),un!==null&&Qr(un)&&(un=null),dn!==null&&Qr(dn)&&(dn=null),qs.forEach(Ju),Xs.forEach(Ju)}function Qs(e,n){e.blockedOn===n&&(e.blockedOn=null,io||(io=!0,s.unstable_scheduleCallback(s.unstable_NormalPriority,zy)))}function Js(e){function n(u){return Qs(u,e)}if(0<Yr.length){Qs(Yr[0],e);for(var a=1;a<Yr.length;a++){var l=Yr[a];l.blockedOn===e&&(l.blockedOn=null)}}for(cn!==null&&Qs(cn,e),un!==null&&Qs(un,e),dn!==null&&Qs(dn,e),qs.forEach(n),Xs.forEach(n),a=0;a<hn.length;a++)l=hn[a],l.blockedOn===e&&(l.blockedOn=null);for(;0<hn.length&&(a=hn[0],a.blockedOn===null);)Qu(a),a.blockedOn===null&&hn.shift()}var ls=I.ReactCurrentBatchConfig,Jr=!0;function Uy(e,n,a,l){var u=be,m=ls.transition;ls.transition=null;try{be=1,ao(e,n,a,l)}finally{be=u,ls.transition=m}}function Wy(e,n,a,l){var u=be,m=ls.transition;ls.transition=null;try{be=4,ao(e,n,a,l)}finally{be=u,ls.transition=m}}function ao(e,n,a,l){if(Jr){var u=oo(e,n,a,l);if(u===null)No(e,n,l,Zr,a),Yu(e,l);else if(Oy(u,e,n,a,l))l.stopPropagation();else if(Yu(e,l),n&4&&-1<By.indexOf(e)){for(;u!==null;){var m=ur(u);if(m!==null&&Gu(m),m=oo(e,n,a,l),m===null&&No(e,n,l,Zr,a),m===u)break;u=m}u!==null&&l.stopPropagation()}else No(e,n,l,null,a)}}var Zr=null;function oo(e,n,a,l){if(Zr=null,e=Xa(l),e=Rn(e),e!==null)if(n=Dn(e),n===null)e=null;else if(a=n.tag,a===13){if(e=Iu(n),e!==null)return e;e=null}else if(a===3){if(n.stateNode.current.memoizedState.isDehydrated)return n.tag===3?n.stateNode.containerInfo:null;e=null}else n!==e&&(e=null);return Zr=e,null}function Zu(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(Ey()){case eo:return 1;case Uu:return 4;case Hr:case Ay:return 16;case Wu:return 536870912;default:return 16}default:return 16}}var mn=null,lo=null,ei=null;function ed(){if(ei)return ei;var e,n=lo,a=n.length,l,u="value"in mn?mn.value:mn.textContent,m=u.length;for(e=0;e<a&&n[e]===u[e];e++);var y=a-e;for(l=1;l<=y&&n[a-l]===u[m-l];l++);return ei=u.slice(e,1<l?1-l:void 0)}function ti(e){var n=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&n===13&&(e=13)):e=n,e===10&&(e=13),32<=e||e===13?e:0}function ni(){return!0}function td(){return!1}function vt(e){function n(a,l,u,m,y){this._reactName=a,this._targetInst=u,this.type=l,this.nativeEvent=m,this.target=y,this.currentTarget=null;for(var b in e)e.hasOwnProperty(b)&&(a=e[b],this[b]=a?a(m):m[b]);return this.isDefaultPrevented=(m.defaultPrevented!=null?m.defaultPrevented:m.returnValue===!1)?ni:td,this.isPropagationStopped=td,this}return K(n.prototype,{preventDefault:function(){this.defaultPrevented=!0;var a=this.nativeEvent;a&&(a.preventDefault?a.preventDefault():typeof a.returnValue!="unknown"&&(a.returnValue=!1),this.isDefaultPrevented=ni)},stopPropagation:function(){var a=this.nativeEvent;a&&(a.stopPropagation?a.stopPropagation():typeof a.cancelBubble!="unknown"&&(a.cancelBubble=!0),this.isPropagationStopped=ni)},persist:function(){},isPersistent:ni}),n}var cs={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},co=vt(cs),Zs=K({},cs,{view:0,detail:0}),$y=vt(Zs),uo,ho,er,si=K({},Zs,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:fo,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==er&&(er&&e.type==="mousemove"?(uo=e.screenX-er.screenX,ho=e.screenY-er.screenY):ho=uo=0,er=e),uo)},movementY:function(e){return"movementY"in e?e.movementY:ho}}),nd=vt(si),Hy=K({},si,{dataTransfer:0}),Gy=vt(Hy),Ky=K({},Zs,{relatedTarget:0}),mo=vt(Ky),qy=K({},cs,{animationName:0,elapsedTime:0,pseudoElement:0}),Xy=vt(qy),Yy=K({},cs,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),Qy=vt(Yy),Jy=K({},cs,{data:0}),sd=vt(Jy),Zy={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},ev={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},tv={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function nv(e){var n=this.nativeEvent;return n.getModifierState?n.getModifierState(e):(e=tv[e])?!!n[e]:!1}function fo(){return nv}var sv=K({},Zs,{key:function(e){if(e.key){var n=Zy[e.key]||e.key;if(n!=="Unidentified")return n}return e.type==="keypress"?(e=ti(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?ev[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:fo,charCode:function(e){return e.type==="keypress"?ti(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?ti(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),rv=vt(sv),iv=K({},si,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),rd=vt(iv),av=K({},Zs,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:fo}),ov=vt(av),lv=K({},cs,{propertyName:0,elapsedTime:0,pseudoElement:0}),cv=vt(lv),uv=K({},si,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),dv=vt(uv),hv=[9,13,27,32],po=f&&"CompositionEvent"in window,tr=null;f&&"documentMode"in document&&(tr=document.documentMode);var mv=f&&"TextEvent"in window&&!tr,id=f&&(!po||tr&&8<tr&&11>=tr),ad=" ",od=!1;function ld(e,n){switch(e){case"keyup":return hv.indexOf(n.keyCode)!==-1;case"keydown":return n.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function cd(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var us=!1;function fv(e,n){switch(e){case"compositionend":return cd(n);case"keypress":return n.which!==32?null:(od=!0,ad);case"textInput":return e=n.data,e===ad&&od?null:e;default:return null}}function pv(e,n){if(us)return e==="compositionend"||!po&&ld(e,n)?(e=ed(),ei=lo=mn=null,us=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(n.ctrlKey||n.altKey||n.metaKey)||n.ctrlKey&&n.altKey){if(n.char&&1<n.char.length)return n.char;if(n.which)return String.fromCharCode(n.which)}return null;case"compositionend":return id&&n.locale!=="ko"?null:n.data;default:return null}}var gv={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function ud(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n==="input"?!!gv[e.type]:n==="textarea"}function dd(e,n,a,l){Au(l),n=li(n,"onChange"),0<n.length&&(a=new co("onChange","change",null,a,l),e.push({event:a,listeners:n}))}var nr=null,sr=null;function yv(e){Md(e,0)}function ri(e){var n=ps(e);if(xu(n))return e}function vv(e,n){if(e==="change")return n}var hd=!1;if(f){var go;if(f){var yo="oninput"in document;if(!yo){var md=document.createElement("div");md.setAttribute("oninput","return;"),yo=typeof md.oninput=="function"}go=yo}else go=!1;hd=go&&(!document.documentMode||9<document.documentMode)}function fd(){nr&&(nr.detachEvent("onpropertychange",pd),sr=nr=null)}function pd(e){if(e.propertyName==="value"&&ri(sr)){var n=[];dd(n,sr,e,Xa(e)),Lu(yv,n)}}function xv(e,n,a){e==="focusin"?(fd(),nr=n,sr=a,nr.attachEvent("onpropertychange",pd)):e==="focusout"&&fd()}function wv(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return ri(sr)}function bv(e,n){if(e==="click")return ri(n)}function kv(e,n){if(e==="input"||e==="change")return ri(n)}function jv(e,n){return e===n&&(e!==0||1/e===1/n)||e!==e&&n!==n}var Dt=typeof Object.is=="function"?Object.is:jv;function rr(e,n){if(Dt(e,n))return!0;if(typeof e!="object"||e===null||typeof n!="object"||n===null)return!1;var a=Object.keys(e),l=Object.keys(n);if(a.length!==l.length)return!1;for(l=0;l<a.length;l++){var u=a[l];if(!p.call(n,u)||!Dt(e[u],n[u]))return!1}return!0}function gd(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function yd(e,n){var a=gd(e);e=0;for(var l;a;){if(a.nodeType===3){if(l=e+a.textContent.length,e<=n&&l>=n)return{node:a,offset:n-e};e=l}e:{for(;a;){if(a.nextSibling){a=a.nextSibling;break e}a=a.parentNode}a=void 0}a=gd(a)}}function vd(e,n){return e&&n?e===n?!0:e&&e.nodeType===3?!1:n&&n.nodeType===3?vd(e,n.parentNode):"contains"in e?e.contains(n):e.compareDocumentPosition?!!(e.compareDocumentPosition(n)&16):!1:!1}function xd(){for(var e=window,n=zr();n instanceof e.HTMLIFrameElement;){try{var a=typeof n.contentWindow.location.href=="string"}catch{a=!1}if(a)e=n.contentWindow;else break;n=zr(e.document)}return n}function vo(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n&&(n==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||n==="textarea"||e.contentEditable==="true")}function Sv(e){var n=xd(),a=e.focusedElem,l=e.selectionRange;if(n!==a&&a&&a.ownerDocument&&vd(a.ownerDocument.documentElement,a)){if(l!==null&&vo(a)){if(n=l.start,e=l.end,e===void 0&&(e=n),"selectionStart"in a)a.selectionStart=n,a.selectionEnd=Math.min(e,a.value.length);else if(e=(n=a.ownerDocument||document)&&n.defaultView||window,e.getSelection){e=e.getSelection();var u=a.textContent.length,m=Math.min(l.start,u);l=l.end===void 0?m:Math.min(l.end,u),!e.extend&&m>l&&(u=l,l=m,m=u),u=yd(a,m);var y=yd(a,l);u&&y&&(e.rangeCount!==1||e.anchorNode!==u.node||e.anchorOffset!==u.offset||e.focusNode!==y.node||e.focusOffset!==y.offset)&&(n=n.createRange(),n.setStart(u.node,u.offset),e.removeAllRanges(),m>l?(e.addRange(n),e.extend(y.node,y.offset)):(n.setEnd(y.node,y.offset),e.addRange(n)))}}for(n=[],e=a;e=e.parentNode;)e.nodeType===1&&n.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof a.focus=="function"&&a.focus(),a=0;a<n.length;a++)e=n[a],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var Nv=f&&"documentMode"in document&&11>=document.documentMode,ds=null,xo=null,ir=null,wo=!1;function wd(e,n,a){var l=a.window===a?a.document:a.nodeType===9?a:a.ownerDocument;wo||ds==null||ds!==zr(l)||(l=ds,"selectionStart"in l&&vo(l)?l={start:l.selectionStart,end:l.selectionEnd}:(l=(l.ownerDocument&&l.ownerDocument.defaultView||window).getSelection(),l={anchorNode:l.anchorNode,anchorOffset:l.anchorOffset,focusNode:l.focusNode,focusOffset:l.focusOffset}),ir&&rr(ir,l)||(ir=l,l=li(xo,"onSelect"),0<l.length&&(n=new co("onSelect","select",null,n,a),e.push({event:n,listeners:l}),n.target=ds)))}function ii(e,n){var a={};return a[e.toLowerCase()]=n.toLowerCase(),a["Webkit"+e]="webkit"+n,a["Moz"+e]="moz"+n,a}var hs={animationend:ii("Animation","AnimationEnd"),animationiteration:ii("Animation","AnimationIteration"),animationstart:ii("Animation","AnimationStart"),transitionend:ii("Transition","TransitionEnd")},bo={},bd={};f&&(bd=document.createElement("div").style,"AnimationEvent"in window||(delete hs.animationend.animation,delete hs.animationiteration.animation,delete hs.animationstart.animation),"TransitionEvent"in window||delete hs.transitionend.transition);function ai(e){if(bo[e])return bo[e];if(!hs[e])return e;var n=hs[e],a;for(a in n)if(n.hasOwnProperty(a)&&a in bd)return bo[e]=n[a];return e}var kd=ai("animationend"),jd=ai("animationiteration"),Sd=ai("animationstart"),Nd=ai("transitionend"),Cd=new Map,Td="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function fn(e,n){Cd.set(e,n),d(n,[e])}for(var ko=0;ko<Td.length;ko++){var jo=Td[ko],Cv=jo.toLowerCase(),Tv=jo[0].toUpperCase()+jo.slice(1);fn(Cv,"on"+Tv)}fn(kd,"onAnimationEnd"),fn(jd,"onAnimationIteration"),fn(Sd,"onAnimationStart"),fn("dblclick","onDoubleClick"),fn("focusin","onFocus"),fn("focusout","onBlur"),fn(Nd,"onTransitionEnd"),h("onMouseEnter",["mouseout","mouseover"]),h("onMouseLeave",["mouseout","mouseover"]),h("onPointerEnter",["pointerout","pointerover"]),h("onPointerLeave",["pointerout","pointerover"]),d("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),d("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),d("onBeforeInput",["compositionend","keypress","textInput","paste"]),d("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),d("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),d("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var ar="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),Pv=new Set("cancel close invalid load scroll toggle".split(" ").concat(ar));function Pd(e,n,a){var l=e.type||"unknown-event";e.currentTarget=a,Cy(l,n,void 0,e),e.currentTarget=null}function Md(e,n){n=(n&4)!==0;for(var a=0;a<e.length;a++){var l=e[a],u=l.event;l=l.listeners;e:{var m=void 0;if(n)for(var y=l.length-1;0<=y;y--){var b=l[y],C=b.instance,L=b.currentTarget;if(b=b.listener,C!==m&&u.isPropagationStopped())break e;Pd(u,b,L),m=C}else for(y=0;y<l.length;y++){if(b=l[y],C=b.instance,L=b.currentTarget,b=b.listener,C!==m&&u.isPropagationStopped())break e;Pd(u,b,L),m=C}}}if($r)throw e=Za,$r=!1,Za=null,e}function Ce(e,n){var a=n[Ao];a===void 0&&(a=n[Ao]=new Set);var l=e+"__bubble";a.has(l)||(Ed(n,e,2,!1),a.add(l))}function So(e,n,a){var l=0;n&&(l|=4),Ed(a,e,l,n)}var oi="_reactListening"+Math.random().toString(36).slice(2);function or(e){if(!e[oi]){e[oi]=!0,o.forEach(function(a){a!=="selectionchange"&&(Pv.has(a)||So(a,!1,e),So(a,!0,e))});var n=e.nodeType===9?e:e.ownerDocument;n===null||n[oi]||(n[oi]=!0,So("selectionchange",!1,n))}}function Ed(e,n,a,l){switch(Zu(n)){case 1:var u=Uy;break;case 4:u=Wy;break;default:u=ao}a=u.bind(null,n,a,e),u=void 0,!Ja||n!=="touchstart"&&n!=="touchmove"&&n!=="wheel"||(u=!0),l?u!==void 0?e.addEventListener(n,a,{capture:!0,passive:u}):e.addEventListener(n,a,!0):u!==void 0?e.addEventListener(n,a,{passive:u}):e.addEventListener(n,a,!1)}function No(e,n,a,l,u){var m=l;if((n&1)===0&&(n&2)===0&&l!==null)e:for(;;){if(l===null)return;var y=l.tag;if(y===3||y===4){var b=l.stateNode.containerInfo;if(b===u||b.nodeType===8&&b.parentNode===u)break;if(y===4)for(y=l.return;y!==null;){var C=y.tag;if((C===3||C===4)&&(C=y.stateNode.containerInfo,C===u||C.nodeType===8&&C.parentNode===u))return;y=y.return}for(;b!==null;){if(y=Rn(b),y===null)return;if(C=y.tag,C===5||C===6){l=m=y;continue e}b=b.parentNode}}l=l.return}Lu(function(){var L=m,$=Xa(a),H=[];e:{var W=Cd.get(e);if(W!==void 0){var X=co,Z=e;switch(e){case"keypress":if(ti(a)===0)break e;case"keydown":case"keyup":X=rv;break;case"focusin":Z="focus",X=mo;break;case"focusout":Z="blur",X=mo;break;case"beforeblur":case"afterblur":X=mo;break;case"click":if(a.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":X=nd;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":X=Gy;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":X=ov;break;case kd:case jd:case Sd:X=Xy;break;case Nd:X=cv;break;case"scroll":X=$y;break;case"wheel":X=dv;break;case"copy":case"cut":case"paste":X=Qy;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":X=rd}var te=(n&4)!==0,Fe=!te&&e==="scroll",A=te?W!==null?W+"Capture":null:W;te=[];for(var T=L,_;T!==null;){_=T;var G=_.stateNode;if(_.tag===5&&G!==null&&(_=G,A!==null&&(G=Ws(T,A),G!=null&&te.push(lr(T,G,_)))),Fe)break;T=T.return}0<te.length&&(W=new X(W,Z,null,a,$),H.push({event:W,listeners:te}))}}if((n&7)===0){e:{if(W=e==="mouseover"||e==="pointerover",X=e==="mouseout"||e==="pointerout",W&&a!==qa&&(Z=a.relatedTarget||a.fromElement)&&(Rn(Z)||Z[Jt]))break e;if((X||W)&&(W=$.window===$?$:(W=$.ownerDocument)?W.defaultView||W.parentWindow:window,X?(Z=a.relatedTarget||a.toElement,X=L,Z=Z?Rn(Z):null,Z!==null&&(Fe=Dn(Z),Z!==Fe||Z.tag!==5&&Z.tag!==6)&&(Z=null)):(X=null,Z=L),X!==Z)){if(te=nd,G="onMouseLeave",A="onMouseEnter",T="mouse",(e==="pointerout"||e==="pointerover")&&(te=rd,G="onPointerLeave",A="onPointerEnter",T="pointer"),Fe=X==null?W:ps(X),_=Z==null?W:ps(Z),W=new te(G,T+"leave",X,a,$),W.target=Fe,W.relatedTarget=_,G=null,Rn($)===L&&(te=new te(A,T+"enter",Z,a,$),te.target=_,te.relatedTarget=Fe,G=te),Fe=G,X&&Z)t:{for(te=X,A=Z,T=0,_=te;_;_=ms(_))T++;for(_=0,G=A;G;G=ms(G))_++;for(;0<T-_;)te=ms(te),T--;for(;0<_-T;)A=ms(A),_--;for(;T--;){if(te===A||A!==null&&te===A.alternate)break t;te=ms(te),A=ms(A)}te=null}else te=null;X!==null&&Ad(H,W,X,te,!1),Z!==null&&Fe!==null&&Ad(H,Fe,Z,te,!0)}}e:{if(W=L?ps(L):window,X=W.nodeName&&W.nodeName.toLowerCase(),X==="select"||X==="input"&&W.type==="file")var ne=vv;else if(ud(W))if(hd)ne=kv;else{ne=wv;var se=xv}else(X=W.nodeName)&&X.toLowerCase()==="input"&&(W.type==="checkbox"||W.type==="radio")&&(ne=bv);if(ne&&(ne=ne(e,L))){dd(H,ne,a,$);break e}se&&se(e,W,L),e==="focusout"&&(se=W._wrapperState)&&se.controlled&&W.type==="number"&&Wa(W,"number",W.value)}switch(se=L?ps(L):window,e){case"focusin":(ud(se)||se.contentEditable==="true")&&(ds=se,xo=L,ir=null);break;case"focusout":ir=xo=ds=null;break;case"mousedown":wo=!0;break;case"contextmenu":case"mouseup":case"dragend":wo=!1,wd(H,a,$);break;case"selectionchange":if(Nv)break;case"keydown":case"keyup":wd(H,a,$)}var re;if(po)e:{switch(e){case"compositionstart":var ae="onCompositionStart";break e;case"compositionend":ae="onCompositionEnd";break e;case"compositionupdate":ae="onCompositionUpdate";break e}ae=void 0}else us?ld(e,a)&&(ae="onCompositionEnd"):e==="keydown"&&a.keyCode===229&&(ae="onCompositionStart");ae&&(id&&a.locale!=="ko"&&(us||ae!=="onCompositionStart"?ae==="onCompositionEnd"&&us&&(re=ed()):(mn=$,lo="value"in mn?mn.value:mn.textContent,us=!0)),se=li(L,ae),0<se.length&&(ae=new sd(ae,e,null,a,$),H.push({event:ae,listeners:se}),re?ae.data=re:(re=cd(a),re!==null&&(ae.data=re)))),(re=mv?fv(e,a):pv(e,a))&&(L=li(L,"onBeforeInput"),0<L.length&&($=new sd("onBeforeInput","beforeinput",null,a,$),H.push({event:$,listeners:L}),$.data=re))}Md(H,n)})}function lr(e,n,a){return{instance:e,listener:n,currentTarget:a}}function li(e,n){for(var a=n+"Capture",l=[];e!==null;){var u=e,m=u.stateNode;u.tag===5&&m!==null&&(u=m,m=Ws(e,a),m!=null&&l.unshift(lr(e,m,u)),m=Ws(e,n),m!=null&&l.push(lr(e,m,u))),e=e.return}return l}function ms(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function Ad(e,n,a,l,u){for(var m=n._reactName,y=[];a!==null&&a!==l;){var b=a,C=b.alternate,L=b.stateNode;if(C!==null&&C===l)break;b.tag===5&&L!==null&&(b=L,u?(C=Ws(a,m),C!=null&&y.unshift(lr(a,C,b))):u||(C=Ws(a,m),C!=null&&y.push(lr(a,C,b)))),a=a.return}y.length!==0&&e.push({event:n,listeners:y})}var Mv=/\r\n?/g,Ev=/\u0000|\uFFFD/g;function _d(e){return(typeof e=="string"?e:""+e).replace(Mv,`
`).replace(Ev,"")}function ci(e,n,a){if(n=_d(n),_d(e)!==n&&a)throw Error(i(425))}function ui(){}var Co=null,To=null;function Po(e,n){return e==="textarea"||e==="noscript"||typeof n.children=="string"||typeof n.children=="number"||typeof n.dangerouslySetInnerHTML=="object"&&n.dangerouslySetInnerHTML!==null&&n.dangerouslySetInnerHTML.__html!=null}var Mo=typeof setTimeout=="function"?setTimeout:void 0,Av=typeof clearTimeout=="function"?clearTimeout:void 0,Dd=typeof Promise=="function"?Promise:void 0,_v=typeof queueMicrotask=="function"?queueMicrotask:typeof Dd<"u"?function(e){return Dd.resolve(null).then(e).catch(Dv)}:Mo;function Dv(e){setTimeout(function(){throw e})}function Eo(e,n){var a=n,l=0;do{var u=a.nextSibling;if(e.removeChild(a),u&&u.nodeType===8)if(a=u.data,a==="/$"){if(l===0){e.removeChild(u),Js(n);return}l--}else a!=="$"&&a!=="$?"&&a!=="$!"||l++;a=u}while(a);Js(n)}function pn(e){for(;e!=null;e=e.nextSibling){var n=e.nodeType;if(n===1||n===3)break;if(n===8){if(n=e.data,n==="$"||n==="$!"||n==="$?")break;if(n==="/$")return null}}return e}function Rd(e){e=e.previousSibling;for(var n=0;e;){if(e.nodeType===8){var a=e.data;if(a==="$"||a==="$!"||a==="$?"){if(n===0)return e;n--}else a==="/$"&&n++}e=e.previousSibling}return null}var fs=Math.random().toString(36).slice(2),$t="__reactFiber$"+fs,cr="__reactProps$"+fs,Jt="__reactContainer$"+fs,Ao="__reactEvents$"+fs,Rv="__reactListeners$"+fs,Lv="__reactHandles$"+fs;function Rn(e){var n=e[$t];if(n)return n;for(var a=e.parentNode;a;){if(n=a[Jt]||a[$t]){if(a=n.alternate,n.child!==null||a!==null&&a.child!==null)for(e=Rd(e);e!==null;){if(a=e[$t])return a;e=Rd(e)}return n}e=a,a=e.parentNode}return null}function ur(e){return e=e[$t]||e[Jt],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function ps(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(i(33))}function di(e){return e[cr]||null}var _o=[],gs=-1;function gn(e){return{current:e}}function Te(e){0>gs||(e.current=_o[gs],_o[gs]=null,gs--)}function Ne(e,n){gs++,_o[gs]=e.current,e.current=n}var yn={},tt=gn(yn),ut=gn(!1),Ln=yn;function ys(e,n){var a=e.type.contextTypes;if(!a)return yn;var l=e.stateNode;if(l&&l.__reactInternalMemoizedUnmaskedChildContext===n)return l.__reactInternalMemoizedMaskedChildContext;var u={},m;for(m in a)u[m]=n[m];return l&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=n,e.__reactInternalMemoizedMaskedChildContext=u),u}function dt(e){return e=e.childContextTypes,e!=null}function hi(){Te(ut),Te(tt)}function Ld(e,n,a){if(tt.current!==yn)throw Error(i(168));Ne(tt,n),Ne(ut,a)}function Id(e,n,a){var l=e.stateNode;if(n=n.childContextTypes,typeof l.getChildContext!="function")return a;l=l.getChildContext();for(var u in l)if(!(u in n))throw Error(i(108,Se(e)||"Unknown",u));return K({},a,l)}function mi(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||yn,Ln=tt.current,Ne(tt,e),Ne(ut,ut.current),!0}function Vd(e,n,a){var l=e.stateNode;if(!l)throw Error(i(169));a?(e=Id(e,n,Ln),l.__reactInternalMemoizedMergedChildContext=e,Te(ut),Te(tt),Ne(tt,e)):Te(ut),Ne(ut,a)}var Zt=null,fi=!1,Do=!1;function Fd(e){Zt===null?Zt=[e]:Zt.push(e)}function Iv(e){fi=!0,Fd(e)}function vn(){if(!Do&&Zt!==null){Do=!0;var e=0,n=be;try{var a=Zt;for(be=1;e<a.length;e++){var l=a[e];do l=l(!0);while(l!==null)}Zt=null,fi=!1}catch(u){throw Zt!==null&&(Zt=Zt.slice(e+1)),Ou(eo,vn),u}finally{be=n,Do=!1}}return null}var vs=[],xs=0,pi=null,gi=0,Nt=[],Ct=0,In=null,en=1,tn="";function Vn(e,n){vs[xs++]=gi,vs[xs++]=pi,pi=e,gi=n}function Bd(e,n,a){Nt[Ct++]=en,Nt[Ct++]=tn,Nt[Ct++]=In,In=e;var l=en;e=tn;var u=32-_t(l)-1;l&=~(1<<u),a+=1;var m=32-_t(n)+u;if(30<m){var y=u-u%5;m=(l&(1<<y)-1).toString(32),l>>=y,u-=y,en=1<<32-_t(n)+u|a<<u|l,tn=m+e}else en=1<<m|a<<u|l,tn=e}function Ro(e){e.return!==null&&(Vn(e,1),Bd(e,1,0))}function Lo(e){for(;e===pi;)pi=vs[--xs],vs[xs]=null,gi=vs[--xs],vs[xs]=null;for(;e===In;)In=Nt[--Ct],Nt[Ct]=null,tn=Nt[--Ct],Nt[Ct]=null,en=Nt[--Ct],Nt[Ct]=null}var xt=null,wt=null,Ee=!1,Rt=null;function Od(e,n){var a=Et(5,null,null,0);a.elementType="DELETED",a.stateNode=n,a.return=e,n=e.deletions,n===null?(e.deletions=[a],e.flags|=16):n.push(a)}function zd(e,n){switch(e.tag){case 5:var a=e.type;return n=n.nodeType!==1||a.toLowerCase()!==n.nodeName.toLowerCase()?null:n,n!==null?(e.stateNode=n,xt=e,wt=pn(n.firstChild),!0):!1;case 6:return n=e.pendingProps===""||n.nodeType!==3?null:n,n!==null?(e.stateNode=n,xt=e,wt=null,!0):!1;case 13:return n=n.nodeType!==8?null:n,n!==null?(a=In!==null?{id:en,overflow:tn}:null,e.memoizedState={dehydrated:n,treeContext:a,retryLane:1073741824},a=Et(18,null,null,0),a.stateNode=n,a.return=e,e.child=a,xt=e,wt=null,!0):!1;default:return!1}}function Io(e){return(e.mode&1)!==0&&(e.flags&128)===0}function Vo(e){if(Ee){var n=wt;if(n){var a=n;if(!zd(e,n)){if(Io(e))throw Error(i(418));n=pn(a.nextSibling);var l=xt;n&&zd(e,n)?Od(l,a):(e.flags=e.flags&-4097|2,Ee=!1,xt=e)}}else{if(Io(e))throw Error(i(418));e.flags=e.flags&-4097|2,Ee=!1,xt=e}}}function Ud(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;xt=e}function yi(e){if(e!==xt)return!1;if(!Ee)return Ud(e),Ee=!0,!1;var n;if((n=e.tag!==3)&&!(n=e.tag!==5)&&(n=e.type,n=n!=="head"&&n!=="body"&&!Po(e.type,e.memoizedProps)),n&&(n=wt)){if(Io(e))throw Wd(),Error(i(418));for(;n;)Od(e,n),n=pn(n.nextSibling)}if(Ud(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(i(317));e:{for(e=e.nextSibling,n=0;e;){if(e.nodeType===8){var a=e.data;if(a==="/$"){if(n===0){wt=pn(e.nextSibling);break e}n--}else a!=="$"&&a!=="$!"&&a!=="$?"||n++}e=e.nextSibling}wt=null}}else wt=xt?pn(e.stateNode.nextSibling):null;return!0}function Wd(){for(var e=wt;e;)e=pn(e.nextSibling)}function ws(){wt=xt=null,Ee=!1}function Fo(e){Rt===null?Rt=[e]:Rt.push(e)}var Vv=I.ReactCurrentBatchConfig;function dr(e,n,a){if(e=a.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(a._owner){if(a=a._owner,a){if(a.tag!==1)throw Error(i(309));var l=a.stateNode}if(!l)throw Error(i(147,e));var u=l,m=""+e;return n!==null&&n.ref!==null&&typeof n.ref=="function"&&n.ref._stringRef===m?n.ref:(n=function(y){var b=u.refs;y===null?delete b[m]:b[m]=y},n._stringRef=m,n)}if(typeof e!="string")throw Error(i(284));if(!a._owner)throw Error(i(290,e))}return e}function vi(e,n){throw e=Object.prototype.toString.call(n),Error(i(31,e==="[object Object]"?"object with keys {"+Object.keys(n).join(", ")+"}":e))}function $d(e){var n=e._init;return n(e._payload)}function Hd(e){function n(A,T){if(e){var _=A.deletions;_===null?(A.deletions=[T],A.flags|=16):_.push(T)}}function a(A,T){if(!e)return null;for(;T!==null;)n(A,T),T=T.sibling;return null}function l(A,T){for(A=new Map;T!==null;)T.key!==null?A.set(T.key,T):A.set(T.index,T),T=T.sibling;return A}function u(A,T){return A=Cn(A,T),A.index=0,A.sibling=null,A}function m(A,T,_){return A.index=_,e?(_=A.alternate,_!==null?(_=_.index,_<T?(A.flags|=2,T):_):(A.flags|=2,T)):(A.flags|=1048576,T)}function y(A){return e&&A.alternate===null&&(A.flags|=2),A}function b(A,T,_,G){return T===null||T.tag!==6?(T=Ml(_,A.mode,G),T.return=A,T):(T=u(T,_),T.return=A,T)}function C(A,T,_,G){var ne=_.type;return ne===V?$(A,T,_.props.children,G,_.key):T!==null&&(T.elementType===ne||typeof ne=="object"&&ne!==null&&ne.$$typeof===Ae&&$d(ne)===T.type)?(G=u(T,_.props),G.ref=dr(A,T,_),G.return=A,G):(G=Ui(_.type,_.key,_.props,null,A.mode,G),G.ref=dr(A,T,_),G.return=A,G)}function L(A,T,_,G){return T===null||T.tag!==4||T.stateNode.containerInfo!==_.containerInfo||T.stateNode.implementation!==_.implementation?(T=El(_,A.mode,G),T.return=A,T):(T=u(T,_.children||[]),T.return=A,T)}function $(A,T,_,G,ne){return T===null||T.tag!==7?(T=Hn(_,A.mode,G,ne),T.return=A,T):(T=u(T,_),T.return=A,T)}function H(A,T,_){if(typeof T=="string"&&T!==""||typeof T=="number")return T=Ml(""+T,A.mode,_),T.return=A,T;if(typeof T=="object"&&T!==null){switch(T.$$typeof){case D:return _=Ui(T.type,T.key,T.props,null,A.mode,_),_.ref=dr(A,null,T),_.return=A,_;case F:return T=El(T,A.mode,_),T.return=A,T;case Ae:var G=T._init;return H(A,G(T._payload),_)}if(Os(T)||q(T))return T=Hn(T,A.mode,_,null),T.return=A,T;vi(A,T)}return null}function W(A,T,_,G){var ne=T!==null?T.key:null;if(typeof _=="string"&&_!==""||typeof _=="number")return ne!==null?null:b(A,T,""+_,G);if(typeof _=="object"&&_!==null){switch(_.$$typeof){case D:return _.key===ne?C(A,T,_,G):null;case F:return _.key===ne?L(A,T,_,G):null;case Ae:return ne=_._init,W(A,T,ne(_._payload),G)}if(Os(_)||q(_))return ne!==null?null:$(A,T,_,G,null);vi(A,_)}return null}function X(A,T,_,G,ne){if(typeof G=="string"&&G!==""||typeof G=="number")return A=A.get(_)||null,b(T,A,""+G,ne);if(typeof G=="object"&&G!==null){switch(G.$$typeof){case D:return A=A.get(G.key===null?_:G.key)||null,C(T,A,G,ne);case F:return A=A.get(G.key===null?_:G.key)||null,L(T,A,G,ne);case Ae:var se=G._init;return X(A,T,_,se(G._payload),ne)}if(Os(G)||q(G))return A=A.get(_)||null,$(T,A,G,ne,null);vi(T,G)}return null}function Z(A,T,_,G){for(var ne=null,se=null,re=T,ae=T=0,Qe=null;re!==null&&ae<_.length;ae++){re.index>ae?(Qe=re,re=null):Qe=re.sibling;var ge=W(A,re,_[ae],G);if(ge===null){re===null&&(re=Qe);break}e&&re&&ge.alternate===null&&n(A,re),T=m(ge,T,ae),se===null?ne=ge:se.sibling=ge,se=ge,re=Qe}if(ae===_.length)return a(A,re),Ee&&Vn(A,ae),ne;if(re===null){for(;ae<_.length;ae++)re=H(A,_[ae],G),re!==null&&(T=m(re,T,ae),se===null?ne=re:se.sibling=re,se=re);return Ee&&Vn(A,ae),ne}for(re=l(A,re);ae<_.length;ae++)Qe=X(re,A,ae,_[ae],G),Qe!==null&&(e&&Qe.alternate!==null&&re.delete(Qe.key===null?ae:Qe.key),T=m(Qe,T,ae),se===null?ne=Qe:se.sibling=Qe,se=Qe);return e&&re.forEach(function(Tn){return n(A,Tn)}),Ee&&Vn(A,ae),ne}function te(A,T,_,G){var ne=q(_);if(typeof ne!="function")throw Error(i(150));if(_=ne.call(_),_==null)throw Error(i(151));for(var se=ne=null,re=T,ae=T=0,Qe=null,ge=_.next();re!==null&&!ge.done;ae++,ge=_.next()){re.index>ae?(Qe=re,re=null):Qe=re.sibling;var Tn=W(A,re,ge.value,G);if(Tn===null){re===null&&(re=Qe);break}e&&re&&Tn.alternate===null&&n(A,re),T=m(Tn,T,ae),se===null?ne=Tn:se.sibling=Tn,se=Tn,re=Qe}if(ge.done)return a(A,re),Ee&&Vn(A,ae),ne;if(re===null){for(;!ge.done;ae++,ge=_.next())ge=H(A,ge.value,G),ge!==null&&(T=m(ge,T,ae),se===null?ne=ge:se.sibling=ge,se=ge);return Ee&&Vn(A,ae),ne}for(re=l(A,re);!ge.done;ae++,ge=_.next())ge=X(re,A,ae,ge.value,G),ge!==null&&(e&&ge.alternate!==null&&re.delete(ge.key===null?ae:ge.key),T=m(ge,T,ae),se===null?ne=ge:se.sibling=ge,se=ge);return e&&re.forEach(function(gx){return n(A,gx)}),Ee&&Vn(A,ae),ne}function Fe(A,T,_,G){if(typeof _=="object"&&_!==null&&_.type===V&&_.key===null&&(_=_.props.children),typeof _=="object"&&_!==null){switch(_.$$typeof){case D:e:{for(var ne=_.key,se=T;se!==null;){if(se.key===ne){if(ne=_.type,ne===V){if(se.tag===7){a(A,se.sibling),T=u(se,_.props.children),T.return=A,A=T;break e}}else if(se.elementType===ne||typeof ne=="object"&&ne!==null&&ne.$$typeof===Ae&&$d(ne)===se.type){a(A,se.sibling),T=u(se,_.props),T.ref=dr(A,se,_),T.return=A,A=T;break e}a(A,se);break}else n(A,se);se=se.sibling}_.type===V?(T=Hn(_.props.children,A.mode,G,_.key),T.return=A,A=T):(G=Ui(_.type,_.key,_.props,null,A.mode,G),G.ref=dr(A,T,_),G.return=A,A=G)}return y(A);case F:e:{for(se=_.key;T!==null;){if(T.key===se)if(T.tag===4&&T.stateNode.containerInfo===_.containerInfo&&T.stateNode.implementation===_.implementation){a(A,T.sibling),T=u(T,_.children||[]),T.return=A,A=T;break e}else{a(A,T);break}else n(A,T);T=T.sibling}T=El(_,A.mode,G),T.return=A,A=T}return y(A);case Ae:return se=_._init,Fe(A,T,se(_._payload),G)}if(Os(_))return Z(A,T,_,G);if(q(_))return te(A,T,_,G);vi(A,_)}return typeof _=="string"&&_!==""||typeof _=="number"?(_=""+_,T!==null&&T.tag===6?(a(A,T.sibling),T=u(T,_),T.return=A,A=T):(a(A,T),T=Ml(_,A.mode,G),T.return=A,A=T),y(A)):a(A,T)}return Fe}var bs=Hd(!0),Gd=Hd(!1),xi=gn(null),wi=null,ks=null,Bo=null;function Oo(){Bo=ks=wi=null}function zo(e){var n=xi.current;Te(xi),e._currentValue=n}function Uo(e,n,a){for(;e!==null;){var l=e.alternate;if((e.childLanes&n)!==n?(e.childLanes|=n,l!==null&&(l.childLanes|=n)):l!==null&&(l.childLanes&n)!==n&&(l.childLanes|=n),e===a)break;e=e.return}}function js(e,n){wi=e,Bo=ks=null,e=e.dependencies,e!==null&&e.firstContext!==null&&((e.lanes&n)!==0&&(ht=!0),e.firstContext=null)}function Tt(e){var n=e._currentValue;if(Bo!==e)if(e={context:e,memoizedValue:n,next:null},ks===null){if(wi===null)throw Error(i(308));ks=e,wi.dependencies={lanes:0,firstContext:e}}else ks=ks.next=e;return n}var Fn=null;function Wo(e){Fn===null?Fn=[e]:Fn.push(e)}function Kd(e,n,a,l){var u=n.interleaved;return u===null?(a.next=a,Wo(n)):(a.next=u.next,u.next=a),n.interleaved=a,nn(e,l)}function nn(e,n){e.lanes|=n;var a=e.alternate;for(a!==null&&(a.lanes|=n),a=e,e=e.return;e!==null;)e.childLanes|=n,a=e.alternate,a!==null&&(a.childLanes|=n),a=e,e=e.return;return a.tag===3?a.stateNode:null}var xn=!1;function $o(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function qd(e,n){e=e.updateQueue,n.updateQueue===e&&(n.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function sn(e,n){return{eventTime:e,lane:n,tag:0,payload:null,callback:null,next:null}}function wn(e,n,a){var l=e.updateQueue;if(l===null)return null;if(l=l.shared,(me&2)!==0){var u=l.pending;return u===null?n.next=n:(n.next=u.next,u.next=n),l.pending=n,nn(e,a)}return u=l.interleaved,u===null?(n.next=n,Wo(l)):(n.next=u.next,u.next=n),l.interleaved=n,nn(e,a)}function bi(e,n,a){if(n=n.updateQueue,n!==null&&(n=n.shared,(a&4194240)!==0)){var l=n.lanes;l&=e.pendingLanes,a|=l,n.lanes=a,so(e,a)}}function Xd(e,n){var a=e.updateQueue,l=e.alternate;if(l!==null&&(l=l.updateQueue,a===l)){var u=null,m=null;if(a=a.firstBaseUpdate,a!==null){do{var y={eventTime:a.eventTime,lane:a.lane,tag:a.tag,payload:a.payload,callback:a.callback,next:null};m===null?u=m=y:m=m.next=y,a=a.next}while(a!==null);m===null?u=m=n:m=m.next=n}else u=m=n;a={baseState:l.baseState,firstBaseUpdate:u,lastBaseUpdate:m,shared:l.shared,effects:l.effects},e.updateQueue=a;return}e=a.lastBaseUpdate,e===null?a.firstBaseUpdate=n:e.next=n,a.lastBaseUpdate=n}function ki(e,n,a,l){var u=e.updateQueue;xn=!1;var m=u.firstBaseUpdate,y=u.lastBaseUpdate,b=u.shared.pending;if(b!==null){u.shared.pending=null;var C=b,L=C.next;C.next=null,y===null?m=L:y.next=L,y=C;var $=e.alternate;$!==null&&($=$.updateQueue,b=$.lastBaseUpdate,b!==y&&(b===null?$.firstBaseUpdate=L:b.next=L,$.lastBaseUpdate=C))}if(m!==null){var H=u.baseState;y=0,$=L=C=null,b=m;do{var W=b.lane,X=b.eventTime;if((l&W)===W){$!==null&&($=$.next={eventTime:X,lane:0,tag:b.tag,payload:b.payload,callback:b.callback,next:null});e:{var Z=e,te=b;switch(W=n,X=a,te.tag){case 1:if(Z=te.payload,typeof Z=="function"){H=Z.call(X,H,W);break e}H=Z;break e;case 3:Z.flags=Z.flags&-65537|128;case 0:if(Z=te.payload,W=typeof Z=="function"?Z.call(X,H,W):Z,W==null)break e;H=K({},H,W);break e;case 2:xn=!0}}b.callback!==null&&b.lane!==0&&(e.flags|=64,W=u.effects,W===null?u.effects=[b]:W.push(b))}else X={eventTime:X,lane:W,tag:b.tag,payload:b.payload,callback:b.callback,next:null},$===null?(L=$=X,C=H):$=$.next=X,y|=W;if(b=b.next,b===null){if(b=u.shared.pending,b===null)break;W=b,b=W.next,W.next=null,u.lastBaseUpdate=W,u.shared.pending=null}}while(!0);if($===null&&(C=H),u.baseState=C,u.firstBaseUpdate=L,u.lastBaseUpdate=$,n=u.shared.interleaved,n!==null){u=n;do y|=u.lane,u=u.next;while(u!==n)}else m===null&&(u.shared.lanes=0);zn|=y,e.lanes=y,e.memoizedState=H}}function Yd(e,n,a){if(e=n.effects,n.effects=null,e!==null)for(n=0;n<e.length;n++){var l=e[n],u=l.callback;if(u!==null){if(l.callback=null,l=a,typeof u!="function")throw Error(i(191,u));u.call(l)}}}var hr={},Ht=gn(hr),mr=gn(hr),fr=gn(hr);function Bn(e){if(e===hr)throw Error(i(174));return e}function Ho(e,n){switch(Ne(fr,n),Ne(mr,e),Ne(Ht,hr),e=n.nodeType,e){case 9:case 11:n=(n=n.documentElement)?n.namespaceURI:Ha(null,"");break;default:e=e===8?n.parentNode:n,n=e.namespaceURI||null,e=e.tagName,n=Ha(n,e)}Te(Ht),Ne(Ht,n)}function Ss(){Te(Ht),Te(mr),Te(fr)}function Qd(e){Bn(fr.current);var n=Bn(Ht.current),a=Ha(n,e.type);n!==a&&(Ne(mr,e),Ne(Ht,a))}function Go(e){mr.current===e&&(Te(Ht),Te(mr))}var _e=gn(0);function ji(e){for(var n=e;n!==null;){if(n.tag===13){var a=n.memoizedState;if(a!==null&&(a=a.dehydrated,a===null||a.data==="$?"||a.data==="$!"))return n}else if(n.tag===19&&n.memoizedProps.revealOrder!==void 0){if((n.flags&128)!==0)return n}else if(n.child!==null){n.child.return=n,n=n.child;continue}if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return null;n=n.return}n.sibling.return=n.return,n=n.sibling}return null}var Ko=[];function qo(){for(var e=0;e<Ko.length;e++)Ko[e]._workInProgressVersionPrimary=null;Ko.length=0}var Si=I.ReactCurrentDispatcher,Xo=I.ReactCurrentBatchConfig,On=0,De=null,We=null,Xe=null,Ni=!1,pr=!1,gr=0,Fv=0;function nt(){throw Error(i(321))}function Yo(e,n){if(n===null)return!1;for(var a=0;a<n.length&&a<e.length;a++)if(!Dt(e[a],n[a]))return!1;return!0}function Qo(e,n,a,l,u,m){if(On=m,De=n,n.memoizedState=null,n.updateQueue=null,n.lanes=0,Si.current=e===null||e.memoizedState===null?Uv:Wv,e=a(l,u),pr){m=0;do{if(pr=!1,gr=0,25<=m)throw Error(i(301));m+=1,Xe=We=null,n.updateQueue=null,Si.current=$v,e=a(l,u)}while(pr)}if(Si.current=Pi,n=We!==null&&We.next!==null,On=0,Xe=We=De=null,Ni=!1,n)throw Error(i(300));return e}function Jo(){var e=gr!==0;return gr=0,e}function Gt(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return Xe===null?De.memoizedState=Xe=e:Xe=Xe.next=e,Xe}function Pt(){if(We===null){var e=De.alternate;e=e!==null?e.memoizedState:null}else e=We.next;var n=Xe===null?De.memoizedState:Xe.next;if(n!==null)Xe=n,We=e;else{if(e===null)throw Error(i(310));We=e,e={memoizedState:We.memoizedState,baseState:We.baseState,baseQueue:We.baseQueue,queue:We.queue,next:null},Xe===null?De.memoizedState=Xe=e:Xe=Xe.next=e}return Xe}function yr(e,n){return typeof n=="function"?n(e):n}function Zo(e){var n=Pt(),a=n.queue;if(a===null)throw Error(i(311));a.lastRenderedReducer=e;var l=We,u=l.baseQueue,m=a.pending;if(m!==null){if(u!==null){var y=u.next;u.next=m.next,m.next=y}l.baseQueue=u=m,a.pending=null}if(u!==null){m=u.next,l=l.baseState;var b=y=null,C=null,L=m;do{var $=L.lane;if((On&$)===$)C!==null&&(C=C.next={lane:0,action:L.action,hasEagerState:L.hasEagerState,eagerState:L.eagerState,next:null}),l=L.hasEagerState?L.eagerState:e(l,L.action);else{var H={lane:$,action:L.action,hasEagerState:L.hasEagerState,eagerState:L.eagerState,next:null};C===null?(b=C=H,y=l):C=C.next=H,De.lanes|=$,zn|=$}L=L.next}while(L!==null&&L!==m);C===null?y=l:C.next=b,Dt(l,n.memoizedState)||(ht=!0),n.memoizedState=l,n.baseState=y,n.baseQueue=C,a.lastRenderedState=l}if(e=a.interleaved,e!==null){u=e;do m=u.lane,De.lanes|=m,zn|=m,u=u.next;while(u!==e)}else u===null&&(a.lanes=0);return[n.memoizedState,a.dispatch]}function el(e){var n=Pt(),a=n.queue;if(a===null)throw Error(i(311));a.lastRenderedReducer=e;var l=a.dispatch,u=a.pending,m=n.memoizedState;if(u!==null){a.pending=null;var y=u=u.next;do m=e(m,y.action),y=y.next;while(y!==u);Dt(m,n.memoizedState)||(ht=!0),n.memoizedState=m,n.baseQueue===null&&(n.baseState=m),a.lastRenderedState=m}return[m,l]}function Jd(){}function Zd(e,n){var a=De,l=Pt(),u=n(),m=!Dt(l.memoizedState,u);if(m&&(l.memoizedState=u,ht=!0),l=l.queue,tl(nh.bind(null,a,l,e),[e]),l.getSnapshot!==n||m||Xe!==null&&Xe.memoizedState.tag&1){if(a.flags|=2048,vr(9,th.bind(null,a,l,u,n),void 0,null),Ye===null)throw Error(i(349));(On&30)!==0||eh(a,n,u)}return u}function eh(e,n,a){e.flags|=16384,e={getSnapshot:n,value:a},n=De.updateQueue,n===null?(n={lastEffect:null,stores:null},De.updateQueue=n,n.stores=[e]):(a=n.stores,a===null?n.stores=[e]:a.push(e))}function th(e,n,a,l){n.value=a,n.getSnapshot=l,sh(n)&&rh(e)}function nh(e,n,a){return a(function(){sh(n)&&rh(e)})}function sh(e){var n=e.getSnapshot;e=e.value;try{var a=n();return!Dt(e,a)}catch{return!0}}function rh(e){var n=nn(e,1);n!==null&&Ft(n,e,1,-1)}function ih(e){var n=Gt();return typeof e=="function"&&(e=e()),n.memoizedState=n.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:yr,lastRenderedState:e},n.queue=e,e=e.dispatch=zv.bind(null,De,e),[n.memoizedState,e]}function vr(e,n,a,l){return e={tag:e,create:n,destroy:a,deps:l,next:null},n=De.updateQueue,n===null?(n={lastEffect:null,stores:null},De.updateQueue=n,n.lastEffect=e.next=e):(a=n.lastEffect,a===null?n.lastEffect=e.next=e:(l=a.next,a.next=e,e.next=l,n.lastEffect=e)),e}function ah(){return Pt().memoizedState}function Ci(e,n,a,l){var u=Gt();De.flags|=e,u.memoizedState=vr(1|n,a,void 0,l===void 0?null:l)}function Ti(e,n,a,l){var u=Pt();l=l===void 0?null:l;var m=void 0;if(We!==null){var y=We.memoizedState;if(m=y.destroy,l!==null&&Yo(l,y.deps)){u.memoizedState=vr(n,a,m,l);return}}De.flags|=e,u.memoizedState=vr(1|n,a,m,l)}function oh(e,n){return Ci(8390656,8,e,n)}function tl(e,n){return Ti(2048,8,e,n)}function lh(e,n){return Ti(4,2,e,n)}function ch(e,n){return Ti(4,4,e,n)}function uh(e,n){if(typeof n=="function")return e=e(),n(e),function(){n(null)};if(n!=null)return e=e(),n.current=e,function(){n.current=null}}function dh(e,n,a){return a=a!=null?a.concat([e]):null,Ti(4,4,uh.bind(null,n,e),a)}function nl(){}function hh(e,n){var a=Pt();n=n===void 0?null:n;var l=a.memoizedState;return l!==null&&n!==null&&Yo(n,l[1])?l[0]:(a.memoizedState=[e,n],e)}function mh(e,n){var a=Pt();n=n===void 0?null:n;var l=a.memoizedState;return l!==null&&n!==null&&Yo(n,l[1])?l[0]:(e=e(),a.memoizedState=[e,n],e)}function fh(e,n,a){return(On&21)===0?(e.baseState&&(e.baseState=!1,ht=!0),e.memoizedState=a):(Dt(a,n)||(a=$u(),De.lanes|=a,zn|=a,e.baseState=!0),n)}function Bv(e,n){var a=be;be=a!==0&&4>a?a:4,e(!0);var l=Xo.transition;Xo.transition={};try{e(!1),n()}finally{be=a,Xo.transition=l}}function ph(){return Pt().memoizedState}function Ov(e,n,a){var l=Sn(e);if(a={lane:l,action:a,hasEagerState:!1,eagerState:null,next:null},gh(e))yh(n,a);else if(a=Kd(e,n,a,l),a!==null){var u=ot();Ft(a,e,l,u),vh(a,n,l)}}function zv(e,n,a){var l=Sn(e),u={lane:l,action:a,hasEagerState:!1,eagerState:null,next:null};if(gh(e))yh(n,u);else{var m=e.alternate;if(e.lanes===0&&(m===null||m.lanes===0)&&(m=n.lastRenderedReducer,m!==null))try{var y=n.lastRenderedState,b=m(y,a);if(u.hasEagerState=!0,u.eagerState=b,Dt(b,y)){var C=n.interleaved;C===null?(u.next=u,Wo(n)):(u.next=C.next,C.next=u),n.interleaved=u;return}}catch{}finally{}a=Kd(e,n,u,l),a!==null&&(u=ot(),Ft(a,e,l,u),vh(a,n,l))}}function gh(e){var n=e.alternate;return e===De||n!==null&&n===De}function yh(e,n){pr=Ni=!0;var a=e.pending;a===null?n.next=n:(n.next=a.next,a.next=n),e.pending=n}function vh(e,n,a){if((a&4194240)!==0){var l=n.lanes;l&=e.pendingLanes,a|=l,n.lanes=a,so(e,a)}}var Pi={readContext:Tt,useCallback:nt,useContext:nt,useEffect:nt,useImperativeHandle:nt,useInsertionEffect:nt,useLayoutEffect:nt,useMemo:nt,useReducer:nt,useRef:nt,useState:nt,useDebugValue:nt,useDeferredValue:nt,useTransition:nt,useMutableSource:nt,useSyncExternalStore:nt,useId:nt,unstable_isNewReconciler:!1},Uv={readContext:Tt,useCallback:function(e,n){return Gt().memoizedState=[e,n===void 0?null:n],e},useContext:Tt,useEffect:oh,useImperativeHandle:function(e,n,a){return a=a!=null?a.concat([e]):null,Ci(4194308,4,uh.bind(null,n,e),a)},useLayoutEffect:function(e,n){return Ci(4194308,4,e,n)},useInsertionEffect:function(e,n){return Ci(4,2,e,n)},useMemo:function(e,n){var a=Gt();return n=n===void 0?null:n,e=e(),a.memoizedState=[e,n],e},useReducer:function(e,n,a){var l=Gt();return n=a!==void 0?a(n):n,l.memoizedState=l.baseState=n,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:n},l.queue=e,e=e.dispatch=Ov.bind(null,De,e),[l.memoizedState,e]},useRef:function(e){var n=Gt();return e={current:e},n.memoizedState=e},useState:ih,useDebugValue:nl,useDeferredValue:function(e){return Gt().memoizedState=e},useTransition:function(){var e=ih(!1),n=e[0];return e=Bv.bind(null,e[1]),Gt().memoizedState=e,[n,e]},useMutableSource:function(){},useSyncExternalStore:function(e,n,a){var l=De,u=Gt();if(Ee){if(a===void 0)throw Error(i(407));a=a()}else{if(a=n(),Ye===null)throw Error(i(349));(On&30)!==0||eh(l,n,a)}u.memoizedState=a;var m={value:a,getSnapshot:n};return u.queue=m,oh(nh.bind(null,l,m,e),[e]),l.flags|=2048,vr(9,th.bind(null,l,m,a,n),void 0,null),a},useId:function(){var e=Gt(),n=Ye.identifierPrefix;if(Ee){var a=tn,l=en;a=(l&~(1<<32-_t(l)-1)).toString(32)+a,n=":"+n+"R"+a,a=gr++,0<a&&(n+="H"+a.toString(32)),n+=":"}else a=Fv++,n=":"+n+"r"+a.toString(32)+":";return e.memoizedState=n},unstable_isNewReconciler:!1},Wv={readContext:Tt,useCallback:hh,useContext:Tt,useEffect:tl,useImperativeHandle:dh,useInsertionEffect:lh,useLayoutEffect:ch,useMemo:mh,useReducer:Zo,useRef:ah,useState:function(){return Zo(yr)},useDebugValue:nl,useDeferredValue:function(e){var n=Pt();return fh(n,We.memoizedState,e)},useTransition:function(){var e=Zo(yr)[0],n=Pt().memoizedState;return[e,n]},useMutableSource:Jd,useSyncExternalStore:Zd,useId:ph,unstable_isNewReconciler:!1},$v={readContext:Tt,useCallback:hh,useContext:Tt,useEffect:tl,useImperativeHandle:dh,useInsertionEffect:lh,useLayoutEffect:ch,useMemo:mh,useReducer:el,useRef:ah,useState:function(){return el(yr)},useDebugValue:nl,useDeferredValue:function(e){var n=Pt();return We===null?n.memoizedState=e:fh(n,We.memoizedState,e)},useTransition:function(){var e=el(yr)[0],n=Pt().memoizedState;return[e,n]},useMutableSource:Jd,useSyncExternalStore:Zd,useId:ph,unstable_isNewReconciler:!1};function Lt(e,n){if(e&&e.defaultProps){n=K({},n),e=e.defaultProps;for(var a in e)n[a]===void 0&&(n[a]=e[a]);return n}return n}function sl(e,n,a,l){n=e.memoizedState,a=a(l,n),a=a==null?n:K({},n,a),e.memoizedState=a,e.lanes===0&&(e.updateQueue.baseState=a)}var Mi={isMounted:function(e){return(e=e._reactInternals)?Dn(e)===e:!1},enqueueSetState:function(e,n,a){e=e._reactInternals;var l=ot(),u=Sn(e),m=sn(l,u);m.payload=n,a!=null&&(m.callback=a),n=wn(e,m,u),n!==null&&(Ft(n,e,u,l),bi(n,e,u))},enqueueReplaceState:function(e,n,a){e=e._reactInternals;var l=ot(),u=Sn(e),m=sn(l,u);m.tag=1,m.payload=n,a!=null&&(m.callback=a),n=wn(e,m,u),n!==null&&(Ft(n,e,u,l),bi(n,e,u))},enqueueForceUpdate:function(e,n){e=e._reactInternals;var a=ot(),l=Sn(e),u=sn(a,l);u.tag=2,n!=null&&(u.callback=n),n=wn(e,u,l),n!==null&&(Ft(n,e,l,a),bi(n,e,l))}};function xh(e,n,a,l,u,m,y){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(l,m,y):n.prototype&&n.prototype.isPureReactComponent?!rr(a,l)||!rr(u,m):!0}function wh(e,n,a){var l=!1,u=yn,m=n.contextType;return typeof m=="object"&&m!==null?m=Tt(m):(u=dt(n)?Ln:tt.current,l=n.contextTypes,m=(l=l!=null)?ys(e,u):yn),n=new n(a,m),e.memoizedState=n.state!==null&&n.state!==void 0?n.state:null,n.updater=Mi,e.stateNode=n,n._reactInternals=e,l&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=u,e.__reactInternalMemoizedMaskedChildContext=m),n}function bh(e,n,a,l){e=n.state,typeof n.componentWillReceiveProps=="function"&&n.componentWillReceiveProps(a,l),typeof n.UNSAFE_componentWillReceiveProps=="function"&&n.UNSAFE_componentWillReceiveProps(a,l),n.state!==e&&Mi.enqueueReplaceState(n,n.state,null)}function rl(e,n,a,l){var u=e.stateNode;u.props=a,u.state=e.memoizedState,u.refs={},$o(e);var m=n.contextType;typeof m=="object"&&m!==null?u.context=Tt(m):(m=dt(n)?Ln:tt.current,u.context=ys(e,m)),u.state=e.memoizedState,m=n.getDerivedStateFromProps,typeof m=="function"&&(sl(e,n,m,a),u.state=e.memoizedState),typeof n.getDerivedStateFromProps=="function"||typeof u.getSnapshotBeforeUpdate=="function"||typeof u.UNSAFE_componentWillMount!="function"&&typeof u.componentWillMount!="function"||(n=u.state,typeof u.componentWillMount=="function"&&u.componentWillMount(),typeof u.UNSAFE_componentWillMount=="function"&&u.UNSAFE_componentWillMount(),n!==u.state&&Mi.enqueueReplaceState(u,u.state,null),ki(e,a,u,l),u.state=e.memoizedState),typeof u.componentDidMount=="function"&&(e.flags|=4194308)}function Ns(e,n){try{var a="",l=n;do a+=fe(l),l=l.return;while(l);var u=a}catch(m){u=`
Error generating stack: `+m.message+`
`+m.stack}return{value:e,source:n,stack:u,digest:null}}function il(e,n,a){return{value:e,source:null,stack:a??null,digest:n??null}}function al(e,n){try{console.error(n.value)}catch(a){setTimeout(function(){throw a})}}var Hv=typeof WeakMap=="function"?WeakMap:Map;function kh(e,n,a){a=sn(-1,a),a.tag=3,a.payload={element:null};var l=n.value;return a.callback=function(){Ii||(Ii=!0,bl=l),al(e,n)},a}function jh(e,n,a){a=sn(-1,a),a.tag=3;var l=e.type.getDerivedStateFromError;if(typeof l=="function"){var u=n.value;a.payload=function(){return l(u)},a.callback=function(){al(e,n)}}var m=e.stateNode;return m!==null&&typeof m.componentDidCatch=="function"&&(a.callback=function(){al(e,n),typeof l!="function"&&(kn===null?kn=new Set([this]):kn.add(this));var y=n.stack;this.componentDidCatch(n.value,{componentStack:y!==null?y:""})}),a}function Sh(e,n,a){var l=e.pingCache;if(l===null){l=e.pingCache=new Hv;var u=new Set;l.set(n,u)}else u=l.get(n),u===void 0&&(u=new Set,l.set(n,u));u.has(a)||(u.add(a),e=ix.bind(null,e,n,a),n.then(e,e))}function Nh(e){do{var n;if((n=e.tag===13)&&(n=e.memoizedState,n=n!==null?n.dehydrated!==null:!0),n)return e;e=e.return}while(e!==null);return null}function Ch(e,n,a,l,u){return(e.mode&1)===0?(e===n?e.flags|=65536:(e.flags|=128,a.flags|=131072,a.flags&=-52805,a.tag===1&&(a.alternate===null?a.tag=17:(n=sn(-1,1),n.tag=2,wn(a,n,1))),a.lanes|=1),e):(e.flags|=65536,e.lanes=u,e)}var Gv=I.ReactCurrentOwner,ht=!1;function at(e,n,a,l){n.child=e===null?Gd(n,null,a,l):bs(n,e.child,a,l)}function Th(e,n,a,l,u){a=a.render;var m=n.ref;return js(n,u),l=Qo(e,n,a,l,m,u),a=Jo(),e!==null&&!ht?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~u,rn(e,n,u)):(Ee&&a&&Ro(n),n.flags|=1,at(e,n,l,u),n.child)}function Ph(e,n,a,l,u){if(e===null){var m=a.type;return typeof m=="function"&&!Pl(m)&&m.defaultProps===void 0&&a.compare===null&&a.defaultProps===void 0?(n.tag=15,n.type=m,Mh(e,n,m,l,u)):(e=Ui(a.type,null,l,n,n.mode,u),e.ref=n.ref,e.return=n,n.child=e)}if(m=e.child,(e.lanes&u)===0){var y=m.memoizedProps;if(a=a.compare,a=a!==null?a:rr,a(y,l)&&e.ref===n.ref)return rn(e,n,u)}return n.flags|=1,e=Cn(m,l),e.ref=n.ref,e.return=n,n.child=e}function Mh(e,n,a,l,u){if(e!==null){var m=e.memoizedProps;if(rr(m,l)&&e.ref===n.ref)if(ht=!1,n.pendingProps=l=m,(e.lanes&u)!==0)(e.flags&131072)!==0&&(ht=!0);else return n.lanes=e.lanes,rn(e,n,u)}return ol(e,n,a,l,u)}function Eh(e,n,a){var l=n.pendingProps,u=l.children,m=e!==null?e.memoizedState:null;if(l.mode==="hidden")if((n.mode&1)===0)n.memoizedState={baseLanes:0,cachePool:null,transitions:null},Ne(Ts,bt),bt|=a;else{if((a&1073741824)===0)return e=m!==null?m.baseLanes|a:a,n.lanes=n.childLanes=1073741824,n.memoizedState={baseLanes:e,cachePool:null,transitions:null},n.updateQueue=null,Ne(Ts,bt),bt|=e,null;n.memoizedState={baseLanes:0,cachePool:null,transitions:null},l=m!==null?m.baseLanes:a,Ne(Ts,bt),bt|=l}else m!==null?(l=m.baseLanes|a,n.memoizedState=null):l=a,Ne(Ts,bt),bt|=l;return at(e,n,u,a),n.child}function Ah(e,n){var a=n.ref;(e===null&&a!==null||e!==null&&e.ref!==a)&&(n.flags|=512,n.flags|=2097152)}function ol(e,n,a,l,u){var m=dt(a)?Ln:tt.current;return m=ys(n,m),js(n,u),a=Qo(e,n,a,l,m,u),l=Jo(),e!==null&&!ht?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~u,rn(e,n,u)):(Ee&&l&&Ro(n),n.flags|=1,at(e,n,a,u),n.child)}function _h(e,n,a,l,u){if(dt(a)){var m=!0;mi(n)}else m=!1;if(js(n,u),n.stateNode===null)Ai(e,n),wh(n,a,l),rl(n,a,l,u),l=!0;else if(e===null){var y=n.stateNode,b=n.memoizedProps;y.props=b;var C=y.context,L=a.contextType;typeof L=="object"&&L!==null?L=Tt(L):(L=dt(a)?Ln:tt.current,L=ys(n,L));var $=a.getDerivedStateFromProps,H=typeof $=="function"||typeof y.getSnapshotBeforeUpdate=="function";H||typeof y.UNSAFE_componentWillReceiveProps!="function"&&typeof y.componentWillReceiveProps!="function"||(b!==l||C!==L)&&bh(n,y,l,L),xn=!1;var W=n.memoizedState;y.state=W,ki(n,l,y,u),C=n.memoizedState,b!==l||W!==C||ut.current||xn?(typeof $=="function"&&(sl(n,a,$,l),C=n.memoizedState),(b=xn||xh(n,a,b,l,W,C,L))?(H||typeof y.UNSAFE_componentWillMount!="function"&&typeof y.componentWillMount!="function"||(typeof y.componentWillMount=="function"&&y.componentWillMount(),typeof y.UNSAFE_componentWillMount=="function"&&y.UNSAFE_componentWillMount()),typeof y.componentDidMount=="function"&&(n.flags|=4194308)):(typeof y.componentDidMount=="function"&&(n.flags|=4194308),n.memoizedProps=l,n.memoizedState=C),y.props=l,y.state=C,y.context=L,l=b):(typeof y.componentDidMount=="function"&&(n.flags|=4194308),l=!1)}else{y=n.stateNode,qd(e,n),b=n.memoizedProps,L=n.type===n.elementType?b:Lt(n.type,b),y.props=L,H=n.pendingProps,W=y.context,C=a.contextType,typeof C=="object"&&C!==null?C=Tt(C):(C=dt(a)?Ln:tt.current,C=ys(n,C));var X=a.getDerivedStateFromProps;($=typeof X=="function"||typeof y.getSnapshotBeforeUpdate=="function")||typeof y.UNSAFE_componentWillReceiveProps!="function"&&typeof y.componentWillReceiveProps!="function"||(b!==H||W!==C)&&bh(n,y,l,C),xn=!1,W=n.memoizedState,y.state=W,ki(n,l,y,u);var Z=n.memoizedState;b!==H||W!==Z||ut.current||xn?(typeof X=="function"&&(sl(n,a,X,l),Z=n.memoizedState),(L=xn||xh(n,a,L,l,W,Z,C)||!1)?($||typeof y.UNSAFE_componentWillUpdate!="function"&&typeof y.componentWillUpdate!="function"||(typeof y.componentWillUpdate=="function"&&y.componentWillUpdate(l,Z,C),typeof y.UNSAFE_componentWillUpdate=="function"&&y.UNSAFE_componentWillUpdate(l,Z,C)),typeof y.componentDidUpdate=="function"&&(n.flags|=4),typeof y.getSnapshotBeforeUpdate=="function"&&(n.flags|=1024)):(typeof y.componentDidUpdate!="function"||b===e.memoizedProps&&W===e.memoizedState||(n.flags|=4),typeof y.getSnapshotBeforeUpdate!="function"||b===e.memoizedProps&&W===e.memoizedState||(n.flags|=1024),n.memoizedProps=l,n.memoizedState=Z),y.props=l,y.state=Z,y.context=C,l=L):(typeof y.componentDidUpdate!="function"||b===e.memoizedProps&&W===e.memoizedState||(n.flags|=4),typeof y.getSnapshotBeforeUpdate!="function"||b===e.memoizedProps&&W===e.memoizedState||(n.flags|=1024),l=!1)}return ll(e,n,a,l,m,u)}function ll(e,n,a,l,u,m){Ah(e,n);var y=(n.flags&128)!==0;if(!l&&!y)return u&&Vd(n,a,!1),rn(e,n,m);l=n.stateNode,Gv.current=n;var b=y&&typeof a.getDerivedStateFromError!="function"?null:l.render();return n.flags|=1,e!==null&&y?(n.child=bs(n,e.child,null,m),n.child=bs(n,null,b,m)):at(e,n,b,m),n.memoizedState=l.state,u&&Vd(n,a,!0),n.child}function Dh(e){var n=e.stateNode;n.pendingContext?Ld(e,n.pendingContext,n.pendingContext!==n.context):n.context&&Ld(e,n.context,!1),Ho(e,n.containerInfo)}function Rh(e,n,a,l,u){return ws(),Fo(u),n.flags|=256,at(e,n,a,l),n.child}var cl={dehydrated:null,treeContext:null,retryLane:0};function ul(e){return{baseLanes:e,cachePool:null,transitions:null}}function Lh(e,n,a){var l=n.pendingProps,u=_e.current,m=!1,y=(n.flags&128)!==0,b;if((b=y)||(b=e!==null&&e.memoizedState===null?!1:(u&2)!==0),b?(m=!0,n.flags&=-129):(e===null||e.memoizedState!==null)&&(u|=1),Ne(_e,u&1),e===null)return Vo(n),e=n.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?((n.mode&1)===0?n.lanes=1:e.data==="$!"?n.lanes=8:n.lanes=1073741824,null):(y=l.children,e=l.fallback,m?(l=n.mode,m=n.child,y={mode:"hidden",children:y},(l&1)===0&&m!==null?(m.childLanes=0,m.pendingProps=y):m=Wi(y,l,0,null),e=Hn(e,l,a,null),m.return=n,e.return=n,m.sibling=e,n.child=m,n.child.memoizedState=ul(a),n.memoizedState=cl,e):dl(n,y));if(u=e.memoizedState,u!==null&&(b=u.dehydrated,b!==null))return Kv(e,n,y,l,b,u,a);if(m){m=l.fallback,y=n.mode,u=e.child,b=u.sibling;var C={mode:"hidden",children:l.children};return(y&1)===0&&n.child!==u?(l=n.child,l.childLanes=0,l.pendingProps=C,n.deletions=null):(l=Cn(u,C),l.subtreeFlags=u.subtreeFlags&14680064),b!==null?m=Cn(b,m):(m=Hn(m,y,a,null),m.flags|=2),m.return=n,l.return=n,l.sibling=m,n.child=l,l=m,m=n.child,y=e.child.memoizedState,y=y===null?ul(a):{baseLanes:y.baseLanes|a,cachePool:null,transitions:y.transitions},m.memoizedState=y,m.childLanes=e.childLanes&~a,n.memoizedState=cl,l}return m=e.child,e=m.sibling,l=Cn(m,{mode:"visible",children:l.children}),(n.mode&1)===0&&(l.lanes=a),l.return=n,l.sibling=null,e!==null&&(a=n.deletions,a===null?(n.deletions=[e],n.flags|=16):a.push(e)),n.child=l,n.memoizedState=null,l}function dl(e,n){return n=Wi({mode:"visible",children:n},e.mode,0,null),n.return=e,e.child=n}function Ei(e,n,a,l){return l!==null&&Fo(l),bs(n,e.child,null,a),e=dl(n,n.pendingProps.children),e.flags|=2,n.memoizedState=null,e}function Kv(e,n,a,l,u,m,y){if(a)return n.flags&256?(n.flags&=-257,l=il(Error(i(422))),Ei(e,n,y,l)):n.memoizedState!==null?(n.child=e.child,n.flags|=128,null):(m=l.fallback,u=n.mode,l=Wi({mode:"visible",children:l.children},u,0,null),m=Hn(m,u,y,null),m.flags|=2,l.return=n,m.return=n,l.sibling=m,n.child=l,(n.mode&1)!==0&&bs(n,e.child,null,y),n.child.memoizedState=ul(y),n.memoizedState=cl,m);if((n.mode&1)===0)return Ei(e,n,y,null);if(u.data==="$!"){if(l=u.nextSibling&&u.nextSibling.dataset,l)var b=l.dgst;return l=b,m=Error(i(419)),l=il(m,l,void 0),Ei(e,n,y,l)}if(b=(y&e.childLanes)!==0,ht||b){if(l=Ye,l!==null){switch(y&-y){case 4:u=2;break;case 16:u=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:u=32;break;case 536870912:u=268435456;break;default:u=0}u=(u&(l.suspendedLanes|y))!==0?0:u,u!==0&&u!==m.retryLane&&(m.retryLane=u,nn(e,u),Ft(l,e,u,-1))}return Tl(),l=il(Error(i(421))),Ei(e,n,y,l)}return u.data==="$?"?(n.flags|=128,n.child=e.child,n=ax.bind(null,e),u._reactRetry=n,null):(e=m.treeContext,wt=pn(u.nextSibling),xt=n,Ee=!0,Rt=null,e!==null&&(Nt[Ct++]=en,Nt[Ct++]=tn,Nt[Ct++]=In,en=e.id,tn=e.overflow,In=n),n=dl(n,l.children),n.flags|=4096,n)}function Ih(e,n,a){e.lanes|=n;var l=e.alternate;l!==null&&(l.lanes|=n),Uo(e.return,n,a)}function hl(e,n,a,l,u){var m=e.memoizedState;m===null?e.memoizedState={isBackwards:n,rendering:null,renderingStartTime:0,last:l,tail:a,tailMode:u}:(m.isBackwards=n,m.rendering=null,m.renderingStartTime=0,m.last=l,m.tail=a,m.tailMode=u)}function Vh(e,n,a){var l=n.pendingProps,u=l.revealOrder,m=l.tail;if(at(e,n,l.children,a),l=_e.current,(l&2)!==0)l=l&1|2,n.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=n.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Ih(e,a,n);else if(e.tag===19)Ih(e,a,n);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===n)break e;for(;e.sibling===null;){if(e.return===null||e.return===n)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}l&=1}if(Ne(_e,l),(n.mode&1)===0)n.memoizedState=null;else switch(u){case"forwards":for(a=n.child,u=null;a!==null;)e=a.alternate,e!==null&&ji(e)===null&&(u=a),a=a.sibling;a=u,a===null?(u=n.child,n.child=null):(u=a.sibling,a.sibling=null),hl(n,!1,u,a,m);break;case"backwards":for(a=null,u=n.child,n.child=null;u!==null;){if(e=u.alternate,e!==null&&ji(e)===null){n.child=u;break}e=u.sibling,u.sibling=a,a=u,u=e}hl(n,!0,a,null,m);break;case"together":hl(n,!1,null,null,void 0);break;default:n.memoizedState=null}return n.child}function Ai(e,n){(n.mode&1)===0&&e!==null&&(e.alternate=null,n.alternate=null,n.flags|=2)}function rn(e,n,a){if(e!==null&&(n.dependencies=e.dependencies),zn|=n.lanes,(a&n.childLanes)===0)return null;if(e!==null&&n.child!==e.child)throw Error(i(153));if(n.child!==null){for(e=n.child,a=Cn(e,e.pendingProps),n.child=a,a.return=n;e.sibling!==null;)e=e.sibling,a=a.sibling=Cn(e,e.pendingProps),a.return=n;a.sibling=null}return n.child}function qv(e,n,a){switch(n.tag){case 3:Dh(n),ws();break;case 5:Qd(n);break;case 1:dt(n.type)&&mi(n);break;case 4:Ho(n,n.stateNode.containerInfo);break;case 10:var l=n.type._context,u=n.memoizedProps.value;Ne(xi,l._currentValue),l._currentValue=u;break;case 13:if(l=n.memoizedState,l!==null)return l.dehydrated!==null?(Ne(_e,_e.current&1),n.flags|=128,null):(a&n.child.childLanes)!==0?Lh(e,n,a):(Ne(_e,_e.current&1),e=rn(e,n,a),e!==null?e.sibling:null);Ne(_e,_e.current&1);break;case 19:if(l=(a&n.childLanes)!==0,(e.flags&128)!==0){if(l)return Vh(e,n,a);n.flags|=128}if(u=n.memoizedState,u!==null&&(u.rendering=null,u.tail=null,u.lastEffect=null),Ne(_e,_e.current),l)break;return null;case 22:case 23:return n.lanes=0,Eh(e,n,a)}return rn(e,n,a)}var Fh,ml,Bh,Oh;Fh=function(e,n){for(var a=n.child;a!==null;){if(a.tag===5||a.tag===6)e.appendChild(a.stateNode);else if(a.tag!==4&&a.child!==null){a.child.return=a,a=a.child;continue}if(a===n)break;for(;a.sibling===null;){if(a.return===null||a.return===n)return;a=a.return}a.sibling.return=a.return,a=a.sibling}},ml=function(){},Bh=function(e,n,a,l){var u=e.memoizedProps;if(u!==l){e=n.stateNode,Bn(Ht.current);var m=null;switch(a){case"input":u=za(e,u),l=za(e,l),m=[];break;case"select":u=K({},u,{value:void 0}),l=K({},l,{value:void 0}),m=[];break;case"textarea":u=$a(e,u),l=$a(e,l),m=[];break;default:typeof u.onClick!="function"&&typeof l.onClick=="function"&&(e.onclick=ui)}Ga(a,l);var y;a=null;for(L in u)if(!l.hasOwnProperty(L)&&u.hasOwnProperty(L)&&u[L]!=null)if(L==="style"){var b=u[L];for(y in b)b.hasOwnProperty(y)&&(a||(a={}),a[y]="")}else L!=="dangerouslySetInnerHTML"&&L!=="children"&&L!=="suppressContentEditableWarning"&&L!=="suppressHydrationWarning"&&L!=="autoFocus"&&(c.hasOwnProperty(L)?m||(m=[]):(m=m||[]).push(L,null));for(L in l){var C=l[L];if(b=u!=null?u[L]:void 0,l.hasOwnProperty(L)&&C!==b&&(C!=null||b!=null))if(L==="style")if(b){for(y in b)!b.hasOwnProperty(y)||C&&C.hasOwnProperty(y)||(a||(a={}),a[y]="");for(y in C)C.hasOwnProperty(y)&&b[y]!==C[y]&&(a||(a={}),a[y]=C[y])}else a||(m||(m=[]),m.push(L,a)),a=C;else L==="dangerouslySetInnerHTML"?(C=C?C.__html:void 0,b=b?b.__html:void 0,C!=null&&b!==C&&(m=m||[]).push(L,C)):L==="children"?typeof C!="string"&&typeof C!="number"||(m=m||[]).push(L,""+C):L!=="suppressContentEditableWarning"&&L!=="suppressHydrationWarning"&&(c.hasOwnProperty(L)?(C!=null&&L==="onScroll"&&Ce("scroll",e),m||b===C||(m=[])):(m=m||[]).push(L,C))}a&&(m=m||[]).push("style",a);var L=m;(n.updateQueue=L)&&(n.flags|=4)}},Oh=function(e,n,a,l){a!==l&&(n.flags|=4)};function xr(e,n){if(!Ee)switch(e.tailMode){case"hidden":n=e.tail;for(var a=null;n!==null;)n.alternate!==null&&(a=n),n=n.sibling;a===null?e.tail=null:a.sibling=null;break;case"collapsed":a=e.tail;for(var l=null;a!==null;)a.alternate!==null&&(l=a),a=a.sibling;l===null?n||e.tail===null?e.tail=null:e.tail.sibling=null:l.sibling=null}}function st(e){var n=e.alternate!==null&&e.alternate.child===e.child,a=0,l=0;if(n)for(var u=e.child;u!==null;)a|=u.lanes|u.childLanes,l|=u.subtreeFlags&14680064,l|=u.flags&14680064,u.return=e,u=u.sibling;else for(u=e.child;u!==null;)a|=u.lanes|u.childLanes,l|=u.subtreeFlags,l|=u.flags,u.return=e,u=u.sibling;return e.subtreeFlags|=l,e.childLanes=a,n}function Xv(e,n,a){var l=n.pendingProps;switch(Lo(n),n.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return st(n),null;case 1:return dt(n.type)&&hi(),st(n),null;case 3:return l=n.stateNode,Ss(),Te(ut),Te(tt),qo(),l.pendingContext&&(l.context=l.pendingContext,l.pendingContext=null),(e===null||e.child===null)&&(yi(n)?n.flags|=4:e===null||e.memoizedState.isDehydrated&&(n.flags&256)===0||(n.flags|=1024,Rt!==null&&(Sl(Rt),Rt=null))),ml(e,n),st(n),null;case 5:Go(n);var u=Bn(fr.current);if(a=n.type,e!==null&&n.stateNode!=null)Bh(e,n,a,l,u),e.ref!==n.ref&&(n.flags|=512,n.flags|=2097152);else{if(!l){if(n.stateNode===null)throw Error(i(166));return st(n),null}if(e=Bn(Ht.current),yi(n)){l=n.stateNode,a=n.type;var m=n.memoizedProps;switch(l[$t]=n,l[cr]=m,e=(n.mode&1)!==0,a){case"dialog":Ce("cancel",l),Ce("close",l);break;case"iframe":case"object":case"embed":Ce("load",l);break;case"video":case"audio":for(u=0;u<ar.length;u++)Ce(ar[u],l);break;case"source":Ce("error",l);break;case"img":case"image":case"link":Ce("error",l),Ce("load",l);break;case"details":Ce("toggle",l);break;case"input":wu(l,m),Ce("invalid",l);break;case"select":l._wrapperState={wasMultiple:!!m.multiple},Ce("invalid",l);break;case"textarea":ju(l,m),Ce("invalid",l)}Ga(a,m),u=null;for(var y in m)if(m.hasOwnProperty(y)){var b=m[y];y==="children"?typeof b=="string"?l.textContent!==b&&(m.suppressHydrationWarning!==!0&&ci(l.textContent,b,e),u=["children",b]):typeof b=="number"&&l.textContent!==""+b&&(m.suppressHydrationWarning!==!0&&ci(l.textContent,b,e),u=["children",""+b]):c.hasOwnProperty(y)&&b!=null&&y==="onScroll"&&Ce("scroll",l)}switch(a){case"input":Or(l),ku(l,m,!0);break;case"textarea":Or(l),Nu(l);break;case"select":case"option":break;default:typeof m.onClick=="function"&&(l.onclick=ui)}l=u,n.updateQueue=l,l!==null&&(n.flags|=4)}else{y=u.nodeType===9?u:u.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=Cu(a)),e==="http://www.w3.org/1999/xhtml"?a==="script"?(e=y.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof l.is=="string"?e=y.createElement(a,{is:l.is}):(e=y.createElement(a),a==="select"&&(y=e,l.multiple?y.multiple=!0:l.size&&(y.size=l.size))):e=y.createElementNS(e,a),e[$t]=n,e[cr]=l,Fh(e,n,!1,!1),n.stateNode=e;e:{switch(y=Ka(a,l),a){case"dialog":Ce("cancel",e),Ce("close",e),u=l;break;case"iframe":case"object":case"embed":Ce("load",e),u=l;break;case"video":case"audio":for(u=0;u<ar.length;u++)Ce(ar[u],e);u=l;break;case"source":Ce("error",e),u=l;break;case"img":case"image":case"link":Ce("error",e),Ce("load",e),u=l;break;case"details":Ce("toggle",e),u=l;break;case"input":wu(e,l),u=za(e,l),Ce("invalid",e);break;case"option":u=l;break;case"select":e._wrapperState={wasMultiple:!!l.multiple},u=K({},l,{value:void 0}),Ce("invalid",e);break;case"textarea":ju(e,l),u=$a(e,l),Ce("invalid",e);break;default:u=l}Ga(a,u),b=u;for(m in b)if(b.hasOwnProperty(m)){var C=b[m];m==="style"?Mu(e,C):m==="dangerouslySetInnerHTML"?(C=C?C.__html:void 0,C!=null&&Tu(e,C)):m==="children"?typeof C=="string"?(a!=="textarea"||C!=="")&&zs(e,C):typeof C=="number"&&zs(e,""+C):m!=="suppressContentEditableWarning"&&m!=="suppressHydrationWarning"&&m!=="autoFocus"&&(c.hasOwnProperty(m)?C!=null&&m==="onScroll"&&Ce("scroll",e):C!=null&&R(e,m,C,y))}switch(a){case"input":Or(e),ku(e,l,!1);break;case"textarea":Or(e),Nu(e);break;case"option":l.value!=null&&e.setAttribute("value",""+we(l.value));break;case"select":e.multiple=!!l.multiple,m=l.value,m!=null?is(e,!!l.multiple,m,!1):l.defaultValue!=null&&is(e,!!l.multiple,l.defaultValue,!0);break;default:typeof u.onClick=="function"&&(e.onclick=ui)}switch(a){case"button":case"input":case"select":case"textarea":l=!!l.autoFocus;break e;case"img":l=!0;break e;default:l=!1}}l&&(n.flags|=4)}n.ref!==null&&(n.flags|=512,n.flags|=2097152)}return st(n),null;case 6:if(e&&n.stateNode!=null)Oh(e,n,e.memoizedProps,l);else{if(typeof l!="string"&&n.stateNode===null)throw Error(i(166));if(a=Bn(fr.current),Bn(Ht.current),yi(n)){if(l=n.stateNode,a=n.memoizedProps,l[$t]=n,(m=l.nodeValue!==a)&&(e=xt,e!==null))switch(e.tag){case 3:ci(l.nodeValue,a,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&ci(l.nodeValue,a,(e.mode&1)!==0)}m&&(n.flags|=4)}else l=(a.nodeType===9?a:a.ownerDocument).createTextNode(l),l[$t]=n,n.stateNode=l}return st(n),null;case 13:if(Te(_e),l=n.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(Ee&&wt!==null&&(n.mode&1)!==0&&(n.flags&128)===0)Wd(),ws(),n.flags|=98560,m=!1;else if(m=yi(n),l!==null&&l.dehydrated!==null){if(e===null){if(!m)throw Error(i(318));if(m=n.memoizedState,m=m!==null?m.dehydrated:null,!m)throw Error(i(317));m[$t]=n}else ws(),(n.flags&128)===0&&(n.memoizedState=null),n.flags|=4;st(n),m=!1}else Rt!==null&&(Sl(Rt),Rt=null),m=!0;if(!m)return n.flags&65536?n:null}return(n.flags&128)!==0?(n.lanes=a,n):(l=l!==null,l!==(e!==null&&e.memoizedState!==null)&&l&&(n.child.flags|=8192,(n.mode&1)!==0&&(e===null||(_e.current&1)!==0?$e===0&&($e=3):Tl())),n.updateQueue!==null&&(n.flags|=4),st(n),null);case 4:return Ss(),ml(e,n),e===null&&or(n.stateNode.containerInfo),st(n),null;case 10:return zo(n.type._context),st(n),null;case 17:return dt(n.type)&&hi(),st(n),null;case 19:if(Te(_e),m=n.memoizedState,m===null)return st(n),null;if(l=(n.flags&128)!==0,y=m.rendering,y===null)if(l)xr(m,!1);else{if($e!==0||e!==null&&(e.flags&128)!==0)for(e=n.child;e!==null;){if(y=ji(e),y!==null){for(n.flags|=128,xr(m,!1),l=y.updateQueue,l!==null&&(n.updateQueue=l,n.flags|=4),n.subtreeFlags=0,l=a,a=n.child;a!==null;)m=a,e=l,m.flags&=14680066,y=m.alternate,y===null?(m.childLanes=0,m.lanes=e,m.child=null,m.subtreeFlags=0,m.memoizedProps=null,m.memoizedState=null,m.updateQueue=null,m.dependencies=null,m.stateNode=null):(m.childLanes=y.childLanes,m.lanes=y.lanes,m.child=y.child,m.subtreeFlags=0,m.deletions=null,m.memoizedProps=y.memoizedProps,m.memoizedState=y.memoizedState,m.updateQueue=y.updateQueue,m.type=y.type,e=y.dependencies,m.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),a=a.sibling;return Ne(_e,_e.current&1|2),n.child}e=e.sibling}m.tail!==null&&Ve()>Ps&&(n.flags|=128,l=!0,xr(m,!1),n.lanes=4194304)}else{if(!l)if(e=ji(y),e!==null){if(n.flags|=128,l=!0,a=e.updateQueue,a!==null&&(n.updateQueue=a,n.flags|=4),xr(m,!0),m.tail===null&&m.tailMode==="hidden"&&!y.alternate&&!Ee)return st(n),null}else 2*Ve()-m.renderingStartTime>Ps&&a!==1073741824&&(n.flags|=128,l=!0,xr(m,!1),n.lanes=4194304);m.isBackwards?(y.sibling=n.child,n.child=y):(a=m.last,a!==null?a.sibling=y:n.child=y,m.last=y)}return m.tail!==null?(n=m.tail,m.rendering=n,m.tail=n.sibling,m.renderingStartTime=Ve(),n.sibling=null,a=_e.current,Ne(_e,l?a&1|2:a&1),n):(st(n),null);case 22:case 23:return Cl(),l=n.memoizedState!==null,e!==null&&e.memoizedState!==null!==l&&(n.flags|=8192),l&&(n.mode&1)!==0?(bt&1073741824)!==0&&(st(n),n.subtreeFlags&6&&(n.flags|=8192)):st(n),null;case 24:return null;case 25:return null}throw Error(i(156,n.tag))}function Yv(e,n){switch(Lo(n),n.tag){case 1:return dt(n.type)&&hi(),e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 3:return Ss(),Te(ut),Te(tt),qo(),e=n.flags,(e&65536)!==0&&(e&128)===0?(n.flags=e&-65537|128,n):null;case 5:return Go(n),null;case 13:if(Te(_e),e=n.memoizedState,e!==null&&e.dehydrated!==null){if(n.alternate===null)throw Error(i(340));ws()}return e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 19:return Te(_e),null;case 4:return Ss(),null;case 10:return zo(n.type._context),null;case 22:case 23:return Cl(),null;case 24:return null;default:return null}}var _i=!1,rt=!1,Qv=typeof WeakSet=="function"?WeakSet:Set,Q=null;function Cs(e,n){var a=e.ref;if(a!==null)if(typeof a=="function")try{a(null)}catch(l){Re(e,n,l)}else a.current=null}function fl(e,n,a){try{a()}catch(l){Re(e,n,l)}}var zh=!1;function Jv(e,n){if(Co=Jr,e=xd(),vo(e)){if("selectionStart"in e)var a={start:e.selectionStart,end:e.selectionEnd};else e:{a=(a=e.ownerDocument)&&a.defaultView||window;var l=a.getSelection&&a.getSelection();if(l&&l.rangeCount!==0){a=l.anchorNode;var u=l.anchorOffset,m=l.focusNode;l=l.focusOffset;try{a.nodeType,m.nodeType}catch{a=null;break e}var y=0,b=-1,C=-1,L=0,$=0,H=e,W=null;t:for(;;){for(var X;H!==a||u!==0&&H.nodeType!==3||(b=y+u),H!==m||l!==0&&H.nodeType!==3||(C=y+l),H.nodeType===3&&(y+=H.nodeValue.length),(X=H.firstChild)!==null;)W=H,H=X;for(;;){if(H===e)break t;if(W===a&&++L===u&&(b=y),W===m&&++$===l&&(C=y),(X=H.nextSibling)!==null)break;H=W,W=H.parentNode}H=X}a=b===-1||C===-1?null:{start:b,end:C}}else a=null}a=a||{start:0,end:0}}else a=null;for(To={focusedElem:e,selectionRange:a},Jr=!1,Q=n;Q!==null;)if(n=Q,e=n.child,(n.subtreeFlags&1028)!==0&&e!==null)e.return=n,Q=e;else for(;Q!==null;){n=Q;try{var Z=n.alternate;if((n.flags&1024)!==0)switch(n.tag){case 0:case 11:case 15:break;case 1:if(Z!==null){var te=Z.memoizedProps,Fe=Z.memoizedState,A=n.stateNode,T=A.getSnapshotBeforeUpdate(n.elementType===n.type?te:Lt(n.type,te),Fe);A.__reactInternalSnapshotBeforeUpdate=T}break;case 3:var _=n.stateNode.containerInfo;_.nodeType===1?_.textContent="":_.nodeType===9&&_.documentElement&&_.removeChild(_.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(i(163))}}catch(G){Re(n,n.return,G)}if(e=n.sibling,e!==null){e.return=n.return,Q=e;break}Q=n.return}return Z=zh,zh=!1,Z}function wr(e,n,a){var l=n.updateQueue;if(l=l!==null?l.lastEffect:null,l!==null){var u=l=l.next;do{if((u.tag&e)===e){var m=u.destroy;u.destroy=void 0,m!==void 0&&fl(n,a,m)}u=u.next}while(u!==l)}}function Di(e,n){if(n=n.updateQueue,n=n!==null?n.lastEffect:null,n!==null){var a=n=n.next;do{if((a.tag&e)===e){var l=a.create;a.destroy=l()}a=a.next}while(a!==n)}}function pl(e){var n=e.ref;if(n!==null){var a=e.stateNode;switch(e.tag){case 5:e=a;break;default:e=a}typeof n=="function"?n(e):n.current=e}}function Uh(e){var n=e.alternate;n!==null&&(e.alternate=null,Uh(n)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(n=e.stateNode,n!==null&&(delete n[$t],delete n[cr],delete n[Ao],delete n[Rv],delete n[Lv])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function Wh(e){return e.tag===5||e.tag===3||e.tag===4}function $h(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||Wh(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function gl(e,n,a){var l=e.tag;if(l===5||l===6)e=e.stateNode,n?a.nodeType===8?a.parentNode.insertBefore(e,n):a.insertBefore(e,n):(a.nodeType===8?(n=a.parentNode,n.insertBefore(e,a)):(n=a,n.appendChild(e)),a=a._reactRootContainer,a!=null||n.onclick!==null||(n.onclick=ui));else if(l!==4&&(e=e.child,e!==null))for(gl(e,n,a),e=e.sibling;e!==null;)gl(e,n,a),e=e.sibling}function yl(e,n,a){var l=e.tag;if(l===5||l===6)e=e.stateNode,n?a.insertBefore(e,n):a.appendChild(e);else if(l!==4&&(e=e.child,e!==null))for(yl(e,n,a),e=e.sibling;e!==null;)yl(e,n,a),e=e.sibling}var Je=null,It=!1;function bn(e,n,a){for(a=a.child;a!==null;)Hh(e,n,a),a=a.sibling}function Hh(e,n,a){if(Wt&&typeof Wt.onCommitFiberUnmount=="function")try{Wt.onCommitFiberUnmount(Gr,a)}catch{}switch(a.tag){case 5:rt||Cs(a,n);case 6:var l=Je,u=It;Je=null,bn(e,n,a),Je=l,It=u,Je!==null&&(It?(e=Je,a=a.stateNode,e.nodeType===8?e.parentNode.removeChild(a):e.removeChild(a)):Je.removeChild(a.stateNode));break;case 18:Je!==null&&(It?(e=Je,a=a.stateNode,e.nodeType===8?Eo(e.parentNode,a):e.nodeType===1&&Eo(e,a),Js(e)):Eo(Je,a.stateNode));break;case 4:l=Je,u=It,Je=a.stateNode.containerInfo,It=!0,bn(e,n,a),Je=l,It=u;break;case 0:case 11:case 14:case 15:if(!rt&&(l=a.updateQueue,l!==null&&(l=l.lastEffect,l!==null))){u=l=l.next;do{var m=u,y=m.destroy;m=m.tag,y!==void 0&&((m&2)!==0||(m&4)!==0)&&fl(a,n,y),u=u.next}while(u!==l)}bn(e,n,a);break;case 1:if(!rt&&(Cs(a,n),l=a.stateNode,typeof l.componentWillUnmount=="function"))try{l.props=a.memoizedProps,l.state=a.memoizedState,l.componentWillUnmount()}catch(b){Re(a,n,b)}bn(e,n,a);break;case 21:bn(e,n,a);break;case 22:a.mode&1?(rt=(l=rt)||a.memoizedState!==null,bn(e,n,a),rt=l):bn(e,n,a);break;default:bn(e,n,a)}}function Gh(e){var n=e.updateQueue;if(n!==null){e.updateQueue=null;var a=e.stateNode;a===null&&(a=e.stateNode=new Qv),n.forEach(function(l){var u=ox.bind(null,e,l);a.has(l)||(a.add(l),l.then(u,u))})}}function Vt(e,n){var a=n.deletions;if(a!==null)for(var l=0;l<a.length;l++){var u=a[l];try{var m=e,y=n,b=y;e:for(;b!==null;){switch(b.tag){case 5:Je=b.stateNode,It=!1;break e;case 3:Je=b.stateNode.containerInfo,It=!0;break e;case 4:Je=b.stateNode.containerInfo,It=!0;break e}b=b.return}if(Je===null)throw Error(i(160));Hh(m,y,u),Je=null,It=!1;var C=u.alternate;C!==null&&(C.return=null),u.return=null}catch(L){Re(u,n,L)}}if(n.subtreeFlags&12854)for(n=n.child;n!==null;)Kh(n,e),n=n.sibling}function Kh(e,n){var a=e.alternate,l=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(Vt(n,e),Kt(e),l&4){try{wr(3,e,e.return),Di(3,e)}catch(te){Re(e,e.return,te)}try{wr(5,e,e.return)}catch(te){Re(e,e.return,te)}}break;case 1:Vt(n,e),Kt(e),l&512&&a!==null&&Cs(a,a.return);break;case 5:if(Vt(n,e),Kt(e),l&512&&a!==null&&Cs(a,a.return),e.flags&32){var u=e.stateNode;try{zs(u,"")}catch(te){Re(e,e.return,te)}}if(l&4&&(u=e.stateNode,u!=null)){var m=e.memoizedProps,y=a!==null?a.memoizedProps:m,b=e.type,C=e.updateQueue;if(e.updateQueue=null,C!==null)try{b==="input"&&m.type==="radio"&&m.name!=null&&bu(u,m),Ka(b,y);var L=Ka(b,m);for(y=0;y<C.length;y+=2){var $=C[y],H=C[y+1];$==="style"?Mu(u,H):$==="dangerouslySetInnerHTML"?Tu(u,H):$==="children"?zs(u,H):R(u,$,H,L)}switch(b){case"input":Ua(u,m);break;case"textarea":Su(u,m);break;case"select":var W=u._wrapperState.wasMultiple;u._wrapperState.wasMultiple=!!m.multiple;var X=m.value;X!=null?is(u,!!m.multiple,X,!1):W!==!!m.multiple&&(m.defaultValue!=null?is(u,!!m.multiple,m.defaultValue,!0):is(u,!!m.multiple,m.multiple?[]:"",!1))}u[cr]=m}catch(te){Re(e,e.return,te)}}break;case 6:if(Vt(n,e),Kt(e),l&4){if(e.stateNode===null)throw Error(i(162));u=e.stateNode,m=e.memoizedProps;try{u.nodeValue=m}catch(te){Re(e,e.return,te)}}break;case 3:if(Vt(n,e),Kt(e),l&4&&a!==null&&a.memoizedState.isDehydrated)try{Js(n.containerInfo)}catch(te){Re(e,e.return,te)}break;case 4:Vt(n,e),Kt(e);break;case 13:Vt(n,e),Kt(e),u=e.child,u.flags&8192&&(m=u.memoizedState!==null,u.stateNode.isHidden=m,!m||u.alternate!==null&&u.alternate.memoizedState!==null||(wl=Ve())),l&4&&Gh(e);break;case 22:if($=a!==null&&a.memoizedState!==null,e.mode&1?(rt=(L=rt)||$,Vt(n,e),rt=L):Vt(n,e),Kt(e),l&8192){if(L=e.memoizedState!==null,(e.stateNode.isHidden=L)&&!$&&(e.mode&1)!==0)for(Q=e,$=e.child;$!==null;){for(H=Q=$;Q!==null;){switch(W=Q,X=W.child,W.tag){case 0:case 11:case 14:case 15:wr(4,W,W.return);break;case 1:Cs(W,W.return);var Z=W.stateNode;if(typeof Z.componentWillUnmount=="function"){l=W,a=W.return;try{n=l,Z.props=n.memoizedProps,Z.state=n.memoizedState,Z.componentWillUnmount()}catch(te){Re(l,a,te)}}break;case 5:Cs(W,W.return);break;case 22:if(W.memoizedState!==null){Yh(H);continue}}X!==null?(X.return=W,Q=X):Yh(H)}$=$.sibling}e:for($=null,H=e;;){if(H.tag===5){if($===null){$=H;try{u=H.stateNode,L?(m=u.style,typeof m.setProperty=="function"?m.setProperty("display","none","important"):m.display="none"):(b=H.stateNode,C=H.memoizedProps.style,y=C!=null&&C.hasOwnProperty("display")?C.display:null,b.style.display=Pu("display",y))}catch(te){Re(e,e.return,te)}}}else if(H.tag===6){if($===null)try{H.stateNode.nodeValue=L?"":H.memoizedProps}catch(te){Re(e,e.return,te)}}else if((H.tag!==22&&H.tag!==23||H.memoizedState===null||H===e)&&H.child!==null){H.child.return=H,H=H.child;continue}if(H===e)break e;for(;H.sibling===null;){if(H.return===null||H.return===e)break e;$===H&&($=null),H=H.return}$===H&&($=null),H.sibling.return=H.return,H=H.sibling}}break;case 19:Vt(n,e),Kt(e),l&4&&Gh(e);break;case 21:break;default:Vt(n,e),Kt(e)}}function Kt(e){var n=e.flags;if(n&2){try{e:{for(var a=e.return;a!==null;){if(Wh(a)){var l=a;break e}a=a.return}throw Error(i(160))}switch(l.tag){case 5:var u=l.stateNode;l.flags&32&&(zs(u,""),l.flags&=-33);var m=$h(e);yl(e,m,u);break;case 3:case 4:var y=l.stateNode.containerInfo,b=$h(e);gl(e,b,y);break;default:throw Error(i(161))}}catch(C){Re(e,e.return,C)}e.flags&=-3}n&4096&&(e.flags&=-4097)}function Zv(e,n,a){Q=e,qh(e)}function qh(e,n,a){for(var l=(e.mode&1)!==0;Q!==null;){var u=Q,m=u.child;if(u.tag===22&&l){var y=u.memoizedState!==null||_i;if(!y){var b=u.alternate,C=b!==null&&b.memoizedState!==null||rt;b=_i;var L=rt;if(_i=y,(rt=C)&&!L)for(Q=u;Q!==null;)y=Q,C=y.child,y.tag===22&&y.memoizedState!==null?Qh(u):C!==null?(C.return=y,Q=C):Qh(u);for(;m!==null;)Q=m,qh(m),m=m.sibling;Q=u,_i=b,rt=L}Xh(e)}else(u.subtreeFlags&8772)!==0&&m!==null?(m.return=u,Q=m):Xh(e)}}function Xh(e){for(;Q!==null;){var n=Q;if((n.flags&8772)!==0){var a=n.alternate;try{if((n.flags&8772)!==0)switch(n.tag){case 0:case 11:case 15:rt||Di(5,n);break;case 1:var l=n.stateNode;if(n.flags&4&&!rt)if(a===null)l.componentDidMount();else{var u=n.elementType===n.type?a.memoizedProps:Lt(n.type,a.memoizedProps);l.componentDidUpdate(u,a.memoizedState,l.__reactInternalSnapshotBeforeUpdate)}var m=n.updateQueue;m!==null&&Yd(n,m,l);break;case 3:var y=n.updateQueue;if(y!==null){if(a=null,n.child!==null)switch(n.child.tag){case 5:a=n.child.stateNode;break;case 1:a=n.child.stateNode}Yd(n,y,a)}break;case 5:var b=n.stateNode;if(a===null&&n.flags&4){a=b;var C=n.memoizedProps;switch(n.type){case"button":case"input":case"select":case"textarea":C.autoFocus&&a.focus();break;case"img":C.src&&(a.src=C.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(n.memoizedState===null){var L=n.alternate;if(L!==null){var $=L.memoizedState;if($!==null){var H=$.dehydrated;H!==null&&Js(H)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(i(163))}rt||n.flags&512&&pl(n)}catch(W){Re(n,n.return,W)}}if(n===e){Q=null;break}if(a=n.sibling,a!==null){a.return=n.return,Q=a;break}Q=n.return}}function Yh(e){for(;Q!==null;){var n=Q;if(n===e){Q=null;break}var a=n.sibling;if(a!==null){a.return=n.return,Q=a;break}Q=n.return}}function Qh(e){for(;Q!==null;){var n=Q;try{switch(n.tag){case 0:case 11:case 15:var a=n.return;try{Di(4,n)}catch(C){Re(n,a,C)}break;case 1:var l=n.stateNode;if(typeof l.componentDidMount=="function"){var u=n.return;try{l.componentDidMount()}catch(C){Re(n,u,C)}}var m=n.return;try{pl(n)}catch(C){Re(n,m,C)}break;case 5:var y=n.return;try{pl(n)}catch(C){Re(n,y,C)}}}catch(C){Re(n,n.return,C)}if(n===e){Q=null;break}var b=n.sibling;if(b!==null){b.return=n.return,Q=b;break}Q=n.return}}var ex=Math.ceil,Ri=I.ReactCurrentDispatcher,vl=I.ReactCurrentOwner,Mt=I.ReactCurrentBatchConfig,me=0,Ye=null,Be=null,Ze=0,bt=0,Ts=gn(0),$e=0,br=null,zn=0,Li=0,xl=0,kr=null,mt=null,wl=0,Ps=1/0,an=null,Ii=!1,bl=null,kn=null,Vi=!1,jn=null,Fi=0,jr=0,kl=null,Bi=-1,Oi=0;function ot(){return(me&6)!==0?Ve():Bi!==-1?Bi:Bi=Ve()}function Sn(e){return(e.mode&1)===0?1:(me&2)!==0&&Ze!==0?Ze&-Ze:Vv.transition!==null?(Oi===0&&(Oi=$u()),Oi):(e=be,e!==0||(e=window.event,e=e===void 0?16:Zu(e.type)),e)}function Ft(e,n,a,l){if(50<jr)throw jr=0,kl=null,Error(i(185));Ks(e,a,l),((me&2)===0||e!==Ye)&&(e===Ye&&((me&2)===0&&(Li|=a),$e===4&&Nn(e,Ze)),ft(e,l),a===1&&me===0&&(n.mode&1)===0&&(Ps=Ve()+500,fi&&vn()))}function ft(e,n){var a=e.callbackNode;Vy(e,n);var l=Xr(e,e===Ye?Ze:0);if(l===0)a!==null&&zu(a),e.callbackNode=null,e.callbackPriority=0;else if(n=l&-l,e.callbackPriority!==n){if(a!=null&&zu(a),n===1)e.tag===0?Iv(Zh.bind(null,e)):Fd(Zh.bind(null,e)),_v(function(){(me&6)===0&&vn()}),a=null;else{switch(Hu(l)){case 1:a=eo;break;case 4:a=Uu;break;case 16:a=Hr;break;case 536870912:a=Wu;break;default:a=Hr}a=om(a,Jh.bind(null,e))}e.callbackPriority=n,e.callbackNode=a}}function Jh(e,n){if(Bi=-1,Oi=0,(me&6)!==0)throw Error(i(327));var a=e.callbackNode;if(Ms()&&e.callbackNode!==a)return null;var l=Xr(e,e===Ye?Ze:0);if(l===0)return null;if((l&30)!==0||(l&e.expiredLanes)!==0||n)n=zi(e,l);else{n=l;var u=me;me|=2;var m=tm();(Ye!==e||Ze!==n)&&(an=null,Ps=Ve()+500,Wn(e,n));do try{sx();break}catch(b){em(e,b)}while(!0);Oo(),Ri.current=m,me=u,Be!==null?n=0:(Ye=null,Ze=0,n=$e)}if(n!==0){if(n===2&&(u=to(e),u!==0&&(l=u,n=jl(e,u))),n===1)throw a=br,Wn(e,0),Nn(e,l),ft(e,Ve()),a;if(n===6)Nn(e,l);else{if(u=e.current.alternate,(l&30)===0&&!tx(u)&&(n=zi(e,l),n===2&&(m=to(e),m!==0&&(l=m,n=jl(e,m))),n===1))throw a=br,Wn(e,0),Nn(e,l),ft(e,Ve()),a;switch(e.finishedWork=u,e.finishedLanes=l,n){case 0:case 1:throw Error(i(345));case 2:$n(e,mt,an);break;case 3:if(Nn(e,l),(l&130023424)===l&&(n=wl+500-Ve(),10<n)){if(Xr(e,0)!==0)break;if(u=e.suspendedLanes,(u&l)!==l){ot(),e.pingedLanes|=e.suspendedLanes&u;break}e.timeoutHandle=Mo($n.bind(null,e,mt,an),n);break}$n(e,mt,an);break;case 4:if(Nn(e,l),(l&4194240)===l)break;for(n=e.eventTimes,u=-1;0<l;){var y=31-_t(l);m=1<<y,y=n[y],y>u&&(u=y),l&=~m}if(l=u,l=Ve()-l,l=(120>l?120:480>l?480:1080>l?1080:1920>l?1920:3e3>l?3e3:4320>l?4320:1960*ex(l/1960))-l,10<l){e.timeoutHandle=Mo($n.bind(null,e,mt,an),l);break}$n(e,mt,an);break;case 5:$n(e,mt,an);break;default:throw Error(i(329))}}}return ft(e,Ve()),e.callbackNode===a?Jh.bind(null,e):null}function jl(e,n){var a=kr;return e.current.memoizedState.isDehydrated&&(Wn(e,n).flags|=256),e=zi(e,n),e!==2&&(n=mt,mt=a,n!==null&&Sl(n)),e}function Sl(e){mt===null?mt=e:mt.push.apply(mt,e)}function tx(e){for(var n=e;;){if(n.flags&16384){var a=n.updateQueue;if(a!==null&&(a=a.stores,a!==null))for(var l=0;l<a.length;l++){var u=a[l],m=u.getSnapshot;u=u.value;try{if(!Dt(m(),u))return!1}catch{return!1}}}if(a=n.child,n.subtreeFlags&16384&&a!==null)a.return=n,n=a;else{if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return!0;n=n.return}n.sibling.return=n.return,n=n.sibling}}return!0}function Nn(e,n){for(n&=~xl,n&=~Li,e.suspendedLanes|=n,e.pingedLanes&=~n,e=e.expirationTimes;0<n;){var a=31-_t(n),l=1<<a;e[a]=-1,n&=~l}}function Zh(e){if((me&6)!==0)throw Error(i(327));Ms();var n=Xr(e,0);if((n&1)===0)return ft(e,Ve()),null;var a=zi(e,n);if(e.tag!==0&&a===2){var l=to(e);l!==0&&(n=l,a=jl(e,l))}if(a===1)throw a=br,Wn(e,0),Nn(e,n),ft(e,Ve()),a;if(a===6)throw Error(i(345));return e.finishedWork=e.current.alternate,e.finishedLanes=n,$n(e,mt,an),ft(e,Ve()),null}function Nl(e,n){var a=me;me|=1;try{return e(n)}finally{me=a,me===0&&(Ps=Ve()+500,fi&&vn())}}function Un(e){jn!==null&&jn.tag===0&&(me&6)===0&&Ms();var n=me;me|=1;var a=Mt.transition,l=be;try{if(Mt.transition=null,be=1,e)return e()}finally{be=l,Mt.transition=a,me=n,(me&6)===0&&vn()}}function Cl(){bt=Ts.current,Te(Ts)}function Wn(e,n){e.finishedWork=null,e.finishedLanes=0;var a=e.timeoutHandle;if(a!==-1&&(e.timeoutHandle=-1,Av(a)),Be!==null)for(a=Be.return;a!==null;){var l=a;switch(Lo(l),l.tag){case 1:l=l.type.childContextTypes,l!=null&&hi();break;case 3:Ss(),Te(ut),Te(tt),qo();break;case 5:Go(l);break;case 4:Ss();break;case 13:Te(_e);break;case 19:Te(_e);break;case 10:zo(l.type._context);break;case 22:case 23:Cl()}a=a.return}if(Ye=e,Be=e=Cn(e.current,null),Ze=bt=n,$e=0,br=null,xl=Li=zn=0,mt=kr=null,Fn!==null){for(n=0;n<Fn.length;n++)if(a=Fn[n],l=a.interleaved,l!==null){a.interleaved=null;var u=l.next,m=a.pending;if(m!==null){var y=m.next;m.next=u,l.next=y}a.pending=l}Fn=null}return e}function em(e,n){do{var a=Be;try{if(Oo(),Si.current=Pi,Ni){for(var l=De.memoizedState;l!==null;){var u=l.queue;u!==null&&(u.pending=null),l=l.next}Ni=!1}if(On=0,Xe=We=De=null,pr=!1,gr=0,vl.current=null,a===null||a.return===null){$e=1,br=n,Be=null;break}e:{var m=e,y=a.return,b=a,C=n;if(n=Ze,b.flags|=32768,C!==null&&typeof C=="object"&&typeof C.then=="function"){var L=C,$=b,H=$.tag;if(($.mode&1)===0&&(H===0||H===11||H===15)){var W=$.alternate;W?($.updateQueue=W.updateQueue,$.memoizedState=W.memoizedState,$.lanes=W.lanes):($.updateQueue=null,$.memoizedState=null)}var X=Nh(y);if(X!==null){X.flags&=-257,Ch(X,y,b,m,n),X.mode&1&&Sh(m,L,n),n=X,C=L;var Z=n.updateQueue;if(Z===null){var te=new Set;te.add(C),n.updateQueue=te}else Z.add(C);break e}else{if((n&1)===0){Sh(m,L,n),Tl();break e}C=Error(i(426))}}else if(Ee&&b.mode&1){var Fe=Nh(y);if(Fe!==null){(Fe.flags&65536)===0&&(Fe.flags|=256),Ch(Fe,y,b,m,n),Fo(Ns(C,b));break e}}m=C=Ns(C,b),$e!==4&&($e=2),kr===null?kr=[m]:kr.push(m),m=y;do{switch(m.tag){case 3:m.flags|=65536,n&=-n,m.lanes|=n;var A=kh(m,C,n);Xd(m,A);break e;case 1:b=C;var T=m.type,_=m.stateNode;if((m.flags&128)===0&&(typeof T.getDerivedStateFromError=="function"||_!==null&&typeof _.componentDidCatch=="function"&&(kn===null||!kn.has(_)))){m.flags|=65536,n&=-n,m.lanes|=n;var G=jh(m,b,n);Xd(m,G);break e}}m=m.return}while(m!==null)}sm(a)}catch(ne){n=ne,Be===a&&a!==null&&(Be=a=a.return);continue}break}while(!0)}function tm(){var e=Ri.current;return Ri.current=Pi,e===null?Pi:e}function Tl(){($e===0||$e===3||$e===2)&&($e=4),Ye===null||(zn&268435455)===0&&(Li&268435455)===0||Nn(Ye,Ze)}function zi(e,n){var a=me;me|=2;var l=tm();(Ye!==e||Ze!==n)&&(an=null,Wn(e,n));do try{nx();break}catch(u){em(e,u)}while(!0);if(Oo(),me=a,Ri.current=l,Be!==null)throw Error(i(261));return Ye=null,Ze=0,$e}function nx(){for(;Be!==null;)nm(Be)}function sx(){for(;Be!==null&&!Py();)nm(Be)}function nm(e){var n=am(e.alternate,e,bt);e.memoizedProps=e.pendingProps,n===null?sm(e):Be=n,vl.current=null}function sm(e){var n=e;do{var a=n.alternate;if(e=n.return,(n.flags&32768)===0){if(a=Xv(a,n,bt),a!==null){Be=a;return}}else{if(a=Yv(a,n),a!==null){a.flags&=32767,Be=a;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{$e=6,Be=null;return}}if(n=n.sibling,n!==null){Be=n;return}Be=n=e}while(n!==null);$e===0&&($e=5)}function $n(e,n,a){var l=be,u=Mt.transition;try{Mt.transition=null,be=1,rx(e,n,a,l)}finally{Mt.transition=u,be=l}return null}function rx(e,n,a,l){do Ms();while(jn!==null);if((me&6)!==0)throw Error(i(327));a=e.finishedWork;var u=e.finishedLanes;if(a===null)return null;if(e.finishedWork=null,e.finishedLanes=0,a===e.current)throw Error(i(177));e.callbackNode=null,e.callbackPriority=0;var m=a.lanes|a.childLanes;if(Fy(e,m),e===Ye&&(Be=Ye=null,Ze=0),(a.subtreeFlags&2064)===0&&(a.flags&2064)===0||Vi||(Vi=!0,om(Hr,function(){return Ms(),null})),m=(a.flags&15990)!==0,(a.subtreeFlags&15990)!==0||m){m=Mt.transition,Mt.transition=null;var y=be;be=1;var b=me;me|=4,vl.current=null,Jv(e,a),Kh(a,e),Sv(To),Jr=!!Co,To=Co=null,e.current=a,Zv(a),My(),me=b,be=y,Mt.transition=m}else e.current=a;if(Vi&&(Vi=!1,jn=e,Fi=u),m=e.pendingLanes,m===0&&(kn=null),_y(a.stateNode),ft(e,Ve()),n!==null)for(l=e.onRecoverableError,a=0;a<n.length;a++)u=n[a],l(u.value,{componentStack:u.stack,digest:u.digest});if(Ii)throw Ii=!1,e=bl,bl=null,e;return(Fi&1)!==0&&e.tag!==0&&Ms(),m=e.pendingLanes,(m&1)!==0?e===kl?jr++:(jr=0,kl=e):jr=0,vn(),null}function Ms(){if(jn!==null){var e=Hu(Fi),n=Mt.transition,a=be;try{if(Mt.transition=null,be=16>e?16:e,jn===null)var l=!1;else{if(e=jn,jn=null,Fi=0,(me&6)!==0)throw Error(i(331));var u=me;for(me|=4,Q=e.current;Q!==null;){var m=Q,y=m.child;if((Q.flags&16)!==0){var b=m.deletions;if(b!==null){for(var C=0;C<b.length;C++){var L=b[C];for(Q=L;Q!==null;){var $=Q;switch($.tag){case 0:case 11:case 15:wr(8,$,m)}var H=$.child;if(H!==null)H.return=$,Q=H;else for(;Q!==null;){$=Q;var W=$.sibling,X=$.return;if(Uh($),$===L){Q=null;break}if(W!==null){W.return=X,Q=W;break}Q=X}}}var Z=m.alternate;if(Z!==null){var te=Z.child;if(te!==null){Z.child=null;do{var Fe=te.sibling;te.sibling=null,te=Fe}while(te!==null)}}Q=m}}if((m.subtreeFlags&2064)!==0&&y!==null)y.return=m,Q=y;else e:for(;Q!==null;){if(m=Q,(m.flags&2048)!==0)switch(m.tag){case 0:case 11:case 15:wr(9,m,m.return)}var A=m.sibling;if(A!==null){A.return=m.return,Q=A;break e}Q=m.return}}var T=e.current;for(Q=T;Q!==null;){y=Q;var _=y.child;if((y.subtreeFlags&2064)!==0&&_!==null)_.return=y,Q=_;else e:for(y=T;Q!==null;){if(b=Q,(b.flags&2048)!==0)try{switch(b.tag){case 0:case 11:case 15:Di(9,b)}}catch(ne){Re(b,b.return,ne)}if(b===y){Q=null;break e}var G=b.sibling;if(G!==null){G.return=b.return,Q=G;break e}Q=b.return}}if(me=u,vn(),Wt&&typeof Wt.onPostCommitFiberRoot=="function")try{Wt.onPostCommitFiberRoot(Gr,e)}catch{}l=!0}return l}finally{be=a,Mt.transition=n}}return!1}function rm(e,n,a){n=Ns(a,n),n=kh(e,n,1),e=wn(e,n,1),n=ot(),e!==null&&(Ks(e,1,n),ft(e,n))}function Re(e,n,a){if(e.tag===3)rm(e,e,a);else for(;n!==null;){if(n.tag===3){rm(n,e,a);break}else if(n.tag===1){var l=n.stateNode;if(typeof n.type.getDerivedStateFromError=="function"||typeof l.componentDidCatch=="function"&&(kn===null||!kn.has(l))){e=Ns(a,e),e=jh(n,e,1),n=wn(n,e,1),e=ot(),n!==null&&(Ks(n,1,e),ft(n,e));break}}n=n.return}}function ix(e,n,a){var l=e.pingCache;l!==null&&l.delete(n),n=ot(),e.pingedLanes|=e.suspendedLanes&a,Ye===e&&(Ze&a)===a&&($e===4||$e===3&&(Ze&130023424)===Ze&&500>Ve()-wl?Wn(e,0):xl|=a),ft(e,n)}function im(e,n){n===0&&((e.mode&1)===0?n=1:(n=qr,qr<<=1,(qr&130023424)===0&&(qr=4194304)));var a=ot();e=nn(e,n),e!==null&&(Ks(e,n,a),ft(e,a))}function ax(e){var n=e.memoizedState,a=0;n!==null&&(a=n.retryLane),im(e,a)}function ox(e,n){var a=0;switch(e.tag){case 13:var l=e.stateNode,u=e.memoizedState;u!==null&&(a=u.retryLane);break;case 19:l=e.stateNode;break;default:throw Error(i(314))}l!==null&&l.delete(n),im(e,a)}var am;am=function(e,n,a){if(e!==null)if(e.memoizedProps!==n.pendingProps||ut.current)ht=!0;else{if((e.lanes&a)===0&&(n.flags&128)===0)return ht=!1,qv(e,n,a);ht=(e.flags&131072)!==0}else ht=!1,Ee&&(n.flags&1048576)!==0&&Bd(n,gi,n.index);switch(n.lanes=0,n.tag){case 2:var l=n.type;Ai(e,n),e=n.pendingProps;var u=ys(n,tt.current);js(n,a),u=Qo(null,n,l,e,u,a);var m=Jo();return n.flags|=1,typeof u=="object"&&u!==null&&typeof u.render=="function"&&u.$$typeof===void 0?(n.tag=1,n.memoizedState=null,n.updateQueue=null,dt(l)?(m=!0,mi(n)):m=!1,n.memoizedState=u.state!==null&&u.state!==void 0?u.state:null,$o(n),u.updater=Mi,n.stateNode=u,u._reactInternals=n,rl(n,l,e,a),n=ll(null,n,l,!0,m,a)):(n.tag=0,Ee&&m&&Ro(n),at(null,n,u,a),n=n.child),n;case 16:l=n.elementType;e:{switch(Ai(e,n),e=n.pendingProps,u=l._init,l=u(l._payload),n.type=l,u=n.tag=cx(l),e=Lt(l,e),u){case 0:n=ol(null,n,l,e,a);break e;case 1:n=_h(null,n,l,e,a);break e;case 11:n=Th(null,n,l,e,a);break e;case 14:n=Ph(null,n,l,Lt(l.type,e),a);break e}throw Error(i(306,l,""))}return n;case 0:return l=n.type,u=n.pendingProps,u=n.elementType===l?u:Lt(l,u),ol(e,n,l,u,a);case 1:return l=n.type,u=n.pendingProps,u=n.elementType===l?u:Lt(l,u),_h(e,n,l,u,a);case 3:e:{if(Dh(n),e===null)throw Error(i(387));l=n.pendingProps,m=n.memoizedState,u=m.element,qd(e,n),ki(n,l,null,a);var y=n.memoizedState;if(l=y.element,m.isDehydrated)if(m={element:l,isDehydrated:!1,cache:y.cache,pendingSuspenseBoundaries:y.pendingSuspenseBoundaries,transitions:y.transitions},n.updateQueue.baseState=m,n.memoizedState=m,n.flags&256){u=Ns(Error(i(423)),n),n=Rh(e,n,l,a,u);break e}else if(l!==u){u=Ns(Error(i(424)),n),n=Rh(e,n,l,a,u);break e}else for(wt=pn(n.stateNode.containerInfo.firstChild),xt=n,Ee=!0,Rt=null,a=Gd(n,null,l,a),n.child=a;a;)a.flags=a.flags&-3|4096,a=a.sibling;else{if(ws(),l===u){n=rn(e,n,a);break e}at(e,n,l,a)}n=n.child}return n;case 5:return Qd(n),e===null&&Vo(n),l=n.type,u=n.pendingProps,m=e!==null?e.memoizedProps:null,y=u.children,Po(l,u)?y=null:m!==null&&Po(l,m)&&(n.flags|=32),Ah(e,n),at(e,n,y,a),n.child;case 6:return e===null&&Vo(n),null;case 13:return Lh(e,n,a);case 4:return Ho(n,n.stateNode.containerInfo),l=n.pendingProps,e===null?n.child=bs(n,null,l,a):at(e,n,l,a),n.child;case 11:return l=n.type,u=n.pendingProps,u=n.elementType===l?u:Lt(l,u),Th(e,n,l,u,a);case 7:return at(e,n,n.pendingProps,a),n.child;case 8:return at(e,n,n.pendingProps.children,a),n.child;case 12:return at(e,n,n.pendingProps.children,a),n.child;case 10:e:{if(l=n.type._context,u=n.pendingProps,m=n.memoizedProps,y=u.value,Ne(xi,l._currentValue),l._currentValue=y,m!==null)if(Dt(m.value,y)){if(m.children===u.children&&!ut.current){n=rn(e,n,a);break e}}else for(m=n.child,m!==null&&(m.return=n);m!==null;){var b=m.dependencies;if(b!==null){y=m.child;for(var C=b.firstContext;C!==null;){if(C.context===l){if(m.tag===1){C=sn(-1,a&-a),C.tag=2;var L=m.updateQueue;if(L!==null){L=L.shared;var $=L.pending;$===null?C.next=C:(C.next=$.next,$.next=C),L.pending=C}}m.lanes|=a,C=m.alternate,C!==null&&(C.lanes|=a),Uo(m.return,a,n),b.lanes|=a;break}C=C.next}}else if(m.tag===10)y=m.type===n.type?null:m.child;else if(m.tag===18){if(y=m.return,y===null)throw Error(i(341));y.lanes|=a,b=y.alternate,b!==null&&(b.lanes|=a),Uo(y,a,n),y=m.sibling}else y=m.child;if(y!==null)y.return=m;else for(y=m;y!==null;){if(y===n){y=null;break}if(m=y.sibling,m!==null){m.return=y.return,y=m;break}y=y.return}m=y}at(e,n,u.children,a),n=n.child}return n;case 9:return u=n.type,l=n.pendingProps.children,js(n,a),u=Tt(u),l=l(u),n.flags|=1,at(e,n,l,a),n.child;case 14:return l=n.type,u=Lt(l,n.pendingProps),u=Lt(l.type,u),Ph(e,n,l,u,a);case 15:return Mh(e,n,n.type,n.pendingProps,a);case 17:return l=n.type,u=n.pendingProps,u=n.elementType===l?u:Lt(l,u),Ai(e,n),n.tag=1,dt(l)?(e=!0,mi(n)):e=!1,js(n,a),wh(n,l,u),rl(n,l,u,a),ll(null,n,l,!0,e,a);case 19:return Vh(e,n,a);case 22:return Eh(e,n,a)}throw Error(i(156,n.tag))};function om(e,n){return Ou(e,n)}function lx(e,n,a,l){this.tag=e,this.key=a,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=n,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=l,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function Et(e,n,a,l){return new lx(e,n,a,l)}function Pl(e){return e=e.prototype,!(!e||!e.isReactComponent)}function cx(e){if(typeof e=="function")return Pl(e)?1:0;if(e!=null){if(e=e.$$typeof,e===ve)return 11;if(e===Ie)return 14}return 2}function Cn(e,n){var a=e.alternate;return a===null?(a=Et(e.tag,n,e.key,e.mode),a.elementType=e.elementType,a.type=e.type,a.stateNode=e.stateNode,a.alternate=e,e.alternate=a):(a.pendingProps=n,a.type=e.type,a.flags=0,a.subtreeFlags=0,a.deletions=null),a.flags=e.flags&14680064,a.childLanes=e.childLanes,a.lanes=e.lanes,a.child=e.child,a.memoizedProps=e.memoizedProps,a.memoizedState=e.memoizedState,a.updateQueue=e.updateQueue,n=e.dependencies,a.dependencies=n===null?null:{lanes:n.lanes,firstContext:n.firstContext},a.sibling=e.sibling,a.index=e.index,a.ref=e.ref,a}function Ui(e,n,a,l,u,m){var y=2;if(l=e,typeof e=="function")Pl(e)&&(y=1);else if(typeof e=="string")y=5;else e:switch(e){case V:return Hn(a.children,u,m,n);case z:y=8,u|=8;break;case oe:return e=Et(12,a,n,u|2),e.elementType=oe,e.lanes=m,e;case ie:return e=Et(13,a,n,u),e.elementType=ie,e.lanes=m,e;case Pe:return e=Et(19,a,n,u),e.elementType=Pe,e.lanes=m,e;case Y:return Wi(a,u,m,n);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case le:y=10;break e;case xe:y=9;break e;case ve:y=11;break e;case Ie:y=14;break e;case Ae:y=16,l=null;break e}throw Error(i(130,e==null?e:typeof e,""))}return n=Et(y,a,n,u),n.elementType=e,n.type=l,n.lanes=m,n}function Hn(e,n,a,l){return e=Et(7,e,l,n),e.lanes=a,e}function Wi(e,n,a,l){return e=Et(22,e,l,n),e.elementType=Y,e.lanes=a,e.stateNode={isHidden:!1},e}function Ml(e,n,a){return e=Et(6,e,null,n),e.lanes=a,e}function El(e,n,a){return n=Et(4,e.children!==null?e.children:[],e.key,n),n.lanes=a,n.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},n}function ux(e,n,a,l,u){this.tag=n,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=no(0),this.expirationTimes=no(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=no(0),this.identifierPrefix=l,this.onRecoverableError=u,this.mutableSourceEagerHydrationData=null}function Al(e,n,a,l,u,m,y,b,C){return e=new ux(e,n,a,b,C),n===1?(n=1,m===!0&&(n|=8)):n=0,m=Et(3,null,null,n),e.current=m,m.stateNode=e,m.memoizedState={element:l,isDehydrated:a,cache:null,transitions:null,pendingSuspenseBoundaries:null},$o(m),e}function dx(e,n,a){var l=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:F,key:l==null?null:""+l,children:e,containerInfo:n,implementation:a}}function lm(e){if(!e)return yn;e=e._reactInternals;e:{if(Dn(e)!==e||e.tag!==1)throw Error(i(170));var n=e;do{switch(n.tag){case 3:n=n.stateNode.context;break e;case 1:if(dt(n.type)){n=n.stateNode.__reactInternalMemoizedMergedChildContext;break e}}n=n.return}while(n!==null);throw Error(i(171))}if(e.tag===1){var a=e.type;if(dt(a))return Id(e,a,n)}return n}function cm(e,n,a,l,u,m,y,b,C){return e=Al(a,l,!0,e,u,m,y,b,C),e.context=lm(null),a=e.current,l=ot(),u=Sn(a),m=sn(l,u),m.callback=n??null,wn(a,m,u),e.current.lanes=u,Ks(e,u,l),ft(e,l),e}function $i(e,n,a,l){var u=n.current,m=ot(),y=Sn(u);return a=lm(a),n.context===null?n.context=a:n.pendingContext=a,n=sn(m,y),n.payload={element:e},l=l===void 0?null:l,l!==null&&(n.callback=l),e=wn(u,n,y),e!==null&&(Ft(e,u,y,m),bi(e,u,y)),y}function Hi(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function um(e,n){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var a=e.retryLane;e.retryLane=a!==0&&a<n?a:n}}function _l(e,n){um(e,n),(e=e.alternate)&&um(e,n)}function hx(){return null}var dm=typeof reportError=="function"?reportError:function(e){console.error(e)};function Dl(e){this._internalRoot=e}Gi.prototype.render=Dl.prototype.render=function(e){var n=this._internalRoot;if(n===null)throw Error(i(409));$i(e,n,null,null)},Gi.prototype.unmount=Dl.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var n=e.containerInfo;Un(function(){$i(null,e,null,null)}),n[Jt]=null}};function Gi(e){this._internalRoot=e}Gi.prototype.unstable_scheduleHydration=function(e){if(e){var n=qu();e={blockedOn:null,target:e,priority:n};for(var a=0;a<hn.length&&n!==0&&n<hn[a].priority;a++);hn.splice(a,0,e),a===0&&Qu(e)}};function Rl(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function Ki(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function hm(){}function mx(e,n,a,l,u){if(u){if(typeof l=="function"){var m=l;l=function(){var L=Hi(y);m.call(L)}}var y=cm(n,l,e,0,null,!1,!1,"",hm);return e._reactRootContainer=y,e[Jt]=y.current,or(e.nodeType===8?e.parentNode:e),Un(),y}for(;u=e.lastChild;)e.removeChild(u);if(typeof l=="function"){var b=l;l=function(){var L=Hi(C);b.call(L)}}var C=Al(e,0,!1,null,null,!1,!1,"",hm);return e._reactRootContainer=C,e[Jt]=C.current,or(e.nodeType===8?e.parentNode:e),Un(function(){$i(n,C,a,l)}),C}function qi(e,n,a,l,u){var m=a._reactRootContainer;if(m){var y=m;if(typeof u=="function"){var b=u;u=function(){var C=Hi(y);b.call(C)}}$i(n,y,e,u)}else y=mx(a,n,e,u,l);return Hi(y)}Gu=function(e){switch(e.tag){case 3:var n=e.stateNode;if(n.current.memoizedState.isDehydrated){var a=Gs(n.pendingLanes);a!==0&&(so(n,a|1),ft(n,Ve()),(me&6)===0&&(Ps=Ve()+500,vn()))}break;case 13:Un(function(){var l=nn(e,1);if(l!==null){var u=ot();Ft(l,e,1,u)}}),_l(e,1)}},ro=function(e){if(e.tag===13){var n=nn(e,134217728);if(n!==null){var a=ot();Ft(n,e,134217728,a)}_l(e,134217728)}},Ku=function(e){if(e.tag===13){var n=Sn(e),a=nn(e,n);if(a!==null){var l=ot();Ft(a,e,n,l)}_l(e,n)}},qu=function(){return be},Xu=function(e,n){var a=be;try{return be=e,n()}finally{be=a}},Ya=function(e,n,a){switch(n){case"input":if(Ua(e,a),n=a.name,a.type==="radio"&&n!=null){for(a=e;a.parentNode;)a=a.parentNode;for(a=a.querySelectorAll("input[name="+JSON.stringify(""+n)+'][type="radio"]'),n=0;n<a.length;n++){var l=a[n];if(l!==e&&l.form===e.form){var u=di(l);if(!u)throw Error(i(90));xu(l),Ua(l,u)}}}break;case"textarea":Su(e,a);break;case"select":n=a.value,n!=null&&is(e,!!a.multiple,n,!1)}},Du=Nl,Ru=Un;var fx={usingClientEntryPoint:!1,Events:[ur,ps,di,Au,_u,Nl]},Sr={findFiberByHostInstance:Rn,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},px={bundleType:Sr.bundleType,version:Sr.version,rendererPackageName:Sr.rendererPackageName,rendererConfig:Sr.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:I.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=Fu(e),e===null?null:e.stateNode},findFiberByHostInstance:Sr.findFiberByHostInstance||hx,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Xi=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Xi.isDisabled&&Xi.supportsFiber)try{Gr=Xi.inject(px),Wt=Xi}catch{}}return pt.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=fx,pt.createPortal=function(e,n){var a=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!Rl(n))throw Error(i(200));return dx(e,n,null,a)},pt.createRoot=function(e,n){if(!Rl(e))throw Error(i(299));var a=!1,l="",u=dm;return n!=null&&(n.unstable_strictMode===!0&&(a=!0),n.identifierPrefix!==void 0&&(l=n.identifierPrefix),n.onRecoverableError!==void 0&&(u=n.onRecoverableError)),n=Al(e,1,!1,null,null,a,!1,l,u),e[Jt]=n.current,or(e.nodeType===8?e.parentNode:e),new Dl(n)},pt.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var n=e._reactInternals;if(n===void 0)throw typeof e.render=="function"?Error(i(188)):(e=Object.keys(e).join(","),Error(i(268,e)));return e=Fu(n),e=e===null?null:e.stateNode,e},pt.flushSync=function(e){return Un(e)},pt.hydrate=function(e,n,a){if(!Ki(n))throw Error(i(200));return qi(null,e,n,!0,a)},pt.hydrateRoot=function(e,n,a){if(!Rl(e))throw Error(i(405));var l=a!=null&&a.hydratedSources||null,u=!1,m="",y=dm;if(a!=null&&(a.unstable_strictMode===!0&&(u=!0),a.identifierPrefix!==void 0&&(m=a.identifierPrefix),a.onRecoverableError!==void 0&&(y=a.onRecoverableError)),n=cm(n,null,e,1,a??null,u,!1,m,y),e[Jt]=n.current,or(e),l)for(e=0;e<l.length;e++)a=l[e],u=a._getVersion,u=u(a._source),n.mutableSourceEagerHydrationData==null?n.mutableSourceEagerHydrationData=[a,u]:n.mutableSourceEagerHydrationData.push(a,u);return new Gi(n)},pt.render=function(e,n,a){if(!Ki(n))throw Error(i(200));return qi(null,e,n,!1,a)},pt.unmountComponentAtNode=function(e){if(!Ki(e))throw Error(i(40));return e._reactRootContainer?(Un(function(){qi(null,null,e,!1,function(){e._reactRootContainer=null,e[Jt]=null})}),!0):!1},pt.unstable_batchedUpdates=Nl,pt.unstable_renderSubtreeIntoContainer=function(e,n,a,l){if(!Ki(a))throw Error(i(200));if(e==null||e._reactInternals===void 0)throw Error(i(38));return qi(e,n,a,!1,l)},pt.version="18.3.1-next-f1338f8080-20240426",pt}var bm;function Nx(){if(bm)return Vl.exports;bm=1;function t(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(t)}catch(s){console.error(s)}}return t(),Vl.exports=Sx(),Vl.exports}var km;function Cx(){if(km)return Yi;km=1;var t=Nx();return Yi.createRoot=t.createRoot,Yi.hydrateRoot=t.hydrateRoot,Yi}var Tx=Cx();class Px extends Error{constructor(i,o){super(i);mm(this,"status");this.status=o}}async function qe(t,s){const i=await fetch(t,{...s,credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json",...s==null?void 0:s.headers}}),o=await i.json().catch(()=>({}));if(!i.ok)throw new Px(o.error||i.statusText||"Request failed",i.status);return o}const lc=()=>qe("/auth/status"),Mx=()=>qe("/api/config"),pa=()=>qe("/api/botstats"),Ex=()=>qe("/api/team"),Ax=t=>qe(`/api/team/${t}`),cc=()=>qe("/api/staff/me"),_x=(t,s)=>qe("/api/staff/profile",{method:"POST",headers:s?{"X-CSRF-Token":s}:void 0,body:JSON.stringify(t)}),Dx=(t,s)=>qe("/api/staff/global-profile",{method:"POST",headers:s?{"X-CSRF-Token":s}:void 0,body:JSON.stringify(t)}),Rx=()=>qe("/api/commands"),uc=()=>qe("/api/guilds"),jm=()=>qe("/api/me/overview"),Lx=t=>qe(`/api/guild/${t}/overview`),Ix=t=>qe(`/api/guild/${t}/levels`),Sm=t=>qe(`/api/guild/${t}/config`),Nm=t=>qe(`/api/guild/${t}/resources`);function _a(t,s,i,o){return qe(`/api/guild/${t}/config/${s}`,{method:"POST",headers:o?{"X-CSRF-Token":o}:void 0,body:JSON.stringify(i)})}function Vx(t,s,i){return qe(`/api/guild/${t}/config/profile`,{method:"POST",headers:i?{"X-CSRF-Token":i}:void 0,body:JSON.stringify(s)})}function sp(t){return t.replace(/\/+$/,"")||"/"}function Cm(t=window.location.pathname){const s=sp(t);return s==="/commands"?"commands":s==="/docs"?"docs":s.startsWith("/docs/")?"docs-detail":s==="/dashboard/staff"||s==="/dashboard/staff/"?"staff":s==="/dashboard"||s.startsWith("/dashboard/")?"dashboard":s==="/team"?"team":s==="/support"?"support":s==="/discord"?"discord":s.startsWith("/team/")?"team-member":s==="/privacy"?"privacy":s==="/terms"?"terms":s==="/community"?"community":s==="/donate"||s.startsWith("/donate")?"donate":s==="/transcript"||s.startsWith("/transcript/")?"transcript":s==="/changelog"?"changelog":s.startsWith("/changelog/")?"changelog-detail":"home"}function Es(t,s="overview"){return t?`/dashboard/${t}/${s}`:"/dashboard"}function dc(){return"/dashboard/servers"}function Tm(){const t=sp(window.location.pathname).split("/").filter(Boolean),s=["overview","leveling","moderation","server","ai","customization"];return t[1]==="servers"?{view:"servers",guildId:null,section:"overview"}:!t[1]||t[1]==="staff"?{view:"overview",guildId:null,section:"overview"}:{view:"guild",guildId:t[1]||null,section:s.includes(t[2])?t[2]:"overview"}}function he(t){t.startsWith("/")&&(window.history.pushState({},"",t),window.dispatchEvent(new PopStateEvent("popstate")),window.scrollTo({top:0,behavior:"smooth"}))}let Pm=null,Ol=null;function rs(){const[t,s]=P.useState(Pm);return P.useEffect(()=>{Ol||(Ol=Mx().then(i=>Pm=i)),Ol.then(s).catch(()=>{})},[]),t}function rp({onNavigate:t}){const s=rs();return r.jsxs("a",{className:"brand",href:"/",onClick:i=>{i.preventDefault(),t?t():he("/")},children:[r.jsx("span",{className:"brand-mark",children:s!=null&&s.bot_avatar_url?r.jsx("img",{src:s.bot_avatar_url,alt:"Niko"}):"n"}),r.jsx("span",{children:"niko"})]})}function St(){return r.jsxs("footer",{className:"site-footer",children:[r.jsx(rp,{}),r.jsx("span",{children:"Built for communities that care."}),r.jsxs("div",{children:[r.jsx("a",{href:"/privacy",onClick:t=>{t.preventDefault(),he("/privacy")},children:"Privacy"}),r.jsx("a",{href:"/terms",onClick:t=>{t.preventDefault(),he("/terms")},children:"Terms"}),r.jsx("a",{href:"/community",onClick:t=>{t.preventDefault(),he("/community")},children:"Community Policy"}),r.jsx("a",{href:"/support",onClick:t=>{t.preventDefault(),he("/support")},children:"Support"})]})]})}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Fx=t=>t==null?void 0:t.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase();/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */function Bx(t,s,i=[]){if(s==null)throw new Error("[lucide]: iconNode is required when icon name is used");return{name:Fx(t),size:24,node:s,...i.length>0?{aliases:i}:{}}}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ox=t=>{let s="",i=!1;for(const o of t){if(o==="-"||o==="_"||o<=" "){i=s.length>0;continue}s.length===0?s+=o.toLowerCase():s+=i?o.toUpperCase():o,i=!1}return s};/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const zx=t=>{const s=Ox(t);return s.charAt(0).toUpperCase()+s.slice(1)};/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const hc=(...t)=>t.filter((s,i,o)=>!!s&&s.trim()!==""&&o.indexOf(s)===i).join(" ").trim();/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Gn={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor","stroke-width":2,"stroke-linecap":"round","stroke-linejoin":"round"};/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */function zl(t){return t!=null}function Ux(t,s={}){var w,j;const i=s.attributeNames??{},o=k=>i[k]??k,c=t.size??t.width??Gn.width,d=t.size??t.height??Gn.height,h=((w=t.aliases)==null?void 0:w.filter(k=>typeof k=="string"&&k.trim()!=="").map(k=>`lucide-${k}`))??[],f=[...t.name?[`lucide-${t.name}`]:[],...h],p=((j=s.className)==null?void 0:j.split(" ").filter(Boolean))??[],v=s.includeDefaultClasses===!1?hc(...p):hc("lucide",...f,...p),g=s.absoluteStrokeWidth?Number(s.strokeWidth??Gn["stroke-width"])*Number(t.size??t.width??Gn.width)/Number(s.size??s.width??Gn.width):s.strokeWidth??Gn["stroke-width"];return["svg",{...Object.entries(Gn).reduce((k,[S,N])=>(k[o(S)]=N,k),{}),..."color"in s&&s.color&&{[o("stroke")]:s.color},..."size"in s&&zl(s.size)&&{[o("width")]:s.size,[o("height")]:s.size},..."width"in s&&zl(s.width)&&{[o("width")]:s.width},..."height"in s&&zl(s.height)&&{[o("height")]:s.height},[o("stroke-width")]:g,...v&&{[o("class")]:v},[o("viewBox")]:`0 0 ${c} ${d}`,...s.hasA11yProp===!1?{[o("aria-hidden")]:"true"}:{},..."attributes"in s&&s.attributes},t.node.map(k=>{const[S,N,B]=k,E=s.nonScalingStroke?{[o("vector-effect")]:"non-scaling-stroke",...N}:N;return B?[S,E,B]:[S,E]})]}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */function Wx(t,s={}){return Ux(t,{...s,attributeNames:{...s.attributeNames,class:"className","stroke-width":"strokeWidth","stroke-linecap":"strokeLinecap","stroke-linejoin":"strokeLinejoin","vector-effect":"vectorEffect"}})}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const $x=t=>{for(const s in t)if(s.startsWith("aria-")||s==="role"||s==="title")return!0;return!1},Hx=P.createContext({}),Gx=()=>P.useContext(Hx),Kx=P.forwardRef(({color:t,size:s,width:i,height:o,strokeWidth:c,absoluteStrokeWidth:d,nonScalingStroke:h,className:f="",children:p,iconNode:v=[],icon:g={node:v,aliases:[],size:24},...x},w)=>{const{size:j=24,strokeWidth:k=2,absoluteStrokeWidth:S=!1,nonScalingStroke:N=!1,color:B="currentColor",className:E=""}=Gx()??{},R=!!p||$x(x),[I,D,F=[]]=Wx(g,{color:t??B,width:i??s??j,height:o??s??j,strokeWidth:c??k,absoluteStrokeWidth:d??S,nonScalingStroke:h??N,className:hc(E,f),hasA11yProp:R,attributes:x});return P.createElement(I,{ref:w,...D},[...F.map(([V,z])=>P.createElement(V,z)),...Array.isArray(p)?p:[p]])});/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */function Ue(t,s=[],i=[]){const o=typeof t=="string"?Bx(t,s,i):t,c=P.forwardRef(({className:d,...h},f)=>P.createElement(Kx,{ref:f,icon:o,className:d,...h}));return o.name&&(c.displayName=zx(o.name)),c}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ip={name:"activity",size:24,node:[["path",{d:"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2",key:"169zse"}]]};ip.node;const qx=Ue(ip);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ap={name:"arrow-right",size:24,node:[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]]};ap.node;const Xx=Ue(ap);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const op={name:"book-open",size:24,node:[["path",{d:"M12 5v16",key:"1f6ucr"}],["path",{d:"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z",key:"1fyvmf"}]]};op.node;const Mm=Ue(op);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const lp={name:"chart-column",size:24,node:[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],aliases:["bar-chart-3"]};lp.node;const aa=Ue(lp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const cp={name:"external-link",size:24,node:[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]]};cp.node;const Yx=Ue(cp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const up={name:"hash",size:24,node:[["line",{x1:"4",x2:"20",y1:"9",y2:"9",key:"4lhtct"}],["line",{x1:"4",x2:"20",y1:"15",y2:"15",key:"vyu0kd"}],["line",{x1:"10",x2:"8",y1:"3",y2:"21",key:"1ggp8o"}],["line",{x1:"16",x2:"14",y1:"3",y2:"21",key:"weycgp"}]]};up.node;const Qx=Ue(up);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const dp={name:"layout-grid",size:24,node:[["rect",{width:"7",height:"7",x:"3",y:"3",rx:"1",key:"1g98yp"}],["rect",{width:"7",height:"7",x:"14",y:"3",rx:"1",key:"6d4xhi"}],["rect",{width:"7",height:"7",x:"14",y:"14",rx:"1",key:"nxv5o0"}],["rect",{width:"7",height:"7",x:"3",y:"14",rx:"1",key:"1bb6yr"}]]};dp.node;const mc=Ue(dp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const hp={name:"lock-keyhole",size:24,node:[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]]};hp.node;const Jx=Ue(hp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const mp={name:"log-out",size:24,node:[["path",{d:"m16 17 5-5-5-5",key:"1bji2h"}],["path",{d:"M21 12H9",key:"dn1m92"}],["path",{d:"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4",key:"1uf3rs"}]]};mp.node;const Zx=Ue(mp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const fp={name:"menu",size:24,node:[["path",{d:"M4 5h16",key:"1tepv9"}],["path",{d:"M4 12h16",key:"1lakjw"}],["path",{d:"M4 19h16",key:"1djgab"}]]};fp.node;const ew=Ue(fp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const pp={name:"message-circle",size:24,node:[["path",{d:"M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719",key:"1sd12s"}]]};pp.node;const tw=Ue(pp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const gp={name:"minus",size:24,node:[["path",{d:"M5 12h14",key:"1ays0h"}]]};gp.node;const nw=Ue(gp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const yp={name:"plus",size:24,node:[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"M12 5v14",key:"s699le"}]]};yp.node;const sw=Ue(yp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const vp={name:"search",size:24,node:[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]]};vp.node;const rw=Ue(vp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const xp={name:"settings",size:24,node:[["path",{d:"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915",key:"1i5ecw"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]]};xp.node;const Qi=Ue(xp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const wp={name:"shield",size:24,node:[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}]]};wp.node;const Ul=Ue(wp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const bp={name:"sparkles",size:24,node:[["path",{d:"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",key:"1s2grr"}],["path",{d:"M20 2v4",key:"1rf3ol"}],["path",{d:"M22 4h-4",key:"gwowj6"}],["circle",{cx:"4",cy:"20",r:"2",key:"6kqj1y"}]],aliases:["stars"]};bp.node;const Ji=Ue(bp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kp={name:"terminal",size:24,node:[["path",{d:"M12 19h8",key:"baeox8"}],["path",{d:"m4 17 6-6-6-6",key:"1yngyt"}]]};kp.node;const iw=Ue(kp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jp={name:"users",size:24,node:[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["path",{d:"M16 3.128a4 4 0 0 1 0 7.744",key:"16gr8j"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}]]};jp.node;const fc=Ue(jp);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Sp={name:"x",size:24,node:[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]]};Sp.node;const aw=Ue(Sp),ow={arrow:Xx,grid:mc,terminal:iw,chart:aa,shield:Ul,spark:Ji,users:fc,settings:Qi,book:Mm,external:Yx,menu:ew,message:tw,close:aw,minus:nw,plus:sw,lock:Jx,logout:Zx,search:rw,doc:Mm,utility:Qi,icon_home:mc,icon_settings:Qi,icon_economy:aa,icon_leveling:aa,icon_moderation:Ul,icon_automod:Ul,icon_heart:Ji,icon_utility:Qi,icon_bot:fc,icon_ai:Ji,icon_lightbulb:Ji};function J({name:t,size:s,className:i=""}){const o=ow[t]||mc;return r.jsx(o,{className:`icon ${i}`.trim(),"aria-hidden":"true",focusable:"false",strokeWidth:1.8,style:s?{width:s,height:s}:void 0})}const Em=[{label:"Home",path:"/",page:"home"},{label:"Commands",path:"/commands",page:"commands"},{label:"Docs",path:"/docs",page:"docs"},{label:"Team",path:"/team",page:"team"},{label:"Changelog",path:"/changelog",page:"changelog"}];function ze({page:t}){const s=rs(),i=t==="dashboard",[o,c]=P.useState(!1),d=h=>f=>{f.preventDefault(),c(!1),he(h)};return r.jsxs("header",{className:`site-header${i?" dashboard-header":""}`,children:[r.jsx(rp,{onNavigate:()=>c(!1)}),!i&&r.jsx("nav",{className:"site-nav","aria-label":"Main navigation",children:Em.map(h=>r.jsx("a",{className:t===h.page?"active":"","aria-current":t===h.page?"page":void 0,href:h.path,onClick:d(h.path),children:h.label},h.path))}),r.jsx("div",{className:"header-actions",children:i?r.jsxs("div",{className:"dashboard-menu",children:[r.jsxs("button",{className:"button button-small button-muted dashboard-menu-trigger",type:"button","aria-expanded":o,"aria-controls":"dashboard-navigation-menu",onClick:()=>c(h=>!h),children:[r.jsx(J,{name:o?"close":"menu"}),r.jsx("span",{children:"Menu"})]}),o&&r.jsxs("nav",{id:"dashboard-navigation-menu",className:"dashboard-menu-popover","aria-label":"Dashboard navigation",children:[r.jsx("span",{className:"dashboard-menu-label",children:"Navigate"}),Em.map(h=>r.jsx("a",{href:h.path,onClick:d(h.path),children:h.label},h.path)),r.jsx("a",{className:"dashboard-menu-current",href:"/dashboard","aria-current":"page",onClick:d("/dashboard"),children:"Dashboard"})]})]}):r.jsxs(r.Fragment,{children:[r.jsxs("a",{className:"button button-small button-muted dashboard-link",href:"/dashboard",onClick:d("/dashboard"),children:["Dashboard ",r.jsx(J,{name:"arrow"})]}),r.jsx("a",{className:"button button-small button-primary",href:(s==null?void 0:s.invite_url)||"#",target:"_blank",rel:"noreferrer",children:"Add to Discord"})]})})]})}const Am=typeof navigator<"u"?(navigator.language||"en").slice(0,2):"en";function pc(t){const s=t.description;if(typeof s=="string")return s;if(s&&typeof s=="object"){const i=s;if(i[Am])return i[Am];if(i.en)return i.en;const o=Object.values(i).find(c=>typeof c=="string"&&c.length>0);if(o)return o}return"A Niko command for your server."}const lw=[{value:"all",label:"All commands"},{value:"slash",label:"Slash"},{value:"prefix",label:"Prefix"},{value:"hybrid",label:"Hybrid"},{value:"context",label:"Context menus"}],ga={slash:"Slash command",prefix:"Prefix command",hybrid:"Hybrid command",context:"Context menu"};function Yn(t){return t.type&&t.type in ga?t.type:"slash"}function cw(t){return t.context_type==="user"?"Right-click a user":"Right-click a message"}function Np(t){const s=Yn(t);return s==="slash"?r.jsxs("code",{children:["/",t.name]}):s==="prefix"?r.jsxs("code",{children:[".",t.name]}):s==="hybrid"?r.jsxs(r.Fragment,{children:[r.jsxs("code",{children:["/",t.name]}),r.jsx("span",{className:"command-or",children:"or"}),r.jsxs("code",{children:[".",t.name]})]}):r.jsxs("code",{className:"context-invocation",children:[cw(t)," · ",t.name]})}function _m(t){return t!=null&&t.length?t:["Not specified"]}function uw({command:t,onClose:s}){P.useEffect(()=>{const h=f=>{f.key==="Escape"&&s()};return document.addEventListener("keydown",h),()=>document.removeEventListener("keydown",h)},[s]);const i=t.parameters||[],o=t.subcommands||[],c=_m(t.aliases),d=_m(t.permissions);return r.jsx("div",{className:"command-dialog-backdrop",role:"presentation",onMouseDown:h=>{h.currentTarget===h.target&&s()},children:r.jsxs("section",{className:"command-dialog",role:"dialog","aria-modal":"true","aria-labelledby":"command-dialog-title",children:[r.jsxs("header",{className:"command-dialog-header",children:[r.jsxs("div",{children:[r.jsxs("div",{className:"command-dialog-kicker",children:[t.category," · ",ga[Yn(t)]]}),r.jsx("h2",{id:"command-dialog-title",children:Np(t)})]}),r.jsx("button",{className:"dialog-close",type:"button",onClick:s,"aria-label":"Close command details",title:"Close command details",children:r.jsx(J,{name:"close"})})]}),r.jsxs("div",{className:"command-dialog-body",children:[r.jsx("p",{className:"command-dialog-description",children:pc(t)}),r.jsxs("div",{className:"command-detail-grid",children:[r.jsxs("section",{className:"command-detail-section command-detail-wide",children:[r.jsx("h3",{children:"Usage"}),r.jsx("code",{className:"command-usage",children:t.usage||`${Yn(t)==="context"?t.name:`/${t.name}`}`})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Permissions"}),r.jsx("ul",{className:"command-detail-list",children:d.map(h=>r.jsx("li",{children:h},h))})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Aliases"}),r.jsx("ul",{className:"command-detail-list",children:c.map(h=>r.jsx("li",{children:r.jsx("code",{children:h==="Not specified"?h:`.${h}`})},h))})]})]}),!!i.length&&r.jsxs("section",{className:"command-detail-section command-parameters",children:[r.jsx("h3",{children:"Parameters"}),r.jsx("div",{className:"command-parameter-list",children:i.map(h=>r.jsxs("div",{className:"command-parameter",children:[r.jsxs("div",{className:"command-parameter-title",children:[r.jsx("code",{children:h.name}),r.jsxs("span",{children:[h.required?"Required":"Optional"," · ",h.type]})]}),r.jsx("p",{children:h.description||"No description provided."})]},h.name))})]}),!!o.length&&r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Subcommands"}),r.jsx("div",{className:"subcommand-list",children:o.map(h=>r.jsxs("code",{children:[t.name," ",h]},h))})]})]}),r.jsxs("footer",{className:"command-dialog-footer",children:[r.jsx("span",{children:"Command registry details are generated from the live bot."}),r.jsx("button",{className:"button button-primary button-small",type:"button",onClick:s,children:"Done"})]})]})})}function dw(){const[t,s]=P.useState([]),[i,o]=P.useState(null),[c,d]=P.useState(""),[h,f]=P.useState("all"),[p,v]=P.useState("all"),[g,x]=P.useState(!0),[w,j]=P.useState("");P.useEffect(()=>{Rx().then(s).catch(()=>j("The command registry is unavailable right now.")).finally(()=>x(!1))},[]),P.useEffect(()=>{if(!i)return;const N=document.body.style.overflow;return document.body.style.overflow="hidden",()=>{document.body.style.overflow=N}},[i]);const k=P.useMemo(()=>["all",...Array.from(new Set(t.map(N=>N.category))).sort()],[t]),S=t.filter(N=>{const B=`${N.name} ${pc(N)} ${N.category} ${ga[Yn(N)]} ${N.context_type||""} ${(N.aliases||[]).join(" ")}`.toLowerCase();return(p==="all"||Yn(N)===p)&&(h==="all"||N.category===h)&&B.includes(c.trim().toLowerCase())});return r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"commands"}),r.jsxs("main",{className:"shell page-main",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Reference library"}),r.jsxs("h1",{children:["Everything Niko",r.jsx("br",{}),r.jsx("em",{children:"knows how to do."})]}),r.jsx("p",{children:"Browse slash, prefix, hybrid, and context commands from the live bot registry. Select any command for permissions, aliases, parameters, usage, and subcommands."})]}),r.jsxs("div",{className:"command-toolbar",children:[r.jsxs("label",{className:"search-field",children:[r.jsx("span",{"aria-hidden":"true",children:"⌕"}),r.jsx("input",{value:c,onChange:N=>d(N.target.value),placeholder:"Search commands","aria-label":"Search commands"})]}),r.jsxs("div",{className:"command-filters",children:[r.jsx("div",{className:"filter-list","aria-label":"Command types",children:lw.map(N=>r.jsx("button",{type:"button",className:p===N.value?"filter active":"filter","aria-pressed":p===N.value,onClick:()=>v(N.value),children:N.label},N.value))}),r.jsx("div",{className:"filter-list","aria-label":"Command categories",children:k.map(N=>r.jsx("button",{type:"button",className:h===N?"filter active":"filter","aria-pressed":h===N,onClick:()=>f(N),children:N==="all"?"All categories":N},N))})]})]}),r.jsxs("div",{className:"command-meta",children:[r.jsx("strong",{children:g?"…":S.length})," commands ",r.jsx("span",{children:"·"})," live bot registry ",r.jsx("span",{children:"·"})," select a card for details"]}),w&&r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Could not load commands"}),r.jsx("span",{children:w})]}),r.jsxs("div",{className:"commands-grid",children:[S.map(N=>r.jsxs("button",{className:"command-card",type:"button",onClick:()=>o(N),"aria-label":`View details for ${N.name}`,children:[r.jsxs("span",{className:"command-card-head",children:[r.jsx("span",{className:"command-name",children:Np(N)}),r.jsx("span",{className:"command-type",children:ga[Yn(N)]})]}),r.jsx("span",{className:"command-card-description",children:pc(N)}),r.jsxs("span",{className:"command-card-footer",children:[r.jsx("span",{className:"category-tag",children:N.category}),r.jsxs("span",{className:"command-expand",children:[r.jsx("span",{children:"Details"}),r.jsx(J,{name:"arrow",size:14})]})]})]},`${Yn(N)}-${N.context_type||""}-${N.category}-${N.name}`)),!g&&!w&&!S.length&&r.jsx("div",{className:"empty-state",children:"No commands match that search."})]})]}),r.jsx(St,{}),i&&r.jsx(uw,{command:i,onClose:()=>o(null)})]})}function ye(t){return t==null?"—":new Intl.NumberFormat("en-US",{notation:t>9999?"compact":"standard"}).format(t)}function Cp(t){return(t==null?void 0:t.global_name)||(t==null?void 0:t.username)||"there"}function Tp(t){return t.split(/\s+/).map(s=>s[0]).join("").slice(0,2).toUpperCase()}function Uc({guild:t,className:s="guild-avatar"}){return r.jsx("span",{className:s,"aria-hidden":"true",children:t.icon_url?r.jsx("img",{src:t.icon_url,alt:""}):t.name.slice(0,1).toUpperCase()})}function Pp({user:t,className:s="avatar"}){const i=t.avatar?`https://cdn.discordapp.com/avatars/${t.id}/${t.avatar}.${t.avatar.startsWith("a_")?"gif":"png"}?size=64`:null;return r.jsx("span",{className:s,"aria-hidden":"true",children:i?r.jsx("img",{src:i,alt:""}):Tp(t.global_name||t.username||"Niko")})}function hw({name:t,avatarUrl:s,className:i="member-avatar"}){return r.jsx("span",{className:i,"aria-hidden":"true",children:s?r.jsx("img",{src:s,alt:""}):Tp(t)})}const mw=[["overview","Overview","grid","At a glance"],["leveling","Leveling","spark","Reward participation"],["moderation","Moderation","shield","Keep things steady"],["server","Server","settings","Manage server features"],["ai","AI controls","settings","Shape Niko’s voice"],["customization","Customization","paint","Niko’s server identity"]];function Mp({user:t,guilds:s,selectedGuild:i,view:o,section:c,stats:d,onHome:h,onServers:f,onGuildChange:p,onSectionChange:v,onRefresh:g,refreshing:x,staffRole:w,children:j}){const k=s.filter(E=>E.installed!==!1),S=(E=!1)=>r.jsx("nav",{className:E?"dash-nav dash-nav-mobile":"dash-nav","aria-label":"Server settings",children:mw.map(([R,I,D])=>r.jsxs("button",{className:o==="guild"&&c===R?"active":"","aria-current":o==="guild"&&c===R?"page":void 0,onClick:()=>v(R),children:[r.jsx(J,{name:D}),r.jsx("span",{children:I})]},R))}),N=(E=!1)=>r.jsxs("nav",{className:E?"dash-nav dash-primary-nav dash-nav-mobile":"dash-nav dash-primary-nav","aria-label":"Dashboard",children:[r.jsxs("button",{className:o==="overview"?"active":"","aria-current":o==="overview"?"page":void 0,onClick:h,children:[r.jsx(J,{name:"grid"}),r.jsx("span",{children:"My overview"})]}),r.jsxs("button",{className:o==="servers"?"active":"","aria-current":o==="servers"?"page":void 0,onClick:f,children:[r.jsx(J,{name:"users"}),r.jsx("span",{children:"My servers"})]}),w&&r.jsxs("button",{onClick:()=>he("/dashboard/staff"),children:[r.jsx(J,{name:"shield"}),r.jsx("span",{children:"Staff workspace"})]})]}),B=()=>r.jsxs("div",{className:"dash-top-actions",children:[o==="guild"?r.jsxs("label",{className:"guild-switcher",children:[r.jsx("span",{className:"sr-only",children:"Switch server"}),r.jsxs("select",{value:(i==null?void 0:i.id)||"",onChange:E=>{const R=k.find(I=>I.id===E.target.value);R&&p(R)},children:[r.jsx("option",{value:"",disabled:!0,children:"Switch server"}),k.map(E=>r.jsx("option",{value:E.id,children:E.name},E.id))]})]}):r.jsxs("button",{className:"button button-muted button-small top-action",onClick:f,children:[r.jsx(J,{name:"users"})," Browse servers"]}),r.jsxs("button",{className:"button button-muted button-small top-action refresh-action",onClick:g,disabled:x,"aria-label":"Refresh dashboard data",children:[r.jsx(J,{name:"spark"})," ",x?"Refreshing…":"Refresh data"]}),o==="guild"&&r.jsxs("span",{className:"connection-chip",children:[r.jsx("span",{className:"status-dot"})," Connected"]}),r.jsxs("div",{className:"user-pill",children:[r.jsx(Pp,{user:t}),r.jsx("span",{children:Cp(t)})]}),r.jsx("a",{className:"logout-button",href:"/auth/logout","aria-label":"Log out",title:"Log out",children:r.jsx(J,{name:"logout"})})]});return r.jsxs("div",{className:"dashboard-layout",children:[r.jsxs("aside",{className:"dash-sidebar",children:[r.jsx("div",{className:"dash-mobile-controls",children:B()}),r.jsxs("div",{className:"side-rail-heading",children:[r.jsx("span",{className:"side-label",children:"Workspace"}),r.jsxs("span",{className:"rail-status",children:[r.jsx("span",{className:"status-dot"})," Live"]})]}),N(),o==="guild"&&i&&r.jsxs(r.Fragment,{children:[r.jsx("div",{className:"side-label side-label-settings",children:"Current server"}),r.jsxs("div",{className:"side-guild",children:[r.jsx(Uc,{guild:i}),r.jsxs("span",{children:[r.jsx("strong",{children:i.name}),r.jsx("small",{children:"Live configuration"})]}),r.jsx("span",{className:"guild-presence",title:"Niko is connected",children:r.jsx("span",{className:"status-dot"})})]}),r.jsxs("div",{className:"side-settings-caption",children:[r.jsx("span",{children:"Settings map"}),r.jsx("small",{children:"Pick a room to tune"})]}),S()]}),r.jsxs("div",{className:"sidebar-bottom",children:[r.jsxs("span",{className:"online-label",children:[r.jsx("span",{className:"status-dot"})," Niko is online"]}),r.jsxs("small",{children:[ye(d==null?void 0:d.guild_count)," connected servers · v",(d==null?void 0:d.version)||"1.0"]}),r.jsxs("a",{href:"/",onClick:E=>{E.preventDefault(),he("/")},children:["Back to public site ",r.jsx(J,{name:"arrow"})]})]})]}),r.jsxs("div",{className:"dash-content",children:[r.jsx(ze,{page:"dashboard"}),r.jsx("div",{className:"dash-contextbar",children:B()}),r.jsx("div",{className:"mobile-primary-bar",children:N(!0)}),o==="guild"&&r.jsx("div",{className:"mobile-section-bar",children:S(!0)}),r.jsx("main",{className:"dash-main",children:j})]})]})}const Ep=P.createContext({});function fw(t){const s=P.useRef(null);return s.current===null&&(s.current=t()),s.current}const pw=typeof window<"u",gw=pw?P.useLayoutEffect:P.useEffect,Wc=P.createContext(null);function $c(t,s){t.indexOf(s)===-1&&t.push(s)}function ya(t,s){const i=t.indexOf(s);i>-1&&t.splice(i,1)}const Ut=(t,s,i)=>i>s?s:i<t?t:i;let Da=()=>{};const ln={},Hc=t=>/^-?(?:\d+(?:\.\d+)?|\.\d+)$/u.test(t),Ap=t=>typeof t=="object"&&t!==null,Gc=t=>/^0[^.\s]+$/u.test(t);function _p(t){let s;return()=>(s===void 0&&(s=t()),s)}const zt=t=>t,Ir=(...t)=>t.reduce((s,i)=>o=>i(s(o))),Ar=(t,s,i)=>{const o=s-t;return o?(i-t)/o:1};class va{constructor(){this.subscriptions=[]}add(s){return $c(this.subscriptions,s),()=>this.remove(s)}remove(s){ya(this.subscriptions,s)}notify(s,i,o){const c=this.subscriptions.length;if(c)if(c===1)this.subscriptions[0](s,i,o);else for(let d=0;d<c;d++){const h=this.subscriptions[d];h&&h(s,i,o)}}getSize(){return this.subscriptions.length}clear(){this.subscriptions.length=0}}const At=t=>t*1e3,kt=t=>t/1e3,Dp=(t,s)=>s?t*(1e3/s):0,Rp=(t,s,i)=>(((1-3*i+3*s)*t+(3*i-6*s))*t+3*s)*t,yw=1e-7,vw=12;function xw(t,s,i,o,c){let d,h,f=0;do h=s+(i-s)/2,d=Rp(h,o,c)-t,d>0?i=h:s=h;while(Math.abs(d)>yw&&++f<vw);return h}function Vr(t,s,i,o){if(t===s&&i===o)return zt;const c=d=>xw(d,0,1,t,i);return d=>d===0||d===1?d:Rp(c(d),s,o)}const Lp=t=>s=>s<=.5?t(2*s)/2:(2-t(2*(1-s)))/2,Ip=t=>s=>1-t(1-s),Vp=Vr(.33,1.53,.69,.99),Kc=Ip(Vp),Fp=Lp(Kc),Bp=t=>t>=1?1:(t*=2)<1?.5*Kc(t):.5*(2-Math.pow(2,-10*(t-1))),qc=t=>1-Math.sin(Math.acos(t)),Op=Ip(qc),zp=Lp(qc),ww=Vr(.42,0,1,1),bw=Vr(0,0,.58,1),Up=Vr(.42,0,.58,1),kw=t=>Array.isArray(t)&&typeof t[0]!="number",Wp=t=>Array.isArray(t)&&typeof t[0]=="number",jw={linear:zt,easeIn:ww,easeInOut:Up,easeOut:bw,circIn:qc,circInOut:zp,circOut:Op,backIn:Kc,backInOut:Fp,backOut:Vp,anticipate:Bp},Sw=t=>typeof t=="string",Dm=t=>{if(Wp(t)){Da(t.length===4);const[s,i,o,c]=t;return Vr(s,i,o,c)}else if(Sw(t))return jw[t];return t},Zi=["setup","read","resolveKeyframes","preUpdate","update","preRender","render","postRender"];function Nw(t){let s=new Set,i=new Set,o=!1,c=!1;const d=new Set;let h={delta:0,timestamp:0,isProcessing:!1};function f(v){d.has(v)&&(i.add(v),t()),v(h)}const p={schedule:(v,g=!1,x=!1)=>{const j=x&&o?s:i;return g&&d.add(v),j.add(v),v},cancel:v=>{i.delete(v),d.delete(v)},process:v=>{if(h=v,o){c=!0;return}o=!0;const g=s;s=i,i=g,s.forEach(f),s.clear(),o=!1,c&&(c=!1,p.process(v))}};return p}const Cw=40;function $p(t,s){let i=!1,o=!0;const c={delta:0,timestamp:0,isProcessing:!1},d=()=>i=!0,h=Zi.reduce((R,I)=>(R[I]=Nw(d),R),{}),{setup:f,read:p,resolveKeyframes:v,preUpdate:g,update:x,preRender:w,render:j,postRender:k}=h,S=()=>{const R=ln.useManualTiming,I=R?c.timestamp:performance.now();i=!1,R||(c.delta=o?1e3/60:Math.max(Math.min(I-c.timestamp,Cw),1)),c.timestamp=I,c.isProcessing=!0,f.process(c),p.process(c),v.process(c),g.process(c),x.process(c),w.process(c),j.process(c),k.process(c),c.isProcessing=!1,i&&s&&(o=!1,t(S))},N=()=>{i=!0,o=!0,c.isProcessing||t(S)};return{schedule:Zi.reduce((R,I)=>{const D=h[I];return R[I]=(F,V=!1,z=!1)=>(i||N(),D.schedule(F,V,z)),R},{}),cancel:R=>{for(let I=0;I<Zi.length;I++)h[Zi[I]].cancel(R)},state:c,steps:h}}const{schedule:je,cancel:En,state:Ge,steps:Wl}=$p(typeof requestAnimationFrame<"u"?requestAnimationFrame:zt,!0);let oa;function Tw(){oa=void 0}const it={now:()=>(oa===void 0&&it.set(Ge.isProcessing||ln.useManualTiming?Ge.timestamp:performance.now()),oa),set:t=>{oa=t,queueMicrotask(Tw)}},Ls=t=>Math.round(t*1e5)/1e5,Hp=t=>s=>typeof s=="string"&&s.startsWith(t),Gp=Hp("--"),Pw=Hp("var(--"),Xc=t=>Pw(t)?Mw.test(t.split("/*")[0].trim()):!1,Mw=/var\(--(?:[\w-]+\s*|[\w-]+\s*,(?:\s*[^)(\s]|\s*\((?:[^)(]|\([^)(]*\))*\))+\s*)\)$/iu;function Rm(t){return typeof t!="string"?!1:t.split("/*")[0].includes("var(--")}const Vs={test:t=>typeof t=="number",parse:parseFloat,transform:t=>t},_r={...Vs,transform:t=>Ut(0,1,t)},ea={...Vs,default:1},Yc=/-?(?:\d+(?:\.\d+)?|\.\d+)/gu;function Ew(t){return t==null}const Aw=/^(?:#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\))$/iu,Qc=(t,s)=>i=>!!(typeof i=="string"&&Aw.test(i)&&i.startsWith(t)||s&&!Ew(i)&&Object.prototype.hasOwnProperty.call(i,s)),Kp=(t,s,i)=>o=>{if(typeof o!="string")return o;const[c,d,h,f]=o.match(Yc);return{[t]:parseFloat(c),[s]:parseFloat(d),[i]:parseFloat(h),alpha:f!==void 0?parseFloat(f):1}},_w=t=>Ut(0,255,t),$l={...Vs,transform:t=>Math.round(_w(t))},Qn={test:Qc("rgb","red"),parse:Kp("red","green","blue"),transform:({red:t,green:s,blue:i,alpha:o=1})=>"rgba("+$l.transform(t)+", "+$l.transform(s)+", "+$l.transform(i)+", "+Ls(_r.transform(o))+")"};function Dw(t){let s="",i="",o="",c="";return t.length>5?(s=t.substring(1,3),i=t.substring(3,5),o=t.substring(5,7),c=t.substring(7,9)):(s=t.substring(1,2),i=t.substring(2,3),o=t.substring(3,4),c=t.substring(4,5),s+=s,i+=i,o+=o,c+=c),{red:parseInt(s,16),green:parseInt(i,16),blue:parseInt(o,16),alpha:c?parseInt(c,16)/255:1}}const gc={test:Qc("#"),parse:Dw,transform:Qn.transform},Fr=t=>({test:s=>typeof s=="string"&&s.endsWith(t)&&s.split(" ").length===1,parse:parseFloat,transform:s=>`${s}${t}`}),on=Fr("deg"),Qt=Fr("%"),ee=Fr("px"),Rw=Fr("vh"),Lw=Fr("vw"),Lm={...Qt,parse:t=>Qt.parse(t)/100,transform:t=>Qt.transform(t*100)},_s={test:Qc("hsl","hue"),parse:Kp("hue","saturation","lightness"),transform:({hue:t,saturation:s,lightness:i,alpha:o=1})=>"hsla("+Math.round(t)+", "+Qt.transform(Ls(s))+", "+Qt.transform(Ls(i))+", "+Ls(_r.transform(o))+")"},Ke={test:t=>Qn.test(t)||gc.test(t)||_s.test(t),parse:t=>Qn.test(t)?Qn.parse(t):_s.test(t)?_s.parse(t):gc.parse(t),transform:t=>typeof t=="string"?t:t.hasOwnProperty("red")?Qn.transform(t):_s.transform(t),getAnimatableNone:t=>{const s=Ke.parse(t);return s.alpha=0,Ke.transform(s)}},Iw=/(?:#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\))/giu,qp=new RegExp(Yc.source),Xp=new RegExp(Iw.source,"i");function Vw(t){return isNaN(t)&&typeof t=="string"&&(qp.test(t)||Xp.test(t))}const Yp="number",Qp="color",Fw="var",Bw="var(",Im="${}",Ow=/var\s*\(\s*--(?:[\w-]+\s*|[\w-]+\s*,(?:\s*[^)(\s]|\s*\((?:[^)(]|\([^)(]*\))*\))+\s*)\)|#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\)|-?(?:\d+(?:\.\d+)?|\.\d+)/giu;function zw(t){const s=t.toString();return qp.test(s)||Xp.test(s)}function Dr(t){const s=t.toString(),i=[],o={color:[],number:[],var:[]},c=[];let d=0;const f=s.replace(Ow,p=>(Ke.test(p)?(o.color.push(d),c.push(Qp),i.push(Ke.parse(p))):p.startsWith(Bw)?(o.var.push(d),c.push(Fw),i.push(p)):(o.number.push(d),c.push(Yp),i.push(parseFloat(p))),++d,Im)).split(Im);return{values:i,split:f,indexes:o,types:c}}function Uw(t){return Dr(t).values}function Jp({split:t,types:s}){const i=t.length;return o=>{let c="";for(let d=0;d<i;d++)if(c+=t[d],o[d]!==void 0){const h=s[d];h===Yp?c+=Ls(o[d]):h===Qp?c+=Ke.transform(o[d]):c+=o[d]}return c}}function Ww(t){return Jp(Dr(t))}const $w=t=>typeof t=="number"?0:Ke.test(t)?Ke.getAnimatableNone(t):t,Hw=(t,s)=>typeof t=="number"?s!=null&&s.trim().endsWith("/")?t:0:$w(t);function Gw(t){const s=Dr(t);return Jp(s)(s.values.map((o,c)=>Hw(o,s.split[c])))}const jt={test:Vw,parse:Uw,createTransformer:Ww,getAnimatableNone:Gw};function Hl(t,s,i){return i<0&&(i+=1),i>1&&(i-=1),i<1/6?t+(s-t)*6*i:i<1/2?s:i<2/3?t+(s-t)*(2/3-i)*6:t}function Kw({hue:t,saturation:s,lightness:i,alpha:o}){t/=360,s/=100,i/=100;let c=0,d=0,h=0;if(!s)c=d=h=i;else{const f=i<.5?i*(1+s):i+s-i*s,p=2*i-f;c=Hl(p,f,t+1/3),d=Hl(p,f,t),h=Hl(p,f,t-1/3)}return{red:Math.round(c*255),green:Math.round(d*255),blue:Math.round(h*255),alpha:o}}function xa(t,s){return i=>i>0?s:t}const ke=(t,s,i)=>t+(s-t)*i,Gl=(t,s,i)=>{const o=t*t,c=i*(s*s-o)+o;return c<0?0:Math.sqrt(c)},qw=[gc,Qn,_s],Xw=t=>qw.find(s=>s.test(t));function Vm(t){const s=Xw(t);if(!s)return!1;let i=s.parse(t);return s===_s&&(i=Kw(i)),i}const Fm=(t,s)=>{const i=Vm(t),o=Vm(s);if(!i||!o)return xa(t,s);const c={...i};return d=>(c.red=Gl(i.red,o.red,d),c.green=Gl(i.green,o.green,d),c.blue=Gl(i.blue,o.blue,d),c.alpha=ke(i.alpha,o.alpha,d),Qn.transform(c))},yc=new Set(["none","hidden"]);function Yw(t,s){return yc.has(t)?i=>i<=0?t:s:i=>i>=1?s:t}function Qw(t,s){return i=>ke(t,s,i)}function Jc(t){return typeof t=="number"?Qw:typeof t=="string"?Xc(t)?xa:Ke.test(t)?Fm:eb:Array.isArray(t)?Zp:typeof t=="object"?Ke.test(t)?Fm:Jw:xa}function Zp(t,s){const i=[...t],o=i.length,c=t.map((d,h)=>Jc(d)(d,s[h]));return d=>{for(let h=0;h<o;h++)i[h]=c[h](d);return i}}function Jw(t,s){const i={...t,...s},o={};for(const c in i)t[c]!==void 0&&s[c]!==void 0&&(o[c]=Jc(t[c])(t[c],s[c]));return c=>{for(const d in o)i[d]=o[d](c);return i}}function Zw(t,s){const i=[],o={color:0,var:0,number:0};for(let c=0;c<s.values.length;c++){const d=s.types[c],h=t.indexes[d][o[d]],f=t.values[h]??0;i[c]=f,o[d]++}return i}const eb=(t,s)=>{const i=jt.createTransformer(s),o=Dr(t),c=Dr(s);return o.indexes.var.length===c.indexes.var.length&&o.indexes.color.length===c.indexes.color.length&&o.indexes.number.length>=c.indexes.number.length?yc.has(t)&&!c.values.length||yc.has(s)&&!o.values.length?Yw(t,s):Ir(Zp(Zw(o,c),c.values),i):xa(t,s)},Bm=/^(-?(?:\d+(?:\.\d*)?|\.\d+))([a-z%]*)$/iu;function tb(t,s){const i=Bm.exec(t);if(!i)return;const o=Bm.exec(s);if(!o||i[2]!==o[2])return;const c=i[2],d=parseFloat(i[1]),h=parseFloat(o[1]);return f=>Ls(ke(d,h,f))+c}function Zc(t,s,i){if(typeof t=="number"&&typeof s=="number"&&typeof i=="number")return ke(t,s,i);if(typeof t=="string"&&typeof s=="string"){const c=tb(t,s);if(c)return c}return Jc(t)(t,s)}const nb=t=>{const s=({timestamp:i})=>t(i);return{start:(i=!0)=>je.update(s,i),stop:()=>En(s),now:()=>Ge.isProcessing?Ge.timestamp:it.now()}},eg=(t,s,i=10)=>{let o="";const c=Math.max(Math.round(s/i),2);for(let d=0;d<c;d++)o+=Math.round(t(d/(c-1))*1e4)/1e4+", ";return`linear(${o.substring(0,o.length-2)})`},eu=2e4;function tu(t,s=50,i=eu,o){let c=0,d=t.next(c);for(;!d.done&&c<i;)c+=s,d=t.next(c);return c>=i?1/0:c}function sb(t,s=100,i){const o=i({...t,keyframes:[0,s]}),c=Math.min(tu(o),eu);return{type:"keyframes",ease:d=>o.next(c*d).value/s,duration:kt(c)}}const Le={stiffness:100,damping:10,mass:1,velocity:0,duration:800,bounce:.3,visualDuration:.3,restSpeed:{granular:.01,default:2},restDelta:{granular:.005,default:.5},minDuration:.01,maxDuration:10,minDamping:.05,maxDamping:1};function vc(t,s){return t*Math.sqrt(1-s*s)}const rb=12;function ib(t,s,i){let o=i;for(let c=1;c<rb;c++)o=o-t(o)/s(o);return o}const Kl=.001;function ab({duration:t=Le.duration,bounce:s=Le.bounce,velocity:i=Le.velocity,mass:o=Le.mass}){let c,d,h=1-s;h=Ut(Le.minDamping,Le.maxDamping,h),t=Ut(Le.minDuration,Le.maxDuration,kt(t)),h<1?(c=v=>{const g=v*h,x=g*t,w=g-i,j=vc(v,h),k=Math.exp(-x);return Kl-w/j*k},d=v=>{const x=v*h*t,w=x*i+i,j=h*h*v*v*t,k=Math.exp(-x),S=vc(v*v,h);return(-c(v)+Kl>0?-1:1)*((w-j)*k)/S}):(c=v=>{const g=Math.exp(-v*t),x=(v-i)*t+1;return-Kl+g*x},d=v=>{const g=Math.exp(-v*t),x=(i-v)*(t*t);return g*x});const f=5/t,p=ib(c,d,f);if(t=At(t),isNaN(p))return{stiffness:Le.stiffness,damping:Le.damping,duration:t};{const v=p*p*o;return{stiffness:v,damping:h*2*Math.sqrt(o*v),duration:t}}}const tg=["duration","bounce"],ng=["stiffness","damping","mass"];function wa(t,s){return s.some(i=>t[i]!==void 0)}function ob(t){let s={velocity:Le.velocity,stiffness:Le.stiffness,damping:Le.damping,mass:Le.mass,isResolvedFromDuration:!1,...t};if(!wa(t,ng)&&wa(t,tg))if(s.velocity=0,t.visualDuration){const i=t.visualDuration,o=2*Math.PI/(i*1.2),c=o*o,d=2*Ut(.05,1,1-(t.bounce||0))*Math.sqrt(c);s={...s,mass:Le.mass,stiffness:c,damping:d}}else{const i=ab({...t,velocity:0});s={...s,...i,mass:Le.mass},s.isResolvedFromDuration=!0}return s}function ba(t=Le.visualDuration,s=Le.bounce){const i=typeof t!="object"?{visualDuration:t,keyframes:[0,1],bounce:s}:t,o=i.keyframes[0],c=i.keyframes[i.keyframes.length-1],d={done:!1,value:o},{stiffness:h,damping:f,mass:p,duration:v,velocity:g,isResolvedFromDuration:x}=ob({...i,velocity:-kt(i.velocity||0)}),w=f/(2*Math.sqrt(h*p)),j=kt(Math.sqrt(h/p)),k=w*j,S={target:c,delta:c-o,velocity:g||0,restSpeed:0,restDelta:0},N=()=>{const V=Math.abs(S.delta)<5;S.restSpeed=i.restSpeed||(V?Le.restSpeed.granular:Le.restSpeed.default),S.restDelta=i.restDelta||(V?Le.restDelta.granular:Le.restDelta.default)};N();let B,E,R;if(w<1){const V=vc(j,w),z={A:0,sinC:0,cosC:0,t:-1,env:0,sin:0,cos:0};R=()=>{z.A=(S.velocity+k*S.delta)/V,z.sinC=k*z.A+S.delta*V,z.cosC=k*S.delta-z.A*V};const oe=le=>{le!==z.t&&(z.t=le,z.env=Math.exp(-k*le),z.sin=Math.sin(V*le),z.cos=Math.cos(V*le))};B=le=>(oe(le),S.target-z.env*(z.A*z.sin+S.delta*z.cos)),E=le=>(oe(le),z.env*(z.sinC*z.sin+z.cosC*z.cos))}else if(w===1){B=z=>S.target-Math.exp(-j*z)*(S.delta+(S.velocity+j*S.delta)*z);const V={C:0};R=()=>{V.C=S.velocity+j*S.delta},E=z=>Math.exp(-j*z)*(j*V.C*z-S.velocity)}else{const V=j*Math.sqrt(w*w-1);B=oe=>{const le=Math.exp(-k*oe),xe=Math.min(V*oe,300);return S.target-le*((S.velocity+k*S.delta)*Math.sinh(xe)+V*S.delta*Math.cosh(xe))/V};const z={P:0,sinh:0,cosh:0};R=()=>{z.P=(S.velocity+k*S.delta)/V,z.sinh=k*z.P-S.delta*V,z.cosh=k*S.delta-z.P*V},E=oe=>{const le=Math.exp(-k*oe),xe=Math.min(V*oe,300);return le*(z.sinh*Math.sinh(xe)+z.cosh*Math.cosh(xe))}}R();const I=!wa(i,ng)&&wa(i,tg),D=x&&v||null,F={calculatedDuration:D,retarget:(V,z)=>{S.target=V[V.length-1],S.delta=S.target-V[0],S.velocity=I?0:-kt(z),i.restSpeed&&i.restDelta||N(),F.calculatedDuration=D,d.done=!1,R()},velocity:V=>At(E(V)),next:V=>{const z=B(V);if(x)d.done=V>=v;else{const oe=At(E(V));d.done=Math.abs(oe)<=S.restSpeed&&Math.abs(S.target-z)<=S.restDelta}return d.value=d.done?S.target:z,d},toString:()=>{const V=Math.min(tu(F),eu),z=eg(oe=>F.next(V*oe).value,V,30);return V+"ms "+z},toTransition:()=>{}};return F}ba.applyToOptions=t=>{const s=sb(t,100,ba);return t.ease=s.ease,t.duration=At(s.duration),t.type="keyframes",t};function xc({keyframes:t,velocity:s=0,power:i=.8,timeConstant:o=325,bounceDamping:c=10,bounceStiffness:d=500,modifyTarget:h,min:f,max:p,restDelta:v=.5,restSpeed:g}){const x=t[0],w={done:!1,value:x},j=V=>V<f||V>p,k=V=>f===void 0?p:p===void 0||Math.abs(f-V)<Math.abs(p-V)?f:p;let S=i*s;const N=x+S,B=h===void 0?N:h(N);B!==N&&(S=B-x);const E=V=>-S*Math.exp(-V/o),R=V=>{const z=E(V);w.done=Math.abs(z)<=v,w.value=w.done?B:B+z};let I,D;const F=V=>{j(w.value)&&(I=V,D=ba({keyframes:[w.value,k(w.value)],velocity:-E(V)/o*1e3,damping:c,stiffness:d,restDelta:v,restSpeed:g}))};return F(0),{calculatedDuration:null,next:V=>{let z=!1;return!D&&I===void 0&&(z=!0,R(V),F(V)),I!==void 0&&V>=I?D.next(V-I):(!z&&R(V),w)}}}function lb(t,s,i){const o=[],c=i||ln.mix||Zc,d=t.length-1;for(let h=0;h<d;h++){let f=c(t[h],t[h+1]);if(s){const p=Array.isArray(s)?s[h]||zt:s;f=Ir(p,f)}o.push(f)}return o}function cb(t,s,{clamp:i=!0,ease:o,mixer:c}={}){const d=t.length;if(Da(d===s.length),d===1)return()=>s[0];if(d===2&&s[0]===s[1])return()=>s[1];const h=t[0]===t[1];t[0]>t[d-1]&&(t=[...t].reverse(),s=[...s].reverse());const f=lb(s,o,c),p=f.length,v=g=>{if(h&&g<t[0])return s[0];let x=0;if(p>1)for(;x<t.length-2&&!(g<t[x+1]);x++);const w=Ar(t[x],t[x+1],g);return f[x](w)};return i?g=>v(Ut(t[0],t[d-1],g)):v}function ub(t,s){const i=t[t.length-1];for(let o=1;o<=s;o++){const c=Ar(0,s,o);t.push(ke(i,1,c))}}function db(t){const s=[0];return ub(s,t.length-1),s}function hb(t,s){return t.map(i=>i*s)}function mb(t,s){return t.map(()=>s||Up).splice(0,t.length-1)}function Pr({duration:t=300,keyframes:s,times:i,ease:o="easeInOut"}){const c=kw(o)?o.map(Dm):Dm(o),d={done:!1,value:s[0]};if(s.length===2&&!Array.isArray(c)&&(!i||i.length!==2||i[0]===0&&i[1]===1)){const[p,v]=s,g=p===v?void 0:(ln.mix||Zc)(p,v);return{calculatedDuration:t,next:x=>(d.value=g?g(c(t>0?Ut(0,1,x/t):1)):v,d.done=x>=t,d)}}const h=hb(i&&i.length===s.length?i:db(s),t),f=cb(h,s,{ease:Array.isArray(c)?c:mb(s,c)});return{calculatedDuration:t,next:p=>(d.value=f(p),d.done=p>=t,d)}}const fb=5;function pb(t,s,i){const o=Math.max(s-fb,0);return Dp(i-t(o),s-o)}function gb(t,s,i=0){return s<=0?i:t.velocity?t.velocity(s):pb(o=>t.next(o).value,s,t.next(s).value)}const yb=t=>t!==null;function Ra(t,{repeat:s,repeatType:i="loop"},o,c=1){const d=t.filter(yb),f=c<0||s&&i!=="loop"&&s%2===1?0:d.length-1;return!f||o===void 0?d[f]:o}const vb={decay:xc,inertia:xc,tween:Pr,keyframes:Pr,spring:ba};function sg(t){typeof t.type=="string"&&(t.type=vb[t.type])}function rg(t,s){return{kind:t,animation:s,timestamp:it.now(),frameTimestamp:Ge.timestamp,frameIsProcessing:Ge.isProcessing}}function ig(t,s,i){const o=globalThis.__MOTION_INSPECT__;if(o)try{o({...rg("animation-start",t),options:i?{...s,...i}:s})}catch{}}function xb(t,s){const i=globalThis.__MOTION_INSPECT__;if(i)try{i({...rg("layout-animation-start",t),node:s})}catch{}}class nu{constructor(){this.isResolved=!1}get finished(){return this._finished||(this._finished=this.isResolved?Promise.resolve():new Promise(s=>{this._resolve=s})),this._finished}updateFinished(){this._finished=this._resolve=void 0,this.isResolved=!1}notifyFinished(){var s;this.isResolved=!0,(s=this._resolve)==null||s.call(this)}then(s,i){return this.finished.then(s,i)}}const wb=t=>t/100;class ka extends nu{constructor(s){super(),this.state="idle",this.startTime=null,this.isStopped=!1,this.currentTime=0,this.holdTime=null,this.playbackSpeed=1,this.delayState={done:!1,value:void 0},this.stop=()=>{var o,c;const{motionValue:i}=this.options;i&&i.updatedAt!==it.now()&&this.tick(it.now()),this.isStopped=!0,this.state!=="idle"&&(this.teardown(),(c=(o=this.options).onStop)==null||c.call(o))},this.options=s,this.initAnimation(),this.play(),s.autoplay===!1&&this.pause(),ig(this,this.options)}initAnimation(){const{options:s}=this;sg(s);const{type:i=Pr,repeat:o=0,repeatDelay:c=0,repeatType:d,velocity:h=0}=s;let{keyframes:f}=s;const p=i||Pr;p!==Pr&&typeof f[0]!="number"&&(this.mixKeyframes=Ir(wb,Zc(f[0],f[1])),f=[0,100]);const v=p(f===s.keyframes?s:{...s,keyframes:f});d==="mirror"&&(this.mirroredGenerator=p({...s,keyframes:[...f].reverse(),velocity:-h})),v.calculatedDuration===null&&(v.calculatedDuration=tu(v));const{calculatedDuration:g}=v;this.calculatedDuration=g,this.resolvedDuration=g+c,this.totalDuration=this.resolvedDuration*(o+1)-c,this.generator=v}updateTime(s){const i=Math.round(s-this.startTime)*this.playbackSpeed;this.holdTime!==null?this.currentTime=this.holdTime:this.currentTime=i}tick(s,i=!1){const{generator:o,totalDuration:c,mixKeyframes:d,mirroredGenerator:h,resolvedDuration:f,calculatedDuration:p}=this;if(this.startTime===null)return o.next(0);const{delay:v=0,keyframes:g,repeat:x,repeatType:w,repeatDelay:j,type:k,onUpdate:S,finalKeyframe:N}=this.options;this.speed>0?this.startTime=Math.min(this.startTime,s):this.speed<0&&(this.startTime=Math.min(s-c/this.speed,this.startTime)),i?this.currentTime=s:this.updateTime(s);const B=this.currentTime-v*(this.playbackSpeed>=0?1:-1),E=this.playbackSpeed>=0?B<0:B>c;this.currentTime=Math.max(B,0),this.state==="finished"&&this.holdTime===null&&(this.currentTime=c);let R=this.currentTime,I=o;if(x){const z=Math.min(this.currentTime,c)/f;let oe=Math.floor(z),le=z%1;!le&&z>=1&&(le=1),le===1&&oe--,oe=Math.min(oe,x+1),!!(oe%2)&&(w==="reverse"?(le=1-le,j&&(le-=j/f)):w==="mirror"&&(I=h)),R=Ut(0,1,le)*f}let D;E?(this.delayState.value=g[0],D=this.delayState):D=I.next(R),d&&!E&&(D.value=d(D.value));let{done:F}=D;!E&&p!==null&&(F=this.playbackSpeed>=0?this.currentTime>=c:this.currentTime<=0);const V=this.holdTime===null&&(this.state==="finished"||this.state==="running"&&F);return V&&k!==xc&&(D.value=Ra(g,this.options,N,this.speed)),S&&S(D.value),V&&this.finish(),D}then(s,i){return this.finished.then(s,i)}get duration(){return kt(this.calculatedDuration)}get iterationDuration(){const{delay:s=0}=this.options||{};return this.duration+kt(s)}get time(){return kt(this.currentTime)}set time(s){s=At(s),this.currentTime=s,this.startTime===null||this.holdTime!==null||this.playbackSpeed===0?this.holdTime=s:this.driver&&(this.startTime=this.driver.now()-s/this.playbackSpeed),this.driver?this.driver.start(!1):(this.startTime=0,this.state="paused",this.holdTime=s,this.tick(s))}getGeneratorVelocity(){return gb(this.generator,this.currentTime,this.options.velocity)}get speed(){return this.playbackSpeed}set speed(s){const i=this.playbackSpeed!==s;i&&this.driver&&this.updateTime(it.now()),this.playbackSpeed=s,i&&this.driver&&(this.time=kt(this.currentTime))}play(){var c,d;if(this.isStopped)return;const{driver:s=nb,startTime:i}=this.options;this.driver||(this.driver=s(h=>this.tick(h))),(d=(c=this.options).onPlay)==null||d.call(c);const o=this.driver.now();this.state==="finished"?(this.updateFinished(),this.startTime=o):this.holdTime!==null?this.startTime=o-this.holdTime:this.startTime||(this.startTime=i??o),this.state==="finished"&&this.speed<0&&(this.startTime+=this.calculatedDuration),this.holdTime=null,this.state="running",this.driver.start()}pause(){this.state="paused",this.updateTime(it.now()),this.holdTime=this.currentTime}complete(){this.state!=="running"&&this.play(),this.state="finished",this.holdTime=null}finish(){var s,i;this.notifyFinished(),this.teardown(),this.state="finished",(i=(s=this.options).onComplete)==null||i.call(s)}cancel(){var s,i;this.holdTime=null,this.startTime=0,this.tick(0),this.teardown(),(i=(s=this.options).onCancel)==null||i.call(s)}teardown(){this.state="idle",this.stopDriver(),this.startTime=this.holdTime=null}stopDriver(){this.driver&&(this.driver.stop(),this.driver=void 0)}sample(s){return this.startTime=0,this.tick(s,!0)}attachTimeline(s){var i;return this.options.allowFlatten&&(this.options.type="keyframes",this.options.ease="linear",this.initAnimation()),(i=this.driver)==null||i.stop(),s.observe(this)}}const bb=new Set(["brightness","contrast","saturate","opacity"]);function kb(t){const[s,i]=t.slice(0,-1).split("(");if(s==="drop-shadow")return t;const[o]=i.match(Yc)||[];if(!o)return t;const c=i.replace(o,"");let d=bb.has(s)?1:0;return o!==i&&(d*=100),s+"("+d+c+")"}const jb=/\b([a-z-]*)\(.*?\)/gu,wc={...jt,getAnimatableNone:t=>{const s=t.match(jb);return s?s.map(kb).join(" "):t}},bc={...jt,getAnimatableNone:t=>{const s=jt.parse(t);return jt.createTransformer(t)(s.map(o=>typeof o=="number"?0:typeof o=="object"?{...o,alpha:1}:o))}},Om={...Vs,transform:Math.round},Sb={rotate:on,pathRotation:on,rotateX:on,rotateY:on,rotateZ:on,scale:ea,scaleX:ea,scaleY:ea,scaleZ:ea,skew:on,skewX:on,skewY:on,distance:ee,translateX:ee,translateY:ee,translateZ:ee,x:ee,y:ee,z:ee,perspective:ee,transformPerspective:ee,opacity:_r,originX:Lm,originY:Lm,originZ:ee},ja={borderWidth:ee,borderTopWidth:ee,borderRightWidth:ee,borderBottomWidth:ee,borderLeftWidth:ee,borderRadius:ee,borderTopLeftRadius:ee,borderTopRightRadius:ee,borderBottomRightRadius:ee,borderBottomLeftRadius:ee,width:ee,maxWidth:ee,height:ee,maxHeight:ee,top:ee,right:ee,bottom:ee,left:ee,inset:ee,insetBlock:ee,insetBlockStart:ee,insetBlockEnd:ee,insetInline:ee,insetInlineStart:ee,insetInlineEnd:ee,padding:ee,paddingTop:ee,paddingRight:ee,paddingBottom:ee,paddingLeft:ee,paddingBlock:ee,paddingBlockStart:ee,paddingBlockEnd:ee,paddingInline:ee,paddingInlineStart:ee,paddingInlineEnd:ee,margin:ee,marginTop:ee,marginRight:ee,marginBottom:ee,marginLeft:ee,marginBlock:ee,marginBlockStart:ee,marginBlockEnd:ee,marginInline:ee,marginInlineStart:ee,marginInlineEnd:ee,fontSize:ee,backgroundPositionX:ee,backgroundPositionY:ee,...Sb,zIndex:Om,fillOpacity:_r,strokeOpacity:_r,numOctaves:Om},Nb={...ja,color:Ke,backgroundColor:Ke,outlineColor:Ke,fill:Ke,stroke:Ke,borderColor:Ke,borderTopColor:Ke,borderRightColor:Ke,borderBottomColor:Ke,borderLeftColor:Ke,filter:wc,WebkitFilter:wc,mask:bc,WebkitMask:bc},ag=t=>Nb[t],Cb=new Set([wc,bc]);function su(t,s){let i=ag(t);return Cb.has(i)||(i=jt),i.getAnimatableNone?i.getAnimatableNone(s):void 0}function Tb(t){for(let s=1;s<t.length;s++)t[s]??(t[s]=t[s-1])}const Jn=t=>t*180/Math.PI,kc=t=>{const s=Jn(Math.atan2(t[1],t[0]));return jc(s)},Pb={x:4,y:5,translateX:4,translateY:5,scaleX:0,scaleY:3,scale:t=>(Math.abs(t[0])+Math.abs(t[3]))/2,rotate:kc,rotateZ:kc,skewX:t=>Jn(Math.atan(t[1])),skewY:t=>Jn(Math.atan(t[2])),skew:t=>(Math.abs(t[1])+Math.abs(t[2]))/2},jc=t=>(t=t%360,t<0&&(t+=360),t),zm=kc,Um=t=>Math.sqrt(t[0]*t[0]+t[1]*t[1]),Wm=t=>Math.sqrt(t[4]*t[4]+t[5]*t[5]),Mb={x:12,y:13,z:14,translateX:12,translateY:13,translateZ:14,scaleX:Um,scaleY:Wm,scale:t=>(Um(t)+Wm(t))/2,rotateX:t=>jc(Jn(Math.atan2(t[6],t[5]))),rotateY:t=>jc(Jn(Math.atan2(-t[2],t[0]))),rotateZ:zm,rotate:zm,skewX:t=>Jn(Math.atan(t[4])),skewY:t=>Jn(Math.atan(t[1])),skew:t=>(Math.abs(t[1])+Math.abs(t[4]))/2};function Sc(t){return t.includes("scale")?1:0}function Nc(t,s){if(!t||t==="none")return Sc(s);const i=t.match(/^matrix3d\(([-\d.e\s,]+)\)$/u);let o,c;if(i)o=Mb,c=i;else{const f=t.match(/^matrix\(([-\d.e\s,]+)\)$/u);o=Pb,c=f}if(!c)return Sc(s);const d=o[s],h=c[1].split(",").map(Ab);return typeof d=="function"?d(h):h[d]}const Eb=(t,s)=>{const{transform:i="none"}=getComputedStyle(t);return Nc(i,s)};function Ab(t){return parseFloat(t.trim())}const Fs=["transformPerspective","x","y","z","translateX","translateY","translateZ","scale","scaleX","scaleY","rotate","rotateX","rotateY","rotateZ","skew","skewX","skewY"],Bs=new Set([...Fs,"pathRotation"]),$m=t=>t===Vs||t===ee,_b=new Set(["x","y","z"]),Db=Fs.filter(t=>!_b.has(t));function Rb(t){const s=[];return Db.forEach(i=>{const o=t.getValue(i);if(o!==void 0){const c=o.get(),d=i.startsWith("scale")?1:0;if(c===d)return;s.push([i,c]),o.set(d)}}),s}const Lb=new Set(["bottom","right"]);function Hm(t,s,i,o,c,d){const h=parseFloat(t);if(!isNaN(h))return h;const{min:f,max:p}=s()[i],v=p-f;return d==="border-box"?v:v-parseFloat(o)-parseFloat(c)}const es={width:({width:t,paddingLeft:s="0",paddingRight:i="0",boxSizing:o},c)=>Hm(t,c,"x",s,i,o),height:({height:t,paddingTop:s="0",paddingBottom:i="0",boxSizing:o},c)=>Hm(t,c,"y",s,i,o),top:({top:t})=>parseFloat(t),left:({left:t})=>parseFloat(t),bottom:({top:t},s)=>{const{y:i}=s();return parseFloat(t)+(i.max-i.min)},right:({left:t},s)=>{const{x:i}=s();return parseFloat(t)+(i.max-i.min)},x:({transform:t})=>Nc(t,"x"),y:({transform:t})=>Nc(t,"y")};es.translateX=es.x;es.translateY=es.y;const ts=new Set;let Cc=!1,Tc=!1,Pc=!1;function og(){if(Tc){const t=[],s=new Set,i=new Set;ts.forEach(c=>{c.needsMeasurement&&(t.push(c),s.add(c.element),Lb.has(c.name)&&i.add(c.element))});const o=new Map;i.forEach(c=>{const d=Rb(c);d.length&&(o.set(c,d),c.render())}),t.forEach(c=>c.measureInitialState()),s.forEach(c=>{c.render();const d=o.get(c);d&&d.forEach(([h,f])=>{var p;(p=c.getValue(h))==null||p.set(f)})}),t.forEach(c=>c.measureEndState()),t.forEach(c=>{c.suspendedScrollY!==void 0&&window.scrollTo(0,c.suspendedScrollY)})}Tc=!1,Cc=!1,ts.forEach(t=>t.complete(Pc)),ts.clear()}function lg(){ts.forEach(t=>{t.readKeyframes(),t.needsMeasurement&&(Tc=!0)})}function Ib(){Pc=!0,lg(),og(),Pc=!1}function Vb(t,s,i){if(typeof t=="string"){if(Hc(t)||Gc(t))return parseFloat(t);if(!jt.test(t)&&jt.test(i))return su(s,i)}return t??void 0}class ru{constructor(s,i,o,c,d,h=!1){this.state="pending",this.isAsync=!1,this.needsMeasurement=!1,this.unresolvedKeyframes=[...s],this.onComplete=i,this.name=o,this.motionValue=c,this.element=d,this.isAsync=h}scheduleResolve(){this.state="scheduled",this.isAsync?(ts.add(this),Cc||(Cc=!0,je.read(lg),je.resolveKeyframes(og))):(this.readKeyframes(),this.complete())}readKeyframes(){const{unresolvedKeyframes:s,name:i,element:o,motionValue:c}=this;if(s[0]===null){const d=c==null?void 0:c.get(),h=s[s.length-1];if(d!==void 0)s[0]=d;else if(o&&i){const f=Vb(o.readValue(i,h),i,h);f!==void 0&&(s[0]=f)}s[0]===void 0&&(s[0]=h),c&&d===void 0&&c.set(s[0])}Tb(s)}setFinalKeyframe(){}measureInitialState(){}renderEndStyles(){}measureEndState(){}complete(s=!1){this.state="complete",this.onComplete(this.unresolvedKeyframes,this.finalKeyframe,s),ts.delete(this)}cancel(){this.state==="scheduled"&&(ts.delete(this),this.state="pending")}resume(){this.state==="pending"&&this.scheduleResolve()}}const Fb=t=>t.startsWith("--");function cg(t,s,i){Fb(s)?t.style.setProperty(s,i):t.style[s]=i}const Bb={};function ug(t,s){const i=_p(t);return()=>Bb[s]??i()}const Ob=ug(()=>window.ScrollTimeline!==void 0,"scrollTimeline"),dg=ug(()=>{try{document.createElement("div").animate({opacity:0},{easing:"linear(0, 1)"})}catch{return!1}return!0},"linearEasing"),Tr=([t,s,i,o])=>`cubic-bezier(${t}, ${s}, ${i}, ${o})`,Gm={linear:"linear",ease:"ease",easeIn:"ease-in",easeOut:"ease-out",easeInOut:"ease-in-out",circIn:Tr([0,.65,.55,1]),circOut:Tr([.55,0,1,.45]),backIn:Tr([.31,.01,.66,-.59]),backOut:Tr([.33,1.53,.69,.99])};function hg(t,s){if(t)return typeof t=="function"?dg()?eg(t,s):"ease-out":Wp(t)?Tr(t):Array.isArray(t)?t.map(i=>hg(i,s)||Gm.easeOut):Gm[t]}function zb(t,s,i,{delay:o=0,duration:c=300,repeat:d=0,repeatType:h="loop",ease:f="easeOut",times:p}={},v=void 0){const g={[s]:i};p&&(g.offset=p);const x=hg(f,c);Array.isArray(x)&&(g.easing=x);const w={delay:o,duration:c,easing:Array.isArray(x)?"linear":x,fill:"both",iterations:d+1,direction:h==="reverse"?"alternate":"normal"};return v&&(w.pseudoElement=v),t.animate(g,w)}function mg(t){return typeof t=="function"&&"applyToOptions"in t}function Ub({type:t,...s}){return mg(t)&&dg()?t.applyToOptions(s):(s.duration??(s.duration=300),s.ease??(s.ease="easeOut"),s)}class fg extends nu{constructor(s){if(super(),this.finishedTime=null,this.isStopped=!1,this.manualStartTime=null,!s)return;const{element:i,name:o,keyframes:c,pseudoElement:d,allowFlatten:h=!1,finalKeyframe:f,onComplete:p}=s;this.isPseudoElement=!!d,this.allowFlatten=h,this.options=s,Da(typeof s.type!="string");const v=Ub(s);this.animation=zb(i,o,c,v,d),v.autoplay===!1&&this.animation.pause(),this.animation.onfinish=()=>{if(this.finishedTime=this.time,!d){const g=Ra(c,this.options,f,this.speed);this.updateMotionValue&&this.updateMotionValue(g),cg(i,o,g),this.animation.cancel()}p==null||p(),this.notifyFinished()},ig(this,s,v)}play(){this.isStopped||(this.manualStartTime=null,this.animation.play(),this.state==="finished"&&this.updateFinished())}pause(){this.animation.pause()}complete(){var s,i;(i=(s=this.animation).finish)==null||i.call(s)}cancel(){try{this.animation.cancel()}catch{}}stop(){if(this.isStopped)return;this.isStopped=!0;const{state:s}=this;s==="idle"||s==="finished"||(this.updateMotionValue?this.updateMotionValue():this.commitStyles(),this.isPseudoElement||this.cancel())}commitStyles(){var i,o,c;const s=(i=this.options)==null?void 0:i.element;!this.isPseudoElement&&(s!=null&&s.isConnected)&&((c=(o=this.animation).commitStyles)==null||c.call(o))}get duration(){var i,o;const s=((o=(i=this.animation.effect)==null?void 0:i.getComputedTiming)==null?void 0:o.call(i).duration)||0;return kt(Number(s))}get iterationDuration(){const{delay:s=0}=this.options||{};return this.duration+kt(s)}get time(){return kt(Number(this.animation.currentTime)||0)}set time(s){const i=this.finishedTime!==null;this.manualStartTime=null,this.finishedTime=null,this.animation.currentTime=At(s),i&&this.animation.pause()}get speed(){return this.animation.playbackRate}set speed(s){s<0&&(this.finishedTime=null),this.animation.playbackRate=s}get state(){return this.finishedTime!==null?"finished":this.animation.playState}get startTime(){return this.manualStartTime??Number(this.animation.startTime)}set startTime(s){this.manualStartTime=this.animation.startTime=s}attachTimeline({timeline:s,rangeStart:i,rangeEnd:o,observe:c}){var d;return this.allowFlatten&&((d=this.animation.effect)==null||d.updateTiming({easing:"linear"})),this.animation.onfinish=null,s&&Ob()?(this.animation.timeline=s,i&&(this.animation.rangeStart=i),o&&(this.animation.rangeEnd=o),zt):c(this)}}const pg={anticipate:Bp,backInOut:Fp,circInOut:zp};function Wb(t){return t in pg}function $b(t){typeof t.ease=="string"&&Wb(t.ease)&&(t.ease=pg[t.ease])}const ql=10;class Hb extends fg{constructor(s){$b(s),sg(s),super(s),s.startTime!==void 0&&s.autoplay!==!1&&(this.startTime=s.startTime),this.options=s}updateMotionValue(s){const{motionValue:i,onUpdate:o,onComplete:c,element:d,...h}=this.options;if(!i)return;if(s!==void 0){i.set(s);return}const f=new ka({...h,autoplay:!1}),p=Math.max(ql,it.now()-this.startTime),v=Ut(0,ql,p-ql),g=f.sample(p).value,{name:x}=this.options;d&&x&&cg(d,x,g),i.setWithVelocity(f.sample(Math.max(0,p-v)).value,g,v),f.stop()}}const Km=(t,s)=>s==="zIndex"?!1:!!(typeof t=="number"||Array.isArray(t)||typeof t=="string"&&(jt.test(t)||t==="0")&&!t.startsWith("url("));function Gb(t){const s=t[0];if(t.length===1)return!0;for(let i=0;i<t.length;i++)if(t[i]!==s)return!0}function Kb(t,s,i,o){const c=t[0];if(c===null)return!1;if(s==="display"||s==="visibility")return!0;const d=t[t.length-1],h=Km(c,s),f=Km(d,s);return!h||!f?!1:Gb(t)||(i==="spring"||mg(i))&&o}function Mc(t){t.duration=0,t.type="keyframes"}const Ec=new Set(["opacity","clipPath","filter","transform","backgroundColor"]),qb=/^(?:oklch|oklab|lab|lch|color|color-mix|light-dark)\(/;function Xb(t){for(let s=0;s<t.length;s++)if(typeof t[s]=="string"&&qb.test(t[s]))return!0;return!1}const qm=new Set(["color","backgroundColor","outlineColor","fill","stroke","borderColor","borderTopColor","borderRightColor","borderBottomColor","borderLeftColor"]),Yb=_p(()=>Object.hasOwnProperty.call(Element.prototype,"animate"));function Qb(t){var x;const{motionValue:s,name:i,repeatDelay:o,repeatType:c,damping:d,type:h,keyframes:f}=t;if(!i||!(Ec.has(i)||qm.has(i)))return!1;const p=(x=s==null?void 0:s.owner)==null?void 0:x.current;if(!(p instanceof HTMLElement)&&!(p instanceof SVGElement))return!1;const{onUpdate:v,transformTemplate:g}=s.owner.getProps();return Yb()&&(Ec.has(i)||qm.has(i)&&Xb(f))&&(i!=="transform"||!g)&&!v&&!o&&c!=="mirror"&&d!==0&&h!=="inertia"}const Jb=40;class Zb extends nu{constructor(s){var p;super(),this.stop=()=>{var v,g;this._animation&&(this._animation.stop(),(v=this.stopTimeline)==null||v.call(this)),(g=this.keyframeResolver)==null||g.cancel()},this.createdAt=it.now();const{keyframes:i,name:o,motionValue:c,element:d}=s,h=s;h.autoplay??(h.autoplay=!0),h.delay??(h.delay=0),h.type??(h.type="keyframes"),h.repeat??(h.repeat=0),h.repeatDelay??(h.repeatDelay=0),h.repeatType??(h.repeatType="loop");const f=(d==null?void 0:d.KeyframeResolver)||ru;this.keyframeResolver=new f(i,(v,g,x)=>this.onKeyframesResolved(v,g,h,!x),o,c,d),(p=this.keyframeResolver)==null||p.scheduleResolve()}onKeyframesResolved(s,i,o,c){var N,B;this.keyframeResolver=void 0;const{name:d,type:h,velocity:f,delay:p,isHandoff:v,onUpdate:g}=o;this.resolvedAt=it.now();let x=!0;Kb(s,d,h,f)||(x=!1,(ln.instantAnimations||!p)&&(g==null||g(Ra(s,o,i))),s[0]=s[s.length-1],Mc(o),o.repeat=0);const w=c?this.resolvedAt?this.resolvedAt-this.createdAt>Jb?this.resolvedAt:this.createdAt:this.createdAt:void 0,{onComplete:j}=o;o.startTime??(o.startTime=w),o.finalKeyframe=i,o.keyframes=s,o.onComplete=()=>{j==null||j(),this.notifyFinished()};const k=x&&!v&&Qb(o);let S;if(k){o.element=(B=(N=o.motionValue)==null?void 0:N.owner)==null?void 0:B.current;try{S=new Hb(o)}catch{S=new ka(o)}}else S=new ka(o);this.pendingTimeline&&(this.stopTimeline=S.attachTimeline(this.pendingTimeline),this.pendingTimeline=void 0),this._animation=S}get finished(){return this._animation?this._animation.finished:super.finished}then(s,i){return this.finished.finally(s).then(()=>{})}get animation(){var s;return this._animation||((s=this.keyframeResolver)==null||s.resume(),Ib()),this._animation}get duration(){return this.animation.duration}get iterationDuration(){return this.animation.iterationDuration}get time(){return this.animation.time}set time(s){this.animation.time=s}get speed(){return this.animation.speed}get state(){return this.animation.state}set speed(s){this.animation.speed=s}get startTime(){return this.animation.startTime}attachTimeline(s){return this._animation?this.stopTimeline=this.animation.attachTimeline(s):this.pendingTimeline=s,()=>this.stop()}play(){this.animation.play()}pause(){this.animation.pause()}complete(){this.animation.complete()}cancel(){var s;this._animation&&this.animation.cancel(),(s=this.keyframeResolver)==null||s.cancel()}}function gg(t,s,i,o=0,c=1){const d=Array.from(t).sort((v,g)=>v.sortNodePosition(g)).indexOf(s),h=t.size,f=(h-1)*o;return typeof i=="function"?i(d,h):c===1?d*o:f-d*o}const Xm=30,ek=t=>!isNaN(parseFloat(t));class tk{constructor(s,i={}){this.canTrackVelocity=null,this.events={},this.updateAndNotify=o=>{const c=it.now();if(this.updatedAt!==c&&this.setPrevFrameValue(),this.prev=this.current,this.setCurrent(o),this.current!==this.prev&&(this.notifyChange(),this.dependents))for(const d of this.dependents)d.dirty()},this.hasAnimated=!1,this.setCurrent(s),this.owner=i.owner}setCurrent(s){this.current=s,this.updatedAt=it.now(),this.canTrackVelocity===null&&s!==void 0&&(this.canTrackVelocity=ek(this.current))}setPrevFrameValue(s=this.current){this.prevFrameValue=s,this.prevUpdatedAt=this.updatedAt}onChange(s){return this.on("change",s)}on(s,i){var o;return s==="change"?this.onChangeSubscribe(i):((o=this.events)[s]||(o[s]=new va)).add(i)}onChangeSubscribe(s){const{events:i}=this;return!i.change&&!this.changeSubscriber?this.changeSubscriber=s:(i.change||(i.change=new va,i.change.add(this.changeSubscriber),this.changeSubscriber=void 0),i.change.add(s)),()=>{var o;this.changeSubscriber===s?this.changeSubscriber=void 0:(o=i.change)==null||o.remove(s),this.stopIfUnobserved()}}stopIfUnobserved(){je.read(()=>{var s;!this.changeSubscriber&&!((s=this.events.change)!=null&&s.getSize())&&this.stop()})}clearListeners(){this.changeSubscriber=void 0;for(const s in this.events)this.events[s].clear()}attach(s,i){this.passiveEffect=s,this.stopPassiveEffect=i}set(s){this.passiveEffect?this.passiveEffect(s,this.updateAndNotify):this.updateAndNotify(s)}setWithVelocity(s,i,o){this.set(i),this.prev=void 0,this.prevFrameValue=s,this.prevUpdatedAt=this.updatedAt-o}jump(s,i=!0){this.updateAndNotify(s),this.prev=s,this.prevUpdatedAt=this.prevFrameValue=void 0,i&&this.stop(),this.stopPassiveEffect&&this.stopPassiveEffect()}dirty(){this.notifyChange()}notifyChange(){var o;const{current:s,changeSubscriber:i}=this;i?i(s):(o=this.events.change)==null||o.notify(s)}addDependent(s){this.dependents||(this.dependents=new Set),this.dependents.add(s)}removeDependent(s){this.dependents&&this.dependents.delete(s)}get(){return this.current}getPrevious(){return this.prev}getVelocity(){const s=it.now();if(!this.canTrackVelocity||this.prevFrameValue===void 0||s-this.updatedAt>Xm)return 0;const i=Math.min(this.updatedAt-this.prevUpdatedAt,Xm);return Dp(parseFloat(this.current)-parseFloat(this.prevFrameValue),i)}start(s){return this.stop(),new Promise(i=>{var d;this.hasAnimated=!0;let o=!1,c;c=s(()=>{var h;o=!0,(h=this.events.animationComplete)==null||h.notify(),this.animation===c&&this.clearAnimation(),i()}),o||(this.animation=c),(d=this.events.animationStart)==null||d.notify()})}stop(){this.animation&&(this.animation.stop(),this.events.animationCancel&&this.events.animationCancel.notify()),this.clearAnimation()}isAnimating(){return!!this.animation}clearAnimation(){this.animation=void 0}destroy(){var s,i;(s=this.dependents)==null||s.clear(),(i=this.events.destroy)==null||i.notify(),this.clearListeners(),this.stop(),this.stopPassiveEffect&&this.stopPassiveEffect()}}function Is(t,s){return new tk(t,s)}function yg(t,s){if(t!=null&&t.inherit&&s){const{inherit:i,...o}=t;return{...s,...o}}return t}function iu(t,s){const i=(t==null?void 0:t[s])??(t==null?void 0:t.default)??t;return i!==t?yg(i,t):i}const nk={type:"spring",stiffness:500,damping:25,restSpeed:10},sk=t=>({type:"spring",stiffness:550,damping:t===0?2*Math.sqrt(550):30,restSpeed:10}),rk={type:"keyframes",duration:.8},ik={type:"keyframes",ease:[.25,.1,.35,1],duration:.3},ak=(t,{keyframes:s})=>s.length>2?rk:Bs.has(t)?t.startsWith("scale")?sk(s[1]):nk:ik,ok=new Set(["when","delay","delayChildren","staggerChildren","staggerDirection","repeat","repeatType","repeatDelay","from","elapsed"]);function lk(t){for(const s in t)if(!ok.has(s))return!0;return!1}const au=(t,s,i,o={},c,d)=>h=>{const f=iu(o,t)||{},p=f.delay||o.delay||0;let{elapsed:v=0}=o;v=v-At(p);const g={keyframes:Array.isArray(i)?i:[null,i],ease:"easeOut",velocity:s.getVelocity(),...f,delay:-v,onUpdate:w=>{s.set(w),f.onUpdate&&f.onUpdate(w)},onComplete:()=>{h(),f.onComplete&&f.onComplete()},name:t,motionValue:s,element:d?void 0:c};lk(f)||Object.assign(g,ak(t,g)),g.duration&&(g.duration=At(g.duration)),g.repeatDelay&&(g.repeatDelay=At(g.repeatDelay)),g.from!==void 0&&(g.keyframes[0]=g.from);let x=!1;if((g.type===!1||g.duration===0&&!g.repeatDelay)&&(Mc(g),g.delay===0&&(x=!0)),(ln.instantAnimations||ln.skipAnimations||c!=null&&c.shouldSkipAnimations||f.skipAnimations)&&(x=!0,Mc(g),g.delay=0),g.allowFlatten=!f.type&&!f.ease,x&&!d&&s.get()!==void 0){const w=Ra(g.keyframes,f);if(w!==void 0){je.update(()=>{g.onUpdate(w),g.onComplete()});return}}return f.isSync?new ka(g):new Zb(g)},ck=/^var\(--(?:([\w-]+)|([\w-]+), ?([a-zA-Z\d ()%#.,-]+))\)/u;function uk(t){const s=ck.exec(t);if(!s)return[,];const[,i,o,c]=s;return[`--${i??o}`,c]}function vg(t,s,i=1){const[o,c]=uk(t);if(!o)return;const d=window.getComputedStyle(s).getPropertyValue(o);if(d){const h=d.trim();return Hc(h)?parseFloat(h):h}return Xc(c)?vg(c,s,i+1):c}function Ym(t){const s=[{},{}];return t==null||t.values.forEach((i,o)=>{s[0][o]=i.get(),s[1][o]=i.getVelocity()}),s}function ou(t,s,i,o){if(typeof s=="function"){const[c,d]=Ym(o);s=s(i!==void 0?i:t.custom,c,d)}if(typeof s=="string"&&(s=t.variants&&t.variants[s]),typeof s=="function"){const[c,d]=Ym(o);s=s(i!==void 0?i:t.custom,c,d)}return s}function ns(t,s,i){const o=t.getProps();return ou(o,s,i!==void 0?i:o.custom,t)}const xg=new Set(["width","height","top","left","right","bottom",...Fs]),Ac=t=>Array.isArray(t);function dk(t,s,i){t.hasValue(s)?t.getValue(s).set(i):t.addValue(s,Is(i))}function hk(t){return Ac(t)?t[t.length-1]||0:t}function mk(t,s){const i=ns(t,s);let{transitionEnd:o={},transition:c={},...d}=i||{};d={...d,...o};for(const h in d){const f=hk(d[h]);dk(t,h,f)}}const et=t=>!!(t&&t.getVelocity);function fk(t){return!!(et(t)&&t.add)}function _c(t,s){const i=t.getValue("willChange");if(fk(i))return i.add(s);if(!i&&ln.WillChange){const o=new ln.WillChange("auto");t.addValue("willChange",o),o.add(s)}}function lu(t){return t.replace(/([A-Z])/g,s=>`-${s.toLowerCase()}`)}const pk="framerAppearId",wg="data-"+lu(pk);function bg(t){return t.props[wg]}const gk=typeof window<"u";function yk({protectedKeys:t,needsAnimating:s},i){const o=t.hasOwnProperty(i)&&s[i]!==!0;return s[i]=!1,o}function kg(t,s,{delay:i=0,transitionOverride:o,type:c}={}){let{transition:d,transitionEnd:h,...f}=s;const p=t.getDefaultTransition();d=d?yg(d,p):p;const v=d==null?void 0:d.reduceMotion,g=d==null?void 0:d.skipAnimations;o&&(d=o);const x=[],w=c&&t.animationState&&t.animationState.getState()[c],j=d==null?void 0:d.path;j&&j.animateVisualElement(t,f,d,i,x);for(const k in f){const S=t.getValue(k,t.latestValues[k]??null),N=f[k];if(N===void 0||w&&yk(w,k))continue;const B={delay:i,...iu(d||{},k)};g&&(B.skipAnimations=!0);const E=S.get();if(E!==void 0&&!S.isAnimating()&&!Array.isArray(N)&&N===E&&!B.velocity){je.update(()=>S.set(N));continue}let R=!1;if(gk&&window.MotionHandoffAnimation){const F=bg(t);if(F){const V=window.MotionHandoffAnimation(F,k,je);V!==null&&(B.startTime=V,R=!0)}}_c(t,k);const I=v??t.shouldReduceMotion;S.start(au(k,S,N,I&&xg.has(k)?{type:!1}:B,t,R));const D=S.animation;D&&x.push(D)}if(h){const k=()=>je.update(()=>{h&&mk(t,h)});x.length?Promise.all(x).then(k):k()}return x}function Dc(t,s,i={}){var p;const o=ns(t,s,i.type==="exit"?(p=t.presenceContext)==null?void 0:p.custom:void 0);let{transition:c=t.getDefaultTransition()||{}}=o||{};i.transitionOverride&&(c=i.transitionOverride);const d=o?()=>Promise.all(kg(t,o,i)):()=>Promise.resolve(),h=t.variantChildren&&t.variantChildren.size?(v=0)=>{const{delayChildren:g=0,staggerChildren:x,staggerDirection:w}=c;return vk(t,s,v,g,x,w,i)}:()=>Promise.resolve(),{when:f}=c;if(f){const[v,g]=f==="beforeChildren"?[d,h]:[h,d];return v().then(()=>g())}else return Promise.all([d(),h(i.delay)])}function vk(t,s,i=0,o=0,c=0,d=1,h){const f=[];for(const p of t.variantChildren)p.notify("AnimationStart",s),f.push(Dc(p,s,{...h,delay:i+(typeof o=="function"?0:o)+gg(t.variantChildren,p,o,c,d)}).then(()=>p.notify("AnimationComplete",s)));return Promise.all(f)}function xk(t,s,i={}){t.notify("AnimationStart",s);let o;if(Array.isArray(s)){const c=s.map(d=>Dc(t,d,i));o=Promise.all(c)}else if(typeof s=="string")o=Dc(t,s,i);else{const c=typeof s=="function"?ns(t,s,i.custom):s;o=Promise.all(kg(t,c,i))}return o.then(()=>{t.notify("AnimationComplete",s)})}const wk={test:t=>t==="auto",parse:t=>t},bk=t=>s=>s.test(t),kk=[Vs,ee,Qt,on,Lw,Rw,wk],Qm=t=>kk.find(bk(t));function jk(t){return typeof t=="number"?t===0:t!==null?t==="none"||t==="0"||Gc(t):!0}const Sk=new Set(["auto","none","0"]);function Nk(t,s,i){let o=0,c;for(;o<t.length&&!c;){const d=t[o];typeof d=="string"&&!Sk.has(d)&&zw(d)&&(c=t[o]),o++}if(c&&i)for(const d of s)t[d]!==c&&(t[d]=su(i,c))}class Ck extends ru{constructor(s,i,o,c,d){super(s,i,o,c,d,!0)}readKeyframes(){const{unresolvedKeyframes:s,element:i,name:o}=this;if(!i||!i.current)return;super.readKeyframes();for(let g=0;g<s.length;g++){let x=s[g];if(typeof x=="string"&&(x=x.trim(),Xc(x))){const w=vg(x,i.current);w!==void 0&&(s[g]=w),g===s.length-1&&(this.finalKeyframe=x)}}if(this.resolveNoneKeyframes(),!xg.has(o)||s.length!==2)return;const[c,d]=s;if(typeof c=="number"&&typeof d=="number")return;const h=Qm(c),f=Qm(d),p=Rm(c),v=Rm(d);if(p!==v&&es[o]){this.needsMeasurement=!0;return}if(h!==f)if($m(h)&&$m(f))for(let g=0;g<s.length;g++){const x=s[g];typeof x=="string"&&(s[g]=parseFloat(x))}else es[o]&&(this.needsMeasurement=!0)}resolveNoneKeyframes(){const{unresolvedKeyframes:s,name:i}=this,o=[];for(let c=0;c<s.length;c++)(s[c]===null||jk(s[c]))&&o.push(c);o.length&&Nk(s,o,i)}measure(){const{element:s,name:i}=this;return es[i](window.getComputedStyle(s.current),()=>s.measureViewportBox())}measureInitialState(){var d;const{element:s,unresolvedKeyframes:i,name:o}=this;if(!s||!s.current)return;o==="height"&&(this.suspendedScrollY=window.pageYOffset),this.measuredOrigin=this.measure(),i[0]=this.measuredOrigin;const c=i[i.length-1];c!==void 0&&((d=this.motionValue)==null||d.jump(c,!1))}measureEndState(){var d,h;const{element:s,unresolvedKeyframes:i}=this;if(!s||!s.current)return;(d=this.motionValue)==null||d.jump(this.measuredOrigin,!1);const o=i.length-1,c=i[o];i[o]=this.measure(),c!==null&&this.finalKeyframe===void 0&&(this.finalKeyframe=c),(h=this.removedTransforms)!=null&&h.length&&this.removedTransforms.forEach(([f,p])=>{s.getValue(f).set(p)}),this.resolveNoneKeyframes()}}const cu=["borderTopLeftRadius","borderTopRightRadius","borderBottomRightRadius","borderBottomLeftRadius"];function Tk(t){return Ap(t)&&"offsetHeight"in t&&!("ownerSVGElement"in t)}function uu(t){return Ap(t)&&"ownerSVGElement"in t}const Rc=(t,s)=>s&&typeof t=="number"?s.transform(t):t;function jg(t,s,i){if(t==null)return[];if(t instanceof EventTarget)return[t];if(typeof t=="string"){let o=document;const c=(i==null?void 0:i[t])??o.querySelectorAll(t);return c?Array.from(c):[]}return Array.from(t).filter(o=>o!=null)}const Pk={x:"translateX",y:"translateY",z:"translateZ",transformPerspective:"perspective"},Mk=Fs.length;function Ek(t,s,i){let o="",c=!0;for(let h=0;h<Mk;h++){const f=Fs[h],p=t[f];if(p===void 0)continue;let v=!0;if(typeof p=="number")v=p===(f.startsWith("scale")?1:0);else{const g=parseFloat(p);v=f.startsWith("scale")?g===1:g===0}if(!v||i){const g=Rc(p,ja[f]);if(!v){c=!1;const x=Pk[f]||f;o+=`${x}(${g}) `}i&&(s[f]=g)}}const d=t.pathRotation;return d&&(c=!1,o+=`rotate(${Rc(d,ja.pathRotation)}) `),o=o.trim(),i?o=i(s,c?"":o):c&&(o="none"),o}function du(t,s,i){const{style:o,vars:c,transformOrigin:d}=t;let h=!1,f=!1;for(const p in s){const v=s[p];if(Bs.has(p)){h=!0;continue}else if(Gp(p)){c[p]=v;continue}else{const g=Rc(v,ja[p]);p.startsWith("origin")?(f=!0,d[p]=g):o[p]=g}}if(s.transform||(h||i?o.transform=Ek(s,t.transform,i):o.transform&&(o.transform="none")),f){const{originX:p="50%",originY:v="50%",originZ:g=0}=d;o.transformOrigin=`${p} ${v} ${g}`}}const Ak={offset:"stroke-dashoffset",array:"stroke-dasharray"},_k={offset:"strokeDashoffset",array:"strokeDasharray"};function Dk(t,s,i=1,o=0,c=!0){t.pathLength=1;const d=c?Ak:_k;t[d.offset]=`${-o}`,t[d.array]=`${s} ${i}`}const Sg=["transform","opacity","offsetDistance","offsetPath","offsetRotate","offsetAnchor"];function Ng(t,{attrX:s,attrY:i,attrScale:o,pathLength:c,pathSpacing:d=1,pathOffset:h=0,...f},p,v,g){if(du(t,f,v),p){t.style.viewBox&&(t.attrs.viewBox=t.style.viewBox);return}t.attrs=t.style,t.style={};const{attrs:x,style:w}=t;for(const j of Sg)x[j]!==void 0&&(w[j]=x[j],delete x[j]);(w.transform||x.transformOrigin)&&(w.transformOrigin=x.transformOrigin??"50% 50%",delete x.transformOrigin),w.transform&&(w.transformBox=(g==null?void 0:g.transformBox)??"fill-box",delete x.transformBox),s!==void 0&&(x.x=s),i!==void 0&&(x.y=i),o!==void 0&&(x.scale=o),c!==void 0&&Dk(x,c,d,h,!1)}function Cg({top:t,left:s,right:i,bottom:o}){return{x:{min:s,max:i},y:{min:t,max:o}}}function Rk({x:t,y:s}){return{top:s.min,right:t.max,bottom:s.max,left:t.min}}function Lk(t,s){if(!s)return t;const i=s({x:t.left,y:t.top}),o=s({x:t.right,y:t.bottom});return{top:i.y,left:i.x,bottom:o.y,right:o.x}}function Xl(t){return t===void 0||t===1}function Lc({scale:t,scaleX:s,scaleY:i}){return!Xl(t)||!Xl(s)||!Xl(i)}function qn(t){return Lc(t)||Tg(t)||t.z||t.rotate||t.rotateX||t.rotateY||t.skewX||t.skewY}function Tg(t){return Jm(t.x)||Jm(t.y)}function Jm(t){return t&&t!=="0%"}function Sa(t,s,i){const o=t-i,c=s*o;return i+c}function Zm(t,s,i,o,c){return c!==void 0&&(t=Sa(t,c,o)),Sa(t,i,o)+s}function Ic(t,s=0,i=1,o,c){t.min=Zm(t.min,s,i,o,c),t.max=Zm(t.max,s,i,o,c)}function Pg(t,{x:s,y:i}){Ic(t.x,s.translate,s.scale,s.originPoint),Ic(t.y,i.translate,i.scale,i.originPoint)}const ef=.999999999999,tf=1.0000000000001;function Ik(t,s,i,o=!1){var f;const c=i.length;if(!c)return;s.x=s.y=1;let d,h;for(let p=0;p<c;p++){d=i[p],h=d.projectionDelta;const{visualElement:v}=d.options;v&&v.props.style&&v.props.style.display==="contents"||(o&&d.options.layoutScroll&&d.scroll&&d!==d.root&&(Xt(t.x,-d.scroll.offset.x),Xt(t.y,-d.scroll.offset.y)),h&&(s.x*=h.x.scale,s.y*=h.y.scale,Pg(t,h)),o&&qn(d.latestValues)&&la(t,d.latestValues,(f=d.layout)==null?void 0:f.layoutBox))}s.x<tf&&s.x>ef&&(s.x=1),s.y<tf&&s.y>ef&&(s.y=1)}function Xt(t,s){t.min+=s,t.max+=s}function nf(t,s,i,o,c=.5){const d=ke(t.min,t.max,c);Ic(t,s,i,d,o)}function sf(t,s){return typeof t=="string"?parseFloat(t)/100*(s.max-s.min):t}function la(t,s,i){const o=i??t;nf(t.x,sf(s.x,o.x),s.scaleX,s.scale,s.originX),nf(t.y,sf(s.y,o.y),s.scaleY,s.scale,s.originY)}function Mg(t,s){return Cg(Lk(t.getBoundingClientRect(),s))}function Vk(t,s,i){const o=Mg(t,i),{scroll:c}=s;return c&&(Xt(o.x,c.offset.x),Xt(o.y,c.offset.y)),o}const{schedule:hu}=$p(queueMicrotask,!1),Ot={x:!1,y:!1};function Eg(){return Ot.x||Ot.y}function Fk(t){return t==="x"||t==="y"?Ot[t]?null:(Ot[t]=!0,()=>{Ot[t]=!1}):Ot.x||Ot.y?null:(Ot.x=Ot.y=!0,()=>{Ot.x=Ot.y=!1})}function Ag(t,s){const i=jg(t),o=new AbortController,c={passive:!0,...s,signal:o.signal};return[i,c,()=>o.abort()]}function Bk(t){return!(t.pointerType==="touch"||Eg())}function Ok(t,s,i={}){const[o,c,d]=Ag(t,i);return o.forEach(h=>{let f=!1,p=!1,v;const g=()=>{h.removeEventListener("pointerleave",k)},x=N=>{v&&(v(N),v=void 0),g()},w=N=>{f=!1,window.removeEventListener("pointerup",w),window.removeEventListener("pointercancel",w),p&&(p=!1,x(N))},j=()=>{f=!0,window.addEventListener("pointerup",w,c),window.addEventListener("pointercancel",w,c)},k=N=>{if(N.pointerType!=="touch"){if(f){p=!0;return}x(N)}},S=N=>{if(!Bk(N))return;p=!1;const B=s(h,N);typeof B=="function"&&(v=B,h.addEventListener("pointerleave",k,c))};h.addEventListener("pointerenter",S,c),h.addEventListener("pointerdown",j,c)}),d}const _g=(t,s)=>s?t===s?!0:_g(t,s.parentElement):!1,mu=t=>t.pointerType==="mouse"?typeof t.button!="number"||t.button<=0:t.isPrimary!==!1,zk=new Set(["BUTTON","INPUT","SELECT","TEXTAREA","A"]);function Uk(t){return zk.has(t.tagName)||t.isContentEditable===!0}const Wk=new Set(["INPUT","SELECT","TEXTAREA"]);function $k(t){return Wk.has(t.tagName)||t.isContentEditable===!0}const ca=new WeakSet;function rf(t){return s=>{s.key==="Enter"&&t(s)}}function Yl(t,s){t.dispatchEvent(new PointerEvent("pointer"+s,{isPrimary:!0,bubbles:!0}))}const Hk=(t,s)=>{const i=t.currentTarget;if(!i)return;const o=rf(()=>{if(ca.has(i))return;Yl(i,"down");const c=rf(()=>{Yl(i,"up")}),d=()=>Yl(i,"cancel");i.addEventListener("keyup",c,s),i.addEventListener("blur",d,s)});i.addEventListener("keydown",o,s),i.addEventListener("blur",()=>i.removeEventListener("keydown",o),s)};function af(t){return mu(t)&&!Eg()}const of=new WeakSet;function Gk(t,s,i={}){const[o,c,d]=Ag(t,i),h=f=>{const p=f.currentTarget;if(!af(f)||of.has(f))return;ca.add(p),i.stopPropagation&&of.add(f);const v=s(p,f),g={...c,capture:!0},x=(k,S)=>{window.removeEventListener("pointerup",w,g),window.removeEventListener("pointercancel",j,g),ca.has(p)&&ca.delete(p),af(k)&&typeof v=="function"&&v(k,{success:S})},w=k=>{x(k,p===window||p===document||i.useGlobalTarget||_g(p,k.target))},j=k=>{x(k,!1)};window.addEventListener("pointerup",w,g),window.addEventListener("pointercancel",j,g)};return o.forEach(f=>{(i.useGlobalTarget?window:f).addEventListener("pointerdown",h,c),Tk(f)&&(f.addEventListener("focus",v=>Hk(v,c)),!Uk(f)&&!f.hasAttribute("tabindex")&&(f.tabIndex=0))}),d}const ua=new WeakMap;let Pn;const Dg=(t,s,i)=>(o,c)=>c&&c[0]?c[0][t+"Size"]:uu(o)&&"getBBox"in o?o.getBBox()[s]:o[i],Kk=Dg("inline","width","offsetWidth"),qk=Dg("block","height","offsetHeight");function Xk({target:t,borderBoxSize:s}){var i;(i=ua.get(t))==null||i.forEach(o=>{o(t,{get width(){return Kk(t,s)},get height(){return qk(t,s)}})})}function Yk(t){t.forEach(Xk)}function Qk(){typeof ResizeObserver>"u"||(Pn=new ResizeObserver(Yk))}function Jk(t,s){Pn||Qk();const i=jg(t);return i.forEach(o=>{let c=ua.get(o);c||(c=new Set,ua.set(o,c)),c.add(s),Pn==null||Pn.observe(o)}),()=>{i.forEach(o=>{const c=ua.get(o);c==null||c.delete(s),c!=null&&c.size||Pn==null||Pn.unobserve(o)})}}const da=new Set;let Ds;function Zk(){Ds=()=>{const t={get width(){return window.innerWidth},get height(){return window.innerHeight}};da.forEach(s=>s(t))},window.addEventListener("resize",Ds)}function e0(t){return da.add(t),Ds||Zk(),()=>{da.delete(t),!da.size&&typeof Ds=="function"&&(window.removeEventListener("resize",Ds),Ds=void 0)}}function lf(t,s){return typeof t=="function"?e0(t):Jk(t,s)}function t0(t){return uu(t)&&t.tagName==="svg"}const cf=()=>({translate:0,scale:1,origin:0,originPoint:0}),Rs=()=>({x:cf(),y:cf()}),uf=()=>({min:0,max:0}),He=()=>({x:uf(),y:uf()}),n0=new WeakMap;function La(t){return t!==null&&typeof t=="object"&&typeof t.start=="function"}function Rr(t){return typeof t=="string"||Array.isArray(t)}const fu=["animate","whileInView","whileFocus","whileHover","whileTap","whileDrag","exit"],Na=["initial",...fu];function Ia(t){if(La(t.animate))return!0;for(let s=0;s<Na.length;s++)if(Rr(t[Na[s]]))return!0;return!1}function Rg(t){return!!(Ia(t)||t.variants)}function s0(t,s,i){for(const o in s){const c=s[o],d=i[o];if(et(c))t.addValue(o,c);else if(et(d))t.addValue(o,Is(c,{owner:t}));else if(d!==c)if(t.hasValue(o)){const h=t.getValue(o);h.liveStyle===!0?h.jump(c):h.hasAnimated||h.set(c)}else{const h=t.getStaticValue(o);t.addValue(o,Is(h!==void 0?h:c,{owner:t}))}}for(const o in i)s[o]===void 0&&t.removeValue(o);return s}const Ca={current:null},pu={current:!1},r0=typeof window<"u";function Lg(){if(pu.current=!0,!!r0)if(window.matchMedia){const t=window.matchMedia("(prefers-reduced-motion)"),s=()=>Ca.current=t.matches;t.addEventListener("change",s),s()}else Ca.current=!1}const df=["AnimationStart","AnimationComplete","Update","BeforeLayoutMeasure","LayoutMeasure","LayoutAnimationStart","LayoutAnimationComplete"];let Ta={};function Ig(t){Ta=t}function i0(){return Ta}class a0{scrapeMotionValuesFromProps(s,i,o){return{}}constructor({parent:s,props:i,presenceContext:o,reducedMotionConfig:c,skipAnimations:d,blockInitialAnimation:h,visualState:f},p={}){this.current=null,this.children=new Set,this.isVariantNode=!1,this.isControllingVariants=!1,this.shouldReduceMotion=null,this.shouldSkipAnimations=!1,this.values=new Map,this.KeyframeResolver=ru,this.features={},this.valueSubscriptions=new Map,this.prevMotionValues={},this.hasBeenMounted=!1,this.events={},this.propEventSubscriptions={},this.notifyUpdate=()=>this.notify("Update",this.latestValues),this.render=()=>{this.current&&(this.triggerBuild(),this.renderInstance(this.current,this.renderState,this.props.style,this.projection))},this.renderScheduledAt=0,this.scheduleRender=()=>{const j=it.now();this.renderScheduledAt<j&&(this.renderScheduledAt=j,je.render(this.render,!1,!0))};const{latestValues:v,renderState:g}=f;this.latestValues=v,this.baseTarget={...v},this.initialValues=i.initial?{...v}:{},this.renderState=g,this.parent=s,this.props=i,this.presenceContext=o,this.depth=s?s.depth+1:0,this.reducedMotionConfig=c,this.skipAnimationsConfig=d,this.options=p,this.blockInitialAnimation=!!h,this.isControllingVariants=Ia(i),this.isVariantNode=Rg(i),this.isVariantNode&&(this.variantChildren=new Set),this.manuallyAnimateOnMount=!!(s&&s.current);const{willChange:x,...w}=this.scrapeMotionValuesFromProps(i,{},this);for(const j in w){const k=w[j];v[j]!==void 0&&et(k)&&k.set(v[j])}}mount(s){var i,o;if(this.hasBeenMounted)for(const c in this.initialValues)(i=this.values.get(c))==null||i.jump(this.initialValues[c]),this.latestValues[c]=this.initialValues[c];this.current=s,n0.set(s,this),this.projection&&!this.projection.instance&&this.projection.mount(s),this.parent&&this.isVariantNode&&!this.isControllingVariants&&(this.removeFromVariantTree=this.parent.addVariantChild(this)),this.values.forEach((c,d)=>this.bindToMotionValue(d,c)),this.reducedMotionConfig==="never"?this.shouldReduceMotion=!1:this.reducedMotionConfig==="always"?this.shouldReduceMotion=!0:(pu.current||Lg(),this.shouldReduceMotion=Ca.current),this.shouldSkipAnimations=this.skipAnimationsConfig??!1,(o=this.parent)==null||o.addChild(this),this.update(this.props,this.presenceContext),this.hasBeenMounted=!0}unmount(){var s;this.projection&&this.projection.unmount(),En(this.notifyUpdate),En(this.render),this.valueSubscriptions.forEach(i=>i()),this.valueSubscriptions.clear(),this.removeFromVariantTree&&this.removeFromVariantTree(),(s=this.parent)==null||s.removeChild(this);for(const i in this.events)this.events[i].clear();for(const i in this.features){const o=this.features[i];o&&(o.unmount(),o.isMounted=!1)}this.current=null}addChild(s){this.children.add(s),this.enteringChildren??(this.enteringChildren=new Set),this.enteringChildren.add(s)}removeChild(s){this.children.delete(s),this.enteringChildren&&this.enteringChildren.delete(s)}bindToMotionValue(s,i){if(this.valueSubscriptions.has(s)&&this.valueSubscriptions.get(s)(),i.accelerate&&Ec.has(s)&&this.current instanceof HTMLElement){const{factory:h,keyframes:f,times:p,ease:v,duration:g}=i.accelerate,x=new fg({element:this.current,name:s,keyframes:f,times:p,ease:v,duration:At(g)}),w=h(x);this.valueSubscriptions.set(s,()=>{w(),x.cancel()});return}const o=Bs.has(s);o&&this.onBindTransform&&this.onBindTransform();const c=i.on("change",h=>{this.latestValues[s]=h,this.props.onUpdate&&je.preRender(this.notifyUpdate),o&&this.projection&&(this.projection.isTransformDirty=!0),this.scheduleRender()});let d;typeof window<"u"&&window.MotionCheckAppearSync&&(d=window.MotionCheckAppearSync(this,s,i)),this.valueSubscriptions.set(s,()=>{c(),d&&d()})}sortNodePosition(s){return!this.current||!this.sortInstanceNodePosition||this.type!==s.type?0:this.sortInstanceNodePosition(this.current,s.current)}updateFeatures(){let s="animation";for(s in Ta){const i=Ta[s];if(!i)continue;const{isEnabled:o,Feature:c}=i;if(!this.features[s]&&c&&o(this.props)&&(this.features[s]=new c(this)),this.features[s]){const d=this.features[s];d.isMounted?d.update():(d.mount(),d.isMounted=!0)}}}triggerBuild(){this.build(this.renderState,this.latestValues,this.props)}measureViewportBox(){return this.current?this.measureInstanceViewportBox(this.current,this.props):He()}getStaticValue(s){return this.latestValues[s]}setStaticValue(s,i){this.latestValues[s]=i}update(s,i){(s.transformTemplate||this.props.transformTemplate)&&this.scheduleRender(),this.prevProps=this.props,this.props=s,this.prevPresenceContext=this.presenceContext,this.presenceContext=i;for(let o=0;o<df.length;o++){const c=df[o];this.propEventSubscriptions[c]&&(this.propEventSubscriptions[c](),delete this.propEventSubscriptions[c]);const d="on"+c,h=s[d];h&&(this.propEventSubscriptions[c]=this.on(c,h))}this.prevMotionValues=s0(this,this.scrapeMotionValuesFromProps(s,this.prevProps||{},this),this.prevMotionValues),this.handleChildMotionValue&&this.handleChildMotionValue()}getProps(){return this.props}getVariant(s){return this.props.variants?this.props.variants[s]:void 0}getDefaultTransition(){return this.props.transition}getTransformPagePoint(){return this.props.transformPagePoint}getClosestVariantNode(){return this.isVariantNode?this:this.parent?this.parent.getClosestVariantNode():void 0}addVariantChild(s){const i=this.getClosestVariantNode();if(i)return i.variantChildren&&i.variantChildren.add(s),()=>i.variantChildren.delete(s)}addValue(s,i){const o=this.values.get(s);i!==o&&(o&&this.removeValue(s),this.bindToMotionValue(s,i),this.values.set(s,i),this.latestValues[s]=i.get())}removeValue(s){this.values.delete(s);const i=this.valueSubscriptions.get(s);i&&(i(),this.valueSubscriptions.delete(s)),delete this.latestValues[s],this.removeValueFromRenderState(s,this.renderState)}hasValue(s){return this.values.has(s)}getValue(s,i){if(this.props.values&&this.props.values[s])return this.props.values[s];let o=this.values.get(s);return o===void 0&&i!==void 0&&(o=Is(i===null?void 0:i,{owner:this}),this.addValue(s,o)),o}readValue(s,i){let o=this.latestValues[s]!==void 0||!this.current?this.latestValues[s]:this.getBaseTargetFromProps(this.props,s)??this.readValueFromInstance(this.current,s,this.options);return o!=null&&(typeof o=="string"&&(Hc(o)||Gc(o))?o=parseFloat(o):typeof o!="number"&&!jt.test(o)&&jt.test(i)&&(o=su(s,i)),this.setBaseTarget(s,et(o)?o.get():o)),et(o)?o.get():o}setBaseTarget(s,i){this.baseTarget[s]=i}getBaseTarget(s){var d;const{initial:i}=this.props;let o;if(typeof i=="string"||typeof i=="object"){const h=ou(this.props,i,(d=this.presenceContext)==null?void 0:d.custom);h&&(o=h[s])}if(i&&o!==void 0)return o;const c=this.getBaseTargetFromProps(this.props,s);return c!==void 0&&!et(c)?c:this.initialValues[s]!==void 0&&o===void 0?void 0:this.baseTarget[s]}on(s,i){return this.events[s]||(this.events[s]=new va),this.events[s].add(i)}notify(s,...i){this.events[s]&&this.events[s].notify(...i)}scheduleRenderMicrotask(){hu.render(this.render)}}class Vg extends a0{constructor(){super(...arguments),this.KeyframeResolver=Ck}sortInstanceNodePosition(s,i){return s.compareDocumentPosition(i)&2?1:-1}getBaseTargetFromProps(s,i){const o=s.style;return o?o[i]:void 0}removeValueFromRenderState(s,{vars:i,style:o}){delete i[s],delete o[s]}handleChildMotionValue(){this.childSubscription&&(this.childSubscription(),delete this.childSubscription);const{children:s}=this.props;et(s)&&(this.childSubscription=s.on("change",i=>{this.current&&(this.current.textContent=`${i}`)}))}}class An{constructor(s){this.isMounted=!1,this.node=s}update(){}}function Fg(t,{style:s,vars:i},o,c){const d=t.style;let h;for(h in s)d[h]=s[h];c==null||c.applyProjectionStyles(d,o);for(h in i)d.setProperty(h,i[h])}function hf(t,s){return s.max===s.min?0:t/(s.max-s.min)*100}const Cr={correct:(t,s)=>{if(!s.target)return t;if(typeof t=="string")if(ee.test(t))t=parseFloat(t);else return t;const i=hf(t,s.target.x),o=hf(t,s.target.y);return`${i}% ${o}%`}},o0={correct:(t,{treeScale:s,projectionDelta:i})=>{const o=t,c=jt.parse(t);if(c.length>5)return o;const d=jt.createTransformer(t),h=typeof c[0]!="number"?1:0,f=i.x.scale*s.x,p=i.y.scale*s.y;c[0+h]/=f,c[1+h]/=p;const v=ke(f,p,.5);return typeof c[2+h]=="number"&&(c[2+h]/=v),typeof c[3+h]=="number"&&(c[3+h]/=v),d(c)}},Vc={borderRadius:{...Cr,applyTo:[...cu]},borderTopLeftRadius:Cr,borderTopRightRadius:Cr,borderBottomLeftRadius:Cr,borderBottomRightRadius:Cr,boxShadow:o0};function Bg(t,{layout:s,layoutId:i}){return Bs.has(t)||t.startsWith("origin")||(s||i!==void 0)&&(!!Vc[t]||t==="opacity")}function gu(t,s,i){var h;const o=t.style,c=s==null?void 0:s.style,d={};if(!o)return d;for(const f in o)(et(o[f])||c&&et(c[f])||Bg(f,t)||((h=i==null?void 0:i.getValue(f))==null?void 0:h.liveStyle)!==void 0)&&(d[f]=o[f]);return d}function l0(t){return window.getComputedStyle(t)}class c0 extends Vg{constructor(){super(...arguments),this.type="html",this.renderInstance=Fg}mount(s){Da(!!s.style),super.mount(s)}readValueFromInstance(s,i){var o;if(Bs.has(i))return(o=this.projection)!=null&&o.isProjecting?Sc(i):Eb(s,i);{const c=l0(s),d=(Gp(i)?c.getPropertyValue(i):c[i])||0;return typeof d=="string"?d.trim():d}}measureInstanceViewportBox(s,{transformPagePoint:i}){return Mg(s,i)}build(s,i,o){du(s,i,o.transformTemplate)}scrapeMotionValuesFromProps(s,i,o){return gu(s,i,o)}}const Og=new Set(["baseFrequency","diffuseConstant","kernelMatrix","kernelUnitLength","keySplines","keyTimes","limitingConeAngle","markerHeight","markerWidth","numOctaves","targetX","targetY","surfaceScale","specularConstant","specularExponent","stdDeviation","tableValues","viewBox","gradientTransform","pathLength","startOffset","textLength","lengthAdjust"]),zg=t=>typeof t=="string"&&t.toLowerCase()==="svg";function u0(t,s,i,o){Fg(t,s,void 0,o);for(const c in s.attrs)t.setAttribute(Og.has(c)?c:lu(c),s.attrs[c])}function Ug(t,s,i){const o=gu(t,s,i);for(const c in t)if(et(t[c])||et(s[c])){const d=Fs.indexOf(c)!==-1?"attr"+c.charAt(0).toUpperCase()+c.substring(1):c;o[d]=t[c]}return o}class d0 extends Vg{constructor(){super(...arguments),this.type="svg",this.isSVGTag=!1,this.measureInstanceViewportBox=He}getBaseTargetFromProps(s,i){return s[i]}readValueFromInstance(s,i){if(Bs.has(i)){const o=ag(i);return o&&o.default||0}if(Sg.includes(i)){const c=getComputedStyle(s)[i];if(typeof c=="string"&&c)return c.trim()}return i=Og.has(i)?i:lu(i),s.getAttribute(i)}scrapeMotionValuesFromProps(s,i,o){return Ug(s,i,o)}build(s,i,o){Ng(s,i,this.isSVGTag,o.transformTemplate,o.style)}renderInstance(s,i,o,c){u0(s,i,o,c)}mount(s){this.isSVGTag=zg(s.tagName),super.mount(s)}}const h0=Na.length;function Wg(t){if(!t)return;if(!t.isControllingVariants){const i=t.parent?Wg(t.parent)||{}:{};return t.props.initial!==void 0&&(i.initial=t.props.initial),i}const s={};for(let i=0;i<h0;i++){const o=Na[i],c=t.props[o];(Rr(c)||c===!1)&&(s[o]=c)}return s}function $g(t,s){if(!Array.isArray(s))return!1;const i=s.length;if(i!==t.length)return!1;for(let o=0;o<i;o++)if(s[o]!==t[o])return!1;return!0}const m0=[...fu].reverse(),f0=fu.length;function p0(t){return s=>Promise.all(s.map(({animation:i,options:o})=>xk(t,i,o)))}function g0(t){let s=p0(t),i=mf(),o=!0,c=!1;const d=v=>(g,x)=>{var j;const w=ns(t,x,v==="exit"?(j=t.presenceContext)==null?void 0:j.custom:void 0);if(w){const{transition:k,transitionEnd:S,...N}=w;g={...g,...N,...S}}return g};function h(v){s=v(t)}function f(v){const{props:g}=t,x=Wg(t.parent)||{},w=[],j=new Set;let k={},S=1/0;for(let B=0;B<f0;B++){const E=m0[B],R=i[E],I=g[E]!==void 0?g[E]:x[E],D=Rr(I),F=E===v?R.isActive:null;F===!1&&(S=B);let V=I===x[E]&&I!==g[E]&&D;if(V&&(o||c)&&t.manuallyAnimateOnMount&&(V=!1),R.protectedKeys={...k},!R.isActive&&F===null||!I&&!R.prevProp||La(I)||typeof I=="boolean")continue;if(E==="exit"&&R.isActive&&F!==!0){R.prevResolvedValues&&(k={...k,...R.prevResolvedValues});continue}const z=y0(R.prevProp,I);let oe=z||E===v&&R.isActive&&!V&&D||B>S&&D,le=!1;const xe=Array.isArray(I)?I:[I];let ve=xe.reduce(d(E),{});F===!1&&(ve={});const{prevResolvedValues:ie={}}=R,Pe={...ie,...ve},Ie=O=>{oe=!0,j.has(O)&&(le=!0,j.delete(O)),R.needsAnimating[O]=!0;const q=t.getValue(O);q&&(q.liveStyle=!1)};for(const O in Pe){const q=ve[O],K=ie[O];if(k.hasOwnProperty(O))continue;let M=!1;Ac(q)&&Ac(K)?M=!$g(q,K)||z:M=q!==K,M?q!=null?Ie(O):j.add(O):q!==void 0&&j.has(O)?Ie(O):R.protectedKeys[O]=!0}R.prevProp=I,R.prevResolvedValues=ve,R.isActive&&(k={...k,...ve}),(o||c)&&t.blockInitialAnimation&&(oe=!1);const Ae=V&&z;oe&&(!Ae||le)&&w.push(...xe.map(O=>{const q={type:E};if(typeof O=="string"&&(o||c)&&!Ae&&t.manuallyAnimateOnMount&&t.parent){const{parent:K}=t,M=ns(K,O);if(K.enteringChildren&&M){const{delayChildren:U}=M.transition||{};q.delay=gg(K.enteringChildren,t,U)}}return{animation:O,options:q}}))}if(j.size){const B={};if(typeof g.initial!="boolean"){const E=ns(t,Array.isArray(g.initial)?g.initial[0]:g.initial);E&&E.transition&&(B.transition=E.transition)}j.forEach(E=>{const R=t.getBaseTarget(E),I=t.getValue(E);I&&(I.liveStyle=!0),B[E]=R??null}),w.push({animation:B})}let N=!!w.length;return o&&(g.initial===!1||g.initial===g.animate)&&!t.manuallyAnimateOnMount&&(N=!1),o=!1,c=!1,N?s(w):Promise.resolve()}function p(v,g){var w;if(i[v].isActive===g)return Promise.resolve();(w=t.variantChildren)==null||w.forEach(j=>{var k;return(k=j.animationState)==null?void 0:k.setActive(v,g)}),i[v].isActive=g;const x=f(v);for(const j in i)i[j].protectedKeys={};return x}return{animateChanges:f,setActive:p,setAnimateFunction:h,getState:()=>i,reset:()=>{i=mf(),c=!0}}}function y0(t,s){return typeof s=="string"?s!==t:Array.isArray(s)?!$g(s,t):!1}function Kn(t=!1){return{isActive:t,protectedKeys:{},needsAnimating:{},prevResolvedValues:{}}}function mf(){return{animate:Kn(!0),whileInView:Kn(),whileHover:Kn(),whileTap:Kn(),whileDrag:Kn(),whileFocus:Kn(),exit:Kn()}}function Fc(t,s){t.min=s.min,t.max=s.max}function Bt(t,s){Fc(t.x,s.x),Fc(t.y,s.y)}function ff(t,s){t.translate=s.translate,t.scale=s.scale,t.originPoint=s.originPoint,t.origin=s.origin}const Hg=1e-4,v0=1-Hg,x0=1+Hg,Gg=.01,w0=0-Gg,b0=0+Gg;function ct(t){return t.max-t.min}function k0(t,s,i){return Math.abs(t-s)<=i}function pf(t,s,i,o=.5){t.origin=o,t.originPoint=ke(s.min,s.max,t.origin),t.scale=ct(i)/ct(s),t.translate=ke(i.min,i.max,t.origin)-t.originPoint,(t.scale>=v0&&t.scale<=x0||isNaN(t.scale))&&(t.scale=1),(t.translate>=w0&&t.translate<=b0||isNaN(t.translate))&&(t.translate=0)}function Mr(t,s,i,o){pf(t.x,s.x,i.x,o?o.originX:void 0),pf(t.y,s.y,i.y,o?o.originY:void 0)}function gf(t,s,i,o=0){const c=o?ke(i.min,i.max,o):i.min;t.min=c+s.min,t.max=t.min+ct(s)}function j0(t,s,i,o){gf(t.x,s.x,i.x,o==null?void 0:o.x),gf(t.y,s.y,i.y,o==null?void 0:o.y)}function yf(t,s,i,o=0){const c=o?ke(i.min,i.max,o):i.min;t.min=s.min-c,t.max=t.min+ct(s)}function Pa(t,s,i,o){yf(t.x,s.x,i.x,o==null?void 0:o.x),yf(t.y,s.y,i.y,o==null?void 0:o.y)}function vf(t,s,i,o,c){return t-=s,t=Sa(t,1/i,o),c!==void 0&&(t=Sa(t,1/c,o)),t}function S0(t,s=0,i=1,o=.5,c,d=t,h=t){if(Qt.test(s)&&(s=parseFloat(s),s=ke(h.min,h.max,s/100)-h.min),typeof s!="number")return;let f=ke(d.min,d.max,o);t===d&&(f-=s),t.min=vf(t.min,s,i,f,c),t.max=vf(t.max,s,i,f,c)}function xf(t,s,[i,o,c],d,h){S0(t,s[i],s[o],s[c],s.scale,d,h)}const N0=["x","scaleX","originX"],C0=["y","scaleY","originY"];function wf(t,s,i,o){xf(t.x,s,N0,i?i.x:void 0,o?o.x:void 0),xf(t.y,s,C0,i?i.y:void 0,o?o.y:void 0)}function bf(t){return t.translate===0&&t.scale===1}function Kg(t){return bf(t.x)&&bf(t.y)}function kf(t,s){return t.min===s.min&&t.max===s.max}function T0(t,s){return kf(t.x,s.x)&&kf(t.y,s.y)}function jf(t,s){return Math.round(t.min)===Math.round(s.min)&&Math.round(t.max)===Math.round(s.max)}function qg(t,s){return jf(t.x,s.x)&&jf(t.y,s.y)}function Sf(t){return ct(t.x)/ct(t.y)}function Nf(t,s){return t.translate===s.translate&&t.scale===s.scale&&t.originPoint===s.originPoint}function qt(t){return[t("x"),t("y")]}function P0(t,s,i){let o="";const c=t.x.translate/s.x,d=t.y.translate/s.y,h=(i==null?void 0:i.z)||0;if((c||d||h)&&(o=`translate3d(${c}px, ${d}px, ${h}px) `),(s.x!==1||s.y!==1)&&(o+=`scale(${1/s.x}, ${1/s.y}) `),i){const{transformPerspective:v,rotate:g,pathRotation:x,rotateX:w,rotateY:j,skewX:k,skewY:S}=i;v&&(o=`perspective(${v}px) ${o}`),g&&(o+=`rotate(${g}deg) `),x&&(o+=`rotate(${x}deg) `),w&&(o+=`rotateX(${w}deg) `),j&&(o+=`rotateY(${j}deg) `),k&&(o+=`skewX(${k}deg) `),S&&(o+=`skewY(${S}deg) `)}const f=t.x.scale*s.x,p=t.y.scale*s.y;return(f!==1||p!==1)&&(o+=`scale(${f}, ${p})`),o||"none"}const M0=cu.length,Cf=t=>typeof t=="string"?parseFloat(t):t,Tf=t=>typeof t=="number"||ee.test(t);function E0(t,s,i,o,c,d){c?(t.opacity=ke(0,i.opacity??1,A0(o)),t.opacityExit=ke(s.opacity??1,0,_0(o))):d&&(t.opacity=ke(s.opacity??1,i.opacity??1,o));for(let h=0;h<M0;h++){const f=cu[h];let p=Pf(s,f),v=Pf(i,f);if(p===void 0&&v===void 0)continue;p||(p=0),v||(v=0),p===0||v===0||Tf(p)===Tf(v)?(t[f]=Math.max(ke(Cf(p),Cf(v),o),0),(Qt.test(v)||Qt.test(p))&&(t[f]+="%")):t[f]=v}(s.rotate||i.rotate)&&(t.rotate=ke(s.rotate||0,i.rotate||0,o))}function Pf(t,s){return t[s]!==void 0?t[s]:t.borderRadius}const A0=Xg(0,.5,Op),_0=Xg(.5,.95,zt);function Xg(t,s,i){return o=>o<t?0:o>s?1:i(Ar(t,s,o))}function D0(t,s,i){const o=et(t)?t:Is(t);return o.start(au("",o,s,i)),o.animation}function Lr(t,s,i,o={passive:!0}){return t.addEventListener(s,i,o),()=>t.removeEventListener(s,i,o)}const R0=(t,s)=>t.depth-s.depth;class L0{constructor(){this.children=[],this.isDirty=!1}add(s){$c(this.children,s),this.isDirty=!0}remove(s){ya(this.children,s),this.isDirty=!0}forEach(s){this.isDirty&&this.children.sort(R0),this.isDirty=!1,this.children.forEach(s)}}function I0(t,s){const i=it.now(),o=({timestamp:c})=>{const d=c-i;d>=s&&(En(o),t(d-s))};return je.setup(o,!0),()=>En(o)}function ha(t){return et(t)?t.get():t}class V0{constructor(){this.members=[]}add(s){$c(this.members,s);for(let i=this.members.length-1;i>=0;i--){const o=this.members[i];if(o===s||o===this.lead||o===this.prevLead)continue;const c=o.instance;(!c||c.isConnected===!1)&&!o.snapshot&&(ya(this.members,o),o.unmount())}s.scheduleRender()}remove(s){if(ya(this.members,s),s===this.prevLead&&(this.prevLead=void 0),s===this.lead){const i=this.members[this.members.length-1];i&&this.promote(i)}}relegate(s){var i;for(let o=this.members.indexOf(s)-1;o>=0;o--){const c=this.members[o];if(c.isPresent!==!1&&((i=c.instance)==null?void 0:i.isConnected)!==!1)return this.promote(c),!0}return!1}promote(s,i){var c;const o=this.lead;if(s!==o&&(this.prevLead=o,this.lead=s,s.show(),o)){o.updateSnapshot(),s.scheduleRender();const{layoutDependency:d}=o.options,{layoutDependency:h}=s.options;(d===void 0||d!==h)&&(s.resumeFrom=o,i&&(o.preserveOpacity=!0),o.snapshot&&(s.snapshot=o.snapshot,s.snapshot.latestValues=o.animationValues||o.latestValues),(c=s.root)!=null&&c.isUpdating&&(s.isLayoutDirty=!0)),s.options.crossfade===!1&&o.hide()}}exitAnimationComplete(){this.members.forEach(s=>{var i,o,c,d,h;(o=(i=s.options).onExitComplete)==null||o.call(i),(h=(c=s.resumingFrom)==null?void 0:(d=c.options).onExitComplete)==null||h.call(d)})}scheduleRender(){this.members.forEach(s=>s.instance&&s.scheduleRender(!1))}removeLeadSnapshot(){var s;(s=this.lead)!=null&&s.snapshot&&(this.lead.snapshot=void 0)}}const ma={hasAnimatedSinceResize:!0,hasEverUpdated:!1},Ql=["","X","Y","Z"],F0=1e3;let B0=0;function Jl(t,s,i,o){const{latestValues:c}=s;c[t]&&(i[t]=c[t],s.setStaticValue(t,0),o&&(o[t]=0))}function Yg(t){if(t.hasCheckedOptimisedAppear=!0,t.root===t)return;const{visualElement:s}=t.options;if(!s)return;const i=bg(s);if(window.MotionHasOptimisedAnimation(i,"transform")){const{layout:c,layoutId:d}=t.options;window.MotionCancelOptimisedAnimation(i,"transform",je,!(c||d))}const{parent:o}=t;o&&!o.hasCheckedOptimisedAppear&&Yg(o)}function Qg({attachResizeListener:t,defaultParent:s,measureScroll:i,checkIsScrollRoot:o,resetTransform:c}){return class{constructor(h={},f=s==null?void 0:s()){this.id=B0++,this.animationId=0,this.animationCommitId=0,this.children=new Set,this.options={},this.isTreeAnimating=!1,this.isAnimationBlocked=!1,this.isLayoutDirty=!1,this.isProjectionDirty=!1,this.isSharedProjectionDirty=!1,this.isTransformDirty=!1,this.updateManuallyBlocked=!1,this.updateBlockedByResize=!1,this.isUpdating=!1,this.isSVG=!1,this.needsReset=!1,this.shouldResetTransform=!1,this.hasCheckedOptimisedAppear=!1,this.treeScale={x:1,y:1},this.eventHandlers=new Map,this.hasTreeAnimated=!1,this.layoutVersion=0,this.updateScheduled=!1,this.scheduleUpdate=()=>this.update(),this.projectionUpdateScheduled=!1,this.checkUpdateFailed=()=>{this.isUpdating&&(this.isUpdating=!1,this.clearAllSnapshots())},this.updateProjection=()=>{this.projectionUpdateScheduled=!1,this.nodes.forEach(U0),this.nodes.forEach(q0),this.nodes.forEach(X0),this.nodes.forEach(W0)},this.resolvedRelativeTargetAt=0,this.linkedParentVersion=0,this.hasProjected=!1,this.isVisible=!0,this.animationProgress=0,this.sharedNodes=new Map,this.latestValues=h,this.root=f?f.root||f:this,this.path=f?[...f.path,f]:[],this.parent=f,this.depth=f?f.depth+1:0;for(let p=0;p<this.path.length;p++)this.path[p].shouldResetTransform=!0;this.root===this&&(this.nodes=new L0)}addEventListener(h,f){return this.eventHandlers.has(h)||this.eventHandlers.set(h,new va),this.eventHandlers.get(h).add(f)}notifyListeners(h,...f){const p=this.eventHandlers.get(h);p&&p.notify(...f)}hasListeners(h){return this.eventHandlers.has(h)}mount(h){if(this.instance)return;this.isSVG=uu(h)&&!t0(h),this.instance=h;const{layoutId:f,layout:p,visualElement:v}=this.options;if(v&&!v.current&&v.mount(h),this.root.nodes.add(this),this.parent&&this.parent.children.add(this),this.root.hasTreeAnimated&&(p||f)&&(this.isLayoutDirty=!0),t){let g,x=0;const w=()=>this.root.updateBlockedByResize=!1;je.read(()=>{x=window.innerWidth}),t(h,()=>{const j=window.innerWidth;j!==x&&(x=j,this.root.updateBlockedByResize=!0,g&&g(),g=I0(w,250),ma.hasAnimatedSinceResize&&(ma.hasAnimatedSinceResize=!1,this.nodes.forEach(Af)))})}f&&this.root.registerSharedNode(f,this),this.options.animate!==!1&&v&&(f||p)&&this.addEventListener("didUpdate",({delta:g,hasLayoutChanged:x,hasRelativeLayoutChanged:w,layout:j})=>{if(this.isTreeAnimationBlocked()){this.target=void 0,this.relativeTarget=void 0;return}const k=this.options.transition||v.getDefaultTransition()||ej,{onLayoutAnimationStart:S,onLayoutAnimationComplete:N}=v.getProps(),B=!this.targetLayout||!qg(this.targetLayout,j),E=!x&&w;if(this.options.layoutRoot||this.resumeFrom||E||x&&(B||!this.currentAnimation)){this.resumeFrom&&(this.resumingFrom=this.resumeFrom,this.resumingFrom.resumingFrom=void 0);const R={...iu(k,"layout"),onPlay:S,onComplete:N};(v.shouldReduceMotion||this.options.layoutRoot)&&(R.delay=0,R.type=!1),this.startAnimation(R),this.setAnimationOrigin(g,E,R.path)}else x||Af(this),this.isLead()&&this.options.onExitComplete&&this.options.onExitComplete();this.targetLayout=j})}unmount(){this.options.layoutId&&this.willUpdate(),this.root.nodes.remove(this);const h=this.getStack();h&&h.remove(this),this.parent&&this.parent.children.delete(this),this.instance=void 0,this.eventHandlers.clear(),En(this.updateProjection)}blockUpdate(){this.updateManuallyBlocked=!0}unblockUpdate(){this.updateManuallyBlocked=!1}isUpdateBlocked(){return this.updateManuallyBlocked||this.updateBlockedByResize}isTreeAnimationBlocked(){return this.isAnimationBlocked||this.parent&&this.parent.isTreeAnimationBlocked()||!1}startUpdate(){this.isUpdateBlocked()||(this.isUpdating=!0,this.nodes&&this.nodes.forEach(Y0),this.animationId++)}getTransformTemplate(){const{visualElement:h}=this.options;return h&&h.getProps().transformTemplate}willUpdate(h=!0){if(this.root.hasTreeAnimated=!0,this.root.isUpdateBlocked()){this.options.onExitComplete&&this.options.onExitComplete();return}if(window.MotionCancelOptimisedAnimation&&!this.hasCheckedOptimisedAppear&&Yg(this),!this.root.isUpdating&&this.root.startUpdate(),this.isLayoutDirty)return;this.isLayoutDirty=!0;for(let g=0;g<this.path.length;g++){const x=this.path[g];x.shouldResetTransform=!0,(typeof x.latestValues.x=="string"||typeof x.latestValues.y=="string")&&(x.isLayoutDirty=!0),x.updateScroll("snapshot"),x.options.layoutRoot&&x.willUpdate(!1)}const{layoutId:f,layout:p}=this.options;if(f===void 0&&!p)return;const v=this.getTransformTemplate();this.prevTransformTemplateValue=v?v(this.latestValues,""):void 0,this.updateSnapshot(),h&&this.notifyListeners("willUpdate")}update(){if(this.updateScheduled=!1,this.isUpdateBlocked()){const p=this.updateBlockedByResize;this.unblockUpdate(),this.updateBlockedByResize=!1,this.clearAllSnapshots(),p&&this.nodes.forEach(H0),this.nodes.forEach(Mf);return}if(this.animationId<=this.animationCommitId){this.nodes.forEach(Ef);return}this.animationCommitId=this.animationId,this.isUpdating?(this.isUpdating=!1,this.nodes.forEach(G0),this.nodes.forEach(K0),this.nodes.forEach(O0),this.nodes.forEach(z0)):this.nodes.forEach(Ef),this.clearAllSnapshots();const f=it.now();Ge.delta=Ut(0,1e3/60,f-Ge.timestamp),Ge.timestamp=f,Ge.isProcessing=!0,Wl.update.process(Ge),Wl.preRender.process(Ge),Wl.render.process(Ge),Ge.isProcessing=!1}didUpdate(){this.updateScheduled||(this.updateScheduled=!0,hu.read(this.scheduleUpdate))}clearAllSnapshots(){this.nodes.forEach($0),this.sharedNodes.forEach(Q0)}scheduleUpdateProjection(){this.projectionUpdateScheduled||(this.projectionUpdateScheduled=!0,je.preRender(this.updateProjection,!1,!0))}scheduleCheckAfterUnmount(){je.postRender(()=>{this.isLayoutDirty?this.root.didUpdate():this.root.checkUpdateFailed()})}updateSnapshot(){this.snapshot||!this.instance||(this.snapshot=this.measure(),this.snapshot&&!ct(this.snapshot.measuredBox.x)&&!ct(this.snapshot.measuredBox.y)&&(this.snapshot=void 0))}updateLayout(){if(!this.instance||(this.updateScroll(),!(this.options.alwaysMeasureLayout&&this.isLead())&&!this.isLayoutDirty))return;if(this.resumeFrom&&!this.resumeFrom.instance)for(let p=0;p<this.path.length;p++)this.path[p].updateScroll();const h=this.layout;this.layout=this.measure(!1),this.layoutVersion++,this.layoutCorrected||(this.layoutCorrected=He()),this.isLayoutDirty=!1,this.projectionDelta=void 0,this.notifyListeners("measure",this.layout.layoutBox);const{visualElement:f}=this.options;f&&f.notify("LayoutMeasure",this.layout.layoutBox,h?h.layoutBox:void 0)}updateScroll(h="measure"){let f=!!(this.options.layoutScroll&&this.instance);if(this.scroll&&this.scroll.animationId===this.root.animationId&&this.scroll.phase===h&&(f=!1),f&&this.instance){const p=o(this.instance);this.scroll={animationId:this.root.animationId,phase:h,isRoot:p,offset:i(this.instance),wasRoot:this.scroll?this.scroll.isRoot:p}}}resetTransform(){if(!c)return;const h=this.isLayoutDirty||this.shouldResetTransform||this.options.alwaysMeasureLayout,f=this.projectionDelta&&!Kg(this.projectionDelta),p=this.getTransformTemplate(),v=p?p(this.latestValues,""):void 0,g=v!==this.prevTransformTemplateValue;h&&this.instance&&(f||qn(this.latestValues)||g)&&(c(this.instance,v),this.shouldResetTransform=!1,this.scheduleRender())}measure(h=!0){const f=this.measurePageBox();let p=this.removeElementScroll(f);return h&&(p=this.removeTransform(p)),tj(p),{animationId:this.root.animationId,measuredBox:f,layoutBox:p,latestValues:{},source:this.id}}measurePageBox(){var v;const{visualElement:h}=this.options;if(!h)return He();const f=h.measureViewportBox();if(!(((v=this.scroll)==null?void 0:v.wasRoot)||this.path.some(nj))){const{scroll:g}=this.root;g&&(Xt(f.x,g.offset.x),Xt(f.y,g.offset.y))}return f}removeElementScroll(h){var p;const f=He();if(Bt(f,h),(p=this.scroll)!=null&&p.wasRoot)return f;for(let v=0;v<this.path.length;v++){const g=this.path[v],{scroll:x,options:w}=g;g!==this.root&&x&&w.layoutScroll&&(x.wasRoot&&Bt(f,h),Xt(f.x,x.offset.x),Xt(f.y,x.offset.y))}return f}applyTransform(h,f=!1,p){var g,x;const v=p||He();Bt(v,h);for(let w=0;w<this.path.length;w++){const j=this.path[w];!f&&j.options.layoutScroll&&j.scroll&&j!==j.root&&(Xt(v.x,-j.scroll.offset.x),Xt(v.y,-j.scroll.offset.y)),qn(j.latestValues)&&la(v,j.latestValues,(g=j.layout)==null?void 0:g.layoutBox)}return qn(this.latestValues)&&la(v,this.latestValues,(x=this.layout)==null?void 0:x.layoutBox),v}removeTransform(h){var p;const f=He();Bt(f,h);for(let v=0;v<this.path.length;v++){const g=this.path[v];if(!qn(g.latestValues))continue;let x;g.instance&&(Lc(g.latestValues)&&g.updateSnapshot(),x=He(),Bt(x,g.measurePageBox())),wf(f,g.latestValues,(p=g.snapshot)==null?void 0:p.layoutBox,x)}return qn(this.latestValues)&&wf(f,this.latestValues),f}setTargetDelta(h){this.targetDelta=h,this.root.scheduleUpdateProjection(),this.isProjectionDirty=!0}setOptions(h){this.options={...this.options,...h,crossfade:h.crossfade!==void 0?h.crossfade:!0}}clearMeasurements(){this.scroll=void 0,this.layout=void 0,this.snapshot=void 0,this.prevTransformTemplateValue=void 0,this.targetDelta=void 0,this.target=void 0,this.isLayoutDirty=!1}forceRelativeParentToResolveTarget(){this.relativeParent&&this.relativeParent.resolvedRelativeTargetAt!==Ge.timestamp&&this.relativeParent.resolveTargetDelta(!0)}resolveTargetDelta(h=!1){var j;const f=this.getLead();this.isProjectionDirty||(this.isProjectionDirty=f.isProjectionDirty),this.isTransformDirty||(this.isTransformDirty=f.isTransformDirty),this.isSharedProjectionDirty||(this.isSharedProjectionDirty=f.isSharedProjectionDirty);const p=!!this.resumingFrom||this!==f;if(!(h||p&&this.isSharedProjectionDirty||this.isProjectionDirty||(j=this.parent)!=null&&j.isProjectionDirty||this.attemptToResolveRelativeTarget||this.root.updateBlockedByResize))return;const{layout:g,layoutId:x}=this.options;if(!this.layout||!(g||x))return;this.resolvedRelativeTargetAt=Ge.timestamp;const w=this.getClosestProjectingParent();w&&this.linkedParentVersion!==w.layoutVersion&&!w.options.layoutRoot&&this.removeRelativeTarget(),!this.targetDelta&&!this.relativeTarget&&(this.options.layoutAnchor!==!1&&w&&w.layout?this.createRelativeTarget(w,this.layout.layoutBox,w.layout.layoutBox):this.removeRelativeTarget()),!(!this.relativeTarget&&!this.targetDelta)&&(this.target||(this.target=He(),this.targetWithTransforms=He()),this.relativeTarget&&this.relativeTargetOrigin&&this.relativeParent&&this.relativeParent.target?(this.forceRelativeParentToResolveTarget(),j0(this.target,this.relativeTarget,this.relativeParent.target,this.options.layoutAnchor||void 0)):this.targetDelta?(this.resumingFrom?this.applyTransform(this.layout.layoutBox,!1,this.target):Bt(this.target,this.layout.layoutBox),Pg(this.target,this.targetDelta)):Bt(this.target,this.layout.layoutBox),this.attemptToResolveRelativeTarget&&(this.attemptToResolveRelativeTarget=!1,this.options.layoutAnchor!==!1&&w&&!!w.resumingFrom==!!this.resumingFrom&&!w.options.layoutScroll&&w.target&&this.animationProgress!==1?this.createRelativeTarget(w,this.target,w.target):this.relativeParent=this.relativeTarget=void 0))}getClosestProjectingParent(){if(!(!this.parent||Lc(this.parent.latestValues)||Tg(this.parent.latestValues)))return this.parent.isProjecting()?this.parent:this.parent.getClosestProjectingParent()}isProjecting(){return!!((this.relativeTarget||this.targetDelta||this.options.layoutRoot)&&this.layout)}createRelativeTarget(h,f,p){this.relativeParent=h,this.linkedParentVersion=h.layoutVersion,this.forceRelativeParentToResolveTarget(),this.relativeTarget=He(),this.relativeTargetOrigin=He(),Pa(this.relativeTargetOrigin,f,p,this.options.layoutAnchor||void 0),Bt(this.relativeTarget,this.relativeTargetOrigin)}removeRelativeTarget(){this.relativeParent=this.relativeTarget=void 0}calcProjection(){var k;const h=this.getLead(),f=!!this.resumingFrom||this!==h;let p=!0;if((this.isProjectionDirty||(k=this.parent)!=null&&k.isProjectionDirty)&&(p=!1),f&&(this.isSharedProjectionDirty||this.isTransformDirty)&&(p=!1),this.resolvedRelativeTargetAt===Ge.timestamp&&(p=!1),p)return;const{layout:v,layoutId:g}=this.options;if(this.isTreeAnimating=!!(this.parent&&this.parent.isTreeAnimating||this.currentAnimation||this.pendingAnimation),this.isTreeAnimating||(this.targetDelta=this.relativeTarget=void 0),!this.layout||!(v||g))return;Bt(this.layoutCorrected,this.layout.layoutBox);const x=this.treeScale.x,w=this.treeScale.y;Ik(this.layoutCorrected,this.treeScale,this.path,f),h.layout&&!h.target&&(this.treeScale.x!==1||this.treeScale.y!==1)&&(h.target=h.layout.layoutBox,h.targetWithTransforms=He());const{target:j}=h;if(!j){this.prevProjectionDelta&&(this.createProjectionDeltas(),this.scheduleRender());return}!this.projectionDelta||!this.prevProjectionDelta?this.createProjectionDeltas():(ff(this.prevProjectionDelta.x,this.projectionDelta.x),ff(this.prevProjectionDelta.y,this.projectionDelta.y)),Mr(this.projectionDelta,this.layoutCorrected,j,this.latestValues),(this.treeScale.x!==x||this.treeScale.y!==w||!Nf(this.projectionDelta.x,this.prevProjectionDelta.x)||!Nf(this.projectionDelta.y,this.prevProjectionDelta.y))&&(this.hasProjected=!0,this.scheduleRender(),this.notifyListeners("projectionUpdate",j))}hide(){this.isVisible=!1}show(){this.isVisible=!0}scheduleRender(h=!0){var f;if((f=this.options.visualElement)==null||f.scheduleRender(),h){const p=this.getStack();p&&p.scheduleRender()}this.resumingFrom&&!this.resumingFrom.instance&&(this.resumingFrom=void 0)}createProjectionDeltas(){this.prevProjectionDelta=Rs(),this.projectionDelta=Rs(),this.projectionDeltaWithTransform=Rs()}setAnimationOrigin(h,f=!1,p){const v=this.snapshot,g=v?v.latestValues:{},x={...this.latestValues},w=Rs();(!this.relativeParent||!this.relativeParent.options.layoutRoot)&&(this.relativeTarget=this.relativeTargetOrigin=void 0),this.attemptToResolveRelativeTarget=!f;const j=He(),k=v?v.source:void 0,S=this.layout?this.layout.source:void 0,N=k!==S,B=this.getStack(),E=!B||B.members.length<=1,R=!!(N&&!E&&this.options.crossfade===!0&&!this.path.some(Z0));this.animationProgress=0;let I;const D=p==null?void 0:p.interpolateProjection(h);this.mixTargetDelta=F=>{const V=F/1e3,z=D==null?void 0:D(V);z?(w.x.translate=z.x,w.x.scale=ke(h.x.scale,1,V),w.x.origin=h.x.origin,w.x.originPoint=h.x.originPoint,w.y.translate=z.y,w.y.scale=ke(h.y.scale,1,V),w.y.origin=h.y.origin,w.y.originPoint=h.y.originPoint):(_f(w.x,h.x,V),_f(w.y,h.y,V)),this.setTargetDelta(w),this.relativeTarget&&this.relativeTargetOrigin&&this.layout&&this.relativeParent&&this.relativeParent.layout&&(Pa(j,this.layout.layoutBox,this.relativeParent.layout.layoutBox,this.options.layoutAnchor||void 0),J0(this.relativeTarget,this.relativeTargetOrigin,j,V),I&&T0(this.relativeTarget,I)&&(this.isProjectionDirty=!1),I||(I=He()),Bt(I,this.relativeTarget)),N&&(this.animationValues=x,E0(x,g,this.latestValues,V,R,E)),z&&z.rotate!==void 0&&(this.animationValues||(this.animationValues=x),this.animationValues.pathRotation=z.rotate),this.root.scheduleUpdateProjection(),this.scheduleRender(),this.animationProgress=V},this.mixTargetDelta(this.options.layoutRoot?1e3:0)}startAnimation(h){var f,p,v;this.notifyListeners("animationStart"),(f=this.currentAnimation)==null||f.stop(),(v=(p=this.resumingFrom)==null?void 0:p.currentAnimation)==null||v.stop(),this.pendingAnimation&&(En(this.pendingAnimation),this.pendingAnimation=void 0),this.pendingAnimation=je.update(()=>{ma.hasAnimatedSinceResize=!0,this.motionValue||(this.motionValue=Is(0)),this.motionValue.jump(0,!1),this.currentAnimation=D0(this.motionValue,[0,1e3],{...h,velocity:0,isSync:!0,onUpdate:g=>{this.mixTargetDelta(g),h.onUpdate&&h.onUpdate(g)},onComplete:()=>{h.onComplete&&h.onComplete(),this.completeAnimation()}}),xb(this.currentAnimation,this),this.resumingFrom&&(this.resumingFrom.currentAnimation=this.currentAnimation),this.pendingAnimation=void 0})}completeAnimation(){this.resumingFrom&&(this.resumingFrom.currentAnimation=void 0,this.resumingFrom.preserveOpacity=void 0);const h=this.getStack();h&&h.exitAnimationComplete(),this.resumingFrom=this.currentAnimation=this.animationValues=void 0,this.notifyListeners("animationComplete")}finishAnimation(){this.currentAnimation&&(this.mixTargetDelta&&this.mixTargetDelta(F0),this.currentAnimation.stop()),this.completeAnimation()}applyTransformsToTarget(){const h=this.getLead(),{targetWithTransforms:f,layout:p,latestValues:v}=h;let{target:g}=h;if(!(!f||!g||!p)){if(this!==h&&this.layout&&p&&Jg(this.options.animationType,this.layout.layoutBox,p.layoutBox)){g=this.target||He();const x=ct(this.layout.layoutBox.x);g.x.min=h.target.x.min,g.x.max=g.x.min+x;const w=ct(this.layout.layoutBox.y);g.y.min=h.target.y.min,g.y.max=g.y.min+w}Bt(f,g),la(f,v),Mr(this.projectionDeltaWithTransform,this.layoutCorrected,f,v)}}registerSharedNode(h,f){this.sharedNodes.has(h)||this.sharedNodes.set(h,new V0),this.sharedNodes.get(h).add(f);const v=f.options.initialPromotionConfig;f.promote({transition:v?v.transition:void 0,preserveFollowOpacity:v&&v.shouldPreserveFollowOpacity?v.shouldPreserveFollowOpacity(f):void 0})}isLead(){const h=this.getStack();return h?h.lead===this:!0}getLead(){var f;const{layoutId:h}=this.options;return h?((f=this.getStack())==null?void 0:f.lead)||this:this}getPrevLead(){var f;const{layoutId:h}=this.options;return h?(f=this.getStack())==null?void 0:f.prevLead:void 0}getStack(){const{layoutId:h}=this.options;if(h)return this.root.sharedNodes.get(h)}promote({needsReset:h,transition:f,preserveFollowOpacity:p}={}){const v=this.getStack();v&&v.promote(this,p),h&&(this.projectionDelta=void 0,this.needsReset=!0),f&&this.setOptions({transition:f})}relegate(){const h=this.getStack();return h?h.relegate(this):!1}resetSkewAndRotation(){const{visualElement:h}=this.options;if(!h)return;let f=!1;const{latestValues:p}=h;if((p.z||p.rotate||p.rotateX||p.rotateY||p.rotateZ||p.skewX||p.skewY)&&(f=!0),!f)return;const v={};p.z&&Jl("z",h,v,this.animationValues);for(let g=0;g<Ql.length;g++)Jl(`rotate${Ql[g]}`,h,v,this.animationValues),Jl(`skew${Ql[g]}`,h,v,this.animationValues);h.render();for(const g in v)h.setStaticValue(g,v[g]),this.animationValues&&(this.animationValues[g]=v[g]);h.scheduleRender()}applyProjectionStyles(h,f){if(!this.instance||this.isSVG)return;if(!this.isVisible){h.visibility="hidden";return}const p=this.getTransformTemplate();if(this.needsReset){this.needsReset=!1,h.visibility="",h.opacity="",h.pointerEvents=ha(f==null?void 0:f.pointerEvents)||"",h.transform=p?p(this.latestValues,""):"none";return}const v=this.getLead();if(!this.projectionDelta||!this.layout||!v.target){this.options.layoutId&&(h.opacity=this.latestValues.opacity!==void 0?this.latestValues.opacity:1,h.pointerEvents=ha(f==null?void 0:f.pointerEvents)||""),this.hasProjected&&!qn(this.latestValues)&&(h.transform=p?p({},""):"none",this.hasProjected=!1);return}h.visibility="";const g=v.animationValues||v.latestValues;this.applyTransformsToTarget();let x=P0(this.projectionDeltaWithTransform,this.treeScale,g);p&&(x=p(g,x)),h.transform=x;const{x:w,y:j}=this.projectionDelta;h.transformOrigin=`${w.origin*100}% ${j.origin*100}% 0`,v.animationValues?h.opacity=v===this?g.opacity??this.latestValues.opacity??1:this.preserveOpacity?this.latestValues.opacity:g.opacityExit:h.opacity=v===this?g.opacity!==void 0?g.opacity:"":g.opacityExit!==void 0?g.opacityExit:0;for(const k in Vc){if(g[k]===void 0)continue;const{correct:S,applyTo:N,isCSSVariable:B}=Vc[k],E=x==="none"?g[k]:S(g[k],v);if(N){const R=N.length;for(let I=0;I<R;I++)h[N[I]]=E}else B?this.options.visualElement.renderState.vars[k]=E:h[k]=E}this.options.layoutId&&(h.pointerEvents=v===this?ha(f==null?void 0:f.pointerEvents)||"":"none")}clearSnapshot(){this.resumeFrom=this.snapshot=void 0}resetTree(){this.root.nodes.forEach(h=>{var f;return(f=h.currentAnimation)==null?void 0:f.stop()}),this.root.nodes.forEach(Mf),this.root.sharedNodes.clear()}}}function O0(t){t.updateLayout()}function z0(t){var i;const s=((i=t.resumeFrom)==null?void 0:i.snapshot)||t.snapshot;if(t.isLead()&&t.layout&&s&&t.hasListeners("didUpdate")){const{layoutBox:o,measuredBox:c}=t.layout,{animationType:d}=t.options,h=s.source!==t.layout.source;if(d==="size")qt(x=>{const w=h?s.measuredBox[x]:s.layoutBox[x],j=ct(w);w.min=o[x].min,w.max=w.min+j});else if(d==="x"||d==="y"){const x=d==="x"?"y":"x";Fc(h?s.measuredBox[x]:s.layoutBox[x],o[x])}else Jg(d,s.layoutBox,o)&&qt(x=>{const w=h?s.measuredBox[x]:s.layoutBox[x],j=ct(o[x]);w.max=w.min+j,t.relativeTarget&&!t.currentAnimation&&(t.isProjectionDirty=!0,t.relativeTarget[x].max=t.relativeTarget[x].min+j)});const f=Rs();Mr(f,o,s.layoutBox);const p=Rs();h?Mr(p,t.applyTransform(c,!0),s.measuredBox):Mr(p,o,s.layoutBox);const v=!Kg(f);let g=!1;if(!t.resumeFrom){const x=t.getClosestProjectingParent();if(x&&!x.resumeFrom){const{snapshot:w,layout:j}=x;if(w&&j){const k=t.options.layoutAnchor||void 0,S=He();Pa(S,s.layoutBox,w.layoutBox,k);const N=He();Pa(N,o,j.layoutBox,k),qg(S,N)||(g=!0),x.options.layoutRoot&&(t.relativeTarget=N,t.relativeTargetOrigin=S,t.relativeParent=x)}}}t.notifyListeners("didUpdate",{layout:o,snapshot:s,delta:p,layoutDelta:f,hasLayoutChanged:v,hasRelativeLayoutChanged:g})}else if(t.isLead()){const{onExitComplete:o}=t.options;o&&o()}t.options.transition=void 0}function U0(t){t.parent&&(t.isProjecting()||(t.isProjectionDirty=t.parent.isProjectionDirty),t.isSharedProjectionDirty||(t.isSharedProjectionDirty=!!(t.isProjectionDirty||t.parent.isProjectionDirty||t.parent.isSharedProjectionDirty)),t.isTransformDirty||(t.isTransformDirty=t.parent.isTransformDirty))}function W0(t){t.isProjectionDirty=t.isSharedProjectionDirty=t.isTransformDirty=!1}function $0(t){t.clearSnapshot()}function Mf(t){t.clearMeasurements()}function H0(t){t.isLayoutDirty=!0,t.updateLayout()}function Ef(t){t.isLayoutDirty=!1}function G0(t){t.isAnimationBlocked&&t.layout&&!t.isLayoutDirty&&(t.snapshot=t.layout,t.isLayoutDirty=!0)}function K0(t){const{visualElement:s}=t.options;s&&s.getProps().onBeforeLayoutMeasure&&s.notify("BeforeLayoutMeasure"),t.resetTransform()}function Af(t){t.finishAnimation(),t.targetDelta=t.relativeTarget=t.target=void 0,t.isProjectionDirty=!0}function q0(t){t.resolveTargetDelta()}function X0(t){t.calcProjection()}function Y0(t){t.resetSkewAndRotation()}function Q0(t){t.removeLeadSnapshot()}function _f(t,s,i){t.translate=ke(s.translate,0,i),t.scale=ke(s.scale,1,i),t.origin=s.origin,t.originPoint=s.originPoint}function Df(t,s,i,o){t.min=ke(s.min,i.min,o),t.max=ke(s.max,i.max,o)}function J0(t,s,i,o){Df(t.x,s.x,i.x,o),Df(t.y,s.y,i.y,o)}function Z0(t){return t.animationValues&&t.animationValues.opacityExit!==void 0}const ej={duration:.45,ease:[.4,0,.1,1]},Rf=t=>typeof navigator<"u"&&navigator.userAgent&&navigator.userAgent.toLowerCase().includes(t),Lf=Rf("applewebkit/")&&!Rf("chrome/")?Math.round:zt;function If(t){t.min=Lf(t.min),t.max=Lf(t.max)}function tj(t){If(t.x),If(t.y)}function Jg(t,s,i){return t==="position"||t==="preserve-aspect"&&!k0(Sf(s),Sf(i),.2)}function nj(t){var s;return t!==t.root&&((s=t.scroll)==null?void 0:s.wasRoot)}const sj=Qg({attachResizeListener:(t,s)=>Lr(t,"resize",s),measureScroll:()=>{var t,s;return{x:document.documentElement.scrollLeft||((t=document.body)==null?void 0:t.scrollLeft)||0,y:document.documentElement.scrollTop||((s=document.body)==null?void 0:s.scrollTop)||0}},checkIsScrollRoot:()=>!0}),Zl={current:void 0},Zg=Qg({measureScroll:t=>({x:t.scrollLeft,y:t.scrollTop}),defaultParent:()=>{if(!Zl.current){const t=new sj({});t.mount(window),t.setOptions({layoutScroll:!0}),Zl.current=t}return Zl.current},resetTransform:(t,s)=>{t.style.transform=s!==void 0?s:"none"},checkIsScrollRoot:t=>window.getComputedStyle(t).position==="fixed"}),ey=P.createContext({transformPagePoint:t=>t,isStatic:!1,reducedMotion:"never"});function rj(t=!0){const s=P.useContext(Wc);if(s===null)return[!0,null];const{isPresent:i,onExitComplete:o,register:c}=s,d=P.useId();P.useEffect(()=>{if(t)return c(d)},[t]);const h=P.useCallback(()=>t&&o&&o(d),[d,o,t]);return!i&&o?[!1,h]:[!0]}const ty=P.createContext({strict:!1}),Vf={animation:["animate","variants","whileHover","whileTap","exit","whileInView","whileFocus","whileDrag"],exit:["exit"],drag:["drag","dragControls"],focus:["whileFocus"],hover:["whileHover","onHoverStart","onHoverEnd"],tap:["whileTap","onTap","onTapStart","onTapCancel"],pan:["onPan","onPanStart","onPanSessionStart","onPanEnd"],inView:["whileInView","onViewportEnter","onViewportLeave"],layout:["layout","layoutId"]};let Ff=!1;function ij(){if(Ff)return;const t={};for(const s in Vf)t[s]={isEnabled:i=>Vf[s].some(o=>!!i[o])};Ig(t),Ff=!0}function ny(){return ij(),i0()}function aj(t){const s=ny();for(const i in t)s[i]={...s[i],...t[i]};Ig(s)}const Va=P.createContext({});function oj(t,s){if(Ia(t)){const{initial:i,animate:o}=t;return{initial:i===!1||Rr(i)?i:void 0,animate:Rr(o)?o:void 0}}return t.inherit!==!1?s:{}}function lj(t){const{initial:s,animate:i}=oj(t,P.useContext(Va));return P.useMemo(()=>({initial:s,animate:i}),[Bf(s),Bf(i)])}function Bf(t){return Array.isArray(t)?t.join(" "):t}const yu=()=>({style:{},transform:{},transformOrigin:{},vars:{}});function sy(t,s,i){for(const o in s)!et(s[o])&&!Bg(o,i)&&(t[o]=s[o])}function cj({transformTemplate:t},s){return P.useMemo(()=>{const i=yu();return du(i,s,t),Object.assign({},i.vars,i.style)},[s])}function uj(t,s){const i=t.style||{},o={};return sy(o,i,t),Object.assign(o,cj(t,s)),o}function dj(t,s){const i={},o=uj(t,s);return t.drag&&t.dragListener!==!1&&(i.draggable=!1,o.userSelect=o.WebkitUserSelect=o.WebkitTouchCallout="none",o.touchAction=t.drag===!0?"none":`pan-${t.drag==="x"?"y":"x"}`),t.tabIndex===void 0&&(t.onTap||t.onTapStart||t.whileTap)&&(i.tabIndex=0),i.style=o,i}const ry=()=>({...yu(),attrs:{}});function hj(t,s,i,o){const c=P.useMemo(()=>{const d=ry();return Ng(d,s,zg(o),t.transformTemplate,t.style),{...d.attrs,style:{...d.style}}},[s]);if(t.style){const d={};sy(d,t.style,t),c.style={...d,...c.style}}return c}const mj=new Set(["animate","exit","variants","initial","style","values","variants","transition","transformTemplate","custom","inherit","onBeforeLayoutMeasure","onAnimationStart","onAnimationComplete","onUpdate","onDragStart","onDrag","onDragEnd","onMeasureDragConstraints","onDirectionLock","onDragTransitionEnd","_dragX","_dragY","onHoverStart","onHoverEnd","onViewportEnter","onViewportLeave","globalTapTarget","propagate","ignoreStrict","viewport"]);function Ma(t){return t.startsWith("while")||t.startsWith("drag")&&t!=="draggable"||t.startsWith("layout")||t.startsWith("onTap")||t.startsWith("onPan")||t.startsWith("onLayout")||mj.has(t)}function fj(t,s){return t.startsWith("on")?!Ma(t):(s==null?void 0:s(t))??!Ma(t)}function pj(t,s,i,o){const c={};for(const d in t)d==="values"&&typeof t.values=="object"||et(t[d])||(fj(d,o)||i===!0&&Ma(d)||!s&&!Ma(d)||t.draggable&&d.startsWith("onDrag"))&&(c[d]=t[d]);return c}const gj=["animate","circle","defs","desc","ellipse","g","image","line","filter","marker","mask","metadata","path","pattern","polygon","polyline","rect","stop","switch","symbol","svg","text","tspan","use","view"];function vu(t){return typeof t!="string"||t.includes("-")?!1:!!(gj.indexOf(t)>-1||/[A-Z]/u.test(t))}function yj(t,s,i,{latestValues:o},c,d=!1,h,f){const v=(h??vu(t)?hj:dj)(s,o,c,t),g=pj(s,typeof t=="string",d,f),x=t!==P.Fragment?{...g,...v,ref:i}:{},{children:w}=s,j=P.useMemo(()=>et(w)?w.get():w,[w]);return P.createElement(t,{...x,children:j})}function vj({scrapeMotionValuesFromProps:t,createRenderState:s},i,o,c){return{latestValues:xj(i,o,c,t),renderState:s()}}function xj(t,s,i,o){const c={},d=o(t,{});for(const w in d)c[w]=ha(d[w]);let{initial:h,animate:f}=t;const p=Ia(t),v=Rg(t);s&&v&&!p&&t.inherit!==!1&&(h===void 0&&(h=s.initial),f===void 0&&(f=s.animate));let g=i?i.initial===!1:!1;g=g||h===!1;const x=g?f:h;if(x&&typeof x!="boolean"&&!La(x)){const w=Array.isArray(x)?x:[x];for(let j=0;j<w.length;j++){const k=ou(t,w[j]);if(k){const{transitionEnd:S,transition:N,...B}=k;for(const E in B){let R=B[E];if(Array.isArray(R)){const I=g?R.length-1:0;R=R[I]}R!==null&&(c[E]=R)}for(const E in S)c[E]=S[E]}}}return c}const iy=t=>(s,i)=>{const o=P.useContext(Va),c=P.useContext(Wc),d=()=>vj(t,s,o,c);return i?d():fw(d)},wj=iy({scrapeMotionValuesFromProps:gu,createRenderState:yu}),bj=iy({scrapeMotionValuesFromProps:Ug,createRenderState:ry}),kj=Symbol.for("motionComponentSymbol");function jj(t,s,i){const o=P.useRef(i);P.useInsertionEffect(()=>{o.current=i});const c=P.useRef(null);return P.useCallback(d=>{var f;d&&((f=t.onMount)==null||f.call(t,d)),s&&(d?s.mount(d):s.unmount());const h=o.current;if(typeof h=="function")if(d){const p=h(d);typeof p=="function"&&(c.current=p)}else c.current?(c.current(),c.current=null):h(d);else h&&(h.current=d)},[s])}const ay=P.createContext({});function As(t){return t&&typeof t=="object"&&Object.prototype.hasOwnProperty.call(t,"current")}function Sj(t,s,i,o,c,d){var R,I;const{visualElement:h}=P.useContext(Va),f=P.useContext(ty),p=P.useContext(Wc),v=P.useContext(ey),g=v.reducedMotion,x=v.skipAnimations,w=P.useRef(null),j=P.useRef(!1);o=o||f.renderer,!w.current&&o&&(w.current=o(t,{visualState:s,parent:h,props:i,presenceContext:p,blockInitialAnimation:p?p.initial===!1:!1,reducedMotionConfig:g,skipAnimations:x,isSVG:d}),j.current&&w.current&&(w.current.manuallyAnimateOnMount=!0));const k=w.current,S=P.useContext(ay);k&&!k.projection&&c&&(k.type==="html"||k.type==="svg")&&Nj(w.current,i,c,S);const N=P.useRef(!1);P.useInsertionEffect(()=>{k&&N.current&&k.update(i,p)});const B=i[wg],E=P.useRef(!!B&&typeof window<"u"&&!((R=window.MotionHandoffIsComplete)!=null&&R.call(window,B))&&((I=window.MotionHasOptimisedAnimation)==null?void 0:I.call(window,B)));return gw(()=>{j.current=!0,k&&(N.current=!0,window.MotionIsMounted=!0,k.updateFeatures(),k.scheduleRenderMicrotask(),E.current&&k.animationState&&k.animationState.animateChanges())}),P.useEffect(()=>{k&&(!E.current&&k.animationState&&k.animationState.animateChanges(),E.current&&(queueMicrotask(()=>{var D;(D=window.MotionHandoffMarkAsComplete)==null||D.call(window,B)}),E.current=!1),k.enteringChildren=void 0)}),k}function Nj(t,s,i,o){const{layoutId:c,layout:d,drag:h,dragConstraints:f,layoutScroll:p,layoutRoot:v,layoutAnchor:g,layoutCrossfade:x}=s;t.projection=new i(t.latestValues,s["data-framer-portal-id"]?void 0:oy(t.parent)),t.projection.setOptions({layoutId:c,layout:d,alwaysMeasureLayout:!!h||f&&As(f),visualElement:t,animationType:typeof d=="string"?d:"both",initialPromotionConfig:o,crossfade:x,layoutScroll:p,layoutRoot:v,layoutAnchor:g})}function oy(t){if(t)return t.options.allowProjection!==!1?t.projection:oy(t.parent)}function ec(t,{forwardMotionProps:s=!1,type:i}={},o,c){o&&aj(o);const d=i?i==="svg":vu(t),h=d?bj:wj;function f(v,g){let x;const w={...P.useContext(ey),...v,layoutId:Cj(v)},{isStatic:j,isValidProp:k}=w,S=lj(v),N=h(v,j);if(!j&&typeof window<"u"){Tj();const B=Pj(w);x=B.MeasureLayout,S.visualElement=Sj(t,N,w,c,B.ProjectionNode,d)}return r.jsxs(Va.Provider,{value:S,children:[x&&S.visualElement?r.jsx(x,{visualElement:S.visualElement,...w}):null,yj(t,v,jj(N,S.visualElement,g),N,j,s,d,k)]})}f.displayName=`motion.${typeof t=="string"?t:`create(${t.displayName??t.name??""})`}`;const p=P.forwardRef(f);return p[kj]=t,p}function Cj({layoutId:t}){const s=P.useContext(Ep).id;return s&&t!==void 0?s+"-"+t:t}function Tj(t,s){P.useContext(ty).strict}function Pj(t){const s=ny(),{drag:i,layout:o}=s;if(!i&&!o)return{};const c={...i,...o};return{MeasureLayout:i!=null&&i.isEnabled(t)||o!=null&&o.isEnabled(t)?c.MeasureLayout:void 0,ProjectionNode:c.ProjectionNode}}function Mj(t,s){if(typeof Proxy>"u")return ec;const i=new Map,o=(d,h)=>ec(d,h,t,s),c=(d,h)=>o(d,h);return new Proxy(c,{get:(d,h)=>h==="create"?o:(i.has(h)||i.set(h,ec(h,void 0,t,s)),i.get(h))})}const Ej=(t,s)=>s.isSVG??vu(t)?new d0(s):new c0(s,{allowProjection:t!==P.Fragment});class Aj extends An{constructor(s){super(s),s.animationState||(s.animationState=g0(s))}updateAnimationControlsSubscription(){const{animate:s}=this.node.getProps();La(s)&&(this.unmountControls=s.subscribe(this.node))}mount(){this.updateAnimationControlsSubscription()}update(){const{animate:s}=this.node.getProps(),{animate:i}=this.node.prevProps||{};s!==i&&this.updateAnimationControlsSubscription()}unmount(){var s;this.node.animationState.reset(),(s=this.unmountControls)==null||s.call(this)}}let _j=0;class Dj extends An{constructor(){super(...arguments),this.id=_j++,this.isExitComplete=!1}update(){var d;if(!this.node.presenceContext)return;const{isPresent:s,onExitComplete:i}=this.node.presenceContext,{isPresent:o}=this.node.prevPresenceContext||{};if(!this.node.animationState||s===o)return;if(s&&o===!1){if(this.isExitComplete){const{initial:h,custom:f}=this.node.getProps();if(typeof h=="string"||typeof h=="object"&&h!==null&&!Array.isArray(h)){const p=ns(this.node,h,f);if(p){const{transition:v,transitionEnd:g,...x}=p;for(const w in x)(d=this.node.getValue(w))==null||d.jump(x[w])}}this.node.animationState.reset(),this.node.animationState.animateChanges()}else this.node.animationState.setActive("exit",!1);this.isExitComplete=!1;return}const c=this.node.animationState.setActive("exit",!s);i&&!s&&c.then(()=>{this.isExitComplete=!0,i(this.id)})}mount(){const{register:s,onExitComplete:i}=this.node.presenceContext||{};i&&i(this.id),s&&(this.unmount=s(this.id))}unmount(){}}const Rj={animation:{Feature:Aj},exit:{Feature:Dj}};function Br(t){return{point:{x:t.pageX,y:t.pageY}}}const Lj=t=>s=>mu(s)&&t(s,Br(s));function Er(t,s,i,o){return Lr(t,s,Lj(i),o)}const ly=({current:t})=>t?t.ownerDocument.defaultView:null,Of=(t,s)=>Math.abs(t-s);function Ij(t,s){const i=Of(t.x,s.x),o=Of(t.y,s.y);return Math.sqrt(i**2+o**2)}const zf=new Set(["auto","scroll"]);class cy{constructor(s,i,{transformPagePoint:o,contextWindow:c=window,dragSnapToOrigin:d=!1,distanceThreshold:h=3,element:f}={}){if(this.startEvent=null,this.lastMoveEvent=null,this.lastMoveEventInfo=null,this.lastRawMoveEventInfo=null,this.handlers={},this.contextWindow=window,this.scrollPositions=new Map,this.removeScrollListeners=null,this.onElementScroll=k=>{this.handleScroll(k.target)},this.onWindowScroll=()=>{this.handleScroll(window)},this.updatePoint=()=>{if(!(this.lastMoveEvent&&this.lastMoveEventInfo))return;this.lastRawMoveEventInfo&&(this.lastMoveEventInfo=ta(this.lastRawMoveEventInfo,this.transformPagePoint));const k=tc(this.lastMoveEventInfo,this.history),S=this.startEvent!==null,N=Ij(k.offset,{x:0,y:0})>=this.distanceThreshold;if(!S&&!N)return;const{point:B}=k,{timestamp:E}=Ge;this.history.push({...B,timestamp:E});const{onStart:R,onMove:I}=this.handlers;S||(R&&R(this.lastMoveEvent,k),this.startEvent=this.lastMoveEvent),I&&I(this.lastMoveEvent,k)},this.handlePointerMove=(k,S)=>{this.lastMoveEvent=k,this.lastRawMoveEventInfo=S,this.lastMoveEventInfo=ta(S,this.transformPagePoint),je.update(this.updatePoint,!0)},this.handlePointerUp=(k,S)=>{this.end();const{onEnd:N,onSessionEnd:B,resumeAnimation:E}=this.handlers;if((this.dragSnapToOrigin||!this.startEvent)&&E&&E(),!(this.lastMoveEvent&&this.lastMoveEventInfo))return;const R=tc(k.type==="pointercancel"?this.lastMoveEventInfo:ta(S,this.transformPagePoint),this.history);this.startEvent&&N&&N(k,R),B&&B(k,R)},!mu(s))return;this.dragSnapToOrigin=d,this.handlers=i,this.transformPagePoint=o,this.distanceThreshold=h,this.contextWindow=c||window;const p=Br(s),v=ta(p,this.transformPagePoint),{point:g}=v,{timestamp:x}=Ge;this.history=[{...g,timestamp:x}];const{onSessionStart:w}=i;w&&w(s,tc(v,this.history));const j={passive:!0,capture:!0};this.removeListeners=Ir(Er(this.contextWindow,"pointermove",this.handlePointerMove,j),Er(this.contextWindow,"pointerup",this.handlePointerUp,j),Er(this.contextWindow,"pointercancel",this.handlePointerUp,j)),f&&this.startScrollTracking(f)}startScrollTracking(s){let i=s.parentElement;for(;i;){const o=getComputedStyle(i);(zf.has(o.overflowX)||zf.has(o.overflowY))&&this.scrollPositions.set(i,{x:i.scrollLeft,y:i.scrollTop}),i=i.parentElement}this.scrollPositions.set(window,{x:window.scrollX,y:window.scrollY}),window.addEventListener("scroll",this.onElementScroll,{capture:!0}),window.addEventListener("scroll",this.onWindowScroll),this.removeScrollListeners=()=>{window.removeEventListener("scroll",this.onElementScroll,{capture:!0}),window.removeEventListener("scroll",this.onWindowScroll)}}handleScroll(s){const i=this.scrollPositions.get(s);if(!i)return;const o=s===window,c=o?{x:window.scrollX,y:window.scrollY}:{x:s.scrollLeft,y:s.scrollTop},d={x:c.x-i.x,y:c.y-i.y};d.x===0&&d.y===0||(o?this.lastMoveEventInfo&&(this.lastMoveEventInfo.point.x+=d.x,this.lastMoveEventInfo.point.y+=d.y):this.history.length>0&&(this.history[0].x-=d.x,this.history[0].y-=d.y),this.scrollPositions.set(s,c),je.update(this.updatePoint,!0))}updateHandlers(s){this.handlers=s}end(){this.removeListeners&&this.removeListeners(),this.removeScrollListeners&&this.removeScrollListeners(),this.scrollPositions.clear(),En(this.updatePoint)}}function ta(t,s){return s?{point:s(t.point)}:t}function Uf(t,s){return{x:t.x-s.x,y:t.y-s.y}}function tc({point:t},s){return{point:t,delta:Uf(t,uy(s)),offset:Uf(t,Vj(s)),velocity:Fj(s,.1)}}function Vj(t){return t[0]}function uy(t){return t[t.length-1]}function Fj(t,s){if(t.length<2)return{x:0,y:0};let i=t.length-1,o=null;const c=uy(t);for(;i>=0&&(o=t[i],!(c.timestamp-o.timestamp>At(s)));)i--;if(!o)return{x:0,y:0};o===t[0]&&t.length>2&&c.timestamp-o.timestamp>At(s)*2&&(o=t[1]);const d=kt(c.timestamp-o.timestamp);if(d===0)return{x:0,y:0};const h={x:(c.x-o.x)/d,y:(c.y-o.y)/d};return h.x===1/0&&(h.x=0),h.y===1/0&&(h.y=0),h}function Bj(t,{min:s,max:i},o){return s!==void 0&&t<s?t=o?ke(s,t,o.min):Math.max(t,s):i!==void 0&&t>i&&(t=o?ke(i,t,o.max):Math.min(t,i)),t}function Wf(t,s,i){return{min:s!==void 0?t.min+s:void 0,max:i!==void 0?t.max+i-(t.max-t.min):void 0}}function Oj(t,{top:s,left:i,bottom:o,right:c}){return{x:Wf(t.x,i,c),y:Wf(t.y,s,o)}}function $f(t,s){let i=s.min-t.min,o=s.max-t.max;return s.max-s.min<t.max-t.min&&([i,o]=[o,i]),{min:i,max:o}}function zj(t,s){return{x:$f(t.x,s.x),y:$f(t.y,s.y)}}function Uj(t,s){let i=.5;const o=ct(t),c=ct(s);return c>o?i=Ar(s.min,s.max-o,t.min):o>c&&(i=Ar(t.min,t.max-c,s.min)),Ut(0,1,i)}function Wj(t,s){const i={};return s.min!==void 0&&(i.min=s.min-t.min),s.max!==void 0&&(i.max=s.max-t.min),i}const Bc=.35;function $j(t=Bc){return t===!1?t=0:t===!0&&(t=Bc),{x:Hf(t,"left","right"),y:Hf(t,"top","bottom")}}function Hf(t,s,i){return{min:Gf(t,s),max:Gf(t,i)}}function Gf(t,s){return typeof t=="number"?t:t[s]||0}const Hj=new WeakMap;class Gj{constructor(s){this.openDragLock=null,this.isDragging=!1,this.currentDirection=null,this.originPoint={x:0,y:0},this.constraints=!1,this.hasMutatedConstraints=!1,this.elastic=He(),this.latestPointerEvent=null,this.latestPanInfo=null,this.visualElement=s}start(s,{snapToCursor:i=!1,distanceThreshold:o}={}){const{presenceContext:c}=this.visualElement;if(c&&c.isPresent===!1)return;const d=x=>{i&&this.snapToCursor(Br(x).point),this.stopAnimation()},h=(x,w)=>{const{drag:j,dragPropagation:k,onDragStart:S}=this.getProps();if(j&&!k&&(this.openDragLock&&this.openDragLock(),this.openDragLock=Fk(j),!this.openDragLock))return;this.latestPointerEvent=x,this.latestPanInfo=w,this.isDragging=!0,this.currentDirection=null,this.resolveConstraints(),this.visualElement.projection&&(this.visualElement.projection.isAnimationBlocked=!0,this.visualElement.projection.target=void 0),qt(B=>{let E=this.getAxisMotionValue(B).get()||0;if(Qt.test(E)){const{projection:R}=this.visualElement;if(R&&R.layout){const I=R.layout.layoutBox[B];I&&(E=ct(I)*(parseFloat(E)/100))}}this.originPoint[B]=E}),S&&je.update(()=>S(x,w),!1,!0),_c(this.visualElement,"transform");const{animationState:N}=this.visualElement;N&&N.setActive("whileDrag",!0)},f=(x,w)=>{this.latestPointerEvent=x,this.latestPanInfo=w;const{dragPropagation:j,dragDirectionLock:k,onDirectionLock:S,onDrag:N}=this.getProps();if(!j&&!this.openDragLock)return;const{offset:B}=w;if(k&&this.currentDirection===null){this.currentDirection=qj(B),this.currentDirection!==null&&S&&S(this.currentDirection);return}this.updateAxis("x",w.point,B),this.updateAxis("y",w.point,B),this.visualElement.render(),N&&je.update(()=>N(x,w),!1,!0)},p=(x,w)=>{this.latestPointerEvent=x,this.latestPanInfo=w,this.stop(x,w),this.latestPointerEvent=null,this.latestPanInfo=null},v=()=>{const{dragSnapToOrigin:x}=this.getProps();(x||this.constraints)&&this.startAnimation({x:0,y:0})},{dragSnapToOrigin:g}=this.getProps();this.panSession=new cy(s,{onSessionStart:d,onStart:h,onMove:f,onSessionEnd:p,resumeAnimation:v},{transformPagePoint:this.visualElement.getTransformPagePoint(),dragSnapToOrigin:g,distanceThreshold:o,contextWindow:ly(this.visualElement),element:this.visualElement.current})}stop(s,i){const o=s||this.latestPointerEvent,c=i||this.latestPanInfo,d=this.isDragging;if(this.cancel(),!d||!c||!o)return;const{velocity:h}=c;this.startAnimation(h);const{onDragEnd:f}=this.getProps();f&&je.postRender(()=>f(o,c))}cancel(){this.isDragging=!1;const{projection:s,animationState:i}=this.visualElement;s&&(s.isAnimationBlocked=!1),this.endPanSession();const{dragPropagation:o}=this.getProps();!o&&this.openDragLock&&(this.openDragLock(),this.openDragLock=null),i&&i.setActive("whileDrag",!1)}endPanSession(){this.panSession&&this.panSession.end(),this.panSession=void 0}updateAxis(s,i,o){const{drag:c}=this.getProps();if(!o||!na(s,c,this.currentDirection))return;const d=this.getAxisMotionValue(s);let h=this.originPoint[s]+o[s];this.constraints&&this.constraints[s]&&(h=Bj(h,this.constraints[s],this.elastic[s])),d.set(h)}resolveConstraints(){var d;const{dragConstraints:s,dragElastic:i}=this.getProps(),o=this.visualElement.projection&&!this.visualElement.projection.layout?this.visualElement.projection.measure(!1):(d=this.visualElement.projection)==null?void 0:d.layout,c=this.constraints;s&&As(s)?this.constraints||(this.constraints=this.resolveRefConstraints()):s&&o?this.constraints=Oj(o.layoutBox,s):this.constraints=!1,this.elastic=$j(i),c!==this.constraints&&!As(s)&&o&&this.constraints&&!this.hasMutatedConstraints&&qt(h=>{this.constraints!==!1&&this.getAxisMotionValue(h)&&(this.constraints[h]=Wj(o.layoutBox[h],this.constraints[h]))})}resolveRefConstraints(){const{dragConstraints:s,onMeasureDragConstraints:i}=this.getProps();if(!s||!As(s))return!1;const o=s.current,{projection:c}=this.visualElement;if(!c||!c.layout)return!1;c.root&&(c.root.scroll=void 0,c.root.updateScroll());const d=Vk(o,c.root,this.visualElement.getTransformPagePoint());let h=zj(c.layout.layoutBox,d);if(i){const f=i(Rk(h));this.hasMutatedConstraints=!!f,f&&(h=Cg(f))}return h}startAnimation(s){const{drag:i,dragMomentum:o,dragElastic:c,dragTransition:d,dragSnapToOrigin:h,onDragTransitionEnd:f}=this.getProps(),p=this.constraints||{},v=qt(g=>{if(!na(g,i,this.currentDirection))return;let x=p&&p[g]||{};(h===!0||h===g)&&(x={min:0,max:0});const w=c?200:1e6,j=c?40:1e7,k={type:"inertia",velocity:o?s[g]:0,bounceStiffness:w,bounceDamping:j,timeConstant:750,restDelta:1,restSpeed:10,...d,...x};return this.startAxisValueAnimation(g,k)});return Promise.all(v).then(f)}startAxisValueAnimation(s,i){const o=this.getAxisMotionValue(s);return _c(this.visualElement,s),o.start(au(s,o,0,i,this.visualElement,!1))}stopAnimation(){qt(s=>this.getAxisMotionValue(s).stop())}getAxisMotionValue(s){const i=`_drag${s.toUpperCase()}`,c=this.visualElement.getProps()[i];return c||this.visualElement.getValue(s,this.visualElement.latestValues[s]??0)}snapToCursor(s){qt(i=>{const{drag:o}=this.getProps();if(!na(i,o,this.currentDirection))return;const{projection:c}=this.visualElement,d=this.getAxisMotionValue(i);if(c&&c.layout){const{min:h,max:f}=c.layout.layoutBox[i],p=d.get()||0;d.set(s[i]-ke(h,f,.5)+p)}})}scalePositionWithinConstraints(){if(!this.visualElement.current)return;const{drag:s,dragConstraints:i}=this.getProps(),{projection:o}=this.visualElement;if(!As(i)||!o||!this.constraints)return;this.stopAnimation();const c={x:0,y:0};qt(h=>{const f=this.getAxisMotionValue(h);if(f&&this.constraints!==!1){const p=f.get();c[h]=Uj({min:p,max:p},this.constraints[h])}});const{transformTemplate:d}=this.visualElement.getProps();this.visualElement.current.style.transform=d?d({},""):"none",o.root&&o.root.updateScroll(),o.updateLayout(),this.constraints=!1,this.resolveConstraints(),qt(h=>{if(!na(h,s,null))return;const f=this.getAxisMotionValue(h),{min:p,max:v}=this.constraints[h];f.set(ke(p,v,c[h]))}),this.visualElement.render()}addListeners(){if(!this.visualElement.current)return;Hj.set(this.visualElement,this);const s=this.visualElement.current,i=Er(s,"pointerdown",v=>{const{drag:g,dragListener:x=!0}=this.getProps(),w=v.target,j=w!==s&&$k(w);g&&x&&!j&&this.start(v)});let o;const c=()=>{const{dragConstraints:v}=this.getProps();As(v)&&v.current&&(this.constraints=this.resolveRefConstraints(),o||(o=Kj(s,v.current,()=>this.scalePositionWithinConstraints())))},{projection:d}=this.visualElement,h=d.addEventListener("measure",c);d&&!d.layout&&(d.root&&d.root.updateScroll(),d.updateLayout()),je.read(c);const f=Lr(window,"resize",()=>this.scalePositionWithinConstraints()),p=d.addEventListener("didUpdate",(({delta:v,hasLayoutChanged:g})=>{this.isDragging&&g&&(qt(x=>{const w=this.getAxisMotionValue(x);w&&(this.originPoint[x]+=v[x].translate,w.set(w.get()+v[x].translate))}),this.visualElement.render())}));return()=>{f(),i(),h(),p&&p(),o&&o()}}getProps(){const s=this.visualElement.getProps(),{drag:i=!1,dragDirectionLock:o=!1,dragPropagation:c=!1,dragConstraints:d=!1,dragElastic:h=Bc,dragMomentum:f=!0}=s;return{...s,drag:i,dragDirectionLock:o,dragPropagation:c,dragConstraints:d,dragElastic:h,dragMomentum:f}}}function Kf(t){let s=!0;return()=>{if(s){s=!1;return}t()}}function Kj(t,s,i){const o=lf(t,Kf(i)),c=lf(s,Kf(i));return()=>{o(),c()}}function na(t,s,i){return(s===!0||s===t)&&(i===null||i===t)}function qj(t,s=10){let i=null;return Math.abs(t.y)>s?i="y":Math.abs(t.x)>s&&(i="x"),i}class Xj extends An{constructor(s){super(s),this.removeGroupControls=zt,this.removeListeners=zt,this.controls=new Gj(s)}mount(){const{dragControls:s}=this.node.getProps();s&&(this.removeGroupControls=s.subscribe(this.controls)),this.removeListeners=this.controls.addListeners()||zt}update(){const{dragControls:s}=this.node.getProps(),{dragControls:i}=this.node.prevProps||{};s!==i&&(this.removeGroupControls(),s&&(this.removeGroupControls=s.subscribe(this.controls)))}unmount(){this.removeGroupControls(),this.removeListeners(),this.controls.isDragging||this.controls.endPanSession()}}const nc=t=>(s,i)=>{t&&je.update(()=>t(s,i),!1,!0)};class Yj extends An{constructor(){super(...arguments),this.removePointerDownListener=zt}onPointerDown(s){this.session=new cy(s,this.createPanHandlers(),{transformPagePoint:this.node.getTransformPagePoint(),contextWindow:ly(this.node)})}createPanHandlers(){const{onPanSessionStart:s,onPanStart:i,onPan:o,onPanEnd:c}=this.node.getProps();return{onSessionStart:nc(s),onStart:nc(i),onMove:nc(o),onEnd:(d,h)=>{delete this.session,c&&je.postRender(()=>c(d,h))}}}mount(){this.removePointerDownListener=Er(this.node.current,"pointerdown",s=>this.onPointerDown(s))}update(){this.session&&this.session.updateHandlers(this.createPanHandlers())}unmount(){this.removePointerDownListener(),this.session&&this.session.end()}}let sc=!1;class Qj extends P.Component{componentDidMount(){const{visualElement:s,layoutGroup:i,switchLayoutGroup:o,layoutId:c}=this.props,{projection:d}=s;d&&(i.group&&i.group.add(d),o&&o.register&&c&&o.register(d),sc&&d.root.didUpdate(),d.addEventListener("animationComplete",()=>{this.safeToRemove()}),d.setOptions({...d.options,layoutDependency:this.props.layoutDependency,onExitComplete:()=>this.safeToRemove()})),ma.hasEverUpdated=!0}getSnapshotBeforeUpdate(s){const{layoutDependency:i,visualElement:o,drag:c,isPresent:d}=this.props,{projection:h}=o;return h&&(h.isPresent=d,s.layoutDependency!==i&&h.setOptions({...h.options,layoutDependency:i}),sc=!0,c||s.layoutDependency!==i||i===void 0||s.isPresent!==d?h.willUpdate():this.safeToRemove(),s.isPresent!==d&&(d?h.promote():h.relegate()||je.postRender(()=>{const f=h.getStack();(!f||!f.members.length)&&this.safeToRemove()}))),null}componentDidUpdate(){const{visualElement:s,layoutAnchor:i}=this.props,{projection:o}=s;o&&(o.options.layoutAnchor=i,o.root.didUpdate(),hu.postRender(()=>{!o.currentAnimation&&o.isLead()&&this.safeToRemove()}))}componentWillUnmount(){const{visualElement:s,layoutGroup:i,switchLayoutGroup:o}=this.props,{projection:c}=s;sc=!0,c&&(c.scheduleCheckAfterUnmount(),i&&i.group&&i.group.remove(c),o&&o.deregister&&o.deregister(c))}safeToRemove(){const{safeToRemove:s}=this.props;s&&s()}render(){return null}}function dy(t){const[s,i]=rj(),o=P.useContext(Ep);return r.jsx(Qj,{...t,layoutGroup:o,switchLayoutGroup:P.useContext(ay),isPresent:s,safeToRemove:i})}const Jj={pan:{Feature:Yj},drag:{Feature:Xj,ProjectionNode:Zg,MeasureLayout:dy}};function qf(t,s,i){const{props:o}=t;t.animationState&&o.whileHover&&t.animationState.setActive("whileHover",i==="Start");const c="onHover"+i,d=o[c];d&&je.postRender(()=>d(s,Br(s)))}class Zj extends An{mount(){const{current:s}=this.node;s&&(this.unmount=Ok(s,(i,o)=>(qf(this.node,o,"Start"),c=>qf(this.node,c,"End"))))}unmount(){}}class e1 extends An{constructor(){super(...arguments),this.isActive=!1}onFocus(){let s=!1;try{s=this.node.current.matches(":focus-visible")}catch{s=!0}!s||!this.node.animationState||(this.node.animationState.setActive("whileFocus",!0),this.isActive=!0)}onBlur(){!this.isActive||!this.node.animationState||(this.node.animationState.setActive("whileFocus",!1),this.isActive=!1)}mount(){this.unmount=Ir(Lr(this.node.current,"focus",()=>this.onFocus()),Lr(this.node.current,"blur",()=>this.onBlur()))}unmount(){}}function Xf(t,s,i){const{props:o}=t;if(t.current instanceof HTMLButtonElement&&t.current.disabled)return;t.animationState&&o.whileTap&&t.animationState.setActive("whileTap",i==="Start");const c="onTap"+(i==="End"?"":i),d=o[c];d&&je.postRender(()=>d(s,Br(s)))}class t1 extends An{mount(){const{current:s}=this.node;if(!s)return;const{globalTapTarget:i,propagate:o}=this.node.props;this.unmount=Gk(s,(c,d)=>(Xf(this.node,d,"Start"),(h,{success:f})=>Xf(this.node,h,f?"End":"Cancel")),{useGlobalTarget:i,stopPropagation:(o==null?void 0:o.tap)===!1})}unmount(){}}const Oc=new WeakMap,rc=new WeakMap,n1=t=>{const s=Oc.get(t.target);s&&s(t)},s1=t=>{t.forEach(n1)};function r1({root:t,...s}){const i=t||document;rc.has(i)||rc.set(i,{});const o=rc.get(i),c=JSON.stringify(s);return o[c]||(o[c]=new IntersectionObserver(s1,{root:t,...s})),o[c]}function i1(t,s,i){const o=r1(s);return Oc.set(t,i),o.observe(t),()=>{Oc.delete(t),o.unobserve(t)}}const a1={some:0,all:1};class o1 extends An{constructor(){super(...arguments),this.hasEnteredView=!1,this.isInView=!1}startObserver(){var p;(p=this.stopObserver)==null||p.call(this);const{viewport:s={}}=this.node.getProps(),{root:i,margin:o,amount:c="some",once:d}=s,h={root:i?i.current:void 0,rootMargin:o,threshold:typeof c=="number"?c:a1[c]},f=v=>{const{isIntersecting:g}=v;if(this.isInView===g||(this.isInView=g,d&&!g&&this.hasEnteredView))return;g&&(this.hasEnteredView=!0),this.node.animationState&&this.node.animationState.setActive("whileInView",g);const{onViewportEnter:x,onViewportLeave:w}=this.node.getProps(),j=g?x:w;j&&j(v)};this.stopObserver=i1(this.node.current,h,f)}mount(){this.startObserver()}update(){if(typeof IntersectionObserver>"u")return;const{props:s,prevProps:i}=this.node;["amount","margin","root"].some(l1(s,i))&&this.startObserver()}unmount(){var s;(s=this.stopObserver)==null||s.call(this),this.hasEnteredView=!1,this.isInView=!1}}function l1({viewport:t={}},{viewport:s={}}={}){return i=>t[i]!==s[i]}const c1={inView:{Feature:o1},tap:{Feature:t1},focus:{Feature:e1},hover:{Feature:Zj}},u1={layout:{ProjectionNode:Zg,MeasureLayout:dy}},d1={...Rj,...c1,...Jj,...u1},h1=Mj(d1,Ej);function m1(){!pu.current&&Lg();const[t]=P.useState(Ca.current);return t}const Yf=h1,f1={type:"spring",stiffness:620,damping:42,mass:.35},p1={type:"spring",stiffness:460,damping:38,mass:.8},g1=typeof window>"u"?P.useEffect:P.useLayoutEffect;function y1({items:t,value:s,defaultValue:i,onValueChange:o,activation:c="automatic"}){const d=P.useId(),h=P.useRef(new Map),f=P.useRef(1),[p,v]=P.useState(()=>{var E,R;return i??((E=t.find(I=>!I.disabled))==null?void 0:E.value)??((R=t[0])==null?void 0:R.value)??""}),g=s??p,x=P.useRef(o);x.current=o;const w=P.useCallback(E=>{var D;if(E===g||!t.some(F=>F.value===E&&!F.disabled))return;const R=t.findIndex(F=>F.value===g),I=t.findIndex(F=>F.value===E);f.current=I<R?-1:1,s===void 0&&v(E),(D=x.current)==null||D.call(x,E)},[s,t,g]),j=P.useCallback(E=>{var I;const R=t[E];R&&((I=h.current.get(R.value))==null||I.focus())},[t]),k=P.useCallback((E,R)=>{const I=t.length;if(!I)return 0;let D=E;for(let F=0;F<I;F+=1)if(D=(D+R+I)%I,!t[D].disabled)return D;return E},[t]),S=P.useCallback(E=>{const R=t.map((I,D)=>D);return E&&R.reverse(),R.find(I=>!t[I].disabled)??0},[t]),N=P.useCallback((E,R)=>({id:`${d}-tab-${E.value}`,role:"tab",type:"button","aria-selected":E.value===g,"aria-controls":`${d}-panel-${E.value}`,"aria-disabled":E.disabled?!0:void 0,tabIndex:E.value===g?0:-1,ref:I=>{I?h.current.set(E.value,I):h.current.delete(E.value)},onClick:()=>{E.disabled||w(E.value)},onKeyDown:I=>{if(I.key==="ArrowRight"||I.key==="ArrowLeft"){I.preventDefault();const D=k(R,I.key==="ArrowRight"?1:-1);j(D),c==="automatic"&&w(t[D].value)}else if(I.key==="Home"||I.key==="End"){I.preventDefault();const D=S(I.key==="End");j(D),c==="automatic"&&w(t[D].value)}else(I.key==="Enter"||I.key===" ")&&(I.preventDefault(),E.disabled||w(E.value))}}),[c,d,S,j,t,k,w,g]),B=P.useCallback(E=>({id:`${d}-panel-${E}`,role:"tabpanel","aria-labelledby":`${d}-tab-${E}`,tabIndex:0}),[d]);return{value:g,select:w,direction:f.current,tabListProps:{role:"tablist","aria-orientation":"horizontal"},getTabProps:N,getPanelProps:B}}function v1({items:t,value:s,defaultValue:i,onValueChange:o,activation:c="automatic",renderPanel:d,label:h="Tabs",panelClassName:f="",className:p=""}){const v=y1({items:t,value:s,defaultValue:i,onValueChange:o,activation:c}),g=m1(),x=P.useRef(null),w=P.useRef([]),[j,k]=P.useState({x:0,width:0,ready:!1}),S=t.findIndex(N=>N.value===v.value);return g1(()=>{const N=w.current[S],B=x.current;if(!N||!B)return;const E=()=>k(I=>I.x===N.offsetLeft&&I.width===N.offsetWidth&&I.ready?I:{x:N.offsetLeft,width:N.offsetWidth,ready:!0});E();const R=new ResizeObserver(E);return R.observe(B),()=>R.disconnect()},[t,S]),r.jsxs("div",{className:`stats-tabs ${p}`,children:[r.jsxs("div",{...v.tabListProps,ref:x,"aria-label":h,className:"stats-tabs-list",children:[r.jsx(Yf.span,{layout:!0,"aria-hidden":"true",className:"stats-tabs-indicator",style:{left:j.x,width:j.width,opacity:j.ready?1:0},transition:g?{duration:0}:f1}),t.map((N,B)=>{const E=N.value===v.value,{ref:R,...I}=v.getTabProps(N,B);return r.jsx("button",{...I,ref:D=>{R(D),w.current[B]=D},className:`stats-tab${E?" selected":""}${N.disabled?" disabled":""}`,children:N.label},N.value)})]}),d&&r.jsx(Yf.div,{custom:v.direction,...v.getPanelProps(v.value),initial:g?!1:{opacity:0,x:v.direction*12},animate:{opacity:1,x:0},transition:g?{duration:0}:p1,className:`stats-tab-panel ${f}`,children:d(v.value)},v.value)]})}const x1=[{value:"messages",label:"Messages"},{value:"members",label:"Members"},{value:"layout",label:"Server layout"}];function hy(t){return new Intl.DateTimeFormat(void 0,{weekday:"short"}).format(new Date(`${t}T12:00:00`))}function w1({stats:t}){const s=t.activity.map(d=>d.messages),i=Math.max(1,...s),o=s.map((d,h)=>{const f=s.length>1?12+h*276/(s.length-1):150,p=102-d/i*78;return`${f},${p}`}).join(" "),c=`12,104 ${o} 288,104`;return r.jsxs("div",{className:"server-chart-wrap",children:[r.jsxs("div",{className:"server-chart-heading",children:[r.jsxs("div",{children:[r.jsx("span",{children:"Daily messages"}),r.jsx("strong",{children:ye(s.reduce((d,h)=>d+h,0))})]}),r.jsx("small",{children:"Last 14 days"})]}),r.jsxs("svg",{className:"server-line-chart",viewBox:"0 0 300 122",role:"img","aria-label":"Daily messages over the last fourteen days",children:[r.jsx("defs",{children:r.jsxs("linearGradient",{id:"message-area-fill",x1:"0",x2:"0",y1:"0",y2:"1",children:[r.jsx("stop",{offset:"0%",stopColor:"var(--accent)",stopOpacity:".24"}),r.jsx("stop",{offset:"100%",stopColor:"var(--accent)",stopOpacity:"0"})]})}),[24,50,76,104].map(d=>r.jsx("line",{x1:"12",x2:"288",y1:d,y2:d,className:"server-chart-gridline"},d)),r.jsx("polygon",{points:c,fill:"url(#message-area-fill)"}),r.jsx("polyline",{points:o,className:"server-chart-line"}),t.activity.map((d,h)=>{const f=s.length>1?12+h*276/(s.length-1):150,p=102-d.messages/i*78;return r.jsx("circle",{cx:f,cy:p,r:"2.7",className:"server-chart-point",children:r.jsx("title",{children:`${d.date}: ${ye(d.messages)} messages`})},d.date)})]}),r.jsx("div",{className:"server-chart-days",children:t.activity.filter((d,h)=>h%2===0).map(d=>r.jsx("span",{children:hy(d.date)},d.date))})]})}function b1({stats:t}){const s=Math.max(1,...t.activity.flatMap(i=>[i.joins,i.leaves]));return r.jsxs("div",{className:"server-chart-wrap",children:[r.jsxs("div",{className:"server-chart-heading",children:[r.jsxs("div",{children:[r.jsx("span",{children:"Member changes"}),r.jsxs("strong",{children:[ye(t.activity.reduce((i,o)=>i+o.joins,0))," joined"]})]}),r.jsx("small",{children:"Last 14 days"})]}),r.jsx("div",{className:"server-member-chart",role:"img","aria-label":"Daily member joins and departures over the last fourteen days",children:t.activity.map(i=>r.jsxs("div",{className:"server-member-day",title:`${i.date}: ${i.joins} joined, ${i.leaves} left`,children:[r.jsxs("div",{className:"server-member-bars",children:[r.jsx("i",{className:"join-bar",style:{height:`${Math.max(i.joins?5:0,i.joins/s*76)}%`}}),r.jsx("i",{className:"leave-bar",style:{height:`${Math.max(i.leaves?5:0,i.leaves/s*76)}%`}})]}),r.jsx("span",{children:hy(i.date).slice(0,1)})]},i.date))}),r.jsxs("div",{className:"server-chart-legend",children:[r.jsxs("span",{children:[r.jsx("i",{className:"join-key"})," Joined ",r.jsx("b",{children:ye(t.activity.reduce((i,o)=>i+o.joins,0))})]}),r.jsxs("span",{children:[r.jsx("i",{className:"leave-key"})," Left ",r.jsx("b",{children:ye(t.activity.reduce((i,o)=>i+o.leaves,0))})]})]})]})}function k1({stats:t}){const s=Math.max(t.member_count,t.channel_count,t.role_count,1),i=[{label:"Members",value:t.member_count,color:"members"},{label:"Channels",value:t.channel_count,color:"channels"},{label:"Roles",value:t.role_count,color:"roles"}];return r.jsxs("div",{className:"server-layout-chart",children:[r.jsxs("div",{className:"server-layout-total",children:[r.jsx("span",{children:"Community size"}),r.jsx("strong",{children:ye(t.member_count)}),r.jsx("small",{children:"members currently in this server"})]}),r.jsx("div",{className:"server-layout-bars",children:i.map(o=>r.jsxs("div",{className:"server-layout-row",children:[r.jsxs("div",{children:[r.jsx("span",{children:o.label}),r.jsx("strong",{children:ye(o.value)})]}),r.jsx("div",{className:"server-layout-track",children:r.jsx("i",{className:`layout-${o.color}`,style:{width:`${Math.max(o.value?4:0,o.value/s*100)}%`}})})]},o.label))})]})}function j1({stats:t}){const[s,i]=P.useState("messages"),o=P.useMemo(()=>({messages:t.activity.reduce((d,h)=>d+h.messages,0),joins:t.activity.reduce((d,h)=>d+h.joins,0)}),[t.activity]),c=s==="members"?r.jsx(b1,{stats:t}):s==="layout"?r.jsx(k1,{stats:t}):r.jsx(w1,{stats:t});return r.jsxs("section",{className:"dash-panel server-stats-card","aria-label":"Server statistics",children:[r.jsxs("div",{className:"panel-heading server-stats-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Community analytics"}),r.jsx("h3",{children:"Server pulse"}),r.jsx("p",{children:"Daily activity tracked by Niko · last 14 days"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(qx,{})})]}),r.jsxs("div",{className:"server-stat-metrics",children:[r.jsxs("div",{children:[r.jsx(fc,{}),r.jsx("span",{children:"Members"}),r.jsx("strong",{children:ye(t.member_count)})]}),r.jsxs("div",{children:[r.jsx(aa,{}),r.jsx("span",{children:"Messages · 14d"}),r.jsx("strong",{children:ye(o.messages)})]}),r.jsxs("div",{children:[r.jsx(Qx,{}),r.jsx("span",{children:"New members · 14d"}),r.jsx("strong",{children:ye(o.joins)})]})]}),r.jsx(v1,{items:x1,value:s,onValueChange:i,label:"Server statistics",renderPanel:()=>c}),r.jsx("div",{className:"server-stats-footnote",children:"Activity is collected from the moment tracking is enabled."})]})}function _n({eyebrow:t,title:s,text:i}){return r.jsxs("div",{className:"dash-heading",children:[r.jsxs("div",{className:"heading-meta",children:[r.jsx("div",{className:"eyebrow",children:t}),r.jsx("span",{className:"heading-context",children:"NIKO / CONTROL ROOM"})]}),r.jsx("h2",{children:s}),r.jsx("p",{children:i})]})}function Yt({label:t,value:s,note:i,accent:o=""}){return r.jsxs("div",{className:`dash-stat ${o}`,children:[r.jsx("span",{children:t}),r.jsx("strong",{children:s}),r.jsx("small",{children:i})]})}function S1({user:t,overview:s,guilds:i,onServers:o,onManage:c}){const d=i.filter(h=>h.installed!==!1);return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"Personal overview",title:"Your Niko snapshot.",text:"Keep an eye on your progress, then jump into a server when you’re ready to tune the room."}),r.jsxs("div",{className:"overview-intro",children:[r.jsxs("div",{className:"profile-card",children:[r.jsx(Pp,{user:t,className:"profile-avatar"}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Signed in as"}),r.jsx("h3",{children:Cp(t)}),r.jsx("p",{children:"Personal economy profile"})]})]}),r.jsxs("button",{className:"button button-primary",onClick:o,children:["Manage a server ",r.jsx(J,{name:"arrow"})]})]}),r.jsxs("div",{className:"dash-stats overview-stats",children:[r.jsx(Yt,{label:"Net worth",value:ye(s==null?void 0:s.net_worth),note:"Across your Niko profile",accent:"accent-orange"}),r.jsx(Yt,{label:"In your wallet",value:ye(s==null?void 0:s.balance),note:"Ready to spend",accent:"accent-violet"}),r.jsx(Yt,{label:"In your vault",value:ye(s==null?void 0:s.bank),note:"Saved for later",accent:"accent-blue"}),r.jsx(Yt,{label:"Current level",value:ye(s==null?void 0:s.level),note:s!=null&&s.job?`Working as a ${s.job}`:"Keep showing up",accent:"accent-green"})]}),r.jsxs("div",{className:"dash-columns overview-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Progress"}),r.jsx("h3",{children:"Your momentum"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(J,{name:"spark"})})]}),r.jsxs("div",{className:"metric-list",children:[r.jsxs("div",{children:[r.jsx("span",{children:"Daily streak"}),r.jsxs("strong",{children:[ye(s==null?void 0:s.daily_streak)," ",r.jsx("small",{children:"days"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Achievements"}),r.jsxs("strong",{children:[ye(s==null?void 0:s.achievements)," ",r.jsx("small",{children:"unlocked"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Total earned"}),r.jsxs("strong",{children:[ye(s==null?void 0:s.total_earned)," ",r.jsx("small",{children:"coins"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Economy standing"}),r.jsxs("strong",{children:[s!=null&&s.economy_rank?`#${ye(s.economy_rank)}`:"—"," ",r.jsx("small",{children:s!=null&&s.economy_profiles?`of ${ye(s.economy_profiles)}`:""})]})]})]})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Quick access"}),r.jsx("h3",{children:"Your servers"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(J,{name:"users"})})]}),r.jsxs("div",{className:"mini-server-list",children:[d.slice(0,4).map(h=>r.jsxs("button",{onClick:()=>c(h),children:[r.jsx(Uc,{guild:h}),r.jsx("span",{children:h.name}),r.jsx(J,{name:"arrow"})]},h.id)),!d.length&&r.jsx("p",{className:"empty-state compact",children:"Add Niko to a server to start managing it."})]}),r.jsxs("button",{className:"text-link overview-link",onClick:o,children:["View all servers ",r.jsx(J,{name:"arrow"})]})]})]})]})}function Qf({guild:t,onManage:s}){const i=t.installed!==!1;return r.jsxs("article",{className:"server-card",children:[r.jsxs("div",{className:"server-card-heading",children:[r.jsx(Uc,{guild:t,className:"server-avatar"}),r.jsx("span",{className:"server-status",children:i?"Niko is installed":"Ready to add"})]}),r.jsx("h3",{children:t.name}),r.jsx("p",{children:i?"Open the dashboard to manage Niko’s features and settings.":"You have permission to manage this server. Add Niko to unlock its controls."}),i?r.jsxs("button",{className:"button button-muted button-small",onClick:()=>s(t),children:["Open settings ",r.jsx(J,{name:"arrow"})]}):r.jsxs("a",{className:"button button-primary button-small",href:t.invite_url||"#",target:"_blank",rel:"noreferrer",children:["Add Niko ",r.jsx(J,{name:"external"})]})]})}function N1({guilds:t,onManage:s}){const i=t.filter(c=>c.installed!==!1),o=t.filter(c=>c.installed===!1);return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"Servers",title:"Choose where to work.",text:"Manage servers with Niko already installed, or add Niko to another server you can administer."}),r.jsxs("div",{className:"server-summary",children:[r.jsxs("div",{children:[r.jsx("strong",{children:ye(i.length)}),r.jsx("span",{children:"Connected to Niko"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:ye(o.length)}),r.jsx("span",{children:"Ready to add"})]}),r.jsxs("div",{className:"server-summary-note",children:[r.jsx(J,{name:"shield"}),r.jsx("span",{children:"Only servers where you have Manage Server access are shown."})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Connected"}),r.jsx("h3",{children:"Manage a server"})]}),r.jsx("span",{className:"section-count",children:i.length})]}),r.jsxs("div",{className:"server-grid",children:[i.map(c=>r.jsx(Qf,{guild:c,onManage:s},c.id)),!i.length&&r.jsxs("div",{className:"empty-state",children:[r.jsx("strong",{children:"No connected servers yet."}),r.jsx("span",{children:"Add Niko below, then come back here to manage it."})]})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Available to you"}),r.jsx("h3",{children:"Add Niko to a server"})]}),r.jsx("span",{className:"section-count",children:o.length})]}),r.jsxs("div",{className:"server-grid",children:[o.map(c=>r.jsx(Qf,{guild:c,onManage:s},c.id)),!o.length&&r.jsx("div",{className:"server-note",children:"Niko is already installed in every server you can manage."})]})]})]})}function my({rows:t}){return r.jsxs("div",{className:"rank-list",children:[t.slice(0,5).map((s,i)=>r.jsxs("div",{className:"rank-row",children:[r.jsx("span",{className:`rank rank-${i+1}`,children:String(i+1).padStart(2,"0")}),r.jsxs("span",{className:"rank-user",children:[r.jsx(hw,{name:s.display_name||s.username||"Unknown member",avatarUrl:s.avatar_url}),r.jsxs("span",{children:[r.jsx("strong",{children:s.display_name||s.username||"Unknown member"}),s.username&&s.display_name&&r.jsxs("small",{children:["@",s.username]})]})]}),r.jsxs("strong",{children:["Level ",ye(s.level),r.jsxs("small",{children:[ye(s.xp)," xp"]})]})]},`${s.user_id}-${i}`)),!t.length&&r.jsx("div",{className:"empty-state compact",children:"No data recorded yet."})]})}function C1({overview:t}){return r.jsxs(r.Fragment,{children:[r.jsxs("div",{className:"guild-welcome",children:[r.jsxs("div",{children:[r.jsx("span",{className:"welcome-mark",children:r.jsx(J,{name:"grid"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server pulse"}),r.jsx("strong",{children:"Here’s what needs your attention."})]})]}),r.jsxs("span",{className:"welcome-time",children:["LIVE SIGNALS ",r.jsx("span",{className:"status-dot"})]})]}),r.jsx(_n,{eyebrow:"Overview",title:"A quick read on your room.",text:"The important signals, without making you hunt for them."}),r.jsxs("div",{className:"dash-stats guild-overview-stats",children:[r.jsx(Yt,{label:"Warnings logged",value:ye(t.moderation.warn_count),note:"For this server",accent:"accent-blue"}),r.jsx(Yt,{label:"Automod",value:t.moderation.automod_active?"Active":"Quiet",note:"Protection status",accent:"accent-green"}),r.jsx(Yt,{label:"Level leaders",value:ye(t.leveling.top.length),note:"Members with recorded XP",accent:"accent-violet"})]}),r.jsx(j1,{stats:t.server}),r.jsxs("div",{className:"dash-columns overview-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Community energy"}),r.jsx("h3",{children:"Top XP"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(J,{name:"spark"})})]}),r.jsx(my,{rows:t.leveling.top})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server controls"}),r.jsx("h3",{children:"Manage the room"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(J,{name:"settings"})})]}),r.jsxs("div",{className:"server-controls-body",children:[r.jsx("p",{children:"Use Server settings for prefixes, welcome messages, logs, and ticket panels."}),r.jsxs("span",{className:"text-link",children:["Open server settings ",r.jsx(J,{name:"arrow"})]})]})]})]})]})}function T1({rows:t,config:s,resources:i,csrfToken:o,guildId:c}){var d,h,f;return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"Leveling",title:"Momentum people can see.",text:"Track the members turning up, and tune the pace to fit your server."}),r.jsxs("div",{className:"dash-stats",children:[r.jsx(Yt,{label:"Top level",value:String(((d=t[0])==null?void 0:d.level)||0),note:((h=t[0])==null?void 0:h.display_name)||((f=t[0])==null?void 0:f.username)||"No members yet",accent:"accent-violet"}),r.jsx(Yt,{label:"XP multiplier",value:`${(s==null?void 0:s.leveling.xp_multiplier)||1}×`,note:(s==null?void 0:s.leveling.xp_enabled)===!1?"XP disabled":"Currently active",accent:"accent-blue"}),r.jsx(Yt,{label:"Cooldown",value:`${(s==null?void 0:s.leveling.xp_cooldown)||0}s`,note:"Between XP awards",accent:"accent-green"})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Leaderboard"}),r.jsx("h3",{children:"XP leaders"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(J,{name:"spark"})})]}),r.jsx(my,{rows:t})]}),r.jsx(A1,{guildId:c,config:s,resources:i,csrfToken:o})]})}const Fa={saving:!1,message:"",error:""};function lt({label:t,hint:s,children:i}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:t}),i,s&&r.jsx("small",{children:s})]})}function P1(t,s){const i=s?String(s):"",o=(t==null?void 0:t.channels)||[];return!i||o.some(c=>String(c.id)===i)?o:[{id:i,name:`Saved channel · ${i}`},...o]}function Ba({icon:t,label:s,title:i,text:o,className:c}){return r.jsxs("div",{className:`settings-intro${c?` ${c}`:""}`,children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(J,{name:t})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:s}),r.jsx("strong",{children:i}),r.jsx("p",{children:o})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]})}function ss({label:t,title:s,detail:i,icon:o}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:t}),r.jsx("h3",{children:s}),i&&r.jsx("p",{children:i})]}),o&&r.jsx("span",{className:"panel-icon",children:r.jsx(J,{name:o})})]})}function Oa({state:t}){return r.jsxs("div",{className:"setting-footer",children:[t.error?r.jsx("span",{className:"form-error",role:"alert",children:t.error}):r.jsx("span",{role:"status",children:t.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:t.saving,children:t.saving?"Saving…":"Save changes"})]})}function M1({guildId:t,config:s,csrfToken:i}){var x,w,j;const[o,c]=P.useState({}),[d,h]=P.useState(Fa);P.useEffect(()=>{const k=(s==null?void 0:s.moderation)||{};c({automod:{...k.automod||{}},spam_threshold:k.spam_threshold??6,spam_interval:k.spam_interval??7,max_mentions:k.max_mentions??5,antinuke:{...k.antinuke||{}},antiraid:{...k.antiraid||{}},antiraid_ext:{...k.antiraid_ext||{}}})},[s]);const f=(k,S,N)=>c(B=>({...B,[k]:{...B[k],[S]:N}})),p=k=>{k.preventDefault(),h({saving:!0,message:"",error:""}),_a(t,"automod",o,i).then(S=>{const N=S.config||{};c({automod:{...N.automod||{}},spam_threshold:N.spam_threshold??6,spam_interval:N.spam_interval??7,max_mentions:N.max_mentions??5,antinuke:{...N.antinuke||{}},antiraid:{...N.antiraid||{}},antiraid_ext:{...N.antiraid_ext||{}}}),h({saving:!1,message:"Moderation settings saved to Niko.",error:""})}).catch(S=>h({saving:!1,message:"",error:S instanceof Error?S.message:"Could not save settings."}))},v=[["antispam","Anti-spam","Detect repeated messages"],["antilink","Invite links","Remove Discord invite links"],["badwords","Blocked words","Filter words from the server list"],["massmention","Mass mentions","Limit mention floods"],["antinuke","Anti-nuke","Protect channels and roles"],["antiraid","Join raid protection","React to sudden join waves"],["antiraid_ext","External app protection","Detect user-installed app abuse"]],g=v.filter(([k])=>{var S;return!!((S=o.automod)!=null&&S[k])}).length;return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"Moderation",title:"Keep the room feeling good.",text:"Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration."}),r.jsx(Ba,{icon:"shield",label:"Protection desk",title:`${g} of ${v.length} safeguards active`,text:"Start with the essentials, then tune thresholds below when you know the room’s rhythm."}),r.jsxs("form",{onSubmit:p,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ss,{label:"Protection rules",title:"AutoMod modules",detail:"Toggle only the responses you want Niko to handle.",icon:"shield"}),r.jsx("div",{className:"setting-list",children:v.map(([k,S,N])=>{var B;return r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:S}),r.jsx("small",{children:N})]}),r.jsx("input",{type:"checkbox",checked:!!((B=o.automod)!=null&&B[k]),onChange:E=>f("automod",k,E.target.checked)}),r.jsx("i",{"aria-hidden":"true"})]},k)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ss,{label:"Thresholds",title:"Choose when protection steps in",detail:"These limits apply across the server."}),r.jsxs("div",{className:"form-grid",children:[r.jsx(lt,{label:"Spam messages",hint:"Messages inside the spam interval",children:r.jsx("input",{type:"number",min:"1",max:"100",value:o.spam_threshold??6,onChange:k=>c({...o,spam_threshold:k.target.value})})}),r.jsx(lt,{label:"Spam interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:o.spam_interval??7,onChange:k=>c({...o,spam_interval:k.target.value})})}),r.jsx(lt,{label:"Maximum mentions",children:r.jsx("input",{type:"number",min:"1",max:"100",value:o.max_mentions??5,onChange:k=>c({...o,max_mentions:k.target.value})})}),r.jsx(lt,{label:"Anti-raid joins",hint:"Joins inside the join interval",children:r.jsx("input",{type:"number",min:"1",max:"1000",value:((x=o.antiraid)==null?void 0:x.join_threshold)??10,onChange:k=>f("antiraid","join_threshold",k.target.value)})}),r.jsx(lt,{label:"Anti-raid interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:((w=o.antiraid)==null?void 0:w.join_interval)??10,onChange:k=>f("antiraid","join_interval",k.target.value)})}),r.jsx(lt,{label:"Anti-raid action",children:r.jsxs("select",{value:((j=o.antiraid)==null?void 0:j.action)??"kick",onChange:k=>f("antiraid","action",k.target.value),children:[r.jsx("option",{value:"kick",children:"Kick"}),r.jsx("option",{value:"ban",children:"Ban"}),r.jsx("option",{value:"softban",children:"Soft-ban"}),r.jsx("option",{value:"slowmode",children:"Slowmode"}),r.jsx("option",{value:"lockdown",children:"Lockdown"})]})})]}),r.jsx(Oa,{state:d})]})]})]})}function E1({guildId:t,config:s,csrfToken:i}){var j,k;const[o,c]=P.useState({ai_name:"Niko",personality:"cafe",enabled:!0,ai_actions_experiment:!1,better_context_experiment:!1,multimodal_experiment:!1}),[d,h]=P.useState(Fa),[f,p]=P.useState(null),v=S=>S===!0||S==="True",g=S=>c({ai_name:S.ai_name||"Niko",personality:S.personality==="normal"?"normal":"cafe",enabled:S.enabled!=="False"&&S.enabled!==!1,ai_actions_experiment:v(S.ai_actions_experiment),better_context_experiment:v(S.better_context_experiment),multimodal_experiment:v(S.multimodal_experiment)});P.useEffect(()=>g((s==null?void 0:s.ai)||{}),[s]);const x=S=>{S.preventDefault(),h({saving:!0,message:"",error:""}),_a(t,"ai",o,i).then(N=>{g(N.config||{}),h({saving:!1,message:"AI settings saved.",error:""})}).catch(N=>h({saving:!1,message:"",error:N instanceof Error?N.message:"Could not save settings."}))},w=[{key:"better_context_experiment",title:"Better context",hint:"Use the last five channel messages",info:"Adds recent conversation and replied-to message context so responses understand ongoing discussions more naturally. It is useful for follow-ups, but sends more conversation context to the AI provider."},{key:"ai_actions_experiment",title:"AI actions",hint:"Allow confirmed actions requested in chat",info:"Lets the AI propose polls and server actions such as moderation or channel management. Every action requires confirmation and is still limited by Discord permissions."},{key:"multimodal_experiment",title:"Multimodal conversation",hint:"Understand images and transcribe voice messages",info:"Allows Niko to inspect image attachments and use voice-message transcriptions as context. Media is processed only while enabled and provider usage costs may apply."}];return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"AI controls",title:"Give your AI the right tone.",text:"Configure the AI identity, personality, and opt-in experiments for this server."}),r.jsx(Ba,{icon:"settings",label:"Conversation desk",title:o.enabled?`${o.ai_name} is ready to respond`:`${o.ai_name} is staying quiet`,text:"All settings apply only to this server."}),r.jsxs("form",{onSubmit:x,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ss,{label:"Conversation",title:"Core settings",detail:"Decide when the AI joins the conversation.",icon:"settings"}),r.jsx("div",{className:"form-grid",children:r.jsx(lt,{label:"AI name",hint:"1–32 characters; this is also the mention trigger",children:r.jsx("input",{value:o.ai_name,maxLength:32,onChange:S=>c({...o,ai_name:S.target.value})})})}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable AI chat"}),r.jsx("small",{children:"Respond when the configured name is mentioned"})]}),r.jsx("input",{type:"checkbox",checked:o.enabled,onChange:S=>c({...o,enabled:S.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"personality-options",children:[r.jsxs("button",{type:"button",className:o.personality==="cafe"?"personality active":"personality",onClick:()=>c({...o,personality:"cafe"}),children:[r.jsx("span",{className:"personality-mark",children:"n"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Café"}),r.jsx("small",{children:"Warm, playful, familiar"})]})]}),r.jsxs("button",{type:"button",className:o.personality==="normal"?"personality active":"personality",onClick:()=>c({...o,personality:"normal"}),children:[r.jsx("span",{className:"personality-mark",children:"—"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Normal"}),r.jsx("small",{children:"Clear and straightforward"})]})]})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ss,{label:"Experiments",title:"Optional capabilities",detail:"Each experiment includes a learn-more explanation before you enable it."}),w.map(S=>r.jsxs("div",{className:"setting-row experiment-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:S.title}),r.jsx("small",{children:S.hint})]}),r.jsxs("div",{className:"experiment-actions",children:[r.jsx("button",{type:"button",className:"button button-secondary",onClick:()=>p(S.key),children:"Learn more"}),r.jsxs("label",{className:"toggle-control","aria-label":`Enable ${S.title}`,children:[r.jsx("input",{type:"checkbox",checked:o[S.key],onChange:N=>c({...o,[S.key]:N.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]})]})]},S.key)),r.jsx(Oa,{state:d})]})]}),f&&r.jsx("div",{className:"modal-backdrop",role:"presentation",onClick:()=>p(null),children:r.jsxs("div",{className:"modal-card",role:"dialog","aria-modal":"true","aria-labelledby":"ai-experiment-title",onClick:S=>S.stopPropagation(),children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"AI experiment"}),r.jsx("h3",{id:"ai-experiment-title",children:(j=w.find(S=>S.key===f))==null?void 0:j.title})]}),r.jsx("button",{type:"button",className:"button button-secondary",onClick:()=>p(null),children:"Close"})]}),r.jsx("p",{children:(k=w.find(S=>S.key===f))==null?void 0:k.info})]})})]})}function A1({guildId:t,config:s,resources:i,csrfToken:o}){const c=(s==null?void 0:s.leveling)||{},[d,h]=P.useState({xp_enabled:!0,xp_multiplier:1,xp_cooldown:0,level_up_channel:"",level_up_message:""}),[f,p]=P.useState(Fa);P.useEffect(()=>h({xp_enabled:c.xp_enabled!==!1,xp_multiplier:c.xp_multiplier??1,xp_cooldown:c.xp_cooldown??0,level_up_channel:c.level_up_channel?String(c.level_up_channel):"",level_up_message:c.level_up_message||""}),[s]);const v=x=>{x.preventDefault(),p({saving:!0,message:"",error:""}),_a(t,"leveling",d,o).then(w=>{const j=w.config||{};h({xp_enabled:j.xp_enabled!==!1,xp_multiplier:j.xp_multiplier??1,xp_cooldown:j.xp_cooldown??0,level_up_channel:j.level_up_channel?String(j.level_up_channel):"",level_up_message:j.level_up_message||""}),p({saving:!1,message:"Leveling settings saved to Niko.",error:""})}).catch(w=>p({saving:!1,message:"",error:w instanceof Error?w.message:"Could not save settings."}))},g=P1(i,d.level_up_channel);return r.jsxs(r.Fragment,{children:[r.jsx(Ba,{className:"leveling-settings-intro",icon:"spark",label:"Participation desk",title:d.xp_enabled?"XP is flowing":"XP is paused",text:"Set a pace that rewards regulars without turning every message into a transaction."}),r.jsx("form",{onSubmit:v,className:"settings-stack",children:r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ss,{label:"Leveling settings",title:"Shape the pace",detail:"These controls apply to every member in this server.",icon:"spark"}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable XP"}),r.jsx("small",{children:"Track activity and award levels"})]}),r.jsx("input",{type:"checkbox",checked:d.xp_enabled,onChange:x=>h({...d,xp_enabled:x.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"form-grid",children:[r.jsx(lt,{label:"XP multiplier",hint:"From 0.1× to 10×",children:r.jsx("input",{type:"number",min:"0.1",max:"10",step:"0.1",value:d.xp_multiplier,onChange:x=>h({...d,xp_multiplier:x.target.value})})}),r.jsx(lt,{label:"Cooldown (seconds)",hint:"0 disables the cooldown",children:r.jsx("input",{type:"number",min:"0",max:"86400",value:d.xp_cooldown,onChange:x=>h({...d,xp_cooldown:x.target.value})})}),r.jsx(lt,{label:"Level-up channel",children:r.jsxs("select",{value:d.level_up_channel,onChange:x=>h({...d,level_up_channel:x.target.value}),children:[r.jsx("option",{value:"",children:"Same channel"}),g.map(x=>r.jsxs("option",{value:x.id,children:["#",x.name]},x.id))]})}),r.jsx(lt,{label:"Level-up message",hint:"Use {mention}, {level}, {name}, or {guild}",children:r.jsx("textarea",{rows:3,maxLength:1e3,value:d.level_up_message,onChange:x=>h({...d,level_up_message:x.target.value}),placeholder:"Leave blank for Niko's default message"})})]}),r.jsx(Oa,{state:f})]})})]})}function _1({guildId:t,config:s,csrfToken:i}){var v;const o=((v=s==null?void 0:s.server)==null?void 0:v.profile)||{},[c,d]=P.useState({display_name:o.display_name||"",bio:o.bio||"",avatar_url:o.avatar_url||"",banner_url:o.banner_url||""}),[h,f]=P.useState(Fa);P.useEffect(()=>{var x;const g=((x=s==null?void 0:s.server)==null?void 0:x.profile)||{};d({display_name:g.display_name||"",bio:g.bio||"",avatar_url:g.avatar_url||"",banner_url:g.banner_url||""})},[s]);const p=g=>{g.preventDefault(),f({saving:!0,message:"",error:""}),Vx(t,{display_name:c.display_name||null,bio:c.bio||null,avatar_url:c.avatar_url||null,banner_url:c.banner_url||null},i).then(x=>{const w=x.profile||{};d({display_name:w.display_name||"",bio:w.bio||"",avatar_url:w.avatar_url||"",banner_url:w.banner_url||""}),f({saving:!1,message:"Bot profile updated.",error:""})}).catch(x=>f({saving:!1,message:"",error:x instanceof Error?x.message:"Could not save profile."}))};return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"Customization",title:"Niko's server presence.",text:"Change how Niko appears in this server. Display name, avatar, banner, and bio are all per-server."}),r.jsx(Ba,{icon:"paint",label:"Identity desk",title:"Server-specific identity",text:"Each server can have its own Niko persona. Changes apply only to this server."}),r.jsxs("form",{onSubmit:p,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ss,{label:"Display name",title:"How Niko appears",detail:"Set the name members see for Niko in this server. Leave blank to use the default.",icon:"settings"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(lt,{label:"Display name",hint:"32 characters or fewer",children:r.jsx("input",{value:c.display_name,maxLength:32,onChange:g=>d({...c,display_name:g.target.value}),placeholder:"Niko"})}),r.jsx(lt,{label:"Bio",hint:"190 characters or fewer",children:r.jsx("input",{value:c.bio,maxLength:190,onChange:g=>d({...c,bio:g.target.value}),placeholder:"A warm Discord companion"})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(ss,{label:"Server avatar & banner",title:"Visual identity",detail:"Provide HTTPS image URLs. Images are uploaded to Discord when saved.",icon:"paint"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(lt,{label:"Avatar URL",hint:"Square image, 512×512 recommended",children:r.jsx("input",{type:"url",value:c.avatar_url,onChange:g=>d({...c,avatar_url:g.target.value}),placeholder:"https://cdn.example.com/avatar.png"})}),r.jsx(lt,{label:"Banner URL",hint:"Wide image, 960×540 recommended",children:r.jsx("input",{type:"url",value:c.banner_url,onChange:g=>d({...c,banner_url:g.target.value}),placeholder:"https://cdn.example.com/banner.png"})})]}),r.jsx("p",{className:"form-hint",children:"Images are fetched, validated, and uploaded to Discord. Maximum 8 MB each. Supported formats: PNG, JPG, GIF."})]}),r.jsx(Oa,{state:h})]})]})}const D1={saving:!1,message:"",error:""};function gt({label:t,hint:s,children:i}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:t}),i,s&&r.jsx("small",{children:s})]})}function sa({label:t,title:s,detail:i,icon:o}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:t}),r.jsx("h3",{children:s}),r.jsx("p",{children:i})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(J,{name:o})})]})}function R1({state:t}){return r.jsxs("div",{className:"setting-footer",children:[t.error?r.jsx("span",{className:"form-error",role:"alert",children:t.error}):r.jsx("span",{role:"status",children:t.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:t.saving,children:t.saving?"Saving...":"Save server settings"})]})}const L1=[["moderation","Moderation"],["automod","AutoMod"],["messages","Messages"],["channels","Channels"],["members","Members"],["captcha","Captcha"],["invites","Invites"],["roles","Roles"],["server","Server"],["voice","Voice"]];function I1(t,s){var i;return s?((i=t==null?void 0:t.channels.find(o=>String(o.id)===String(s)))==null?void 0:i.name)||`Saved channel · ${s}`:"Not set"}function Jf(t){const s=t.replace(/^#/,"");return/^[0-9a-fA-F]{6}$/.test(s)?`#${s}`:"#5865F2"}function ra(t,s){const i=s?String(s):"",o=(t==null?void 0:t.channels)||[];return!i||o.some(c=>String(c.id)===i)?o:[{id:i,name:`Saved channel · ${i}`},...o]}function Zf(t,s=[]){const i=(t==null?void 0:t.roles)||[],o=new Set(i.map(d=>String(d.id)));return[...s.map(String).filter((d,h,f)=>d&&!o.has(d)&&f.indexOf(d)===h).map(d=>({id:d,name:`Unavailable role (${d})`})),...i]}function ic(t){var o,c;const s=(t==null?void 0:t.onboarding)||{},i=(t==null?void 0:t.tickets)||{};return{prefixes:((o=t==null?void 0:t.prefixes)!=null&&o.length?t.prefixes:["."]).join(`
`),welcome_channel:s.welcome_channel?String(s.welcome_channel):"",welcome_title:s.welcome_title||"",welcome_description:s.welcome_description||"",welcome_color:s.welcome_color===null||s.welcome_color===void 0?"5865F2":s.welcome_color.toString(16).padStart(6,"0"),welcome_image:s.welcome_image||"",rules_channel:s.rules_channel?String(s.rules_channel):"",rules_text:s.rules_text||"",rules_role_id:s.rules_role_id?String(s.rules_role_id):"",logging:Object.fromEntries(Object.entries((t==null?void 0:t.logging)||{}).map(([d,h])=>[d,h==null?"":String(h)])),disabled_logging:[...((c=t==null?void 0:t.logging)==null?void 0:c.disabled)||[]].map(String),panel_title:i.panel_title||"",panel_description:i.panel_description||"",panel_categories:(i.panel_categories||[]).join(`
`),panel_channel_id:i.panel_channel_id?String(i.panel_channel_id):"",support_roles:[...i.support_roles||[]].map(String)}}function V1({guildId:t,config:s,resources:i,csrfToken:o}){const[c,d]=P.useState(()=>ic(s==null?void 0:s.server)),[h,f]=P.useState(D1),[p,v]=P.useState(!1);P.useEffect(()=>{s!=null&&s.server&&d(ic(s.server))},[s]);const g=(D,F)=>d(V=>({...V,[D]:F})),x=D=>g("welcome_color",D.replace(/^#/,"").replace(/[^0-9a-fA-F]/g,"").slice(0,6)),w=(D,F)=>d(V=>({...V,logging:{...V.logging,[D]:F}})),j=D=>d(F=>({...F,disabled_logging:F.disabled_logging.includes(D)?F.disabled_logging.filter(V=>V!==D):[...F.disabled_logging,D]})),k=D=>{D.preventDefault(),f({saving:!0,message:"",error:""});const F=c.prefixes.split(/\r?\n|,/).map(z=>z.trim()).filter(Boolean),V=c.panel_categories.split(/\r?\n|,/).map(z=>z.trim()).filter(Boolean);_a(t,"server",{prefixes:F,onboarding:{welcome_channel:c.welcome_channel,welcome_title:c.welcome_title,welcome_description:c.welcome_description,welcome_color:c.welcome_color,welcome_image:c.welcome_image,rules_channel:c.rules_channel,rules_text:c.rules_text,rules_role_id:c.rules_role_id},logging:{...c.logging,disabled:c.disabled_logging},tickets:{panel_title:c.panel_title,panel_description:c.panel_description,panel_categories:V,panel_channel_id:c.panel_channel_id,support_roles:c.support_roles}},o).then(z=>{d(ic(z.config)),f({saving:!1,message:"Server settings saved to Niko.",error:""})}).catch(z=>f({saving:!1,message:"",error:z instanceof Error?z.message:"Could not save server settings."}))},S=c.welcome_channel,N=c.panel_channel_id,B=ra(i,c.welcome_channel),E=ra(i,c.rules_channel),R=ra(i,c.panel_channel_id),I=Zf(i,c.support_roles);return r.jsxs(r.Fragment,{children:[r.jsx(_n,{eyebrow:"Server settings",title:"Make Niko fit your room.",text:"Manage the settings that shape how Niko behaves in this server. Economy balances remain global to each user and are not configured here."}),r.jsxs("div",{className:"settings-intro",children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(J,{name:"settings"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server control room"}),r.jsxs("strong",{children:[c.prefixes.split(/\r?\n|,/).filter(Boolean).length||0," command prefixes configured"]}),r.jsx("p",{children:"Welcome flows, log destinations, and ticket panels all live here."})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]}),r.jsxs("form",{onSubmit:k,className:"settings-stack server-settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(sa,{label:"Commands",title:"Prefixes",detail:"Use one prefix per line. Niko will respond to all of them.",icon:"terminal"}),r.jsx(gt,{label:"Command prefixes",hint:"The default prefix is .",children:r.jsx("textarea",{rows:3,maxLength:200,value:c.prefixes,onChange:D=>g("prefixes",D.target.value),placeholder:".\\n!"})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(sa,{label:"Welcome flow",title:"Welcome and rules",detail:"Choose where new members see your welcome message and rules.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(gt,{label:"Welcome channel",children:r.jsxs("select",{value:S,onChange:D=>g("welcome_channel",D.target.value),children:[r.jsx("option",{value:"",children:"Disabled"}),B.map(D=>r.jsxs("option",{value:D.id,children:["#",D.name]},D.id))]})}),r.jsx(gt,{label:"Welcome title",children:r.jsx("input",{value:c.welcome_title,maxLength:200,onChange:D=>g("welcome_title",D.target.value),placeholder:"Welcome to the server"})}),r.jsx(gt,{label:"Welcome message",hint:"Supports {user} and {name}",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:c.welcome_description,onChange:D=>g("welcome_description",D.target.value),placeholder:"Welcome {user}!"})}),r.jsx(gt,{label:"Accent color",hint:"Hex color, for example 5865F2",children:r.jsxs("div",{className:"color-picker",children:[r.jsxs("div",{className:"color-field-control",children:[r.jsx("button",{type:"button",className:"color-preview",style:{backgroundColor:Jf(c.welcome_color)},onClick:()=>v(D=>!D),"aria-label":"Choose welcome accent color","aria-expanded":p}),r.jsx("input",{value:c.welcome_color,maxLength:6,onChange:D=>x(D.target.value),placeholder:"5865F2"})]}),p&&r.jsxs("div",{className:"color-picker-popover",role:"dialog","aria-label":"Choose accent color",children:[r.jsxs("div",{className:"color-picker-header",children:[r.jsx("strong",{children:"Choose color"}),r.jsx("button",{type:"button",className:"color-picker-close",onClick:()=>v(!1),"aria-label":"Close color picker",children:"×"})]}),r.jsx("input",{className:"color-picker-native",type:"color",value:Jf(c.welcome_color),onChange:D=>x(D.target.value)}),r.jsxs("div",{className:"color-picker-value",children:[r.jsx("span",{children:"#"}),r.jsx("input",{value:c.welcome_color.replace(/^#/,""),maxLength:6,onChange:D=>x(D.target.value),placeholder:"5865F2"})]})]})]})}),r.jsx(gt,{label:"Welcome image URL",children:r.jsx("input",{type:"url",value:c.welcome_image,onChange:D=>g("welcome_image",D.target.value),placeholder:"https://..."})}),r.jsx(gt,{label:"Rules channel",children:r.jsxs("select",{value:c.rules_channel,onChange:D=>g("rules_channel",D.target.value),children:[r.jsx("option",{value:"",children:"Not configured"}),E.map(D=>r.jsxs("option",{value:D.id,children:["#",D.name]},D.id))]})}),r.jsx(gt,{label:"Rules text",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:c.rules_text,onChange:D=>g("rules_text",D.target.value),placeholder:"Write the rules members should acknowledge."})}),r.jsx(gt,{label:"Role after rules acknowledgment",children:r.jsxs("select",{value:c.rules_role_id,onChange:D=>g("rules_role_id",D.target.value),children:[r.jsx("option",{value:"",children:"No role"}),Zf(i,c.rules_role_id?[c.rules_role_id]:[]).map(D=>r.jsxs("option",{value:D.id,children:["@",D.name]},D.id))]})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(sa,{label:"Audit trail",title:"Logging destinations",detail:"Pick a channel for each event type and disable categories you do not need.",icon:"book"}),r.jsx("div",{className:"server-logging-list",children:L1.map(([D,F])=>{const V=ra(i,c.logging[D]);return r.jsxs("div",{className:"server-logging-row",children:[r.jsxs("label",{className:"form-field",children:[r.jsxs("span",{className:"form-label",children:[F," logs"]}),r.jsxs("select",{value:String(c.logging[D]||""),onChange:z=>w(D,z.target.value),children:[r.jsx("option",{value:"",children:"Not set"}),V.map(z=>r.jsxs("option",{value:z.id,children:["#",z.name]},z.id))]})]}),r.jsxs("label",{className:"setting-row compact-setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enabled"}),r.jsx("small",{children:I1(i,c.logging[D])})]}),r.jsx("input",{type:"checkbox",checked:!c.disabled_logging.includes(D),onChange:()=>j(D)}),r.jsx("i",{"aria-hidden":"true"})]})]},D)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(sa,{label:"Support desk",title:"Ticket panel",detail:"Configure the public panel and decide who can handle tickets.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(gt,{label:"Panel title",children:r.jsx("input",{value:c.panel_title,maxLength:200,onChange:D=>g("panel_title",D.target.value),placeholder:"Open a Ticket"})}),r.jsx(gt,{label:"Panel channel",children:r.jsxs("select",{value:N,onChange:D=>g("panel_channel_id",D.target.value),children:[r.jsx("option",{value:"",children:"Keep current panel channel"}),R.map(D=>r.jsxs("option",{value:D.id,children:["#",D.name]},D.id))]})}),r.jsx(gt,{label:"Panel description",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:c.panel_description,onChange:D=>g("panel_description",D.target.value),placeholder:"Tell members what the ticket panel is for."})}),r.jsx(gt,{label:"Ticket categories",hint:"One category per line",children:r.jsx("textarea",{rows:4,value:c.panel_categories,onChange:D=>g("panel_categories",D.target.value),placeholder:"General\\nSupport\\nReports"})}),r.jsx(gt,{label:"Support roles",hint:"Hold Ctrl/Cmd to select more than one",children:r.jsx("select",{multiple:!0,value:c.support_roles,onChange:D=>g("support_roles",Array.from(D.target.selectedOptions,F=>F.value)),children:I.map(D=>r.jsxs("option",{value:D.id,children:["@",D.name]},D.id))})})]}),r.jsx("p",{className:"form-hint",children:"Saving panel settings updates the existing posted panel when Niko can find its saved message."})]}),r.jsx(R1,{state:h})]})]})}function F1({auth:t}){const s=rs();return r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"n"}),r.jsx("div",{className:"eyebrow",children:"Private workspace"}),r.jsxs("h1",{children:["Settle in, ",r.jsx("em",{children:"admin."})]}),r.jsx("p",{children:"Sign in with Discord to see your Niko profile and manage the servers you look after."}),t.oauth_available?r.jsxs("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard",children:[r.jsx(J,{name:"lock"})," Continue with Discord ",r.jsx(J,{name:"arrow"})]}):r.jsxs("div",{className:"notice warning",children:["Discord login is not configured yet. Add ",r.jsx("code",{children:"DISCORD_CLIENT_SECRET"})," to the environment and restart the bot."]}),!s&&r.jsx("p",{className:"form-hint",children:"The public bot configuration is still loading."}),r.jsx("a",{className:"back-link",href:"/",onClick:i=>{i.preventDefault(),he("/")},children:"Return to public site"})]})})]})}function B1({section:t,guild:s,stats:i,csrfToken:o,refreshToken:c}){const[d,h]=P.useState(null),[f,p]=P.useState([]),[v,g]=P.useState(null),[x,w]=P.useState(null),[j,k]=P.useState(!0),[S,N]=P.useState("");return P.useEffect(()=>{k(!0),N(""),(t==="overview"?Lx(s.id).then(h):t==="leveling"?Promise.all([Ix(s.id),Sm(s.id),Nm(s.id)]).then(([E,R,I])=>{p(E),g(R),w(I)}):Promise.all([Sm(s.id),Nm(s.id)]).then(([E,R])=>{g(E),w(R)})).catch(E=>N(E instanceof Error?E.message:"This server could not be loaded.")).finally(()=>k(!1))},[s.id,t,c]),j?r.jsxs("div",{className:"section-loading section-skeleton",role:"status","aria-label":`Loading ${t}`,children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsxs("span",{children:["Loading ",t,"..."]})]}):S?r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Couldn’t load this page."}),r.jsx("span",{children:S}),r.jsx("button",{className:"button button-muted",onClick:()=>window.location.reload(),children:"Try again"})]}):t==="overview"&&d?r.jsx(C1,{overview:d}):t==="leveling"?r.jsx(T1,{guildId:s.id,rows:f,config:v,resources:x,csrfToken:o}):t==="moderation"?r.jsx(M1,{guildId:s.id,config:v,csrfToken:o}):t==="server"?r.jsx(V1,{guildId:s.id,config:v,resources:x,csrfToken:o}):t==="customization"?r.jsx(_1,{guildId:s.id,config:v,csrfToken:o}):r.jsx(E1,{guildId:s.id,config:v,csrfToken:o})}function O1(){return r.jsxs("div",{className:"section-loading section-skeleton dashboard-loading",role:"status",children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"Preparing your dashboard..."})]})}function z1(){rs();const[t,s]=P.useState(Tm),[i,o]=P.useState(null),[c,d]=P.useState(null),[h,f]=P.useState(null),[p,v]=P.useState([]),[g,x]=P.useState(null),[w,j]=P.useState(!0),[k,S]=P.useState(""),[N,B]=P.useState(0),[E,R]=P.useState(!1),[I,D]=P.useState(null);if(P.useEffect(()=>{const ie=()=>s(Tm());return window.addEventListener("popstate",ie),()=>window.removeEventListener("popstate",ie)},[]),P.useEffect(()=>{j(!0),Promise.all([lc(),pa()]).then(([ie,Pe])=>(o(ie),d(Pe),ie.authenticated?Promise.all([jm(),uc(),cc().catch(()=>null)]).then(([Ie,Ae,Y])=>{f(Ie),v(Ae),D((Y==null?void 0:Y.role)||null)}):null)).catch(ie=>S(ie instanceof Error?ie.message:"Dashboard unavailable")).finally(()=>j(!1))},[]),P.useEffect(()=>{if(t.view!=="guild"){x(null);return}const ie=p.find(Pe=>Pe.id===t.guildId&&Pe.installed!==!1);ie?(x(ie),localStorage.setItem("niko-guild",ie.id)):t.guildId&&p.length&&he(dc())},[p,t.guildId,t.view]),w||!i)return r.jsxs("div",{className:"dashboard-state",children:[r.jsx("div",{className:"loading-ring"}),r.jsx("p",{children:"Connecting to Niko…"})]});if(k)return r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Connection issue"}),r.jsxs("h1",{children:["Couldn’t load",r.jsx("br",{}),r.jsx("em",{children:"your workspace."})]}),r.jsx("p",{children:k}),r.jsxs("button",{className:"button button-primary",onClick:()=>window.location.reload(),children:["Try again ",r.jsx(J,{name:"arrow"})]})]})})]});if(!i.authenticated)return r.jsx(F1,{auth:i});const F=ie=>{ie.installed!==!1&&(localStorage.setItem("niko-guild",ie.id),he(Es(ie.id,t.section)))},V=ie=>{ie.installed!==!1&&(localStorage.setItem("niko-guild",ie.id),he(Es(ie.id,"overview")))},z=ie=>{he(g?Es(g.id,ie):Es())},oe=()=>he(Es()),le=()=>he(dc()),xe=async()=>{if(!E){R(!0);try{const[ie,Pe]=await Promise.all([lc(),pa()]);if(o(ie),d(Pe),ie.authenticated){const[Ie,Ae,Y]=await Promise.all([jm(),uc(),cc().catch(()=>null)]);f(Ie),v(Ae),D((Y==null?void 0:Y.role)||null)}B(Ie=>Ie+1),S("")}catch(ie){S(ie instanceof Error?ie.message:"Dashboard refresh failed")}finally{R(!1)}}};let ve;return t.view==="servers"?ve=r.jsx(N1,{guilds:p,onManage:V}):t.view==="guild"?ve=g?r.jsx(B1,{section:t.section,guild:g,stats:c,csrfToken:i.csrf_token,refreshToken:N},`${g.id}-${t.section}`):r.jsx(O1,{}):ve=r.jsx(S1,{user:i.user,overview:h,guilds:p,onServers:le,onManage:V}),r.jsx(Mp,{user:i.user,guilds:p,selectedGuild:g,view:t.view,section:t.section,stats:c,onHome:oe,onServers:le,onGuildChange:F,onSectionChange:z,onRefresh:xe,refreshing:E,staffRole:I,children:ve})}function U1({value:t,onChange:s,placeholder:i="Search documentation...",onFocus:o,onBlur:c}){const[d,h]=P.useState(!1),f=P.useRef(null),[p,v]=P.useState(!1);P.useEffect(()=>{const k=S=>{var N;(S.metaKey||S.ctrlKey)&&S.key==="k"&&(S.preventDefault(),(N=f.current)==null||N.focus())};return document.addEventListener("keydown",k),()=>document.removeEventListener("keydown",k)},[]);const g=()=>{h(!0),v(!0),o==null||o()},x=()=>{h(!1),setTimeout(()=>v(!1),200),c==null||c()},w=k=>{s(k.target.value)},j=k=>{var S;k.key==="Escape"&&((S=f.current)==null||S.blur())};return r.jsxs("div",{className:`doc-search-bar ${p?"expanded":""}`,children:[r.jsxs("div",{className:"search-input-wrapper",children:[r.jsx(J,{name:"search",className:"search-icon"}),r.jsx("input",{ref:f,type:"text",value:t,onChange:w,onFocus:g,onBlur:x,onKeyDown:j,placeholder:i,className:"search-input","aria-label":"Search documentation"}),r.jsxs("kbd",{className:"search-shortcut",children:[r.jsx("span",{className:"shortcut-key",children:"⌘"}),"K"]})]}),r.jsxs("div",{className:"search-hint",children:["Press ",r.jsx("kbd",{children:"⌘K"})," to focus search"]})]})}function W1({selectedCategory:t,onSelectCategory:s,sections:i,allCategoriesLabel:o="All Categories"}){return r.jsx("div",{className:"doc-filters",children:r.jsxs("div",{className:"filter-tabs",role:"tablist","aria-label":"Filter by category",children:[r.jsx("button",{role:"tab","aria-selected":t==="",className:`filter-tab ${t===""?"active":""}`,onClick:()=>s(""),children:o}),i.map(c=>r.jsxs("button",{role:"tab","aria-selected":t===c.id,className:`filter-tab ${t===c.id?"active":""}`,onClick:()=>s(c.id),children:[r.jsx(J,{name:c.icon,size:14}),r.jsx("span",{children:c.label})]},c.id))]})})}function ac({doc:t,variant:s="default"}){const i="page"in t?t.page:t,[o,c]=P.useState(!1),d=p=>{p.preventDefault(),he(`/docs/${i.slug}`)},h=p=>{(p.key==="Enter"||p.key===" ")&&(p.preventDefault(),he(`/docs/${i.slug}`))};if(s==="compact")return r.jsx("a",{href:`/docs/${i.slug}`,onClick:d,onKeyDown:h,className:"doc-card-compact",tabIndex:0,role:"button",children:r.jsxs("div",{className:"compact-content",children:[r.jsx("span",{className:"compact-title",children:i.title}),r.jsx("span",{className:"compact-excerpt",children:i.excerpt})]})});const f="highlights"in t?t.highlights:[];return r.jsx("article",{className:`doc-card ${s==="highlighted"?"highlighted":""}`,children:r.jsxs("div",{className:`doc-card-content ${o?"loaded":""}`,children:[r.jsxs("div",{className:"doc-card-header",children:[r.jsx("span",{className:"doc-category",children:i.category.replace(/-/g," ")}),r.jsxs("span",{className:"doc-order",children:["#",i.order]})]}),r.jsx("h3",{className:"doc-title",children:i.title}),r.jsx("p",{className:"doc-excerpt",children:i.excerpt}),f.length>0&&r.jsx("div",{className:"doc-highlights",children:f.slice(0,2).map((p,v)=>r.jsxs("p",{className:"highlight-snippet",children:[p.slice(0,150),p.length>150?"...":""]},v))}),r.jsxs("div",{className:"doc-card-footer",children:[r.jsx("div",{className:"doc-tags",children:i.tags.slice(0,3).map(p=>r.jsxs("span",{className:"doc-tag",children:["#",p]},p))}),r.jsxs("a",{href:`/docs/${i.slug}`,onClick:d,onKeyDown:h,className:"doc-read-more",children:["Read more ",r.jsx(J,{name:"arrow",size:14})]})]})]})})}const Oe=[{slug:"welcome",title:"Welcome to Niko",category:"getting-started",excerpt:"New to Niko? Start here to understand what the bot can do for your server.",tags:["introduction","overview","beginner"],order:1,content:`
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
    `}];function $1(t){return Oe.find(s=>s.slug===t)}const Mn=[{id:"getting-started",label:"Getting Started",description:"New to Niko? Start here.",icon:"icon_home",count:Oe.filter(t=>t.category==="getting-started").length},{id:"setup",label:"Setup",description:"Configure Niko for your server.",icon:"icon_settings",count:Oe.filter(t=>t.category==="setup").length},{id:"economy",label:"Economy",description:"Money, jobs, banking, and more.",icon:"icon_economy",count:Oe.filter(t=>t.category==="economy").length},{id:"leveling",label:"Leveling",description:"XP, levels, and rankings.",icon:"icon_leveling",count:Oe.filter(t=>t.category==="leveling").length},{id:"moderation",label:"Moderation",description:"Moderation tools and commands.",icon:"icon_moderation",count:Oe.filter(t=>t.category==="moderation").length},{id:"automod",label:"AutoMod",description:"Automated moderation features.",icon:"icon_automod",count:Oe.filter(t=>t.category==="automod").length},{id:"logging",label:"Logging",description:"Server event logging.",icon:"icon_settings",count:Oe.filter(t=>t.category==="logging").length},{id:"social",label:"Social",description:"Community engagement features.",icon:"icon_heart",count:Oe.filter(t=>t.category==="social").length},{id:"utility",label:"Utility",description:"Helpful tools and utilities.",icon:"icon_utility",count:Oe.filter(t=>t.category==="utility").length},{id:"voice",label:"Voice",description:"Voice and music features.",icon:"icon_bot",count:Oe.filter(t=>t.category==="voice").length},{id:"ai",label:"AI",description:"AI-powered features.",icon:"icon_ai",count:Oe.filter(t=>t.category==="ai").length},{id:"dashboard",label:"Dashboard",description:"Web dashboard guides.",icon:"icon_settings",count:Oe.filter(t=>t.category==="dashboard").length},{id:"tips",label:"Tips",description:"Tips and best practices.",icon:"icon_lightbulb",count:Oe.filter(t=>t.category==="tips").length}];function fy(){const[t,s]=P.useState({query:"",category:"",tags:[]}),i=P.useCallback(p=>{s(v=>({...v,query:p.toLowerCase(),tags:[]}))},[]),o=P.useCallback(p=>{s(v=>({...v,category:p,tags:[]}))},[]),c=P.useCallback(p=>{s(v=>{const g=v.tags.includes(p)?v.tags.filter(x=>x!==p):[...v.tags,p];return{...v,tags:g,query:""}})},[]),d=P.useCallback(()=>{s({query:"",category:"",tags:[]})},[]),h=P.useMemo(()=>{const{query:p,category:v,tags:g}=t;if(!p&&!v&&g.length===0)return Oe.map(w=>({page:w,score:1,highlights:[]}));const x=[];for(const w of Oe)if(!(v&&w.category!==v)&&!(g.length>0&&!g.some(j=>w.tags.includes(j))))if(p){const j=H1(w,p);if(j===0)continue;const k=G1(w,p);x.push({page:w,score:j,highlights:k})}else x.push({page:w,score:1,highlights:[]});return x.sort((w,j)=>j.score!==w.score?j.score-w.score:w.page.order-j.page.order),x},[t]),f=t.query!==""||t.category!==""||t.tags.length>0;return{filters:t,setQuery:i,setCategory:o,toggleTag:c,clearFilters:d,results:h,hasActiveFilters:f,resultCount:h.length}}function H1(t,s){let i=0;const o=s.toLowerCase();t.title.toLowerCase()===o?i+=100:t.title.toLowerCase().includes(o)&&(i+=50),t.excerpt.toLowerCase().includes(o)&&(i+=25),t.content.toLowerCase().includes(o)&&(i+=10);for(const c of t.tags)c.toLowerCase().includes(o)&&(i+=15);return t.category.toLowerCase().includes(o)&&(i+=5),i}function G1(t,s){const i=[],o=s.toLowerCase(),c=3;if(t.title.toLowerCase().includes(o)&&(i.push(t.title),i.length>=c)||t.excerpt.toLowerCase().includes(o)&&(i.push(t.excerpt),i.length>=c))return i;const d=t.content.split(`
`).filter(h=>h.trim());for(const h of d)if(h.toLowerCase().includes(o)){const f=h.replace(/#{1,6}\s?/g,"").trim();if(f.length>10&&(i.push(f),i.length>=c))break}return i}function K1(){return P.useMemo(()=>{const s={};return Oe.forEach(i=>{i.tags.forEach(o=>{s[o]=(s[o]||0)+1})}),Object.entries(s).map(([i,o])=>({tag:i,count:o})).sort((i,o)=>o.count-i.count)},[])}function q1({slug:t}){var p,v;const{setCategory:s,clearFilters:i}=fy();P.useEffect(()=>{window.location.hash!==`#/docs/${t}`&&window.history.replaceState(null,"",`#/docs/${t}`)},[t]);const o=$1(t);if(!o)return r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"docs"}),r.jsx("main",{className:"shell page-main docs-page",children:r.jsxs("div",{className:"docs-not-found",children:[r.jsx(J,{name:"doc",size:48,className:"not-found-icon"}),r.jsx("h1",{children:"Page Not Found"}),r.jsxs("p",{children:[`We couldn't find documentation for "`,t,'".']}),r.jsxs("div",{className:"not-found-actions",children:[r.jsx("button",{onClick:()=>he("/docs"),children:"Browse all documentation"}),r.jsx("button",{onClick:()=>{he("/docs"),i()},children:"Clear filters"})]})]})}),r.jsx(St,{})]});const c=g=>{const x=[],w=/(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*)/g;let j=0,k,S=0;for(;(k=w.exec(g))!==null;){k.index>j&&x.push(g.slice(j,k.index));const N=k[0];if(N.startsWith("`")&&N.endsWith("`")&&N.length>2)x.push(r.jsx("code",{className:"doc-inline-code",children:N.slice(1,-1)},S++));else if(N.startsWith("[")){const B=N.match(/^\[([^\]]+)\]\(([^)]+)\)$/);B?x.push(r.jsx("a",{href:B[2],target:"_blank",rel:"noreferrer",children:c(B[1])},S++)):x.push(N)}else N.startsWith("**")?x.push(r.jsx("strong",{children:c(N.slice(2,-2))},S++)):N.startsWith("*")?x.push(r.jsx("em",{children:c(N.slice(1,-1))},S++)):x.push(N);j=k.index+N.length}return j<g.length&&x.push(g.slice(j)),x},h=(g=>{const x=g.split(`
`),w=[];let j=0,k=null,S=[];const N=()=>{if(S.length===0)return;const E=k==="ol"?"ol":"ul";w.push(r.jsx(E,{className:`doc-content-list ${k==="ol"?"doc-content-list-ol":""}`,children:S.map((R,I)=>r.jsx("li",{children:c(R)},I))},`list-${w.length}`)),S=[],k=null},B=()=>{var I;const E=w[w.length-1];P.isValidElement(E)&&((I=E.props)==null?void 0:I.className)==="doc-content-spacer"||w.push(r.jsx("div",{className:"doc-content-spacer"},`spacer-${w.length}`))};for(;j<x.length;){const R=x[j].trim();if(!R){N(),B(),j+=1;continue}if(R.startsWith("```")){N();const F=[];let V=j+1;for(;V<x.length&&x[V].trim()!=="```";)F.push(x[V]),V+=1;w.push(r.jsx("pre",{className:"doc-code-block",children:r.jsx("code",{children:F.join(`
`)})},`code-${j}`)),j=V+1;continue}if(R.startsWith("|")){N();const F=[];let V=j;for(;V<x.length&&x[V].trim().startsWith("|");){const xe=x[V].trim().replace(/^\|/,"").replace(/\|$/,"").split("|").map(ve=>ve.trim());F.push(xe),V+=1}const z=F.length>1&&F[1].every(xe=>/^:?-{2,}:?$/.test(xe.replace(/\s+/g,""))),oe=F[0],le=z?F.slice(2):F.slice(1);oe.length>1&&w.push(r.jsxs("table",{className:"doc-table",children:[r.jsx("thead",{children:r.jsx("tr",{children:oe.map((xe,ve)=>r.jsx("th",{children:c(xe)},ve))})}),r.jsx("tbody",{children:le.map((xe,ve)=>r.jsx("tr",{children:xe.map((ie,Pe)=>r.jsx("td",{children:c(ie)},Pe))},ve))})]},`table-${j}`)),j=V;continue}if(R.startsWith("### ")){N(),w.push(r.jsx("h4",{className:"doc-heading doc-heading-h4",children:R.slice(4)},`h-${j}`)),j+=1;continue}if(R.startsWith("## ")){N(),w.push(r.jsx("h3",{className:"doc-heading doc-heading-h3",children:R.slice(3)},`h-${j}`)),j+=1;continue}if(R.startsWith("# ")){N(),w.push(r.jsx("h2",{className:"doc-heading doc-heading-h2",children:R.slice(2)},`h-${j}`)),j+=1;continue}if(R.startsWith("> ")){N(),w.push(r.jsx("blockquote",{className:"doc-blockquote",children:c(R.slice(2))},`q-${j}`)),j+=1;continue}const I=R.match(/^[-*]\s+(.*)$/);if(I){k!=="ul"&&N(),k="ul",S.push(I[1]),j+=1;continue}const D=R.match(/^\d+\.\s+(.*)$/);if(D){k!=="ol"&&N(),k="ol",S.push(D[1]),j+=1;continue}N(),w.push(r.jsx("p",{className:"doc-paragraph",children:c(R)},`p-${j}`)),j+=1}return N(),w})(o.content),f=h.filter(g=>P.isValidElement(g)&&(g.type==="h2"||g.type==="h3"));return r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page docs-detail-page",children:[r.jsx("div",{className:"docs-detail-back",children:r.jsxs("button",{onClick:()=>he("/docs"),className:"back-button",children:[r.jsx(J,{name:"arrow",size:16}),"Back to Documentation"]})}),r.jsxs("header",{className:"doc-article-header",children:[r.jsxs("div",{className:"doc-article-meta",children:[r.jsx("span",{className:"doc-category-badge",children:((p=Mn.find(g=>g.id===o.category))==null?void 0:p.label)||o.category}),r.jsxs("span",{className:"doc-order-badge",children:["Article #",o.order]})]}),r.jsx("h1",{className:"doc-article-title",children:o.title}),r.jsx("p",{className:"doc-article-excerpt",children:o.excerpt}),r.jsx("div",{className:"doc-article-tags",children:o.tags.map(g=>r.jsxs("span",{className:"doc-tag-pill",children:["#",g]},g))})]}),r.jsx("article",{className:"doc-article-content",children:h}),r.jsx("footer",{className:"doc-article-footer",children:r.jsx("div",{className:"doc-nav-container",children:r.jsxs("div",{className:"doc-nav-col",children:[r.jsx("span",{className:"doc-nav-label",children:"Category"}),r.jsxs("button",{className:"doc-nav-link",onClick:()=>{s(o.category),he("/docs")},children:[r.jsx(J,{name:"arrow",size:14}),"View all ",(v=Mn.find(g=>g.id===o.category))==null?void 0:v.label]})]})})}),f.length>0&&r.jsxs("aside",{className:"doc-toc",children:[r.jsxs("div",{className:"toc-title",children:[r.jsx(J,{name:"utility",size:16}),r.jsx("span",{children:"On this page"})]}),r.jsx("nav",{className:"toc-nav",children:f.map((g,x)=>{var j;const w=(j=g.props.className)==null?void 0:j.includes("doc-heading-h2");return r.jsx("a",{href:`#${w?"h2-":"h3-"}-${x}`,className:`toc-link ${w?"toc-h2":"toc-h3"}`,children:g.props.children},x)})})]})]}),r.jsx(St,{})]})}function X1(){var I,D;const[t,s]=P.useState(!1),[i,o]=P.useState(""),[c,d]=P.useState(!1),{filters:h,setQuery:f,setCategory:p,toggleTag:v,clearFilters:g,results:x,hasActiveFilters:w,resultCount:j}=fy(),k=K1();P.useEffect(()=>{const F=()=>{const V=window.location.hash.slice(1);if(V.startsWith("#/docs/")){const z=V.replace("#/docs/",""),oe=Oe.find(le=>le.slug===z);oe&&(o(oe.category),p(oe.category))}};return F(),window.addEventListener("hashchange",F),()=>window.removeEventListener("hashchange",F)},[]);const S=()=>{d(!0)},N=F=>{o(F),p(F),s(!1)},B=()=>{h.query||d(!1)},E=F=>{he(`/docs/${F}`),f(""),d(!1)},R=P.useMemo(()=>{const F={};return x.forEach(V=>{const z=V.page.category;F[z]||(F[z]=[]),F[z].push(V)}),F},[x]);return r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page",children:[r.jsx("div",{className:"docs-hero",children:r.jsxs("div",{className:"docs-hero-content",children:[r.jsx("div",{className:"eyebrow docs-eyebrow",children:"Documentation Center"}),r.jsxs("h1",{className:"docs-title",children:["Everything you need to know about",r.jsx("br",{}),r.jsx("span",{className:"title-accent",children:"using Niko"})]}),r.jsx("p",{className:"docs-subtitle",children:"Comprehensive guides, command references, and tips to help you get the most out of your server bot."})]})}),r.jsx("div",{className:`docs-search-section ${c?"active":""}`,children:r.jsxs("div",{className:"docs-search-container",children:[r.jsx(U1,{value:h.query,onChange:f,placeholder:"Search documentation, commands, guides...",onFocus:S,onBlur:B}),c&&h.query&&x.length>0&&r.jsxs("div",{className:"search-results-dropdown",children:[r.jsxs("div",{className:"search-results-header",children:[r.jsxs("span",{className:"results-count",children:[j," ",j===1?"result":"results"]}),r.jsx("button",{className:"clear-search-btn",onClick:()=>{f(""),g(),o("")},children:"Clear"})]}),r.jsx("div",{className:"search-results-list",children:x.slice(0,8).map((F,V)=>r.jsxs("button",{className:"search-result-item",onClick:()=>E(F.page.slug),onMouseEnter:()=>{},children:[r.jsx("div",{className:"result-icon",children:r.jsx(J,{name:"doc",size:18})}),r.jsxs("div",{className:"result-content",children:[r.jsx("div",{className:"result-title",children:F.page.title}),r.jsx("div",{className:"result-excerpt",children:F.page.excerpt}),F.highlights.length>0&&r.jsxs("div",{className:"result-highlight",children:[F.highlights[0].slice(0,100),"..."]})]}),r.jsx(J,{name:"arrow",size:14,className:"result-arrow"})]},F.page.slug))}),x.length>8&&r.jsx("div",{className:"search-results-footer",children:r.jsxs("span",{children:["Showing 8 of ",x.length," results. Browse all docs below."]})})]})]})}),r.jsxs("div",{className:"docs-mobile-nav",children:[r.jsx("button",{className:"mobile-menu-toggle",onClick:()=>s(!t),"aria-label":"Toggle documentation menu",children:r.jsx(J,{name:"utility",size:20})}),t&&r.jsxs("div",{className:"mobile-nav-panel",children:[r.jsxs("div",{className:"mobile-nav-header",children:[r.jsx("h3",{children:"Documentation"}),r.jsx("button",{className:"close-menu-btn",onClick:()=>s(!1),"aria-label":"Close menu",children:r.jsx(J,{name:"utility",size:16,className:"rotated"})})]}),r.jsx("div",{className:"mobile-nav-sections",children:Mn.map(F=>r.jsxs("button",{className:`mobile-nav-item ${i===F.id?"active":""}`,onClick:()=>{N(F.id)},children:[r.jsx(J,{name:F.icon,size:18}),r.jsx("span",{className:"mobile-section-label",children:F.label}),r.jsx("span",{className:"mobile-section-count",children:F.count})]},F.id))})]})]}),k.length>0&&!w&&r.jsxs("div",{className:"docs-tags-cloud",children:[r.jsxs("div",{className:"tags-cloud-title",children:[r.jsx(J,{name:"utility",size:16}),r.jsx("span",{children:"Popular Topics"})]}),r.jsx("div",{className:"tags-cloud-list",children:k.slice(0,15).map(({tag:F,count:V})=>r.jsxs("button",{className:"tag-cloud-item",onClick:()=>v(F),style:{fontSize:`${.75+Math.min(V/4,1)}rem`},children:["#",F,r.jsx("span",{className:"tag-count",children:V})]},F))})]}),r.jsx("div",{className:"docs-category-filters",children:r.jsx(W1,{selectedCategory:h.category,onSelectCategory:N,sections:Mn})}),w&&r.jsxs("div",{className:"docs-results-header",children:[r.jsxs("div",{className:"results-info",children:[r.jsxs("span",{className:"results-count-large",children:[j," ",j===1?"article":"articles"]}),h.query&&r.jsxs("span",{className:"search-query-display",children:['for "',r.jsx("strong",{children:h.query}),'"']})]}),r.jsxs("button",{className:"clear-all-btn",onClick:()=>{g(),o("")},disabled:!w,children:[r.jsx(J,{name:"utility",size:14}),"Clear all filters"]})]}),r.jsx("div",{className:"docs-content",children:w?r.jsx("div",{className:"search-results-view",children:Object.entries(R).map(([F,V])=>{var z;return r.jsxs("section",{className:"results-category",children:[r.jsx("h2",{className:"category-title",children:((z=Mn.find(oe=>oe.id===F))==null?void 0:z.label)||F}),r.jsx("div",{className:"category-results-grid",children:V.map(oe=>r.jsx(ac,{doc:oe,variant:"highlighted"},oe.page.slug))})]},F)})}):i?r.jsxs("div",{className:"category-view",children:[r.jsxs("div",{className:"category-header",children:[r.jsx("h2",{className:"category-page-title",children:((I=Mn.find(F=>F.id===i))==null?void 0:I.label)||i}),r.jsx("p",{className:"category-description",children:(D=Mn.find(F=>F.id===i))==null?void 0:D.description})]}),r.jsx("div",{className:"category-articles",children:Oe.filter(F=>F.category===i).sort((F,V)=>F.order-V.order).map(F=>r.jsx(ac,{doc:F},F.slug))})]}):r.jsx("div",{className:"all-categories-view",children:Mn.map(F=>r.jsxs("section",{className:"docs-section",id:`section-${F.id}`,children:[r.jsxs("div",{className:"section-header",children:[r.jsx("div",{className:"section-icon",children:r.jsx(J,{name:F.icon,size:28})}),r.jsxs("div",{className:"section-info",children:[r.jsx("h2",{className:"section-title",children:F.label}),r.jsx("p",{className:"section-description",children:F.description})]}),r.jsx("span",{className:"section-count",children:F.count})]}),r.jsx("div",{className:"section-articles",children:Oe.filter(V=>V.category===F.id).sort((V,z)=>V.order-z.order).map(V=>r.jsx(ac,{doc:V},V.slug))})]},F.id))})}),r.jsxs("div",{className:"docs-footer-note",children:[r.jsx(J,{name:"book",size:20}),r.jsxs("div",{children:[r.jsx("strong",{children:"Want more detail?"}),r.jsxs("p",{children:["The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in the"," ",r.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"docs/"})," ","folder."]})]})]})]}),r.jsx(St,{})]})}function Y1(){const t=rs(),[s,i]=P.useState(null);P.useEffect(()=>{pa().then(i).catch(()=>{})},[]);const o=[["spark","AI that remembers","Thoughtful conversation with a cozy personality and controls that respect your community."],["chart","A living economy","Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],["shield","Confident moderation","Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],["users","Community rituals","Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."]];return r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"home"}),r.jsxs("main",{children:[r.jsxs("section",{className:"hero shell",children:[r.jsxs("div",{className:"hero-copy",children:[r.jsxs("div",{className:"eyebrow",children:[r.jsx("span",{className:"status-dot"})," Discord companion · online"]}),r.jsxs("div",{className:"hero-identity",children:[r.jsx("span",{className:"hero-avatar",children:t!=null&&t.bot_avatar_url?r.jsx("img",{src:t.bot_avatar_url,alt:"Niko"}):"n"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Niko"}),r.jsx("small",{children:"Your server’s calm, capable co-pilot"})]})]}),r.jsxs("h1",{children:["Useful tools for a ",r.jsx("em",{children:"better server."})]}),r.jsx("p",{children:"Niko handles the everyday work of running a Discord community, so your moderators can focus on the people in it."}),r.jsxs("div",{className:"hero-buttons",children:[r.jsxs("a",{className:"button button-primary",href:(t==null?void 0:t.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Invite Niko ",r.jsx(J,{name:"arrow"})]}),r.jsx("a",{className:"button button-muted",href:"/commands",onClick:c=>{c.preventDefault(),he("/commands")},children:"Explore commands"})]}),r.jsxs("div",{className:"stats-strip",children:[r.jsxs("div",{children:[r.jsx("strong",{children:ye(s==null?void 0:s.guild_count)}),r.jsx("span",{children:"servers"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:ye(s==null?void 0:s.user_count)}),r.jsx("span",{children:"members"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:ye(s==null?void 0:s.command_count)}),r.jsx("span",{children:"commands"})]})]})]}),r.jsx("div",{className:"hero-art","aria-label":"A preview of Niko's server workspace",children:r.jsxs("div",{className:"workspace-preview",children:[r.jsxs("div",{className:"workspace-preview-top",children:[r.jsxs("span",{className:"preview-dots",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"server workspace"}),r.jsxs("span",{className:"preview-status",children:[r.jsx("span",{className:"status-dot"})," live"]})]}),r.jsxs("div",{className:"preview-body",children:[r.jsxs("div",{className:"preview-sidebar",children:[r.jsx("span",{className:"preview-label",children:"NIKO"}),r.jsx("b",{children:"Overview"}),r.jsx("span",{children:"Economy"}),r.jsx("span",{children:"Leveling"}),r.jsx("span",{children:"Moderation"}),r.jsx("span",{children:"AI controls"})]}),r.jsxs("div",{className:"preview-main",children:[r.jsx("span",{className:"preview-label",children:"SERVER SNAPSHOT"}),r.jsx("strong",{children:"Everything in one place."}),r.jsxs("div",{className:"preview-stats",children:[r.jsxs("span",{children:[r.jsx("b",{children:ye(s==null?void 0:s.user_count)}),r.jsx("small",{children:"members"})]}),r.jsxs("span",{children:[r.jsx("b",{children:ye(s==null?void 0:s.command_count)}),r.jsx("small",{children:"commands"})]})]}),r.jsxs("div",{className:"preview-line",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]})]})]})]})})]}),r.jsxs("section",{className:"shell intro-section",children:[r.jsx("div",{className:"section-kicker",children:"Why Niko"}),r.jsxs("div",{className:"intro-grid",children:[r.jsxs("h2",{children:["The good kind of",r.jsx("br",{}),r.jsx("em",{children:"always-on."})]}),r.jsx("p",{children:"Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile."})]})]}),r.jsx("section",{className:"shell feature-grid",children:o.map(([c,d,h])=>r.jsxs("article",{className:"feature-card",children:[r.jsx("span",{className:"feature-icon",children:r.jsx(J,{name:c})}),r.jsx("h3",{children:d}),r.jsx("p",{children:h}),r.jsxs("a",{href:"/docs",onClick:f=>{f.preventDefault(),he("/docs")},children:["Learn more ",r.jsx(J,{name:"arrow"})]})]},d))}),r.jsxs("section",{className:"shell callout",children:[r.jsxs("div",{children:[r.jsx("div",{className:"section-kicker",children:"Ready when you are"}),r.jsxs("h2",{children:["A calmer, cleverer home",r.jsx("br",{}),"for your community."]})]}),r.jsxs("a",{className:"button button-primary",href:(t==null?void 0:t.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Bring Niko in ",r.jsx(J,{name:"arrow"})]})]})]}),r.jsx(St,{})]})}const Q1=[{code:"USDT",label:"Tether"},{code:"ETH",label:"Ethereum"},{code:"BTC",label:"Bitcoin"},{code:"BNB",label:"BNB"},{code:"LTC",label:"Litecoin"},{code:"DOGE",label:"Dogecoin"},{code:"TRX",label:"TRON"},{code:"XMR",label:"Monero"}];function J1(){const s=new URLSearchParams(window.location.search).get("token")||"",[i,o]=P.useState("5"),[c,d]=P.useState("USDT"),[h,f]=P.useState(!1),[p,v]=P.useState(""),[g,x]=P.useState(null),[w,j]=P.useState(null),[k,S]=P.useState(!1);P.useEffect(()=>{s||S(!0)},[s]),P.useEffect(()=>{if(!(g!=null&&g.status_url)||g.paid)return;const B=setInterval(async()=>{try{const E=await qe(g.status_url);j(E),E.paid&&clearInterval(B)}catch{}},5e3);return()=>clearInterval(B)},[g]);const N=async B=>{B.preventDefault(),f(!0),v("");try{const E=await qe("/api/donations/invoice",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:s,amount:parseFloat(i),currency:c})});x(E),E.error&&(v(E.error),x(null))}catch(E){v(E instanceof Error?E.message:"Could not create invoice.")}finally{f(!1)}};return k?r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Invalid donation link"}),r.jsxs("h1",{children:["This link is ",r.jsx("em",{children:"invalid."})]}),r.jsxs("p",{children:["The donation link is missing or has expired. Use the"," ",r.jsx("code",{children:"/donate"})," command in Discord to generate a new one."]}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>he("/"),children:"Return home"})]})})]}):w!=null&&w.paid?r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"✓"}),r.jsx("div",{className:"eyebrow",children:"Payment confirmed"}),r.jsxs("h1",{children:["Thank you ",r.jsx("em",{children:"for supporting!"})]}),r.jsx("p",{children:"Your donation has been confirmed. You will receive the Supporter badge shortly."}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>he("/"),children:"Return home"})]})})]}):r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"home"}),r.jsx("main",{className:"page-main",children:r.jsx("div",{className:"shell",children:r.jsxs("div",{className:"page-heading",style:{maxWidth:500,margin:"0 auto"},children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:15},children:"Support Niko"}),r.jsxs("h1",{children:["Keep Niko ",r.jsx("em",{children:"running."})]}),r.jsx("p",{style:{color:"var(--muted)",marginBottom:30},children:"Your donation helps cover hosting costs and keeps Niko running for all servers. Choose an amount and cryptocurrency below."}),g!=null&&g.pay_link?r.jsxs("div",{className:"dash-panel",style:{marginBottom:24},children:[r.jsx("div",{className:"panel-heading",children:r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Invoice created"}),r.jsx("h3",{children:"Complete your payment"})]})}),r.jsxs("p",{style:{color:"var(--muted)",fontSize:12,marginBottom:16},children:["Amount: ",r.jsxs("strong",{children:["$",parseFloat(i).toFixed(2)," USD"]})," in"," ",r.jsx("strong",{children:c})]}),r.jsxs("p",{style:{color:"var(--dim)",fontSize:10,marginBottom:16},children:["Track ID: ",r.jsx("code",{children:g.track_id})," · Expires in 60 minutes"]}),r.jsxs("a",{className:"button button-primary",href:g.pay_link,target:"_blank",rel:"noopener noreferrer",children:["Pay now ",r.jsx(J,{name:"arrow"})]}),r.jsx("p",{style:{color:"var(--dim)",fontSize:10,marginTop:12},children:"Payment will be confirmed automatically once the transaction is processed on-chain."})]}):r.jsxs("form",{onSubmit:N,className:"dash-panel",style:{marginBottom:24},children:[r.jsxs("div",{className:"form-grid",children:[r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Amount (USD)"}),r.jsx("input",{type:"number",min:"1",max:"10000",step:"0.01",value:i,onChange:B=>o(B.target.value)}),r.jsx("small",{children:"Minimum $1.00, maximum $10,000.00"})]}),r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Cryptocurrency"}),r.jsx("select",{value:c,onChange:B=>d(B.target.value),children:Q1.map(B=>r.jsxs("option",{value:B.code,children:[B.label," (",B.code,")"]},B.code))})]})]}),p&&r.jsx("p",{className:"form-error",style:{marginTop:12},role:"alert",children:p}),r.jsx("div",{style:{marginTop:16},children:r.jsx("button",{className:"button button-primary",type:"submit",disabled:h,children:h?"Creating invoice…":"Create invoice"})})]}),r.jsxs("div",{className:"docs-footer-note",style:{marginTop:20},children:[r.jsx("strong",{children:"How it works"}),r.jsx("p",{children:'1. Choose an amount and currency above · 2. Click "Pay now" to open the payment page · 3. Send crypto to the displayed address · 4. Payment is confirmed automatically once processed on-chain'})]})]})})})]})}const Z1={privacy:{title:"Privacy policy",intro:"Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",sections:[["Information we use","User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature. The dashboard stores daily aggregate message, join, and leave counts without message text or member IDs."],["How it is used","Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],["Storage and retention","Data is stored by the server hosting Niko in local JSON and SQLite files. Economy, leveling, and configuration data remain until removed. Daily server activity totals are retained as aggregates. AI conversation history is limited and can be cleared with /clearhistory."],["Third-party services","When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Music and external lookup features may contact their respective services."],["Your choices","Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."]]},terms:{title:"Terms of service",intro:"By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",sections:[["Permitted use","Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],["Availability","Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],["Moderation","The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],["AI content","AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],["Virtual items","In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],["Contact","Questions or concerns can be sent through the Niko support server."]]},community:{title:"Community policy",intro:"These community expectations apply to every server that uses Niko. By adding the bot to a server, the server's owners and administrators agree to uphold these standards.",sections:[["Purpose","Niko is a community companion for Discord servers of all kinds. To keep the platform safe for everyone, all servers using Niko must follow the expectations below in addition to Discord's Terms of Service and Community Guidelines."],["Discrimination and harassment","Servers must not permit or promote discrimination, harassment, or hate speech targeting people based on race, ethnicity, national origin, religion, disability, gender, gender identity or expression, sexual orientation, age, veteran status, or any other protected identity characteristic."],["Illegal and malicious content","Servers must not create, host, share, or distribute illegal or malicious content. This includes, but is not limited to: child sexual abuse material (CSAM), malware and other malicious software, gore or shock content, pirated media and/or software, content that facilitates violence or terrorism, scams and phishing, and any other content that is illegal under applicable law."],["Other prohibited conduct","Servers must not use Niko to facilitate doxxing, targeted harassment campaigns, sextortion, trafficking, or the sexualization of minors in any form."],["Enforcement and investigations","When a server is reported or flagged for potentially violating this policy, Niko will send a warning notice to the server. The notice is followed by an investigation by Niko staff. Servers that cooperate in good faith and are found not to be breaking the policies will not receive any further action."],["Obstruction of investigations","Banning, kicking, or otherwise removing the staff member(s) sent to investigate, or hiding, deleting, or tampering with potential evidence, is treated as an admission of guilt. Doing so will result in the server — and any users who are involved — being permanently blacklisted from further use of Niko, in addition to any other action the investigation warrants."],["Reporting","If you believe a server using Niko is violating this policy, report it through the Niko support server. Reports are reviewed by staff and handled confidentially."]]}};function oc({type:t}){const s=Z1[t];return r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:t}),r.jsxs("main",{className:"shell page-main legal-page",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Niko legal"}),r.jsx("h1",{children:s.title}),r.jsx("p",{children:s.intro}),r.jsx("small",{children:"Effective date: 1 January 2025"})]}),r.jsx("div",{className:"legal-copy",children:s.sections.map(([i,o])=>r.jsxs("section",{children:[r.jsx("h2",{children:i}),r.jsx("p",{children:o})]},i))})]}),r.jsx(St,{})]})}const eS=[{key:"txt",label:"TXT",icon:"📄"},{key:"html",label:"HTML",icon:"🌐"},{key:"csv",label:"CSV",icon:"📊"},{key:"json",label:"JSON",icon:"{ }"}],py=t=>typeof t!="number"||t<0||t>16777215?"":`#${t.toString(16).padStart(6,"0")}`,Zn=t=>(t==null?void 0:t.url)||(t==null?void 0:t.proxy_url)||"",gy=t=>/\.(?:png|jpe?g|gif|webp|bmp|svg)(?:[?#]|$)/i.test(t)||t.startsWith("data:image/"),yy=t=>/\.(?:mp4|webm|mov|m4v|ogg)(?:[?#]|$)/i.test(t)||t.startsWith("data:video/"),tS=t=>t.url?t.url:t.id?`https://cdn.discordapp.com/stickers/${t.id}.${t.format_type===4?"gif":"png"}`:"";function nS(t){var i;const s=Zn(t);return s?(i=t==null?void 0:t.content_type)!=null&&i.startsWith("video/")?!0:yy(s):!1}const ep=new RegExp("(`[^`\\n]+`)|(\\[([^\\]\\n]+)\\]\\((https?:\\/\\/[^\\s)\\] ]+)\\))|(\\*\\*)|(?<!\\*)\\*(?!\\*)|(~~)","g"),sS=/(https?:\/\/[^\s<>)]+)/g,tp={bold:"**",italic:"*",strike:"~~"},rS=new Set(["t","T","d","D","f","F","R"]);function iS(t,s){if(!Number.isFinite(t)||!rS.has(s))return null;const i=new Date(t*1e3);if(Number.isNaN(i.getTime()))return null;if(s==="R"){const c=t-Math.floor(Date.now()/1e3),d=Math.abs(c),h=d<60?"second":d<3600?"minute":d<86400?"hour":d<604800?"day":d<2592e3?"week":d<31536e3?"month":"year",f=h==="second"?1:h==="minute"?60:h==="hour"?3600:h==="day"?86400:h==="week"?604800:h==="month"?2592e3:31536e3;return new Intl.RelativeTimeFormat(void 0,{numeric:"always"}).format(Math.round(c/f),h)}const o={...s==="t"||s==="T"?{hour:"numeric",minute:"2-digit"}:{},...s==="T"?{second:"2-digit"}:{},...s==="d"?{year:"numeric",month:"2-digit",day:"2-digit"}:{},...s==="D"?{year:"numeric",month:"long",day:"numeric"}:{},...s==="f"?{year:"numeric",month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}:{},...s==="F"?{weekday:"long",year:"numeric",month:"long",day:"numeric",hour:"numeric",minute:"2-digit"}:{}};return new Intl.DateTimeFormat(void 0,o).format(i)}function aS(t){const s=[];let i=0,o;const c=d=>{if(!d)return;const h=d.split(/(<a?:[A-Za-z0-9_~]+:\d+>|<t:-?\d+:[tTdDfFR]>)/g);for(const f of h){if(!f)continue;const p=f.match(/^<(a?):([A-Za-z0-9_~]+):(\d+)>$/);if(p){s.push({type:"emoji",name:p[2],id:p[3],animated:p[1]==="a"});continue}const v=f.match(/^<t:(-?\d+):([tTdDfFR])>$/);if(v){s.push({type:"timestamp",unix:Number(v[1]),style:v[2],raw:f});continue}const g=f.split(sS);for(let x=0;x<g.length;x++)g[x]&&(x%2===1?s.push({type:"link",text:g[x],url:g[x]}):s.push({type:"text",text:g[x]}))}};for(ep.lastIndex=0;(o=ep.exec(t))!==null;)o.index>i&&c(t.slice(i,o.index)),o[1]!==void 0?s.push({type:"code",text:o[1].slice(1,-1)}):o[2]!==void 0?s.push({type:"link",text:o[3],url:o[4]}):o[5]!==void 0?s.push({type:"marker",fmt:"bold"}):o[6]!==void 0?s.push({type:"marker",fmt:"italic"}):o[7]!==void 0&&s.push({type:"marker",fmt:"strike"}),i=o.index+o[0].length;return i<t.length&&c(t.slice(i)),s}function oS(t){const s=[],i=[],o=new Set,c=d=>{i.length>0?i[i.length-1].children.push(d):s.push(d)};for(const d of aS(t))if(d.type==="text")c({kind:"text",text:d.text});else if(d.type==="code")c({kind:"code",text:d.text});else if(d.type==="link")c({kind:"link",text:d.text,url:d.url});else if(d.type==="emoji")c({kind:"emoji",name:d.name,id:d.id,animated:d.animated});else if(d.type==="timestamp")c({kind:"timestamp",unix:d.unix,style:d.style,raw:d.raw});else if(d.type==="marker")if(o.has(d.fmt)){const h=i.map(v=>v.fmt).lastIndexOf(d.fmt),f=i.splice(h);f.forEach(v=>o.delete(v.fmt));const p={kind:"fmt",fmt:d.fmt,children:[...f[0].children]};for(const v of f.slice(1))p.children.push({kind:"text",text:tp[v.fmt]??""}),p.children.push(...v.children);c(p)}else i.push({fmt:d.fmt,children:[]}),o.add(d.fmt);if(i.length>0)for(const d of i){c({kind:"text",text:tp[d.fmt]??""});for(const h of d.children)c(h)}return s}const vy=(t,s)=>t.map((i,o)=>{const c=`${s}-${o}`;switch(i.kind){case"text":return r.jsx("span",{children:i.text},c);case"code":return r.jsx("code",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:4,padding:"0 5px",color:"#f2b8c2",fontFamily:"monospace",fontSize:"0.92em"},children:i.text},c);case"emoji":return r.jsx("img",{src:`https://cdn.discordapp.com/emojis/${i.id}.${i.animated?"gif":"png"}`,alt:`:${i.name}:`,title:`:${i.name}:`,style:{width:22,height:22,objectFit:"contain",verticalAlign:"-0.35em",display:"inline-block"},onError:d=>{d.currentTarget.alt=`:${i.name}:`}},c);case"timestamp":{const d=iS(i.unix,i.style);return d?r.jsx("time",{dateTime:new Date(i.unix*1e3).toISOString(),title:i.raw,children:d},c):r.jsx("span",{children:i.raw},c)}case"link":return r.jsx("a",{href:i.url,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",textDecoration:"none"},onMouseEnter:d=>{d.currentTarget.style.textDecoration="underline"},onMouseLeave:d=>{d.currentTarget.style.textDecoration="none"},children:i.text},c);case"fmt":{const d={};return i.fmt==="bold"&&(d.fontWeight=700),i.fmt==="italic"&&(d.fontStyle="italic"),i.fmt==="strike"&&(d.textDecoration="line-through"),r.jsx("span",{style:d,children:vy(i.children,c)},c)}}}),ia=t=>vy(oS(t),"md");function Xn({text:t,muted:s}){const i=t.split(`
`),o=[];return i.forEach((c,d)=>{const h=c.trimStart(),p=d===i.length-1?null:r.jsx("br",{},`br${d}`);h.startsWith("-# ")?o.push(r.jsxs("span",{style:{color:s?"#6d737a":"#949ba4",fontSize:12},children:[ia(h.slice(3)),p]},d)):/^#{1,4}\s/.test(h)?o.push(r.jsxs("span",{style:{color:"#f2f3f5",fontWeight:700,fontSize:16},children:[ia(h),p]},d)):h.startsWith("> ")?o.push(r.jsxs("span",{style:{display:"inline-block",color:"#b5bac1",borderLeft:"3px solid #4e5058",paddingLeft:8},children:[ia(h.slice(2)),p]},d)):h.startsWith("```")?o.push(r.jsxs("pre",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:6,padding:"10px 12px",overflowX:"auto",whiteSpace:"pre-wrap",wordBreak:"break-word",fontFamily:"monospace",fontSize:12.5,color:"#dbdee1",margin:"2px 0"},children:[h.replace(/^```[a-zA-Z]*/,"").replace(/```$/,""),p]},d)):o.push(r.jsxs("span",{children:[ia(c),p]},d))}),r.jsx("span",{style:{whiteSpace:"pre-wrap",wordBreak:"break-word"},children:o})}function lS({embed:t}){const s=py(t.color)||"#5865f2",i=t.author,o=t.footer,c=Zn(t.thumbnail),d=Zn(t.image);return r.jsxs("div",{style:{display:"flex",gap:12,maxWidth:560,marginTop:8,background:"#2b2d31",border:"1px solid #3f4147",borderLeft:`4px solid ${s}`,borderRadius:6,padding:"10px 12px"},children:[r.jsxs("div",{style:{flex:1,minWidth:0},children:[(i==null?void 0:i.name)&&r.jsxs("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:4},children:[i.icon_url&&r.jsx("img",{src:i.icon_url||i.proxy_icon_url,alt:"",style:{width:18,height:18,borderRadius:"50%",verticalAlign:"-4px",marginRight:6}}),i.name]}),t.title&&r.jsx("div",{style:{color:"#00a8fc",fontWeight:600,margin:"2px 0 4px",fontSize:14},children:t.url?r.jsx("a",{href:t.url,target:"_blank",rel:"noopener noreferrer",style:{color:"inherit",textDecoration:"none"},children:r.jsx(Xn,{text:t.title})}):r.jsx(Xn,{text:t.title})}),t.description&&r.jsx("div",{style:{color:"#dbdee1",fontSize:13,lineHeight:1.5},children:r.jsx(Xn,{text:t.description})}),t.fields&&t.fields.length>0&&r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:"6px 12px",marginTop:8},children:t.fields.map((h,f)=>r.jsxs("div",{style:{flex:h.inline?"0 1 45%":"1 1 100%",minWidth:0,marginBottom:4},children:[h.name&&r.jsx("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:2},children:r.jsx(Xn,{text:h.name})}),h.value&&r.jsx("div",{style:{color:"#dbdee1",fontSize:13},children:r.jsx(Xn,{text:h.value})})]},f))}),d&&r.jsx("a",{href:d,target:"_blank",rel:"noopener noreferrer",style:{display:"block",marginTop:8},children:r.jsx("img",{src:d,alt:"",style:{maxWidth:"100%",maxHeight:300,borderRadius:4,display:"block"},onError:h=>{h.currentTarget.style.display="none"}})}),((o==null?void 0:o.text)||t.timestamp)&&r.jsxs("div",{style:{display:"flex",alignItems:"center",gap:6,marginTop:6,color:"#949ba4",fontSize:11},children:[(o==null?void 0:o.icon_url)&&r.jsx("img",{src:o.icon_url||o.proxy_icon_url,alt:"",style:{width:16,height:16,borderRadius:"50%"}}),(o==null?void 0:o.text)&&r.jsx("span",{children:o.text}),t.timestamp&&r.jsx("span",{children:String(t.timestamp).replace("T"," ").replace("+00:00"," UTC")})]})]}),c&&r.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:r.jsx("img",{src:c,alt:"",style:{width:80,height:80,borderRadius:6,objectFit:"cover"},onError:h=>{h.currentTarget.style.display="none"}})})]})}function fa({component:t}){switch(t.type){case 17:{const s=py(t.accent_color);return r.jsxs("div",{style:{display:"flex",overflow:"hidden",maxWidth:560,marginTop:8,background:"#2b2d31",border:`1px solid ${s||"#3f4147"}`,borderRadius:12},children:[s&&r.jsx("div",{style:{flex:"0 0 4px",background:s}}),r.jsx("div",{style:{flex:1,minWidth:0,padding:"6px 12px 8px"},children:(t.components||[]).map((i,o)=>r.jsx(fa,{component:i},o))})]})}case 1:return r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,margin:"6px 0"},children:(t.components||[]).map((s,i)=>r.jsx(fa,{component:s},i))});case 2:{const s=t.emoji,i=`${(s==null?void 0:s.name)??""}${t.label?` ${t.label}`:""}`.trim();return t.style===5&&!!t.url?r.jsx("a",{href:t.url,target:"_blank",rel:"noopener noreferrer",style:{display:"inline-block",padding:"3px 14px",background:"#5865f2",borderRadius:4,color:"#fff",fontSize:13,fontWeight:600,textDecoration:"none"},children:i||"Button"}):r.jsx("span",{style:{display:"inline-block",padding:"3px 14px",background:"#4e5058",borderRadius:4,color:t.disabled?"#8a8e96":"#f2f3f5",fontSize:13,cursor:t.disabled?"not-allowed":"default",opacity:t.disabled?.55:1},children:i||"Button"})}case 9:{const s=[...t.components||[]];return t.accessory&&s.push(t.accessory),r.jsx("div",{style:{display:"flex",alignItems:"center",gap:10,margin:"4px 0"},children:s.map((i,o)=>r.jsx(fa,{component:i},o))})}case 10:return r.jsx("div",{style:{color:"#dbdee1",fontSize:14,lineHeight:1.5,margin:"4px 0",wordBreak:"break-word"},children:r.jsx(Xn,{text:t.content||""})});case 18:return r.jsx("div",{style:{color:"#f2f3f5",fontWeight:700,textTransform:"uppercase",letterSpacing:"0.04em",fontSize:12,margin:"4px 0"},children:t.content});case 14:return r.jsx("div",{style:{margin:t.divider===!1?"6px 0":"9px 0",...t.divider===!1?{}:{borderTop:"1px solid #3f4147"}}});case 11:{const s=Zn(t.media);return s?r.jsx("a",{href:s,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:r.jsx("img",{src:s,alt:t.description||"",style:{width:40,height:40,borderRadius:"50%",objectFit:"cover",display:"block"},onError:i=>{i.currentTarget.style.display="none"}})}):null}case 12:{const i=(t.items||[]).filter(o=>Zn(o.media));return i.length===0?null:r.jsx("div",{style:{display:"grid",gridTemplateColumns:`repeat(auto-fill, minmax(${Math.min(220,Math.max(140,Math.floor(560/Math.max(1,i.length))))}px, 1fr))`,gap:6,margin:"6px 0"},children:i.map((o,c)=>{const d=Zn(o.media),h=o.description;return nS(o.media)?r.jsxs("figure",{style:{margin:0},children:[r.jsx("video",{src:d,controls:!0,preload:"metadata",style:{width:"100%",maxHeight:260,borderRadius:6,background:"#1e1f22"}}),h&&r.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:h})]},c):gy(d)?r.jsxs("figure",{style:{margin:0},children:[r.jsx("a",{href:d,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:r.jsx("img",{src:d,alt:h||"",style:{width:"100%",maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:f=>{f.currentTarget.style.display="none"}})}),h&&r.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:h})]},c):r.jsxs("a",{href:d,target:"_blank",rel:"noopener noreferrer",style:{display:"flex",alignItems:"center",gap:6,padding:"6px 10px",background:"#383a40",borderRadius:6,color:"#dbdee1",fontSize:12,textDecoration:"none"},children:["📎 ",h||"Attachment"]},c)})})}case 13:{const s=Zn(t.media)||t.url||"";return s?r.jsxs("a",{href:s,target:"_blank",rel:"noopener noreferrer",style:{display:"block",margin:"4px 0",color:"#00a8fc",fontSize:12.5,textDecoration:"none"},children:["📎 ",t.label||"Attachment"]}):null}default:return null}}function cS({components:t}){return r.jsx(r.Fragment,{children:t.map((s,i)=>r.jsx(fa,{component:s},i))})}function uS({text:t}){return r.jsx(Xn,{text:t})}function dS({msg:t}){const s=!!(t.attachments&&t.attachments.length>0||t.embeds&&t.embeds.length>0||t.components&&t.components.length>0||t.stickers&&t.stickers.length>0);return r.jsxs("div",{style:{padding:"10px 16px",borderBottom:"1px solid #2b2d31",fontSize:14,lineHeight:1.6},children:[r.jsxs("div",{style:{marginBottom:2},children:[r.jsx("span",{style:{color:"#949ba4",fontSize:11,fontFamily:"monospace"},children:t.timestamp})," ",r.jsx("span",{style:{color:"#f2f3f5",fontWeight:600},children:t.author})," ",r.jsxs("span",{style:{color:"#949ba4",fontSize:11},children:["(",t.author_id,")"]})]}),t.content?r.jsx("div",{style:{color:"#dbdee1"},children:r.jsx(uS,{text:t.content})}):s?null:r.jsx("div",{style:{color:"#6d737a",fontStyle:"italic",fontSize:13},children:"Message content unavailable"}),t.attachments&&t.attachments.length>0&&r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:4},children:t.attachments.map((i,o)=>yy(i)?r.jsx("video",{src:i,controls:!0,preload:"metadata",style:{maxWidth:360,maxHeight:260,borderRadius:6,background:"#1e1f22"}},o):gy(i)?r.jsx("a",{href:i,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:r.jsx("img",{src:i,alt:"",style:{maxWidth:300,maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:c=>{const d=c.currentTarget;d.style.display="none"}})},o):r.jsx("a",{href:i,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",fontSize:12,textDecoration:"none"},children:"📎 Attachment"},o))}),t.embeds&&t.embeds.length>0&&r.jsx(r.Fragment,{children:t.embeds.map((i,o)=>r.jsx(lS,{embed:i},o))}),t.stickers&&t.stickers.length>0&&r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:8},children:t.stickers.map((i,o)=>{const c=tS(i);return c?r.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:r.jsx("img",{src:c,alt:i.name||"Discord sticker",title:i.name||"Discord sticker",style:{width:160,maxWidth:"100%",maxHeight:160,objectFit:"contain",display:"block"}})},o):null})}),t.components&&t.components.length>0&&r.jsx(cS,{components:t.components})]})}function hS({transcriptId:t}){const[s,i]=P.useState(null),[o,c]=P.useState(!0),[d,h]=P.useState("");P.useEffect(()=>{c(!0),h(""),fetch(`/api/transcript/${t}`).then(p=>{if(!p.ok)throw new Error("Transcript not found");return p.json()}).then(p=>{i(p),c(!1)}).catch(p=>{h(p.message||"Failed to load transcript"),c(!1)})},[t]);const f=p=>{window.open(`/api/transcript/${t}/download?format=${p}`,"_blank")};return o?r.jsx("div",{className:"page-main",children:r.jsx("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:r.jsx("div",{style:{color:"var(--muted)",fontSize:14},children:"Loading transcript…"})})}):d||!s?r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:[r.jsx("h2",{style:{marginBottom:12},children:"Transcript not found"}),r.jsx("p",{style:{color:"var(--muted)"},children:d||"This transcript doesn't exist or has been deleted."})]})}):r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{maxWidth:800},children:[r.jsx("div",{style:{background:"var(--surface)",border:"1px solid var(--line)",borderRadius:8,padding:24,marginBottom:20},children:r.jsxs("div",{style:{display:"flex",alignItems:"flex-start",justifyContent:"space-between",gap:16,flexWrap:"wrap"},children:[r.jsxs("div",{children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:8},children:"Ticket Transcript"}),r.jsxs("h1",{style:{fontSize:24,letterSpacing:"-0.04em",margin:0},children:["#",s.channel_name]}),r.jsxs("div",{style:{color:"var(--muted)",fontSize:13,marginTop:6},children:[s.category," · ",s.message_count," messages · ",s.created_at]})]}),r.jsx("div",{style:{display:"flex",gap:8,flexWrap:"wrap"},children:eS.map(p=>r.jsxs("button",{className:"button button-small button-muted",onClick:()=>f(p.key),style:{minWidth:70},children:[r.jsx("span",{children:p.icon}),r.jsx("span",{children:p.label})]},p.key))})]})}),r.jsxs("div",{style:{background:"#1e1f22",border:"1px solid #3f4147",borderRadius:8,overflow:"hidden"},children:[s.messages.map((p,v)=>r.jsx(dS,{msg:p},v)),s.messages.length===0&&r.jsx("div",{style:{padding:40,textAlign:"center",color:"#949ba4"},children:"No messages in this transcript."})]}),r.jsxs("div",{style:{marginTop:16,padding:"12px 0",textAlign:"center",color:"var(--dim)",fontSize:12},children:["Transcript ID: ",r.jsx("code",{style:{fontFamily:"monospace"},children:t})]})]})})}const Ea=[{slug:"uwulock-starboard-overhaul",title:"UwU Lock Rebuilt & Starboard Persistence",date:"2026-09-25",version:"2.11.0",tags:["uwulock","starboard","database","fun","social"],summary:"The UwU Lock command has been completely rebuilt around the main database with immediate webhook reposts, reliable message transforms, and full Starboard integration — with proper author attribution that persists cleanly across restarts.",highlights:[{title:"Instant Webhook Transforms",description:"Locked users' messages are now deleted and immediately reposted via a shared per-channel webhook with their display name and avatar, including attachments, embeds, and stickers, with thread support and a guard against double-processing.",icon:"spark"},{title:"Real Author on the Starboard",description:"When a uwu-ified webhook message is starred, the Starboard resolves the original author from persistent attribution and renders their name, avatar, and original timestamp — not the webhook — in a clean Section with Thumbnail layout.",icon:"users"},{title:"Survives Restarts",description:"Both UwU Lock rules and Starboard configuration now live in the main database, loaded on startup via cog_load with automatic migration from the legacy JSON files and stale-webhook healing.",icon:"settings"}],changes:[{category:"added",items:["Main-database tables uwulock_config and uwulock_messages for lock rules and author attribution","Main-database tables starboard_config and starboard_messages for channel, threshold, emoji and post mappings","Automatic migration of legacy data/uwulock.json and data/starboard.json into the primary database with .migrated backups","Per-channel webhook reuse with stale-webhook detection via fetch and shared-webhook protection on removal","Thread-aware webhook sending with AllowedMentions.none and wait:true repost handling","UwU attribution storage (author name, avatar, original timestamp) for every transformed message","Starboard Section + Thumbnail rendering for uwu-locked messages with correct original author credit","Explicit UwU lock hook in events.on_message before AI triggers with a 2,000-entry dedup guard and fallback listener"]},{category:"improved",items:["UwU Lock now deletes the original message immediately instead of queuing for a background task","Attachment, embed, and sticker handling with text truncation and text-only fallback on send failure","Permission checks for Manage Messages and Manage Webhooks with localized failure messaging","Starboard reaction handling now distinguishes webhook reposts via database attribution","Starboard message edits and sends now use AllowedMentions.none for cleaner output","Webhook Channel resolution for threads via parent channel with robust create_webhook flow"]},{category:"fixed",items:["UwU Lock not creating the webhook or showing any sign it saw the message","Webhook created but original message not deleted and no new message sent","UwU transforms silently failing due to queue delay and background-task errors","Starboard not displaying correct author for uwu-locked webhook messages","Starboard and UwU Lock losing all state after a restart despite being stored","Stale or deleted webhooks leaving lock rules in a broken state"]},{category:"migrated",items:["UwU Lock from data/uwulock.json file storage to the primary database","Starboard configuration and starred post IDs from data/starboard.json to the primary database"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Added",value:"8",detail:"new persistence features",color:"#66866f"},{label:"Improved",value:"6",detail:"reliability upgrades",color:"#4a7fb5"},{label:"Fixed",value:"6",detail:"workflow bugs",color:"#d96545"}]},commits:[]},{slug:"guild-server-pulse-stats",title:"Guild Server Pulse Stats",date:"2026-09-24",tags:["dashboard","guild","analytics","stats"],summary:"Guild settings now include a Server pulse analytics card with an at-a-glance view of server size and recent community activity.",highlights:[{title:"Server Activity at a Glance",description:"The card summarizes member count, messages, and new members over the last 14 days, with interactive views for message trends, member joins and departures, and the server's members, channels, and roles.",icon:"chart"},{title:"Community Analytics",description:"Daily activity charts make it easier to spot changes in conversation and membership, with activity tracking noted from the time it is enabled.",icon:"users"}],changes:[{category:"added",items:["Server pulse analytics card in guild settings","14-day daily message activity and member join/leave charts","Server layout view for member, channel, and role counts"]}],commits:[]},{slug:"team-page-ai-name-config",title:"Team Profiles & Custom AI Names",date:"2026-09-22",version:"2.10.0",tags:["team","staff","dashboard","ai","website"],summary:"Niko's public website now introduces the people behind the bot, while server owners can give their AI a custom name and manage its experimental capabilities from the dashboard.",highlights:[{title:"Meet the Niko Team",description:"The new Team page showcases owners, developers, moderators, support staff, and other persisted staff roles with Discord-synced identities, presence, activities, bios, and profile pages.",icon:"users"},{title:"Choose Your AI's Name",description:"Server administrators can configure the AI's display name from the dashboard or the AI configuration command. The chosen name is used for mention detection and reply identity in that server.",icon:"spark"},{title:"Staff Public Listings",description:"Staff members can customize their public bio, banner, and visibility while their name and avatar remain synchronized with Discord.",icon:"settings"}],changes:[{category:"added",items:["Public Team page with persisted staff roles and linked staff profiles","Discord-synced staff presence, current activities, Spotify, streaming, and custom status display","Staff self-service controls for public bio, banner, and Team page visibility","Configurable per-server AI name in the dashboard and AI configuration command","Dashboard controls for AI Actions, Better Context, and Multimodal Conversation experiments","Learn-more dialogs explaining each AI experiment"]},{category:"improved",items:["Dashboard staff workspace navigation and responsive layout","Team profile cards and profile-page activity presentation","AI configuration persistence through the shared database","Public page metadata and favicon handling during the website build"]},{category:"fixed",items:["Team presence labels showing online staff as away","Spotify and streaming activities being hidden behind custom statuses","Staff profile updates being rejected for authorized owners","Staff profile avatars being clipped by profile banners"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Team",value:"1",detail:"new public experience",color:"#66866f"},{label:"AI",value:"4",detail:"new configuration controls",color:"#d96545"},{label:"Profiles",value:"3",detail:"public staff controls",color:"#4a7fb5"}]},commits:[]},{slug:"september-platform-updates",title:"September Platform Updates",date:"2026-09-21",version:"2.9.0",tags:["dashboard","ai","tickets","music","website"],summary:"A broad set of public improvements landed across Niko: richer ticket transcripts, a multimodal AI experiment, more reliable music playback, a redesigned dashboard experience, persistent giveaways and suggestions, and a refreshed public website with dynamic social previews.",highlights:[{title:"More Natural AI Conversations",description:"The new opt-in Multimodal Conversation experiment can understand image attachments and transcribe voice messages before generating a reply, while safely falling back to text when media processing is unavailable.",icon:"spark"},{title:"Richer Ticket Transcripts",description:"Transcript pages and HTML downloads now render Discord custom emojis, stickers, and dynamic timestamps such as <t:1788800225:f> in a more faithful format.",icon:"doc"},{title:"Dashboard & Website Refresh",description:"Dashboard navigation and mobile layouts were refined, documentation was expanded, and public routes now receive route-specific Open Graph cards generated during the build.",icon:"settings"},{title:"Reliable Long-Running Features",description:"Giveaways and suggestions now restore their state from the main database at startup, while music nodes are rescanned periodically to keep playback available.",icon:"utility"}],changes:[{category:"added",items:["Opt-in Multimodal Conversation AI experiment for image understanding and voice-message transcription","Official update notification system with a configurable server notification channel","Discord custom emoji and sticker rendering in ticket transcript pages and HTML downloads","Dynamic Discord timestamp rendering in ticket transcripts","Persistent suggestion configuration and voting buttons restored from the main database","Automatic hourly Lavalink node rescans with a hardcoded fallback node catalog","Additional economy SVG card API endpoints","Community Policy page on the public website","Route-specific Open Graph metadata and generated social preview cards"]},{category:"improved",items:["Dashboard navigation consistency and mobile layout","Dashboard page layout and visual polish","Music connection reliability, autoplay, Spotify playback, and node recovery","Giveaway persistence and startup restoration for MongoDB-backed data","Onboarding setup handling and configuration persistence","Poll command design and interaction flow","Ticket transcript HTML download formatting","Economy image-card font rendering, SVG output, and emoji support","Documentation pages and public website frontend"]},{category:"fixed",items:["Giveaways losing their live buttons after a restart or extended runtime","Suggestion buttons and configuration not surviving process restarts","Ticket transcript rendering for custom media and dynamic timestamps","Lavalink connection failures and stale music nodes","Broken SVG card and SVG endpoint output","Status panel polling noise and retired image-model defaults"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Added",value:"9",detail:"new capabilities",color:"#66866f"},{label:"Improved",value:"9",detail:"upgraded systems",color:"#4a7fb5"},{label:"Fixed",value:"6",detail:"reliability issues",color:"#d96545"}]},commits:["ac102df Fixed the Open Graph image cards","33aaf12 Added dynamic Open Graph tags to the website","3153e28 Rebuilt the frontend","bab665e Added a new Lavalink node","ee44a5e Improved the music cog","bc61e34 Released the new Multimodal Conversation AI experiment","c46af7d Fixed the suggestion system persistence","25703ca Added a broadcast system for official updates and announcements","265bdb2 Added dynamic timestamp rendering inside ticket transcripts","d8005db Added custom emoji and sticker rendering to ticket transcripts","e561d84 Fixed the dashboards navbar","a0bab78 Improved the dashboards mobile layout","fb2f5aa Patched giveaway persistence for MongoDB compatibility","d77779e Fixed several dashboard flaws","b8e06a5 Improved the dashboard pages","3708207 Patched issues in the giveaway and onboarding cogs","d58bb37 Redesigned the poll command","bb523e3 Added a Community Policy page","5b34c7c Updated the documentation pages","3a52fc2 Added new economy card API endpoints","df3ea25 Fixed an issue in the SVG endpoints","39b7340 Fixed an error in the SVG cards","9e3483e Replaced HTML entities with valid XML numeric character references in economy cards"]},{slug:"economy-leveling-overhaul",title:"Economy Items, Leveling Cards & Subcommands",date:"2026-09-08",version:"2.8.0",tags:["economy","leveling","shop","image-cards"],summary:"The economy shop expanded with four new consumable items that affect gameplay — Rigged Coin, Streak Insurance, Double Down Token, and Lucky Horseshoe — plus daily streak milestone bonuses at 7, 14, 30, 60, and 90 days. The leveling system now renders rank cards and leaderboards as customizable image cards, and all leveling commands live under a single `/leveling` group with subcommands.",highlights:[{title:"New Shop Items",description:"Four new consumables: Rigged Coin (60/40 coinflip odds), Streak Insurance (protects daily streak for one missed day), Double Down Token (1.5x gambling payout), and Lucky Horseshoe (+10% work reward).",icon:"chart"},{title:"Leveling Image Cards",description:"Rank cards and the leaderboard now render as styled images with avatar, level, XP bar, and rank. Server admins can customize the card accent color and background gradient.",icon:"spark"},{title:"Leveling Subcommands",description:"All leveling commands reorganized under `/leveling` with `rank`, `leaderboard`, `panel`, and `config` subcommands. The leaderboard now has interactive pagination buttons.",icon:"settings"},{title:"Daily Streak Milestones",description:"Hitting 7, 14, 30, 60, or 90-day daily streaks now awards bonus items from the shop (Espresso Shots, Lockpicks, Lucky Charms, Rob Shields) along with a coin bonus.",icon:"utility"}],changes:[{category:"added",items:["Coinflip command with heads/tails call and double-or-nothing payout","Rigged Coin shop item — gives 60/40 coinflip odds for one use","Streak Insurance shop item — protects daily streak if you miss one day","Double Down Token shop item — next gambling win pays 1.5x","Lucky Horseshoe shop item — next work reward gets +10%","Daily streak milestone bonuses at 7/14/30/60/90 days with item rewards","Image card rendering for `/leveling rank` with customizable accent and background","Image card rendering for the leveling leaderboard","Inventory display as an image card in the shop command","Twemoji emoji rendering in economy card images","Pagination buttons (◀ ▶) on the leveling leaderboard","Card customization fields in the database: card_accent, card_bg_top, card_bg_bottom"]},{category:"improved",items:["Leveling commands restructured as `/leveling rank`, `leaderboard`, `panel`, `config` subcommands","Shop command visual layout with better font rendering on economy image cards","Crime and rob commands now check for gambling_boost effect for 1.5x payout","HTML download format for ticket transcripts","Dashboard UI refinements"]},{category:"fixed",items:["Command name conflicts between leveling and other cogs","Missing import in leveling cog after image card addition","Duplicate command alias in leveling system","Command name conflict in the gambling cog"]}],chart:{type:"bar",title:"New Shop Items & Their Effects",data:[{label:"Rigged Coin",value:3e3,color:"#c9a84c"},{label:"Streak Insurance",value:4e3,color:"#4a7fb5"},{label:"Double Down Token",value:5e3,color:"#d96545"},{label:"Lucky Horseshoe",value:2500,color:"#66866f"}]},commits:["41d86fb Expanded the gambling and economy system","bd6a09c Added image cards to the leveling system","5307bb1 Moved the leveling commands to the levels subcommand","dafd224 Added an image card to the inventory command","49fc83b Added emoji rendering to the shop command","0aca6ba Improved the shop command","30c9735 Added better font rendering to the economy system image cards","2b96835 Fixed a command name conflict","158ad8f Fixed a command name conflict in the gambling cog","d465598 Fixed a missing import","1f24ffb Fixed a duplicate command alias"]},{slug:"database-migration",title:"Database Migration to MongoDB",date:"2026-09-03",version:"2.7.0",tags:["database","mongodb","migration","infrastructure"],summary:"Every major system has been migrated from SQLite to MongoDB. The migration covered economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and the blacklist — with a custom interpreter that translates SQLite-style writes to MongoDB operations.",highlights:[{title:"Full MongoDB Migration",description:"Economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and blacklist now all store data in MongoDB instead of SQLite.",icon:"settings"},{title:"Slash Command Sync Safeguard",description:"A new check prevents redundant Discord API calls when all commands are already registered, reducing rate-limit issues on startup.",icon:"utility"},{title:"Proxy Integration",description:"A new proxy manager reduces downtime on shared hosting environments by routing API requests through a proxy layer.",icon:"shield"}],changes:[{category:"migrated",items:["Economy system — balances, banks, jobs, achievements, inventory","Leveling system — XP, levels, role rewards, card customization","Moderation system — warnings, mutes, automod config","Ticket system — panels, transcripts, support roles","Birthday system — dates, channels, messages","AFK system — status, timestamps","Sticky messages — content, channels","Blacklist — users, words, filters"]},{category:"added",items:["MongoDB interpreter that translates SQLite-style writes to proper MongoDB operations","Proxy manager for shared hosting reliability","Slash command sync safeguard to prevent redundant API calls","Context menu command support in the sync utility"]},{category:"fixed",items:["MongoDB interpreter not translating all SQLite write patterns correctly","Economy interest calculation after migration","Birthday system data persistence","Several database connection issues across various cogs","Leveling database initialization issue"]}],chart:{type:"donut",title:"Systems Migrated to MongoDB",centerLabel:"8 systems",data:[{label:"Economy",value:1,color:"#d96545"},{label:"Leveling",value:1,color:"#66866f"},{label:"Moderation",value:1,color:"#4a7fb5"},{label:"Tickets",value:1,color:"#c9a84c"},{label:"Birthdays",value:1,color:"#b07cc6"},{label:"AFK",value:1,color:"#e0976e"},{label:"Sticky Msgs",value:1,color:"#7ca898"},{label:"Blacklist",value:1,color:"#8c918e"}]},commits:["c07f9b1 Fixed the MongoDB interpreter to properly translate all SQLite database writes","0d3aca5 Migrated the blacklist to the main database","954ebac Migrated the birthday system to the main database","5013d54 Migrated the warns and mutes to use the main database","f29c217 Migrated the afk system to the main database","5732b48 Migrated the sticky messages to use the main database","b0524f1 Migrated the ticket system to the main database","70e6d7a Fixed the sync util to support context commands and slash groups","2c01817 Added a safeguard to prevent slash command syncs when all commands are already present","121afcf Added a proxy integration to reduce downtime on shared hosting","9f2f1fd Fixed several database issues across various cogs"]},{slug:"ticket-system-transcripts",title:"Ticket Transcripts & VoiceMaster",date:"2026-09-03",version:"2.6.0",tags:["tickets","transcripts","voicemaster"],summary:"The ticket system gained a web-based transcript viewer that renders ticket conversations as styled HTML pages. The VoiceMaster was also improved with better reliability and database usage. Ticket transcripts can now be downloaded as HTML or viewed online.",highlights:[{title:"Web Transcript Viewer",description:"Ticket transcripts are now rendered as styled HTML pages that can be viewed online. The HTML download format was also improved for better readability.",icon:"doc"},{title:"VoiceMaster Reliability",description:"The VoiceMaster (temporary voice channels) was improved with better database usage and reliability fixes.",icon:"utility"},{title:"Donation Dashboard Page",description:"A new customization page in the dashboard lets server admins configure donation settings without using commands.",icon:"settings"}],changes:[{category:"added",items:["Web-based ticket transcript viewer with styled HTML output","Ticket transcript database table for storing transcripts online","Dashboard customization page for donation system settings"]},{category:"improved",items:["HTML download format for ticket transcripts","VoiceMaster reliability and database usage patterns","Ticket system persistence and data handling"]},{category:"fixed",items:["Ticket transcript pages rendering incorrectly","Ticket system data loss on restart","Ticket transcript generation issues","Ticket transcript page display bugs"]}],commits:["e953321 Added a new web transcript feature to the ticket system","aa0b73b Improved the donation system and added a customization page to the dashboard","3255385 Improved the html download format for the ticket transcripts","45f1fb0 Fixed the ticket system persistence","ef4e057 Added the ticket system database migrations","d4e0bc8 Fixed the ticket transcripts","4bf5e04 Fixed an issue with the ticket transcript pages","e8dbcb0 Improved the VoiceMaster reliability and improved the database usage"]},{slug:"roleplay-music-status",title:"Roleplay, Music & Status Rotation",date:"2026-09-05",version:"2.5.0",tags:["roleplay","music","status","social"],summary:"The roleplay cog was completely rewritten to use nekos.best API GIFs with CV2 layout messages and a persistent 'hug back' button. The music cog was restructured with a ghost queue feature and fixed autoplay/Spotify playback. A status message rotation system was added with a configurable timer.",highlights:[{title:"Roleplay Rewrite",description:"The roleplay cog now fetches SFW reaction GIFs from nekos.best, renders them in styled CV2 containers, and includes a 'hug back' button that persists across restarts. A single user context menu replaces individual action menus to stay under Discord's 15-command cap.",icon:"users"},{title:"Music Ghost Queue",description:"A new ghost queue feature lets songs be queued even when nothing is currently playing. Autoplay and Spotify playback were also fixed.",icon:"utility"},{title:"Status Rotation",description:"The bot now rotates through configurable status messages on a timer (default 30s interval), with activity types and a VR device presence.",icon:"spark"}],changes:[{category:"added",items:["Status message rotation with configurable interval and activity types","Persistent status panel command for the support server (owner only)","Roleplay block feature to prevent specific users from being targeted","Ghost queue feature — queue songs even when nothing is playing","User context menu for roleplay actions (replaces per-action menus)","YouTube channel name validation for notification system"]},{category:"improved",items:["Roleplay cog complete rewrite — nekos.best GIFs, CV2 layouts, persistent buttons","Social media notification emoji formatting (Bluesky, Reddit, TikTok, Twitch icons)","Music node connection system and autoplay reliability","Spotify playback quality","Music cog restructured with better error handling"]},{category:"fixed",items:["Status rotator startup errors and activity conflicts","on_ready event error handling and reliability","Lavalink connection bug","Roleplay prefix command handling","Bluesky and Reddit notification delivery issues"]}],commits:["0c58178 Redesigned the roleplay cog","6c4ee09 Fixed the roleplay prefix commands","f1f8591 Added a roleplay block feature","e01e3e4 Added status message rotation","5e63e1d Added a persistent status panel","ae7501a Restructured the music cog","526813e Added a new ghost queue feature to the music cog","6524da1 Improved the music node connection system, fixed the autoplay, and fixed the Spotify playback","4264677 Fixed a lavalink connection bug","d62ead8 Improved the social media notification system's emojis","0f0305d Improved the social media notification formatting","42069d4 Added proper channel name validation to the YouTube notification system"]},{slug:"moderation-logging-dashboard",title:"Logging, Moderation & Documentation",date:"2026-09-07",version:"2.4.0",tags:["logging","moderation","documentation","dashboard"],summary:"Logging got two major improvements: deleted message logs now show image attachments in a MediaGallery component, and the Member category now tracks avatar changes using a Section with Thumbnail accessory. The documentation page was fully rebuilt with search, filters, and a card-based layout.",highlights:[{title:"Image Attachments in Logs",description:"Deleted message logs now render attached images in a MediaGallery component inside the log container, so moderators can see what was posted without leaving Discord.",icon:"chart"},{title:"Avatar Change Tracking",description:"The Member logging category now detects avatar changes (global and server avatars) and displays them in a Section with a Thumbnail accessory showing the new avatar.",icon:"users"},{title:"Documentation Redesign",description:"The documentation page was rebuilt from scratch with a search bar, category filters, tag cloud, card-based layout, and individual article pages with table of contents.",icon:"doc"}],changes:[{category:"added",items:["Image attachments rendered in deleted message logs via MediaGallery","Avatar change detection in Member logging with Section + Thumbnail display","Startup economy cache that loads all users into memory for accurate leaderboards","Error handler for role menu post buttons","Full-text search with result highlighting in documentation","Category filters and tag cloud in documentation","Individual documentation article pages with table of contents"]},{category:"improved",items:["Logging system now supports media_urls, thumbnail_url, and files parameters","Commands page expanded with better organization","Dashboard UI refinements","Economy interest feature — skips malformed records with non-integer user IDs"]},{category:"fixed",items:["Logging command issues","Documentation command references","Status device detection issue","Status rotator conflicts between multiple status types","on_ready event reliability with proper error handling"]}],commits:["722a34f Added avatar updates to the logging cogs Member logs","1d82ea1 Moved file attachments inside the main log message for the deleted message logs","358d537 Added a startup economy cache to fix the leaderboard","566e0c4 Improved the dashboard","132bcbb Fully redesigned the documentation page","4f7a89a Improved the commands page","6d953b6 Fixed the logging command","a202687 Fixed some documentation issues","49d22ad Fixed the documentation command references","52de287 Added an error handler to the post role menu button"]},{slug:"website-launch-donation",title:"Website, Donation System & API",date:"2026-09-02",version:"2.3.0",tags:["website","donations","api"],summary:"The public website and documentation portal launched with a React + Vite frontend, documentation center with search, and a commands reference page. The donation system gained a dashboard customization page, and the Flask API backend was fixed to use proper database calls.",highlights:[{title:"Public Website",description:"A complete public website built with React and Vite featuring a landing page, documentation center, command reference, dashboard, and legal pages.",icon:"spark"},{title:"Documentation Center",description:"The documentation page was redesigned with a card-based layout, individual article pages, and a modern visual design matching the bot's aesthetic.",icon:"doc"},{title:"Donation Dashboard",description:"Server admins can now configure donation settings through a new dashboard page instead of relying solely on commands.",icon:"settings"}],changes:[{category:"added",items:["Public website with landing page, documentation center, and command reference","Donation system customization page in the dashboard","Ticket transcript viewer web page","Donate page with Oxapay integration"]},{category:"improved",items:["Flask API to use proper database calls instead of direct SQLite access","Website commands page with expanded details","Database layer reliability for production"]},{category:"fixed",items:["Flask API database call issues","Several database-related bugs across cogs","node_modules folder accidentally committed to repository"]}],commits:["132bcbb Fully redesigned the documentation page","aa0b73b Improved the donation system and added a customization page to the dashboard","bd5e3be Expanded the website's commands page","e266644 Fixed the flask API to use the proper database calls","e99ed47 Fixed several database related issues","c783514 Minor API fixes and improvements","0df4478 Added the node_modules folder to the gitignore file"]}];function mS(t){return Ea.find(s=>s.slug===t)}function fS(){const t=new Set;return Ea.forEach(s=>s.tags.forEach(i=>t.add(i))),Array.from(t).sort()}function pS(){const[t,s]=P.useState(""),i=fS(),o=t?Ea.filter(c=>c.tags.includes(t)):Ea;return r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"home"}),r.jsxs("main",{className:"shell page-main changelog-page",children:[r.jsxs("div",{className:"changelog-hero",children:[r.jsxs("div",{className:"eyebrow",children:[r.jsx("span",{className:"status-dot"})," What's new"]}),r.jsxs("h1",{className:"changelog-title",children:["Changelog",r.jsx("br",{}),r.jsx("span",{className:"title-accent",children:"& updates"})]}),r.jsx("p",{className:"changelog-subtitle",children:"A record of every improvement, fix, and new feature added to Niko. Grouped by release for clarity."})]}),r.jsxs("div",{className:"changelog-tags",children:[r.jsx("button",{className:`changelog-tag-btn ${t===""?"active":""}`,onClick:()=>s(""),children:"All"}),i.slice(0,12).map(c=>r.jsx("button",{className:`changelog-tag-btn ${t===c?"active":""}`,onClick:()=>s(c),children:c},c))]}),r.jsx("div",{className:"changelog-timeline",children:o.map((c,d)=>r.jsxs("article",{className:"changelog-entry",children:[r.jsxs("div",{className:"changelog-entry-date-col",children:[r.jsx("div",{className:"changelog-date-dot"}),d<o.length-1&&r.jsx("div",{className:"changelog-date-line"})]}),r.jsxs("div",{className:"changelog-entry-card",children:[r.jsxs("div",{className:"changelog-entry-header",children:[r.jsxs("div",{className:"changelog-entry-meta",children:[r.jsx("time",{className:"changelog-entry-date",children:new Date(c.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),c.version&&r.jsxs("span",{className:"changelog-version",children:["v",c.version]})]}),r.jsx("h2",{className:"changelog-entry-title",children:c.title}),r.jsx("p",{className:"changelog-entry-summary",children:c.summary})]}),r.jsx("div",{className:"changelog-entry-highlights",children:c.highlights.slice(0,2).map(h=>r.jsxs("div",{className:"changelog-highlight-mini",children:[r.jsx("span",{className:"highlight-mini-icon",children:r.jsx(J,{name:h.icon,size:16})}),r.jsxs("div",{children:[r.jsx("strong",{children:h.title}),r.jsxs("p",{children:[h.description.slice(0,120),"..."]})]})]},h.title))}),r.jsx("div",{className:"changelog-entry-tags",children:c.tags.map(h=>r.jsx("span",{className:"changelog-tag",children:h},h))}),r.jsxs("button",{className:"changelog-read-more",onClick:()=>{he(`/changelog/${c.slug}`)},children:["Read full release notes ",r.jsx(J,{name:"arrow",size:14})]})]})]},c.slug))}),o.length===0&&r.jsxs("div",{className:"changelog-empty",children:[r.jsx(J,{name:"doc",size:40}),r.jsx("p",{children:"No changelog entries match this filter."})]})]}),r.jsx(St,{})]})}function gS({slug:t}){const s=mS(t);return s?r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"home"}),r.jsxs("main",{className:"shell page-main changelog-page changelog-detail",children:[r.jsx("div",{className:"changelog-back",children:r.jsxs("button",{onClick:()=>he("/changelog"),className:"back-button",children:[r.jsx(J,{name:"arrow",size:16}),"Back to Changelog"]})}),r.jsxs("header",{className:"changelog-detail-header",children:[r.jsxs("div",{className:"changelog-detail-meta",children:[r.jsx("time",{children:new Date(s.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),s.version&&r.jsxs("span",{className:"changelog-version",children:["v",s.version]})]}),r.jsx("h1",{children:s.title}),r.jsx("p",{className:"changelog-detail-summary",children:s.summary}),r.jsx("div",{className:"changelog-detail-tags",children:s.tags.map(i=>r.jsx("span",{className:"changelog-tag",children:i},i))})]}),r.jsxs("section",{className:"changelog-highlights-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"Highlights"}),r.jsx("div",{className:"changelog-highlights-grid",children:s.highlights.map(i=>r.jsxs("div",{className:"changelog-highlight-card",children:[r.jsx("span",{className:"highlight-icon",children:r.jsx(J,{name:i.icon,size:22})}),r.jsx("h3",{children:i.title}),r.jsx("p",{children:i.description})]},i.title))})]}),s.chart&&r.jsx(yS,{chart:s.chart}),r.jsxs("section",{className:"changelog-changes-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"All Changes"}),r.jsx("div",{className:"changelog-changes-grid",children:s.changes.map(i=>r.jsxs("div",{className:`changelog-change-group changelog-change-${i.category}`,children:[r.jsx("h3",{className:"change-group-title",children:r.jsx("span",{className:`change-badge change-badge-${i.category}`,children:i.category})}),r.jsx("ul",{children:i.items.map((o,c)=>r.jsx("li",{children:o},c))})]},i.category))})]}),s.commits.length>0&&r.jsxs("section",{className:"changelog-commits-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"Commits"}),r.jsx("div",{className:"changelog-commits-list",children:s.commits.map(i=>{const[o,...c]=i.split(" ");return r.jsxs("div",{className:"changelog-commit",children:[r.jsx("code",{className:"commit-hash",children:o.slice(0,7)}),r.jsx("span",{className:"commit-msg",children:c.join(" ")})]},o)})})]}),r.jsx("nav",{className:"changelog-detail-nav",children:r.jsxs("button",{onClick:()=>he("/changelog"),children:[r.jsx(J,{name:"arrow",size:14}),"All releases"]})})]}),r.jsx(St,{})]}):r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"home"}),r.jsx("main",{className:"shell page-main changelog-page",children:r.jsxs("div",{className:"changelog-not-found",children:[r.jsx(J,{name:"doc",size:48}),r.jsx("h1",{children:"Entry Not Found"}),r.jsxs("p",{children:[`We couldn't find a changelog entry for "`,t,'".']}),r.jsx("button",{onClick:()=>he("/changelog"),children:"View all changelog entries"})]})}),r.jsx(St,{})]})}function yS({chart:t}){return r.jsxs("section",{className:"changelog-chart-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:t.title}),r.jsxs("div",{className:"changelog-chart-container",children:[t.type==="bar"&&r.jsx(vS,{chart:t}),t.type==="pie"&&r.jsx(xS,{chart:t}),t.type==="donut"&&r.jsx(wS,{chart:t}),t.type==="line"&&r.jsx(bS,{chart:t}),t.type==="timeline"&&r.jsx(kS,{chart:t}),t.type==="comparison"&&r.jsx(SS,{chart:t}),t.type==="metrics"&&r.jsx(jS,{chart:t})]})]})}function vS({chart:t}){const s=Math.max(...t.data.map(i=>i.value));return r.jsx("div",{className:"chart-bar",children:t.data.map(i=>r.jsxs("div",{className:"chart-bar-row",children:[r.jsx("span",{className:"chart-bar-label",children:i.label}),r.jsxs("div",{className:"chart-bar-track",children:[r.jsx("div",{className:"chart-bar-fill",style:{width:`${i.value/s*100}%`,background:i.color||"var(--accent)"}}),r.jsx("span",{className:"chart-bar-value",children:i.value})]})]},i.label))})}function xS({chart:t}){const s=t.data.reduce((d,h)=>d+h.value,0);let i=0;const c=t.data.map(d=>{const h=i/s*360;i+=d.value;const f=i/s*360;return{...d,start:h,end:f}}).map(d=>{const h=d.start/360*100,f=d.end/360*100;return`${d.color||"#d96545"} ${h}% ${f}%`}).join(", ");return r.jsxs("div",{className:"chart-pie-wrapper",children:[r.jsx("div",{className:"chart-pie",style:{background:`conic-gradient(${c})`}}),r.jsx("div",{className:"chart-pie-legend",children:t.data.map(d=>r.jsxs("div",{className:"chart-legend-item",children:[r.jsx("span",{className:"chart-legend-dot",style:{background:d.color||"var(--accent)"}}),r.jsx("span",{className:"chart-legend-label",children:d.label})]},d.label))})]})}function wS({chart:t}){const s=t.data.reduce((o,c)=>o+c.value,0),i=t.data.reduce((o,c)=>{const d=o.current/s*100,h=(o.current+c.value)/s*100;return o.css+=`${c.color||"#d96545"} ${d}% ${h}%, `,o.current+=c.value,o},{css:"",current:0}).css.slice(0,-2);return r.jsxs("div",{className:"chart-donut-wrapper",children:[r.jsx("div",{className:"chart-donut",style:{background:`conic-gradient(${i})`},children:r.jsx("span",{children:t.centerLabel||s})}),r.jsx("div",{className:"chart-pie-legend",children:t.data.map(o=>r.jsxs("div",{className:"chart-legend-item",children:[r.jsx("span",{className:"chart-legend-dot",style:{background:o.color||"var(--accent)"}}),r.jsx("span",{className:"chart-legend-label",children:o.label})]},o.label))})]})}function bS({chart:t}){const s=Math.max(...t.data.map(o=>o.value),1),i=t.data.map((o,c)=>{const d=t.data.length===1?50:c/(t.data.length-1)*100,h=100-o.value/s*82-9;return`${d},${h}`}).join(" ");return r.jsxs("div",{className:"chart-line-wrapper",children:[r.jsxs("svg",{className:"chart-line",viewBox:"0 0 100 100",preserveAspectRatio:"none",role:"img","aria-label":t.title,children:[r.jsx("polyline",{points:i,fill:"none",stroke:"var(--accent)",strokeWidth:"3",vectorEffect:"non-scaling-stroke"}),t.data.map((o,c)=>{const d=t.data.length===1?50:c/(t.data.length-1)*100,h=100-o.value/s*82-9;return r.jsx("circle",{cx:d,cy:h,r:"3",fill:"var(--accent)",vectorEffect:"non-scaling-stroke"},o.label)})]}),r.jsx("div",{className:"chart-line-labels",children:t.data.map(o=>r.jsx("span",{children:o.label},o.label))})]})}function kS({chart:t}){const s=Math.max(...t.data.map(i=>i.value),1);return r.jsx("div",{className:"chart-timeline",children:t.data.map(i=>r.jsxs("div",{className:"chart-timeline-item",children:[r.jsx("div",{className:"chart-timeline-marker",style:{background:i.color||"var(--accent)"}}),r.jsxs("div",{className:"chart-timeline-content",children:[r.jsx("strong",{children:i.label}),r.jsx("div",{className:"chart-timeline-track",children:r.jsx("div",{className:"chart-timeline-fill",style:{width:`${i.value/s*100}%`,background:i.color||"var(--accent)"}})}),i.detail&&r.jsx("span",{children:i.detail})]})]},i.label))})}function jS({chart:t}){return r.jsx("div",{className:"chart-metrics",children:t.data.map(s=>r.jsxs("div",{className:"chart-metric",style:{borderTopColor:s.color||"var(--accent)"},children:[r.jsx("span",{className:"chart-metric-label",children:s.label}),r.jsx("strong",{children:s.value}),s.detail&&r.jsx("small",{children:s.detail})]},s.label))})}function SS({chart:t}){const s=Math.max(...t.before.concat(t.after).map(o=>o.value),1),i=(o,c,d)=>r.jsxs("div",{className:"chart-comparison-col",children:[r.jsx("h4",{className:`comparison-label ${d}`,children:o}),c.map(h=>r.jsxs("div",{className:"chart-bar-row",children:[r.jsx("span",{className:"chart-bar-label",children:h.label}),r.jsxs("div",{className:"chart-bar-track",children:[r.jsx("div",{className:"chart-bar-fill",style:{width:`${h.value/s*100}%`,background:h.color||"var(--accent)"}}),r.jsx("span",{className:"chart-bar-value",children:h.value})]})]},h.label))]});return r.jsxs("div",{className:"chart-comparison",children:[i("Before",t.before,"comparison-before"),r.jsx("div",{className:"chart-comparison-divider",children:r.jsx(J,{name:"arrow",size:20})}),i("After",t.after,"comparison-after")]})}function Aa(t){return t.avatar_url}function NS(t){return`https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/svg/${Array.from(t).map(i=>i.codePointAt(0).toString(16)).join("-")}.svg`}function CS({emoji:t}){return t?t.kind==="custom"?r.jsx("img",{className:"presence-emoji",src:`https://cdn.discordapp.com/emojis/${t.value}.${t.animated?"gif":"png"}?size=18`,alt:t.name||"custom emoji"}):r.jsx("img",{className:"presence-emoji",src:NS(t.value),alt:t.name||t.value}):null}function TS(t){return{playing:"Playing",listening:"Listening to",watching:"Watching",streaming:"Streaming",competing:"Competing in"}[t]||(t?`${t.charAt(0).toUpperCase()}${t.slice(1)}`:"Activity")}function PS({activity:t}){const s=t.kind==="spotify",i=s?"Listening on Spotify":TS(t.type),o=s?t.details||"Spotify":t.name,c=(s?[t.state]:[t.details,t.state]).filter(h=>!!(h&&h!==o)),d=r.jsxs("span",{className:`activity-card activity-${t.kind}`,children:[t.image_url&&r.jsx("img",{className:"activity-art",src:t.image_url,alt:""}),r.jsxs("span",{className:"activity-copy",children:[r.jsx("strong",{children:i}),r.jsx("span",{children:o}),c.map((h,f)=>r.jsx("small",{children:h},`${h}-${f}`))]})]});return t.url?r.jsx("a",{className:"presence-activity",href:t.url,target:"_blank",rel:"noreferrer",children:d}):r.jsx("span",{className:"presence-activity",children:d})}function MS(t){return t.status_label||{online:"Online",idle:"Idle",dnd:"Do Not Disturb",offline:"Offline"}[t.status||"offline"]||"Offline"}function ES({member:t}){const s=t.custom_status,i=t.activities||[],o=!!(s!=null&&s.text||s!=null&&s.emoji);return!o&&!i.length?null:r.jsxs("span",{className:"presence-stack",children:[o&&r.jsxs("span",{className:"presence-line",children:[r.jsx(CS,{emoji:s==null?void 0:s.emoji}),(s==null?void 0:s.text)||"Custom status"]}),i.length>0&&r.jsx("span",{className:"presence-line activity-list",children:i.map((c,d)=>r.jsx(PS,{activity:c},`${c.kind}-${c.name}-${d}`))})]})}const xy=`
.team-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));align-items:start;gap:14px;margin-top:58px}.team-card{display:flex;flex-direction:column;min-width:0;overflow:hidden;padding:0;color:var(--ink);text-align:left;background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow-soft)}.team-card:hover{border-color:#dfaa98;transform:translateY(-2px)}.team-card-art,.team-profile-banner{min-height:105px;background:linear-gradient(135deg,var(--callout),var(--surface-muted));background-size:cover;background-position:center}.team-card-body{display:flex;align-items:flex-start;flex:1;min-width:0;gap:14px;padding:18px}.team-card-body>div:last-child{min-width:0}.team-card h2,.team-card p{overflow-wrap:anywhere}.team-avatar,.team-profile-avatar{display:grid;place-items:center;flex:0 0 auto;overflow:hidden;color:#fffaf5;background:var(--accent);border-radius:50%;font-weight:800;object-fit:cover}.team-avatar{width:56px;height:56px;margin-top:-39px;border:3px solid var(--surface)}.team-role{color:var(--accent-dark);text-transform:uppercase;letter-spacing:.1em;font:700 9px "Space Mono",monospace}.team-card h2{margin:5px 0 6px;font-size:17px}.team-card p{margin:0 0 10px;color:var(--muted);font-size:11px;line-height:1.6}.team-status{color:var(--dim);font-size:10px}.presence-stack{display:block}.presence-stack>.presence-line+.presence-line{margin-top:12px}.presence-line{display:flex;align-items:center;flex-wrap:wrap;gap:7px;margin-top:7px;color:var(--muted);font-size:10px}.presence-activity{display:inline-flex;align-items:center;gap:4px;color:inherit}.presence-activity:hover{text-decoration:none}.activity-card{display:flex;align-items:center;min-width:0;gap:8px;padding:7px 9px;background:var(--surface-muted);border:1px solid var(--line);border-radius:8px;text-align:left}.activity-art{width:30px;height:30px;flex:0 0 auto;border-radius:5px;object-fit:cover}.activity-copy{display:flex;min-width:0;flex-direction:column;gap:1px}.activity-copy strong{color:var(--accent-dark);font-size:9px;text-transform:uppercase;letter-spacing:.06em}.activity-copy span,.activity-copy small{overflow:hidden;max-width:210px;text-overflow:ellipsis;white-space:nowrap}.activity-copy span{color:var(--ink);font-size:10px}.activity-copy small{color:var(--dim);font-size:9px}.presence-emoji{width:18px;height:18px;object-fit:contain;vertical-align:middle}.is-online{color:var(--sage)}.team-profile-page{max-width:760px}.team-back{width:auto;margin:0 0 18px;border:0;background:transparent}.team-profile-banner{min-height:220px;border:1px solid var(--line);border-radius:14px 14px 0 0}.team-profile-card{padding:0 34px 38px;text-align:center;background:var(--surface);border:1px solid var(--line);border-top:0;border-radius:0 0 14px 14px;box-shadow:var(--shadow-soft)}.team-profile-avatar{width:100px;height:100px;margin:-50px auto 6px;border:5px solid var(--surface);font-size:32px;transform:translateY(-20px)}.team-profile-card h1{margin:8px 0 5px;font-size:34px;letter-spacing:-.07em}.team-profile-handle{color:var(--dim);font-size:11px}.team-profile-bio{max-width:560px;margin:27px auto 0;color:var(--muted);line-height:1.8}.team-profile-links{display:flex;justify-content:center;flex-wrap:wrap;gap:9px;margin:20px auto 0}.team-profile-links a{display:inline-flex;align-items:center;gap:7px;padding:9px 13px;color:var(--accent-dark);background:var(--surface-muted);border:1px solid var(--line);border-radius:999px;font-size:11px;font-weight:700;transition:background .18s,border-color .18s,transform .18s}.team-profile-links a:hover{background:var(--filter-active);border-color:var(--filter-border);transform:translateY(-1px)}.team-activity{display:block;width:min(100%,560px);margin:20px auto 0;padding:12px;color:var(--muted);background:var(--surface-muted);border:1px solid var(--line);border-radius:12px;font-size:10px;text-align:left}.team-activity .presence-line{margin-top:0}.team-activity .activity-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));align-items:stretch}.team-activity .activity-card{height:100%;width:100%}@media(max-width:800px){.team-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.team-grid{grid-template-columns:1fr;margin-top:38px}.team-profile-card{padding-left:18px;padding-right:18px}.team-profile-banner{min-height:150px}}`,wy=5e3;function AS(){const[t,s]=P.useState([]);return P.useEffect(()=>{let i=!0;const o=()=>{Ex().then(h=>{i&&s(h)}).catch(()=>{})},c=()=>{document.visibilityState==="visible"&&o()};o();const d=window.setInterval(()=>{document.visibilityState==="visible"&&o()},wy);return document.addEventListener("visibilitychange",c),()=>{i=!1,window.clearInterval(d),document.removeEventListener("visibilitychange",c)}},[]),r.jsxs(r.Fragment,{children:[r.jsx("style",{children:xy}),r.jsx(ze,{page:"team"}),r.jsxs("main",{className:"shell page-main",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"The people behind Niko"}),r.jsx("h1",{children:"Meet the team."}),r.jsx("p",{children:"A small group of builders, moderators, and creative minds keeping Niko friendly, useful, and moving forward."})]}),r.jsxs("div",{className:"team-grid",children:[t.map(i=>r.jsxs("button",{className:"team-card",onClick:()=>he(`/team/${i.id}`),children:[r.jsx("div",{className:"team-card-art",style:i.public_banner_url?{backgroundImage:`url(${i.public_banner_url})`}:void 0}),r.jsxs("div",{className:"team-card-body",children:[Aa(i)?r.jsx("img",{className:"team-avatar",src:Aa(i),alt:""}):r.jsx("span",{className:"team-avatar team-avatar-fallback",children:i.name.slice(0,1)}),r.jsxs("div",{children:[r.jsx("span",{className:"team-role",children:i.role_label}),r.jsx("h2",{children:i.name}),r.jsx("p",{children:i.bio||"Part of the Niko team."})]})]})]},i.id)),!t.length&&r.jsx("div",{className:"empty-state",children:"The team roster is being prepared."})]})]}),r.jsx(St,{})]})}function _S({id:t}){const[s,i]=P.useState(null),[o,c]=P.useState("");return P.useEffect(()=>{let d=!0;const h=(v=!1)=>{Ax(t).then(g=>{d&&(i(g),c(""))}).catch(g=>{d&&v&&c(g instanceof Error?g.message:"Team member not found.")})},f=()=>{document.visibilityState==="visible"&&h()};h(!0);const p=window.setInterval(()=>{document.visibilityState==="visible"&&h()},wy);return document.addEventListener("visibilitychange",f),()=>{d=!1,window.clearInterval(p),document.removeEventListener("visibilitychange",f)}},[t]),r.jsxs(r.Fragment,{children:[r.jsx("style",{children:xy}),r.jsx(ze,{page:"team"}),r.jsx("main",{className:"shell page-main team-profile-page",children:o?r.jsx("div",{className:"empty-state",children:o}):s?r.jsxs(r.Fragment,{children:[r.jsx("button",{className:"back-link team-back",onClick:()=>he("/team"),children:"← Back to team"}),r.jsx("div",{className:"team-profile-banner",style:s.public_banner_url?{backgroundImage:`url(${s.public_banner_url})`}:void 0}),r.jsxs("section",{className:"team-profile-card",children:[Aa(s)?r.jsx("img",{className:"team-profile-avatar",src:Aa(s),alt:""}):r.jsx("span",{className:"team-profile-avatar team-avatar-fallback",children:s.name.slice(0,1)}),r.jsx("div",{className:"team-role",children:s.role_label}),r.jsx("h1",{children:s.name}),r.jsxs("p",{className:"team-profile-handle",children:[s.username?`@${s.username}`:"Niko staff"," · ",r.jsx("span",{className:`status-${s.status||"offline"} ${s.status==="online"?"is-online":""}`,children:MS(s)})]}),r.jsx("p",{className:"team-profile-bio",children:s.bio||"This team member has not added an extended introduction yet."}),(s.public_links||[]).length>0&&r.jsx("nav",{className:"team-profile-links","aria-label":`${s.name}'s links`,children:(s.public_links||[]).map((d,h)=>r.jsxs("a",{href:d.url,target:"_blank",rel:"noopener noreferrer",children:[d.label||d.type," ",r.jsx("span",{"aria-hidden":"true",children:"↗"})]},`${d.type}-${h}`))}),r.jsxs("div",{className:"team-activity",children:[r.jsx(ES,{member:s}),!s.custom_status&&!(s.activities||[]).length&&"No current activity"]})]})]}):r.jsx("div",{className:"section-loading",children:"Loading profile…"})}),r.jsx(St,{})]})}const DS=[["website","Website"],["github","GitHub"],["instagram","Instagram"],["x","X"],["tiktok","TikTok"],["youtube","YouTube"],["twitch","Twitch"],["bluesky","Bluesky"],["linkedin","LinkedIn"],["reddit","Reddit"],["mastodon","Mastodon"],["facebook","Facebook"],["discord","Discord"],["other","Other"]];function RS(){const[t,s]=P.useState(null),[i,o]=P.useState(null),[c,d]=P.useState(null),[h,f]=P.useState([]),[p,v]=P.useState({public_bio:"",public_banner_url:"",public_visible:!0}),[g,x]=P.useState([]),[w,j]=P.useState({avatar_url:"",banner_url:""}),[k,S]=P.useState(""),[N,B]=P.useState(""),[E,R]=P.useState(!1),[I,D]=P.useState(!1);if(P.useEffect(()=>{Promise.all([lc(),cc(),pa(),uc()]).then(([Y,O,q,K])=>{s(Y),o(O),d(q),f(K),v({public_bio:O.profile.bio||"",public_banner_url:O.profile.public_banner_url||"",public_visible:O.profile.visible!==!1}),x(O.profile.public_links||[])}).catch(Y=>B(Y instanceof Error?Y.message:"Staff access unavailable."))},[]),!t||!i&&!N)return r.jsxs("div",{className:"dashboard-state",children:[r.jsx("div",{className:"loading-ring"}),r.jsx("p",{children:"Checking staff access…"})]});if(N||!i||!t.authenticated)return r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("div",{className:"eyebrow",children:"Staff workspace"}),r.jsx("h1",{children:"Private team area."}),r.jsx("p",{children:t!=null&&t.authenticated?N||"This area is only available to official Niko staff.":"Sign in with Discord to continue."}),!(t!=null&&t.authenticated)&&r.jsx("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard/staff",children:"Continue with Discord"}),r.jsx("button",{className:"back-link",onClick:()=>he("/dashboard"),children:"Return to dashboard"})]})})]});const F=t.user,V=`https://cdn.discordapp.com/embed/avatars/${Number(BigInt(F.id)%5n)}.png`,z=F.avatar?`https://cdn.discordapp.com/avatars/${F.id}/${F.avatar}.png?size=128`:V,oe=["owner","head_admin","graphic_designer"].includes(i.role),le=(Y,O)=>v(q=>({...q,[Y]:O})),xe=()=>x(Y=>Y.length<10?[...Y,{type:"",url:""}]:Y),ve=(Y,O,q)=>{x(K=>K.map((M,U)=>U===Y?{...M,[O]:q}:M))},ie=Y=>x(O=>O.filter((q,K)=>K!==Y)),Pe=async()=>{if(E)return;const Y=g.filter(O=>O.type.trim()||O.url.trim());if(Y.some(O=>!O.type.trim()||!O.url.trim())){B("Choose a link type and enter its URL, or remove the unfinished link."),S("");return}R(!0),B(""),S("");try{await _x({...p,public_links:Y},t.csrf_token),S("Your public team listing was saved.")}catch(O){B(O instanceof Error?O.message:"Could not save listing.")}finally{R(!1)}},Ie=async()=>{if(!I){D(!0),B(""),S("");try{await Dx(w,t.csrf_token),S("Niko's global profile was updated.")}catch(Y){B(Y instanceof Error?Y.message:"Could not update global profile.")}finally{D(!1)}}},Ae=r.jsxs("div",{className:"staff-page",children:[r.jsxs("header",{className:"staff-heading",children:[r.jsxs("div",{children:[r.jsx("div",{className:"eyebrow",children:"Staff workspace"}),r.jsx("h1",{children:"Shape your presence."}),r.jsxs("p",{children:["Manage the public details granted to your ",r.jsx("strong",{children:i.role_label})," role. Your name and avatar always come directly from Discord."]})]}),r.jsxs("div",{className:"staff-role-card",children:[r.jsx("span",{className:"staff-role-mark",children:r.jsx("img",{src:z,alt:"Your Discord profile",onError:Y=>{Y.currentTarget.onerror=null,Y.currentTarget.src=V}})}),r.jsxs("span",{children:[r.jsx("small",{children:"Signed in as"}),r.jsx("strong",{children:i.role_label})]})]})]}),r.jsxs("div",{className:"staff-layout",children:[r.jsxs("section",{className:"staff-panel staff-panel-main",children:[r.jsxs("div",{className:"staff-panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Public listing"}),r.jsx("h2",{children:"How the team sees you"}),r.jsx("p",{children:"Keep your introduction current while Discord remains the source of truth for your identity."})]}),r.jsx("span",{className:"staff-step",children:"01"})]}),r.jsxs("div",{className:"staff-fields",children:[r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Banner URL"}),r.jsx("input",{type:"url",value:p.public_banner_url,onChange:Y=>le("public_banner_url",Y.target.value),placeholder:"https://…"}),r.jsx("small",{children:"Use a publicly reachable image. Leave blank for no banner."})]}),r.jsxs("section",{className:"staff-links-section","aria-labelledby":"staff-links-heading",children:[r.jsxs("div",{className:"staff-links-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"form-label",id:"staff-links-heading",children:"Links"}),r.jsx("small",{children:"Add up to 10 links. They appear on your profile, not the team overview card."})]}),r.jsxs("span",{className:"staff-links-count",children:[g.length,"/10"]})]}),r.jsx("div",{className:"staff-link-list",children:g.map((Y,O)=>r.jsxs("div",{className:"staff-link-row",children:[r.jsxs("label",{className:"form-field staff-link-type",children:[r.jsxs("span",{className:"sr-only",children:["Link ",O+1," type"]}),r.jsxs("select",{value:Y.type,onChange:q=>ve(O,"type",q.target.value),children:[r.jsx("option",{value:"",children:"Choose link type…"}),DS.map(([q,K])=>r.jsx("option",{value:q,children:K},q))]})]}),r.jsxs("label",{className:"form-field staff-link-url",children:[r.jsxs("span",{className:"sr-only",children:["Link ",O+1," URL"]}),r.jsx("input",{type:"url",value:Y.url,onChange:q=>ve(O,"url",q.target.value),placeholder:"https://…"})]}),r.jsx("button",{type:"button",className:"staff-link-remove",onClick:()=>ie(O),"aria-label":`Remove link ${O+1}`,children:"Remove"})]},`profile-link-${O}`))}),r.jsx("button",{type:"button",className:"button button-muted staff-add-link",onClick:xe,disabled:g.length>=10,children:"＋ Add link"})]}),r.jsxs("label",{className:"form-field staff-bio-field",children:[r.jsx("span",{className:"form-label",children:"Extended introduction"}),r.jsx("textarea",{value:p.public_bio,onChange:Y=>le("public_bio",Y.target.value),maxLength:1200,placeholder:"Tell the community what you do…"}),r.jsxs("small",{children:[p.public_bio.length,"/1200 characters"]})]})]}),r.jsxs("label",{className:"setting-row staff-visibility",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Show me on the public Team page"}),r.jsx("small",{children:"Hide your listing without removing your staff access."})]}),r.jsx("input",{type:"checkbox",checked:p.public_visible,onChange:Y=>le("public_visible",Y.target.checked)}),r.jsx("i",{})]}),r.jsxs("div",{className:"staff-panel-footer",children:[r.jsx("span",{children:"Changes apply immediately to your public profile."}),r.jsx("button",{type:"button",className:"button button-primary",onClick:Pe,disabled:E,children:E?"Saving…":"Save public listing"})]})]}),r.jsxs("aside",{className:"staff-sidebar-card",children:[r.jsx("span",{className:"panel-kicker",children:"Profile rules"}),r.jsx("h3",{children:"Stay consistent with Discord"}),r.jsx("p",{children:"Your global display name and profile picture sync automatically, so updates made in Discord are reflected here without another form."}),r.jsxs("div",{className:"staff-rule",children:[r.jsx("span",{children:"Identity"}),r.jsx("strong",{children:"Discord synced"})]}),r.jsxs("div",{className:"staff-rule",children:[r.jsx("span",{children:"Editable"}),r.jsx("strong",{children:"Bio · banner · links · visibility"})]})]})]}),oe&&r.jsxs("section",{className:"staff-panel staff-global-panel",children:[r.jsxs("div",{className:"staff-panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Graphic direction"}),r.jsx("h2",{children:"Global Niko profile"}),r.jsx("p",{children:"Reserved for Graphic Designers, Head Admins, and owners. Paste publicly reachable image URLs."})]}),r.jsx("span",{className:"staff-step",children:"02"})]}),r.jsxs("div",{className:"staff-fields staff-fields-two",children:[r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Bot avatar URL"}),r.jsx("input",{value:w.avatar_url,onChange:Y=>j({...w,avatar_url:Y.target.value}),placeholder:"https://…"})]}),r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Bot banner URL"}),r.jsx("input",{value:w.banner_url,onChange:Y=>j({...w,banner_url:Y.target.value}),placeholder:"https://…"})]})]}),r.jsxs("div",{className:"staff-panel-footer",children:[r.jsx("span",{children:"Updates the bot-wide Discord profile."}),r.jsx("button",{type:"button",className:"button button-primary",onClick:Ie,disabled:I,children:I?"Updating…":"Update global profile"})]})]}),k&&r.jsx("div",{className:"notice",children:k}),N&&r.jsx("div",{className:"notice warning",children:N})]});return r.jsx(Mp,{user:t.user,guilds:h,selectedGuild:null,view:"overview",section:"overview",stats:c,staffRole:i.role,onHome:()=>he(Es()),onServers:()=>he(dc()),onGuildChange:()=>{},onSectionChange:()=>{},onRefresh:()=>window.location.reload(),refreshing:!1,children:Ae})}const np=[{question:"How do I invite Niko to my server?",answer:"Use the Add to Discord button in the site header to start the invite flow. You’ll need permission to add apps to the server."},{question:"Where can I find setup instructions and command help?",answer:"The documentation library includes setup guides, feature walkthroughs, and a searchable command reference."},{question:"Why isn’t a command or feature working?",answer:"Check that Niko is online and has the permissions needed in the channel. If the issue continues, share the command name and a short description in the support server."},{question:"How do I report a bug or request a feature?",answer:"Join the support server and post in the appropriate help or feedback channel. Include steps to reproduce bugs, and never share passwords or private tokens."},{question:"How can I request deletion of my data?",answer:"Contact the Niko team through the support server and include your Discord user ID so staff can locate the relevant data."}];function LS(){var c;const t=rs(),s=(c=t==null?void 0:t.support_server_url)==null?void 0:c.trim(),[i,o]=P.useState(0);return r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"support"}),r.jsxs("main",{className:"shell page-main support-page",children:[r.jsxs("section",{className:"support-hero",children:[r.jsx("div",{className:"eyebrow",children:"Niko support"}),r.jsxs("h1",{children:["Let’s get you ",r.jsx("em",{children:"unstuck."})]}),r.jsx("p",{children:"Browse quick answers, explore the guides, or talk with the community and Niko team."}),r.jsxs("div",{className:"support-actions",children:[r.jsxs("a",{className:"button button-primary",href:"/docs",children:["Browse documentation ",r.jsx(J,{name:"arrow"})]}),s&&r.jsxs("a",{className:"button button-muted",href:"/discord",children:["Join the support server ",r.jsx(J,{name:"arrow"})]})]})]}),r.jsxs("section",{className:"support-faq","aria-labelledby":"support-faq-title",children:[r.jsxs("div",{className:"support-section-heading",children:[r.jsxs("div",{children:[r.jsx("div",{className:"eyebrow",children:"Quick answers"}),r.jsx("h2",{id:"support-faq-title",children:"Frequently asked questions"})]}),r.jsxs("span",{className:"support-faq-count",children:[np.length," helpful guides"]})]}),r.jsx("div",{className:"support-faq-list",children:np.map((d,h)=>{const f=i===h,p=`support-faq-answer-${h}`;return r.jsxs("article",{className:`support-faq-item${f?" is-open":""}`,children:[r.jsx("h3",{children:r.jsxs("button",{type:"button","aria-expanded":f,"aria-controls":p,onClick:()=>o(f?null:h),children:[r.jsxs("span",{className:"support-faq-question",children:[r.jsx("span",{className:"support-faq-number",children:String(h+1).padStart(2,"0")}),d.question]}),r.jsx("span",{className:"support-faq-toggle",children:r.jsx(J,{name:f?"minus":"plus"})})]})}),r.jsx("div",{id:p,className:"support-faq-answer","aria-hidden":!f,children:r.jsx("div",{className:"support-faq-answer-inner",children:r.jsxs("p",{children:[d.answer,h===1&&r.jsxs(r.Fragment,{children:[" ",r.jsxs("a",{href:"/docs",tabIndex:f?0:-1,children:["Open the docs ",r.jsx("span",{"aria-hidden":"true",children:"↗"})]}),"."]})]})})})]},d.question)})})]}),r.jsxs("aside",{className:"support-contact-card",children:[r.jsx("div",{className:"support-contact-mark",children:r.jsx(J,{name:"message"})}),r.jsxs("div",{children:[r.jsx("div",{className:"eyebrow",children:"Need a hand?"}),r.jsx("h2",{children:"Find us in the community."}),r.jsx("p",{children:"Get help from other Niko users and the staff team in the official support server."})]}),s?r.jsxs("a",{className:"button button-primary",href:"/discord",children:["Open support server ",r.jsx(J,{name:"arrow"})]}):r.jsx("p",{className:"support-missing-link",role:"status",children:"The support server link isn’t available right now. Please check back later."})]})]}),r.jsx(St,{})]})}function IS(){var i;const t=rs(),s=(i=t==null?void 0:t.support_server_url)==null?void 0:i.trim();return P.useEffect(()=>{s&&window.location.replace(s)},[s]),t?s?r.jsxs("main",{className:"discord-redirect-state",children:[r.jsx("div",{className:"loading-ring"}),r.jsx("p",{children:"Taking you to the Niko support server…"}),r.jsx("a",{href:s,children:"Continue if you aren’t redirected"})]}):r.jsxs(r.Fragment,{children:[r.jsx(ze,{page:"support"}),r.jsxs("main",{className:"shell page-main discord-redirect-missing",children:[r.jsx("div",{className:"eyebrow",children:"Niko support"}),r.jsx("h1",{children:"We couldn’t find the support link."}),r.jsx("p",{children:"The official support server link isn’t configured right now. Please check back later."}),r.jsx("a",{className:"button button-primary",href:"/support",children:"Visit support"})]}),r.jsx(St,{})]}):r.jsxs("main",{className:"discord-redirect-state",children:[r.jsx("div",{className:"loading-ring"}),r.jsx("p",{children:"Checking the Niko support link…"})]})}function VS(){const[t,s]=P.useState(Cm);if(P.useEffect(()=>{const i=()=>s(Cm());return window.addEventListener("popstate",i),()=>window.removeEventListener("popstate",i)},[]),t==="commands")return r.jsx(dw,{});if(t==="docs-detail"){const i=window.location.pathname.split("/"),o=i[i.length-1];return r.jsx(q1,{slug:o})}if(t==="docs")return r.jsx(X1,{});if(t==="staff")return r.jsx(RS,{});if(t==="dashboard")return r.jsx(z1,{});if(t==="team")return r.jsx(AS,{});if(t==="team-member")return r.jsx(_S,{id:window.location.pathname.split("/").filter(Boolean)[1]||""});if(t==="support")return r.jsx(LS,{});if(t==="discord")return r.jsx(IS,{});if(t==="privacy")return r.jsx(oc,{type:"privacy"});if(t==="terms")return r.jsx(oc,{type:"terms"});if(t==="community")return r.jsx(oc,{type:"community"});if(t==="donate")return r.jsx(J1,{});if(t==="transcript"){const o=window.location.pathname.split("/").filter(Boolean)[1]||"";return r.jsx(hS,{transcriptId:o})}if(t==="changelog")return r.jsx(pS,{});if(t==="changelog-detail"){const i=window.location.pathname.split("/"),o=i[i.length-1];return r.jsx(gS,{slug:o})}return r.jsx(Y1,{})}Tx.createRoot(document.getElementById("root")).render(r.jsx(P.StrictMode,{children:r.jsx(VS,{})}));
