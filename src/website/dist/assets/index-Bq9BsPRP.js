var Lm=Object.defineProperty;var Rm=(l,c,u)=>c in l?Lm(l,c,{enumerable:!0,configurable:!0,writable:!0,value:u}):l[c]=u;var ic=(l,c,u)=>Rm(l,typeof c!="symbol"?c+"":c,u);(function(){const c=document.createElement("link").relList;if(c&&c.supports&&c.supports("modulepreload"))return;for(const y of document.querySelectorAll('link[rel="modulepreload"]'))p(y);new MutationObserver(y=>{for(const E of y)if(E.type==="childList")for(const S of E.addedNodes)S.tagName==="LINK"&&S.rel==="modulepreload"&&p(S)}).observe(document,{childList:!0,subtree:!0});function u(y){const E={};return y.integrity&&(E.integrity=y.integrity),y.referrerPolicy&&(E.referrerPolicy=y.referrerPolicy),y.crossOrigin==="use-credentials"?E.credentials="include":y.crossOrigin==="anonymous"?E.credentials="omit":E.credentials="same-origin",E}function p(y){if(y.ep)return;y.ep=!0;const E=u(y);fetch(y.href,E)}})();var Ko={exports:{}},Lr={},Go={exports:{}},ee={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var oc;function Dm(){if(oc)return ee;oc=1;var l=Symbol.for("react.element"),c=Symbol.for("react.portal"),u=Symbol.for("react.fragment"),p=Symbol.for("react.strict_mode"),y=Symbol.for("react.profiler"),E=Symbol.for("react.provider"),S=Symbol.for("react.context"),F=Symbol.for("react.forward_ref"),w=Symbol.for("react.suspense"),O=Symbol.for("react.memo"),L=Symbol.for("react.lazy"),I=Symbol.iterator;function R(f){return f===null||typeof f!="object"?null:(f=I&&f[I]||f["@@iterator"],typeof f=="function"?f:null)}var G={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},k=Object.assign,P={};function j(f,C,Z){this.props=f,this.context=C,this.refs=P,this.updater=Z||G}j.prototype.isReactComponent={},j.prototype.setState=function(f,C){if(typeof f!="object"&&typeof f!="function"&&f!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,f,C,"setState")},j.prototype.forceUpdate=function(f){this.updater.enqueueForceUpdate(this,f,"forceUpdate")};function H(){}H.prototype=j.prototype;function le(f,C,Z){this.props=f,this.context=C,this.refs=P,this.updater=Z||G}var je=le.prototype=new H;je.constructor=le,k(je,j.prototype),je.isPureReactComponent=!0;var pe=Array.isArray,be=Object.prototype.hasOwnProperty,M={current:null},J={key:!0,ref:!0,__self:!0,__source:!0};function de(f,C,Z){var ne,re={},se=null,ue=null;if(C!=null)for(ne in C.ref!==void 0&&(ue=C.ref),C.key!==void 0&&(se=""+C.key),C)be.call(C,ne)&&!J.hasOwnProperty(ne)&&(re[ne]=C[ne]);var oe=arguments.length-2;if(oe===1)re.children=Z;else if(1<oe){for(var ge=Array(oe),Ze=0;Ze<oe;Ze++)ge[Ze]=arguments[Ze+2];re.children=ge}if(f&&f.defaultProps)for(ne in oe=f.defaultProps,oe)re[ne]===void 0&&(re[ne]=oe[ne]);return{$$typeof:l,type:f,key:se,ref:ue,props:re,_owner:M.current}}function Ee(f,C){return{$$typeof:l,type:f.type,key:C,ref:f.ref,props:f.props,_owner:f._owner}}function dn(f){return typeof f=="object"&&f!==null&&f.$$typeof===l}function it(f){var C={"=":"=0",":":"=2"};return"$"+f.replace(/[=:]/g,function(Z){return C[Z]})}var wn=/\/+/g;function Je(f,C){return typeof f=="object"&&f!==null&&f.key!=null?it(""+f.key):C.toString(36)}function mn(f,C,Z,ne,re){var se=typeof f;(se==="undefined"||se==="boolean")&&(f=null);var ue=!1;if(f===null)ue=!0;else switch(se){case"string":case"number":ue=!0;break;case"object":switch(f.$$typeof){case l:case c:ue=!0}}if(ue)return ue=f,re=re(ue),f=ne===""?"."+Je(ue,0):ne,pe(re)?(Z="",f!=null&&(Z=f.replace(wn,"$&/")+"/"),mn(re,C,Z,"",function(Ze){return Ze})):re!=null&&(dn(re)&&(re=Ee(re,Z+(!re.key||ue&&ue.key===re.key?"":(""+re.key).replace(wn,"$&/")+"/")+f)),C.push(re)),1;if(ue=0,ne=ne===""?".":ne+":",pe(f))for(var oe=0;oe<f.length;oe++){se=f[oe];var ge=ne+Je(se,oe);ue+=mn(se,C,Z,ge,re)}else if(ge=R(f),typeof ge=="function")for(f=ge.call(f),oe=0;!(se=f.next()).done;)se=se.value,ge=ne+Je(se,oe++),ue+=mn(se,C,Z,ge,re);else if(se==="object")throw C=String(f),Error("Objects are not valid as a React child (found: "+(C==="[object Object]"?"object with keys {"+Object.keys(f).join(", ")+"}":C)+"). If you meant to render a collection of children, use an array instead.");return ue}function jn(f,C,Z){if(f==null)return f;var ne=[],re=0;return mn(f,ne,"","",function(se){return C.call(Z,se,re++)}),ne}function Ve(f){if(f._status===-1){var C=f._result;C=C(),C.then(function(Z){(f._status===0||f._status===-1)&&(f._status=1,f._result=Z)},function(Z){(f._status===0||f._status===-1)&&(f._status=2,f._result=Z)}),f._status===-1&&(f._status=0,f._result=C)}if(f._status===1)return f._result.default;throw f._result}var ke={current:null},A={transition:null},X={ReactCurrentDispatcher:ke,ReactCurrentBatchConfig:A,ReactCurrentOwner:M};function U(){throw Error("act(...) is not supported in production builds of React.")}return ee.Children={map:jn,forEach:function(f,C,Z){jn(f,function(){C.apply(this,arguments)},Z)},count:function(f){var C=0;return jn(f,function(){C++}),C},toArray:function(f){return jn(f,function(C){return C})||[]},only:function(f){if(!dn(f))throw Error("React.Children.only expected to receive a single React element child.");return f}},ee.Component=j,ee.Fragment=u,ee.Profiler=y,ee.PureComponent=le,ee.StrictMode=p,ee.Suspense=w,ee.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=X,ee.act=U,ee.cloneElement=function(f,C,Z){if(f==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+f+".");var ne=k({},f.props),re=f.key,se=f.ref,ue=f._owner;if(C!=null){if(C.ref!==void 0&&(se=C.ref,ue=M.current),C.key!==void 0&&(re=""+C.key),f.type&&f.type.defaultProps)var oe=f.type.defaultProps;for(ge in C)be.call(C,ge)&&!J.hasOwnProperty(ge)&&(ne[ge]=C[ge]===void 0&&oe!==void 0?oe[ge]:C[ge])}var ge=arguments.length-2;if(ge===1)ne.children=Z;else if(1<ge){oe=Array(ge);for(var Ze=0;Ze<ge;Ze++)oe[Ze]=arguments[Ze+2];ne.children=oe}return{$$typeof:l,type:f.type,key:re,ref:se,props:ne,_owner:ue}},ee.createContext=function(f){return f={$$typeof:S,_currentValue:f,_currentValue2:f,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},f.Provider={$$typeof:E,_context:f},f.Consumer=f},ee.createElement=de,ee.createFactory=function(f){var C=de.bind(null,f);return C.type=f,C},ee.createRef=function(){return{current:null}},ee.forwardRef=function(f){return{$$typeof:F,render:f}},ee.isValidElement=dn,ee.lazy=function(f){return{$$typeof:L,_payload:{_status:-1,_result:f},_init:Ve}},ee.memo=function(f,C){return{$$typeof:O,type:f,compare:C===void 0?null:C}},ee.startTransition=function(f){var C=A.transition;A.transition={};try{f()}finally{A.transition=C}},ee.unstable_act=U,ee.useCallback=function(f,C){return ke.current.useCallback(f,C)},ee.useContext=function(f){return ke.current.useContext(f)},ee.useDebugValue=function(){},ee.useDeferredValue=function(f){return ke.current.useDeferredValue(f)},ee.useEffect=function(f,C){return ke.current.useEffect(f,C)},ee.useId=function(){return ke.current.useId()},ee.useImperativeHandle=function(f,C,Z){return ke.current.useImperativeHandle(f,C,Z)},ee.useInsertionEffect=function(f,C){return ke.current.useInsertionEffect(f,C)},ee.useLayoutEffect=function(f,C){return ke.current.useLayoutEffect(f,C)},ee.useMemo=function(f,C){return ke.current.useMemo(f,C)},ee.useReducer=function(f,C,Z){return ke.current.useReducer(f,C,Z)},ee.useRef=function(f){return ke.current.useRef(f)},ee.useState=function(f){return ke.current.useState(f)},ee.useSyncExternalStore=function(f,C,Z){return ke.current.useSyncExternalStore(f,C,Z)},ee.useTransition=function(){return ke.current.useTransition()},ee.version="18.3.1",ee}var ac;function oa(){return ac||(ac=1,Go.exports=Dm()),Go.exports}/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var lc;function Am(){if(lc)return Lr;lc=1;var l=oa(),c=Symbol.for("react.element"),u=Symbol.for("react.fragment"),p=Object.prototype.hasOwnProperty,y=l.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,E={key:!0,ref:!0,__self:!0,__source:!0};function S(F,w,O){var L,I={},R=null,G=null;O!==void 0&&(R=""+O),w.key!==void 0&&(R=""+w.key),w.ref!==void 0&&(G=w.ref);for(L in w)p.call(w,L)&&!E.hasOwnProperty(L)&&(I[L]=w[L]);if(F&&F.defaultProps)for(L in w=F.defaultProps,w)I[L]===void 0&&(I[L]=w[L]);return{$$typeof:c,type:F,key:R,ref:G,props:I,_owner:y.current}}return Lr.Fragment=u,Lr.jsx=S,Lr.jsxs=S,Lr}var uc;function Im(){return uc||(uc=1,Ko.exports=Am()),Ko.exports}var s=Im(),D=oa(),Hs={},Xo={exports:{}},Xe={},qo={exports:{}},Yo={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var cc;function zm(){return cc||(cc=1,(function(l){function c(A,X){var U=A.length;A.push(X);e:for(;0<U;){var f=U-1>>>1,C=A[f];if(0<y(C,X))A[f]=X,A[U]=C,U=f;else break e}}function u(A){return A.length===0?null:A[0]}function p(A){if(A.length===0)return null;var X=A[0],U=A.pop();if(U!==X){A[0]=U;e:for(var f=0,C=A.length,Z=C>>>1;f<Z;){var ne=2*(f+1)-1,re=A[ne],se=ne+1,ue=A[se];if(0>y(re,U))se<C&&0>y(ue,re)?(A[f]=ue,A[se]=U,f=se):(A[f]=re,A[ne]=U,f=ne);else if(se<C&&0>y(ue,U))A[f]=ue,A[se]=U,f=se;else break e}}return X}function y(A,X){var U=A.sortIndex-X.sortIndex;return U!==0?U:A.id-X.id}if(typeof performance=="object"&&typeof performance.now=="function"){var E=performance;l.unstable_now=function(){return E.now()}}else{var S=Date,F=S.now();l.unstable_now=function(){return S.now()-F}}var w=[],O=[],L=1,I=null,R=3,G=!1,k=!1,P=!1,j=typeof setTimeout=="function"?setTimeout:null,H=typeof clearTimeout=="function"?clearTimeout:null,le=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function je(A){for(var X=u(O);X!==null;){if(X.callback===null)p(O);else if(X.startTime<=A)p(O),X.sortIndex=X.expirationTime,c(w,X);else break;X=u(O)}}function pe(A){if(P=!1,je(A),!k)if(u(w)!==null)k=!0,Ve(be);else{var X=u(O);X!==null&&ke(pe,X.startTime-A)}}function be(A,X){k=!1,P&&(P=!1,H(de),de=-1),G=!0;var U=R;try{for(je(X),I=u(w);I!==null&&(!(I.expirationTime>X)||A&&!it());){var f=I.callback;if(typeof f=="function"){I.callback=null,R=I.priorityLevel;var C=f(I.expirationTime<=X);X=l.unstable_now(),typeof C=="function"?I.callback=C:I===u(w)&&p(w),je(X)}else p(w);I=u(w)}if(I!==null)var Z=!0;else{var ne=u(O);ne!==null&&ke(pe,ne.startTime-X),Z=!1}return Z}finally{I=null,R=U,G=!1}}var M=!1,J=null,de=-1,Ee=5,dn=-1;function it(){return!(l.unstable_now()-dn<Ee)}function wn(){if(J!==null){var A=l.unstable_now();dn=A;var X=!0;try{X=J(!0,A)}finally{X?Je():(M=!1,J=null)}}else M=!1}var Je;if(typeof le=="function")Je=function(){le(wn)};else if(typeof MessageChannel<"u"){var mn=new MessageChannel,jn=mn.port2;mn.port1.onmessage=wn,Je=function(){jn.postMessage(null)}}else Je=function(){j(wn,0)};function Ve(A){J=A,M||(M=!0,Je())}function ke(A,X){de=j(function(){A(l.unstable_now())},X)}l.unstable_IdlePriority=5,l.unstable_ImmediatePriority=1,l.unstable_LowPriority=4,l.unstable_NormalPriority=3,l.unstable_Profiling=null,l.unstable_UserBlockingPriority=2,l.unstable_cancelCallback=function(A){A.callback=null},l.unstable_continueExecution=function(){k||G||(k=!0,Ve(be))},l.unstable_forceFrameRate=function(A){0>A||125<A?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):Ee=0<A?Math.floor(1e3/A):5},l.unstable_getCurrentPriorityLevel=function(){return R},l.unstable_getFirstCallbackNode=function(){return u(w)},l.unstable_next=function(A){switch(R){case 1:case 2:case 3:var X=3;break;default:X=R}var U=R;R=X;try{return A()}finally{R=U}},l.unstable_pauseExecution=function(){},l.unstable_requestPaint=function(){},l.unstable_runWithPriority=function(A,X){switch(A){case 1:case 2:case 3:case 4:case 5:break;default:A=3}var U=R;R=A;try{return X()}finally{R=U}},l.unstable_scheduleCallback=function(A,X,U){var f=l.unstable_now();switch(typeof U=="object"&&U!==null?(U=U.delay,U=typeof U=="number"&&0<U?f+U:f):U=f,A){case 1:var C=-1;break;case 2:C=250;break;case 5:C=1073741823;break;case 4:C=1e4;break;default:C=5e3}return C=U+C,A={id:L++,callback:X,priorityLevel:A,startTime:U,expirationTime:C,sortIndex:-1},U>f?(A.sortIndex=U,c(O,A),u(w)===null&&A===u(O)&&(P?(H(de),de=-1):P=!0,ke(pe,U-f))):(A.sortIndex=C,c(w,A),k||G||(k=!0,Ve(be))),A},l.unstable_shouldYield=it,l.unstable_wrapCallback=function(A){var X=R;return function(){var U=R;R=X;try{return A.apply(this,arguments)}finally{R=U}}}})(Yo)),Yo}var dc;function Fm(){return dc||(dc=1,qo.exports=zm()),qo.exports}/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var mc;function Om(){if(mc)return Xe;mc=1;var l=oa(),c=Fm();function u(e){for(var n="https://reactjs.org/docs/error-decoder.html?invariant="+e,t=1;t<arguments.length;t++)n+="&args[]="+encodeURIComponent(arguments[t]);return"Minified React error #"+e+"; visit "+n+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var p=new Set,y={};function E(e,n){S(e,n),S(e+"Capture",n)}function S(e,n){for(y[e]=n,e=0;e<n.length;e++)p.add(n[e])}var F=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),w=Object.prototype.hasOwnProperty,O=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,L={},I={};function R(e){return w.call(I,e)?!0:w.call(L,e)?!1:O.test(e)?I[e]=!0:(L[e]=!0,!1)}function G(e,n,t,r){if(t!==null&&t.type===0)return!1;switch(typeof n){case"function":case"symbol":return!0;case"boolean":return r?!1:t!==null?!t.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function k(e,n,t,r){if(n===null||typeof n>"u"||G(e,n,t,r))return!0;if(r)return!1;if(t!==null)switch(t.type){case 3:return!n;case 4:return n===!1;case 5:return isNaN(n);case 6:return isNaN(n)||1>n}return!1}function P(e,n,t,r,i,o,a){this.acceptsBooleans=n===2||n===3||n===4,this.attributeName=r,this.attributeNamespace=i,this.mustUseProperty=t,this.propertyName=e,this.type=n,this.sanitizeURL=o,this.removeEmptyString=a}var j={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){j[e]=new P(e,0,!1,e,null,!1,!1)}),[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var n=e[0];j[n]=new P(n,1,!1,e[1],null,!1,!1)}),["contentEditable","draggable","spellCheck","value"].forEach(function(e){j[e]=new P(e,2,!1,e.toLowerCase(),null,!1,!1)}),["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){j[e]=new P(e,2,!1,e,null,!1,!1)}),"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){j[e]=new P(e,3,!1,e.toLowerCase(),null,!1,!1)}),["checked","multiple","muted","selected"].forEach(function(e){j[e]=new P(e,3,!0,e,null,!1,!1)}),["capture","download"].forEach(function(e){j[e]=new P(e,4,!1,e,null,!1,!1)}),["cols","rows","size","span"].forEach(function(e){j[e]=new P(e,6,!1,e,null,!1,!1)}),["rowSpan","start"].forEach(function(e){j[e]=new P(e,5,!1,e.toLowerCase(),null,!1,!1)});var H=/[\-:]([a-z])/g;function le(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var n=e.replace(H,le);j[n]=new P(n,1,!1,e,null,!1,!1)}),"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var n=e.replace(H,le);j[n]=new P(n,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)}),["xml:base","xml:lang","xml:space"].forEach(function(e){var n=e.replace(H,le);j[n]=new P(n,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)}),["tabIndex","crossOrigin"].forEach(function(e){j[e]=new P(e,1,!1,e.toLowerCase(),null,!1,!1)}),j.xlinkHref=new P("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1),["src","href","action","formAction"].forEach(function(e){j[e]=new P(e,1,!1,e.toLowerCase(),null,!0,!0)});function je(e,n,t,r){var i=j.hasOwnProperty(n)?j[n]:null;(i!==null?i.type!==0:r||!(2<n.length)||n[0]!=="o"&&n[0]!=="O"||n[1]!=="n"&&n[1]!=="N")&&(k(n,t,i,r)&&(t=null),r||i===null?R(n)&&(t===null?e.removeAttribute(n):e.setAttribute(n,""+t)):i.mustUseProperty?e[i.propertyName]=t===null?i.type===3?!1:"":t:(n=i.attributeName,r=i.attributeNamespace,t===null?e.removeAttribute(n):(i=i.type,t=i===3||i===4&&t===!0?"":""+t,r?e.setAttributeNS(r,n,t):e.setAttribute(n,t))))}var pe=l.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,be=Symbol.for("react.element"),M=Symbol.for("react.portal"),J=Symbol.for("react.fragment"),de=Symbol.for("react.strict_mode"),Ee=Symbol.for("react.profiler"),dn=Symbol.for("react.provider"),it=Symbol.for("react.context"),wn=Symbol.for("react.forward_ref"),Je=Symbol.for("react.suspense"),mn=Symbol.for("react.suspense_list"),jn=Symbol.for("react.memo"),Ve=Symbol.for("react.lazy"),ke=Symbol.for("react.offscreen"),A=Symbol.iterator;function X(e){return e===null||typeof e!="object"?null:(e=A&&e[A]||e["@@iterator"],typeof e=="function"?e:null)}var U=Object.assign,f;function C(e){if(f===void 0)try{throw Error()}catch(t){var n=t.stack.trim().match(/\n( *(at )?)/);f=n&&n[1]||""}return`
`+f+e}var Z=!1;function ne(e,n){if(!e||Z)return"";Z=!0;var t=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(n)if(n=function(){throw Error()},Object.defineProperty(n.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(n,[])}catch(x){var r=x}Reflect.construct(e,[],n)}else{try{n.call()}catch(x){r=x}e.call(n.prototype)}else{try{throw Error()}catch(x){r=x}e()}}catch(x){if(x&&r&&typeof x.stack=="string"){for(var i=x.stack.split(`
`),o=r.stack.split(`
`),a=i.length-1,d=o.length-1;1<=a&&0<=d&&i[a]!==o[d];)d--;for(;1<=a&&0<=d;a--,d--)if(i[a]!==o[d]){if(a!==1||d!==1)do if(a--,d--,0>d||i[a]!==o[d]){var m=`
`+i[a].replace(" at new "," at ");return e.displayName&&m.includes("<anonymous>")&&(m=m.replace("<anonymous>",e.displayName)),m}while(1<=a&&0<=d);break}}}finally{Z=!1,Error.prepareStackTrace=t}return(e=e?e.displayName||e.name:"")?C(e):""}function re(e){switch(e.tag){case 5:return C(e.type);case 16:return C("Lazy");case 13:return C("Suspense");case 19:return C("SuspenseList");case 0:case 2:case 15:return e=ne(e.type,!1),e;case 11:return e=ne(e.type.render,!1),e;case 1:return e=ne(e.type,!0),e;default:return""}}function se(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case J:return"Fragment";case M:return"Portal";case Ee:return"Profiler";case de:return"StrictMode";case Je:return"Suspense";case mn:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case it:return(e.displayName||"Context")+".Consumer";case dn:return(e._context.displayName||"Context")+".Provider";case wn:var n=e.render;return e=e.displayName,e||(e=n.displayName||n.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case jn:return n=e.displayName||null,n!==null?n:se(e.type)||"Memo";case Ve:n=e._payload,e=e._init;try{return se(e(n))}catch{}}return null}function ue(e){var n=e.type;switch(e.tag){case 24:return"Cache";case 9:return(n.displayName||"Context")+".Consumer";case 10:return(n._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=n.render,e=e.displayName||e.name||"",n.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return n;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return se(n);case 8:return n===de?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof n=="function")return n.displayName||n.name||null;if(typeof n=="string")return n}return null}function oe(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function ge(e){var n=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(n==="checkbox"||n==="radio")}function Ze(e){var n=ge(e)?"checked":"value",t=Object.getOwnPropertyDescriptor(e.constructor.prototype,n),r=""+e[n];if(!e.hasOwnProperty(n)&&typeof t<"u"&&typeof t.get=="function"&&typeof t.set=="function"){var i=t.get,o=t.set;return Object.defineProperty(e,n,{configurable:!0,get:function(){return i.call(this)},set:function(a){r=""+a,o.call(this,a)}}),Object.defineProperty(e,n,{enumerable:t.enumerable}),{getValue:function(){return r},setValue:function(a){r=""+a},stopTracking:function(){e._valueTracker=null,delete e[n]}}}}function Ar(e){e._valueTracker||(e._valueTracker=Ze(e))}function da(e){if(!e)return!1;var n=e._valueTracker;if(!n)return!0;var t=n.getValue(),r="";return e&&(r=ge(e)?e.checked?"true":"false":e.value),e=r,e!==t?(n.setValue(e),!0):!1}function Ir(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function Zs(e,n){var t=n.checked;return U({},n,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:t??e._wrapperState.initialChecked})}function ma(e,n){var t=n.defaultValue==null?"":n.defaultValue,r=n.checked!=null?n.checked:n.defaultChecked;t=oe(n.value!=null?n.value:t),e._wrapperState={initialChecked:r,initialValue:t,controlled:n.type==="checkbox"||n.type==="radio"?n.checked!=null:n.value!=null}}function ha(e,n){n=n.checked,n!=null&&je(e,"checked",n,!1)}function ei(e,n){ha(e,n);var t=oe(n.value),r=n.type;if(t!=null)r==="number"?(t===0&&e.value===""||e.value!=t)&&(e.value=""+t):e.value!==""+t&&(e.value=""+t);else if(r==="submit"||r==="reset"){e.removeAttribute("value");return}n.hasOwnProperty("value")?ni(e,n.type,t):n.hasOwnProperty("defaultValue")&&ni(e,n.type,oe(n.defaultValue)),n.checked==null&&n.defaultChecked!=null&&(e.defaultChecked=!!n.defaultChecked)}function fa(e,n,t){if(n.hasOwnProperty("value")||n.hasOwnProperty("defaultValue")){var r=n.type;if(!(r!=="submit"&&r!=="reset"||n.value!==void 0&&n.value!==null))return;n=""+e._wrapperState.initialValue,t||n===e.value||(e.value=n),e.defaultValue=n}t=e.name,t!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,t!==""&&(e.name=t)}function ni(e,n,t){(n!=="number"||Ir(e.ownerDocument)!==e)&&(t==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+t&&(e.defaultValue=""+t))}var Kt=Array.isArray;function wt(e,n,t,r){if(e=e.options,n){n={};for(var i=0;i<t.length;i++)n["$"+t[i]]=!0;for(t=0;t<e.length;t++)i=n.hasOwnProperty("$"+e[t].value),e[t].selected!==i&&(e[t].selected=i),i&&r&&(e[t].defaultSelected=!0)}else{for(t=""+oe(t),n=null,i=0;i<e.length;i++){if(e[i].value===t){e[i].selected=!0,r&&(e[i].defaultSelected=!0);return}n!==null||e[i].disabled||(n=e[i])}n!==null&&(n.selected=!0)}}function ti(e,n){if(n.dangerouslySetInnerHTML!=null)throw Error(u(91));return U({},n,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function pa(e,n){var t=n.value;if(t==null){if(t=n.children,n=n.defaultValue,t!=null){if(n!=null)throw Error(u(92));if(Kt(t)){if(1<t.length)throw Error(u(93));t=t[0]}n=t}n==null&&(n=""),t=n}e._wrapperState={initialValue:oe(t)}}function ga(e,n){var t=oe(n.value),r=oe(n.defaultValue);t!=null&&(t=""+t,t!==e.value&&(e.value=t),n.defaultValue==null&&e.defaultValue!==t&&(e.defaultValue=t)),r!=null&&(e.defaultValue=""+r)}function va(e){var n=e.textContent;n===e._wrapperState.initialValue&&n!==""&&n!==null&&(e.value=n)}function ya(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function ri(e,n){return e==null||e==="http://www.w3.org/1999/xhtml"?ya(n):e==="http://www.w3.org/2000/svg"&&n==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var zr,xa=(function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(n,t,r,i){MSApp.execUnsafeLocalFunction(function(){return e(n,t,r,i)})}:e})(function(e,n){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=n;else{for(zr=zr||document.createElement("div"),zr.innerHTML="<svg>"+n.valueOf().toString()+"</svg>",n=zr.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;n.firstChild;)e.appendChild(n.firstChild)}});function Gt(e,n){if(n){var t=e.firstChild;if(t&&t===e.lastChild&&t.nodeType===3){t.nodeValue=n;return}}e.textContent=n}var Xt={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},Ic=["Webkit","ms","Moz","O"];Object.keys(Xt).forEach(function(e){Ic.forEach(function(n){n=n+e.charAt(0).toUpperCase()+e.substring(1),Xt[n]=Xt[e]})});function ka(e,n,t){return n==null||typeof n=="boolean"||n===""?"":t||typeof n!="number"||n===0||Xt.hasOwnProperty(e)&&Xt[e]?(""+n).trim():n+"px"}function wa(e,n){e=e.style;for(var t in n)if(n.hasOwnProperty(t)){var r=t.indexOf("--")===0,i=ka(t,n[t],r);t==="float"&&(t="cssFloat"),r?e.setProperty(t,i):e[t]=i}}var zc=U({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function si(e,n){if(n){if(zc[e]&&(n.children!=null||n.dangerouslySetInnerHTML!=null))throw Error(u(137,e));if(n.dangerouslySetInnerHTML!=null){if(n.children!=null)throw Error(u(60));if(typeof n.dangerouslySetInnerHTML!="object"||!("__html"in n.dangerouslySetInnerHTML))throw Error(u(61))}if(n.style!=null&&typeof n.style!="object")throw Error(u(62))}}function ii(e,n){if(e.indexOf("-")===-1)return typeof n.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var oi=null;function ai(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var li=null,jt=null,St=null;function ja(e){if(e=vr(e)){if(typeof li!="function")throw Error(u(280));var n=e.stateNode;n&&(n=os(n),li(e.stateNode,e.type,n))}}function Sa(e){jt?St?St.push(e):St=[e]:jt=e}function Na(){if(jt){var e=jt,n=St;if(St=jt=null,ja(e),n)for(e=0;e<n.length;e++)ja(n[e])}}function Ca(e,n){return e(n)}function _a(){}var ui=!1;function ba(e,n,t){if(ui)return e(n,t);ui=!0;try{return Ca(e,n,t)}finally{ui=!1,(jt!==null||St!==null)&&(_a(),Na())}}function qt(e,n){var t=e.stateNode;if(t===null)return null;var r=os(t);if(r===null)return null;t=r[n];e:switch(n){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(r=!r.disabled)||(e=e.type,r=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!r;break e;default:e=!1}if(e)return null;if(t&&typeof t!="function")throw Error(u(231,n,typeof t));return t}var ci=!1;if(F)try{var Yt={};Object.defineProperty(Yt,"passive",{get:function(){ci=!0}}),window.addEventListener("test",Yt,Yt),window.removeEventListener("test",Yt,Yt)}catch{ci=!1}function Fc(e,n,t,r,i,o,a,d,m){var x=Array.prototype.slice.call(arguments,3);try{n.apply(t,x)}catch(_){this.onError(_)}}var Jt=!1,Fr=null,Or=!1,di=null,Oc={onError:function(e){Jt=!0,Fr=e}};function Bc(e,n,t,r,i,o,a,d,m){Jt=!1,Fr=null,Fc.apply(Oc,arguments)}function Uc(e,n,t,r,i,o,a,d,m){if(Bc.apply(this,arguments),Jt){if(Jt){var x=Fr;Jt=!1,Fr=null}else throw Error(u(198));Or||(Or=!0,di=x)}}function ot(e){var n=e,t=e;if(e.alternate)for(;n.return;)n=n.return;else{e=n;do n=e,(n.flags&4098)!==0&&(t=n.return),e=n.return;while(e)}return n.tag===3?t:null}function Ea(e){if(e.tag===13){var n=e.memoizedState;if(n===null&&(e=e.alternate,e!==null&&(n=e.memoizedState)),n!==null)return n.dehydrated}return null}function Pa(e){if(ot(e)!==e)throw Error(u(188))}function Wc(e){var n=e.alternate;if(!n){if(n=ot(e),n===null)throw Error(u(188));return n!==e?null:e}for(var t=e,r=n;;){var i=t.return;if(i===null)break;var o=i.alternate;if(o===null){if(r=i.return,r!==null){t=r;continue}break}if(i.child===o.child){for(o=i.child;o;){if(o===t)return Pa(i),e;if(o===r)return Pa(i),n;o=o.sibling}throw Error(u(188))}if(t.return!==r.return)t=i,r=o;else{for(var a=!1,d=i.child;d;){if(d===t){a=!0,t=i,r=o;break}if(d===r){a=!0,r=i,t=o;break}d=d.sibling}if(!a){for(d=o.child;d;){if(d===t){a=!0,t=o,r=i;break}if(d===r){a=!0,r=o,t=i;break}d=d.sibling}if(!a)throw Error(u(189))}}if(t.alternate!==r)throw Error(u(190))}if(t.tag!==3)throw Error(u(188));return t.stateNode.current===t?e:n}function Ma(e){return e=Wc(e),e!==null?Ta(e):null}function Ta(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var n=Ta(e);if(n!==null)return n;e=e.sibling}return null}var La=c.unstable_scheduleCallback,Ra=c.unstable_cancelCallback,Vc=c.unstable_shouldYield,$c=c.unstable_requestPaint,Se=c.unstable_now,Hc=c.unstable_getCurrentPriorityLevel,mi=c.unstable_ImmediatePriority,Da=c.unstable_UserBlockingPriority,Br=c.unstable_NormalPriority,Qc=c.unstable_LowPriority,Aa=c.unstable_IdlePriority,Ur=null,Sn=null;function Kc(e){if(Sn&&typeof Sn.onCommitFiberRoot=="function")try{Sn.onCommitFiberRoot(Ur,e,void 0,(e.current.flags&128)===128)}catch{}}var hn=Math.clz32?Math.clz32:qc,Gc=Math.log,Xc=Math.LN2;function qc(e){return e>>>=0,e===0?32:31-(Gc(e)/Xc|0)|0}var Wr=64,Vr=4194304;function Zt(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function $r(e,n){var t=e.pendingLanes;if(t===0)return 0;var r=0,i=e.suspendedLanes,o=e.pingedLanes,a=t&268435455;if(a!==0){var d=a&~i;d!==0?r=Zt(d):(o&=a,o!==0&&(r=Zt(o)))}else a=t&~i,a!==0?r=Zt(a):o!==0&&(r=Zt(o));if(r===0)return 0;if(n!==0&&n!==r&&(n&i)===0&&(i=r&-r,o=n&-n,i>=o||i===16&&(o&4194240)!==0))return n;if((r&4)!==0&&(r|=t&16),n=e.entangledLanes,n!==0)for(e=e.entanglements,n&=r;0<n;)t=31-hn(n),i=1<<t,r|=e[t],n&=~i;return r}function Yc(e,n){switch(e){case 1:case 2:case 4:return n+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return n+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function Jc(e,n){for(var t=e.suspendedLanes,r=e.pingedLanes,i=e.expirationTimes,o=e.pendingLanes;0<o;){var a=31-hn(o),d=1<<a,m=i[a];m===-1?((d&t)===0||(d&r)!==0)&&(i[a]=Yc(d,n)):m<=n&&(e.expiredLanes|=d),o&=~d}}function hi(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function Ia(){var e=Wr;return Wr<<=1,(Wr&4194240)===0&&(Wr=64),e}function fi(e){for(var n=[],t=0;31>t;t++)n.push(e);return n}function er(e,n,t){e.pendingLanes|=n,n!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,n=31-hn(n),e[n]=t}function Zc(e,n){var t=e.pendingLanes&~n;e.pendingLanes=n,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=n,e.mutableReadLanes&=n,e.entangledLanes&=n,n=e.entanglements;var r=e.eventTimes;for(e=e.expirationTimes;0<t;){var i=31-hn(t),o=1<<i;n[i]=0,r[i]=-1,e[i]=-1,t&=~o}}function pi(e,n){var t=e.entangledLanes|=n;for(e=e.entanglements;t;){var r=31-hn(t),i=1<<r;i&n|e[r]&n&&(e[r]|=n),t&=~i}}var ae=0;function za(e){return e&=-e,1<e?4<e?(e&268435455)!==0?16:536870912:4:1}var Fa,gi,Oa,Ba,Ua,vi=!1,Hr=[],Fn=null,On=null,Bn=null,nr=new Map,tr=new Map,Un=[],ed="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function Wa(e,n){switch(e){case"focusin":case"focusout":Fn=null;break;case"dragenter":case"dragleave":On=null;break;case"mouseover":case"mouseout":Bn=null;break;case"pointerover":case"pointerout":nr.delete(n.pointerId);break;case"gotpointercapture":case"lostpointercapture":tr.delete(n.pointerId)}}function rr(e,n,t,r,i,o){return e===null||e.nativeEvent!==o?(e={blockedOn:n,domEventName:t,eventSystemFlags:r,nativeEvent:o,targetContainers:[i]},n!==null&&(n=vr(n),n!==null&&gi(n)),e):(e.eventSystemFlags|=r,n=e.targetContainers,i!==null&&n.indexOf(i)===-1&&n.push(i),e)}function nd(e,n,t,r,i){switch(n){case"focusin":return Fn=rr(Fn,e,n,t,r,i),!0;case"dragenter":return On=rr(On,e,n,t,r,i),!0;case"mouseover":return Bn=rr(Bn,e,n,t,r,i),!0;case"pointerover":var o=i.pointerId;return nr.set(o,rr(nr.get(o)||null,e,n,t,r,i)),!0;case"gotpointercapture":return o=i.pointerId,tr.set(o,rr(tr.get(o)||null,e,n,t,r,i)),!0}return!1}function Va(e){var n=at(e.target);if(n!==null){var t=ot(n);if(t!==null){if(n=t.tag,n===13){if(n=Ea(t),n!==null){e.blockedOn=n,Ua(e.priority,function(){Oa(t)});return}}else if(n===3&&t.stateNode.current.memoizedState.isDehydrated){e.blockedOn=t.tag===3?t.stateNode.containerInfo:null;return}}}e.blockedOn=null}function Qr(e){if(e.blockedOn!==null)return!1;for(var n=e.targetContainers;0<n.length;){var t=xi(e.domEventName,e.eventSystemFlags,n[0],e.nativeEvent);if(t===null){t=e.nativeEvent;var r=new t.constructor(t.type,t);oi=r,t.target.dispatchEvent(r),oi=null}else return n=vr(t),n!==null&&gi(n),e.blockedOn=t,!1;n.shift()}return!0}function $a(e,n,t){Qr(e)&&t.delete(n)}function td(){vi=!1,Fn!==null&&Qr(Fn)&&(Fn=null),On!==null&&Qr(On)&&(On=null),Bn!==null&&Qr(Bn)&&(Bn=null),nr.forEach($a),tr.forEach($a)}function sr(e,n){e.blockedOn===n&&(e.blockedOn=null,vi||(vi=!0,c.unstable_scheduleCallback(c.unstable_NormalPriority,td)))}function ir(e){function n(i){return sr(i,e)}if(0<Hr.length){sr(Hr[0],e);for(var t=1;t<Hr.length;t++){var r=Hr[t];r.blockedOn===e&&(r.blockedOn=null)}}for(Fn!==null&&sr(Fn,e),On!==null&&sr(On,e),Bn!==null&&sr(Bn,e),nr.forEach(n),tr.forEach(n),t=0;t<Un.length;t++)r=Un[t],r.blockedOn===e&&(r.blockedOn=null);for(;0<Un.length&&(t=Un[0],t.blockedOn===null);)Va(t),t.blockedOn===null&&Un.shift()}var Nt=pe.ReactCurrentBatchConfig,Kr=!0;function rd(e,n,t,r){var i=ae,o=Nt.transition;Nt.transition=null;try{ae=1,yi(e,n,t,r)}finally{ae=i,Nt.transition=o}}function sd(e,n,t,r){var i=ae,o=Nt.transition;Nt.transition=null;try{ae=4,yi(e,n,t,r)}finally{ae=i,Nt.transition=o}}function yi(e,n,t,r){if(Kr){var i=xi(e,n,t,r);if(i===null)Ii(e,n,r,Gr,t),Wa(e,r);else if(nd(i,e,n,t,r))r.stopPropagation();else if(Wa(e,r),n&4&&-1<ed.indexOf(e)){for(;i!==null;){var o=vr(i);if(o!==null&&Fa(o),o=xi(e,n,t,r),o===null&&Ii(e,n,r,Gr,t),o===i)break;i=o}i!==null&&r.stopPropagation()}else Ii(e,n,r,null,t)}}var Gr=null;function xi(e,n,t,r){if(Gr=null,e=ai(r),e=at(e),e!==null)if(n=ot(e),n===null)e=null;else if(t=n.tag,t===13){if(e=Ea(n),e!==null)return e;e=null}else if(t===3){if(n.stateNode.current.memoizedState.isDehydrated)return n.tag===3?n.stateNode.containerInfo:null;e=null}else n!==e&&(e=null);return Gr=e,null}function Ha(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(Hc()){case mi:return 1;case Da:return 4;case Br:case Qc:return 16;case Aa:return 536870912;default:return 16}default:return 16}}var Wn=null,ki=null,Xr=null;function Qa(){if(Xr)return Xr;var e,n=ki,t=n.length,r,i="value"in Wn?Wn.value:Wn.textContent,o=i.length;for(e=0;e<t&&n[e]===i[e];e++);var a=t-e;for(r=1;r<=a&&n[t-r]===i[o-r];r++);return Xr=i.slice(e,1<r?1-r:void 0)}function qr(e){var n=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&n===13&&(e=13)):e=n,e===10&&(e=13),32<=e||e===13?e:0}function Yr(){return!0}function Ka(){return!1}function en(e){function n(t,r,i,o,a){this._reactName=t,this._targetInst=i,this.type=r,this.nativeEvent=o,this.target=a,this.currentTarget=null;for(var d in e)e.hasOwnProperty(d)&&(t=e[d],this[d]=t?t(o):o[d]);return this.isDefaultPrevented=(o.defaultPrevented!=null?o.defaultPrevented:o.returnValue===!1)?Yr:Ka,this.isPropagationStopped=Ka,this}return U(n.prototype,{preventDefault:function(){this.defaultPrevented=!0;var t=this.nativeEvent;t&&(t.preventDefault?t.preventDefault():typeof t.returnValue!="unknown"&&(t.returnValue=!1),this.isDefaultPrevented=Yr)},stopPropagation:function(){var t=this.nativeEvent;t&&(t.stopPropagation?t.stopPropagation():typeof t.cancelBubble!="unknown"&&(t.cancelBubble=!0),this.isPropagationStopped=Yr)},persist:function(){},isPersistent:Yr}),n}var Ct={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},wi=en(Ct),or=U({},Ct,{view:0,detail:0}),id=en(or),ji,Si,ar,Jr=U({},or,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:Ci,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==ar&&(ar&&e.type==="mousemove"?(ji=e.screenX-ar.screenX,Si=e.screenY-ar.screenY):Si=ji=0,ar=e),ji)},movementY:function(e){return"movementY"in e?e.movementY:Si}}),Ga=en(Jr),od=U({},Jr,{dataTransfer:0}),ad=en(od),ld=U({},or,{relatedTarget:0}),Ni=en(ld),ud=U({},Ct,{animationName:0,elapsedTime:0,pseudoElement:0}),cd=en(ud),dd=U({},Ct,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),md=en(dd),hd=U({},Ct,{data:0}),Xa=en(hd),fd={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},pd={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},gd={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function vd(e){var n=this.nativeEvent;return n.getModifierState?n.getModifierState(e):(e=gd[e])?!!n[e]:!1}function Ci(){return vd}var yd=U({},or,{key:function(e){if(e.key){var n=fd[e.key]||e.key;if(n!=="Unidentified")return n}return e.type==="keypress"?(e=qr(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?pd[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:Ci,charCode:function(e){return e.type==="keypress"?qr(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?qr(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),xd=en(yd),kd=U({},Jr,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),qa=en(kd),wd=U({},or,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:Ci}),jd=en(wd),Sd=U({},Ct,{propertyName:0,elapsedTime:0,pseudoElement:0}),Nd=en(Sd),Cd=U({},Jr,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),_d=en(Cd),bd=[9,13,27,32],_i=F&&"CompositionEvent"in window,lr=null;F&&"documentMode"in document&&(lr=document.documentMode);var Ed=F&&"TextEvent"in window&&!lr,Ya=F&&(!_i||lr&&8<lr&&11>=lr),Ja=" ",Za=!1;function el(e,n){switch(e){case"keyup":return bd.indexOf(n.keyCode)!==-1;case"keydown":return n.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function nl(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var _t=!1;function Pd(e,n){switch(e){case"compositionend":return nl(n);case"keypress":return n.which!==32?null:(Za=!0,Ja);case"textInput":return e=n.data,e===Ja&&Za?null:e;default:return null}}function Md(e,n){if(_t)return e==="compositionend"||!_i&&el(e,n)?(e=Qa(),Xr=ki=Wn=null,_t=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(n.ctrlKey||n.altKey||n.metaKey)||n.ctrlKey&&n.altKey){if(n.char&&1<n.char.length)return n.char;if(n.which)return String.fromCharCode(n.which)}return null;case"compositionend":return Ya&&n.locale!=="ko"?null:n.data;default:return null}}var Td={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function tl(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n==="input"?!!Td[e.type]:n==="textarea"}function rl(e,n,t,r){Sa(r),n=rs(n,"onChange"),0<n.length&&(t=new wi("onChange","change",null,t,r),e.push({event:t,listeners:n}))}var ur=null,cr=null;function Ld(e){wl(e,0)}function Zr(e){var n=Tt(e);if(da(n))return e}function Rd(e,n){if(e==="change")return n}var sl=!1;if(F){var bi;if(F){var Ei="oninput"in document;if(!Ei){var il=document.createElement("div");il.setAttribute("oninput","return;"),Ei=typeof il.oninput=="function"}bi=Ei}else bi=!1;sl=bi&&(!document.documentMode||9<document.documentMode)}function ol(){ur&&(ur.detachEvent("onpropertychange",al),cr=ur=null)}function al(e){if(e.propertyName==="value"&&Zr(cr)){var n=[];rl(n,cr,e,ai(e)),ba(Ld,n)}}function Dd(e,n,t){e==="focusin"?(ol(),ur=n,cr=t,ur.attachEvent("onpropertychange",al)):e==="focusout"&&ol()}function Ad(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return Zr(cr)}function Id(e,n){if(e==="click")return Zr(n)}function zd(e,n){if(e==="input"||e==="change")return Zr(n)}function Fd(e,n){return e===n&&(e!==0||1/e===1/n)||e!==e&&n!==n}var fn=typeof Object.is=="function"?Object.is:Fd;function dr(e,n){if(fn(e,n))return!0;if(typeof e!="object"||e===null||typeof n!="object"||n===null)return!1;var t=Object.keys(e),r=Object.keys(n);if(t.length!==r.length)return!1;for(r=0;r<t.length;r++){var i=t[r];if(!w.call(n,i)||!fn(e[i],n[i]))return!1}return!0}function ll(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function ul(e,n){var t=ll(e);e=0;for(var r;t;){if(t.nodeType===3){if(r=e+t.textContent.length,e<=n&&r>=n)return{node:t,offset:n-e};e=r}e:{for(;t;){if(t.nextSibling){t=t.nextSibling;break e}t=t.parentNode}t=void 0}t=ll(t)}}function cl(e,n){return e&&n?e===n?!0:e&&e.nodeType===3?!1:n&&n.nodeType===3?cl(e,n.parentNode):"contains"in e?e.contains(n):e.compareDocumentPosition?!!(e.compareDocumentPosition(n)&16):!1:!1}function dl(){for(var e=window,n=Ir();n instanceof e.HTMLIFrameElement;){try{var t=typeof n.contentWindow.location.href=="string"}catch{t=!1}if(t)e=n.contentWindow;else break;n=Ir(e.document)}return n}function Pi(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n&&(n==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||n==="textarea"||e.contentEditable==="true")}function Od(e){var n=dl(),t=e.focusedElem,r=e.selectionRange;if(n!==t&&t&&t.ownerDocument&&cl(t.ownerDocument.documentElement,t)){if(r!==null&&Pi(t)){if(n=r.start,e=r.end,e===void 0&&(e=n),"selectionStart"in t)t.selectionStart=n,t.selectionEnd=Math.min(e,t.value.length);else if(e=(n=t.ownerDocument||document)&&n.defaultView||window,e.getSelection){e=e.getSelection();var i=t.textContent.length,o=Math.min(r.start,i);r=r.end===void 0?o:Math.min(r.end,i),!e.extend&&o>r&&(i=r,r=o,o=i),i=ul(t,o);var a=ul(t,r);i&&a&&(e.rangeCount!==1||e.anchorNode!==i.node||e.anchorOffset!==i.offset||e.focusNode!==a.node||e.focusOffset!==a.offset)&&(n=n.createRange(),n.setStart(i.node,i.offset),e.removeAllRanges(),o>r?(e.addRange(n),e.extend(a.node,a.offset)):(n.setEnd(a.node,a.offset),e.addRange(n)))}}for(n=[],e=t;e=e.parentNode;)e.nodeType===1&&n.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof t.focus=="function"&&t.focus(),t=0;t<n.length;t++)e=n[t],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var Bd=F&&"documentMode"in document&&11>=document.documentMode,bt=null,Mi=null,mr=null,Ti=!1;function ml(e,n,t){var r=t.window===t?t.document:t.nodeType===9?t:t.ownerDocument;Ti||bt==null||bt!==Ir(r)||(r=bt,"selectionStart"in r&&Pi(r)?r={start:r.selectionStart,end:r.selectionEnd}:(r=(r.ownerDocument&&r.ownerDocument.defaultView||window).getSelection(),r={anchorNode:r.anchorNode,anchorOffset:r.anchorOffset,focusNode:r.focusNode,focusOffset:r.focusOffset}),mr&&dr(mr,r)||(mr=r,r=rs(Mi,"onSelect"),0<r.length&&(n=new wi("onSelect","select",null,n,t),e.push({event:n,listeners:r}),n.target=bt)))}function es(e,n){var t={};return t[e.toLowerCase()]=n.toLowerCase(),t["Webkit"+e]="webkit"+n,t["Moz"+e]="moz"+n,t}var Et={animationend:es("Animation","AnimationEnd"),animationiteration:es("Animation","AnimationIteration"),animationstart:es("Animation","AnimationStart"),transitionend:es("Transition","TransitionEnd")},Li={},hl={};F&&(hl=document.createElement("div").style,"AnimationEvent"in window||(delete Et.animationend.animation,delete Et.animationiteration.animation,delete Et.animationstart.animation),"TransitionEvent"in window||delete Et.transitionend.transition);function ns(e){if(Li[e])return Li[e];if(!Et[e])return e;var n=Et[e],t;for(t in n)if(n.hasOwnProperty(t)&&t in hl)return Li[e]=n[t];return e}var fl=ns("animationend"),pl=ns("animationiteration"),gl=ns("animationstart"),vl=ns("transitionend"),yl=new Map,xl="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function Vn(e,n){yl.set(e,n),E(n,[e])}for(var Ri=0;Ri<xl.length;Ri++){var Di=xl[Ri],Ud=Di.toLowerCase(),Wd=Di[0].toUpperCase()+Di.slice(1);Vn(Ud,"on"+Wd)}Vn(fl,"onAnimationEnd"),Vn(pl,"onAnimationIteration"),Vn(gl,"onAnimationStart"),Vn("dblclick","onDoubleClick"),Vn("focusin","onFocus"),Vn("focusout","onBlur"),Vn(vl,"onTransitionEnd"),S("onMouseEnter",["mouseout","mouseover"]),S("onMouseLeave",["mouseout","mouseover"]),S("onPointerEnter",["pointerout","pointerover"]),S("onPointerLeave",["pointerout","pointerover"]),E("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),E("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),E("onBeforeInput",["compositionend","keypress","textInput","paste"]),E("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),E("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),E("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var hr="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),Vd=new Set("cancel close invalid load scroll toggle".split(" ").concat(hr));function kl(e,n,t){var r=e.type||"unknown-event";e.currentTarget=t,Uc(r,n,void 0,e),e.currentTarget=null}function wl(e,n){n=(n&4)!==0;for(var t=0;t<e.length;t++){var r=e[t],i=r.event;r=r.listeners;e:{var o=void 0;if(n)for(var a=r.length-1;0<=a;a--){var d=r[a],m=d.instance,x=d.currentTarget;if(d=d.listener,m!==o&&i.isPropagationStopped())break e;kl(i,d,x),o=m}else for(a=0;a<r.length;a++){if(d=r[a],m=d.instance,x=d.currentTarget,d=d.listener,m!==o&&i.isPropagationStopped())break e;kl(i,d,x),o=m}}}if(Or)throw e=di,Or=!1,di=null,e}function me(e,n){var t=n[Wi];t===void 0&&(t=n[Wi]=new Set);var r=e+"__bubble";t.has(r)||(jl(n,e,2,!1),t.add(r))}function Ai(e,n,t){var r=0;n&&(r|=4),jl(t,e,r,n)}var ts="_reactListening"+Math.random().toString(36).slice(2);function fr(e){if(!e[ts]){e[ts]=!0,p.forEach(function(t){t!=="selectionchange"&&(Vd.has(t)||Ai(t,!1,e),Ai(t,!0,e))});var n=e.nodeType===9?e:e.ownerDocument;n===null||n[ts]||(n[ts]=!0,Ai("selectionchange",!1,n))}}function jl(e,n,t,r){switch(Ha(n)){case 1:var i=rd;break;case 4:i=sd;break;default:i=yi}t=i.bind(null,n,t,e),i=void 0,!ci||n!=="touchstart"&&n!=="touchmove"&&n!=="wheel"||(i=!0),r?i!==void 0?e.addEventListener(n,t,{capture:!0,passive:i}):e.addEventListener(n,t,!0):i!==void 0?e.addEventListener(n,t,{passive:i}):e.addEventListener(n,t,!1)}function Ii(e,n,t,r,i){var o=r;if((n&1)===0&&(n&2)===0&&r!==null)e:for(;;){if(r===null)return;var a=r.tag;if(a===3||a===4){var d=r.stateNode.containerInfo;if(d===i||d.nodeType===8&&d.parentNode===i)break;if(a===4)for(a=r.return;a!==null;){var m=a.tag;if((m===3||m===4)&&(m=a.stateNode.containerInfo,m===i||m.nodeType===8&&m.parentNode===i))return;a=a.return}for(;d!==null;){if(a=at(d),a===null)return;if(m=a.tag,m===5||m===6){r=o=a;continue e}d=d.parentNode}}r=r.return}ba(function(){var x=o,_=ai(t),b=[];e:{var N=yl.get(e);if(N!==void 0){var z=wi,W=e;switch(e){case"keypress":if(qr(t)===0)break e;case"keydown":case"keyup":z=xd;break;case"focusin":W="focus",z=Ni;break;case"focusout":W="blur",z=Ni;break;case"beforeblur":case"afterblur":z=Ni;break;case"click":if(t.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":z=Ga;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":z=ad;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":z=jd;break;case fl:case pl:case gl:z=cd;break;case vl:z=Nd;break;case"scroll":z=id;break;case"wheel":z=_d;break;case"copy":case"cut":case"paste":z=md;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":z=qa}var V=(n&4)!==0,Ne=!V&&e==="scroll",g=V?N!==null?N+"Capture":null:N;V=[];for(var h=x,v;h!==null;){v=h;var T=v.stateNode;if(v.tag===5&&T!==null&&(v=T,g!==null&&(T=qt(h,g),T!=null&&V.push(pr(h,T,v)))),Ne)break;h=h.return}0<V.length&&(N=new z(N,W,null,t,_),b.push({event:N,listeners:V}))}}if((n&7)===0){e:{if(N=e==="mouseover"||e==="pointerover",z=e==="mouseout"||e==="pointerout",N&&t!==oi&&(W=t.relatedTarget||t.fromElement)&&(at(W)||W[Mn]))break e;if((z||N)&&(N=_.window===_?_:(N=_.ownerDocument)?N.defaultView||N.parentWindow:window,z?(W=t.relatedTarget||t.toElement,z=x,W=W?at(W):null,W!==null&&(Ne=ot(W),W!==Ne||W.tag!==5&&W.tag!==6)&&(W=null)):(z=null,W=x),z!==W)){if(V=Ga,T="onMouseLeave",g="onMouseEnter",h="mouse",(e==="pointerout"||e==="pointerover")&&(V=qa,T="onPointerLeave",g="onPointerEnter",h="pointer"),Ne=z==null?N:Tt(z),v=W==null?N:Tt(W),N=new V(T,h+"leave",z,t,_),N.target=Ne,N.relatedTarget=v,T=null,at(_)===x&&(V=new V(g,h+"enter",W,t,_),V.target=v,V.relatedTarget=Ne,T=V),Ne=T,z&&W)n:{for(V=z,g=W,h=0,v=V;v;v=Pt(v))h++;for(v=0,T=g;T;T=Pt(T))v++;for(;0<h-v;)V=Pt(V),h--;for(;0<v-h;)g=Pt(g),v--;for(;h--;){if(V===g||g!==null&&V===g.alternate)break n;V=Pt(V),g=Pt(g)}V=null}else V=null;z!==null&&Sl(b,N,z,V,!1),W!==null&&Ne!==null&&Sl(b,Ne,W,V,!0)}}e:{if(N=x?Tt(x):window,z=N.nodeName&&N.nodeName.toLowerCase(),z==="select"||z==="input"&&N.type==="file")var $=Rd;else if(tl(N))if(sl)$=zd;else{$=Ad;var Q=Dd}else(z=N.nodeName)&&z.toLowerCase()==="input"&&(N.type==="checkbox"||N.type==="radio")&&($=Id);if($&&($=$(e,x))){rl(b,$,t,_);break e}Q&&Q(e,N,x),e==="focusout"&&(Q=N._wrapperState)&&Q.controlled&&N.type==="number"&&ni(N,"number",N.value)}switch(Q=x?Tt(x):window,e){case"focusin":(tl(Q)||Q.contentEditable==="true")&&(bt=Q,Mi=x,mr=null);break;case"focusout":mr=Mi=bt=null;break;case"mousedown":Ti=!0;break;case"contextmenu":case"mouseup":case"dragend":Ti=!1,ml(b,t,_);break;case"selectionchange":if(Bd)break;case"keydown":case"keyup":ml(b,t,_)}var K;if(_i)e:{switch(e){case"compositionstart":var q="onCompositionStart";break e;case"compositionend":q="onCompositionEnd";break e;case"compositionupdate":q="onCompositionUpdate";break e}q=void 0}else _t?el(e,t)&&(q="onCompositionEnd"):e==="keydown"&&t.keyCode===229&&(q="onCompositionStart");q&&(Ya&&t.locale!=="ko"&&(_t||q!=="onCompositionStart"?q==="onCompositionEnd"&&_t&&(K=Qa()):(Wn=_,ki="value"in Wn?Wn.value:Wn.textContent,_t=!0)),Q=rs(x,q),0<Q.length&&(q=new Xa(q,e,null,t,_),b.push({event:q,listeners:Q}),K?q.data=K:(K=nl(t),K!==null&&(q.data=K)))),(K=Ed?Pd(e,t):Md(e,t))&&(x=rs(x,"onBeforeInput"),0<x.length&&(_=new Xa("onBeforeInput","beforeinput",null,t,_),b.push({event:_,listeners:x}),_.data=K))}wl(b,n)})}function pr(e,n,t){return{instance:e,listener:n,currentTarget:t}}function rs(e,n){for(var t=n+"Capture",r=[];e!==null;){var i=e,o=i.stateNode;i.tag===5&&o!==null&&(i=o,o=qt(e,t),o!=null&&r.unshift(pr(e,o,i)),o=qt(e,n),o!=null&&r.push(pr(e,o,i))),e=e.return}return r}function Pt(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function Sl(e,n,t,r,i){for(var o=n._reactName,a=[];t!==null&&t!==r;){var d=t,m=d.alternate,x=d.stateNode;if(m!==null&&m===r)break;d.tag===5&&x!==null&&(d=x,i?(m=qt(t,o),m!=null&&a.unshift(pr(t,m,d))):i||(m=qt(t,o),m!=null&&a.push(pr(t,m,d)))),t=t.return}a.length!==0&&e.push({event:n,listeners:a})}var $d=/\r\n?/g,Hd=/\u0000|\uFFFD/g;function Nl(e){return(typeof e=="string"?e:""+e).replace($d,`
`).replace(Hd,"")}function ss(e,n,t){if(n=Nl(n),Nl(e)!==n&&t)throw Error(u(425))}function is(){}var zi=null,Fi=null;function Oi(e,n){return e==="textarea"||e==="noscript"||typeof n.children=="string"||typeof n.children=="number"||typeof n.dangerouslySetInnerHTML=="object"&&n.dangerouslySetInnerHTML!==null&&n.dangerouslySetInnerHTML.__html!=null}var Bi=typeof setTimeout=="function"?setTimeout:void 0,Qd=typeof clearTimeout=="function"?clearTimeout:void 0,Cl=typeof Promise=="function"?Promise:void 0,Kd=typeof queueMicrotask=="function"?queueMicrotask:typeof Cl<"u"?function(e){return Cl.resolve(null).then(e).catch(Gd)}:Bi;function Gd(e){setTimeout(function(){throw e})}function Ui(e,n){var t=n,r=0;do{var i=t.nextSibling;if(e.removeChild(t),i&&i.nodeType===8)if(t=i.data,t==="/$"){if(r===0){e.removeChild(i),ir(n);return}r--}else t!=="$"&&t!=="$?"&&t!=="$!"||r++;t=i}while(t);ir(n)}function $n(e){for(;e!=null;e=e.nextSibling){var n=e.nodeType;if(n===1||n===3)break;if(n===8){if(n=e.data,n==="$"||n==="$!"||n==="$?")break;if(n==="/$")return null}}return e}function _l(e){e=e.previousSibling;for(var n=0;e;){if(e.nodeType===8){var t=e.data;if(t==="$"||t==="$!"||t==="$?"){if(n===0)return e;n--}else t==="/$"&&n++}e=e.previousSibling}return null}var Mt=Math.random().toString(36).slice(2),Nn="__reactFiber$"+Mt,gr="__reactProps$"+Mt,Mn="__reactContainer$"+Mt,Wi="__reactEvents$"+Mt,Xd="__reactListeners$"+Mt,qd="__reactHandles$"+Mt;function at(e){var n=e[Nn];if(n)return n;for(var t=e.parentNode;t;){if(n=t[Mn]||t[Nn]){if(t=n.alternate,n.child!==null||t!==null&&t.child!==null)for(e=_l(e);e!==null;){if(t=e[Nn])return t;e=_l(e)}return n}e=t,t=e.parentNode}return null}function vr(e){return e=e[Nn]||e[Mn],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function Tt(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(u(33))}function os(e){return e[gr]||null}var Vi=[],Lt=-1;function Hn(e){return{current:e}}function he(e){0>Lt||(e.current=Vi[Lt],Vi[Lt]=null,Lt--)}function ce(e,n){Lt++,Vi[Lt]=e.current,e.current=n}var Qn={},ze=Hn(Qn),$e=Hn(!1),lt=Qn;function Rt(e,n){var t=e.type.contextTypes;if(!t)return Qn;var r=e.stateNode;if(r&&r.__reactInternalMemoizedUnmaskedChildContext===n)return r.__reactInternalMemoizedMaskedChildContext;var i={},o;for(o in t)i[o]=n[o];return r&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=n,e.__reactInternalMemoizedMaskedChildContext=i),i}function He(e){return e=e.childContextTypes,e!=null}function as(){he($e),he(ze)}function bl(e,n,t){if(ze.current!==Qn)throw Error(u(168));ce(ze,n),ce($e,t)}function El(e,n,t){var r=e.stateNode;if(n=n.childContextTypes,typeof r.getChildContext!="function")return t;r=r.getChildContext();for(var i in r)if(!(i in n))throw Error(u(108,ue(e)||"Unknown",i));return U({},t,r)}function ls(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||Qn,lt=ze.current,ce(ze,e),ce($e,$e.current),!0}function Pl(e,n,t){var r=e.stateNode;if(!r)throw Error(u(169));t?(e=El(e,n,lt),r.__reactInternalMemoizedMergedChildContext=e,he($e),he(ze),ce(ze,e)):he($e),ce($e,t)}var Tn=null,us=!1,$i=!1;function Ml(e){Tn===null?Tn=[e]:Tn.push(e)}function Yd(e){us=!0,Ml(e)}function Kn(){if(!$i&&Tn!==null){$i=!0;var e=0,n=ae;try{var t=Tn;for(ae=1;e<t.length;e++){var r=t[e];do r=r(!0);while(r!==null)}Tn=null,us=!1}catch(i){throw Tn!==null&&(Tn=Tn.slice(e+1)),La(mi,Kn),i}finally{ae=n,$i=!1}}return null}var Dt=[],At=0,cs=null,ds=0,sn=[],on=0,ut=null,Ln=1,Rn="";function ct(e,n){Dt[At++]=ds,Dt[At++]=cs,cs=e,ds=n}function Tl(e,n,t){sn[on++]=Ln,sn[on++]=Rn,sn[on++]=ut,ut=e;var r=Ln;e=Rn;var i=32-hn(r)-1;r&=~(1<<i),t+=1;var o=32-hn(n)+i;if(30<o){var a=i-i%5;o=(r&(1<<a)-1).toString(32),r>>=a,i-=a,Ln=1<<32-hn(n)+i|t<<i|r,Rn=o+e}else Ln=1<<o|t<<i|r,Rn=e}function Hi(e){e.return!==null&&(ct(e,1),Tl(e,1,0))}function Qi(e){for(;e===cs;)cs=Dt[--At],Dt[At]=null,ds=Dt[--At],Dt[At]=null;for(;e===ut;)ut=sn[--on],sn[on]=null,Rn=sn[--on],sn[on]=null,Ln=sn[--on],sn[on]=null}var nn=null,tn=null,ve=!1,pn=null;function Ll(e,n){var t=cn(5,null,null,0);t.elementType="DELETED",t.stateNode=n,t.return=e,n=e.deletions,n===null?(e.deletions=[t],e.flags|=16):n.push(t)}function Rl(e,n){switch(e.tag){case 5:var t=e.type;return n=n.nodeType!==1||t.toLowerCase()!==n.nodeName.toLowerCase()?null:n,n!==null?(e.stateNode=n,nn=e,tn=$n(n.firstChild),!0):!1;case 6:return n=e.pendingProps===""||n.nodeType!==3?null:n,n!==null?(e.stateNode=n,nn=e,tn=null,!0):!1;case 13:return n=n.nodeType!==8?null:n,n!==null?(t=ut!==null?{id:Ln,overflow:Rn}:null,e.memoizedState={dehydrated:n,treeContext:t,retryLane:1073741824},t=cn(18,null,null,0),t.stateNode=n,t.return=e,e.child=t,nn=e,tn=null,!0):!1;default:return!1}}function Ki(e){return(e.mode&1)!==0&&(e.flags&128)===0}function Gi(e){if(ve){var n=tn;if(n){var t=n;if(!Rl(e,n)){if(Ki(e))throw Error(u(418));n=$n(t.nextSibling);var r=nn;n&&Rl(e,n)?Ll(r,t):(e.flags=e.flags&-4097|2,ve=!1,nn=e)}}else{if(Ki(e))throw Error(u(418));e.flags=e.flags&-4097|2,ve=!1,nn=e}}}function Dl(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;nn=e}function ms(e){if(e!==nn)return!1;if(!ve)return Dl(e),ve=!0,!1;var n;if((n=e.tag!==3)&&!(n=e.tag!==5)&&(n=e.type,n=n!=="head"&&n!=="body"&&!Oi(e.type,e.memoizedProps)),n&&(n=tn)){if(Ki(e))throw Al(),Error(u(418));for(;n;)Ll(e,n),n=$n(n.nextSibling)}if(Dl(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(u(317));e:{for(e=e.nextSibling,n=0;e;){if(e.nodeType===8){var t=e.data;if(t==="/$"){if(n===0){tn=$n(e.nextSibling);break e}n--}else t!=="$"&&t!=="$!"&&t!=="$?"||n++}e=e.nextSibling}tn=null}}else tn=nn?$n(e.stateNode.nextSibling):null;return!0}function Al(){for(var e=tn;e;)e=$n(e.nextSibling)}function It(){tn=nn=null,ve=!1}function Xi(e){pn===null?pn=[e]:pn.push(e)}var Jd=pe.ReactCurrentBatchConfig;function yr(e,n,t){if(e=t.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(t._owner){if(t=t._owner,t){if(t.tag!==1)throw Error(u(309));var r=t.stateNode}if(!r)throw Error(u(147,e));var i=r,o=""+e;return n!==null&&n.ref!==null&&typeof n.ref=="function"&&n.ref._stringRef===o?n.ref:(n=function(a){var d=i.refs;a===null?delete d[o]:d[o]=a},n._stringRef=o,n)}if(typeof e!="string")throw Error(u(284));if(!t._owner)throw Error(u(290,e))}return e}function hs(e,n){throw e=Object.prototype.toString.call(n),Error(u(31,e==="[object Object]"?"object with keys {"+Object.keys(n).join(", ")+"}":e))}function Il(e){var n=e._init;return n(e._payload)}function zl(e){function n(g,h){if(e){var v=g.deletions;v===null?(g.deletions=[h],g.flags|=16):v.push(h)}}function t(g,h){if(!e)return null;for(;h!==null;)n(g,h),h=h.sibling;return null}function r(g,h){for(g=new Map;h!==null;)h.key!==null?g.set(h.key,h):g.set(h.index,h),h=h.sibling;return g}function i(g,h){return g=nt(g,h),g.index=0,g.sibling=null,g}function o(g,h,v){return g.index=v,e?(v=g.alternate,v!==null?(v=v.index,v<h?(g.flags|=2,h):v):(g.flags|=2,h)):(g.flags|=1048576,h)}function a(g){return e&&g.alternate===null&&(g.flags|=2),g}function d(g,h,v,T){return h===null||h.tag!==6?(h=Uo(v,g.mode,T),h.return=g,h):(h=i(h,v),h.return=g,h)}function m(g,h,v,T){var $=v.type;return $===J?_(g,h,v.props.children,T,v.key):h!==null&&(h.elementType===$||typeof $=="object"&&$!==null&&$.$$typeof===Ve&&Il($)===h.type)?(T=i(h,v.props),T.ref=yr(g,h,v),T.return=g,T):(T=zs(v.type,v.key,v.props,null,g.mode,T),T.ref=yr(g,h,v),T.return=g,T)}function x(g,h,v,T){return h===null||h.tag!==4||h.stateNode.containerInfo!==v.containerInfo||h.stateNode.implementation!==v.implementation?(h=Wo(v,g.mode,T),h.return=g,h):(h=i(h,v.children||[]),h.return=g,h)}function _(g,h,v,T,$){return h===null||h.tag!==7?(h=yt(v,g.mode,T,$),h.return=g,h):(h=i(h,v),h.return=g,h)}function b(g,h,v){if(typeof h=="string"&&h!==""||typeof h=="number")return h=Uo(""+h,g.mode,v),h.return=g,h;if(typeof h=="object"&&h!==null){switch(h.$$typeof){case be:return v=zs(h.type,h.key,h.props,null,g.mode,v),v.ref=yr(g,null,h),v.return=g,v;case M:return h=Wo(h,g.mode,v),h.return=g,h;case Ve:var T=h._init;return b(g,T(h._payload),v)}if(Kt(h)||X(h))return h=yt(h,g.mode,v,null),h.return=g,h;hs(g,h)}return null}function N(g,h,v,T){var $=h!==null?h.key:null;if(typeof v=="string"&&v!==""||typeof v=="number")return $!==null?null:d(g,h,""+v,T);if(typeof v=="object"&&v!==null){switch(v.$$typeof){case be:return v.key===$?m(g,h,v,T):null;case M:return v.key===$?x(g,h,v,T):null;case Ve:return $=v._init,N(g,h,$(v._payload),T)}if(Kt(v)||X(v))return $!==null?null:_(g,h,v,T,null);hs(g,v)}return null}function z(g,h,v,T,$){if(typeof T=="string"&&T!==""||typeof T=="number")return g=g.get(v)||null,d(h,g,""+T,$);if(typeof T=="object"&&T!==null){switch(T.$$typeof){case be:return g=g.get(T.key===null?v:T.key)||null,m(h,g,T,$);case M:return g=g.get(T.key===null?v:T.key)||null,x(h,g,T,$);case Ve:var Q=T._init;return z(g,h,v,Q(T._payload),$)}if(Kt(T)||X(T))return g=g.get(v)||null,_(h,g,T,$,null);hs(h,T)}return null}function W(g,h,v,T){for(var $=null,Q=null,K=h,q=h=0,De=null;K!==null&&q<v.length;q++){K.index>q?(De=K,K=null):De=K.sibling;var ie=N(g,K,v[q],T);if(ie===null){K===null&&(K=De);break}e&&K&&ie.alternate===null&&n(g,K),h=o(ie,h,q),Q===null?$=ie:Q.sibling=ie,Q=ie,K=De}if(q===v.length)return t(g,K),ve&&ct(g,q),$;if(K===null){for(;q<v.length;q++)K=b(g,v[q],T),K!==null&&(h=o(K,h,q),Q===null?$=K:Q.sibling=K,Q=K);return ve&&ct(g,q),$}for(K=r(g,K);q<v.length;q++)De=z(K,g,q,v[q],T),De!==null&&(e&&De.alternate!==null&&K.delete(De.key===null?q:De.key),h=o(De,h,q),Q===null?$=De:Q.sibling=De,Q=De);return e&&K.forEach(function(tt){return n(g,tt)}),ve&&ct(g,q),$}function V(g,h,v,T){var $=X(v);if(typeof $!="function")throw Error(u(150));if(v=$.call(v),v==null)throw Error(u(151));for(var Q=$=null,K=h,q=h=0,De=null,ie=v.next();K!==null&&!ie.done;q++,ie=v.next()){K.index>q?(De=K,K=null):De=K.sibling;var tt=N(g,K,ie.value,T);if(tt===null){K===null&&(K=De);break}e&&K&&tt.alternate===null&&n(g,K),h=o(tt,h,q),Q===null?$=tt:Q.sibling=tt,Q=tt,K=De}if(ie.done)return t(g,K),ve&&ct(g,q),$;if(K===null){for(;!ie.done;q++,ie=v.next())ie=b(g,ie.value,T),ie!==null&&(h=o(ie,h,q),Q===null?$=ie:Q.sibling=ie,Q=ie);return ve&&ct(g,q),$}for(K=r(g,K);!ie.done;q++,ie=v.next())ie=z(K,g,q,ie.value,T),ie!==null&&(e&&ie.alternate!==null&&K.delete(ie.key===null?q:ie.key),h=o(ie,h,q),Q===null?$=ie:Q.sibling=ie,Q=ie);return e&&K.forEach(function(Tm){return n(g,Tm)}),ve&&ct(g,q),$}function Ne(g,h,v,T){if(typeof v=="object"&&v!==null&&v.type===J&&v.key===null&&(v=v.props.children),typeof v=="object"&&v!==null){switch(v.$$typeof){case be:e:{for(var $=v.key,Q=h;Q!==null;){if(Q.key===$){if($=v.type,$===J){if(Q.tag===7){t(g,Q.sibling),h=i(Q,v.props.children),h.return=g,g=h;break e}}else if(Q.elementType===$||typeof $=="object"&&$!==null&&$.$$typeof===Ve&&Il($)===Q.type){t(g,Q.sibling),h=i(Q,v.props),h.ref=yr(g,Q,v),h.return=g,g=h;break e}t(g,Q);break}else n(g,Q);Q=Q.sibling}v.type===J?(h=yt(v.props.children,g.mode,T,v.key),h.return=g,g=h):(T=zs(v.type,v.key,v.props,null,g.mode,T),T.ref=yr(g,h,v),T.return=g,g=T)}return a(g);case M:e:{for(Q=v.key;h!==null;){if(h.key===Q)if(h.tag===4&&h.stateNode.containerInfo===v.containerInfo&&h.stateNode.implementation===v.implementation){t(g,h.sibling),h=i(h,v.children||[]),h.return=g,g=h;break e}else{t(g,h);break}else n(g,h);h=h.sibling}h=Wo(v,g.mode,T),h.return=g,g=h}return a(g);case Ve:return Q=v._init,Ne(g,h,Q(v._payload),T)}if(Kt(v))return W(g,h,v,T);if(X(v))return V(g,h,v,T);hs(g,v)}return typeof v=="string"&&v!==""||typeof v=="number"?(v=""+v,h!==null&&h.tag===6?(t(g,h.sibling),h=i(h,v),h.return=g,g=h):(t(g,h),h=Uo(v,g.mode,T),h.return=g,g=h),a(g)):t(g,h)}return Ne}var zt=zl(!0),Fl=zl(!1),fs=Hn(null),ps=null,Ft=null,qi=null;function Yi(){qi=Ft=ps=null}function Ji(e){var n=fs.current;he(fs),e._currentValue=n}function Zi(e,n,t){for(;e!==null;){var r=e.alternate;if((e.childLanes&n)!==n?(e.childLanes|=n,r!==null&&(r.childLanes|=n)):r!==null&&(r.childLanes&n)!==n&&(r.childLanes|=n),e===t)break;e=e.return}}function Ot(e,n){ps=e,qi=Ft=null,e=e.dependencies,e!==null&&e.firstContext!==null&&((e.lanes&n)!==0&&(Qe=!0),e.firstContext=null)}function an(e){var n=e._currentValue;if(qi!==e)if(e={context:e,memoizedValue:n,next:null},Ft===null){if(ps===null)throw Error(u(308));Ft=e,ps.dependencies={lanes:0,firstContext:e}}else Ft=Ft.next=e;return n}var dt=null;function eo(e){dt===null?dt=[e]:dt.push(e)}function Ol(e,n,t,r){var i=n.interleaved;return i===null?(t.next=t,eo(n)):(t.next=i.next,i.next=t),n.interleaved=t,Dn(e,r)}function Dn(e,n){e.lanes|=n;var t=e.alternate;for(t!==null&&(t.lanes|=n),t=e,e=e.return;e!==null;)e.childLanes|=n,t=e.alternate,t!==null&&(t.childLanes|=n),t=e,e=e.return;return t.tag===3?t.stateNode:null}var Gn=!1;function no(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function Bl(e,n){e=e.updateQueue,n.updateQueue===e&&(n.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function An(e,n){return{eventTime:e,lane:n,tag:0,payload:null,callback:null,next:null}}function Xn(e,n,t){var r=e.updateQueue;if(r===null)return null;if(r=r.shared,(te&2)!==0){var i=r.pending;return i===null?n.next=n:(n.next=i.next,i.next=n),r.pending=n,Dn(e,t)}return i=r.interleaved,i===null?(n.next=n,eo(r)):(n.next=i.next,i.next=n),r.interleaved=n,Dn(e,t)}function gs(e,n,t){if(n=n.updateQueue,n!==null&&(n=n.shared,(t&4194240)!==0)){var r=n.lanes;r&=e.pendingLanes,t|=r,n.lanes=t,pi(e,t)}}function Ul(e,n){var t=e.updateQueue,r=e.alternate;if(r!==null&&(r=r.updateQueue,t===r)){var i=null,o=null;if(t=t.firstBaseUpdate,t!==null){do{var a={eventTime:t.eventTime,lane:t.lane,tag:t.tag,payload:t.payload,callback:t.callback,next:null};o===null?i=o=a:o=o.next=a,t=t.next}while(t!==null);o===null?i=o=n:o=o.next=n}else i=o=n;t={baseState:r.baseState,firstBaseUpdate:i,lastBaseUpdate:o,shared:r.shared,effects:r.effects},e.updateQueue=t;return}e=t.lastBaseUpdate,e===null?t.firstBaseUpdate=n:e.next=n,t.lastBaseUpdate=n}function vs(e,n,t,r){var i=e.updateQueue;Gn=!1;var o=i.firstBaseUpdate,a=i.lastBaseUpdate,d=i.shared.pending;if(d!==null){i.shared.pending=null;var m=d,x=m.next;m.next=null,a===null?o=x:a.next=x,a=m;var _=e.alternate;_!==null&&(_=_.updateQueue,d=_.lastBaseUpdate,d!==a&&(d===null?_.firstBaseUpdate=x:d.next=x,_.lastBaseUpdate=m))}if(o!==null){var b=i.baseState;a=0,_=x=m=null,d=o;do{var N=d.lane,z=d.eventTime;if((r&N)===N){_!==null&&(_=_.next={eventTime:z,lane:0,tag:d.tag,payload:d.payload,callback:d.callback,next:null});e:{var W=e,V=d;switch(N=n,z=t,V.tag){case 1:if(W=V.payload,typeof W=="function"){b=W.call(z,b,N);break e}b=W;break e;case 3:W.flags=W.flags&-65537|128;case 0:if(W=V.payload,N=typeof W=="function"?W.call(z,b,N):W,N==null)break e;b=U({},b,N);break e;case 2:Gn=!0}}d.callback!==null&&d.lane!==0&&(e.flags|=64,N=i.effects,N===null?i.effects=[d]:N.push(d))}else z={eventTime:z,lane:N,tag:d.tag,payload:d.payload,callback:d.callback,next:null},_===null?(x=_=z,m=b):_=_.next=z,a|=N;if(d=d.next,d===null){if(d=i.shared.pending,d===null)break;N=d,d=N.next,N.next=null,i.lastBaseUpdate=N,i.shared.pending=null}}while(!0);if(_===null&&(m=b),i.baseState=m,i.firstBaseUpdate=x,i.lastBaseUpdate=_,n=i.shared.interleaved,n!==null){i=n;do a|=i.lane,i=i.next;while(i!==n)}else o===null&&(i.shared.lanes=0);ft|=a,e.lanes=a,e.memoizedState=b}}function Wl(e,n,t){if(e=n.effects,n.effects=null,e!==null)for(n=0;n<e.length;n++){var r=e[n],i=r.callback;if(i!==null){if(r.callback=null,r=t,typeof i!="function")throw Error(u(191,i));i.call(r)}}}var xr={},Cn=Hn(xr),kr=Hn(xr),wr=Hn(xr);function mt(e){if(e===xr)throw Error(u(174));return e}function to(e,n){switch(ce(wr,n),ce(kr,e),ce(Cn,xr),e=n.nodeType,e){case 9:case 11:n=(n=n.documentElement)?n.namespaceURI:ri(null,"");break;default:e=e===8?n.parentNode:n,n=e.namespaceURI||null,e=e.tagName,n=ri(n,e)}he(Cn),ce(Cn,n)}function Bt(){he(Cn),he(kr),he(wr)}function Vl(e){mt(wr.current);var n=mt(Cn.current),t=ri(n,e.type);n!==t&&(ce(kr,e),ce(Cn,t))}function ro(e){kr.current===e&&(he(Cn),he(kr))}var ye=Hn(0);function ys(e){for(var n=e;n!==null;){if(n.tag===13){var t=n.memoizedState;if(t!==null&&(t=t.dehydrated,t===null||t.data==="$?"||t.data==="$!"))return n}else if(n.tag===19&&n.memoizedProps.revealOrder!==void 0){if((n.flags&128)!==0)return n}else if(n.child!==null){n.child.return=n,n=n.child;continue}if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return null;n=n.return}n.sibling.return=n.return,n=n.sibling}return null}var so=[];function io(){for(var e=0;e<so.length;e++)so[e]._workInProgressVersionPrimary=null;so.length=0}var xs=pe.ReactCurrentDispatcher,oo=pe.ReactCurrentBatchConfig,ht=0,xe=null,Pe=null,Le=null,ks=!1,jr=!1,Sr=0,Zd=0;function Fe(){throw Error(u(321))}function ao(e,n){if(n===null)return!1;for(var t=0;t<n.length&&t<e.length;t++)if(!fn(e[t],n[t]))return!1;return!0}function lo(e,n,t,r,i,o){if(ht=o,xe=n,n.memoizedState=null,n.updateQueue=null,n.lanes=0,xs.current=e===null||e.memoizedState===null?rm:sm,e=t(r,i),jr){o=0;do{if(jr=!1,Sr=0,25<=o)throw Error(u(301));o+=1,Le=Pe=null,n.updateQueue=null,xs.current=im,e=t(r,i)}while(jr)}if(xs.current=Ss,n=Pe!==null&&Pe.next!==null,ht=0,Le=Pe=xe=null,ks=!1,n)throw Error(u(300));return e}function uo(){var e=Sr!==0;return Sr=0,e}function _n(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return Le===null?xe.memoizedState=Le=e:Le=Le.next=e,Le}function ln(){if(Pe===null){var e=xe.alternate;e=e!==null?e.memoizedState:null}else e=Pe.next;var n=Le===null?xe.memoizedState:Le.next;if(n!==null)Le=n,Pe=e;else{if(e===null)throw Error(u(310));Pe=e,e={memoizedState:Pe.memoizedState,baseState:Pe.baseState,baseQueue:Pe.baseQueue,queue:Pe.queue,next:null},Le===null?xe.memoizedState=Le=e:Le=Le.next=e}return Le}function Nr(e,n){return typeof n=="function"?n(e):n}function co(e){var n=ln(),t=n.queue;if(t===null)throw Error(u(311));t.lastRenderedReducer=e;var r=Pe,i=r.baseQueue,o=t.pending;if(o!==null){if(i!==null){var a=i.next;i.next=o.next,o.next=a}r.baseQueue=i=o,t.pending=null}if(i!==null){o=i.next,r=r.baseState;var d=a=null,m=null,x=o;do{var _=x.lane;if((ht&_)===_)m!==null&&(m=m.next={lane:0,action:x.action,hasEagerState:x.hasEagerState,eagerState:x.eagerState,next:null}),r=x.hasEagerState?x.eagerState:e(r,x.action);else{var b={lane:_,action:x.action,hasEagerState:x.hasEagerState,eagerState:x.eagerState,next:null};m===null?(d=m=b,a=r):m=m.next=b,xe.lanes|=_,ft|=_}x=x.next}while(x!==null&&x!==o);m===null?a=r:m.next=d,fn(r,n.memoizedState)||(Qe=!0),n.memoizedState=r,n.baseState=a,n.baseQueue=m,t.lastRenderedState=r}if(e=t.interleaved,e!==null){i=e;do o=i.lane,xe.lanes|=o,ft|=o,i=i.next;while(i!==e)}else i===null&&(t.lanes=0);return[n.memoizedState,t.dispatch]}function mo(e){var n=ln(),t=n.queue;if(t===null)throw Error(u(311));t.lastRenderedReducer=e;var r=t.dispatch,i=t.pending,o=n.memoizedState;if(i!==null){t.pending=null;var a=i=i.next;do o=e(o,a.action),a=a.next;while(a!==i);fn(o,n.memoizedState)||(Qe=!0),n.memoizedState=o,n.baseQueue===null&&(n.baseState=o),t.lastRenderedState=o}return[o,r]}function $l(){}function Hl(e,n){var t=xe,r=ln(),i=n(),o=!fn(r.memoizedState,i);if(o&&(r.memoizedState=i,Qe=!0),r=r.queue,ho(Gl.bind(null,t,r,e),[e]),r.getSnapshot!==n||o||Le!==null&&Le.memoizedState.tag&1){if(t.flags|=2048,Cr(9,Kl.bind(null,t,r,i,n),void 0,null),Re===null)throw Error(u(349));(ht&30)!==0||Ql(t,n,i)}return i}function Ql(e,n,t){e.flags|=16384,e={getSnapshot:n,value:t},n=xe.updateQueue,n===null?(n={lastEffect:null,stores:null},xe.updateQueue=n,n.stores=[e]):(t=n.stores,t===null?n.stores=[e]:t.push(e))}function Kl(e,n,t,r){n.value=t,n.getSnapshot=r,Xl(n)&&ql(e)}function Gl(e,n,t){return t(function(){Xl(n)&&ql(e)})}function Xl(e){var n=e.getSnapshot;e=e.value;try{var t=n();return!fn(e,t)}catch{return!0}}function ql(e){var n=Dn(e,1);n!==null&&xn(n,e,1,-1)}function Yl(e){var n=_n();return typeof e=="function"&&(e=e()),n.memoizedState=n.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:Nr,lastRenderedState:e},n.queue=e,e=e.dispatch=tm.bind(null,xe,e),[n.memoizedState,e]}function Cr(e,n,t,r){return e={tag:e,create:n,destroy:t,deps:r,next:null},n=xe.updateQueue,n===null?(n={lastEffect:null,stores:null},xe.updateQueue=n,n.lastEffect=e.next=e):(t=n.lastEffect,t===null?n.lastEffect=e.next=e:(r=t.next,t.next=e,e.next=r,n.lastEffect=e)),e}function Jl(){return ln().memoizedState}function ws(e,n,t,r){var i=_n();xe.flags|=e,i.memoizedState=Cr(1|n,t,void 0,r===void 0?null:r)}function js(e,n,t,r){var i=ln();r=r===void 0?null:r;var o=void 0;if(Pe!==null){var a=Pe.memoizedState;if(o=a.destroy,r!==null&&ao(r,a.deps)){i.memoizedState=Cr(n,t,o,r);return}}xe.flags|=e,i.memoizedState=Cr(1|n,t,o,r)}function Zl(e,n){return ws(8390656,8,e,n)}function ho(e,n){return js(2048,8,e,n)}function eu(e,n){return js(4,2,e,n)}function nu(e,n){return js(4,4,e,n)}function tu(e,n){if(typeof n=="function")return e=e(),n(e),function(){n(null)};if(n!=null)return e=e(),n.current=e,function(){n.current=null}}function ru(e,n,t){return t=t!=null?t.concat([e]):null,js(4,4,tu.bind(null,n,e),t)}function fo(){}function su(e,n){var t=ln();n=n===void 0?null:n;var r=t.memoizedState;return r!==null&&n!==null&&ao(n,r[1])?r[0]:(t.memoizedState=[e,n],e)}function iu(e,n){var t=ln();n=n===void 0?null:n;var r=t.memoizedState;return r!==null&&n!==null&&ao(n,r[1])?r[0]:(e=e(),t.memoizedState=[e,n],e)}function ou(e,n,t){return(ht&21)===0?(e.baseState&&(e.baseState=!1,Qe=!0),e.memoizedState=t):(fn(t,n)||(t=Ia(),xe.lanes|=t,ft|=t,e.baseState=!0),n)}function em(e,n){var t=ae;ae=t!==0&&4>t?t:4,e(!0);var r=oo.transition;oo.transition={};try{e(!1),n()}finally{ae=t,oo.transition=r}}function au(){return ln().memoizedState}function nm(e,n,t){var r=Zn(e);if(t={lane:r,action:t,hasEagerState:!1,eagerState:null,next:null},lu(e))uu(n,t);else if(t=Ol(e,n,t,r),t!==null){var i=We();xn(t,e,r,i),cu(t,n,r)}}function tm(e,n,t){var r=Zn(e),i={lane:r,action:t,hasEagerState:!1,eagerState:null,next:null};if(lu(e))uu(n,i);else{var o=e.alternate;if(e.lanes===0&&(o===null||o.lanes===0)&&(o=n.lastRenderedReducer,o!==null))try{var a=n.lastRenderedState,d=o(a,t);if(i.hasEagerState=!0,i.eagerState=d,fn(d,a)){var m=n.interleaved;m===null?(i.next=i,eo(n)):(i.next=m.next,m.next=i),n.interleaved=i;return}}catch{}finally{}t=Ol(e,n,i,r),t!==null&&(i=We(),xn(t,e,r,i),cu(t,n,r))}}function lu(e){var n=e.alternate;return e===xe||n!==null&&n===xe}function uu(e,n){jr=ks=!0;var t=e.pending;t===null?n.next=n:(n.next=t.next,t.next=n),e.pending=n}function cu(e,n,t){if((t&4194240)!==0){var r=n.lanes;r&=e.pendingLanes,t|=r,n.lanes=t,pi(e,t)}}var Ss={readContext:an,useCallback:Fe,useContext:Fe,useEffect:Fe,useImperativeHandle:Fe,useInsertionEffect:Fe,useLayoutEffect:Fe,useMemo:Fe,useReducer:Fe,useRef:Fe,useState:Fe,useDebugValue:Fe,useDeferredValue:Fe,useTransition:Fe,useMutableSource:Fe,useSyncExternalStore:Fe,useId:Fe,unstable_isNewReconciler:!1},rm={readContext:an,useCallback:function(e,n){return _n().memoizedState=[e,n===void 0?null:n],e},useContext:an,useEffect:Zl,useImperativeHandle:function(e,n,t){return t=t!=null?t.concat([e]):null,ws(4194308,4,tu.bind(null,n,e),t)},useLayoutEffect:function(e,n){return ws(4194308,4,e,n)},useInsertionEffect:function(e,n){return ws(4,2,e,n)},useMemo:function(e,n){var t=_n();return n=n===void 0?null:n,e=e(),t.memoizedState=[e,n],e},useReducer:function(e,n,t){var r=_n();return n=t!==void 0?t(n):n,r.memoizedState=r.baseState=n,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:n},r.queue=e,e=e.dispatch=nm.bind(null,xe,e),[r.memoizedState,e]},useRef:function(e){var n=_n();return e={current:e},n.memoizedState=e},useState:Yl,useDebugValue:fo,useDeferredValue:function(e){return _n().memoizedState=e},useTransition:function(){var e=Yl(!1),n=e[0];return e=em.bind(null,e[1]),_n().memoizedState=e,[n,e]},useMutableSource:function(){},useSyncExternalStore:function(e,n,t){var r=xe,i=_n();if(ve){if(t===void 0)throw Error(u(407));t=t()}else{if(t=n(),Re===null)throw Error(u(349));(ht&30)!==0||Ql(r,n,t)}i.memoizedState=t;var o={value:t,getSnapshot:n};return i.queue=o,Zl(Gl.bind(null,r,o,e),[e]),r.flags|=2048,Cr(9,Kl.bind(null,r,o,t,n),void 0,null),t},useId:function(){var e=_n(),n=Re.identifierPrefix;if(ve){var t=Rn,r=Ln;t=(r&~(1<<32-hn(r)-1)).toString(32)+t,n=":"+n+"R"+t,t=Sr++,0<t&&(n+="H"+t.toString(32)),n+=":"}else t=Zd++,n=":"+n+"r"+t.toString(32)+":";return e.memoizedState=n},unstable_isNewReconciler:!1},sm={readContext:an,useCallback:su,useContext:an,useEffect:ho,useImperativeHandle:ru,useInsertionEffect:eu,useLayoutEffect:nu,useMemo:iu,useReducer:co,useRef:Jl,useState:function(){return co(Nr)},useDebugValue:fo,useDeferredValue:function(e){var n=ln();return ou(n,Pe.memoizedState,e)},useTransition:function(){var e=co(Nr)[0],n=ln().memoizedState;return[e,n]},useMutableSource:$l,useSyncExternalStore:Hl,useId:au,unstable_isNewReconciler:!1},im={readContext:an,useCallback:su,useContext:an,useEffect:ho,useImperativeHandle:ru,useInsertionEffect:eu,useLayoutEffect:nu,useMemo:iu,useReducer:mo,useRef:Jl,useState:function(){return mo(Nr)},useDebugValue:fo,useDeferredValue:function(e){var n=ln();return Pe===null?n.memoizedState=e:ou(n,Pe.memoizedState,e)},useTransition:function(){var e=mo(Nr)[0],n=ln().memoizedState;return[e,n]},useMutableSource:$l,useSyncExternalStore:Hl,useId:au,unstable_isNewReconciler:!1};function gn(e,n){if(e&&e.defaultProps){n=U({},n),e=e.defaultProps;for(var t in e)n[t]===void 0&&(n[t]=e[t]);return n}return n}function po(e,n,t,r){n=e.memoizedState,t=t(r,n),t=t==null?n:U({},n,t),e.memoizedState=t,e.lanes===0&&(e.updateQueue.baseState=t)}var Ns={isMounted:function(e){return(e=e._reactInternals)?ot(e)===e:!1},enqueueSetState:function(e,n,t){e=e._reactInternals;var r=We(),i=Zn(e),o=An(r,i);o.payload=n,t!=null&&(o.callback=t),n=Xn(e,o,i),n!==null&&(xn(n,e,i,r),gs(n,e,i))},enqueueReplaceState:function(e,n,t){e=e._reactInternals;var r=We(),i=Zn(e),o=An(r,i);o.tag=1,o.payload=n,t!=null&&(o.callback=t),n=Xn(e,o,i),n!==null&&(xn(n,e,i,r),gs(n,e,i))},enqueueForceUpdate:function(e,n){e=e._reactInternals;var t=We(),r=Zn(e),i=An(t,r);i.tag=2,n!=null&&(i.callback=n),n=Xn(e,i,r),n!==null&&(xn(n,e,r,t),gs(n,e,r))}};function du(e,n,t,r,i,o,a){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(r,o,a):n.prototype&&n.prototype.isPureReactComponent?!dr(t,r)||!dr(i,o):!0}function mu(e,n,t){var r=!1,i=Qn,o=n.contextType;return typeof o=="object"&&o!==null?o=an(o):(i=He(n)?lt:ze.current,r=n.contextTypes,o=(r=r!=null)?Rt(e,i):Qn),n=new n(t,o),e.memoizedState=n.state!==null&&n.state!==void 0?n.state:null,n.updater=Ns,e.stateNode=n,n._reactInternals=e,r&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=i,e.__reactInternalMemoizedMaskedChildContext=o),n}function hu(e,n,t,r){e=n.state,typeof n.componentWillReceiveProps=="function"&&n.componentWillReceiveProps(t,r),typeof n.UNSAFE_componentWillReceiveProps=="function"&&n.UNSAFE_componentWillReceiveProps(t,r),n.state!==e&&Ns.enqueueReplaceState(n,n.state,null)}function go(e,n,t,r){var i=e.stateNode;i.props=t,i.state=e.memoizedState,i.refs={},no(e);var o=n.contextType;typeof o=="object"&&o!==null?i.context=an(o):(o=He(n)?lt:ze.current,i.context=Rt(e,o)),i.state=e.memoizedState,o=n.getDerivedStateFromProps,typeof o=="function"&&(po(e,n,o,t),i.state=e.memoizedState),typeof n.getDerivedStateFromProps=="function"||typeof i.getSnapshotBeforeUpdate=="function"||typeof i.UNSAFE_componentWillMount!="function"&&typeof i.componentWillMount!="function"||(n=i.state,typeof i.componentWillMount=="function"&&i.componentWillMount(),typeof i.UNSAFE_componentWillMount=="function"&&i.UNSAFE_componentWillMount(),n!==i.state&&Ns.enqueueReplaceState(i,i.state,null),vs(e,t,i,r),i.state=e.memoizedState),typeof i.componentDidMount=="function"&&(e.flags|=4194308)}function Ut(e,n){try{var t="",r=n;do t+=re(r),r=r.return;while(r);var i=t}catch(o){i=`
Error generating stack: `+o.message+`
`+o.stack}return{value:e,source:n,stack:i,digest:null}}function vo(e,n,t){return{value:e,source:null,stack:t??null,digest:n??null}}function yo(e,n){try{console.error(n.value)}catch(t){setTimeout(function(){throw t})}}var om=typeof WeakMap=="function"?WeakMap:Map;function fu(e,n,t){t=An(-1,t),t.tag=3,t.payload={element:null};var r=n.value;return t.callback=function(){Ts||(Ts=!0,Ro=r),yo(e,n)},t}function pu(e,n,t){t=An(-1,t),t.tag=3;var r=e.type.getDerivedStateFromError;if(typeof r=="function"){var i=n.value;t.payload=function(){return r(i)},t.callback=function(){yo(e,n)}}var o=e.stateNode;return o!==null&&typeof o.componentDidCatch=="function"&&(t.callback=function(){yo(e,n),typeof r!="function"&&(Yn===null?Yn=new Set([this]):Yn.add(this));var a=n.stack;this.componentDidCatch(n.value,{componentStack:a!==null?a:""})}),t}function gu(e,n,t){var r=e.pingCache;if(r===null){r=e.pingCache=new om;var i=new Set;r.set(n,i)}else i=r.get(n),i===void 0&&(i=new Set,r.set(n,i));i.has(t)||(i.add(t),e=km.bind(null,e,n,t),n.then(e,e))}function vu(e){do{var n;if((n=e.tag===13)&&(n=e.memoizedState,n=n!==null?n.dehydrated!==null:!0),n)return e;e=e.return}while(e!==null);return null}function yu(e,n,t,r,i){return(e.mode&1)===0?(e===n?e.flags|=65536:(e.flags|=128,t.flags|=131072,t.flags&=-52805,t.tag===1&&(t.alternate===null?t.tag=17:(n=An(-1,1),n.tag=2,Xn(t,n,1))),t.lanes|=1),e):(e.flags|=65536,e.lanes=i,e)}var am=pe.ReactCurrentOwner,Qe=!1;function Ue(e,n,t,r){n.child=e===null?Fl(n,null,t,r):zt(n,e.child,t,r)}function xu(e,n,t,r,i){t=t.render;var o=n.ref;return Ot(n,i),r=lo(e,n,t,r,o,i),t=uo(),e!==null&&!Qe?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~i,In(e,n,i)):(ve&&t&&Hi(n),n.flags|=1,Ue(e,n,r,i),n.child)}function ku(e,n,t,r,i){if(e===null){var o=t.type;return typeof o=="function"&&!Bo(o)&&o.defaultProps===void 0&&t.compare===null&&t.defaultProps===void 0?(n.tag=15,n.type=o,wu(e,n,o,r,i)):(e=zs(t.type,null,r,n,n.mode,i),e.ref=n.ref,e.return=n,n.child=e)}if(o=e.child,(e.lanes&i)===0){var a=o.memoizedProps;if(t=t.compare,t=t!==null?t:dr,t(a,r)&&e.ref===n.ref)return In(e,n,i)}return n.flags|=1,e=nt(o,r),e.ref=n.ref,e.return=n,n.child=e}function wu(e,n,t,r,i){if(e!==null){var o=e.memoizedProps;if(dr(o,r)&&e.ref===n.ref)if(Qe=!1,n.pendingProps=r=o,(e.lanes&i)!==0)(e.flags&131072)!==0&&(Qe=!0);else return n.lanes=e.lanes,In(e,n,i)}return xo(e,n,t,r,i)}function ju(e,n,t){var r=n.pendingProps,i=r.children,o=e!==null?e.memoizedState:null;if(r.mode==="hidden")if((n.mode&1)===0)n.memoizedState={baseLanes:0,cachePool:null,transitions:null},ce(Vt,rn),rn|=t;else{if((t&1073741824)===0)return e=o!==null?o.baseLanes|t:t,n.lanes=n.childLanes=1073741824,n.memoizedState={baseLanes:e,cachePool:null,transitions:null},n.updateQueue=null,ce(Vt,rn),rn|=e,null;n.memoizedState={baseLanes:0,cachePool:null,transitions:null},r=o!==null?o.baseLanes:t,ce(Vt,rn),rn|=r}else o!==null?(r=o.baseLanes|t,n.memoizedState=null):r=t,ce(Vt,rn),rn|=r;return Ue(e,n,i,t),n.child}function Su(e,n){var t=n.ref;(e===null&&t!==null||e!==null&&e.ref!==t)&&(n.flags|=512,n.flags|=2097152)}function xo(e,n,t,r,i){var o=He(t)?lt:ze.current;return o=Rt(n,o),Ot(n,i),t=lo(e,n,t,r,o,i),r=uo(),e!==null&&!Qe?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~i,In(e,n,i)):(ve&&r&&Hi(n),n.flags|=1,Ue(e,n,t,i),n.child)}function Nu(e,n,t,r,i){if(He(t)){var o=!0;ls(n)}else o=!1;if(Ot(n,i),n.stateNode===null)_s(e,n),mu(n,t,r),go(n,t,r,i),r=!0;else if(e===null){var a=n.stateNode,d=n.memoizedProps;a.props=d;var m=a.context,x=t.contextType;typeof x=="object"&&x!==null?x=an(x):(x=He(t)?lt:ze.current,x=Rt(n,x));var _=t.getDerivedStateFromProps,b=typeof _=="function"||typeof a.getSnapshotBeforeUpdate=="function";b||typeof a.UNSAFE_componentWillReceiveProps!="function"&&typeof a.componentWillReceiveProps!="function"||(d!==r||m!==x)&&hu(n,a,r,x),Gn=!1;var N=n.memoizedState;a.state=N,vs(n,r,a,i),m=n.memoizedState,d!==r||N!==m||$e.current||Gn?(typeof _=="function"&&(po(n,t,_,r),m=n.memoizedState),(d=Gn||du(n,t,d,r,N,m,x))?(b||typeof a.UNSAFE_componentWillMount!="function"&&typeof a.componentWillMount!="function"||(typeof a.componentWillMount=="function"&&a.componentWillMount(),typeof a.UNSAFE_componentWillMount=="function"&&a.UNSAFE_componentWillMount()),typeof a.componentDidMount=="function"&&(n.flags|=4194308)):(typeof a.componentDidMount=="function"&&(n.flags|=4194308),n.memoizedProps=r,n.memoizedState=m),a.props=r,a.state=m,a.context=x,r=d):(typeof a.componentDidMount=="function"&&(n.flags|=4194308),r=!1)}else{a=n.stateNode,Bl(e,n),d=n.memoizedProps,x=n.type===n.elementType?d:gn(n.type,d),a.props=x,b=n.pendingProps,N=a.context,m=t.contextType,typeof m=="object"&&m!==null?m=an(m):(m=He(t)?lt:ze.current,m=Rt(n,m));var z=t.getDerivedStateFromProps;(_=typeof z=="function"||typeof a.getSnapshotBeforeUpdate=="function")||typeof a.UNSAFE_componentWillReceiveProps!="function"&&typeof a.componentWillReceiveProps!="function"||(d!==b||N!==m)&&hu(n,a,r,m),Gn=!1,N=n.memoizedState,a.state=N,vs(n,r,a,i);var W=n.memoizedState;d!==b||N!==W||$e.current||Gn?(typeof z=="function"&&(po(n,t,z,r),W=n.memoizedState),(x=Gn||du(n,t,x,r,N,W,m)||!1)?(_||typeof a.UNSAFE_componentWillUpdate!="function"&&typeof a.componentWillUpdate!="function"||(typeof a.componentWillUpdate=="function"&&a.componentWillUpdate(r,W,m),typeof a.UNSAFE_componentWillUpdate=="function"&&a.UNSAFE_componentWillUpdate(r,W,m)),typeof a.componentDidUpdate=="function"&&(n.flags|=4),typeof a.getSnapshotBeforeUpdate=="function"&&(n.flags|=1024)):(typeof a.componentDidUpdate!="function"||d===e.memoizedProps&&N===e.memoizedState||(n.flags|=4),typeof a.getSnapshotBeforeUpdate!="function"||d===e.memoizedProps&&N===e.memoizedState||(n.flags|=1024),n.memoizedProps=r,n.memoizedState=W),a.props=r,a.state=W,a.context=m,r=x):(typeof a.componentDidUpdate!="function"||d===e.memoizedProps&&N===e.memoizedState||(n.flags|=4),typeof a.getSnapshotBeforeUpdate!="function"||d===e.memoizedProps&&N===e.memoizedState||(n.flags|=1024),r=!1)}return ko(e,n,t,r,o,i)}function ko(e,n,t,r,i,o){Su(e,n);var a=(n.flags&128)!==0;if(!r&&!a)return i&&Pl(n,t,!1),In(e,n,o);r=n.stateNode,am.current=n;var d=a&&typeof t.getDerivedStateFromError!="function"?null:r.render();return n.flags|=1,e!==null&&a?(n.child=zt(n,e.child,null,o),n.child=zt(n,null,d,o)):Ue(e,n,d,o),n.memoizedState=r.state,i&&Pl(n,t,!0),n.child}function Cu(e){var n=e.stateNode;n.pendingContext?bl(e,n.pendingContext,n.pendingContext!==n.context):n.context&&bl(e,n.context,!1),to(e,n.containerInfo)}function _u(e,n,t,r,i){return It(),Xi(i),n.flags|=256,Ue(e,n,t,r),n.child}var wo={dehydrated:null,treeContext:null,retryLane:0};function jo(e){return{baseLanes:e,cachePool:null,transitions:null}}function bu(e,n,t){var r=n.pendingProps,i=ye.current,o=!1,a=(n.flags&128)!==0,d;if((d=a)||(d=e!==null&&e.memoizedState===null?!1:(i&2)!==0),d?(o=!0,n.flags&=-129):(e===null||e.memoizedState!==null)&&(i|=1),ce(ye,i&1),e===null)return Gi(n),e=n.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?((n.mode&1)===0?n.lanes=1:e.data==="$!"?n.lanes=8:n.lanes=1073741824,null):(a=r.children,e=r.fallback,o?(r=n.mode,o=n.child,a={mode:"hidden",children:a},(r&1)===0&&o!==null?(o.childLanes=0,o.pendingProps=a):o=Fs(a,r,0,null),e=yt(e,r,t,null),o.return=n,e.return=n,o.sibling=e,n.child=o,n.child.memoizedState=jo(t),n.memoizedState=wo,e):So(n,a));if(i=e.memoizedState,i!==null&&(d=i.dehydrated,d!==null))return lm(e,n,a,r,d,i,t);if(o){o=r.fallback,a=n.mode,i=e.child,d=i.sibling;var m={mode:"hidden",children:r.children};return(a&1)===0&&n.child!==i?(r=n.child,r.childLanes=0,r.pendingProps=m,n.deletions=null):(r=nt(i,m),r.subtreeFlags=i.subtreeFlags&14680064),d!==null?o=nt(d,o):(o=yt(o,a,t,null),o.flags|=2),o.return=n,r.return=n,r.sibling=o,n.child=r,r=o,o=n.child,a=e.child.memoizedState,a=a===null?jo(t):{baseLanes:a.baseLanes|t,cachePool:null,transitions:a.transitions},o.memoizedState=a,o.childLanes=e.childLanes&~t,n.memoizedState=wo,r}return o=e.child,e=o.sibling,r=nt(o,{mode:"visible",children:r.children}),(n.mode&1)===0&&(r.lanes=t),r.return=n,r.sibling=null,e!==null&&(t=n.deletions,t===null?(n.deletions=[e],n.flags|=16):t.push(e)),n.child=r,n.memoizedState=null,r}function So(e,n){return n=Fs({mode:"visible",children:n},e.mode,0,null),n.return=e,e.child=n}function Cs(e,n,t,r){return r!==null&&Xi(r),zt(n,e.child,null,t),e=So(n,n.pendingProps.children),e.flags|=2,n.memoizedState=null,e}function lm(e,n,t,r,i,o,a){if(t)return n.flags&256?(n.flags&=-257,r=vo(Error(u(422))),Cs(e,n,a,r)):n.memoizedState!==null?(n.child=e.child,n.flags|=128,null):(o=r.fallback,i=n.mode,r=Fs({mode:"visible",children:r.children},i,0,null),o=yt(o,i,a,null),o.flags|=2,r.return=n,o.return=n,r.sibling=o,n.child=r,(n.mode&1)!==0&&zt(n,e.child,null,a),n.child.memoizedState=jo(a),n.memoizedState=wo,o);if((n.mode&1)===0)return Cs(e,n,a,null);if(i.data==="$!"){if(r=i.nextSibling&&i.nextSibling.dataset,r)var d=r.dgst;return r=d,o=Error(u(419)),r=vo(o,r,void 0),Cs(e,n,a,r)}if(d=(a&e.childLanes)!==0,Qe||d){if(r=Re,r!==null){switch(a&-a){case 4:i=2;break;case 16:i=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:i=32;break;case 536870912:i=268435456;break;default:i=0}i=(i&(r.suspendedLanes|a))!==0?0:i,i!==0&&i!==o.retryLane&&(o.retryLane=i,Dn(e,i),xn(r,e,i,-1))}return Oo(),r=vo(Error(u(421))),Cs(e,n,a,r)}return i.data==="$?"?(n.flags|=128,n.child=e.child,n=wm.bind(null,e),i._reactRetry=n,null):(e=o.treeContext,tn=$n(i.nextSibling),nn=n,ve=!0,pn=null,e!==null&&(sn[on++]=Ln,sn[on++]=Rn,sn[on++]=ut,Ln=e.id,Rn=e.overflow,ut=n),n=So(n,r.children),n.flags|=4096,n)}function Eu(e,n,t){e.lanes|=n;var r=e.alternate;r!==null&&(r.lanes|=n),Zi(e.return,n,t)}function No(e,n,t,r,i){var o=e.memoizedState;o===null?e.memoizedState={isBackwards:n,rendering:null,renderingStartTime:0,last:r,tail:t,tailMode:i}:(o.isBackwards=n,o.rendering=null,o.renderingStartTime=0,o.last=r,o.tail=t,o.tailMode=i)}function Pu(e,n,t){var r=n.pendingProps,i=r.revealOrder,o=r.tail;if(Ue(e,n,r.children,t),r=ye.current,(r&2)!==0)r=r&1|2,n.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=n.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Eu(e,t,n);else if(e.tag===19)Eu(e,t,n);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===n)break e;for(;e.sibling===null;){if(e.return===null||e.return===n)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}r&=1}if(ce(ye,r),(n.mode&1)===0)n.memoizedState=null;else switch(i){case"forwards":for(t=n.child,i=null;t!==null;)e=t.alternate,e!==null&&ys(e)===null&&(i=t),t=t.sibling;t=i,t===null?(i=n.child,n.child=null):(i=t.sibling,t.sibling=null),No(n,!1,i,t,o);break;case"backwards":for(t=null,i=n.child,n.child=null;i!==null;){if(e=i.alternate,e!==null&&ys(e)===null){n.child=i;break}e=i.sibling,i.sibling=t,t=i,i=e}No(n,!0,t,null,o);break;case"together":No(n,!1,null,null,void 0);break;default:n.memoizedState=null}return n.child}function _s(e,n){(n.mode&1)===0&&e!==null&&(e.alternate=null,n.alternate=null,n.flags|=2)}function In(e,n,t){if(e!==null&&(n.dependencies=e.dependencies),ft|=n.lanes,(t&n.childLanes)===0)return null;if(e!==null&&n.child!==e.child)throw Error(u(153));if(n.child!==null){for(e=n.child,t=nt(e,e.pendingProps),n.child=t,t.return=n;e.sibling!==null;)e=e.sibling,t=t.sibling=nt(e,e.pendingProps),t.return=n;t.sibling=null}return n.child}function um(e,n,t){switch(n.tag){case 3:Cu(n),It();break;case 5:Vl(n);break;case 1:He(n.type)&&ls(n);break;case 4:to(n,n.stateNode.containerInfo);break;case 10:var r=n.type._context,i=n.memoizedProps.value;ce(fs,r._currentValue),r._currentValue=i;break;case 13:if(r=n.memoizedState,r!==null)return r.dehydrated!==null?(ce(ye,ye.current&1),n.flags|=128,null):(t&n.child.childLanes)!==0?bu(e,n,t):(ce(ye,ye.current&1),e=In(e,n,t),e!==null?e.sibling:null);ce(ye,ye.current&1);break;case 19:if(r=(t&n.childLanes)!==0,(e.flags&128)!==0){if(r)return Pu(e,n,t);n.flags|=128}if(i=n.memoizedState,i!==null&&(i.rendering=null,i.tail=null,i.lastEffect=null),ce(ye,ye.current),r)break;return null;case 22:case 23:return n.lanes=0,ju(e,n,t)}return In(e,n,t)}var Mu,Co,Tu,Lu;Mu=function(e,n){for(var t=n.child;t!==null;){if(t.tag===5||t.tag===6)e.appendChild(t.stateNode);else if(t.tag!==4&&t.child!==null){t.child.return=t,t=t.child;continue}if(t===n)break;for(;t.sibling===null;){if(t.return===null||t.return===n)return;t=t.return}t.sibling.return=t.return,t=t.sibling}},Co=function(){},Tu=function(e,n,t,r){var i=e.memoizedProps;if(i!==r){e=n.stateNode,mt(Cn.current);var o=null;switch(t){case"input":i=Zs(e,i),r=Zs(e,r),o=[];break;case"select":i=U({},i,{value:void 0}),r=U({},r,{value:void 0}),o=[];break;case"textarea":i=ti(e,i),r=ti(e,r),o=[];break;default:typeof i.onClick!="function"&&typeof r.onClick=="function"&&(e.onclick=is)}si(t,r);var a;t=null;for(x in i)if(!r.hasOwnProperty(x)&&i.hasOwnProperty(x)&&i[x]!=null)if(x==="style"){var d=i[x];for(a in d)d.hasOwnProperty(a)&&(t||(t={}),t[a]="")}else x!=="dangerouslySetInnerHTML"&&x!=="children"&&x!=="suppressContentEditableWarning"&&x!=="suppressHydrationWarning"&&x!=="autoFocus"&&(y.hasOwnProperty(x)?o||(o=[]):(o=o||[]).push(x,null));for(x in r){var m=r[x];if(d=i!=null?i[x]:void 0,r.hasOwnProperty(x)&&m!==d&&(m!=null||d!=null))if(x==="style")if(d){for(a in d)!d.hasOwnProperty(a)||m&&m.hasOwnProperty(a)||(t||(t={}),t[a]="");for(a in m)m.hasOwnProperty(a)&&d[a]!==m[a]&&(t||(t={}),t[a]=m[a])}else t||(o||(o=[]),o.push(x,t)),t=m;else x==="dangerouslySetInnerHTML"?(m=m?m.__html:void 0,d=d?d.__html:void 0,m!=null&&d!==m&&(o=o||[]).push(x,m)):x==="children"?typeof m!="string"&&typeof m!="number"||(o=o||[]).push(x,""+m):x!=="suppressContentEditableWarning"&&x!=="suppressHydrationWarning"&&(y.hasOwnProperty(x)?(m!=null&&x==="onScroll"&&me("scroll",e),o||d===m||(o=[])):(o=o||[]).push(x,m))}t&&(o=o||[]).push("style",t);var x=o;(n.updateQueue=x)&&(n.flags|=4)}},Lu=function(e,n,t,r){t!==r&&(n.flags|=4)};function _r(e,n){if(!ve)switch(e.tailMode){case"hidden":n=e.tail;for(var t=null;n!==null;)n.alternate!==null&&(t=n),n=n.sibling;t===null?e.tail=null:t.sibling=null;break;case"collapsed":t=e.tail;for(var r=null;t!==null;)t.alternate!==null&&(r=t),t=t.sibling;r===null?n||e.tail===null?e.tail=null:e.tail.sibling=null:r.sibling=null}}function Oe(e){var n=e.alternate!==null&&e.alternate.child===e.child,t=0,r=0;if(n)for(var i=e.child;i!==null;)t|=i.lanes|i.childLanes,r|=i.subtreeFlags&14680064,r|=i.flags&14680064,i.return=e,i=i.sibling;else for(i=e.child;i!==null;)t|=i.lanes|i.childLanes,r|=i.subtreeFlags,r|=i.flags,i.return=e,i=i.sibling;return e.subtreeFlags|=r,e.childLanes=t,n}function cm(e,n,t){var r=n.pendingProps;switch(Qi(n),n.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Oe(n),null;case 1:return He(n.type)&&as(),Oe(n),null;case 3:return r=n.stateNode,Bt(),he($e),he(ze),io(),r.pendingContext&&(r.context=r.pendingContext,r.pendingContext=null),(e===null||e.child===null)&&(ms(n)?n.flags|=4:e===null||e.memoizedState.isDehydrated&&(n.flags&256)===0||(n.flags|=1024,pn!==null&&(Io(pn),pn=null))),Co(e,n),Oe(n),null;case 5:ro(n);var i=mt(wr.current);if(t=n.type,e!==null&&n.stateNode!=null)Tu(e,n,t,r,i),e.ref!==n.ref&&(n.flags|=512,n.flags|=2097152);else{if(!r){if(n.stateNode===null)throw Error(u(166));return Oe(n),null}if(e=mt(Cn.current),ms(n)){r=n.stateNode,t=n.type;var o=n.memoizedProps;switch(r[Nn]=n,r[gr]=o,e=(n.mode&1)!==0,t){case"dialog":me("cancel",r),me("close",r);break;case"iframe":case"object":case"embed":me("load",r);break;case"video":case"audio":for(i=0;i<hr.length;i++)me(hr[i],r);break;case"source":me("error",r);break;case"img":case"image":case"link":me("error",r),me("load",r);break;case"details":me("toggle",r);break;case"input":ma(r,o),me("invalid",r);break;case"select":r._wrapperState={wasMultiple:!!o.multiple},me("invalid",r);break;case"textarea":pa(r,o),me("invalid",r)}si(t,o),i=null;for(var a in o)if(o.hasOwnProperty(a)){var d=o[a];a==="children"?typeof d=="string"?r.textContent!==d&&(o.suppressHydrationWarning!==!0&&ss(r.textContent,d,e),i=["children",d]):typeof d=="number"&&r.textContent!==""+d&&(o.suppressHydrationWarning!==!0&&ss(r.textContent,d,e),i=["children",""+d]):y.hasOwnProperty(a)&&d!=null&&a==="onScroll"&&me("scroll",r)}switch(t){case"input":Ar(r),fa(r,o,!0);break;case"textarea":Ar(r),va(r);break;case"select":case"option":break;default:typeof o.onClick=="function"&&(r.onclick=is)}r=i,n.updateQueue=r,r!==null&&(n.flags|=4)}else{a=i.nodeType===9?i:i.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=ya(t)),e==="http://www.w3.org/1999/xhtml"?t==="script"?(e=a.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof r.is=="string"?e=a.createElement(t,{is:r.is}):(e=a.createElement(t),t==="select"&&(a=e,r.multiple?a.multiple=!0:r.size&&(a.size=r.size))):e=a.createElementNS(e,t),e[Nn]=n,e[gr]=r,Mu(e,n,!1,!1),n.stateNode=e;e:{switch(a=ii(t,r),t){case"dialog":me("cancel",e),me("close",e),i=r;break;case"iframe":case"object":case"embed":me("load",e),i=r;break;case"video":case"audio":for(i=0;i<hr.length;i++)me(hr[i],e);i=r;break;case"source":me("error",e),i=r;break;case"img":case"image":case"link":me("error",e),me("load",e),i=r;break;case"details":me("toggle",e),i=r;break;case"input":ma(e,r),i=Zs(e,r),me("invalid",e);break;case"option":i=r;break;case"select":e._wrapperState={wasMultiple:!!r.multiple},i=U({},r,{value:void 0}),me("invalid",e);break;case"textarea":pa(e,r),i=ti(e,r),me("invalid",e);break;default:i=r}si(t,i),d=i;for(o in d)if(d.hasOwnProperty(o)){var m=d[o];o==="style"?wa(e,m):o==="dangerouslySetInnerHTML"?(m=m?m.__html:void 0,m!=null&&xa(e,m)):o==="children"?typeof m=="string"?(t!=="textarea"||m!=="")&&Gt(e,m):typeof m=="number"&&Gt(e,""+m):o!=="suppressContentEditableWarning"&&o!=="suppressHydrationWarning"&&o!=="autoFocus"&&(y.hasOwnProperty(o)?m!=null&&o==="onScroll"&&me("scroll",e):m!=null&&je(e,o,m,a))}switch(t){case"input":Ar(e),fa(e,r,!1);break;case"textarea":Ar(e),va(e);break;case"option":r.value!=null&&e.setAttribute("value",""+oe(r.value));break;case"select":e.multiple=!!r.multiple,o=r.value,o!=null?wt(e,!!r.multiple,o,!1):r.defaultValue!=null&&wt(e,!!r.multiple,r.defaultValue,!0);break;default:typeof i.onClick=="function"&&(e.onclick=is)}switch(t){case"button":case"input":case"select":case"textarea":r=!!r.autoFocus;break e;case"img":r=!0;break e;default:r=!1}}r&&(n.flags|=4)}n.ref!==null&&(n.flags|=512,n.flags|=2097152)}return Oe(n),null;case 6:if(e&&n.stateNode!=null)Lu(e,n,e.memoizedProps,r);else{if(typeof r!="string"&&n.stateNode===null)throw Error(u(166));if(t=mt(wr.current),mt(Cn.current),ms(n)){if(r=n.stateNode,t=n.memoizedProps,r[Nn]=n,(o=r.nodeValue!==t)&&(e=nn,e!==null))switch(e.tag){case 3:ss(r.nodeValue,t,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&ss(r.nodeValue,t,(e.mode&1)!==0)}o&&(n.flags|=4)}else r=(t.nodeType===9?t:t.ownerDocument).createTextNode(r),r[Nn]=n,n.stateNode=r}return Oe(n),null;case 13:if(he(ye),r=n.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(ve&&tn!==null&&(n.mode&1)!==0&&(n.flags&128)===0)Al(),It(),n.flags|=98560,o=!1;else if(o=ms(n),r!==null&&r.dehydrated!==null){if(e===null){if(!o)throw Error(u(318));if(o=n.memoizedState,o=o!==null?o.dehydrated:null,!o)throw Error(u(317));o[Nn]=n}else It(),(n.flags&128)===0&&(n.memoizedState=null),n.flags|=4;Oe(n),o=!1}else pn!==null&&(Io(pn),pn=null),o=!0;if(!o)return n.flags&65536?n:null}return(n.flags&128)!==0?(n.lanes=t,n):(r=r!==null,r!==(e!==null&&e.memoizedState!==null)&&r&&(n.child.flags|=8192,(n.mode&1)!==0&&(e===null||(ye.current&1)!==0?Me===0&&(Me=3):Oo())),n.updateQueue!==null&&(n.flags|=4),Oe(n),null);case 4:return Bt(),Co(e,n),e===null&&fr(n.stateNode.containerInfo),Oe(n),null;case 10:return Ji(n.type._context),Oe(n),null;case 17:return He(n.type)&&as(),Oe(n),null;case 19:if(he(ye),o=n.memoizedState,o===null)return Oe(n),null;if(r=(n.flags&128)!==0,a=o.rendering,a===null)if(r)_r(o,!1);else{if(Me!==0||e!==null&&(e.flags&128)!==0)for(e=n.child;e!==null;){if(a=ys(e),a!==null){for(n.flags|=128,_r(o,!1),r=a.updateQueue,r!==null&&(n.updateQueue=r,n.flags|=4),n.subtreeFlags=0,r=t,t=n.child;t!==null;)o=t,e=r,o.flags&=14680066,a=o.alternate,a===null?(o.childLanes=0,o.lanes=e,o.child=null,o.subtreeFlags=0,o.memoizedProps=null,o.memoizedState=null,o.updateQueue=null,o.dependencies=null,o.stateNode=null):(o.childLanes=a.childLanes,o.lanes=a.lanes,o.child=a.child,o.subtreeFlags=0,o.deletions=null,o.memoizedProps=a.memoizedProps,o.memoizedState=a.memoizedState,o.updateQueue=a.updateQueue,o.type=a.type,e=a.dependencies,o.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),t=t.sibling;return ce(ye,ye.current&1|2),n.child}e=e.sibling}o.tail!==null&&Se()>$t&&(n.flags|=128,r=!0,_r(o,!1),n.lanes=4194304)}else{if(!r)if(e=ys(a),e!==null){if(n.flags|=128,r=!0,t=e.updateQueue,t!==null&&(n.updateQueue=t,n.flags|=4),_r(o,!0),o.tail===null&&o.tailMode==="hidden"&&!a.alternate&&!ve)return Oe(n),null}else 2*Se()-o.renderingStartTime>$t&&t!==1073741824&&(n.flags|=128,r=!0,_r(o,!1),n.lanes=4194304);o.isBackwards?(a.sibling=n.child,n.child=a):(t=o.last,t!==null?t.sibling=a:n.child=a,o.last=a)}return o.tail!==null?(n=o.tail,o.rendering=n,o.tail=n.sibling,o.renderingStartTime=Se(),n.sibling=null,t=ye.current,ce(ye,r?t&1|2:t&1),n):(Oe(n),null);case 22:case 23:return Fo(),r=n.memoizedState!==null,e!==null&&e.memoizedState!==null!==r&&(n.flags|=8192),r&&(n.mode&1)!==0?(rn&1073741824)!==0&&(Oe(n),n.subtreeFlags&6&&(n.flags|=8192)):Oe(n),null;case 24:return null;case 25:return null}throw Error(u(156,n.tag))}function dm(e,n){switch(Qi(n),n.tag){case 1:return He(n.type)&&as(),e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 3:return Bt(),he($e),he(ze),io(),e=n.flags,(e&65536)!==0&&(e&128)===0?(n.flags=e&-65537|128,n):null;case 5:return ro(n),null;case 13:if(he(ye),e=n.memoizedState,e!==null&&e.dehydrated!==null){if(n.alternate===null)throw Error(u(340));It()}return e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 19:return he(ye),null;case 4:return Bt(),null;case 10:return Ji(n.type._context),null;case 22:case 23:return Fo(),null;case 24:return null;default:return null}}var bs=!1,Be=!1,mm=typeof WeakSet=="function"?WeakSet:Set,B=null;function Wt(e,n){var t=e.ref;if(t!==null)if(typeof t=="function")try{t(null)}catch(r){we(e,n,r)}else t.current=null}function _o(e,n,t){try{t()}catch(r){we(e,n,r)}}var Ru=!1;function hm(e,n){if(zi=Kr,e=dl(),Pi(e)){if("selectionStart"in e)var t={start:e.selectionStart,end:e.selectionEnd};else e:{t=(t=e.ownerDocument)&&t.defaultView||window;var r=t.getSelection&&t.getSelection();if(r&&r.rangeCount!==0){t=r.anchorNode;var i=r.anchorOffset,o=r.focusNode;r=r.focusOffset;try{t.nodeType,o.nodeType}catch{t=null;break e}var a=0,d=-1,m=-1,x=0,_=0,b=e,N=null;n:for(;;){for(var z;b!==t||i!==0&&b.nodeType!==3||(d=a+i),b!==o||r!==0&&b.nodeType!==3||(m=a+r),b.nodeType===3&&(a+=b.nodeValue.length),(z=b.firstChild)!==null;)N=b,b=z;for(;;){if(b===e)break n;if(N===t&&++x===i&&(d=a),N===o&&++_===r&&(m=a),(z=b.nextSibling)!==null)break;b=N,N=b.parentNode}b=z}t=d===-1||m===-1?null:{start:d,end:m}}else t=null}t=t||{start:0,end:0}}else t=null;for(Fi={focusedElem:e,selectionRange:t},Kr=!1,B=n;B!==null;)if(n=B,e=n.child,(n.subtreeFlags&1028)!==0&&e!==null)e.return=n,B=e;else for(;B!==null;){n=B;try{var W=n.alternate;if((n.flags&1024)!==0)switch(n.tag){case 0:case 11:case 15:break;case 1:if(W!==null){var V=W.memoizedProps,Ne=W.memoizedState,g=n.stateNode,h=g.getSnapshotBeforeUpdate(n.elementType===n.type?V:gn(n.type,V),Ne);g.__reactInternalSnapshotBeforeUpdate=h}break;case 3:var v=n.stateNode.containerInfo;v.nodeType===1?v.textContent="":v.nodeType===9&&v.documentElement&&v.removeChild(v.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(u(163))}}catch(T){we(n,n.return,T)}if(e=n.sibling,e!==null){e.return=n.return,B=e;break}B=n.return}return W=Ru,Ru=!1,W}function br(e,n,t){var r=n.updateQueue;if(r=r!==null?r.lastEffect:null,r!==null){var i=r=r.next;do{if((i.tag&e)===e){var o=i.destroy;i.destroy=void 0,o!==void 0&&_o(n,t,o)}i=i.next}while(i!==r)}}function Es(e,n){if(n=n.updateQueue,n=n!==null?n.lastEffect:null,n!==null){var t=n=n.next;do{if((t.tag&e)===e){var r=t.create;t.destroy=r()}t=t.next}while(t!==n)}}function bo(e){var n=e.ref;if(n!==null){var t=e.stateNode;switch(e.tag){case 5:e=t;break;default:e=t}typeof n=="function"?n(e):n.current=e}}function Du(e){var n=e.alternate;n!==null&&(e.alternate=null,Du(n)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(n=e.stateNode,n!==null&&(delete n[Nn],delete n[gr],delete n[Wi],delete n[Xd],delete n[qd])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function Au(e){return e.tag===5||e.tag===3||e.tag===4}function Iu(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||Au(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Eo(e,n,t){var r=e.tag;if(r===5||r===6)e=e.stateNode,n?t.nodeType===8?t.parentNode.insertBefore(e,n):t.insertBefore(e,n):(t.nodeType===8?(n=t.parentNode,n.insertBefore(e,t)):(n=t,n.appendChild(e)),t=t._reactRootContainer,t!=null||n.onclick!==null||(n.onclick=is));else if(r!==4&&(e=e.child,e!==null))for(Eo(e,n,t),e=e.sibling;e!==null;)Eo(e,n,t),e=e.sibling}function Po(e,n,t){var r=e.tag;if(r===5||r===6)e=e.stateNode,n?t.insertBefore(e,n):t.appendChild(e);else if(r!==4&&(e=e.child,e!==null))for(Po(e,n,t),e=e.sibling;e!==null;)Po(e,n,t),e=e.sibling}var Ae=null,vn=!1;function qn(e,n,t){for(t=t.child;t!==null;)zu(e,n,t),t=t.sibling}function zu(e,n,t){if(Sn&&typeof Sn.onCommitFiberUnmount=="function")try{Sn.onCommitFiberUnmount(Ur,t)}catch{}switch(t.tag){case 5:Be||Wt(t,n);case 6:var r=Ae,i=vn;Ae=null,qn(e,n,t),Ae=r,vn=i,Ae!==null&&(vn?(e=Ae,t=t.stateNode,e.nodeType===8?e.parentNode.removeChild(t):e.removeChild(t)):Ae.removeChild(t.stateNode));break;case 18:Ae!==null&&(vn?(e=Ae,t=t.stateNode,e.nodeType===8?Ui(e.parentNode,t):e.nodeType===1&&Ui(e,t),ir(e)):Ui(Ae,t.stateNode));break;case 4:r=Ae,i=vn,Ae=t.stateNode.containerInfo,vn=!0,qn(e,n,t),Ae=r,vn=i;break;case 0:case 11:case 14:case 15:if(!Be&&(r=t.updateQueue,r!==null&&(r=r.lastEffect,r!==null))){i=r=r.next;do{var o=i,a=o.destroy;o=o.tag,a!==void 0&&((o&2)!==0||(o&4)!==0)&&_o(t,n,a),i=i.next}while(i!==r)}qn(e,n,t);break;case 1:if(!Be&&(Wt(t,n),r=t.stateNode,typeof r.componentWillUnmount=="function"))try{r.props=t.memoizedProps,r.state=t.memoizedState,r.componentWillUnmount()}catch(d){we(t,n,d)}qn(e,n,t);break;case 21:qn(e,n,t);break;case 22:t.mode&1?(Be=(r=Be)||t.memoizedState!==null,qn(e,n,t),Be=r):qn(e,n,t);break;default:qn(e,n,t)}}function Fu(e){var n=e.updateQueue;if(n!==null){e.updateQueue=null;var t=e.stateNode;t===null&&(t=e.stateNode=new mm),n.forEach(function(r){var i=jm.bind(null,e,r);t.has(r)||(t.add(r),r.then(i,i))})}}function yn(e,n){var t=n.deletions;if(t!==null)for(var r=0;r<t.length;r++){var i=t[r];try{var o=e,a=n,d=a;e:for(;d!==null;){switch(d.tag){case 5:Ae=d.stateNode,vn=!1;break e;case 3:Ae=d.stateNode.containerInfo,vn=!0;break e;case 4:Ae=d.stateNode.containerInfo,vn=!0;break e}d=d.return}if(Ae===null)throw Error(u(160));zu(o,a,i),Ae=null,vn=!1;var m=i.alternate;m!==null&&(m.return=null),i.return=null}catch(x){we(i,n,x)}}if(n.subtreeFlags&12854)for(n=n.child;n!==null;)Ou(n,e),n=n.sibling}function Ou(e,n){var t=e.alternate,r=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(yn(n,e),bn(e),r&4){try{br(3,e,e.return),Es(3,e)}catch(V){we(e,e.return,V)}try{br(5,e,e.return)}catch(V){we(e,e.return,V)}}break;case 1:yn(n,e),bn(e),r&512&&t!==null&&Wt(t,t.return);break;case 5:if(yn(n,e),bn(e),r&512&&t!==null&&Wt(t,t.return),e.flags&32){var i=e.stateNode;try{Gt(i,"")}catch(V){we(e,e.return,V)}}if(r&4&&(i=e.stateNode,i!=null)){var o=e.memoizedProps,a=t!==null?t.memoizedProps:o,d=e.type,m=e.updateQueue;if(e.updateQueue=null,m!==null)try{d==="input"&&o.type==="radio"&&o.name!=null&&ha(i,o),ii(d,a);var x=ii(d,o);for(a=0;a<m.length;a+=2){var _=m[a],b=m[a+1];_==="style"?wa(i,b):_==="dangerouslySetInnerHTML"?xa(i,b):_==="children"?Gt(i,b):je(i,_,b,x)}switch(d){case"input":ei(i,o);break;case"textarea":ga(i,o);break;case"select":var N=i._wrapperState.wasMultiple;i._wrapperState.wasMultiple=!!o.multiple;var z=o.value;z!=null?wt(i,!!o.multiple,z,!1):N!==!!o.multiple&&(o.defaultValue!=null?wt(i,!!o.multiple,o.defaultValue,!0):wt(i,!!o.multiple,o.multiple?[]:"",!1))}i[gr]=o}catch(V){we(e,e.return,V)}}break;case 6:if(yn(n,e),bn(e),r&4){if(e.stateNode===null)throw Error(u(162));i=e.stateNode,o=e.memoizedProps;try{i.nodeValue=o}catch(V){we(e,e.return,V)}}break;case 3:if(yn(n,e),bn(e),r&4&&t!==null&&t.memoizedState.isDehydrated)try{ir(n.containerInfo)}catch(V){we(e,e.return,V)}break;case 4:yn(n,e),bn(e);break;case 13:yn(n,e),bn(e),i=e.child,i.flags&8192&&(o=i.memoizedState!==null,i.stateNode.isHidden=o,!o||i.alternate!==null&&i.alternate.memoizedState!==null||(Lo=Se())),r&4&&Fu(e);break;case 22:if(_=t!==null&&t.memoizedState!==null,e.mode&1?(Be=(x=Be)||_,yn(n,e),Be=x):yn(n,e),bn(e),r&8192){if(x=e.memoizedState!==null,(e.stateNode.isHidden=x)&&!_&&(e.mode&1)!==0)for(B=e,_=e.child;_!==null;){for(b=B=_;B!==null;){switch(N=B,z=N.child,N.tag){case 0:case 11:case 14:case 15:br(4,N,N.return);break;case 1:Wt(N,N.return);var W=N.stateNode;if(typeof W.componentWillUnmount=="function"){r=N,t=N.return;try{n=r,W.props=n.memoizedProps,W.state=n.memoizedState,W.componentWillUnmount()}catch(V){we(r,t,V)}}break;case 5:Wt(N,N.return);break;case 22:if(N.memoizedState!==null){Wu(b);continue}}z!==null?(z.return=N,B=z):Wu(b)}_=_.sibling}e:for(_=null,b=e;;){if(b.tag===5){if(_===null){_=b;try{i=b.stateNode,x?(o=i.style,typeof o.setProperty=="function"?o.setProperty("display","none","important"):o.display="none"):(d=b.stateNode,m=b.memoizedProps.style,a=m!=null&&m.hasOwnProperty("display")?m.display:null,d.style.display=ka("display",a))}catch(V){we(e,e.return,V)}}}else if(b.tag===6){if(_===null)try{b.stateNode.nodeValue=x?"":b.memoizedProps}catch(V){we(e,e.return,V)}}else if((b.tag!==22&&b.tag!==23||b.memoizedState===null||b===e)&&b.child!==null){b.child.return=b,b=b.child;continue}if(b===e)break e;for(;b.sibling===null;){if(b.return===null||b.return===e)break e;_===b&&(_=null),b=b.return}_===b&&(_=null),b.sibling.return=b.return,b=b.sibling}}break;case 19:yn(n,e),bn(e),r&4&&Fu(e);break;case 21:break;default:yn(n,e),bn(e)}}function bn(e){var n=e.flags;if(n&2){try{e:{for(var t=e.return;t!==null;){if(Au(t)){var r=t;break e}t=t.return}throw Error(u(160))}switch(r.tag){case 5:var i=r.stateNode;r.flags&32&&(Gt(i,""),r.flags&=-33);var o=Iu(e);Po(e,o,i);break;case 3:case 4:var a=r.stateNode.containerInfo,d=Iu(e);Eo(e,d,a);break;default:throw Error(u(161))}}catch(m){we(e,e.return,m)}e.flags&=-3}n&4096&&(e.flags&=-4097)}function fm(e,n,t){B=e,Bu(e)}function Bu(e,n,t){for(var r=(e.mode&1)!==0;B!==null;){var i=B,o=i.child;if(i.tag===22&&r){var a=i.memoizedState!==null||bs;if(!a){var d=i.alternate,m=d!==null&&d.memoizedState!==null||Be;d=bs;var x=Be;if(bs=a,(Be=m)&&!x)for(B=i;B!==null;)a=B,m=a.child,a.tag===22&&a.memoizedState!==null?Vu(i):m!==null?(m.return=a,B=m):Vu(i);for(;o!==null;)B=o,Bu(o),o=o.sibling;B=i,bs=d,Be=x}Uu(e)}else(i.subtreeFlags&8772)!==0&&o!==null?(o.return=i,B=o):Uu(e)}}function Uu(e){for(;B!==null;){var n=B;if((n.flags&8772)!==0){var t=n.alternate;try{if((n.flags&8772)!==0)switch(n.tag){case 0:case 11:case 15:Be||Es(5,n);break;case 1:var r=n.stateNode;if(n.flags&4&&!Be)if(t===null)r.componentDidMount();else{var i=n.elementType===n.type?t.memoizedProps:gn(n.type,t.memoizedProps);r.componentDidUpdate(i,t.memoizedState,r.__reactInternalSnapshotBeforeUpdate)}var o=n.updateQueue;o!==null&&Wl(n,o,r);break;case 3:var a=n.updateQueue;if(a!==null){if(t=null,n.child!==null)switch(n.child.tag){case 5:t=n.child.stateNode;break;case 1:t=n.child.stateNode}Wl(n,a,t)}break;case 5:var d=n.stateNode;if(t===null&&n.flags&4){t=d;var m=n.memoizedProps;switch(n.type){case"button":case"input":case"select":case"textarea":m.autoFocus&&t.focus();break;case"img":m.src&&(t.src=m.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(n.memoizedState===null){var x=n.alternate;if(x!==null){var _=x.memoizedState;if(_!==null){var b=_.dehydrated;b!==null&&ir(b)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(u(163))}Be||n.flags&512&&bo(n)}catch(N){we(n,n.return,N)}}if(n===e){B=null;break}if(t=n.sibling,t!==null){t.return=n.return,B=t;break}B=n.return}}function Wu(e){for(;B!==null;){var n=B;if(n===e){B=null;break}var t=n.sibling;if(t!==null){t.return=n.return,B=t;break}B=n.return}}function Vu(e){for(;B!==null;){var n=B;try{switch(n.tag){case 0:case 11:case 15:var t=n.return;try{Es(4,n)}catch(m){we(n,t,m)}break;case 1:var r=n.stateNode;if(typeof r.componentDidMount=="function"){var i=n.return;try{r.componentDidMount()}catch(m){we(n,i,m)}}var o=n.return;try{bo(n)}catch(m){we(n,o,m)}break;case 5:var a=n.return;try{bo(n)}catch(m){we(n,a,m)}}}catch(m){we(n,n.return,m)}if(n===e){B=null;break}var d=n.sibling;if(d!==null){d.return=n.return,B=d;break}B=n.return}}var pm=Math.ceil,Ps=pe.ReactCurrentDispatcher,Mo=pe.ReactCurrentOwner,un=pe.ReactCurrentBatchConfig,te=0,Re=null,Ce=null,Ie=0,rn=0,Vt=Hn(0),Me=0,Er=null,ft=0,Ms=0,To=0,Pr=null,Ke=null,Lo=0,$t=1/0,zn=null,Ts=!1,Ro=null,Yn=null,Ls=!1,Jn=null,Rs=0,Mr=0,Do=null,Ds=-1,As=0;function We(){return(te&6)!==0?Se():Ds!==-1?Ds:Ds=Se()}function Zn(e){return(e.mode&1)===0?1:(te&2)!==0&&Ie!==0?Ie&-Ie:Jd.transition!==null?(As===0&&(As=Ia()),As):(e=ae,e!==0||(e=window.event,e=e===void 0?16:Ha(e.type)),e)}function xn(e,n,t,r){if(50<Mr)throw Mr=0,Do=null,Error(u(185));er(e,t,r),((te&2)===0||e!==Re)&&(e===Re&&((te&2)===0&&(Ms|=t),Me===4&&et(e,Ie)),Ge(e,r),t===1&&te===0&&(n.mode&1)===0&&($t=Se()+500,us&&Kn()))}function Ge(e,n){var t=e.callbackNode;Jc(e,n);var r=$r(e,e===Re?Ie:0);if(r===0)t!==null&&Ra(t),e.callbackNode=null,e.callbackPriority=0;else if(n=r&-r,e.callbackPriority!==n){if(t!=null&&Ra(t),n===1)e.tag===0?Yd(Hu.bind(null,e)):Ml(Hu.bind(null,e)),Kd(function(){(te&6)===0&&Kn()}),t=null;else{switch(za(r)){case 1:t=mi;break;case 4:t=Da;break;case 16:t=Br;break;case 536870912:t=Aa;break;default:t=Br}t=Zu(t,$u.bind(null,e))}e.callbackPriority=n,e.callbackNode=t}}function $u(e,n){if(Ds=-1,As=0,(te&6)!==0)throw Error(u(327));var t=e.callbackNode;if(Ht()&&e.callbackNode!==t)return null;var r=$r(e,e===Re?Ie:0);if(r===0)return null;if((r&30)!==0||(r&e.expiredLanes)!==0||n)n=Is(e,r);else{n=r;var i=te;te|=2;var o=Ku();(Re!==e||Ie!==n)&&(zn=null,$t=Se()+500,gt(e,n));do try{ym();break}catch(d){Qu(e,d)}while(!0);Yi(),Ps.current=o,te=i,Ce!==null?n=0:(Re=null,Ie=0,n=Me)}if(n!==0){if(n===2&&(i=hi(e),i!==0&&(r=i,n=Ao(e,i))),n===1)throw t=Er,gt(e,0),et(e,r),Ge(e,Se()),t;if(n===6)et(e,r);else{if(i=e.current.alternate,(r&30)===0&&!gm(i)&&(n=Is(e,r),n===2&&(o=hi(e),o!==0&&(r=o,n=Ao(e,o))),n===1))throw t=Er,gt(e,0),et(e,r),Ge(e,Se()),t;switch(e.finishedWork=i,e.finishedLanes=r,n){case 0:case 1:throw Error(u(345));case 2:vt(e,Ke,zn);break;case 3:if(et(e,r),(r&130023424)===r&&(n=Lo+500-Se(),10<n)){if($r(e,0)!==0)break;if(i=e.suspendedLanes,(i&r)!==r){We(),e.pingedLanes|=e.suspendedLanes&i;break}e.timeoutHandle=Bi(vt.bind(null,e,Ke,zn),n);break}vt(e,Ke,zn);break;case 4:if(et(e,r),(r&4194240)===r)break;for(n=e.eventTimes,i=-1;0<r;){var a=31-hn(r);o=1<<a,a=n[a],a>i&&(i=a),r&=~o}if(r=i,r=Se()-r,r=(120>r?120:480>r?480:1080>r?1080:1920>r?1920:3e3>r?3e3:4320>r?4320:1960*pm(r/1960))-r,10<r){e.timeoutHandle=Bi(vt.bind(null,e,Ke,zn),r);break}vt(e,Ke,zn);break;case 5:vt(e,Ke,zn);break;default:throw Error(u(329))}}}return Ge(e,Se()),e.callbackNode===t?$u.bind(null,e):null}function Ao(e,n){var t=Pr;return e.current.memoizedState.isDehydrated&&(gt(e,n).flags|=256),e=Is(e,n),e!==2&&(n=Ke,Ke=t,n!==null&&Io(n)),e}function Io(e){Ke===null?Ke=e:Ke.push.apply(Ke,e)}function gm(e){for(var n=e;;){if(n.flags&16384){var t=n.updateQueue;if(t!==null&&(t=t.stores,t!==null))for(var r=0;r<t.length;r++){var i=t[r],o=i.getSnapshot;i=i.value;try{if(!fn(o(),i))return!1}catch{return!1}}}if(t=n.child,n.subtreeFlags&16384&&t!==null)t.return=n,n=t;else{if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return!0;n=n.return}n.sibling.return=n.return,n=n.sibling}}return!0}function et(e,n){for(n&=~To,n&=~Ms,e.suspendedLanes|=n,e.pingedLanes&=~n,e=e.expirationTimes;0<n;){var t=31-hn(n),r=1<<t;e[t]=-1,n&=~r}}function Hu(e){if((te&6)!==0)throw Error(u(327));Ht();var n=$r(e,0);if((n&1)===0)return Ge(e,Se()),null;var t=Is(e,n);if(e.tag!==0&&t===2){var r=hi(e);r!==0&&(n=r,t=Ao(e,r))}if(t===1)throw t=Er,gt(e,0),et(e,n),Ge(e,Se()),t;if(t===6)throw Error(u(345));return e.finishedWork=e.current.alternate,e.finishedLanes=n,vt(e,Ke,zn),Ge(e,Se()),null}function zo(e,n){var t=te;te|=1;try{return e(n)}finally{te=t,te===0&&($t=Se()+500,us&&Kn())}}function pt(e){Jn!==null&&Jn.tag===0&&(te&6)===0&&Ht();var n=te;te|=1;var t=un.transition,r=ae;try{if(un.transition=null,ae=1,e)return e()}finally{ae=r,un.transition=t,te=n,(te&6)===0&&Kn()}}function Fo(){rn=Vt.current,he(Vt)}function gt(e,n){e.finishedWork=null,e.finishedLanes=0;var t=e.timeoutHandle;if(t!==-1&&(e.timeoutHandle=-1,Qd(t)),Ce!==null)for(t=Ce.return;t!==null;){var r=t;switch(Qi(r),r.tag){case 1:r=r.type.childContextTypes,r!=null&&as();break;case 3:Bt(),he($e),he(ze),io();break;case 5:ro(r);break;case 4:Bt();break;case 13:he(ye);break;case 19:he(ye);break;case 10:Ji(r.type._context);break;case 22:case 23:Fo()}t=t.return}if(Re=e,Ce=e=nt(e.current,null),Ie=rn=n,Me=0,Er=null,To=Ms=ft=0,Ke=Pr=null,dt!==null){for(n=0;n<dt.length;n++)if(t=dt[n],r=t.interleaved,r!==null){t.interleaved=null;var i=r.next,o=t.pending;if(o!==null){var a=o.next;o.next=i,r.next=a}t.pending=r}dt=null}return e}function Qu(e,n){do{var t=Ce;try{if(Yi(),xs.current=Ss,ks){for(var r=xe.memoizedState;r!==null;){var i=r.queue;i!==null&&(i.pending=null),r=r.next}ks=!1}if(ht=0,Le=Pe=xe=null,jr=!1,Sr=0,Mo.current=null,t===null||t.return===null){Me=1,Er=n,Ce=null;break}e:{var o=e,a=t.return,d=t,m=n;if(n=Ie,d.flags|=32768,m!==null&&typeof m=="object"&&typeof m.then=="function"){var x=m,_=d,b=_.tag;if((_.mode&1)===0&&(b===0||b===11||b===15)){var N=_.alternate;N?(_.updateQueue=N.updateQueue,_.memoizedState=N.memoizedState,_.lanes=N.lanes):(_.updateQueue=null,_.memoizedState=null)}var z=vu(a);if(z!==null){z.flags&=-257,yu(z,a,d,o,n),z.mode&1&&gu(o,x,n),n=z,m=x;var W=n.updateQueue;if(W===null){var V=new Set;V.add(m),n.updateQueue=V}else W.add(m);break e}else{if((n&1)===0){gu(o,x,n),Oo();break e}m=Error(u(426))}}else if(ve&&d.mode&1){var Ne=vu(a);if(Ne!==null){(Ne.flags&65536)===0&&(Ne.flags|=256),yu(Ne,a,d,o,n),Xi(Ut(m,d));break e}}o=m=Ut(m,d),Me!==4&&(Me=2),Pr===null?Pr=[o]:Pr.push(o),o=a;do{switch(o.tag){case 3:o.flags|=65536,n&=-n,o.lanes|=n;var g=fu(o,m,n);Ul(o,g);break e;case 1:d=m;var h=o.type,v=o.stateNode;if((o.flags&128)===0&&(typeof h.getDerivedStateFromError=="function"||v!==null&&typeof v.componentDidCatch=="function"&&(Yn===null||!Yn.has(v)))){o.flags|=65536,n&=-n,o.lanes|=n;var T=pu(o,d,n);Ul(o,T);break e}}o=o.return}while(o!==null)}Xu(t)}catch($){n=$,Ce===t&&t!==null&&(Ce=t=t.return);continue}break}while(!0)}function Ku(){var e=Ps.current;return Ps.current=Ss,e===null?Ss:e}function Oo(){(Me===0||Me===3||Me===2)&&(Me=4),Re===null||(ft&268435455)===0&&(Ms&268435455)===0||et(Re,Ie)}function Is(e,n){var t=te;te|=2;var r=Ku();(Re!==e||Ie!==n)&&(zn=null,gt(e,n));do try{vm();break}catch(i){Qu(e,i)}while(!0);if(Yi(),te=t,Ps.current=r,Ce!==null)throw Error(u(261));return Re=null,Ie=0,Me}function vm(){for(;Ce!==null;)Gu(Ce)}function ym(){for(;Ce!==null&&!Vc();)Gu(Ce)}function Gu(e){var n=Ju(e.alternate,e,rn);e.memoizedProps=e.pendingProps,n===null?Xu(e):Ce=n,Mo.current=null}function Xu(e){var n=e;do{var t=n.alternate;if(e=n.return,(n.flags&32768)===0){if(t=cm(t,n,rn),t!==null){Ce=t;return}}else{if(t=dm(t,n),t!==null){t.flags&=32767,Ce=t;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{Me=6,Ce=null;return}}if(n=n.sibling,n!==null){Ce=n;return}Ce=n=e}while(n!==null);Me===0&&(Me=5)}function vt(e,n,t){var r=ae,i=un.transition;try{un.transition=null,ae=1,xm(e,n,t,r)}finally{un.transition=i,ae=r}return null}function xm(e,n,t,r){do Ht();while(Jn!==null);if((te&6)!==0)throw Error(u(327));t=e.finishedWork;var i=e.finishedLanes;if(t===null)return null;if(e.finishedWork=null,e.finishedLanes=0,t===e.current)throw Error(u(177));e.callbackNode=null,e.callbackPriority=0;var o=t.lanes|t.childLanes;if(Zc(e,o),e===Re&&(Ce=Re=null,Ie=0),(t.subtreeFlags&2064)===0&&(t.flags&2064)===0||Ls||(Ls=!0,Zu(Br,function(){return Ht(),null})),o=(t.flags&15990)!==0,(t.subtreeFlags&15990)!==0||o){o=un.transition,un.transition=null;var a=ae;ae=1;var d=te;te|=4,Mo.current=null,hm(e,t),Ou(t,e),Od(Fi),Kr=!!zi,Fi=zi=null,e.current=t,fm(t),$c(),te=d,ae=a,un.transition=o}else e.current=t;if(Ls&&(Ls=!1,Jn=e,Rs=i),o=e.pendingLanes,o===0&&(Yn=null),Kc(t.stateNode),Ge(e,Se()),n!==null)for(r=e.onRecoverableError,t=0;t<n.length;t++)i=n[t],r(i.value,{componentStack:i.stack,digest:i.digest});if(Ts)throw Ts=!1,e=Ro,Ro=null,e;return(Rs&1)!==0&&e.tag!==0&&Ht(),o=e.pendingLanes,(o&1)!==0?e===Do?Mr++:(Mr=0,Do=e):Mr=0,Kn(),null}function Ht(){if(Jn!==null){var e=za(Rs),n=un.transition,t=ae;try{if(un.transition=null,ae=16>e?16:e,Jn===null)var r=!1;else{if(e=Jn,Jn=null,Rs=0,(te&6)!==0)throw Error(u(331));var i=te;for(te|=4,B=e.current;B!==null;){var o=B,a=o.child;if((B.flags&16)!==0){var d=o.deletions;if(d!==null){for(var m=0;m<d.length;m++){var x=d[m];for(B=x;B!==null;){var _=B;switch(_.tag){case 0:case 11:case 15:br(8,_,o)}var b=_.child;if(b!==null)b.return=_,B=b;else for(;B!==null;){_=B;var N=_.sibling,z=_.return;if(Du(_),_===x){B=null;break}if(N!==null){N.return=z,B=N;break}B=z}}}var W=o.alternate;if(W!==null){var V=W.child;if(V!==null){W.child=null;do{var Ne=V.sibling;V.sibling=null,V=Ne}while(V!==null)}}B=o}}if((o.subtreeFlags&2064)!==0&&a!==null)a.return=o,B=a;else e:for(;B!==null;){if(o=B,(o.flags&2048)!==0)switch(o.tag){case 0:case 11:case 15:br(9,o,o.return)}var g=o.sibling;if(g!==null){g.return=o.return,B=g;break e}B=o.return}}var h=e.current;for(B=h;B!==null;){a=B;var v=a.child;if((a.subtreeFlags&2064)!==0&&v!==null)v.return=a,B=v;else e:for(a=h;B!==null;){if(d=B,(d.flags&2048)!==0)try{switch(d.tag){case 0:case 11:case 15:Es(9,d)}}catch($){we(d,d.return,$)}if(d===a){B=null;break e}var T=d.sibling;if(T!==null){T.return=d.return,B=T;break e}B=d.return}}if(te=i,Kn(),Sn&&typeof Sn.onPostCommitFiberRoot=="function")try{Sn.onPostCommitFiberRoot(Ur,e)}catch{}r=!0}return r}finally{ae=t,un.transition=n}}return!1}function qu(e,n,t){n=Ut(t,n),n=fu(e,n,1),e=Xn(e,n,1),n=We(),e!==null&&(er(e,1,n),Ge(e,n))}function we(e,n,t){if(e.tag===3)qu(e,e,t);else for(;n!==null;){if(n.tag===3){qu(n,e,t);break}else if(n.tag===1){var r=n.stateNode;if(typeof n.type.getDerivedStateFromError=="function"||typeof r.componentDidCatch=="function"&&(Yn===null||!Yn.has(r))){e=Ut(t,e),e=pu(n,e,1),n=Xn(n,e,1),e=We(),n!==null&&(er(n,1,e),Ge(n,e));break}}n=n.return}}function km(e,n,t){var r=e.pingCache;r!==null&&r.delete(n),n=We(),e.pingedLanes|=e.suspendedLanes&t,Re===e&&(Ie&t)===t&&(Me===4||Me===3&&(Ie&130023424)===Ie&&500>Se()-Lo?gt(e,0):To|=t),Ge(e,n)}function Yu(e,n){n===0&&((e.mode&1)===0?n=1:(n=Vr,Vr<<=1,(Vr&130023424)===0&&(Vr=4194304)));var t=We();e=Dn(e,n),e!==null&&(er(e,n,t),Ge(e,t))}function wm(e){var n=e.memoizedState,t=0;n!==null&&(t=n.retryLane),Yu(e,t)}function jm(e,n){var t=0;switch(e.tag){case 13:var r=e.stateNode,i=e.memoizedState;i!==null&&(t=i.retryLane);break;case 19:r=e.stateNode;break;default:throw Error(u(314))}r!==null&&r.delete(n),Yu(e,t)}var Ju;Ju=function(e,n,t){if(e!==null)if(e.memoizedProps!==n.pendingProps||$e.current)Qe=!0;else{if((e.lanes&t)===0&&(n.flags&128)===0)return Qe=!1,um(e,n,t);Qe=(e.flags&131072)!==0}else Qe=!1,ve&&(n.flags&1048576)!==0&&Tl(n,ds,n.index);switch(n.lanes=0,n.tag){case 2:var r=n.type;_s(e,n),e=n.pendingProps;var i=Rt(n,ze.current);Ot(n,t),i=lo(null,n,r,e,i,t);var o=uo();return n.flags|=1,typeof i=="object"&&i!==null&&typeof i.render=="function"&&i.$$typeof===void 0?(n.tag=1,n.memoizedState=null,n.updateQueue=null,He(r)?(o=!0,ls(n)):o=!1,n.memoizedState=i.state!==null&&i.state!==void 0?i.state:null,no(n),i.updater=Ns,n.stateNode=i,i._reactInternals=n,go(n,r,e,t),n=ko(null,n,r,!0,o,t)):(n.tag=0,ve&&o&&Hi(n),Ue(null,n,i,t),n=n.child),n;case 16:r=n.elementType;e:{switch(_s(e,n),e=n.pendingProps,i=r._init,r=i(r._payload),n.type=r,i=n.tag=Nm(r),e=gn(r,e),i){case 0:n=xo(null,n,r,e,t);break e;case 1:n=Nu(null,n,r,e,t);break e;case 11:n=xu(null,n,r,e,t);break e;case 14:n=ku(null,n,r,gn(r.type,e),t);break e}throw Error(u(306,r,""))}return n;case 0:return r=n.type,i=n.pendingProps,i=n.elementType===r?i:gn(r,i),xo(e,n,r,i,t);case 1:return r=n.type,i=n.pendingProps,i=n.elementType===r?i:gn(r,i),Nu(e,n,r,i,t);case 3:e:{if(Cu(n),e===null)throw Error(u(387));r=n.pendingProps,o=n.memoizedState,i=o.element,Bl(e,n),vs(n,r,null,t);var a=n.memoizedState;if(r=a.element,o.isDehydrated)if(o={element:r,isDehydrated:!1,cache:a.cache,pendingSuspenseBoundaries:a.pendingSuspenseBoundaries,transitions:a.transitions},n.updateQueue.baseState=o,n.memoizedState=o,n.flags&256){i=Ut(Error(u(423)),n),n=_u(e,n,r,t,i);break e}else if(r!==i){i=Ut(Error(u(424)),n),n=_u(e,n,r,t,i);break e}else for(tn=$n(n.stateNode.containerInfo.firstChild),nn=n,ve=!0,pn=null,t=Fl(n,null,r,t),n.child=t;t;)t.flags=t.flags&-3|4096,t=t.sibling;else{if(It(),r===i){n=In(e,n,t);break e}Ue(e,n,r,t)}n=n.child}return n;case 5:return Vl(n),e===null&&Gi(n),r=n.type,i=n.pendingProps,o=e!==null?e.memoizedProps:null,a=i.children,Oi(r,i)?a=null:o!==null&&Oi(r,o)&&(n.flags|=32),Su(e,n),Ue(e,n,a,t),n.child;case 6:return e===null&&Gi(n),null;case 13:return bu(e,n,t);case 4:return to(n,n.stateNode.containerInfo),r=n.pendingProps,e===null?n.child=zt(n,null,r,t):Ue(e,n,r,t),n.child;case 11:return r=n.type,i=n.pendingProps,i=n.elementType===r?i:gn(r,i),xu(e,n,r,i,t);case 7:return Ue(e,n,n.pendingProps,t),n.child;case 8:return Ue(e,n,n.pendingProps.children,t),n.child;case 12:return Ue(e,n,n.pendingProps.children,t),n.child;case 10:e:{if(r=n.type._context,i=n.pendingProps,o=n.memoizedProps,a=i.value,ce(fs,r._currentValue),r._currentValue=a,o!==null)if(fn(o.value,a)){if(o.children===i.children&&!$e.current){n=In(e,n,t);break e}}else for(o=n.child,o!==null&&(o.return=n);o!==null;){var d=o.dependencies;if(d!==null){a=o.child;for(var m=d.firstContext;m!==null;){if(m.context===r){if(o.tag===1){m=An(-1,t&-t),m.tag=2;var x=o.updateQueue;if(x!==null){x=x.shared;var _=x.pending;_===null?m.next=m:(m.next=_.next,_.next=m),x.pending=m}}o.lanes|=t,m=o.alternate,m!==null&&(m.lanes|=t),Zi(o.return,t,n),d.lanes|=t;break}m=m.next}}else if(o.tag===10)a=o.type===n.type?null:o.child;else if(o.tag===18){if(a=o.return,a===null)throw Error(u(341));a.lanes|=t,d=a.alternate,d!==null&&(d.lanes|=t),Zi(a,t,n),a=o.sibling}else a=o.child;if(a!==null)a.return=o;else for(a=o;a!==null;){if(a===n){a=null;break}if(o=a.sibling,o!==null){o.return=a.return,a=o;break}a=a.return}o=a}Ue(e,n,i.children,t),n=n.child}return n;case 9:return i=n.type,r=n.pendingProps.children,Ot(n,t),i=an(i),r=r(i),n.flags|=1,Ue(e,n,r,t),n.child;case 14:return r=n.type,i=gn(r,n.pendingProps),i=gn(r.type,i),ku(e,n,r,i,t);case 15:return wu(e,n,n.type,n.pendingProps,t);case 17:return r=n.type,i=n.pendingProps,i=n.elementType===r?i:gn(r,i),_s(e,n),n.tag=1,He(r)?(e=!0,ls(n)):e=!1,Ot(n,t),mu(n,r,i),go(n,r,i,t),ko(null,n,r,!0,e,t);case 19:return Pu(e,n,t);case 22:return ju(e,n,t)}throw Error(u(156,n.tag))};function Zu(e,n){return La(e,n)}function Sm(e,n,t,r){this.tag=e,this.key=t,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=n,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=r,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function cn(e,n,t,r){return new Sm(e,n,t,r)}function Bo(e){return e=e.prototype,!(!e||!e.isReactComponent)}function Nm(e){if(typeof e=="function")return Bo(e)?1:0;if(e!=null){if(e=e.$$typeof,e===wn)return 11;if(e===jn)return 14}return 2}function nt(e,n){var t=e.alternate;return t===null?(t=cn(e.tag,n,e.key,e.mode),t.elementType=e.elementType,t.type=e.type,t.stateNode=e.stateNode,t.alternate=e,e.alternate=t):(t.pendingProps=n,t.type=e.type,t.flags=0,t.subtreeFlags=0,t.deletions=null),t.flags=e.flags&14680064,t.childLanes=e.childLanes,t.lanes=e.lanes,t.child=e.child,t.memoizedProps=e.memoizedProps,t.memoizedState=e.memoizedState,t.updateQueue=e.updateQueue,n=e.dependencies,t.dependencies=n===null?null:{lanes:n.lanes,firstContext:n.firstContext},t.sibling=e.sibling,t.index=e.index,t.ref=e.ref,t}function zs(e,n,t,r,i,o){var a=2;if(r=e,typeof e=="function")Bo(e)&&(a=1);else if(typeof e=="string")a=5;else e:switch(e){case J:return yt(t.children,i,o,n);case de:a=8,i|=8;break;case Ee:return e=cn(12,t,n,i|2),e.elementType=Ee,e.lanes=o,e;case Je:return e=cn(13,t,n,i),e.elementType=Je,e.lanes=o,e;case mn:return e=cn(19,t,n,i),e.elementType=mn,e.lanes=o,e;case ke:return Fs(t,i,o,n);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case dn:a=10;break e;case it:a=9;break e;case wn:a=11;break e;case jn:a=14;break e;case Ve:a=16,r=null;break e}throw Error(u(130,e==null?e:typeof e,""))}return n=cn(a,t,n,i),n.elementType=e,n.type=r,n.lanes=o,n}function yt(e,n,t,r){return e=cn(7,e,r,n),e.lanes=t,e}function Fs(e,n,t,r){return e=cn(22,e,r,n),e.elementType=ke,e.lanes=t,e.stateNode={isHidden:!1},e}function Uo(e,n,t){return e=cn(6,e,null,n),e.lanes=t,e}function Wo(e,n,t){return n=cn(4,e.children!==null?e.children:[],e.key,n),n.lanes=t,n.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},n}function Cm(e,n,t,r,i){this.tag=n,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=fi(0),this.expirationTimes=fi(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=fi(0),this.identifierPrefix=r,this.onRecoverableError=i,this.mutableSourceEagerHydrationData=null}function Vo(e,n,t,r,i,o,a,d,m){return e=new Cm(e,n,t,d,m),n===1?(n=1,o===!0&&(n|=8)):n=0,o=cn(3,null,null,n),e.current=o,o.stateNode=e,o.memoizedState={element:r,isDehydrated:t,cache:null,transitions:null,pendingSuspenseBoundaries:null},no(o),e}function _m(e,n,t){var r=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:M,key:r==null?null:""+r,children:e,containerInfo:n,implementation:t}}function ec(e){if(!e)return Qn;e=e._reactInternals;e:{if(ot(e)!==e||e.tag!==1)throw Error(u(170));var n=e;do{switch(n.tag){case 3:n=n.stateNode.context;break e;case 1:if(He(n.type)){n=n.stateNode.__reactInternalMemoizedMergedChildContext;break e}}n=n.return}while(n!==null);throw Error(u(171))}if(e.tag===1){var t=e.type;if(He(t))return El(e,t,n)}return n}function nc(e,n,t,r,i,o,a,d,m){return e=Vo(t,r,!0,e,i,o,a,d,m),e.context=ec(null),t=e.current,r=We(),i=Zn(t),o=An(r,i),o.callback=n??null,Xn(t,o,i),e.current.lanes=i,er(e,i,r),Ge(e,r),e}function Os(e,n,t,r){var i=n.current,o=We(),a=Zn(i);return t=ec(t),n.context===null?n.context=t:n.pendingContext=t,n=An(o,a),n.payload={element:e},r=r===void 0?null:r,r!==null&&(n.callback=r),e=Xn(i,n,a),e!==null&&(xn(e,i,a,o),gs(e,i,a)),a}function Bs(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function tc(e,n){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var t=e.retryLane;e.retryLane=t!==0&&t<n?t:n}}function $o(e,n){tc(e,n),(e=e.alternate)&&tc(e,n)}function bm(){return null}var rc=typeof reportError=="function"?reportError:function(e){console.error(e)};function Ho(e){this._internalRoot=e}Us.prototype.render=Ho.prototype.render=function(e){var n=this._internalRoot;if(n===null)throw Error(u(409));Os(e,n,null,null)},Us.prototype.unmount=Ho.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var n=e.containerInfo;pt(function(){Os(null,e,null,null)}),n[Mn]=null}};function Us(e){this._internalRoot=e}Us.prototype.unstable_scheduleHydration=function(e){if(e){var n=Ba();e={blockedOn:null,target:e,priority:n};for(var t=0;t<Un.length&&n!==0&&n<Un[t].priority;t++);Un.splice(t,0,e),t===0&&Va(e)}};function Qo(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function Ws(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function sc(){}function Em(e,n,t,r,i){if(i){if(typeof r=="function"){var o=r;r=function(){var x=Bs(a);o.call(x)}}var a=nc(n,r,e,0,null,!1,!1,"",sc);return e._reactRootContainer=a,e[Mn]=a.current,fr(e.nodeType===8?e.parentNode:e),pt(),a}for(;i=e.lastChild;)e.removeChild(i);if(typeof r=="function"){var d=r;r=function(){var x=Bs(m);d.call(x)}}var m=Vo(e,0,!1,null,null,!1,!1,"",sc);return e._reactRootContainer=m,e[Mn]=m.current,fr(e.nodeType===8?e.parentNode:e),pt(function(){Os(n,m,t,r)}),m}function Vs(e,n,t,r,i){var o=t._reactRootContainer;if(o){var a=o;if(typeof i=="function"){var d=i;i=function(){var m=Bs(a);d.call(m)}}Os(n,a,e,i)}else a=Em(t,n,e,i,r);return Bs(a)}Fa=function(e){switch(e.tag){case 3:var n=e.stateNode;if(n.current.memoizedState.isDehydrated){var t=Zt(n.pendingLanes);t!==0&&(pi(n,t|1),Ge(n,Se()),(te&6)===0&&($t=Se()+500,Kn()))}break;case 13:pt(function(){var r=Dn(e,1);if(r!==null){var i=We();xn(r,e,1,i)}}),$o(e,1)}},gi=function(e){if(e.tag===13){var n=Dn(e,134217728);if(n!==null){var t=We();xn(n,e,134217728,t)}$o(e,134217728)}},Oa=function(e){if(e.tag===13){var n=Zn(e),t=Dn(e,n);if(t!==null){var r=We();xn(t,e,n,r)}$o(e,n)}},Ba=function(){return ae},Ua=function(e,n){var t=ae;try{return ae=e,n()}finally{ae=t}},li=function(e,n,t){switch(n){case"input":if(ei(e,t),n=t.name,t.type==="radio"&&n!=null){for(t=e;t.parentNode;)t=t.parentNode;for(t=t.querySelectorAll("input[name="+JSON.stringify(""+n)+'][type="radio"]'),n=0;n<t.length;n++){var r=t[n];if(r!==e&&r.form===e.form){var i=os(r);if(!i)throw Error(u(90));da(r),ei(r,i)}}}break;case"textarea":ga(e,t);break;case"select":n=t.value,n!=null&&wt(e,!!t.multiple,n,!1)}},Ca=zo,_a=pt;var Pm={usingClientEntryPoint:!1,Events:[vr,Tt,os,Sa,Na,zo]},Tr={findFiberByHostInstance:at,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},Mm={bundleType:Tr.bundleType,version:Tr.version,rendererPackageName:Tr.rendererPackageName,rendererConfig:Tr.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:pe.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=Ma(e),e===null?null:e.stateNode},findFiberByHostInstance:Tr.findFiberByHostInstance||bm,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var $s=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!$s.isDisabled&&$s.supportsFiber)try{Ur=$s.inject(Mm),Sn=$s}catch{}}return Xe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Pm,Xe.createPortal=function(e,n){var t=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!Qo(n))throw Error(u(200));return _m(e,n,null,t)},Xe.createRoot=function(e,n){if(!Qo(e))throw Error(u(299));var t=!1,r="",i=rc;return n!=null&&(n.unstable_strictMode===!0&&(t=!0),n.identifierPrefix!==void 0&&(r=n.identifierPrefix),n.onRecoverableError!==void 0&&(i=n.onRecoverableError)),n=Vo(e,1,!1,null,null,t,!1,r,i),e[Mn]=n.current,fr(e.nodeType===8?e.parentNode:e),new Ho(n)},Xe.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var n=e._reactInternals;if(n===void 0)throw typeof e.render=="function"?Error(u(188)):(e=Object.keys(e).join(","),Error(u(268,e)));return e=Ma(n),e=e===null?null:e.stateNode,e},Xe.flushSync=function(e){return pt(e)},Xe.hydrate=function(e,n,t){if(!Ws(n))throw Error(u(200));return Vs(null,e,n,!0,t)},Xe.hydrateRoot=function(e,n,t){if(!Qo(e))throw Error(u(405));var r=t!=null&&t.hydratedSources||null,i=!1,o="",a=rc;if(t!=null&&(t.unstable_strictMode===!0&&(i=!0),t.identifierPrefix!==void 0&&(o=t.identifierPrefix),t.onRecoverableError!==void 0&&(a=t.onRecoverableError)),n=nc(n,null,e,1,t??null,i,!1,o,a),e[Mn]=n.current,fr(e),r)for(e=0;e<r.length;e++)t=r[e],i=t._getVersion,i=i(t._source),n.mutableSourceEagerHydrationData==null?n.mutableSourceEagerHydrationData=[t,i]:n.mutableSourceEagerHydrationData.push(t,i);return new Us(n)},Xe.render=function(e,n,t){if(!Ws(n))throw Error(u(200));return Vs(null,e,n,!1,t)},Xe.unmountComponentAtNode=function(e){if(!Ws(e))throw Error(u(40));return e._reactRootContainer?(pt(function(){Vs(null,null,e,!1,function(){e._reactRootContainer=null,e[Mn]=null})}),!0):!1},Xe.unstable_batchedUpdates=zo,Xe.unstable_renderSubtreeIntoContainer=function(e,n,t,r){if(!Ws(t))throw Error(u(200));if(e==null||e._reactInternals===void 0)throw Error(u(38));return Vs(e,n,t,!1,r)},Xe.version="18.3.1-next-f1338f8080-20240426",Xe}var hc;function Bm(){if(hc)return Xo.exports;hc=1;function l(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(l)}catch(c){console.error(c)}}return l(),Xo.exports=Om(),Xo.exports}var fc;function Um(){if(fc)return Hs;fc=1;var l=Bm();return Hs.createRoot=l.createRoot,Hs.hydrateRoot=l.hydrateRoot,Hs}var Wm=Um();class Vm extends Error{constructor(u,p){super(u);ic(this,"status");this.status=p}}async function kn(l,c){const u=await fetch(l,{...c,credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json",...c==null?void 0:c.headers}}),p=await u.json().catch(()=>({}));if(!u.ok)throw new Vm(p.error||u.statusText||"Request failed",u.status);return p}const $m=()=>kn("/auth/status"),Hm=()=>kn("/api/config"),Ec=()=>kn("/api/botstats"),Qm=()=>kn("/api/commands"),Km=()=>kn("/api/guilds"),Gm=()=>kn("/api/me/overview"),Xm=l=>kn(`/api/guild/${l}/overview`),qm=l=>kn(`/api/guild/${l}/levels`),pc=l=>kn(`/api/guild/${l}/config`),gc=l=>kn(`/api/guild/${l}/resources`);function Ys(l,c,u,p){return kn(`/api/guild/${l}/config/${c}`,{method:"POST",headers:p?{"X-CSRF-Token":p}:void 0,body:JSON.stringify(u)})}function Pc(l){return l.replace(/\/+$/,"")||"/"}function vc(l=window.location.pathname){const c=Pc(l);return c==="/commands"?"commands":c==="/docs"?"docs":c.startsWith("/docs/")?"docs-detail":c==="/dashboard"||c.startsWith("/dashboard/")?"dashboard":c==="/privacy"?"privacy":c==="/terms"?"terms":"home"}function Rr(l,c="overview"){return l?`/dashboard/${l}/${c}`:"/dashboard"}function yc(){return"/dashboard/servers"}function xc(){const l=Pc(window.location.pathname).split("/").filter(Boolean),c=["overview","leveling","moderation","server","ai"];return l[1]==="servers"?{view:"servers",guildId:null,section:"overview"}:l[1]?{view:"guild",guildId:l[1]||null,section:c.includes(l[2])?l[2]:"overview"}:{view:"overview",guildId:null,section:"overview"}}function fe(l){l.startsWith("/")&&(window.history.pushState({},"",l),window.dispatchEvent(new PopStateEvent("popstate")),window.scrollTo({top:0,behavior:"smooth"}))}function Xs({onNavigate:l}){return s.jsxs("a",{className:"brand",href:"/",onClick:c=>{c.preventDefault(),l?l():fe("/")},children:[s.jsx("span",{className:"brand-mark",children:"n"}),s.jsx("span",{children:"niko"})]})}function Qt(){return s.jsxs("footer",{className:"site-footer",children:[s.jsx(Xs,{}),s.jsx("span",{children:"Built for communities that care."}),s.jsxs("div",{children:[s.jsx("a",{href:"/privacy",onClick:l=>{l.preventDefault(),fe("/privacy")},children:"Privacy"}),s.jsx("a",{href:"/terms",onClick:l=>{l.preventDefault(),fe("/terms")},children:"Terms"}),s.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"GitHub"})]})]})}/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Mc=(...l)=>l.filter((c,u,p)=>!!c&&c.trim()!==""&&p.indexOf(c)===u).join(" ").trim();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ym=l=>l.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Jm=l=>l.replace(/^([A-Z])|[\s-_]+(\w)/g,(c,u,p)=>p?p.toUpperCase():u.toLowerCase());/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kc=l=>{const c=Jm(l);return c.charAt(0).toUpperCase()+c.slice(1)};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var Jo={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Zm=l=>{for(const c in l)if(c.startsWith("aria-")||c==="role"||c==="title")return!0;return!1},eh=D.createContext({}),nh=()=>D.useContext(eh),th=D.forwardRef(({color:l,size:c,strokeWidth:u,absoluteStrokeWidth:p,className:y="",children:E,iconNode:S,...F},w)=>{const{size:O=24,strokeWidth:L=2,absoluteStrokeWidth:I=!1,color:R="currentColor",className:G=""}=nh()??{},k=p??I?Number(u??L)*24/Number(c??O):u??L;return D.createElement("svg",{ref:w,...Jo,width:c??O??Jo.width,height:c??O??Jo.height,stroke:l??R,strokeWidth:k,className:Mc("lucide",G,y),...!E&&!Zm(F)&&{"aria-hidden":"true"},...F},[...S.map(([P,j])=>D.createElement(P,j)),...Array.isArray(E)?E:[E]])});/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ye=(l,c)=>{const u=D.forwardRef(({className:p,...y},E)=>D.createElement(th,{ref:E,iconNode:c,className:Mc(`lucide-${Ym(kc(l))}`,`lucide-${l}`,p),...y}));return u.displayName=kc(l),u};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const rh=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]],sh=Ye("arrow-right",rh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ih=[["path",{d:"M12 5v16",key:"1f6ucr"}],["path",{d:"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z",key:"1fyvmf"}]],wc=Ye("book-open",ih);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const oh=[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],Zo=Ye("chart-column",oh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ah=[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]],lh=Ye("external-link",ah);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const uh=[["rect",{width:"7",height:"7",x:"3",y:"3",rx:"1",key:"1g98yp"}],["rect",{width:"7",height:"7",x:"14",y:"3",rx:"1",key:"6d4xhi"}],["rect",{width:"7",height:"7",x:"14",y:"14",rx:"1",key:"nxv5o0"}],["rect",{width:"7",height:"7",x:"3",y:"14",rx:"1",key:"1bb6yr"}]],sa=Ye("layout-grid",uh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ch=[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]],dh=Ye("lock-keyhole",ch);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const mh=[["path",{d:"M4 5h16",key:"1tepv9"}],["path",{d:"M4 12h16",key:"1lakjw"}],["path",{d:"M4 19h16",key:"1djgab"}]],hh=Ye("menu",mh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const fh=[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]],ph=Ye("search",fh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const gh=[["path",{d:"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915",key:"1i5ecw"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]],Qs=Ye("settings",gh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const vh=[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}]],ea=Ye("shield",vh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const yh=[["path",{d:"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",key:"1s2grr"}],["path",{d:"M20 2v4",key:"1rf3ol"}],["path",{d:"M22 4h-4",key:"gwowj6"}],["circle",{cx:"4",cy:"20",r:"2",key:"6kqj1y"}]],Ks=Ye("sparkles",yh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const xh=[["path",{d:"M12 19h8",key:"baeox8"}],["path",{d:"m4 17 6-6-6-6",key:"1yngyt"}]],kh=Ye("terminal",xh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const wh=[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["path",{d:"M16 3.128a4 4 0 0 1 0 7.744",key:"16gr8j"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}]],jc=Ye("users",wh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jh=[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]],Sh=Ye("x",jh),Nh={arrow:sh,grid:sa,terminal:kh,chart:Zo,shield:ea,spark:Ks,users:jc,settings:Qs,book:wc,external:lh,menu:hh,close:Sh,lock:dh,search:ph,doc:wc,utility:Qs,icon_home:sa,icon_settings:Qs,icon_economy:Zo,icon_leveling:Zo,icon_moderation:ea,icon_automod:ea,icon_heart:Ks,icon_utility:Qs,icon_bot:jc,icon_ai:Ks,icon_lightbulb:Ks};function Y({name:l,size:c,className:u=""}){const p=Nh[l]||sa;return s.jsx(p,{className:`icon ${u}`.trim(),"aria-hidden":"true",focusable:"false",strokeWidth:1.8,style:c?{width:c,height:c}:void 0})}let Sc=null,na=null;function Js(){const[l,c]=D.useState(Sc);return D.useEffect(()=>{na||(na=Hm().then(u=>Sc=u)),na.then(c).catch(()=>{})},[]),l}function st({page:l}){const c=Js();return s.jsxs("header",{className:"site-header",children:[s.jsx(Xs,{}),s.jsxs("nav",{className:"site-nav","aria-label":"Main navigation",children:[s.jsx("a",{className:l==="home"?"active":"","aria-current":l==="home"?"page":void 0,href:"/",onClick:u=>{u.preventDefault(),fe("/")},children:"Home"}),s.jsx("a",{className:l==="commands"?"active":"","aria-current":l==="commands"?"page":void 0,href:"/commands",onClick:u=>{u.preventDefault(),fe("/commands")},children:"Commands"}),s.jsx("a",{className:l==="docs"?"active":"","aria-current":l==="docs"?"page":void 0,href:"/docs",onClick:u=>{u.preventDefault(),fe("/docs")},children:"Docs"})]}),s.jsxs("div",{className:"header-actions",children:[s.jsxs("a",{className:"button button-small button-muted dashboard-link",href:"/dashboard",onClick:u=>{u.preventDefault(),fe("/dashboard")},children:["Dashboard ",s.jsx(Y,{name:"arrow"})]}),s.jsx("a",{className:"button button-small button-primary",href:(c==null?void 0:c.invite_url)||"#",target:"_blank",rel:"noreferrer",children:"Add to Discord"})]})]})}const Ch=[{value:"all",label:"All commands"},{value:"slash",label:"Slash"},{value:"prefix",label:"Prefix"},{value:"hybrid",label:"Hybrid"},{value:"context",label:"Context menus"}],qs={slash:"Slash command",prefix:"Prefix command",hybrid:"Hybrid command",context:"Context menu"};function xt(l){return l.type&&l.type in qs?l.type:"slash"}function _h(l){return l.context_type==="user"?"Right-click a user":"Right-click a message"}function Tc(l){const c=xt(l);return c==="slash"?s.jsxs("code",{children:["/",l.name]}):c==="prefix"?s.jsxs("code",{children:[".",l.name]}):c==="hybrid"?s.jsxs(s.Fragment,{children:[s.jsxs("code",{children:["/",l.name]}),s.jsx("span",{className:"command-or",children:"or"}),s.jsxs("code",{children:[".",l.name]})]}):s.jsxs("code",{className:"context-invocation",children:[_h(l)," · ",l.name]})}function Nc(l){return l!=null&&l.length?l:["Not specified"]}function bh({command:l,onClose:c}){D.useEffect(()=>{const S=F=>{F.key==="Escape"&&c()};return document.addEventListener("keydown",S),()=>document.removeEventListener("keydown",S)},[c]);const u=l.parameters||[],p=l.subcommands||[],y=Nc(l.aliases),E=Nc(l.permissions);return s.jsx("div",{className:"command-dialog-backdrop",role:"presentation",onMouseDown:S=>{S.currentTarget===S.target&&c()},children:s.jsxs("section",{className:"command-dialog",role:"dialog","aria-modal":"true","aria-labelledby":"command-dialog-title",children:[s.jsxs("header",{className:"command-dialog-header",children:[s.jsxs("div",{children:[s.jsxs("div",{className:"command-dialog-kicker",children:[l.category," · ",qs[xt(l)]]}),s.jsx("h2",{id:"command-dialog-title",children:Tc(l)})]}),s.jsx("button",{className:"dialog-close",type:"button",onClick:c,"aria-label":"Close command details",title:"Close command details",children:s.jsx(Y,{name:"close"})})]}),s.jsxs("div",{className:"command-dialog-body",children:[s.jsx("p",{className:"command-dialog-description",children:l.description||"A Niko command for your server."}),s.jsxs("div",{className:"command-detail-grid",children:[s.jsxs("section",{className:"command-detail-section command-detail-wide",children:[s.jsx("h3",{children:"Usage"}),s.jsx("code",{className:"command-usage",children:l.usage||`${xt(l)==="context"?l.name:`/${l.name}`}`})]}),s.jsxs("section",{className:"command-detail-section",children:[s.jsx("h3",{children:"Permissions"}),s.jsx("ul",{className:"command-detail-list",children:E.map(S=>s.jsx("li",{children:S},S))})]}),s.jsxs("section",{className:"command-detail-section",children:[s.jsx("h3",{children:"Aliases"}),s.jsx("ul",{className:"command-detail-list",children:y.map(S=>s.jsx("li",{children:s.jsx("code",{children:S==="Not specified"?S:`.${S}`})},S))})]})]}),!!u.length&&s.jsxs("section",{className:"command-detail-section command-parameters",children:[s.jsx("h3",{children:"Parameters"}),s.jsx("div",{className:"command-parameter-list",children:u.map(S=>s.jsxs("div",{className:"command-parameter",children:[s.jsxs("div",{className:"command-parameter-title",children:[s.jsx("code",{children:S.name}),s.jsxs("span",{children:[S.required?"Required":"Optional"," · ",S.type]})]}),s.jsx("p",{children:S.description||"No description provided."})]},S.name))})]}),!!p.length&&s.jsxs("section",{className:"command-detail-section",children:[s.jsx("h3",{children:"Subcommands"}),s.jsx("div",{className:"subcommand-list",children:p.map(S=>s.jsxs("code",{children:[l.name," ",S]},S))})]})]}),s.jsxs("footer",{className:"command-dialog-footer",children:[s.jsx("span",{children:"Command registry details are generated from the live bot."}),s.jsx("button",{className:"button button-primary button-small",type:"button",onClick:c,children:"Done"})]})]})})}function Eh(){const[l,c]=D.useState([]),[u,p]=D.useState(null),[y,E]=D.useState(""),[S,F]=D.useState("all"),[w,O]=D.useState("all"),[L,I]=D.useState(!0),[R,G]=D.useState("");D.useEffect(()=>{Qm().then(c).catch(()=>G("The command registry is unavailable right now.")).finally(()=>I(!1))},[]),D.useEffect(()=>{if(!u)return;const j=document.body.style.overflow;return document.body.style.overflow="hidden",()=>{document.body.style.overflow=j}},[u]);const k=D.useMemo(()=>["all",...Array.from(new Set(l.map(j=>j.category))).sort()],[l]),P=l.filter(j=>{const H=`${j.name} ${j.description} ${j.category} ${qs[xt(j)]} ${j.context_type||""} ${(j.aliases||[]).join(" ")}`.toLowerCase();return(w==="all"||xt(j)===w)&&(S==="all"||j.category===S)&&H.includes(y.trim().toLowerCase())});return s.jsxs(s.Fragment,{children:[s.jsx(st,{page:"commands"}),s.jsxs("main",{className:"shell page-main",children:[s.jsxs("div",{className:"page-heading",children:[s.jsx("div",{className:"eyebrow",children:"Reference library"}),s.jsxs("h1",{children:["Everything Niko",s.jsx("br",{}),s.jsx("em",{children:"knows how to do."})]}),s.jsx("p",{children:"Browse slash, prefix, hybrid, and context commands from the live bot registry. Select any command for permissions, aliases, parameters, usage, and subcommands."})]}),s.jsxs("div",{className:"command-toolbar",children:[s.jsxs("label",{className:"search-field",children:[s.jsx("span",{"aria-hidden":"true",children:"⌕"}),s.jsx("input",{value:y,onChange:j=>E(j.target.value),placeholder:"Search commands","aria-label":"Search commands"})]}),s.jsxs("div",{className:"command-filters",children:[s.jsx("div",{className:"filter-list","aria-label":"Command types",children:Ch.map(j=>s.jsx("button",{type:"button",className:w===j.value?"filter active":"filter","aria-pressed":w===j.value,onClick:()=>O(j.value),children:j.label},j.value))}),s.jsx("div",{className:"filter-list","aria-label":"Command categories",children:k.map(j=>s.jsx("button",{type:"button",className:S===j?"filter active":"filter","aria-pressed":S===j,onClick:()=>F(j),children:j==="all"?"All categories":j},j))})]})]}),s.jsxs("div",{className:"command-meta",children:[s.jsx("strong",{children:L?"…":P.length})," commands ",s.jsx("span",{children:"·"})," live bot registry ",s.jsx("span",{children:"·"})," select a card for details"]}),R&&s.jsxs("div",{className:"inline-error",role:"alert",children:[s.jsx("strong",{children:"Could not load commands"}),s.jsx("span",{children:R})]}),s.jsxs("div",{className:"commands-grid",children:[P.map(j=>s.jsxs("button",{className:"command-card",type:"button",onClick:()=>p(j),"aria-label":`View details for ${j.name}`,children:[s.jsxs("span",{className:"command-card-head",children:[s.jsx("span",{className:"command-name",children:Tc(j)}),s.jsx("span",{className:"command-type",children:qs[xt(j)]})]}),s.jsx("span",{className:"command-card-description",children:j.description||"A Niko command for your server."}),s.jsxs("span",{className:"command-card-footer",children:[s.jsx("span",{className:"category-tag",children:j.category}),s.jsxs("span",{className:"command-expand",children:[s.jsx("span",{children:"Details"}),s.jsx(Y,{name:"arrow",size:14})]})]})]},`${xt(j)}-${j.context_type||""}-${j.category}-${j.name}`)),!L&&!R&&!P.length&&s.jsx("div",{className:"empty-state",children:"No commands match that search."})]})]}),s.jsx(Qt,{}),u&&s.jsx(bh,{command:u,onClose:()=>p(null)})]})}function _e(l){return l==null?"—":new Intl.NumberFormat("en-US",{notation:l>9999?"compact":"standard"}).format(l)}function ia(l){return(l==null?void 0:l.global_name)||(l==null?void 0:l.username)||"there"}function Lc(l){return l.split(/\s+/).map(c=>c[0]).join("").slice(0,2).toUpperCase()}function aa({guild:l,className:c="guild-avatar"}){return s.jsx("span",{className:c,"aria-hidden":"true",children:l.icon_url?s.jsx("img",{src:l.icon_url,alt:""}):l.name.slice(0,1).toUpperCase()})}function Rc({user:l,className:c="avatar"}){const u=l.avatar?`https://cdn.discordapp.com/avatars/${l.id}/${l.avatar}.${l.avatar.startsWith("a_")?"gif":"png"}?size=64`:null;return s.jsx("span",{className:c,"aria-hidden":"true",children:u?s.jsx("img",{src:u,alt:""}):Lc(l.global_name||l.username||"Niko")})}function Ph({name:l,avatarUrl:c,className:u="member-avatar"}){return s.jsx("span",{className:u,"aria-hidden":"true",children:c?s.jsx("img",{src:c,alt:""}):Lc(l)})}const Cc=[["overview","Overview","grid","At a glance"],["leveling","Leveling","spark","Reward participation"],["moderation","Moderation","shield","Keep things steady"],["server","Server","settings","Manage server features"],["ai","AI controls","settings","Shape Niko’s voice"]];function Mh({user:l,guilds:c,selectedGuild:u,view:p,section:y,stats:E,onHome:S,onServers:F,onGuildChange:w,onSectionChange:O,children:L}){var j;const I=c.filter(H=>H.installed!==!1),R=(H=!1)=>s.jsx("nav",{className:H?"dash-nav dash-nav-mobile":"dash-nav","aria-label":"Server settings",children:Cc.map(([le,je,pe])=>s.jsxs("button",{className:p==="guild"&&y===le?"active":"","aria-current":p==="guild"&&y===le?"page":void 0,onClick:()=>O(le),children:[s.jsx(Y,{name:pe}),s.jsx("span",{children:je})]},le))}),G=(H=!1)=>s.jsxs("nav",{className:H?"dash-nav dash-primary-nav dash-nav-mobile":"dash-nav dash-primary-nav","aria-label":"Dashboard",children:[s.jsxs("button",{className:p==="overview"?"active":"","aria-current":p==="overview"?"page":void 0,onClick:S,children:[s.jsx(Y,{name:"grid"}),s.jsx("span",{children:"My overview"})]}),s.jsxs("button",{className:p==="servers"?"active":"","aria-current":p==="servers"?"page":void 0,onClick:F,children:[s.jsx(Y,{name:"users"}),s.jsx("span",{children:"My servers"})]})]}),k=p==="overview"?`Welcome, ${ia(l)}`:p==="servers"?"Your servers":(u==null?void 0:u.name)||"Server settings",P=p==="guild"?"Managing server":"Niko dashboard";return s.jsxs("div",{className:"dashboard-layout",children:[s.jsxs("aside",{className:"dash-sidebar",children:[s.jsx(Xs,{onNavigate:S}),s.jsxs("div",{className:"side-rail-heading",children:[s.jsx("span",{className:"side-label",children:"Workspace"}),s.jsxs("span",{className:"rail-status",children:[s.jsx("span",{className:"status-dot"})," Live"]})]}),G(),p==="guild"&&u&&s.jsxs(s.Fragment,{children:[s.jsx("div",{className:"side-label side-label-settings",children:"Current server"}),s.jsxs("div",{className:"side-guild",children:[s.jsx(aa,{guild:u}),s.jsxs("span",{children:[s.jsx("strong",{children:u.name}),s.jsx("small",{children:"Live configuration"})]}),s.jsx("span",{className:"guild-presence",title:"Niko is connected",children:s.jsx("span",{className:"status-dot"})})]}),s.jsxs("div",{className:"side-settings-caption",children:[s.jsx("span",{children:"Settings map"}),s.jsx("small",{children:"Pick a room to tune"})]}),R()]}),p!=="guild"&&s.jsxs("div",{className:"side-rail-note",children:[s.jsx("span",{className:"panel-kicker",children:"Niko workspace"}),s.jsxs("strong",{children:["Make the useful",s.jsx("br",{}),"things easier to find."]}),s.jsx("small",{children:"Your servers and their live signals, in one quiet place."})]}),s.jsxs("div",{className:"sidebar-bottom",children:[s.jsxs("span",{className:"online-label",children:[s.jsx("span",{className:"status-dot"})," Niko is online"]}),s.jsxs("small",{children:[_e(E==null?void 0:E.guild_count)," connected servers · v",(E==null?void 0:E.version)||"1.0"]}),s.jsxs("a",{href:"/",onClick:H=>{H.preventDefault(),fe("/")},children:["Back to public site ",s.jsx(Y,{name:"arrow"})]})]})]}),s.jsxs("div",{className:"dash-content",children:[s.jsxs("header",{className:"dash-topbar",children:[s.jsxs("div",{className:"mobile-top-row",children:[s.jsx("span",{className:"mobile-brand",children:s.jsx(Xs,{})}),s.jsxs("span",{className:"mobile-status",children:[s.jsx("span",{className:"status-dot"})," Online"]})]}),s.jsxs("div",{className:"dash-title",children:[s.jsxs("span",{className:"dash-overline",children:[P," ",s.jsx("span",{className:"dash-title-divider",children:"/"})," ",p==="guild"?(j=Cc.find(([H])=>H===y))==null?void 0:j[1]:"Workspace"]}),s.jsx("h1",{children:k})]}),s.jsxs("div",{className:"dash-top-actions",children:[p==="guild"?s.jsxs("label",{className:"guild-switcher",children:[s.jsx("span",{className:"sr-only",children:"Switch server"}),s.jsxs("select",{value:(u==null?void 0:u.id)||"",onChange:H=>{const le=I.find(je=>je.id===H.target.value);le&&w(le)},children:[s.jsx("option",{value:"",disabled:!0,children:"Switch server"}),I.map(H=>s.jsx("option",{value:H.id,children:H.name},H.id))]})]}):s.jsxs("button",{className:"button button-muted button-small top-action",onClick:F,children:[s.jsx(Y,{name:"users"})," Browse servers"]}),p==="guild"&&s.jsxs("span",{className:"connection-chip",children:[s.jsx("span",{className:"status-dot"})," Connected"]}),s.jsxs("div",{className:"user-pill",children:[s.jsx(Rc,{user:l}),s.jsx("span",{children:ia(l)})]}),s.jsx("a",{className:"logout-link",href:"/auth/logout",children:"Log out"})]})]}),s.jsx("div",{className:"mobile-primary-bar",children:G(!0)}),p==="guild"&&s.jsx("div",{className:"mobile-section-bar",children:R(!0)}),s.jsx("main",{className:"dash-main",children:L})]})]})}function kt({eyebrow:l,title:c,text:u}){return s.jsxs("div",{className:"dash-heading",children:[s.jsxs("div",{className:"heading-meta",children:[s.jsx("div",{className:"eyebrow",children:l}),s.jsx("span",{className:"heading-context",children:"NIKO / CONTROL ROOM"})]}),s.jsx("h2",{children:c}),s.jsx("p",{children:u})]})}function Pn({label:l,value:c,note:u,accent:p=""}){return s.jsxs("div",{className:`dash-stat ${p}`,children:[s.jsx("span",{children:l}),s.jsx("strong",{children:c}),s.jsx("small",{children:u})]})}function Th({user:l,overview:c,guilds:u,onServers:p,onManage:y}){const E=u.filter(S=>S.installed!==!1);return s.jsxs(s.Fragment,{children:[s.jsx(kt,{eyebrow:"Personal overview",title:"Your Niko snapshot.",text:"Keep an eye on your progress, then jump into a server when you’re ready to tune the room."}),s.jsxs("div",{className:"overview-intro",children:[s.jsxs("div",{className:"profile-card",children:[s.jsx(Rc,{user:l,className:"profile-avatar"}),s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Signed in as"}),s.jsx("h3",{children:ia(l)}),s.jsx("p",{children:"Personal economy profile"})]})]}),s.jsxs("button",{className:"button button-primary",onClick:p,children:["Manage a server ",s.jsx(Y,{name:"arrow"})]})]}),s.jsxs("div",{className:"dash-stats overview-stats",children:[s.jsx(Pn,{label:"Net worth",value:_e(c==null?void 0:c.net_worth),note:"Across your Niko profile",accent:"accent-orange"}),s.jsx(Pn,{label:"In your wallet",value:_e(c==null?void 0:c.balance),note:"Ready to spend",accent:"accent-violet"}),s.jsx(Pn,{label:"In your vault",value:_e(c==null?void 0:c.bank),note:"Saved for later",accent:"accent-blue"}),s.jsx(Pn,{label:"Current level",value:_e(c==null?void 0:c.level),note:c!=null&&c.job?`Working as a ${c.job}`:"Keep showing up",accent:"accent-green"})]}),s.jsxs("div",{className:"dash-columns overview-columns",children:[s.jsxs("section",{className:"dash-panel",children:[s.jsxs("div",{className:"panel-heading",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Progress"}),s.jsx("h3",{children:"Your momentum"})]}),s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:"spark"})})]}),s.jsxs("div",{className:"metric-list",children:[s.jsxs("div",{children:[s.jsx("span",{children:"Daily streak"}),s.jsxs("strong",{children:[_e(c==null?void 0:c.daily_streak)," ",s.jsx("small",{children:"days"})]})]}),s.jsxs("div",{children:[s.jsx("span",{children:"Achievements"}),s.jsxs("strong",{children:[_e(c==null?void 0:c.achievements)," ",s.jsx("small",{children:"unlocked"})]})]}),s.jsxs("div",{children:[s.jsx("span",{children:"Total earned"}),s.jsxs("strong",{children:[_e(c==null?void 0:c.total_earned)," ",s.jsx("small",{children:"coins"})]})]}),s.jsxs("div",{children:[s.jsx("span",{children:"Economy standing"}),s.jsxs("strong",{children:[c!=null&&c.economy_rank?`#${_e(c.economy_rank)}`:"—"," ",s.jsx("small",{children:c!=null&&c.economy_profiles?`of ${_e(c.economy_profiles)}`:""})]})]})]})]}),s.jsxs("section",{className:"dash-panel",children:[s.jsxs("div",{className:"panel-heading",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Quick access"}),s.jsx("h3",{children:"Your servers"})]}),s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:"users"})})]}),s.jsxs("div",{className:"mini-server-list",children:[E.slice(0,4).map(S=>s.jsxs("button",{onClick:()=>y(S),children:[s.jsx(aa,{guild:S}),s.jsx("span",{children:S.name}),s.jsx(Y,{name:"arrow"})]},S.id)),!E.length&&s.jsx("p",{className:"empty-state compact",children:"Add Niko to a server to start managing it."})]}),s.jsxs("button",{className:"text-link overview-link",onClick:p,children:["View all servers ",s.jsx(Y,{name:"arrow"})]})]})]})]})}function _c({guild:l,onManage:c}){const u=l.installed!==!1;return s.jsxs("article",{className:"server-card",children:[s.jsxs("div",{className:"server-card-heading",children:[s.jsx(aa,{guild:l,className:"server-avatar"}),s.jsx("span",{className:"server-status",children:u?"Niko is installed":"Ready to add"})]}),s.jsx("h3",{children:l.name}),s.jsx("p",{children:u?"Open the dashboard to manage Niko’s features and settings.":"You have permission to manage this server. Add Niko to unlock its controls."}),u?s.jsxs("button",{className:"button button-muted button-small",onClick:()=>c(l),children:["Open settings ",s.jsx(Y,{name:"arrow"})]}):s.jsxs("a",{className:"button button-primary button-small",href:l.invite_url||"#",target:"_blank",rel:"noreferrer",children:["Add Niko ",s.jsx(Y,{name:"external"})]})]})}function Lh({guilds:l,onManage:c}){const u=l.filter(y=>y.installed!==!1),p=l.filter(y=>y.installed===!1);return s.jsxs(s.Fragment,{children:[s.jsx(kt,{eyebrow:"Servers",title:"Choose where to work.",text:"Manage servers with Niko already installed, or add Niko to another server you can administer."}),s.jsxs("div",{className:"server-summary",children:[s.jsxs("div",{children:[s.jsx("strong",{children:_e(u.length)}),s.jsx("span",{children:"Connected to Niko"})]}),s.jsxs("div",{children:[s.jsx("strong",{children:_e(p.length)}),s.jsx("span",{children:"Ready to add"})]}),s.jsxs("div",{className:"server-summary-note",children:[s.jsx(Y,{name:"shield"}),s.jsx("span",{children:"Only servers where you have Manage Server access are shown."})]})]}),s.jsxs("section",{className:"server-section",children:[s.jsxs("div",{className:"section-heading-row",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Connected"}),s.jsx("h3",{children:"Manage a server"})]}),s.jsx("span",{className:"section-count",children:u.length})]}),s.jsxs("div",{className:"server-grid",children:[u.map(y=>s.jsx(_c,{guild:y,onManage:c},y.id)),!u.length&&s.jsxs("div",{className:"empty-state",children:[s.jsx("strong",{children:"No connected servers yet."}),s.jsx("span",{children:"Add Niko below, then come back here to manage it."})]})]})]}),s.jsxs("section",{className:"server-section",children:[s.jsxs("div",{className:"section-heading-row",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Available to you"}),s.jsx("h3",{children:"Add Niko to a server"})]}),s.jsx("span",{className:"section-count",children:p.length})]}),s.jsxs("div",{className:"server-grid",children:[p.map(y=>s.jsx(_c,{guild:y,onManage:c},y.id)),!p.length&&s.jsx("div",{className:"server-note",children:"Niko is already installed in every server you can manage."})]})]})]})}function Dc({rows:l}){return s.jsxs("div",{className:"rank-list",children:[l.slice(0,5).map((c,u)=>s.jsxs("div",{className:"rank-row",children:[s.jsx("span",{className:`rank rank-${u+1}`,children:String(u+1).padStart(2,"0")}),s.jsxs("span",{className:"rank-user",children:[s.jsx(Ph,{name:c.display_name||c.username||"Unknown member",avatarUrl:c.avatar_url}),s.jsxs("span",{children:[s.jsx("strong",{children:c.display_name||c.username||"Unknown member"}),c.username&&c.display_name&&s.jsxs("small",{children:["@",c.username]})]})]}),s.jsxs("strong",{children:[_e(c.xp),s.jsx("small",{children:" xp"})]})]},`${c.user_id}-${u}`)),!l.length&&s.jsx("div",{className:"empty-state compact",children:"No data recorded yet."})]})}function Rh({overview:l}){return s.jsxs(s.Fragment,{children:[s.jsxs("div",{className:"guild-welcome",children:[s.jsxs("div",{children:[s.jsx("span",{className:"welcome-mark",children:s.jsx(Y,{name:"grid"})}),s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Server pulse"}),s.jsx("strong",{children:"Here’s what needs your attention."})]})]}),s.jsxs("span",{className:"welcome-time",children:["LIVE SIGNALS ",s.jsx("span",{className:"status-dot"})]})]}),s.jsx(kt,{eyebrow:"Overview",title:"A quick read on your room.",text:"The important signals, without making you hunt for them."}),s.jsxs("div",{className:"dash-stats guild-overview-stats",children:[s.jsx(Pn,{label:"Warnings logged",value:_e(l.moderation.warn_count),note:"For this server",accent:"accent-blue"}),s.jsx(Pn,{label:"Automod",value:l.moderation.automod_active?"Active":"Quiet",note:"Protection status",accent:"accent-green"}),s.jsx(Pn,{label:"Level leaders",value:_e(l.leveling.top.length),note:"Members with recorded XP",accent:"accent-violet"})]}),s.jsxs("div",{className:"dash-columns",children:[s.jsxs("section",{className:"dash-panel",children:[s.jsxs("div",{className:"panel-heading",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Community energy"}),s.jsx("h3",{children:"Top XP"})]}),s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:"spark"})})]}),s.jsx(Dc,{rows:l.leveling.top})]}),s.jsx("section",{className:"dash-panel",children:s.jsxs("div",{className:"panel-heading",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Server controls"}),s.jsx("h3",{children:"Manage the room"})]}),s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:"settings"})}),s.jsx("p",{children:"Use Server settings for prefixes, welcome messages, logs, and ticket panels."})]})})]})]})}function Dh({rows:l,config:c,resources:u,csrfToken:p,guildId:y}){var E,S,F;return s.jsxs(s.Fragment,{children:[s.jsx(kt,{eyebrow:"Leveling",title:"Momentum people can see.",text:"Track the members turning up, and tune the pace to fit your server."}),s.jsxs("div",{className:"dash-stats",children:[s.jsx(Pn,{label:"Top level",value:String(((E=l[0])==null?void 0:E.level)||0),note:((S=l[0])==null?void 0:S.display_name)||((F=l[0])==null?void 0:F.username)||"No members yet",accent:"accent-violet"}),s.jsx(Pn,{label:"XP multiplier",value:`${(c==null?void 0:c.leveling.xp_multiplier)||1}×`,note:(c==null?void 0:c.leveling.xp_enabled)===!1?"XP disabled":"Currently active",accent:"accent-blue"}),s.jsx(Pn,{label:"Cooldown",value:`${(c==null?void 0:c.leveling.xp_cooldown)||0}s`,note:"Between XP awards",accent:"accent-green"})]}),s.jsxs("section",{className:"dash-panel",children:[s.jsxs("div",{className:"panel-heading",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Leaderboard"}),s.jsx("h3",{children:"XP leaders"})]}),s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:"spark"})})]}),s.jsx(Dc,{rows:l})]}),s.jsx(zh,{guildId:y,config:c,resources:u,csrfToken:p})]})}const la={saving:!1,message:"",error:""};function En({label:l,hint:c,children:u}){return s.jsxs("label",{className:"form-field",children:[s.jsx("span",{className:"form-label",children:l}),u,c&&s.jsx("small",{children:c})]})}function ua({icon:l,label:c,title:u,text:p}){return s.jsxs("div",{className:"settings-intro",children:[s.jsx("span",{className:"settings-intro-icon",children:s.jsx(Y,{name:l})}),s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:c}),s.jsx("strong",{children:u}),s.jsx("p",{children:p})]}),s.jsxs("span",{className:"settings-intro-state",children:[s.jsx("span",{className:"status-dot"})," Per server"]})]})}function Dr({label:l,title:c,detail:u,icon:p}){return s.jsxs("div",{className:"panel-heading settings-section-title",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:l}),s.jsx("h3",{children:c}),u&&s.jsx("p",{children:u})]}),p&&s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:p})})]})}function ca({state:l}){return s.jsxs("div",{className:"setting-footer",children:[l.error?s.jsx("span",{className:"form-error",role:"alert",children:l.error}):s.jsx("span",{role:"status",children:l.message||"Changes apply to this server."}),s.jsx("button",{className:"button button-primary",type:"submit",disabled:l.saving,children:l.saving?"Saving…":"Save changes"})]})}function Ah({guildId:l,config:c,csrfToken:u}){var I,R,G;const[p,y]=D.useState({}),[E,S]=D.useState(la);D.useEffect(()=>{const k=(c==null?void 0:c.moderation)||{};y({automod:{...k.automod||{}},spam_threshold:k.spam_threshold??6,spam_interval:k.spam_interval??7,max_mentions:k.max_mentions??5,antinuke:{...k.antinuke||{}},antiraid:{...k.antiraid||{}},antiraid_ext:{...k.antiraid_ext||{}}})},[c]);const F=(k,P,j)=>y(H=>({...H,[k]:{...H[k],[P]:j}})),w=k=>{k.preventDefault(),S({saving:!0,message:"",error:""}),Ys(l,"automod",p,u).then(P=>{const j=P.config||{};y({automod:{...j.automod||{}},spam_threshold:j.spam_threshold??6,spam_interval:j.spam_interval??7,max_mentions:j.max_mentions??5,antinuke:{...j.antinuke||{}},antiraid:{...j.antiraid||{}},antiraid_ext:{...j.antiraid_ext||{}}}),S({saving:!1,message:"Moderation settings saved to Niko.",error:""})}).catch(P=>S({saving:!1,message:"",error:P instanceof Error?P.message:"Could not save settings."}))},O=[["antispam","Anti-spam","Detect repeated messages"],["antilink","Invite links","Remove Discord invite links"],["badwords","Blocked words","Filter words from the server list"],["massmention","Mass mentions","Limit mention floods"],["antinuke","Anti-nuke","Protect channels and roles"],["antiraid","Join raid protection","React to sudden join waves"],["antiraid_ext","External app protection","Detect user-installed app abuse"]],L=O.filter(([k])=>{var P;return!!((P=p.automod)!=null&&P[k])}).length;return s.jsxs(s.Fragment,{children:[s.jsx(kt,{eyebrow:"Moderation",title:"Keep the room feeling good.",text:"Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration."}),s.jsx(ua,{icon:"shield",label:"Protection desk",title:`${L} of ${O.length} safeguards active`,text:"Start with the essentials, then tune thresholds below when you know the room’s rhythm."}),s.jsxs("form",{onSubmit:w,className:"settings-stack",children:[s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Dr,{label:"Protection rules",title:"AutoMod modules",detail:"Toggle only the responses you want Niko to handle.",icon:"shield"}),s.jsx("div",{className:"setting-list",children:O.map(([k,P,j])=>{var H;return s.jsxs("label",{className:"setting-row",children:[s.jsxs("span",{children:[s.jsx("strong",{children:P}),s.jsx("small",{children:j})]}),s.jsx("input",{type:"checkbox",checked:!!((H=p.automod)!=null&&H[k]),onChange:le=>F("automod",k,le.target.checked)}),s.jsx("i",{"aria-hidden":"true"})]},k)})})]}),s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Dr,{label:"Thresholds",title:"Choose when protection steps in",detail:"These limits apply across the server."}),s.jsxs("div",{className:"form-grid",children:[s.jsx(En,{label:"Spam messages",hint:"Messages inside the spam interval",children:s.jsx("input",{type:"number",min:"1",max:"100",value:p.spam_threshold??6,onChange:k=>y({...p,spam_threshold:k.target.value})})}),s.jsx(En,{label:"Spam interval (seconds)",children:s.jsx("input",{type:"number",min:"1",max:"3600",value:p.spam_interval??7,onChange:k=>y({...p,spam_interval:k.target.value})})}),s.jsx(En,{label:"Maximum mentions",children:s.jsx("input",{type:"number",min:"1",max:"100",value:p.max_mentions??5,onChange:k=>y({...p,max_mentions:k.target.value})})}),s.jsx(En,{label:"Anti-raid joins",hint:"Joins inside the join interval",children:s.jsx("input",{type:"number",min:"1",max:"1000",value:((I=p.antiraid)==null?void 0:I.join_threshold)??10,onChange:k=>F("antiraid","join_threshold",k.target.value)})}),s.jsx(En,{label:"Anti-raid interval (seconds)",children:s.jsx("input",{type:"number",min:"1",max:"3600",value:((R=p.antiraid)==null?void 0:R.join_interval)??10,onChange:k=>F("antiraid","join_interval",k.target.value)})}),s.jsx(En,{label:"Anti-raid action",children:s.jsxs("select",{value:((G=p.antiraid)==null?void 0:G.action)??"kick",onChange:k=>F("antiraid","action",k.target.value),children:[s.jsx("option",{value:"kick",children:"Kick"}),s.jsx("option",{value:"ban",children:"Ban"}),s.jsx("option",{value:"softban",children:"Soft-ban"}),s.jsx("option",{value:"slowmode",children:"Slowmode"}),s.jsx("option",{value:"lockdown",children:"Lockdown"})]})})]}),s.jsx(ca,{state:E})]})]})]})}function Ih({guildId:l,config:c,csrfToken:u}){const[p,y]=D.useState({personality:"cafe",enabled:!0,ai_actions_experiment:!1,better_context_experiment:!1}),[E,S]=D.useState(la);D.useEffect(()=>{const w=(c==null?void 0:c.ai)||{};y({personality:w.personality||"cafe",enabled:w.enabled!=="False"&&w.enabled!==!1,ai_actions_experiment:w.ai_actions_experiment===!0||w.ai_actions_experiment==="True",better_context_experiment:w.better_context_experiment===!0||w.better_context_experiment==="True"})},[c]);const F=w=>{w.preventDefault(),S({saving:!0,message:"",error:""}),Ys(l,"ai",p,u).then(O=>{const L=O.config||{};y({personality:L.personality==="normal"?"normal":"cafe",enabled:L.enabled!=="False"&&L.enabled!==!1,ai_actions_experiment:L.ai_actions_experiment===!0||L.ai_actions_experiment==="True",better_context_experiment:L.better_context_experiment===!0||L.better_context_experiment==="True"}),S({saving:!1,message:"AI settings saved to Niko.",error:""})}).catch(O=>S({saving:!1,message:"",error:O instanceof Error?O.message:"Could not save settings."}))};return s.jsxs(s.Fragment,{children:[s.jsx(kt,{eyebrow:"AI controls",title:"Give Niko the right tone.",text:"AI is optional, configurable per server, and designed to stay out of the way when the room does not need it."}),s.jsx(ua,{icon:"settings",label:"Conversation desk",title:p.enabled?"Niko is ready to respond":"Niko is staying quiet",text:"Choose a voice that fits your community. You can change this without affecting other servers."}),s.jsxs("form",{onSubmit:F,className:"settings-stack",children:[s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Dr,{label:"Conversation",title:"Core settings",detail:"Decide when Niko joins the conversation.",icon:"settings"}),s.jsxs("label",{className:"setting-row",children:[s.jsxs("span",{children:[s.jsx("strong",{children:"Enable AI chat"}),s.jsx("small",{children:"Respond when Niko is mentioned"})]}),s.jsx("input",{type:"checkbox",checked:p.enabled,onChange:w=>y({...p,enabled:w.target.checked})}),s.jsx("i",{"aria-hidden":"true"})]}),s.jsxs("div",{className:"personality-options",children:[s.jsxs("button",{type:"button",className:p.personality==="cafe"?"personality active":"personality",onClick:()=>y({...p,personality:"cafe"}),children:[s.jsx("span",{className:"personality-mark",children:"n"}),s.jsxs("span",{children:[s.jsx("strong",{children:"Café"}),s.jsx("small",{children:"Warm, playful, familiar"})]})]}),s.jsxs("button",{type:"button",className:p.personality==="normal"?"personality active":"personality",onClick:()=>y({...p,personality:"normal"}),children:[s.jsx("span",{className:"personality-mark",children:"—"}),s.jsxs("span",{children:[s.jsx("strong",{children:"Normal"}),s.jsx("small",{children:"Clear and straightforward"})]})]})]})]}),s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Dr,{label:"Experiments",title:"Optional context",detail:"Try new capabilities when your team is ready."}),s.jsxs("label",{className:"setting-row",children:[s.jsxs("span",{children:[s.jsx("strong",{children:"Better context"}),s.jsx("small",{children:"Use the last five channel messages"})]}),s.jsx("input",{type:"checkbox",checked:p.better_context_experiment,onChange:w=>y({...p,better_context_experiment:w.target.checked})}),s.jsx("i",{"aria-hidden":"true"})]}),s.jsxs("label",{className:"setting-row",children:[s.jsxs("span",{children:[s.jsx("strong",{children:"AI actions"}),s.jsx("small",{children:"Allow confirmed actions requested in chat"})]}),s.jsx("input",{type:"checkbox",checked:p.ai_actions_experiment,onChange:w=>y({...p,ai_actions_experiment:w.target.checked})}),s.jsx("i",{"aria-hidden":"true"})]}),s.jsx(ca,{state:E})]})]})]})}function zh({guildId:l,config:c,resources:u,csrfToken:p}){const y=(c==null?void 0:c.leveling)||{},[E,S]=D.useState({xp_enabled:!0,xp_multiplier:1,xp_cooldown:0,level_up_channel:"",level_up_message:""}),[F,w]=D.useState(la);D.useEffect(()=>S({xp_enabled:y.xp_enabled!==!1,xp_multiplier:y.xp_multiplier??1,xp_cooldown:y.xp_cooldown??0,level_up_channel:y.level_up_channel||"",level_up_message:y.level_up_message||""}),[c]);const O=L=>{L.preventDefault(),w({saving:!0,message:"",error:""}),Ys(l,"leveling",E,p).then(I=>{const R=I.config||{};S({xp_enabled:R.xp_enabled!==!1,xp_multiplier:R.xp_multiplier??1,xp_cooldown:R.xp_cooldown??0,level_up_channel:R.level_up_channel||"",level_up_message:R.level_up_message||""}),w({saving:!1,message:"Leveling settings saved to Niko.",error:""})}).catch(I=>w({saving:!1,message:"",error:I instanceof Error?I.message:"Could not save settings."}))};return s.jsxs(s.Fragment,{children:[s.jsx(ua,{icon:"spark",label:"Participation desk",title:E.xp_enabled?"XP is flowing":"XP is paused",text:"Set a pace that rewards regulars without turning every message into a transaction."}),s.jsx("form",{onSubmit:O,className:"settings-stack",children:s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Dr,{label:"Leveling settings",title:"Shape the pace",detail:"These controls apply to every member in this server.",icon:"spark"}),s.jsxs("label",{className:"setting-row",children:[s.jsxs("span",{children:[s.jsx("strong",{children:"Enable XP"}),s.jsx("small",{children:"Track activity and award levels"})]}),s.jsx("input",{type:"checkbox",checked:E.xp_enabled,onChange:L=>S({...E,xp_enabled:L.target.checked})}),s.jsx("i",{"aria-hidden":"true"})]}),s.jsxs("div",{className:"form-grid",children:[s.jsx(En,{label:"XP multiplier",hint:"From 0.1× to 10×",children:s.jsx("input",{type:"number",min:"0.1",max:"10",step:"0.1",value:E.xp_multiplier,onChange:L=>S({...E,xp_multiplier:L.target.value})})}),s.jsx(En,{label:"Cooldown (seconds)",hint:"0 disables the cooldown",children:s.jsx("input",{type:"number",min:"0",max:"86400",value:E.xp_cooldown,onChange:L=>S({...E,xp_cooldown:L.target.value})})}),s.jsx(En,{label:"Level-up channel",children:s.jsxs("select",{value:E.level_up_channel,onChange:L=>S({...E,level_up_channel:L.target.value}),children:[s.jsx("option",{value:"",children:"Same channel"}),u==null?void 0:u.channels.map(L=>s.jsxs("option",{value:L.id,children:["#",L.name]},L.id))]})}),s.jsx(En,{label:"Level-up message",hint:"Use {mention}, {level}, {name}, or {guild}",children:s.jsx("textarea",{rows:3,maxLength:1e3,value:E.level_up_message,onChange:L=>S({...E,level_up_message:L.target.value}),placeholder:"Leave blank for Niko's default message"})})]}),s.jsx(ca,{state:F})]})})]})}const Fh={saving:!1,message:"",error:""};function qe({label:l,hint:c,children:u}){return s.jsxs("label",{className:"form-field",children:[s.jsx("span",{className:"form-label",children:l}),u,c&&s.jsx("small",{children:c})]})}function Gs({label:l,title:c,detail:u,icon:p}){return s.jsxs("div",{className:"panel-heading settings-section-title",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:l}),s.jsx("h3",{children:c}),s.jsx("p",{children:u})]}),s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:p})})]})}function Oh({state:l}){return s.jsxs("div",{className:"setting-footer",children:[l.error?s.jsx("span",{className:"form-error",role:"alert",children:l.error}):s.jsx("span",{role:"status",children:l.message||"Changes apply to this server."}),s.jsx("button",{className:"button button-primary",type:"submit",disabled:l.saving,children:l.saving?"Saving...":"Save server settings"})]})}const Bh=[["moderation","Moderation"],["automod","AutoMod"],["messages","Messages"],["channels","Channels"],["members","Members"],["captcha","Captcha"],["invites","Invites"],["roles","Roles"],["server","Server"],["voice","Voice"]];function Uh(l,c){var u;return c?((u=l==null?void 0:l.channels.find(p=>p.id===String(c)))==null?void 0:u.name)||`Channel ${c}`:"Not set"}function ta(l){var p,y;const c=(l==null?void 0:l.onboarding)||{},u=(l==null?void 0:l.tickets)||{};return{prefixes:((p=l==null?void 0:l.prefixes)!=null&&p.length?l.prefixes:["."]).join(`
`),welcome_channel:c.welcome_channel?String(c.welcome_channel):"",welcome_title:c.welcome_title||"",welcome_description:c.welcome_description||"",welcome_color:c.welcome_color===null||c.welcome_color===void 0?"5865F2":c.welcome_color.toString(16).padStart(6,"0"),welcome_image:c.welcome_image||"",rules_channel:c.rules_channel?String(c.rules_channel):"",rules_text:c.rules_text||"",rules_role_id:c.rules_role_id?String(c.rules_role_id):"",logging:{...(l==null?void 0:l.logging)||{}},disabled_logging:[...((y=l==null?void 0:l.logging)==null?void 0:y.disabled)||[]],panel_title:u.panel_title||"",panel_description:u.panel_description||"",panel_categories:(u.panel_categories||[]).join(`
`),panel_channel_id:u.panel_channel_id||"",support_roles:[...u.support_roles||[]]}}function Wh({guildId:l,config:c,resources:u,csrfToken:p}){const[y,E]=D.useState(()=>ta(c==null?void 0:c.server)),[S,F]=D.useState(Fh);D.useEffect(()=>E(ta(c==null?void 0:c.server)),[c]);const w=(k,P)=>E(j=>({...j,[k]:P})),O=(k,P)=>E(j=>({...j,logging:{...j.logging,[k]:P}})),L=k=>E(P=>({...P,disabled_logging:P.disabled_logging.includes(k)?P.disabled_logging.filter(j=>j!==k):[...P.disabled_logging,k]})),I=k=>{k.preventDefault(),F({saving:!0,message:"",error:""});const P=y.prefixes.split(/\r?\n|,/).map(H=>H.trim()).filter(Boolean),j=y.panel_categories.split(/\r?\n|,/).map(H=>H.trim()).filter(Boolean);Ys(l,"server",{prefixes:P,onboarding:{welcome_channel:y.welcome_channel,welcome_title:y.welcome_title,welcome_description:y.welcome_description,welcome_color:y.welcome_color,welcome_image:y.welcome_image,rules_channel:y.rules_channel,rules_text:y.rules_text,rules_role_id:y.rules_role_id},logging:{...y.logging,disabled:y.disabled_logging},tickets:{panel_title:y.panel_title,panel_description:y.panel_description,panel_categories:j,panel_channel_id:y.panel_channel_id,support_roles:y.support_roles}},p).then(H=>{E(ta({...c==null?void 0:c.server,...H.config})),F({saving:!1,message:"Server settings saved to Niko.",error:""})}).catch(H=>F({saving:!1,message:"",error:H instanceof Error?H.message:"Could not save server settings."}))};c==null||c.server;const R=y.welcome_channel,G=y.panel_channel_id;return s.jsxs(s.Fragment,{children:[s.jsx(kt,{eyebrow:"Server settings",title:"Make Niko fit your room.",text:"Manage the settings that shape how Niko behaves in this server. Economy balances remain global to each user and are not configured here."}),s.jsxs("div",{className:"settings-intro",children:[s.jsx("span",{className:"settings-intro-icon",children:s.jsx(Y,{name:"settings"})}),s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Server control room"}),s.jsxs("strong",{children:[y.prefixes.split(/\r?\n|,/).filter(Boolean).length||0," command prefixes configured"]}),s.jsx("p",{children:"Welcome flows, log destinations, and ticket panels all live here."})]}),s.jsxs("span",{className:"settings-intro-state",children:[s.jsx("span",{className:"status-dot"})," Per server"]})]}),s.jsxs("form",{onSubmit:I,className:"settings-stack server-settings-stack",children:[s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Gs,{label:"Commands",title:"Prefixes",detail:"Use one prefix per line. Niko will respond to all of them.",icon:"terminal"}),s.jsx(qe,{label:"Command prefixes",hint:"The default prefix is .",children:s.jsx("textarea",{rows:3,maxLength:200,value:y.prefixes,onChange:k=>w("prefixes",k.target.value),placeholder:".\\n!"})})]}),s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Gs,{label:"Welcome flow",title:"Welcome and rules",detail:"Choose where new members see your welcome message and rules.",icon:"users"}),s.jsxs("div",{className:"form-grid",children:[s.jsx(qe,{label:"Welcome channel",children:s.jsxs("select",{value:R,onChange:k=>w("welcome_channel",k.target.value),children:[s.jsx("option",{value:"",children:"Disabled"}),u==null?void 0:u.channels.map(k=>s.jsxs("option",{value:k.id,children:["#",k.name]},k.id))]})}),s.jsx(qe,{label:"Welcome title",children:s.jsx("input",{value:y.welcome_title,maxLength:200,onChange:k=>w("welcome_title",k.target.value),placeholder:"Welcome to the server"})}),s.jsx(qe,{label:"Welcome message",hint:"Supports {user} and {name}",children:s.jsx("textarea",{rows:4,maxLength:2e3,value:y.welcome_description,onChange:k=>w("welcome_description",k.target.value),placeholder:"Welcome {user}!"})}),s.jsx(qe,{label:"Accent color",hint:"Hex color, for example 5865F2",children:s.jsx("input",{value:y.welcome_color,maxLength:7,onChange:k=>w("welcome_color",k.target.value),placeholder:"5865F2"})}),s.jsx(qe,{label:"Welcome image URL",children:s.jsx("input",{type:"url",value:y.welcome_image,onChange:k=>w("welcome_image",k.target.value),placeholder:"https://..."})}),s.jsx(qe,{label:"Rules channel",children:s.jsxs("select",{value:y.rules_channel,onChange:k=>w("rules_channel",k.target.value),children:[s.jsx("option",{value:"",children:"Not configured"}),u==null?void 0:u.channels.map(k=>s.jsxs("option",{value:k.id,children:["#",k.name]},k.id))]})}),s.jsx(qe,{label:"Rules text",children:s.jsx("textarea",{rows:4,maxLength:2e3,value:y.rules_text,onChange:k=>w("rules_text",k.target.value),placeholder:"Write the rules members should acknowledge."})}),s.jsx(qe,{label:"Role after rules acknowledgment",children:s.jsxs("select",{value:y.rules_role_id,onChange:k=>w("rules_role_id",k.target.value),children:[s.jsx("option",{value:"",children:"No role"}),u==null?void 0:u.roles.map(k=>s.jsxs("option",{value:k.id,children:["@",k.name]},k.id))]})})]})]}),s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Gs,{label:"Audit trail",title:"Logging destinations",detail:"Pick a channel for each event type and disable categories you do not need.",icon:"book"}),s.jsx("div",{className:"server-logging-list",children:Bh.map(([k,P])=>s.jsxs("div",{className:"server-logging-row",children:[s.jsxs("label",{className:"form-field",children:[s.jsxs("span",{className:"form-label",children:[P," logs"]}),s.jsxs("select",{value:String(y.logging[k]||""),onChange:j=>O(k,j.target.value),children:[s.jsx("option",{value:"",children:"Not set"}),u==null?void 0:u.channels.map(j=>s.jsxs("option",{value:j.id,children:["#",j.name]},j.id))]})]}),s.jsxs("label",{className:"setting-row compact-setting-row",children:[s.jsxs("span",{children:[s.jsx("strong",{children:"Enabled"}),s.jsx("small",{children:Uh(u,y.logging[k])})]}),s.jsx("input",{type:"checkbox",checked:!y.disabled_logging.includes(k),onChange:()=>L(k)}),s.jsx("i",{"aria-hidden":"true"})]})]},k))})]}),s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Gs,{label:"Support desk",title:"Ticket panel",detail:"Configure the public panel and decide who can handle tickets.",icon:"users"}),s.jsxs("div",{className:"form-grid",children:[s.jsx(qe,{label:"Panel title",children:s.jsx("input",{value:y.panel_title,maxLength:200,onChange:k=>w("panel_title",k.target.value),placeholder:"Open a Ticket"})}),s.jsx(qe,{label:"Panel channel",children:s.jsxs("select",{value:G,onChange:k=>w("panel_channel_id",k.target.value),children:[s.jsx("option",{value:"",children:"Keep current panel channel"}),u==null?void 0:u.channels.map(k=>s.jsxs("option",{value:k.id,children:["#",k.name]},k.id))]})}),s.jsx(qe,{label:"Panel description",children:s.jsx("textarea",{rows:4,maxLength:2e3,value:y.panel_description,onChange:k=>w("panel_description",k.target.value),placeholder:"Tell members what the ticket panel is for."})}),s.jsx(qe,{label:"Ticket categories",hint:"One category per line",children:s.jsx("textarea",{rows:4,value:y.panel_categories,onChange:k=>w("panel_categories",k.target.value),placeholder:"General\\nSupport\\nReports"})}),s.jsx(qe,{label:"Support roles",hint:"Hold Ctrl/Cmd to select more than one",children:s.jsx("select",{multiple:!0,value:y.support_roles,onChange:k=>w("support_roles",Array.from(k.target.selectedOptions,P=>P.value)),children:u==null?void 0:u.roles.map(k=>s.jsxs("option",{value:k.id,children:["@",k.name]},k.id))})})]}),s.jsx("p",{className:"form-hint",children:"Saving panel settings updates the existing posted panel when Niko can find its saved message."})]}),s.jsx(Oh,{state:S})]})]})}function Vh({auth:l}){const c=Js();return s.jsxs(s.Fragment,{children:[s.jsx(st,{page:"dashboard"}),s.jsx("main",{className:"auth-page",children:s.jsxs("div",{className:"auth-card",children:[s.jsx("span",{className:"auth-mark",children:"n"}),s.jsx("div",{className:"eyebrow",children:"Private workspace"}),s.jsxs("h1",{children:["Settle in, ",s.jsx("em",{children:"admin."})]}),s.jsx("p",{children:"Sign in with Discord to see your Niko profile and manage the servers you look after."}),l.oauth_available?s.jsxs("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard",children:[s.jsx(Y,{name:"lock"})," Continue with Discord ",s.jsx(Y,{name:"arrow"})]}):s.jsxs("div",{className:"notice warning",children:["Discord login is not configured yet. Add ",s.jsx("code",{children:"DISCORD_CLIENT_SECRET"})," to the environment and restart the bot."]}),!c&&s.jsx("p",{className:"form-hint",children:"The public bot configuration is still loading."}),s.jsx("a",{className:"back-link",href:"/",onClick:u=>{u.preventDefault(),fe("/")},children:"Return to public site"})]})})]})}function $h({section:l,guild:c,stats:u,csrfToken:p}){const[y,E]=D.useState(null),[S,F]=D.useState([]),[w,O]=D.useState(null),[L,I]=D.useState(null),[R,G]=D.useState(!0),[k,P]=D.useState("");return D.useEffect(()=>{G(!0),P(""),(l==="overview"?Xm(c.id).then(E):l==="leveling"?Promise.all([qm(c.id),pc(c.id),gc(c.id)]).then(([H,le,je])=>{F(H),O(le),I(je)}):Promise.all([pc(c.id),gc(c.id)]).then(([H,le])=>{O(H),I(le)})).catch(H=>P(H instanceof Error?H.message:"This server could not be loaded.")).finally(()=>G(!1))},[c.id,l]),R?s.jsxs("div",{className:"section-loading section-skeleton",role:"status","aria-label":`Loading ${l}`,children:[s.jsx("div",{className:"skeleton-title"}),s.jsx("div",{className:"skeleton-copy"}),s.jsxs("div",{className:"skeleton-grid",children:[s.jsx("i",{}),s.jsx("i",{}),s.jsx("i",{})]}),s.jsxs("span",{children:["Loading ",l,"..."]})]}):k?s.jsxs("div",{className:"inline-error",role:"alert",children:[s.jsx("strong",{children:"Couldn’t load this page."}),s.jsx("span",{children:k}),s.jsx("button",{className:"button button-muted",onClick:()=>window.location.reload(),children:"Try again"})]}):l==="overview"&&y?s.jsx(Rh,{overview:y}):l==="leveling"?s.jsx(Dh,{guildId:c.id,rows:S,config:w,resources:L,csrfToken:p}):l==="moderation"?s.jsx(Ah,{guildId:c.id,config:w,csrfToken:p}):l==="server"?s.jsx(Wh,{guildId:c.id,config:w,resources:L,csrfToken:p}):s.jsx(Ih,{guildId:c.id,config:w,csrfToken:p})}function Hh(){return s.jsxs("div",{className:"section-loading section-skeleton dashboard-loading",role:"status",children:[s.jsx("div",{className:"skeleton-title"}),s.jsx("div",{className:"skeleton-copy"}),s.jsxs("div",{className:"skeleton-grid",children:[s.jsx("i",{}),s.jsx("i",{}),s.jsx("i",{})]}),s.jsx("span",{children:"Preparing your dashboard..."})]})}function Qh(){Js();const[l,c]=D.useState(xc),[u,p]=D.useState(null),[y,E]=D.useState(null),[S,F]=D.useState(null),[w,O]=D.useState([]),[L,I]=D.useState(null),[R,G]=D.useState(!0),[k,P]=D.useState("");if(D.useEffect(()=>{const M=()=>c(xc());return window.addEventListener("popstate",M),()=>window.removeEventListener("popstate",M)},[]),D.useEffect(()=>{G(!0),Promise.all([$m(),Ec()]).then(([M,J])=>(p(M),E(J),M.authenticated?Promise.all([Gm(),Km()]).then(([de,Ee])=>{F(de),O(Ee)}):null)).catch(M=>P(M instanceof Error?M.message:"Dashboard unavailable")).finally(()=>G(!1))},[]),D.useEffect(()=>{if(l.view!=="guild"){I(null);return}const M=w.find(J=>J.id===l.guildId&&J.installed!==!1);M?(I(M),localStorage.setItem("niko-guild",M.id)):l.guildId&&w.length&&fe(yc())},[w,l.guildId,l.view]),R||!u)return s.jsxs("div",{className:"dashboard-state",children:[s.jsx("div",{className:"loading-ring"}),s.jsx("p",{children:"Connecting to Niko…"})]});if(k)return s.jsxs(s.Fragment,{children:[s.jsx(st,{page:"dashboard"}),s.jsx("main",{className:"auth-page",children:s.jsxs("div",{className:"auth-card",children:[s.jsx("span",{className:"auth-mark",children:"!"}),s.jsx("div",{className:"eyebrow",children:"Connection issue"}),s.jsxs("h1",{children:["Couldn’t load",s.jsx("br",{}),s.jsx("em",{children:"your workspace."})]}),s.jsx("p",{children:k}),s.jsxs("button",{className:"button button-primary",onClick:()=>window.location.reload(),children:["Try again ",s.jsx(Y,{name:"arrow"})]})]})})]});if(!u.authenticated)return s.jsx(Vh,{auth:u});const j=M=>{M.installed!==!1&&(localStorage.setItem("niko-guild",M.id),fe(Rr(M.id,l.section)))},H=M=>{M.installed!==!1&&(localStorage.setItem("niko-guild",M.id),fe(Rr(M.id,"overview")))},le=M=>{fe(L?Rr(L.id,M):Rr())},je=()=>fe(Rr()),pe=()=>fe(yc());let be;return l.view==="servers"?be=s.jsx(Lh,{guilds:w,onManage:H}):l.view==="guild"?be=L?s.jsx($h,{section:l.section,guild:L,stats:y,csrfToken:u.csrf_token},`${L.id}-${l.section}`):s.jsx(Hh,{}):be=s.jsx(Th,{user:u.user,overview:S,guilds:w,onServers:pe,onManage:H}),s.jsx(Mh,{user:u.user,guilds:w,selectedGuild:L,view:l.view,section:l.section,stats:y,onHome:je,onServers:pe,onGuildChange:j,onSectionChange:le,children:be})}function Kh({value:l,onChange:c,placeholder:u="Search documentation...",onFocus:p,onBlur:y}){const[E,S]=D.useState(!1),F=D.useRef(null),[w,O]=D.useState(!1);D.useEffect(()=>{const k=P=>{var j;(P.metaKey||P.ctrlKey)&&P.key==="k"&&(P.preventDefault(),(j=F.current)==null||j.focus())};return document.addEventListener("keydown",k),()=>document.removeEventListener("keydown",k)},[]);const L=()=>{S(!0),O(!0),p==null||p()},I=()=>{S(!1),setTimeout(()=>O(!1),200),y==null||y()},R=k=>{c(k.target.value)},G=k=>{var P;k.key==="Escape"&&((P=F.current)==null||P.blur())};return s.jsxs("div",{className:`doc-search-bar ${w?"expanded":""}`,children:[s.jsxs("div",{className:"search-input-wrapper",children:[s.jsx(Y,{name:"search",className:"search-icon"}),s.jsx("input",{ref:F,type:"text",value:l,onChange:R,onFocus:L,onBlur:I,onKeyDown:G,placeholder:u,className:"search-input","aria-label":"Search documentation"}),s.jsxs("kbd",{className:"search-shortcut",children:[s.jsx("span",{className:"shortcut-key",children:"⌘"}),"K"]})]}),s.jsxs("div",{className:"search-hint",children:["Press ",s.jsx("kbd",{children:"⌘K"})," to focus search"]})]})}function Gh({selectedCategory:l,onSelectCategory:c,sections:u,allCategoriesLabel:p="All Categories"}){return s.jsx("div",{className:"doc-filters",children:s.jsxs("div",{className:"filter-tabs",role:"tablist","aria-label":"Filter by category",children:[s.jsx("button",{role:"tab","aria-selected":l==="",className:`filter-tab ${l===""?"active":""}`,onClick:()=>c(""),children:p}),u.map(y=>s.jsxs("button",{role:"tab","aria-selected":l===y.id,className:`filter-tab ${l===y.id?"active":""}`,onClick:()=>c(y.id),children:[s.jsx(Y,{name:y.icon,size:14}),s.jsx("span",{children:y.label})]},y.id))]})})}function ra({doc:l,variant:c="default"}){const u="page"in l?l.page:l,[p,y]=D.useState(!1),E=w=>{w.preventDefault(),fe(`/docs/${u.slug}`)},S=w=>{(w.key==="Enter"||w.key===" ")&&(w.preventDefault(),fe(`/docs/${u.slug}`))};if(c==="compact")return s.jsx("a",{href:`/docs/${u.slug}`,onClick:E,onKeyDown:S,className:"doc-card-compact",tabIndex:0,role:"button",children:s.jsxs("div",{className:"compact-content",children:[s.jsx("span",{className:"compact-title",children:u.title}),s.jsx("span",{className:"compact-excerpt",children:u.excerpt})]})});const F="highlights"in l?l.highlights:[];return s.jsx("article",{className:`doc-card ${c==="highlighted"?"highlighted":""}`,children:s.jsxs("div",{className:`doc-card-content ${p?"loaded":""}`,children:[s.jsxs("div",{className:"doc-card-header",children:[s.jsx("span",{className:"doc-category",children:u.category.replace(/-/g," ")}),s.jsxs("span",{className:"doc-order",children:["#",u.order]})]}),s.jsx("h3",{className:"doc-title",children:u.title}),s.jsx("p",{className:"doc-excerpt",children:u.excerpt}),F.length>0&&s.jsx("div",{className:"doc-highlights",children:F.slice(0,2).map((w,O)=>s.jsxs("p",{className:"highlight-snippet",children:[w.slice(0,150),w.length>150?"...":""]},O))}),s.jsxs("div",{className:"doc-card-footer",children:[s.jsx("div",{className:"doc-tags",children:u.tags.slice(0,3).map(w=>s.jsxs("span",{className:"doc-tag",children:["#",w]},w))}),s.jsxs("a",{href:`/docs/${u.slug}`,onClick:E,onKeyDown:S,className:"doc-read-more",children:["Read more ",s.jsx(Y,{name:"arrow",size:14})]})]})]})})}const Te=[{slug:"welcome",title:"Welcome to Niko",category:"getting-started",excerpt:"New to Niko? Start here to understand what the bot can do for your server.",tags:["introduction","overview","beginner"],order:1,content:`
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

- Default prefix: \`niko\` or your server's custom prefix
- Use \`niko help\` to see available commands
- Use \`niko setprefix <new prefix>\` to change it

## Setting a Custom Prefix

To set a custom prefix for your server:

\`\`\`
niko setprefix !
\`\`\`

Or use the dashboard to configure it visually.

## Command Types

- **Slash Commands** (\`/\`): Modern, contextual commands
- **Prefix Commands** (\`niko\`): Traditional text commands
- **Hybrid Commands**: Both slash and prefix versions available

Most features are available through both command types.
    `},{slug:"server-configuration",title:"Server Configuration Basics",category:"setup",excerpt:"Learn the essentials of configuring Niko for your server.",tags:["configuration","settings","admin"],order:1,content:`
# Server Configuration Basics

Proper server configuration ensures Niko works the way you want. This guide covers the essential settings.

## Access Settings

There are two ways to configure Niko:

1. **Discord Commands**: Use commands like \`niko settings\` or category-specific commands
2. **Web Dashboard**: Visit the dashboard at \`/dashboard\` for a visual interface

## Essential Settings to Configure

### Welcome Messages
Set up welcome messages for new members:
\`\`\`
niko onboarding setup
\`\`\`

### Logging Channels
Configure where moderation and event logs are sent:
\`\`\`
niko logging status
\`\`\`

### Moderation Settings
Customize moderation behavior:
\`\`\`
niko automod
\`\`\`

### Leveling Settings
Configure XP and leveling:
\`\`\`
niko leveling
\`\`\`

## Setting Up Categories

For larger servers, consider setting up category-specific settings:

- Different welcome channels for different sections
- Separate log channels for different moderation types
- Custom leveling rates per channel
    `},{slug:"roles-and-permissions",title:"Roles and Permissions Guide",category:"setup",excerpt:"Understand how Niko interacts with Discord roles and permissions.",tags:["roles","permissions","admin"],order:2,content:`
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
niko work
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
- \`job\` - See your current job
- \`jobs\` - View available jobs
- \`promote\` - Advance to better jobs (when available)
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
niko deposit <amount>
\`\`\`

### Withdraw
Take money from bank to balance:

\`\`\`
niko withdraw <amount>
\`\`\`

### Bank Info
Check your bank status:

\`\`\`
niko bank
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
niko shop
\`\`\`

### Buy Items
\`\`\`
niko buy <item name or id>
\`\`\`

### View Inventory
\`\`\`
niko inventory
\`\`\`

### Use Items
Some items are automatic, others need to be activated:
\`\`\`
niko use <item name>
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
Classic slot machine game with various symbols and payout combinations.

\`\`\`
niko slots <bet amount>
\`\`\`

### Blackjack
Play against the dealer in this classic card game.

\`\`\`
niko blackjack <bet amount>
\`\`\`

### Roulette
Bet on numbers, colors, or combinations in roulette.

\`\`\`
niko roulette <bet amount> <bet type>
\`\`\`

### Lottery
Weekly lottery where members buy tickets for a chance at the pot.

\`\`\`
niko lottery <tickets>
\`\`\`

## Gambling Commands

### General
- \`casino\` - Open the casino interface
- \`slots\` - Play slots
- \`blackjack\` - Play blackjack
- \`roulette\` - Play roulette
- \`lottery\` - Buy lottery tickets

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

Niko's leveling system rewards members for participating in your server with XP and level-ups.

## How Leveling Works

### Earning XP
Members earn XP when they:
- Send messages in enabled channels
- Participate in activities
- Reach certain milestones

### Level Progression
Each level requires more XP than the last:
- Level 1: 100 XP
- Level 2: 200 XP
- Level 3: 350 XP
- (and increasing)

### XP Formula
The XP needed for each level increases progressively:
\`\`\`
XP for next level = current_level * 100 + 100
\`\`\`

## Configuration

### Enable/Disable Leveling
\`\`\`
niko leveling toggle
\`\`\`

### Set XP Multiplier
Adjust how fast members level:

\`\`\`
niko leveling multiplier <value>
\`\`\`

### Set Cooldown
Prevent XP spam with cooldowns:

\`\`\`
niko leveling cooldown <seconds>
\`\`\`

### Level Up Channel
Choose where level-up announcements appear:

\`\`\`
niko leveling channel <channel>
\`\`\`

### Custom Level Up Messages
Set custom messages for level-ups:

\`\`\`
niko leveling message <message>
\`\`\`

Use \`{user}\`, \`{level}\`, and \`{guild}\` in your message.

## Level Rewards

### Automatic Rewards
Members can be rewarded automatically on level-up:
- Role assignments
- Custom messages
- Channel announcements

### Level Roles
Assign roles at specific levels:

\`\`\`
niko leveling role <level> <role>
\`\`\`

## Leaderboards

View leveling leaderboards:

\`\`\`
niko leaderboard
\`\`\`

Shows:
- Top leveled members
- XP totals
- Level rankings

## Leveling Tips

1. **Enable in all channels**: More channels = more XP opportunities
2. **Set reasonable multipliers**: Don't make leveling too fast or slow
3. **Use cooldowns**: Prevent XP grinding abuse
4. **Celebrate milestones**: Level-up announcements build engagement
5. **Reward participation**: Leveling encourages activity
    `},{slug:"leveling-configuration",title:"Leveling Configuration Guide",category:"leveling",excerpt:"Detailed guide to configuring every aspect of the leveling system.",tags:["leveling","configuration","admin"],order:2,content:`
# Leveling Configuration Guide

Fine-tune the leveling system to match your server's needs.

## Basic Settings

### Enable/Disable
Toggle the entire leveling system on or off:

\`\`\`
niko leveling toggle
\`\`\`

When disabled, no XP is earned and level-up events don't fire.

### XP Multiplier
Adjust the rate at which members earn XP:

\`\`\`
niko leveling multiplier <number>
\`\`\`

- \`1.0\` = Normal speed
- \`2.0\` = Double speed
- \`0.5\` = Half speed

### XP Cooldown
Set a cooldown between XP gains from messages:

\`\`\`
niko leveling cooldown <seconds>
\`\`\`

Example: \`niko leveling cooldown 60\` gives 60 seconds between XP from messages.

## Channel Configuration

### Enable/Disable Channels
Specify which channels give XP:

\`\`\`
niko leveling channel add <channel>
niko leveling channel remove <channel>
\`\`\`

### Channel Overrides
Set different multipliers for specific channels:

\`\`\`
niko leveling channel set <channel> multiplier <value>
\`\`\`

## Announcements

### Level Up Channel
Set where level-up notifications are sent:

\`\`\`
niko leveling levelupchannel <channel>
\`\`\`

### Custom Messages
Set custom level-up messages:

\`\`\`
niko leveling message <message>
\`\`\`

Placeholders:
- \`{user}\` - Username
- \`{level}\` - New level
- \`{guild}\` - Server name
- \`{xp}\` - XP earned

Example:
\`\`\`
niko leveling message " 축하 {user}님이 이제 레벨 {level}이 되었습니다!"
\`\`\`

## Level Roles

### Assigning Roles
Give roles when members reach certain levels:

\`\`\`
niko leveling role add <level> <role mention or id>
\`\`\`

Example:
\`\`\`
niko leveling role add 10 @Member @
niko leveling role add 50 @Regular @
niko leveling role add 100 @Veteran @
\`\`\`

### Removing Roles
Remove level-based roles:

\`\`\`
niko leveling role remove <level>
\`\`\`

## Advanced Settings

### Minimum Account Age
Prevent very new accounts from earning XP:

\`\`\`
niko leveling minage <days>
\`\`\`

### Minimum Server Join Age
Prevent recent joins from earning XP:

\`\`\`
niko leveling minjoin <days>
\`\`\`

### Ignore Bots
Toggle whether bots can earn XP:

\`\`\`
niko leveling ignorebots
\`\`\`

## Resetting Leveling Data

To reset all leveling data for your server:

\`\`\`
niko leveling reset
\`\`\`

> **Warning**: This permanently deletes all leveling progress!
    `},{slug:"moderation-overview",title:"Moderation Tools Overview",category:"moderation",excerpt:"Comprehensive guide to Niko's moderation features including warns, mutes, and moderation commands.",tags:["moderation","warns","mutes","kicks","bans"],order:1,content:`
# Moderation Tools Overview

Niko provides a complete set of moderation tools to help you manage your server.

## Moderation Commands

### Warning System
Issue warnings to members:

\`\`\`
niko warn <user> [reason]
\`\`\`

Warnings are tracked per user and can be viewed or cleared.

### Muting
Temporarily prevent a member from speaking:

\`\`\`
niko mute <user> [duration] [reason]
\`\`\`

Duration examples:
- \`1h\` - 1 hour
- \`30m\` - 30 minutes
- \`1d\` - 1 day
- \`7d\` - 1 week

### Unmuting
Remove a mute:

\`\`\`
niko unmute <user>
\`\`\`

### Kicking
Remove a member from the server:

\`\`\`
niko kick <user> [reason]
\`\`\`

### Banning
Ban a member from the server:

\`\`\`
niko ban <user> [reason]
\`\`\`

### Temporary Mutes
Mute a member for a specific duration:

\`\`\`
niko tempmute <user> <duration> [reason]
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
| \`unban\` | Unban a member |
| \`modlog\` | View moderation logs |

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
niko warn <user> [reason]
\`\`\`

Example:
\`\`\`
niko warn @User Spamming in general chat
\`\`\`

### Warnings with Evidence
It's helpful to include specific details:
- What rule was broken
- When it happened
- Any relevant context

## Viewing Warnings

### Check a User's Warnings
\`\`\`
niko warnings <user>
\`\`\`

This shows:
- Total warning count
- Each warning with moderator and reason
- When each warning was issued

### Check Your Own Warnings
Members can check their own warnings:

\`\`\`
niko warnings
\`\`\`

## Clearing Warnings

### Clear All Warnings
Remove all warnings from a member:

\`\`\`
niko clearwarnings <user>
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
A permanent mute until manually removed:

\`\`\`
niko mute <user> [reason]
\`\`\`

### Temporary Mute
A mute that expires automatically:

\`\`\`
niko tempmute <user> <duration> [reason]
\`\`\`

Duration formats:
- \`1h\` - 1 hour
- \`30m\` - 30 minutes  
- \`2h30m\` - 2 hours 30 minutes
- \`1d\` - 1 day
- \`7d\` - 7 days

### Timeout (Discord Native)
Uses Discord's built-in timeout feature:

\`\`\`
niko timeout <user> <duration> [reason]
\`\`\`

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
Temporary mutes are automatically removed when the duration expires. Niko checks every 15 seconds for expired mutes.

## Unmuting

### Remove a Mute
\`\`\`
niko unmute <user>
\`\`\`

This removes the Muted role and restores the member's permissions.

## Mute Commands

| Command | Description |
|---------|-------------|
| \`mute\` | Permanently mute a member |
| \`tempmute\` | Temporarily mute a member |
| \`unmute\` | Remove a mute |
| \`timeout\` | Use Discord timeout |
| \`removetimeout\` | Remove a timeout |

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
\`\`\`
niko automod
\`\`\`

Or use the dashboard for visual configuration.

### Toggle Features
Each AutoMod feature can be toggled on/off independently:

\`\`\`
niko automod antispam toggle
niko automod antilink toggle
niko automod badwords toggle
\`\`\`

## Actions

When AutoMod detects an issue, it can:
- **Warn**: Send a warning to the member
- **Delete**: Remove the offending message
- **Mute**: Temporarily mute the member
- **Kick**: Remove the member
- **Ban**: Permanently ban the member
- **Notify**: Alert moderators

## Whitelisting

### User Whitelist
Exclude specific users from AutoMod:

\`\`\`
niko automod whitelist add <user>
\`\`\`

### Role Whitelist
Exclude members with specific roles:

\`\`\`
niko automod whitelist role add <role>
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

### Spam Threshold
Set how many messages trigger spam detection:

\`\`\`
niko automod spamthreshold <count>
\`\`\`

Default: 6 messages

### Spam Interval
Set the time window for counting messages:

\`\`\`
niko automod spaminterval <seconds>
\`\`\`

Default: 7 seconds

### Max Mentions
Limit mentions per message:

\`\`\`
niko automod maxmentions <count>
\`\`\`

Default: 5 mentions

## Actions

Choose what happens when spam is detected:

\`\`\`
niko automod antispam action <action>
\`\`\`

Actions:
- \`warn\` - Warn the member
- \`mute\` - Mute the member
- \`kick\` - Kick the member
- \`ban\` - Ban the member
- \`notify\` - Just notify moderators

## Mass Mention Protection

### Enable Mass Mention Detection
\`\`\`
niko automod massmention toggle
\`\`\`

### Set Threshold
\`\`\`
niko automod massmention threshold <count>
\`\`\`

## Customization

### Whitelist Channels
Some channels may be exempt from anti-spam:

\`\`\`
niko automod exemptchannel add <channel>
niko automod exemptchannel remove <channel>
\`\`\`

### Whitelist Users
Specific users can be exempt:

\`\`\`
niko automod whitelist add <user>
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
Set how many actions trigger a response:

\`\`\`
niko automod antinuke threshold <action> <count>
\`\`\`

Example:
\`\`\`
niko automod antinuke threshold channel_delete 3
\`\`\`

### Time Window
Actions are counted within a time window:

\`\`\`
niki automod antinuke interval <seconds>
\`\`\`

Default: 10 seconds

## Actions

Choose what happens when anti-nuke triggers:

### Strip Dangerous Roles
Remove roles with dangerous permissions from the offender.

### Kick
Kick the offending member.

### Ban
Ban the offending member.

Set the action:
\`\`\`
niko automod antinuke action <strip|kick|ban>
\`\`\`

## Response

When anti-nuke triggers:
1. The offending user is immediately actioned
2. A log is sent to your moderation log channel
3. The server owner receives a DM notification
4. Further actions from that user are suppressed for a cooldown period

## Configuration

### Enable Anti-Nuke
\`\`\`
niko automod antinuke toggle
\`\`\`

### Set Thresholds
\`\`\`
niko automod antinuke threshold channel_delete 3
niko automod antinuke threshold role_delete 3
niko automod antinuke threshold ban 3
\`\`\`

### Set Action
\`\`\`
niko automod antinuke action strip
\`\`\`

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
Detects when many members join in a short period:

\`\`\`
niko automod antiraid jointhreshold <count>
\`\`\`

Default: 10 joins

\`\`\`
niko automod antiraid joininterval <seconds>
\`\`\`

Default: 10 seconds

### New Account Detection
Filter out accounts that are too new:

\`\`\`
niko automod antiraid newaccountdays <days>
\`\`\`

Example: \`niko automod antiraid newaccountdays 7\` blocks accounts less than 7 days old.

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

Set the action:
\`\`\`
niko automod antiraid action <kick|ban|slowmode|lockdown>
\`\`\`

## External App Detection

Detect members using external apps/bots:

\`\`\`
niko automod antiraid ext enabled
\`\`\`

Configuration:
- Interaction threshold: How many interactions trigger detection
- Interaction window: Time window for counting
- Join age limit: Minimum account age
- Action: What to do with detected accounts

## Configuration

### Enable Anti-Raid
\`\`\`
niko automod antiraid toggle
\`\`\`

### Set Parameters
\`\`\`
niko automod antiraid jointhreshold 10
niko automod antiraid joininterval 10
niko automod antiraid action kick
\`\`\`

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
niko birthday set <date>
niko birthday remove
niko birthday today
\`\`\`

Birthdays are stored per member and can be announced in a designated channel.

### Polls
Create polls for server decisions:

\`\`\`
niko poll create <question>
niko poll vote <poll id> <option>
niko poll results <poll id>
\`\`\`

Supports multiple choice options and various voting methods.

### Suggestions
Let members submit suggestions:

\`\`\`
niko suggest <suggestion>
\`\`\`

Suggestions can be voted on and reviewed by moderators.

### Starboard
Highlight starred messages:

\`\`\`
niko starboard set <channel>
\`\`\`

Messages with enough stars are automatically posted to the starboard channel.

### Giveaways
Host giveaways for your community:

\`\`\`
niko giveaway start <duration> <prize>
niko giveaway reroll <message id>
\`\`\`

## Configuration

Most social features are configured through:
- Discord commands
- Web dashboard

### Birthday Channel
Set where birthday announcements appear:

\`\`\`
niko birthday channel <channel>
\`\`\`

### Starboard Threshold
Set how many stars trigger starboard posting:

\`\`\`
niko starboard threshold <count>
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
niko birthday set <month>/<day>
\`\`\`

Example:
\`\`\`
niko birthday set 6/15
\`\`\`

### Remove Your Birthday
\`\`\`
niko birthday remove
\`\`\`

### Check Your Birthday
\`\`\`
niko birthday
\`\`\`

## Server Birthdays

### Today's Birthdays
See who has birthdays today:

\`\`\`
niko birthday today
\`\`\`

### Birthday Channel
Set a channel for birthday announcements:

\`\`\`
niko birthday channel <channel>
\`\`\`

When someone has a birthday, Niko will announce it in this channel.

## Configuration

### Enable Birthday Announcements
\`\`\`
niko birthday toggle
\`\`\`

### Set Announcement Channel
\`\`\`
niko birthday channel #birthdays
\`\`\`

### Custom Messages
Set a custom birthday message:

\`\`\`
niko birthday message <message>
\`\`\`

Use \`{user}\` for the member's name.

## Birthday Commands

| Command | Description |
|---------|-------------|
| \`birthday set\` | Set your birthday |
| \`birthday remove\` | Remove your birthday |
| \`birthday\` | Show your birthday |
| \`birthday today\` | Show today's birthdays |
| \`birthday channel\` | Set announcement channel |
| \`birthday toggle\` | Enable/disable announcements |

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
niko poll create <question>
\`\`\`

### Poll with Options
Create a poll with custom options:

\`\`\`
niko poll create <question> | <option 1> | <option 2> | <option 3>
\`\`\`

Example:
\`\`\`
niko poll create "What should our next community event be?" | "Game Night" | "Movie Watch" | "Trivia Contest"
\`\`\`

## Voting

### Vote in a Poll
\`\`\`
niko poll vote <poll id> <option>
\`\`\`

### View Poll Results
\`\`\`
niko poll results <poll id>
\`\`\`

## Poll Management

### End a Poll Early
\`\`\`
niko poll end <poll id>
\`\`\`

### Delete a Poll
\`\`\`
niko poll delete <poll id>
\`\`\`

## Poll Features

### Vote Tracking
- Each user can only vote once per poll
- Vote counts are tracked in real-time
- Results show percentage breakdowns

### Poll Duration
Polls can be set to expire after a duration:

\`\`\`
niko poll create <question> | <duration>
\`\`\`

Duration formats:
- \`1h\` - 1 hour
- \`1d\` - 1 day
- \`1w\` - 1 week

## Poll Commands

| Command | Description |
|---------|-------------|
| \`poll create\` | Create a new poll |
| \`poll vote\` | Vote in a poll |
| \`poll results\` | View poll results |
| \`poll end\` | End a poll early |
| \`poll delete\` | Delete a poll |
| \`poll list\` | List active polls |

## Tips

1. **Keep it simple**: Clear questions get better responses
2. **Use appropriate options**: Cover the main possibilities
3. **Set reasonable durations**: Give enough time but not too much
4. **Follow up**: Share results and act on feedback
5. **Use for decisions**: Polls work great for community choices
    `},{slug:"utility-overview",title:"Utility Features Overview",category:"utility",excerpt:"Discover Niko's utility features including reminders, tags, and other helpful tools.",tags:["utility","reminders","tags","snipe","afk"],order:1,content:`
# Utility Features Overview

Niko includes various utility features that make everyday server use easier.

## Available Utilities

### Reminders
Set reminders for yourself or others:

\`\`\`
niko remind <time> <message>
niko reminders
niko remind remove <id>
\`\`\`

Time formats:
- \`10m\` - 10 minutes
- \`1h\` - 1 hour
- \`1d\` - 1 day
- \`1w\` - 1 week

### Tags
Create custom tags for quick responses:

\`\`\`
niko tag create <name> <content>
niko tag <name>
niko tag list
niko tag delete <name>
\`\`\`

Tags are great for frequently used information.

### AFK
Set yourself as AFK:

\`\`\`
niko afk <reason>
\`\`\`

When mentioned while AFK, Niko will let people know.

### Snipe
View recently deleted messages:

\`\`\`
niko snipe
niko snipe <channel>
\`\`\`

### Define
Look up word definitions:

\`\`\`
niko define <word>
\`\`\`

### Translate
Translate text between languages:

\`\`\`
niko translate <language> <text>
\`\`\`

## Utility Commands

| Command | Description |
|---------|-------------|
| \`remind\` | Set a reminder |
| \`reminders\` | View your reminders |
| \`tag create\` | Create a tag |
| \`tag\` | Use a tag |
| \`tag list\` | List all tags |
| \`afk\` | Set AFK status |
| \`snipe\` | View deleted messages |
| \`define\` | Look up a definition |
| \`translate\` | Translate text |

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
niko remind <time> <message>
\`\`\`

Examples:
\`\`\`
niko remind 1h Check the server
niko remind 30m Meeting starts
niko remind 1d Birthday tomorrow!
niko remind 1w Project deadline
\`\`\`

### Reminder for Someone Else
\`\`\`
niko remind <user> <time> <message>
\`\`\`

## Viewing Reminders

### Your Reminders
\`\`\`
niko reminders
\`\`\`

Shows all your active reminders with:
- Reminder ID
- Time remaining
- Message content

### Delete a Reminder
\`\`\`
niko remind remove <id>
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
2. Niko checks for due reminders every minute
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
| \`remind\` | Set a reminder |
| \`reminders\` | View your reminders |
| \`remind remove\` | Delete a reminder |
| \`remind clear\` | Clear all reminders |
    `},{slug:"utility-tags",title:"Tags System Guide",category:"utility",excerpt:"Create and manage custom tags for quick access to frequently used information.",tags:["tags","utility","customization"],order:3,content:`
# Tags System Guide

Tags let you create custom short commands that expand to longer messages or information.

## What are Tags?

Tags are custom commands you can create for your server. When someone uses a tag, Niko responds with the tag's content.

## Creating Tags

### Basic Tag
\`\`\`
niko tag create <name> <content>
\`\`\`

Example:
\`\`\`
niko tag create rules Welcome to the server! Please read the rules in #rules-channel.
\`\`\`

### Tag with Embed
Tags can include formatting and even embeds for richer responses.

## Using Tags

### Call a Tag
\`\`\`
niko tag <name>
\`\`\`

Example:
\`\`\`
niko tag rules
\`\`\`

### List All Tags
\`\`\`
niko tag list
\`\`\`

### Search Tags
\`\`\`
niko tag search <term>
\`\`\`

## Managing Tags

### Edit a Tag
\`\`\`
niko tag edit <name> <new content>
\`\`\`

### Delete a Tag
\`\`\`
niko tag delete <name>
\`\`\`

### Transfer Tag Ownership
\`\`\`
niko tag transfer <name> <user>
\`\`\`

## Tag Permissions

### Who Can Create Tags
By default, anyone can create tags. Configure with:

\`\`\`
niko tag permissions
\`\`\`

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
\`\`\`
niko play <song name or URL>
\`\`\`

Supports:
- YouTube videos
-Spotify links (when available)
- Direct URLs
- Search queries

### Music Controls
- \`pause\` - Pause playback
- \`resume\` - Resume playback
- \`stop\` - Stop playback
- \`skip\` - Skip to next song
- \`queue\` - View play queue
- \`nowplaying\` - See current song

### Playlist Features
- Save playlists
- Load saved playlists
- Shuffle playback
- Repeat modes

## Voice Channel Management

### Join Voice
\`\`\`
niko join
\`\`\`

### Leave Voice
\`\`\`
niko leave
\`\`\`

### Voice Settings
Configure default voice settings:
- Volume
- Bitrate
- Region

## Permissions

Niko needs these permissions for voice:
- Connect to voice channels
- Speak in voice channels
- Use voice activity (if needed)

## Tips

1. **Set up voice channels**: Dedicated music channels work best
2. **Configure volume**: Set appropriate default volume
3. **Use playlists**: Create playlists for recurring events
4. **Moderate voice**: Use voice moderation features if available
    `},{slug:"ai-overview",title:"AI Features Overview",category:"ai",excerpt:"Explore Niko's AI-powered features for chat and moderation assistance.",tags:["ai","artificial intelligence","chat"],order:1,content:`
# AI Features Overview

Niko integrates AI capabilities to enhance moderation and provide interactive experiences.

## Available AI Features

### AI Chat
Members can interact with Niko's AI for conversations:

\`\`\`
niko chat <message>
\`\`\`

The AI responds based on configured personalities and context.

### AI Moderation Assistance
AI can help with:
- Suggesting moderation actions
- Analyzing message content
- Providing context for decisions

### AI Configuration
Configure AI behavior through:
- Personality settings
- Enabled/disabled per server
- Response templates

## Configuration

### Enable AI
\`\`\`
niko ai toggle
\`\`\`

### Set Personality
Choose or customize AI personality:

\`\`\`
niko ai personality <personality>
\`\`\`

### AI Settings
Adjust AI behavior:
- Response length
- Formality level
- Specific knowledge areas

## Privacy

AI features process message content to generate responses. Be aware that:
- Messages may be sent to AI providers
- Check your privacy settings and member expectations
- You can disable AI features if preferred

## AI Commands

| Command | Description |
|---------|-------------|
| \`ai chat\` | Chat with AI |
| \`ai toggle\` | Enable/disable AI |
| \`ai personality\` | Set AI personality |
| \`ai config\` | View AI configuration |

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
niko onboarding setup
\`\`\`

Configure a welcome channel and message for new members.

### Step 4: Configure Logging
\`\`\`
niko logging status
\`\`\`

Set up log channels for moderation events.

### Step 5: Test Commands
Try a few commands to make sure everything works:
- \`niko help\` - See available commands
- \`niko balance\` - Check economy
- \`niko leaderboard\` - See leaderboards

## Next Steps

### Enable Features
Turn on features you want:
\`\`\`
niko leveling toggle
niko economy toggle
niko automod toggle
\`\`\`

### Configure Moderation
Set up AutoMod to reduce your workload:
\`\`\`
niko automod antispam toggle
niko automod antilink toggle
\`\`\`

### Invite Members
Let your community know Niko is available and show them useful commands.

## Essential Commands to Know

### For Members
- \`balance\` / \`wallet\` - Check money
- \`daily\` - Daily reward
- \`work\` - Earn money
- \`leaderboard\` - See rankings
- \`help\` - Get help

### For Moderators
- \`warn\` - Warn a member
- \`mute\` / \`unmute\` - Mute management
- \`kick\` / \`ban\` - Removal commands
- \`automod\` - AutoMod settings

### For Administrators
- \`logging\` - Configure logs
- \`onboarding\` - Welcome setup
- \`leveling\` - Level settings
- \`economy\` - Economy settings

## Troubleshooting Quick Fixes

### Bot Not Responding
1. Check bot permissions
2. Check bot role position
3. Try \`niko ping\` to test

### Commands Not Working
1. Check prefix settings
2. Verify user permissions
3. Check if feature is enabled

### Economy Issues
1. Check if economy is enabled
2. Verify database is working
3. Check user has required permissions

## Getting Help

- Use \`niko help\` for command references
- Browse this documentation for guides
- Visit the dashboard for visual configuration
- Join support server for assistance
    `}];function Xh(l){return Te.find(c=>c.slug===l)}const rt=[{id:"getting-started",label:"Getting Started",description:"New to Niko? Start here.",icon:"icon_home",count:Te.filter(l=>l.category==="getting-started").length},{id:"setup",label:"Setup",description:"Configure Niko for your server.",icon:"icon_settings",count:Te.filter(l=>l.category==="setup").length},{id:"economy",label:"Economy",description:"Money, jobs, banking, and more.",icon:"icon_economy",count:Te.filter(l=>l.category==="economy").length},{id:"leveling",label:"Leveling",description:"XP, levels, and rankings.",icon:"icon_leveling",count:Te.filter(l=>l.category==="leveling").length},{id:"moderation",label:"Moderation",description:"Moderation tools and commands.",icon:"icon_moderation",count:Te.filter(l=>l.category==="moderation").length},{id:"automod",label:"AutoMod",description:"Automated moderation features.",icon:"icon_automod",count:Te.filter(l=>l.category==="automod").length},{id:"social",label:"Social",description:"Community engagement features.",icon:"icon_heart",count:Te.filter(l=>l.category==="social").length},{id:"utility",label:"Utility",description:"Helpful tools and utilities.",icon:"icon_utility",count:Te.filter(l=>l.category==="utility").length},{id:"voice",label:"Voice",description:"Voice and music features.",icon:"icon_bot",count:Te.filter(l=>l.category==="voice").length},{id:"ai",label:"AI",description:"AI-powered features.",icon:"icon_ai",count:Te.filter(l=>l.category==="ai").length},{id:"dashboard",label:"Dashboard",description:"Web dashboard guides.",icon:"icon_settings",count:Te.filter(l=>l.category==="dashboard").length},{id:"tips",label:"Tips",description:"Tips and best practices.",icon:"icon_lightbulb",count:Te.filter(l=>l.category==="tips").length}];function Ac(){const[l,c]=D.useState({query:"",category:"",tags:[]}),u=D.useCallback(w=>{c(O=>({...O,query:w.toLowerCase(),tags:[]}))},[]),p=D.useCallback(w=>{c(O=>({...O,category:w,tags:[]}))},[]),y=D.useCallback(w=>{c(O=>{const L=O.tags.includes(w)?O.tags.filter(I=>I!==w):[...O.tags,w];return{...O,tags:L,query:""}})},[]),E=D.useCallback(()=>{c({query:"",category:"",tags:[]})},[]),S=D.useMemo(()=>{const{query:w,category:O,tags:L}=l;if(!w&&!O&&L.length===0)return Te.map(R=>({page:R,score:1,highlights:[]}));const I=[];for(const R of Te)if(!(O&&R.category!==O)&&!(L.length>0&&!L.some(G=>R.tags.includes(G))))if(w){const G=qh(R,w);if(G===0)continue;const k=Yh(R,w);I.push({page:R,score:G,highlights:k})}else I.push({page:R,score:1,highlights:[]});return I.sort((R,G)=>G.score!==R.score?G.score-R.score:R.page.order-G.page.order),I},[l]),F=l.query!==""||l.category!==""||l.tags.length>0;return{filters:l,setQuery:u,setCategory:p,toggleTag:y,clearFilters:E,results:S,hasActiveFilters:F,resultCount:S.length}}function qh(l,c){let u=0;const p=c.toLowerCase();l.title.toLowerCase()===p?u+=100:l.title.toLowerCase().includes(p)&&(u+=50),l.excerpt.toLowerCase().includes(p)&&(u+=25),l.content.toLowerCase().includes(p)&&(u+=10);for(const y of l.tags)y.toLowerCase().includes(p)&&(u+=15);return l.category.toLowerCase().includes(p)&&(u+=5),u}function Yh(l,c){const u=[],p=c.toLowerCase(),y=3;if(l.title.toLowerCase().includes(p)&&(u.push(l.title),u.length>=y)||l.excerpt.toLowerCase().includes(p)&&(u.push(l.excerpt),u.length>=y))return u;const E=l.content.split(`
`).filter(S=>S.trim());for(const S of E)if(S.toLowerCase().includes(p)){const F=S.replace(/#{1,6}\s?/g,"").trim();if(F.length>10&&(u.push(F),u.length>=y))break}return u}function Jh(){return D.useMemo(()=>{const c={};return Te.forEach(u=>{u.tags.forEach(p=>{c[p]=(c[p]||0)+1})}),Object.entries(c).map(([u,p])=>({tag:u,count:p})).sort((u,p)=>p.count-u.count)},[])}function Zh({slug:l}){var S,F;const{setCategory:c,clearFilters:u}=Ac();D.useEffect(()=>{window.location.hash!==`#/docs/${l}`&&window.history.replaceState(null,"",`#/docs/${l}`)},[l]);const p=Xh(l);if(!p)return s.jsxs(s.Fragment,{children:[s.jsx(st,{page:"docs"}),s.jsx("main",{className:"shell page-main docs-page",children:s.jsxs("div",{className:"docs-not-found",children:[s.jsx(Y,{name:"doc",size:48,className:"not-found-icon"}),s.jsx("h1",{children:"Page Not Found"}),s.jsxs("p",{children:[`We couldn't find documentation for "`,l,'".']}),s.jsxs("div",{className:"not-found-actions",children:[s.jsx("button",{onClick:()=>fe("/docs"),children:"Browse all documentation"}),s.jsx("button",{onClick:()=>{fe("/docs"),u()},children:"Clear filters"})]})]})}),s.jsx(Qt,{})]});const E=(w=>{const O=w.split(`
`),L=[];let I=[];const R=()=>{I.length>0&&(L.push(s.jsx("ul",{className:"doc-content-list",children:I.map((G,k)=>s.jsx("li",{children:G},k))},`list-${L.length}`)),I=[])};return O.forEach((G,k)=>{const P=G.trim();if(!P){R(),L.push(s.jsx("div",{className:"doc-content-spacer"},k));return}if(P.startsWith("# ")){R(),L.push(s.jsx("h2",{className:"doc-heading doc-heading-h2",children:P.slice(2)},k));return}if(P.startsWith("## ")){R(),L.push(s.jsx("h3",{className:"doc-heading doc-heading-h3",children:P.slice(3)},k));return}if(P.startsWith("### ")){R(),L.push(s.jsx("h4",{className:"doc-heading doc-heading-h4",children:P.slice(4)},k));return}if(P.startsWith("> ")){R(),L.push(s.jsx("blockquote",{className:"doc-blockquote",children:P.slice(2)},k));return}if(P.startsWith("```")){R();const j=[];let H=k+1;for(;H<O.length&&O[H].trim()!=="```";)j.push(O[H]),H++;L.push(s.jsx("pre",{className:"doc-code-block",children:s.jsx("code",{children:j.join(`
`)})},k));return}if(P.startsWith("`")&&P.endsWith("`")&&P.length>2){R(),L.push(s.jsx("code",{className:"doc-inline-code",children:P.slice(1,-1)},k));return}if(P.startsWith("- ")||P.startsWith("* ")){I.push(P.slice(2));return}if(/^\d+\.\s/.test(P)){I.push(P.replace(/^\d+\.\s/,""));return}R(),L.push(s.jsx("p",{className:"doc-paragraph",children:P},k))}),R(),L})(p.content);return s.jsxs(s.Fragment,{children:[s.jsx(st,{page:"docs"}),s.jsxs("main",{className:"shell page-main docs-page docs-detail-page",children:[s.jsx("div",{className:"docs-detail-back",children:s.jsxs("button",{onClick:()=>fe("/docs"),className:"back-button",children:[s.jsx(Y,{name:"arrow",size:16}),"Back to Documentation"]})}),s.jsxs("header",{className:"doc-article-header",children:[s.jsxs("div",{className:"doc-article-meta",children:[s.jsx("span",{className:"doc-category-badge",children:((S=rt.find(w=>w.id===p.category))==null?void 0:S.label)||p.category}),s.jsxs("span",{className:"doc-order-badge",children:["Article #",p.order]})]}),s.jsx("h1",{className:"doc-article-title",children:p.title}),s.jsx("p",{className:"doc-article-excerpt",children:p.excerpt}),s.jsx("div",{className:"doc-article-tags",children:p.tags.map(w=>s.jsxs("span",{className:"doc-tag-pill",children:["#",w]},w))})]}),s.jsx("article",{className:"doc-article-content",children:E}),s.jsx("footer",{className:"doc-article-footer",children:s.jsx("div",{className:"doc-nav-container",children:s.jsxs("div",{className:"doc-nav-col",children:[s.jsx("span",{className:"doc-nav-label",children:"Category"}),s.jsxs("button",{className:"doc-nav-link",onClick:()=>{c(p.category),fe("/docs")},children:[s.jsx(Y,{name:"arrow",size:14}),"View all ",(F=rt.find(w=>w.id===p.category))==null?void 0:F.label]})]})})}),E.filter(w=>w.type==="h2"||w.type==="h3").length>0&&s.jsxs("aside",{className:"doc-toc",children:[s.jsxs("div",{className:"toc-title",children:[s.jsx(Y,{name:"utility",size:16}),s.jsx("span",{children:"On this page"})]}),s.jsx("nav",{className:"toc-nav",children:E.filter(w=>w.type==="h2"||w.type==="h3").map((w,O)=>{var I;const L=(I=w.props.className)==null?void 0:I.includes("doc-heading-h2");return s.jsx("a",{href:`#${L?"h2-":"h3-"}-${O}`,className:`toc-link ${L?"toc-h2":"toc-h3"}`,children:w.props.children},O)})})]})]}),s.jsx(Qt,{})]})}function ef(){var pe,be;const[l,c]=D.useState(!1),[u,p]=D.useState(""),[y,E]=D.useState(!1),{filters:S,setQuery:F,setCategory:w,toggleTag:O,clearFilters:L,results:I,hasActiveFilters:R,resultCount:G}=Ac(),k=Jh();D.useEffect(()=>{const M=()=>{const J=window.location.hash.slice(1);if(J.startsWith("#/docs/")){const de=J.replace("#/docs/",""),Ee=Te.find(dn=>dn.slug===de);Ee&&(p(Ee.category),w(Ee.category))}};return M(),window.addEventListener("hashchange",M),()=>window.removeEventListener("hashchange",M)},[]);const P=()=>{E(!0)},j=M=>{p(M),w(M),c(!1)},H=()=>{S.query||E(!1)},le=M=>{fe(`/docs/${M}`),F(""),E(!1)},je=D.useMemo(()=>{const M={};return I.forEach(J=>{const de=J.page.category;M[de]||(M[de]=[]),M[de].push(J)}),M},[I]);return s.jsxs(s.Fragment,{children:[s.jsx(st,{page:"docs"}),s.jsxs("main",{className:"shell page-main docs-page",children:[s.jsx("div",{className:"docs-hero",children:s.jsxs("div",{className:"docs-hero-content",children:[s.jsx("div",{className:"eyebrow docs-eyebrow",children:"Documentation Center"}),s.jsxs("h1",{className:"docs-title",children:["Everything you need to know about",s.jsx("br",{}),s.jsx("span",{className:"title-accent",children:"using Niko"})]}),s.jsx("p",{className:"docs-subtitle",children:"Comprehensive guides, command references, and tips to help you get the most out of your server bot."})]})}),s.jsx("div",{className:`docs-search-section ${y?"active":""}`,children:s.jsxs("div",{className:"docs-search-container",children:[s.jsx(Kh,{value:S.query,onChange:F,placeholder:"Search documentation, commands, guides...",onFocus:P,onBlur:H}),y&&S.query&&I.length>0&&s.jsxs("div",{className:"search-results-dropdown",children:[s.jsxs("div",{className:"search-results-header",children:[s.jsxs("span",{className:"results-count",children:[G," ",G===1?"result":"results"]}),s.jsx("button",{className:"clear-search-btn",onClick:()=>{F(""),L(),p("")},children:"Clear"})]}),s.jsx("div",{className:"search-results-list",children:I.slice(0,8).map((M,J)=>s.jsxs("button",{className:"search-result-item",onClick:()=>le(M.page.slug),onMouseEnter:()=>{},children:[s.jsx("div",{className:"result-icon",children:s.jsx(Y,{name:"doc",size:18})}),s.jsxs("div",{className:"result-content",children:[s.jsx("div",{className:"result-title",children:M.page.title}),s.jsx("div",{className:"result-excerpt",children:M.page.excerpt}),M.highlights.length>0&&s.jsxs("div",{className:"result-highlight",children:[M.highlights[0].slice(0,100),"..."]})]}),s.jsx(Y,{name:"arrow",size:14,className:"result-arrow"})]},M.page.slug))}),I.length>8&&s.jsx("div",{className:"search-results-footer",children:s.jsxs("span",{children:["Showing 8 of ",I.length," results. Browse all docs below."]})})]})]})}),s.jsxs("div",{className:"docs-mobile-nav",children:[s.jsx("button",{className:"mobile-menu-toggle",onClick:()=>c(!l),"aria-label":"Toggle documentation menu",children:s.jsx(Y,{name:"utility",size:20})}),l&&s.jsxs("div",{className:"mobile-nav-panel",children:[s.jsxs("div",{className:"mobile-nav-header",children:[s.jsx("h3",{children:"Documentation"}),s.jsx("button",{className:"close-menu-btn",onClick:()=>c(!1),"aria-label":"Close menu",children:s.jsx(Y,{name:"utility",size:16,className:"rotated"})})]}),s.jsx("div",{className:"mobile-nav-sections",children:rt.map(M=>s.jsxs("button",{className:`mobile-nav-item ${u===M.id?"active":""}`,onClick:()=>{j(M.id)},children:[s.jsx(Y,{name:M.icon,size:18}),s.jsx("span",{className:"mobile-section-label",children:M.label}),s.jsx("span",{className:"mobile-section-count",children:M.count})]},M.id))})]})]}),k.length>0&&!R&&s.jsxs("div",{className:"docs-tags-cloud",children:[s.jsxs("div",{className:"tags-cloud-title",children:[s.jsx(Y,{name:"utility",size:16}),s.jsx("span",{children:"Popular Topics"})]}),s.jsx("div",{className:"tags-cloud-list",children:k.slice(0,15).map(({tag:M,count:J})=>s.jsxs("button",{className:"tag-cloud-item",onClick:()=>O(M),style:{fontSize:`${.75+Math.min(J/4,1)}rem`},children:["#",M,s.jsx("span",{className:"tag-count",children:J})]},M))})]}),s.jsx("div",{className:"docs-category-filters",children:s.jsx(Gh,{selectedCategory:S.category,onSelectCategory:j,sections:rt})}),R&&s.jsxs("div",{className:"docs-results-header",children:[s.jsxs("div",{className:"results-info",children:[s.jsxs("span",{className:"results-count-large",children:[G," ",G===1?"article":"articles"]}),S.query&&s.jsxs("span",{className:"search-query-display",children:['for "',s.jsx("strong",{children:S.query}),'"']})]}),s.jsxs("button",{className:"clear-all-btn",onClick:()=>{L(),p("")},disabled:!R,children:[s.jsx(Y,{name:"utility",size:14}),"Clear all filters"]})]}),s.jsx("div",{className:"docs-content",children:R?s.jsx("div",{className:"search-results-view",children:Object.entries(je).map(([M,J])=>{var de;return s.jsxs("section",{className:"results-category",children:[s.jsx("h2",{className:"category-title",children:((de=rt.find(Ee=>Ee.id===M))==null?void 0:de.label)||M}),s.jsx("div",{className:"category-results-grid",children:J.map(Ee=>s.jsx(ra,{doc:Ee,variant:"highlighted"},Ee.page.slug))})]},M)})}):u?s.jsxs("div",{className:"category-view",children:[s.jsxs("div",{className:"category-header",children:[s.jsx("h2",{className:"category-page-title",children:((pe=rt.find(M=>M.id===u))==null?void 0:pe.label)||u}),s.jsx("p",{className:"category-description",children:(be=rt.find(M=>M.id===u))==null?void 0:be.description})]}),s.jsx("div",{className:"category-articles",children:Te.filter(M=>M.category===u).sort((M,J)=>M.order-J.order).map(M=>s.jsx(ra,{doc:M},M.slug))})]}):s.jsx("div",{className:"all-categories-view",children:rt.map(M=>s.jsxs("section",{className:"docs-section",id:`section-${M.id}`,children:[s.jsxs("div",{className:"section-header",children:[s.jsx("div",{className:"section-icon",children:s.jsx(Y,{name:M.icon,size:28})}),s.jsxs("div",{className:"section-info",children:[s.jsx("h2",{className:"section-title",children:M.label}),s.jsx("p",{className:"section-description",children:M.description})]}),s.jsx("span",{className:"section-count",children:M.count})]}),s.jsx("div",{className:"section-articles",children:Te.filter(J=>J.category===M.id).sort((J,de)=>J.order-de.order).map(J=>s.jsx(ra,{doc:J},J.slug))})]},M.id))})}),s.jsxs("div",{className:"docs-footer-note",children:[s.jsx(Y,{name:"book",size:20}),s.jsxs("div",{children:[s.jsx("strong",{children:"Want more detail?"}),s.jsxs("p",{children:["The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in the"," ",s.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"docs/"})," ","folder."]})]})]})]}),s.jsx(Qt,{})]})}function nf(){const l=Js(),[c,u]=D.useState(null);D.useEffect(()=>{Ec().then(u).catch(()=>{})},[]);const p=[["spark","AI that remembers","Thoughtful conversation with a cozy personality and controls that respect your community."],["chart","A living economy","Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],["shield","Confident moderation","Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],["users","Community rituals","Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."]];return s.jsxs(s.Fragment,{children:[s.jsx(st,{page:"home"}),s.jsxs("main",{children:[s.jsxs("section",{className:"hero shell",children:[s.jsxs("div",{className:"hero-copy",children:[s.jsxs("div",{className:"eyebrow",children:[s.jsx("span",{className:"status-dot"})," Discord companion · online"]}),s.jsxs("h1",{children:["Useful tools for a ",s.jsx("em",{children:"better server."})]}),s.jsx("p",{children:"Niko handles the everyday work of running a Discord community, so your moderators can focus on the people in it."}),s.jsxs("div",{className:"hero-buttons",children:[s.jsxs("a",{className:"button button-primary",href:(l==null?void 0:l.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Invite Niko ",s.jsx(Y,{name:"arrow"})]}),s.jsx("a",{className:"button button-muted",href:"/commands",onClick:y=>{y.preventDefault(),fe("/commands")},children:"Explore commands"})]}),s.jsxs("div",{className:"stats-strip",children:[s.jsxs("div",{children:[s.jsx("strong",{children:_e(c==null?void 0:c.guild_count)}),s.jsx("span",{children:"servers"})]}),s.jsxs("div",{children:[s.jsx("strong",{children:_e(c==null?void 0:c.user_count)}),s.jsx("span",{children:"members"})]}),s.jsxs("div",{children:[s.jsx("strong",{children:_e(c==null?void 0:c.command_count)}),s.jsx("span",{children:"commands"})]})]})]}),s.jsx("div",{className:"hero-art","aria-label":"A preview of Niko's server workspace",children:s.jsxs("div",{className:"workspace-preview",children:[s.jsxs("div",{className:"workspace-preview-top",children:[s.jsxs("span",{className:"preview-dots",children:[s.jsx("i",{}),s.jsx("i",{}),s.jsx("i",{})]}),s.jsx("span",{children:"server workspace"}),s.jsxs("span",{className:"preview-status",children:[s.jsx("span",{className:"status-dot"})," live"]})]}),s.jsxs("div",{className:"preview-body",children:[s.jsxs("div",{className:"preview-sidebar",children:[s.jsx("span",{className:"preview-label",children:"NIKO"}),s.jsx("b",{children:"Overview"}),s.jsx("span",{children:"Economy"}),s.jsx("span",{children:"Leveling"}),s.jsx("span",{children:"Moderation"}),s.jsx("span",{children:"AI controls"})]}),s.jsxs("div",{className:"preview-main",children:[s.jsx("span",{className:"preview-label",children:"SERVER SNAPSHOT"}),s.jsx("strong",{children:"Everything in one place."}),s.jsxs("div",{className:"preview-stats",children:[s.jsxs("span",{children:[s.jsx("b",{children:_e(c==null?void 0:c.user_count)}),s.jsx("small",{children:"members"})]}),s.jsxs("span",{children:[s.jsx("b",{children:_e(c==null?void 0:c.command_count)}),s.jsx("small",{children:"commands"})]})]}),s.jsxs("div",{className:"preview-line",children:[s.jsx("i",{}),s.jsx("i",{}),s.jsx("i",{})]})]})]})]})})]}),s.jsxs("section",{className:"shell intro-section",children:[s.jsx("div",{className:"section-kicker",children:"Why Niko"}),s.jsxs("div",{className:"intro-grid",children:[s.jsxs("h2",{children:["The good kind of",s.jsx("br",{}),s.jsx("em",{children:"always-on."})]}),s.jsx("p",{children:"Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile."})]})]}),s.jsx("section",{className:"shell feature-grid",children:p.map(([y,E,S])=>s.jsxs("article",{className:"feature-card",children:[s.jsx("span",{className:"feature-icon",children:s.jsx(Y,{name:y})}),s.jsx("h3",{children:E}),s.jsx("p",{children:S}),s.jsxs("a",{href:"/docs",onClick:F=>{F.preventDefault(),fe("/docs")},children:["Learn more ",s.jsx(Y,{name:"arrow"})]})]},E))}),s.jsxs("section",{className:"shell callout",children:[s.jsxs("div",{children:[s.jsx("div",{className:"section-kicker",children:"Ready when you are"}),s.jsxs("h2",{children:["A calmer, cleverer home",s.jsx("br",{}),"for your community."]})]}),s.jsxs("a",{className:"button button-primary",href:(l==null?void 0:l.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Bring Niko in ",s.jsx(Y,{name:"arrow"})]})]})]}),s.jsx(Qt,{})]})}const tf={privacy:{title:"Privacy policy",intro:"Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",sections:[["Information we use","User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature."],["How it is used","Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],["Storage and retention","Data is stored by the server hosting Niko in local JSON and SQLite files. Economy, leveling, and configuration data remain until removed. AI conversation history is limited and can be cleared with /clearhistory."],["Third-party services","When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Music and external lookup features may contact their respective services."],["Your choices","Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."]]},terms:{title:"Terms of service",intro:"By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",sections:[["Permitted use","Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],["Availability","Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],["Moderation","The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],["AI content","AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],["Virtual items","In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],["Contact","Questions or concerns can be sent through the Niko support server."]]}};function bc({type:l}){const c=tf[l];return s.jsxs(s.Fragment,{children:[s.jsx(st,{page:l}),s.jsxs("main",{className:"shell page-main legal-page",children:[s.jsxs("div",{className:"page-heading",children:[s.jsx("div",{className:"eyebrow",children:"Niko legal"}),s.jsx("h1",{children:c.title}),s.jsx("p",{children:c.intro}),s.jsx("small",{children:"Effective date: 1 January 2025"})]}),s.jsx("div",{className:"legal-copy",children:c.sections.map(([u,p])=>s.jsxs("section",{children:[s.jsx("h2",{children:u}),s.jsx("p",{children:p})]},u))})]}),s.jsx(Qt,{})]})}function rf(){const[l,c]=D.useState(vc);if(D.useEffect(()=>{const u=()=>c(vc());return window.addEventListener("popstate",u),()=>window.removeEventListener("popstate",u)},[]),l==="commands")return s.jsx(Eh,{});if(l==="docs-detail"){const u=window.location.pathname.split("/"),p=u[u.length-1];return s.jsx(Zh,{slug:p})}return l==="docs"?s.jsx(ef,{}):l==="dashboard"?s.jsx(Qh,{}):l==="privacy"?s.jsx(bc,{type:"privacy"}):l==="terms"?s.jsx(bc,{type:"terms"}):s.jsx(nf,{})}Wm.createRoot(document.getElementById("root")).render(s.jsx(D.StrictMode,{children:s.jsx(rf,{})}));
