var xx=Object.defineProperty;var bx=(t,s,r)=>s in t?xx(t,s,{enumerable:!0,configurable:!0,writable:!0,value:r}):t[s]=r;var fm=(t,s,r)=>bx(t,typeof s!="symbol"?s+"":s,r);(function(){const s=document.createElement("link").relList;if(s&&s.supports&&s.supports("modulepreload"))return;for(const c of document.querySelectorAll('link[rel="modulepreload"]'))o(c);new MutationObserver(c=>{for(const d of c)if(d.type==="childList")for(const h of d.addedNodes)h.tagName==="LINK"&&h.rel==="modulepreload"&&o(h)}).observe(document,{childList:!0,subtree:!0});function r(c){const d={};return c.integrity&&(d.integrity=c.integrity),c.referrerPolicy&&(d.referrerPolicy=c.referrerPolicy),c.crossOrigin==="use-credentials"?d.credentials="include":c.crossOrigin==="anonymous"?d.credentials="omit":d.credentials="same-origin",d}function o(c){if(c.ep)return;c.ep=!0;const d=r(c);fetch(c.href,d)}})();var Il={exports:{}},Ni={},Vl={exports:{}},he={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var gm;function wx(){if(gm)return he;gm=1;var t=Symbol.for("react.element"),s=Symbol.for("react.portal"),r=Symbol.for("react.fragment"),o=Symbol.for("react.strict_mode"),c=Symbol.for("react.profiler"),d=Symbol.for("react.provider"),h=Symbol.for("react.context"),p=Symbol.for("react.forward_ref"),f=Symbol.for("react.suspense"),v=Symbol.for("react.memo"),g=Symbol.for("react.lazy"),x=Symbol.iterator;function b(P){return P===null||typeof P!="object"?null:(P=x&&P[x]||P["@@iterator"],typeof P=="function"?P:null)}var j={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},k=Object.assign,S={};function N(P,U,de){this.props=P,this.context=U,this.refs=S,this.updater=de||j}N.prototype.isReactComponent={},N.prototype.setState=function(P,U){if(typeof P!="object"&&typeof P!="function"&&P!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,P,U,"setState")},N.prototype.forceUpdate=function(P){this.updater.enqueueForceUpdate(this,P,"forceUpdate")};function O(){}O.prototype=N.prototype;function M(P,U,de){this.props=P,this.context=U,this.refs=S,this.updater=de||j}var L=M.prototype=new O;L.constructor=M,k(L,N.prototype),L.isPureReactComponent=!0;var I=Array.isArray,D=Object.prototype.hasOwnProperty,B={current:null},V={key:!0,ref:!0,__self:!0,__source:!0};function z(P,U,de){var me,ge={},ye=null,Ne=null;if(U!=null)for(me in U.ref!==void 0&&(Ne=U.ref),U.key!==void 0&&(ye=""+U.key),U)D.call(U,me)&&!V.hasOwnProperty(me)&&(ge[me]=U[me]);var be=arguments.length-2;if(be===1)ge.children=de;else if(1<be){for(var Me=Array(be),yt=0;yt<be;yt++)Me[yt]=arguments[yt+2];ge.children=Me}if(P&&P.defaultProps)for(me in be=P.defaultProps,be)ge[me]===void 0&&(ge[me]=be[me]);return{$$typeof:t,type:P,key:ye,ref:Ne,props:ge,_owner:B.current}}function re(P,U){return{$$typeof:t,type:P.type,key:U,ref:P.ref,props:P.props,_owner:P._owner}}function Y(P){return typeof P=="object"&&P!==null&&P.$$typeof===t}function ce(P){var U={"=":"=0",":":"=2"};return"$"+P.replace(/[=:]/g,function(de){return U[de]})}var ue=/\/+/g;function ie(P,U){return typeof P=="object"&&P!==null&&P.key!=null?ce(""+P.key):U.toString(36)}function Se(P,U,de,me,ge){var ye=typeof P;(ye==="undefined"||ye==="boolean")&&(P=null);var Ne=!1;if(P===null)Ne=!0;else switch(ye){case"string":case"number":Ne=!0;break;case"object":switch(P.$$typeof){case t:case s:Ne=!0}}if(Ne)return Ne=P,ge=ge(Ne),P=me===""?"."+ie(Ne,0):me,I(ge)?(de="",P!=null&&(de=P.replace(ue,"$&/")+"/"),Se(ge,U,de,"",function(yt){return yt})):ge!=null&&(Y(ge)&&(ge=re(ge,de+(!ge.key||Ne&&Ne.key===ge.key?"":(""+ge.key).replace(ue,"$&/")+"/")+P)),U.push(ge)),1;if(Ne=0,me=me===""?".":me+":",I(P))for(var be=0;be<P.length;be++){ye=P[be];var Me=me+ie(ye,be);Ne+=Se(ye,U,de,Me,ge)}else if(Me=b(P),typeof Me=="function")for(P=Me.call(P),be=0;!(ye=P.next()).done;)ye=ye.value,Me=me+ie(ye,be++),Ne+=Se(ye,U,de,Me,ge);else if(ye==="object")throw U=String(P),Error("Objects are not valid as a React child (found: "+(U==="[object Object]"?"object with keys {"+Object.keys(P).join(", ")+"}":U)+"). If you meant to render a collection of children, use an array instead.");return Ne}function De(P,U,de){if(P==null)return P;var me=[],ge=0;return Se(P,me,"","",function(ye){return U.call(de,ye,ge++)}),me}function Pe(P){if(P._status===-1){var U=P._result;U=U(),U.then(function(de){(P._status===0||P._status===-1)&&(P._status=1,P._result=de)},function(de){(P._status===0||P._status===-1)&&(P._status=2,P._result=de)}),P._status===-1&&(P._status=0,P._result=U)}if(P._status===1)return P._result.default;throw P._result}var Q={current:null},E={transition:null},H={ReactCurrentDispatcher:Q,ReactCurrentBatchConfig:E,ReactCurrentOwner:B};function W(){throw Error("act(...) is not supported in production builds of React.")}return he.Children={map:De,forEach:function(P,U,de){De(P,function(){U.apply(this,arguments)},de)},count:function(P){var U=0;return De(P,function(){U++}),U},toArray:function(P){return De(P,function(U){return U})||[]},only:function(P){if(!Y(P))throw Error("React.Children.only expected to receive a single React element child.");return P}},he.Component=N,he.Fragment=r,he.Profiler=c,he.PureComponent=M,he.StrictMode=o,he.Suspense=f,he.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=H,he.act=W,he.cloneElement=function(P,U,de){if(P==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+P+".");var me=k({},P.props),ge=P.key,ye=P.ref,Ne=P._owner;if(U!=null){if(U.ref!==void 0&&(ye=U.ref,Ne=B.current),U.key!==void 0&&(ge=""+U.key),P.type&&P.type.defaultProps)var be=P.type.defaultProps;for(Me in U)D.call(U,Me)&&!V.hasOwnProperty(Me)&&(me[Me]=U[Me]===void 0&&be!==void 0?be[Me]:U[Me])}var Me=arguments.length-2;if(Me===1)me.children=de;else if(1<Me){be=Array(Me);for(var yt=0;yt<Me;yt++)be[yt]=arguments[yt+2];me.children=be}return{$$typeof:t,type:P.type,key:ge,ref:ye,props:me,_owner:Ne}},he.createContext=function(P){return P={$$typeof:h,_currentValue:P,_currentValue2:P,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},P.Provider={$$typeof:d,_context:P},P.Consumer=P},he.createElement=z,he.createFactory=function(P){var U=z.bind(null,P);return U.type=P,U},he.createRef=function(){return{current:null}},he.forwardRef=function(P){return{$$typeof:p,render:P}},he.isValidElement=Y,he.lazy=function(P){return{$$typeof:g,_payload:{_status:-1,_result:P},_init:Pe}},he.memo=function(P,U){return{$$typeof:v,type:P,compare:U===void 0?null:U}},he.startTransition=function(P){var U=E.transition;E.transition={};try{P()}finally{E.transition=U}},he.unstable_act=W,he.useCallback=function(P,U){return Q.current.useCallback(P,U)},he.useContext=function(P){return Q.current.useContext(P)},he.useDebugValue=function(){},he.useDeferredValue=function(P){return Q.current.useDeferredValue(P)},he.useEffect=function(P,U){return Q.current.useEffect(P,U)},he.useId=function(){return Q.current.useId()},he.useImperativeHandle=function(P,U,de){return Q.current.useImperativeHandle(P,U,de)},he.useInsertionEffect=function(P,U){return Q.current.useInsertionEffect(P,U)},he.useLayoutEffect=function(P,U){return Q.current.useLayoutEffect(P,U)},he.useMemo=function(P,U){return Q.current.useMemo(P,U)},he.useReducer=function(P,U,de){return Q.current.useReducer(P,U,de)},he.useRef=function(P){return Q.current.useRef(P)},he.useState=function(P){return Q.current.useState(P)},he.useSyncExternalStore=function(P,U,de){return Q.current.useSyncExternalStore(P,U,de)},he.useTransition=function(){return Q.current.useTransition()},he.version="18.3.1",he}var ym;function Wc(){return ym||(ym=1,Vl.exports=wx()),Vl.exports}/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var vm;function kx(){if(vm)return Ni;vm=1;var t=Wc(),s=Symbol.for("react.element"),r=Symbol.for("react.fragment"),o=Object.prototype.hasOwnProperty,c=t.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,d={key:!0,ref:!0,__self:!0,__source:!0};function h(p,f,v){var g,x={},b=null,j=null;v!==void 0&&(b=""+v),f.key!==void 0&&(b=""+f.key),f.ref!==void 0&&(j=f.ref);for(g in f)o.call(f,g)&&!d.hasOwnProperty(g)&&(x[g]=f[g]);if(p&&p.defaultProps)for(g in f=p.defaultProps,f)x[g]===void 0&&(x[g]=f[g]);return{$$typeof:s,type:p,key:b,ref:j,props:x,_owner:c.current}}return Ni.Fragment=r,Ni.jsx=h,Ni.jsxs=h,Ni}var xm;function jx(){return xm||(xm=1,Il.exports=kx()),Il.exports}var i=jx(),T=Wc(),Yr={},Fl={exports:{}},ft={},Bl={exports:{}},Ol={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var bm;function Sx(){return bm||(bm=1,(function(t){function s(E,H){var W=E.length;E.push(H);e:for(;0<W;){var P=W-1>>>1,U=E[P];if(0<c(U,H))E[P]=H,E[W]=U,W=P;else break e}}function r(E){return E.length===0?null:E[0]}function o(E){if(E.length===0)return null;var H=E[0],W=E.pop();if(W!==H){E[0]=W;e:for(var P=0,U=E.length,de=U>>>1;P<de;){var me=2*(P+1)-1,ge=E[me],ye=me+1,Ne=E[ye];if(0>c(ge,W))ye<U&&0>c(Ne,ge)?(E[P]=Ne,E[ye]=W,P=ye):(E[P]=ge,E[me]=W,P=me);else if(ye<U&&0>c(Ne,W))E[P]=Ne,E[ye]=W,P=ye;else break e}}return H}function c(E,H){var W=E.sortIndex-H.sortIndex;return W!==0?W:E.id-H.id}if(typeof performance=="object"&&typeof performance.now=="function"){var d=performance;t.unstable_now=function(){return d.now()}}else{var h=Date,p=h.now();t.unstable_now=function(){return h.now()-p}}var f=[],v=[],g=1,x=null,b=3,j=!1,k=!1,S=!1,N=typeof setTimeout=="function"?setTimeout:null,O=typeof clearTimeout=="function"?clearTimeout:null,M=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function L(E){for(var H=r(v);H!==null;){if(H.callback===null)o(v);else if(H.startTime<=E)o(v),H.sortIndex=H.expirationTime,s(f,H);else break;H=r(v)}}function I(E){if(S=!1,L(E),!k)if(r(f)!==null)k=!0,Pe(D);else{var H=r(v);H!==null&&Q(I,H.startTime-E)}}function D(E,H){k=!1,S&&(S=!1,O(z),z=-1),j=!0;var W=b;try{for(L(H),x=r(f);x!==null&&(!(x.expirationTime>H)||E&&!ce());){var P=x.callback;if(typeof P=="function"){x.callback=null,b=x.priorityLevel;var U=P(x.expirationTime<=H);H=t.unstable_now(),typeof U=="function"?x.callback=U:x===r(f)&&o(f),L(H)}else o(f);x=r(f)}if(x!==null)var de=!0;else{var me=r(v);me!==null&&Q(I,me.startTime-H),de=!1}return de}finally{x=null,b=W,j=!1}}var B=!1,V=null,z=-1,re=5,Y=-1;function ce(){return!(t.unstable_now()-Y<re)}function ue(){if(V!==null){var E=t.unstable_now();Y=E;var H=!0;try{H=V(!0,E)}finally{H?ie():(B=!1,V=null)}}else B=!1}var ie;if(typeof M=="function")ie=function(){M(ue)};else if(typeof MessageChannel<"u"){var Se=new MessageChannel,De=Se.port2;Se.port1.onmessage=ue,ie=function(){De.postMessage(null)}}else ie=function(){N(ue,0)};function Pe(E){V=E,B||(B=!0,ie())}function Q(E,H){z=N(function(){E(t.unstable_now())},H)}t.unstable_IdlePriority=5,t.unstable_ImmediatePriority=1,t.unstable_LowPriority=4,t.unstable_NormalPriority=3,t.unstable_Profiling=null,t.unstable_UserBlockingPriority=2,t.unstable_cancelCallback=function(E){E.callback=null},t.unstable_continueExecution=function(){k||j||(k=!0,Pe(D))},t.unstable_forceFrameRate=function(E){0>E||125<E?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):re=0<E?Math.floor(1e3/E):5},t.unstable_getCurrentPriorityLevel=function(){return b},t.unstable_getFirstCallbackNode=function(){return r(f)},t.unstable_next=function(E){switch(b){case 1:case 2:case 3:var H=3;break;default:H=b}var W=b;b=H;try{return E()}finally{b=W}},t.unstable_pauseExecution=function(){},t.unstable_requestPaint=function(){},t.unstable_runWithPriority=function(E,H){switch(E){case 1:case 2:case 3:case 4:case 5:break;default:E=3}var W=b;b=E;try{return H()}finally{b=W}},t.unstable_scheduleCallback=function(E,H,W){var P=t.unstable_now();switch(typeof W=="object"&&W!==null?(W=W.delay,W=typeof W=="number"&&0<W?P+W:P):W=P,E){case 1:var U=-1;break;case 2:U=250;break;case 5:U=1073741823;break;case 4:U=1e4;break;default:U=5e3}return U=W+U,E={id:g++,callback:H,priorityLevel:E,startTime:W,expirationTime:U,sortIndex:-1},W>P?(E.sortIndex=W,s(v,E),r(f)===null&&E===r(v)&&(S?(O(z),z=-1):S=!0,Q(I,W-P))):(E.sortIndex=U,s(f,E),k||j||(k=!0,Pe(D))),E},t.unstable_shouldYield=ce,t.unstable_wrapCallback=function(E){var H=b;return function(){var W=b;b=H;try{return E.apply(this,arguments)}finally{b=W}}}})(Ol)),Ol}var wm;function Nx(){return wm||(wm=1,Bl.exports=Sx()),Bl.exports}/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var km;function Cx(){if(km)return ft;km=1;var t=Wc(),s=Nx();function r(e){for(var n="https://reactjs.org/docs/error-decoder.html?invariant="+e,a=1;a<arguments.length;a++)n+="&args[]="+encodeURIComponent(arguments[a]);return"Minified React error #"+e+"; visit "+n+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var o=new Set,c={};function d(e,n){h(e,n),h(e+"Capture",n)}function h(e,n){for(c[e]=n,e=0;e<n.length;e++)o.add(n[e])}var p=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),f=Object.prototype.hasOwnProperty,v=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,g={},x={};function b(e){return f.call(x,e)?!0:f.call(g,e)?!1:v.test(e)?x[e]=!0:(g[e]=!0,!1)}function j(e,n,a,l){if(a!==null&&a.type===0)return!1;switch(typeof n){case"function":case"symbol":return!0;case"boolean":return l?!1:a!==null?!a.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function k(e,n,a,l){if(n===null||typeof n>"u"||j(e,n,a,l))return!0;if(l)return!1;if(a!==null)switch(a.type){case 3:return!n;case 4:return n===!1;case 5:return isNaN(n);case 6:return isNaN(n)||1>n}return!1}function S(e,n,a,l,u,m,y){this.acceptsBooleans=n===2||n===3||n===4,this.attributeName=l,this.attributeNamespace=u,this.mustUseProperty=a,this.propertyName=e,this.type=n,this.sanitizeURL=m,this.removeEmptyString=y}var N={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){N[e]=new S(e,0,!1,e,null,!1,!1)}),[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var n=e[0];N[n]=new S(n,1,!1,e[1],null,!1,!1)}),["contentEditable","draggable","spellCheck","value"].forEach(function(e){N[e]=new S(e,2,!1,e.toLowerCase(),null,!1,!1)}),["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){N[e]=new S(e,2,!1,e,null,!1,!1)}),"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){N[e]=new S(e,3,!1,e.toLowerCase(),null,!1,!1)}),["checked","multiple","muted","selected"].forEach(function(e){N[e]=new S(e,3,!0,e,null,!1,!1)}),["capture","download"].forEach(function(e){N[e]=new S(e,4,!1,e,null,!1,!1)}),["cols","rows","size","span"].forEach(function(e){N[e]=new S(e,6,!1,e,null,!1,!1)}),["rowSpan","start"].forEach(function(e){N[e]=new S(e,5,!1,e.toLowerCase(),null,!1,!1)});var O=/[\-:]([a-z])/g;function M(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var n=e.replace(O,M);N[n]=new S(n,1,!1,e,null,!1,!1)}),"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var n=e.replace(O,M);N[n]=new S(n,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)}),["xml:base","xml:lang","xml:space"].forEach(function(e){var n=e.replace(O,M);N[n]=new S(n,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)}),["tabIndex","crossOrigin"].forEach(function(e){N[e]=new S(e,1,!1,e.toLowerCase(),null,!1,!1)}),N.xlinkHref=new S("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1),["src","href","action","formAction"].forEach(function(e){N[e]=new S(e,1,!1,e.toLowerCase(),null,!0,!0)});function L(e,n,a,l){var u=N.hasOwnProperty(n)?N[n]:null;(u!==null?u.type!==0:l||!(2<n.length)||n[0]!=="o"&&n[0]!=="O"||n[1]!=="n"&&n[1]!=="N")&&(k(n,a,u,l)&&(a=null),l||u===null?b(n)&&(a===null?e.removeAttribute(n):e.setAttribute(n,""+a)):u.mustUseProperty?e[u.propertyName]=a===null?u.type===3?!1:"":a:(n=u.attributeName,l=u.attributeNamespace,a===null?e.removeAttribute(n):(u=u.type,a=u===3||u===4&&a===!0?"":""+a,l?e.setAttributeNS(l,n,a):e.setAttribute(n,a))))}var I=t.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,D=Symbol.for("react.element"),B=Symbol.for("react.portal"),V=Symbol.for("react.fragment"),z=Symbol.for("react.strict_mode"),re=Symbol.for("react.profiler"),Y=Symbol.for("react.provider"),ce=Symbol.for("react.context"),ue=Symbol.for("react.forward_ref"),ie=Symbol.for("react.suspense"),Se=Symbol.for("react.suspense_list"),De=Symbol.for("react.memo"),Pe=Symbol.for("react.lazy"),Q=Symbol.for("react.offscreen"),E=Symbol.iterator;function H(e){return e===null||typeof e!="object"?null:(e=E&&e[E]||e["@@iterator"],typeof e=="function"?e:null)}var W=Object.assign,P;function U(e){if(P===void 0)try{throw Error()}catch(a){var n=a.stack.trim().match(/\n( *(at )?)/);P=n&&n[1]||""}return`
`+P+e}var de=!1;function me(e,n){if(!e||de)return"";de=!0;var a=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(n)if(n=function(){throw Error()},Object.defineProperty(n.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(n,[])}catch(F){var l=F}Reflect.construct(e,[],n)}else{try{n.call()}catch(F){l=F}e.call(n.prototype)}else{try{throw Error()}catch(F){l=F}e()}}catch(F){if(F&&l&&typeof F.stack=="string"){for(var u=F.stack.split(`
`),m=l.stack.split(`
`),y=u.length-1,w=m.length-1;1<=y&&0<=w&&u[y]!==m[w];)w--;for(;1<=y&&0<=w;y--,w--)if(u[y]!==m[w]){if(y!==1||w!==1)do if(y--,w--,0>w||u[y]!==m[w]){var C=`
`+u[y].replace(" at new "," at ");return e.displayName&&C.includes("<anonymous>")&&(C=C.replace("<anonymous>",e.displayName)),C}while(1<=y&&0<=w);break}}}finally{de=!1,Error.prepareStackTrace=a}return(e=e?e.displayName||e.name:"")?U(e):""}function ge(e){switch(e.tag){case 5:return U(e.type);case 16:return U("Lazy");case 13:return U("Suspense");case 19:return U("SuspenseList");case 0:case 2:case 15:return e=me(e.type,!1),e;case 11:return e=me(e.type.render,!1),e;case 1:return e=me(e.type,!0),e;default:return""}}function ye(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case V:return"Fragment";case B:return"Portal";case re:return"Profiler";case z:return"StrictMode";case ie:return"Suspense";case Se:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case ce:return(e.displayName||"Context")+".Consumer";case Y:return(e._context.displayName||"Context")+".Provider";case ue:var n=e.render;return e=e.displayName,e||(e=n.displayName||n.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case De:return n=e.displayName||null,n!==null?n:ye(e.type)||"Memo";case Pe:n=e._payload,e=e._init;try{return ye(e(n))}catch{}}return null}function Ne(e){var n=e.type;switch(e.tag){case 24:return"Cache";case 9:return(n.displayName||"Context")+".Consumer";case 10:return(n._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=n.render,e=e.displayName||e.name||"",n.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return n;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return ye(n);case 8:return n===z?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof n=="function")return n.displayName||n.name||null;if(typeof n=="string")return n}return null}function be(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function Me(e){var n=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(n==="checkbox"||n==="radio")}function yt(e){var n=Me(e)?"checked":"value",a=Object.getOwnPropertyDescriptor(e.constructor.prototype,n),l=""+e[n];if(!e.hasOwnProperty(n)&&typeof a<"u"&&typeof a.get=="function"&&typeof a.set=="function"){var u=a.get,m=a.set;return Object.defineProperty(e,n,{configurable:!0,get:function(){return u.call(this)},set:function(y){l=""+y,m.call(this,y)}}),Object.defineProperty(e,n,{enumerable:a.enumerable}),{getValue:function(){return l},setValue:function(y){l=""+y},stopTracking:function(){e._valueTracker=null,delete e[n]}}}}function Oi(e){e._valueTracker||(e._valueTracker=yt(e))}function wu(e){if(!e)return!1;var n=e._valueTracker;if(!n)return!0;var a=n.getValue(),l="";return e&&(l=Me(e)?e.checked?"true":"false":e.value),e=l,e!==a?(n.setValue(e),!0):!1}function zi(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function Ua(e,n){var a=n.checked;return W({},n,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:a??e._wrapperState.initialChecked})}function ku(e,n){var a=n.defaultValue==null?"":n.defaultValue,l=n.checked!=null?n.checked:n.defaultChecked;a=be(n.value!=null?n.value:a),e._wrapperState={initialChecked:l,initialValue:a,controlled:n.type==="checkbox"||n.type==="radio"?n.checked!=null:n.value!=null}}function ju(e,n){n=n.checked,n!=null&&L(e,"checked",n,!1)}function Wa(e,n){ju(e,n);var a=be(n.value),l=n.type;if(a!=null)l==="number"?(a===0&&e.value===""||e.value!=a)&&(e.value=""+a):e.value!==""+a&&(e.value=""+a);else if(l==="submit"||l==="reset"){e.removeAttribute("value");return}n.hasOwnProperty("value")?$a(e,n.type,a):n.hasOwnProperty("defaultValue")&&$a(e,n.type,be(n.defaultValue)),n.checked==null&&n.defaultChecked!=null&&(e.defaultChecked=!!n.defaultChecked)}function Su(e,n,a){if(n.hasOwnProperty("value")||n.hasOwnProperty("defaultValue")){var l=n.type;if(!(l!=="submit"&&l!=="reset"||n.value!==void 0&&n.value!==null))return;n=""+e._wrapperState.initialValue,a||n===e.value||(e.value=n),e.defaultValue=n}a=e.name,a!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,a!==""&&(e.name=a)}function $a(e,n,a){(n!=="number"||zi(e.ownerDocument)!==e)&&(a==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+a&&(e.defaultValue=""+a))}var Os=Array.isArray;function rs(e,n,a,l){if(e=e.options,n){n={};for(var u=0;u<a.length;u++)n["$"+a[u]]=!0;for(a=0;a<e.length;a++)u=n.hasOwnProperty("$"+e[a].value),e[a].selected!==u&&(e[a].selected=u),u&&l&&(e[a].defaultSelected=!0)}else{for(a=""+be(a),n=null,u=0;u<e.length;u++){if(e[u].value===a){e[u].selected=!0,l&&(e[u].defaultSelected=!0);return}n!==null||e[u].disabled||(n=e[u])}n!==null&&(n.selected=!0)}}function Ha(e,n){if(n.dangerouslySetInnerHTML!=null)throw Error(r(91));return W({},n,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function Nu(e,n){var a=n.value;if(a==null){if(a=n.children,n=n.defaultValue,a!=null){if(n!=null)throw Error(r(92));if(Os(a)){if(1<a.length)throw Error(r(93));a=a[0]}n=a}n==null&&(n=""),a=n}e._wrapperState={initialValue:be(a)}}function Cu(e,n){var a=be(n.value),l=be(n.defaultValue);a!=null&&(a=""+a,a!==e.value&&(e.value=a),n.defaultValue==null&&e.defaultValue!==a&&(e.defaultValue=a)),l!=null&&(e.defaultValue=""+l)}function Tu(e){var n=e.textContent;n===e._wrapperState.initialValue&&n!==""&&n!==null&&(e.value=n)}function Pu(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function Ga(e,n){return e==null||e==="http://www.w3.org/1999/xhtml"?Pu(n):e==="http://www.w3.org/2000/svg"&&n==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var Ui,Au=(function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(n,a,l,u){MSApp.execUnsafeLocalFunction(function(){return e(n,a,l,u)})}:e})(function(e,n){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=n;else{for(Ui=Ui||document.createElement("div"),Ui.innerHTML="<svg>"+n.valueOf().toString()+"</svg>",n=Ui.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;n.firstChild;)e.appendChild(n.firstChild)}});function zs(e,n){if(n){var a=e.firstChild;if(a&&a===e.lastChild&&a.nodeType===3){a.nodeValue=n;return}}e.textContent=n}var Us={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},jy=["Webkit","ms","Moz","O"];Object.keys(Us).forEach(function(e){jy.forEach(function(n){n=n+e.charAt(0).toUpperCase()+e.substring(1),Us[n]=Us[e]})});function Eu(e,n,a){return n==null||typeof n=="boolean"||n===""?"":a||typeof n!="number"||n===0||Us.hasOwnProperty(e)&&Us[e]?(""+n).trim():n+"px"}function Mu(e,n){e=e.style;for(var a in n)if(n.hasOwnProperty(a)){var l=a.indexOf("--")===0,u=Eu(a,n[a],l);a==="float"&&(a="cssFloat"),l?e.setProperty(a,u):e[a]=u}}var Sy=W({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function Ka(e,n){if(n){if(Sy[e]&&(n.children!=null||n.dangerouslySetInnerHTML!=null))throw Error(r(137,e));if(n.dangerouslySetInnerHTML!=null){if(n.children!=null)throw Error(r(60));if(typeof n.dangerouslySetInnerHTML!="object"||!("__html"in n.dangerouslySetInnerHTML))throw Error(r(61))}if(n.style!=null&&typeof n.style!="object")throw Error(r(62))}}function qa(e,n){if(e.indexOf("-")===-1)return typeof n.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var Xa=null;function Ya(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var Qa=null,as=null,os=null;function _u(e){if(e=ui(e)){if(typeof Qa!="function")throw Error(r(280));var n=e.stateNode;n&&(n=dr(n),Qa(e.stateNode,e.type,n))}}function Du(e){as?os?os.push(e):os=[e]:as=e}function Ru(){if(as){var e=as,n=os;if(os=as=null,_u(e),n)for(e=0;e<n.length;e++)_u(n[e])}}function Lu(e,n){return e(n)}function Iu(){}var Ja=!1;function Vu(e,n,a){if(Ja)return e(n,a);Ja=!0;try{return Lu(e,n,a)}finally{Ja=!1,(as!==null||os!==null)&&(Iu(),Ru())}}function Ws(e,n){var a=e.stateNode;if(a===null)return null;var l=dr(a);if(l===null)return null;a=l[n];e:switch(n){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(l=!l.disabled)||(e=e.type,l=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!l;break e;default:e=!1}if(e)return null;if(a&&typeof a!="function")throw Error(r(231,n,typeof a));return a}var Za=!1;if(p)try{var $s={};Object.defineProperty($s,"passive",{get:function(){Za=!0}}),window.addEventListener("test",$s,$s),window.removeEventListener("test",$s,$s)}catch{Za=!1}function Ny(e,n,a,l,u,m,y,w,C){var F=Array.prototype.slice.call(arguments,3);try{n.apply(a,F)}catch(G){this.onError(G)}}var Hs=!1,Wi=null,$i=!1,eo=null,Cy={onError:function(e){Hs=!0,Wi=e}};function Ty(e,n,a,l,u,m,y,w,C){Hs=!1,Wi=null,Ny.apply(Cy,arguments)}function Py(e,n,a,l,u,m,y,w,C){if(Ty.apply(this,arguments),Hs){if(Hs){var F=Wi;Hs=!1,Wi=null}else throw Error(r(198));$i||($i=!0,eo=F)}}function Rn(e){var n=e,a=e;if(e.alternate)for(;n.return;)n=n.return;else{e=n;do n=e,(n.flags&4098)!==0&&(a=n.return),e=n.return;while(e)}return n.tag===3?a:null}function Fu(e){if(e.tag===13){var n=e.memoizedState;if(n===null&&(e=e.alternate,e!==null&&(n=e.memoizedState)),n!==null)return n.dehydrated}return null}function Bu(e){if(Rn(e)!==e)throw Error(r(188))}function Ay(e){var n=e.alternate;if(!n){if(n=Rn(e),n===null)throw Error(r(188));return n!==e?null:e}for(var a=e,l=n;;){var u=a.return;if(u===null)break;var m=u.alternate;if(m===null){if(l=u.return,l!==null){a=l;continue}break}if(u.child===m.child){for(m=u.child;m;){if(m===a)return Bu(u),e;if(m===l)return Bu(u),n;m=m.sibling}throw Error(r(188))}if(a.return!==l.return)a=u,l=m;else{for(var y=!1,w=u.child;w;){if(w===a){y=!0,a=u,l=m;break}if(w===l){y=!0,l=u,a=m;break}w=w.sibling}if(!y){for(w=m.child;w;){if(w===a){y=!0,a=m,l=u;break}if(w===l){y=!0,l=m,a=u;break}w=w.sibling}if(!y)throw Error(r(189))}}if(a.alternate!==l)throw Error(r(190))}if(a.tag!==3)throw Error(r(188));return a.stateNode.current===a?e:n}function Ou(e){return e=Ay(e),e!==null?zu(e):null}function zu(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var n=zu(e);if(n!==null)return n;e=e.sibling}return null}var Uu=s.unstable_scheduleCallback,Wu=s.unstable_cancelCallback,Ey=s.unstable_shouldYield,My=s.unstable_requestPaint,Fe=s.unstable_now,_y=s.unstable_getCurrentPriorityLevel,to=s.unstable_ImmediatePriority,$u=s.unstable_UserBlockingPriority,Hi=s.unstable_NormalPriority,Dy=s.unstable_LowPriority,Hu=s.unstable_IdlePriority,Gi=null,Wt=null;function Ry(e){if(Wt&&typeof Wt.onCommitFiberRoot=="function")try{Wt.onCommitFiberRoot(Gi,e,void 0,(e.current.flags&128)===128)}catch{}}var _t=Math.clz32?Math.clz32:Vy,Ly=Math.log,Iy=Math.LN2;function Vy(e){return e>>>=0,e===0?32:31-(Ly(e)/Iy|0)|0}var Ki=64,qi=4194304;function Gs(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function Xi(e,n){var a=e.pendingLanes;if(a===0)return 0;var l=0,u=e.suspendedLanes,m=e.pingedLanes,y=a&268435455;if(y!==0){var w=y&~u;w!==0?l=Gs(w):(m&=y,m!==0&&(l=Gs(m)))}else y=a&~u,y!==0?l=Gs(y):m!==0&&(l=Gs(m));if(l===0)return 0;if(n!==0&&n!==l&&(n&u)===0&&(u=l&-l,m=n&-n,u>=m||u===16&&(m&4194240)!==0))return n;if((l&4)!==0&&(l|=a&16),n=e.entangledLanes,n!==0)for(e=e.entanglements,n&=l;0<n;)a=31-_t(n),u=1<<a,l|=e[a],n&=~u;return l}function Fy(e,n){switch(e){case 1:case 2:case 4:return n+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return n+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function By(e,n){for(var a=e.suspendedLanes,l=e.pingedLanes,u=e.expirationTimes,m=e.pendingLanes;0<m;){var y=31-_t(m),w=1<<y,C=u[y];C===-1?((w&a)===0||(w&l)!==0)&&(u[y]=Fy(w,n)):C<=n&&(e.expiredLanes|=w),m&=~w}}function no(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function Gu(){var e=Ki;return Ki<<=1,(Ki&4194240)===0&&(Ki=64),e}function so(e){for(var n=[],a=0;31>a;a++)n.push(e);return n}function Ks(e,n,a){e.pendingLanes|=n,n!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,n=31-_t(n),e[n]=a}function Oy(e,n){var a=e.pendingLanes&~n;e.pendingLanes=n,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=n,e.mutableReadLanes&=n,e.entangledLanes&=n,n=e.entanglements;var l=e.eventTimes;for(e=e.expirationTimes;0<a;){var u=31-_t(a),m=1<<u;n[u]=0,l[u]=-1,e[u]=-1,a&=~m}}function io(e,n){var a=e.entangledLanes|=n;for(e=e.entanglements;a;){var l=31-_t(a),u=1<<l;u&n|e[l]&n&&(e[l]|=n),a&=~u}}var we=0;function Ku(e){return e&=-e,1<e?4<e?(e&268435455)!==0?16:536870912:4:1}var qu,ro,Xu,Yu,Qu,ao=!1,Yi=[],un=null,dn=null,hn=null,qs=new Map,Xs=new Map,mn=[],zy="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function Ju(e,n){switch(e){case"focusin":case"focusout":un=null;break;case"dragenter":case"dragleave":dn=null;break;case"mouseover":case"mouseout":hn=null;break;case"pointerover":case"pointerout":qs.delete(n.pointerId);break;case"gotpointercapture":case"lostpointercapture":Xs.delete(n.pointerId)}}function Ys(e,n,a,l,u,m){return e===null||e.nativeEvent!==m?(e={blockedOn:n,domEventName:a,eventSystemFlags:l,nativeEvent:m,targetContainers:[u]},n!==null&&(n=ui(n),n!==null&&ro(n)),e):(e.eventSystemFlags|=l,n=e.targetContainers,u!==null&&n.indexOf(u)===-1&&n.push(u),e)}function Uy(e,n,a,l,u){switch(n){case"focusin":return un=Ys(un,e,n,a,l,u),!0;case"dragenter":return dn=Ys(dn,e,n,a,l,u),!0;case"mouseover":return hn=Ys(hn,e,n,a,l,u),!0;case"pointerover":var m=u.pointerId;return qs.set(m,Ys(qs.get(m)||null,e,n,a,l,u)),!0;case"gotpointercapture":return m=u.pointerId,Xs.set(m,Ys(Xs.get(m)||null,e,n,a,l,u)),!0}return!1}function Zu(e){var n=Ln(e.target);if(n!==null){var a=Rn(n);if(a!==null){if(n=a.tag,n===13){if(n=Fu(a),n!==null){e.blockedOn=n,Qu(e.priority,function(){Xu(a)});return}}else if(n===3&&a.stateNode.current.memoizedState.isDehydrated){e.blockedOn=a.tag===3?a.stateNode.containerInfo:null;return}}}e.blockedOn=null}function Qi(e){if(e.blockedOn!==null)return!1;for(var n=e.targetContainers;0<n.length;){var a=lo(e.domEventName,e.eventSystemFlags,n[0],e.nativeEvent);if(a===null){a=e.nativeEvent;var l=new a.constructor(a.type,a);Xa=l,a.target.dispatchEvent(l),Xa=null}else return n=ui(a),n!==null&&ro(n),e.blockedOn=a,!1;n.shift()}return!0}function ed(e,n,a){Qi(e)&&a.delete(n)}function Wy(){ao=!1,un!==null&&Qi(un)&&(un=null),dn!==null&&Qi(dn)&&(dn=null),hn!==null&&Qi(hn)&&(hn=null),qs.forEach(ed),Xs.forEach(ed)}function Qs(e,n){e.blockedOn===n&&(e.blockedOn=null,ao||(ao=!0,s.unstable_scheduleCallback(s.unstable_NormalPriority,Wy)))}function Js(e){function n(u){return Qs(u,e)}if(0<Yi.length){Qs(Yi[0],e);for(var a=1;a<Yi.length;a++){var l=Yi[a];l.blockedOn===e&&(l.blockedOn=null)}}for(un!==null&&Qs(un,e),dn!==null&&Qs(dn,e),hn!==null&&Qs(hn,e),qs.forEach(n),Xs.forEach(n),a=0;a<mn.length;a++)l=mn[a],l.blockedOn===e&&(l.blockedOn=null);for(;0<mn.length&&(a=mn[0],a.blockedOn===null);)Zu(a),a.blockedOn===null&&mn.shift()}var ls=I.ReactCurrentBatchConfig,Ji=!0;function $y(e,n,a,l){var u=we,m=ls.transition;ls.transition=null;try{we=1,oo(e,n,a,l)}finally{we=u,ls.transition=m}}function Hy(e,n,a,l){var u=we,m=ls.transition;ls.transition=null;try{we=4,oo(e,n,a,l)}finally{we=u,ls.transition=m}}function oo(e,n,a,l){if(Ji){var u=lo(e,n,a,l);if(u===null)Co(e,n,l,Zi,a),Ju(e,l);else if(Uy(u,e,n,a,l))l.stopPropagation();else if(Ju(e,l),n&4&&-1<zy.indexOf(e)){for(;u!==null;){var m=ui(u);if(m!==null&&qu(m),m=lo(e,n,a,l),m===null&&Co(e,n,l,Zi,a),m===u)break;u=m}u!==null&&l.stopPropagation()}else Co(e,n,l,null,a)}}var Zi=null;function lo(e,n,a,l){if(Zi=null,e=Ya(l),e=Ln(e),e!==null)if(n=Rn(e),n===null)e=null;else if(a=n.tag,a===13){if(e=Fu(n),e!==null)return e;e=null}else if(a===3){if(n.stateNode.current.memoizedState.isDehydrated)return n.tag===3?n.stateNode.containerInfo:null;e=null}else n!==e&&(e=null);return Zi=e,null}function td(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(_y()){case to:return 1;case $u:return 4;case Hi:case Dy:return 16;case Hu:return 536870912;default:return 16}default:return 16}}var pn=null,co=null,er=null;function nd(){if(er)return er;var e,n=co,a=n.length,l,u="value"in pn?pn.value:pn.textContent,m=u.length;for(e=0;e<a&&n[e]===u[e];e++);var y=a-e;for(l=1;l<=y&&n[a-l]===u[m-l];l++);return er=u.slice(e,1<l?1-l:void 0)}function tr(e){var n=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&n===13&&(e=13)):e=n,e===10&&(e=13),32<=e||e===13?e:0}function nr(){return!0}function sd(){return!1}function vt(e){function n(a,l,u,m,y){this._reactName=a,this._targetInst=u,this.type=l,this.nativeEvent=m,this.target=y,this.currentTarget=null;for(var w in e)e.hasOwnProperty(w)&&(a=e[w],this[w]=a?a(m):m[w]);return this.isDefaultPrevented=(m.defaultPrevented!=null?m.defaultPrevented:m.returnValue===!1)?nr:sd,this.isPropagationStopped=sd,this}return W(n.prototype,{preventDefault:function(){this.defaultPrevented=!0;var a=this.nativeEvent;a&&(a.preventDefault?a.preventDefault():typeof a.returnValue!="unknown"&&(a.returnValue=!1),this.isDefaultPrevented=nr)},stopPropagation:function(){var a=this.nativeEvent;a&&(a.stopPropagation?a.stopPropagation():typeof a.cancelBubble!="unknown"&&(a.cancelBubble=!0),this.isPropagationStopped=nr)},persist:function(){},isPersistent:nr}),n}var cs={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},uo=vt(cs),Zs=W({},cs,{view:0,detail:0}),Gy=vt(Zs),ho,mo,ei,sr=W({},Zs,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:fo,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==ei&&(ei&&e.type==="mousemove"?(ho=e.screenX-ei.screenX,mo=e.screenY-ei.screenY):mo=ho=0,ei=e),ho)},movementY:function(e){return"movementY"in e?e.movementY:mo}}),id=vt(sr),Ky=W({},sr,{dataTransfer:0}),qy=vt(Ky),Xy=W({},Zs,{relatedTarget:0}),po=vt(Xy),Yy=W({},cs,{animationName:0,elapsedTime:0,pseudoElement:0}),Qy=vt(Yy),Jy=W({},cs,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),Zy=vt(Jy),ev=W({},cs,{data:0}),rd=vt(ev),tv={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},nv={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},sv={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function iv(e){var n=this.nativeEvent;return n.getModifierState?n.getModifierState(e):(e=sv[e])?!!n[e]:!1}function fo(){return iv}var rv=W({},Zs,{key:function(e){if(e.key){var n=tv[e.key]||e.key;if(n!=="Unidentified")return n}return e.type==="keypress"?(e=tr(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?nv[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:fo,charCode:function(e){return e.type==="keypress"?tr(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?tr(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),av=vt(rv),ov=W({},sr,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),ad=vt(ov),lv=W({},Zs,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:fo}),cv=vt(lv),uv=W({},cs,{propertyName:0,elapsedTime:0,pseudoElement:0}),dv=vt(uv),hv=W({},sr,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),mv=vt(hv),pv=[9,13,27,32],go=p&&"CompositionEvent"in window,ti=null;p&&"documentMode"in document&&(ti=document.documentMode);var fv=p&&"TextEvent"in window&&!ti,od=p&&(!go||ti&&8<ti&&11>=ti),ld=" ",cd=!1;function ud(e,n){switch(e){case"keyup":return pv.indexOf(n.keyCode)!==-1;case"keydown":return n.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function dd(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var us=!1;function gv(e,n){switch(e){case"compositionend":return dd(n);case"keypress":return n.which!==32?null:(cd=!0,ld);case"textInput":return e=n.data,e===ld&&cd?null:e;default:return null}}function yv(e,n){if(us)return e==="compositionend"||!go&&ud(e,n)?(e=nd(),er=co=pn=null,us=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(n.ctrlKey||n.altKey||n.metaKey)||n.ctrlKey&&n.altKey){if(n.char&&1<n.char.length)return n.char;if(n.which)return String.fromCharCode(n.which)}return null;case"compositionend":return od&&n.locale!=="ko"?null:n.data;default:return null}}var vv={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function hd(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n==="input"?!!vv[e.type]:n==="textarea"}function md(e,n,a,l){Du(l),n=lr(n,"onChange"),0<n.length&&(a=new uo("onChange","change",null,a,l),e.push({event:a,listeners:n}))}var ni=null,si=null;function xv(e){Md(e,0)}function ir(e){var n=fs(e);if(wu(n))return e}function bv(e,n){if(e==="change")return n}var pd=!1;if(p){var yo;if(p){var vo="oninput"in document;if(!vo){var fd=document.createElement("div");fd.setAttribute("oninput","return;"),vo=typeof fd.oninput=="function"}yo=vo}else yo=!1;pd=yo&&(!document.documentMode||9<document.documentMode)}function gd(){ni&&(ni.detachEvent("onpropertychange",yd),si=ni=null)}function yd(e){if(e.propertyName==="value"&&ir(si)){var n=[];md(n,si,e,Ya(e)),Vu(xv,n)}}function wv(e,n,a){e==="focusin"?(gd(),ni=n,si=a,ni.attachEvent("onpropertychange",yd)):e==="focusout"&&gd()}function kv(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return ir(si)}function jv(e,n){if(e==="click")return ir(n)}function Sv(e,n){if(e==="input"||e==="change")return ir(n)}function Nv(e,n){return e===n&&(e!==0||1/e===1/n)||e!==e&&n!==n}var Dt=typeof Object.is=="function"?Object.is:Nv;function ii(e,n){if(Dt(e,n))return!0;if(typeof e!="object"||e===null||typeof n!="object"||n===null)return!1;var a=Object.keys(e),l=Object.keys(n);if(a.length!==l.length)return!1;for(l=0;l<a.length;l++){var u=a[l];if(!f.call(n,u)||!Dt(e[u],n[u]))return!1}return!0}function vd(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function xd(e,n){var a=vd(e);e=0;for(var l;a;){if(a.nodeType===3){if(l=e+a.textContent.length,e<=n&&l>=n)return{node:a,offset:n-e};e=l}e:{for(;a;){if(a.nextSibling){a=a.nextSibling;break e}a=a.parentNode}a=void 0}a=vd(a)}}function bd(e,n){return e&&n?e===n?!0:e&&e.nodeType===3?!1:n&&n.nodeType===3?bd(e,n.parentNode):"contains"in e?e.contains(n):e.compareDocumentPosition?!!(e.compareDocumentPosition(n)&16):!1:!1}function wd(){for(var e=window,n=zi();n instanceof e.HTMLIFrameElement;){try{var a=typeof n.contentWindow.location.href=="string"}catch{a=!1}if(a)e=n.contentWindow;else break;n=zi(e.document)}return n}function xo(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n&&(n==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||n==="textarea"||e.contentEditable==="true")}function Cv(e){var n=wd(),a=e.focusedElem,l=e.selectionRange;if(n!==a&&a&&a.ownerDocument&&bd(a.ownerDocument.documentElement,a)){if(l!==null&&xo(a)){if(n=l.start,e=l.end,e===void 0&&(e=n),"selectionStart"in a)a.selectionStart=n,a.selectionEnd=Math.min(e,a.value.length);else if(e=(n=a.ownerDocument||document)&&n.defaultView||window,e.getSelection){e=e.getSelection();var u=a.textContent.length,m=Math.min(l.start,u);l=l.end===void 0?m:Math.min(l.end,u),!e.extend&&m>l&&(u=l,l=m,m=u),u=xd(a,m);var y=xd(a,l);u&&y&&(e.rangeCount!==1||e.anchorNode!==u.node||e.anchorOffset!==u.offset||e.focusNode!==y.node||e.focusOffset!==y.offset)&&(n=n.createRange(),n.setStart(u.node,u.offset),e.removeAllRanges(),m>l?(e.addRange(n),e.extend(y.node,y.offset)):(n.setEnd(y.node,y.offset),e.addRange(n)))}}for(n=[],e=a;e=e.parentNode;)e.nodeType===1&&n.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof a.focus=="function"&&a.focus(),a=0;a<n.length;a++)e=n[a],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var Tv=p&&"documentMode"in document&&11>=document.documentMode,ds=null,bo=null,ri=null,wo=!1;function kd(e,n,a){var l=a.window===a?a.document:a.nodeType===9?a:a.ownerDocument;wo||ds==null||ds!==zi(l)||(l=ds,"selectionStart"in l&&xo(l)?l={start:l.selectionStart,end:l.selectionEnd}:(l=(l.ownerDocument&&l.ownerDocument.defaultView||window).getSelection(),l={anchorNode:l.anchorNode,anchorOffset:l.anchorOffset,focusNode:l.focusNode,focusOffset:l.focusOffset}),ri&&ii(ri,l)||(ri=l,l=lr(bo,"onSelect"),0<l.length&&(n=new uo("onSelect","select",null,n,a),e.push({event:n,listeners:l}),n.target=ds)))}function rr(e,n){var a={};return a[e.toLowerCase()]=n.toLowerCase(),a["Webkit"+e]="webkit"+n,a["Moz"+e]="moz"+n,a}var hs={animationend:rr("Animation","AnimationEnd"),animationiteration:rr("Animation","AnimationIteration"),animationstart:rr("Animation","AnimationStart"),transitionend:rr("Transition","TransitionEnd")},ko={},jd={};p&&(jd=document.createElement("div").style,"AnimationEvent"in window||(delete hs.animationend.animation,delete hs.animationiteration.animation,delete hs.animationstart.animation),"TransitionEvent"in window||delete hs.transitionend.transition);function ar(e){if(ko[e])return ko[e];if(!hs[e])return e;var n=hs[e],a;for(a in n)if(n.hasOwnProperty(a)&&a in jd)return ko[e]=n[a];return e}var Sd=ar("animationend"),Nd=ar("animationiteration"),Cd=ar("animationstart"),Td=ar("transitionend"),Pd=new Map,Ad="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function fn(e,n){Pd.set(e,n),d(n,[e])}for(var jo=0;jo<Ad.length;jo++){var So=Ad[jo],Pv=So.toLowerCase(),Av=So[0].toUpperCase()+So.slice(1);fn(Pv,"on"+Av)}fn(Sd,"onAnimationEnd"),fn(Nd,"onAnimationIteration"),fn(Cd,"onAnimationStart"),fn("dblclick","onDoubleClick"),fn("focusin","onFocus"),fn("focusout","onBlur"),fn(Td,"onTransitionEnd"),h("onMouseEnter",["mouseout","mouseover"]),h("onMouseLeave",["mouseout","mouseover"]),h("onPointerEnter",["pointerout","pointerover"]),h("onPointerLeave",["pointerout","pointerover"]),d("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),d("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),d("onBeforeInput",["compositionend","keypress","textInput","paste"]),d("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),d("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),d("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var ai="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),Ev=new Set("cancel close invalid load scroll toggle".split(" ").concat(ai));function Ed(e,n,a){var l=e.type||"unknown-event";e.currentTarget=a,Py(l,n,void 0,e),e.currentTarget=null}function Md(e,n){n=(n&4)!==0;for(var a=0;a<e.length;a++){var l=e[a],u=l.event;l=l.listeners;e:{var m=void 0;if(n)for(var y=l.length-1;0<=y;y--){var w=l[y],C=w.instance,F=w.currentTarget;if(w=w.listener,C!==m&&u.isPropagationStopped())break e;Ed(u,w,F),m=C}else for(y=0;y<l.length;y++){if(w=l[y],C=w.instance,F=w.currentTarget,w=w.listener,C!==m&&u.isPropagationStopped())break e;Ed(u,w,F),m=C}}}if($i)throw e=eo,$i=!1,eo=null,e}function Ae(e,n){var a=n[_o];a===void 0&&(a=n[_o]=new Set);var l=e+"__bubble";a.has(l)||(_d(n,e,2,!1),a.add(l))}function No(e,n,a){var l=0;n&&(l|=4),_d(a,e,l,n)}var or="_reactListening"+Math.random().toString(36).slice(2);function oi(e){if(!e[or]){e[or]=!0,o.forEach(function(a){a!=="selectionchange"&&(Ev.has(a)||No(a,!1,e),No(a,!0,e))});var n=e.nodeType===9?e:e.ownerDocument;n===null||n[or]||(n[or]=!0,No("selectionchange",!1,n))}}function _d(e,n,a,l){switch(td(n)){case 1:var u=$y;break;case 4:u=Hy;break;default:u=oo}a=u.bind(null,n,a,e),u=void 0,!Za||n!=="touchstart"&&n!=="touchmove"&&n!=="wheel"||(u=!0),l?u!==void 0?e.addEventListener(n,a,{capture:!0,passive:u}):e.addEventListener(n,a,!0):u!==void 0?e.addEventListener(n,a,{passive:u}):e.addEventListener(n,a,!1)}function Co(e,n,a,l,u){var m=l;if((n&1)===0&&(n&2)===0&&l!==null)e:for(;;){if(l===null)return;var y=l.tag;if(y===3||y===4){var w=l.stateNode.containerInfo;if(w===u||w.nodeType===8&&w.parentNode===u)break;if(y===4)for(y=l.return;y!==null;){var C=y.tag;if((C===3||C===4)&&(C=y.stateNode.containerInfo,C===u||C.nodeType===8&&C.parentNode===u))return;y=y.return}for(;w!==null;){if(y=Ln(w),y===null)return;if(C=y.tag,C===5||C===6){l=m=y;continue e}w=w.parentNode}}l=l.return}Vu(function(){var F=m,G=Ya(a),K=[];e:{var $=Pd.get(e);if($!==void 0){var J=uo,ee=e;switch(e){case"keypress":if(tr(a)===0)break e;case"keydown":case"keyup":J=av;break;case"focusin":ee="focus",J=po;break;case"focusout":ee="blur",J=po;break;case"beforeblur":case"afterblur":J=po;break;case"click":if(a.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":J=id;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":J=qy;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":J=cv;break;case Sd:case Nd:case Cd:J=Qy;break;case Td:J=dv;break;case"scroll":J=Gy;break;case"wheel":J=mv;break;case"copy":case"cut":case"paste":J=Zy;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":J=ad}var ne=(n&4)!==0,Be=!ne&&e==="scroll",_=ne?$!==null?$+"Capture":null:$;ne=[];for(var A=F,R;A!==null;){R=A;var q=R.stateNode;if(R.tag===5&&q!==null&&(R=q,_!==null&&(q=Ws(A,_),q!=null&&ne.push(li(A,q,R)))),Be)break;A=A.return}0<ne.length&&($=new J($,ee,null,a,G),K.push({event:$,listeners:ne}))}}if((n&7)===0){e:{if($=e==="mouseover"||e==="pointerover",J=e==="mouseout"||e==="pointerout",$&&a!==Xa&&(ee=a.relatedTarget||a.fromElement)&&(Ln(ee)||ee[Jt]))break e;if((J||$)&&($=G.window===G?G:($=G.ownerDocument)?$.defaultView||$.parentWindow:window,J?(ee=a.relatedTarget||a.toElement,J=F,ee=ee?Ln(ee):null,ee!==null&&(Be=Rn(ee),ee!==Be||ee.tag!==5&&ee.tag!==6)&&(ee=null)):(J=null,ee=F),J!==ee)){if(ne=id,q="onMouseLeave",_="onMouseEnter",A="mouse",(e==="pointerout"||e==="pointerover")&&(ne=ad,q="onPointerLeave",_="onPointerEnter",A="pointer"),Be=J==null?$:fs(J),R=ee==null?$:fs(ee),$=new ne(q,A+"leave",J,a,G),$.target=Be,$.relatedTarget=R,q=null,Ln(G)===F&&(ne=new ne(_,A+"enter",ee,a,G),ne.target=R,ne.relatedTarget=Be,q=ne),Be=q,J&&ee)t:{for(ne=J,_=ee,A=0,R=ne;R;R=ms(R))A++;for(R=0,q=_;q;q=ms(q))R++;for(;0<A-R;)ne=ms(ne),A--;for(;0<R-A;)_=ms(_),R--;for(;A--;){if(ne===_||_!==null&&ne===_.alternate)break t;ne=ms(ne),_=ms(_)}ne=null}else ne=null;J!==null&&Dd(K,$,J,ne,!1),ee!==null&&Be!==null&&Dd(K,Be,ee,ne,!0)}}e:{if($=F?fs(F):window,J=$.nodeName&&$.nodeName.toLowerCase(),J==="select"||J==="input"&&$.type==="file")var se=bv;else if(hd($))if(pd)se=Sv;else{se=kv;var ae=wv}else(J=$.nodeName)&&J.toLowerCase()==="input"&&($.type==="checkbox"||$.type==="radio")&&(se=jv);if(se&&(se=se(e,F))){md(K,se,a,G);break e}ae&&ae(e,$,F),e==="focusout"&&(ae=$._wrapperState)&&ae.controlled&&$.type==="number"&&$a($,"number",$.value)}switch(ae=F?fs(F):window,e){case"focusin":(hd(ae)||ae.contentEditable==="true")&&(ds=ae,bo=F,ri=null);break;case"focusout":ri=bo=ds=null;break;case"mousedown":wo=!0;break;case"contextmenu":case"mouseup":case"dragend":wo=!1,kd(K,a,G);break;case"selectionchange":if(Tv)break;case"keydown":case"keyup":kd(K,a,G)}var oe;if(go)e:{switch(e){case"compositionstart":var le="onCompositionStart";break e;case"compositionend":le="onCompositionEnd";break e;case"compositionupdate":le="onCompositionUpdate";break e}le=void 0}else us?ud(e,a)&&(le="onCompositionEnd"):e==="keydown"&&a.keyCode===229&&(le="onCompositionStart");le&&(od&&a.locale!=="ko"&&(us||le!=="onCompositionStart"?le==="onCompositionEnd"&&us&&(oe=nd()):(pn=G,co="value"in pn?pn.value:pn.textContent,us=!0)),ae=lr(F,le),0<ae.length&&(le=new rd(le,e,null,a,G),K.push({event:le,listeners:ae}),oe?le.data=oe:(oe=dd(a),oe!==null&&(le.data=oe)))),(oe=fv?gv(e,a):yv(e,a))&&(F=lr(F,"onBeforeInput"),0<F.length&&(G=new rd("onBeforeInput","beforeinput",null,a,G),K.push({event:G,listeners:F}),G.data=oe))}Md(K,n)})}function li(e,n,a){return{instance:e,listener:n,currentTarget:a}}function lr(e,n){for(var a=n+"Capture",l=[];e!==null;){var u=e,m=u.stateNode;u.tag===5&&m!==null&&(u=m,m=Ws(e,a),m!=null&&l.unshift(li(e,m,u)),m=Ws(e,n),m!=null&&l.push(li(e,m,u))),e=e.return}return l}function ms(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function Dd(e,n,a,l,u){for(var m=n._reactName,y=[];a!==null&&a!==l;){var w=a,C=w.alternate,F=w.stateNode;if(C!==null&&C===l)break;w.tag===5&&F!==null&&(w=F,u?(C=Ws(a,m),C!=null&&y.unshift(li(a,C,w))):u||(C=Ws(a,m),C!=null&&y.push(li(a,C,w)))),a=a.return}y.length!==0&&e.push({event:n,listeners:y})}var Mv=/\r\n?/g,_v=/\u0000|\uFFFD/g;function Rd(e){return(typeof e=="string"?e:""+e).replace(Mv,`
`).replace(_v,"")}function cr(e,n,a){if(n=Rd(n),Rd(e)!==n&&a)throw Error(r(425))}function ur(){}var To=null,Po=null;function Ao(e,n){return e==="textarea"||e==="noscript"||typeof n.children=="string"||typeof n.children=="number"||typeof n.dangerouslySetInnerHTML=="object"&&n.dangerouslySetInnerHTML!==null&&n.dangerouslySetInnerHTML.__html!=null}var Eo=typeof setTimeout=="function"?setTimeout:void 0,Dv=typeof clearTimeout=="function"?clearTimeout:void 0,Ld=typeof Promise=="function"?Promise:void 0,Rv=typeof queueMicrotask=="function"?queueMicrotask:typeof Ld<"u"?function(e){return Ld.resolve(null).then(e).catch(Lv)}:Eo;function Lv(e){setTimeout(function(){throw e})}function Mo(e,n){var a=n,l=0;do{var u=a.nextSibling;if(e.removeChild(a),u&&u.nodeType===8)if(a=u.data,a==="/$"){if(l===0){e.removeChild(u),Js(n);return}l--}else a!=="$"&&a!=="$?"&&a!=="$!"||l++;a=u}while(a);Js(n)}function gn(e){for(;e!=null;e=e.nextSibling){var n=e.nodeType;if(n===1||n===3)break;if(n===8){if(n=e.data,n==="$"||n==="$!"||n==="$?")break;if(n==="/$")return null}}return e}function Id(e){e=e.previousSibling;for(var n=0;e;){if(e.nodeType===8){var a=e.data;if(a==="$"||a==="$!"||a==="$?"){if(n===0)return e;n--}else a==="/$"&&n++}e=e.previousSibling}return null}var ps=Math.random().toString(36).slice(2),$t="__reactFiber$"+ps,ci="__reactProps$"+ps,Jt="__reactContainer$"+ps,_o="__reactEvents$"+ps,Iv="__reactListeners$"+ps,Vv="__reactHandles$"+ps;function Ln(e){var n=e[$t];if(n)return n;for(var a=e.parentNode;a;){if(n=a[Jt]||a[$t]){if(a=n.alternate,n.child!==null||a!==null&&a.child!==null)for(e=Id(e);e!==null;){if(a=e[$t])return a;e=Id(e)}return n}e=a,a=e.parentNode}return null}function ui(e){return e=e[$t]||e[Jt],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function fs(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(r(33))}function dr(e){return e[ci]||null}var Do=[],gs=-1;function yn(e){return{current:e}}function Ee(e){0>gs||(e.current=Do[gs],Do[gs]=null,gs--)}function Ce(e,n){gs++,Do[gs]=e.current,e.current=n}var vn={},tt=yn(vn),ut=yn(!1),In=vn;function ys(e,n){var a=e.type.contextTypes;if(!a)return vn;var l=e.stateNode;if(l&&l.__reactInternalMemoizedUnmaskedChildContext===n)return l.__reactInternalMemoizedMaskedChildContext;var u={},m;for(m in a)u[m]=n[m];return l&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=n,e.__reactInternalMemoizedMaskedChildContext=u),u}function dt(e){return e=e.childContextTypes,e!=null}function hr(){Ee(ut),Ee(tt)}function Vd(e,n,a){if(tt.current!==vn)throw Error(r(168));Ce(tt,n),Ce(ut,a)}function Fd(e,n,a){var l=e.stateNode;if(n=n.childContextTypes,typeof l.getChildContext!="function")return a;l=l.getChildContext();for(var u in l)if(!(u in n))throw Error(r(108,Ne(e)||"Unknown",u));return W({},a,l)}function mr(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||vn,In=tt.current,Ce(tt,e),Ce(ut,ut.current),!0}function Bd(e,n,a){var l=e.stateNode;if(!l)throw Error(r(169));a?(e=Fd(e,n,In),l.__reactInternalMemoizedMergedChildContext=e,Ee(ut),Ee(tt),Ce(tt,e)):Ee(ut),Ce(ut,a)}var Zt=null,pr=!1,Ro=!1;function Od(e){Zt===null?Zt=[e]:Zt.push(e)}function Fv(e){pr=!0,Od(e)}function xn(){if(!Ro&&Zt!==null){Ro=!0;var e=0,n=we;try{var a=Zt;for(we=1;e<a.length;e++){var l=a[e];do l=l(!0);while(l!==null)}Zt=null,pr=!1}catch(u){throw Zt!==null&&(Zt=Zt.slice(e+1)),Uu(to,xn),u}finally{we=n,Ro=!1}}return null}var vs=[],xs=0,fr=null,gr=0,Nt=[],Ct=0,Vn=null,en=1,tn="";function Fn(e,n){vs[xs++]=gr,vs[xs++]=fr,fr=e,gr=n}function zd(e,n,a){Nt[Ct++]=en,Nt[Ct++]=tn,Nt[Ct++]=Vn,Vn=e;var l=en;e=tn;var u=32-_t(l)-1;l&=~(1<<u),a+=1;var m=32-_t(n)+u;if(30<m){var y=u-u%5;m=(l&(1<<y)-1).toString(32),l>>=y,u-=y,en=1<<32-_t(n)+u|a<<u|l,tn=m+e}else en=1<<m|a<<u|l,tn=e}function Lo(e){e.return!==null&&(Fn(e,1),zd(e,1,0))}function Io(e){for(;e===fr;)fr=vs[--xs],vs[xs]=null,gr=vs[--xs],vs[xs]=null;for(;e===Vn;)Vn=Nt[--Ct],Nt[Ct]=null,tn=Nt[--Ct],Nt[Ct]=null,en=Nt[--Ct],Nt[Ct]=null}var xt=null,bt=null,_e=!1,Rt=null;function Ud(e,n){var a=Et(5,null,null,0);a.elementType="DELETED",a.stateNode=n,a.return=e,n=e.deletions,n===null?(e.deletions=[a],e.flags|=16):n.push(a)}function Wd(e,n){switch(e.tag){case 5:var a=e.type;return n=n.nodeType!==1||a.toLowerCase()!==n.nodeName.toLowerCase()?null:n,n!==null?(e.stateNode=n,xt=e,bt=gn(n.firstChild),!0):!1;case 6:return n=e.pendingProps===""||n.nodeType!==3?null:n,n!==null?(e.stateNode=n,xt=e,bt=null,!0):!1;case 13:return n=n.nodeType!==8?null:n,n!==null?(a=Vn!==null?{id:en,overflow:tn}:null,e.memoizedState={dehydrated:n,treeContext:a,retryLane:1073741824},a=Et(18,null,null,0),a.stateNode=n,a.return=e,e.child=a,xt=e,bt=null,!0):!1;default:return!1}}function Vo(e){return(e.mode&1)!==0&&(e.flags&128)===0}function Fo(e){if(_e){var n=bt;if(n){var a=n;if(!Wd(e,n)){if(Vo(e))throw Error(r(418));n=gn(a.nextSibling);var l=xt;n&&Wd(e,n)?Ud(l,a):(e.flags=e.flags&-4097|2,_e=!1,xt=e)}}else{if(Vo(e))throw Error(r(418));e.flags=e.flags&-4097|2,_e=!1,xt=e}}}function $d(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;xt=e}function yr(e){if(e!==xt)return!1;if(!_e)return $d(e),_e=!0,!1;var n;if((n=e.tag!==3)&&!(n=e.tag!==5)&&(n=e.type,n=n!=="head"&&n!=="body"&&!Ao(e.type,e.memoizedProps)),n&&(n=bt)){if(Vo(e))throw Hd(),Error(r(418));for(;n;)Ud(e,n),n=gn(n.nextSibling)}if($d(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(r(317));e:{for(e=e.nextSibling,n=0;e;){if(e.nodeType===8){var a=e.data;if(a==="/$"){if(n===0){bt=gn(e.nextSibling);break e}n--}else a!=="$"&&a!=="$!"&&a!=="$?"||n++}e=e.nextSibling}bt=null}}else bt=xt?gn(e.stateNode.nextSibling):null;return!0}function Hd(){for(var e=bt;e;)e=gn(e.nextSibling)}function bs(){bt=xt=null,_e=!1}function Bo(e){Rt===null?Rt=[e]:Rt.push(e)}var Bv=I.ReactCurrentBatchConfig;function di(e,n,a){if(e=a.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(a._owner){if(a=a._owner,a){if(a.tag!==1)throw Error(r(309));var l=a.stateNode}if(!l)throw Error(r(147,e));var u=l,m=""+e;return n!==null&&n.ref!==null&&typeof n.ref=="function"&&n.ref._stringRef===m?n.ref:(n=function(y){var w=u.refs;y===null?delete w[m]:w[m]=y},n._stringRef=m,n)}if(typeof e!="string")throw Error(r(284));if(!a._owner)throw Error(r(290,e))}return e}function vr(e,n){throw e=Object.prototype.toString.call(n),Error(r(31,e==="[object Object]"?"object with keys {"+Object.keys(n).join(", ")+"}":e))}function Gd(e){var n=e._init;return n(e._payload)}function Kd(e){function n(_,A){if(e){var R=_.deletions;R===null?(_.deletions=[A],_.flags|=16):R.push(A)}}function a(_,A){if(!e)return null;for(;A!==null;)n(_,A),A=A.sibling;return null}function l(_,A){for(_=new Map;A!==null;)A.key!==null?_.set(A.key,A):_.set(A.index,A),A=A.sibling;return _}function u(_,A){return _=Tn(_,A),_.index=0,_.sibling=null,_}function m(_,A,R){return _.index=R,e?(R=_.alternate,R!==null?(R=R.index,R<A?(_.flags|=2,A):R):(_.flags|=2,A)):(_.flags|=1048576,A)}function y(_){return e&&_.alternate===null&&(_.flags|=2),_}function w(_,A,R,q){return A===null||A.tag!==6?(A=El(R,_.mode,q),A.return=_,A):(A=u(A,R),A.return=_,A)}function C(_,A,R,q){var se=R.type;return se===V?G(_,A,R.props.children,q,R.key):A!==null&&(A.elementType===se||typeof se=="object"&&se!==null&&se.$$typeof===Pe&&Gd(se)===A.type)?(q=u(A,R.props),q.ref=di(_,A,R),q.return=_,q):(q=Ur(R.type,R.key,R.props,null,_.mode,q),q.ref=di(_,A,R),q.return=_,q)}function F(_,A,R,q){return A===null||A.tag!==4||A.stateNode.containerInfo!==R.containerInfo||A.stateNode.implementation!==R.implementation?(A=Ml(R,_.mode,q),A.return=_,A):(A=u(A,R.children||[]),A.return=_,A)}function G(_,A,R,q,se){return A===null||A.tag!==7?(A=Gn(R,_.mode,q,se),A.return=_,A):(A=u(A,R),A.return=_,A)}function K(_,A,R){if(typeof A=="string"&&A!==""||typeof A=="number")return A=El(""+A,_.mode,R),A.return=_,A;if(typeof A=="object"&&A!==null){switch(A.$$typeof){case D:return R=Ur(A.type,A.key,A.props,null,_.mode,R),R.ref=di(_,null,A),R.return=_,R;case B:return A=Ml(A,_.mode,R),A.return=_,A;case Pe:var q=A._init;return K(_,q(A._payload),R)}if(Os(A)||H(A))return A=Gn(A,_.mode,R,null),A.return=_,A;vr(_,A)}return null}function $(_,A,R,q){var se=A!==null?A.key:null;if(typeof R=="string"&&R!==""||typeof R=="number")return se!==null?null:w(_,A,""+R,q);if(typeof R=="object"&&R!==null){switch(R.$$typeof){case D:return R.key===se?C(_,A,R,q):null;case B:return R.key===se?F(_,A,R,q):null;case Pe:return se=R._init,$(_,A,se(R._payload),q)}if(Os(R)||H(R))return se!==null?null:G(_,A,R,q,null);vr(_,R)}return null}function J(_,A,R,q,se){if(typeof q=="string"&&q!==""||typeof q=="number")return _=_.get(R)||null,w(A,_,""+q,se);if(typeof q=="object"&&q!==null){switch(q.$$typeof){case D:return _=_.get(q.key===null?R:q.key)||null,C(A,_,q,se);case B:return _=_.get(q.key===null?R:q.key)||null,F(A,_,q,se);case Pe:var ae=q._init;return J(_,A,R,ae(q._payload),se)}if(Os(q)||H(q))return _=_.get(R)||null,G(A,_,q,se,null);vr(A,q)}return null}function ee(_,A,R,q){for(var se=null,ae=null,oe=A,le=A=0,Qe=null;oe!==null&&le<R.length;le++){oe.index>le?(Qe=oe,oe=null):Qe=oe.sibling;var ve=$(_,oe,R[le],q);if(ve===null){oe===null&&(oe=Qe);break}e&&oe&&ve.alternate===null&&n(_,oe),A=m(ve,A,le),ae===null?se=ve:ae.sibling=ve,ae=ve,oe=Qe}if(le===R.length)return a(_,oe),_e&&Fn(_,le),se;if(oe===null){for(;le<R.length;le++)oe=K(_,R[le],q),oe!==null&&(A=m(oe,A,le),ae===null?se=oe:ae.sibling=oe,ae=oe);return _e&&Fn(_,le),se}for(oe=l(_,oe);le<R.length;le++)Qe=J(oe,_,le,R[le],q),Qe!==null&&(e&&Qe.alternate!==null&&oe.delete(Qe.key===null?le:Qe.key),A=m(Qe,A,le),ae===null?se=Qe:ae.sibling=Qe,ae=Qe);return e&&oe.forEach(function(Pn){return n(_,Pn)}),_e&&Fn(_,le),se}function ne(_,A,R,q){var se=H(R);if(typeof se!="function")throw Error(r(150));if(R=se.call(R),R==null)throw Error(r(151));for(var ae=se=null,oe=A,le=A=0,Qe=null,ve=R.next();oe!==null&&!ve.done;le++,ve=R.next()){oe.index>le?(Qe=oe,oe=null):Qe=oe.sibling;var Pn=$(_,oe,ve.value,q);if(Pn===null){oe===null&&(oe=Qe);break}e&&oe&&Pn.alternate===null&&n(_,oe),A=m(Pn,A,le),ae===null?se=Pn:ae.sibling=Pn,ae=Pn,oe=Qe}if(ve.done)return a(_,oe),_e&&Fn(_,le),se;if(oe===null){for(;!ve.done;le++,ve=R.next())ve=K(_,ve.value,q),ve!==null&&(A=m(ve,A,le),ae===null?se=ve:ae.sibling=ve,ae=ve);return _e&&Fn(_,le),se}for(oe=l(_,oe);!ve.done;le++,ve=R.next())ve=J(oe,_,le,ve.value,q),ve!==null&&(e&&ve.alternate!==null&&oe.delete(ve.key===null?le:ve.key),A=m(ve,A,le),ae===null?se=ve:ae.sibling=ve,ae=ve);return e&&oe.forEach(function(vx){return n(_,vx)}),_e&&Fn(_,le),se}function Be(_,A,R,q){if(typeof R=="object"&&R!==null&&R.type===V&&R.key===null&&(R=R.props.children),typeof R=="object"&&R!==null){switch(R.$$typeof){case D:e:{for(var se=R.key,ae=A;ae!==null;){if(ae.key===se){if(se=R.type,se===V){if(ae.tag===7){a(_,ae.sibling),A=u(ae,R.props.children),A.return=_,_=A;break e}}else if(ae.elementType===se||typeof se=="object"&&se!==null&&se.$$typeof===Pe&&Gd(se)===ae.type){a(_,ae.sibling),A=u(ae,R.props),A.ref=di(_,ae,R),A.return=_,_=A;break e}a(_,ae);break}else n(_,ae);ae=ae.sibling}R.type===V?(A=Gn(R.props.children,_.mode,q,R.key),A.return=_,_=A):(q=Ur(R.type,R.key,R.props,null,_.mode,q),q.ref=di(_,A,R),q.return=_,_=q)}return y(_);case B:e:{for(ae=R.key;A!==null;){if(A.key===ae)if(A.tag===4&&A.stateNode.containerInfo===R.containerInfo&&A.stateNode.implementation===R.implementation){a(_,A.sibling),A=u(A,R.children||[]),A.return=_,_=A;break e}else{a(_,A);break}else n(_,A);A=A.sibling}A=Ml(R,_.mode,q),A.return=_,_=A}return y(_);case Pe:return ae=R._init,Be(_,A,ae(R._payload),q)}if(Os(R))return ee(_,A,R,q);if(H(R))return ne(_,A,R,q);vr(_,R)}return typeof R=="string"&&R!==""||typeof R=="number"?(R=""+R,A!==null&&A.tag===6?(a(_,A.sibling),A=u(A,R),A.return=_,_=A):(a(_,A),A=El(R,_.mode,q),A.return=_,_=A),y(_)):a(_,A)}return Be}var ws=Kd(!0),qd=Kd(!1),xr=yn(null),br=null,ks=null,Oo=null;function zo(){Oo=ks=br=null}function Uo(e){var n=xr.current;Ee(xr),e._currentValue=n}function Wo(e,n,a){for(;e!==null;){var l=e.alternate;if((e.childLanes&n)!==n?(e.childLanes|=n,l!==null&&(l.childLanes|=n)):l!==null&&(l.childLanes&n)!==n&&(l.childLanes|=n),e===a)break;e=e.return}}function js(e,n){br=e,Oo=ks=null,e=e.dependencies,e!==null&&e.firstContext!==null&&((e.lanes&n)!==0&&(ht=!0),e.firstContext=null)}function Tt(e){var n=e._currentValue;if(Oo!==e)if(e={context:e,memoizedValue:n,next:null},ks===null){if(br===null)throw Error(r(308));ks=e,br.dependencies={lanes:0,firstContext:e}}else ks=ks.next=e;return n}var Bn=null;function $o(e){Bn===null?Bn=[e]:Bn.push(e)}function Xd(e,n,a,l){var u=n.interleaved;return u===null?(a.next=a,$o(n)):(a.next=u.next,u.next=a),n.interleaved=a,nn(e,l)}function nn(e,n){e.lanes|=n;var a=e.alternate;for(a!==null&&(a.lanes|=n),a=e,e=e.return;e!==null;)e.childLanes|=n,a=e.alternate,a!==null&&(a.childLanes|=n),a=e,e=e.return;return a.tag===3?a.stateNode:null}var bn=!1;function Ho(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function Yd(e,n){e=e.updateQueue,n.updateQueue===e&&(n.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function sn(e,n){return{eventTime:e,lane:n,tag:0,payload:null,callback:null,next:null}}function wn(e,n,a){var l=e.updateQueue;if(l===null)return null;if(l=l.shared,(fe&2)!==0){var u=l.pending;return u===null?n.next=n:(n.next=u.next,u.next=n),l.pending=n,nn(e,a)}return u=l.interleaved,u===null?(n.next=n,$o(l)):(n.next=u.next,u.next=n),l.interleaved=n,nn(e,a)}function wr(e,n,a){if(n=n.updateQueue,n!==null&&(n=n.shared,(a&4194240)!==0)){var l=n.lanes;l&=e.pendingLanes,a|=l,n.lanes=a,io(e,a)}}function Qd(e,n){var a=e.updateQueue,l=e.alternate;if(l!==null&&(l=l.updateQueue,a===l)){var u=null,m=null;if(a=a.firstBaseUpdate,a!==null){do{var y={eventTime:a.eventTime,lane:a.lane,tag:a.tag,payload:a.payload,callback:a.callback,next:null};m===null?u=m=y:m=m.next=y,a=a.next}while(a!==null);m===null?u=m=n:m=m.next=n}else u=m=n;a={baseState:l.baseState,firstBaseUpdate:u,lastBaseUpdate:m,shared:l.shared,effects:l.effects},e.updateQueue=a;return}e=a.lastBaseUpdate,e===null?a.firstBaseUpdate=n:e.next=n,a.lastBaseUpdate=n}function kr(e,n,a,l){var u=e.updateQueue;bn=!1;var m=u.firstBaseUpdate,y=u.lastBaseUpdate,w=u.shared.pending;if(w!==null){u.shared.pending=null;var C=w,F=C.next;C.next=null,y===null?m=F:y.next=F,y=C;var G=e.alternate;G!==null&&(G=G.updateQueue,w=G.lastBaseUpdate,w!==y&&(w===null?G.firstBaseUpdate=F:w.next=F,G.lastBaseUpdate=C))}if(m!==null){var K=u.baseState;y=0,G=F=C=null,w=m;do{var $=w.lane,J=w.eventTime;if((l&$)===$){G!==null&&(G=G.next={eventTime:J,lane:0,tag:w.tag,payload:w.payload,callback:w.callback,next:null});e:{var ee=e,ne=w;switch($=n,J=a,ne.tag){case 1:if(ee=ne.payload,typeof ee=="function"){K=ee.call(J,K,$);break e}K=ee;break e;case 3:ee.flags=ee.flags&-65537|128;case 0:if(ee=ne.payload,$=typeof ee=="function"?ee.call(J,K,$):ee,$==null)break e;K=W({},K,$);break e;case 2:bn=!0}}w.callback!==null&&w.lane!==0&&(e.flags|=64,$=u.effects,$===null?u.effects=[w]:$.push(w))}else J={eventTime:J,lane:$,tag:w.tag,payload:w.payload,callback:w.callback,next:null},G===null?(F=G=J,C=K):G=G.next=J,y|=$;if(w=w.next,w===null){if(w=u.shared.pending,w===null)break;$=w,w=$.next,$.next=null,u.lastBaseUpdate=$,u.shared.pending=null}}while(!0);if(G===null&&(C=K),u.baseState=C,u.firstBaseUpdate=F,u.lastBaseUpdate=G,n=u.shared.interleaved,n!==null){u=n;do y|=u.lane,u=u.next;while(u!==n)}else m===null&&(u.shared.lanes=0);Un|=y,e.lanes=y,e.memoizedState=K}}function Jd(e,n,a){if(e=n.effects,n.effects=null,e!==null)for(n=0;n<e.length;n++){var l=e[n],u=l.callback;if(u!==null){if(l.callback=null,l=a,typeof u!="function")throw Error(r(191,u));u.call(l)}}}var hi={},Ht=yn(hi),mi=yn(hi),pi=yn(hi);function On(e){if(e===hi)throw Error(r(174));return e}function Go(e,n){switch(Ce(pi,n),Ce(mi,e),Ce(Ht,hi),e=n.nodeType,e){case 9:case 11:n=(n=n.documentElement)?n.namespaceURI:Ga(null,"");break;default:e=e===8?n.parentNode:n,n=e.namespaceURI||null,e=e.tagName,n=Ga(n,e)}Ee(Ht),Ce(Ht,n)}function Ss(){Ee(Ht),Ee(mi),Ee(pi)}function Zd(e){On(pi.current);var n=On(Ht.current),a=Ga(n,e.type);n!==a&&(Ce(mi,e),Ce(Ht,a))}function Ko(e){mi.current===e&&(Ee(Ht),Ee(mi))}var Re=yn(0);function jr(e){for(var n=e;n!==null;){if(n.tag===13){var a=n.memoizedState;if(a!==null&&(a=a.dehydrated,a===null||a.data==="$?"||a.data==="$!"))return n}else if(n.tag===19&&n.memoizedProps.revealOrder!==void 0){if((n.flags&128)!==0)return n}else if(n.child!==null){n.child.return=n,n=n.child;continue}if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return null;n=n.return}n.sibling.return=n.return,n=n.sibling}return null}var qo=[];function Xo(){for(var e=0;e<qo.length;e++)qo[e]._workInProgressVersionPrimary=null;qo.length=0}var Sr=I.ReactCurrentDispatcher,Yo=I.ReactCurrentBatchConfig,zn=0,Le=null,$e=null,Xe=null,Nr=!1,fi=!1,gi=0,Ov=0;function nt(){throw Error(r(321))}function Qo(e,n){if(n===null)return!1;for(var a=0;a<n.length&&a<e.length;a++)if(!Dt(e[a],n[a]))return!1;return!0}function Jo(e,n,a,l,u,m){if(zn=m,Le=n,n.memoizedState=null,n.updateQueue=null,n.lanes=0,Sr.current=e===null||e.memoizedState===null?$v:Hv,e=a(l,u),fi){m=0;do{if(fi=!1,gi=0,25<=m)throw Error(r(301));m+=1,Xe=$e=null,n.updateQueue=null,Sr.current=Gv,e=a(l,u)}while(fi)}if(Sr.current=Pr,n=$e!==null&&$e.next!==null,zn=0,Xe=$e=Le=null,Nr=!1,n)throw Error(r(300));return e}function Zo(){var e=gi!==0;return gi=0,e}function Gt(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return Xe===null?Le.memoizedState=Xe=e:Xe=Xe.next=e,Xe}function Pt(){if($e===null){var e=Le.alternate;e=e!==null?e.memoizedState:null}else e=$e.next;var n=Xe===null?Le.memoizedState:Xe.next;if(n!==null)Xe=n,$e=e;else{if(e===null)throw Error(r(310));$e=e,e={memoizedState:$e.memoizedState,baseState:$e.baseState,baseQueue:$e.baseQueue,queue:$e.queue,next:null},Xe===null?Le.memoizedState=Xe=e:Xe=Xe.next=e}return Xe}function yi(e,n){return typeof n=="function"?n(e):n}function el(e){var n=Pt(),a=n.queue;if(a===null)throw Error(r(311));a.lastRenderedReducer=e;var l=$e,u=l.baseQueue,m=a.pending;if(m!==null){if(u!==null){var y=u.next;u.next=m.next,m.next=y}l.baseQueue=u=m,a.pending=null}if(u!==null){m=u.next,l=l.baseState;var w=y=null,C=null,F=m;do{var G=F.lane;if((zn&G)===G)C!==null&&(C=C.next={lane:0,action:F.action,hasEagerState:F.hasEagerState,eagerState:F.eagerState,next:null}),l=F.hasEagerState?F.eagerState:e(l,F.action);else{var K={lane:G,action:F.action,hasEagerState:F.hasEagerState,eagerState:F.eagerState,next:null};C===null?(w=C=K,y=l):C=C.next=K,Le.lanes|=G,Un|=G}F=F.next}while(F!==null&&F!==m);C===null?y=l:C.next=w,Dt(l,n.memoizedState)||(ht=!0),n.memoizedState=l,n.baseState=y,n.baseQueue=C,a.lastRenderedState=l}if(e=a.interleaved,e!==null){u=e;do m=u.lane,Le.lanes|=m,Un|=m,u=u.next;while(u!==e)}else u===null&&(a.lanes=0);return[n.memoizedState,a.dispatch]}function tl(e){var n=Pt(),a=n.queue;if(a===null)throw Error(r(311));a.lastRenderedReducer=e;var l=a.dispatch,u=a.pending,m=n.memoizedState;if(u!==null){a.pending=null;var y=u=u.next;do m=e(m,y.action),y=y.next;while(y!==u);Dt(m,n.memoizedState)||(ht=!0),n.memoizedState=m,n.baseQueue===null&&(n.baseState=m),a.lastRenderedState=m}return[m,l]}function eh(){}function th(e,n){var a=Le,l=Pt(),u=n(),m=!Dt(l.memoizedState,u);if(m&&(l.memoizedState=u,ht=!0),l=l.queue,nl(ih.bind(null,a,l,e),[e]),l.getSnapshot!==n||m||Xe!==null&&Xe.memoizedState.tag&1){if(a.flags|=2048,vi(9,sh.bind(null,a,l,u,n),void 0,null),Ye===null)throw Error(r(349));(zn&30)!==0||nh(a,n,u)}return u}function nh(e,n,a){e.flags|=16384,e={getSnapshot:n,value:a},n=Le.updateQueue,n===null?(n={lastEffect:null,stores:null},Le.updateQueue=n,n.stores=[e]):(a=n.stores,a===null?n.stores=[e]:a.push(e))}function sh(e,n,a,l){n.value=a,n.getSnapshot=l,rh(n)&&ah(e)}function ih(e,n,a){return a(function(){rh(n)&&ah(e)})}function rh(e){var n=e.getSnapshot;e=e.value;try{var a=n();return!Dt(e,a)}catch{return!0}}function ah(e){var n=nn(e,1);n!==null&&Ft(n,e,1,-1)}function oh(e){var n=Gt();return typeof e=="function"&&(e=e()),n.memoizedState=n.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:yi,lastRenderedState:e},n.queue=e,e=e.dispatch=Wv.bind(null,Le,e),[n.memoizedState,e]}function vi(e,n,a,l){return e={tag:e,create:n,destroy:a,deps:l,next:null},n=Le.updateQueue,n===null?(n={lastEffect:null,stores:null},Le.updateQueue=n,n.lastEffect=e.next=e):(a=n.lastEffect,a===null?n.lastEffect=e.next=e:(l=a.next,a.next=e,e.next=l,n.lastEffect=e)),e}function lh(){return Pt().memoizedState}function Cr(e,n,a,l){var u=Gt();Le.flags|=e,u.memoizedState=vi(1|n,a,void 0,l===void 0?null:l)}function Tr(e,n,a,l){var u=Pt();l=l===void 0?null:l;var m=void 0;if($e!==null){var y=$e.memoizedState;if(m=y.destroy,l!==null&&Qo(l,y.deps)){u.memoizedState=vi(n,a,m,l);return}}Le.flags|=e,u.memoizedState=vi(1|n,a,m,l)}function ch(e,n){return Cr(8390656,8,e,n)}function nl(e,n){return Tr(2048,8,e,n)}function uh(e,n){return Tr(4,2,e,n)}function dh(e,n){return Tr(4,4,e,n)}function hh(e,n){if(typeof n=="function")return e=e(),n(e),function(){n(null)};if(n!=null)return e=e(),n.current=e,function(){n.current=null}}function mh(e,n,a){return a=a!=null?a.concat([e]):null,Tr(4,4,hh.bind(null,n,e),a)}function sl(){}function ph(e,n){var a=Pt();n=n===void 0?null:n;var l=a.memoizedState;return l!==null&&n!==null&&Qo(n,l[1])?l[0]:(a.memoizedState=[e,n],e)}function fh(e,n){var a=Pt();n=n===void 0?null:n;var l=a.memoizedState;return l!==null&&n!==null&&Qo(n,l[1])?l[0]:(e=e(),a.memoizedState=[e,n],e)}function gh(e,n,a){return(zn&21)===0?(e.baseState&&(e.baseState=!1,ht=!0),e.memoizedState=a):(Dt(a,n)||(a=Gu(),Le.lanes|=a,Un|=a,e.baseState=!0),n)}function zv(e,n){var a=we;we=a!==0&&4>a?a:4,e(!0);var l=Yo.transition;Yo.transition={};try{e(!1),n()}finally{we=a,Yo.transition=l}}function yh(){return Pt().memoizedState}function Uv(e,n,a){var l=Nn(e);if(a={lane:l,action:a,hasEagerState:!1,eagerState:null,next:null},vh(e))xh(n,a);else if(a=Xd(e,n,a,l),a!==null){var u=ot();Ft(a,e,l,u),bh(a,n,l)}}function Wv(e,n,a){var l=Nn(e),u={lane:l,action:a,hasEagerState:!1,eagerState:null,next:null};if(vh(e))xh(n,u);else{var m=e.alternate;if(e.lanes===0&&(m===null||m.lanes===0)&&(m=n.lastRenderedReducer,m!==null))try{var y=n.lastRenderedState,w=m(y,a);if(u.hasEagerState=!0,u.eagerState=w,Dt(w,y)){var C=n.interleaved;C===null?(u.next=u,$o(n)):(u.next=C.next,C.next=u),n.interleaved=u;return}}catch{}finally{}a=Xd(e,n,u,l),a!==null&&(u=ot(),Ft(a,e,l,u),bh(a,n,l))}}function vh(e){var n=e.alternate;return e===Le||n!==null&&n===Le}function xh(e,n){fi=Nr=!0;var a=e.pending;a===null?n.next=n:(n.next=a.next,a.next=n),e.pending=n}function bh(e,n,a){if((a&4194240)!==0){var l=n.lanes;l&=e.pendingLanes,a|=l,n.lanes=a,io(e,a)}}var Pr={readContext:Tt,useCallback:nt,useContext:nt,useEffect:nt,useImperativeHandle:nt,useInsertionEffect:nt,useLayoutEffect:nt,useMemo:nt,useReducer:nt,useRef:nt,useState:nt,useDebugValue:nt,useDeferredValue:nt,useTransition:nt,useMutableSource:nt,useSyncExternalStore:nt,useId:nt,unstable_isNewReconciler:!1},$v={readContext:Tt,useCallback:function(e,n){return Gt().memoizedState=[e,n===void 0?null:n],e},useContext:Tt,useEffect:ch,useImperativeHandle:function(e,n,a){return a=a!=null?a.concat([e]):null,Cr(4194308,4,hh.bind(null,n,e),a)},useLayoutEffect:function(e,n){return Cr(4194308,4,e,n)},useInsertionEffect:function(e,n){return Cr(4,2,e,n)},useMemo:function(e,n){var a=Gt();return n=n===void 0?null:n,e=e(),a.memoizedState=[e,n],e},useReducer:function(e,n,a){var l=Gt();return n=a!==void 0?a(n):n,l.memoizedState=l.baseState=n,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:n},l.queue=e,e=e.dispatch=Uv.bind(null,Le,e),[l.memoizedState,e]},useRef:function(e){var n=Gt();return e={current:e},n.memoizedState=e},useState:oh,useDebugValue:sl,useDeferredValue:function(e){return Gt().memoizedState=e},useTransition:function(){var e=oh(!1),n=e[0];return e=zv.bind(null,e[1]),Gt().memoizedState=e,[n,e]},useMutableSource:function(){},useSyncExternalStore:function(e,n,a){var l=Le,u=Gt();if(_e){if(a===void 0)throw Error(r(407));a=a()}else{if(a=n(),Ye===null)throw Error(r(349));(zn&30)!==0||nh(l,n,a)}u.memoizedState=a;var m={value:a,getSnapshot:n};return u.queue=m,ch(ih.bind(null,l,m,e),[e]),l.flags|=2048,vi(9,sh.bind(null,l,m,a,n),void 0,null),a},useId:function(){var e=Gt(),n=Ye.identifierPrefix;if(_e){var a=tn,l=en;a=(l&~(1<<32-_t(l)-1)).toString(32)+a,n=":"+n+"R"+a,a=gi++,0<a&&(n+="H"+a.toString(32)),n+=":"}else a=Ov++,n=":"+n+"r"+a.toString(32)+":";return e.memoizedState=n},unstable_isNewReconciler:!1},Hv={readContext:Tt,useCallback:ph,useContext:Tt,useEffect:nl,useImperativeHandle:mh,useInsertionEffect:uh,useLayoutEffect:dh,useMemo:fh,useReducer:el,useRef:lh,useState:function(){return el(yi)},useDebugValue:sl,useDeferredValue:function(e){var n=Pt();return gh(n,$e.memoizedState,e)},useTransition:function(){var e=el(yi)[0],n=Pt().memoizedState;return[e,n]},useMutableSource:eh,useSyncExternalStore:th,useId:yh,unstable_isNewReconciler:!1},Gv={readContext:Tt,useCallback:ph,useContext:Tt,useEffect:nl,useImperativeHandle:mh,useInsertionEffect:uh,useLayoutEffect:dh,useMemo:fh,useReducer:tl,useRef:lh,useState:function(){return tl(yi)},useDebugValue:sl,useDeferredValue:function(e){var n=Pt();return $e===null?n.memoizedState=e:gh(n,$e.memoizedState,e)},useTransition:function(){var e=tl(yi)[0],n=Pt().memoizedState;return[e,n]},useMutableSource:eh,useSyncExternalStore:th,useId:yh,unstable_isNewReconciler:!1};function Lt(e,n){if(e&&e.defaultProps){n=W({},n),e=e.defaultProps;for(var a in e)n[a]===void 0&&(n[a]=e[a]);return n}return n}function il(e,n,a,l){n=e.memoizedState,a=a(l,n),a=a==null?n:W({},n,a),e.memoizedState=a,e.lanes===0&&(e.updateQueue.baseState=a)}var Ar={isMounted:function(e){return(e=e._reactInternals)?Rn(e)===e:!1},enqueueSetState:function(e,n,a){e=e._reactInternals;var l=ot(),u=Nn(e),m=sn(l,u);m.payload=n,a!=null&&(m.callback=a),n=wn(e,m,u),n!==null&&(Ft(n,e,u,l),wr(n,e,u))},enqueueReplaceState:function(e,n,a){e=e._reactInternals;var l=ot(),u=Nn(e),m=sn(l,u);m.tag=1,m.payload=n,a!=null&&(m.callback=a),n=wn(e,m,u),n!==null&&(Ft(n,e,u,l),wr(n,e,u))},enqueueForceUpdate:function(e,n){e=e._reactInternals;var a=ot(),l=Nn(e),u=sn(a,l);u.tag=2,n!=null&&(u.callback=n),n=wn(e,u,l),n!==null&&(Ft(n,e,l,a),wr(n,e,l))}};function wh(e,n,a,l,u,m,y){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(l,m,y):n.prototype&&n.prototype.isPureReactComponent?!ii(a,l)||!ii(u,m):!0}function kh(e,n,a){var l=!1,u=vn,m=n.contextType;return typeof m=="object"&&m!==null?m=Tt(m):(u=dt(n)?In:tt.current,l=n.contextTypes,m=(l=l!=null)?ys(e,u):vn),n=new n(a,m),e.memoizedState=n.state!==null&&n.state!==void 0?n.state:null,n.updater=Ar,e.stateNode=n,n._reactInternals=e,l&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=u,e.__reactInternalMemoizedMaskedChildContext=m),n}function jh(e,n,a,l){e=n.state,typeof n.componentWillReceiveProps=="function"&&n.componentWillReceiveProps(a,l),typeof n.UNSAFE_componentWillReceiveProps=="function"&&n.UNSAFE_componentWillReceiveProps(a,l),n.state!==e&&Ar.enqueueReplaceState(n,n.state,null)}function rl(e,n,a,l){var u=e.stateNode;u.props=a,u.state=e.memoizedState,u.refs={},Ho(e);var m=n.contextType;typeof m=="object"&&m!==null?u.context=Tt(m):(m=dt(n)?In:tt.current,u.context=ys(e,m)),u.state=e.memoizedState,m=n.getDerivedStateFromProps,typeof m=="function"&&(il(e,n,m,a),u.state=e.memoizedState),typeof n.getDerivedStateFromProps=="function"||typeof u.getSnapshotBeforeUpdate=="function"||typeof u.UNSAFE_componentWillMount!="function"&&typeof u.componentWillMount!="function"||(n=u.state,typeof u.componentWillMount=="function"&&u.componentWillMount(),typeof u.UNSAFE_componentWillMount=="function"&&u.UNSAFE_componentWillMount(),n!==u.state&&Ar.enqueueReplaceState(u,u.state,null),kr(e,a,u,l),u.state=e.memoizedState),typeof u.componentDidMount=="function"&&(e.flags|=4194308)}function Ns(e,n){try{var a="",l=n;do a+=ge(l),l=l.return;while(l);var u=a}catch(m){u=`
Error generating stack: `+m.message+`
`+m.stack}return{value:e,source:n,stack:u,digest:null}}function al(e,n,a){return{value:e,source:null,stack:a??null,digest:n??null}}function ol(e,n){try{console.error(n.value)}catch(a){setTimeout(function(){throw a})}}var Kv=typeof WeakMap=="function"?WeakMap:Map;function Sh(e,n,a){a=sn(-1,a),a.tag=3,a.payload={element:null};var l=n.value;return a.callback=function(){Ir||(Ir=!0,kl=l),ol(e,n)},a}function Nh(e,n,a){a=sn(-1,a),a.tag=3;var l=e.type.getDerivedStateFromError;if(typeof l=="function"){var u=n.value;a.payload=function(){return l(u)},a.callback=function(){ol(e,n)}}var m=e.stateNode;return m!==null&&typeof m.componentDidCatch=="function"&&(a.callback=function(){ol(e,n),typeof l!="function"&&(jn===null?jn=new Set([this]):jn.add(this));var y=n.stack;this.componentDidCatch(n.value,{componentStack:y!==null?y:""})}),a}function Ch(e,n,a){var l=e.pingCache;if(l===null){l=e.pingCache=new Kv;var u=new Set;l.set(n,u)}else u=l.get(n),u===void 0&&(u=new Set,l.set(n,u));u.has(a)||(u.add(a),e=ox.bind(null,e,n,a),n.then(e,e))}function Th(e){do{var n;if((n=e.tag===13)&&(n=e.memoizedState,n=n!==null?n.dehydrated!==null:!0),n)return e;e=e.return}while(e!==null);return null}function Ph(e,n,a,l,u){return(e.mode&1)===0?(e===n?e.flags|=65536:(e.flags|=128,a.flags|=131072,a.flags&=-52805,a.tag===1&&(a.alternate===null?a.tag=17:(n=sn(-1,1),n.tag=2,wn(a,n,1))),a.lanes|=1),e):(e.flags|=65536,e.lanes=u,e)}var qv=I.ReactCurrentOwner,ht=!1;function at(e,n,a,l){n.child=e===null?qd(n,null,a,l):ws(n,e.child,a,l)}function Ah(e,n,a,l,u){a=a.render;var m=n.ref;return js(n,u),l=Jo(e,n,a,l,m,u),a=Zo(),e!==null&&!ht?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~u,rn(e,n,u)):(_e&&a&&Lo(n),n.flags|=1,at(e,n,l,u),n.child)}function Eh(e,n,a,l,u){if(e===null){var m=a.type;return typeof m=="function"&&!Al(m)&&m.defaultProps===void 0&&a.compare===null&&a.defaultProps===void 0?(n.tag=15,n.type=m,Mh(e,n,m,l,u)):(e=Ur(a.type,null,l,n,n.mode,u),e.ref=n.ref,e.return=n,n.child=e)}if(m=e.child,(e.lanes&u)===0){var y=m.memoizedProps;if(a=a.compare,a=a!==null?a:ii,a(y,l)&&e.ref===n.ref)return rn(e,n,u)}return n.flags|=1,e=Tn(m,l),e.ref=n.ref,e.return=n,n.child=e}function Mh(e,n,a,l,u){if(e!==null){var m=e.memoizedProps;if(ii(m,l)&&e.ref===n.ref)if(ht=!1,n.pendingProps=l=m,(e.lanes&u)!==0)(e.flags&131072)!==0&&(ht=!0);else return n.lanes=e.lanes,rn(e,n,u)}return ll(e,n,a,l,u)}function _h(e,n,a){var l=n.pendingProps,u=l.children,m=e!==null?e.memoizedState:null;if(l.mode==="hidden")if((n.mode&1)===0)n.memoizedState={baseLanes:0,cachePool:null,transitions:null},Ce(Ts,wt),wt|=a;else{if((a&1073741824)===0)return e=m!==null?m.baseLanes|a:a,n.lanes=n.childLanes=1073741824,n.memoizedState={baseLanes:e,cachePool:null,transitions:null},n.updateQueue=null,Ce(Ts,wt),wt|=e,null;n.memoizedState={baseLanes:0,cachePool:null,transitions:null},l=m!==null?m.baseLanes:a,Ce(Ts,wt),wt|=l}else m!==null?(l=m.baseLanes|a,n.memoizedState=null):l=a,Ce(Ts,wt),wt|=l;return at(e,n,u,a),n.child}function Dh(e,n){var a=n.ref;(e===null&&a!==null||e!==null&&e.ref!==a)&&(n.flags|=512,n.flags|=2097152)}function ll(e,n,a,l,u){var m=dt(a)?In:tt.current;return m=ys(n,m),js(n,u),a=Jo(e,n,a,l,m,u),l=Zo(),e!==null&&!ht?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~u,rn(e,n,u)):(_e&&l&&Lo(n),n.flags|=1,at(e,n,a,u),n.child)}function Rh(e,n,a,l,u){if(dt(a)){var m=!0;mr(n)}else m=!1;if(js(n,u),n.stateNode===null)Mr(e,n),kh(n,a,l),rl(n,a,l,u),l=!0;else if(e===null){var y=n.stateNode,w=n.memoizedProps;y.props=w;var C=y.context,F=a.contextType;typeof F=="object"&&F!==null?F=Tt(F):(F=dt(a)?In:tt.current,F=ys(n,F));var G=a.getDerivedStateFromProps,K=typeof G=="function"||typeof y.getSnapshotBeforeUpdate=="function";K||typeof y.UNSAFE_componentWillReceiveProps!="function"&&typeof y.componentWillReceiveProps!="function"||(w!==l||C!==F)&&jh(n,y,l,F),bn=!1;var $=n.memoizedState;y.state=$,kr(n,l,y,u),C=n.memoizedState,w!==l||$!==C||ut.current||bn?(typeof G=="function"&&(il(n,a,G,l),C=n.memoizedState),(w=bn||wh(n,a,w,l,$,C,F))?(K||typeof y.UNSAFE_componentWillMount!="function"&&typeof y.componentWillMount!="function"||(typeof y.componentWillMount=="function"&&y.componentWillMount(),typeof y.UNSAFE_componentWillMount=="function"&&y.UNSAFE_componentWillMount()),typeof y.componentDidMount=="function"&&(n.flags|=4194308)):(typeof y.componentDidMount=="function"&&(n.flags|=4194308),n.memoizedProps=l,n.memoizedState=C),y.props=l,y.state=C,y.context=F,l=w):(typeof y.componentDidMount=="function"&&(n.flags|=4194308),l=!1)}else{y=n.stateNode,Yd(e,n),w=n.memoizedProps,F=n.type===n.elementType?w:Lt(n.type,w),y.props=F,K=n.pendingProps,$=y.context,C=a.contextType,typeof C=="object"&&C!==null?C=Tt(C):(C=dt(a)?In:tt.current,C=ys(n,C));var J=a.getDerivedStateFromProps;(G=typeof J=="function"||typeof y.getSnapshotBeforeUpdate=="function")||typeof y.UNSAFE_componentWillReceiveProps!="function"&&typeof y.componentWillReceiveProps!="function"||(w!==K||$!==C)&&jh(n,y,l,C),bn=!1,$=n.memoizedState,y.state=$,kr(n,l,y,u);var ee=n.memoizedState;w!==K||$!==ee||ut.current||bn?(typeof J=="function"&&(il(n,a,J,l),ee=n.memoizedState),(F=bn||wh(n,a,F,l,$,ee,C)||!1)?(G||typeof y.UNSAFE_componentWillUpdate!="function"&&typeof y.componentWillUpdate!="function"||(typeof y.componentWillUpdate=="function"&&y.componentWillUpdate(l,ee,C),typeof y.UNSAFE_componentWillUpdate=="function"&&y.UNSAFE_componentWillUpdate(l,ee,C)),typeof y.componentDidUpdate=="function"&&(n.flags|=4),typeof y.getSnapshotBeforeUpdate=="function"&&(n.flags|=1024)):(typeof y.componentDidUpdate!="function"||w===e.memoizedProps&&$===e.memoizedState||(n.flags|=4),typeof y.getSnapshotBeforeUpdate!="function"||w===e.memoizedProps&&$===e.memoizedState||(n.flags|=1024),n.memoizedProps=l,n.memoizedState=ee),y.props=l,y.state=ee,y.context=C,l=F):(typeof y.componentDidUpdate!="function"||w===e.memoizedProps&&$===e.memoizedState||(n.flags|=4),typeof y.getSnapshotBeforeUpdate!="function"||w===e.memoizedProps&&$===e.memoizedState||(n.flags|=1024),l=!1)}return cl(e,n,a,l,m,u)}function cl(e,n,a,l,u,m){Dh(e,n);var y=(n.flags&128)!==0;if(!l&&!y)return u&&Bd(n,a,!1),rn(e,n,m);l=n.stateNode,qv.current=n;var w=y&&typeof a.getDerivedStateFromError!="function"?null:l.render();return n.flags|=1,e!==null&&y?(n.child=ws(n,e.child,null,m),n.child=ws(n,null,w,m)):at(e,n,w,m),n.memoizedState=l.state,u&&Bd(n,a,!0),n.child}function Lh(e){var n=e.stateNode;n.pendingContext?Vd(e,n.pendingContext,n.pendingContext!==n.context):n.context&&Vd(e,n.context,!1),Go(e,n.containerInfo)}function Ih(e,n,a,l,u){return bs(),Bo(u),n.flags|=256,at(e,n,a,l),n.child}var ul={dehydrated:null,treeContext:null,retryLane:0};function dl(e){return{baseLanes:e,cachePool:null,transitions:null}}function Vh(e,n,a){var l=n.pendingProps,u=Re.current,m=!1,y=(n.flags&128)!==0,w;if((w=y)||(w=e!==null&&e.memoizedState===null?!1:(u&2)!==0),w?(m=!0,n.flags&=-129):(e===null||e.memoizedState!==null)&&(u|=1),Ce(Re,u&1),e===null)return Fo(n),e=n.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?((n.mode&1)===0?n.lanes=1:e.data==="$!"?n.lanes=8:n.lanes=1073741824,null):(y=l.children,e=l.fallback,m?(l=n.mode,m=n.child,y={mode:"hidden",children:y},(l&1)===0&&m!==null?(m.childLanes=0,m.pendingProps=y):m=Wr(y,l,0,null),e=Gn(e,l,a,null),m.return=n,e.return=n,m.sibling=e,n.child=m,n.child.memoizedState=dl(a),n.memoizedState=ul,e):hl(n,y));if(u=e.memoizedState,u!==null&&(w=u.dehydrated,w!==null))return Xv(e,n,y,l,w,u,a);if(m){m=l.fallback,y=n.mode,u=e.child,w=u.sibling;var C={mode:"hidden",children:l.children};return(y&1)===0&&n.child!==u?(l=n.child,l.childLanes=0,l.pendingProps=C,n.deletions=null):(l=Tn(u,C),l.subtreeFlags=u.subtreeFlags&14680064),w!==null?m=Tn(w,m):(m=Gn(m,y,a,null),m.flags|=2),m.return=n,l.return=n,l.sibling=m,n.child=l,l=m,m=n.child,y=e.child.memoizedState,y=y===null?dl(a):{baseLanes:y.baseLanes|a,cachePool:null,transitions:y.transitions},m.memoizedState=y,m.childLanes=e.childLanes&~a,n.memoizedState=ul,l}return m=e.child,e=m.sibling,l=Tn(m,{mode:"visible",children:l.children}),(n.mode&1)===0&&(l.lanes=a),l.return=n,l.sibling=null,e!==null&&(a=n.deletions,a===null?(n.deletions=[e],n.flags|=16):a.push(e)),n.child=l,n.memoizedState=null,l}function hl(e,n){return n=Wr({mode:"visible",children:n},e.mode,0,null),n.return=e,e.child=n}function Er(e,n,a,l){return l!==null&&Bo(l),ws(n,e.child,null,a),e=hl(n,n.pendingProps.children),e.flags|=2,n.memoizedState=null,e}function Xv(e,n,a,l,u,m,y){if(a)return n.flags&256?(n.flags&=-257,l=al(Error(r(422))),Er(e,n,y,l)):n.memoizedState!==null?(n.child=e.child,n.flags|=128,null):(m=l.fallback,u=n.mode,l=Wr({mode:"visible",children:l.children},u,0,null),m=Gn(m,u,y,null),m.flags|=2,l.return=n,m.return=n,l.sibling=m,n.child=l,(n.mode&1)!==0&&ws(n,e.child,null,y),n.child.memoizedState=dl(y),n.memoizedState=ul,m);if((n.mode&1)===0)return Er(e,n,y,null);if(u.data==="$!"){if(l=u.nextSibling&&u.nextSibling.dataset,l)var w=l.dgst;return l=w,m=Error(r(419)),l=al(m,l,void 0),Er(e,n,y,l)}if(w=(y&e.childLanes)!==0,ht||w){if(l=Ye,l!==null){switch(y&-y){case 4:u=2;break;case 16:u=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:u=32;break;case 536870912:u=268435456;break;default:u=0}u=(u&(l.suspendedLanes|y))!==0?0:u,u!==0&&u!==m.retryLane&&(m.retryLane=u,nn(e,u),Ft(l,e,u,-1))}return Pl(),l=al(Error(r(421))),Er(e,n,y,l)}return u.data==="$?"?(n.flags|=128,n.child=e.child,n=lx.bind(null,e),u._reactRetry=n,null):(e=m.treeContext,bt=gn(u.nextSibling),xt=n,_e=!0,Rt=null,e!==null&&(Nt[Ct++]=en,Nt[Ct++]=tn,Nt[Ct++]=Vn,en=e.id,tn=e.overflow,Vn=n),n=hl(n,l.children),n.flags|=4096,n)}function Fh(e,n,a){e.lanes|=n;var l=e.alternate;l!==null&&(l.lanes|=n),Wo(e.return,n,a)}function ml(e,n,a,l,u){var m=e.memoizedState;m===null?e.memoizedState={isBackwards:n,rendering:null,renderingStartTime:0,last:l,tail:a,tailMode:u}:(m.isBackwards=n,m.rendering=null,m.renderingStartTime=0,m.last=l,m.tail=a,m.tailMode=u)}function Bh(e,n,a){var l=n.pendingProps,u=l.revealOrder,m=l.tail;if(at(e,n,l.children,a),l=Re.current,(l&2)!==0)l=l&1|2,n.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=n.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Fh(e,a,n);else if(e.tag===19)Fh(e,a,n);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===n)break e;for(;e.sibling===null;){if(e.return===null||e.return===n)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}l&=1}if(Ce(Re,l),(n.mode&1)===0)n.memoizedState=null;else switch(u){case"forwards":for(a=n.child,u=null;a!==null;)e=a.alternate,e!==null&&jr(e)===null&&(u=a),a=a.sibling;a=u,a===null?(u=n.child,n.child=null):(u=a.sibling,a.sibling=null),ml(n,!1,u,a,m);break;case"backwards":for(a=null,u=n.child,n.child=null;u!==null;){if(e=u.alternate,e!==null&&jr(e)===null){n.child=u;break}e=u.sibling,u.sibling=a,a=u,u=e}ml(n,!0,a,null,m);break;case"together":ml(n,!1,null,null,void 0);break;default:n.memoizedState=null}return n.child}function Mr(e,n){(n.mode&1)===0&&e!==null&&(e.alternate=null,n.alternate=null,n.flags|=2)}function rn(e,n,a){if(e!==null&&(n.dependencies=e.dependencies),Un|=n.lanes,(a&n.childLanes)===0)return null;if(e!==null&&n.child!==e.child)throw Error(r(153));if(n.child!==null){for(e=n.child,a=Tn(e,e.pendingProps),n.child=a,a.return=n;e.sibling!==null;)e=e.sibling,a=a.sibling=Tn(e,e.pendingProps),a.return=n;a.sibling=null}return n.child}function Yv(e,n,a){switch(n.tag){case 3:Lh(n),bs();break;case 5:Zd(n);break;case 1:dt(n.type)&&mr(n);break;case 4:Go(n,n.stateNode.containerInfo);break;case 10:var l=n.type._context,u=n.memoizedProps.value;Ce(xr,l._currentValue),l._currentValue=u;break;case 13:if(l=n.memoizedState,l!==null)return l.dehydrated!==null?(Ce(Re,Re.current&1),n.flags|=128,null):(a&n.child.childLanes)!==0?Vh(e,n,a):(Ce(Re,Re.current&1),e=rn(e,n,a),e!==null?e.sibling:null);Ce(Re,Re.current&1);break;case 19:if(l=(a&n.childLanes)!==0,(e.flags&128)!==0){if(l)return Bh(e,n,a);n.flags|=128}if(u=n.memoizedState,u!==null&&(u.rendering=null,u.tail=null,u.lastEffect=null),Ce(Re,Re.current),l)break;return null;case 22:case 23:return n.lanes=0,_h(e,n,a)}return rn(e,n,a)}var Oh,pl,zh,Uh;Oh=function(e,n){for(var a=n.child;a!==null;){if(a.tag===5||a.tag===6)e.appendChild(a.stateNode);else if(a.tag!==4&&a.child!==null){a.child.return=a,a=a.child;continue}if(a===n)break;for(;a.sibling===null;){if(a.return===null||a.return===n)return;a=a.return}a.sibling.return=a.return,a=a.sibling}},pl=function(){},zh=function(e,n,a,l){var u=e.memoizedProps;if(u!==l){e=n.stateNode,On(Ht.current);var m=null;switch(a){case"input":u=Ua(e,u),l=Ua(e,l),m=[];break;case"select":u=W({},u,{value:void 0}),l=W({},l,{value:void 0}),m=[];break;case"textarea":u=Ha(e,u),l=Ha(e,l),m=[];break;default:typeof u.onClick!="function"&&typeof l.onClick=="function"&&(e.onclick=ur)}Ka(a,l);var y;a=null;for(F in u)if(!l.hasOwnProperty(F)&&u.hasOwnProperty(F)&&u[F]!=null)if(F==="style"){var w=u[F];for(y in w)w.hasOwnProperty(y)&&(a||(a={}),a[y]="")}else F!=="dangerouslySetInnerHTML"&&F!=="children"&&F!=="suppressContentEditableWarning"&&F!=="suppressHydrationWarning"&&F!=="autoFocus"&&(c.hasOwnProperty(F)?m||(m=[]):(m=m||[]).push(F,null));for(F in l){var C=l[F];if(w=u!=null?u[F]:void 0,l.hasOwnProperty(F)&&C!==w&&(C!=null||w!=null))if(F==="style")if(w){for(y in w)!w.hasOwnProperty(y)||C&&C.hasOwnProperty(y)||(a||(a={}),a[y]="");for(y in C)C.hasOwnProperty(y)&&w[y]!==C[y]&&(a||(a={}),a[y]=C[y])}else a||(m||(m=[]),m.push(F,a)),a=C;else F==="dangerouslySetInnerHTML"?(C=C?C.__html:void 0,w=w?w.__html:void 0,C!=null&&w!==C&&(m=m||[]).push(F,C)):F==="children"?typeof C!="string"&&typeof C!="number"||(m=m||[]).push(F,""+C):F!=="suppressContentEditableWarning"&&F!=="suppressHydrationWarning"&&(c.hasOwnProperty(F)?(C!=null&&F==="onScroll"&&Ae("scroll",e),m||w===C||(m=[])):(m=m||[]).push(F,C))}a&&(m=m||[]).push("style",a);var F=m;(n.updateQueue=F)&&(n.flags|=4)}},Uh=function(e,n,a,l){a!==l&&(n.flags|=4)};function xi(e,n){if(!_e)switch(e.tailMode){case"hidden":n=e.tail;for(var a=null;n!==null;)n.alternate!==null&&(a=n),n=n.sibling;a===null?e.tail=null:a.sibling=null;break;case"collapsed":a=e.tail;for(var l=null;a!==null;)a.alternate!==null&&(l=a),a=a.sibling;l===null?n||e.tail===null?e.tail=null:e.tail.sibling=null:l.sibling=null}}function st(e){var n=e.alternate!==null&&e.alternate.child===e.child,a=0,l=0;if(n)for(var u=e.child;u!==null;)a|=u.lanes|u.childLanes,l|=u.subtreeFlags&14680064,l|=u.flags&14680064,u.return=e,u=u.sibling;else for(u=e.child;u!==null;)a|=u.lanes|u.childLanes,l|=u.subtreeFlags,l|=u.flags,u.return=e,u=u.sibling;return e.subtreeFlags|=l,e.childLanes=a,n}function Qv(e,n,a){var l=n.pendingProps;switch(Io(n),n.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return st(n),null;case 1:return dt(n.type)&&hr(),st(n),null;case 3:return l=n.stateNode,Ss(),Ee(ut),Ee(tt),Xo(),l.pendingContext&&(l.context=l.pendingContext,l.pendingContext=null),(e===null||e.child===null)&&(yr(n)?n.flags|=4:e===null||e.memoizedState.isDehydrated&&(n.flags&256)===0||(n.flags|=1024,Rt!==null&&(Nl(Rt),Rt=null))),pl(e,n),st(n),null;case 5:Ko(n);var u=On(pi.current);if(a=n.type,e!==null&&n.stateNode!=null)zh(e,n,a,l,u),e.ref!==n.ref&&(n.flags|=512,n.flags|=2097152);else{if(!l){if(n.stateNode===null)throw Error(r(166));return st(n),null}if(e=On(Ht.current),yr(n)){l=n.stateNode,a=n.type;var m=n.memoizedProps;switch(l[$t]=n,l[ci]=m,e=(n.mode&1)!==0,a){case"dialog":Ae("cancel",l),Ae("close",l);break;case"iframe":case"object":case"embed":Ae("load",l);break;case"video":case"audio":for(u=0;u<ai.length;u++)Ae(ai[u],l);break;case"source":Ae("error",l);break;case"img":case"image":case"link":Ae("error",l),Ae("load",l);break;case"details":Ae("toggle",l);break;case"input":ku(l,m),Ae("invalid",l);break;case"select":l._wrapperState={wasMultiple:!!m.multiple},Ae("invalid",l);break;case"textarea":Nu(l,m),Ae("invalid",l)}Ka(a,m),u=null;for(var y in m)if(m.hasOwnProperty(y)){var w=m[y];y==="children"?typeof w=="string"?l.textContent!==w&&(m.suppressHydrationWarning!==!0&&cr(l.textContent,w,e),u=["children",w]):typeof w=="number"&&l.textContent!==""+w&&(m.suppressHydrationWarning!==!0&&cr(l.textContent,w,e),u=["children",""+w]):c.hasOwnProperty(y)&&w!=null&&y==="onScroll"&&Ae("scroll",l)}switch(a){case"input":Oi(l),Su(l,m,!0);break;case"textarea":Oi(l),Tu(l);break;case"select":case"option":break;default:typeof m.onClick=="function"&&(l.onclick=ur)}l=u,n.updateQueue=l,l!==null&&(n.flags|=4)}else{y=u.nodeType===9?u:u.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=Pu(a)),e==="http://www.w3.org/1999/xhtml"?a==="script"?(e=y.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof l.is=="string"?e=y.createElement(a,{is:l.is}):(e=y.createElement(a),a==="select"&&(y=e,l.multiple?y.multiple=!0:l.size&&(y.size=l.size))):e=y.createElementNS(e,a),e[$t]=n,e[ci]=l,Oh(e,n,!1,!1),n.stateNode=e;e:{switch(y=qa(a,l),a){case"dialog":Ae("cancel",e),Ae("close",e),u=l;break;case"iframe":case"object":case"embed":Ae("load",e),u=l;break;case"video":case"audio":for(u=0;u<ai.length;u++)Ae(ai[u],e);u=l;break;case"source":Ae("error",e),u=l;break;case"img":case"image":case"link":Ae("error",e),Ae("load",e),u=l;break;case"details":Ae("toggle",e),u=l;break;case"input":ku(e,l),u=Ua(e,l),Ae("invalid",e);break;case"option":u=l;break;case"select":e._wrapperState={wasMultiple:!!l.multiple},u=W({},l,{value:void 0}),Ae("invalid",e);break;case"textarea":Nu(e,l),u=Ha(e,l),Ae("invalid",e);break;default:u=l}Ka(a,u),w=u;for(m in w)if(w.hasOwnProperty(m)){var C=w[m];m==="style"?Mu(e,C):m==="dangerouslySetInnerHTML"?(C=C?C.__html:void 0,C!=null&&Au(e,C)):m==="children"?typeof C=="string"?(a!=="textarea"||C!=="")&&zs(e,C):typeof C=="number"&&zs(e,""+C):m!=="suppressContentEditableWarning"&&m!=="suppressHydrationWarning"&&m!=="autoFocus"&&(c.hasOwnProperty(m)?C!=null&&m==="onScroll"&&Ae("scroll",e):C!=null&&L(e,m,C,y))}switch(a){case"input":Oi(e),Su(e,l,!1);break;case"textarea":Oi(e),Tu(e);break;case"option":l.value!=null&&e.setAttribute("value",""+be(l.value));break;case"select":e.multiple=!!l.multiple,m=l.value,m!=null?rs(e,!!l.multiple,m,!1):l.defaultValue!=null&&rs(e,!!l.multiple,l.defaultValue,!0);break;default:typeof u.onClick=="function"&&(e.onclick=ur)}switch(a){case"button":case"input":case"select":case"textarea":l=!!l.autoFocus;break e;case"img":l=!0;break e;default:l=!1}}l&&(n.flags|=4)}n.ref!==null&&(n.flags|=512,n.flags|=2097152)}return st(n),null;case 6:if(e&&n.stateNode!=null)Uh(e,n,e.memoizedProps,l);else{if(typeof l!="string"&&n.stateNode===null)throw Error(r(166));if(a=On(pi.current),On(Ht.current),yr(n)){if(l=n.stateNode,a=n.memoizedProps,l[$t]=n,(m=l.nodeValue!==a)&&(e=xt,e!==null))switch(e.tag){case 3:cr(l.nodeValue,a,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&cr(l.nodeValue,a,(e.mode&1)!==0)}m&&(n.flags|=4)}else l=(a.nodeType===9?a:a.ownerDocument).createTextNode(l),l[$t]=n,n.stateNode=l}return st(n),null;case 13:if(Ee(Re),l=n.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(_e&&bt!==null&&(n.mode&1)!==0&&(n.flags&128)===0)Hd(),bs(),n.flags|=98560,m=!1;else if(m=yr(n),l!==null&&l.dehydrated!==null){if(e===null){if(!m)throw Error(r(318));if(m=n.memoizedState,m=m!==null?m.dehydrated:null,!m)throw Error(r(317));m[$t]=n}else bs(),(n.flags&128)===0&&(n.memoizedState=null),n.flags|=4;st(n),m=!1}else Rt!==null&&(Nl(Rt),Rt=null),m=!0;if(!m)return n.flags&65536?n:null}return(n.flags&128)!==0?(n.lanes=a,n):(l=l!==null,l!==(e!==null&&e.memoizedState!==null)&&l&&(n.child.flags|=8192,(n.mode&1)!==0&&(e===null||(Re.current&1)!==0?He===0&&(He=3):Pl())),n.updateQueue!==null&&(n.flags|=4),st(n),null);case 4:return Ss(),pl(e,n),e===null&&oi(n.stateNode.containerInfo),st(n),null;case 10:return Uo(n.type._context),st(n),null;case 17:return dt(n.type)&&hr(),st(n),null;case 19:if(Ee(Re),m=n.memoizedState,m===null)return st(n),null;if(l=(n.flags&128)!==0,y=m.rendering,y===null)if(l)xi(m,!1);else{if(He!==0||e!==null&&(e.flags&128)!==0)for(e=n.child;e!==null;){if(y=jr(e),y!==null){for(n.flags|=128,xi(m,!1),l=y.updateQueue,l!==null&&(n.updateQueue=l,n.flags|=4),n.subtreeFlags=0,l=a,a=n.child;a!==null;)m=a,e=l,m.flags&=14680066,y=m.alternate,y===null?(m.childLanes=0,m.lanes=e,m.child=null,m.subtreeFlags=0,m.memoizedProps=null,m.memoizedState=null,m.updateQueue=null,m.dependencies=null,m.stateNode=null):(m.childLanes=y.childLanes,m.lanes=y.lanes,m.child=y.child,m.subtreeFlags=0,m.deletions=null,m.memoizedProps=y.memoizedProps,m.memoizedState=y.memoizedState,m.updateQueue=y.updateQueue,m.type=y.type,e=y.dependencies,m.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),a=a.sibling;return Ce(Re,Re.current&1|2),n.child}e=e.sibling}m.tail!==null&&Fe()>Ps&&(n.flags|=128,l=!0,xi(m,!1),n.lanes=4194304)}else{if(!l)if(e=jr(y),e!==null){if(n.flags|=128,l=!0,a=e.updateQueue,a!==null&&(n.updateQueue=a,n.flags|=4),xi(m,!0),m.tail===null&&m.tailMode==="hidden"&&!y.alternate&&!_e)return st(n),null}else 2*Fe()-m.renderingStartTime>Ps&&a!==1073741824&&(n.flags|=128,l=!0,xi(m,!1),n.lanes=4194304);m.isBackwards?(y.sibling=n.child,n.child=y):(a=m.last,a!==null?a.sibling=y:n.child=y,m.last=y)}return m.tail!==null?(n=m.tail,m.rendering=n,m.tail=n.sibling,m.renderingStartTime=Fe(),n.sibling=null,a=Re.current,Ce(Re,l?a&1|2:a&1),n):(st(n),null);case 22:case 23:return Tl(),l=n.memoizedState!==null,e!==null&&e.memoizedState!==null!==l&&(n.flags|=8192),l&&(n.mode&1)!==0?(wt&1073741824)!==0&&(st(n),n.subtreeFlags&6&&(n.flags|=8192)):st(n),null;case 24:return null;case 25:return null}throw Error(r(156,n.tag))}function Jv(e,n){switch(Io(n),n.tag){case 1:return dt(n.type)&&hr(),e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 3:return Ss(),Ee(ut),Ee(tt),Xo(),e=n.flags,(e&65536)!==0&&(e&128)===0?(n.flags=e&-65537|128,n):null;case 5:return Ko(n),null;case 13:if(Ee(Re),e=n.memoizedState,e!==null&&e.dehydrated!==null){if(n.alternate===null)throw Error(r(340));bs()}return e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 19:return Ee(Re),null;case 4:return Ss(),null;case 10:return Uo(n.type._context),null;case 22:case 23:return Tl(),null;case 24:return null;default:return null}}var _r=!1,it=!1,Zv=typeof WeakSet=="function"?WeakSet:Set,Z=null;function Cs(e,n){var a=e.ref;if(a!==null)if(typeof a=="function")try{a(null)}catch(l){Ie(e,n,l)}else a.current=null}function fl(e,n,a){try{a()}catch(l){Ie(e,n,l)}}var Wh=!1;function ex(e,n){if(To=Ji,e=wd(),xo(e)){if("selectionStart"in e)var a={start:e.selectionStart,end:e.selectionEnd};else e:{a=(a=e.ownerDocument)&&a.defaultView||window;var l=a.getSelection&&a.getSelection();if(l&&l.rangeCount!==0){a=l.anchorNode;var u=l.anchorOffset,m=l.focusNode;l=l.focusOffset;try{a.nodeType,m.nodeType}catch{a=null;break e}var y=0,w=-1,C=-1,F=0,G=0,K=e,$=null;t:for(;;){for(var J;K!==a||u!==0&&K.nodeType!==3||(w=y+u),K!==m||l!==0&&K.nodeType!==3||(C=y+l),K.nodeType===3&&(y+=K.nodeValue.length),(J=K.firstChild)!==null;)$=K,K=J;for(;;){if(K===e)break t;if($===a&&++F===u&&(w=y),$===m&&++G===l&&(C=y),(J=K.nextSibling)!==null)break;K=$,$=K.parentNode}K=J}a=w===-1||C===-1?null:{start:w,end:C}}else a=null}a=a||{start:0,end:0}}else a=null;for(Po={focusedElem:e,selectionRange:a},Ji=!1,Z=n;Z!==null;)if(n=Z,e=n.child,(n.subtreeFlags&1028)!==0&&e!==null)e.return=n,Z=e;else for(;Z!==null;){n=Z;try{var ee=n.alternate;if((n.flags&1024)!==0)switch(n.tag){case 0:case 11:case 15:break;case 1:if(ee!==null){var ne=ee.memoizedProps,Be=ee.memoizedState,_=n.stateNode,A=_.getSnapshotBeforeUpdate(n.elementType===n.type?ne:Lt(n.type,ne),Be);_.__reactInternalSnapshotBeforeUpdate=A}break;case 3:var R=n.stateNode.containerInfo;R.nodeType===1?R.textContent="":R.nodeType===9&&R.documentElement&&R.removeChild(R.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(r(163))}}catch(q){Ie(n,n.return,q)}if(e=n.sibling,e!==null){e.return=n.return,Z=e;break}Z=n.return}return ee=Wh,Wh=!1,ee}function bi(e,n,a){var l=n.updateQueue;if(l=l!==null?l.lastEffect:null,l!==null){var u=l=l.next;do{if((u.tag&e)===e){var m=u.destroy;u.destroy=void 0,m!==void 0&&fl(n,a,m)}u=u.next}while(u!==l)}}function Dr(e,n){if(n=n.updateQueue,n=n!==null?n.lastEffect:null,n!==null){var a=n=n.next;do{if((a.tag&e)===e){var l=a.create;a.destroy=l()}a=a.next}while(a!==n)}}function gl(e){var n=e.ref;if(n!==null){var a=e.stateNode;switch(e.tag){case 5:e=a;break;default:e=a}typeof n=="function"?n(e):n.current=e}}function $h(e){var n=e.alternate;n!==null&&(e.alternate=null,$h(n)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(n=e.stateNode,n!==null&&(delete n[$t],delete n[ci],delete n[_o],delete n[Iv],delete n[Vv])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function Hh(e){return e.tag===5||e.tag===3||e.tag===4}function Gh(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||Hh(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function yl(e,n,a){var l=e.tag;if(l===5||l===6)e=e.stateNode,n?a.nodeType===8?a.parentNode.insertBefore(e,n):a.insertBefore(e,n):(a.nodeType===8?(n=a.parentNode,n.insertBefore(e,a)):(n=a,n.appendChild(e)),a=a._reactRootContainer,a!=null||n.onclick!==null||(n.onclick=ur));else if(l!==4&&(e=e.child,e!==null))for(yl(e,n,a),e=e.sibling;e!==null;)yl(e,n,a),e=e.sibling}function vl(e,n,a){var l=e.tag;if(l===5||l===6)e=e.stateNode,n?a.insertBefore(e,n):a.appendChild(e);else if(l!==4&&(e=e.child,e!==null))for(vl(e,n,a),e=e.sibling;e!==null;)vl(e,n,a),e=e.sibling}var Je=null,It=!1;function kn(e,n,a){for(a=a.child;a!==null;)Kh(e,n,a),a=a.sibling}function Kh(e,n,a){if(Wt&&typeof Wt.onCommitFiberUnmount=="function")try{Wt.onCommitFiberUnmount(Gi,a)}catch{}switch(a.tag){case 5:it||Cs(a,n);case 6:var l=Je,u=It;Je=null,kn(e,n,a),Je=l,It=u,Je!==null&&(It?(e=Je,a=a.stateNode,e.nodeType===8?e.parentNode.removeChild(a):e.removeChild(a)):Je.removeChild(a.stateNode));break;case 18:Je!==null&&(It?(e=Je,a=a.stateNode,e.nodeType===8?Mo(e.parentNode,a):e.nodeType===1&&Mo(e,a),Js(e)):Mo(Je,a.stateNode));break;case 4:l=Je,u=It,Je=a.stateNode.containerInfo,It=!0,kn(e,n,a),Je=l,It=u;break;case 0:case 11:case 14:case 15:if(!it&&(l=a.updateQueue,l!==null&&(l=l.lastEffect,l!==null))){u=l=l.next;do{var m=u,y=m.destroy;m=m.tag,y!==void 0&&((m&2)!==0||(m&4)!==0)&&fl(a,n,y),u=u.next}while(u!==l)}kn(e,n,a);break;case 1:if(!it&&(Cs(a,n),l=a.stateNode,typeof l.componentWillUnmount=="function"))try{l.props=a.memoizedProps,l.state=a.memoizedState,l.componentWillUnmount()}catch(w){Ie(a,n,w)}kn(e,n,a);break;case 21:kn(e,n,a);break;case 22:a.mode&1?(it=(l=it)||a.memoizedState!==null,kn(e,n,a),it=l):kn(e,n,a);break;default:kn(e,n,a)}}function qh(e){var n=e.updateQueue;if(n!==null){e.updateQueue=null;var a=e.stateNode;a===null&&(a=e.stateNode=new Zv),n.forEach(function(l){var u=cx.bind(null,e,l);a.has(l)||(a.add(l),l.then(u,u))})}}function Vt(e,n){var a=n.deletions;if(a!==null)for(var l=0;l<a.length;l++){var u=a[l];try{var m=e,y=n,w=y;e:for(;w!==null;){switch(w.tag){case 5:Je=w.stateNode,It=!1;break e;case 3:Je=w.stateNode.containerInfo,It=!0;break e;case 4:Je=w.stateNode.containerInfo,It=!0;break e}w=w.return}if(Je===null)throw Error(r(160));Kh(m,y,u),Je=null,It=!1;var C=u.alternate;C!==null&&(C.return=null),u.return=null}catch(F){Ie(u,n,F)}}if(n.subtreeFlags&12854)for(n=n.child;n!==null;)Xh(n,e),n=n.sibling}function Xh(e,n){var a=e.alternate,l=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(Vt(n,e),Kt(e),l&4){try{bi(3,e,e.return),Dr(3,e)}catch(ne){Ie(e,e.return,ne)}try{bi(5,e,e.return)}catch(ne){Ie(e,e.return,ne)}}break;case 1:Vt(n,e),Kt(e),l&512&&a!==null&&Cs(a,a.return);break;case 5:if(Vt(n,e),Kt(e),l&512&&a!==null&&Cs(a,a.return),e.flags&32){var u=e.stateNode;try{zs(u,"")}catch(ne){Ie(e,e.return,ne)}}if(l&4&&(u=e.stateNode,u!=null)){var m=e.memoizedProps,y=a!==null?a.memoizedProps:m,w=e.type,C=e.updateQueue;if(e.updateQueue=null,C!==null)try{w==="input"&&m.type==="radio"&&m.name!=null&&ju(u,m),qa(w,y);var F=qa(w,m);for(y=0;y<C.length;y+=2){var G=C[y],K=C[y+1];G==="style"?Mu(u,K):G==="dangerouslySetInnerHTML"?Au(u,K):G==="children"?zs(u,K):L(u,G,K,F)}switch(w){case"input":Wa(u,m);break;case"textarea":Cu(u,m);break;case"select":var $=u._wrapperState.wasMultiple;u._wrapperState.wasMultiple=!!m.multiple;var J=m.value;J!=null?rs(u,!!m.multiple,J,!1):$!==!!m.multiple&&(m.defaultValue!=null?rs(u,!!m.multiple,m.defaultValue,!0):rs(u,!!m.multiple,m.multiple?[]:"",!1))}u[ci]=m}catch(ne){Ie(e,e.return,ne)}}break;case 6:if(Vt(n,e),Kt(e),l&4){if(e.stateNode===null)throw Error(r(162));u=e.stateNode,m=e.memoizedProps;try{u.nodeValue=m}catch(ne){Ie(e,e.return,ne)}}break;case 3:if(Vt(n,e),Kt(e),l&4&&a!==null&&a.memoizedState.isDehydrated)try{Js(n.containerInfo)}catch(ne){Ie(e,e.return,ne)}break;case 4:Vt(n,e),Kt(e);break;case 13:Vt(n,e),Kt(e),u=e.child,u.flags&8192&&(m=u.memoizedState!==null,u.stateNode.isHidden=m,!m||u.alternate!==null&&u.alternate.memoizedState!==null||(wl=Fe())),l&4&&qh(e);break;case 22:if(G=a!==null&&a.memoizedState!==null,e.mode&1?(it=(F=it)||G,Vt(n,e),it=F):Vt(n,e),Kt(e),l&8192){if(F=e.memoizedState!==null,(e.stateNode.isHidden=F)&&!G&&(e.mode&1)!==0)for(Z=e,G=e.child;G!==null;){for(K=Z=G;Z!==null;){switch($=Z,J=$.child,$.tag){case 0:case 11:case 14:case 15:bi(4,$,$.return);break;case 1:Cs($,$.return);var ee=$.stateNode;if(typeof ee.componentWillUnmount=="function"){l=$,a=$.return;try{n=l,ee.props=n.memoizedProps,ee.state=n.memoizedState,ee.componentWillUnmount()}catch(ne){Ie(l,a,ne)}}break;case 5:Cs($,$.return);break;case 22:if($.memoizedState!==null){Jh(K);continue}}J!==null?(J.return=$,Z=J):Jh(K)}G=G.sibling}e:for(G=null,K=e;;){if(K.tag===5){if(G===null){G=K;try{u=K.stateNode,F?(m=u.style,typeof m.setProperty=="function"?m.setProperty("display","none","important"):m.display="none"):(w=K.stateNode,C=K.memoizedProps.style,y=C!=null&&C.hasOwnProperty("display")?C.display:null,w.style.display=Eu("display",y))}catch(ne){Ie(e,e.return,ne)}}}else if(K.tag===6){if(G===null)try{K.stateNode.nodeValue=F?"":K.memoizedProps}catch(ne){Ie(e,e.return,ne)}}else if((K.tag!==22&&K.tag!==23||K.memoizedState===null||K===e)&&K.child!==null){K.child.return=K,K=K.child;continue}if(K===e)break e;for(;K.sibling===null;){if(K.return===null||K.return===e)break e;G===K&&(G=null),K=K.return}G===K&&(G=null),K.sibling.return=K.return,K=K.sibling}}break;case 19:Vt(n,e),Kt(e),l&4&&qh(e);break;case 21:break;default:Vt(n,e),Kt(e)}}function Kt(e){var n=e.flags;if(n&2){try{e:{for(var a=e.return;a!==null;){if(Hh(a)){var l=a;break e}a=a.return}throw Error(r(160))}switch(l.tag){case 5:var u=l.stateNode;l.flags&32&&(zs(u,""),l.flags&=-33);var m=Gh(e);vl(e,m,u);break;case 3:case 4:var y=l.stateNode.containerInfo,w=Gh(e);yl(e,w,y);break;default:throw Error(r(161))}}catch(C){Ie(e,e.return,C)}e.flags&=-3}n&4096&&(e.flags&=-4097)}function tx(e,n,a){Z=e,Yh(e)}function Yh(e,n,a){for(var l=(e.mode&1)!==0;Z!==null;){var u=Z,m=u.child;if(u.tag===22&&l){var y=u.memoizedState!==null||_r;if(!y){var w=u.alternate,C=w!==null&&w.memoizedState!==null||it;w=_r;var F=it;if(_r=y,(it=C)&&!F)for(Z=u;Z!==null;)y=Z,C=y.child,y.tag===22&&y.memoizedState!==null?Zh(u):C!==null?(C.return=y,Z=C):Zh(u);for(;m!==null;)Z=m,Yh(m),m=m.sibling;Z=u,_r=w,it=F}Qh(e)}else(u.subtreeFlags&8772)!==0&&m!==null?(m.return=u,Z=m):Qh(e)}}function Qh(e){for(;Z!==null;){var n=Z;if((n.flags&8772)!==0){var a=n.alternate;try{if((n.flags&8772)!==0)switch(n.tag){case 0:case 11:case 15:it||Dr(5,n);break;case 1:var l=n.stateNode;if(n.flags&4&&!it)if(a===null)l.componentDidMount();else{var u=n.elementType===n.type?a.memoizedProps:Lt(n.type,a.memoizedProps);l.componentDidUpdate(u,a.memoizedState,l.__reactInternalSnapshotBeforeUpdate)}var m=n.updateQueue;m!==null&&Jd(n,m,l);break;case 3:var y=n.updateQueue;if(y!==null){if(a=null,n.child!==null)switch(n.child.tag){case 5:a=n.child.stateNode;break;case 1:a=n.child.stateNode}Jd(n,y,a)}break;case 5:var w=n.stateNode;if(a===null&&n.flags&4){a=w;var C=n.memoizedProps;switch(n.type){case"button":case"input":case"select":case"textarea":C.autoFocus&&a.focus();break;case"img":C.src&&(a.src=C.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(n.memoizedState===null){var F=n.alternate;if(F!==null){var G=F.memoizedState;if(G!==null){var K=G.dehydrated;K!==null&&Js(K)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(r(163))}it||n.flags&512&&gl(n)}catch($){Ie(n,n.return,$)}}if(n===e){Z=null;break}if(a=n.sibling,a!==null){a.return=n.return,Z=a;break}Z=n.return}}function Jh(e){for(;Z!==null;){var n=Z;if(n===e){Z=null;break}var a=n.sibling;if(a!==null){a.return=n.return,Z=a;break}Z=n.return}}function Zh(e){for(;Z!==null;){var n=Z;try{switch(n.tag){case 0:case 11:case 15:var a=n.return;try{Dr(4,n)}catch(C){Ie(n,a,C)}break;case 1:var l=n.stateNode;if(typeof l.componentDidMount=="function"){var u=n.return;try{l.componentDidMount()}catch(C){Ie(n,u,C)}}var m=n.return;try{gl(n)}catch(C){Ie(n,m,C)}break;case 5:var y=n.return;try{gl(n)}catch(C){Ie(n,y,C)}}}catch(C){Ie(n,n.return,C)}if(n===e){Z=null;break}var w=n.sibling;if(w!==null){w.return=n.return,Z=w;break}Z=n.return}}var nx=Math.ceil,Rr=I.ReactCurrentDispatcher,xl=I.ReactCurrentOwner,At=I.ReactCurrentBatchConfig,fe=0,Ye=null,Ue=null,Ze=0,wt=0,Ts=yn(0),He=0,wi=null,Un=0,Lr=0,bl=0,ki=null,mt=null,wl=0,Ps=1/0,an=null,Ir=!1,kl=null,jn=null,Vr=!1,Sn=null,Fr=0,ji=0,jl=null,Br=-1,Or=0;function ot(){return(fe&6)!==0?Fe():Br!==-1?Br:Br=Fe()}function Nn(e){return(e.mode&1)===0?1:(fe&2)!==0&&Ze!==0?Ze&-Ze:Bv.transition!==null?(Or===0&&(Or=Gu()),Or):(e=we,e!==0||(e=window.event,e=e===void 0?16:td(e.type)),e)}function Ft(e,n,a,l){if(50<ji)throw ji=0,jl=null,Error(r(185));Ks(e,a,l),((fe&2)===0||e!==Ye)&&(e===Ye&&((fe&2)===0&&(Lr|=a),He===4&&Cn(e,Ze)),pt(e,l),a===1&&fe===0&&(n.mode&1)===0&&(Ps=Fe()+500,pr&&xn()))}function pt(e,n){var a=e.callbackNode;By(e,n);var l=Xi(e,e===Ye?Ze:0);if(l===0)a!==null&&Wu(a),e.callbackNode=null,e.callbackPriority=0;else if(n=l&-l,e.callbackPriority!==n){if(a!=null&&Wu(a),n===1)e.tag===0?Fv(tm.bind(null,e)):Od(tm.bind(null,e)),Rv(function(){(fe&6)===0&&xn()}),a=null;else{switch(Ku(l)){case 1:a=to;break;case 4:a=$u;break;case 16:a=Hi;break;case 536870912:a=Hu;break;default:a=Hi}a=cm(a,em.bind(null,e))}e.callbackPriority=n,e.callbackNode=a}}function em(e,n){if(Br=-1,Or=0,(fe&6)!==0)throw Error(r(327));var a=e.callbackNode;if(As()&&e.callbackNode!==a)return null;var l=Xi(e,e===Ye?Ze:0);if(l===0)return null;if((l&30)!==0||(l&e.expiredLanes)!==0||n)n=zr(e,l);else{n=l;var u=fe;fe|=2;var m=sm();(Ye!==e||Ze!==n)&&(an=null,Ps=Fe()+500,$n(e,n));do try{rx();break}catch(w){nm(e,w)}while(!0);zo(),Rr.current=m,fe=u,Ue!==null?n=0:(Ye=null,Ze=0,n=He)}if(n!==0){if(n===2&&(u=no(e),u!==0&&(l=u,n=Sl(e,u))),n===1)throw a=wi,$n(e,0),Cn(e,l),pt(e,Fe()),a;if(n===6)Cn(e,l);else{if(u=e.current.alternate,(l&30)===0&&!sx(u)&&(n=zr(e,l),n===2&&(m=no(e),m!==0&&(l=m,n=Sl(e,m))),n===1))throw a=wi,$n(e,0),Cn(e,l),pt(e,Fe()),a;switch(e.finishedWork=u,e.finishedLanes=l,n){case 0:case 1:throw Error(r(345));case 2:Hn(e,mt,an);break;case 3:if(Cn(e,l),(l&130023424)===l&&(n=wl+500-Fe(),10<n)){if(Xi(e,0)!==0)break;if(u=e.suspendedLanes,(u&l)!==l){ot(),e.pingedLanes|=e.suspendedLanes&u;break}e.timeoutHandle=Eo(Hn.bind(null,e,mt,an),n);break}Hn(e,mt,an);break;case 4:if(Cn(e,l),(l&4194240)===l)break;for(n=e.eventTimes,u=-1;0<l;){var y=31-_t(l);m=1<<y,y=n[y],y>u&&(u=y),l&=~m}if(l=u,l=Fe()-l,l=(120>l?120:480>l?480:1080>l?1080:1920>l?1920:3e3>l?3e3:4320>l?4320:1960*nx(l/1960))-l,10<l){e.timeoutHandle=Eo(Hn.bind(null,e,mt,an),l);break}Hn(e,mt,an);break;case 5:Hn(e,mt,an);break;default:throw Error(r(329))}}}return pt(e,Fe()),e.callbackNode===a?em.bind(null,e):null}function Sl(e,n){var a=ki;return e.current.memoizedState.isDehydrated&&($n(e,n).flags|=256),e=zr(e,n),e!==2&&(n=mt,mt=a,n!==null&&Nl(n)),e}function Nl(e){mt===null?mt=e:mt.push.apply(mt,e)}function sx(e){for(var n=e;;){if(n.flags&16384){var a=n.updateQueue;if(a!==null&&(a=a.stores,a!==null))for(var l=0;l<a.length;l++){var u=a[l],m=u.getSnapshot;u=u.value;try{if(!Dt(m(),u))return!1}catch{return!1}}}if(a=n.child,n.subtreeFlags&16384&&a!==null)a.return=n,n=a;else{if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return!0;n=n.return}n.sibling.return=n.return,n=n.sibling}}return!0}function Cn(e,n){for(n&=~bl,n&=~Lr,e.suspendedLanes|=n,e.pingedLanes&=~n,e=e.expirationTimes;0<n;){var a=31-_t(n),l=1<<a;e[a]=-1,n&=~l}}function tm(e){if((fe&6)!==0)throw Error(r(327));As();var n=Xi(e,0);if((n&1)===0)return pt(e,Fe()),null;var a=zr(e,n);if(e.tag!==0&&a===2){var l=no(e);l!==0&&(n=l,a=Sl(e,l))}if(a===1)throw a=wi,$n(e,0),Cn(e,n),pt(e,Fe()),a;if(a===6)throw Error(r(345));return e.finishedWork=e.current.alternate,e.finishedLanes=n,Hn(e,mt,an),pt(e,Fe()),null}function Cl(e,n){var a=fe;fe|=1;try{return e(n)}finally{fe=a,fe===0&&(Ps=Fe()+500,pr&&xn())}}function Wn(e){Sn!==null&&Sn.tag===0&&(fe&6)===0&&As();var n=fe;fe|=1;var a=At.transition,l=we;try{if(At.transition=null,we=1,e)return e()}finally{we=l,At.transition=a,fe=n,(fe&6)===0&&xn()}}function Tl(){wt=Ts.current,Ee(Ts)}function $n(e,n){e.finishedWork=null,e.finishedLanes=0;var a=e.timeoutHandle;if(a!==-1&&(e.timeoutHandle=-1,Dv(a)),Ue!==null)for(a=Ue.return;a!==null;){var l=a;switch(Io(l),l.tag){case 1:l=l.type.childContextTypes,l!=null&&hr();break;case 3:Ss(),Ee(ut),Ee(tt),Xo();break;case 5:Ko(l);break;case 4:Ss();break;case 13:Ee(Re);break;case 19:Ee(Re);break;case 10:Uo(l.type._context);break;case 22:case 23:Tl()}a=a.return}if(Ye=e,Ue=e=Tn(e.current,null),Ze=wt=n,He=0,wi=null,bl=Lr=Un=0,mt=ki=null,Bn!==null){for(n=0;n<Bn.length;n++)if(a=Bn[n],l=a.interleaved,l!==null){a.interleaved=null;var u=l.next,m=a.pending;if(m!==null){var y=m.next;m.next=u,l.next=y}a.pending=l}Bn=null}return e}function nm(e,n){do{var a=Ue;try{if(zo(),Sr.current=Pr,Nr){for(var l=Le.memoizedState;l!==null;){var u=l.queue;u!==null&&(u.pending=null),l=l.next}Nr=!1}if(zn=0,Xe=$e=Le=null,fi=!1,gi=0,xl.current=null,a===null||a.return===null){He=1,wi=n,Ue=null;break}e:{var m=e,y=a.return,w=a,C=n;if(n=Ze,w.flags|=32768,C!==null&&typeof C=="object"&&typeof C.then=="function"){var F=C,G=w,K=G.tag;if((G.mode&1)===0&&(K===0||K===11||K===15)){var $=G.alternate;$?(G.updateQueue=$.updateQueue,G.memoizedState=$.memoizedState,G.lanes=$.lanes):(G.updateQueue=null,G.memoizedState=null)}var J=Th(y);if(J!==null){J.flags&=-257,Ph(J,y,w,m,n),J.mode&1&&Ch(m,F,n),n=J,C=F;var ee=n.updateQueue;if(ee===null){var ne=new Set;ne.add(C),n.updateQueue=ne}else ee.add(C);break e}else{if((n&1)===0){Ch(m,F,n),Pl();break e}C=Error(r(426))}}else if(_e&&w.mode&1){var Be=Th(y);if(Be!==null){(Be.flags&65536)===0&&(Be.flags|=256),Ph(Be,y,w,m,n),Bo(Ns(C,w));break e}}m=C=Ns(C,w),He!==4&&(He=2),ki===null?ki=[m]:ki.push(m),m=y;do{switch(m.tag){case 3:m.flags|=65536,n&=-n,m.lanes|=n;var _=Sh(m,C,n);Qd(m,_);break e;case 1:w=C;var A=m.type,R=m.stateNode;if((m.flags&128)===0&&(typeof A.getDerivedStateFromError=="function"||R!==null&&typeof R.componentDidCatch=="function"&&(jn===null||!jn.has(R)))){m.flags|=65536,n&=-n,m.lanes|=n;var q=Nh(m,w,n);Qd(m,q);break e}}m=m.return}while(m!==null)}rm(a)}catch(se){n=se,Ue===a&&a!==null&&(Ue=a=a.return);continue}break}while(!0)}function sm(){var e=Rr.current;return Rr.current=Pr,e===null?Pr:e}function Pl(){(He===0||He===3||He===2)&&(He=4),Ye===null||(Un&268435455)===0&&(Lr&268435455)===0||Cn(Ye,Ze)}function zr(e,n){var a=fe;fe|=2;var l=sm();(Ye!==e||Ze!==n)&&(an=null,$n(e,n));do try{ix();break}catch(u){nm(e,u)}while(!0);if(zo(),fe=a,Rr.current=l,Ue!==null)throw Error(r(261));return Ye=null,Ze=0,He}function ix(){for(;Ue!==null;)im(Ue)}function rx(){for(;Ue!==null&&!Ey();)im(Ue)}function im(e){var n=lm(e.alternate,e,wt);e.memoizedProps=e.pendingProps,n===null?rm(e):Ue=n,xl.current=null}function rm(e){var n=e;do{var a=n.alternate;if(e=n.return,(n.flags&32768)===0){if(a=Qv(a,n,wt),a!==null){Ue=a;return}}else{if(a=Jv(a,n),a!==null){a.flags&=32767,Ue=a;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{He=6,Ue=null;return}}if(n=n.sibling,n!==null){Ue=n;return}Ue=n=e}while(n!==null);He===0&&(He=5)}function Hn(e,n,a){var l=we,u=At.transition;try{At.transition=null,we=1,ax(e,n,a,l)}finally{At.transition=u,we=l}return null}function ax(e,n,a,l){do As();while(Sn!==null);if((fe&6)!==0)throw Error(r(327));a=e.finishedWork;var u=e.finishedLanes;if(a===null)return null;if(e.finishedWork=null,e.finishedLanes=0,a===e.current)throw Error(r(177));e.callbackNode=null,e.callbackPriority=0;var m=a.lanes|a.childLanes;if(Oy(e,m),e===Ye&&(Ue=Ye=null,Ze=0),(a.subtreeFlags&2064)===0&&(a.flags&2064)===0||Vr||(Vr=!0,cm(Hi,function(){return As(),null})),m=(a.flags&15990)!==0,(a.subtreeFlags&15990)!==0||m){m=At.transition,At.transition=null;var y=we;we=1;var w=fe;fe|=4,xl.current=null,ex(e,a),Xh(a,e),Cv(Po),Ji=!!To,Po=To=null,e.current=a,tx(a),My(),fe=w,we=y,At.transition=m}else e.current=a;if(Vr&&(Vr=!1,Sn=e,Fr=u),m=e.pendingLanes,m===0&&(jn=null),Ry(a.stateNode),pt(e,Fe()),n!==null)for(l=e.onRecoverableError,a=0;a<n.length;a++)u=n[a],l(u.value,{componentStack:u.stack,digest:u.digest});if(Ir)throw Ir=!1,e=kl,kl=null,e;return(Fr&1)!==0&&e.tag!==0&&As(),m=e.pendingLanes,(m&1)!==0?e===jl?ji++:(ji=0,jl=e):ji=0,xn(),null}function As(){if(Sn!==null){var e=Ku(Fr),n=At.transition,a=we;try{if(At.transition=null,we=16>e?16:e,Sn===null)var l=!1;else{if(e=Sn,Sn=null,Fr=0,(fe&6)!==0)throw Error(r(331));var u=fe;for(fe|=4,Z=e.current;Z!==null;){var m=Z,y=m.child;if((Z.flags&16)!==0){var w=m.deletions;if(w!==null){for(var C=0;C<w.length;C++){var F=w[C];for(Z=F;Z!==null;){var G=Z;switch(G.tag){case 0:case 11:case 15:bi(8,G,m)}var K=G.child;if(K!==null)K.return=G,Z=K;else for(;Z!==null;){G=Z;var $=G.sibling,J=G.return;if($h(G),G===F){Z=null;break}if($!==null){$.return=J,Z=$;break}Z=J}}}var ee=m.alternate;if(ee!==null){var ne=ee.child;if(ne!==null){ee.child=null;do{var Be=ne.sibling;ne.sibling=null,ne=Be}while(ne!==null)}}Z=m}}if((m.subtreeFlags&2064)!==0&&y!==null)y.return=m,Z=y;else e:for(;Z!==null;){if(m=Z,(m.flags&2048)!==0)switch(m.tag){case 0:case 11:case 15:bi(9,m,m.return)}var _=m.sibling;if(_!==null){_.return=m.return,Z=_;break e}Z=m.return}}var A=e.current;for(Z=A;Z!==null;){y=Z;var R=y.child;if((y.subtreeFlags&2064)!==0&&R!==null)R.return=y,Z=R;else e:for(y=A;Z!==null;){if(w=Z,(w.flags&2048)!==0)try{switch(w.tag){case 0:case 11:case 15:Dr(9,w)}}catch(se){Ie(w,w.return,se)}if(w===y){Z=null;break e}var q=w.sibling;if(q!==null){q.return=w.return,Z=q;break e}Z=w.return}}if(fe=u,xn(),Wt&&typeof Wt.onPostCommitFiberRoot=="function")try{Wt.onPostCommitFiberRoot(Gi,e)}catch{}l=!0}return l}finally{we=a,At.transition=n}}return!1}function am(e,n,a){n=Ns(a,n),n=Sh(e,n,1),e=wn(e,n,1),n=ot(),e!==null&&(Ks(e,1,n),pt(e,n))}function Ie(e,n,a){if(e.tag===3)am(e,e,a);else for(;n!==null;){if(n.tag===3){am(n,e,a);break}else if(n.tag===1){var l=n.stateNode;if(typeof n.type.getDerivedStateFromError=="function"||typeof l.componentDidCatch=="function"&&(jn===null||!jn.has(l))){e=Ns(a,e),e=Nh(n,e,1),n=wn(n,e,1),e=ot(),n!==null&&(Ks(n,1,e),pt(n,e));break}}n=n.return}}function ox(e,n,a){var l=e.pingCache;l!==null&&l.delete(n),n=ot(),e.pingedLanes|=e.suspendedLanes&a,Ye===e&&(Ze&a)===a&&(He===4||He===3&&(Ze&130023424)===Ze&&500>Fe()-wl?$n(e,0):bl|=a),pt(e,n)}function om(e,n){n===0&&((e.mode&1)===0?n=1:(n=qi,qi<<=1,(qi&130023424)===0&&(qi=4194304)));var a=ot();e=nn(e,n),e!==null&&(Ks(e,n,a),pt(e,a))}function lx(e){var n=e.memoizedState,a=0;n!==null&&(a=n.retryLane),om(e,a)}function cx(e,n){var a=0;switch(e.tag){case 13:var l=e.stateNode,u=e.memoizedState;u!==null&&(a=u.retryLane);break;case 19:l=e.stateNode;break;default:throw Error(r(314))}l!==null&&l.delete(n),om(e,a)}var lm;lm=function(e,n,a){if(e!==null)if(e.memoizedProps!==n.pendingProps||ut.current)ht=!0;else{if((e.lanes&a)===0&&(n.flags&128)===0)return ht=!1,Yv(e,n,a);ht=(e.flags&131072)!==0}else ht=!1,_e&&(n.flags&1048576)!==0&&zd(n,gr,n.index);switch(n.lanes=0,n.tag){case 2:var l=n.type;Mr(e,n),e=n.pendingProps;var u=ys(n,tt.current);js(n,a),u=Jo(null,n,l,e,u,a);var m=Zo();return n.flags|=1,typeof u=="object"&&u!==null&&typeof u.render=="function"&&u.$$typeof===void 0?(n.tag=1,n.memoizedState=null,n.updateQueue=null,dt(l)?(m=!0,mr(n)):m=!1,n.memoizedState=u.state!==null&&u.state!==void 0?u.state:null,Ho(n),u.updater=Ar,n.stateNode=u,u._reactInternals=n,rl(n,l,e,a),n=cl(null,n,l,!0,m,a)):(n.tag=0,_e&&m&&Lo(n),at(null,n,u,a),n=n.child),n;case 16:l=n.elementType;e:{switch(Mr(e,n),e=n.pendingProps,u=l._init,l=u(l._payload),n.type=l,u=n.tag=dx(l),e=Lt(l,e),u){case 0:n=ll(null,n,l,e,a);break e;case 1:n=Rh(null,n,l,e,a);break e;case 11:n=Ah(null,n,l,e,a);break e;case 14:n=Eh(null,n,l,Lt(l.type,e),a);break e}throw Error(r(306,l,""))}return n;case 0:return l=n.type,u=n.pendingProps,u=n.elementType===l?u:Lt(l,u),ll(e,n,l,u,a);case 1:return l=n.type,u=n.pendingProps,u=n.elementType===l?u:Lt(l,u),Rh(e,n,l,u,a);case 3:e:{if(Lh(n),e===null)throw Error(r(387));l=n.pendingProps,m=n.memoizedState,u=m.element,Yd(e,n),kr(n,l,null,a);var y=n.memoizedState;if(l=y.element,m.isDehydrated)if(m={element:l,isDehydrated:!1,cache:y.cache,pendingSuspenseBoundaries:y.pendingSuspenseBoundaries,transitions:y.transitions},n.updateQueue.baseState=m,n.memoizedState=m,n.flags&256){u=Ns(Error(r(423)),n),n=Ih(e,n,l,a,u);break e}else if(l!==u){u=Ns(Error(r(424)),n),n=Ih(e,n,l,a,u);break e}else for(bt=gn(n.stateNode.containerInfo.firstChild),xt=n,_e=!0,Rt=null,a=qd(n,null,l,a),n.child=a;a;)a.flags=a.flags&-3|4096,a=a.sibling;else{if(bs(),l===u){n=rn(e,n,a);break e}at(e,n,l,a)}n=n.child}return n;case 5:return Zd(n),e===null&&Fo(n),l=n.type,u=n.pendingProps,m=e!==null?e.memoizedProps:null,y=u.children,Ao(l,u)?y=null:m!==null&&Ao(l,m)&&(n.flags|=32),Dh(e,n),at(e,n,y,a),n.child;case 6:return e===null&&Fo(n),null;case 13:return Vh(e,n,a);case 4:return Go(n,n.stateNode.containerInfo),l=n.pendingProps,e===null?n.child=ws(n,null,l,a):at(e,n,l,a),n.child;case 11:return l=n.type,u=n.pendingProps,u=n.elementType===l?u:Lt(l,u),Ah(e,n,l,u,a);case 7:return at(e,n,n.pendingProps,a),n.child;case 8:return at(e,n,n.pendingProps.children,a),n.child;case 12:return at(e,n,n.pendingProps.children,a),n.child;case 10:e:{if(l=n.type._context,u=n.pendingProps,m=n.memoizedProps,y=u.value,Ce(xr,l._currentValue),l._currentValue=y,m!==null)if(Dt(m.value,y)){if(m.children===u.children&&!ut.current){n=rn(e,n,a);break e}}else for(m=n.child,m!==null&&(m.return=n);m!==null;){var w=m.dependencies;if(w!==null){y=m.child;for(var C=w.firstContext;C!==null;){if(C.context===l){if(m.tag===1){C=sn(-1,a&-a),C.tag=2;var F=m.updateQueue;if(F!==null){F=F.shared;var G=F.pending;G===null?C.next=C:(C.next=G.next,G.next=C),F.pending=C}}m.lanes|=a,C=m.alternate,C!==null&&(C.lanes|=a),Wo(m.return,a,n),w.lanes|=a;break}C=C.next}}else if(m.tag===10)y=m.type===n.type?null:m.child;else if(m.tag===18){if(y=m.return,y===null)throw Error(r(341));y.lanes|=a,w=y.alternate,w!==null&&(w.lanes|=a),Wo(y,a,n),y=m.sibling}else y=m.child;if(y!==null)y.return=m;else for(y=m;y!==null;){if(y===n){y=null;break}if(m=y.sibling,m!==null){m.return=y.return,y=m;break}y=y.return}m=y}at(e,n,u.children,a),n=n.child}return n;case 9:return u=n.type,l=n.pendingProps.children,js(n,a),u=Tt(u),l=l(u),n.flags|=1,at(e,n,l,a),n.child;case 14:return l=n.type,u=Lt(l,n.pendingProps),u=Lt(l.type,u),Eh(e,n,l,u,a);case 15:return Mh(e,n,n.type,n.pendingProps,a);case 17:return l=n.type,u=n.pendingProps,u=n.elementType===l?u:Lt(l,u),Mr(e,n),n.tag=1,dt(l)?(e=!0,mr(n)):e=!1,js(n,a),kh(n,l,u),rl(n,l,u,a),cl(null,n,l,!0,e,a);case 19:return Bh(e,n,a);case 22:return _h(e,n,a)}throw Error(r(156,n.tag))};function cm(e,n){return Uu(e,n)}function ux(e,n,a,l){this.tag=e,this.key=a,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=n,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=l,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function Et(e,n,a,l){return new ux(e,n,a,l)}function Al(e){return e=e.prototype,!(!e||!e.isReactComponent)}function dx(e){if(typeof e=="function")return Al(e)?1:0;if(e!=null){if(e=e.$$typeof,e===ue)return 11;if(e===De)return 14}return 2}function Tn(e,n){var a=e.alternate;return a===null?(a=Et(e.tag,n,e.key,e.mode),a.elementType=e.elementType,a.type=e.type,a.stateNode=e.stateNode,a.alternate=e,e.alternate=a):(a.pendingProps=n,a.type=e.type,a.flags=0,a.subtreeFlags=0,a.deletions=null),a.flags=e.flags&14680064,a.childLanes=e.childLanes,a.lanes=e.lanes,a.child=e.child,a.memoizedProps=e.memoizedProps,a.memoizedState=e.memoizedState,a.updateQueue=e.updateQueue,n=e.dependencies,a.dependencies=n===null?null:{lanes:n.lanes,firstContext:n.firstContext},a.sibling=e.sibling,a.index=e.index,a.ref=e.ref,a}function Ur(e,n,a,l,u,m){var y=2;if(l=e,typeof e=="function")Al(e)&&(y=1);else if(typeof e=="string")y=5;else e:switch(e){case V:return Gn(a.children,u,m,n);case z:y=8,u|=8;break;case re:return e=Et(12,a,n,u|2),e.elementType=re,e.lanes=m,e;case ie:return e=Et(13,a,n,u),e.elementType=ie,e.lanes=m,e;case Se:return e=Et(19,a,n,u),e.elementType=Se,e.lanes=m,e;case Q:return Wr(a,u,m,n);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case Y:y=10;break e;case ce:y=9;break e;case ue:y=11;break e;case De:y=14;break e;case Pe:y=16,l=null;break e}throw Error(r(130,e==null?e:typeof e,""))}return n=Et(y,a,n,u),n.elementType=e,n.type=l,n.lanes=m,n}function Gn(e,n,a,l){return e=Et(7,e,l,n),e.lanes=a,e}function Wr(e,n,a,l){return e=Et(22,e,l,n),e.elementType=Q,e.lanes=a,e.stateNode={isHidden:!1},e}function El(e,n,a){return e=Et(6,e,null,n),e.lanes=a,e}function Ml(e,n,a){return n=Et(4,e.children!==null?e.children:[],e.key,n),n.lanes=a,n.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},n}function hx(e,n,a,l,u){this.tag=n,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=so(0),this.expirationTimes=so(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=so(0),this.identifierPrefix=l,this.onRecoverableError=u,this.mutableSourceEagerHydrationData=null}function _l(e,n,a,l,u,m,y,w,C){return e=new hx(e,n,a,w,C),n===1?(n=1,m===!0&&(n|=8)):n=0,m=Et(3,null,null,n),e.current=m,m.stateNode=e,m.memoizedState={element:l,isDehydrated:a,cache:null,transitions:null,pendingSuspenseBoundaries:null},Ho(m),e}function mx(e,n,a){var l=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:B,key:l==null?null:""+l,children:e,containerInfo:n,implementation:a}}function um(e){if(!e)return vn;e=e._reactInternals;e:{if(Rn(e)!==e||e.tag!==1)throw Error(r(170));var n=e;do{switch(n.tag){case 3:n=n.stateNode.context;break e;case 1:if(dt(n.type)){n=n.stateNode.__reactInternalMemoizedMergedChildContext;break e}}n=n.return}while(n!==null);throw Error(r(171))}if(e.tag===1){var a=e.type;if(dt(a))return Fd(e,a,n)}return n}function dm(e,n,a,l,u,m,y,w,C){return e=_l(a,l,!0,e,u,m,y,w,C),e.context=um(null),a=e.current,l=ot(),u=Nn(a),m=sn(l,u),m.callback=n??null,wn(a,m,u),e.current.lanes=u,Ks(e,u,l),pt(e,l),e}function $r(e,n,a,l){var u=n.current,m=ot(),y=Nn(u);return a=um(a),n.context===null?n.context=a:n.pendingContext=a,n=sn(m,y),n.payload={element:e},l=l===void 0?null:l,l!==null&&(n.callback=l),e=wn(u,n,y),e!==null&&(Ft(e,u,y,m),wr(e,u,y)),y}function Hr(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function hm(e,n){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var a=e.retryLane;e.retryLane=a!==0&&a<n?a:n}}function Dl(e,n){hm(e,n),(e=e.alternate)&&hm(e,n)}function px(){return null}var mm=typeof reportError=="function"?reportError:function(e){console.error(e)};function Rl(e){this._internalRoot=e}Gr.prototype.render=Rl.prototype.render=function(e){var n=this._internalRoot;if(n===null)throw Error(r(409));$r(e,n,null,null)},Gr.prototype.unmount=Rl.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var n=e.containerInfo;Wn(function(){$r(null,e,null,null)}),n[Jt]=null}};function Gr(e){this._internalRoot=e}Gr.prototype.unstable_scheduleHydration=function(e){if(e){var n=Yu();e={blockedOn:null,target:e,priority:n};for(var a=0;a<mn.length&&n!==0&&n<mn[a].priority;a++);mn.splice(a,0,e),a===0&&Zu(e)}};function Ll(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function Kr(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function pm(){}function fx(e,n,a,l,u){if(u){if(typeof l=="function"){var m=l;l=function(){var F=Hr(y);m.call(F)}}var y=dm(n,l,e,0,null,!1,!1,"",pm);return e._reactRootContainer=y,e[Jt]=y.current,oi(e.nodeType===8?e.parentNode:e),Wn(),y}for(;u=e.lastChild;)e.removeChild(u);if(typeof l=="function"){var w=l;l=function(){var F=Hr(C);w.call(F)}}var C=_l(e,0,!1,null,null,!1,!1,"",pm);return e._reactRootContainer=C,e[Jt]=C.current,oi(e.nodeType===8?e.parentNode:e),Wn(function(){$r(n,C,a,l)}),C}function qr(e,n,a,l,u){var m=a._reactRootContainer;if(m){var y=m;if(typeof u=="function"){var w=u;u=function(){var C=Hr(y);w.call(C)}}$r(n,y,e,u)}else y=fx(a,n,e,u,l);return Hr(y)}qu=function(e){switch(e.tag){case 3:var n=e.stateNode;if(n.current.memoizedState.isDehydrated){var a=Gs(n.pendingLanes);a!==0&&(io(n,a|1),pt(n,Fe()),(fe&6)===0&&(Ps=Fe()+500,xn()))}break;case 13:Wn(function(){var l=nn(e,1);if(l!==null){var u=ot();Ft(l,e,1,u)}}),Dl(e,1)}},ro=function(e){if(e.tag===13){var n=nn(e,134217728);if(n!==null){var a=ot();Ft(n,e,134217728,a)}Dl(e,134217728)}},Xu=function(e){if(e.tag===13){var n=Nn(e),a=nn(e,n);if(a!==null){var l=ot();Ft(a,e,n,l)}Dl(e,n)}},Yu=function(){return we},Qu=function(e,n){var a=we;try{return we=e,n()}finally{we=a}},Qa=function(e,n,a){switch(n){case"input":if(Wa(e,a),n=a.name,a.type==="radio"&&n!=null){for(a=e;a.parentNode;)a=a.parentNode;for(a=a.querySelectorAll("input[name="+JSON.stringify(""+n)+'][type="radio"]'),n=0;n<a.length;n++){var l=a[n];if(l!==e&&l.form===e.form){var u=dr(l);if(!u)throw Error(r(90));wu(l),Wa(l,u)}}}break;case"textarea":Cu(e,a);break;case"select":n=a.value,n!=null&&rs(e,!!a.multiple,n,!1)}},Lu=Cl,Iu=Wn;var gx={usingClientEntryPoint:!1,Events:[ui,fs,dr,Du,Ru,Cl]},Si={findFiberByHostInstance:Ln,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},yx={bundleType:Si.bundleType,version:Si.version,rendererPackageName:Si.rendererPackageName,rendererConfig:Si.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:I.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=Ou(e),e===null?null:e.stateNode},findFiberByHostInstance:Si.findFiberByHostInstance||px,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Xr=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Xr.isDisabled&&Xr.supportsFiber)try{Gi=Xr.inject(yx),Wt=Xr}catch{}}return ft.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=gx,ft.createPortal=function(e,n){var a=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!Ll(n))throw Error(r(200));return mx(e,n,null,a)},ft.createRoot=function(e,n){if(!Ll(e))throw Error(r(299));var a=!1,l="",u=mm;return n!=null&&(n.unstable_strictMode===!0&&(a=!0),n.identifierPrefix!==void 0&&(l=n.identifierPrefix),n.onRecoverableError!==void 0&&(u=n.onRecoverableError)),n=_l(e,1,!1,null,null,a,!1,l,u),e[Jt]=n.current,oi(e.nodeType===8?e.parentNode:e),new Rl(n)},ft.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var n=e._reactInternals;if(n===void 0)throw typeof e.render=="function"?Error(r(188)):(e=Object.keys(e).join(","),Error(r(268,e)));return e=Ou(n),e=e===null?null:e.stateNode,e},ft.flushSync=function(e){return Wn(e)},ft.hydrate=function(e,n,a){if(!Kr(n))throw Error(r(200));return qr(null,e,n,!0,a)},ft.hydrateRoot=function(e,n,a){if(!Ll(e))throw Error(r(405));var l=a!=null&&a.hydratedSources||null,u=!1,m="",y=mm;if(a!=null&&(a.unstable_strictMode===!0&&(u=!0),a.identifierPrefix!==void 0&&(m=a.identifierPrefix),a.onRecoverableError!==void 0&&(y=a.onRecoverableError)),n=dm(n,null,e,1,a??null,u,!1,m,y),e[Jt]=n.current,oi(e),l)for(e=0;e<l.length;e++)a=l[e],u=a._getVersion,u=u(a._source),n.mutableSourceEagerHydrationData==null?n.mutableSourceEagerHydrationData=[a,u]:n.mutableSourceEagerHydrationData.push(a,u);return new Gr(n)},ft.render=function(e,n,a){if(!Kr(n))throw Error(r(200));return qr(null,e,n,!1,a)},ft.unmountComponentAtNode=function(e){if(!Kr(e))throw Error(r(40));return e._reactRootContainer?(Wn(function(){qr(null,null,e,!1,function(){e._reactRootContainer=null,e[Jt]=null})}),!0):!1},ft.unstable_batchedUpdates=Cl,ft.unstable_renderSubtreeIntoContainer=function(e,n,a,l){if(!Kr(a))throw Error(r(200));if(e==null||e._reactInternals===void 0)throw Error(r(38));return qr(e,n,a,!1,l)},ft.version="18.3.1-next-f1338f8080-20240426",ft}var jm;function Tx(){if(jm)return Fl.exports;jm=1;function t(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(t)}catch(s){console.error(s)}}return t(),Fl.exports=Cx(),Fl.exports}var Sm;function Px(){if(Sm)return Yr;Sm=1;var t=Tx();return Yr.createRoot=t.createRoot,Yr.hydrateRoot=t.hydrateRoot,Yr}var Ax=Px();class Ex extends Error{constructor(r,o){super(r);fm(this,"status");this.status=o}}async function Te(t,s){const r=await fetch(t,{...s,credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json",...s==null?void 0:s.headers}}),o=await r.json().catch(()=>({}));if(!r.ok)throw new Ex(o.error||r.statusText||"Request failed",r.status);return o}const fa=()=>Te("/auth/status"),Mx=()=>Te("/api/config"),ga=()=>Te("/api/botstats"),_x=()=>Te("/api/team"),Dx=t=>Te(`/api/team/${t}`),dc=()=>Te("/api/staff/me"),Rx=(t,s)=>Te("/api/staff/profile",{method:"POST",headers:s?{"X-CSRF-Token":s}:void 0,body:JSON.stringify(t)}),Lx=(t,s)=>Te("/api/staff/global-profile",{method:"POST",headers:s?{"X-CSRF-Token":s}:void 0,body:JSON.stringify(t)}),Ix=()=>Te("/api/commands"),hc=()=>Te("/api/guilds"),Nm=()=>Te("/api/me/overview"),Vx=t=>Te(`/api/guild/${t}/overview`),Fx=t=>Te(`/api/guild/${t}/levels`),Cm=t=>Te(`/api/guild/${t}/config`),zl=t=>Te(`/api/guild/${t}/resources`),Bx=t=>Te(`/api/guild/${t}/applications`),Ox=(t,s,r)=>Te(`/api/guild/${t}/applications`,{method:"POST",headers:r?{"X-CSRF-Token":r}:void 0,body:JSON.stringify(s)}),zx=(t,s,r,o)=>Te(`/api/guild/${t}/applications/${s}/status`,{method:"POST",headers:o?{"X-CSRF-Token":o}:void 0,body:JSON.stringify({status:r})}),Ux=(t,s)=>Te(`/api/guild/${t}/applications/${s}/submissions`),Wx=t=>Te(`/api/applications/${t}`),$x=(t,s)=>Te(`/api/applications/${t}/${s}`),Hx=(t,s,r,o)=>Te(`/api/applications/${t}/${s}/submit`,{method:"POST",headers:o?{"X-CSRF-Token":o}:void 0,body:JSON.stringify({answers:r})});function Da(t,s,r,o){return Te(`/api/guild/${t}/config/${s}`,{method:"POST",headers:o?{"X-CSRF-Token":o}:void 0,body:JSON.stringify(r)})}function Gx(t,s,r){return Te(`/api/guild/${t}/config/profile`,{method:"POST",headers:r?{"X-CSRF-Token":r}:void 0,body:JSON.stringify(s)})}function sf(t){return t.replace(/\/+$/,"")||"/"}function Tm(t=window.location.pathname){const s=sf(t);return s==="/commands"?"commands":s==="/docs"?"docs":s.startsWith("/docs/")?"docs-detail":s==="/dashboard/staff"||s==="/dashboard/staff/"?"staff":s.startsWith("/apply/")?"application":s==="/dashboard"||s.startsWith("/dashboard/")?"dashboard":s==="/team"?"team":s==="/support"?"support":s==="/discord"?"discord":s.startsWith("/team/")?"team-member":s==="/privacy"?"privacy":s==="/terms"?"terms":s==="/community"?"community":s==="/donate"||s.startsWith("/donate")?"donate":s==="/transcript"||s.startsWith("/transcript/")?"transcript":s==="/changelog"?"changelog":s.startsWith("/changelog/")?"changelog-detail":"home"}function Es(t,s="overview"){return t?`/dashboard/${t}/${s}`:"/dashboard"}function mc(){return"/dashboard/servers"}function Pm(){const t=sf(window.location.pathname).split("/").filter(Boolean),s=["overview","leveling","moderation","server","applications","ai","customization"];return t[1]==="servers"?{view:"servers",guildId:null,section:"overview"}:!t[1]||t[1]==="staff"?{view:"overview",guildId:null,section:"overview"}:{view:"guild",guildId:t[1]||null,section:s.includes(t[2])?t[2]:"overview"}}function pe(t){t.startsWith("/")&&(window.history.pushState({},"",t),window.dispatchEvent(new PopStateEvent("popstate")),window.scrollTo({top:0,behavior:"smooth"}))}let Am=null,Ul=null;function _n(){const[t,s]=T.useState(Am);return T.useEffect(()=>{Ul||(Ul=Mx().then(r=>Am=r)),Ul.then(s).catch(()=>{})},[]),t}function rf({onNavigate:t}){const s=_n();return i.jsxs("a",{className:"brand",href:"/",onClick:r=>{r.preventDefault(),t?t():pe("/")},children:[i.jsx("span",{className:"brand-mark",children:s!=null&&s.bot_avatar_url?i.jsx("img",{src:s.bot_avatar_url,alt:"Niko"}):"n"}),i.jsx("span",{children:"niko"})]})}function St(){return i.jsxs("footer",{className:"site-footer",children:[i.jsx(rf,{}),i.jsx("span",{children:"Built for communities that care."}),i.jsxs("div",{children:[i.jsx("a",{href:"/privacy",onClick:t=>{t.preventDefault(),pe("/privacy")},children:"Privacy"}),i.jsx("a",{href:"/terms",onClick:t=>{t.preventDefault(),pe("/terms")},children:"Terms"}),i.jsx("a",{href:"/community",onClick:t=>{t.preventDefault(),pe("/community")},children:"Community Policy"}),i.jsx("a",{href:"/support",onClick:t=>{t.preventDefault(),pe("/support")},children:"Support"})]})]})}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Kx=t=>t==null?void 0:t.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase();/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */function qx(t,s,r=[]){if(s==null)throw new Error("[lucide]: iconNode is required when icon name is used");return{name:Kx(t),size:24,node:s,...r.length>0?{aliases:r}:{}}}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Xx=t=>{let s="",r=!1;for(const o of t){if(o==="-"||o==="_"||o<=" "){r=s.length>0;continue}s.length===0?s+=o.toLowerCase():s+=r?o.toUpperCase():o,r=!1}return s};/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Yx=t=>{const s=Xx(t);return s.charAt(0).toUpperCase()+s.slice(1)};/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const pc=(...t)=>t.filter((s,r,o)=>!!s&&s.trim()!==""&&o.indexOf(s)===r).join(" ").trim();/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Kn={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor","stroke-width":2,"stroke-linecap":"round","stroke-linejoin":"round"};/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */function Wl(t){return t!=null}function Qx(t,s={}){var b,j;const r=s.attributeNames??{},o=k=>r[k]??k,c=t.size??t.width??Kn.width,d=t.size??t.height??Kn.height,h=((b=t.aliases)==null?void 0:b.filter(k=>typeof k=="string"&&k.trim()!=="").map(k=>`lucide-${k}`))??[],p=[...t.name?[`lucide-${t.name}`]:[],...h],f=((j=s.className)==null?void 0:j.split(" ").filter(Boolean))??[],v=s.includeDefaultClasses===!1?pc(...f):pc("lucide",...p,...f),g=s.absoluteStrokeWidth?Number(s.strokeWidth??Kn["stroke-width"])*Number(t.size??t.width??Kn.width)/Number(s.size??s.width??Kn.width):s.strokeWidth??Kn["stroke-width"];return["svg",{...Object.entries(Kn).reduce((k,[S,N])=>(k[o(S)]=N,k),{}),..."color"in s&&s.color&&{[o("stroke")]:s.color},..."size"in s&&Wl(s.size)&&{[o("width")]:s.size,[o("height")]:s.size},..."width"in s&&Wl(s.width)&&{[o("width")]:s.width},..."height"in s&&Wl(s.height)&&{[o("height")]:s.height},[o("stroke-width")]:g,...v&&{[o("class")]:v},[o("viewBox")]:`0 0 ${c} ${d}`,...s.hasA11yProp===!1?{[o("aria-hidden")]:"true"}:{},..."attributes"in s&&s.attributes},t.node.map(k=>{const[S,N,O]=k,M=s.nonScalingStroke?{[o("vector-effect")]:"non-scaling-stroke",...N}:N;return O?[S,M,O]:[S,M]})]}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */function Jx(t,s={}){return Qx(t,{...s,attributeNames:{...s.attributeNames,class:"className","stroke-width":"strokeWidth","stroke-linecap":"strokeLinecap","stroke-linejoin":"strokeLinejoin","vector-effect":"vectorEffect"}})}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Zx=t=>{for(const s in t)if(s.startsWith("aria-")||s==="role"||s==="title")return!0;return!1},eb=T.createContext({}),tb=()=>T.useContext(eb),nb=T.forwardRef(({color:t,size:s,width:r,height:o,strokeWidth:c,absoluteStrokeWidth:d,nonScalingStroke:h,className:p="",children:f,iconNode:v=[],icon:g={node:v,aliases:[],size:24},...x},b)=>{const{size:j=24,strokeWidth:k=2,absoluteStrokeWidth:S=!1,nonScalingStroke:N=!1,color:O="currentColor",className:M=""}=tb()??{},L=!!f||Zx(x),[I,D,B=[]]=Jx(g,{color:t??O,width:r??s??j,height:o??s??j,strokeWidth:c??k,absoluteStrokeWidth:d??S,nonScalingStroke:h??N,className:pc(M,p),hasA11yProp:L,attributes:x});return T.createElement(I,{ref:b,...D},[...B.map(([V,z])=>T.createElement(V,z)),...Array.isArray(f)?f:[f]])});/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */function ze(t,s=[],r=[]){const o=typeof t=="string"?qx(t,s,r):t,c=T.forwardRef(({className:d,...h},p)=>T.createElement(nb,{ref:p,icon:o,className:d,...h}));return o.name&&(c.displayName=Yx(o.name)),c}/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const af={name:"activity",size:24,node:[["path",{d:"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2",key:"169zse"}]]};af.node;const sb=ze(af);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const of={name:"arrow-right",size:24,node:[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]]};of.node;const ib=ze(of);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const lf={name:"book-open",size:24,node:[["path",{d:"M12 5v16",key:"1f6ucr"}],["path",{d:"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z",key:"1fyvmf"}]]};lf.node;const Em=ze(lf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const cf={name:"chart-column",size:24,node:[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],aliases:["bar-chart-3"]};cf.node;const aa=ze(cf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const uf={name:"external-link",size:24,node:[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]]};uf.node;const rb=ze(uf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const df={name:"hash",size:24,node:[["line",{x1:"4",x2:"20",y1:"9",y2:"9",key:"4lhtct"}],["line",{x1:"4",x2:"20",y1:"15",y2:"15",key:"vyu0kd"}],["line",{x1:"10",x2:"8",y1:"3",y2:"21",key:"1ggp8o"}],["line",{x1:"16",x2:"14",y1:"3",y2:"21",key:"weycgp"}]]};df.node;const ab=ze(df);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const hf={name:"layout-grid",size:24,node:[["rect",{width:"7",height:"7",x:"3",y:"3",rx:"1",key:"1g98yp"}],["rect",{width:"7",height:"7",x:"14",y:"3",rx:"1",key:"6d4xhi"}],["rect",{width:"7",height:"7",x:"14",y:"14",rx:"1",key:"nxv5o0"}],["rect",{width:"7",height:"7",x:"3",y:"14",rx:"1",key:"1bb6yr"}]]};hf.node;const fc=ze(hf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const mf={name:"link-2",size:24,node:[["path",{d:"M9 17H7A5 5 0 0 1 7 7h2",key:"8i5ue5"}],["path",{d:"M15 7h2a5 5 0 1 1 0 10h-2",key:"1b9ql8"}],["line",{x1:"8",x2:"16",y1:"12",y2:"12",key:"1jonct"}]]};mf.node;const ob=ze(mf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const pf={name:"lock-keyhole",size:24,node:[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]]};pf.node;const lb=ze(pf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ff={name:"log-out",size:24,node:[["path",{d:"m16 17 5-5-5-5",key:"1bji2h"}],["path",{d:"M21 12H9",key:"dn1m92"}],["path",{d:"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4",key:"1uf3rs"}]]};ff.node;const cb=ze(ff);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const gf={name:"menu",size:24,node:[["path",{d:"M4 5h16",key:"1tepv9"}],["path",{d:"M4 12h16",key:"1lakjw"}],["path",{d:"M4 19h16",key:"1djgab"}]]};gf.node;const ub=ze(gf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const yf={name:"message-circle",size:24,node:[["path",{d:"M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719",key:"1sd12s"}]]};yf.node;const db=ze(yf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const vf={name:"minus",size:24,node:[["path",{d:"M5 12h14",key:"1ays0h"}]]};vf.node;const hb=ze(vf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const xf={name:"plus",size:24,node:[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"M12 5v14",key:"s699le"}]]};xf.node;const mb=ze(xf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const bf={name:"search",size:24,node:[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]]};bf.node;const pb=ze(bf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const wf={name:"settings",size:24,node:[["path",{d:"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915",key:"1i5ecw"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]]};wf.node;const Qr=ze(wf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kf={name:"shield",size:24,node:[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}]]};kf.node;const $l=ze(kf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jf={name:"sparkles",size:24,node:[["path",{d:"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",key:"1s2grr"}],["path",{d:"M20 2v4",key:"1rf3ol"}],["path",{d:"M22 4h-4",key:"gwowj6"}],["circle",{cx:"4",cy:"20",r:"2",key:"6kqj1y"}]],aliases:["stars"]};jf.node;const Jr=ze(jf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Sf={name:"terminal",size:24,node:[["path",{d:"M12 19h8",key:"baeox8"}],["path",{d:"m4 17 6-6-6-6",key:"1yngyt"}]]};Sf.node;const fb=ze(Sf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Nf={name:"users",size:24,node:[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["path",{d:"M16 3.128a4 4 0 0 1 0 7.744",key:"16gr8j"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}]]};Nf.node;const gc=ze(Nf);/**
 * @license lucide-react v1.47.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Cf={name:"x",size:24,node:[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]]};Cf.node;const gb=ze(Cf),yb={arrow:ib,grid:fc,terminal:fb,chart:aa,shield:$l,spark:Jr,users:gc,link:ob,settings:Qr,book:Em,external:rb,menu:ub,message:db,close:gb,minus:hb,plus:mb,lock:lb,logout:cb,search:pb,doc:Em,utility:Qr,icon_home:fc,icon_settings:Qr,icon_economy:aa,icon_leveling:aa,icon_moderation:$l,icon_automod:$l,icon_heart:Jr,icon_utility:Qr,icon_bot:gc,icon_ai:Jr,icon_lightbulb:Jr};function X({name:t,size:s,className:r=""}){const o=yb[t]||fc;return i.jsx(o,{className:`icon ${r}`.trim(),"aria-hidden":"true",focusable:"false",strokeWidth:1.8,style:s?{width:s,height:s}:void 0})}const Mm=[{label:"Home",path:"/",page:"home"},{label:"Commands",path:"/commands",page:"commands"},{label:"Docs",path:"/docs",page:"docs"},{label:"Team",path:"/team",page:"team"},{label:"Changelog",path:"/changelog",page:"changelog"}];function Oe({page:t}){const s=_n(),r=t==="dashboard",[o,c]=T.useState(!1),d=h=>p=>{p.preventDefault(),c(!1),pe(h)};return i.jsxs("header",{className:`site-header${r?" dashboard-header":""}`,children:[i.jsx(rf,{onNavigate:()=>c(!1)}),!r&&i.jsx("nav",{className:"site-nav","aria-label":"Main navigation",children:Mm.map(h=>i.jsx("a",{className:t===h.page?"active":"","aria-current":t===h.page?"page":void 0,href:h.path,onClick:d(h.path),children:h.label},h.path))}),i.jsx("div",{className:"header-actions",children:r?i.jsxs("div",{className:"dashboard-menu",children:[i.jsxs("button",{className:"button button-small button-muted dashboard-menu-trigger",type:"button","aria-expanded":o,"aria-controls":"dashboard-navigation-menu",onClick:()=>c(h=>!h),children:[i.jsx(X,{name:o?"close":"menu"}),i.jsx("span",{children:"Menu"})]}),o&&i.jsxs("nav",{id:"dashboard-navigation-menu",className:"dashboard-menu-popover","aria-label":"Dashboard navigation",children:[i.jsx("span",{className:"dashboard-menu-label",children:"Navigate"}),Mm.map(h=>i.jsx("a",{href:h.path,onClick:d(h.path),children:h.label},h.path)),i.jsx("a",{className:"dashboard-menu-current",href:"/dashboard","aria-current":"page",onClick:d("/dashboard"),children:"Dashboard"})]})]}):i.jsxs(i.Fragment,{children:[i.jsxs("a",{className:"button button-small button-muted dashboard-link",href:"/dashboard",onClick:d("/dashboard"),children:["Dashboard ",i.jsx(X,{name:"arrow"})]}),i.jsx("a",{className:"button button-small button-primary",href:(s==null?void 0:s.invite_url)||"#",target:"_blank",rel:"noreferrer",children:"Add to Discord"})]})})]})}const _m=typeof navigator<"u"?(navigator.language||"en").slice(0,2):"en";function yc(t){const s=t.description;if(typeof s=="string")return s;if(s&&typeof s=="object"){const r=s;if(r[_m])return r[_m];if(r.en)return r.en;const o=Object.values(r).find(c=>typeof c=="string"&&c.length>0);if(o)return o}return"A Niko command for your server."}const vb=[{value:"all",label:"All commands"},{value:"slash",label:"Slash"},{value:"prefix",label:"Prefix"},{value:"hybrid",label:"Hybrid"},{value:"context",label:"Context menus"}],ya={slash:"Slash command",prefix:"Prefix command",hybrid:"Hybrid command",context:"Context menu"};function Qn(t){return t.type&&t.type in ya?t.type:"slash"}function xb(t){return t.context_type==="user"?"Right-click a user":"Right-click a message"}function Tf(t){const s=Qn(t);return s==="slash"?i.jsxs("code",{children:["/",t.name]}):s==="prefix"?i.jsxs("code",{children:[".",t.name]}):s==="hybrid"?i.jsxs(i.Fragment,{children:[i.jsxs("code",{children:["/",t.name]}),i.jsx("span",{className:"command-or",children:"or"}),i.jsxs("code",{children:[".",t.name]})]}):i.jsxs("code",{className:"context-invocation",children:[xb(t)," · ",t.name]})}function Dm(t){return t!=null&&t.length?t:["Not specified"]}function bb({command:t,onClose:s}){T.useEffect(()=>{const h=p=>{p.key==="Escape"&&s()};return document.addEventListener("keydown",h),()=>document.removeEventListener("keydown",h)},[s]);const r=t.parameters||[],o=t.subcommands||[],c=Dm(t.aliases),d=Dm(t.permissions);return i.jsx("div",{className:"command-dialog-backdrop",role:"presentation",onMouseDown:h=>{h.currentTarget===h.target&&s()},children:i.jsxs("section",{className:"command-dialog",role:"dialog","aria-modal":"true","aria-labelledby":"command-dialog-title",children:[i.jsxs("header",{className:"command-dialog-header",children:[i.jsxs("div",{children:[i.jsxs("div",{className:"command-dialog-kicker",children:[t.category," · ",ya[Qn(t)]]}),i.jsx("h2",{id:"command-dialog-title",children:Tf(t)})]}),i.jsx("button",{className:"dialog-close",type:"button",onClick:s,"aria-label":"Close command details",title:"Close command details",children:i.jsx(X,{name:"close"})})]}),i.jsxs("div",{className:"command-dialog-body",children:[i.jsx("p",{className:"command-dialog-description",children:yc(t)}),i.jsxs("div",{className:"command-detail-grid",children:[i.jsxs("section",{className:"command-detail-section command-detail-wide",children:[i.jsx("h3",{children:"Usage"}),i.jsx("code",{className:"command-usage",children:t.usage||`${Qn(t)==="context"?t.name:`/${t.name}`}`})]}),i.jsxs("section",{className:"command-detail-section",children:[i.jsx("h3",{children:"Permissions"}),i.jsx("ul",{className:"command-detail-list",children:d.map(h=>i.jsx("li",{children:h},h))})]}),i.jsxs("section",{className:"command-detail-section",children:[i.jsx("h3",{children:"Aliases"}),i.jsx("ul",{className:"command-detail-list",children:c.map(h=>i.jsx("li",{children:i.jsx("code",{children:h==="Not specified"?h:`.${h}`})},h))})]})]}),!!r.length&&i.jsxs("section",{className:"command-detail-section command-parameters",children:[i.jsx("h3",{children:"Parameters"}),i.jsx("div",{className:"command-parameter-list",children:r.map(h=>i.jsxs("div",{className:"command-parameter",children:[i.jsxs("div",{className:"command-parameter-title",children:[i.jsx("code",{children:h.name}),i.jsxs("span",{children:[h.required?"Required":"Optional"," · ",h.type]})]}),i.jsx("p",{children:h.description||"No description provided."})]},h.name))})]}),!!o.length&&i.jsxs("section",{className:"command-detail-section",children:[i.jsx("h3",{children:"Subcommands"}),i.jsx("div",{className:"subcommand-list",children:o.map(h=>i.jsxs("code",{children:[t.name," ",h]},h))})]})]}),i.jsxs("footer",{className:"command-dialog-footer",children:[i.jsx("span",{children:"Command registry details are generated from the live bot."}),i.jsx("button",{className:"button button-primary button-small",type:"button",onClick:s,children:"Done"})]})]})})}function wb(){const[t,s]=T.useState([]),[r,o]=T.useState(null),[c,d]=T.useState(""),[h,p]=T.useState("all"),[f,v]=T.useState("all"),[g,x]=T.useState(!0),[b,j]=T.useState("");T.useEffect(()=>{Ix().then(s).catch(()=>j("The command registry is unavailable right now.")).finally(()=>x(!1))},[]),T.useEffect(()=>{if(!r)return;const N=document.body.style.overflow;return document.body.style.overflow="hidden",()=>{document.body.style.overflow=N}},[r]);const k=T.useMemo(()=>["all",...Array.from(new Set(t.map(N=>N.category))).sort()],[t]),S=t.filter(N=>{const O=`${N.name} ${yc(N)} ${N.category} ${ya[Qn(N)]} ${N.context_type||""} ${(N.aliases||[]).join(" ")}`.toLowerCase();return(f==="all"||Qn(N)===f)&&(h==="all"||N.category===h)&&O.includes(c.trim().toLowerCase())});return i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"commands"}),i.jsxs("main",{className:"shell page-main",children:[i.jsxs("div",{className:"page-heading",children:[i.jsx("div",{className:"eyebrow",children:"Reference library"}),i.jsxs("h1",{children:["Everything Niko",i.jsx("br",{}),i.jsx("em",{children:"knows how to do."})]}),i.jsx("p",{children:"Browse slash, prefix, hybrid, and context commands from the live bot registry. Select any command for permissions, aliases, parameters, usage, and subcommands."})]}),i.jsxs("div",{className:"command-toolbar",children:[i.jsxs("label",{className:"search-field",children:[i.jsx("span",{"aria-hidden":"true",children:"⌕"}),i.jsx("input",{value:c,onChange:N=>d(N.target.value),placeholder:"Search commands","aria-label":"Search commands"})]}),i.jsxs("div",{className:"command-filters",children:[i.jsx("div",{className:"filter-list","aria-label":"Command types",children:vb.map(N=>i.jsx("button",{type:"button",className:f===N.value?"filter active":"filter","aria-pressed":f===N.value,onClick:()=>v(N.value),children:N.label},N.value))}),i.jsx("div",{className:"filter-list","aria-label":"Command categories",children:k.map(N=>i.jsx("button",{type:"button",className:h===N?"filter active":"filter","aria-pressed":h===N,onClick:()=>p(N),children:N==="all"?"All categories":N},N))})]})]}),i.jsxs("div",{className:"command-meta",children:[i.jsx("strong",{children:g?"…":S.length})," commands ",i.jsx("span",{children:"·"})," live bot registry ",i.jsx("span",{children:"·"})," select a card for details"]}),b&&i.jsxs("div",{className:"inline-error",role:"alert",children:[i.jsx("strong",{children:"Could not load commands"}),i.jsx("span",{children:b})]}),i.jsxs("div",{className:"commands-grid",children:[S.map(N=>i.jsxs("button",{className:"command-card",type:"button",onClick:()=>o(N),"aria-label":`View details for ${N.name}`,children:[i.jsxs("span",{className:"command-card-head",children:[i.jsx("span",{className:"command-name",children:Tf(N)}),i.jsx("span",{className:"command-type",children:ya[Qn(N)]})]}),i.jsx("span",{className:"command-card-description",children:yc(N)}),i.jsxs("span",{className:"command-card-footer",children:[i.jsx("span",{className:"category-tag",children:N.category}),i.jsxs("span",{className:"command-expand",children:[i.jsx("span",{children:"Details"}),i.jsx(X,{name:"arrow",size:14})]})]})]},`${Qn(N)}-${N.context_type||""}-${N.category}-${N.name}`)),!g&&!b&&!S.length&&i.jsx("div",{className:"empty-state",children:"No commands match that search."})]})]}),i.jsx(St,{}),r&&i.jsx(bb,{command:r,onClose:()=>o(null)})]})}function xe(t){return t==null?"—":new Intl.NumberFormat("en-US",{notation:t>9999?"compact":"standard"}).format(t)}function Pf(t){return(t==null?void 0:t.global_name)||(t==null?void 0:t.username)||"there"}function Af(t){return t.split(/\s+/).map(s=>s[0]).join("").slice(0,2).toUpperCase()}function $c({guild:t,className:s="guild-avatar"}){return i.jsx("span",{className:s,"aria-hidden":"true",children:t.icon_url?i.jsx("img",{src:t.icon_url,alt:""}):t.name.slice(0,1).toUpperCase()})}function Ef({user:t,className:s="avatar"}){const r=t.avatar?`https://cdn.discordapp.com/avatars/${t.id}/${t.avatar}.${t.avatar.startsWith("a_")?"gif":"png"}?size=64`:null;return i.jsx("span",{className:s,"aria-hidden":"true",children:r?i.jsx("img",{src:r,alt:""}):Af(t.global_name||t.username||"Niko")})}function kb({name:t,avatarUrl:s,className:r="member-avatar"}){return i.jsx("span",{className:r,"aria-hidden":"true",children:s?i.jsx("img",{src:s,alt:""}):Af(t)})}const jb=[["overview","Overview","grid","At a glance"],["leveling","Leveling","spark","Reward participation"],["moderation","Moderation","shield","Keep things steady"],["server","Server","settings","Manage server features"],["applications","Applications","users","Staff role openings"],["ai","AI controls","settings","Shape Niko’s voice"],["customization","Customization","paint","Niko’s server identity"]];function Mf({user:t,guilds:s,selectedGuild:r,view:o,section:c,stats:d,onHome:h,onServers:p,onGuildChange:f,onSectionChange:v,onRefresh:g,refreshing:x,staffRole:b,children:j}){const k=s.filter(M=>M.installed!==!1),S=(M=!1)=>i.jsx("nav",{className:M?"dash-nav dash-nav-mobile":"dash-nav","aria-label":"Server settings",children:jb.map(([L,I,D])=>i.jsxs("button",{className:o==="guild"&&c===L?"active":"","aria-current":o==="guild"&&c===L?"page":void 0,onClick:()=>v(L),children:[i.jsx(X,{name:D}),i.jsx("span",{children:I})]},L))}),N=(M=!1)=>i.jsxs("nav",{className:M?"dash-nav dash-primary-nav dash-nav-mobile":"dash-nav dash-primary-nav","aria-label":"Dashboard",children:[i.jsxs("button",{className:o==="overview"?"active":"","aria-current":o==="overview"?"page":void 0,onClick:h,children:[i.jsx(X,{name:"grid"}),i.jsx("span",{children:"My overview"})]}),i.jsxs("button",{className:o==="servers"?"active":"","aria-current":o==="servers"?"page":void 0,onClick:p,children:[i.jsx(X,{name:"users"}),i.jsx("span",{children:"My servers"})]}),b&&i.jsxs("button",{onClick:()=>pe("/dashboard/staff"),children:[i.jsx(X,{name:"shield"}),i.jsx("span",{children:"Staff workspace"})]})]}),O=()=>i.jsxs("div",{className:"dash-top-actions",children:[o==="guild"?i.jsxs("label",{className:"guild-switcher",children:[i.jsx("span",{className:"sr-only",children:"Switch server"}),i.jsxs("select",{value:(r==null?void 0:r.id)||"",onChange:M=>{const L=k.find(I=>I.id===M.target.value);L&&f(L)},children:[i.jsx("option",{value:"",disabled:!0,children:"Switch server"}),k.map(M=>i.jsx("option",{value:M.id,children:M.name},M.id))]})]}):i.jsxs("button",{className:"button button-muted button-small top-action",onClick:p,children:[i.jsx(X,{name:"users"})," Browse servers"]}),i.jsxs("button",{className:"button button-muted button-small top-action refresh-action",onClick:g,disabled:x,"aria-label":"Refresh dashboard data",children:[i.jsx(X,{name:"spark"})," ",x?"Refreshing…":"Refresh data"]}),o==="guild"&&i.jsxs("span",{className:"connection-chip",children:[i.jsx("span",{className:"status-dot"})," Connected"]}),i.jsxs("div",{className:"user-pill",children:[i.jsx(Ef,{user:t}),i.jsx("span",{children:Pf(t)})]}),i.jsx("a",{className:"logout-button",href:"/auth/logout","aria-label":"Log out",title:"Log out",children:i.jsx(X,{name:"logout"})})]});return i.jsxs("div",{className:"dashboard-layout",children:[i.jsxs("aside",{className:"dash-sidebar",children:[i.jsx("div",{className:"dash-mobile-controls",children:O()}),i.jsxs("div",{className:"side-rail-heading",children:[i.jsx("span",{className:"side-label",children:"Workspace"}),i.jsxs("span",{className:"rail-status",children:[i.jsx("span",{className:"status-dot"})," Live"]})]}),N(),o==="guild"&&r&&i.jsxs(i.Fragment,{children:[i.jsx("div",{className:"side-label side-label-settings",children:"Current server"}),i.jsxs("div",{className:"side-guild",children:[i.jsx($c,{guild:r}),i.jsxs("span",{children:[i.jsx("strong",{children:r.name}),i.jsx("small",{children:"Live configuration"})]}),i.jsx("span",{className:"guild-presence",title:"Niko is connected",children:i.jsx("span",{className:"status-dot"})})]}),i.jsxs("div",{className:"side-settings-caption",children:[i.jsx("span",{children:"Settings map"}),i.jsx("small",{children:"Pick a room to tune"})]}),S()]}),i.jsxs("div",{className:"sidebar-bottom",children:[i.jsxs("span",{className:"online-label",children:[i.jsx("span",{className:"status-dot"})," Niko is online"]}),i.jsxs("small",{children:[xe(d==null?void 0:d.guild_count)," connected servers · v",(d==null?void 0:d.version)||"1.0"]}),i.jsxs("a",{href:"/",onClick:M=>{M.preventDefault(),pe("/")},children:["Back to public site ",i.jsx(X,{name:"arrow"})]})]})]}),i.jsxs("div",{className:"dash-content",children:[i.jsx(Oe,{page:"dashboard"}),i.jsx("div",{className:"dash-contextbar",children:O()}),i.jsx("div",{className:"mobile-primary-bar",children:N(!0)}),o==="guild"&&i.jsx("div",{className:"mobile-section-bar",children:S(!0)}),i.jsx("main",{className:"dash-main",children:j})]})]})}const _f=T.createContext({});function Sb(t){const s=T.useRef(null);return s.current===null&&(s.current=t()),s.current}const Nb=typeof window<"u",Cb=Nb?T.useLayoutEffect:T.useEffect,Hc=T.createContext(null);function Gc(t,s){t.indexOf(s)===-1&&t.push(s)}function va(t,s){const r=t.indexOf(s);r>-1&&t.splice(r,1)}const Ut=(t,s,r)=>r>s?s:r<t?t:r;let Ra=()=>{};const ln={},Kc=t=>/^-?(?:\d+(?:\.\d+)?|\.\d+)$/u.test(t),Df=t=>typeof t=="object"&&t!==null,qc=t=>/^0[^.\s]+$/u.test(t);function Rf(t){let s;return()=>(s===void 0&&(s=t()),s)}const zt=t=>t,Ii=(...t)=>t.reduce((s,r)=>o=>r(s(o))),Mi=(t,s,r)=>{const o=s-t;return o?(r-t)/o:1};class xa{constructor(){this.subscriptions=[]}add(s){return Gc(this.subscriptions,s),()=>this.remove(s)}remove(s){va(this.subscriptions,s)}notify(s,r,o){const c=this.subscriptions.length;if(c)if(c===1)this.subscriptions[0](s,r,o);else for(let d=0;d<c;d++){const h=this.subscriptions[d];h&&h(s,r,o)}}getSize(){return this.subscriptions.length}clear(){this.subscriptions.length=0}}const Mt=t=>t*1e3,kt=t=>t/1e3,Lf=(t,s)=>s?t*(1e3/s):0,If=(t,s,r)=>(((1-3*r+3*s)*t+(3*r-6*s))*t+3*s)*t,Tb=1e-7,Pb=12;function Ab(t,s,r,o,c){let d,h,p=0;do h=s+(r-s)/2,d=If(h,o,c)-t,d>0?r=h:s=h;while(Math.abs(d)>Tb&&++p<Pb);return h}function Vi(t,s,r,o){if(t===s&&r===o)return zt;const c=d=>Ab(d,0,1,t,r);return d=>d===0||d===1?d:If(c(d),s,o)}const Vf=t=>s=>s<=.5?t(2*s)/2:(2-t(2*(1-s)))/2,Ff=t=>s=>1-t(1-s),Bf=Vi(.33,1.53,.69,.99),Xc=Ff(Bf),Of=Vf(Xc),zf=t=>t>=1?1:(t*=2)<1?.5*Xc(t):.5*(2-Math.pow(2,-10*(t-1))),Yc=t=>1-Math.sin(Math.acos(t)),Uf=Ff(Yc),Wf=Vf(Yc),Eb=Vi(.42,0,1,1),Mb=Vi(0,0,.58,1),$f=Vi(.42,0,.58,1),_b=t=>Array.isArray(t)&&typeof t[0]!="number",Hf=t=>Array.isArray(t)&&typeof t[0]=="number",Db={linear:zt,easeIn:Eb,easeInOut:$f,easeOut:Mb,circIn:Yc,circInOut:Wf,circOut:Uf,backIn:Xc,backInOut:Of,backOut:Bf,anticipate:zf},Rb=t=>typeof t=="string",Rm=t=>{if(Hf(t)){Ra(t.length===4);const[s,r,o,c]=t;return Vi(s,r,o,c)}else if(Rb(t))return Db[t];return t},Zr=["setup","read","resolveKeyframes","preUpdate","update","preRender","render","postRender"];function Lb(t){let s=new Set,r=new Set,o=!1,c=!1;const d=new Set;let h={delta:0,timestamp:0,isProcessing:!1};function p(v){d.has(v)&&(r.add(v),t()),v(h)}const f={schedule:(v,g=!1,x=!1)=>{const j=x&&o?s:r;return g&&d.add(v),j.add(v),v},cancel:v=>{r.delete(v),d.delete(v)},process:v=>{if(h=v,o){c=!0;return}o=!0;const g=s;s=r,r=g,s.forEach(p),s.clear(),o=!1,c&&(c=!1,f.process(v))}};return f}const Ib=40;function Gf(t,s){let r=!1,o=!0;const c={delta:0,timestamp:0,isProcessing:!1},d=()=>r=!0,h=Zr.reduce((L,I)=>(L[I]=Lb(d),L),{}),{setup:p,read:f,resolveKeyframes:v,preUpdate:g,update:x,preRender:b,render:j,postRender:k}=h,S=()=>{const L=ln.useManualTiming,I=L?c.timestamp:performance.now();r=!1,L||(c.delta=o?1e3/60:Math.max(Math.min(I-c.timestamp,Ib),1)),c.timestamp=I,c.isProcessing=!0,p.process(c),f.process(c),v.process(c),g.process(c),x.process(c),b.process(c),j.process(c),k.process(c),c.isProcessing=!1,r&&s&&(o=!1,t(S))},N=()=>{r=!0,o=!0,c.isProcessing||t(S)};return{schedule:Zr.reduce((L,I)=>{const D=h[I];return L[I]=(B,V=!1,z=!1)=>(r||N(),D.schedule(B,V,z)),L},{}),cancel:L=>{for(let I=0;I<Zr.length;I++)h[Zr[I]].cancel(L)},state:c,steps:h}}const{schedule:je,cancel:Mn,state:Ke,steps:Hl}=Gf(typeof requestAnimationFrame<"u"?requestAnimationFrame:zt,!0);let oa;function Vb(){oa=void 0}const rt={now:()=>(oa===void 0&&rt.set(Ke.isProcessing||ln.useManualTiming?Ke.timestamp:performance.now()),oa),set:t=>{oa=t,queueMicrotask(Vb)}},Ls=t=>Math.round(t*1e5)/1e5,Kf=t=>s=>typeof s=="string"&&s.startsWith(t),qf=Kf("--"),Fb=Kf("var(--"),Qc=t=>Fb(t)?Bb.test(t.split("/*")[0].trim()):!1,Bb=/var\(--(?:[\w-]+\s*|[\w-]+\s*,(?:\s*[^)(\s]|\s*\((?:[^)(]|\([^)(]*\))*\))+\s*)\)$/iu;function Lm(t){return typeof t!="string"?!1:t.split("/*")[0].includes("var(--")}const Vs={test:t=>typeof t=="number",parse:parseFloat,transform:t=>t},_i={...Vs,transform:t=>Ut(0,1,t)},ea={...Vs,default:1},Jc=/-?(?:\d+(?:\.\d+)?|\.\d+)/gu;function Ob(t){return t==null}const zb=/^(?:#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\))$/iu,Zc=(t,s)=>r=>!!(typeof r=="string"&&zb.test(r)&&r.startsWith(t)||s&&!Ob(r)&&Object.prototype.hasOwnProperty.call(r,s)),Xf=(t,s,r)=>o=>{if(typeof o!="string")return o;const[c,d,h,p]=o.match(Jc);return{[t]:parseFloat(c),[s]:parseFloat(d),[r]:parseFloat(h),alpha:p!==void 0?parseFloat(p):1}},Ub=t=>Ut(0,255,t),Gl={...Vs,transform:t=>Math.round(Ub(t))},Jn={test:Zc("rgb","red"),parse:Xf("red","green","blue"),transform:({red:t,green:s,blue:r,alpha:o=1})=>"rgba("+Gl.transform(t)+", "+Gl.transform(s)+", "+Gl.transform(r)+", "+Ls(_i.transform(o))+")"};function Wb(t){let s="",r="",o="",c="";return t.length>5?(s=t.substring(1,3),r=t.substring(3,5),o=t.substring(5,7),c=t.substring(7,9)):(s=t.substring(1,2),r=t.substring(2,3),o=t.substring(3,4),c=t.substring(4,5),s+=s,r+=r,o+=o,c+=c),{red:parseInt(s,16),green:parseInt(r,16),blue:parseInt(o,16),alpha:c?parseInt(c,16)/255:1}}const vc={test:Zc("#"),parse:Wb,transform:Jn.transform},Fi=t=>({test:s=>typeof s=="string"&&s.endsWith(t)&&s.split(" ").length===1,parse:parseFloat,transform:s=>`${s}${t}`}),on=Fi("deg"),Qt=Fi("%"),te=Fi("px"),$b=Fi("vh"),Hb=Fi("vw"),Im={...Qt,parse:t=>Qt.parse(t)/100,transform:t=>Qt.transform(t*100)},_s={test:Zc("hsl","hue"),parse:Xf("hue","saturation","lightness"),transform:({hue:t,saturation:s,lightness:r,alpha:o=1})=>"hsla("+Math.round(t)+", "+Qt.transform(Ls(s))+", "+Qt.transform(Ls(r))+", "+Ls(_i.transform(o))+")"},qe={test:t=>Jn.test(t)||vc.test(t)||_s.test(t),parse:t=>Jn.test(t)?Jn.parse(t):_s.test(t)?_s.parse(t):vc.parse(t),transform:t=>typeof t=="string"?t:t.hasOwnProperty("red")?Jn.transform(t):_s.transform(t),getAnimatableNone:t=>{const s=qe.parse(t);return s.alpha=0,qe.transform(s)}},Gb=/(?:#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\))/giu,Yf=new RegExp(Jc.source),Qf=new RegExp(Gb.source,"i");function Kb(t){return isNaN(t)&&typeof t=="string"&&(Yf.test(t)||Qf.test(t))}const Jf="number",Zf="color",qb="var",Xb="var(",Vm="${}",Yb=/var\s*\(\s*--(?:[\w-]+\s*|[\w-]+\s*,(?:\s*[^)(\s]|\s*\((?:[^)(]|\([^)(]*\))*\))+\s*)\)|#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\)|-?(?:\d+(?:\.\d+)?|\.\d+)/giu;function Qb(t){const s=t.toString();return Yf.test(s)||Qf.test(s)}function Di(t){const s=t.toString(),r=[],o={color:[],number:[],var:[]},c=[];let d=0;const p=s.replace(Yb,f=>(qe.test(f)?(o.color.push(d),c.push(Zf),r.push(qe.parse(f))):f.startsWith(Xb)?(o.var.push(d),c.push(qb),r.push(f)):(o.number.push(d),c.push(Jf),r.push(parseFloat(f))),++d,Vm)).split(Vm);return{values:r,split:p,indexes:o,types:c}}function Jb(t){return Di(t).values}function eg({split:t,types:s}){const r=t.length;return o=>{let c="";for(let d=0;d<r;d++)if(c+=t[d],o[d]!==void 0){const h=s[d];h===Jf?c+=Ls(o[d]):h===Zf?c+=qe.transform(o[d]):c+=o[d]}return c}}function Zb(t){return eg(Di(t))}const ew=t=>typeof t=="number"?0:qe.test(t)?qe.getAnimatableNone(t):t,tw=(t,s)=>typeof t=="number"?s!=null&&s.trim().endsWith("/")?t:0:ew(t);function nw(t){const s=Di(t);return eg(s)(s.values.map((o,c)=>tw(o,s.split[c])))}const jt={test:Kb,parse:Jb,createTransformer:Zb,getAnimatableNone:nw};function Kl(t,s,r){return r<0&&(r+=1),r>1&&(r-=1),r<1/6?t+(s-t)*6*r:r<1/2?s:r<2/3?t+(s-t)*(2/3-r)*6:t}function sw({hue:t,saturation:s,lightness:r,alpha:o}){t/=360,s/=100,r/=100;let c=0,d=0,h=0;if(!s)c=d=h=r;else{const p=r<.5?r*(1+s):r+s-r*s,f=2*r-p;c=Kl(f,p,t+1/3),d=Kl(f,p,t),h=Kl(f,p,t-1/3)}return{red:Math.round(c*255),green:Math.round(d*255),blue:Math.round(h*255),alpha:o}}function ba(t,s){return r=>r>0?s:t}const ke=(t,s,r)=>t+(s-t)*r,ql=(t,s,r)=>{const o=t*t,c=r*(s*s-o)+o;return c<0?0:Math.sqrt(c)},iw=[vc,Jn,_s],rw=t=>iw.find(s=>s.test(t));function Fm(t){const s=rw(t);if(!s)return!1;let r=s.parse(t);return s===_s&&(r=sw(r)),r}const Bm=(t,s)=>{const r=Fm(t),o=Fm(s);if(!r||!o)return ba(t,s);const c={...r};return d=>(c.red=ql(r.red,o.red,d),c.green=ql(r.green,o.green,d),c.blue=ql(r.blue,o.blue,d),c.alpha=ke(r.alpha,o.alpha,d),Jn.transform(c))},xc=new Set(["none","hidden"]);function aw(t,s){return xc.has(t)?r=>r<=0?t:s:r=>r>=1?s:t}function ow(t,s){return r=>ke(t,s,r)}function eu(t){return typeof t=="number"?ow:typeof t=="string"?Qc(t)?ba:qe.test(t)?Bm:uw:Array.isArray(t)?tg:typeof t=="object"?qe.test(t)?Bm:lw:ba}function tg(t,s){const r=[...t],o=r.length,c=t.map((d,h)=>eu(d)(d,s[h]));return d=>{for(let h=0;h<o;h++)r[h]=c[h](d);return r}}function lw(t,s){const r={...t,...s},o={};for(const c in r)t[c]!==void 0&&s[c]!==void 0&&(o[c]=eu(t[c])(t[c],s[c]));return c=>{for(const d in o)r[d]=o[d](c);return r}}function cw(t,s){const r=[],o={color:0,var:0,number:0};for(let c=0;c<s.values.length;c++){const d=s.types[c],h=t.indexes[d][o[d]],p=t.values[h]??0;r[c]=p,o[d]++}return r}const uw=(t,s)=>{const r=jt.createTransformer(s),o=Di(t),c=Di(s);return o.indexes.var.length===c.indexes.var.length&&o.indexes.color.length===c.indexes.color.length&&o.indexes.number.length>=c.indexes.number.length?xc.has(t)&&!c.values.length||xc.has(s)&&!o.values.length?aw(t,s):Ii(tg(cw(o,c),c.values),r):ba(t,s)},Om=/^(-?(?:\d+(?:\.\d*)?|\.\d+))([a-z%]*)$/iu;function dw(t,s){const r=Om.exec(t);if(!r)return;const o=Om.exec(s);if(!o||r[2]!==o[2])return;const c=r[2],d=parseFloat(r[1]),h=parseFloat(o[1]);return p=>Ls(ke(d,h,p))+c}function tu(t,s,r){if(typeof t=="number"&&typeof s=="number"&&typeof r=="number")return ke(t,s,r);if(typeof t=="string"&&typeof s=="string"){const c=dw(t,s);if(c)return c}return eu(t)(t,s)}const hw=t=>{const s=({timestamp:r})=>t(r);return{start:(r=!0)=>je.update(s,r),stop:()=>Mn(s),now:()=>Ke.isProcessing?Ke.timestamp:rt.now()}},ng=(t,s,r=10)=>{let o="";const c=Math.max(Math.round(s/r),2);for(let d=0;d<c;d++)o+=Math.round(t(d/(c-1))*1e4)/1e4+", ";return`linear(${o.substring(0,o.length-2)})`},nu=2e4;function su(t,s=50,r=nu,o){let c=0,d=t.next(c);for(;!d.done&&c<r;)c+=s,d=t.next(c);return c>=r?1/0:c}function mw(t,s=100,r){const o=r({...t,keyframes:[0,s]}),c=Math.min(su(o),nu);return{type:"keyframes",ease:d=>o.next(c*d).value/s,duration:kt(c)}}const Ve={stiffness:100,damping:10,mass:1,velocity:0,duration:800,bounce:.3,visualDuration:.3,restSpeed:{granular:.01,default:2},restDelta:{granular:.005,default:.5},minDuration:.01,maxDuration:10,minDamping:.05,maxDamping:1};function bc(t,s){return t*Math.sqrt(1-s*s)}const pw=12;function fw(t,s,r){let o=r;for(let c=1;c<pw;c++)o=o-t(o)/s(o);return o}const Xl=.001;function gw({duration:t=Ve.duration,bounce:s=Ve.bounce,velocity:r=Ve.velocity,mass:o=Ve.mass}){let c,d,h=1-s;h=Ut(Ve.minDamping,Ve.maxDamping,h),t=Ut(Ve.minDuration,Ve.maxDuration,kt(t)),h<1?(c=v=>{const g=v*h,x=g*t,b=g-r,j=bc(v,h),k=Math.exp(-x);return Xl-b/j*k},d=v=>{const x=v*h*t,b=x*r+r,j=h*h*v*v*t,k=Math.exp(-x),S=bc(v*v,h);return(-c(v)+Xl>0?-1:1)*((b-j)*k)/S}):(c=v=>{const g=Math.exp(-v*t),x=(v-r)*t+1;return-Xl+g*x},d=v=>{const g=Math.exp(-v*t),x=(r-v)*(t*t);return g*x});const p=5/t,f=fw(c,d,p);if(t=Mt(t),isNaN(f))return{stiffness:Ve.stiffness,damping:Ve.damping,duration:t};{const v=f*f*o;return{stiffness:v,damping:h*2*Math.sqrt(o*v),duration:t}}}const sg=["duration","bounce"],ig=["stiffness","damping","mass"];function wa(t,s){return s.some(r=>t[r]!==void 0)}function yw(t){let s={velocity:Ve.velocity,stiffness:Ve.stiffness,damping:Ve.damping,mass:Ve.mass,isResolvedFromDuration:!1,...t};if(!wa(t,ig)&&wa(t,sg))if(s.velocity=0,t.visualDuration){const r=t.visualDuration,o=2*Math.PI/(r*1.2),c=o*o,d=2*Ut(.05,1,1-(t.bounce||0))*Math.sqrt(c);s={...s,mass:Ve.mass,stiffness:c,damping:d}}else{const r=gw({...t,velocity:0});s={...s,...r,mass:Ve.mass},s.isResolvedFromDuration=!0}return s}function ka(t=Ve.visualDuration,s=Ve.bounce){const r=typeof t!="object"?{visualDuration:t,keyframes:[0,1],bounce:s}:t,o=r.keyframes[0],c=r.keyframes[r.keyframes.length-1],d={done:!1,value:o},{stiffness:h,damping:p,mass:f,duration:v,velocity:g,isResolvedFromDuration:x}=yw({...r,velocity:-kt(r.velocity||0)}),b=p/(2*Math.sqrt(h*f)),j=kt(Math.sqrt(h/f)),k=b*j,S={target:c,delta:c-o,velocity:g||0,restSpeed:0,restDelta:0},N=()=>{const V=Math.abs(S.delta)<5;S.restSpeed=r.restSpeed||(V?Ve.restSpeed.granular:Ve.restSpeed.default),S.restDelta=r.restDelta||(V?Ve.restDelta.granular:Ve.restDelta.default)};N();let O,M,L;if(b<1){const V=bc(j,b),z={A:0,sinC:0,cosC:0,t:-1,env:0,sin:0,cos:0};L=()=>{z.A=(S.velocity+k*S.delta)/V,z.sinC=k*z.A+S.delta*V,z.cosC=k*S.delta-z.A*V};const re=Y=>{Y!==z.t&&(z.t=Y,z.env=Math.exp(-k*Y),z.sin=Math.sin(V*Y),z.cos=Math.cos(V*Y))};O=Y=>(re(Y),S.target-z.env*(z.A*z.sin+S.delta*z.cos)),M=Y=>(re(Y),z.env*(z.sinC*z.sin+z.cosC*z.cos))}else if(b===1){O=z=>S.target-Math.exp(-j*z)*(S.delta+(S.velocity+j*S.delta)*z);const V={C:0};L=()=>{V.C=S.velocity+j*S.delta},M=z=>Math.exp(-j*z)*(j*V.C*z-S.velocity)}else{const V=j*Math.sqrt(b*b-1);O=re=>{const Y=Math.exp(-k*re),ce=Math.min(V*re,300);return S.target-Y*((S.velocity+k*S.delta)*Math.sinh(ce)+V*S.delta*Math.cosh(ce))/V};const z={P:0,sinh:0,cosh:0};L=()=>{z.P=(S.velocity+k*S.delta)/V,z.sinh=k*z.P-S.delta*V,z.cosh=k*S.delta-z.P*V},M=re=>{const Y=Math.exp(-k*re),ce=Math.min(V*re,300);return Y*(z.sinh*Math.sinh(ce)+z.cosh*Math.cosh(ce))}}L();const I=!wa(r,ig)&&wa(r,sg),D=x&&v||null,B={calculatedDuration:D,retarget:(V,z)=>{S.target=V[V.length-1],S.delta=S.target-V[0],S.velocity=I?0:-kt(z),r.restSpeed&&r.restDelta||N(),B.calculatedDuration=D,d.done=!1,L()},velocity:V=>Mt(M(V)),next:V=>{const z=O(V);if(x)d.done=V>=v;else{const re=Mt(M(V));d.done=Math.abs(re)<=S.restSpeed&&Math.abs(S.target-z)<=S.restDelta}return d.value=d.done?S.target:z,d},toString:()=>{const V=Math.min(su(B),nu),z=ng(re=>B.next(V*re).value,V,30);return V+"ms "+z},toTransition:()=>{}};return B}ka.applyToOptions=t=>{const s=mw(t,100,ka);return t.ease=s.ease,t.duration=Mt(s.duration),t.type="keyframes",t};function wc({keyframes:t,velocity:s=0,power:r=.8,timeConstant:o=325,bounceDamping:c=10,bounceStiffness:d=500,modifyTarget:h,min:p,max:f,restDelta:v=.5,restSpeed:g}){const x=t[0],b={done:!1,value:x},j=V=>V<p||V>f,k=V=>p===void 0?f:f===void 0||Math.abs(p-V)<Math.abs(f-V)?p:f;let S=r*s;const N=x+S,O=h===void 0?N:h(N);O!==N&&(S=O-x);const M=V=>-S*Math.exp(-V/o),L=V=>{const z=M(V);b.done=Math.abs(z)<=v,b.value=b.done?O:O+z};let I,D;const B=V=>{j(b.value)&&(I=V,D=ka({keyframes:[b.value,k(b.value)],velocity:-M(V)/o*1e3,damping:c,stiffness:d,restDelta:v,restSpeed:g}))};return B(0),{calculatedDuration:null,next:V=>{let z=!1;return!D&&I===void 0&&(z=!0,L(V),B(V)),I!==void 0&&V>=I?D.next(V-I):(!z&&L(V),b)}}}function vw(t,s,r){const o=[],c=r||ln.mix||tu,d=t.length-1;for(let h=0;h<d;h++){let p=c(t[h],t[h+1]);if(s){const f=Array.isArray(s)?s[h]||zt:s;p=Ii(f,p)}o.push(p)}return o}function xw(t,s,{clamp:r=!0,ease:o,mixer:c}={}){const d=t.length;if(Ra(d===s.length),d===1)return()=>s[0];if(d===2&&s[0]===s[1])return()=>s[1];const h=t[0]===t[1];t[0]>t[d-1]&&(t=[...t].reverse(),s=[...s].reverse());const p=vw(s,o,c),f=p.length,v=g=>{if(h&&g<t[0])return s[0];let x=0;if(f>1)for(;x<t.length-2&&!(g<t[x+1]);x++);const b=Mi(t[x],t[x+1],g);return p[x](b)};return r?g=>v(Ut(t[0],t[d-1],g)):v}function bw(t,s){const r=t[t.length-1];for(let o=1;o<=s;o++){const c=Mi(0,s,o);t.push(ke(r,1,c))}}function ww(t){const s=[0];return bw(s,t.length-1),s}function kw(t,s){return t.map(r=>r*s)}function jw(t,s){return t.map(()=>s||$f).splice(0,t.length-1)}function Pi({duration:t=300,keyframes:s,times:r,ease:o="easeInOut"}){const c=_b(o)?o.map(Rm):Rm(o),d={done:!1,value:s[0]};if(s.length===2&&!Array.isArray(c)&&(!r||r.length!==2||r[0]===0&&r[1]===1)){const[f,v]=s,g=f===v?void 0:(ln.mix||tu)(f,v);return{calculatedDuration:t,next:x=>(d.value=g?g(c(t>0?Ut(0,1,x/t):1)):v,d.done=x>=t,d)}}const h=kw(r&&r.length===s.length?r:ww(s),t),p=xw(h,s,{ease:Array.isArray(c)?c:jw(s,c)});return{calculatedDuration:t,next:f=>(d.value=p(f),d.done=f>=t,d)}}const Sw=5;function Nw(t,s,r){const o=Math.max(s-Sw,0);return Lf(r-t(o),s-o)}function Cw(t,s,r=0){return s<=0?r:t.velocity?t.velocity(s):Nw(o=>t.next(o).value,s,t.next(s).value)}const Tw=t=>t!==null;function La(t,{repeat:s,repeatType:r="loop"},o,c=1){const d=t.filter(Tw),p=c<0||s&&r!=="loop"&&s%2===1?0:d.length-1;return!p||o===void 0?d[p]:o}const Pw={decay:wc,inertia:wc,tween:Pi,keyframes:Pi,spring:ka};function rg(t){typeof t.type=="string"&&(t.type=Pw[t.type])}function ag(t,s){return{kind:t,animation:s,timestamp:rt.now(),frameTimestamp:Ke.timestamp,frameIsProcessing:Ke.isProcessing}}function og(t,s,r){const o=globalThis.__MOTION_INSPECT__;if(o)try{o({...ag("animation-start",t),options:r?{...s,...r}:s})}catch{}}function Aw(t,s){const r=globalThis.__MOTION_INSPECT__;if(r)try{r({...ag("layout-animation-start",t),node:s})}catch{}}class iu{constructor(){this.isResolved=!1}get finished(){return this._finished||(this._finished=this.isResolved?Promise.resolve():new Promise(s=>{this._resolve=s})),this._finished}updateFinished(){this._finished=this._resolve=void 0,this.isResolved=!1}notifyFinished(){var s;this.isResolved=!0,(s=this._resolve)==null||s.call(this)}then(s,r){return this.finished.then(s,r)}}const Ew=t=>t/100;class ja extends iu{constructor(s){super(),this.state="idle",this.startTime=null,this.isStopped=!1,this.currentTime=0,this.holdTime=null,this.playbackSpeed=1,this.delayState={done:!1,value:void 0},this.stop=()=>{var o,c;const{motionValue:r}=this.options;r&&r.updatedAt!==rt.now()&&this.tick(rt.now()),this.isStopped=!0,this.state!=="idle"&&(this.teardown(),(c=(o=this.options).onStop)==null||c.call(o))},this.options=s,this.initAnimation(),this.play(),s.autoplay===!1&&this.pause(),og(this,this.options)}initAnimation(){const{options:s}=this;rg(s);const{type:r=Pi,repeat:o=0,repeatDelay:c=0,repeatType:d,velocity:h=0}=s;let{keyframes:p}=s;const f=r||Pi;f!==Pi&&typeof p[0]!="number"&&(this.mixKeyframes=Ii(Ew,tu(p[0],p[1])),p=[0,100]);const v=f(p===s.keyframes?s:{...s,keyframes:p});d==="mirror"&&(this.mirroredGenerator=f({...s,keyframes:[...p].reverse(),velocity:-h})),v.calculatedDuration===null&&(v.calculatedDuration=su(v));const{calculatedDuration:g}=v;this.calculatedDuration=g,this.resolvedDuration=g+c,this.totalDuration=this.resolvedDuration*(o+1)-c,this.generator=v}updateTime(s){const r=Math.round(s-this.startTime)*this.playbackSpeed;this.holdTime!==null?this.currentTime=this.holdTime:this.currentTime=r}tick(s,r=!1){const{generator:o,totalDuration:c,mixKeyframes:d,mirroredGenerator:h,resolvedDuration:p,calculatedDuration:f}=this;if(this.startTime===null)return o.next(0);const{delay:v=0,keyframes:g,repeat:x,repeatType:b,repeatDelay:j,type:k,onUpdate:S,finalKeyframe:N}=this.options;this.speed>0?this.startTime=Math.min(this.startTime,s):this.speed<0&&(this.startTime=Math.min(s-c/this.speed,this.startTime)),r?this.currentTime=s:this.updateTime(s);const O=this.currentTime-v*(this.playbackSpeed>=0?1:-1),M=this.playbackSpeed>=0?O<0:O>c;this.currentTime=Math.max(O,0),this.state==="finished"&&this.holdTime===null&&(this.currentTime=c);let L=this.currentTime,I=o;if(x){const z=Math.min(this.currentTime,c)/p;let re=Math.floor(z),Y=z%1;!Y&&z>=1&&(Y=1),Y===1&&re--,re=Math.min(re,x+1),!!(re%2)&&(b==="reverse"?(Y=1-Y,j&&(Y-=j/p)):b==="mirror"&&(I=h)),L=Ut(0,1,Y)*p}let D;M?(this.delayState.value=g[0],D=this.delayState):D=I.next(L),d&&!M&&(D.value=d(D.value));let{done:B}=D;!M&&f!==null&&(B=this.playbackSpeed>=0?this.currentTime>=c:this.currentTime<=0);const V=this.holdTime===null&&(this.state==="finished"||this.state==="running"&&B);return V&&k!==wc&&(D.value=La(g,this.options,N,this.speed)),S&&S(D.value),V&&this.finish(),D}then(s,r){return this.finished.then(s,r)}get duration(){return kt(this.calculatedDuration)}get iterationDuration(){const{delay:s=0}=this.options||{};return this.duration+kt(s)}get time(){return kt(this.currentTime)}set time(s){s=Mt(s),this.currentTime=s,this.startTime===null||this.holdTime!==null||this.playbackSpeed===0?this.holdTime=s:this.driver&&(this.startTime=this.driver.now()-s/this.playbackSpeed),this.driver?this.driver.start(!1):(this.startTime=0,this.state="paused",this.holdTime=s,this.tick(s))}getGeneratorVelocity(){return Cw(this.generator,this.currentTime,this.options.velocity)}get speed(){return this.playbackSpeed}set speed(s){const r=this.playbackSpeed!==s;r&&this.driver&&this.updateTime(rt.now()),this.playbackSpeed=s,r&&this.driver&&(this.time=kt(this.currentTime))}play(){var c,d;if(this.isStopped)return;const{driver:s=hw,startTime:r}=this.options;this.driver||(this.driver=s(h=>this.tick(h))),(d=(c=this.options).onPlay)==null||d.call(c);const o=this.driver.now();this.state==="finished"?(this.updateFinished(),this.startTime=o):this.holdTime!==null?this.startTime=o-this.holdTime:this.startTime||(this.startTime=r??o),this.state==="finished"&&this.speed<0&&(this.startTime+=this.calculatedDuration),this.holdTime=null,this.state="running",this.driver.start()}pause(){this.state="paused",this.updateTime(rt.now()),this.holdTime=this.currentTime}complete(){this.state!=="running"&&this.play(),this.state="finished",this.holdTime=null}finish(){var s,r;this.notifyFinished(),this.teardown(),this.state="finished",(r=(s=this.options).onComplete)==null||r.call(s)}cancel(){var s,r;this.holdTime=null,this.startTime=0,this.tick(0),this.teardown(),(r=(s=this.options).onCancel)==null||r.call(s)}teardown(){this.state="idle",this.stopDriver(),this.startTime=this.holdTime=null}stopDriver(){this.driver&&(this.driver.stop(),this.driver=void 0)}sample(s){return this.startTime=0,this.tick(s,!0)}attachTimeline(s){var r;return this.options.allowFlatten&&(this.options.type="keyframes",this.options.ease="linear",this.initAnimation()),(r=this.driver)==null||r.stop(),s.observe(this)}}const Mw=new Set(["brightness","contrast","saturate","opacity"]);function _w(t){const[s,r]=t.slice(0,-1).split("(");if(s==="drop-shadow")return t;const[o]=r.match(Jc)||[];if(!o)return t;const c=r.replace(o,"");let d=Mw.has(s)?1:0;return o!==r&&(d*=100),s+"("+d+c+")"}const Dw=/\b([a-z-]*)\(.*?\)/gu,kc={...jt,getAnimatableNone:t=>{const s=t.match(Dw);return s?s.map(_w).join(" "):t}},jc={...jt,getAnimatableNone:t=>{const s=jt.parse(t);return jt.createTransformer(t)(s.map(o=>typeof o=="number"?0:typeof o=="object"?{...o,alpha:1}:o))}},zm={...Vs,transform:Math.round},Rw={rotate:on,pathRotation:on,rotateX:on,rotateY:on,rotateZ:on,scale:ea,scaleX:ea,scaleY:ea,scaleZ:ea,skew:on,skewX:on,skewY:on,distance:te,translateX:te,translateY:te,translateZ:te,x:te,y:te,z:te,perspective:te,transformPerspective:te,opacity:_i,originX:Im,originY:Im,originZ:te},Sa={borderWidth:te,borderTopWidth:te,borderRightWidth:te,borderBottomWidth:te,borderLeftWidth:te,borderRadius:te,borderTopLeftRadius:te,borderTopRightRadius:te,borderBottomRightRadius:te,borderBottomLeftRadius:te,width:te,maxWidth:te,height:te,maxHeight:te,top:te,right:te,bottom:te,left:te,inset:te,insetBlock:te,insetBlockStart:te,insetBlockEnd:te,insetInline:te,insetInlineStart:te,insetInlineEnd:te,padding:te,paddingTop:te,paddingRight:te,paddingBottom:te,paddingLeft:te,paddingBlock:te,paddingBlockStart:te,paddingBlockEnd:te,paddingInline:te,paddingInlineStart:te,paddingInlineEnd:te,margin:te,marginTop:te,marginRight:te,marginBottom:te,marginLeft:te,marginBlock:te,marginBlockStart:te,marginBlockEnd:te,marginInline:te,marginInlineStart:te,marginInlineEnd:te,fontSize:te,backgroundPositionX:te,backgroundPositionY:te,...Rw,zIndex:zm,fillOpacity:_i,strokeOpacity:_i,numOctaves:zm},Lw={...Sa,color:qe,backgroundColor:qe,outlineColor:qe,fill:qe,stroke:qe,borderColor:qe,borderTopColor:qe,borderRightColor:qe,borderBottomColor:qe,borderLeftColor:qe,filter:kc,WebkitFilter:kc,mask:jc,WebkitMask:jc},lg=t=>Lw[t],Iw=new Set([kc,jc]);function ru(t,s){let r=lg(t);return Iw.has(r)||(r=jt),r.getAnimatableNone?r.getAnimatableNone(s):void 0}function Vw(t){for(let s=1;s<t.length;s++)t[s]??(t[s]=t[s-1])}const Zn=t=>t*180/Math.PI,Sc=t=>{const s=Zn(Math.atan2(t[1],t[0]));return Nc(s)},Fw={x:4,y:5,translateX:4,translateY:5,scaleX:0,scaleY:3,scale:t=>(Math.abs(t[0])+Math.abs(t[3]))/2,rotate:Sc,rotateZ:Sc,skewX:t=>Zn(Math.atan(t[1])),skewY:t=>Zn(Math.atan(t[2])),skew:t=>(Math.abs(t[1])+Math.abs(t[2]))/2},Nc=t=>(t=t%360,t<0&&(t+=360),t),Um=Sc,Wm=t=>Math.sqrt(t[0]*t[0]+t[1]*t[1]),$m=t=>Math.sqrt(t[4]*t[4]+t[5]*t[5]),Bw={x:12,y:13,z:14,translateX:12,translateY:13,translateZ:14,scaleX:Wm,scaleY:$m,scale:t=>(Wm(t)+$m(t))/2,rotateX:t=>Nc(Zn(Math.atan2(t[6],t[5]))),rotateY:t=>Nc(Zn(Math.atan2(-t[2],t[0]))),rotateZ:Um,rotate:Um,skewX:t=>Zn(Math.atan(t[4])),skewY:t=>Zn(Math.atan(t[1])),skew:t=>(Math.abs(t[1])+Math.abs(t[4]))/2};function Cc(t){return t.includes("scale")?1:0}function Tc(t,s){if(!t||t==="none")return Cc(s);const r=t.match(/^matrix3d\(([-\d.e\s,]+)\)$/u);let o,c;if(r)o=Bw,c=r;else{const p=t.match(/^matrix\(([-\d.e\s,]+)\)$/u);o=Fw,c=p}if(!c)return Cc(s);const d=o[s],h=c[1].split(",").map(zw);return typeof d=="function"?d(h):h[d]}const Ow=(t,s)=>{const{transform:r="none"}=getComputedStyle(t);return Tc(r,s)};function zw(t){return parseFloat(t.trim())}const Fs=["transformPerspective","x","y","z","translateX","translateY","translateZ","scale","scaleX","scaleY","rotate","rotateX","rotateY","rotateZ","skew","skewX","skewY"],Bs=new Set([...Fs,"pathRotation"]),Hm=t=>t===Vs||t===te,Uw=new Set(["x","y","z"]),Ww=Fs.filter(t=>!Uw.has(t));function $w(t){const s=[];return Ww.forEach(r=>{const o=t.getValue(r);if(o!==void 0){const c=o.get(),d=r.startsWith("scale")?1:0;if(c===d)return;s.push([r,c]),o.set(d)}}),s}const Hw=new Set(["bottom","right"]);function Gm(t,s,r,o,c,d){const h=parseFloat(t);if(!isNaN(h))return h;const{min:p,max:f}=s()[r],v=f-p;return d==="border-box"?v:v-parseFloat(o)-parseFloat(c)}const ts={width:({width:t,paddingLeft:s="0",paddingRight:r="0",boxSizing:o},c)=>Gm(t,c,"x",s,r,o),height:({height:t,paddingTop:s="0",paddingBottom:r="0",boxSizing:o},c)=>Gm(t,c,"y",s,r,o),top:({top:t})=>parseFloat(t),left:({left:t})=>parseFloat(t),bottom:({top:t},s)=>{const{y:r}=s();return parseFloat(t)+(r.max-r.min)},right:({left:t},s)=>{const{x:r}=s();return parseFloat(t)+(r.max-r.min)},x:({transform:t})=>Tc(t,"x"),y:({transform:t})=>Tc(t,"y")};ts.translateX=ts.x;ts.translateY=ts.y;const ns=new Set;let Pc=!1,Ac=!1,Ec=!1;function cg(){if(Ac){const t=[],s=new Set,r=new Set;ns.forEach(c=>{c.needsMeasurement&&(t.push(c),s.add(c.element),Hw.has(c.name)&&r.add(c.element))});const o=new Map;r.forEach(c=>{const d=$w(c);d.length&&(o.set(c,d),c.render())}),t.forEach(c=>c.measureInitialState()),s.forEach(c=>{c.render();const d=o.get(c);d&&d.forEach(([h,p])=>{var f;(f=c.getValue(h))==null||f.set(p)})}),t.forEach(c=>c.measureEndState()),t.forEach(c=>{c.suspendedScrollY!==void 0&&window.scrollTo(0,c.suspendedScrollY)})}Ac=!1,Pc=!1,ns.forEach(t=>t.complete(Ec)),ns.clear()}function ug(){ns.forEach(t=>{t.readKeyframes(),t.needsMeasurement&&(Ac=!0)})}function Gw(){Ec=!0,ug(),cg(),Ec=!1}function Kw(t,s,r){if(typeof t=="string"){if(Kc(t)||qc(t))return parseFloat(t);if(!jt.test(t)&&jt.test(r))return ru(s,r)}return t??void 0}class au{constructor(s,r,o,c,d,h=!1){this.state="pending",this.isAsync=!1,this.needsMeasurement=!1,this.unresolvedKeyframes=[...s],this.onComplete=r,this.name=o,this.motionValue=c,this.element=d,this.isAsync=h}scheduleResolve(){this.state="scheduled",this.isAsync?(ns.add(this),Pc||(Pc=!0,je.read(ug),je.resolveKeyframes(cg))):(this.readKeyframes(),this.complete())}readKeyframes(){const{unresolvedKeyframes:s,name:r,element:o,motionValue:c}=this;if(s[0]===null){const d=c==null?void 0:c.get(),h=s[s.length-1];if(d!==void 0)s[0]=d;else if(o&&r){const p=Kw(o.readValue(r,h),r,h);p!==void 0&&(s[0]=p)}s[0]===void 0&&(s[0]=h),c&&d===void 0&&c.set(s[0])}Vw(s)}setFinalKeyframe(){}measureInitialState(){}renderEndStyles(){}measureEndState(){}complete(s=!1){this.state="complete",this.onComplete(this.unresolvedKeyframes,this.finalKeyframe,s),ns.delete(this)}cancel(){this.state==="scheduled"&&(ns.delete(this),this.state="pending")}resume(){this.state==="pending"&&this.scheduleResolve()}}const qw=t=>t.startsWith("--");function dg(t,s,r){qw(s)?t.style.setProperty(s,r):t.style[s]=r}const Xw={};function hg(t,s){const r=Rf(t);return()=>Xw[s]??r()}const Yw=hg(()=>window.ScrollTimeline!==void 0,"scrollTimeline"),mg=hg(()=>{try{document.createElement("div").animate({opacity:0},{easing:"linear(0, 1)"})}catch{return!1}return!0},"linearEasing"),Ti=([t,s,r,o])=>`cubic-bezier(${t}, ${s}, ${r}, ${o})`,Km={linear:"linear",ease:"ease",easeIn:"ease-in",easeOut:"ease-out",easeInOut:"ease-in-out",circIn:Ti([0,.65,.55,1]),circOut:Ti([.55,0,1,.45]),backIn:Ti([.31,.01,.66,-.59]),backOut:Ti([.33,1.53,.69,.99])};function pg(t,s){if(t)return typeof t=="function"?mg()?ng(t,s):"ease-out":Hf(t)?Ti(t):Array.isArray(t)?t.map(r=>pg(r,s)||Km.easeOut):Km[t]}function Qw(t,s,r,{delay:o=0,duration:c=300,repeat:d=0,repeatType:h="loop",ease:p="easeOut",times:f}={},v=void 0){const g={[s]:r};f&&(g.offset=f);const x=pg(p,c);Array.isArray(x)&&(g.easing=x);const b={delay:o,duration:c,easing:Array.isArray(x)?"linear":x,fill:"both",iterations:d+1,direction:h==="reverse"?"alternate":"normal"};return v&&(b.pseudoElement=v),t.animate(g,b)}function fg(t){return typeof t=="function"&&"applyToOptions"in t}function Jw({type:t,...s}){return fg(t)&&mg()?t.applyToOptions(s):(s.duration??(s.duration=300),s.ease??(s.ease="easeOut"),s)}class gg extends iu{constructor(s){if(super(),this.finishedTime=null,this.isStopped=!1,this.manualStartTime=null,!s)return;const{element:r,name:o,keyframes:c,pseudoElement:d,allowFlatten:h=!1,finalKeyframe:p,onComplete:f}=s;this.isPseudoElement=!!d,this.allowFlatten=h,this.options=s,Ra(typeof s.type!="string");const v=Jw(s);this.animation=Qw(r,o,c,v,d),v.autoplay===!1&&this.animation.pause(),this.animation.onfinish=()=>{if(this.finishedTime=this.time,!d){const g=La(c,this.options,p,this.speed);this.updateMotionValue&&this.updateMotionValue(g),dg(r,o,g),this.animation.cancel()}f==null||f(),this.notifyFinished()},og(this,s,v)}play(){this.isStopped||(this.manualStartTime=null,this.animation.play(),this.state==="finished"&&this.updateFinished())}pause(){this.animation.pause()}complete(){var s,r;(r=(s=this.animation).finish)==null||r.call(s)}cancel(){try{this.animation.cancel()}catch{}}stop(){if(this.isStopped)return;this.isStopped=!0;const{state:s}=this;s==="idle"||s==="finished"||(this.updateMotionValue?this.updateMotionValue():this.commitStyles(),this.isPseudoElement||this.cancel())}commitStyles(){var r,o,c;const s=(r=this.options)==null?void 0:r.element;!this.isPseudoElement&&(s!=null&&s.isConnected)&&((c=(o=this.animation).commitStyles)==null||c.call(o))}get duration(){var r,o;const s=((o=(r=this.animation.effect)==null?void 0:r.getComputedTiming)==null?void 0:o.call(r).duration)||0;return kt(Number(s))}get iterationDuration(){const{delay:s=0}=this.options||{};return this.duration+kt(s)}get time(){return kt(Number(this.animation.currentTime)||0)}set time(s){const r=this.finishedTime!==null;this.manualStartTime=null,this.finishedTime=null,this.animation.currentTime=Mt(s),r&&this.animation.pause()}get speed(){return this.animation.playbackRate}set speed(s){s<0&&(this.finishedTime=null),this.animation.playbackRate=s}get state(){return this.finishedTime!==null?"finished":this.animation.playState}get startTime(){return this.manualStartTime??Number(this.animation.startTime)}set startTime(s){this.manualStartTime=this.animation.startTime=s}attachTimeline({timeline:s,rangeStart:r,rangeEnd:o,observe:c}){var d;return this.allowFlatten&&((d=this.animation.effect)==null||d.updateTiming({easing:"linear"})),this.animation.onfinish=null,s&&Yw()?(this.animation.timeline=s,r&&(this.animation.rangeStart=r),o&&(this.animation.rangeEnd=o),zt):c(this)}}const yg={anticipate:zf,backInOut:Of,circInOut:Wf};function Zw(t){return t in yg}function ek(t){typeof t.ease=="string"&&Zw(t.ease)&&(t.ease=yg[t.ease])}const Yl=10;class tk extends gg{constructor(s){ek(s),rg(s),super(s),s.startTime!==void 0&&s.autoplay!==!1&&(this.startTime=s.startTime),this.options=s}updateMotionValue(s){const{motionValue:r,onUpdate:o,onComplete:c,element:d,...h}=this.options;if(!r)return;if(s!==void 0){r.set(s);return}const p=new ja({...h,autoplay:!1}),f=Math.max(Yl,rt.now()-this.startTime),v=Ut(0,Yl,f-Yl),g=p.sample(f).value,{name:x}=this.options;d&&x&&dg(d,x,g),r.setWithVelocity(p.sample(Math.max(0,f-v)).value,g,v),p.stop()}}const qm=(t,s)=>s==="zIndex"?!1:!!(typeof t=="number"||Array.isArray(t)||typeof t=="string"&&(jt.test(t)||t==="0")&&!t.startsWith("url("));function nk(t){const s=t[0];if(t.length===1)return!0;for(let r=0;r<t.length;r++)if(t[r]!==s)return!0}function sk(t,s,r,o){const c=t[0];if(c===null)return!1;if(s==="display"||s==="visibility")return!0;const d=t[t.length-1],h=qm(c,s),p=qm(d,s);return!h||!p?!1:nk(t)||(r==="spring"||fg(r))&&o}function Mc(t){t.duration=0,t.type="keyframes"}const _c=new Set(["opacity","clipPath","filter","transform","backgroundColor"]),ik=/^(?:oklch|oklab|lab|lch|color|color-mix|light-dark)\(/;function rk(t){for(let s=0;s<t.length;s++)if(typeof t[s]=="string"&&ik.test(t[s]))return!0;return!1}const Xm=new Set(["color","backgroundColor","outlineColor","fill","stroke","borderColor","borderTopColor","borderRightColor","borderBottomColor","borderLeftColor"]),ak=Rf(()=>Object.hasOwnProperty.call(Element.prototype,"animate"));function ok(t){var x;const{motionValue:s,name:r,repeatDelay:o,repeatType:c,damping:d,type:h,keyframes:p}=t;if(!r||!(_c.has(r)||Xm.has(r)))return!1;const f=(x=s==null?void 0:s.owner)==null?void 0:x.current;if(!(f instanceof HTMLElement)&&!(f instanceof SVGElement))return!1;const{onUpdate:v,transformTemplate:g}=s.owner.getProps();return ak()&&(_c.has(r)||Xm.has(r)&&rk(p))&&(r!=="transform"||!g)&&!v&&!o&&c!=="mirror"&&d!==0&&h!=="inertia"}const lk=40;class ck extends iu{constructor(s){var f;super(),this.stop=()=>{var v,g;this._animation&&(this._animation.stop(),(v=this.stopTimeline)==null||v.call(this)),(g=this.keyframeResolver)==null||g.cancel()},this.createdAt=rt.now();const{keyframes:r,name:o,motionValue:c,element:d}=s,h=s;h.autoplay??(h.autoplay=!0),h.delay??(h.delay=0),h.type??(h.type="keyframes"),h.repeat??(h.repeat=0),h.repeatDelay??(h.repeatDelay=0),h.repeatType??(h.repeatType="loop");const p=(d==null?void 0:d.KeyframeResolver)||au;this.keyframeResolver=new p(r,(v,g,x)=>this.onKeyframesResolved(v,g,h,!x),o,c,d),(f=this.keyframeResolver)==null||f.scheduleResolve()}onKeyframesResolved(s,r,o,c){var N,O;this.keyframeResolver=void 0;const{name:d,type:h,velocity:p,delay:f,isHandoff:v,onUpdate:g}=o;this.resolvedAt=rt.now();let x=!0;sk(s,d,h,p)||(x=!1,(ln.instantAnimations||!f)&&(g==null||g(La(s,o,r))),s[0]=s[s.length-1],Mc(o),o.repeat=0);const b=c?this.resolvedAt?this.resolvedAt-this.createdAt>lk?this.resolvedAt:this.createdAt:this.createdAt:void 0,{onComplete:j}=o;o.startTime??(o.startTime=b),o.finalKeyframe=r,o.keyframes=s,o.onComplete=()=>{j==null||j(),this.notifyFinished()};const k=x&&!v&&ok(o);let S;if(k){o.element=(O=(N=o.motionValue)==null?void 0:N.owner)==null?void 0:O.current;try{S=new tk(o)}catch{S=new ja(o)}}else S=new ja(o);this.pendingTimeline&&(this.stopTimeline=S.attachTimeline(this.pendingTimeline),this.pendingTimeline=void 0),this._animation=S}get finished(){return this._animation?this._animation.finished:super.finished}then(s,r){return this.finished.finally(s).then(()=>{})}get animation(){var s;return this._animation||((s=this.keyframeResolver)==null||s.resume(),Gw()),this._animation}get duration(){return this.animation.duration}get iterationDuration(){return this.animation.iterationDuration}get time(){return this.animation.time}set time(s){this.animation.time=s}get speed(){return this.animation.speed}get state(){return this.animation.state}set speed(s){this.animation.speed=s}get startTime(){return this.animation.startTime}attachTimeline(s){return this._animation?this.stopTimeline=this.animation.attachTimeline(s):this.pendingTimeline=s,()=>this.stop()}play(){this.animation.play()}pause(){this.animation.pause()}complete(){this.animation.complete()}cancel(){var s;this._animation&&this.animation.cancel(),(s=this.keyframeResolver)==null||s.cancel()}}function vg(t,s,r,o=0,c=1){const d=Array.from(t).sort((v,g)=>v.sortNodePosition(g)).indexOf(s),h=t.size,p=(h-1)*o;return typeof r=="function"?r(d,h):c===1?d*o:p-d*o}const Ym=30,uk=t=>!isNaN(parseFloat(t));class dk{constructor(s,r={}){this.canTrackVelocity=null,this.events={},this.updateAndNotify=o=>{const c=rt.now();if(this.updatedAt!==c&&this.setPrevFrameValue(),this.prev=this.current,this.setCurrent(o),this.current!==this.prev&&(this.notifyChange(),this.dependents))for(const d of this.dependents)d.dirty()},this.hasAnimated=!1,this.setCurrent(s),this.owner=r.owner}setCurrent(s){this.current=s,this.updatedAt=rt.now(),this.canTrackVelocity===null&&s!==void 0&&(this.canTrackVelocity=uk(this.current))}setPrevFrameValue(s=this.current){this.prevFrameValue=s,this.prevUpdatedAt=this.updatedAt}onChange(s){return this.on("change",s)}on(s,r){var o;return s==="change"?this.onChangeSubscribe(r):((o=this.events)[s]||(o[s]=new xa)).add(r)}onChangeSubscribe(s){const{events:r}=this;return!r.change&&!this.changeSubscriber?this.changeSubscriber=s:(r.change||(r.change=new xa,r.change.add(this.changeSubscriber),this.changeSubscriber=void 0),r.change.add(s)),()=>{var o;this.changeSubscriber===s?this.changeSubscriber=void 0:(o=r.change)==null||o.remove(s),this.stopIfUnobserved()}}stopIfUnobserved(){je.read(()=>{var s;!this.changeSubscriber&&!((s=this.events.change)!=null&&s.getSize())&&this.stop()})}clearListeners(){this.changeSubscriber=void 0;for(const s in this.events)this.events[s].clear()}attach(s,r){this.passiveEffect=s,this.stopPassiveEffect=r}set(s){this.passiveEffect?this.passiveEffect(s,this.updateAndNotify):this.updateAndNotify(s)}setWithVelocity(s,r,o){this.set(r),this.prev=void 0,this.prevFrameValue=s,this.prevUpdatedAt=this.updatedAt-o}jump(s,r=!0){this.updateAndNotify(s),this.prev=s,this.prevUpdatedAt=this.prevFrameValue=void 0,r&&this.stop(),this.stopPassiveEffect&&this.stopPassiveEffect()}dirty(){this.notifyChange()}notifyChange(){var o;const{current:s,changeSubscriber:r}=this;r?r(s):(o=this.events.change)==null||o.notify(s)}addDependent(s){this.dependents||(this.dependents=new Set),this.dependents.add(s)}removeDependent(s){this.dependents&&this.dependents.delete(s)}get(){return this.current}getPrevious(){return this.prev}getVelocity(){const s=rt.now();if(!this.canTrackVelocity||this.prevFrameValue===void 0||s-this.updatedAt>Ym)return 0;const r=Math.min(this.updatedAt-this.prevUpdatedAt,Ym);return Lf(parseFloat(this.current)-parseFloat(this.prevFrameValue),r)}start(s){return this.stop(),new Promise(r=>{var d;this.hasAnimated=!0;let o=!1,c;c=s(()=>{var h;o=!0,(h=this.events.animationComplete)==null||h.notify(),this.animation===c&&this.clearAnimation(),r()}),o||(this.animation=c),(d=this.events.animationStart)==null||d.notify()})}stop(){this.animation&&(this.animation.stop(),this.events.animationCancel&&this.events.animationCancel.notify()),this.clearAnimation()}isAnimating(){return!!this.animation}clearAnimation(){this.animation=void 0}destroy(){var s,r;(s=this.dependents)==null||s.clear(),(r=this.events.destroy)==null||r.notify(),this.clearListeners(),this.stop(),this.stopPassiveEffect&&this.stopPassiveEffect()}}function Is(t,s){return new dk(t,s)}function xg(t,s){if(t!=null&&t.inherit&&s){const{inherit:r,...o}=t;return{...s,...o}}return t}function ou(t,s){const r=(t==null?void 0:t[s])??(t==null?void 0:t.default)??t;return r!==t?xg(r,t):r}const hk={type:"spring",stiffness:500,damping:25,restSpeed:10},mk=t=>({type:"spring",stiffness:550,damping:t===0?2*Math.sqrt(550):30,restSpeed:10}),pk={type:"keyframes",duration:.8},fk={type:"keyframes",ease:[.25,.1,.35,1],duration:.3},gk=(t,{keyframes:s})=>s.length>2?pk:Bs.has(t)?t.startsWith("scale")?mk(s[1]):hk:fk,yk=new Set(["when","delay","delayChildren","staggerChildren","staggerDirection","repeat","repeatType","repeatDelay","from","elapsed"]);function vk(t){for(const s in t)if(!yk.has(s))return!0;return!1}const lu=(t,s,r,o={},c,d)=>h=>{const p=ou(o,t)||{},f=p.delay||o.delay||0;let{elapsed:v=0}=o;v=v-Mt(f);const g={keyframes:Array.isArray(r)?r:[null,r],ease:"easeOut",velocity:s.getVelocity(),...p,delay:-v,onUpdate:b=>{s.set(b),p.onUpdate&&p.onUpdate(b)},onComplete:()=>{h(),p.onComplete&&p.onComplete()},name:t,motionValue:s,element:d?void 0:c};vk(p)||Object.assign(g,gk(t,g)),g.duration&&(g.duration=Mt(g.duration)),g.repeatDelay&&(g.repeatDelay=Mt(g.repeatDelay)),g.from!==void 0&&(g.keyframes[0]=g.from);let x=!1;if((g.type===!1||g.duration===0&&!g.repeatDelay)&&(Mc(g),g.delay===0&&(x=!0)),(ln.instantAnimations||ln.skipAnimations||c!=null&&c.shouldSkipAnimations||p.skipAnimations)&&(x=!0,Mc(g),g.delay=0),g.allowFlatten=!p.type&&!p.ease,x&&!d&&s.get()!==void 0){const b=La(g.keyframes,p);if(b!==void 0){je.update(()=>{g.onUpdate(b),g.onComplete()});return}}return p.isSync?new ja(g):new ck(g)},xk=/^var\(--(?:([\w-]+)|([\w-]+), ?([a-zA-Z\d ()%#.,-]+))\)/u;function bk(t){const s=xk.exec(t);if(!s)return[,];const[,r,o,c]=s;return[`--${r??o}`,c]}function bg(t,s,r=1){const[o,c]=bk(t);if(!o)return;const d=window.getComputedStyle(s).getPropertyValue(o);if(d){const h=d.trim();return Kc(h)?parseFloat(h):h}return Qc(c)?bg(c,s,r+1):c}function Qm(t){const s=[{},{}];return t==null||t.values.forEach((r,o)=>{s[0][o]=r.get(),s[1][o]=r.getVelocity()}),s}function cu(t,s,r,o){if(typeof s=="function"){const[c,d]=Qm(o);s=s(r!==void 0?r:t.custom,c,d)}if(typeof s=="string"&&(s=t.variants&&t.variants[s]),typeof s=="function"){const[c,d]=Qm(o);s=s(r!==void 0?r:t.custom,c,d)}return s}function ss(t,s,r){const o=t.getProps();return cu(o,s,r!==void 0?r:o.custom,t)}const wg=new Set(["width","height","top","left","right","bottom",...Fs]),Dc=t=>Array.isArray(t);function wk(t,s,r){t.hasValue(s)?t.getValue(s).set(r):t.addValue(s,Is(r))}function kk(t){return Dc(t)?t[t.length-1]||0:t}function jk(t,s){const r=ss(t,s);let{transitionEnd:o={},transition:c={},...d}=r||{};d={...d,...o};for(const h in d){const p=kk(d[h]);wk(t,h,p)}}const et=t=>!!(t&&t.getVelocity);function Sk(t){return!!(et(t)&&t.add)}function Rc(t,s){const r=t.getValue("willChange");if(Sk(r))return r.add(s);if(!r&&ln.WillChange){const o=new ln.WillChange("auto");t.addValue("willChange",o),o.add(s)}}function uu(t){return t.replace(/([A-Z])/g,s=>`-${s.toLowerCase()}`)}const Nk="framerAppearId",kg="data-"+uu(Nk);function jg(t){return t.props[kg]}const Ck=typeof window<"u";function Tk({protectedKeys:t,needsAnimating:s},r){const o=t.hasOwnProperty(r)&&s[r]!==!0;return s[r]=!1,o}function Sg(t,s,{delay:r=0,transitionOverride:o,type:c}={}){let{transition:d,transitionEnd:h,...p}=s;const f=t.getDefaultTransition();d=d?xg(d,f):f;const v=d==null?void 0:d.reduceMotion,g=d==null?void 0:d.skipAnimations;o&&(d=o);const x=[],b=c&&t.animationState&&t.animationState.getState()[c],j=d==null?void 0:d.path;j&&j.animateVisualElement(t,p,d,r,x);for(const k in p){const S=t.getValue(k,t.latestValues[k]??null),N=p[k];if(N===void 0||b&&Tk(b,k))continue;const O={delay:r,...ou(d||{},k)};g&&(O.skipAnimations=!0);const M=S.get();if(M!==void 0&&!S.isAnimating()&&!Array.isArray(N)&&N===M&&!O.velocity){je.update(()=>S.set(N));continue}let L=!1;if(Ck&&window.MotionHandoffAnimation){const B=jg(t);if(B){const V=window.MotionHandoffAnimation(B,k,je);V!==null&&(O.startTime=V,L=!0)}}Rc(t,k);const I=v??t.shouldReduceMotion;S.start(lu(k,S,N,I&&wg.has(k)?{type:!1}:O,t,L));const D=S.animation;D&&x.push(D)}if(h){const k=()=>je.update(()=>{h&&jk(t,h)});x.length?Promise.all(x).then(k):k()}return x}function Lc(t,s,r={}){var f;const o=ss(t,s,r.type==="exit"?(f=t.presenceContext)==null?void 0:f.custom:void 0);let{transition:c=t.getDefaultTransition()||{}}=o||{};r.transitionOverride&&(c=r.transitionOverride);const d=o?()=>Promise.all(Sg(t,o,r)):()=>Promise.resolve(),h=t.variantChildren&&t.variantChildren.size?(v=0)=>{const{delayChildren:g=0,staggerChildren:x,staggerDirection:b}=c;return Pk(t,s,v,g,x,b,r)}:()=>Promise.resolve(),{when:p}=c;if(p){const[v,g]=p==="beforeChildren"?[d,h]:[h,d];return v().then(()=>g())}else return Promise.all([d(),h(r.delay)])}function Pk(t,s,r=0,o=0,c=0,d=1,h){const p=[];for(const f of t.variantChildren)f.notify("AnimationStart",s),p.push(Lc(f,s,{...h,delay:r+(typeof o=="function"?0:o)+vg(t.variantChildren,f,o,c,d)}).then(()=>f.notify("AnimationComplete",s)));return Promise.all(p)}function Ak(t,s,r={}){t.notify("AnimationStart",s);let o;if(Array.isArray(s)){const c=s.map(d=>Lc(t,d,r));o=Promise.all(c)}else if(typeof s=="string")o=Lc(t,s,r);else{const c=typeof s=="function"?ss(t,s,r.custom):s;o=Promise.all(Sg(t,c,r))}return o.then(()=>{t.notify("AnimationComplete",s)})}const Ek={test:t=>t==="auto",parse:t=>t},Mk=t=>s=>s.test(t),_k=[Vs,te,Qt,on,Hb,$b,Ek],Jm=t=>_k.find(Mk(t));function Dk(t){return typeof t=="number"?t===0:t!==null?t==="none"||t==="0"||qc(t):!0}const Rk=new Set(["auto","none","0"]);function Lk(t,s,r){let o=0,c;for(;o<t.length&&!c;){const d=t[o];typeof d=="string"&&!Rk.has(d)&&Qb(d)&&(c=t[o]),o++}if(c&&r)for(const d of s)t[d]!==c&&(t[d]=ru(r,c))}class Ik extends au{constructor(s,r,o,c,d){super(s,r,o,c,d,!0)}readKeyframes(){const{unresolvedKeyframes:s,element:r,name:o}=this;if(!r||!r.current)return;super.readKeyframes();for(let g=0;g<s.length;g++){let x=s[g];if(typeof x=="string"&&(x=x.trim(),Qc(x))){const b=bg(x,r.current);b!==void 0&&(s[g]=b),g===s.length-1&&(this.finalKeyframe=x)}}if(this.resolveNoneKeyframes(),!wg.has(o)||s.length!==2)return;const[c,d]=s;if(typeof c=="number"&&typeof d=="number")return;const h=Jm(c),p=Jm(d),f=Lm(c),v=Lm(d);if(f!==v&&ts[o]){this.needsMeasurement=!0;return}if(h!==p)if(Hm(h)&&Hm(p))for(let g=0;g<s.length;g++){const x=s[g];typeof x=="string"&&(s[g]=parseFloat(x))}else ts[o]&&(this.needsMeasurement=!0)}resolveNoneKeyframes(){const{unresolvedKeyframes:s,name:r}=this,o=[];for(let c=0;c<s.length;c++)(s[c]===null||Dk(s[c]))&&o.push(c);o.length&&Lk(s,o,r)}measure(){const{element:s,name:r}=this;return ts[r](window.getComputedStyle(s.current),()=>s.measureViewportBox())}measureInitialState(){var d;const{element:s,unresolvedKeyframes:r,name:o}=this;if(!s||!s.current)return;o==="height"&&(this.suspendedScrollY=window.pageYOffset),this.measuredOrigin=this.measure(),r[0]=this.measuredOrigin;const c=r[r.length-1];c!==void 0&&((d=this.motionValue)==null||d.jump(c,!1))}measureEndState(){var d,h;const{element:s,unresolvedKeyframes:r}=this;if(!s||!s.current)return;(d=this.motionValue)==null||d.jump(this.measuredOrigin,!1);const o=r.length-1,c=r[o];r[o]=this.measure(),c!==null&&this.finalKeyframe===void 0&&(this.finalKeyframe=c),(h=this.removedTransforms)!=null&&h.length&&this.removedTransforms.forEach(([p,f])=>{s.getValue(p).set(f)}),this.resolveNoneKeyframes()}}const du=["borderTopLeftRadius","borderTopRightRadius","borderBottomRightRadius","borderBottomLeftRadius"];function Vk(t){return Df(t)&&"offsetHeight"in t&&!("ownerSVGElement"in t)}function hu(t){return Df(t)&&"ownerSVGElement"in t}const Ic=(t,s)=>s&&typeof t=="number"?s.transform(t):t;function Ng(t,s,r){if(t==null)return[];if(t instanceof EventTarget)return[t];if(typeof t=="string"){let o=document;const c=(r==null?void 0:r[t])??o.querySelectorAll(t);return c?Array.from(c):[]}return Array.from(t).filter(o=>o!=null)}const Fk={x:"translateX",y:"translateY",z:"translateZ",transformPerspective:"perspective"},Bk=Fs.length;function Ok(t,s,r){let o="",c=!0;for(let h=0;h<Bk;h++){const p=Fs[h],f=t[p];if(f===void 0)continue;let v=!0;if(typeof f=="number")v=f===(p.startsWith("scale")?1:0);else{const g=parseFloat(f);v=p.startsWith("scale")?g===1:g===0}if(!v||r){const g=Ic(f,Sa[p]);if(!v){c=!1;const x=Fk[p]||p;o+=`${x}(${g}) `}r&&(s[p]=g)}}const d=t.pathRotation;return d&&(c=!1,o+=`rotate(${Ic(d,Sa.pathRotation)}) `),o=o.trim(),r?o=r(s,c?"":o):c&&(o="none"),o}function mu(t,s,r){const{style:o,vars:c,transformOrigin:d}=t;let h=!1,p=!1;for(const f in s){const v=s[f];if(Bs.has(f)){h=!0;continue}else if(qf(f)){c[f]=v;continue}else{const g=Ic(v,Sa[f]);f.startsWith("origin")?(p=!0,d[f]=g):o[f]=g}}if(s.transform||(h||r?o.transform=Ok(s,t.transform,r):o.transform&&(o.transform="none")),p){const{originX:f="50%",originY:v="50%",originZ:g=0}=d;o.transformOrigin=`${f} ${v} ${g}`}}const zk={offset:"stroke-dashoffset",array:"stroke-dasharray"},Uk={offset:"strokeDashoffset",array:"strokeDasharray"};function Wk(t,s,r=1,o=0,c=!0){t.pathLength=1;const d=c?zk:Uk;t[d.offset]=`${-o}`,t[d.array]=`${s} ${r}`}const Cg=["transform","opacity","offsetDistance","offsetPath","offsetRotate","offsetAnchor"];function Tg(t,{attrX:s,attrY:r,attrScale:o,pathLength:c,pathSpacing:d=1,pathOffset:h=0,...p},f,v,g){if(mu(t,p,v),f){t.style.viewBox&&(t.attrs.viewBox=t.style.viewBox);return}t.attrs=t.style,t.style={};const{attrs:x,style:b}=t;for(const j of Cg)x[j]!==void 0&&(b[j]=x[j],delete x[j]);(b.transform||x.transformOrigin)&&(b.transformOrigin=x.transformOrigin??"50% 50%",delete x.transformOrigin),b.transform&&(b.transformBox=(g==null?void 0:g.transformBox)??"fill-box",delete x.transformBox),s!==void 0&&(x.x=s),r!==void 0&&(x.y=r),o!==void 0&&(x.scale=o),c!==void 0&&Wk(x,c,d,h,!1)}function Pg({top:t,left:s,right:r,bottom:o}){return{x:{min:s,max:r},y:{min:t,max:o}}}function $k({x:t,y:s}){return{top:s.min,right:t.max,bottom:s.max,left:t.min}}function Hk(t,s){if(!s)return t;const r=s({x:t.left,y:t.top}),o=s({x:t.right,y:t.bottom});return{top:r.y,left:r.x,bottom:o.y,right:o.x}}function Ql(t){return t===void 0||t===1}function Vc({scale:t,scaleX:s,scaleY:r}){return!Ql(t)||!Ql(s)||!Ql(r)}function Xn(t){return Vc(t)||Ag(t)||t.z||t.rotate||t.rotateX||t.rotateY||t.skewX||t.skewY}function Ag(t){return Zm(t.x)||Zm(t.y)}function Zm(t){return t&&t!=="0%"}function Na(t,s,r){const o=t-r,c=s*o;return r+c}function ep(t,s,r,o,c){return c!==void 0&&(t=Na(t,c,o)),Na(t,r,o)+s}function Fc(t,s=0,r=1,o,c){t.min=ep(t.min,s,r,o,c),t.max=ep(t.max,s,r,o,c)}function Eg(t,{x:s,y:r}){Fc(t.x,s.translate,s.scale,s.originPoint),Fc(t.y,r.translate,r.scale,r.originPoint)}const tp=.999999999999,np=1.0000000000001;function Gk(t,s,r,o=!1){var p;const c=r.length;if(!c)return;s.x=s.y=1;let d,h;for(let f=0;f<c;f++){d=r[f],h=d.projectionDelta;const{visualElement:v}=d.options;v&&v.props.style&&v.props.style.display==="contents"||(o&&d.options.layoutScroll&&d.scroll&&d!==d.root&&(Xt(t.x,-d.scroll.offset.x),Xt(t.y,-d.scroll.offset.y)),h&&(s.x*=h.x.scale,s.y*=h.y.scale,Eg(t,h)),o&&Xn(d.latestValues)&&la(t,d.latestValues,(p=d.layout)==null?void 0:p.layoutBox))}s.x<np&&s.x>tp&&(s.x=1),s.y<np&&s.y>tp&&(s.y=1)}function Xt(t,s){t.min+=s,t.max+=s}function sp(t,s,r,o,c=.5){const d=ke(t.min,t.max,c);Fc(t,s,r,d,o)}function ip(t,s){return typeof t=="string"?parseFloat(t)/100*(s.max-s.min):t}function la(t,s,r){const o=r??t;sp(t.x,ip(s.x,o.x),s.scaleX,s.scale,s.originX),sp(t.y,ip(s.y,o.y),s.scaleY,s.scale,s.originY)}function Mg(t,s){return Pg(Hk(t.getBoundingClientRect(),s))}function Kk(t,s,r){const o=Mg(t,r),{scroll:c}=s;return c&&(Xt(o.x,c.offset.x),Xt(o.y,c.offset.y)),o}const{schedule:pu}=Gf(queueMicrotask,!1),Ot={x:!1,y:!1};function _g(){return Ot.x||Ot.y}function qk(t){return t==="x"||t==="y"?Ot[t]?null:(Ot[t]=!0,()=>{Ot[t]=!1}):Ot.x||Ot.y?null:(Ot.x=Ot.y=!0,()=>{Ot.x=Ot.y=!1})}function Dg(t,s){const r=Ng(t),o=new AbortController,c={passive:!0,...s,signal:o.signal};return[r,c,()=>o.abort()]}function Xk(t){return!(t.pointerType==="touch"||_g())}function Yk(t,s,r={}){const[o,c,d]=Dg(t,r);return o.forEach(h=>{let p=!1,f=!1,v;const g=()=>{h.removeEventListener("pointerleave",k)},x=N=>{v&&(v(N),v=void 0),g()},b=N=>{p=!1,window.removeEventListener("pointerup",b),window.removeEventListener("pointercancel",b),f&&(f=!1,x(N))},j=()=>{p=!0,window.addEventListener("pointerup",b,c),window.addEventListener("pointercancel",b,c)},k=N=>{if(N.pointerType!=="touch"){if(p){f=!0;return}x(N)}},S=N=>{if(!Xk(N))return;f=!1;const O=s(h,N);typeof O=="function"&&(v=O,h.addEventListener("pointerleave",k,c))};h.addEventListener("pointerenter",S,c),h.addEventListener("pointerdown",j,c)}),d}const Rg=(t,s)=>s?t===s?!0:Rg(t,s.parentElement):!1,fu=t=>t.pointerType==="mouse"?typeof t.button!="number"||t.button<=0:t.isPrimary!==!1,Qk=new Set(["BUTTON","INPUT","SELECT","TEXTAREA","A"]);function Jk(t){return Qk.has(t.tagName)||t.isContentEditable===!0}const Zk=new Set(["INPUT","SELECT","TEXTAREA"]);function e0(t){return Zk.has(t.tagName)||t.isContentEditable===!0}const ca=new WeakSet;function rp(t){return s=>{s.key==="Enter"&&t(s)}}function Jl(t,s){t.dispatchEvent(new PointerEvent("pointer"+s,{isPrimary:!0,bubbles:!0}))}const t0=(t,s)=>{const r=t.currentTarget;if(!r)return;const o=rp(()=>{if(ca.has(r))return;Jl(r,"down");const c=rp(()=>{Jl(r,"up")}),d=()=>Jl(r,"cancel");r.addEventListener("keyup",c,s),r.addEventListener("blur",d,s)});r.addEventListener("keydown",o,s),r.addEventListener("blur",()=>r.removeEventListener("keydown",o),s)};function ap(t){return fu(t)&&!_g()}const op=new WeakSet;function n0(t,s,r={}){const[o,c,d]=Dg(t,r),h=p=>{const f=p.currentTarget;if(!ap(p)||op.has(p))return;ca.add(f),r.stopPropagation&&op.add(p);const v=s(f,p),g={...c,capture:!0},x=(k,S)=>{window.removeEventListener("pointerup",b,g),window.removeEventListener("pointercancel",j,g),ca.has(f)&&ca.delete(f),ap(k)&&typeof v=="function"&&v(k,{success:S})},b=k=>{x(k,f===window||f===document||r.useGlobalTarget||Rg(f,k.target))},j=k=>{x(k,!1)};window.addEventListener("pointerup",b,g),window.addEventListener("pointercancel",j,g)};return o.forEach(p=>{(r.useGlobalTarget?window:p).addEventListener("pointerdown",h,c),Vk(p)&&(p.addEventListener("focus",v=>t0(v,c)),!Jk(p)&&!p.hasAttribute("tabindex")&&(p.tabIndex=0))}),d}const ua=new WeakMap;let An;const Lg=(t,s,r)=>(o,c)=>c&&c[0]?c[0][t+"Size"]:hu(o)&&"getBBox"in o?o.getBBox()[s]:o[r],s0=Lg("inline","width","offsetWidth"),i0=Lg("block","height","offsetHeight");function r0({target:t,borderBoxSize:s}){var r;(r=ua.get(t))==null||r.forEach(o=>{o(t,{get width(){return s0(t,s)},get height(){return i0(t,s)}})})}function a0(t){t.forEach(r0)}function o0(){typeof ResizeObserver>"u"||(An=new ResizeObserver(a0))}function l0(t,s){An||o0();const r=Ng(t);return r.forEach(o=>{let c=ua.get(o);c||(c=new Set,ua.set(o,c)),c.add(s),An==null||An.observe(o)}),()=>{r.forEach(o=>{const c=ua.get(o);c==null||c.delete(s),c!=null&&c.size||An==null||An.unobserve(o)})}}const da=new Set;let Ds;function c0(){Ds=()=>{const t={get width(){return window.innerWidth},get height(){return window.innerHeight}};da.forEach(s=>s(t))},window.addEventListener("resize",Ds)}function u0(t){return da.add(t),Ds||c0(),()=>{da.delete(t),!da.size&&typeof Ds=="function"&&(window.removeEventListener("resize",Ds),Ds=void 0)}}function lp(t,s){return typeof t=="function"?u0(t):l0(t,s)}function d0(t){return hu(t)&&t.tagName==="svg"}const cp=()=>({translate:0,scale:1,origin:0,originPoint:0}),Rs=()=>({x:cp(),y:cp()}),up=()=>({min:0,max:0}),Ge=()=>({x:up(),y:up()}),h0=new WeakMap;function Ia(t){return t!==null&&typeof t=="object"&&typeof t.start=="function"}function Ri(t){return typeof t=="string"||Array.isArray(t)}const gu=["animate","whileInView","whileFocus","whileHover","whileTap","whileDrag","exit"],Ca=["initial",...gu];function Va(t){if(Ia(t.animate))return!0;for(let s=0;s<Ca.length;s++)if(Ri(t[Ca[s]]))return!0;return!1}function Ig(t){return!!(Va(t)||t.variants)}function m0(t,s,r){for(const o in s){const c=s[o],d=r[o];if(et(c))t.addValue(o,c);else if(et(d))t.addValue(o,Is(c,{owner:t}));else if(d!==c)if(t.hasValue(o)){const h=t.getValue(o);h.liveStyle===!0?h.jump(c):h.hasAnimated||h.set(c)}else{const h=t.getStaticValue(o);t.addValue(o,Is(h!==void 0?h:c,{owner:t}))}}for(const o in r)s[o]===void 0&&t.removeValue(o);return s}const Ta={current:null},yu={current:!1},p0=typeof window<"u";function Vg(){if(yu.current=!0,!!p0)if(window.matchMedia){const t=window.matchMedia("(prefers-reduced-motion)"),s=()=>Ta.current=t.matches;t.addEventListener("change",s),s()}else Ta.current=!1}const dp=["AnimationStart","AnimationComplete","Update","BeforeLayoutMeasure","LayoutMeasure","LayoutAnimationStart","LayoutAnimationComplete"];let Pa={};function Fg(t){Pa=t}function f0(){return Pa}class g0{scrapeMotionValuesFromProps(s,r,o){return{}}constructor({parent:s,props:r,presenceContext:o,reducedMotionConfig:c,skipAnimations:d,blockInitialAnimation:h,visualState:p},f={}){this.current=null,this.children=new Set,this.isVariantNode=!1,this.isControllingVariants=!1,this.shouldReduceMotion=null,this.shouldSkipAnimations=!1,this.values=new Map,this.KeyframeResolver=au,this.features={},this.valueSubscriptions=new Map,this.prevMotionValues={},this.hasBeenMounted=!1,this.events={},this.propEventSubscriptions={},this.notifyUpdate=()=>this.notify("Update",this.latestValues),this.render=()=>{this.current&&(this.triggerBuild(),this.renderInstance(this.current,this.renderState,this.props.style,this.projection))},this.renderScheduledAt=0,this.scheduleRender=()=>{const j=rt.now();this.renderScheduledAt<j&&(this.renderScheduledAt=j,je.render(this.render,!1,!0))};const{latestValues:v,renderState:g}=p;this.latestValues=v,this.baseTarget={...v},this.initialValues=r.initial?{...v}:{},this.renderState=g,this.parent=s,this.props=r,this.presenceContext=o,this.depth=s?s.depth+1:0,this.reducedMotionConfig=c,this.skipAnimationsConfig=d,this.options=f,this.blockInitialAnimation=!!h,this.isControllingVariants=Va(r),this.isVariantNode=Ig(r),this.isVariantNode&&(this.variantChildren=new Set),this.manuallyAnimateOnMount=!!(s&&s.current);const{willChange:x,...b}=this.scrapeMotionValuesFromProps(r,{},this);for(const j in b){const k=b[j];v[j]!==void 0&&et(k)&&k.set(v[j])}}mount(s){var r,o;if(this.hasBeenMounted)for(const c in this.initialValues)(r=this.values.get(c))==null||r.jump(this.initialValues[c]),this.latestValues[c]=this.initialValues[c];this.current=s,h0.set(s,this),this.projection&&!this.projection.instance&&this.projection.mount(s),this.parent&&this.isVariantNode&&!this.isControllingVariants&&(this.removeFromVariantTree=this.parent.addVariantChild(this)),this.values.forEach((c,d)=>this.bindToMotionValue(d,c)),this.reducedMotionConfig==="never"?this.shouldReduceMotion=!1:this.reducedMotionConfig==="always"?this.shouldReduceMotion=!0:(yu.current||Vg(),this.shouldReduceMotion=Ta.current),this.shouldSkipAnimations=this.skipAnimationsConfig??!1,(o=this.parent)==null||o.addChild(this),this.update(this.props,this.presenceContext),this.hasBeenMounted=!0}unmount(){var s;this.projection&&this.projection.unmount(),Mn(this.notifyUpdate),Mn(this.render),this.valueSubscriptions.forEach(r=>r()),this.valueSubscriptions.clear(),this.removeFromVariantTree&&this.removeFromVariantTree(),(s=this.parent)==null||s.removeChild(this);for(const r in this.events)this.events[r].clear();for(const r in this.features){const o=this.features[r];o&&(o.unmount(),o.isMounted=!1)}this.current=null}addChild(s){this.children.add(s),this.enteringChildren??(this.enteringChildren=new Set),this.enteringChildren.add(s)}removeChild(s){this.children.delete(s),this.enteringChildren&&this.enteringChildren.delete(s)}bindToMotionValue(s,r){if(this.valueSubscriptions.has(s)&&this.valueSubscriptions.get(s)(),r.accelerate&&_c.has(s)&&this.current instanceof HTMLElement){const{factory:h,keyframes:p,times:f,ease:v,duration:g}=r.accelerate,x=new gg({element:this.current,name:s,keyframes:p,times:f,ease:v,duration:Mt(g)}),b=h(x);this.valueSubscriptions.set(s,()=>{b(),x.cancel()});return}const o=Bs.has(s);o&&this.onBindTransform&&this.onBindTransform();const c=r.on("change",h=>{this.latestValues[s]=h,this.props.onUpdate&&je.preRender(this.notifyUpdate),o&&this.projection&&(this.projection.isTransformDirty=!0),this.scheduleRender()});let d;typeof window<"u"&&window.MotionCheckAppearSync&&(d=window.MotionCheckAppearSync(this,s,r)),this.valueSubscriptions.set(s,()=>{c(),d&&d()})}sortNodePosition(s){return!this.current||!this.sortInstanceNodePosition||this.type!==s.type?0:this.sortInstanceNodePosition(this.current,s.current)}updateFeatures(){let s="animation";for(s in Pa){const r=Pa[s];if(!r)continue;const{isEnabled:o,Feature:c}=r;if(!this.features[s]&&c&&o(this.props)&&(this.features[s]=new c(this)),this.features[s]){const d=this.features[s];d.isMounted?d.update():(d.mount(),d.isMounted=!0)}}}triggerBuild(){this.build(this.renderState,this.latestValues,this.props)}measureViewportBox(){return this.current?this.measureInstanceViewportBox(this.current,this.props):Ge()}getStaticValue(s){return this.latestValues[s]}setStaticValue(s,r){this.latestValues[s]=r}update(s,r){(s.transformTemplate||this.props.transformTemplate)&&this.scheduleRender(),this.prevProps=this.props,this.props=s,this.prevPresenceContext=this.presenceContext,this.presenceContext=r;for(let o=0;o<dp.length;o++){const c=dp[o];this.propEventSubscriptions[c]&&(this.propEventSubscriptions[c](),delete this.propEventSubscriptions[c]);const d="on"+c,h=s[d];h&&(this.propEventSubscriptions[c]=this.on(c,h))}this.prevMotionValues=m0(this,this.scrapeMotionValuesFromProps(s,this.prevProps||{},this),this.prevMotionValues),this.handleChildMotionValue&&this.handleChildMotionValue()}getProps(){return this.props}getVariant(s){return this.props.variants?this.props.variants[s]:void 0}getDefaultTransition(){return this.props.transition}getTransformPagePoint(){return this.props.transformPagePoint}getClosestVariantNode(){return this.isVariantNode?this:this.parent?this.parent.getClosestVariantNode():void 0}addVariantChild(s){const r=this.getClosestVariantNode();if(r)return r.variantChildren&&r.variantChildren.add(s),()=>r.variantChildren.delete(s)}addValue(s,r){const o=this.values.get(s);r!==o&&(o&&this.removeValue(s),this.bindToMotionValue(s,r),this.values.set(s,r),this.latestValues[s]=r.get())}removeValue(s){this.values.delete(s);const r=this.valueSubscriptions.get(s);r&&(r(),this.valueSubscriptions.delete(s)),delete this.latestValues[s],this.removeValueFromRenderState(s,this.renderState)}hasValue(s){return this.values.has(s)}getValue(s,r){if(this.props.values&&this.props.values[s])return this.props.values[s];let o=this.values.get(s);return o===void 0&&r!==void 0&&(o=Is(r===null?void 0:r,{owner:this}),this.addValue(s,o)),o}readValue(s,r){let o=this.latestValues[s]!==void 0||!this.current?this.latestValues[s]:this.getBaseTargetFromProps(this.props,s)??this.readValueFromInstance(this.current,s,this.options);return o!=null&&(typeof o=="string"&&(Kc(o)||qc(o))?o=parseFloat(o):typeof o!="number"&&!jt.test(o)&&jt.test(r)&&(o=ru(s,r)),this.setBaseTarget(s,et(o)?o.get():o)),et(o)?o.get():o}setBaseTarget(s,r){this.baseTarget[s]=r}getBaseTarget(s){var d;const{initial:r}=this.props;let o;if(typeof r=="string"||typeof r=="object"){const h=cu(this.props,r,(d=this.presenceContext)==null?void 0:d.custom);h&&(o=h[s])}if(r&&o!==void 0)return o;const c=this.getBaseTargetFromProps(this.props,s);return c!==void 0&&!et(c)?c:this.initialValues[s]!==void 0&&o===void 0?void 0:this.baseTarget[s]}on(s,r){return this.events[s]||(this.events[s]=new xa),this.events[s].add(r)}notify(s,...r){this.events[s]&&this.events[s].notify(...r)}scheduleRenderMicrotask(){pu.render(this.render)}}class Bg extends g0{constructor(){super(...arguments),this.KeyframeResolver=Ik}sortInstanceNodePosition(s,r){return s.compareDocumentPosition(r)&2?1:-1}getBaseTargetFromProps(s,r){const o=s.style;return o?o[r]:void 0}removeValueFromRenderState(s,{vars:r,style:o}){delete r[s],delete o[s]}handleChildMotionValue(){this.childSubscription&&(this.childSubscription(),delete this.childSubscription);const{children:s}=this.props;et(s)&&(this.childSubscription=s.on("change",r=>{this.current&&(this.current.textContent=`${r}`)}))}}class Dn{constructor(s){this.isMounted=!1,this.node=s}update(){}}function Og(t,{style:s,vars:r},o,c){const d=t.style;let h;for(h in s)d[h]=s[h];c==null||c.applyProjectionStyles(d,o);for(h in r)d.setProperty(h,r[h])}function hp(t,s){return s.max===s.min?0:t/(s.max-s.min)*100}const Ci={correct:(t,s)=>{if(!s.target)return t;if(typeof t=="string")if(te.test(t))t=parseFloat(t);else return t;const r=hp(t,s.target.x),o=hp(t,s.target.y);return`${r}% ${o}%`}},y0={correct:(t,{treeScale:s,projectionDelta:r})=>{const o=t,c=jt.parse(t);if(c.length>5)return o;const d=jt.createTransformer(t),h=typeof c[0]!="number"?1:0,p=r.x.scale*s.x,f=r.y.scale*s.y;c[0+h]/=p,c[1+h]/=f;const v=ke(p,f,.5);return typeof c[2+h]=="number"&&(c[2+h]/=v),typeof c[3+h]=="number"&&(c[3+h]/=v),d(c)}},Bc={borderRadius:{...Ci,applyTo:[...du]},borderTopLeftRadius:Ci,borderTopRightRadius:Ci,borderBottomLeftRadius:Ci,borderBottomRightRadius:Ci,boxShadow:y0};function zg(t,{layout:s,layoutId:r}){return Bs.has(t)||t.startsWith("origin")||(s||r!==void 0)&&(!!Bc[t]||t==="opacity")}function vu(t,s,r){var h;const o=t.style,c=s==null?void 0:s.style,d={};if(!o)return d;for(const p in o)(et(o[p])||c&&et(c[p])||zg(p,t)||((h=r==null?void 0:r.getValue(p))==null?void 0:h.liveStyle)!==void 0)&&(d[p]=o[p]);return d}function v0(t){return window.getComputedStyle(t)}class x0 extends Bg{constructor(){super(...arguments),this.type="html",this.renderInstance=Og}mount(s){Ra(!!s.style),super.mount(s)}readValueFromInstance(s,r){var o;if(Bs.has(r))return(o=this.projection)!=null&&o.isProjecting?Cc(r):Ow(s,r);{const c=v0(s),d=(qf(r)?c.getPropertyValue(r):c[r])||0;return typeof d=="string"?d.trim():d}}measureInstanceViewportBox(s,{transformPagePoint:r}){return Mg(s,r)}build(s,r,o){mu(s,r,o.transformTemplate)}scrapeMotionValuesFromProps(s,r,o){return vu(s,r,o)}}const Ug=new Set(["baseFrequency","diffuseConstant","kernelMatrix","kernelUnitLength","keySplines","keyTimes","limitingConeAngle","markerHeight","markerWidth","numOctaves","targetX","targetY","surfaceScale","specularConstant","specularExponent","stdDeviation","tableValues","viewBox","gradientTransform","pathLength","startOffset","textLength","lengthAdjust"]),Wg=t=>typeof t=="string"&&t.toLowerCase()==="svg";function b0(t,s,r,o){Og(t,s,void 0,o);for(const c in s.attrs)t.setAttribute(Ug.has(c)?c:uu(c),s.attrs[c])}function $g(t,s,r){const o=vu(t,s,r);for(const c in t)if(et(t[c])||et(s[c])){const d=Fs.indexOf(c)!==-1?"attr"+c.charAt(0).toUpperCase()+c.substring(1):c;o[d]=t[c]}return o}class w0 extends Bg{constructor(){super(...arguments),this.type="svg",this.isSVGTag=!1,this.measureInstanceViewportBox=Ge}getBaseTargetFromProps(s,r){return s[r]}readValueFromInstance(s,r){if(Bs.has(r)){const o=lg(r);return o&&o.default||0}if(Cg.includes(r)){const c=getComputedStyle(s)[r];if(typeof c=="string"&&c)return c.trim()}return r=Ug.has(r)?r:uu(r),s.getAttribute(r)}scrapeMotionValuesFromProps(s,r,o){return $g(s,r,o)}build(s,r,o){Tg(s,r,this.isSVGTag,o.transformTemplate,o.style)}renderInstance(s,r,o,c){b0(s,r,o,c)}mount(s){this.isSVGTag=Wg(s.tagName),super.mount(s)}}const k0=Ca.length;function Hg(t){if(!t)return;if(!t.isControllingVariants){const r=t.parent?Hg(t.parent)||{}:{};return t.props.initial!==void 0&&(r.initial=t.props.initial),r}const s={};for(let r=0;r<k0;r++){const o=Ca[r],c=t.props[o];(Ri(c)||c===!1)&&(s[o]=c)}return s}function Gg(t,s){if(!Array.isArray(s))return!1;const r=s.length;if(r!==t.length)return!1;for(let o=0;o<r;o++)if(s[o]!==t[o])return!1;return!0}const j0=[...gu].reverse(),S0=gu.length;function N0(t){return s=>Promise.all(s.map(({animation:r,options:o})=>Ak(t,r,o)))}function C0(t){let s=N0(t),r=mp(),o=!0,c=!1;const d=v=>(g,x)=>{var j;const b=ss(t,x,v==="exit"?(j=t.presenceContext)==null?void 0:j.custom:void 0);if(b){const{transition:k,transitionEnd:S,...N}=b;g={...g,...N,...S}}return g};function h(v){s=v(t)}function p(v){const{props:g}=t,x=Hg(t.parent)||{},b=[],j=new Set;let k={},S=1/0;for(let O=0;O<S0;O++){const M=j0[O],L=r[M],I=g[M]!==void 0?g[M]:x[M],D=Ri(I),B=M===v?L.isActive:null;B===!1&&(S=O);let V=I===x[M]&&I!==g[M]&&D;if(V&&(o||c)&&t.manuallyAnimateOnMount&&(V=!1),L.protectedKeys={...k},!L.isActive&&B===null||!I&&!L.prevProp||Ia(I)||typeof I=="boolean")continue;if(M==="exit"&&L.isActive&&B!==!0){L.prevResolvedValues&&(k={...k,...L.prevResolvedValues});continue}const z=T0(L.prevProp,I);let re=z||M===v&&L.isActive&&!V&&D||O>S&&D,Y=!1;const ce=Array.isArray(I)?I:[I];let ue=ce.reduce(d(M),{});B===!1&&(ue={});const{prevResolvedValues:ie={}}=L,Se={...ie,...ue},De=E=>{re=!0,j.has(E)&&(Y=!0,j.delete(E)),L.needsAnimating[E]=!0;const H=t.getValue(E);H&&(H.liveStyle=!1)};for(const E in Se){const H=ue[E],W=ie[E];if(k.hasOwnProperty(E))continue;let P=!1;Dc(H)&&Dc(W)?P=!Gg(H,W)||z:P=H!==W,P?H!=null?De(E):j.add(E):H!==void 0&&j.has(E)?De(E):L.protectedKeys[E]=!0}L.prevProp=I,L.prevResolvedValues=ue,L.isActive&&(k={...k,...ue}),(o||c)&&t.blockInitialAnimation&&(re=!1);const Pe=V&&z;re&&(!Pe||Y)&&b.push(...ce.map(E=>{const H={type:M};if(typeof E=="string"&&(o||c)&&!Pe&&t.manuallyAnimateOnMount&&t.parent){const{parent:W}=t,P=ss(W,E);if(W.enteringChildren&&P){const{delayChildren:U}=P.transition||{};H.delay=vg(W.enteringChildren,t,U)}}return{animation:E,options:H}}))}if(j.size){const O={};if(typeof g.initial!="boolean"){const M=ss(t,Array.isArray(g.initial)?g.initial[0]:g.initial);M&&M.transition&&(O.transition=M.transition)}j.forEach(M=>{const L=t.getBaseTarget(M),I=t.getValue(M);I&&(I.liveStyle=!0),O[M]=L??null}),b.push({animation:O})}let N=!!b.length;return o&&(g.initial===!1||g.initial===g.animate)&&!t.manuallyAnimateOnMount&&(N=!1),o=!1,c=!1,N?s(b):Promise.resolve()}function f(v,g){var b;if(r[v].isActive===g)return Promise.resolve();(b=t.variantChildren)==null||b.forEach(j=>{var k;return(k=j.animationState)==null?void 0:k.setActive(v,g)}),r[v].isActive=g;const x=p(v);for(const j in r)r[j].protectedKeys={};return x}return{animateChanges:p,setActive:f,setAnimateFunction:h,getState:()=>r,reset:()=>{r=mp(),c=!0}}}function T0(t,s){return typeof s=="string"?s!==t:Array.isArray(s)?!Gg(s,t):!1}function qn(t=!1){return{isActive:t,protectedKeys:{},needsAnimating:{},prevResolvedValues:{}}}function mp(){return{animate:qn(!0),whileInView:qn(),whileHover:qn(),whileTap:qn(),whileDrag:qn(),whileFocus:qn(),exit:qn()}}function Oc(t,s){t.min=s.min,t.max=s.max}function Bt(t,s){Oc(t.x,s.x),Oc(t.y,s.y)}function pp(t,s){t.translate=s.translate,t.scale=s.scale,t.originPoint=s.originPoint,t.origin=s.origin}const Kg=1e-4,P0=1-Kg,A0=1+Kg,qg=.01,E0=0-qg,M0=0+qg;function ct(t){return t.max-t.min}function _0(t,s,r){return Math.abs(t-s)<=r}function fp(t,s,r,o=.5){t.origin=o,t.originPoint=ke(s.min,s.max,t.origin),t.scale=ct(r)/ct(s),t.translate=ke(r.min,r.max,t.origin)-t.originPoint,(t.scale>=P0&&t.scale<=A0||isNaN(t.scale))&&(t.scale=1),(t.translate>=E0&&t.translate<=M0||isNaN(t.translate))&&(t.translate=0)}function Ai(t,s,r,o){fp(t.x,s.x,r.x,o?o.originX:void 0),fp(t.y,s.y,r.y,o?o.originY:void 0)}function gp(t,s,r,o=0){const c=o?ke(r.min,r.max,o):r.min;t.min=c+s.min,t.max=t.min+ct(s)}function D0(t,s,r,o){gp(t.x,s.x,r.x,o==null?void 0:o.x),gp(t.y,s.y,r.y,o==null?void 0:o.y)}function yp(t,s,r,o=0){const c=o?ke(r.min,r.max,o):r.min;t.min=s.min-c,t.max=t.min+ct(s)}function Aa(t,s,r,o){yp(t.x,s.x,r.x,o==null?void 0:o.x),yp(t.y,s.y,r.y,o==null?void 0:o.y)}function vp(t,s,r,o,c){return t-=s,t=Na(t,1/r,o),c!==void 0&&(t=Na(t,1/c,o)),t}function R0(t,s=0,r=1,o=.5,c,d=t,h=t){if(Qt.test(s)&&(s=parseFloat(s),s=ke(h.min,h.max,s/100)-h.min),typeof s!="number")return;let p=ke(d.min,d.max,o);t===d&&(p-=s),t.min=vp(t.min,s,r,p,c),t.max=vp(t.max,s,r,p,c)}function xp(t,s,[r,o,c],d,h){R0(t,s[r],s[o],s[c],s.scale,d,h)}const L0=["x","scaleX","originX"],I0=["y","scaleY","originY"];function bp(t,s,r,o){xp(t.x,s,L0,r?r.x:void 0,o?o.x:void 0),xp(t.y,s,I0,r?r.y:void 0,o?o.y:void 0)}function wp(t){return t.translate===0&&t.scale===1}function Xg(t){return wp(t.x)&&wp(t.y)}function kp(t,s){return t.min===s.min&&t.max===s.max}function V0(t,s){return kp(t.x,s.x)&&kp(t.y,s.y)}function jp(t,s){return Math.round(t.min)===Math.round(s.min)&&Math.round(t.max)===Math.round(s.max)}function Yg(t,s){return jp(t.x,s.x)&&jp(t.y,s.y)}function Sp(t){return ct(t.x)/ct(t.y)}function Np(t,s){return t.translate===s.translate&&t.scale===s.scale&&t.originPoint===s.originPoint}function qt(t){return[t("x"),t("y")]}function F0(t,s,r){let o="";const c=t.x.translate/s.x,d=t.y.translate/s.y,h=(r==null?void 0:r.z)||0;if((c||d||h)&&(o=`translate3d(${c}px, ${d}px, ${h}px) `),(s.x!==1||s.y!==1)&&(o+=`scale(${1/s.x}, ${1/s.y}) `),r){const{transformPerspective:v,rotate:g,pathRotation:x,rotateX:b,rotateY:j,skewX:k,skewY:S}=r;v&&(o=`perspective(${v}px) ${o}`),g&&(o+=`rotate(${g}deg) `),x&&(o+=`rotate(${x}deg) `),b&&(o+=`rotateX(${b}deg) `),j&&(o+=`rotateY(${j}deg) `),k&&(o+=`skewX(${k}deg) `),S&&(o+=`skewY(${S}deg) `)}const p=t.x.scale*s.x,f=t.y.scale*s.y;return(p!==1||f!==1)&&(o+=`scale(${p}, ${f})`),o||"none"}const B0=du.length,Cp=t=>typeof t=="string"?parseFloat(t):t,Tp=t=>typeof t=="number"||te.test(t);function O0(t,s,r,o,c,d){c?(t.opacity=ke(0,r.opacity??1,z0(o)),t.opacityExit=ke(s.opacity??1,0,U0(o))):d&&(t.opacity=ke(s.opacity??1,r.opacity??1,o));for(let h=0;h<B0;h++){const p=du[h];let f=Pp(s,p),v=Pp(r,p);if(f===void 0&&v===void 0)continue;f||(f=0),v||(v=0),f===0||v===0||Tp(f)===Tp(v)?(t[p]=Math.max(ke(Cp(f),Cp(v),o),0),(Qt.test(v)||Qt.test(f))&&(t[p]+="%")):t[p]=v}(s.rotate||r.rotate)&&(t.rotate=ke(s.rotate||0,r.rotate||0,o))}function Pp(t,s){return t[s]!==void 0?t[s]:t.borderRadius}const z0=Qg(0,.5,Uf),U0=Qg(.5,.95,zt);function Qg(t,s,r){return o=>o<t?0:o>s?1:r(Mi(t,s,o))}function W0(t,s,r){const o=et(t)?t:Is(t);return o.start(lu("",o,s,r)),o.animation}function Li(t,s,r,o={passive:!0}){return t.addEventListener(s,r,o),()=>t.removeEventListener(s,r,o)}const $0=(t,s)=>t.depth-s.depth;class H0{constructor(){this.children=[],this.isDirty=!1}add(s){Gc(this.children,s),this.isDirty=!0}remove(s){va(this.children,s),this.isDirty=!0}forEach(s){this.isDirty&&this.children.sort($0),this.isDirty=!1,this.children.forEach(s)}}function G0(t,s){const r=rt.now(),o=({timestamp:c})=>{const d=c-r;d>=s&&(Mn(o),t(d-s))};return je.setup(o,!0),()=>Mn(o)}function ha(t){return et(t)?t.get():t}class K0{constructor(){this.members=[]}add(s){Gc(this.members,s);for(let r=this.members.length-1;r>=0;r--){const o=this.members[r];if(o===s||o===this.lead||o===this.prevLead)continue;const c=o.instance;(!c||c.isConnected===!1)&&!o.snapshot&&(va(this.members,o),o.unmount())}s.scheduleRender()}remove(s){if(va(this.members,s),s===this.prevLead&&(this.prevLead=void 0),s===this.lead){const r=this.members[this.members.length-1];r&&this.promote(r)}}relegate(s){var r;for(let o=this.members.indexOf(s)-1;o>=0;o--){const c=this.members[o];if(c.isPresent!==!1&&((r=c.instance)==null?void 0:r.isConnected)!==!1)return this.promote(c),!0}return!1}promote(s,r){var c;const o=this.lead;if(s!==o&&(this.prevLead=o,this.lead=s,s.show(),o)){o.updateSnapshot(),s.scheduleRender();const{layoutDependency:d}=o.options,{layoutDependency:h}=s.options;(d===void 0||d!==h)&&(s.resumeFrom=o,r&&(o.preserveOpacity=!0),o.snapshot&&(s.snapshot=o.snapshot,s.snapshot.latestValues=o.animationValues||o.latestValues),(c=s.root)!=null&&c.isUpdating&&(s.isLayoutDirty=!0)),s.options.crossfade===!1&&o.hide()}}exitAnimationComplete(){this.members.forEach(s=>{var r,o,c,d,h;(o=(r=s.options).onExitComplete)==null||o.call(r),(h=(c=s.resumingFrom)==null?void 0:(d=c.options).onExitComplete)==null||h.call(d)})}scheduleRender(){this.members.forEach(s=>s.instance&&s.scheduleRender(!1))}removeLeadSnapshot(){var s;(s=this.lead)!=null&&s.snapshot&&(this.lead.snapshot=void 0)}}const ma={hasAnimatedSinceResize:!0,hasEverUpdated:!1},Zl=["","X","Y","Z"],q0=1e3;let X0=0;function ec(t,s,r,o){const{latestValues:c}=s;c[t]&&(r[t]=c[t],s.setStaticValue(t,0),o&&(o[t]=0))}function Jg(t){if(t.hasCheckedOptimisedAppear=!0,t.root===t)return;const{visualElement:s}=t.options;if(!s)return;const r=jg(s);if(window.MotionHasOptimisedAnimation(r,"transform")){const{layout:c,layoutId:d}=t.options;window.MotionCancelOptimisedAnimation(r,"transform",je,!(c||d))}const{parent:o}=t;o&&!o.hasCheckedOptimisedAppear&&Jg(o)}function Zg({attachResizeListener:t,defaultParent:s,measureScroll:r,checkIsScrollRoot:o,resetTransform:c}){return class{constructor(h={},p=s==null?void 0:s()){this.id=X0++,this.animationId=0,this.animationCommitId=0,this.children=new Set,this.options={},this.isTreeAnimating=!1,this.isAnimationBlocked=!1,this.isLayoutDirty=!1,this.isProjectionDirty=!1,this.isSharedProjectionDirty=!1,this.isTransformDirty=!1,this.updateManuallyBlocked=!1,this.updateBlockedByResize=!1,this.isUpdating=!1,this.isSVG=!1,this.needsReset=!1,this.shouldResetTransform=!1,this.hasCheckedOptimisedAppear=!1,this.treeScale={x:1,y:1},this.eventHandlers=new Map,this.hasTreeAnimated=!1,this.layoutVersion=0,this.updateScheduled=!1,this.scheduleUpdate=()=>this.update(),this.projectionUpdateScheduled=!1,this.checkUpdateFailed=()=>{this.isUpdating&&(this.isUpdating=!1,this.clearAllSnapshots())},this.updateProjection=()=>{this.projectionUpdateScheduled=!1,this.nodes.forEach(J0),this.nodes.forEach(ij),this.nodes.forEach(rj),this.nodes.forEach(Z0)},this.resolvedRelativeTargetAt=0,this.linkedParentVersion=0,this.hasProjected=!1,this.isVisible=!0,this.animationProgress=0,this.sharedNodes=new Map,this.latestValues=h,this.root=p?p.root||p:this,this.path=p?[...p.path,p]:[],this.parent=p,this.depth=p?p.depth+1:0;for(let f=0;f<this.path.length;f++)this.path[f].shouldResetTransform=!0;this.root===this&&(this.nodes=new H0)}addEventListener(h,p){return this.eventHandlers.has(h)||this.eventHandlers.set(h,new xa),this.eventHandlers.get(h).add(p)}notifyListeners(h,...p){const f=this.eventHandlers.get(h);f&&f.notify(...p)}hasListeners(h){return this.eventHandlers.has(h)}mount(h){if(this.instance)return;this.isSVG=hu(h)&&!d0(h),this.instance=h;const{layoutId:p,layout:f,visualElement:v}=this.options;if(v&&!v.current&&v.mount(h),this.root.nodes.add(this),this.parent&&this.parent.children.add(this),this.root.hasTreeAnimated&&(f||p)&&(this.isLayoutDirty=!0),t){let g,x=0;const b=()=>this.root.updateBlockedByResize=!1;je.read(()=>{x=window.innerWidth}),t(h,()=>{const j=window.innerWidth;j!==x&&(x=j,this.root.updateBlockedByResize=!0,g&&g(),g=G0(b,250),ma.hasAnimatedSinceResize&&(ma.hasAnimatedSinceResize=!1,this.nodes.forEach(Mp)))})}p&&this.root.registerSharedNode(p,this),this.options.animate!==!1&&v&&(p||f)&&this.addEventListener("didUpdate",({delta:g,hasLayoutChanged:x,hasRelativeLayoutChanged:b,layout:j})=>{if(this.isTreeAnimationBlocked()){this.target=void 0,this.relativeTarget=void 0;return}const k=this.options.transition||v.getDefaultTransition()||uj,{onLayoutAnimationStart:S,onLayoutAnimationComplete:N}=v.getProps(),O=!this.targetLayout||!Yg(this.targetLayout,j),M=!x&&b;if(this.options.layoutRoot||this.resumeFrom||M||x&&(O||!this.currentAnimation)){this.resumeFrom&&(this.resumingFrom=this.resumeFrom,this.resumingFrom.resumingFrom=void 0);const L={...ou(k,"layout"),onPlay:S,onComplete:N};(v.shouldReduceMotion||this.options.layoutRoot)&&(L.delay=0,L.type=!1),this.startAnimation(L),this.setAnimationOrigin(g,M,L.path)}else x||Mp(this),this.isLead()&&this.options.onExitComplete&&this.options.onExitComplete();this.targetLayout=j})}unmount(){this.options.layoutId&&this.willUpdate(),this.root.nodes.remove(this);const h=this.getStack();h&&h.remove(this),this.parent&&this.parent.children.delete(this),this.instance=void 0,this.eventHandlers.clear(),Mn(this.updateProjection)}blockUpdate(){this.updateManuallyBlocked=!0}unblockUpdate(){this.updateManuallyBlocked=!1}isUpdateBlocked(){return this.updateManuallyBlocked||this.updateBlockedByResize}isTreeAnimationBlocked(){return this.isAnimationBlocked||this.parent&&this.parent.isTreeAnimationBlocked()||!1}startUpdate(){this.isUpdateBlocked()||(this.isUpdating=!0,this.nodes&&this.nodes.forEach(aj),this.animationId++)}getTransformTemplate(){const{visualElement:h}=this.options;return h&&h.getProps().transformTemplate}willUpdate(h=!0){if(this.root.hasTreeAnimated=!0,this.root.isUpdateBlocked()){this.options.onExitComplete&&this.options.onExitComplete();return}if(window.MotionCancelOptimisedAnimation&&!this.hasCheckedOptimisedAppear&&Jg(this),!this.root.isUpdating&&this.root.startUpdate(),this.isLayoutDirty)return;this.isLayoutDirty=!0;for(let g=0;g<this.path.length;g++){const x=this.path[g];x.shouldResetTransform=!0,(typeof x.latestValues.x=="string"||typeof x.latestValues.y=="string")&&(x.isLayoutDirty=!0),x.updateScroll("snapshot"),x.options.layoutRoot&&x.willUpdate(!1)}const{layoutId:p,layout:f}=this.options;if(p===void 0&&!f)return;const v=this.getTransformTemplate();this.prevTransformTemplateValue=v?v(this.latestValues,""):void 0,this.updateSnapshot(),h&&this.notifyListeners("willUpdate")}update(){if(this.updateScheduled=!1,this.isUpdateBlocked()){const f=this.updateBlockedByResize;this.unblockUpdate(),this.updateBlockedByResize=!1,this.clearAllSnapshots(),f&&this.nodes.forEach(tj),this.nodes.forEach(Ap);return}if(this.animationId<=this.animationCommitId){this.nodes.forEach(Ep);return}this.animationCommitId=this.animationId,this.isUpdating?(this.isUpdating=!1,this.nodes.forEach(nj),this.nodes.forEach(sj),this.nodes.forEach(Y0),this.nodes.forEach(Q0)):this.nodes.forEach(Ep),this.clearAllSnapshots();const p=rt.now();Ke.delta=Ut(0,1e3/60,p-Ke.timestamp),Ke.timestamp=p,Ke.isProcessing=!0,Hl.update.process(Ke),Hl.preRender.process(Ke),Hl.render.process(Ke),Ke.isProcessing=!1}didUpdate(){this.updateScheduled||(this.updateScheduled=!0,pu.read(this.scheduleUpdate))}clearAllSnapshots(){this.nodes.forEach(ej),this.sharedNodes.forEach(oj)}scheduleUpdateProjection(){this.projectionUpdateScheduled||(this.projectionUpdateScheduled=!0,je.preRender(this.updateProjection,!1,!0))}scheduleCheckAfterUnmount(){je.postRender(()=>{this.isLayoutDirty?this.root.didUpdate():this.root.checkUpdateFailed()})}updateSnapshot(){this.snapshot||!this.instance||(this.snapshot=this.measure(),this.snapshot&&!ct(this.snapshot.measuredBox.x)&&!ct(this.snapshot.measuredBox.y)&&(this.snapshot=void 0))}updateLayout(){if(!this.instance||(this.updateScroll(),!(this.options.alwaysMeasureLayout&&this.isLead())&&!this.isLayoutDirty))return;if(this.resumeFrom&&!this.resumeFrom.instance)for(let f=0;f<this.path.length;f++)this.path[f].updateScroll();const h=this.layout;this.layout=this.measure(!1),this.layoutVersion++,this.layoutCorrected||(this.layoutCorrected=Ge()),this.isLayoutDirty=!1,this.projectionDelta=void 0,this.notifyListeners("measure",this.layout.layoutBox);const{visualElement:p}=this.options;p&&p.notify("LayoutMeasure",this.layout.layoutBox,h?h.layoutBox:void 0)}updateScroll(h="measure"){let p=!!(this.options.layoutScroll&&this.instance);if(this.scroll&&this.scroll.animationId===this.root.animationId&&this.scroll.phase===h&&(p=!1),p&&this.instance){const f=o(this.instance);this.scroll={animationId:this.root.animationId,phase:h,isRoot:f,offset:r(this.instance),wasRoot:this.scroll?this.scroll.isRoot:f}}}resetTransform(){if(!c)return;const h=this.isLayoutDirty||this.shouldResetTransform||this.options.alwaysMeasureLayout,p=this.projectionDelta&&!Xg(this.projectionDelta),f=this.getTransformTemplate(),v=f?f(this.latestValues,""):void 0,g=v!==this.prevTransformTemplateValue;h&&this.instance&&(p||Xn(this.latestValues)||g)&&(c(this.instance,v),this.shouldResetTransform=!1,this.scheduleRender())}measure(h=!0){const p=this.measurePageBox();let f=this.removeElementScroll(p);return h&&(f=this.removeTransform(f)),dj(f),{animationId:this.root.animationId,measuredBox:p,layoutBox:f,latestValues:{},source:this.id}}measurePageBox(){var v;const{visualElement:h}=this.options;if(!h)return Ge();const p=h.measureViewportBox();if(!(((v=this.scroll)==null?void 0:v.wasRoot)||this.path.some(hj))){const{scroll:g}=this.root;g&&(Xt(p.x,g.offset.x),Xt(p.y,g.offset.y))}return p}removeElementScroll(h){var f;const p=Ge();if(Bt(p,h),(f=this.scroll)!=null&&f.wasRoot)return p;for(let v=0;v<this.path.length;v++){const g=this.path[v],{scroll:x,options:b}=g;g!==this.root&&x&&b.layoutScroll&&(x.wasRoot&&Bt(p,h),Xt(p.x,x.offset.x),Xt(p.y,x.offset.y))}return p}applyTransform(h,p=!1,f){var g,x;const v=f||Ge();Bt(v,h);for(let b=0;b<this.path.length;b++){const j=this.path[b];!p&&j.options.layoutScroll&&j.scroll&&j!==j.root&&(Xt(v.x,-j.scroll.offset.x),Xt(v.y,-j.scroll.offset.y)),Xn(j.latestValues)&&la(v,j.latestValues,(g=j.layout)==null?void 0:g.layoutBox)}return Xn(this.latestValues)&&la(v,this.latestValues,(x=this.layout)==null?void 0:x.layoutBox),v}removeTransform(h){var f;const p=Ge();Bt(p,h);for(let v=0;v<this.path.length;v++){const g=this.path[v];if(!Xn(g.latestValues))continue;let x;g.instance&&(Vc(g.latestValues)&&g.updateSnapshot(),x=Ge(),Bt(x,g.measurePageBox())),bp(p,g.latestValues,(f=g.snapshot)==null?void 0:f.layoutBox,x)}return Xn(this.latestValues)&&bp(p,this.latestValues),p}setTargetDelta(h){this.targetDelta=h,this.root.scheduleUpdateProjection(),this.isProjectionDirty=!0}setOptions(h){this.options={...this.options,...h,crossfade:h.crossfade!==void 0?h.crossfade:!0}}clearMeasurements(){this.scroll=void 0,this.layout=void 0,this.snapshot=void 0,this.prevTransformTemplateValue=void 0,this.targetDelta=void 0,this.target=void 0,this.isLayoutDirty=!1}forceRelativeParentToResolveTarget(){this.relativeParent&&this.relativeParent.resolvedRelativeTargetAt!==Ke.timestamp&&this.relativeParent.resolveTargetDelta(!0)}resolveTargetDelta(h=!1){var j;const p=this.getLead();this.isProjectionDirty||(this.isProjectionDirty=p.isProjectionDirty),this.isTransformDirty||(this.isTransformDirty=p.isTransformDirty),this.isSharedProjectionDirty||(this.isSharedProjectionDirty=p.isSharedProjectionDirty);const f=!!this.resumingFrom||this!==p;if(!(h||f&&this.isSharedProjectionDirty||this.isProjectionDirty||(j=this.parent)!=null&&j.isProjectionDirty||this.attemptToResolveRelativeTarget||this.root.updateBlockedByResize))return;const{layout:g,layoutId:x}=this.options;if(!this.layout||!(g||x))return;this.resolvedRelativeTargetAt=Ke.timestamp;const b=this.getClosestProjectingParent();b&&this.linkedParentVersion!==b.layoutVersion&&!b.options.layoutRoot&&this.removeRelativeTarget(),!this.targetDelta&&!this.relativeTarget&&(this.options.layoutAnchor!==!1&&b&&b.layout?this.createRelativeTarget(b,this.layout.layoutBox,b.layout.layoutBox):this.removeRelativeTarget()),!(!this.relativeTarget&&!this.targetDelta)&&(this.target||(this.target=Ge(),this.targetWithTransforms=Ge()),this.relativeTarget&&this.relativeTargetOrigin&&this.relativeParent&&this.relativeParent.target?(this.forceRelativeParentToResolveTarget(),D0(this.target,this.relativeTarget,this.relativeParent.target,this.options.layoutAnchor||void 0)):this.targetDelta?(this.resumingFrom?this.applyTransform(this.layout.layoutBox,!1,this.target):Bt(this.target,this.layout.layoutBox),Eg(this.target,this.targetDelta)):Bt(this.target,this.layout.layoutBox),this.attemptToResolveRelativeTarget&&(this.attemptToResolveRelativeTarget=!1,this.options.layoutAnchor!==!1&&b&&!!b.resumingFrom==!!this.resumingFrom&&!b.options.layoutScroll&&b.target&&this.animationProgress!==1?this.createRelativeTarget(b,this.target,b.target):this.relativeParent=this.relativeTarget=void 0))}getClosestProjectingParent(){if(!(!this.parent||Vc(this.parent.latestValues)||Ag(this.parent.latestValues)))return this.parent.isProjecting()?this.parent:this.parent.getClosestProjectingParent()}isProjecting(){return!!((this.relativeTarget||this.targetDelta||this.options.layoutRoot)&&this.layout)}createRelativeTarget(h,p,f){this.relativeParent=h,this.linkedParentVersion=h.layoutVersion,this.forceRelativeParentToResolveTarget(),this.relativeTarget=Ge(),this.relativeTargetOrigin=Ge(),Aa(this.relativeTargetOrigin,p,f,this.options.layoutAnchor||void 0),Bt(this.relativeTarget,this.relativeTargetOrigin)}removeRelativeTarget(){this.relativeParent=this.relativeTarget=void 0}calcProjection(){var k;const h=this.getLead(),p=!!this.resumingFrom||this!==h;let f=!0;if((this.isProjectionDirty||(k=this.parent)!=null&&k.isProjectionDirty)&&(f=!1),p&&(this.isSharedProjectionDirty||this.isTransformDirty)&&(f=!1),this.resolvedRelativeTargetAt===Ke.timestamp&&(f=!1),f)return;const{layout:v,layoutId:g}=this.options;if(this.isTreeAnimating=!!(this.parent&&this.parent.isTreeAnimating||this.currentAnimation||this.pendingAnimation),this.isTreeAnimating||(this.targetDelta=this.relativeTarget=void 0),!this.layout||!(v||g))return;Bt(this.layoutCorrected,this.layout.layoutBox);const x=this.treeScale.x,b=this.treeScale.y;Gk(this.layoutCorrected,this.treeScale,this.path,p),h.layout&&!h.target&&(this.treeScale.x!==1||this.treeScale.y!==1)&&(h.target=h.layout.layoutBox,h.targetWithTransforms=Ge());const{target:j}=h;if(!j){this.prevProjectionDelta&&(this.createProjectionDeltas(),this.scheduleRender());return}!this.projectionDelta||!this.prevProjectionDelta?this.createProjectionDeltas():(pp(this.prevProjectionDelta.x,this.projectionDelta.x),pp(this.prevProjectionDelta.y,this.projectionDelta.y)),Ai(this.projectionDelta,this.layoutCorrected,j,this.latestValues),(this.treeScale.x!==x||this.treeScale.y!==b||!Np(this.projectionDelta.x,this.prevProjectionDelta.x)||!Np(this.projectionDelta.y,this.prevProjectionDelta.y))&&(this.hasProjected=!0,this.scheduleRender(),this.notifyListeners("projectionUpdate",j))}hide(){this.isVisible=!1}show(){this.isVisible=!0}scheduleRender(h=!0){var p;if((p=this.options.visualElement)==null||p.scheduleRender(),h){const f=this.getStack();f&&f.scheduleRender()}this.resumingFrom&&!this.resumingFrom.instance&&(this.resumingFrom=void 0)}createProjectionDeltas(){this.prevProjectionDelta=Rs(),this.projectionDelta=Rs(),this.projectionDeltaWithTransform=Rs()}setAnimationOrigin(h,p=!1,f){const v=this.snapshot,g=v?v.latestValues:{},x={...this.latestValues},b=Rs();(!this.relativeParent||!this.relativeParent.options.layoutRoot)&&(this.relativeTarget=this.relativeTargetOrigin=void 0),this.attemptToResolveRelativeTarget=!p;const j=Ge(),k=v?v.source:void 0,S=this.layout?this.layout.source:void 0,N=k!==S,O=this.getStack(),M=!O||O.members.length<=1,L=!!(N&&!M&&this.options.crossfade===!0&&!this.path.some(cj));this.animationProgress=0;let I;const D=f==null?void 0:f.interpolateProjection(h);this.mixTargetDelta=B=>{const V=B/1e3,z=D==null?void 0:D(V);z?(b.x.translate=z.x,b.x.scale=ke(h.x.scale,1,V),b.x.origin=h.x.origin,b.x.originPoint=h.x.originPoint,b.y.translate=z.y,b.y.scale=ke(h.y.scale,1,V),b.y.origin=h.y.origin,b.y.originPoint=h.y.originPoint):(_p(b.x,h.x,V),_p(b.y,h.y,V)),this.setTargetDelta(b),this.relativeTarget&&this.relativeTargetOrigin&&this.layout&&this.relativeParent&&this.relativeParent.layout&&(Aa(j,this.layout.layoutBox,this.relativeParent.layout.layoutBox,this.options.layoutAnchor||void 0),lj(this.relativeTarget,this.relativeTargetOrigin,j,V),I&&V0(this.relativeTarget,I)&&(this.isProjectionDirty=!1),I||(I=Ge()),Bt(I,this.relativeTarget)),N&&(this.animationValues=x,O0(x,g,this.latestValues,V,L,M)),z&&z.rotate!==void 0&&(this.animationValues||(this.animationValues=x),this.animationValues.pathRotation=z.rotate),this.root.scheduleUpdateProjection(),this.scheduleRender(),this.animationProgress=V},this.mixTargetDelta(this.options.layoutRoot?1e3:0)}startAnimation(h){var p,f,v;this.notifyListeners("animationStart"),(p=this.currentAnimation)==null||p.stop(),(v=(f=this.resumingFrom)==null?void 0:f.currentAnimation)==null||v.stop(),this.pendingAnimation&&(Mn(this.pendingAnimation),this.pendingAnimation=void 0),this.pendingAnimation=je.update(()=>{ma.hasAnimatedSinceResize=!0,this.motionValue||(this.motionValue=Is(0)),this.motionValue.jump(0,!1),this.currentAnimation=W0(this.motionValue,[0,1e3],{...h,velocity:0,isSync:!0,onUpdate:g=>{this.mixTargetDelta(g),h.onUpdate&&h.onUpdate(g)},onComplete:()=>{h.onComplete&&h.onComplete(),this.completeAnimation()}}),Aw(this.currentAnimation,this),this.resumingFrom&&(this.resumingFrom.currentAnimation=this.currentAnimation),this.pendingAnimation=void 0})}completeAnimation(){this.resumingFrom&&(this.resumingFrom.currentAnimation=void 0,this.resumingFrom.preserveOpacity=void 0);const h=this.getStack();h&&h.exitAnimationComplete(),this.resumingFrom=this.currentAnimation=this.animationValues=void 0,this.notifyListeners("animationComplete")}finishAnimation(){this.currentAnimation&&(this.mixTargetDelta&&this.mixTargetDelta(q0),this.currentAnimation.stop()),this.completeAnimation()}applyTransformsToTarget(){const h=this.getLead(),{targetWithTransforms:p,layout:f,latestValues:v}=h;let{target:g}=h;if(!(!p||!g||!f)){if(this!==h&&this.layout&&f&&ey(this.options.animationType,this.layout.layoutBox,f.layoutBox)){g=this.target||Ge();const x=ct(this.layout.layoutBox.x);g.x.min=h.target.x.min,g.x.max=g.x.min+x;const b=ct(this.layout.layoutBox.y);g.y.min=h.target.y.min,g.y.max=g.y.min+b}Bt(p,g),la(p,v),Ai(this.projectionDeltaWithTransform,this.layoutCorrected,p,v)}}registerSharedNode(h,p){this.sharedNodes.has(h)||this.sharedNodes.set(h,new K0),this.sharedNodes.get(h).add(p);const v=p.options.initialPromotionConfig;p.promote({transition:v?v.transition:void 0,preserveFollowOpacity:v&&v.shouldPreserveFollowOpacity?v.shouldPreserveFollowOpacity(p):void 0})}isLead(){const h=this.getStack();return h?h.lead===this:!0}getLead(){var p;const{layoutId:h}=this.options;return h?((p=this.getStack())==null?void 0:p.lead)||this:this}getPrevLead(){var p;const{layoutId:h}=this.options;return h?(p=this.getStack())==null?void 0:p.prevLead:void 0}getStack(){const{layoutId:h}=this.options;if(h)return this.root.sharedNodes.get(h)}promote({needsReset:h,transition:p,preserveFollowOpacity:f}={}){const v=this.getStack();v&&v.promote(this,f),h&&(this.projectionDelta=void 0,this.needsReset=!0),p&&this.setOptions({transition:p})}relegate(){const h=this.getStack();return h?h.relegate(this):!1}resetSkewAndRotation(){const{visualElement:h}=this.options;if(!h)return;let p=!1;const{latestValues:f}=h;if((f.z||f.rotate||f.rotateX||f.rotateY||f.rotateZ||f.skewX||f.skewY)&&(p=!0),!p)return;const v={};f.z&&ec("z",h,v,this.animationValues);for(let g=0;g<Zl.length;g++)ec(`rotate${Zl[g]}`,h,v,this.animationValues),ec(`skew${Zl[g]}`,h,v,this.animationValues);h.render();for(const g in v)h.setStaticValue(g,v[g]),this.animationValues&&(this.animationValues[g]=v[g]);h.scheduleRender()}applyProjectionStyles(h,p){if(!this.instance||this.isSVG)return;if(!this.isVisible){h.visibility="hidden";return}const f=this.getTransformTemplate();if(this.needsReset){this.needsReset=!1,h.visibility="",h.opacity="",h.pointerEvents=ha(p==null?void 0:p.pointerEvents)||"",h.transform=f?f(this.latestValues,""):"none";return}const v=this.getLead();if(!this.projectionDelta||!this.layout||!v.target){this.options.layoutId&&(h.opacity=this.latestValues.opacity!==void 0?this.latestValues.opacity:1,h.pointerEvents=ha(p==null?void 0:p.pointerEvents)||""),this.hasProjected&&!Xn(this.latestValues)&&(h.transform=f?f({},""):"none",this.hasProjected=!1);return}h.visibility="";const g=v.animationValues||v.latestValues;this.applyTransformsToTarget();let x=F0(this.projectionDeltaWithTransform,this.treeScale,g);f&&(x=f(g,x)),h.transform=x;const{x:b,y:j}=this.projectionDelta;h.transformOrigin=`${b.origin*100}% ${j.origin*100}% 0`,v.animationValues?h.opacity=v===this?g.opacity??this.latestValues.opacity??1:this.preserveOpacity?this.latestValues.opacity:g.opacityExit:h.opacity=v===this?g.opacity!==void 0?g.opacity:"":g.opacityExit!==void 0?g.opacityExit:0;for(const k in Bc){if(g[k]===void 0)continue;const{correct:S,applyTo:N,isCSSVariable:O}=Bc[k],M=x==="none"?g[k]:S(g[k],v);if(N){const L=N.length;for(let I=0;I<L;I++)h[N[I]]=M}else O?this.options.visualElement.renderState.vars[k]=M:h[k]=M}this.options.layoutId&&(h.pointerEvents=v===this?ha(p==null?void 0:p.pointerEvents)||"":"none")}clearSnapshot(){this.resumeFrom=this.snapshot=void 0}resetTree(){this.root.nodes.forEach(h=>{var p;return(p=h.currentAnimation)==null?void 0:p.stop()}),this.root.nodes.forEach(Ap),this.root.sharedNodes.clear()}}}function Y0(t){t.updateLayout()}function Q0(t){var r;const s=((r=t.resumeFrom)==null?void 0:r.snapshot)||t.snapshot;if(t.isLead()&&t.layout&&s&&t.hasListeners("didUpdate")){const{layoutBox:o,measuredBox:c}=t.layout,{animationType:d}=t.options,h=s.source!==t.layout.source;if(d==="size")qt(x=>{const b=h?s.measuredBox[x]:s.layoutBox[x],j=ct(b);b.min=o[x].min,b.max=b.min+j});else if(d==="x"||d==="y"){const x=d==="x"?"y":"x";Oc(h?s.measuredBox[x]:s.layoutBox[x],o[x])}else ey(d,s.layoutBox,o)&&qt(x=>{const b=h?s.measuredBox[x]:s.layoutBox[x],j=ct(o[x]);b.max=b.min+j,t.relativeTarget&&!t.currentAnimation&&(t.isProjectionDirty=!0,t.relativeTarget[x].max=t.relativeTarget[x].min+j)});const p=Rs();Ai(p,o,s.layoutBox);const f=Rs();h?Ai(f,t.applyTransform(c,!0),s.measuredBox):Ai(f,o,s.layoutBox);const v=!Xg(p);let g=!1;if(!t.resumeFrom){const x=t.getClosestProjectingParent();if(x&&!x.resumeFrom){const{snapshot:b,layout:j}=x;if(b&&j){const k=t.options.layoutAnchor||void 0,S=Ge();Aa(S,s.layoutBox,b.layoutBox,k);const N=Ge();Aa(N,o,j.layoutBox,k),Yg(S,N)||(g=!0),x.options.layoutRoot&&(t.relativeTarget=N,t.relativeTargetOrigin=S,t.relativeParent=x)}}}t.notifyListeners("didUpdate",{layout:o,snapshot:s,delta:f,layoutDelta:p,hasLayoutChanged:v,hasRelativeLayoutChanged:g})}else if(t.isLead()){const{onExitComplete:o}=t.options;o&&o()}t.options.transition=void 0}function J0(t){t.parent&&(t.isProjecting()||(t.isProjectionDirty=t.parent.isProjectionDirty),t.isSharedProjectionDirty||(t.isSharedProjectionDirty=!!(t.isProjectionDirty||t.parent.isProjectionDirty||t.parent.isSharedProjectionDirty)),t.isTransformDirty||(t.isTransformDirty=t.parent.isTransformDirty))}function Z0(t){t.isProjectionDirty=t.isSharedProjectionDirty=t.isTransformDirty=!1}function ej(t){t.clearSnapshot()}function Ap(t){t.clearMeasurements()}function tj(t){t.isLayoutDirty=!0,t.updateLayout()}function Ep(t){t.isLayoutDirty=!1}function nj(t){t.isAnimationBlocked&&t.layout&&!t.isLayoutDirty&&(t.snapshot=t.layout,t.isLayoutDirty=!0)}function sj(t){const{visualElement:s}=t.options;s&&s.getProps().onBeforeLayoutMeasure&&s.notify("BeforeLayoutMeasure"),t.resetTransform()}function Mp(t){t.finishAnimation(),t.targetDelta=t.relativeTarget=t.target=void 0,t.isProjectionDirty=!0}function ij(t){t.resolveTargetDelta()}function rj(t){t.calcProjection()}function aj(t){t.resetSkewAndRotation()}function oj(t){t.removeLeadSnapshot()}function _p(t,s,r){t.translate=ke(s.translate,0,r),t.scale=ke(s.scale,1,r),t.origin=s.origin,t.originPoint=s.originPoint}function Dp(t,s,r,o){t.min=ke(s.min,r.min,o),t.max=ke(s.max,r.max,o)}function lj(t,s,r,o){Dp(t.x,s.x,r.x,o),Dp(t.y,s.y,r.y,o)}function cj(t){return t.animationValues&&t.animationValues.opacityExit!==void 0}const uj={duration:.45,ease:[.4,0,.1,1]},Rp=t=>typeof navigator<"u"&&navigator.userAgent&&navigator.userAgent.toLowerCase().includes(t),Lp=Rp("applewebkit/")&&!Rp("chrome/")?Math.round:zt;function Ip(t){t.min=Lp(t.min),t.max=Lp(t.max)}function dj(t){Ip(t.x),Ip(t.y)}function ey(t,s,r){return t==="position"||t==="preserve-aspect"&&!_0(Sp(s),Sp(r),.2)}function hj(t){var s;return t!==t.root&&((s=t.scroll)==null?void 0:s.wasRoot)}const mj=Zg({attachResizeListener:(t,s)=>Li(t,"resize",s),measureScroll:()=>{var t,s;return{x:document.documentElement.scrollLeft||((t=document.body)==null?void 0:t.scrollLeft)||0,y:document.documentElement.scrollTop||((s=document.body)==null?void 0:s.scrollTop)||0}},checkIsScrollRoot:()=>!0}),tc={current:void 0},ty=Zg({measureScroll:t=>({x:t.scrollLeft,y:t.scrollTop}),defaultParent:()=>{if(!tc.current){const t=new mj({});t.mount(window),t.setOptions({layoutScroll:!0}),tc.current=t}return tc.current},resetTransform:(t,s)=>{t.style.transform=s!==void 0?s:"none"},checkIsScrollRoot:t=>window.getComputedStyle(t).position==="fixed"}),ny=T.createContext({transformPagePoint:t=>t,isStatic:!1,reducedMotion:"never"});function pj(t=!0){const s=T.useContext(Hc);if(s===null)return[!0,null];const{isPresent:r,onExitComplete:o,register:c}=s,d=T.useId();T.useEffect(()=>{if(t)return c(d)},[t]);const h=T.useCallback(()=>t&&o&&o(d),[d,o,t]);return!r&&o?[!1,h]:[!0]}const sy=T.createContext({strict:!1}),Vp={animation:["animate","variants","whileHover","whileTap","exit","whileInView","whileFocus","whileDrag"],exit:["exit"],drag:["drag","dragControls"],focus:["whileFocus"],hover:["whileHover","onHoverStart","onHoverEnd"],tap:["whileTap","onTap","onTapStart","onTapCancel"],pan:["onPan","onPanStart","onPanSessionStart","onPanEnd"],inView:["whileInView","onViewportEnter","onViewportLeave"],layout:["layout","layoutId"]};let Fp=!1;function fj(){if(Fp)return;const t={};for(const s in Vp)t[s]={isEnabled:r=>Vp[s].some(o=>!!r[o])};Fg(t),Fp=!0}function iy(){return fj(),f0()}function gj(t){const s=iy();for(const r in t)s[r]={...s[r],...t[r]};Fg(s)}const Fa=T.createContext({});function yj(t,s){if(Va(t)){const{initial:r,animate:o}=t;return{initial:r===!1||Ri(r)?r:void 0,animate:Ri(o)?o:void 0}}return t.inherit!==!1?s:{}}function vj(t){const{initial:s,animate:r}=yj(t,T.useContext(Fa));return T.useMemo(()=>({initial:s,animate:r}),[Bp(s),Bp(r)])}function Bp(t){return Array.isArray(t)?t.join(" "):t}const xu=()=>({style:{},transform:{},transformOrigin:{},vars:{}});function ry(t,s,r){for(const o in s)!et(s[o])&&!zg(o,r)&&(t[o]=s[o])}function xj({transformTemplate:t},s){return T.useMemo(()=>{const r=xu();return mu(r,s,t),Object.assign({},r.vars,r.style)},[s])}function bj(t,s){const r=t.style||{},o={};return ry(o,r,t),Object.assign(o,xj(t,s)),o}function wj(t,s){const r={},o=bj(t,s);return t.drag&&t.dragListener!==!1&&(r.draggable=!1,o.userSelect=o.WebkitUserSelect=o.WebkitTouchCallout="none",o.touchAction=t.drag===!0?"none":`pan-${t.drag==="x"?"y":"x"}`),t.tabIndex===void 0&&(t.onTap||t.onTapStart||t.whileTap)&&(r.tabIndex=0),r.style=o,r}const ay=()=>({...xu(),attrs:{}});function kj(t,s,r,o){const c=T.useMemo(()=>{const d=ay();return Tg(d,s,Wg(o),t.transformTemplate,t.style),{...d.attrs,style:{...d.style}}},[s]);if(t.style){const d={};ry(d,t.style,t),c.style={...d,...c.style}}return c}const jj=new Set(["animate","exit","variants","initial","style","values","variants","transition","transformTemplate","custom","inherit","onBeforeLayoutMeasure","onAnimationStart","onAnimationComplete","onUpdate","onDragStart","onDrag","onDragEnd","onMeasureDragConstraints","onDirectionLock","onDragTransitionEnd","_dragX","_dragY","onHoverStart","onHoverEnd","onViewportEnter","onViewportLeave","globalTapTarget","propagate","ignoreStrict","viewport"]);function Ea(t){return t.startsWith("while")||t.startsWith("drag")&&t!=="draggable"||t.startsWith("layout")||t.startsWith("onTap")||t.startsWith("onPan")||t.startsWith("onLayout")||jj.has(t)}function Sj(t,s){return t.startsWith("on")?!Ea(t):(s==null?void 0:s(t))??!Ea(t)}function Nj(t,s,r,o){const c={};for(const d in t)d==="values"&&typeof t.values=="object"||et(t[d])||(Sj(d,o)||r===!0&&Ea(d)||!s&&!Ea(d)||t.draggable&&d.startsWith("onDrag"))&&(c[d]=t[d]);return c}const Cj=["animate","circle","defs","desc","ellipse","g","image","line","filter","marker","mask","metadata","path","pattern","polygon","polyline","rect","stop","switch","symbol","svg","text","tspan","use","view"];function bu(t){return typeof t!="string"||t.includes("-")?!1:!!(Cj.indexOf(t)>-1||/[A-Z]/u.test(t))}function Tj(t,s,r,{latestValues:o},c,d=!1,h,p){const v=(h??bu(t)?kj:wj)(s,o,c,t),g=Nj(s,typeof t=="string",d,p),x=t!==T.Fragment?{...g,...v,ref:r}:{},{children:b}=s,j=T.useMemo(()=>et(b)?b.get():b,[b]);return T.createElement(t,{...x,children:j})}function Pj({scrapeMotionValuesFromProps:t,createRenderState:s},r,o,c){return{latestValues:Aj(r,o,c,t),renderState:s()}}function Aj(t,s,r,o){const c={},d=o(t,{});for(const b in d)c[b]=ha(d[b]);let{initial:h,animate:p}=t;const f=Va(t),v=Ig(t);s&&v&&!f&&t.inherit!==!1&&(h===void 0&&(h=s.initial),p===void 0&&(p=s.animate));let g=r?r.initial===!1:!1;g=g||h===!1;const x=g?p:h;if(x&&typeof x!="boolean"&&!Ia(x)){const b=Array.isArray(x)?x:[x];for(let j=0;j<b.length;j++){const k=cu(t,b[j]);if(k){const{transitionEnd:S,transition:N,...O}=k;for(const M in O){let L=O[M];if(Array.isArray(L)){const I=g?L.length-1:0;L=L[I]}L!==null&&(c[M]=L)}for(const M in S)c[M]=S[M]}}}return c}const oy=t=>(s,r)=>{const o=T.useContext(Fa),c=T.useContext(Hc),d=()=>Pj(t,s,o,c);return r?d():Sb(d)},Ej=oy({scrapeMotionValuesFromProps:vu,createRenderState:xu}),Mj=oy({scrapeMotionValuesFromProps:$g,createRenderState:ay}),_j=Symbol.for("motionComponentSymbol");function Dj(t,s,r){const o=T.useRef(r);T.useInsertionEffect(()=>{o.current=r});const c=T.useRef(null);return T.useCallback(d=>{var p;d&&((p=t.onMount)==null||p.call(t,d)),s&&(d?s.mount(d):s.unmount());const h=o.current;if(typeof h=="function")if(d){const f=h(d);typeof f=="function"&&(c.current=f)}else c.current?(c.current(),c.current=null):h(d);else h&&(h.current=d)},[s])}const ly=T.createContext({});function Ms(t){return t&&typeof t=="object"&&Object.prototype.hasOwnProperty.call(t,"current")}function Rj(t,s,r,o,c,d){var L,I;const{visualElement:h}=T.useContext(Fa),p=T.useContext(sy),f=T.useContext(Hc),v=T.useContext(ny),g=v.reducedMotion,x=v.skipAnimations,b=T.useRef(null),j=T.useRef(!1);o=o||p.renderer,!b.current&&o&&(b.current=o(t,{visualState:s,parent:h,props:r,presenceContext:f,blockInitialAnimation:f?f.initial===!1:!1,reducedMotionConfig:g,skipAnimations:x,isSVG:d}),j.current&&b.current&&(b.current.manuallyAnimateOnMount=!0));const k=b.current,S=T.useContext(ly);k&&!k.projection&&c&&(k.type==="html"||k.type==="svg")&&Lj(b.current,r,c,S);const N=T.useRef(!1);T.useInsertionEffect(()=>{k&&N.current&&k.update(r,f)});const O=r[kg],M=T.useRef(!!O&&typeof window<"u"&&!((L=window.MotionHandoffIsComplete)!=null&&L.call(window,O))&&((I=window.MotionHasOptimisedAnimation)==null?void 0:I.call(window,O)));return Cb(()=>{j.current=!0,k&&(N.current=!0,window.MotionIsMounted=!0,k.updateFeatures(),k.scheduleRenderMicrotask(),M.current&&k.animationState&&k.animationState.animateChanges())}),T.useEffect(()=>{k&&(!M.current&&k.animationState&&k.animationState.animateChanges(),M.current&&(queueMicrotask(()=>{var D;(D=window.MotionHandoffMarkAsComplete)==null||D.call(window,O)}),M.current=!1),k.enteringChildren=void 0)}),k}function Lj(t,s,r,o){const{layoutId:c,layout:d,drag:h,dragConstraints:p,layoutScroll:f,layoutRoot:v,layoutAnchor:g,layoutCrossfade:x}=s;t.projection=new r(t.latestValues,s["data-framer-portal-id"]?void 0:cy(t.parent)),t.projection.setOptions({layoutId:c,layout:d,alwaysMeasureLayout:!!h||p&&Ms(p),visualElement:t,animationType:typeof d=="string"?d:"both",initialPromotionConfig:o,crossfade:x,layoutScroll:f,layoutRoot:v,layoutAnchor:g})}function cy(t){if(t)return t.options.allowProjection!==!1?t.projection:cy(t.parent)}function nc(t,{forwardMotionProps:s=!1,type:r}={},o,c){o&&gj(o);const d=r?r==="svg":bu(t),h=d?Mj:Ej;function p(v,g){let x;const b={...T.useContext(ny),...v,layoutId:Ij(v)},{isStatic:j,isValidProp:k}=b,S=vj(v),N=h(v,j);if(!j&&typeof window<"u"){Vj();const O=Fj(b);x=O.MeasureLayout,S.visualElement=Rj(t,N,b,c,O.ProjectionNode,d)}return i.jsxs(Fa.Provider,{value:S,children:[x&&S.visualElement?i.jsx(x,{visualElement:S.visualElement,...b}):null,Tj(t,v,Dj(N,S.visualElement,g),N,j,s,d,k)]})}p.displayName=`motion.${typeof t=="string"?t:`create(${t.displayName??t.name??""})`}`;const f=T.forwardRef(p);return f[_j]=t,f}function Ij({layoutId:t}){const s=T.useContext(_f).id;return s&&t!==void 0?s+"-"+t:t}function Vj(t,s){T.useContext(sy).strict}function Fj(t){const s=iy(),{drag:r,layout:o}=s;if(!r&&!o)return{};const c={...r,...o};return{MeasureLayout:r!=null&&r.isEnabled(t)||o!=null&&o.isEnabled(t)?c.MeasureLayout:void 0,ProjectionNode:c.ProjectionNode}}function Bj(t,s){if(typeof Proxy>"u")return nc;const r=new Map,o=(d,h)=>nc(d,h,t,s),c=(d,h)=>o(d,h);return new Proxy(c,{get:(d,h)=>h==="create"?o:(r.has(h)||r.set(h,nc(h,void 0,t,s)),r.get(h))})}const Oj=(t,s)=>s.isSVG??bu(t)?new w0(s):new x0(s,{allowProjection:t!==T.Fragment});class zj extends Dn{constructor(s){super(s),s.animationState||(s.animationState=C0(s))}updateAnimationControlsSubscription(){const{animate:s}=this.node.getProps();Ia(s)&&(this.unmountControls=s.subscribe(this.node))}mount(){this.updateAnimationControlsSubscription()}update(){const{animate:s}=this.node.getProps(),{animate:r}=this.node.prevProps||{};s!==r&&this.updateAnimationControlsSubscription()}unmount(){var s;this.node.animationState.reset(),(s=this.unmountControls)==null||s.call(this)}}let Uj=0;class Wj extends Dn{constructor(){super(...arguments),this.id=Uj++,this.isExitComplete=!1}update(){var d;if(!this.node.presenceContext)return;const{isPresent:s,onExitComplete:r}=this.node.presenceContext,{isPresent:o}=this.node.prevPresenceContext||{};if(!this.node.animationState||s===o)return;if(s&&o===!1){if(this.isExitComplete){const{initial:h,custom:p}=this.node.getProps();if(typeof h=="string"||typeof h=="object"&&h!==null&&!Array.isArray(h)){const f=ss(this.node,h,p);if(f){const{transition:v,transitionEnd:g,...x}=f;for(const b in x)(d=this.node.getValue(b))==null||d.jump(x[b])}}this.node.animationState.reset(),this.node.animationState.animateChanges()}else this.node.animationState.setActive("exit",!1);this.isExitComplete=!1;return}const c=this.node.animationState.setActive("exit",!s);r&&!s&&c.then(()=>{this.isExitComplete=!0,r(this.id)})}mount(){const{register:s,onExitComplete:r}=this.node.presenceContext||{};r&&r(this.id),s&&(this.unmount=s(this.id))}unmount(){}}const $j={animation:{Feature:zj},exit:{Feature:Wj}};function Bi(t){return{point:{x:t.pageX,y:t.pageY}}}const Hj=t=>s=>fu(s)&&t(s,Bi(s));function Ei(t,s,r,o){return Li(t,s,Hj(r),o)}const uy=({current:t})=>t?t.ownerDocument.defaultView:null,Op=(t,s)=>Math.abs(t-s);function Gj(t,s){const r=Op(t.x,s.x),o=Op(t.y,s.y);return Math.sqrt(r**2+o**2)}const zp=new Set(["auto","scroll"]);class dy{constructor(s,r,{transformPagePoint:o,contextWindow:c=window,dragSnapToOrigin:d=!1,distanceThreshold:h=3,element:p}={}){if(this.startEvent=null,this.lastMoveEvent=null,this.lastMoveEventInfo=null,this.lastRawMoveEventInfo=null,this.handlers={},this.contextWindow=window,this.scrollPositions=new Map,this.removeScrollListeners=null,this.onElementScroll=k=>{this.handleScroll(k.target)},this.onWindowScroll=()=>{this.handleScroll(window)},this.updatePoint=()=>{if(!(this.lastMoveEvent&&this.lastMoveEventInfo))return;this.lastRawMoveEventInfo&&(this.lastMoveEventInfo=ta(this.lastRawMoveEventInfo,this.transformPagePoint));const k=sc(this.lastMoveEventInfo,this.history),S=this.startEvent!==null,N=Gj(k.offset,{x:0,y:0})>=this.distanceThreshold;if(!S&&!N)return;const{point:O}=k,{timestamp:M}=Ke;this.history.push({...O,timestamp:M});const{onStart:L,onMove:I}=this.handlers;S||(L&&L(this.lastMoveEvent,k),this.startEvent=this.lastMoveEvent),I&&I(this.lastMoveEvent,k)},this.handlePointerMove=(k,S)=>{this.lastMoveEvent=k,this.lastRawMoveEventInfo=S,this.lastMoveEventInfo=ta(S,this.transformPagePoint),je.update(this.updatePoint,!0)},this.handlePointerUp=(k,S)=>{this.end();const{onEnd:N,onSessionEnd:O,resumeAnimation:M}=this.handlers;if((this.dragSnapToOrigin||!this.startEvent)&&M&&M(),!(this.lastMoveEvent&&this.lastMoveEventInfo))return;const L=sc(k.type==="pointercancel"?this.lastMoveEventInfo:ta(S,this.transformPagePoint),this.history);this.startEvent&&N&&N(k,L),O&&O(k,L)},!fu(s))return;this.dragSnapToOrigin=d,this.handlers=r,this.transformPagePoint=o,this.distanceThreshold=h,this.contextWindow=c||window;const f=Bi(s),v=ta(f,this.transformPagePoint),{point:g}=v,{timestamp:x}=Ke;this.history=[{...g,timestamp:x}];const{onSessionStart:b}=r;b&&b(s,sc(v,this.history));const j={passive:!0,capture:!0};this.removeListeners=Ii(Ei(this.contextWindow,"pointermove",this.handlePointerMove,j),Ei(this.contextWindow,"pointerup",this.handlePointerUp,j),Ei(this.contextWindow,"pointercancel",this.handlePointerUp,j)),p&&this.startScrollTracking(p)}startScrollTracking(s){let r=s.parentElement;for(;r;){const o=getComputedStyle(r);(zp.has(o.overflowX)||zp.has(o.overflowY))&&this.scrollPositions.set(r,{x:r.scrollLeft,y:r.scrollTop}),r=r.parentElement}this.scrollPositions.set(window,{x:window.scrollX,y:window.scrollY}),window.addEventListener("scroll",this.onElementScroll,{capture:!0}),window.addEventListener("scroll",this.onWindowScroll),this.removeScrollListeners=()=>{window.removeEventListener("scroll",this.onElementScroll,{capture:!0}),window.removeEventListener("scroll",this.onWindowScroll)}}handleScroll(s){const r=this.scrollPositions.get(s);if(!r)return;const o=s===window,c=o?{x:window.scrollX,y:window.scrollY}:{x:s.scrollLeft,y:s.scrollTop},d={x:c.x-r.x,y:c.y-r.y};d.x===0&&d.y===0||(o?this.lastMoveEventInfo&&(this.lastMoveEventInfo.point.x+=d.x,this.lastMoveEventInfo.point.y+=d.y):this.history.length>0&&(this.history[0].x-=d.x,this.history[0].y-=d.y),this.scrollPositions.set(s,c),je.update(this.updatePoint,!0))}updateHandlers(s){this.handlers=s}end(){this.removeListeners&&this.removeListeners(),this.removeScrollListeners&&this.removeScrollListeners(),this.scrollPositions.clear(),Mn(this.updatePoint)}}function ta(t,s){return s?{point:s(t.point)}:t}function Up(t,s){return{x:t.x-s.x,y:t.y-s.y}}function sc({point:t},s){return{point:t,delta:Up(t,hy(s)),offset:Up(t,Kj(s)),velocity:qj(s,.1)}}function Kj(t){return t[0]}function hy(t){return t[t.length-1]}function qj(t,s){if(t.length<2)return{x:0,y:0};let r=t.length-1,o=null;const c=hy(t);for(;r>=0&&(o=t[r],!(c.timestamp-o.timestamp>Mt(s)));)r--;if(!o)return{x:0,y:0};o===t[0]&&t.length>2&&c.timestamp-o.timestamp>Mt(s)*2&&(o=t[1]);const d=kt(c.timestamp-o.timestamp);if(d===0)return{x:0,y:0};const h={x:(c.x-o.x)/d,y:(c.y-o.y)/d};return h.x===1/0&&(h.x=0),h.y===1/0&&(h.y=0),h}function Xj(t,{min:s,max:r},o){return s!==void 0&&t<s?t=o?ke(s,t,o.min):Math.max(t,s):r!==void 0&&t>r&&(t=o?ke(r,t,o.max):Math.min(t,r)),t}function Wp(t,s,r){return{min:s!==void 0?t.min+s:void 0,max:r!==void 0?t.max+r-(t.max-t.min):void 0}}function Yj(t,{top:s,left:r,bottom:o,right:c}){return{x:Wp(t.x,r,c),y:Wp(t.y,s,o)}}function $p(t,s){let r=s.min-t.min,o=s.max-t.max;return s.max-s.min<t.max-t.min&&([r,o]=[o,r]),{min:r,max:o}}function Qj(t,s){return{x:$p(t.x,s.x),y:$p(t.y,s.y)}}function Jj(t,s){let r=.5;const o=ct(t),c=ct(s);return c>o?r=Mi(s.min,s.max-o,t.min):o>c&&(r=Mi(t.min,t.max-c,s.min)),Ut(0,1,r)}function Zj(t,s){const r={};return s.min!==void 0&&(r.min=s.min-t.min),s.max!==void 0&&(r.max=s.max-t.min),r}const zc=.35;function e1(t=zc){return t===!1?t=0:t===!0&&(t=zc),{x:Hp(t,"left","right"),y:Hp(t,"top","bottom")}}function Hp(t,s,r){return{min:Gp(t,s),max:Gp(t,r)}}function Gp(t,s){return typeof t=="number"?t:t[s]||0}const t1=new WeakMap;class n1{constructor(s){this.openDragLock=null,this.isDragging=!1,this.currentDirection=null,this.originPoint={x:0,y:0},this.constraints=!1,this.hasMutatedConstraints=!1,this.elastic=Ge(),this.latestPointerEvent=null,this.latestPanInfo=null,this.visualElement=s}start(s,{snapToCursor:r=!1,distanceThreshold:o}={}){const{presenceContext:c}=this.visualElement;if(c&&c.isPresent===!1)return;const d=x=>{r&&this.snapToCursor(Bi(x).point),this.stopAnimation()},h=(x,b)=>{const{drag:j,dragPropagation:k,onDragStart:S}=this.getProps();if(j&&!k&&(this.openDragLock&&this.openDragLock(),this.openDragLock=qk(j),!this.openDragLock))return;this.latestPointerEvent=x,this.latestPanInfo=b,this.isDragging=!0,this.currentDirection=null,this.resolveConstraints(),this.visualElement.projection&&(this.visualElement.projection.isAnimationBlocked=!0,this.visualElement.projection.target=void 0),qt(O=>{let M=this.getAxisMotionValue(O).get()||0;if(Qt.test(M)){const{projection:L}=this.visualElement;if(L&&L.layout){const I=L.layout.layoutBox[O];I&&(M=ct(I)*(parseFloat(M)/100))}}this.originPoint[O]=M}),S&&je.update(()=>S(x,b),!1,!0),Rc(this.visualElement,"transform");const{animationState:N}=this.visualElement;N&&N.setActive("whileDrag",!0)},p=(x,b)=>{this.latestPointerEvent=x,this.latestPanInfo=b;const{dragPropagation:j,dragDirectionLock:k,onDirectionLock:S,onDrag:N}=this.getProps();if(!j&&!this.openDragLock)return;const{offset:O}=b;if(k&&this.currentDirection===null){this.currentDirection=i1(O),this.currentDirection!==null&&S&&S(this.currentDirection);return}this.updateAxis("x",b.point,O),this.updateAxis("y",b.point,O),this.visualElement.render(),N&&je.update(()=>N(x,b),!1,!0)},f=(x,b)=>{this.latestPointerEvent=x,this.latestPanInfo=b,this.stop(x,b),this.latestPointerEvent=null,this.latestPanInfo=null},v=()=>{const{dragSnapToOrigin:x}=this.getProps();(x||this.constraints)&&this.startAnimation({x:0,y:0})},{dragSnapToOrigin:g}=this.getProps();this.panSession=new dy(s,{onSessionStart:d,onStart:h,onMove:p,onSessionEnd:f,resumeAnimation:v},{transformPagePoint:this.visualElement.getTransformPagePoint(),dragSnapToOrigin:g,distanceThreshold:o,contextWindow:uy(this.visualElement),element:this.visualElement.current})}stop(s,r){const o=s||this.latestPointerEvent,c=r||this.latestPanInfo,d=this.isDragging;if(this.cancel(),!d||!c||!o)return;const{velocity:h}=c;this.startAnimation(h);const{onDragEnd:p}=this.getProps();p&&je.postRender(()=>p(o,c))}cancel(){this.isDragging=!1;const{projection:s,animationState:r}=this.visualElement;s&&(s.isAnimationBlocked=!1),this.endPanSession();const{dragPropagation:o}=this.getProps();!o&&this.openDragLock&&(this.openDragLock(),this.openDragLock=null),r&&r.setActive("whileDrag",!1)}endPanSession(){this.panSession&&this.panSession.end(),this.panSession=void 0}updateAxis(s,r,o){const{drag:c}=this.getProps();if(!o||!na(s,c,this.currentDirection))return;const d=this.getAxisMotionValue(s);let h=this.originPoint[s]+o[s];this.constraints&&this.constraints[s]&&(h=Xj(h,this.constraints[s],this.elastic[s])),d.set(h)}resolveConstraints(){var d;const{dragConstraints:s,dragElastic:r}=this.getProps(),o=this.visualElement.projection&&!this.visualElement.projection.layout?this.visualElement.projection.measure(!1):(d=this.visualElement.projection)==null?void 0:d.layout,c=this.constraints;s&&Ms(s)?this.constraints||(this.constraints=this.resolveRefConstraints()):s&&o?this.constraints=Yj(o.layoutBox,s):this.constraints=!1,this.elastic=e1(r),c!==this.constraints&&!Ms(s)&&o&&this.constraints&&!this.hasMutatedConstraints&&qt(h=>{this.constraints!==!1&&this.getAxisMotionValue(h)&&(this.constraints[h]=Zj(o.layoutBox[h],this.constraints[h]))})}resolveRefConstraints(){const{dragConstraints:s,onMeasureDragConstraints:r}=this.getProps();if(!s||!Ms(s))return!1;const o=s.current,{projection:c}=this.visualElement;if(!c||!c.layout)return!1;c.root&&(c.root.scroll=void 0,c.root.updateScroll());const d=Kk(o,c.root,this.visualElement.getTransformPagePoint());let h=Qj(c.layout.layoutBox,d);if(r){const p=r($k(h));this.hasMutatedConstraints=!!p,p&&(h=Pg(p))}return h}startAnimation(s){const{drag:r,dragMomentum:o,dragElastic:c,dragTransition:d,dragSnapToOrigin:h,onDragTransitionEnd:p}=this.getProps(),f=this.constraints||{},v=qt(g=>{if(!na(g,r,this.currentDirection))return;let x=f&&f[g]||{};(h===!0||h===g)&&(x={min:0,max:0});const b=c?200:1e6,j=c?40:1e7,k={type:"inertia",velocity:o?s[g]:0,bounceStiffness:b,bounceDamping:j,timeConstant:750,restDelta:1,restSpeed:10,...d,...x};return this.startAxisValueAnimation(g,k)});return Promise.all(v).then(p)}startAxisValueAnimation(s,r){const o=this.getAxisMotionValue(s);return Rc(this.visualElement,s),o.start(lu(s,o,0,r,this.visualElement,!1))}stopAnimation(){qt(s=>this.getAxisMotionValue(s).stop())}getAxisMotionValue(s){const r=`_drag${s.toUpperCase()}`,c=this.visualElement.getProps()[r];return c||this.visualElement.getValue(s,this.visualElement.latestValues[s]??0)}snapToCursor(s){qt(r=>{const{drag:o}=this.getProps();if(!na(r,o,this.currentDirection))return;const{projection:c}=this.visualElement,d=this.getAxisMotionValue(r);if(c&&c.layout){const{min:h,max:p}=c.layout.layoutBox[r],f=d.get()||0;d.set(s[r]-ke(h,p,.5)+f)}})}scalePositionWithinConstraints(){if(!this.visualElement.current)return;const{drag:s,dragConstraints:r}=this.getProps(),{projection:o}=this.visualElement;if(!Ms(r)||!o||!this.constraints)return;this.stopAnimation();const c={x:0,y:0};qt(h=>{const p=this.getAxisMotionValue(h);if(p&&this.constraints!==!1){const f=p.get();c[h]=Jj({min:f,max:f},this.constraints[h])}});const{transformTemplate:d}=this.visualElement.getProps();this.visualElement.current.style.transform=d?d({},""):"none",o.root&&o.root.updateScroll(),o.updateLayout(),this.constraints=!1,this.resolveConstraints(),qt(h=>{if(!na(h,s,null))return;const p=this.getAxisMotionValue(h),{min:f,max:v}=this.constraints[h];p.set(ke(f,v,c[h]))}),this.visualElement.render()}addListeners(){if(!this.visualElement.current)return;t1.set(this.visualElement,this);const s=this.visualElement.current,r=Ei(s,"pointerdown",v=>{const{drag:g,dragListener:x=!0}=this.getProps(),b=v.target,j=b!==s&&e0(b);g&&x&&!j&&this.start(v)});let o;const c=()=>{const{dragConstraints:v}=this.getProps();Ms(v)&&v.current&&(this.constraints=this.resolveRefConstraints(),o||(o=s1(s,v.current,()=>this.scalePositionWithinConstraints())))},{projection:d}=this.visualElement,h=d.addEventListener("measure",c);d&&!d.layout&&(d.root&&d.root.updateScroll(),d.updateLayout()),je.read(c);const p=Li(window,"resize",()=>this.scalePositionWithinConstraints()),f=d.addEventListener("didUpdate",(({delta:v,hasLayoutChanged:g})=>{this.isDragging&&g&&(qt(x=>{const b=this.getAxisMotionValue(x);b&&(this.originPoint[x]+=v[x].translate,b.set(b.get()+v[x].translate))}),this.visualElement.render())}));return()=>{p(),r(),h(),f&&f(),o&&o()}}getProps(){const s=this.visualElement.getProps(),{drag:r=!1,dragDirectionLock:o=!1,dragPropagation:c=!1,dragConstraints:d=!1,dragElastic:h=zc,dragMomentum:p=!0}=s;return{...s,drag:r,dragDirectionLock:o,dragPropagation:c,dragConstraints:d,dragElastic:h,dragMomentum:p}}}function Kp(t){let s=!0;return()=>{if(s){s=!1;return}t()}}function s1(t,s,r){const o=lp(t,Kp(r)),c=lp(s,Kp(r));return()=>{o(),c()}}function na(t,s,r){return(s===!0||s===t)&&(r===null||r===t)}function i1(t,s=10){let r=null;return Math.abs(t.y)>s?r="y":Math.abs(t.x)>s&&(r="x"),r}class r1 extends Dn{constructor(s){super(s),this.removeGroupControls=zt,this.removeListeners=zt,this.controls=new n1(s)}mount(){const{dragControls:s}=this.node.getProps();s&&(this.removeGroupControls=s.subscribe(this.controls)),this.removeListeners=this.controls.addListeners()||zt}update(){const{dragControls:s}=this.node.getProps(),{dragControls:r}=this.node.prevProps||{};s!==r&&(this.removeGroupControls(),s&&(this.removeGroupControls=s.subscribe(this.controls)))}unmount(){this.removeGroupControls(),this.removeListeners(),this.controls.isDragging||this.controls.endPanSession()}}const ic=t=>(s,r)=>{t&&je.update(()=>t(s,r),!1,!0)};class a1 extends Dn{constructor(){super(...arguments),this.removePointerDownListener=zt}onPointerDown(s){this.session=new dy(s,this.createPanHandlers(),{transformPagePoint:this.node.getTransformPagePoint(),contextWindow:uy(this.node)})}createPanHandlers(){const{onPanSessionStart:s,onPanStart:r,onPan:o,onPanEnd:c}=this.node.getProps();return{onSessionStart:ic(s),onStart:ic(r),onMove:ic(o),onEnd:(d,h)=>{delete this.session,c&&je.postRender(()=>c(d,h))}}}mount(){this.removePointerDownListener=Ei(this.node.current,"pointerdown",s=>this.onPointerDown(s))}update(){this.session&&this.session.updateHandlers(this.createPanHandlers())}unmount(){this.removePointerDownListener(),this.session&&this.session.end()}}let rc=!1;class o1 extends T.Component{componentDidMount(){const{visualElement:s,layoutGroup:r,switchLayoutGroup:o,layoutId:c}=this.props,{projection:d}=s;d&&(r.group&&r.group.add(d),o&&o.register&&c&&o.register(d),rc&&d.root.didUpdate(),d.addEventListener("animationComplete",()=>{this.safeToRemove()}),d.setOptions({...d.options,layoutDependency:this.props.layoutDependency,onExitComplete:()=>this.safeToRemove()})),ma.hasEverUpdated=!0}getSnapshotBeforeUpdate(s){const{layoutDependency:r,visualElement:o,drag:c,isPresent:d}=this.props,{projection:h}=o;return h&&(h.isPresent=d,s.layoutDependency!==r&&h.setOptions({...h.options,layoutDependency:r}),rc=!0,c||s.layoutDependency!==r||r===void 0||s.isPresent!==d?h.willUpdate():this.safeToRemove(),s.isPresent!==d&&(d?h.promote():h.relegate()||je.postRender(()=>{const p=h.getStack();(!p||!p.members.length)&&this.safeToRemove()}))),null}componentDidUpdate(){const{visualElement:s,layoutAnchor:r}=this.props,{projection:o}=s;o&&(o.options.layoutAnchor=r,o.root.didUpdate(),pu.postRender(()=>{!o.currentAnimation&&o.isLead()&&this.safeToRemove()}))}componentWillUnmount(){const{visualElement:s,layoutGroup:r,switchLayoutGroup:o}=this.props,{projection:c}=s;rc=!0,c&&(c.scheduleCheckAfterUnmount(),r&&r.group&&r.group.remove(c),o&&o.deregister&&o.deregister(c))}safeToRemove(){const{safeToRemove:s}=this.props;s&&s()}render(){return null}}function my(t){const[s,r]=pj(),o=T.useContext(_f);return i.jsx(o1,{...t,layoutGroup:o,switchLayoutGroup:T.useContext(ly),isPresent:s,safeToRemove:r})}const l1={pan:{Feature:a1},drag:{Feature:r1,ProjectionNode:ty,MeasureLayout:my}};function qp(t,s,r){const{props:o}=t;t.animationState&&o.whileHover&&t.animationState.setActive("whileHover",r==="Start");const c="onHover"+r,d=o[c];d&&je.postRender(()=>d(s,Bi(s)))}class c1 extends Dn{mount(){const{current:s}=this.node;s&&(this.unmount=Yk(s,(r,o)=>(qp(this.node,o,"Start"),c=>qp(this.node,c,"End"))))}unmount(){}}class u1 extends Dn{constructor(){super(...arguments),this.isActive=!1}onFocus(){let s=!1;try{s=this.node.current.matches(":focus-visible")}catch{s=!0}!s||!this.node.animationState||(this.node.animationState.setActive("whileFocus",!0),this.isActive=!0)}onBlur(){!this.isActive||!this.node.animationState||(this.node.animationState.setActive("whileFocus",!1),this.isActive=!1)}mount(){this.unmount=Ii(Li(this.node.current,"focus",()=>this.onFocus()),Li(this.node.current,"blur",()=>this.onBlur()))}unmount(){}}function Xp(t,s,r){const{props:o}=t;if(t.current instanceof HTMLButtonElement&&t.current.disabled)return;t.animationState&&o.whileTap&&t.animationState.setActive("whileTap",r==="Start");const c="onTap"+(r==="End"?"":r),d=o[c];d&&je.postRender(()=>d(s,Bi(s)))}class d1 extends Dn{mount(){const{current:s}=this.node;if(!s)return;const{globalTapTarget:r,propagate:o}=this.node.props;this.unmount=n0(s,(c,d)=>(Xp(this.node,d,"Start"),(h,{success:p})=>Xp(this.node,h,p?"End":"Cancel")),{useGlobalTarget:r,stopPropagation:(o==null?void 0:o.tap)===!1})}unmount(){}}const Uc=new WeakMap,ac=new WeakMap,h1=t=>{const s=Uc.get(t.target);s&&s(t)},m1=t=>{t.forEach(h1)};function p1({root:t,...s}){const r=t||document;ac.has(r)||ac.set(r,{});const o=ac.get(r),c=JSON.stringify(s);return o[c]||(o[c]=new IntersectionObserver(m1,{root:t,...s})),o[c]}function f1(t,s,r){const o=p1(s);return Uc.set(t,r),o.observe(t),()=>{Uc.delete(t),o.unobserve(t)}}const g1={some:0,all:1};class y1 extends Dn{constructor(){super(...arguments),this.hasEnteredView=!1,this.isInView=!1}startObserver(){var f;(f=this.stopObserver)==null||f.call(this);const{viewport:s={}}=this.node.getProps(),{root:r,margin:o,amount:c="some",once:d}=s,h={root:r?r.current:void 0,rootMargin:o,threshold:typeof c=="number"?c:g1[c]},p=v=>{const{isIntersecting:g}=v;if(this.isInView===g||(this.isInView=g,d&&!g&&this.hasEnteredView))return;g&&(this.hasEnteredView=!0),this.node.animationState&&this.node.animationState.setActive("whileInView",g);const{onViewportEnter:x,onViewportLeave:b}=this.node.getProps(),j=g?x:b;j&&j(v)};this.stopObserver=f1(this.node.current,h,p)}mount(){this.startObserver()}update(){if(typeof IntersectionObserver>"u")return;const{props:s,prevProps:r}=this.node;["amount","margin","root"].some(v1(s,r))&&this.startObserver()}unmount(){var s;(s=this.stopObserver)==null||s.call(this),this.hasEnteredView=!1,this.isInView=!1}}function v1({viewport:t={}},{viewport:s={}}={}){return r=>t[r]!==s[r]}const x1={inView:{Feature:y1},tap:{Feature:d1},focus:{Feature:u1},hover:{Feature:c1}},b1={layout:{ProjectionNode:ty,MeasureLayout:my}},w1={...$j,...x1,...l1,...b1},k1=Bj(w1,Oj);function j1(){!yu.current&&Vg();const[t]=T.useState(Ta.current);return t}const Yp=k1,S1={type:"spring",stiffness:620,damping:42,mass:.35},N1={type:"spring",stiffness:460,damping:38,mass:.8},C1=typeof window>"u"?T.useEffect:T.useLayoutEffect;function T1({items:t,value:s,defaultValue:r,onValueChange:o,activation:c="automatic"}){const d=T.useId(),h=T.useRef(new Map),p=T.useRef(1),[f,v]=T.useState(()=>{var M,L;return r??((M=t.find(I=>!I.disabled))==null?void 0:M.value)??((L=t[0])==null?void 0:L.value)??""}),g=s??f,x=T.useRef(o);x.current=o;const b=T.useCallback(M=>{var D;if(M===g||!t.some(B=>B.value===M&&!B.disabled))return;const L=t.findIndex(B=>B.value===g),I=t.findIndex(B=>B.value===M);p.current=I<L?-1:1,s===void 0&&v(M),(D=x.current)==null||D.call(x,M)},[s,t,g]),j=T.useCallback(M=>{var I;const L=t[M];L&&((I=h.current.get(L.value))==null||I.focus())},[t]),k=T.useCallback((M,L)=>{const I=t.length;if(!I)return 0;let D=M;for(let B=0;B<I;B+=1)if(D=(D+L+I)%I,!t[D].disabled)return D;return M},[t]),S=T.useCallback(M=>{const L=t.map((I,D)=>D);return M&&L.reverse(),L.find(I=>!t[I].disabled)??0},[t]),N=T.useCallback((M,L)=>({id:`${d}-tab-${M.value}`,role:"tab",type:"button","aria-selected":M.value===g,"aria-controls":`${d}-panel-${M.value}`,"aria-disabled":M.disabled?!0:void 0,tabIndex:M.value===g?0:-1,ref:I=>{I?h.current.set(M.value,I):h.current.delete(M.value)},onClick:()=>{M.disabled||b(M.value)},onKeyDown:I=>{if(I.key==="ArrowRight"||I.key==="ArrowLeft"){I.preventDefault();const D=k(L,I.key==="ArrowRight"?1:-1);j(D),c==="automatic"&&b(t[D].value)}else if(I.key==="Home"||I.key==="End"){I.preventDefault();const D=S(I.key==="End");j(D),c==="automatic"&&b(t[D].value)}else(I.key==="Enter"||I.key===" ")&&(I.preventDefault(),M.disabled||b(M.value))}}),[c,d,S,j,t,k,b,g]),O=T.useCallback(M=>({id:`${d}-panel-${M}`,role:"tabpanel","aria-labelledby":`${d}-tab-${M}`,tabIndex:0}),[d]);return{value:g,select:b,direction:p.current,tabListProps:{role:"tablist","aria-orientation":"horizontal"},getTabProps:N,getPanelProps:O}}function P1({items:t,value:s,defaultValue:r,onValueChange:o,activation:c="automatic",renderPanel:d,label:h="Tabs",panelClassName:p="",className:f=""}){const v=T1({items:t,value:s,defaultValue:r,onValueChange:o,activation:c}),g=j1(),x=T.useRef(null),b=T.useRef([]),[j,k]=T.useState({x:0,width:0,ready:!1}),S=t.findIndex(N=>N.value===v.value);return C1(()=>{const N=b.current[S],O=x.current;if(!N||!O)return;const M=()=>k(I=>I.x===N.offsetLeft&&I.width===N.offsetWidth&&I.ready?I:{x:N.offsetLeft,width:N.offsetWidth,ready:!0});M();const L=new ResizeObserver(M);return L.observe(O),()=>L.disconnect()},[t,S]),i.jsxs("div",{className:`stats-tabs ${f}`,children:[i.jsxs("div",{...v.tabListProps,ref:x,"aria-label":h,className:"stats-tabs-list",children:[i.jsx(Yp.span,{layout:!0,"aria-hidden":"true",className:"stats-tabs-indicator",style:{left:j.x,width:j.width,opacity:j.ready?1:0},transition:g?{duration:0}:S1}),t.map((N,O)=>{const M=N.value===v.value,{ref:L,...I}=v.getTabProps(N,O);return i.jsx("button",{...I,ref:D=>{L(D),b.current[O]=D},className:`stats-tab${M?" selected":""}${N.disabled?" disabled":""}`,children:N.label},N.value)})]}),d&&i.jsx(Yp.div,{custom:v.direction,...v.getPanelProps(v.value),initial:g?!1:{opacity:0,x:v.direction*12},animate:{opacity:1,x:0},transition:g?{duration:0}:N1,className:`stats-tab-panel ${p}`,children:d(v.value)},v.value)]})}const A1=[{value:"messages",label:"Messages"},{value:"members",label:"Members"},{value:"layout",label:"Server layout"}];function py(t){return new Intl.DateTimeFormat(void 0,{weekday:"short"}).format(new Date(`${t}T12:00:00`))}function E1({stats:t}){const s=t.activity.map(d=>d.messages),r=Math.max(1,...s),o=s.map((d,h)=>{const p=s.length>1?12+h*276/(s.length-1):150,f=102-d/r*78;return`${p},${f}`}).join(" "),c=`12,104 ${o} 288,104`;return i.jsxs("div",{className:"server-chart-wrap",children:[i.jsxs("div",{className:"server-chart-heading",children:[i.jsxs("div",{children:[i.jsx("span",{children:"Daily messages"}),i.jsx("strong",{children:xe(s.reduce((d,h)=>d+h,0))})]}),i.jsx("small",{children:"Last 14 days"})]}),i.jsxs("svg",{className:"server-line-chart",viewBox:"0 0 300 122",role:"img","aria-label":"Daily messages over the last fourteen days",children:[i.jsx("defs",{children:i.jsxs("linearGradient",{id:"message-area-fill",x1:"0",x2:"0",y1:"0",y2:"1",children:[i.jsx("stop",{offset:"0%",stopColor:"var(--accent)",stopOpacity:".24"}),i.jsx("stop",{offset:"100%",stopColor:"var(--accent)",stopOpacity:"0"})]})}),[24,50,76,104].map(d=>i.jsx("line",{x1:"12",x2:"288",y1:d,y2:d,className:"server-chart-gridline"},d)),i.jsx("polygon",{points:c,fill:"url(#message-area-fill)"}),i.jsx("polyline",{points:o,className:"server-chart-line"}),t.activity.map((d,h)=>{const p=s.length>1?12+h*276/(s.length-1):150,f=102-d.messages/r*78;return i.jsx("circle",{cx:p,cy:f,r:"2.7",className:"server-chart-point",children:i.jsx("title",{children:`${d.date}: ${xe(d.messages)} messages`})},d.date)})]}),i.jsx("div",{className:"server-chart-days",children:t.activity.filter((d,h)=>h%2===0).map(d=>i.jsx("span",{children:py(d.date)},d.date))})]})}function M1({stats:t}){const s=Math.max(1,...t.activity.flatMap(r=>[r.joins,r.leaves]));return i.jsxs("div",{className:"server-chart-wrap",children:[i.jsxs("div",{className:"server-chart-heading",children:[i.jsxs("div",{children:[i.jsx("span",{children:"Member changes"}),i.jsxs("strong",{children:[xe(t.activity.reduce((r,o)=>r+o.joins,0))," joined"]})]}),i.jsx("small",{children:"Last 14 days"})]}),i.jsx("div",{className:"server-member-chart",role:"img","aria-label":"Daily member joins and departures over the last fourteen days",children:t.activity.map(r=>i.jsxs("div",{className:"server-member-day",title:`${r.date}: ${r.joins} joined, ${r.leaves} left`,children:[i.jsxs("div",{className:"server-member-bars",children:[i.jsx("i",{className:"join-bar",style:{height:`${Math.max(r.joins?5:0,r.joins/s*76)}%`}}),i.jsx("i",{className:"leave-bar",style:{height:`${Math.max(r.leaves?5:0,r.leaves/s*76)}%`}})]}),i.jsx("span",{children:py(r.date).slice(0,1)})]},r.date))}),i.jsxs("div",{className:"server-chart-legend",children:[i.jsxs("span",{children:[i.jsx("i",{className:"join-key"})," Joined ",i.jsx("b",{children:xe(t.activity.reduce((r,o)=>r+o.joins,0))})]}),i.jsxs("span",{children:[i.jsx("i",{className:"leave-key"})," Left ",i.jsx("b",{children:xe(t.activity.reduce((r,o)=>r+o.leaves,0))})]})]})]})}function _1({stats:t}){const s=Math.max(t.member_count,t.channel_count,t.role_count,1),r=[{label:"Members",value:t.member_count,color:"members"},{label:"Channels",value:t.channel_count,color:"channels"},{label:"Roles",value:t.role_count,color:"roles"}];return i.jsxs("div",{className:"server-layout-chart",children:[i.jsxs("div",{className:"server-layout-total",children:[i.jsx("span",{children:"Community size"}),i.jsx("strong",{children:xe(t.member_count)}),i.jsx("small",{children:"members currently in this server"})]}),i.jsx("div",{className:"server-layout-bars",children:r.map(o=>i.jsxs("div",{className:"server-layout-row",children:[i.jsxs("div",{children:[i.jsx("span",{children:o.label}),i.jsx("strong",{children:xe(o.value)})]}),i.jsx("div",{className:"server-layout-track",children:i.jsx("i",{className:`layout-${o.color}`,style:{width:`${Math.max(o.value?4:0,o.value/s*100)}%`}})})]},o.label))})]})}function D1({stats:t}){const[s,r]=T.useState("messages"),o=T.useMemo(()=>({messages:t.activity.reduce((d,h)=>d+h.messages,0),joins:t.activity.reduce((d,h)=>d+h.joins,0)}),[t.activity]),c=s==="members"?i.jsx(M1,{stats:t}):s==="layout"?i.jsx(_1,{stats:t}):i.jsx(E1,{stats:t});return i.jsxs("section",{className:"dash-panel server-stats-card","aria-label":"Server statistics",children:[i.jsxs("div",{className:"panel-heading server-stats-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Community analytics"}),i.jsx("h3",{children:"Server pulse"}),i.jsx("p",{children:"Daily activity tracked by Niko · last 14 days"})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(sb,{})})]}),i.jsxs("div",{className:"server-stat-metrics",children:[i.jsxs("div",{children:[i.jsx(gc,{}),i.jsx("span",{children:"Members"}),i.jsx("strong",{children:xe(t.member_count)})]}),i.jsxs("div",{children:[i.jsx(aa,{}),i.jsx("span",{children:"Messages · 14d"}),i.jsx("strong",{children:xe(o.messages)})]}),i.jsxs("div",{children:[i.jsx(ab,{}),i.jsx("span",{children:"New members · 14d"}),i.jsx("strong",{children:xe(o.joins)})]})]}),i.jsx(P1,{items:A1,value:s,onValueChange:r,label:"Server statistics",renderPanel:()=>c}),i.jsx("div",{className:"server-stats-footnote",children:"Activity is collected from the moment tracking is enabled."})]})}function cn({eyebrow:t,title:s,text:r}){return i.jsxs("div",{className:"dash-heading",children:[i.jsxs("div",{className:"heading-meta",children:[i.jsx("div",{className:"eyebrow",children:t}),i.jsx("span",{className:"heading-context",children:"NIKO / CONTROL ROOM"})]}),i.jsx("h2",{children:s}),i.jsx("p",{children:r})]})}function Yt({label:t,value:s,note:r,accent:o=""}){return i.jsxs("div",{className:`dash-stat ${o}`,children:[i.jsx("span",{children:t}),i.jsx("strong",{children:s}),i.jsx("small",{children:r})]})}function R1({user:t,overview:s,guilds:r,onServers:o,onManage:c}){const d=r.filter(h=>h.installed!==!1);return i.jsxs(i.Fragment,{children:[i.jsx(cn,{eyebrow:"Personal overview",title:"Your Niko snapshot.",text:"Keep an eye on your progress, then jump into a server when you’re ready to tune the room."}),i.jsxs("div",{className:"overview-intro",children:[i.jsxs("div",{className:"profile-card",children:[i.jsx(Ef,{user:t,className:"profile-avatar"}),i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Signed in as"}),i.jsx("h3",{children:Pf(t)}),i.jsx("p",{children:"Personal economy profile"})]})]}),i.jsxs("button",{className:"button button-primary",onClick:o,children:["Manage a server ",i.jsx(X,{name:"arrow"})]})]}),i.jsxs("div",{className:"dash-stats overview-stats",children:[i.jsx(Yt,{label:"Net worth",value:xe(s==null?void 0:s.net_worth),note:"Across your Niko profile",accent:"accent-orange"}),i.jsx(Yt,{label:"In your wallet",value:xe(s==null?void 0:s.balance),note:"Ready to spend",accent:"accent-violet"}),i.jsx(Yt,{label:"In your vault",value:xe(s==null?void 0:s.bank),note:"Saved for later",accent:"accent-blue"}),i.jsx(Yt,{label:"Current level",value:xe(s==null?void 0:s.level),note:s!=null&&s.job?`Working as a ${s.job}`:"Keep showing up",accent:"accent-green"})]}),i.jsxs("div",{className:"dash-columns overview-columns",children:[i.jsxs("section",{className:"dash-panel",children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Progress"}),i.jsx("h3",{children:"Your momentum"})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(X,{name:"spark"})})]}),i.jsxs("div",{className:"metric-list",children:[i.jsxs("div",{children:[i.jsx("span",{children:"Daily streak"}),i.jsxs("strong",{children:[xe(s==null?void 0:s.daily_streak)," ",i.jsx("small",{children:"days"})]})]}),i.jsxs("div",{children:[i.jsx("span",{children:"Achievements"}),i.jsxs("strong",{children:[xe(s==null?void 0:s.achievements)," ",i.jsx("small",{children:"unlocked"})]})]}),i.jsxs("div",{children:[i.jsx("span",{children:"Total earned"}),i.jsxs("strong",{children:[xe(s==null?void 0:s.total_earned)," ",i.jsx("small",{children:"coins"})]})]}),i.jsxs("div",{children:[i.jsx("span",{children:"Economy standing"}),i.jsxs("strong",{children:[s!=null&&s.economy_rank?`#${xe(s.economy_rank)}`:"—"," ",i.jsx("small",{children:s!=null&&s.economy_profiles?`of ${xe(s.economy_profiles)}`:""})]})]})]})]}),i.jsxs("section",{className:"dash-panel",children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Quick access"}),i.jsx("h3",{children:"Your servers"})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(X,{name:"users"})})]}),i.jsxs("div",{className:"mini-server-list",children:[d.slice(0,4).map(h=>i.jsxs("button",{onClick:()=>c(h),children:[i.jsx($c,{guild:h}),i.jsx("span",{children:h.name}),i.jsx(X,{name:"arrow"})]},h.id)),!d.length&&i.jsx("p",{className:"empty-state compact",children:"Add Niko to a server to start managing it."})]}),i.jsxs("button",{className:"text-link overview-link",onClick:o,children:["View all servers ",i.jsx(X,{name:"arrow"})]})]})]})]})}function Qp({guild:t,onManage:s}){const r=t.installed!==!1;return i.jsxs("article",{className:"server-card",children:[i.jsxs("div",{className:"server-card-heading",children:[i.jsx($c,{guild:t,className:"server-avatar"}),i.jsx("span",{className:"server-status",children:r?"Niko is installed":"Ready to add"})]}),i.jsx("h3",{children:t.name}),i.jsx("p",{children:r?"Open the dashboard to manage Niko’s features and settings.":"You have permission to manage this server. Add Niko to unlock its controls."}),r?i.jsxs("button",{className:"button button-muted button-small",onClick:()=>s(t),children:["Open settings ",i.jsx(X,{name:"arrow"})]}):i.jsxs("a",{className:"button button-primary button-small",href:t.invite_url||"#",target:"_blank",rel:"noreferrer",children:["Add Niko ",i.jsx(X,{name:"external"})]})]})}function L1({guilds:t,onManage:s}){const r=t.filter(c=>c.installed!==!1),o=t.filter(c=>c.installed===!1);return i.jsxs(i.Fragment,{children:[i.jsx(cn,{eyebrow:"Servers",title:"Choose where to work.",text:"Manage servers with Niko already installed, or add Niko to another server you can administer."}),i.jsxs("div",{className:"server-summary",children:[i.jsxs("div",{children:[i.jsx("strong",{children:xe(r.length)}),i.jsx("span",{children:"Connected to Niko"})]}),i.jsxs("div",{children:[i.jsx("strong",{children:xe(o.length)}),i.jsx("span",{children:"Ready to add"})]}),i.jsxs("div",{className:"server-summary-note",children:[i.jsx(X,{name:"shield"}),i.jsx("span",{children:"Only servers where you have Manage Server access are shown."})]})]}),i.jsxs("section",{className:"server-section",children:[i.jsxs("div",{className:"section-heading-row",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Connected"}),i.jsx("h3",{children:"Manage a server"})]}),i.jsx("span",{className:"section-count",children:r.length})]}),i.jsxs("div",{className:"server-grid",children:[r.map(c=>i.jsx(Qp,{guild:c,onManage:s},c.id)),!r.length&&i.jsxs("div",{className:"empty-state",children:[i.jsx("strong",{children:"No connected servers yet."}),i.jsx("span",{children:"Add Niko below, then come back here to manage it."})]})]})]}),i.jsxs("section",{className:"server-section",children:[i.jsxs("div",{className:"section-heading-row",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Available to you"}),i.jsx("h3",{children:"Add Niko to a server"})]}),i.jsx("span",{className:"section-count",children:o.length})]}),i.jsxs("div",{className:"server-grid",children:[o.map(c=>i.jsx(Qp,{guild:c,onManage:s},c.id)),!o.length&&i.jsx("div",{className:"server-note",children:"Niko is already installed in every server you can manage."})]})]})]})}function fy({rows:t}){return i.jsxs("div",{className:"rank-list",children:[t.slice(0,5).map((s,r)=>i.jsxs("div",{className:"rank-row",children:[i.jsx("span",{className:`rank rank-${r+1}`,children:String(r+1).padStart(2,"0")}),i.jsxs("span",{className:"rank-user",children:[i.jsx(kb,{name:s.display_name||s.username||"Unknown member",avatarUrl:s.avatar_url}),i.jsxs("span",{children:[i.jsx("strong",{children:s.display_name||s.username||"Unknown member"}),s.username&&s.display_name&&i.jsxs("small",{children:["@",s.username]})]})]}),i.jsxs("strong",{children:["Level ",xe(s.level),i.jsxs("small",{children:[xe(s.xp)," xp"]})]})]},`${s.user_id}-${r}`)),!t.length&&i.jsx("div",{className:"empty-state compact",children:"No data recorded yet."})]})}function I1({overview:t}){return i.jsxs(i.Fragment,{children:[i.jsxs("div",{className:"guild-welcome",children:[i.jsxs("div",{children:[i.jsx("span",{className:"welcome-mark",children:i.jsx(X,{name:"grid"})}),i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Server pulse"}),i.jsx("strong",{children:"Here’s what needs your attention."})]})]}),i.jsxs("span",{className:"welcome-time",children:["LIVE SIGNALS ",i.jsx("span",{className:"status-dot"})]})]}),i.jsx(cn,{eyebrow:"Overview",title:"A quick read on your room.",text:"The important signals, without making you hunt for them."}),i.jsxs("div",{className:"dash-stats guild-overview-stats",children:[i.jsx(Yt,{label:"Warnings logged",value:xe(t.moderation.warn_count),note:"For this server",accent:"accent-blue"}),i.jsx(Yt,{label:"Automod",value:t.moderation.automod_active?"Active":"Quiet",note:"Protection status",accent:"accent-green"}),i.jsx(Yt,{label:"Level leaders",value:xe(t.leveling.top.length),note:"Members with recorded XP",accent:"accent-violet"})]}),i.jsx(D1,{stats:t.server}),i.jsxs("div",{className:"dash-columns overview-columns",children:[i.jsxs("section",{className:"dash-panel",children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Community energy"}),i.jsx("h3",{children:"Top XP"})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(X,{name:"spark"})})]}),i.jsx(fy,{rows:t.leveling.top})]}),i.jsxs("section",{className:"dash-panel",children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Server controls"}),i.jsx("h3",{children:"Manage the room"})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(X,{name:"settings"})})]}),i.jsxs("div",{className:"server-controls-body",children:[i.jsx("p",{children:"Use Server settings for prefixes, welcome messages, logs, and ticket panels."}),i.jsxs("span",{className:"text-link",children:["Open server settings ",i.jsx(X,{name:"arrow"})]})]})]})]})]})}function V1({rows:t,config:s,resources:r,csrfToken:o,guildId:c}){var d,h,p;return i.jsxs(i.Fragment,{children:[i.jsx(cn,{eyebrow:"Leveling",title:"Momentum people can see.",text:"Track the members turning up, and tune the pace to fit your server."}),i.jsxs("div",{className:"dash-stats",children:[i.jsx(Yt,{label:"Top level",value:String(((d=t[0])==null?void 0:d.level)||0),note:((h=t[0])==null?void 0:h.display_name)||((p=t[0])==null?void 0:p.username)||"No members yet",accent:"accent-violet"}),i.jsx(Yt,{label:"XP multiplier",value:`${(s==null?void 0:s.leveling.xp_multiplier)||1}×`,note:(s==null?void 0:s.leveling.xp_enabled)===!1?"XP disabled":"Currently active",accent:"accent-blue"}),i.jsx(Yt,{label:"Cooldown",value:`${(s==null?void 0:s.leveling.xp_cooldown)||0}s`,note:"Between XP awards",accent:"accent-green"})]}),i.jsxs("section",{className:"dash-panel",children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Leaderboard"}),i.jsx("h3",{children:"XP leaders"})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(X,{name:"spark"})})]}),i.jsx(fy,{rows:t})]}),i.jsx(z1,{guildId:c,config:s,resources:r,csrfToken:o})]})}const Ba={saving:!1,message:"",error:""};function lt({label:t,hint:s,children:r}){return i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:t}),r,s&&i.jsx("small",{children:s})]})}function F1(t,s){const r=s?String(s):"",o=(t==null?void 0:t.channels)||[];return!r||o.some(c=>String(c.id)===r)?o:[{id:r,name:`Saved channel · ${r}`},...o]}function Oa({icon:t,label:s,title:r,text:o,className:c}){return i.jsxs("div",{className:`settings-intro${c?` ${c}`:""}`,children:[i.jsx("span",{className:"settings-intro-icon",children:i.jsx(X,{name:t})}),i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:s}),i.jsx("strong",{children:r}),i.jsx("p",{children:o})]}),i.jsxs("span",{className:"settings-intro-state",children:[i.jsx("span",{className:"status-dot"})," Per server"]})]})}function is({label:t,title:s,detail:r,icon:o}){return i.jsxs("div",{className:"panel-heading settings-section-title",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:t}),i.jsx("h3",{children:s}),r&&i.jsx("p",{children:r})]}),o&&i.jsx("span",{className:"panel-icon",children:i.jsx(X,{name:o})})]})}function za({state:t}){return i.jsxs("div",{className:"setting-footer",children:[t.error?i.jsx("span",{className:"form-error",role:"alert",children:t.error}):i.jsx("span",{role:"status",children:t.message||"Changes apply to this server."}),i.jsx("button",{className:"button button-primary",type:"submit",disabled:t.saving,children:t.saving?"Saving…":"Save changes"})]})}function B1({guildId:t,config:s,csrfToken:r}){var x,b,j;const[o,c]=T.useState({}),[d,h]=T.useState(Ba);T.useEffect(()=>{const k=(s==null?void 0:s.moderation)||{};c({automod:{...k.automod||{}},spam_threshold:k.spam_threshold??6,spam_interval:k.spam_interval??7,max_mentions:k.max_mentions??5,antinuke:{...k.antinuke||{}},antiraid:{...k.antiraid||{}},antiraid_ext:{...k.antiraid_ext||{}}})},[s]);const p=(k,S,N)=>c(O=>({...O,[k]:{...O[k],[S]:N}})),f=k=>{k.preventDefault(),h({saving:!0,message:"",error:""}),Da(t,"automod",o,r).then(S=>{const N=S.config||{};c({automod:{...N.automod||{}},spam_threshold:N.spam_threshold??6,spam_interval:N.spam_interval??7,max_mentions:N.max_mentions??5,antinuke:{...N.antinuke||{}},antiraid:{...N.antiraid||{}},antiraid_ext:{...N.antiraid_ext||{}}}),h({saving:!1,message:"Moderation settings saved to Niko.",error:""})}).catch(S=>h({saving:!1,message:"",error:S instanceof Error?S.message:"Could not save settings."}))},v=[["antispam","Anti-spam","Detect repeated messages"],["antilink","Invite links","Remove Discord invite links"],["badwords","Blocked words","Filter words from the server list"],["massmention","Mass mentions","Limit mention floods"],["antinuke","Anti-nuke","Protect channels and roles"],["antiraid","Join raid protection","React to sudden join waves"],["antiraid_ext","External app protection","Detect user-installed app abuse"]],g=v.filter(([k])=>{var S;return!!((S=o.automod)!=null&&S[k])}).length;return i.jsxs(i.Fragment,{children:[i.jsx(cn,{eyebrow:"Moderation",title:"Keep the room feeling good.",text:"Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration."}),i.jsx(Oa,{icon:"shield",label:"Protection desk",title:`${g} of ${v.length} safeguards active`,text:"Start with the essentials, then tune thresholds below when you know the room’s rhythm."}),i.jsxs("form",{onSubmit:f,className:"settings-stack",children:[i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(is,{label:"Protection rules",title:"AutoMod modules",detail:"Toggle only the responses you want Niko to handle.",icon:"shield"}),i.jsx("div",{className:"setting-list",children:v.map(([k,S,N])=>{var O;return i.jsxs("label",{className:"setting-row",children:[i.jsxs("span",{children:[i.jsx("strong",{children:S}),i.jsx("small",{children:N})]}),i.jsx("input",{type:"checkbox",checked:!!((O=o.automod)!=null&&O[k]),onChange:M=>p("automod",k,M.target.checked)}),i.jsx("i",{"aria-hidden":"true"})]},k)})})]}),i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(is,{label:"Thresholds",title:"Choose when protection steps in",detail:"These limits apply across the server."}),i.jsxs("div",{className:"form-grid",children:[i.jsx(lt,{label:"Spam messages",hint:"Messages inside the spam interval",children:i.jsx("input",{type:"number",min:"1",max:"100",value:o.spam_threshold??6,onChange:k=>c({...o,spam_threshold:k.target.value})})}),i.jsx(lt,{label:"Spam interval (seconds)",children:i.jsx("input",{type:"number",min:"1",max:"3600",value:o.spam_interval??7,onChange:k=>c({...o,spam_interval:k.target.value})})}),i.jsx(lt,{label:"Maximum mentions",children:i.jsx("input",{type:"number",min:"1",max:"100",value:o.max_mentions??5,onChange:k=>c({...o,max_mentions:k.target.value})})}),i.jsx(lt,{label:"Anti-raid joins",hint:"Joins inside the join interval",children:i.jsx("input",{type:"number",min:"1",max:"1000",value:((x=o.antiraid)==null?void 0:x.join_threshold)??10,onChange:k=>p("antiraid","join_threshold",k.target.value)})}),i.jsx(lt,{label:"Anti-raid interval (seconds)",children:i.jsx("input",{type:"number",min:"1",max:"3600",value:((b=o.antiraid)==null?void 0:b.join_interval)??10,onChange:k=>p("antiraid","join_interval",k.target.value)})}),i.jsx(lt,{label:"Anti-raid action",children:i.jsxs("select",{value:((j=o.antiraid)==null?void 0:j.action)??"kick",onChange:k=>p("antiraid","action",k.target.value),children:[i.jsx("option",{value:"kick",children:"Kick"}),i.jsx("option",{value:"ban",children:"Ban"}),i.jsx("option",{value:"softban",children:"Soft-ban"}),i.jsx("option",{value:"slowmode",children:"Slowmode"}),i.jsx("option",{value:"lockdown",children:"Lockdown"})]})})]}),i.jsx(za,{state:d})]})]})]})}function O1({guildId:t,config:s,csrfToken:r}){var j,k;const[o,c]=T.useState({ai_name:"Niko",personality:"cafe",enabled:!0,ai_actions_experiment:!1,better_context_experiment:!1,multimodal_experiment:!1}),[d,h]=T.useState(Ba),[p,f]=T.useState(null),v=S=>S===!0||S==="True",g=S=>c({ai_name:S.ai_name||"Niko",personality:S.personality==="normal"?"normal":"cafe",enabled:S.enabled!=="False"&&S.enabled!==!1,ai_actions_experiment:v(S.ai_actions_experiment),better_context_experiment:v(S.better_context_experiment),multimodal_experiment:v(S.multimodal_experiment)});T.useEffect(()=>g((s==null?void 0:s.ai)||{}),[s]);const x=S=>{S.preventDefault(),h({saving:!0,message:"",error:""}),Da(t,"ai",o,r).then(N=>{g(N.config||{}),h({saving:!1,message:"AI settings saved.",error:""})}).catch(N=>h({saving:!1,message:"",error:N instanceof Error?N.message:"Could not save settings."}))},b=[{key:"better_context_experiment",title:"Better context",hint:"Use the last five channel messages",info:"Adds recent conversation and replied-to message context so responses understand ongoing discussions more naturally. It is useful for follow-ups, but sends more conversation context to the AI provider."},{key:"ai_actions_experiment",title:"AI actions",hint:"Allow confirmed actions requested in chat",info:"Lets the AI propose polls and server actions such as moderation or channel management. Every action requires confirmation and is still limited by Discord permissions."},{key:"multimodal_experiment",title:"Multimodal conversation",hint:"Understand images and transcribe voice messages",info:"Allows Niko to inspect image attachments and use voice-message transcriptions as context. Media is processed only while enabled and provider usage costs may apply."}];return i.jsxs(i.Fragment,{children:[i.jsx(cn,{eyebrow:"AI controls",title:"Give your AI the right tone.",text:"Configure the AI identity, personality, and opt-in experiments for this server."}),i.jsx(Oa,{icon:"settings",label:"Conversation desk",title:o.enabled?`${o.ai_name} is ready to respond`:`${o.ai_name} is staying quiet`,text:"All settings apply only to this server."}),i.jsxs("form",{onSubmit:x,className:"settings-stack",children:[i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(is,{label:"Conversation",title:"Core settings",detail:"Decide when the AI joins the conversation.",icon:"settings"}),i.jsx("div",{className:"form-grid",children:i.jsx(lt,{label:"AI name",hint:"1–32 characters; this is also the mention trigger",children:i.jsx("input",{value:o.ai_name,maxLength:32,onChange:S=>c({...o,ai_name:S.target.value})})})}),i.jsxs("label",{className:"setting-row",children:[i.jsxs("span",{children:[i.jsx("strong",{children:"Enable AI chat"}),i.jsx("small",{children:"Respond when the configured name is mentioned"})]}),i.jsx("input",{type:"checkbox",checked:o.enabled,onChange:S=>c({...o,enabled:S.target.checked})}),i.jsx("i",{"aria-hidden":"true"})]}),i.jsxs("div",{className:"personality-options",children:[i.jsxs("button",{type:"button",className:o.personality==="cafe"?"personality active":"personality",onClick:()=>c({...o,personality:"cafe"}),children:[i.jsx("span",{className:"personality-mark",children:"n"}),i.jsxs("span",{children:[i.jsx("strong",{children:"Café"}),i.jsx("small",{children:"Warm, playful, familiar"})]})]}),i.jsxs("button",{type:"button",className:o.personality==="normal"?"personality active":"personality",onClick:()=>c({...o,personality:"normal"}),children:[i.jsx("span",{className:"personality-mark",children:"—"}),i.jsxs("span",{children:[i.jsx("strong",{children:"Normal"}),i.jsx("small",{children:"Clear and straightforward"})]})]})]})]}),i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(is,{label:"Experiments",title:"Optional capabilities",detail:"Each experiment includes a learn-more explanation before you enable it."}),b.map(S=>i.jsxs("div",{className:"setting-row experiment-row",children:[i.jsxs("span",{children:[i.jsx("strong",{children:S.title}),i.jsx("small",{children:S.hint})]}),i.jsxs("div",{className:"experiment-actions",children:[i.jsx("button",{type:"button",className:"button button-secondary",onClick:()=>f(S.key),children:"Learn more"}),i.jsxs("label",{className:"toggle-control","aria-label":`Enable ${S.title}`,children:[i.jsx("input",{type:"checkbox",checked:o[S.key],onChange:N=>c({...o,[S.key]:N.target.checked})}),i.jsx("i",{"aria-hidden":"true"})]})]})]},S.key)),i.jsx(za,{state:d})]})]}),p&&i.jsx("div",{className:"modal-backdrop",role:"presentation",onClick:()=>f(null),children:i.jsxs("div",{className:"modal-card",role:"dialog","aria-modal":"true","aria-labelledby":"ai-experiment-title",onClick:S=>S.stopPropagation(),children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"AI experiment"}),i.jsx("h3",{id:"ai-experiment-title",children:(j=b.find(S=>S.key===p))==null?void 0:j.title})]}),i.jsx("button",{type:"button",className:"button button-secondary",onClick:()=>f(null),children:"Close"})]}),i.jsx("p",{children:(k=b.find(S=>S.key===p))==null?void 0:k.info})]})})]})}function z1({guildId:t,config:s,resources:r,csrfToken:o}){const c=(s==null?void 0:s.leveling)||{},[d,h]=T.useState({xp_enabled:!0,xp_multiplier:1,xp_cooldown:0,level_up_channel:"",level_up_message:""}),[p,f]=T.useState(Ba);T.useEffect(()=>h({xp_enabled:c.xp_enabled!==!1,xp_multiplier:c.xp_multiplier??1,xp_cooldown:c.xp_cooldown??0,level_up_channel:c.level_up_channel?String(c.level_up_channel):"",level_up_message:c.level_up_message||""}),[s]);const v=x=>{x.preventDefault(),f({saving:!0,message:"",error:""}),Da(t,"leveling",d,o).then(b=>{const j=b.config||{};h({xp_enabled:j.xp_enabled!==!1,xp_multiplier:j.xp_multiplier??1,xp_cooldown:j.xp_cooldown??0,level_up_channel:j.level_up_channel?String(j.level_up_channel):"",level_up_message:j.level_up_message||""}),f({saving:!1,message:"Leveling settings saved to Niko.",error:""})}).catch(b=>f({saving:!1,message:"",error:b instanceof Error?b.message:"Could not save settings."}))},g=F1(r,d.level_up_channel);return i.jsxs(i.Fragment,{children:[i.jsx(Oa,{className:"leveling-settings-intro",icon:"spark",label:"Participation desk",title:d.xp_enabled?"XP is flowing":"XP is paused",text:"Set a pace that rewards regulars without turning every message into a transaction."}),i.jsx("form",{onSubmit:v,className:"settings-stack",children:i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(is,{label:"Leveling settings",title:"Shape the pace",detail:"These controls apply to every member in this server.",icon:"spark"}),i.jsxs("label",{className:"setting-row",children:[i.jsxs("span",{children:[i.jsx("strong",{children:"Enable XP"}),i.jsx("small",{children:"Track activity and award levels"})]}),i.jsx("input",{type:"checkbox",checked:d.xp_enabled,onChange:x=>h({...d,xp_enabled:x.target.checked})}),i.jsx("i",{"aria-hidden":"true"})]}),i.jsxs("div",{className:"form-grid",children:[i.jsx(lt,{label:"XP multiplier",hint:"From 0.1× to 10×",children:i.jsx("input",{type:"number",min:"0.1",max:"10",step:"0.1",value:d.xp_multiplier,onChange:x=>h({...d,xp_multiplier:x.target.value})})}),i.jsx(lt,{label:"Cooldown (seconds)",hint:"0 disables the cooldown",children:i.jsx("input",{type:"number",min:"0",max:"86400",value:d.xp_cooldown,onChange:x=>h({...d,xp_cooldown:x.target.value})})}),i.jsx(lt,{label:"Level-up channel",children:i.jsxs("select",{value:d.level_up_channel,onChange:x=>h({...d,level_up_channel:x.target.value}),children:[i.jsx("option",{value:"",children:"Same channel"}),g.map(x=>i.jsxs("option",{value:x.id,children:["#",x.name]},x.id))]})}),i.jsx(lt,{label:"Level-up message",hint:"Use {mention}, {level}, {name}, or {guild}",children:i.jsx("textarea",{rows:3,maxLength:1e3,value:d.level_up_message,onChange:x=>h({...d,level_up_message:x.target.value}),placeholder:"Leave blank for Niko's default message"})})]}),i.jsx(za,{state:p})]})})]})}function U1({guildId:t,config:s,csrfToken:r}){var v;const o=((v=s==null?void 0:s.server)==null?void 0:v.profile)||{},[c,d]=T.useState({display_name:o.display_name||"",bio:o.bio||"",avatar_url:o.avatar_url||"",banner_url:o.banner_url||""}),[h,p]=T.useState(Ba);T.useEffect(()=>{var x;const g=((x=s==null?void 0:s.server)==null?void 0:x.profile)||{};d({display_name:g.display_name||"",bio:g.bio||"",avatar_url:g.avatar_url||"",banner_url:g.banner_url||""})},[s]);const f=g=>{g.preventDefault(),p({saving:!0,message:"",error:""}),Gx(t,{display_name:c.display_name||null,bio:c.bio||null,avatar_url:c.avatar_url||null,banner_url:c.banner_url||null},r).then(x=>{const b=x.profile||{};d({display_name:b.display_name||"",bio:b.bio||"",avatar_url:b.avatar_url||"",banner_url:b.banner_url||""}),p({saving:!1,message:"Bot profile updated.",error:""})}).catch(x=>p({saving:!1,message:"",error:x instanceof Error?x.message:"Could not save profile."}))};return i.jsxs(i.Fragment,{children:[i.jsx(cn,{eyebrow:"Customization",title:"Niko's server presence.",text:"Change how Niko appears in this server. Display name, avatar, banner, and bio are all per-server."}),i.jsx(Oa,{icon:"paint",label:"Identity desk",title:"Server-specific identity",text:"Each server can have its own Niko persona. Changes apply only to this server."}),i.jsxs("form",{onSubmit:f,className:"settings-stack",children:[i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(is,{label:"Display name",title:"How Niko appears",detail:"Set the name members see for Niko in this server. Leave blank to use the default.",icon:"settings"}),i.jsxs("div",{className:"form-grid",children:[i.jsx(lt,{label:"Display name",hint:"32 characters or fewer",children:i.jsx("input",{value:c.display_name,maxLength:32,onChange:g=>d({...c,display_name:g.target.value}),placeholder:"Niko"})}),i.jsx(lt,{label:"Bio",hint:"190 characters or fewer",children:i.jsx("input",{value:c.bio,maxLength:190,onChange:g=>d({...c,bio:g.target.value}),placeholder:"A warm Discord companion"})})]})]}),i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(is,{label:"Server avatar & banner",title:"Visual identity",detail:"Provide HTTPS image URLs. Images are uploaded to Discord when saved.",icon:"paint"}),i.jsxs("div",{className:"form-grid",children:[i.jsx(lt,{label:"Avatar URL",hint:"Square image, 512×512 recommended",children:i.jsx("input",{type:"url",value:c.avatar_url,onChange:g=>d({...c,avatar_url:g.target.value}),placeholder:"https://cdn.example.com/avatar.png"})}),i.jsx(lt,{label:"Banner URL",hint:"Wide image, 960×540 recommended",children:i.jsx("input",{type:"url",value:c.banner_url,onChange:g=>d({...c,banner_url:g.target.value}),placeholder:"https://cdn.example.com/banner.png"})})]}),i.jsx("p",{className:"form-hint",children:"Images are fetched, validated, and uploaded to Discord. Maximum 8 MB each. Supported formats: PNG, JPG, GIF."})]}),i.jsx(za,{state:h})]})]})}const W1={saving:!1,message:"",error:""};function gt({label:t,hint:s,children:r}){return i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:t}),r,s&&i.jsx("small",{children:s})]})}function sa({label:t,title:s,detail:r,icon:o}){return i.jsxs("div",{className:"panel-heading settings-section-title",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:t}),i.jsx("h3",{children:s}),i.jsx("p",{children:r})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(X,{name:o})})]})}function $1({state:t}){return i.jsxs("div",{className:"setting-footer",children:[t.error?i.jsx("span",{className:"form-error",role:"alert",children:t.error}):i.jsx("span",{role:"status",children:t.message||"Changes apply to this server."}),i.jsx("button",{className:"button button-primary",type:"submit",disabled:t.saving,children:t.saving?"Saving...":"Save server settings"})]})}const H1=[["moderation","Moderation"],["automod","AutoMod"],["messages","Messages"],["channels","Channels"],["members","Members"],["captcha","Captcha"],["invites","Invites"],["roles","Roles"],["server","Server"],["voice","Voice"]];function G1(t,s){var r;return s?((r=t==null?void 0:t.channels.find(o=>String(o.id)===String(s)))==null?void 0:r.name)||`Saved channel · ${s}`:"Not set"}function Jp(t){const s=t.replace(/^#/,"");return/^[0-9a-fA-F]{6}$/.test(s)?`#${s}`:"#5865F2"}function ia(t,s){const r=s?String(s):"",o=(t==null?void 0:t.channels)||[];return!r||o.some(c=>String(c.id)===r)?o:[{id:r,name:`Saved channel · ${r}`},...o]}function Zp(t,s=[]){const r=(t==null?void 0:t.roles)||[],o=new Set(r.map(d=>String(d.id)));return[...s.map(String).filter((d,h,p)=>d&&!o.has(d)&&p.indexOf(d)===h).map(d=>({id:d,name:`Unavailable role (${d})`})),...r]}function oc(t){var o,c;const s=(t==null?void 0:t.onboarding)||{},r=(t==null?void 0:t.tickets)||{};return{prefixes:((o=t==null?void 0:t.prefixes)!=null&&o.length?t.prefixes:["."]).join(`
`),welcome_channel:s.welcome_channel?String(s.welcome_channel):"",welcome_title:s.welcome_title||"",welcome_description:s.welcome_description||"",welcome_color:s.welcome_color===null||s.welcome_color===void 0?"5865F2":s.welcome_color.toString(16).padStart(6,"0"),welcome_image:s.welcome_image||"",rules_channel:s.rules_channel?String(s.rules_channel):"",rules_text:s.rules_text||"",rules_role_id:s.rules_role_id?String(s.rules_role_id):"",logging:Object.fromEntries(Object.entries((t==null?void 0:t.logging)||{}).map(([d,h])=>[d,h==null?"":String(h)])),disabled_logging:[...((c=t==null?void 0:t.logging)==null?void 0:c.disabled)||[]].map(String),panel_title:r.panel_title||"",panel_description:r.panel_description||"",panel_categories:(r.panel_categories||[]).join(`
`),panel_channel_id:r.panel_channel_id?String(r.panel_channel_id):"",support_roles:[...r.support_roles||[]].map(String)}}function K1({guildId:t,config:s,resources:r,csrfToken:o}){const[c,d]=T.useState(()=>oc(s==null?void 0:s.server)),[h,p]=T.useState(W1),[f,v]=T.useState(!1);T.useEffect(()=>{s!=null&&s.server&&d(oc(s.server))},[s]);const g=(D,B)=>d(V=>({...V,[D]:B})),x=D=>g("welcome_color",D.replace(/^#/,"").replace(/[^0-9a-fA-F]/g,"").slice(0,6)),b=(D,B)=>d(V=>({...V,logging:{...V.logging,[D]:B}})),j=D=>d(B=>({...B,disabled_logging:B.disabled_logging.includes(D)?B.disabled_logging.filter(V=>V!==D):[...B.disabled_logging,D]})),k=D=>{D.preventDefault(),p({saving:!0,message:"",error:""});const B=c.prefixes.split(/\r?\n|,/).map(z=>z.trim()).filter(Boolean),V=c.panel_categories.split(/\r?\n|,/).map(z=>z.trim()).filter(Boolean);Da(t,"server",{prefixes:B,onboarding:{welcome_channel:c.welcome_channel,welcome_title:c.welcome_title,welcome_description:c.welcome_description,welcome_color:c.welcome_color,welcome_image:c.welcome_image,rules_channel:c.rules_channel,rules_text:c.rules_text,rules_role_id:c.rules_role_id},logging:{...c.logging,disabled:c.disabled_logging},tickets:{panel_title:c.panel_title,panel_description:c.panel_description,panel_categories:V,panel_channel_id:c.panel_channel_id,support_roles:c.support_roles}},o).then(z=>{d(oc(z.config)),p({saving:!1,message:"Server settings saved to Niko.",error:""})}).catch(z=>p({saving:!1,message:"",error:z instanceof Error?z.message:"Could not save server settings."}))},S=c.welcome_channel,N=c.panel_channel_id,O=ia(r,c.welcome_channel),M=ia(r,c.rules_channel),L=ia(r,c.panel_channel_id),I=Zp(r,c.support_roles);return i.jsxs(i.Fragment,{children:[i.jsx(cn,{eyebrow:"Server settings",title:"Make Niko fit your room.",text:"Manage the settings that shape how Niko behaves in this server. Economy balances remain global to each user and are not configured here."}),i.jsxs("div",{className:"settings-intro",children:[i.jsx("span",{className:"settings-intro-icon",children:i.jsx(X,{name:"settings"})}),i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Server control room"}),i.jsxs("strong",{children:[c.prefixes.split(/\r?\n|,/).filter(Boolean).length||0," command prefixes configured"]}),i.jsx("p",{children:"Welcome flows, log destinations, and ticket panels all live here."})]}),i.jsxs("span",{className:"settings-intro-state",children:[i.jsx("span",{className:"status-dot"})," Per server"]})]}),i.jsxs("form",{onSubmit:k,className:"settings-stack server-settings-stack",children:[i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(sa,{label:"Commands",title:"Prefixes",detail:"Use one prefix per line. Niko will respond to all of them.",icon:"terminal"}),i.jsx(gt,{label:"Command prefixes",hint:"The default prefix is .",children:i.jsx("textarea",{rows:3,maxLength:200,value:c.prefixes,onChange:D=>g("prefixes",D.target.value),placeholder:".\\n!"})})]}),i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(sa,{label:"Welcome flow",title:"Welcome and rules",detail:"Choose where new members see your welcome message and rules.",icon:"users"}),i.jsxs("div",{className:"form-grid",children:[i.jsx(gt,{label:"Welcome channel",children:i.jsxs("select",{value:S,onChange:D=>g("welcome_channel",D.target.value),children:[i.jsx("option",{value:"",children:"Disabled"}),O.map(D=>i.jsxs("option",{value:D.id,children:["#",D.name]},D.id))]})}),i.jsx(gt,{label:"Welcome title",children:i.jsx("input",{value:c.welcome_title,maxLength:200,onChange:D=>g("welcome_title",D.target.value),placeholder:"Welcome to the server"})}),i.jsx(gt,{label:"Welcome message",hint:"Supports {user} and {name}",children:i.jsx("textarea",{rows:4,maxLength:2e3,value:c.welcome_description,onChange:D=>g("welcome_description",D.target.value),placeholder:"Welcome {user}!"})}),i.jsx(gt,{label:"Accent color",hint:"Hex color, for example 5865F2",children:i.jsxs("div",{className:"color-picker",children:[i.jsxs("div",{className:"color-field-control",children:[i.jsx("button",{type:"button",className:"color-preview",style:{backgroundColor:Jp(c.welcome_color)},onClick:()=>v(D=>!D),"aria-label":"Choose welcome accent color","aria-expanded":f}),i.jsx("input",{value:c.welcome_color,maxLength:6,onChange:D=>x(D.target.value),placeholder:"5865F2"})]}),f&&i.jsxs("div",{className:"color-picker-popover",role:"dialog","aria-label":"Choose accent color",children:[i.jsxs("div",{className:"color-picker-header",children:[i.jsx("strong",{children:"Choose color"}),i.jsx("button",{type:"button",className:"color-picker-close",onClick:()=>v(!1),"aria-label":"Close color picker",children:"×"})]}),i.jsx("input",{className:"color-picker-native",type:"color",value:Jp(c.welcome_color),onChange:D=>x(D.target.value)}),i.jsxs("div",{className:"color-picker-value",children:[i.jsx("span",{children:"#"}),i.jsx("input",{value:c.welcome_color.replace(/^#/,""),maxLength:6,onChange:D=>x(D.target.value),placeholder:"5865F2"})]})]})]})}),i.jsx(gt,{label:"Welcome image URL",children:i.jsx("input",{type:"url",value:c.welcome_image,onChange:D=>g("welcome_image",D.target.value),placeholder:"https://..."})}),i.jsx(gt,{label:"Rules channel",children:i.jsxs("select",{value:c.rules_channel,onChange:D=>g("rules_channel",D.target.value),children:[i.jsx("option",{value:"",children:"Not configured"}),M.map(D=>i.jsxs("option",{value:D.id,children:["#",D.name]},D.id))]})}),i.jsx(gt,{label:"Rules text",children:i.jsx("textarea",{rows:4,maxLength:2e3,value:c.rules_text,onChange:D=>g("rules_text",D.target.value),placeholder:"Write the rules members should acknowledge."})}),i.jsx(gt,{label:"Role after rules acknowledgment",children:i.jsxs("select",{value:c.rules_role_id,onChange:D=>g("rules_role_id",D.target.value),children:[i.jsx("option",{value:"",children:"No role"}),Zp(r,c.rules_role_id?[c.rules_role_id]:[]).map(D=>i.jsxs("option",{value:D.id,children:["@",D.name]},D.id))]})})]})]}),i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(sa,{label:"Audit trail",title:"Logging destinations",detail:"Pick a channel for each event type and disable categories you do not need.",icon:"book"}),i.jsx("div",{className:"server-logging-list",children:H1.map(([D,B])=>{const V=ia(r,c.logging[D]);return i.jsxs("div",{className:"server-logging-row",children:[i.jsxs("label",{className:"form-field",children:[i.jsxs("span",{className:"form-label",children:[B," logs"]}),i.jsxs("select",{value:String(c.logging[D]||""),onChange:z=>b(D,z.target.value),children:[i.jsx("option",{value:"",children:"Not set"}),V.map(z=>i.jsxs("option",{value:z.id,children:["#",z.name]},z.id))]})]}),i.jsxs("label",{className:"setting-row compact-setting-row",children:[i.jsxs("span",{children:[i.jsx("strong",{children:"Enabled"}),i.jsx("small",{children:G1(r,c.logging[D])})]}),i.jsx("input",{type:"checkbox",checked:!c.disabled_logging.includes(D),onChange:()=>j(D)}),i.jsx("i",{"aria-hidden":"true"})]})]},D)})})]}),i.jsxs("section",{className:"dash-panel settings-panel",children:[i.jsx(sa,{label:"Support desk",title:"Ticket panel",detail:"Configure the public panel and decide who can handle tickets.",icon:"users"}),i.jsxs("div",{className:"form-grid",children:[i.jsx(gt,{label:"Panel title",children:i.jsx("input",{value:c.panel_title,maxLength:200,onChange:D=>g("panel_title",D.target.value),placeholder:"Open a Ticket"})}),i.jsx(gt,{label:"Panel channel",children:i.jsxs("select",{value:N,onChange:D=>g("panel_channel_id",D.target.value),children:[i.jsx("option",{value:"",children:"Keep current panel channel"}),L.map(D=>i.jsxs("option",{value:D.id,children:["#",D.name]},D.id))]})}),i.jsx(gt,{label:"Panel description",children:i.jsx("textarea",{rows:4,maxLength:2e3,value:c.panel_description,onChange:D=>g("panel_description",D.target.value),placeholder:"Tell members what the ticket panel is for."})}),i.jsx(gt,{label:"Ticket categories",hint:"One category per line",children:i.jsx("textarea",{rows:4,value:c.panel_categories,onChange:D=>g("panel_categories",D.target.value),placeholder:"General\\nSupport\\nReports"})}),i.jsx(gt,{label:"Support roles",hint:"Hold Ctrl/Cmd to select more than one",children:i.jsx("select",{multiple:!0,value:c.support_roles,onChange:D=>g("support_roles",Array.from(D.target.selectedOptions,B=>B.value)),children:I.map(D=>i.jsxs("option",{value:D.id,children:["@",D.name]},D.id))})})]}),i.jsx("p",{className:"form-hint",children:"Saving panel settings updates the existing posted panel when Niko can find its saved message."})]}),i.jsx($1,{state:h})]})]})}const lc=()=>({id:crypto.randomUUID(),prompt:"",required:!0});function q1({guildId:t,resources:s,csrfToken:r}){const[o,c]=T.useState([]),[d,h]=T.useState(""),[p,f]=T.useState(""),[v,g]=T.useState(""),[x,b]=T.useState([]),[j,k]=T.useState([lc()]),[S,N]=T.useState(!0),[O,M]=T.useState(!1),[L,I]=T.useState(""),[D,B]=T.useState(""),[V,z]=T.useState(null),[re,Y]=T.useState([]),[ce,ue]=T.useState(""),ie=T.useCallback(()=>Bx(t).then(c),[t]);T.useEffect(()=>{N(!0),ie().catch(E=>I(E instanceof Error?E.message:"Applications could not be loaded.")).finally(()=>N(!1))},[ie]);const Se=E=>{E.preventDefault(),M(!0),I(""),B(""),Ox(t,{title:d,description:p,role_id:v,eligible_role_ids:x,questions:j.map(({id:H,prompt:W,required:P})=>({id:H,prompt:W,required:P}))},r).then(({application:H})=>{c(W=>[H,...W]),h(""),f(""),g(""),b([]),k([lc()]),B("Application created. Its link is ready to share.")}).catch(H=>I(H instanceof Error?H.message:"Application could not be created.")).finally(()=>M(!1))},De=E=>{const H=E.status==="open"?"closed":"open";zx(t,E.id,H,r).then(()=>{c(W=>W.map(P=>P.id===E.id?{...P,status:H}:P)),B(H==="open"?"Opening reopened. The same link is active again.":"Opening closed. Its link and responses are preserved."),I("")}).catch(W=>I(W instanceof Error?W.message:"Application status could not be changed."))},Pe=E=>{if(V===E.id){z(null);return}z(E.id),Y([]),Ux(t,E.id).then(H=>Y(H.submissions)).catch(H=>I(H instanceof Error?H.message:"Responses could not be loaded."))},Q=async E=>{const H=`${window.location.origin}/apply/${t}/${E.id}`;try{await navigator.clipboard.writeText(H),ue(E.id),window.setTimeout(()=>ue(""),1800)}catch{I("Could not copy the link. Open it in a new tab and copy the address instead.")}};return i.jsxs(i.Fragment,{children:[i.jsx(cn,{eyebrow:"People · applications",title:"Build your next team.",text:"Keep separate role openings active at once. Close an opening when hiring pauses, then reopen the same link next time—past responses and one-time submissions stay attached."}),i.jsxs("div",{className:"applications-intro",children:[i.jsx("span",{className:"applications-intro-icon",children:i.jsx(X,{name:"users"})}),i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Hiring desk"}),i.jsxs("strong",{children:[o.filter(E=>E.status==="open").length," open · ",o.length," saved openings"]}),i.jsx("p",{children:"Each opening has its own stable public link and response archive."})]}),i.jsxs("a",{href:`/apply/${t}`,target:"_blank",rel:"noreferrer",className:"button button-muted button-small",children:["Preview server link ",i.jsx(X,{name:"arrow"})]})]}),L&&i.jsx("div",{className:"notice warning",role:"alert",children:L}),D&&i.jsx("div",{className:"notice applications-success",role:"status",children:D}),i.jsxs("section",{className:"applications-layout",children:[i.jsxs("form",{className:"dash-panel applications-editor",onSubmit:Se,children:[i.jsxs("div",{className:"panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"New opening"}),i.jsx("h3",{children:"Create a role application"}),i.jsx("p",{children:"One saved opening per role and hiring round. Reopen it later to reuse its URL."})]}),i.jsx("span",{className:"panel-icon",children:i.jsx(X,{name:"plus"})})]}),i.jsxs("div",{className:"form-grid applications-fields",children:[i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Opening title"}),i.jsx("input",{required:!0,maxLength:100,value:d,onChange:E=>h(E.target.value),placeholder:"Community moderator"})]}),i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Discord role"}),i.jsxs("select",{required:!0,value:v,onChange:E=>g(E.target.value),children:[i.jsx("option",{value:"",children:"Choose the role you’re hiring for"}),((s==null?void 0:s.roles)||[]).map(E=>i.jsxs("option",{value:E.id,children:["@",E.name]},E.id))]})]}),i.jsxs("label",{className:"form-field application-description",children:[i.jsx("span",{className:"form-label",children:"About this opening"}),i.jsx("textarea",{rows:3,maxLength:2e3,value:p,onChange:E=>f(E.target.value),placeholder:"Share what the role involves and who you’re looking for."})]}),i.jsxs("label",{className:"form-field application-role-gates",children:[i.jsx("span",{className:"form-label",children:"Eligibility role gates"}),i.jsx("select",{multiple:!0,value:x,onChange:E=>b(Array.from(E.target.selectedOptions,H=>H.value)),children:((s==null?void 0:s.roles)||[]).map(E=>i.jsxs("option",{value:E.id,children:["@",E.name]},E.id))}),i.jsx("small",{children:"Applicants need at least one selected role. Leave empty to allow any server member."})]})]}),i.jsxs("div",{className:"application-question-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"form-label",children:"Application questions"}),i.jsx("small",{children:"Ask up to 12 questions. Required answers must be completed."})]}),i.jsx("button",{type:"button",className:"button button-muted button-small",onClick:()=>k(E=>E.length<12?[...E,lc()]:E),disabled:j.length>=12,children:"＋ Add question"})]}),i.jsx("div",{className:"application-question-list",children:j.map((E,H)=>i.jsxs("div",{className:"application-question",children:[i.jsxs("label",{className:"form-field",children:[i.jsxs("span",{className:"form-label",children:["Question ",H+1]}),i.jsx("input",{required:!0,maxLength:240,value:E.prompt,onChange:W=>k(P=>P.map(U=>U.id===E.id?{...U,prompt:W.target.value}:U)),placeholder:"Why would you be a good fit?"})]}),i.jsxs("label",{className:"application-required",children:[i.jsx("input",{type:"checkbox",checked:E.required,onChange:W=>k(P=>P.map(U=>U.id===E.id?{...U,required:W.target.checked}:U))})," Required"]}),j.length>1&&i.jsx("button",{type:"button",className:"application-remove-question",onClick:()=>k(W=>W.filter(P=>P.id!==E.id)),"aria-label":`Remove question ${H+1}`,children:"×"})]},E.id))}),i.jsxs("div",{className:"setting-footer",children:[i.jsx("span",{children:"Your public application link requires Discord sign-in and server membership."}),i.jsx("button",{className:"button button-primary",type:"submit",disabled:O||!(s!=null&&s.roles.length),children:O?"Creating…":"Create opening"})]})]}),i.jsxs("aside",{className:"applications-aside dash-panel",children:[i.jsx("span",{className:"panel-kicker",children:"Applicant checks"}),i.jsx("h3",{children:"Fair, verified submissions."}),i.jsx("p",{children:"Niko confirms membership directly with Discord before showing or submitting a form. Selected role gates are checked against the applicant’s current server roles."}),i.jsxs("div",{className:"applications-check",children:[i.jsx("span",{children:"01"}),i.jsxs("div",{children:[i.jsx("strong",{children:"Discord identity"}),i.jsx("small",{children:"One verified account per response"})]})]}),i.jsxs("div",{className:"applications-check",children:[i.jsx("span",{children:"02"}),i.jsxs("div",{children:[i.jsx("strong",{children:"Server membership"}),i.jsx("small",{children:"Bot-verified at form load and submit"})]})]}),i.jsxs("div",{className:"applications-check",children:[i.jsx("span",{children:"03"}),i.jsxs("div",{children:[i.jsx("strong",{children:"One application per opening"}),i.jsx("small",{children:"Reopening never clears old submissions"})]})]})]})]}),i.jsxs("section",{className:"applications-list-section",children:[i.jsxs("div",{className:"section-heading-row",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Opening library"}),i.jsx("h3",{children:"Applications & responses"})]}),i.jsxs("span",{className:"section-count",children:[o.length," total"]})]}),S?i.jsx("div",{className:"empty-state",children:"Loading saved applications…"}):o.length===0?i.jsx("div",{className:"empty-state",children:"No applications yet. Create your first role opening above."}):i.jsx("div",{className:"applications-list",children:o.map(E=>{var H;return i.jsxs("article",{className:"application-card dash-panel",children:[i.jsxs("div",{className:"application-card-main",children:[i.jsx("div",{className:`application-status ${E.status}`,children:E.status==="open"?"Open":"Closed"}),i.jsx("h4",{children:E.title}),i.jsx("p",{children:E.description||"A role application for this server."}),i.jsxs("div",{className:"application-meta",children:[i.jsx("span",{children:((H=s==null?void 0:s.roles.find(W=>W.id===E.role_id))==null?void 0:H.name)||`Role ${E.role_id}`}),i.jsxs("span",{children:[E.submission_count," ",E.submission_count===1?"response":"responses"]}),i.jsx("span",{children:E.eligible_role_ids.length?`${E.eligible_role_ids.length} eligibility role${E.eligible_role_ids.length===1?"":"s"}`:"Open to all members"})]})]}),i.jsxs("div",{className:"application-card-actions",children:[i.jsxs("button",{className:"button button-muted button-small",onClick:()=>void Q(E),children:[i.jsx(X,{name:"link"})," ",ce===E.id?"Copied":"Copy link"]}),i.jsxs("button",{className:"button button-muted button-small",onClick:()=>Pe(E),children:[i.jsx(X,{name:"book"})," ",V===E.id?"Hide responses":"Responses"]}),i.jsx("button",{className:`button button-small ${E.status==="open"?"button-muted":"button-primary"}`,onClick:()=>De(E),children:E.status==="open"?"Close opening":"Reopen"})]}),V===E.id&&i.jsx("div",{className:"application-response-list",children:re.length===0?i.jsx("div",{className:"empty-state compact",children:"No responses yet, or loading…"}):re.map(W=>i.jsxs("details",{className:"application-response",children:[i.jsxs("summary",{children:[i.jsxs("span",{className:"application-response-identity",children:[W.avatar_url&&i.jsx("img",{src:W.avatar_url,alt:""}),i.jsx("strong",{children:W.display_name})]}),i.jsx("time",{children:W.submitted_at?new Date(`${W.submitted_at}Z`).toLocaleString():"Submitted"})]}),i.jsx("div",{className:"application-answers",children:W.answers.map(P=>i.jsxs("div",{children:[i.jsx("strong",{children:P.prompt}),i.jsx("p",{children:P.answer||"No answer provided."})]},P.question_id))})]},W.user_id))})]},E.id)})})]})]})}function X1({auth:t}){const s=_n();return i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"dashboard"}),i.jsx("main",{className:"auth-page",children:i.jsxs("div",{className:"auth-card",children:[i.jsx("span",{className:"auth-mark",children:"n"}),i.jsx("div",{className:"eyebrow",children:"Private workspace"}),i.jsxs("h1",{children:["Settle in, ",i.jsx("em",{children:"admin."})]}),i.jsx("p",{children:"Sign in with Discord to see your Niko profile and manage the servers you look after."}),t.oauth_available?i.jsxs("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard",children:[i.jsx(X,{name:"lock"})," Continue with Discord ",i.jsx(X,{name:"arrow"})]}):i.jsxs("div",{className:"notice warning",children:["Discord login is not configured yet. Add ",i.jsx("code",{children:"DISCORD_CLIENT_SECRET"})," to the environment and restart the bot."]}),!s&&i.jsx("p",{className:"form-hint",children:"The public bot configuration is still loading."}),i.jsx("a",{className:"back-link",href:"/",onClick:r=>{r.preventDefault(),pe("/")},children:"Return to public site"})]})})]})}function Y1({section:t,guild:s,stats:r,csrfToken:o,refreshToken:c}){const[d,h]=T.useState(null),[p,f]=T.useState([]),[v,g]=T.useState(null),[x,b]=T.useState(null),[j,k]=T.useState(!0),[S,N]=T.useState("");return T.useEffect(()=>{k(!0),N(""),(t==="overview"?Vx(s.id).then(h):t==="leveling"?Promise.all([Fx(s.id),Cm(s.id),zl(s.id)]).then(([M,L,I])=>{f(M),g(L),b(I)}):t==="applications"?zl(s.id).then(b):Promise.all([Cm(s.id),zl(s.id)]).then(([M,L])=>{g(M),b(L)})).catch(M=>N(M instanceof Error?M.message:"This server could not be loaded.")).finally(()=>k(!1))},[s.id,t,c]),j?i.jsxs("div",{className:"section-loading section-skeleton",role:"status","aria-label":`Loading ${t}`,children:[i.jsx("div",{className:"skeleton-title"}),i.jsx("div",{className:"skeleton-copy"}),i.jsxs("div",{className:"skeleton-grid",children:[i.jsx("i",{}),i.jsx("i",{}),i.jsx("i",{})]}),i.jsxs("span",{children:["Loading ",t,"..."]})]}):S?i.jsxs("div",{className:"inline-error",role:"alert",children:[i.jsx("strong",{children:"Couldn’t load this page."}),i.jsx("span",{children:S}),i.jsx("button",{className:"button button-muted",onClick:()=>window.location.reload(),children:"Try again"})]}):t==="overview"&&d?i.jsx(I1,{overview:d}):t==="leveling"?i.jsx(V1,{guildId:s.id,rows:p,config:v,resources:x,csrfToken:o}):t==="moderation"?i.jsx(B1,{guildId:s.id,config:v,csrfToken:o}):t==="server"?i.jsx(K1,{guildId:s.id,config:v,resources:x,csrfToken:o}):t==="applications"?i.jsx(q1,{guildId:s.id,resources:x,csrfToken:o}):t==="customization"?i.jsx(U1,{guildId:s.id,config:v,csrfToken:o}):i.jsx(O1,{guildId:s.id,config:v,csrfToken:o})}function Q1(){return i.jsxs("div",{className:"section-loading section-skeleton dashboard-loading",role:"status",children:[i.jsx("div",{className:"skeleton-title"}),i.jsx("div",{className:"skeleton-copy"}),i.jsxs("div",{className:"skeleton-grid",children:[i.jsx("i",{}),i.jsx("i",{}),i.jsx("i",{})]}),i.jsx("span",{children:"Preparing your dashboard..."})]})}function J1(){_n();const[t,s]=T.useState(Pm),[r,o]=T.useState(null),[c,d]=T.useState(null),[h,p]=T.useState(null),[f,v]=T.useState([]),[g,x]=T.useState(null),[b,j]=T.useState(!0),[k,S]=T.useState(""),[N,O]=T.useState(0),[M,L]=T.useState(!1),[I,D]=T.useState(null);if(T.useEffect(()=>{const ie=()=>s(Pm());return window.addEventListener("popstate",ie),()=>window.removeEventListener("popstate",ie)},[]),T.useEffect(()=>{j(!0),Promise.all([fa(),ga()]).then(([ie,Se])=>(o(ie),d(Se),ie.authenticated?Promise.all([Nm(),hc(),dc().catch(()=>null)]).then(([De,Pe,Q])=>{p(De),v(Pe),D((Q==null?void 0:Q.role)||null)}):null)).catch(ie=>S(ie instanceof Error?ie.message:"Dashboard unavailable")).finally(()=>j(!1))},[]),T.useEffect(()=>{if(t.view!=="guild"){x(null);return}const ie=f.find(Se=>Se.id===t.guildId&&Se.installed!==!1);ie?(x(ie),localStorage.setItem("niko-guild",ie.id)):t.guildId&&f.length&&pe(mc())},[f,t.guildId,t.view]),b||!r)return i.jsxs("div",{className:"dashboard-state",children:[i.jsx("div",{className:"loading-ring"}),i.jsx("p",{children:"Connecting to Niko…"})]});if(k)return i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"dashboard"}),i.jsx("main",{className:"auth-page",children:i.jsxs("div",{className:"auth-card",children:[i.jsx("span",{className:"auth-mark",children:"!"}),i.jsx("div",{className:"eyebrow",children:"Connection issue"}),i.jsxs("h1",{children:["Couldn’t load",i.jsx("br",{}),i.jsx("em",{children:"your workspace."})]}),i.jsx("p",{children:k}),i.jsxs("button",{className:"button button-primary",onClick:()=>window.location.reload(),children:["Try again ",i.jsx(X,{name:"arrow"})]})]})})]});if(!r.authenticated)return i.jsx(X1,{auth:r});const B=ie=>{ie.installed!==!1&&(localStorage.setItem("niko-guild",ie.id),pe(Es(ie.id,t.section)))},V=ie=>{ie.installed!==!1&&(localStorage.setItem("niko-guild",ie.id),pe(Es(ie.id,"overview")))},z=ie=>{pe(g?Es(g.id,ie):Es())},re=()=>pe(Es()),Y=()=>pe(mc()),ce=async()=>{if(!M){L(!0);try{const[ie,Se]=await Promise.all([fa(),ga()]);if(o(ie),d(Se),ie.authenticated){const[De,Pe,Q]=await Promise.all([Nm(),hc(),dc().catch(()=>null)]);p(De),v(Pe),D((Q==null?void 0:Q.role)||null)}O(De=>De+1),S("")}catch(ie){S(ie instanceof Error?ie.message:"Dashboard refresh failed")}finally{L(!1)}}};let ue;return t.view==="servers"?ue=i.jsx(L1,{guilds:f,onManage:V}):t.view==="guild"?ue=g?i.jsx(Y1,{section:t.section,guild:g,stats:c,csrfToken:r.csrf_token,refreshToken:N},`${g.id}-${t.section}`):i.jsx(Q1,{}):ue=i.jsx(R1,{user:r.user,overview:h,guilds:f,onServers:Y,onManage:V}),i.jsx(Mf,{user:r.user,guilds:f,selectedGuild:g,view:t.view,section:t.section,stats:c,onHome:re,onServers:Y,onGuildChange:B,onSectionChange:z,onRefresh:ce,refreshing:M,staffRole:I,children:ue})}function Z1({value:t,onChange:s,placeholder:r="Search documentation...",onFocus:o,onBlur:c}){const[d,h]=T.useState(!1),p=T.useRef(null),[f,v]=T.useState(!1);T.useEffect(()=>{const k=S=>{var N;(S.metaKey||S.ctrlKey)&&S.key==="k"&&(S.preventDefault(),(N=p.current)==null||N.focus())};return document.addEventListener("keydown",k),()=>document.removeEventListener("keydown",k)},[]);const g=()=>{h(!0),v(!0),o==null||o()},x=()=>{h(!1),setTimeout(()=>v(!1),200),c==null||c()},b=k=>{s(k.target.value)},j=k=>{var S;k.key==="Escape"&&((S=p.current)==null||S.blur())};return i.jsxs("div",{className:`doc-search-bar ${f?"expanded":""}`,children:[i.jsxs("div",{className:"search-input-wrapper",children:[i.jsx(X,{name:"search",className:"search-icon"}),i.jsx("input",{ref:p,type:"text",value:t,onChange:b,onFocus:g,onBlur:x,onKeyDown:j,placeholder:r,className:"search-input","aria-label":"Search documentation"}),i.jsxs("kbd",{className:"search-shortcut",children:[i.jsx("span",{className:"shortcut-key",children:"⌘"}),"K"]})]}),i.jsxs("div",{className:"search-hint",children:["Press ",i.jsx("kbd",{children:"⌘K"})," to focus search"]})]})}function eS({selectedCategory:t,onSelectCategory:s,sections:r,allCategoriesLabel:o="All Categories"}){return i.jsx("div",{className:"doc-filters",children:i.jsxs("div",{className:"filter-tabs",role:"tablist","aria-label":"Filter by category",children:[i.jsx("button",{role:"tab","aria-selected":t==="",className:`filter-tab ${t===""?"active":""}`,onClick:()=>s(""),children:o}),r.map(c=>i.jsxs("button",{role:"tab","aria-selected":t===c.id,className:`filter-tab ${t===c.id?"active":""}`,onClick:()=>s(c.id),children:[i.jsx(X,{name:c.icon,size:14}),i.jsx("span",{children:c.label})]},c.id))]})})}function cc({doc:t,variant:s="default"}){const r="page"in t?t.page:t,[o,c]=T.useState(!1),d=f=>{f.preventDefault(),pe(`/docs/${r.slug}`)},h=f=>{(f.key==="Enter"||f.key===" ")&&(f.preventDefault(),pe(`/docs/${r.slug}`))};if(s==="compact")return i.jsx("a",{href:`/docs/${r.slug}`,onClick:d,onKeyDown:h,className:"doc-card-compact",tabIndex:0,role:"button",children:i.jsxs("div",{className:"compact-content",children:[i.jsx("span",{className:"compact-title",children:r.title}),i.jsx("span",{className:"compact-excerpt",children:r.excerpt})]})});const p="highlights"in t?t.highlights:[];return i.jsx("article",{className:`doc-card ${s==="highlighted"?"highlighted":""}`,children:i.jsxs("div",{className:`doc-card-content ${o?"loaded":""}`,children:[i.jsxs("div",{className:"doc-card-header",children:[i.jsx("span",{className:"doc-category",children:r.category.replace(/-/g," ")}),i.jsxs("span",{className:"doc-order",children:["#",r.order]})]}),i.jsx("h3",{className:"doc-title",children:r.title}),i.jsx("p",{className:"doc-excerpt",children:r.excerpt}),p.length>0&&i.jsx("div",{className:"doc-highlights",children:p.slice(0,2).map((f,v)=>i.jsxs("p",{className:"highlight-snippet",children:[f.slice(0,150),f.length>150?"...":""]},v))}),i.jsxs("div",{className:"doc-card-footer",children:[i.jsx("div",{className:"doc-tags",children:r.tags.slice(0,3).map(f=>i.jsxs("span",{className:"doc-tag",children:["#",f]},f))}),i.jsxs("a",{href:`/docs/${r.slug}`,onClick:d,onKeyDown:h,className:"doc-read-more",children:["Read more ",i.jsx(X,{name:"arrow",size:14})]})]})]})})}const We=[{slug:"welcome",title:"Welcome to Niko",category:"getting-started",excerpt:"New to Niko? Start here to understand what the bot can do for your server.",tags:["introduction","overview","beginner"],order:1,content:`
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
    `}];function tS(t){return We.find(s=>s.slug===t)}const En=[{id:"getting-started",label:"Getting Started",description:"New to Niko? Start here.",icon:"icon_home",count:We.filter(t=>t.category==="getting-started").length},{id:"setup",label:"Setup",description:"Configure Niko for your server.",icon:"icon_settings",count:We.filter(t=>t.category==="setup").length},{id:"economy",label:"Economy",description:"Money, jobs, banking, and more.",icon:"icon_economy",count:We.filter(t=>t.category==="economy").length},{id:"leveling",label:"Leveling",description:"XP, levels, and rankings.",icon:"icon_leveling",count:We.filter(t=>t.category==="leveling").length},{id:"moderation",label:"Moderation",description:"Moderation tools and commands.",icon:"icon_moderation",count:We.filter(t=>t.category==="moderation").length},{id:"automod",label:"AutoMod",description:"Automated moderation features.",icon:"icon_automod",count:We.filter(t=>t.category==="automod").length},{id:"logging",label:"Logging",description:"Server event logging.",icon:"icon_settings",count:We.filter(t=>t.category==="logging").length},{id:"social",label:"Social",description:"Community engagement features.",icon:"icon_heart",count:We.filter(t=>t.category==="social").length},{id:"utility",label:"Utility",description:"Helpful tools and utilities.",icon:"icon_utility",count:We.filter(t=>t.category==="utility").length},{id:"voice",label:"Voice",description:"Voice and music features.",icon:"icon_bot",count:We.filter(t=>t.category==="voice").length},{id:"ai",label:"AI",description:"AI-powered features.",icon:"icon_ai",count:We.filter(t=>t.category==="ai").length},{id:"dashboard",label:"Dashboard",description:"Web dashboard guides.",icon:"icon_settings",count:We.filter(t=>t.category==="dashboard").length},{id:"tips",label:"Tips",description:"Tips and best practices.",icon:"icon_lightbulb",count:We.filter(t=>t.category==="tips").length}];function gy(){const[t,s]=T.useState({query:"",category:"",tags:[]}),r=T.useCallback(f=>{s(v=>({...v,query:f.toLowerCase(),tags:[]}))},[]),o=T.useCallback(f=>{s(v=>({...v,category:f,tags:[]}))},[]),c=T.useCallback(f=>{s(v=>{const g=v.tags.includes(f)?v.tags.filter(x=>x!==f):[...v.tags,f];return{...v,tags:g,query:""}})},[]),d=T.useCallback(()=>{s({query:"",category:"",tags:[]})},[]),h=T.useMemo(()=>{const{query:f,category:v,tags:g}=t;if(!f&&!v&&g.length===0)return We.map(b=>({page:b,score:1,highlights:[]}));const x=[];for(const b of We)if(!(v&&b.category!==v)&&!(g.length>0&&!g.some(j=>b.tags.includes(j))))if(f){const j=nS(b,f);if(j===0)continue;const k=sS(b,f);x.push({page:b,score:j,highlights:k})}else x.push({page:b,score:1,highlights:[]});return x.sort((b,j)=>j.score!==b.score?j.score-b.score:b.page.order-j.page.order),x},[t]),p=t.query!==""||t.category!==""||t.tags.length>0;return{filters:t,setQuery:r,setCategory:o,toggleTag:c,clearFilters:d,results:h,hasActiveFilters:p,resultCount:h.length}}function nS(t,s){let r=0;const o=s.toLowerCase();t.title.toLowerCase()===o?r+=100:t.title.toLowerCase().includes(o)&&(r+=50),t.excerpt.toLowerCase().includes(o)&&(r+=25),t.content.toLowerCase().includes(o)&&(r+=10);for(const c of t.tags)c.toLowerCase().includes(o)&&(r+=15);return t.category.toLowerCase().includes(o)&&(r+=5),r}function sS(t,s){const r=[],o=s.toLowerCase(),c=3;if(t.title.toLowerCase().includes(o)&&(r.push(t.title),r.length>=c)||t.excerpt.toLowerCase().includes(o)&&(r.push(t.excerpt),r.length>=c))return r;const d=t.content.split(`
`).filter(h=>h.trim());for(const h of d)if(h.toLowerCase().includes(o)){const p=h.replace(/#{1,6}\s?/g,"").trim();if(p.length>10&&(r.push(p),r.length>=c))break}return r}function iS(){return T.useMemo(()=>{const s={};return We.forEach(r=>{r.tags.forEach(o=>{s[o]=(s[o]||0)+1})}),Object.entries(s).map(([r,o])=>({tag:r,count:o})).sort((r,o)=>o.count-r.count)},[])}function rS({slug:t}){var f,v;const{setCategory:s,clearFilters:r}=gy();T.useEffect(()=>{window.location.hash!==`#/docs/${t}`&&window.history.replaceState(null,"",`#/docs/${t}`)},[t]);const o=tS(t);if(!o)return i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"docs"}),i.jsx("main",{className:"shell page-main docs-page",children:i.jsxs("div",{className:"docs-not-found",children:[i.jsx(X,{name:"doc",size:48,className:"not-found-icon"}),i.jsx("h1",{children:"Page Not Found"}),i.jsxs("p",{children:[`We couldn't find documentation for "`,t,'".']}),i.jsxs("div",{className:"not-found-actions",children:[i.jsx("button",{onClick:()=>pe("/docs"),children:"Browse all documentation"}),i.jsx("button",{onClick:()=>{pe("/docs"),r()},children:"Clear filters"})]})]})}),i.jsx(St,{})]});const c=g=>{const x=[],b=/(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*)/g;let j=0,k,S=0;for(;(k=b.exec(g))!==null;){k.index>j&&x.push(g.slice(j,k.index));const N=k[0];if(N.startsWith("`")&&N.endsWith("`")&&N.length>2)x.push(i.jsx("code",{className:"doc-inline-code",children:N.slice(1,-1)},S++));else if(N.startsWith("[")){const O=N.match(/^\[([^\]]+)\]\(([^)]+)\)$/);O?x.push(i.jsx("a",{href:O[2],target:"_blank",rel:"noreferrer",children:c(O[1])},S++)):x.push(N)}else N.startsWith("**")?x.push(i.jsx("strong",{children:c(N.slice(2,-2))},S++)):N.startsWith("*")?x.push(i.jsx("em",{children:c(N.slice(1,-1))},S++)):x.push(N);j=k.index+N.length}return j<g.length&&x.push(g.slice(j)),x},h=(g=>{const x=g.split(`
`),b=[];let j=0,k=null,S=[];const N=()=>{if(S.length===0)return;const M=k==="ol"?"ol":"ul";b.push(i.jsx(M,{className:`doc-content-list ${k==="ol"?"doc-content-list-ol":""}`,children:S.map((L,I)=>i.jsx("li",{children:c(L)},I))},`list-${b.length}`)),S=[],k=null},O=()=>{var I;const M=b[b.length-1];T.isValidElement(M)&&((I=M.props)==null?void 0:I.className)==="doc-content-spacer"||b.push(i.jsx("div",{className:"doc-content-spacer"},`spacer-${b.length}`))};for(;j<x.length;){const L=x[j].trim();if(!L){N(),O(),j+=1;continue}if(L.startsWith("```")){N();const B=[];let V=j+1;for(;V<x.length&&x[V].trim()!=="```";)B.push(x[V]),V+=1;b.push(i.jsx("pre",{className:"doc-code-block",children:i.jsx("code",{children:B.join(`
`)})},`code-${j}`)),j=V+1;continue}if(L.startsWith("|")){N();const B=[];let V=j;for(;V<x.length&&x[V].trim().startsWith("|");){const ce=x[V].trim().replace(/^\|/,"").replace(/\|$/,"").split("|").map(ue=>ue.trim());B.push(ce),V+=1}const z=B.length>1&&B[1].every(ce=>/^:?-{2,}:?$/.test(ce.replace(/\s+/g,""))),re=B[0],Y=z?B.slice(2):B.slice(1);re.length>1&&b.push(i.jsxs("table",{className:"doc-table",children:[i.jsx("thead",{children:i.jsx("tr",{children:re.map((ce,ue)=>i.jsx("th",{children:c(ce)},ue))})}),i.jsx("tbody",{children:Y.map((ce,ue)=>i.jsx("tr",{children:ce.map((ie,Se)=>i.jsx("td",{children:c(ie)},Se))},ue))})]},`table-${j}`)),j=V;continue}if(L.startsWith("### ")){N(),b.push(i.jsx("h4",{className:"doc-heading doc-heading-h4",children:L.slice(4)},`h-${j}`)),j+=1;continue}if(L.startsWith("## ")){N(),b.push(i.jsx("h3",{className:"doc-heading doc-heading-h3",children:L.slice(3)},`h-${j}`)),j+=1;continue}if(L.startsWith("# ")){N(),b.push(i.jsx("h2",{className:"doc-heading doc-heading-h2",children:L.slice(2)},`h-${j}`)),j+=1;continue}if(L.startsWith("> ")){N(),b.push(i.jsx("blockquote",{className:"doc-blockquote",children:c(L.slice(2))},`q-${j}`)),j+=1;continue}const I=L.match(/^[-*]\s+(.*)$/);if(I){k!=="ul"&&N(),k="ul",S.push(I[1]),j+=1;continue}const D=L.match(/^\d+\.\s+(.*)$/);if(D){k!=="ol"&&N(),k="ol",S.push(D[1]),j+=1;continue}N(),b.push(i.jsx("p",{className:"doc-paragraph",children:c(L)},`p-${j}`)),j+=1}return N(),b})(o.content),p=h.filter(g=>T.isValidElement(g)&&(g.type==="h2"||g.type==="h3"));return i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"docs"}),i.jsxs("main",{className:"shell page-main docs-page docs-detail-page",children:[i.jsx("div",{className:"docs-detail-back",children:i.jsxs("button",{onClick:()=>pe("/docs"),className:"back-button",children:[i.jsx(X,{name:"arrow",size:16}),"Back to Documentation"]})}),i.jsxs("header",{className:"doc-article-header",children:[i.jsxs("div",{className:"doc-article-meta",children:[i.jsx("span",{className:"doc-category-badge",children:((f=En.find(g=>g.id===o.category))==null?void 0:f.label)||o.category}),i.jsxs("span",{className:"doc-order-badge",children:["Article #",o.order]})]}),i.jsx("h1",{className:"doc-article-title",children:o.title}),i.jsx("p",{className:"doc-article-excerpt",children:o.excerpt}),i.jsx("div",{className:"doc-article-tags",children:o.tags.map(g=>i.jsxs("span",{className:"doc-tag-pill",children:["#",g]},g))})]}),i.jsx("article",{className:"doc-article-content",children:h}),i.jsx("footer",{className:"doc-article-footer",children:i.jsx("div",{className:"doc-nav-container",children:i.jsxs("div",{className:"doc-nav-col",children:[i.jsx("span",{className:"doc-nav-label",children:"Category"}),i.jsxs("button",{className:"doc-nav-link",onClick:()=>{s(o.category),pe("/docs")},children:[i.jsx(X,{name:"arrow",size:14}),"View all ",(v=En.find(g=>g.id===o.category))==null?void 0:v.label]})]})})}),p.length>0&&i.jsxs("aside",{className:"doc-toc",children:[i.jsxs("div",{className:"toc-title",children:[i.jsx(X,{name:"utility",size:16}),i.jsx("span",{children:"On this page"})]}),i.jsx("nav",{className:"toc-nav",children:p.map((g,x)=>{var j;const b=(j=g.props.className)==null?void 0:j.includes("doc-heading-h2");return i.jsx("a",{href:`#${b?"h2-":"h3-"}-${x}`,className:`toc-link ${b?"toc-h2":"toc-h3"}`,children:g.props.children},x)})})]})]}),i.jsx(St,{})]})}function aS(){var I,D;const[t,s]=T.useState(!1),[r,o]=T.useState(""),[c,d]=T.useState(!1),{filters:h,setQuery:p,setCategory:f,toggleTag:v,clearFilters:g,results:x,hasActiveFilters:b,resultCount:j}=gy(),k=iS();T.useEffect(()=>{const B=()=>{const V=window.location.hash.slice(1);if(V.startsWith("#/docs/")){const z=V.replace("#/docs/",""),re=We.find(Y=>Y.slug===z);re&&(o(re.category),f(re.category))}};return B(),window.addEventListener("hashchange",B),()=>window.removeEventListener("hashchange",B)},[]);const S=()=>{d(!0)},N=B=>{o(B),f(B),s(!1)},O=()=>{h.query||d(!1)},M=B=>{pe(`/docs/${B}`),p(""),d(!1)},L=T.useMemo(()=>{const B={};return x.forEach(V=>{const z=V.page.category;B[z]||(B[z]=[]),B[z].push(V)}),B},[x]);return i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"docs"}),i.jsxs("main",{className:"shell page-main docs-page",children:[i.jsx("div",{className:"docs-hero",children:i.jsxs("div",{className:"docs-hero-content",children:[i.jsx("div",{className:"eyebrow docs-eyebrow",children:"Documentation Center"}),i.jsxs("h1",{className:"docs-title",children:["Everything you need to know about",i.jsx("br",{}),i.jsx("span",{className:"title-accent",children:"using Niko"})]}),i.jsx("p",{className:"docs-subtitle",children:"Comprehensive guides, command references, and tips to help you get the most out of your server bot."})]})}),i.jsx("div",{className:`docs-search-section ${c?"active":""}`,children:i.jsxs("div",{className:"docs-search-container",children:[i.jsx(Z1,{value:h.query,onChange:p,placeholder:"Search documentation, commands, guides...",onFocus:S,onBlur:O}),c&&h.query&&x.length>0&&i.jsxs("div",{className:"search-results-dropdown",children:[i.jsxs("div",{className:"search-results-header",children:[i.jsxs("span",{className:"results-count",children:[j," ",j===1?"result":"results"]}),i.jsx("button",{className:"clear-search-btn",onClick:()=>{p(""),g(),o("")},children:"Clear"})]}),i.jsx("div",{className:"search-results-list",children:x.slice(0,8).map((B,V)=>i.jsxs("button",{className:"search-result-item",onClick:()=>M(B.page.slug),onMouseEnter:()=>{},children:[i.jsx("div",{className:"result-icon",children:i.jsx(X,{name:"doc",size:18})}),i.jsxs("div",{className:"result-content",children:[i.jsx("div",{className:"result-title",children:B.page.title}),i.jsx("div",{className:"result-excerpt",children:B.page.excerpt}),B.highlights.length>0&&i.jsxs("div",{className:"result-highlight",children:[B.highlights[0].slice(0,100),"..."]})]}),i.jsx(X,{name:"arrow",size:14,className:"result-arrow"})]},B.page.slug))}),x.length>8&&i.jsx("div",{className:"search-results-footer",children:i.jsxs("span",{children:["Showing 8 of ",x.length," results. Browse all docs below."]})})]})]})}),i.jsxs("div",{className:"docs-mobile-nav",children:[i.jsx("button",{className:"mobile-menu-toggle",onClick:()=>s(!t),"aria-label":"Toggle documentation menu",children:i.jsx(X,{name:"utility",size:20})}),t&&i.jsxs("div",{className:"mobile-nav-panel",children:[i.jsxs("div",{className:"mobile-nav-header",children:[i.jsx("h3",{children:"Documentation"}),i.jsx("button",{className:"close-menu-btn",onClick:()=>s(!1),"aria-label":"Close menu",children:i.jsx(X,{name:"utility",size:16,className:"rotated"})})]}),i.jsx("div",{className:"mobile-nav-sections",children:En.map(B=>i.jsxs("button",{className:`mobile-nav-item ${r===B.id?"active":""}`,onClick:()=>{N(B.id)},children:[i.jsx(X,{name:B.icon,size:18}),i.jsx("span",{className:"mobile-section-label",children:B.label}),i.jsx("span",{className:"mobile-section-count",children:B.count})]},B.id))})]})]}),k.length>0&&!b&&i.jsxs("div",{className:"docs-tags-cloud",children:[i.jsxs("div",{className:"tags-cloud-title",children:[i.jsx(X,{name:"utility",size:16}),i.jsx("span",{children:"Popular Topics"})]}),i.jsx("div",{className:"tags-cloud-list",children:k.slice(0,15).map(({tag:B,count:V})=>i.jsxs("button",{className:"tag-cloud-item",onClick:()=>v(B),style:{fontSize:`${.75+Math.min(V/4,1)}rem`},children:["#",B,i.jsx("span",{className:"tag-count",children:V})]},B))})]}),i.jsx("div",{className:"docs-category-filters",children:i.jsx(eS,{selectedCategory:h.category,onSelectCategory:N,sections:En})}),b&&i.jsxs("div",{className:"docs-results-header",children:[i.jsxs("div",{className:"results-info",children:[i.jsxs("span",{className:"results-count-large",children:[j," ",j===1?"article":"articles"]}),h.query&&i.jsxs("span",{className:"search-query-display",children:['for "',i.jsx("strong",{children:h.query}),'"']})]}),i.jsxs("button",{className:"clear-all-btn",onClick:()=>{g(),o("")},disabled:!b,children:[i.jsx(X,{name:"utility",size:14}),"Clear all filters"]})]}),i.jsx("div",{className:"docs-content",children:b?i.jsx("div",{className:"search-results-view",children:Object.entries(L).map(([B,V])=>{var z;return i.jsxs("section",{className:"results-category",children:[i.jsx("h2",{className:"category-title",children:((z=En.find(re=>re.id===B))==null?void 0:z.label)||B}),i.jsx("div",{className:"category-results-grid",children:V.map(re=>i.jsx(cc,{doc:re,variant:"highlighted"},re.page.slug))})]},B)})}):r?i.jsxs("div",{className:"category-view",children:[i.jsxs("div",{className:"category-header",children:[i.jsx("h2",{className:"category-page-title",children:((I=En.find(B=>B.id===r))==null?void 0:I.label)||r}),i.jsx("p",{className:"category-description",children:(D=En.find(B=>B.id===r))==null?void 0:D.description})]}),i.jsx("div",{className:"category-articles",children:We.filter(B=>B.category===r).sort((B,V)=>B.order-V.order).map(B=>i.jsx(cc,{doc:B},B.slug))})]}):i.jsx("div",{className:"all-categories-view",children:En.map(B=>i.jsxs("section",{className:"docs-section",id:`section-${B.id}`,children:[i.jsxs("div",{className:"section-header",children:[i.jsx("div",{className:"section-icon",children:i.jsx(X,{name:B.icon,size:28})}),i.jsxs("div",{className:"section-info",children:[i.jsx("h2",{className:"section-title",children:B.label}),i.jsx("p",{className:"section-description",children:B.description})]}),i.jsx("span",{className:"section-count",children:B.count})]}),i.jsx("div",{className:"section-articles",children:We.filter(V=>V.category===B.id).sort((V,z)=>V.order-z.order).map(V=>i.jsx(cc,{doc:V},V.slug))})]},B.id))})}),i.jsxs("div",{className:"docs-footer-note",children:[i.jsx(X,{name:"book",size:20}),i.jsxs("div",{children:[i.jsx("strong",{children:"Want more detail?"}),i.jsxs("p",{children:["The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in the"," ",i.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"docs/"})," ","folder."]})]})]})]}),i.jsx(St,{})]})}function oS(){const t=_n(),[s,r]=T.useState(null);T.useEffect(()=>{ga().then(r).catch(()=>{})},[]);const o=[["spark","AI that remembers","Thoughtful conversation with a cozy personality and controls that respect your community."],["chart","A living economy","Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],["shield","Confident moderation","Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],["users","Community rituals","Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."]];return i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"home"}),i.jsxs("main",{children:[i.jsxs("section",{className:"hero shell",children:[i.jsxs("div",{className:"hero-copy",children:[i.jsxs("div",{className:"eyebrow",children:[i.jsx("span",{className:"status-dot"})," Discord companion · online"]}),i.jsxs("div",{className:"hero-identity",children:[i.jsx("span",{className:"hero-avatar",children:t!=null&&t.bot_avatar_url?i.jsx("img",{src:t.bot_avatar_url,alt:"Niko"}):"n"}),i.jsxs("span",{children:[i.jsx("strong",{children:"Niko"}),i.jsx("small",{children:"Your server’s calm, capable co-pilot"})]})]}),i.jsxs("h1",{children:["Useful tools for a ",i.jsx("em",{children:"better server."})]}),i.jsx("p",{children:"Niko handles the everyday work of running a Discord community, so your moderators can focus on the people in it."}),i.jsxs("div",{className:"hero-buttons",children:[i.jsxs("a",{className:"button button-primary",href:(t==null?void 0:t.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Invite Niko ",i.jsx(X,{name:"arrow"})]}),i.jsx("a",{className:"button button-muted",href:"/commands",onClick:c=>{c.preventDefault(),pe("/commands")},children:"Explore commands"})]}),i.jsxs("div",{className:"stats-strip",children:[i.jsxs("div",{children:[i.jsx("strong",{children:xe(s==null?void 0:s.guild_count)}),i.jsx("span",{children:"servers"})]}),i.jsxs("div",{children:[i.jsx("strong",{children:xe(s==null?void 0:s.user_count)}),i.jsx("span",{children:"members"})]}),i.jsxs("div",{children:[i.jsx("strong",{children:xe(s==null?void 0:s.command_count)}),i.jsx("span",{children:"commands"})]})]})]}),i.jsx("div",{className:"hero-art","aria-label":"A preview of Niko's server workspace",children:i.jsxs("div",{className:"workspace-preview",children:[i.jsxs("div",{className:"workspace-preview-top",children:[i.jsxs("span",{className:"preview-dots",children:[i.jsx("i",{}),i.jsx("i",{}),i.jsx("i",{})]}),i.jsx("span",{children:"server workspace"}),i.jsxs("span",{className:"preview-status",children:[i.jsx("span",{className:"status-dot"})," live"]})]}),i.jsxs("div",{className:"preview-body",children:[i.jsxs("div",{className:"preview-sidebar",children:[i.jsx("span",{className:"preview-label",children:"NIKO"}),i.jsx("b",{children:"Overview"}),i.jsx("span",{children:"Economy"}),i.jsx("span",{children:"Leveling"}),i.jsx("span",{children:"Moderation"}),i.jsx("span",{children:"AI controls"})]}),i.jsxs("div",{className:"preview-main",children:[i.jsx("span",{className:"preview-label",children:"SERVER SNAPSHOT"}),i.jsx("strong",{children:"Everything in one place."}),i.jsxs("div",{className:"preview-stats",children:[i.jsxs("span",{children:[i.jsx("b",{children:xe(s==null?void 0:s.user_count)}),i.jsx("small",{children:"members"})]}),i.jsxs("span",{children:[i.jsx("b",{children:xe(s==null?void 0:s.command_count)}),i.jsx("small",{children:"commands"})]})]}),i.jsxs("div",{className:"preview-line",children:[i.jsx("i",{}),i.jsx("i",{}),i.jsx("i",{})]})]})]})]})})]}),i.jsxs("section",{className:"shell intro-section",children:[i.jsx("div",{className:"section-kicker",children:"Why Niko"}),i.jsxs("div",{className:"intro-grid",children:[i.jsxs("h2",{children:["The good kind of",i.jsx("br",{}),i.jsx("em",{children:"always-on."})]}),i.jsx("p",{children:"Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile."})]})]}),i.jsx("section",{className:"shell feature-grid",children:o.map(([c,d,h])=>i.jsxs("article",{className:"feature-card",children:[i.jsx("span",{className:"feature-icon",children:i.jsx(X,{name:c})}),i.jsx("h3",{children:d}),i.jsx("p",{children:h}),i.jsxs("a",{href:"/docs",onClick:p=>{p.preventDefault(),pe("/docs")},children:["Learn more ",i.jsx(X,{name:"arrow"})]})]},d))}),i.jsxs("section",{className:"shell callout",children:[i.jsxs("div",{children:[i.jsx("div",{className:"section-kicker",children:"Ready when you are"}),i.jsxs("h2",{children:["A calmer, cleverer home",i.jsx("br",{}),"for your community."]})]}),i.jsxs("a",{className:"button button-primary",href:(t==null?void 0:t.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Bring Niko in ",i.jsx(X,{name:"arrow"})]})]})]}),i.jsx(St,{})]})}const lS=[{code:"USDT",label:"Tether"},{code:"ETH",label:"Ethereum"},{code:"BTC",label:"Bitcoin"},{code:"BNB",label:"BNB"},{code:"LTC",label:"Litecoin"},{code:"DOGE",label:"Dogecoin"},{code:"TRX",label:"TRON"},{code:"XMR",label:"Monero"}];function cS(){const s=new URLSearchParams(window.location.search).get("token")||"",[r,o]=T.useState("5"),[c,d]=T.useState("USDT"),[h,p]=T.useState(!1),[f,v]=T.useState(""),[g,x]=T.useState(null),[b,j]=T.useState(null),[k,S]=T.useState(!1);T.useEffect(()=>{s||S(!0)},[s]),T.useEffect(()=>{if(!(g!=null&&g.status_url)||g.paid)return;const O=setInterval(async()=>{try{const M=await Te(g.status_url);j(M),M.paid&&clearInterval(O)}catch{}},5e3);return()=>clearInterval(O)},[g]);const N=async O=>{O.preventDefault(),p(!0),v("");try{const M=await Te("/api/donations/invoice",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:s,amount:parseFloat(r),currency:c})});x(M),M.error&&(v(M.error),x(null))}catch(M){v(M instanceof Error?M.message:"Could not create invoice.")}finally{p(!1)}};return k?i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"home"}),i.jsx("main",{className:"auth-page",children:i.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[i.jsx("span",{className:"auth-mark",children:"!"}),i.jsx("div",{className:"eyebrow",children:"Invalid donation link"}),i.jsxs("h1",{children:["This link is ",i.jsx("em",{children:"invalid."})]}),i.jsxs("p",{children:["The donation link is missing or has expired. Use the"," ",i.jsx("code",{children:"/donate"})," command in Discord to generate a new one."]}),i.jsx("button",{className:"button button-primary full-width",onClick:()=>pe("/"),children:"Return home"})]})})]}):b!=null&&b.paid?i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"home"}),i.jsx("main",{className:"auth-page",children:i.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[i.jsx("span",{className:"auth-mark",children:"✓"}),i.jsx("div",{className:"eyebrow",children:"Payment confirmed"}),i.jsxs("h1",{children:["Thank you ",i.jsx("em",{children:"for supporting!"})]}),i.jsx("p",{children:"Your donation has been confirmed. You will receive the Supporter badge shortly."}),i.jsx("button",{className:"button button-primary full-width",onClick:()=>pe("/"),children:"Return home"})]})})]}):i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"home"}),i.jsx("main",{className:"page-main",children:i.jsx("div",{className:"shell",children:i.jsxs("div",{className:"page-heading",style:{maxWidth:500,margin:"0 auto"},children:[i.jsx("div",{className:"eyebrow",style:{marginBottom:15},children:"Support Niko"}),i.jsxs("h1",{children:["Keep Niko ",i.jsx("em",{children:"running."})]}),i.jsx("p",{style:{color:"var(--muted)",marginBottom:30},children:"Your donation helps cover hosting costs and keeps Niko running for all servers. Choose an amount and cryptocurrency below."}),g!=null&&g.pay_link?i.jsxs("div",{className:"dash-panel",style:{marginBottom:24},children:[i.jsx("div",{className:"panel-heading",children:i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Invoice created"}),i.jsx("h3",{children:"Complete your payment"})]})}),i.jsxs("p",{style:{color:"var(--muted)",fontSize:12,marginBottom:16},children:["Amount: ",i.jsxs("strong",{children:["$",parseFloat(r).toFixed(2)," USD"]})," in"," ",i.jsx("strong",{children:c})]}),i.jsxs("p",{style:{color:"var(--dim)",fontSize:10,marginBottom:16},children:["Track ID: ",i.jsx("code",{children:g.track_id})," · Expires in 60 minutes"]}),i.jsxs("a",{className:"button button-primary",href:g.pay_link,target:"_blank",rel:"noopener noreferrer",children:["Pay now ",i.jsx(X,{name:"arrow"})]}),i.jsx("p",{style:{color:"var(--dim)",fontSize:10,marginTop:12},children:"Payment will be confirmed automatically once the transaction is processed on-chain."})]}):i.jsxs("form",{onSubmit:N,className:"dash-panel",style:{marginBottom:24},children:[i.jsxs("div",{className:"form-grid",children:[i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Amount (USD)"}),i.jsx("input",{type:"number",min:"1",max:"10000",step:"0.01",value:r,onChange:O=>o(O.target.value)}),i.jsx("small",{children:"Minimum $1.00, maximum $10,000.00"})]}),i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Cryptocurrency"}),i.jsx("select",{value:c,onChange:O=>d(O.target.value),children:lS.map(O=>i.jsxs("option",{value:O.code,children:[O.label," (",O.code,")"]},O.code))})]})]}),f&&i.jsx("p",{className:"form-error",style:{marginTop:12},role:"alert",children:f}),i.jsx("div",{style:{marginTop:16},children:i.jsx("button",{className:"button button-primary",type:"submit",disabled:h,children:h?"Creating invoice…":"Create invoice"})})]}),i.jsxs("div",{className:"docs-footer-note",style:{marginTop:20},children:[i.jsx("strong",{children:"How it works"}),i.jsx("p",{children:'1. Choose an amount and currency above · 2. Click "Pay now" to open the payment page · 3. Send crypto to the displayed address · 4. Payment is confirmed automatically once processed on-chain'})]})]})})})]})}const uS={privacy:{title:"Privacy policy",intro:"Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",sections:[["Information we use","User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature. The dashboard stores daily aggregate message, join, and leave counts without message text or member IDs."],["How it is used","Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],["Storage and retention","Data is stored by the server hosting Niko in local JSON and SQLite files. Economy, leveling, and configuration data remain until removed. Daily server activity totals are retained as aggregates. AI conversation history is limited and can be cleared with /clearhistory."],["Third-party services","When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Music and external lookup features may contact their respective services."],["Your choices","Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."]]},terms:{title:"Terms of service",intro:"By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",sections:[["Permitted use","Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],["Availability","Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],["Moderation","The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],["AI content","AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],["Virtual items","In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],["Contact","Questions or concerns can be sent through the Niko support server."]]},community:{title:"Community policy",intro:"These community expectations apply to every server that uses Niko. By adding the bot to a server, the server's owners and administrators agree to uphold these standards.",sections:[["Purpose","Niko is a community companion for Discord servers of all kinds. To keep the platform safe for everyone, all servers using Niko must follow the expectations below in addition to Discord's Terms of Service and Community Guidelines."],["Discrimination and harassment","Servers must not permit or promote discrimination, harassment, or hate speech targeting people based on race, ethnicity, national origin, religion, disability, gender, gender identity or expression, sexual orientation, age, veteran status, or any other protected identity characteristic."],["Illegal and malicious content","Servers must not create, host, share, or distribute illegal or malicious content. This includes, but is not limited to: child sexual abuse material (CSAM), malware and other malicious software, gore or shock content, pirated media and/or software, content that facilitates violence or terrorism, scams and phishing, and any other content that is illegal under applicable law."],["Other prohibited conduct","Servers must not use Niko to facilitate doxxing, targeted harassment campaigns, sextortion, trafficking, or the sexualization of minors in any form."],["Enforcement and investigations","When a server is reported or flagged for potentially violating this policy, Niko will send a warning notice to the server. The notice is followed by an investigation by Niko staff. Servers that cooperate in good faith and are found not to be breaking the policies will not receive any further action."],["Obstruction of investigations","Banning, kicking, or otherwise removing the staff member(s) sent to investigate, or hiding, deleting, or tampering with potential evidence, is treated as an admission of guilt. Doing so will result in the server — and any users who are involved — being permanently blacklisted from further use of Niko, in addition to any other action the investigation warrants."],["Reporting","If you believe a server using Niko is violating this policy, report it through the Niko support server. Reports are reviewed by staff and handled confidentially."]]}};function uc({type:t}){const s=uS[t];return i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:t}),i.jsxs("main",{className:"shell page-main legal-page",children:[i.jsxs("div",{className:"page-heading",children:[i.jsx("div",{className:"eyebrow",children:"Niko legal"}),i.jsx("h1",{children:s.title}),i.jsx("p",{children:s.intro}),i.jsx("small",{children:"Effective date: 1 January 2025"})]}),i.jsx("div",{className:"legal-copy",children:s.sections.map(([r,o])=>i.jsxs("section",{children:[i.jsx("h2",{children:r}),i.jsx("p",{children:o})]},r))})]}),i.jsx(St,{})]})}const dS=[{key:"txt",label:"TXT",icon:"📄"},{key:"html",label:"HTML",icon:"🌐"},{key:"csv",label:"CSV",icon:"📊"},{key:"json",label:"JSON",icon:"{ }"}],yy=t=>typeof t!="number"||t<0||t>16777215?"":`#${t.toString(16).padStart(6,"0")}`,es=t=>(t==null?void 0:t.url)||(t==null?void 0:t.proxy_url)||"",vy=t=>/\.(?:png|jpe?g|gif|webp|bmp|svg)(?:[?#]|$)/i.test(t)||t.startsWith("data:image/"),xy=t=>/\.(?:mp4|webm|mov|m4v|ogg)(?:[?#]|$)/i.test(t)||t.startsWith("data:video/"),hS=t=>t.url?t.url:t.id?`https://cdn.discordapp.com/stickers/${t.id}.${t.format_type===4?"gif":"png"}`:"";function mS(t){var r;const s=es(t);return s?(r=t==null?void 0:t.content_type)!=null&&r.startsWith("video/")?!0:xy(s):!1}const ef=new RegExp("(`[^`\\n]+`)|(\\[([^\\]\\n]+)\\]\\((https?:\\/\\/[^\\s)\\] ]+)\\))|(\\*\\*)|(?<!\\*)\\*(?!\\*)|(~~)","g"),pS=/(https?:\/\/[^\s<>)]+)/g,tf={bold:"**",italic:"*",strike:"~~"},fS=new Set(["t","T","d","D","f","F","R"]);function gS(t,s){if(!Number.isFinite(t)||!fS.has(s))return null;const r=new Date(t*1e3);if(Number.isNaN(r.getTime()))return null;if(s==="R"){const c=t-Math.floor(Date.now()/1e3),d=Math.abs(c),h=d<60?"second":d<3600?"minute":d<86400?"hour":d<604800?"day":d<2592e3?"week":d<31536e3?"month":"year",p=h==="second"?1:h==="minute"?60:h==="hour"?3600:h==="day"?86400:h==="week"?604800:h==="month"?2592e3:31536e3;return new Intl.RelativeTimeFormat(void 0,{numeric:"always"}).format(Math.round(c/p),h)}const o={...s==="t"||s==="T"?{hour:"numeric",minute:"2-digit"}:{},...s==="T"?{second:"2-digit"}:{},...s==="d"?{year:"numeric",month:"2-digit",day:"2-digit"}:{},...s==="D"?{year:"numeric",month:"long",day:"numeric"}:{},...s==="f"?{year:"numeric",month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}:{},...s==="F"?{weekday:"long",year:"numeric",month:"long",day:"numeric",hour:"numeric",minute:"2-digit"}:{}};return new Intl.DateTimeFormat(void 0,o).format(r)}function yS(t){const s=[];let r=0,o;const c=d=>{if(!d)return;const h=d.split(/(<a?:[A-Za-z0-9_~]+:\d+>|<t:-?\d+:[tTdDfFR]>)/g);for(const p of h){if(!p)continue;const f=p.match(/^<(a?):([A-Za-z0-9_~]+):(\d+)>$/);if(f){s.push({type:"emoji",name:f[2],id:f[3],animated:f[1]==="a"});continue}const v=p.match(/^<t:(-?\d+):([tTdDfFR])>$/);if(v){s.push({type:"timestamp",unix:Number(v[1]),style:v[2],raw:p});continue}const g=p.split(pS);for(let x=0;x<g.length;x++)g[x]&&(x%2===1?s.push({type:"link",text:g[x],url:g[x]}):s.push({type:"text",text:g[x]}))}};for(ef.lastIndex=0;(o=ef.exec(t))!==null;)o.index>r&&c(t.slice(r,o.index)),o[1]!==void 0?s.push({type:"code",text:o[1].slice(1,-1)}):o[2]!==void 0?s.push({type:"link",text:o[3],url:o[4]}):o[5]!==void 0?s.push({type:"marker",fmt:"bold"}):o[6]!==void 0?s.push({type:"marker",fmt:"italic"}):o[7]!==void 0&&s.push({type:"marker",fmt:"strike"}),r=o.index+o[0].length;return r<t.length&&c(t.slice(r)),s}function vS(t){const s=[],r=[],o=new Set,c=d=>{r.length>0?r[r.length-1].children.push(d):s.push(d)};for(const d of yS(t))if(d.type==="text")c({kind:"text",text:d.text});else if(d.type==="code")c({kind:"code",text:d.text});else if(d.type==="link")c({kind:"link",text:d.text,url:d.url});else if(d.type==="emoji")c({kind:"emoji",name:d.name,id:d.id,animated:d.animated});else if(d.type==="timestamp")c({kind:"timestamp",unix:d.unix,style:d.style,raw:d.raw});else if(d.type==="marker")if(o.has(d.fmt)){const h=r.map(v=>v.fmt).lastIndexOf(d.fmt),p=r.splice(h);p.forEach(v=>o.delete(v.fmt));const f={kind:"fmt",fmt:d.fmt,children:[...p[0].children]};for(const v of p.slice(1))f.children.push({kind:"text",text:tf[v.fmt]??""}),f.children.push(...v.children);c(f)}else r.push({fmt:d.fmt,children:[]}),o.add(d.fmt);if(r.length>0)for(const d of r){c({kind:"text",text:tf[d.fmt]??""});for(const h of d.children)c(h)}return s}const by=(t,s)=>t.map((r,o)=>{const c=`${s}-${o}`;switch(r.kind){case"text":return i.jsx("span",{children:r.text},c);case"code":return i.jsx("code",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:4,padding:"0 5px",color:"#f2b8c2",fontFamily:"monospace",fontSize:"0.92em"},children:r.text},c);case"emoji":return i.jsx("img",{src:`https://cdn.discordapp.com/emojis/${r.id}.${r.animated?"gif":"png"}`,alt:`:${r.name}:`,title:`:${r.name}:`,style:{width:22,height:22,objectFit:"contain",verticalAlign:"-0.35em",display:"inline-block"},onError:d=>{d.currentTarget.alt=`:${r.name}:`}},c);case"timestamp":{const d=gS(r.unix,r.style);return d?i.jsx("time",{dateTime:new Date(r.unix*1e3).toISOString(),title:r.raw,children:d},c):i.jsx("span",{children:r.raw},c)}case"link":return i.jsx("a",{href:r.url,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",textDecoration:"none"},onMouseEnter:d=>{d.currentTarget.style.textDecoration="underline"},onMouseLeave:d=>{d.currentTarget.style.textDecoration="none"},children:r.text},c);case"fmt":{const d={};return r.fmt==="bold"&&(d.fontWeight=700),r.fmt==="italic"&&(d.fontStyle="italic"),r.fmt==="strike"&&(d.textDecoration="line-through"),i.jsx("span",{style:d,children:by(r.children,c)},c)}}}),ra=t=>by(vS(t),"md");function Yn({text:t,muted:s}){const r=t.split(`
`),o=[];return r.forEach((c,d)=>{const h=c.trimStart(),f=d===r.length-1?null:i.jsx("br",{},`br${d}`);h.startsWith("-# ")?o.push(i.jsxs("span",{style:{color:s?"#6d737a":"#949ba4",fontSize:12},children:[ra(h.slice(3)),f]},d)):/^#{1,4}\s/.test(h)?o.push(i.jsxs("span",{style:{color:"#f2f3f5",fontWeight:700,fontSize:16},children:[ra(h),f]},d)):h.startsWith("> ")?o.push(i.jsxs("span",{style:{display:"inline-block",color:"#b5bac1",borderLeft:"3px solid #4e5058",paddingLeft:8},children:[ra(h.slice(2)),f]},d)):h.startsWith("```")?o.push(i.jsxs("pre",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:6,padding:"10px 12px",overflowX:"auto",whiteSpace:"pre-wrap",wordBreak:"break-word",fontFamily:"monospace",fontSize:12.5,color:"#dbdee1",margin:"2px 0"},children:[h.replace(/^```[a-zA-Z]*/,"").replace(/```$/,""),f]},d)):o.push(i.jsxs("span",{children:[ra(c),f]},d))}),i.jsx("span",{style:{whiteSpace:"pre-wrap",wordBreak:"break-word"},children:o})}function xS({embed:t}){const s=yy(t.color)||"#5865f2",r=t.author,o=t.footer,c=es(t.thumbnail),d=es(t.image);return i.jsxs("div",{style:{display:"flex",gap:12,maxWidth:560,marginTop:8,background:"#2b2d31",border:"1px solid #3f4147",borderLeft:`4px solid ${s}`,borderRadius:6,padding:"10px 12px"},children:[i.jsxs("div",{style:{flex:1,minWidth:0},children:[(r==null?void 0:r.name)&&i.jsxs("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:4},children:[r.icon_url&&i.jsx("img",{src:r.icon_url||r.proxy_icon_url,alt:"",style:{width:18,height:18,borderRadius:"50%",verticalAlign:"-4px",marginRight:6}}),r.name]}),t.title&&i.jsx("div",{style:{color:"#00a8fc",fontWeight:600,margin:"2px 0 4px",fontSize:14},children:t.url?i.jsx("a",{href:t.url,target:"_blank",rel:"noopener noreferrer",style:{color:"inherit",textDecoration:"none"},children:i.jsx(Yn,{text:t.title})}):i.jsx(Yn,{text:t.title})}),t.description&&i.jsx("div",{style:{color:"#dbdee1",fontSize:13,lineHeight:1.5},children:i.jsx(Yn,{text:t.description})}),t.fields&&t.fields.length>0&&i.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:"6px 12px",marginTop:8},children:t.fields.map((h,p)=>i.jsxs("div",{style:{flex:h.inline?"0 1 45%":"1 1 100%",minWidth:0,marginBottom:4},children:[h.name&&i.jsx("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:2},children:i.jsx(Yn,{text:h.name})}),h.value&&i.jsx("div",{style:{color:"#dbdee1",fontSize:13},children:i.jsx(Yn,{text:h.value})})]},p))}),d&&i.jsx("a",{href:d,target:"_blank",rel:"noopener noreferrer",style:{display:"block",marginTop:8},children:i.jsx("img",{src:d,alt:"",style:{maxWidth:"100%",maxHeight:300,borderRadius:4,display:"block"},onError:h=>{h.currentTarget.style.display="none"}})}),((o==null?void 0:o.text)||t.timestamp)&&i.jsxs("div",{style:{display:"flex",alignItems:"center",gap:6,marginTop:6,color:"#949ba4",fontSize:11},children:[(o==null?void 0:o.icon_url)&&i.jsx("img",{src:o.icon_url||o.proxy_icon_url,alt:"",style:{width:16,height:16,borderRadius:"50%"}}),(o==null?void 0:o.text)&&i.jsx("span",{children:o.text}),t.timestamp&&i.jsx("span",{children:String(t.timestamp).replace("T"," ").replace("+00:00"," UTC")})]})]}),c&&i.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:i.jsx("img",{src:c,alt:"",style:{width:80,height:80,borderRadius:6,objectFit:"cover"},onError:h=>{h.currentTarget.style.display="none"}})})]})}function pa({component:t}){switch(t.type){case 17:{const s=yy(t.accent_color);return i.jsxs("div",{style:{display:"flex",overflow:"hidden",maxWidth:560,marginTop:8,background:"#2b2d31",border:`1px solid ${s||"#3f4147"}`,borderRadius:12},children:[s&&i.jsx("div",{style:{flex:"0 0 4px",background:s}}),i.jsx("div",{style:{flex:1,minWidth:0,padding:"6px 12px 8px"},children:(t.components||[]).map((r,o)=>i.jsx(pa,{component:r},o))})]})}case 1:return i.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,margin:"6px 0"},children:(t.components||[]).map((s,r)=>i.jsx(pa,{component:s},r))});case 2:{const s=t.emoji,r=`${(s==null?void 0:s.name)??""}${t.label?` ${t.label}`:""}`.trim();return t.style===5&&!!t.url?i.jsx("a",{href:t.url,target:"_blank",rel:"noopener noreferrer",style:{display:"inline-block",padding:"3px 14px",background:"#5865f2",borderRadius:4,color:"#fff",fontSize:13,fontWeight:600,textDecoration:"none"},children:r||"Button"}):i.jsx("span",{style:{display:"inline-block",padding:"3px 14px",background:"#4e5058",borderRadius:4,color:t.disabled?"#8a8e96":"#f2f3f5",fontSize:13,cursor:t.disabled?"not-allowed":"default",opacity:t.disabled?.55:1},children:r||"Button"})}case 9:{const s=[...t.components||[]];return t.accessory&&s.push(t.accessory),i.jsx("div",{style:{display:"flex",alignItems:"center",gap:10,margin:"4px 0"},children:s.map((r,o)=>i.jsx(pa,{component:r},o))})}case 10:return i.jsx("div",{style:{color:"#dbdee1",fontSize:14,lineHeight:1.5,margin:"4px 0",wordBreak:"break-word"},children:i.jsx(Yn,{text:t.content||""})});case 18:return i.jsx("div",{style:{color:"#f2f3f5",fontWeight:700,textTransform:"uppercase",letterSpacing:"0.04em",fontSize:12,margin:"4px 0"},children:t.content});case 14:return i.jsx("div",{style:{margin:t.divider===!1?"6px 0":"9px 0",...t.divider===!1?{}:{borderTop:"1px solid #3f4147"}}});case 11:{const s=es(t.media);return s?i.jsx("a",{href:s,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:i.jsx("img",{src:s,alt:t.description||"",style:{width:40,height:40,borderRadius:"50%",objectFit:"cover",display:"block"},onError:r=>{r.currentTarget.style.display="none"}})}):null}case 12:{const r=(t.items||[]).filter(o=>es(o.media));return r.length===0?null:i.jsx("div",{style:{display:"grid",gridTemplateColumns:`repeat(auto-fill, minmax(${Math.min(220,Math.max(140,Math.floor(560/Math.max(1,r.length))))}px, 1fr))`,gap:6,margin:"6px 0"},children:r.map((o,c)=>{const d=es(o.media),h=o.description;return mS(o.media)?i.jsxs("figure",{style:{margin:0},children:[i.jsx("video",{src:d,controls:!0,preload:"metadata",style:{width:"100%",maxHeight:260,borderRadius:6,background:"#1e1f22"}}),h&&i.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:h})]},c):vy(d)?i.jsxs("figure",{style:{margin:0},children:[i.jsx("a",{href:d,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:i.jsx("img",{src:d,alt:h||"",style:{width:"100%",maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:p=>{p.currentTarget.style.display="none"}})}),h&&i.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:h})]},c):i.jsxs("a",{href:d,target:"_blank",rel:"noopener noreferrer",style:{display:"flex",alignItems:"center",gap:6,padding:"6px 10px",background:"#383a40",borderRadius:6,color:"#dbdee1",fontSize:12,textDecoration:"none"},children:["📎 ",h||"Attachment"]},c)})})}case 13:{const s=es(t.media)||t.url||"";return s?i.jsxs("a",{href:s,target:"_blank",rel:"noopener noreferrer",style:{display:"block",margin:"4px 0",color:"#00a8fc",fontSize:12.5,textDecoration:"none"},children:["📎 ",t.label||"Attachment"]}):null}default:return null}}function bS({components:t}){return i.jsx(i.Fragment,{children:t.map((s,r)=>i.jsx(pa,{component:s},r))})}function wS({text:t}){return i.jsx(Yn,{text:t})}function kS({msg:t}){const s=!!(t.attachments&&t.attachments.length>0||t.embeds&&t.embeds.length>0||t.components&&t.components.length>0||t.stickers&&t.stickers.length>0);return i.jsxs("div",{style:{padding:"10px 16px",borderBottom:"1px solid #2b2d31",fontSize:14,lineHeight:1.6},children:[i.jsxs("div",{style:{marginBottom:2},children:[i.jsx("span",{style:{color:"#949ba4",fontSize:11,fontFamily:"monospace"},children:t.timestamp})," ",i.jsx("span",{style:{color:"#f2f3f5",fontWeight:600},children:t.author})," ",i.jsxs("span",{style:{color:"#949ba4",fontSize:11},children:["(",t.author_id,")"]})]}),t.content?i.jsx("div",{style:{color:"#dbdee1"},children:i.jsx(wS,{text:t.content})}):s?null:i.jsx("div",{style:{color:"#6d737a",fontStyle:"italic",fontSize:13},children:"Message content unavailable"}),t.attachments&&t.attachments.length>0&&i.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:4},children:t.attachments.map((r,o)=>xy(r)?i.jsx("video",{src:r,controls:!0,preload:"metadata",style:{maxWidth:360,maxHeight:260,borderRadius:6,background:"#1e1f22"}},o):vy(r)?i.jsx("a",{href:r,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:i.jsx("img",{src:r,alt:"",style:{maxWidth:300,maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:c=>{const d=c.currentTarget;d.style.display="none"}})},o):i.jsx("a",{href:r,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",fontSize:12,textDecoration:"none"},children:"📎 Attachment"},o))}),t.embeds&&t.embeds.length>0&&i.jsx(i.Fragment,{children:t.embeds.map((r,o)=>i.jsx(xS,{embed:r},o))}),t.stickers&&t.stickers.length>0&&i.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:8},children:t.stickers.map((r,o)=>{const c=hS(r);return c?i.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:i.jsx("img",{src:c,alt:r.name||"Discord sticker",title:r.name||"Discord sticker",style:{width:160,maxWidth:"100%",maxHeight:160,objectFit:"contain",display:"block"}})},o):null})}),t.components&&t.components.length>0&&i.jsx(bS,{components:t.components})]})}function jS({transcriptId:t}){const[s,r]=T.useState(null),[o,c]=T.useState(!0),[d,h]=T.useState("");T.useEffect(()=>{c(!0),h(""),fetch(`/api/transcript/${t}`).then(f=>{if(!f.ok)throw new Error("Transcript not found");return f.json()}).then(f=>{r(f),c(!1)}).catch(f=>{h(f.message||"Failed to load transcript"),c(!1)})},[t]);const p=f=>{window.open(`/api/transcript/${t}/download?format=${f}`,"_blank")};return o?i.jsx("div",{className:"page-main",children:i.jsx("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:i.jsx("div",{style:{color:"var(--muted)",fontSize:14},children:"Loading transcript…"})})}):d||!s?i.jsx("div",{className:"page-main",children:i.jsxs("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:[i.jsx("h2",{style:{marginBottom:12},children:"Transcript not found"}),i.jsx("p",{style:{color:"var(--muted)"},children:d||"This transcript doesn't exist or has been deleted."})]})}):i.jsx("div",{className:"page-main",children:i.jsxs("div",{className:"shell",style:{maxWidth:800},children:[i.jsx("div",{style:{background:"var(--surface)",border:"1px solid var(--line)",borderRadius:8,padding:24,marginBottom:20},children:i.jsxs("div",{style:{display:"flex",alignItems:"flex-start",justifyContent:"space-between",gap:16,flexWrap:"wrap"},children:[i.jsxs("div",{children:[i.jsx("div",{className:"eyebrow",style:{marginBottom:8},children:"Ticket Transcript"}),i.jsxs("h1",{style:{fontSize:24,letterSpacing:"-0.04em",margin:0},children:["#",s.channel_name]}),i.jsxs("div",{style:{color:"var(--muted)",fontSize:13,marginTop:6},children:[s.category," · ",s.message_count," messages · ",s.created_at]})]}),i.jsx("div",{style:{display:"flex",gap:8,flexWrap:"wrap"},children:dS.map(f=>i.jsxs("button",{className:"button button-small button-muted",onClick:()=>p(f.key),style:{minWidth:70},children:[i.jsx("span",{children:f.icon}),i.jsx("span",{children:f.label})]},f.key))})]})}),i.jsxs("div",{style:{background:"#1e1f22",border:"1px solid #3f4147",borderRadius:8,overflow:"hidden"},children:[s.messages.map((f,v)=>i.jsx(kS,{msg:f},v)),s.messages.length===0&&i.jsx("div",{style:{padding:40,textAlign:"center",color:"#949ba4"},children:"No messages in this transcript."})]}),i.jsxs("div",{style:{marginTop:16,padding:"12px 0",textAlign:"center",color:"var(--dim)",fontSize:12},children:["Transcript ID: ",i.jsx("code",{style:{fontFamily:"monospace"},children:t})]})]})})}const Ma=[{slug:"staff-applications",title:"Staff Applications",date:"2026-09-29",tags:["applications","staff","dashboard","discord"],summary:"Guild dashboards can now manage multiple staff role openings with shareable web forms, Discord membership and eligibility checks, and reusable application links.",highlights:[{title:"Multiple Role Openings",description:"Create a separate application for each role, add custom questions, and optionally limit applications to members with selected server roles.",icon:"users"},{title:"Reusable Application Links",description:"Close an opening when hiring pauses and reopen it later with the same link. Earlier responses remain saved, and each Discord account can apply only once per opening.",icon:"utility"},{title:"Verified Applicant Forms",description:"Applicants sign in with Discord, and Niko verifies server membership and role eligibility before accepting a response. Managers can review submissions in the guild dashboard.",icon:"shield"}],changes:[{category:"added",items:["Guild dashboard tab to create and manage staff application openings","Custom application questions and optional role-based eligibility gates","Public Discord-authenticated application forms with bot-verified server membership","Stable per-opening application links, close/reopen controls, and response review","Database-enforced one-submission-per-user limit for each opening"]}],commits:[]},{slug:"server-logging-onboarding-updates",title:"Logging Reliability & Onboarding Rules",date:"2026-09-29",tags:["logging","onboarding","dashboard"],summary:"Server event logs are less likely to be delayed during busy periods, and onboarding now gives communities more room to share their rules with new members.",highlights:[{title:"More Reliable Server Logs",description:"Server event logs are less likely to be delayed during busy periods, helping moderation and activity updates stay easier to follow.",icon:"utility"},{title:"Longer Onboarding Rules",description:"Server rules in onboarding can now be up to 4,000 characters, making it easier to share complete guidelines with new members.",icon:"doc"}],changes:[{category:"improved",items:["Server event log delivery reliability during busy periods","Onboarding rules support for up to 4,000 characters"]}],commits:[]},{slug:"uwulock-starboard-overhaul",title:"UwU Lock Rebuilt & Starboard Persistence",date:"2026-09-25",version:"2.11.0",tags:["uwulock","starboard","database","fun","social"],summary:"The UwU Lock command has been completely rebuilt around the main database with immediate webhook reposts, reliable message transforms, and full Starboard integration — with proper author attribution that persists cleanly across restarts.",highlights:[{title:"Instant Webhook Transforms",description:"Locked users' messages are now deleted and immediately reposted via a shared per-channel webhook with their display name and avatar, including attachments, embeds, and stickers, with thread support and a guard against double-processing.",icon:"spark"},{title:"Real Author on the Starboard",description:"When a uwu-ified webhook message is starred, the Starboard resolves the original author from persistent attribution and renders their name, avatar, and original timestamp — not the webhook — in a clean Section with Thumbnail layout.",icon:"users"},{title:"Survives Restarts",description:"Both UwU Lock rules and Starboard configuration now live in the main database, loaded on startup via cog_load with automatic migration from the legacy JSON files and stale-webhook healing.",icon:"settings"}],changes:[{category:"added",items:["Main-database tables uwulock_config and uwulock_messages for lock rules and author attribution","Main-database tables starboard_config and starboard_messages for channel, threshold, emoji and post mappings","Automatic migration of legacy data/uwulock.json and data/starboard.json into the primary database with .migrated backups","Per-channel webhook reuse with stale-webhook detection via fetch and shared-webhook protection on removal","Thread-aware webhook sending with AllowedMentions.none and wait:true repost handling","UwU attribution storage (author name, avatar, original timestamp) for every transformed message","Starboard Section + Thumbnail rendering for uwu-locked messages with correct original author credit","Explicit UwU lock hook in events.on_message before AI triggers with a 2,000-entry dedup guard and fallback listener"]},{category:"improved",items:["UwU Lock now deletes the original message immediately instead of queuing for a background task","Attachment, embed, and sticker handling with text truncation and text-only fallback on send failure","Permission checks for Manage Messages and Manage Webhooks with localized failure messaging","Starboard reaction handling now distinguishes webhook reposts via database attribution","Starboard message edits and sends now use AllowedMentions.none for cleaner output","Webhook Channel resolution for threads via parent channel with robust create_webhook flow"]},{category:"fixed",items:["UwU Lock not creating the webhook or showing any sign it saw the message","Webhook created but original message not deleted and no new message sent","UwU transforms silently failing due to queue delay and background-task errors","Starboard not displaying correct author for uwu-locked webhook messages","Starboard and UwU Lock losing all state after a restart despite being stored","Stale or deleted webhooks leaving lock rules in a broken state"]},{category:"migrated",items:["UwU Lock from data/uwulock.json file storage to the primary database","Starboard configuration and starred post IDs from data/starboard.json to the primary database"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Added",value:"8",detail:"new persistence features",color:"#66866f"},{label:"Improved",value:"6",detail:"reliability upgrades",color:"#4a7fb5"},{label:"Fixed",value:"6",detail:"workflow bugs",color:"#d96545"}]},commits:[]},{slug:"guild-server-pulse-stats",title:"Guild Server Pulse Stats",date:"2026-09-24",tags:["dashboard","guild","analytics","stats"],summary:"Guild settings now include a Server pulse analytics card with an at-a-glance view of server size and recent community activity.",highlights:[{title:"Server Activity at a Glance",description:"The card summarizes member count, messages, and new members over the last 14 days, with interactive views for message trends, member joins and departures, and the server's members, channels, and roles.",icon:"chart"},{title:"Community Analytics",description:"Daily activity charts make it easier to spot changes in conversation and membership, with activity tracking noted from the time it is enabled.",icon:"users"}],changes:[{category:"added",items:["Server pulse analytics card in guild settings","14-day daily message activity and member join/leave charts","Server layout view for member, channel, and role counts"]}],commits:[]},{slug:"team-page-ai-name-config",title:"Team Profiles & Custom AI Names",date:"2026-09-22",version:"2.10.0",tags:["team","staff","dashboard","ai","website"],summary:"Niko's public website now introduces the people behind the bot, while server owners can give their AI a custom name and manage its experimental capabilities from the dashboard.",highlights:[{title:"Meet the Niko Team",description:"The new Team page showcases owners, developers, moderators, support staff, and other persisted staff roles with Discord-synced identities, presence, activities, bios, and profile pages.",icon:"users"},{title:"Choose Your AI's Name",description:"Server administrators can configure the AI's display name from the dashboard or the AI configuration command. The chosen name is used for mention detection and reply identity in that server.",icon:"spark"},{title:"Staff Public Listings",description:"Staff members can customize their public bio, banner, and visibility while their name and avatar remain synchronized with Discord.",icon:"settings"}],changes:[{category:"added",items:["Public Team page with persisted staff roles and linked staff profiles","Discord-synced staff presence, current activities, Spotify, streaming, and custom status display","Staff self-service controls for public bio, banner, and Team page visibility","Configurable per-server AI name in the dashboard and AI configuration command","Dashboard controls for AI Actions, Better Context, and Multimodal Conversation experiments","Learn-more dialogs explaining each AI experiment"]},{category:"improved",items:["Dashboard staff workspace navigation and responsive layout","Team profile cards and profile-page activity presentation","AI configuration persistence through the shared database","Public page metadata and favicon handling during the website build"]},{category:"fixed",items:["Team presence labels showing online staff as away","Spotify and streaming activities being hidden behind custom statuses","Staff profile updates being rejected for authorized owners","Staff profile avatars being clipped by profile banners"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Team",value:"1",detail:"new public experience",color:"#66866f"},{label:"AI",value:"4",detail:"new configuration controls",color:"#d96545"},{label:"Profiles",value:"3",detail:"public staff controls",color:"#4a7fb5"}]},commits:[]},{slug:"september-platform-updates",title:"September Platform Updates",date:"2026-09-21",version:"2.9.0",tags:["dashboard","ai","tickets","music","website"],summary:"A broad set of public improvements landed across Niko: richer ticket transcripts, a multimodal AI experiment, more reliable music playback, a redesigned dashboard experience, persistent giveaways and suggestions, and a refreshed public website with dynamic social previews.",highlights:[{title:"More Natural AI Conversations",description:"The new opt-in Multimodal Conversation experiment can understand image attachments and transcribe voice messages before generating a reply, while safely falling back to text when media processing is unavailable.",icon:"spark"},{title:"Richer Ticket Transcripts",description:"Transcript pages and HTML downloads now render Discord custom emojis, stickers, and dynamic timestamps such as <t:1788800225:f> in a more faithful format.",icon:"doc"},{title:"Dashboard & Website Refresh",description:"Dashboard navigation and mobile layouts were refined, documentation was expanded, and public routes now receive route-specific Open Graph cards generated during the build.",icon:"settings"},{title:"Reliable Long-Running Features",description:"Giveaways and suggestions now restore their state from the main database at startup, while music nodes are rescanned periodically to keep playback available.",icon:"utility"}],changes:[{category:"added",items:["Opt-in Multimodal Conversation AI experiment for image understanding and voice-message transcription","Official update notification system with a configurable server notification channel","Discord custom emoji and sticker rendering in ticket transcript pages and HTML downloads","Dynamic Discord timestamp rendering in ticket transcripts","Persistent suggestion configuration and voting buttons restored from the main database","Automatic hourly Lavalink node rescans with a hardcoded fallback node catalog","Additional economy SVG card API endpoints","Community Policy page on the public website","Route-specific Open Graph metadata and generated social preview cards"]},{category:"improved",items:["Dashboard navigation consistency and mobile layout","Dashboard page layout and visual polish","Music connection reliability, autoplay, Spotify playback, and node recovery","Giveaway persistence and startup restoration for MongoDB-backed data","Onboarding setup handling and configuration persistence","Poll command design and interaction flow","Ticket transcript HTML download formatting","Economy image-card font rendering, SVG output, and emoji support","Documentation pages and public website frontend"]},{category:"fixed",items:["Giveaways losing their live buttons after a restart or extended runtime","Suggestion buttons and configuration not surviving process restarts","Ticket transcript rendering for custom media and dynamic timestamps","Lavalink connection failures and stale music nodes","Broken SVG card and SVG endpoint output","Status panel polling noise and retired image-model defaults"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Added",value:"9",detail:"new capabilities",color:"#66866f"},{label:"Improved",value:"9",detail:"upgraded systems",color:"#4a7fb5"},{label:"Fixed",value:"6",detail:"reliability issues",color:"#d96545"}]},commits:["ac102df Fixed the Open Graph image cards","33aaf12 Added dynamic Open Graph tags to the website","3153e28 Rebuilt the frontend","bab665e Added a new Lavalink node","ee44a5e Improved the music cog","bc61e34 Released the new Multimodal Conversation AI experiment","c46af7d Fixed the suggestion system persistence","25703ca Added a broadcast system for official updates and announcements","265bdb2 Added dynamic timestamp rendering inside ticket transcripts","d8005db Added custom emoji and sticker rendering to ticket transcripts","e561d84 Fixed the dashboards navbar","a0bab78 Improved the dashboards mobile layout","fb2f5aa Patched giveaway persistence for MongoDB compatibility","d77779e Fixed several dashboard flaws","b8e06a5 Improved the dashboard pages","3708207 Patched issues in the giveaway and onboarding cogs","d58bb37 Redesigned the poll command","bb523e3 Added a Community Policy page","5b34c7c Updated the documentation pages","3a52fc2 Added new economy card API endpoints","df3ea25 Fixed an issue in the SVG endpoints","39b7340 Fixed an error in the SVG cards","9e3483e Replaced HTML entities with valid XML numeric character references in economy cards"]},{slug:"economy-leveling-overhaul",title:"Economy Items, Leveling Cards & Subcommands",date:"2026-09-08",version:"2.8.0",tags:["economy","leveling","shop","image-cards"],summary:"The economy shop expanded with four new consumable items that affect gameplay — Rigged Coin, Streak Insurance, Double Down Token, and Lucky Horseshoe — plus daily streak milestone bonuses at 7, 14, 30, 60, and 90 days. The leveling system now renders rank cards and leaderboards as customizable image cards, and all leveling commands live under a single `/leveling` group with subcommands.",highlights:[{title:"New Shop Items",description:"Four new consumables: Rigged Coin (60/40 coinflip odds), Streak Insurance (protects daily streak for one missed day), Double Down Token (1.5x gambling payout), and Lucky Horseshoe (+10% work reward).",icon:"chart"},{title:"Leveling Image Cards",description:"Rank cards and the leaderboard now render as styled images with avatar, level, XP bar, and rank. Server admins can customize the card accent color and background gradient.",icon:"spark"},{title:"Leveling Subcommands",description:"All leveling commands reorganized under `/leveling` with `rank`, `leaderboard`, `panel`, and `config` subcommands. The leaderboard now has interactive pagination buttons.",icon:"settings"},{title:"Daily Streak Milestones",description:"Hitting 7, 14, 30, 60, or 90-day daily streaks now awards bonus items from the shop (Espresso Shots, Lockpicks, Lucky Charms, Rob Shields) along with a coin bonus.",icon:"utility"}],changes:[{category:"added",items:["Coinflip command with heads/tails call and double-or-nothing payout","Rigged Coin shop item — gives 60/40 coinflip odds for one use","Streak Insurance shop item — protects daily streak if you miss one day","Double Down Token shop item — next gambling win pays 1.5x","Lucky Horseshoe shop item — next work reward gets +10%","Daily streak milestone bonuses at 7/14/30/60/90 days with item rewards","Image card rendering for `/leveling rank` with customizable accent and background","Image card rendering for the leveling leaderboard","Inventory display as an image card in the shop command","Twemoji emoji rendering in economy card images","Pagination buttons (◀ ▶) on the leveling leaderboard","Card customization fields in the database: card_accent, card_bg_top, card_bg_bottom"]},{category:"improved",items:["Leveling commands restructured as `/leveling rank`, `leaderboard`, `panel`, `config` subcommands","Shop command visual layout with better font rendering on economy image cards","Crime and rob commands now check for gambling_boost effect for 1.5x payout","HTML download format for ticket transcripts","Dashboard UI refinements"]},{category:"fixed",items:["Command name conflicts between leveling and other cogs","Missing import in leveling cog after image card addition","Duplicate command alias in leveling system","Command name conflict in the gambling cog"]}],chart:{type:"bar",title:"New Shop Items & Their Effects",data:[{label:"Rigged Coin",value:3e3,color:"#c9a84c"},{label:"Streak Insurance",value:4e3,color:"#4a7fb5"},{label:"Double Down Token",value:5e3,color:"#d96545"},{label:"Lucky Horseshoe",value:2500,color:"#66866f"}]},commits:["41d86fb Expanded the gambling and economy system","bd6a09c Added image cards to the leveling system","5307bb1 Moved the leveling commands to the levels subcommand","dafd224 Added an image card to the inventory command","49fc83b Added emoji rendering to the shop command","0aca6ba Improved the shop command","30c9735 Added better font rendering to the economy system image cards","2b96835 Fixed a command name conflict","158ad8f Fixed a command name conflict in the gambling cog","d465598 Fixed a missing import","1f24ffb Fixed a duplicate command alias"]},{slug:"database-migration",title:"Database Migration to MongoDB",date:"2026-09-03",version:"2.7.0",tags:["database","mongodb","migration","infrastructure"],summary:"Every major system has been migrated from SQLite to MongoDB. The migration covered economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and the blacklist — with a custom interpreter that translates SQLite-style writes to MongoDB operations.",highlights:[{title:"Full MongoDB Migration",description:"Economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and blacklist now all store data in MongoDB instead of SQLite.",icon:"settings"},{title:"Slash Command Sync Safeguard",description:"A new check prevents redundant Discord API calls when all commands are already registered, reducing rate-limit issues on startup.",icon:"utility"},{title:"Proxy Integration",description:"A new proxy manager reduces downtime on shared hosting environments by routing API requests through a proxy layer.",icon:"shield"}],changes:[{category:"migrated",items:["Economy system — balances, banks, jobs, achievements, inventory","Leveling system — XP, levels, role rewards, card customization","Moderation system — warnings, mutes, automod config","Ticket system — panels, transcripts, support roles","Birthday system — dates, channels, messages","AFK system — status, timestamps","Sticky messages — content, channels","Blacklist — users, words, filters"]},{category:"added",items:["MongoDB interpreter that translates SQLite-style writes to proper MongoDB operations","Proxy manager for shared hosting reliability","Slash command sync safeguard to prevent redundant API calls","Context menu command support in the sync utility"]},{category:"fixed",items:["MongoDB interpreter not translating all SQLite write patterns correctly","Economy interest calculation after migration","Birthday system data persistence","Several database connection issues across various cogs","Leveling database initialization issue"]}],chart:{type:"donut",title:"Systems Migrated to MongoDB",centerLabel:"8 systems",data:[{label:"Economy",value:1,color:"#d96545"},{label:"Leveling",value:1,color:"#66866f"},{label:"Moderation",value:1,color:"#4a7fb5"},{label:"Tickets",value:1,color:"#c9a84c"},{label:"Birthdays",value:1,color:"#b07cc6"},{label:"AFK",value:1,color:"#e0976e"},{label:"Sticky Msgs",value:1,color:"#7ca898"},{label:"Blacklist",value:1,color:"#8c918e"}]},commits:["c07f9b1 Fixed the MongoDB interpreter to properly translate all SQLite database writes","0d3aca5 Migrated the blacklist to the main database","954ebac Migrated the birthday system to the main database","5013d54 Migrated the warns and mutes to use the main database","f29c217 Migrated the afk system to the main database","5732b48 Migrated the sticky messages to use the main database","b0524f1 Migrated the ticket system to the main database","70e6d7a Fixed the sync util to support context commands and slash groups","2c01817 Added a safeguard to prevent slash command syncs when all commands are already present","121afcf Added a proxy integration to reduce downtime on shared hosting","9f2f1fd Fixed several database issues across various cogs"]},{slug:"ticket-system-transcripts",title:"Ticket Transcripts & VoiceMaster",date:"2026-09-03",version:"2.6.0",tags:["tickets","transcripts","voicemaster"],summary:"The ticket system gained a web-based transcript viewer that renders ticket conversations as styled HTML pages. The VoiceMaster was also improved with better reliability and database usage. Ticket transcripts can now be downloaded as HTML or viewed online.",highlights:[{title:"Web Transcript Viewer",description:"Ticket transcripts are now rendered as styled HTML pages that can be viewed online. The HTML download format was also improved for better readability.",icon:"doc"},{title:"VoiceMaster Reliability",description:"The VoiceMaster (temporary voice channels) was improved with better database usage and reliability fixes.",icon:"utility"},{title:"Donation Dashboard Page",description:"A new customization page in the dashboard lets server admins configure donation settings without using commands.",icon:"settings"}],changes:[{category:"added",items:["Web-based ticket transcript viewer with styled HTML output","Ticket transcript database table for storing transcripts online","Dashboard customization page for donation system settings"]},{category:"improved",items:["HTML download format for ticket transcripts","VoiceMaster reliability and database usage patterns","Ticket system persistence and data handling"]},{category:"fixed",items:["Ticket transcript pages rendering incorrectly","Ticket system data loss on restart","Ticket transcript generation issues","Ticket transcript page display bugs"]}],commits:["e953321 Added a new web transcript feature to the ticket system","aa0b73b Improved the donation system and added a customization page to the dashboard","3255385 Improved the html download format for the ticket transcripts","45f1fb0 Fixed the ticket system persistence","ef4e057 Added the ticket system database migrations","d4e0bc8 Fixed the ticket transcripts","4bf5e04 Fixed an issue with the ticket transcript pages","e8dbcb0 Improved the VoiceMaster reliability and improved the database usage"]},{slug:"roleplay-music-status",title:"Roleplay, Music & Status Rotation",date:"2026-09-05",version:"2.5.0",tags:["roleplay","music","status","social"],summary:"The roleplay cog was completely rewritten to use nekos.best API GIFs with CV2 layout messages and a persistent 'hug back' button. The music cog was restructured with a ghost queue feature and fixed autoplay/Spotify playback. A status message rotation system was added with a configurable timer.",highlights:[{title:"Roleplay Rewrite",description:"The roleplay cog now fetches SFW reaction GIFs from nekos.best, renders them in styled CV2 containers, and includes a 'hug back' button that persists across restarts. A single user context menu replaces individual action menus to stay under Discord's 15-command cap.",icon:"users"},{title:"Music Ghost Queue",description:"A new ghost queue feature lets songs be queued even when nothing is currently playing. Autoplay and Spotify playback were also fixed.",icon:"utility"},{title:"Status Rotation",description:"The bot now rotates through configurable status messages on a timer (default 30s interval), with activity types and a VR device presence.",icon:"spark"}],changes:[{category:"added",items:["Status message rotation with configurable interval and activity types","Persistent status panel command for the support server (owner only)","Roleplay block feature to prevent specific users from being targeted","Ghost queue feature — queue songs even when nothing is playing","User context menu for roleplay actions (replaces per-action menus)","YouTube channel name validation for notification system"]},{category:"improved",items:["Roleplay cog complete rewrite — nekos.best GIFs, CV2 layouts, persistent buttons","Social media notification emoji formatting (Bluesky, Reddit, TikTok, Twitch icons)","Music node connection system and autoplay reliability","Spotify playback quality","Music cog restructured with better error handling"]},{category:"fixed",items:["Status rotator startup errors and activity conflicts","on_ready event error handling and reliability","Lavalink connection bug","Roleplay prefix command handling","Bluesky and Reddit notification delivery issues"]}],commits:["0c58178 Redesigned the roleplay cog","6c4ee09 Fixed the roleplay prefix commands","f1f8591 Added a roleplay block feature","e01e3e4 Added status message rotation","5e63e1d Added a persistent status panel","ae7501a Restructured the music cog","526813e Added a new ghost queue feature to the music cog","6524da1 Improved the music node connection system, fixed the autoplay, and fixed the Spotify playback","4264677 Fixed a lavalink connection bug","d62ead8 Improved the social media notification system's emojis","0f0305d Improved the social media notification formatting","42069d4 Added proper channel name validation to the YouTube notification system"]},{slug:"moderation-logging-dashboard",title:"Logging, Moderation & Documentation",date:"2026-09-07",version:"2.4.0",tags:["logging","moderation","documentation","dashboard"],summary:"Logging got two major improvements: deleted message logs now show image attachments in a MediaGallery component, and the Member category now tracks avatar changes using a Section with Thumbnail accessory. The documentation page was fully rebuilt with search, filters, and a card-based layout.",highlights:[{title:"Image Attachments in Logs",description:"Deleted message logs now render attached images in a MediaGallery component inside the log container, so moderators can see what was posted without leaving Discord.",icon:"chart"},{title:"Avatar Change Tracking",description:"The Member logging category now detects avatar changes (global and server avatars) and displays them in a Section with a Thumbnail accessory showing the new avatar.",icon:"users"},{title:"Documentation Redesign",description:"The documentation page was rebuilt from scratch with a search bar, category filters, tag cloud, card-based layout, and individual article pages with table of contents.",icon:"doc"}],changes:[{category:"added",items:["Image attachments rendered in deleted message logs via MediaGallery","Avatar change detection in Member logging with Section + Thumbnail display","Startup economy cache that loads all users into memory for accurate leaderboards","Error handler for role menu post buttons","Full-text search with result highlighting in documentation","Category filters and tag cloud in documentation","Individual documentation article pages with table of contents"]},{category:"improved",items:["Logging system now supports media_urls, thumbnail_url, and files parameters","Commands page expanded with better organization","Dashboard UI refinements","Economy interest feature — skips malformed records with non-integer user IDs"]},{category:"fixed",items:["Logging command issues","Documentation command references","Status device detection issue","Status rotator conflicts between multiple status types","on_ready event reliability with proper error handling"]}],commits:["722a34f Added avatar updates to the logging cogs Member logs","1d82ea1 Moved file attachments inside the main log message for the deleted message logs","358d537 Added a startup economy cache to fix the leaderboard","566e0c4 Improved the dashboard","132bcbb Fully redesigned the documentation page","4f7a89a Improved the commands page","6d953b6 Fixed the logging command","a202687 Fixed some documentation issues","49d22ad Fixed the documentation command references","52de287 Added an error handler to the post role menu button"]},{slug:"website-launch-donation",title:"Website, Donation System & API",date:"2026-09-02",version:"2.3.0",tags:["website","donations","api"],summary:"The public website and documentation portal launched with a React + Vite frontend, documentation center with search, and a commands reference page. The donation system gained a dashboard customization page, and the Flask API backend was fixed to use proper database calls.",highlights:[{title:"Public Website",description:"A complete public website built with React and Vite featuring a landing page, documentation center, command reference, dashboard, and legal pages.",icon:"spark"},{title:"Documentation Center",description:"The documentation page was redesigned with a card-based layout, individual article pages, and a modern visual design matching the bot's aesthetic.",icon:"doc"},{title:"Donation Dashboard",description:"Server admins can now configure donation settings through a new dashboard page instead of relying solely on commands.",icon:"settings"}],changes:[{category:"added",items:["Public website with landing page, documentation center, and command reference","Donation system customization page in the dashboard","Ticket transcript viewer web page","Donate page with Oxapay integration"]},{category:"improved",items:["Flask API to use proper database calls instead of direct SQLite access","Website commands page with expanded details","Database layer reliability for production"]},{category:"fixed",items:["Flask API database call issues","Several database-related bugs across cogs","node_modules folder accidentally committed to repository"]}],commits:["132bcbb Fully redesigned the documentation page","aa0b73b Improved the donation system and added a customization page to the dashboard","bd5e3be Expanded the website's commands page","e266644 Fixed the flask API to use the proper database calls","e99ed47 Fixed several database related issues","c783514 Minor API fixes and improvements","0df4478 Added the node_modules folder to the gitignore file"]}];function SS(t){return Ma.find(s=>s.slug===t)}function NS(){const t=new Set;return Ma.forEach(s=>s.tags.forEach(r=>t.add(r))),Array.from(t).sort()}function CS(){const[t,s]=T.useState(""),r=NS(),o=t?Ma.filter(c=>c.tags.includes(t)):Ma;return i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"home"}),i.jsxs("main",{className:"shell page-main changelog-page",children:[i.jsxs("div",{className:"changelog-hero",children:[i.jsxs("div",{className:"eyebrow",children:[i.jsx("span",{className:"status-dot"})," What's new"]}),i.jsxs("h1",{className:"changelog-title",children:["Changelog",i.jsx("br",{}),i.jsx("span",{className:"title-accent",children:"& updates"})]}),i.jsx("p",{className:"changelog-subtitle",children:"A record of every improvement, fix, and new feature added to Niko. Grouped by release for clarity."})]}),i.jsxs("div",{className:"changelog-tags",children:[i.jsx("button",{className:`changelog-tag-btn ${t===""?"active":""}`,onClick:()=>s(""),children:"All"}),r.slice(0,12).map(c=>i.jsx("button",{className:`changelog-tag-btn ${t===c?"active":""}`,onClick:()=>s(c),children:c},c))]}),i.jsx("div",{className:"changelog-timeline",children:o.map((c,d)=>i.jsxs("article",{className:"changelog-entry",children:[i.jsxs("div",{className:"changelog-entry-date-col",children:[i.jsx("div",{className:"changelog-date-dot"}),d<o.length-1&&i.jsx("div",{className:"changelog-date-line"})]}),i.jsxs("div",{className:"changelog-entry-card",children:[i.jsxs("div",{className:"changelog-entry-header",children:[i.jsxs("div",{className:"changelog-entry-meta",children:[i.jsx("time",{className:"changelog-entry-date",children:new Date(c.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),c.version&&i.jsxs("span",{className:"changelog-version",children:["v",c.version]})]}),i.jsx("h2",{className:"changelog-entry-title",children:c.title}),i.jsx("p",{className:"changelog-entry-summary",children:c.summary})]}),i.jsx("div",{className:"changelog-entry-highlights",children:c.highlights.slice(0,2).map(h=>i.jsxs("div",{className:"changelog-highlight-mini",children:[i.jsx("span",{className:"highlight-mini-icon",children:i.jsx(X,{name:h.icon,size:16})}),i.jsxs("div",{children:[i.jsx("strong",{children:h.title}),i.jsxs("p",{children:[h.description.slice(0,120),"..."]})]})]},h.title))}),i.jsx("div",{className:"changelog-entry-tags",children:c.tags.map(h=>i.jsx("span",{className:"changelog-tag",children:h},h))}),i.jsxs("button",{className:"changelog-read-more",onClick:()=>{pe(`/changelog/${c.slug}`)},children:["Read full release notes ",i.jsx(X,{name:"arrow",size:14})]})]})]},c.slug))}),o.length===0&&i.jsxs("div",{className:"changelog-empty",children:[i.jsx(X,{name:"doc",size:40}),i.jsx("p",{children:"No changelog entries match this filter."})]})]}),i.jsx(St,{})]})}function TS({slug:t}){const s=SS(t);return s?i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"home"}),i.jsxs("main",{className:"shell page-main changelog-page changelog-detail",children:[i.jsx("div",{className:"changelog-back",children:i.jsxs("button",{onClick:()=>pe("/changelog"),className:"back-button",children:[i.jsx(X,{name:"arrow",size:16}),"Back to Changelog"]})}),i.jsxs("header",{className:"changelog-detail-header",children:[i.jsxs("div",{className:"changelog-detail-meta",children:[i.jsx("time",{children:new Date(s.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),s.version&&i.jsxs("span",{className:"changelog-version",children:["v",s.version]})]}),i.jsx("h1",{children:s.title}),i.jsx("p",{className:"changelog-detail-summary",children:s.summary}),i.jsx("div",{className:"changelog-detail-tags",children:s.tags.map(r=>i.jsx("span",{className:"changelog-tag",children:r},r))})]}),i.jsxs("section",{className:"changelog-highlights-section",children:[i.jsx("h2",{className:"changelog-section-heading",children:"Highlights"}),i.jsx("div",{className:"changelog-highlights-grid",children:s.highlights.map(r=>i.jsxs("div",{className:"changelog-highlight-card",children:[i.jsx("span",{className:"highlight-icon",children:i.jsx(X,{name:r.icon,size:22})}),i.jsx("h3",{children:r.title}),i.jsx("p",{children:r.description})]},r.title))})]}),s.chart&&i.jsx(PS,{chart:s.chart}),i.jsxs("section",{className:"changelog-changes-section",children:[i.jsx("h2",{className:"changelog-section-heading",children:"All Changes"}),i.jsx("div",{className:"changelog-changes-grid",children:s.changes.map(r=>i.jsxs("div",{className:`changelog-change-group changelog-change-${r.category}`,children:[i.jsx("h3",{className:"change-group-title",children:i.jsx("span",{className:`change-badge change-badge-${r.category}`,children:r.category})}),i.jsx("ul",{children:r.items.map((o,c)=>i.jsx("li",{children:o},c))})]},r.category))})]}),s.commits.length>0&&i.jsxs("section",{className:"changelog-commits-section",children:[i.jsx("h2",{className:"changelog-section-heading",children:"Commits"}),i.jsx("div",{className:"changelog-commits-list",children:s.commits.map(r=>{const[o,...c]=r.split(" ");return i.jsxs("div",{className:"changelog-commit",children:[i.jsx("code",{className:"commit-hash",children:o.slice(0,7)}),i.jsx("span",{className:"commit-msg",children:c.join(" ")})]},o)})})]}),i.jsx("nav",{className:"changelog-detail-nav",children:i.jsxs("button",{onClick:()=>pe("/changelog"),children:[i.jsx(X,{name:"arrow",size:14}),"All releases"]})})]}),i.jsx(St,{})]}):i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"home"}),i.jsx("main",{className:"shell page-main changelog-page",children:i.jsxs("div",{className:"changelog-not-found",children:[i.jsx(X,{name:"doc",size:48}),i.jsx("h1",{children:"Entry Not Found"}),i.jsxs("p",{children:[`We couldn't find a changelog entry for "`,t,'".']}),i.jsx("button",{onClick:()=>pe("/changelog"),children:"View all changelog entries"})]})}),i.jsx(St,{})]})}function PS({chart:t}){return i.jsxs("section",{className:"changelog-chart-section",children:[i.jsx("h2",{className:"changelog-section-heading",children:t.title}),i.jsxs("div",{className:"changelog-chart-container",children:[t.type==="bar"&&i.jsx(AS,{chart:t}),t.type==="pie"&&i.jsx(ES,{chart:t}),t.type==="donut"&&i.jsx(MS,{chart:t}),t.type==="line"&&i.jsx(_S,{chart:t}),t.type==="timeline"&&i.jsx(DS,{chart:t}),t.type==="comparison"&&i.jsx(LS,{chart:t}),t.type==="metrics"&&i.jsx(RS,{chart:t})]})]})}function AS({chart:t}){const s=Math.max(...t.data.map(r=>r.value));return i.jsx("div",{className:"chart-bar",children:t.data.map(r=>i.jsxs("div",{className:"chart-bar-row",children:[i.jsx("span",{className:"chart-bar-label",children:r.label}),i.jsxs("div",{className:"chart-bar-track",children:[i.jsx("div",{className:"chart-bar-fill",style:{width:`${r.value/s*100}%`,background:r.color||"var(--accent)"}}),i.jsx("span",{className:"chart-bar-value",children:r.value})]})]},r.label))})}function ES({chart:t}){const s=t.data.reduce((d,h)=>d+h.value,0);let r=0;const c=t.data.map(d=>{const h=r/s*360;r+=d.value;const p=r/s*360;return{...d,start:h,end:p}}).map(d=>{const h=d.start/360*100,p=d.end/360*100;return`${d.color||"#d96545"} ${h}% ${p}%`}).join(", ");return i.jsxs("div",{className:"chart-pie-wrapper",children:[i.jsx("div",{className:"chart-pie",style:{background:`conic-gradient(${c})`}}),i.jsx("div",{className:"chart-pie-legend",children:t.data.map(d=>i.jsxs("div",{className:"chart-legend-item",children:[i.jsx("span",{className:"chart-legend-dot",style:{background:d.color||"var(--accent)"}}),i.jsx("span",{className:"chart-legend-label",children:d.label})]},d.label))})]})}function MS({chart:t}){const s=t.data.reduce((o,c)=>o+c.value,0),r=t.data.reduce((o,c)=>{const d=o.current/s*100,h=(o.current+c.value)/s*100;return o.css+=`${c.color||"#d96545"} ${d}% ${h}%, `,o.current+=c.value,o},{css:"",current:0}).css.slice(0,-2);return i.jsxs("div",{className:"chart-donut-wrapper",children:[i.jsx("div",{className:"chart-donut",style:{background:`conic-gradient(${r})`},children:i.jsx("span",{children:t.centerLabel||s})}),i.jsx("div",{className:"chart-pie-legend",children:t.data.map(o=>i.jsxs("div",{className:"chart-legend-item",children:[i.jsx("span",{className:"chart-legend-dot",style:{background:o.color||"var(--accent)"}}),i.jsx("span",{className:"chart-legend-label",children:o.label})]},o.label))})]})}function _S({chart:t}){const s=Math.max(...t.data.map(o=>o.value),1),r=t.data.map((o,c)=>{const d=t.data.length===1?50:c/(t.data.length-1)*100,h=100-o.value/s*82-9;return`${d},${h}`}).join(" ");return i.jsxs("div",{className:"chart-line-wrapper",children:[i.jsxs("svg",{className:"chart-line",viewBox:"0 0 100 100",preserveAspectRatio:"none",role:"img","aria-label":t.title,children:[i.jsx("polyline",{points:r,fill:"none",stroke:"var(--accent)",strokeWidth:"3",vectorEffect:"non-scaling-stroke"}),t.data.map((o,c)=>{const d=t.data.length===1?50:c/(t.data.length-1)*100,h=100-o.value/s*82-9;return i.jsx("circle",{cx:d,cy:h,r:"3",fill:"var(--accent)",vectorEffect:"non-scaling-stroke"},o.label)})]}),i.jsx("div",{className:"chart-line-labels",children:t.data.map(o=>i.jsx("span",{children:o.label},o.label))})]})}function DS({chart:t}){const s=Math.max(...t.data.map(r=>r.value),1);return i.jsx("div",{className:"chart-timeline",children:t.data.map(r=>i.jsxs("div",{className:"chart-timeline-item",children:[i.jsx("div",{className:"chart-timeline-marker",style:{background:r.color||"var(--accent)"}}),i.jsxs("div",{className:"chart-timeline-content",children:[i.jsx("strong",{children:r.label}),i.jsx("div",{className:"chart-timeline-track",children:i.jsx("div",{className:"chart-timeline-fill",style:{width:`${r.value/s*100}%`,background:r.color||"var(--accent)"}})}),r.detail&&i.jsx("span",{children:r.detail})]})]},r.label))})}function RS({chart:t}){return i.jsx("div",{className:"chart-metrics",children:t.data.map(s=>i.jsxs("div",{className:"chart-metric",style:{borderTopColor:s.color||"var(--accent)"},children:[i.jsx("span",{className:"chart-metric-label",children:s.label}),i.jsx("strong",{children:s.value}),s.detail&&i.jsx("small",{children:s.detail})]},s.label))})}function LS({chart:t}){const s=Math.max(...t.before.concat(t.after).map(o=>o.value),1),r=(o,c,d)=>i.jsxs("div",{className:"chart-comparison-col",children:[i.jsx("h4",{className:`comparison-label ${d}`,children:o}),c.map(h=>i.jsxs("div",{className:"chart-bar-row",children:[i.jsx("span",{className:"chart-bar-label",children:h.label}),i.jsxs("div",{className:"chart-bar-track",children:[i.jsx("div",{className:"chart-bar-fill",style:{width:`${h.value/s*100}%`,background:h.color||"var(--accent)"}}),i.jsx("span",{className:"chart-bar-value",children:h.value})]})]},h.label))]});return i.jsxs("div",{className:"chart-comparison",children:[r("Before",t.before,"comparison-before"),i.jsx("div",{className:"chart-comparison-divider",children:i.jsx(X,{name:"arrow",size:20})}),r("After",t.after,"comparison-after")]})}function _a(t){return t.avatar_url}function IS(t){return`https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/svg/${Array.from(t).map(r=>r.codePointAt(0).toString(16)).join("-")}.svg`}function VS({emoji:t}){return t?t.kind==="custom"?i.jsx("img",{className:"presence-emoji",src:`https://cdn.discordapp.com/emojis/${t.value}.${t.animated?"gif":"png"}?size=18`,alt:t.name||"custom emoji"}):i.jsx("img",{className:"presence-emoji",src:IS(t.value),alt:t.name||t.value}):null}function FS(t){return{playing:"Playing",listening:"Listening to",watching:"Watching",streaming:"Streaming",competing:"Competing in"}[t]||(t?`${t.charAt(0).toUpperCase()}${t.slice(1)}`:"Activity")}function BS({activity:t}){const s=t.kind==="spotify",r=s?"Listening on Spotify":FS(t.type),o=s?t.details||"Spotify":t.name,c=(s?[t.state]:[t.details,t.state]).filter(h=>!!(h&&h!==o)),d=i.jsxs("span",{className:`activity-card activity-${t.kind}`,children:[t.image_url&&i.jsx("img",{className:"activity-art",src:t.image_url,alt:""}),i.jsxs("span",{className:"activity-copy",children:[i.jsx("strong",{children:r}),i.jsx("span",{children:o}),c.map((h,p)=>i.jsx("small",{children:h},`${h}-${p}`))]})]});return t.url?i.jsx("a",{className:"presence-activity",href:t.url,target:"_blank",rel:"noreferrer",children:d}):i.jsx("span",{className:"presence-activity",children:d})}function OS(t){return t.status_label||{online:"Online",idle:"Idle",dnd:"Do Not Disturb",offline:"Offline"}[t.status||"offline"]||"Offline"}function zS({member:t}){const s=t.custom_status,r=t.activities||[],o=!!(s!=null&&s.text||s!=null&&s.emoji);return!o&&!r.length?null:i.jsxs("span",{className:"presence-stack",children:[o&&i.jsxs("span",{className:"presence-line",children:[i.jsx(VS,{emoji:s==null?void 0:s.emoji}),(s==null?void 0:s.text)||"Custom status"]}),r.length>0&&i.jsx("span",{className:"presence-line activity-list",children:r.map((c,d)=>i.jsx(BS,{activity:c},`${c.kind}-${c.name}-${d}`))})]})}const wy=`
.team-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));align-items:start;gap:14px;margin-top:58px}.team-card{display:flex;flex-direction:column;min-width:0;overflow:hidden;padding:0;color:var(--ink);text-align:left;background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow-soft)}.team-card:hover{border-color:#dfaa98;transform:translateY(-2px)}.team-card-art,.team-profile-banner{min-height:105px;background:linear-gradient(135deg,var(--callout),var(--surface-muted));background-size:cover;background-position:center}.team-card-body{display:flex;align-items:flex-start;flex:1;min-width:0;gap:14px;padding:18px}.team-card-body>div:last-child{min-width:0}.team-card h2,.team-card p{overflow-wrap:anywhere}.team-avatar,.team-profile-avatar{display:grid;place-items:center;flex:0 0 auto;overflow:hidden;color:#fffaf5;background:var(--accent);border-radius:50%;font-weight:800;object-fit:cover}.team-avatar{width:56px;height:56px;margin-top:-39px;border:3px solid var(--surface)}.team-role{color:var(--accent-dark);text-transform:uppercase;letter-spacing:.1em;font:700 9px "Space Mono",monospace}.team-card h2{margin:5px 0 6px;font-size:17px}.team-card p{margin:0 0 10px;color:var(--muted);font-size:11px;line-height:1.6}.team-status{color:var(--dim);font-size:10px}.presence-stack{display:block}.presence-stack>.presence-line+.presence-line{margin-top:12px}.presence-line{display:flex;align-items:center;flex-wrap:wrap;gap:7px;margin-top:7px;color:var(--muted);font-size:10px}.presence-activity{display:inline-flex;align-items:center;gap:4px;color:inherit}.presence-activity:hover{text-decoration:none}.activity-card{display:flex;align-items:center;min-width:0;gap:8px;padding:7px 9px;background:var(--surface-muted);border:1px solid var(--line);border-radius:8px;text-align:left}.activity-art{width:30px;height:30px;flex:0 0 auto;border-radius:5px;object-fit:cover}.activity-copy{display:flex;min-width:0;flex-direction:column;gap:1px}.activity-copy strong{color:var(--accent-dark);font-size:9px;text-transform:uppercase;letter-spacing:.06em}.activity-copy span,.activity-copy small{overflow:hidden;max-width:210px;text-overflow:ellipsis;white-space:nowrap}.activity-copy span{color:var(--ink);font-size:10px}.activity-copy small{color:var(--dim);font-size:9px}.presence-emoji{width:18px;height:18px;object-fit:contain;vertical-align:middle}.is-online{color:var(--sage)}.team-profile-page{max-width:760px}.team-back{width:auto;margin:0 0 18px;border:0;background:transparent}.team-profile-banner{min-height:220px;border:1px solid var(--line);border-radius:14px 14px 0 0}.team-profile-card{padding:0 34px 38px;text-align:center;background:var(--surface);border:1px solid var(--line);border-top:0;border-radius:0 0 14px 14px;box-shadow:var(--shadow-soft)}.team-profile-avatar{width:100px;height:100px;margin:-50px auto 6px;border:5px solid var(--surface);font-size:32px;transform:translateY(-20px)}.team-profile-card h1{margin:8px 0 5px;font-size:34px;letter-spacing:-.07em}.team-profile-handle{color:var(--dim);font-size:11px}.team-profile-bio{max-width:560px;margin:27px auto 0;color:var(--muted);line-height:1.8}.team-profile-links{display:flex;justify-content:center;flex-wrap:wrap;gap:9px;margin:20px auto 0}.team-profile-links a{display:inline-flex;align-items:center;gap:7px;padding:9px 13px;color:var(--accent-dark);background:var(--surface-muted);border:1px solid var(--line);border-radius:999px;font-size:11px;font-weight:700;transition:background .18s,border-color .18s,transform .18s}.team-profile-links a:hover{background:var(--filter-active);border-color:var(--filter-border);transform:translateY(-1px)}.team-activity{display:block;width:min(100%,560px);margin:20px auto 0;padding:12px;color:var(--muted);background:var(--surface-muted);border:1px solid var(--line);border-radius:12px;font-size:10px;text-align:left}.team-activity .presence-line{margin-top:0}.team-activity .activity-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));align-items:stretch}.team-activity .activity-card{height:100%;width:100%}@media(max-width:800px){.team-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.team-grid{grid-template-columns:1fr;margin-top:38px}.team-profile-card{padding-left:18px;padding-right:18px}.team-profile-banner{min-height:150px}}`,ky=5e3;function US(){const[t,s]=T.useState([]);return T.useEffect(()=>{let r=!0;const o=()=>{_x().then(h=>{r&&s(h)}).catch(()=>{})},c=()=>{document.visibilityState==="visible"&&o()};o();const d=window.setInterval(()=>{document.visibilityState==="visible"&&o()},ky);return document.addEventListener("visibilitychange",c),()=>{r=!1,window.clearInterval(d),document.removeEventListener("visibilitychange",c)}},[]),i.jsxs(i.Fragment,{children:[i.jsx("style",{children:wy}),i.jsx(Oe,{page:"team"}),i.jsxs("main",{className:"shell page-main",children:[i.jsxs("div",{className:"page-heading",children:[i.jsx("div",{className:"eyebrow",children:"The people behind Niko"}),i.jsx("h1",{children:"Meet the team."}),i.jsx("p",{children:"A small group of builders, moderators, and creative minds keeping Niko friendly, useful, and moving forward."})]}),i.jsxs("div",{className:"team-grid",children:[t.map(r=>i.jsxs("button",{className:"team-card",onClick:()=>pe(`/team/${r.id}`),children:[i.jsx("div",{className:"team-card-art",style:r.public_banner_url?{backgroundImage:`url(${r.public_banner_url})`}:void 0}),i.jsxs("div",{className:"team-card-body",children:[_a(r)?i.jsx("img",{className:"team-avatar",src:_a(r),alt:""}):i.jsx("span",{className:"team-avatar team-avatar-fallback",children:r.name.slice(0,1)}),i.jsxs("div",{children:[i.jsx("span",{className:"team-role",children:r.role_label}),i.jsx("h2",{children:r.name}),i.jsx("p",{children:r.bio||"Part of the Niko team."})]})]})]},r.id)),!t.length&&i.jsx("div",{className:"empty-state",children:"The team roster is being prepared."})]})]}),i.jsx(St,{})]})}function WS({id:t}){const[s,r]=T.useState(null),[o,c]=T.useState("");return T.useEffect(()=>{let d=!0;const h=(v=!1)=>{Dx(t).then(g=>{d&&(r(g),c(""))}).catch(g=>{d&&v&&c(g instanceof Error?g.message:"Team member not found.")})},p=()=>{document.visibilityState==="visible"&&h()};h(!0);const f=window.setInterval(()=>{document.visibilityState==="visible"&&h()},ky);return document.addEventListener("visibilitychange",p),()=>{d=!1,window.clearInterval(f),document.removeEventListener("visibilitychange",p)}},[t]),i.jsxs(i.Fragment,{children:[i.jsx("style",{children:wy}),i.jsx(Oe,{page:"team"}),i.jsx("main",{className:"shell page-main team-profile-page",children:o?i.jsx("div",{className:"empty-state",children:o}):s?i.jsxs(i.Fragment,{children:[i.jsx("button",{className:"back-link team-back",onClick:()=>pe("/team"),children:"← Back to team"}),i.jsx("div",{className:"team-profile-banner",style:s.public_banner_url?{backgroundImage:`url(${s.public_banner_url})`}:void 0}),i.jsxs("section",{className:"team-profile-card",children:[_a(s)?i.jsx("img",{className:"team-profile-avatar",src:_a(s),alt:""}):i.jsx("span",{className:"team-profile-avatar team-avatar-fallback",children:s.name.slice(0,1)}),i.jsx("div",{className:"team-role",children:s.role_label}),i.jsx("h1",{children:s.name}),i.jsxs("p",{className:"team-profile-handle",children:[s.username?`@${s.username}`:"Niko staff"," · ",i.jsx("span",{className:`status-${s.status||"offline"} ${s.status==="online"?"is-online":""}`,children:OS(s)})]}),i.jsx("p",{className:"team-profile-bio",children:s.bio||"This team member has not added an extended introduction yet."}),(s.public_links||[]).length>0&&i.jsx("nav",{className:"team-profile-links","aria-label":`${s.name}'s links`,children:(s.public_links||[]).map((d,h)=>i.jsxs("a",{href:d.url,target:"_blank",rel:"noopener noreferrer",children:[d.label||d.type," ",i.jsx("span",{"aria-hidden":"true",children:"↗"})]},`${d.type}-${h}`))}),i.jsxs("div",{className:"team-activity",children:[i.jsx(zS,{member:s}),!s.custom_status&&!(s.activities||[]).length&&"No current activity"]})]})]}):i.jsx("div",{className:"section-loading",children:"Loading profile…"})}),i.jsx(St,{})]})}const $S=[["website","Website"],["github","GitHub"],["instagram","Instagram"],["x","X"],["tiktok","TikTok"],["youtube","YouTube"],["twitch","Twitch"],["bluesky","Bluesky"],["linkedin","LinkedIn"],["reddit","Reddit"],["mastodon","Mastodon"],["facebook","Facebook"],["discord","Discord"],["other","Other"]];function HS(){const[t,s]=T.useState(null),[r,o]=T.useState(null),[c,d]=T.useState(null),[h,p]=T.useState([]),[f,v]=T.useState({public_bio:"",public_banner_url:"",public_visible:!0}),[g,x]=T.useState([]),[b,j]=T.useState({avatar_url:"",banner_url:""}),[k,S]=T.useState(""),[N,O]=T.useState(""),[M,L]=T.useState(!1),[I,D]=T.useState(!1);if(T.useEffect(()=>{Promise.all([fa(),dc(),ga(),hc()]).then(([Q,E,H,W])=>{s(Q),o(E),d(H),p(W),v({public_bio:E.profile.bio||"",public_banner_url:E.profile.public_banner_url||"",public_visible:E.profile.visible!==!1}),x(E.profile.public_links||[])}).catch(Q=>O(Q instanceof Error?Q.message:"Staff access unavailable."))},[]),!t||!r&&!N)return i.jsxs("div",{className:"dashboard-state",children:[i.jsx("div",{className:"loading-ring"}),i.jsx("p",{children:"Checking staff access…"})]});if(N||!r||!t.authenticated)return i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"dashboard"}),i.jsx("main",{className:"auth-page",children:i.jsxs("div",{className:"auth-card",children:[i.jsx("div",{className:"eyebrow",children:"Staff workspace"}),i.jsx("h1",{children:"Private team area."}),i.jsx("p",{children:t!=null&&t.authenticated?N||"This area is only available to official Niko staff.":"Sign in with Discord to continue."}),!(t!=null&&t.authenticated)&&i.jsx("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard/staff",children:"Continue with Discord"}),i.jsx("button",{className:"back-link",onClick:()=>pe("/dashboard"),children:"Return to dashboard"})]})})]});const B=t.user,V=`https://cdn.discordapp.com/embed/avatars/${Number(BigInt(B.id)%5n)}.png`,z=B.avatar?`https://cdn.discordapp.com/avatars/${B.id}/${B.avatar}.png?size=128`:V,re=["owner","head_admin","graphic_designer"].includes(r.role),Y=(Q,E)=>v(H=>({...H,[Q]:E})),ce=()=>x(Q=>Q.length<10?[...Q,{type:"",url:""}]:Q),ue=(Q,E,H)=>{x(W=>W.map((P,U)=>U===Q?{...P,[E]:H}:P))},ie=Q=>x(E=>E.filter((H,W)=>W!==Q)),Se=async()=>{if(M)return;const Q=g.filter(E=>E.type.trim()||E.url.trim());if(Q.some(E=>!E.type.trim()||!E.url.trim())){O("Choose a link type and enter its URL, or remove the unfinished link."),S("");return}L(!0),O(""),S("");try{await Rx({...f,public_links:Q},t.csrf_token),S("Your public team listing was saved.")}catch(E){O(E instanceof Error?E.message:"Could not save listing.")}finally{L(!1)}},De=async()=>{if(!I){D(!0),O(""),S("");try{await Lx(b,t.csrf_token),S("Niko's global profile was updated.")}catch(Q){O(Q instanceof Error?Q.message:"Could not update global profile.")}finally{D(!1)}}},Pe=i.jsxs("div",{className:"staff-page",children:[i.jsxs("header",{className:"staff-heading",children:[i.jsxs("div",{children:[i.jsx("div",{className:"eyebrow",children:"Staff workspace"}),i.jsx("h1",{children:"Shape your presence."}),i.jsxs("p",{children:["Manage the public details granted to your ",i.jsx("strong",{children:r.role_label})," role. Your name and avatar always come directly from Discord."]})]}),i.jsxs("div",{className:"staff-role-card",children:[i.jsx("span",{className:"staff-role-mark",children:i.jsx("img",{src:z,alt:"Your Discord profile",onError:Q=>{Q.currentTarget.onerror=null,Q.currentTarget.src=V}})}),i.jsxs("span",{children:[i.jsx("small",{children:"Signed in as"}),i.jsx("strong",{children:r.role_label})]})]})]}),i.jsxs("div",{className:"staff-layout",children:[i.jsxs("section",{className:"staff-panel staff-panel-main",children:[i.jsxs("div",{className:"staff-panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Public listing"}),i.jsx("h2",{children:"How the team sees you"}),i.jsx("p",{children:"Keep your introduction current while Discord remains the source of truth for your identity."})]}),i.jsx("span",{className:"staff-step",children:"01"})]}),i.jsxs("div",{className:"staff-fields",children:[i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Banner URL"}),i.jsx("input",{type:"url",value:f.public_banner_url,onChange:Q=>Y("public_banner_url",Q.target.value),placeholder:"https://…"}),i.jsx("small",{children:"Use a publicly reachable image. Leave blank for no banner."})]}),i.jsxs("section",{className:"staff-links-section","aria-labelledby":"staff-links-heading",children:[i.jsxs("div",{className:"staff-links-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"form-label",id:"staff-links-heading",children:"Links"}),i.jsx("small",{children:"Add up to 10 links. They appear on your profile, not the team overview card."})]}),i.jsxs("span",{className:"staff-links-count",children:[g.length,"/10"]})]}),i.jsx("div",{className:"staff-link-list",children:g.map((Q,E)=>i.jsxs("div",{className:"staff-link-row",children:[i.jsxs("label",{className:"form-field staff-link-type",children:[i.jsxs("span",{className:"sr-only",children:["Link ",E+1," type"]}),i.jsxs("select",{value:Q.type,onChange:H=>ue(E,"type",H.target.value),children:[i.jsx("option",{value:"",children:"Choose link type…"}),$S.map(([H,W])=>i.jsx("option",{value:H,children:W},H))]})]}),i.jsxs("label",{className:"form-field staff-link-url",children:[i.jsxs("span",{className:"sr-only",children:["Link ",E+1," URL"]}),i.jsx("input",{type:"url",value:Q.url,onChange:H=>ue(E,"url",H.target.value),placeholder:"https://…"})]}),i.jsx("button",{type:"button",className:"staff-link-remove",onClick:()=>ie(E),"aria-label":`Remove link ${E+1}`,children:"Remove"})]},`profile-link-${E}`))}),i.jsx("button",{type:"button",className:"button button-muted staff-add-link",onClick:ce,disabled:g.length>=10,children:"＋ Add link"})]}),i.jsxs("label",{className:"form-field staff-bio-field",children:[i.jsx("span",{className:"form-label",children:"Extended introduction"}),i.jsx("textarea",{value:f.public_bio,onChange:Q=>Y("public_bio",Q.target.value),maxLength:1200,placeholder:"Tell the community what you do…"}),i.jsxs("small",{children:[f.public_bio.length,"/1200 characters"]})]})]}),i.jsxs("label",{className:"setting-row staff-visibility",children:[i.jsxs("span",{children:[i.jsx("strong",{children:"Show me on the public Team page"}),i.jsx("small",{children:"Hide your listing without removing your staff access."})]}),i.jsx("input",{type:"checkbox",checked:f.public_visible,onChange:Q=>Y("public_visible",Q.target.checked)}),i.jsx("i",{})]}),i.jsxs("div",{className:"staff-panel-footer",children:[i.jsx("span",{children:"Changes apply immediately to your public profile."}),i.jsx("button",{type:"button",className:"button button-primary",onClick:Se,disabled:M,children:M?"Saving…":"Save public listing"})]})]}),i.jsxs("aside",{className:"staff-sidebar-card",children:[i.jsx("span",{className:"panel-kicker",children:"Profile rules"}),i.jsx("h3",{children:"Stay consistent with Discord"}),i.jsx("p",{children:"Your global display name and profile picture sync automatically, so updates made in Discord are reflected here without another form."}),i.jsxs("div",{className:"staff-rule",children:[i.jsx("span",{children:"Identity"}),i.jsx("strong",{children:"Discord synced"})]}),i.jsxs("div",{className:"staff-rule",children:[i.jsx("span",{children:"Editable"}),i.jsx("strong",{children:"Bio · banner · links · visibility"})]})]})]}),re&&i.jsxs("section",{className:"staff-panel staff-global-panel",children:[i.jsxs("div",{className:"staff-panel-heading",children:[i.jsxs("div",{children:[i.jsx("span",{className:"panel-kicker",children:"Graphic direction"}),i.jsx("h2",{children:"Global Niko profile"}),i.jsx("p",{children:"Reserved for Graphic Designers, Head Admins, and owners. Paste publicly reachable image URLs."})]}),i.jsx("span",{className:"staff-step",children:"02"})]}),i.jsxs("div",{className:"staff-fields staff-fields-two",children:[i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Bot avatar URL"}),i.jsx("input",{value:b.avatar_url,onChange:Q=>j({...b,avatar_url:Q.target.value}),placeholder:"https://…"})]}),i.jsxs("label",{className:"form-field",children:[i.jsx("span",{className:"form-label",children:"Bot banner URL"}),i.jsx("input",{value:b.banner_url,onChange:Q=>j({...b,banner_url:Q.target.value}),placeholder:"https://…"})]})]}),i.jsxs("div",{className:"staff-panel-footer",children:[i.jsx("span",{children:"Updates the bot-wide Discord profile."}),i.jsx("button",{type:"button",className:"button button-primary",onClick:De,disabled:I,children:I?"Updating…":"Update global profile"})]})]}),k&&i.jsx("div",{className:"notice",children:k}),N&&i.jsx("div",{className:"notice warning",children:N})]});return i.jsx(Mf,{user:t.user,guilds:h,selectedGuild:null,view:"overview",section:"overview",stats:c,staffRole:r.role,onHome:()=>pe(Es()),onServers:()=>pe(mc()),onGuildChange:()=>{},onSectionChange:()=>{},onRefresh:()=>window.location.reload(),refreshing:!1,children:Pe})}function GS(){var z,re;const[t,s]=T.useState(null),[r,o]=T.useState(null),[c,d]=T.useState([]),[h,p]=T.useState({}),[f,v]=T.useState(!0),[g,x]=T.useState(""),[b,j]=T.useState(!1),[k,S]=T.useState(!1),N=_n(),O=window.location.pathname.split("/").filter(Boolean),M=O[1]||"",L=O[2]||"",I=window.location.pathname;T.useEffect(()=>{let Y=!0;return v(!0),x(""),fa().then(ce=>{if(Y&&(s(ce),!!ce.authenticated))return L?$x(M,L).then(ue=>{Y&&o(ue)}):Wx(M).then(ue=>{Y&&d(ue.openings)})}).catch(ce=>{Y&&x(ce instanceof Error?ce.message:"The application could not be loaded.")}).finally(()=>{Y&&v(!1)}),()=>{Y=!1}},[M,L]);const D=Y=>{Y.preventDefault(),r&&(S(!0),x(""),Hx(M,r.id,h,t==null?void 0:t.csrf_token).then(()=>j(!0)).catch(ce=>x(ce instanceof Error?ce.message:"Your application could not be submitted.")).finally(()=>S(!1)))},B=`/auth/login?next=${encodeURIComponent(I)}`,V=(r==null?void 0:r.guild_name)||"the server";return i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"dashboard"}),i.jsx("main",{className:"application-public-page",children:i.jsxs("div",{className:"application-public-shell",children:[i.jsx("a",{className:"application-back-link",href:"/",onClick:Y=>{Y.preventDefault(),pe("/")},children:"← Back to Niko"}),i.jsxs("div",{className:"application-public-brand",children:[i.jsx("span",{className:"application-public-mark",children:"n"}),i.jsxs("span",{children:["TEAM APPLICATIONS ",i.jsx("small",{children:"POWERED BY NIKO"})]})]}),i.jsx("div",{className:"application-public-card",children:f?i.jsxs("div",{className:"application-public-state",children:[i.jsx("div",{className:"loading-ring"}),i.jsx("p",{children:"Checking your sign-in and server access…"})]}):t!=null&&t.authenticated?b?i.jsxs("div",{className:"application-public-state",children:[i.jsx("div",{className:"application-success-mark",children:"✓"}),i.jsx("span",{className:"panel-kicker",children:"Application received"}),i.jsx("h1",{children:"Thanks for stepping up."}),i.jsxs("p",{children:["Your answers were sent to ",V,". You can only apply once to this opening."]}),i.jsxs("a",{className:"button button-muted",href:`/apply/${M}`,children:["View other openings ",i.jsx(X,{name:"arrow"})]})]}):g&&!r&&c.length===0?i.jsxs("div",{className:"application-public-state",children:[i.jsx("div",{className:"application-public-symbol",children:i.jsx(X,{name:"shield"})}),i.jsx("span",{className:"panel-kicker",children:"Access check"}),i.jsx("h1",{children:"We couldn’t open this application."}),i.jsx("p",{children:g}),i.jsx("a",{className:"button button-muted",href:"/",children:"Return home"})]}):r!=null&&r.already_submitted?i.jsxs("div",{className:"application-public-state",children:[i.jsx("div",{className:"application-success-mark",children:"✓"}),i.jsx("span",{className:"panel-kicker",children:"Already submitted"}),i.jsx("h1",{children:"Your application is on file."}),i.jsxs("p",{children:["You’ve already submitted an application for ",r.title,". Reopening it later won’t allow a second submission."]}),i.jsxs("a",{className:"button button-muted",href:`/apply/${M}`,children:["View other openings ",i.jsx(X,{name:"arrow"})]})]}):r?i.jsxs(i.Fragment,{children:[i.jsxs("div",{className:"application-public-topline",children:[i.jsx("span",{className:"application-status open",children:"Accepting applications"}),i.jsx("span",{className:"application-server-tag",children:V})]}),i.jsxs("div",{className:"application-public-heading",children:[i.jsxs("span",{className:"panel-kicker",children:["STAFF APPLICATION · ",r.role_name||"ROLE OPENING"]}),i.jsx("h1",{children:r.title}),i.jsx("p",{children:r.description||"Complete the questions below to apply for this opening."})]}),i.jsxs("div",{className:"application-verified",children:[i.jsx("span",{className:"application-verified-icon",children:i.jsx(X,{name:"shield"})}),i.jsxs("span",{children:[i.jsx("strong",{children:"Membership verified"}),i.jsxs("small",{children:["Signed in as ",((z=t.user)==null?void 0:z.global_name)||((re=t.user)==null?void 0:re.username)||"your Discord account",". Niko checked your server roles."]})]}),i.jsx("a",{href:"/auth/logout",children:"Switch account"})]}),i.jsxs("form",{className:"application-public-form",onSubmit:D,children:[r.questions.map((Y,ce)=>i.jsxs("label",{className:"form-field application-answer-field",children:[i.jsxs("span",{className:"application-question-count",children:["QUESTION ",String(ce+1).padStart(2,"0")]}),i.jsxs("span",{className:"form-label",children:[Y.prompt,Y.required&&i.jsx("i",{children:"Required"})]}),i.jsx("textarea",{required:Y.required,maxLength:4e3,rows:4,value:h[Y.id]||"",onChange:ue=>p(ie=>({...ie,[Y.id]:ue.target.value})),placeholder:"Write your answer here…"}),i.jsxs("small",{children:[(h[Y.id]||"").length,"/4000 characters"]})]},Y.id)),g&&i.jsx("div",{className:"notice warning",role:"alert",children:g}),i.jsxs("div",{className:"application-submit-footer",children:[i.jsx("span",{children:"Your submission is private to this server’s application managers."}),i.jsxs("button",{type:"submit",className:"button button-primary",disabled:k,children:[k?"Sending…":"Submit application"," ",i.jsx(X,{name:"arrow"})]})]})]})]}):c.length>0?i.jsxs("div",{className:"application-public-state application-opening-state",children:[i.jsxs("span",{className:"panel-kicker",children:[V," · open roles"]}),i.jsx("h1",{children:"Choose your opening."}),i.jsx("p",{children:"Select an eligible team role to start your application."}),i.jsx("div",{className:"public-opening-list",children:c.map(Y=>i.jsxs("article",{className:"public-opening-card",children:[i.jsxs("div",{children:[i.jsx("span",{className:`application-status ${Y.already_submitted?"closed":Y.eligible?"open":"closed"}`,children:Y.already_submitted?"Already applied":Y.eligible?"Eligible":"Role required"}),i.jsx("h2",{children:Y.title}),i.jsx("p",{children:Y.description||`Apply for ${Y.role_name||"this role"}.`})]}),Y.eligible&&!Y.already_submitted&&i.jsxs("a",{className:"button button-primary",href:`/apply/${M}/${Y.id}`,children:["Apply ",i.jsx(X,{name:"arrow"})]})]},Y.id))})]}):i.jsxs("div",{className:"application-public-state",children:[i.jsx("div",{className:"application-public-symbol",children:i.jsx(X,{name:"users"})}),i.jsx("span",{className:"panel-kicker",children:"Nothing open just yet"}),i.jsx("h1",{children:"No openings available."}),i.jsx("p",{children:g||"This server doesn’t have any open staff applications right now."}),i.jsx("a",{className:"button button-muted",href:"/",children:"Return home"})]}):i.jsxs("div",{className:"application-public-state",children:[i.jsx("div",{className:"application-public-symbol",children:i.jsx(X,{name:"lock"})}),i.jsx("span",{className:"panel-kicker",children:"A safe, verified application"}),i.jsx("h1",{children:"Sign in to continue."}),i.jsx("p",{children:"Use your Discord account to confirm that you’re a member of this server and eligible for its openings."}),t!=null&&t.oauth_available?i.jsxs("a",{className:"button button-primary",href:B,children:["Continue with Discord ",i.jsx(X,{name:"arrow"})]}):i.jsx("p",{className:"form-error",children:"Discord sign-in isn’t available right now."})]})}),i.jsxs("footer",{className:"application-public-footer",children:[i.jsx("span",{children:"Identity and server roles verified by Discord."}),(N==null?void 0:N.bot_avatar_url)&&i.jsx("img",{src:N.bot_avatar_url,alt:"Niko"})]})]})})]})}const nf=[{question:"How do I invite Niko to my server?",answer:"Use the Add to Discord button in the site header to start the invite flow. You’ll need permission to add apps to the server."},{question:"Where can I find setup instructions and command help?",answer:"The documentation library includes setup guides, feature walkthroughs, and a searchable command reference."},{question:"Why isn’t a command or feature working?",answer:"Check that Niko is online and has the permissions needed in the channel. If the issue continues, share the command name and a short description in the support server."},{question:"How do I report a bug or request a feature?",answer:"Join the support server and post in the appropriate help or feedback channel. Include steps to reproduce bugs, and never share passwords or private tokens."},{question:"How can I request deletion of my data?",answer:"Contact the Niko team through the support server and include your Discord user ID so staff can locate the relevant data."}];function KS(){var c;const t=_n(),s=(c=t==null?void 0:t.support_server_url)==null?void 0:c.trim(),[r,o]=T.useState(0);return i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"support"}),i.jsxs("main",{className:"shell page-main support-page",children:[i.jsxs("section",{className:"support-hero",children:[i.jsx("div",{className:"eyebrow",children:"Niko support"}),i.jsxs("h1",{children:["Let’s get you ",i.jsx("em",{children:"unstuck."})]}),i.jsx("p",{children:"Browse quick answers, explore the guides, or talk with the community and Niko team."}),i.jsxs("div",{className:"support-actions",children:[i.jsxs("a",{className:"button button-primary",href:"/docs",children:["Browse documentation ",i.jsx(X,{name:"arrow"})]}),s&&i.jsxs("a",{className:"button button-muted",href:"/discord",children:["Join the support server ",i.jsx(X,{name:"arrow"})]})]})]}),i.jsxs("section",{className:"support-faq","aria-labelledby":"support-faq-title",children:[i.jsxs("div",{className:"support-section-heading",children:[i.jsxs("div",{children:[i.jsx("div",{className:"eyebrow",children:"Quick answers"}),i.jsx("h2",{id:"support-faq-title",children:"Frequently asked questions"})]}),i.jsxs("span",{className:"support-faq-count",children:[nf.length," helpful guides"]})]}),i.jsx("div",{className:"support-faq-list",children:nf.map((d,h)=>{const p=r===h,f=`support-faq-answer-${h}`;return i.jsxs("article",{className:`support-faq-item${p?" is-open":""}`,children:[i.jsx("h3",{children:i.jsxs("button",{type:"button","aria-expanded":p,"aria-controls":f,onClick:()=>o(p?null:h),children:[i.jsxs("span",{className:"support-faq-question",children:[i.jsx("span",{className:"support-faq-number",children:String(h+1).padStart(2,"0")}),d.question]}),i.jsx("span",{className:"support-faq-toggle",children:i.jsx(X,{name:p?"minus":"plus"})})]})}),i.jsx("div",{id:f,className:"support-faq-answer","aria-hidden":!p,children:i.jsx("div",{className:"support-faq-answer-inner",children:i.jsxs("p",{children:[d.answer,h===1&&i.jsxs(i.Fragment,{children:[" ",i.jsxs("a",{href:"/docs",tabIndex:p?0:-1,children:["Open the docs ",i.jsx("span",{"aria-hidden":"true",children:"↗"})]}),"."]})]})})})]},d.question)})})]}),i.jsxs("aside",{className:"support-contact-card",children:[i.jsx("div",{className:"support-contact-mark",children:i.jsx(X,{name:"message"})}),i.jsxs("div",{children:[i.jsx("div",{className:"eyebrow",children:"Need a hand?"}),i.jsx("h2",{children:"Find us in the community."}),i.jsx("p",{children:"Get help from other Niko users and the staff team in the official support server."})]}),s?i.jsxs("a",{className:"button button-primary",href:"/discord",children:["Open support server ",i.jsx(X,{name:"arrow"})]}):i.jsx("p",{className:"support-missing-link",role:"status",children:"The support server link isn’t available right now. Please check back later."})]})]}),i.jsx(St,{})]})}function qS(){var r;const t=_n(),s=(r=t==null?void 0:t.support_server_url)==null?void 0:r.trim();return T.useEffect(()=>{s&&window.location.replace(s)},[s]),t?s?i.jsxs("main",{className:"discord-redirect-state",children:[i.jsx("div",{className:"loading-ring"}),i.jsx("p",{children:"Taking you to the Niko support server…"}),i.jsx("a",{href:s,children:"Continue if you aren’t redirected"})]}):i.jsxs(i.Fragment,{children:[i.jsx(Oe,{page:"support"}),i.jsxs("main",{className:"shell page-main discord-redirect-missing",children:[i.jsx("div",{className:"eyebrow",children:"Niko support"}),i.jsx("h1",{children:"We couldn’t find the support link."}),i.jsx("p",{children:"The official support server link isn’t configured right now. Please check back later."}),i.jsx("a",{className:"button button-primary",href:"/support",children:"Visit support"})]}),i.jsx(St,{})]}):i.jsxs("main",{className:"discord-redirect-state",children:[i.jsx("div",{className:"loading-ring"}),i.jsx("p",{children:"Checking the Niko support link…"})]})}function XS(){const[t,s]=T.useState(Tm);if(T.useEffect(()=>{const r=()=>s(Tm());return window.addEventListener("popstate",r),()=>window.removeEventListener("popstate",r)},[]),t==="commands")return i.jsx(wb,{});if(t==="docs-detail"){const r=window.location.pathname.split("/"),o=r[r.length-1];return i.jsx(rS,{slug:o})}if(t==="docs")return i.jsx(aS,{});if(t==="staff")return i.jsx(HS,{});if(t==="application")return i.jsx(GS,{});if(t==="dashboard")return i.jsx(J1,{});if(t==="team")return i.jsx(US,{});if(t==="team-member")return i.jsx(WS,{id:window.location.pathname.split("/").filter(Boolean)[1]||""});if(t==="support")return i.jsx(KS,{});if(t==="discord")return i.jsx(qS,{});if(t==="privacy")return i.jsx(uc,{type:"privacy"});if(t==="terms")return i.jsx(uc,{type:"terms"});if(t==="community")return i.jsx(uc,{type:"community"});if(t==="donate")return i.jsx(cS,{});if(t==="transcript"){const o=window.location.pathname.split("/").filter(Boolean)[1]||"";return i.jsx(jS,{transcriptId:o})}if(t==="changelog")return i.jsx(CS,{});if(t==="changelog-detail"){const r=window.location.pathname.split("/"),o=r[r.length-1];return i.jsx(TS,{slug:o})}return i.jsx(oS,{})}"serviceWorker"in navigator&&window.addEventListener("load",()=>{navigator.serviceWorker.register("/service-worker.js").catch(t=>{console.warn("Niko app support could not be initialized.",t)})});Ax.createRoot(document.getElementById("root")).render(i.jsx(T.StrictMode,{children:i.jsx(XS,{})}));
