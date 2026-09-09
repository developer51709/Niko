var qm=Object.defineProperty;var Qm=(o,c,l)=>c in o?qm(o,c,{enumerable:!0,configurable:!0,writable:!0,value:l}):o[c]=l;var mu=(o,c,l)=>Qm(o,typeof c!="symbol"?c+"":c,l);(function(){const c=document.createElement("link").relList;if(c&&c.supports&&c.supports("modulepreload"))return;for(const m of document.querySelectorAll('link[rel="modulepreload"]'))d(m);new MutationObserver(m=>{for(const f of m)if(f.type==="childList")for(const v of f.addedNodes)v.tagName==="LINK"&&v.rel==="modulepreload"&&d(v)}).observe(document,{childList:!0,subtree:!0});function l(m){const f={};return m.integrity&&(f.integrity=m.integrity),m.referrerPolicy&&(f.referrerPolicy=m.referrerPolicy),m.crossOrigin==="use-credentials"?f.credentials="include":m.crossOrigin==="anonymous"?f.credentials="omit":f.credentials="same-origin",f}function d(m){if(m.ep)return;m.ep=!0;const f=l(m);fetch(m.href,f)}})();var to={exports:{}},Dr={},no={exports:{}},re={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var hu;function Xm(){if(hu)return re;hu=1;var o=Symbol.for("react.element"),c=Symbol.for("react.portal"),l=Symbol.for("react.fragment"),d=Symbol.for("react.strict_mode"),m=Symbol.for("react.profiler"),f=Symbol.for("react.provider"),v=Symbol.for("react.context"),P=Symbol.for("react.forward_ref"),w=Symbol.for("react.suspense"),F=Symbol.for("react.memo"),N=Symbol.for("react.lazy"),C=Symbol.iterator;function L(y){return y===null||typeof y!="object"?null:(y=C&&y[C]||y["@@iterator"],typeof y=="function"?y:null)}var I={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},z=Object.assign,B={};function b(y,E,ne){this.props=y,this.context=E,this.refs=B,this.updater=ne||I}b.prototype.isReactComponent={},b.prototype.setState=function(y,E){if(typeof y!="object"&&typeof y!="function"&&y!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,y,E,"setState")},b.prototype.forceUpdate=function(y){this.updater.enqueueForceUpdate(this,y,"forceUpdate")};function U(){}U.prototype=b.prototype;function S(y,E,ne){this.props=y,this.context=E,this.refs=B,this.updater=ne||I}var Q=S.prototype=new U;Q.constructor=S,z(Q,b.prototype),Q.isPureReactComponent=!0;var te=Array.isArray,se=Object.prototype.hasOwnProperty,_={current:null},X={key:!0,ref:!0,__self:!0,__source:!0};function he(y,E,ne){var ae,le={},ce=null,pe=null;if(E!=null)for(ae in E.ref!==void 0&&(pe=E.ref),E.key!==void 0&&(ce=""+E.key),E)se.call(E,ae)&&!X.hasOwnProperty(ae)&&(le[ae]=E[ae]);var de=arguments.length-2;if(de===1)le.children=ne;else if(1<de){for(var ye=Array(de),it=0;it<de;it++)ye[it]=arguments[it+2];le.children=ye}if(y&&y.defaultProps)for(ae in de=y.defaultProps,de)le[ae]===void 0&&(le[ae]=de[ae]);return{$$typeof:o,type:y,key:ce,ref:pe,props:le,_owner:_.current}}function je(y,E){return{$$typeof:o,type:y.type,key:E,ref:y.ref,props:y.props,_owner:y._owner}}function st(y){return typeof y=="object"&&y!==null&&y.$$typeof===o}function Ue(y){var E={"=":"=0",":":"=2"};return"$"+y.replace(/[=:]/g,function(ne){return E[ne]})}var ze=/\/+/g;function $e(y,E){return typeof y=="object"&&y!==null&&y.key!=null?Ue(""+y.key):E.toString(36)}function at(y,E,ne,ae,le){var ce=typeof y;(ce==="undefined"||ce==="boolean")&&(y=null);var pe=!1;if(y===null)pe=!0;else switch(ce){case"string":case"number":pe=!0;break;case"object":switch(y.$$typeof){case o:case c:pe=!0}}if(pe)return pe=y,le=le(pe),y=ae===""?"."+$e(pe,0):ae,te(le)?(ne="",y!=null&&(ne=y.replace(ze,"$&/")+"/"),at(le,E,ne,"",function(it){return it})):le!=null&&(st(le)&&(le=je(le,ne+(!le.key||pe&&pe.key===le.key?"":(""+le.key).replace(ze,"$&/")+"/")+y)),E.push(le)),1;if(pe=0,ae=ae===""?".":ae+":",te(y))for(var de=0;de<y.length;de++){ce=y[de];var ye=ae+$e(ce,de);pe+=at(ce,E,ne,ye,le)}else if(ye=L(y),typeof ye=="function")for(y=ye.call(y),de=0;!(ce=y.next()).done;)ce=ce.value,ye=ae+$e(ce,de++),pe+=at(ce,E,ne,ye,le);else if(ce==="object")throw E=String(y),Error("Objects are not valid as a React child (found: "+(E==="[object Object]"?"object with keys {"+Object.keys(y).join(", ")+"}":E)+"). If you meant to render a collection of children, use an array instead.");return pe}function St(y,E,ne){if(y==null)return y;var ae=[],le=0;return at(y,ae,"","",function(ce){return E.call(ne,ce,le++)}),ae}function Ge(y){if(y._status===-1){var E=y._result;E=E(),E.then(function(ne){(y._status===0||y._status===-1)&&(y._status=1,y._result=ne)},function(ne){(y._status===0||y._status===-1)&&(y._status=2,y._result=ne)}),y._status===-1&&(y._status=0,y._result=E)}if(y._status===1)return y._result.default;throw y._result}var be={current:null},O={transition:null},Z={ReactCurrentDispatcher:be,ReactCurrentBatchConfig:O,ReactCurrentOwner:_};function V(){throw Error("act(...) is not supported in production builds of React.")}return re.Children={map:St,forEach:function(y,E,ne){St(y,function(){E.apply(this,arguments)},ne)},count:function(y){var E=0;return St(y,function(){E++}),E},toArray:function(y){return St(y,function(E){return E})||[]},only:function(y){if(!st(y))throw Error("React.Children.only expected to receive a single React element child.");return y}},re.Component=b,re.Fragment=l,re.Profiler=m,re.PureComponent=S,re.StrictMode=d,re.Suspense=w,re.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Z,re.act=V,re.cloneElement=function(y,E,ne){if(y==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+y+".");var ae=z({},y.props),le=y.key,ce=y.ref,pe=y._owner;if(E!=null){if(E.ref!==void 0&&(ce=E.ref,pe=_.current),E.key!==void 0&&(le=""+E.key),y.type&&y.type.defaultProps)var de=y.type.defaultProps;for(ye in E)se.call(E,ye)&&!X.hasOwnProperty(ye)&&(ae[ye]=E[ye]===void 0&&de!==void 0?de[ye]:E[ye])}var ye=arguments.length-2;if(ye===1)ae.children=ne;else if(1<ye){de=Array(ye);for(var it=0;it<ye;it++)de[it]=arguments[it+2];ae.children=de}return{$$typeof:o,type:y.type,key:le,ref:ce,props:ae,_owner:pe}},re.createContext=function(y){return y={$$typeof:v,_currentValue:y,_currentValue2:y,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},y.Provider={$$typeof:f,_context:y},y.Consumer=y},re.createElement=he,re.createFactory=function(y){var E=he.bind(null,y);return E.type=y,E},re.createRef=function(){return{current:null}},re.forwardRef=function(y){return{$$typeof:P,render:y}},re.isValidElement=st,re.lazy=function(y){return{$$typeof:N,_payload:{_status:-1,_result:y},_init:Ge}},re.memo=function(y,E){return{$$typeof:F,type:y,compare:E===void 0?null:E}},re.startTransition=function(y){var E=O.transition;O.transition={};try{y()}finally{O.transition=E}},re.unstable_act=V,re.useCallback=function(y,E){return be.current.useCallback(y,E)},re.useContext=function(y){return be.current.useContext(y)},re.useDebugValue=function(){},re.useDeferredValue=function(y){return be.current.useDeferredValue(y)},re.useEffect=function(y,E){return be.current.useEffect(y,E)},re.useId=function(){return be.current.useId()},re.useImperativeHandle=function(y,E,ne){return be.current.useImperativeHandle(y,E,ne)},re.useInsertionEffect=function(y,E){return be.current.useInsertionEffect(y,E)},re.useLayoutEffect=function(y,E){return be.current.useLayoutEffect(y,E)},re.useMemo=function(y,E){return be.current.useMemo(y,E)},re.useReducer=function(y,E,ne){return be.current.useReducer(y,E,ne)},re.useRef=function(y){return be.current.useRef(y)},re.useState=function(y){return be.current.useState(y)},re.useSyncExternalStore=function(y,E,ne){return be.current.useSyncExternalStore(y,E,ne)},re.useTransition=function(){return be.current.useTransition()},re.version="18.3.1",re}var pu;function go(){return pu||(pu=1,no.exports=Xm()),no.exports}/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var fu;function Ym(){if(fu)return Dr;fu=1;var o=go(),c=Symbol.for("react.element"),l=Symbol.for("react.fragment"),d=Object.prototype.hasOwnProperty,m=o.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,f={key:!0,ref:!0,__self:!0,__source:!0};function v(P,w,F){var N,C={},L=null,I=null;F!==void 0&&(L=""+F),w.key!==void 0&&(L=""+w.key),w.ref!==void 0&&(I=w.ref);for(N in w)d.call(w,N)&&!f.hasOwnProperty(N)&&(C[N]=w[N]);if(P&&P.defaultProps)for(N in w=P.defaultProps,w)C[N]===void 0&&(C[N]=w[N]);return{$$typeof:c,type:P,key:L,ref:I,props:C,_owner:m.current}}return Dr.Fragment=l,Dr.jsx=v,Dr.jsxs=v,Dr}var gu;function Jm(){return gu||(gu=1,to.exports=Ym()),to.exports}var r=Jm(),A=go(),Ks={},ro={exports:{}},Je={},so={exports:{}},ao={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var vu;function Zm(){return vu||(vu=1,(function(o){function c(O,Z){var V=O.length;O.push(Z);e:for(;0<V;){var y=V-1>>>1,E=O[y];if(0<m(E,Z))O[y]=Z,O[V]=E,V=y;else break e}}function l(O){return O.length===0?null:O[0]}function d(O){if(O.length===0)return null;var Z=O[0],V=O.pop();if(V!==Z){O[0]=V;e:for(var y=0,E=O.length,ne=E>>>1;y<ne;){var ae=2*(y+1)-1,le=O[ae],ce=ae+1,pe=O[ce];if(0>m(le,V))ce<E&&0>m(pe,le)?(O[y]=pe,O[ce]=V,y=ce):(O[y]=le,O[ae]=V,y=ae);else if(ce<E&&0>m(pe,V))O[y]=pe,O[ce]=V,y=ce;else break e}}return Z}function m(O,Z){var V=O.sortIndex-Z.sortIndex;return V!==0?V:O.id-Z.id}if(typeof performance=="object"&&typeof performance.now=="function"){var f=performance;o.unstable_now=function(){return f.now()}}else{var v=Date,P=v.now();o.unstable_now=function(){return v.now()-P}}var w=[],F=[],N=1,C=null,L=3,I=!1,z=!1,B=!1,b=typeof setTimeout=="function"?setTimeout:null,U=typeof clearTimeout=="function"?clearTimeout:null,S=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function Q(O){for(var Z=l(F);Z!==null;){if(Z.callback===null)d(F);else if(Z.startTime<=O)d(F),Z.sortIndex=Z.expirationTime,c(w,Z);else break;Z=l(F)}}function te(O){if(B=!1,Q(O),!z)if(l(w)!==null)z=!0,Ge(se);else{var Z=l(F);Z!==null&&be(te,Z.startTime-O)}}function se(O,Z){z=!1,B&&(B=!1,U(he),he=-1),I=!0;var V=L;try{for(Q(Z),C=l(w);C!==null&&(!(C.expirationTime>Z)||O&&!Ue());){var y=C.callback;if(typeof y=="function"){C.callback=null,L=C.priorityLevel;var E=y(C.expirationTime<=Z);Z=o.unstable_now(),typeof E=="function"?C.callback=E:C===l(w)&&d(w),Q(Z)}else d(w);C=l(w)}if(C!==null)var ne=!0;else{var ae=l(F);ae!==null&&be(te,ae.startTime-Z),ne=!1}return ne}finally{C=null,L=V,I=!1}}var _=!1,X=null,he=-1,je=5,st=-1;function Ue(){return!(o.unstable_now()-st<je)}function ze(){if(X!==null){var O=o.unstable_now();st=O;var Z=!0;try{Z=X(!0,O)}finally{Z?$e():(_=!1,X=null)}}else _=!1}var $e;if(typeof S=="function")$e=function(){S(ze)};else if(typeof MessageChannel<"u"){var at=new MessageChannel,St=at.port2;at.port1.onmessage=ze,$e=function(){St.postMessage(null)}}else $e=function(){b(ze,0)};function Ge(O){X=O,_||(_=!0,$e())}function be(O,Z){he=b(function(){O(o.unstable_now())},Z)}o.unstable_IdlePriority=5,o.unstable_ImmediatePriority=1,o.unstable_LowPriority=4,o.unstable_NormalPriority=3,o.unstable_Profiling=null,o.unstable_UserBlockingPriority=2,o.unstable_cancelCallback=function(O){O.callback=null},o.unstable_continueExecution=function(){z||I||(z=!0,Ge(se))},o.unstable_forceFrameRate=function(O){0>O||125<O?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):je=0<O?Math.floor(1e3/O):5},o.unstable_getCurrentPriorityLevel=function(){return L},o.unstable_getFirstCallbackNode=function(){return l(w)},o.unstable_next=function(O){switch(L){case 1:case 2:case 3:var Z=3;break;default:Z=L}var V=L;L=Z;try{return O()}finally{L=V}},o.unstable_pauseExecution=function(){},o.unstable_requestPaint=function(){},o.unstable_runWithPriority=function(O,Z){switch(O){case 1:case 2:case 3:case 4:case 5:break;default:O=3}var V=L;L=O;try{return Z()}finally{L=V}},o.unstable_scheduleCallback=function(O,Z,V){var y=o.unstable_now();switch(typeof V=="object"&&V!==null?(V=V.delay,V=typeof V=="number"&&0<V?y+V:y):V=y,O){case 1:var E=-1;break;case 2:E=250;break;case 5:E=1073741823;break;case 4:E=1e4;break;default:E=5e3}return E=V+E,O={id:N++,callback:Z,priorityLevel:O,startTime:V,expirationTime:E,sortIndex:-1},V>y?(O.sortIndex=V,c(F,O),l(w)===null&&O===l(F)&&(B?(U(he),he=-1):B=!0,be(te,V-y))):(O.sortIndex=E,c(w,O),z||I||(z=!0,Ge(se))),O},o.unstable_shouldYield=Ue,o.unstable_wrapCallback=function(O){var Z=L;return function(){var V=L;L=Z;try{return O.apply(this,arguments)}finally{L=V}}}})(ao)),ao}var yu;function eh(){return yu||(yu=1,so.exports=Zm()),so.exports}/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var xu;function th(){if(xu)return Je;xu=1;var o=go(),c=eh();function l(e){for(var t="https://reactjs.org/docs/error-decoder.html?invariant="+e,n=1;n<arguments.length;n++)t+="&args[]="+encodeURIComponent(arguments[n]);return"Minified React error #"+e+"; visit "+t+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var d=new Set,m={};function f(e,t){v(e,t),v(e+"Capture",t)}function v(e,t){for(m[e]=t,e=0;e<t.length;e++)d.add(t[e])}var P=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),w=Object.prototype.hasOwnProperty,F=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,N={},C={};function L(e){return w.call(C,e)?!0:w.call(N,e)?!1:F.test(e)?C[e]=!0:(N[e]=!0,!1)}function I(e,t,n,s){if(n!==null&&n.type===0)return!1;switch(typeof t){case"function":case"symbol":return!0;case"boolean":return s?!1:n!==null?!n.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function z(e,t,n,s){if(t===null||typeof t>"u"||I(e,t,n,s))return!0;if(s)return!1;if(n!==null)switch(n.type){case 3:return!t;case 4:return t===!1;case 5:return isNaN(t);case 6:return isNaN(t)||1>t}return!1}function B(e,t,n,s,a,i,u){this.acceptsBooleans=t===2||t===3||t===4,this.attributeName=s,this.attributeNamespace=a,this.mustUseProperty=n,this.propertyName=e,this.type=t,this.sanitizeURL=i,this.removeEmptyString=u}var b={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){b[e]=new B(e,0,!1,e,null,!1,!1)}),[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var t=e[0];b[t]=new B(t,1,!1,e[1],null,!1,!1)}),["contentEditable","draggable","spellCheck","value"].forEach(function(e){b[e]=new B(e,2,!1,e.toLowerCase(),null,!1,!1)}),["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){b[e]=new B(e,2,!1,e,null,!1,!1)}),"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){b[e]=new B(e,3,!1,e.toLowerCase(),null,!1,!1)}),["checked","multiple","muted","selected"].forEach(function(e){b[e]=new B(e,3,!0,e,null,!1,!1)}),["capture","download"].forEach(function(e){b[e]=new B(e,4,!1,e,null,!1,!1)}),["cols","rows","size","span"].forEach(function(e){b[e]=new B(e,6,!1,e,null,!1,!1)}),["rowSpan","start"].forEach(function(e){b[e]=new B(e,5,!1,e.toLowerCase(),null,!1,!1)});var U=/[\-:]([a-z])/g;function S(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var t=e.replace(U,S);b[t]=new B(t,1,!1,e,null,!1,!1)}),"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var t=e.replace(U,S);b[t]=new B(t,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)}),["xml:base","xml:lang","xml:space"].forEach(function(e){var t=e.replace(U,S);b[t]=new B(t,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)}),["tabIndex","crossOrigin"].forEach(function(e){b[e]=new B(e,1,!1,e.toLowerCase(),null,!1,!1)}),b.xlinkHref=new B("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1),["src","href","action","formAction"].forEach(function(e){b[e]=new B(e,1,!1,e.toLowerCase(),null,!0,!0)});function Q(e,t,n,s){var a=b.hasOwnProperty(t)?b[t]:null;(a!==null?a.type!==0:s||!(2<t.length)||t[0]!=="o"&&t[0]!=="O"||t[1]!=="n"&&t[1]!=="N")&&(z(t,n,a,s)&&(n=null),s||a===null?L(t)&&(n===null?e.removeAttribute(t):e.setAttribute(t,""+n)):a.mustUseProperty?e[a.propertyName]=n===null?a.type===3?!1:"":n:(t=a.attributeName,s=a.attributeNamespace,n===null?e.removeAttribute(t):(a=a.type,n=a===3||a===4&&n===!0?"":""+n,s?e.setAttributeNS(s,t,n):e.setAttribute(t,n))))}var te=o.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,se=Symbol.for("react.element"),_=Symbol.for("react.portal"),X=Symbol.for("react.fragment"),he=Symbol.for("react.strict_mode"),je=Symbol.for("react.profiler"),st=Symbol.for("react.provider"),Ue=Symbol.for("react.context"),ze=Symbol.for("react.forward_ref"),$e=Symbol.for("react.suspense"),at=Symbol.for("react.suspense_list"),St=Symbol.for("react.memo"),Ge=Symbol.for("react.lazy"),be=Symbol.for("react.offscreen"),O=Symbol.iterator;function Z(e){return e===null||typeof e!="object"?null:(e=O&&e[O]||e["@@iterator"],typeof e=="function"?e:null)}var V=Object.assign,y;function E(e){if(y===void 0)try{throw Error()}catch(n){var t=n.stack.trim().match(/\n( *(at )?)/);y=t&&t[1]||""}return`
`+y+e}var ne=!1;function ae(e,t){if(!e||ne)return"";ne=!0;var n=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(t)if(t=function(){throw Error()},Object.defineProperty(t.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(t,[])}catch(j){var s=j}Reflect.construct(e,[],t)}else{try{t.call()}catch(j){s=j}e.call(t.prototype)}else{try{throw Error()}catch(j){s=j}e()}}catch(j){if(j&&s&&typeof j.stack=="string"){for(var a=j.stack.split(`
`),i=s.stack.split(`
`),u=a.length-1,h=i.length-1;1<=u&&0<=h&&a[u]!==i[h];)h--;for(;1<=u&&0<=h;u--,h--)if(a[u]!==i[h]){if(u!==1||h!==1)do if(u--,h--,0>h||a[u]!==i[h]){var p=`
`+a[u].replace(" at new "," at ");return e.displayName&&p.includes("<anonymous>")&&(p=p.replace("<anonymous>",e.displayName)),p}while(1<=u&&0<=h);break}}}finally{ne=!1,Error.prepareStackTrace=n}return(e=e?e.displayName||e.name:"")?E(e):""}function le(e){switch(e.tag){case 5:return E(e.type);case 16:return E("Lazy");case 13:return E("Suspense");case 19:return E("SuspenseList");case 0:case 2:case 15:return e=ae(e.type,!1),e;case 11:return e=ae(e.type.render,!1),e;case 1:return e=ae(e.type,!0),e;default:return""}}function ce(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case X:return"Fragment";case _:return"Portal";case je:return"Profiler";case he:return"StrictMode";case $e:return"Suspense";case at:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case Ue:return(e.displayName||"Context")+".Consumer";case st:return(e._context.displayName||"Context")+".Provider";case ze:var t=e.render;return e=e.displayName,e||(e=t.displayName||t.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case St:return t=e.displayName||null,t!==null?t:ce(e.type)||"Memo";case Ge:t=e._payload,e=e._init;try{return ce(e(t))}catch{}}return null}function pe(e){var t=e.type;switch(e.tag){case 24:return"Cache";case 9:return(t.displayName||"Context")+".Consumer";case 10:return(t._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=t.render,e=e.displayName||e.name||"",t.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return t;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return ce(t);case 8:return t===he?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof t=="function")return t.displayName||t.name||null;if(typeof t=="string")return t}return null}function de(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function ye(e){var t=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(t==="checkbox"||t==="radio")}function it(e){var t=ye(e)?"checked":"value",n=Object.getOwnPropertyDescriptor(e.constructor.prototype,t),s=""+e[t];if(!e.hasOwnProperty(t)&&typeof n<"u"&&typeof n.get=="function"&&typeof n.set=="function"){var a=n.get,i=n.set;return Object.defineProperty(e,t,{configurable:!0,get:function(){return a.call(this)},set:function(u){s=""+u,i.call(this,u)}}),Object.defineProperty(e,t,{enumerable:n.enumerable}),{getValue:function(){return s},setValue:function(u){s=""+u},stopTracking:function(){e._valueTracker=null,delete e[t]}}}}function zr(e){e._valueTracker||(e._valueTracker=it(e))}function yo(e){if(!e)return!1;var t=e._valueTracker;if(!t)return!0;var n=t.getValue(),s="";return e&&(s=ye(e)?e.checked?"true":"false":e.value),e=s,e!==n?(t.setValue(e),!0):!1}function Fr(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function la(e,t){var n=t.checked;return V({},t,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:n??e._wrapperState.initialChecked})}function xo(e,t){var n=t.defaultValue==null?"":t.defaultValue,s=t.checked!=null?t.checked:t.defaultChecked;n=de(t.value!=null?t.value:n),e._wrapperState={initialChecked:s,initialValue:n,controlled:t.type==="checkbox"||t.type==="radio"?t.checked!=null:t.value!=null}}function ko(e,t){t=t.checked,t!=null&&Q(e,"checked",t,!1)}function ca(e,t){ko(e,t);var n=de(t.value),s=t.type;if(n!=null)s==="number"?(n===0&&e.value===""||e.value!=n)&&(e.value=""+n):e.value!==""+n&&(e.value=""+n);else if(s==="submit"||s==="reset"){e.removeAttribute("value");return}t.hasOwnProperty("value")?ua(e,t.type,n):t.hasOwnProperty("defaultValue")&&ua(e,t.type,de(t.defaultValue)),t.checked==null&&t.defaultChecked!=null&&(e.defaultChecked=!!t.defaultChecked)}function wo(e,t,n){if(t.hasOwnProperty("value")||t.hasOwnProperty("defaultValue")){var s=t.type;if(!(s!=="submit"&&s!=="reset"||t.value!==void 0&&t.value!==null))return;t=""+e._wrapperState.initialValue,n||t===e.value||(e.value=t),e.defaultValue=t}n=e.name,n!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,n!==""&&(e.name=n)}function ua(e,t,n){(t!=="number"||Fr(e.ownerDocument)!==e)&&(n==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+n&&(e.defaultValue=""+n))}var Xn=Array.isArray;function Nn(e,t,n,s){if(e=e.options,t){t={};for(var a=0;a<n.length;a++)t["$"+n[a]]=!0;for(n=0;n<e.length;n++)a=t.hasOwnProperty("$"+e[n].value),e[n].selected!==a&&(e[n].selected=a),a&&s&&(e[n].defaultSelected=!0)}else{for(n=""+de(n),t=null,a=0;a<e.length;a++){if(e[a].value===n){e[a].selected=!0,s&&(e[a].defaultSelected=!0);return}t!==null||e[a].disabled||(t=e[a])}t!==null&&(t.selected=!0)}}function da(e,t){if(t.dangerouslySetInnerHTML!=null)throw Error(l(91));return V({},t,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function jo(e,t){var n=t.value;if(n==null){if(n=t.children,t=t.defaultValue,n!=null){if(t!=null)throw Error(l(92));if(Xn(n)){if(1<n.length)throw Error(l(93));n=n[0]}t=n}t==null&&(t=""),n=t}e._wrapperState={initialValue:de(n)}}function bo(e,t){var n=de(t.value),s=de(t.defaultValue);n!=null&&(n=""+n,n!==e.value&&(e.value=n),t.defaultValue==null&&e.defaultValue!==n&&(e.defaultValue=n)),s!=null&&(e.defaultValue=""+s)}function So(e){var t=e.textContent;t===e._wrapperState.initialValue&&t!==""&&t!==null&&(e.value=t)}function No(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function ma(e,t){return e==null||e==="http://www.w3.org/1999/xhtml"?No(t):e==="http://www.w3.org/2000/svg"&&t==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var Br,Co=(function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(t,n,s,a){MSApp.execUnsafeLocalFunction(function(){return e(t,n,s,a)})}:e})(function(e,t){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=t;else{for(Br=Br||document.createElement("div"),Br.innerHTML="<svg>"+t.valueOf().toString()+"</svg>",t=Br.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;t.firstChild;)e.appendChild(t.firstChild)}});function Yn(e,t){if(t){var n=e.firstChild;if(n&&n===e.lastChild&&n.nodeType===3){n.nodeValue=t;return}}e.textContent=t}var Jn={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},Ju=["Webkit","ms","Moz","O"];Object.keys(Jn).forEach(function(e){Ju.forEach(function(t){t=t+e.charAt(0).toUpperCase()+e.substring(1),Jn[t]=Jn[e]})});function _o(e,t,n){return t==null||typeof t=="boolean"||t===""?"":n||typeof t!="number"||t===0||Jn.hasOwnProperty(e)&&Jn[e]?(""+t).trim():t+"px"}function To(e,t){e=e.style;for(var n in t)if(t.hasOwnProperty(n)){var s=n.indexOf("--")===0,a=_o(n,t[n],s);n==="float"&&(n="cssFloat"),s?e.setProperty(n,a):e[n]=a}}var Zu=V({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function ha(e,t){if(t){if(Zu[e]&&(t.children!=null||t.dangerouslySetInnerHTML!=null))throw Error(l(137,e));if(t.dangerouslySetInnerHTML!=null){if(t.children!=null)throw Error(l(60));if(typeof t.dangerouslySetInnerHTML!="object"||!("__html"in t.dangerouslySetInnerHTML))throw Error(l(61))}if(t.style!=null&&typeof t.style!="object")throw Error(l(62))}}function pa(e,t){if(e.indexOf("-")===-1)return typeof t.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var fa=null;function ga(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var va=null,Cn=null,_n=null;function Eo(e){if(e=kr(e)){if(typeof va!="function")throw Error(l(280));var t=e.stateNode;t&&(t=ls(t),va(e.stateNode,e.type,t))}}function Mo(e){Cn?_n?_n.push(e):_n=[e]:Cn=e}function Po(){if(Cn){var e=Cn,t=_n;if(_n=Cn=null,Eo(e),t)for(e=0;e<t.length;e++)Eo(t[e])}}function Lo(e,t){return e(t)}function Ro(){}var ya=!1;function Ao(e,t,n){if(ya)return e(t,n);ya=!0;try{return Lo(e,t,n)}finally{ya=!1,(Cn!==null||_n!==null)&&(Ro(),Po())}}function Zn(e,t){var n=e.stateNode;if(n===null)return null;var s=ls(n);if(s===null)return null;n=s[t];e:switch(t){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(s=!s.disabled)||(e=e.type,s=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!s;break e;default:e=!1}if(e)return null;if(n&&typeof n!="function")throw Error(l(231,t,typeof n));return n}var xa=!1;if(P)try{var er={};Object.defineProperty(er,"passive",{get:function(){xa=!0}}),window.addEventListener("test",er,er),window.removeEventListener("test",er,er)}catch{xa=!1}function ed(e,t,n,s,a,i,u,h,p){var j=Array.prototype.slice.call(arguments,3);try{t.apply(n,j)}catch(M){this.onError(M)}}var tr=!1,Or=null,Wr=!1,ka=null,td={onError:function(e){tr=!0,Or=e}};function nd(e,t,n,s,a,i,u,h,p){tr=!1,Or=null,ed.apply(td,arguments)}function rd(e,t,n,s,a,i,u,h,p){if(nd.apply(this,arguments),tr){if(tr){var j=Or;tr=!1,Or=null}else throw Error(l(198));Wr||(Wr=!0,ka=j)}}function ln(e){var t=e,n=e;if(e.alternate)for(;t.return;)t=t.return;else{e=t;do t=e,(t.flags&4098)!==0&&(n=t.return),e=t.return;while(e)}return t.tag===3?n:null}function Do(e){if(e.tag===13){var t=e.memoizedState;if(t===null&&(e=e.alternate,e!==null&&(t=e.memoizedState)),t!==null)return t.dehydrated}return null}function Io(e){if(ln(e)!==e)throw Error(l(188))}function sd(e){var t=e.alternate;if(!t){if(t=ln(e),t===null)throw Error(l(188));return t!==e?null:e}for(var n=e,s=t;;){var a=n.return;if(a===null)break;var i=a.alternate;if(i===null){if(s=a.return,s!==null){n=s;continue}break}if(a.child===i.child){for(i=a.child;i;){if(i===n)return Io(a),e;if(i===s)return Io(a),t;i=i.sibling}throw Error(l(188))}if(n.return!==s.return)n=a,s=i;else{for(var u=!1,h=a.child;h;){if(h===n){u=!0,n=a,s=i;break}if(h===s){u=!0,s=a,n=i;break}h=h.sibling}if(!u){for(h=i.child;h;){if(h===n){u=!0,n=i,s=a;break}if(h===s){u=!0,s=i,n=a;break}h=h.sibling}if(!u)throw Error(l(189))}}if(n.alternate!==s)throw Error(l(190))}if(n.tag!==3)throw Error(l(188));return n.stateNode.current===n?e:t}function zo(e){return e=sd(e),e!==null?Fo(e):null}function Fo(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var t=Fo(e);if(t!==null)return t;e=e.sibling}return null}var Bo=c.unstable_scheduleCallback,Oo=c.unstable_cancelCallback,ad=c.unstable_shouldYield,id=c.unstable_requestPaint,Ne=c.unstable_now,od=c.unstable_getCurrentPriorityLevel,wa=c.unstable_ImmediatePriority,Wo=c.unstable_UserBlockingPriority,Ur=c.unstable_NormalPriority,ld=c.unstable_LowPriority,Uo=c.unstable_IdlePriority,$r=null,Nt=null;function cd(e){if(Nt&&typeof Nt.onCommitFiberRoot=="function")try{Nt.onCommitFiberRoot($r,e,void 0,(e.current.flags&128)===128)}catch{}}var vt=Math.clz32?Math.clz32:md,ud=Math.log,dd=Math.LN2;function md(e){return e>>>=0,e===0?32:31-(ud(e)/dd|0)|0}var Vr=64,Hr=4194304;function nr(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function Gr(e,t){var n=e.pendingLanes;if(n===0)return 0;var s=0,a=e.suspendedLanes,i=e.pingedLanes,u=n&268435455;if(u!==0){var h=u&~a;h!==0?s=nr(h):(i&=u,i!==0&&(s=nr(i)))}else u=n&~a,u!==0?s=nr(u):i!==0&&(s=nr(i));if(s===0)return 0;if(t!==0&&t!==s&&(t&a)===0&&(a=s&-s,i=t&-t,a>=i||a===16&&(i&4194240)!==0))return t;if((s&4)!==0&&(s|=n&16),t=e.entangledLanes,t!==0)for(e=e.entanglements,t&=s;0<t;)n=31-vt(t),a=1<<n,s|=e[n],t&=~a;return s}function hd(e,t){switch(e){case 1:case 2:case 4:return t+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return t+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function pd(e,t){for(var n=e.suspendedLanes,s=e.pingedLanes,a=e.expirationTimes,i=e.pendingLanes;0<i;){var u=31-vt(i),h=1<<u,p=a[u];p===-1?((h&n)===0||(h&s)!==0)&&(a[u]=hd(h,t)):p<=t&&(e.expiredLanes|=h),i&=~h}}function ja(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function $o(){var e=Vr;return Vr<<=1,(Vr&4194240)===0&&(Vr=64),e}function ba(e){for(var t=[],n=0;31>n;n++)t.push(e);return t}function rr(e,t,n){e.pendingLanes|=t,t!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,t=31-vt(t),e[t]=n}function fd(e,t){var n=e.pendingLanes&~t;e.pendingLanes=t,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=t,e.mutableReadLanes&=t,e.entangledLanes&=t,t=e.entanglements;var s=e.eventTimes;for(e=e.expirationTimes;0<n;){var a=31-vt(n),i=1<<a;t[a]=0,s[a]=-1,e[a]=-1,n&=~i}}function Sa(e,t){var n=e.entangledLanes|=t;for(e=e.entanglements;n;){var s=31-vt(n),a=1<<s;a&t|e[s]&t&&(e[s]|=t),n&=~a}}var me=0;function Vo(e){return e&=-e,1<e?4<e?(e&268435455)!==0?16:536870912:4:1}var Ho,Na,Go,Ko,qo,Ca=!1,Kr=[],Ot=null,Wt=null,Ut=null,sr=new Map,ar=new Map,$t=[],gd="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function Qo(e,t){switch(e){case"focusin":case"focusout":Ot=null;break;case"dragenter":case"dragleave":Wt=null;break;case"mouseover":case"mouseout":Ut=null;break;case"pointerover":case"pointerout":sr.delete(t.pointerId);break;case"gotpointercapture":case"lostpointercapture":ar.delete(t.pointerId)}}function ir(e,t,n,s,a,i){return e===null||e.nativeEvent!==i?(e={blockedOn:t,domEventName:n,eventSystemFlags:s,nativeEvent:i,targetContainers:[a]},t!==null&&(t=kr(t),t!==null&&Na(t)),e):(e.eventSystemFlags|=s,t=e.targetContainers,a!==null&&t.indexOf(a)===-1&&t.push(a),e)}function vd(e,t,n,s,a){switch(t){case"focusin":return Ot=ir(Ot,e,t,n,s,a),!0;case"dragenter":return Wt=ir(Wt,e,t,n,s,a),!0;case"mouseover":return Ut=ir(Ut,e,t,n,s,a),!0;case"pointerover":var i=a.pointerId;return sr.set(i,ir(sr.get(i)||null,e,t,n,s,a)),!0;case"gotpointercapture":return i=a.pointerId,ar.set(i,ir(ar.get(i)||null,e,t,n,s,a)),!0}return!1}function Xo(e){var t=cn(e.target);if(t!==null){var n=ln(t);if(n!==null){if(t=n.tag,t===13){if(t=Do(n),t!==null){e.blockedOn=t,qo(e.priority,function(){Go(n)});return}}else if(t===3&&n.stateNode.current.memoizedState.isDehydrated){e.blockedOn=n.tag===3?n.stateNode.containerInfo:null;return}}}e.blockedOn=null}function qr(e){if(e.blockedOn!==null)return!1;for(var t=e.targetContainers;0<t.length;){var n=Ta(e.domEventName,e.eventSystemFlags,t[0],e.nativeEvent);if(n===null){n=e.nativeEvent;var s=new n.constructor(n.type,n);fa=s,n.target.dispatchEvent(s),fa=null}else return t=kr(n),t!==null&&Na(t),e.blockedOn=n,!1;t.shift()}return!0}function Yo(e,t,n){qr(e)&&n.delete(t)}function yd(){Ca=!1,Ot!==null&&qr(Ot)&&(Ot=null),Wt!==null&&qr(Wt)&&(Wt=null),Ut!==null&&qr(Ut)&&(Ut=null),sr.forEach(Yo),ar.forEach(Yo)}function or(e,t){e.blockedOn===t&&(e.blockedOn=null,Ca||(Ca=!0,c.unstable_scheduleCallback(c.unstable_NormalPriority,yd)))}function lr(e){function t(a){return or(a,e)}if(0<Kr.length){or(Kr[0],e);for(var n=1;n<Kr.length;n++){var s=Kr[n];s.blockedOn===e&&(s.blockedOn=null)}}for(Ot!==null&&or(Ot,e),Wt!==null&&or(Wt,e),Ut!==null&&or(Ut,e),sr.forEach(t),ar.forEach(t),n=0;n<$t.length;n++)s=$t[n],s.blockedOn===e&&(s.blockedOn=null);for(;0<$t.length&&(n=$t[0],n.blockedOn===null);)Xo(n),n.blockedOn===null&&$t.shift()}var Tn=te.ReactCurrentBatchConfig,Qr=!0;function xd(e,t,n,s){var a=me,i=Tn.transition;Tn.transition=null;try{me=1,_a(e,t,n,s)}finally{me=a,Tn.transition=i}}function kd(e,t,n,s){var a=me,i=Tn.transition;Tn.transition=null;try{me=4,_a(e,t,n,s)}finally{me=a,Tn.transition=i}}function _a(e,t,n,s){if(Qr){var a=Ta(e,t,n,s);if(a===null)Ha(e,t,s,Xr,n),Qo(e,s);else if(vd(a,e,t,n,s))s.stopPropagation();else if(Qo(e,s),t&4&&-1<gd.indexOf(e)){for(;a!==null;){var i=kr(a);if(i!==null&&Ho(i),i=Ta(e,t,n,s),i===null&&Ha(e,t,s,Xr,n),i===a)break;a=i}a!==null&&s.stopPropagation()}else Ha(e,t,s,null,n)}}var Xr=null;function Ta(e,t,n,s){if(Xr=null,e=ga(s),e=cn(e),e!==null)if(t=ln(e),t===null)e=null;else if(n=t.tag,n===13){if(e=Do(t),e!==null)return e;e=null}else if(n===3){if(t.stateNode.current.memoizedState.isDehydrated)return t.tag===3?t.stateNode.containerInfo:null;e=null}else t!==e&&(e=null);return Xr=e,null}function Jo(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(od()){case wa:return 1;case Wo:return 4;case Ur:case ld:return 16;case Uo:return 536870912;default:return 16}default:return 16}}var Vt=null,Ea=null,Yr=null;function Zo(){if(Yr)return Yr;var e,t=Ea,n=t.length,s,a="value"in Vt?Vt.value:Vt.textContent,i=a.length;for(e=0;e<n&&t[e]===a[e];e++);var u=n-e;for(s=1;s<=u&&t[n-s]===a[i-s];s++);return Yr=a.slice(e,1<s?1-s:void 0)}function Jr(e){var t=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&t===13&&(e=13)):e=t,e===10&&(e=13),32<=e||e===13?e:0}function Zr(){return!0}function el(){return!1}function ot(e){function t(n,s,a,i,u){this._reactName=n,this._targetInst=a,this.type=s,this.nativeEvent=i,this.target=u,this.currentTarget=null;for(var h in e)e.hasOwnProperty(h)&&(n=e[h],this[h]=n?n(i):i[h]);return this.isDefaultPrevented=(i.defaultPrevented!=null?i.defaultPrevented:i.returnValue===!1)?Zr:el,this.isPropagationStopped=el,this}return V(t.prototype,{preventDefault:function(){this.defaultPrevented=!0;var n=this.nativeEvent;n&&(n.preventDefault?n.preventDefault():typeof n.returnValue!="unknown"&&(n.returnValue=!1),this.isDefaultPrevented=Zr)},stopPropagation:function(){var n=this.nativeEvent;n&&(n.stopPropagation?n.stopPropagation():typeof n.cancelBubble!="unknown"&&(n.cancelBubble=!0),this.isPropagationStopped=Zr)},persist:function(){},isPersistent:Zr}),t}var En={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},Ma=ot(En),cr=V({},En,{view:0,detail:0}),wd=ot(cr),Pa,La,ur,es=V({},cr,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:Aa,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==ur&&(ur&&e.type==="mousemove"?(Pa=e.screenX-ur.screenX,La=e.screenY-ur.screenY):La=Pa=0,ur=e),Pa)},movementY:function(e){return"movementY"in e?e.movementY:La}}),tl=ot(es),jd=V({},es,{dataTransfer:0}),bd=ot(jd),Sd=V({},cr,{relatedTarget:0}),Ra=ot(Sd),Nd=V({},En,{animationName:0,elapsedTime:0,pseudoElement:0}),Cd=ot(Nd),_d=V({},En,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),Td=ot(_d),Ed=V({},En,{data:0}),nl=ot(Ed),Md={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},Pd={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},Ld={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function Rd(e){var t=this.nativeEvent;return t.getModifierState?t.getModifierState(e):(e=Ld[e])?!!t[e]:!1}function Aa(){return Rd}var Ad=V({},cr,{key:function(e){if(e.key){var t=Md[e.key]||e.key;if(t!=="Unidentified")return t}return e.type==="keypress"?(e=Jr(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?Pd[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:Aa,charCode:function(e){return e.type==="keypress"?Jr(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?Jr(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),Dd=ot(Ad),Id=V({},es,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),rl=ot(Id),zd=V({},cr,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:Aa}),Fd=ot(zd),Bd=V({},En,{propertyName:0,elapsedTime:0,pseudoElement:0}),Od=ot(Bd),Wd=V({},es,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),Ud=ot(Wd),$d=[9,13,27,32],Da=P&&"CompositionEvent"in window,dr=null;P&&"documentMode"in document&&(dr=document.documentMode);var Vd=P&&"TextEvent"in window&&!dr,sl=P&&(!Da||dr&&8<dr&&11>=dr),al=" ",il=!1;function ol(e,t){switch(e){case"keyup":return $d.indexOf(t.keyCode)!==-1;case"keydown":return t.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function ll(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var Mn=!1;function Hd(e,t){switch(e){case"compositionend":return ll(t);case"keypress":return t.which!==32?null:(il=!0,al);case"textInput":return e=t.data,e===al&&il?null:e;default:return null}}function Gd(e,t){if(Mn)return e==="compositionend"||!Da&&ol(e,t)?(e=Zo(),Yr=Ea=Vt=null,Mn=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(t.ctrlKey||t.altKey||t.metaKey)||t.ctrlKey&&t.altKey){if(t.char&&1<t.char.length)return t.char;if(t.which)return String.fromCharCode(t.which)}return null;case"compositionend":return sl&&t.locale!=="ko"?null:t.data;default:return null}}var Kd={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function cl(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t==="input"?!!Kd[e.type]:t==="textarea"}function ul(e,t,n,s){Mo(s),t=as(t,"onChange"),0<t.length&&(n=new Ma("onChange","change",null,n,s),e.push({event:n,listeners:t}))}var mr=null,hr=null;function qd(e){Tl(e,0)}function ts(e){var t=Dn(e);if(yo(t))return e}function Qd(e,t){if(e==="change")return t}var dl=!1;if(P){var Ia;if(P){var za="oninput"in document;if(!za){var ml=document.createElement("div");ml.setAttribute("oninput","return;"),za=typeof ml.oninput=="function"}Ia=za}else Ia=!1;dl=Ia&&(!document.documentMode||9<document.documentMode)}function hl(){mr&&(mr.detachEvent("onpropertychange",pl),hr=mr=null)}function pl(e){if(e.propertyName==="value"&&ts(hr)){var t=[];ul(t,hr,e,ga(e)),Ao(qd,t)}}function Xd(e,t,n){e==="focusin"?(hl(),mr=t,hr=n,mr.attachEvent("onpropertychange",pl)):e==="focusout"&&hl()}function Yd(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return ts(hr)}function Jd(e,t){if(e==="click")return ts(t)}function Zd(e,t){if(e==="input"||e==="change")return ts(t)}function em(e,t){return e===t&&(e!==0||1/e===1/t)||e!==e&&t!==t}var yt=typeof Object.is=="function"?Object.is:em;function pr(e,t){if(yt(e,t))return!0;if(typeof e!="object"||e===null||typeof t!="object"||t===null)return!1;var n=Object.keys(e),s=Object.keys(t);if(n.length!==s.length)return!1;for(s=0;s<n.length;s++){var a=n[s];if(!w.call(t,a)||!yt(e[a],t[a]))return!1}return!0}function fl(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function gl(e,t){var n=fl(e);e=0;for(var s;n;){if(n.nodeType===3){if(s=e+n.textContent.length,e<=t&&s>=t)return{node:n,offset:t-e};e=s}e:{for(;n;){if(n.nextSibling){n=n.nextSibling;break e}n=n.parentNode}n=void 0}n=fl(n)}}function vl(e,t){return e&&t?e===t?!0:e&&e.nodeType===3?!1:t&&t.nodeType===3?vl(e,t.parentNode):"contains"in e?e.contains(t):e.compareDocumentPosition?!!(e.compareDocumentPosition(t)&16):!1:!1}function yl(){for(var e=window,t=Fr();t instanceof e.HTMLIFrameElement;){try{var n=typeof t.contentWindow.location.href=="string"}catch{n=!1}if(n)e=t.contentWindow;else break;t=Fr(e.document)}return t}function Fa(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t&&(t==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||t==="textarea"||e.contentEditable==="true")}function tm(e){var t=yl(),n=e.focusedElem,s=e.selectionRange;if(t!==n&&n&&n.ownerDocument&&vl(n.ownerDocument.documentElement,n)){if(s!==null&&Fa(n)){if(t=s.start,e=s.end,e===void 0&&(e=t),"selectionStart"in n)n.selectionStart=t,n.selectionEnd=Math.min(e,n.value.length);else if(e=(t=n.ownerDocument||document)&&t.defaultView||window,e.getSelection){e=e.getSelection();var a=n.textContent.length,i=Math.min(s.start,a);s=s.end===void 0?i:Math.min(s.end,a),!e.extend&&i>s&&(a=s,s=i,i=a),a=gl(n,i);var u=gl(n,s);a&&u&&(e.rangeCount!==1||e.anchorNode!==a.node||e.anchorOffset!==a.offset||e.focusNode!==u.node||e.focusOffset!==u.offset)&&(t=t.createRange(),t.setStart(a.node,a.offset),e.removeAllRanges(),i>s?(e.addRange(t),e.extend(u.node,u.offset)):(t.setEnd(u.node,u.offset),e.addRange(t)))}}for(t=[],e=n;e=e.parentNode;)e.nodeType===1&&t.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof n.focus=="function"&&n.focus(),n=0;n<t.length;n++)e=t[n],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var nm=P&&"documentMode"in document&&11>=document.documentMode,Pn=null,Ba=null,fr=null,Oa=!1;function xl(e,t,n){var s=n.window===n?n.document:n.nodeType===9?n:n.ownerDocument;Oa||Pn==null||Pn!==Fr(s)||(s=Pn,"selectionStart"in s&&Fa(s)?s={start:s.selectionStart,end:s.selectionEnd}:(s=(s.ownerDocument&&s.ownerDocument.defaultView||window).getSelection(),s={anchorNode:s.anchorNode,anchorOffset:s.anchorOffset,focusNode:s.focusNode,focusOffset:s.focusOffset}),fr&&pr(fr,s)||(fr=s,s=as(Ba,"onSelect"),0<s.length&&(t=new Ma("onSelect","select",null,t,n),e.push({event:t,listeners:s}),t.target=Pn)))}function ns(e,t){var n={};return n[e.toLowerCase()]=t.toLowerCase(),n["Webkit"+e]="webkit"+t,n["Moz"+e]="moz"+t,n}var Ln={animationend:ns("Animation","AnimationEnd"),animationiteration:ns("Animation","AnimationIteration"),animationstart:ns("Animation","AnimationStart"),transitionend:ns("Transition","TransitionEnd")},Wa={},kl={};P&&(kl=document.createElement("div").style,"AnimationEvent"in window||(delete Ln.animationend.animation,delete Ln.animationiteration.animation,delete Ln.animationstart.animation),"TransitionEvent"in window||delete Ln.transitionend.transition);function rs(e){if(Wa[e])return Wa[e];if(!Ln[e])return e;var t=Ln[e],n;for(n in t)if(t.hasOwnProperty(n)&&n in kl)return Wa[e]=t[n];return e}var wl=rs("animationend"),jl=rs("animationiteration"),bl=rs("animationstart"),Sl=rs("transitionend"),Nl=new Map,Cl="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function Ht(e,t){Nl.set(e,t),f(t,[e])}for(var Ua=0;Ua<Cl.length;Ua++){var $a=Cl[Ua],rm=$a.toLowerCase(),sm=$a[0].toUpperCase()+$a.slice(1);Ht(rm,"on"+sm)}Ht(wl,"onAnimationEnd"),Ht(jl,"onAnimationIteration"),Ht(bl,"onAnimationStart"),Ht("dblclick","onDoubleClick"),Ht("focusin","onFocus"),Ht("focusout","onBlur"),Ht(Sl,"onTransitionEnd"),v("onMouseEnter",["mouseout","mouseover"]),v("onMouseLeave",["mouseout","mouseover"]),v("onPointerEnter",["pointerout","pointerover"]),v("onPointerLeave",["pointerout","pointerover"]),f("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),f("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),f("onBeforeInput",["compositionend","keypress","textInput","paste"]),f("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),f("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),f("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var gr="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),am=new Set("cancel close invalid load scroll toggle".split(" ").concat(gr));function _l(e,t,n){var s=e.type||"unknown-event";e.currentTarget=n,rd(s,t,void 0,e),e.currentTarget=null}function Tl(e,t){t=(t&4)!==0;for(var n=0;n<e.length;n++){var s=e[n],a=s.event;s=s.listeners;e:{var i=void 0;if(t)for(var u=s.length-1;0<=u;u--){var h=s[u],p=h.instance,j=h.currentTarget;if(h=h.listener,p!==i&&a.isPropagationStopped())break e;_l(a,h,j),i=p}else for(u=0;u<s.length;u++){if(h=s[u],p=h.instance,j=h.currentTarget,h=h.listener,p!==i&&a.isPropagationStopped())break e;_l(a,h,j),i=p}}}if(Wr)throw e=ka,Wr=!1,ka=null,e}function ge(e,t){var n=t[Ya];n===void 0&&(n=t[Ya]=new Set);var s=e+"__bubble";n.has(s)||(El(t,e,2,!1),n.add(s))}function Va(e,t,n){var s=0;t&&(s|=4),El(n,e,s,t)}var ss="_reactListening"+Math.random().toString(36).slice(2);function vr(e){if(!e[ss]){e[ss]=!0,d.forEach(function(n){n!=="selectionchange"&&(am.has(n)||Va(n,!1,e),Va(n,!0,e))});var t=e.nodeType===9?e:e.ownerDocument;t===null||t[ss]||(t[ss]=!0,Va("selectionchange",!1,t))}}function El(e,t,n,s){switch(Jo(t)){case 1:var a=xd;break;case 4:a=kd;break;default:a=_a}n=a.bind(null,t,n,e),a=void 0,!xa||t!=="touchstart"&&t!=="touchmove"&&t!=="wheel"||(a=!0),s?a!==void 0?e.addEventListener(t,n,{capture:!0,passive:a}):e.addEventListener(t,n,!0):a!==void 0?e.addEventListener(t,n,{passive:a}):e.addEventListener(t,n,!1)}function Ha(e,t,n,s,a){var i=s;if((t&1)===0&&(t&2)===0&&s!==null)e:for(;;){if(s===null)return;var u=s.tag;if(u===3||u===4){var h=s.stateNode.containerInfo;if(h===a||h.nodeType===8&&h.parentNode===a)break;if(u===4)for(u=s.return;u!==null;){var p=u.tag;if((p===3||p===4)&&(p=u.stateNode.containerInfo,p===a||p.nodeType===8&&p.parentNode===a))return;u=u.return}for(;h!==null;){if(u=cn(h),u===null)return;if(p=u.tag,p===5||p===6){s=i=u;continue e}h=h.parentNode}}s=s.return}Ao(function(){var j=i,M=ga(n),R=[];e:{var T=Nl.get(e);if(T!==void 0){var W=Ma,H=e;switch(e){case"keypress":if(Jr(n)===0)break e;case"keydown":case"keyup":W=Dd;break;case"focusin":H="focus",W=Ra;break;case"focusout":H="blur",W=Ra;break;case"beforeblur":case"afterblur":W=Ra;break;case"click":if(n.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":W=tl;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":W=bd;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":W=Fd;break;case wl:case jl:case bl:W=Cd;break;case Sl:W=Od;break;case"scroll":W=wd;break;case"wheel":W=Ud;break;case"copy":case"cut":case"paste":W=Td;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":W=rl}var G=(t&4)!==0,Ce=!G&&e==="scroll",x=G?T!==null?T+"Capture":null:T;G=[];for(var g=j,k;g!==null;){k=g;var D=k.stateNode;if(k.tag===5&&D!==null&&(k=D,x!==null&&(D=Zn(g,x),D!=null&&G.push(yr(g,D,k)))),Ce)break;g=g.return}0<G.length&&(T=new W(T,H,null,n,M),R.push({event:T,listeners:G}))}}if((t&7)===0){e:{if(T=e==="mouseover"||e==="pointerover",W=e==="mouseout"||e==="pointerout",T&&n!==fa&&(H=n.relatedTarget||n.fromElement)&&(cn(H)||H[Pt]))break e;if((W||T)&&(T=M.window===M?M:(T=M.ownerDocument)?T.defaultView||T.parentWindow:window,W?(H=n.relatedTarget||n.toElement,W=j,H=H?cn(H):null,H!==null&&(Ce=ln(H),H!==Ce||H.tag!==5&&H.tag!==6)&&(H=null)):(W=null,H=j),W!==H)){if(G=tl,D="onMouseLeave",x="onMouseEnter",g="mouse",(e==="pointerout"||e==="pointerover")&&(G=rl,D="onPointerLeave",x="onPointerEnter",g="pointer"),Ce=W==null?T:Dn(W),k=H==null?T:Dn(H),T=new G(D,g+"leave",W,n,M),T.target=Ce,T.relatedTarget=k,D=null,cn(M)===j&&(G=new G(x,g+"enter",H,n,M),G.target=k,G.relatedTarget=Ce,D=G),Ce=D,W&&H)t:{for(G=W,x=H,g=0,k=G;k;k=Rn(k))g++;for(k=0,D=x;D;D=Rn(D))k++;for(;0<g-k;)G=Rn(G),g--;for(;0<k-g;)x=Rn(x),k--;for(;g--;){if(G===x||x!==null&&G===x.alternate)break t;G=Rn(G),x=Rn(x)}G=null}else G=null;W!==null&&Ml(R,T,W,G,!1),H!==null&&Ce!==null&&Ml(R,Ce,H,G,!0)}}e:{if(T=j?Dn(j):window,W=T.nodeName&&T.nodeName.toLowerCase(),W==="select"||W==="input"&&T.type==="file")var K=Qd;else if(cl(T))if(dl)K=Zd;else{K=Yd;var Y=Xd}else(W=T.nodeName)&&W.toLowerCase()==="input"&&(T.type==="checkbox"||T.type==="radio")&&(K=Jd);if(K&&(K=K(e,j))){ul(R,K,n,M);break e}Y&&Y(e,T,j),e==="focusout"&&(Y=T._wrapperState)&&Y.controlled&&T.type==="number"&&ua(T,"number",T.value)}switch(Y=j?Dn(j):window,e){case"focusin":(cl(Y)||Y.contentEditable==="true")&&(Pn=Y,Ba=j,fr=null);break;case"focusout":fr=Ba=Pn=null;break;case"mousedown":Oa=!0;break;case"contextmenu":case"mouseup":case"dragend":Oa=!1,xl(R,n,M);break;case"selectionchange":if(nm)break;case"keydown":case"keyup":xl(R,n,M)}var J;if(Da)e:{switch(e){case"compositionstart":var ee="onCompositionStart";break e;case"compositionend":ee="onCompositionEnd";break e;case"compositionupdate":ee="onCompositionUpdate";break e}ee=void 0}else Mn?ol(e,n)&&(ee="onCompositionEnd"):e==="keydown"&&n.keyCode===229&&(ee="onCompositionStart");ee&&(sl&&n.locale!=="ko"&&(Mn||ee!=="onCompositionStart"?ee==="onCompositionEnd"&&Mn&&(J=Zo()):(Vt=M,Ea="value"in Vt?Vt.value:Vt.textContent,Mn=!0)),Y=as(j,ee),0<Y.length&&(ee=new nl(ee,e,null,n,M),R.push({event:ee,listeners:Y}),J?ee.data=J:(J=ll(n),J!==null&&(ee.data=J)))),(J=Vd?Hd(e,n):Gd(e,n))&&(j=as(j,"onBeforeInput"),0<j.length&&(M=new nl("onBeforeInput","beforeinput",null,n,M),R.push({event:M,listeners:j}),M.data=J))}Tl(R,t)})}function yr(e,t,n){return{instance:e,listener:t,currentTarget:n}}function as(e,t){for(var n=t+"Capture",s=[];e!==null;){var a=e,i=a.stateNode;a.tag===5&&i!==null&&(a=i,i=Zn(e,n),i!=null&&s.unshift(yr(e,i,a)),i=Zn(e,t),i!=null&&s.push(yr(e,i,a))),e=e.return}return s}function Rn(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function Ml(e,t,n,s,a){for(var i=t._reactName,u=[];n!==null&&n!==s;){var h=n,p=h.alternate,j=h.stateNode;if(p!==null&&p===s)break;h.tag===5&&j!==null&&(h=j,a?(p=Zn(n,i),p!=null&&u.unshift(yr(n,p,h))):a||(p=Zn(n,i),p!=null&&u.push(yr(n,p,h)))),n=n.return}u.length!==0&&e.push({event:t,listeners:u})}var im=/\r\n?/g,om=/\u0000|\uFFFD/g;function Pl(e){return(typeof e=="string"?e:""+e).replace(im,`
`).replace(om,"")}function is(e,t,n){if(t=Pl(t),Pl(e)!==t&&n)throw Error(l(425))}function os(){}var Ga=null,Ka=null;function qa(e,t){return e==="textarea"||e==="noscript"||typeof t.children=="string"||typeof t.children=="number"||typeof t.dangerouslySetInnerHTML=="object"&&t.dangerouslySetInnerHTML!==null&&t.dangerouslySetInnerHTML.__html!=null}var Qa=typeof setTimeout=="function"?setTimeout:void 0,lm=typeof clearTimeout=="function"?clearTimeout:void 0,Ll=typeof Promise=="function"?Promise:void 0,cm=typeof queueMicrotask=="function"?queueMicrotask:typeof Ll<"u"?function(e){return Ll.resolve(null).then(e).catch(um)}:Qa;function um(e){setTimeout(function(){throw e})}function Xa(e,t){var n=t,s=0;do{var a=n.nextSibling;if(e.removeChild(n),a&&a.nodeType===8)if(n=a.data,n==="/$"){if(s===0){e.removeChild(a),lr(t);return}s--}else n!=="$"&&n!=="$?"&&n!=="$!"||s++;n=a}while(n);lr(t)}function Gt(e){for(;e!=null;e=e.nextSibling){var t=e.nodeType;if(t===1||t===3)break;if(t===8){if(t=e.data,t==="$"||t==="$!"||t==="$?")break;if(t==="/$")return null}}return e}function Rl(e){e=e.previousSibling;for(var t=0;e;){if(e.nodeType===8){var n=e.data;if(n==="$"||n==="$!"||n==="$?"){if(t===0)return e;t--}else n==="/$"&&t++}e=e.previousSibling}return null}var An=Math.random().toString(36).slice(2),Ct="__reactFiber$"+An,xr="__reactProps$"+An,Pt="__reactContainer$"+An,Ya="__reactEvents$"+An,dm="__reactListeners$"+An,mm="__reactHandles$"+An;function cn(e){var t=e[Ct];if(t)return t;for(var n=e.parentNode;n;){if(t=n[Pt]||n[Ct]){if(n=t.alternate,t.child!==null||n!==null&&n.child!==null)for(e=Rl(e);e!==null;){if(n=e[Ct])return n;e=Rl(e)}return t}e=n,n=e.parentNode}return null}function kr(e){return e=e[Ct]||e[Pt],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function Dn(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(l(33))}function ls(e){return e[xr]||null}var Ja=[],In=-1;function Kt(e){return{current:e}}function ve(e){0>In||(e.current=Ja[In],Ja[In]=null,In--)}function fe(e,t){In++,Ja[In]=e.current,e.current=t}var qt={},Fe=Kt(qt),Ke=Kt(!1),un=qt;function zn(e,t){var n=e.type.contextTypes;if(!n)return qt;var s=e.stateNode;if(s&&s.__reactInternalMemoizedUnmaskedChildContext===t)return s.__reactInternalMemoizedMaskedChildContext;var a={},i;for(i in n)a[i]=t[i];return s&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=t,e.__reactInternalMemoizedMaskedChildContext=a),a}function qe(e){return e=e.childContextTypes,e!=null}function cs(){ve(Ke),ve(Fe)}function Al(e,t,n){if(Fe.current!==qt)throw Error(l(168));fe(Fe,t),fe(Ke,n)}function Dl(e,t,n){var s=e.stateNode;if(t=t.childContextTypes,typeof s.getChildContext!="function")return n;s=s.getChildContext();for(var a in s)if(!(a in t))throw Error(l(108,pe(e)||"Unknown",a));return V({},n,s)}function us(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||qt,un=Fe.current,fe(Fe,e),fe(Ke,Ke.current),!0}function Il(e,t,n){var s=e.stateNode;if(!s)throw Error(l(169));n?(e=Dl(e,t,un),s.__reactInternalMemoizedMergedChildContext=e,ve(Ke),ve(Fe),fe(Fe,e)):ve(Ke),fe(Ke,n)}var Lt=null,ds=!1,Za=!1;function zl(e){Lt===null?Lt=[e]:Lt.push(e)}function hm(e){ds=!0,zl(e)}function Qt(){if(!Za&&Lt!==null){Za=!0;var e=0,t=me;try{var n=Lt;for(me=1;e<n.length;e++){var s=n[e];do s=s(!0);while(s!==null)}Lt=null,ds=!1}catch(a){throw Lt!==null&&(Lt=Lt.slice(e+1)),Bo(wa,Qt),a}finally{me=t,Za=!1}}return null}var Fn=[],Bn=0,ms=null,hs=0,dt=[],mt=0,dn=null,Rt=1,At="";function mn(e,t){Fn[Bn++]=hs,Fn[Bn++]=ms,ms=e,hs=t}function Fl(e,t,n){dt[mt++]=Rt,dt[mt++]=At,dt[mt++]=dn,dn=e;var s=Rt;e=At;var a=32-vt(s)-1;s&=~(1<<a),n+=1;var i=32-vt(t)+a;if(30<i){var u=a-a%5;i=(s&(1<<u)-1).toString(32),s>>=u,a-=u,Rt=1<<32-vt(t)+a|n<<a|s,At=i+e}else Rt=1<<i|n<<a|s,At=e}function ei(e){e.return!==null&&(mn(e,1),Fl(e,1,0))}function ti(e){for(;e===ms;)ms=Fn[--Bn],Fn[Bn]=null,hs=Fn[--Bn],Fn[Bn]=null;for(;e===dn;)dn=dt[--mt],dt[mt]=null,At=dt[--mt],dt[mt]=null,Rt=dt[--mt],dt[mt]=null}var lt=null,ct=null,xe=!1,xt=null;function Bl(e,t){var n=gt(5,null,null,0);n.elementType="DELETED",n.stateNode=t,n.return=e,t=e.deletions,t===null?(e.deletions=[n],e.flags|=16):t.push(n)}function Ol(e,t){switch(e.tag){case 5:var n=e.type;return t=t.nodeType!==1||n.toLowerCase()!==t.nodeName.toLowerCase()?null:t,t!==null?(e.stateNode=t,lt=e,ct=Gt(t.firstChild),!0):!1;case 6:return t=e.pendingProps===""||t.nodeType!==3?null:t,t!==null?(e.stateNode=t,lt=e,ct=null,!0):!1;case 13:return t=t.nodeType!==8?null:t,t!==null?(n=dn!==null?{id:Rt,overflow:At}:null,e.memoizedState={dehydrated:t,treeContext:n,retryLane:1073741824},n=gt(18,null,null,0),n.stateNode=t,n.return=e,e.child=n,lt=e,ct=null,!0):!1;default:return!1}}function ni(e){return(e.mode&1)!==0&&(e.flags&128)===0}function ri(e){if(xe){var t=ct;if(t){var n=t;if(!Ol(e,t)){if(ni(e))throw Error(l(418));t=Gt(n.nextSibling);var s=lt;t&&Ol(e,t)?Bl(s,n):(e.flags=e.flags&-4097|2,xe=!1,lt=e)}}else{if(ni(e))throw Error(l(418));e.flags=e.flags&-4097|2,xe=!1,lt=e}}}function Wl(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;lt=e}function ps(e){if(e!==lt)return!1;if(!xe)return Wl(e),xe=!0,!1;var t;if((t=e.tag!==3)&&!(t=e.tag!==5)&&(t=e.type,t=t!=="head"&&t!=="body"&&!qa(e.type,e.memoizedProps)),t&&(t=ct)){if(ni(e))throw Ul(),Error(l(418));for(;t;)Bl(e,t),t=Gt(t.nextSibling)}if(Wl(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(l(317));e:{for(e=e.nextSibling,t=0;e;){if(e.nodeType===8){var n=e.data;if(n==="/$"){if(t===0){ct=Gt(e.nextSibling);break e}t--}else n!=="$"&&n!=="$!"&&n!=="$?"||t++}e=e.nextSibling}ct=null}}else ct=lt?Gt(e.stateNode.nextSibling):null;return!0}function Ul(){for(var e=ct;e;)e=Gt(e.nextSibling)}function On(){ct=lt=null,xe=!1}function si(e){xt===null?xt=[e]:xt.push(e)}var pm=te.ReactCurrentBatchConfig;function wr(e,t,n){if(e=n.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(n._owner){if(n=n._owner,n){if(n.tag!==1)throw Error(l(309));var s=n.stateNode}if(!s)throw Error(l(147,e));var a=s,i=""+e;return t!==null&&t.ref!==null&&typeof t.ref=="function"&&t.ref._stringRef===i?t.ref:(t=function(u){var h=a.refs;u===null?delete h[i]:h[i]=u},t._stringRef=i,t)}if(typeof e!="string")throw Error(l(284));if(!n._owner)throw Error(l(290,e))}return e}function fs(e,t){throw e=Object.prototype.toString.call(t),Error(l(31,e==="[object Object]"?"object with keys {"+Object.keys(t).join(", ")+"}":e))}function $l(e){var t=e._init;return t(e._payload)}function Vl(e){function t(x,g){if(e){var k=x.deletions;k===null?(x.deletions=[g],x.flags|=16):k.push(g)}}function n(x,g){if(!e)return null;for(;g!==null;)t(x,g),g=g.sibling;return null}function s(x,g){for(x=new Map;g!==null;)g.key!==null?x.set(g.key,g):x.set(g.index,g),g=g.sibling;return x}function a(x,g){return x=rn(x,g),x.index=0,x.sibling=null,x}function i(x,g,k){return x.index=k,e?(k=x.alternate,k!==null?(k=k.index,k<g?(x.flags|=2,g):k):(x.flags|=2,g)):(x.flags|=1048576,g)}function u(x){return e&&x.alternate===null&&(x.flags|=2),x}function h(x,g,k,D){return g===null||g.tag!==6?(g=Qi(k,x.mode,D),g.return=x,g):(g=a(g,k),g.return=x,g)}function p(x,g,k,D){var K=k.type;return K===X?M(x,g,k.props.children,D,k.key):g!==null&&(g.elementType===K||typeof K=="object"&&K!==null&&K.$$typeof===Ge&&$l(K)===g.type)?(D=a(g,k.props),D.ref=wr(x,g,k),D.return=x,D):(D=Bs(k.type,k.key,k.props,null,x.mode,D),D.ref=wr(x,g,k),D.return=x,D)}function j(x,g,k,D){return g===null||g.tag!==4||g.stateNode.containerInfo!==k.containerInfo||g.stateNode.implementation!==k.implementation?(g=Xi(k,x.mode,D),g.return=x,g):(g=a(g,k.children||[]),g.return=x,g)}function M(x,g,k,D,K){return g===null||g.tag!==7?(g=kn(k,x.mode,D,K),g.return=x,g):(g=a(g,k),g.return=x,g)}function R(x,g,k){if(typeof g=="string"&&g!==""||typeof g=="number")return g=Qi(""+g,x.mode,k),g.return=x,g;if(typeof g=="object"&&g!==null){switch(g.$$typeof){case se:return k=Bs(g.type,g.key,g.props,null,x.mode,k),k.ref=wr(x,null,g),k.return=x,k;case _:return g=Xi(g,x.mode,k),g.return=x,g;case Ge:var D=g._init;return R(x,D(g._payload),k)}if(Xn(g)||Z(g))return g=kn(g,x.mode,k,null),g.return=x,g;fs(x,g)}return null}function T(x,g,k,D){var K=g!==null?g.key:null;if(typeof k=="string"&&k!==""||typeof k=="number")return K!==null?null:h(x,g,""+k,D);if(typeof k=="object"&&k!==null){switch(k.$$typeof){case se:return k.key===K?p(x,g,k,D):null;case _:return k.key===K?j(x,g,k,D):null;case Ge:return K=k._init,T(x,g,K(k._payload),D)}if(Xn(k)||Z(k))return K!==null?null:M(x,g,k,D,null);fs(x,k)}return null}function W(x,g,k,D,K){if(typeof D=="string"&&D!==""||typeof D=="number")return x=x.get(k)||null,h(g,x,""+D,K);if(typeof D=="object"&&D!==null){switch(D.$$typeof){case se:return x=x.get(D.key===null?k:D.key)||null,p(g,x,D,K);case _:return x=x.get(D.key===null?k:D.key)||null,j(g,x,D,K);case Ge:var Y=D._init;return W(x,g,k,Y(D._payload),K)}if(Xn(D)||Z(D))return x=x.get(k)||null,M(g,x,D,K,null);fs(g,D)}return null}function H(x,g,k,D){for(var K=null,Y=null,J=g,ee=g=0,Ae=null;J!==null&&ee<k.length;ee++){J.index>ee?(Ae=J,J=null):Ae=J.sibling;var ue=T(x,J,k[ee],D);if(ue===null){J===null&&(J=Ae);break}e&&J&&ue.alternate===null&&t(x,J),g=i(ue,g,ee),Y===null?K=ue:Y.sibling=ue,Y=ue,J=Ae}if(ee===k.length)return n(x,J),xe&&mn(x,ee),K;if(J===null){for(;ee<k.length;ee++)J=R(x,k[ee],D),J!==null&&(g=i(J,g,ee),Y===null?K=J:Y.sibling=J,Y=J);return xe&&mn(x,ee),K}for(J=s(x,J);ee<k.length;ee++)Ae=W(J,x,ee,k[ee],D),Ae!==null&&(e&&Ae.alternate!==null&&J.delete(Ae.key===null?ee:Ae.key),g=i(Ae,g,ee),Y===null?K=Ae:Y.sibling=Ae,Y=Ae);return e&&J.forEach(function(sn){return t(x,sn)}),xe&&mn(x,ee),K}function G(x,g,k,D){var K=Z(k);if(typeof K!="function")throw Error(l(150));if(k=K.call(k),k==null)throw Error(l(151));for(var Y=K=null,J=g,ee=g=0,Ae=null,ue=k.next();J!==null&&!ue.done;ee++,ue=k.next()){J.index>ee?(Ae=J,J=null):Ae=J.sibling;var sn=T(x,J,ue.value,D);if(sn===null){J===null&&(J=Ae);break}e&&J&&sn.alternate===null&&t(x,J),g=i(sn,g,ee),Y===null?K=sn:Y.sibling=sn,Y=sn,J=Ae}if(ue.done)return n(x,J),xe&&mn(x,ee),K;if(J===null){for(;!ue.done;ee++,ue=k.next())ue=R(x,ue.value,D),ue!==null&&(g=i(ue,g,ee),Y===null?K=ue:Y.sibling=ue,Y=ue);return xe&&mn(x,ee),K}for(J=s(x,J);!ue.done;ee++,ue=k.next())ue=W(J,x,ee,ue.value,D),ue!==null&&(e&&ue.alternate!==null&&J.delete(ue.key===null?ee:ue.key),g=i(ue,g,ee),Y===null?K=ue:Y.sibling=ue,Y=ue);return e&&J.forEach(function(Km){return t(x,Km)}),xe&&mn(x,ee),K}function Ce(x,g,k,D){if(typeof k=="object"&&k!==null&&k.type===X&&k.key===null&&(k=k.props.children),typeof k=="object"&&k!==null){switch(k.$$typeof){case se:e:{for(var K=k.key,Y=g;Y!==null;){if(Y.key===K){if(K=k.type,K===X){if(Y.tag===7){n(x,Y.sibling),g=a(Y,k.props.children),g.return=x,x=g;break e}}else if(Y.elementType===K||typeof K=="object"&&K!==null&&K.$$typeof===Ge&&$l(K)===Y.type){n(x,Y.sibling),g=a(Y,k.props),g.ref=wr(x,Y,k),g.return=x,x=g;break e}n(x,Y);break}else t(x,Y);Y=Y.sibling}k.type===X?(g=kn(k.props.children,x.mode,D,k.key),g.return=x,x=g):(D=Bs(k.type,k.key,k.props,null,x.mode,D),D.ref=wr(x,g,k),D.return=x,x=D)}return u(x);case _:e:{for(Y=k.key;g!==null;){if(g.key===Y)if(g.tag===4&&g.stateNode.containerInfo===k.containerInfo&&g.stateNode.implementation===k.implementation){n(x,g.sibling),g=a(g,k.children||[]),g.return=x,x=g;break e}else{n(x,g);break}else t(x,g);g=g.sibling}g=Xi(k,x.mode,D),g.return=x,x=g}return u(x);case Ge:return Y=k._init,Ce(x,g,Y(k._payload),D)}if(Xn(k))return H(x,g,k,D);if(Z(k))return G(x,g,k,D);fs(x,k)}return typeof k=="string"&&k!==""||typeof k=="number"?(k=""+k,g!==null&&g.tag===6?(n(x,g.sibling),g=a(g,k),g.return=x,x=g):(n(x,g),g=Qi(k,x.mode,D),g.return=x,x=g),u(x)):n(x,g)}return Ce}var Wn=Vl(!0),Hl=Vl(!1),gs=Kt(null),vs=null,Un=null,ai=null;function ii(){ai=Un=vs=null}function oi(e){var t=gs.current;ve(gs),e._currentValue=t}function li(e,t,n){for(;e!==null;){var s=e.alternate;if((e.childLanes&t)!==t?(e.childLanes|=t,s!==null&&(s.childLanes|=t)):s!==null&&(s.childLanes&t)!==t&&(s.childLanes|=t),e===n)break;e=e.return}}function $n(e,t){vs=e,ai=Un=null,e=e.dependencies,e!==null&&e.firstContext!==null&&((e.lanes&t)!==0&&(Qe=!0),e.firstContext=null)}function ht(e){var t=e._currentValue;if(ai!==e)if(e={context:e,memoizedValue:t,next:null},Un===null){if(vs===null)throw Error(l(308));Un=e,vs.dependencies={lanes:0,firstContext:e}}else Un=Un.next=e;return t}var hn=null;function ci(e){hn===null?hn=[e]:hn.push(e)}function Gl(e,t,n,s){var a=t.interleaved;return a===null?(n.next=n,ci(t)):(n.next=a.next,a.next=n),t.interleaved=n,Dt(e,s)}function Dt(e,t){e.lanes|=t;var n=e.alternate;for(n!==null&&(n.lanes|=t),n=e,e=e.return;e!==null;)e.childLanes|=t,n=e.alternate,n!==null&&(n.childLanes|=t),n=e,e=e.return;return n.tag===3?n.stateNode:null}var Xt=!1;function ui(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function Kl(e,t){e=e.updateQueue,t.updateQueue===e&&(t.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function It(e,t){return{eventTime:e,lane:t,tag:0,payload:null,callback:null,next:null}}function Yt(e,t,n){var s=e.updateQueue;if(s===null)return null;if(s=s.shared,(oe&2)!==0){var a=s.pending;return a===null?t.next=t:(t.next=a.next,a.next=t),s.pending=t,Dt(e,n)}return a=s.interleaved,a===null?(t.next=t,ci(s)):(t.next=a.next,a.next=t),s.interleaved=t,Dt(e,n)}function ys(e,t,n){if(t=t.updateQueue,t!==null&&(t=t.shared,(n&4194240)!==0)){var s=t.lanes;s&=e.pendingLanes,n|=s,t.lanes=n,Sa(e,n)}}function ql(e,t){var n=e.updateQueue,s=e.alternate;if(s!==null&&(s=s.updateQueue,n===s)){var a=null,i=null;if(n=n.firstBaseUpdate,n!==null){do{var u={eventTime:n.eventTime,lane:n.lane,tag:n.tag,payload:n.payload,callback:n.callback,next:null};i===null?a=i=u:i=i.next=u,n=n.next}while(n!==null);i===null?a=i=t:i=i.next=t}else a=i=t;n={baseState:s.baseState,firstBaseUpdate:a,lastBaseUpdate:i,shared:s.shared,effects:s.effects},e.updateQueue=n;return}e=n.lastBaseUpdate,e===null?n.firstBaseUpdate=t:e.next=t,n.lastBaseUpdate=t}function xs(e,t,n,s){var a=e.updateQueue;Xt=!1;var i=a.firstBaseUpdate,u=a.lastBaseUpdate,h=a.shared.pending;if(h!==null){a.shared.pending=null;var p=h,j=p.next;p.next=null,u===null?i=j:u.next=j,u=p;var M=e.alternate;M!==null&&(M=M.updateQueue,h=M.lastBaseUpdate,h!==u&&(h===null?M.firstBaseUpdate=j:h.next=j,M.lastBaseUpdate=p))}if(i!==null){var R=a.baseState;u=0,M=j=p=null,h=i;do{var T=h.lane,W=h.eventTime;if((s&T)===T){M!==null&&(M=M.next={eventTime:W,lane:0,tag:h.tag,payload:h.payload,callback:h.callback,next:null});e:{var H=e,G=h;switch(T=t,W=n,G.tag){case 1:if(H=G.payload,typeof H=="function"){R=H.call(W,R,T);break e}R=H;break e;case 3:H.flags=H.flags&-65537|128;case 0:if(H=G.payload,T=typeof H=="function"?H.call(W,R,T):H,T==null)break e;R=V({},R,T);break e;case 2:Xt=!0}}h.callback!==null&&h.lane!==0&&(e.flags|=64,T=a.effects,T===null?a.effects=[h]:T.push(h))}else W={eventTime:W,lane:T,tag:h.tag,payload:h.payload,callback:h.callback,next:null},M===null?(j=M=W,p=R):M=M.next=W,u|=T;if(h=h.next,h===null){if(h=a.shared.pending,h===null)break;T=h,h=T.next,T.next=null,a.lastBaseUpdate=T,a.shared.pending=null}}while(!0);if(M===null&&(p=R),a.baseState=p,a.firstBaseUpdate=j,a.lastBaseUpdate=M,t=a.shared.interleaved,t!==null){a=t;do u|=a.lane,a=a.next;while(a!==t)}else i===null&&(a.shared.lanes=0);gn|=u,e.lanes=u,e.memoizedState=R}}function Ql(e,t,n){if(e=t.effects,t.effects=null,e!==null)for(t=0;t<e.length;t++){var s=e[t],a=s.callback;if(a!==null){if(s.callback=null,s=n,typeof a!="function")throw Error(l(191,a));a.call(s)}}}var jr={},_t=Kt(jr),br=Kt(jr),Sr=Kt(jr);function pn(e){if(e===jr)throw Error(l(174));return e}function di(e,t){switch(fe(Sr,t),fe(br,e),fe(_t,jr),e=t.nodeType,e){case 9:case 11:t=(t=t.documentElement)?t.namespaceURI:ma(null,"");break;default:e=e===8?t.parentNode:t,t=e.namespaceURI||null,e=e.tagName,t=ma(t,e)}ve(_t),fe(_t,t)}function Vn(){ve(_t),ve(br),ve(Sr)}function Xl(e){pn(Sr.current);var t=pn(_t.current),n=ma(t,e.type);t!==n&&(fe(br,e),fe(_t,n))}function mi(e){br.current===e&&(ve(_t),ve(br))}var ke=Kt(0);function ks(e){for(var t=e;t!==null;){if(t.tag===13){var n=t.memoizedState;if(n!==null&&(n=n.dehydrated,n===null||n.data==="$?"||n.data==="$!"))return t}else if(t.tag===19&&t.memoizedProps.revealOrder!==void 0){if((t.flags&128)!==0)return t}else if(t.child!==null){t.child.return=t,t=t.child;continue}if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return null;t=t.return}t.sibling.return=t.return,t=t.sibling}return null}var hi=[];function pi(){for(var e=0;e<hi.length;e++)hi[e]._workInProgressVersionPrimary=null;hi.length=0}var ws=te.ReactCurrentDispatcher,fi=te.ReactCurrentBatchConfig,fn=0,we=null,Me=null,Le=null,js=!1,Nr=!1,Cr=0,fm=0;function Be(){throw Error(l(321))}function gi(e,t){if(t===null)return!1;for(var n=0;n<t.length&&n<e.length;n++)if(!yt(e[n],t[n]))return!1;return!0}function vi(e,t,n,s,a,i){if(fn=i,we=t,t.memoizedState=null,t.updateQueue=null,t.lanes=0,ws.current=e===null||e.memoizedState===null?xm:km,e=n(s,a),Nr){i=0;do{if(Nr=!1,Cr=0,25<=i)throw Error(l(301));i+=1,Le=Me=null,t.updateQueue=null,ws.current=wm,e=n(s,a)}while(Nr)}if(ws.current=Ns,t=Me!==null&&Me.next!==null,fn=0,Le=Me=we=null,js=!1,t)throw Error(l(300));return e}function yi(){var e=Cr!==0;return Cr=0,e}function Tt(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return Le===null?we.memoizedState=Le=e:Le=Le.next=e,Le}function pt(){if(Me===null){var e=we.alternate;e=e!==null?e.memoizedState:null}else e=Me.next;var t=Le===null?we.memoizedState:Le.next;if(t!==null)Le=t,Me=e;else{if(e===null)throw Error(l(310));Me=e,e={memoizedState:Me.memoizedState,baseState:Me.baseState,baseQueue:Me.baseQueue,queue:Me.queue,next:null},Le===null?we.memoizedState=Le=e:Le=Le.next=e}return Le}function _r(e,t){return typeof t=="function"?t(e):t}function xi(e){var t=pt(),n=t.queue;if(n===null)throw Error(l(311));n.lastRenderedReducer=e;var s=Me,a=s.baseQueue,i=n.pending;if(i!==null){if(a!==null){var u=a.next;a.next=i.next,i.next=u}s.baseQueue=a=i,n.pending=null}if(a!==null){i=a.next,s=s.baseState;var h=u=null,p=null,j=i;do{var M=j.lane;if((fn&M)===M)p!==null&&(p=p.next={lane:0,action:j.action,hasEagerState:j.hasEagerState,eagerState:j.eagerState,next:null}),s=j.hasEagerState?j.eagerState:e(s,j.action);else{var R={lane:M,action:j.action,hasEagerState:j.hasEagerState,eagerState:j.eagerState,next:null};p===null?(h=p=R,u=s):p=p.next=R,we.lanes|=M,gn|=M}j=j.next}while(j!==null&&j!==i);p===null?u=s:p.next=h,yt(s,t.memoizedState)||(Qe=!0),t.memoizedState=s,t.baseState=u,t.baseQueue=p,n.lastRenderedState=s}if(e=n.interleaved,e!==null){a=e;do i=a.lane,we.lanes|=i,gn|=i,a=a.next;while(a!==e)}else a===null&&(n.lanes=0);return[t.memoizedState,n.dispatch]}function ki(e){var t=pt(),n=t.queue;if(n===null)throw Error(l(311));n.lastRenderedReducer=e;var s=n.dispatch,a=n.pending,i=t.memoizedState;if(a!==null){n.pending=null;var u=a=a.next;do i=e(i,u.action),u=u.next;while(u!==a);yt(i,t.memoizedState)||(Qe=!0),t.memoizedState=i,t.baseQueue===null&&(t.baseState=i),n.lastRenderedState=i}return[i,s]}function Yl(){}function Jl(e,t){var n=we,s=pt(),a=t(),i=!yt(s.memoizedState,a);if(i&&(s.memoizedState=a,Qe=!0),s=s.queue,wi(tc.bind(null,n,s,e),[e]),s.getSnapshot!==t||i||Le!==null&&Le.memoizedState.tag&1){if(n.flags|=2048,Tr(9,ec.bind(null,n,s,a,t),void 0,null),Re===null)throw Error(l(349));(fn&30)!==0||Zl(n,t,a)}return a}function Zl(e,t,n){e.flags|=16384,e={getSnapshot:t,value:n},t=we.updateQueue,t===null?(t={lastEffect:null,stores:null},we.updateQueue=t,t.stores=[e]):(n=t.stores,n===null?t.stores=[e]:n.push(e))}function ec(e,t,n,s){t.value=n,t.getSnapshot=s,nc(t)&&rc(e)}function tc(e,t,n){return n(function(){nc(t)&&rc(e)})}function nc(e){var t=e.getSnapshot;e=e.value;try{var n=t();return!yt(e,n)}catch{return!0}}function rc(e){var t=Dt(e,1);t!==null&&bt(t,e,1,-1)}function sc(e){var t=Tt();return typeof e=="function"&&(e=e()),t.memoizedState=t.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:_r,lastRenderedState:e},t.queue=e,e=e.dispatch=ym.bind(null,we,e),[t.memoizedState,e]}function Tr(e,t,n,s){return e={tag:e,create:t,destroy:n,deps:s,next:null},t=we.updateQueue,t===null?(t={lastEffect:null,stores:null},we.updateQueue=t,t.lastEffect=e.next=e):(n=t.lastEffect,n===null?t.lastEffect=e.next=e:(s=n.next,n.next=e,e.next=s,t.lastEffect=e)),e}function ac(){return pt().memoizedState}function bs(e,t,n,s){var a=Tt();we.flags|=e,a.memoizedState=Tr(1|t,n,void 0,s===void 0?null:s)}function Ss(e,t,n,s){var a=pt();s=s===void 0?null:s;var i=void 0;if(Me!==null){var u=Me.memoizedState;if(i=u.destroy,s!==null&&gi(s,u.deps)){a.memoizedState=Tr(t,n,i,s);return}}we.flags|=e,a.memoizedState=Tr(1|t,n,i,s)}function ic(e,t){return bs(8390656,8,e,t)}function wi(e,t){return Ss(2048,8,e,t)}function oc(e,t){return Ss(4,2,e,t)}function lc(e,t){return Ss(4,4,e,t)}function cc(e,t){if(typeof t=="function")return e=e(),t(e),function(){t(null)};if(t!=null)return e=e(),t.current=e,function(){t.current=null}}function uc(e,t,n){return n=n!=null?n.concat([e]):null,Ss(4,4,cc.bind(null,t,e),n)}function ji(){}function dc(e,t){var n=pt();t=t===void 0?null:t;var s=n.memoizedState;return s!==null&&t!==null&&gi(t,s[1])?s[0]:(n.memoizedState=[e,t],e)}function mc(e,t){var n=pt();t=t===void 0?null:t;var s=n.memoizedState;return s!==null&&t!==null&&gi(t,s[1])?s[0]:(e=e(),n.memoizedState=[e,t],e)}function hc(e,t,n){return(fn&21)===0?(e.baseState&&(e.baseState=!1,Qe=!0),e.memoizedState=n):(yt(n,t)||(n=$o(),we.lanes|=n,gn|=n,e.baseState=!0),t)}function gm(e,t){var n=me;me=n!==0&&4>n?n:4,e(!0);var s=fi.transition;fi.transition={};try{e(!1),t()}finally{me=n,fi.transition=s}}function pc(){return pt().memoizedState}function vm(e,t,n){var s=tn(e);if(n={lane:s,action:n,hasEagerState:!1,eagerState:null,next:null},fc(e))gc(t,n);else if(n=Gl(e,t,n,s),n!==null){var a=He();bt(n,e,s,a),vc(n,t,s)}}function ym(e,t,n){var s=tn(e),a={lane:s,action:n,hasEagerState:!1,eagerState:null,next:null};if(fc(e))gc(t,a);else{var i=e.alternate;if(e.lanes===0&&(i===null||i.lanes===0)&&(i=t.lastRenderedReducer,i!==null))try{var u=t.lastRenderedState,h=i(u,n);if(a.hasEagerState=!0,a.eagerState=h,yt(h,u)){var p=t.interleaved;p===null?(a.next=a,ci(t)):(a.next=p.next,p.next=a),t.interleaved=a;return}}catch{}finally{}n=Gl(e,t,a,s),n!==null&&(a=He(),bt(n,e,s,a),vc(n,t,s))}}function fc(e){var t=e.alternate;return e===we||t!==null&&t===we}function gc(e,t){Nr=js=!0;var n=e.pending;n===null?t.next=t:(t.next=n.next,n.next=t),e.pending=t}function vc(e,t,n){if((n&4194240)!==0){var s=t.lanes;s&=e.pendingLanes,n|=s,t.lanes=n,Sa(e,n)}}var Ns={readContext:ht,useCallback:Be,useContext:Be,useEffect:Be,useImperativeHandle:Be,useInsertionEffect:Be,useLayoutEffect:Be,useMemo:Be,useReducer:Be,useRef:Be,useState:Be,useDebugValue:Be,useDeferredValue:Be,useTransition:Be,useMutableSource:Be,useSyncExternalStore:Be,useId:Be,unstable_isNewReconciler:!1},xm={readContext:ht,useCallback:function(e,t){return Tt().memoizedState=[e,t===void 0?null:t],e},useContext:ht,useEffect:ic,useImperativeHandle:function(e,t,n){return n=n!=null?n.concat([e]):null,bs(4194308,4,cc.bind(null,t,e),n)},useLayoutEffect:function(e,t){return bs(4194308,4,e,t)},useInsertionEffect:function(e,t){return bs(4,2,e,t)},useMemo:function(e,t){var n=Tt();return t=t===void 0?null:t,e=e(),n.memoizedState=[e,t],e},useReducer:function(e,t,n){var s=Tt();return t=n!==void 0?n(t):t,s.memoizedState=s.baseState=t,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:t},s.queue=e,e=e.dispatch=vm.bind(null,we,e),[s.memoizedState,e]},useRef:function(e){var t=Tt();return e={current:e},t.memoizedState=e},useState:sc,useDebugValue:ji,useDeferredValue:function(e){return Tt().memoizedState=e},useTransition:function(){var e=sc(!1),t=e[0];return e=gm.bind(null,e[1]),Tt().memoizedState=e,[t,e]},useMutableSource:function(){},useSyncExternalStore:function(e,t,n){var s=we,a=Tt();if(xe){if(n===void 0)throw Error(l(407));n=n()}else{if(n=t(),Re===null)throw Error(l(349));(fn&30)!==0||Zl(s,t,n)}a.memoizedState=n;var i={value:n,getSnapshot:t};return a.queue=i,ic(tc.bind(null,s,i,e),[e]),s.flags|=2048,Tr(9,ec.bind(null,s,i,n,t),void 0,null),n},useId:function(){var e=Tt(),t=Re.identifierPrefix;if(xe){var n=At,s=Rt;n=(s&~(1<<32-vt(s)-1)).toString(32)+n,t=":"+t+"R"+n,n=Cr++,0<n&&(t+="H"+n.toString(32)),t+=":"}else n=fm++,t=":"+t+"r"+n.toString(32)+":";return e.memoizedState=t},unstable_isNewReconciler:!1},km={readContext:ht,useCallback:dc,useContext:ht,useEffect:wi,useImperativeHandle:uc,useInsertionEffect:oc,useLayoutEffect:lc,useMemo:mc,useReducer:xi,useRef:ac,useState:function(){return xi(_r)},useDebugValue:ji,useDeferredValue:function(e){var t=pt();return hc(t,Me.memoizedState,e)},useTransition:function(){var e=xi(_r)[0],t=pt().memoizedState;return[e,t]},useMutableSource:Yl,useSyncExternalStore:Jl,useId:pc,unstable_isNewReconciler:!1},wm={readContext:ht,useCallback:dc,useContext:ht,useEffect:wi,useImperativeHandle:uc,useInsertionEffect:oc,useLayoutEffect:lc,useMemo:mc,useReducer:ki,useRef:ac,useState:function(){return ki(_r)},useDebugValue:ji,useDeferredValue:function(e){var t=pt();return Me===null?t.memoizedState=e:hc(t,Me.memoizedState,e)},useTransition:function(){var e=ki(_r)[0],t=pt().memoizedState;return[e,t]},useMutableSource:Yl,useSyncExternalStore:Jl,useId:pc,unstable_isNewReconciler:!1};function kt(e,t){if(e&&e.defaultProps){t=V({},t),e=e.defaultProps;for(var n in e)t[n]===void 0&&(t[n]=e[n]);return t}return t}function bi(e,t,n,s){t=e.memoizedState,n=n(s,t),n=n==null?t:V({},t,n),e.memoizedState=n,e.lanes===0&&(e.updateQueue.baseState=n)}var Cs={isMounted:function(e){return(e=e._reactInternals)?ln(e)===e:!1},enqueueSetState:function(e,t,n){e=e._reactInternals;var s=He(),a=tn(e),i=It(s,a);i.payload=t,n!=null&&(i.callback=n),t=Yt(e,i,a),t!==null&&(bt(t,e,a,s),ys(t,e,a))},enqueueReplaceState:function(e,t,n){e=e._reactInternals;var s=He(),a=tn(e),i=It(s,a);i.tag=1,i.payload=t,n!=null&&(i.callback=n),t=Yt(e,i,a),t!==null&&(bt(t,e,a,s),ys(t,e,a))},enqueueForceUpdate:function(e,t){e=e._reactInternals;var n=He(),s=tn(e),a=It(n,s);a.tag=2,t!=null&&(a.callback=t),t=Yt(e,a,s),t!==null&&(bt(t,e,s,n),ys(t,e,s))}};function yc(e,t,n,s,a,i,u){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(s,i,u):t.prototype&&t.prototype.isPureReactComponent?!pr(n,s)||!pr(a,i):!0}function xc(e,t,n){var s=!1,a=qt,i=t.contextType;return typeof i=="object"&&i!==null?i=ht(i):(a=qe(t)?un:Fe.current,s=t.contextTypes,i=(s=s!=null)?zn(e,a):qt),t=new t(n,i),e.memoizedState=t.state!==null&&t.state!==void 0?t.state:null,t.updater=Cs,e.stateNode=t,t._reactInternals=e,s&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=a,e.__reactInternalMemoizedMaskedChildContext=i),t}function kc(e,t,n,s){e=t.state,typeof t.componentWillReceiveProps=="function"&&t.componentWillReceiveProps(n,s),typeof t.UNSAFE_componentWillReceiveProps=="function"&&t.UNSAFE_componentWillReceiveProps(n,s),t.state!==e&&Cs.enqueueReplaceState(t,t.state,null)}function Si(e,t,n,s){var a=e.stateNode;a.props=n,a.state=e.memoizedState,a.refs={},ui(e);var i=t.contextType;typeof i=="object"&&i!==null?a.context=ht(i):(i=qe(t)?un:Fe.current,a.context=zn(e,i)),a.state=e.memoizedState,i=t.getDerivedStateFromProps,typeof i=="function"&&(bi(e,t,i,n),a.state=e.memoizedState),typeof t.getDerivedStateFromProps=="function"||typeof a.getSnapshotBeforeUpdate=="function"||typeof a.UNSAFE_componentWillMount!="function"&&typeof a.componentWillMount!="function"||(t=a.state,typeof a.componentWillMount=="function"&&a.componentWillMount(),typeof a.UNSAFE_componentWillMount=="function"&&a.UNSAFE_componentWillMount(),t!==a.state&&Cs.enqueueReplaceState(a,a.state,null),xs(e,n,a,s),a.state=e.memoizedState),typeof a.componentDidMount=="function"&&(e.flags|=4194308)}function Hn(e,t){try{var n="",s=t;do n+=le(s),s=s.return;while(s);var a=n}catch(i){a=`
Error generating stack: `+i.message+`
`+i.stack}return{value:e,source:t,stack:a,digest:null}}function Ni(e,t,n){return{value:e,source:null,stack:n??null,digest:t??null}}function Ci(e,t){try{console.error(t.value)}catch(n){setTimeout(function(){throw n})}}var jm=typeof WeakMap=="function"?WeakMap:Map;function wc(e,t,n){n=It(-1,n),n.tag=3,n.payload={element:null};var s=t.value;return n.callback=function(){Rs||(Rs=!0,Wi=s),Ci(e,t)},n}function jc(e,t,n){n=It(-1,n),n.tag=3;var s=e.type.getDerivedStateFromError;if(typeof s=="function"){var a=t.value;n.payload=function(){return s(a)},n.callback=function(){Ci(e,t)}}var i=e.stateNode;return i!==null&&typeof i.componentDidCatch=="function"&&(n.callback=function(){Ci(e,t),typeof s!="function"&&(Zt===null?Zt=new Set([this]):Zt.add(this));var u=t.stack;this.componentDidCatch(t.value,{componentStack:u!==null?u:""})}),n}function bc(e,t,n){var s=e.pingCache;if(s===null){s=e.pingCache=new jm;var a=new Set;s.set(t,a)}else a=s.get(t),a===void 0&&(a=new Set,s.set(t,a));a.has(n)||(a.add(n),e=Im.bind(null,e,t,n),t.then(e,e))}function Sc(e){do{var t;if((t=e.tag===13)&&(t=e.memoizedState,t=t!==null?t.dehydrated!==null:!0),t)return e;e=e.return}while(e!==null);return null}function Nc(e,t,n,s,a){return(e.mode&1)===0?(e===t?e.flags|=65536:(e.flags|=128,n.flags|=131072,n.flags&=-52805,n.tag===1&&(n.alternate===null?n.tag=17:(t=It(-1,1),t.tag=2,Yt(n,t,1))),n.lanes|=1),e):(e.flags|=65536,e.lanes=a,e)}var bm=te.ReactCurrentOwner,Qe=!1;function Ve(e,t,n,s){t.child=e===null?Hl(t,null,n,s):Wn(t,e.child,n,s)}function Cc(e,t,n,s,a){n=n.render;var i=t.ref;return $n(t,a),s=vi(e,t,n,s,i,a),n=yi(),e!==null&&!Qe?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~a,zt(e,t,a)):(xe&&n&&ei(t),t.flags|=1,Ve(e,t,s,a),t.child)}function _c(e,t,n,s,a){if(e===null){var i=n.type;return typeof i=="function"&&!qi(i)&&i.defaultProps===void 0&&n.compare===null&&n.defaultProps===void 0?(t.tag=15,t.type=i,Tc(e,t,i,s,a)):(e=Bs(n.type,null,s,t,t.mode,a),e.ref=t.ref,e.return=t,t.child=e)}if(i=e.child,(e.lanes&a)===0){var u=i.memoizedProps;if(n=n.compare,n=n!==null?n:pr,n(u,s)&&e.ref===t.ref)return zt(e,t,a)}return t.flags|=1,e=rn(i,s),e.ref=t.ref,e.return=t,t.child=e}function Tc(e,t,n,s,a){if(e!==null){var i=e.memoizedProps;if(pr(i,s)&&e.ref===t.ref)if(Qe=!1,t.pendingProps=s=i,(e.lanes&a)!==0)(e.flags&131072)!==0&&(Qe=!0);else return t.lanes=e.lanes,zt(e,t,a)}return _i(e,t,n,s,a)}function Ec(e,t,n){var s=t.pendingProps,a=s.children,i=e!==null?e.memoizedState:null;if(s.mode==="hidden")if((t.mode&1)===0)t.memoizedState={baseLanes:0,cachePool:null,transitions:null},fe(Kn,ut),ut|=n;else{if((n&1073741824)===0)return e=i!==null?i.baseLanes|n:n,t.lanes=t.childLanes=1073741824,t.memoizedState={baseLanes:e,cachePool:null,transitions:null},t.updateQueue=null,fe(Kn,ut),ut|=e,null;t.memoizedState={baseLanes:0,cachePool:null,transitions:null},s=i!==null?i.baseLanes:n,fe(Kn,ut),ut|=s}else i!==null?(s=i.baseLanes|n,t.memoizedState=null):s=n,fe(Kn,ut),ut|=s;return Ve(e,t,a,n),t.child}function Mc(e,t){var n=t.ref;(e===null&&n!==null||e!==null&&e.ref!==n)&&(t.flags|=512,t.flags|=2097152)}function _i(e,t,n,s,a){var i=qe(n)?un:Fe.current;return i=zn(t,i),$n(t,a),n=vi(e,t,n,s,i,a),s=yi(),e!==null&&!Qe?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~a,zt(e,t,a)):(xe&&s&&ei(t),t.flags|=1,Ve(e,t,n,a),t.child)}function Pc(e,t,n,s,a){if(qe(n)){var i=!0;us(t)}else i=!1;if($n(t,a),t.stateNode===null)Ts(e,t),xc(t,n,s),Si(t,n,s,a),s=!0;else if(e===null){var u=t.stateNode,h=t.memoizedProps;u.props=h;var p=u.context,j=n.contextType;typeof j=="object"&&j!==null?j=ht(j):(j=qe(n)?un:Fe.current,j=zn(t,j));var M=n.getDerivedStateFromProps,R=typeof M=="function"||typeof u.getSnapshotBeforeUpdate=="function";R||typeof u.UNSAFE_componentWillReceiveProps!="function"&&typeof u.componentWillReceiveProps!="function"||(h!==s||p!==j)&&kc(t,u,s,j),Xt=!1;var T=t.memoizedState;u.state=T,xs(t,s,u,a),p=t.memoizedState,h!==s||T!==p||Ke.current||Xt?(typeof M=="function"&&(bi(t,n,M,s),p=t.memoizedState),(h=Xt||yc(t,n,h,s,T,p,j))?(R||typeof u.UNSAFE_componentWillMount!="function"&&typeof u.componentWillMount!="function"||(typeof u.componentWillMount=="function"&&u.componentWillMount(),typeof u.UNSAFE_componentWillMount=="function"&&u.UNSAFE_componentWillMount()),typeof u.componentDidMount=="function"&&(t.flags|=4194308)):(typeof u.componentDidMount=="function"&&(t.flags|=4194308),t.memoizedProps=s,t.memoizedState=p),u.props=s,u.state=p,u.context=j,s=h):(typeof u.componentDidMount=="function"&&(t.flags|=4194308),s=!1)}else{u=t.stateNode,Kl(e,t),h=t.memoizedProps,j=t.type===t.elementType?h:kt(t.type,h),u.props=j,R=t.pendingProps,T=u.context,p=n.contextType,typeof p=="object"&&p!==null?p=ht(p):(p=qe(n)?un:Fe.current,p=zn(t,p));var W=n.getDerivedStateFromProps;(M=typeof W=="function"||typeof u.getSnapshotBeforeUpdate=="function")||typeof u.UNSAFE_componentWillReceiveProps!="function"&&typeof u.componentWillReceiveProps!="function"||(h!==R||T!==p)&&kc(t,u,s,p),Xt=!1,T=t.memoizedState,u.state=T,xs(t,s,u,a);var H=t.memoizedState;h!==R||T!==H||Ke.current||Xt?(typeof W=="function"&&(bi(t,n,W,s),H=t.memoizedState),(j=Xt||yc(t,n,j,s,T,H,p)||!1)?(M||typeof u.UNSAFE_componentWillUpdate!="function"&&typeof u.componentWillUpdate!="function"||(typeof u.componentWillUpdate=="function"&&u.componentWillUpdate(s,H,p),typeof u.UNSAFE_componentWillUpdate=="function"&&u.UNSAFE_componentWillUpdate(s,H,p)),typeof u.componentDidUpdate=="function"&&(t.flags|=4),typeof u.getSnapshotBeforeUpdate=="function"&&(t.flags|=1024)):(typeof u.componentDidUpdate!="function"||h===e.memoizedProps&&T===e.memoizedState||(t.flags|=4),typeof u.getSnapshotBeforeUpdate!="function"||h===e.memoizedProps&&T===e.memoizedState||(t.flags|=1024),t.memoizedProps=s,t.memoizedState=H),u.props=s,u.state=H,u.context=p,s=j):(typeof u.componentDidUpdate!="function"||h===e.memoizedProps&&T===e.memoizedState||(t.flags|=4),typeof u.getSnapshotBeforeUpdate!="function"||h===e.memoizedProps&&T===e.memoizedState||(t.flags|=1024),s=!1)}return Ti(e,t,n,s,i,a)}function Ti(e,t,n,s,a,i){Mc(e,t);var u=(t.flags&128)!==0;if(!s&&!u)return a&&Il(t,n,!1),zt(e,t,i);s=t.stateNode,bm.current=t;var h=u&&typeof n.getDerivedStateFromError!="function"?null:s.render();return t.flags|=1,e!==null&&u?(t.child=Wn(t,e.child,null,i),t.child=Wn(t,null,h,i)):Ve(e,t,h,i),t.memoizedState=s.state,a&&Il(t,n,!0),t.child}function Lc(e){var t=e.stateNode;t.pendingContext?Al(e,t.pendingContext,t.pendingContext!==t.context):t.context&&Al(e,t.context,!1),di(e,t.containerInfo)}function Rc(e,t,n,s,a){return On(),si(a),t.flags|=256,Ve(e,t,n,s),t.child}var Ei={dehydrated:null,treeContext:null,retryLane:0};function Mi(e){return{baseLanes:e,cachePool:null,transitions:null}}function Ac(e,t,n){var s=t.pendingProps,a=ke.current,i=!1,u=(t.flags&128)!==0,h;if((h=u)||(h=e!==null&&e.memoizedState===null?!1:(a&2)!==0),h?(i=!0,t.flags&=-129):(e===null||e.memoizedState!==null)&&(a|=1),fe(ke,a&1),e===null)return ri(t),e=t.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?((t.mode&1)===0?t.lanes=1:e.data==="$!"?t.lanes=8:t.lanes=1073741824,null):(u=s.children,e=s.fallback,i?(s=t.mode,i=t.child,u={mode:"hidden",children:u},(s&1)===0&&i!==null?(i.childLanes=0,i.pendingProps=u):i=Os(u,s,0,null),e=kn(e,s,n,null),i.return=t,e.return=t,i.sibling=e,t.child=i,t.child.memoizedState=Mi(n),t.memoizedState=Ei,e):Pi(t,u));if(a=e.memoizedState,a!==null&&(h=a.dehydrated,h!==null))return Sm(e,t,u,s,h,a,n);if(i){i=s.fallback,u=t.mode,a=e.child,h=a.sibling;var p={mode:"hidden",children:s.children};return(u&1)===0&&t.child!==a?(s=t.child,s.childLanes=0,s.pendingProps=p,t.deletions=null):(s=rn(a,p),s.subtreeFlags=a.subtreeFlags&14680064),h!==null?i=rn(h,i):(i=kn(i,u,n,null),i.flags|=2),i.return=t,s.return=t,s.sibling=i,t.child=s,s=i,i=t.child,u=e.child.memoizedState,u=u===null?Mi(n):{baseLanes:u.baseLanes|n,cachePool:null,transitions:u.transitions},i.memoizedState=u,i.childLanes=e.childLanes&~n,t.memoizedState=Ei,s}return i=e.child,e=i.sibling,s=rn(i,{mode:"visible",children:s.children}),(t.mode&1)===0&&(s.lanes=n),s.return=t,s.sibling=null,e!==null&&(n=t.deletions,n===null?(t.deletions=[e],t.flags|=16):n.push(e)),t.child=s,t.memoizedState=null,s}function Pi(e,t){return t=Os({mode:"visible",children:t},e.mode,0,null),t.return=e,e.child=t}function _s(e,t,n,s){return s!==null&&si(s),Wn(t,e.child,null,n),e=Pi(t,t.pendingProps.children),e.flags|=2,t.memoizedState=null,e}function Sm(e,t,n,s,a,i,u){if(n)return t.flags&256?(t.flags&=-257,s=Ni(Error(l(422))),_s(e,t,u,s)):t.memoizedState!==null?(t.child=e.child,t.flags|=128,null):(i=s.fallback,a=t.mode,s=Os({mode:"visible",children:s.children},a,0,null),i=kn(i,a,u,null),i.flags|=2,s.return=t,i.return=t,s.sibling=i,t.child=s,(t.mode&1)!==0&&Wn(t,e.child,null,u),t.child.memoizedState=Mi(u),t.memoizedState=Ei,i);if((t.mode&1)===0)return _s(e,t,u,null);if(a.data==="$!"){if(s=a.nextSibling&&a.nextSibling.dataset,s)var h=s.dgst;return s=h,i=Error(l(419)),s=Ni(i,s,void 0),_s(e,t,u,s)}if(h=(u&e.childLanes)!==0,Qe||h){if(s=Re,s!==null){switch(u&-u){case 4:a=2;break;case 16:a=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:a=32;break;case 536870912:a=268435456;break;default:a=0}a=(a&(s.suspendedLanes|u))!==0?0:a,a!==0&&a!==i.retryLane&&(i.retryLane=a,Dt(e,a),bt(s,e,a,-1))}return Ki(),s=Ni(Error(l(421))),_s(e,t,u,s)}return a.data==="$?"?(t.flags|=128,t.child=e.child,t=zm.bind(null,e),a._reactRetry=t,null):(e=i.treeContext,ct=Gt(a.nextSibling),lt=t,xe=!0,xt=null,e!==null&&(dt[mt++]=Rt,dt[mt++]=At,dt[mt++]=dn,Rt=e.id,At=e.overflow,dn=t),t=Pi(t,s.children),t.flags|=4096,t)}function Dc(e,t,n){e.lanes|=t;var s=e.alternate;s!==null&&(s.lanes|=t),li(e.return,t,n)}function Li(e,t,n,s,a){var i=e.memoizedState;i===null?e.memoizedState={isBackwards:t,rendering:null,renderingStartTime:0,last:s,tail:n,tailMode:a}:(i.isBackwards=t,i.rendering=null,i.renderingStartTime=0,i.last=s,i.tail=n,i.tailMode=a)}function Ic(e,t,n){var s=t.pendingProps,a=s.revealOrder,i=s.tail;if(Ve(e,t,s.children,n),s=ke.current,(s&2)!==0)s=s&1|2,t.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=t.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Dc(e,n,t);else if(e.tag===19)Dc(e,n,t);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===t)break e;for(;e.sibling===null;){if(e.return===null||e.return===t)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}s&=1}if(fe(ke,s),(t.mode&1)===0)t.memoizedState=null;else switch(a){case"forwards":for(n=t.child,a=null;n!==null;)e=n.alternate,e!==null&&ks(e)===null&&(a=n),n=n.sibling;n=a,n===null?(a=t.child,t.child=null):(a=n.sibling,n.sibling=null),Li(t,!1,a,n,i);break;case"backwards":for(n=null,a=t.child,t.child=null;a!==null;){if(e=a.alternate,e!==null&&ks(e)===null){t.child=a;break}e=a.sibling,a.sibling=n,n=a,a=e}Li(t,!0,n,null,i);break;case"together":Li(t,!1,null,null,void 0);break;default:t.memoizedState=null}return t.child}function Ts(e,t){(t.mode&1)===0&&e!==null&&(e.alternate=null,t.alternate=null,t.flags|=2)}function zt(e,t,n){if(e!==null&&(t.dependencies=e.dependencies),gn|=t.lanes,(n&t.childLanes)===0)return null;if(e!==null&&t.child!==e.child)throw Error(l(153));if(t.child!==null){for(e=t.child,n=rn(e,e.pendingProps),t.child=n,n.return=t;e.sibling!==null;)e=e.sibling,n=n.sibling=rn(e,e.pendingProps),n.return=t;n.sibling=null}return t.child}function Nm(e,t,n){switch(t.tag){case 3:Lc(t),On();break;case 5:Xl(t);break;case 1:qe(t.type)&&us(t);break;case 4:di(t,t.stateNode.containerInfo);break;case 10:var s=t.type._context,a=t.memoizedProps.value;fe(gs,s._currentValue),s._currentValue=a;break;case 13:if(s=t.memoizedState,s!==null)return s.dehydrated!==null?(fe(ke,ke.current&1),t.flags|=128,null):(n&t.child.childLanes)!==0?Ac(e,t,n):(fe(ke,ke.current&1),e=zt(e,t,n),e!==null?e.sibling:null);fe(ke,ke.current&1);break;case 19:if(s=(n&t.childLanes)!==0,(e.flags&128)!==0){if(s)return Ic(e,t,n);t.flags|=128}if(a=t.memoizedState,a!==null&&(a.rendering=null,a.tail=null,a.lastEffect=null),fe(ke,ke.current),s)break;return null;case 22:case 23:return t.lanes=0,Ec(e,t,n)}return zt(e,t,n)}var zc,Ri,Fc,Bc;zc=function(e,t){for(var n=t.child;n!==null;){if(n.tag===5||n.tag===6)e.appendChild(n.stateNode);else if(n.tag!==4&&n.child!==null){n.child.return=n,n=n.child;continue}if(n===t)break;for(;n.sibling===null;){if(n.return===null||n.return===t)return;n=n.return}n.sibling.return=n.return,n=n.sibling}},Ri=function(){},Fc=function(e,t,n,s){var a=e.memoizedProps;if(a!==s){e=t.stateNode,pn(_t.current);var i=null;switch(n){case"input":a=la(e,a),s=la(e,s),i=[];break;case"select":a=V({},a,{value:void 0}),s=V({},s,{value:void 0}),i=[];break;case"textarea":a=da(e,a),s=da(e,s),i=[];break;default:typeof a.onClick!="function"&&typeof s.onClick=="function"&&(e.onclick=os)}ha(n,s);var u;n=null;for(j in a)if(!s.hasOwnProperty(j)&&a.hasOwnProperty(j)&&a[j]!=null)if(j==="style"){var h=a[j];for(u in h)h.hasOwnProperty(u)&&(n||(n={}),n[u]="")}else j!=="dangerouslySetInnerHTML"&&j!=="children"&&j!=="suppressContentEditableWarning"&&j!=="suppressHydrationWarning"&&j!=="autoFocus"&&(m.hasOwnProperty(j)?i||(i=[]):(i=i||[]).push(j,null));for(j in s){var p=s[j];if(h=a!=null?a[j]:void 0,s.hasOwnProperty(j)&&p!==h&&(p!=null||h!=null))if(j==="style")if(h){for(u in h)!h.hasOwnProperty(u)||p&&p.hasOwnProperty(u)||(n||(n={}),n[u]="");for(u in p)p.hasOwnProperty(u)&&h[u]!==p[u]&&(n||(n={}),n[u]=p[u])}else n||(i||(i=[]),i.push(j,n)),n=p;else j==="dangerouslySetInnerHTML"?(p=p?p.__html:void 0,h=h?h.__html:void 0,p!=null&&h!==p&&(i=i||[]).push(j,p)):j==="children"?typeof p!="string"&&typeof p!="number"||(i=i||[]).push(j,""+p):j!=="suppressContentEditableWarning"&&j!=="suppressHydrationWarning"&&(m.hasOwnProperty(j)?(p!=null&&j==="onScroll"&&ge("scroll",e),i||h===p||(i=[])):(i=i||[]).push(j,p))}n&&(i=i||[]).push("style",n);var j=i;(t.updateQueue=j)&&(t.flags|=4)}},Bc=function(e,t,n,s){n!==s&&(t.flags|=4)};function Er(e,t){if(!xe)switch(e.tailMode){case"hidden":t=e.tail;for(var n=null;t!==null;)t.alternate!==null&&(n=t),t=t.sibling;n===null?e.tail=null:n.sibling=null;break;case"collapsed":n=e.tail;for(var s=null;n!==null;)n.alternate!==null&&(s=n),n=n.sibling;s===null?t||e.tail===null?e.tail=null:e.tail.sibling=null:s.sibling=null}}function Oe(e){var t=e.alternate!==null&&e.alternate.child===e.child,n=0,s=0;if(t)for(var a=e.child;a!==null;)n|=a.lanes|a.childLanes,s|=a.subtreeFlags&14680064,s|=a.flags&14680064,a.return=e,a=a.sibling;else for(a=e.child;a!==null;)n|=a.lanes|a.childLanes,s|=a.subtreeFlags,s|=a.flags,a.return=e,a=a.sibling;return e.subtreeFlags|=s,e.childLanes=n,t}function Cm(e,t,n){var s=t.pendingProps;switch(ti(t),t.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Oe(t),null;case 1:return qe(t.type)&&cs(),Oe(t),null;case 3:return s=t.stateNode,Vn(),ve(Ke),ve(Fe),pi(),s.pendingContext&&(s.context=s.pendingContext,s.pendingContext=null),(e===null||e.child===null)&&(ps(t)?t.flags|=4:e===null||e.memoizedState.isDehydrated&&(t.flags&256)===0||(t.flags|=1024,xt!==null&&(Vi(xt),xt=null))),Ri(e,t),Oe(t),null;case 5:mi(t);var a=pn(Sr.current);if(n=t.type,e!==null&&t.stateNode!=null)Fc(e,t,n,s,a),e.ref!==t.ref&&(t.flags|=512,t.flags|=2097152);else{if(!s){if(t.stateNode===null)throw Error(l(166));return Oe(t),null}if(e=pn(_t.current),ps(t)){s=t.stateNode,n=t.type;var i=t.memoizedProps;switch(s[Ct]=t,s[xr]=i,e=(t.mode&1)!==0,n){case"dialog":ge("cancel",s),ge("close",s);break;case"iframe":case"object":case"embed":ge("load",s);break;case"video":case"audio":for(a=0;a<gr.length;a++)ge(gr[a],s);break;case"source":ge("error",s);break;case"img":case"image":case"link":ge("error",s),ge("load",s);break;case"details":ge("toggle",s);break;case"input":xo(s,i),ge("invalid",s);break;case"select":s._wrapperState={wasMultiple:!!i.multiple},ge("invalid",s);break;case"textarea":jo(s,i),ge("invalid",s)}ha(n,i),a=null;for(var u in i)if(i.hasOwnProperty(u)){var h=i[u];u==="children"?typeof h=="string"?s.textContent!==h&&(i.suppressHydrationWarning!==!0&&is(s.textContent,h,e),a=["children",h]):typeof h=="number"&&s.textContent!==""+h&&(i.suppressHydrationWarning!==!0&&is(s.textContent,h,e),a=["children",""+h]):m.hasOwnProperty(u)&&h!=null&&u==="onScroll"&&ge("scroll",s)}switch(n){case"input":zr(s),wo(s,i,!0);break;case"textarea":zr(s),So(s);break;case"select":case"option":break;default:typeof i.onClick=="function"&&(s.onclick=os)}s=a,t.updateQueue=s,s!==null&&(t.flags|=4)}else{u=a.nodeType===9?a:a.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=No(n)),e==="http://www.w3.org/1999/xhtml"?n==="script"?(e=u.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof s.is=="string"?e=u.createElement(n,{is:s.is}):(e=u.createElement(n),n==="select"&&(u=e,s.multiple?u.multiple=!0:s.size&&(u.size=s.size))):e=u.createElementNS(e,n),e[Ct]=t,e[xr]=s,zc(e,t,!1,!1),t.stateNode=e;e:{switch(u=pa(n,s),n){case"dialog":ge("cancel",e),ge("close",e),a=s;break;case"iframe":case"object":case"embed":ge("load",e),a=s;break;case"video":case"audio":for(a=0;a<gr.length;a++)ge(gr[a],e);a=s;break;case"source":ge("error",e),a=s;break;case"img":case"image":case"link":ge("error",e),ge("load",e),a=s;break;case"details":ge("toggle",e),a=s;break;case"input":xo(e,s),a=la(e,s),ge("invalid",e);break;case"option":a=s;break;case"select":e._wrapperState={wasMultiple:!!s.multiple},a=V({},s,{value:void 0}),ge("invalid",e);break;case"textarea":jo(e,s),a=da(e,s),ge("invalid",e);break;default:a=s}ha(n,a),h=a;for(i in h)if(h.hasOwnProperty(i)){var p=h[i];i==="style"?To(e,p):i==="dangerouslySetInnerHTML"?(p=p?p.__html:void 0,p!=null&&Co(e,p)):i==="children"?typeof p=="string"?(n!=="textarea"||p!=="")&&Yn(e,p):typeof p=="number"&&Yn(e,""+p):i!=="suppressContentEditableWarning"&&i!=="suppressHydrationWarning"&&i!=="autoFocus"&&(m.hasOwnProperty(i)?p!=null&&i==="onScroll"&&ge("scroll",e):p!=null&&Q(e,i,p,u))}switch(n){case"input":zr(e),wo(e,s,!1);break;case"textarea":zr(e),So(e);break;case"option":s.value!=null&&e.setAttribute("value",""+de(s.value));break;case"select":e.multiple=!!s.multiple,i=s.value,i!=null?Nn(e,!!s.multiple,i,!1):s.defaultValue!=null&&Nn(e,!!s.multiple,s.defaultValue,!0);break;default:typeof a.onClick=="function"&&(e.onclick=os)}switch(n){case"button":case"input":case"select":case"textarea":s=!!s.autoFocus;break e;case"img":s=!0;break e;default:s=!1}}s&&(t.flags|=4)}t.ref!==null&&(t.flags|=512,t.flags|=2097152)}return Oe(t),null;case 6:if(e&&t.stateNode!=null)Bc(e,t,e.memoizedProps,s);else{if(typeof s!="string"&&t.stateNode===null)throw Error(l(166));if(n=pn(Sr.current),pn(_t.current),ps(t)){if(s=t.stateNode,n=t.memoizedProps,s[Ct]=t,(i=s.nodeValue!==n)&&(e=lt,e!==null))switch(e.tag){case 3:is(s.nodeValue,n,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&is(s.nodeValue,n,(e.mode&1)!==0)}i&&(t.flags|=4)}else s=(n.nodeType===9?n:n.ownerDocument).createTextNode(s),s[Ct]=t,t.stateNode=s}return Oe(t),null;case 13:if(ve(ke),s=t.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(xe&&ct!==null&&(t.mode&1)!==0&&(t.flags&128)===0)Ul(),On(),t.flags|=98560,i=!1;else if(i=ps(t),s!==null&&s.dehydrated!==null){if(e===null){if(!i)throw Error(l(318));if(i=t.memoizedState,i=i!==null?i.dehydrated:null,!i)throw Error(l(317));i[Ct]=t}else On(),(t.flags&128)===0&&(t.memoizedState=null),t.flags|=4;Oe(t),i=!1}else xt!==null&&(Vi(xt),xt=null),i=!0;if(!i)return t.flags&65536?t:null}return(t.flags&128)!==0?(t.lanes=n,t):(s=s!==null,s!==(e!==null&&e.memoizedState!==null)&&s&&(t.child.flags|=8192,(t.mode&1)!==0&&(e===null||(ke.current&1)!==0?Pe===0&&(Pe=3):Ki())),t.updateQueue!==null&&(t.flags|=4),Oe(t),null);case 4:return Vn(),Ri(e,t),e===null&&vr(t.stateNode.containerInfo),Oe(t),null;case 10:return oi(t.type._context),Oe(t),null;case 17:return qe(t.type)&&cs(),Oe(t),null;case 19:if(ve(ke),i=t.memoizedState,i===null)return Oe(t),null;if(s=(t.flags&128)!==0,u=i.rendering,u===null)if(s)Er(i,!1);else{if(Pe!==0||e!==null&&(e.flags&128)!==0)for(e=t.child;e!==null;){if(u=ks(e),u!==null){for(t.flags|=128,Er(i,!1),s=u.updateQueue,s!==null&&(t.updateQueue=s,t.flags|=4),t.subtreeFlags=0,s=n,n=t.child;n!==null;)i=n,e=s,i.flags&=14680066,u=i.alternate,u===null?(i.childLanes=0,i.lanes=e,i.child=null,i.subtreeFlags=0,i.memoizedProps=null,i.memoizedState=null,i.updateQueue=null,i.dependencies=null,i.stateNode=null):(i.childLanes=u.childLanes,i.lanes=u.lanes,i.child=u.child,i.subtreeFlags=0,i.deletions=null,i.memoizedProps=u.memoizedProps,i.memoizedState=u.memoizedState,i.updateQueue=u.updateQueue,i.type=u.type,e=u.dependencies,i.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),n=n.sibling;return fe(ke,ke.current&1|2),t.child}e=e.sibling}i.tail!==null&&Ne()>qn&&(t.flags|=128,s=!0,Er(i,!1),t.lanes=4194304)}else{if(!s)if(e=ks(u),e!==null){if(t.flags|=128,s=!0,n=e.updateQueue,n!==null&&(t.updateQueue=n,t.flags|=4),Er(i,!0),i.tail===null&&i.tailMode==="hidden"&&!u.alternate&&!xe)return Oe(t),null}else 2*Ne()-i.renderingStartTime>qn&&n!==1073741824&&(t.flags|=128,s=!0,Er(i,!1),t.lanes=4194304);i.isBackwards?(u.sibling=t.child,t.child=u):(n=i.last,n!==null?n.sibling=u:t.child=u,i.last=u)}return i.tail!==null?(t=i.tail,i.rendering=t,i.tail=t.sibling,i.renderingStartTime=Ne(),t.sibling=null,n=ke.current,fe(ke,s?n&1|2:n&1),t):(Oe(t),null);case 22:case 23:return Gi(),s=t.memoizedState!==null,e!==null&&e.memoizedState!==null!==s&&(t.flags|=8192),s&&(t.mode&1)!==0?(ut&1073741824)!==0&&(Oe(t),t.subtreeFlags&6&&(t.flags|=8192)):Oe(t),null;case 24:return null;case 25:return null}throw Error(l(156,t.tag))}function _m(e,t){switch(ti(t),t.tag){case 1:return qe(t.type)&&cs(),e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 3:return Vn(),ve(Ke),ve(Fe),pi(),e=t.flags,(e&65536)!==0&&(e&128)===0?(t.flags=e&-65537|128,t):null;case 5:return mi(t),null;case 13:if(ve(ke),e=t.memoizedState,e!==null&&e.dehydrated!==null){if(t.alternate===null)throw Error(l(340));On()}return e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 19:return ve(ke),null;case 4:return Vn(),null;case 10:return oi(t.type._context),null;case 22:case 23:return Gi(),null;case 24:return null;default:return null}}var Es=!1,We=!1,Tm=typeof WeakSet=="function"?WeakSet:Set,$=null;function Gn(e,t){var n=e.ref;if(n!==null)if(typeof n=="function")try{n(null)}catch(s){Se(e,t,s)}else n.current=null}function Ai(e,t,n){try{n()}catch(s){Se(e,t,s)}}var Oc=!1;function Em(e,t){if(Ga=Qr,e=yl(),Fa(e)){if("selectionStart"in e)var n={start:e.selectionStart,end:e.selectionEnd};else e:{n=(n=e.ownerDocument)&&n.defaultView||window;var s=n.getSelection&&n.getSelection();if(s&&s.rangeCount!==0){n=s.anchorNode;var a=s.anchorOffset,i=s.focusNode;s=s.focusOffset;try{n.nodeType,i.nodeType}catch{n=null;break e}var u=0,h=-1,p=-1,j=0,M=0,R=e,T=null;t:for(;;){for(var W;R!==n||a!==0&&R.nodeType!==3||(h=u+a),R!==i||s!==0&&R.nodeType!==3||(p=u+s),R.nodeType===3&&(u+=R.nodeValue.length),(W=R.firstChild)!==null;)T=R,R=W;for(;;){if(R===e)break t;if(T===n&&++j===a&&(h=u),T===i&&++M===s&&(p=u),(W=R.nextSibling)!==null)break;R=T,T=R.parentNode}R=W}n=h===-1||p===-1?null:{start:h,end:p}}else n=null}n=n||{start:0,end:0}}else n=null;for(Ka={focusedElem:e,selectionRange:n},Qr=!1,$=t;$!==null;)if(t=$,e=t.child,(t.subtreeFlags&1028)!==0&&e!==null)e.return=t,$=e;else for(;$!==null;){t=$;try{var H=t.alternate;if((t.flags&1024)!==0)switch(t.tag){case 0:case 11:case 15:break;case 1:if(H!==null){var G=H.memoizedProps,Ce=H.memoizedState,x=t.stateNode,g=x.getSnapshotBeforeUpdate(t.elementType===t.type?G:kt(t.type,G),Ce);x.__reactInternalSnapshotBeforeUpdate=g}break;case 3:var k=t.stateNode.containerInfo;k.nodeType===1?k.textContent="":k.nodeType===9&&k.documentElement&&k.removeChild(k.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(l(163))}}catch(D){Se(t,t.return,D)}if(e=t.sibling,e!==null){e.return=t.return,$=e;break}$=t.return}return H=Oc,Oc=!1,H}function Mr(e,t,n){var s=t.updateQueue;if(s=s!==null?s.lastEffect:null,s!==null){var a=s=s.next;do{if((a.tag&e)===e){var i=a.destroy;a.destroy=void 0,i!==void 0&&Ai(t,n,i)}a=a.next}while(a!==s)}}function Ms(e,t){if(t=t.updateQueue,t=t!==null?t.lastEffect:null,t!==null){var n=t=t.next;do{if((n.tag&e)===e){var s=n.create;n.destroy=s()}n=n.next}while(n!==t)}}function Di(e){var t=e.ref;if(t!==null){var n=e.stateNode;switch(e.tag){case 5:e=n;break;default:e=n}typeof t=="function"?t(e):t.current=e}}function Wc(e){var t=e.alternate;t!==null&&(e.alternate=null,Wc(t)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(t=e.stateNode,t!==null&&(delete t[Ct],delete t[xr],delete t[Ya],delete t[dm],delete t[mm])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function Uc(e){return e.tag===5||e.tag===3||e.tag===4}function $c(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||Uc(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Ii(e,t,n){var s=e.tag;if(s===5||s===6)e=e.stateNode,t?n.nodeType===8?n.parentNode.insertBefore(e,t):n.insertBefore(e,t):(n.nodeType===8?(t=n.parentNode,t.insertBefore(e,n)):(t=n,t.appendChild(e)),n=n._reactRootContainer,n!=null||t.onclick!==null||(t.onclick=os));else if(s!==4&&(e=e.child,e!==null))for(Ii(e,t,n),e=e.sibling;e!==null;)Ii(e,t,n),e=e.sibling}function zi(e,t,n){var s=e.tag;if(s===5||s===6)e=e.stateNode,t?n.insertBefore(e,t):n.appendChild(e);else if(s!==4&&(e=e.child,e!==null))for(zi(e,t,n),e=e.sibling;e!==null;)zi(e,t,n),e=e.sibling}var De=null,wt=!1;function Jt(e,t,n){for(n=n.child;n!==null;)Vc(e,t,n),n=n.sibling}function Vc(e,t,n){if(Nt&&typeof Nt.onCommitFiberUnmount=="function")try{Nt.onCommitFiberUnmount($r,n)}catch{}switch(n.tag){case 5:We||Gn(n,t);case 6:var s=De,a=wt;De=null,Jt(e,t,n),De=s,wt=a,De!==null&&(wt?(e=De,n=n.stateNode,e.nodeType===8?e.parentNode.removeChild(n):e.removeChild(n)):De.removeChild(n.stateNode));break;case 18:De!==null&&(wt?(e=De,n=n.stateNode,e.nodeType===8?Xa(e.parentNode,n):e.nodeType===1&&Xa(e,n),lr(e)):Xa(De,n.stateNode));break;case 4:s=De,a=wt,De=n.stateNode.containerInfo,wt=!0,Jt(e,t,n),De=s,wt=a;break;case 0:case 11:case 14:case 15:if(!We&&(s=n.updateQueue,s!==null&&(s=s.lastEffect,s!==null))){a=s=s.next;do{var i=a,u=i.destroy;i=i.tag,u!==void 0&&((i&2)!==0||(i&4)!==0)&&Ai(n,t,u),a=a.next}while(a!==s)}Jt(e,t,n);break;case 1:if(!We&&(Gn(n,t),s=n.stateNode,typeof s.componentWillUnmount=="function"))try{s.props=n.memoizedProps,s.state=n.memoizedState,s.componentWillUnmount()}catch(h){Se(n,t,h)}Jt(e,t,n);break;case 21:Jt(e,t,n);break;case 22:n.mode&1?(We=(s=We)||n.memoizedState!==null,Jt(e,t,n),We=s):Jt(e,t,n);break;default:Jt(e,t,n)}}function Hc(e){var t=e.updateQueue;if(t!==null){e.updateQueue=null;var n=e.stateNode;n===null&&(n=e.stateNode=new Tm),t.forEach(function(s){var a=Fm.bind(null,e,s);n.has(s)||(n.add(s),s.then(a,a))})}}function jt(e,t){var n=t.deletions;if(n!==null)for(var s=0;s<n.length;s++){var a=n[s];try{var i=e,u=t,h=u;e:for(;h!==null;){switch(h.tag){case 5:De=h.stateNode,wt=!1;break e;case 3:De=h.stateNode.containerInfo,wt=!0;break e;case 4:De=h.stateNode.containerInfo,wt=!0;break e}h=h.return}if(De===null)throw Error(l(160));Vc(i,u,a),De=null,wt=!1;var p=a.alternate;p!==null&&(p.return=null),a.return=null}catch(j){Se(a,t,j)}}if(t.subtreeFlags&12854)for(t=t.child;t!==null;)Gc(t,e),t=t.sibling}function Gc(e,t){var n=e.alternate,s=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(jt(t,e),Et(e),s&4){try{Mr(3,e,e.return),Ms(3,e)}catch(G){Se(e,e.return,G)}try{Mr(5,e,e.return)}catch(G){Se(e,e.return,G)}}break;case 1:jt(t,e),Et(e),s&512&&n!==null&&Gn(n,n.return);break;case 5:if(jt(t,e),Et(e),s&512&&n!==null&&Gn(n,n.return),e.flags&32){var a=e.stateNode;try{Yn(a,"")}catch(G){Se(e,e.return,G)}}if(s&4&&(a=e.stateNode,a!=null)){var i=e.memoizedProps,u=n!==null?n.memoizedProps:i,h=e.type,p=e.updateQueue;if(e.updateQueue=null,p!==null)try{h==="input"&&i.type==="radio"&&i.name!=null&&ko(a,i),pa(h,u);var j=pa(h,i);for(u=0;u<p.length;u+=2){var M=p[u],R=p[u+1];M==="style"?To(a,R):M==="dangerouslySetInnerHTML"?Co(a,R):M==="children"?Yn(a,R):Q(a,M,R,j)}switch(h){case"input":ca(a,i);break;case"textarea":bo(a,i);break;case"select":var T=a._wrapperState.wasMultiple;a._wrapperState.wasMultiple=!!i.multiple;var W=i.value;W!=null?Nn(a,!!i.multiple,W,!1):T!==!!i.multiple&&(i.defaultValue!=null?Nn(a,!!i.multiple,i.defaultValue,!0):Nn(a,!!i.multiple,i.multiple?[]:"",!1))}a[xr]=i}catch(G){Se(e,e.return,G)}}break;case 6:if(jt(t,e),Et(e),s&4){if(e.stateNode===null)throw Error(l(162));a=e.stateNode,i=e.memoizedProps;try{a.nodeValue=i}catch(G){Se(e,e.return,G)}}break;case 3:if(jt(t,e),Et(e),s&4&&n!==null&&n.memoizedState.isDehydrated)try{lr(t.containerInfo)}catch(G){Se(e,e.return,G)}break;case 4:jt(t,e),Et(e);break;case 13:jt(t,e),Et(e),a=e.child,a.flags&8192&&(i=a.memoizedState!==null,a.stateNode.isHidden=i,!i||a.alternate!==null&&a.alternate.memoizedState!==null||(Oi=Ne())),s&4&&Hc(e);break;case 22:if(M=n!==null&&n.memoizedState!==null,e.mode&1?(We=(j=We)||M,jt(t,e),We=j):jt(t,e),Et(e),s&8192){if(j=e.memoizedState!==null,(e.stateNode.isHidden=j)&&!M&&(e.mode&1)!==0)for($=e,M=e.child;M!==null;){for(R=$=M;$!==null;){switch(T=$,W=T.child,T.tag){case 0:case 11:case 14:case 15:Mr(4,T,T.return);break;case 1:Gn(T,T.return);var H=T.stateNode;if(typeof H.componentWillUnmount=="function"){s=T,n=T.return;try{t=s,H.props=t.memoizedProps,H.state=t.memoizedState,H.componentWillUnmount()}catch(G){Se(s,n,G)}}break;case 5:Gn(T,T.return);break;case 22:if(T.memoizedState!==null){Qc(R);continue}}W!==null?(W.return=T,$=W):Qc(R)}M=M.sibling}e:for(M=null,R=e;;){if(R.tag===5){if(M===null){M=R;try{a=R.stateNode,j?(i=a.style,typeof i.setProperty=="function"?i.setProperty("display","none","important"):i.display="none"):(h=R.stateNode,p=R.memoizedProps.style,u=p!=null&&p.hasOwnProperty("display")?p.display:null,h.style.display=_o("display",u))}catch(G){Se(e,e.return,G)}}}else if(R.tag===6){if(M===null)try{R.stateNode.nodeValue=j?"":R.memoizedProps}catch(G){Se(e,e.return,G)}}else if((R.tag!==22&&R.tag!==23||R.memoizedState===null||R===e)&&R.child!==null){R.child.return=R,R=R.child;continue}if(R===e)break e;for(;R.sibling===null;){if(R.return===null||R.return===e)break e;M===R&&(M=null),R=R.return}M===R&&(M=null),R.sibling.return=R.return,R=R.sibling}}break;case 19:jt(t,e),Et(e),s&4&&Hc(e);break;case 21:break;default:jt(t,e),Et(e)}}function Et(e){var t=e.flags;if(t&2){try{e:{for(var n=e.return;n!==null;){if(Uc(n)){var s=n;break e}n=n.return}throw Error(l(160))}switch(s.tag){case 5:var a=s.stateNode;s.flags&32&&(Yn(a,""),s.flags&=-33);var i=$c(e);zi(e,i,a);break;case 3:case 4:var u=s.stateNode.containerInfo,h=$c(e);Ii(e,h,u);break;default:throw Error(l(161))}}catch(p){Se(e,e.return,p)}e.flags&=-3}t&4096&&(e.flags&=-4097)}function Mm(e,t,n){$=e,Kc(e)}function Kc(e,t,n){for(var s=(e.mode&1)!==0;$!==null;){var a=$,i=a.child;if(a.tag===22&&s){var u=a.memoizedState!==null||Es;if(!u){var h=a.alternate,p=h!==null&&h.memoizedState!==null||We;h=Es;var j=We;if(Es=u,(We=p)&&!j)for($=a;$!==null;)u=$,p=u.child,u.tag===22&&u.memoizedState!==null?Xc(a):p!==null?(p.return=u,$=p):Xc(a);for(;i!==null;)$=i,Kc(i),i=i.sibling;$=a,Es=h,We=j}qc(e)}else(a.subtreeFlags&8772)!==0&&i!==null?(i.return=a,$=i):qc(e)}}function qc(e){for(;$!==null;){var t=$;if((t.flags&8772)!==0){var n=t.alternate;try{if((t.flags&8772)!==0)switch(t.tag){case 0:case 11:case 15:We||Ms(5,t);break;case 1:var s=t.stateNode;if(t.flags&4&&!We)if(n===null)s.componentDidMount();else{var a=t.elementType===t.type?n.memoizedProps:kt(t.type,n.memoizedProps);s.componentDidUpdate(a,n.memoizedState,s.__reactInternalSnapshotBeforeUpdate)}var i=t.updateQueue;i!==null&&Ql(t,i,s);break;case 3:var u=t.updateQueue;if(u!==null){if(n=null,t.child!==null)switch(t.child.tag){case 5:n=t.child.stateNode;break;case 1:n=t.child.stateNode}Ql(t,u,n)}break;case 5:var h=t.stateNode;if(n===null&&t.flags&4){n=h;var p=t.memoizedProps;switch(t.type){case"button":case"input":case"select":case"textarea":p.autoFocus&&n.focus();break;case"img":p.src&&(n.src=p.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(t.memoizedState===null){var j=t.alternate;if(j!==null){var M=j.memoizedState;if(M!==null){var R=M.dehydrated;R!==null&&lr(R)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(l(163))}We||t.flags&512&&Di(t)}catch(T){Se(t,t.return,T)}}if(t===e){$=null;break}if(n=t.sibling,n!==null){n.return=t.return,$=n;break}$=t.return}}function Qc(e){for(;$!==null;){var t=$;if(t===e){$=null;break}var n=t.sibling;if(n!==null){n.return=t.return,$=n;break}$=t.return}}function Xc(e){for(;$!==null;){var t=$;try{switch(t.tag){case 0:case 11:case 15:var n=t.return;try{Ms(4,t)}catch(p){Se(t,n,p)}break;case 1:var s=t.stateNode;if(typeof s.componentDidMount=="function"){var a=t.return;try{s.componentDidMount()}catch(p){Se(t,a,p)}}var i=t.return;try{Di(t)}catch(p){Se(t,i,p)}break;case 5:var u=t.return;try{Di(t)}catch(p){Se(t,u,p)}}}catch(p){Se(t,t.return,p)}if(t===e){$=null;break}var h=t.sibling;if(h!==null){h.return=t.return,$=h;break}$=t.return}}var Pm=Math.ceil,Ps=te.ReactCurrentDispatcher,Fi=te.ReactCurrentOwner,ft=te.ReactCurrentBatchConfig,oe=0,Re=null,_e=null,Ie=0,ut=0,Kn=Kt(0),Pe=0,Pr=null,gn=0,Ls=0,Bi=0,Lr=null,Xe=null,Oi=0,qn=1/0,Ft=null,Rs=!1,Wi=null,Zt=null,As=!1,en=null,Ds=0,Rr=0,Ui=null,Is=-1,zs=0;function He(){return(oe&6)!==0?Ne():Is!==-1?Is:Is=Ne()}function tn(e){return(e.mode&1)===0?1:(oe&2)!==0&&Ie!==0?Ie&-Ie:pm.transition!==null?(zs===0&&(zs=$o()),zs):(e=me,e!==0||(e=window.event,e=e===void 0?16:Jo(e.type)),e)}function bt(e,t,n,s){if(50<Rr)throw Rr=0,Ui=null,Error(l(185));rr(e,n,s),((oe&2)===0||e!==Re)&&(e===Re&&((oe&2)===0&&(Ls|=n),Pe===4&&nn(e,Ie)),Ye(e,s),n===1&&oe===0&&(t.mode&1)===0&&(qn=Ne()+500,ds&&Qt()))}function Ye(e,t){var n=e.callbackNode;pd(e,t);var s=Gr(e,e===Re?Ie:0);if(s===0)n!==null&&Oo(n),e.callbackNode=null,e.callbackPriority=0;else if(t=s&-s,e.callbackPriority!==t){if(n!=null&&Oo(n),t===1)e.tag===0?hm(Jc.bind(null,e)):zl(Jc.bind(null,e)),cm(function(){(oe&6)===0&&Qt()}),n=null;else{switch(Vo(s)){case 1:n=wa;break;case 4:n=Wo;break;case 16:n=Ur;break;case 536870912:n=Uo;break;default:n=Ur}n=iu(n,Yc.bind(null,e))}e.callbackPriority=t,e.callbackNode=n}}function Yc(e,t){if(Is=-1,zs=0,(oe&6)!==0)throw Error(l(327));var n=e.callbackNode;if(Qn()&&e.callbackNode!==n)return null;var s=Gr(e,e===Re?Ie:0);if(s===0)return null;if((s&30)!==0||(s&e.expiredLanes)!==0||t)t=Fs(e,s);else{t=s;var a=oe;oe|=2;var i=eu();(Re!==e||Ie!==t)&&(Ft=null,qn=Ne()+500,yn(e,t));do try{Am();break}catch(h){Zc(e,h)}while(!0);ii(),Ps.current=i,oe=a,_e!==null?t=0:(Re=null,Ie=0,t=Pe)}if(t!==0){if(t===2&&(a=ja(e),a!==0&&(s=a,t=$i(e,a))),t===1)throw n=Pr,yn(e,0),nn(e,s),Ye(e,Ne()),n;if(t===6)nn(e,s);else{if(a=e.current.alternate,(s&30)===0&&!Lm(a)&&(t=Fs(e,s),t===2&&(i=ja(e),i!==0&&(s=i,t=$i(e,i))),t===1))throw n=Pr,yn(e,0),nn(e,s),Ye(e,Ne()),n;switch(e.finishedWork=a,e.finishedLanes=s,t){case 0:case 1:throw Error(l(345));case 2:xn(e,Xe,Ft);break;case 3:if(nn(e,s),(s&130023424)===s&&(t=Oi+500-Ne(),10<t)){if(Gr(e,0)!==0)break;if(a=e.suspendedLanes,(a&s)!==s){He(),e.pingedLanes|=e.suspendedLanes&a;break}e.timeoutHandle=Qa(xn.bind(null,e,Xe,Ft),t);break}xn(e,Xe,Ft);break;case 4:if(nn(e,s),(s&4194240)===s)break;for(t=e.eventTimes,a=-1;0<s;){var u=31-vt(s);i=1<<u,u=t[u],u>a&&(a=u),s&=~i}if(s=a,s=Ne()-s,s=(120>s?120:480>s?480:1080>s?1080:1920>s?1920:3e3>s?3e3:4320>s?4320:1960*Pm(s/1960))-s,10<s){e.timeoutHandle=Qa(xn.bind(null,e,Xe,Ft),s);break}xn(e,Xe,Ft);break;case 5:xn(e,Xe,Ft);break;default:throw Error(l(329))}}}return Ye(e,Ne()),e.callbackNode===n?Yc.bind(null,e):null}function $i(e,t){var n=Lr;return e.current.memoizedState.isDehydrated&&(yn(e,t).flags|=256),e=Fs(e,t),e!==2&&(t=Xe,Xe=n,t!==null&&Vi(t)),e}function Vi(e){Xe===null?Xe=e:Xe.push.apply(Xe,e)}function Lm(e){for(var t=e;;){if(t.flags&16384){var n=t.updateQueue;if(n!==null&&(n=n.stores,n!==null))for(var s=0;s<n.length;s++){var a=n[s],i=a.getSnapshot;a=a.value;try{if(!yt(i(),a))return!1}catch{return!1}}}if(n=t.child,t.subtreeFlags&16384&&n!==null)n.return=t,t=n;else{if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return!0;t=t.return}t.sibling.return=t.return,t=t.sibling}}return!0}function nn(e,t){for(t&=~Bi,t&=~Ls,e.suspendedLanes|=t,e.pingedLanes&=~t,e=e.expirationTimes;0<t;){var n=31-vt(t),s=1<<n;e[n]=-1,t&=~s}}function Jc(e){if((oe&6)!==0)throw Error(l(327));Qn();var t=Gr(e,0);if((t&1)===0)return Ye(e,Ne()),null;var n=Fs(e,t);if(e.tag!==0&&n===2){var s=ja(e);s!==0&&(t=s,n=$i(e,s))}if(n===1)throw n=Pr,yn(e,0),nn(e,t),Ye(e,Ne()),n;if(n===6)throw Error(l(345));return e.finishedWork=e.current.alternate,e.finishedLanes=t,xn(e,Xe,Ft),Ye(e,Ne()),null}function Hi(e,t){var n=oe;oe|=1;try{return e(t)}finally{oe=n,oe===0&&(qn=Ne()+500,ds&&Qt())}}function vn(e){en!==null&&en.tag===0&&(oe&6)===0&&Qn();var t=oe;oe|=1;var n=ft.transition,s=me;try{if(ft.transition=null,me=1,e)return e()}finally{me=s,ft.transition=n,oe=t,(oe&6)===0&&Qt()}}function Gi(){ut=Kn.current,ve(Kn)}function yn(e,t){e.finishedWork=null,e.finishedLanes=0;var n=e.timeoutHandle;if(n!==-1&&(e.timeoutHandle=-1,lm(n)),_e!==null)for(n=_e.return;n!==null;){var s=n;switch(ti(s),s.tag){case 1:s=s.type.childContextTypes,s!=null&&cs();break;case 3:Vn(),ve(Ke),ve(Fe),pi();break;case 5:mi(s);break;case 4:Vn();break;case 13:ve(ke);break;case 19:ve(ke);break;case 10:oi(s.type._context);break;case 22:case 23:Gi()}n=n.return}if(Re=e,_e=e=rn(e.current,null),Ie=ut=t,Pe=0,Pr=null,Bi=Ls=gn=0,Xe=Lr=null,hn!==null){for(t=0;t<hn.length;t++)if(n=hn[t],s=n.interleaved,s!==null){n.interleaved=null;var a=s.next,i=n.pending;if(i!==null){var u=i.next;i.next=a,s.next=u}n.pending=s}hn=null}return e}function Zc(e,t){do{var n=_e;try{if(ii(),ws.current=Ns,js){for(var s=we.memoizedState;s!==null;){var a=s.queue;a!==null&&(a.pending=null),s=s.next}js=!1}if(fn=0,Le=Me=we=null,Nr=!1,Cr=0,Fi.current=null,n===null||n.return===null){Pe=1,Pr=t,_e=null;break}e:{var i=e,u=n.return,h=n,p=t;if(t=Ie,h.flags|=32768,p!==null&&typeof p=="object"&&typeof p.then=="function"){var j=p,M=h,R=M.tag;if((M.mode&1)===0&&(R===0||R===11||R===15)){var T=M.alternate;T?(M.updateQueue=T.updateQueue,M.memoizedState=T.memoizedState,M.lanes=T.lanes):(M.updateQueue=null,M.memoizedState=null)}var W=Sc(u);if(W!==null){W.flags&=-257,Nc(W,u,h,i,t),W.mode&1&&bc(i,j,t),t=W,p=j;var H=t.updateQueue;if(H===null){var G=new Set;G.add(p),t.updateQueue=G}else H.add(p);break e}else{if((t&1)===0){bc(i,j,t),Ki();break e}p=Error(l(426))}}else if(xe&&h.mode&1){var Ce=Sc(u);if(Ce!==null){(Ce.flags&65536)===0&&(Ce.flags|=256),Nc(Ce,u,h,i,t),si(Hn(p,h));break e}}i=p=Hn(p,h),Pe!==4&&(Pe=2),Lr===null?Lr=[i]:Lr.push(i),i=u;do{switch(i.tag){case 3:i.flags|=65536,t&=-t,i.lanes|=t;var x=wc(i,p,t);ql(i,x);break e;case 1:h=p;var g=i.type,k=i.stateNode;if((i.flags&128)===0&&(typeof g.getDerivedStateFromError=="function"||k!==null&&typeof k.componentDidCatch=="function"&&(Zt===null||!Zt.has(k)))){i.flags|=65536,t&=-t,i.lanes|=t;var D=jc(i,h,t);ql(i,D);break e}}i=i.return}while(i!==null)}nu(n)}catch(K){t=K,_e===n&&n!==null&&(_e=n=n.return);continue}break}while(!0)}function eu(){var e=Ps.current;return Ps.current=Ns,e===null?Ns:e}function Ki(){(Pe===0||Pe===3||Pe===2)&&(Pe=4),Re===null||(gn&268435455)===0&&(Ls&268435455)===0||nn(Re,Ie)}function Fs(e,t){var n=oe;oe|=2;var s=eu();(Re!==e||Ie!==t)&&(Ft=null,yn(e,t));do try{Rm();break}catch(a){Zc(e,a)}while(!0);if(ii(),oe=n,Ps.current=s,_e!==null)throw Error(l(261));return Re=null,Ie=0,Pe}function Rm(){for(;_e!==null;)tu(_e)}function Am(){for(;_e!==null&&!ad();)tu(_e)}function tu(e){var t=au(e.alternate,e,ut);e.memoizedProps=e.pendingProps,t===null?nu(e):_e=t,Fi.current=null}function nu(e){var t=e;do{var n=t.alternate;if(e=t.return,(t.flags&32768)===0){if(n=Cm(n,t,ut),n!==null){_e=n;return}}else{if(n=_m(n,t),n!==null){n.flags&=32767,_e=n;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{Pe=6,_e=null;return}}if(t=t.sibling,t!==null){_e=t;return}_e=t=e}while(t!==null);Pe===0&&(Pe=5)}function xn(e,t,n){var s=me,a=ft.transition;try{ft.transition=null,me=1,Dm(e,t,n,s)}finally{ft.transition=a,me=s}return null}function Dm(e,t,n,s){do Qn();while(en!==null);if((oe&6)!==0)throw Error(l(327));n=e.finishedWork;var a=e.finishedLanes;if(n===null)return null;if(e.finishedWork=null,e.finishedLanes=0,n===e.current)throw Error(l(177));e.callbackNode=null,e.callbackPriority=0;var i=n.lanes|n.childLanes;if(fd(e,i),e===Re&&(_e=Re=null,Ie=0),(n.subtreeFlags&2064)===0&&(n.flags&2064)===0||As||(As=!0,iu(Ur,function(){return Qn(),null})),i=(n.flags&15990)!==0,(n.subtreeFlags&15990)!==0||i){i=ft.transition,ft.transition=null;var u=me;me=1;var h=oe;oe|=4,Fi.current=null,Em(e,n),Gc(n,e),tm(Ka),Qr=!!Ga,Ka=Ga=null,e.current=n,Mm(n),id(),oe=h,me=u,ft.transition=i}else e.current=n;if(As&&(As=!1,en=e,Ds=a),i=e.pendingLanes,i===0&&(Zt=null),cd(n.stateNode),Ye(e,Ne()),t!==null)for(s=e.onRecoverableError,n=0;n<t.length;n++)a=t[n],s(a.value,{componentStack:a.stack,digest:a.digest});if(Rs)throw Rs=!1,e=Wi,Wi=null,e;return(Ds&1)!==0&&e.tag!==0&&Qn(),i=e.pendingLanes,(i&1)!==0?e===Ui?Rr++:(Rr=0,Ui=e):Rr=0,Qt(),null}function Qn(){if(en!==null){var e=Vo(Ds),t=ft.transition,n=me;try{if(ft.transition=null,me=16>e?16:e,en===null)var s=!1;else{if(e=en,en=null,Ds=0,(oe&6)!==0)throw Error(l(331));var a=oe;for(oe|=4,$=e.current;$!==null;){var i=$,u=i.child;if(($.flags&16)!==0){var h=i.deletions;if(h!==null){for(var p=0;p<h.length;p++){var j=h[p];for($=j;$!==null;){var M=$;switch(M.tag){case 0:case 11:case 15:Mr(8,M,i)}var R=M.child;if(R!==null)R.return=M,$=R;else for(;$!==null;){M=$;var T=M.sibling,W=M.return;if(Wc(M),M===j){$=null;break}if(T!==null){T.return=W,$=T;break}$=W}}}var H=i.alternate;if(H!==null){var G=H.child;if(G!==null){H.child=null;do{var Ce=G.sibling;G.sibling=null,G=Ce}while(G!==null)}}$=i}}if((i.subtreeFlags&2064)!==0&&u!==null)u.return=i,$=u;else e:for(;$!==null;){if(i=$,(i.flags&2048)!==0)switch(i.tag){case 0:case 11:case 15:Mr(9,i,i.return)}var x=i.sibling;if(x!==null){x.return=i.return,$=x;break e}$=i.return}}var g=e.current;for($=g;$!==null;){u=$;var k=u.child;if((u.subtreeFlags&2064)!==0&&k!==null)k.return=u,$=k;else e:for(u=g;$!==null;){if(h=$,(h.flags&2048)!==0)try{switch(h.tag){case 0:case 11:case 15:Ms(9,h)}}catch(K){Se(h,h.return,K)}if(h===u){$=null;break e}var D=h.sibling;if(D!==null){D.return=h.return,$=D;break e}$=h.return}}if(oe=a,Qt(),Nt&&typeof Nt.onPostCommitFiberRoot=="function")try{Nt.onPostCommitFiberRoot($r,e)}catch{}s=!0}return s}finally{me=n,ft.transition=t}}return!1}function ru(e,t,n){t=Hn(n,t),t=wc(e,t,1),e=Yt(e,t,1),t=He(),e!==null&&(rr(e,1,t),Ye(e,t))}function Se(e,t,n){if(e.tag===3)ru(e,e,n);else for(;t!==null;){if(t.tag===3){ru(t,e,n);break}else if(t.tag===1){var s=t.stateNode;if(typeof t.type.getDerivedStateFromError=="function"||typeof s.componentDidCatch=="function"&&(Zt===null||!Zt.has(s))){e=Hn(n,e),e=jc(t,e,1),t=Yt(t,e,1),e=He(),t!==null&&(rr(t,1,e),Ye(t,e));break}}t=t.return}}function Im(e,t,n){var s=e.pingCache;s!==null&&s.delete(t),t=He(),e.pingedLanes|=e.suspendedLanes&n,Re===e&&(Ie&n)===n&&(Pe===4||Pe===3&&(Ie&130023424)===Ie&&500>Ne()-Oi?yn(e,0):Bi|=n),Ye(e,t)}function su(e,t){t===0&&((e.mode&1)===0?t=1:(t=Hr,Hr<<=1,(Hr&130023424)===0&&(Hr=4194304)));var n=He();e=Dt(e,t),e!==null&&(rr(e,t,n),Ye(e,n))}function zm(e){var t=e.memoizedState,n=0;t!==null&&(n=t.retryLane),su(e,n)}function Fm(e,t){var n=0;switch(e.tag){case 13:var s=e.stateNode,a=e.memoizedState;a!==null&&(n=a.retryLane);break;case 19:s=e.stateNode;break;default:throw Error(l(314))}s!==null&&s.delete(t),su(e,n)}var au;au=function(e,t,n){if(e!==null)if(e.memoizedProps!==t.pendingProps||Ke.current)Qe=!0;else{if((e.lanes&n)===0&&(t.flags&128)===0)return Qe=!1,Nm(e,t,n);Qe=(e.flags&131072)!==0}else Qe=!1,xe&&(t.flags&1048576)!==0&&Fl(t,hs,t.index);switch(t.lanes=0,t.tag){case 2:var s=t.type;Ts(e,t),e=t.pendingProps;var a=zn(t,Fe.current);$n(t,n),a=vi(null,t,s,e,a,n);var i=yi();return t.flags|=1,typeof a=="object"&&a!==null&&typeof a.render=="function"&&a.$$typeof===void 0?(t.tag=1,t.memoizedState=null,t.updateQueue=null,qe(s)?(i=!0,us(t)):i=!1,t.memoizedState=a.state!==null&&a.state!==void 0?a.state:null,ui(t),a.updater=Cs,t.stateNode=a,a._reactInternals=t,Si(t,s,e,n),t=Ti(null,t,s,!0,i,n)):(t.tag=0,xe&&i&&ei(t),Ve(null,t,a,n),t=t.child),t;case 16:s=t.elementType;e:{switch(Ts(e,t),e=t.pendingProps,a=s._init,s=a(s._payload),t.type=s,a=t.tag=Om(s),e=kt(s,e),a){case 0:t=_i(null,t,s,e,n);break e;case 1:t=Pc(null,t,s,e,n);break e;case 11:t=Cc(null,t,s,e,n);break e;case 14:t=_c(null,t,s,kt(s.type,e),n);break e}throw Error(l(306,s,""))}return t;case 0:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:kt(s,a),_i(e,t,s,a,n);case 1:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:kt(s,a),Pc(e,t,s,a,n);case 3:e:{if(Lc(t),e===null)throw Error(l(387));s=t.pendingProps,i=t.memoizedState,a=i.element,Kl(e,t),xs(t,s,null,n);var u=t.memoizedState;if(s=u.element,i.isDehydrated)if(i={element:s,isDehydrated:!1,cache:u.cache,pendingSuspenseBoundaries:u.pendingSuspenseBoundaries,transitions:u.transitions},t.updateQueue.baseState=i,t.memoizedState=i,t.flags&256){a=Hn(Error(l(423)),t),t=Rc(e,t,s,n,a);break e}else if(s!==a){a=Hn(Error(l(424)),t),t=Rc(e,t,s,n,a);break e}else for(ct=Gt(t.stateNode.containerInfo.firstChild),lt=t,xe=!0,xt=null,n=Hl(t,null,s,n),t.child=n;n;)n.flags=n.flags&-3|4096,n=n.sibling;else{if(On(),s===a){t=zt(e,t,n);break e}Ve(e,t,s,n)}t=t.child}return t;case 5:return Xl(t),e===null&&ri(t),s=t.type,a=t.pendingProps,i=e!==null?e.memoizedProps:null,u=a.children,qa(s,a)?u=null:i!==null&&qa(s,i)&&(t.flags|=32),Mc(e,t),Ve(e,t,u,n),t.child;case 6:return e===null&&ri(t),null;case 13:return Ac(e,t,n);case 4:return di(t,t.stateNode.containerInfo),s=t.pendingProps,e===null?t.child=Wn(t,null,s,n):Ve(e,t,s,n),t.child;case 11:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:kt(s,a),Cc(e,t,s,a,n);case 7:return Ve(e,t,t.pendingProps,n),t.child;case 8:return Ve(e,t,t.pendingProps.children,n),t.child;case 12:return Ve(e,t,t.pendingProps.children,n),t.child;case 10:e:{if(s=t.type._context,a=t.pendingProps,i=t.memoizedProps,u=a.value,fe(gs,s._currentValue),s._currentValue=u,i!==null)if(yt(i.value,u)){if(i.children===a.children&&!Ke.current){t=zt(e,t,n);break e}}else for(i=t.child,i!==null&&(i.return=t);i!==null;){var h=i.dependencies;if(h!==null){u=i.child;for(var p=h.firstContext;p!==null;){if(p.context===s){if(i.tag===1){p=It(-1,n&-n),p.tag=2;var j=i.updateQueue;if(j!==null){j=j.shared;var M=j.pending;M===null?p.next=p:(p.next=M.next,M.next=p),j.pending=p}}i.lanes|=n,p=i.alternate,p!==null&&(p.lanes|=n),li(i.return,n,t),h.lanes|=n;break}p=p.next}}else if(i.tag===10)u=i.type===t.type?null:i.child;else if(i.tag===18){if(u=i.return,u===null)throw Error(l(341));u.lanes|=n,h=u.alternate,h!==null&&(h.lanes|=n),li(u,n,t),u=i.sibling}else u=i.child;if(u!==null)u.return=i;else for(u=i;u!==null;){if(u===t){u=null;break}if(i=u.sibling,i!==null){i.return=u.return,u=i;break}u=u.return}i=u}Ve(e,t,a.children,n),t=t.child}return t;case 9:return a=t.type,s=t.pendingProps.children,$n(t,n),a=ht(a),s=s(a),t.flags|=1,Ve(e,t,s,n),t.child;case 14:return s=t.type,a=kt(s,t.pendingProps),a=kt(s.type,a),_c(e,t,s,a,n);case 15:return Tc(e,t,t.type,t.pendingProps,n);case 17:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:kt(s,a),Ts(e,t),t.tag=1,qe(s)?(e=!0,us(t)):e=!1,$n(t,n),xc(t,s,a),Si(t,s,a,n),Ti(null,t,s,!0,e,n);case 19:return Ic(e,t,n);case 22:return Ec(e,t,n)}throw Error(l(156,t.tag))};function iu(e,t){return Bo(e,t)}function Bm(e,t,n,s){this.tag=e,this.key=n,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=t,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=s,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function gt(e,t,n,s){return new Bm(e,t,n,s)}function qi(e){return e=e.prototype,!(!e||!e.isReactComponent)}function Om(e){if(typeof e=="function")return qi(e)?1:0;if(e!=null){if(e=e.$$typeof,e===ze)return 11;if(e===St)return 14}return 2}function rn(e,t){var n=e.alternate;return n===null?(n=gt(e.tag,t,e.key,e.mode),n.elementType=e.elementType,n.type=e.type,n.stateNode=e.stateNode,n.alternate=e,e.alternate=n):(n.pendingProps=t,n.type=e.type,n.flags=0,n.subtreeFlags=0,n.deletions=null),n.flags=e.flags&14680064,n.childLanes=e.childLanes,n.lanes=e.lanes,n.child=e.child,n.memoizedProps=e.memoizedProps,n.memoizedState=e.memoizedState,n.updateQueue=e.updateQueue,t=e.dependencies,n.dependencies=t===null?null:{lanes:t.lanes,firstContext:t.firstContext},n.sibling=e.sibling,n.index=e.index,n.ref=e.ref,n}function Bs(e,t,n,s,a,i){var u=2;if(s=e,typeof e=="function")qi(e)&&(u=1);else if(typeof e=="string")u=5;else e:switch(e){case X:return kn(n.children,a,i,t);case he:u=8,a|=8;break;case je:return e=gt(12,n,t,a|2),e.elementType=je,e.lanes=i,e;case $e:return e=gt(13,n,t,a),e.elementType=$e,e.lanes=i,e;case at:return e=gt(19,n,t,a),e.elementType=at,e.lanes=i,e;case be:return Os(n,a,i,t);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case st:u=10;break e;case Ue:u=9;break e;case ze:u=11;break e;case St:u=14;break e;case Ge:u=16,s=null;break e}throw Error(l(130,e==null?e:typeof e,""))}return t=gt(u,n,t,a),t.elementType=e,t.type=s,t.lanes=i,t}function kn(e,t,n,s){return e=gt(7,e,s,t),e.lanes=n,e}function Os(e,t,n,s){return e=gt(22,e,s,t),e.elementType=be,e.lanes=n,e.stateNode={isHidden:!1},e}function Qi(e,t,n){return e=gt(6,e,null,t),e.lanes=n,e}function Xi(e,t,n){return t=gt(4,e.children!==null?e.children:[],e.key,t),t.lanes=n,t.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},t}function Wm(e,t,n,s,a){this.tag=t,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=ba(0),this.expirationTimes=ba(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=ba(0),this.identifierPrefix=s,this.onRecoverableError=a,this.mutableSourceEagerHydrationData=null}function Yi(e,t,n,s,a,i,u,h,p){return e=new Wm(e,t,n,h,p),t===1?(t=1,i===!0&&(t|=8)):t=0,i=gt(3,null,null,t),e.current=i,i.stateNode=e,i.memoizedState={element:s,isDehydrated:n,cache:null,transitions:null,pendingSuspenseBoundaries:null},ui(i),e}function Um(e,t,n){var s=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:_,key:s==null?null:""+s,children:e,containerInfo:t,implementation:n}}function ou(e){if(!e)return qt;e=e._reactInternals;e:{if(ln(e)!==e||e.tag!==1)throw Error(l(170));var t=e;do{switch(t.tag){case 3:t=t.stateNode.context;break e;case 1:if(qe(t.type)){t=t.stateNode.__reactInternalMemoizedMergedChildContext;break e}}t=t.return}while(t!==null);throw Error(l(171))}if(e.tag===1){var n=e.type;if(qe(n))return Dl(e,n,t)}return t}function lu(e,t,n,s,a,i,u,h,p){return e=Yi(n,s,!0,e,a,i,u,h,p),e.context=ou(null),n=e.current,s=He(),a=tn(n),i=It(s,a),i.callback=t??null,Yt(n,i,a),e.current.lanes=a,rr(e,a,s),Ye(e,s),e}function Ws(e,t,n,s){var a=t.current,i=He(),u=tn(a);return n=ou(n),t.context===null?t.context=n:t.pendingContext=n,t=It(i,u),t.payload={element:e},s=s===void 0?null:s,s!==null&&(t.callback=s),e=Yt(a,t,u),e!==null&&(bt(e,a,u,i),ys(e,a,u)),u}function Us(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function cu(e,t){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var n=e.retryLane;e.retryLane=n!==0&&n<t?n:t}}function Ji(e,t){cu(e,t),(e=e.alternate)&&cu(e,t)}function $m(){return null}var uu=typeof reportError=="function"?reportError:function(e){console.error(e)};function Zi(e){this._internalRoot=e}$s.prototype.render=Zi.prototype.render=function(e){var t=this._internalRoot;if(t===null)throw Error(l(409));Ws(e,t,null,null)},$s.prototype.unmount=Zi.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var t=e.containerInfo;vn(function(){Ws(null,e,null,null)}),t[Pt]=null}};function $s(e){this._internalRoot=e}$s.prototype.unstable_scheduleHydration=function(e){if(e){var t=Ko();e={blockedOn:null,target:e,priority:t};for(var n=0;n<$t.length&&t!==0&&t<$t[n].priority;n++);$t.splice(n,0,e),n===0&&Xo(e)}};function eo(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function Vs(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function du(){}function Vm(e,t,n,s,a){if(a){if(typeof s=="function"){var i=s;s=function(){var j=Us(u);i.call(j)}}var u=lu(t,s,e,0,null,!1,!1,"",du);return e._reactRootContainer=u,e[Pt]=u.current,vr(e.nodeType===8?e.parentNode:e),vn(),u}for(;a=e.lastChild;)e.removeChild(a);if(typeof s=="function"){var h=s;s=function(){var j=Us(p);h.call(j)}}var p=Yi(e,0,!1,null,null,!1,!1,"",du);return e._reactRootContainer=p,e[Pt]=p.current,vr(e.nodeType===8?e.parentNode:e),vn(function(){Ws(t,p,n,s)}),p}function Hs(e,t,n,s,a){var i=n._reactRootContainer;if(i){var u=i;if(typeof a=="function"){var h=a;a=function(){var p=Us(u);h.call(p)}}Ws(t,u,e,a)}else u=Vm(n,t,e,a,s);return Us(u)}Ho=function(e){switch(e.tag){case 3:var t=e.stateNode;if(t.current.memoizedState.isDehydrated){var n=nr(t.pendingLanes);n!==0&&(Sa(t,n|1),Ye(t,Ne()),(oe&6)===0&&(qn=Ne()+500,Qt()))}break;case 13:vn(function(){var s=Dt(e,1);if(s!==null){var a=He();bt(s,e,1,a)}}),Ji(e,1)}},Na=function(e){if(e.tag===13){var t=Dt(e,134217728);if(t!==null){var n=He();bt(t,e,134217728,n)}Ji(e,134217728)}},Go=function(e){if(e.tag===13){var t=tn(e),n=Dt(e,t);if(n!==null){var s=He();bt(n,e,t,s)}Ji(e,t)}},Ko=function(){return me},qo=function(e,t){var n=me;try{return me=e,t()}finally{me=n}},va=function(e,t,n){switch(t){case"input":if(ca(e,n),t=n.name,n.type==="radio"&&t!=null){for(n=e;n.parentNode;)n=n.parentNode;for(n=n.querySelectorAll("input[name="+JSON.stringify(""+t)+'][type="radio"]'),t=0;t<n.length;t++){var s=n[t];if(s!==e&&s.form===e.form){var a=ls(s);if(!a)throw Error(l(90));yo(s),ca(s,a)}}}break;case"textarea":bo(e,n);break;case"select":t=n.value,t!=null&&Nn(e,!!n.multiple,t,!1)}},Lo=Hi,Ro=vn;var Hm={usingClientEntryPoint:!1,Events:[kr,Dn,ls,Mo,Po,Hi]},Ar={findFiberByHostInstance:cn,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},Gm={bundleType:Ar.bundleType,version:Ar.version,rendererPackageName:Ar.rendererPackageName,rendererConfig:Ar.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:te.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=zo(e),e===null?null:e.stateNode},findFiberByHostInstance:Ar.findFiberByHostInstance||$m,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Gs=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Gs.isDisabled&&Gs.supportsFiber)try{$r=Gs.inject(Gm),Nt=Gs}catch{}}return Je.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Hm,Je.createPortal=function(e,t){var n=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!eo(t))throw Error(l(200));return Um(e,t,null,n)},Je.createRoot=function(e,t){if(!eo(e))throw Error(l(299));var n=!1,s="",a=uu;return t!=null&&(t.unstable_strictMode===!0&&(n=!0),t.identifierPrefix!==void 0&&(s=t.identifierPrefix),t.onRecoverableError!==void 0&&(a=t.onRecoverableError)),t=Yi(e,1,!1,null,null,n,!1,s,a),e[Pt]=t.current,vr(e.nodeType===8?e.parentNode:e),new Zi(t)},Je.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var t=e._reactInternals;if(t===void 0)throw typeof e.render=="function"?Error(l(188)):(e=Object.keys(e).join(","),Error(l(268,e)));return e=zo(t),e=e===null?null:e.stateNode,e},Je.flushSync=function(e){return vn(e)},Je.hydrate=function(e,t,n){if(!Vs(t))throw Error(l(200));return Hs(null,e,t,!0,n)},Je.hydrateRoot=function(e,t,n){if(!eo(e))throw Error(l(405));var s=n!=null&&n.hydratedSources||null,a=!1,i="",u=uu;if(n!=null&&(n.unstable_strictMode===!0&&(a=!0),n.identifierPrefix!==void 0&&(i=n.identifierPrefix),n.onRecoverableError!==void 0&&(u=n.onRecoverableError)),t=lu(t,null,e,1,n??null,a,!1,i,u),e[Pt]=t.current,vr(e),s)for(e=0;e<s.length;e++)n=s[e],a=n._getVersion,a=a(n._source),t.mutableSourceEagerHydrationData==null?t.mutableSourceEagerHydrationData=[n,a]:t.mutableSourceEagerHydrationData.push(n,a);return new $s(t)},Je.render=function(e,t,n){if(!Vs(t))throw Error(l(200));return Hs(null,e,t,!1,n)},Je.unmountComponentAtNode=function(e){if(!Vs(e))throw Error(l(40));return e._reactRootContainer?(vn(function(){Hs(null,null,e,!1,function(){e._reactRootContainer=null,e[Pt]=null})}),!0):!1},Je.unstable_batchedUpdates=Hi,Je.unstable_renderSubtreeIntoContainer=function(e,t,n,s){if(!Vs(n))throw Error(l(200));if(e==null||e._reactInternals===void 0)throw Error(l(38));return Hs(e,t,n,!1,s)},Je.version="18.3.1-next-f1338f8080-20240426",Je}var ku;function nh(){if(ku)return ro.exports;ku=1;function o(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(o)}catch(c){console.error(c)}}return o(),ro.exports=th(),ro.exports}var wu;function rh(){if(wu)return Ks;wu=1;var o=nh();return Ks.createRoot=o.createRoot,Ks.hydrateRoot=o.hydrateRoot,Ks}var sh=rh();class ah extends Error{constructor(l,d){super(l);mu(this,"status");this.status=d}}async function nt(o,c){const l=await fetch(o,{...c,credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json",...c==null?void 0:c.headers}}),d=await l.json().catch(()=>({}));if(!l.ok)throw new ah(d.error||l.statusText||"Request failed",l.status);return d}const ih=()=>nt("/auth/status"),oh=()=>nt("/api/config"),Ou=()=>nt("/api/botstats"),lh=()=>nt("/api/commands"),ch=()=>nt("/api/guilds"),uh=()=>nt("/api/me/overview"),dh=o=>nt(`/api/guild/${o}/overview`),mh=o=>nt(`/api/guild/${o}/levels`),ju=o=>nt(`/api/guild/${o}/config`),bu=o=>nt(`/api/guild/${o}/resources`);function ra(o,c,l,d){return nt(`/api/guild/${o}/config/${c}`,{method:"POST",headers:d?{"X-CSRF-Token":d}:void 0,body:JSON.stringify(l)})}function hh(o,c,l){return nt(`/api/guild/${o}/config/profile`,{method:"POST",headers:l?{"X-CSRF-Token":l}:void 0,body:JSON.stringify(c)})}function Wu(o){return o.replace(/\/+$/,"")||"/"}function Su(o=window.location.pathname){const c=Wu(o);return c==="/commands"?"commands":c==="/docs"?"docs":c.startsWith("/docs/")?"docs-detail":c==="/dashboard"||c.startsWith("/dashboard/")?"dashboard":c==="/privacy"?"privacy":c==="/terms"?"terms":c==="/community"?"community":c==="/donate"||c.startsWith("/donate")?"donate":c==="/transcript"||c.startsWith("/transcript/")?"transcript":c==="/changelog"?"changelog":c.startsWith("/changelog/")?"changelog-detail":"home"}function Ir(o,c="overview"){return o?`/dashboard/${o}/${c}`:"/dashboard"}function Nu(){return"/dashboard/servers"}function Cu(){const o=Wu(window.location.pathname).split("/").filter(Boolean),c=["overview","leveling","moderation","server","ai","customization"];return o[1]==="servers"?{view:"servers",guildId:null,section:"overview"}:o[1]?{view:"guild",guildId:o[1]||null,section:c.includes(o[2])?o[2]:"overview"}:{view:"overview",guildId:null,section:"overview"}}function ie(o){o.startsWith("/")&&(window.history.pushState({},"",o),window.dispatchEvent(new PopStateEvent("popstate")),window.scrollTo({top:0,behavior:"smooth"}))}function ea({onNavigate:o}){return r.jsxs("a",{className:"brand",href:"/",onClick:c=>{c.preventDefault(),o?o():ie("/")},children:[r.jsx("span",{className:"brand-mark",children:"n"}),r.jsx("span",{children:"niko"})]})}function Bt(){return r.jsxs("footer",{className:"site-footer",children:[r.jsx(ea,{}),r.jsx("span",{children:"Built for communities that care."}),r.jsxs("div",{children:[r.jsx("a",{href:"/changelog",onClick:o=>{o.preventDefault(),ie("/changelog")},children:"Changelog"}),r.jsx("a",{href:"/privacy",onClick:o=>{o.preventDefault(),ie("/privacy")},children:"Privacy"}),r.jsx("a",{href:"/terms",onClick:o=>{o.preventDefault(),ie("/terms")},children:"Terms"}),r.jsx("a",{href:"/community",onClick:o=>{o.preventDefault(),ie("/community")},children:"Community Policy"}),r.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"GitHub"})]})]})}/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Uu=(...o)=>o.filter((c,l,d)=>!!c&&c.trim()!==""&&d.indexOf(c)===l).join(" ").trim();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ph=o=>o.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const fh=o=>o.replace(/^([A-Z])|[\s-_]+(\w)/g,(c,l,d)=>d?d.toUpperCase():l.toLowerCase());/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const _u=o=>{const c=fh(o);return c.charAt(0).toUpperCase()+c.slice(1)};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var io={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const gh=o=>{for(const c in o)if(c.startsWith("aria-")||c==="role"||c==="title")return!0;return!1},vh=A.createContext({}),yh=()=>A.useContext(vh),xh=A.forwardRef(({color:o,size:c,strokeWidth:l,absoluteStrokeWidth:d,className:m="",children:f,iconNode:v,...P},w)=>{const{size:F=24,strokeWidth:N=2,absoluteStrokeWidth:C=!1,color:L="currentColor",className:I=""}=yh()??{},z=d??C?Number(l??N)*24/Number(c??F):l??N;return A.createElement("svg",{ref:w,...io,width:c??F??io.width,height:c??F??io.height,stroke:o??L,strokeWidth:z,className:Uu("lucide",I,m),...!f&&!gh(P)&&{"aria-hidden":"true"},...P},[...v.map(([B,b])=>A.createElement(B,b)),...Array.isArray(f)?f:[f]])});/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const rt=(o,c)=>{const l=A.forwardRef(({className:d,...m},f)=>A.createElement(xh,{ref:f,iconNode:c,className:Uu(`lucide-${ph(_u(o))}`,`lucide-${o}`,d),...m}));return l.displayName=_u(o),l};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kh=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]],wh=rt("arrow-right",kh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jh=[["path",{d:"M12 5v16",key:"1f6ucr"}],["path",{d:"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z",key:"1fyvmf"}]],Tu=rt("book-open",jh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const bh=[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],oo=rt("chart-column",bh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Sh=[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]],Nh=rt("external-link",Sh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ch=[["rect",{width:"7",height:"7",x:"3",y:"3",rx:"1",key:"1g98yp"}],["rect",{width:"7",height:"7",x:"14",y:"3",rx:"1",key:"6d4xhi"}],["rect",{width:"7",height:"7",x:"14",y:"14",rx:"1",key:"nxv5o0"}],["rect",{width:"7",height:"7",x:"3",y:"14",rx:"1",key:"1bb6yr"}]],ho=rt("layout-grid",Ch);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const _h=[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]],Th=rt("lock-keyhole",_h);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Eh=[["path",{d:"M4 5h16",key:"1tepv9"}],["path",{d:"M4 12h16",key:"1lakjw"}],["path",{d:"M4 19h16",key:"1djgab"}]],Mh=rt("menu",Eh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ph=[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]],Lh=rt("search",Ph);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Rh=[["path",{d:"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915",key:"1i5ecw"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]],qs=rt("settings",Rh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ah=[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}]],lo=rt("shield",Ah);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Dh=[["path",{d:"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",key:"1s2grr"}],["path",{d:"M20 2v4",key:"1rf3ol"}],["path",{d:"M22 4h-4",key:"gwowj6"}],["circle",{cx:"4",cy:"20",r:"2",key:"6kqj1y"}]],Qs=rt("sparkles",Dh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ih=[["path",{d:"M12 19h8",key:"baeox8"}],["path",{d:"m4 17 6-6-6-6",key:"1yngyt"}]],zh=rt("terminal",Ih);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Fh=[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["path",{d:"M16 3.128a4 4 0 0 1 0 7.744",key:"16gr8j"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}]],Eu=rt("users",Fh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Bh=[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]],Oh=rt("x",Bh),Wh={arrow:wh,grid:ho,terminal:zh,chart:oo,shield:lo,spark:Qs,users:Eu,settings:qs,book:Tu,external:Nh,menu:Mh,close:Oh,lock:Th,search:Lh,doc:Tu,utility:qs,icon_home:ho,icon_settings:qs,icon_economy:oo,icon_leveling:oo,icon_moderation:lo,icon_automod:lo,icon_heart:Qs,icon_utility:qs,icon_bot:Eu,icon_ai:Qs,icon_lightbulb:Qs};function q({name:o,size:c,className:l=""}){const d=Wh[o]||ho;return r.jsx(d,{className:`icon ${l}`.trim(),"aria-hidden":"true",focusable:"false",strokeWidth:1.8,style:c?{width:c,height:c}:void 0})}let Mu=null,co=null;function sa(){const[o,c]=A.useState(Mu);return A.useEffect(()=>{co||(co=oh().then(l=>Mu=l)),co.then(c).catch(()=>{})},[]),o}function tt({page:o}){const c=sa();return r.jsxs("header",{className:"site-header",children:[r.jsx(ea,{}),r.jsxs("nav",{className:"site-nav","aria-label":"Main navigation",children:[r.jsx("a",{className:o==="home"?"active":"","aria-current":o==="home"?"page":void 0,href:"/",onClick:l=>{l.preventDefault(),ie("/")},children:"Home"}),r.jsx("a",{className:o==="commands"?"active":"","aria-current":o==="commands"?"page":void 0,href:"/commands",onClick:l=>{l.preventDefault(),ie("/commands")},children:"Commands"}),r.jsx("a",{className:o==="docs"?"active":"","aria-current":o==="docs"?"page":void 0,href:"/docs",onClick:l=>{l.preventDefault(),ie("/docs")},children:"Docs"}),r.jsx("a",{href:"/changelog",onClick:l=>{l.preventDefault(),ie("/changelog")},children:"Changelog"})]}),r.jsxs("div",{className:"header-actions",children:[r.jsxs("a",{className:"button button-small button-muted dashboard-link",href:"/dashboard",onClick:l=>{l.preventDefault(),ie("/dashboard")},children:["Dashboard ",r.jsx(q,{name:"arrow"})]}),r.jsx("a",{className:"button button-small button-primary",href:(c==null?void 0:c.invite_url)||"#",target:"_blank",rel:"noreferrer",children:"Add to Discord"})]})]})}const Pu=typeof navigator<"u"?(navigator.language||"en").slice(0,2):"en";function po(o){const c=o.description;if(typeof c=="string")return c;if(c&&typeof c=="object"){const l=c;if(l[Pu])return l[Pu];if(l.en)return l.en;const d=Object.values(l).find(m=>typeof m=="string"&&m.length>0);if(d)return d}return"A Niko command for your server."}const Uh=[{value:"all",label:"All commands"},{value:"slash",label:"Slash"},{value:"prefix",label:"Prefix"},{value:"hybrid",label:"Hybrid"},{value:"context",label:"Context menus"}],ta={slash:"Slash command",prefix:"Prefix command",hybrid:"Hybrid command",context:"Context menu"};function jn(o){return o.type&&o.type in ta?o.type:"slash"}function $h(o){return o.context_type==="user"?"Right-click a user":"Right-click a message"}function $u(o){const c=jn(o);return c==="slash"?r.jsxs("code",{children:["/",o.name]}):c==="prefix"?r.jsxs("code",{children:[".",o.name]}):c==="hybrid"?r.jsxs(r.Fragment,{children:[r.jsxs("code",{children:["/",o.name]}),r.jsx("span",{className:"command-or",children:"or"}),r.jsxs("code",{children:[".",o.name]})]}):r.jsxs("code",{className:"context-invocation",children:[$h(o)," · ",o.name]})}function Lu(o){return o!=null&&o.length?o:["Not specified"]}function Vh({command:o,onClose:c}){A.useEffect(()=>{const v=P=>{P.key==="Escape"&&c()};return document.addEventListener("keydown",v),()=>document.removeEventListener("keydown",v)},[c]);const l=o.parameters||[],d=o.subcommands||[],m=Lu(o.aliases),f=Lu(o.permissions);return r.jsx("div",{className:"command-dialog-backdrop",role:"presentation",onMouseDown:v=>{v.currentTarget===v.target&&c()},children:r.jsxs("section",{className:"command-dialog",role:"dialog","aria-modal":"true","aria-labelledby":"command-dialog-title",children:[r.jsxs("header",{className:"command-dialog-header",children:[r.jsxs("div",{children:[r.jsxs("div",{className:"command-dialog-kicker",children:[o.category," · ",ta[jn(o)]]}),r.jsx("h2",{id:"command-dialog-title",children:$u(o)})]}),r.jsx("button",{className:"dialog-close",type:"button",onClick:c,"aria-label":"Close command details",title:"Close command details",children:r.jsx(q,{name:"close"})})]}),r.jsxs("div",{className:"command-dialog-body",children:[r.jsx("p",{className:"command-dialog-description",children:po(o)}),r.jsxs("div",{className:"command-detail-grid",children:[r.jsxs("section",{className:"command-detail-section command-detail-wide",children:[r.jsx("h3",{children:"Usage"}),r.jsx("code",{className:"command-usage",children:o.usage||`${jn(o)==="context"?o.name:`/${o.name}`}`})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Permissions"}),r.jsx("ul",{className:"command-detail-list",children:f.map(v=>r.jsx("li",{children:v},v))})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Aliases"}),r.jsx("ul",{className:"command-detail-list",children:m.map(v=>r.jsx("li",{children:r.jsx("code",{children:v==="Not specified"?v:`.${v}`})},v))})]})]}),!!l.length&&r.jsxs("section",{className:"command-detail-section command-parameters",children:[r.jsx("h3",{children:"Parameters"}),r.jsx("div",{className:"command-parameter-list",children:l.map(v=>r.jsxs("div",{className:"command-parameter",children:[r.jsxs("div",{className:"command-parameter-title",children:[r.jsx("code",{children:v.name}),r.jsxs("span",{children:[v.required?"Required":"Optional"," · ",v.type]})]}),r.jsx("p",{children:v.description||"No description provided."})]},v.name))})]}),!!d.length&&r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Subcommands"}),r.jsx("div",{className:"subcommand-list",children:d.map(v=>r.jsxs("code",{children:[o.name," ",v]},v))})]})]}),r.jsxs("footer",{className:"command-dialog-footer",children:[r.jsx("span",{children:"Command registry details are generated from the live bot."}),r.jsx("button",{className:"button button-primary button-small",type:"button",onClick:c,children:"Done"})]})]})})}function Hh(){const[o,c]=A.useState([]),[l,d]=A.useState(null),[m,f]=A.useState(""),[v,P]=A.useState("all"),[w,F]=A.useState("all"),[N,C]=A.useState(!0),[L,I]=A.useState("");A.useEffect(()=>{lh().then(c).catch(()=>I("The command registry is unavailable right now.")).finally(()=>C(!1))},[]),A.useEffect(()=>{if(!l)return;const b=document.body.style.overflow;return document.body.style.overflow="hidden",()=>{document.body.style.overflow=b}},[l]);const z=A.useMemo(()=>["all",...Array.from(new Set(o.map(b=>b.category))).sort()],[o]),B=o.filter(b=>{const U=`${b.name} ${po(b)} ${b.category} ${ta[jn(b)]} ${b.context_type||""} ${(b.aliases||[]).join(" ")}`.toLowerCase();return(w==="all"||jn(b)===w)&&(v==="all"||b.category===v)&&U.includes(m.trim().toLowerCase())});return r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:"commands"}),r.jsxs("main",{className:"shell page-main",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Reference library"}),r.jsxs("h1",{children:["Everything Niko",r.jsx("br",{}),r.jsx("em",{children:"knows how to do."})]}),r.jsx("p",{children:"Browse slash, prefix, hybrid, and context commands from the live bot registry. Select any command for permissions, aliases, parameters, usage, and subcommands."})]}),r.jsxs("div",{className:"command-toolbar",children:[r.jsxs("label",{className:"search-field",children:[r.jsx("span",{"aria-hidden":"true",children:"⌕"}),r.jsx("input",{value:m,onChange:b=>f(b.target.value),placeholder:"Search commands","aria-label":"Search commands"})]}),r.jsxs("div",{className:"command-filters",children:[r.jsx("div",{className:"filter-list","aria-label":"Command types",children:Uh.map(b=>r.jsx("button",{type:"button",className:w===b.value?"filter active":"filter","aria-pressed":w===b.value,onClick:()=>F(b.value),children:b.label},b.value))}),r.jsx("div",{className:"filter-list","aria-label":"Command categories",children:z.map(b=>r.jsx("button",{type:"button",className:v===b?"filter active":"filter","aria-pressed":v===b,onClick:()=>P(b),children:b==="all"?"All categories":b},b))})]})]}),r.jsxs("div",{className:"command-meta",children:[r.jsx("strong",{children:N?"…":B.length})," commands ",r.jsx("span",{children:"·"})," live bot registry ",r.jsx("span",{children:"·"})," select a card for details"]}),L&&r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Could not load commands"}),r.jsx("span",{children:L})]}),r.jsxs("div",{className:"commands-grid",children:[B.map(b=>r.jsxs("button",{className:"command-card",type:"button",onClick:()=>d(b),"aria-label":`View details for ${b.name}`,children:[r.jsxs("span",{className:"command-card-head",children:[r.jsx("span",{className:"command-name",children:$u(b)}),r.jsx("span",{className:"command-type",children:ta[jn(b)]})]}),r.jsx("span",{className:"command-card-description",children:po(b)}),r.jsxs("span",{className:"command-card-footer",children:[r.jsx("span",{className:"category-tag",children:b.category}),r.jsxs("span",{className:"command-expand",children:[r.jsx("span",{children:"Details"}),r.jsx(q,{name:"arrow",size:14})]})]})]},`${jn(b)}-${b.context_type||""}-${b.category}-${b.name}`)),!N&&!L&&!B.length&&r.jsx("div",{className:"empty-state",children:"No commands match that search."})]})]}),r.jsx(Bt,{}),l&&r.jsx(Vh,{command:l,onClose:()=>d(null)})]})}function Ee(o){return o==null?"—":new Intl.NumberFormat("en-US",{notation:o>9999?"compact":"standard"}).format(o)}function fo(o){return(o==null?void 0:o.global_name)||(o==null?void 0:o.username)||"there"}function Vu(o){return o.split(/\s+/).map(c=>c[0]).join("").slice(0,2).toUpperCase()}function vo({guild:o,className:c="guild-avatar"}){return r.jsx("span",{className:c,"aria-hidden":"true",children:o.icon_url?r.jsx("img",{src:o.icon_url,alt:""}):o.name.slice(0,1).toUpperCase()})}function Hu({user:o,className:c="avatar"}){const l=o.avatar?`https://cdn.discordapp.com/avatars/${o.id}/${o.avatar}.${o.avatar.startsWith("a_")?"gif":"png"}?size=64`:null;return r.jsx("span",{className:c,"aria-hidden":"true",children:l?r.jsx("img",{src:l,alt:""}):Vu(o.global_name||o.username||"Niko")})}function Gh({name:o,avatarUrl:c,className:l="member-avatar"}){return r.jsx("span",{className:l,"aria-hidden":"true",children:c?r.jsx("img",{src:c,alt:""}):Vu(o)})}const Ru=[["overview","Overview","grid","At a glance"],["leveling","Leveling","spark","Reward participation"],["moderation","Moderation","shield","Keep things steady"],["server","Server","settings","Manage server features"],["ai","AI controls","settings","Shape Niko’s voice"],["customization","Customization","paint","Niko’s server identity"]];function Kh({user:o,guilds:c,selectedGuild:l,view:d,section:m,stats:f,onHome:v,onServers:P,onGuildChange:w,onSectionChange:F,children:N}){var b;const C=c.filter(U=>U.installed!==!1),L=(U=!1)=>r.jsx("nav",{className:U?"dash-nav dash-nav-mobile":"dash-nav","aria-label":"Server settings",children:Ru.map(([S,Q,te])=>r.jsxs("button",{className:d==="guild"&&m===S?"active":"","aria-current":d==="guild"&&m===S?"page":void 0,onClick:()=>F(S),children:[r.jsx(q,{name:te}),r.jsx("span",{children:Q})]},S))}),I=(U=!1)=>r.jsxs("nav",{className:U?"dash-nav dash-primary-nav dash-nav-mobile":"dash-nav dash-primary-nav","aria-label":"Dashboard",children:[r.jsxs("button",{className:d==="overview"?"active":"","aria-current":d==="overview"?"page":void 0,onClick:v,children:[r.jsx(q,{name:"grid"}),r.jsx("span",{children:"My overview"})]}),r.jsxs("button",{className:d==="servers"?"active":"","aria-current":d==="servers"?"page":void 0,onClick:P,children:[r.jsx(q,{name:"users"}),r.jsx("span",{children:"My servers"})]})]}),z=d==="overview"?`Welcome, ${fo(o)}`:d==="servers"?"Your servers":(l==null?void 0:l.name)||"Server settings",B=d==="guild"?"Managing server":"Niko dashboard";return r.jsxs("div",{className:"dashboard-layout",children:[r.jsxs("aside",{className:"dash-sidebar",children:[r.jsx(ea,{onNavigate:v}),r.jsxs("div",{className:"side-rail-heading",children:[r.jsx("span",{className:"side-label",children:"Workspace"}),r.jsxs("span",{className:"rail-status",children:[r.jsx("span",{className:"status-dot"})," Live"]})]}),I(),d==="guild"&&l&&r.jsxs(r.Fragment,{children:[r.jsx("div",{className:"side-label side-label-settings",children:"Current server"}),r.jsxs("div",{className:"side-guild",children:[r.jsx(vo,{guild:l}),r.jsxs("span",{children:[r.jsx("strong",{children:l.name}),r.jsx("small",{children:"Live configuration"})]}),r.jsx("span",{className:"guild-presence",title:"Niko is connected",children:r.jsx("span",{className:"status-dot"})})]}),r.jsxs("div",{className:"side-settings-caption",children:[r.jsx("span",{children:"Settings map"}),r.jsx("small",{children:"Pick a room to tune"})]}),L()]}),d!=="guild"&&r.jsxs("div",{className:"side-rail-note",children:[r.jsx("span",{className:"panel-kicker",children:"Niko workspace"}),r.jsxs("strong",{children:["Make the useful",r.jsx("br",{}),"things easier to find."]}),r.jsx("small",{children:"Your servers and their live signals, in one quiet place."})]}),r.jsxs("div",{className:"sidebar-bottom",children:[r.jsxs("span",{className:"online-label",children:[r.jsx("span",{className:"status-dot"})," Niko is online"]}),r.jsxs("small",{children:[Ee(f==null?void 0:f.guild_count)," connected servers · v",(f==null?void 0:f.version)||"1.0"]}),r.jsxs("a",{href:"/",onClick:U=>{U.preventDefault(),ie("/")},children:["Back to public site ",r.jsx(q,{name:"arrow"})]})]})]}),r.jsxs("div",{className:"dash-content",children:[r.jsxs("header",{className:"dash-topbar",children:[r.jsxs("div",{className:"mobile-top-row",children:[r.jsx("span",{className:"mobile-brand",children:r.jsx(ea,{})}),r.jsxs("span",{className:"mobile-status",children:[r.jsx("span",{className:"status-dot"})," Online"]})]}),r.jsxs("div",{className:"dash-title",children:[r.jsxs("span",{className:"dash-overline",children:[B," ",r.jsx("span",{className:"dash-title-divider",children:"/"})," ",d==="guild"?(b=Ru.find(([U])=>U===m))==null?void 0:b[1]:"Workspace"]}),r.jsx("h1",{children:z})]}),r.jsxs("div",{className:"dash-top-actions",children:[d==="guild"?r.jsxs("label",{className:"guild-switcher",children:[r.jsx("span",{className:"sr-only",children:"Switch server"}),r.jsxs("select",{value:(l==null?void 0:l.id)||"",onChange:U=>{const S=C.find(Q=>Q.id===U.target.value);S&&w(S)},children:[r.jsx("option",{value:"",disabled:!0,children:"Switch server"}),C.map(U=>r.jsx("option",{value:U.id,children:U.name},U.id))]})]}):r.jsxs("button",{className:"button button-muted button-small top-action",onClick:P,children:[r.jsx(q,{name:"users"})," Browse servers"]}),d==="guild"&&r.jsxs("span",{className:"connection-chip",children:[r.jsx("span",{className:"status-dot"})," Connected"]}),r.jsxs("div",{className:"user-pill",children:[r.jsx(Hu,{user:o}),r.jsx("span",{children:fo(o)})]}),r.jsx("a",{className:"logout-link",href:"/auth/logout",children:"Log out"})]})]}),r.jsx("div",{className:"mobile-primary-bar",children:I(!0)}),d==="guild"&&r.jsx("div",{className:"mobile-section-bar",children:L(!0)}),r.jsx("main",{className:"dash-main",children:N})]})]})}function on({eyebrow:o,title:c,text:l}){return r.jsxs("div",{className:"dash-heading",children:[r.jsxs("div",{className:"heading-meta",children:[r.jsx("div",{className:"eyebrow",children:o}),r.jsx("span",{className:"heading-context",children:"NIKO / CONTROL ROOM"})]}),r.jsx("h2",{children:c}),r.jsx("p",{children:l})]})}function Mt({label:o,value:c,note:l,accent:d=""}){return r.jsxs("div",{className:`dash-stat ${d}`,children:[r.jsx("span",{children:o}),r.jsx("strong",{children:c}),r.jsx("small",{children:l})]})}function qh({user:o,overview:c,guilds:l,onServers:d,onManage:m}){const f=l.filter(v=>v.installed!==!1);return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Personal overview",title:"Your Niko snapshot.",text:"Keep an eye on your progress, then jump into a server when you’re ready to tune the room."}),r.jsxs("div",{className:"overview-intro",children:[r.jsxs("div",{className:"profile-card",children:[r.jsx(Hu,{user:o,className:"profile-avatar"}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Signed in as"}),r.jsx("h3",{children:fo(o)}),r.jsx("p",{children:"Personal economy profile"})]})]}),r.jsxs("button",{className:"button button-primary",onClick:d,children:["Manage a server ",r.jsx(q,{name:"arrow"})]})]}),r.jsxs("div",{className:"dash-stats overview-stats",children:[r.jsx(Mt,{label:"Net worth",value:Ee(c==null?void 0:c.net_worth),note:"Across your Niko profile",accent:"accent-orange"}),r.jsx(Mt,{label:"In your wallet",value:Ee(c==null?void 0:c.balance),note:"Ready to spend",accent:"accent-violet"}),r.jsx(Mt,{label:"In your vault",value:Ee(c==null?void 0:c.bank),note:"Saved for later",accent:"accent-blue"}),r.jsx(Mt,{label:"Current level",value:Ee(c==null?void 0:c.level),note:c!=null&&c.job?`Working as a ${c.job}`:"Keep showing up",accent:"accent-green"})]}),r.jsxs("div",{className:"dash-columns overview-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Progress"}),r.jsx("h3",{children:"Your momentum"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:"spark"})})]}),r.jsxs("div",{className:"metric-list",children:[r.jsxs("div",{children:[r.jsx("span",{children:"Daily streak"}),r.jsxs("strong",{children:[Ee(c==null?void 0:c.daily_streak)," ",r.jsx("small",{children:"days"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Achievements"}),r.jsxs("strong",{children:[Ee(c==null?void 0:c.achievements)," ",r.jsx("small",{children:"unlocked"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Total earned"}),r.jsxs("strong",{children:[Ee(c==null?void 0:c.total_earned)," ",r.jsx("small",{children:"coins"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Economy standing"}),r.jsxs("strong",{children:[c!=null&&c.economy_rank?`#${Ee(c.economy_rank)}`:"—"," ",r.jsx("small",{children:c!=null&&c.economy_profiles?`of ${Ee(c.economy_profiles)}`:""})]})]})]})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Quick access"}),r.jsx("h3",{children:"Your servers"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:"users"})})]}),r.jsxs("div",{className:"mini-server-list",children:[f.slice(0,4).map(v=>r.jsxs("button",{onClick:()=>m(v),children:[r.jsx(vo,{guild:v}),r.jsx("span",{children:v.name}),r.jsx(q,{name:"arrow"})]},v.id)),!f.length&&r.jsx("p",{className:"empty-state compact",children:"Add Niko to a server to start managing it."})]}),r.jsxs("button",{className:"text-link overview-link",onClick:d,children:["View all servers ",r.jsx(q,{name:"arrow"})]})]})]})]})}function Au({guild:o,onManage:c}){const l=o.installed!==!1;return r.jsxs("article",{className:"server-card",children:[r.jsxs("div",{className:"server-card-heading",children:[r.jsx(vo,{guild:o,className:"server-avatar"}),r.jsx("span",{className:"server-status",children:l?"Niko is installed":"Ready to add"})]}),r.jsx("h3",{children:o.name}),r.jsx("p",{children:l?"Open the dashboard to manage Niko’s features and settings.":"You have permission to manage this server. Add Niko to unlock its controls."}),l?r.jsxs("button",{className:"button button-muted button-small",onClick:()=>c(o),children:["Open settings ",r.jsx(q,{name:"arrow"})]}):r.jsxs("a",{className:"button button-primary button-small",href:o.invite_url||"#",target:"_blank",rel:"noreferrer",children:["Add Niko ",r.jsx(q,{name:"external"})]})]})}function Qh({guilds:o,onManage:c}){const l=o.filter(m=>m.installed!==!1),d=o.filter(m=>m.installed===!1);return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Servers",title:"Choose where to work.",text:"Manage servers with Niko already installed, or add Niko to another server you can administer."}),r.jsxs("div",{className:"server-summary",children:[r.jsxs("div",{children:[r.jsx("strong",{children:Ee(l.length)}),r.jsx("span",{children:"Connected to Niko"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:Ee(d.length)}),r.jsx("span",{children:"Ready to add"})]}),r.jsxs("div",{className:"server-summary-note",children:[r.jsx(q,{name:"shield"}),r.jsx("span",{children:"Only servers where you have Manage Server access are shown."})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Connected"}),r.jsx("h3",{children:"Manage a server"})]}),r.jsx("span",{className:"section-count",children:l.length})]}),r.jsxs("div",{className:"server-grid",children:[l.map(m=>r.jsx(Au,{guild:m,onManage:c},m.id)),!l.length&&r.jsxs("div",{className:"empty-state",children:[r.jsx("strong",{children:"No connected servers yet."}),r.jsx("span",{children:"Add Niko below, then come back here to manage it."})]})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Available to you"}),r.jsx("h3",{children:"Add Niko to a server"})]}),r.jsx("span",{className:"section-count",children:d.length})]}),r.jsxs("div",{className:"server-grid",children:[d.map(m=>r.jsx(Au,{guild:m,onManage:c},m.id)),!d.length&&r.jsx("div",{className:"server-note",children:"Niko is already installed in every server you can manage."})]})]})]})}function Gu({rows:o}){return r.jsxs("div",{className:"rank-list",children:[o.slice(0,5).map((c,l)=>r.jsxs("div",{className:"rank-row",children:[r.jsx("span",{className:`rank rank-${l+1}`,children:String(l+1).padStart(2,"0")}),r.jsxs("span",{className:"rank-user",children:[r.jsx(Gh,{name:c.display_name||c.username||"Unknown member",avatarUrl:c.avatar_url}),r.jsxs("span",{children:[r.jsx("strong",{children:c.display_name||c.username||"Unknown member"}),c.username&&c.display_name&&r.jsxs("small",{children:["@",c.username]})]})]}),r.jsxs("strong",{children:[Ee(c.xp),r.jsx("small",{children:" xp"})]})]},`${c.user_id}-${l}`)),!o.length&&r.jsx("div",{className:"empty-state compact",children:"No data recorded yet."})]})}function Xh({overview:o}){return r.jsxs(r.Fragment,{children:[r.jsxs("div",{className:"guild-welcome",children:[r.jsxs("div",{children:[r.jsx("span",{className:"welcome-mark",children:r.jsx(q,{name:"grid"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server pulse"}),r.jsx("strong",{children:"Here’s what needs your attention."})]})]}),r.jsxs("span",{className:"welcome-time",children:["LIVE SIGNALS ",r.jsx("span",{className:"status-dot"})]})]}),r.jsx(on,{eyebrow:"Overview",title:"A quick read on your room.",text:"The important signals, without making you hunt for them."}),r.jsxs("div",{className:"dash-stats guild-overview-stats",children:[r.jsx(Mt,{label:"Warnings logged",value:Ee(o.moderation.warn_count),note:"For this server",accent:"accent-blue"}),r.jsx(Mt,{label:"Automod",value:o.moderation.automod_active?"Active":"Quiet",note:"Protection status",accent:"accent-green"}),r.jsx(Mt,{label:"Level leaders",value:Ee(o.leveling.top.length),note:"Members with recorded XP",accent:"accent-violet"})]}),r.jsxs("div",{className:"dash-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Community energy"}),r.jsx("h3",{children:"Top XP"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:"spark"})})]}),r.jsx(Gu,{rows:o.leveling.top})]}),r.jsx("section",{className:"dash-panel",children:r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server controls"}),r.jsx("h3",{children:"Manage the room"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:"settings"})}),r.jsx("p",{children:"Use Server settings for prefixes, welcome messages, logs, and ticket panels."})]})})]})]})}function Yh({rows:o,config:c,resources:l,csrfToken:d,guildId:m}){var f,v,P;return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Leveling",title:"Momentum people can see.",text:"Track the members turning up, and tune the pace to fit your server."}),r.jsxs("div",{className:"dash-stats",children:[r.jsx(Mt,{label:"Top level",value:String(((f=o[0])==null?void 0:f.level)||0),note:((v=o[0])==null?void 0:v.display_name)||((P=o[0])==null?void 0:P.username)||"No members yet",accent:"accent-violet"}),r.jsx(Mt,{label:"XP multiplier",value:`${(c==null?void 0:c.leveling.xp_multiplier)||1}×`,note:(c==null?void 0:c.leveling.xp_enabled)===!1?"XP disabled":"Currently active",accent:"accent-blue"}),r.jsx(Mt,{label:"Cooldown",value:`${(c==null?void 0:c.leveling.xp_cooldown)||0}s`,note:"Between XP awards",accent:"accent-green"})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Leaderboard"}),r.jsx("h3",{children:"XP leaders"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:"spark"})})]}),r.jsx(Gu,{rows:o})]}),r.jsx(tp,{guildId:m,config:c,resources:l,csrfToken:d})]})}const aa={saving:!1,message:"",error:""};function et({label:o,hint:c,children:l}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:o}),l,c&&r.jsx("small",{children:c})]})}function Jh(o,c){const l=c?String(c):"",d=(o==null?void 0:o.channels)||[];return!l||d.some(m=>m.id===l)?d:[{id:l,name:`Saved channel · ${l}`},...d]}function ia({icon:o,label:c,title:l,text:d}){return r.jsxs("div",{className:"settings-intro",children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(q,{name:o})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:c}),r.jsx("strong",{children:l}),r.jsx("p",{children:d})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]})}function Sn({label:o,title:c,detail:l,icon:d}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:o}),r.jsx("h3",{children:c}),l&&r.jsx("p",{children:l})]}),d&&r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:d})})]})}function oa({state:o}){return r.jsxs("div",{className:"setting-footer",children:[o.error?r.jsx("span",{className:"form-error",role:"alert",children:o.error}):r.jsx("span",{role:"status",children:o.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:o.saving,children:o.saving?"Saving…":"Save changes"})]})}function Zh({guildId:o,config:c,csrfToken:l}){var C,L,I;const[d,m]=A.useState({}),[f,v]=A.useState(aa);A.useEffect(()=>{const z=(c==null?void 0:c.moderation)||{};m({automod:{...z.automod||{}},spam_threshold:z.spam_threshold??6,spam_interval:z.spam_interval??7,max_mentions:z.max_mentions??5,antinuke:{...z.antinuke||{}},antiraid:{...z.antiraid||{}},antiraid_ext:{...z.antiraid_ext||{}}})},[c]);const P=(z,B,b)=>m(U=>({...U,[z]:{...U[z],[B]:b}})),w=z=>{z.preventDefault(),v({saving:!0,message:"",error:""}),ra(o,"automod",d,l).then(B=>{const b=B.config||{};m({automod:{...b.automod||{}},spam_threshold:b.spam_threshold??6,spam_interval:b.spam_interval??7,max_mentions:b.max_mentions??5,antinuke:{...b.antinuke||{}},antiraid:{...b.antiraid||{}},antiraid_ext:{...b.antiraid_ext||{}}}),v({saving:!1,message:"Moderation settings saved to Niko.",error:""})}).catch(B=>v({saving:!1,message:"",error:B instanceof Error?B.message:"Could not save settings."}))},F=[["antispam","Anti-spam","Detect repeated messages"],["antilink","Invite links","Remove Discord invite links"],["badwords","Blocked words","Filter words from the server list"],["massmention","Mass mentions","Limit mention floods"],["antinuke","Anti-nuke","Protect channels and roles"],["antiraid","Join raid protection","React to sudden join waves"],["antiraid_ext","External app protection","Detect user-installed app abuse"]],N=F.filter(([z])=>{var B;return!!((B=d.automod)!=null&&B[z])}).length;return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Moderation",title:"Keep the room feeling good.",text:"Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration."}),r.jsx(ia,{icon:"shield",label:"Protection desk",title:`${N} of ${F.length} safeguards active`,text:"Start with the essentials, then tune thresholds below when you know the room’s rhythm."}),r.jsxs("form",{onSubmit:w,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Protection rules",title:"AutoMod modules",detail:"Toggle only the responses you want Niko to handle.",icon:"shield"}),r.jsx("div",{className:"setting-list",children:F.map(([z,B,b])=>{var U;return r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:B}),r.jsx("small",{children:b})]}),r.jsx("input",{type:"checkbox",checked:!!((U=d.automod)!=null&&U[z]),onChange:S=>P("automod",z,S.target.checked)}),r.jsx("i",{"aria-hidden":"true"})]},z)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Thresholds",title:"Choose when protection steps in",detail:"These limits apply across the server."}),r.jsxs("div",{className:"form-grid",children:[r.jsx(et,{label:"Spam messages",hint:"Messages inside the spam interval",children:r.jsx("input",{type:"number",min:"1",max:"100",value:d.spam_threshold??6,onChange:z=>m({...d,spam_threshold:z.target.value})})}),r.jsx(et,{label:"Spam interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:d.spam_interval??7,onChange:z=>m({...d,spam_interval:z.target.value})})}),r.jsx(et,{label:"Maximum mentions",children:r.jsx("input",{type:"number",min:"1",max:"100",value:d.max_mentions??5,onChange:z=>m({...d,max_mentions:z.target.value})})}),r.jsx(et,{label:"Anti-raid joins",hint:"Joins inside the join interval",children:r.jsx("input",{type:"number",min:"1",max:"1000",value:((C=d.antiraid)==null?void 0:C.join_threshold)??10,onChange:z=>P("antiraid","join_threshold",z.target.value)})}),r.jsx(et,{label:"Anti-raid interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:((L=d.antiraid)==null?void 0:L.join_interval)??10,onChange:z=>P("antiraid","join_interval",z.target.value)})}),r.jsx(et,{label:"Anti-raid action",children:r.jsxs("select",{value:((I=d.antiraid)==null?void 0:I.action)??"kick",onChange:z=>P("antiraid","action",z.target.value),children:[r.jsx("option",{value:"kick",children:"Kick"}),r.jsx("option",{value:"ban",children:"Ban"}),r.jsx("option",{value:"softban",children:"Soft-ban"}),r.jsx("option",{value:"slowmode",children:"Slowmode"}),r.jsx("option",{value:"lockdown",children:"Lockdown"})]})})]}),r.jsx(oa,{state:f})]})]})]})}function ep({guildId:o,config:c,csrfToken:l}){const[d,m]=A.useState({personality:"cafe",enabled:!0,ai_actions_experiment:!1,better_context_experiment:!1}),[f,v]=A.useState(aa);A.useEffect(()=>{const w=(c==null?void 0:c.ai)||{};m({personality:w.personality||"cafe",enabled:w.enabled!=="False"&&w.enabled!==!1,ai_actions_experiment:w.ai_actions_experiment===!0||w.ai_actions_experiment==="True",better_context_experiment:w.better_context_experiment===!0||w.better_context_experiment==="True"})},[c]);const P=w=>{w.preventDefault(),v({saving:!0,message:"",error:""}),ra(o,"ai",d,l).then(F=>{const N=F.config||{};m({personality:N.personality==="normal"?"normal":"cafe",enabled:N.enabled!=="False"&&N.enabled!==!1,ai_actions_experiment:N.ai_actions_experiment===!0||N.ai_actions_experiment==="True",better_context_experiment:N.better_context_experiment===!0||N.better_context_experiment==="True"}),v({saving:!1,message:"AI settings saved to Niko.",error:""})}).catch(F=>v({saving:!1,message:"",error:F instanceof Error?F.message:"Could not save settings."}))};return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"AI controls",title:"Give Niko the right tone.",text:"AI is optional, configurable per server, and designed to stay out of the way when the room does not need it."}),r.jsx(ia,{icon:"settings",label:"Conversation desk",title:d.enabled?"Niko is ready to respond":"Niko is staying quiet",text:"Choose a voice that fits your community. You can change this without affecting other servers."}),r.jsxs("form",{onSubmit:P,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Conversation",title:"Core settings",detail:"Decide when Niko joins the conversation.",icon:"settings"}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable AI chat"}),r.jsx("small",{children:"Respond when Niko is mentioned"})]}),r.jsx("input",{type:"checkbox",checked:d.enabled,onChange:w=>m({...d,enabled:w.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"personality-options",children:[r.jsxs("button",{type:"button",className:d.personality==="cafe"?"personality active":"personality",onClick:()=>m({...d,personality:"cafe"}),children:[r.jsx("span",{className:"personality-mark",children:"n"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Café"}),r.jsx("small",{children:"Warm, playful, familiar"})]})]}),r.jsxs("button",{type:"button",className:d.personality==="normal"?"personality active":"personality",onClick:()=>m({...d,personality:"normal"}),children:[r.jsx("span",{className:"personality-mark",children:"—"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Normal"}),r.jsx("small",{children:"Clear and straightforward"})]})]})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Experiments",title:"Optional context",detail:"Try new capabilities when your team is ready."}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Better context"}),r.jsx("small",{children:"Use the last five channel messages"})]}),r.jsx("input",{type:"checkbox",checked:d.better_context_experiment,onChange:w=>m({...d,better_context_experiment:w.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"AI actions"}),r.jsx("small",{children:"Allow confirmed actions requested in chat"})]}),r.jsx("input",{type:"checkbox",checked:d.ai_actions_experiment,onChange:w=>m({...d,ai_actions_experiment:w.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsx(oa,{state:f})]})]})]})}function tp({guildId:o,config:c,resources:l,csrfToken:d}){const m=(c==null?void 0:c.leveling)||{},[f,v]=A.useState({xp_enabled:!0,xp_multiplier:1,xp_cooldown:0,level_up_channel:"",level_up_message:""}),[P,w]=A.useState(aa);A.useEffect(()=>v({xp_enabled:m.xp_enabled!==!1,xp_multiplier:m.xp_multiplier??1,xp_cooldown:m.xp_cooldown??0,level_up_channel:m.level_up_channel?String(m.level_up_channel):"",level_up_message:m.level_up_message||""}),[c]);const F=C=>{C.preventDefault(),w({saving:!0,message:"",error:""}),ra(o,"leveling",f,d).then(L=>{const I=L.config||{};v({xp_enabled:I.xp_enabled!==!1,xp_multiplier:I.xp_multiplier??1,xp_cooldown:I.xp_cooldown??0,level_up_channel:I.level_up_channel?String(I.level_up_channel):"",level_up_message:I.level_up_message||""}),w({saving:!1,message:"Leveling settings saved to Niko.",error:""})}).catch(L=>w({saving:!1,message:"",error:L instanceof Error?L.message:"Could not save settings."}))},N=Jh(l,f.level_up_channel);return r.jsxs(r.Fragment,{children:[r.jsx(ia,{icon:"spark",label:"Participation desk",title:f.xp_enabled?"XP is flowing":"XP is paused",text:"Set a pace that rewards regulars without turning every message into a transaction."}),r.jsx("form",{onSubmit:F,className:"settings-stack",children:r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Leveling settings",title:"Shape the pace",detail:"These controls apply to every member in this server.",icon:"spark"}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable XP"}),r.jsx("small",{children:"Track activity and award levels"})]}),r.jsx("input",{type:"checkbox",checked:f.xp_enabled,onChange:C=>v({...f,xp_enabled:C.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"form-grid",children:[r.jsx(et,{label:"XP multiplier",hint:"From 0.1× to 10×",children:r.jsx("input",{type:"number",min:"0.1",max:"10",step:"0.1",value:f.xp_multiplier,onChange:C=>v({...f,xp_multiplier:C.target.value})})}),r.jsx(et,{label:"Cooldown (seconds)",hint:"0 disables the cooldown",children:r.jsx("input",{type:"number",min:"0",max:"86400",value:f.xp_cooldown,onChange:C=>v({...f,xp_cooldown:C.target.value})})}),r.jsx(et,{label:"Level-up channel",children:r.jsxs("select",{value:f.level_up_channel,onChange:C=>v({...f,level_up_channel:C.target.value}),children:[r.jsx("option",{value:"",children:"Same channel"}),N.map(C=>r.jsxs("option",{value:C.id,children:["#",C.name]},C.id))]})}),r.jsx(et,{label:"Level-up message",hint:"Use {mention}, {level}, {name}, or {guild}",children:r.jsx("textarea",{rows:3,maxLength:1e3,value:f.level_up_message,onChange:C=>v({...f,level_up_message:C.target.value}),placeholder:"Leave blank for Niko's default message"})})]}),r.jsx(oa,{state:P})]})})]})}function np({guildId:o,config:c,csrfToken:l}){var F;const d=((F=c==null?void 0:c.server)==null?void 0:F.profile)||{},[m,f]=A.useState({display_name:d.display_name||"",bio:d.bio||"",avatar_url:d.avatar_url||"",banner_url:d.banner_url||""}),[v,P]=A.useState(aa);A.useEffect(()=>{var C;const N=((C=c==null?void 0:c.server)==null?void 0:C.profile)||{};f({display_name:N.display_name||"",bio:N.bio||"",avatar_url:N.avatar_url||"",banner_url:N.banner_url||""})},[c]);const w=N=>{N.preventDefault(),P({saving:!0,message:"",error:""}),hh(o,{display_name:m.display_name||null,bio:m.bio||null,avatar_url:m.avatar_url||null,banner_url:m.banner_url||null},l).then(C=>{const L=C.profile||{};f({display_name:L.display_name||"",bio:L.bio||"",avatar_url:L.avatar_url||"",banner_url:L.banner_url||""}),P({saving:!1,message:"Bot profile updated.",error:""})}).catch(C=>P({saving:!1,message:"",error:C instanceof Error?C.message:"Could not save profile."}))};return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Customization",title:"Niko's server presence.",text:"Change how Niko appears in this server. Display name, avatar, banner, and bio are all per-server."}),r.jsx(ia,{icon:"paint",label:"Identity desk",title:"Server-specific identity",text:"Each server can have its own Niko persona. Changes apply only to this server."}),r.jsxs("form",{onSubmit:w,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Display name",title:"How Niko appears",detail:"Set the name members see for Niko in this server. Leave blank to use the default.",icon:"settings"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(et,{label:"Display name",hint:"32 characters or fewer",children:r.jsx("input",{value:m.display_name,maxLength:32,onChange:N=>f({...m,display_name:N.target.value}),placeholder:"Niko"})}),r.jsx(et,{label:"Bio",hint:"190 characters or fewer",children:r.jsx("input",{value:m.bio,maxLength:190,onChange:N=>f({...m,bio:N.target.value}),placeholder:"A warm Discord companion"})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Server avatar & banner",title:"Visual identity",detail:"Provide HTTPS image URLs. Images are uploaded to Discord when saved.",icon:"paint"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(et,{label:"Avatar URL",hint:"Square image, 512×512 recommended",children:r.jsx("input",{type:"url",value:m.avatar_url,onChange:N=>f({...m,avatar_url:N.target.value}),placeholder:"https://cdn.example.com/avatar.png"})}),r.jsx(et,{label:"Banner URL",hint:"Wide image, 960×540 recommended",children:r.jsx("input",{type:"url",value:m.banner_url,onChange:N=>f({...m,banner_url:N.target.value}),placeholder:"https://cdn.example.com/banner.png"})})]}),r.jsx("p",{className:"form-hint",children:"Images are fetched, validated, and uploaded to Discord. Maximum 8 MB each. Supported formats: PNG, JPG, GIF."})]}),r.jsx(oa,{state:v})]})]})}const rp={saving:!1,message:"",error:""};function Ze({label:o,hint:c,children:l}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:o}),l,c&&r.jsx("small",{children:c})]})}function Xs({label:o,title:c,detail:l,icon:d}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:o}),r.jsx("h3",{children:c}),r.jsx("p",{children:l})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:d})})]})}function sp({state:o}){return r.jsxs("div",{className:"setting-footer",children:[o.error?r.jsx("span",{className:"form-error",role:"alert",children:o.error}):r.jsx("span",{role:"status",children:o.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:o.saving,children:o.saving?"Saving...":"Save server settings"})]})}const ap=[["moderation","Moderation"],["automod","AutoMod"],["messages","Messages"],["channels","Channels"],["members","Members"],["captcha","Captcha"],["invites","Invites"],["roles","Roles"],["server","Server"],["voice","Voice"]];function ip(o,c){var l;return c?((l=o==null?void 0:o.channels.find(d=>d.id===String(c)))==null?void 0:l.name)||`Saved channel · ${c}`:"Not set"}function Ys(o,c){const l=c?String(c):"",d=(o==null?void 0:o.channels)||[];return!l||d.some(m=>m.id===l)?d:[{id:l,name:`Saved channel · ${l}`},...d]}function Du(o,c=[]){const l=(o==null?void 0:o.roles)||[],d=new Set(l.map(f=>f.id));return[...c.map(String).filter((f,v,P)=>f&&!d.has(f)&&P.indexOf(f)===v).map(f=>({id:f,name:`Unavailable role (${f})`})),...l]}function Iu(o){var d,m;const c=(o==null?void 0:o.onboarding)||{},l=(o==null?void 0:o.tickets)||{};return{prefixes:((d=o==null?void 0:o.prefixes)!=null&&d.length?o.prefixes:["."]).join(`
`),welcome_channel:c.welcome_channel?String(c.welcome_channel):"",welcome_title:c.welcome_title||"",welcome_description:c.welcome_description||"",welcome_color:c.welcome_color===null||c.welcome_color===void 0?"5865F2":c.welcome_color.toString(16).padStart(6,"0"),welcome_image:c.welcome_image||"",rules_channel:c.rules_channel?String(c.rules_channel):"",rules_text:c.rules_text||"",rules_role_id:c.rules_role_id?String(c.rules_role_id):"",logging:Object.fromEntries(Object.entries((o==null?void 0:o.logging)||{}).map(([f,v])=>[f,v==null?"":String(v)])),disabled_logging:[...((m=o==null?void 0:o.logging)==null?void 0:m.disabled)||[]].map(String),panel_title:l.panel_title||"",panel_description:l.panel_description||"",panel_categories:(l.panel_categories||[]).join(`
`),panel_channel_id:l.panel_channel_id?String(l.panel_channel_id):"",support_roles:[...l.support_roles||[]].map(String)}}function op({guildId:o,config:c,resources:l,csrfToken:d}){const[m,f]=A.useState(()=>Iu(c==null?void 0:c.server)),[v,P]=A.useState(rp),w=(S,Q)=>f(te=>({...te,[S]:Q})),F=(S,Q)=>f(te=>({...te,logging:{...te.logging,[S]:Q}})),N=S=>f(Q=>({...Q,disabled_logging:Q.disabled_logging.includes(S)?Q.disabled_logging.filter(te=>te!==S):[...Q.disabled_logging,S]})),C=S=>{S.preventDefault(),P({saving:!0,message:"",error:""});const Q=m.prefixes.split(/\r?\n|,/).map(se=>se.trim()).filter(Boolean),te=m.panel_categories.split(/\r?\n|,/).map(se=>se.trim()).filter(Boolean);ra(o,"server",{prefixes:Q,onboarding:{welcome_channel:m.welcome_channel,welcome_title:m.welcome_title,welcome_description:m.welcome_description,welcome_color:m.welcome_color,welcome_image:m.welcome_image,rules_channel:m.rules_channel,rules_text:m.rules_text,rules_role_id:m.rules_role_id},logging:{...m.logging,disabled:m.disabled_logging},tickets:{panel_title:m.panel_title,panel_description:m.panel_description,panel_categories:te,panel_channel_id:m.panel_channel_id,support_roles:m.support_roles}},d).then(se=>{f(Iu(se.config)),P({saving:!1,message:"Server settings saved to Niko.",error:""})}).catch(se=>P({saving:!1,message:"",error:se instanceof Error?se.message:"Could not save server settings."}))},L=m.welcome_channel,I=m.panel_channel_id,z=Ys(l,m.welcome_channel),B=Ys(l,m.rules_channel),b=Ys(l,m.panel_channel_id),U=Du(l,m.support_roles);return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Server settings",title:"Make Niko fit your room.",text:"Manage the settings that shape how Niko behaves in this server. Economy balances remain global to each user and are not configured here."}),r.jsxs("div",{className:"settings-intro",children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(q,{name:"settings"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server control room"}),r.jsxs("strong",{children:[m.prefixes.split(/\r?\n|,/).filter(Boolean).length||0," command prefixes configured"]}),r.jsx("p",{children:"Welcome flows, log destinations, and ticket panels all live here."})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]}),r.jsxs("form",{onSubmit:C,className:"settings-stack server-settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Xs,{label:"Commands",title:"Prefixes",detail:"Use one prefix per line. Niko will respond to all of them.",icon:"terminal"}),r.jsx(Ze,{label:"Command prefixes",hint:"The default prefix is .",children:r.jsx("textarea",{rows:3,maxLength:200,value:m.prefixes,onChange:S=>w("prefixes",S.target.value),placeholder:".\\n!"})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Xs,{label:"Welcome flow",title:"Welcome and rules",detail:"Choose where new members see your welcome message and rules.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(Ze,{label:"Welcome channel",children:r.jsxs("select",{value:L,onChange:S=>w("welcome_channel",S.target.value),children:[r.jsx("option",{value:"",children:"Disabled"}),z.map(S=>r.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),r.jsx(Ze,{label:"Welcome title",children:r.jsx("input",{value:m.welcome_title,maxLength:200,onChange:S=>w("welcome_title",S.target.value),placeholder:"Welcome to the server"})}),r.jsx(Ze,{label:"Welcome message",hint:"Supports {user} and {name}",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:m.welcome_description,onChange:S=>w("welcome_description",S.target.value),placeholder:"Welcome {user}!"})}),r.jsx(Ze,{label:"Accent color",hint:"Hex color, for example 5865F2",children:r.jsx("input",{value:m.welcome_color,maxLength:7,onChange:S=>w("welcome_color",S.target.value),placeholder:"5865F2"})}),r.jsx(Ze,{label:"Welcome image URL",children:r.jsx("input",{type:"url",value:m.welcome_image,onChange:S=>w("welcome_image",S.target.value),placeholder:"https://..."})}),r.jsx(Ze,{label:"Rules channel",children:r.jsxs("select",{value:m.rules_channel,onChange:S=>w("rules_channel",S.target.value),children:[r.jsx("option",{value:"",children:"Not configured"}),B.map(S=>r.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),r.jsx(Ze,{label:"Rules text",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:m.rules_text,onChange:S=>w("rules_text",S.target.value),placeholder:"Write the rules members should acknowledge."})}),r.jsx(Ze,{label:"Role after rules acknowledgment",children:r.jsxs("select",{value:m.rules_role_id,onChange:S=>w("rules_role_id",S.target.value),children:[r.jsx("option",{value:"",children:"No role"}),Du(l,m.rules_role_id?[m.rules_role_id]:[]).map(S=>r.jsxs("option",{value:S.id,children:["@",S.name]},S.id))]})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Xs,{label:"Audit trail",title:"Logging destinations",detail:"Pick a channel for each event type and disable categories you do not need.",icon:"book"}),r.jsx("div",{className:"server-logging-list",children:ap.map(([S,Q])=>{const te=Ys(l,m.logging[S]);return r.jsxs("div",{className:"server-logging-row",children:[r.jsxs("label",{className:"form-field",children:[r.jsxs("span",{className:"form-label",children:[Q," logs"]}),r.jsxs("select",{value:String(m.logging[S]||""),onChange:se=>F(S,se.target.value),children:[r.jsx("option",{value:"",children:"Not set"}),te.map(se=>r.jsxs("option",{value:se.id,children:["#",se.name]},se.id))]})]}),r.jsxs("label",{className:"setting-row compact-setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enabled"}),r.jsx("small",{children:ip(l,m.logging[S])})]}),r.jsx("input",{type:"checkbox",checked:!m.disabled_logging.includes(S),onChange:()=>N(S)}),r.jsx("i",{"aria-hidden":"true"})]})]},S)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Xs,{label:"Support desk",title:"Ticket panel",detail:"Configure the public panel and decide who can handle tickets.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(Ze,{label:"Panel title",children:r.jsx("input",{value:m.panel_title,maxLength:200,onChange:S=>w("panel_title",S.target.value),placeholder:"Open a Ticket"})}),r.jsx(Ze,{label:"Panel channel",children:r.jsxs("select",{value:I,onChange:S=>w("panel_channel_id",S.target.value),children:[r.jsx("option",{value:"",children:"Keep current panel channel"}),b.map(S=>r.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),r.jsx(Ze,{label:"Panel description",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:m.panel_description,onChange:S=>w("panel_description",S.target.value),placeholder:"Tell members what the ticket panel is for."})}),r.jsx(Ze,{label:"Ticket categories",hint:"One category per line",children:r.jsx("textarea",{rows:4,value:m.panel_categories,onChange:S=>w("panel_categories",S.target.value),placeholder:"General\\nSupport\\nReports"})}),r.jsx(Ze,{label:"Support roles",hint:"Hold Ctrl/Cmd to select more than one",children:r.jsx("select",{multiple:!0,value:m.support_roles,onChange:S=>w("support_roles",Array.from(S.target.selectedOptions,Q=>Q.value)),children:U.map(S=>r.jsxs("option",{value:S.id,children:["@",S.name]},S.id))})})]}),r.jsx("p",{className:"form-hint",children:"Saving panel settings updates the existing posted panel when Niko can find its saved message."})]}),r.jsx(sp,{state:v})]})]})}function lp({auth:o}){const c=sa();return r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"n"}),r.jsx("div",{className:"eyebrow",children:"Private workspace"}),r.jsxs("h1",{children:["Settle in, ",r.jsx("em",{children:"admin."})]}),r.jsx("p",{children:"Sign in with Discord to see your Niko profile and manage the servers you look after."}),o.oauth_available?r.jsxs("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard",children:[r.jsx(q,{name:"lock"})," Continue with Discord ",r.jsx(q,{name:"arrow"})]}):r.jsxs("div",{className:"notice warning",children:["Discord login is not configured yet. Add ",r.jsx("code",{children:"DISCORD_CLIENT_SECRET"})," to the environment and restart the bot."]}),!c&&r.jsx("p",{className:"form-hint",children:"The public bot configuration is still loading."}),r.jsx("a",{className:"back-link",href:"/",onClick:l=>{l.preventDefault(),ie("/")},children:"Return to public site"})]})})]})}function cp({section:o,guild:c,stats:l,csrfToken:d}){const[m,f]=A.useState(null),[v,P]=A.useState([]),[w,F]=A.useState(null),[N,C]=A.useState(null),[L,I]=A.useState(!0),[z,B]=A.useState("");return A.useEffect(()=>{I(!0),B(""),(o==="overview"?dh(c.id).then(f):o==="leveling"?Promise.all([mh(c.id),ju(c.id),bu(c.id)]).then(([U,S,Q])=>{P(U),F(S),C(Q)}):Promise.all([ju(c.id),bu(c.id)]).then(([U,S])=>{F(U),C(S)})).catch(U=>B(U instanceof Error?U.message:"This server could not be loaded.")).finally(()=>I(!1))},[c.id,o]),L?r.jsxs("div",{className:"section-loading section-skeleton",role:"status","aria-label":`Loading ${o}`,children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsxs("span",{children:["Loading ",o,"..."]})]}):z?r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Couldn’t load this page."}),r.jsx("span",{children:z}),r.jsx("button",{className:"button button-muted",onClick:()=>window.location.reload(),children:"Try again"})]}):o==="overview"&&m?r.jsx(Xh,{overview:m}):o==="leveling"?r.jsx(Yh,{guildId:c.id,rows:v,config:w,resources:N,csrfToken:d}):o==="moderation"?r.jsx(Zh,{guildId:c.id,config:w,csrfToken:d}):o==="server"?r.jsx(op,{guildId:c.id,config:w,resources:N,csrfToken:d}):o==="customization"?r.jsx(np,{guildId:c.id,config:w,csrfToken:d}):r.jsx(ep,{guildId:c.id,config:w,csrfToken:d})}function up(){return r.jsxs("div",{className:"section-loading section-skeleton dashboard-loading",role:"status",children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"Preparing your dashboard..."})]})}function dp(){sa();const[o,c]=A.useState(Cu),[l,d]=A.useState(null),[m,f]=A.useState(null),[v,P]=A.useState(null),[w,F]=A.useState([]),[N,C]=A.useState(null),[L,I]=A.useState(!0),[z,B]=A.useState("");if(A.useEffect(()=>{const _=()=>c(Cu());return window.addEventListener("popstate",_),()=>window.removeEventListener("popstate",_)},[]),A.useEffect(()=>{I(!0),Promise.all([ih(),Ou()]).then(([_,X])=>(d(_),f(X),_.authenticated?Promise.all([uh(),ch()]).then(([he,je])=>{P(he),F(je)}):null)).catch(_=>B(_ instanceof Error?_.message:"Dashboard unavailable")).finally(()=>I(!1))},[]),A.useEffect(()=>{if(o.view!=="guild"){C(null);return}const _=w.find(X=>X.id===o.guildId&&X.installed!==!1);_?(C(_),localStorage.setItem("niko-guild",_.id)):o.guildId&&w.length&&ie(Nu())},[w,o.guildId,o.view]),L||!l)return r.jsxs("div",{className:"dashboard-state",children:[r.jsx("div",{className:"loading-ring"}),r.jsx("p",{children:"Connecting to Niko…"})]});if(z)return r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Connection issue"}),r.jsxs("h1",{children:["Couldn’t load",r.jsx("br",{}),r.jsx("em",{children:"your workspace."})]}),r.jsx("p",{children:z}),r.jsxs("button",{className:"button button-primary",onClick:()=>window.location.reload(),children:["Try again ",r.jsx(q,{name:"arrow"})]})]})})]});if(!l.authenticated)return r.jsx(lp,{auth:l});const b=_=>{_.installed!==!1&&(localStorage.setItem("niko-guild",_.id),ie(Ir(_.id,o.section)))},U=_=>{_.installed!==!1&&(localStorage.setItem("niko-guild",_.id),ie(Ir(_.id,"overview")))},S=_=>{ie(N?Ir(N.id,_):Ir())},Q=()=>ie(Ir()),te=()=>ie(Nu());let se;return o.view==="servers"?se=r.jsx(Qh,{guilds:w,onManage:U}):o.view==="guild"?se=N?r.jsx(cp,{section:o.section,guild:N,stats:m,csrfToken:l.csrf_token},`${N.id}-${o.section}`):r.jsx(up,{}):se=r.jsx(qh,{user:l.user,overview:v,guilds:w,onServers:te,onManage:U}),r.jsx(Kh,{user:l.user,guilds:w,selectedGuild:N,view:o.view,section:o.section,stats:m,onHome:Q,onServers:te,onGuildChange:b,onSectionChange:S,children:se})}function mp({value:o,onChange:c,placeholder:l="Search documentation...",onFocus:d,onBlur:m}){const[f,v]=A.useState(!1),P=A.useRef(null),[w,F]=A.useState(!1);A.useEffect(()=>{const z=B=>{var b;(B.metaKey||B.ctrlKey)&&B.key==="k"&&(B.preventDefault(),(b=P.current)==null||b.focus())};return document.addEventListener("keydown",z),()=>document.removeEventListener("keydown",z)},[]);const N=()=>{v(!0),F(!0),d==null||d()},C=()=>{v(!1),setTimeout(()=>F(!1),200),m==null||m()},L=z=>{c(z.target.value)},I=z=>{var B;z.key==="Escape"&&((B=P.current)==null||B.blur())};return r.jsxs("div",{className:`doc-search-bar ${w?"expanded":""}`,children:[r.jsxs("div",{className:"search-input-wrapper",children:[r.jsx(q,{name:"search",className:"search-icon"}),r.jsx("input",{ref:P,type:"text",value:o,onChange:L,onFocus:N,onBlur:C,onKeyDown:I,placeholder:l,className:"search-input","aria-label":"Search documentation"}),r.jsxs("kbd",{className:"search-shortcut",children:[r.jsx("span",{className:"shortcut-key",children:"⌘"}),"K"]})]}),r.jsxs("div",{className:"search-hint",children:["Press ",r.jsx("kbd",{children:"⌘K"})," to focus search"]})]})}function hp({selectedCategory:o,onSelectCategory:c,sections:l,allCategoriesLabel:d="All Categories"}){return r.jsx("div",{className:"doc-filters",children:r.jsxs("div",{className:"filter-tabs",role:"tablist","aria-label":"Filter by category",children:[r.jsx("button",{role:"tab","aria-selected":o==="",className:`filter-tab ${o===""?"active":""}`,onClick:()=>c(""),children:d}),l.map(m=>r.jsxs("button",{role:"tab","aria-selected":o===m.id,className:`filter-tab ${o===m.id?"active":""}`,onClick:()=>c(m.id),children:[r.jsx(q,{name:m.icon,size:14}),r.jsx("span",{children:m.label})]},m.id))]})})}function uo({doc:o,variant:c="default"}){const l="page"in o?o.page:o,[d,m]=A.useState(!1),f=w=>{w.preventDefault(),ie(`/docs/${l.slug}`)},v=w=>{(w.key==="Enter"||w.key===" ")&&(w.preventDefault(),ie(`/docs/${l.slug}`))};if(c==="compact")return r.jsx("a",{href:`/docs/${l.slug}`,onClick:f,onKeyDown:v,className:"doc-card-compact",tabIndex:0,role:"button",children:r.jsxs("div",{className:"compact-content",children:[r.jsx("span",{className:"compact-title",children:l.title}),r.jsx("span",{className:"compact-excerpt",children:l.excerpt})]})});const P="highlights"in o?o.highlights:[];return r.jsx("article",{className:`doc-card ${c==="highlighted"?"highlighted":""}`,children:r.jsxs("div",{className:`doc-card-content ${d?"loaded":""}`,children:[r.jsxs("div",{className:"doc-card-header",children:[r.jsx("span",{className:"doc-category",children:l.category.replace(/-/g," ")}),r.jsxs("span",{className:"doc-order",children:["#",l.order]})]}),r.jsx("h3",{className:"doc-title",children:l.title}),r.jsx("p",{className:"doc-excerpt",children:l.excerpt}),P.length>0&&r.jsx("div",{className:"doc-highlights",children:P.slice(0,2).map((w,F)=>r.jsxs("p",{className:"highlight-snippet",children:[w.slice(0,150),w.length>150?"...":""]},F))}),r.jsxs("div",{className:"doc-card-footer",children:[r.jsx("div",{className:"doc-tags",children:l.tags.slice(0,3).map(w=>r.jsxs("span",{className:"doc-tag",children:["#",w]},w))}),r.jsxs("a",{href:`/docs/${l.slug}`,onClick:f,onKeyDown:v,className:"doc-read-more",children:["Read more ",r.jsx(q,{name:"arrow",size:14})]})]})]})})}const Te=[{slug:"welcome",title:"Welcome to Niko",category:"getting-started",excerpt:"New to Niko? Start here to understand what the bot can do for your server.",tags:["introduction","overview","beginner"],order:1,content:`
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
    `}];function pp(o){return Te.find(c=>c.slug===o)}const an=[{id:"getting-started",label:"Getting Started",description:"New to Niko? Start here.",icon:"icon_home",count:Te.filter(o=>o.category==="getting-started").length},{id:"setup",label:"Setup",description:"Configure Niko for your server.",icon:"icon_settings",count:Te.filter(o=>o.category==="setup").length},{id:"economy",label:"Economy",description:"Money, jobs, banking, and more.",icon:"icon_economy",count:Te.filter(o=>o.category==="economy").length},{id:"leveling",label:"Leveling",description:"XP, levels, and rankings.",icon:"icon_leveling",count:Te.filter(o=>o.category==="leveling").length},{id:"moderation",label:"Moderation",description:"Moderation tools and commands.",icon:"icon_moderation",count:Te.filter(o=>o.category==="moderation").length},{id:"automod",label:"AutoMod",description:"Automated moderation features.",icon:"icon_automod",count:Te.filter(o=>o.category==="automod").length},{id:"logging",label:"Logging",description:"Server event logging.",icon:"icon_settings",count:Te.filter(o=>o.category==="logging").length},{id:"social",label:"Social",description:"Community engagement features.",icon:"icon_heart",count:Te.filter(o=>o.category==="social").length},{id:"utility",label:"Utility",description:"Helpful tools and utilities.",icon:"icon_utility",count:Te.filter(o=>o.category==="utility").length},{id:"voice",label:"Voice",description:"Voice and music features.",icon:"icon_bot",count:Te.filter(o=>o.category==="voice").length},{id:"ai",label:"AI",description:"AI-powered features.",icon:"icon_ai",count:Te.filter(o=>o.category==="ai").length},{id:"dashboard",label:"Dashboard",description:"Web dashboard guides.",icon:"icon_settings",count:Te.filter(o=>o.category==="dashboard").length},{id:"tips",label:"Tips",description:"Tips and best practices.",icon:"icon_lightbulb",count:Te.filter(o=>o.category==="tips").length}];function Ku(){const[o,c]=A.useState({query:"",category:"",tags:[]}),l=A.useCallback(w=>{c(F=>({...F,query:w.toLowerCase(),tags:[]}))},[]),d=A.useCallback(w=>{c(F=>({...F,category:w,tags:[]}))},[]),m=A.useCallback(w=>{c(F=>{const N=F.tags.includes(w)?F.tags.filter(C=>C!==w):[...F.tags,w];return{...F,tags:N,query:""}})},[]),f=A.useCallback(()=>{c({query:"",category:"",tags:[]})},[]),v=A.useMemo(()=>{const{query:w,category:F,tags:N}=o;if(!w&&!F&&N.length===0)return Te.map(L=>({page:L,score:1,highlights:[]}));const C=[];for(const L of Te)if(!(F&&L.category!==F)&&!(N.length>0&&!N.some(I=>L.tags.includes(I))))if(w){const I=fp(L,w);if(I===0)continue;const z=gp(L,w);C.push({page:L,score:I,highlights:z})}else C.push({page:L,score:1,highlights:[]});return C.sort((L,I)=>I.score!==L.score?I.score-L.score:L.page.order-I.page.order),C},[o]),P=o.query!==""||o.category!==""||o.tags.length>0;return{filters:o,setQuery:l,setCategory:d,toggleTag:m,clearFilters:f,results:v,hasActiveFilters:P,resultCount:v.length}}function fp(o,c){let l=0;const d=c.toLowerCase();o.title.toLowerCase()===d?l+=100:o.title.toLowerCase().includes(d)&&(l+=50),o.excerpt.toLowerCase().includes(d)&&(l+=25),o.content.toLowerCase().includes(d)&&(l+=10);for(const m of o.tags)m.toLowerCase().includes(d)&&(l+=15);return o.category.toLowerCase().includes(d)&&(l+=5),l}function gp(o,c){const l=[],d=c.toLowerCase(),m=3;if(o.title.toLowerCase().includes(d)&&(l.push(o.title),l.length>=m)||o.excerpt.toLowerCase().includes(d)&&(l.push(o.excerpt),l.length>=m))return l;const f=o.content.split(`
`).filter(v=>v.trim());for(const v of f)if(v.toLowerCase().includes(d)){const P=v.replace(/#{1,6}\s?/g,"").trim();if(P.length>10&&(l.push(P),l.length>=m))break}return l}function vp(){return A.useMemo(()=>{const c={};return Te.forEach(l=>{l.tags.forEach(d=>{c[d]=(c[d]||0)+1})}),Object.entries(c).map(([l,d])=>({tag:l,count:d})).sort((l,d)=>d.count-l.count)},[])}function yp({slug:o}){var w,F;const{setCategory:c,clearFilters:l}=Ku();A.useEffect(()=>{window.location.hash!==`#/docs/${o}`&&window.history.replaceState(null,"",`#/docs/${o}`)},[o]);const d=pp(o);if(!d)return r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:"docs"}),r.jsx("main",{className:"shell page-main docs-page",children:r.jsxs("div",{className:"docs-not-found",children:[r.jsx(q,{name:"doc",size:48,className:"not-found-icon"}),r.jsx("h1",{children:"Page Not Found"}),r.jsxs("p",{children:[`We couldn't find documentation for "`,o,'".']}),r.jsxs("div",{className:"not-found-actions",children:[r.jsx("button",{onClick:()=>ie("/docs"),children:"Browse all documentation"}),r.jsx("button",{onClick:()=>{ie("/docs"),l()},children:"Clear filters"})]})]})}),r.jsx(Bt,{})]});const m=N=>{const C=[],L=/(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*)/g;let I=0,z,B=0;for(;(z=L.exec(N))!==null;){z.index>I&&C.push(N.slice(I,z.index));const b=z[0];if(b.startsWith("`")&&b.endsWith("`")&&b.length>2)C.push(r.jsx("code",{className:"doc-inline-code",children:b.slice(1,-1)},B++));else if(b.startsWith("[")){const U=b.match(/^\[([^\]]+)\]\(([^)]+)\)$/);U?C.push(r.jsx("a",{href:U[2],target:"_blank",rel:"noreferrer",children:m(U[1])},B++)):C.push(b)}else b.startsWith("**")?C.push(r.jsx("strong",{children:m(b.slice(2,-2))},B++)):b.startsWith("*")?C.push(r.jsx("em",{children:m(b.slice(1,-1))},B++)):C.push(b);I=z.index+b.length}return I<N.length&&C.push(N.slice(I)),C},v=(N=>{const C=N.split(`
`),L=[];let I=0,z=null,B=[];const b=()=>{if(B.length===0)return;const S=z==="ol"?"ol":"ul";L.push(r.jsx(S,{className:`doc-content-list ${z==="ol"?"doc-content-list-ol":""}`,children:B.map((Q,te)=>r.jsx("li",{children:m(Q)},te))},`list-${L.length}`)),B=[],z=null},U=()=>{var te;const S=L[L.length-1];A.isValidElement(S)&&((te=S.props)==null?void 0:te.className)==="doc-content-spacer"||L.push(r.jsx("div",{className:"doc-content-spacer"},`spacer-${L.length}`))};for(;I<C.length;){const Q=C[I].trim();if(!Q){b(),U(),I+=1;continue}if(Q.startsWith("```")){b();const _=[];let X=I+1;for(;X<C.length&&C[X].trim()!=="```";)_.push(C[X]),X+=1;L.push(r.jsx("pre",{className:"doc-code-block",children:r.jsx("code",{children:_.join(`
`)})},`code-${I}`)),I=X+1;continue}if(Q.startsWith("|")){b();const _=[];let X=I;for(;X<C.length&&C[X].trim().startsWith("|");){const Ue=C[X].trim().replace(/^\|/,"").replace(/\|$/,"").split("|").map(ze=>ze.trim());_.push(Ue),X+=1}const he=_.length>1&&_[1].every(Ue=>/^:?-{2,}:?$/.test(Ue.replace(/\s+/g,""))),je=_[0],st=he?_.slice(2):_.slice(1);je.length>1&&L.push(r.jsxs("table",{className:"doc-table",children:[r.jsx("thead",{children:r.jsx("tr",{children:je.map((Ue,ze)=>r.jsx("th",{children:m(Ue)},ze))})}),r.jsx("tbody",{children:st.map((Ue,ze)=>r.jsx("tr",{children:Ue.map(($e,at)=>r.jsx("td",{children:m($e)},at))},ze))})]},`table-${I}`)),I=X;continue}if(Q.startsWith("### ")){b(),L.push(r.jsx("h4",{className:"doc-heading doc-heading-h4",children:Q.slice(4)},`h-${I}`)),I+=1;continue}if(Q.startsWith("## ")){b(),L.push(r.jsx("h3",{className:"doc-heading doc-heading-h3",children:Q.slice(3)},`h-${I}`)),I+=1;continue}if(Q.startsWith("# ")){b(),L.push(r.jsx("h2",{className:"doc-heading doc-heading-h2",children:Q.slice(2)},`h-${I}`)),I+=1;continue}if(Q.startsWith("> ")){b(),L.push(r.jsx("blockquote",{className:"doc-blockquote",children:m(Q.slice(2))},`q-${I}`)),I+=1;continue}const te=Q.match(/^[-*]\s+(.*)$/);if(te){z!=="ul"&&b(),z="ul",B.push(te[1]),I+=1;continue}const se=Q.match(/^\d+\.\s+(.*)$/);if(se){z!=="ol"&&b(),z="ol",B.push(se[1]),I+=1;continue}b(),L.push(r.jsx("p",{className:"doc-paragraph",children:m(Q)},`p-${I}`)),I+=1}return b(),L})(d.content),P=v.filter(N=>A.isValidElement(N)&&(N.type==="h2"||N.type==="h3"));return r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page docs-detail-page",children:[r.jsx("div",{className:"docs-detail-back",children:r.jsxs("button",{onClick:()=>ie("/docs"),className:"back-button",children:[r.jsx(q,{name:"arrow",size:16}),"Back to Documentation"]})}),r.jsxs("header",{className:"doc-article-header",children:[r.jsxs("div",{className:"doc-article-meta",children:[r.jsx("span",{className:"doc-category-badge",children:((w=an.find(N=>N.id===d.category))==null?void 0:w.label)||d.category}),r.jsxs("span",{className:"doc-order-badge",children:["Article #",d.order]})]}),r.jsx("h1",{className:"doc-article-title",children:d.title}),r.jsx("p",{className:"doc-article-excerpt",children:d.excerpt}),r.jsx("div",{className:"doc-article-tags",children:d.tags.map(N=>r.jsxs("span",{className:"doc-tag-pill",children:["#",N]},N))})]}),r.jsx("article",{className:"doc-article-content",children:v}),r.jsx("footer",{className:"doc-article-footer",children:r.jsx("div",{className:"doc-nav-container",children:r.jsxs("div",{className:"doc-nav-col",children:[r.jsx("span",{className:"doc-nav-label",children:"Category"}),r.jsxs("button",{className:"doc-nav-link",onClick:()=>{c(d.category),ie("/docs")},children:[r.jsx(q,{name:"arrow",size:14}),"View all ",(F=an.find(N=>N.id===d.category))==null?void 0:F.label]})]})})}),P.length>0&&r.jsxs("aside",{className:"doc-toc",children:[r.jsxs("div",{className:"toc-title",children:[r.jsx(q,{name:"utility",size:16}),r.jsx("span",{children:"On this page"})]}),r.jsx("nav",{className:"toc-nav",children:P.map((N,C)=>{var I;const L=(I=N.props.className)==null?void 0:I.includes("doc-heading-h2");return r.jsx("a",{href:`#${L?"h2-":"h3-"}-${C}`,className:`toc-link ${L?"toc-h2":"toc-h3"}`,children:N.props.children},C)})})]})]}),r.jsx(Bt,{})]})}function xp(){var te,se;const[o,c]=A.useState(!1),[l,d]=A.useState(""),[m,f]=A.useState(!1),{filters:v,setQuery:P,setCategory:w,toggleTag:F,clearFilters:N,results:C,hasActiveFilters:L,resultCount:I}=Ku(),z=vp();A.useEffect(()=>{const _=()=>{const X=window.location.hash.slice(1);if(X.startsWith("#/docs/")){const he=X.replace("#/docs/",""),je=Te.find(st=>st.slug===he);je&&(d(je.category),w(je.category))}};return _(),window.addEventListener("hashchange",_),()=>window.removeEventListener("hashchange",_)},[]);const B=()=>{f(!0)},b=_=>{d(_),w(_),c(!1)},U=()=>{v.query||f(!1)},S=_=>{ie(`/docs/${_}`),P(""),f(!1)},Q=A.useMemo(()=>{const _={};return C.forEach(X=>{const he=X.page.category;_[he]||(_[he]=[]),_[he].push(X)}),_},[C]);return r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page",children:[r.jsx("div",{className:"docs-hero",children:r.jsxs("div",{className:"docs-hero-content",children:[r.jsx("div",{className:"eyebrow docs-eyebrow",children:"Documentation Center"}),r.jsxs("h1",{className:"docs-title",children:["Everything you need to know about",r.jsx("br",{}),r.jsx("span",{className:"title-accent",children:"using Niko"})]}),r.jsx("p",{className:"docs-subtitle",children:"Comprehensive guides, command references, and tips to help you get the most out of your server bot."})]})}),r.jsx("div",{className:`docs-search-section ${m?"active":""}`,children:r.jsxs("div",{className:"docs-search-container",children:[r.jsx(mp,{value:v.query,onChange:P,placeholder:"Search documentation, commands, guides...",onFocus:B,onBlur:U}),m&&v.query&&C.length>0&&r.jsxs("div",{className:"search-results-dropdown",children:[r.jsxs("div",{className:"search-results-header",children:[r.jsxs("span",{className:"results-count",children:[I," ",I===1?"result":"results"]}),r.jsx("button",{className:"clear-search-btn",onClick:()=>{P(""),N(),d("")},children:"Clear"})]}),r.jsx("div",{className:"search-results-list",children:C.slice(0,8).map((_,X)=>r.jsxs("button",{className:"search-result-item",onClick:()=>S(_.page.slug),onMouseEnter:()=>{},children:[r.jsx("div",{className:"result-icon",children:r.jsx(q,{name:"doc",size:18})}),r.jsxs("div",{className:"result-content",children:[r.jsx("div",{className:"result-title",children:_.page.title}),r.jsx("div",{className:"result-excerpt",children:_.page.excerpt}),_.highlights.length>0&&r.jsxs("div",{className:"result-highlight",children:[_.highlights[0].slice(0,100),"..."]})]}),r.jsx(q,{name:"arrow",size:14,className:"result-arrow"})]},_.page.slug))}),C.length>8&&r.jsx("div",{className:"search-results-footer",children:r.jsxs("span",{children:["Showing 8 of ",C.length," results. Browse all docs below."]})})]})]})}),r.jsxs("div",{className:"docs-mobile-nav",children:[r.jsx("button",{className:"mobile-menu-toggle",onClick:()=>c(!o),"aria-label":"Toggle documentation menu",children:r.jsx(q,{name:"utility",size:20})}),o&&r.jsxs("div",{className:"mobile-nav-panel",children:[r.jsxs("div",{className:"mobile-nav-header",children:[r.jsx("h3",{children:"Documentation"}),r.jsx("button",{className:"close-menu-btn",onClick:()=>c(!1),"aria-label":"Close menu",children:r.jsx(q,{name:"utility",size:16,className:"rotated"})})]}),r.jsx("div",{className:"mobile-nav-sections",children:an.map(_=>r.jsxs("button",{className:`mobile-nav-item ${l===_.id?"active":""}`,onClick:()=>{b(_.id)},children:[r.jsx(q,{name:_.icon,size:18}),r.jsx("span",{className:"mobile-section-label",children:_.label}),r.jsx("span",{className:"mobile-section-count",children:_.count})]},_.id))})]})]}),z.length>0&&!L&&r.jsxs("div",{className:"docs-tags-cloud",children:[r.jsxs("div",{className:"tags-cloud-title",children:[r.jsx(q,{name:"utility",size:16}),r.jsx("span",{children:"Popular Topics"})]}),r.jsx("div",{className:"tags-cloud-list",children:z.slice(0,15).map(({tag:_,count:X})=>r.jsxs("button",{className:"tag-cloud-item",onClick:()=>F(_),style:{fontSize:`${.75+Math.min(X/4,1)}rem`},children:["#",_,r.jsx("span",{className:"tag-count",children:X})]},_))})]}),r.jsx("div",{className:"docs-category-filters",children:r.jsx(hp,{selectedCategory:v.category,onSelectCategory:b,sections:an})}),L&&r.jsxs("div",{className:"docs-results-header",children:[r.jsxs("div",{className:"results-info",children:[r.jsxs("span",{className:"results-count-large",children:[I," ",I===1?"article":"articles"]}),v.query&&r.jsxs("span",{className:"search-query-display",children:['for "',r.jsx("strong",{children:v.query}),'"']})]}),r.jsxs("button",{className:"clear-all-btn",onClick:()=>{N(),d("")},disabled:!L,children:[r.jsx(q,{name:"utility",size:14}),"Clear all filters"]})]}),r.jsx("div",{className:"docs-content",children:L?r.jsx("div",{className:"search-results-view",children:Object.entries(Q).map(([_,X])=>{var he;return r.jsxs("section",{className:"results-category",children:[r.jsx("h2",{className:"category-title",children:((he=an.find(je=>je.id===_))==null?void 0:he.label)||_}),r.jsx("div",{className:"category-results-grid",children:X.map(je=>r.jsx(uo,{doc:je,variant:"highlighted"},je.page.slug))})]},_)})}):l?r.jsxs("div",{className:"category-view",children:[r.jsxs("div",{className:"category-header",children:[r.jsx("h2",{className:"category-page-title",children:((te=an.find(_=>_.id===l))==null?void 0:te.label)||l}),r.jsx("p",{className:"category-description",children:(se=an.find(_=>_.id===l))==null?void 0:se.description})]}),r.jsx("div",{className:"category-articles",children:Te.filter(_=>_.category===l).sort((_,X)=>_.order-X.order).map(_=>r.jsx(uo,{doc:_},_.slug))})]}):r.jsx("div",{className:"all-categories-view",children:an.map(_=>r.jsxs("section",{className:"docs-section",id:`section-${_.id}`,children:[r.jsxs("div",{className:"section-header",children:[r.jsx("div",{className:"section-icon",children:r.jsx(q,{name:_.icon,size:28})}),r.jsxs("div",{className:"section-info",children:[r.jsx("h2",{className:"section-title",children:_.label}),r.jsx("p",{className:"section-description",children:_.description})]}),r.jsx("span",{className:"section-count",children:_.count})]}),r.jsx("div",{className:"section-articles",children:Te.filter(X=>X.category===_.id).sort((X,he)=>X.order-he.order).map(X=>r.jsx(uo,{doc:X},X.slug))})]},_.id))})}),r.jsxs("div",{className:"docs-footer-note",children:[r.jsx(q,{name:"book",size:20}),r.jsxs("div",{children:[r.jsx("strong",{children:"Want more detail?"}),r.jsxs("p",{children:["The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in the"," ",r.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"docs/"})," ","folder."]})]})]})]}),r.jsx(Bt,{})]})}function kp(){const o=sa(),[c,l]=A.useState(null);A.useEffect(()=>{Ou().then(l).catch(()=>{})},[]);const d=[["spark","AI that remembers","Thoughtful conversation with a cozy personality and controls that respect your community."],["chart","A living economy","Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],["shield","Confident moderation","Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],["users","Community rituals","Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."]];return r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:"home"}),r.jsxs("main",{children:[r.jsxs("section",{className:"hero shell",children:[r.jsxs("div",{className:"hero-copy",children:[r.jsxs("div",{className:"eyebrow",children:[r.jsx("span",{className:"status-dot"})," Discord companion · online"]}),r.jsxs("div",{className:"hero-identity",children:[r.jsx("span",{className:"hero-avatar",children:o!=null&&o.bot_avatar_url?r.jsx("img",{src:o.bot_avatar_url,alt:"Niko"}):"n"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Niko"}),r.jsx("small",{children:"Your server’s calm, capable co-pilot"})]})]}),r.jsxs("h1",{children:["Useful tools for a ",r.jsx("em",{children:"better server."})]}),r.jsx("p",{children:"Niko handles the everyday work of running a Discord community, so your moderators can focus on the people in it."}),r.jsxs("div",{className:"hero-buttons",children:[r.jsxs("a",{className:"button button-primary",href:(o==null?void 0:o.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Invite Niko ",r.jsx(q,{name:"arrow"})]}),r.jsx("a",{className:"button button-muted",href:"/commands",onClick:m=>{m.preventDefault(),ie("/commands")},children:"Explore commands"})]}),r.jsxs("div",{className:"stats-strip",children:[r.jsxs("div",{children:[r.jsx("strong",{children:Ee(c==null?void 0:c.guild_count)}),r.jsx("span",{children:"servers"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:Ee(c==null?void 0:c.user_count)}),r.jsx("span",{children:"members"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:Ee(c==null?void 0:c.command_count)}),r.jsx("span",{children:"commands"})]})]})]}),r.jsx("div",{className:"hero-art","aria-label":"A preview of Niko's server workspace",children:r.jsxs("div",{className:"workspace-preview",children:[r.jsxs("div",{className:"workspace-preview-top",children:[r.jsxs("span",{className:"preview-dots",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"server workspace"}),r.jsxs("span",{className:"preview-status",children:[r.jsx("span",{className:"status-dot"})," live"]})]}),r.jsxs("div",{className:"preview-body",children:[r.jsxs("div",{className:"preview-sidebar",children:[r.jsx("span",{className:"preview-label",children:"NIKO"}),r.jsx("b",{children:"Overview"}),r.jsx("span",{children:"Economy"}),r.jsx("span",{children:"Leveling"}),r.jsx("span",{children:"Moderation"}),r.jsx("span",{children:"AI controls"})]}),r.jsxs("div",{className:"preview-main",children:[r.jsx("span",{className:"preview-label",children:"SERVER SNAPSHOT"}),r.jsx("strong",{children:"Everything in one place."}),r.jsxs("div",{className:"preview-stats",children:[r.jsxs("span",{children:[r.jsx("b",{children:Ee(c==null?void 0:c.user_count)}),r.jsx("small",{children:"members"})]}),r.jsxs("span",{children:[r.jsx("b",{children:Ee(c==null?void 0:c.command_count)}),r.jsx("small",{children:"commands"})]})]}),r.jsxs("div",{className:"preview-line",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]})]})]})]})})]}),r.jsxs("section",{className:"shell intro-section",children:[r.jsx("div",{className:"section-kicker",children:"Why Niko"}),r.jsxs("div",{className:"intro-grid",children:[r.jsxs("h2",{children:["The good kind of",r.jsx("br",{}),r.jsx("em",{children:"always-on."})]}),r.jsx("p",{children:"Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile."})]})]}),r.jsx("section",{className:"shell feature-grid",children:d.map(([m,f,v])=>r.jsxs("article",{className:"feature-card",children:[r.jsx("span",{className:"feature-icon",children:r.jsx(q,{name:m})}),r.jsx("h3",{children:f}),r.jsx("p",{children:v}),r.jsxs("a",{href:"/docs",onClick:P=>{P.preventDefault(),ie("/docs")},children:["Learn more ",r.jsx(q,{name:"arrow"})]})]},f))}),r.jsxs("section",{className:"shell callout",children:[r.jsxs("div",{children:[r.jsx("div",{className:"section-kicker",children:"Ready when you are"}),r.jsxs("h2",{children:["A calmer, cleverer home",r.jsx("br",{}),"for your community."]})]}),r.jsxs("a",{className:"button button-primary",href:(o==null?void 0:o.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Bring Niko in ",r.jsx(q,{name:"arrow"})]})]})]}),r.jsx(Bt,{})]})}const wp=[{code:"USDT",label:"Tether"},{code:"ETH",label:"Ethereum"},{code:"BTC",label:"Bitcoin"},{code:"BNB",label:"BNB"},{code:"LTC",label:"Litecoin"},{code:"DOGE",label:"Dogecoin"},{code:"TRX",label:"TRON"},{code:"XMR",label:"Monero"}];function jp(){const c=new URLSearchParams(window.location.search).get("token")||"",[l,d]=A.useState("5"),[m,f]=A.useState("USDT"),[v,P]=A.useState(!1),[w,F]=A.useState(""),[N,C]=A.useState(null),[L,I]=A.useState(null),[z,B]=A.useState(!1);A.useEffect(()=>{c||B(!0)},[c]),A.useEffect(()=>{if(!(N!=null&&N.status_url)||N.paid)return;const U=setInterval(async()=>{try{const S=await nt(N.status_url);I(S),S.paid&&clearInterval(U)}catch{}},5e3);return()=>clearInterval(U)},[N]);const b=async U=>{U.preventDefault(),P(!0),F("");try{const S=await nt("/api/donations/invoice",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:c,amount:parseFloat(l),currency:m})});C(S),S.error&&(F(S.error),C(null))}catch(S){F(S instanceof Error?S.message:"Could not create invoice.")}finally{P(!1)}};return z?r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Invalid donation link"}),r.jsxs("h1",{children:["This link is ",r.jsx("em",{children:"invalid."})]}),r.jsxs("p",{children:["The donation link is missing or has expired. Use the"," ",r.jsx("code",{children:"/donate"})," command in Discord to generate a new one."]}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>ie("/"),children:"Return home"})]})})]}):L!=null&&L.paid?r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"✓"}),r.jsx("div",{className:"eyebrow",children:"Payment confirmed"}),r.jsxs("h1",{children:["Thank you ",r.jsx("em",{children:"for supporting!"})]}),r.jsx("p",{children:"Your donation has been confirmed. You will receive the Supporter badge shortly."}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>ie("/"),children:"Return home"})]})})]}):r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:"home"}),r.jsx("main",{className:"page-main",children:r.jsx("div",{className:"shell",children:r.jsxs("div",{className:"page-heading",style:{maxWidth:500,margin:"0 auto"},children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:15},children:"Support Niko"}),r.jsxs("h1",{children:["Keep Niko ",r.jsx("em",{children:"running."})]}),r.jsx("p",{style:{color:"var(--muted)",marginBottom:30},children:"Your donation helps cover hosting costs and keeps Niko running for all servers. Choose an amount and cryptocurrency below."}),N!=null&&N.pay_link?r.jsxs("div",{className:"dash-panel",style:{marginBottom:24},children:[r.jsx("div",{className:"panel-heading",children:r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Invoice created"}),r.jsx("h3",{children:"Complete your payment"})]})}),r.jsxs("p",{style:{color:"var(--muted)",fontSize:12,marginBottom:16},children:["Amount: ",r.jsxs("strong",{children:["$",parseFloat(l).toFixed(2)," USD"]})," in"," ",r.jsx("strong",{children:m})]}),r.jsxs("p",{style:{color:"var(--dim)",fontSize:10,marginBottom:16},children:["Track ID: ",r.jsx("code",{children:N.track_id})," · Expires in 60 minutes"]}),r.jsxs("a",{className:"button button-primary",href:N.pay_link,target:"_blank",rel:"noopener noreferrer",children:["Pay now ",r.jsx(q,{name:"arrow"})]}),r.jsx("p",{style:{color:"var(--dim)",fontSize:10,marginTop:12},children:"Payment will be confirmed automatically once the transaction is processed on-chain."})]}):r.jsxs("form",{onSubmit:b,className:"dash-panel",style:{marginBottom:24},children:[r.jsxs("div",{className:"form-grid",children:[r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Amount (USD)"}),r.jsx("input",{type:"number",min:"1",max:"10000",step:"0.01",value:l,onChange:U=>d(U.target.value)}),r.jsx("small",{children:"Minimum $1.00, maximum $10,000.00"})]}),r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Cryptocurrency"}),r.jsx("select",{value:m,onChange:U=>f(U.target.value),children:wp.map(U=>r.jsxs("option",{value:U.code,children:[U.label," (",U.code,")"]},U.code))})]})]}),w&&r.jsx("p",{className:"form-error",style:{marginTop:12},role:"alert",children:w}),r.jsx("div",{style:{marginTop:16},children:r.jsx("button",{className:"button button-primary",type:"submit",disabled:v,children:v?"Creating invoice…":"Create invoice"})})]}),r.jsxs("div",{className:"docs-footer-note",style:{marginTop:20},children:[r.jsx("strong",{children:"How it works"}),r.jsx("p",{children:'1. Choose an amount and currency above · 2. Click "Pay now" to open the payment page · 3. Send crypto to the displayed address · 4. Payment is confirmed automatically once processed on-chain'})]})]})})})]})}const bp={privacy:{title:"Privacy policy",intro:"Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",sections:[["Information we use","User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature."],["How it is used","Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],["Storage and retention","Data is stored by the server hosting Niko in local JSON and SQLite files. Economy, leveling, and configuration data remain until removed. AI conversation history is limited and can be cleared with /clearhistory."],["Third-party services","When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Music and external lookup features may contact their respective services."],["Your choices","Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."]]},terms:{title:"Terms of service",intro:"By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",sections:[["Permitted use","Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],["Availability","Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],["Moderation","The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],["AI content","AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],["Virtual items","In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],["Contact","Questions or concerns can be sent through the Niko support server."]]},community:{title:"Community policy",intro:"These community expectations apply to every server that uses Niko. By adding the bot to a server, the server's owners and administrators agree to uphold these standards.",sections:[["Purpose","Niko is a community companion for Discord servers of all kinds. To keep the platform safe for everyone, all servers using Niko must follow the expectations below in addition to Discord's Terms of Service and Community Guidelines."],["Discrimination and harassment","Servers must not permit or promote discrimination, harassment, or hate speech targeting people based on race, ethnicity, national origin, religion, disability, gender, gender identity or expression, sexual orientation, age, veteran status, or any other protected identity characteristic."],["Illegal and malicious content","Servers must not create, host, share, or distribute illegal or malicious content. This includes, but is not limited to: child sexual abuse material (CSAM), malware and other malicious software, gore or shock content, pirated media and/or software, content that facilitates violence or terrorism, scams and phishing, and any other content that is illegal under applicable law."],["Other prohibited conduct","Servers must not use Niko to facilitate doxxing, targeted harassment campaigns, sextortion, trafficking, or the sexualization of minors in any form."],["Enforcement and investigations","When a server is reported or flagged for potentially violating this policy, Niko will send a warning notice to the server. The notice is followed by an investigation by Niko staff. Servers that cooperate in good faith and are found not to be breaking the policies will not receive any further action."],["Obstruction of investigations","Banning, kicking, or otherwise removing the staff member(s) sent to investigate, or hiding, deleting, or tampering with potential evidence, is treated as an admission of guilt. Doing so will result in the server — and any users who are involved — being permanently blacklisted from further use of Niko, in addition to any other action the investigation warrants."],["Reporting","If you believe a server using Niko is violating this policy, report it through the Niko support server. Reports are reviewed by staff and handled confidentially."]]}};function mo({type:o}){const c=bp[o];return r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:o}),r.jsxs("main",{className:"shell page-main legal-page",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Niko legal"}),r.jsx("h1",{children:c.title}),r.jsx("p",{children:c.intro}),r.jsx("small",{children:"Effective date: 1 January 2025"})]}),r.jsx("div",{className:"legal-copy",children:c.sections.map(([l,d])=>r.jsxs("section",{children:[r.jsx("h2",{children:l}),r.jsx("p",{children:d})]},l))})]}),r.jsx(Bt,{})]})}const Sp=[{key:"txt",label:"TXT",icon:"📄"},{key:"html",label:"HTML",icon:"🌐"},{key:"csv",label:"CSV",icon:"📊"},{key:"json",label:"JSON",icon:"{ }"}],qu=o=>typeof o!="number"||o<0||o>16777215?"":`#${o.toString(16).padStart(6,"0")}`,bn=o=>(o==null?void 0:o.url)||(o==null?void 0:o.proxy_url)||"",Qu=o=>/\.(?:png|jpe?g|gif|webp|bmp|svg)(?:[?#]|$)/i.test(o)||o.startsWith("data:image/"),Xu=o=>/\.(?:mp4|webm|mov|m4v|ogg)(?:[?#]|$)/i.test(o)||o.startsWith("data:video/");function Np(o){var l;const c=bn(o);return c?(l=o==null?void 0:o.content_type)!=null&&l.startsWith("video/")?!0:Xu(c):!1}const zu=new RegExp("(`[^`\\n]+`)|(\\[([^\\]\\n]+)\\]\\((https?:\\/\\/[^\\s)\\] ]+)\\))|(\\*\\*)|(?<!\\*)\\*(?!\\*)|(~~)","g"),Cp=/(https?:\/\/[^\s<>)]+)/g,Fu={bold:"**",italic:"*",strike:"~~"};function _p(o){const c=[];let l=0,d;const m=f=>{if(!f)return;const v=f.split(Cp);for(let P=0;P<v.length;P++){const w=v[P];w&&(P%2===1?c.push({type:"link",text:w,url:w}):c.push({type:"text",text:w}))}};for(zu.lastIndex=0;(d=zu.exec(o))!==null;)d.index>l&&m(o.slice(l,d.index)),d[1]!==void 0?c.push({type:"code",text:d[1].slice(1,-1)}):d[2]!==void 0?c.push({type:"link",text:d[3],url:d[4]}):d[5]!==void 0?c.push({type:"marker",fmt:"bold"}):d[6]!==void 0?c.push({type:"marker",fmt:"italic"}):d[7]!==void 0&&c.push({type:"marker",fmt:"strike"}),l=d.index+d[0].length;return l<o.length&&m(o.slice(l)),c}function Tp(o){const c=[],l=[],d=new Set,m=f=>{l.length>0?l[l.length-1].children.push(f):c.push(f)};for(const f of _p(o))if(f.type==="text")m({kind:"text",text:f.text});else if(f.type==="code")m({kind:"code",text:f.text});else if(f.type==="link")m({kind:"link",text:f.text,url:f.url});else if(f.type==="marker")if(d.has(f.fmt)){const v=l.map(F=>F.fmt).lastIndexOf(f.fmt),P=l.splice(v);P.forEach(F=>d.delete(F.fmt));const w={kind:"fmt",fmt:f.fmt,children:[...P[0].children]};for(const F of P.slice(1))w.children.push({kind:"text",text:Fu[F.fmt]??""}),w.children.push(...F.children);m(w)}else l.push({fmt:f.fmt,children:[]}),d.add(f.fmt);if(l.length>0)for(const f of l){m({kind:"text",text:Fu[f.fmt]??""});for(const v of f.children)m(v)}return c}const Yu=(o,c)=>o.map((l,d)=>{const m=`${c}-${d}`;switch(l.kind){case"text":return r.jsx("span",{children:l.text},m);case"code":return r.jsx("code",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:4,padding:"0 5px",color:"#f2b8c2",fontFamily:"monospace",fontSize:"0.92em"},children:l.text},m);case"link":return r.jsx("a",{href:l.url,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",textDecoration:"none"},onMouseEnter:f=>{f.currentTarget.style.textDecoration="underline"},onMouseLeave:f=>{f.currentTarget.style.textDecoration="none"},children:l.text},m);case"fmt":{const f={};return l.fmt==="bold"&&(f.fontWeight=700),l.fmt==="italic"&&(f.fontStyle="italic"),l.fmt==="strike"&&(f.textDecoration="line-through"),r.jsx("span",{style:f,children:Yu(l.children,m)},m)}}}),Js=o=>Yu(Tp(o),"md");function wn({text:o,muted:c}){const l=o.split(`
`),d=[];return l.forEach((m,f)=>{const v=m.trimStart(),w=f===l.length-1?null:r.jsx("br",{},`br${f}`);v.startsWith("-# ")?d.push(r.jsxs("span",{style:{color:c?"#6d737a":"#949ba4",fontSize:12},children:[Js(v.slice(3)),w]},f)):/^#{1,4}\s/.test(v)?d.push(r.jsxs("span",{style:{color:"#f2f3f5",fontWeight:700,fontSize:16},children:[Js(v),w]},f)):v.startsWith("> ")?d.push(r.jsxs("span",{style:{display:"inline-block",color:"#b5bac1",borderLeft:"3px solid #4e5058",paddingLeft:8},children:[Js(v.slice(2)),w]},f)):v.startsWith("```")?d.push(r.jsxs("pre",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:6,padding:"10px 12px",overflowX:"auto",whiteSpace:"pre-wrap",wordBreak:"break-word",fontFamily:"monospace",fontSize:12.5,color:"#dbdee1",margin:"2px 0"},children:[v.replace(/^```[a-zA-Z]*/,"").replace(/```$/,""),w]},f)):d.push(r.jsxs("span",{children:[Js(m),w]},f))}),r.jsx("span",{style:{whiteSpace:"pre-wrap",wordBreak:"break-word"},children:d})}function Ep({embed:o}){const c=qu(o.color)||"#5865f2",l=o.author,d=o.footer,m=bn(o.thumbnail),f=bn(o.image);return r.jsxs("div",{style:{display:"flex",gap:12,maxWidth:560,marginTop:8,background:"#2b2d31",border:"1px solid #3f4147",borderLeft:`4px solid ${c}`,borderRadius:6,padding:"10px 12px"},children:[r.jsxs("div",{style:{flex:1,minWidth:0},children:[(l==null?void 0:l.name)&&r.jsxs("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:4},children:[l.icon_url&&r.jsx("img",{src:l.icon_url||l.proxy_icon_url,alt:"",style:{width:18,height:18,borderRadius:"50%",verticalAlign:"-4px",marginRight:6}}),l.name]}),o.title&&r.jsx("div",{style:{color:"#00a8fc",fontWeight:600,margin:"2px 0 4px",fontSize:14},children:o.url?r.jsx("a",{href:o.url,target:"_blank",rel:"noopener noreferrer",style:{color:"inherit",textDecoration:"none"},children:r.jsx(wn,{text:o.title})}):r.jsx(wn,{text:o.title})}),o.description&&r.jsx("div",{style:{color:"#dbdee1",fontSize:13,lineHeight:1.5},children:r.jsx(wn,{text:o.description})}),o.fields&&o.fields.length>0&&r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:"6px 12px",marginTop:8},children:o.fields.map((v,P)=>r.jsxs("div",{style:{flex:v.inline?"0 1 45%":"1 1 100%",minWidth:0,marginBottom:4},children:[v.name&&r.jsx("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:2},children:r.jsx(wn,{text:v.name})}),v.value&&r.jsx("div",{style:{color:"#dbdee1",fontSize:13},children:r.jsx(wn,{text:v.value})})]},P))}),f&&r.jsx("a",{href:f,target:"_blank",rel:"noopener noreferrer",style:{display:"block",marginTop:8},children:r.jsx("img",{src:f,alt:"",style:{maxWidth:"100%",maxHeight:300,borderRadius:4,display:"block"},onError:v=>{v.currentTarget.style.display="none"}})}),((d==null?void 0:d.text)||o.timestamp)&&r.jsxs("div",{style:{display:"flex",alignItems:"center",gap:6,marginTop:6,color:"#949ba4",fontSize:11},children:[(d==null?void 0:d.icon_url)&&r.jsx("img",{src:d.icon_url||d.proxy_icon_url,alt:"",style:{width:16,height:16,borderRadius:"50%"}}),(d==null?void 0:d.text)&&r.jsx("span",{children:d.text}),o.timestamp&&r.jsx("span",{children:String(o.timestamp).replace("T"," ").replace("+00:00"," UTC")})]})]}),m&&r.jsx("a",{href:m,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:r.jsx("img",{src:m,alt:"",style:{width:80,height:80,borderRadius:6,objectFit:"cover"},onError:v=>{v.currentTarget.style.display="none"}})})]})}function Zs({component:o}){switch(o.type){case 17:{const c=qu(o.accent_color);return r.jsxs("div",{style:{display:"flex",overflow:"hidden",maxWidth:560,marginTop:8,background:"#2b2d31",border:`1px solid ${c||"#3f4147"}`,borderRadius:12},children:[c&&r.jsx("div",{style:{flex:"0 0 4px",background:c}}),r.jsx("div",{style:{flex:1,minWidth:0,padding:"6px 12px 8px"},children:(o.components||[]).map((l,d)=>r.jsx(Zs,{component:l},d))})]})}case 1:return r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,margin:"6px 0"},children:(o.components||[]).map((c,l)=>r.jsx(Zs,{component:c},l))});case 2:{const c=o.emoji,l=`${(c==null?void 0:c.name)??""}${o.label?` ${o.label}`:""}`.trim();return o.style===5&&!!o.url?r.jsx("a",{href:o.url,target:"_blank",rel:"noopener noreferrer",style:{display:"inline-block",padding:"3px 14px",background:"#5865f2",borderRadius:4,color:"#fff",fontSize:13,fontWeight:600,textDecoration:"none"},children:l||"Button"}):r.jsx("span",{style:{display:"inline-block",padding:"3px 14px",background:"#4e5058",borderRadius:4,color:o.disabled?"#8a8e96":"#f2f3f5",fontSize:13,cursor:o.disabled?"not-allowed":"default",opacity:o.disabled?.55:1},children:l||"Button"})}case 9:{const c=[...o.components||[]];return o.accessory&&c.push(o.accessory),r.jsx("div",{style:{display:"flex",alignItems:"center",gap:10,margin:"4px 0"},children:c.map((l,d)=>r.jsx(Zs,{component:l},d))})}case 10:return r.jsx("div",{style:{color:"#dbdee1",fontSize:14,lineHeight:1.5,margin:"4px 0",wordBreak:"break-word"},children:r.jsx(wn,{text:o.content||""})});case 18:return r.jsx("div",{style:{color:"#f2f3f5",fontWeight:700,textTransform:"uppercase",letterSpacing:"0.04em",fontSize:12,margin:"4px 0"},children:o.content});case 14:return r.jsx("div",{style:{margin:o.divider===!1?"6px 0":"9px 0",...o.divider===!1?{}:{borderTop:"1px solid #3f4147"}}});case 11:{const c=bn(o.media);return c?r.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:r.jsx("img",{src:c,alt:o.description||"",style:{width:40,height:40,borderRadius:"50%",objectFit:"cover",display:"block"},onError:l=>{l.currentTarget.style.display="none"}})}):null}case 12:{const l=(o.items||[]).filter(d=>bn(d.media));return l.length===0?null:r.jsx("div",{style:{display:"grid",gridTemplateColumns:`repeat(auto-fill, minmax(${Math.min(220,Math.max(140,Math.floor(560/Math.max(1,l.length))))}px, 1fr))`,gap:6,margin:"6px 0"},children:l.map((d,m)=>{const f=bn(d.media),v=d.description;return Np(d.media)?r.jsxs("figure",{style:{margin:0},children:[r.jsx("video",{src:f,controls:!0,preload:"metadata",style:{width:"100%",maxHeight:260,borderRadius:6,background:"#1e1f22"}}),v&&r.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:v})]},m):Qu(f)?r.jsxs("figure",{style:{margin:0},children:[r.jsx("a",{href:f,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:r.jsx("img",{src:f,alt:v||"",style:{width:"100%",maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:P=>{P.currentTarget.style.display="none"}})}),v&&r.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:v})]},m):r.jsxs("a",{href:f,target:"_blank",rel:"noopener noreferrer",style:{display:"flex",alignItems:"center",gap:6,padding:"6px 10px",background:"#383a40",borderRadius:6,color:"#dbdee1",fontSize:12,textDecoration:"none"},children:["📎 ",v||"Attachment"]},m)})})}case 13:{const c=bn(o.media)||o.url||"";return c?r.jsxs("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{display:"block",margin:"4px 0",color:"#00a8fc",fontSize:12.5,textDecoration:"none"},children:["📎 ",o.label||"Attachment"]}):null}default:return null}}function Mp({components:o}){return r.jsx(r.Fragment,{children:o.map((c,l)=>r.jsx(Zs,{component:c},l))})}function Pp({text:o}){return r.jsx(wn,{text:o})}function Lp({msg:o}){const c=!!(o.attachments&&o.attachments.length>0||o.embeds&&o.embeds.length>0||o.components&&o.components.length>0);return r.jsxs("div",{style:{padding:"10px 16px",borderBottom:"1px solid #2b2d31",fontSize:14,lineHeight:1.6},children:[r.jsxs("div",{style:{marginBottom:2},children:[r.jsx("span",{style:{color:"#949ba4",fontSize:11,fontFamily:"monospace"},children:o.timestamp})," ",r.jsx("span",{style:{color:"#f2f3f5",fontWeight:600},children:o.author})," ",r.jsxs("span",{style:{color:"#949ba4",fontSize:11},children:["(",o.author_id,")"]})]}),o.content?r.jsx("div",{style:{color:"#dbdee1"},children:r.jsx(Pp,{text:o.content})}):c?null:r.jsx("div",{style:{color:"#6d737a",fontStyle:"italic",fontSize:13},children:"Message content unavailable"}),o.attachments&&o.attachments.length>0&&r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:4},children:o.attachments.map((l,d)=>Xu(l)?r.jsx("video",{src:l,controls:!0,preload:"metadata",style:{maxWidth:360,maxHeight:260,borderRadius:6,background:"#1e1f22"}},d):Qu(l)?r.jsx("a",{href:l,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:r.jsx("img",{src:l,alt:"",style:{maxWidth:300,maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:m=>{const f=m.currentTarget;f.style.display="none"}})},d):r.jsx("a",{href:l,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",fontSize:12,textDecoration:"none"},children:"📎 Attachment"},d))}),o.embeds&&o.embeds.length>0&&r.jsx(r.Fragment,{children:o.embeds.map((l,d)=>r.jsx(Ep,{embed:l},d))}),o.components&&o.components.length>0&&r.jsx(Mp,{components:o.components})]})}function Rp({transcriptId:o}){const[c,l]=A.useState(null),[d,m]=A.useState(!0),[f,v]=A.useState("");A.useEffect(()=>{m(!0),v(""),fetch(`/api/transcript/${o}`).then(w=>{if(!w.ok)throw new Error("Transcript not found");return w.json()}).then(w=>{l(w),m(!1)}).catch(w=>{v(w.message||"Failed to load transcript"),m(!1)})},[o]);const P=w=>{window.open(`/api/transcript/${o}/download?format=${w}`,"_blank")};return d?r.jsx("div",{className:"page-main",children:r.jsx("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:r.jsx("div",{style:{color:"var(--muted)",fontSize:14},children:"Loading transcript…"})})}):f||!c?r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:[r.jsx("h2",{style:{marginBottom:12},children:"Transcript not found"}),r.jsx("p",{style:{color:"var(--muted)"},children:f||"This transcript doesn't exist or has been deleted."})]})}):r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{maxWidth:800},children:[r.jsx("div",{style:{background:"var(--surface)",border:"1px solid var(--line)",borderRadius:8,padding:24,marginBottom:20},children:r.jsxs("div",{style:{display:"flex",alignItems:"flex-start",justifyContent:"space-between",gap:16,flexWrap:"wrap"},children:[r.jsxs("div",{children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:8},children:"Ticket Transcript"}),r.jsxs("h1",{style:{fontSize:24,letterSpacing:"-0.04em",margin:0},children:["#",c.channel_name]}),r.jsxs("div",{style:{color:"var(--muted)",fontSize:13,marginTop:6},children:[c.category," · ",c.message_count," messages · ",c.created_at]})]}),r.jsx("div",{style:{display:"flex",gap:8,flexWrap:"wrap"},children:Sp.map(w=>r.jsxs("button",{className:"button button-small button-muted",onClick:()=>P(w.key),style:{minWidth:70},children:[r.jsx("span",{children:w.icon}),r.jsx("span",{children:w.label})]},w.key))})]})}),r.jsxs("div",{style:{background:"#1e1f22",border:"1px solid #3f4147",borderRadius:8,overflow:"hidden"},children:[c.messages.map((w,F)=>r.jsx(Lp,{msg:w},F)),c.messages.length===0&&r.jsx("div",{style:{padding:40,textAlign:"center",color:"#949ba4"},children:"No messages in this transcript."})]}),r.jsxs("div",{style:{marginTop:16,padding:"12px 0",textAlign:"center",color:"var(--dim)",fontSize:12},children:["Transcript ID: ",r.jsx("code",{style:{fontFamily:"monospace"},children:o})]})]})})}const na=[{slug:"economy-leveling-overhaul",title:"Economy Items, Leveling Cards & Subcommands",date:"2026-09-08",version:"2.8.0",tags:["economy","leveling","shop","image-cards"],summary:"The economy shop expanded with four new consumable items that affect gameplay — Rigged Coin, Streak Insurance, Double Down Token, and Lucky Horseshoe — plus daily streak milestone bonuses at 7, 14, 30, 60, and 90 days. The leveling system now renders rank cards and leaderboards as customizable image cards, and all leveling commands live under a single `/leveling` group with subcommands.",highlights:[{title:"New Shop Items",description:"Four new consumables: Rigged Coin (60/40 coinflip odds), Streak Insurance (protects daily streak for one missed day), Double Down Token (1.5x gambling payout), and Lucky Horseshoe (+10% work reward).",icon:"chart"},{title:"Leveling Image Cards",description:"Rank cards and the leaderboard now render as styled images with avatar, level, XP bar, and rank. Server admins can customize the card accent color and background gradient.",icon:"spark"},{title:"Leveling Subcommands",description:"All leveling commands reorganized under `/leveling` with `rank`, `leaderboard`, `panel`, and `config` subcommands. The leaderboard now has interactive pagination buttons.",icon:"settings"},{title:"Daily Streak Milestones",description:"Hitting 7, 14, 30, 60, or 90-day daily streaks now awards bonus items from the shop (Espresso Shots, Lockpicks, Lucky Charms, Rob Shields) along with a coin bonus.",icon:"utility"}],changes:[{category:"added",items:["Coinflip command with heads/tails call and double-or-nothing payout","Rigged Coin shop item — gives 60/40 coinflip odds for one use","Streak Insurance shop item — protects daily streak if you miss one day","Double Down Token shop item — next gambling win pays 1.5x","Lucky Horseshoe shop item — next work reward gets +10%","Daily streak milestone bonuses at 7/14/30/60/90 days with item rewards","Image card rendering for `/leveling rank` with customizable accent and background","Image card rendering for the leveling leaderboard","Inventory display as an image card in the shop command","Twemoji emoji rendering in economy card images","Pagination buttons (◀ ▶) on the leveling leaderboard","Card customization fields in the database: card_accent, card_bg_top, card_bg_bottom"]},{category:"improved",items:["Leveling commands restructured as `/leveling rank`, `leaderboard`, `panel`, `config` subcommands","Shop command visual layout with better font rendering on economy image cards","Crime and rob commands now check for gambling_boost effect for 1.5x payout","HTML download format for ticket transcripts","Dashboard UI refinements"]},{category:"fixed",items:["Command name conflicts between leveling and other cogs","Missing import in leveling cog after image card addition","Duplicate command alias in leveling system","Command name conflict in the gambling cog"]}],chart:{type:"bar",title:"New Shop Items & Their Effects",data:[{label:"Rigged Coin",value:3e3,color:"#c9a84c"},{label:"Streak Insurance",value:4e3,color:"#4a7fb5"},{label:"Double Down Token",value:5e3,color:"#d96545"},{label:"Lucky Horseshoe",value:2500,color:"#66866f"}]},commits:["41d86fb Expanded the gambling and economy system","bd6a09c Added image cards to the leveling system","5307bb1 Moved the leveling commands to the levels subcommand","dafd224 Added an image card to the inventory command","49fc83b Added emoji rendering to the shop command","0aca6ba Improved the shop command","30c9735 Added better font rendering to the economy system image cards","2b96835 Fixed a command name conflict","158ad8f Fixed a command name conflict in the gambling cog","d465598 Fixed a missing import","1f24ffb Fixed a duplicate command alias"]},{slug:"database-migration",title:"Database Migration to MongoDB",date:"2026-09-03",version:"2.7.0",tags:["database","mongodb","migration","infrastructure"],summary:"Every major system has been migrated from SQLite to MongoDB. The migration covered economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and the blacklist — with a custom interpreter that translates SQLite-style writes to MongoDB operations.",highlights:[{title:"Full MongoDB Migration",description:"Economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and blacklist now all store data in MongoDB instead of SQLite.",icon:"settings"},{title:"Slash Command Sync Safeguard",description:"A new check prevents redundant Discord API calls when all commands are already registered, reducing rate-limit issues on startup.",icon:"utility"},{title:"Proxy Integration",description:"A new proxy manager reduces downtime on shared hosting environments by routing API requests through a proxy layer.",icon:"shield"}],changes:[{category:"migrated",items:["Economy system — balances, banks, jobs, achievements, inventory","Leveling system — XP, levels, role rewards, card customization","Moderation system — warnings, mutes, automod config","Ticket system — panels, transcripts, support roles","Birthday system — dates, channels, messages","AFK system — status, timestamps","Sticky messages — content, channels","Blacklist — users, words, filters"]},{category:"added",items:["MongoDB interpreter that translates SQLite-style writes to proper MongoDB operations","Proxy manager for shared hosting reliability","Slash command sync safeguard to prevent redundant API calls","Context menu command support in the sync utility"]},{category:"fixed",items:["MongoDB interpreter not translating all SQLite write patterns correctly","Economy interest calculation after migration","Birthday system data persistence","Several database connection issues across various cogs","Leveling database initialization issue"]}],chart:{type:"pie",title:"Systems Migrated to MongoDB",data:[{label:"Economy",value:1,color:"#d96545"},{label:"Leveling",value:1,color:"#66866f"},{label:"Moderation",value:1,color:"#4a7fb5"},{label:"Tickets",value:1,color:"#c9a84c"},{label:"Birthdays",value:1,color:"#b07cc6"},{label:"AFK",value:1,color:"#e0976e"},{label:"Sticky Msgs",value:1,color:"#7ca898"},{label:"Blacklist",value:1,color:"#8c918e"}]},commits:["c07f9b1 Fixed the MongoDB interpreter to properly translate all SQLite database writes","0d3aca5 Migrated the blacklist to the main database","954ebac Migrated the birthday system to the main database","5013d54 Migrated the warns and mutes to use the main database","f29c217 Migrated the afk system to the main database","5732b48 Migrated the sticky messages to use the main database","b0524f1 Migrated the ticket system to the main database","70e6d7a Fixed the sync util to support context commands and slash groups","2c01817 Added a safeguard to prevent slash command syncs when all commands are already present","121afcf Added a proxy integration to reduce downtime on shared hosting","9f2f1fd Fixed several database issues across various cogs"]},{slug:"ticket-system-transcripts",title:"Ticket Transcripts & VoiceMaster",date:"2026-09-03",version:"2.6.0",tags:["tickets","transcripts","voicemaster"],summary:"The ticket system gained a web-based transcript viewer that renders ticket conversations as styled HTML pages. The VoiceMaster was also improved with better reliability and database usage. Ticket transcripts can now be downloaded as HTML or viewed online.",highlights:[{title:"Web Transcript Viewer",description:"Ticket transcripts are now rendered as styled HTML pages that can be viewed online. The HTML download format was also improved for better readability.",icon:"doc"},{title:"VoiceMaster Reliability",description:"The VoiceMaster (temporary voice channels) was improved with better database usage and reliability fixes.",icon:"utility"},{title:"Donation Dashboard Page",description:"A new customization page in the dashboard lets server admins configure donation settings without using commands.",icon:"settings"}],changes:[{category:"added",items:["Web-based ticket transcript viewer with styled HTML output","Ticket transcript database table for storing transcripts online","Dashboard customization page for donation system settings"]},{category:"improved",items:["HTML download format for ticket transcripts","VoiceMaster reliability and database usage patterns","Ticket system persistence and data handling"]},{category:"fixed",items:["Ticket transcript pages rendering incorrectly","Ticket system data loss on restart","Ticket transcript generation issues","Ticket transcript page display bugs"]}],commits:["e953321 Added a new web transcript feature to the ticket system","aa0b73b Improved the donation system and added a customization page to the dashboard","3255385 Improved the html download format for the ticket transcripts","45f1fb0 Fixed the ticket system persistence","ef4e057 Added the ticket system database migrations","d4e0bc8 Fixed the ticket transcripts","4bf5e04 Fixed an issue with the ticket transcript pages","e8dbcb0 Improved the VoiceMaster reliability and improved the database usage"]},{slug:"roleplay-music-status",title:"Roleplay, Music & Status Rotation",date:"2026-09-05",version:"2.5.0",tags:["roleplay","music","status","social"],summary:"The roleplay cog was completely rewritten to use nekos.best API GIFs with CV2 layout messages and a persistent 'hug back' button. The music cog was restructured with a ghost queue feature and fixed autoplay/Spotify playback. A status message rotation system was added with a configurable timer.",highlights:[{title:"Roleplay Rewrite",description:"The roleplay cog now fetches SFW reaction GIFs from nekos.best, renders them in styled CV2 containers, and includes a 'hug back' button that persists across restarts. A single user context menu replaces individual action menus to stay under Discord's 15-command cap.",icon:"users"},{title:"Music Ghost Queue",description:"A new ghost queue feature lets songs be queued even when nothing is currently playing. Autoplay and Spotify playback were also fixed.",icon:"utility"},{title:"Status Rotation",description:"The bot now rotates through configurable status messages on a timer (default 30s interval), with activity types and a VR device presence.",icon:"spark"}],changes:[{category:"added",items:["Status message rotation with configurable interval and activity types","Persistent status panel command for the support server (owner only)","Roleplay block feature to prevent specific users from being targeted","Ghost queue feature — queue songs even when nothing is playing","User context menu for roleplay actions (replaces per-action menus)","YouTube channel name validation for notification system"]},{category:"improved",items:["Roleplay cog complete rewrite — nekos.best GIFs, CV2 layouts, persistent buttons","Social media notification emoji formatting (Bluesky, Reddit, TikTok, Twitch icons)","Music node connection system and autoplay reliability","Spotify playback quality","Music cog restructured with better error handling"]},{category:"fixed",items:["Status rotator startup errors and activity conflicts","on_ready event error handling and reliability","Lavalink connection bug","Roleplay prefix command handling","Bluesky and Reddit notification delivery issues"]}],chart:{type:"bar",title:"Files Changed per Feature Area",data:[{label:"Roleplay",value:3,color:"#d96545"},{label:"Music",value:4,color:"#4a7fb5"},{label:"Status",value:3,color:"#66866f"},{label:"Social",value:2,color:"#c9a84c"}]},commits:["0c58178 Redesigned the roleplay cog","6c4ee09 Fixed the roleplay prefix commands","f1f8591 Added a roleplay block feature","e01e3e4 Added status message rotation","5e63e1d Added a persistent status panel","ae7501a Restructured the music cog","526813e Added a new ghost queue feature to the music cog","6524da1 Improved the music node connection system, fixed the autoplay, and fixed the Spotify playback","4264677 Fixed a lavalink connection bug","d62ead8 Improved the social media notification system's emojis","0f0305d Improved the social media notification formatting","42069d4 Added proper channel name validation to the YouTube notification system"]},{slug:"moderation-logging-dashboard",title:"Logging, Moderation & Documentation",date:"2026-09-07",version:"2.4.0",tags:["logging","moderation","documentation","dashboard"],summary:"Logging got two major improvements: deleted message logs now show image attachments in a MediaGallery component, and the Member category now tracks avatar changes using a Section with Thumbnail accessory. The documentation page was fully rebuilt with search, filters, and a card-based layout.",highlights:[{title:"Image Attachments in Logs",description:"Deleted message logs now render attached images in a MediaGallery component inside the log container, so moderators can see what was posted without leaving Discord.",icon:"chart"},{title:"Avatar Change Tracking",description:"The Member logging category now detects avatar changes (global and server avatars) and displays them in a Section with a Thumbnail accessory showing the new avatar.",icon:"users"},{title:"Documentation Redesign",description:"The documentation page was rebuilt from scratch with a search bar, category filters, tag cloud, card-based layout, and individual article pages with table of contents.",icon:"doc"}],changes:[{category:"added",items:["Image attachments rendered in deleted message logs via MediaGallery","Avatar change detection in Member logging with Section + Thumbnail display","Startup economy cache that loads all users into memory for accurate leaderboards","Error handler for role menu post buttons","Full-text search with result highlighting in documentation","Category filters and tag cloud in documentation","Individual documentation article pages with table of contents"]},{category:"improved",items:["Logging system now supports media_urls, thumbnail_url, and files parameters","Commands page expanded with better organization","Dashboard UI refinements","Economy interest feature — skips malformed records with non-integer user IDs"]},{category:"fixed",items:["Logging command issues","Documentation command references","Status device detection issue","Status rotator conflicts between multiple status types","on_ready event reliability with proper error handling"]}],commits:["722a34f Added avatar updates to the logging cogs Member logs","1d82ea1 Moved file attachments inside the main log message for the deleted message logs","358d537 Added a startup economy cache to fix the leaderboard","566e0c4 Improved the dashboard","132bcbb Fully redesigned the documentation page","4f7a89a Improved the commands page","6d953b6 Fixed the logging command","a202687 Fixed some documentation issues","49d22ad Fixed the documentation command references","52de287 Added an error handler to the post role menu button"]},{slug:"website-launch-donation",title:"Website, Donation System & API",date:"2026-09-02",version:"2.3.0",tags:["website","donations","api"],summary:"The public website and documentation portal launched with a React + Vite frontend, documentation center with search, and a commands reference page. The donation system gained a dashboard customization page, and the Flask API backend was fixed to use proper database calls.",highlights:[{title:"Public Website",description:"A complete public website built with React and Vite featuring a landing page, documentation center, command reference, dashboard, and legal pages.",icon:"spark"},{title:"Documentation Center",description:"The documentation page was redesigned with a card-based layout, individual article pages, and a modern visual design matching the bot's aesthetic.",icon:"doc"},{title:"Donation Dashboard",description:"Server admins can now configure donation settings through a new dashboard page instead of relying solely on commands.",icon:"settings"}],changes:[{category:"added",items:["Public website with landing page, documentation center, and command reference","Donation system customization page in the dashboard","Ticket transcript viewer web page","Donate page with Oxapay integration"]},{category:"improved",items:["Flask API to use proper database calls instead of direct SQLite access","Website commands page with expanded details","Database layer reliability for production"]},{category:"fixed",items:["Flask API database call issues","Several database-related bugs across cogs","node_modules folder accidentally committed to repository"]}],commits:["132bcbb Fully redesigned the documentation page","aa0b73b Improved the donation system and added a customization page to the dashboard","bd5e3be Expanded the website's commands page","e266644 Fixed the flask API to use the proper database calls","e99ed47 Fixed several database related issues","c783514 Minor API fixes and improvements","0df4478 Added the node_modules folder to the gitignore file"]}];function Ap(o){return na.find(c=>c.slug===o)}function Dp(){const o=new Set;return na.forEach(c=>c.tags.forEach(l=>o.add(l))),Array.from(o).sort()}function Ip(){const[o,c]=A.useState(""),l=Dp(),d=o?na.filter(m=>m.tags.includes(o)):na;return r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:"home"}),r.jsxs("main",{className:"shell page-main changelog-page",children:[r.jsxs("div",{className:"changelog-hero",children:[r.jsxs("div",{className:"eyebrow",children:[r.jsx("span",{className:"status-dot"})," What's new"]}),r.jsxs("h1",{className:"changelog-title",children:["Changelog",r.jsx("br",{}),r.jsx("span",{className:"title-accent",children:"& updates"})]}),r.jsx("p",{className:"changelog-subtitle",children:"A record of every improvement, fix, and new feature added to Niko. Grouped by release for clarity."})]}),r.jsxs("div",{className:"changelog-tags",children:[r.jsx("button",{className:`changelog-tag-btn ${o===""?"active":""}`,onClick:()=>c(""),children:"All"}),l.slice(0,12).map(m=>r.jsx("button",{className:`changelog-tag-btn ${o===m?"active":""}`,onClick:()=>c(m),children:m},m))]}),r.jsx("div",{className:"changelog-timeline",children:d.map((m,f)=>r.jsxs("article",{className:"changelog-entry",children:[r.jsxs("div",{className:"changelog-entry-date-col",children:[r.jsx("div",{className:"changelog-date-dot"}),f<d.length-1&&r.jsx("div",{className:"changelog-date-line"})]}),r.jsxs("div",{className:"changelog-entry-card",children:[r.jsxs("div",{className:"changelog-entry-header",children:[r.jsxs("div",{className:"changelog-entry-meta",children:[r.jsx("time",{className:"changelog-entry-date",children:new Date(m.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),m.version&&r.jsxs("span",{className:"changelog-version",children:["v",m.version]})]}),r.jsx("h2",{className:"changelog-entry-title",children:m.title}),r.jsx("p",{className:"changelog-entry-summary",children:m.summary})]}),r.jsx("div",{className:"changelog-entry-highlights",children:m.highlights.slice(0,2).map(v=>r.jsxs("div",{className:"changelog-highlight-mini",children:[r.jsx("span",{className:"highlight-mini-icon",children:r.jsx(q,{name:v.icon,size:16})}),r.jsxs("div",{children:[r.jsx("strong",{children:v.title}),r.jsxs("p",{children:[v.description.slice(0,120),"..."]})]})]},v.title))}),r.jsx("div",{className:"changelog-entry-tags",children:m.tags.map(v=>r.jsx("span",{className:"changelog-tag",children:v},v))}),r.jsxs("button",{className:"changelog-read-more",onClick:()=>{ie(`/changelog/${m.slug}`)},children:["Read full release notes ",r.jsx(q,{name:"arrow",size:14})]})]})]},m.slug))}),d.length===0&&r.jsxs("div",{className:"changelog-empty",children:[r.jsx(q,{name:"doc",size:40}),r.jsx("p",{children:"No changelog entries match this filter."})]})]}),r.jsx(Bt,{})]})}function zp({slug:o}){const c=Ap(o);return c?r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:"home"}),r.jsxs("main",{className:"shell page-main changelog-page changelog-detail",children:[r.jsx("div",{className:"changelog-back",children:r.jsxs("button",{onClick:()=>ie("/changelog"),className:"back-button",children:[r.jsx(q,{name:"arrow",size:16}),"Back to Changelog"]})}),r.jsxs("header",{className:"changelog-detail-header",children:[r.jsxs("div",{className:"changelog-detail-meta",children:[r.jsx("time",{children:new Date(c.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),c.version&&r.jsxs("span",{className:"changelog-version",children:["v",c.version]})]}),r.jsx("h1",{children:c.title}),r.jsx("p",{className:"changelog-detail-summary",children:c.summary}),r.jsx("div",{className:"changelog-detail-tags",children:c.tags.map(l=>r.jsx("span",{className:"changelog-tag",children:l},l))})]}),r.jsxs("section",{className:"changelog-highlights-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"Highlights"}),r.jsx("div",{className:"changelog-highlights-grid",children:c.highlights.map(l=>r.jsxs("div",{className:"changelog-highlight-card",children:[r.jsx("span",{className:"highlight-icon",children:r.jsx(q,{name:l.icon,size:22})}),r.jsx("h3",{children:l.title}),r.jsx("p",{children:l.description})]},l.title))})]}),c.chart&&r.jsx(Fp,{chart:c.chart}),r.jsxs("section",{className:"changelog-changes-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"All Changes"}),r.jsx("div",{className:"changelog-changes-grid",children:c.changes.map(l=>r.jsxs("div",{className:`changelog-change-group changelog-change-${l.category}`,children:[r.jsx("h3",{className:"change-group-title",children:r.jsx("span",{className:`change-badge change-badge-${l.category}`,children:l.category})}),r.jsx("ul",{children:l.items.map((d,m)=>r.jsx("li",{children:d},m))})]},l.category))})]}),c.commits.length>0&&r.jsxs("section",{className:"changelog-commits-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"Commits"}),r.jsx("div",{className:"changelog-commits-list",children:c.commits.map(l=>{const[d,...m]=l.split(" ");return r.jsxs("div",{className:"changelog-commit",children:[r.jsx("code",{className:"commit-hash",children:d.slice(0,7)}),r.jsx("span",{className:"commit-msg",children:m.join(" ")})]},d)})})]}),r.jsx("nav",{className:"changelog-detail-nav",children:r.jsxs("button",{onClick:()=>ie("/changelog"),children:[r.jsx(q,{name:"arrow",size:14}),"All releases"]})})]}),r.jsx(Bt,{})]}):r.jsxs(r.Fragment,{children:[r.jsx(tt,{page:"home"}),r.jsx("main",{className:"shell page-main changelog-page",children:r.jsxs("div",{className:"changelog-not-found",children:[r.jsx(q,{name:"doc",size:48}),r.jsx("h1",{children:"Entry Not Found"}),r.jsxs("p",{children:[`We couldn't find a changelog entry for "`,o,'".']}),r.jsx("button",{onClick:()=>ie("/changelog"),children:"View all changelog entries"})]})}),r.jsx(Bt,{})]})}function Fp({chart:o}){return r.jsxs("section",{className:"changelog-chart-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:o.title}),r.jsxs("div",{className:"changelog-chart-container",children:[o.type==="bar"&&r.jsx(Bu,{chart:o}),o.type==="pie"&&r.jsx(Bp,{chart:o}),o.type==="comparison"&&r.jsx(Op,{chart:o}),o.type==="line"&&r.jsx(Bu,{chart:o})]})]})}function Bu({chart:o}){const c=Math.max(...o.data.map(l=>l.value));return r.jsx("div",{className:"chart-bar",children:o.data.map(l=>r.jsxs("div",{className:"chart-bar-row",children:[r.jsx("span",{className:"chart-bar-label",children:l.label}),r.jsxs("div",{className:"chart-bar-track",children:[r.jsx("div",{className:"chart-bar-fill",style:{width:`${l.value/c*100}%`,background:l.color||"var(--accent)"}}),r.jsx("span",{className:"chart-bar-value",children:l.value})]})]},l.label))})}function Bp({chart:o}){const c=o.data.reduce((f,v)=>f+v.value,0);let l=0;const m=o.data.map(f=>{const v=l/c*360;l+=f.value;const P=l/c*360;return{...f,start:v,end:P}}).map(f=>{const v=f.start/360*100,P=f.end/360*100;return`${f.color||"#d96545"} ${v}% ${P}%`}).join(", ");return r.jsxs("div",{className:"chart-pie-wrapper",children:[r.jsx("div",{className:"chart-pie",style:{background:`conic-gradient(${m})`}}),r.jsx("div",{className:"chart-pie-legend",children:o.data.map(f=>r.jsxs("div",{className:"chart-legend-item",children:[r.jsx("span",{className:"chart-legend-dot",style:{background:f.color||"var(--accent)"}}),r.jsx("span",{className:"chart-legend-label",children:f.label})]},f.label))})]})}function Op({chart:o}){const c=Math.ceil(o.data.length/2),l=o.data.slice(0,c),d=o.data.slice(c),m=Math.max(...o.data.map(f=>f.value));return r.jsxs("div",{className:"chart-comparison",children:[r.jsxs("div",{className:"chart-comparison-col",children:[r.jsx("h4",{className:"comparison-label comparison-before",children:"Before"}),l.map(f=>r.jsxs("div",{className:"chart-bar-row",children:[r.jsx("span",{className:"chart-bar-label",children:f.label}),r.jsxs("div",{className:"chart-bar-track",children:[r.jsx("div",{className:"chart-bar-fill",style:{width:`${f.value/m*100}%`,background:f.color||"var(--accent)"}}),r.jsx("span",{className:"chart-bar-value",children:f.value})]})]},f.label))]}),r.jsx("div",{className:"chart-comparison-divider",children:r.jsx(q,{name:"arrow",size:20})}),r.jsxs("div",{className:"chart-comparison-col",children:[r.jsx("h4",{className:"comparison-label comparison-after",children:"After"}),d.map(f=>r.jsxs("div",{className:"chart-bar-row",children:[r.jsx("span",{className:"chart-bar-label",children:f.label}),r.jsxs("div",{className:"chart-bar-track",children:[r.jsx("div",{className:"chart-bar-fill",style:{width:`${f.value/m*100}%`,background:f.color||"var(--accent)"}}),r.jsx("span",{className:"chart-bar-value",children:f.value})]})]},f.label))]})]})}function Wp(){const[o,c]=A.useState(Su);if(A.useEffect(()=>{const l=()=>c(Su());return window.addEventListener("popstate",l),()=>window.removeEventListener("popstate",l)},[]),o==="commands")return r.jsx(Hh,{});if(o==="docs-detail"){const l=window.location.pathname.split("/"),d=l[l.length-1];return r.jsx(yp,{slug:d})}if(o==="docs")return r.jsx(xp,{});if(o==="dashboard")return r.jsx(dp,{});if(o==="privacy")return r.jsx(mo,{type:"privacy"});if(o==="terms")return r.jsx(mo,{type:"terms"});if(o==="community")return r.jsx(mo,{type:"community"});if(o==="donate")return r.jsx(jp,{});if(o==="transcript"){const d=window.location.pathname.split("/").filter(Boolean)[1]||"";return r.jsx(Rp,{transcriptId:d})}if(o==="changelog")return r.jsx(Ip,{});if(o==="changelog-detail"){const l=window.location.pathname.split("/"),d=l[l.length-1];return r.jsx(zp,{slug:d})}return r.jsx(kp,{})}sh.createRoot(document.getElementById("root")).render(r.jsx(A.StrictMode,{children:r.jsx(Wp,{})}));
