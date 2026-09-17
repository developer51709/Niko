var Xm=Object.defineProperty;var Ym=(o,c,l)=>c in o?Xm(o,c,{enumerable:!0,configurable:!0,writable:!0,value:l}):o[c]=l;var hu=(o,c,l)=>Ym(o,typeof c!="symbol"?c+"":c,l);(function(){const c=document.createElement("link").relList;if(c&&c.supports&&c.supports("modulepreload"))return;for(const m of document.querySelectorAll('link[rel="modulepreload"]'))d(m);new MutationObserver(m=>{for(const f of m)if(f.type==="childList")for(const v of f.addedNodes)v.tagName==="LINK"&&v.rel==="modulepreload"&&d(v)}).observe(document,{childList:!0,subtree:!0});function l(m){const f={};return m.integrity&&(f.integrity=m.integrity),m.referrerPolicy&&(f.referrerPolicy=m.referrerPolicy),m.crossOrigin==="use-credentials"?f.credentials="include":m.crossOrigin==="anonymous"?f.credentials="omit":f.credentials="same-origin",f}function d(m){if(m.ep)return;m.ep=!0;const f=l(m);fetch(m.href,f)}})();var to={exports:{}},Dr={},no={exports:{}},se={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var pu;function Jm(){if(pu)return se;pu=1;var o=Symbol.for("react.element"),c=Symbol.for("react.portal"),l=Symbol.for("react.fragment"),d=Symbol.for("react.strict_mode"),m=Symbol.for("react.profiler"),f=Symbol.for("react.provider"),v=Symbol.for("react.context"),M=Symbol.for("react.forward_ref"),w=Symbol.for("react.suspense"),z=Symbol.for("react.memo"),N=Symbol.for("react.lazy"),C=Symbol.iterator;function P(y){return y===null||typeof y!="object"?null:(y=C&&y[C]||y["@@iterator"],typeof y=="function"?y:null)}var I={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},D=Object.assign,B={};function b(y,T,re){this.props=y,this.context=T,this.refs=B,this.updater=re||I}b.prototype.isReactComponent={},b.prototype.setState=function(y,T){if(typeof y!="object"&&typeof y!="function"&&y!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,y,T,"setState")},b.prototype.forceUpdate=function(y){this.updater.enqueueForceUpdate(this,y,"forceUpdate")};function Q(){}Q.prototype=b.prototype;function S(y,T,re){this.props=y,this.context=T,this.refs=B,this.updater=re||I}var q=S.prototype=new Q;q.constructor=S,D(q,b.prototype),q.isPureReactComponent=!0;var ne=Array.isArray,ie=Object.prototype.hasOwnProperty,F={current:null},J={key:!0,ref:!0,__self:!0,__source:!0};function pe(y,T,re){var ae,ce={},ue=null,fe=null;if(T!=null)for(ae in T.ref!==void 0&&(fe=T.ref),T.key!==void 0&&(ue=""+T.key),T)ie.call(T,ae)&&!J.hasOwnProperty(ae)&&(ce[ae]=T[ae]);var me=arguments.length-2;if(me===1)ce.children=re;else if(1<me){for(var xe=Array(me),it=0;it<me;it++)xe[it]=arguments[it+2];ce.children=xe}if(y&&y.defaultProps)for(ae in me=y.defaultProps,me)ce[ae]===void 0&&(ce[ae]=me[ae]);return{$$typeof:o,type:y,key:ue,ref:fe,props:ce,_owner:F.current}}function Se(y,T){return{$$typeof:o,type:y.type,key:T,ref:y.ref,props:y.props,_owner:y._owner}}function De(y){return typeof y=="object"&&y!==null&&y.$$typeof===o}function te(y){var T={"=":"=0",":":"=2"};return"$"+y.replace(/[=:]/g,function(re){return T[re]})}var we=/\/+/g;function _e(y,T){return typeof y=="object"&&y!==null&&y.key!=null?te(""+y.key):T.toString(36)}function Be(y,T,re,ae,ce){var ue=typeof y;(ue==="undefined"||ue==="boolean")&&(y=null);var fe=!1;if(y===null)fe=!0;else switch(ue){case"string":case"number":fe=!0;break;case"object":switch(y.$$typeof){case o:case c:fe=!0}}if(fe)return fe=y,ce=ce(fe),y=ae===""?"."+_e(fe,0):ae,ne(ce)?(re="",y!=null&&(re=y.replace(we,"$&/")+"/"),Be(ce,T,re,"",function(it){return it})):ce!=null&&(De(ce)&&(ce=Se(ce,re+(!ce.key||fe&&fe.key===ce.key?"":(""+ce.key).replace(we,"$&/")+"/")+y)),T.push(ce)),1;if(fe=0,ae=ae===""?".":ae+":",ne(y))for(var me=0;me<y.length;me++){ue=y[me];var xe=ae+_e(ue,me);fe+=Be(ue,T,re,xe,ce)}else if(xe=P(y),typeof xe=="function")for(y=xe.call(y),me=0;!(ue=y.next()).done;)ue=ue.value,xe=ae+_e(ue,me++),fe+=Be(ue,T,re,xe,ce);else if(ue==="object")throw T=String(y),Error("Objects are not valid as a React child (found: "+(T==="[object Object]"?"object with keys {"+Object.keys(y).join(", ")+"}":T)+"). If you meant to render a collection of children, use an array instead.");return fe}function St(y,T,re){if(y==null)return y;var ae=[],ce=0;return Be(y,ae,"","",function(ue){return T.call(re,ue,ce++)}),ae}function qe(y){if(y._status===-1){var T=y._result;T=T(),T.then(function(re){(y._status===0||y._status===-1)&&(y._status=1,y._result=re)},function(re){(y._status===0||y._status===-1)&&(y._status=2,y._result=re)}),y._status===-1&&(y._status=0,y._result=T)}if(y._status===1)return y._result.default;throw y._result}var Ne={current:null},O={transition:null},Z={ReactCurrentDispatcher:Ne,ReactCurrentBatchConfig:O,ReactCurrentOwner:F};function $(){throw Error("act(...) is not supported in production builds of React.")}return se.Children={map:St,forEach:function(y,T,re){St(y,function(){T.apply(this,arguments)},re)},count:function(y){var T=0;return St(y,function(){T++}),T},toArray:function(y){return St(y,function(T){return T})||[]},only:function(y){if(!De(y))throw Error("React.Children.only expected to receive a single React element child.");return y}},se.Component=b,se.Fragment=l,se.Profiler=m,se.PureComponent=S,se.StrictMode=d,se.Suspense=w,se.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Z,se.act=$,se.cloneElement=function(y,T,re){if(y==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+y+".");var ae=D({},y.props),ce=y.key,ue=y.ref,fe=y._owner;if(T!=null){if(T.ref!==void 0&&(ue=T.ref,fe=F.current),T.key!==void 0&&(ce=""+T.key),y.type&&y.type.defaultProps)var me=y.type.defaultProps;for(xe in T)ie.call(T,xe)&&!J.hasOwnProperty(xe)&&(ae[xe]=T[xe]===void 0&&me!==void 0?me[xe]:T[xe])}var xe=arguments.length-2;if(xe===1)ae.children=re;else if(1<xe){me=Array(xe);for(var it=0;it<xe;it++)me[it]=arguments[it+2];ae.children=me}return{$$typeof:o,type:y.type,key:ce,ref:ue,props:ae,_owner:fe}},se.createContext=function(y){return y={$$typeof:v,_currentValue:y,_currentValue2:y,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},y.Provider={$$typeof:f,_context:y},y.Consumer=y},se.createElement=pe,se.createFactory=function(y){var T=pe.bind(null,y);return T.type=y,T},se.createRef=function(){return{current:null}},se.forwardRef=function(y){return{$$typeof:M,render:y}},se.isValidElement=De,se.lazy=function(y){return{$$typeof:N,_payload:{_status:-1,_result:y},_init:qe}},se.memo=function(y,T){return{$$typeof:z,type:y,compare:T===void 0?null:T}},se.startTransition=function(y){var T=O.transition;O.transition={};try{y()}finally{O.transition=T}},se.unstable_act=$,se.useCallback=function(y,T){return Ne.current.useCallback(y,T)},se.useContext=function(y){return Ne.current.useContext(y)},se.useDebugValue=function(){},se.useDeferredValue=function(y){return Ne.current.useDeferredValue(y)},se.useEffect=function(y,T){return Ne.current.useEffect(y,T)},se.useId=function(){return Ne.current.useId()},se.useImperativeHandle=function(y,T,re){return Ne.current.useImperativeHandle(y,T,re)},se.useInsertionEffect=function(y,T){return Ne.current.useInsertionEffect(y,T)},se.useLayoutEffect=function(y,T){return Ne.current.useLayoutEffect(y,T)},se.useMemo=function(y,T){return Ne.current.useMemo(y,T)},se.useReducer=function(y,T,re){return Ne.current.useReducer(y,T,re)},se.useRef=function(y){return Ne.current.useRef(y)},se.useState=function(y){return Ne.current.useState(y)},se.useSyncExternalStore=function(y,T,re){return Ne.current.useSyncExternalStore(y,T,re)},se.useTransition=function(){return Ne.current.useTransition()},se.version="18.3.1",se}var fu;function vo(){return fu||(fu=1,no.exports=Jm()),no.exports}/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var gu;function Zm(){if(gu)return Dr;gu=1;var o=vo(),c=Symbol.for("react.element"),l=Symbol.for("react.fragment"),d=Object.prototype.hasOwnProperty,m=o.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,f={key:!0,ref:!0,__self:!0,__source:!0};function v(M,w,z){var N,C={},P=null,I=null;z!==void 0&&(P=""+z),w.key!==void 0&&(P=""+w.key),w.ref!==void 0&&(I=w.ref);for(N in w)d.call(w,N)&&!f.hasOwnProperty(N)&&(C[N]=w[N]);if(M&&M.defaultProps)for(N in w=M.defaultProps,w)C[N]===void 0&&(C[N]=w[N]);return{$$typeof:c,type:M,key:P,ref:I,props:C,_owner:m.current}}return Dr.Fragment=l,Dr.jsx=v,Dr.jsxs=v,Dr}var vu;function eh(){return vu||(vu=1,to.exports=Zm()),to.exports}var r=eh(),R=vo(),Ks={},ro={exports:{}},et={},so={exports:{}},ao={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var yu;function th(){return yu||(yu=1,(function(o){function c(O,Z){var $=O.length;O.push(Z);e:for(;0<$;){var y=$-1>>>1,T=O[y];if(0<m(T,Z))O[y]=Z,O[$]=T,$=y;else break e}}function l(O){return O.length===0?null:O[0]}function d(O){if(O.length===0)return null;var Z=O[0],$=O.pop();if($!==Z){O[0]=$;e:for(var y=0,T=O.length,re=T>>>1;y<re;){var ae=2*(y+1)-1,ce=O[ae],ue=ae+1,fe=O[ue];if(0>m(ce,$))ue<T&&0>m(fe,ce)?(O[y]=fe,O[ue]=$,y=ue):(O[y]=ce,O[ae]=$,y=ae);else if(ue<T&&0>m(fe,$))O[y]=fe,O[ue]=$,y=ue;else break e}}return Z}function m(O,Z){var $=O.sortIndex-Z.sortIndex;return $!==0?$:O.id-Z.id}if(typeof performance=="object"&&typeof performance.now=="function"){var f=performance;o.unstable_now=function(){return f.now()}}else{var v=Date,M=v.now();o.unstable_now=function(){return v.now()-M}}var w=[],z=[],N=1,C=null,P=3,I=!1,D=!1,B=!1,b=typeof setTimeout=="function"?setTimeout:null,Q=typeof clearTimeout=="function"?clearTimeout:null,S=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function q(O){for(var Z=l(z);Z!==null;){if(Z.callback===null)d(z);else if(Z.startTime<=O)d(z),Z.sortIndex=Z.expirationTime,c(w,Z);else break;Z=l(z)}}function ne(O){if(B=!1,q(O),!D)if(l(w)!==null)D=!0,qe(ie);else{var Z=l(z);Z!==null&&Ne(ne,Z.startTime-O)}}function ie(O,Z){D=!1,B&&(B=!1,Q(pe),pe=-1),I=!0;var $=P;try{for(q(Z),C=l(w);C!==null&&(!(C.expirationTime>Z)||O&&!te());){var y=C.callback;if(typeof y=="function"){C.callback=null,P=C.priorityLevel;var T=y(C.expirationTime<=Z);Z=o.unstable_now(),typeof T=="function"?C.callback=T:C===l(w)&&d(w),q(Z)}else d(w);C=l(w)}if(C!==null)var re=!0;else{var ae=l(z);ae!==null&&Ne(ne,ae.startTime-Z),re=!1}return re}finally{C=null,P=$,I=!1}}var F=!1,J=null,pe=-1,Se=5,De=-1;function te(){return!(o.unstable_now()-De<Se)}function we(){if(J!==null){var O=o.unstable_now();De=O;var Z=!0;try{Z=J(!0,O)}finally{Z?_e():(F=!1,J=null)}}else F=!1}var _e;if(typeof S=="function")_e=function(){S(we)};else if(typeof MessageChannel<"u"){var Be=new MessageChannel,St=Be.port2;Be.port1.onmessage=we,_e=function(){St.postMessage(null)}}else _e=function(){b(we,0)};function qe(O){J=O,F||(F=!0,_e())}function Ne(O,Z){pe=b(function(){O(o.unstable_now())},Z)}o.unstable_IdlePriority=5,o.unstable_ImmediatePriority=1,o.unstable_LowPriority=4,o.unstable_NormalPriority=3,o.unstable_Profiling=null,o.unstable_UserBlockingPriority=2,o.unstable_cancelCallback=function(O){O.callback=null},o.unstable_continueExecution=function(){D||I||(D=!0,qe(ie))},o.unstable_forceFrameRate=function(O){0>O||125<O?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):Se=0<O?Math.floor(1e3/O):5},o.unstable_getCurrentPriorityLevel=function(){return P},o.unstable_getFirstCallbackNode=function(){return l(w)},o.unstable_next=function(O){switch(P){case 1:case 2:case 3:var Z=3;break;default:Z=P}var $=P;P=Z;try{return O()}finally{P=$}},o.unstable_pauseExecution=function(){},o.unstable_requestPaint=function(){},o.unstable_runWithPriority=function(O,Z){switch(O){case 1:case 2:case 3:case 4:case 5:break;default:O=3}var $=P;P=O;try{return Z()}finally{P=$}},o.unstable_scheduleCallback=function(O,Z,$){var y=o.unstable_now();switch(typeof $=="object"&&$!==null?($=$.delay,$=typeof $=="number"&&0<$?y+$:y):$=y,O){case 1:var T=-1;break;case 2:T=250;break;case 5:T=1073741823;break;case 4:T=1e4;break;default:T=5e3}return T=$+T,O={id:N++,callback:Z,priorityLevel:O,startTime:$,expirationTime:T,sortIndex:-1},$>y?(O.sortIndex=$,c(z,O),l(w)===null&&O===l(z)&&(B?(Q(pe),pe=-1):B=!0,Ne(ne,$-y))):(O.sortIndex=T,c(w,O),D||I||(D=!0,qe(ie))),O},o.unstable_shouldYield=te,o.unstable_wrapCallback=function(O){var Z=P;return function(){var $=P;P=Z;try{return O.apply(this,arguments)}finally{P=$}}}})(ao)),ao}var xu;function nh(){return xu||(xu=1,so.exports=th()),so.exports}/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var ku;function rh(){if(ku)return et;ku=1;var o=vo(),c=nh();function l(e){for(var t="https://reactjs.org/docs/error-decoder.html?invariant="+e,n=1;n<arguments.length;n++)t+="&args[]="+encodeURIComponent(arguments[n]);return"Minified React error #"+e+"; visit "+t+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var d=new Set,m={};function f(e,t){v(e,t),v(e+"Capture",t)}function v(e,t){for(m[e]=t,e=0;e<t.length;e++)d.add(t[e])}var M=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),w=Object.prototype.hasOwnProperty,z=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,N={},C={};function P(e){return w.call(C,e)?!0:w.call(N,e)?!1:z.test(e)?C[e]=!0:(N[e]=!0,!1)}function I(e,t,n,s){if(n!==null&&n.type===0)return!1;switch(typeof t){case"function":case"symbol":return!0;case"boolean":return s?!1:n!==null?!n.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function D(e,t,n,s){if(t===null||typeof t>"u"||I(e,t,n,s))return!0;if(s)return!1;if(n!==null)switch(n.type){case 3:return!t;case 4:return t===!1;case 5:return isNaN(t);case 6:return isNaN(t)||1>t}return!1}function B(e,t,n,s,a,i,u){this.acceptsBooleans=t===2||t===3||t===4,this.attributeName=s,this.attributeNamespace=a,this.mustUseProperty=n,this.propertyName=e,this.type=t,this.sanitizeURL=i,this.removeEmptyString=u}var b={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){b[e]=new B(e,0,!1,e,null,!1,!1)}),[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var t=e[0];b[t]=new B(t,1,!1,e[1],null,!1,!1)}),["contentEditable","draggable","spellCheck","value"].forEach(function(e){b[e]=new B(e,2,!1,e.toLowerCase(),null,!1,!1)}),["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){b[e]=new B(e,2,!1,e,null,!1,!1)}),"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){b[e]=new B(e,3,!1,e.toLowerCase(),null,!1,!1)}),["checked","multiple","muted","selected"].forEach(function(e){b[e]=new B(e,3,!0,e,null,!1,!1)}),["capture","download"].forEach(function(e){b[e]=new B(e,4,!1,e,null,!1,!1)}),["cols","rows","size","span"].forEach(function(e){b[e]=new B(e,6,!1,e,null,!1,!1)}),["rowSpan","start"].forEach(function(e){b[e]=new B(e,5,!1,e.toLowerCase(),null,!1,!1)});var Q=/[\-:]([a-z])/g;function S(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var t=e.replace(Q,S);b[t]=new B(t,1,!1,e,null,!1,!1)}),"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var t=e.replace(Q,S);b[t]=new B(t,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)}),["xml:base","xml:lang","xml:space"].forEach(function(e){var t=e.replace(Q,S);b[t]=new B(t,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)}),["tabIndex","crossOrigin"].forEach(function(e){b[e]=new B(e,1,!1,e.toLowerCase(),null,!1,!1)}),b.xlinkHref=new B("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1),["src","href","action","formAction"].forEach(function(e){b[e]=new B(e,1,!1,e.toLowerCase(),null,!0,!0)});function q(e,t,n,s){var a=b.hasOwnProperty(t)?b[t]:null;(a!==null?a.type!==0:s||!(2<t.length)||t[0]!=="o"&&t[0]!=="O"||t[1]!=="n"&&t[1]!=="N")&&(D(t,n,a,s)&&(n=null),s||a===null?P(t)&&(n===null?e.removeAttribute(t):e.setAttribute(t,""+n)):a.mustUseProperty?e[a.propertyName]=n===null?a.type===3?!1:"":n:(t=a.attributeName,s=a.attributeNamespace,n===null?e.removeAttribute(t):(a=a.type,n=a===3||a===4&&n===!0?"":""+n,s?e.setAttributeNS(s,t,n):e.setAttribute(t,n))))}var ne=o.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,ie=Symbol.for("react.element"),F=Symbol.for("react.portal"),J=Symbol.for("react.fragment"),pe=Symbol.for("react.strict_mode"),Se=Symbol.for("react.profiler"),De=Symbol.for("react.provider"),te=Symbol.for("react.context"),we=Symbol.for("react.forward_ref"),_e=Symbol.for("react.suspense"),Be=Symbol.for("react.suspense_list"),St=Symbol.for("react.memo"),qe=Symbol.for("react.lazy"),Ne=Symbol.for("react.offscreen"),O=Symbol.iterator;function Z(e){return e===null||typeof e!="object"?null:(e=O&&e[O]||e["@@iterator"],typeof e=="function"?e:null)}var $=Object.assign,y;function T(e){if(y===void 0)try{throw Error()}catch(n){var t=n.stack.trim().match(/\n( *(at )?)/);y=t&&t[1]||""}return`
`+y+e}var re=!1;function ae(e,t){if(!e||re)return"";re=!0;var n=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(t)if(t=function(){throw Error()},Object.defineProperty(t.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(t,[])}catch(j){var s=j}Reflect.construct(e,[],t)}else{try{t.call()}catch(j){s=j}e.call(t.prototype)}else{try{throw Error()}catch(j){s=j}e()}}catch(j){if(j&&s&&typeof j.stack=="string"){for(var a=j.stack.split(`
`),i=s.stack.split(`
`),u=a.length-1,h=i.length-1;1<=u&&0<=h&&a[u]!==i[h];)h--;for(;1<=u&&0<=h;u--,h--)if(a[u]!==i[h]){if(u!==1||h!==1)do if(u--,h--,0>h||a[u]!==i[h]){var p=`
`+a[u].replace(" at new "," at ");return e.displayName&&p.includes("<anonymous>")&&(p=p.replace("<anonymous>",e.displayName)),p}while(1<=u&&0<=h);break}}}finally{re=!1,Error.prepareStackTrace=n}return(e=e?e.displayName||e.name:"")?T(e):""}function ce(e){switch(e.tag){case 5:return T(e.type);case 16:return T("Lazy");case 13:return T("Suspense");case 19:return T("SuspenseList");case 0:case 2:case 15:return e=ae(e.type,!1),e;case 11:return e=ae(e.type.render,!1),e;case 1:return e=ae(e.type,!0),e;default:return""}}function ue(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case J:return"Fragment";case F:return"Portal";case Se:return"Profiler";case pe:return"StrictMode";case _e:return"Suspense";case Be:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case te:return(e.displayName||"Context")+".Consumer";case De:return(e._context.displayName||"Context")+".Provider";case we:var t=e.render;return e=e.displayName,e||(e=t.displayName||t.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case St:return t=e.displayName||null,t!==null?t:ue(e.type)||"Memo";case qe:t=e._payload,e=e._init;try{return ue(e(t))}catch{}}return null}function fe(e){var t=e.type;switch(e.tag){case 24:return"Cache";case 9:return(t.displayName||"Context")+".Consumer";case 10:return(t._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=t.render,e=e.displayName||e.name||"",t.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return t;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return ue(t);case 8:return t===pe?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof t=="function")return t.displayName||t.name||null;if(typeof t=="string")return t}return null}function me(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function xe(e){var t=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(t==="checkbox"||t==="radio")}function it(e){var t=xe(e)?"checked":"value",n=Object.getOwnPropertyDescriptor(e.constructor.prototype,t),s=""+e[t];if(!e.hasOwnProperty(t)&&typeof n<"u"&&typeof n.get=="function"&&typeof n.set=="function"){var a=n.get,i=n.set;return Object.defineProperty(e,t,{configurable:!0,get:function(){return a.call(this)},set:function(u){s=""+u,i.call(this,u)}}),Object.defineProperty(e,t,{enumerable:n.enumerable}),{getValue:function(){return s},setValue:function(u){s=""+u},stopTracking:function(){e._valueTracker=null,delete e[t]}}}}function zr(e){e._valueTracker||(e._valueTracker=it(e))}function xo(e){if(!e)return!1;var t=e._valueTracker;if(!t)return!0;var n=t.getValue(),s="";return e&&(s=xe(e)?e.checked?"true":"false":e.value),e=s,e!==n?(t.setValue(e),!0):!1}function Fr(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function la(e,t){var n=t.checked;return $({},t,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:n??e._wrapperState.initialChecked})}function ko(e,t){var n=t.defaultValue==null?"":t.defaultValue,s=t.checked!=null?t.checked:t.defaultChecked;n=me(t.value!=null?t.value:n),e._wrapperState={initialChecked:s,initialValue:n,controlled:t.type==="checkbox"||t.type==="radio"?t.checked!=null:t.value!=null}}function wo(e,t){t=t.checked,t!=null&&q(e,"checked",t,!1)}function ca(e,t){wo(e,t);var n=me(t.value),s=t.type;if(n!=null)s==="number"?(n===0&&e.value===""||e.value!=n)&&(e.value=""+n):e.value!==""+n&&(e.value=""+n);else if(s==="submit"||s==="reset"){e.removeAttribute("value");return}t.hasOwnProperty("value")?ua(e,t.type,n):t.hasOwnProperty("defaultValue")&&ua(e,t.type,me(t.defaultValue)),t.checked==null&&t.defaultChecked!=null&&(e.defaultChecked=!!t.defaultChecked)}function jo(e,t,n){if(t.hasOwnProperty("value")||t.hasOwnProperty("defaultValue")){var s=t.type;if(!(s!=="submit"&&s!=="reset"||t.value!==void 0&&t.value!==null))return;t=""+e._wrapperState.initialValue,n||t===e.value||(e.value=t),e.defaultValue=t}n=e.name,n!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,n!==""&&(e.name=n)}function ua(e,t,n){(t!=="number"||Fr(e.ownerDocument)!==e)&&(n==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+n&&(e.defaultValue=""+n))}var Xn=Array.isArray;function Nn(e,t,n,s){if(e=e.options,t){t={};for(var a=0;a<n.length;a++)t["$"+n[a]]=!0;for(n=0;n<e.length;n++)a=t.hasOwnProperty("$"+e[n].value),e[n].selected!==a&&(e[n].selected=a),a&&s&&(e[n].defaultSelected=!0)}else{for(n=""+me(n),t=null,a=0;a<e.length;a++){if(e[a].value===n){e[a].selected=!0,s&&(e[a].defaultSelected=!0);return}t!==null||e[a].disabled||(t=e[a])}t!==null&&(t.selected=!0)}}function da(e,t){if(t.dangerouslySetInnerHTML!=null)throw Error(l(91));return $({},t,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function bo(e,t){var n=t.value;if(n==null){if(n=t.children,t=t.defaultValue,n!=null){if(t!=null)throw Error(l(92));if(Xn(n)){if(1<n.length)throw Error(l(93));n=n[0]}t=n}t==null&&(t=""),n=t}e._wrapperState={initialValue:me(n)}}function So(e,t){var n=me(t.value),s=me(t.defaultValue);n!=null&&(n=""+n,n!==e.value&&(e.value=n),t.defaultValue==null&&e.defaultValue!==n&&(e.defaultValue=n)),s!=null&&(e.defaultValue=""+s)}function No(e){var t=e.textContent;t===e._wrapperState.initialValue&&t!==""&&t!==null&&(e.value=t)}function Co(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function ma(e,t){return e==null||e==="http://www.w3.org/1999/xhtml"?Co(t):e==="http://www.w3.org/2000/svg"&&t==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var Br,_o=(function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(t,n,s,a){MSApp.execUnsafeLocalFunction(function(){return e(t,n,s,a)})}:e})(function(e,t){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=t;else{for(Br=Br||document.createElement("div"),Br.innerHTML="<svg>"+t.valueOf().toString()+"</svg>",t=Br.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;t.firstChild;)e.appendChild(t.firstChild)}});function Yn(e,t){if(t){var n=e.firstChild;if(n&&n===e.lastChild&&n.nodeType===3){n.nodeValue=t;return}}e.textContent=t}var Jn={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},ed=["Webkit","ms","Moz","O"];Object.keys(Jn).forEach(function(e){ed.forEach(function(t){t=t+e.charAt(0).toUpperCase()+e.substring(1),Jn[t]=Jn[e]})});function To(e,t,n){return t==null||typeof t=="boolean"||t===""?"":n||typeof t!="number"||t===0||Jn.hasOwnProperty(e)&&Jn[e]?(""+t).trim():t+"px"}function Eo(e,t){e=e.style;for(var n in t)if(t.hasOwnProperty(n)){var s=n.indexOf("--")===0,a=To(n,t[n],s);n==="float"&&(n="cssFloat"),s?e.setProperty(n,a):e[n]=a}}var td=$({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function ha(e,t){if(t){if(td[e]&&(t.children!=null||t.dangerouslySetInnerHTML!=null))throw Error(l(137,e));if(t.dangerouslySetInnerHTML!=null){if(t.children!=null)throw Error(l(60));if(typeof t.dangerouslySetInnerHTML!="object"||!("__html"in t.dangerouslySetInnerHTML))throw Error(l(61))}if(t.style!=null&&typeof t.style!="object")throw Error(l(62))}}function pa(e,t){if(e.indexOf("-")===-1)return typeof t.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var fa=null;function ga(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var va=null,Cn=null,_n=null;function Mo(e){if(e=kr(e)){if(typeof va!="function")throw Error(l(280));var t=e.stateNode;t&&(t=ls(t),va(e.stateNode,e.type,t))}}function Po(e){Cn?_n?_n.push(e):_n=[e]:Cn=e}function Lo(){if(Cn){var e=Cn,t=_n;if(_n=Cn=null,Mo(e),t)for(e=0;e<t.length;e++)Mo(t[e])}}function Ro(e,t){return e(t)}function Ao(){}var ya=!1;function Do(e,t,n){if(ya)return e(t,n);ya=!0;try{return Ro(e,t,n)}finally{ya=!1,(Cn!==null||_n!==null)&&(Ao(),Lo())}}function Zn(e,t){var n=e.stateNode;if(n===null)return null;var s=ls(n);if(s===null)return null;n=s[t];e:switch(t){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(s=!s.disabled)||(e=e.type,s=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!s;break e;default:e=!1}if(e)return null;if(n&&typeof n!="function")throw Error(l(231,t,typeof n));return n}var xa=!1;if(M)try{var er={};Object.defineProperty(er,"passive",{get:function(){xa=!0}}),window.addEventListener("test",er,er),window.removeEventListener("test",er,er)}catch{xa=!1}function nd(e,t,n,s,a,i,u,h,p){var j=Array.prototype.slice.call(arguments,3);try{t.apply(n,j)}catch(E){this.onError(E)}}var tr=!1,Or=null,Wr=!1,ka=null,rd={onError:function(e){tr=!0,Or=e}};function sd(e,t,n,s,a,i,u,h,p){tr=!1,Or=null,nd.apply(rd,arguments)}function ad(e,t,n,s,a,i,u,h,p){if(sd.apply(this,arguments),tr){if(tr){var j=Or;tr=!1,Or=null}else throw Error(l(198));Wr||(Wr=!0,ka=j)}}function ln(e){var t=e,n=e;if(e.alternate)for(;t.return;)t=t.return;else{e=t;do t=e,(t.flags&4098)!==0&&(n=t.return),e=t.return;while(e)}return t.tag===3?n:null}function Io(e){if(e.tag===13){var t=e.memoizedState;if(t===null&&(e=e.alternate,e!==null&&(t=e.memoizedState)),t!==null)return t.dehydrated}return null}function zo(e){if(ln(e)!==e)throw Error(l(188))}function id(e){var t=e.alternate;if(!t){if(t=ln(e),t===null)throw Error(l(188));return t!==e?null:e}for(var n=e,s=t;;){var a=n.return;if(a===null)break;var i=a.alternate;if(i===null){if(s=a.return,s!==null){n=s;continue}break}if(a.child===i.child){for(i=a.child;i;){if(i===n)return zo(a),e;if(i===s)return zo(a),t;i=i.sibling}throw Error(l(188))}if(n.return!==s.return)n=a,s=i;else{for(var u=!1,h=a.child;h;){if(h===n){u=!0,n=a,s=i;break}if(h===s){u=!0,s=a,n=i;break}h=h.sibling}if(!u){for(h=i.child;h;){if(h===n){u=!0,n=i,s=a;break}if(h===s){u=!0,s=i,n=a;break}h=h.sibling}if(!u)throw Error(l(189))}}if(n.alternate!==s)throw Error(l(190))}if(n.tag!==3)throw Error(l(188));return n.stateNode.current===n?e:t}function Fo(e){return e=id(e),e!==null?Bo(e):null}function Bo(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var t=Bo(e);if(t!==null)return t;e=e.sibling}return null}var Oo=c.unstable_scheduleCallback,Wo=c.unstable_cancelCallback,od=c.unstable_shouldYield,ld=c.unstable_requestPaint,Te=c.unstable_now,cd=c.unstable_getCurrentPriorityLevel,wa=c.unstable_ImmediatePriority,Uo=c.unstable_UserBlockingPriority,Ur=c.unstable_NormalPriority,ud=c.unstable_LowPriority,$o=c.unstable_IdlePriority,$r=null,Nt=null;function dd(e){if(Nt&&typeof Nt.onCommitFiberRoot=="function")try{Nt.onCommitFiberRoot($r,e,void 0,(e.current.flags&128)===128)}catch{}}var vt=Math.clz32?Math.clz32:pd,md=Math.log,hd=Math.LN2;function pd(e){return e>>>=0,e===0?32:31-(md(e)/hd|0)|0}var Vr=64,Hr=4194304;function nr(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function Gr(e,t){var n=e.pendingLanes;if(n===0)return 0;var s=0,a=e.suspendedLanes,i=e.pingedLanes,u=n&268435455;if(u!==0){var h=u&~a;h!==0?s=nr(h):(i&=u,i!==0&&(s=nr(i)))}else u=n&~a,u!==0?s=nr(u):i!==0&&(s=nr(i));if(s===0)return 0;if(t!==0&&t!==s&&(t&a)===0&&(a=s&-s,i=t&-t,a>=i||a===16&&(i&4194240)!==0))return t;if((s&4)!==0&&(s|=n&16),t=e.entangledLanes,t!==0)for(e=e.entanglements,t&=s;0<t;)n=31-vt(t),a=1<<n,s|=e[n],t&=~a;return s}function fd(e,t){switch(e){case 1:case 2:case 4:return t+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return t+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function gd(e,t){for(var n=e.suspendedLanes,s=e.pingedLanes,a=e.expirationTimes,i=e.pendingLanes;0<i;){var u=31-vt(i),h=1<<u,p=a[u];p===-1?((h&n)===0||(h&s)!==0)&&(a[u]=fd(h,t)):p<=t&&(e.expiredLanes|=h),i&=~h}}function ja(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function Vo(){var e=Vr;return Vr<<=1,(Vr&4194240)===0&&(Vr=64),e}function ba(e){for(var t=[],n=0;31>n;n++)t.push(e);return t}function rr(e,t,n){e.pendingLanes|=t,t!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,t=31-vt(t),e[t]=n}function vd(e,t){var n=e.pendingLanes&~t;e.pendingLanes=t,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=t,e.mutableReadLanes&=t,e.entangledLanes&=t,t=e.entanglements;var s=e.eventTimes;for(e=e.expirationTimes;0<n;){var a=31-vt(n),i=1<<a;t[a]=0,s[a]=-1,e[a]=-1,n&=~i}}function Sa(e,t){var n=e.entangledLanes|=t;for(e=e.entanglements;n;){var s=31-vt(n),a=1<<s;a&t|e[s]&t&&(e[s]|=t),n&=~a}}var he=0;function Ho(e){return e&=-e,1<e?4<e?(e&268435455)!==0?16:536870912:4:1}var Go,Na,Ko,qo,Qo,Ca=!1,Kr=[],Ot=null,Wt=null,Ut=null,sr=new Map,ar=new Map,$t=[],yd="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function Xo(e,t){switch(e){case"focusin":case"focusout":Ot=null;break;case"dragenter":case"dragleave":Wt=null;break;case"mouseover":case"mouseout":Ut=null;break;case"pointerover":case"pointerout":sr.delete(t.pointerId);break;case"gotpointercapture":case"lostpointercapture":ar.delete(t.pointerId)}}function ir(e,t,n,s,a,i){return e===null||e.nativeEvent!==i?(e={blockedOn:t,domEventName:n,eventSystemFlags:s,nativeEvent:i,targetContainers:[a]},t!==null&&(t=kr(t),t!==null&&Na(t)),e):(e.eventSystemFlags|=s,t=e.targetContainers,a!==null&&t.indexOf(a)===-1&&t.push(a),e)}function xd(e,t,n,s,a){switch(t){case"focusin":return Ot=ir(Ot,e,t,n,s,a),!0;case"dragenter":return Wt=ir(Wt,e,t,n,s,a),!0;case"mouseover":return Ut=ir(Ut,e,t,n,s,a),!0;case"pointerover":var i=a.pointerId;return sr.set(i,ir(sr.get(i)||null,e,t,n,s,a)),!0;case"gotpointercapture":return i=a.pointerId,ar.set(i,ir(ar.get(i)||null,e,t,n,s,a)),!0}return!1}function Yo(e){var t=cn(e.target);if(t!==null){var n=ln(t);if(n!==null){if(t=n.tag,t===13){if(t=Io(n),t!==null){e.blockedOn=t,Qo(e.priority,function(){Ko(n)});return}}else if(t===3&&n.stateNode.current.memoizedState.isDehydrated){e.blockedOn=n.tag===3?n.stateNode.containerInfo:null;return}}}e.blockedOn=null}function qr(e){if(e.blockedOn!==null)return!1;for(var t=e.targetContainers;0<t.length;){var n=Ta(e.domEventName,e.eventSystemFlags,t[0],e.nativeEvent);if(n===null){n=e.nativeEvent;var s=new n.constructor(n.type,n);fa=s,n.target.dispatchEvent(s),fa=null}else return t=kr(n),t!==null&&Na(t),e.blockedOn=n,!1;t.shift()}return!0}function Jo(e,t,n){qr(e)&&n.delete(t)}function kd(){Ca=!1,Ot!==null&&qr(Ot)&&(Ot=null),Wt!==null&&qr(Wt)&&(Wt=null),Ut!==null&&qr(Ut)&&(Ut=null),sr.forEach(Jo),ar.forEach(Jo)}function or(e,t){e.blockedOn===t&&(e.blockedOn=null,Ca||(Ca=!0,c.unstable_scheduleCallback(c.unstable_NormalPriority,kd)))}function lr(e){function t(a){return or(a,e)}if(0<Kr.length){or(Kr[0],e);for(var n=1;n<Kr.length;n++){var s=Kr[n];s.blockedOn===e&&(s.blockedOn=null)}}for(Ot!==null&&or(Ot,e),Wt!==null&&or(Wt,e),Ut!==null&&or(Ut,e),sr.forEach(t),ar.forEach(t),n=0;n<$t.length;n++)s=$t[n],s.blockedOn===e&&(s.blockedOn=null);for(;0<$t.length&&(n=$t[0],n.blockedOn===null);)Yo(n),n.blockedOn===null&&$t.shift()}var Tn=ne.ReactCurrentBatchConfig,Qr=!0;function wd(e,t,n,s){var a=he,i=Tn.transition;Tn.transition=null;try{he=1,_a(e,t,n,s)}finally{he=a,Tn.transition=i}}function jd(e,t,n,s){var a=he,i=Tn.transition;Tn.transition=null;try{he=4,_a(e,t,n,s)}finally{he=a,Tn.transition=i}}function _a(e,t,n,s){if(Qr){var a=Ta(e,t,n,s);if(a===null)Ha(e,t,s,Xr,n),Xo(e,s);else if(xd(a,e,t,n,s))s.stopPropagation();else if(Xo(e,s),t&4&&-1<yd.indexOf(e)){for(;a!==null;){var i=kr(a);if(i!==null&&Go(i),i=Ta(e,t,n,s),i===null&&Ha(e,t,s,Xr,n),i===a)break;a=i}a!==null&&s.stopPropagation()}else Ha(e,t,s,null,n)}}var Xr=null;function Ta(e,t,n,s){if(Xr=null,e=ga(s),e=cn(e),e!==null)if(t=ln(e),t===null)e=null;else if(n=t.tag,n===13){if(e=Io(t),e!==null)return e;e=null}else if(n===3){if(t.stateNode.current.memoizedState.isDehydrated)return t.tag===3?t.stateNode.containerInfo:null;e=null}else t!==e&&(e=null);return Xr=e,null}function Zo(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(cd()){case wa:return 1;case Uo:return 4;case Ur:case ud:return 16;case $o:return 536870912;default:return 16}default:return 16}}var Vt=null,Ea=null,Yr=null;function el(){if(Yr)return Yr;var e,t=Ea,n=t.length,s,a="value"in Vt?Vt.value:Vt.textContent,i=a.length;for(e=0;e<n&&t[e]===a[e];e++);var u=n-e;for(s=1;s<=u&&t[n-s]===a[i-s];s++);return Yr=a.slice(e,1<s?1-s:void 0)}function Jr(e){var t=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&t===13&&(e=13)):e=t,e===10&&(e=13),32<=e||e===13?e:0}function Zr(){return!0}function tl(){return!1}function ot(e){function t(n,s,a,i,u){this._reactName=n,this._targetInst=a,this.type=s,this.nativeEvent=i,this.target=u,this.currentTarget=null;for(var h in e)e.hasOwnProperty(h)&&(n=e[h],this[h]=n?n(i):i[h]);return this.isDefaultPrevented=(i.defaultPrevented!=null?i.defaultPrevented:i.returnValue===!1)?Zr:tl,this.isPropagationStopped=tl,this}return $(t.prototype,{preventDefault:function(){this.defaultPrevented=!0;var n=this.nativeEvent;n&&(n.preventDefault?n.preventDefault():typeof n.returnValue!="unknown"&&(n.returnValue=!1),this.isDefaultPrevented=Zr)},stopPropagation:function(){var n=this.nativeEvent;n&&(n.stopPropagation?n.stopPropagation():typeof n.cancelBubble!="unknown"&&(n.cancelBubble=!0),this.isPropagationStopped=Zr)},persist:function(){},isPersistent:Zr}),t}var En={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},Ma=ot(En),cr=$({},En,{view:0,detail:0}),bd=ot(cr),Pa,La,ur,es=$({},cr,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:Aa,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==ur&&(ur&&e.type==="mousemove"?(Pa=e.screenX-ur.screenX,La=e.screenY-ur.screenY):La=Pa=0,ur=e),Pa)},movementY:function(e){return"movementY"in e?e.movementY:La}}),nl=ot(es),Sd=$({},es,{dataTransfer:0}),Nd=ot(Sd),Cd=$({},cr,{relatedTarget:0}),Ra=ot(Cd),_d=$({},En,{animationName:0,elapsedTime:0,pseudoElement:0}),Td=ot(_d),Ed=$({},En,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),Md=ot(Ed),Pd=$({},En,{data:0}),rl=ot(Pd),Ld={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},Rd={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},Ad={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function Dd(e){var t=this.nativeEvent;return t.getModifierState?t.getModifierState(e):(e=Ad[e])?!!t[e]:!1}function Aa(){return Dd}var Id=$({},cr,{key:function(e){if(e.key){var t=Ld[e.key]||e.key;if(t!=="Unidentified")return t}return e.type==="keypress"?(e=Jr(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?Rd[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:Aa,charCode:function(e){return e.type==="keypress"?Jr(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?Jr(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),zd=ot(Id),Fd=$({},es,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),sl=ot(Fd),Bd=$({},cr,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:Aa}),Od=ot(Bd),Wd=$({},En,{propertyName:0,elapsedTime:0,pseudoElement:0}),Ud=ot(Wd),$d=$({},es,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),Vd=ot($d),Hd=[9,13,27,32],Da=M&&"CompositionEvent"in window,dr=null;M&&"documentMode"in document&&(dr=document.documentMode);var Gd=M&&"TextEvent"in window&&!dr,al=M&&(!Da||dr&&8<dr&&11>=dr),il=" ",ol=!1;function ll(e,t){switch(e){case"keyup":return Hd.indexOf(t.keyCode)!==-1;case"keydown":return t.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function cl(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var Mn=!1;function Kd(e,t){switch(e){case"compositionend":return cl(t);case"keypress":return t.which!==32?null:(ol=!0,il);case"textInput":return e=t.data,e===il&&ol?null:e;default:return null}}function qd(e,t){if(Mn)return e==="compositionend"||!Da&&ll(e,t)?(e=el(),Yr=Ea=Vt=null,Mn=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(t.ctrlKey||t.altKey||t.metaKey)||t.ctrlKey&&t.altKey){if(t.char&&1<t.char.length)return t.char;if(t.which)return String.fromCharCode(t.which)}return null;case"compositionend":return al&&t.locale!=="ko"?null:t.data;default:return null}}var Qd={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function ul(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t==="input"?!!Qd[e.type]:t==="textarea"}function dl(e,t,n,s){Po(s),t=as(t,"onChange"),0<t.length&&(n=new Ma("onChange","change",null,n,s),e.push({event:n,listeners:t}))}var mr=null,hr=null;function Xd(e){El(e,0)}function ts(e){var t=Dn(e);if(xo(t))return e}function Yd(e,t){if(e==="change")return t}var ml=!1;if(M){var Ia;if(M){var za="oninput"in document;if(!za){var hl=document.createElement("div");hl.setAttribute("oninput","return;"),za=typeof hl.oninput=="function"}Ia=za}else Ia=!1;ml=Ia&&(!document.documentMode||9<document.documentMode)}function pl(){mr&&(mr.detachEvent("onpropertychange",fl),hr=mr=null)}function fl(e){if(e.propertyName==="value"&&ts(hr)){var t=[];dl(t,hr,e,ga(e)),Do(Xd,t)}}function Jd(e,t,n){e==="focusin"?(pl(),mr=t,hr=n,mr.attachEvent("onpropertychange",fl)):e==="focusout"&&pl()}function Zd(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return ts(hr)}function em(e,t){if(e==="click")return ts(t)}function tm(e,t){if(e==="input"||e==="change")return ts(t)}function nm(e,t){return e===t&&(e!==0||1/e===1/t)||e!==e&&t!==t}var yt=typeof Object.is=="function"?Object.is:nm;function pr(e,t){if(yt(e,t))return!0;if(typeof e!="object"||e===null||typeof t!="object"||t===null)return!1;var n=Object.keys(e),s=Object.keys(t);if(n.length!==s.length)return!1;for(s=0;s<n.length;s++){var a=n[s];if(!w.call(t,a)||!yt(e[a],t[a]))return!1}return!0}function gl(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function vl(e,t){var n=gl(e);e=0;for(var s;n;){if(n.nodeType===3){if(s=e+n.textContent.length,e<=t&&s>=t)return{node:n,offset:t-e};e=s}e:{for(;n;){if(n.nextSibling){n=n.nextSibling;break e}n=n.parentNode}n=void 0}n=gl(n)}}function yl(e,t){return e&&t?e===t?!0:e&&e.nodeType===3?!1:t&&t.nodeType===3?yl(e,t.parentNode):"contains"in e?e.contains(t):e.compareDocumentPosition?!!(e.compareDocumentPosition(t)&16):!1:!1}function xl(){for(var e=window,t=Fr();t instanceof e.HTMLIFrameElement;){try{var n=typeof t.contentWindow.location.href=="string"}catch{n=!1}if(n)e=t.contentWindow;else break;t=Fr(e.document)}return t}function Fa(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t&&(t==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||t==="textarea"||e.contentEditable==="true")}function rm(e){var t=xl(),n=e.focusedElem,s=e.selectionRange;if(t!==n&&n&&n.ownerDocument&&yl(n.ownerDocument.documentElement,n)){if(s!==null&&Fa(n)){if(t=s.start,e=s.end,e===void 0&&(e=t),"selectionStart"in n)n.selectionStart=t,n.selectionEnd=Math.min(e,n.value.length);else if(e=(t=n.ownerDocument||document)&&t.defaultView||window,e.getSelection){e=e.getSelection();var a=n.textContent.length,i=Math.min(s.start,a);s=s.end===void 0?i:Math.min(s.end,a),!e.extend&&i>s&&(a=s,s=i,i=a),a=vl(n,i);var u=vl(n,s);a&&u&&(e.rangeCount!==1||e.anchorNode!==a.node||e.anchorOffset!==a.offset||e.focusNode!==u.node||e.focusOffset!==u.offset)&&(t=t.createRange(),t.setStart(a.node,a.offset),e.removeAllRanges(),i>s?(e.addRange(t),e.extend(u.node,u.offset)):(t.setEnd(u.node,u.offset),e.addRange(t)))}}for(t=[],e=n;e=e.parentNode;)e.nodeType===1&&t.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof n.focus=="function"&&n.focus(),n=0;n<t.length;n++)e=t[n],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var sm=M&&"documentMode"in document&&11>=document.documentMode,Pn=null,Ba=null,fr=null,Oa=!1;function kl(e,t,n){var s=n.window===n?n.document:n.nodeType===9?n:n.ownerDocument;Oa||Pn==null||Pn!==Fr(s)||(s=Pn,"selectionStart"in s&&Fa(s)?s={start:s.selectionStart,end:s.selectionEnd}:(s=(s.ownerDocument&&s.ownerDocument.defaultView||window).getSelection(),s={anchorNode:s.anchorNode,anchorOffset:s.anchorOffset,focusNode:s.focusNode,focusOffset:s.focusOffset}),fr&&pr(fr,s)||(fr=s,s=as(Ba,"onSelect"),0<s.length&&(t=new Ma("onSelect","select",null,t,n),e.push({event:t,listeners:s}),t.target=Pn)))}function ns(e,t){var n={};return n[e.toLowerCase()]=t.toLowerCase(),n["Webkit"+e]="webkit"+t,n["Moz"+e]="moz"+t,n}var Ln={animationend:ns("Animation","AnimationEnd"),animationiteration:ns("Animation","AnimationIteration"),animationstart:ns("Animation","AnimationStart"),transitionend:ns("Transition","TransitionEnd")},Wa={},wl={};M&&(wl=document.createElement("div").style,"AnimationEvent"in window||(delete Ln.animationend.animation,delete Ln.animationiteration.animation,delete Ln.animationstart.animation),"TransitionEvent"in window||delete Ln.transitionend.transition);function rs(e){if(Wa[e])return Wa[e];if(!Ln[e])return e;var t=Ln[e],n;for(n in t)if(t.hasOwnProperty(n)&&n in wl)return Wa[e]=t[n];return e}var jl=rs("animationend"),bl=rs("animationiteration"),Sl=rs("animationstart"),Nl=rs("transitionend"),Cl=new Map,_l="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function Ht(e,t){Cl.set(e,t),f(t,[e])}for(var Ua=0;Ua<_l.length;Ua++){var $a=_l[Ua],am=$a.toLowerCase(),im=$a[0].toUpperCase()+$a.slice(1);Ht(am,"on"+im)}Ht(jl,"onAnimationEnd"),Ht(bl,"onAnimationIteration"),Ht(Sl,"onAnimationStart"),Ht("dblclick","onDoubleClick"),Ht("focusin","onFocus"),Ht("focusout","onBlur"),Ht(Nl,"onTransitionEnd"),v("onMouseEnter",["mouseout","mouseover"]),v("onMouseLeave",["mouseout","mouseover"]),v("onPointerEnter",["pointerout","pointerover"]),v("onPointerLeave",["pointerout","pointerover"]),f("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),f("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),f("onBeforeInput",["compositionend","keypress","textInput","paste"]),f("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),f("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),f("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var gr="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),om=new Set("cancel close invalid load scroll toggle".split(" ").concat(gr));function Tl(e,t,n){var s=e.type||"unknown-event";e.currentTarget=n,ad(s,t,void 0,e),e.currentTarget=null}function El(e,t){t=(t&4)!==0;for(var n=0;n<e.length;n++){var s=e[n],a=s.event;s=s.listeners;e:{var i=void 0;if(t)for(var u=s.length-1;0<=u;u--){var h=s[u],p=h.instance,j=h.currentTarget;if(h=h.listener,p!==i&&a.isPropagationStopped())break e;Tl(a,h,j),i=p}else for(u=0;u<s.length;u++){if(h=s[u],p=h.instance,j=h.currentTarget,h=h.listener,p!==i&&a.isPropagationStopped())break e;Tl(a,h,j),i=p}}}if(Wr)throw e=ka,Wr=!1,ka=null,e}function ve(e,t){var n=t[Ya];n===void 0&&(n=t[Ya]=new Set);var s=e+"__bubble";n.has(s)||(Ml(t,e,2,!1),n.add(s))}function Va(e,t,n){var s=0;t&&(s|=4),Ml(n,e,s,t)}var ss="_reactListening"+Math.random().toString(36).slice(2);function vr(e){if(!e[ss]){e[ss]=!0,d.forEach(function(n){n!=="selectionchange"&&(om.has(n)||Va(n,!1,e),Va(n,!0,e))});var t=e.nodeType===9?e:e.ownerDocument;t===null||t[ss]||(t[ss]=!0,Va("selectionchange",!1,t))}}function Ml(e,t,n,s){switch(Zo(t)){case 1:var a=wd;break;case 4:a=jd;break;default:a=_a}n=a.bind(null,t,n,e),a=void 0,!xa||t!=="touchstart"&&t!=="touchmove"&&t!=="wheel"||(a=!0),s?a!==void 0?e.addEventListener(t,n,{capture:!0,passive:a}):e.addEventListener(t,n,!0):a!==void 0?e.addEventListener(t,n,{passive:a}):e.addEventListener(t,n,!1)}function Ha(e,t,n,s,a){var i=s;if((t&1)===0&&(t&2)===0&&s!==null)e:for(;;){if(s===null)return;var u=s.tag;if(u===3||u===4){var h=s.stateNode.containerInfo;if(h===a||h.nodeType===8&&h.parentNode===a)break;if(u===4)for(u=s.return;u!==null;){var p=u.tag;if((p===3||p===4)&&(p=u.stateNode.containerInfo,p===a||p.nodeType===8&&p.parentNode===a))return;u=u.return}for(;h!==null;){if(u=cn(h),u===null)return;if(p=u.tag,p===5||p===6){s=i=u;continue e}h=h.parentNode}}s=s.return}Do(function(){var j=i,E=ga(n),L=[];e:{var _=Cl.get(e);if(_!==void 0){var W=Ma,V=e;switch(e){case"keypress":if(Jr(n)===0)break e;case"keydown":case"keyup":W=zd;break;case"focusin":V="focus",W=Ra;break;case"focusout":V="blur",W=Ra;break;case"beforeblur":case"afterblur":W=Ra;break;case"click":if(n.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":W=nl;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":W=Nd;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":W=Od;break;case jl:case bl:case Sl:W=Td;break;case Nl:W=Ud;break;case"scroll":W=bd;break;case"wheel":W=Vd;break;case"copy":case"cut":case"paste":W=Md;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":W=sl}var H=(t&4)!==0,Ee=!H&&e==="scroll",x=H?_!==null?_+"Capture":null:_;H=[];for(var g=j,k;g!==null;){k=g;var A=k.stateNode;if(k.tag===5&&A!==null&&(k=A,x!==null&&(A=Zn(g,x),A!=null&&H.push(yr(g,A,k)))),Ee)break;g=g.return}0<H.length&&(_=new W(_,V,null,n,E),L.push({event:_,listeners:H}))}}if((t&7)===0){e:{if(_=e==="mouseover"||e==="pointerover",W=e==="mouseout"||e==="pointerout",_&&n!==fa&&(V=n.relatedTarget||n.fromElement)&&(cn(V)||V[Pt]))break e;if((W||_)&&(_=E.window===E?E:(_=E.ownerDocument)?_.defaultView||_.parentWindow:window,W?(V=n.relatedTarget||n.toElement,W=j,V=V?cn(V):null,V!==null&&(Ee=ln(V),V!==Ee||V.tag!==5&&V.tag!==6)&&(V=null)):(W=null,V=j),W!==V)){if(H=nl,A="onMouseLeave",x="onMouseEnter",g="mouse",(e==="pointerout"||e==="pointerover")&&(H=sl,A="onPointerLeave",x="onPointerEnter",g="pointer"),Ee=W==null?_:Dn(W),k=V==null?_:Dn(V),_=new H(A,g+"leave",W,n,E),_.target=Ee,_.relatedTarget=k,A=null,cn(E)===j&&(H=new H(x,g+"enter",V,n,E),H.target=k,H.relatedTarget=Ee,A=H),Ee=A,W&&V)t:{for(H=W,x=V,g=0,k=H;k;k=Rn(k))g++;for(k=0,A=x;A;A=Rn(A))k++;for(;0<g-k;)H=Rn(H),g--;for(;0<k-g;)x=Rn(x),k--;for(;g--;){if(H===x||x!==null&&H===x.alternate)break t;H=Rn(H),x=Rn(x)}H=null}else H=null;W!==null&&Pl(L,_,W,H,!1),V!==null&&Ee!==null&&Pl(L,Ee,V,H,!0)}}e:{if(_=j?Dn(j):window,W=_.nodeName&&_.nodeName.toLowerCase(),W==="select"||W==="input"&&_.type==="file")var G=Yd;else if(ul(_))if(ml)G=tm;else{G=Zd;var X=Jd}else(W=_.nodeName)&&W.toLowerCase()==="input"&&(_.type==="checkbox"||_.type==="radio")&&(G=em);if(G&&(G=G(e,j))){dl(L,G,n,E);break e}X&&X(e,_,j),e==="focusout"&&(X=_._wrapperState)&&X.controlled&&_.type==="number"&&ua(_,"number",_.value)}switch(X=j?Dn(j):window,e){case"focusin":(ul(X)||X.contentEditable==="true")&&(Pn=X,Ba=j,fr=null);break;case"focusout":fr=Ba=Pn=null;break;case"mousedown":Oa=!0;break;case"contextmenu":case"mouseup":case"dragend":Oa=!1,kl(L,n,E);break;case"selectionchange":if(sm)break;case"keydown":case"keyup":kl(L,n,E)}var Y;if(Da)e:{switch(e){case"compositionstart":var ee="onCompositionStart";break e;case"compositionend":ee="onCompositionEnd";break e;case"compositionupdate":ee="onCompositionUpdate";break e}ee=void 0}else Mn?ll(e,n)&&(ee="onCompositionEnd"):e==="keydown"&&n.keyCode===229&&(ee="onCompositionStart");ee&&(al&&n.locale!=="ko"&&(Mn||ee!=="onCompositionStart"?ee==="onCompositionEnd"&&Mn&&(Y=el()):(Vt=E,Ea="value"in Vt?Vt.value:Vt.textContent,Mn=!0)),X=as(j,ee),0<X.length&&(ee=new rl(ee,e,null,n,E),L.push({event:ee,listeners:X}),Y?ee.data=Y:(Y=cl(n),Y!==null&&(ee.data=Y)))),(Y=Gd?Kd(e,n):qd(e,n))&&(j=as(j,"onBeforeInput"),0<j.length&&(E=new rl("onBeforeInput","beforeinput",null,n,E),L.push({event:E,listeners:j}),E.data=Y))}El(L,t)})}function yr(e,t,n){return{instance:e,listener:t,currentTarget:n}}function as(e,t){for(var n=t+"Capture",s=[];e!==null;){var a=e,i=a.stateNode;a.tag===5&&i!==null&&(a=i,i=Zn(e,n),i!=null&&s.unshift(yr(e,i,a)),i=Zn(e,t),i!=null&&s.push(yr(e,i,a))),e=e.return}return s}function Rn(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function Pl(e,t,n,s,a){for(var i=t._reactName,u=[];n!==null&&n!==s;){var h=n,p=h.alternate,j=h.stateNode;if(p!==null&&p===s)break;h.tag===5&&j!==null&&(h=j,a?(p=Zn(n,i),p!=null&&u.unshift(yr(n,p,h))):a||(p=Zn(n,i),p!=null&&u.push(yr(n,p,h)))),n=n.return}u.length!==0&&e.push({event:t,listeners:u})}var lm=/\r\n?/g,cm=/\u0000|\uFFFD/g;function Ll(e){return(typeof e=="string"?e:""+e).replace(lm,`
`).replace(cm,"")}function is(e,t,n){if(t=Ll(t),Ll(e)!==t&&n)throw Error(l(425))}function os(){}var Ga=null,Ka=null;function qa(e,t){return e==="textarea"||e==="noscript"||typeof t.children=="string"||typeof t.children=="number"||typeof t.dangerouslySetInnerHTML=="object"&&t.dangerouslySetInnerHTML!==null&&t.dangerouslySetInnerHTML.__html!=null}var Qa=typeof setTimeout=="function"?setTimeout:void 0,um=typeof clearTimeout=="function"?clearTimeout:void 0,Rl=typeof Promise=="function"?Promise:void 0,dm=typeof queueMicrotask=="function"?queueMicrotask:typeof Rl<"u"?function(e){return Rl.resolve(null).then(e).catch(mm)}:Qa;function mm(e){setTimeout(function(){throw e})}function Xa(e,t){var n=t,s=0;do{var a=n.nextSibling;if(e.removeChild(n),a&&a.nodeType===8)if(n=a.data,n==="/$"){if(s===0){e.removeChild(a),lr(t);return}s--}else n!=="$"&&n!=="$?"&&n!=="$!"||s++;n=a}while(n);lr(t)}function Gt(e){for(;e!=null;e=e.nextSibling){var t=e.nodeType;if(t===1||t===3)break;if(t===8){if(t=e.data,t==="$"||t==="$!"||t==="$?")break;if(t==="/$")return null}}return e}function Al(e){e=e.previousSibling;for(var t=0;e;){if(e.nodeType===8){var n=e.data;if(n==="$"||n==="$!"||n==="$?"){if(t===0)return e;t--}else n==="/$"&&t++}e=e.previousSibling}return null}var An=Math.random().toString(36).slice(2),Ct="__reactFiber$"+An,xr="__reactProps$"+An,Pt="__reactContainer$"+An,Ya="__reactEvents$"+An,hm="__reactListeners$"+An,pm="__reactHandles$"+An;function cn(e){var t=e[Ct];if(t)return t;for(var n=e.parentNode;n;){if(t=n[Pt]||n[Ct]){if(n=t.alternate,t.child!==null||n!==null&&n.child!==null)for(e=Al(e);e!==null;){if(n=e[Ct])return n;e=Al(e)}return t}e=n,n=e.parentNode}return null}function kr(e){return e=e[Ct]||e[Pt],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function Dn(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(l(33))}function ls(e){return e[xr]||null}var Ja=[],In=-1;function Kt(e){return{current:e}}function ye(e){0>In||(e.current=Ja[In],Ja[In]=null,In--)}function ge(e,t){In++,Ja[In]=e.current,e.current=t}var qt={},Ue=Kt(qt),Qe=Kt(!1),un=qt;function zn(e,t){var n=e.type.contextTypes;if(!n)return qt;var s=e.stateNode;if(s&&s.__reactInternalMemoizedUnmaskedChildContext===t)return s.__reactInternalMemoizedMaskedChildContext;var a={},i;for(i in n)a[i]=t[i];return s&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=t,e.__reactInternalMemoizedMaskedChildContext=a),a}function Xe(e){return e=e.childContextTypes,e!=null}function cs(){ye(Qe),ye(Ue)}function Dl(e,t,n){if(Ue.current!==qt)throw Error(l(168));ge(Ue,t),ge(Qe,n)}function Il(e,t,n){var s=e.stateNode;if(t=t.childContextTypes,typeof s.getChildContext!="function")return n;s=s.getChildContext();for(var a in s)if(!(a in t))throw Error(l(108,fe(e)||"Unknown",a));return $({},n,s)}function us(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||qt,un=Ue.current,ge(Ue,e),ge(Qe,Qe.current),!0}function zl(e,t,n){var s=e.stateNode;if(!s)throw Error(l(169));n?(e=Il(e,t,un),s.__reactInternalMemoizedMergedChildContext=e,ye(Qe),ye(Ue),ge(Ue,e)):ye(Qe),ge(Qe,n)}var Lt=null,ds=!1,Za=!1;function Fl(e){Lt===null?Lt=[e]:Lt.push(e)}function fm(e){ds=!0,Fl(e)}function Qt(){if(!Za&&Lt!==null){Za=!0;var e=0,t=he;try{var n=Lt;for(he=1;e<n.length;e++){var s=n[e];do s=s(!0);while(s!==null)}Lt=null,ds=!1}catch(a){throw Lt!==null&&(Lt=Lt.slice(e+1)),Oo(wa,Qt),a}finally{he=t,Za=!1}}return null}var Fn=[],Bn=0,ms=null,hs=0,dt=[],mt=0,dn=null,Rt=1,At="";function mn(e,t){Fn[Bn++]=hs,Fn[Bn++]=ms,ms=e,hs=t}function Bl(e,t,n){dt[mt++]=Rt,dt[mt++]=At,dt[mt++]=dn,dn=e;var s=Rt;e=At;var a=32-vt(s)-1;s&=~(1<<a),n+=1;var i=32-vt(t)+a;if(30<i){var u=a-a%5;i=(s&(1<<u)-1).toString(32),s>>=u,a-=u,Rt=1<<32-vt(t)+a|n<<a|s,At=i+e}else Rt=1<<i|n<<a|s,At=e}function ei(e){e.return!==null&&(mn(e,1),Bl(e,1,0))}function ti(e){for(;e===ms;)ms=Fn[--Bn],Fn[Bn]=null,hs=Fn[--Bn],Fn[Bn]=null;for(;e===dn;)dn=dt[--mt],dt[mt]=null,At=dt[--mt],dt[mt]=null,Rt=dt[--mt],dt[mt]=null}var lt=null,ct=null,ke=!1,xt=null;function Ol(e,t){var n=gt(5,null,null,0);n.elementType="DELETED",n.stateNode=t,n.return=e,t=e.deletions,t===null?(e.deletions=[n],e.flags|=16):t.push(n)}function Wl(e,t){switch(e.tag){case 5:var n=e.type;return t=t.nodeType!==1||n.toLowerCase()!==t.nodeName.toLowerCase()?null:t,t!==null?(e.stateNode=t,lt=e,ct=Gt(t.firstChild),!0):!1;case 6:return t=e.pendingProps===""||t.nodeType!==3?null:t,t!==null?(e.stateNode=t,lt=e,ct=null,!0):!1;case 13:return t=t.nodeType!==8?null:t,t!==null?(n=dn!==null?{id:Rt,overflow:At}:null,e.memoizedState={dehydrated:t,treeContext:n,retryLane:1073741824},n=gt(18,null,null,0),n.stateNode=t,n.return=e,e.child=n,lt=e,ct=null,!0):!1;default:return!1}}function ni(e){return(e.mode&1)!==0&&(e.flags&128)===0}function ri(e){if(ke){var t=ct;if(t){var n=t;if(!Wl(e,t)){if(ni(e))throw Error(l(418));t=Gt(n.nextSibling);var s=lt;t&&Wl(e,t)?Ol(s,n):(e.flags=e.flags&-4097|2,ke=!1,lt=e)}}else{if(ni(e))throw Error(l(418));e.flags=e.flags&-4097|2,ke=!1,lt=e}}}function Ul(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;lt=e}function ps(e){if(e!==lt)return!1;if(!ke)return Ul(e),ke=!0,!1;var t;if((t=e.tag!==3)&&!(t=e.tag!==5)&&(t=e.type,t=t!=="head"&&t!=="body"&&!qa(e.type,e.memoizedProps)),t&&(t=ct)){if(ni(e))throw $l(),Error(l(418));for(;t;)Ol(e,t),t=Gt(t.nextSibling)}if(Ul(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(l(317));e:{for(e=e.nextSibling,t=0;e;){if(e.nodeType===8){var n=e.data;if(n==="/$"){if(t===0){ct=Gt(e.nextSibling);break e}t--}else n!=="$"&&n!=="$!"&&n!=="$?"||t++}e=e.nextSibling}ct=null}}else ct=lt?Gt(e.stateNode.nextSibling):null;return!0}function $l(){for(var e=ct;e;)e=Gt(e.nextSibling)}function On(){ct=lt=null,ke=!1}function si(e){xt===null?xt=[e]:xt.push(e)}var gm=ne.ReactCurrentBatchConfig;function wr(e,t,n){if(e=n.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(n._owner){if(n=n._owner,n){if(n.tag!==1)throw Error(l(309));var s=n.stateNode}if(!s)throw Error(l(147,e));var a=s,i=""+e;return t!==null&&t.ref!==null&&typeof t.ref=="function"&&t.ref._stringRef===i?t.ref:(t=function(u){var h=a.refs;u===null?delete h[i]:h[i]=u},t._stringRef=i,t)}if(typeof e!="string")throw Error(l(284));if(!n._owner)throw Error(l(290,e))}return e}function fs(e,t){throw e=Object.prototype.toString.call(t),Error(l(31,e==="[object Object]"?"object with keys {"+Object.keys(t).join(", ")+"}":e))}function Vl(e){var t=e._init;return t(e._payload)}function Hl(e){function t(x,g){if(e){var k=x.deletions;k===null?(x.deletions=[g],x.flags|=16):k.push(g)}}function n(x,g){if(!e)return null;for(;g!==null;)t(x,g),g=g.sibling;return null}function s(x,g){for(x=new Map;g!==null;)g.key!==null?x.set(g.key,g):x.set(g.index,g),g=g.sibling;return x}function a(x,g){return x=rn(x,g),x.index=0,x.sibling=null,x}function i(x,g,k){return x.index=k,e?(k=x.alternate,k!==null?(k=k.index,k<g?(x.flags|=2,g):k):(x.flags|=2,g)):(x.flags|=1048576,g)}function u(x){return e&&x.alternate===null&&(x.flags|=2),x}function h(x,g,k,A){return g===null||g.tag!==6?(g=Qi(k,x.mode,A),g.return=x,g):(g=a(g,k),g.return=x,g)}function p(x,g,k,A){var G=k.type;return G===J?E(x,g,k.props.children,A,k.key):g!==null&&(g.elementType===G||typeof G=="object"&&G!==null&&G.$$typeof===qe&&Vl(G)===g.type)?(A=a(g,k.props),A.ref=wr(x,g,k),A.return=x,A):(A=Bs(k.type,k.key,k.props,null,x.mode,A),A.ref=wr(x,g,k),A.return=x,A)}function j(x,g,k,A){return g===null||g.tag!==4||g.stateNode.containerInfo!==k.containerInfo||g.stateNode.implementation!==k.implementation?(g=Xi(k,x.mode,A),g.return=x,g):(g=a(g,k.children||[]),g.return=x,g)}function E(x,g,k,A,G){return g===null||g.tag!==7?(g=kn(k,x.mode,A,G),g.return=x,g):(g=a(g,k),g.return=x,g)}function L(x,g,k){if(typeof g=="string"&&g!==""||typeof g=="number")return g=Qi(""+g,x.mode,k),g.return=x,g;if(typeof g=="object"&&g!==null){switch(g.$$typeof){case ie:return k=Bs(g.type,g.key,g.props,null,x.mode,k),k.ref=wr(x,null,g),k.return=x,k;case F:return g=Xi(g,x.mode,k),g.return=x,g;case qe:var A=g._init;return L(x,A(g._payload),k)}if(Xn(g)||Z(g))return g=kn(g,x.mode,k,null),g.return=x,g;fs(x,g)}return null}function _(x,g,k,A){var G=g!==null?g.key:null;if(typeof k=="string"&&k!==""||typeof k=="number")return G!==null?null:h(x,g,""+k,A);if(typeof k=="object"&&k!==null){switch(k.$$typeof){case ie:return k.key===G?p(x,g,k,A):null;case F:return k.key===G?j(x,g,k,A):null;case qe:return G=k._init,_(x,g,G(k._payload),A)}if(Xn(k)||Z(k))return G!==null?null:E(x,g,k,A,null);fs(x,k)}return null}function W(x,g,k,A,G){if(typeof A=="string"&&A!==""||typeof A=="number")return x=x.get(k)||null,h(g,x,""+A,G);if(typeof A=="object"&&A!==null){switch(A.$$typeof){case ie:return x=x.get(A.key===null?k:A.key)||null,p(g,x,A,G);case F:return x=x.get(A.key===null?k:A.key)||null,j(g,x,A,G);case qe:var X=A._init;return W(x,g,k,X(A._payload),G)}if(Xn(A)||Z(A))return x=x.get(k)||null,E(g,x,A,G,null);fs(g,A)}return null}function V(x,g,k,A){for(var G=null,X=null,Y=g,ee=g=0,Fe=null;Y!==null&&ee<k.length;ee++){Y.index>ee?(Fe=Y,Y=null):Fe=Y.sibling;var de=_(x,Y,k[ee],A);if(de===null){Y===null&&(Y=Fe);break}e&&Y&&de.alternate===null&&t(x,Y),g=i(de,g,ee),X===null?G=de:X.sibling=de,X=de,Y=Fe}if(ee===k.length)return n(x,Y),ke&&mn(x,ee),G;if(Y===null){for(;ee<k.length;ee++)Y=L(x,k[ee],A),Y!==null&&(g=i(Y,g,ee),X===null?G=Y:X.sibling=Y,X=Y);return ke&&mn(x,ee),G}for(Y=s(x,Y);ee<k.length;ee++)Fe=W(Y,x,ee,k[ee],A),Fe!==null&&(e&&Fe.alternate!==null&&Y.delete(Fe.key===null?ee:Fe.key),g=i(Fe,g,ee),X===null?G=Fe:X.sibling=Fe,X=Fe);return e&&Y.forEach(function(sn){return t(x,sn)}),ke&&mn(x,ee),G}function H(x,g,k,A){var G=Z(k);if(typeof G!="function")throw Error(l(150));if(k=G.call(k),k==null)throw Error(l(151));for(var X=G=null,Y=g,ee=g=0,Fe=null,de=k.next();Y!==null&&!de.done;ee++,de=k.next()){Y.index>ee?(Fe=Y,Y=null):Fe=Y.sibling;var sn=_(x,Y,de.value,A);if(sn===null){Y===null&&(Y=Fe);break}e&&Y&&sn.alternate===null&&t(x,Y),g=i(sn,g,ee),X===null?G=sn:X.sibling=sn,X=sn,Y=Fe}if(de.done)return n(x,Y),ke&&mn(x,ee),G;if(Y===null){for(;!de.done;ee++,de=k.next())de=L(x,de.value,A),de!==null&&(g=i(de,g,ee),X===null?G=de:X.sibling=de,X=de);return ke&&mn(x,ee),G}for(Y=s(x,Y);!de.done;ee++,de=k.next())de=W(Y,x,ee,de.value,A),de!==null&&(e&&de.alternate!==null&&Y.delete(de.key===null?ee:de.key),g=i(de,g,ee),X===null?G=de:X.sibling=de,X=de);return e&&Y.forEach(function(Qm){return t(x,Qm)}),ke&&mn(x,ee),G}function Ee(x,g,k,A){if(typeof k=="object"&&k!==null&&k.type===J&&k.key===null&&(k=k.props.children),typeof k=="object"&&k!==null){switch(k.$$typeof){case ie:e:{for(var G=k.key,X=g;X!==null;){if(X.key===G){if(G=k.type,G===J){if(X.tag===7){n(x,X.sibling),g=a(X,k.props.children),g.return=x,x=g;break e}}else if(X.elementType===G||typeof G=="object"&&G!==null&&G.$$typeof===qe&&Vl(G)===X.type){n(x,X.sibling),g=a(X,k.props),g.ref=wr(x,X,k),g.return=x,x=g;break e}n(x,X);break}else t(x,X);X=X.sibling}k.type===J?(g=kn(k.props.children,x.mode,A,k.key),g.return=x,x=g):(A=Bs(k.type,k.key,k.props,null,x.mode,A),A.ref=wr(x,g,k),A.return=x,x=A)}return u(x);case F:e:{for(X=k.key;g!==null;){if(g.key===X)if(g.tag===4&&g.stateNode.containerInfo===k.containerInfo&&g.stateNode.implementation===k.implementation){n(x,g.sibling),g=a(g,k.children||[]),g.return=x,x=g;break e}else{n(x,g);break}else t(x,g);g=g.sibling}g=Xi(k,x.mode,A),g.return=x,x=g}return u(x);case qe:return X=k._init,Ee(x,g,X(k._payload),A)}if(Xn(k))return V(x,g,k,A);if(Z(k))return H(x,g,k,A);fs(x,k)}return typeof k=="string"&&k!==""||typeof k=="number"?(k=""+k,g!==null&&g.tag===6?(n(x,g.sibling),g=a(g,k),g.return=x,x=g):(n(x,g),g=Qi(k,x.mode,A),g.return=x,x=g),u(x)):n(x,g)}return Ee}var Wn=Hl(!0),Gl=Hl(!1),gs=Kt(null),vs=null,Un=null,ai=null;function ii(){ai=Un=vs=null}function oi(e){var t=gs.current;ye(gs),e._currentValue=t}function li(e,t,n){for(;e!==null;){var s=e.alternate;if((e.childLanes&t)!==t?(e.childLanes|=t,s!==null&&(s.childLanes|=t)):s!==null&&(s.childLanes&t)!==t&&(s.childLanes|=t),e===n)break;e=e.return}}function $n(e,t){vs=e,ai=Un=null,e=e.dependencies,e!==null&&e.firstContext!==null&&((e.lanes&t)!==0&&(Ye=!0),e.firstContext=null)}function ht(e){var t=e._currentValue;if(ai!==e)if(e={context:e,memoizedValue:t,next:null},Un===null){if(vs===null)throw Error(l(308));Un=e,vs.dependencies={lanes:0,firstContext:e}}else Un=Un.next=e;return t}var hn=null;function ci(e){hn===null?hn=[e]:hn.push(e)}function Kl(e,t,n,s){var a=t.interleaved;return a===null?(n.next=n,ci(t)):(n.next=a.next,a.next=n),t.interleaved=n,Dt(e,s)}function Dt(e,t){e.lanes|=t;var n=e.alternate;for(n!==null&&(n.lanes|=t),n=e,e=e.return;e!==null;)e.childLanes|=t,n=e.alternate,n!==null&&(n.childLanes|=t),n=e,e=e.return;return n.tag===3?n.stateNode:null}var Xt=!1;function ui(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function ql(e,t){e=e.updateQueue,t.updateQueue===e&&(t.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function It(e,t){return{eventTime:e,lane:t,tag:0,payload:null,callback:null,next:null}}function Yt(e,t,n){var s=e.updateQueue;if(s===null)return null;if(s=s.shared,(le&2)!==0){var a=s.pending;return a===null?t.next=t:(t.next=a.next,a.next=t),s.pending=t,Dt(e,n)}return a=s.interleaved,a===null?(t.next=t,ci(s)):(t.next=a.next,a.next=t),s.interleaved=t,Dt(e,n)}function ys(e,t,n){if(t=t.updateQueue,t!==null&&(t=t.shared,(n&4194240)!==0)){var s=t.lanes;s&=e.pendingLanes,n|=s,t.lanes=n,Sa(e,n)}}function Ql(e,t){var n=e.updateQueue,s=e.alternate;if(s!==null&&(s=s.updateQueue,n===s)){var a=null,i=null;if(n=n.firstBaseUpdate,n!==null){do{var u={eventTime:n.eventTime,lane:n.lane,tag:n.tag,payload:n.payload,callback:n.callback,next:null};i===null?a=i=u:i=i.next=u,n=n.next}while(n!==null);i===null?a=i=t:i=i.next=t}else a=i=t;n={baseState:s.baseState,firstBaseUpdate:a,lastBaseUpdate:i,shared:s.shared,effects:s.effects},e.updateQueue=n;return}e=n.lastBaseUpdate,e===null?n.firstBaseUpdate=t:e.next=t,n.lastBaseUpdate=t}function xs(e,t,n,s){var a=e.updateQueue;Xt=!1;var i=a.firstBaseUpdate,u=a.lastBaseUpdate,h=a.shared.pending;if(h!==null){a.shared.pending=null;var p=h,j=p.next;p.next=null,u===null?i=j:u.next=j,u=p;var E=e.alternate;E!==null&&(E=E.updateQueue,h=E.lastBaseUpdate,h!==u&&(h===null?E.firstBaseUpdate=j:h.next=j,E.lastBaseUpdate=p))}if(i!==null){var L=a.baseState;u=0,E=j=p=null,h=i;do{var _=h.lane,W=h.eventTime;if((s&_)===_){E!==null&&(E=E.next={eventTime:W,lane:0,tag:h.tag,payload:h.payload,callback:h.callback,next:null});e:{var V=e,H=h;switch(_=t,W=n,H.tag){case 1:if(V=H.payload,typeof V=="function"){L=V.call(W,L,_);break e}L=V;break e;case 3:V.flags=V.flags&-65537|128;case 0:if(V=H.payload,_=typeof V=="function"?V.call(W,L,_):V,_==null)break e;L=$({},L,_);break e;case 2:Xt=!0}}h.callback!==null&&h.lane!==0&&(e.flags|=64,_=a.effects,_===null?a.effects=[h]:_.push(h))}else W={eventTime:W,lane:_,tag:h.tag,payload:h.payload,callback:h.callback,next:null},E===null?(j=E=W,p=L):E=E.next=W,u|=_;if(h=h.next,h===null){if(h=a.shared.pending,h===null)break;_=h,h=_.next,_.next=null,a.lastBaseUpdate=_,a.shared.pending=null}}while(!0);if(E===null&&(p=L),a.baseState=p,a.firstBaseUpdate=j,a.lastBaseUpdate=E,t=a.shared.interleaved,t!==null){a=t;do u|=a.lane,a=a.next;while(a!==t)}else i===null&&(a.shared.lanes=0);gn|=u,e.lanes=u,e.memoizedState=L}}function Xl(e,t,n){if(e=t.effects,t.effects=null,e!==null)for(t=0;t<e.length;t++){var s=e[t],a=s.callback;if(a!==null){if(s.callback=null,s=n,typeof a!="function")throw Error(l(191,a));a.call(s)}}}var jr={},_t=Kt(jr),br=Kt(jr),Sr=Kt(jr);function pn(e){if(e===jr)throw Error(l(174));return e}function di(e,t){switch(ge(Sr,t),ge(br,e),ge(_t,jr),e=t.nodeType,e){case 9:case 11:t=(t=t.documentElement)?t.namespaceURI:ma(null,"");break;default:e=e===8?t.parentNode:t,t=e.namespaceURI||null,e=e.tagName,t=ma(t,e)}ye(_t),ge(_t,t)}function Vn(){ye(_t),ye(br),ye(Sr)}function Yl(e){pn(Sr.current);var t=pn(_t.current),n=ma(t,e.type);t!==n&&(ge(br,e),ge(_t,n))}function mi(e){br.current===e&&(ye(_t),ye(br))}var je=Kt(0);function ks(e){for(var t=e;t!==null;){if(t.tag===13){var n=t.memoizedState;if(n!==null&&(n=n.dehydrated,n===null||n.data==="$?"||n.data==="$!"))return t}else if(t.tag===19&&t.memoizedProps.revealOrder!==void 0){if((t.flags&128)!==0)return t}else if(t.child!==null){t.child.return=t,t=t.child;continue}if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return null;t=t.return}t.sibling.return=t.return,t=t.sibling}return null}var hi=[];function pi(){for(var e=0;e<hi.length;e++)hi[e]._workInProgressVersionPrimary=null;hi.length=0}var ws=ne.ReactCurrentDispatcher,fi=ne.ReactCurrentBatchConfig,fn=0,be=null,Re=null,Ie=null,js=!1,Nr=!1,Cr=0,vm=0;function $e(){throw Error(l(321))}function gi(e,t){if(t===null)return!1;for(var n=0;n<t.length&&n<e.length;n++)if(!yt(e[n],t[n]))return!1;return!0}function vi(e,t,n,s,a,i){if(fn=i,be=t,t.memoizedState=null,t.updateQueue=null,t.lanes=0,ws.current=e===null||e.memoizedState===null?wm:jm,e=n(s,a),Nr){i=0;do{if(Nr=!1,Cr=0,25<=i)throw Error(l(301));i+=1,Ie=Re=null,t.updateQueue=null,ws.current=bm,e=n(s,a)}while(Nr)}if(ws.current=Ns,t=Re!==null&&Re.next!==null,fn=0,Ie=Re=be=null,js=!1,t)throw Error(l(300));return e}function yi(){var e=Cr!==0;return Cr=0,e}function Tt(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return Ie===null?be.memoizedState=Ie=e:Ie=Ie.next=e,Ie}function pt(){if(Re===null){var e=be.alternate;e=e!==null?e.memoizedState:null}else e=Re.next;var t=Ie===null?be.memoizedState:Ie.next;if(t!==null)Ie=t,Re=e;else{if(e===null)throw Error(l(310));Re=e,e={memoizedState:Re.memoizedState,baseState:Re.baseState,baseQueue:Re.baseQueue,queue:Re.queue,next:null},Ie===null?be.memoizedState=Ie=e:Ie=Ie.next=e}return Ie}function _r(e,t){return typeof t=="function"?t(e):t}function xi(e){var t=pt(),n=t.queue;if(n===null)throw Error(l(311));n.lastRenderedReducer=e;var s=Re,a=s.baseQueue,i=n.pending;if(i!==null){if(a!==null){var u=a.next;a.next=i.next,i.next=u}s.baseQueue=a=i,n.pending=null}if(a!==null){i=a.next,s=s.baseState;var h=u=null,p=null,j=i;do{var E=j.lane;if((fn&E)===E)p!==null&&(p=p.next={lane:0,action:j.action,hasEagerState:j.hasEagerState,eagerState:j.eagerState,next:null}),s=j.hasEagerState?j.eagerState:e(s,j.action);else{var L={lane:E,action:j.action,hasEagerState:j.hasEagerState,eagerState:j.eagerState,next:null};p===null?(h=p=L,u=s):p=p.next=L,be.lanes|=E,gn|=E}j=j.next}while(j!==null&&j!==i);p===null?u=s:p.next=h,yt(s,t.memoizedState)||(Ye=!0),t.memoizedState=s,t.baseState=u,t.baseQueue=p,n.lastRenderedState=s}if(e=n.interleaved,e!==null){a=e;do i=a.lane,be.lanes|=i,gn|=i,a=a.next;while(a!==e)}else a===null&&(n.lanes=0);return[t.memoizedState,n.dispatch]}function ki(e){var t=pt(),n=t.queue;if(n===null)throw Error(l(311));n.lastRenderedReducer=e;var s=n.dispatch,a=n.pending,i=t.memoizedState;if(a!==null){n.pending=null;var u=a=a.next;do i=e(i,u.action),u=u.next;while(u!==a);yt(i,t.memoizedState)||(Ye=!0),t.memoizedState=i,t.baseQueue===null&&(t.baseState=i),n.lastRenderedState=i}return[i,s]}function Jl(){}function Zl(e,t){var n=be,s=pt(),a=t(),i=!yt(s.memoizedState,a);if(i&&(s.memoizedState=a,Ye=!0),s=s.queue,wi(nc.bind(null,n,s,e),[e]),s.getSnapshot!==t||i||Ie!==null&&Ie.memoizedState.tag&1){if(n.flags|=2048,Tr(9,tc.bind(null,n,s,a,t),void 0,null),ze===null)throw Error(l(349));(fn&30)!==0||ec(n,t,a)}return a}function ec(e,t,n){e.flags|=16384,e={getSnapshot:t,value:n},t=be.updateQueue,t===null?(t={lastEffect:null,stores:null},be.updateQueue=t,t.stores=[e]):(n=t.stores,n===null?t.stores=[e]:n.push(e))}function tc(e,t,n,s){t.value=n,t.getSnapshot=s,rc(t)&&sc(e)}function nc(e,t,n){return n(function(){rc(t)&&sc(e)})}function rc(e){var t=e.getSnapshot;e=e.value;try{var n=t();return!yt(e,n)}catch{return!0}}function sc(e){var t=Dt(e,1);t!==null&&bt(t,e,1,-1)}function ac(e){var t=Tt();return typeof e=="function"&&(e=e()),t.memoizedState=t.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:_r,lastRenderedState:e},t.queue=e,e=e.dispatch=km.bind(null,be,e),[t.memoizedState,e]}function Tr(e,t,n,s){return e={tag:e,create:t,destroy:n,deps:s,next:null},t=be.updateQueue,t===null?(t={lastEffect:null,stores:null},be.updateQueue=t,t.lastEffect=e.next=e):(n=t.lastEffect,n===null?t.lastEffect=e.next=e:(s=n.next,n.next=e,e.next=s,t.lastEffect=e)),e}function ic(){return pt().memoizedState}function bs(e,t,n,s){var a=Tt();be.flags|=e,a.memoizedState=Tr(1|t,n,void 0,s===void 0?null:s)}function Ss(e,t,n,s){var a=pt();s=s===void 0?null:s;var i=void 0;if(Re!==null){var u=Re.memoizedState;if(i=u.destroy,s!==null&&gi(s,u.deps)){a.memoizedState=Tr(t,n,i,s);return}}be.flags|=e,a.memoizedState=Tr(1|t,n,i,s)}function oc(e,t){return bs(8390656,8,e,t)}function wi(e,t){return Ss(2048,8,e,t)}function lc(e,t){return Ss(4,2,e,t)}function cc(e,t){return Ss(4,4,e,t)}function uc(e,t){if(typeof t=="function")return e=e(),t(e),function(){t(null)};if(t!=null)return e=e(),t.current=e,function(){t.current=null}}function dc(e,t,n){return n=n!=null?n.concat([e]):null,Ss(4,4,uc.bind(null,t,e),n)}function ji(){}function mc(e,t){var n=pt();t=t===void 0?null:t;var s=n.memoizedState;return s!==null&&t!==null&&gi(t,s[1])?s[0]:(n.memoizedState=[e,t],e)}function hc(e,t){var n=pt();t=t===void 0?null:t;var s=n.memoizedState;return s!==null&&t!==null&&gi(t,s[1])?s[0]:(e=e(),n.memoizedState=[e,t],e)}function pc(e,t,n){return(fn&21)===0?(e.baseState&&(e.baseState=!1,Ye=!0),e.memoizedState=n):(yt(n,t)||(n=Vo(),be.lanes|=n,gn|=n,e.baseState=!0),t)}function ym(e,t){var n=he;he=n!==0&&4>n?n:4,e(!0);var s=fi.transition;fi.transition={};try{e(!1),t()}finally{he=n,fi.transition=s}}function fc(){return pt().memoizedState}function xm(e,t,n){var s=tn(e);if(n={lane:s,action:n,hasEagerState:!1,eagerState:null,next:null},gc(e))vc(t,n);else if(n=Kl(e,t,n,s),n!==null){var a=Ke();bt(n,e,s,a),yc(n,t,s)}}function km(e,t,n){var s=tn(e),a={lane:s,action:n,hasEagerState:!1,eagerState:null,next:null};if(gc(e))vc(t,a);else{var i=e.alternate;if(e.lanes===0&&(i===null||i.lanes===0)&&(i=t.lastRenderedReducer,i!==null))try{var u=t.lastRenderedState,h=i(u,n);if(a.hasEagerState=!0,a.eagerState=h,yt(h,u)){var p=t.interleaved;p===null?(a.next=a,ci(t)):(a.next=p.next,p.next=a),t.interleaved=a;return}}catch{}finally{}n=Kl(e,t,a,s),n!==null&&(a=Ke(),bt(n,e,s,a),yc(n,t,s))}}function gc(e){var t=e.alternate;return e===be||t!==null&&t===be}function vc(e,t){Nr=js=!0;var n=e.pending;n===null?t.next=t:(t.next=n.next,n.next=t),e.pending=t}function yc(e,t,n){if((n&4194240)!==0){var s=t.lanes;s&=e.pendingLanes,n|=s,t.lanes=n,Sa(e,n)}}var Ns={readContext:ht,useCallback:$e,useContext:$e,useEffect:$e,useImperativeHandle:$e,useInsertionEffect:$e,useLayoutEffect:$e,useMemo:$e,useReducer:$e,useRef:$e,useState:$e,useDebugValue:$e,useDeferredValue:$e,useTransition:$e,useMutableSource:$e,useSyncExternalStore:$e,useId:$e,unstable_isNewReconciler:!1},wm={readContext:ht,useCallback:function(e,t){return Tt().memoizedState=[e,t===void 0?null:t],e},useContext:ht,useEffect:oc,useImperativeHandle:function(e,t,n){return n=n!=null?n.concat([e]):null,bs(4194308,4,uc.bind(null,t,e),n)},useLayoutEffect:function(e,t){return bs(4194308,4,e,t)},useInsertionEffect:function(e,t){return bs(4,2,e,t)},useMemo:function(e,t){var n=Tt();return t=t===void 0?null:t,e=e(),n.memoizedState=[e,t],e},useReducer:function(e,t,n){var s=Tt();return t=n!==void 0?n(t):t,s.memoizedState=s.baseState=t,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:t},s.queue=e,e=e.dispatch=xm.bind(null,be,e),[s.memoizedState,e]},useRef:function(e){var t=Tt();return e={current:e},t.memoizedState=e},useState:ac,useDebugValue:ji,useDeferredValue:function(e){return Tt().memoizedState=e},useTransition:function(){var e=ac(!1),t=e[0];return e=ym.bind(null,e[1]),Tt().memoizedState=e,[t,e]},useMutableSource:function(){},useSyncExternalStore:function(e,t,n){var s=be,a=Tt();if(ke){if(n===void 0)throw Error(l(407));n=n()}else{if(n=t(),ze===null)throw Error(l(349));(fn&30)!==0||ec(s,t,n)}a.memoizedState=n;var i={value:n,getSnapshot:t};return a.queue=i,oc(nc.bind(null,s,i,e),[e]),s.flags|=2048,Tr(9,tc.bind(null,s,i,n,t),void 0,null),n},useId:function(){var e=Tt(),t=ze.identifierPrefix;if(ke){var n=At,s=Rt;n=(s&~(1<<32-vt(s)-1)).toString(32)+n,t=":"+t+"R"+n,n=Cr++,0<n&&(t+="H"+n.toString(32)),t+=":"}else n=vm++,t=":"+t+"r"+n.toString(32)+":";return e.memoizedState=t},unstable_isNewReconciler:!1},jm={readContext:ht,useCallback:mc,useContext:ht,useEffect:wi,useImperativeHandle:dc,useInsertionEffect:lc,useLayoutEffect:cc,useMemo:hc,useReducer:xi,useRef:ic,useState:function(){return xi(_r)},useDebugValue:ji,useDeferredValue:function(e){var t=pt();return pc(t,Re.memoizedState,e)},useTransition:function(){var e=xi(_r)[0],t=pt().memoizedState;return[e,t]},useMutableSource:Jl,useSyncExternalStore:Zl,useId:fc,unstable_isNewReconciler:!1},bm={readContext:ht,useCallback:mc,useContext:ht,useEffect:wi,useImperativeHandle:dc,useInsertionEffect:lc,useLayoutEffect:cc,useMemo:hc,useReducer:ki,useRef:ic,useState:function(){return ki(_r)},useDebugValue:ji,useDeferredValue:function(e){var t=pt();return Re===null?t.memoizedState=e:pc(t,Re.memoizedState,e)},useTransition:function(){var e=ki(_r)[0],t=pt().memoizedState;return[e,t]},useMutableSource:Jl,useSyncExternalStore:Zl,useId:fc,unstable_isNewReconciler:!1};function kt(e,t){if(e&&e.defaultProps){t=$({},t),e=e.defaultProps;for(var n in e)t[n]===void 0&&(t[n]=e[n]);return t}return t}function bi(e,t,n,s){t=e.memoizedState,n=n(s,t),n=n==null?t:$({},t,n),e.memoizedState=n,e.lanes===0&&(e.updateQueue.baseState=n)}var Cs={isMounted:function(e){return(e=e._reactInternals)?ln(e)===e:!1},enqueueSetState:function(e,t,n){e=e._reactInternals;var s=Ke(),a=tn(e),i=It(s,a);i.payload=t,n!=null&&(i.callback=n),t=Yt(e,i,a),t!==null&&(bt(t,e,a,s),ys(t,e,a))},enqueueReplaceState:function(e,t,n){e=e._reactInternals;var s=Ke(),a=tn(e),i=It(s,a);i.tag=1,i.payload=t,n!=null&&(i.callback=n),t=Yt(e,i,a),t!==null&&(bt(t,e,a,s),ys(t,e,a))},enqueueForceUpdate:function(e,t){e=e._reactInternals;var n=Ke(),s=tn(e),a=It(n,s);a.tag=2,t!=null&&(a.callback=t),t=Yt(e,a,s),t!==null&&(bt(t,e,s,n),ys(t,e,s))}};function xc(e,t,n,s,a,i,u){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(s,i,u):t.prototype&&t.prototype.isPureReactComponent?!pr(n,s)||!pr(a,i):!0}function kc(e,t,n){var s=!1,a=qt,i=t.contextType;return typeof i=="object"&&i!==null?i=ht(i):(a=Xe(t)?un:Ue.current,s=t.contextTypes,i=(s=s!=null)?zn(e,a):qt),t=new t(n,i),e.memoizedState=t.state!==null&&t.state!==void 0?t.state:null,t.updater=Cs,e.stateNode=t,t._reactInternals=e,s&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=a,e.__reactInternalMemoizedMaskedChildContext=i),t}function wc(e,t,n,s){e=t.state,typeof t.componentWillReceiveProps=="function"&&t.componentWillReceiveProps(n,s),typeof t.UNSAFE_componentWillReceiveProps=="function"&&t.UNSAFE_componentWillReceiveProps(n,s),t.state!==e&&Cs.enqueueReplaceState(t,t.state,null)}function Si(e,t,n,s){var a=e.stateNode;a.props=n,a.state=e.memoizedState,a.refs={},ui(e);var i=t.contextType;typeof i=="object"&&i!==null?a.context=ht(i):(i=Xe(t)?un:Ue.current,a.context=zn(e,i)),a.state=e.memoizedState,i=t.getDerivedStateFromProps,typeof i=="function"&&(bi(e,t,i,n),a.state=e.memoizedState),typeof t.getDerivedStateFromProps=="function"||typeof a.getSnapshotBeforeUpdate=="function"||typeof a.UNSAFE_componentWillMount!="function"&&typeof a.componentWillMount!="function"||(t=a.state,typeof a.componentWillMount=="function"&&a.componentWillMount(),typeof a.UNSAFE_componentWillMount=="function"&&a.UNSAFE_componentWillMount(),t!==a.state&&Cs.enqueueReplaceState(a,a.state,null),xs(e,n,a,s),a.state=e.memoizedState),typeof a.componentDidMount=="function"&&(e.flags|=4194308)}function Hn(e,t){try{var n="",s=t;do n+=ce(s),s=s.return;while(s);var a=n}catch(i){a=`
Error generating stack: `+i.message+`
`+i.stack}return{value:e,source:t,stack:a,digest:null}}function Ni(e,t,n){return{value:e,source:null,stack:n??null,digest:t??null}}function Ci(e,t){try{console.error(t.value)}catch(n){setTimeout(function(){throw n})}}var Sm=typeof WeakMap=="function"?WeakMap:Map;function jc(e,t,n){n=It(-1,n),n.tag=3,n.payload={element:null};var s=t.value;return n.callback=function(){Rs||(Rs=!0,Wi=s),Ci(e,t)},n}function bc(e,t,n){n=It(-1,n),n.tag=3;var s=e.type.getDerivedStateFromError;if(typeof s=="function"){var a=t.value;n.payload=function(){return s(a)},n.callback=function(){Ci(e,t)}}var i=e.stateNode;return i!==null&&typeof i.componentDidCatch=="function"&&(n.callback=function(){Ci(e,t),typeof s!="function"&&(Zt===null?Zt=new Set([this]):Zt.add(this));var u=t.stack;this.componentDidCatch(t.value,{componentStack:u!==null?u:""})}),n}function Sc(e,t,n){var s=e.pingCache;if(s===null){s=e.pingCache=new Sm;var a=new Set;s.set(t,a)}else a=s.get(t),a===void 0&&(a=new Set,s.set(t,a));a.has(n)||(a.add(n),e=Fm.bind(null,e,t,n),t.then(e,e))}function Nc(e){do{var t;if((t=e.tag===13)&&(t=e.memoizedState,t=t!==null?t.dehydrated!==null:!0),t)return e;e=e.return}while(e!==null);return null}function Cc(e,t,n,s,a){return(e.mode&1)===0?(e===t?e.flags|=65536:(e.flags|=128,n.flags|=131072,n.flags&=-52805,n.tag===1&&(n.alternate===null?n.tag=17:(t=It(-1,1),t.tag=2,Yt(n,t,1))),n.lanes|=1),e):(e.flags|=65536,e.lanes=a,e)}var Nm=ne.ReactCurrentOwner,Ye=!1;function Ge(e,t,n,s){t.child=e===null?Gl(t,null,n,s):Wn(t,e.child,n,s)}function _c(e,t,n,s,a){n=n.render;var i=t.ref;return $n(t,a),s=vi(e,t,n,s,i,a),n=yi(),e!==null&&!Ye?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~a,zt(e,t,a)):(ke&&n&&ei(t),t.flags|=1,Ge(e,t,s,a),t.child)}function Tc(e,t,n,s,a){if(e===null){var i=n.type;return typeof i=="function"&&!qi(i)&&i.defaultProps===void 0&&n.compare===null&&n.defaultProps===void 0?(t.tag=15,t.type=i,Ec(e,t,i,s,a)):(e=Bs(n.type,null,s,t,t.mode,a),e.ref=t.ref,e.return=t,t.child=e)}if(i=e.child,(e.lanes&a)===0){var u=i.memoizedProps;if(n=n.compare,n=n!==null?n:pr,n(u,s)&&e.ref===t.ref)return zt(e,t,a)}return t.flags|=1,e=rn(i,s),e.ref=t.ref,e.return=t,t.child=e}function Ec(e,t,n,s,a){if(e!==null){var i=e.memoizedProps;if(pr(i,s)&&e.ref===t.ref)if(Ye=!1,t.pendingProps=s=i,(e.lanes&a)!==0)(e.flags&131072)!==0&&(Ye=!0);else return t.lanes=e.lanes,zt(e,t,a)}return _i(e,t,n,s,a)}function Mc(e,t,n){var s=t.pendingProps,a=s.children,i=e!==null?e.memoizedState:null;if(s.mode==="hidden")if((t.mode&1)===0)t.memoizedState={baseLanes:0,cachePool:null,transitions:null},ge(Kn,ut),ut|=n;else{if((n&1073741824)===0)return e=i!==null?i.baseLanes|n:n,t.lanes=t.childLanes=1073741824,t.memoizedState={baseLanes:e,cachePool:null,transitions:null},t.updateQueue=null,ge(Kn,ut),ut|=e,null;t.memoizedState={baseLanes:0,cachePool:null,transitions:null},s=i!==null?i.baseLanes:n,ge(Kn,ut),ut|=s}else i!==null?(s=i.baseLanes|n,t.memoizedState=null):s=n,ge(Kn,ut),ut|=s;return Ge(e,t,a,n),t.child}function Pc(e,t){var n=t.ref;(e===null&&n!==null||e!==null&&e.ref!==n)&&(t.flags|=512,t.flags|=2097152)}function _i(e,t,n,s,a){var i=Xe(n)?un:Ue.current;return i=zn(t,i),$n(t,a),n=vi(e,t,n,s,i,a),s=yi(),e!==null&&!Ye?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~a,zt(e,t,a)):(ke&&s&&ei(t),t.flags|=1,Ge(e,t,n,a),t.child)}function Lc(e,t,n,s,a){if(Xe(n)){var i=!0;us(t)}else i=!1;if($n(t,a),t.stateNode===null)Ts(e,t),kc(t,n,s),Si(t,n,s,a),s=!0;else if(e===null){var u=t.stateNode,h=t.memoizedProps;u.props=h;var p=u.context,j=n.contextType;typeof j=="object"&&j!==null?j=ht(j):(j=Xe(n)?un:Ue.current,j=zn(t,j));var E=n.getDerivedStateFromProps,L=typeof E=="function"||typeof u.getSnapshotBeforeUpdate=="function";L||typeof u.UNSAFE_componentWillReceiveProps!="function"&&typeof u.componentWillReceiveProps!="function"||(h!==s||p!==j)&&wc(t,u,s,j),Xt=!1;var _=t.memoizedState;u.state=_,xs(t,s,u,a),p=t.memoizedState,h!==s||_!==p||Qe.current||Xt?(typeof E=="function"&&(bi(t,n,E,s),p=t.memoizedState),(h=Xt||xc(t,n,h,s,_,p,j))?(L||typeof u.UNSAFE_componentWillMount!="function"&&typeof u.componentWillMount!="function"||(typeof u.componentWillMount=="function"&&u.componentWillMount(),typeof u.UNSAFE_componentWillMount=="function"&&u.UNSAFE_componentWillMount()),typeof u.componentDidMount=="function"&&(t.flags|=4194308)):(typeof u.componentDidMount=="function"&&(t.flags|=4194308),t.memoizedProps=s,t.memoizedState=p),u.props=s,u.state=p,u.context=j,s=h):(typeof u.componentDidMount=="function"&&(t.flags|=4194308),s=!1)}else{u=t.stateNode,ql(e,t),h=t.memoizedProps,j=t.type===t.elementType?h:kt(t.type,h),u.props=j,L=t.pendingProps,_=u.context,p=n.contextType,typeof p=="object"&&p!==null?p=ht(p):(p=Xe(n)?un:Ue.current,p=zn(t,p));var W=n.getDerivedStateFromProps;(E=typeof W=="function"||typeof u.getSnapshotBeforeUpdate=="function")||typeof u.UNSAFE_componentWillReceiveProps!="function"&&typeof u.componentWillReceiveProps!="function"||(h!==L||_!==p)&&wc(t,u,s,p),Xt=!1,_=t.memoizedState,u.state=_,xs(t,s,u,a);var V=t.memoizedState;h!==L||_!==V||Qe.current||Xt?(typeof W=="function"&&(bi(t,n,W,s),V=t.memoizedState),(j=Xt||xc(t,n,j,s,_,V,p)||!1)?(E||typeof u.UNSAFE_componentWillUpdate!="function"&&typeof u.componentWillUpdate!="function"||(typeof u.componentWillUpdate=="function"&&u.componentWillUpdate(s,V,p),typeof u.UNSAFE_componentWillUpdate=="function"&&u.UNSAFE_componentWillUpdate(s,V,p)),typeof u.componentDidUpdate=="function"&&(t.flags|=4),typeof u.getSnapshotBeforeUpdate=="function"&&(t.flags|=1024)):(typeof u.componentDidUpdate!="function"||h===e.memoizedProps&&_===e.memoizedState||(t.flags|=4),typeof u.getSnapshotBeforeUpdate!="function"||h===e.memoizedProps&&_===e.memoizedState||(t.flags|=1024),t.memoizedProps=s,t.memoizedState=V),u.props=s,u.state=V,u.context=p,s=j):(typeof u.componentDidUpdate!="function"||h===e.memoizedProps&&_===e.memoizedState||(t.flags|=4),typeof u.getSnapshotBeforeUpdate!="function"||h===e.memoizedProps&&_===e.memoizedState||(t.flags|=1024),s=!1)}return Ti(e,t,n,s,i,a)}function Ti(e,t,n,s,a,i){Pc(e,t);var u=(t.flags&128)!==0;if(!s&&!u)return a&&zl(t,n,!1),zt(e,t,i);s=t.stateNode,Nm.current=t;var h=u&&typeof n.getDerivedStateFromError!="function"?null:s.render();return t.flags|=1,e!==null&&u?(t.child=Wn(t,e.child,null,i),t.child=Wn(t,null,h,i)):Ge(e,t,h,i),t.memoizedState=s.state,a&&zl(t,n,!0),t.child}function Rc(e){var t=e.stateNode;t.pendingContext?Dl(e,t.pendingContext,t.pendingContext!==t.context):t.context&&Dl(e,t.context,!1),di(e,t.containerInfo)}function Ac(e,t,n,s,a){return On(),si(a),t.flags|=256,Ge(e,t,n,s),t.child}var Ei={dehydrated:null,treeContext:null,retryLane:0};function Mi(e){return{baseLanes:e,cachePool:null,transitions:null}}function Dc(e,t,n){var s=t.pendingProps,a=je.current,i=!1,u=(t.flags&128)!==0,h;if((h=u)||(h=e!==null&&e.memoizedState===null?!1:(a&2)!==0),h?(i=!0,t.flags&=-129):(e===null||e.memoizedState!==null)&&(a|=1),ge(je,a&1),e===null)return ri(t),e=t.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?((t.mode&1)===0?t.lanes=1:e.data==="$!"?t.lanes=8:t.lanes=1073741824,null):(u=s.children,e=s.fallback,i?(s=t.mode,i=t.child,u={mode:"hidden",children:u},(s&1)===0&&i!==null?(i.childLanes=0,i.pendingProps=u):i=Os(u,s,0,null),e=kn(e,s,n,null),i.return=t,e.return=t,i.sibling=e,t.child=i,t.child.memoizedState=Mi(n),t.memoizedState=Ei,e):Pi(t,u));if(a=e.memoizedState,a!==null&&(h=a.dehydrated,h!==null))return Cm(e,t,u,s,h,a,n);if(i){i=s.fallback,u=t.mode,a=e.child,h=a.sibling;var p={mode:"hidden",children:s.children};return(u&1)===0&&t.child!==a?(s=t.child,s.childLanes=0,s.pendingProps=p,t.deletions=null):(s=rn(a,p),s.subtreeFlags=a.subtreeFlags&14680064),h!==null?i=rn(h,i):(i=kn(i,u,n,null),i.flags|=2),i.return=t,s.return=t,s.sibling=i,t.child=s,s=i,i=t.child,u=e.child.memoizedState,u=u===null?Mi(n):{baseLanes:u.baseLanes|n,cachePool:null,transitions:u.transitions},i.memoizedState=u,i.childLanes=e.childLanes&~n,t.memoizedState=Ei,s}return i=e.child,e=i.sibling,s=rn(i,{mode:"visible",children:s.children}),(t.mode&1)===0&&(s.lanes=n),s.return=t,s.sibling=null,e!==null&&(n=t.deletions,n===null?(t.deletions=[e],t.flags|=16):n.push(e)),t.child=s,t.memoizedState=null,s}function Pi(e,t){return t=Os({mode:"visible",children:t},e.mode,0,null),t.return=e,e.child=t}function _s(e,t,n,s){return s!==null&&si(s),Wn(t,e.child,null,n),e=Pi(t,t.pendingProps.children),e.flags|=2,t.memoizedState=null,e}function Cm(e,t,n,s,a,i,u){if(n)return t.flags&256?(t.flags&=-257,s=Ni(Error(l(422))),_s(e,t,u,s)):t.memoizedState!==null?(t.child=e.child,t.flags|=128,null):(i=s.fallback,a=t.mode,s=Os({mode:"visible",children:s.children},a,0,null),i=kn(i,a,u,null),i.flags|=2,s.return=t,i.return=t,s.sibling=i,t.child=s,(t.mode&1)!==0&&Wn(t,e.child,null,u),t.child.memoizedState=Mi(u),t.memoizedState=Ei,i);if((t.mode&1)===0)return _s(e,t,u,null);if(a.data==="$!"){if(s=a.nextSibling&&a.nextSibling.dataset,s)var h=s.dgst;return s=h,i=Error(l(419)),s=Ni(i,s,void 0),_s(e,t,u,s)}if(h=(u&e.childLanes)!==0,Ye||h){if(s=ze,s!==null){switch(u&-u){case 4:a=2;break;case 16:a=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:a=32;break;case 536870912:a=268435456;break;default:a=0}a=(a&(s.suspendedLanes|u))!==0?0:a,a!==0&&a!==i.retryLane&&(i.retryLane=a,Dt(e,a),bt(s,e,a,-1))}return Ki(),s=Ni(Error(l(421))),_s(e,t,u,s)}return a.data==="$?"?(t.flags|=128,t.child=e.child,t=Bm.bind(null,e),a._reactRetry=t,null):(e=i.treeContext,ct=Gt(a.nextSibling),lt=t,ke=!0,xt=null,e!==null&&(dt[mt++]=Rt,dt[mt++]=At,dt[mt++]=dn,Rt=e.id,At=e.overflow,dn=t),t=Pi(t,s.children),t.flags|=4096,t)}function Ic(e,t,n){e.lanes|=t;var s=e.alternate;s!==null&&(s.lanes|=t),li(e.return,t,n)}function Li(e,t,n,s,a){var i=e.memoizedState;i===null?e.memoizedState={isBackwards:t,rendering:null,renderingStartTime:0,last:s,tail:n,tailMode:a}:(i.isBackwards=t,i.rendering=null,i.renderingStartTime=0,i.last=s,i.tail=n,i.tailMode=a)}function zc(e,t,n){var s=t.pendingProps,a=s.revealOrder,i=s.tail;if(Ge(e,t,s.children,n),s=je.current,(s&2)!==0)s=s&1|2,t.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=t.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Ic(e,n,t);else if(e.tag===19)Ic(e,n,t);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===t)break e;for(;e.sibling===null;){if(e.return===null||e.return===t)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}s&=1}if(ge(je,s),(t.mode&1)===0)t.memoizedState=null;else switch(a){case"forwards":for(n=t.child,a=null;n!==null;)e=n.alternate,e!==null&&ks(e)===null&&(a=n),n=n.sibling;n=a,n===null?(a=t.child,t.child=null):(a=n.sibling,n.sibling=null),Li(t,!1,a,n,i);break;case"backwards":for(n=null,a=t.child,t.child=null;a!==null;){if(e=a.alternate,e!==null&&ks(e)===null){t.child=a;break}e=a.sibling,a.sibling=n,n=a,a=e}Li(t,!0,n,null,i);break;case"together":Li(t,!1,null,null,void 0);break;default:t.memoizedState=null}return t.child}function Ts(e,t){(t.mode&1)===0&&e!==null&&(e.alternate=null,t.alternate=null,t.flags|=2)}function zt(e,t,n){if(e!==null&&(t.dependencies=e.dependencies),gn|=t.lanes,(n&t.childLanes)===0)return null;if(e!==null&&t.child!==e.child)throw Error(l(153));if(t.child!==null){for(e=t.child,n=rn(e,e.pendingProps),t.child=n,n.return=t;e.sibling!==null;)e=e.sibling,n=n.sibling=rn(e,e.pendingProps),n.return=t;n.sibling=null}return t.child}function _m(e,t,n){switch(t.tag){case 3:Rc(t),On();break;case 5:Yl(t);break;case 1:Xe(t.type)&&us(t);break;case 4:di(t,t.stateNode.containerInfo);break;case 10:var s=t.type._context,a=t.memoizedProps.value;ge(gs,s._currentValue),s._currentValue=a;break;case 13:if(s=t.memoizedState,s!==null)return s.dehydrated!==null?(ge(je,je.current&1),t.flags|=128,null):(n&t.child.childLanes)!==0?Dc(e,t,n):(ge(je,je.current&1),e=zt(e,t,n),e!==null?e.sibling:null);ge(je,je.current&1);break;case 19:if(s=(n&t.childLanes)!==0,(e.flags&128)!==0){if(s)return zc(e,t,n);t.flags|=128}if(a=t.memoizedState,a!==null&&(a.rendering=null,a.tail=null,a.lastEffect=null),ge(je,je.current),s)break;return null;case 22:case 23:return t.lanes=0,Mc(e,t,n)}return zt(e,t,n)}var Fc,Ri,Bc,Oc;Fc=function(e,t){for(var n=t.child;n!==null;){if(n.tag===5||n.tag===6)e.appendChild(n.stateNode);else if(n.tag!==4&&n.child!==null){n.child.return=n,n=n.child;continue}if(n===t)break;for(;n.sibling===null;){if(n.return===null||n.return===t)return;n=n.return}n.sibling.return=n.return,n=n.sibling}},Ri=function(){},Bc=function(e,t,n,s){var a=e.memoizedProps;if(a!==s){e=t.stateNode,pn(_t.current);var i=null;switch(n){case"input":a=la(e,a),s=la(e,s),i=[];break;case"select":a=$({},a,{value:void 0}),s=$({},s,{value:void 0}),i=[];break;case"textarea":a=da(e,a),s=da(e,s),i=[];break;default:typeof a.onClick!="function"&&typeof s.onClick=="function"&&(e.onclick=os)}ha(n,s);var u;n=null;for(j in a)if(!s.hasOwnProperty(j)&&a.hasOwnProperty(j)&&a[j]!=null)if(j==="style"){var h=a[j];for(u in h)h.hasOwnProperty(u)&&(n||(n={}),n[u]="")}else j!=="dangerouslySetInnerHTML"&&j!=="children"&&j!=="suppressContentEditableWarning"&&j!=="suppressHydrationWarning"&&j!=="autoFocus"&&(m.hasOwnProperty(j)?i||(i=[]):(i=i||[]).push(j,null));for(j in s){var p=s[j];if(h=a!=null?a[j]:void 0,s.hasOwnProperty(j)&&p!==h&&(p!=null||h!=null))if(j==="style")if(h){for(u in h)!h.hasOwnProperty(u)||p&&p.hasOwnProperty(u)||(n||(n={}),n[u]="");for(u in p)p.hasOwnProperty(u)&&h[u]!==p[u]&&(n||(n={}),n[u]=p[u])}else n||(i||(i=[]),i.push(j,n)),n=p;else j==="dangerouslySetInnerHTML"?(p=p?p.__html:void 0,h=h?h.__html:void 0,p!=null&&h!==p&&(i=i||[]).push(j,p)):j==="children"?typeof p!="string"&&typeof p!="number"||(i=i||[]).push(j,""+p):j!=="suppressContentEditableWarning"&&j!=="suppressHydrationWarning"&&(m.hasOwnProperty(j)?(p!=null&&j==="onScroll"&&ve("scroll",e),i||h===p||(i=[])):(i=i||[]).push(j,p))}n&&(i=i||[]).push("style",n);var j=i;(t.updateQueue=j)&&(t.flags|=4)}},Oc=function(e,t,n,s){n!==s&&(t.flags|=4)};function Er(e,t){if(!ke)switch(e.tailMode){case"hidden":t=e.tail;for(var n=null;t!==null;)t.alternate!==null&&(n=t),t=t.sibling;n===null?e.tail=null:n.sibling=null;break;case"collapsed":n=e.tail;for(var s=null;n!==null;)n.alternate!==null&&(s=n),n=n.sibling;s===null?t||e.tail===null?e.tail=null:e.tail.sibling=null:s.sibling=null}}function Ve(e){var t=e.alternate!==null&&e.alternate.child===e.child,n=0,s=0;if(t)for(var a=e.child;a!==null;)n|=a.lanes|a.childLanes,s|=a.subtreeFlags&14680064,s|=a.flags&14680064,a.return=e,a=a.sibling;else for(a=e.child;a!==null;)n|=a.lanes|a.childLanes,s|=a.subtreeFlags,s|=a.flags,a.return=e,a=a.sibling;return e.subtreeFlags|=s,e.childLanes=n,t}function Tm(e,t,n){var s=t.pendingProps;switch(ti(t),t.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Ve(t),null;case 1:return Xe(t.type)&&cs(),Ve(t),null;case 3:return s=t.stateNode,Vn(),ye(Qe),ye(Ue),pi(),s.pendingContext&&(s.context=s.pendingContext,s.pendingContext=null),(e===null||e.child===null)&&(ps(t)?t.flags|=4:e===null||e.memoizedState.isDehydrated&&(t.flags&256)===0||(t.flags|=1024,xt!==null&&(Vi(xt),xt=null))),Ri(e,t),Ve(t),null;case 5:mi(t);var a=pn(Sr.current);if(n=t.type,e!==null&&t.stateNode!=null)Bc(e,t,n,s,a),e.ref!==t.ref&&(t.flags|=512,t.flags|=2097152);else{if(!s){if(t.stateNode===null)throw Error(l(166));return Ve(t),null}if(e=pn(_t.current),ps(t)){s=t.stateNode,n=t.type;var i=t.memoizedProps;switch(s[Ct]=t,s[xr]=i,e=(t.mode&1)!==0,n){case"dialog":ve("cancel",s),ve("close",s);break;case"iframe":case"object":case"embed":ve("load",s);break;case"video":case"audio":for(a=0;a<gr.length;a++)ve(gr[a],s);break;case"source":ve("error",s);break;case"img":case"image":case"link":ve("error",s),ve("load",s);break;case"details":ve("toggle",s);break;case"input":ko(s,i),ve("invalid",s);break;case"select":s._wrapperState={wasMultiple:!!i.multiple},ve("invalid",s);break;case"textarea":bo(s,i),ve("invalid",s)}ha(n,i),a=null;for(var u in i)if(i.hasOwnProperty(u)){var h=i[u];u==="children"?typeof h=="string"?s.textContent!==h&&(i.suppressHydrationWarning!==!0&&is(s.textContent,h,e),a=["children",h]):typeof h=="number"&&s.textContent!==""+h&&(i.suppressHydrationWarning!==!0&&is(s.textContent,h,e),a=["children",""+h]):m.hasOwnProperty(u)&&h!=null&&u==="onScroll"&&ve("scroll",s)}switch(n){case"input":zr(s),jo(s,i,!0);break;case"textarea":zr(s),No(s);break;case"select":case"option":break;default:typeof i.onClick=="function"&&(s.onclick=os)}s=a,t.updateQueue=s,s!==null&&(t.flags|=4)}else{u=a.nodeType===9?a:a.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=Co(n)),e==="http://www.w3.org/1999/xhtml"?n==="script"?(e=u.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof s.is=="string"?e=u.createElement(n,{is:s.is}):(e=u.createElement(n),n==="select"&&(u=e,s.multiple?u.multiple=!0:s.size&&(u.size=s.size))):e=u.createElementNS(e,n),e[Ct]=t,e[xr]=s,Fc(e,t,!1,!1),t.stateNode=e;e:{switch(u=pa(n,s),n){case"dialog":ve("cancel",e),ve("close",e),a=s;break;case"iframe":case"object":case"embed":ve("load",e),a=s;break;case"video":case"audio":for(a=0;a<gr.length;a++)ve(gr[a],e);a=s;break;case"source":ve("error",e),a=s;break;case"img":case"image":case"link":ve("error",e),ve("load",e),a=s;break;case"details":ve("toggle",e),a=s;break;case"input":ko(e,s),a=la(e,s),ve("invalid",e);break;case"option":a=s;break;case"select":e._wrapperState={wasMultiple:!!s.multiple},a=$({},s,{value:void 0}),ve("invalid",e);break;case"textarea":bo(e,s),a=da(e,s),ve("invalid",e);break;default:a=s}ha(n,a),h=a;for(i in h)if(h.hasOwnProperty(i)){var p=h[i];i==="style"?Eo(e,p):i==="dangerouslySetInnerHTML"?(p=p?p.__html:void 0,p!=null&&_o(e,p)):i==="children"?typeof p=="string"?(n!=="textarea"||p!=="")&&Yn(e,p):typeof p=="number"&&Yn(e,""+p):i!=="suppressContentEditableWarning"&&i!=="suppressHydrationWarning"&&i!=="autoFocus"&&(m.hasOwnProperty(i)?p!=null&&i==="onScroll"&&ve("scroll",e):p!=null&&q(e,i,p,u))}switch(n){case"input":zr(e),jo(e,s,!1);break;case"textarea":zr(e),No(e);break;case"option":s.value!=null&&e.setAttribute("value",""+me(s.value));break;case"select":e.multiple=!!s.multiple,i=s.value,i!=null?Nn(e,!!s.multiple,i,!1):s.defaultValue!=null&&Nn(e,!!s.multiple,s.defaultValue,!0);break;default:typeof a.onClick=="function"&&(e.onclick=os)}switch(n){case"button":case"input":case"select":case"textarea":s=!!s.autoFocus;break e;case"img":s=!0;break e;default:s=!1}}s&&(t.flags|=4)}t.ref!==null&&(t.flags|=512,t.flags|=2097152)}return Ve(t),null;case 6:if(e&&t.stateNode!=null)Oc(e,t,e.memoizedProps,s);else{if(typeof s!="string"&&t.stateNode===null)throw Error(l(166));if(n=pn(Sr.current),pn(_t.current),ps(t)){if(s=t.stateNode,n=t.memoizedProps,s[Ct]=t,(i=s.nodeValue!==n)&&(e=lt,e!==null))switch(e.tag){case 3:is(s.nodeValue,n,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&is(s.nodeValue,n,(e.mode&1)!==0)}i&&(t.flags|=4)}else s=(n.nodeType===9?n:n.ownerDocument).createTextNode(s),s[Ct]=t,t.stateNode=s}return Ve(t),null;case 13:if(ye(je),s=t.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(ke&&ct!==null&&(t.mode&1)!==0&&(t.flags&128)===0)$l(),On(),t.flags|=98560,i=!1;else if(i=ps(t),s!==null&&s.dehydrated!==null){if(e===null){if(!i)throw Error(l(318));if(i=t.memoizedState,i=i!==null?i.dehydrated:null,!i)throw Error(l(317));i[Ct]=t}else On(),(t.flags&128)===0&&(t.memoizedState=null),t.flags|=4;Ve(t),i=!1}else xt!==null&&(Vi(xt),xt=null),i=!0;if(!i)return t.flags&65536?t:null}return(t.flags&128)!==0?(t.lanes=n,t):(s=s!==null,s!==(e!==null&&e.memoizedState!==null)&&s&&(t.child.flags|=8192,(t.mode&1)!==0&&(e===null||(je.current&1)!==0?Ae===0&&(Ae=3):Ki())),t.updateQueue!==null&&(t.flags|=4),Ve(t),null);case 4:return Vn(),Ri(e,t),e===null&&vr(t.stateNode.containerInfo),Ve(t),null;case 10:return oi(t.type._context),Ve(t),null;case 17:return Xe(t.type)&&cs(),Ve(t),null;case 19:if(ye(je),i=t.memoizedState,i===null)return Ve(t),null;if(s=(t.flags&128)!==0,u=i.rendering,u===null)if(s)Er(i,!1);else{if(Ae!==0||e!==null&&(e.flags&128)!==0)for(e=t.child;e!==null;){if(u=ks(e),u!==null){for(t.flags|=128,Er(i,!1),s=u.updateQueue,s!==null&&(t.updateQueue=s,t.flags|=4),t.subtreeFlags=0,s=n,n=t.child;n!==null;)i=n,e=s,i.flags&=14680066,u=i.alternate,u===null?(i.childLanes=0,i.lanes=e,i.child=null,i.subtreeFlags=0,i.memoizedProps=null,i.memoizedState=null,i.updateQueue=null,i.dependencies=null,i.stateNode=null):(i.childLanes=u.childLanes,i.lanes=u.lanes,i.child=u.child,i.subtreeFlags=0,i.deletions=null,i.memoizedProps=u.memoizedProps,i.memoizedState=u.memoizedState,i.updateQueue=u.updateQueue,i.type=u.type,e=u.dependencies,i.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),n=n.sibling;return ge(je,je.current&1|2),t.child}e=e.sibling}i.tail!==null&&Te()>qn&&(t.flags|=128,s=!0,Er(i,!1),t.lanes=4194304)}else{if(!s)if(e=ks(u),e!==null){if(t.flags|=128,s=!0,n=e.updateQueue,n!==null&&(t.updateQueue=n,t.flags|=4),Er(i,!0),i.tail===null&&i.tailMode==="hidden"&&!u.alternate&&!ke)return Ve(t),null}else 2*Te()-i.renderingStartTime>qn&&n!==1073741824&&(t.flags|=128,s=!0,Er(i,!1),t.lanes=4194304);i.isBackwards?(u.sibling=t.child,t.child=u):(n=i.last,n!==null?n.sibling=u:t.child=u,i.last=u)}return i.tail!==null?(t=i.tail,i.rendering=t,i.tail=t.sibling,i.renderingStartTime=Te(),t.sibling=null,n=je.current,ge(je,s?n&1|2:n&1),t):(Ve(t),null);case 22:case 23:return Gi(),s=t.memoizedState!==null,e!==null&&e.memoizedState!==null!==s&&(t.flags|=8192),s&&(t.mode&1)!==0?(ut&1073741824)!==0&&(Ve(t),t.subtreeFlags&6&&(t.flags|=8192)):Ve(t),null;case 24:return null;case 25:return null}throw Error(l(156,t.tag))}function Em(e,t){switch(ti(t),t.tag){case 1:return Xe(t.type)&&cs(),e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 3:return Vn(),ye(Qe),ye(Ue),pi(),e=t.flags,(e&65536)!==0&&(e&128)===0?(t.flags=e&-65537|128,t):null;case 5:return mi(t),null;case 13:if(ye(je),e=t.memoizedState,e!==null&&e.dehydrated!==null){if(t.alternate===null)throw Error(l(340));On()}return e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 19:return ye(je),null;case 4:return Vn(),null;case 10:return oi(t.type._context),null;case 22:case 23:return Gi(),null;case 24:return null;default:return null}}var Es=!1,He=!1,Mm=typeof WeakSet=="function"?WeakSet:Set,U=null;function Gn(e,t){var n=e.ref;if(n!==null)if(typeof n=="function")try{n(null)}catch(s){Ce(e,t,s)}else n.current=null}function Ai(e,t,n){try{n()}catch(s){Ce(e,t,s)}}var Wc=!1;function Pm(e,t){if(Ga=Qr,e=xl(),Fa(e)){if("selectionStart"in e)var n={start:e.selectionStart,end:e.selectionEnd};else e:{n=(n=e.ownerDocument)&&n.defaultView||window;var s=n.getSelection&&n.getSelection();if(s&&s.rangeCount!==0){n=s.anchorNode;var a=s.anchorOffset,i=s.focusNode;s=s.focusOffset;try{n.nodeType,i.nodeType}catch{n=null;break e}var u=0,h=-1,p=-1,j=0,E=0,L=e,_=null;t:for(;;){for(var W;L!==n||a!==0&&L.nodeType!==3||(h=u+a),L!==i||s!==0&&L.nodeType!==3||(p=u+s),L.nodeType===3&&(u+=L.nodeValue.length),(W=L.firstChild)!==null;)_=L,L=W;for(;;){if(L===e)break t;if(_===n&&++j===a&&(h=u),_===i&&++E===s&&(p=u),(W=L.nextSibling)!==null)break;L=_,_=L.parentNode}L=W}n=h===-1||p===-1?null:{start:h,end:p}}else n=null}n=n||{start:0,end:0}}else n=null;for(Ka={focusedElem:e,selectionRange:n},Qr=!1,U=t;U!==null;)if(t=U,e=t.child,(t.subtreeFlags&1028)!==0&&e!==null)e.return=t,U=e;else for(;U!==null;){t=U;try{var V=t.alternate;if((t.flags&1024)!==0)switch(t.tag){case 0:case 11:case 15:break;case 1:if(V!==null){var H=V.memoizedProps,Ee=V.memoizedState,x=t.stateNode,g=x.getSnapshotBeforeUpdate(t.elementType===t.type?H:kt(t.type,H),Ee);x.__reactInternalSnapshotBeforeUpdate=g}break;case 3:var k=t.stateNode.containerInfo;k.nodeType===1?k.textContent="":k.nodeType===9&&k.documentElement&&k.removeChild(k.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(l(163))}}catch(A){Ce(t,t.return,A)}if(e=t.sibling,e!==null){e.return=t.return,U=e;break}U=t.return}return V=Wc,Wc=!1,V}function Mr(e,t,n){var s=t.updateQueue;if(s=s!==null?s.lastEffect:null,s!==null){var a=s=s.next;do{if((a.tag&e)===e){var i=a.destroy;a.destroy=void 0,i!==void 0&&Ai(t,n,i)}a=a.next}while(a!==s)}}function Ms(e,t){if(t=t.updateQueue,t=t!==null?t.lastEffect:null,t!==null){var n=t=t.next;do{if((n.tag&e)===e){var s=n.create;n.destroy=s()}n=n.next}while(n!==t)}}function Di(e){var t=e.ref;if(t!==null){var n=e.stateNode;switch(e.tag){case 5:e=n;break;default:e=n}typeof t=="function"?t(e):t.current=e}}function Uc(e){var t=e.alternate;t!==null&&(e.alternate=null,Uc(t)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(t=e.stateNode,t!==null&&(delete t[Ct],delete t[xr],delete t[Ya],delete t[hm],delete t[pm])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function $c(e){return e.tag===5||e.tag===3||e.tag===4}function Vc(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||$c(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Ii(e,t,n){var s=e.tag;if(s===5||s===6)e=e.stateNode,t?n.nodeType===8?n.parentNode.insertBefore(e,t):n.insertBefore(e,t):(n.nodeType===8?(t=n.parentNode,t.insertBefore(e,n)):(t=n,t.appendChild(e)),n=n._reactRootContainer,n!=null||t.onclick!==null||(t.onclick=os));else if(s!==4&&(e=e.child,e!==null))for(Ii(e,t,n),e=e.sibling;e!==null;)Ii(e,t,n),e=e.sibling}function zi(e,t,n){var s=e.tag;if(s===5||s===6)e=e.stateNode,t?n.insertBefore(e,t):n.appendChild(e);else if(s!==4&&(e=e.child,e!==null))for(zi(e,t,n),e=e.sibling;e!==null;)zi(e,t,n),e=e.sibling}var Oe=null,wt=!1;function Jt(e,t,n){for(n=n.child;n!==null;)Hc(e,t,n),n=n.sibling}function Hc(e,t,n){if(Nt&&typeof Nt.onCommitFiberUnmount=="function")try{Nt.onCommitFiberUnmount($r,n)}catch{}switch(n.tag){case 5:He||Gn(n,t);case 6:var s=Oe,a=wt;Oe=null,Jt(e,t,n),Oe=s,wt=a,Oe!==null&&(wt?(e=Oe,n=n.stateNode,e.nodeType===8?e.parentNode.removeChild(n):e.removeChild(n)):Oe.removeChild(n.stateNode));break;case 18:Oe!==null&&(wt?(e=Oe,n=n.stateNode,e.nodeType===8?Xa(e.parentNode,n):e.nodeType===1&&Xa(e,n),lr(e)):Xa(Oe,n.stateNode));break;case 4:s=Oe,a=wt,Oe=n.stateNode.containerInfo,wt=!0,Jt(e,t,n),Oe=s,wt=a;break;case 0:case 11:case 14:case 15:if(!He&&(s=n.updateQueue,s!==null&&(s=s.lastEffect,s!==null))){a=s=s.next;do{var i=a,u=i.destroy;i=i.tag,u!==void 0&&((i&2)!==0||(i&4)!==0)&&Ai(n,t,u),a=a.next}while(a!==s)}Jt(e,t,n);break;case 1:if(!He&&(Gn(n,t),s=n.stateNode,typeof s.componentWillUnmount=="function"))try{s.props=n.memoizedProps,s.state=n.memoizedState,s.componentWillUnmount()}catch(h){Ce(n,t,h)}Jt(e,t,n);break;case 21:Jt(e,t,n);break;case 22:n.mode&1?(He=(s=He)||n.memoizedState!==null,Jt(e,t,n),He=s):Jt(e,t,n);break;default:Jt(e,t,n)}}function Gc(e){var t=e.updateQueue;if(t!==null){e.updateQueue=null;var n=e.stateNode;n===null&&(n=e.stateNode=new Mm),t.forEach(function(s){var a=Om.bind(null,e,s);n.has(s)||(n.add(s),s.then(a,a))})}}function jt(e,t){var n=t.deletions;if(n!==null)for(var s=0;s<n.length;s++){var a=n[s];try{var i=e,u=t,h=u;e:for(;h!==null;){switch(h.tag){case 5:Oe=h.stateNode,wt=!1;break e;case 3:Oe=h.stateNode.containerInfo,wt=!0;break e;case 4:Oe=h.stateNode.containerInfo,wt=!0;break e}h=h.return}if(Oe===null)throw Error(l(160));Hc(i,u,a),Oe=null,wt=!1;var p=a.alternate;p!==null&&(p.return=null),a.return=null}catch(j){Ce(a,t,j)}}if(t.subtreeFlags&12854)for(t=t.child;t!==null;)Kc(t,e),t=t.sibling}function Kc(e,t){var n=e.alternate,s=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(jt(t,e),Et(e),s&4){try{Mr(3,e,e.return),Ms(3,e)}catch(H){Ce(e,e.return,H)}try{Mr(5,e,e.return)}catch(H){Ce(e,e.return,H)}}break;case 1:jt(t,e),Et(e),s&512&&n!==null&&Gn(n,n.return);break;case 5:if(jt(t,e),Et(e),s&512&&n!==null&&Gn(n,n.return),e.flags&32){var a=e.stateNode;try{Yn(a,"")}catch(H){Ce(e,e.return,H)}}if(s&4&&(a=e.stateNode,a!=null)){var i=e.memoizedProps,u=n!==null?n.memoizedProps:i,h=e.type,p=e.updateQueue;if(e.updateQueue=null,p!==null)try{h==="input"&&i.type==="radio"&&i.name!=null&&wo(a,i),pa(h,u);var j=pa(h,i);for(u=0;u<p.length;u+=2){var E=p[u],L=p[u+1];E==="style"?Eo(a,L):E==="dangerouslySetInnerHTML"?_o(a,L):E==="children"?Yn(a,L):q(a,E,L,j)}switch(h){case"input":ca(a,i);break;case"textarea":So(a,i);break;case"select":var _=a._wrapperState.wasMultiple;a._wrapperState.wasMultiple=!!i.multiple;var W=i.value;W!=null?Nn(a,!!i.multiple,W,!1):_!==!!i.multiple&&(i.defaultValue!=null?Nn(a,!!i.multiple,i.defaultValue,!0):Nn(a,!!i.multiple,i.multiple?[]:"",!1))}a[xr]=i}catch(H){Ce(e,e.return,H)}}break;case 6:if(jt(t,e),Et(e),s&4){if(e.stateNode===null)throw Error(l(162));a=e.stateNode,i=e.memoizedProps;try{a.nodeValue=i}catch(H){Ce(e,e.return,H)}}break;case 3:if(jt(t,e),Et(e),s&4&&n!==null&&n.memoizedState.isDehydrated)try{lr(t.containerInfo)}catch(H){Ce(e,e.return,H)}break;case 4:jt(t,e),Et(e);break;case 13:jt(t,e),Et(e),a=e.child,a.flags&8192&&(i=a.memoizedState!==null,a.stateNode.isHidden=i,!i||a.alternate!==null&&a.alternate.memoizedState!==null||(Oi=Te())),s&4&&Gc(e);break;case 22:if(E=n!==null&&n.memoizedState!==null,e.mode&1?(He=(j=He)||E,jt(t,e),He=j):jt(t,e),Et(e),s&8192){if(j=e.memoizedState!==null,(e.stateNode.isHidden=j)&&!E&&(e.mode&1)!==0)for(U=e,E=e.child;E!==null;){for(L=U=E;U!==null;){switch(_=U,W=_.child,_.tag){case 0:case 11:case 14:case 15:Mr(4,_,_.return);break;case 1:Gn(_,_.return);var V=_.stateNode;if(typeof V.componentWillUnmount=="function"){s=_,n=_.return;try{t=s,V.props=t.memoizedProps,V.state=t.memoizedState,V.componentWillUnmount()}catch(H){Ce(s,n,H)}}break;case 5:Gn(_,_.return);break;case 22:if(_.memoizedState!==null){Xc(L);continue}}W!==null?(W.return=_,U=W):Xc(L)}E=E.sibling}e:for(E=null,L=e;;){if(L.tag===5){if(E===null){E=L;try{a=L.stateNode,j?(i=a.style,typeof i.setProperty=="function"?i.setProperty("display","none","important"):i.display="none"):(h=L.stateNode,p=L.memoizedProps.style,u=p!=null&&p.hasOwnProperty("display")?p.display:null,h.style.display=To("display",u))}catch(H){Ce(e,e.return,H)}}}else if(L.tag===6){if(E===null)try{L.stateNode.nodeValue=j?"":L.memoizedProps}catch(H){Ce(e,e.return,H)}}else if((L.tag!==22&&L.tag!==23||L.memoizedState===null||L===e)&&L.child!==null){L.child.return=L,L=L.child;continue}if(L===e)break e;for(;L.sibling===null;){if(L.return===null||L.return===e)break e;E===L&&(E=null),L=L.return}E===L&&(E=null),L.sibling.return=L.return,L=L.sibling}}break;case 19:jt(t,e),Et(e),s&4&&Gc(e);break;case 21:break;default:jt(t,e),Et(e)}}function Et(e){var t=e.flags;if(t&2){try{e:{for(var n=e.return;n!==null;){if($c(n)){var s=n;break e}n=n.return}throw Error(l(160))}switch(s.tag){case 5:var a=s.stateNode;s.flags&32&&(Yn(a,""),s.flags&=-33);var i=Vc(e);zi(e,i,a);break;case 3:case 4:var u=s.stateNode.containerInfo,h=Vc(e);Ii(e,h,u);break;default:throw Error(l(161))}}catch(p){Ce(e,e.return,p)}e.flags&=-3}t&4096&&(e.flags&=-4097)}function Lm(e,t,n){U=e,qc(e)}function qc(e,t,n){for(var s=(e.mode&1)!==0;U!==null;){var a=U,i=a.child;if(a.tag===22&&s){var u=a.memoizedState!==null||Es;if(!u){var h=a.alternate,p=h!==null&&h.memoizedState!==null||He;h=Es;var j=He;if(Es=u,(He=p)&&!j)for(U=a;U!==null;)u=U,p=u.child,u.tag===22&&u.memoizedState!==null?Yc(a):p!==null?(p.return=u,U=p):Yc(a);for(;i!==null;)U=i,qc(i),i=i.sibling;U=a,Es=h,He=j}Qc(e)}else(a.subtreeFlags&8772)!==0&&i!==null?(i.return=a,U=i):Qc(e)}}function Qc(e){for(;U!==null;){var t=U;if((t.flags&8772)!==0){var n=t.alternate;try{if((t.flags&8772)!==0)switch(t.tag){case 0:case 11:case 15:He||Ms(5,t);break;case 1:var s=t.stateNode;if(t.flags&4&&!He)if(n===null)s.componentDidMount();else{var a=t.elementType===t.type?n.memoizedProps:kt(t.type,n.memoizedProps);s.componentDidUpdate(a,n.memoizedState,s.__reactInternalSnapshotBeforeUpdate)}var i=t.updateQueue;i!==null&&Xl(t,i,s);break;case 3:var u=t.updateQueue;if(u!==null){if(n=null,t.child!==null)switch(t.child.tag){case 5:n=t.child.stateNode;break;case 1:n=t.child.stateNode}Xl(t,u,n)}break;case 5:var h=t.stateNode;if(n===null&&t.flags&4){n=h;var p=t.memoizedProps;switch(t.type){case"button":case"input":case"select":case"textarea":p.autoFocus&&n.focus();break;case"img":p.src&&(n.src=p.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(t.memoizedState===null){var j=t.alternate;if(j!==null){var E=j.memoizedState;if(E!==null){var L=E.dehydrated;L!==null&&lr(L)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(l(163))}He||t.flags&512&&Di(t)}catch(_){Ce(t,t.return,_)}}if(t===e){U=null;break}if(n=t.sibling,n!==null){n.return=t.return,U=n;break}U=t.return}}function Xc(e){for(;U!==null;){var t=U;if(t===e){U=null;break}var n=t.sibling;if(n!==null){n.return=t.return,U=n;break}U=t.return}}function Yc(e){for(;U!==null;){var t=U;try{switch(t.tag){case 0:case 11:case 15:var n=t.return;try{Ms(4,t)}catch(p){Ce(t,n,p)}break;case 1:var s=t.stateNode;if(typeof s.componentDidMount=="function"){var a=t.return;try{s.componentDidMount()}catch(p){Ce(t,a,p)}}var i=t.return;try{Di(t)}catch(p){Ce(t,i,p)}break;case 5:var u=t.return;try{Di(t)}catch(p){Ce(t,u,p)}}}catch(p){Ce(t,t.return,p)}if(t===e){U=null;break}var h=t.sibling;if(h!==null){h.return=t.return,U=h;break}U=t.return}}var Rm=Math.ceil,Ps=ne.ReactCurrentDispatcher,Fi=ne.ReactCurrentOwner,ft=ne.ReactCurrentBatchConfig,le=0,ze=null,Me=null,We=0,ut=0,Kn=Kt(0),Ae=0,Pr=null,gn=0,Ls=0,Bi=0,Lr=null,Je=null,Oi=0,qn=1/0,Ft=null,Rs=!1,Wi=null,Zt=null,As=!1,en=null,Ds=0,Rr=0,Ui=null,Is=-1,zs=0;function Ke(){return(le&6)!==0?Te():Is!==-1?Is:Is=Te()}function tn(e){return(e.mode&1)===0?1:(le&2)!==0&&We!==0?We&-We:gm.transition!==null?(zs===0&&(zs=Vo()),zs):(e=he,e!==0||(e=window.event,e=e===void 0?16:Zo(e.type)),e)}function bt(e,t,n,s){if(50<Rr)throw Rr=0,Ui=null,Error(l(185));rr(e,n,s),((le&2)===0||e!==ze)&&(e===ze&&((le&2)===0&&(Ls|=n),Ae===4&&nn(e,We)),Ze(e,s),n===1&&le===0&&(t.mode&1)===0&&(qn=Te()+500,ds&&Qt()))}function Ze(e,t){var n=e.callbackNode;gd(e,t);var s=Gr(e,e===ze?We:0);if(s===0)n!==null&&Wo(n),e.callbackNode=null,e.callbackPriority=0;else if(t=s&-s,e.callbackPriority!==t){if(n!=null&&Wo(n),t===1)e.tag===0?fm(Zc.bind(null,e)):Fl(Zc.bind(null,e)),dm(function(){(le&6)===0&&Qt()}),n=null;else{switch(Ho(s)){case 1:n=wa;break;case 4:n=Uo;break;case 16:n=Ur;break;case 536870912:n=$o;break;default:n=Ur}n=ou(n,Jc.bind(null,e))}e.callbackPriority=t,e.callbackNode=n}}function Jc(e,t){if(Is=-1,zs=0,(le&6)!==0)throw Error(l(327));var n=e.callbackNode;if(Qn()&&e.callbackNode!==n)return null;var s=Gr(e,e===ze?We:0);if(s===0)return null;if((s&30)!==0||(s&e.expiredLanes)!==0||t)t=Fs(e,s);else{t=s;var a=le;le|=2;var i=tu();(ze!==e||We!==t)&&(Ft=null,qn=Te()+500,yn(e,t));do try{Im();break}catch(h){eu(e,h)}while(!0);ii(),Ps.current=i,le=a,Me!==null?t=0:(ze=null,We=0,t=Ae)}if(t!==0){if(t===2&&(a=ja(e),a!==0&&(s=a,t=$i(e,a))),t===1)throw n=Pr,yn(e,0),nn(e,s),Ze(e,Te()),n;if(t===6)nn(e,s);else{if(a=e.current.alternate,(s&30)===0&&!Am(a)&&(t=Fs(e,s),t===2&&(i=ja(e),i!==0&&(s=i,t=$i(e,i))),t===1))throw n=Pr,yn(e,0),nn(e,s),Ze(e,Te()),n;switch(e.finishedWork=a,e.finishedLanes=s,t){case 0:case 1:throw Error(l(345));case 2:xn(e,Je,Ft);break;case 3:if(nn(e,s),(s&130023424)===s&&(t=Oi+500-Te(),10<t)){if(Gr(e,0)!==0)break;if(a=e.suspendedLanes,(a&s)!==s){Ke(),e.pingedLanes|=e.suspendedLanes&a;break}e.timeoutHandle=Qa(xn.bind(null,e,Je,Ft),t);break}xn(e,Je,Ft);break;case 4:if(nn(e,s),(s&4194240)===s)break;for(t=e.eventTimes,a=-1;0<s;){var u=31-vt(s);i=1<<u,u=t[u],u>a&&(a=u),s&=~i}if(s=a,s=Te()-s,s=(120>s?120:480>s?480:1080>s?1080:1920>s?1920:3e3>s?3e3:4320>s?4320:1960*Rm(s/1960))-s,10<s){e.timeoutHandle=Qa(xn.bind(null,e,Je,Ft),s);break}xn(e,Je,Ft);break;case 5:xn(e,Je,Ft);break;default:throw Error(l(329))}}}return Ze(e,Te()),e.callbackNode===n?Jc.bind(null,e):null}function $i(e,t){var n=Lr;return e.current.memoizedState.isDehydrated&&(yn(e,t).flags|=256),e=Fs(e,t),e!==2&&(t=Je,Je=n,t!==null&&Vi(t)),e}function Vi(e){Je===null?Je=e:Je.push.apply(Je,e)}function Am(e){for(var t=e;;){if(t.flags&16384){var n=t.updateQueue;if(n!==null&&(n=n.stores,n!==null))for(var s=0;s<n.length;s++){var a=n[s],i=a.getSnapshot;a=a.value;try{if(!yt(i(),a))return!1}catch{return!1}}}if(n=t.child,t.subtreeFlags&16384&&n!==null)n.return=t,t=n;else{if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return!0;t=t.return}t.sibling.return=t.return,t=t.sibling}}return!0}function nn(e,t){for(t&=~Bi,t&=~Ls,e.suspendedLanes|=t,e.pingedLanes&=~t,e=e.expirationTimes;0<t;){var n=31-vt(t),s=1<<n;e[n]=-1,t&=~s}}function Zc(e){if((le&6)!==0)throw Error(l(327));Qn();var t=Gr(e,0);if((t&1)===0)return Ze(e,Te()),null;var n=Fs(e,t);if(e.tag!==0&&n===2){var s=ja(e);s!==0&&(t=s,n=$i(e,s))}if(n===1)throw n=Pr,yn(e,0),nn(e,t),Ze(e,Te()),n;if(n===6)throw Error(l(345));return e.finishedWork=e.current.alternate,e.finishedLanes=t,xn(e,Je,Ft),Ze(e,Te()),null}function Hi(e,t){var n=le;le|=1;try{return e(t)}finally{le=n,le===0&&(qn=Te()+500,ds&&Qt())}}function vn(e){en!==null&&en.tag===0&&(le&6)===0&&Qn();var t=le;le|=1;var n=ft.transition,s=he;try{if(ft.transition=null,he=1,e)return e()}finally{he=s,ft.transition=n,le=t,(le&6)===0&&Qt()}}function Gi(){ut=Kn.current,ye(Kn)}function yn(e,t){e.finishedWork=null,e.finishedLanes=0;var n=e.timeoutHandle;if(n!==-1&&(e.timeoutHandle=-1,um(n)),Me!==null)for(n=Me.return;n!==null;){var s=n;switch(ti(s),s.tag){case 1:s=s.type.childContextTypes,s!=null&&cs();break;case 3:Vn(),ye(Qe),ye(Ue),pi();break;case 5:mi(s);break;case 4:Vn();break;case 13:ye(je);break;case 19:ye(je);break;case 10:oi(s.type._context);break;case 22:case 23:Gi()}n=n.return}if(ze=e,Me=e=rn(e.current,null),We=ut=t,Ae=0,Pr=null,Bi=Ls=gn=0,Je=Lr=null,hn!==null){for(t=0;t<hn.length;t++)if(n=hn[t],s=n.interleaved,s!==null){n.interleaved=null;var a=s.next,i=n.pending;if(i!==null){var u=i.next;i.next=a,s.next=u}n.pending=s}hn=null}return e}function eu(e,t){do{var n=Me;try{if(ii(),ws.current=Ns,js){for(var s=be.memoizedState;s!==null;){var a=s.queue;a!==null&&(a.pending=null),s=s.next}js=!1}if(fn=0,Ie=Re=be=null,Nr=!1,Cr=0,Fi.current=null,n===null||n.return===null){Ae=1,Pr=t,Me=null;break}e:{var i=e,u=n.return,h=n,p=t;if(t=We,h.flags|=32768,p!==null&&typeof p=="object"&&typeof p.then=="function"){var j=p,E=h,L=E.tag;if((E.mode&1)===0&&(L===0||L===11||L===15)){var _=E.alternate;_?(E.updateQueue=_.updateQueue,E.memoizedState=_.memoizedState,E.lanes=_.lanes):(E.updateQueue=null,E.memoizedState=null)}var W=Nc(u);if(W!==null){W.flags&=-257,Cc(W,u,h,i,t),W.mode&1&&Sc(i,j,t),t=W,p=j;var V=t.updateQueue;if(V===null){var H=new Set;H.add(p),t.updateQueue=H}else V.add(p);break e}else{if((t&1)===0){Sc(i,j,t),Ki();break e}p=Error(l(426))}}else if(ke&&h.mode&1){var Ee=Nc(u);if(Ee!==null){(Ee.flags&65536)===0&&(Ee.flags|=256),Cc(Ee,u,h,i,t),si(Hn(p,h));break e}}i=p=Hn(p,h),Ae!==4&&(Ae=2),Lr===null?Lr=[i]:Lr.push(i),i=u;do{switch(i.tag){case 3:i.flags|=65536,t&=-t,i.lanes|=t;var x=jc(i,p,t);Ql(i,x);break e;case 1:h=p;var g=i.type,k=i.stateNode;if((i.flags&128)===0&&(typeof g.getDerivedStateFromError=="function"||k!==null&&typeof k.componentDidCatch=="function"&&(Zt===null||!Zt.has(k)))){i.flags|=65536,t&=-t,i.lanes|=t;var A=bc(i,h,t);Ql(i,A);break e}}i=i.return}while(i!==null)}ru(n)}catch(G){t=G,Me===n&&n!==null&&(Me=n=n.return);continue}break}while(!0)}function tu(){var e=Ps.current;return Ps.current=Ns,e===null?Ns:e}function Ki(){(Ae===0||Ae===3||Ae===2)&&(Ae=4),ze===null||(gn&268435455)===0&&(Ls&268435455)===0||nn(ze,We)}function Fs(e,t){var n=le;le|=2;var s=tu();(ze!==e||We!==t)&&(Ft=null,yn(e,t));do try{Dm();break}catch(a){eu(e,a)}while(!0);if(ii(),le=n,Ps.current=s,Me!==null)throw Error(l(261));return ze=null,We=0,Ae}function Dm(){for(;Me!==null;)nu(Me)}function Im(){for(;Me!==null&&!od();)nu(Me)}function nu(e){var t=iu(e.alternate,e,ut);e.memoizedProps=e.pendingProps,t===null?ru(e):Me=t,Fi.current=null}function ru(e){var t=e;do{var n=t.alternate;if(e=t.return,(t.flags&32768)===0){if(n=Tm(n,t,ut),n!==null){Me=n;return}}else{if(n=Em(n,t),n!==null){n.flags&=32767,Me=n;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{Ae=6,Me=null;return}}if(t=t.sibling,t!==null){Me=t;return}Me=t=e}while(t!==null);Ae===0&&(Ae=5)}function xn(e,t,n){var s=he,a=ft.transition;try{ft.transition=null,he=1,zm(e,t,n,s)}finally{ft.transition=a,he=s}return null}function zm(e,t,n,s){do Qn();while(en!==null);if((le&6)!==0)throw Error(l(327));n=e.finishedWork;var a=e.finishedLanes;if(n===null)return null;if(e.finishedWork=null,e.finishedLanes=0,n===e.current)throw Error(l(177));e.callbackNode=null,e.callbackPriority=0;var i=n.lanes|n.childLanes;if(vd(e,i),e===ze&&(Me=ze=null,We=0),(n.subtreeFlags&2064)===0&&(n.flags&2064)===0||As||(As=!0,ou(Ur,function(){return Qn(),null})),i=(n.flags&15990)!==0,(n.subtreeFlags&15990)!==0||i){i=ft.transition,ft.transition=null;var u=he;he=1;var h=le;le|=4,Fi.current=null,Pm(e,n),Kc(n,e),rm(Ka),Qr=!!Ga,Ka=Ga=null,e.current=n,Lm(n),ld(),le=h,he=u,ft.transition=i}else e.current=n;if(As&&(As=!1,en=e,Ds=a),i=e.pendingLanes,i===0&&(Zt=null),dd(n.stateNode),Ze(e,Te()),t!==null)for(s=e.onRecoverableError,n=0;n<t.length;n++)a=t[n],s(a.value,{componentStack:a.stack,digest:a.digest});if(Rs)throw Rs=!1,e=Wi,Wi=null,e;return(Ds&1)!==0&&e.tag!==0&&Qn(),i=e.pendingLanes,(i&1)!==0?e===Ui?Rr++:(Rr=0,Ui=e):Rr=0,Qt(),null}function Qn(){if(en!==null){var e=Ho(Ds),t=ft.transition,n=he;try{if(ft.transition=null,he=16>e?16:e,en===null)var s=!1;else{if(e=en,en=null,Ds=0,(le&6)!==0)throw Error(l(331));var a=le;for(le|=4,U=e.current;U!==null;){var i=U,u=i.child;if((U.flags&16)!==0){var h=i.deletions;if(h!==null){for(var p=0;p<h.length;p++){var j=h[p];for(U=j;U!==null;){var E=U;switch(E.tag){case 0:case 11:case 15:Mr(8,E,i)}var L=E.child;if(L!==null)L.return=E,U=L;else for(;U!==null;){E=U;var _=E.sibling,W=E.return;if(Uc(E),E===j){U=null;break}if(_!==null){_.return=W,U=_;break}U=W}}}var V=i.alternate;if(V!==null){var H=V.child;if(H!==null){V.child=null;do{var Ee=H.sibling;H.sibling=null,H=Ee}while(H!==null)}}U=i}}if((i.subtreeFlags&2064)!==0&&u!==null)u.return=i,U=u;else e:for(;U!==null;){if(i=U,(i.flags&2048)!==0)switch(i.tag){case 0:case 11:case 15:Mr(9,i,i.return)}var x=i.sibling;if(x!==null){x.return=i.return,U=x;break e}U=i.return}}var g=e.current;for(U=g;U!==null;){u=U;var k=u.child;if((u.subtreeFlags&2064)!==0&&k!==null)k.return=u,U=k;else e:for(u=g;U!==null;){if(h=U,(h.flags&2048)!==0)try{switch(h.tag){case 0:case 11:case 15:Ms(9,h)}}catch(G){Ce(h,h.return,G)}if(h===u){U=null;break e}var A=h.sibling;if(A!==null){A.return=h.return,U=A;break e}U=h.return}}if(le=a,Qt(),Nt&&typeof Nt.onPostCommitFiberRoot=="function")try{Nt.onPostCommitFiberRoot($r,e)}catch{}s=!0}return s}finally{he=n,ft.transition=t}}return!1}function su(e,t,n){t=Hn(n,t),t=jc(e,t,1),e=Yt(e,t,1),t=Ke(),e!==null&&(rr(e,1,t),Ze(e,t))}function Ce(e,t,n){if(e.tag===3)su(e,e,n);else for(;t!==null;){if(t.tag===3){su(t,e,n);break}else if(t.tag===1){var s=t.stateNode;if(typeof t.type.getDerivedStateFromError=="function"||typeof s.componentDidCatch=="function"&&(Zt===null||!Zt.has(s))){e=Hn(n,e),e=bc(t,e,1),t=Yt(t,e,1),e=Ke(),t!==null&&(rr(t,1,e),Ze(t,e));break}}t=t.return}}function Fm(e,t,n){var s=e.pingCache;s!==null&&s.delete(t),t=Ke(),e.pingedLanes|=e.suspendedLanes&n,ze===e&&(We&n)===n&&(Ae===4||Ae===3&&(We&130023424)===We&&500>Te()-Oi?yn(e,0):Bi|=n),Ze(e,t)}function au(e,t){t===0&&((e.mode&1)===0?t=1:(t=Hr,Hr<<=1,(Hr&130023424)===0&&(Hr=4194304)));var n=Ke();e=Dt(e,t),e!==null&&(rr(e,t,n),Ze(e,n))}function Bm(e){var t=e.memoizedState,n=0;t!==null&&(n=t.retryLane),au(e,n)}function Om(e,t){var n=0;switch(e.tag){case 13:var s=e.stateNode,a=e.memoizedState;a!==null&&(n=a.retryLane);break;case 19:s=e.stateNode;break;default:throw Error(l(314))}s!==null&&s.delete(t),au(e,n)}var iu;iu=function(e,t,n){if(e!==null)if(e.memoizedProps!==t.pendingProps||Qe.current)Ye=!0;else{if((e.lanes&n)===0&&(t.flags&128)===0)return Ye=!1,_m(e,t,n);Ye=(e.flags&131072)!==0}else Ye=!1,ke&&(t.flags&1048576)!==0&&Bl(t,hs,t.index);switch(t.lanes=0,t.tag){case 2:var s=t.type;Ts(e,t),e=t.pendingProps;var a=zn(t,Ue.current);$n(t,n),a=vi(null,t,s,e,a,n);var i=yi();return t.flags|=1,typeof a=="object"&&a!==null&&typeof a.render=="function"&&a.$$typeof===void 0?(t.tag=1,t.memoizedState=null,t.updateQueue=null,Xe(s)?(i=!0,us(t)):i=!1,t.memoizedState=a.state!==null&&a.state!==void 0?a.state:null,ui(t),a.updater=Cs,t.stateNode=a,a._reactInternals=t,Si(t,s,e,n),t=Ti(null,t,s,!0,i,n)):(t.tag=0,ke&&i&&ei(t),Ge(null,t,a,n),t=t.child),t;case 16:s=t.elementType;e:{switch(Ts(e,t),e=t.pendingProps,a=s._init,s=a(s._payload),t.type=s,a=t.tag=Um(s),e=kt(s,e),a){case 0:t=_i(null,t,s,e,n);break e;case 1:t=Lc(null,t,s,e,n);break e;case 11:t=_c(null,t,s,e,n);break e;case 14:t=Tc(null,t,s,kt(s.type,e),n);break e}throw Error(l(306,s,""))}return t;case 0:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:kt(s,a),_i(e,t,s,a,n);case 1:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:kt(s,a),Lc(e,t,s,a,n);case 3:e:{if(Rc(t),e===null)throw Error(l(387));s=t.pendingProps,i=t.memoizedState,a=i.element,ql(e,t),xs(t,s,null,n);var u=t.memoizedState;if(s=u.element,i.isDehydrated)if(i={element:s,isDehydrated:!1,cache:u.cache,pendingSuspenseBoundaries:u.pendingSuspenseBoundaries,transitions:u.transitions},t.updateQueue.baseState=i,t.memoizedState=i,t.flags&256){a=Hn(Error(l(423)),t),t=Ac(e,t,s,n,a);break e}else if(s!==a){a=Hn(Error(l(424)),t),t=Ac(e,t,s,n,a);break e}else for(ct=Gt(t.stateNode.containerInfo.firstChild),lt=t,ke=!0,xt=null,n=Gl(t,null,s,n),t.child=n;n;)n.flags=n.flags&-3|4096,n=n.sibling;else{if(On(),s===a){t=zt(e,t,n);break e}Ge(e,t,s,n)}t=t.child}return t;case 5:return Yl(t),e===null&&ri(t),s=t.type,a=t.pendingProps,i=e!==null?e.memoizedProps:null,u=a.children,qa(s,a)?u=null:i!==null&&qa(s,i)&&(t.flags|=32),Pc(e,t),Ge(e,t,u,n),t.child;case 6:return e===null&&ri(t),null;case 13:return Dc(e,t,n);case 4:return di(t,t.stateNode.containerInfo),s=t.pendingProps,e===null?t.child=Wn(t,null,s,n):Ge(e,t,s,n),t.child;case 11:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:kt(s,a),_c(e,t,s,a,n);case 7:return Ge(e,t,t.pendingProps,n),t.child;case 8:return Ge(e,t,t.pendingProps.children,n),t.child;case 12:return Ge(e,t,t.pendingProps.children,n),t.child;case 10:e:{if(s=t.type._context,a=t.pendingProps,i=t.memoizedProps,u=a.value,ge(gs,s._currentValue),s._currentValue=u,i!==null)if(yt(i.value,u)){if(i.children===a.children&&!Qe.current){t=zt(e,t,n);break e}}else for(i=t.child,i!==null&&(i.return=t);i!==null;){var h=i.dependencies;if(h!==null){u=i.child;for(var p=h.firstContext;p!==null;){if(p.context===s){if(i.tag===1){p=It(-1,n&-n),p.tag=2;var j=i.updateQueue;if(j!==null){j=j.shared;var E=j.pending;E===null?p.next=p:(p.next=E.next,E.next=p),j.pending=p}}i.lanes|=n,p=i.alternate,p!==null&&(p.lanes|=n),li(i.return,n,t),h.lanes|=n;break}p=p.next}}else if(i.tag===10)u=i.type===t.type?null:i.child;else if(i.tag===18){if(u=i.return,u===null)throw Error(l(341));u.lanes|=n,h=u.alternate,h!==null&&(h.lanes|=n),li(u,n,t),u=i.sibling}else u=i.child;if(u!==null)u.return=i;else for(u=i;u!==null;){if(u===t){u=null;break}if(i=u.sibling,i!==null){i.return=u.return,u=i;break}u=u.return}i=u}Ge(e,t,a.children,n),t=t.child}return t;case 9:return a=t.type,s=t.pendingProps.children,$n(t,n),a=ht(a),s=s(a),t.flags|=1,Ge(e,t,s,n),t.child;case 14:return s=t.type,a=kt(s,t.pendingProps),a=kt(s.type,a),Tc(e,t,s,a,n);case 15:return Ec(e,t,t.type,t.pendingProps,n);case 17:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:kt(s,a),Ts(e,t),t.tag=1,Xe(s)?(e=!0,us(t)):e=!1,$n(t,n),kc(t,s,a),Si(t,s,a,n),Ti(null,t,s,!0,e,n);case 19:return zc(e,t,n);case 22:return Mc(e,t,n)}throw Error(l(156,t.tag))};function ou(e,t){return Oo(e,t)}function Wm(e,t,n,s){this.tag=e,this.key=n,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=t,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=s,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function gt(e,t,n,s){return new Wm(e,t,n,s)}function qi(e){return e=e.prototype,!(!e||!e.isReactComponent)}function Um(e){if(typeof e=="function")return qi(e)?1:0;if(e!=null){if(e=e.$$typeof,e===we)return 11;if(e===St)return 14}return 2}function rn(e,t){var n=e.alternate;return n===null?(n=gt(e.tag,t,e.key,e.mode),n.elementType=e.elementType,n.type=e.type,n.stateNode=e.stateNode,n.alternate=e,e.alternate=n):(n.pendingProps=t,n.type=e.type,n.flags=0,n.subtreeFlags=0,n.deletions=null),n.flags=e.flags&14680064,n.childLanes=e.childLanes,n.lanes=e.lanes,n.child=e.child,n.memoizedProps=e.memoizedProps,n.memoizedState=e.memoizedState,n.updateQueue=e.updateQueue,t=e.dependencies,n.dependencies=t===null?null:{lanes:t.lanes,firstContext:t.firstContext},n.sibling=e.sibling,n.index=e.index,n.ref=e.ref,n}function Bs(e,t,n,s,a,i){var u=2;if(s=e,typeof e=="function")qi(e)&&(u=1);else if(typeof e=="string")u=5;else e:switch(e){case J:return kn(n.children,a,i,t);case pe:u=8,a|=8;break;case Se:return e=gt(12,n,t,a|2),e.elementType=Se,e.lanes=i,e;case _e:return e=gt(13,n,t,a),e.elementType=_e,e.lanes=i,e;case Be:return e=gt(19,n,t,a),e.elementType=Be,e.lanes=i,e;case Ne:return Os(n,a,i,t);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case De:u=10;break e;case te:u=9;break e;case we:u=11;break e;case St:u=14;break e;case qe:u=16,s=null;break e}throw Error(l(130,e==null?e:typeof e,""))}return t=gt(u,n,t,a),t.elementType=e,t.type=s,t.lanes=i,t}function kn(e,t,n,s){return e=gt(7,e,s,t),e.lanes=n,e}function Os(e,t,n,s){return e=gt(22,e,s,t),e.elementType=Ne,e.lanes=n,e.stateNode={isHidden:!1},e}function Qi(e,t,n){return e=gt(6,e,null,t),e.lanes=n,e}function Xi(e,t,n){return t=gt(4,e.children!==null?e.children:[],e.key,t),t.lanes=n,t.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},t}function $m(e,t,n,s,a){this.tag=t,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=ba(0),this.expirationTimes=ba(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=ba(0),this.identifierPrefix=s,this.onRecoverableError=a,this.mutableSourceEagerHydrationData=null}function Yi(e,t,n,s,a,i,u,h,p){return e=new $m(e,t,n,h,p),t===1?(t=1,i===!0&&(t|=8)):t=0,i=gt(3,null,null,t),e.current=i,i.stateNode=e,i.memoizedState={element:s,isDehydrated:n,cache:null,transitions:null,pendingSuspenseBoundaries:null},ui(i),e}function Vm(e,t,n){var s=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:F,key:s==null?null:""+s,children:e,containerInfo:t,implementation:n}}function lu(e){if(!e)return qt;e=e._reactInternals;e:{if(ln(e)!==e||e.tag!==1)throw Error(l(170));var t=e;do{switch(t.tag){case 3:t=t.stateNode.context;break e;case 1:if(Xe(t.type)){t=t.stateNode.__reactInternalMemoizedMergedChildContext;break e}}t=t.return}while(t!==null);throw Error(l(171))}if(e.tag===1){var n=e.type;if(Xe(n))return Il(e,n,t)}return t}function cu(e,t,n,s,a,i,u,h,p){return e=Yi(n,s,!0,e,a,i,u,h,p),e.context=lu(null),n=e.current,s=Ke(),a=tn(n),i=It(s,a),i.callback=t??null,Yt(n,i,a),e.current.lanes=a,rr(e,a,s),Ze(e,s),e}function Ws(e,t,n,s){var a=t.current,i=Ke(),u=tn(a);return n=lu(n),t.context===null?t.context=n:t.pendingContext=n,t=It(i,u),t.payload={element:e},s=s===void 0?null:s,s!==null&&(t.callback=s),e=Yt(a,t,u),e!==null&&(bt(e,a,u,i),ys(e,a,u)),u}function Us(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function uu(e,t){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var n=e.retryLane;e.retryLane=n!==0&&n<t?n:t}}function Ji(e,t){uu(e,t),(e=e.alternate)&&uu(e,t)}function Hm(){return null}var du=typeof reportError=="function"?reportError:function(e){console.error(e)};function Zi(e){this._internalRoot=e}$s.prototype.render=Zi.prototype.render=function(e){var t=this._internalRoot;if(t===null)throw Error(l(409));Ws(e,t,null,null)},$s.prototype.unmount=Zi.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var t=e.containerInfo;vn(function(){Ws(null,e,null,null)}),t[Pt]=null}};function $s(e){this._internalRoot=e}$s.prototype.unstable_scheduleHydration=function(e){if(e){var t=qo();e={blockedOn:null,target:e,priority:t};for(var n=0;n<$t.length&&t!==0&&t<$t[n].priority;n++);$t.splice(n,0,e),n===0&&Yo(e)}};function eo(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function Vs(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function mu(){}function Gm(e,t,n,s,a){if(a){if(typeof s=="function"){var i=s;s=function(){var j=Us(u);i.call(j)}}var u=cu(t,s,e,0,null,!1,!1,"",mu);return e._reactRootContainer=u,e[Pt]=u.current,vr(e.nodeType===8?e.parentNode:e),vn(),u}for(;a=e.lastChild;)e.removeChild(a);if(typeof s=="function"){var h=s;s=function(){var j=Us(p);h.call(j)}}var p=Yi(e,0,!1,null,null,!1,!1,"",mu);return e._reactRootContainer=p,e[Pt]=p.current,vr(e.nodeType===8?e.parentNode:e),vn(function(){Ws(t,p,n,s)}),p}function Hs(e,t,n,s,a){var i=n._reactRootContainer;if(i){var u=i;if(typeof a=="function"){var h=a;a=function(){var p=Us(u);h.call(p)}}Ws(t,u,e,a)}else u=Gm(n,t,e,a,s);return Us(u)}Go=function(e){switch(e.tag){case 3:var t=e.stateNode;if(t.current.memoizedState.isDehydrated){var n=nr(t.pendingLanes);n!==0&&(Sa(t,n|1),Ze(t,Te()),(le&6)===0&&(qn=Te()+500,Qt()))}break;case 13:vn(function(){var s=Dt(e,1);if(s!==null){var a=Ke();bt(s,e,1,a)}}),Ji(e,1)}},Na=function(e){if(e.tag===13){var t=Dt(e,134217728);if(t!==null){var n=Ke();bt(t,e,134217728,n)}Ji(e,134217728)}},Ko=function(e){if(e.tag===13){var t=tn(e),n=Dt(e,t);if(n!==null){var s=Ke();bt(n,e,t,s)}Ji(e,t)}},qo=function(){return he},Qo=function(e,t){var n=he;try{return he=e,t()}finally{he=n}},va=function(e,t,n){switch(t){case"input":if(ca(e,n),t=n.name,n.type==="radio"&&t!=null){for(n=e;n.parentNode;)n=n.parentNode;for(n=n.querySelectorAll("input[name="+JSON.stringify(""+t)+'][type="radio"]'),t=0;t<n.length;t++){var s=n[t];if(s!==e&&s.form===e.form){var a=ls(s);if(!a)throw Error(l(90));xo(s),ca(s,a)}}}break;case"textarea":So(e,n);break;case"select":t=n.value,t!=null&&Nn(e,!!n.multiple,t,!1)}},Ro=Hi,Ao=vn;var Km={usingClientEntryPoint:!1,Events:[kr,Dn,ls,Po,Lo,Hi]},Ar={findFiberByHostInstance:cn,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},qm={bundleType:Ar.bundleType,version:Ar.version,rendererPackageName:Ar.rendererPackageName,rendererConfig:Ar.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:ne.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=Fo(e),e===null?null:e.stateNode},findFiberByHostInstance:Ar.findFiberByHostInstance||Hm,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Gs=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Gs.isDisabled&&Gs.supportsFiber)try{$r=Gs.inject(qm),Nt=Gs}catch{}}return et.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Km,et.createPortal=function(e,t){var n=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!eo(t))throw Error(l(200));return Vm(e,t,null,n)},et.createRoot=function(e,t){if(!eo(e))throw Error(l(299));var n=!1,s="",a=du;return t!=null&&(t.unstable_strictMode===!0&&(n=!0),t.identifierPrefix!==void 0&&(s=t.identifierPrefix),t.onRecoverableError!==void 0&&(a=t.onRecoverableError)),t=Yi(e,1,!1,null,null,n,!1,s,a),e[Pt]=t.current,vr(e.nodeType===8?e.parentNode:e),new Zi(t)},et.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var t=e._reactInternals;if(t===void 0)throw typeof e.render=="function"?Error(l(188)):(e=Object.keys(e).join(","),Error(l(268,e)));return e=Fo(t),e=e===null?null:e.stateNode,e},et.flushSync=function(e){return vn(e)},et.hydrate=function(e,t,n){if(!Vs(t))throw Error(l(200));return Hs(null,e,t,!0,n)},et.hydrateRoot=function(e,t,n){if(!eo(e))throw Error(l(405));var s=n!=null&&n.hydratedSources||null,a=!1,i="",u=du;if(n!=null&&(n.unstable_strictMode===!0&&(a=!0),n.identifierPrefix!==void 0&&(i=n.identifierPrefix),n.onRecoverableError!==void 0&&(u=n.onRecoverableError)),t=cu(t,null,e,1,n??null,a,!1,i,u),e[Pt]=t.current,vr(e),s)for(e=0;e<s.length;e++)n=s[e],a=n._getVersion,a=a(n._source),t.mutableSourceEagerHydrationData==null?t.mutableSourceEagerHydrationData=[n,a]:t.mutableSourceEagerHydrationData.push(n,a);return new $s(t)},et.render=function(e,t,n){if(!Vs(t))throw Error(l(200));return Hs(null,e,t,!1,n)},et.unmountComponentAtNode=function(e){if(!Vs(e))throw Error(l(40));return e._reactRootContainer?(vn(function(){Hs(null,null,e,!1,function(){e._reactRootContainer=null,e[Pt]=null})}),!0):!1},et.unstable_batchedUpdates=Hi,et.unstable_renderSubtreeIntoContainer=function(e,t,n,s){if(!Vs(n))throw Error(l(200));if(e==null||e._reactInternals===void 0)throw Error(l(38));return Hs(e,t,n,!1,s)},et.version="18.3.1-next-f1338f8080-20240426",et}var wu;function sh(){if(wu)return ro.exports;wu=1;function o(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(o)}catch(c){console.error(c)}}return o(),ro.exports=rh(),ro.exports}var ju;function ah(){if(ju)return Ks;ju=1;var o=sh();return Ks.createRoot=o.createRoot,Ks.hydrateRoot=o.hydrateRoot,Ks}var ih=ah();class oh extends Error{constructor(l,d){super(l);hu(this,"status");this.status=d}}async function st(o,c){const l=await fetch(o,{...c,credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json",...c==null?void 0:c.headers}}),d=await l.json().catch(()=>({}));if(!l.ok)throw new oh(d.error||l.statusText||"Request failed",l.status);return d}const bu=()=>st("/auth/status"),lh=()=>st("/api/config"),po=()=>st("/api/botstats"),ch=()=>st("/api/commands"),Su=()=>st("/api/guilds"),Nu=()=>st("/api/me/overview"),uh=o=>st(`/api/guild/${o}/overview`),dh=o=>st(`/api/guild/${o}/levels`),Cu=o=>st(`/api/guild/${o}/config`),_u=o=>st(`/api/guild/${o}/resources`);function ra(o,c,l,d){return st(`/api/guild/${o}/config/${c}`,{method:"POST",headers:d?{"X-CSRF-Token":d}:void 0,body:JSON.stringify(l)})}function mh(o,c,l){return st(`/api/guild/${o}/config/profile`,{method:"POST",headers:l?{"X-CSRF-Token":l}:void 0,body:JSON.stringify(c)})}function Uu(o){return o.replace(/\/+$/,"")||"/"}function Tu(o=window.location.pathname){const c=Uu(o);return c==="/commands"?"commands":c==="/docs"?"docs":c.startsWith("/docs/")?"docs-detail":c==="/dashboard"||c.startsWith("/dashboard/")?"dashboard":c==="/privacy"?"privacy":c==="/terms"?"terms":c==="/community"?"community":c==="/donate"||c.startsWith("/donate")?"donate":c==="/transcript"||c.startsWith("/transcript/")?"transcript":c==="/changelog"?"changelog":c.startsWith("/changelog/")?"changelog-detail":"home"}function Ir(o,c="overview"){return o?`/dashboard/${o}/${c}`:"/dashboard"}function Eu(){return"/dashboard/servers"}function Mu(){const o=Uu(window.location.pathname).split("/").filter(Boolean),c=["overview","leveling","moderation","server","ai","customization"];return o[1]==="servers"?{view:"servers",guildId:null,section:"overview"}:o[1]?{view:"guild",guildId:o[1]||null,section:c.includes(o[2])?o[2]:"overview"}:{view:"overview",guildId:null,section:"overview"}}function oe(o){o.startsWith("/")&&(window.history.pushState({},"",o),window.dispatchEvent(new PopStateEvent("popstate")),window.scrollTo({top:0,behavior:"smooth"}))}function ea({onNavigate:o}){return r.jsxs("a",{className:"brand",href:"/",onClick:c=>{c.preventDefault(),o?o():oe("/")},children:[r.jsx("span",{className:"brand-mark",children:"n"}),r.jsx("span",{children:"niko"})]})}function Bt(){return r.jsxs("footer",{className:"site-footer",children:[r.jsx(ea,{}),r.jsx("span",{children:"Built for communities that care."}),r.jsxs("div",{children:[r.jsx("a",{href:"/changelog",onClick:o=>{o.preventDefault(),oe("/changelog")},children:"Changelog"}),r.jsx("a",{href:"/privacy",onClick:o=>{o.preventDefault(),oe("/privacy")},children:"Privacy"}),r.jsx("a",{href:"/terms",onClick:o=>{o.preventDefault(),oe("/terms")},children:"Terms"}),r.jsx("a",{href:"/community",onClick:o=>{o.preventDefault(),oe("/community")},children:"Community Policy"}),r.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"GitHub"})]})]})}/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const $u=(...o)=>o.filter((c,l,d)=>!!c&&c.trim()!==""&&d.indexOf(c)===l).join(" ").trim();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const hh=o=>o.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ph=o=>o.replace(/^([A-Z])|[\s-_]+(\w)/g,(c,l,d)=>d?d.toUpperCase():l.toLowerCase());/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Pu=o=>{const c=ph(o);return c.charAt(0).toUpperCase()+c.slice(1)};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var io={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const fh=o=>{for(const c in o)if(c.startsWith("aria-")||c==="role"||c==="title")return!0;return!1},gh=R.createContext({}),vh=()=>R.useContext(gh),yh=R.forwardRef(({color:o,size:c,strokeWidth:l,absoluteStrokeWidth:d,className:m="",children:f,iconNode:v,...M},w)=>{const{size:z=24,strokeWidth:N=2,absoluteStrokeWidth:C=!1,color:P="currentColor",className:I=""}=vh()??{},D=d??C?Number(l??N)*24/Number(c??z):l??N;return R.createElement("svg",{ref:w,...io,width:c??z??io.width,height:c??z??io.height,stroke:o??P,strokeWidth:D,className:$u("lucide",I,m),...!f&&!fh(M)&&{"aria-hidden":"true"},...M},[...v.map(([B,b])=>R.createElement(B,b)),...Array.isArray(f)?f:[f]])});/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const at=(o,c)=>{const l=R.forwardRef(({className:d,...m},f)=>R.createElement(yh,{ref:f,iconNode:c,className:$u(`lucide-${hh(Pu(o))}`,`lucide-${o}`,d),...m}));return l.displayName=Pu(o),l};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const xh=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]],kh=at("arrow-right",xh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const wh=[["path",{d:"M12 5v16",key:"1f6ucr"}],["path",{d:"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z",key:"1fyvmf"}]],Lu=at("book-open",wh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jh=[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],oo=at("chart-column",jh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const bh=[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]],Sh=at("external-link",bh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Nh=[["rect",{width:"7",height:"7",x:"3",y:"3",rx:"1",key:"1g98yp"}],["rect",{width:"7",height:"7",x:"14",y:"3",rx:"1",key:"6d4xhi"}],["rect",{width:"7",height:"7",x:"14",y:"14",rx:"1",key:"nxv5o0"}],["rect",{width:"7",height:"7",x:"3",y:"14",rx:"1",key:"1bb6yr"}]],fo=at("layout-grid",Nh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ch=[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]],_h=at("lock-keyhole",Ch);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Th=[["path",{d:"M4 5h16",key:"1tepv9"}],["path",{d:"M4 12h16",key:"1lakjw"}],["path",{d:"M4 19h16",key:"1djgab"}]],Eh=at("menu",Th);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Mh=[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]],Ph=at("search",Mh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Lh=[["path",{d:"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915",key:"1i5ecw"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]],qs=at("settings",Lh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Rh=[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}]],lo=at("shield",Rh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ah=[["path",{d:"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",key:"1s2grr"}],["path",{d:"M20 2v4",key:"1rf3ol"}],["path",{d:"M22 4h-4",key:"gwowj6"}],["circle",{cx:"4",cy:"20",r:"2",key:"6kqj1y"}]],Qs=at("sparkles",Ah);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Dh=[["path",{d:"M12 19h8",key:"baeox8"}],["path",{d:"m4 17 6-6-6-6",key:"1yngyt"}]],Ih=at("terminal",Dh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const zh=[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["path",{d:"M16 3.128a4 4 0 0 1 0 7.744",key:"16gr8j"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}]],Ru=at("users",zh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Fh=[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]],Bh=at("x",Fh),Oh={arrow:kh,grid:fo,terminal:Ih,chart:oo,shield:lo,spark:Qs,users:Ru,settings:qs,book:Lu,external:Sh,menu:Eh,close:Bh,lock:_h,search:Ph,doc:Lu,utility:qs,icon_home:fo,icon_settings:qs,icon_economy:oo,icon_leveling:oo,icon_moderation:lo,icon_automod:lo,icon_heart:Qs,icon_utility:qs,icon_bot:Ru,icon_ai:Qs,icon_lightbulb:Qs};function K({name:o,size:c,className:l=""}){const d=Oh[o]||fo;return r.jsx(d,{className:`icon ${l}`.trim(),"aria-hidden":"true",focusable:"false",strokeWidth:1.8,style:c?{width:c,height:c}:void 0})}let Au=null,co=null;function sa(){const[o,c]=R.useState(Au);return R.useEffect(()=>{co||(co=lh().then(l=>Au=l)),co.then(c).catch(()=>{})},[]),o}function rt({page:o}){const c=sa();return r.jsxs("header",{className:"site-header",children:[r.jsx(ea,{}),r.jsxs("nav",{className:"site-nav","aria-label":"Main navigation",children:[r.jsx("a",{className:o==="home"?"active":"","aria-current":o==="home"?"page":void 0,href:"/",onClick:l=>{l.preventDefault(),oe("/")},children:"Home"}),r.jsx("a",{className:o==="commands"?"active":"","aria-current":o==="commands"?"page":void 0,href:"/commands",onClick:l=>{l.preventDefault(),oe("/commands")},children:"Commands"}),r.jsx("a",{className:o==="docs"?"active":"","aria-current":o==="docs"?"page":void 0,href:"/docs",onClick:l=>{l.preventDefault(),oe("/docs")},children:"Docs"}),r.jsx("a",{href:"/changelog",onClick:l=>{l.preventDefault(),oe("/changelog")},children:"Changelog"})]}),r.jsxs("div",{className:"header-actions",children:[r.jsxs("a",{className:"button button-small button-muted dashboard-link",href:"/dashboard",onClick:l=>{l.preventDefault(),oe("/dashboard")},children:["Dashboard ",r.jsx(K,{name:"arrow"})]}),r.jsx("a",{className:"button button-small button-primary",href:(c==null?void 0:c.invite_url)||"#",target:"_blank",rel:"noreferrer",children:"Add to Discord"})]})]})}const Du=typeof navigator<"u"?(navigator.language||"en").slice(0,2):"en";function go(o){const c=o.description;if(typeof c=="string")return c;if(c&&typeof c=="object"){const l=c;if(l[Du])return l[Du];if(l.en)return l.en;const d=Object.values(l).find(m=>typeof m=="string"&&m.length>0);if(d)return d}return"A Niko command for your server."}const Wh=[{value:"all",label:"All commands"},{value:"slash",label:"Slash"},{value:"prefix",label:"Prefix"},{value:"hybrid",label:"Hybrid"},{value:"context",label:"Context menus"}],ta={slash:"Slash command",prefix:"Prefix command",hybrid:"Hybrid command",context:"Context menu"};function jn(o){return o.type&&o.type in ta?o.type:"slash"}function Uh(o){return o.context_type==="user"?"Right-click a user":"Right-click a message"}function Vu(o){const c=jn(o);return c==="slash"?r.jsxs("code",{children:["/",o.name]}):c==="prefix"?r.jsxs("code",{children:[".",o.name]}):c==="hybrid"?r.jsxs(r.Fragment,{children:[r.jsxs("code",{children:["/",o.name]}),r.jsx("span",{className:"command-or",children:"or"}),r.jsxs("code",{children:[".",o.name]})]}):r.jsxs("code",{className:"context-invocation",children:[Uh(o)," · ",o.name]})}function Iu(o){return o!=null&&o.length?o:["Not specified"]}function $h({command:o,onClose:c}){R.useEffect(()=>{const v=M=>{M.key==="Escape"&&c()};return document.addEventListener("keydown",v),()=>document.removeEventListener("keydown",v)},[c]);const l=o.parameters||[],d=o.subcommands||[],m=Iu(o.aliases),f=Iu(o.permissions);return r.jsx("div",{className:"command-dialog-backdrop",role:"presentation",onMouseDown:v=>{v.currentTarget===v.target&&c()},children:r.jsxs("section",{className:"command-dialog",role:"dialog","aria-modal":"true","aria-labelledby":"command-dialog-title",children:[r.jsxs("header",{className:"command-dialog-header",children:[r.jsxs("div",{children:[r.jsxs("div",{className:"command-dialog-kicker",children:[o.category," · ",ta[jn(o)]]}),r.jsx("h2",{id:"command-dialog-title",children:Vu(o)})]}),r.jsx("button",{className:"dialog-close",type:"button",onClick:c,"aria-label":"Close command details",title:"Close command details",children:r.jsx(K,{name:"close"})})]}),r.jsxs("div",{className:"command-dialog-body",children:[r.jsx("p",{className:"command-dialog-description",children:go(o)}),r.jsxs("div",{className:"command-detail-grid",children:[r.jsxs("section",{className:"command-detail-section command-detail-wide",children:[r.jsx("h3",{children:"Usage"}),r.jsx("code",{className:"command-usage",children:o.usage||`${jn(o)==="context"?o.name:`/${o.name}`}`})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Permissions"}),r.jsx("ul",{className:"command-detail-list",children:f.map(v=>r.jsx("li",{children:v},v))})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Aliases"}),r.jsx("ul",{className:"command-detail-list",children:m.map(v=>r.jsx("li",{children:r.jsx("code",{children:v==="Not specified"?v:`.${v}`})},v))})]})]}),!!l.length&&r.jsxs("section",{className:"command-detail-section command-parameters",children:[r.jsx("h3",{children:"Parameters"}),r.jsx("div",{className:"command-parameter-list",children:l.map(v=>r.jsxs("div",{className:"command-parameter",children:[r.jsxs("div",{className:"command-parameter-title",children:[r.jsx("code",{children:v.name}),r.jsxs("span",{children:[v.required?"Required":"Optional"," · ",v.type]})]}),r.jsx("p",{children:v.description||"No description provided."})]},v.name))})]}),!!d.length&&r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Subcommands"}),r.jsx("div",{className:"subcommand-list",children:d.map(v=>r.jsxs("code",{children:[o.name," ",v]},v))})]})]}),r.jsxs("footer",{className:"command-dialog-footer",children:[r.jsx("span",{children:"Command registry details are generated from the live bot."}),r.jsx("button",{className:"button button-primary button-small",type:"button",onClick:c,children:"Done"})]})]})})}function Vh(){const[o,c]=R.useState([]),[l,d]=R.useState(null),[m,f]=R.useState(""),[v,M]=R.useState("all"),[w,z]=R.useState("all"),[N,C]=R.useState(!0),[P,I]=R.useState("");R.useEffect(()=>{ch().then(c).catch(()=>I("The command registry is unavailable right now.")).finally(()=>C(!1))},[]),R.useEffect(()=>{if(!l)return;const b=document.body.style.overflow;return document.body.style.overflow="hidden",()=>{document.body.style.overflow=b}},[l]);const D=R.useMemo(()=>["all",...Array.from(new Set(o.map(b=>b.category))).sort()],[o]),B=o.filter(b=>{const Q=`${b.name} ${go(b)} ${b.category} ${ta[jn(b)]} ${b.context_type||""} ${(b.aliases||[]).join(" ")}`.toLowerCase();return(w==="all"||jn(b)===w)&&(v==="all"||b.category===v)&&Q.includes(m.trim().toLowerCase())});return r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:"commands"}),r.jsxs("main",{className:"shell page-main",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Reference library"}),r.jsxs("h1",{children:["Everything Niko",r.jsx("br",{}),r.jsx("em",{children:"knows how to do."})]}),r.jsx("p",{children:"Browse slash, prefix, hybrid, and context commands from the live bot registry. Select any command for permissions, aliases, parameters, usage, and subcommands."})]}),r.jsxs("div",{className:"command-toolbar",children:[r.jsxs("label",{className:"search-field",children:[r.jsx("span",{"aria-hidden":"true",children:"⌕"}),r.jsx("input",{value:m,onChange:b=>f(b.target.value),placeholder:"Search commands","aria-label":"Search commands"})]}),r.jsxs("div",{className:"command-filters",children:[r.jsx("div",{className:"filter-list","aria-label":"Command types",children:Wh.map(b=>r.jsx("button",{type:"button",className:w===b.value?"filter active":"filter","aria-pressed":w===b.value,onClick:()=>z(b.value),children:b.label},b.value))}),r.jsx("div",{className:"filter-list","aria-label":"Command categories",children:D.map(b=>r.jsx("button",{type:"button",className:v===b?"filter active":"filter","aria-pressed":v===b,onClick:()=>M(b),children:b==="all"?"All categories":b},b))})]})]}),r.jsxs("div",{className:"command-meta",children:[r.jsx("strong",{children:N?"…":B.length})," commands ",r.jsx("span",{children:"·"})," live bot registry ",r.jsx("span",{children:"·"})," select a card for details"]}),P&&r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Could not load commands"}),r.jsx("span",{children:P})]}),r.jsxs("div",{className:"commands-grid",children:[B.map(b=>r.jsxs("button",{className:"command-card",type:"button",onClick:()=>d(b),"aria-label":`View details for ${b.name}`,children:[r.jsxs("span",{className:"command-card-head",children:[r.jsx("span",{className:"command-name",children:Vu(b)}),r.jsx("span",{className:"command-type",children:ta[jn(b)]})]}),r.jsx("span",{className:"command-card-description",children:go(b)}),r.jsxs("span",{className:"command-card-footer",children:[r.jsx("span",{className:"category-tag",children:b.category}),r.jsxs("span",{className:"command-expand",children:[r.jsx("span",{children:"Details"}),r.jsx(K,{name:"arrow",size:14})]})]})]},`${jn(b)}-${b.context_type||""}-${b.category}-${b.name}`)),!N&&!P&&!B.length&&r.jsx("div",{className:"empty-state",children:"No commands match that search."})]})]}),r.jsx(Bt,{}),l&&r.jsx($h,{command:l,onClose:()=>d(null)})]})}function Le(o){return o==null?"—":new Intl.NumberFormat("en-US",{notation:o>9999?"compact":"standard"}).format(o)}function Hu(o){return(o==null?void 0:o.global_name)||(o==null?void 0:o.username)||"there"}function Gu(o){return o.split(/\s+/).map(c=>c[0]).join("").slice(0,2).toUpperCase()}function yo({guild:o,className:c="guild-avatar"}){return r.jsx("span",{className:c,"aria-hidden":"true",children:o.icon_url?r.jsx("img",{src:o.icon_url,alt:""}):o.name.slice(0,1).toUpperCase()})}function Ku({user:o,className:c="avatar"}){const l=o.avatar?`https://cdn.discordapp.com/avatars/${o.id}/${o.avatar}.${o.avatar.startsWith("a_")?"gif":"png"}?size=64`:null;return r.jsx("span",{className:c,"aria-hidden":"true",children:l?r.jsx("img",{src:l,alt:""}):Gu(o.global_name||o.username||"Niko")})}function Hh({name:o,avatarUrl:c,className:l="member-avatar"}){return r.jsx("span",{className:l,"aria-hidden":"true",children:c?r.jsx("img",{src:c,alt:""}):Gu(o)})}const Gh=[["overview","Overview","grid","At a glance"],["leveling","Leveling","spark","Reward participation"],["moderation","Moderation","shield","Keep things steady"],["server","Server","settings","Manage server features"],["ai","AI controls","settings","Shape Niko’s voice"],["customization","Customization","paint","Niko’s server identity"]];function Kh({user:o,guilds:c,selectedGuild:l,view:d,section:m,stats:f,onHome:v,onServers:M,onGuildChange:w,onSectionChange:z,onRefresh:N,refreshing:C,children:P}){const I=c.filter(b=>b.installed!==!1),D=(b=!1)=>r.jsx("nav",{className:b?"dash-nav dash-nav-mobile":"dash-nav","aria-label":"Server settings",children:Gh.map(([Q,S,q])=>r.jsxs("button",{className:d==="guild"&&m===Q?"active":"","aria-current":d==="guild"&&m===Q?"page":void 0,onClick:()=>z(Q),children:[r.jsx(K,{name:q}),r.jsx("span",{children:S})]},Q))}),B=(b=!1)=>r.jsxs("nav",{className:b?"dash-nav dash-primary-nav dash-nav-mobile":"dash-nav dash-primary-nav","aria-label":"Dashboard",children:[r.jsxs("button",{className:d==="overview"?"active":"","aria-current":d==="overview"?"page":void 0,onClick:v,children:[r.jsx(K,{name:"grid"}),r.jsx("span",{children:"My overview"})]}),r.jsxs("button",{className:d==="servers"?"active":"","aria-current":d==="servers"?"page":void 0,onClick:M,children:[r.jsx(K,{name:"users"}),r.jsx("span",{children:"My servers"})]})]});return r.jsxs("div",{className:"dashboard-layout",children:[r.jsxs("aside",{className:"dash-sidebar",children:[r.jsx(ea,{onNavigate:v}),r.jsxs("div",{className:"side-rail-heading",children:[r.jsx("span",{className:"side-label",children:"Workspace"}),r.jsxs("span",{className:"rail-status",children:[r.jsx("span",{className:"status-dot"})," Live"]})]}),B(),d==="guild"&&l&&r.jsxs(r.Fragment,{children:[r.jsx("div",{className:"side-label side-label-settings",children:"Current server"}),r.jsxs("div",{className:"side-guild",children:[r.jsx(yo,{guild:l}),r.jsxs("span",{children:[r.jsx("strong",{children:l.name}),r.jsx("small",{children:"Live configuration"})]}),r.jsx("span",{className:"guild-presence",title:"Niko is connected",children:r.jsx("span",{className:"status-dot"})})]}),r.jsxs("div",{className:"side-settings-caption",children:[r.jsx("span",{children:"Settings map"}),r.jsx("small",{children:"Pick a room to tune"})]}),D()]}),d!=="guild"&&r.jsxs("div",{className:"side-rail-note",children:[r.jsx("span",{className:"panel-kicker",children:"Niko workspace"}),r.jsxs("strong",{children:["Make the useful",r.jsx("br",{}),"things easier to find."]}),r.jsx("small",{children:"Your servers and their live signals, in one quiet place."})]}),r.jsxs("div",{className:"sidebar-bottom",children:[r.jsxs("span",{className:"online-label",children:[r.jsx("span",{className:"status-dot"})," Niko is online"]}),r.jsxs("small",{children:[Le(f==null?void 0:f.guild_count)," connected servers · v",(f==null?void 0:f.version)||"1.0"]}),r.jsxs("a",{href:"/",onClick:b=>{b.preventDefault(),oe("/")},children:["Back to public site ",r.jsx(K,{name:"arrow"})]})]})]}),r.jsxs("div",{className:"dash-content",children:[r.jsxs("header",{className:"dash-topbar",children:[r.jsxs("div",{className:"mobile-top-row",children:[r.jsx("span",{className:"mobile-brand",children:r.jsx(ea,{})}),r.jsxs("span",{className:"mobile-status",children:[r.jsx("span",{className:"status-dot"})," Online"]})]}),r.jsxs("div",{className:"dash-top-actions",children:[d==="guild"?r.jsxs("label",{className:"guild-switcher",children:[r.jsx("span",{className:"sr-only",children:"Switch server"}),r.jsxs("select",{value:(l==null?void 0:l.id)||"",onChange:b=>{const Q=I.find(S=>S.id===b.target.value);Q&&w(Q)},children:[r.jsx("option",{value:"",disabled:!0,children:"Switch server"}),I.map(b=>r.jsx("option",{value:b.id,children:b.name},b.id))]})]}):r.jsxs("button",{className:"button button-muted button-small top-action",onClick:M,children:[r.jsx(K,{name:"users"})," Browse servers"]}),r.jsxs("button",{className:"button button-muted button-small top-action refresh-action",onClick:N,disabled:C,"aria-label":"Refresh dashboard data",children:[r.jsx(K,{name:"spark"})," ",C?"Refreshing…":"Refresh data"]}),d==="guild"&&r.jsxs("span",{className:"connection-chip",children:[r.jsx("span",{className:"status-dot"})," Connected"]}),r.jsxs("div",{className:"user-pill",children:[r.jsx(Ku,{user:o}),r.jsx("span",{children:Hu(o)})]}),r.jsx("a",{className:"logout-link",href:"/auth/logout",children:"Log out"})]})]}),r.jsx("div",{className:"mobile-primary-bar",children:B(!0)}),d==="guild"&&r.jsx("div",{className:"mobile-section-bar",children:D(!0)}),r.jsx("main",{className:"dash-main",children:P})]})]})}function on({eyebrow:o,title:c,text:l}){return r.jsxs("div",{className:"dash-heading",children:[r.jsxs("div",{className:"heading-meta",children:[r.jsx("div",{className:"eyebrow",children:o}),r.jsx("span",{className:"heading-context",children:"NIKO / CONTROL ROOM"})]}),r.jsx("h2",{children:c}),r.jsx("p",{children:l})]})}function Mt({label:o,value:c,note:l,accent:d=""}){return r.jsxs("div",{className:`dash-stat ${d}`,children:[r.jsx("span",{children:o}),r.jsx("strong",{children:c}),r.jsx("small",{children:l})]})}function qh({user:o,overview:c,guilds:l,onServers:d,onManage:m}){const f=l.filter(v=>v.installed!==!1);return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Personal overview",title:"Your Niko snapshot.",text:"Keep an eye on your progress, then jump into a server when you’re ready to tune the room."}),r.jsxs("div",{className:"overview-intro",children:[r.jsxs("div",{className:"profile-card",children:[r.jsx(Ku,{user:o,className:"profile-avatar"}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Signed in as"}),r.jsx("h3",{children:Hu(o)}),r.jsx("p",{children:"Personal economy profile"})]})]}),r.jsxs("button",{className:"button button-primary",onClick:d,children:["Manage a server ",r.jsx(K,{name:"arrow"})]})]}),r.jsxs("div",{className:"dash-stats overview-stats",children:[r.jsx(Mt,{label:"Net worth",value:Le(c==null?void 0:c.net_worth),note:"Across your Niko profile",accent:"accent-orange"}),r.jsx(Mt,{label:"In your wallet",value:Le(c==null?void 0:c.balance),note:"Ready to spend",accent:"accent-violet"}),r.jsx(Mt,{label:"In your vault",value:Le(c==null?void 0:c.bank),note:"Saved for later",accent:"accent-blue"}),r.jsx(Mt,{label:"Current level",value:Le(c==null?void 0:c.level),note:c!=null&&c.job?`Working as a ${c.job}`:"Keep showing up",accent:"accent-green"})]}),r.jsxs("div",{className:"dash-columns overview-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Progress"}),r.jsx("h3",{children:"Your momentum"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(K,{name:"spark"})})]}),r.jsxs("div",{className:"metric-list",children:[r.jsxs("div",{children:[r.jsx("span",{children:"Daily streak"}),r.jsxs("strong",{children:[Le(c==null?void 0:c.daily_streak)," ",r.jsx("small",{children:"days"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Achievements"}),r.jsxs("strong",{children:[Le(c==null?void 0:c.achievements)," ",r.jsx("small",{children:"unlocked"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Total earned"}),r.jsxs("strong",{children:[Le(c==null?void 0:c.total_earned)," ",r.jsx("small",{children:"coins"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Economy standing"}),r.jsxs("strong",{children:[c!=null&&c.economy_rank?`#${Le(c.economy_rank)}`:"—"," ",r.jsx("small",{children:c!=null&&c.economy_profiles?`of ${Le(c.economy_profiles)}`:""})]})]})]})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Quick access"}),r.jsx("h3",{children:"Your servers"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(K,{name:"users"})})]}),r.jsxs("div",{className:"mini-server-list",children:[f.slice(0,4).map(v=>r.jsxs("button",{onClick:()=>m(v),children:[r.jsx(yo,{guild:v}),r.jsx("span",{children:v.name}),r.jsx(K,{name:"arrow"})]},v.id)),!f.length&&r.jsx("p",{className:"empty-state compact",children:"Add Niko to a server to start managing it."})]}),r.jsxs("button",{className:"text-link overview-link",onClick:d,children:["View all servers ",r.jsx(K,{name:"arrow"})]})]})]})]})}function zu({guild:o,onManage:c}){const l=o.installed!==!1;return r.jsxs("article",{className:"server-card",children:[r.jsxs("div",{className:"server-card-heading",children:[r.jsx(yo,{guild:o,className:"server-avatar"}),r.jsx("span",{className:"server-status",children:l?"Niko is installed":"Ready to add"})]}),r.jsx("h3",{children:o.name}),r.jsx("p",{children:l?"Open the dashboard to manage Niko’s features and settings.":"You have permission to manage this server. Add Niko to unlock its controls."}),l?r.jsxs("button",{className:"button button-muted button-small",onClick:()=>c(o),children:["Open settings ",r.jsx(K,{name:"arrow"})]}):r.jsxs("a",{className:"button button-primary button-small",href:o.invite_url||"#",target:"_blank",rel:"noreferrer",children:["Add Niko ",r.jsx(K,{name:"external"})]})]})}function Qh({guilds:o,onManage:c}){const l=o.filter(m=>m.installed!==!1),d=o.filter(m=>m.installed===!1);return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Servers",title:"Choose where to work.",text:"Manage servers with Niko already installed, or add Niko to another server you can administer."}),r.jsxs("div",{className:"server-summary",children:[r.jsxs("div",{children:[r.jsx("strong",{children:Le(l.length)}),r.jsx("span",{children:"Connected to Niko"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:Le(d.length)}),r.jsx("span",{children:"Ready to add"})]}),r.jsxs("div",{className:"server-summary-note",children:[r.jsx(K,{name:"shield"}),r.jsx("span",{children:"Only servers where you have Manage Server access are shown."})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Connected"}),r.jsx("h3",{children:"Manage a server"})]}),r.jsx("span",{className:"section-count",children:l.length})]}),r.jsxs("div",{className:"server-grid",children:[l.map(m=>r.jsx(zu,{guild:m,onManage:c},m.id)),!l.length&&r.jsxs("div",{className:"empty-state",children:[r.jsx("strong",{children:"No connected servers yet."}),r.jsx("span",{children:"Add Niko below, then come back here to manage it."})]})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Available to you"}),r.jsx("h3",{children:"Add Niko to a server"})]}),r.jsx("span",{className:"section-count",children:d.length})]}),r.jsxs("div",{className:"server-grid",children:[d.map(m=>r.jsx(zu,{guild:m,onManage:c},m.id)),!d.length&&r.jsx("div",{className:"server-note",children:"Niko is already installed in every server you can manage."})]})]})]})}function qu({rows:o}){return r.jsxs("div",{className:"rank-list",children:[o.slice(0,5).map((c,l)=>r.jsxs("div",{className:"rank-row",children:[r.jsx("span",{className:`rank rank-${l+1}`,children:String(l+1).padStart(2,"0")}),r.jsxs("span",{className:"rank-user",children:[r.jsx(Hh,{name:c.display_name||c.username||"Unknown member",avatarUrl:c.avatar_url}),r.jsxs("span",{children:[r.jsx("strong",{children:c.display_name||c.username||"Unknown member"}),c.username&&c.display_name&&r.jsxs("small",{children:["@",c.username]})]})]}),r.jsxs("strong",{children:[Le(c.xp),r.jsx("small",{children:" xp"})]})]},`${c.user_id}-${l}`)),!o.length&&r.jsx("div",{className:"empty-state compact",children:"No data recorded yet."})]})}function Xh({overview:o}){return r.jsxs(r.Fragment,{children:[r.jsxs("div",{className:"guild-welcome",children:[r.jsxs("div",{children:[r.jsx("span",{className:"welcome-mark",children:r.jsx(K,{name:"grid"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server pulse"}),r.jsx("strong",{children:"Here’s what needs your attention."})]})]}),r.jsxs("span",{className:"welcome-time",children:["LIVE SIGNALS ",r.jsx("span",{className:"status-dot"})]})]}),r.jsx(on,{eyebrow:"Overview",title:"A quick read on your room.",text:"The important signals, without making you hunt for them."}),r.jsxs("div",{className:"dash-stats guild-overview-stats",children:[r.jsx(Mt,{label:"Warnings logged",value:Le(o.moderation.warn_count),note:"For this server",accent:"accent-blue"}),r.jsx(Mt,{label:"Automod",value:o.moderation.automod_active?"Active":"Quiet",note:"Protection status",accent:"accent-green"}),r.jsx(Mt,{label:"Level leaders",value:Le(o.leveling.top.length),note:"Members with recorded XP",accent:"accent-violet"})]}),r.jsxs("div",{className:"dash-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Community energy"}),r.jsx("h3",{children:"Top XP"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(K,{name:"spark"})})]}),r.jsx(qu,{rows:o.leveling.top})]}),r.jsx("section",{className:"dash-panel",children:r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server controls"}),r.jsx("h3",{children:"Manage the room"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(K,{name:"settings"})}),r.jsx("p",{children:"Use Server settings for prefixes, welcome messages, logs, and ticket panels."})]})})]})]})}function Yh({rows:o,config:c,resources:l,csrfToken:d,guildId:m}){var f,v,M;return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Leveling",title:"Momentum people can see.",text:"Track the members turning up, and tune the pace to fit your server."}),r.jsxs("div",{className:"dash-stats",children:[r.jsx(Mt,{label:"Top level",value:String(((f=o[0])==null?void 0:f.level)||0),note:((v=o[0])==null?void 0:v.display_name)||((M=o[0])==null?void 0:M.username)||"No members yet",accent:"accent-violet"}),r.jsx(Mt,{label:"XP multiplier",value:`${(c==null?void 0:c.leveling.xp_multiplier)||1}×`,note:(c==null?void 0:c.leveling.xp_enabled)===!1?"XP disabled":"Currently active",accent:"accent-blue"}),r.jsx(Mt,{label:"Cooldown",value:`${(c==null?void 0:c.leveling.xp_cooldown)||0}s`,note:"Between XP awards",accent:"accent-green"})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Leaderboard"}),r.jsx("h3",{children:"XP leaders"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(K,{name:"spark"})})]}),r.jsx(qu,{rows:o})]}),r.jsx(tp,{guildId:m,config:c,resources:l,csrfToken:d})]})}const aa={saving:!1,message:"",error:""};function nt({label:o,hint:c,children:l}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:o}),l,c&&r.jsx("small",{children:c})]})}function Jh(o,c){const l=c?String(c):"",d=(o==null?void 0:o.channels)||[];return!l||d.some(m=>m.id===l)?d:[{id:l,name:`Saved channel · ${l}`},...d]}function ia({icon:o,label:c,title:l,text:d}){return r.jsxs("div",{className:"settings-intro",children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(K,{name:o})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:c}),r.jsx("strong",{children:l}),r.jsx("p",{children:d})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]})}function Sn({label:o,title:c,detail:l,icon:d}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:o}),r.jsx("h3",{children:c}),l&&r.jsx("p",{children:l})]}),d&&r.jsx("span",{className:"panel-icon",children:r.jsx(K,{name:d})})]})}function oa({state:o}){return r.jsxs("div",{className:"setting-footer",children:[o.error?r.jsx("span",{className:"form-error",role:"alert",children:o.error}):r.jsx("span",{role:"status",children:o.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:o.saving,children:o.saving?"Saving…":"Save changes"})]})}function Zh({guildId:o,config:c,csrfToken:l}){var C,P,I;const[d,m]=R.useState({}),[f,v]=R.useState(aa);R.useEffect(()=>{const D=(c==null?void 0:c.moderation)||{};m({automod:{...D.automod||{}},spam_threshold:D.spam_threshold??6,spam_interval:D.spam_interval??7,max_mentions:D.max_mentions??5,antinuke:{...D.antinuke||{}},antiraid:{...D.antiraid||{}},antiraid_ext:{...D.antiraid_ext||{}}})},[c]);const M=(D,B,b)=>m(Q=>({...Q,[D]:{...Q[D],[B]:b}})),w=D=>{D.preventDefault(),v({saving:!0,message:"",error:""}),ra(o,"automod",d,l).then(B=>{const b=B.config||{};m({automod:{...b.automod||{}},spam_threshold:b.spam_threshold??6,spam_interval:b.spam_interval??7,max_mentions:b.max_mentions??5,antinuke:{...b.antinuke||{}},antiraid:{...b.antiraid||{}},antiraid_ext:{...b.antiraid_ext||{}}}),v({saving:!1,message:"Moderation settings saved to Niko.",error:""})}).catch(B=>v({saving:!1,message:"",error:B instanceof Error?B.message:"Could not save settings."}))},z=[["antispam","Anti-spam","Detect repeated messages"],["antilink","Invite links","Remove Discord invite links"],["badwords","Blocked words","Filter words from the server list"],["massmention","Mass mentions","Limit mention floods"],["antinuke","Anti-nuke","Protect channels and roles"],["antiraid","Join raid protection","React to sudden join waves"],["antiraid_ext","External app protection","Detect user-installed app abuse"]],N=z.filter(([D])=>{var B;return!!((B=d.automod)!=null&&B[D])}).length;return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Moderation",title:"Keep the room feeling good.",text:"Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration."}),r.jsx(ia,{icon:"shield",label:"Protection desk",title:`${N} of ${z.length} safeguards active`,text:"Start with the essentials, then tune thresholds below when you know the room’s rhythm."}),r.jsxs("form",{onSubmit:w,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Protection rules",title:"AutoMod modules",detail:"Toggle only the responses you want Niko to handle.",icon:"shield"}),r.jsx("div",{className:"setting-list",children:z.map(([D,B,b])=>{var Q;return r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:B}),r.jsx("small",{children:b})]}),r.jsx("input",{type:"checkbox",checked:!!((Q=d.automod)!=null&&Q[D]),onChange:S=>M("automod",D,S.target.checked)}),r.jsx("i",{"aria-hidden":"true"})]},D)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Thresholds",title:"Choose when protection steps in",detail:"These limits apply across the server."}),r.jsxs("div",{className:"form-grid",children:[r.jsx(nt,{label:"Spam messages",hint:"Messages inside the spam interval",children:r.jsx("input",{type:"number",min:"1",max:"100",value:d.spam_threshold??6,onChange:D=>m({...d,spam_threshold:D.target.value})})}),r.jsx(nt,{label:"Spam interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:d.spam_interval??7,onChange:D=>m({...d,spam_interval:D.target.value})})}),r.jsx(nt,{label:"Maximum mentions",children:r.jsx("input",{type:"number",min:"1",max:"100",value:d.max_mentions??5,onChange:D=>m({...d,max_mentions:D.target.value})})}),r.jsx(nt,{label:"Anti-raid joins",hint:"Joins inside the join interval",children:r.jsx("input",{type:"number",min:"1",max:"1000",value:((C=d.antiraid)==null?void 0:C.join_threshold)??10,onChange:D=>M("antiraid","join_threshold",D.target.value)})}),r.jsx(nt,{label:"Anti-raid interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:((P=d.antiraid)==null?void 0:P.join_interval)??10,onChange:D=>M("antiraid","join_interval",D.target.value)})}),r.jsx(nt,{label:"Anti-raid action",children:r.jsxs("select",{value:((I=d.antiraid)==null?void 0:I.action)??"kick",onChange:D=>M("antiraid","action",D.target.value),children:[r.jsx("option",{value:"kick",children:"Kick"}),r.jsx("option",{value:"ban",children:"Ban"}),r.jsx("option",{value:"softban",children:"Soft-ban"}),r.jsx("option",{value:"slowmode",children:"Slowmode"}),r.jsx("option",{value:"lockdown",children:"Lockdown"})]})})]}),r.jsx(oa,{state:f})]})]})]})}function ep({guildId:o,config:c,csrfToken:l}){const[d,m]=R.useState({personality:"cafe",enabled:!0,ai_actions_experiment:!1,better_context_experiment:!1}),[f,v]=R.useState(aa);R.useEffect(()=>{const w=(c==null?void 0:c.ai)||{};m({personality:w.personality||"cafe",enabled:w.enabled!=="False"&&w.enabled!==!1,ai_actions_experiment:w.ai_actions_experiment===!0||w.ai_actions_experiment==="True",better_context_experiment:w.better_context_experiment===!0||w.better_context_experiment==="True"})},[c]);const M=w=>{w.preventDefault(),v({saving:!0,message:"",error:""}),ra(o,"ai",d,l).then(z=>{const N=z.config||{};m({personality:N.personality==="normal"?"normal":"cafe",enabled:N.enabled!=="False"&&N.enabled!==!1,ai_actions_experiment:N.ai_actions_experiment===!0||N.ai_actions_experiment==="True",better_context_experiment:N.better_context_experiment===!0||N.better_context_experiment==="True"}),v({saving:!1,message:"AI settings saved to Niko.",error:""})}).catch(z=>v({saving:!1,message:"",error:z instanceof Error?z.message:"Could not save settings."}))};return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"AI controls",title:"Give Niko the right tone.",text:"AI is optional, configurable per server, and designed to stay out of the way when the room does not need it."}),r.jsx(ia,{icon:"settings",label:"Conversation desk",title:d.enabled?"Niko is ready to respond":"Niko is staying quiet",text:"Choose a voice that fits your community. You can change this without affecting other servers."}),r.jsxs("form",{onSubmit:M,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Conversation",title:"Core settings",detail:"Decide when Niko joins the conversation.",icon:"settings"}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable AI chat"}),r.jsx("small",{children:"Respond when Niko is mentioned"})]}),r.jsx("input",{type:"checkbox",checked:d.enabled,onChange:w=>m({...d,enabled:w.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"personality-options",children:[r.jsxs("button",{type:"button",className:d.personality==="cafe"?"personality active":"personality",onClick:()=>m({...d,personality:"cafe"}),children:[r.jsx("span",{className:"personality-mark",children:"n"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Café"}),r.jsx("small",{children:"Warm, playful, familiar"})]})]}),r.jsxs("button",{type:"button",className:d.personality==="normal"?"personality active":"personality",onClick:()=>m({...d,personality:"normal"}),children:[r.jsx("span",{className:"personality-mark",children:"—"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Normal"}),r.jsx("small",{children:"Clear and straightforward"})]})]})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Experiments",title:"Optional context",detail:"Try new capabilities when your team is ready."}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Better context"}),r.jsx("small",{children:"Use the last five channel messages"})]}),r.jsx("input",{type:"checkbox",checked:d.better_context_experiment,onChange:w=>m({...d,better_context_experiment:w.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"AI actions"}),r.jsx("small",{children:"Allow confirmed actions requested in chat"})]}),r.jsx("input",{type:"checkbox",checked:d.ai_actions_experiment,onChange:w=>m({...d,ai_actions_experiment:w.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsx(oa,{state:f})]})]})]})}function tp({guildId:o,config:c,resources:l,csrfToken:d}){const m=(c==null?void 0:c.leveling)||{},[f,v]=R.useState({xp_enabled:!0,xp_multiplier:1,xp_cooldown:0,level_up_channel:"",level_up_message:""}),[M,w]=R.useState(aa);R.useEffect(()=>v({xp_enabled:m.xp_enabled!==!1,xp_multiplier:m.xp_multiplier??1,xp_cooldown:m.xp_cooldown??0,level_up_channel:m.level_up_channel?String(m.level_up_channel):"",level_up_message:m.level_up_message||""}),[c]);const z=C=>{C.preventDefault(),w({saving:!0,message:"",error:""}),ra(o,"leveling",f,d).then(P=>{const I=P.config||{};v({xp_enabled:I.xp_enabled!==!1,xp_multiplier:I.xp_multiplier??1,xp_cooldown:I.xp_cooldown??0,level_up_channel:I.level_up_channel?String(I.level_up_channel):"",level_up_message:I.level_up_message||""}),w({saving:!1,message:"Leveling settings saved to Niko.",error:""})}).catch(P=>w({saving:!1,message:"",error:P instanceof Error?P.message:"Could not save settings."}))},N=Jh(l,f.level_up_channel);return r.jsxs(r.Fragment,{children:[r.jsx(ia,{icon:"spark",label:"Participation desk",title:f.xp_enabled?"XP is flowing":"XP is paused",text:"Set a pace that rewards regulars without turning every message into a transaction."}),r.jsx("form",{onSubmit:z,className:"settings-stack",children:r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Leveling settings",title:"Shape the pace",detail:"These controls apply to every member in this server.",icon:"spark"}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable XP"}),r.jsx("small",{children:"Track activity and award levels"})]}),r.jsx("input",{type:"checkbox",checked:f.xp_enabled,onChange:C=>v({...f,xp_enabled:C.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"form-grid",children:[r.jsx(nt,{label:"XP multiplier",hint:"From 0.1× to 10×",children:r.jsx("input",{type:"number",min:"0.1",max:"10",step:"0.1",value:f.xp_multiplier,onChange:C=>v({...f,xp_multiplier:C.target.value})})}),r.jsx(nt,{label:"Cooldown (seconds)",hint:"0 disables the cooldown",children:r.jsx("input",{type:"number",min:"0",max:"86400",value:f.xp_cooldown,onChange:C=>v({...f,xp_cooldown:C.target.value})})}),r.jsx(nt,{label:"Level-up channel",children:r.jsxs("select",{value:f.level_up_channel,onChange:C=>v({...f,level_up_channel:C.target.value}),children:[r.jsx("option",{value:"",children:"Same channel"}),N.map(C=>r.jsxs("option",{value:C.id,children:["#",C.name]},C.id))]})}),r.jsx(nt,{label:"Level-up message",hint:"Use {mention}, {level}, {name}, or {guild}",children:r.jsx("textarea",{rows:3,maxLength:1e3,value:f.level_up_message,onChange:C=>v({...f,level_up_message:C.target.value}),placeholder:"Leave blank for Niko's default message"})})]}),r.jsx(oa,{state:M})]})})]})}function np({guildId:o,config:c,csrfToken:l}){var z;const d=((z=c==null?void 0:c.server)==null?void 0:z.profile)||{},[m,f]=R.useState({display_name:d.display_name||"",bio:d.bio||"",avatar_url:d.avatar_url||"",banner_url:d.banner_url||""}),[v,M]=R.useState(aa);R.useEffect(()=>{var C;const N=((C=c==null?void 0:c.server)==null?void 0:C.profile)||{};f({display_name:N.display_name||"",bio:N.bio||"",avatar_url:N.avatar_url||"",banner_url:N.banner_url||""})},[c]);const w=N=>{N.preventDefault(),M({saving:!0,message:"",error:""}),mh(o,{display_name:m.display_name||null,bio:m.bio||null,avatar_url:m.avatar_url||null,banner_url:m.banner_url||null},l).then(C=>{const P=C.profile||{};f({display_name:P.display_name||"",bio:P.bio||"",avatar_url:P.avatar_url||"",banner_url:P.banner_url||""}),M({saving:!1,message:"Bot profile updated.",error:""})}).catch(C=>M({saving:!1,message:"",error:C instanceof Error?C.message:"Could not save profile."}))};return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Customization",title:"Niko's server presence.",text:"Change how Niko appears in this server. Display name, avatar, banner, and bio are all per-server."}),r.jsx(ia,{icon:"paint",label:"Identity desk",title:"Server-specific identity",text:"Each server can have its own Niko persona. Changes apply only to this server."}),r.jsxs("form",{onSubmit:w,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Display name",title:"How Niko appears",detail:"Set the name members see for Niko in this server. Leave blank to use the default.",icon:"settings"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(nt,{label:"Display name",hint:"32 characters or fewer",children:r.jsx("input",{value:m.display_name,maxLength:32,onChange:N=>f({...m,display_name:N.target.value}),placeholder:"Niko"})}),r.jsx(nt,{label:"Bio",hint:"190 characters or fewer",children:r.jsx("input",{value:m.bio,maxLength:190,onChange:N=>f({...m,bio:N.target.value}),placeholder:"A warm Discord companion"})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Server avatar & banner",title:"Visual identity",detail:"Provide HTTPS image URLs. Images are uploaded to Discord when saved.",icon:"paint"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(nt,{label:"Avatar URL",hint:"Square image, 512×512 recommended",children:r.jsx("input",{type:"url",value:m.avatar_url,onChange:N=>f({...m,avatar_url:N.target.value}),placeholder:"https://cdn.example.com/avatar.png"})}),r.jsx(nt,{label:"Banner URL",hint:"Wide image, 960×540 recommended",children:r.jsx("input",{type:"url",value:m.banner_url,onChange:N=>f({...m,banner_url:N.target.value}),placeholder:"https://cdn.example.com/banner.png"})})]}),r.jsx("p",{className:"form-hint",children:"Images are fetched, validated, and uploaded to Discord. Maximum 8 MB each. Supported formats: PNG, JPG, GIF."})]}),r.jsx(oa,{state:v})]})]})}const rp={saving:!1,message:"",error:""};function tt({label:o,hint:c,children:l}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:o}),l,c&&r.jsx("small",{children:c})]})}function Xs({label:o,title:c,detail:l,icon:d}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:o}),r.jsx("h3",{children:c}),r.jsx("p",{children:l})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(K,{name:d})})]})}function sp({state:o}){return r.jsxs("div",{className:"setting-footer",children:[o.error?r.jsx("span",{className:"form-error",role:"alert",children:o.error}):r.jsx("span",{role:"status",children:o.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:o.saving,children:o.saving?"Saving...":"Save server settings"})]})}const ap=[["moderation","Moderation"],["automod","AutoMod"],["messages","Messages"],["channels","Channels"],["members","Members"],["captcha","Captcha"],["invites","Invites"],["roles","Roles"],["server","Server"],["voice","Voice"]];function ip(o,c){var l;return c?((l=o==null?void 0:o.channels.find(d=>d.id===String(c)))==null?void 0:l.name)||`Saved channel · ${c}`:"Not set"}function Ys(o,c){const l=c?String(c):"",d=(o==null?void 0:o.channels)||[];return!l||d.some(m=>m.id===l)?d:[{id:l,name:`Saved channel · ${l}`},...d]}function Fu(o,c=[]){const l=(o==null?void 0:o.roles)||[],d=new Set(l.map(f=>f.id));return[...c.map(String).filter((f,v,M)=>f&&!d.has(f)&&M.indexOf(f)===v).map(f=>({id:f,name:`Unavailable role (${f})`})),...l]}function uo(o){var d,m;const c=(o==null?void 0:o.onboarding)||{},l=(o==null?void 0:o.tickets)||{};return{prefixes:((d=o==null?void 0:o.prefixes)!=null&&d.length?o.prefixes:["."]).join(`
`),welcome_channel:c.welcome_channel?String(c.welcome_channel):"",welcome_title:c.welcome_title||"",welcome_description:c.welcome_description||"",welcome_color:c.welcome_color===null||c.welcome_color===void 0?"5865F2":c.welcome_color.toString(16).padStart(6,"0"),welcome_image:c.welcome_image||"",rules_channel:c.rules_channel?String(c.rules_channel):"",rules_text:c.rules_text||"",rules_role_id:c.rules_role_id?String(c.rules_role_id):"",logging:Object.fromEntries(Object.entries((o==null?void 0:o.logging)||{}).map(([f,v])=>[f,v==null?"":String(v)])),disabled_logging:[...((m=o==null?void 0:o.logging)==null?void 0:m.disabled)||[]].map(String),panel_title:l.panel_title||"",panel_description:l.panel_description||"",panel_categories:(l.panel_categories||[]).join(`
`),panel_channel_id:l.panel_channel_id?String(l.panel_channel_id):"",support_roles:[...l.support_roles||[]].map(String)}}function op({guildId:o,config:c,resources:l,csrfToken:d}){const[m,f]=R.useState(()=>uo(c==null?void 0:c.server)),[v,M]=R.useState(rp);R.useEffect(()=>{c!=null&&c.server&&f(uo(c.server))},[c]);const w=(S,q)=>f(ne=>({...ne,[S]:q})),z=(S,q)=>f(ne=>({...ne,logging:{...ne.logging,[S]:q}})),N=S=>f(q=>({...q,disabled_logging:q.disabled_logging.includes(S)?q.disabled_logging.filter(ne=>ne!==S):[...q.disabled_logging,S]})),C=S=>{S.preventDefault(),M({saving:!0,message:"",error:""});const q=m.prefixes.split(/\r?\n|,/).map(ie=>ie.trim()).filter(Boolean),ne=m.panel_categories.split(/\r?\n|,/).map(ie=>ie.trim()).filter(Boolean);ra(o,"server",{prefixes:q,onboarding:{welcome_channel:m.welcome_channel,welcome_title:m.welcome_title,welcome_description:m.welcome_description,welcome_color:m.welcome_color,welcome_image:m.welcome_image,rules_channel:m.rules_channel,rules_text:m.rules_text,rules_role_id:m.rules_role_id},logging:{...m.logging,disabled:m.disabled_logging},tickets:{panel_title:m.panel_title,panel_description:m.panel_description,panel_categories:ne,panel_channel_id:m.panel_channel_id,support_roles:m.support_roles}},d).then(ie=>{f(uo(ie.config)),M({saving:!1,message:"Server settings saved to Niko.",error:""})}).catch(ie=>M({saving:!1,message:"",error:ie instanceof Error?ie.message:"Could not save server settings."}))},P=m.welcome_channel,I=m.panel_channel_id,D=Ys(l,m.welcome_channel),B=Ys(l,m.rules_channel),b=Ys(l,m.panel_channel_id),Q=Fu(l,m.support_roles);return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Server settings",title:"Make Niko fit your room.",text:"Manage the settings that shape how Niko behaves in this server. Economy balances remain global to each user and are not configured here."}),r.jsxs("div",{className:"settings-intro",children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(K,{name:"settings"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server control room"}),r.jsxs("strong",{children:[m.prefixes.split(/\r?\n|,/).filter(Boolean).length||0," command prefixes configured"]}),r.jsx("p",{children:"Welcome flows, log destinations, and ticket panels all live here."})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]}),r.jsxs("form",{onSubmit:C,className:"settings-stack server-settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Xs,{label:"Commands",title:"Prefixes",detail:"Use one prefix per line. Niko will respond to all of them.",icon:"terminal"}),r.jsx(tt,{label:"Command prefixes",hint:"The default prefix is .",children:r.jsx("textarea",{rows:3,maxLength:200,value:m.prefixes,onChange:S=>w("prefixes",S.target.value),placeholder:".\\n!"})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Xs,{label:"Welcome flow",title:"Welcome and rules",detail:"Choose where new members see your welcome message and rules.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(tt,{label:"Welcome channel",children:r.jsxs("select",{value:P,onChange:S=>w("welcome_channel",S.target.value),children:[r.jsx("option",{value:"",children:"Disabled"}),D.map(S=>r.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),r.jsx(tt,{label:"Welcome title",children:r.jsx("input",{value:m.welcome_title,maxLength:200,onChange:S=>w("welcome_title",S.target.value),placeholder:"Welcome to the server"})}),r.jsx(tt,{label:"Welcome message",hint:"Supports {user} and {name}",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:m.welcome_description,onChange:S=>w("welcome_description",S.target.value),placeholder:"Welcome {user}!"})}),r.jsx(tt,{label:"Accent color",hint:"Hex color, for example 5865F2",children:r.jsx("input",{value:m.welcome_color,maxLength:7,onChange:S=>w("welcome_color",S.target.value),placeholder:"5865F2"})}),r.jsx(tt,{label:"Welcome image URL",children:r.jsx("input",{type:"url",value:m.welcome_image,onChange:S=>w("welcome_image",S.target.value),placeholder:"https://..."})}),r.jsx(tt,{label:"Rules channel",children:r.jsxs("select",{value:m.rules_channel,onChange:S=>w("rules_channel",S.target.value),children:[r.jsx("option",{value:"",children:"Not configured"}),B.map(S=>r.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),r.jsx(tt,{label:"Rules text",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:m.rules_text,onChange:S=>w("rules_text",S.target.value),placeholder:"Write the rules members should acknowledge."})}),r.jsx(tt,{label:"Role after rules acknowledgment",children:r.jsxs("select",{value:m.rules_role_id,onChange:S=>w("rules_role_id",S.target.value),children:[r.jsx("option",{value:"",children:"No role"}),Fu(l,m.rules_role_id?[m.rules_role_id]:[]).map(S=>r.jsxs("option",{value:S.id,children:["@",S.name]},S.id))]})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Xs,{label:"Audit trail",title:"Logging destinations",detail:"Pick a channel for each event type and disable categories you do not need.",icon:"book"}),r.jsx("div",{className:"server-logging-list",children:ap.map(([S,q])=>{const ne=Ys(l,m.logging[S]);return r.jsxs("div",{className:"server-logging-row",children:[r.jsxs("label",{className:"form-field",children:[r.jsxs("span",{className:"form-label",children:[q," logs"]}),r.jsxs("select",{value:String(m.logging[S]||""),onChange:ie=>z(S,ie.target.value),children:[r.jsx("option",{value:"",children:"Not set"}),ne.map(ie=>r.jsxs("option",{value:ie.id,children:["#",ie.name]},ie.id))]})]}),r.jsxs("label",{className:"setting-row compact-setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enabled"}),r.jsx("small",{children:ip(l,m.logging[S])})]}),r.jsx("input",{type:"checkbox",checked:!m.disabled_logging.includes(S),onChange:()=>N(S)}),r.jsx("i",{"aria-hidden":"true"})]})]},S)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Xs,{label:"Support desk",title:"Ticket panel",detail:"Configure the public panel and decide who can handle tickets.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(tt,{label:"Panel title",children:r.jsx("input",{value:m.panel_title,maxLength:200,onChange:S=>w("panel_title",S.target.value),placeholder:"Open a Ticket"})}),r.jsx(tt,{label:"Panel channel",children:r.jsxs("select",{value:I,onChange:S=>w("panel_channel_id",S.target.value),children:[r.jsx("option",{value:"",children:"Keep current panel channel"}),b.map(S=>r.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),r.jsx(tt,{label:"Panel description",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:m.panel_description,onChange:S=>w("panel_description",S.target.value),placeholder:"Tell members what the ticket panel is for."})}),r.jsx(tt,{label:"Ticket categories",hint:"One category per line",children:r.jsx("textarea",{rows:4,value:m.panel_categories,onChange:S=>w("panel_categories",S.target.value),placeholder:"General\\nSupport\\nReports"})}),r.jsx(tt,{label:"Support roles",hint:"Hold Ctrl/Cmd to select more than one",children:r.jsx("select",{multiple:!0,value:m.support_roles,onChange:S=>w("support_roles",Array.from(S.target.selectedOptions,q=>q.value)),children:Q.map(S=>r.jsxs("option",{value:S.id,children:["@",S.name]},S.id))})})]}),r.jsx("p",{className:"form-hint",children:"Saving panel settings updates the existing posted panel when Niko can find its saved message."})]}),r.jsx(sp,{state:v})]})]})}function lp({auth:o}){const c=sa();return r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"n"}),r.jsx("div",{className:"eyebrow",children:"Private workspace"}),r.jsxs("h1",{children:["Settle in, ",r.jsx("em",{children:"admin."})]}),r.jsx("p",{children:"Sign in with Discord to see your Niko profile and manage the servers you look after."}),o.oauth_available?r.jsxs("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard",children:[r.jsx(K,{name:"lock"})," Continue with Discord ",r.jsx(K,{name:"arrow"})]}):r.jsxs("div",{className:"notice warning",children:["Discord login is not configured yet. Add ",r.jsx("code",{children:"DISCORD_CLIENT_SECRET"})," to the environment and restart the bot."]}),!c&&r.jsx("p",{className:"form-hint",children:"The public bot configuration is still loading."}),r.jsx("a",{className:"back-link",href:"/",onClick:l=>{l.preventDefault(),oe("/")},children:"Return to public site"})]})})]})}function cp({section:o,guild:c,stats:l,csrfToken:d,refreshToken:m}){const[f,v]=R.useState(null),[M,w]=R.useState([]),[z,N]=R.useState(null),[C,P]=R.useState(null),[I,D]=R.useState(!0),[B,b]=R.useState("");return R.useEffect(()=>{D(!0),b(""),(o==="overview"?uh(c.id).then(v):o==="leveling"?Promise.all([dh(c.id),Cu(c.id),_u(c.id)]).then(([S,q,ne])=>{w(S),N(q),P(ne)}):Promise.all([Cu(c.id),_u(c.id)]).then(([S,q])=>{N(S),P(q)})).catch(S=>b(S instanceof Error?S.message:"This server could not be loaded.")).finally(()=>D(!1))},[c.id,o,m]),I?r.jsxs("div",{className:"section-loading section-skeleton",role:"status","aria-label":`Loading ${o}`,children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsxs("span",{children:["Loading ",o,"..."]})]}):B?r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Couldn’t load this page."}),r.jsx("span",{children:B}),r.jsx("button",{className:"button button-muted",onClick:()=>window.location.reload(),children:"Try again"})]}):o==="overview"&&f?r.jsx(Xh,{overview:f}):o==="leveling"?r.jsx(Yh,{guildId:c.id,rows:M,config:z,resources:C,csrfToken:d}):o==="moderation"?r.jsx(Zh,{guildId:c.id,config:z,csrfToken:d}):o==="server"?r.jsx(op,{guildId:c.id,config:z,resources:C,csrfToken:d}):o==="customization"?r.jsx(np,{guildId:c.id,config:z,csrfToken:d}):r.jsx(ep,{guildId:c.id,config:z,csrfToken:d})}function up(){return r.jsxs("div",{className:"section-loading section-skeleton dashboard-loading",role:"status",children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"Preparing your dashboard..."})]})}function dp(){sa();const[o,c]=R.useState(Mu),[l,d]=R.useState(null),[m,f]=R.useState(null),[v,M]=R.useState(null),[w,z]=R.useState([]),[N,C]=R.useState(null),[P,I]=R.useState(!0),[D,B]=R.useState(""),[b,Q]=R.useState(0),[S,q]=R.useState(!1);if(R.useEffect(()=>{const te=()=>c(Mu());return window.addEventListener("popstate",te),()=>window.removeEventListener("popstate",te)},[]),R.useEffect(()=>{I(!0),Promise.all([bu(),po()]).then(([te,we])=>(d(te),f(we),te.authenticated?Promise.all([Nu(),Su()]).then(([_e,Be])=>{M(_e),z(Be)}):null)).catch(te=>B(te instanceof Error?te.message:"Dashboard unavailable")).finally(()=>I(!1))},[]),R.useEffect(()=>{if(o.view!=="guild"){C(null);return}const te=w.find(we=>we.id===o.guildId&&we.installed!==!1);te?(C(te),localStorage.setItem("niko-guild",te.id)):o.guildId&&w.length&&oe(Eu())},[w,o.guildId,o.view]),P||!l)return r.jsxs("div",{className:"dashboard-state",children:[r.jsx("div",{className:"loading-ring"}),r.jsx("p",{children:"Connecting to Niko…"})]});if(D)return r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Connection issue"}),r.jsxs("h1",{children:["Couldn’t load",r.jsx("br",{}),r.jsx("em",{children:"your workspace."})]}),r.jsx("p",{children:D}),r.jsxs("button",{className:"button button-primary",onClick:()=>window.location.reload(),children:["Try again ",r.jsx(K,{name:"arrow"})]})]})})]});if(!l.authenticated)return r.jsx(lp,{auth:l});const ne=te=>{te.installed!==!1&&(localStorage.setItem("niko-guild",te.id),oe(Ir(te.id,o.section)))},ie=te=>{te.installed!==!1&&(localStorage.setItem("niko-guild",te.id),oe(Ir(te.id,"overview")))},F=te=>{oe(N?Ir(N.id,te):Ir())},J=()=>oe(Ir()),pe=()=>oe(Eu()),Se=async()=>{if(!S){q(!0);try{const[te,we]=await Promise.all([bu(),po()]);if(d(te),f(we),te.authenticated){const[_e,Be]=await Promise.all([Nu(),Su()]);M(_e),z(Be)}Q(_e=>_e+1),B("")}catch(te){B(te instanceof Error?te.message:"Dashboard refresh failed")}finally{q(!1)}}};let De;return o.view==="servers"?De=r.jsx(Qh,{guilds:w,onManage:ie}):o.view==="guild"?De=N?r.jsx(cp,{section:o.section,guild:N,stats:m,csrfToken:l.csrf_token,refreshToken:b},`${N.id}-${o.section}`):r.jsx(up,{}):De=r.jsx(qh,{user:l.user,overview:v,guilds:w,onServers:pe,onManage:ie}),r.jsx(Kh,{user:l.user,guilds:w,selectedGuild:N,view:o.view,section:o.section,stats:m,onHome:J,onServers:pe,onGuildChange:ne,onSectionChange:F,onRefresh:Se,refreshing:S,children:De})}function mp({value:o,onChange:c,placeholder:l="Search documentation...",onFocus:d,onBlur:m}){const[f,v]=R.useState(!1),M=R.useRef(null),[w,z]=R.useState(!1);R.useEffect(()=>{const D=B=>{var b;(B.metaKey||B.ctrlKey)&&B.key==="k"&&(B.preventDefault(),(b=M.current)==null||b.focus())};return document.addEventListener("keydown",D),()=>document.removeEventListener("keydown",D)},[]);const N=()=>{v(!0),z(!0),d==null||d()},C=()=>{v(!1),setTimeout(()=>z(!1),200),m==null||m()},P=D=>{c(D.target.value)},I=D=>{var B;D.key==="Escape"&&((B=M.current)==null||B.blur())};return r.jsxs("div",{className:`doc-search-bar ${w?"expanded":""}`,children:[r.jsxs("div",{className:"search-input-wrapper",children:[r.jsx(K,{name:"search",className:"search-icon"}),r.jsx("input",{ref:M,type:"text",value:o,onChange:P,onFocus:N,onBlur:C,onKeyDown:I,placeholder:l,className:"search-input","aria-label":"Search documentation"}),r.jsxs("kbd",{className:"search-shortcut",children:[r.jsx("span",{className:"shortcut-key",children:"⌘"}),"K"]})]}),r.jsxs("div",{className:"search-hint",children:["Press ",r.jsx("kbd",{children:"⌘K"})," to focus search"]})]})}function hp({selectedCategory:o,onSelectCategory:c,sections:l,allCategoriesLabel:d="All Categories"}){return r.jsx("div",{className:"doc-filters",children:r.jsxs("div",{className:"filter-tabs",role:"tablist","aria-label":"Filter by category",children:[r.jsx("button",{role:"tab","aria-selected":o==="",className:`filter-tab ${o===""?"active":""}`,onClick:()=>c(""),children:d}),l.map(m=>r.jsxs("button",{role:"tab","aria-selected":o===m.id,className:`filter-tab ${o===m.id?"active":""}`,onClick:()=>c(m.id),children:[r.jsx(K,{name:m.icon,size:14}),r.jsx("span",{children:m.label})]},m.id))]})})}function mo({doc:o,variant:c="default"}){const l="page"in o?o.page:o,[d,m]=R.useState(!1),f=w=>{w.preventDefault(),oe(`/docs/${l.slug}`)},v=w=>{(w.key==="Enter"||w.key===" ")&&(w.preventDefault(),oe(`/docs/${l.slug}`))};if(c==="compact")return r.jsx("a",{href:`/docs/${l.slug}`,onClick:f,onKeyDown:v,className:"doc-card-compact",tabIndex:0,role:"button",children:r.jsxs("div",{className:"compact-content",children:[r.jsx("span",{className:"compact-title",children:l.title}),r.jsx("span",{className:"compact-excerpt",children:l.excerpt})]})});const M="highlights"in o?o.highlights:[];return r.jsx("article",{className:`doc-card ${c==="highlighted"?"highlighted":""}`,children:r.jsxs("div",{className:`doc-card-content ${d?"loaded":""}`,children:[r.jsxs("div",{className:"doc-card-header",children:[r.jsx("span",{className:"doc-category",children:l.category.replace(/-/g," ")}),r.jsxs("span",{className:"doc-order",children:["#",l.order]})]}),r.jsx("h3",{className:"doc-title",children:l.title}),r.jsx("p",{className:"doc-excerpt",children:l.excerpt}),M.length>0&&r.jsx("div",{className:"doc-highlights",children:M.slice(0,2).map((w,z)=>r.jsxs("p",{className:"highlight-snippet",children:[w.slice(0,150),w.length>150?"...":""]},z))}),r.jsxs("div",{className:"doc-card-footer",children:[r.jsx("div",{className:"doc-tags",children:l.tags.slice(0,3).map(w=>r.jsxs("span",{className:"doc-tag",children:["#",w]},w))}),r.jsxs("a",{href:`/docs/${l.slug}`,onClick:f,onKeyDown:v,className:"doc-read-more",children:["Read more ",r.jsx(K,{name:"arrow",size:14})]})]})]})})}const Pe=[{slug:"welcome",title:"Welcome to Niko",category:"getting-started",excerpt:"New to Niko? Start here to understand what the bot can do for your server.",tags:["introduction","overview","beginner"],order:1,content:`
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
Some items are automatic, others need to be activated:
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
    `}];function pp(o){return Pe.find(c=>c.slug===o)}const an=[{id:"getting-started",label:"Getting Started",description:"New to Niko? Start here.",icon:"icon_home",count:Pe.filter(o=>o.category==="getting-started").length},{id:"setup",label:"Setup",description:"Configure Niko for your server.",icon:"icon_settings",count:Pe.filter(o=>o.category==="setup").length},{id:"economy",label:"Economy",description:"Money, jobs, banking, and more.",icon:"icon_economy",count:Pe.filter(o=>o.category==="economy").length},{id:"leveling",label:"Leveling",description:"XP, levels, and rankings.",icon:"icon_leveling",count:Pe.filter(o=>o.category==="leveling").length},{id:"moderation",label:"Moderation",description:"Moderation tools and commands.",icon:"icon_moderation",count:Pe.filter(o=>o.category==="moderation").length},{id:"automod",label:"AutoMod",description:"Automated moderation features.",icon:"icon_automod",count:Pe.filter(o=>o.category==="automod").length},{id:"logging",label:"Logging",description:"Server event logging.",icon:"icon_settings",count:Pe.filter(o=>o.category==="logging").length},{id:"social",label:"Social",description:"Community engagement features.",icon:"icon_heart",count:Pe.filter(o=>o.category==="social").length},{id:"utility",label:"Utility",description:"Helpful tools and utilities.",icon:"icon_utility",count:Pe.filter(o=>o.category==="utility").length},{id:"voice",label:"Voice",description:"Voice and music features.",icon:"icon_bot",count:Pe.filter(o=>o.category==="voice").length},{id:"ai",label:"AI",description:"AI-powered features.",icon:"icon_ai",count:Pe.filter(o=>o.category==="ai").length},{id:"dashboard",label:"Dashboard",description:"Web dashboard guides.",icon:"icon_settings",count:Pe.filter(o=>o.category==="dashboard").length},{id:"tips",label:"Tips",description:"Tips and best practices.",icon:"icon_lightbulb",count:Pe.filter(o=>o.category==="tips").length}];function Qu(){const[o,c]=R.useState({query:"",category:"",tags:[]}),l=R.useCallback(w=>{c(z=>({...z,query:w.toLowerCase(),tags:[]}))},[]),d=R.useCallback(w=>{c(z=>({...z,category:w,tags:[]}))},[]),m=R.useCallback(w=>{c(z=>{const N=z.tags.includes(w)?z.tags.filter(C=>C!==w):[...z.tags,w];return{...z,tags:N,query:""}})},[]),f=R.useCallback(()=>{c({query:"",category:"",tags:[]})},[]),v=R.useMemo(()=>{const{query:w,category:z,tags:N}=o;if(!w&&!z&&N.length===0)return Pe.map(P=>({page:P,score:1,highlights:[]}));const C=[];for(const P of Pe)if(!(z&&P.category!==z)&&!(N.length>0&&!N.some(I=>P.tags.includes(I))))if(w){const I=fp(P,w);if(I===0)continue;const D=gp(P,w);C.push({page:P,score:I,highlights:D})}else C.push({page:P,score:1,highlights:[]});return C.sort((P,I)=>I.score!==P.score?I.score-P.score:P.page.order-I.page.order),C},[o]),M=o.query!==""||o.category!==""||o.tags.length>0;return{filters:o,setQuery:l,setCategory:d,toggleTag:m,clearFilters:f,results:v,hasActiveFilters:M,resultCount:v.length}}function fp(o,c){let l=0;const d=c.toLowerCase();o.title.toLowerCase()===d?l+=100:o.title.toLowerCase().includes(d)&&(l+=50),o.excerpt.toLowerCase().includes(d)&&(l+=25),o.content.toLowerCase().includes(d)&&(l+=10);for(const m of o.tags)m.toLowerCase().includes(d)&&(l+=15);return o.category.toLowerCase().includes(d)&&(l+=5),l}function gp(o,c){const l=[],d=c.toLowerCase(),m=3;if(o.title.toLowerCase().includes(d)&&(l.push(o.title),l.length>=m)||o.excerpt.toLowerCase().includes(d)&&(l.push(o.excerpt),l.length>=m))return l;const f=o.content.split(`
`).filter(v=>v.trim());for(const v of f)if(v.toLowerCase().includes(d)){const M=v.replace(/#{1,6}\s?/g,"").trim();if(M.length>10&&(l.push(M),l.length>=m))break}return l}function vp(){return R.useMemo(()=>{const c={};return Pe.forEach(l=>{l.tags.forEach(d=>{c[d]=(c[d]||0)+1})}),Object.entries(c).map(([l,d])=>({tag:l,count:d})).sort((l,d)=>d.count-l.count)},[])}function yp({slug:o}){var w,z;const{setCategory:c,clearFilters:l}=Qu();R.useEffect(()=>{window.location.hash!==`#/docs/${o}`&&window.history.replaceState(null,"",`#/docs/${o}`)},[o]);const d=pp(o);if(!d)return r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:"docs"}),r.jsx("main",{className:"shell page-main docs-page",children:r.jsxs("div",{className:"docs-not-found",children:[r.jsx(K,{name:"doc",size:48,className:"not-found-icon"}),r.jsx("h1",{children:"Page Not Found"}),r.jsxs("p",{children:[`We couldn't find documentation for "`,o,'".']}),r.jsxs("div",{className:"not-found-actions",children:[r.jsx("button",{onClick:()=>oe("/docs"),children:"Browse all documentation"}),r.jsx("button",{onClick:()=>{oe("/docs"),l()},children:"Clear filters"})]})]})}),r.jsx(Bt,{})]});const m=N=>{const C=[],P=/(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*)/g;let I=0,D,B=0;for(;(D=P.exec(N))!==null;){D.index>I&&C.push(N.slice(I,D.index));const b=D[0];if(b.startsWith("`")&&b.endsWith("`")&&b.length>2)C.push(r.jsx("code",{className:"doc-inline-code",children:b.slice(1,-1)},B++));else if(b.startsWith("[")){const Q=b.match(/^\[([^\]]+)\]\(([^)]+)\)$/);Q?C.push(r.jsx("a",{href:Q[2],target:"_blank",rel:"noreferrer",children:m(Q[1])},B++)):C.push(b)}else b.startsWith("**")?C.push(r.jsx("strong",{children:m(b.slice(2,-2))},B++)):b.startsWith("*")?C.push(r.jsx("em",{children:m(b.slice(1,-1))},B++)):C.push(b);I=D.index+b.length}return I<N.length&&C.push(N.slice(I)),C},v=(N=>{const C=N.split(`
`),P=[];let I=0,D=null,B=[];const b=()=>{if(B.length===0)return;const S=D==="ol"?"ol":"ul";P.push(r.jsx(S,{className:`doc-content-list ${D==="ol"?"doc-content-list-ol":""}`,children:B.map((q,ne)=>r.jsx("li",{children:m(q)},ne))},`list-${P.length}`)),B=[],D=null},Q=()=>{var ne;const S=P[P.length-1];R.isValidElement(S)&&((ne=S.props)==null?void 0:ne.className)==="doc-content-spacer"||P.push(r.jsx("div",{className:"doc-content-spacer"},`spacer-${P.length}`))};for(;I<C.length;){const q=C[I].trim();if(!q){b(),Q(),I+=1;continue}if(q.startsWith("```")){b();const F=[];let J=I+1;for(;J<C.length&&C[J].trim()!=="```";)F.push(C[J]),J+=1;P.push(r.jsx("pre",{className:"doc-code-block",children:r.jsx("code",{children:F.join(`
`)})},`code-${I}`)),I=J+1;continue}if(q.startsWith("|")){b();const F=[];let J=I;for(;J<C.length&&C[J].trim().startsWith("|");){const te=C[J].trim().replace(/^\|/,"").replace(/\|$/,"").split("|").map(we=>we.trim());F.push(te),J+=1}const pe=F.length>1&&F[1].every(te=>/^:?-{2,}:?$/.test(te.replace(/\s+/g,""))),Se=F[0],De=pe?F.slice(2):F.slice(1);Se.length>1&&P.push(r.jsxs("table",{className:"doc-table",children:[r.jsx("thead",{children:r.jsx("tr",{children:Se.map((te,we)=>r.jsx("th",{children:m(te)},we))})}),r.jsx("tbody",{children:De.map((te,we)=>r.jsx("tr",{children:te.map((_e,Be)=>r.jsx("td",{children:m(_e)},Be))},we))})]},`table-${I}`)),I=J;continue}if(q.startsWith("### ")){b(),P.push(r.jsx("h4",{className:"doc-heading doc-heading-h4",children:q.slice(4)},`h-${I}`)),I+=1;continue}if(q.startsWith("## ")){b(),P.push(r.jsx("h3",{className:"doc-heading doc-heading-h3",children:q.slice(3)},`h-${I}`)),I+=1;continue}if(q.startsWith("# ")){b(),P.push(r.jsx("h2",{className:"doc-heading doc-heading-h2",children:q.slice(2)},`h-${I}`)),I+=1;continue}if(q.startsWith("> ")){b(),P.push(r.jsx("blockquote",{className:"doc-blockquote",children:m(q.slice(2))},`q-${I}`)),I+=1;continue}const ne=q.match(/^[-*]\s+(.*)$/);if(ne){D!=="ul"&&b(),D="ul",B.push(ne[1]),I+=1;continue}const ie=q.match(/^\d+\.\s+(.*)$/);if(ie){D!=="ol"&&b(),D="ol",B.push(ie[1]),I+=1;continue}b(),P.push(r.jsx("p",{className:"doc-paragraph",children:m(q)},`p-${I}`)),I+=1}return b(),P})(d.content),M=v.filter(N=>R.isValidElement(N)&&(N.type==="h2"||N.type==="h3"));return r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page docs-detail-page",children:[r.jsx("div",{className:"docs-detail-back",children:r.jsxs("button",{onClick:()=>oe("/docs"),className:"back-button",children:[r.jsx(K,{name:"arrow",size:16}),"Back to Documentation"]})}),r.jsxs("header",{className:"doc-article-header",children:[r.jsxs("div",{className:"doc-article-meta",children:[r.jsx("span",{className:"doc-category-badge",children:((w=an.find(N=>N.id===d.category))==null?void 0:w.label)||d.category}),r.jsxs("span",{className:"doc-order-badge",children:["Article #",d.order]})]}),r.jsx("h1",{className:"doc-article-title",children:d.title}),r.jsx("p",{className:"doc-article-excerpt",children:d.excerpt}),r.jsx("div",{className:"doc-article-tags",children:d.tags.map(N=>r.jsxs("span",{className:"doc-tag-pill",children:["#",N]},N))})]}),r.jsx("article",{className:"doc-article-content",children:v}),r.jsx("footer",{className:"doc-article-footer",children:r.jsx("div",{className:"doc-nav-container",children:r.jsxs("div",{className:"doc-nav-col",children:[r.jsx("span",{className:"doc-nav-label",children:"Category"}),r.jsxs("button",{className:"doc-nav-link",onClick:()=>{c(d.category),oe("/docs")},children:[r.jsx(K,{name:"arrow",size:14}),"View all ",(z=an.find(N=>N.id===d.category))==null?void 0:z.label]})]})})}),M.length>0&&r.jsxs("aside",{className:"doc-toc",children:[r.jsxs("div",{className:"toc-title",children:[r.jsx(K,{name:"utility",size:16}),r.jsx("span",{children:"On this page"})]}),r.jsx("nav",{className:"toc-nav",children:M.map((N,C)=>{var I;const P=(I=N.props.className)==null?void 0:I.includes("doc-heading-h2");return r.jsx("a",{href:`#${P?"h2-":"h3-"}-${C}`,className:`toc-link ${P?"toc-h2":"toc-h3"}`,children:N.props.children},C)})})]})]}),r.jsx(Bt,{})]})}function xp(){var ne,ie;const[o,c]=R.useState(!1),[l,d]=R.useState(""),[m,f]=R.useState(!1),{filters:v,setQuery:M,setCategory:w,toggleTag:z,clearFilters:N,results:C,hasActiveFilters:P,resultCount:I}=Qu(),D=vp();R.useEffect(()=>{const F=()=>{const J=window.location.hash.slice(1);if(J.startsWith("#/docs/")){const pe=J.replace("#/docs/",""),Se=Pe.find(De=>De.slug===pe);Se&&(d(Se.category),w(Se.category))}};return F(),window.addEventListener("hashchange",F),()=>window.removeEventListener("hashchange",F)},[]);const B=()=>{f(!0)},b=F=>{d(F),w(F),c(!1)},Q=()=>{v.query||f(!1)},S=F=>{oe(`/docs/${F}`),M(""),f(!1)},q=R.useMemo(()=>{const F={};return C.forEach(J=>{const pe=J.page.category;F[pe]||(F[pe]=[]),F[pe].push(J)}),F},[C]);return r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page",children:[r.jsx("div",{className:"docs-hero",children:r.jsxs("div",{className:"docs-hero-content",children:[r.jsx("div",{className:"eyebrow docs-eyebrow",children:"Documentation Center"}),r.jsxs("h1",{className:"docs-title",children:["Everything you need to know about",r.jsx("br",{}),r.jsx("span",{className:"title-accent",children:"using Niko"})]}),r.jsx("p",{className:"docs-subtitle",children:"Comprehensive guides, command references, and tips to help you get the most out of your server bot."})]})}),r.jsx("div",{className:`docs-search-section ${m?"active":""}`,children:r.jsxs("div",{className:"docs-search-container",children:[r.jsx(mp,{value:v.query,onChange:M,placeholder:"Search documentation, commands, guides...",onFocus:B,onBlur:Q}),m&&v.query&&C.length>0&&r.jsxs("div",{className:"search-results-dropdown",children:[r.jsxs("div",{className:"search-results-header",children:[r.jsxs("span",{className:"results-count",children:[I," ",I===1?"result":"results"]}),r.jsx("button",{className:"clear-search-btn",onClick:()=>{M(""),N(),d("")},children:"Clear"})]}),r.jsx("div",{className:"search-results-list",children:C.slice(0,8).map((F,J)=>r.jsxs("button",{className:"search-result-item",onClick:()=>S(F.page.slug),onMouseEnter:()=>{},children:[r.jsx("div",{className:"result-icon",children:r.jsx(K,{name:"doc",size:18})}),r.jsxs("div",{className:"result-content",children:[r.jsx("div",{className:"result-title",children:F.page.title}),r.jsx("div",{className:"result-excerpt",children:F.page.excerpt}),F.highlights.length>0&&r.jsxs("div",{className:"result-highlight",children:[F.highlights[0].slice(0,100),"..."]})]}),r.jsx(K,{name:"arrow",size:14,className:"result-arrow"})]},F.page.slug))}),C.length>8&&r.jsx("div",{className:"search-results-footer",children:r.jsxs("span",{children:["Showing 8 of ",C.length," results. Browse all docs below."]})})]})]})}),r.jsxs("div",{className:"docs-mobile-nav",children:[r.jsx("button",{className:"mobile-menu-toggle",onClick:()=>c(!o),"aria-label":"Toggle documentation menu",children:r.jsx(K,{name:"utility",size:20})}),o&&r.jsxs("div",{className:"mobile-nav-panel",children:[r.jsxs("div",{className:"mobile-nav-header",children:[r.jsx("h3",{children:"Documentation"}),r.jsx("button",{className:"close-menu-btn",onClick:()=>c(!1),"aria-label":"Close menu",children:r.jsx(K,{name:"utility",size:16,className:"rotated"})})]}),r.jsx("div",{className:"mobile-nav-sections",children:an.map(F=>r.jsxs("button",{className:`mobile-nav-item ${l===F.id?"active":""}`,onClick:()=>{b(F.id)},children:[r.jsx(K,{name:F.icon,size:18}),r.jsx("span",{className:"mobile-section-label",children:F.label}),r.jsx("span",{className:"mobile-section-count",children:F.count})]},F.id))})]})]}),D.length>0&&!P&&r.jsxs("div",{className:"docs-tags-cloud",children:[r.jsxs("div",{className:"tags-cloud-title",children:[r.jsx(K,{name:"utility",size:16}),r.jsx("span",{children:"Popular Topics"})]}),r.jsx("div",{className:"tags-cloud-list",children:D.slice(0,15).map(({tag:F,count:J})=>r.jsxs("button",{className:"tag-cloud-item",onClick:()=>z(F),style:{fontSize:`${.75+Math.min(J/4,1)}rem`},children:["#",F,r.jsx("span",{className:"tag-count",children:J})]},F))})]}),r.jsx("div",{className:"docs-category-filters",children:r.jsx(hp,{selectedCategory:v.category,onSelectCategory:b,sections:an})}),P&&r.jsxs("div",{className:"docs-results-header",children:[r.jsxs("div",{className:"results-info",children:[r.jsxs("span",{className:"results-count-large",children:[I," ",I===1?"article":"articles"]}),v.query&&r.jsxs("span",{className:"search-query-display",children:['for "',r.jsx("strong",{children:v.query}),'"']})]}),r.jsxs("button",{className:"clear-all-btn",onClick:()=>{N(),d("")},disabled:!P,children:[r.jsx(K,{name:"utility",size:14}),"Clear all filters"]})]}),r.jsx("div",{className:"docs-content",children:P?r.jsx("div",{className:"search-results-view",children:Object.entries(q).map(([F,J])=>{var pe;return r.jsxs("section",{className:"results-category",children:[r.jsx("h2",{className:"category-title",children:((pe=an.find(Se=>Se.id===F))==null?void 0:pe.label)||F}),r.jsx("div",{className:"category-results-grid",children:J.map(Se=>r.jsx(mo,{doc:Se,variant:"highlighted"},Se.page.slug))})]},F)})}):l?r.jsxs("div",{className:"category-view",children:[r.jsxs("div",{className:"category-header",children:[r.jsx("h2",{className:"category-page-title",children:((ne=an.find(F=>F.id===l))==null?void 0:ne.label)||l}),r.jsx("p",{className:"category-description",children:(ie=an.find(F=>F.id===l))==null?void 0:ie.description})]}),r.jsx("div",{className:"category-articles",children:Pe.filter(F=>F.category===l).sort((F,J)=>F.order-J.order).map(F=>r.jsx(mo,{doc:F},F.slug))})]}):r.jsx("div",{className:"all-categories-view",children:an.map(F=>r.jsxs("section",{className:"docs-section",id:`section-${F.id}`,children:[r.jsxs("div",{className:"section-header",children:[r.jsx("div",{className:"section-icon",children:r.jsx(K,{name:F.icon,size:28})}),r.jsxs("div",{className:"section-info",children:[r.jsx("h2",{className:"section-title",children:F.label}),r.jsx("p",{className:"section-description",children:F.description})]}),r.jsx("span",{className:"section-count",children:F.count})]}),r.jsx("div",{className:"section-articles",children:Pe.filter(J=>J.category===F.id).sort((J,pe)=>J.order-pe.order).map(J=>r.jsx(mo,{doc:J},J.slug))})]},F.id))})}),r.jsxs("div",{className:"docs-footer-note",children:[r.jsx(K,{name:"book",size:20}),r.jsxs("div",{children:[r.jsx("strong",{children:"Want more detail?"}),r.jsxs("p",{children:["The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in the"," ",r.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"docs/"})," ","folder."]})]})]})]}),r.jsx(Bt,{})]})}function kp(){const o=sa(),[c,l]=R.useState(null);R.useEffect(()=>{po().then(l).catch(()=>{})},[]);const d=[["spark","AI that remembers","Thoughtful conversation with a cozy personality and controls that respect your community."],["chart","A living economy","Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],["shield","Confident moderation","Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],["users","Community rituals","Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."]];return r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:"home"}),r.jsxs("main",{children:[r.jsxs("section",{className:"hero shell",children:[r.jsxs("div",{className:"hero-copy",children:[r.jsxs("div",{className:"eyebrow",children:[r.jsx("span",{className:"status-dot"})," Discord companion · online"]}),r.jsxs("div",{className:"hero-identity",children:[r.jsx("span",{className:"hero-avatar",children:o!=null&&o.bot_avatar_url?r.jsx("img",{src:o.bot_avatar_url,alt:"Niko"}):"n"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Niko"}),r.jsx("small",{children:"Your server’s calm, capable co-pilot"})]})]}),r.jsxs("h1",{children:["Useful tools for a ",r.jsx("em",{children:"better server."})]}),r.jsx("p",{children:"Niko handles the everyday work of running a Discord community, so your moderators can focus on the people in it."}),r.jsxs("div",{className:"hero-buttons",children:[r.jsxs("a",{className:"button button-primary",href:(o==null?void 0:o.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Invite Niko ",r.jsx(K,{name:"arrow"})]}),r.jsx("a",{className:"button button-muted",href:"/commands",onClick:m=>{m.preventDefault(),oe("/commands")},children:"Explore commands"})]}),r.jsxs("div",{className:"stats-strip",children:[r.jsxs("div",{children:[r.jsx("strong",{children:Le(c==null?void 0:c.guild_count)}),r.jsx("span",{children:"servers"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:Le(c==null?void 0:c.user_count)}),r.jsx("span",{children:"members"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:Le(c==null?void 0:c.command_count)}),r.jsx("span",{children:"commands"})]})]})]}),r.jsx("div",{className:"hero-art","aria-label":"A preview of Niko's server workspace",children:r.jsxs("div",{className:"workspace-preview",children:[r.jsxs("div",{className:"workspace-preview-top",children:[r.jsxs("span",{className:"preview-dots",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"server workspace"}),r.jsxs("span",{className:"preview-status",children:[r.jsx("span",{className:"status-dot"})," live"]})]}),r.jsxs("div",{className:"preview-body",children:[r.jsxs("div",{className:"preview-sidebar",children:[r.jsx("span",{className:"preview-label",children:"NIKO"}),r.jsx("b",{children:"Overview"}),r.jsx("span",{children:"Economy"}),r.jsx("span",{children:"Leveling"}),r.jsx("span",{children:"Moderation"}),r.jsx("span",{children:"AI controls"})]}),r.jsxs("div",{className:"preview-main",children:[r.jsx("span",{className:"preview-label",children:"SERVER SNAPSHOT"}),r.jsx("strong",{children:"Everything in one place."}),r.jsxs("div",{className:"preview-stats",children:[r.jsxs("span",{children:[r.jsx("b",{children:Le(c==null?void 0:c.user_count)}),r.jsx("small",{children:"members"})]}),r.jsxs("span",{children:[r.jsx("b",{children:Le(c==null?void 0:c.command_count)}),r.jsx("small",{children:"commands"})]})]}),r.jsxs("div",{className:"preview-line",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]})]})]})]})})]}),r.jsxs("section",{className:"shell intro-section",children:[r.jsx("div",{className:"section-kicker",children:"Why Niko"}),r.jsxs("div",{className:"intro-grid",children:[r.jsxs("h2",{children:["The good kind of",r.jsx("br",{}),r.jsx("em",{children:"always-on."})]}),r.jsx("p",{children:"Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile."})]})]}),r.jsx("section",{className:"shell feature-grid",children:d.map(([m,f,v])=>r.jsxs("article",{className:"feature-card",children:[r.jsx("span",{className:"feature-icon",children:r.jsx(K,{name:m})}),r.jsx("h3",{children:f}),r.jsx("p",{children:v}),r.jsxs("a",{href:"/docs",onClick:M=>{M.preventDefault(),oe("/docs")},children:["Learn more ",r.jsx(K,{name:"arrow"})]})]},f))}),r.jsxs("section",{className:"shell callout",children:[r.jsxs("div",{children:[r.jsx("div",{className:"section-kicker",children:"Ready when you are"}),r.jsxs("h2",{children:["A calmer, cleverer home",r.jsx("br",{}),"for your community."]})]}),r.jsxs("a",{className:"button button-primary",href:(o==null?void 0:o.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Bring Niko in ",r.jsx(K,{name:"arrow"})]})]})]}),r.jsx(Bt,{})]})}const wp=[{code:"USDT",label:"Tether"},{code:"ETH",label:"Ethereum"},{code:"BTC",label:"Bitcoin"},{code:"BNB",label:"BNB"},{code:"LTC",label:"Litecoin"},{code:"DOGE",label:"Dogecoin"},{code:"TRX",label:"TRON"},{code:"XMR",label:"Monero"}];function jp(){const c=new URLSearchParams(window.location.search).get("token")||"",[l,d]=R.useState("5"),[m,f]=R.useState("USDT"),[v,M]=R.useState(!1),[w,z]=R.useState(""),[N,C]=R.useState(null),[P,I]=R.useState(null),[D,B]=R.useState(!1);R.useEffect(()=>{c||B(!0)},[c]),R.useEffect(()=>{if(!(N!=null&&N.status_url)||N.paid)return;const Q=setInterval(async()=>{try{const S=await st(N.status_url);I(S),S.paid&&clearInterval(Q)}catch{}},5e3);return()=>clearInterval(Q)},[N]);const b=async Q=>{Q.preventDefault(),M(!0),z("");try{const S=await st("/api/donations/invoice",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:c,amount:parseFloat(l),currency:m})});C(S),S.error&&(z(S.error),C(null))}catch(S){z(S instanceof Error?S.message:"Could not create invoice.")}finally{M(!1)}};return D?r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Invalid donation link"}),r.jsxs("h1",{children:["This link is ",r.jsx("em",{children:"invalid."})]}),r.jsxs("p",{children:["The donation link is missing or has expired. Use the"," ",r.jsx("code",{children:"/donate"})," command in Discord to generate a new one."]}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>oe("/"),children:"Return home"})]})})]}):P!=null&&P.paid?r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"✓"}),r.jsx("div",{className:"eyebrow",children:"Payment confirmed"}),r.jsxs("h1",{children:["Thank you ",r.jsx("em",{children:"for supporting!"})]}),r.jsx("p",{children:"Your donation has been confirmed. You will receive the Supporter badge shortly."}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>oe("/"),children:"Return home"})]})})]}):r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:"home"}),r.jsx("main",{className:"page-main",children:r.jsx("div",{className:"shell",children:r.jsxs("div",{className:"page-heading",style:{maxWidth:500,margin:"0 auto"},children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:15},children:"Support Niko"}),r.jsxs("h1",{children:["Keep Niko ",r.jsx("em",{children:"running."})]}),r.jsx("p",{style:{color:"var(--muted)",marginBottom:30},children:"Your donation helps cover hosting costs and keeps Niko running for all servers. Choose an amount and cryptocurrency below."}),N!=null&&N.pay_link?r.jsxs("div",{className:"dash-panel",style:{marginBottom:24},children:[r.jsx("div",{className:"panel-heading",children:r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Invoice created"}),r.jsx("h3",{children:"Complete your payment"})]})}),r.jsxs("p",{style:{color:"var(--muted)",fontSize:12,marginBottom:16},children:["Amount: ",r.jsxs("strong",{children:["$",parseFloat(l).toFixed(2)," USD"]})," in"," ",r.jsx("strong",{children:m})]}),r.jsxs("p",{style:{color:"var(--dim)",fontSize:10,marginBottom:16},children:["Track ID: ",r.jsx("code",{children:N.track_id})," · Expires in 60 minutes"]}),r.jsxs("a",{className:"button button-primary",href:N.pay_link,target:"_blank",rel:"noopener noreferrer",children:["Pay now ",r.jsx(K,{name:"arrow"})]}),r.jsx("p",{style:{color:"var(--dim)",fontSize:10,marginTop:12},children:"Payment will be confirmed automatically once the transaction is processed on-chain."})]}):r.jsxs("form",{onSubmit:b,className:"dash-panel",style:{marginBottom:24},children:[r.jsxs("div",{className:"form-grid",children:[r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Amount (USD)"}),r.jsx("input",{type:"number",min:"1",max:"10000",step:"0.01",value:l,onChange:Q=>d(Q.target.value)}),r.jsx("small",{children:"Minimum $1.00, maximum $10,000.00"})]}),r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Cryptocurrency"}),r.jsx("select",{value:m,onChange:Q=>f(Q.target.value),children:wp.map(Q=>r.jsxs("option",{value:Q.code,children:[Q.label," (",Q.code,")"]},Q.code))})]})]}),w&&r.jsx("p",{className:"form-error",style:{marginTop:12},role:"alert",children:w}),r.jsx("div",{style:{marginTop:16},children:r.jsx("button",{className:"button button-primary",type:"submit",disabled:v,children:v?"Creating invoice…":"Create invoice"})})]}),r.jsxs("div",{className:"docs-footer-note",style:{marginTop:20},children:[r.jsx("strong",{children:"How it works"}),r.jsx("p",{children:'1. Choose an amount and currency above · 2. Click "Pay now" to open the payment page · 3. Send crypto to the displayed address · 4. Payment is confirmed automatically once processed on-chain'})]})]})})})]})}const bp={privacy:{title:"Privacy policy",intro:"Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",sections:[["Information we use","User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature."],["How it is used","Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],["Storage and retention","Data is stored by the server hosting Niko in local JSON and SQLite files. Economy, leveling, and configuration data remain until removed. AI conversation history is limited and can be cleared with /clearhistory."],["Third-party services","When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Music and external lookup features may contact their respective services."],["Your choices","Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."]]},terms:{title:"Terms of service",intro:"By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",sections:[["Permitted use","Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],["Availability","Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],["Moderation","The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],["AI content","AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],["Virtual items","In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],["Contact","Questions or concerns can be sent through the Niko support server."]]},community:{title:"Community policy",intro:"These community expectations apply to every server that uses Niko. By adding the bot to a server, the server's owners and administrators agree to uphold these standards.",sections:[["Purpose","Niko is a community companion for Discord servers of all kinds. To keep the platform safe for everyone, all servers using Niko must follow the expectations below in addition to Discord's Terms of Service and Community Guidelines."],["Discrimination and harassment","Servers must not permit or promote discrimination, harassment, or hate speech targeting people based on race, ethnicity, national origin, religion, disability, gender, gender identity or expression, sexual orientation, age, veteran status, or any other protected identity characteristic."],["Illegal and malicious content","Servers must not create, host, share, or distribute illegal or malicious content. This includes, but is not limited to: child sexual abuse material (CSAM), malware and other malicious software, gore or shock content, pirated media and/or software, content that facilitates violence or terrorism, scams and phishing, and any other content that is illegal under applicable law."],["Other prohibited conduct","Servers must not use Niko to facilitate doxxing, targeted harassment campaigns, sextortion, trafficking, or the sexualization of minors in any form."],["Enforcement and investigations","When a server is reported or flagged for potentially violating this policy, Niko will send a warning notice to the server. The notice is followed by an investigation by Niko staff. Servers that cooperate in good faith and are found not to be breaking the policies will not receive any further action."],["Obstruction of investigations","Banning, kicking, or otherwise removing the staff member(s) sent to investigate, or hiding, deleting, or tampering with potential evidence, is treated as an admission of guilt. Doing so will result in the server — and any users who are involved — being permanently blacklisted from further use of Niko, in addition to any other action the investigation warrants."],["Reporting","If you believe a server using Niko is violating this policy, report it through the Niko support server. Reports are reviewed by staff and handled confidentially."]]}};function ho({type:o}){const c=bp[o];return r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:o}),r.jsxs("main",{className:"shell page-main legal-page",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Niko legal"}),r.jsx("h1",{children:c.title}),r.jsx("p",{children:c.intro}),r.jsx("small",{children:"Effective date: 1 January 2025"})]}),r.jsx("div",{className:"legal-copy",children:c.sections.map(([l,d])=>r.jsxs("section",{children:[r.jsx("h2",{children:l}),r.jsx("p",{children:d})]},l))})]}),r.jsx(Bt,{})]})}const Sp=[{key:"txt",label:"TXT",icon:"📄"},{key:"html",label:"HTML",icon:"🌐"},{key:"csv",label:"CSV",icon:"📊"},{key:"json",label:"JSON",icon:"{ }"}],Xu=o=>typeof o!="number"||o<0||o>16777215?"":`#${o.toString(16).padStart(6,"0")}`,bn=o=>(o==null?void 0:o.url)||(o==null?void 0:o.proxy_url)||"",Yu=o=>/\.(?:png|jpe?g|gif|webp|bmp|svg)(?:[?#]|$)/i.test(o)||o.startsWith("data:image/"),Ju=o=>/\.(?:mp4|webm|mov|m4v|ogg)(?:[?#]|$)/i.test(o)||o.startsWith("data:video/");function Np(o){var l;const c=bn(o);return c?(l=o==null?void 0:o.content_type)!=null&&l.startsWith("video/")?!0:Ju(c):!1}const Bu=new RegExp("(`[^`\\n]+`)|(\\[([^\\]\\n]+)\\]\\((https?:\\/\\/[^\\s)\\] ]+)\\))|(\\*\\*)|(?<!\\*)\\*(?!\\*)|(~~)","g"),Cp=/(https?:\/\/[^\s<>)]+)/g,Ou={bold:"**",italic:"*",strike:"~~"};function _p(o){const c=[];let l=0,d;const m=f=>{if(!f)return;const v=f.split(Cp);for(let M=0;M<v.length;M++){const w=v[M];w&&(M%2===1?c.push({type:"link",text:w,url:w}):c.push({type:"text",text:w}))}};for(Bu.lastIndex=0;(d=Bu.exec(o))!==null;)d.index>l&&m(o.slice(l,d.index)),d[1]!==void 0?c.push({type:"code",text:d[1].slice(1,-1)}):d[2]!==void 0?c.push({type:"link",text:d[3],url:d[4]}):d[5]!==void 0?c.push({type:"marker",fmt:"bold"}):d[6]!==void 0?c.push({type:"marker",fmt:"italic"}):d[7]!==void 0&&c.push({type:"marker",fmt:"strike"}),l=d.index+d[0].length;return l<o.length&&m(o.slice(l)),c}function Tp(o){const c=[],l=[],d=new Set,m=f=>{l.length>0?l[l.length-1].children.push(f):c.push(f)};for(const f of _p(o))if(f.type==="text")m({kind:"text",text:f.text});else if(f.type==="code")m({kind:"code",text:f.text});else if(f.type==="link")m({kind:"link",text:f.text,url:f.url});else if(f.type==="marker")if(d.has(f.fmt)){const v=l.map(z=>z.fmt).lastIndexOf(f.fmt),M=l.splice(v);M.forEach(z=>d.delete(z.fmt));const w={kind:"fmt",fmt:f.fmt,children:[...M[0].children]};for(const z of M.slice(1))w.children.push({kind:"text",text:Ou[z.fmt]??""}),w.children.push(...z.children);m(w)}else l.push({fmt:f.fmt,children:[]}),d.add(f.fmt);if(l.length>0)for(const f of l){m({kind:"text",text:Ou[f.fmt]??""});for(const v of f.children)m(v)}return c}const Zu=(o,c)=>o.map((l,d)=>{const m=`${c}-${d}`;switch(l.kind){case"text":return r.jsx("span",{children:l.text},m);case"code":return r.jsx("code",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:4,padding:"0 5px",color:"#f2b8c2",fontFamily:"monospace",fontSize:"0.92em"},children:l.text},m);case"link":return r.jsx("a",{href:l.url,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",textDecoration:"none"},onMouseEnter:f=>{f.currentTarget.style.textDecoration="underline"},onMouseLeave:f=>{f.currentTarget.style.textDecoration="none"},children:l.text},m);case"fmt":{const f={};return l.fmt==="bold"&&(f.fontWeight=700),l.fmt==="italic"&&(f.fontStyle="italic"),l.fmt==="strike"&&(f.textDecoration="line-through"),r.jsx("span",{style:f,children:Zu(l.children,m)},m)}}}),Js=o=>Zu(Tp(o),"md");function wn({text:o,muted:c}){const l=o.split(`
`),d=[];return l.forEach((m,f)=>{const v=m.trimStart(),w=f===l.length-1?null:r.jsx("br",{},`br${f}`);v.startsWith("-# ")?d.push(r.jsxs("span",{style:{color:c?"#6d737a":"#949ba4",fontSize:12},children:[Js(v.slice(3)),w]},f)):/^#{1,4}\s/.test(v)?d.push(r.jsxs("span",{style:{color:"#f2f3f5",fontWeight:700,fontSize:16},children:[Js(v),w]},f)):v.startsWith("> ")?d.push(r.jsxs("span",{style:{display:"inline-block",color:"#b5bac1",borderLeft:"3px solid #4e5058",paddingLeft:8},children:[Js(v.slice(2)),w]},f)):v.startsWith("```")?d.push(r.jsxs("pre",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:6,padding:"10px 12px",overflowX:"auto",whiteSpace:"pre-wrap",wordBreak:"break-word",fontFamily:"monospace",fontSize:12.5,color:"#dbdee1",margin:"2px 0"},children:[v.replace(/^```[a-zA-Z]*/,"").replace(/```$/,""),w]},f)):d.push(r.jsxs("span",{children:[Js(m),w]},f))}),r.jsx("span",{style:{whiteSpace:"pre-wrap",wordBreak:"break-word"},children:d})}function Ep({embed:o}){const c=Xu(o.color)||"#5865f2",l=o.author,d=o.footer,m=bn(o.thumbnail),f=bn(o.image);return r.jsxs("div",{style:{display:"flex",gap:12,maxWidth:560,marginTop:8,background:"#2b2d31",border:"1px solid #3f4147",borderLeft:`4px solid ${c}`,borderRadius:6,padding:"10px 12px"},children:[r.jsxs("div",{style:{flex:1,minWidth:0},children:[(l==null?void 0:l.name)&&r.jsxs("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:4},children:[l.icon_url&&r.jsx("img",{src:l.icon_url||l.proxy_icon_url,alt:"",style:{width:18,height:18,borderRadius:"50%",verticalAlign:"-4px",marginRight:6}}),l.name]}),o.title&&r.jsx("div",{style:{color:"#00a8fc",fontWeight:600,margin:"2px 0 4px",fontSize:14},children:o.url?r.jsx("a",{href:o.url,target:"_blank",rel:"noopener noreferrer",style:{color:"inherit",textDecoration:"none"},children:r.jsx(wn,{text:o.title})}):r.jsx(wn,{text:o.title})}),o.description&&r.jsx("div",{style:{color:"#dbdee1",fontSize:13,lineHeight:1.5},children:r.jsx(wn,{text:o.description})}),o.fields&&o.fields.length>0&&r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:"6px 12px",marginTop:8},children:o.fields.map((v,M)=>r.jsxs("div",{style:{flex:v.inline?"0 1 45%":"1 1 100%",minWidth:0,marginBottom:4},children:[v.name&&r.jsx("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:2},children:r.jsx(wn,{text:v.name})}),v.value&&r.jsx("div",{style:{color:"#dbdee1",fontSize:13},children:r.jsx(wn,{text:v.value})})]},M))}),f&&r.jsx("a",{href:f,target:"_blank",rel:"noopener noreferrer",style:{display:"block",marginTop:8},children:r.jsx("img",{src:f,alt:"",style:{maxWidth:"100%",maxHeight:300,borderRadius:4,display:"block"},onError:v=>{v.currentTarget.style.display="none"}})}),((d==null?void 0:d.text)||o.timestamp)&&r.jsxs("div",{style:{display:"flex",alignItems:"center",gap:6,marginTop:6,color:"#949ba4",fontSize:11},children:[(d==null?void 0:d.icon_url)&&r.jsx("img",{src:d.icon_url||d.proxy_icon_url,alt:"",style:{width:16,height:16,borderRadius:"50%"}}),(d==null?void 0:d.text)&&r.jsx("span",{children:d.text}),o.timestamp&&r.jsx("span",{children:String(o.timestamp).replace("T"," ").replace("+00:00"," UTC")})]})]}),m&&r.jsx("a",{href:m,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:r.jsx("img",{src:m,alt:"",style:{width:80,height:80,borderRadius:6,objectFit:"cover"},onError:v=>{v.currentTarget.style.display="none"}})})]})}function Zs({component:o}){switch(o.type){case 17:{const c=Xu(o.accent_color);return r.jsxs("div",{style:{display:"flex",overflow:"hidden",maxWidth:560,marginTop:8,background:"#2b2d31",border:`1px solid ${c||"#3f4147"}`,borderRadius:12},children:[c&&r.jsx("div",{style:{flex:"0 0 4px",background:c}}),r.jsx("div",{style:{flex:1,minWidth:0,padding:"6px 12px 8px"},children:(o.components||[]).map((l,d)=>r.jsx(Zs,{component:l},d))})]})}case 1:return r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,margin:"6px 0"},children:(o.components||[]).map((c,l)=>r.jsx(Zs,{component:c},l))});case 2:{const c=o.emoji,l=`${(c==null?void 0:c.name)??""}${o.label?` ${o.label}`:""}`.trim();return o.style===5&&!!o.url?r.jsx("a",{href:o.url,target:"_blank",rel:"noopener noreferrer",style:{display:"inline-block",padding:"3px 14px",background:"#5865f2",borderRadius:4,color:"#fff",fontSize:13,fontWeight:600,textDecoration:"none"},children:l||"Button"}):r.jsx("span",{style:{display:"inline-block",padding:"3px 14px",background:"#4e5058",borderRadius:4,color:o.disabled?"#8a8e96":"#f2f3f5",fontSize:13,cursor:o.disabled?"not-allowed":"default",opacity:o.disabled?.55:1},children:l||"Button"})}case 9:{const c=[...o.components||[]];return o.accessory&&c.push(o.accessory),r.jsx("div",{style:{display:"flex",alignItems:"center",gap:10,margin:"4px 0"},children:c.map((l,d)=>r.jsx(Zs,{component:l},d))})}case 10:return r.jsx("div",{style:{color:"#dbdee1",fontSize:14,lineHeight:1.5,margin:"4px 0",wordBreak:"break-word"},children:r.jsx(wn,{text:o.content||""})});case 18:return r.jsx("div",{style:{color:"#f2f3f5",fontWeight:700,textTransform:"uppercase",letterSpacing:"0.04em",fontSize:12,margin:"4px 0"},children:o.content});case 14:return r.jsx("div",{style:{margin:o.divider===!1?"6px 0":"9px 0",...o.divider===!1?{}:{borderTop:"1px solid #3f4147"}}});case 11:{const c=bn(o.media);return c?r.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:r.jsx("img",{src:c,alt:o.description||"",style:{width:40,height:40,borderRadius:"50%",objectFit:"cover",display:"block"},onError:l=>{l.currentTarget.style.display="none"}})}):null}case 12:{const l=(o.items||[]).filter(d=>bn(d.media));return l.length===0?null:r.jsx("div",{style:{display:"grid",gridTemplateColumns:`repeat(auto-fill, minmax(${Math.min(220,Math.max(140,Math.floor(560/Math.max(1,l.length))))}px, 1fr))`,gap:6,margin:"6px 0"},children:l.map((d,m)=>{const f=bn(d.media),v=d.description;return Np(d.media)?r.jsxs("figure",{style:{margin:0},children:[r.jsx("video",{src:f,controls:!0,preload:"metadata",style:{width:"100%",maxHeight:260,borderRadius:6,background:"#1e1f22"}}),v&&r.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:v})]},m):Yu(f)?r.jsxs("figure",{style:{margin:0},children:[r.jsx("a",{href:f,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:r.jsx("img",{src:f,alt:v||"",style:{width:"100%",maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:M=>{M.currentTarget.style.display="none"}})}),v&&r.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:v})]},m):r.jsxs("a",{href:f,target:"_blank",rel:"noopener noreferrer",style:{display:"flex",alignItems:"center",gap:6,padding:"6px 10px",background:"#383a40",borderRadius:6,color:"#dbdee1",fontSize:12,textDecoration:"none"},children:["📎 ",v||"Attachment"]},m)})})}case 13:{const c=bn(o.media)||o.url||"";return c?r.jsxs("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{display:"block",margin:"4px 0",color:"#00a8fc",fontSize:12.5,textDecoration:"none"},children:["📎 ",o.label||"Attachment"]}):null}default:return null}}function Mp({components:o}){return r.jsx(r.Fragment,{children:o.map((c,l)=>r.jsx(Zs,{component:c},l))})}function Pp({text:o}){return r.jsx(wn,{text:o})}function Lp({msg:o}){const c=!!(o.attachments&&o.attachments.length>0||o.embeds&&o.embeds.length>0||o.components&&o.components.length>0);return r.jsxs("div",{style:{padding:"10px 16px",borderBottom:"1px solid #2b2d31",fontSize:14,lineHeight:1.6},children:[r.jsxs("div",{style:{marginBottom:2},children:[r.jsx("span",{style:{color:"#949ba4",fontSize:11,fontFamily:"monospace"},children:o.timestamp})," ",r.jsx("span",{style:{color:"#f2f3f5",fontWeight:600},children:o.author})," ",r.jsxs("span",{style:{color:"#949ba4",fontSize:11},children:["(",o.author_id,")"]})]}),o.content?r.jsx("div",{style:{color:"#dbdee1"},children:r.jsx(Pp,{text:o.content})}):c?null:r.jsx("div",{style:{color:"#6d737a",fontStyle:"italic",fontSize:13},children:"Message content unavailable"}),o.attachments&&o.attachments.length>0&&r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:4},children:o.attachments.map((l,d)=>Ju(l)?r.jsx("video",{src:l,controls:!0,preload:"metadata",style:{maxWidth:360,maxHeight:260,borderRadius:6,background:"#1e1f22"}},d):Yu(l)?r.jsx("a",{href:l,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:r.jsx("img",{src:l,alt:"",style:{maxWidth:300,maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:m=>{const f=m.currentTarget;f.style.display="none"}})},d):r.jsx("a",{href:l,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",fontSize:12,textDecoration:"none"},children:"📎 Attachment"},d))}),o.embeds&&o.embeds.length>0&&r.jsx(r.Fragment,{children:o.embeds.map((l,d)=>r.jsx(Ep,{embed:l},d))}),o.components&&o.components.length>0&&r.jsx(Mp,{components:o.components})]})}function Rp({transcriptId:o}){const[c,l]=R.useState(null),[d,m]=R.useState(!0),[f,v]=R.useState("");R.useEffect(()=>{m(!0),v(""),fetch(`/api/transcript/${o}`).then(w=>{if(!w.ok)throw new Error("Transcript not found");return w.json()}).then(w=>{l(w),m(!1)}).catch(w=>{v(w.message||"Failed to load transcript"),m(!1)})},[o]);const M=w=>{window.open(`/api/transcript/${o}/download?format=${w}`,"_blank")};return d?r.jsx("div",{className:"page-main",children:r.jsx("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:r.jsx("div",{style:{color:"var(--muted)",fontSize:14},children:"Loading transcript…"})})}):f||!c?r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:[r.jsx("h2",{style:{marginBottom:12},children:"Transcript not found"}),r.jsx("p",{style:{color:"var(--muted)"},children:f||"This transcript doesn't exist or has been deleted."})]})}):r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{maxWidth:800},children:[r.jsx("div",{style:{background:"var(--surface)",border:"1px solid var(--line)",borderRadius:8,padding:24,marginBottom:20},children:r.jsxs("div",{style:{display:"flex",alignItems:"flex-start",justifyContent:"space-between",gap:16,flexWrap:"wrap"},children:[r.jsxs("div",{children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:8},children:"Ticket Transcript"}),r.jsxs("h1",{style:{fontSize:24,letterSpacing:"-0.04em",margin:0},children:["#",c.channel_name]}),r.jsxs("div",{style:{color:"var(--muted)",fontSize:13,marginTop:6},children:[c.category," · ",c.message_count," messages · ",c.created_at]})]}),r.jsx("div",{style:{display:"flex",gap:8,flexWrap:"wrap"},children:Sp.map(w=>r.jsxs("button",{className:"button button-small button-muted",onClick:()=>M(w.key),style:{minWidth:70},children:[r.jsx("span",{children:w.icon}),r.jsx("span",{children:w.label})]},w.key))})]})}),r.jsxs("div",{style:{background:"#1e1f22",border:"1px solid #3f4147",borderRadius:8,overflow:"hidden"},children:[c.messages.map((w,z)=>r.jsx(Lp,{msg:w},z)),c.messages.length===0&&r.jsx("div",{style:{padding:40,textAlign:"center",color:"#949ba4"},children:"No messages in this transcript."})]}),r.jsxs("div",{style:{marginTop:16,padding:"12px 0",textAlign:"center",color:"var(--dim)",fontSize:12},children:["Transcript ID: ",r.jsx("code",{style:{fontFamily:"monospace"},children:o})]})]})})}const na=[{slug:"economy-leveling-overhaul",title:"Economy Items, Leveling Cards & Subcommands",date:"2026-09-08",version:"2.8.0",tags:["economy","leveling","shop","image-cards"],summary:"The economy shop expanded with four new consumable items that affect gameplay — Rigged Coin, Streak Insurance, Double Down Token, and Lucky Horseshoe — plus daily streak milestone bonuses at 7, 14, 30, 60, and 90 days. The leveling system now renders rank cards and leaderboards as customizable image cards, and all leveling commands live under a single `/leveling` group with subcommands.",highlights:[{title:"New Shop Items",description:"Four new consumables: Rigged Coin (60/40 coinflip odds), Streak Insurance (protects daily streak for one missed day), Double Down Token (1.5x gambling payout), and Lucky Horseshoe (+10% work reward).",icon:"chart"},{title:"Leveling Image Cards",description:"Rank cards and the leaderboard now render as styled images with avatar, level, XP bar, and rank. Server admins can customize the card accent color and background gradient.",icon:"spark"},{title:"Leveling Subcommands",description:"All leveling commands reorganized under `/leveling` with `rank`, `leaderboard`, `panel`, and `config` subcommands. The leaderboard now has interactive pagination buttons.",icon:"settings"},{title:"Daily Streak Milestones",description:"Hitting 7, 14, 30, 60, or 90-day daily streaks now awards bonus items from the shop (Espresso Shots, Lockpicks, Lucky Charms, Rob Shields) along with a coin bonus.",icon:"utility"}],changes:[{category:"added",items:["Coinflip command with heads/tails call and double-or-nothing payout","Rigged Coin shop item — gives 60/40 coinflip odds for one use","Streak Insurance shop item — protects daily streak if you miss one day","Double Down Token shop item — next gambling win pays 1.5x","Lucky Horseshoe shop item — next work reward gets +10%","Daily streak milestone bonuses at 7/14/30/60/90 days with item rewards","Image card rendering for `/leveling rank` with customizable accent and background","Image card rendering for the leveling leaderboard","Inventory display as an image card in the shop command","Twemoji emoji rendering in economy card images","Pagination buttons (◀ ▶) on the leveling leaderboard","Card customization fields in the database: card_accent, card_bg_top, card_bg_bottom"]},{category:"improved",items:["Leveling commands restructured as `/leveling rank`, `leaderboard`, `panel`, `config` subcommands","Shop command visual layout with better font rendering on economy image cards","Crime and rob commands now check for gambling_boost effect for 1.5x payout","HTML download format for ticket transcripts","Dashboard UI refinements"]},{category:"fixed",items:["Command name conflicts between leveling and other cogs","Missing import in leveling cog after image card addition","Duplicate command alias in leveling system","Command name conflict in the gambling cog"]}],chart:{type:"bar",title:"New Shop Items & Their Effects",data:[{label:"Rigged Coin",value:3e3,color:"#c9a84c"},{label:"Streak Insurance",value:4e3,color:"#4a7fb5"},{label:"Double Down Token",value:5e3,color:"#d96545"},{label:"Lucky Horseshoe",value:2500,color:"#66866f"}]},commits:["41d86fb Expanded the gambling and economy system","bd6a09c Added image cards to the leveling system","5307bb1 Moved the leveling commands to the levels subcommand","dafd224 Added an image card to the inventory command","49fc83b Added emoji rendering to the shop command","0aca6ba Improved the shop command","30c9735 Added better font rendering to the economy system image cards","2b96835 Fixed a command name conflict","158ad8f Fixed a command name conflict in the gambling cog","d465598 Fixed a missing import","1f24ffb Fixed a duplicate command alias"]},{slug:"database-migration",title:"Database Migration to MongoDB",date:"2026-09-03",version:"2.7.0",tags:["database","mongodb","migration","infrastructure"],summary:"Every major system has been migrated from SQLite to MongoDB. The migration covered economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and the blacklist — with a custom interpreter that translates SQLite-style writes to MongoDB operations.",highlights:[{title:"Full MongoDB Migration",description:"Economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and blacklist now all store data in MongoDB instead of SQLite.",icon:"settings"},{title:"Slash Command Sync Safeguard",description:"A new check prevents redundant Discord API calls when all commands are already registered, reducing rate-limit issues on startup.",icon:"utility"},{title:"Proxy Integration",description:"A new proxy manager reduces downtime on shared hosting environments by routing API requests through a proxy layer.",icon:"shield"}],changes:[{category:"migrated",items:["Economy system — balances, banks, jobs, achievements, inventory","Leveling system — XP, levels, role rewards, card customization","Moderation system — warnings, mutes, automod config","Ticket system — panels, transcripts, support roles","Birthday system — dates, channels, messages","AFK system — status, timestamps","Sticky messages — content, channels","Blacklist — users, words, filters"]},{category:"added",items:["MongoDB interpreter that translates SQLite-style writes to proper MongoDB operations","Proxy manager for shared hosting reliability","Slash command sync safeguard to prevent redundant API calls","Context menu command support in the sync utility"]},{category:"fixed",items:["MongoDB interpreter not translating all SQLite write patterns correctly","Economy interest calculation after migration","Birthday system data persistence","Several database connection issues across various cogs","Leveling database initialization issue"]}],chart:{type:"pie",title:"Systems Migrated to MongoDB",data:[{label:"Economy",value:1,color:"#d96545"},{label:"Leveling",value:1,color:"#66866f"},{label:"Moderation",value:1,color:"#4a7fb5"},{label:"Tickets",value:1,color:"#c9a84c"},{label:"Birthdays",value:1,color:"#b07cc6"},{label:"AFK",value:1,color:"#e0976e"},{label:"Sticky Msgs",value:1,color:"#7ca898"},{label:"Blacklist",value:1,color:"#8c918e"}]},commits:["c07f9b1 Fixed the MongoDB interpreter to properly translate all SQLite database writes","0d3aca5 Migrated the blacklist to the main database","954ebac Migrated the birthday system to the main database","5013d54 Migrated the warns and mutes to use the main database","f29c217 Migrated the afk system to the main database","5732b48 Migrated the sticky messages to use the main database","b0524f1 Migrated the ticket system to the main database","70e6d7a Fixed the sync util to support context commands and slash groups","2c01817 Added a safeguard to prevent slash command syncs when all commands are already present","121afcf Added a proxy integration to reduce downtime on shared hosting","9f2f1fd Fixed several database issues across various cogs"]},{slug:"ticket-system-transcripts",title:"Ticket Transcripts & VoiceMaster",date:"2026-09-03",version:"2.6.0",tags:["tickets","transcripts","voicemaster"],summary:"The ticket system gained a web-based transcript viewer that renders ticket conversations as styled HTML pages. The VoiceMaster was also improved with better reliability and database usage. Ticket transcripts can now be downloaded as HTML or viewed online.",highlights:[{title:"Web Transcript Viewer",description:"Ticket transcripts are now rendered as styled HTML pages that can be viewed online. The HTML download format was also improved for better readability.",icon:"doc"},{title:"VoiceMaster Reliability",description:"The VoiceMaster (temporary voice channels) was improved with better database usage and reliability fixes.",icon:"utility"},{title:"Donation Dashboard Page",description:"A new customization page in the dashboard lets server admins configure donation settings without using commands.",icon:"settings"}],changes:[{category:"added",items:["Web-based ticket transcript viewer with styled HTML output","Ticket transcript database table for storing transcripts online","Dashboard customization page for donation system settings"]},{category:"improved",items:["HTML download format for ticket transcripts","VoiceMaster reliability and database usage patterns","Ticket system persistence and data handling"]},{category:"fixed",items:["Ticket transcript pages rendering incorrectly","Ticket system data loss on restart","Ticket transcript generation issues","Ticket transcript page display bugs"]}],commits:["e953321 Added a new web transcript feature to the ticket system","aa0b73b Improved the donation system and added a customization page to the dashboard","3255385 Improved the html download format for the ticket transcripts","45f1fb0 Fixed the ticket system persistence","ef4e057 Added the ticket system database migrations","d4e0bc8 Fixed the ticket transcripts","4bf5e04 Fixed an issue with the ticket transcript pages","e8dbcb0 Improved the VoiceMaster reliability and improved the database usage"]},{slug:"roleplay-music-status",title:"Roleplay, Music & Status Rotation",date:"2026-09-05",version:"2.5.0",tags:["roleplay","music","status","social"],summary:"The roleplay cog was completely rewritten to use nekos.best API GIFs with CV2 layout messages and a persistent 'hug back' button. The music cog was restructured with a ghost queue feature and fixed autoplay/Spotify playback. A status message rotation system was added with a configurable timer.",highlights:[{title:"Roleplay Rewrite",description:"The roleplay cog now fetches SFW reaction GIFs from nekos.best, renders them in styled CV2 containers, and includes a 'hug back' button that persists across restarts. A single user context menu replaces individual action menus to stay under Discord's 15-command cap.",icon:"users"},{title:"Music Ghost Queue",description:"A new ghost queue feature lets songs be queued even when nothing is currently playing. Autoplay and Spotify playback were also fixed.",icon:"utility"},{title:"Status Rotation",description:"The bot now rotates through configurable status messages on a timer (default 30s interval), with activity types and a VR device presence.",icon:"spark"}],changes:[{category:"added",items:["Status message rotation with configurable interval and activity types","Persistent status panel command for the support server (owner only)","Roleplay block feature to prevent specific users from being targeted","Ghost queue feature — queue songs even when nothing is playing","User context menu for roleplay actions (replaces per-action menus)","YouTube channel name validation for notification system"]},{category:"improved",items:["Roleplay cog complete rewrite — nekos.best GIFs, CV2 layouts, persistent buttons","Social media notification emoji formatting (Bluesky, Reddit, TikTok, Twitch icons)","Music node connection system and autoplay reliability","Spotify playback quality","Music cog restructured with better error handling"]},{category:"fixed",items:["Status rotator startup errors and activity conflicts","on_ready event error handling and reliability","Lavalink connection bug","Roleplay prefix command handling","Bluesky and Reddit notification delivery issues"]}],chart:{type:"bar",title:"Files Changed per Feature Area",data:[{label:"Roleplay",value:3,color:"#d96545"},{label:"Music",value:4,color:"#4a7fb5"},{label:"Status",value:3,color:"#66866f"},{label:"Social",value:2,color:"#c9a84c"}]},commits:["0c58178 Redesigned the roleplay cog","6c4ee09 Fixed the roleplay prefix commands","f1f8591 Added a roleplay block feature","e01e3e4 Added status message rotation","5e63e1d Added a persistent status panel","ae7501a Restructured the music cog","526813e Added a new ghost queue feature to the music cog","6524da1 Improved the music node connection system, fixed the autoplay, and fixed the Spotify playback","4264677 Fixed a lavalink connection bug","d62ead8 Improved the social media notification system's emojis","0f0305d Improved the social media notification formatting","42069d4 Added proper channel name validation to the YouTube notification system"]},{slug:"moderation-logging-dashboard",title:"Logging, Moderation & Documentation",date:"2026-09-07",version:"2.4.0",tags:["logging","moderation","documentation","dashboard"],summary:"Logging got two major improvements: deleted message logs now show image attachments in a MediaGallery component, and the Member category now tracks avatar changes using a Section with Thumbnail accessory. The documentation page was fully rebuilt with search, filters, and a card-based layout.",highlights:[{title:"Image Attachments in Logs",description:"Deleted message logs now render attached images in a MediaGallery component inside the log container, so moderators can see what was posted without leaving Discord.",icon:"chart"},{title:"Avatar Change Tracking",description:"The Member logging category now detects avatar changes (global and server avatars) and displays them in a Section with a Thumbnail accessory showing the new avatar.",icon:"users"},{title:"Documentation Redesign",description:"The documentation page was rebuilt from scratch with a search bar, category filters, tag cloud, card-based layout, and individual article pages with table of contents.",icon:"doc"}],changes:[{category:"added",items:["Image attachments rendered in deleted message logs via MediaGallery","Avatar change detection in Member logging with Section + Thumbnail display","Startup economy cache that loads all users into memory for accurate leaderboards","Error handler for role menu post buttons","Full-text search with result highlighting in documentation","Category filters and tag cloud in documentation","Individual documentation article pages with table of contents"]},{category:"improved",items:["Logging system now supports media_urls, thumbnail_url, and files parameters","Commands page expanded with better organization","Dashboard UI refinements","Economy interest feature — skips malformed records with non-integer user IDs"]},{category:"fixed",items:["Logging command issues","Documentation command references","Status device detection issue","Status rotator conflicts between multiple status types","on_ready event reliability with proper error handling"]}],commits:["722a34f Added avatar updates to the logging cogs Member logs","1d82ea1 Moved file attachments inside the main log message for the deleted message logs","358d537 Added a startup economy cache to fix the leaderboard","566e0c4 Improved the dashboard","132bcbb Fully redesigned the documentation page","4f7a89a Improved the commands page","6d953b6 Fixed the logging command","a202687 Fixed some documentation issues","49d22ad Fixed the documentation command references","52de287 Added an error handler to the post role menu button"]},{slug:"website-launch-donation",title:"Website, Donation System & API",date:"2026-09-02",version:"2.3.0",tags:["website","donations","api"],summary:"The public website and documentation portal launched with a React + Vite frontend, documentation center with search, and a commands reference page. The donation system gained a dashboard customization page, and the Flask API backend was fixed to use proper database calls.",highlights:[{title:"Public Website",description:"A complete public website built with React and Vite featuring a landing page, documentation center, command reference, dashboard, and legal pages.",icon:"spark"},{title:"Documentation Center",description:"The documentation page was redesigned with a card-based layout, individual article pages, and a modern visual design matching the bot's aesthetic.",icon:"doc"},{title:"Donation Dashboard",description:"Server admins can now configure donation settings through a new dashboard page instead of relying solely on commands.",icon:"settings"}],changes:[{category:"added",items:["Public website with landing page, documentation center, and command reference","Donation system customization page in the dashboard","Ticket transcript viewer web page","Donate page with Oxapay integration"]},{category:"improved",items:["Flask API to use proper database calls instead of direct SQLite access","Website commands page with expanded details","Database layer reliability for production"]},{category:"fixed",items:["Flask API database call issues","Several database-related bugs across cogs","node_modules folder accidentally committed to repository"]}],commits:["132bcbb Fully redesigned the documentation page","aa0b73b Improved the donation system and added a customization page to the dashboard","bd5e3be Expanded the website's commands page","e266644 Fixed the flask API to use the proper database calls","e99ed47 Fixed several database related issues","c783514 Minor API fixes and improvements","0df4478 Added the node_modules folder to the gitignore file"]}];function Ap(o){return na.find(c=>c.slug===o)}function Dp(){const o=new Set;return na.forEach(c=>c.tags.forEach(l=>o.add(l))),Array.from(o).sort()}function Ip(){const[o,c]=R.useState(""),l=Dp(),d=o?na.filter(m=>m.tags.includes(o)):na;return r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:"home"}),r.jsxs("main",{className:"shell page-main changelog-page",children:[r.jsxs("div",{className:"changelog-hero",children:[r.jsxs("div",{className:"eyebrow",children:[r.jsx("span",{className:"status-dot"})," What's new"]}),r.jsxs("h1",{className:"changelog-title",children:["Changelog",r.jsx("br",{}),r.jsx("span",{className:"title-accent",children:"& updates"})]}),r.jsx("p",{className:"changelog-subtitle",children:"A record of every improvement, fix, and new feature added to Niko. Grouped by release for clarity."})]}),r.jsxs("div",{className:"changelog-tags",children:[r.jsx("button",{className:`changelog-tag-btn ${o===""?"active":""}`,onClick:()=>c(""),children:"All"}),l.slice(0,12).map(m=>r.jsx("button",{className:`changelog-tag-btn ${o===m?"active":""}`,onClick:()=>c(m),children:m},m))]}),r.jsx("div",{className:"changelog-timeline",children:d.map((m,f)=>r.jsxs("article",{className:"changelog-entry",children:[r.jsxs("div",{className:"changelog-entry-date-col",children:[r.jsx("div",{className:"changelog-date-dot"}),f<d.length-1&&r.jsx("div",{className:"changelog-date-line"})]}),r.jsxs("div",{className:"changelog-entry-card",children:[r.jsxs("div",{className:"changelog-entry-header",children:[r.jsxs("div",{className:"changelog-entry-meta",children:[r.jsx("time",{className:"changelog-entry-date",children:new Date(m.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),m.version&&r.jsxs("span",{className:"changelog-version",children:["v",m.version]})]}),r.jsx("h2",{className:"changelog-entry-title",children:m.title}),r.jsx("p",{className:"changelog-entry-summary",children:m.summary})]}),r.jsx("div",{className:"changelog-entry-highlights",children:m.highlights.slice(0,2).map(v=>r.jsxs("div",{className:"changelog-highlight-mini",children:[r.jsx("span",{className:"highlight-mini-icon",children:r.jsx(K,{name:v.icon,size:16})}),r.jsxs("div",{children:[r.jsx("strong",{children:v.title}),r.jsxs("p",{children:[v.description.slice(0,120),"..."]})]})]},v.title))}),r.jsx("div",{className:"changelog-entry-tags",children:m.tags.map(v=>r.jsx("span",{className:"changelog-tag",children:v},v))}),r.jsxs("button",{className:"changelog-read-more",onClick:()=>{oe(`/changelog/${m.slug}`)},children:["Read full release notes ",r.jsx(K,{name:"arrow",size:14})]})]})]},m.slug))}),d.length===0&&r.jsxs("div",{className:"changelog-empty",children:[r.jsx(K,{name:"doc",size:40}),r.jsx("p",{children:"No changelog entries match this filter."})]})]}),r.jsx(Bt,{})]})}function zp({slug:o}){const c=Ap(o);return c?r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:"home"}),r.jsxs("main",{className:"shell page-main changelog-page changelog-detail",children:[r.jsx("div",{className:"changelog-back",children:r.jsxs("button",{onClick:()=>oe("/changelog"),className:"back-button",children:[r.jsx(K,{name:"arrow",size:16}),"Back to Changelog"]})}),r.jsxs("header",{className:"changelog-detail-header",children:[r.jsxs("div",{className:"changelog-detail-meta",children:[r.jsx("time",{children:new Date(c.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),c.version&&r.jsxs("span",{className:"changelog-version",children:["v",c.version]})]}),r.jsx("h1",{children:c.title}),r.jsx("p",{className:"changelog-detail-summary",children:c.summary}),r.jsx("div",{className:"changelog-detail-tags",children:c.tags.map(l=>r.jsx("span",{className:"changelog-tag",children:l},l))})]}),r.jsxs("section",{className:"changelog-highlights-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"Highlights"}),r.jsx("div",{className:"changelog-highlights-grid",children:c.highlights.map(l=>r.jsxs("div",{className:"changelog-highlight-card",children:[r.jsx("span",{className:"highlight-icon",children:r.jsx(K,{name:l.icon,size:22})}),r.jsx("h3",{children:l.title}),r.jsx("p",{children:l.description})]},l.title))})]}),c.chart&&r.jsx(Fp,{chart:c.chart}),r.jsxs("section",{className:"changelog-changes-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"All Changes"}),r.jsx("div",{className:"changelog-changes-grid",children:c.changes.map(l=>r.jsxs("div",{className:`changelog-change-group changelog-change-${l.category}`,children:[r.jsx("h3",{className:"change-group-title",children:r.jsx("span",{className:`change-badge change-badge-${l.category}`,children:l.category})}),r.jsx("ul",{children:l.items.map((d,m)=>r.jsx("li",{children:d},m))})]},l.category))})]}),c.commits.length>0&&r.jsxs("section",{className:"changelog-commits-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"Commits"}),r.jsx("div",{className:"changelog-commits-list",children:c.commits.map(l=>{const[d,...m]=l.split(" ");return r.jsxs("div",{className:"changelog-commit",children:[r.jsx("code",{className:"commit-hash",children:d.slice(0,7)}),r.jsx("span",{className:"commit-msg",children:m.join(" ")})]},d)})})]}),r.jsx("nav",{className:"changelog-detail-nav",children:r.jsxs("button",{onClick:()=>oe("/changelog"),children:[r.jsx(K,{name:"arrow",size:14}),"All releases"]})})]}),r.jsx(Bt,{})]}):r.jsxs(r.Fragment,{children:[r.jsx(rt,{page:"home"}),r.jsx("main",{className:"shell page-main changelog-page",children:r.jsxs("div",{className:"changelog-not-found",children:[r.jsx(K,{name:"doc",size:48}),r.jsx("h1",{children:"Entry Not Found"}),r.jsxs("p",{children:[`We couldn't find a changelog entry for "`,o,'".']}),r.jsx("button",{onClick:()=>oe("/changelog"),children:"View all changelog entries"})]})}),r.jsx(Bt,{})]})}function Fp({chart:o}){return r.jsxs("section",{className:"changelog-chart-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:o.title}),r.jsxs("div",{className:"changelog-chart-container",children:[o.type==="bar"&&r.jsx(Wu,{chart:o}),o.type==="pie"&&r.jsx(Bp,{chart:o}),o.type==="comparison"&&r.jsx(Op,{chart:o}),o.type==="line"&&r.jsx(Wu,{chart:o})]})]})}function Wu({chart:o}){const c=Math.max(...o.data.map(l=>l.value));return r.jsx("div",{className:"chart-bar",children:o.data.map(l=>r.jsxs("div",{className:"chart-bar-row",children:[r.jsx("span",{className:"chart-bar-label",children:l.label}),r.jsxs("div",{className:"chart-bar-track",children:[r.jsx("div",{className:"chart-bar-fill",style:{width:`${l.value/c*100}%`,background:l.color||"var(--accent)"}}),r.jsx("span",{className:"chart-bar-value",children:l.value})]})]},l.label))})}function Bp({chart:o}){const c=o.data.reduce((f,v)=>f+v.value,0);let l=0;const m=o.data.map(f=>{const v=l/c*360;l+=f.value;const M=l/c*360;return{...f,start:v,end:M}}).map(f=>{const v=f.start/360*100,M=f.end/360*100;return`${f.color||"#d96545"} ${v}% ${M}%`}).join(", ");return r.jsxs("div",{className:"chart-pie-wrapper",children:[r.jsx("div",{className:"chart-pie",style:{background:`conic-gradient(${m})`}}),r.jsx("div",{className:"chart-pie-legend",children:o.data.map(f=>r.jsxs("div",{className:"chart-legend-item",children:[r.jsx("span",{className:"chart-legend-dot",style:{background:f.color||"var(--accent)"}}),r.jsx("span",{className:"chart-legend-label",children:f.label})]},f.label))})]})}function Op({chart:o}){const c=Math.ceil(o.data.length/2),l=o.data.slice(0,c),d=o.data.slice(c),m=Math.max(...o.data.map(f=>f.value));return r.jsxs("div",{className:"chart-comparison",children:[r.jsxs("div",{className:"chart-comparison-col",children:[r.jsx("h4",{className:"comparison-label comparison-before",children:"Before"}),l.map(f=>r.jsxs("div",{className:"chart-bar-row",children:[r.jsx("span",{className:"chart-bar-label",children:f.label}),r.jsxs("div",{className:"chart-bar-track",children:[r.jsx("div",{className:"chart-bar-fill",style:{width:`${f.value/m*100}%`,background:f.color||"var(--accent)"}}),r.jsx("span",{className:"chart-bar-value",children:f.value})]})]},f.label))]}),r.jsx("div",{className:"chart-comparison-divider",children:r.jsx(K,{name:"arrow",size:20})}),r.jsxs("div",{className:"chart-comparison-col",children:[r.jsx("h4",{className:"comparison-label comparison-after",children:"After"}),d.map(f=>r.jsxs("div",{className:"chart-bar-row",children:[r.jsx("span",{className:"chart-bar-label",children:f.label}),r.jsxs("div",{className:"chart-bar-track",children:[r.jsx("div",{className:"chart-bar-fill",style:{width:`${f.value/m*100}%`,background:f.color||"var(--accent)"}}),r.jsx("span",{className:"chart-bar-value",children:f.value})]})]},f.label))]})]})}function Wp(){const[o,c]=R.useState(Tu);if(R.useEffect(()=>{const l=()=>c(Tu());return window.addEventListener("popstate",l),()=>window.removeEventListener("popstate",l)},[]),o==="commands")return r.jsx(Vh,{});if(o==="docs-detail"){const l=window.location.pathname.split("/"),d=l[l.length-1];return r.jsx(yp,{slug:d})}if(o==="docs")return r.jsx(xp,{});if(o==="dashboard")return r.jsx(dp,{});if(o==="privacy")return r.jsx(ho,{type:"privacy"});if(o==="terms")return r.jsx(ho,{type:"terms"});if(o==="community")return r.jsx(ho,{type:"community"});if(o==="donate")return r.jsx(jp,{});if(o==="transcript"){const d=window.location.pathname.split("/").filter(Boolean)[1]||"";return r.jsx(Rp,{transcriptId:d})}if(o==="changelog")return r.jsx(Ip,{});if(o==="changelog-detail"){const l=window.location.pathname.split("/"),d=l[l.length-1];return r.jsx(zp,{slug:d})}return r.jsx(kp,{})}ih.createRoot(document.getElementById("root")).render(r.jsx(R.StrictMode,{children:r.jsx(Wp,{})}));
