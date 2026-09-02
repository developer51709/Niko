var bm=Object.defineProperty;var Pm=(l,c,u)=>c in l?bm(l,c,{enumerable:!0,configurable:!0,writable:!0,value:u}):l[c]=u;var rc=(l,c,u)=>Pm(l,typeof c!="symbol"?c+"":c,u);(function(){const c=document.createElement("link").relList;if(c&&c.supports&&c.supports("modulepreload"))return;for(const k of document.querySelectorAll('link[rel="modulepreload"]'))g(k);new MutationObserver(k=>{for(const P of k)if(P.type==="childList")for(const M of P.addedNodes)M.tagName==="LINK"&&M.rel==="modulepreload"&&g(M)}).observe(document,{childList:!0,subtree:!0});function u(k){const P={};return k.integrity&&(P.integrity=k.integrity),k.referrerPolicy&&(P.referrerPolicy=k.referrerPolicy),k.crossOrigin==="use-credentials"?P.credentials="include":k.crossOrigin==="anonymous"?P.credentials="omit":P.credentials="same-origin",P}function g(k){if(k.ep)return;k.ep=!0;const P=u(k);fetch(k.href,P)}})();var Vo={exports:{}},Mr={},$o={exports:{}},ee={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var sc;function Mm(){if(sc)return ee;sc=1;var l=Symbol.for("react.element"),c=Symbol.for("react.portal"),u=Symbol.for("react.fragment"),g=Symbol.for("react.strict_mode"),k=Symbol.for("react.profiler"),P=Symbol.for("react.provider"),M=Symbol.for("react.context"),U=Symbol.for("react.forward_ref"),x=Symbol.for("react.suspense"),z=Symbol.for("react.memo"),b=Symbol.for("react.lazy"),A=Symbol.iterator;function L(h){return h===null||typeof h!="object"?null:(h=A&&h[A]||h["@@iterator"],typeof h=="function"?h:null)}var K={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},w=Object.assign,T={};function $(h,S,Z){this.props=h,this.context=S,this.refs=T,this.updater=Z||K}$.prototype.isReactComponent={},$.prototype.setState=function(h,S){if(typeof h!="object"&&typeof h!="function"&&h!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,h,S,"setState")},$.prototype.forceUpdate=function(h){this.updater.enqueueForceUpdate(this,h,"forceUpdate")};function q(){}q.prototype=$.prototype;function me(h,S,Z){this.props=h,this.context=S,this.refs=T,this.updater=Z||K}var ue=me.prototype=new q;ue.constructor=me,w(ue,$.prototype),ue.isPureReactComponent=!0;var le=Array.isArray,Ne=Object.prototype.hasOwnProperty,_={current:null},J={key:!0,ref:!0,__self:!0,__source:!0};function fe(h,S,Z){var te,re={},se=null,ce=null;if(S!=null)for(te in S.ref!==void 0&&(ce=S.ref),S.key!==void 0&&(se=""+S.key),S)Ne.call(S,te)&&!J.hasOwnProperty(te)&&(re[te]=S[te]);var oe=arguments.length-2;if(oe===1)re.children=Z;else if(1<oe){for(var ve=Array(oe),Je=0;Je<oe;Je++)ve[Je]=arguments[Je+2];re.children=ve}if(h&&h.defaultProps)for(te in oe=h.defaultProps,oe)re[te]===void 0&&(re[te]=oe[te]);return{$$typeof:l,type:h,key:se,ref:ce,props:re,_owner:_.current}}function be(h,S){return{$$typeof:l,type:h.type,key:S,ref:h.ref,props:h.props,_owner:h._owner}}function dt(h){return typeof h=="object"&&h!==null&&h.$$typeof===l}function rn(h){var S={"=":"=0",":":"=2"};return"$"+h.replace(/[=:]/g,function(Z){return S[Z]})}var xt=/\/+/g;function Ye(h,S){return typeof h=="object"&&h!==null&&h.key!=null?rn(""+h.key):S.toString(36)}function mt(h,S,Z,te,re){var se=typeof h;(se==="undefined"||se==="boolean")&&(h=null);var ce=!1;if(h===null)ce=!0;else switch(se){case"string":case"number":ce=!0;break;case"object":switch(h.$$typeof){case l:case c:ce=!0}}if(ce)return ce=h,re=re(ce),h=te===""?"."+Ye(ce,0):te,le(re)?(Z="",h!=null&&(Z=h.replace(xt,"$&/")+"/"),mt(re,S,Z,"",function(Je){return Je})):re!=null&&(dt(re)&&(re=be(re,Z+(!re.key||ce&&ce.key===re.key?"":(""+re.key).replace(xt,"$&/")+"/")+h)),S.push(re)),1;if(ce=0,te=te===""?".":te+":",le(h))for(var oe=0;oe<h.length;oe++){se=h[oe];var ve=te+Ye(se,oe);ce+=mt(se,S,Z,ve,re)}else if(ve=L(h),typeof ve=="function")for(h=ve.call(h),oe=0;!(se=h.next()).done;)se=se.value,ve=te+Ye(se,oe++),ce+=mt(se,S,Z,ve,re);else if(se==="object")throw S=String(h),Error("Objects are not valid as a React child (found: "+(S==="[object Object]"?"object with keys {"+Object.keys(h).join(", ")+"}":S)+"). If you meant to render a collection of children, use an array instead.");return ce}function wt(h,S,Z){if(h==null)return h;var te=[],re=0;return mt(h,te,"","",function(se){return S.call(Z,se,re++)}),te}function Ve(h){if(h._status===-1){var S=h._result;S=S(),S.then(function(Z){(h._status===0||h._status===-1)&&(h._status=1,h._result=Z)},function(Z){(h._status===0||h._status===-1)&&(h._status=2,h._result=Z)}),h._status===-1&&(h._status=0,h._result=S)}if(h._status===1)return h._result.default;throw h._result}var je={current:null},R={transition:null},G={ReactCurrentDispatcher:je,ReactCurrentBatchConfig:R,ReactCurrentOwner:_};function O(){throw Error("act(...) is not supported in production builds of React.")}return ee.Children={map:wt,forEach:function(h,S,Z){wt(h,function(){S.apply(this,arguments)},Z)},count:function(h){var S=0;return wt(h,function(){S++}),S},toArray:function(h){return wt(h,function(S){return S})||[]},only:function(h){if(!dt(h))throw Error("React.Children.only expected to receive a single React element child.");return h}},ee.Component=$,ee.Fragment=u,ee.Profiler=k,ee.PureComponent=me,ee.StrictMode=g,ee.Suspense=x,ee.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=G,ee.act=O,ee.cloneElement=function(h,S,Z){if(h==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+h+".");var te=w({},h.props),re=h.key,se=h.ref,ce=h._owner;if(S!=null){if(S.ref!==void 0&&(se=S.ref,ce=_.current),S.key!==void 0&&(re=""+S.key),h.type&&h.type.defaultProps)var oe=h.type.defaultProps;for(ve in S)Ne.call(S,ve)&&!J.hasOwnProperty(ve)&&(te[ve]=S[ve]===void 0&&oe!==void 0?oe[ve]:S[ve])}var ve=arguments.length-2;if(ve===1)te.children=Z;else if(1<ve){oe=Array(ve);for(var Je=0;Je<ve;Je++)oe[Je]=arguments[Je+2];te.children=oe}return{$$typeof:l,type:h.type,key:re,ref:se,props:te,_owner:ce}},ee.createContext=function(h){return h={$$typeof:M,_currentValue:h,_currentValue2:h,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},h.Provider={$$typeof:P,_context:h},h.Consumer=h},ee.createElement=fe,ee.createFactory=function(h){var S=fe.bind(null,h);return S.type=h,S},ee.createRef=function(){return{current:null}},ee.forwardRef=function(h){return{$$typeof:U,render:h}},ee.isValidElement=dt,ee.lazy=function(h){return{$$typeof:b,_payload:{_status:-1,_result:h},_init:Ve}},ee.memo=function(h,S){return{$$typeof:z,type:h,compare:S===void 0?null:S}},ee.startTransition=function(h){var S=R.transition;R.transition={};try{h()}finally{R.transition=S}},ee.unstable_act=O,ee.useCallback=function(h,S){return je.current.useCallback(h,S)},ee.useContext=function(h){return je.current.useContext(h)},ee.useDebugValue=function(){},ee.useDeferredValue=function(h){return je.current.useDeferredValue(h)},ee.useEffect=function(h,S){return je.current.useEffect(h,S)},ee.useId=function(){return je.current.useId()},ee.useImperativeHandle=function(h,S,Z){return je.current.useImperativeHandle(h,S,Z)},ee.useInsertionEffect=function(h,S){return je.current.useInsertionEffect(h,S)},ee.useLayoutEffect=function(h,S){return je.current.useLayoutEffect(h,S)},ee.useMemo=function(h,S){return je.current.useMemo(h,S)},ee.useReducer=function(h,S,Z){return je.current.useReducer(h,S,Z)},ee.useRef=function(h){return je.current.useRef(h)},ee.useState=function(h){return je.current.useState(h)},ee.useSyncExternalStore=function(h,S,Z){return je.current.useSyncExternalStore(h,S,Z)},ee.useTransition=function(){return je.current.useTransition()},ee.version="18.3.1",ee}var ic;function ra(){return ic||(ic=1,$o.exports=Mm()),$o.exports}/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var oc;function Tm(){if(oc)return Mr;oc=1;var l=ra(),c=Symbol.for("react.element"),u=Symbol.for("react.fragment"),g=Object.prototype.hasOwnProperty,k=l.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,P={key:!0,ref:!0,__self:!0,__source:!0};function M(U,x,z){var b,A={},L=null,K=null;z!==void 0&&(L=""+z),x.key!==void 0&&(L=""+x.key),x.ref!==void 0&&(K=x.ref);for(b in x)g.call(x,b)&&!P.hasOwnProperty(b)&&(A[b]=x[b]);if(U&&U.defaultProps)for(b in x=U.defaultProps,x)A[b]===void 0&&(A[b]=x[b]);return{$$typeof:c,type:U,key:L,ref:K,props:A,_owner:k.current}}return Mr.Fragment=u,Mr.jsx=M,Mr.jsxs=M,Mr}var ac;function Lm(){return ac||(ac=1,Vo.exports=Tm()),Vo.exports}var s=Lm(),I=ra(),$s={},Ho={exports:{}},Xe={},Qo={exports:{}},Ko={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var lc;function Rm(){return lc||(lc=1,(function(l){function c(R,G){var O=R.length;R.push(G);e:for(;0<O;){var h=O-1>>>1,S=R[h];if(0<k(S,G))R[h]=G,R[O]=S,O=h;else break e}}function u(R){return R.length===0?null:R[0]}function g(R){if(R.length===0)return null;var G=R[0],O=R.pop();if(O!==G){R[0]=O;e:for(var h=0,S=R.length,Z=S>>>1;h<Z;){var te=2*(h+1)-1,re=R[te],se=te+1,ce=R[se];if(0>k(re,O))se<S&&0>k(ce,re)?(R[h]=ce,R[se]=O,h=se):(R[h]=re,R[te]=O,h=te);else if(se<S&&0>k(ce,O))R[h]=ce,R[se]=O,h=se;else break e}}return G}function k(R,G){var O=R.sortIndex-G.sortIndex;return O!==0?O:R.id-G.id}if(typeof performance=="object"&&typeof performance.now=="function"){var P=performance;l.unstable_now=function(){return P.now()}}else{var M=Date,U=M.now();l.unstable_now=function(){return M.now()-U}}var x=[],z=[],b=1,A=null,L=3,K=!1,w=!1,T=!1,$=typeof setTimeout=="function"?setTimeout:null,q=typeof clearTimeout=="function"?clearTimeout:null,me=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function ue(R){for(var G=u(z);G!==null;){if(G.callback===null)g(z);else if(G.startTime<=R)g(z),G.sortIndex=G.expirationTime,c(x,G);else break;G=u(z)}}function le(R){if(T=!1,ue(R),!w)if(u(x)!==null)w=!0,Ve(Ne);else{var G=u(z);G!==null&&je(le,G.startTime-R)}}function Ne(R,G){w=!1,T&&(T=!1,q(fe),fe=-1),K=!0;var O=L;try{for(ue(G),A=u(x);A!==null&&(!(A.expirationTime>G)||R&&!rn());){var h=A.callback;if(typeof h=="function"){A.callback=null,L=A.priorityLevel;var S=h(A.expirationTime<=G);G=l.unstable_now(),typeof S=="function"?A.callback=S:A===u(x)&&g(x),ue(G)}else g(x);A=u(x)}if(A!==null)var Z=!0;else{var te=u(z);te!==null&&je(le,te.startTime-G),Z=!1}return Z}finally{A=null,L=O,K=!1}}var _=!1,J=null,fe=-1,be=5,dt=-1;function rn(){return!(l.unstable_now()-dt<be)}function xt(){if(J!==null){var R=l.unstable_now();dt=R;var G=!0;try{G=J(!0,R)}finally{G?Ye():(_=!1,J=null)}}else _=!1}var Ye;if(typeof me=="function")Ye=function(){me(xt)};else if(typeof MessageChannel<"u"){var mt=new MessageChannel,wt=mt.port2;mt.port1.onmessage=xt,Ye=function(){wt.postMessage(null)}}else Ye=function(){$(xt,0)};function Ve(R){J=R,_||(_=!0,Ye())}function je(R,G){fe=$(function(){R(l.unstable_now())},G)}l.unstable_IdlePriority=5,l.unstable_ImmediatePriority=1,l.unstable_LowPriority=4,l.unstable_NormalPriority=3,l.unstable_Profiling=null,l.unstable_UserBlockingPriority=2,l.unstable_cancelCallback=function(R){R.callback=null},l.unstable_continueExecution=function(){w||K||(w=!0,Ve(Ne))},l.unstable_forceFrameRate=function(R){0>R||125<R?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):be=0<R?Math.floor(1e3/R):5},l.unstable_getCurrentPriorityLevel=function(){return L},l.unstable_getFirstCallbackNode=function(){return u(x)},l.unstable_next=function(R){switch(L){case 1:case 2:case 3:var G=3;break;default:G=L}var O=L;L=G;try{return R()}finally{L=O}},l.unstable_pauseExecution=function(){},l.unstable_requestPaint=function(){},l.unstable_runWithPriority=function(R,G){switch(R){case 1:case 2:case 3:case 4:case 5:break;default:R=3}var O=L;L=R;try{return G()}finally{L=O}},l.unstable_scheduleCallback=function(R,G,O){var h=l.unstable_now();switch(typeof O=="object"&&O!==null?(O=O.delay,O=typeof O=="number"&&0<O?h+O:h):O=h,R){case 1:var S=-1;break;case 2:S=250;break;case 5:S=1073741823;break;case 4:S=1e4;break;default:S=5e3}return S=O+S,R={id:b++,callback:G,priorityLevel:R,startTime:O,expirationTime:S,sortIndex:-1},O>h?(R.sortIndex=O,c(z,R),u(x)===null&&R===u(z)&&(T?(q(fe),fe=-1):T=!0,je(le,O-h))):(R.sortIndex=S,c(x,R),w||K||(w=!0,Ve(Ne))),R},l.unstable_shouldYield=rn,l.unstable_wrapCallback=function(R){var G=L;return function(){var O=L;L=G;try{return R.apply(this,arguments)}finally{L=O}}}})(Ko)),Ko}var uc;function Dm(){return uc||(uc=1,Qo.exports=Rm()),Qo.exports}/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var cc;function Am(){if(cc)return Xe;cc=1;var l=ra(),c=Dm();function u(e){for(var t="https://reactjs.org/docs/error-decoder.html?invariant="+e,n=1;n<arguments.length;n++)t+="&args[]="+encodeURIComponent(arguments[n]);return"Minified React error #"+e+"; visit "+t+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var g=new Set,k={};function P(e,t){M(e,t),M(e+"Capture",t)}function M(e,t){for(k[e]=t,e=0;e<t.length;e++)g.add(t[e])}var U=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),x=Object.prototype.hasOwnProperty,z=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,b={},A={};function L(e){return x.call(A,e)?!0:x.call(b,e)?!1:z.test(e)?A[e]=!0:(b[e]=!0,!1)}function K(e,t,n,r){if(n!==null&&n.type===0)return!1;switch(typeof t){case"function":case"symbol":return!0;case"boolean":return r?!1:n!==null?!n.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function w(e,t,n,r){if(t===null||typeof t>"u"||K(e,t,n,r))return!0;if(r)return!1;if(n!==null)switch(n.type){case 3:return!t;case 4:return t===!1;case 5:return isNaN(t);case 6:return isNaN(t)||1>t}return!1}function T(e,t,n,r,i,o,a){this.acceptsBooleans=t===2||t===3||t===4,this.attributeName=r,this.attributeNamespace=i,this.mustUseProperty=n,this.propertyName=e,this.type=t,this.sanitizeURL=o,this.removeEmptyString=a}var $={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){$[e]=new T(e,0,!1,e,null,!1,!1)}),[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var t=e[0];$[t]=new T(t,1,!1,e[1],null,!1,!1)}),["contentEditable","draggable","spellCheck","value"].forEach(function(e){$[e]=new T(e,2,!1,e.toLowerCase(),null,!1,!1)}),["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){$[e]=new T(e,2,!1,e,null,!1,!1)}),"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){$[e]=new T(e,3,!1,e.toLowerCase(),null,!1,!1)}),["checked","multiple","muted","selected"].forEach(function(e){$[e]=new T(e,3,!0,e,null,!1,!1)}),["capture","download"].forEach(function(e){$[e]=new T(e,4,!1,e,null,!1,!1)}),["cols","rows","size","span"].forEach(function(e){$[e]=new T(e,6,!1,e,null,!1,!1)}),["rowSpan","start"].forEach(function(e){$[e]=new T(e,5,!1,e.toLowerCase(),null,!1,!1)});var q=/[\-:]([a-z])/g;function me(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var t=e.replace(q,me);$[t]=new T(t,1,!1,e,null,!1,!1)}),"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var t=e.replace(q,me);$[t]=new T(t,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)}),["xml:base","xml:lang","xml:space"].forEach(function(e){var t=e.replace(q,me);$[t]=new T(t,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)}),["tabIndex","crossOrigin"].forEach(function(e){$[e]=new T(e,1,!1,e.toLowerCase(),null,!1,!1)}),$.xlinkHref=new T("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1),["src","href","action","formAction"].forEach(function(e){$[e]=new T(e,1,!1,e.toLowerCase(),null,!0,!0)});function ue(e,t,n,r){var i=$.hasOwnProperty(t)?$[t]:null;(i!==null?i.type!==0:r||!(2<t.length)||t[0]!=="o"&&t[0]!=="O"||t[1]!=="n"&&t[1]!=="N")&&(w(t,n,i,r)&&(n=null),r||i===null?L(t)&&(n===null?e.removeAttribute(t):e.setAttribute(t,""+n)):i.mustUseProperty?e[i.propertyName]=n===null?i.type===3?!1:"":n:(t=i.attributeName,r=i.attributeNamespace,n===null?e.removeAttribute(t):(i=i.type,n=i===3||i===4&&n===!0?"":""+n,r?e.setAttributeNS(r,t,n):e.setAttribute(t,n))))}var le=l.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,Ne=Symbol.for("react.element"),_=Symbol.for("react.portal"),J=Symbol.for("react.fragment"),fe=Symbol.for("react.strict_mode"),be=Symbol.for("react.profiler"),dt=Symbol.for("react.provider"),rn=Symbol.for("react.context"),xt=Symbol.for("react.forward_ref"),Ye=Symbol.for("react.suspense"),mt=Symbol.for("react.suspense_list"),wt=Symbol.for("react.memo"),Ve=Symbol.for("react.lazy"),je=Symbol.for("react.offscreen"),R=Symbol.iterator;function G(e){return e===null||typeof e!="object"?null:(e=R&&e[R]||e["@@iterator"],typeof e=="function"?e:null)}var O=Object.assign,h;function S(e){if(h===void 0)try{throw Error()}catch(n){var t=n.stack.trim().match(/\n( *(at )?)/);h=t&&t[1]||""}return`
`+h+e}var Z=!1;function te(e,t){if(!e||Z)return"";Z=!0;var n=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(t)if(t=function(){throw Error()},Object.defineProperty(t.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(t,[])}catch(y){var r=y}Reflect.construct(e,[],t)}else{try{t.call()}catch(y){r=y}e.call(t.prototype)}else{try{throw Error()}catch(y){r=y}e()}}catch(y){if(y&&r&&typeof y.stack=="string"){for(var i=y.stack.split(`
`),o=r.stack.split(`
`),a=i.length-1,d=o.length-1;1<=a&&0<=d&&i[a]!==o[d];)d--;for(;1<=a&&0<=d;a--,d--)if(i[a]!==o[d]){if(a!==1||d!==1)do if(a--,d--,0>d||i[a]!==o[d]){var m=`
`+i[a].replace(" at new "," at ");return e.displayName&&m.includes("<anonymous>")&&(m=m.replace("<anonymous>",e.displayName)),m}while(1<=a&&0<=d);break}}}finally{Z=!1,Error.prepareStackTrace=n}return(e=e?e.displayName||e.name:"")?S(e):""}function re(e){switch(e.tag){case 5:return S(e.type);case 16:return S("Lazy");case 13:return S("Suspense");case 19:return S("SuspenseList");case 0:case 2:case 15:return e=te(e.type,!1),e;case 11:return e=te(e.type.render,!1),e;case 1:return e=te(e.type,!0),e;default:return""}}function se(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case J:return"Fragment";case _:return"Portal";case be:return"Profiler";case fe:return"StrictMode";case Ye:return"Suspense";case mt:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case rn:return(e.displayName||"Context")+".Consumer";case dt:return(e._context.displayName||"Context")+".Provider";case xt:var t=e.render;return e=e.displayName,e||(e=t.displayName||t.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case wt:return t=e.displayName||null,t!==null?t:se(e.type)||"Memo";case Ve:t=e._payload,e=e._init;try{return se(e(t))}catch{}}return null}function ce(e){var t=e.type;switch(e.tag){case 24:return"Cache";case 9:return(t.displayName||"Context")+".Consumer";case 10:return(t._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=t.render,e=e.displayName||e.name||"",t.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return t;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return se(t);case 8:return t===fe?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof t=="function")return t.displayName||t.name||null;if(typeof t=="string")return t}return null}function oe(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function ve(e){var t=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(t==="checkbox"||t==="radio")}function Je(e){var t=ve(e)?"checked":"value",n=Object.getOwnPropertyDescriptor(e.constructor.prototype,t),r=""+e[t];if(!e.hasOwnProperty(t)&&typeof n<"u"&&typeof n.get=="function"&&typeof n.set=="function"){var i=n.get,o=n.set;return Object.defineProperty(e,t,{configurable:!0,get:function(){return i.call(this)},set:function(a){r=""+a,o.call(this,a)}}),Object.defineProperty(e,t,{enumerable:n.enumerable}),{getValue:function(){return r},setValue:function(a){r=""+a},stopTracking:function(){e._valueTracker=null,delete e[t]}}}}function Dr(e){e._valueTracker||(e._valueTracker=Je(e))}function ua(e){if(!e)return!1;var t=e._valueTracker;if(!t)return!0;var n=t.getValue(),r="";return e&&(r=ve(e)?e.checked?"true":"false":e.value),e=r,e!==n?(t.setValue(e),!0):!1}function Ar(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function Xs(e,t){var n=t.checked;return O({},t,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:n??e._wrapperState.initialChecked})}function ca(e,t){var n=t.defaultValue==null?"":t.defaultValue,r=t.checked!=null?t.checked:t.defaultChecked;n=oe(t.value!=null?t.value:n),e._wrapperState={initialChecked:r,initialValue:n,controlled:t.type==="checkbox"||t.type==="radio"?t.checked!=null:t.value!=null}}function da(e,t){t=t.checked,t!=null&&ue(e,"checked",t,!1)}function qs(e,t){da(e,t);var n=oe(t.value),r=t.type;if(n!=null)r==="number"?(n===0&&e.value===""||e.value!=n)&&(e.value=""+n):e.value!==""+n&&(e.value=""+n);else if(r==="submit"||r==="reset"){e.removeAttribute("value");return}t.hasOwnProperty("value")?Ys(e,t.type,n):t.hasOwnProperty("defaultValue")&&Ys(e,t.type,oe(t.defaultValue)),t.checked==null&&t.defaultChecked!=null&&(e.defaultChecked=!!t.defaultChecked)}function ma(e,t,n){if(t.hasOwnProperty("value")||t.hasOwnProperty("defaultValue")){var r=t.type;if(!(r!=="submit"&&r!=="reset"||t.value!==void 0&&t.value!==null))return;t=""+e._wrapperState.initialValue,n||t===e.value||(e.value=t),e.defaultValue=t}n=e.name,n!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,n!==""&&(e.name=n)}function Ys(e,t,n){(t!=="number"||Ar(e.ownerDocument)!==e)&&(n==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+n&&(e.defaultValue=""+n))}var Hn=Array.isArray;function kn(e,t,n,r){if(e=e.options,t){t={};for(var i=0;i<n.length;i++)t["$"+n[i]]=!0;for(n=0;n<e.length;n++)i=t.hasOwnProperty("$"+e[n].value),e[n].selected!==i&&(e[n].selected=i),i&&r&&(e[n].defaultSelected=!0)}else{for(n=""+oe(n),t=null,i=0;i<e.length;i++){if(e[i].value===n){e[i].selected=!0,r&&(e[i].defaultSelected=!0);return}t!==null||e[i].disabled||(t=e[i])}t!==null&&(t.selected=!0)}}function Js(e,t){if(t.dangerouslySetInnerHTML!=null)throw Error(u(91));return O({},t,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function fa(e,t){var n=t.value;if(n==null){if(n=t.children,t=t.defaultValue,n!=null){if(t!=null)throw Error(u(92));if(Hn(n)){if(1<n.length)throw Error(u(93));n=n[0]}t=n}t==null&&(t=""),n=t}e._wrapperState={initialValue:oe(n)}}function ha(e,t){var n=oe(t.value),r=oe(t.defaultValue);n!=null&&(n=""+n,n!==e.value&&(e.value=n),t.defaultValue==null&&e.defaultValue!==n&&(e.defaultValue=n)),r!=null&&(e.defaultValue=""+r)}function pa(e){var t=e.textContent;t===e._wrapperState.initialValue&&t!==""&&t!==null&&(e.value=t)}function ga(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function Zs(e,t){return e==null||e==="http://www.w3.org/1999/xhtml"?ga(t):e==="http://www.w3.org/2000/svg"&&t==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var Ir,va=(function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(t,n,r,i){MSApp.execUnsafeLocalFunction(function(){return e(t,n,r,i)})}:e})(function(e,t){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=t;else{for(Ir=Ir||document.createElement("div"),Ir.innerHTML="<svg>"+t.valueOf().toString()+"</svg>",t=Ir.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;t.firstChild;)e.appendChild(t.firstChild)}});function Qn(e,t){if(t){var n=e.firstChild;if(n&&n===e.lastChild&&n.nodeType===3){n.nodeValue=t;return}}e.textContent=t}var Kn={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},Lc=["Webkit","ms","Moz","O"];Object.keys(Kn).forEach(function(e){Lc.forEach(function(t){t=t+e.charAt(0).toUpperCase()+e.substring(1),Kn[t]=Kn[e]})});function ya(e,t,n){return t==null||typeof t=="boolean"||t===""?"":n||typeof t!="number"||t===0||Kn.hasOwnProperty(e)&&Kn[e]?(""+t).trim():t+"px"}function ka(e,t){e=e.style;for(var n in t)if(t.hasOwnProperty(n)){var r=n.indexOf("--")===0,i=ya(n,t[n],r);n==="float"&&(n="cssFloat"),r?e.setProperty(n,i):e[n]=i}}var Rc=O({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function ei(e,t){if(t){if(Rc[e]&&(t.children!=null||t.dangerouslySetInnerHTML!=null))throw Error(u(137,e));if(t.dangerouslySetInnerHTML!=null){if(t.children!=null)throw Error(u(60));if(typeof t.dangerouslySetInnerHTML!="object"||!("__html"in t.dangerouslySetInnerHTML))throw Error(u(61))}if(t.style!=null&&typeof t.style!="object")throw Error(u(62))}}function ti(e,t){if(e.indexOf("-")===-1)return typeof t.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var ni=null;function ri(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var si=null,xn=null,wn=null;function xa(e){if(e=pr(e)){if(typeof si!="function")throw Error(u(280));var t=e.stateNode;t&&(t=is(t),si(e.stateNode,e.type,t))}}function wa(e){xn?wn?wn.push(e):wn=[e]:xn=e}function ja(){if(xn){var e=xn,t=wn;if(wn=xn=null,xa(e),t)for(e=0;e<t.length;e++)xa(t[e])}}function Sa(e,t){return e(t)}function Na(){}var ii=!1;function Ca(e,t,n){if(ii)return e(t,n);ii=!0;try{return Sa(e,t,n)}finally{ii=!1,(xn!==null||wn!==null)&&(Na(),ja())}}function Gn(e,t){var n=e.stateNode;if(n===null)return null;var r=is(n);if(r===null)return null;n=r[t];e:switch(t){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(r=!r.disabled)||(e=e.type,r=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!r;break e;default:e=!1}if(e)return null;if(n&&typeof n!="function")throw Error(u(231,t,typeof n));return n}var oi=!1;if(U)try{var Xn={};Object.defineProperty(Xn,"passive",{get:function(){oi=!0}}),window.addEventListener("test",Xn,Xn),window.removeEventListener("test",Xn,Xn)}catch{oi=!1}function Dc(e,t,n,r,i,o,a,d,m){var y=Array.prototype.slice.call(arguments,3);try{t.apply(n,y)}catch(N){this.onError(N)}}var qn=!1,zr=null,Fr=!1,ai=null,Ac={onError:function(e){qn=!0,zr=e}};function Ic(e,t,n,r,i,o,a,d,m){qn=!1,zr=null,Dc.apply(Ac,arguments)}function zc(e,t,n,r,i,o,a,d,m){if(Ic.apply(this,arguments),qn){if(qn){var y=zr;qn=!1,zr=null}else throw Error(u(198));Fr||(Fr=!0,ai=y)}}function sn(e){var t=e,n=e;if(e.alternate)for(;t.return;)t=t.return;else{e=t;do t=e,(t.flags&4098)!==0&&(n=t.return),e=t.return;while(e)}return t.tag===3?n:null}function _a(e){if(e.tag===13){var t=e.memoizedState;if(t===null&&(e=e.alternate,e!==null&&(t=e.memoizedState)),t!==null)return t.dehydrated}return null}function Ea(e){if(sn(e)!==e)throw Error(u(188))}function Fc(e){var t=e.alternate;if(!t){if(t=sn(e),t===null)throw Error(u(188));return t!==e?null:e}for(var n=e,r=t;;){var i=n.return;if(i===null)break;var o=i.alternate;if(o===null){if(r=i.return,r!==null){n=r;continue}break}if(i.child===o.child){for(o=i.child;o;){if(o===n)return Ea(i),e;if(o===r)return Ea(i),t;o=o.sibling}throw Error(u(188))}if(n.return!==r.return)n=i,r=o;else{for(var a=!1,d=i.child;d;){if(d===n){a=!0,n=i,r=o;break}if(d===r){a=!0,r=i,n=o;break}d=d.sibling}if(!a){for(d=o.child;d;){if(d===n){a=!0,n=o,r=i;break}if(d===r){a=!0,r=o,n=i;break}d=d.sibling}if(!a)throw Error(u(189))}}if(n.alternate!==r)throw Error(u(190))}if(n.tag!==3)throw Error(u(188));return n.stateNode.current===n?e:t}function ba(e){return e=Fc(e),e!==null?Pa(e):null}function Pa(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var t=Pa(e);if(t!==null)return t;e=e.sibling}return null}var Ma=c.unstable_scheduleCallback,Ta=c.unstable_cancelCallback,Oc=c.unstable_shouldYield,Bc=c.unstable_requestPaint,Ce=c.unstable_now,Uc=c.unstable_getCurrentPriorityLevel,li=c.unstable_ImmediatePriority,La=c.unstable_UserBlockingPriority,Or=c.unstable_NormalPriority,Wc=c.unstable_LowPriority,Ra=c.unstable_IdlePriority,Br=null,jt=null;function Vc(e){if(jt&&typeof jt.onCommitFiberRoot=="function")try{jt.onCommitFiberRoot(Br,e,void 0,(e.current.flags&128)===128)}catch{}}var ft=Math.clz32?Math.clz32:Qc,$c=Math.log,Hc=Math.LN2;function Qc(e){return e>>>=0,e===0?32:31-($c(e)/Hc|0)|0}var Ur=64,Wr=4194304;function Yn(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function Vr(e,t){var n=e.pendingLanes;if(n===0)return 0;var r=0,i=e.suspendedLanes,o=e.pingedLanes,a=n&268435455;if(a!==0){var d=a&~i;d!==0?r=Yn(d):(o&=a,o!==0&&(r=Yn(o)))}else a=n&~i,a!==0?r=Yn(a):o!==0&&(r=Yn(o));if(r===0)return 0;if(t!==0&&t!==r&&(t&i)===0&&(i=r&-r,o=t&-t,i>=o||i===16&&(o&4194240)!==0))return t;if((r&4)!==0&&(r|=n&16),t=e.entangledLanes,t!==0)for(e=e.entanglements,t&=r;0<t;)n=31-ft(t),i=1<<n,r|=e[n],t&=~i;return r}function Kc(e,t){switch(e){case 1:case 2:case 4:return t+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return t+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function Gc(e,t){for(var n=e.suspendedLanes,r=e.pingedLanes,i=e.expirationTimes,o=e.pendingLanes;0<o;){var a=31-ft(o),d=1<<a,m=i[a];m===-1?((d&n)===0||(d&r)!==0)&&(i[a]=Kc(d,t)):m<=t&&(e.expiredLanes|=d),o&=~d}}function ui(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function Da(){var e=Ur;return Ur<<=1,(Ur&4194240)===0&&(Ur=64),e}function ci(e){for(var t=[],n=0;31>n;n++)t.push(e);return t}function Jn(e,t,n){e.pendingLanes|=t,t!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,t=31-ft(t),e[t]=n}function Xc(e,t){var n=e.pendingLanes&~t;e.pendingLanes=t,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=t,e.mutableReadLanes&=t,e.entangledLanes&=t,t=e.entanglements;var r=e.eventTimes;for(e=e.expirationTimes;0<n;){var i=31-ft(n),o=1<<i;t[i]=0,r[i]=-1,e[i]=-1,n&=~o}}function di(e,t){var n=e.entangledLanes|=t;for(e=e.entanglements;n;){var r=31-ft(n),i=1<<r;i&t|e[r]&t&&(e[r]|=t),n&=~i}}var ae=0;function Aa(e){return e&=-e,1<e?4<e?(e&268435455)!==0?16:536870912:4:1}var Ia,mi,za,Fa,Oa,fi=!1,$r=[],It=null,zt=null,Ft=null,Zn=new Map,er=new Map,Ot=[],qc="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function Ba(e,t){switch(e){case"focusin":case"focusout":It=null;break;case"dragenter":case"dragleave":zt=null;break;case"mouseover":case"mouseout":Ft=null;break;case"pointerover":case"pointerout":Zn.delete(t.pointerId);break;case"gotpointercapture":case"lostpointercapture":er.delete(t.pointerId)}}function tr(e,t,n,r,i,o){return e===null||e.nativeEvent!==o?(e={blockedOn:t,domEventName:n,eventSystemFlags:r,nativeEvent:o,targetContainers:[i]},t!==null&&(t=pr(t),t!==null&&mi(t)),e):(e.eventSystemFlags|=r,t=e.targetContainers,i!==null&&t.indexOf(i)===-1&&t.push(i),e)}function Yc(e,t,n,r,i){switch(t){case"focusin":return It=tr(It,e,t,n,r,i),!0;case"dragenter":return zt=tr(zt,e,t,n,r,i),!0;case"mouseover":return Ft=tr(Ft,e,t,n,r,i),!0;case"pointerover":var o=i.pointerId;return Zn.set(o,tr(Zn.get(o)||null,e,t,n,r,i)),!0;case"gotpointercapture":return o=i.pointerId,er.set(o,tr(er.get(o)||null,e,t,n,r,i)),!0}return!1}function Ua(e){var t=on(e.target);if(t!==null){var n=sn(t);if(n!==null){if(t=n.tag,t===13){if(t=_a(n),t!==null){e.blockedOn=t,Oa(e.priority,function(){za(n)});return}}else if(t===3&&n.stateNode.current.memoizedState.isDehydrated){e.blockedOn=n.tag===3?n.stateNode.containerInfo:null;return}}}e.blockedOn=null}function Hr(e){if(e.blockedOn!==null)return!1;for(var t=e.targetContainers;0<t.length;){var n=pi(e.domEventName,e.eventSystemFlags,t[0],e.nativeEvent);if(n===null){n=e.nativeEvent;var r=new n.constructor(n.type,n);ni=r,n.target.dispatchEvent(r),ni=null}else return t=pr(n),t!==null&&mi(t),e.blockedOn=n,!1;t.shift()}return!0}function Wa(e,t,n){Hr(e)&&n.delete(t)}function Jc(){fi=!1,It!==null&&Hr(It)&&(It=null),zt!==null&&Hr(zt)&&(zt=null),Ft!==null&&Hr(Ft)&&(Ft=null),Zn.forEach(Wa),er.forEach(Wa)}function nr(e,t){e.blockedOn===t&&(e.blockedOn=null,fi||(fi=!0,c.unstable_scheduleCallback(c.unstable_NormalPriority,Jc)))}function rr(e){function t(i){return nr(i,e)}if(0<$r.length){nr($r[0],e);for(var n=1;n<$r.length;n++){var r=$r[n];r.blockedOn===e&&(r.blockedOn=null)}}for(It!==null&&nr(It,e),zt!==null&&nr(zt,e),Ft!==null&&nr(Ft,e),Zn.forEach(t),er.forEach(t),n=0;n<Ot.length;n++)r=Ot[n],r.blockedOn===e&&(r.blockedOn=null);for(;0<Ot.length&&(n=Ot[0],n.blockedOn===null);)Ua(n),n.blockedOn===null&&Ot.shift()}var jn=le.ReactCurrentBatchConfig,Qr=!0;function Zc(e,t,n,r){var i=ae,o=jn.transition;jn.transition=null;try{ae=1,hi(e,t,n,r)}finally{ae=i,jn.transition=o}}function ed(e,t,n,r){var i=ae,o=jn.transition;jn.transition=null;try{ae=4,hi(e,t,n,r)}finally{ae=i,jn.transition=o}}function hi(e,t,n,r){if(Qr){var i=pi(e,t,n,r);if(i===null)Li(e,t,r,Kr,n),Ba(e,r);else if(Yc(i,e,t,n,r))r.stopPropagation();else if(Ba(e,r),t&4&&-1<qc.indexOf(e)){for(;i!==null;){var o=pr(i);if(o!==null&&Ia(o),o=pi(e,t,n,r),o===null&&Li(e,t,r,Kr,n),o===i)break;i=o}i!==null&&r.stopPropagation()}else Li(e,t,r,null,n)}}var Kr=null;function pi(e,t,n,r){if(Kr=null,e=ri(r),e=on(e),e!==null)if(t=sn(e),t===null)e=null;else if(n=t.tag,n===13){if(e=_a(t),e!==null)return e;e=null}else if(n===3){if(t.stateNode.current.memoizedState.isDehydrated)return t.tag===3?t.stateNode.containerInfo:null;e=null}else t!==e&&(e=null);return Kr=e,null}function Va(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(Uc()){case li:return 1;case La:return 4;case Or:case Wc:return 16;case Ra:return 536870912;default:return 16}default:return 16}}var Bt=null,gi=null,Gr=null;function $a(){if(Gr)return Gr;var e,t=gi,n=t.length,r,i="value"in Bt?Bt.value:Bt.textContent,o=i.length;for(e=0;e<n&&t[e]===i[e];e++);var a=n-e;for(r=1;r<=a&&t[n-r]===i[o-r];r++);return Gr=i.slice(e,1<r?1-r:void 0)}function Xr(e){var t=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&t===13&&(e=13)):e=t,e===10&&(e=13),32<=e||e===13?e:0}function qr(){return!0}function Ha(){return!1}function Ze(e){function t(n,r,i,o,a){this._reactName=n,this._targetInst=i,this.type=r,this.nativeEvent=o,this.target=a,this.currentTarget=null;for(var d in e)e.hasOwnProperty(d)&&(n=e[d],this[d]=n?n(o):o[d]);return this.isDefaultPrevented=(o.defaultPrevented!=null?o.defaultPrevented:o.returnValue===!1)?qr:Ha,this.isPropagationStopped=Ha,this}return O(t.prototype,{preventDefault:function(){this.defaultPrevented=!0;var n=this.nativeEvent;n&&(n.preventDefault?n.preventDefault():typeof n.returnValue!="unknown"&&(n.returnValue=!1),this.isDefaultPrevented=qr)},stopPropagation:function(){var n=this.nativeEvent;n&&(n.stopPropagation?n.stopPropagation():typeof n.cancelBubble!="unknown"&&(n.cancelBubble=!0),this.isPropagationStopped=qr)},persist:function(){},isPersistent:qr}),t}var Sn={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},vi=Ze(Sn),sr=O({},Sn,{view:0,detail:0}),td=Ze(sr),yi,ki,ir,Yr=O({},sr,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:wi,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==ir&&(ir&&e.type==="mousemove"?(yi=e.screenX-ir.screenX,ki=e.screenY-ir.screenY):ki=yi=0,ir=e),yi)},movementY:function(e){return"movementY"in e?e.movementY:ki}}),Qa=Ze(Yr),nd=O({},Yr,{dataTransfer:0}),rd=Ze(nd),sd=O({},sr,{relatedTarget:0}),xi=Ze(sd),id=O({},Sn,{animationName:0,elapsedTime:0,pseudoElement:0}),od=Ze(id),ad=O({},Sn,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),ld=Ze(ad),ud=O({},Sn,{data:0}),Ka=Ze(ud),cd={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},dd={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},md={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function fd(e){var t=this.nativeEvent;return t.getModifierState?t.getModifierState(e):(e=md[e])?!!t[e]:!1}function wi(){return fd}var hd=O({},sr,{key:function(e){if(e.key){var t=cd[e.key]||e.key;if(t!=="Unidentified")return t}return e.type==="keypress"?(e=Xr(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?dd[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:wi,charCode:function(e){return e.type==="keypress"?Xr(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?Xr(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),pd=Ze(hd),gd=O({},Yr,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),Ga=Ze(gd),vd=O({},sr,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:wi}),yd=Ze(vd),kd=O({},Sn,{propertyName:0,elapsedTime:0,pseudoElement:0}),xd=Ze(kd),wd=O({},Yr,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),jd=Ze(wd),Sd=[9,13,27,32],ji=U&&"CompositionEvent"in window,or=null;U&&"documentMode"in document&&(or=document.documentMode);var Nd=U&&"TextEvent"in window&&!or,Xa=U&&(!ji||or&&8<or&&11>=or),qa=" ",Ya=!1;function Ja(e,t){switch(e){case"keyup":return Sd.indexOf(t.keyCode)!==-1;case"keydown":return t.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function Za(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var Nn=!1;function Cd(e,t){switch(e){case"compositionend":return Za(t);case"keypress":return t.which!==32?null:(Ya=!0,qa);case"textInput":return e=t.data,e===qa&&Ya?null:e;default:return null}}function _d(e,t){if(Nn)return e==="compositionend"||!ji&&Ja(e,t)?(e=$a(),Gr=gi=Bt=null,Nn=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(t.ctrlKey||t.altKey||t.metaKey)||t.ctrlKey&&t.altKey){if(t.char&&1<t.char.length)return t.char;if(t.which)return String.fromCharCode(t.which)}return null;case"compositionend":return Xa&&t.locale!=="ko"?null:t.data;default:return null}}var Ed={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function el(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t==="input"?!!Ed[e.type]:t==="textarea"}function tl(e,t,n,r){wa(r),t=ns(t,"onChange"),0<t.length&&(n=new vi("onChange","change",null,n,r),e.push({event:n,listeners:t}))}var ar=null,lr=null;function bd(e){kl(e,0)}function Jr(e){var t=Pn(e);if(ua(t))return e}function Pd(e,t){if(e==="change")return t}var nl=!1;if(U){var Si;if(U){var Ni="oninput"in document;if(!Ni){var rl=document.createElement("div");rl.setAttribute("oninput","return;"),Ni=typeof rl.oninput=="function"}Si=Ni}else Si=!1;nl=Si&&(!document.documentMode||9<document.documentMode)}function sl(){ar&&(ar.detachEvent("onpropertychange",il),lr=ar=null)}function il(e){if(e.propertyName==="value"&&Jr(lr)){var t=[];tl(t,lr,e,ri(e)),Ca(bd,t)}}function Md(e,t,n){e==="focusin"?(sl(),ar=t,lr=n,ar.attachEvent("onpropertychange",il)):e==="focusout"&&sl()}function Td(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return Jr(lr)}function Ld(e,t){if(e==="click")return Jr(t)}function Rd(e,t){if(e==="input"||e==="change")return Jr(t)}function Dd(e,t){return e===t&&(e!==0||1/e===1/t)||e!==e&&t!==t}var ht=typeof Object.is=="function"?Object.is:Dd;function ur(e,t){if(ht(e,t))return!0;if(typeof e!="object"||e===null||typeof t!="object"||t===null)return!1;var n=Object.keys(e),r=Object.keys(t);if(n.length!==r.length)return!1;for(r=0;r<n.length;r++){var i=n[r];if(!x.call(t,i)||!ht(e[i],t[i]))return!1}return!0}function ol(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function al(e,t){var n=ol(e);e=0;for(var r;n;){if(n.nodeType===3){if(r=e+n.textContent.length,e<=t&&r>=t)return{node:n,offset:t-e};e=r}e:{for(;n;){if(n.nextSibling){n=n.nextSibling;break e}n=n.parentNode}n=void 0}n=ol(n)}}function ll(e,t){return e&&t?e===t?!0:e&&e.nodeType===3?!1:t&&t.nodeType===3?ll(e,t.parentNode):"contains"in e?e.contains(t):e.compareDocumentPosition?!!(e.compareDocumentPosition(t)&16):!1:!1}function ul(){for(var e=window,t=Ar();t instanceof e.HTMLIFrameElement;){try{var n=typeof t.contentWindow.location.href=="string"}catch{n=!1}if(n)e=t.contentWindow;else break;t=Ar(e.document)}return t}function Ci(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t&&(t==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||t==="textarea"||e.contentEditable==="true")}function Ad(e){var t=ul(),n=e.focusedElem,r=e.selectionRange;if(t!==n&&n&&n.ownerDocument&&ll(n.ownerDocument.documentElement,n)){if(r!==null&&Ci(n)){if(t=r.start,e=r.end,e===void 0&&(e=t),"selectionStart"in n)n.selectionStart=t,n.selectionEnd=Math.min(e,n.value.length);else if(e=(t=n.ownerDocument||document)&&t.defaultView||window,e.getSelection){e=e.getSelection();var i=n.textContent.length,o=Math.min(r.start,i);r=r.end===void 0?o:Math.min(r.end,i),!e.extend&&o>r&&(i=r,r=o,o=i),i=al(n,o);var a=al(n,r);i&&a&&(e.rangeCount!==1||e.anchorNode!==i.node||e.anchorOffset!==i.offset||e.focusNode!==a.node||e.focusOffset!==a.offset)&&(t=t.createRange(),t.setStart(i.node,i.offset),e.removeAllRanges(),o>r?(e.addRange(t),e.extend(a.node,a.offset)):(t.setEnd(a.node,a.offset),e.addRange(t)))}}for(t=[],e=n;e=e.parentNode;)e.nodeType===1&&t.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof n.focus=="function"&&n.focus(),n=0;n<t.length;n++)e=t[n],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var Id=U&&"documentMode"in document&&11>=document.documentMode,Cn=null,_i=null,cr=null,Ei=!1;function cl(e,t,n){var r=n.window===n?n.document:n.nodeType===9?n:n.ownerDocument;Ei||Cn==null||Cn!==Ar(r)||(r=Cn,"selectionStart"in r&&Ci(r)?r={start:r.selectionStart,end:r.selectionEnd}:(r=(r.ownerDocument&&r.ownerDocument.defaultView||window).getSelection(),r={anchorNode:r.anchorNode,anchorOffset:r.anchorOffset,focusNode:r.focusNode,focusOffset:r.focusOffset}),cr&&ur(cr,r)||(cr=r,r=ns(_i,"onSelect"),0<r.length&&(t=new vi("onSelect","select",null,t,n),e.push({event:t,listeners:r}),t.target=Cn)))}function Zr(e,t){var n={};return n[e.toLowerCase()]=t.toLowerCase(),n["Webkit"+e]="webkit"+t,n["Moz"+e]="moz"+t,n}var _n={animationend:Zr("Animation","AnimationEnd"),animationiteration:Zr("Animation","AnimationIteration"),animationstart:Zr("Animation","AnimationStart"),transitionend:Zr("Transition","TransitionEnd")},bi={},dl={};U&&(dl=document.createElement("div").style,"AnimationEvent"in window||(delete _n.animationend.animation,delete _n.animationiteration.animation,delete _n.animationstart.animation),"TransitionEvent"in window||delete _n.transitionend.transition);function es(e){if(bi[e])return bi[e];if(!_n[e])return e;var t=_n[e],n;for(n in t)if(t.hasOwnProperty(n)&&n in dl)return bi[e]=t[n];return e}var ml=es("animationend"),fl=es("animationiteration"),hl=es("animationstart"),pl=es("transitionend"),gl=new Map,vl="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function Ut(e,t){gl.set(e,t),P(t,[e])}for(var Pi=0;Pi<vl.length;Pi++){var Mi=vl[Pi],zd=Mi.toLowerCase(),Fd=Mi[0].toUpperCase()+Mi.slice(1);Ut(zd,"on"+Fd)}Ut(ml,"onAnimationEnd"),Ut(fl,"onAnimationIteration"),Ut(hl,"onAnimationStart"),Ut("dblclick","onDoubleClick"),Ut("focusin","onFocus"),Ut("focusout","onBlur"),Ut(pl,"onTransitionEnd"),M("onMouseEnter",["mouseout","mouseover"]),M("onMouseLeave",["mouseout","mouseover"]),M("onPointerEnter",["pointerout","pointerover"]),M("onPointerLeave",["pointerout","pointerover"]),P("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),P("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),P("onBeforeInput",["compositionend","keypress","textInput","paste"]),P("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),P("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),P("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var dr="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),Od=new Set("cancel close invalid load scroll toggle".split(" ").concat(dr));function yl(e,t,n){var r=e.type||"unknown-event";e.currentTarget=n,zc(r,t,void 0,e),e.currentTarget=null}function kl(e,t){t=(t&4)!==0;for(var n=0;n<e.length;n++){var r=e[n],i=r.event;r=r.listeners;e:{var o=void 0;if(t)for(var a=r.length-1;0<=a;a--){var d=r[a],m=d.instance,y=d.currentTarget;if(d=d.listener,m!==o&&i.isPropagationStopped())break e;yl(i,d,y),o=m}else for(a=0;a<r.length;a++){if(d=r[a],m=d.instance,y=d.currentTarget,d=d.listener,m!==o&&i.isPropagationStopped())break e;yl(i,d,y),o=m}}}if(Fr)throw e=ai,Fr=!1,ai=null,e}function he(e,t){var n=t[Fi];n===void 0&&(n=t[Fi]=new Set);var r=e+"__bubble";n.has(r)||(xl(t,e,2,!1),n.add(r))}function Ti(e,t,n){var r=0;t&&(r|=4),xl(n,e,r,t)}var ts="_reactListening"+Math.random().toString(36).slice(2);function mr(e){if(!e[ts]){e[ts]=!0,g.forEach(function(n){n!=="selectionchange"&&(Od.has(n)||Ti(n,!1,e),Ti(n,!0,e))});var t=e.nodeType===9?e:e.ownerDocument;t===null||t[ts]||(t[ts]=!0,Ti("selectionchange",!1,t))}}function xl(e,t,n,r){switch(Va(t)){case 1:var i=Zc;break;case 4:i=ed;break;default:i=hi}n=i.bind(null,t,n,e),i=void 0,!oi||t!=="touchstart"&&t!=="touchmove"&&t!=="wheel"||(i=!0),r?i!==void 0?e.addEventListener(t,n,{capture:!0,passive:i}):e.addEventListener(t,n,!0):i!==void 0?e.addEventListener(t,n,{passive:i}):e.addEventListener(t,n,!1)}function Li(e,t,n,r,i){var o=r;if((t&1)===0&&(t&2)===0&&r!==null)e:for(;;){if(r===null)return;var a=r.tag;if(a===3||a===4){var d=r.stateNode.containerInfo;if(d===i||d.nodeType===8&&d.parentNode===i)break;if(a===4)for(a=r.return;a!==null;){var m=a.tag;if((m===3||m===4)&&(m=a.stateNode.containerInfo,m===i||m.nodeType===8&&m.parentNode===i))return;a=a.return}for(;d!==null;){if(a=on(d),a===null)return;if(m=a.tag,m===5||m===6){r=o=a;continue e}d=d.parentNode}}r=r.return}Ca(function(){var y=o,N=ri(n),C=[];e:{var j=gl.get(e);if(j!==void 0){var D=vi,B=e;switch(e){case"keypress":if(Xr(n)===0)break e;case"keydown":case"keyup":D=pd;break;case"focusin":B="focus",D=xi;break;case"focusout":B="blur",D=xi;break;case"beforeblur":case"afterblur":D=xi;break;case"click":if(n.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":D=Qa;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":D=rd;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":D=yd;break;case ml:case fl:case hl:D=od;break;case pl:D=xd;break;case"scroll":D=td;break;case"wheel":D=jd;break;case"copy":case"cut":case"paste":D=ld;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":D=Ga}var W=(t&4)!==0,_e=!W&&e==="scroll",p=W?j!==null?j+"Capture":null:j;W=[];for(var f=y,v;f!==null;){v=f;var E=v.stateNode;if(v.tag===5&&E!==null&&(v=E,p!==null&&(E=Gn(f,p),E!=null&&W.push(fr(f,E,v)))),_e)break;f=f.return}0<W.length&&(j=new D(j,B,null,n,N),C.push({event:j,listeners:W}))}}if((t&7)===0){e:{if(j=e==="mouseover"||e==="pointerover",D=e==="mouseout"||e==="pointerout",j&&n!==ni&&(B=n.relatedTarget||n.fromElement)&&(on(B)||B[bt]))break e;if((D||j)&&(j=N.window===N?N:(j=N.ownerDocument)?j.defaultView||j.parentWindow:window,D?(B=n.relatedTarget||n.toElement,D=y,B=B?on(B):null,B!==null&&(_e=sn(B),B!==_e||B.tag!==5&&B.tag!==6)&&(B=null)):(D=null,B=y),D!==B)){if(W=Qa,E="onMouseLeave",p="onMouseEnter",f="mouse",(e==="pointerout"||e==="pointerover")&&(W=Ga,E="onPointerLeave",p="onPointerEnter",f="pointer"),_e=D==null?j:Pn(D),v=B==null?j:Pn(B),j=new W(E,f+"leave",D,n,N),j.target=_e,j.relatedTarget=v,E=null,on(N)===y&&(W=new W(p,f+"enter",B,n,N),W.target=v,W.relatedTarget=_e,E=W),_e=E,D&&B)t:{for(W=D,p=B,f=0,v=W;v;v=En(v))f++;for(v=0,E=p;E;E=En(E))v++;for(;0<f-v;)W=En(W),f--;for(;0<v-f;)p=En(p),v--;for(;f--;){if(W===p||p!==null&&W===p.alternate)break t;W=En(W),p=En(p)}W=null}else W=null;D!==null&&wl(C,j,D,W,!1),B!==null&&_e!==null&&wl(C,_e,B,W,!0)}}e:{if(j=y?Pn(y):window,D=j.nodeName&&j.nodeName.toLowerCase(),D==="select"||D==="input"&&j.type==="file")var V=Pd;else if(el(j))if(nl)V=Rd;else{V=Td;var H=Md}else(D=j.nodeName)&&D.toLowerCase()==="input"&&(j.type==="checkbox"||j.type==="radio")&&(V=Ld);if(V&&(V=V(e,y))){tl(C,V,n,N);break e}H&&H(e,j,y),e==="focusout"&&(H=j._wrapperState)&&H.controlled&&j.type==="number"&&Ys(j,"number",j.value)}switch(H=y?Pn(y):window,e){case"focusin":(el(H)||H.contentEditable==="true")&&(Cn=H,_i=y,cr=null);break;case"focusout":cr=_i=Cn=null;break;case"mousedown":Ei=!0;break;case"contextmenu":case"mouseup":case"dragend":Ei=!1,cl(C,n,N);break;case"selectionchange":if(Id)break;case"keydown":case"keyup":cl(C,n,N)}var Q;if(ji)e:{switch(e){case"compositionstart":var X="onCompositionStart";break e;case"compositionend":X="onCompositionEnd";break e;case"compositionupdate":X="onCompositionUpdate";break e}X=void 0}else Nn?Ja(e,n)&&(X="onCompositionEnd"):e==="keydown"&&n.keyCode===229&&(X="onCompositionStart");X&&(Xa&&n.locale!=="ko"&&(Nn||X!=="onCompositionStart"?X==="onCompositionEnd"&&Nn&&(Q=$a()):(Bt=N,gi="value"in Bt?Bt.value:Bt.textContent,Nn=!0)),H=ns(y,X),0<H.length&&(X=new Ka(X,e,null,n,N),C.push({event:X,listeners:H}),Q?X.data=Q:(Q=Za(n),Q!==null&&(X.data=Q)))),(Q=Nd?Cd(e,n):_d(e,n))&&(y=ns(y,"onBeforeInput"),0<y.length&&(N=new Ka("onBeforeInput","beforeinput",null,n,N),C.push({event:N,listeners:y}),N.data=Q))}kl(C,t)})}function fr(e,t,n){return{instance:e,listener:t,currentTarget:n}}function ns(e,t){for(var n=t+"Capture",r=[];e!==null;){var i=e,o=i.stateNode;i.tag===5&&o!==null&&(i=o,o=Gn(e,n),o!=null&&r.unshift(fr(e,o,i)),o=Gn(e,t),o!=null&&r.push(fr(e,o,i))),e=e.return}return r}function En(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function wl(e,t,n,r,i){for(var o=t._reactName,a=[];n!==null&&n!==r;){var d=n,m=d.alternate,y=d.stateNode;if(m!==null&&m===r)break;d.tag===5&&y!==null&&(d=y,i?(m=Gn(n,o),m!=null&&a.unshift(fr(n,m,d))):i||(m=Gn(n,o),m!=null&&a.push(fr(n,m,d)))),n=n.return}a.length!==0&&e.push({event:t,listeners:a})}var Bd=/\r\n?/g,Ud=/\u0000|\uFFFD/g;function jl(e){return(typeof e=="string"?e:""+e).replace(Bd,`
`).replace(Ud,"")}function rs(e,t,n){if(t=jl(t),jl(e)!==t&&n)throw Error(u(425))}function ss(){}var Ri=null,Di=null;function Ai(e,t){return e==="textarea"||e==="noscript"||typeof t.children=="string"||typeof t.children=="number"||typeof t.dangerouslySetInnerHTML=="object"&&t.dangerouslySetInnerHTML!==null&&t.dangerouslySetInnerHTML.__html!=null}var Ii=typeof setTimeout=="function"?setTimeout:void 0,Wd=typeof clearTimeout=="function"?clearTimeout:void 0,Sl=typeof Promise=="function"?Promise:void 0,Vd=typeof queueMicrotask=="function"?queueMicrotask:typeof Sl<"u"?function(e){return Sl.resolve(null).then(e).catch($d)}:Ii;function $d(e){setTimeout(function(){throw e})}function zi(e,t){var n=t,r=0;do{var i=n.nextSibling;if(e.removeChild(n),i&&i.nodeType===8)if(n=i.data,n==="/$"){if(r===0){e.removeChild(i),rr(t);return}r--}else n!=="$"&&n!=="$?"&&n!=="$!"||r++;n=i}while(n);rr(t)}function Wt(e){for(;e!=null;e=e.nextSibling){var t=e.nodeType;if(t===1||t===3)break;if(t===8){if(t=e.data,t==="$"||t==="$!"||t==="$?")break;if(t==="/$")return null}}return e}function Nl(e){e=e.previousSibling;for(var t=0;e;){if(e.nodeType===8){var n=e.data;if(n==="$"||n==="$!"||n==="$?"){if(t===0)return e;t--}else n==="/$"&&t++}e=e.previousSibling}return null}var bn=Math.random().toString(36).slice(2),St="__reactFiber$"+bn,hr="__reactProps$"+bn,bt="__reactContainer$"+bn,Fi="__reactEvents$"+bn,Hd="__reactListeners$"+bn,Qd="__reactHandles$"+bn;function on(e){var t=e[St];if(t)return t;for(var n=e.parentNode;n;){if(t=n[bt]||n[St]){if(n=t.alternate,t.child!==null||n!==null&&n.child!==null)for(e=Nl(e);e!==null;){if(n=e[St])return n;e=Nl(e)}return t}e=n,n=e.parentNode}return null}function pr(e){return e=e[St]||e[bt],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function Pn(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(u(33))}function is(e){return e[hr]||null}var Oi=[],Mn=-1;function Vt(e){return{current:e}}function pe(e){0>Mn||(e.current=Oi[Mn],Oi[Mn]=null,Mn--)}function de(e,t){Mn++,Oi[Mn]=e.current,e.current=t}var $t={},ze=Vt($t),$e=Vt(!1),an=$t;function Tn(e,t){var n=e.type.contextTypes;if(!n)return $t;var r=e.stateNode;if(r&&r.__reactInternalMemoizedUnmaskedChildContext===t)return r.__reactInternalMemoizedMaskedChildContext;var i={},o;for(o in n)i[o]=t[o];return r&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=t,e.__reactInternalMemoizedMaskedChildContext=i),i}function He(e){return e=e.childContextTypes,e!=null}function os(){pe($e),pe(ze)}function Cl(e,t,n){if(ze.current!==$t)throw Error(u(168));de(ze,t),de($e,n)}function _l(e,t,n){var r=e.stateNode;if(t=t.childContextTypes,typeof r.getChildContext!="function")return n;r=r.getChildContext();for(var i in r)if(!(i in t))throw Error(u(108,ce(e)||"Unknown",i));return O({},n,r)}function as(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||$t,an=ze.current,de(ze,e),de($e,$e.current),!0}function El(e,t,n){var r=e.stateNode;if(!r)throw Error(u(169));n?(e=_l(e,t,an),r.__reactInternalMemoizedMergedChildContext=e,pe($e),pe(ze),de(ze,e)):pe($e),de($e,n)}var Pt=null,ls=!1,Bi=!1;function bl(e){Pt===null?Pt=[e]:Pt.push(e)}function Kd(e){ls=!0,bl(e)}function Ht(){if(!Bi&&Pt!==null){Bi=!0;var e=0,t=ae;try{var n=Pt;for(ae=1;e<n.length;e++){var r=n[e];do r=r(!0);while(r!==null)}Pt=null,ls=!1}catch(i){throw Pt!==null&&(Pt=Pt.slice(e+1)),Ma(li,Ht),i}finally{ae=t,Bi=!1}}return null}var Ln=[],Rn=0,us=null,cs=0,rt=[],st=0,ln=null,Mt=1,Tt="";function un(e,t){Ln[Rn++]=cs,Ln[Rn++]=us,us=e,cs=t}function Pl(e,t,n){rt[st++]=Mt,rt[st++]=Tt,rt[st++]=ln,ln=e;var r=Mt;e=Tt;var i=32-ft(r)-1;r&=~(1<<i),n+=1;var o=32-ft(t)+i;if(30<o){var a=i-i%5;o=(r&(1<<a)-1).toString(32),r>>=a,i-=a,Mt=1<<32-ft(t)+i|n<<i|r,Tt=o+e}else Mt=1<<o|n<<i|r,Tt=e}function Ui(e){e.return!==null&&(un(e,1),Pl(e,1,0))}function Wi(e){for(;e===us;)us=Ln[--Rn],Ln[Rn]=null,cs=Ln[--Rn],Ln[Rn]=null;for(;e===ln;)ln=rt[--st],rt[st]=null,Tt=rt[--st],rt[st]=null,Mt=rt[--st],rt[st]=null}var et=null,tt=null,ye=!1,pt=null;function Ml(e,t){var n=lt(5,null,null,0);n.elementType="DELETED",n.stateNode=t,n.return=e,t=e.deletions,t===null?(e.deletions=[n],e.flags|=16):t.push(n)}function Tl(e,t){switch(e.tag){case 5:var n=e.type;return t=t.nodeType!==1||n.toLowerCase()!==t.nodeName.toLowerCase()?null:t,t!==null?(e.stateNode=t,et=e,tt=Wt(t.firstChild),!0):!1;case 6:return t=e.pendingProps===""||t.nodeType!==3?null:t,t!==null?(e.stateNode=t,et=e,tt=null,!0):!1;case 13:return t=t.nodeType!==8?null:t,t!==null?(n=ln!==null?{id:Mt,overflow:Tt}:null,e.memoizedState={dehydrated:t,treeContext:n,retryLane:1073741824},n=lt(18,null,null,0),n.stateNode=t,n.return=e,e.child=n,et=e,tt=null,!0):!1;default:return!1}}function Vi(e){return(e.mode&1)!==0&&(e.flags&128)===0}function $i(e){if(ye){var t=tt;if(t){var n=t;if(!Tl(e,t)){if(Vi(e))throw Error(u(418));t=Wt(n.nextSibling);var r=et;t&&Tl(e,t)?Ml(r,n):(e.flags=e.flags&-4097|2,ye=!1,et=e)}}else{if(Vi(e))throw Error(u(418));e.flags=e.flags&-4097|2,ye=!1,et=e}}}function Ll(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;et=e}function ds(e){if(e!==et)return!1;if(!ye)return Ll(e),ye=!0,!1;var t;if((t=e.tag!==3)&&!(t=e.tag!==5)&&(t=e.type,t=t!=="head"&&t!=="body"&&!Ai(e.type,e.memoizedProps)),t&&(t=tt)){if(Vi(e))throw Rl(),Error(u(418));for(;t;)Ml(e,t),t=Wt(t.nextSibling)}if(Ll(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(u(317));e:{for(e=e.nextSibling,t=0;e;){if(e.nodeType===8){var n=e.data;if(n==="/$"){if(t===0){tt=Wt(e.nextSibling);break e}t--}else n!=="$"&&n!=="$!"&&n!=="$?"||t++}e=e.nextSibling}tt=null}}else tt=et?Wt(e.stateNode.nextSibling):null;return!0}function Rl(){for(var e=tt;e;)e=Wt(e.nextSibling)}function Dn(){tt=et=null,ye=!1}function Hi(e){pt===null?pt=[e]:pt.push(e)}var Gd=le.ReactCurrentBatchConfig;function gr(e,t,n){if(e=n.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(n._owner){if(n=n._owner,n){if(n.tag!==1)throw Error(u(309));var r=n.stateNode}if(!r)throw Error(u(147,e));var i=r,o=""+e;return t!==null&&t.ref!==null&&typeof t.ref=="function"&&t.ref._stringRef===o?t.ref:(t=function(a){var d=i.refs;a===null?delete d[o]:d[o]=a},t._stringRef=o,t)}if(typeof e!="string")throw Error(u(284));if(!n._owner)throw Error(u(290,e))}return e}function ms(e,t){throw e=Object.prototype.toString.call(t),Error(u(31,e==="[object Object]"?"object with keys {"+Object.keys(t).join(", ")+"}":e))}function Dl(e){var t=e._init;return t(e._payload)}function Al(e){function t(p,f){if(e){var v=p.deletions;v===null?(p.deletions=[f],p.flags|=16):v.push(f)}}function n(p,f){if(!e)return null;for(;f!==null;)t(p,f),f=f.sibling;return null}function r(p,f){for(p=new Map;f!==null;)f.key!==null?p.set(f.key,f):p.set(f.index,f),f=f.sibling;return p}function i(p,f){return p=Zt(p,f),p.index=0,p.sibling=null,p}function o(p,f,v){return p.index=v,e?(v=p.alternate,v!==null?(v=v.index,v<f?(p.flags|=2,f):v):(p.flags|=2,f)):(p.flags|=1048576,f)}function a(p){return e&&p.alternate===null&&(p.flags|=2),p}function d(p,f,v,E){return f===null||f.tag!==6?(f=zo(v,p.mode,E),f.return=p,f):(f=i(f,v),f.return=p,f)}function m(p,f,v,E){var V=v.type;return V===J?N(p,f,v.props.children,E,v.key):f!==null&&(f.elementType===V||typeof V=="object"&&V!==null&&V.$$typeof===Ve&&Dl(V)===f.type)?(E=i(f,v.props),E.ref=gr(p,f,v),E.return=p,E):(E=Is(v.type,v.key,v.props,null,p.mode,E),E.ref=gr(p,f,v),E.return=p,E)}function y(p,f,v,E){return f===null||f.tag!==4||f.stateNode.containerInfo!==v.containerInfo||f.stateNode.implementation!==v.implementation?(f=Fo(v,p.mode,E),f.return=p,f):(f=i(f,v.children||[]),f.return=p,f)}function N(p,f,v,E,V){return f===null||f.tag!==7?(f=vn(v,p.mode,E,V),f.return=p,f):(f=i(f,v),f.return=p,f)}function C(p,f,v){if(typeof f=="string"&&f!==""||typeof f=="number")return f=zo(""+f,p.mode,v),f.return=p,f;if(typeof f=="object"&&f!==null){switch(f.$$typeof){case Ne:return v=Is(f.type,f.key,f.props,null,p.mode,v),v.ref=gr(p,null,f),v.return=p,v;case _:return f=Fo(f,p.mode,v),f.return=p,f;case Ve:var E=f._init;return C(p,E(f._payload),v)}if(Hn(f)||G(f))return f=vn(f,p.mode,v,null),f.return=p,f;ms(p,f)}return null}function j(p,f,v,E){var V=f!==null?f.key:null;if(typeof v=="string"&&v!==""||typeof v=="number")return V!==null?null:d(p,f,""+v,E);if(typeof v=="object"&&v!==null){switch(v.$$typeof){case Ne:return v.key===V?m(p,f,v,E):null;case _:return v.key===V?y(p,f,v,E):null;case Ve:return V=v._init,j(p,f,V(v._payload),E)}if(Hn(v)||G(v))return V!==null?null:N(p,f,v,E,null);ms(p,v)}return null}function D(p,f,v,E,V){if(typeof E=="string"&&E!==""||typeof E=="number")return p=p.get(v)||null,d(f,p,""+E,V);if(typeof E=="object"&&E!==null){switch(E.$$typeof){case Ne:return p=p.get(E.key===null?v:E.key)||null,m(f,p,E,V);case _:return p=p.get(E.key===null?v:E.key)||null,y(f,p,E,V);case Ve:var H=E._init;return D(p,f,v,H(E._payload),V)}if(Hn(E)||G(E))return p=p.get(v)||null,N(f,p,E,V,null);ms(f,E)}return null}function B(p,f,v,E){for(var V=null,H=null,Q=f,X=f=0,De=null;Q!==null&&X<v.length;X++){Q.index>X?(De=Q,Q=null):De=Q.sibling;var ie=j(p,Q,v[X],E);if(ie===null){Q===null&&(Q=De);break}e&&Q&&ie.alternate===null&&t(p,Q),f=o(ie,f,X),H===null?V=ie:H.sibling=ie,H=ie,Q=De}if(X===v.length)return n(p,Q),ye&&un(p,X),V;if(Q===null){for(;X<v.length;X++)Q=C(p,v[X],E),Q!==null&&(f=o(Q,f,X),H===null?V=Q:H.sibling=Q,H=Q);return ye&&un(p,X),V}for(Q=r(p,Q);X<v.length;X++)De=D(Q,p,X,v[X],E),De!==null&&(e&&De.alternate!==null&&Q.delete(De.key===null?X:De.key),f=o(De,f,X),H===null?V=De:H.sibling=De,H=De);return e&&Q.forEach(function(en){return t(p,en)}),ye&&un(p,X),V}function W(p,f,v,E){var V=G(v);if(typeof V!="function")throw Error(u(150));if(v=V.call(v),v==null)throw Error(u(151));for(var H=V=null,Q=f,X=f=0,De=null,ie=v.next();Q!==null&&!ie.done;X++,ie=v.next()){Q.index>X?(De=Q,Q=null):De=Q.sibling;var en=j(p,Q,ie.value,E);if(en===null){Q===null&&(Q=De);break}e&&Q&&en.alternate===null&&t(p,Q),f=o(en,f,X),H===null?V=en:H.sibling=en,H=en,Q=De}if(ie.done)return n(p,Q),ye&&un(p,X),V;if(Q===null){for(;!ie.done;X++,ie=v.next())ie=C(p,ie.value,E),ie!==null&&(f=o(ie,f,X),H===null?V=ie:H.sibling=ie,H=ie);return ye&&un(p,X),V}for(Q=r(p,Q);!ie.done;X++,ie=v.next())ie=D(Q,p,X,ie.value,E),ie!==null&&(e&&ie.alternate!==null&&Q.delete(ie.key===null?X:ie.key),f=o(ie,f,X),H===null?V=ie:H.sibling=ie,H=ie);return e&&Q.forEach(function(Em){return t(p,Em)}),ye&&un(p,X),V}function _e(p,f,v,E){if(typeof v=="object"&&v!==null&&v.type===J&&v.key===null&&(v=v.props.children),typeof v=="object"&&v!==null){switch(v.$$typeof){case Ne:e:{for(var V=v.key,H=f;H!==null;){if(H.key===V){if(V=v.type,V===J){if(H.tag===7){n(p,H.sibling),f=i(H,v.props.children),f.return=p,p=f;break e}}else if(H.elementType===V||typeof V=="object"&&V!==null&&V.$$typeof===Ve&&Dl(V)===H.type){n(p,H.sibling),f=i(H,v.props),f.ref=gr(p,H,v),f.return=p,p=f;break e}n(p,H);break}else t(p,H);H=H.sibling}v.type===J?(f=vn(v.props.children,p.mode,E,v.key),f.return=p,p=f):(E=Is(v.type,v.key,v.props,null,p.mode,E),E.ref=gr(p,f,v),E.return=p,p=E)}return a(p);case _:e:{for(H=v.key;f!==null;){if(f.key===H)if(f.tag===4&&f.stateNode.containerInfo===v.containerInfo&&f.stateNode.implementation===v.implementation){n(p,f.sibling),f=i(f,v.children||[]),f.return=p,p=f;break e}else{n(p,f);break}else t(p,f);f=f.sibling}f=Fo(v,p.mode,E),f.return=p,p=f}return a(p);case Ve:return H=v._init,_e(p,f,H(v._payload),E)}if(Hn(v))return B(p,f,v,E);if(G(v))return W(p,f,v,E);ms(p,v)}return typeof v=="string"&&v!==""||typeof v=="number"?(v=""+v,f!==null&&f.tag===6?(n(p,f.sibling),f=i(f,v),f.return=p,p=f):(n(p,f),f=zo(v,p.mode,E),f.return=p,p=f),a(p)):n(p,f)}return _e}var An=Al(!0),Il=Al(!1),fs=Vt(null),hs=null,In=null,Qi=null;function Ki(){Qi=In=hs=null}function Gi(e){var t=fs.current;pe(fs),e._currentValue=t}function Xi(e,t,n){for(;e!==null;){var r=e.alternate;if((e.childLanes&t)!==t?(e.childLanes|=t,r!==null&&(r.childLanes|=t)):r!==null&&(r.childLanes&t)!==t&&(r.childLanes|=t),e===n)break;e=e.return}}function zn(e,t){hs=e,Qi=In=null,e=e.dependencies,e!==null&&e.firstContext!==null&&((e.lanes&t)!==0&&(Qe=!0),e.firstContext=null)}function it(e){var t=e._currentValue;if(Qi!==e)if(e={context:e,memoizedValue:t,next:null},In===null){if(hs===null)throw Error(u(308));In=e,hs.dependencies={lanes:0,firstContext:e}}else In=In.next=e;return t}var cn=null;function qi(e){cn===null?cn=[e]:cn.push(e)}function zl(e,t,n,r){var i=t.interleaved;return i===null?(n.next=n,qi(t)):(n.next=i.next,i.next=n),t.interleaved=n,Lt(e,r)}function Lt(e,t){e.lanes|=t;var n=e.alternate;for(n!==null&&(n.lanes|=t),n=e,e=e.return;e!==null;)e.childLanes|=t,n=e.alternate,n!==null&&(n.childLanes|=t),n=e,e=e.return;return n.tag===3?n.stateNode:null}var Qt=!1;function Yi(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function Fl(e,t){e=e.updateQueue,t.updateQueue===e&&(t.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function Rt(e,t){return{eventTime:e,lane:t,tag:0,payload:null,callback:null,next:null}}function Kt(e,t,n){var r=e.updateQueue;if(r===null)return null;if(r=r.shared,(ne&2)!==0){var i=r.pending;return i===null?t.next=t:(t.next=i.next,i.next=t),r.pending=t,Lt(e,n)}return i=r.interleaved,i===null?(t.next=t,qi(r)):(t.next=i.next,i.next=t),r.interleaved=t,Lt(e,n)}function ps(e,t,n){if(t=t.updateQueue,t!==null&&(t=t.shared,(n&4194240)!==0)){var r=t.lanes;r&=e.pendingLanes,n|=r,t.lanes=n,di(e,n)}}function Ol(e,t){var n=e.updateQueue,r=e.alternate;if(r!==null&&(r=r.updateQueue,n===r)){var i=null,o=null;if(n=n.firstBaseUpdate,n!==null){do{var a={eventTime:n.eventTime,lane:n.lane,tag:n.tag,payload:n.payload,callback:n.callback,next:null};o===null?i=o=a:o=o.next=a,n=n.next}while(n!==null);o===null?i=o=t:o=o.next=t}else i=o=t;n={baseState:r.baseState,firstBaseUpdate:i,lastBaseUpdate:o,shared:r.shared,effects:r.effects},e.updateQueue=n;return}e=n.lastBaseUpdate,e===null?n.firstBaseUpdate=t:e.next=t,n.lastBaseUpdate=t}function gs(e,t,n,r){var i=e.updateQueue;Qt=!1;var o=i.firstBaseUpdate,a=i.lastBaseUpdate,d=i.shared.pending;if(d!==null){i.shared.pending=null;var m=d,y=m.next;m.next=null,a===null?o=y:a.next=y,a=m;var N=e.alternate;N!==null&&(N=N.updateQueue,d=N.lastBaseUpdate,d!==a&&(d===null?N.firstBaseUpdate=y:d.next=y,N.lastBaseUpdate=m))}if(o!==null){var C=i.baseState;a=0,N=y=m=null,d=o;do{var j=d.lane,D=d.eventTime;if((r&j)===j){N!==null&&(N=N.next={eventTime:D,lane:0,tag:d.tag,payload:d.payload,callback:d.callback,next:null});e:{var B=e,W=d;switch(j=t,D=n,W.tag){case 1:if(B=W.payload,typeof B=="function"){C=B.call(D,C,j);break e}C=B;break e;case 3:B.flags=B.flags&-65537|128;case 0:if(B=W.payload,j=typeof B=="function"?B.call(D,C,j):B,j==null)break e;C=O({},C,j);break e;case 2:Qt=!0}}d.callback!==null&&d.lane!==0&&(e.flags|=64,j=i.effects,j===null?i.effects=[d]:j.push(d))}else D={eventTime:D,lane:j,tag:d.tag,payload:d.payload,callback:d.callback,next:null},N===null?(y=N=D,m=C):N=N.next=D,a|=j;if(d=d.next,d===null){if(d=i.shared.pending,d===null)break;j=d,d=j.next,j.next=null,i.lastBaseUpdate=j,i.shared.pending=null}}while(!0);if(N===null&&(m=C),i.baseState=m,i.firstBaseUpdate=y,i.lastBaseUpdate=N,t=i.shared.interleaved,t!==null){i=t;do a|=i.lane,i=i.next;while(i!==t)}else o===null&&(i.shared.lanes=0);fn|=a,e.lanes=a,e.memoizedState=C}}function Bl(e,t,n){if(e=t.effects,t.effects=null,e!==null)for(t=0;t<e.length;t++){var r=e[t],i=r.callback;if(i!==null){if(r.callback=null,r=n,typeof i!="function")throw Error(u(191,i));i.call(r)}}}var vr={},Nt=Vt(vr),yr=Vt(vr),kr=Vt(vr);function dn(e){if(e===vr)throw Error(u(174));return e}function Ji(e,t){switch(de(kr,t),de(yr,e),de(Nt,vr),e=t.nodeType,e){case 9:case 11:t=(t=t.documentElement)?t.namespaceURI:Zs(null,"");break;default:e=e===8?t.parentNode:t,t=e.namespaceURI||null,e=e.tagName,t=Zs(t,e)}pe(Nt),de(Nt,t)}function Fn(){pe(Nt),pe(yr),pe(kr)}function Ul(e){dn(kr.current);var t=dn(Nt.current),n=Zs(t,e.type);t!==n&&(de(yr,e),de(Nt,n))}function Zi(e){yr.current===e&&(pe(Nt),pe(yr))}var xe=Vt(0);function vs(e){for(var t=e;t!==null;){if(t.tag===13){var n=t.memoizedState;if(n!==null&&(n=n.dehydrated,n===null||n.data==="$?"||n.data==="$!"))return t}else if(t.tag===19&&t.memoizedProps.revealOrder!==void 0){if((t.flags&128)!==0)return t}else if(t.child!==null){t.child.return=t,t=t.child;continue}if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return null;t=t.return}t.sibling.return=t.return,t=t.sibling}return null}var eo=[];function to(){for(var e=0;e<eo.length;e++)eo[e]._workInProgressVersionPrimary=null;eo.length=0}var ys=le.ReactCurrentDispatcher,no=le.ReactCurrentBatchConfig,mn=0,we=null,Pe=null,Le=null,ks=!1,xr=!1,wr=0,Xd=0;function Fe(){throw Error(u(321))}function ro(e,t){if(t===null)return!1;for(var n=0;n<t.length&&n<e.length;n++)if(!ht(e[n],t[n]))return!1;return!0}function so(e,t,n,r,i,o){if(mn=o,we=t,t.memoizedState=null,t.updateQueue=null,t.lanes=0,ys.current=e===null||e.memoizedState===null?Zd:em,e=n(r,i),xr){o=0;do{if(xr=!1,wr=0,25<=o)throw Error(u(301));o+=1,Le=Pe=null,t.updateQueue=null,ys.current=tm,e=n(r,i)}while(xr)}if(ys.current=js,t=Pe!==null&&Pe.next!==null,mn=0,Le=Pe=we=null,ks=!1,t)throw Error(u(300));return e}function io(){var e=wr!==0;return wr=0,e}function Ct(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return Le===null?we.memoizedState=Le=e:Le=Le.next=e,Le}function ot(){if(Pe===null){var e=we.alternate;e=e!==null?e.memoizedState:null}else e=Pe.next;var t=Le===null?we.memoizedState:Le.next;if(t!==null)Le=t,Pe=e;else{if(e===null)throw Error(u(310));Pe=e,e={memoizedState:Pe.memoizedState,baseState:Pe.baseState,baseQueue:Pe.baseQueue,queue:Pe.queue,next:null},Le===null?we.memoizedState=Le=e:Le=Le.next=e}return Le}function jr(e,t){return typeof t=="function"?t(e):t}function oo(e){var t=ot(),n=t.queue;if(n===null)throw Error(u(311));n.lastRenderedReducer=e;var r=Pe,i=r.baseQueue,o=n.pending;if(o!==null){if(i!==null){var a=i.next;i.next=o.next,o.next=a}r.baseQueue=i=o,n.pending=null}if(i!==null){o=i.next,r=r.baseState;var d=a=null,m=null,y=o;do{var N=y.lane;if((mn&N)===N)m!==null&&(m=m.next={lane:0,action:y.action,hasEagerState:y.hasEagerState,eagerState:y.eagerState,next:null}),r=y.hasEagerState?y.eagerState:e(r,y.action);else{var C={lane:N,action:y.action,hasEagerState:y.hasEagerState,eagerState:y.eagerState,next:null};m===null?(d=m=C,a=r):m=m.next=C,we.lanes|=N,fn|=N}y=y.next}while(y!==null&&y!==o);m===null?a=r:m.next=d,ht(r,t.memoizedState)||(Qe=!0),t.memoizedState=r,t.baseState=a,t.baseQueue=m,n.lastRenderedState=r}if(e=n.interleaved,e!==null){i=e;do o=i.lane,we.lanes|=o,fn|=o,i=i.next;while(i!==e)}else i===null&&(n.lanes=0);return[t.memoizedState,n.dispatch]}function ao(e){var t=ot(),n=t.queue;if(n===null)throw Error(u(311));n.lastRenderedReducer=e;var r=n.dispatch,i=n.pending,o=t.memoizedState;if(i!==null){n.pending=null;var a=i=i.next;do o=e(o,a.action),a=a.next;while(a!==i);ht(o,t.memoizedState)||(Qe=!0),t.memoizedState=o,t.baseQueue===null&&(t.baseState=o),n.lastRenderedState=o}return[o,r]}function Wl(){}function Vl(e,t){var n=we,r=ot(),i=t(),o=!ht(r.memoizedState,i);if(o&&(r.memoizedState=i,Qe=!0),r=r.queue,lo(Ql.bind(null,n,r,e),[e]),r.getSnapshot!==t||o||Le!==null&&Le.memoizedState.tag&1){if(n.flags|=2048,Sr(9,Hl.bind(null,n,r,i,t),void 0,null),Re===null)throw Error(u(349));(mn&30)!==0||$l(n,t,i)}return i}function $l(e,t,n){e.flags|=16384,e={getSnapshot:t,value:n},t=we.updateQueue,t===null?(t={lastEffect:null,stores:null},we.updateQueue=t,t.stores=[e]):(n=t.stores,n===null?t.stores=[e]:n.push(e))}function Hl(e,t,n,r){t.value=n,t.getSnapshot=r,Kl(t)&&Gl(e)}function Ql(e,t,n){return n(function(){Kl(t)&&Gl(e)})}function Kl(e){var t=e.getSnapshot;e=e.value;try{var n=t();return!ht(e,n)}catch{return!0}}function Gl(e){var t=Lt(e,1);t!==null&&kt(t,e,1,-1)}function Xl(e){var t=Ct();return typeof e=="function"&&(e=e()),t.memoizedState=t.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:jr,lastRenderedState:e},t.queue=e,e=e.dispatch=Jd.bind(null,we,e),[t.memoizedState,e]}function Sr(e,t,n,r){return e={tag:e,create:t,destroy:n,deps:r,next:null},t=we.updateQueue,t===null?(t={lastEffect:null,stores:null},we.updateQueue=t,t.lastEffect=e.next=e):(n=t.lastEffect,n===null?t.lastEffect=e.next=e:(r=n.next,n.next=e,e.next=r,t.lastEffect=e)),e}function ql(){return ot().memoizedState}function xs(e,t,n,r){var i=Ct();we.flags|=e,i.memoizedState=Sr(1|t,n,void 0,r===void 0?null:r)}function ws(e,t,n,r){var i=ot();r=r===void 0?null:r;var o=void 0;if(Pe!==null){var a=Pe.memoizedState;if(o=a.destroy,r!==null&&ro(r,a.deps)){i.memoizedState=Sr(t,n,o,r);return}}we.flags|=e,i.memoizedState=Sr(1|t,n,o,r)}function Yl(e,t){return xs(8390656,8,e,t)}function lo(e,t){return ws(2048,8,e,t)}function Jl(e,t){return ws(4,2,e,t)}function Zl(e,t){return ws(4,4,e,t)}function eu(e,t){if(typeof t=="function")return e=e(),t(e),function(){t(null)};if(t!=null)return e=e(),t.current=e,function(){t.current=null}}function tu(e,t,n){return n=n!=null?n.concat([e]):null,ws(4,4,eu.bind(null,t,e),n)}function uo(){}function nu(e,t){var n=ot();t=t===void 0?null:t;var r=n.memoizedState;return r!==null&&t!==null&&ro(t,r[1])?r[0]:(n.memoizedState=[e,t],e)}function ru(e,t){var n=ot();t=t===void 0?null:t;var r=n.memoizedState;return r!==null&&t!==null&&ro(t,r[1])?r[0]:(e=e(),n.memoizedState=[e,t],e)}function su(e,t,n){return(mn&21)===0?(e.baseState&&(e.baseState=!1,Qe=!0),e.memoizedState=n):(ht(n,t)||(n=Da(),we.lanes|=n,fn|=n,e.baseState=!0),t)}function qd(e,t){var n=ae;ae=n!==0&&4>n?n:4,e(!0);var r=no.transition;no.transition={};try{e(!1),t()}finally{ae=n,no.transition=r}}function iu(){return ot().memoizedState}function Yd(e,t,n){var r=Yt(e);if(n={lane:r,action:n,hasEagerState:!1,eagerState:null,next:null},ou(e))au(t,n);else if(n=zl(e,t,n,r),n!==null){var i=We();kt(n,e,r,i),lu(n,t,r)}}function Jd(e,t,n){var r=Yt(e),i={lane:r,action:n,hasEagerState:!1,eagerState:null,next:null};if(ou(e))au(t,i);else{var o=e.alternate;if(e.lanes===0&&(o===null||o.lanes===0)&&(o=t.lastRenderedReducer,o!==null))try{var a=t.lastRenderedState,d=o(a,n);if(i.hasEagerState=!0,i.eagerState=d,ht(d,a)){var m=t.interleaved;m===null?(i.next=i,qi(t)):(i.next=m.next,m.next=i),t.interleaved=i;return}}catch{}finally{}n=zl(e,t,i,r),n!==null&&(i=We(),kt(n,e,r,i),lu(n,t,r))}}function ou(e){var t=e.alternate;return e===we||t!==null&&t===we}function au(e,t){xr=ks=!0;var n=e.pending;n===null?t.next=t:(t.next=n.next,n.next=t),e.pending=t}function lu(e,t,n){if((n&4194240)!==0){var r=t.lanes;r&=e.pendingLanes,n|=r,t.lanes=n,di(e,n)}}var js={readContext:it,useCallback:Fe,useContext:Fe,useEffect:Fe,useImperativeHandle:Fe,useInsertionEffect:Fe,useLayoutEffect:Fe,useMemo:Fe,useReducer:Fe,useRef:Fe,useState:Fe,useDebugValue:Fe,useDeferredValue:Fe,useTransition:Fe,useMutableSource:Fe,useSyncExternalStore:Fe,useId:Fe,unstable_isNewReconciler:!1},Zd={readContext:it,useCallback:function(e,t){return Ct().memoizedState=[e,t===void 0?null:t],e},useContext:it,useEffect:Yl,useImperativeHandle:function(e,t,n){return n=n!=null?n.concat([e]):null,xs(4194308,4,eu.bind(null,t,e),n)},useLayoutEffect:function(e,t){return xs(4194308,4,e,t)},useInsertionEffect:function(e,t){return xs(4,2,e,t)},useMemo:function(e,t){var n=Ct();return t=t===void 0?null:t,e=e(),n.memoizedState=[e,t],e},useReducer:function(e,t,n){var r=Ct();return t=n!==void 0?n(t):t,r.memoizedState=r.baseState=t,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:t},r.queue=e,e=e.dispatch=Yd.bind(null,we,e),[r.memoizedState,e]},useRef:function(e){var t=Ct();return e={current:e},t.memoizedState=e},useState:Xl,useDebugValue:uo,useDeferredValue:function(e){return Ct().memoizedState=e},useTransition:function(){var e=Xl(!1),t=e[0];return e=qd.bind(null,e[1]),Ct().memoizedState=e,[t,e]},useMutableSource:function(){},useSyncExternalStore:function(e,t,n){var r=we,i=Ct();if(ye){if(n===void 0)throw Error(u(407));n=n()}else{if(n=t(),Re===null)throw Error(u(349));(mn&30)!==0||$l(r,t,n)}i.memoizedState=n;var o={value:n,getSnapshot:t};return i.queue=o,Yl(Ql.bind(null,r,o,e),[e]),r.flags|=2048,Sr(9,Hl.bind(null,r,o,n,t),void 0,null),n},useId:function(){var e=Ct(),t=Re.identifierPrefix;if(ye){var n=Tt,r=Mt;n=(r&~(1<<32-ft(r)-1)).toString(32)+n,t=":"+t+"R"+n,n=wr++,0<n&&(t+="H"+n.toString(32)),t+=":"}else n=Xd++,t=":"+t+"r"+n.toString(32)+":";return e.memoizedState=t},unstable_isNewReconciler:!1},em={readContext:it,useCallback:nu,useContext:it,useEffect:lo,useImperativeHandle:tu,useInsertionEffect:Jl,useLayoutEffect:Zl,useMemo:ru,useReducer:oo,useRef:ql,useState:function(){return oo(jr)},useDebugValue:uo,useDeferredValue:function(e){var t=ot();return su(t,Pe.memoizedState,e)},useTransition:function(){var e=oo(jr)[0],t=ot().memoizedState;return[e,t]},useMutableSource:Wl,useSyncExternalStore:Vl,useId:iu,unstable_isNewReconciler:!1},tm={readContext:it,useCallback:nu,useContext:it,useEffect:lo,useImperativeHandle:tu,useInsertionEffect:Jl,useLayoutEffect:Zl,useMemo:ru,useReducer:ao,useRef:ql,useState:function(){return ao(jr)},useDebugValue:uo,useDeferredValue:function(e){var t=ot();return Pe===null?t.memoizedState=e:su(t,Pe.memoizedState,e)},useTransition:function(){var e=ao(jr)[0],t=ot().memoizedState;return[e,t]},useMutableSource:Wl,useSyncExternalStore:Vl,useId:iu,unstable_isNewReconciler:!1};function gt(e,t){if(e&&e.defaultProps){t=O({},t),e=e.defaultProps;for(var n in e)t[n]===void 0&&(t[n]=e[n]);return t}return t}function co(e,t,n,r){t=e.memoizedState,n=n(r,t),n=n==null?t:O({},t,n),e.memoizedState=n,e.lanes===0&&(e.updateQueue.baseState=n)}var Ss={isMounted:function(e){return(e=e._reactInternals)?sn(e)===e:!1},enqueueSetState:function(e,t,n){e=e._reactInternals;var r=We(),i=Yt(e),o=Rt(r,i);o.payload=t,n!=null&&(o.callback=n),t=Kt(e,o,i),t!==null&&(kt(t,e,i,r),ps(t,e,i))},enqueueReplaceState:function(e,t,n){e=e._reactInternals;var r=We(),i=Yt(e),o=Rt(r,i);o.tag=1,o.payload=t,n!=null&&(o.callback=n),t=Kt(e,o,i),t!==null&&(kt(t,e,i,r),ps(t,e,i))},enqueueForceUpdate:function(e,t){e=e._reactInternals;var n=We(),r=Yt(e),i=Rt(n,r);i.tag=2,t!=null&&(i.callback=t),t=Kt(e,i,r),t!==null&&(kt(t,e,r,n),ps(t,e,r))}};function uu(e,t,n,r,i,o,a){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(r,o,a):t.prototype&&t.prototype.isPureReactComponent?!ur(n,r)||!ur(i,o):!0}function cu(e,t,n){var r=!1,i=$t,o=t.contextType;return typeof o=="object"&&o!==null?o=it(o):(i=He(t)?an:ze.current,r=t.contextTypes,o=(r=r!=null)?Tn(e,i):$t),t=new t(n,o),e.memoizedState=t.state!==null&&t.state!==void 0?t.state:null,t.updater=Ss,e.stateNode=t,t._reactInternals=e,r&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=i,e.__reactInternalMemoizedMaskedChildContext=o),t}function du(e,t,n,r){e=t.state,typeof t.componentWillReceiveProps=="function"&&t.componentWillReceiveProps(n,r),typeof t.UNSAFE_componentWillReceiveProps=="function"&&t.UNSAFE_componentWillReceiveProps(n,r),t.state!==e&&Ss.enqueueReplaceState(t,t.state,null)}function mo(e,t,n,r){var i=e.stateNode;i.props=n,i.state=e.memoizedState,i.refs={},Yi(e);var o=t.contextType;typeof o=="object"&&o!==null?i.context=it(o):(o=He(t)?an:ze.current,i.context=Tn(e,o)),i.state=e.memoizedState,o=t.getDerivedStateFromProps,typeof o=="function"&&(co(e,t,o,n),i.state=e.memoizedState),typeof t.getDerivedStateFromProps=="function"||typeof i.getSnapshotBeforeUpdate=="function"||typeof i.UNSAFE_componentWillMount!="function"&&typeof i.componentWillMount!="function"||(t=i.state,typeof i.componentWillMount=="function"&&i.componentWillMount(),typeof i.UNSAFE_componentWillMount=="function"&&i.UNSAFE_componentWillMount(),t!==i.state&&Ss.enqueueReplaceState(i,i.state,null),gs(e,n,i,r),i.state=e.memoizedState),typeof i.componentDidMount=="function"&&(e.flags|=4194308)}function On(e,t){try{var n="",r=t;do n+=re(r),r=r.return;while(r);var i=n}catch(o){i=`
Error generating stack: `+o.message+`
`+o.stack}return{value:e,source:t,stack:i,digest:null}}function fo(e,t,n){return{value:e,source:null,stack:n??null,digest:t??null}}function ho(e,t){try{console.error(t.value)}catch(n){setTimeout(function(){throw n})}}var nm=typeof WeakMap=="function"?WeakMap:Map;function mu(e,t,n){n=Rt(-1,n),n.tag=3,n.payload={element:null};var r=t.value;return n.callback=function(){Ms||(Ms=!0,Po=r),ho(e,t)},n}function fu(e,t,n){n=Rt(-1,n),n.tag=3;var r=e.type.getDerivedStateFromError;if(typeof r=="function"){var i=t.value;n.payload=function(){return r(i)},n.callback=function(){ho(e,t)}}var o=e.stateNode;return o!==null&&typeof o.componentDidCatch=="function"&&(n.callback=function(){ho(e,t),typeof r!="function"&&(Xt===null?Xt=new Set([this]):Xt.add(this));var a=t.stack;this.componentDidCatch(t.value,{componentStack:a!==null?a:""})}),n}function hu(e,t,n){var r=e.pingCache;if(r===null){r=e.pingCache=new nm;var i=new Set;r.set(t,i)}else i=r.get(t),i===void 0&&(i=new Set,r.set(t,i));i.has(n)||(i.add(n),e=gm.bind(null,e,t,n),t.then(e,e))}function pu(e){do{var t;if((t=e.tag===13)&&(t=e.memoizedState,t=t!==null?t.dehydrated!==null:!0),t)return e;e=e.return}while(e!==null);return null}function gu(e,t,n,r,i){return(e.mode&1)===0?(e===t?e.flags|=65536:(e.flags|=128,n.flags|=131072,n.flags&=-52805,n.tag===1&&(n.alternate===null?n.tag=17:(t=Rt(-1,1),t.tag=2,Kt(n,t,1))),n.lanes|=1),e):(e.flags|=65536,e.lanes=i,e)}var rm=le.ReactCurrentOwner,Qe=!1;function Ue(e,t,n,r){t.child=e===null?Il(t,null,n,r):An(t,e.child,n,r)}function vu(e,t,n,r,i){n=n.render;var o=t.ref;return zn(t,i),r=so(e,t,n,r,o,i),n=io(),e!==null&&!Qe?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~i,Dt(e,t,i)):(ye&&n&&Ui(t),t.flags|=1,Ue(e,t,r,i),t.child)}function yu(e,t,n,r,i){if(e===null){var o=n.type;return typeof o=="function"&&!Io(o)&&o.defaultProps===void 0&&n.compare===null&&n.defaultProps===void 0?(t.tag=15,t.type=o,ku(e,t,o,r,i)):(e=Is(n.type,null,r,t,t.mode,i),e.ref=t.ref,e.return=t,t.child=e)}if(o=e.child,(e.lanes&i)===0){var a=o.memoizedProps;if(n=n.compare,n=n!==null?n:ur,n(a,r)&&e.ref===t.ref)return Dt(e,t,i)}return t.flags|=1,e=Zt(o,r),e.ref=t.ref,e.return=t,t.child=e}function ku(e,t,n,r,i){if(e!==null){var o=e.memoizedProps;if(ur(o,r)&&e.ref===t.ref)if(Qe=!1,t.pendingProps=r=o,(e.lanes&i)!==0)(e.flags&131072)!==0&&(Qe=!0);else return t.lanes=e.lanes,Dt(e,t,i)}return po(e,t,n,r,i)}function xu(e,t,n){var r=t.pendingProps,i=r.children,o=e!==null?e.memoizedState:null;if(r.mode==="hidden")if((t.mode&1)===0)t.memoizedState={baseLanes:0,cachePool:null,transitions:null},de(Un,nt),nt|=n;else{if((n&1073741824)===0)return e=o!==null?o.baseLanes|n:n,t.lanes=t.childLanes=1073741824,t.memoizedState={baseLanes:e,cachePool:null,transitions:null},t.updateQueue=null,de(Un,nt),nt|=e,null;t.memoizedState={baseLanes:0,cachePool:null,transitions:null},r=o!==null?o.baseLanes:n,de(Un,nt),nt|=r}else o!==null?(r=o.baseLanes|n,t.memoizedState=null):r=n,de(Un,nt),nt|=r;return Ue(e,t,i,n),t.child}function wu(e,t){var n=t.ref;(e===null&&n!==null||e!==null&&e.ref!==n)&&(t.flags|=512,t.flags|=2097152)}function po(e,t,n,r,i){var o=He(n)?an:ze.current;return o=Tn(t,o),zn(t,i),n=so(e,t,n,r,o,i),r=io(),e!==null&&!Qe?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~i,Dt(e,t,i)):(ye&&r&&Ui(t),t.flags|=1,Ue(e,t,n,i),t.child)}function ju(e,t,n,r,i){if(He(n)){var o=!0;as(t)}else o=!1;if(zn(t,i),t.stateNode===null)Cs(e,t),cu(t,n,r),mo(t,n,r,i),r=!0;else if(e===null){var a=t.stateNode,d=t.memoizedProps;a.props=d;var m=a.context,y=n.contextType;typeof y=="object"&&y!==null?y=it(y):(y=He(n)?an:ze.current,y=Tn(t,y));var N=n.getDerivedStateFromProps,C=typeof N=="function"||typeof a.getSnapshotBeforeUpdate=="function";C||typeof a.UNSAFE_componentWillReceiveProps!="function"&&typeof a.componentWillReceiveProps!="function"||(d!==r||m!==y)&&du(t,a,r,y),Qt=!1;var j=t.memoizedState;a.state=j,gs(t,r,a,i),m=t.memoizedState,d!==r||j!==m||$e.current||Qt?(typeof N=="function"&&(co(t,n,N,r),m=t.memoizedState),(d=Qt||uu(t,n,d,r,j,m,y))?(C||typeof a.UNSAFE_componentWillMount!="function"&&typeof a.componentWillMount!="function"||(typeof a.componentWillMount=="function"&&a.componentWillMount(),typeof a.UNSAFE_componentWillMount=="function"&&a.UNSAFE_componentWillMount()),typeof a.componentDidMount=="function"&&(t.flags|=4194308)):(typeof a.componentDidMount=="function"&&(t.flags|=4194308),t.memoizedProps=r,t.memoizedState=m),a.props=r,a.state=m,a.context=y,r=d):(typeof a.componentDidMount=="function"&&(t.flags|=4194308),r=!1)}else{a=t.stateNode,Fl(e,t),d=t.memoizedProps,y=t.type===t.elementType?d:gt(t.type,d),a.props=y,C=t.pendingProps,j=a.context,m=n.contextType,typeof m=="object"&&m!==null?m=it(m):(m=He(n)?an:ze.current,m=Tn(t,m));var D=n.getDerivedStateFromProps;(N=typeof D=="function"||typeof a.getSnapshotBeforeUpdate=="function")||typeof a.UNSAFE_componentWillReceiveProps!="function"&&typeof a.componentWillReceiveProps!="function"||(d!==C||j!==m)&&du(t,a,r,m),Qt=!1,j=t.memoizedState,a.state=j,gs(t,r,a,i);var B=t.memoizedState;d!==C||j!==B||$e.current||Qt?(typeof D=="function"&&(co(t,n,D,r),B=t.memoizedState),(y=Qt||uu(t,n,y,r,j,B,m)||!1)?(N||typeof a.UNSAFE_componentWillUpdate!="function"&&typeof a.componentWillUpdate!="function"||(typeof a.componentWillUpdate=="function"&&a.componentWillUpdate(r,B,m),typeof a.UNSAFE_componentWillUpdate=="function"&&a.UNSAFE_componentWillUpdate(r,B,m)),typeof a.componentDidUpdate=="function"&&(t.flags|=4),typeof a.getSnapshotBeforeUpdate=="function"&&(t.flags|=1024)):(typeof a.componentDidUpdate!="function"||d===e.memoizedProps&&j===e.memoizedState||(t.flags|=4),typeof a.getSnapshotBeforeUpdate!="function"||d===e.memoizedProps&&j===e.memoizedState||(t.flags|=1024),t.memoizedProps=r,t.memoizedState=B),a.props=r,a.state=B,a.context=m,r=y):(typeof a.componentDidUpdate!="function"||d===e.memoizedProps&&j===e.memoizedState||(t.flags|=4),typeof a.getSnapshotBeforeUpdate!="function"||d===e.memoizedProps&&j===e.memoizedState||(t.flags|=1024),r=!1)}return go(e,t,n,r,o,i)}function go(e,t,n,r,i,o){wu(e,t);var a=(t.flags&128)!==0;if(!r&&!a)return i&&El(t,n,!1),Dt(e,t,o);r=t.stateNode,rm.current=t;var d=a&&typeof n.getDerivedStateFromError!="function"?null:r.render();return t.flags|=1,e!==null&&a?(t.child=An(t,e.child,null,o),t.child=An(t,null,d,o)):Ue(e,t,d,o),t.memoizedState=r.state,i&&El(t,n,!0),t.child}function Su(e){var t=e.stateNode;t.pendingContext?Cl(e,t.pendingContext,t.pendingContext!==t.context):t.context&&Cl(e,t.context,!1),Ji(e,t.containerInfo)}function Nu(e,t,n,r,i){return Dn(),Hi(i),t.flags|=256,Ue(e,t,n,r),t.child}var vo={dehydrated:null,treeContext:null,retryLane:0};function yo(e){return{baseLanes:e,cachePool:null,transitions:null}}function Cu(e,t,n){var r=t.pendingProps,i=xe.current,o=!1,a=(t.flags&128)!==0,d;if((d=a)||(d=e!==null&&e.memoizedState===null?!1:(i&2)!==0),d?(o=!0,t.flags&=-129):(e===null||e.memoizedState!==null)&&(i|=1),de(xe,i&1),e===null)return $i(t),e=t.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?((t.mode&1)===0?t.lanes=1:e.data==="$!"?t.lanes=8:t.lanes=1073741824,null):(a=r.children,e=r.fallback,o?(r=t.mode,o=t.child,a={mode:"hidden",children:a},(r&1)===0&&o!==null?(o.childLanes=0,o.pendingProps=a):o=zs(a,r,0,null),e=vn(e,r,n,null),o.return=t,e.return=t,o.sibling=e,t.child=o,t.child.memoizedState=yo(n),t.memoizedState=vo,e):ko(t,a));if(i=e.memoizedState,i!==null&&(d=i.dehydrated,d!==null))return sm(e,t,a,r,d,i,n);if(o){o=r.fallback,a=t.mode,i=e.child,d=i.sibling;var m={mode:"hidden",children:r.children};return(a&1)===0&&t.child!==i?(r=t.child,r.childLanes=0,r.pendingProps=m,t.deletions=null):(r=Zt(i,m),r.subtreeFlags=i.subtreeFlags&14680064),d!==null?o=Zt(d,o):(o=vn(o,a,n,null),o.flags|=2),o.return=t,r.return=t,r.sibling=o,t.child=r,r=o,o=t.child,a=e.child.memoizedState,a=a===null?yo(n):{baseLanes:a.baseLanes|n,cachePool:null,transitions:a.transitions},o.memoizedState=a,o.childLanes=e.childLanes&~n,t.memoizedState=vo,r}return o=e.child,e=o.sibling,r=Zt(o,{mode:"visible",children:r.children}),(t.mode&1)===0&&(r.lanes=n),r.return=t,r.sibling=null,e!==null&&(n=t.deletions,n===null?(t.deletions=[e],t.flags|=16):n.push(e)),t.child=r,t.memoizedState=null,r}function ko(e,t){return t=zs({mode:"visible",children:t},e.mode,0,null),t.return=e,e.child=t}function Ns(e,t,n,r){return r!==null&&Hi(r),An(t,e.child,null,n),e=ko(t,t.pendingProps.children),e.flags|=2,t.memoizedState=null,e}function sm(e,t,n,r,i,o,a){if(n)return t.flags&256?(t.flags&=-257,r=fo(Error(u(422))),Ns(e,t,a,r)):t.memoizedState!==null?(t.child=e.child,t.flags|=128,null):(o=r.fallback,i=t.mode,r=zs({mode:"visible",children:r.children},i,0,null),o=vn(o,i,a,null),o.flags|=2,r.return=t,o.return=t,r.sibling=o,t.child=r,(t.mode&1)!==0&&An(t,e.child,null,a),t.child.memoizedState=yo(a),t.memoizedState=vo,o);if((t.mode&1)===0)return Ns(e,t,a,null);if(i.data==="$!"){if(r=i.nextSibling&&i.nextSibling.dataset,r)var d=r.dgst;return r=d,o=Error(u(419)),r=fo(o,r,void 0),Ns(e,t,a,r)}if(d=(a&e.childLanes)!==0,Qe||d){if(r=Re,r!==null){switch(a&-a){case 4:i=2;break;case 16:i=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:i=32;break;case 536870912:i=268435456;break;default:i=0}i=(i&(r.suspendedLanes|a))!==0?0:i,i!==0&&i!==o.retryLane&&(o.retryLane=i,Lt(e,i),kt(r,e,i,-1))}return Ao(),r=fo(Error(u(421))),Ns(e,t,a,r)}return i.data==="$?"?(t.flags|=128,t.child=e.child,t=vm.bind(null,e),i._reactRetry=t,null):(e=o.treeContext,tt=Wt(i.nextSibling),et=t,ye=!0,pt=null,e!==null&&(rt[st++]=Mt,rt[st++]=Tt,rt[st++]=ln,Mt=e.id,Tt=e.overflow,ln=t),t=ko(t,r.children),t.flags|=4096,t)}function _u(e,t,n){e.lanes|=t;var r=e.alternate;r!==null&&(r.lanes|=t),Xi(e.return,t,n)}function xo(e,t,n,r,i){var o=e.memoizedState;o===null?e.memoizedState={isBackwards:t,rendering:null,renderingStartTime:0,last:r,tail:n,tailMode:i}:(o.isBackwards=t,o.rendering=null,o.renderingStartTime=0,o.last=r,o.tail=n,o.tailMode=i)}function Eu(e,t,n){var r=t.pendingProps,i=r.revealOrder,o=r.tail;if(Ue(e,t,r.children,n),r=xe.current,(r&2)!==0)r=r&1|2,t.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=t.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&_u(e,n,t);else if(e.tag===19)_u(e,n,t);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===t)break e;for(;e.sibling===null;){if(e.return===null||e.return===t)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}r&=1}if(de(xe,r),(t.mode&1)===0)t.memoizedState=null;else switch(i){case"forwards":for(n=t.child,i=null;n!==null;)e=n.alternate,e!==null&&vs(e)===null&&(i=n),n=n.sibling;n=i,n===null?(i=t.child,t.child=null):(i=n.sibling,n.sibling=null),xo(t,!1,i,n,o);break;case"backwards":for(n=null,i=t.child,t.child=null;i!==null;){if(e=i.alternate,e!==null&&vs(e)===null){t.child=i;break}e=i.sibling,i.sibling=n,n=i,i=e}xo(t,!0,n,null,o);break;case"together":xo(t,!1,null,null,void 0);break;default:t.memoizedState=null}return t.child}function Cs(e,t){(t.mode&1)===0&&e!==null&&(e.alternate=null,t.alternate=null,t.flags|=2)}function Dt(e,t,n){if(e!==null&&(t.dependencies=e.dependencies),fn|=t.lanes,(n&t.childLanes)===0)return null;if(e!==null&&t.child!==e.child)throw Error(u(153));if(t.child!==null){for(e=t.child,n=Zt(e,e.pendingProps),t.child=n,n.return=t;e.sibling!==null;)e=e.sibling,n=n.sibling=Zt(e,e.pendingProps),n.return=t;n.sibling=null}return t.child}function im(e,t,n){switch(t.tag){case 3:Su(t),Dn();break;case 5:Ul(t);break;case 1:He(t.type)&&as(t);break;case 4:Ji(t,t.stateNode.containerInfo);break;case 10:var r=t.type._context,i=t.memoizedProps.value;de(fs,r._currentValue),r._currentValue=i;break;case 13:if(r=t.memoizedState,r!==null)return r.dehydrated!==null?(de(xe,xe.current&1),t.flags|=128,null):(n&t.child.childLanes)!==0?Cu(e,t,n):(de(xe,xe.current&1),e=Dt(e,t,n),e!==null?e.sibling:null);de(xe,xe.current&1);break;case 19:if(r=(n&t.childLanes)!==0,(e.flags&128)!==0){if(r)return Eu(e,t,n);t.flags|=128}if(i=t.memoizedState,i!==null&&(i.rendering=null,i.tail=null,i.lastEffect=null),de(xe,xe.current),r)break;return null;case 22:case 23:return t.lanes=0,xu(e,t,n)}return Dt(e,t,n)}var bu,wo,Pu,Mu;bu=function(e,t){for(var n=t.child;n!==null;){if(n.tag===5||n.tag===6)e.appendChild(n.stateNode);else if(n.tag!==4&&n.child!==null){n.child.return=n,n=n.child;continue}if(n===t)break;for(;n.sibling===null;){if(n.return===null||n.return===t)return;n=n.return}n.sibling.return=n.return,n=n.sibling}},wo=function(){},Pu=function(e,t,n,r){var i=e.memoizedProps;if(i!==r){e=t.stateNode,dn(Nt.current);var o=null;switch(n){case"input":i=Xs(e,i),r=Xs(e,r),o=[];break;case"select":i=O({},i,{value:void 0}),r=O({},r,{value:void 0}),o=[];break;case"textarea":i=Js(e,i),r=Js(e,r),o=[];break;default:typeof i.onClick!="function"&&typeof r.onClick=="function"&&(e.onclick=ss)}ei(n,r);var a;n=null;for(y in i)if(!r.hasOwnProperty(y)&&i.hasOwnProperty(y)&&i[y]!=null)if(y==="style"){var d=i[y];for(a in d)d.hasOwnProperty(a)&&(n||(n={}),n[a]="")}else y!=="dangerouslySetInnerHTML"&&y!=="children"&&y!=="suppressContentEditableWarning"&&y!=="suppressHydrationWarning"&&y!=="autoFocus"&&(k.hasOwnProperty(y)?o||(o=[]):(o=o||[]).push(y,null));for(y in r){var m=r[y];if(d=i!=null?i[y]:void 0,r.hasOwnProperty(y)&&m!==d&&(m!=null||d!=null))if(y==="style")if(d){for(a in d)!d.hasOwnProperty(a)||m&&m.hasOwnProperty(a)||(n||(n={}),n[a]="");for(a in m)m.hasOwnProperty(a)&&d[a]!==m[a]&&(n||(n={}),n[a]=m[a])}else n||(o||(o=[]),o.push(y,n)),n=m;else y==="dangerouslySetInnerHTML"?(m=m?m.__html:void 0,d=d?d.__html:void 0,m!=null&&d!==m&&(o=o||[]).push(y,m)):y==="children"?typeof m!="string"&&typeof m!="number"||(o=o||[]).push(y,""+m):y!=="suppressContentEditableWarning"&&y!=="suppressHydrationWarning"&&(k.hasOwnProperty(y)?(m!=null&&y==="onScroll"&&he("scroll",e),o||d===m||(o=[])):(o=o||[]).push(y,m))}n&&(o=o||[]).push("style",n);var y=o;(t.updateQueue=y)&&(t.flags|=4)}},Mu=function(e,t,n,r){n!==r&&(t.flags|=4)};function Nr(e,t){if(!ye)switch(e.tailMode){case"hidden":t=e.tail;for(var n=null;t!==null;)t.alternate!==null&&(n=t),t=t.sibling;n===null?e.tail=null:n.sibling=null;break;case"collapsed":n=e.tail;for(var r=null;n!==null;)n.alternate!==null&&(r=n),n=n.sibling;r===null?t||e.tail===null?e.tail=null:e.tail.sibling=null:r.sibling=null}}function Oe(e){var t=e.alternate!==null&&e.alternate.child===e.child,n=0,r=0;if(t)for(var i=e.child;i!==null;)n|=i.lanes|i.childLanes,r|=i.subtreeFlags&14680064,r|=i.flags&14680064,i.return=e,i=i.sibling;else for(i=e.child;i!==null;)n|=i.lanes|i.childLanes,r|=i.subtreeFlags,r|=i.flags,i.return=e,i=i.sibling;return e.subtreeFlags|=r,e.childLanes=n,t}function om(e,t,n){var r=t.pendingProps;switch(Wi(t),t.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Oe(t),null;case 1:return He(t.type)&&os(),Oe(t),null;case 3:return r=t.stateNode,Fn(),pe($e),pe(ze),to(),r.pendingContext&&(r.context=r.pendingContext,r.pendingContext=null),(e===null||e.child===null)&&(ds(t)?t.flags|=4:e===null||e.memoizedState.isDehydrated&&(t.flags&256)===0||(t.flags|=1024,pt!==null&&(Lo(pt),pt=null))),wo(e,t),Oe(t),null;case 5:Zi(t);var i=dn(kr.current);if(n=t.type,e!==null&&t.stateNode!=null)Pu(e,t,n,r,i),e.ref!==t.ref&&(t.flags|=512,t.flags|=2097152);else{if(!r){if(t.stateNode===null)throw Error(u(166));return Oe(t),null}if(e=dn(Nt.current),ds(t)){r=t.stateNode,n=t.type;var o=t.memoizedProps;switch(r[St]=t,r[hr]=o,e=(t.mode&1)!==0,n){case"dialog":he("cancel",r),he("close",r);break;case"iframe":case"object":case"embed":he("load",r);break;case"video":case"audio":for(i=0;i<dr.length;i++)he(dr[i],r);break;case"source":he("error",r);break;case"img":case"image":case"link":he("error",r),he("load",r);break;case"details":he("toggle",r);break;case"input":ca(r,o),he("invalid",r);break;case"select":r._wrapperState={wasMultiple:!!o.multiple},he("invalid",r);break;case"textarea":fa(r,o),he("invalid",r)}ei(n,o),i=null;for(var a in o)if(o.hasOwnProperty(a)){var d=o[a];a==="children"?typeof d=="string"?r.textContent!==d&&(o.suppressHydrationWarning!==!0&&rs(r.textContent,d,e),i=["children",d]):typeof d=="number"&&r.textContent!==""+d&&(o.suppressHydrationWarning!==!0&&rs(r.textContent,d,e),i=["children",""+d]):k.hasOwnProperty(a)&&d!=null&&a==="onScroll"&&he("scroll",r)}switch(n){case"input":Dr(r),ma(r,o,!0);break;case"textarea":Dr(r),pa(r);break;case"select":case"option":break;default:typeof o.onClick=="function"&&(r.onclick=ss)}r=i,t.updateQueue=r,r!==null&&(t.flags|=4)}else{a=i.nodeType===9?i:i.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=ga(n)),e==="http://www.w3.org/1999/xhtml"?n==="script"?(e=a.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof r.is=="string"?e=a.createElement(n,{is:r.is}):(e=a.createElement(n),n==="select"&&(a=e,r.multiple?a.multiple=!0:r.size&&(a.size=r.size))):e=a.createElementNS(e,n),e[St]=t,e[hr]=r,bu(e,t,!1,!1),t.stateNode=e;e:{switch(a=ti(n,r),n){case"dialog":he("cancel",e),he("close",e),i=r;break;case"iframe":case"object":case"embed":he("load",e),i=r;break;case"video":case"audio":for(i=0;i<dr.length;i++)he(dr[i],e);i=r;break;case"source":he("error",e),i=r;break;case"img":case"image":case"link":he("error",e),he("load",e),i=r;break;case"details":he("toggle",e),i=r;break;case"input":ca(e,r),i=Xs(e,r),he("invalid",e);break;case"option":i=r;break;case"select":e._wrapperState={wasMultiple:!!r.multiple},i=O({},r,{value:void 0}),he("invalid",e);break;case"textarea":fa(e,r),i=Js(e,r),he("invalid",e);break;default:i=r}ei(n,i),d=i;for(o in d)if(d.hasOwnProperty(o)){var m=d[o];o==="style"?ka(e,m):o==="dangerouslySetInnerHTML"?(m=m?m.__html:void 0,m!=null&&va(e,m)):o==="children"?typeof m=="string"?(n!=="textarea"||m!=="")&&Qn(e,m):typeof m=="number"&&Qn(e,""+m):o!=="suppressContentEditableWarning"&&o!=="suppressHydrationWarning"&&o!=="autoFocus"&&(k.hasOwnProperty(o)?m!=null&&o==="onScroll"&&he("scroll",e):m!=null&&ue(e,o,m,a))}switch(n){case"input":Dr(e),ma(e,r,!1);break;case"textarea":Dr(e),pa(e);break;case"option":r.value!=null&&e.setAttribute("value",""+oe(r.value));break;case"select":e.multiple=!!r.multiple,o=r.value,o!=null?kn(e,!!r.multiple,o,!1):r.defaultValue!=null&&kn(e,!!r.multiple,r.defaultValue,!0);break;default:typeof i.onClick=="function"&&(e.onclick=ss)}switch(n){case"button":case"input":case"select":case"textarea":r=!!r.autoFocus;break e;case"img":r=!0;break e;default:r=!1}}r&&(t.flags|=4)}t.ref!==null&&(t.flags|=512,t.flags|=2097152)}return Oe(t),null;case 6:if(e&&t.stateNode!=null)Mu(e,t,e.memoizedProps,r);else{if(typeof r!="string"&&t.stateNode===null)throw Error(u(166));if(n=dn(kr.current),dn(Nt.current),ds(t)){if(r=t.stateNode,n=t.memoizedProps,r[St]=t,(o=r.nodeValue!==n)&&(e=et,e!==null))switch(e.tag){case 3:rs(r.nodeValue,n,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&rs(r.nodeValue,n,(e.mode&1)!==0)}o&&(t.flags|=4)}else r=(n.nodeType===9?n:n.ownerDocument).createTextNode(r),r[St]=t,t.stateNode=r}return Oe(t),null;case 13:if(pe(xe),r=t.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(ye&&tt!==null&&(t.mode&1)!==0&&(t.flags&128)===0)Rl(),Dn(),t.flags|=98560,o=!1;else if(o=ds(t),r!==null&&r.dehydrated!==null){if(e===null){if(!o)throw Error(u(318));if(o=t.memoizedState,o=o!==null?o.dehydrated:null,!o)throw Error(u(317));o[St]=t}else Dn(),(t.flags&128)===0&&(t.memoizedState=null),t.flags|=4;Oe(t),o=!1}else pt!==null&&(Lo(pt),pt=null),o=!0;if(!o)return t.flags&65536?t:null}return(t.flags&128)!==0?(t.lanes=n,t):(r=r!==null,r!==(e!==null&&e.memoizedState!==null)&&r&&(t.child.flags|=8192,(t.mode&1)!==0&&(e===null||(xe.current&1)!==0?Me===0&&(Me=3):Ao())),t.updateQueue!==null&&(t.flags|=4),Oe(t),null);case 4:return Fn(),wo(e,t),e===null&&mr(t.stateNode.containerInfo),Oe(t),null;case 10:return Gi(t.type._context),Oe(t),null;case 17:return He(t.type)&&os(),Oe(t),null;case 19:if(pe(xe),o=t.memoizedState,o===null)return Oe(t),null;if(r=(t.flags&128)!==0,a=o.rendering,a===null)if(r)Nr(o,!1);else{if(Me!==0||e!==null&&(e.flags&128)!==0)for(e=t.child;e!==null;){if(a=vs(e),a!==null){for(t.flags|=128,Nr(o,!1),r=a.updateQueue,r!==null&&(t.updateQueue=r,t.flags|=4),t.subtreeFlags=0,r=n,n=t.child;n!==null;)o=n,e=r,o.flags&=14680066,a=o.alternate,a===null?(o.childLanes=0,o.lanes=e,o.child=null,o.subtreeFlags=0,o.memoizedProps=null,o.memoizedState=null,o.updateQueue=null,o.dependencies=null,o.stateNode=null):(o.childLanes=a.childLanes,o.lanes=a.lanes,o.child=a.child,o.subtreeFlags=0,o.deletions=null,o.memoizedProps=a.memoizedProps,o.memoizedState=a.memoizedState,o.updateQueue=a.updateQueue,o.type=a.type,e=a.dependencies,o.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),n=n.sibling;return de(xe,xe.current&1|2),t.child}e=e.sibling}o.tail!==null&&Ce()>Wn&&(t.flags|=128,r=!0,Nr(o,!1),t.lanes=4194304)}else{if(!r)if(e=vs(a),e!==null){if(t.flags|=128,r=!0,n=e.updateQueue,n!==null&&(t.updateQueue=n,t.flags|=4),Nr(o,!0),o.tail===null&&o.tailMode==="hidden"&&!a.alternate&&!ye)return Oe(t),null}else 2*Ce()-o.renderingStartTime>Wn&&n!==1073741824&&(t.flags|=128,r=!0,Nr(o,!1),t.lanes=4194304);o.isBackwards?(a.sibling=t.child,t.child=a):(n=o.last,n!==null?n.sibling=a:t.child=a,o.last=a)}return o.tail!==null?(t=o.tail,o.rendering=t,o.tail=t.sibling,o.renderingStartTime=Ce(),t.sibling=null,n=xe.current,de(xe,r?n&1|2:n&1),t):(Oe(t),null);case 22:case 23:return Do(),r=t.memoizedState!==null,e!==null&&e.memoizedState!==null!==r&&(t.flags|=8192),r&&(t.mode&1)!==0?(nt&1073741824)!==0&&(Oe(t),t.subtreeFlags&6&&(t.flags|=8192)):Oe(t),null;case 24:return null;case 25:return null}throw Error(u(156,t.tag))}function am(e,t){switch(Wi(t),t.tag){case 1:return He(t.type)&&os(),e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 3:return Fn(),pe($e),pe(ze),to(),e=t.flags,(e&65536)!==0&&(e&128)===0?(t.flags=e&-65537|128,t):null;case 5:return Zi(t),null;case 13:if(pe(xe),e=t.memoizedState,e!==null&&e.dehydrated!==null){if(t.alternate===null)throw Error(u(340));Dn()}return e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 19:return pe(xe),null;case 4:return Fn(),null;case 10:return Gi(t.type._context),null;case 22:case 23:return Do(),null;case 24:return null;default:return null}}var _s=!1,Be=!1,lm=typeof WeakSet=="function"?WeakSet:Set,F=null;function Bn(e,t){var n=e.ref;if(n!==null)if(typeof n=="function")try{n(null)}catch(r){Se(e,t,r)}else n.current=null}function jo(e,t,n){try{n()}catch(r){Se(e,t,r)}}var Tu=!1;function um(e,t){if(Ri=Qr,e=ul(),Ci(e)){if("selectionStart"in e)var n={start:e.selectionStart,end:e.selectionEnd};else e:{n=(n=e.ownerDocument)&&n.defaultView||window;var r=n.getSelection&&n.getSelection();if(r&&r.rangeCount!==0){n=r.anchorNode;var i=r.anchorOffset,o=r.focusNode;r=r.focusOffset;try{n.nodeType,o.nodeType}catch{n=null;break e}var a=0,d=-1,m=-1,y=0,N=0,C=e,j=null;t:for(;;){for(var D;C!==n||i!==0&&C.nodeType!==3||(d=a+i),C!==o||r!==0&&C.nodeType!==3||(m=a+r),C.nodeType===3&&(a+=C.nodeValue.length),(D=C.firstChild)!==null;)j=C,C=D;for(;;){if(C===e)break t;if(j===n&&++y===i&&(d=a),j===o&&++N===r&&(m=a),(D=C.nextSibling)!==null)break;C=j,j=C.parentNode}C=D}n=d===-1||m===-1?null:{start:d,end:m}}else n=null}n=n||{start:0,end:0}}else n=null;for(Di={focusedElem:e,selectionRange:n},Qr=!1,F=t;F!==null;)if(t=F,e=t.child,(t.subtreeFlags&1028)!==0&&e!==null)e.return=t,F=e;else for(;F!==null;){t=F;try{var B=t.alternate;if((t.flags&1024)!==0)switch(t.tag){case 0:case 11:case 15:break;case 1:if(B!==null){var W=B.memoizedProps,_e=B.memoizedState,p=t.stateNode,f=p.getSnapshotBeforeUpdate(t.elementType===t.type?W:gt(t.type,W),_e);p.__reactInternalSnapshotBeforeUpdate=f}break;case 3:var v=t.stateNode.containerInfo;v.nodeType===1?v.textContent="":v.nodeType===9&&v.documentElement&&v.removeChild(v.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(u(163))}}catch(E){Se(t,t.return,E)}if(e=t.sibling,e!==null){e.return=t.return,F=e;break}F=t.return}return B=Tu,Tu=!1,B}function Cr(e,t,n){var r=t.updateQueue;if(r=r!==null?r.lastEffect:null,r!==null){var i=r=r.next;do{if((i.tag&e)===e){var o=i.destroy;i.destroy=void 0,o!==void 0&&jo(t,n,o)}i=i.next}while(i!==r)}}function Es(e,t){if(t=t.updateQueue,t=t!==null?t.lastEffect:null,t!==null){var n=t=t.next;do{if((n.tag&e)===e){var r=n.create;n.destroy=r()}n=n.next}while(n!==t)}}function So(e){var t=e.ref;if(t!==null){var n=e.stateNode;switch(e.tag){case 5:e=n;break;default:e=n}typeof t=="function"?t(e):t.current=e}}function Lu(e){var t=e.alternate;t!==null&&(e.alternate=null,Lu(t)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(t=e.stateNode,t!==null&&(delete t[St],delete t[hr],delete t[Fi],delete t[Hd],delete t[Qd])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function Ru(e){return e.tag===5||e.tag===3||e.tag===4}function Du(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||Ru(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function No(e,t,n){var r=e.tag;if(r===5||r===6)e=e.stateNode,t?n.nodeType===8?n.parentNode.insertBefore(e,t):n.insertBefore(e,t):(n.nodeType===8?(t=n.parentNode,t.insertBefore(e,n)):(t=n,t.appendChild(e)),n=n._reactRootContainer,n!=null||t.onclick!==null||(t.onclick=ss));else if(r!==4&&(e=e.child,e!==null))for(No(e,t,n),e=e.sibling;e!==null;)No(e,t,n),e=e.sibling}function Co(e,t,n){var r=e.tag;if(r===5||r===6)e=e.stateNode,t?n.insertBefore(e,t):n.appendChild(e);else if(r!==4&&(e=e.child,e!==null))for(Co(e,t,n),e=e.sibling;e!==null;)Co(e,t,n),e=e.sibling}var Ae=null,vt=!1;function Gt(e,t,n){for(n=n.child;n!==null;)Au(e,t,n),n=n.sibling}function Au(e,t,n){if(jt&&typeof jt.onCommitFiberUnmount=="function")try{jt.onCommitFiberUnmount(Br,n)}catch{}switch(n.tag){case 5:Be||Bn(n,t);case 6:var r=Ae,i=vt;Ae=null,Gt(e,t,n),Ae=r,vt=i,Ae!==null&&(vt?(e=Ae,n=n.stateNode,e.nodeType===8?e.parentNode.removeChild(n):e.removeChild(n)):Ae.removeChild(n.stateNode));break;case 18:Ae!==null&&(vt?(e=Ae,n=n.stateNode,e.nodeType===8?zi(e.parentNode,n):e.nodeType===1&&zi(e,n),rr(e)):zi(Ae,n.stateNode));break;case 4:r=Ae,i=vt,Ae=n.stateNode.containerInfo,vt=!0,Gt(e,t,n),Ae=r,vt=i;break;case 0:case 11:case 14:case 15:if(!Be&&(r=n.updateQueue,r!==null&&(r=r.lastEffect,r!==null))){i=r=r.next;do{var o=i,a=o.destroy;o=o.tag,a!==void 0&&((o&2)!==0||(o&4)!==0)&&jo(n,t,a),i=i.next}while(i!==r)}Gt(e,t,n);break;case 1:if(!Be&&(Bn(n,t),r=n.stateNode,typeof r.componentWillUnmount=="function"))try{r.props=n.memoizedProps,r.state=n.memoizedState,r.componentWillUnmount()}catch(d){Se(n,t,d)}Gt(e,t,n);break;case 21:Gt(e,t,n);break;case 22:n.mode&1?(Be=(r=Be)||n.memoizedState!==null,Gt(e,t,n),Be=r):Gt(e,t,n);break;default:Gt(e,t,n)}}function Iu(e){var t=e.updateQueue;if(t!==null){e.updateQueue=null;var n=e.stateNode;n===null&&(n=e.stateNode=new lm),t.forEach(function(r){var i=ym.bind(null,e,r);n.has(r)||(n.add(r),r.then(i,i))})}}function yt(e,t){var n=t.deletions;if(n!==null)for(var r=0;r<n.length;r++){var i=n[r];try{var o=e,a=t,d=a;e:for(;d!==null;){switch(d.tag){case 5:Ae=d.stateNode,vt=!1;break e;case 3:Ae=d.stateNode.containerInfo,vt=!0;break e;case 4:Ae=d.stateNode.containerInfo,vt=!0;break e}d=d.return}if(Ae===null)throw Error(u(160));Au(o,a,i),Ae=null,vt=!1;var m=i.alternate;m!==null&&(m.return=null),i.return=null}catch(y){Se(i,t,y)}}if(t.subtreeFlags&12854)for(t=t.child;t!==null;)zu(t,e),t=t.sibling}function zu(e,t){var n=e.alternate,r=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(yt(t,e),_t(e),r&4){try{Cr(3,e,e.return),Es(3,e)}catch(W){Se(e,e.return,W)}try{Cr(5,e,e.return)}catch(W){Se(e,e.return,W)}}break;case 1:yt(t,e),_t(e),r&512&&n!==null&&Bn(n,n.return);break;case 5:if(yt(t,e),_t(e),r&512&&n!==null&&Bn(n,n.return),e.flags&32){var i=e.stateNode;try{Qn(i,"")}catch(W){Se(e,e.return,W)}}if(r&4&&(i=e.stateNode,i!=null)){var o=e.memoizedProps,a=n!==null?n.memoizedProps:o,d=e.type,m=e.updateQueue;if(e.updateQueue=null,m!==null)try{d==="input"&&o.type==="radio"&&o.name!=null&&da(i,o),ti(d,a);var y=ti(d,o);for(a=0;a<m.length;a+=2){var N=m[a],C=m[a+1];N==="style"?ka(i,C):N==="dangerouslySetInnerHTML"?va(i,C):N==="children"?Qn(i,C):ue(i,N,C,y)}switch(d){case"input":qs(i,o);break;case"textarea":ha(i,o);break;case"select":var j=i._wrapperState.wasMultiple;i._wrapperState.wasMultiple=!!o.multiple;var D=o.value;D!=null?kn(i,!!o.multiple,D,!1):j!==!!o.multiple&&(o.defaultValue!=null?kn(i,!!o.multiple,o.defaultValue,!0):kn(i,!!o.multiple,o.multiple?[]:"",!1))}i[hr]=o}catch(W){Se(e,e.return,W)}}break;case 6:if(yt(t,e),_t(e),r&4){if(e.stateNode===null)throw Error(u(162));i=e.stateNode,o=e.memoizedProps;try{i.nodeValue=o}catch(W){Se(e,e.return,W)}}break;case 3:if(yt(t,e),_t(e),r&4&&n!==null&&n.memoizedState.isDehydrated)try{rr(t.containerInfo)}catch(W){Se(e,e.return,W)}break;case 4:yt(t,e),_t(e);break;case 13:yt(t,e),_t(e),i=e.child,i.flags&8192&&(o=i.memoizedState!==null,i.stateNode.isHidden=o,!o||i.alternate!==null&&i.alternate.memoizedState!==null||(bo=Ce())),r&4&&Iu(e);break;case 22:if(N=n!==null&&n.memoizedState!==null,e.mode&1?(Be=(y=Be)||N,yt(t,e),Be=y):yt(t,e),_t(e),r&8192){if(y=e.memoizedState!==null,(e.stateNode.isHidden=y)&&!N&&(e.mode&1)!==0)for(F=e,N=e.child;N!==null;){for(C=F=N;F!==null;){switch(j=F,D=j.child,j.tag){case 0:case 11:case 14:case 15:Cr(4,j,j.return);break;case 1:Bn(j,j.return);var B=j.stateNode;if(typeof B.componentWillUnmount=="function"){r=j,n=j.return;try{t=r,B.props=t.memoizedProps,B.state=t.memoizedState,B.componentWillUnmount()}catch(W){Se(r,n,W)}}break;case 5:Bn(j,j.return);break;case 22:if(j.memoizedState!==null){Bu(C);continue}}D!==null?(D.return=j,F=D):Bu(C)}N=N.sibling}e:for(N=null,C=e;;){if(C.tag===5){if(N===null){N=C;try{i=C.stateNode,y?(o=i.style,typeof o.setProperty=="function"?o.setProperty("display","none","important"):o.display="none"):(d=C.stateNode,m=C.memoizedProps.style,a=m!=null&&m.hasOwnProperty("display")?m.display:null,d.style.display=ya("display",a))}catch(W){Se(e,e.return,W)}}}else if(C.tag===6){if(N===null)try{C.stateNode.nodeValue=y?"":C.memoizedProps}catch(W){Se(e,e.return,W)}}else if((C.tag!==22&&C.tag!==23||C.memoizedState===null||C===e)&&C.child!==null){C.child.return=C,C=C.child;continue}if(C===e)break e;for(;C.sibling===null;){if(C.return===null||C.return===e)break e;N===C&&(N=null),C=C.return}N===C&&(N=null),C.sibling.return=C.return,C=C.sibling}}break;case 19:yt(t,e),_t(e),r&4&&Iu(e);break;case 21:break;default:yt(t,e),_t(e)}}function _t(e){var t=e.flags;if(t&2){try{e:{for(var n=e.return;n!==null;){if(Ru(n)){var r=n;break e}n=n.return}throw Error(u(160))}switch(r.tag){case 5:var i=r.stateNode;r.flags&32&&(Qn(i,""),r.flags&=-33);var o=Du(e);Co(e,o,i);break;case 3:case 4:var a=r.stateNode.containerInfo,d=Du(e);No(e,d,a);break;default:throw Error(u(161))}}catch(m){Se(e,e.return,m)}e.flags&=-3}t&4096&&(e.flags&=-4097)}function cm(e,t,n){F=e,Fu(e)}function Fu(e,t,n){for(var r=(e.mode&1)!==0;F!==null;){var i=F,o=i.child;if(i.tag===22&&r){var a=i.memoizedState!==null||_s;if(!a){var d=i.alternate,m=d!==null&&d.memoizedState!==null||Be;d=_s;var y=Be;if(_s=a,(Be=m)&&!y)for(F=i;F!==null;)a=F,m=a.child,a.tag===22&&a.memoizedState!==null?Uu(i):m!==null?(m.return=a,F=m):Uu(i);for(;o!==null;)F=o,Fu(o),o=o.sibling;F=i,_s=d,Be=y}Ou(e)}else(i.subtreeFlags&8772)!==0&&o!==null?(o.return=i,F=o):Ou(e)}}function Ou(e){for(;F!==null;){var t=F;if((t.flags&8772)!==0){var n=t.alternate;try{if((t.flags&8772)!==0)switch(t.tag){case 0:case 11:case 15:Be||Es(5,t);break;case 1:var r=t.stateNode;if(t.flags&4&&!Be)if(n===null)r.componentDidMount();else{var i=t.elementType===t.type?n.memoizedProps:gt(t.type,n.memoizedProps);r.componentDidUpdate(i,n.memoizedState,r.__reactInternalSnapshotBeforeUpdate)}var o=t.updateQueue;o!==null&&Bl(t,o,r);break;case 3:var a=t.updateQueue;if(a!==null){if(n=null,t.child!==null)switch(t.child.tag){case 5:n=t.child.stateNode;break;case 1:n=t.child.stateNode}Bl(t,a,n)}break;case 5:var d=t.stateNode;if(n===null&&t.flags&4){n=d;var m=t.memoizedProps;switch(t.type){case"button":case"input":case"select":case"textarea":m.autoFocus&&n.focus();break;case"img":m.src&&(n.src=m.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(t.memoizedState===null){var y=t.alternate;if(y!==null){var N=y.memoizedState;if(N!==null){var C=N.dehydrated;C!==null&&rr(C)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(u(163))}Be||t.flags&512&&So(t)}catch(j){Se(t,t.return,j)}}if(t===e){F=null;break}if(n=t.sibling,n!==null){n.return=t.return,F=n;break}F=t.return}}function Bu(e){for(;F!==null;){var t=F;if(t===e){F=null;break}var n=t.sibling;if(n!==null){n.return=t.return,F=n;break}F=t.return}}function Uu(e){for(;F!==null;){var t=F;try{switch(t.tag){case 0:case 11:case 15:var n=t.return;try{Es(4,t)}catch(m){Se(t,n,m)}break;case 1:var r=t.stateNode;if(typeof r.componentDidMount=="function"){var i=t.return;try{r.componentDidMount()}catch(m){Se(t,i,m)}}var o=t.return;try{So(t)}catch(m){Se(t,o,m)}break;case 5:var a=t.return;try{So(t)}catch(m){Se(t,a,m)}}}catch(m){Se(t,t.return,m)}if(t===e){F=null;break}var d=t.sibling;if(d!==null){d.return=t.return,F=d;break}F=t.return}}var dm=Math.ceil,bs=le.ReactCurrentDispatcher,_o=le.ReactCurrentOwner,at=le.ReactCurrentBatchConfig,ne=0,Re=null,Ee=null,Ie=0,nt=0,Un=Vt(0),Me=0,_r=null,fn=0,Ps=0,Eo=0,Er=null,Ke=null,bo=0,Wn=1/0,At=null,Ms=!1,Po=null,Xt=null,Ts=!1,qt=null,Ls=0,br=0,Mo=null,Rs=-1,Ds=0;function We(){return(ne&6)!==0?Ce():Rs!==-1?Rs:Rs=Ce()}function Yt(e){return(e.mode&1)===0?1:(ne&2)!==0&&Ie!==0?Ie&-Ie:Gd.transition!==null?(Ds===0&&(Ds=Da()),Ds):(e=ae,e!==0||(e=window.event,e=e===void 0?16:Va(e.type)),e)}function kt(e,t,n,r){if(50<br)throw br=0,Mo=null,Error(u(185));Jn(e,n,r),((ne&2)===0||e!==Re)&&(e===Re&&((ne&2)===0&&(Ps|=n),Me===4&&Jt(e,Ie)),Ge(e,r),n===1&&ne===0&&(t.mode&1)===0&&(Wn=Ce()+500,ls&&Ht()))}function Ge(e,t){var n=e.callbackNode;Gc(e,t);var r=Vr(e,e===Re?Ie:0);if(r===0)n!==null&&Ta(n),e.callbackNode=null,e.callbackPriority=0;else if(t=r&-r,e.callbackPriority!==t){if(n!=null&&Ta(n),t===1)e.tag===0?Kd(Vu.bind(null,e)):bl(Vu.bind(null,e)),Vd(function(){(ne&6)===0&&Ht()}),n=null;else{switch(Aa(r)){case 1:n=li;break;case 4:n=La;break;case 16:n=Or;break;case 536870912:n=Ra;break;default:n=Or}n=Yu(n,Wu.bind(null,e))}e.callbackPriority=t,e.callbackNode=n}}function Wu(e,t){if(Rs=-1,Ds=0,(ne&6)!==0)throw Error(u(327));var n=e.callbackNode;if(Vn()&&e.callbackNode!==n)return null;var r=Vr(e,e===Re?Ie:0);if(r===0)return null;if((r&30)!==0||(r&e.expiredLanes)!==0||t)t=As(e,r);else{t=r;var i=ne;ne|=2;var o=Hu();(Re!==e||Ie!==t)&&(At=null,Wn=Ce()+500,pn(e,t));do try{hm();break}catch(d){$u(e,d)}while(!0);Ki(),bs.current=o,ne=i,Ee!==null?t=0:(Re=null,Ie=0,t=Me)}if(t!==0){if(t===2&&(i=ui(e),i!==0&&(r=i,t=To(e,i))),t===1)throw n=_r,pn(e,0),Jt(e,r),Ge(e,Ce()),n;if(t===6)Jt(e,r);else{if(i=e.current.alternate,(r&30)===0&&!mm(i)&&(t=As(e,r),t===2&&(o=ui(e),o!==0&&(r=o,t=To(e,o))),t===1))throw n=_r,pn(e,0),Jt(e,r),Ge(e,Ce()),n;switch(e.finishedWork=i,e.finishedLanes=r,t){case 0:case 1:throw Error(u(345));case 2:gn(e,Ke,At);break;case 3:if(Jt(e,r),(r&130023424)===r&&(t=bo+500-Ce(),10<t)){if(Vr(e,0)!==0)break;if(i=e.suspendedLanes,(i&r)!==r){We(),e.pingedLanes|=e.suspendedLanes&i;break}e.timeoutHandle=Ii(gn.bind(null,e,Ke,At),t);break}gn(e,Ke,At);break;case 4:if(Jt(e,r),(r&4194240)===r)break;for(t=e.eventTimes,i=-1;0<r;){var a=31-ft(r);o=1<<a,a=t[a],a>i&&(i=a),r&=~o}if(r=i,r=Ce()-r,r=(120>r?120:480>r?480:1080>r?1080:1920>r?1920:3e3>r?3e3:4320>r?4320:1960*dm(r/1960))-r,10<r){e.timeoutHandle=Ii(gn.bind(null,e,Ke,At),r);break}gn(e,Ke,At);break;case 5:gn(e,Ke,At);break;default:throw Error(u(329))}}}return Ge(e,Ce()),e.callbackNode===n?Wu.bind(null,e):null}function To(e,t){var n=Er;return e.current.memoizedState.isDehydrated&&(pn(e,t).flags|=256),e=As(e,t),e!==2&&(t=Ke,Ke=n,t!==null&&Lo(t)),e}function Lo(e){Ke===null?Ke=e:Ke.push.apply(Ke,e)}function mm(e){for(var t=e;;){if(t.flags&16384){var n=t.updateQueue;if(n!==null&&(n=n.stores,n!==null))for(var r=0;r<n.length;r++){var i=n[r],o=i.getSnapshot;i=i.value;try{if(!ht(o(),i))return!1}catch{return!1}}}if(n=t.child,t.subtreeFlags&16384&&n!==null)n.return=t,t=n;else{if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return!0;t=t.return}t.sibling.return=t.return,t=t.sibling}}return!0}function Jt(e,t){for(t&=~Eo,t&=~Ps,e.suspendedLanes|=t,e.pingedLanes&=~t,e=e.expirationTimes;0<t;){var n=31-ft(t),r=1<<n;e[n]=-1,t&=~r}}function Vu(e){if((ne&6)!==0)throw Error(u(327));Vn();var t=Vr(e,0);if((t&1)===0)return Ge(e,Ce()),null;var n=As(e,t);if(e.tag!==0&&n===2){var r=ui(e);r!==0&&(t=r,n=To(e,r))}if(n===1)throw n=_r,pn(e,0),Jt(e,t),Ge(e,Ce()),n;if(n===6)throw Error(u(345));return e.finishedWork=e.current.alternate,e.finishedLanes=t,gn(e,Ke,At),Ge(e,Ce()),null}function Ro(e,t){var n=ne;ne|=1;try{return e(t)}finally{ne=n,ne===0&&(Wn=Ce()+500,ls&&Ht())}}function hn(e){qt!==null&&qt.tag===0&&(ne&6)===0&&Vn();var t=ne;ne|=1;var n=at.transition,r=ae;try{if(at.transition=null,ae=1,e)return e()}finally{ae=r,at.transition=n,ne=t,(ne&6)===0&&Ht()}}function Do(){nt=Un.current,pe(Un)}function pn(e,t){e.finishedWork=null,e.finishedLanes=0;var n=e.timeoutHandle;if(n!==-1&&(e.timeoutHandle=-1,Wd(n)),Ee!==null)for(n=Ee.return;n!==null;){var r=n;switch(Wi(r),r.tag){case 1:r=r.type.childContextTypes,r!=null&&os();break;case 3:Fn(),pe($e),pe(ze),to();break;case 5:Zi(r);break;case 4:Fn();break;case 13:pe(xe);break;case 19:pe(xe);break;case 10:Gi(r.type._context);break;case 22:case 23:Do()}n=n.return}if(Re=e,Ee=e=Zt(e.current,null),Ie=nt=t,Me=0,_r=null,Eo=Ps=fn=0,Ke=Er=null,cn!==null){for(t=0;t<cn.length;t++)if(n=cn[t],r=n.interleaved,r!==null){n.interleaved=null;var i=r.next,o=n.pending;if(o!==null){var a=o.next;o.next=i,r.next=a}n.pending=r}cn=null}return e}function $u(e,t){do{var n=Ee;try{if(Ki(),ys.current=js,ks){for(var r=we.memoizedState;r!==null;){var i=r.queue;i!==null&&(i.pending=null),r=r.next}ks=!1}if(mn=0,Le=Pe=we=null,xr=!1,wr=0,_o.current=null,n===null||n.return===null){Me=1,_r=t,Ee=null;break}e:{var o=e,a=n.return,d=n,m=t;if(t=Ie,d.flags|=32768,m!==null&&typeof m=="object"&&typeof m.then=="function"){var y=m,N=d,C=N.tag;if((N.mode&1)===0&&(C===0||C===11||C===15)){var j=N.alternate;j?(N.updateQueue=j.updateQueue,N.memoizedState=j.memoizedState,N.lanes=j.lanes):(N.updateQueue=null,N.memoizedState=null)}var D=pu(a);if(D!==null){D.flags&=-257,gu(D,a,d,o,t),D.mode&1&&hu(o,y,t),t=D,m=y;var B=t.updateQueue;if(B===null){var W=new Set;W.add(m),t.updateQueue=W}else B.add(m);break e}else{if((t&1)===0){hu(o,y,t),Ao();break e}m=Error(u(426))}}else if(ye&&d.mode&1){var _e=pu(a);if(_e!==null){(_e.flags&65536)===0&&(_e.flags|=256),gu(_e,a,d,o,t),Hi(On(m,d));break e}}o=m=On(m,d),Me!==4&&(Me=2),Er===null?Er=[o]:Er.push(o),o=a;do{switch(o.tag){case 3:o.flags|=65536,t&=-t,o.lanes|=t;var p=mu(o,m,t);Ol(o,p);break e;case 1:d=m;var f=o.type,v=o.stateNode;if((o.flags&128)===0&&(typeof f.getDerivedStateFromError=="function"||v!==null&&typeof v.componentDidCatch=="function"&&(Xt===null||!Xt.has(v)))){o.flags|=65536,t&=-t,o.lanes|=t;var E=fu(o,d,t);Ol(o,E);break e}}o=o.return}while(o!==null)}Ku(n)}catch(V){t=V,Ee===n&&n!==null&&(Ee=n=n.return);continue}break}while(!0)}function Hu(){var e=bs.current;return bs.current=js,e===null?js:e}function Ao(){(Me===0||Me===3||Me===2)&&(Me=4),Re===null||(fn&268435455)===0&&(Ps&268435455)===0||Jt(Re,Ie)}function As(e,t){var n=ne;ne|=2;var r=Hu();(Re!==e||Ie!==t)&&(At=null,pn(e,t));do try{fm();break}catch(i){$u(e,i)}while(!0);if(Ki(),ne=n,bs.current=r,Ee!==null)throw Error(u(261));return Re=null,Ie=0,Me}function fm(){for(;Ee!==null;)Qu(Ee)}function hm(){for(;Ee!==null&&!Oc();)Qu(Ee)}function Qu(e){var t=qu(e.alternate,e,nt);e.memoizedProps=e.pendingProps,t===null?Ku(e):Ee=t,_o.current=null}function Ku(e){var t=e;do{var n=t.alternate;if(e=t.return,(t.flags&32768)===0){if(n=om(n,t,nt),n!==null){Ee=n;return}}else{if(n=am(n,t),n!==null){n.flags&=32767,Ee=n;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{Me=6,Ee=null;return}}if(t=t.sibling,t!==null){Ee=t;return}Ee=t=e}while(t!==null);Me===0&&(Me=5)}function gn(e,t,n){var r=ae,i=at.transition;try{at.transition=null,ae=1,pm(e,t,n,r)}finally{at.transition=i,ae=r}return null}function pm(e,t,n,r){do Vn();while(qt!==null);if((ne&6)!==0)throw Error(u(327));n=e.finishedWork;var i=e.finishedLanes;if(n===null)return null;if(e.finishedWork=null,e.finishedLanes=0,n===e.current)throw Error(u(177));e.callbackNode=null,e.callbackPriority=0;var o=n.lanes|n.childLanes;if(Xc(e,o),e===Re&&(Ee=Re=null,Ie=0),(n.subtreeFlags&2064)===0&&(n.flags&2064)===0||Ts||(Ts=!0,Yu(Or,function(){return Vn(),null})),o=(n.flags&15990)!==0,(n.subtreeFlags&15990)!==0||o){o=at.transition,at.transition=null;var a=ae;ae=1;var d=ne;ne|=4,_o.current=null,um(e,n),zu(n,e),Ad(Di),Qr=!!Ri,Di=Ri=null,e.current=n,cm(n),Bc(),ne=d,ae=a,at.transition=o}else e.current=n;if(Ts&&(Ts=!1,qt=e,Ls=i),o=e.pendingLanes,o===0&&(Xt=null),Vc(n.stateNode),Ge(e,Ce()),t!==null)for(r=e.onRecoverableError,n=0;n<t.length;n++)i=t[n],r(i.value,{componentStack:i.stack,digest:i.digest});if(Ms)throw Ms=!1,e=Po,Po=null,e;return(Ls&1)!==0&&e.tag!==0&&Vn(),o=e.pendingLanes,(o&1)!==0?e===Mo?br++:(br=0,Mo=e):br=0,Ht(),null}function Vn(){if(qt!==null){var e=Aa(Ls),t=at.transition,n=ae;try{if(at.transition=null,ae=16>e?16:e,qt===null)var r=!1;else{if(e=qt,qt=null,Ls=0,(ne&6)!==0)throw Error(u(331));var i=ne;for(ne|=4,F=e.current;F!==null;){var o=F,a=o.child;if((F.flags&16)!==0){var d=o.deletions;if(d!==null){for(var m=0;m<d.length;m++){var y=d[m];for(F=y;F!==null;){var N=F;switch(N.tag){case 0:case 11:case 15:Cr(8,N,o)}var C=N.child;if(C!==null)C.return=N,F=C;else for(;F!==null;){N=F;var j=N.sibling,D=N.return;if(Lu(N),N===y){F=null;break}if(j!==null){j.return=D,F=j;break}F=D}}}var B=o.alternate;if(B!==null){var W=B.child;if(W!==null){B.child=null;do{var _e=W.sibling;W.sibling=null,W=_e}while(W!==null)}}F=o}}if((o.subtreeFlags&2064)!==0&&a!==null)a.return=o,F=a;else e:for(;F!==null;){if(o=F,(o.flags&2048)!==0)switch(o.tag){case 0:case 11:case 15:Cr(9,o,o.return)}var p=o.sibling;if(p!==null){p.return=o.return,F=p;break e}F=o.return}}var f=e.current;for(F=f;F!==null;){a=F;var v=a.child;if((a.subtreeFlags&2064)!==0&&v!==null)v.return=a,F=v;else e:for(a=f;F!==null;){if(d=F,(d.flags&2048)!==0)try{switch(d.tag){case 0:case 11:case 15:Es(9,d)}}catch(V){Se(d,d.return,V)}if(d===a){F=null;break e}var E=d.sibling;if(E!==null){E.return=d.return,F=E;break e}F=d.return}}if(ne=i,Ht(),jt&&typeof jt.onPostCommitFiberRoot=="function")try{jt.onPostCommitFiberRoot(Br,e)}catch{}r=!0}return r}finally{ae=n,at.transition=t}}return!1}function Gu(e,t,n){t=On(n,t),t=mu(e,t,1),e=Kt(e,t,1),t=We(),e!==null&&(Jn(e,1,t),Ge(e,t))}function Se(e,t,n){if(e.tag===3)Gu(e,e,n);else for(;t!==null;){if(t.tag===3){Gu(t,e,n);break}else if(t.tag===1){var r=t.stateNode;if(typeof t.type.getDerivedStateFromError=="function"||typeof r.componentDidCatch=="function"&&(Xt===null||!Xt.has(r))){e=On(n,e),e=fu(t,e,1),t=Kt(t,e,1),e=We(),t!==null&&(Jn(t,1,e),Ge(t,e));break}}t=t.return}}function gm(e,t,n){var r=e.pingCache;r!==null&&r.delete(t),t=We(),e.pingedLanes|=e.suspendedLanes&n,Re===e&&(Ie&n)===n&&(Me===4||Me===3&&(Ie&130023424)===Ie&&500>Ce()-bo?pn(e,0):Eo|=n),Ge(e,t)}function Xu(e,t){t===0&&((e.mode&1)===0?t=1:(t=Wr,Wr<<=1,(Wr&130023424)===0&&(Wr=4194304)));var n=We();e=Lt(e,t),e!==null&&(Jn(e,t,n),Ge(e,n))}function vm(e){var t=e.memoizedState,n=0;t!==null&&(n=t.retryLane),Xu(e,n)}function ym(e,t){var n=0;switch(e.tag){case 13:var r=e.stateNode,i=e.memoizedState;i!==null&&(n=i.retryLane);break;case 19:r=e.stateNode;break;default:throw Error(u(314))}r!==null&&r.delete(t),Xu(e,n)}var qu;qu=function(e,t,n){if(e!==null)if(e.memoizedProps!==t.pendingProps||$e.current)Qe=!0;else{if((e.lanes&n)===0&&(t.flags&128)===0)return Qe=!1,im(e,t,n);Qe=(e.flags&131072)!==0}else Qe=!1,ye&&(t.flags&1048576)!==0&&Pl(t,cs,t.index);switch(t.lanes=0,t.tag){case 2:var r=t.type;Cs(e,t),e=t.pendingProps;var i=Tn(t,ze.current);zn(t,n),i=so(null,t,r,e,i,n);var o=io();return t.flags|=1,typeof i=="object"&&i!==null&&typeof i.render=="function"&&i.$$typeof===void 0?(t.tag=1,t.memoizedState=null,t.updateQueue=null,He(r)?(o=!0,as(t)):o=!1,t.memoizedState=i.state!==null&&i.state!==void 0?i.state:null,Yi(t),i.updater=Ss,t.stateNode=i,i._reactInternals=t,mo(t,r,e,n),t=go(null,t,r,!0,o,n)):(t.tag=0,ye&&o&&Ui(t),Ue(null,t,i,n),t=t.child),t;case 16:r=t.elementType;e:{switch(Cs(e,t),e=t.pendingProps,i=r._init,r=i(r._payload),t.type=r,i=t.tag=xm(r),e=gt(r,e),i){case 0:t=po(null,t,r,e,n);break e;case 1:t=ju(null,t,r,e,n);break e;case 11:t=vu(null,t,r,e,n);break e;case 14:t=yu(null,t,r,gt(r.type,e),n);break e}throw Error(u(306,r,""))}return t;case 0:return r=t.type,i=t.pendingProps,i=t.elementType===r?i:gt(r,i),po(e,t,r,i,n);case 1:return r=t.type,i=t.pendingProps,i=t.elementType===r?i:gt(r,i),ju(e,t,r,i,n);case 3:e:{if(Su(t),e===null)throw Error(u(387));r=t.pendingProps,o=t.memoizedState,i=o.element,Fl(e,t),gs(t,r,null,n);var a=t.memoizedState;if(r=a.element,o.isDehydrated)if(o={element:r,isDehydrated:!1,cache:a.cache,pendingSuspenseBoundaries:a.pendingSuspenseBoundaries,transitions:a.transitions},t.updateQueue.baseState=o,t.memoizedState=o,t.flags&256){i=On(Error(u(423)),t),t=Nu(e,t,r,n,i);break e}else if(r!==i){i=On(Error(u(424)),t),t=Nu(e,t,r,n,i);break e}else for(tt=Wt(t.stateNode.containerInfo.firstChild),et=t,ye=!0,pt=null,n=Il(t,null,r,n),t.child=n;n;)n.flags=n.flags&-3|4096,n=n.sibling;else{if(Dn(),r===i){t=Dt(e,t,n);break e}Ue(e,t,r,n)}t=t.child}return t;case 5:return Ul(t),e===null&&$i(t),r=t.type,i=t.pendingProps,o=e!==null?e.memoizedProps:null,a=i.children,Ai(r,i)?a=null:o!==null&&Ai(r,o)&&(t.flags|=32),wu(e,t),Ue(e,t,a,n),t.child;case 6:return e===null&&$i(t),null;case 13:return Cu(e,t,n);case 4:return Ji(t,t.stateNode.containerInfo),r=t.pendingProps,e===null?t.child=An(t,null,r,n):Ue(e,t,r,n),t.child;case 11:return r=t.type,i=t.pendingProps,i=t.elementType===r?i:gt(r,i),vu(e,t,r,i,n);case 7:return Ue(e,t,t.pendingProps,n),t.child;case 8:return Ue(e,t,t.pendingProps.children,n),t.child;case 12:return Ue(e,t,t.pendingProps.children,n),t.child;case 10:e:{if(r=t.type._context,i=t.pendingProps,o=t.memoizedProps,a=i.value,de(fs,r._currentValue),r._currentValue=a,o!==null)if(ht(o.value,a)){if(o.children===i.children&&!$e.current){t=Dt(e,t,n);break e}}else for(o=t.child,o!==null&&(o.return=t);o!==null;){var d=o.dependencies;if(d!==null){a=o.child;for(var m=d.firstContext;m!==null;){if(m.context===r){if(o.tag===1){m=Rt(-1,n&-n),m.tag=2;var y=o.updateQueue;if(y!==null){y=y.shared;var N=y.pending;N===null?m.next=m:(m.next=N.next,N.next=m),y.pending=m}}o.lanes|=n,m=o.alternate,m!==null&&(m.lanes|=n),Xi(o.return,n,t),d.lanes|=n;break}m=m.next}}else if(o.tag===10)a=o.type===t.type?null:o.child;else if(o.tag===18){if(a=o.return,a===null)throw Error(u(341));a.lanes|=n,d=a.alternate,d!==null&&(d.lanes|=n),Xi(a,n,t),a=o.sibling}else a=o.child;if(a!==null)a.return=o;else for(a=o;a!==null;){if(a===t){a=null;break}if(o=a.sibling,o!==null){o.return=a.return,a=o;break}a=a.return}o=a}Ue(e,t,i.children,n),t=t.child}return t;case 9:return i=t.type,r=t.pendingProps.children,zn(t,n),i=it(i),r=r(i),t.flags|=1,Ue(e,t,r,n),t.child;case 14:return r=t.type,i=gt(r,t.pendingProps),i=gt(r.type,i),yu(e,t,r,i,n);case 15:return ku(e,t,t.type,t.pendingProps,n);case 17:return r=t.type,i=t.pendingProps,i=t.elementType===r?i:gt(r,i),Cs(e,t),t.tag=1,He(r)?(e=!0,as(t)):e=!1,zn(t,n),cu(t,r,i),mo(t,r,i,n),go(null,t,r,!0,e,n);case 19:return Eu(e,t,n);case 22:return xu(e,t,n)}throw Error(u(156,t.tag))};function Yu(e,t){return Ma(e,t)}function km(e,t,n,r){this.tag=e,this.key=n,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=t,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=r,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function lt(e,t,n,r){return new km(e,t,n,r)}function Io(e){return e=e.prototype,!(!e||!e.isReactComponent)}function xm(e){if(typeof e=="function")return Io(e)?1:0;if(e!=null){if(e=e.$$typeof,e===xt)return 11;if(e===wt)return 14}return 2}function Zt(e,t){var n=e.alternate;return n===null?(n=lt(e.tag,t,e.key,e.mode),n.elementType=e.elementType,n.type=e.type,n.stateNode=e.stateNode,n.alternate=e,e.alternate=n):(n.pendingProps=t,n.type=e.type,n.flags=0,n.subtreeFlags=0,n.deletions=null),n.flags=e.flags&14680064,n.childLanes=e.childLanes,n.lanes=e.lanes,n.child=e.child,n.memoizedProps=e.memoizedProps,n.memoizedState=e.memoizedState,n.updateQueue=e.updateQueue,t=e.dependencies,n.dependencies=t===null?null:{lanes:t.lanes,firstContext:t.firstContext},n.sibling=e.sibling,n.index=e.index,n.ref=e.ref,n}function Is(e,t,n,r,i,o){var a=2;if(r=e,typeof e=="function")Io(e)&&(a=1);else if(typeof e=="string")a=5;else e:switch(e){case J:return vn(n.children,i,o,t);case fe:a=8,i|=8;break;case be:return e=lt(12,n,t,i|2),e.elementType=be,e.lanes=o,e;case Ye:return e=lt(13,n,t,i),e.elementType=Ye,e.lanes=o,e;case mt:return e=lt(19,n,t,i),e.elementType=mt,e.lanes=o,e;case je:return zs(n,i,o,t);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case dt:a=10;break e;case rn:a=9;break e;case xt:a=11;break e;case wt:a=14;break e;case Ve:a=16,r=null;break e}throw Error(u(130,e==null?e:typeof e,""))}return t=lt(a,n,t,i),t.elementType=e,t.type=r,t.lanes=o,t}function vn(e,t,n,r){return e=lt(7,e,r,t),e.lanes=n,e}function zs(e,t,n,r){return e=lt(22,e,r,t),e.elementType=je,e.lanes=n,e.stateNode={isHidden:!1},e}function zo(e,t,n){return e=lt(6,e,null,t),e.lanes=n,e}function Fo(e,t,n){return t=lt(4,e.children!==null?e.children:[],e.key,t),t.lanes=n,t.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},t}function wm(e,t,n,r,i){this.tag=t,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=ci(0),this.expirationTimes=ci(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=ci(0),this.identifierPrefix=r,this.onRecoverableError=i,this.mutableSourceEagerHydrationData=null}function Oo(e,t,n,r,i,o,a,d,m){return e=new wm(e,t,n,d,m),t===1?(t=1,o===!0&&(t|=8)):t=0,o=lt(3,null,null,t),e.current=o,o.stateNode=e,o.memoizedState={element:r,isDehydrated:n,cache:null,transitions:null,pendingSuspenseBoundaries:null},Yi(o),e}function jm(e,t,n){var r=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:_,key:r==null?null:""+r,children:e,containerInfo:t,implementation:n}}function Ju(e){if(!e)return $t;e=e._reactInternals;e:{if(sn(e)!==e||e.tag!==1)throw Error(u(170));var t=e;do{switch(t.tag){case 3:t=t.stateNode.context;break e;case 1:if(He(t.type)){t=t.stateNode.__reactInternalMemoizedMergedChildContext;break e}}t=t.return}while(t!==null);throw Error(u(171))}if(e.tag===1){var n=e.type;if(He(n))return _l(e,n,t)}return t}function Zu(e,t,n,r,i,o,a,d,m){return e=Oo(n,r,!0,e,i,o,a,d,m),e.context=Ju(null),n=e.current,r=We(),i=Yt(n),o=Rt(r,i),o.callback=t??null,Kt(n,o,i),e.current.lanes=i,Jn(e,i,r),Ge(e,r),e}function Fs(e,t,n,r){var i=t.current,o=We(),a=Yt(i);return n=Ju(n),t.context===null?t.context=n:t.pendingContext=n,t=Rt(o,a),t.payload={element:e},r=r===void 0?null:r,r!==null&&(t.callback=r),e=Kt(i,t,a),e!==null&&(kt(e,i,a,o),ps(e,i,a)),a}function Os(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function ec(e,t){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var n=e.retryLane;e.retryLane=n!==0&&n<t?n:t}}function Bo(e,t){ec(e,t),(e=e.alternate)&&ec(e,t)}function Sm(){return null}var tc=typeof reportError=="function"?reportError:function(e){console.error(e)};function Uo(e){this._internalRoot=e}Bs.prototype.render=Uo.prototype.render=function(e){var t=this._internalRoot;if(t===null)throw Error(u(409));Fs(e,t,null,null)},Bs.prototype.unmount=Uo.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var t=e.containerInfo;hn(function(){Fs(null,e,null,null)}),t[bt]=null}};function Bs(e){this._internalRoot=e}Bs.prototype.unstable_scheduleHydration=function(e){if(e){var t=Fa();e={blockedOn:null,target:e,priority:t};for(var n=0;n<Ot.length&&t!==0&&t<Ot[n].priority;n++);Ot.splice(n,0,e),n===0&&Ua(e)}};function Wo(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function Us(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function nc(){}function Nm(e,t,n,r,i){if(i){if(typeof r=="function"){var o=r;r=function(){var y=Os(a);o.call(y)}}var a=Zu(t,r,e,0,null,!1,!1,"",nc);return e._reactRootContainer=a,e[bt]=a.current,mr(e.nodeType===8?e.parentNode:e),hn(),a}for(;i=e.lastChild;)e.removeChild(i);if(typeof r=="function"){var d=r;r=function(){var y=Os(m);d.call(y)}}var m=Oo(e,0,!1,null,null,!1,!1,"",nc);return e._reactRootContainer=m,e[bt]=m.current,mr(e.nodeType===8?e.parentNode:e),hn(function(){Fs(t,m,n,r)}),m}function Ws(e,t,n,r,i){var o=n._reactRootContainer;if(o){var a=o;if(typeof i=="function"){var d=i;i=function(){var m=Os(a);d.call(m)}}Fs(t,a,e,i)}else a=Nm(n,t,e,i,r);return Os(a)}Ia=function(e){switch(e.tag){case 3:var t=e.stateNode;if(t.current.memoizedState.isDehydrated){var n=Yn(t.pendingLanes);n!==0&&(di(t,n|1),Ge(t,Ce()),(ne&6)===0&&(Wn=Ce()+500,Ht()))}break;case 13:hn(function(){var r=Lt(e,1);if(r!==null){var i=We();kt(r,e,1,i)}}),Bo(e,1)}},mi=function(e){if(e.tag===13){var t=Lt(e,134217728);if(t!==null){var n=We();kt(t,e,134217728,n)}Bo(e,134217728)}},za=function(e){if(e.tag===13){var t=Yt(e),n=Lt(e,t);if(n!==null){var r=We();kt(n,e,t,r)}Bo(e,t)}},Fa=function(){return ae},Oa=function(e,t){var n=ae;try{return ae=e,t()}finally{ae=n}},si=function(e,t,n){switch(t){case"input":if(qs(e,n),t=n.name,n.type==="radio"&&t!=null){for(n=e;n.parentNode;)n=n.parentNode;for(n=n.querySelectorAll("input[name="+JSON.stringify(""+t)+'][type="radio"]'),t=0;t<n.length;t++){var r=n[t];if(r!==e&&r.form===e.form){var i=is(r);if(!i)throw Error(u(90));ua(r),qs(r,i)}}}break;case"textarea":ha(e,n);break;case"select":t=n.value,t!=null&&kn(e,!!n.multiple,t,!1)}},Sa=Ro,Na=hn;var Cm={usingClientEntryPoint:!1,Events:[pr,Pn,is,wa,ja,Ro]},Pr={findFiberByHostInstance:on,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},_m={bundleType:Pr.bundleType,version:Pr.version,rendererPackageName:Pr.rendererPackageName,rendererConfig:Pr.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:le.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=ba(e),e===null?null:e.stateNode},findFiberByHostInstance:Pr.findFiberByHostInstance||Sm,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Vs=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Vs.isDisabled&&Vs.supportsFiber)try{Br=Vs.inject(_m),jt=Vs}catch{}}return Xe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Cm,Xe.createPortal=function(e,t){var n=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!Wo(t))throw Error(u(200));return jm(e,t,null,n)},Xe.createRoot=function(e,t){if(!Wo(e))throw Error(u(299));var n=!1,r="",i=tc;return t!=null&&(t.unstable_strictMode===!0&&(n=!0),t.identifierPrefix!==void 0&&(r=t.identifierPrefix),t.onRecoverableError!==void 0&&(i=t.onRecoverableError)),t=Oo(e,1,!1,null,null,n,!1,r,i),e[bt]=t.current,mr(e.nodeType===8?e.parentNode:e),new Uo(t)},Xe.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var t=e._reactInternals;if(t===void 0)throw typeof e.render=="function"?Error(u(188)):(e=Object.keys(e).join(","),Error(u(268,e)));return e=ba(t),e=e===null?null:e.stateNode,e},Xe.flushSync=function(e){return hn(e)},Xe.hydrate=function(e,t,n){if(!Us(t))throw Error(u(200));return Ws(null,e,t,!0,n)},Xe.hydrateRoot=function(e,t,n){if(!Wo(e))throw Error(u(405));var r=n!=null&&n.hydratedSources||null,i=!1,o="",a=tc;if(n!=null&&(n.unstable_strictMode===!0&&(i=!0),n.identifierPrefix!==void 0&&(o=n.identifierPrefix),n.onRecoverableError!==void 0&&(a=n.onRecoverableError)),t=Zu(t,null,e,1,n??null,i,!1,o,a),e[bt]=t.current,mr(e),r)for(e=0;e<r.length;e++)n=r[e],i=n._getVersion,i=i(n._source),t.mutableSourceEagerHydrationData==null?t.mutableSourceEagerHydrationData=[n,i]:t.mutableSourceEagerHydrationData.push(n,i);return new Bs(t)},Xe.render=function(e,t,n){if(!Us(t))throw Error(u(200));return Ws(null,e,t,!1,n)},Xe.unmountComponentAtNode=function(e){if(!Us(e))throw Error(u(40));return e._reactRootContainer?(hn(function(){Ws(null,null,e,!1,function(){e._reactRootContainer=null,e[bt]=null})}),!0):!1},Xe.unstable_batchedUpdates=Ro,Xe.unstable_renderSubtreeIntoContainer=function(e,t,n,r){if(!Us(n))throw Error(u(200));if(e==null||e._reactInternals===void 0)throw Error(u(38));return Ws(e,t,n,!1,r)},Xe.version="18.3.1-next-f1338f8080-20240426",Xe}var dc;function Im(){if(dc)return Ho.exports;dc=1;function l(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(l)}catch(c){console.error(c)}}return l(),Ho.exports=Am(),Ho.exports}var mc;function zm(){if(mc)return $s;mc=1;var l=Im();return $s.createRoot=l.createRoot,$s.hydrateRoot=l.hydrateRoot,$s}var Fm=zm();class Om extends Error{constructor(u,g){super(u);rc(this,"status");this.status=g}}async function ct(l,c){const u=await fetch(l,{credentials:"same-origin",headers:{"Content-Type":"application/json",...c==null?void 0:c.headers},cache:"no-store",...c}),g=await u.json().catch(()=>({}));if(!u.ok)throw new Om(g.error||u.statusText||"Request failed",u.status);return g}const Bm=()=>ct("/auth/status"),Um=()=>ct("/api/config"),Cc=()=>ct("/api/botstats"),Wm=()=>ct("/api/commands"),Vm=()=>ct("/api/guilds"),$m=()=>ct("/api/me/overview"),Hm=l=>ct(`/api/guild/${l}/overview`),Qm=l=>ct(`/api/guild/${l}/economy`),Km=l=>ct(`/api/guild/${l}/levels`),fc=l=>ct(`/api/guild/${l}/config`),hc=l=>ct(`/api/guild/${l}/resources`);function sa(l,c,u,g){return ct(`/api/guild/${l}/config/${c}`,{method:"POST",headers:g?{"X-CSRF-Token":g}:void 0,body:JSON.stringify(u)})}function _c(l){return l.replace(/\/+$/,"")||"/"}function pc(l=window.location.pathname){const c=_c(l);return c==="/commands"?"commands":c==="/docs"?"docs":c.startsWith("/docs/")?"docs-detail":c==="/dashboard"||c.startsWith("/dashboard/")?"dashboard":c==="/privacy"?"privacy":c==="/terms"?"terms":"home"}function Tr(l,c="overview"){return l?`/dashboard/${l}/${c}`:"/dashboard"}function gc(){return"/dashboard/servers"}function vc(){const l=_c(window.location.pathname).split("/").filter(Boolean),c=["overview","economy","leveling","moderation","ai"];return l[1]==="servers"?{view:"servers",guildId:null,section:"overview"}:l[1]?{view:"guild",guildId:l[1]||null,section:c.includes(l[2])?l[2]:"overview"}:{view:"overview",guildId:null,section:"overview"}}function ge(l){l.startsWith("/")&&(window.history.pushState({},"",l),window.dispatchEvent(new PopStateEvent("popstate")),window.scrollTo({top:0,behavior:"smooth"}))}function Ks({onNavigate:l}){return s.jsxs("a",{className:"brand",href:"/",onClick:c=>{c.preventDefault(),l?l():ge("/")},children:[s.jsx("span",{className:"brand-mark",children:"n"}),s.jsx("span",{children:"niko"})]})}function $n(){return s.jsxs("footer",{className:"site-footer",children:[s.jsx(Ks,{}),s.jsx("span",{children:"Built for communities that care."}),s.jsxs("div",{children:[s.jsx("a",{href:"/privacy",onClick:l=>{l.preventDefault(),ge("/privacy")},children:"Privacy"}),s.jsx("a",{href:"/terms",onClick:l=>{l.preventDefault(),ge("/terms")},children:"Terms"}),s.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"GitHub"})]})]})}let yc=null,Go=null;function Gs(){const[l,c]=I.useState(yc);return I.useEffect(()=>{Go||(Go=Um().then(u=>yc=u)),Go.then(c).catch(()=>{})},[]),l}/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ec=(...l)=>l.filter((c,u,g)=>!!c&&c.trim()!==""&&g.indexOf(c)===u).join(" ").trim();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Gm=l=>l.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Xm=l=>l.replace(/^([A-Z])|[\s-_]+(\w)/g,(c,u,g)=>g?g.toUpperCase():u.toLowerCase());/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kc=l=>{const c=Xm(l);return c.charAt(0).toUpperCase()+c.slice(1)};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var Xo={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const qm=l=>{for(const c in l)if(c.startsWith("aria-")||c==="role"||c==="title")return!0;return!1},Ym=I.createContext({}),Jm=()=>I.useContext(Ym),Zm=I.forwardRef(({color:l,size:c,strokeWidth:u,absoluteStrokeWidth:g,className:k="",children:P,iconNode:M,...U},x)=>{const{size:z=24,strokeWidth:b=2,absoluteStrokeWidth:A=!1,color:L="currentColor",className:K=""}=Jm()??{},w=g??A?Number(u??b)*24/Number(c??z):u??b;return I.createElement("svg",{ref:x,...Xo,width:c??z??Xo.width,height:c??z??Xo.height,stroke:l??L,strokeWidth:w,className:Ec("lucide",K,k),...!P&&!qm(U)&&{"aria-hidden":"true"},...U},[...M.map(([T,$])=>I.createElement(T,$)),...Array.isArray(P)?P:[P]])});/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const qe=(l,c)=>{const u=I.forwardRef(({className:g,...k},P)=>I.createElement(Zm,{ref:P,iconNode:c,className:Ec(`lucide-${Gm(kc(l))}`,`lucide-${l}`,g),...k}));return u.displayName=kc(l),u};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ef=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]],tf=qe("arrow-right",ef);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const nf=[["path",{d:"M12 5v16",key:"1f6ucr"}],["path",{d:"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z",key:"1fyvmf"}]],xc=qe("book-open",nf);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const rf=[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],qo=qe("chart-column",rf);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const sf=[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]],of=qe("external-link",sf);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const af=[["rect",{width:"7",height:"7",x:"3",y:"3",rx:"1",key:"1g98yp"}],["rect",{width:"7",height:"7",x:"14",y:"3",rx:"1",key:"6d4xhi"}],["rect",{width:"7",height:"7",x:"14",y:"14",rx:"1",key:"nxv5o0"}],["rect",{width:"7",height:"7",x:"3",y:"14",rx:"1",key:"1bb6yr"}]],Zo=qe("layout-grid",af);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const lf=[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]],uf=qe("lock-keyhole",lf);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const cf=[["path",{d:"M4 5h16",key:"1tepv9"}],["path",{d:"M4 12h16",key:"1lakjw"}],["path",{d:"M4 19h16",key:"1djgab"}]],df=qe("menu",cf);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const mf=[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]],ff=qe("search",mf);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const hf=[["path",{d:"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915",key:"1i5ecw"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]],Hs=qe("settings",hf);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const pf=[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}]],Yo=qe("shield",pf);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const gf=[["path",{d:"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",key:"1s2grr"}],["path",{d:"M20 2v4",key:"1rf3ol"}],["path",{d:"M22 4h-4",key:"gwowj6"}],["circle",{cx:"4",cy:"20",r:"2",key:"6kqj1y"}]],Qs=qe("sparkles",gf);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const vf=[["path",{d:"M12 19h8",key:"baeox8"}],["path",{d:"m4 17 6-6-6-6",key:"1yngyt"}]],yf=qe("terminal",vf);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kf=[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["path",{d:"M16 3.128a4 4 0 0 1 0 7.744",key:"16gr8j"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}]],wc=qe("users",kf);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const xf=[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]],wf=qe("x",xf),jf={arrow:tf,grid:Zo,terminal:yf,chart:qo,shield:Yo,spark:Qs,users:wc,settings:Hs,book:xc,external:of,menu:df,close:wf,lock:uf,search:ff,doc:xc,utility:Hs,icon_home:Zo,icon_settings:Hs,icon_economy:qo,icon_leveling:qo,icon_moderation:Yo,icon_automod:Yo,icon_heart:Qs,icon_utility:Hs,icon_bot:wc,icon_ai:Qs,icon_lightbulb:Qs};function Y({name:l,size:c,className:u=""}){const g=jf[l]||Zo;return s.jsx(g,{className:`icon ${u}`.trim(),"aria-hidden":"true",focusable:"false",strokeWidth:1.8,style:c?{width:c,height:c}:void 0})}function nn({page:l}){const c=Gs();return s.jsxs("header",{className:"site-header",children:[s.jsx(Ks,{}),s.jsxs("nav",{className:"site-nav","aria-label":"Main navigation",children:[s.jsx("a",{className:l==="home"?"active":"","aria-current":l==="home"?"page":void 0,href:"/",onClick:u=>{u.preventDefault(),ge("/")},children:"Home"}),s.jsx("a",{className:l==="commands"?"active":"","aria-current":l==="commands"?"page":void 0,href:"/commands",onClick:u=>{u.preventDefault(),ge("/commands")},children:"Commands"}),s.jsx("a",{className:l==="docs"?"active":"","aria-current":l==="docs"?"page":void 0,href:"/docs",onClick:u=>{u.preventDefault(),ge("/docs")},children:"Docs"})]}),s.jsxs("div",{className:"header-actions",children:[s.jsxs("a",{className:"button button-small button-muted dashboard-link",href:"/dashboard",onClick:u=>{u.preventDefault(),ge("/dashboard")},children:["Dashboard ",s.jsx(Y,{name:"arrow"})]}),s.jsx("a",{className:"button button-small button-primary",href:(c==null?void 0:c.invite_url)||"#",target:"_blank",rel:"noreferrer",children:"Add to Discord"})]})]})}const Sf=[{value:"all",label:"All commands"},{value:"slash",label:"Slash"},{value:"prefix",label:"Prefix"},{value:"hybrid",label:"Hybrid"},{value:"context",label:"Context menus"}],ea={slash:"Slash command",prefix:"Prefix command",hybrid:"Hybrid command",context:"Context menu"};function Lr(l){return l.type&&l.type in ea?l.type:"slash"}function Nf(l){return l.context_type==="user"?"Right-click a user":"Right-click a message"}function Cf(l){const c=Lr(l);return c==="slash"?s.jsxs("code",{children:["/",l.name]}):c==="prefix"?s.jsxs("code",{children:[".",l.name]}):c==="hybrid"?s.jsxs(s.Fragment,{children:[s.jsxs("code",{children:["/",l.name]}),s.jsx("span",{className:"command-or",children:"or"}),s.jsxs("code",{children:[".",l.name]})]}):s.jsxs("code",{className:"context-invocation",children:[Nf(l)," · ",l.name]})}function _f(){const[l,c]=I.useState([]),[u,g]=I.useState(""),[k,P]=I.useState("all"),[M,U]=I.useState("all"),[x,z]=I.useState(!0),[b,A]=I.useState("");I.useEffect(()=>{Wm().then(c).catch(()=>A("The command registry is unavailable right now.")).finally(()=>z(!1))},[]);const L=I.useMemo(()=>["all",...Array.from(new Set(l.map(w=>w.category))).sort()],[l]),K=l.filter(w=>{const T=`${w.name} ${w.description} ${w.category} ${ea[Lr(w)]} ${w.context_type||""}`.toLowerCase();return(M==="all"||Lr(w)===M)&&(k==="all"||w.category===k)&&T.includes(u.trim().toLowerCase())});return s.jsxs(s.Fragment,{children:[s.jsx(nn,{page:"commands"}),s.jsxs("main",{className:"shell page-main",children:[s.jsxs("div",{className:"page-heading",children:[s.jsx("div",{className:"eyebrow",children:"Reference library"}),s.jsxs("h1",{children:["Everything Niko",s.jsx("br",{}),s.jsx("em",{children:"knows how to do."})]}),s.jsx("p",{children:"Browse slash, prefix, hybrid, and context commands from the live bot registry. Search by name, description, or category."})]}),s.jsxs("div",{className:"command-toolbar",children:[s.jsxs("label",{className:"search-field",children:[s.jsx("span",{"aria-hidden":"true",children:"⌕"}),s.jsx("input",{value:u,onChange:w=>g(w.target.value),placeholder:"Search commands","aria-label":"Search commands"})]}),s.jsxs("div",{className:"command-filters",children:[s.jsx("div",{className:"filter-list","aria-label":"Command types",children:Sf.map(w=>s.jsx("button",{type:"button",className:M===w.value?"filter active":"filter","aria-pressed":M===w.value,onClick:()=>U(w.value),children:w.label},w.value))}),s.jsx("div",{className:"filter-list","aria-label":"Command categories",children:L.map(w=>s.jsx("button",{type:"button",className:k===w?"filter active":"filter","aria-pressed":k===w,onClick:()=>P(w),children:w==="all"?"All categories":w},w))})]})]}),s.jsxs("div",{className:"command-meta",children:[s.jsx("strong",{children:x?"…":K.length})," commands ",s.jsx("span",{children:"·"})," live bot registry"]}),b&&s.jsxs("div",{className:"inline-error",role:"alert",children:[s.jsx("strong",{children:"Could not load commands"}),s.jsx("span",{children:b})]}),s.jsxs("div",{className:"commands-grid",children:[K.map(w=>s.jsxs("article",{className:"command-card",children:[s.jsxs("div",{className:"command-card-head",children:[s.jsx("div",{className:"command-name",children:Cf(w)}),s.jsx("span",{className:"command-type",children:ea[Lr(w)]})]}),s.jsx("p",{children:w.description||"A Niko command for your server."}),s.jsx("span",{className:"category-tag",children:w.category})]},`${Lr(w)}-${w.context_type||""}-${w.category}-${w.name}`)),!x&&!b&&!K.length&&s.jsx("div",{className:"empty-state",children:"No commands match that search."})]})]}),s.jsx($n,{})]})}function ke(l){return l==null?"—":new Intl.NumberFormat("en-US",{notation:l>9999?"compact":"standard"}).format(l)}function ta(l){return(l==null?void 0:l.global_name)||(l==null?void 0:l.username)||"there"}function bc(l){return l.split(/\s+/).map(c=>c[0]).join("").slice(0,2).toUpperCase()}function ia({guild:l,className:c="guild-avatar"}){return s.jsx("span",{className:c,"aria-hidden":"true",children:l.icon_url?s.jsx("img",{src:l.icon_url,alt:""}):l.name.slice(0,1).toUpperCase()})}function Pc({user:l,className:c="avatar"}){const u=l.avatar?`https://cdn.discordapp.com/avatars/${l.id}/${l.avatar}.${l.avatar.startsWith("a_")?"gif":"png"}?size=64`:null;return s.jsx("span",{className:c,"aria-hidden":"true",children:u?s.jsx("img",{src:u,alt:""}):bc(l.global_name||l.username||"Niko")})}function Mc({name:l,avatarUrl:c,className:u="member-avatar"}){return s.jsx("span",{className:u,"aria-hidden":"true",children:c?s.jsx("img",{src:c,alt:""}):bc(l)})}const jc=[["overview","Overview","grid","At a glance"],["economy","Economy","chart","Member momentum"],["leveling","Leveling","spark","Reward participation"],["moderation","Moderation","shield","Keep things steady"],["ai","AI controls","settings","Shape Niko’s voice"]];function Ef({user:l,guilds:c,selectedGuild:u,view:g,section:k,stats:P,onHome:M,onServers:U,onGuildChange:x,onSectionChange:z,children:b}){var $;const A=c.filter(q=>q.installed!==!1),L=(q=!1)=>s.jsx("nav",{className:q?"dash-nav dash-nav-mobile":"dash-nav","aria-label":"Server settings",children:jc.map(([me,ue,le])=>s.jsxs("button",{className:g==="guild"&&k===me?"active":"","aria-current":g==="guild"&&k===me?"page":void 0,onClick:()=>z(me),children:[s.jsx(Y,{name:le}),s.jsx("span",{children:ue})]},me))}),K=(q=!1)=>s.jsxs("nav",{className:q?"dash-nav dash-primary-nav dash-nav-mobile":"dash-nav dash-primary-nav","aria-label":"Dashboard",children:[s.jsxs("button",{className:g==="overview"?"active":"","aria-current":g==="overview"?"page":void 0,onClick:M,children:[s.jsx(Y,{name:"grid"}),s.jsx("span",{children:"My overview"})]}),s.jsxs("button",{className:g==="servers"?"active":"","aria-current":g==="servers"?"page":void 0,onClick:U,children:[s.jsx(Y,{name:"users"}),s.jsx("span",{children:"My servers"})]})]}),w=g==="overview"?`Welcome, ${ta(l)}`:g==="servers"?"Your servers":(u==null?void 0:u.name)||"Server settings",T=g==="guild"?"Managing server":"Niko dashboard";return s.jsxs("div",{className:"dashboard-layout",children:[s.jsxs("aside",{className:"dash-sidebar",children:[s.jsx(Ks,{onNavigate:M}),s.jsxs("div",{className:"side-rail-heading",children:[s.jsx("span",{className:"side-label",children:"Workspace"}),s.jsxs("span",{className:"rail-status",children:[s.jsx("span",{className:"status-dot"})," Live"]})]}),K(),g==="guild"&&u&&s.jsxs(s.Fragment,{children:[s.jsx("div",{className:"side-label side-label-settings",children:"Current server"}),s.jsxs("div",{className:"side-guild",children:[s.jsx(ia,{guild:u}),s.jsxs("span",{children:[s.jsx("strong",{children:u.name}),s.jsx("small",{children:"Live configuration"})]}),s.jsx("span",{className:"guild-presence",title:"Niko is connected",children:s.jsx("span",{className:"status-dot"})})]}),s.jsxs("div",{className:"side-settings-caption",children:[s.jsx("span",{children:"Settings map"}),s.jsx("small",{children:"Pick a room to tune"})]}),L()]}),g!=="guild"&&s.jsxs("div",{className:"side-rail-note",children:[s.jsx("span",{className:"panel-kicker",children:"Niko workspace"}),s.jsxs("strong",{children:["Make the useful",s.jsx("br",{}),"things easier to find."]}),s.jsx("small",{children:"Your servers and their live signals, in one quiet place."})]}),s.jsxs("div",{className:"sidebar-bottom",children:[s.jsxs("span",{className:"online-label",children:[s.jsx("span",{className:"status-dot"})," Niko is online"]}),s.jsxs("small",{children:[ke(P==null?void 0:P.guild_count)," connected servers · v",(P==null?void 0:P.version)||"1.0"]}),s.jsxs("a",{href:"/",onClick:q=>{q.preventDefault(),ge("/")},children:["Back to public site ",s.jsx(Y,{name:"arrow"})]})]})]}),s.jsxs("div",{className:"dash-content",children:[s.jsxs("header",{className:"dash-topbar",children:[s.jsxs("div",{className:"mobile-top-row",children:[s.jsx("span",{className:"mobile-brand",children:s.jsx(Ks,{})}),s.jsxs("span",{className:"mobile-status",children:[s.jsx("span",{className:"status-dot"})," Online"]})]}),s.jsxs("div",{className:"dash-title",children:[s.jsxs("span",{className:"dash-overline",children:[T," ",s.jsx("span",{className:"dash-title-divider",children:"/"})," ",g==="guild"?($=jc.find(([q])=>q===k))==null?void 0:$[1]:"Workspace"]}),s.jsx("h1",{children:w})]}),s.jsxs("div",{className:"dash-top-actions",children:[g==="guild"?s.jsxs("label",{className:"guild-switcher",children:[s.jsx("span",{className:"sr-only",children:"Switch server"}),s.jsxs("select",{value:(u==null?void 0:u.id)||"",onChange:q=>{const me=A.find(ue=>ue.id===q.target.value);me&&x(me)},children:[s.jsx("option",{value:"",disabled:!0,children:"Switch server"}),A.map(q=>s.jsx("option",{value:q.id,children:q.name},q.id))]})]}):s.jsxs("button",{className:"button button-muted button-small top-action",onClick:U,children:[s.jsx(Y,{name:"users"})," Browse servers"]}),g==="guild"&&s.jsxs("span",{className:"connection-chip",children:[s.jsx("span",{className:"status-dot"})," Connected"]}),s.jsxs("div",{className:"user-pill",children:[s.jsx(Pc,{user:l}),s.jsx("span",{children:ta(l)})]}),s.jsx("a",{className:"logout-link",href:"/auth/logout",children:"Log out"})]})]}),s.jsx("div",{className:"mobile-primary-bar",children:K(!0)}),g==="guild"&&s.jsx("div",{className:"mobile-section-bar",children:L(!0)}),s.jsx("main",{className:"dash-main",children:b})]})]})}function yn({eyebrow:l,title:c,text:u}){return s.jsxs("div",{className:"dash-heading",children:[s.jsxs("div",{className:"heading-meta",children:[s.jsx("div",{className:"eyebrow",children:l}),s.jsx("span",{className:"heading-context",children:"NIKO / CONTROL ROOM"})]}),s.jsx("h2",{children:c}),s.jsx("p",{children:u})]})}function ut({label:l,value:c,note:u,accent:g=""}){return s.jsxs("div",{className:`dash-stat ${g}`,children:[s.jsx("span",{children:l}),s.jsx("strong",{children:c}),s.jsx("small",{children:u})]})}function bf({user:l,overview:c,guilds:u,onServers:g,onManage:k}){const P=u.filter(M=>M.installed!==!1);return s.jsxs(s.Fragment,{children:[s.jsx(yn,{eyebrow:"Personal overview",title:"Your Niko snapshot.",text:"Keep an eye on your progress, then jump into a server when you’re ready to tune the room."}),s.jsxs("div",{className:"overview-intro",children:[s.jsxs("div",{className:"profile-card",children:[s.jsx(Pc,{user:l,className:"profile-avatar"}),s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Signed in as"}),s.jsx("h3",{children:ta(l)}),s.jsx("p",{children:"Personal economy profile"})]})]}),s.jsxs("button",{className:"button button-primary",onClick:g,children:["Manage a server ",s.jsx(Y,{name:"arrow"})]})]}),s.jsxs("div",{className:"dash-stats overview-stats",children:[s.jsx(ut,{label:"Net worth",value:ke(c==null?void 0:c.net_worth),note:"Across your Niko profile",accent:"accent-orange"}),s.jsx(ut,{label:"In your wallet",value:ke(c==null?void 0:c.balance),note:"Ready to spend",accent:"accent-violet"}),s.jsx(ut,{label:"In your vault",value:ke(c==null?void 0:c.bank),note:"Saved for later",accent:"accent-blue"}),s.jsx(ut,{label:"Current level",value:ke(c==null?void 0:c.level),note:c!=null&&c.job?`Working as a ${c.job}`:"Keep showing up",accent:"accent-green"})]}),s.jsxs("div",{className:"dash-columns overview-columns",children:[s.jsxs("section",{className:"dash-panel",children:[s.jsxs("div",{className:"panel-heading",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Progress"}),s.jsx("h3",{children:"Your momentum"})]}),s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:"spark"})})]}),s.jsxs("div",{className:"metric-list",children:[s.jsxs("div",{children:[s.jsx("span",{children:"Daily streak"}),s.jsxs("strong",{children:[ke(c==null?void 0:c.daily_streak)," ",s.jsx("small",{children:"days"})]})]}),s.jsxs("div",{children:[s.jsx("span",{children:"Achievements"}),s.jsxs("strong",{children:[ke(c==null?void 0:c.achievements)," ",s.jsx("small",{children:"unlocked"})]})]}),s.jsxs("div",{children:[s.jsx("span",{children:"Total earned"}),s.jsxs("strong",{children:[ke(c==null?void 0:c.total_earned)," ",s.jsx("small",{children:"coins"})]})]}),s.jsxs("div",{children:[s.jsx("span",{children:"Economy standing"}),s.jsxs("strong",{children:[c!=null&&c.economy_rank?`#${ke(c.economy_rank)}`:"—"," ",s.jsx("small",{children:c!=null&&c.economy_profiles?`of ${ke(c.economy_profiles)}`:""})]})]})]})]}),s.jsxs("section",{className:"dash-panel",children:[s.jsxs("div",{className:"panel-heading",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Quick access"}),s.jsx("h3",{children:"Your servers"})]}),s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:"users"})})]}),s.jsxs("div",{className:"mini-server-list",children:[P.slice(0,4).map(M=>s.jsxs("button",{onClick:()=>k(M),children:[s.jsx(ia,{guild:M}),s.jsx("span",{children:M.name}),s.jsx(Y,{name:"arrow"})]},M.id)),!P.length&&s.jsx("p",{className:"empty-state compact",children:"Add Niko to a server to start managing it."})]}),s.jsxs("button",{className:"text-link overview-link",onClick:g,children:["View all servers ",s.jsx(Y,{name:"arrow"})]})]})]})]})}function Sc({guild:l,onManage:c}){const u=l.installed!==!1;return s.jsxs("article",{className:"server-card",children:[s.jsxs("div",{className:"server-card-heading",children:[s.jsx(ia,{guild:l,className:"server-avatar"}),s.jsx("span",{className:"server-status",children:u?"Niko is installed":"Ready to add"})]}),s.jsx("h3",{children:l.name}),s.jsx("p",{children:u?"Open the dashboard to manage Niko’s features and settings.":"You have permission to manage this server. Add Niko to unlock its controls."}),u?s.jsxs("button",{className:"button button-muted button-small",onClick:()=>c(l),children:["Open settings ",s.jsx(Y,{name:"arrow"})]}):s.jsxs("a",{className:"button button-primary button-small",href:l.invite_url||"#",target:"_blank",rel:"noreferrer",children:["Add Niko ",s.jsx(Y,{name:"external"})]})]})}function Pf({guilds:l,onManage:c}){const u=l.filter(k=>k.installed!==!1),g=l.filter(k=>k.installed===!1);return s.jsxs(s.Fragment,{children:[s.jsx(yn,{eyebrow:"Servers",title:"Choose where to work.",text:"Manage servers with Niko already installed, or add Niko to another server you can administer."}),s.jsxs("div",{className:"server-summary",children:[s.jsxs("div",{children:[s.jsx("strong",{children:ke(u.length)}),s.jsx("span",{children:"Connected to Niko"})]}),s.jsxs("div",{children:[s.jsx("strong",{children:ke(g.length)}),s.jsx("span",{children:"Ready to add"})]}),s.jsxs("div",{className:"server-summary-note",children:[s.jsx(Y,{name:"shield"}),s.jsx("span",{children:"Only servers where you have Manage Server access are shown."})]})]}),s.jsxs("section",{className:"server-section",children:[s.jsxs("div",{className:"section-heading-row",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Connected"}),s.jsx("h3",{children:"Manage a server"})]}),s.jsx("span",{className:"section-count",children:u.length})]}),s.jsxs("div",{className:"server-grid",children:[u.map(k=>s.jsx(Sc,{guild:k,onManage:c},k.id)),!u.length&&s.jsxs("div",{className:"empty-state",children:[s.jsx("strong",{children:"No connected servers yet."}),s.jsx("span",{children:"Add Niko below, then come back here to manage it."})]})]})]}),s.jsxs("section",{className:"server-section",children:[s.jsxs("div",{className:"section-heading-row",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Available to you"}),s.jsx("h3",{children:"Add Niko to a server"})]}),s.jsx("span",{className:"section-count",children:g.length})]}),s.jsxs("div",{className:"server-grid",children:[g.map(k=>s.jsx(Sc,{guild:k,onManage:c},k.id)),!g.length&&s.jsx("div",{className:"server-note",children:"Niko is already installed in every server you can manage."})]})]})]})}function na({rows:l,type:c}){return s.jsxs("div",{className:"rank-list",children:[l.slice(0,5).map((u,g)=>s.jsxs("div",{className:"rank-row",children:[s.jsx("span",{className:`rank rank-${g+1}`,children:String(g+1).padStart(2,"0")}),s.jsxs("span",{className:"rank-user",children:[s.jsx(Mc,{name:u.display_name||u.username||"Unknown member",avatarUrl:u.avatar_url}),s.jsxs("span",{children:[s.jsx("strong",{children:u.display_name||u.username||"Unknown member"}),u.username&&u.display_name&&s.jsxs("small",{children:["@",u.username]})]})]}),s.jsxs("strong",{children:[ke(c==="coins"?u.net_worth:u.xp),s.jsx("small",{children:c==="coins"?" coins":" xp"})]})]},`${u.user_id}-${g}`)),!l.length&&s.jsx("div",{className:"empty-state compact",children:"No data recorded yet."})]})}function Mf({overview:l}){return s.jsxs(s.Fragment,{children:[s.jsxs("div",{className:"guild-welcome",children:[s.jsxs("div",{children:[s.jsx("span",{className:"welcome-mark",children:s.jsx(Y,{name:"grid"})}),s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Server pulse"}),s.jsx("strong",{children:"Here’s what needs your attention."})]})]}),s.jsxs("span",{className:"welcome-time",children:["LIVE SIGNALS ",s.jsx("span",{className:"status-dot"})]})]}),s.jsx(yn,{eyebrow:"Overview",title:"A quick read on your room.",text:"The important signals, without making you hunt for them."}),s.jsxs("div",{className:"dash-stats guild-overview-stats",children:[s.jsx(ut,{label:"Economy in circulation",value:ke(l.economy.total_coins),note:`${ke(l.economy.user_count)} active profiles`,accent:"accent-orange"}),s.jsx(ut,{label:"Warnings logged",value:ke(l.moderation.warn_count),note:"For this server",accent:"accent-blue"}),s.jsx(ut,{label:"Automod",value:l.moderation.automod_active?"Active":"Quiet",note:"Protection status",accent:"accent-green"})]}),s.jsxs("div",{className:"dash-columns",children:[s.jsxs("section",{className:"dash-panel",children:[s.jsxs("div",{className:"panel-heading",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Community economy"}),s.jsx("h3",{children:"Top net worth"})]}),s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:"chart"})})]}),s.jsx(na,{rows:l.economy.top,type:"coins"})]}),s.jsxs("section",{className:"dash-panel",children:[s.jsxs("div",{className:"panel-heading",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Community energy"}),s.jsx("h3",{children:"Top XP"})]}),s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:"spark"})})]}),s.jsx(na,{rows:l.leveling.top,type:"xp"})]})]})]})}function Tf({rows:l}){const c=l.reduce((u,g)=>u+g.net_worth,0);return s.jsxs(s.Fragment,{children:[s.jsx(yn,{eyebrow:"Economy",title:"Give members something to build.",text:"A snapshot of the café economy and its most active players."}),s.jsxs("div",{className:"dash-stats",children:[s.jsx(ut,{label:"Tracked net worth",value:ke(c),note:"Top 25 profiles",accent:"accent-orange"}),s.jsx(ut,{label:"Profiles",value:ke(l.length),note:"With economy data",accent:"accent-violet"})]}),s.jsxs("section",{className:"dash-panel",children:[s.jsxs("div",{className:"panel-heading",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Leaderboard"}),s.jsx("h3",{children:"Net worth"})]}),s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:"chart"})})]}),s.jsxs("div",{className:"wide-table",role:"table","aria-label":"Economy leaderboard",children:[s.jsxs("div",{className:"table-head",role:"row",children:[s.jsx("span",{children:"Rank"}),s.jsx("span",{children:"Member"}),s.jsx("span",{children:"Job"}),s.jsx("span",{children:"Level"}),s.jsx("span",{children:"Net worth"})]}),l.map((u,g)=>{const k=u.display_name||u.username||"Unknown member";return s.jsxs("div",{className:"table-row",role:"row",children:[s.jsx("span",{className:"rank",children:String(g+1).padStart(2,"0")}),s.jsxs("span",{className:"table-member",children:[s.jsx(Mc,{name:k,avatarUrl:u.avatar_url}),s.jsxs("span",{children:[s.jsx("strong",{children:k}),u.username&&u.display_name&&s.jsxs("small",{children:["@",u.username]})]})]}),s.jsx("span",{className:"muted",children:u.job}),s.jsx("span",{children:u.level}),s.jsx("strong",{children:ke(u.net_worth)})]},u.user_id)})]})]})]})}function Lf({rows:l,config:c,resources:u,csrfToken:g,guildId:k}){var P,M,U;return s.jsxs(s.Fragment,{children:[s.jsx(yn,{eyebrow:"Leveling",title:"Momentum people can see.",text:"Track the members turning up, and tune the pace to fit your server."}),s.jsxs("div",{className:"dash-stats",children:[s.jsx(ut,{label:"Top level",value:String(((P=l[0])==null?void 0:P.level)||0),note:((M=l[0])==null?void 0:M.display_name)||((U=l[0])==null?void 0:U.username)||"No members yet",accent:"accent-violet"}),s.jsx(ut,{label:"XP multiplier",value:`${(c==null?void 0:c.leveling.xp_multiplier)||1}×`,note:(c==null?void 0:c.leveling.xp_enabled)===!1?"XP disabled":"Currently active",accent:"accent-blue"}),s.jsx(ut,{label:"Cooldown",value:`${(c==null?void 0:c.leveling.xp_cooldown)||0}s`,note:"Between XP awards",accent:"accent-green"})]}),s.jsxs("section",{className:"dash-panel",children:[s.jsxs("div",{className:"panel-heading",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:"Leaderboard"}),s.jsx("h3",{children:"XP leaders"})]}),s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:"spark"})})]}),s.jsx(na,{rows:l,type:"xp"})]}),s.jsx(Af,{guildId:k,config:c,resources:u,csrfToken:g})]})}const oa={saving:!1,message:"",error:""};function Et({label:l,hint:c,children:u}){return s.jsxs("label",{className:"form-field",children:[s.jsx("span",{className:"form-label",children:l}),u,c&&s.jsx("small",{children:c})]})}function aa({icon:l,label:c,title:u,text:g}){return s.jsxs("div",{className:"settings-intro",children:[s.jsx("span",{className:"settings-intro-icon",children:s.jsx(Y,{name:l})}),s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:c}),s.jsx("strong",{children:u}),s.jsx("p",{children:g})]}),s.jsxs("span",{className:"settings-intro-state",children:[s.jsx("span",{className:"status-dot"})," Per server"]})]})}function Rr({label:l,title:c,detail:u,icon:g}){return s.jsxs("div",{className:"panel-heading settings-section-title",children:[s.jsxs("div",{children:[s.jsx("span",{className:"panel-kicker",children:l}),s.jsx("h3",{children:c}),u&&s.jsx("p",{children:u})]}),g&&s.jsx("span",{className:"panel-icon",children:s.jsx(Y,{name:g})})]})}function la({state:l}){return s.jsxs("div",{className:"setting-footer",children:[l.error?s.jsx("span",{className:"form-error",role:"alert",children:l.error}):s.jsx("span",{role:"status",children:l.message||"Changes apply to this server."}),s.jsx("button",{className:"button button-primary",type:"submit",disabled:l.saving,children:l.saving?"Saving…":"Save changes"})]})}function Rf({guildId:l,config:c,csrfToken:u}){var A,L,K;const[g,k]=I.useState({}),[P,M]=I.useState(oa);I.useEffect(()=>{const w=(c==null?void 0:c.moderation)||{};k({automod:{...w.automod||{}},spam_threshold:w.spam_threshold??6,spam_interval:w.spam_interval??7,max_mentions:w.max_mentions??5,antinuke:{...w.antinuke||{}},antiraid:{...w.antiraid||{}},antiraid_ext:{...w.antiraid_ext||{}}})},[c]);const U=(w,T,$)=>k(q=>({...q,[w]:{...q[w],[T]:$}})),x=w=>{w.preventDefault(),M({saving:!0,message:"",error:""}),sa(l,"automod",g,u).then(T=>{const $=T.config||{};k({automod:{...$.automod||{}},spam_threshold:$.spam_threshold??6,spam_interval:$.spam_interval??7,max_mentions:$.max_mentions??5,antinuke:{...$.antinuke||{}},antiraid:{...$.antiraid||{}},antiraid_ext:{...$.antiraid_ext||{}}}),M({saving:!1,message:"Moderation settings saved to Niko.",error:""})}).catch(T=>M({saving:!1,message:"",error:T instanceof Error?T.message:"Could not save settings."}))},z=[["antispam","Anti-spam","Detect repeated messages"],["antilink","Invite links","Remove Discord invite links"],["badwords","Blocked words","Filter words from the server list"],["massmention","Mass mentions","Limit mention floods"],["antinuke","Anti-nuke","Protect channels and roles"],["antiraid","Join raid protection","React to sudden join waves"],["antiraid_ext","External app protection","Detect user-installed app abuse"]],b=z.filter(([w])=>{var T;return!!((T=g.automod)!=null&&T[w])}).length;return s.jsxs(s.Fragment,{children:[s.jsx(yn,{eyebrow:"Moderation",title:"Keep the room feeling good.",text:"Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration."}),s.jsx(aa,{icon:"shield",label:"Protection desk",title:`${b} of ${z.length} safeguards active`,text:"Start with the essentials, then tune thresholds below when you know the room’s rhythm."}),s.jsxs("form",{onSubmit:x,className:"settings-stack",children:[s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Rr,{label:"Protection rules",title:"AutoMod modules",detail:"Toggle only the responses you want Niko to handle.",icon:"shield"}),s.jsx("div",{className:"setting-list",children:z.map(([w,T,$])=>{var q;return s.jsxs("label",{className:"setting-row",children:[s.jsxs("span",{children:[s.jsx("strong",{children:T}),s.jsx("small",{children:$})]}),s.jsx("input",{type:"checkbox",checked:!!((q=g.automod)!=null&&q[w]),onChange:me=>U("automod",w,me.target.checked)}),s.jsx("i",{"aria-hidden":"true"})]},w)})})]}),s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Rr,{label:"Thresholds",title:"Choose when protection steps in",detail:"These limits apply across the server."}),s.jsxs("div",{className:"form-grid",children:[s.jsx(Et,{label:"Spam messages",hint:"Messages inside the spam interval",children:s.jsx("input",{type:"number",min:"1",max:"100",value:g.spam_threshold??6,onChange:w=>k({...g,spam_threshold:w.target.value})})}),s.jsx(Et,{label:"Spam interval (seconds)",children:s.jsx("input",{type:"number",min:"1",max:"3600",value:g.spam_interval??7,onChange:w=>k({...g,spam_interval:w.target.value})})}),s.jsx(Et,{label:"Maximum mentions",children:s.jsx("input",{type:"number",min:"1",max:"100",value:g.max_mentions??5,onChange:w=>k({...g,max_mentions:w.target.value})})}),s.jsx(Et,{label:"Anti-raid joins",hint:"Joins inside the join interval",children:s.jsx("input",{type:"number",min:"1",max:"1000",value:((A=g.antiraid)==null?void 0:A.join_threshold)??10,onChange:w=>U("antiraid","join_threshold",w.target.value)})}),s.jsx(Et,{label:"Anti-raid interval (seconds)",children:s.jsx("input",{type:"number",min:"1",max:"3600",value:((L=g.antiraid)==null?void 0:L.join_interval)??10,onChange:w=>U("antiraid","join_interval",w.target.value)})}),s.jsx(Et,{label:"Anti-raid action",children:s.jsxs("select",{value:((K=g.antiraid)==null?void 0:K.action)??"kick",onChange:w=>U("antiraid","action",w.target.value),children:[s.jsx("option",{value:"kick",children:"Kick"}),s.jsx("option",{value:"ban",children:"Ban"}),s.jsx("option",{value:"softban",children:"Soft-ban"}),s.jsx("option",{value:"slowmode",children:"Slowmode"}),s.jsx("option",{value:"lockdown",children:"Lockdown"})]})})]}),s.jsx(la,{state:P})]})]})]})}function Df({guildId:l,config:c,csrfToken:u}){const[g,k]=I.useState({personality:"cafe",enabled:!0,ai_actions_experiment:!1,better_context_experiment:!1}),[P,M]=I.useState(oa);I.useEffect(()=>{const x=(c==null?void 0:c.ai)||{};k({personality:x.personality||"cafe",enabled:x.enabled!=="False"&&x.enabled!==!1,ai_actions_experiment:x.ai_actions_experiment===!0||x.ai_actions_experiment==="True",better_context_experiment:x.better_context_experiment===!0||x.better_context_experiment==="True"})},[c]);const U=x=>{x.preventDefault(),M({saving:!0,message:"",error:""}),sa(l,"ai",g,u).then(z=>{const b=z.config||{};k({personality:b.personality==="normal"?"normal":"cafe",enabled:b.enabled!=="False"&&b.enabled!==!1,ai_actions_experiment:b.ai_actions_experiment===!0||b.ai_actions_experiment==="True",better_context_experiment:b.better_context_experiment===!0||b.better_context_experiment==="True"}),M({saving:!1,message:"AI settings saved to Niko.",error:""})}).catch(z=>M({saving:!1,message:"",error:z instanceof Error?z.message:"Could not save settings."}))};return s.jsxs(s.Fragment,{children:[s.jsx(yn,{eyebrow:"AI controls",title:"Give Niko the right tone.",text:"AI is optional, configurable per server, and designed to stay out of the way when the room does not need it."}),s.jsx(aa,{icon:"settings",label:"Conversation desk",title:g.enabled?"Niko is ready to respond":"Niko is staying quiet",text:"Choose a voice that fits your community. You can change this without affecting other servers."}),s.jsxs("form",{onSubmit:U,className:"settings-stack",children:[s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Rr,{label:"Conversation",title:"Core settings",detail:"Decide when Niko joins the conversation.",icon:"settings"}),s.jsxs("label",{className:"setting-row",children:[s.jsxs("span",{children:[s.jsx("strong",{children:"Enable AI chat"}),s.jsx("small",{children:"Respond when Niko is mentioned"})]}),s.jsx("input",{type:"checkbox",checked:g.enabled,onChange:x=>k({...g,enabled:x.target.checked})}),s.jsx("i",{"aria-hidden":"true"})]}),s.jsxs("div",{className:"personality-options",children:[s.jsxs("button",{type:"button",className:g.personality==="cafe"?"personality active":"personality",onClick:()=>k({...g,personality:"cafe"}),children:[s.jsx("span",{className:"personality-mark",children:"n"}),s.jsxs("span",{children:[s.jsx("strong",{children:"Café"}),s.jsx("small",{children:"Warm, playful, familiar"})]})]}),s.jsxs("button",{type:"button",className:g.personality==="normal"?"personality active":"personality",onClick:()=>k({...g,personality:"normal"}),children:[s.jsx("span",{className:"personality-mark",children:"—"}),s.jsxs("span",{children:[s.jsx("strong",{children:"Normal"}),s.jsx("small",{children:"Clear and straightforward"})]})]})]})]}),s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Rr,{label:"Experiments",title:"Optional context",detail:"Try new capabilities when your team is ready."}),s.jsxs("label",{className:"setting-row",children:[s.jsxs("span",{children:[s.jsx("strong",{children:"Better context"}),s.jsx("small",{children:"Use the last five channel messages"})]}),s.jsx("input",{type:"checkbox",checked:g.better_context_experiment,onChange:x=>k({...g,better_context_experiment:x.target.checked})}),s.jsx("i",{"aria-hidden":"true"})]}),s.jsxs("label",{className:"setting-row",children:[s.jsxs("span",{children:[s.jsx("strong",{children:"AI actions"}),s.jsx("small",{children:"Allow confirmed actions requested in chat"})]}),s.jsx("input",{type:"checkbox",checked:g.ai_actions_experiment,onChange:x=>k({...g,ai_actions_experiment:x.target.checked})}),s.jsx("i",{"aria-hidden":"true"})]}),s.jsx(la,{state:P})]})]})]})}function Af({guildId:l,config:c,resources:u,csrfToken:g}){const k=(c==null?void 0:c.leveling)||{},[P,M]=I.useState({xp_enabled:!0,xp_multiplier:1,xp_cooldown:0,level_up_channel:"",level_up_message:""}),[U,x]=I.useState(oa);I.useEffect(()=>M({xp_enabled:k.xp_enabled!==!1,xp_multiplier:k.xp_multiplier??1,xp_cooldown:k.xp_cooldown??0,level_up_channel:k.level_up_channel||"",level_up_message:k.level_up_message||""}),[c]);const z=b=>{b.preventDefault(),x({saving:!0,message:"",error:""}),sa(l,"leveling",P,g).then(A=>{const L=A.config||{};M({xp_enabled:L.xp_enabled!==!1,xp_multiplier:L.xp_multiplier??1,xp_cooldown:L.xp_cooldown??0,level_up_channel:L.level_up_channel||"",level_up_message:L.level_up_message||""}),x({saving:!1,message:"Leveling settings saved to Niko.",error:""})}).catch(A=>x({saving:!1,message:"",error:A instanceof Error?A.message:"Could not save settings."}))};return s.jsxs(s.Fragment,{children:[s.jsx(aa,{icon:"spark",label:"Participation desk",title:P.xp_enabled?"XP is flowing":"XP is paused",text:"Set a pace that rewards regulars without turning every message into a transaction."}),s.jsx("form",{onSubmit:z,className:"settings-stack",children:s.jsxs("section",{className:"dash-panel settings-panel",children:[s.jsx(Rr,{label:"Leveling settings",title:"Shape the pace",detail:"These controls apply to every member in this server.",icon:"spark"}),s.jsxs("label",{className:"setting-row",children:[s.jsxs("span",{children:[s.jsx("strong",{children:"Enable XP"}),s.jsx("small",{children:"Track activity and award levels"})]}),s.jsx("input",{type:"checkbox",checked:P.xp_enabled,onChange:b=>M({...P,xp_enabled:b.target.checked})}),s.jsx("i",{"aria-hidden":"true"})]}),s.jsxs("div",{className:"form-grid",children:[s.jsx(Et,{label:"XP multiplier",hint:"From 0.1× to 10×",children:s.jsx("input",{type:"number",min:"0.1",max:"10",step:"0.1",value:P.xp_multiplier,onChange:b=>M({...P,xp_multiplier:b.target.value})})}),s.jsx(Et,{label:"Cooldown (seconds)",hint:"0 disables the cooldown",children:s.jsx("input",{type:"number",min:"0",max:"86400",value:P.xp_cooldown,onChange:b=>M({...P,xp_cooldown:b.target.value})})}),s.jsx(Et,{label:"Level-up channel",children:s.jsxs("select",{value:P.level_up_channel,onChange:b=>M({...P,level_up_channel:b.target.value}),children:[s.jsx("option",{value:"",children:"Same channel"}),u==null?void 0:u.channels.map(b=>s.jsxs("option",{value:b.id,children:["#",b.name]},b.id))]})}),s.jsx(Et,{label:"Level-up message",hint:"Use {mention}, {level}, {name}, or {guild}",children:s.jsx("textarea",{rows:3,maxLength:1e3,value:P.level_up_message,onChange:b=>M({...P,level_up_message:b.target.value}),placeholder:"Leave blank for Niko's default message"})})]}),s.jsx(la,{state:U})]})})]})}function If({auth:l}){const c=Gs();return s.jsxs(s.Fragment,{children:[s.jsx(nn,{page:"dashboard"}),s.jsx("main",{className:"auth-page",children:s.jsxs("div",{className:"auth-card",children:[s.jsx("span",{className:"auth-mark",children:"n"}),s.jsx("div",{className:"eyebrow",children:"Private workspace"}),s.jsxs("h1",{children:["Settle in, ",s.jsx("em",{children:"admin."})]}),s.jsx("p",{children:"Sign in with Discord to see your Niko profile and manage the servers you look after."}),l.oauth_available?s.jsxs("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard",children:[s.jsx(Y,{name:"lock"})," Continue with Discord ",s.jsx(Y,{name:"arrow"})]}):s.jsxs("div",{className:"notice warning",children:["Discord login is not configured yet. Add ",s.jsx("code",{children:"DISCORD_CLIENT_SECRET"})," to the environment and restart the bot."]}),!c&&s.jsx("p",{className:"form-hint",children:"The public bot configuration is still loading."}),s.jsx("a",{className:"back-link",href:"/",onClick:u=>{u.preventDefault(),ge("/")},children:"Return to public site"})]})})]})}function zf({section:l,guild:c,stats:u,csrfToken:g}){const[k,P]=I.useState(null),[M,U]=I.useState([]),[x,z]=I.useState([]),[b,A]=I.useState(null),[L,K]=I.useState(null),[w,T]=I.useState(!0),[$,q]=I.useState("");return I.useEffect(()=>{T(!0),q(""),(l==="overview"?Hm(c.id).then(P):l==="economy"?Qm(c.id).then(U):l==="leveling"?Promise.all([Km(c.id),fc(c.id),hc(c.id)]).then(([ue,le,Ne])=>{z(ue),A(le),K(Ne)}):Promise.all([fc(c.id),hc(c.id)]).then(([ue,le])=>{A(ue),K(le)})).catch(ue=>q(ue instanceof Error?ue.message:"This server could not be loaded.")).finally(()=>T(!1))},[c.id,l]),w?s.jsxs("div",{className:"section-loading section-skeleton",role:"status","aria-label":`Loading ${l}`,children:[s.jsx("div",{className:"skeleton-title"}),s.jsx("div",{className:"skeleton-copy"}),s.jsxs("div",{className:"skeleton-grid",children:[s.jsx("i",{}),s.jsx("i",{}),s.jsx("i",{})]}),s.jsxs("span",{children:["Loading ",l,"..."]})]}):$?s.jsxs("div",{className:"inline-error",role:"alert",children:[s.jsx("strong",{children:"Couldn’t load this page."}),s.jsx("span",{children:$}),s.jsx("button",{className:"button button-muted",onClick:()=>window.location.reload(),children:"Try again"})]}):l==="overview"&&k?s.jsx(Mf,{overview:k}):l==="economy"?s.jsx(Tf,{rows:M}):l==="leveling"?s.jsx(Lf,{guildId:c.id,rows:x,config:b,resources:L,csrfToken:g}):l==="moderation"?s.jsx(Rf,{guildId:c.id,config:b,csrfToken:g}):s.jsx(Df,{guildId:c.id,config:b,csrfToken:g})}function Ff(){return s.jsxs("div",{className:"section-loading section-skeleton dashboard-loading",role:"status",children:[s.jsx("div",{className:"skeleton-title"}),s.jsx("div",{className:"skeleton-copy"}),s.jsxs("div",{className:"skeleton-grid",children:[s.jsx("i",{}),s.jsx("i",{}),s.jsx("i",{})]}),s.jsx("span",{children:"Preparing your dashboard..."})]})}function Of(){Gs();const[l,c]=I.useState(vc),[u,g]=I.useState(null),[k,P]=I.useState(null),[M,U]=I.useState(null),[x,z]=I.useState([]),[b,A]=I.useState(null),[L,K]=I.useState(!0),[w,T]=I.useState("");if(I.useEffect(()=>{const _=()=>c(vc());return window.addEventListener("popstate",_),()=>window.removeEventListener("popstate",_)},[]),I.useEffect(()=>{K(!0),Promise.all([Bm(),Cc()]).then(([_,J])=>(g(_),P(J),_.authenticated?Promise.all([$m(),Vm()]).then(([fe,be])=>{U(fe),z(be)}):null)).catch(_=>T(_ instanceof Error?_.message:"Dashboard unavailable")).finally(()=>K(!1))},[]),I.useEffect(()=>{if(l.view!=="guild"){A(null);return}const _=x.find(J=>J.id===l.guildId&&J.installed!==!1);_?(A(_),localStorage.setItem("niko-guild",_.id)):l.guildId&&x.length&&ge(gc())},[x,l.guildId,l.view]),L||!u)return s.jsxs("div",{className:"dashboard-state",children:[s.jsx("div",{className:"loading-ring"}),s.jsx("p",{children:"Connecting to Niko…"})]});if(w)return s.jsxs(s.Fragment,{children:[s.jsx(nn,{page:"dashboard"}),s.jsx("main",{className:"auth-page",children:s.jsxs("div",{className:"auth-card",children:[s.jsx("span",{className:"auth-mark",children:"!"}),s.jsx("div",{className:"eyebrow",children:"Connection issue"}),s.jsxs("h1",{children:["Couldn’t load",s.jsx("br",{}),s.jsx("em",{children:"your workspace."})]}),s.jsx("p",{children:w}),s.jsxs("button",{className:"button button-primary",onClick:()=>window.location.reload(),children:["Try again ",s.jsx(Y,{name:"arrow"})]})]})})]});if(!u.authenticated)return s.jsx(If,{auth:u});const $=_=>{_.installed!==!1&&(localStorage.setItem("niko-guild",_.id),ge(Tr(_.id,l.section)))},q=_=>{_.installed!==!1&&(localStorage.setItem("niko-guild",_.id),ge(Tr(_.id,"overview")))},me=_=>{ge(b?Tr(b.id,_):Tr())},ue=()=>ge(Tr()),le=()=>ge(gc());let Ne;return l.view==="servers"?Ne=s.jsx(Pf,{guilds:x,onManage:q}):l.view==="guild"?Ne=b?s.jsx(zf,{section:l.section,guild:b,stats:k,csrfToken:u.csrf_token},`${b.id}-${l.section}`):s.jsx(Ff,{}):Ne=s.jsx(bf,{user:u.user,overview:M,guilds:x,onServers:le,onManage:q}),s.jsx(Ef,{user:u.user,guilds:x,selectedGuild:b,view:l.view,section:l.section,stats:k,onHome:ue,onServers:le,onGuildChange:$,onSectionChange:me,children:Ne})}function Bf({value:l,onChange:c,placeholder:u="Search documentation...",onFocus:g,onBlur:k}){const[P,M]=I.useState(!1),U=I.useRef(null),[x,z]=I.useState(!1);I.useEffect(()=>{const w=T=>{var $;(T.metaKey||T.ctrlKey)&&T.key==="k"&&(T.preventDefault(),($=U.current)==null||$.focus())};return document.addEventListener("keydown",w),()=>document.removeEventListener("keydown",w)},[]);const b=()=>{M(!0),z(!0),g==null||g()},A=()=>{M(!1),setTimeout(()=>z(!1),200),k==null||k()},L=w=>{c(w.target.value)},K=w=>{var T;w.key==="Escape"&&((T=U.current)==null||T.blur())};return s.jsxs("div",{className:`doc-search-bar ${x?"expanded":""}`,children:[s.jsxs("div",{className:"search-input-wrapper",children:[s.jsx(Y,{name:"search",className:"search-icon"}),s.jsx("input",{ref:U,type:"text",value:l,onChange:L,onFocus:b,onBlur:A,onKeyDown:K,placeholder:u,className:"search-input","aria-label":"Search documentation"}),s.jsxs("kbd",{className:"search-shortcut",children:[s.jsx("span",{className:"shortcut-key",children:"⌘"}),"K"]})]}),s.jsxs("div",{className:"search-hint",children:["Press ",s.jsx("kbd",{children:"⌘K"})," to focus search"]})]})}function Uf({selectedCategory:l,onSelectCategory:c,sections:u,allCategoriesLabel:g="All Categories"}){return s.jsx("div",{className:"doc-filters",children:s.jsxs("div",{className:"filter-tabs",role:"tablist","aria-label":"Filter by category",children:[s.jsx("button",{role:"tab","aria-selected":l==="",className:`filter-tab ${l===""?"active":""}`,onClick:()=>c(""),children:g}),u.map(k=>s.jsxs("button",{role:"tab","aria-selected":l===k.id,className:`filter-tab ${l===k.id?"active":""}`,onClick:()=>c(k.id),children:[s.jsx(Y,{name:k.icon,size:14}),s.jsx("span",{children:k.label})]},k.id))]})})}function Jo({doc:l,variant:c="default"}){const u="page"in l?l.page:l,[g,k]=I.useState(!1),P=x=>{x.preventDefault(),ge(`/docs/${u.slug}`)},M=x=>{(x.key==="Enter"||x.key===" ")&&(x.preventDefault(),ge(`/docs/${u.slug}`))};if(c==="compact")return s.jsx("a",{href:`/docs/${u.slug}`,onClick:P,onKeyDown:M,className:"doc-card-compact",tabIndex:0,role:"button",children:s.jsxs("div",{className:"compact-content",children:[s.jsx("span",{className:"compact-title",children:u.title}),s.jsx("span",{className:"compact-excerpt",children:u.excerpt})]})});const U="highlights"in l?l.highlights:[];return s.jsx("article",{className:`doc-card ${c==="highlighted"?"highlighted":""}`,children:s.jsxs("div",{className:`doc-card-content ${g?"loaded":""}`,children:[s.jsxs("div",{className:"doc-card-header",children:[s.jsx("span",{className:"doc-category",children:u.category.replace(/-/g," ")}),s.jsxs("span",{className:"doc-order",children:["#",u.order]})]}),s.jsx("h3",{className:"doc-title",children:u.title}),s.jsx("p",{className:"doc-excerpt",children:u.excerpt}),U.length>0&&s.jsx("div",{className:"doc-highlights",children:U.slice(0,2).map((x,z)=>s.jsxs("p",{className:"highlight-snippet",children:[x.slice(0,150),x.length>150?"...":""]},z))}),s.jsxs("div",{className:"doc-card-footer",children:[s.jsx("div",{className:"doc-tags",children:u.tags.slice(0,3).map(x=>s.jsxs("span",{className:"doc-tag",children:["#",x]},x))}),s.jsxs("a",{href:`/docs/${u.slug}`,onClick:P,onKeyDown:M,className:"doc-read-more",children:["Read more ",s.jsx(Y,{name:"arrow",size:14})]})]})]})})}const Te=[{slug:"welcome",title:"Welcome to Niko",category:"getting-started",excerpt:"New to Niko? Start here to understand what the bot can do for your server.",tags:["introduction","overview","beginner"],order:1,content:`
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
    `}];function Wf(l){return Te.find(c=>c.slug===l)}const tn=[{id:"getting-started",label:"Getting Started",description:"New to Niko? Start here.",icon:"icon_home",count:Te.filter(l=>l.category==="getting-started").length},{id:"setup",label:"Setup",description:"Configure Niko for your server.",icon:"icon_settings",count:Te.filter(l=>l.category==="setup").length},{id:"economy",label:"Economy",description:"Money, jobs, banking, and more.",icon:"icon_economy",count:Te.filter(l=>l.category==="economy").length},{id:"leveling",label:"Leveling",description:"XP, levels, and rankings.",icon:"icon_leveling",count:Te.filter(l=>l.category==="leveling").length},{id:"moderation",label:"Moderation",description:"Moderation tools and commands.",icon:"icon_moderation",count:Te.filter(l=>l.category==="moderation").length},{id:"automod",label:"AutoMod",description:"Automated moderation features.",icon:"icon_automod",count:Te.filter(l=>l.category==="automod").length},{id:"social",label:"Social",description:"Community engagement features.",icon:"icon_heart",count:Te.filter(l=>l.category==="social").length},{id:"utility",label:"Utility",description:"Helpful tools and utilities.",icon:"icon_utility",count:Te.filter(l=>l.category==="utility").length},{id:"voice",label:"Voice",description:"Voice and music features.",icon:"icon_bot",count:Te.filter(l=>l.category==="voice").length},{id:"ai",label:"AI",description:"AI-powered features.",icon:"icon_ai",count:Te.filter(l=>l.category==="ai").length},{id:"dashboard",label:"Dashboard",description:"Web dashboard guides.",icon:"icon_settings",count:Te.filter(l=>l.category==="dashboard").length},{id:"tips",label:"Tips",description:"Tips and best practices.",icon:"icon_lightbulb",count:Te.filter(l=>l.category==="tips").length}];function Tc(){const[l,c]=I.useState({query:"",category:"",tags:[]}),u=I.useCallback(x=>{c(z=>({...z,query:x.toLowerCase(),tags:[]}))},[]),g=I.useCallback(x=>{c(z=>({...z,category:x,tags:[]}))},[]),k=I.useCallback(x=>{c(z=>{const b=z.tags.includes(x)?z.tags.filter(A=>A!==x):[...z.tags,x];return{...z,tags:b,query:""}})},[]),P=I.useCallback(()=>{c({query:"",category:"",tags:[]})},[]),M=I.useMemo(()=>{const{query:x,category:z,tags:b}=l;if(!x&&!z&&b.length===0)return Te.map(L=>({page:L,score:1,highlights:[]}));const A=[];for(const L of Te)if(!(z&&L.category!==z)&&!(b.length>0&&!b.some(K=>L.tags.includes(K))))if(x){const K=Vf(L,x);if(K===0)continue;const w=$f(L,x);A.push({page:L,score:K,highlights:w})}else A.push({page:L,score:1,highlights:[]});return A.sort((L,K)=>K.score!==L.score?K.score-L.score:L.page.order-K.page.order),A},[l]),U=l.query!==""||l.category!==""||l.tags.length>0;return{filters:l,setQuery:u,setCategory:g,toggleTag:k,clearFilters:P,results:M,hasActiveFilters:U,resultCount:M.length}}function Vf(l,c){let u=0;const g=c.toLowerCase();l.title.toLowerCase()===g?u+=100:l.title.toLowerCase().includes(g)&&(u+=50),l.excerpt.toLowerCase().includes(g)&&(u+=25),l.content.toLowerCase().includes(g)&&(u+=10);for(const k of l.tags)k.toLowerCase().includes(g)&&(u+=15);return l.category.toLowerCase().includes(g)&&(u+=5),u}function $f(l,c){const u=[],g=c.toLowerCase(),k=3;if(l.title.toLowerCase().includes(g)&&(u.push(l.title),u.length>=k)||l.excerpt.toLowerCase().includes(g)&&(u.push(l.excerpt),u.length>=k))return u;const P=l.content.split(`
`).filter(M=>M.trim());for(const M of P)if(M.toLowerCase().includes(g)){const U=M.replace(/#{1,6}\s?/g,"").trim();if(U.length>10&&(u.push(U),u.length>=k))break}return u}function Hf(){return I.useMemo(()=>{const c={};return Te.forEach(u=>{u.tags.forEach(g=>{c[g]=(c[g]||0)+1})}),Object.entries(c).map(([u,g])=>({tag:u,count:g})).sort((u,g)=>g.count-u.count)},[])}function Qf({slug:l}){var M,U;const{setCategory:c,clearFilters:u}=Tc();I.useEffect(()=>{window.location.hash!==`#/docs/${l}`&&window.history.replaceState(null,"",`#/docs/${l}`)},[l]);const g=Wf(l);if(!g)return s.jsxs(s.Fragment,{children:[s.jsx(nn,{page:"docs"}),s.jsx("main",{className:"shell page-main docs-page",children:s.jsxs("div",{className:"docs-not-found",children:[s.jsx(Y,{name:"doc",size:48,className:"not-found-icon"}),s.jsx("h1",{children:"Page Not Found"}),s.jsxs("p",{children:[`We couldn't find documentation for "`,l,'".']}),s.jsxs("div",{className:"not-found-actions",children:[s.jsx("button",{onClick:()=>ge("/docs"),children:"Browse all documentation"}),s.jsx("button",{onClick:()=>{ge("/docs"),u()},children:"Clear filters"})]})]})}),s.jsx($n,{})]});const P=(x=>{const z=x.split(`
`),b=[];let A=[];const L=()=>{A.length>0&&(b.push(s.jsx("ul",{className:"doc-content-list",children:A.map((K,w)=>s.jsx("li",{children:K},w))},`list-${b.length}`)),A=[])};return z.forEach((K,w)=>{const T=K.trim();if(!T){L(),b.push(s.jsx("div",{className:"doc-content-spacer"},w));return}if(T.startsWith("# ")){L(),b.push(s.jsx("h2",{className:"doc-heading doc-heading-h2",children:T.slice(2)},w));return}if(T.startsWith("## ")){L(),b.push(s.jsx("h3",{className:"doc-heading doc-heading-h3",children:T.slice(3)},w));return}if(T.startsWith("### ")){L(),b.push(s.jsx("h4",{className:"doc-heading doc-heading-h4",children:T.slice(4)},w));return}if(T.startsWith("> ")){L(),b.push(s.jsx("blockquote",{className:"doc-blockquote",children:T.slice(2)},w));return}if(T.startsWith("```")){L();const $=[];let q=w+1;for(;q<z.length&&z[q].trim()!=="```";)$.push(z[q]),q++;b.push(s.jsx("pre",{className:"doc-code-block",children:s.jsx("code",{children:$.join(`
`)})},w));return}if(T.startsWith("`")&&T.endsWith("`")&&T.length>2){L(),b.push(s.jsx("code",{className:"doc-inline-code",children:T.slice(1,-1)},w));return}if(T.startsWith("- ")||T.startsWith("* ")){A.push(T.slice(2));return}if(/^\d+\.\s/.test(T)){A.push(T.replace(/^\d+\.\s/,""));return}L(),b.push(s.jsx("p",{className:"doc-paragraph",children:T},w))}),L(),b})(g.content);return s.jsxs(s.Fragment,{children:[s.jsx(nn,{page:"docs"}),s.jsxs("main",{className:"shell page-main docs-page docs-detail-page",children:[s.jsx("div",{className:"docs-detail-back",children:s.jsxs("button",{onClick:()=>ge("/docs"),className:"back-button",children:[s.jsx(Y,{name:"arrow",size:16}),"Back to Documentation"]})}),s.jsxs("header",{className:"doc-article-header",children:[s.jsxs("div",{className:"doc-article-meta",children:[s.jsx("span",{className:"doc-category-badge",children:((M=tn.find(x=>x.id===g.category))==null?void 0:M.label)||g.category}),s.jsxs("span",{className:"doc-order-badge",children:["Article #",g.order]})]}),s.jsx("h1",{className:"doc-article-title",children:g.title}),s.jsx("p",{className:"doc-article-excerpt",children:g.excerpt}),s.jsx("div",{className:"doc-article-tags",children:g.tags.map(x=>s.jsxs("span",{className:"doc-tag-pill",children:["#",x]},x))})]}),s.jsx("article",{className:"doc-article-content",children:P}),s.jsx("footer",{className:"doc-article-footer",children:s.jsx("div",{className:"doc-nav-container",children:s.jsxs("div",{className:"doc-nav-col",children:[s.jsx("span",{className:"doc-nav-label",children:"Category"}),s.jsxs("button",{className:"doc-nav-link",onClick:()=>{c(g.category),ge("/docs")},children:[s.jsx(Y,{name:"arrow",size:14}),"View all ",(U=tn.find(x=>x.id===g.category))==null?void 0:U.label]})]})})}),P.filter(x=>x.type==="h2"||x.type==="h3").length>0&&s.jsxs("aside",{className:"doc-toc",children:[s.jsxs("div",{className:"toc-title",children:[s.jsx(Y,{name:"utility",size:16}),s.jsx("span",{children:"On this page"})]}),s.jsx("nav",{className:"toc-nav",children:P.filter(x=>x.type==="h2"||x.type==="h3").map((x,z)=>{var A;const b=(A=x.props.className)==null?void 0:A.includes("doc-heading-h2");return s.jsx("a",{href:`#${b?"h2-":"h3-"}-${z}`,className:`toc-link ${b?"toc-h2":"toc-h3"}`,children:x.props.children},z)})})]})]}),s.jsx($n,{})]})}function Kf(){var le,Ne;const[l,c]=I.useState(!1),[u,g]=I.useState(""),[k,P]=I.useState(!1),{filters:M,setQuery:U,setCategory:x,toggleTag:z,clearFilters:b,results:A,hasActiveFilters:L,resultCount:K}=Tc(),w=Hf();I.useEffect(()=>{const _=()=>{const J=window.location.hash.slice(1);if(J.startsWith("#/docs/")){const fe=J.replace("#/docs/",""),be=Te.find(dt=>dt.slug===fe);be&&(g(be.category),x(be.category))}};return _(),window.addEventListener("hashchange",_),()=>window.removeEventListener("hashchange",_)},[]);const T=()=>{P(!0)},$=_=>{g(_),x(_),c(!1)},q=()=>{M.query||P(!1)},me=_=>{ge(`/docs/${_}`),U(""),P(!1)},ue=I.useMemo(()=>{const _={};return A.forEach(J=>{const fe=J.page.category;_[fe]||(_[fe]=[]),_[fe].push(J)}),_},[A]);return s.jsxs(s.Fragment,{children:[s.jsx(nn,{page:"docs"}),s.jsxs("main",{className:"shell page-main docs-page",children:[s.jsx("div",{className:"docs-hero",children:s.jsxs("div",{className:"docs-hero-content",children:[s.jsx("div",{className:"eyebrow docs-eyebrow",children:"Documentation Center"}),s.jsxs("h1",{className:"docs-title",children:["Everything you need to know about",s.jsx("br",{}),s.jsx("span",{className:"title-accent",children:"using Niko"})]}),s.jsx("p",{className:"docs-subtitle",children:"Comprehensive guides, command references, and tips to help you get the most out of your server bot."})]})}),s.jsx("div",{className:`docs-search-section ${k?"active":""}`,children:s.jsxs("div",{className:"docs-search-container",children:[s.jsx(Bf,{value:M.query,onChange:U,placeholder:"Search documentation, commands, guides...",onFocus:T,onBlur:q}),k&&M.query&&A.length>0&&s.jsxs("div",{className:"search-results-dropdown",children:[s.jsxs("div",{className:"search-results-header",children:[s.jsxs("span",{className:"results-count",children:[K," ",K===1?"result":"results"]}),s.jsx("button",{className:"clear-search-btn",onClick:()=>{U(""),b(),g("")},children:"Clear"})]}),s.jsx("div",{className:"search-results-list",children:A.slice(0,8).map((_,J)=>s.jsxs("button",{className:"search-result-item",onClick:()=>me(_.page.slug),onMouseEnter:()=>{},children:[s.jsx("div",{className:"result-icon",children:s.jsx(Y,{name:"doc",size:18})}),s.jsxs("div",{className:"result-content",children:[s.jsx("div",{className:"result-title",children:_.page.title}),s.jsx("div",{className:"result-excerpt",children:_.page.excerpt}),_.highlights.length>0&&s.jsxs("div",{className:"result-highlight",children:[_.highlights[0].slice(0,100),"..."]})]}),s.jsx(Y,{name:"arrow",size:14,className:"result-arrow"})]},_.page.slug))}),A.length>8&&s.jsx("div",{className:"search-results-footer",children:s.jsxs("span",{children:["Showing 8 of ",A.length," results. Browse all docs below."]})})]})]})}),s.jsxs("div",{className:"docs-mobile-nav",children:[s.jsx("button",{className:"mobile-menu-toggle",onClick:()=>c(!l),"aria-label":"Toggle documentation menu",children:s.jsx(Y,{name:"utility",size:20})}),l&&s.jsxs("div",{className:"mobile-nav-panel",children:[s.jsxs("div",{className:"mobile-nav-header",children:[s.jsx("h3",{children:"Documentation"}),s.jsx("button",{className:"close-menu-btn",onClick:()=>c(!1),"aria-label":"Close menu",children:s.jsx(Y,{name:"utility",size:16,className:"rotated"})})]}),s.jsx("div",{className:"mobile-nav-sections",children:tn.map(_=>s.jsxs("button",{className:`mobile-nav-item ${u===_.id?"active":""}`,onClick:()=>{$(_.id)},children:[s.jsx(Y,{name:_.icon,size:18}),s.jsx("span",{className:"mobile-section-label",children:_.label}),s.jsx("span",{className:"mobile-section-count",children:_.count})]},_.id))})]})]}),w.length>0&&!L&&s.jsxs("div",{className:"docs-tags-cloud",children:[s.jsxs("div",{className:"tags-cloud-title",children:[s.jsx(Y,{name:"utility",size:16}),s.jsx("span",{children:"Popular Topics"})]}),s.jsx("div",{className:"tags-cloud-list",children:w.slice(0,15).map(({tag:_,count:J})=>s.jsxs("button",{className:"tag-cloud-item",onClick:()=>z(_),style:{fontSize:`${.75+Math.min(J/4,1)}rem`},children:["#",_,s.jsx("span",{className:"tag-count",children:J})]},_))})]}),s.jsx("div",{className:"docs-category-filters",children:s.jsx(Uf,{selectedCategory:M.category,onSelectCategory:$,sections:tn})}),L&&s.jsxs("div",{className:"docs-results-header",children:[s.jsxs("div",{className:"results-info",children:[s.jsxs("span",{className:"results-count-large",children:[K," ",K===1?"article":"articles"]}),M.query&&s.jsxs("span",{className:"search-query-display",children:['for "',s.jsx("strong",{children:M.query}),'"']})]}),s.jsxs("button",{className:"clear-all-btn",onClick:()=>{b(),g("")},disabled:!L,children:[s.jsx(Y,{name:"utility",size:14}),"Clear all filters"]})]}),s.jsx("div",{className:"docs-content",children:L?s.jsx("div",{className:"search-results-view",children:Object.entries(ue).map(([_,J])=>{var fe;return s.jsxs("section",{className:"results-category",children:[s.jsx("h2",{className:"category-title",children:((fe=tn.find(be=>be.id===_))==null?void 0:fe.label)||_}),s.jsx("div",{className:"category-results-grid",children:J.map(be=>s.jsx(Jo,{doc:be,variant:"highlighted"},be.page.slug))})]},_)})}):u?s.jsxs("div",{className:"category-view",children:[s.jsxs("div",{className:"category-header",children:[s.jsx("h2",{className:"category-page-title",children:((le=tn.find(_=>_.id===u))==null?void 0:le.label)||u}),s.jsx("p",{className:"category-description",children:(Ne=tn.find(_=>_.id===u))==null?void 0:Ne.description})]}),s.jsx("div",{className:"category-articles",children:Te.filter(_=>_.category===u).sort((_,J)=>_.order-J.order).map(_=>s.jsx(Jo,{doc:_},_.slug))})]}):s.jsx("div",{className:"all-categories-view",children:tn.map(_=>s.jsxs("section",{className:"docs-section",id:`section-${_.id}`,children:[s.jsxs("div",{className:"section-header",children:[s.jsx("div",{className:"section-icon",children:s.jsx(Y,{name:_.icon,size:28})}),s.jsxs("div",{className:"section-info",children:[s.jsx("h2",{className:"section-title",children:_.label}),s.jsx("p",{className:"section-description",children:_.description})]}),s.jsx("span",{className:"section-count",children:_.count})]}),s.jsx("div",{className:"section-articles",children:Te.filter(J=>J.category===_.id).sort((J,fe)=>J.order-fe.order).map(J=>s.jsx(Jo,{doc:J},J.slug))})]},_.id))})}),s.jsxs("div",{className:"docs-footer-note",children:[s.jsx(Y,{name:"book",size:20}),s.jsxs("div",{children:[s.jsx("strong",{children:"Want more detail?"}),s.jsxs("p",{children:["The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in the"," ",s.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"docs/"})," ","folder."]})]})]})]}),s.jsx($n,{})]})}function Gf(){const l=Gs(),[c,u]=I.useState(null);I.useEffect(()=>{Cc().then(u).catch(()=>{})},[]);const g=[["spark","AI that remembers","Thoughtful conversation with a cozy personality and controls that respect your community."],["chart","A living economy","Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],["shield","Confident moderation","Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],["users","Community rituals","Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."]];return s.jsxs(s.Fragment,{children:[s.jsx(nn,{page:"home"}),s.jsxs("main",{children:[s.jsxs("section",{className:"hero shell",children:[s.jsxs("div",{className:"hero-copy",children:[s.jsxs("div",{className:"eyebrow",children:[s.jsx("span",{className:"status-dot"})," Discord companion · online"]}),s.jsxs("h1",{children:["Useful tools for a ",s.jsx("em",{children:"better server."})]}),s.jsx("p",{children:"Niko handles the everyday work of running a Discord community, so your moderators can focus on the people in it."}),s.jsxs("div",{className:"hero-buttons",children:[s.jsxs("a",{className:"button button-primary",href:(l==null?void 0:l.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Invite Niko ",s.jsx(Y,{name:"arrow"})]}),s.jsx("a",{className:"button button-muted",href:"/commands",onClick:k=>{k.preventDefault(),ge("/commands")},children:"Explore commands"})]}),s.jsxs("div",{className:"stats-strip",children:[s.jsxs("div",{children:[s.jsx("strong",{children:ke(c==null?void 0:c.guild_count)}),s.jsx("span",{children:"servers"})]}),s.jsxs("div",{children:[s.jsx("strong",{children:ke(c==null?void 0:c.user_count)}),s.jsx("span",{children:"members"})]}),s.jsxs("div",{children:[s.jsx("strong",{children:ke(c==null?void 0:c.command_count)}),s.jsx("span",{children:"commands"})]})]})]}),s.jsx("div",{className:"hero-art","aria-label":"A preview of Niko's server workspace",children:s.jsxs("div",{className:"workspace-preview",children:[s.jsxs("div",{className:"workspace-preview-top",children:[s.jsxs("span",{className:"preview-dots",children:[s.jsx("i",{}),s.jsx("i",{}),s.jsx("i",{})]}),s.jsx("span",{children:"server workspace"}),s.jsxs("span",{className:"preview-status",children:[s.jsx("span",{className:"status-dot"})," live"]})]}),s.jsxs("div",{className:"preview-body",children:[s.jsxs("div",{className:"preview-sidebar",children:[s.jsx("span",{className:"preview-label",children:"NIKO"}),s.jsx("b",{children:"Overview"}),s.jsx("span",{children:"Economy"}),s.jsx("span",{children:"Leveling"}),s.jsx("span",{children:"Moderation"}),s.jsx("span",{children:"AI controls"})]}),s.jsxs("div",{className:"preview-main",children:[s.jsx("span",{className:"preview-label",children:"SERVER SNAPSHOT"}),s.jsx("strong",{children:"Everything in one place."}),s.jsxs("div",{className:"preview-stats",children:[s.jsxs("span",{children:[s.jsx("b",{children:ke(c==null?void 0:c.user_count)}),s.jsx("small",{children:"members"})]}),s.jsxs("span",{children:[s.jsx("b",{children:ke(c==null?void 0:c.command_count)}),s.jsx("small",{children:"commands"})]})]}),s.jsxs("div",{className:"preview-line",children:[s.jsx("i",{}),s.jsx("i",{}),s.jsx("i",{})]})]})]})]})})]}),s.jsxs("section",{className:"shell intro-section",children:[s.jsx("div",{className:"section-kicker",children:"Why Niko"}),s.jsxs("div",{className:"intro-grid",children:[s.jsxs("h2",{children:["The good kind of",s.jsx("br",{}),s.jsx("em",{children:"always-on."})]}),s.jsx("p",{children:"Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile."})]})]}),s.jsx("section",{className:"shell feature-grid",children:g.map(([k,P,M])=>s.jsxs("article",{className:"feature-card",children:[s.jsx("span",{className:"feature-icon",children:s.jsx(Y,{name:k})}),s.jsx("h3",{children:P}),s.jsx("p",{children:M}),s.jsxs("a",{href:"/docs",onClick:U=>{U.preventDefault(),ge("/docs")},children:["Learn more ",s.jsx(Y,{name:"arrow"})]})]},P))}),s.jsxs("section",{className:"shell callout",children:[s.jsxs("div",{children:[s.jsx("div",{className:"section-kicker",children:"Ready when you are"}),s.jsxs("h2",{children:["A calmer, cleverer home",s.jsx("br",{}),"for your community."]})]}),s.jsxs("a",{className:"button button-primary",href:(l==null?void 0:l.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Bring Niko in ",s.jsx(Y,{name:"arrow"})]})]})]}),s.jsx($n,{})]})}const Xf={privacy:{title:"Privacy policy",intro:"Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",sections:[["Information we use","User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature."],["How it is used","Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],["Storage and retention","Data is stored by the server hosting Niko in local JSON and SQLite files. Economy, leveling, and configuration data remain until removed. AI conversation history is limited and can be cleared with /clearhistory."],["Third-party services","When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Music and external lookup features may contact their respective services."],["Your choices","Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."]]},terms:{title:"Terms of service",intro:"By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",sections:[["Permitted use","Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],["Availability","Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],["Moderation","The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],["AI content","AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],["Virtual items","In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],["Contact","Questions or concerns can be sent through the Niko support server."]]}};function Nc({type:l}){const c=Xf[l];return s.jsxs(s.Fragment,{children:[s.jsx(nn,{page:l}),s.jsxs("main",{className:"shell page-main legal-page",children:[s.jsxs("div",{className:"page-heading",children:[s.jsx("div",{className:"eyebrow",children:"Niko legal"}),s.jsx("h1",{children:c.title}),s.jsx("p",{children:c.intro}),s.jsx("small",{children:"Effective date: 1 January 2025"})]}),s.jsx("div",{className:"legal-copy",children:c.sections.map(([u,g])=>s.jsxs("section",{children:[s.jsx("h2",{children:u}),s.jsx("p",{children:g})]},u))})]}),s.jsx($n,{})]})}function qf(){const[l,c]=I.useState(pc);if(I.useEffect(()=>{const u=()=>c(pc());return window.addEventListener("popstate",u),()=>window.removeEventListener("popstate",u)},[]),l==="commands")return s.jsx(_f,{});if(l==="docs-detail"){const u=window.location.pathname.split("/"),g=u[u.length-1];return s.jsx(Qf,{slug:g})}return l==="docs"?s.jsx(Kf,{}):l==="dashboard"?s.jsx(Of,{}):l==="privacy"?s.jsx(Nc,{type:"privacy"}):l==="terms"?s.jsx(Nc,{type:"terms"}):s.jsx(Gf,{})}Fm.createRoot(document.getElementById("root")).render(s.jsx(I.StrictMode,{children:s.jsx(qf,{})}));
