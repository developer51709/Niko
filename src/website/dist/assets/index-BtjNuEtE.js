var nh=Object.defineProperty;var rh=(i,l,c)=>l in i?nh(i,l,{enumerable:!0,configurable:!0,writable:!0,value:c}):i[l]=c;var vu=(i,l,c)=>rh(i,typeof l!="symbol"?l+"":l,c);(function(){const l=document.createElement("link").relList;if(l&&l.supports&&l.supports("modulepreload"))return;for(const m of document.querySelectorAll('link[rel="modulepreload"]'))d(m);new MutationObserver(m=>{for(const p of m)if(p.type==="childList")for(const g of p.addedNodes)g.tagName==="LINK"&&g.rel==="modulepreload"&&d(g)}).observe(document,{childList:!0,subtree:!0});function c(m){const p={};return m.integrity&&(p.integrity=m.integrity),m.referrerPolicy&&(p.referrerPolicy=m.referrerPolicy),m.crossOrigin==="use-credentials"?p.credentials="include":m.crossOrigin==="anonymous"?p.credentials="omit":p.credentials="same-origin",p}function d(m){if(m.ep)return;m.ep=!0;const p=c(m);fetch(m.href,p)}})();var no={exports:{}},Ir={},ro={exports:{}},ie={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var yu;function sh(){if(yu)return ie;yu=1;var i=Symbol.for("react.element"),l=Symbol.for("react.portal"),c=Symbol.for("react.fragment"),d=Symbol.for("react.strict_mode"),m=Symbol.for("react.profiler"),p=Symbol.for("react.provider"),g=Symbol.for("react.context"),E=Symbol.for("react.forward_ref"),b=Symbol.for("react.suspense"),z=Symbol.for("react.memo"),C=Symbol.for("react.lazy"),N=Symbol.iterator;function M(y){return y===null||typeof y!="object"?null:(y=N&&y[N]||y["@@iterator"],typeof y=="function"?y:null)}var I={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},R=Object.assign,_={};function j(y,L,ae){this.props=y,this.context=L,this.refs=_,this.updater=ae||I}j.prototype.isReactComponent={},j.prototype.setState=function(y,L){if(typeof y!="object"&&typeof y!="function"&&y!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,y,L,"setState")},j.prototype.forceUpdate=function(y){this.updater.enqueueForceUpdate(this,y,"forceUpdate")};function J(){}J.prototype=j.prototype;function S(y,L,ae){this.props=y,this.context=L,this.refs=_,this.updater=ae||I}var V=S.prototype=new J;V.constructor=S,R(V,j.prototype),V.isPureReactComponent=!0;var ee=Array.isArray,se=Object.prototype.hasOwnProperty,B={current:null},Q={key:!0,ref:!0,__self:!0,__source:!0};function pe(y,L,ae){var oe,ue={},de=null,ve=null;if(L!=null)for(oe in L.ref!==void 0&&(ve=L.ref),L.key!==void 0&&(de=""+L.key),L)se.call(L,oe)&&!Q.hasOwnProperty(oe)&&(ue[oe]=L[oe]);var fe=arguments.length-2;if(fe===1)ue.children=ae;else if(1<fe){for(var we=Array(fe),ot=0;ot<fe;ot++)we[ot]=arguments[ot+2];ue.children=we}if(y&&y.defaultProps)for(oe in fe=y.defaultProps,fe)ue[oe]===void 0&&(ue[oe]=fe[oe]);return{$$typeof:i,type:y,key:de,ref:ve,props:ue,_owner:B.current}}function ne(y,L){return{$$typeof:i,type:y.type,key:L,ref:y.ref,props:y.props,_owner:y._owner}}function je(y){return typeof y=="object"&&y!==null&&y.$$typeof===i}function Te(y){var L={"=":"=0",":":"=2"};return"$"+y.replace(/[=:]/g,function(ae){return L[ae]})}var Se=/\/+/g;function re(y,L){return typeof y=="object"&&y!==null&&y.key!=null?Te(""+y.key):L.toString(36)}function Le(y,L,ae,oe,ue){var de=typeof y;(de==="undefined"||de==="boolean")&&(y=null);var ve=!1;if(y===null)ve=!0;else switch(de){case"string":case"number":ve=!0;break;case"object":switch(y.$$typeof){case i:case l:ve=!0}}if(ve)return ve=y,ue=ue(ve),y=oe===""?"."+re(ve,0):oe,ee(ue)?(ae="",y!=null&&(ae=y.replace(Se,"$&/")+"/"),Le(ue,L,ae,"",function(ot){return ot})):ue!=null&&(je(ue)&&(ue=ne(ue,ae+(!ue.key||ve&&ve.key===ue.key?"":(""+ue.key).replace(Se,"$&/")+"/")+y)),L.push(ue)),1;if(ve=0,oe=oe===""?".":oe+":",ee(y))for(var fe=0;fe<y.length;fe++){de=y[fe];var we=oe+re(de,fe);ve+=Le(de,L,ae,we,ue)}else if(we=M(y),typeof we=="function")for(y=we.call(y),fe=0;!(de=y.next()).done;)de=de.value,we=oe+re(de,fe++),ve+=Le(de,L,ae,we,ue);else if(de==="object")throw L=String(y),Error("Objects are not valid as a React child (found: "+(L==="[object Object]"?"object with keys {"+Object.keys(y).join(", ")+"}":L)+"). If you meant to render a collection of children, use an array instead.");return ve}function He(y,L,ae){if(y==null)return y;var oe=[],ue=0;return Le(y,oe,"","",function(de){return L.call(ae,de,ue++)}),oe}function Fe(y){if(y._status===-1){var L=y._result;L=L(),L.then(function(ae){(y._status===0||y._status===-1)&&(y._status=1,y._result=ae)},function(ae){(y._status===0||y._status===-1)&&(y._status=2,y._result=ae)}),y._status===-1&&(y._status=0,y._result=L)}if(y._status===1)return y._result.default;throw y._result}var he={current:null},O={transition:null},Z={ReactCurrentDispatcher:he,ReactCurrentBatchConfig:O,ReactCurrentOwner:B};function $(){throw Error("act(...) is not supported in production builds of React.")}return ie.Children={map:He,forEach:function(y,L,ae){He(y,function(){L.apply(this,arguments)},ae)},count:function(y){var L=0;return He(y,function(){L++}),L},toArray:function(y){return He(y,function(L){return L})||[]},only:function(y){if(!je(y))throw Error("React.Children.only expected to receive a single React element child.");return y}},ie.Component=j,ie.Fragment=c,ie.Profiler=m,ie.PureComponent=S,ie.StrictMode=d,ie.Suspense=b,ie.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Z,ie.act=$,ie.cloneElement=function(y,L,ae){if(y==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+y+".");var oe=R({},y.props),ue=y.key,de=y.ref,ve=y._owner;if(L!=null){if(L.ref!==void 0&&(de=L.ref,ve=B.current),L.key!==void 0&&(ue=""+L.key),y.type&&y.type.defaultProps)var fe=y.type.defaultProps;for(we in L)se.call(L,we)&&!Q.hasOwnProperty(we)&&(oe[we]=L[we]===void 0&&fe!==void 0?fe[we]:L[we])}var we=arguments.length-2;if(we===1)oe.children=ae;else if(1<we){fe=Array(we);for(var ot=0;ot<we;ot++)fe[ot]=arguments[ot+2];oe.children=fe}return{$$typeof:i,type:y.type,key:ue,ref:de,props:oe,_owner:ve}},ie.createContext=function(y){return y={$$typeof:g,_currentValue:y,_currentValue2:y,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},y.Provider={$$typeof:p,_context:y},y.Consumer=y},ie.createElement=pe,ie.createFactory=function(y){var L=pe.bind(null,y);return L.type=y,L},ie.createRef=function(){return{current:null}},ie.forwardRef=function(y){return{$$typeof:E,render:y}},ie.isValidElement=je,ie.lazy=function(y){return{$$typeof:C,_payload:{_status:-1,_result:y},_init:Fe}},ie.memo=function(y,L){return{$$typeof:z,type:y,compare:L===void 0?null:L}},ie.startTransition=function(y){var L=O.transition;O.transition={};try{y()}finally{O.transition=L}},ie.unstable_act=$,ie.useCallback=function(y,L){return he.current.useCallback(y,L)},ie.useContext=function(y){return he.current.useContext(y)},ie.useDebugValue=function(){},ie.useDeferredValue=function(y){return he.current.useDeferredValue(y)},ie.useEffect=function(y,L){return he.current.useEffect(y,L)},ie.useId=function(){return he.current.useId()},ie.useImperativeHandle=function(y,L,ae){return he.current.useImperativeHandle(y,L,ae)},ie.useInsertionEffect=function(y,L){return he.current.useInsertionEffect(y,L)},ie.useLayoutEffect=function(y,L){return he.current.useLayoutEffect(y,L)},ie.useMemo=function(y,L){return he.current.useMemo(y,L)},ie.useReducer=function(y,L,ae){return he.current.useReducer(y,L,ae)},ie.useRef=function(y){return he.current.useRef(y)},ie.useState=function(y){return he.current.useState(y)},ie.useSyncExternalStore=function(y,L,ae){return he.current.useSyncExternalStore(y,L,ae)},ie.useTransition=function(){return he.current.useTransition()},ie.version="18.3.1",ie}var xu;function wo(){return xu||(xu=1,ro.exports=sh()),ro.exports}/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var ku;function ah(){if(ku)return Ir;ku=1;var i=wo(),l=Symbol.for("react.element"),c=Symbol.for("react.fragment"),d=Object.prototype.hasOwnProperty,m=i.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,p={key:!0,ref:!0,__self:!0,__source:!0};function g(E,b,z){var C,N={},M=null,I=null;z!==void 0&&(M=""+z),b.key!==void 0&&(M=""+b.key),b.ref!==void 0&&(I=b.ref);for(C in b)d.call(b,C)&&!p.hasOwnProperty(C)&&(N[C]=b[C]);if(E&&E.defaultProps)for(C in b=E.defaultProps,b)N[C]===void 0&&(N[C]=b[C]);return{$$typeof:l,type:E,key:M,ref:I,props:N,_owner:m.current}}return Ir.Fragment=c,Ir.jsx=g,Ir.jsxs=g,Ir}var wu;function ih(){return wu||(wu=1,no.exports=ah()),no.exports}var n=ih(),T=wo(),Ks={},so={exports:{}},at={},ao={exports:{}},io={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var bu;function oh(){return bu||(bu=1,(function(i){function l(O,Z){var $=O.length;O.push(Z);e:for(;0<$;){var y=$-1>>>1,L=O[y];if(0<m(L,Z))O[y]=Z,O[$]=L,$=y;else break e}}function c(O){return O.length===0?null:O[0]}function d(O){if(O.length===0)return null;var Z=O[0],$=O.pop();if($!==Z){O[0]=$;e:for(var y=0,L=O.length,ae=L>>>1;y<ae;){var oe=2*(y+1)-1,ue=O[oe],de=oe+1,ve=O[de];if(0>m(ue,$))de<L&&0>m(ve,ue)?(O[y]=ve,O[de]=$,y=de):(O[y]=ue,O[oe]=$,y=oe);else if(de<L&&0>m(ve,$))O[y]=ve,O[de]=$,y=de;else break e}}return Z}function m(O,Z){var $=O.sortIndex-Z.sortIndex;return $!==0?$:O.id-Z.id}if(typeof performance=="object"&&typeof performance.now=="function"){var p=performance;i.unstable_now=function(){return p.now()}}else{var g=Date,E=g.now();i.unstable_now=function(){return g.now()-E}}var b=[],z=[],C=1,N=null,M=3,I=!1,R=!1,_=!1,j=typeof setTimeout=="function"?setTimeout:null,J=typeof clearTimeout=="function"?clearTimeout:null,S=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function V(O){for(var Z=c(z);Z!==null;){if(Z.callback===null)d(z);else if(Z.startTime<=O)d(z),Z.sortIndex=Z.expirationTime,l(b,Z);else break;Z=c(z)}}function ee(O){if(_=!1,V(O),!R)if(c(b)!==null)R=!0,Fe(se);else{var Z=c(z);Z!==null&&he(ee,Z.startTime-O)}}function se(O,Z){R=!1,_&&(_=!1,J(pe),pe=-1),I=!0;var $=M;try{for(V(Z),N=c(b);N!==null&&(!(N.expirationTime>Z)||O&&!Te());){var y=N.callback;if(typeof y=="function"){N.callback=null,M=N.priorityLevel;var L=y(N.expirationTime<=Z);Z=i.unstable_now(),typeof L=="function"?N.callback=L:N===c(b)&&d(b),V(Z)}else d(b);N=c(b)}if(N!==null)var ae=!0;else{var oe=c(z);oe!==null&&he(ee,oe.startTime-Z),ae=!1}return ae}finally{N=null,M=$,I=!1}}var B=!1,Q=null,pe=-1,ne=5,je=-1;function Te(){return!(i.unstable_now()-je<ne)}function Se(){if(Q!==null){var O=i.unstable_now();je=O;var Z=!0;try{Z=Q(!0,O)}finally{Z?re():(B=!1,Q=null)}}else B=!1}var re;if(typeof S=="function")re=function(){S(Se)};else if(typeof MessageChannel<"u"){var Le=new MessageChannel,He=Le.port2;Le.port1.onmessage=Se,re=function(){He.postMessage(null)}}else re=function(){j(Se,0)};function Fe(O){Q=O,B||(B=!0,re())}function he(O,Z){pe=j(function(){O(i.unstable_now())},Z)}i.unstable_IdlePriority=5,i.unstable_ImmediatePriority=1,i.unstable_LowPriority=4,i.unstable_NormalPriority=3,i.unstable_Profiling=null,i.unstable_UserBlockingPriority=2,i.unstable_cancelCallback=function(O){O.callback=null},i.unstable_continueExecution=function(){R||I||(R=!0,Fe(se))},i.unstable_forceFrameRate=function(O){0>O||125<O?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):ne=0<O?Math.floor(1e3/O):5},i.unstable_getCurrentPriorityLevel=function(){return M},i.unstable_getFirstCallbackNode=function(){return c(b)},i.unstable_next=function(O){switch(M){case 1:case 2:case 3:var Z=3;break;default:Z=M}var $=M;M=Z;try{return O()}finally{M=$}},i.unstable_pauseExecution=function(){},i.unstable_requestPaint=function(){},i.unstable_runWithPriority=function(O,Z){switch(O){case 1:case 2:case 3:case 4:case 5:break;default:O=3}var $=M;M=O;try{return Z()}finally{M=$}},i.unstable_scheduleCallback=function(O,Z,$){var y=i.unstable_now();switch(typeof $=="object"&&$!==null?($=$.delay,$=typeof $=="number"&&0<$?y+$:y):$=y,O){case 1:var L=-1;break;case 2:L=250;break;case 5:L=1073741823;break;case 4:L=1e4;break;default:L=5e3}return L=$+L,O={id:C++,callback:Z,priorityLevel:O,startTime:$,expirationTime:L,sortIndex:-1},$>y?(O.sortIndex=$,l(z,O),c(b)===null&&O===c(z)&&(_?(J(pe),pe=-1):_=!0,he(ee,$-y))):(O.sortIndex=L,l(b,O),R||I||(R=!0,Fe(se))),O},i.unstable_shouldYield=Te,i.unstable_wrapCallback=function(O){var Z=M;return function(){var $=M;M=Z;try{return O.apply(this,arguments)}finally{M=$}}}})(io)),io}var ju;function lh(){return ju||(ju=1,ao.exports=oh()),ao.exports}/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var Su;function ch(){if(Su)return at;Su=1;var i=wo(),l=lh();function c(e){for(var t="https://reactjs.org/docs/error-decoder.html?invariant="+e,r=1;r<arguments.length;r++)t+="&args[]="+encodeURIComponent(arguments[r]);return"Minified React error #"+e+"; visit "+t+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var d=new Set,m={};function p(e,t){g(e,t),g(e+"Capture",t)}function g(e,t){for(m[e]=t,e=0;e<t.length;e++)d.add(t[e])}var E=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),b=Object.prototype.hasOwnProperty,z=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,C={},N={};function M(e){return b.call(N,e)?!0:b.call(C,e)?!1:z.test(e)?N[e]=!0:(C[e]=!0,!1)}function I(e,t,r,s){if(r!==null&&r.type===0)return!1;switch(typeof t){case"function":case"symbol":return!0;case"boolean":return s?!1:r!==null?!r.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function R(e,t,r,s){if(t===null||typeof t>"u"||I(e,t,r,s))return!0;if(s)return!1;if(r!==null)switch(r.type){case 3:return!t;case 4:return t===!1;case 5:return isNaN(t);case 6:return isNaN(t)||1>t}return!1}function _(e,t,r,s,a,o,u){this.acceptsBooleans=t===2||t===3||t===4,this.attributeName=s,this.attributeNamespace=a,this.mustUseProperty=r,this.propertyName=e,this.type=t,this.sanitizeURL=o,this.removeEmptyString=u}var j={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){j[e]=new _(e,0,!1,e,null,!1,!1)}),[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var t=e[0];j[t]=new _(t,1,!1,e[1],null,!1,!1)}),["contentEditable","draggable","spellCheck","value"].forEach(function(e){j[e]=new _(e,2,!1,e.toLowerCase(),null,!1,!1)}),["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){j[e]=new _(e,2,!1,e,null,!1,!1)}),"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){j[e]=new _(e,3,!1,e.toLowerCase(),null,!1,!1)}),["checked","multiple","muted","selected"].forEach(function(e){j[e]=new _(e,3,!0,e,null,!1,!1)}),["capture","download"].forEach(function(e){j[e]=new _(e,4,!1,e,null,!1,!1)}),["cols","rows","size","span"].forEach(function(e){j[e]=new _(e,6,!1,e,null,!1,!1)}),["rowSpan","start"].forEach(function(e){j[e]=new _(e,5,!1,e.toLowerCase(),null,!1,!1)});var J=/[\-:]([a-z])/g;function S(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var t=e.replace(J,S);j[t]=new _(t,1,!1,e,null,!1,!1)}),"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var t=e.replace(J,S);j[t]=new _(t,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)}),["xml:base","xml:lang","xml:space"].forEach(function(e){var t=e.replace(J,S);j[t]=new _(t,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)}),["tabIndex","crossOrigin"].forEach(function(e){j[e]=new _(e,1,!1,e.toLowerCase(),null,!1,!1)}),j.xlinkHref=new _("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1),["src","href","action","formAction"].forEach(function(e){j[e]=new _(e,1,!1,e.toLowerCase(),null,!0,!0)});function V(e,t,r,s){var a=j.hasOwnProperty(t)?j[t]:null;(a!==null?a.type!==0:s||!(2<t.length)||t[0]!=="o"&&t[0]!=="O"||t[1]!=="n"&&t[1]!=="N")&&(R(t,r,a,s)&&(r=null),s||a===null?M(t)&&(r===null?e.removeAttribute(t):e.setAttribute(t,""+r)):a.mustUseProperty?e[a.propertyName]=r===null?a.type===3?!1:"":r:(t=a.attributeName,s=a.attributeNamespace,r===null?e.removeAttribute(t):(a=a.type,r=a===3||a===4&&r===!0?"":""+r,s?e.setAttributeNS(s,t,r):e.setAttribute(t,r))))}var ee=i.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,se=Symbol.for("react.element"),B=Symbol.for("react.portal"),Q=Symbol.for("react.fragment"),pe=Symbol.for("react.strict_mode"),ne=Symbol.for("react.profiler"),je=Symbol.for("react.provider"),Te=Symbol.for("react.context"),Se=Symbol.for("react.forward_ref"),re=Symbol.for("react.suspense"),Le=Symbol.for("react.suspense_list"),He=Symbol.for("react.memo"),Fe=Symbol.for("react.lazy"),he=Symbol.for("react.offscreen"),O=Symbol.iterator;function Z(e){return e===null||typeof e!="object"?null:(e=O&&e[O]||e["@@iterator"],typeof e=="function"?e:null)}var $=Object.assign,y;function L(e){if(y===void 0)try{throw Error()}catch(r){var t=r.stack.trim().match(/\n( *(at )?)/);y=t&&t[1]||""}return`
`+y+e}var ae=!1;function oe(e,t){if(!e||ae)return"";ae=!0;var r=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(t)if(t=function(){throw Error()},Object.defineProperty(t.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(t,[])}catch(w){var s=w}Reflect.construct(e,[],t)}else{try{t.call()}catch(w){s=w}e.call(t.prototype)}else{try{throw Error()}catch(w){s=w}e()}}catch(w){if(w&&s&&typeof w.stack=="string"){for(var a=w.stack.split(`
`),o=s.stack.split(`
`),u=a.length-1,h=o.length-1;1<=u&&0<=h&&a[u]!==o[h];)h--;for(;1<=u&&0<=h;u--,h--)if(a[u]!==o[h]){if(u!==1||h!==1)do if(u--,h--,0>h||a[u]!==o[h]){var f=`
`+a[u].replace(" at new "," at ");return e.displayName&&f.includes("<anonymous>")&&(f=f.replace("<anonymous>",e.displayName)),f}while(1<=u&&0<=h);break}}}finally{ae=!1,Error.prepareStackTrace=r}return(e=e?e.displayName||e.name:"")?L(e):""}function ue(e){switch(e.tag){case 5:return L(e.type);case 16:return L("Lazy");case 13:return L("Suspense");case 19:return L("SuspenseList");case 0:case 2:case 15:return e=oe(e.type,!1),e;case 11:return e=oe(e.type.render,!1),e;case 1:return e=oe(e.type,!0),e;default:return""}}function de(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case Q:return"Fragment";case B:return"Portal";case ne:return"Profiler";case pe:return"StrictMode";case re:return"Suspense";case Le:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case Te:return(e.displayName||"Context")+".Consumer";case je:return(e._context.displayName||"Context")+".Provider";case Se:var t=e.render;return e=e.displayName,e||(e=t.displayName||t.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case He:return t=e.displayName||null,t!==null?t:de(e.type)||"Memo";case Fe:t=e._payload,e=e._init;try{return de(e(t))}catch{}}return null}function ve(e){var t=e.type;switch(e.tag){case 24:return"Cache";case 9:return(t.displayName||"Context")+".Consumer";case 10:return(t._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=t.render,e=e.displayName||e.name||"",t.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return t;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return de(t);case 8:return t===pe?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof t=="function")return t.displayName||t.name||null;if(typeof t=="string")return t}return null}function fe(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function we(e){var t=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(t==="checkbox"||t==="radio")}function ot(e){var t=we(e)?"checked":"value",r=Object.getOwnPropertyDescriptor(e.constructor.prototype,t),s=""+e[t];if(!e.hasOwnProperty(t)&&typeof r<"u"&&typeof r.get=="function"&&typeof r.set=="function"){var a=r.get,o=r.set;return Object.defineProperty(e,t,{configurable:!0,get:function(){return a.call(this)},set:function(u){s=""+u,o.call(this,u)}}),Object.defineProperty(e,t,{enumerable:r.enumerable}),{getValue:function(){return s},setValue:function(u){s=""+u},stopTracking:function(){e._valueTracker=null,delete e[t]}}}}function zr(e){e._valueTracker||(e._valueTracker=ot(e))}function jo(e){if(!e)return!1;var t=e._valueTracker;if(!t)return!0;var r=t.getValue(),s="";return e&&(s=we(e)?e.checked?"true":"false":e.value),e=s,e!==r?(t.setValue(e),!0):!1}function Fr(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function ca(e,t){var r=t.checked;return $({},t,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:r??e._wrapperState.initialChecked})}function So(e,t){var r=t.defaultValue==null?"":t.defaultValue,s=t.checked!=null?t.checked:t.defaultChecked;r=fe(t.value!=null?t.value:r),e._wrapperState={initialChecked:s,initialValue:r,controlled:t.type==="checkbox"||t.type==="radio"?t.checked!=null:t.value!=null}}function No(e,t){t=t.checked,t!=null&&V(e,"checked",t,!1)}function ua(e,t){No(e,t);var r=fe(t.value),s=t.type;if(r!=null)s==="number"?(r===0&&e.value===""||e.value!=r)&&(e.value=""+r):e.value!==""+r&&(e.value=""+r);else if(s==="submit"||s==="reset"){e.removeAttribute("value");return}t.hasOwnProperty("value")?da(e,t.type,r):t.hasOwnProperty("defaultValue")&&da(e,t.type,fe(t.defaultValue)),t.checked==null&&t.defaultChecked!=null&&(e.defaultChecked=!!t.defaultChecked)}function Co(e,t,r){if(t.hasOwnProperty("value")||t.hasOwnProperty("defaultValue")){var s=t.type;if(!(s!=="submit"&&s!=="reset"||t.value!==void 0&&t.value!==null))return;t=""+e._wrapperState.initialValue,r||t===e.value||(e.value=t),e.defaultValue=t}r=e.name,r!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,r!==""&&(e.name=r)}function da(e,t,r){(t!=="number"||Fr(e.ownerDocument)!==e)&&(r==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+r&&(e.defaultValue=""+r))}var Yn=Array.isArray;function Nn(e,t,r,s){if(e=e.options,t){t={};for(var a=0;a<r.length;a++)t["$"+r[a]]=!0;for(r=0;r<e.length;r++)a=t.hasOwnProperty("$"+e[r].value),e[r].selected!==a&&(e[r].selected=a),a&&s&&(e[r].defaultSelected=!0)}else{for(r=""+fe(r),t=null,a=0;a<e.length;a++){if(e[a].value===r){e[a].selected=!0,s&&(e[a].defaultSelected=!0);return}t!==null||e[a].disabled||(t=e[a])}t!==null&&(t.selected=!0)}}function ma(e,t){if(t.dangerouslySetInnerHTML!=null)throw Error(c(91));return $({},t,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function _o(e,t){var r=t.value;if(r==null){if(r=t.children,t=t.defaultValue,r!=null){if(t!=null)throw Error(c(92));if(Yn(r)){if(1<r.length)throw Error(c(93));r=r[0]}t=r}t==null&&(t=""),r=t}e._wrapperState={initialValue:fe(r)}}function To(e,t){var r=fe(t.value),s=fe(t.defaultValue);r!=null&&(r=""+r,r!==e.value&&(e.value=r),t.defaultValue==null&&e.defaultValue!==r&&(e.defaultValue=r)),s!=null&&(e.defaultValue=""+s)}function Eo(e){var t=e.textContent;t===e._wrapperState.initialValue&&t!==""&&t!==null&&(e.value=t)}function Mo(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function ha(e,t){return e==null||e==="http://www.w3.org/1999/xhtml"?Mo(t):e==="http://www.w3.org/2000/svg"&&t==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var Br,Po=(function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(t,r,s,a){MSApp.execUnsafeLocalFunction(function(){return e(t,r,s,a)})}:e})(function(e,t){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=t;else{for(Br=Br||document.createElement("div"),Br.innerHTML="<svg>"+t.valueOf().toString()+"</svg>",t=Br.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;t.firstChild;)e.appendChild(t.firstChild)}});function Jn(e,t){if(t){var r=e.firstChild;if(r&&r===e.lastChild&&r.nodeType===3){r.nodeValue=t;return}}e.textContent=t}var Zn={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},id=["Webkit","ms","Moz","O"];Object.keys(Zn).forEach(function(e){id.forEach(function(t){t=t+e.charAt(0).toUpperCase()+e.substring(1),Zn[t]=Zn[e]})});function Lo(e,t,r){return t==null||typeof t=="boolean"||t===""?"":r||typeof t!="number"||t===0||Zn.hasOwnProperty(e)&&Zn[e]?(""+t).trim():t+"px"}function Ao(e,t){e=e.style;for(var r in t)if(t.hasOwnProperty(r)){var s=r.indexOf("--")===0,a=Lo(r,t[r],s);r==="float"&&(r="cssFloat"),s?e.setProperty(r,a):e[r]=a}}var od=$({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function pa(e,t){if(t){if(od[e]&&(t.children!=null||t.dangerouslySetInnerHTML!=null))throw Error(c(137,e));if(t.dangerouslySetInnerHTML!=null){if(t.children!=null)throw Error(c(60));if(typeof t.dangerouslySetInnerHTML!="object"||!("__html"in t.dangerouslySetInnerHTML))throw Error(c(61))}if(t.style!=null&&typeof t.style!="object")throw Error(c(62))}}function fa(e,t){if(e.indexOf("-")===-1)return typeof t.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var ga=null;function va(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var ya=null,Cn=null,_n=null;function Do(e){if(e=wr(e)){if(typeof ya!="function")throw Error(c(280));var t=e.stateNode;t&&(t=ls(t),ya(e.stateNode,e.type,t))}}function Ro(e){Cn?_n?_n.push(e):_n=[e]:Cn=e}function Io(){if(Cn){var e=Cn,t=_n;if(_n=Cn=null,Do(e),t)for(e=0;e<t.length;e++)Do(t[e])}}function zo(e,t){return e(t)}function Fo(){}var xa=!1;function Bo(e,t,r){if(xa)return e(t,r);xa=!0;try{return zo(e,t,r)}finally{xa=!1,(Cn!==null||_n!==null)&&(Fo(),Io())}}function er(e,t){var r=e.stateNode;if(r===null)return null;var s=ls(r);if(s===null)return null;r=s[t];e:switch(t){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(s=!s.disabled)||(e=e.type,s=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!s;break e;default:e=!1}if(e)return null;if(r&&typeof r!="function")throw Error(c(231,t,typeof r));return r}var ka=!1;if(E)try{var tr={};Object.defineProperty(tr,"passive",{get:function(){ka=!0}}),window.addEventListener("test",tr,tr),window.removeEventListener("test",tr,tr)}catch{ka=!1}function ld(e,t,r,s,a,o,u,h,f){var w=Array.prototype.slice.call(arguments,3);try{t.apply(r,w)}catch(A){this.onError(A)}}var nr=!1,Or=null,Ur=!1,wa=null,cd={onError:function(e){nr=!0,Or=e}};function ud(e,t,r,s,a,o,u,h,f){nr=!1,Or=null,ld.apply(cd,arguments)}function dd(e,t,r,s,a,o,u,h,f){if(ud.apply(this,arguments),nr){if(nr){var w=Or;nr=!1,Or=null}else throw Error(c(198));Ur||(Ur=!0,wa=w)}}function ln(e){var t=e,r=e;if(e.alternate)for(;t.return;)t=t.return;else{e=t;do t=e,(t.flags&4098)!==0&&(r=t.return),e=t.return;while(e)}return t.tag===3?r:null}function Oo(e){if(e.tag===13){var t=e.memoizedState;if(t===null&&(e=e.alternate,e!==null&&(t=e.memoizedState)),t!==null)return t.dehydrated}return null}function Uo(e){if(ln(e)!==e)throw Error(c(188))}function md(e){var t=e.alternate;if(!t){if(t=ln(e),t===null)throw Error(c(188));return t!==e?null:e}for(var r=e,s=t;;){var a=r.return;if(a===null)break;var o=a.alternate;if(o===null){if(s=a.return,s!==null){r=s;continue}break}if(a.child===o.child){for(o=a.child;o;){if(o===r)return Uo(a),e;if(o===s)return Uo(a),t;o=o.sibling}throw Error(c(188))}if(r.return!==s.return)r=a,s=o;else{for(var u=!1,h=a.child;h;){if(h===r){u=!0,r=a,s=o;break}if(h===s){u=!0,s=a,r=o;break}h=h.sibling}if(!u){for(h=o.child;h;){if(h===r){u=!0,r=o,s=a;break}if(h===s){u=!0,s=o,r=a;break}h=h.sibling}if(!u)throw Error(c(189))}}if(r.alternate!==s)throw Error(c(190))}if(r.tag!==3)throw Error(c(188));return r.stateNode.current===r?e:t}function Wo(e){return e=md(e),e!==null?$o(e):null}function $o(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var t=$o(e);if(t!==null)return t;e=e.sibling}return null}var Vo=l.unstable_scheduleCallback,Ho=l.unstable_cancelCallback,hd=l.unstable_shouldYield,pd=l.unstable_requestPaint,Ee=l.unstable_now,fd=l.unstable_getCurrentPriorityLevel,ba=l.unstable_ImmediatePriority,Go=l.unstable_UserBlockingPriority,Wr=l.unstable_NormalPriority,gd=l.unstable_LowPriority,Ko=l.unstable_IdlePriority,$r=null,Ct=null;function vd(e){if(Ct&&typeof Ct.onCommitFiberRoot=="function")try{Ct.onCommitFiberRoot($r,e,void 0,(e.current.flags&128)===128)}catch{}}var yt=Math.clz32?Math.clz32:kd,yd=Math.log,xd=Math.LN2;function kd(e){return e>>>=0,e===0?32:31-(yd(e)/xd|0)|0}var Vr=64,Hr=4194304;function rr(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function Gr(e,t){var r=e.pendingLanes;if(r===0)return 0;var s=0,a=e.suspendedLanes,o=e.pingedLanes,u=r&268435455;if(u!==0){var h=u&~a;h!==0?s=rr(h):(o&=u,o!==0&&(s=rr(o)))}else u=r&~a,u!==0?s=rr(u):o!==0&&(s=rr(o));if(s===0)return 0;if(t!==0&&t!==s&&(t&a)===0&&(a=s&-s,o=t&-t,a>=o||a===16&&(o&4194240)!==0))return t;if((s&4)!==0&&(s|=r&16),t=e.entangledLanes,t!==0)for(e=e.entanglements,t&=s;0<t;)r=31-yt(t),a=1<<r,s|=e[r],t&=~a;return s}function wd(e,t){switch(e){case 1:case 2:case 4:return t+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return t+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function bd(e,t){for(var r=e.suspendedLanes,s=e.pingedLanes,a=e.expirationTimes,o=e.pendingLanes;0<o;){var u=31-yt(o),h=1<<u,f=a[u];f===-1?((h&r)===0||(h&s)!==0)&&(a[u]=wd(h,t)):f<=t&&(e.expiredLanes|=h),o&=~h}}function ja(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function qo(){var e=Vr;return Vr<<=1,(Vr&4194240)===0&&(Vr=64),e}function Sa(e){for(var t=[],r=0;31>r;r++)t.push(e);return t}function sr(e,t,r){e.pendingLanes|=t,t!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,t=31-yt(t),e[t]=r}function jd(e,t){var r=e.pendingLanes&~t;e.pendingLanes=t,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=t,e.mutableReadLanes&=t,e.entangledLanes&=t,t=e.entanglements;var s=e.eventTimes;for(e=e.expirationTimes;0<r;){var a=31-yt(r),o=1<<a;t[a]=0,s[a]=-1,e[a]=-1,r&=~o}}function Na(e,t){var r=e.entangledLanes|=t;for(e=e.entanglements;r;){var s=31-yt(r),a=1<<s;a&t|e[s]&t&&(e[s]|=t),r&=~a}}var ge=0;function Qo(e){return e&=-e,1<e?4<e?(e&268435455)!==0?16:536870912:4:1}var Xo,Ca,Yo,Jo,Zo,_a=!1,Kr=[],Ot=null,Ut=null,Wt=null,ar=new Map,ir=new Map,$t=[],Sd="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function el(e,t){switch(e){case"focusin":case"focusout":Ot=null;break;case"dragenter":case"dragleave":Ut=null;break;case"mouseover":case"mouseout":Wt=null;break;case"pointerover":case"pointerout":ar.delete(t.pointerId);break;case"gotpointercapture":case"lostpointercapture":ir.delete(t.pointerId)}}function or(e,t,r,s,a,o){return e===null||e.nativeEvent!==o?(e={blockedOn:t,domEventName:r,eventSystemFlags:s,nativeEvent:o,targetContainers:[a]},t!==null&&(t=wr(t),t!==null&&Ca(t)),e):(e.eventSystemFlags|=s,t=e.targetContainers,a!==null&&t.indexOf(a)===-1&&t.push(a),e)}function Nd(e,t,r,s,a){switch(t){case"focusin":return Ot=or(Ot,e,t,r,s,a),!0;case"dragenter":return Ut=or(Ut,e,t,r,s,a),!0;case"mouseover":return Wt=or(Wt,e,t,r,s,a),!0;case"pointerover":var o=a.pointerId;return ar.set(o,or(ar.get(o)||null,e,t,r,s,a)),!0;case"gotpointercapture":return o=a.pointerId,ir.set(o,or(ir.get(o)||null,e,t,r,s,a)),!0}return!1}function tl(e){var t=cn(e.target);if(t!==null){var r=ln(t);if(r!==null){if(t=r.tag,t===13){if(t=Oo(r),t!==null){e.blockedOn=t,Zo(e.priority,function(){Yo(r)});return}}else if(t===3&&r.stateNode.current.memoizedState.isDehydrated){e.blockedOn=r.tag===3?r.stateNode.containerInfo:null;return}}}e.blockedOn=null}function qr(e){if(e.blockedOn!==null)return!1;for(var t=e.targetContainers;0<t.length;){var r=Ea(e.domEventName,e.eventSystemFlags,t[0],e.nativeEvent);if(r===null){r=e.nativeEvent;var s=new r.constructor(r.type,r);ga=s,r.target.dispatchEvent(s),ga=null}else return t=wr(r),t!==null&&Ca(t),e.blockedOn=r,!1;t.shift()}return!0}function nl(e,t,r){qr(e)&&r.delete(t)}function Cd(){_a=!1,Ot!==null&&qr(Ot)&&(Ot=null),Ut!==null&&qr(Ut)&&(Ut=null),Wt!==null&&qr(Wt)&&(Wt=null),ar.forEach(nl),ir.forEach(nl)}function lr(e,t){e.blockedOn===t&&(e.blockedOn=null,_a||(_a=!0,l.unstable_scheduleCallback(l.unstable_NormalPriority,Cd)))}function cr(e){function t(a){return lr(a,e)}if(0<Kr.length){lr(Kr[0],e);for(var r=1;r<Kr.length;r++){var s=Kr[r];s.blockedOn===e&&(s.blockedOn=null)}}for(Ot!==null&&lr(Ot,e),Ut!==null&&lr(Ut,e),Wt!==null&&lr(Wt,e),ar.forEach(t),ir.forEach(t),r=0;r<$t.length;r++)s=$t[r],s.blockedOn===e&&(s.blockedOn=null);for(;0<$t.length&&(r=$t[0],r.blockedOn===null);)tl(r),r.blockedOn===null&&$t.shift()}var Tn=ee.ReactCurrentBatchConfig,Qr=!0;function _d(e,t,r,s){var a=ge,o=Tn.transition;Tn.transition=null;try{ge=1,Ta(e,t,r,s)}finally{ge=a,Tn.transition=o}}function Td(e,t,r,s){var a=ge,o=Tn.transition;Tn.transition=null;try{ge=4,Ta(e,t,r,s)}finally{ge=a,Tn.transition=o}}function Ta(e,t,r,s){if(Qr){var a=Ea(e,t,r,s);if(a===null)Ga(e,t,s,Xr,r),el(e,s);else if(Nd(a,e,t,r,s))s.stopPropagation();else if(el(e,s),t&4&&-1<Sd.indexOf(e)){for(;a!==null;){var o=wr(a);if(o!==null&&Xo(o),o=Ea(e,t,r,s),o===null&&Ga(e,t,s,Xr,r),o===a)break;a=o}a!==null&&s.stopPropagation()}else Ga(e,t,s,null,r)}}var Xr=null;function Ea(e,t,r,s){if(Xr=null,e=va(s),e=cn(e),e!==null)if(t=ln(e),t===null)e=null;else if(r=t.tag,r===13){if(e=Oo(t),e!==null)return e;e=null}else if(r===3){if(t.stateNode.current.memoizedState.isDehydrated)return t.tag===3?t.stateNode.containerInfo:null;e=null}else t!==e&&(e=null);return Xr=e,null}function rl(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(fd()){case ba:return 1;case Go:return 4;case Wr:case gd:return 16;case Ko:return 536870912;default:return 16}default:return 16}}var Vt=null,Ma=null,Yr=null;function sl(){if(Yr)return Yr;var e,t=Ma,r=t.length,s,a="value"in Vt?Vt.value:Vt.textContent,o=a.length;for(e=0;e<r&&t[e]===a[e];e++);var u=r-e;for(s=1;s<=u&&t[r-s]===a[o-s];s++);return Yr=a.slice(e,1<s?1-s:void 0)}function Jr(e){var t=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&t===13&&(e=13)):e=t,e===10&&(e=13),32<=e||e===13?e:0}function Zr(){return!0}function al(){return!1}function lt(e){function t(r,s,a,o,u){this._reactName=r,this._targetInst=a,this.type=s,this.nativeEvent=o,this.target=u,this.currentTarget=null;for(var h in e)e.hasOwnProperty(h)&&(r=e[h],this[h]=r?r(o):o[h]);return this.isDefaultPrevented=(o.defaultPrevented!=null?o.defaultPrevented:o.returnValue===!1)?Zr:al,this.isPropagationStopped=al,this}return $(t.prototype,{preventDefault:function(){this.defaultPrevented=!0;var r=this.nativeEvent;r&&(r.preventDefault?r.preventDefault():typeof r.returnValue!="unknown"&&(r.returnValue=!1),this.isDefaultPrevented=Zr)},stopPropagation:function(){var r=this.nativeEvent;r&&(r.stopPropagation?r.stopPropagation():typeof r.cancelBubble!="unknown"&&(r.cancelBubble=!0),this.isPropagationStopped=Zr)},persist:function(){},isPersistent:Zr}),t}var En={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},Pa=lt(En),ur=$({},En,{view:0,detail:0}),Ed=lt(ur),La,Aa,dr,es=$({},ur,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:Ra,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==dr&&(dr&&e.type==="mousemove"?(La=e.screenX-dr.screenX,Aa=e.screenY-dr.screenY):Aa=La=0,dr=e),La)},movementY:function(e){return"movementY"in e?e.movementY:Aa}}),il=lt(es),Md=$({},es,{dataTransfer:0}),Pd=lt(Md),Ld=$({},ur,{relatedTarget:0}),Da=lt(Ld),Ad=$({},En,{animationName:0,elapsedTime:0,pseudoElement:0}),Dd=lt(Ad),Rd=$({},En,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),Id=lt(Rd),zd=$({},En,{data:0}),ol=lt(zd),Fd={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},Bd={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},Od={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function Ud(e){var t=this.nativeEvent;return t.getModifierState?t.getModifierState(e):(e=Od[e])?!!t[e]:!1}function Ra(){return Ud}var Wd=$({},ur,{key:function(e){if(e.key){var t=Fd[e.key]||e.key;if(t!=="Unidentified")return t}return e.type==="keypress"?(e=Jr(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?Bd[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:Ra,charCode:function(e){return e.type==="keypress"?Jr(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?Jr(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),$d=lt(Wd),Vd=$({},es,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),ll=lt(Vd),Hd=$({},ur,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:Ra}),Gd=lt(Hd),Kd=$({},En,{propertyName:0,elapsedTime:0,pseudoElement:0}),qd=lt(Kd),Qd=$({},es,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),Xd=lt(Qd),Yd=[9,13,27,32],Ia=E&&"CompositionEvent"in window,mr=null;E&&"documentMode"in document&&(mr=document.documentMode);var Jd=E&&"TextEvent"in window&&!mr,cl=E&&(!Ia||mr&&8<mr&&11>=mr),ul=" ",dl=!1;function ml(e,t){switch(e){case"keyup":return Yd.indexOf(t.keyCode)!==-1;case"keydown":return t.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function hl(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var Mn=!1;function Zd(e,t){switch(e){case"compositionend":return hl(t);case"keypress":return t.which!==32?null:(dl=!0,ul);case"textInput":return e=t.data,e===ul&&dl?null:e;default:return null}}function em(e,t){if(Mn)return e==="compositionend"||!Ia&&ml(e,t)?(e=sl(),Yr=Ma=Vt=null,Mn=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(t.ctrlKey||t.altKey||t.metaKey)||t.ctrlKey&&t.altKey){if(t.char&&1<t.char.length)return t.char;if(t.which)return String.fromCharCode(t.which)}return null;case"compositionend":return cl&&t.locale!=="ko"?null:t.data;default:return null}}var tm={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function pl(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t==="input"?!!tm[e.type]:t==="textarea"}function fl(e,t,r,s){Ro(s),t=as(t,"onChange"),0<t.length&&(r=new Pa("onChange","change",null,r,s),e.push({event:r,listeners:t}))}var hr=null,pr=null;function nm(e){Al(e,0)}function ts(e){var t=Rn(e);if(jo(t))return e}function rm(e,t){if(e==="change")return t}var gl=!1;if(E){var za;if(E){var Fa="oninput"in document;if(!Fa){var vl=document.createElement("div");vl.setAttribute("oninput","return;"),Fa=typeof vl.oninput=="function"}za=Fa}else za=!1;gl=za&&(!document.documentMode||9<document.documentMode)}function yl(){hr&&(hr.detachEvent("onpropertychange",xl),pr=hr=null)}function xl(e){if(e.propertyName==="value"&&ts(pr)){var t=[];fl(t,pr,e,va(e)),Bo(nm,t)}}function sm(e,t,r){e==="focusin"?(yl(),hr=t,pr=r,hr.attachEvent("onpropertychange",xl)):e==="focusout"&&yl()}function am(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return ts(pr)}function im(e,t){if(e==="click")return ts(t)}function om(e,t){if(e==="input"||e==="change")return ts(t)}function lm(e,t){return e===t&&(e!==0||1/e===1/t)||e!==e&&t!==t}var xt=typeof Object.is=="function"?Object.is:lm;function fr(e,t){if(xt(e,t))return!0;if(typeof e!="object"||e===null||typeof t!="object"||t===null)return!1;var r=Object.keys(e),s=Object.keys(t);if(r.length!==s.length)return!1;for(s=0;s<r.length;s++){var a=r[s];if(!b.call(t,a)||!xt(e[a],t[a]))return!1}return!0}function kl(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function wl(e,t){var r=kl(e);e=0;for(var s;r;){if(r.nodeType===3){if(s=e+r.textContent.length,e<=t&&s>=t)return{node:r,offset:t-e};e=s}e:{for(;r;){if(r.nextSibling){r=r.nextSibling;break e}r=r.parentNode}r=void 0}r=kl(r)}}function bl(e,t){return e&&t?e===t?!0:e&&e.nodeType===3?!1:t&&t.nodeType===3?bl(e,t.parentNode):"contains"in e?e.contains(t):e.compareDocumentPosition?!!(e.compareDocumentPosition(t)&16):!1:!1}function jl(){for(var e=window,t=Fr();t instanceof e.HTMLIFrameElement;){try{var r=typeof t.contentWindow.location.href=="string"}catch{r=!1}if(r)e=t.contentWindow;else break;t=Fr(e.document)}return t}function Ba(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t&&(t==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||t==="textarea"||e.contentEditable==="true")}function cm(e){var t=jl(),r=e.focusedElem,s=e.selectionRange;if(t!==r&&r&&r.ownerDocument&&bl(r.ownerDocument.documentElement,r)){if(s!==null&&Ba(r)){if(t=s.start,e=s.end,e===void 0&&(e=t),"selectionStart"in r)r.selectionStart=t,r.selectionEnd=Math.min(e,r.value.length);else if(e=(t=r.ownerDocument||document)&&t.defaultView||window,e.getSelection){e=e.getSelection();var a=r.textContent.length,o=Math.min(s.start,a);s=s.end===void 0?o:Math.min(s.end,a),!e.extend&&o>s&&(a=s,s=o,o=a),a=wl(r,o);var u=wl(r,s);a&&u&&(e.rangeCount!==1||e.anchorNode!==a.node||e.anchorOffset!==a.offset||e.focusNode!==u.node||e.focusOffset!==u.offset)&&(t=t.createRange(),t.setStart(a.node,a.offset),e.removeAllRanges(),o>s?(e.addRange(t),e.extend(u.node,u.offset)):(t.setEnd(u.node,u.offset),e.addRange(t)))}}for(t=[],e=r;e=e.parentNode;)e.nodeType===1&&t.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof r.focus=="function"&&r.focus(),r=0;r<t.length;r++)e=t[r],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var um=E&&"documentMode"in document&&11>=document.documentMode,Pn=null,Oa=null,gr=null,Ua=!1;function Sl(e,t,r){var s=r.window===r?r.document:r.nodeType===9?r:r.ownerDocument;Ua||Pn==null||Pn!==Fr(s)||(s=Pn,"selectionStart"in s&&Ba(s)?s={start:s.selectionStart,end:s.selectionEnd}:(s=(s.ownerDocument&&s.ownerDocument.defaultView||window).getSelection(),s={anchorNode:s.anchorNode,anchorOffset:s.anchorOffset,focusNode:s.focusNode,focusOffset:s.focusOffset}),gr&&fr(gr,s)||(gr=s,s=as(Oa,"onSelect"),0<s.length&&(t=new Pa("onSelect","select",null,t,r),e.push({event:t,listeners:s}),t.target=Pn)))}function ns(e,t){var r={};return r[e.toLowerCase()]=t.toLowerCase(),r["Webkit"+e]="webkit"+t,r["Moz"+e]="moz"+t,r}var Ln={animationend:ns("Animation","AnimationEnd"),animationiteration:ns("Animation","AnimationIteration"),animationstart:ns("Animation","AnimationStart"),transitionend:ns("Transition","TransitionEnd")},Wa={},Nl={};E&&(Nl=document.createElement("div").style,"AnimationEvent"in window||(delete Ln.animationend.animation,delete Ln.animationiteration.animation,delete Ln.animationstart.animation),"TransitionEvent"in window||delete Ln.transitionend.transition);function rs(e){if(Wa[e])return Wa[e];if(!Ln[e])return e;var t=Ln[e],r;for(r in t)if(t.hasOwnProperty(r)&&r in Nl)return Wa[e]=t[r];return e}var Cl=rs("animationend"),_l=rs("animationiteration"),Tl=rs("animationstart"),El=rs("transitionend"),Ml=new Map,Pl="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function Ht(e,t){Ml.set(e,t),p(t,[e])}for(var $a=0;$a<Pl.length;$a++){var Va=Pl[$a],dm=Va.toLowerCase(),mm=Va[0].toUpperCase()+Va.slice(1);Ht(dm,"on"+mm)}Ht(Cl,"onAnimationEnd"),Ht(_l,"onAnimationIteration"),Ht(Tl,"onAnimationStart"),Ht("dblclick","onDoubleClick"),Ht("focusin","onFocus"),Ht("focusout","onBlur"),Ht(El,"onTransitionEnd"),g("onMouseEnter",["mouseout","mouseover"]),g("onMouseLeave",["mouseout","mouseover"]),g("onPointerEnter",["pointerout","pointerover"]),g("onPointerLeave",["pointerout","pointerover"]),p("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),p("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),p("onBeforeInput",["compositionend","keypress","textInput","paste"]),p("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),p("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),p("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var vr="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),hm=new Set("cancel close invalid load scroll toggle".split(" ").concat(vr));function Ll(e,t,r){var s=e.type||"unknown-event";e.currentTarget=r,dd(s,t,void 0,e),e.currentTarget=null}function Al(e,t){t=(t&4)!==0;for(var r=0;r<e.length;r++){var s=e[r],a=s.event;s=s.listeners;e:{var o=void 0;if(t)for(var u=s.length-1;0<=u;u--){var h=s[u],f=h.instance,w=h.currentTarget;if(h=h.listener,f!==o&&a.isPropagationStopped())break e;Ll(a,h,w),o=f}else for(u=0;u<s.length;u++){if(h=s[u],f=h.instance,w=h.currentTarget,h=h.listener,f!==o&&a.isPropagationStopped())break e;Ll(a,h,w),o=f}}}if(Ur)throw e=wa,Ur=!1,wa=null,e}function xe(e,t){var r=t[Ja];r===void 0&&(r=t[Ja]=new Set);var s=e+"__bubble";r.has(s)||(Dl(t,e,2,!1),r.add(s))}function Ha(e,t,r){var s=0;t&&(s|=4),Dl(r,e,s,t)}var ss="_reactListening"+Math.random().toString(36).slice(2);function yr(e){if(!e[ss]){e[ss]=!0,d.forEach(function(r){r!=="selectionchange"&&(hm.has(r)||Ha(r,!1,e),Ha(r,!0,e))});var t=e.nodeType===9?e:e.ownerDocument;t===null||t[ss]||(t[ss]=!0,Ha("selectionchange",!1,t))}}function Dl(e,t,r,s){switch(rl(t)){case 1:var a=_d;break;case 4:a=Td;break;default:a=Ta}r=a.bind(null,t,r,e),a=void 0,!ka||t!=="touchstart"&&t!=="touchmove"&&t!=="wheel"||(a=!0),s?a!==void 0?e.addEventListener(t,r,{capture:!0,passive:a}):e.addEventListener(t,r,!0):a!==void 0?e.addEventListener(t,r,{passive:a}):e.addEventListener(t,r,!1)}function Ga(e,t,r,s,a){var o=s;if((t&1)===0&&(t&2)===0&&s!==null)e:for(;;){if(s===null)return;var u=s.tag;if(u===3||u===4){var h=s.stateNode.containerInfo;if(h===a||h.nodeType===8&&h.parentNode===a)break;if(u===4)for(u=s.return;u!==null;){var f=u.tag;if((f===3||f===4)&&(f=u.stateNode.containerInfo,f===a||f.nodeType===8&&f.parentNode===a))return;u=u.return}for(;h!==null;){if(u=cn(h),u===null)return;if(f=u.tag,f===5||f===6){s=o=u;continue e}h=h.parentNode}}s=s.return}Bo(function(){var w=o,A=va(r),D=[];e:{var P=Ml.get(e);if(P!==void 0){var U=Pa,H=e;switch(e){case"keypress":if(Jr(r)===0)break e;case"keydown":case"keyup":U=$d;break;case"focusin":H="focus",U=Da;break;case"focusout":H="blur",U=Da;break;case"beforeblur":case"afterblur":U=Da;break;case"click":if(r.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":U=il;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":U=Pd;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":U=Gd;break;case Cl:case _l:case Tl:U=Dd;break;case El:U=qd;break;case"scroll":U=Ed;break;case"wheel":U=Xd;break;case"copy":case"cut":case"paste":U=Id;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":U=ll}var G=(t&4)!==0,Me=!G&&e==="scroll",x=G?P!==null?P+"Capture":null:P;G=[];for(var v=w,k;v!==null;){k=v;var F=k.stateNode;if(k.tag===5&&F!==null&&(k=F,x!==null&&(F=er(v,x),F!=null&&G.push(xr(v,F,k)))),Me)break;v=v.return}0<G.length&&(P=new U(P,H,null,r,A),D.push({event:P,listeners:G}))}}if((t&7)===0){e:{if(P=e==="mouseover"||e==="pointerover",U=e==="mouseout"||e==="pointerout",P&&r!==ga&&(H=r.relatedTarget||r.fromElement)&&(cn(H)||H[Lt]))break e;if((U||P)&&(P=A.window===A?A:(P=A.ownerDocument)?P.defaultView||P.parentWindow:window,U?(H=r.relatedTarget||r.toElement,U=w,H=H?cn(H):null,H!==null&&(Me=ln(H),H!==Me||H.tag!==5&&H.tag!==6)&&(H=null)):(U=null,H=w),U!==H)){if(G=il,F="onMouseLeave",x="onMouseEnter",v="mouse",(e==="pointerout"||e==="pointerover")&&(G=ll,F="onPointerLeave",x="onPointerEnter",v="pointer"),Me=U==null?P:Rn(U),k=H==null?P:Rn(H),P=new G(F,v+"leave",U,r,A),P.target=Me,P.relatedTarget=k,F=null,cn(A)===w&&(G=new G(x,v+"enter",H,r,A),G.target=k,G.relatedTarget=Me,F=G),Me=F,U&&H)t:{for(G=U,x=H,v=0,k=G;k;k=An(k))v++;for(k=0,F=x;F;F=An(F))k++;for(;0<v-k;)G=An(G),v--;for(;0<k-v;)x=An(x),k--;for(;v--;){if(G===x||x!==null&&G===x.alternate)break t;G=An(G),x=An(x)}G=null}else G=null;U!==null&&Rl(D,P,U,G,!1),H!==null&&Me!==null&&Rl(D,Me,H,G,!0)}}e:{if(P=w?Rn(w):window,U=P.nodeName&&P.nodeName.toLowerCase(),U==="select"||U==="input"&&P.type==="file")var q=rm;else if(pl(P))if(gl)q=om;else{q=am;var X=sm}else(U=P.nodeName)&&U.toLowerCase()==="input"&&(P.type==="checkbox"||P.type==="radio")&&(q=im);if(q&&(q=q(e,w))){fl(D,q,r,A);break e}X&&X(e,P,w),e==="focusout"&&(X=P._wrapperState)&&X.controlled&&P.type==="number"&&da(P,"number",P.value)}switch(X=w?Rn(w):window,e){case"focusin":(pl(X)||X.contentEditable==="true")&&(Pn=X,Oa=w,gr=null);break;case"focusout":gr=Oa=Pn=null;break;case"mousedown":Ua=!0;break;case"contextmenu":case"mouseup":case"dragend":Ua=!1,Sl(D,r,A);break;case"selectionchange":if(um)break;case"keydown":case"keyup":Sl(D,r,A)}var Y;if(Ia)e:{switch(e){case"compositionstart":var te="onCompositionStart";break e;case"compositionend":te="onCompositionEnd";break e;case"compositionupdate":te="onCompositionUpdate";break e}te=void 0}else Mn?ml(e,r)&&(te="onCompositionEnd"):e==="keydown"&&r.keyCode===229&&(te="onCompositionStart");te&&(cl&&r.locale!=="ko"&&(Mn||te!=="onCompositionStart"?te==="onCompositionEnd"&&Mn&&(Y=sl()):(Vt=A,Ma="value"in Vt?Vt.value:Vt.textContent,Mn=!0)),X=as(w,te),0<X.length&&(te=new ol(te,e,null,r,A),D.push({event:te,listeners:X}),Y?te.data=Y:(Y=hl(r),Y!==null&&(te.data=Y)))),(Y=Jd?Zd(e,r):em(e,r))&&(w=as(w,"onBeforeInput"),0<w.length&&(A=new ol("onBeforeInput","beforeinput",null,r,A),D.push({event:A,listeners:w}),A.data=Y))}Al(D,t)})}function xr(e,t,r){return{instance:e,listener:t,currentTarget:r}}function as(e,t){for(var r=t+"Capture",s=[];e!==null;){var a=e,o=a.stateNode;a.tag===5&&o!==null&&(a=o,o=er(e,r),o!=null&&s.unshift(xr(e,o,a)),o=er(e,t),o!=null&&s.push(xr(e,o,a))),e=e.return}return s}function An(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function Rl(e,t,r,s,a){for(var o=t._reactName,u=[];r!==null&&r!==s;){var h=r,f=h.alternate,w=h.stateNode;if(f!==null&&f===s)break;h.tag===5&&w!==null&&(h=w,a?(f=er(r,o),f!=null&&u.unshift(xr(r,f,h))):a||(f=er(r,o),f!=null&&u.push(xr(r,f,h)))),r=r.return}u.length!==0&&e.push({event:t,listeners:u})}var pm=/\r\n?/g,fm=/\u0000|\uFFFD/g;function Il(e){return(typeof e=="string"?e:""+e).replace(pm,`
`).replace(fm,"")}function is(e,t,r){if(t=Il(t),Il(e)!==t&&r)throw Error(c(425))}function os(){}var Ka=null,qa=null;function Qa(e,t){return e==="textarea"||e==="noscript"||typeof t.children=="string"||typeof t.children=="number"||typeof t.dangerouslySetInnerHTML=="object"&&t.dangerouslySetInnerHTML!==null&&t.dangerouslySetInnerHTML.__html!=null}var Xa=typeof setTimeout=="function"?setTimeout:void 0,gm=typeof clearTimeout=="function"?clearTimeout:void 0,zl=typeof Promise=="function"?Promise:void 0,vm=typeof queueMicrotask=="function"?queueMicrotask:typeof zl<"u"?function(e){return zl.resolve(null).then(e).catch(ym)}:Xa;function ym(e){setTimeout(function(){throw e})}function Ya(e,t){var r=t,s=0;do{var a=r.nextSibling;if(e.removeChild(r),a&&a.nodeType===8)if(r=a.data,r==="/$"){if(s===0){e.removeChild(a),cr(t);return}s--}else r!=="$"&&r!=="$?"&&r!=="$!"||s++;r=a}while(r);cr(t)}function Gt(e){for(;e!=null;e=e.nextSibling){var t=e.nodeType;if(t===1||t===3)break;if(t===8){if(t=e.data,t==="$"||t==="$!"||t==="$?")break;if(t==="/$")return null}}return e}function Fl(e){e=e.previousSibling;for(var t=0;e;){if(e.nodeType===8){var r=e.data;if(r==="$"||r==="$!"||r==="$?"){if(t===0)return e;t--}else r==="/$"&&t++}e=e.previousSibling}return null}var Dn=Math.random().toString(36).slice(2),_t="__reactFiber$"+Dn,kr="__reactProps$"+Dn,Lt="__reactContainer$"+Dn,Ja="__reactEvents$"+Dn,xm="__reactListeners$"+Dn,km="__reactHandles$"+Dn;function cn(e){var t=e[_t];if(t)return t;for(var r=e.parentNode;r;){if(t=r[Lt]||r[_t]){if(r=t.alternate,t.child!==null||r!==null&&r.child!==null)for(e=Fl(e);e!==null;){if(r=e[_t])return r;e=Fl(e)}return t}e=r,r=e.parentNode}return null}function wr(e){return e=e[_t]||e[Lt],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function Rn(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(c(33))}function ls(e){return e[kr]||null}var Za=[],In=-1;function Kt(e){return{current:e}}function ke(e){0>In||(e.current=Za[In],Za[In]=null,In--)}function ye(e,t){In++,Za[In]=e.current,e.current=t}var qt={},Ge=Kt(qt),et=Kt(!1),un=qt;function zn(e,t){var r=e.type.contextTypes;if(!r)return qt;var s=e.stateNode;if(s&&s.__reactInternalMemoizedUnmaskedChildContext===t)return s.__reactInternalMemoizedMaskedChildContext;var a={},o;for(o in r)a[o]=t[o];return s&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=t,e.__reactInternalMemoizedMaskedChildContext=a),a}function tt(e){return e=e.childContextTypes,e!=null}function cs(){ke(et),ke(Ge)}function Bl(e,t,r){if(Ge.current!==qt)throw Error(c(168));ye(Ge,t),ye(et,r)}function Ol(e,t,r){var s=e.stateNode;if(t=t.childContextTypes,typeof s.getChildContext!="function")return r;s=s.getChildContext();for(var a in s)if(!(a in t))throw Error(c(108,ve(e)||"Unknown",a));return $({},r,s)}function us(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||qt,un=Ge.current,ye(Ge,e),ye(et,et.current),!0}function Ul(e,t,r){var s=e.stateNode;if(!s)throw Error(c(169));r?(e=Ol(e,t,un),s.__reactInternalMemoizedMergedChildContext=e,ke(et),ke(Ge),ye(Ge,e)):ke(et),ye(et,r)}var At=null,ds=!1,ei=!1;function Wl(e){At===null?At=[e]:At.push(e)}function wm(e){ds=!0,Wl(e)}function Qt(){if(!ei&&At!==null){ei=!0;var e=0,t=ge;try{var r=At;for(ge=1;e<r.length;e++){var s=r[e];do s=s(!0);while(s!==null)}At=null,ds=!1}catch(a){throw At!==null&&(At=At.slice(e+1)),Vo(ba,Qt),a}finally{ge=t,ei=!1}}return null}var Fn=[],Bn=0,ms=null,hs=0,mt=[],ht=0,dn=null,Dt=1,Rt="";function mn(e,t){Fn[Bn++]=hs,Fn[Bn++]=ms,ms=e,hs=t}function $l(e,t,r){mt[ht++]=Dt,mt[ht++]=Rt,mt[ht++]=dn,dn=e;var s=Dt;e=Rt;var a=32-yt(s)-1;s&=~(1<<a),r+=1;var o=32-yt(t)+a;if(30<o){var u=a-a%5;o=(s&(1<<u)-1).toString(32),s>>=u,a-=u,Dt=1<<32-yt(t)+a|r<<a|s,Rt=o+e}else Dt=1<<o|r<<a|s,Rt=e}function ti(e){e.return!==null&&(mn(e,1),$l(e,1,0))}function ni(e){for(;e===ms;)ms=Fn[--Bn],Fn[Bn]=null,hs=Fn[--Bn],Fn[Bn]=null;for(;e===dn;)dn=mt[--ht],mt[ht]=null,Rt=mt[--ht],mt[ht]=null,Dt=mt[--ht],mt[ht]=null}var ct=null,ut=null,be=!1,kt=null;function Vl(e,t){var r=vt(5,null,null,0);r.elementType="DELETED",r.stateNode=t,r.return=e,t=e.deletions,t===null?(e.deletions=[r],e.flags|=16):t.push(r)}function Hl(e,t){switch(e.tag){case 5:var r=e.type;return t=t.nodeType!==1||r.toLowerCase()!==t.nodeName.toLowerCase()?null:t,t!==null?(e.stateNode=t,ct=e,ut=Gt(t.firstChild),!0):!1;case 6:return t=e.pendingProps===""||t.nodeType!==3?null:t,t!==null?(e.stateNode=t,ct=e,ut=null,!0):!1;case 13:return t=t.nodeType!==8?null:t,t!==null?(r=dn!==null?{id:Dt,overflow:Rt}:null,e.memoizedState={dehydrated:t,treeContext:r,retryLane:1073741824},r=vt(18,null,null,0),r.stateNode=t,r.return=e,e.child=r,ct=e,ut=null,!0):!1;default:return!1}}function ri(e){return(e.mode&1)!==0&&(e.flags&128)===0}function si(e){if(be){var t=ut;if(t){var r=t;if(!Hl(e,t)){if(ri(e))throw Error(c(418));t=Gt(r.nextSibling);var s=ct;t&&Hl(e,t)?Vl(s,r):(e.flags=e.flags&-4097|2,be=!1,ct=e)}}else{if(ri(e))throw Error(c(418));e.flags=e.flags&-4097|2,be=!1,ct=e}}}function Gl(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;ct=e}function ps(e){if(e!==ct)return!1;if(!be)return Gl(e),be=!0,!1;var t;if((t=e.tag!==3)&&!(t=e.tag!==5)&&(t=e.type,t=t!=="head"&&t!=="body"&&!Qa(e.type,e.memoizedProps)),t&&(t=ut)){if(ri(e))throw Kl(),Error(c(418));for(;t;)Vl(e,t),t=Gt(t.nextSibling)}if(Gl(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(c(317));e:{for(e=e.nextSibling,t=0;e;){if(e.nodeType===8){var r=e.data;if(r==="/$"){if(t===0){ut=Gt(e.nextSibling);break e}t--}else r!=="$"&&r!=="$!"&&r!=="$?"||t++}e=e.nextSibling}ut=null}}else ut=ct?Gt(e.stateNode.nextSibling):null;return!0}function Kl(){for(var e=ut;e;)e=Gt(e.nextSibling)}function On(){ut=ct=null,be=!1}function ai(e){kt===null?kt=[e]:kt.push(e)}var bm=ee.ReactCurrentBatchConfig;function br(e,t,r){if(e=r.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(r._owner){if(r=r._owner,r){if(r.tag!==1)throw Error(c(309));var s=r.stateNode}if(!s)throw Error(c(147,e));var a=s,o=""+e;return t!==null&&t.ref!==null&&typeof t.ref=="function"&&t.ref._stringRef===o?t.ref:(t=function(u){var h=a.refs;u===null?delete h[o]:h[o]=u},t._stringRef=o,t)}if(typeof e!="string")throw Error(c(284));if(!r._owner)throw Error(c(290,e))}return e}function fs(e,t){throw e=Object.prototype.toString.call(t),Error(c(31,e==="[object Object]"?"object with keys {"+Object.keys(t).join(", ")+"}":e))}function ql(e){var t=e._init;return t(e._payload)}function Ql(e){function t(x,v){if(e){var k=x.deletions;k===null?(x.deletions=[v],x.flags|=16):k.push(v)}}function r(x,v){if(!e)return null;for(;v!==null;)t(x,v),v=v.sibling;return null}function s(x,v){for(x=new Map;v!==null;)v.key!==null?x.set(v.key,v):x.set(v.index,v),v=v.sibling;return x}function a(x,v){return x=rn(x,v),x.index=0,x.sibling=null,x}function o(x,v,k){return x.index=k,e?(k=x.alternate,k!==null?(k=k.index,k<v?(x.flags|=2,v):k):(x.flags|=2,v)):(x.flags|=1048576,v)}function u(x){return e&&x.alternate===null&&(x.flags|=2),x}function h(x,v,k,F){return v===null||v.tag!==6?(v=Xi(k,x.mode,F),v.return=x,v):(v=a(v,k),v.return=x,v)}function f(x,v,k,F){var q=k.type;return q===Q?A(x,v,k.props.children,F,k.key):v!==null&&(v.elementType===q||typeof q=="object"&&q!==null&&q.$$typeof===Fe&&ql(q)===v.type)?(F=a(v,k.props),F.ref=br(x,v,k),F.return=x,F):(F=Bs(k.type,k.key,k.props,null,x.mode,F),F.ref=br(x,v,k),F.return=x,F)}function w(x,v,k,F){return v===null||v.tag!==4||v.stateNode.containerInfo!==k.containerInfo||v.stateNode.implementation!==k.implementation?(v=Yi(k,x.mode,F),v.return=x,v):(v=a(v,k.children||[]),v.return=x,v)}function A(x,v,k,F,q){return v===null||v.tag!==7?(v=kn(k,x.mode,F,q),v.return=x,v):(v=a(v,k),v.return=x,v)}function D(x,v,k){if(typeof v=="string"&&v!==""||typeof v=="number")return v=Xi(""+v,x.mode,k),v.return=x,v;if(typeof v=="object"&&v!==null){switch(v.$$typeof){case se:return k=Bs(v.type,v.key,v.props,null,x.mode,k),k.ref=br(x,null,v),k.return=x,k;case B:return v=Yi(v,x.mode,k),v.return=x,v;case Fe:var F=v._init;return D(x,F(v._payload),k)}if(Yn(v)||Z(v))return v=kn(v,x.mode,k,null),v.return=x,v;fs(x,v)}return null}function P(x,v,k,F){var q=v!==null?v.key:null;if(typeof k=="string"&&k!==""||typeof k=="number")return q!==null?null:h(x,v,""+k,F);if(typeof k=="object"&&k!==null){switch(k.$$typeof){case se:return k.key===q?f(x,v,k,F):null;case B:return k.key===q?w(x,v,k,F):null;case Fe:return q=k._init,P(x,v,q(k._payload),F)}if(Yn(k)||Z(k))return q!==null?null:A(x,v,k,F,null);fs(x,k)}return null}function U(x,v,k,F,q){if(typeof F=="string"&&F!==""||typeof F=="number")return x=x.get(k)||null,h(v,x,""+F,q);if(typeof F=="object"&&F!==null){switch(F.$$typeof){case se:return x=x.get(F.key===null?k:F.key)||null,f(v,x,F,q);case B:return x=x.get(F.key===null?k:F.key)||null,w(v,x,F,q);case Fe:var X=F._init;return U(x,v,k,X(F._payload),q)}if(Yn(F)||Z(F))return x=x.get(k)||null,A(v,x,F,q,null);fs(v,F)}return null}function H(x,v,k,F){for(var q=null,X=null,Y=v,te=v=0,Ue=null;Y!==null&&te<k.length;te++){Y.index>te?(Ue=Y,Y=null):Ue=Y.sibling;var me=P(x,Y,k[te],F);if(me===null){Y===null&&(Y=Ue);break}e&&Y&&me.alternate===null&&t(x,Y),v=o(me,v,te),X===null?q=me:X.sibling=me,X=me,Y=Ue}if(te===k.length)return r(x,Y),be&&mn(x,te),q;if(Y===null){for(;te<k.length;te++)Y=D(x,k[te],F),Y!==null&&(v=o(Y,v,te),X===null?q=Y:X.sibling=Y,X=Y);return be&&mn(x,te),q}for(Y=s(x,Y);te<k.length;te++)Ue=U(Y,x,te,k[te],F),Ue!==null&&(e&&Ue.alternate!==null&&Y.delete(Ue.key===null?te:Ue.key),v=o(Ue,v,te),X===null?q=Ue:X.sibling=Ue,X=Ue);return e&&Y.forEach(function(sn){return t(x,sn)}),be&&mn(x,te),q}function G(x,v,k,F){var q=Z(k);if(typeof q!="function")throw Error(c(150));if(k=q.call(k),k==null)throw Error(c(151));for(var X=q=null,Y=v,te=v=0,Ue=null,me=k.next();Y!==null&&!me.done;te++,me=k.next()){Y.index>te?(Ue=Y,Y=null):Ue=Y.sibling;var sn=P(x,Y,me.value,F);if(sn===null){Y===null&&(Y=Ue);break}e&&Y&&sn.alternate===null&&t(x,Y),v=o(sn,v,te),X===null?q=sn:X.sibling=sn,X=sn,Y=Ue}if(me.done)return r(x,Y),be&&mn(x,te),q;if(Y===null){for(;!me.done;te++,me=k.next())me=D(x,me.value,F),me!==null&&(v=o(me,v,te),X===null?q=me:X.sibling=me,X=me);return be&&mn(x,te),q}for(Y=s(x,Y);!me.done;te++,me=k.next())me=U(Y,x,te,me.value,F),me!==null&&(e&&me.alternate!==null&&Y.delete(me.key===null?te:me.key),v=o(me,v,te),X===null?q=me:X.sibling=me,X=me);return e&&Y.forEach(function(th){return t(x,th)}),be&&mn(x,te),q}function Me(x,v,k,F){if(typeof k=="object"&&k!==null&&k.type===Q&&k.key===null&&(k=k.props.children),typeof k=="object"&&k!==null){switch(k.$$typeof){case se:e:{for(var q=k.key,X=v;X!==null;){if(X.key===q){if(q=k.type,q===Q){if(X.tag===7){r(x,X.sibling),v=a(X,k.props.children),v.return=x,x=v;break e}}else if(X.elementType===q||typeof q=="object"&&q!==null&&q.$$typeof===Fe&&ql(q)===X.type){r(x,X.sibling),v=a(X,k.props),v.ref=br(x,X,k),v.return=x,x=v;break e}r(x,X);break}else t(x,X);X=X.sibling}k.type===Q?(v=kn(k.props.children,x.mode,F,k.key),v.return=x,x=v):(F=Bs(k.type,k.key,k.props,null,x.mode,F),F.ref=br(x,v,k),F.return=x,x=F)}return u(x);case B:e:{for(X=k.key;v!==null;){if(v.key===X)if(v.tag===4&&v.stateNode.containerInfo===k.containerInfo&&v.stateNode.implementation===k.implementation){r(x,v.sibling),v=a(v,k.children||[]),v.return=x,x=v;break e}else{r(x,v);break}else t(x,v);v=v.sibling}v=Yi(k,x.mode,F),v.return=x,x=v}return u(x);case Fe:return X=k._init,Me(x,v,X(k._payload),F)}if(Yn(k))return H(x,v,k,F);if(Z(k))return G(x,v,k,F);fs(x,k)}return typeof k=="string"&&k!==""||typeof k=="number"?(k=""+k,v!==null&&v.tag===6?(r(x,v.sibling),v=a(v,k),v.return=x,x=v):(r(x,v),v=Xi(k,x.mode,F),v.return=x,x=v),u(x)):r(x,v)}return Me}var Un=Ql(!0),Xl=Ql(!1),gs=Kt(null),vs=null,Wn=null,ii=null;function oi(){ii=Wn=vs=null}function li(e){var t=gs.current;ke(gs),e._currentValue=t}function ci(e,t,r){for(;e!==null;){var s=e.alternate;if((e.childLanes&t)!==t?(e.childLanes|=t,s!==null&&(s.childLanes|=t)):s!==null&&(s.childLanes&t)!==t&&(s.childLanes|=t),e===r)break;e=e.return}}function $n(e,t){vs=e,ii=Wn=null,e=e.dependencies,e!==null&&e.firstContext!==null&&((e.lanes&t)!==0&&(nt=!0),e.firstContext=null)}function pt(e){var t=e._currentValue;if(ii!==e)if(e={context:e,memoizedValue:t,next:null},Wn===null){if(vs===null)throw Error(c(308));Wn=e,vs.dependencies={lanes:0,firstContext:e}}else Wn=Wn.next=e;return t}var hn=null;function ui(e){hn===null?hn=[e]:hn.push(e)}function Yl(e,t,r,s){var a=t.interleaved;return a===null?(r.next=r,ui(t)):(r.next=a.next,a.next=r),t.interleaved=r,It(e,s)}function It(e,t){e.lanes|=t;var r=e.alternate;for(r!==null&&(r.lanes|=t),r=e,e=e.return;e!==null;)e.childLanes|=t,r=e.alternate,r!==null&&(r.childLanes|=t),r=e,e=e.return;return r.tag===3?r.stateNode:null}var Xt=!1;function di(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function Jl(e,t){e=e.updateQueue,t.updateQueue===e&&(t.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function zt(e,t){return{eventTime:e,lane:t,tag:0,payload:null,callback:null,next:null}}function Yt(e,t,r){var s=e.updateQueue;if(s===null)return null;if(s=s.shared,(ce&2)!==0){var a=s.pending;return a===null?t.next=t:(t.next=a.next,a.next=t),s.pending=t,It(e,r)}return a=s.interleaved,a===null?(t.next=t,ui(s)):(t.next=a.next,a.next=t),s.interleaved=t,It(e,r)}function ys(e,t,r){if(t=t.updateQueue,t!==null&&(t=t.shared,(r&4194240)!==0)){var s=t.lanes;s&=e.pendingLanes,r|=s,t.lanes=r,Na(e,r)}}function Zl(e,t){var r=e.updateQueue,s=e.alternate;if(s!==null&&(s=s.updateQueue,r===s)){var a=null,o=null;if(r=r.firstBaseUpdate,r!==null){do{var u={eventTime:r.eventTime,lane:r.lane,tag:r.tag,payload:r.payload,callback:r.callback,next:null};o===null?a=o=u:o=o.next=u,r=r.next}while(r!==null);o===null?a=o=t:o=o.next=t}else a=o=t;r={baseState:s.baseState,firstBaseUpdate:a,lastBaseUpdate:o,shared:s.shared,effects:s.effects},e.updateQueue=r;return}e=r.lastBaseUpdate,e===null?r.firstBaseUpdate=t:e.next=t,r.lastBaseUpdate=t}function xs(e,t,r,s){var a=e.updateQueue;Xt=!1;var o=a.firstBaseUpdate,u=a.lastBaseUpdate,h=a.shared.pending;if(h!==null){a.shared.pending=null;var f=h,w=f.next;f.next=null,u===null?o=w:u.next=w,u=f;var A=e.alternate;A!==null&&(A=A.updateQueue,h=A.lastBaseUpdate,h!==u&&(h===null?A.firstBaseUpdate=w:h.next=w,A.lastBaseUpdate=f))}if(o!==null){var D=a.baseState;u=0,A=w=f=null,h=o;do{var P=h.lane,U=h.eventTime;if((s&P)===P){A!==null&&(A=A.next={eventTime:U,lane:0,tag:h.tag,payload:h.payload,callback:h.callback,next:null});e:{var H=e,G=h;switch(P=t,U=r,G.tag){case 1:if(H=G.payload,typeof H=="function"){D=H.call(U,D,P);break e}D=H;break e;case 3:H.flags=H.flags&-65537|128;case 0:if(H=G.payload,P=typeof H=="function"?H.call(U,D,P):H,P==null)break e;D=$({},D,P);break e;case 2:Xt=!0}}h.callback!==null&&h.lane!==0&&(e.flags|=64,P=a.effects,P===null?a.effects=[h]:P.push(h))}else U={eventTime:U,lane:P,tag:h.tag,payload:h.payload,callback:h.callback,next:null},A===null?(w=A=U,f=D):A=A.next=U,u|=P;if(h=h.next,h===null){if(h=a.shared.pending,h===null)break;P=h,h=P.next,P.next=null,a.lastBaseUpdate=P,a.shared.pending=null}}while(!0);if(A===null&&(f=D),a.baseState=f,a.firstBaseUpdate=w,a.lastBaseUpdate=A,t=a.shared.interleaved,t!==null){a=t;do u|=a.lane,a=a.next;while(a!==t)}else o===null&&(a.shared.lanes=0);gn|=u,e.lanes=u,e.memoizedState=D}}function ec(e,t,r){if(e=t.effects,t.effects=null,e!==null)for(t=0;t<e.length;t++){var s=e[t],a=s.callback;if(a!==null){if(s.callback=null,s=r,typeof a!="function")throw Error(c(191,a));a.call(s)}}}var jr={},Tt=Kt(jr),Sr=Kt(jr),Nr=Kt(jr);function pn(e){if(e===jr)throw Error(c(174));return e}function mi(e,t){switch(ye(Nr,t),ye(Sr,e),ye(Tt,jr),e=t.nodeType,e){case 9:case 11:t=(t=t.documentElement)?t.namespaceURI:ha(null,"");break;default:e=e===8?t.parentNode:t,t=e.namespaceURI||null,e=e.tagName,t=ha(t,e)}ke(Tt),ye(Tt,t)}function Vn(){ke(Tt),ke(Sr),ke(Nr)}function tc(e){pn(Nr.current);var t=pn(Tt.current),r=ha(t,e.type);t!==r&&(ye(Sr,e),ye(Tt,r))}function hi(e){Sr.current===e&&(ke(Tt),ke(Sr))}var Ne=Kt(0);function ks(e){for(var t=e;t!==null;){if(t.tag===13){var r=t.memoizedState;if(r!==null&&(r=r.dehydrated,r===null||r.data==="$?"||r.data==="$!"))return t}else if(t.tag===19&&t.memoizedProps.revealOrder!==void 0){if((t.flags&128)!==0)return t}else if(t.child!==null){t.child.return=t,t=t.child;continue}if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return null;t=t.return}t.sibling.return=t.return,t=t.sibling}return null}var pi=[];function fi(){for(var e=0;e<pi.length;e++)pi[e]._workInProgressVersionPrimary=null;pi.length=0}var ws=ee.ReactCurrentDispatcher,gi=ee.ReactCurrentBatchConfig,fn=0,Ce=null,Re=null,Be=null,bs=!1,Cr=!1,_r=0,jm=0;function Ke(){throw Error(c(321))}function vi(e,t){if(t===null)return!1;for(var r=0;r<t.length&&r<e.length;r++)if(!xt(e[r],t[r]))return!1;return!0}function yi(e,t,r,s,a,o){if(fn=o,Ce=t,t.memoizedState=null,t.updateQueue=null,t.lanes=0,ws.current=e===null||e.memoizedState===null?_m:Tm,e=r(s,a),Cr){o=0;do{if(Cr=!1,_r=0,25<=o)throw Error(c(301));o+=1,Be=Re=null,t.updateQueue=null,ws.current=Em,e=r(s,a)}while(Cr)}if(ws.current=Ns,t=Re!==null&&Re.next!==null,fn=0,Be=Re=Ce=null,bs=!1,t)throw Error(c(300));return e}function xi(){var e=_r!==0;return _r=0,e}function Et(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return Be===null?Ce.memoizedState=Be=e:Be=Be.next=e,Be}function ft(){if(Re===null){var e=Ce.alternate;e=e!==null?e.memoizedState:null}else e=Re.next;var t=Be===null?Ce.memoizedState:Be.next;if(t!==null)Be=t,Re=e;else{if(e===null)throw Error(c(310));Re=e,e={memoizedState:Re.memoizedState,baseState:Re.baseState,baseQueue:Re.baseQueue,queue:Re.queue,next:null},Be===null?Ce.memoizedState=Be=e:Be=Be.next=e}return Be}function Tr(e,t){return typeof t=="function"?t(e):t}function ki(e){var t=ft(),r=t.queue;if(r===null)throw Error(c(311));r.lastRenderedReducer=e;var s=Re,a=s.baseQueue,o=r.pending;if(o!==null){if(a!==null){var u=a.next;a.next=o.next,o.next=u}s.baseQueue=a=o,r.pending=null}if(a!==null){o=a.next,s=s.baseState;var h=u=null,f=null,w=o;do{var A=w.lane;if((fn&A)===A)f!==null&&(f=f.next={lane:0,action:w.action,hasEagerState:w.hasEagerState,eagerState:w.eagerState,next:null}),s=w.hasEagerState?w.eagerState:e(s,w.action);else{var D={lane:A,action:w.action,hasEagerState:w.hasEagerState,eagerState:w.eagerState,next:null};f===null?(h=f=D,u=s):f=f.next=D,Ce.lanes|=A,gn|=A}w=w.next}while(w!==null&&w!==o);f===null?u=s:f.next=h,xt(s,t.memoizedState)||(nt=!0),t.memoizedState=s,t.baseState=u,t.baseQueue=f,r.lastRenderedState=s}if(e=r.interleaved,e!==null){a=e;do o=a.lane,Ce.lanes|=o,gn|=o,a=a.next;while(a!==e)}else a===null&&(r.lanes=0);return[t.memoizedState,r.dispatch]}function wi(e){var t=ft(),r=t.queue;if(r===null)throw Error(c(311));r.lastRenderedReducer=e;var s=r.dispatch,a=r.pending,o=t.memoizedState;if(a!==null){r.pending=null;var u=a=a.next;do o=e(o,u.action),u=u.next;while(u!==a);xt(o,t.memoizedState)||(nt=!0),t.memoizedState=o,t.baseQueue===null&&(t.baseState=o),r.lastRenderedState=o}return[o,s]}function nc(){}function rc(e,t){var r=Ce,s=ft(),a=t(),o=!xt(s.memoizedState,a);if(o&&(s.memoizedState=a,nt=!0),s=s.queue,bi(ic.bind(null,r,s,e),[e]),s.getSnapshot!==t||o||Be!==null&&Be.memoizedState.tag&1){if(r.flags|=2048,Er(9,ac.bind(null,r,s,a,t),void 0,null),Oe===null)throw Error(c(349));(fn&30)!==0||sc(r,t,a)}return a}function sc(e,t,r){e.flags|=16384,e={getSnapshot:t,value:r},t=Ce.updateQueue,t===null?(t={lastEffect:null,stores:null},Ce.updateQueue=t,t.stores=[e]):(r=t.stores,r===null?t.stores=[e]:r.push(e))}function ac(e,t,r,s){t.value=r,t.getSnapshot=s,oc(t)&&lc(e)}function ic(e,t,r){return r(function(){oc(t)&&lc(e)})}function oc(e){var t=e.getSnapshot;e=e.value;try{var r=t();return!xt(e,r)}catch{return!0}}function lc(e){var t=It(e,1);t!==null&&St(t,e,1,-1)}function cc(e){var t=Et();return typeof e=="function"&&(e=e()),t.memoizedState=t.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:Tr,lastRenderedState:e},t.queue=e,e=e.dispatch=Cm.bind(null,Ce,e),[t.memoizedState,e]}function Er(e,t,r,s){return e={tag:e,create:t,destroy:r,deps:s,next:null},t=Ce.updateQueue,t===null?(t={lastEffect:null,stores:null},Ce.updateQueue=t,t.lastEffect=e.next=e):(r=t.lastEffect,r===null?t.lastEffect=e.next=e:(s=r.next,r.next=e,e.next=s,t.lastEffect=e)),e}function uc(){return ft().memoizedState}function js(e,t,r,s){var a=Et();Ce.flags|=e,a.memoizedState=Er(1|t,r,void 0,s===void 0?null:s)}function Ss(e,t,r,s){var a=ft();s=s===void 0?null:s;var o=void 0;if(Re!==null){var u=Re.memoizedState;if(o=u.destroy,s!==null&&vi(s,u.deps)){a.memoizedState=Er(t,r,o,s);return}}Ce.flags|=e,a.memoizedState=Er(1|t,r,o,s)}function dc(e,t){return js(8390656,8,e,t)}function bi(e,t){return Ss(2048,8,e,t)}function mc(e,t){return Ss(4,2,e,t)}function hc(e,t){return Ss(4,4,e,t)}function pc(e,t){if(typeof t=="function")return e=e(),t(e),function(){t(null)};if(t!=null)return e=e(),t.current=e,function(){t.current=null}}function fc(e,t,r){return r=r!=null?r.concat([e]):null,Ss(4,4,pc.bind(null,t,e),r)}function ji(){}function gc(e,t){var r=ft();t=t===void 0?null:t;var s=r.memoizedState;return s!==null&&t!==null&&vi(t,s[1])?s[0]:(r.memoizedState=[e,t],e)}function vc(e,t){var r=ft();t=t===void 0?null:t;var s=r.memoizedState;return s!==null&&t!==null&&vi(t,s[1])?s[0]:(e=e(),r.memoizedState=[e,t],e)}function yc(e,t,r){return(fn&21)===0?(e.baseState&&(e.baseState=!1,nt=!0),e.memoizedState=r):(xt(r,t)||(r=qo(),Ce.lanes|=r,gn|=r,e.baseState=!0),t)}function Sm(e,t){var r=ge;ge=r!==0&&4>r?r:4,e(!0);var s=gi.transition;gi.transition={};try{e(!1),t()}finally{ge=r,gi.transition=s}}function xc(){return ft().memoizedState}function Nm(e,t,r){var s=tn(e);if(r={lane:s,action:r,hasEagerState:!1,eagerState:null,next:null},kc(e))wc(t,r);else if(r=Yl(e,t,r,s),r!==null){var a=Ye();St(r,e,s,a),bc(r,t,s)}}function Cm(e,t,r){var s=tn(e),a={lane:s,action:r,hasEagerState:!1,eagerState:null,next:null};if(kc(e))wc(t,a);else{var o=e.alternate;if(e.lanes===0&&(o===null||o.lanes===0)&&(o=t.lastRenderedReducer,o!==null))try{var u=t.lastRenderedState,h=o(u,r);if(a.hasEagerState=!0,a.eagerState=h,xt(h,u)){var f=t.interleaved;f===null?(a.next=a,ui(t)):(a.next=f.next,f.next=a),t.interleaved=a;return}}catch{}finally{}r=Yl(e,t,a,s),r!==null&&(a=Ye(),St(r,e,s,a),bc(r,t,s))}}function kc(e){var t=e.alternate;return e===Ce||t!==null&&t===Ce}function wc(e,t){Cr=bs=!0;var r=e.pending;r===null?t.next=t:(t.next=r.next,r.next=t),e.pending=t}function bc(e,t,r){if((r&4194240)!==0){var s=t.lanes;s&=e.pendingLanes,r|=s,t.lanes=r,Na(e,r)}}var Ns={readContext:pt,useCallback:Ke,useContext:Ke,useEffect:Ke,useImperativeHandle:Ke,useInsertionEffect:Ke,useLayoutEffect:Ke,useMemo:Ke,useReducer:Ke,useRef:Ke,useState:Ke,useDebugValue:Ke,useDeferredValue:Ke,useTransition:Ke,useMutableSource:Ke,useSyncExternalStore:Ke,useId:Ke,unstable_isNewReconciler:!1},_m={readContext:pt,useCallback:function(e,t){return Et().memoizedState=[e,t===void 0?null:t],e},useContext:pt,useEffect:dc,useImperativeHandle:function(e,t,r){return r=r!=null?r.concat([e]):null,js(4194308,4,pc.bind(null,t,e),r)},useLayoutEffect:function(e,t){return js(4194308,4,e,t)},useInsertionEffect:function(e,t){return js(4,2,e,t)},useMemo:function(e,t){var r=Et();return t=t===void 0?null:t,e=e(),r.memoizedState=[e,t],e},useReducer:function(e,t,r){var s=Et();return t=r!==void 0?r(t):t,s.memoizedState=s.baseState=t,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:t},s.queue=e,e=e.dispatch=Nm.bind(null,Ce,e),[s.memoizedState,e]},useRef:function(e){var t=Et();return e={current:e},t.memoizedState=e},useState:cc,useDebugValue:ji,useDeferredValue:function(e){return Et().memoizedState=e},useTransition:function(){var e=cc(!1),t=e[0];return e=Sm.bind(null,e[1]),Et().memoizedState=e,[t,e]},useMutableSource:function(){},useSyncExternalStore:function(e,t,r){var s=Ce,a=Et();if(be){if(r===void 0)throw Error(c(407));r=r()}else{if(r=t(),Oe===null)throw Error(c(349));(fn&30)!==0||sc(s,t,r)}a.memoizedState=r;var o={value:r,getSnapshot:t};return a.queue=o,dc(ic.bind(null,s,o,e),[e]),s.flags|=2048,Er(9,ac.bind(null,s,o,r,t),void 0,null),r},useId:function(){var e=Et(),t=Oe.identifierPrefix;if(be){var r=Rt,s=Dt;r=(s&~(1<<32-yt(s)-1)).toString(32)+r,t=":"+t+"R"+r,r=_r++,0<r&&(t+="H"+r.toString(32)),t+=":"}else r=jm++,t=":"+t+"r"+r.toString(32)+":";return e.memoizedState=t},unstable_isNewReconciler:!1},Tm={readContext:pt,useCallback:gc,useContext:pt,useEffect:bi,useImperativeHandle:fc,useInsertionEffect:mc,useLayoutEffect:hc,useMemo:vc,useReducer:ki,useRef:uc,useState:function(){return ki(Tr)},useDebugValue:ji,useDeferredValue:function(e){var t=ft();return yc(t,Re.memoizedState,e)},useTransition:function(){var e=ki(Tr)[0],t=ft().memoizedState;return[e,t]},useMutableSource:nc,useSyncExternalStore:rc,useId:xc,unstable_isNewReconciler:!1},Em={readContext:pt,useCallback:gc,useContext:pt,useEffect:bi,useImperativeHandle:fc,useInsertionEffect:mc,useLayoutEffect:hc,useMemo:vc,useReducer:wi,useRef:uc,useState:function(){return wi(Tr)},useDebugValue:ji,useDeferredValue:function(e){var t=ft();return Re===null?t.memoizedState=e:yc(t,Re.memoizedState,e)},useTransition:function(){var e=wi(Tr)[0],t=ft().memoizedState;return[e,t]},useMutableSource:nc,useSyncExternalStore:rc,useId:xc,unstable_isNewReconciler:!1};function wt(e,t){if(e&&e.defaultProps){t=$({},t),e=e.defaultProps;for(var r in e)t[r]===void 0&&(t[r]=e[r]);return t}return t}function Si(e,t,r,s){t=e.memoizedState,r=r(s,t),r=r==null?t:$({},t,r),e.memoizedState=r,e.lanes===0&&(e.updateQueue.baseState=r)}var Cs={isMounted:function(e){return(e=e._reactInternals)?ln(e)===e:!1},enqueueSetState:function(e,t,r){e=e._reactInternals;var s=Ye(),a=tn(e),o=zt(s,a);o.payload=t,r!=null&&(o.callback=r),t=Yt(e,o,a),t!==null&&(St(t,e,a,s),ys(t,e,a))},enqueueReplaceState:function(e,t,r){e=e._reactInternals;var s=Ye(),a=tn(e),o=zt(s,a);o.tag=1,o.payload=t,r!=null&&(o.callback=r),t=Yt(e,o,a),t!==null&&(St(t,e,a,s),ys(t,e,a))},enqueueForceUpdate:function(e,t){e=e._reactInternals;var r=Ye(),s=tn(e),a=zt(r,s);a.tag=2,t!=null&&(a.callback=t),t=Yt(e,a,s),t!==null&&(St(t,e,s,r),ys(t,e,s))}};function jc(e,t,r,s,a,o,u){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(s,o,u):t.prototype&&t.prototype.isPureReactComponent?!fr(r,s)||!fr(a,o):!0}function Sc(e,t,r){var s=!1,a=qt,o=t.contextType;return typeof o=="object"&&o!==null?o=pt(o):(a=tt(t)?un:Ge.current,s=t.contextTypes,o=(s=s!=null)?zn(e,a):qt),t=new t(r,o),e.memoizedState=t.state!==null&&t.state!==void 0?t.state:null,t.updater=Cs,e.stateNode=t,t._reactInternals=e,s&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=a,e.__reactInternalMemoizedMaskedChildContext=o),t}function Nc(e,t,r,s){e=t.state,typeof t.componentWillReceiveProps=="function"&&t.componentWillReceiveProps(r,s),typeof t.UNSAFE_componentWillReceiveProps=="function"&&t.UNSAFE_componentWillReceiveProps(r,s),t.state!==e&&Cs.enqueueReplaceState(t,t.state,null)}function Ni(e,t,r,s){var a=e.stateNode;a.props=r,a.state=e.memoizedState,a.refs={},di(e);var o=t.contextType;typeof o=="object"&&o!==null?a.context=pt(o):(o=tt(t)?un:Ge.current,a.context=zn(e,o)),a.state=e.memoizedState,o=t.getDerivedStateFromProps,typeof o=="function"&&(Si(e,t,o,r),a.state=e.memoizedState),typeof t.getDerivedStateFromProps=="function"||typeof a.getSnapshotBeforeUpdate=="function"||typeof a.UNSAFE_componentWillMount!="function"&&typeof a.componentWillMount!="function"||(t=a.state,typeof a.componentWillMount=="function"&&a.componentWillMount(),typeof a.UNSAFE_componentWillMount=="function"&&a.UNSAFE_componentWillMount(),t!==a.state&&Cs.enqueueReplaceState(a,a.state,null),xs(e,r,a,s),a.state=e.memoizedState),typeof a.componentDidMount=="function"&&(e.flags|=4194308)}function Hn(e,t){try{var r="",s=t;do r+=ue(s),s=s.return;while(s);var a=r}catch(o){a=`
Error generating stack: `+o.message+`
`+o.stack}return{value:e,source:t,stack:a,digest:null}}function Ci(e,t,r){return{value:e,source:null,stack:r??null,digest:t??null}}function _i(e,t){try{console.error(t.value)}catch(r){setTimeout(function(){throw r})}}var Mm=typeof WeakMap=="function"?WeakMap:Map;function Cc(e,t,r){r=zt(-1,r),r.tag=3,r.payload={element:null};var s=t.value;return r.callback=function(){As||(As=!0,Wi=s),_i(e,t)},r}function _c(e,t,r){r=zt(-1,r),r.tag=3;var s=e.type.getDerivedStateFromError;if(typeof s=="function"){var a=t.value;r.payload=function(){return s(a)},r.callback=function(){_i(e,t)}}var o=e.stateNode;return o!==null&&typeof o.componentDidCatch=="function"&&(r.callback=function(){_i(e,t),typeof s!="function"&&(Zt===null?Zt=new Set([this]):Zt.add(this));var u=t.stack;this.componentDidCatch(t.value,{componentStack:u!==null?u:""})}),r}function Tc(e,t,r){var s=e.pingCache;if(s===null){s=e.pingCache=new Mm;var a=new Set;s.set(t,a)}else a=s.get(t),a===void 0&&(a=new Set,s.set(t,a));a.has(r)||(a.add(r),e=Vm.bind(null,e,t,r),t.then(e,e))}function Ec(e){do{var t;if((t=e.tag===13)&&(t=e.memoizedState,t=t!==null?t.dehydrated!==null:!0),t)return e;e=e.return}while(e!==null);return null}function Mc(e,t,r,s,a){return(e.mode&1)===0?(e===t?e.flags|=65536:(e.flags|=128,r.flags|=131072,r.flags&=-52805,r.tag===1&&(r.alternate===null?r.tag=17:(t=zt(-1,1),t.tag=2,Yt(r,t,1))),r.lanes|=1),e):(e.flags|=65536,e.lanes=a,e)}var Pm=ee.ReactCurrentOwner,nt=!1;function Xe(e,t,r,s){t.child=e===null?Xl(t,null,r,s):Un(t,e.child,r,s)}function Pc(e,t,r,s,a){r=r.render;var o=t.ref;return $n(t,a),s=yi(e,t,r,s,o,a),r=xi(),e!==null&&!nt?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~a,Ft(e,t,a)):(be&&r&&ti(t),t.flags|=1,Xe(e,t,s,a),t.child)}function Lc(e,t,r,s,a){if(e===null){var o=r.type;return typeof o=="function"&&!Qi(o)&&o.defaultProps===void 0&&r.compare===null&&r.defaultProps===void 0?(t.tag=15,t.type=o,Ac(e,t,o,s,a)):(e=Bs(r.type,null,s,t,t.mode,a),e.ref=t.ref,e.return=t,t.child=e)}if(o=e.child,(e.lanes&a)===0){var u=o.memoizedProps;if(r=r.compare,r=r!==null?r:fr,r(u,s)&&e.ref===t.ref)return Ft(e,t,a)}return t.flags|=1,e=rn(o,s),e.ref=t.ref,e.return=t,t.child=e}function Ac(e,t,r,s,a){if(e!==null){var o=e.memoizedProps;if(fr(o,s)&&e.ref===t.ref)if(nt=!1,t.pendingProps=s=o,(e.lanes&a)!==0)(e.flags&131072)!==0&&(nt=!0);else return t.lanes=e.lanes,Ft(e,t,a)}return Ti(e,t,r,s,a)}function Dc(e,t,r){var s=t.pendingProps,a=s.children,o=e!==null?e.memoizedState:null;if(s.mode==="hidden")if((t.mode&1)===0)t.memoizedState={baseLanes:0,cachePool:null,transitions:null},ye(Kn,dt),dt|=r;else{if((r&1073741824)===0)return e=o!==null?o.baseLanes|r:r,t.lanes=t.childLanes=1073741824,t.memoizedState={baseLanes:e,cachePool:null,transitions:null},t.updateQueue=null,ye(Kn,dt),dt|=e,null;t.memoizedState={baseLanes:0,cachePool:null,transitions:null},s=o!==null?o.baseLanes:r,ye(Kn,dt),dt|=s}else o!==null?(s=o.baseLanes|r,t.memoizedState=null):s=r,ye(Kn,dt),dt|=s;return Xe(e,t,a,r),t.child}function Rc(e,t){var r=t.ref;(e===null&&r!==null||e!==null&&e.ref!==r)&&(t.flags|=512,t.flags|=2097152)}function Ti(e,t,r,s,a){var o=tt(r)?un:Ge.current;return o=zn(t,o),$n(t,a),r=yi(e,t,r,s,o,a),s=xi(),e!==null&&!nt?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~a,Ft(e,t,a)):(be&&s&&ti(t),t.flags|=1,Xe(e,t,r,a),t.child)}function Ic(e,t,r,s,a){if(tt(r)){var o=!0;us(t)}else o=!1;if($n(t,a),t.stateNode===null)Ts(e,t),Sc(t,r,s),Ni(t,r,s,a),s=!0;else if(e===null){var u=t.stateNode,h=t.memoizedProps;u.props=h;var f=u.context,w=r.contextType;typeof w=="object"&&w!==null?w=pt(w):(w=tt(r)?un:Ge.current,w=zn(t,w));var A=r.getDerivedStateFromProps,D=typeof A=="function"||typeof u.getSnapshotBeforeUpdate=="function";D||typeof u.UNSAFE_componentWillReceiveProps!="function"&&typeof u.componentWillReceiveProps!="function"||(h!==s||f!==w)&&Nc(t,u,s,w),Xt=!1;var P=t.memoizedState;u.state=P,xs(t,s,u,a),f=t.memoizedState,h!==s||P!==f||et.current||Xt?(typeof A=="function"&&(Si(t,r,A,s),f=t.memoizedState),(h=Xt||jc(t,r,h,s,P,f,w))?(D||typeof u.UNSAFE_componentWillMount!="function"&&typeof u.componentWillMount!="function"||(typeof u.componentWillMount=="function"&&u.componentWillMount(),typeof u.UNSAFE_componentWillMount=="function"&&u.UNSAFE_componentWillMount()),typeof u.componentDidMount=="function"&&(t.flags|=4194308)):(typeof u.componentDidMount=="function"&&(t.flags|=4194308),t.memoizedProps=s,t.memoizedState=f),u.props=s,u.state=f,u.context=w,s=h):(typeof u.componentDidMount=="function"&&(t.flags|=4194308),s=!1)}else{u=t.stateNode,Jl(e,t),h=t.memoizedProps,w=t.type===t.elementType?h:wt(t.type,h),u.props=w,D=t.pendingProps,P=u.context,f=r.contextType,typeof f=="object"&&f!==null?f=pt(f):(f=tt(r)?un:Ge.current,f=zn(t,f));var U=r.getDerivedStateFromProps;(A=typeof U=="function"||typeof u.getSnapshotBeforeUpdate=="function")||typeof u.UNSAFE_componentWillReceiveProps!="function"&&typeof u.componentWillReceiveProps!="function"||(h!==D||P!==f)&&Nc(t,u,s,f),Xt=!1,P=t.memoizedState,u.state=P,xs(t,s,u,a);var H=t.memoizedState;h!==D||P!==H||et.current||Xt?(typeof U=="function"&&(Si(t,r,U,s),H=t.memoizedState),(w=Xt||jc(t,r,w,s,P,H,f)||!1)?(A||typeof u.UNSAFE_componentWillUpdate!="function"&&typeof u.componentWillUpdate!="function"||(typeof u.componentWillUpdate=="function"&&u.componentWillUpdate(s,H,f),typeof u.UNSAFE_componentWillUpdate=="function"&&u.UNSAFE_componentWillUpdate(s,H,f)),typeof u.componentDidUpdate=="function"&&(t.flags|=4),typeof u.getSnapshotBeforeUpdate=="function"&&(t.flags|=1024)):(typeof u.componentDidUpdate!="function"||h===e.memoizedProps&&P===e.memoizedState||(t.flags|=4),typeof u.getSnapshotBeforeUpdate!="function"||h===e.memoizedProps&&P===e.memoizedState||(t.flags|=1024),t.memoizedProps=s,t.memoizedState=H),u.props=s,u.state=H,u.context=f,s=w):(typeof u.componentDidUpdate!="function"||h===e.memoizedProps&&P===e.memoizedState||(t.flags|=4),typeof u.getSnapshotBeforeUpdate!="function"||h===e.memoizedProps&&P===e.memoizedState||(t.flags|=1024),s=!1)}return Ei(e,t,r,s,o,a)}function Ei(e,t,r,s,a,o){Rc(e,t);var u=(t.flags&128)!==0;if(!s&&!u)return a&&Ul(t,r,!1),Ft(e,t,o);s=t.stateNode,Pm.current=t;var h=u&&typeof r.getDerivedStateFromError!="function"?null:s.render();return t.flags|=1,e!==null&&u?(t.child=Un(t,e.child,null,o),t.child=Un(t,null,h,o)):Xe(e,t,h,o),t.memoizedState=s.state,a&&Ul(t,r,!0),t.child}function zc(e){var t=e.stateNode;t.pendingContext?Bl(e,t.pendingContext,t.pendingContext!==t.context):t.context&&Bl(e,t.context,!1),mi(e,t.containerInfo)}function Fc(e,t,r,s,a){return On(),ai(a),t.flags|=256,Xe(e,t,r,s),t.child}var Mi={dehydrated:null,treeContext:null,retryLane:0};function Pi(e){return{baseLanes:e,cachePool:null,transitions:null}}function Bc(e,t,r){var s=t.pendingProps,a=Ne.current,o=!1,u=(t.flags&128)!==0,h;if((h=u)||(h=e!==null&&e.memoizedState===null?!1:(a&2)!==0),h?(o=!0,t.flags&=-129):(e===null||e.memoizedState!==null)&&(a|=1),ye(Ne,a&1),e===null)return si(t),e=t.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?((t.mode&1)===0?t.lanes=1:e.data==="$!"?t.lanes=8:t.lanes=1073741824,null):(u=s.children,e=s.fallback,o?(s=t.mode,o=t.child,u={mode:"hidden",children:u},(s&1)===0&&o!==null?(o.childLanes=0,o.pendingProps=u):o=Os(u,s,0,null),e=kn(e,s,r,null),o.return=t,e.return=t,o.sibling=e,t.child=o,t.child.memoizedState=Pi(r),t.memoizedState=Mi,e):Li(t,u));if(a=e.memoizedState,a!==null&&(h=a.dehydrated,h!==null))return Lm(e,t,u,s,h,a,r);if(o){o=s.fallback,u=t.mode,a=e.child,h=a.sibling;var f={mode:"hidden",children:s.children};return(u&1)===0&&t.child!==a?(s=t.child,s.childLanes=0,s.pendingProps=f,t.deletions=null):(s=rn(a,f),s.subtreeFlags=a.subtreeFlags&14680064),h!==null?o=rn(h,o):(o=kn(o,u,r,null),o.flags|=2),o.return=t,s.return=t,s.sibling=o,t.child=s,s=o,o=t.child,u=e.child.memoizedState,u=u===null?Pi(r):{baseLanes:u.baseLanes|r,cachePool:null,transitions:u.transitions},o.memoizedState=u,o.childLanes=e.childLanes&~r,t.memoizedState=Mi,s}return o=e.child,e=o.sibling,s=rn(o,{mode:"visible",children:s.children}),(t.mode&1)===0&&(s.lanes=r),s.return=t,s.sibling=null,e!==null&&(r=t.deletions,r===null?(t.deletions=[e],t.flags|=16):r.push(e)),t.child=s,t.memoizedState=null,s}function Li(e,t){return t=Os({mode:"visible",children:t},e.mode,0,null),t.return=e,e.child=t}function _s(e,t,r,s){return s!==null&&ai(s),Un(t,e.child,null,r),e=Li(t,t.pendingProps.children),e.flags|=2,t.memoizedState=null,e}function Lm(e,t,r,s,a,o,u){if(r)return t.flags&256?(t.flags&=-257,s=Ci(Error(c(422))),_s(e,t,u,s)):t.memoizedState!==null?(t.child=e.child,t.flags|=128,null):(o=s.fallback,a=t.mode,s=Os({mode:"visible",children:s.children},a,0,null),o=kn(o,a,u,null),o.flags|=2,s.return=t,o.return=t,s.sibling=o,t.child=s,(t.mode&1)!==0&&Un(t,e.child,null,u),t.child.memoizedState=Pi(u),t.memoizedState=Mi,o);if((t.mode&1)===0)return _s(e,t,u,null);if(a.data==="$!"){if(s=a.nextSibling&&a.nextSibling.dataset,s)var h=s.dgst;return s=h,o=Error(c(419)),s=Ci(o,s,void 0),_s(e,t,u,s)}if(h=(u&e.childLanes)!==0,nt||h){if(s=Oe,s!==null){switch(u&-u){case 4:a=2;break;case 16:a=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:a=32;break;case 536870912:a=268435456;break;default:a=0}a=(a&(s.suspendedLanes|u))!==0?0:a,a!==0&&a!==o.retryLane&&(o.retryLane=a,It(e,a),St(s,e,a,-1))}return qi(),s=Ci(Error(c(421))),_s(e,t,u,s)}return a.data==="$?"?(t.flags|=128,t.child=e.child,t=Hm.bind(null,e),a._reactRetry=t,null):(e=o.treeContext,ut=Gt(a.nextSibling),ct=t,be=!0,kt=null,e!==null&&(mt[ht++]=Dt,mt[ht++]=Rt,mt[ht++]=dn,Dt=e.id,Rt=e.overflow,dn=t),t=Li(t,s.children),t.flags|=4096,t)}function Oc(e,t,r){e.lanes|=t;var s=e.alternate;s!==null&&(s.lanes|=t),ci(e.return,t,r)}function Ai(e,t,r,s,a){var o=e.memoizedState;o===null?e.memoizedState={isBackwards:t,rendering:null,renderingStartTime:0,last:s,tail:r,tailMode:a}:(o.isBackwards=t,o.rendering=null,o.renderingStartTime=0,o.last=s,o.tail=r,o.tailMode=a)}function Uc(e,t,r){var s=t.pendingProps,a=s.revealOrder,o=s.tail;if(Xe(e,t,s.children,r),s=Ne.current,(s&2)!==0)s=s&1|2,t.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=t.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Oc(e,r,t);else if(e.tag===19)Oc(e,r,t);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===t)break e;for(;e.sibling===null;){if(e.return===null||e.return===t)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}s&=1}if(ye(Ne,s),(t.mode&1)===0)t.memoizedState=null;else switch(a){case"forwards":for(r=t.child,a=null;r!==null;)e=r.alternate,e!==null&&ks(e)===null&&(a=r),r=r.sibling;r=a,r===null?(a=t.child,t.child=null):(a=r.sibling,r.sibling=null),Ai(t,!1,a,r,o);break;case"backwards":for(r=null,a=t.child,t.child=null;a!==null;){if(e=a.alternate,e!==null&&ks(e)===null){t.child=a;break}e=a.sibling,a.sibling=r,r=a,a=e}Ai(t,!0,r,null,o);break;case"together":Ai(t,!1,null,null,void 0);break;default:t.memoizedState=null}return t.child}function Ts(e,t){(t.mode&1)===0&&e!==null&&(e.alternate=null,t.alternate=null,t.flags|=2)}function Ft(e,t,r){if(e!==null&&(t.dependencies=e.dependencies),gn|=t.lanes,(r&t.childLanes)===0)return null;if(e!==null&&t.child!==e.child)throw Error(c(153));if(t.child!==null){for(e=t.child,r=rn(e,e.pendingProps),t.child=r,r.return=t;e.sibling!==null;)e=e.sibling,r=r.sibling=rn(e,e.pendingProps),r.return=t;r.sibling=null}return t.child}function Am(e,t,r){switch(t.tag){case 3:zc(t),On();break;case 5:tc(t);break;case 1:tt(t.type)&&us(t);break;case 4:mi(t,t.stateNode.containerInfo);break;case 10:var s=t.type._context,a=t.memoizedProps.value;ye(gs,s._currentValue),s._currentValue=a;break;case 13:if(s=t.memoizedState,s!==null)return s.dehydrated!==null?(ye(Ne,Ne.current&1),t.flags|=128,null):(r&t.child.childLanes)!==0?Bc(e,t,r):(ye(Ne,Ne.current&1),e=Ft(e,t,r),e!==null?e.sibling:null);ye(Ne,Ne.current&1);break;case 19:if(s=(r&t.childLanes)!==0,(e.flags&128)!==0){if(s)return Uc(e,t,r);t.flags|=128}if(a=t.memoizedState,a!==null&&(a.rendering=null,a.tail=null,a.lastEffect=null),ye(Ne,Ne.current),s)break;return null;case 22:case 23:return t.lanes=0,Dc(e,t,r)}return Ft(e,t,r)}var Wc,Di,$c,Vc;Wc=function(e,t){for(var r=t.child;r!==null;){if(r.tag===5||r.tag===6)e.appendChild(r.stateNode);else if(r.tag!==4&&r.child!==null){r.child.return=r,r=r.child;continue}if(r===t)break;for(;r.sibling===null;){if(r.return===null||r.return===t)return;r=r.return}r.sibling.return=r.return,r=r.sibling}},Di=function(){},$c=function(e,t,r,s){var a=e.memoizedProps;if(a!==s){e=t.stateNode,pn(Tt.current);var o=null;switch(r){case"input":a=ca(e,a),s=ca(e,s),o=[];break;case"select":a=$({},a,{value:void 0}),s=$({},s,{value:void 0}),o=[];break;case"textarea":a=ma(e,a),s=ma(e,s),o=[];break;default:typeof a.onClick!="function"&&typeof s.onClick=="function"&&(e.onclick=os)}pa(r,s);var u;r=null;for(w in a)if(!s.hasOwnProperty(w)&&a.hasOwnProperty(w)&&a[w]!=null)if(w==="style"){var h=a[w];for(u in h)h.hasOwnProperty(u)&&(r||(r={}),r[u]="")}else w!=="dangerouslySetInnerHTML"&&w!=="children"&&w!=="suppressContentEditableWarning"&&w!=="suppressHydrationWarning"&&w!=="autoFocus"&&(m.hasOwnProperty(w)?o||(o=[]):(o=o||[]).push(w,null));for(w in s){var f=s[w];if(h=a!=null?a[w]:void 0,s.hasOwnProperty(w)&&f!==h&&(f!=null||h!=null))if(w==="style")if(h){for(u in h)!h.hasOwnProperty(u)||f&&f.hasOwnProperty(u)||(r||(r={}),r[u]="");for(u in f)f.hasOwnProperty(u)&&h[u]!==f[u]&&(r||(r={}),r[u]=f[u])}else r||(o||(o=[]),o.push(w,r)),r=f;else w==="dangerouslySetInnerHTML"?(f=f?f.__html:void 0,h=h?h.__html:void 0,f!=null&&h!==f&&(o=o||[]).push(w,f)):w==="children"?typeof f!="string"&&typeof f!="number"||(o=o||[]).push(w,""+f):w!=="suppressContentEditableWarning"&&w!=="suppressHydrationWarning"&&(m.hasOwnProperty(w)?(f!=null&&w==="onScroll"&&xe("scroll",e),o||h===f||(o=[])):(o=o||[]).push(w,f))}r&&(o=o||[]).push("style",r);var w=o;(t.updateQueue=w)&&(t.flags|=4)}},Vc=function(e,t,r,s){r!==s&&(t.flags|=4)};function Mr(e,t){if(!be)switch(e.tailMode){case"hidden":t=e.tail;for(var r=null;t!==null;)t.alternate!==null&&(r=t),t=t.sibling;r===null?e.tail=null:r.sibling=null;break;case"collapsed":r=e.tail;for(var s=null;r!==null;)r.alternate!==null&&(s=r),r=r.sibling;s===null?t||e.tail===null?e.tail=null:e.tail.sibling=null:s.sibling=null}}function qe(e){var t=e.alternate!==null&&e.alternate.child===e.child,r=0,s=0;if(t)for(var a=e.child;a!==null;)r|=a.lanes|a.childLanes,s|=a.subtreeFlags&14680064,s|=a.flags&14680064,a.return=e,a=a.sibling;else for(a=e.child;a!==null;)r|=a.lanes|a.childLanes,s|=a.subtreeFlags,s|=a.flags,a.return=e,a=a.sibling;return e.subtreeFlags|=s,e.childLanes=r,t}function Dm(e,t,r){var s=t.pendingProps;switch(ni(t),t.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return qe(t),null;case 1:return tt(t.type)&&cs(),qe(t),null;case 3:return s=t.stateNode,Vn(),ke(et),ke(Ge),fi(),s.pendingContext&&(s.context=s.pendingContext,s.pendingContext=null),(e===null||e.child===null)&&(ps(t)?t.flags|=4:e===null||e.memoizedState.isDehydrated&&(t.flags&256)===0||(t.flags|=1024,kt!==null&&(Hi(kt),kt=null))),Di(e,t),qe(t),null;case 5:hi(t);var a=pn(Nr.current);if(r=t.type,e!==null&&t.stateNode!=null)$c(e,t,r,s,a),e.ref!==t.ref&&(t.flags|=512,t.flags|=2097152);else{if(!s){if(t.stateNode===null)throw Error(c(166));return qe(t),null}if(e=pn(Tt.current),ps(t)){s=t.stateNode,r=t.type;var o=t.memoizedProps;switch(s[_t]=t,s[kr]=o,e=(t.mode&1)!==0,r){case"dialog":xe("cancel",s),xe("close",s);break;case"iframe":case"object":case"embed":xe("load",s);break;case"video":case"audio":for(a=0;a<vr.length;a++)xe(vr[a],s);break;case"source":xe("error",s);break;case"img":case"image":case"link":xe("error",s),xe("load",s);break;case"details":xe("toggle",s);break;case"input":So(s,o),xe("invalid",s);break;case"select":s._wrapperState={wasMultiple:!!o.multiple},xe("invalid",s);break;case"textarea":_o(s,o),xe("invalid",s)}pa(r,o),a=null;for(var u in o)if(o.hasOwnProperty(u)){var h=o[u];u==="children"?typeof h=="string"?s.textContent!==h&&(o.suppressHydrationWarning!==!0&&is(s.textContent,h,e),a=["children",h]):typeof h=="number"&&s.textContent!==""+h&&(o.suppressHydrationWarning!==!0&&is(s.textContent,h,e),a=["children",""+h]):m.hasOwnProperty(u)&&h!=null&&u==="onScroll"&&xe("scroll",s)}switch(r){case"input":zr(s),Co(s,o,!0);break;case"textarea":zr(s),Eo(s);break;case"select":case"option":break;default:typeof o.onClick=="function"&&(s.onclick=os)}s=a,t.updateQueue=s,s!==null&&(t.flags|=4)}else{u=a.nodeType===9?a:a.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=Mo(r)),e==="http://www.w3.org/1999/xhtml"?r==="script"?(e=u.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof s.is=="string"?e=u.createElement(r,{is:s.is}):(e=u.createElement(r),r==="select"&&(u=e,s.multiple?u.multiple=!0:s.size&&(u.size=s.size))):e=u.createElementNS(e,r),e[_t]=t,e[kr]=s,Wc(e,t,!1,!1),t.stateNode=e;e:{switch(u=fa(r,s),r){case"dialog":xe("cancel",e),xe("close",e),a=s;break;case"iframe":case"object":case"embed":xe("load",e),a=s;break;case"video":case"audio":for(a=0;a<vr.length;a++)xe(vr[a],e);a=s;break;case"source":xe("error",e),a=s;break;case"img":case"image":case"link":xe("error",e),xe("load",e),a=s;break;case"details":xe("toggle",e),a=s;break;case"input":So(e,s),a=ca(e,s),xe("invalid",e);break;case"option":a=s;break;case"select":e._wrapperState={wasMultiple:!!s.multiple},a=$({},s,{value:void 0}),xe("invalid",e);break;case"textarea":_o(e,s),a=ma(e,s),xe("invalid",e);break;default:a=s}pa(r,a),h=a;for(o in h)if(h.hasOwnProperty(o)){var f=h[o];o==="style"?Ao(e,f):o==="dangerouslySetInnerHTML"?(f=f?f.__html:void 0,f!=null&&Po(e,f)):o==="children"?typeof f=="string"?(r!=="textarea"||f!=="")&&Jn(e,f):typeof f=="number"&&Jn(e,""+f):o!=="suppressContentEditableWarning"&&o!=="suppressHydrationWarning"&&o!=="autoFocus"&&(m.hasOwnProperty(o)?f!=null&&o==="onScroll"&&xe("scroll",e):f!=null&&V(e,o,f,u))}switch(r){case"input":zr(e),Co(e,s,!1);break;case"textarea":zr(e),Eo(e);break;case"option":s.value!=null&&e.setAttribute("value",""+fe(s.value));break;case"select":e.multiple=!!s.multiple,o=s.value,o!=null?Nn(e,!!s.multiple,o,!1):s.defaultValue!=null&&Nn(e,!!s.multiple,s.defaultValue,!0);break;default:typeof a.onClick=="function"&&(e.onclick=os)}switch(r){case"button":case"input":case"select":case"textarea":s=!!s.autoFocus;break e;case"img":s=!0;break e;default:s=!1}}s&&(t.flags|=4)}t.ref!==null&&(t.flags|=512,t.flags|=2097152)}return qe(t),null;case 6:if(e&&t.stateNode!=null)Vc(e,t,e.memoizedProps,s);else{if(typeof s!="string"&&t.stateNode===null)throw Error(c(166));if(r=pn(Nr.current),pn(Tt.current),ps(t)){if(s=t.stateNode,r=t.memoizedProps,s[_t]=t,(o=s.nodeValue!==r)&&(e=ct,e!==null))switch(e.tag){case 3:is(s.nodeValue,r,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&is(s.nodeValue,r,(e.mode&1)!==0)}o&&(t.flags|=4)}else s=(r.nodeType===9?r:r.ownerDocument).createTextNode(s),s[_t]=t,t.stateNode=s}return qe(t),null;case 13:if(ke(Ne),s=t.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(be&&ut!==null&&(t.mode&1)!==0&&(t.flags&128)===0)Kl(),On(),t.flags|=98560,o=!1;else if(o=ps(t),s!==null&&s.dehydrated!==null){if(e===null){if(!o)throw Error(c(318));if(o=t.memoizedState,o=o!==null?o.dehydrated:null,!o)throw Error(c(317));o[_t]=t}else On(),(t.flags&128)===0&&(t.memoizedState=null),t.flags|=4;qe(t),o=!1}else kt!==null&&(Hi(kt),kt=null),o=!0;if(!o)return t.flags&65536?t:null}return(t.flags&128)!==0?(t.lanes=r,t):(s=s!==null,s!==(e!==null&&e.memoizedState!==null)&&s&&(t.child.flags|=8192,(t.mode&1)!==0&&(e===null||(Ne.current&1)!==0?Ie===0&&(Ie=3):qi())),t.updateQueue!==null&&(t.flags|=4),qe(t),null);case 4:return Vn(),Di(e,t),e===null&&yr(t.stateNode.containerInfo),qe(t),null;case 10:return li(t.type._context),qe(t),null;case 17:return tt(t.type)&&cs(),qe(t),null;case 19:if(ke(Ne),o=t.memoizedState,o===null)return qe(t),null;if(s=(t.flags&128)!==0,u=o.rendering,u===null)if(s)Mr(o,!1);else{if(Ie!==0||e!==null&&(e.flags&128)!==0)for(e=t.child;e!==null;){if(u=ks(e),u!==null){for(t.flags|=128,Mr(o,!1),s=u.updateQueue,s!==null&&(t.updateQueue=s,t.flags|=4),t.subtreeFlags=0,s=r,r=t.child;r!==null;)o=r,e=s,o.flags&=14680066,u=o.alternate,u===null?(o.childLanes=0,o.lanes=e,o.child=null,o.subtreeFlags=0,o.memoizedProps=null,o.memoizedState=null,o.updateQueue=null,o.dependencies=null,o.stateNode=null):(o.childLanes=u.childLanes,o.lanes=u.lanes,o.child=u.child,o.subtreeFlags=0,o.deletions=null,o.memoizedProps=u.memoizedProps,o.memoizedState=u.memoizedState,o.updateQueue=u.updateQueue,o.type=u.type,e=u.dependencies,o.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),r=r.sibling;return ye(Ne,Ne.current&1|2),t.child}e=e.sibling}o.tail!==null&&Ee()>qn&&(t.flags|=128,s=!0,Mr(o,!1),t.lanes=4194304)}else{if(!s)if(e=ks(u),e!==null){if(t.flags|=128,s=!0,r=e.updateQueue,r!==null&&(t.updateQueue=r,t.flags|=4),Mr(o,!0),o.tail===null&&o.tailMode==="hidden"&&!u.alternate&&!be)return qe(t),null}else 2*Ee()-o.renderingStartTime>qn&&r!==1073741824&&(t.flags|=128,s=!0,Mr(o,!1),t.lanes=4194304);o.isBackwards?(u.sibling=t.child,t.child=u):(r=o.last,r!==null?r.sibling=u:t.child=u,o.last=u)}return o.tail!==null?(t=o.tail,o.rendering=t,o.tail=t.sibling,o.renderingStartTime=Ee(),t.sibling=null,r=Ne.current,ye(Ne,s?r&1|2:r&1),t):(qe(t),null);case 22:case 23:return Ki(),s=t.memoizedState!==null,e!==null&&e.memoizedState!==null!==s&&(t.flags|=8192),s&&(t.mode&1)!==0?(dt&1073741824)!==0&&(qe(t),t.subtreeFlags&6&&(t.flags|=8192)):qe(t),null;case 24:return null;case 25:return null}throw Error(c(156,t.tag))}function Rm(e,t){switch(ni(t),t.tag){case 1:return tt(t.type)&&cs(),e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 3:return Vn(),ke(et),ke(Ge),fi(),e=t.flags,(e&65536)!==0&&(e&128)===0?(t.flags=e&-65537|128,t):null;case 5:return hi(t),null;case 13:if(ke(Ne),e=t.memoizedState,e!==null&&e.dehydrated!==null){if(t.alternate===null)throw Error(c(340));On()}return e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 19:return ke(Ne),null;case 4:return Vn(),null;case 10:return li(t.type._context),null;case 22:case 23:return Ki(),null;case 24:return null;default:return null}}var Es=!1,Qe=!1,Im=typeof WeakSet=="function"?WeakSet:Set,W=null;function Gn(e,t){var r=e.ref;if(r!==null)if(typeof r=="function")try{r(null)}catch(s){_e(e,t,s)}else r.current=null}function Ri(e,t,r){try{r()}catch(s){_e(e,t,s)}}var Hc=!1;function zm(e,t){if(Ka=Qr,e=jl(),Ba(e)){if("selectionStart"in e)var r={start:e.selectionStart,end:e.selectionEnd};else e:{r=(r=e.ownerDocument)&&r.defaultView||window;var s=r.getSelection&&r.getSelection();if(s&&s.rangeCount!==0){r=s.anchorNode;var a=s.anchorOffset,o=s.focusNode;s=s.focusOffset;try{r.nodeType,o.nodeType}catch{r=null;break e}var u=0,h=-1,f=-1,w=0,A=0,D=e,P=null;t:for(;;){for(var U;D!==r||a!==0&&D.nodeType!==3||(h=u+a),D!==o||s!==0&&D.nodeType!==3||(f=u+s),D.nodeType===3&&(u+=D.nodeValue.length),(U=D.firstChild)!==null;)P=D,D=U;for(;;){if(D===e)break t;if(P===r&&++w===a&&(h=u),P===o&&++A===s&&(f=u),(U=D.nextSibling)!==null)break;D=P,P=D.parentNode}D=U}r=h===-1||f===-1?null:{start:h,end:f}}else r=null}r=r||{start:0,end:0}}else r=null;for(qa={focusedElem:e,selectionRange:r},Qr=!1,W=t;W!==null;)if(t=W,e=t.child,(t.subtreeFlags&1028)!==0&&e!==null)e.return=t,W=e;else for(;W!==null;){t=W;try{var H=t.alternate;if((t.flags&1024)!==0)switch(t.tag){case 0:case 11:case 15:break;case 1:if(H!==null){var G=H.memoizedProps,Me=H.memoizedState,x=t.stateNode,v=x.getSnapshotBeforeUpdate(t.elementType===t.type?G:wt(t.type,G),Me);x.__reactInternalSnapshotBeforeUpdate=v}break;case 3:var k=t.stateNode.containerInfo;k.nodeType===1?k.textContent="":k.nodeType===9&&k.documentElement&&k.removeChild(k.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(c(163))}}catch(F){_e(t,t.return,F)}if(e=t.sibling,e!==null){e.return=t.return,W=e;break}W=t.return}return H=Hc,Hc=!1,H}function Pr(e,t,r){var s=t.updateQueue;if(s=s!==null?s.lastEffect:null,s!==null){var a=s=s.next;do{if((a.tag&e)===e){var o=a.destroy;a.destroy=void 0,o!==void 0&&Ri(t,r,o)}a=a.next}while(a!==s)}}function Ms(e,t){if(t=t.updateQueue,t=t!==null?t.lastEffect:null,t!==null){var r=t=t.next;do{if((r.tag&e)===e){var s=r.create;r.destroy=s()}r=r.next}while(r!==t)}}function Ii(e){var t=e.ref;if(t!==null){var r=e.stateNode;switch(e.tag){case 5:e=r;break;default:e=r}typeof t=="function"?t(e):t.current=e}}function Gc(e){var t=e.alternate;t!==null&&(e.alternate=null,Gc(t)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(t=e.stateNode,t!==null&&(delete t[_t],delete t[kr],delete t[Ja],delete t[xm],delete t[km])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function Kc(e){return e.tag===5||e.tag===3||e.tag===4}function qc(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||Kc(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function zi(e,t,r){var s=e.tag;if(s===5||s===6)e=e.stateNode,t?r.nodeType===8?r.parentNode.insertBefore(e,t):r.insertBefore(e,t):(r.nodeType===8?(t=r.parentNode,t.insertBefore(e,r)):(t=r,t.appendChild(e)),r=r._reactRootContainer,r!=null||t.onclick!==null||(t.onclick=os));else if(s!==4&&(e=e.child,e!==null))for(zi(e,t,r),e=e.sibling;e!==null;)zi(e,t,r),e=e.sibling}function Fi(e,t,r){var s=e.tag;if(s===5||s===6)e=e.stateNode,t?r.insertBefore(e,t):r.appendChild(e);else if(s!==4&&(e=e.child,e!==null))for(Fi(e,t,r),e=e.sibling;e!==null;)Fi(e,t,r),e=e.sibling}var $e=null,bt=!1;function Jt(e,t,r){for(r=r.child;r!==null;)Qc(e,t,r),r=r.sibling}function Qc(e,t,r){if(Ct&&typeof Ct.onCommitFiberUnmount=="function")try{Ct.onCommitFiberUnmount($r,r)}catch{}switch(r.tag){case 5:Qe||Gn(r,t);case 6:var s=$e,a=bt;$e=null,Jt(e,t,r),$e=s,bt=a,$e!==null&&(bt?(e=$e,r=r.stateNode,e.nodeType===8?e.parentNode.removeChild(r):e.removeChild(r)):$e.removeChild(r.stateNode));break;case 18:$e!==null&&(bt?(e=$e,r=r.stateNode,e.nodeType===8?Ya(e.parentNode,r):e.nodeType===1&&Ya(e,r),cr(e)):Ya($e,r.stateNode));break;case 4:s=$e,a=bt,$e=r.stateNode.containerInfo,bt=!0,Jt(e,t,r),$e=s,bt=a;break;case 0:case 11:case 14:case 15:if(!Qe&&(s=r.updateQueue,s!==null&&(s=s.lastEffect,s!==null))){a=s=s.next;do{var o=a,u=o.destroy;o=o.tag,u!==void 0&&((o&2)!==0||(o&4)!==0)&&Ri(r,t,u),a=a.next}while(a!==s)}Jt(e,t,r);break;case 1:if(!Qe&&(Gn(r,t),s=r.stateNode,typeof s.componentWillUnmount=="function"))try{s.props=r.memoizedProps,s.state=r.memoizedState,s.componentWillUnmount()}catch(h){_e(r,t,h)}Jt(e,t,r);break;case 21:Jt(e,t,r);break;case 22:r.mode&1?(Qe=(s=Qe)||r.memoizedState!==null,Jt(e,t,r),Qe=s):Jt(e,t,r);break;default:Jt(e,t,r)}}function Xc(e){var t=e.updateQueue;if(t!==null){e.updateQueue=null;var r=e.stateNode;r===null&&(r=e.stateNode=new Im),t.forEach(function(s){var a=Gm.bind(null,e,s);r.has(s)||(r.add(s),s.then(a,a))})}}function jt(e,t){var r=t.deletions;if(r!==null)for(var s=0;s<r.length;s++){var a=r[s];try{var o=e,u=t,h=u;e:for(;h!==null;){switch(h.tag){case 5:$e=h.stateNode,bt=!1;break e;case 3:$e=h.stateNode.containerInfo,bt=!0;break e;case 4:$e=h.stateNode.containerInfo,bt=!0;break e}h=h.return}if($e===null)throw Error(c(160));Qc(o,u,a),$e=null,bt=!1;var f=a.alternate;f!==null&&(f.return=null),a.return=null}catch(w){_e(a,t,w)}}if(t.subtreeFlags&12854)for(t=t.child;t!==null;)Yc(t,e),t=t.sibling}function Yc(e,t){var r=e.alternate,s=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(jt(t,e),Mt(e),s&4){try{Pr(3,e,e.return),Ms(3,e)}catch(G){_e(e,e.return,G)}try{Pr(5,e,e.return)}catch(G){_e(e,e.return,G)}}break;case 1:jt(t,e),Mt(e),s&512&&r!==null&&Gn(r,r.return);break;case 5:if(jt(t,e),Mt(e),s&512&&r!==null&&Gn(r,r.return),e.flags&32){var a=e.stateNode;try{Jn(a,"")}catch(G){_e(e,e.return,G)}}if(s&4&&(a=e.stateNode,a!=null)){var o=e.memoizedProps,u=r!==null?r.memoizedProps:o,h=e.type,f=e.updateQueue;if(e.updateQueue=null,f!==null)try{h==="input"&&o.type==="radio"&&o.name!=null&&No(a,o),fa(h,u);var w=fa(h,o);for(u=0;u<f.length;u+=2){var A=f[u],D=f[u+1];A==="style"?Ao(a,D):A==="dangerouslySetInnerHTML"?Po(a,D):A==="children"?Jn(a,D):V(a,A,D,w)}switch(h){case"input":ua(a,o);break;case"textarea":To(a,o);break;case"select":var P=a._wrapperState.wasMultiple;a._wrapperState.wasMultiple=!!o.multiple;var U=o.value;U!=null?Nn(a,!!o.multiple,U,!1):P!==!!o.multiple&&(o.defaultValue!=null?Nn(a,!!o.multiple,o.defaultValue,!0):Nn(a,!!o.multiple,o.multiple?[]:"",!1))}a[kr]=o}catch(G){_e(e,e.return,G)}}break;case 6:if(jt(t,e),Mt(e),s&4){if(e.stateNode===null)throw Error(c(162));a=e.stateNode,o=e.memoizedProps;try{a.nodeValue=o}catch(G){_e(e,e.return,G)}}break;case 3:if(jt(t,e),Mt(e),s&4&&r!==null&&r.memoizedState.isDehydrated)try{cr(t.containerInfo)}catch(G){_e(e,e.return,G)}break;case 4:jt(t,e),Mt(e);break;case 13:jt(t,e),Mt(e),a=e.child,a.flags&8192&&(o=a.memoizedState!==null,a.stateNode.isHidden=o,!o||a.alternate!==null&&a.alternate.memoizedState!==null||(Ui=Ee())),s&4&&Xc(e);break;case 22:if(A=r!==null&&r.memoizedState!==null,e.mode&1?(Qe=(w=Qe)||A,jt(t,e),Qe=w):jt(t,e),Mt(e),s&8192){if(w=e.memoizedState!==null,(e.stateNode.isHidden=w)&&!A&&(e.mode&1)!==0)for(W=e,A=e.child;A!==null;){for(D=W=A;W!==null;){switch(P=W,U=P.child,P.tag){case 0:case 11:case 14:case 15:Pr(4,P,P.return);break;case 1:Gn(P,P.return);var H=P.stateNode;if(typeof H.componentWillUnmount=="function"){s=P,r=P.return;try{t=s,H.props=t.memoizedProps,H.state=t.memoizedState,H.componentWillUnmount()}catch(G){_e(s,r,G)}}break;case 5:Gn(P,P.return);break;case 22:if(P.memoizedState!==null){eu(D);continue}}U!==null?(U.return=P,W=U):eu(D)}A=A.sibling}e:for(A=null,D=e;;){if(D.tag===5){if(A===null){A=D;try{a=D.stateNode,w?(o=a.style,typeof o.setProperty=="function"?o.setProperty("display","none","important"):o.display="none"):(h=D.stateNode,f=D.memoizedProps.style,u=f!=null&&f.hasOwnProperty("display")?f.display:null,h.style.display=Lo("display",u))}catch(G){_e(e,e.return,G)}}}else if(D.tag===6){if(A===null)try{D.stateNode.nodeValue=w?"":D.memoizedProps}catch(G){_e(e,e.return,G)}}else if((D.tag!==22&&D.tag!==23||D.memoizedState===null||D===e)&&D.child!==null){D.child.return=D,D=D.child;continue}if(D===e)break e;for(;D.sibling===null;){if(D.return===null||D.return===e)break e;A===D&&(A=null),D=D.return}A===D&&(A=null),D.sibling.return=D.return,D=D.sibling}}break;case 19:jt(t,e),Mt(e),s&4&&Xc(e);break;case 21:break;default:jt(t,e),Mt(e)}}function Mt(e){var t=e.flags;if(t&2){try{e:{for(var r=e.return;r!==null;){if(Kc(r)){var s=r;break e}r=r.return}throw Error(c(160))}switch(s.tag){case 5:var a=s.stateNode;s.flags&32&&(Jn(a,""),s.flags&=-33);var o=qc(e);Fi(e,o,a);break;case 3:case 4:var u=s.stateNode.containerInfo,h=qc(e);zi(e,h,u);break;default:throw Error(c(161))}}catch(f){_e(e,e.return,f)}e.flags&=-3}t&4096&&(e.flags&=-4097)}function Fm(e,t,r){W=e,Jc(e)}function Jc(e,t,r){for(var s=(e.mode&1)!==0;W!==null;){var a=W,o=a.child;if(a.tag===22&&s){var u=a.memoizedState!==null||Es;if(!u){var h=a.alternate,f=h!==null&&h.memoizedState!==null||Qe;h=Es;var w=Qe;if(Es=u,(Qe=f)&&!w)for(W=a;W!==null;)u=W,f=u.child,u.tag===22&&u.memoizedState!==null?tu(a):f!==null?(f.return=u,W=f):tu(a);for(;o!==null;)W=o,Jc(o),o=o.sibling;W=a,Es=h,Qe=w}Zc(e)}else(a.subtreeFlags&8772)!==0&&o!==null?(o.return=a,W=o):Zc(e)}}function Zc(e){for(;W!==null;){var t=W;if((t.flags&8772)!==0){var r=t.alternate;try{if((t.flags&8772)!==0)switch(t.tag){case 0:case 11:case 15:Qe||Ms(5,t);break;case 1:var s=t.stateNode;if(t.flags&4&&!Qe)if(r===null)s.componentDidMount();else{var a=t.elementType===t.type?r.memoizedProps:wt(t.type,r.memoizedProps);s.componentDidUpdate(a,r.memoizedState,s.__reactInternalSnapshotBeforeUpdate)}var o=t.updateQueue;o!==null&&ec(t,o,s);break;case 3:var u=t.updateQueue;if(u!==null){if(r=null,t.child!==null)switch(t.child.tag){case 5:r=t.child.stateNode;break;case 1:r=t.child.stateNode}ec(t,u,r)}break;case 5:var h=t.stateNode;if(r===null&&t.flags&4){r=h;var f=t.memoizedProps;switch(t.type){case"button":case"input":case"select":case"textarea":f.autoFocus&&r.focus();break;case"img":f.src&&(r.src=f.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(t.memoizedState===null){var w=t.alternate;if(w!==null){var A=w.memoizedState;if(A!==null){var D=A.dehydrated;D!==null&&cr(D)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(c(163))}Qe||t.flags&512&&Ii(t)}catch(P){_e(t,t.return,P)}}if(t===e){W=null;break}if(r=t.sibling,r!==null){r.return=t.return,W=r;break}W=t.return}}function eu(e){for(;W!==null;){var t=W;if(t===e){W=null;break}var r=t.sibling;if(r!==null){r.return=t.return,W=r;break}W=t.return}}function tu(e){for(;W!==null;){var t=W;try{switch(t.tag){case 0:case 11:case 15:var r=t.return;try{Ms(4,t)}catch(f){_e(t,r,f)}break;case 1:var s=t.stateNode;if(typeof s.componentDidMount=="function"){var a=t.return;try{s.componentDidMount()}catch(f){_e(t,a,f)}}var o=t.return;try{Ii(t)}catch(f){_e(t,o,f)}break;case 5:var u=t.return;try{Ii(t)}catch(f){_e(t,u,f)}}}catch(f){_e(t,t.return,f)}if(t===e){W=null;break}var h=t.sibling;if(h!==null){h.return=t.return,W=h;break}W=t.return}}var Bm=Math.ceil,Ps=ee.ReactCurrentDispatcher,Bi=ee.ReactCurrentOwner,gt=ee.ReactCurrentBatchConfig,ce=0,Oe=null,Ae=null,Ve=0,dt=0,Kn=Kt(0),Ie=0,Lr=null,gn=0,Ls=0,Oi=0,Ar=null,rt=null,Ui=0,qn=1/0,Bt=null,As=!1,Wi=null,Zt=null,Ds=!1,en=null,Rs=0,Dr=0,$i=null,Is=-1,zs=0;function Ye(){return(ce&6)!==0?Ee():Is!==-1?Is:Is=Ee()}function tn(e){return(e.mode&1)===0?1:(ce&2)!==0&&Ve!==0?Ve&-Ve:bm.transition!==null?(zs===0&&(zs=qo()),zs):(e=ge,e!==0||(e=window.event,e=e===void 0?16:rl(e.type)),e)}function St(e,t,r,s){if(50<Dr)throw Dr=0,$i=null,Error(c(185));sr(e,r,s),((ce&2)===0||e!==Oe)&&(e===Oe&&((ce&2)===0&&(Ls|=r),Ie===4&&nn(e,Ve)),st(e,s),r===1&&ce===0&&(t.mode&1)===0&&(qn=Ee()+500,ds&&Qt()))}function st(e,t){var r=e.callbackNode;bd(e,t);var s=Gr(e,e===Oe?Ve:0);if(s===0)r!==null&&Ho(r),e.callbackNode=null,e.callbackPriority=0;else if(t=s&-s,e.callbackPriority!==t){if(r!=null&&Ho(r),t===1)e.tag===0?wm(ru.bind(null,e)):Wl(ru.bind(null,e)),vm(function(){(ce&6)===0&&Qt()}),r=null;else{switch(Qo(s)){case 1:r=ba;break;case 4:r=Go;break;case 16:r=Wr;break;case 536870912:r=Ko;break;default:r=Wr}r=du(r,nu.bind(null,e))}e.callbackPriority=t,e.callbackNode=r}}function nu(e,t){if(Is=-1,zs=0,(ce&6)!==0)throw Error(c(327));var r=e.callbackNode;if(Qn()&&e.callbackNode!==r)return null;var s=Gr(e,e===Oe?Ve:0);if(s===0)return null;if((s&30)!==0||(s&e.expiredLanes)!==0||t)t=Fs(e,s);else{t=s;var a=ce;ce|=2;var o=au();(Oe!==e||Ve!==t)&&(Bt=null,qn=Ee()+500,yn(e,t));do try{Wm();break}catch(h){su(e,h)}while(!0);oi(),Ps.current=o,ce=a,Ae!==null?t=0:(Oe=null,Ve=0,t=Ie)}if(t!==0){if(t===2&&(a=ja(e),a!==0&&(s=a,t=Vi(e,a))),t===1)throw r=Lr,yn(e,0),nn(e,s),st(e,Ee()),r;if(t===6)nn(e,s);else{if(a=e.current.alternate,(s&30)===0&&!Om(a)&&(t=Fs(e,s),t===2&&(o=ja(e),o!==0&&(s=o,t=Vi(e,o))),t===1))throw r=Lr,yn(e,0),nn(e,s),st(e,Ee()),r;switch(e.finishedWork=a,e.finishedLanes=s,t){case 0:case 1:throw Error(c(345));case 2:xn(e,rt,Bt);break;case 3:if(nn(e,s),(s&130023424)===s&&(t=Ui+500-Ee(),10<t)){if(Gr(e,0)!==0)break;if(a=e.suspendedLanes,(a&s)!==s){Ye(),e.pingedLanes|=e.suspendedLanes&a;break}e.timeoutHandle=Xa(xn.bind(null,e,rt,Bt),t);break}xn(e,rt,Bt);break;case 4:if(nn(e,s),(s&4194240)===s)break;for(t=e.eventTimes,a=-1;0<s;){var u=31-yt(s);o=1<<u,u=t[u],u>a&&(a=u),s&=~o}if(s=a,s=Ee()-s,s=(120>s?120:480>s?480:1080>s?1080:1920>s?1920:3e3>s?3e3:4320>s?4320:1960*Bm(s/1960))-s,10<s){e.timeoutHandle=Xa(xn.bind(null,e,rt,Bt),s);break}xn(e,rt,Bt);break;case 5:xn(e,rt,Bt);break;default:throw Error(c(329))}}}return st(e,Ee()),e.callbackNode===r?nu.bind(null,e):null}function Vi(e,t){var r=Ar;return e.current.memoizedState.isDehydrated&&(yn(e,t).flags|=256),e=Fs(e,t),e!==2&&(t=rt,rt=r,t!==null&&Hi(t)),e}function Hi(e){rt===null?rt=e:rt.push.apply(rt,e)}function Om(e){for(var t=e;;){if(t.flags&16384){var r=t.updateQueue;if(r!==null&&(r=r.stores,r!==null))for(var s=0;s<r.length;s++){var a=r[s],o=a.getSnapshot;a=a.value;try{if(!xt(o(),a))return!1}catch{return!1}}}if(r=t.child,t.subtreeFlags&16384&&r!==null)r.return=t,t=r;else{if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return!0;t=t.return}t.sibling.return=t.return,t=t.sibling}}return!0}function nn(e,t){for(t&=~Oi,t&=~Ls,e.suspendedLanes|=t,e.pingedLanes&=~t,e=e.expirationTimes;0<t;){var r=31-yt(t),s=1<<r;e[r]=-1,t&=~s}}function ru(e){if((ce&6)!==0)throw Error(c(327));Qn();var t=Gr(e,0);if((t&1)===0)return st(e,Ee()),null;var r=Fs(e,t);if(e.tag!==0&&r===2){var s=ja(e);s!==0&&(t=s,r=Vi(e,s))}if(r===1)throw r=Lr,yn(e,0),nn(e,t),st(e,Ee()),r;if(r===6)throw Error(c(345));return e.finishedWork=e.current.alternate,e.finishedLanes=t,xn(e,rt,Bt),st(e,Ee()),null}function Gi(e,t){var r=ce;ce|=1;try{return e(t)}finally{ce=r,ce===0&&(qn=Ee()+500,ds&&Qt())}}function vn(e){en!==null&&en.tag===0&&(ce&6)===0&&Qn();var t=ce;ce|=1;var r=gt.transition,s=ge;try{if(gt.transition=null,ge=1,e)return e()}finally{ge=s,gt.transition=r,ce=t,(ce&6)===0&&Qt()}}function Ki(){dt=Kn.current,ke(Kn)}function yn(e,t){e.finishedWork=null,e.finishedLanes=0;var r=e.timeoutHandle;if(r!==-1&&(e.timeoutHandle=-1,gm(r)),Ae!==null)for(r=Ae.return;r!==null;){var s=r;switch(ni(s),s.tag){case 1:s=s.type.childContextTypes,s!=null&&cs();break;case 3:Vn(),ke(et),ke(Ge),fi();break;case 5:hi(s);break;case 4:Vn();break;case 13:ke(Ne);break;case 19:ke(Ne);break;case 10:li(s.type._context);break;case 22:case 23:Ki()}r=r.return}if(Oe=e,Ae=e=rn(e.current,null),Ve=dt=t,Ie=0,Lr=null,Oi=Ls=gn=0,rt=Ar=null,hn!==null){for(t=0;t<hn.length;t++)if(r=hn[t],s=r.interleaved,s!==null){r.interleaved=null;var a=s.next,o=r.pending;if(o!==null){var u=o.next;o.next=a,s.next=u}r.pending=s}hn=null}return e}function su(e,t){do{var r=Ae;try{if(oi(),ws.current=Ns,bs){for(var s=Ce.memoizedState;s!==null;){var a=s.queue;a!==null&&(a.pending=null),s=s.next}bs=!1}if(fn=0,Be=Re=Ce=null,Cr=!1,_r=0,Bi.current=null,r===null||r.return===null){Ie=1,Lr=t,Ae=null;break}e:{var o=e,u=r.return,h=r,f=t;if(t=Ve,h.flags|=32768,f!==null&&typeof f=="object"&&typeof f.then=="function"){var w=f,A=h,D=A.tag;if((A.mode&1)===0&&(D===0||D===11||D===15)){var P=A.alternate;P?(A.updateQueue=P.updateQueue,A.memoizedState=P.memoizedState,A.lanes=P.lanes):(A.updateQueue=null,A.memoizedState=null)}var U=Ec(u);if(U!==null){U.flags&=-257,Mc(U,u,h,o,t),U.mode&1&&Tc(o,w,t),t=U,f=w;var H=t.updateQueue;if(H===null){var G=new Set;G.add(f),t.updateQueue=G}else H.add(f);break e}else{if((t&1)===0){Tc(o,w,t),qi();break e}f=Error(c(426))}}else if(be&&h.mode&1){var Me=Ec(u);if(Me!==null){(Me.flags&65536)===0&&(Me.flags|=256),Mc(Me,u,h,o,t),ai(Hn(f,h));break e}}o=f=Hn(f,h),Ie!==4&&(Ie=2),Ar===null?Ar=[o]:Ar.push(o),o=u;do{switch(o.tag){case 3:o.flags|=65536,t&=-t,o.lanes|=t;var x=Cc(o,f,t);Zl(o,x);break e;case 1:h=f;var v=o.type,k=o.stateNode;if((o.flags&128)===0&&(typeof v.getDerivedStateFromError=="function"||k!==null&&typeof k.componentDidCatch=="function"&&(Zt===null||!Zt.has(k)))){o.flags|=65536,t&=-t,o.lanes|=t;var F=_c(o,h,t);Zl(o,F);break e}}o=o.return}while(o!==null)}ou(r)}catch(q){t=q,Ae===r&&r!==null&&(Ae=r=r.return);continue}break}while(!0)}function au(){var e=Ps.current;return Ps.current=Ns,e===null?Ns:e}function qi(){(Ie===0||Ie===3||Ie===2)&&(Ie=4),Oe===null||(gn&268435455)===0&&(Ls&268435455)===0||nn(Oe,Ve)}function Fs(e,t){var r=ce;ce|=2;var s=au();(Oe!==e||Ve!==t)&&(Bt=null,yn(e,t));do try{Um();break}catch(a){su(e,a)}while(!0);if(oi(),ce=r,Ps.current=s,Ae!==null)throw Error(c(261));return Oe=null,Ve=0,Ie}function Um(){for(;Ae!==null;)iu(Ae)}function Wm(){for(;Ae!==null&&!hd();)iu(Ae)}function iu(e){var t=uu(e.alternate,e,dt);e.memoizedProps=e.pendingProps,t===null?ou(e):Ae=t,Bi.current=null}function ou(e){var t=e;do{var r=t.alternate;if(e=t.return,(t.flags&32768)===0){if(r=Dm(r,t,dt),r!==null){Ae=r;return}}else{if(r=Rm(r,t),r!==null){r.flags&=32767,Ae=r;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{Ie=6,Ae=null;return}}if(t=t.sibling,t!==null){Ae=t;return}Ae=t=e}while(t!==null);Ie===0&&(Ie=5)}function xn(e,t,r){var s=ge,a=gt.transition;try{gt.transition=null,ge=1,$m(e,t,r,s)}finally{gt.transition=a,ge=s}return null}function $m(e,t,r,s){do Qn();while(en!==null);if((ce&6)!==0)throw Error(c(327));r=e.finishedWork;var a=e.finishedLanes;if(r===null)return null;if(e.finishedWork=null,e.finishedLanes=0,r===e.current)throw Error(c(177));e.callbackNode=null,e.callbackPriority=0;var o=r.lanes|r.childLanes;if(jd(e,o),e===Oe&&(Ae=Oe=null,Ve=0),(r.subtreeFlags&2064)===0&&(r.flags&2064)===0||Ds||(Ds=!0,du(Wr,function(){return Qn(),null})),o=(r.flags&15990)!==0,(r.subtreeFlags&15990)!==0||o){o=gt.transition,gt.transition=null;var u=ge;ge=1;var h=ce;ce|=4,Bi.current=null,zm(e,r),Yc(r,e),cm(qa),Qr=!!Ka,qa=Ka=null,e.current=r,Fm(r),pd(),ce=h,ge=u,gt.transition=o}else e.current=r;if(Ds&&(Ds=!1,en=e,Rs=a),o=e.pendingLanes,o===0&&(Zt=null),vd(r.stateNode),st(e,Ee()),t!==null)for(s=e.onRecoverableError,r=0;r<t.length;r++)a=t[r],s(a.value,{componentStack:a.stack,digest:a.digest});if(As)throw As=!1,e=Wi,Wi=null,e;return(Rs&1)!==0&&e.tag!==0&&Qn(),o=e.pendingLanes,(o&1)!==0?e===$i?Dr++:(Dr=0,$i=e):Dr=0,Qt(),null}function Qn(){if(en!==null){var e=Qo(Rs),t=gt.transition,r=ge;try{if(gt.transition=null,ge=16>e?16:e,en===null)var s=!1;else{if(e=en,en=null,Rs=0,(ce&6)!==0)throw Error(c(331));var a=ce;for(ce|=4,W=e.current;W!==null;){var o=W,u=o.child;if((W.flags&16)!==0){var h=o.deletions;if(h!==null){for(var f=0;f<h.length;f++){var w=h[f];for(W=w;W!==null;){var A=W;switch(A.tag){case 0:case 11:case 15:Pr(8,A,o)}var D=A.child;if(D!==null)D.return=A,W=D;else for(;W!==null;){A=W;var P=A.sibling,U=A.return;if(Gc(A),A===w){W=null;break}if(P!==null){P.return=U,W=P;break}W=U}}}var H=o.alternate;if(H!==null){var G=H.child;if(G!==null){H.child=null;do{var Me=G.sibling;G.sibling=null,G=Me}while(G!==null)}}W=o}}if((o.subtreeFlags&2064)!==0&&u!==null)u.return=o,W=u;else e:for(;W!==null;){if(o=W,(o.flags&2048)!==0)switch(o.tag){case 0:case 11:case 15:Pr(9,o,o.return)}var x=o.sibling;if(x!==null){x.return=o.return,W=x;break e}W=o.return}}var v=e.current;for(W=v;W!==null;){u=W;var k=u.child;if((u.subtreeFlags&2064)!==0&&k!==null)k.return=u,W=k;else e:for(u=v;W!==null;){if(h=W,(h.flags&2048)!==0)try{switch(h.tag){case 0:case 11:case 15:Ms(9,h)}}catch(q){_e(h,h.return,q)}if(h===u){W=null;break e}var F=h.sibling;if(F!==null){F.return=h.return,W=F;break e}W=h.return}}if(ce=a,Qt(),Ct&&typeof Ct.onPostCommitFiberRoot=="function")try{Ct.onPostCommitFiberRoot($r,e)}catch{}s=!0}return s}finally{ge=r,gt.transition=t}}return!1}function lu(e,t,r){t=Hn(r,t),t=Cc(e,t,1),e=Yt(e,t,1),t=Ye(),e!==null&&(sr(e,1,t),st(e,t))}function _e(e,t,r){if(e.tag===3)lu(e,e,r);else for(;t!==null;){if(t.tag===3){lu(t,e,r);break}else if(t.tag===1){var s=t.stateNode;if(typeof t.type.getDerivedStateFromError=="function"||typeof s.componentDidCatch=="function"&&(Zt===null||!Zt.has(s))){e=Hn(r,e),e=_c(t,e,1),t=Yt(t,e,1),e=Ye(),t!==null&&(sr(t,1,e),st(t,e));break}}t=t.return}}function Vm(e,t,r){var s=e.pingCache;s!==null&&s.delete(t),t=Ye(),e.pingedLanes|=e.suspendedLanes&r,Oe===e&&(Ve&r)===r&&(Ie===4||Ie===3&&(Ve&130023424)===Ve&&500>Ee()-Ui?yn(e,0):Oi|=r),st(e,t)}function cu(e,t){t===0&&((e.mode&1)===0?t=1:(t=Hr,Hr<<=1,(Hr&130023424)===0&&(Hr=4194304)));var r=Ye();e=It(e,t),e!==null&&(sr(e,t,r),st(e,r))}function Hm(e){var t=e.memoizedState,r=0;t!==null&&(r=t.retryLane),cu(e,r)}function Gm(e,t){var r=0;switch(e.tag){case 13:var s=e.stateNode,a=e.memoizedState;a!==null&&(r=a.retryLane);break;case 19:s=e.stateNode;break;default:throw Error(c(314))}s!==null&&s.delete(t),cu(e,r)}var uu;uu=function(e,t,r){if(e!==null)if(e.memoizedProps!==t.pendingProps||et.current)nt=!0;else{if((e.lanes&r)===0&&(t.flags&128)===0)return nt=!1,Am(e,t,r);nt=(e.flags&131072)!==0}else nt=!1,be&&(t.flags&1048576)!==0&&$l(t,hs,t.index);switch(t.lanes=0,t.tag){case 2:var s=t.type;Ts(e,t),e=t.pendingProps;var a=zn(t,Ge.current);$n(t,r),a=yi(null,t,s,e,a,r);var o=xi();return t.flags|=1,typeof a=="object"&&a!==null&&typeof a.render=="function"&&a.$$typeof===void 0?(t.tag=1,t.memoizedState=null,t.updateQueue=null,tt(s)?(o=!0,us(t)):o=!1,t.memoizedState=a.state!==null&&a.state!==void 0?a.state:null,di(t),a.updater=Cs,t.stateNode=a,a._reactInternals=t,Ni(t,s,e,r),t=Ei(null,t,s,!0,o,r)):(t.tag=0,be&&o&&ti(t),Xe(null,t,a,r),t=t.child),t;case 16:s=t.elementType;e:{switch(Ts(e,t),e=t.pendingProps,a=s._init,s=a(s._payload),t.type=s,a=t.tag=qm(s),e=wt(s,e),a){case 0:t=Ti(null,t,s,e,r);break e;case 1:t=Ic(null,t,s,e,r);break e;case 11:t=Pc(null,t,s,e,r);break e;case 14:t=Lc(null,t,s,wt(s.type,e),r);break e}throw Error(c(306,s,""))}return t;case 0:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:wt(s,a),Ti(e,t,s,a,r);case 1:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:wt(s,a),Ic(e,t,s,a,r);case 3:e:{if(zc(t),e===null)throw Error(c(387));s=t.pendingProps,o=t.memoizedState,a=o.element,Jl(e,t),xs(t,s,null,r);var u=t.memoizedState;if(s=u.element,o.isDehydrated)if(o={element:s,isDehydrated:!1,cache:u.cache,pendingSuspenseBoundaries:u.pendingSuspenseBoundaries,transitions:u.transitions},t.updateQueue.baseState=o,t.memoizedState=o,t.flags&256){a=Hn(Error(c(423)),t),t=Fc(e,t,s,r,a);break e}else if(s!==a){a=Hn(Error(c(424)),t),t=Fc(e,t,s,r,a);break e}else for(ut=Gt(t.stateNode.containerInfo.firstChild),ct=t,be=!0,kt=null,r=Xl(t,null,s,r),t.child=r;r;)r.flags=r.flags&-3|4096,r=r.sibling;else{if(On(),s===a){t=Ft(e,t,r);break e}Xe(e,t,s,r)}t=t.child}return t;case 5:return tc(t),e===null&&si(t),s=t.type,a=t.pendingProps,o=e!==null?e.memoizedProps:null,u=a.children,Qa(s,a)?u=null:o!==null&&Qa(s,o)&&(t.flags|=32),Rc(e,t),Xe(e,t,u,r),t.child;case 6:return e===null&&si(t),null;case 13:return Bc(e,t,r);case 4:return mi(t,t.stateNode.containerInfo),s=t.pendingProps,e===null?t.child=Un(t,null,s,r):Xe(e,t,s,r),t.child;case 11:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:wt(s,a),Pc(e,t,s,a,r);case 7:return Xe(e,t,t.pendingProps,r),t.child;case 8:return Xe(e,t,t.pendingProps.children,r),t.child;case 12:return Xe(e,t,t.pendingProps.children,r),t.child;case 10:e:{if(s=t.type._context,a=t.pendingProps,o=t.memoizedProps,u=a.value,ye(gs,s._currentValue),s._currentValue=u,o!==null)if(xt(o.value,u)){if(o.children===a.children&&!et.current){t=Ft(e,t,r);break e}}else for(o=t.child,o!==null&&(o.return=t);o!==null;){var h=o.dependencies;if(h!==null){u=o.child;for(var f=h.firstContext;f!==null;){if(f.context===s){if(o.tag===1){f=zt(-1,r&-r),f.tag=2;var w=o.updateQueue;if(w!==null){w=w.shared;var A=w.pending;A===null?f.next=f:(f.next=A.next,A.next=f),w.pending=f}}o.lanes|=r,f=o.alternate,f!==null&&(f.lanes|=r),ci(o.return,r,t),h.lanes|=r;break}f=f.next}}else if(o.tag===10)u=o.type===t.type?null:o.child;else if(o.tag===18){if(u=o.return,u===null)throw Error(c(341));u.lanes|=r,h=u.alternate,h!==null&&(h.lanes|=r),ci(u,r,t),u=o.sibling}else u=o.child;if(u!==null)u.return=o;else for(u=o;u!==null;){if(u===t){u=null;break}if(o=u.sibling,o!==null){o.return=u.return,u=o;break}u=u.return}o=u}Xe(e,t,a.children,r),t=t.child}return t;case 9:return a=t.type,s=t.pendingProps.children,$n(t,r),a=pt(a),s=s(a),t.flags|=1,Xe(e,t,s,r),t.child;case 14:return s=t.type,a=wt(s,t.pendingProps),a=wt(s.type,a),Lc(e,t,s,a,r);case 15:return Ac(e,t,t.type,t.pendingProps,r);case 17:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:wt(s,a),Ts(e,t),t.tag=1,tt(s)?(e=!0,us(t)):e=!1,$n(t,r),Sc(t,s,a),Ni(t,s,a,r),Ei(null,t,s,!0,e,r);case 19:return Uc(e,t,r);case 22:return Dc(e,t,r)}throw Error(c(156,t.tag))};function du(e,t){return Vo(e,t)}function Km(e,t,r,s){this.tag=e,this.key=r,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=t,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=s,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function vt(e,t,r,s){return new Km(e,t,r,s)}function Qi(e){return e=e.prototype,!(!e||!e.isReactComponent)}function qm(e){if(typeof e=="function")return Qi(e)?1:0;if(e!=null){if(e=e.$$typeof,e===Se)return 11;if(e===He)return 14}return 2}function rn(e,t){var r=e.alternate;return r===null?(r=vt(e.tag,t,e.key,e.mode),r.elementType=e.elementType,r.type=e.type,r.stateNode=e.stateNode,r.alternate=e,e.alternate=r):(r.pendingProps=t,r.type=e.type,r.flags=0,r.subtreeFlags=0,r.deletions=null),r.flags=e.flags&14680064,r.childLanes=e.childLanes,r.lanes=e.lanes,r.child=e.child,r.memoizedProps=e.memoizedProps,r.memoizedState=e.memoizedState,r.updateQueue=e.updateQueue,t=e.dependencies,r.dependencies=t===null?null:{lanes:t.lanes,firstContext:t.firstContext},r.sibling=e.sibling,r.index=e.index,r.ref=e.ref,r}function Bs(e,t,r,s,a,o){var u=2;if(s=e,typeof e=="function")Qi(e)&&(u=1);else if(typeof e=="string")u=5;else e:switch(e){case Q:return kn(r.children,a,o,t);case pe:u=8,a|=8;break;case ne:return e=vt(12,r,t,a|2),e.elementType=ne,e.lanes=o,e;case re:return e=vt(13,r,t,a),e.elementType=re,e.lanes=o,e;case Le:return e=vt(19,r,t,a),e.elementType=Le,e.lanes=o,e;case he:return Os(r,a,o,t);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case je:u=10;break e;case Te:u=9;break e;case Se:u=11;break e;case He:u=14;break e;case Fe:u=16,s=null;break e}throw Error(c(130,e==null?e:typeof e,""))}return t=vt(u,r,t,a),t.elementType=e,t.type=s,t.lanes=o,t}function kn(e,t,r,s){return e=vt(7,e,s,t),e.lanes=r,e}function Os(e,t,r,s){return e=vt(22,e,s,t),e.elementType=he,e.lanes=r,e.stateNode={isHidden:!1},e}function Xi(e,t,r){return e=vt(6,e,null,t),e.lanes=r,e}function Yi(e,t,r){return t=vt(4,e.children!==null?e.children:[],e.key,t),t.lanes=r,t.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},t}function Qm(e,t,r,s,a){this.tag=t,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=Sa(0),this.expirationTimes=Sa(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=Sa(0),this.identifierPrefix=s,this.onRecoverableError=a,this.mutableSourceEagerHydrationData=null}function Ji(e,t,r,s,a,o,u,h,f){return e=new Qm(e,t,r,h,f),t===1?(t=1,o===!0&&(t|=8)):t=0,o=vt(3,null,null,t),e.current=o,o.stateNode=e,o.memoizedState={element:s,isDehydrated:r,cache:null,transitions:null,pendingSuspenseBoundaries:null},di(o),e}function Xm(e,t,r){var s=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:B,key:s==null?null:""+s,children:e,containerInfo:t,implementation:r}}function mu(e){if(!e)return qt;e=e._reactInternals;e:{if(ln(e)!==e||e.tag!==1)throw Error(c(170));var t=e;do{switch(t.tag){case 3:t=t.stateNode.context;break e;case 1:if(tt(t.type)){t=t.stateNode.__reactInternalMemoizedMergedChildContext;break e}}t=t.return}while(t!==null);throw Error(c(171))}if(e.tag===1){var r=e.type;if(tt(r))return Ol(e,r,t)}return t}function hu(e,t,r,s,a,o,u,h,f){return e=Ji(r,s,!0,e,a,o,u,h,f),e.context=mu(null),r=e.current,s=Ye(),a=tn(r),o=zt(s,a),o.callback=t??null,Yt(r,o,a),e.current.lanes=a,sr(e,a,s),st(e,s),e}function Us(e,t,r,s){var a=t.current,o=Ye(),u=tn(a);return r=mu(r),t.context===null?t.context=r:t.pendingContext=r,t=zt(o,u),t.payload={element:e},s=s===void 0?null:s,s!==null&&(t.callback=s),e=Yt(a,t,u),e!==null&&(St(e,a,u,o),ys(e,a,u)),u}function Ws(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function pu(e,t){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var r=e.retryLane;e.retryLane=r!==0&&r<t?r:t}}function Zi(e,t){pu(e,t),(e=e.alternate)&&pu(e,t)}function Ym(){return null}var fu=typeof reportError=="function"?reportError:function(e){console.error(e)};function eo(e){this._internalRoot=e}$s.prototype.render=eo.prototype.render=function(e){var t=this._internalRoot;if(t===null)throw Error(c(409));Us(e,t,null,null)},$s.prototype.unmount=eo.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var t=e.containerInfo;vn(function(){Us(null,e,null,null)}),t[Lt]=null}};function $s(e){this._internalRoot=e}$s.prototype.unstable_scheduleHydration=function(e){if(e){var t=Jo();e={blockedOn:null,target:e,priority:t};for(var r=0;r<$t.length&&t!==0&&t<$t[r].priority;r++);$t.splice(r,0,e),r===0&&tl(e)}};function to(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function Vs(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function gu(){}function Jm(e,t,r,s,a){if(a){if(typeof s=="function"){var o=s;s=function(){var w=Ws(u);o.call(w)}}var u=hu(t,s,e,0,null,!1,!1,"",gu);return e._reactRootContainer=u,e[Lt]=u.current,yr(e.nodeType===8?e.parentNode:e),vn(),u}for(;a=e.lastChild;)e.removeChild(a);if(typeof s=="function"){var h=s;s=function(){var w=Ws(f);h.call(w)}}var f=Ji(e,0,!1,null,null,!1,!1,"",gu);return e._reactRootContainer=f,e[Lt]=f.current,yr(e.nodeType===8?e.parentNode:e),vn(function(){Us(t,f,r,s)}),f}function Hs(e,t,r,s,a){var o=r._reactRootContainer;if(o){var u=o;if(typeof a=="function"){var h=a;a=function(){var f=Ws(u);h.call(f)}}Us(t,u,e,a)}else u=Jm(r,t,e,a,s);return Ws(u)}Xo=function(e){switch(e.tag){case 3:var t=e.stateNode;if(t.current.memoizedState.isDehydrated){var r=rr(t.pendingLanes);r!==0&&(Na(t,r|1),st(t,Ee()),(ce&6)===0&&(qn=Ee()+500,Qt()))}break;case 13:vn(function(){var s=It(e,1);if(s!==null){var a=Ye();St(s,e,1,a)}}),Zi(e,1)}},Ca=function(e){if(e.tag===13){var t=It(e,134217728);if(t!==null){var r=Ye();St(t,e,134217728,r)}Zi(e,134217728)}},Yo=function(e){if(e.tag===13){var t=tn(e),r=It(e,t);if(r!==null){var s=Ye();St(r,e,t,s)}Zi(e,t)}},Jo=function(){return ge},Zo=function(e,t){var r=ge;try{return ge=e,t()}finally{ge=r}},ya=function(e,t,r){switch(t){case"input":if(ua(e,r),t=r.name,r.type==="radio"&&t!=null){for(r=e;r.parentNode;)r=r.parentNode;for(r=r.querySelectorAll("input[name="+JSON.stringify(""+t)+'][type="radio"]'),t=0;t<r.length;t++){var s=r[t];if(s!==e&&s.form===e.form){var a=ls(s);if(!a)throw Error(c(90));jo(s),ua(s,a)}}}break;case"textarea":To(e,r);break;case"select":t=r.value,t!=null&&Nn(e,!!r.multiple,t,!1)}},zo=Gi,Fo=vn;var Zm={usingClientEntryPoint:!1,Events:[wr,Rn,ls,Ro,Io,Gi]},Rr={findFiberByHostInstance:cn,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},eh={bundleType:Rr.bundleType,version:Rr.version,rendererPackageName:Rr.rendererPackageName,rendererConfig:Rr.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:ee.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=Wo(e),e===null?null:e.stateNode},findFiberByHostInstance:Rr.findFiberByHostInstance||Ym,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Gs=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Gs.isDisabled&&Gs.supportsFiber)try{$r=Gs.inject(eh),Ct=Gs}catch{}}return at.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Zm,at.createPortal=function(e,t){var r=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!to(t))throw Error(c(200));return Xm(e,t,null,r)},at.createRoot=function(e,t){if(!to(e))throw Error(c(299));var r=!1,s="",a=fu;return t!=null&&(t.unstable_strictMode===!0&&(r=!0),t.identifierPrefix!==void 0&&(s=t.identifierPrefix),t.onRecoverableError!==void 0&&(a=t.onRecoverableError)),t=Ji(e,1,!1,null,null,r,!1,s,a),e[Lt]=t.current,yr(e.nodeType===8?e.parentNode:e),new eo(t)},at.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var t=e._reactInternals;if(t===void 0)throw typeof e.render=="function"?Error(c(188)):(e=Object.keys(e).join(","),Error(c(268,e)));return e=Wo(t),e=e===null?null:e.stateNode,e},at.flushSync=function(e){return vn(e)},at.hydrate=function(e,t,r){if(!Vs(t))throw Error(c(200));return Hs(null,e,t,!0,r)},at.hydrateRoot=function(e,t,r){if(!to(e))throw Error(c(405));var s=r!=null&&r.hydratedSources||null,a=!1,o="",u=fu;if(r!=null&&(r.unstable_strictMode===!0&&(a=!0),r.identifierPrefix!==void 0&&(o=r.identifierPrefix),r.onRecoverableError!==void 0&&(u=r.onRecoverableError)),t=hu(t,null,e,1,r??null,a,!1,o,u),e[Lt]=t.current,yr(e),s)for(e=0;e<s.length;e++)r=s[e],a=r._getVersion,a=a(r._source),t.mutableSourceEagerHydrationData==null?t.mutableSourceEagerHydrationData=[r,a]:t.mutableSourceEagerHydrationData.push(r,a);return new $s(t)},at.render=function(e,t,r){if(!Vs(t))throw Error(c(200));return Hs(null,e,t,!1,r)},at.unmountComponentAtNode=function(e){if(!Vs(e))throw Error(c(40));return e._reactRootContainer?(vn(function(){Hs(null,null,e,!1,function(){e._reactRootContainer=null,e[Lt]=null})}),!0):!1},at.unstable_batchedUpdates=Gi,at.unstable_renderSubtreeIntoContainer=function(e,t,r,s){if(!Vs(r))throw Error(c(200));if(e==null||e._reactInternals===void 0)throw Error(c(38));return Hs(e,t,r,!1,s)},at.version="18.3.1-next-f1338f8080-20240426",at}var Nu;function uh(){if(Nu)return so.exports;Nu=1;function i(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(i)}catch(l){console.error(l)}}return i(),so.exports=ch(),so.exports}var Cu;function dh(){if(Cu)return Ks;Cu=1;var i=uh();return Ks.createRoot=i.createRoot,Ks.hydrateRoot=i.hydrateRoot,Ks}var mh=dh();class hh extends Error{constructor(c,d){super(c);vu(this,"status");this.status=d}}async function ze(i,l){const c=await fetch(i,{...l,credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json",...l==null?void 0:l.headers}}),d=await c.json().catch(()=>({}));if(!c.ok)throw new hh(d.error||c.statusText||"Request failed",c.status);return d}const fo=()=>ze("/auth/status"),ph=()=>ze("/api/config"),ea=()=>ze("/api/botstats"),fh=()=>ze("/api/team"),gh=i=>ze(`/api/team/${i}`),go=()=>ze("/api/staff/me"),vh=(i,l)=>ze("/api/staff/profile",{method:"POST",headers:l?{"X-CSRF-Token":l}:void 0,body:JSON.stringify(i)}),yh=(i,l)=>ze("/api/staff/global-profile",{method:"POST",headers:l?{"X-CSRF-Token":l}:void 0,body:JSON.stringify(i)}),xh=()=>ze("/api/commands"),vo=()=>ze("/api/guilds"),_u=()=>ze("/api/me/overview"),kh=i=>ze(`/api/guild/${i}/overview`),wh=i=>ze(`/api/guild/${i}/levels`),Tu=i=>ze(`/api/guild/${i}/config`),Eu=i=>ze(`/api/guild/${i}/resources`);function sa(i,l,c,d){return ze(`/api/guild/${i}/config/${l}`,{method:"POST",headers:d?{"X-CSRF-Token":d}:void 0,body:JSON.stringify(c)})}function bh(i,l,c){return ze(`/api/guild/${i}/config/profile`,{method:"POST",headers:c?{"X-CSRF-Token":c}:void 0,body:JSON.stringify(l)})}function $u(i){return i.replace(/\/+$/,"")||"/"}function Mu(i=window.location.pathname){const l=$u(i);return l==="/commands"?"commands":l==="/docs"?"docs":l.startsWith("/docs/")?"docs-detail":l==="/dashboard/staff"||l==="/dashboard/staff/"?"staff":l==="/dashboard"||l.startsWith("/dashboard/")?"dashboard":l==="/team"?"team":l.startsWith("/team/")?"team-member":l==="/privacy"?"privacy":l==="/terms"?"terms":l==="/community"?"community":l==="/donate"||l.startsWith("/donate")?"donate":l==="/transcript"||l.startsWith("/transcript/")?"transcript":l==="/changelog"?"changelog":l.startsWith("/changelog/")?"changelog-detail":"home"}function Xn(i,l="overview"){return i?`/dashboard/${i}/${l}`:"/dashboard"}function yo(){return"/dashboard/servers"}function Pu(){const i=$u(window.location.pathname).split("/").filter(Boolean),l=["overview","leveling","moderation","server","ai","customization"];return i[1]==="servers"?{view:"servers",guildId:null,section:"overview"}:!i[1]||i[1]==="staff"?{view:"overview",guildId:null,section:"overview"}:{view:"guild",guildId:i[1]||null,section:l.includes(i[2])?i[2]:"overview"}}function le(i){i.startsWith("/")&&(window.history.pushState({},"",i),window.dispatchEvent(new PopStateEvent("popstate")),window.scrollTo({top:0,behavior:"smooth"}))}function Vu({onNavigate:i}){return n.jsxs("a",{className:"brand",href:"/",onClick:l=>{l.preventDefault(),i?i():le("/")},children:[n.jsx("span",{className:"brand-mark",children:"n"}),n.jsx("span",{children:"niko"})]})}function Nt(){return n.jsxs("footer",{className:"site-footer",children:[n.jsx(Vu,{}),n.jsx("span",{children:"Built for communities that care."}),n.jsxs("div",{children:[n.jsx("a",{href:"/changelog",onClick:i=>{i.preventDefault(),le("/changelog")},children:"Changelog"}),n.jsx("a",{href:"/privacy",onClick:i=>{i.preventDefault(),le("/privacy")},children:"Privacy"}),n.jsx("a",{href:"/terms",onClick:i=>{i.preventDefault(),le("/terms")},children:"Terms"}),n.jsx("a",{href:"/community",onClick:i=>{i.preventDefault(),le("/community")},children:"Community Policy"}),n.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"GitHub"})]})]})}/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Hu=(...i)=>i.filter((l,c,d)=>!!l&&l.trim()!==""&&d.indexOf(l)===c).join(" ").trim();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jh=i=>i.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Sh=i=>i.replace(/^([A-Z])|[\s-_]+(\w)/g,(l,c,d)=>d?d.toUpperCase():c.toLowerCase());/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Lu=i=>{const l=Sh(i);return l.charAt(0).toUpperCase()+l.slice(1)};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var oo={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Nh=i=>{for(const l in i)if(l.startsWith("aria-")||l==="role"||l==="title")return!0;return!1},Ch=T.createContext({}),_h=()=>T.useContext(Ch),Th=T.forwardRef(({color:i,size:l,strokeWidth:c,absoluteStrokeWidth:d,className:m="",children:p,iconNode:g,...E},b)=>{const{size:z=24,strokeWidth:C=2,absoluteStrokeWidth:N=!1,color:M="currentColor",className:I=""}=_h()??{},R=d??N?Number(c??C)*24/Number(l??z):c??C;return T.createElement("svg",{ref:b,...oo,width:l??z??oo.width,height:l??z??oo.height,stroke:i??M,strokeWidth:R,className:Hu("lucide",I,m),...!p&&!Nh(E)&&{"aria-hidden":"true"},...E},[...g.map(([_,j])=>T.createElement(_,j)),...Array.isArray(p)?p:[p]])});/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ze=(i,l)=>{const c=T.forwardRef(({className:d,...m},p)=>T.createElement(Th,{ref:p,iconNode:l,className:Hu(`lucide-${jh(Lu(i))}`,`lucide-${i}`,d),...m}));return c.displayName=Lu(i),c};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Eh=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]],Mh=Ze("arrow-right",Eh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ph=[["path",{d:"M12 5v16",key:"1f6ucr"}],["path",{d:"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z",key:"1fyvmf"}]],Au=Ze("book-open",Ph);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Lh=[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],lo=Ze("chart-column",Lh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ah=[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]],Dh=Ze("external-link",Ah);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Rh=[["rect",{width:"7",height:"7",x:"3",y:"3",rx:"1",key:"1g98yp"}],["rect",{width:"7",height:"7",x:"14",y:"3",rx:"1",key:"6d4xhi"}],["rect",{width:"7",height:"7",x:"14",y:"14",rx:"1",key:"nxv5o0"}],["rect",{width:"7",height:"7",x:"3",y:"14",rx:"1",key:"1bb6yr"}]],xo=Ze("layout-grid",Rh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ih=[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]],zh=Ze("lock-keyhole",Ih);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Fh=[["path",{d:"m16 17 5-5-5-5",key:"1bji2h"}],["path",{d:"M21 12H9",key:"dn1m92"}],["path",{d:"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4",key:"1uf3rs"}]],Bh=Ze("log-out",Fh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Oh=[["path",{d:"M4 5h16",key:"1tepv9"}],["path",{d:"M4 12h16",key:"1lakjw"}],["path",{d:"M4 19h16",key:"1djgab"}]],Uh=Ze("menu",Oh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Wh=[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]],$h=Ze("search",Wh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Vh=[["path",{d:"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915",key:"1i5ecw"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]],qs=Ze("settings",Vh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Hh=[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}]],co=Ze("shield",Hh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Gh=[["path",{d:"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",key:"1s2grr"}],["path",{d:"M20 2v4",key:"1rf3ol"}],["path",{d:"M22 4h-4",key:"gwowj6"}],["circle",{cx:"4",cy:"20",r:"2",key:"6kqj1y"}]],Qs=Ze("sparkles",Gh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Kh=[["path",{d:"M12 19h8",key:"baeox8"}],["path",{d:"m4 17 6-6-6-6",key:"1yngyt"}]],qh=Ze("terminal",Kh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Qh=[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["path",{d:"M16 3.128a4 4 0 0 1 0 7.744",key:"16gr8j"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}]],Du=Ze("users",Qh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Xh=[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]],Yh=Ze("x",Xh),Jh={arrow:Mh,grid:xo,terminal:qh,chart:lo,shield:co,spark:Qs,users:Du,settings:qs,book:Au,external:Dh,menu:Uh,close:Yh,lock:zh,logout:Bh,search:$h,doc:Au,utility:qs,icon_home:xo,icon_settings:qs,icon_economy:lo,icon_leveling:lo,icon_moderation:co,icon_automod:co,icon_heart:Qs,icon_utility:qs,icon_bot:Du,icon_ai:Qs,icon_lightbulb:Qs};function K({name:i,size:l,className:c=""}){const d=Jh[i]||xo;return n.jsx(d,{className:`icon ${c}`.trim(),"aria-hidden":"true",focusable:"false",strokeWidth:1.8,style:l?{width:l,height:l}:void 0})}let Ru=null,uo=null;function aa(){const[i,l]=T.useState(Ru);return T.useEffect(()=>{uo||(uo=ph().then(c=>Ru=c)),uo.then(l).catch(()=>{})},[]),i}const Iu=[{label:"Home",path:"/",page:"home"},{label:"Commands",path:"/commands",page:"commands"},{label:"Docs",path:"/docs",page:"docs"},{label:"Team",path:"/team",page:"team"},{label:"Changelog",path:"/changelog",page:"changelog"}];function We({page:i}){const l=aa(),c=i==="dashboard",[d,m]=T.useState(!1),p=g=>E=>{E.preventDefault(),m(!1),le(g)};return n.jsxs("header",{className:`site-header${c?" dashboard-header":""}`,children:[n.jsx(Vu,{onNavigate:()=>m(!1)}),!c&&n.jsx("nav",{className:"site-nav","aria-label":"Main navigation",children:Iu.map(g=>n.jsx("a",{className:i===g.page?"active":"","aria-current":i===g.page?"page":void 0,href:g.path,onClick:p(g.path),children:g.label},g.path))}),n.jsx("div",{className:"header-actions",children:c?n.jsxs("div",{className:"dashboard-menu",children:[n.jsxs("button",{className:"button button-small button-muted dashboard-menu-trigger",type:"button","aria-expanded":d,"aria-controls":"dashboard-navigation-menu",onClick:()=>m(g=>!g),children:[n.jsx(K,{name:d?"close":"menu"}),n.jsx("span",{children:"Menu"})]}),d&&n.jsxs("nav",{id:"dashboard-navigation-menu",className:"dashboard-menu-popover","aria-label":"Dashboard navigation",children:[n.jsx("span",{className:"dashboard-menu-label",children:"Navigate"}),Iu.map(g=>n.jsx("a",{href:g.path,onClick:p(g.path),children:g.label},g.path)),n.jsx("a",{className:"dashboard-menu-current",href:"/dashboard","aria-current":"page",onClick:p("/dashboard"),children:"Dashboard"})]})]}):n.jsxs(n.Fragment,{children:[n.jsxs("a",{className:"button button-small button-muted dashboard-link",href:"/dashboard",onClick:p("/dashboard"),children:["Dashboard ",n.jsx(K,{name:"arrow"})]}),n.jsx("a",{className:"button button-small button-primary",href:(l==null?void 0:l.invite_url)||"#",target:"_blank",rel:"noreferrer",children:"Add to Discord"})]})})]})}const zu=typeof navigator<"u"?(navigator.language||"en").slice(0,2):"en";function ko(i){const l=i.description;if(typeof l=="string")return l;if(l&&typeof l=="object"){const c=l;if(c[zu])return c[zu];if(c.en)return c.en;const d=Object.values(c).find(m=>typeof m=="string"&&m.length>0);if(d)return d}return"A Niko command for your server."}const Zh=[{value:"all",label:"All commands"},{value:"slash",label:"Slash"},{value:"prefix",label:"Prefix"},{value:"hybrid",label:"Hybrid"},{value:"context",label:"Context menus"}],ta={slash:"Slash command",prefix:"Prefix command",hybrid:"Hybrid command",context:"Context menu"};function bn(i){return i.type&&i.type in ta?i.type:"slash"}function ep(i){return i.context_type==="user"?"Right-click a user":"Right-click a message"}function Gu(i){const l=bn(i);return l==="slash"?n.jsxs("code",{children:["/",i.name]}):l==="prefix"?n.jsxs("code",{children:[".",i.name]}):l==="hybrid"?n.jsxs(n.Fragment,{children:[n.jsxs("code",{children:["/",i.name]}),n.jsx("span",{className:"command-or",children:"or"}),n.jsxs("code",{children:[".",i.name]})]}):n.jsxs("code",{className:"context-invocation",children:[ep(i)," · ",i.name]})}function Fu(i){return i!=null&&i.length?i:["Not specified"]}function tp({command:i,onClose:l}){T.useEffect(()=>{const g=E=>{E.key==="Escape"&&l()};return document.addEventListener("keydown",g),()=>document.removeEventListener("keydown",g)},[l]);const c=i.parameters||[],d=i.subcommands||[],m=Fu(i.aliases),p=Fu(i.permissions);return n.jsx("div",{className:"command-dialog-backdrop",role:"presentation",onMouseDown:g=>{g.currentTarget===g.target&&l()},children:n.jsxs("section",{className:"command-dialog",role:"dialog","aria-modal":"true","aria-labelledby":"command-dialog-title",children:[n.jsxs("header",{className:"command-dialog-header",children:[n.jsxs("div",{children:[n.jsxs("div",{className:"command-dialog-kicker",children:[i.category," · ",ta[bn(i)]]}),n.jsx("h2",{id:"command-dialog-title",children:Gu(i)})]}),n.jsx("button",{className:"dialog-close",type:"button",onClick:l,"aria-label":"Close command details",title:"Close command details",children:n.jsx(K,{name:"close"})})]}),n.jsxs("div",{className:"command-dialog-body",children:[n.jsx("p",{className:"command-dialog-description",children:ko(i)}),n.jsxs("div",{className:"command-detail-grid",children:[n.jsxs("section",{className:"command-detail-section command-detail-wide",children:[n.jsx("h3",{children:"Usage"}),n.jsx("code",{className:"command-usage",children:i.usage||`${bn(i)==="context"?i.name:`/${i.name}`}`})]}),n.jsxs("section",{className:"command-detail-section",children:[n.jsx("h3",{children:"Permissions"}),n.jsx("ul",{className:"command-detail-list",children:p.map(g=>n.jsx("li",{children:g},g))})]}),n.jsxs("section",{className:"command-detail-section",children:[n.jsx("h3",{children:"Aliases"}),n.jsx("ul",{className:"command-detail-list",children:m.map(g=>n.jsx("li",{children:n.jsx("code",{children:g==="Not specified"?g:`.${g}`})},g))})]})]}),!!c.length&&n.jsxs("section",{className:"command-detail-section command-parameters",children:[n.jsx("h3",{children:"Parameters"}),n.jsx("div",{className:"command-parameter-list",children:c.map(g=>n.jsxs("div",{className:"command-parameter",children:[n.jsxs("div",{className:"command-parameter-title",children:[n.jsx("code",{children:g.name}),n.jsxs("span",{children:[g.required?"Required":"Optional"," · ",g.type]})]}),n.jsx("p",{children:g.description||"No description provided."})]},g.name))})]}),!!d.length&&n.jsxs("section",{className:"command-detail-section",children:[n.jsx("h3",{children:"Subcommands"}),n.jsx("div",{className:"subcommand-list",children:d.map(g=>n.jsxs("code",{children:[i.name," ",g]},g))})]})]}),n.jsxs("footer",{className:"command-dialog-footer",children:[n.jsx("span",{children:"Command registry details are generated from the live bot."}),n.jsx("button",{className:"button button-primary button-small",type:"button",onClick:l,children:"Done"})]})]})})}function np(){const[i,l]=T.useState([]),[c,d]=T.useState(null),[m,p]=T.useState(""),[g,E]=T.useState("all"),[b,z]=T.useState("all"),[C,N]=T.useState(!0),[M,I]=T.useState("");T.useEffect(()=>{xh().then(l).catch(()=>I("The command registry is unavailable right now.")).finally(()=>N(!1))},[]),T.useEffect(()=>{if(!c)return;const j=document.body.style.overflow;return document.body.style.overflow="hidden",()=>{document.body.style.overflow=j}},[c]);const R=T.useMemo(()=>["all",...Array.from(new Set(i.map(j=>j.category))).sort()],[i]),_=i.filter(j=>{const J=`${j.name} ${ko(j)} ${j.category} ${ta[bn(j)]} ${j.context_type||""} ${(j.aliases||[]).join(" ")}`.toLowerCase();return(b==="all"||bn(j)===b)&&(g==="all"||j.category===g)&&J.includes(m.trim().toLowerCase())});return n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"commands"}),n.jsxs("main",{className:"shell page-main",children:[n.jsxs("div",{className:"page-heading",children:[n.jsx("div",{className:"eyebrow",children:"Reference library"}),n.jsxs("h1",{children:["Everything Niko",n.jsx("br",{}),n.jsx("em",{children:"knows how to do."})]}),n.jsx("p",{children:"Browse slash, prefix, hybrid, and context commands from the live bot registry. Select any command for permissions, aliases, parameters, usage, and subcommands."})]}),n.jsxs("div",{className:"command-toolbar",children:[n.jsxs("label",{className:"search-field",children:[n.jsx("span",{"aria-hidden":"true",children:"⌕"}),n.jsx("input",{value:m,onChange:j=>p(j.target.value),placeholder:"Search commands","aria-label":"Search commands"})]}),n.jsxs("div",{className:"command-filters",children:[n.jsx("div",{className:"filter-list","aria-label":"Command types",children:Zh.map(j=>n.jsx("button",{type:"button",className:b===j.value?"filter active":"filter","aria-pressed":b===j.value,onClick:()=>z(j.value),children:j.label},j.value))}),n.jsx("div",{className:"filter-list","aria-label":"Command categories",children:R.map(j=>n.jsx("button",{type:"button",className:g===j?"filter active":"filter","aria-pressed":g===j,onClick:()=>E(j),children:j==="all"?"All categories":j},j))})]})]}),n.jsxs("div",{className:"command-meta",children:[n.jsx("strong",{children:C?"…":_.length})," commands ",n.jsx("span",{children:"·"})," live bot registry ",n.jsx("span",{children:"·"})," select a card for details"]}),M&&n.jsxs("div",{className:"inline-error",role:"alert",children:[n.jsx("strong",{children:"Could not load commands"}),n.jsx("span",{children:M})]}),n.jsxs("div",{className:"commands-grid",children:[_.map(j=>n.jsxs("button",{className:"command-card",type:"button",onClick:()=>d(j),"aria-label":`View details for ${j.name}`,children:[n.jsxs("span",{className:"command-card-head",children:[n.jsx("span",{className:"command-name",children:Gu(j)}),n.jsx("span",{className:"command-type",children:ta[bn(j)]})]}),n.jsx("span",{className:"command-card-description",children:ko(j)}),n.jsxs("span",{className:"command-card-footer",children:[n.jsx("span",{className:"category-tag",children:j.category}),n.jsxs("span",{className:"command-expand",children:[n.jsx("span",{children:"Details"}),n.jsx(K,{name:"arrow",size:14})]})]})]},`${bn(j)}-${j.context_type||""}-${j.category}-${j.name}`)),!C&&!M&&!_.length&&n.jsx("div",{className:"empty-state",children:"No commands match that search."})]})]}),n.jsx(Nt,{}),c&&n.jsx(tp,{command:c,onClose:()=>d(null)})]})}function Pe(i){return i==null?"—":new Intl.NumberFormat("en-US",{notation:i>9999?"compact":"standard"}).format(i)}function Ku(i){return(i==null?void 0:i.global_name)||(i==null?void 0:i.username)||"there"}function qu(i){return i.split(/\s+/).map(l=>l[0]).join("").slice(0,2).toUpperCase()}function bo({guild:i,className:l="guild-avatar"}){return n.jsx("span",{className:l,"aria-hidden":"true",children:i.icon_url?n.jsx("img",{src:i.icon_url,alt:""}):i.name.slice(0,1).toUpperCase()})}function Qu({user:i,className:l="avatar"}){const c=i.avatar?`https://cdn.discordapp.com/avatars/${i.id}/${i.avatar}.${i.avatar.startsWith("a_")?"gif":"png"}?size=64`:null;return n.jsx("span",{className:l,"aria-hidden":"true",children:c?n.jsx("img",{src:c,alt:""}):qu(i.global_name||i.username||"Niko")})}function rp({name:i,avatarUrl:l,className:c="member-avatar"}){return n.jsx("span",{className:c,"aria-hidden":"true",children:l?n.jsx("img",{src:l,alt:""}):qu(i)})}const sp=[["overview","Overview","grid","At a glance"],["leveling","Leveling","spark","Reward participation"],["moderation","Moderation","shield","Keep things steady"],["server","Server","settings","Manage server features"],["ai","AI controls","settings","Shape Niko’s voice"],["customization","Customization","paint","Niko’s server identity"]];function Xu({user:i,guilds:l,selectedGuild:c,view:d,section:m,stats:p,onHome:g,onServers:E,onGuildChange:b,onSectionChange:z,onRefresh:C,refreshing:N,staffRole:M,children:I}){const R=l.filter(S=>S.installed!==!1),_=(S=!1)=>n.jsx("nav",{className:S?"dash-nav dash-nav-mobile":"dash-nav","aria-label":"Server settings",children:sp.map(([V,ee,se])=>n.jsxs("button",{className:d==="guild"&&m===V?"active":"","aria-current":d==="guild"&&m===V?"page":void 0,onClick:()=>z(V),children:[n.jsx(K,{name:se}),n.jsx("span",{children:ee})]},V))}),j=(S=!1)=>n.jsxs("nav",{className:S?"dash-nav dash-primary-nav dash-nav-mobile":"dash-nav dash-primary-nav","aria-label":"Dashboard",children:[n.jsxs("button",{className:d==="overview"?"active":"","aria-current":d==="overview"?"page":void 0,onClick:g,children:[n.jsx(K,{name:"grid"}),n.jsx("span",{children:"My overview"})]}),n.jsxs("button",{className:d==="servers"?"active":"","aria-current":d==="servers"?"page":void 0,onClick:E,children:[n.jsx(K,{name:"users"}),n.jsx("span",{children:"My servers"})]}),M&&n.jsxs("button",{onClick:()=>le("/dashboard/staff"),children:[n.jsx(K,{name:"shield"}),n.jsx("span",{children:"Staff workspace"})]})]}),J=()=>n.jsxs("div",{className:"dash-top-actions",children:[d==="guild"?n.jsxs("label",{className:"guild-switcher",children:[n.jsx("span",{className:"sr-only",children:"Switch server"}),n.jsxs("select",{value:(c==null?void 0:c.id)||"",onChange:S=>{const V=R.find(ee=>ee.id===S.target.value);V&&b(V)},children:[n.jsx("option",{value:"",disabled:!0,children:"Switch server"}),R.map(S=>n.jsx("option",{value:S.id,children:S.name},S.id))]})]}):n.jsxs("button",{className:"button button-muted button-small top-action",onClick:E,children:[n.jsx(K,{name:"users"})," Browse servers"]}),n.jsxs("button",{className:"button button-muted button-small top-action refresh-action",onClick:C,disabled:N,"aria-label":"Refresh dashboard data",children:[n.jsx(K,{name:"spark"})," ",N?"Refreshing…":"Refresh data"]}),d==="guild"&&n.jsxs("span",{className:"connection-chip",children:[n.jsx("span",{className:"status-dot"})," Connected"]}),n.jsxs("div",{className:"user-pill",children:[n.jsx(Qu,{user:i}),n.jsx("span",{children:Ku(i)})]}),n.jsx("a",{className:"logout-button",href:"/auth/logout","aria-label":"Log out",title:"Log out",children:n.jsx(K,{name:"logout"})})]});return n.jsxs("div",{className:"dashboard-layout",children:[n.jsxs("aside",{className:"dash-sidebar",children:[n.jsx("div",{className:"dash-mobile-controls",children:J()}),n.jsxs("div",{className:"side-rail-heading",children:[n.jsx("span",{className:"side-label",children:"Workspace"}),n.jsxs("span",{className:"rail-status",children:[n.jsx("span",{className:"status-dot"})," Live"]})]}),j(),d==="guild"&&c&&n.jsxs(n.Fragment,{children:[n.jsx("div",{className:"side-label side-label-settings",children:"Current server"}),n.jsxs("div",{className:"side-guild",children:[n.jsx(bo,{guild:c}),n.jsxs("span",{children:[n.jsx("strong",{children:c.name}),n.jsx("small",{children:"Live configuration"})]}),n.jsx("span",{className:"guild-presence",title:"Niko is connected",children:n.jsx("span",{className:"status-dot"})})]}),n.jsxs("div",{className:"side-settings-caption",children:[n.jsx("span",{children:"Settings map"}),n.jsx("small",{children:"Pick a room to tune"})]}),_()]}),n.jsxs("div",{className:"sidebar-bottom",children:[n.jsxs("span",{className:"online-label",children:[n.jsx("span",{className:"status-dot"})," Niko is online"]}),n.jsxs("small",{children:[Pe(p==null?void 0:p.guild_count)," connected servers · v",(p==null?void 0:p.version)||"1.0"]}),n.jsxs("a",{href:"/",onClick:S=>{S.preventDefault(),le("/")},children:["Back to public site ",n.jsx(K,{name:"arrow"})]})]})]}),n.jsxs("div",{className:"dash-content",children:[n.jsx(We,{page:"dashboard"}),n.jsx("div",{className:"dash-contextbar",children:J()}),n.jsx("div",{className:"mobile-primary-bar",children:j(!0)}),d==="guild"&&n.jsx("div",{className:"mobile-section-bar",children:_(!0)}),n.jsx("main",{className:"dash-main",children:I})]})]})}function on({eyebrow:i,title:l,text:c}){return n.jsxs("div",{className:"dash-heading",children:[n.jsxs("div",{className:"heading-meta",children:[n.jsx("div",{className:"eyebrow",children:i}),n.jsx("span",{className:"heading-context",children:"NIKO / CONTROL ROOM"})]}),n.jsx("h2",{children:l}),n.jsx("p",{children:c})]})}function Pt({label:i,value:l,note:c,accent:d=""}){return n.jsxs("div",{className:`dash-stat ${d}`,children:[n.jsx("span",{children:i}),n.jsx("strong",{children:l}),n.jsx("small",{children:c})]})}function ap({user:i,overview:l,guilds:c,onServers:d,onManage:m}){const p=c.filter(g=>g.installed!==!1);return n.jsxs(n.Fragment,{children:[n.jsx(on,{eyebrow:"Personal overview",title:"Your Niko snapshot.",text:"Keep an eye on your progress, then jump into a server when you’re ready to tune the room."}),n.jsxs("div",{className:"overview-intro",children:[n.jsxs("div",{className:"profile-card",children:[n.jsx(Qu,{user:i,className:"profile-avatar"}),n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"Signed in as"}),n.jsx("h3",{children:Ku(i)}),n.jsx("p",{children:"Personal economy profile"})]})]}),n.jsxs("button",{className:"button button-primary",onClick:d,children:["Manage a server ",n.jsx(K,{name:"arrow"})]})]}),n.jsxs("div",{className:"dash-stats overview-stats",children:[n.jsx(Pt,{label:"Net worth",value:Pe(l==null?void 0:l.net_worth),note:"Across your Niko profile",accent:"accent-orange"}),n.jsx(Pt,{label:"In your wallet",value:Pe(l==null?void 0:l.balance),note:"Ready to spend",accent:"accent-violet"}),n.jsx(Pt,{label:"In your vault",value:Pe(l==null?void 0:l.bank),note:"Saved for later",accent:"accent-blue"}),n.jsx(Pt,{label:"Current level",value:Pe(l==null?void 0:l.level),note:l!=null&&l.job?`Working as a ${l.job}`:"Keep showing up",accent:"accent-green"})]}),n.jsxs("div",{className:"dash-columns overview-columns",children:[n.jsxs("section",{className:"dash-panel",children:[n.jsxs("div",{className:"panel-heading",children:[n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"Progress"}),n.jsx("h3",{children:"Your momentum"})]}),n.jsx("span",{className:"panel-icon",children:n.jsx(K,{name:"spark"})})]}),n.jsxs("div",{className:"metric-list",children:[n.jsxs("div",{children:[n.jsx("span",{children:"Daily streak"}),n.jsxs("strong",{children:[Pe(l==null?void 0:l.daily_streak)," ",n.jsx("small",{children:"days"})]})]}),n.jsxs("div",{children:[n.jsx("span",{children:"Achievements"}),n.jsxs("strong",{children:[Pe(l==null?void 0:l.achievements)," ",n.jsx("small",{children:"unlocked"})]})]}),n.jsxs("div",{children:[n.jsx("span",{children:"Total earned"}),n.jsxs("strong",{children:[Pe(l==null?void 0:l.total_earned)," ",n.jsx("small",{children:"coins"})]})]}),n.jsxs("div",{children:[n.jsx("span",{children:"Economy standing"}),n.jsxs("strong",{children:[l!=null&&l.economy_rank?`#${Pe(l.economy_rank)}`:"—"," ",n.jsx("small",{children:l!=null&&l.economy_profiles?`of ${Pe(l.economy_profiles)}`:""})]})]})]})]}),n.jsxs("section",{className:"dash-panel",children:[n.jsxs("div",{className:"panel-heading",children:[n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"Quick access"}),n.jsx("h3",{children:"Your servers"})]}),n.jsx("span",{className:"panel-icon",children:n.jsx(K,{name:"users"})})]}),n.jsxs("div",{className:"mini-server-list",children:[p.slice(0,4).map(g=>n.jsxs("button",{onClick:()=>m(g),children:[n.jsx(bo,{guild:g}),n.jsx("span",{children:g.name}),n.jsx(K,{name:"arrow"})]},g.id)),!p.length&&n.jsx("p",{className:"empty-state compact",children:"Add Niko to a server to start managing it."})]}),n.jsxs("button",{className:"text-link overview-link",onClick:d,children:["View all servers ",n.jsx(K,{name:"arrow"})]})]})]})]})}function Bu({guild:i,onManage:l}){const c=i.installed!==!1;return n.jsxs("article",{className:"server-card",children:[n.jsxs("div",{className:"server-card-heading",children:[n.jsx(bo,{guild:i,className:"server-avatar"}),n.jsx("span",{className:"server-status",children:c?"Niko is installed":"Ready to add"})]}),n.jsx("h3",{children:i.name}),n.jsx("p",{children:c?"Open the dashboard to manage Niko’s features and settings.":"You have permission to manage this server. Add Niko to unlock its controls."}),c?n.jsxs("button",{className:"button button-muted button-small",onClick:()=>l(i),children:["Open settings ",n.jsx(K,{name:"arrow"})]}):n.jsxs("a",{className:"button button-primary button-small",href:i.invite_url||"#",target:"_blank",rel:"noreferrer",children:["Add Niko ",n.jsx(K,{name:"external"})]})]})}function ip({guilds:i,onManage:l}){const c=i.filter(m=>m.installed!==!1),d=i.filter(m=>m.installed===!1);return n.jsxs(n.Fragment,{children:[n.jsx(on,{eyebrow:"Servers",title:"Choose where to work.",text:"Manage servers with Niko already installed, or add Niko to another server you can administer."}),n.jsxs("div",{className:"server-summary",children:[n.jsxs("div",{children:[n.jsx("strong",{children:Pe(c.length)}),n.jsx("span",{children:"Connected to Niko"})]}),n.jsxs("div",{children:[n.jsx("strong",{children:Pe(d.length)}),n.jsx("span",{children:"Ready to add"})]}),n.jsxs("div",{className:"server-summary-note",children:[n.jsx(K,{name:"shield"}),n.jsx("span",{children:"Only servers where you have Manage Server access are shown."})]})]}),n.jsxs("section",{className:"server-section",children:[n.jsxs("div",{className:"section-heading-row",children:[n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"Connected"}),n.jsx("h3",{children:"Manage a server"})]}),n.jsx("span",{className:"section-count",children:c.length})]}),n.jsxs("div",{className:"server-grid",children:[c.map(m=>n.jsx(Bu,{guild:m,onManage:l},m.id)),!c.length&&n.jsxs("div",{className:"empty-state",children:[n.jsx("strong",{children:"No connected servers yet."}),n.jsx("span",{children:"Add Niko below, then come back here to manage it."})]})]})]}),n.jsxs("section",{className:"server-section",children:[n.jsxs("div",{className:"section-heading-row",children:[n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"Available to you"}),n.jsx("h3",{children:"Add Niko to a server"})]}),n.jsx("span",{className:"section-count",children:d.length})]}),n.jsxs("div",{className:"server-grid",children:[d.map(m=>n.jsx(Bu,{guild:m,onManage:l},m.id)),!d.length&&n.jsx("div",{className:"server-note",children:"Niko is already installed in every server you can manage."})]})]})]})}function Yu({rows:i}){return n.jsxs("div",{className:"rank-list",children:[i.slice(0,5).map((l,c)=>n.jsxs("div",{className:"rank-row",children:[n.jsx("span",{className:`rank rank-${c+1}`,children:String(c+1).padStart(2,"0")}),n.jsxs("span",{className:"rank-user",children:[n.jsx(rp,{name:l.display_name||l.username||"Unknown member",avatarUrl:l.avatar_url}),n.jsxs("span",{children:[n.jsx("strong",{children:l.display_name||l.username||"Unknown member"}),l.username&&l.display_name&&n.jsxs("small",{children:["@",l.username]})]})]}),n.jsxs("strong",{children:["Level ",Pe(l.level),n.jsxs("small",{children:[Pe(l.xp)," xp"]})]})]},`${l.user_id}-${c}`)),!i.length&&n.jsx("div",{className:"empty-state compact",children:"No data recorded yet."})]})}function op({overview:i}){return n.jsxs(n.Fragment,{children:[n.jsxs("div",{className:"guild-welcome",children:[n.jsxs("div",{children:[n.jsx("span",{className:"welcome-mark",children:n.jsx(K,{name:"grid"})}),n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"Server pulse"}),n.jsx("strong",{children:"Here’s what needs your attention."})]})]}),n.jsxs("span",{className:"welcome-time",children:["LIVE SIGNALS ",n.jsx("span",{className:"status-dot"})]})]}),n.jsx(on,{eyebrow:"Overview",title:"A quick read on your room.",text:"The important signals, without making you hunt for them."}),n.jsxs("div",{className:"dash-stats guild-overview-stats",children:[n.jsx(Pt,{label:"Warnings logged",value:Pe(i.moderation.warn_count),note:"For this server",accent:"accent-blue"}),n.jsx(Pt,{label:"Automod",value:i.moderation.automod_active?"Active":"Quiet",note:"Protection status",accent:"accent-green"}),n.jsx(Pt,{label:"Level leaders",value:Pe(i.leveling.top.length),note:"Members with recorded XP",accent:"accent-violet"})]}),n.jsxs("div",{className:"dash-columns",children:[n.jsxs("section",{className:"dash-panel",children:[n.jsxs("div",{className:"panel-heading",children:[n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"Community energy"}),n.jsx("h3",{children:"Top XP"})]}),n.jsx("span",{className:"panel-icon",children:n.jsx(K,{name:"spark"})})]}),n.jsx(Yu,{rows:i.leveling.top})]}),n.jsxs("section",{className:"dash-panel",children:[n.jsxs("div",{className:"panel-heading",children:[n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"Server controls"}),n.jsx("h3",{children:"Manage the room"})]}),n.jsx("span",{className:"panel-icon",children:n.jsx(K,{name:"settings"})})]}),n.jsxs("div",{className:"server-controls-body",children:[n.jsx("p",{children:"Use Server settings for prefixes, welcome messages, logs, and ticket panels."}),n.jsxs("span",{className:"text-link",children:["Open server settings ",n.jsx(K,{name:"arrow"})]})]})]})]})]})}function lp({rows:i,config:l,resources:c,csrfToken:d,guildId:m}){var p,g,E;return n.jsxs(n.Fragment,{children:[n.jsx(on,{eyebrow:"Leveling",title:"Momentum people can see.",text:"Track the members turning up, and tune the pace to fit your server."}),n.jsxs("div",{className:"dash-stats",children:[n.jsx(Pt,{label:"Top level",value:String(((p=i[0])==null?void 0:p.level)||0),note:((g=i[0])==null?void 0:g.display_name)||((E=i[0])==null?void 0:E.username)||"No members yet",accent:"accent-violet"}),n.jsx(Pt,{label:"XP multiplier",value:`${(l==null?void 0:l.leveling.xp_multiplier)||1}×`,note:(l==null?void 0:l.leveling.xp_enabled)===!1?"XP disabled":"Currently active",accent:"accent-blue"}),n.jsx(Pt,{label:"Cooldown",value:`${(l==null?void 0:l.leveling.xp_cooldown)||0}s`,note:"Between XP awards",accent:"accent-green"})]}),n.jsxs("section",{className:"dash-panel",children:[n.jsxs("div",{className:"panel-heading",children:[n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"Leaderboard"}),n.jsx("h3",{children:"XP leaders"})]}),n.jsx("span",{className:"panel-icon",children:n.jsx(K,{name:"spark"})})]}),n.jsx(Yu,{rows:i})]}),n.jsx(mp,{guildId:m,config:l,resources:c,csrfToken:d})]})}const ia={saving:!1,message:"",error:""};function Je({label:i,hint:l,children:c}){return n.jsxs("label",{className:"form-field",children:[n.jsx("span",{className:"form-label",children:i}),c,l&&n.jsx("small",{children:l})]})}function cp(i,l){const c=l?String(l):"",d=(i==null?void 0:i.channels)||[];return!c||d.some(m=>m.id===c)?d:[{id:c,name:`Saved channel · ${c}`},...d]}function oa({icon:i,label:l,title:c,text:d}){return n.jsxs("div",{className:"settings-intro",children:[n.jsx("span",{className:"settings-intro-icon",children:n.jsx(K,{name:i})}),n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:l}),n.jsx("strong",{children:c}),n.jsx("p",{children:d})]}),n.jsxs("span",{className:"settings-intro-state",children:[n.jsx("span",{className:"status-dot"})," Per server"]})]})}function Sn({label:i,title:l,detail:c,icon:d}){return n.jsxs("div",{className:"panel-heading settings-section-title",children:[n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:i}),n.jsx("h3",{children:l}),c&&n.jsx("p",{children:c})]}),d&&n.jsx("span",{className:"panel-icon",children:n.jsx(K,{name:d})})]})}function la({state:i}){return n.jsxs("div",{className:"setting-footer",children:[i.error?n.jsx("span",{className:"form-error",role:"alert",children:i.error}):n.jsx("span",{role:"status",children:i.message||"Changes apply to this server."}),n.jsx("button",{className:"button button-primary",type:"submit",disabled:i.saving,children:i.saving?"Saving…":"Save changes"})]})}function up({guildId:i,config:l,csrfToken:c}){var N,M,I;const[d,m]=T.useState({}),[p,g]=T.useState(ia);T.useEffect(()=>{const R=(l==null?void 0:l.moderation)||{};m({automod:{...R.automod||{}},spam_threshold:R.spam_threshold??6,spam_interval:R.spam_interval??7,max_mentions:R.max_mentions??5,antinuke:{...R.antinuke||{}},antiraid:{...R.antiraid||{}},antiraid_ext:{...R.antiraid_ext||{}}})},[l]);const E=(R,_,j)=>m(J=>({...J,[R]:{...J[R],[_]:j}})),b=R=>{R.preventDefault(),g({saving:!0,message:"",error:""}),sa(i,"automod",d,c).then(_=>{const j=_.config||{};m({automod:{...j.automod||{}},spam_threshold:j.spam_threshold??6,spam_interval:j.spam_interval??7,max_mentions:j.max_mentions??5,antinuke:{...j.antinuke||{}},antiraid:{...j.antiraid||{}},antiraid_ext:{...j.antiraid_ext||{}}}),g({saving:!1,message:"Moderation settings saved to Niko.",error:""})}).catch(_=>g({saving:!1,message:"",error:_ instanceof Error?_.message:"Could not save settings."}))},z=[["antispam","Anti-spam","Detect repeated messages"],["antilink","Invite links","Remove Discord invite links"],["badwords","Blocked words","Filter words from the server list"],["massmention","Mass mentions","Limit mention floods"],["antinuke","Anti-nuke","Protect channels and roles"],["antiraid","Join raid protection","React to sudden join waves"],["antiraid_ext","External app protection","Detect user-installed app abuse"]],C=z.filter(([R])=>{var _;return!!((_=d.automod)!=null&&_[R])}).length;return n.jsxs(n.Fragment,{children:[n.jsx(on,{eyebrow:"Moderation",title:"Keep the room feeling good.",text:"Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration."}),n.jsx(oa,{icon:"shield",label:"Protection desk",title:`${C} of ${z.length} safeguards active`,text:"Start with the essentials, then tune thresholds below when you know the room’s rhythm."}),n.jsxs("form",{onSubmit:b,className:"settings-stack",children:[n.jsxs("section",{className:"dash-panel settings-panel",children:[n.jsx(Sn,{label:"Protection rules",title:"AutoMod modules",detail:"Toggle only the responses you want Niko to handle.",icon:"shield"}),n.jsx("div",{className:"setting-list",children:z.map(([R,_,j])=>{var J;return n.jsxs("label",{className:"setting-row",children:[n.jsxs("span",{children:[n.jsx("strong",{children:_}),n.jsx("small",{children:j})]}),n.jsx("input",{type:"checkbox",checked:!!((J=d.automod)!=null&&J[R]),onChange:S=>E("automod",R,S.target.checked)}),n.jsx("i",{"aria-hidden":"true"})]},R)})})]}),n.jsxs("section",{className:"dash-panel settings-panel",children:[n.jsx(Sn,{label:"Thresholds",title:"Choose when protection steps in",detail:"These limits apply across the server."}),n.jsxs("div",{className:"form-grid",children:[n.jsx(Je,{label:"Spam messages",hint:"Messages inside the spam interval",children:n.jsx("input",{type:"number",min:"1",max:"100",value:d.spam_threshold??6,onChange:R=>m({...d,spam_threshold:R.target.value})})}),n.jsx(Je,{label:"Spam interval (seconds)",children:n.jsx("input",{type:"number",min:"1",max:"3600",value:d.spam_interval??7,onChange:R=>m({...d,spam_interval:R.target.value})})}),n.jsx(Je,{label:"Maximum mentions",children:n.jsx("input",{type:"number",min:"1",max:"100",value:d.max_mentions??5,onChange:R=>m({...d,max_mentions:R.target.value})})}),n.jsx(Je,{label:"Anti-raid joins",hint:"Joins inside the join interval",children:n.jsx("input",{type:"number",min:"1",max:"1000",value:((N=d.antiraid)==null?void 0:N.join_threshold)??10,onChange:R=>E("antiraid","join_threshold",R.target.value)})}),n.jsx(Je,{label:"Anti-raid interval (seconds)",children:n.jsx("input",{type:"number",min:"1",max:"3600",value:((M=d.antiraid)==null?void 0:M.join_interval)??10,onChange:R=>E("antiraid","join_interval",R.target.value)})}),n.jsx(Je,{label:"Anti-raid action",children:n.jsxs("select",{value:((I=d.antiraid)==null?void 0:I.action)??"kick",onChange:R=>E("antiraid","action",R.target.value),children:[n.jsx("option",{value:"kick",children:"Kick"}),n.jsx("option",{value:"ban",children:"Ban"}),n.jsx("option",{value:"softban",children:"Soft-ban"}),n.jsx("option",{value:"slowmode",children:"Slowmode"}),n.jsx("option",{value:"lockdown",children:"Lockdown"})]})})]}),n.jsx(la,{state:p})]})]})]})}function dp({guildId:i,config:l,csrfToken:c}){var I,R;const[d,m]=T.useState({ai_name:"Niko",personality:"cafe",enabled:!0,ai_actions_experiment:!1,better_context_experiment:!1,multimodal_experiment:!1}),[p,g]=T.useState(ia),[E,b]=T.useState(null),z=_=>_===!0||_==="True",C=_=>m({ai_name:_.ai_name||"Niko",personality:_.personality==="normal"?"normal":"cafe",enabled:_.enabled!=="False"&&_.enabled!==!1,ai_actions_experiment:z(_.ai_actions_experiment),better_context_experiment:z(_.better_context_experiment),multimodal_experiment:z(_.multimodal_experiment)});T.useEffect(()=>C((l==null?void 0:l.ai)||{}),[l]);const N=_=>{_.preventDefault(),g({saving:!0,message:"",error:""}),sa(i,"ai",d,c).then(j=>{C(j.config||{}),g({saving:!1,message:"AI settings saved.",error:""})}).catch(j=>g({saving:!1,message:"",error:j instanceof Error?j.message:"Could not save settings."}))},M=[{key:"better_context_experiment",title:"Better context",hint:"Use the last five channel messages",info:"Adds recent conversation and replied-to message context so responses understand ongoing discussions more naturally. It is useful for follow-ups, but sends more conversation context to the AI provider."},{key:"ai_actions_experiment",title:"AI actions",hint:"Allow confirmed actions requested in chat",info:"Lets the AI propose polls and server actions such as moderation or channel management. Every action requires confirmation and is still limited by Discord permissions."},{key:"multimodal_experiment",title:"Multimodal conversation",hint:"Understand images and transcribe voice messages",info:"Allows Niko to inspect image attachments and use voice-message transcriptions as context. Media is processed only while enabled and provider usage costs may apply."}];return n.jsxs(n.Fragment,{children:[n.jsx(on,{eyebrow:"AI controls",title:"Give your AI the right tone.",text:"Configure the AI identity, personality, and opt-in experiments for this server."}),n.jsx(oa,{icon:"settings",label:"Conversation desk",title:d.enabled?`${d.ai_name} is ready to respond`:`${d.ai_name} is staying quiet`,text:"All settings apply only to this server."}),n.jsxs("form",{onSubmit:N,className:"settings-stack",children:[n.jsxs("section",{className:"dash-panel settings-panel",children:[n.jsx(Sn,{label:"Conversation",title:"Core settings",detail:"Decide when the AI joins the conversation.",icon:"settings"}),n.jsx("div",{className:"form-grid",children:n.jsx(Je,{label:"AI name",hint:"1–32 characters; this is also the mention trigger",children:n.jsx("input",{value:d.ai_name,maxLength:32,onChange:_=>m({...d,ai_name:_.target.value})})})}),n.jsxs("label",{className:"setting-row",children:[n.jsxs("span",{children:[n.jsx("strong",{children:"Enable AI chat"}),n.jsx("small",{children:"Respond when the configured name is mentioned"})]}),n.jsx("input",{type:"checkbox",checked:d.enabled,onChange:_=>m({...d,enabled:_.target.checked})}),n.jsx("i",{"aria-hidden":"true"})]}),n.jsxs("div",{className:"personality-options",children:[n.jsxs("button",{type:"button",className:d.personality==="cafe"?"personality active":"personality",onClick:()=>m({...d,personality:"cafe"}),children:[n.jsx("span",{className:"personality-mark",children:"n"}),n.jsxs("span",{children:[n.jsx("strong",{children:"Café"}),n.jsx("small",{children:"Warm, playful, familiar"})]})]}),n.jsxs("button",{type:"button",className:d.personality==="normal"?"personality active":"personality",onClick:()=>m({...d,personality:"normal"}),children:[n.jsx("span",{className:"personality-mark",children:"—"}),n.jsxs("span",{children:[n.jsx("strong",{children:"Normal"}),n.jsx("small",{children:"Clear and straightforward"})]})]})]})]}),n.jsxs("section",{className:"dash-panel settings-panel",children:[n.jsx(Sn,{label:"Experiments",title:"Optional capabilities",detail:"Each experiment includes a learn-more explanation before you enable it."}),M.map(_=>n.jsxs("div",{className:"setting-row",children:[n.jsxs("span",{children:[n.jsx("strong",{children:_.title}),n.jsx("small",{children:_.hint})]}),n.jsxs("div",{children:[n.jsx("button",{type:"button",className:"button button-secondary",onClick:()=>b(_.key),children:"Learn more"}),n.jsx("input",{type:"checkbox",checked:d[_.key],onChange:j=>m({...d,[_.key]:j.target.checked})}),n.jsx("i",{"aria-hidden":"true"})]})]},_.key)),n.jsx(la,{state:p})]})]}),E&&n.jsx("div",{className:"modal-backdrop",role:"presentation",onClick:()=>b(null),children:n.jsxs("div",{className:"modal-card",role:"dialog","aria-modal":"true",onClick:_=>_.stopPropagation(),children:[n.jsxs("div",{className:"panel-heading",children:[n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"AI experiment"}),n.jsx("h3",{children:(I=M.find(_=>_.key===E))==null?void 0:I.title})]}),n.jsx("button",{type:"button",className:"button button-secondary",onClick:()=>b(null),children:"Close"})]}),n.jsx("p",{children:(R=M.find(_=>_.key===E))==null?void 0:R.info})]})})]})}function mp({guildId:i,config:l,resources:c,csrfToken:d}){const m=(l==null?void 0:l.leveling)||{},[p,g]=T.useState({xp_enabled:!0,xp_multiplier:1,xp_cooldown:0,level_up_channel:"",level_up_message:""}),[E,b]=T.useState(ia);T.useEffect(()=>g({xp_enabled:m.xp_enabled!==!1,xp_multiplier:m.xp_multiplier??1,xp_cooldown:m.xp_cooldown??0,level_up_channel:m.level_up_channel?String(m.level_up_channel):"",level_up_message:m.level_up_message||""}),[l]);const z=N=>{N.preventDefault(),b({saving:!0,message:"",error:""}),sa(i,"leveling",p,d).then(M=>{const I=M.config||{};g({xp_enabled:I.xp_enabled!==!1,xp_multiplier:I.xp_multiplier??1,xp_cooldown:I.xp_cooldown??0,level_up_channel:I.level_up_channel?String(I.level_up_channel):"",level_up_message:I.level_up_message||""}),b({saving:!1,message:"Leveling settings saved to Niko.",error:""})}).catch(M=>b({saving:!1,message:"",error:M instanceof Error?M.message:"Could not save settings."}))},C=cp(c,p.level_up_channel);return n.jsxs(n.Fragment,{children:[n.jsx(oa,{icon:"spark",label:"Participation desk",title:p.xp_enabled?"XP is flowing":"XP is paused",text:"Set a pace that rewards regulars without turning every message into a transaction."}),n.jsx("form",{onSubmit:z,className:"settings-stack",children:n.jsxs("section",{className:"dash-panel settings-panel",children:[n.jsx(Sn,{label:"Leveling settings",title:"Shape the pace",detail:"These controls apply to every member in this server.",icon:"spark"}),n.jsxs("label",{className:"setting-row",children:[n.jsxs("span",{children:[n.jsx("strong",{children:"Enable XP"}),n.jsx("small",{children:"Track activity and award levels"})]}),n.jsx("input",{type:"checkbox",checked:p.xp_enabled,onChange:N=>g({...p,xp_enabled:N.target.checked})}),n.jsx("i",{"aria-hidden":"true"})]}),n.jsxs("div",{className:"form-grid",children:[n.jsx(Je,{label:"XP multiplier",hint:"From 0.1× to 10×",children:n.jsx("input",{type:"number",min:"0.1",max:"10",step:"0.1",value:p.xp_multiplier,onChange:N=>g({...p,xp_multiplier:N.target.value})})}),n.jsx(Je,{label:"Cooldown (seconds)",hint:"0 disables the cooldown",children:n.jsx("input",{type:"number",min:"0",max:"86400",value:p.xp_cooldown,onChange:N=>g({...p,xp_cooldown:N.target.value})})}),n.jsx(Je,{label:"Level-up channel",children:n.jsxs("select",{value:p.level_up_channel,onChange:N=>g({...p,level_up_channel:N.target.value}),children:[n.jsx("option",{value:"",children:"Same channel"}),C.map(N=>n.jsxs("option",{value:N.id,children:["#",N.name]},N.id))]})}),n.jsx(Je,{label:"Level-up message",hint:"Use {mention}, {level}, {name}, or {guild}",children:n.jsx("textarea",{rows:3,maxLength:1e3,value:p.level_up_message,onChange:N=>g({...p,level_up_message:N.target.value}),placeholder:"Leave blank for Niko's default message"})})]}),n.jsx(la,{state:E})]})})]})}function hp({guildId:i,config:l,csrfToken:c}){var z;const d=((z=l==null?void 0:l.server)==null?void 0:z.profile)||{},[m,p]=T.useState({display_name:d.display_name||"",bio:d.bio||"",avatar_url:d.avatar_url||"",banner_url:d.banner_url||""}),[g,E]=T.useState(ia);T.useEffect(()=>{var N;const C=((N=l==null?void 0:l.server)==null?void 0:N.profile)||{};p({display_name:C.display_name||"",bio:C.bio||"",avatar_url:C.avatar_url||"",banner_url:C.banner_url||""})},[l]);const b=C=>{C.preventDefault(),E({saving:!0,message:"",error:""}),bh(i,{display_name:m.display_name||null,bio:m.bio||null,avatar_url:m.avatar_url||null,banner_url:m.banner_url||null},c).then(N=>{const M=N.profile||{};p({display_name:M.display_name||"",bio:M.bio||"",avatar_url:M.avatar_url||"",banner_url:M.banner_url||""}),E({saving:!1,message:"Bot profile updated.",error:""})}).catch(N=>E({saving:!1,message:"",error:N instanceof Error?N.message:"Could not save profile."}))};return n.jsxs(n.Fragment,{children:[n.jsx(on,{eyebrow:"Customization",title:"Niko's server presence.",text:"Change how Niko appears in this server. Display name, avatar, banner, and bio are all per-server."}),n.jsx(oa,{icon:"paint",label:"Identity desk",title:"Server-specific identity",text:"Each server can have its own Niko persona. Changes apply only to this server."}),n.jsxs("form",{onSubmit:b,className:"settings-stack",children:[n.jsxs("section",{className:"dash-panel settings-panel",children:[n.jsx(Sn,{label:"Display name",title:"How Niko appears",detail:"Set the name members see for Niko in this server. Leave blank to use the default.",icon:"settings"}),n.jsxs("div",{className:"form-grid",children:[n.jsx(Je,{label:"Display name",hint:"32 characters or fewer",children:n.jsx("input",{value:m.display_name,maxLength:32,onChange:C=>p({...m,display_name:C.target.value}),placeholder:"Niko"})}),n.jsx(Je,{label:"Bio",hint:"190 characters or fewer",children:n.jsx("input",{value:m.bio,maxLength:190,onChange:C=>p({...m,bio:C.target.value}),placeholder:"A warm Discord companion"})})]})]}),n.jsxs("section",{className:"dash-panel settings-panel",children:[n.jsx(Sn,{label:"Server avatar & banner",title:"Visual identity",detail:"Provide HTTPS image URLs. Images are uploaded to Discord when saved.",icon:"paint"}),n.jsxs("div",{className:"form-grid",children:[n.jsx(Je,{label:"Avatar URL",hint:"Square image, 512×512 recommended",children:n.jsx("input",{type:"url",value:m.avatar_url,onChange:C=>p({...m,avatar_url:C.target.value}),placeholder:"https://cdn.example.com/avatar.png"})}),n.jsx(Je,{label:"Banner URL",hint:"Wide image, 960×540 recommended",children:n.jsx("input",{type:"url",value:m.banner_url,onChange:C=>p({...m,banner_url:C.target.value}),placeholder:"https://cdn.example.com/banner.png"})})]}),n.jsx("p",{className:"form-hint",children:"Images are fetched, validated, and uploaded to Discord. Maximum 8 MB each. Supported formats: PNG, JPG, GIF."})]}),n.jsx(la,{state:g})]})]})}const pp={saving:!1,message:"",error:""};function it({label:i,hint:l,children:c}){return n.jsxs("label",{className:"form-field",children:[n.jsx("span",{className:"form-label",children:i}),c,l&&n.jsx("small",{children:l})]})}function Xs({label:i,title:l,detail:c,icon:d}){return n.jsxs("div",{className:"panel-heading settings-section-title",children:[n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:i}),n.jsx("h3",{children:l}),n.jsx("p",{children:c})]}),n.jsx("span",{className:"panel-icon",children:n.jsx(K,{name:d})})]})}function fp({state:i}){return n.jsxs("div",{className:"setting-footer",children:[i.error?n.jsx("span",{className:"form-error",role:"alert",children:i.error}):n.jsx("span",{role:"status",children:i.message||"Changes apply to this server."}),n.jsx("button",{className:"button button-primary",type:"submit",disabled:i.saving,children:i.saving?"Saving...":"Save server settings"})]})}const gp=[["moderation","Moderation"],["automod","AutoMod"],["messages","Messages"],["channels","Channels"],["members","Members"],["captcha","Captcha"],["invites","Invites"],["roles","Roles"],["server","Server"],["voice","Voice"]];function vp(i,l){var c;return l?((c=i==null?void 0:i.channels.find(d=>d.id===String(l)))==null?void 0:c.name)||`Saved channel · ${l}`:"Not set"}function Ys(i,l){const c=l?String(l):"",d=(i==null?void 0:i.channels)||[];return!c||d.some(m=>m.id===c)?d:[{id:c,name:`Saved channel · ${c}`},...d]}function Ou(i,l=[]){const c=(i==null?void 0:i.roles)||[],d=new Set(c.map(p=>p.id));return[...l.map(String).filter((p,g,E)=>p&&!d.has(p)&&E.indexOf(p)===g).map(p=>({id:p,name:`Unavailable role (${p})`})),...c]}function mo(i){var d,m;const l=(i==null?void 0:i.onboarding)||{},c=(i==null?void 0:i.tickets)||{};return{prefixes:((d=i==null?void 0:i.prefixes)!=null&&d.length?i.prefixes:["."]).join(`
`),welcome_channel:l.welcome_channel?String(l.welcome_channel):"",welcome_title:l.welcome_title||"",welcome_description:l.welcome_description||"",welcome_color:l.welcome_color===null||l.welcome_color===void 0?"5865F2":l.welcome_color.toString(16).padStart(6,"0"),welcome_image:l.welcome_image||"",rules_channel:l.rules_channel?String(l.rules_channel):"",rules_text:l.rules_text||"",rules_role_id:l.rules_role_id?String(l.rules_role_id):"",logging:Object.fromEntries(Object.entries((i==null?void 0:i.logging)||{}).map(([p,g])=>[p,g==null?"":String(g)])),disabled_logging:[...((m=i==null?void 0:i.logging)==null?void 0:m.disabled)||[]].map(String),panel_title:c.panel_title||"",panel_description:c.panel_description||"",panel_categories:(c.panel_categories||[]).join(`
`),panel_channel_id:c.panel_channel_id?String(c.panel_channel_id):"",support_roles:[...c.support_roles||[]].map(String)}}function yp({guildId:i,config:l,resources:c,csrfToken:d}){const[m,p]=T.useState(()=>mo(l==null?void 0:l.server)),[g,E]=T.useState(pp);T.useEffect(()=>{l!=null&&l.server&&p(mo(l.server))},[l]);const b=(S,V)=>p(ee=>({...ee,[S]:V})),z=(S,V)=>p(ee=>({...ee,logging:{...ee.logging,[S]:V}})),C=S=>p(V=>({...V,disabled_logging:V.disabled_logging.includes(S)?V.disabled_logging.filter(ee=>ee!==S):[...V.disabled_logging,S]})),N=S=>{S.preventDefault(),E({saving:!0,message:"",error:""});const V=m.prefixes.split(/\r?\n|,/).map(se=>se.trim()).filter(Boolean),ee=m.panel_categories.split(/\r?\n|,/).map(se=>se.trim()).filter(Boolean);sa(i,"server",{prefixes:V,onboarding:{welcome_channel:m.welcome_channel,welcome_title:m.welcome_title,welcome_description:m.welcome_description,welcome_color:m.welcome_color,welcome_image:m.welcome_image,rules_channel:m.rules_channel,rules_text:m.rules_text,rules_role_id:m.rules_role_id},logging:{...m.logging,disabled:m.disabled_logging},tickets:{panel_title:m.panel_title,panel_description:m.panel_description,panel_categories:ee,panel_channel_id:m.panel_channel_id,support_roles:m.support_roles}},d).then(se=>{p(mo(se.config)),E({saving:!1,message:"Server settings saved to Niko.",error:""})}).catch(se=>E({saving:!1,message:"",error:se instanceof Error?se.message:"Could not save server settings."}))},M=m.welcome_channel,I=m.panel_channel_id,R=Ys(c,m.welcome_channel),_=Ys(c,m.rules_channel),j=Ys(c,m.panel_channel_id),J=Ou(c,m.support_roles);return n.jsxs(n.Fragment,{children:[n.jsx(on,{eyebrow:"Server settings",title:"Make Niko fit your room.",text:"Manage the settings that shape how Niko behaves in this server. Economy balances remain global to each user and are not configured here."}),n.jsxs("div",{className:"settings-intro",children:[n.jsx("span",{className:"settings-intro-icon",children:n.jsx(K,{name:"settings"})}),n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"Server control room"}),n.jsxs("strong",{children:[m.prefixes.split(/\r?\n|,/).filter(Boolean).length||0," command prefixes configured"]}),n.jsx("p",{children:"Welcome flows, log destinations, and ticket panels all live here."})]}),n.jsxs("span",{className:"settings-intro-state",children:[n.jsx("span",{className:"status-dot"})," Per server"]})]}),n.jsxs("form",{onSubmit:N,className:"settings-stack server-settings-stack",children:[n.jsxs("section",{className:"dash-panel settings-panel",children:[n.jsx(Xs,{label:"Commands",title:"Prefixes",detail:"Use one prefix per line. Niko will respond to all of them.",icon:"terminal"}),n.jsx(it,{label:"Command prefixes",hint:"The default prefix is .",children:n.jsx("textarea",{rows:3,maxLength:200,value:m.prefixes,onChange:S=>b("prefixes",S.target.value),placeholder:".\\n!"})})]}),n.jsxs("section",{className:"dash-panel settings-panel",children:[n.jsx(Xs,{label:"Welcome flow",title:"Welcome and rules",detail:"Choose where new members see your welcome message and rules.",icon:"users"}),n.jsxs("div",{className:"form-grid",children:[n.jsx(it,{label:"Welcome channel",children:n.jsxs("select",{value:M,onChange:S=>b("welcome_channel",S.target.value),children:[n.jsx("option",{value:"",children:"Disabled"}),R.map(S=>n.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),n.jsx(it,{label:"Welcome title",children:n.jsx("input",{value:m.welcome_title,maxLength:200,onChange:S=>b("welcome_title",S.target.value),placeholder:"Welcome to the server"})}),n.jsx(it,{label:"Welcome message",hint:"Supports {user} and {name}",children:n.jsx("textarea",{rows:4,maxLength:2e3,value:m.welcome_description,onChange:S=>b("welcome_description",S.target.value),placeholder:"Welcome {user}!"})}),n.jsx(it,{label:"Accent color",hint:"Hex color, for example 5865F2",children:n.jsx("input",{value:m.welcome_color,maxLength:7,onChange:S=>b("welcome_color",S.target.value),placeholder:"5865F2"})}),n.jsx(it,{label:"Welcome image URL",children:n.jsx("input",{type:"url",value:m.welcome_image,onChange:S=>b("welcome_image",S.target.value),placeholder:"https://..."})}),n.jsx(it,{label:"Rules channel",children:n.jsxs("select",{value:m.rules_channel,onChange:S=>b("rules_channel",S.target.value),children:[n.jsx("option",{value:"",children:"Not configured"}),_.map(S=>n.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),n.jsx(it,{label:"Rules text",children:n.jsx("textarea",{rows:4,maxLength:2e3,value:m.rules_text,onChange:S=>b("rules_text",S.target.value),placeholder:"Write the rules members should acknowledge."})}),n.jsx(it,{label:"Role after rules acknowledgment",children:n.jsxs("select",{value:m.rules_role_id,onChange:S=>b("rules_role_id",S.target.value),children:[n.jsx("option",{value:"",children:"No role"}),Ou(c,m.rules_role_id?[m.rules_role_id]:[]).map(S=>n.jsxs("option",{value:S.id,children:["@",S.name]},S.id))]})})]})]}),n.jsxs("section",{className:"dash-panel settings-panel",children:[n.jsx(Xs,{label:"Audit trail",title:"Logging destinations",detail:"Pick a channel for each event type and disable categories you do not need.",icon:"book"}),n.jsx("div",{className:"server-logging-list",children:gp.map(([S,V])=>{const ee=Ys(c,m.logging[S]);return n.jsxs("div",{className:"server-logging-row",children:[n.jsxs("label",{className:"form-field",children:[n.jsxs("span",{className:"form-label",children:[V," logs"]}),n.jsxs("select",{value:String(m.logging[S]||""),onChange:se=>z(S,se.target.value),children:[n.jsx("option",{value:"",children:"Not set"}),ee.map(se=>n.jsxs("option",{value:se.id,children:["#",se.name]},se.id))]})]}),n.jsxs("label",{className:"setting-row compact-setting-row",children:[n.jsxs("span",{children:[n.jsx("strong",{children:"Enabled"}),n.jsx("small",{children:vp(c,m.logging[S])})]}),n.jsx("input",{type:"checkbox",checked:!m.disabled_logging.includes(S),onChange:()=>C(S)}),n.jsx("i",{"aria-hidden":"true"})]})]},S)})})]}),n.jsxs("section",{className:"dash-panel settings-panel",children:[n.jsx(Xs,{label:"Support desk",title:"Ticket panel",detail:"Configure the public panel and decide who can handle tickets.",icon:"users"}),n.jsxs("div",{className:"form-grid",children:[n.jsx(it,{label:"Panel title",children:n.jsx("input",{value:m.panel_title,maxLength:200,onChange:S=>b("panel_title",S.target.value),placeholder:"Open a Ticket"})}),n.jsx(it,{label:"Panel channel",children:n.jsxs("select",{value:I,onChange:S=>b("panel_channel_id",S.target.value),children:[n.jsx("option",{value:"",children:"Keep current panel channel"}),j.map(S=>n.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),n.jsx(it,{label:"Panel description",children:n.jsx("textarea",{rows:4,maxLength:2e3,value:m.panel_description,onChange:S=>b("panel_description",S.target.value),placeholder:"Tell members what the ticket panel is for."})}),n.jsx(it,{label:"Ticket categories",hint:"One category per line",children:n.jsx("textarea",{rows:4,value:m.panel_categories,onChange:S=>b("panel_categories",S.target.value),placeholder:"General\\nSupport\\nReports"})}),n.jsx(it,{label:"Support roles",hint:"Hold Ctrl/Cmd to select more than one",children:n.jsx("select",{multiple:!0,value:m.support_roles,onChange:S=>b("support_roles",Array.from(S.target.selectedOptions,V=>V.value)),children:J.map(S=>n.jsxs("option",{value:S.id,children:["@",S.name]},S.id))})})]}),n.jsx("p",{className:"form-hint",children:"Saving panel settings updates the existing posted panel when Niko can find its saved message."})]}),n.jsx(fp,{state:g})]})]})}function xp({auth:i}){const l=aa();return n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"dashboard"}),n.jsx("main",{className:"auth-page",children:n.jsxs("div",{className:"auth-card",children:[n.jsx("span",{className:"auth-mark",children:"n"}),n.jsx("div",{className:"eyebrow",children:"Private workspace"}),n.jsxs("h1",{children:["Settle in, ",n.jsx("em",{children:"admin."})]}),n.jsx("p",{children:"Sign in with Discord to see your Niko profile and manage the servers you look after."}),i.oauth_available?n.jsxs("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard",children:[n.jsx(K,{name:"lock"})," Continue with Discord ",n.jsx(K,{name:"arrow"})]}):n.jsxs("div",{className:"notice warning",children:["Discord login is not configured yet. Add ",n.jsx("code",{children:"DISCORD_CLIENT_SECRET"})," to the environment and restart the bot."]}),!l&&n.jsx("p",{className:"form-hint",children:"The public bot configuration is still loading."}),n.jsx("a",{className:"back-link",href:"/",onClick:c=>{c.preventDefault(),le("/")},children:"Return to public site"})]})})]})}function kp({section:i,guild:l,stats:c,csrfToken:d,refreshToken:m}){const[p,g]=T.useState(null),[E,b]=T.useState([]),[z,C]=T.useState(null),[N,M]=T.useState(null),[I,R]=T.useState(!0),[_,j]=T.useState("");return T.useEffect(()=>{R(!0),j(""),(i==="overview"?kh(l.id).then(g):i==="leveling"?Promise.all([wh(l.id),Tu(l.id),Eu(l.id)]).then(([S,V,ee])=>{b(S),C(V),M(ee)}):Promise.all([Tu(l.id),Eu(l.id)]).then(([S,V])=>{C(S),M(V)})).catch(S=>j(S instanceof Error?S.message:"This server could not be loaded.")).finally(()=>R(!1))},[l.id,i,m]),I?n.jsxs("div",{className:"section-loading section-skeleton",role:"status","aria-label":`Loading ${i}`,children:[n.jsx("div",{className:"skeleton-title"}),n.jsx("div",{className:"skeleton-copy"}),n.jsxs("div",{className:"skeleton-grid",children:[n.jsx("i",{}),n.jsx("i",{}),n.jsx("i",{})]}),n.jsxs("span",{children:["Loading ",i,"..."]})]}):_?n.jsxs("div",{className:"inline-error",role:"alert",children:[n.jsx("strong",{children:"Couldn’t load this page."}),n.jsx("span",{children:_}),n.jsx("button",{className:"button button-muted",onClick:()=>window.location.reload(),children:"Try again"})]}):i==="overview"&&p?n.jsx(op,{overview:p}):i==="leveling"?n.jsx(lp,{guildId:l.id,rows:E,config:z,resources:N,csrfToken:d}):i==="moderation"?n.jsx(up,{guildId:l.id,config:z,csrfToken:d}):i==="server"?n.jsx(yp,{guildId:l.id,config:z,resources:N,csrfToken:d}):i==="customization"?n.jsx(hp,{guildId:l.id,config:z,csrfToken:d}):n.jsx(dp,{guildId:l.id,config:z,csrfToken:d})}function wp(){return n.jsxs("div",{className:"section-loading section-skeleton dashboard-loading",role:"status",children:[n.jsx("div",{className:"skeleton-title"}),n.jsx("div",{className:"skeleton-copy"}),n.jsxs("div",{className:"skeleton-grid",children:[n.jsx("i",{}),n.jsx("i",{}),n.jsx("i",{})]}),n.jsx("span",{children:"Preparing your dashboard..."})]})}function bp(){aa();const[i,l]=T.useState(Pu),[c,d]=T.useState(null),[m,p]=T.useState(null),[g,E]=T.useState(null),[b,z]=T.useState([]),[C,N]=T.useState(null),[M,I]=T.useState(!0),[R,_]=T.useState(""),[j,J]=T.useState(0),[S,V]=T.useState(!1),[ee,se]=T.useState(null);if(T.useEffect(()=>{const re=()=>l(Pu());return window.addEventListener("popstate",re),()=>window.removeEventListener("popstate",re)},[]),T.useEffect(()=>{I(!0),Promise.all([fo(),ea()]).then(([re,Le])=>(d(re),p(Le),re.authenticated?Promise.all([_u(),vo(),go().catch(()=>null)]).then(([He,Fe,he])=>{E(He),z(Fe),se((he==null?void 0:he.role)||null)}):null)).catch(re=>_(re instanceof Error?re.message:"Dashboard unavailable")).finally(()=>I(!1))},[]),T.useEffect(()=>{if(i.view!=="guild"){N(null);return}const re=b.find(Le=>Le.id===i.guildId&&Le.installed!==!1);re?(N(re),localStorage.setItem("niko-guild",re.id)):i.guildId&&b.length&&le(yo())},[b,i.guildId,i.view]),M||!c)return n.jsxs("div",{className:"dashboard-state",children:[n.jsx("div",{className:"loading-ring"}),n.jsx("p",{children:"Connecting to Niko…"})]});if(R)return n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"dashboard"}),n.jsx("main",{className:"auth-page",children:n.jsxs("div",{className:"auth-card",children:[n.jsx("span",{className:"auth-mark",children:"!"}),n.jsx("div",{className:"eyebrow",children:"Connection issue"}),n.jsxs("h1",{children:["Couldn’t load",n.jsx("br",{}),n.jsx("em",{children:"your workspace."})]}),n.jsx("p",{children:R}),n.jsxs("button",{className:"button button-primary",onClick:()=>window.location.reload(),children:["Try again ",n.jsx(K,{name:"arrow"})]})]})})]});if(!c.authenticated)return n.jsx(xp,{auth:c});const B=re=>{re.installed!==!1&&(localStorage.setItem("niko-guild",re.id),le(Xn(re.id,i.section)))},Q=re=>{re.installed!==!1&&(localStorage.setItem("niko-guild",re.id),le(Xn(re.id,"overview")))},pe=re=>{le(C?Xn(C.id,re):Xn())},ne=()=>le(Xn()),je=()=>le(yo()),Te=async()=>{if(!S){V(!0);try{const[re,Le]=await Promise.all([fo(),ea()]);if(d(re),p(Le),re.authenticated){const[He,Fe,he]=await Promise.all([_u(),vo(),go().catch(()=>null)]);E(He),z(Fe),se((he==null?void 0:he.role)||null)}J(He=>He+1),_("")}catch(re){_(re instanceof Error?re.message:"Dashboard refresh failed")}finally{V(!1)}}};let Se;return i.view==="servers"?Se=n.jsx(ip,{guilds:b,onManage:Q}):i.view==="guild"?Se=C?n.jsx(kp,{section:i.section,guild:C,stats:m,csrfToken:c.csrf_token,refreshToken:j},`${C.id}-${i.section}`):n.jsx(wp,{}):Se=n.jsx(ap,{user:c.user,overview:g,guilds:b,onServers:je,onManage:Q}),n.jsx(Xu,{user:c.user,guilds:b,selectedGuild:C,view:i.view,section:i.section,stats:m,onHome:ne,onServers:je,onGuildChange:B,onSectionChange:pe,onRefresh:Te,refreshing:S,staffRole:ee,children:Se})}function jp({value:i,onChange:l,placeholder:c="Search documentation...",onFocus:d,onBlur:m}){const[p,g]=T.useState(!1),E=T.useRef(null),[b,z]=T.useState(!1);T.useEffect(()=>{const R=_=>{var j;(_.metaKey||_.ctrlKey)&&_.key==="k"&&(_.preventDefault(),(j=E.current)==null||j.focus())};return document.addEventListener("keydown",R),()=>document.removeEventListener("keydown",R)},[]);const C=()=>{g(!0),z(!0),d==null||d()},N=()=>{g(!1),setTimeout(()=>z(!1),200),m==null||m()},M=R=>{l(R.target.value)},I=R=>{var _;R.key==="Escape"&&((_=E.current)==null||_.blur())};return n.jsxs("div",{className:`doc-search-bar ${b?"expanded":""}`,children:[n.jsxs("div",{className:"search-input-wrapper",children:[n.jsx(K,{name:"search",className:"search-icon"}),n.jsx("input",{ref:E,type:"text",value:i,onChange:M,onFocus:C,onBlur:N,onKeyDown:I,placeholder:c,className:"search-input","aria-label":"Search documentation"}),n.jsxs("kbd",{className:"search-shortcut",children:[n.jsx("span",{className:"shortcut-key",children:"⌘"}),"K"]})]}),n.jsxs("div",{className:"search-hint",children:["Press ",n.jsx("kbd",{children:"⌘K"})," to focus search"]})]})}function Sp({selectedCategory:i,onSelectCategory:l,sections:c,allCategoriesLabel:d="All Categories"}){return n.jsx("div",{className:"doc-filters",children:n.jsxs("div",{className:"filter-tabs",role:"tablist","aria-label":"Filter by category",children:[n.jsx("button",{role:"tab","aria-selected":i==="",className:`filter-tab ${i===""?"active":""}`,onClick:()=>l(""),children:d}),c.map(m=>n.jsxs("button",{role:"tab","aria-selected":i===m.id,className:`filter-tab ${i===m.id?"active":""}`,onClick:()=>l(m.id),children:[n.jsx(K,{name:m.icon,size:14}),n.jsx("span",{children:m.label})]},m.id))]})})}function ho({doc:i,variant:l="default"}){const c="page"in i?i.page:i,[d,m]=T.useState(!1),p=b=>{b.preventDefault(),le(`/docs/${c.slug}`)},g=b=>{(b.key==="Enter"||b.key===" ")&&(b.preventDefault(),le(`/docs/${c.slug}`))};if(l==="compact")return n.jsx("a",{href:`/docs/${c.slug}`,onClick:p,onKeyDown:g,className:"doc-card-compact",tabIndex:0,role:"button",children:n.jsxs("div",{className:"compact-content",children:[n.jsx("span",{className:"compact-title",children:c.title}),n.jsx("span",{className:"compact-excerpt",children:c.excerpt})]})});const E="highlights"in i?i.highlights:[];return n.jsx("article",{className:`doc-card ${l==="highlighted"?"highlighted":""}`,children:n.jsxs("div",{className:`doc-card-content ${d?"loaded":""}`,children:[n.jsxs("div",{className:"doc-card-header",children:[n.jsx("span",{className:"doc-category",children:c.category.replace(/-/g," ")}),n.jsxs("span",{className:"doc-order",children:["#",c.order]})]}),n.jsx("h3",{className:"doc-title",children:c.title}),n.jsx("p",{className:"doc-excerpt",children:c.excerpt}),E.length>0&&n.jsx("div",{className:"doc-highlights",children:E.slice(0,2).map((b,z)=>n.jsxs("p",{className:"highlight-snippet",children:[b.slice(0,150),b.length>150?"...":""]},z))}),n.jsxs("div",{className:"doc-card-footer",children:[n.jsx("div",{className:"doc-tags",children:c.tags.slice(0,3).map(b=>n.jsxs("span",{className:"doc-tag",children:["#",b]},b))}),n.jsxs("a",{href:`/docs/${c.slug}`,onClick:p,onKeyDown:g,className:"doc-read-more",children:["Read more ",n.jsx(K,{name:"arrow",size:14})]})]})]})})}const De=[{slug:"welcome",title:"Welcome to Niko",category:"getting-started",excerpt:"New to Niko? Start here to understand what the bot can do for your server.",tags:["introduction","overview","beginner"],order:1,content:`
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
    `}];function Np(i){return De.find(l=>l.slug===i)}const an=[{id:"getting-started",label:"Getting Started",description:"New to Niko? Start here.",icon:"icon_home",count:De.filter(i=>i.category==="getting-started").length},{id:"setup",label:"Setup",description:"Configure Niko for your server.",icon:"icon_settings",count:De.filter(i=>i.category==="setup").length},{id:"economy",label:"Economy",description:"Money, jobs, banking, and more.",icon:"icon_economy",count:De.filter(i=>i.category==="economy").length},{id:"leveling",label:"Leveling",description:"XP, levels, and rankings.",icon:"icon_leveling",count:De.filter(i=>i.category==="leveling").length},{id:"moderation",label:"Moderation",description:"Moderation tools and commands.",icon:"icon_moderation",count:De.filter(i=>i.category==="moderation").length},{id:"automod",label:"AutoMod",description:"Automated moderation features.",icon:"icon_automod",count:De.filter(i=>i.category==="automod").length},{id:"logging",label:"Logging",description:"Server event logging.",icon:"icon_settings",count:De.filter(i=>i.category==="logging").length},{id:"social",label:"Social",description:"Community engagement features.",icon:"icon_heart",count:De.filter(i=>i.category==="social").length},{id:"utility",label:"Utility",description:"Helpful tools and utilities.",icon:"icon_utility",count:De.filter(i=>i.category==="utility").length},{id:"voice",label:"Voice",description:"Voice and music features.",icon:"icon_bot",count:De.filter(i=>i.category==="voice").length},{id:"ai",label:"AI",description:"AI-powered features.",icon:"icon_ai",count:De.filter(i=>i.category==="ai").length},{id:"dashboard",label:"Dashboard",description:"Web dashboard guides.",icon:"icon_settings",count:De.filter(i=>i.category==="dashboard").length},{id:"tips",label:"Tips",description:"Tips and best practices.",icon:"icon_lightbulb",count:De.filter(i=>i.category==="tips").length}];function Ju(){const[i,l]=T.useState({query:"",category:"",tags:[]}),c=T.useCallback(b=>{l(z=>({...z,query:b.toLowerCase(),tags:[]}))},[]),d=T.useCallback(b=>{l(z=>({...z,category:b,tags:[]}))},[]),m=T.useCallback(b=>{l(z=>{const C=z.tags.includes(b)?z.tags.filter(N=>N!==b):[...z.tags,b];return{...z,tags:C,query:""}})},[]),p=T.useCallback(()=>{l({query:"",category:"",tags:[]})},[]),g=T.useMemo(()=>{const{query:b,category:z,tags:C}=i;if(!b&&!z&&C.length===0)return De.map(M=>({page:M,score:1,highlights:[]}));const N=[];for(const M of De)if(!(z&&M.category!==z)&&!(C.length>0&&!C.some(I=>M.tags.includes(I))))if(b){const I=Cp(M,b);if(I===0)continue;const R=_p(M,b);N.push({page:M,score:I,highlights:R})}else N.push({page:M,score:1,highlights:[]});return N.sort((M,I)=>I.score!==M.score?I.score-M.score:M.page.order-I.page.order),N},[i]),E=i.query!==""||i.category!==""||i.tags.length>0;return{filters:i,setQuery:c,setCategory:d,toggleTag:m,clearFilters:p,results:g,hasActiveFilters:E,resultCount:g.length}}function Cp(i,l){let c=0;const d=l.toLowerCase();i.title.toLowerCase()===d?c+=100:i.title.toLowerCase().includes(d)&&(c+=50),i.excerpt.toLowerCase().includes(d)&&(c+=25),i.content.toLowerCase().includes(d)&&(c+=10);for(const m of i.tags)m.toLowerCase().includes(d)&&(c+=15);return i.category.toLowerCase().includes(d)&&(c+=5),c}function _p(i,l){const c=[],d=l.toLowerCase(),m=3;if(i.title.toLowerCase().includes(d)&&(c.push(i.title),c.length>=m)||i.excerpt.toLowerCase().includes(d)&&(c.push(i.excerpt),c.length>=m))return c;const p=i.content.split(`
`).filter(g=>g.trim());for(const g of p)if(g.toLowerCase().includes(d)){const E=g.replace(/#{1,6}\s?/g,"").trim();if(E.length>10&&(c.push(E),c.length>=m))break}return c}function Tp(){return T.useMemo(()=>{const l={};return De.forEach(c=>{c.tags.forEach(d=>{l[d]=(l[d]||0)+1})}),Object.entries(l).map(([c,d])=>({tag:c,count:d})).sort((c,d)=>d.count-c.count)},[])}function Ep({slug:i}){var b,z;const{setCategory:l,clearFilters:c}=Ju();T.useEffect(()=>{window.location.hash!==`#/docs/${i}`&&window.history.replaceState(null,"",`#/docs/${i}`)},[i]);const d=Np(i);if(!d)return n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"docs"}),n.jsx("main",{className:"shell page-main docs-page",children:n.jsxs("div",{className:"docs-not-found",children:[n.jsx(K,{name:"doc",size:48,className:"not-found-icon"}),n.jsx("h1",{children:"Page Not Found"}),n.jsxs("p",{children:[`We couldn't find documentation for "`,i,'".']}),n.jsxs("div",{className:"not-found-actions",children:[n.jsx("button",{onClick:()=>le("/docs"),children:"Browse all documentation"}),n.jsx("button",{onClick:()=>{le("/docs"),c()},children:"Clear filters"})]})]})}),n.jsx(Nt,{})]});const m=C=>{const N=[],M=/(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*)/g;let I=0,R,_=0;for(;(R=M.exec(C))!==null;){R.index>I&&N.push(C.slice(I,R.index));const j=R[0];if(j.startsWith("`")&&j.endsWith("`")&&j.length>2)N.push(n.jsx("code",{className:"doc-inline-code",children:j.slice(1,-1)},_++));else if(j.startsWith("[")){const J=j.match(/^\[([^\]]+)\]\(([^)]+)\)$/);J?N.push(n.jsx("a",{href:J[2],target:"_blank",rel:"noreferrer",children:m(J[1])},_++)):N.push(j)}else j.startsWith("**")?N.push(n.jsx("strong",{children:m(j.slice(2,-2))},_++)):j.startsWith("*")?N.push(n.jsx("em",{children:m(j.slice(1,-1))},_++)):N.push(j);I=R.index+j.length}return I<C.length&&N.push(C.slice(I)),N},g=(C=>{const N=C.split(`
`),M=[];let I=0,R=null,_=[];const j=()=>{if(_.length===0)return;const S=R==="ol"?"ol":"ul";M.push(n.jsx(S,{className:`doc-content-list ${R==="ol"?"doc-content-list-ol":""}`,children:_.map((V,ee)=>n.jsx("li",{children:m(V)},ee))},`list-${M.length}`)),_=[],R=null},J=()=>{var ee;const S=M[M.length-1];T.isValidElement(S)&&((ee=S.props)==null?void 0:ee.className)==="doc-content-spacer"||M.push(n.jsx("div",{className:"doc-content-spacer"},`spacer-${M.length}`))};for(;I<N.length;){const V=N[I].trim();if(!V){j(),J(),I+=1;continue}if(V.startsWith("```")){j();const B=[];let Q=I+1;for(;Q<N.length&&N[Q].trim()!=="```";)B.push(N[Q]),Q+=1;M.push(n.jsx("pre",{className:"doc-code-block",children:n.jsx("code",{children:B.join(`
`)})},`code-${I}`)),I=Q+1;continue}if(V.startsWith("|")){j();const B=[];let Q=I;for(;Q<N.length&&N[Q].trim().startsWith("|");){const Te=N[Q].trim().replace(/^\|/,"").replace(/\|$/,"").split("|").map(Se=>Se.trim());B.push(Te),Q+=1}const pe=B.length>1&&B[1].every(Te=>/^:?-{2,}:?$/.test(Te.replace(/\s+/g,""))),ne=B[0],je=pe?B.slice(2):B.slice(1);ne.length>1&&M.push(n.jsxs("table",{className:"doc-table",children:[n.jsx("thead",{children:n.jsx("tr",{children:ne.map((Te,Se)=>n.jsx("th",{children:m(Te)},Se))})}),n.jsx("tbody",{children:je.map((Te,Se)=>n.jsx("tr",{children:Te.map((re,Le)=>n.jsx("td",{children:m(re)},Le))},Se))})]},`table-${I}`)),I=Q;continue}if(V.startsWith("### ")){j(),M.push(n.jsx("h4",{className:"doc-heading doc-heading-h4",children:V.slice(4)},`h-${I}`)),I+=1;continue}if(V.startsWith("## ")){j(),M.push(n.jsx("h3",{className:"doc-heading doc-heading-h3",children:V.slice(3)},`h-${I}`)),I+=1;continue}if(V.startsWith("# ")){j(),M.push(n.jsx("h2",{className:"doc-heading doc-heading-h2",children:V.slice(2)},`h-${I}`)),I+=1;continue}if(V.startsWith("> ")){j(),M.push(n.jsx("blockquote",{className:"doc-blockquote",children:m(V.slice(2))},`q-${I}`)),I+=1;continue}const ee=V.match(/^[-*]\s+(.*)$/);if(ee){R!=="ul"&&j(),R="ul",_.push(ee[1]),I+=1;continue}const se=V.match(/^\d+\.\s+(.*)$/);if(se){R!=="ol"&&j(),R="ol",_.push(se[1]),I+=1;continue}j(),M.push(n.jsx("p",{className:"doc-paragraph",children:m(V)},`p-${I}`)),I+=1}return j(),M})(d.content),E=g.filter(C=>T.isValidElement(C)&&(C.type==="h2"||C.type==="h3"));return n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"docs"}),n.jsxs("main",{className:"shell page-main docs-page docs-detail-page",children:[n.jsx("div",{className:"docs-detail-back",children:n.jsxs("button",{onClick:()=>le("/docs"),className:"back-button",children:[n.jsx(K,{name:"arrow",size:16}),"Back to Documentation"]})}),n.jsxs("header",{className:"doc-article-header",children:[n.jsxs("div",{className:"doc-article-meta",children:[n.jsx("span",{className:"doc-category-badge",children:((b=an.find(C=>C.id===d.category))==null?void 0:b.label)||d.category}),n.jsxs("span",{className:"doc-order-badge",children:["Article #",d.order]})]}),n.jsx("h1",{className:"doc-article-title",children:d.title}),n.jsx("p",{className:"doc-article-excerpt",children:d.excerpt}),n.jsx("div",{className:"doc-article-tags",children:d.tags.map(C=>n.jsxs("span",{className:"doc-tag-pill",children:["#",C]},C))})]}),n.jsx("article",{className:"doc-article-content",children:g}),n.jsx("footer",{className:"doc-article-footer",children:n.jsx("div",{className:"doc-nav-container",children:n.jsxs("div",{className:"doc-nav-col",children:[n.jsx("span",{className:"doc-nav-label",children:"Category"}),n.jsxs("button",{className:"doc-nav-link",onClick:()=>{l(d.category),le("/docs")},children:[n.jsx(K,{name:"arrow",size:14}),"View all ",(z=an.find(C=>C.id===d.category))==null?void 0:z.label]})]})})}),E.length>0&&n.jsxs("aside",{className:"doc-toc",children:[n.jsxs("div",{className:"toc-title",children:[n.jsx(K,{name:"utility",size:16}),n.jsx("span",{children:"On this page"})]}),n.jsx("nav",{className:"toc-nav",children:E.map((C,N)=>{var I;const M=(I=C.props.className)==null?void 0:I.includes("doc-heading-h2");return n.jsx("a",{href:`#${M?"h2-":"h3-"}-${N}`,className:`toc-link ${M?"toc-h2":"toc-h3"}`,children:C.props.children},N)})})]})]}),n.jsx(Nt,{})]})}function Mp(){var ee,se;const[i,l]=T.useState(!1),[c,d]=T.useState(""),[m,p]=T.useState(!1),{filters:g,setQuery:E,setCategory:b,toggleTag:z,clearFilters:C,results:N,hasActiveFilters:M,resultCount:I}=Ju(),R=Tp();T.useEffect(()=>{const B=()=>{const Q=window.location.hash.slice(1);if(Q.startsWith("#/docs/")){const pe=Q.replace("#/docs/",""),ne=De.find(je=>je.slug===pe);ne&&(d(ne.category),b(ne.category))}};return B(),window.addEventListener("hashchange",B),()=>window.removeEventListener("hashchange",B)},[]);const _=()=>{p(!0)},j=B=>{d(B),b(B),l(!1)},J=()=>{g.query||p(!1)},S=B=>{le(`/docs/${B}`),E(""),p(!1)},V=T.useMemo(()=>{const B={};return N.forEach(Q=>{const pe=Q.page.category;B[pe]||(B[pe]=[]),B[pe].push(Q)}),B},[N]);return n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"docs"}),n.jsxs("main",{className:"shell page-main docs-page",children:[n.jsx("div",{className:"docs-hero",children:n.jsxs("div",{className:"docs-hero-content",children:[n.jsx("div",{className:"eyebrow docs-eyebrow",children:"Documentation Center"}),n.jsxs("h1",{className:"docs-title",children:["Everything you need to know about",n.jsx("br",{}),n.jsx("span",{className:"title-accent",children:"using Niko"})]}),n.jsx("p",{className:"docs-subtitle",children:"Comprehensive guides, command references, and tips to help you get the most out of your server bot."})]})}),n.jsx("div",{className:`docs-search-section ${m?"active":""}`,children:n.jsxs("div",{className:"docs-search-container",children:[n.jsx(jp,{value:g.query,onChange:E,placeholder:"Search documentation, commands, guides...",onFocus:_,onBlur:J}),m&&g.query&&N.length>0&&n.jsxs("div",{className:"search-results-dropdown",children:[n.jsxs("div",{className:"search-results-header",children:[n.jsxs("span",{className:"results-count",children:[I," ",I===1?"result":"results"]}),n.jsx("button",{className:"clear-search-btn",onClick:()=>{E(""),C(),d("")},children:"Clear"})]}),n.jsx("div",{className:"search-results-list",children:N.slice(0,8).map((B,Q)=>n.jsxs("button",{className:"search-result-item",onClick:()=>S(B.page.slug),onMouseEnter:()=>{},children:[n.jsx("div",{className:"result-icon",children:n.jsx(K,{name:"doc",size:18})}),n.jsxs("div",{className:"result-content",children:[n.jsx("div",{className:"result-title",children:B.page.title}),n.jsx("div",{className:"result-excerpt",children:B.page.excerpt}),B.highlights.length>0&&n.jsxs("div",{className:"result-highlight",children:[B.highlights[0].slice(0,100),"..."]})]}),n.jsx(K,{name:"arrow",size:14,className:"result-arrow"})]},B.page.slug))}),N.length>8&&n.jsx("div",{className:"search-results-footer",children:n.jsxs("span",{children:["Showing 8 of ",N.length," results. Browse all docs below."]})})]})]})}),n.jsxs("div",{className:"docs-mobile-nav",children:[n.jsx("button",{className:"mobile-menu-toggle",onClick:()=>l(!i),"aria-label":"Toggle documentation menu",children:n.jsx(K,{name:"utility",size:20})}),i&&n.jsxs("div",{className:"mobile-nav-panel",children:[n.jsxs("div",{className:"mobile-nav-header",children:[n.jsx("h3",{children:"Documentation"}),n.jsx("button",{className:"close-menu-btn",onClick:()=>l(!1),"aria-label":"Close menu",children:n.jsx(K,{name:"utility",size:16,className:"rotated"})})]}),n.jsx("div",{className:"mobile-nav-sections",children:an.map(B=>n.jsxs("button",{className:`mobile-nav-item ${c===B.id?"active":""}`,onClick:()=>{j(B.id)},children:[n.jsx(K,{name:B.icon,size:18}),n.jsx("span",{className:"mobile-section-label",children:B.label}),n.jsx("span",{className:"mobile-section-count",children:B.count})]},B.id))})]})]}),R.length>0&&!M&&n.jsxs("div",{className:"docs-tags-cloud",children:[n.jsxs("div",{className:"tags-cloud-title",children:[n.jsx(K,{name:"utility",size:16}),n.jsx("span",{children:"Popular Topics"})]}),n.jsx("div",{className:"tags-cloud-list",children:R.slice(0,15).map(({tag:B,count:Q})=>n.jsxs("button",{className:"tag-cloud-item",onClick:()=>z(B),style:{fontSize:`${.75+Math.min(Q/4,1)}rem`},children:["#",B,n.jsx("span",{className:"tag-count",children:Q})]},B))})]}),n.jsx("div",{className:"docs-category-filters",children:n.jsx(Sp,{selectedCategory:g.category,onSelectCategory:j,sections:an})}),M&&n.jsxs("div",{className:"docs-results-header",children:[n.jsxs("div",{className:"results-info",children:[n.jsxs("span",{className:"results-count-large",children:[I," ",I===1?"article":"articles"]}),g.query&&n.jsxs("span",{className:"search-query-display",children:['for "',n.jsx("strong",{children:g.query}),'"']})]}),n.jsxs("button",{className:"clear-all-btn",onClick:()=>{C(),d("")},disabled:!M,children:[n.jsx(K,{name:"utility",size:14}),"Clear all filters"]})]}),n.jsx("div",{className:"docs-content",children:M?n.jsx("div",{className:"search-results-view",children:Object.entries(V).map(([B,Q])=>{var pe;return n.jsxs("section",{className:"results-category",children:[n.jsx("h2",{className:"category-title",children:((pe=an.find(ne=>ne.id===B))==null?void 0:pe.label)||B}),n.jsx("div",{className:"category-results-grid",children:Q.map(ne=>n.jsx(ho,{doc:ne,variant:"highlighted"},ne.page.slug))})]},B)})}):c?n.jsxs("div",{className:"category-view",children:[n.jsxs("div",{className:"category-header",children:[n.jsx("h2",{className:"category-page-title",children:((ee=an.find(B=>B.id===c))==null?void 0:ee.label)||c}),n.jsx("p",{className:"category-description",children:(se=an.find(B=>B.id===c))==null?void 0:se.description})]}),n.jsx("div",{className:"category-articles",children:De.filter(B=>B.category===c).sort((B,Q)=>B.order-Q.order).map(B=>n.jsx(ho,{doc:B},B.slug))})]}):n.jsx("div",{className:"all-categories-view",children:an.map(B=>n.jsxs("section",{className:"docs-section",id:`section-${B.id}`,children:[n.jsxs("div",{className:"section-header",children:[n.jsx("div",{className:"section-icon",children:n.jsx(K,{name:B.icon,size:28})}),n.jsxs("div",{className:"section-info",children:[n.jsx("h2",{className:"section-title",children:B.label}),n.jsx("p",{className:"section-description",children:B.description})]}),n.jsx("span",{className:"section-count",children:B.count})]}),n.jsx("div",{className:"section-articles",children:De.filter(Q=>Q.category===B.id).sort((Q,pe)=>Q.order-pe.order).map(Q=>n.jsx(ho,{doc:Q},Q.slug))})]},B.id))})}),n.jsxs("div",{className:"docs-footer-note",children:[n.jsx(K,{name:"book",size:20}),n.jsxs("div",{children:[n.jsx("strong",{children:"Want more detail?"}),n.jsxs("p",{children:["The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in the"," ",n.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"docs/"})," ","folder."]})]})]})]}),n.jsx(Nt,{})]})}function Pp(){const i=aa(),[l,c]=T.useState(null);T.useEffect(()=>{ea().then(c).catch(()=>{})},[]);const d=[["spark","AI that remembers","Thoughtful conversation with a cozy personality and controls that respect your community."],["chart","A living economy","Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],["shield","Confident moderation","Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],["users","Community rituals","Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."]];return n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"home"}),n.jsxs("main",{children:[n.jsxs("section",{className:"hero shell",children:[n.jsxs("div",{className:"hero-copy",children:[n.jsxs("div",{className:"eyebrow",children:[n.jsx("span",{className:"status-dot"})," Discord companion · online"]}),n.jsxs("div",{className:"hero-identity",children:[n.jsx("span",{className:"hero-avatar",children:i!=null&&i.bot_avatar_url?n.jsx("img",{src:i.bot_avatar_url,alt:"Niko"}):"n"}),n.jsxs("span",{children:[n.jsx("strong",{children:"Niko"}),n.jsx("small",{children:"Your server’s calm, capable co-pilot"})]})]}),n.jsxs("h1",{children:["Useful tools for a ",n.jsx("em",{children:"better server."})]}),n.jsx("p",{children:"Niko handles the everyday work of running a Discord community, so your moderators can focus on the people in it."}),n.jsxs("div",{className:"hero-buttons",children:[n.jsxs("a",{className:"button button-primary",href:(i==null?void 0:i.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Invite Niko ",n.jsx(K,{name:"arrow"})]}),n.jsx("a",{className:"button button-muted",href:"/commands",onClick:m=>{m.preventDefault(),le("/commands")},children:"Explore commands"})]}),n.jsxs("div",{className:"stats-strip",children:[n.jsxs("div",{children:[n.jsx("strong",{children:Pe(l==null?void 0:l.guild_count)}),n.jsx("span",{children:"servers"})]}),n.jsxs("div",{children:[n.jsx("strong",{children:Pe(l==null?void 0:l.user_count)}),n.jsx("span",{children:"members"})]}),n.jsxs("div",{children:[n.jsx("strong",{children:Pe(l==null?void 0:l.command_count)}),n.jsx("span",{children:"commands"})]})]})]}),n.jsx("div",{className:"hero-art","aria-label":"A preview of Niko's server workspace",children:n.jsxs("div",{className:"workspace-preview",children:[n.jsxs("div",{className:"workspace-preview-top",children:[n.jsxs("span",{className:"preview-dots",children:[n.jsx("i",{}),n.jsx("i",{}),n.jsx("i",{})]}),n.jsx("span",{children:"server workspace"}),n.jsxs("span",{className:"preview-status",children:[n.jsx("span",{className:"status-dot"})," live"]})]}),n.jsxs("div",{className:"preview-body",children:[n.jsxs("div",{className:"preview-sidebar",children:[n.jsx("span",{className:"preview-label",children:"NIKO"}),n.jsx("b",{children:"Overview"}),n.jsx("span",{children:"Economy"}),n.jsx("span",{children:"Leveling"}),n.jsx("span",{children:"Moderation"}),n.jsx("span",{children:"AI controls"})]}),n.jsxs("div",{className:"preview-main",children:[n.jsx("span",{className:"preview-label",children:"SERVER SNAPSHOT"}),n.jsx("strong",{children:"Everything in one place."}),n.jsxs("div",{className:"preview-stats",children:[n.jsxs("span",{children:[n.jsx("b",{children:Pe(l==null?void 0:l.user_count)}),n.jsx("small",{children:"members"})]}),n.jsxs("span",{children:[n.jsx("b",{children:Pe(l==null?void 0:l.command_count)}),n.jsx("small",{children:"commands"})]})]}),n.jsxs("div",{className:"preview-line",children:[n.jsx("i",{}),n.jsx("i",{}),n.jsx("i",{})]})]})]})]})})]}),n.jsxs("section",{className:"shell intro-section",children:[n.jsx("div",{className:"section-kicker",children:"Why Niko"}),n.jsxs("div",{className:"intro-grid",children:[n.jsxs("h2",{children:["The good kind of",n.jsx("br",{}),n.jsx("em",{children:"always-on."})]}),n.jsx("p",{children:"Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile."})]})]}),n.jsx("section",{className:"shell feature-grid",children:d.map(([m,p,g])=>n.jsxs("article",{className:"feature-card",children:[n.jsx("span",{className:"feature-icon",children:n.jsx(K,{name:m})}),n.jsx("h3",{children:p}),n.jsx("p",{children:g}),n.jsxs("a",{href:"/docs",onClick:E=>{E.preventDefault(),le("/docs")},children:["Learn more ",n.jsx(K,{name:"arrow"})]})]},p))}),n.jsxs("section",{className:"shell callout",children:[n.jsxs("div",{children:[n.jsx("div",{className:"section-kicker",children:"Ready when you are"}),n.jsxs("h2",{children:["A calmer, cleverer home",n.jsx("br",{}),"for your community."]})]}),n.jsxs("a",{className:"button button-primary",href:(i==null?void 0:i.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Bring Niko in ",n.jsx(K,{name:"arrow"})]})]})]}),n.jsx(Nt,{})]})}const Lp=[{code:"USDT",label:"Tether"},{code:"ETH",label:"Ethereum"},{code:"BTC",label:"Bitcoin"},{code:"BNB",label:"BNB"},{code:"LTC",label:"Litecoin"},{code:"DOGE",label:"Dogecoin"},{code:"TRX",label:"TRON"},{code:"XMR",label:"Monero"}];function Ap(){const l=new URLSearchParams(window.location.search).get("token")||"",[c,d]=T.useState("5"),[m,p]=T.useState("USDT"),[g,E]=T.useState(!1),[b,z]=T.useState(""),[C,N]=T.useState(null),[M,I]=T.useState(null),[R,_]=T.useState(!1);T.useEffect(()=>{l||_(!0)},[l]),T.useEffect(()=>{if(!(C!=null&&C.status_url)||C.paid)return;const J=setInterval(async()=>{try{const S=await ze(C.status_url);I(S),S.paid&&clearInterval(J)}catch{}},5e3);return()=>clearInterval(J)},[C]);const j=async J=>{J.preventDefault(),E(!0),z("");try{const S=await ze("/api/donations/invoice",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:l,amount:parseFloat(c),currency:m})});N(S),S.error&&(z(S.error),N(null))}catch(S){z(S instanceof Error?S.message:"Could not create invoice.")}finally{E(!1)}};return R?n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"home"}),n.jsx("main",{className:"auth-page",children:n.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[n.jsx("span",{className:"auth-mark",children:"!"}),n.jsx("div",{className:"eyebrow",children:"Invalid donation link"}),n.jsxs("h1",{children:["This link is ",n.jsx("em",{children:"invalid."})]}),n.jsxs("p",{children:["The donation link is missing or has expired. Use the"," ",n.jsx("code",{children:"/donate"})," command in Discord to generate a new one."]}),n.jsx("button",{className:"button button-primary full-width",onClick:()=>le("/"),children:"Return home"})]})})]}):M!=null&&M.paid?n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"home"}),n.jsx("main",{className:"auth-page",children:n.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[n.jsx("span",{className:"auth-mark",children:"✓"}),n.jsx("div",{className:"eyebrow",children:"Payment confirmed"}),n.jsxs("h1",{children:["Thank you ",n.jsx("em",{children:"for supporting!"})]}),n.jsx("p",{children:"Your donation has been confirmed. You will receive the Supporter badge shortly."}),n.jsx("button",{className:"button button-primary full-width",onClick:()=>le("/"),children:"Return home"})]})})]}):n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"home"}),n.jsx("main",{className:"page-main",children:n.jsx("div",{className:"shell",children:n.jsxs("div",{className:"page-heading",style:{maxWidth:500,margin:"0 auto"},children:[n.jsx("div",{className:"eyebrow",style:{marginBottom:15},children:"Support Niko"}),n.jsxs("h1",{children:["Keep Niko ",n.jsx("em",{children:"running."})]}),n.jsx("p",{style:{color:"var(--muted)",marginBottom:30},children:"Your donation helps cover hosting costs and keeps Niko running for all servers. Choose an amount and cryptocurrency below."}),C!=null&&C.pay_link?n.jsxs("div",{className:"dash-panel",style:{marginBottom:24},children:[n.jsx("div",{className:"panel-heading",children:n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"Invoice created"}),n.jsx("h3",{children:"Complete your payment"})]})}),n.jsxs("p",{style:{color:"var(--muted)",fontSize:12,marginBottom:16},children:["Amount: ",n.jsxs("strong",{children:["$",parseFloat(c).toFixed(2)," USD"]})," in"," ",n.jsx("strong",{children:m})]}),n.jsxs("p",{style:{color:"var(--dim)",fontSize:10,marginBottom:16},children:["Track ID: ",n.jsx("code",{children:C.track_id})," · Expires in 60 minutes"]}),n.jsxs("a",{className:"button button-primary",href:C.pay_link,target:"_blank",rel:"noopener noreferrer",children:["Pay now ",n.jsx(K,{name:"arrow"})]}),n.jsx("p",{style:{color:"var(--dim)",fontSize:10,marginTop:12},children:"Payment will be confirmed automatically once the transaction is processed on-chain."})]}):n.jsxs("form",{onSubmit:j,className:"dash-panel",style:{marginBottom:24},children:[n.jsxs("div",{className:"form-grid",children:[n.jsxs("label",{className:"form-field",children:[n.jsx("span",{className:"form-label",children:"Amount (USD)"}),n.jsx("input",{type:"number",min:"1",max:"10000",step:"0.01",value:c,onChange:J=>d(J.target.value)}),n.jsx("small",{children:"Minimum $1.00, maximum $10,000.00"})]}),n.jsxs("label",{className:"form-field",children:[n.jsx("span",{className:"form-label",children:"Cryptocurrency"}),n.jsx("select",{value:m,onChange:J=>p(J.target.value),children:Lp.map(J=>n.jsxs("option",{value:J.code,children:[J.label," (",J.code,")"]},J.code))})]})]}),b&&n.jsx("p",{className:"form-error",style:{marginTop:12},role:"alert",children:b}),n.jsx("div",{style:{marginTop:16},children:n.jsx("button",{className:"button button-primary",type:"submit",disabled:g,children:g?"Creating invoice…":"Create invoice"})})]}),n.jsxs("div",{className:"docs-footer-note",style:{marginTop:20},children:[n.jsx("strong",{children:"How it works"}),n.jsx("p",{children:'1. Choose an amount and currency above · 2. Click "Pay now" to open the payment page · 3. Send crypto to the displayed address · 4. Payment is confirmed automatically once processed on-chain'})]})]})})})]})}const Dp={privacy:{title:"Privacy policy",intro:"Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",sections:[["Information we use","User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature."],["How it is used","Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],["Storage and retention","Data is stored by the server hosting Niko in local JSON and SQLite files. Economy, leveling, and configuration data remain until removed. AI conversation history is limited and can be cleared with /clearhistory."],["Third-party services","When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Music and external lookup features may contact their respective services."],["Your choices","Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."]]},terms:{title:"Terms of service",intro:"By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",sections:[["Permitted use","Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],["Availability","Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],["Moderation","The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],["AI content","AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],["Virtual items","In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],["Contact","Questions or concerns can be sent through the Niko support server."]]},community:{title:"Community policy",intro:"These community expectations apply to every server that uses Niko. By adding the bot to a server, the server's owners and administrators agree to uphold these standards.",sections:[["Purpose","Niko is a community companion for Discord servers of all kinds. To keep the platform safe for everyone, all servers using Niko must follow the expectations below in addition to Discord's Terms of Service and Community Guidelines."],["Discrimination and harassment","Servers must not permit or promote discrimination, harassment, or hate speech targeting people based on race, ethnicity, national origin, religion, disability, gender, gender identity or expression, sexual orientation, age, veteran status, or any other protected identity characteristic."],["Illegal and malicious content","Servers must not create, host, share, or distribute illegal or malicious content. This includes, but is not limited to: child sexual abuse material (CSAM), malware and other malicious software, gore or shock content, pirated media and/or software, content that facilitates violence or terrorism, scams and phishing, and any other content that is illegal under applicable law."],["Other prohibited conduct","Servers must not use Niko to facilitate doxxing, targeted harassment campaigns, sextortion, trafficking, or the sexualization of minors in any form."],["Enforcement and investigations","When a server is reported or flagged for potentially violating this policy, Niko will send a warning notice to the server. The notice is followed by an investigation by Niko staff. Servers that cooperate in good faith and are found not to be breaking the policies will not receive any further action."],["Obstruction of investigations","Banning, kicking, or otherwise removing the staff member(s) sent to investigate, or hiding, deleting, or tampering with potential evidence, is treated as an admission of guilt. Doing so will result in the server — and any users who are involved — being permanently blacklisted from further use of Niko, in addition to any other action the investigation warrants."],["Reporting","If you believe a server using Niko is violating this policy, report it through the Niko support server. Reports are reviewed by staff and handled confidentially."]]}};function po({type:i}){const l=Dp[i];return n.jsxs(n.Fragment,{children:[n.jsx(We,{page:i}),n.jsxs("main",{className:"shell page-main legal-page",children:[n.jsxs("div",{className:"page-heading",children:[n.jsx("div",{className:"eyebrow",children:"Niko legal"}),n.jsx("h1",{children:l.title}),n.jsx("p",{children:l.intro}),n.jsx("small",{children:"Effective date: 1 January 2025"})]}),n.jsx("div",{className:"legal-copy",children:l.sections.map(([c,d])=>n.jsxs("section",{children:[n.jsx("h2",{children:c}),n.jsx("p",{children:d})]},c))})]}),n.jsx(Nt,{})]})}const Rp=[{key:"txt",label:"TXT",icon:"📄"},{key:"html",label:"HTML",icon:"🌐"},{key:"csv",label:"CSV",icon:"📊"},{key:"json",label:"JSON",icon:"{ }"}],Zu=i=>typeof i!="number"||i<0||i>16777215?"":`#${i.toString(16).padStart(6,"0")}`,jn=i=>(i==null?void 0:i.url)||(i==null?void 0:i.proxy_url)||"",ed=i=>/\.(?:png|jpe?g|gif|webp|bmp|svg)(?:[?#]|$)/i.test(i)||i.startsWith("data:image/"),td=i=>/\.(?:mp4|webm|mov|m4v|ogg)(?:[?#]|$)/i.test(i)||i.startsWith("data:video/"),Ip=i=>i.url?i.url:i.id?`https://cdn.discordapp.com/stickers/${i.id}.${i.format_type===4?"gif":"png"}`:"";function zp(i){var c;const l=jn(i);return l?(c=i==null?void 0:i.content_type)!=null&&c.startsWith("video/")?!0:td(l):!1}const Uu=new RegExp("(`[^`\\n]+`)|(\\[([^\\]\\n]+)\\]\\((https?:\\/\\/[^\\s)\\] ]+)\\))|(\\*\\*)|(?<!\\*)\\*(?!\\*)|(~~)","g"),Fp=/(https?:\/\/[^\s<>)]+)/g,Wu={bold:"**",italic:"*",strike:"~~"},Bp=new Set(["t","T","d","D","f","F","R"]);function Op(i,l){if(!Number.isFinite(i)||!Bp.has(l))return null;const c=new Date(i*1e3);if(Number.isNaN(c.getTime()))return null;if(l==="R"){const m=i-Math.floor(Date.now()/1e3),p=Math.abs(m),g=p<60?"second":p<3600?"minute":p<86400?"hour":p<604800?"day":p<2592e3?"week":p<31536e3?"month":"year",E=g==="second"?1:g==="minute"?60:g==="hour"?3600:g==="day"?86400:g==="week"?604800:g==="month"?2592e3:31536e3;return new Intl.RelativeTimeFormat(void 0,{numeric:"always"}).format(Math.round(m/E),g)}const d={...l==="t"||l==="T"?{hour:"numeric",minute:"2-digit"}:{},...l==="T"?{second:"2-digit"}:{},...l==="d"?{year:"numeric",month:"2-digit",day:"2-digit"}:{},...l==="D"?{year:"numeric",month:"long",day:"numeric"}:{},...l==="f"?{year:"numeric",month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}:{},...l==="F"?{weekday:"long",year:"numeric",month:"long",day:"numeric",hour:"numeric",minute:"2-digit"}:{}};return new Intl.DateTimeFormat(void 0,d).format(c)}function Up(i){const l=[];let c=0,d;const m=p=>{if(!p)return;const g=p.split(/(<a?:[A-Za-z0-9_~]+:\d+>|<t:-?\d+:[tTdDfFR]>)/g);for(const E of g){if(!E)continue;const b=E.match(/^<(a?):([A-Za-z0-9_~]+):(\d+)>$/);if(b){l.push({type:"emoji",name:b[2],id:b[3],animated:b[1]==="a"});continue}const z=E.match(/^<t:(-?\d+):([tTdDfFR])>$/);if(z){l.push({type:"timestamp",unix:Number(z[1]),style:z[2],raw:E});continue}const C=E.split(Fp);for(let N=0;N<C.length;N++)C[N]&&(N%2===1?l.push({type:"link",text:C[N],url:C[N]}):l.push({type:"text",text:C[N]}))}};for(Uu.lastIndex=0;(d=Uu.exec(i))!==null;)d.index>c&&m(i.slice(c,d.index)),d[1]!==void 0?l.push({type:"code",text:d[1].slice(1,-1)}):d[2]!==void 0?l.push({type:"link",text:d[3],url:d[4]}):d[5]!==void 0?l.push({type:"marker",fmt:"bold"}):d[6]!==void 0?l.push({type:"marker",fmt:"italic"}):d[7]!==void 0&&l.push({type:"marker",fmt:"strike"}),c=d.index+d[0].length;return c<i.length&&m(i.slice(c)),l}function Wp(i){const l=[],c=[],d=new Set,m=p=>{c.length>0?c[c.length-1].children.push(p):l.push(p)};for(const p of Up(i))if(p.type==="text")m({kind:"text",text:p.text});else if(p.type==="code")m({kind:"code",text:p.text});else if(p.type==="link")m({kind:"link",text:p.text,url:p.url});else if(p.type==="emoji")m({kind:"emoji",name:p.name,id:p.id,animated:p.animated});else if(p.type==="timestamp")m({kind:"timestamp",unix:p.unix,style:p.style,raw:p.raw});else if(p.type==="marker")if(d.has(p.fmt)){const g=c.map(z=>z.fmt).lastIndexOf(p.fmt),E=c.splice(g);E.forEach(z=>d.delete(z.fmt));const b={kind:"fmt",fmt:p.fmt,children:[...E[0].children]};for(const z of E.slice(1))b.children.push({kind:"text",text:Wu[z.fmt]??""}),b.children.push(...z.children);m(b)}else c.push({fmt:p.fmt,children:[]}),d.add(p.fmt);if(c.length>0)for(const p of c){m({kind:"text",text:Wu[p.fmt]??""});for(const g of p.children)m(g)}return l}const nd=(i,l)=>i.map((c,d)=>{const m=`${l}-${d}`;switch(c.kind){case"text":return n.jsx("span",{children:c.text},m);case"code":return n.jsx("code",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:4,padding:"0 5px",color:"#f2b8c2",fontFamily:"monospace",fontSize:"0.92em"},children:c.text},m);case"emoji":return n.jsx("img",{src:`https://cdn.discordapp.com/emojis/${c.id}.${c.animated?"gif":"png"}`,alt:`:${c.name}:`,title:`:${c.name}:`,style:{width:22,height:22,objectFit:"contain",verticalAlign:"-0.35em",display:"inline-block"},onError:p=>{p.currentTarget.alt=`:${c.name}:`}},m);case"timestamp":{const p=Op(c.unix,c.style);return p?n.jsx("time",{dateTime:new Date(c.unix*1e3).toISOString(),title:c.raw,children:p},m):n.jsx("span",{children:c.raw},m)}case"link":return n.jsx("a",{href:c.url,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",textDecoration:"none"},onMouseEnter:p=>{p.currentTarget.style.textDecoration="underline"},onMouseLeave:p=>{p.currentTarget.style.textDecoration="none"},children:c.text},m);case"fmt":{const p={};return c.fmt==="bold"&&(p.fontWeight=700),c.fmt==="italic"&&(p.fontStyle="italic"),c.fmt==="strike"&&(p.textDecoration="line-through"),n.jsx("span",{style:p,children:nd(c.children,m)},m)}}}),Js=i=>nd(Wp(i),"md");function wn({text:i,muted:l}){const c=i.split(`
`),d=[];return c.forEach((m,p)=>{const g=m.trimStart(),b=p===c.length-1?null:n.jsx("br",{},`br${p}`);g.startsWith("-# ")?d.push(n.jsxs("span",{style:{color:l?"#6d737a":"#949ba4",fontSize:12},children:[Js(g.slice(3)),b]},p)):/^#{1,4}\s/.test(g)?d.push(n.jsxs("span",{style:{color:"#f2f3f5",fontWeight:700,fontSize:16},children:[Js(g),b]},p)):g.startsWith("> ")?d.push(n.jsxs("span",{style:{display:"inline-block",color:"#b5bac1",borderLeft:"3px solid #4e5058",paddingLeft:8},children:[Js(g.slice(2)),b]},p)):g.startsWith("```")?d.push(n.jsxs("pre",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:6,padding:"10px 12px",overflowX:"auto",whiteSpace:"pre-wrap",wordBreak:"break-word",fontFamily:"monospace",fontSize:12.5,color:"#dbdee1",margin:"2px 0"},children:[g.replace(/^```[a-zA-Z]*/,"").replace(/```$/,""),b]},p)):d.push(n.jsxs("span",{children:[Js(m),b]},p))}),n.jsx("span",{style:{whiteSpace:"pre-wrap",wordBreak:"break-word"},children:d})}function $p({embed:i}){const l=Zu(i.color)||"#5865f2",c=i.author,d=i.footer,m=jn(i.thumbnail),p=jn(i.image);return n.jsxs("div",{style:{display:"flex",gap:12,maxWidth:560,marginTop:8,background:"#2b2d31",border:"1px solid #3f4147",borderLeft:`4px solid ${l}`,borderRadius:6,padding:"10px 12px"},children:[n.jsxs("div",{style:{flex:1,minWidth:0},children:[(c==null?void 0:c.name)&&n.jsxs("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:4},children:[c.icon_url&&n.jsx("img",{src:c.icon_url||c.proxy_icon_url,alt:"",style:{width:18,height:18,borderRadius:"50%",verticalAlign:"-4px",marginRight:6}}),c.name]}),i.title&&n.jsx("div",{style:{color:"#00a8fc",fontWeight:600,margin:"2px 0 4px",fontSize:14},children:i.url?n.jsx("a",{href:i.url,target:"_blank",rel:"noopener noreferrer",style:{color:"inherit",textDecoration:"none"},children:n.jsx(wn,{text:i.title})}):n.jsx(wn,{text:i.title})}),i.description&&n.jsx("div",{style:{color:"#dbdee1",fontSize:13,lineHeight:1.5},children:n.jsx(wn,{text:i.description})}),i.fields&&i.fields.length>0&&n.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:"6px 12px",marginTop:8},children:i.fields.map((g,E)=>n.jsxs("div",{style:{flex:g.inline?"0 1 45%":"1 1 100%",minWidth:0,marginBottom:4},children:[g.name&&n.jsx("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:2},children:n.jsx(wn,{text:g.name})}),g.value&&n.jsx("div",{style:{color:"#dbdee1",fontSize:13},children:n.jsx(wn,{text:g.value})})]},E))}),p&&n.jsx("a",{href:p,target:"_blank",rel:"noopener noreferrer",style:{display:"block",marginTop:8},children:n.jsx("img",{src:p,alt:"",style:{maxWidth:"100%",maxHeight:300,borderRadius:4,display:"block"},onError:g=>{g.currentTarget.style.display="none"}})}),((d==null?void 0:d.text)||i.timestamp)&&n.jsxs("div",{style:{display:"flex",alignItems:"center",gap:6,marginTop:6,color:"#949ba4",fontSize:11},children:[(d==null?void 0:d.icon_url)&&n.jsx("img",{src:d.icon_url||d.proxy_icon_url,alt:"",style:{width:16,height:16,borderRadius:"50%"}}),(d==null?void 0:d.text)&&n.jsx("span",{children:d.text}),i.timestamp&&n.jsx("span",{children:String(i.timestamp).replace("T"," ").replace("+00:00"," UTC")})]})]}),m&&n.jsx("a",{href:m,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:n.jsx("img",{src:m,alt:"",style:{width:80,height:80,borderRadius:6,objectFit:"cover"},onError:g=>{g.currentTarget.style.display="none"}})})]})}function Zs({component:i}){switch(i.type){case 17:{const l=Zu(i.accent_color);return n.jsxs("div",{style:{display:"flex",overflow:"hidden",maxWidth:560,marginTop:8,background:"#2b2d31",border:`1px solid ${l||"#3f4147"}`,borderRadius:12},children:[l&&n.jsx("div",{style:{flex:"0 0 4px",background:l}}),n.jsx("div",{style:{flex:1,minWidth:0,padding:"6px 12px 8px"},children:(i.components||[]).map((c,d)=>n.jsx(Zs,{component:c},d))})]})}case 1:return n.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,margin:"6px 0"},children:(i.components||[]).map((l,c)=>n.jsx(Zs,{component:l},c))});case 2:{const l=i.emoji,c=`${(l==null?void 0:l.name)??""}${i.label?` ${i.label}`:""}`.trim();return i.style===5&&!!i.url?n.jsx("a",{href:i.url,target:"_blank",rel:"noopener noreferrer",style:{display:"inline-block",padding:"3px 14px",background:"#5865f2",borderRadius:4,color:"#fff",fontSize:13,fontWeight:600,textDecoration:"none"},children:c||"Button"}):n.jsx("span",{style:{display:"inline-block",padding:"3px 14px",background:"#4e5058",borderRadius:4,color:i.disabled?"#8a8e96":"#f2f3f5",fontSize:13,cursor:i.disabled?"not-allowed":"default",opacity:i.disabled?.55:1},children:c||"Button"})}case 9:{const l=[...i.components||[]];return i.accessory&&l.push(i.accessory),n.jsx("div",{style:{display:"flex",alignItems:"center",gap:10,margin:"4px 0"},children:l.map((c,d)=>n.jsx(Zs,{component:c},d))})}case 10:return n.jsx("div",{style:{color:"#dbdee1",fontSize:14,lineHeight:1.5,margin:"4px 0",wordBreak:"break-word"},children:n.jsx(wn,{text:i.content||""})});case 18:return n.jsx("div",{style:{color:"#f2f3f5",fontWeight:700,textTransform:"uppercase",letterSpacing:"0.04em",fontSize:12,margin:"4px 0"},children:i.content});case 14:return n.jsx("div",{style:{margin:i.divider===!1?"6px 0":"9px 0",...i.divider===!1?{}:{borderTop:"1px solid #3f4147"}}});case 11:{const l=jn(i.media);return l?n.jsx("a",{href:l,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:n.jsx("img",{src:l,alt:i.description||"",style:{width:40,height:40,borderRadius:"50%",objectFit:"cover",display:"block"},onError:c=>{c.currentTarget.style.display="none"}})}):null}case 12:{const c=(i.items||[]).filter(d=>jn(d.media));return c.length===0?null:n.jsx("div",{style:{display:"grid",gridTemplateColumns:`repeat(auto-fill, minmax(${Math.min(220,Math.max(140,Math.floor(560/Math.max(1,c.length))))}px, 1fr))`,gap:6,margin:"6px 0"},children:c.map((d,m)=>{const p=jn(d.media),g=d.description;return zp(d.media)?n.jsxs("figure",{style:{margin:0},children:[n.jsx("video",{src:p,controls:!0,preload:"metadata",style:{width:"100%",maxHeight:260,borderRadius:6,background:"#1e1f22"}}),g&&n.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:g})]},m):ed(p)?n.jsxs("figure",{style:{margin:0},children:[n.jsx("a",{href:p,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:n.jsx("img",{src:p,alt:g||"",style:{width:"100%",maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:E=>{E.currentTarget.style.display="none"}})}),g&&n.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:g})]},m):n.jsxs("a",{href:p,target:"_blank",rel:"noopener noreferrer",style:{display:"flex",alignItems:"center",gap:6,padding:"6px 10px",background:"#383a40",borderRadius:6,color:"#dbdee1",fontSize:12,textDecoration:"none"},children:["📎 ",g||"Attachment"]},m)})})}case 13:{const l=jn(i.media)||i.url||"";return l?n.jsxs("a",{href:l,target:"_blank",rel:"noopener noreferrer",style:{display:"block",margin:"4px 0",color:"#00a8fc",fontSize:12.5,textDecoration:"none"},children:["📎 ",i.label||"Attachment"]}):null}default:return null}}function Vp({components:i}){return n.jsx(n.Fragment,{children:i.map((l,c)=>n.jsx(Zs,{component:l},c))})}function Hp({text:i}){return n.jsx(wn,{text:i})}function Gp({msg:i}){const l=!!(i.attachments&&i.attachments.length>0||i.embeds&&i.embeds.length>0||i.components&&i.components.length>0||i.stickers&&i.stickers.length>0);return n.jsxs("div",{style:{padding:"10px 16px",borderBottom:"1px solid #2b2d31",fontSize:14,lineHeight:1.6},children:[n.jsxs("div",{style:{marginBottom:2},children:[n.jsx("span",{style:{color:"#949ba4",fontSize:11,fontFamily:"monospace"},children:i.timestamp})," ",n.jsx("span",{style:{color:"#f2f3f5",fontWeight:600},children:i.author})," ",n.jsxs("span",{style:{color:"#949ba4",fontSize:11},children:["(",i.author_id,")"]})]}),i.content?n.jsx("div",{style:{color:"#dbdee1"},children:n.jsx(Hp,{text:i.content})}):l?null:n.jsx("div",{style:{color:"#6d737a",fontStyle:"italic",fontSize:13},children:"Message content unavailable"}),i.attachments&&i.attachments.length>0&&n.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:4},children:i.attachments.map((c,d)=>td(c)?n.jsx("video",{src:c,controls:!0,preload:"metadata",style:{maxWidth:360,maxHeight:260,borderRadius:6,background:"#1e1f22"}},d):ed(c)?n.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:n.jsx("img",{src:c,alt:"",style:{maxWidth:300,maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:m=>{const p=m.currentTarget;p.style.display="none"}})},d):n.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",fontSize:12,textDecoration:"none"},children:"📎 Attachment"},d))}),i.embeds&&i.embeds.length>0&&n.jsx(n.Fragment,{children:i.embeds.map((c,d)=>n.jsx($p,{embed:c},d))}),i.stickers&&i.stickers.length>0&&n.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:8},children:i.stickers.map((c,d)=>{const m=Ip(c);return m?n.jsx("a",{href:m,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:n.jsx("img",{src:m,alt:c.name||"Discord sticker",title:c.name||"Discord sticker",style:{width:160,maxWidth:"100%",maxHeight:160,objectFit:"contain",display:"block"}})},d):null})}),i.components&&i.components.length>0&&n.jsx(Vp,{components:i.components})]})}function Kp({transcriptId:i}){const[l,c]=T.useState(null),[d,m]=T.useState(!0),[p,g]=T.useState("");T.useEffect(()=>{m(!0),g(""),fetch(`/api/transcript/${i}`).then(b=>{if(!b.ok)throw new Error("Transcript not found");return b.json()}).then(b=>{c(b),m(!1)}).catch(b=>{g(b.message||"Failed to load transcript"),m(!1)})},[i]);const E=b=>{window.open(`/api/transcript/${i}/download?format=${b}`,"_blank")};return d?n.jsx("div",{className:"page-main",children:n.jsx("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:n.jsx("div",{style:{color:"var(--muted)",fontSize:14},children:"Loading transcript…"})})}):p||!l?n.jsx("div",{className:"page-main",children:n.jsxs("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:[n.jsx("h2",{style:{marginBottom:12},children:"Transcript not found"}),n.jsx("p",{style:{color:"var(--muted)"},children:p||"This transcript doesn't exist or has been deleted."})]})}):n.jsx("div",{className:"page-main",children:n.jsxs("div",{className:"shell",style:{maxWidth:800},children:[n.jsx("div",{style:{background:"var(--surface)",border:"1px solid var(--line)",borderRadius:8,padding:24,marginBottom:20},children:n.jsxs("div",{style:{display:"flex",alignItems:"flex-start",justifyContent:"space-between",gap:16,flexWrap:"wrap"},children:[n.jsxs("div",{children:[n.jsx("div",{className:"eyebrow",style:{marginBottom:8},children:"Ticket Transcript"}),n.jsxs("h1",{style:{fontSize:24,letterSpacing:"-0.04em",margin:0},children:["#",l.channel_name]}),n.jsxs("div",{style:{color:"var(--muted)",fontSize:13,marginTop:6},children:[l.category," · ",l.message_count," messages · ",l.created_at]})]}),n.jsx("div",{style:{display:"flex",gap:8,flexWrap:"wrap"},children:Rp.map(b=>n.jsxs("button",{className:"button button-small button-muted",onClick:()=>E(b.key),style:{minWidth:70},children:[n.jsx("span",{children:b.icon}),n.jsx("span",{children:b.label})]},b.key))})]})}),n.jsxs("div",{style:{background:"#1e1f22",border:"1px solid #3f4147",borderRadius:8,overflow:"hidden"},children:[l.messages.map((b,z)=>n.jsx(Gp,{msg:b},z)),l.messages.length===0&&n.jsx("div",{style:{padding:40,textAlign:"center",color:"#949ba4"},children:"No messages in this transcript."})]}),n.jsxs("div",{style:{marginTop:16,padding:"12px 0",textAlign:"center",color:"var(--dim)",fontSize:12},children:["Transcript ID: ",n.jsx("code",{style:{fontFamily:"monospace"},children:i})]})]})})}const na=[{slug:"team-page-ai-name-config",title:"Team Profiles & Custom AI Names",date:"2026-09-22",version:"2.10.0",tags:["team","staff","dashboard","ai","website"],summary:"Niko's public website now introduces the people behind the bot, while server owners can give their AI a custom name and manage its experimental capabilities from the dashboard.",highlights:[{title:"Meet the Niko Team",description:"The new Team page showcases owners, developers, moderators, support staff, and other persisted staff roles with Discord-synced identities, presence, activities, bios, and profile pages.",icon:"users"},{title:"Choose Your AI's Name",description:"Server administrators can configure the AI's display name from the dashboard or the AI configuration command. The chosen name is used for mention detection and reply identity in that server.",icon:"spark"},{title:"Staff Public Listings",description:"Staff members can customize their public bio, banner, and visibility while their name and avatar remain synchronized with Discord.",icon:"settings"}],changes:[{category:"added",items:["Public Team page with persisted staff roles and linked staff profiles","Discord-synced staff presence, current activities, Spotify, streaming, and custom status display","Staff self-service controls for public bio, banner, and Team page visibility","Configurable per-server AI name in the dashboard and AI configuration command","Dashboard controls for AI Actions, Better Context, and Multimodal Conversation experiments","Learn-more dialogs explaining each AI experiment"]},{category:"improved",items:["Dashboard staff workspace navigation and responsive layout","Team profile cards and profile-page activity presentation","AI configuration persistence through the shared database","Public page metadata and favicon handling during the website build"]},{category:"fixed",items:["Team presence labels showing online staff as away","Spotify and streaming activities being hidden behind custom statuses","Staff profile updates being rejected for authorized owners","Staff profile avatars being clipped by profile banners"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Team",value:"1",detail:"new public experience",color:"#66866f"},{label:"AI",value:"4",detail:"new configuration controls",color:"#d96545"},{label:"Profiles",value:"3",detail:"public staff controls",color:"#4a7fb5"}]},commits:[]},{slug:"september-platform-updates",title:"September Platform Updates",date:"2026-09-21",version:"2.9.0",tags:["dashboard","ai","tickets","music","website"],summary:"A broad set of public improvements landed across Niko: richer ticket transcripts, a multimodal AI experiment, more reliable music playback, a redesigned dashboard experience, persistent giveaways and suggestions, and a refreshed public website with dynamic social previews.",highlights:[{title:"More Natural AI Conversations",description:"The new opt-in Multimodal Conversation experiment can understand image attachments and transcribe voice messages before generating a reply, while safely falling back to text when media processing is unavailable.",icon:"spark"},{title:"Richer Ticket Transcripts",description:"Transcript pages and HTML downloads now render Discord custom emojis, stickers, and dynamic timestamps such as <t:1788800225:f> in a more faithful format.",icon:"doc"},{title:"Dashboard & Website Refresh",description:"Dashboard navigation and mobile layouts were refined, documentation was expanded, and public routes now receive route-specific Open Graph cards generated during the build.",icon:"settings"},{title:"Reliable Long-Running Features",description:"Giveaways and suggestions now restore their state from the main database at startup, while music nodes are rescanned periodically to keep playback available.",icon:"utility"}],changes:[{category:"added",items:["Opt-in Multimodal Conversation AI experiment for image understanding and voice-message transcription","Official update notification system with a configurable server notification channel","Discord custom emoji and sticker rendering in ticket transcript pages and HTML downloads","Dynamic Discord timestamp rendering in ticket transcripts","Persistent suggestion configuration and voting buttons restored from the main database","Automatic hourly Lavalink node rescans with a hardcoded fallback node catalog","Additional economy SVG card API endpoints","Community Policy page on the public website","Route-specific Open Graph metadata and generated social preview cards"]},{category:"improved",items:["Dashboard navigation consistency and mobile layout","Dashboard page layout and visual polish","Music connection reliability, autoplay, Spotify playback, and node recovery","Giveaway persistence and startup restoration for MongoDB-backed data","Onboarding setup handling and configuration persistence","Poll command design and interaction flow","Ticket transcript HTML download formatting","Economy image-card font rendering, SVG output, and emoji support","Documentation pages and public website frontend"]},{category:"fixed",items:["Giveaways losing their live buttons after a restart or extended runtime","Suggestion buttons and configuration not surviving process restarts","Ticket transcript rendering for custom media and dynamic timestamps","Lavalink connection failures and stale music nodes","Broken SVG card and SVG endpoint output","Status panel polling noise and retired image-model defaults"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Added",value:"9",detail:"new capabilities",color:"#66866f"},{label:"Improved",value:"9",detail:"upgraded systems",color:"#4a7fb5"},{label:"Fixed",value:"6",detail:"reliability issues",color:"#d96545"}]},commits:["ac102df Fixed the Open Graph image cards","33aaf12 Added dynamic Open Graph tags to the website","3153e28 Rebuilt the frontend","bab665e Added a new Lavalink node","ee44a5e Improved the music cog","bc61e34 Released the new Multimodal Conversation AI experiment","c46af7d Fixed the suggestion system persistence","25703ca Added a broadcast system for official updates and announcements","265bdb2 Added dynamic timestamp rendering inside ticket transcripts","d8005db Added custom emoji and sticker rendering to ticket transcripts","e561d84 Fixed the dashboards navbar","a0bab78 Improved the dashboards mobile layout","fb2f5aa Patched giveaway persistence for MongoDB compatibility","d77779e Fixed several dashboard flaws","b8e06a5 Improved the dashboard pages","3708207 Patched issues in the giveaway and onboarding cogs","d58bb37 Redesigned the poll command","bb523e3 Added a Community Policy page","5b34c7c Updated the documentation pages","3a52fc2 Added new economy card API endpoints","df3ea25 Fixed an issue in the SVG endpoints","39b7340 Fixed an error in the SVG cards","9e3483e Replaced HTML entities with valid XML numeric character references in economy cards"]},{slug:"economy-leveling-overhaul",title:"Economy Items, Leveling Cards & Subcommands",date:"2026-09-08",version:"2.8.0",tags:["economy","leveling","shop","image-cards"],summary:"The economy shop expanded with four new consumable items that affect gameplay — Rigged Coin, Streak Insurance, Double Down Token, and Lucky Horseshoe — plus daily streak milestone bonuses at 7, 14, 30, 60, and 90 days. The leveling system now renders rank cards and leaderboards as customizable image cards, and all leveling commands live under a single `/leveling` group with subcommands.",highlights:[{title:"New Shop Items",description:"Four new consumables: Rigged Coin (60/40 coinflip odds), Streak Insurance (protects daily streak for one missed day), Double Down Token (1.5x gambling payout), and Lucky Horseshoe (+10% work reward).",icon:"chart"},{title:"Leveling Image Cards",description:"Rank cards and the leaderboard now render as styled images with avatar, level, XP bar, and rank. Server admins can customize the card accent color and background gradient.",icon:"spark"},{title:"Leveling Subcommands",description:"All leveling commands reorganized under `/leveling` with `rank`, `leaderboard`, `panel`, and `config` subcommands. The leaderboard now has interactive pagination buttons.",icon:"settings"},{title:"Daily Streak Milestones",description:"Hitting 7, 14, 30, 60, or 90-day daily streaks now awards bonus items from the shop (Espresso Shots, Lockpicks, Lucky Charms, Rob Shields) along with a coin bonus.",icon:"utility"}],changes:[{category:"added",items:["Coinflip command with heads/tails call and double-or-nothing payout","Rigged Coin shop item — gives 60/40 coinflip odds for one use","Streak Insurance shop item — protects daily streak if you miss one day","Double Down Token shop item — next gambling win pays 1.5x","Lucky Horseshoe shop item — next work reward gets +10%","Daily streak milestone bonuses at 7/14/30/60/90 days with item rewards","Image card rendering for `/leveling rank` with customizable accent and background","Image card rendering for the leveling leaderboard","Inventory display as an image card in the shop command","Twemoji emoji rendering in economy card images","Pagination buttons (◀ ▶) on the leveling leaderboard","Card customization fields in the database: card_accent, card_bg_top, card_bg_bottom"]},{category:"improved",items:["Leveling commands restructured as `/leveling rank`, `leaderboard`, `panel`, `config` subcommands","Shop command visual layout with better font rendering on economy image cards","Crime and rob commands now check for gambling_boost effect for 1.5x payout","HTML download format for ticket transcripts","Dashboard UI refinements"]},{category:"fixed",items:["Command name conflicts between leveling and other cogs","Missing import in leveling cog after image card addition","Duplicate command alias in leveling system","Command name conflict in the gambling cog"]}],chart:{type:"bar",title:"New Shop Items & Their Effects",data:[{label:"Rigged Coin",value:3e3,color:"#c9a84c"},{label:"Streak Insurance",value:4e3,color:"#4a7fb5"},{label:"Double Down Token",value:5e3,color:"#d96545"},{label:"Lucky Horseshoe",value:2500,color:"#66866f"}]},commits:["41d86fb Expanded the gambling and economy system","bd6a09c Added image cards to the leveling system","5307bb1 Moved the leveling commands to the levels subcommand","dafd224 Added an image card to the inventory command","49fc83b Added emoji rendering to the shop command","0aca6ba Improved the shop command","30c9735 Added better font rendering to the economy system image cards","2b96835 Fixed a command name conflict","158ad8f Fixed a command name conflict in the gambling cog","d465598 Fixed a missing import","1f24ffb Fixed a duplicate command alias"]},{slug:"database-migration",title:"Database Migration to MongoDB",date:"2026-09-03",version:"2.7.0",tags:["database","mongodb","migration","infrastructure"],summary:"Every major system has been migrated from SQLite to MongoDB. The migration covered economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and the blacklist — with a custom interpreter that translates SQLite-style writes to MongoDB operations.",highlights:[{title:"Full MongoDB Migration",description:"Economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and blacklist now all store data in MongoDB instead of SQLite.",icon:"settings"},{title:"Slash Command Sync Safeguard",description:"A new check prevents redundant Discord API calls when all commands are already registered, reducing rate-limit issues on startup.",icon:"utility"},{title:"Proxy Integration",description:"A new proxy manager reduces downtime on shared hosting environments by routing API requests through a proxy layer.",icon:"shield"}],changes:[{category:"migrated",items:["Economy system — balances, banks, jobs, achievements, inventory","Leveling system — XP, levels, role rewards, card customization","Moderation system — warnings, mutes, automod config","Ticket system — panels, transcripts, support roles","Birthday system — dates, channels, messages","AFK system — status, timestamps","Sticky messages — content, channels","Blacklist — users, words, filters"]},{category:"added",items:["MongoDB interpreter that translates SQLite-style writes to proper MongoDB operations","Proxy manager for shared hosting reliability","Slash command sync safeguard to prevent redundant API calls","Context menu command support in the sync utility"]},{category:"fixed",items:["MongoDB interpreter not translating all SQLite write patterns correctly","Economy interest calculation after migration","Birthday system data persistence","Several database connection issues across various cogs","Leveling database initialization issue"]}],chart:{type:"donut",title:"Systems Migrated to MongoDB",centerLabel:"8 systems",data:[{label:"Economy",value:1,color:"#d96545"},{label:"Leveling",value:1,color:"#66866f"},{label:"Moderation",value:1,color:"#4a7fb5"},{label:"Tickets",value:1,color:"#c9a84c"},{label:"Birthdays",value:1,color:"#b07cc6"},{label:"AFK",value:1,color:"#e0976e"},{label:"Sticky Msgs",value:1,color:"#7ca898"},{label:"Blacklist",value:1,color:"#8c918e"}]},commits:["c07f9b1 Fixed the MongoDB interpreter to properly translate all SQLite database writes","0d3aca5 Migrated the blacklist to the main database","954ebac Migrated the birthday system to the main database","5013d54 Migrated the warns and mutes to use the main database","f29c217 Migrated the afk system to the main database","5732b48 Migrated the sticky messages to use the main database","b0524f1 Migrated the ticket system to the main database","70e6d7a Fixed the sync util to support context commands and slash groups","2c01817 Added a safeguard to prevent slash command syncs when all commands are already present","121afcf Added a proxy integration to reduce downtime on shared hosting","9f2f1fd Fixed several database issues across various cogs"]},{slug:"ticket-system-transcripts",title:"Ticket Transcripts & VoiceMaster",date:"2026-09-03",version:"2.6.0",tags:["tickets","transcripts","voicemaster"],summary:"The ticket system gained a web-based transcript viewer that renders ticket conversations as styled HTML pages. The VoiceMaster was also improved with better reliability and database usage. Ticket transcripts can now be downloaded as HTML or viewed online.",highlights:[{title:"Web Transcript Viewer",description:"Ticket transcripts are now rendered as styled HTML pages that can be viewed online. The HTML download format was also improved for better readability.",icon:"doc"},{title:"VoiceMaster Reliability",description:"The VoiceMaster (temporary voice channels) was improved with better database usage and reliability fixes.",icon:"utility"},{title:"Donation Dashboard Page",description:"A new customization page in the dashboard lets server admins configure donation settings without using commands.",icon:"settings"}],changes:[{category:"added",items:["Web-based ticket transcript viewer with styled HTML output","Ticket transcript database table for storing transcripts online","Dashboard customization page for donation system settings"]},{category:"improved",items:["HTML download format for ticket transcripts","VoiceMaster reliability and database usage patterns","Ticket system persistence and data handling"]},{category:"fixed",items:["Ticket transcript pages rendering incorrectly","Ticket system data loss on restart","Ticket transcript generation issues","Ticket transcript page display bugs"]}],commits:["e953321 Added a new web transcript feature to the ticket system","aa0b73b Improved the donation system and added a customization page to the dashboard","3255385 Improved the html download format for the ticket transcripts","45f1fb0 Fixed the ticket system persistence","ef4e057 Added the ticket system database migrations","d4e0bc8 Fixed the ticket transcripts","4bf5e04 Fixed an issue with the ticket transcript pages","e8dbcb0 Improved the VoiceMaster reliability and improved the database usage"]},{slug:"roleplay-music-status",title:"Roleplay, Music & Status Rotation",date:"2026-09-05",version:"2.5.0",tags:["roleplay","music","status","social"],summary:"The roleplay cog was completely rewritten to use nekos.best API GIFs with CV2 layout messages and a persistent 'hug back' button. The music cog was restructured with a ghost queue feature and fixed autoplay/Spotify playback. A status message rotation system was added with a configurable timer.",highlights:[{title:"Roleplay Rewrite",description:"The roleplay cog now fetches SFW reaction GIFs from nekos.best, renders them in styled CV2 containers, and includes a 'hug back' button that persists across restarts. A single user context menu replaces individual action menus to stay under Discord's 15-command cap.",icon:"users"},{title:"Music Ghost Queue",description:"A new ghost queue feature lets songs be queued even when nothing is currently playing. Autoplay and Spotify playback were also fixed.",icon:"utility"},{title:"Status Rotation",description:"The bot now rotates through configurable status messages on a timer (default 30s interval), with activity types and a VR device presence.",icon:"spark"}],changes:[{category:"added",items:["Status message rotation with configurable interval and activity types","Persistent status panel command for the support server (owner only)","Roleplay block feature to prevent specific users from being targeted","Ghost queue feature — queue songs even when nothing is playing","User context menu for roleplay actions (replaces per-action menus)","YouTube channel name validation for notification system"]},{category:"improved",items:["Roleplay cog complete rewrite — nekos.best GIFs, CV2 layouts, persistent buttons","Social media notification emoji formatting (Bluesky, Reddit, TikTok, Twitch icons)","Music node connection system and autoplay reliability","Spotify playback quality","Music cog restructured with better error handling"]},{category:"fixed",items:["Status rotator startup errors and activity conflicts","on_ready event error handling and reliability","Lavalink connection bug","Roleplay prefix command handling","Bluesky and Reddit notification delivery issues"]}],commits:["0c58178 Redesigned the roleplay cog","6c4ee09 Fixed the roleplay prefix commands","f1f8591 Added a roleplay block feature","e01e3e4 Added status message rotation","5e63e1d Added a persistent status panel","ae7501a Restructured the music cog","526813e Added a new ghost queue feature to the music cog","6524da1 Improved the music node connection system, fixed the autoplay, and fixed the Spotify playback","4264677 Fixed a lavalink connection bug","d62ead8 Improved the social media notification system's emojis","0f0305d Improved the social media notification formatting","42069d4 Added proper channel name validation to the YouTube notification system"]},{slug:"moderation-logging-dashboard",title:"Logging, Moderation & Documentation",date:"2026-09-07",version:"2.4.0",tags:["logging","moderation","documentation","dashboard"],summary:"Logging got two major improvements: deleted message logs now show image attachments in a MediaGallery component, and the Member category now tracks avatar changes using a Section with Thumbnail accessory. The documentation page was fully rebuilt with search, filters, and a card-based layout.",highlights:[{title:"Image Attachments in Logs",description:"Deleted message logs now render attached images in a MediaGallery component inside the log container, so moderators can see what was posted without leaving Discord.",icon:"chart"},{title:"Avatar Change Tracking",description:"The Member logging category now detects avatar changes (global and server avatars) and displays them in a Section with a Thumbnail accessory showing the new avatar.",icon:"users"},{title:"Documentation Redesign",description:"The documentation page was rebuilt from scratch with a search bar, category filters, tag cloud, card-based layout, and individual article pages with table of contents.",icon:"doc"}],changes:[{category:"added",items:["Image attachments rendered in deleted message logs via MediaGallery","Avatar change detection in Member logging with Section + Thumbnail display","Startup economy cache that loads all users into memory for accurate leaderboards","Error handler for role menu post buttons","Full-text search with result highlighting in documentation","Category filters and tag cloud in documentation","Individual documentation article pages with table of contents"]},{category:"improved",items:["Logging system now supports media_urls, thumbnail_url, and files parameters","Commands page expanded with better organization","Dashboard UI refinements","Economy interest feature — skips malformed records with non-integer user IDs"]},{category:"fixed",items:["Logging command issues","Documentation command references","Status device detection issue","Status rotator conflicts between multiple status types","on_ready event reliability with proper error handling"]}],commits:["722a34f Added avatar updates to the logging cogs Member logs","1d82ea1 Moved file attachments inside the main log message for the deleted message logs","358d537 Added a startup economy cache to fix the leaderboard","566e0c4 Improved the dashboard","132bcbb Fully redesigned the documentation page","4f7a89a Improved the commands page","6d953b6 Fixed the logging command","a202687 Fixed some documentation issues","49d22ad Fixed the documentation command references","52de287 Added an error handler to the post role menu button"]},{slug:"website-launch-donation",title:"Website, Donation System & API",date:"2026-09-02",version:"2.3.0",tags:["website","donations","api"],summary:"The public website and documentation portal launched with a React + Vite frontend, documentation center with search, and a commands reference page. The donation system gained a dashboard customization page, and the Flask API backend was fixed to use proper database calls.",highlights:[{title:"Public Website",description:"A complete public website built with React and Vite featuring a landing page, documentation center, command reference, dashboard, and legal pages.",icon:"spark"},{title:"Documentation Center",description:"The documentation page was redesigned with a card-based layout, individual article pages, and a modern visual design matching the bot's aesthetic.",icon:"doc"},{title:"Donation Dashboard",description:"Server admins can now configure donation settings through a new dashboard page instead of relying solely on commands.",icon:"settings"}],changes:[{category:"added",items:["Public website with landing page, documentation center, and command reference","Donation system customization page in the dashboard","Ticket transcript viewer web page","Donate page with Oxapay integration"]},{category:"improved",items:["Flask API to use proper database calls instead of direct SQLite access","Website commands page with expanded details","Database layer reliability for production"]},{category:"fixed",items:["Flask API database call issues","Several database-related bugs across cogs","node_modules folder accidentally committed to repository"]}],commits:["132bcbb Fully redesigned the documentation page","aa0b73b Improved the donation system and added a customization page to the dashboard","bd5e3be Expanded the website's commands page","e266644 Fixed the flask API to use the proper database calls","e99ed47 Fixed several database related issues","c783514 Minor API fixes and improvements","0df4478 Added the node_modules folder to the gitignore file"]}];function qp(i){return na.find(l=>l.slug===i)}function Qp(){const i=new Set;return na.forEach(l=>l.tags.forEach(c=>i.add(c))),Array.from(i).sort()}function Xp(){const[i,l]=T.useState(""),c=Qp(),d=i?na.filter(m=>m.tags.includes(i)):na;return n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"home"}),n.jsxs("main",{className:"shell page-main changelog-page",children:[n.jsxs("div",{className:"changelog-hero",children:[n.jsxs("div",{className:"eyebrow",children:[n.jsx("span",{className:"status-dot"})," What's new"]}),n.jsxs("h1",{className:"changelog-title",children:["Changelog",n.jsx("br",{}),n.jsx("span",{className:"title-accent",children:"& updates"})]}),n.jsx("p",{className:"changelog-subtitle",children:"A record of every improvement, fix, and new feature added to Niko. Grouped by release for clarity."})]}),n.jsxs("div",{className:"changelog-tags",children:[n.jsx("button",{className:`changelog-tag-btn ${i===""?"active":""}`,onClick:()=>l(""),children:"All"}),c.slice(0,12).map(m=>n.jsx("button",{className:`changelog-tag-btn ${i===m?"active":""}`,onClick:()=>l(m),children:m},m))]}),n.jsx("div",{className:"changelog-timeline",children:d.map((m,p)=>n.jsxs("article",{className:"changelog-entry",children:[n.jsxs("div",{className:"changelog-entry-date-col",children:[n.jsx("div",{className:"changelog-date-dot"}),p<d.length-1&&n.jsx("div",{className:"changelog-date-line"})]}),n.jsxs("div",{className:"changelog-entry-card",children:[n.jsxs("div",{className:"changelog-entry-header",children:[n.jsxs("div",{className:"changelog-entry-meta",children:[n.jsx("time",{className:"changelog-entry-date",children:new Date(m.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),m.version&&n.jsxs("span",{className:"changelog-version",children:["v",m.version]})]}),n.jsx("h2",{className:"changelog-entry-title",children:m.title}),n.jsx("p",{className:"changelog-entry-summary",children:m.summary})]}),n.jsx("div",{className:"changelog-entry-highlights",children:m.highlights.slice(0,2).map(g=>n.jsxs("div",{className:"changelog-highlight-mini",children:[n.jsx("span",{className:"highlight-mini-icon",children:n.jsx(K,{name:g.icon,size:16})}),n.jsxs("div",{children:[n.jsx("strong",{children:g.title}),n.jsxs("p",{children:[g.description.slice(0,120),"..."]})]})]},g.title))}),n.jsx("div",{className:"changelog-entry-tags",children:m.tags.map(g=>n.jsx("span",{className:"changelog-tag",children:g},g))}),n.jsxs("button",{className:"changelog-read-more",onClick:()=>{le(`/changelog/${m.slug}`)},children:["Read full release notes ",n.jsx(K,{name:"arrow",size:14})]})]})]},m.slug))}),d.length===0&&n.jsxs("div",{className:"changelog-empty",children:[n.jsx(K,{name:"doc",size:40}),n.jsx("p",{children:"No changelog entries match this filter."})]})]}),n.jsx(Nt,{})]})}function Yp({slug:i}){const l=qp(i);return l?n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"home"}),n.jsxs("main",{className:"shell page-main changelog-page changelog-detail",children:[n.jsx("div",{className:"changelog-back",children:n.jsxs("button",{onClick:()=>le("/changelog"),className:"back-button",children:[n.jsx(K,{name:"arrow",size:16}),"Back to Changelog"]})}),n.jsxs("header",{className:"changelog-detail-header",children:[n.jsxs("div",{className:"changelog-detail-meta",children:[n.jsx("time",{children:new Date(l.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),l.version&&n.jsxs("span",{className:"changelog-version",children:["v",l.version]})]}),n.jsx("h1",{children:l.title}),n.jsx("p",{className:"changelog-detail-summary",children:l.summary}),n.jsx("div",{className:"changelog-detail-tags",children:l.tags.map(c=>n.jsx("span",{className:"changelog-tag",children:c},c))})]}),n.jsxs("section",{className:"changelog-highlights-section",children:[n.jsx("h2",{className:"changelog-section-heading",children:"Highlights"}),n.jsx("div",{className:"changelog-highlights-grid",children:l.highlights.map(c=>n.jsxs("div",{className:"changelog-highlight-card",children:[n.jsx("span",{className:"highlight-icon",children:n.jsx(K,{name:c.icon,size:22})}),n.jsx("h3",{children:c.title}),n.jsx("p",{children:c.description})]},c.title))})]}),l.chart&&n.jsx(Jp,{chart:l.chart}),n.jsxs("section",{className:"changelog-changes-section",children:[n.jsx("h2",{className:"changelog-section-heading",children:"All Changes"}),n.jsx("div",{className:"changelog-changes-grid",children:l.changes.map(c=>n.jsxs("div",{className:`changelog-change-group changelog-change-${c.category}`,children:[n.jsx("h3",{className:"change-group-title",children:n.jsx("span",{className:`change-badge change-badge-${c.category}`,children:c.category})}),n.jsx("ul",{children:c.items.map((d,m)=>n.jsx("li",{children:d},m))})]},c.category))})]}),l.commits.length>0&&n.jsxs("section",{className:"changelog-commits-section",children:[n.jsx("h2",{className:"changelog-section-heading",children:"Commits"}),n.jsx("div",{className:"changelog-commits-list",children:l.commits.map(c=>{const[d,...m]=c.split(" ");return n.jsxs("div",{className:"changelog-commit",children:[n.jsx("code",{className:"commit-hash",children:d.slice(0,7)}),n.jsx("span",{className:"commit-msg",children:m.join(" ")})]},d)})})]}),n.jsx("nav",{className:"changelog-detail-nav",children:n.jsxs("button",{onClick:()=>le("/changelog"),children:[n.jsx(K,{name:"arrow",size:14}),"All releases"]})})]}),n.jsx(Nt,{})]}):n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"home"}),n.jsx("main",{className:"shell page-main changelog-page",children:n.jsxs("div",{className:"changelog-not-found",children:[n.jsx(K,{name:"doc",size:48}),n.jsx("h1",{children:"Entry Not Found"}),n.jsxs("p",{children:[`We couldn't find a changelog entry for "`,i,'".']}),n.jsx("button",{onClick:()=>le("/changelog"),children:"View all changelog entries"})]})}),n.jsx(Nt,{})]})}function Jp({chart:i}){return n.jsxs("section",{className:"changelog-chart-section",children:[n.jsx("h2",{className:"changelog-section-heading",children:i.title}),n.jsxs("div",{className:"changelog-chart-container",children:[i.type==="bar"&&n.jsx(Zp,{chart:i}),i.type==="pie"&&n.jsx(ef,{chart:i}),i.type==="donut"&&n.jsx(tf,{chart:i}),i.type==="line"&&n.jsx(nf,{chart:i}),i.type==="timeline"&&n.jsx(rf,{chart:i}),i.type==="comparison"&&n.jsx(af,{chart:i}),i.type==="metrics"&&n.jsx(sf,{chart:i})]})]})}function Zp({chart:i}){const l=Math.max(...i.data.map(c=>c.value));return n.jsx("div",{className:"chart-bar",children:i.data.map(c=>n.jsxs("div",{className:"chart-bar-row",children:[n.jsx("span",{className:"chart-bar-label",children:c.label}),n.jsxs("div",{className:"chart-bar-track",children:[n.jsx("div",{className:"chart-bar-fill",style:{width:`${c.value/l*100}%`,background:c.color||"var(--accent)"}}),n.jsx("span",{className:"chart-bar-value",children:c.value})]})]},c.label))})}function ef({chart:i}){const l=i.data.reduce((p,g)=>p+g.value,0);let c=0;const m=i.data.map(p=>{const g=c/l*360;c+=p.value;const E=c/l*360;return{...p,start:g,end:E}}).map(p=>{const g=p.start/360*100,E=p.end/360*100;return`${p.color||"#d96545"} ${g}% ${E}%`}).join(", ");return n.jsxs("div",{className:"chart-pie-wrapper",children:[n.jsx("div",{className:"chart-pie",style:{background:`conic-gradient(${m})`}}),n.jsx("div",{className:"chart-pie-legend",children:i.data.map(p=>n.jsxs("div",{className:"chart-legend-item",children:[n.jsx("span",{className:"chart-legend-dot",style:{background:p.color||"var(--accent)"}}),n.jsx("span",{className:"chart-legend-label",children:p.label})]},p.label))})]})}function tf({chart:i}){const l=i.data.reduce((d,m)=>d+m.value,0),c=i.data.reduce((d,m)=>{const p=d.current/l*100,g=(d.current+m.value)/l*100;return d.css+=`${m.color||"#d96545"} ${p}% ${g}%, `,d.current+=m.value,d},{css:"",current:0}).css.slice(0,-2);return n.jsxs("div",{className:"chart-donut-wrapper",children:[n.jsx("div",{className:"chart-donut",style:{background:`conic-gradient(${c})`},children:n.jsx("span",{children:i.centerLabel||l})}),n.jsx("div",{className:"chart-pie-legend",children:i.data.map(d=>n.jsxs("div",{className:"chart-legend-item",children:[n.jsx("span",{className:"chart-legend-dot",style:{background:d.color||"var(--accent)"}}),n.jsx("span",{className:"chart-legend-label",children:d.label})]},d.label))})]})}function nf({chart:i}){const l=Math.max(...i.data.map(d=>d.value),1),c=i.data.map((d,m)=>{const p=i.data.length===1?50:m/(i.data.length-1)*100,g=100-d.value/l*82-9;return`${p},${g}`}).join(" ");return n.jsxs("div",{className:"chart-line-wrapper",children:[n.jsxs("svg",{className:"chart-line",viewBox:"0 0 100 100",preserveAspectRatio:"none",role:"img","aria-label":i.title,children:[n.jsx("polyline",{points:c,fill:"none",stroke:"var(--accent)",strokeWidth:"3",vectorEffect:"non-scaling-stroke"}),i.data.map((d,m)=>{const p=i.data.length===1?50:m/(i.data.length-1)*100,g=100-d.value/l*82-9;return n.jsx("circle",{cx:p,cy:g,r:"3",fill:"var(--accent)",vectorEffect:"non-scaling-stroke"},d.label)})]}),n.jsx("div",{className:"chart-line-labels",children:i.data.map(d=>n.jsx("span",{children:d.label},d.label))})]})}function rf({chart:i}){const l=Math.max(...i.data.map(c=>c.value),1);return n.jsx("div",{className:"chart-timeline",children:i.data.map(c=>n.jsxs("div",{className:"chart-timeline-item",children:[n.jsx("div",{className:"chart-timeline-marker",style:{background:c.color||"var(--accent)"}}),n.jsxs("div",{className:"chart-timeline-content",children:[n.jsx("strong",{children:c.label}),n.jsx("div",{className:"chart-timeline-track",children:n.jsx("div",{className:"chart-timeline-fill",style:{width:`${c.value/l*100}%`,background:c.color||"var(--accent)"}})}),c.detail&&n.jsx("span",{children:c.detail})]})]},c.label))})}function sf({chart:i}){return n.jsx("div",{className:"chart-metrics",children:i.data.map(l=>n.jsxs("div",{className:"chart-metric",style:{borderTopColor:l.color||"var(--accent)"},children:[n.jsx("span",{className:"chart-metric-label",children:l.label}),n.jsx("strong",{children:l.value}),l.detail&&n.jsx("small",{children:l.detail})]},l.label))})}function af({chart:i}){const l=Math.max(...i.before.concat(i.after).map(d=>d.value),1),c=(d,m,p)=>n.jsxs("div",{className:"chart-comparison-col",children:[n.jsx("h4",{className:`comparison-label ${p}`,children:d}),m.map(g=>n.jsxs("div",{className:"chart-bar-row",children:[n.jsx("span",{className:"chart-bar-label",children:g.label}),n.jsxs("div",{className:"chart-bar-track",children:[n.jsx("div",{className:"chart-bar-fill",style:{width:`${g.value/l*100}%`,background:g.color||"var(--accent)"}}),n.jsx("span",{className:"chart-bar-value",children:g.value})]})]},g.label))]});return n.jsxs("div",{className:"chart-comparison",children:[c("Before",i.before,"comparison-before"),n.jsx("div",{className:"chart-comparison-divider",children:n.jsx(K,{name:"arrow",size:20})}),c("After",i.after,"comparison-after")]})}function ra(i){return i.avatar_url}function of(i){return`https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/svg/${Array.from(i).map(c=>c.codePointAt(0).toString(16)).join("-")}.svg`}function lf({emoji:i}){return i?i.kind==="custom"?n.jsx("img",{className:"presence-emoji",src:`https://cdn.discordapp.com/emojis/${i.value}.${i.animated?"gif":"png"}?size=18`,alt:i.name||"custom emoji"}):n.jsx("img",{className:"presence-emoji",src:of(i.value),alt:i.name||i.value}):null}function cf(i){return{playing:"Playing",listening:"Listening to",watching:"Watching",streaming:"Streaming",competing:"Competing in"}[i]||(i?`${i.charAt(0).toUpperCase()}${i.slice(1)}`:"Activity")}function uf({activity:i}){const l=i.kind==="spotify",c=l?"Listening on Spotify":cf(i.type),d=l?i.details||"Spotify":i.name,m=l?i.state:i.details,p=n.jsxs("span",{className:`activity-card activity-${i.kind}`,children:[i.image_url&&n.jsx("img",{className:"activity-art",src:i.image_url,alt:""}),n.jsxs("span",{className:"activity-copy",children:[n.jsx("strong",{children:c}),n.jsx("span",{children:d}),m&&n.jsx("small",{children:m})]})]});return i.url?n.jsx("a",{className:"presence-activity",href:i.url,target:"_blank",rel:"noreferrer",children:p}):n.jsx("span",{className:"presence-activity",children:p})}function rd(i){return i.status_label||{online:"Online",idle:"Idle",dnd:"Do Not Disturb",offline:"Offline"}[i.status||"offline"]||"Offline"}function sd({member:i}){const l=i.custom_status,c=i.activities||[],d=!!(l!=null&&l.text||l!=null&&l.emoji);return!d&&!c.length?null:n.jsxs("span",{className:"presence-stack",children:[d&&n.jsxs("span",{className:"presence-line",children:[n.jsx(lf,{emoji:l==null?void 0:l.emoji}),(l==null?void 0:l.text)||"Custom status"]}),c.length>0&&n.jsx("span",{className:"presence-line activity-list",children:c.map((m,p)=>n.jsx(uf,{activity:m},`${m.kind}-${m.name}-${p}`))})]})}const ad=`
.team-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:58px}.team-card{display:flex;flex-direction:column;min-width:0;min-height:286px;overflow:hidden;padding:0;color:var(--ink);text-align:left;background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow-soft)}.team-card:hover{border-color:#dfaa98;transform:translateY(-2px)}.team-card-art,.team-profile-banner{min-height:105px;background:linear-gradient(135deg,var(--callout),var(--surface-muted));background-size:cover;background-position:center}.team-card-body{display:flex;align-items:flex-start;flex:1;min-width:0;gap:14px;padding:18px}.team-card-body>div:last-child{min-width:0}.team-card h2,.team-card p{overflow-wrap:anywhere}.team-avatar,.team-profile-avatar{display:grid;place-items:center;flex:0 0 auto;overflow:hidden;color:#fffaf5;background:var(--accent);border-radius:50%;font-weight:800;object-fit:cover}.team-avatar{width:48px;height:48px;margin-top:-35px;border:3px solid var(--surface)}.team-role{color:var(--accent-dark);text-transform:uppercase;letter-spacing:.1em;font:700 9px "Space Mono",monospace}.team-card h2{margin:5px 0 6px;font-size:17px}.team-card p{margin:0 0 10px;color:var(--muted);font-size:11px;line-height:1.6}.team-status{color:var(--dim);font-size:10px}.presence-stack{display:block}.presence-line{display:flex;align-items:center;flex-wrap:wrap;gap:7px;margin-top:7px;color:var(--muted);font-size:10px}.presence-activity{display:inline-flex;align-items:center;gap:4px;color:inherit}.presence-activity:hover{text-decoration:none}.activity-card{display:flex;align-items:center;min-width:0;gap:8px;padding:7px 9px;background:var(--surface-muted);border:1px solid var(--line);border-radius:8px;text-align:left}.activity-art{width:30px;height:30px;flex:0 0 auto;border-radius:5px;object-fit:cover}.activity-copy{display:flex;min-width:0;flex-direction:column;gap:1px}.activity-copy strong{color:var(--accent-dark);font-size:9px;text-transform:uppercase;letter-spacing:.06em}.activity-copy span,.activity-copy small{overflow:hidden;max-width:210px;text-overflow:ellipsis;white-space:nowrap}.activity-copy span{color:var(--ink);font-size:10px}.activity-copy small{color:var(--dim);font-size:9px}.presence-emoji{width:18px;height:18px;object-fit:contain;vertical-align:middle}.is-online{color:var(--sage)}.team-profile-page{max-width:760px}.team-back{width:auto;margin:0 0 18px;border:0;background:transparent}.team-profile-banner{min-height:220px;border:1px solid var(--line);border-radius:14px 14px 0 0}.team-profile-card{padding:0 34px 38px;text-align:center;background:var(--surface);border:1px solid var(--line);border-top:0;border-radius:0 0 14px 14px;box-shadow:var(--shadow-soft)}.team-profile-avatar{width:100px;height:100px;margin:-50px auto 18px;border:5px solid var(--surface);font-size:32px}.team-profile-card h1{margin:8px 0 5px;font-size:34px;letter-spacing:-.07em}.team-profile-handle{color:var(--dim);font-size:11px}.team-profile-bio{max-width:560px;margin:27px auto 0;color:var(--muted);line-height:1.8}.team-activity{display:block;width:min(100%,560px);margin:20px auto 0;padding:12px;color:var(--muted);background:var(--surface-muted);border:1px solid var(--line);border-radius:12px;font-size:10px;text-align:left}.team-activity .presence-line{margin-top:0}.team-activity .activity-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));align-items:stretch}.team-activity .activity-card{height:100%;width:100%}@media(max-width:800px){.team-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.team-grid{grid-template-columns:1fr;margin-top:38px}.team-profile-card{padding-left:18px;padding-right:18px}.team-profile-banner{min-height:150px}}`;function df(){const[i,l]=T.useState([]);return T.useEffect(()=>{fh().then(l).catch(()=>l([]))},[]),n.jsxs(n.Fragment,{children:[n.jsx("style",{children:ad}),n.jsx(We,{page:"team"}),n.jsxs("main",{className:"shell page-main",children:[n.jsxs("div",{className:"page-heading",children:[n.jsx("div",{className:"eyebrow",children:"The people behind Niko"}),n.jsx("h1",{children:"Meet the team."}),n.jsx("p",{children:"A small group of builders, moderators, and creative minds keeping Niko friendly, useful, and moving forward."})]}),n.jsxs("div",{className:"team-grid",children:[i.map(c=>n.jsxs("button",{className:"team-card",onClick:()=>le(`/team/${c.id}`),children:[n.jsx("div",{className:"team-card-art",style:c.public_banner_url?{backgroundImage:`url(${c.public_banner_url})`}:void 0}),n.jsxs("div",{className:"team-card-body",children:[ra(c)?n.jsx("img",{className:"team-avatar",src:ra(c),alt:""}):n.jsx("span",{className:"team-avatar team-avatar-fallback",children:c.name.slice(0,1)}),n.jsxs("div",{children:[n.jsx("span",{className:"team-role",children:c.role_label}),n.jsx("h2",{children:c.name}),n.jsx("p",{children:c.bio||"Part of the Niko team."}),n.jsx("span",{className:`team-status status-${c.status||"offline"} ${c.status==="online"?"is-online":""}`,children:rd(c)}),n.jsx(sd,{member:c})]})]})]},c.id)),!i.length&&n.jsx("div",{className:"empty-state",children:"The team roster is being prepared."})]})]}),n.jsx(Nt,{})]})}function mf({id:i}){const[l,c]=T.useState(null),[d,m]=T.useState("");return T.useEffect(()=>{gh(i).then(c).catch(p=>m(p instanceof Error?p.message:"Team member not found."))},[i]),n.jsxs(n.Fragment,{children:[n.jsx("style",{children:ad}),n.jsx(We,{page:"team"}),n.jsx("main",{className:"shell page-main team-profile-page",children:d?n.jsx("div",{className:"empty-state",children:d}):l?n.jsxs(n.Fragment,{children:[n.jsx("button",{className:"back-link team-back",onClick:()=>le("/team"),children:"← Back to team"}),n.jsx("div",{className:"team-profile-banner",style:l.public_banner_url?{backgroundImage:`url(${l.public_banner_url})`}:void 0}),n.jsxs("section",{className:"team-profile-card",children:[ra(l)?n.jsx("img",{className:"team-profile-avatar",src:ra(l),alt:""}):n.jsx("span",{className:"team-profile-avatar team-avatar-fallback",children:l.name.slice(0,1)}),n.jsx("div",{className:"team-role",children:l.role_label}),n.jsx("h1",{children:l.name}),n.jsxs("p",{className:"team-profile-handle",children:[l.username?`@${l.username}`:"Niko staff"," · ",n.jsx("span",{className:`status-${l.status||"offline"} ${l.status==="online"?"is-online":""}`,children:rd(l)})]}),n.jsx("p",{className:"team-profile-bio",children:l.bio||"This team member has not added an extended introduction yet."}),n.jsxs("div",{className:"team-activity",children:[n.jsx(sd,{member:l}),!l.custom_status&&!(l.activities||[]).length&&"No current activity"]})]})]}):n.jsx("div",{className:"section-loading",children:"Loading profile…"})}),n.jsx(Nt,{})]})}function hf(){const[i,l]=T.useState(null),[c,d]=T.useState(null),[m,p]=T.useState(null),[g,E]=T.useState([]),[b,z]=T.useState({public_bio:"",public_banner_url:"",public_visible:!0}),[C,N]=T.useState({avatar_url:"",banner_url:""}),[M,I]=T.useState(""),[R,_]=T.useState(""),[j,J]=T.useState(!1),[S,V]=T.useState(!1);if(T.useEffect(()=>{Promise.all([fo(),go(),ea(),vo()]).then(([ne,je,Te,Se])=>{l(ne),d(je),p(Te),E(Se),z({public_bio:je.profile.bio||"",public_banner_url:je.profile.public_banner_url||"",public_visible:je.profile.visible!==!1})}).catch(ne=>_(ne instanceof Error?ne.message:"Staff access unavailable."))},[]),!i||!c&&!R)return n.jsxs("div",{className:"dashboard-state",children:[n.jsx("div",{className:"loading-ring"}),n.jsx("p",{children:"Checking staff access…"})]});if(R||!c||!i.authenticated)return n.jsxs(n.Fragment,{children:[n.jsx(We,{page:"dashboard"}),n.jsx("main",{className:"auth-page",children:n.jsxs("div",{className:"auth-card",children:[n.jsx("div",{className:"eyebrow",children:"Staff workspace"}),n.jsx("h1",{children:"Private team area."}),n.jsx("p",{children:i!=null&&i.authenticated?R||"This area is only available to official Niko staff.":"Sign in with Discord to continue."}),!(i!=null&&i.authenticated)&&n.jsx("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard/staff",children:"Continue with Discord"}),n.jsx("button",{className:"back-link",onClick:()=>le("/dashboard"),children:"Return to dashboard"})]})})]});const ee=["owner","head_admin","graphic_designer"].includes(c.role),se=(ne,je)=>z(Te=>({...Te,[ne]:je})),B=async()=>{if(!j){J(!0),_(""),I("");try{await vh(b,i.csrf_token),I("Your public team listing was saved.")}catch(ne){_(ne instanceof Error?ne.message:"Could not save listing.")}finally{J(!1)}}},Q=async()=>{if(!S){V(!0),_(""),I("");try{await yh(C,i.csrf_token),I("Niko's global profile was updated.")}catch(ne){_(ne instanceof Error?ne.message:"Could not update global profile.")}finally{V(!1)}}},pe=n.jsxs("div",{className:"staff-page",children:[n.jsxs("header",{className:"staff-heading",children:[n.jsxs("div",{children:[n.jsx("div",{className:"eyebrow",children:"Staff workspace"}),n.jsx("h1",{children:"Shape your presence."}),n.jsxs("p",{children:["Manage the public details granted to your ",n.jsx("strong",{children:c.role_label})," role. Your name and avatar always come directly from Discord."]})]}),n.jsxs("div",{className:"staff-role-card",children:[n.jsx("span",{className:"staff-role-mark",children:c.role_label.slice(0,1)}),n.jsxs("span",{children:[n.jsx("small",{children:"Signed in as"}),n.jsx("strong",{children:c.role_label})]})]})]}),n.jsxs("div",{className:"staff-layout",children:[n.jsxs("section",{className:"staff-panel staff-panel-main",children:[n.jsxs("div",{className:"staff-panel-heading",children:[n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"Public listing"}),n.jsx("h2",{children:"How the team sees you"}),n.jsx("p",{children:"Keep your introduction current while Discord remains the source of truth for your identity."})]}),n.jsx("span",{className:"staff-step",children:"01"})]}),n.jsxs("div",{className:"staff-fields",children:[n.jsxs("label",{className:"form-field",children:[n.jsx("span",{className:"form-label",children:"Banner URL"}),n.jsx("input",{value:b.public_banner_url,onChange:ne=>se("public_banner_url",ne.target.value),placeholder:"https://…"}),n.jsx("small",{children:"Use a publicly reachable image. Leave blank for no banner."})]}),n.jsxs("label",{className:"form-field staff-bio-field",children:[n.jsx("span",{className:"form-label",children:"Extended introduction"}),n.jsx("textarea",{value:b.public_bio,onChange:ne=>se("public_bio",ne.target.value),maxLength:1200,placeholder:"Tell the community what you do…"}),n.jsxs("small",{children:[b.public_bio.length,"/1200 characters"]})]})]}),n.jsxs("label",{className:"setting-row staff-visibility",children:[n.jsxs("span",{children:[n.jsx("strong",{children:"Show me on the public Team page"}),n.jsx("small",{children:"Hide your listing without removing your staff access."})]}),n.jsx("input",{type:"checkbox",checked:b.public_visible,onChange:ne=>se("public_visible",ne.target.checked)}),n.jsx("i",{})]}),n.jsxs("div",{className:"staff-panel-footer",children:[n.jsx("span",{children:"Changes apply immediately to your public profile."}),n.jsx("button",{type:"button",className:"button button-primary",onClick:B,disabled:j,children:j?"Saving…":"Save public listing"})]})]}),n.jsxs("aside",{className:"staff-sidebar-card",children:[n.jsx("span",{className:"panel-kicker",children:"Profile rules"}),n.jsx("h3",{children:"Stay consistent with Discord"}),n.jsx("p",{children:"Your global display name and profile picture sync automatically, so updates made in Discord are reflected here without another form."}),n.jsxs("div",{className:"staff-rule",children:[n.jsx("span",{children:"Identity"}),n.jsx("strong",{children:"Discord synced"})]}),n.jsxs("div",{className:"staff-rule",children:[n.jsx("span",{children:"Editable"}),n.jsx("strong",{children:"Bio · banner · visibility"})]})]})]}),ee&&n.jsxs("section",{className:"staff-panel staff-global-panel",children:[n.jsxs("div",{className:"staff-panel-heading",children:[n.jsxs("div",{children:[n.jsx("span",{className:"panel-kicker",children:"Graphic direction"}),n.jsx("h2",{children:"Global Niko profile"}),n.jsx("p",{children:"Reserved for Graphic Designers, Head Admins, and owners. Paste publicly reachable image URLs."})]}),n.jsx("span",{className:"staff-step",children:"02"})]}),n.jsxs("div",{className:"staff-fields staff-fields-two",children:[n.jsxs("label",{className:"form-field",children:[n.jsx("span",{className:"form-label",children:"Bot avatar URL"}),n.jsx("input",{value:C.avatar_url,onChange:ne=>N({...C,avatar_url:ne.target.value}),placeholder:"https://…"})]}),n.jsxs("label",{className:"form-field",children:[n.jsx("span",{className:"form-label",children:"Bot banner URL"}),n.jsx("input",{value:C.banner_url,onChange:ne=>N({...C,banner_url:ne.target.value}),placeholder:"https://…"})]})]}),n.jsxs("div",{className:"staff-panel-footer",children:[n.jsx("span",{children:"Updates the bot-wide Discord profile."}),n.jsx("button",{type:"button",className:"button button-primary",onClick:Q,disabled:S,children:S?"Updating…":"Update global profile"})]})]}),M&&n.jsx("div",{className:"notice",children:M}),R&&n.jsx("div",{className:"notice warning",children:R})]});return n.jsx(Xu,{user:i.user,guilds:g,selectedGuild:null,view:"overview",section:"overview",stats:m,staffRole:c.role,onHome:()=>le(Xn()),onServers:()=>le(yo()),onGuildChange:()=>{},onSectionChange:()=>{},onRefresh:()=>window.location.reload(),refreshing:!1,children:pe})}function pf(){const[i,l]=T.useState(Mu);if(T.useEffect(()=>{const c=()=>l(Mu());return window.addEventListener("popstate",c),()=>window.removeEventListener("popstate",c)},[]),i==="commands")return n.jsx(np,{});if(i==="docs-detail"){const c=window.location.pathname.split("/"),d=c[c.length-1];return n.jsx(Ep,{slug:d})}if(i==="docs")return n.jsx(Mp,{});if(i==="staff")return n.jsx(hf,{});if(i==="dashboard")return n.jsx(bp,{});if(i==="team")return n.jsx(df,{});if(i==="team-member")return n.jsx(mf,{id:window.location.pathname.split("/").filter(Boolean)[1]||""});if(i==="privacy")return n.jsx(po,{type:"privacy"});if(i==="terms")return n.jsx(po,{type:"terms"});if(i==="community")return n.jsx(po,{type:"community"});if(i==="donate")return n.jsx(Ap,{});if(i==="transcript"){const d=window.location.pathname.split("/").filter(Boolean)[1]||"";return n.jsx(Kp,{transcriptId:d})}if(i==="changelog")return n.jsx(Xp,{});if(i==="changelog-detail"){const c=window.location.pathname.split("/"),d=c[c.length-1];return n.jsx(Yp,{slug:d})}return n.jsx(Pp,{})}mh.createRoot(document.getElementById("root")).render(n.jsx(T.StrictMode,{children:n.jsx(pf,{})}));
