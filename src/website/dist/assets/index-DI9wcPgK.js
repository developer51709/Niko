var nh=Object.defineProperty;var rh=(i,l,c)=>l in i?nh(i,l,{enumerable:!0,configurable:!0,writable:!0,value:c}):i[l]=c;var vu=(i,l,c)=>rh(i,typeof l!="symbol"?l+"":l,c);(function(){const l=document.createElement("link").relList;if(l&&l.supports&&l.supports("modulepreload"))return;for(const m of document.querySelectorAll('link[rel="modulepreload"]'))d(m);new MutationObserver(m=>{for(const p of m)if(p.type==="childList")for(const g of p.addedNodes)g.tagName==="LINK"&&g.rel==="modulepreload"&&d(g)}).observe(document,{childList:!0,subtree:!0});function c(m){const p={};return m.integrity&&(p.integrity=m.integrity),m.referrerPolicy&&(p.referrerPolicy=m.referrerPolicy),m.crossOrigin==="use-credentials"?p.credentials="include":m.crossOrigin==="anonymous"?p.credentials="omit":p.credentials="same-origin",p}function d(m){if(m.ep)return;m.ep=!0;const p=c(m);fetch(m.href,p)}})();var no={exports:{}},Ir={},ro={exports:{}},ae={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var yu;function sh(){if(yu)return ae;yu=1;var i=Symbol.for("react.element"),l=Symbol.for("react.portal"),c=Symbol.for("react.fragment"),d=Symbol.for("react.strict_mode"),m=Symbol.for("react.profiler"),p=Symbol.for("react.provider"),g=Symbol.for("react.context"),T=Symbol.for("react.forward_ref"),k=Symbol.for("react.suspense"),D=Symbol.for("react.memo"),N=Symbol.for("react.lazy"),C=Symbol.iterator;function L(y){return y===null||typeof y!="object"?null:(y=C&&y[C]||y["@@iterator"],typeof y=="function"?y:null)}var I={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},A=Object.assign,B={};function j(y,M,se){this.props=y,this.context=M,this.refs=B,this.updater=se||I}j.prototype.isReactComponent={},j.prototype.setState=function(y,M){if(typeof y!="object"&&typeof y!="function"&&y!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,y,M,"setState")},j.prototype.forceUpdate=function(y){this.updater.enqueueForceUpdate(this,y,"forceUpdate")};function J(){}J.prototype=j.prototype;function S(y,M,se){this.props=y,this.context=M,this.refs=B,this.updater=se||I}var V=S.prototype=new J;V.constructor=S,A(V,j.prototype),V.isPureReactComponent=!0;var ee=Array.isArray,re=Object.prototype.hasOwnProperty,z={current:null},O={key:!0,ref:!0,__self:!0,__source:!0};function ce(y,M,se){var ie,ue={},de=null,ve=null;if(M!=null)for(ie in M.ref!==void 0&&(ve=M.ref),M.key!==void 0&&(de=""+M.key),M)re.call(M,ie)&&!O.hasOwnProperty(ie)&&(ue[ie]=M[ie]);var pe=arguments.length-2;if(pe===1)ue.children=se;else if(1<pe){for(var we=Array(pe),ot=0;ot<pe;ot++)we[ot]=arguments[ot+2];ue.children=we}if(y&&y.defaultProps)for(ie in pe=y.defaultProps,pe)ue[ie]===void 0&&(ue[ie]=pe[ie]);return{$$typeof:i,type:y,key:de,ref:ve,props:ue,_owner:z.current}}function ge(y,M){return{$$typeof:i,type:y.type,key:M,ref:y.ref,props:y.props,_owner:y._owner}}function Fe(y){return typeof y=="object"&&y!==null&&y.$$typeof===i}function Ce(y){var M={"=":"=0",":":"=2"};return"$"+y.replace(/[=:]/g,function(se){return M[se]})}var _e=/\/+/g;function ne(y,M){return typeof y=="object"&&y!==null&&y.key!=null?Ce(""+y.key):M.toString(36)}function Pe(y,M,se,ie,ue){var de=typeof y;(de==="undefined"||de==="boolean")&&(y=null);var ve=!1;if(y===null)ve=!0;else switch(de){case"string":case"number":ve=!0;break;case"object":switch(y.$$typeof){case i:case l:ve=!0}}if(ve)return ve=y,ue=ue(ve),y=ie===""?"."+ne(ve,0):ie,ee(ue)?(se="",y!=null&&(se=y.replace(_e,"$&/")+"/"),Pe(ue,M,se,"",function(ot){return ot})):ue!=null&&(Fe(ue)&&(ue=ge(ue,se+(!ue.key||ve&&ve.key===ue.key?"":(""+ue.key).replace(_e,"$&/")+"/")+y)),M.push(ue)),1;if(ve=0,ie=ie===""?".":ie+":",ee(y))for(var pe=0;pe<y.length;pe++){de=y[pe];var we=ie+ne(de,pe);ve+=Pe(de,M,se,we,ue)}else if(we=L(y),typeof we=="function")for(y=we.call(y),pe=0;!(de=y.next()).done;)de=de.value,we=ie+ne(de,pe++),ve+=Pe(de,M,se,we,ue);else if(de==="object")throw M=String(y),Error("Objects are not valid as a React child (found: "+(M==="[object Object]"?"object with keys {"+Object.keys(y).join(", ")+"}":M)+"). If you meant to render a collection of children, use an array instead.");return ve}function He(y,M,se){if(y==null)return y;var ie=[],ue=0;return Pe(y,ie,"","",function(de){return M.call(se,de,ue++)}),ie}function ze(y){if(y._status===-1){var M=y._result;M=M(),M.then(function(se){(y._status===0||y._status===-1)&&(y._status=1,y._result=se)},function(se){(y._status===0||y._status===-1)&&(y._status=2,y._result=se)}),y._status===-1&&(y._status=0,y._result=M)}if(y._status===1)return y._result.default;throw y._result}var he={current:null},W={transition:null},Z={ReactCurrentDispatcher:he,ReactCurrentBatchConfig:W,ReactCurrentOwner:z};function H(){throw Error("act(...) is not supported in production builds of React.")}return ae.Children={map:He,forEach:function(y,M,se){He(y,function(){M.apply(this,arguments)},se)},count:function(y){var M=0;return He(y,function(){M++}),M},toArray:function(y){return He(y,function(M){return M})||[]},only:function(y){if(!Fe(y))throw Error("React.Children.only expected to receive a single React element child.");return y}},ae.Component=j,ae.Fragment=c,ae.Profiler=m,ae.PureComponent=S,ae.StrictMode=d,ae.Suspense=k,ae.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Z,ae.act=H,ae.cloneElement=function(y,M,se){if(y==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+y+".");var ie=A({},y.props),ue=y.key,de=y.ref,ve=y._owner;if(M!=null){if(M.ref!==void 0&&(de=M.ref,ve=z.current),M.key!==void 0&&(ue=""+M.key),y.type&&y.type.defaultProps)var pe=y.type.defaultProps;for(we in M)re.call(M,we)&&!O.hasOwnProperty(we)&&(ie[we]=M[we]===void 0&&pe!==void 0?pe[we]:M[we])}var we=arguments.length-2;if(we===1)ie.children=se;else if(1<we){pe=Array(we);for(var ot=0;ot<we;ot++)pe[ot]=arguments[ot+2];ie.children=pe}return{$$typeof:i,type:y.type,key:ue,ref:de,props:ie,_owner:ve}},ae.createContext=function(y){return y={$$typeof:g,_currentValue:y,_currentValue2:y,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},y.Provider={$$typeof:p,_context:y},y.Consumer=y},ae.createElement=ce,ae.createFactory=function(y){var M=ce.bind(null,y);return M.type=y,M},ae.createRef=function(){return{current:null}},ae.forwardRef=function(y){return{$$typeof:T,render:y}},ae.isValidElement=Fe,ae.lazy=function(y){return{$$typeof:N,_payload:{_status:-1,_result:y},_init:ze}},ae.memo=function(y,M){return{$$typeof:D,type:y,compare:M===void 0?null:M}},ae.startTransition=function(y){var M=W.transition;W.transition={};try{y()}finally{W.transition=M}},ae.unstable_act=H,ae.useCallback=function(y,M){return he.current.useCallback(y,M)},ae.useContext=function(y){return he.current.useContext(y)},ae.useDebugValue=function(){},ae.useDeferredValue=function(y){return he.current.useDeferredValue(y)},ae.useEffect=function(y,M){return he.current.useEffect(y,M)},ae.useId=function(){return he.current.useId()},ae.useImperativeHandle=function(y,M,se){return he.current.useImperativeHandle(y,M,se)},ae.useInsertionEffect=function(y,M){return he.current.useInsertionEffect(y,M)},ae.useLayoutEffect=function(y,M){return he.current.useLayoutEffect(y,M)},ae.useMemo=function(y,M){return he.current.useMemo(y,M)},ae.useReducer=function(y,M,se){return he.current.useReducer(y,M,se)},ae.useRef=function(y){return he.current.useRef(y)},ae.useState=function(y){return he.current.useState(y)},ae.useSyncExternalStore=function(y,M,se){return he.current.useSyncExternalStore(y,M,se)},ae.useTransition=function(){return he.current.useTransition()},ae.version="18.3.1",ae}var xu;function wo(){return xu||(xu=1,ro.exports=sh()),ro.exports}/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var ku;function ah(){if(ku)return Ir;ku=1;var i=wo(),l=Symbol.for("react.element"),c=Symbol.for("react.fragment"),d=Object.prototype.hasOwnProperty,m=i.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,p={key:!0,ref:!0,__self:!0,__source:!0};function g(T,k,D){var N,C={},L=null,I=null;D!==void 0&&(L=""+D),k.key!==void 0&&(L=""+k.key),k.ref!==void 0&&(I=k.ref);for(N in k)d.call(k,N)&&!p.hasOwnProperty(N)&&(C[N]=k[N]);if(T&&T.defaultProps)for(N in k=T.defaultProps,k)C[N]===void 0&&(C[N]=k[N]);return{$$typeof:l,type:T,key:L,ref:I,props:C,_owner:m.current}}return Ir.Fragment=c,Ir.jsx=g,Ir.jsxs=g,Ir}var wu;function ih(){return wu||(wu=1,no.exports=ah()),no.exports}var r=ih(),_=wo(),Ks={},so={exports:{}},st={},ao={exports:{}},io={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var bu;function oh(){return bu||(bu=1,(function(i){function l(W,Z){var H=W.length;W.push(Z);e:for(;0<H;){var y=H-1>>>1,M=W[y];if(0<m(M,Z))W[y]=Z,W[H]=M,H=y;else break e}}function c(W){return W.length===0?null:W[0]}function d(W){if(W.length===0)return null;var Z=W[0],H=W.pop();if(H!==Z){W[0]=H;e:for(var y=0,M=W.length,se=M>>>1;y<se;){var ie=2*(y+1)-1,ue=W[ie],de=ie+1,ve=W[de];if(0>m(ue,H))de<M&&0>m(ve,ue)?(W[y]=ve,W[de]=H,y=de):(W[y]=ue,W[ie]=H,y=ie);else if(de<M&&0>m(ve,H))W[y]=ve,W[de]=H,y=de;else break e}}return Z}function m(W,Z){var H=W.sortIndex-Z.sortIndex;return H!==0?H:W.id-Z.id}if(typeof performance=="object"&&typeof performance.now=="function"){var p=performance;i.unstable_now=function(){return p.now()}}else{var g=Date,T=g.now();i.unstable_now=function(){return g.now()-T}}var k=[],D=[],N=1,C=null,L=3,I=!1,A=!1,B=!1,j=typeof setTimeout=="function"?setTimeout:null,J=typeof clearTimeout=="function"?clearTimeout:null,S=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function V(W){for(var Z=c(D);Z!==null;){if(Z.callback===null)d(D);else if(Z.startTime<=W)d(D),Z.sortIndex=Z.expirationTime,l(k,Z);else break;Z=c(D)}}function ee(W){if(B=!1,V(W),!A)if(c(k)!==null)A=!0,ze(re);else{var Z=c(D);Z!==null&&he(ee,Z.startTime-W)}}function re(W,Z){A=!1,B&&(B=!1,J(ce),ce=-1),I=!0;var H=L;try{for(V(Z),C=c(k);C!==null&&(!(C.expirationTime>Z)||W&&!Ce());){var y=C.callback;if(typeof y=="function"){C.callback=null,L=C.priorityLevel;var M=y(C.expirationTime<=Z);Z=i.unstable_now(),typeof M=="function"?C.callback=M:C===c(k)&&d(k),V(Z)}else d(k);C=c(k)}if(C!==null)var se=!0;else{var ie=c(D);ie!==null&&he(ee,ie.startTime-Z),se=!1}return se}finally{C=null,L=H,I=!1}}var z=!1,O=null,ce=-1,ge=5,Fe=-1;function Ce(){return!(i.unstable_now()-Fe<ge)}function _e(){if(O!==null){var W=i.unstable_now();Fe=W;var Z=!0;try{Z=O(!0,W)}finally{Z?ne():(z=!1,O=null)}}else z=!1}var ne;if(typeof S=="function")ne=function(){S(_e)};else if(typeof MessageChannel<"u"){var Pe=new MessageChannel,He=Pe.port2;Pe.port1.onmessage=_e,ne=function(){He.postMessage(null)}}else ne=function(){j(_e,0)};function ze(W){O=W,z||(z=!0,ne())}function he(W,Z){ce=j(function(){W(i.unstable_now())},Z)}i.unstable_IdlePriority=5,i.unstable_ImmediatePriority=1,i.unstable_LowPriority=4,i.unstable_NormalPriority=3,i.unstable_Profiling=null,i.unstable_UserBlockingPriority=2,i.unstable_cancelCallback=function(W){W.callback=null},i.unstable_continueExecution=function(){A||I||(A=!0,ze(re))},i.unstable_forceFrameRate=function(W){0>W||125<W?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):ge=0<W?Math.floor(1e3/W):5},i.unstable_getCurrentPriorityLevel=function(){return L},i.unstable_getFirstCallbackNode=function(){return c(k)},i.unstable_next=function(W){switch(L){case 1:case 2:case 3:var Z=3;break;default:Z=L}var H=L;L=Z;try{return W()}finally{L=H}},i.unstable_pauseExecution=function(){},i.unstable_requestPaint=function(){},i.unstable_runWithPriority=function(W,Z){switch(W){case 1:case 2:case 3:case 4:case 5:break;default:W=3}var H=L;L=W;try{return Z()}finally{L=H}},i.unstable_scheduleCallback=function(W,Z,H){var y=i.unstable_now();switch(typeof H=="object"&&H!==null?(H=H.delay,H=typeof H=="number"&&0<H?y+H:y):H=y,W){case 1:var M=-1;break;case 2:M=250;break;case 5:M=1073741823;break;case 4:M=1e4;break;default:M=5e3}return M=H+M,W={id:N++,callback:Z,priorityLevel:W,startTime:H,expirationTime:M,sortIndex:-1},H>y?(W.sortIndex=H,l(D,W),c(k)===null&&W===c(D)&&(B?(J(ce),ce=-1):B=!0,he(ee,H-y))):(W.sortIndex=M,l(k,W),A||I||(A=!0,ze(re))),W},i.unstable_shouldYield=Ce,i.unstable_wrapCallback=function(W){var Z=L;return function(){var H=L;L=Z;try{return W.apply(this,arguments)}finally{L=H}}}})(io)),io}var ju;function lh(){return ju||(ju=1,ao.exports=oh()),ao.exports}/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var Su;function ch(){if(Su)return st;Su=1;var i=wo(),l=lh();function c(e){for(var t="https://reactjs.org/docs/error-decoder.html?invariant="+e,n=1;n<arguments.length;n++)t+="&args[]="+encodeURIComponent(arguments[n]);return"Minified React error #"+e+"; visit "+t+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var d=new Set,m={};function p(e,t){g(e,t),g(e+"Capture",t)}function g(e,t){for(m[e]=t,e=0;e<t.length;e++)d.add(t[e])}var T=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),k=Object.prototype.hasOwnProperty,D=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,N={},C={};function L(e){return k.call(C,e)?!0:k.call(N,e)?!1:D.test(e)?C[e]=!0:(N[e]=!0,!1)}function I(e,t,n,s){if(n!==null&&n.type===0)return!1;switch(typeof t){case"function":case"symbol":return!0;case"boolean":return s?!1:n!==null?!n.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function A(e,t,n,s){if(t===null||typeof t>"u"||I(e,t,n,s))return!0;if(s)return!1;if(n!==null)switch(n.type){case 3:return!t;case 4:return t===!1;case 5:return isNaN(t);case 6:return isNaN(t)||1>t}return!1}function B(e,t,n,s,a,o,u){this.acceptsBooleans=t===2||t===3||t===4,this.attributeName=s,this.attributeNamespace=a,this.mustUseProperty=n,this.propertyName=e,this.type=t,this.sanitizeURL=o,this.removeEmptyString=u}var j={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){j[e]=new B(e,0,!1,e,null,!1,!1)}),[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var t=e[0];j[t]=new B(t,1,!1,e[1],null,!1,!1)}),["contentEditable","draggable","spellCheck","value"].forEach(function(e){j[e]=new B(e,2,!1,e.toLowerCase(),null,!1,!1)}),["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){j[e]=new B(e,2,!1,e,null,!1,!1)}),"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){j[e]=new B(e,3,!1,e.toLowerCase(),null,!1,!1)}),["checked","multiple","muted","selected"].forEach(function(e){j[e]=new B(e,3,!0,e,null,!1,!1)}),["capture","download"].forEach(function(e){j[e]=new B(e,4,!1,e,null,!1,!1)}),["cols","rows","size","span"].forEach(function(e){j[e]=new B(e,6,!1,e,null,!1,!1)}),["rowSpan","start"].forEach(function(e){j[e]=new B(e,5,!1,e.toLowerCase(),null,!1,!1)});var J=/[\-:]([a-z])/g;function S(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var t=e.replace(J,S);j[t]=new B(t,1,!1,e,null,!1,!1)}),"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var t=e.replace(J,S);j[t]=new B(t,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)}),["xml:base","xml:lang","xml:space"].forEach(function(e){var t=e.replace(J,S);j[t]=new B(t,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)}),["tabIndex","crossOrigin"].forEach(function(e){j[e]=new B(e,1,!1,e.toLowerCase(),null,!1,!1)}),j.xlinkHref=new B("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1),["src","href","action","formAction"].forEach(function(e){j[e]=new B(e,1,!1,e.toLowerCase(),null,!0,!0)});function V(e,t,n,s){var a=j.hasOwnProperty(t)?j[t]:null;(a!==null?a.type!==0:s||!(2<t.length)||t[0]!=="o"&&t[0]!=="O"||t[1]!=="n"&&t[1]!=="N")&&(A(t,n,a,s)&&(n=null),s||a===null?L(t)&&(n===null?e.removeAttribute(t):e.setAttribute(t,""+n)):a.mustUseProperty?e[a.propertyName]=n===null?a.type===3?!1:"":n:(t=a.attributeName,s=a.attributeNamespace,n===null?e.removeAttribute(t):(a=a.type,n=a===3||a===4&&n===!0?"":""+n,s?e.setAttributeNS(s,t,n):e.setAttribute(t,n))))}var ee=i.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,re=Symbol.for("react.element"),z=Symbol.for("react.portal"),O=Symbol.for("react.fragment"),ce=Symbol.for("react.strict_mode"),ge=Symbol.for("react.profiler"),Fe=Symbol.for("react.provider"),Ce=Symbol.for("react.context"),_e=Symbol.for("react.forward_ref"),ne=Symbol.for("react.suspense"),Pe=Symbol.for("react.suspense_list"),He=Symbol.for("react.memo"),ze=Symbol.for("react.lazy"),he=Symbol.for("react.offscreen"),W=Symbol.iterator;function Z(e){return e===null||typeof e!="object"?null:(e=W&&e[W]||e["@@iterator"],typeof e=="function"?e:null)}var H=Object.assign,y;function M(e){if(y===void 0)try{throw Error()}catch(n){var t=n.stack.trim().match(/\n( *(at )?)/);y=t&&t[1]||""}return`
`+y+e}var se=!1;function ie(e,t){if(!e||se)return"";se=!0;var n=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(t)if(t=function(){throw Error()},Object.defineProperty(t.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(t,[])}catch(b){var s=b}Reflect.construct(e,[],t)}else{try{t.call()}catch(b){s=b}e.call(t.prototype)}else{try{throw Error()}catch(b){s=b}e()}}catch(b){if(b&&s&&typeof b.stack=="string"){for(var a=b.stack.split(`
`),o=s.stack.split(`
`),u=a.length-1,h=o.length-1;1<=u&&0<=h&&a[u]!==o[h];)h--;for(;1<=u&&0<=h;u--,h--)if(a[u]!==o[h]){if(u!==1||h!==1)do if(u--,h--,0>h||a[u]!==o[h]){var f=`
`+a[u].replace(" at new "," at ");return e.displayName&&f.includes("<anonymous>")&&(f=f.replace("<anonymous>",e.displayName)),f}while(1<=u&&0<=h);break}}}finally{se=!1,Error.prepareStackTrace=n}return(e=e?e.displayName||e.name:"")?M(e):""}function ue(e){switch(e.tag){case 5:return M(e.type);case 16:return M("Lazy");case 13:return M("Suspense");case 19:return M("SuspenseList");case 0:case 2:case 15:return e=ie(e.type,!1),e;case 11:return e=ie(e.type.render,!1),e;case 1:return e=ie(e.type,!0),e;default:return""}}function de(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case O:return"Fragment";case z:return"Portal";case ge:return"Profiler";case ce:return"StrictMode";case ne:return"Suspense";case Pe:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case Ce:return(e.displayName||"Context")+".Consumer";case Fe:return(e._context.displayName||"Context")+".Provider";case _e:var t=e.render;return e=e.displayName,e||(e=t.displayName||t.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case He:return t=e.displayName||null,t!==null?t:de(e.type)||"Memo";case ze:t=e._payload,e=e._init;try{return de(e(t))}catch{}}return null}function ve(e){var t=e.type;switch(e.tag){case 24:return"Cache";case 9:return(t.displayName||"Context")+".Consumer";case 10:return(t._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=t.render,e=e.displayName||e.name||"",t.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return t;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return de(t);case 8:return t===ce?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof t=="function")return t.displayName||t.name||null;if(typeof t=="string")return t}return null}function pe(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function we(e){var t=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(t==="checkbox"||t==="radio")}function ot(e){var t=we(e)?"checked":"value",n=Object.getOwnPropertyDescriptor(e.constructor.prototype,t),s=""+e[t];if(!e.hasOwnProperty(t)&&typeof n<"u"&&typeof n.get=="function"&&typeof n.set=="function"){var a=n.get,o=n.set;return Object.defineProperty(e,t,{configurable:!0,get:function(){return a.call(this)},set:function(u){s=""+u,o.call(this,u)}}),Object.defineProperty(e,t,{enumerable:n.enumerable}),{getValue:function(){return s},setValue:function(u){s=""+u},stopTracking:function(){e._valueTracker=null,delete e[t]}}}}function Fr(e){e._valueTracker||(e._valueTracker=ot(e))}function jo(e){if(!e)return!1;var t=e._valueTracker;if(!t)return!0;var n=t.getValue(),s="";return e&&(s=we(e)?e.checked?"true":"false":e.value),e=s,e!==n?(t.setValue(e),!0):!1}function zr(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function ca(e,t){var n=t.checked;return H({},t,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:n??e._wrapperState.initialChecked})}function So(e,t){var n=t.defaultValue==null?"":t.defaultValue,s=t.checked!=null?t.checked:t.defaultChecked;n=pe(t.value!=null?t.value:n),e._wrapperState={initialChecked:s,initialValue:n,controlled:t.type==="checkbox"||t.type==="radio"?t.checked!=null:t.value!=null}}function No(e,t){t=t.checked,t!=null&&V(e,"checked",t,!1)}function ua(e,t){No(e,t);var n=pe(t.value),s=t.type;if(n!=null)s==="number"?(n===0&&e.value===""||e.value!=n)&&(e.value=""+n):e.value!==""+n&&(e.value=""+n);else if(s==="submit"||s==="reset"){e.removeAttribute("value");return}t.hasOwnProperty("value")?da(e,t.type,n):t.hasOwnProperty("defaultValue")&&da(e,t.type,pe(t.defaultValue)),t.checked==null&&t.defaultChecked!=null&&(e.defaultChecked=!!t.defaultChecked)}function Co(e,t,n){if(t.hasOwnProperty("value")||t.hasOwnProperty("defaultValue")){var s=t.type;if(!(s!=="submit"&&s!=="reset"||t.value!==void 0&&t.value!==null))return;t=""+e._wrapperState.initialValue,n||t===e.value||(e.value=t),e.defaultValue=t}n=e.name,n!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,n!==""&&(e.name=n)}function da(e,t,n){(t!=="number"||zr(e.ownerDocument)!==e)&&(n==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+n&&(e.defaultValue=""+n))}var Yn=Array.isArray;function Nn(e,t,n,s){if(e=e.options,t){t={};for(var a=0;a<n.length;a++)t["$"+n[a]]=!0;for(n=0;n<e.length;n++)a=t.hasOwnProperty("$"+e[n].value),e[n].selected!==a&&(e[n].selected=a),a&&s&&(e[n].defaultSelected=!0)}else{for(n=""+pe(n),t=null,a=0;a<e.length;a++){if(e[a].value===n){e[a].selected=!0,s&&(e[a].defaultSelected=!0);return}t!==null||e[a].disabled||(t=e[a])}t!==null&&(t.selected=!0)}}function ma(e,t){if(t.dangerouslySetInnerHTML!=null)throw Error(c(91));return H({},t,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function _o(e,t){var n=t.value;if(n==null){if(n=t.children,t=t.defaultValue,n!=null){if(t!=null)throw Error(c(92));if(Yn(n)){if(1<n.length)throw Error(c(93));n=n[0]}t=n}t==null&&(t=""),n=t}e._wrapperState={initialValue:pe(n)}}function To(e,t){var n=pe(t.value),s=pe(t.defaultValue);n!=null&&(n=""+n,n!==e.value&&(e.value=n),t.defaultValue==null&&e.defaultValue!==n&&(e.defaultValue=n)),s!=null&&(e.defaultValue=""+s)}function Eo(e){var t=e.textContent;t===e._wrapperState.initialValue&&t!==""&&t!==null&&(e.value=t)}function Mo(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function ha(e,t){return e==null||e==="http://www.w3.org/1999/xhtml"?Mo(t):e==="http://www.w3.org/2000/svg"&&t==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var Br,Po=(function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(t,n,s,a){MSApp.execUnsafeLocalFunction(function(){return e(t,n,s,a)})}:e})(function(e,t){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=t;else{for(Br=Br||document.createElement("div"),Br.innerHTML="<svg>"+t.valueOf().toString()+"</svg>",t=Br.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;t.firstChild;)e.appendChild(t.firstChild)}});function Jn(e,t){if(t){var n=e.firstChild;if(n&&n===e.lastChild&&n.nodeType===3){n.nodeValue=t;return}}e.textContent=t}var Zn={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},id=["Webkit","ms","Moz","O"];Object.keys(Zn).forEach(function(e){id.forEach(function(t){t=t+e.charAt(0).toUpperCase()+e.substring(1),Zn[t]=Zn[e]})});function Lo(e,t,n){return t==null||typeof t=="boolean"||t===""?"":n||typeof t!="number"||t===0||Zn.hasOwnProperty(e)&&Zn[e]?(""+t).trim():t+"px"}function Ro(e,t){e=e.style;for(var n in t)if(t.hasOwnProperty(n)){var s=n.indexOf("--")===0,a=Lo(n,t[n],s);n==="float"&&(n="cssFloat"),s?e.setProperty(n,a):e[n]=a}}var od=H({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function pa(e,t){if(t){if(od[e]&&(t.children!=null||t.dangerouslySetInnerHTML!=null))throw Error(c(137,e));if(t.dangerouslySetInnerHTML!=null){if(t.children!=null)throw Error(c(60));if(typeof t.dangerouslySetInnerHTML!="object"||!("__html"in t.dangerouslySetInnerHTML))throw Error(c(61))}if(t.style!=null&&typeof t.style!="object")throw Error(c(62))}}function fa(e,t){if(e.indexOf("-")===-1)return typeof t.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var ga=null;function va(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var ya=null,Cn=null,_n=null;function Ao(e){if(e=wr(e)){if(typeof ya!="function")throw Error(c(280));var t=e.stateNode;t&&(t=ls(t),ya(e.stateNode,e.type,t))}}function Do(e){Cn?_n?_n.push(e):_n=[e]:Cn=e}function Io(){if(Cn){var e=Cn,t=_n;if(_n=Cn=null,Ao(e),t)for(e=0;e<t.length;e++)Ao(t[e])}}function Fo(e,t){return e(t)}function zo(){}var xa=!1;function Bo(e,t,n){if(xa)return e(t,n);xa=!0;try{return Fo(e,t,n)}finally{xa=!1,(Cn!==null||_n!==null)&&(zo(),Io())}}function er(e,t){var n=e.stateNode;if(n===null)return null;var s=ls(n);if(s===null)return null;n=s[t];e:switch(t){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(s=!s.disabled)||(e=e.type,s=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!s;break e;default:e=!1}if(e)return null;if(n&&typeof n!="function")throw Error(c(231,t,typeof n));return n}var ka=!1;if(T)try{var tr={};Object.defineProperty(tr,"passive",{get:function(){ka=!0}}),window.addEventListener("test",tr,tr),window.removeEventListener("test",tr,tr)}catch{ka=!1}function ld(e,t,n,s,a,o,u,h,f){var b=Array.prototype.slice.call(arguments,3);try{t.apply(n,b)}catch(P){this.onError(P)}}var nr=!1,Or=null,Wr=!1,wa=null,cd={onError:function(e){nr=!0,Or=e}};function ud(e,t,n,s,a,o,u,h,f){nr=!1,Or=null,ld.apply(cd,arguments)}function dd(e,t,n,s,a,o,u,h,f){if(ud.apply(this,arguments),nr){if(nr){var b=Or;nr=!1,Or=null}else throw Error(c(198));Wr||(Wr=!0,wa=b)}}function ln(e){var t=e,n=e;if(e.alternate)for(;t.return;)t=t.return;else{e=t;do t=e,(t.flags&4098)!==0&&(n=t.return),e=t.return;while(e)}return t.tag===3?n:null}function Oo(e){if(e.tag===13){var t=e.memoizedState;if(t===null&&(e=e.alternate,e!==null&&(t=e.memoizedState)),t!==null)return t.dehydrated}return null}function Wo(e){if(ln(e)!==e)throw Error(c(188))}function md(e){var t=e.alternate;if(!t){if(t=ln(e),t===null)throw Error(c(188));return t!==e?null:e}for(var n=e,s=t;;){var a=n.return;if(a===null)break;var o=a.alternate;if(o===null){if(s=a.return,s!==null){n=s;continue}break}if(a.child===o.child){for(o=a.child;o;){if(o===n)return Wo(a),e;if(o===s)return Wo(a),t;o=o.sibling}throw Error(c(188))}if(n.return!==s.return)n=a,s=o;else{for(var u=!1,h=a.child;h;){if(h===n){u=!0,n=a,s=o;break}if(h===s){u=!0,s=a,n=o;break}h=h.sibling}if(!u){for(h=o.child;h;){if(h===n){u=!0,n=o,s=a;break}if(h===s){u=!0,s=o,n=a;break}h=h.sibling}if(!u)throw Error(c(189))}}if(n.alternate!==s)throw Error(c(190))}if(n.tag!==3)throw Error(c(188));return n.stateNode.current===n?e:t}function Uo(e){return e=md(e),e!==null?$o(e):null}function $o(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var t=$o(e);if(t!==null)return t;e=e.sibling}return null}var Vo=l.unstable_scheduleCallback,Ho=l.unstable_cancelCallback,hd=l.unstable_shouldYield,pd=l.unstable_requestPaint,Te=l.unstable_now,fd=l.unstable_getCurrentPriorityLevel,ba=l.unstable_ImmediatePriority,Go=l.unstable_UserBlockingPriority,Ur=l.unstable_NormalPriority,gd=l.unstable_LowPriority,Ko=l.unstable_IdlePriority,$r=null,Ct=null;function vd(e){if(Ct&&typeof Ct.onCommitFiberRoot=="function")try{Ct.onCommitFiberRoot($r,e,void 0,(e.current.flags&128)===128)}catch{}}var yt=Math.clz32?Math.clz32:kd,yd=Math.log,xd=Math.LN2;function kd(e){return e>>>=0,e===0?32:31-(yd(e)/xd|0)|0}var Vr=64,Hr=4194304;function rr(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function Gr(e,t){var n=e.pendingLanes;if(n===0)return 0;var s=0,a=e.suspendedLanes,o=e.pingedLanes,u=n&268435455;if(u!==0){var h=u&~a;h!==0?s=rr(h):(o&=u,o!==0&&(s=rr(o)))}else u=n&~a,u!==0?s=rr(u):o!==0&&(s=rr(o));if(s===0)return 0;if(t!==0&&t!==s&&(t&a)===0&&(a=s&-s,o=t&-t,a>=o||a===16&&(o&4194240)!==0))return t;if((s&4)!==0&&(s|=n&16),t=e.entangledLanes,t!==0)for(e=e.entanglements,t&=s;0<t;)n=31-yt(t),a=1<<n,s|=e[n],t&=~a;return s}function wd(e,t){switch(e){case 1:case 2:case 4:return t+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return t+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function bd(e,t){for(var n=e.suspendedLanes,s=e.pingedLanes,a=e.expirationTimes,o=e.pendingLanes;0<o;){var u=31-yt(o),h=1<<u,f=a[u];f===-1?((h&n)===0||(h&s)!==0)&&(a[u]=wd(h,t)):f<=t&&(e.expiredLanes|=h),o&=~h}}function ja(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function qo(){var e=Vr;return Vr<<=1,(Vr&4194240)===0&&(Vr=64),e}function Sa(e){for(var t=[],n=0;31>n;n++)t.push(e);return t}function sr(e,t,n){e.pendingLanes|=t,t!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,t=31-yt(t),e[t]=n}function jd(e,t){var n=e.pendingLanes&~t;e.pendingLanes=t,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=t,e.mutableReadLanes&=t,e.entangledLanes&=t,t=e.entanglements;var s=e.eventTimes;for(e=e.expirationTimes;0<n;){var a=31-yt(n),o=1<<a;t[a]=0,s[a]=-1,e[a]=-1,n&=~o}}function Na(e,t){var n=e.entangledLanes|=t;for(e=e.entanglements;n;){var s=31-yt(n),a=1<<s;a&t|e[s]&t&&(e[s]|=t),n&=~a}}var fe=0;function Qo(e){return e&=-e,1<e?4<e?(e&268435455)!==0?16:536870912:4:1}var Xo,Ca,Yo,Jo,Zo,_a=!1,Kr=[],Ot=null,Wt=null,Ut=null,ar=new Map,ir=new Map,$t=[],Sd="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function el(e,t){switch(e){case"focusin":case"focusout":Ot=null;break;case"dragenter":case"dragleave":Wt=null;break;case"mouseover":case"mouseout":Ut=null;break;case"pointerover":case"pointerout":ar.delete(t.pointerId);break;case"gotpointercapture":case"lostpointercapture":ir.delete(t.pointerId)}}function or(e,t,n,s,a,o){return e===null||e.nativeEvent!==o?(e={blockedOn:t,domEventName:n,eventSystemFlags:s,nativeEvent:o,targetContainers:[a]},t!==null&&(t=wr(t),t!==null&&Ca(t)),e):(e.eventSystemFlags|=s,t=e.targetContainers,a!==null&&t.indexOf(a)===-1&&t.push(a),e)}function Nd(e,t,n,s,a){switch(t){case"focusin":return Ot=or(Ot,e,t,n,s,a),!0;case"dragenter":return Wt=or(Wt,e,t,n,s,a),!0;case"mouseover":return Ut=or(Ut,e,t,n,s,a),!0;case"pointerover":var o=a.pointerId;return ar.set(o,or(ar.get(o)||null,e,t,n,s,a)),!0;case"gotpointercapture":return o=a.pointerId,ir.set(o,or(ir.get(o)||null,e,t,n,s,a)),!0}return!1}function tl(e){var t=cn(e.target);if(t!==null){var n=ln(t);if(n!==null){if(t=n.tag,t===13){if(t=Oo(n),t!==null){e.blockedOn=t,Zo(e.priority,function(){Yo(n)});return}}else if(t===3&&n.stateNode.current.memoizedState.isDehydrated){e.blockedOn=n.tag===3?n.stateNode.containerInfo:null;return}}}e.blockedOn=null}function qr(e){if(e.blockedOn!==null)return!1;for(var t=e.targetContainers;0<t.length;){var n=Ea(e.domEventName,e.eventSystemFlags,t[0],e.nativeEvent);if(n===null){n=e.nativeEvent;var s=new n.constructor(n.type,n);ga=s,n.target.dispatchEvent(s),ga=null}else return t=wr(n),t!==null&&Ca(t),e.blockedOn=n,!1;t.shift()}return!0}function nl(e,t,n){qr(e)&&n.delete(t)}function Cd(){_a=!1,Ot!==null&&qr(Ot)&&(Ot=null),Wt!==null&&qr(Wt)&&(Wt=null),Ut!==null&&qr(Ut)&&(Ut=null),ar.forEach(nl),ir.forEach(nl)}function lr(e,t){e.blockedOn===t&&(e.blockedOn=null,_a||(_a=!0,l.unstable_scheduleCallback(l.unstable_NormalPriority,Cd)))}function cr(e){function t(a){return lr(a,e)}if(0<Kr.length){lr(Kr[0],e);for(var n=1;n<Kr.length;n++){var s=Kr[n];s.blockedOn===e&&(s.blockedOn=null)}}for(Ot!==null&&lr(Ot,e),Wt!==null&&lr(Wt,e),Ut!==null&&lr(Ut,e),ar.forEach(t),ir.forEach(t),n=0;n<$t.length;n++)s=$t[n],s.blockedOn===e&&(s.blockedOn=null);for(;0<$t.length&&(n=$t[0],n.blockedOn===null);)tl(n),n.blockedOn===null&&$t.shift()}var Tn=ee.ReactCurrentBatchConfig,Qr=!0;function _d(e,t,n,s){var a=fe,o=Tn.transition;Tn.transition=null;try{fe=1,Ta(e,t,n,s)}finally{fe=a,Tn.transition=o}}function Td(e,t,n,s){var a=fe,o=Tn.transition;Tn.transition=null;try{fe=4,Ta(e,t,n,s)}finally{fe=a,Tn.transition=o}}function Ta(e,t,n,s){if(Qr){var a=Ea(e,t,n,s);if(a===null)Ga(e,t,s,Xr,n),el(e,s);else if(Nd(a,e,t,n,s))s.stopPropagation();else if(el(e,s),t&4&&-1<Sd.indexOf(e)){for(;a!==null;){var o=wr(a);if(o!==null&&Xo(o),o=Ea(e,t,n,s),o===null&&Ga(e,t,s,Xr,n),o===a)break;a=o}a!==null&&s.stopPropagation()}else Ga(e,t,s,null,n)}}var Xr=null;function Ea(e,t,n,s){if(Xr=null,e=va(s),e=cn(e),e!==null)if(t=ln(e),t===null)e=null;else if(n=t.tag,n===13){if(e=Oo(t),e!==null)return e;e=null}else if(n===3){if(t.stateNode.current.memoizedState.isDehydrated)return t.tag===3?t.stateNode.containerInfo:null;e=null}else t!==e&&(e=null);return Xr=e,null}function rl(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(fd()){case ba:return 1;case Go:return 4;case Ur:case gd:return 16;case Ko:return 536870912;default:return 16}default:return 16}}var Vt=null,Ma=null,Yr=null;function sl(){if(Yr)return Yr;var e,t=Ma,n=t.length,s,a="value"in Vt?Vt.value:Vt.textContent,o=a.length;for(e=0;e<n&&t[e]===a[e];e++);var u=n-e;for(s=1;s<=u&&t[n-s]===a[o-s];s++);return Yr=a.slice(e,1<s?1-s:void 0)}function Jr(e){var t=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&t===13&&(e=13)):e=t,e===10&&(e=13),32<=e||e===13?e:0}function Zr(){return!0}function al(){return!1}function lt(e){function t(n,s,a,o,u){this._reactName=n,this._targetInst=a,this.type=s,this.nativeEvent=o,this.target=u,this.currentTarget=null;for(var h in e)e.hasOwnProperty(h)&&(n=e[h],this[h]=n?n(o):o[h]);return this.isDefaultPrevented=(o.defaultPrevented!=null?o.defaultPrevented:o.returnValue===!1)?Zr:al,this.isPropagationStopped=al,this}return H(t.prototype,{preventDefault:function(){this.defaultPrevented=!0;var n=this.nativeEvent;n&&(n.preventDefault?n.preventDefault():typeof n.returnValue!="unknown"&&(n.returnValue=!1),this.isDefaultPrevented=Zr)},stopPropagation:function(){var n=this.nativeEvent;n&&(n.stopPropagation?n.stopPropagation():typeof n.cancelBubble!="unknown"&&(n.cancelBubble=!0),this.isPropagationStopped=Zr)},persist:function(){},isPersistent:Zr}),t}var En={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},Pa=lt(En),ur=H({},En,{view:0,detail:0}),Ed=lt(ur),La,Ra,dr,es=H({},ur,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:Da,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==dr&&(dr&&e.type==="mousemove"?(La=e.screenX-dr.screenX,Ra=e.screenY-dr.screenY):Ra=La=0,dr=e),La)},movementY:function(e){return"movementY"in e?e.movementY:Ra}}),il=lt(es),Md=H({},es,{dataTransfer:0}),Pd=lt(Md),Ld=H({},ur,{relatedTarget:0}),Aa=lt(Ld),Rd=H({},En,{animationName:0,elapsedTime:0,pseudoElement:0}),Ad=lt(Rd),Dd=H({},En,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),Id=lt(Dd),Fd=H({},En,{data:0}),ol=lt(Fd),zd={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},Bd={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},Od={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function Wd(e){var t=this.nativeEvent;return t.getModifierState?t.getModifierState(e):(e=Od[e])?!!t[e]:!1}function Da(){return Wd}var Ud=H({},ur,{key:function(e){if(e.key){var t=zd[e.key]||e.key;if(t!=="Unidentified")return t}return e.type==="keypress"?(e=Jr(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?Bd[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:Da,charCode:function(e){return e.type==="keypress"?Jr(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?Jr(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),$d=lt(Ud),Vd=H({},es,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),ll=lt(Vd),Hd=H({},ur,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:Da}),Gd=lt(Hd),Kd=H({},En,{propertyName:0,elapsedTime:0,pseudoElement:0}),qd=lt(Kd),Qd=H({},es,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),Xd=lt(Qd),Yd=[9,13,27,32],Ia=T&&"CompositionEvent"in window,mr=null;T&&"documentMode"in document&&(mr=document.documentMode);var Jd=T&&"TextEvent"in window&&!mr,cl=T&&(!Ia||mr&&8<mr&&11>=mr),ul=" ",dl=!1;function ml(e,t){switch(e){case"keyup":return Yd.indexOf(t.keyCode)!==-1;case"keydown":return t.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function hl(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var Mn=!1;function Zd(e,t){switch(e){case"compositionend":return hl(t);case"keypress":return t.which!==32?null:(dl=!0,ul);case"textInput":return e=t.data,e===ul&&dl?null:e;default:return null}}function em(e,t){if(Mn)return e==="compositionend"||!Ia&&ml(e,t)?(e=sl(),Yr=Ma=Vt=null,Mn=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(t.ctrlKey||t.altKey||t.metaKey)||t.ctrlKey&&t.altKey){if(t.char&&1<t.char.length)return t.char;if(t.which)return String.fromCharCode(t.which)}return null;case"compositionend":return cl&&t.locale!=="ko"?null:t.data;default:return null}}var tm={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function pl(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t==="input"?!!tm[e.type]:t==="textarea"}function fl(e,t,n,s){Do(s),t=as(t,"onChange"),0<t.length&&(n=new Pa("onChange","change",null,n,s),e.push({event:n,listeners:t}))}var hr=null,pr=null;function nm(e){Rl(e,0)}function ts(e){var t=Dn(e);if(jo(t))return e}function rm(e,t){if(e==="change")return t}var gl=!1;if(T){var Fa;if(T){var za="oninput"in document;if(!za){var vl=document.createElement("div");vl.setAttribute("oninput","return;"),za=typeof vl.oninput=="function"}Fa=za}else Fa=!1;gl=Fa&&(!document.documentMode||9<document.documentMode)}function yl(){hr&&(hr.detachEvent("onpropertychange",xl),pr=hr=null)}function xl(e){if(e.propertyName==="value"&&ts(pr)){var t=[];fl(t,pr,e,va(e)),Bo(nm,t)}}function sm(e,t,n){e==="focusin"?(yl(),hr=t,pr=n,hr.attachEvent("onpropertychange",xl)):e==="focusout"&&yl()}function am(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return ts(pr)}function im(e,t){if(e==="click")return ts(t)}function om(e,t){if(e==="input"||e==="change")return ts(t)}function lm(e,t){return e===t&&(e!==0||1/e===1/t)||e!==e&&t!==t}var xt=typeof Object.is=="function"?Object.is:lm;function fr(e,t){if(xt(e,t))return!0;if(typeof e!="object"||e===null||typeof t!="object"||t===null)return!1;var n=Object.keys(e),s=Object.keys(t);if(n.length!==s.length)return!1;for(s=0;s<n.length;s++){var a=n[s];if(!k.call(t,a)||!xt(e[a],t[a]))return!1}return!0}function kl(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function wl(e,t){var n=kl(e);e=0;for(var s;n;){if(n.nodeType===3){if(s=e+n.textContent.length,e<=t&&s>=t)return{node:n,offset:t-e};e=s}e:{for(;n;){if(n.nextSibling){n=n.nextSibling;break e}n=n.parentNode}n=void 0}n=kl(n)}}function bl(e,t){return e&&t?e===t?!0:e&&e.nodeType===3?!1:t&&t.nodeType===3?bl(e,t.parentNode):"contains"in e?e.contains(t):e.compareDocumentPosition?!!(e.compareDocumentPosition(t)&16):!1:!1}function jl(){for(var e=window,t=zr();t instanceof e.HTMLIFrameElement;){try{var n=typeof t.contentWindow.location.href=="string"}catch{n=!1}if(n)e=t.contentWindow;else break;t=zr(e.document)}return t}function Ba(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t&&(t==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||t==="textarea"||e.contentEditable==="true")}function cm(e){var t=jl(),n=e.focusedElem,s=e.selectionRange;if(t!==n&&n&&n.ownerDocument&&bl(n.ownerDocument.documentElement,n)){if(s!==null&&Ba(n)){if(t=s.start,e=s.end,e===void 0&&(e=t),"selectionStart"in n)n.selectionStart=t,n.selectionEnd=Math.min(e,n.value.length);else if(e=(t=n.ownerDocument||document)&&t.defaultView||window,e.getSelection){e=e.getSelection();var a=n.textContent.length,o=Math.min(s.start,a);s=s.end===void 0?o:Math.min(s.end,a),!e.extend&&o>s&&(a=s,s=o,o=a),a=wl(n,o);var u=wl(n,s);a&&u&&(e.rangeCount!==1||e.anchorNode!==a.node||e.anchorOffset!==a.offset||e.focusNode!==u.node||e.focusOffset!==u.offset)&&(t=t.createRange(),t.setStart(a.node,a.offset),e.removeAllRanges(),o>s?(e.addRange(t),e.extend(u.node,u.offset)):(t.setEnd(u.node,u.offset),e.addRange(t)))}}for(t=[],e=n;e=e.parentNode;)e.nodeType===1&&t.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof n.focus=="function"&&n.focus(),n=0;n<t.length;n++)e=t[n],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var um=T&&"documentMode"in document&&11>=document.documentMode,Pn=null,Oa=null,gr=null,Wa=!1;function Sl(e,t,n){var s=n.window===n?n.document:n.nodeType===9?n:n.ownerDocument;Wa||Pn==null||Pn!==zr(s)||(s=Pn,"selectionStart"in s&&Ba(s)?s={start:s.selectionStart,end:s.selectionEnd}:(s=(s.ownerDocument&&s.ownerDocument.defaultView||window).getSelection(),s={anchorNode:s.anchorNode,anchorOffset:s.anchorOffset,focusNode:s.focusNode,focusOffset:s.focusOffset}),gr&&fr(gr,s)||(gr=s,s=as(Oa,"onSelect"),0<s.length&&(t=new Pa("onSelect","select",null,t,n),e.push({event:t,listeners:s}),t.target=Pn)))}function ns(e,t){var n={};return n[e.toLowerCase()]=t.toLowerCase(),n["Webkit"+e]="webkit"+t,n["Moz"+e]="moz"+t,n}var Ln={animationend:ns("Animation","AnimationEnd"),animationiteration:ns("Animation","AnimationIteration"),animationstart:ns("Animation","AnimationStart"),transitionend:ns("Transition","TransitionEnd")},Ua={},Nl={};T&&(Nl=document.createElement("div").style,"AnimationEvent"in window||(delete Ln.animationend.animation,delete Ln.animationiteration.animation,delete Ln.animationstart.animation),"TransitionEvent"in window||delete Ln.transitionend.transition);function rs(e){if(Ua[e])return Ua[e];if(!Ln[e])return e;var t=Ln[e],n;for(n in t)if(t.hasOwnProperty(n)&&n in Nl)return Ua[e]=t[n];return e}var Cl=rs("animationend"),_l=rs("animationiteration"),Tl=rs("animationstart"),El=rs("transitionend"),Ml=new Map,Pl="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function Ht(e,t){Ml.set(e,t),p(t,[e])}for(var $a=0;$a<Pl.length;$a++){var Va=Pl[$a],dm=Va.toLowerCase(),mm=Va[0].toUpperCase()+Va.slice(1);Ht(dm,"on"+mm)}Ht(Cl,"onAnimationEnd"),Ht(_l,"onAnimationIteration"),Ht(Tl,"onAnimationStart"),Ht("dblclick","onDoubleClick"),Ht("focusin","onFocus"),Ht("focusout","onBlur"),Ht(El,"onTransitionEnd"),g("onMouseEnter",["mouseout","mouseover"]),g("onMouseLeave",["mouseout","mouseover"]),g("onPointerEnter",["pointerout","pointerover"]),g("onPointerLeave",["pointerout","pointerover"]),p("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),p("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),p("onBeforeInput",["compositionend","keypress","textInput","paste"]),p("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),p("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),p("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var vr="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),hm=new Set("cancel close invalid load scroll toggle".split(" ").concat(vr));function Ll(e,t,n){var s=e.type||"unknown-event";e.currentTarget=n,dd(s,t,void 0,e),e.currentTarget=null}function Rl(e,t){t=(t&4)!==0;for(var n=0;n<e.length;n++){var s=e[n],a=s.event;s=s.listeners;e:{var o=void 0;if(t)for(var u=s.length-1;0<=u;u--){var h=s[u],f=h.instance,b=h.currentTarget;if(h=h.listener,f!==o&&a.isPropagationStopped())break e;Ll(a,h,b),o=f}else for(u=0;u<s.length;u++){if(h=s[u],f=h.instance,b=h.currentTarget,h=h.listener,f!==o&&a.isPropagationStopped())break e;Ll(a,h,b),o=f}}}if(Wr)throw e=wa,Wr=!1,wa=null,e}function xe(e,t){var n=t[Ja];n===void 0&&(n=t[Ja]=new Set);var s=e+"__bubble";n.has(s)||(Al(t,e,2,!1),n.add(s))}function Ha(e,t,n){var s=0;t&&(s|=4),Al(n,e,s,t)}var ss="_reactListening"+Math.random().toString(36).slice(2);function yr(e){if(!e[ss]){e[ss]=!0,d.forEach(function(n){n!=="selectionchange"&&(hm.has(n)||Ha(n,!1,e),Ha(n,!0,e))});var t=e.nodeType===9?e:e.ownerDocument;t===null||t[ss]||(t[ss]=!0,Ha("selectionchange",!1,t))}}function Al(e,t,n,s){switch(rl(t)){case 1:var a=_d;break;case 4:a=Td;break;default:a=Ta}n=a.bind(null,t,n,e),a=void 0,!ka||t!=="touchstart"&&t!=="touchmove"&&t!=="wheel"||(a=!0),s?a!==void 0?e.addEventListener(t,n,{capture:!0,passive:a}):e.addEventListener(t,n,!0):a!==void 0?e.addEventListener(t,n,{passive:a}):e.addEventListener(t,n,!1)}function Ga(e,t,n,s,a){var o=s;if((t&1)===0&&(t&2)===0&&s!==null)e:for(;;){if(s===null)return;var u=s.tag;if(u===3||u===4){var h=s.stateNode.containerInfo;if(h===a||h.nodeType===8&&h.parentNode===a)break;if(u===4)for(u=s.return;u!==null;){var f=u.tag;if((f===3||f===4)&&(f=u.stateNode.containerInfo,f===a||f.nodeType===8&&f.parentNode===a))return;u=u.return}for(;h!==null;){if(u=cn(h),u===null)return;if(f=u.tag,f===5||f===6){s=o=u;continue e}h=h.parentNode}}s=s.return}Bo(function(){var b=o,P=va(n),R=[];e:{var E=Ml.get(e);if(E!==void 0){var U=Pa,G=e;switch(e){case"keypress":if(Jr(n)===0)break e;case"keydown":case"keyup":U=$d;break;case"focusin":G="focus",U=Aa;break;case"focusout":G="blur",U=Aa;break;case"beforeblur":case"afterblur":U=Aa;break;case"click":if(n.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":U=il;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":U=Pd;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":U=Gd;break;case Cl:case _l:case Tl:U=Ad;break;case El:U=qd;break;case"scroll":U=Ed;break;case"wheel":U=Xd;break;case"copy":case"cut":case"paste":U=Id;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":U=ll}var K=(t&4)!==0,Ee=!K&&e==="scroll",x=K?E!==null?E+"Capture":null:E;K=[];for(var v=b,w;v!==null;){w=v;var F=w.stateNode;if(w.tag===5&&F!==null&&(w=F,x!==null&&(F=er(v,x),F!=null&&K.push(xr(v,F,w)))),Ee)break;v=v.return}0<K.length&&(E=new U(E,G,null,n,P),R.push({event:E,listeners:K}))}}if((t&7)===0){e:{if(E=e==="mouseover"||e==="pointerover",U=e==="mouseout"||e==="pointerout",E&&n!==ga&&(G=n.relatedTarget||n.fromElement)&&(cn(G)||G[Lt]))break e;if((U||E)&&(E=P.window===P?P:(E=P.ownerDocument)?E.defaultView||E.parentWindow:window,U?(G=n.relatedTarget||n.toElement,U=b,G=G?cn(G):null,G!==null&&(Ee=ln(G),G!==Ee||G.tag!==5&&G.tag!==6)&&(G=null)):(U=null,G=b),U!==G)){if(K=il,F="onMouseLeave",x="onMouseEnter",v="mouse",(e==="pointerout"||e==="pointerover")&&(K=ll,F="onPointerLeave",x="onPointerEnter",v="pointer"),Ee=U==null?E:Dn(U),w=G==null?E:Dn(G),E=new K(F,v+"leave",U,n,P),E.target=Ee,E.relatedTarget=w,F=null,cn(P)===b&&(K=new K(x,v+"enter",G,n,P),K.target=w,K.relatedTarget=Ee,F=K),Ee=F,U&&G)t:{for(K=U,x=G,v=0,w=K;w;w=Rn(w))v++;for(w=0,F=x;F;F=Rn(F))w++;for(;0<v-w;)K=Rn(K),v--;for(;0<w-v;)x=Rn(x),w--;for(;v--;){if(K===x||x!==null&&K===x.alternate)break t;K=Rn(K),x=Rn(x)}K=null}else K=null;U!==null&&Dl(R,E,U,K,!1),G!==null&&Ee!==null&&Dl(R,Ee,G,K,!0)}}e:{if(E=b?Dn(b):window,U=E.nodeName&&E.nodeName.toLowerCase(),U==="select"||U==="input"&&E.type==="file")var Q=rm;else if(pl(E))if(gl)Q=om;else{Q=am;var X=sm}else(U=E.nodeName)&&U.toLowerCase()==="input"&&(E.type==="checkbox"||E.type==="radio")&&(Q=im);if(Q&&(Q=Q(e,b))){fl(R,Q,n,P);break e}X&&X(e,E,b),e==="focusout"&&(X=E._wrapperState)&&X.controlled&&E.type==="number"&&da(E,"number",E.value)}switch(X=b?Dn(b):window,e){case"focusin":(pl(X)||X.contentEditable==="true")&&(Pn=X,Oa=b,gr=null);break;case"focusout":gr=Oa=Pn=null;break;case"mousedown":Wa=!0;break;case"contextmenu":case"mouseup":case"dragend":Wa=!1,Sl(R,n,P);break;case"selectionchange":if(um)break;case"keydown":case"keyup":Sl(R,n,P)}var Y;if(Ia)e:{switch(e){case"compositionstart":var te="onCompositionStart";break e;case"compositionend":te="onCompositionEnd";break e;case"compositionupdate":te="onCompositionUpdate";break e}te=void 0}else Mn?ml(e,n)&&(te="onCompositionEnd"):e==="keydown"&&n.keyCode===229&&(te="onCompositionStart");te&&(cl&&n.locale!=="ko"&&(Mn||te!=="onCompositionStart"?te==="onCompositionEnd"&&Mn&&(Y=sl()):(Vt=P,Ma="value"in Vt?Vt.value:Vt.textContent,Mn=!0)),X=as(b,te),0<X.length&&(te=new ol(te,e,null,n,P),R.push({event:te,listeners:X}),Y?te.data=Y:(Y=hl(n),Y!==null&&(te.data=Y)))),(Y=Jd?Zd(e,n):em(e,n))&&(b=as(b,"onBeforeInput"),0<b.length&&(P=new ol("onBeforeInput","beforeinput",null,n,P),R.push({event:P,listeners:b}),P.data=Y))}Rl(R,t)})}function xr(e,t,n){return{instance:e,listener:t,currentTarget:n}}function as(e,t){for(var n=t+"Capture",s=[];e!==null;){var a=e,o=a.stateNode;a.tag===5&&o!==null&&(a=o,o=er(e,n),o!=null&&s.unshift(xr(e,o,a)),o=er(e,t),o!=null&&s.push(xr(e,o,a))),e=e.return}return s}function Rn(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function Dl(e,t,n,s,a){for(var o=t._reactName,u=[];n!==null&&n!==s;){var h=n,f=h.alternate,b=h.stateNode;if(f!==null&&f===s)break;h.tag===5&&b!==null&&(h=b,a?(f=er(n,o),f!=null&&u.unshift(xr(n,f,h))):a||(f=er(n,o),f!=null&&u.push(xr(n,f,h)))),n=n.return}u.length!==0&&e.push({event:t,listeners:u})}var pm=/\r\n?/g,fm=/\u0000|\uFFFD/g;function Il(e){return(typeof e=="string"?e:""+e).replace(pm,`
`).replace(fm,"")}function is(e,t,n){if(t=Il(t),Il(e)!==t&&n)throw Error(c(425))}function os(){}var Ka=null,qa=null;function Qa(e,t){return e==="textarea"||e==="noscript"||typeof t.children=="string"||typeof t.children=="number"||typeof t.dangerouslySetInnerHTML=="object"&&t.dangerouslySetInnerHTML!==null&&t.dangerouslySetInnerHTML.__html!=null}var Xa=typeof setTimeout=="function"?setTimeout:void 0,gm=typeof clearTimeout=="function"?clearTimeout:void 0,Fl=typeof Promise=="function"?Promise:void 0,vm=typeof queueMicrotask=="function"?queueMicrotask:typeof Fl<"u"?function(e){return Fl.resolve(null).then(e).catch(ym)}:Xa;function ym(e){setTimeout(function(){throw e})}function Ya(e,t){var n=t,s=0;do{var a=n.nextSibling;if(e.removeChild(n),a&&a.nodeType===8)if(n=a.data,n==="/$"){if(s===0){e.removeChild(a),cr(t);return}s--}else n!=="$"&&n!=="$?"&&n!=="$!"||s++;n=a}while(n);cr(t)}function Gt(e){for(;e!=null;e=e.nextSibling){var t=e.nodeType;if(t===1||t===3)break;if(t===8){if(t=e.data,t==="$"||t==="$!"||t==="$?")break;if(t==="/$")return null}}return e}function zl(e){e=e.previousSibling;for(var t=0;e;){if(e.nodeType===8){var n=e.data;if(n==="$"||n==="$!"||n==="$?"){if(t===0)return e;t--}else n==="/$"&&t++}e=e.previousSibling}return null}var An=Math.random().toString(36).slice(2),_t="__reactFiber$"+An,kr="__reactProps$"+An,Lt="__reactContainer$"+An,Ja="__reactEvents$"+An,xm="__reactListeners$"+An,km="__reactHandles$"+An;function cn(e){var t=e[_t];if(t)return t;for(var n=e.parentNode;n;){if(t=n[Lt]||n[_t]){if(n=t.alternate,t.child!==null||n!==null&&n.child!==null)for(e=zl(e);e!==null;){if(n=e[_t])return n;e=zl(e)}return t}e=n,n=e.parentNode}return null}function wr(e){return e=e[_t]||e[Lt],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function Dn(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(c(33))}function ls(e){return e[kr]||null}var Za=[],In=-1;function Kt(e){return{current:e}}function ke(e){0>In||(e.current=Za[In],Za[In]=null,In--)}function ye(e,t){In++,Za[In]=e.current,e.current=t}var qt={},Ge=Kt(qt),Ze=Kt(!1),un=qt;function Fn(e,t){var n=e.type.contextTypes;if(!n)return qt;var s=e.stateNode;if(s&&s.__reactInternalMemoizedUnmaskedChildContext===t)return s.__reactInternalMemoizedMaskedChildContext;var a={},o;for(o in n)a[o]=t[o];return s&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=t,e.__reactInternalMemoizedMaskedChildContext=a),a}function et(e){return e=e.childContextTypes,e!=null}function cs(){ke(Ze),ke(Ge)}function Bl(e,t,n){if(Ge.current!==qt)throw Error(c(168));ye(Ge,t),ye(Ze,n)}function Ol(e,t,n){var s=e.stateNode;if(t=t.childContextTypes,typeof s.getChildContext!="function")return n;s=s.getChildContext();for(var a in s)if(!(a in t))throw Error(c(108,ve(e)||"Unknown",a));return H({},n,s)}function us(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||qt,un=Ge.current,ye(Ge,e),ye(Ze,Ze.current),!0}function Wl(e,t,n){var s=e.stateNode;if(!s)throw Error(c(169));n?(e=Ol(e,t,un),s.__reactInternalMemoizedMergedChildContext=e,ke(Ze),ke(Ge),ye(Ge,e)):ke(Ze),ye(Ze,n)}var Rt=null,ds=!1,ei=!1;function Ul(e){Rt===null?Rt=[e]:Rt.push(e)}function wm(e){ds=!0,Ul(e)}function Qt(){if(!ei&&Rt!==null){ei=!0;var e=0,t=fe;try{var n=Rt;for(fe=1;e<n.length;e++){var s=n[e];do s=s(!0);while(s!==null)}Rt=null,ds=!1}catch(a){throw Rt!==null&&(Rt=Rt.slice(e+1)),Vo(ba,Qt),a}finally{fe=t,ei=!1}}return null}var zn=[],Bn=0,ms=null,hs=0,mt=[],ht=0,dn=null,At=1,Dt="";function mn(e,t){zn[Bn++]=hs,zn[Bn++]=ms,ms=e,hs=t}function $l(e,t,n){mt[ht++]=At,mt[ht++]=Dt,mt[ht++]=dn,dn=e;var s=At;e=Dt;var a=32-yt(s)-1;s&=~(1<<a),n+=1;var o=32-yt(t)+a;if(30<o){var u=a-a%5;o=(s&(1<<u)-1).toString(32),s>>=u,a-=u,At=1<<32-yt(t)+a|n<<a|s,Dt=o+e}else At=1<<o|n<<a|s,Dt=e}function ti(e){e.return!==null&&(mn(e,1),$l(e,1,0))}function ni(e){for(;e===ms;)ms=zn[--Bn],zn[Bn]=null,hs=zn[--Bn],zn[Bn]=null;for(;e===dn;)dn=mt[--ht],mt[ht]=null,Dt=mt[--ht],mt[ht]=null,At=mt[--ht],mt[ht]=null}var ct=null,ut=null,be=!1,kt=null;function Vl(e,t){var n=vt(5,null,null,0);n.elementType="DELETED",n.stateNode=t,n.return=e,t=e.deletions,t===null?(e.deletions=[n],e.flags|=16):t.push(n)}function Hl(e,t){switch(e.tag){case 5:var n=e.type;return t=t.nodeType!==1||n.toLowerCase()!==t.nodeName.toLowerCase()?null:t,t!==null?(e.stateNode=t,ct=e,ut=Gt(t.firstChild),!0):!1;case 6:return t=e.pendingProps===""||t.nodeType!==3?null:t,t!==null?(e.stateNode=t,ct=e,ut=null,!0):!1;case 13:return t=t.nodeType!==8?null:t,t!==null?(n=dn!==null?{id:At,overflow:Dt}:null,e.memoizedState={dehydrated:t,treeContext:n,retryLane:1073741824},n=vt(18,null,null,0),n.stateNode=t,n.return=e,e.child=n,ct=e,ut=null,!0):!1;default:return!1}}function ri(e){return(e.mode&1)!==0&&(e.flags&128)===0}function si(e){if(be){var t=ut;if(t){var n=t;if(!Hl(e,t)){if(ri(e))throw Error(c(418));t=Gt(n.nextSibling);var s=ct;t&&Hl(e,t)?Vl(s,n):(e.flags=e.flags&-4097|2,be=!1,ct=e)}}else{if(ri(e))throw Error(c(418));e.flags=e.flags&-4097|2,be=!1,ct=e}}}function Gl(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;ct=e}function ps(e){if(e!==ct)return!1;if(!be)return Gl(e),be=!0,!1;var t;if((t=e.tag!==3)&&!(t=e.tag!==5)&&(t=e.type,t=t!=="head"&&t!=="body"&&!Qa(e.type,e.memoizedProps)),t&&(t=ut)){if(ri(e))throw Kl(),Error(c(418));for(;t;)Vl(e,t),t=Gt(t.nextSibling)}if(Gl(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(c(317));e:{for(e=e.nextSibling,t=0;e;){if(e.nodeType===8){var n=e.data;if(n==="/$"){if(t===0){ut=Gt(e.nextSibling);break e}t--}else n!=="$"&&n!=="$!"&&n!=="$?"||t++}e=e.nextSibling}ut=null}}else ut=ct?Gt(e.stateNode.nextSibling):null;return!0}function Kl(){for(var e=ut;e;)e=Gt(e.nextSibling)}function On(){ut=ct=null,be=!1}function ai(e){kt===null?kt=[e]:kt.push(e)}var bm=ee.ReactCurrentBatchConfig;function br(e,t,n){if(e=n.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(n._owner){if(n=n._owner,n){if(n.tag!==1)throw Error(c(309));var s=n.stateNode}if(!s)throw Error(c(147,e));var a=s,o=""+e;return t!==null&&t.ref!==null&&typeof t.ref=="function"&&t.ref._stringRef===o?t.ref:(t=function(u){var h=a.refs;u===null?delete h[o]:h[o]=u},t._stringRef=o,t)}if(typeof e!="string")throw Error(c(284));if(!n._owner)throw Error(c(290,e))}return e}function fs(e,t){throw e=Object.prototype.toString.call(t),Error(c(31,e==="[object Object]"?"object with keys {"+Object.keys(t).join(", ")+"}":e))}function ql(e){var t=e._init;return t(e._payload)}function Ql(e){function t(x,v){if(e){var w=x.deletions;w===null?(x.deletions=[v],x.flags|=16):w.push(v)}}function n(x,v){if(!e)return null;for(;v!==null;)t(x,v),v=v.sibling;return null}function s(x,v){for(x=new Map;v!==null;)v.key!==null?x.set(v.key,v):x.set(v.index,v),v=v.sibling;return x}function a(x,v){return x=rn(x,v),x.index=0,x.sibling=null,x}function o(x,v,w){return x.index=w,e?(w=x.alternate,w!==null?(w=w.index,w<v?(x.flags|=2,v):w):(x.flags|=2,v)):(x.flags|=1048576,v)}function u(x){return e&&x.alternate===null&&(x.flags|=2),x}function h(x,v,w,F){return v===null||v.tag!==6?(v=Xi(w,x.mode,F),v.return=x,v):(v=a(v,w),v.return=x,v)}function f(x,v,w,F){var Q=w.type;return Q===O?P(x,v,w.props.children,F,w.key):v!==null&&(v.elementType===Q||typeof Q=="object"&&Q!==null&&Q.$$typeof===ze&&ql(Q)===v.type)?(F=a(v,w.props),F.ref=br(x,v,w),F.return=x,F):(F=Bs(w.type,w.key,w.props,null,x.mode,F),F.ref=br(x,v,w),F.return=x,F)}function b(x,v,w,F){return v===null||v.tag!==4||v.stateNode.containerInfo!==w.containerInfo||v.stateNode.implementation!==w.implementation?(v=Yi(w,x.mode,F),v.return=x,v):(v=a(v,w.children||[]),v.return=x,v)}function P(x,v,w,F,Q){return v===null||v.tag!==7?(v=kn(w,x.mode,F,Q),v.return=x,v):(v=a(v,w),v.return=x,v)}function R(x,v,w){if(typeof v=="string"&&v!==""||typeof v=="number")return v=Xi(""+v,x.mode,w),v.return=x,v;if(typeof v=="object"&&v!==null){switch(v.$$typeof){case re:return w=Bs(v.type,v.key,v.props,null,x.mode,w),w.ref=br(x,null,v),w.return=x,w;case z:return v=Yi(v,x.mode,w),v.return=x,v;case ze:var F=v._init;return R(x,F(v._payload),w)}if(Yn(v)||Z(v))return v=kn(v,x.mode,w,null),v.return=x,v;fs(x,v)}return null}function E(x,v,w,F){var Q=v!==null?v.key:null;if(typeof w=="string"&&w!==""||typeof w=="number")return Q!==null?null:h(x,v,""+w,F);if(typeof w=="object"&&w!==null){switch(w.$$typeof){case re:return w.key===Q?f(x,v,w,F):null;case z:return w.key===Q?b(x,v,w,F):null;case ze:return Q=w._init,E(x,v,Q(w._payload),F)}if(Yn(w)||Z(w))return Q!==null?null:P(x,v,w,F,null);fs(x,w)}return null}function U(x,v,w,F,Q){if(typeof F=="string"&&F!==""||typeof F=="number")return x=x.get(w)||null,h(v,x,""+F,Q);if(typeof F=="object"&&F!==null){switch(F.$$typeof){case re:return x=x.get(F.key===null?w:F.key)||null,f(v,x,F,Q);case z:return x=x.get(F.key===null?w:F.key)||null,b(v,x,F,Q);case ze:var X=F._init;return U(x,v,w,X(F._payload),Q)}if(Yn(F)||Z(F))return x=x.get(w)||null,P(v,x,F,Q,null);fs(v,F)}return null}function G(x,v,w,F){for(var Q=null,X=null,Y=v,te=v=0,We=null;Y!==null&&te<w.length;te++){Y.index>te?(We=Y,Y=null):We=Y.sibling;var me=E(x,Y,w[te],F);if(me===null){Y===null&&(Y=We);break}e&&Y&&me.alternate===null&&t(x,Y),v=o(me,v,te),X===null?Q=me:X.sibling=me,X=me,Y=We}if(te===w.length)return n(x,Y),be&&mn(x,te),Q;if(Y===null){for(;te<w.length;te++)Y=R(x,w[te],F),Y!==null&&(v=o(Y,v,te),X===null?Q=Y:X.sibling=Y,X=Y);return be&&mn(x,te),Q}for(Y=s(x,Y);te<w.length;te++)We=U(Y,x,te,w[te],F),We!==null&&(e&&We.alternate!==null&&Y.delete(We.key===null?te:We.key),v=o(We,v,te),X===null?Q=We:X.sibling=We,X=We);return e&&Y.forEach(function(sn){return t(x,sn)}),be&&mn(x,te),Q}function K(x,v,w,F){var Q=Z(w);if(typeof Q!="function")throw Error(c(150));if(w=Q.call(w),w==null)throw Error(c(151));for(var X=Q=null,Y=v,te=v=0,We=null,me=w.next();Y!==null&&!me.done;te++,me=w.next()){Y.index>te?(We=Y,Y=null):We=Y.sibling;var sn=E(x,Y,me.value,F);if(sn===null){Y===null&&(Y=We);break}e&&Y&&sn.alternate===null&&t(x,Y),v=o(sn,v,te),X===null?Q=sn:X.sibling=sn,X=sn,Y=We}if(me.done)return n(x,Y),be&&mn(x,te),Q;if(Y===null){for(;!me.done;te++,me=w.next())me=R(x,me.value,F),me!==null&&(v=o(me,v,te),X===null?Q=me:X.sibling=me,X=me);return be&&mn(x,te),Q}for(Y=s(x,Y);!me.done;te++,me=w.next())me=U(Y,x,te,me.value,F),me!==null&&(e&&me.alternate!==null&&Y.delete(me.key===null?te:me.key),v=o(me,v,te),X===null?Q=me:X.sibling=me,X=me);return e&&Y.forEach(function(th){return t(x,th)}),be&&mn(x,te),Q}function Ee(x,v,w,F){if(typeof w=="object"&&w!==null&&w.type===O&&w.key===null&&(w=w.props.children),typeof w=="object"&&w!==null){switch(w.$$typeof){case re:e:{for(var Q=w.key,X=v;X!==null;){if(X.key===Q){if(Q=w.type,Q===O){if(X.tag===7){n(x,X.sibling),v=a(X,w.props.children),v.return=x,x=v;break e}}else if(X.elementType===Q||typeof Q=="object"&&Q!==null&&Q.$$typeof===ze&&ql(Q)===X.type){n(x,X.sibling),v=a(X,w.props),v.ref=br(x,X,w),v.return=x,x=v;break e}n(x,X);break}else t(x,X);X=X.sibling}w.type===O?(v=kn(w.props.children,x.mode,F,w.key),v.return=x,x=v):(F=Bs(w.type,w.key,w.props,null,x.mode,F),F.ref=br(x,v,w),F.return=x,x=F)}return u(x);case z:e:{for(X=w.key;v!==null;){if(v.key===X)if(v.tag===4&&v.stateNode.containerInfo===w.containerInfo&&v.stateNode.implementation===w.implementation){n(x,v.sibling),v=a(v,w.children||[]),v.return=x,x=v;break e}else{n(x,v);break}else t(x,v);v=v.sibling}v=Yi(w,x.mode,F),v.return=x,x=v}return u(x);case ze:return X=w._init,Ee(x,v,X(w._payload),F)}if(Yn(w))return G(x,v,w,F);if(Z(w))return K(x,v,w,F);fs(x,w)}return typeof w=="string"&&w!==""||typeof w=="number"?(w=""+w,v!==null&&v.tag===6?(n(x,v.sibling),v=a(v,w),v.return=x,x=v):(n(x,v),v=Xi(w,x.mode,F),v.return=x,x=v),u(x)):n(x,v)}return Ee}var Wn=Ql(!0),Xl=Ql(!1),gs=Kt(null),vs=null,Un=null,ii=null;function oi(){ii=Un=vs=null}function li(e){var t=gs.current;ke(gs),e._currentValue=t}function ci(e,t,n){for(;e!==null;){var s=e.alternate;if((e.childLanes&t)!==t?(e.childLanes|=t,s!==null&&(s.childLanes|=t)):s!==null&&(s.childLanes&t)!==t&&(s.childLanes|=t),e===n)break;e=e.return}}function $n(e,t){vs=e,ii=Un=null,e=e.dependencies,e!==null&&e.firstContext!==null&&((e.lanes&t)!==0&&(tt=!0),e.firstContext=null)}function pt(e){var t=e._currentValue;if(ii!==e)if(e={context:e,memoizedValue:t,next:null},Un===null){if(vs===null)throw Error(c(308));Un=e,vs.dependencies={lanes:0,firstContext:e}}else Un=Un.next=e;return t}var hn=null;function ui(e){hn===null?hn=[e]:hn.push(e)}function Yl(e,t,n,s){var a=t.interleaved;return a===null?(n.next=n,ui(t)):(n.next=a.next,a.next=n),t.interleaved=n,It(e,s)}function It(e,t){e.lanes|=t;var n=e.alternate;for(n!==null&&(n.lanes|=t),n=e,e=e.return;e!==null;)e.childLanes|=t,n=e.alternate,n!==null&&(n.childLanes|=t),n=e,e=e.return;return n.tag===3?n.stateNode:null}var Xt=!1;function di(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function Jl(e,t){e=e.updateQueue,t.updateQueue===e&&(t.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function Ft(e,t){return{eventTime:e,lane:t,tag:0,payload:null,callback:null,next:null}}function Yt(e,t,n){var s=e.updateQueue;if(s===null)return null;if(s=s.shared,(le&2)!==0){var a=s.pending;return a===null?t.next=t:(t.next=a.next,a.next=t),s.pending=t,It(e,n)}return a=s.interleaved,a===null?(t.next=t,ui(s)):(t.next=a.next,a.next=t),s.interleaved=t,It(e,n)}function ys(e,t,n){if(t=t.updateQueue,t!==null&&(t=t.shared,(n&4194240)!==0)){var s=t.lanes;s&=e.pendingLanes,n|=s,t.lanes=n,Na(e,n)}}function Zl(e,t){var n=e.updateQueue,s=e.alternate;if(s!==null&&(s=s.updateQueue,n===s)){var a=null,o=null;if(n=n.firstBaseUpdate,n!==null){do{var u={eventTime:n.eventTime,lane:n.lane,tag:n.tag,payload:n.payload,callback:n.callback,next:null};o===null?a=o=u:o=o.next=u,n=n.next}while(n!==null);o===null?a=o=t:o=o.next=t}else a=o=t;n={baseState:s.baseState,firstBaseUpdate:a,lastBaseUpdate:o,shared:s.shared,effects:s.effects},e.updateQueue=n;return}e=n.lastBaseUpdate,e===null?n.firstBaseUpdate=t:e.next=t,n.lastBaseUpdate=t}function xs(e,t,n,s){var a=e.updateQueue;Xt=!1;var o=a.firstBaseUpdate,u=a.lastBaseUpdate,h=a.shared.pending;if(h!==null){a.shared.pending=null;var f=h,b=f.next;f.next=null,u===null?o=b:u.next=b,u=f;var P=e.alternate;P!==null&&(P=P.updateQueue,h=P.lastBaseUpdate,h!==u&&(h===null?P.firstBaseUpdate=b:h.next=b,P.lastBaseUpdate=f))}if(o!==null){var R=a.baseState;u=0,P=b=f=null,h=o;do{var E=h.lane,U=h.eventTime;if((s&E)===E){P!==null&&(P=P.next={eventTime:U,lane:0,tag:h.tag,payload:h.payload,callback:h.callback,next:null});e:{var G=e,K=h;switch(E=t,U=n,K.tag){case 1:if(G=K.payload,typeof G=="function"){R=G.call(U,R,E);break e}R=G;break e;case 3:G.flags=G.flags&-65537|128;case 0:if(G=K.payload,E=typeof G=="function"?G.call(U,R,E):G,E==null)break e;R=H({},R,E);break e;case 2:Xt=!0}}h.callback!==null&&h.lane!==0&&(e.flags|=64,E=a.effects,E===null?a.effects=[h]:E.push(h))}else U={eventTime:U,lane:E,tag:h.tag,payload:h.payload,callback:h.callback,next:null},P===null?(b=P=U,f=R):P=P.next=U,u|=E;if(h=h.next,h===null){if(h=a.shared.pending,h===null)break;E=h,h=E.next,E.next=null,a.lastBaseUpdate=E,a.shared.pending=null}}while(!0);if(P===null&&(f=R),a.baseState=f,a.firstBaseUpdate=b,a.lastBaseUpdate=P,t=a.shared.interleaved,t!==null){a=t;do u|=a.lane,a=a.next;while(a!==t)}else o===null&&(a.shared.lanes=0);gn|=u,e.lanes=u,e.memoizedState=R}}function ec(e,t,n){if(e=t.effects,t.effects=null,e!==null)for(t=0;t<e.length;t++){var s=e[t],a=s.callback;if(a!==null){if(s.callback=null,s=n,typeof a!="function")throw Error(c(191,a));a.call(s)}}}var jr={},Tt=Kt(jr),Sr=Kt(jr),Nr=Kt(jr);function pn(e){if(e===jr)throw Error(c(174));return e}function mi(e,t){switch(ye(Nr,t),ye(Sr,e),ye(Tt,jr),e=t.nodeType,e){case 9:case 11:t=(t=t.documentElement)?t.namespaceURI:ha(null,"");break;default:e=e===8?t.parentNode:t,t=e.namespaceURI||null,e=e.tagName,t=ha(t,e)}ke(Tt),ye(Tt,t)}function Vn(){ke(Tt),ke(Sr),ke(Nr)}function tc(e){pn(Nr.current);var t=pn(Tt.current),n=ha(t,e.type);t!==n&&(ye(Sr,e),ye(Tt,n))}function hi(e){Sr.current===e&&(ke(Tt),ke(Sr))}var je=Kt(0);function ks(e){for(var t=e;t!==null;){if(t.tag===13){var n=t.memoizedState;if(n!==null&&(n=n.dehydrated,n===null||n.data==="$?"||n.data==="$!"))return t}else if(t.tag===19&&t.memoizedProps.revealOrder!==void 0){if((t.flags&128)!==0)return t}else if(t.child!==null){t.child.return=t,t=t.child;continue}if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return null;t=t.return}t.sibling.return=t.return,t=t.sibling}return null}var pi=[];function fi(){for(var e=0;e<pi.length;e++)pi[e]._workInProgressVersionPrimary=null;pi.length=0}var ws=ee.ReactCurrentDispatcher,gi=ee.ReactCurrentBatchConfig,fn=0,Se=null,Ae=null,Be=null,bs=!1,Cr=!1,_r=0,jm=0;function Ke(){throw Error(c(321))}function vi(e,t){if(t===null)return!1;for(var n=0;n<t.length&&n<e.length;n++)if(!xt(e[n],t[n]))return!1;return!0}function yi(e,t,n,s,a,o){if(fn=o,Se=t,t.memoizedState=null,t.updateQueue=null,t.lanes=0,ws.current=e===null||e.memoizedState===null?_m:Tm,e=n(s,a),Cr){o=0;do{if(Cr=!1,_r=0,25<=o)throw Error(c(301));o+=1,Be=Ae=null,t.updateQueue=null,ws.current=Em,e=n(s,a)}while(Cr)}if(ws.current=Ns,t=Ae!==null&&Ae.next!==null,fn=0,Be=Ae=Se=null,bs=!1,t)throw Error(c(300));return e}function xi(){var e=_r!==0;return _r=0,e}function Et(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return Be===null?Se.memoizedState=Be=e:Be=Be.next=e,Be}function ft(){if(Ae===null){var e=Se.alternate;e=e!==null?e.memoizedState:null}else e=Ae.next;var t=Be===null?Se.memoizedState:Be.next;if(t!==null)Be=t,Ae=e;else{if(e===null)throw Error(c(310));Ae=e,e={memoizedState:Ae.memoizedState,baseState:Ae.baseState,baseQueue:Ae.baseQueue,queue:Ae.queue,next:null},Be===null?Se.memoizedState=Be=e:Be=Be.next=e}return Be}function Tr(e,t){return typeof t=="function"?t(e):t}function ki(e){var t=ft(),n=t.queue;if(n===null)throw Error(c(311));n.lastRenderedReducer=e;var s=Ae,a=s.baseQueue,o=n.pending;if(o!==null){if(a!==null){var u=a.next;a.next=o.next,o.next=u}s.baseQueue=a=o,n.pending=null}if(a!==null){o=a.next,s=s.baseState;var h=u=null,f=null,b=o;do{var P=b.lane;if((fn&P)===P)f!==null&&(f=f.next={lane:0,action:b.action,hasEagerState:b.hasEagerState,eagerState:b.eagerState,next:null}),s=b.hasEagerState?b.eagerState:e(s,b.action);else{var R={lane:P,action:b.action,hasEagerState:b.hasEagerState,eagerState:b.eagerState,next:null};f===null?(h=f=R,u=s):f=f.next=R,Se.lanes|=P,gn|=P}b=b.next}while(b!==null&&b!==o);f===null?u=s:f.next=h,xt(s,t.memoizedState)||(tt=!0),t.memoizedState=s,t.baseState=u,t.baseQueue=f,n.lastRenderedState=s}if(e=n.interleaved,e!==null){a=e;do o=a.lane,Se.lanes|=o,gn|=o,a=a.next;while(a!==e)}else a===null&&(n.lanes=0);return[t.memoizedState,n.dispatch]}function wi(e){var t=ft(),n=t.queue;if(n===null)throw Error(c(311));n.lastRenderedReducer=e;var s=n.dispatch,a=n.pending,o=t.memoizedState;if(a!==null){n.pending=null;var u=a=a.next;do o=e(o,u.action),u=u.next;while(u!==a);xt(o,t.memoizedState)||(tt=!0),t.memoizedState=o,t.baseQueue===null&&(t.baseState=o),n.lastRenderedState=o}return[o,s]}function nc(){}function rc(e,t){var n=Se,s=ft(),a=t(),o=!xt(s.memoizedState,a);if(o&&(s.memoizedState=a,tt=!0),s=s.queue,bi(ic.bind(null,n,s,e),[e]),s.getSnapshot!==t||o||Be!==null&&Be.memoizedState.tag&1){if(n.flags|=2048,Er(9,ac.bind(null,n,s,a,t),void 0,null),Oe===null)throw Error(c(349));(fn&30)!==0||sc(n,t,a)}return a}function sc(e,t,n){e.flags|=16384,e={getSnapshot:t,value:n},t=Se.updateQueue,t===null?(t={lastEffect:null,stores:null},Se.updateQueue=t,t.stores=[e]):(n=t.stores,n===null?t.stores=[e]:n.push(e))}function ac(e,t,n,s){t.value=n,t.getSnapshot=s,oc(t)&&lc(e)}function ic(e,t,n){return n(function(){oc(t)&&lc(e)})}function oc(e){var t=e.getSnapshot;e=e.value;try{var n=t();return!xt(e,n)}catch{return!0}}function lc(e){var t=It(e,1);t!==null&&St(t,e,1,-1)}function cc(e){var t=Et();return typeof e=="function"&&(e=e()),t.memoizedState=t.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:Tr,lastRenderedState:e},t.queue=e,e=e.dispatch=Cm.bind(null,Se,e),[t.memoizedState,e]}function Er(e,t,n,s){return e={tag:e,create:t,destroy:n,deps:s,next:null},t=Se.updateQueue,t===null?(t={lastEffect:null,stores:null},Se.updateQueue=t,t.lastEffect=e.next=e):(n=t.lastEffect,n===null?t.lastEffect=e.next=e:(s=n.next,n.next=e,e.next=s,t.lastEffect=e)),e}function uc(){return ft().memoizedState}function js(e,t,n,s){var a=Et();Se.flags|=e,a.memoizedState=Er(1|t,n,void 0,s===void 0?null:s)}function Ss(e,t,n,s){var a=ft();s=s===void 0?null:s;var o=void 0;if(Ae!==null){var u=Ae.memoizedState;if(o=u.destroy,s!==null&&vi(s,u.deps)){a.memoizedState=Er(t,n,o,s);return}}Se.flags|=e,a.memoizedState=Er(1|t,n,o,s)}function dc(e,t){return js(8390656,8,e,t)}function bi(e,t){return Ss(2048,8,e,t)}function mc(e,t){return Ss(4,2,e,t)}function hc(e,t){return Ss(4,4,e,t)}function pc(e,t){if(typeof t=="function")return e=e(),t(e),function(){t(null)};if(t!=null)return e=e(),t.current=e,function(){t.current=null}}function fc(e,t,n){return n=n!=null?n.concat([e]):null,Ss(4,4,pc.bind(null,t,e),n)}function ji(){}function gc(e,t){var n=ft();t=t===void 0?null:t;var s=n.memoizedState;return s!==null&&t!==null&&vi(t,s[1])?s[0]:(n.memoizedState=[e,t],e)}function vc(e,t){var n=ft();t=t===void 0?null:t;var s=n.memoizedState;return s!==null&&t!==null&&vi(t,s[1])?s[0]:(e=e(),n.memoizedState=[e,t],e)}function yc(e,t,n){return(fn&21)===0?(e.baseState&&(e.baseState=!1,tt=!0),e.memoizedState=n):(xt(n,t)||(n=qo(),Se.lanes|=n,gn|=n,e.baseState=!0),t)}function Sm(e,t){var n=fe;fe=n!==0&&4>n?n:4,e(!0);var s=gi.transition;gi.transition={};try{e(!1),t()}finally{fe=n,gi.transition=s}}function xc(){return ft().memoizedState}function Nm(e,t,n){var s=tn(e);if(n={lane:s,action:n,hasEagerState:!1,eagerState:null,next:null},kc(e))wc(t,n);else if(n=Yl(e,t,n,s),n!==null){var a=Ye();St(n,e,s,a),bc(n,t,s)}}function Cm(e,t,n){var s=tn(e),a={lane:s,action:n,hasEagerState:!1,eagerState:null,next:null};if(kc(e))wc(t,a);else{var o=e.alternate;if(e.lanes===0&&(o===null||o.lanes===0)&&(o=t.lastRenderedReducer,o!==null))try{var u=t.lastRenderedState,h=o(u,n);if(a.hasEagerState=!0,a.eagerState=h,xt(h,u)){var f=t.interleaved;f===null?(a.next=a,ui(t)):(a.next=f.next,f.next=a),t.interleaved=a;return}}catch{}finally{}n=Yl(e,t,a,s),n!==null&&(a=Ye(),St(n,e,s,a),bc(n,t,s))}}function kc(e){var t=e.alternate;return e===Se||t!==null&&t===Se}function wc(e,t){Cr=bs=!0;var n=e.pending;n===null?t.next=t:(t.next=n.next,n.next=t),e.pending=t}function bc(e,t,n){if((n&4194240)!==0){var s=t.lanes;s&=e.pendingLanes,n|=s,t.lanes=n,Na(e,n)}}var Ns={readContext:pt,useCallback:Ke,useContext:Ke,useEffect:Ke,useImperativeHandle:Ke,useInsertionEffect:Ke,useLayoutEffect:Ke,useMemo:Ke,useReducer:Ke,useRef:Ke,useState:Ke,useDebugValue:Ke,useDeferredValue:Ke,useTransition:Ke,useMutableSource:Ke,useSyncExternalStore:Ke,useId:Ke,unstable_isNewReconciler:!1},_m={readContext:pt,useCallback:function(e,t){return Et().memoizedState=[e,t===void 0?null:t],e},useContext:pt,useEffect:dc,useImperativeHandle:function(e,t,n){return n=n!=null?n.concat([e]):null,js(4194308,4,pc.bind(null,t,e),n)},useLayoutEffect:function(e,t){return js(4194308,4,e,t)},useInsertionEffect:function(e,t){return js(4,2,e,t)},useMemo:function(e,t){var n=Et();return t=t===void 0?null:t,e=e(),n.memoizedState=[e,t],e},useReducer:function(e,t,n){var s=Et();return t=n!==void 0?n(t):t,s.memoizedState=s.baseState=t,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:t},s.queue=e,e=e.dispatch=Nm.bind(null,Se,e),[s.memoizedState,e]},useRef:function(e){var t=Et();return e={current:e},t.memoizedState=e},useState:cc,useDebugValue:ji,useDeferredValue:function(e){return Et().memoizedState=e},useTransition:function(){var e=cc(!1),t=e[0];return e=Sm.bind(null,e[1]),Et().memoizedState=e,[t,e]},useMutableSource:function(){},useSyncExternalStore:function(e,t,n){var s=Se,a=Et();if(be){if(n===void 0)throw Error(c(407));n=n()}else{if(n=t(),Oe===null)throw Error(c(349));(fn&30)!==0||sc(s,t,n)}a.memoizedState=n;var o={value:n,getSnapshot:t};return a.queue=o,dc(ic.bind(null,s,o,e),[e]),s.flags|=2048,Er(9,ac.bind(null,s,o,n,t),void 0,null),n},useId:function(){var e=Et(),t=Oe.identifierPrefix;if(be){var n=Dt,s=At;n=(s&~(1<<32-yt(s)-1)).toString(32)+n,t=":"+t+"R"+n,n=_r++,0<n&&(t+="H"+n.toString(32)),t+=":"}else n=jm++,t=":"+t+"r"+n.toString(32)+":";return e.memoizedState=t},unstable_isNewReconciler:!1},Tm={readContext:pt,useCallback:gc,useContext:pt,useEffect:bi,useImperativeHandle:fc,useInsertionEffect:mc,useLayoutEffect:hc,useMemo:vc,useReducer:ki,useRef:uc,useState:function(){return ki(Tr)},useDebugValue:ji,useDeferredValue:function(e){var t=ft();return yc(t,Ae.memoizedState,e)},useTransition:function(){var e=ki(Tr)[0],t=ft().memoizedState;return[e,t]},useMutableSource:nc,useSyncExternalStore:rc,useId:xc,unstable_isNewReconciler:!1},Em={readContext:pt,useCallback:gc,useContext:pt,useEffect:bi,useImperativeHandle:fc,useInsertionEffect:mc,useLayoutEffect:hc,useMemo:vc,useReducer:wi,useRef:uc,useState:function(){return wi(Tr)},useDebugValue:ji,useDeferredValue:function(e){var t=ft();return Ae===null?t.memoizedState=e:yc(t,Ae.memoizedState,e)},useTransition:function(){var e=wi(Tr)[0],t=ft().memoizedState;return[e,t]},useMutableSource:nc,useSyncExternalStore:rc,useId:xc,unstable_isNewReconciler:!1};function wt(e,t){if(e&&e.defaultProps){t=H({},t),e=e.defaultProps;for(var n in e)t[n]===void 0&&(t[n]=e[n]);return t}return t}function Si(e,t,n,s){t=e.memoizedState,n=n(s,t),n=n==null?t:H({},t,n),e.memoizedState=n,e.lanes===0&&(e.updateQueue.baseState=n)}var Cs={isMounted:function(e){return(e=e._reactInternals)?ln(e)===e:!1},enqueueSetState:function(e,t,n){e=e._reactInternals;var s=Ye(),a=tn(e),o=Ft(s,a);o.payload=t,n!=null&&(o.callback=n),t=Yt(e,o,a),t!==null&&(St(t,e,a,s),ys(t,e,a))},enqueueReplaceState:function(e,t,n){e=e._reactInternals;var s=Ye(),a=tn(e),o=Ft(s,a);o.tag=1,o.payload=t,n!=null&&(o.callback=n),t=Yt(e,o,a),t!==null&&(St(t,e,a,s),ys(t,e,a))},enqueueForceUpdate:function(e,t){e=e._reactInternals;var n=Ye(),s=tn(e),a=Ft(n,s);a.tag=2,t!=null&&(a.callback=t),t=Yt(e,a,s),t!==null&&(St(t,e,s,n),ys(t,e,s))}};function jc(e,t,n,s,a,o,u){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(s,o,u):t.prototype&&t.prototype.isPureReactComponent?!fr(n,s)||!fr(a,o):!0}function Sc(e,t,n){var s=!1,a=qt,o=t.contextType;return typeof o=="object"&&o!==null?o=pt(o):(a=et(t)?un:Ge.current,s=t.contextTypes,o=(s=s!=null)?Fn(e,a):qt),t=new t(n,o),e.memoizedState=t.state!==null&&t.state!==void 0?t.state:null,t.updater=Cs,e.stateNode=t,t._reactInternals=e,s&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=a,e.__reactInternalMemoizedMaskedChildContext=o),t}function Nc(e,t,n,s){e=t.state,typeof t.componentWillReceiveProps=="function"&&t.componentWillReceiveProps(n,s),typeof t.UNSAFE_componentWillReceiveProps=="function"&&t.UNSAFE_componentWillReceiveProps(n,s),t.state!==e&&Cs.enqueueReplaceState(t,t.state,null)}function Ni(e,t,n,s){var a=e.stateNode;a.props=n,a.state=e.memoizedState,a.refs={},di(e);var o=t.contextType;typeof o=="object"&&o!==null?a.context=pt(o):(o=et(t)?un:Ge.current,a.context=Fn(e,o)),a.state=e.memoizedState,o=t.getDerivedStateFromProps,typeof o=="function"&&(Si(e,t,o,n),a.state=e.memoizedState),typeof t.getDerivedStateFromProps=="function"||typeof a.getSnapshotBeforeUpdate=="function"||typeof a.UNSAFE_componentWillMount!="function"&&typeof a.componentWillMount!="function"||(t=a.state,typeof a.componentWillMount=="function"&&a.componentWillMount(),typeof a.UNSAFE_componentWillMount=="function"&&a.UNSAFE_componentWillMount(),t!==a.state&&Cs.enqueueReplaceState(a,a.state,null),xs(e,n,a,s),a.state=e.memoizedState),typeof a.componentDidMount=="function"&&(e.flags|=4194308)}function Hn(e,t){try{var n="",s=t;do n+=ue(s),s=s.return;while(s);var a=n}catch(o){a=`
Error generating stack: `+o.message+`
`+o.stack}return{value:e,source:t,stack:a,digest:null}}function Ci(e,t,n){return{value:e,source:null,stack:n??null,digest:t??null}}function _i(e,t){try{console.error(t.value)}catch(n){setTimeout(function(){throw n})}}var Mm=typeof WeakMap=="function"?WeakMap:Map;function Cc(e,t,n){n=Ft(-1,n),n.tag=3,n.payload={element:null};var s=t.value;return n.callback=function(){Rs||(Rs=!0,Ui=s),_i(e,t)},n}function _c(e,t,n){n=Ft(-1,n),n.tag=3;var s=e.type.getDerivedStateFromError;if(typeof s=="function"){var a=t.value;n.payload=function(){return s(a)},n.callback=function(){_i(e,t)}}var o=e.stateNode;return o!==null&&typeof o.componentDidCatch=="function"&&(n.callback=function(){_i(e,t),typeof s!="function"&&(Zt===null?Zt=new Set([this]):Zt.add(this));var u=t.stack;this.componentDidCatch(t.value,{componentStack:u!==null?u:""})}),n}function Tc(e,t,n){var s=e.pingCache;if(s===null){s=e.pingCache=new Mm;var a=new Set;s.set(t,a)}else a=s.get(t),a===void 0&&(a=new Set,s.set(t,a));a.has(n)||(a.add(n),e=Vm.bind(null,e,t,n),t.then(e,e))}function Ec(e){do{var t;if((t=e.tag===13)&&(t=e.memoizedState,t=t!==null?t.dehydrated!==null:!0),t)return e;e=e.return}while(e!==null);return null}function Mc(e,t,n,s,a){return(e.mode&1)===0?(e===t?e.flags|=65536:(e.flags|=128,n.flags|=131072,n.flags&=-52805,n.tag===1&&(n.alternate===null?n.tag=17:(t=Ft(-1,1),t.tag=2,Yt(n,t,1))),n.lanes|=1),e):(e.flags|=65536,e.lanes=a,e)}var Pm=ee.ReactCurrentOwner,tt=!1;function Xe(e,t,n,s){t.child=e===null?Xl(t,null,n,s):Wn(t,e.child,n,s)}function Pc(e,t,n,s,a){n=n.render;var o=t.ref;return $n(t,a),s=yi(e,t,n,s,o,a),n=xi(),e!==null&&!tt?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~a,zt(e,t,a)):(be&&n&&ti(t),t.flags|=1,Xe(e,t,s,a),t.child)}function Lc(e,t,n,s,a){if(e===null){var o=n.type;return typeof o=="function"&&!Qi(o)&&o.defaultProps===void 0&&n.compare===null&&n.defaultProps===void 0?(t.tag=15,t.type=o,Rc(e,t,o,s,a)):(e=Bs(n.type,null,s,t,t.mode,a),e.ref=t.ref,e.return=t,t.child=e)}if(o=e.child,(e.lanes&a)===0){var u=o.memoizedProps;if(n=n.compare,n=n!==null?n:fr,n(u,s)&&e.ref===t.ref)return zt(e,t,a)}return t.flags|=1,e=rn(o,s),e.ref=t.ref,e.return=t,t.child=e}function Rc(e,t,n,s,a){if(e!==null){var o=e.memoizedProps;if(fr(o,s)&&e.ref===t.ref)if(tt=!1,t.pendingProps=s=o,(e.lanes&a)!==0)(e.flags&131072)!==0&&(tt=!0);else return t.lanes=e.lanes,zt(e,t,a)}return Ti(e,t,n,s,a)}function Ac(e,t,n){var s=t.pendingProps,a=s.children,o=e!==null?e.memoizedState:null;if(s.mode==="hidden")if((t.mode&1)===0)t.memoizedState={baseLanes:0,cachePool:null,transitions:null},ye(Kn,dt),dt|=n;else{if((n&1073741824)===0)return e=o!==null?o.baseLanes|n:n,t.lanes=t.childLanes=1073741824,t.memoizedState={baseLanes:e,cachePool:null,transitions:null},t.updateQueue=null,ye(Kn,dt),dt|=e,null;t.memoizedState={baseLanes:0,cachePool:null,transitions:null},s=o!==null?o.baseLanes:n,ye(Kn,dt),dt|=s}else o!==null?(s=o.baseLanes|n,t.memoizedState=null):s=n,ye(Kn,dt),dt|=s;return Xe(e,t,a,n),t.child}function Dc(e,t){var n=t.ref;(e===null&&n!==null||e!==null&&e.ref!==n)&&(t.flags|=512,t.flags|=2097152)}function Ti(e,t,n,s,a){var o=et(n)?un:Ge.current;return o=Fn(t,o),$n(t,a),n=yi(e,t,n,s,o,a),s=xi(),e!==null&&!tt?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~a,zt(e,t,a)):(be&&s&&ti(t),t.flags|=1,Xe(e,t,n,a),t.child)}function Ic(e,t,n,s,a){if(et(n)){var o=!0;us(t)}else o=!1;if($n(t,a),t.stateNode===null)Ts(e,t),Sc(t,n,s),Ni(t,n,s,a),s=!0;else if(e===null){var u=t.stateNode,h=t.memoizedProps;u.props=h;var f=u.context,b=n.contextType;typeof b=="object"&&b!==null?b=pt(b):(b=et(n)?un:Ge.current,b=Fn(t,b));var P=n.getDerivedStateFromProps,R=typeof P=="function"||typeof u.getSnapshotBeforeUpdate=="function";R||typeof u.UNSAFE_componentWillReceiveProps!="function"&&typeof u.componentWillReceiveProps!="function"||(h!==s||f!==b)&&Nc(t,u,s,b),Xt=!1;var E=t.memoizedState;u.state=E,xs(t,s,u,a),f=t.memoizedState,h!==s||E!==f||Ze.current||Xt?(typeof P=="function"&&(Si(t,n,P,s),f=t.memoizedState),(h=Xt||jc(t,n,h,s,E,f,b))?(R||typeof u.UNSAFE_componentWillMount!="function"&&typeof u.componentWillMount!="function"||(typeof u.componentWillMount=="function"&&u.componentWillMount(),typeof u.UNSAFE_componentWillMount=="function"&&u.UNSAFE_componentWillMount()),typeof u.componentDidMount=="function"&&(t.flags|=4194308)):(typeof u.componentDidMount=="function"&&(t.flags|=4194308),t.memoizedProps=s,t.memoizedState=f),u.props=s,u.state=f,u.context=b,s=h):(typeof u.componentDidMount=="function"&&(t.flags|=4194308),s=!1)}else{u=t.stateNode,Jl(e,t),h=t.memoizedProps,b=t.type===t.elementType?h:wt(t.type,h),u.props=b,R=t.pendingProps,E=u.context,f=n.contextType,typeof f=="object"&&f!==null?f=pt(f):(f=et(n)?un:Ge.current,f=Fn(t,f));var U=n.getDerivedStateFromProps;(P=typeof U=="function"||typeof u.getSnapshotBeforeUpdate=="function")||typeof u.UNSAFE_componentWillReceiveProps!="function"&&typeof u.componentWillReceiveProps!="function"||(h!==R||E!==f)&&Nc(t,u,s,f),Xt=!1,E=t.memoizedState,u.state=E,xs(t,s,u,a);var G=t.memoizedState;h!==R||E!==G||Ze.current||Xt?(typeof U=="function"&&(Si(t,n,U,s),G=t.memoizedState),(b=Xt||jc(t,n,b,s,E,G,f)||!1)?(P||typeof u.UNSAFE_componentWillUpdate!="function"&&typeof u.componentWillUpdate!="function"||(typeof u.componentWillUpdate=="function"&&u.componentWillUpdate(s,G,f),typeof u.UNSAFE_componentWillUpdate=="function"&&u.UNSAFE_componentWillUpdate(s,G,f)),typeof u.componentDidUpdate=="function"&&(t.flags|=4),typeof u.getSnapshotBeforeUpdate=="function"&&(t.flags|=1024)):(typeof u.componentDidUpdate!="function"||h===e.memoizedProps&&E===e.memoizedState||(t.flags|=4),typeof u.getSnapshotBeforeUpdate!="function"||h===e.memoizedProps&&E===e.memoizedState||(t.flags|=1024),t.memoizedProps=s,t.memoizedState=G),u.props=s,u.state=G,u.context=f,s=b):(typeof u.componentDidUpdate!="function"||h===e.memoizedProps&&E===e.memoizedState||(t.flags|=4),typeof u.getSnapshotBeforeUpdate!="function"||h===e.memoizedProps&&E===e.memoizedState||(t.flags|=1024),s=!1)}return Ei(e,t,n,s,o,a)}function Ei(e,t,n,s,a,o){Dc(e,t);var u=(t.flags&128)!==0;if(!s&&!u)return a&&Wl(t,n,!1),zt(e,t,o);s=t.stateNode,Pm.current=t;var h=u&&typeof n.getDerivedStateFromError!="function"?null:s.render();return t.flags|=1,e!==null&&u?(t.child=Wn(t,e.child,null,o),t.child=Wn(t,null,h,o)):Xe(e,t,h,o),t.memoizedState=s.state,a&&Wl(t,n,!0),t.child}function Fc(e){var t=e.stateNode;t.pendingContext?Bl(e,t.pendingContext,t.pendingContext!==t.context):t.context&&Bl(e,t.context,!1),mi(e,t.containerInfo)}function zc(e,t,n,s,a){return On(),ai(a),t.flags|=256,Xe(e,t,n,s),t.child}var Mi={dehydrated:null,treeContext:null,retryLane:0};function Pi(e){return{baseLanes:e,cachePool:null,transitions:null}}function Bc(e,t,n){var s=t.pendingProps,a=je.current,o=!1,u=(t.flags&128)!==0,h;if((h=u)||(h=e!==null&&e.memoizedState===null?!1:(a&2)!==0),h?(o=!0,t.flags&=-129):(e===null||e.memoizedState!==null)&&(a|=1),ye(je,a&1),e===null)return si(t),e=t.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?((t.mode&1)===0?t.lanes=1:e.data==="$!"?t.lanes=8:t.lanes=1073741824,null):(u=s.children,e=s.fallback,o?(s=t.mode,o=t.child,u={mode:"hidden",children:u},(s&1)===0&&o!==null?(o.childLanes=0,o.pendingProps=u):o=Os(u,s,0,null),e=kn(e,s,n,null),o.return=t,e.return=t,o.sibling=e,t.child=o,t.child.memoizedState=Pi(n),t.memoizedState=Mi,e):Li(t,u));if(a=e.memoizedState,a!==null&&(h=a.dehydrated,h!==null))return Lm(e,t,u,s,h,a,n);if(o){o=s.fallback,u=t.mode,a=e.child,h=a.sibling;var f={mode:"hidden",children:s.children};return(u&1)===0&&t.child!==a?(s=t.child,s.childLanes=0,s.pendingProps=f,t.deletions=null):(s=rn(a,f),s.subtreeFlags=a.subtreeFlags&14680064),h!==null?o=rn(h,o):(o=kn(o,u,n,null),o.flags|=2),o.return=t,s.return=t,s.sibling=o,t.child=s,s=o,o=t.child,u=e.child.memoizedState,u=u===null?Pi(n):{baseLanes:u.baseLanes|n,cachePool:null,transitions:u.transitions},o.memoizedState=u,o.childLanes=e.childLanes&~n,t.memoizedState=Mi,s}return o=e.child,e=o.sibling,s=rn(o,{mode:"visible",children:s.children}),(t.mode&1)===0&&(s.lanes=n),s.return=t,s.sibling=null,e!==null&&(n=t.deletions,n===null?(t.deletions=[e],t.flags|=16):n.push(e)),t.child=s,t.memoizedState=null,s}function Li(e,t){return t=Os({mode:"visible",children:t},e.mode,0,null),t.return=e,e.child=t}function _s(e,t,n,s){return s!==null&&ai(s),Wn(t,e.child,null,n),e=Li(t,t.pendingProps.children),e.flags|=2,t.memoizedState=null,e}function Lm(e,t,n,s,a,o,u){if(n)return t.flags&256?(t.flags&=-257,s=Ci(Error(c(422))),_s(e,t,u,s)):t.memoizedState!==null?(t.child=e.child,t.flags|=128,null):(o=s.fallback,a=t.mode,s=Os({mode:"visible",children:s.children},a,0,null),o=kn(o,a,u,null),o.flags|=2,s.return=t,o.return=t,s.sibling=o,t.child=s,(t.mode&1)!==0&&Wn(t,e.child,null,u),t.child.memoizedState=Pi(u),t.memoizedState=Mi,o);if((t.mode&1)===0)return _s(e,t,u,null);if(a.data==="$!"){if(s=a.nextSibling&&a.nextSibling.dataset,s)var h=s.dgst;return s=h,o=Error(c(419)),s=Ci(o,s,void 0),_s(e,t,u,s)}if(h=(u&e.childLanes)!==0,tt||h){if(s=Oe,s!==null){switch(u&-u){case 4:a=2;break;case 16:a=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:a=32;break;case 536870912:a=268435456;break;default:a=0}a=(a&(s.suspendedLanes|u))!==0?0:a,a!==0&&a!==o.retryLane&&(o.retryLane=a,It(e,a),St(s,e,a,-1))}return qi(),s=Ci(Error(c(421))),_s(e,t,u,s)}return a.data==="$?"?(t.flags|=128,t.child=e.child,t=Hm.bind(null,e),a._reactRetry=t,null):(e=o.treeContext,ut=Gt(a.nextSibling),ct=t,be=!0,kt=null,e!==null&&(mt[ht++]=At,mt[ht++]=Dt,mt[ht++]=dn,At=e.id,Dt=e.overflow,dn=t),t=Li(t,s.children),t.flags|=4096,t)}function Oc(e,t,n){e.lanes|=t;var s=e.alternate;s!==null&&(s.lanes|=t),ci(e.return,t,n)}function Ri(e,t,n,s,a){var o=e.memoizedState;o===null?e.memoizedState={isBackwards:t,rendering:null,renderingStartTime:0,last:s,tail:n,tailMode:a}:(o.isBackwards=t,o.rendering=null,o.renderingStartTime=0,o.last=s,o.tail=n,o.tailMode=a)}function Wc(e,t,n){var s=t.pendingProps,a=s.revealOrder,o=s.tail;if(Xe(e,t,s.children,n),s=je.current,(s&2)!==0)s=s&1|2,t.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=t.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Oc(e,n,t);else if(e.tag===19)Oc(e,n,t);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===t)break e;for(;e.sibling===null;){if(e.return===null||e.return===t)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}s&=1}if(ye(je,s),(t.mode&1)===0)t.memoizedState=null;else switch(a){case"forwards":for(n=t.child,a=null;n!==null;)e=n.alternate,e!==null&&ks(e)===null&&(a=n),n=n.sibling;n=a,n===null?(a=t.child,t.child=null):(a=n.sibling,n.sibling=null),Ri(t,!1,a,n,o);break;case"backwards":for(n=null,a=t.child,t.child=null;a!==null;){if(e=a.alternate,e!==null&&ks(e)===null){t.child=a;break}e=a.sibling,a.sibling=n,n=a,a=e}Ri(t,!0,n,null,o);break;case"together":Ri(t,!1,null,null,void 0);break;default:t.memoizedState=null}return t.child}function Ts(e,t){(t.mode&1)===0&&e!==null&&(e.alternate=null,t.alternate=null,t.flags|=2)}function zt(e,t,n){if(e!==null&&(t.dependencies=e.dependencies),gn|=t.lanes,(n&t.childLanes)===0)return null;if(e!==null&&t.child!==e.child)throw Error(c(153));if(t.child!==null){for(e=t.child,n=rn(e,e.pendingProps),t.child=n,n.return=t;e.sibling!==null;)e=e.sibling,n=n.sibling=rn(e,e.pendingProps),n.return=t;n.sibling=null}return t.child}function Rm(e,t,n){switch(t.tag){case 3:Fc(t),On();break;case 5:tc(t);break;case 1:et(t.type)&&us(t);break;case 4:mi(t,t.stateNode.containerInfo);break;case 10:var s=t.type._context,a=t.memoizedProps.value;ye(gs,s._currentValue),s._currentValue=a;break;case 13:if(s=t.memoizedState,s!==null)return s.dehydrated!==null?(ye(je,je.current&1),t.flags|=128,null):(n&t.child.childLanes)!==0?Bc(e,t,n):(ye(je,je.current&1),e=zt(e,t,n),e!==null?e.sibling:null);ye(je,je.current&1);break;case 19:if(s=(n&t.childLanes)!==0,(e.flags&128)!==0){if(s)return Wc(e,t,n);t.flags|=128}if(a=t.memoizedState,a!==null&&(a.rendering=null,a.tail=null,a.lastEffect=null),ye(je,je.current),s)break;return null;case 22:case 23:return t.lanes=0,Ac(e,t,n)}return zt(e,t,n)}var Uc,Ai,$c,Vc;Uc=function(e,t){for(var n=t.child;n!==null;){if(n.tag===5||n.tag===6)e.appendChild(n.stateNode);else if(n.tag!==4&&n.child!==null){n.child.return=n,n=n.child;continue}if(n===t)break;for(;n.sibling===null;){if(n.return===null||n.return===t)return;n=n.return}n.sibling.return=n.return,n=n.sibling}},Ai=function(){},$c=function(e,t,n,s){var a=e.memoizedProps;if(a!==s){e=t.stateNode,pn(Tt.current);var o=null;switch(n){case"input":a=ca(e,a),s=ca(e,s),o=[];break;case"select":a=H({},a,{value:void 0}),s=H({},s,{value:void 0}),o=[];break;case"textarea":a=ma(e,a),s=ma(e,s),o=[];break;default:typeof a.onClick!="function"&&typeof s.onClick=="function"&&(e.onclick=os)}pa(n,s);var u;n=null;for(b in a)if(!s.hasOwnProperty(b)&&a.hasOwnProperty(b)&&a[b]!=null)if(b==="style"){var h=a[b];for(u in h)h.hasOwnProperty(u)&&(n||(n={}),n[u]="")}else b!=="dangerouslySetInnerHTML"&&b!=="children"&&b!=="suppressContentEditableWarning"&&b!=="suppressHydrationWarning"&&b!=="autoFocus"&&(m.hasOwnProperty(b)?o||(o=[]):(o=o||[]).push(b,null));for(b in s){var f=s[b];if(h=a!=null?a[b]:void 0,s.hasOwnProperty(b)&&f!==h&&(f!=null||h!=null))if(b==="style")if(h){for(u in h)!h.hasOwnProperty(u)||f&&f.hasOwnProperty(u)||(n||(n={}),n[u]="");for(u in f)f.hasOwnProperty(u)&&h[u]!==f[u]&&(n||(n={}),n[u]=f[u])}else n||(o||(o=[]),o.push(b,n)),n=f;else b==="dangerouslySetInnerHTML"?(f=f?f.__html:void 0,h=h?h.__html:void 0,f!=null&&h!==f&&(o=o||[]).push(b,f)):b==="children"?typeof f!="string"&&typeof f!="number"||(o=o||[]).push(b,""+f):b!=="suppressContentEditableWarning"&&b!=="suppressHydrationWarning"&&(m.hasOwnProperty(b)?(f!=null&&b==="onScroll"&&xe("scroll",e),o||h===f||(o=[])):(o=o||[]).push(b,f))}n&&(o=o||[]).push("style",n);var b=o;(t.updateQueue=b)&&(t.flags|=4)}},Vc=function(e,t,n,s){n!==s&&(t.flags|=4)};function Mr(e,t){if(!be)switch(e.tailMode){case"hidden":t=e.tail;for(var n=null;t!==null;)t.alternate!==null&&(n=t),t=t.sibling;n===null?e.tail=null:n.sibling=null;break;case"collapsed":n=e.tail;for(var s=null;n!==null;)n.alternate!==null&&(s=n),n=n.sibling;s===null?t||e.tail===null?e.tail=null:e.tail.sibling=null:s.sibling=null}}function qe(e){var t=e.alternate!==null&&e.alternate.child===e.child,n=0,s=0;if(t)for(var a=e.child;a!==null;)n|=a.lanes|a.childLanes,s|=a.subtreeFlags&14680064,s|=a.flags&14680064,a.return=e,a=a.sibling;else for(a=e.child;a!==null;)n|=a.lanes|a.childLanes,s|=a.subtreeFlags,s|=a.flags,a.return=e,a=a.sibling;return e.subtreeFlags|=s,e.childLanes=n,t}function Am(e,t,n){var s=t.pendingProps;switch(ni(t),t.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return qe(t),null;case 1:return et(t.type)&&cs(),qe(t),null;case 3:return s=t.stateNode,Vn(),ke(Ze),ke(Ge),fi(),s.pendingContext&&(s.context=s.pendingContext,s.pendingContext=null),(e===null||e.child===null)&&(ps(t)?t.flags|=4:e===null||e.memoizedState.isDehydrated&&(t.flags&256)===0||(t.flags|=1024,kt!==null&&(Hi(kt),kt=null))),Ai(e,t),qe(t),null;case 5:hi(t);var a=pn(Nr.current);if(n=t.type,e!==null&&t.stateNode!=null)$c(e,t,n,s,a),e.ref!==t.ref&&(t.flags|=512,t.flags|=2097152);else{if(!s){if(t.stateNode===null)throw Error(c(166));return qe(t),null}if(e=pn(Tt.current),ps(t)){s=t.stateNode,n=t.type;var o=t.memoizedProps;switch(s[_t]=t,s[kr]=o,e=(t.mode&1)!==0,n){case"dialog":xe("cancel",s),xe("close",s);break;case"iframe":case"object":case"embed":xe("load",s);break;case"video":case"audio":for(a=0;a<vr.length;a++)xe(vr[a],s);break;case"source":xe("error",s);break;case"img":case"image":case"link":xe("error",s),xe("load",s);break;case"details":xe("toggle",s);break;case"input":So(s,o),xe("invalid",s);break;case"select":s._wrapperState={wasMultiple:!!o.multiple},xe("invalid",s);break;case"textarea":_o(s,o),xe("invalid",s)}pa(n,o),a=null;for(var u in o)if(o.hasOwnProperty(u)){var h=o[u];u==="children"?typeof h=="string"?s.textContent!==h&&(o.suppressHydrationWarning!==!0&&is(s.textContent,h,e),a=["children",h]):typeof h=="number"&&s.textContent!==""+h&&(o.suppressHydrationWarning!==!0&&is(s.textContent,h,e),a=["children",""+h]):m.hasOwnProperty(u)&&h!=null&&u==="onScroll"&&xe("scroll",s)}switch(n){case"input":Fr(s),Co(s,o,!0);break;case"textarea":Fr(s),Eo(s);break;case"select":case"option":break;default:typeof o.onClick=="function"&&(s.onclick=os)}s=a,t.updateQueue=s,s!==null&&(t.flags|=4)}else{u=a.nodeType===9?a:a.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=Mo(n)),e==="http://www.w3.org/1999/xhtml"?n==="script"?(e=u.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof s.is=="string"?e=u.createElement(n,{is:s.is}):(e=u.createElement(n),n==="select"&&(u=e,s.multiple?u.multiple=!0:s.size&&(u.size=s.size))):e=u.createElementNS(e,n),e[_t]=t,e[kr]=s,Uc(e,t,!1,!1),t.stateNode=e;e:{switch(u=fa(n,s),n){case"dialog":xe("cancel",e),xe("close",e),a=s;break;case"iframe":case"object":case"embed":xe("load",e),a=s;break;case"video":case"audio":for(a=0;a<vr.length;a++)xe(vr[a],e);a=s;break;case"source":xe("error",e),a=s;break;case"img":case"image":case"link":xe("error",e),xe("load",e),a=s;break;case"details":xe("toggle",e),a=s;break;case"input":So(e,s),a=ca(e,s),xe("invalid",e);break;case"option":a=s;break;case"select":e._wrapperState={wasMultiple:!!s.multiple},a=H({},s,{value:void 0}),xe("invalid",e);break;case"textarea":_o(e,s),a=ma(e,s),xe("invalid",e);break;default:a=s}pa(n,a),h=a;for(o in h)if(h.hasOwnProperty(o)){var f=h[o];o==="style"?Ro(e,f):o==="dangerouslySetInnerHTML"?(f=f?f.__html:void 0,f!=null&&Po(e,f)):o==="children"?typeof f=="string"?(n!=="textarea"||f!=="")&&Jn(e,f):typeof f=="number"&&Jn(e,""+f):o!=="suppressContentEditableWarning"&&o!=="suppressHydrationWarning"&&o!=="autoFocus"&&(m.hasOwnProperty(o)?f!=null&&o==="onScroll"&&xe("scroll",e):f!=null&&V(e,o,f,u))}switch(n){case"input":Fr(e),Co(e,s,!1);break;case"textarea":Fr(e),Eo(e);break;case"option":s.value!=null&&e.setAttribute("value",""+pe(s.value));break;case"select":e.multiple=!!s.multiple,o=s.value,o!=null?Nn(e,!!s.multiple,o,!1):s.defaultValue!=null&&Nn(e,!!s.multiple,s.defaultValue,!0);break;default:typeof a.onClick=="function"&&(e.onclick=os)}switch(n){case"button":case"input":case"select":case"textarea":s=!!s.autoFocus;break e;case"img":s=!0;break e;default:s=!1}}s&&(t.flags|=4)}t.ref!==null&&(t.flags|=512,t.flags|=2097152)}return qe(t),null;case 6:if(e&&t.stateNode!=null)Vc(e,t,e.memoizedProps,s);else{if(typeof s!="string"&&t.stateNode===null)throw Error(c(166));if(n=pn(Nr.current),pn(Tt.current),ps(t)){if(s=t.stateNode,n=t.memoizedProps,s[_t]=t,(o=s.nodeValue!==n)&&(e=ct,e!==null))switch(e.tag){case 3:is(s.nodeValue,n,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&is(s.nodeValue,n,(e.mode&1)!==0)}o&&(t.flags|=4)}else s=(n.nodeType===9?n:n.ownerDocument).createTextNode(s),s[_t]=t,t.stateNode=s}return qe(t),null;case 13:if(ke(je),s=t.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(be&&ut!==null&&(t.mode&1)!==0&&(t.flags&128)===0)Kl(),On(),t.flags|=98560,o=!1;else if(o=ps(t),s!==null&&s.dehydrated!==null){if(e===null){if(!o)throw Error(c(318));if(o=t.memoizedState,o=o!==null?o.dehydrated:null,!o)throw Error(c(317));o[_t]=t}else On(),(t.flags&128)===0&&(t.memoizedState=null),t.flags|=4;qe(t),o=!1}else kt!==null&&(Hi(kt),kt=null),o=!0;if(!o)return t.flags&65536?t:null}return(t.flags&128)!==0?(t.lanes=n,t):(s=s!==null,s!==(e!==null&&e.memoizedState!==null)&&s&&(t.child.flags|=8192,(t.mode&1)!==0&&(e===null||(je.current&1)!==0?De===0&&(De=3):qi())),t.updateQueue!==null&&(t.flags|=4),qe(t),null);case 4:return Vn(),Ai(e,t),e===null&&yr(t.stateNode.containerInfo),qe(t),null;case 10:return li(t.type._context),qe(t),null;case 17:return et(t.type)&&cs(),qe(t),null;case 19:if(ke(je),o=t.memoizedState,o===null)return qe(t),null;if(s=(t.flags&128)!==0,u=o.rendering,u===null)if(s)Mr(o,!1);else{if(De!==0||e!==null&&(e.flags&128)!==0)for(e=t.child;e!==null;){if(u=ks(e),u!==null){for(t.flags|=128,Mr(o,!1),s=u.updateQueue,s!==null&&(t.updateQueue=s,t.flags|=4),t.subtreeFlags=0,s=n,n=t.child;n!==null;)o=n,e=s,o.flags&=14680066,u=o.alternate,u===null?(o.childLanes=0,o.lanes=e,o.child=null,o.subtreeFlags=0,o.memoizedProps=null,o.memoizedState=null,o.updateQueue=null,o.dependencies=null,o.stateNode=null):(o.childLanes=u.childLanes,o.lanes=u.lanes,o.child=u.child,o.subtreeFlags=0,o.deletions=null,o.memoizedProps=u.memoizedProps,o.memoizedState=u.memoizedState,o.updateQueue=u.updateQueue,o.type=u.type,e=u.dependencies,o.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),n=n.sibling;return ye(je,je.current&1|2),t.child}e=e.sibling}o.tail!==null&&Te()>qn&&(t.flags|=128,s=!0,Mr(o,!1),t.lanes=4194304)}else{if(!s)if(e=ks(u),e!==null){if(t.flags|=128,s=!0,n=e.updateQueue,n!==null&&(t.updateQueue=n,t.flags|=4),Mr(o,!0),o.tail===null&&o.tailMode==="hidden"&&!u.alternate&&!be)return qe(t),null}else 2*Te()-o.renderingStartTime>qn&&n!==1073741824&&(t.flags|=128,s=!0,Mr(o,!1),t.lanes=4194304);o.isBackwards?(u.sibling=t.child,t.child=u):(n=o.last,n!==null?n.sibling=u:t.child=u,o.last=u)}return o.tail!==null?(t=o.tail,o.rendering=t,o.tail=t.sibling,o.renderingStartTime=Te(),t.sibling=null,n=je.current,ye(je,s?n&1|2:n&1),t):(qe(t),null);case 22:case 23:return Ki(),s=t.memoizedState!==null,e!==null&&e.memoizedState!==null!==s&&(t.flags|=8192),s&&(t.mode&1)!==0?(dt&1073741824)!==0&&(qe(t),t.subtreeFlags&6&&(t.flags|=8192)):qe(t),null;case 24:return null;case 25:return null}throw Error(c(156,t.tag))}function Dm(e,t){switch(ni(t),t.tag){case 1:return et(t.type)&&cs(),e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 3:return Vn(),ke(Ze),ke(Ge),fi(),e=t.flags,(e&65536)!==0&&(e&128)===0?(t.flags=e&-65537|128,t):null;case 5:return hi(t),null;case 13:if(ke(je),e=t.memoizedState,e!==null&&e.dehydrated!==null){if(t.alternate===null)throw Error(c(340));On()}return e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 19:return ke(je),null;case 4:return Vn(),null;case 10:return li(t.type._context),null;case 22:case 23:return Ki(),null;case 24:return null;default:return null}}var Es=!1,Qe=!1,Im=typeof WeakSet=="function"?WeakSet:Set,$=null;function Gn(e,t){var n=e.ref;if(n!==null)if(typeof n=="function")try{n(null)}catch(s){Ne(e,t,s)}else n.current=null}function Di(e,t,n){try{n()}catch(s){Ne(e,t,s)}}var Hc=!1;function Fm(e,t){if(Ka=Qr,e=jl(),Ba(e)){if("selectionStart"in e)var n={start:e.selectionStart,end:e.selectionEnd};else e:{n=(n=e.ownerDocument)&&n.defaultView||window;var s=n.getSelection&&n.getSelection();if(s&&s.rangeCount!==0){n=s.anchorNode;var a=s.anchorOffset,o=s.focusNode;s=s.focusOffset;try{n.nodeType,o.nodeType}catch{n=null;break e}var u=0,h=-1,f=-1,b=0,P=0,R=e,E=null;t:for(;;){for(var U;R!==n||a!==0&&R.nodeType!==3||(h=u+a),R!==o||s!==0&&R.nodeType!==3||(f=u+s),R.nodeType===3&&(u+=R.nodeValue.length),(U=R.firstChild)!==null;)E=R,R=U;for(;;){if(R===e)break t;if(E===n&&++b===a&&(h=u),E===o&&++P===s&&(f=u),(U=R.nextSibling)!==null)break;R=E,E=R.parentNode}R=U}n=h===-1||f===-1?null:{start:h,end:f}}else n=null}n=n||{start:0,end:0}}else n=null;for(qa={focusedElem:e,selectionRange:n},Qr=!1,$=t;$!==null;)if(t=$,e=t.child,(t.subtreeFlags&1028)!==0&&e!==null)e.return=t,$=e;else for(;$!==null;){t=$;try{var G=t.alternate;if((t.flags&1024)!==0)switch(t.tag){case 0:case 11:case 15:break;case 1:if(G!==null){var K=G.memoizedProps,Ee=G.memoizedState,x=t.stateNode,v=x.getSnapshotBeforeUpdate(t.elementType===t.type?K:wt(t.type,K),Ee);x.__reactInternalSnapshotBeforeUpdate=v}break;case 3:var w=t.stateNode.containerInfo;w.nodeType===1?w.textContent="":w.nodeType===9&&w.documentElement&&w.removeChild(w.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(c(163))}}catch(F){Ne(t,t.return,F)}if(e=t.sibling,e!==null){e.return=t.return,$=e;break}$=t.return}return G=Hc,Hc=!1,G}function Pr(e,t,n){var s=t.updateQueue;if(s=s!==null?s.lastEffect:null,s!==null){var a=s=s.next;do{if((a.tag&e)===e){var o=a.destroy;a.destroy=void 0,o!==void 0&&Di(t,n,o)}a=a.next}while(a!==s)}}function Ms(e,t){if(t=t.updateQueue,t=t!==null?t.lastEffect:null,t!==null){var n=t=t.next;do{if((n.tag&e)===e){var s=n.create;n.destroy=s()}n=n.next}while(n!==t)}}function Ii(e){var t=e.ref;if(t!==null){var n=e.stateNode;switch(e.tag){case 5:e=n;break;default:e=n}typeof t=="function"?t(e):t.current=e}}function Gc(e){var t=e.alternate;t!==null&&(e.alternate=null,Gc(t)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(t=e.stateNode,t!==null&&(delete t[_t],delete t[kr],delete t[Ja],delete t[xm],delete t[km])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function Kc(e){return e.tag===5||e.tag===3||e.tag===4}function qc(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||Kc(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Fi(e,t,n){var s=e.tag;if(s===5||s===6)e=e.stateNode,t?n.nodeType===8?n.parentNode.insertBefore(e,t):n.insertBefore(e,t):(n.nodeType===8?(t=n.parentNode,t.insertBefore(e,n)):(t=n,t.appendChild(e)),n=n._reactRootContainer,n!=null||t.onclick!==null||(t.onclick=os));else if(s!==4&&(e=e.child,e!==null))for(Fi(e,t,n),e=e.sibling;e!==null;)Fi(e,t,n),e=e.sibling}function zi(e,t,n){var s=e.tag;if(s===5||s===6)e=e.stateNode,t?n.insertBefore(e,t):n.appendChild(e);else if(s!==4&&(e=e.child,e!==null))for(zi(e,t,n),e=e.sibling;e!==null;)zi(e,t,n),e=e.sibling}var $e=null,bt=!1;function Jt(e,t,n){for(n=n.child;n!==null;)Qc(e,t,n),n=n.sibling}function Qc(e,t,n){if(Ct&&typeof Ct.onCommitFiberUnmount=="function")try{Ct.onCommitFiberUnmount($r,n)}catch{}switch(n.tag){case 5:Qe||Gn(n,t);case 6:var s=$e,a=bt;$e=null,Jt(e,t,n),$e=s,bt=a,$e!==null&&(bt?(e=$e,n=n.stateNode,e.nodeType===8?e.parentNode.removeChild(n):e.removeChild(n)):$e.removeChild(n.stateNode));break;case 18:$e!==null&&(bt?(e=$e,n=n.stateNode,e.nodeType===8?Ya(e.parentNode,n):e.nodeType===1&&Ya(e,n),cr(e)):Ya($e,n.stateNode));break;case 4:s=$e,a=bt,$e=n.stateNode.containerInfo,bt=!0,Jt(e,t,n),$e=s,bt=a;break;case 0:case 11:case 14:case 15:if(!Qe&&(s=n.updateQueue,s!==null&&(s=s.lastEffect,s!==null))){a=s=s.next;do{var o=a,u=o.destroy;o=o.tag,u!==void 0&&((o&2)!==0||(o&4)!==0)&&Di(n,t,u),a=a.next}while(a!==s)}Jt(e,t,n);break;case 1:if(!Qe&&(Gn(n,t),s=n.stateNode,typeof s.componentWillUnmount=="function"))try{s.props=n.memoizedProps,s.state=n.memoizedState,s.componentWillUnmount()}catch(h){Ne(n,t,h)}Jt(e,t,n);break;case 21:Jt(e,t,n);break;case 22:n.mode&1?(Qe=(s=Qe)||n.memoizedState!==null,Jt(e,t,n),Qe=s):Jt(e,t,n);break;default:Jt(e,t,n)}}function Xc(e){var t=e.updateQueue;if(t!==null){e.updateQueue=null;var n=e.stateNode;n===null&&(n=e.stateNode=new Im),t.forEach(function(s){var a=Gm.bind(null,e,s);n.has(s)||(n.add(s),s.then(a,a))})}}function jt(e,t){var n=t.deletions;if(n!==null)for(var s=0;s<n.length;s++){var a=n[s];try{var o=e,u=t,h=u;e:for(;h!==null;){switch(h.tag){case 5:$e=h.stateNode,bt=!1;break e;case 3:$e=h.stateNode.containerInfo,bt=!0;break e;case 4:$e=h.stateNode.containerInfo,bt=!0;break e}h=h.return}if($e===null)throw Error(c(160));Qc(o,u,a),$e=null,bt=!1;var f=a.alternate;f!==null&&(f.return=null),a.return=null}catch(b){Ne(a,t,b)}}if(t.subtreeFlags&12854)for(t=t.child;t!==null;)Yc(t,e),t=t.sibling}function Yc(e,t){var n=e.alternate,s=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(jt(t,e),Mt(e),s&4){try{Pr(3,e,e.return),Ms(3,e)}catch(K){Ne(e,e.return,K)}try{Pr(5,e,e.return)}catch(K){Ne(e,e.return,K)}}break;case 1:jt(t,e),Mt(e),s&512&&n!==null&&Gn(n,n.return);break;case 5:if(jt(t,e),Mt(e),s&512&&n!==null&&Gn(n,n.return),e.flags&32){var a=e.stateNode;try{Jn(a,"")}catch(K){Ne(e,e.return,K)}}if(s&4&&(a=e.stateNode,a!=null)){var o=e.memoizedProps,u=n!==null?n.memoizedProps:o,h=e.type,f=e.updateQueue;if(e.updateQueue=null,f!==null)try{h==="input"&&o.type==="radio"&&o.name!=null&&No(a,o),fa(h,u);var b=fa(h,o);for(u=0;u<f.length;u+=2){var P=f[u],R=f[u+1];P==="style"?Ro(a,R):P==="dangerouslySetInnerHTML"?Po(a,R):P==="children"?Jn(a,R):V(a,P,R,b)}switch(h){case"input":ua(a,o);break;case"textarea":To(a,o);break;case"select":var E=a._wrapperState.wasMultiple;a._wrapperState.wasMultiple=!!o.multiple;var U=o.value;U!=null?Nn(a,!!o.multiple,U,!1):E!==!!o.multiple&&(o.defaultValue!=null?Nn(a,!!o.multiple,o.defaultValue,!0):Nn(a,!!o.multiple,o.multiple?[]:"",!1))}a[kr]=o}catch(K){Ne(e,e.return,K)}}break;case 6:if(jt(t,e),Mt(e),s&4){if(e.stateNode===null)throw Error(c(162));a=e.stateNode,o=e.memoizedProps;try{a.nodeValue=o}catch(K){Ne(e,e.return,K)}}break;case 3:if(jt(t,e),Mt(e),s&4&&n!==null&&n.memoizedState.isDehydrated)try{cr(t.containerInfo)}catch(K){Ne(e,e.return,K)}break;case 4:jt(t,e),Mt(e);break;case 13:jt(t,e),Mt(e),a=e.child,a.flags&8192&&(o=a.memoizedState!==null,a.stateNode.isHidden=o,!o||a.alternate!==null&&a.alternate.memoizedState!==null||(Wi=Te())),s&4&&Xc(e);break;case 22:if(P=n!==null&&n.memoizedState!==null,e.mode&1?(Qe=(b=Qe)||P,jt(t,e),Qe=b):jt(t,e),Mt(e),s&8192){if(b=e.memoizedState!==null,(e.stateNode.isHidden=b)&&!P&&(e.mode&1)!==0)for($=e,P=e.child;P!==null;){for(R=$=P;$!==null;){switch(E=$,U=E.child,E.tag){case 0:case 11:case 14:case 15:Pr(4,E,E.return);break;case 1:Gn(E,E.return);var G=E.stateNode;if(typeof G.componentWillUnmount=="function"){s=E,n=E.return;try{t=s,G.props=t.memoizedProps,G.state=t.memoizedState,G.componentWillUnmount()}catch(K){Ne(s,n,K)}}break;case 5:Gn(E,E.return);break;case 22:if(E.memoizedState!==null){eu(R);continue}}U!==null?(U.return=E,$=U):eu(R)}P=P.sibling}e:for(P=null,R=e;;){if(R.tag===5){if(P===null){P=R;try{a=R.stateNode,b?(o=a.style,typeof o.setProperty=="function"?o.setProperty("display","none","important"):o.display="none"):(h=R.stateNode,f=R.memoizedProps.style,u=f!=null&&f.hasOwnProperty("display")?f.display:null,h.style.display=Lo("display",u))}catch(K){Ne(e,e.return,K)}}}else if(R.tag===6){if(P===null)try{R.stateNode.nodeValue=b?"":R.memoizedProps}catch(K){Ne(e,e.return,K)}}else if((R.tag!==22&&R.tag!==23||R.memoizedState===null||R===e)&&R.child!==null){R.child.return=R,R=R.child;continue}if(R===e)break e;for(;R.sibling===null;){if(R.return===null||R.return===e)break e;P===R&&(P=null),R=R.return}P===R&&(P=null),R.sibling.return=R.return,R=R.sibling}}break;case 19:jt(t,e),Mt(e),s&4&&Xc(e);break;case 21:break;default:jt(t,e),Mt(e)}}function Mt(e){var t=e.flags;if(t&2){try{e:{for(var n=e.return;n!==null;){if(Kc(n)){var s=n;break e}n=n.return}throw Error(c(160))}switch(s.tag){case 5:var a=s.stateNode;s.flags&32&&(Jn(a,""),s.flags&=-33);var o=qc(e);zi(e,o,a);break;case 3:case 4:var u=s.stateNode.containerInfo,h=qc(e);Fi(e,h,u);break;default:throw Error(c(161))}}catch(f){Ne(e,e.return,f)}e.flags&=-3}t&4096&&(e.flags&=-4097)}function zm(e,t,n){$=e,Jc(e)}function Jc(e,t,n){for(var s=(e.mode&1)!==0;$!==null;){var a=$,o=a.child;if(a.tag===22&&s){var u=a.memoizedState!==null||Es;if(!u){var h=a.alternate,f=h!==null&&h.memoizedState!==null||Qe;h=Es;var b=Qe;if(Es=u,(Qe=f)&&!b)for($=a;$!==null;)u=$,f=u.child,u.tag===22&&u.memoizedState!==null?tu(a):f!==null?(f.return=u,$=f):tu(a);for(;o!==null;)$=o,Jc(o),o=o.sibling;$=a,Es=h,Qe=b}Zc(e)}else(a.subtreeFlags&8772)!==0&&o!==null?(o.return=a,$=o):Zc(e)}}function Zc(e){for(;$!==null;){var t=$;if((t.flags&8772)!==0){var n=t.alternate;try{if((t.flags&8772)!==0)switch(t.tag){case 0:case 11:case 15:Qe||Ms(5,t);break;case 1:var s=t.stateNode;if(t.flags&4&&!Qe)if(n===null)s.componentDidMount();else{var a=t.elementType===t.type?n.memoizedProps:wt(t.type,n.memoizedProps);s.componentDidUpdate(a,n.memoizedState,s.__reactInternalSnapshotBeforeUpdate)}var o=t.updateQueue;o!==null&&ec(t,o,s);break;case 3:var u=t.updateQueue;if(u!==null){if(n=null,t.child!==null)switch(t.child.tag){case 5:n=t.child.stateNode;break;case 1:n=t.child.stateNode}ec(t,u,n)}break;case 5:var h=t.stateNode;if(n===null&&t.flags&4){n=h;var f=t.memoizedProps;switch(t.type){case"button":case"input":case"select":case"textarea":f.autoFocus&&n.focus();break;case"img":f.src&&(n.src=f.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(t.memoizedState===null){var b=t.alternate;if(b!==null){var P=b.memoizedState;if(P!==null){var R=P.dehydrated;R!==null&&cr(R)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(c(163))}Qe||t.flags&512&&Ii(t)}catch(E){Ne(t,t.return,E)}}if(t===e){$=null;break}if(n=t.sibling,n!==null){n.return=t.return,$=n;break}$=t.return}}function eu(e){for(;$!==null;){var t=$;if(t===e){$=null;break}var n=t.sibling;if(n!==null){n.return=t.return,$=n;break}$=t.return}}function tu(e){for(;$!==null;){var t=$;try{switch(t.tag){case 0:case 11:case 15:var n=t.return;try{Ms(4,t)}catch(f){Ne(t,n,f)}break;case 1:var s=t.stateNode;if(typeof s.componentDidMount=="function"){var a=t.return;try{s.componentDidMount()}catch(f){Ne(t,a,f)}}var o=t.return;try{Ii(t)}catch(f){Ne(t,o,f)}break;case 5:var u=t.return;try{Ii(t)}catch(f){Ne(t,u,f)}}}catch(f){Ne(t,t.return,f)}if(t===e){$=null;break}var h=t.sibling;if(h!==null){h.return=t.return,$=h;break}$=t.return}}var Bm=Math.ceil,Ps=ee.ReactCurrentDispatcher,Bi=ee.ReactCurrentOwner,gt=ee.ReactCurrentBatchConfig,le=0,Oe=null,Le=null,Ve=0,dt=0,Kn=Kt(0),De=0,Lr=null,gn=0,Ls=0,Oi=0,Rr=null,nt=null,Wi=0,qn=1/0,Bt=null,Rs=!1,Ui=null,Zt=null,As=!1,en=null,Ds=0,Ar=0,$i=null,Is=-1,Fs=0;function Ye(){return(le&6)!==0?Te():Is!==-1?Is:Is=Te()}function tn(e){return(e.mode&1)===0?1:(le&2)!==0&&Ve!==0?Ve&-Ve:bm.transition!==null?(Fs===0&&(Fs=qo()),Fs):(e=fe,e!==0||(e=window.event,e=e===void 0?16:rl(e.type)),e)}function St(e,t,n,s){if(50<Ar)throw Ar=0,$i=null,Error(c(185));sr(e,n,s),((le&2)===0||e!==Oe)&&(e===Oe&&((le&2)===0&&(Ls|=n),De===4&&nn(e,Ve)),rt(e,s),n===1&&le===0&&(t.mode&1)===0&&(qn=Te()+500,ds&&Qt()))}function rt(e,t){var n=e.callbackNode;bd(e,t);var s=Gr(e,e===Oe?Ve:0);if(s===0)n!==null&&Ho(n),e.callbackNode=null,e.callbackPriority=0;else if(t=s&-s,e.callbackPriority!==t){if(n!=null&&Ho(n),t===1)e.tag===0?wm(ru.bind(null,e)):Ul(ru.bind(null,e)),vm(function(){(le&6)===0&&Qt()}),n=null;else{switch(Qo(s)){case 1:n=ba;break;case 4:n=Go;break;case 16:n=Ur;break;case 536870912:n=Ko;break;default:n=Ur}n=du(n,nu.bind(null,e))}e.callbackPriority=t,e.callbackNode=n}}function nu(e,t){if(Is=-1,Fs=0,(le&6)!==0)throw Error(c(327));var n=e.callbackNode;if(Qn()&&e.callbackNode!==n)return null;var s=Gr(e,e===Oe?Ve:0);if(s===0)return null;if((s&30)!==0||(s&e.expiredLanes)!==0||t)t=zs(e,s);else{t=s;var a=le;le|=2;var o=au();(Oe!==e||Ve!==t)&&(Bt=null,qn=Te()+500,yn(e,t));do try{Um();break}catch(h){su(e,h)}while(!0);oi(),Ps.current=o,le=a,Le!==null?t=0:(Oe=null,Ve=0,t=De)}if(t!==0){if(t===2&&(a=ja(e),a!==0&&(s=a,t=Vi(e,a))),t===1)throw n=Lr,yn(e,0),nn(e,s),rt(e,Te()),n;if(t===6)nn(e,s);else{if(a=e.current.alternate,(s&30)===0&&!Om(a)&&(t=zs(e,s),t===2&&(o=ja(e),o!==0&&(s=o,t=Vi(e,o))),t===1))throw n=Lr,yn(e,0),nn(e,s),rt(e,Te()),n;switch(e.finishedWork=a,e.finishedLanes=s,t){case 0:case 1:throw Error(c(345));case 2:xn(e,nt,Bt);break;case 3:if(nn(e,s),(s&130023424)===s&&(t=Wi+500-Te(),10<t)){if(Gr(e,0)!==0)break;if(a=e.suspendedLanes,(a&s)!==s){Ye(),e.pingedLanes|=e.suspendedLanes&a;break}e.timeoutHandle=Xa(xn.bind(null,e,nt,Bt),t);break}xn(e,nt,Bt);break;case 4:if(nn(e,s),(s&4194240)===s)break;for(t=e.eventTimes,a=-1;0<s;){var u=31-yt(s);o=1<<u,u=t[u],u>a&&(a=u),s&=~o}if(s=a,s=Te()-s,s=(120>s?120:480>s?480:1080>s?1080:1920>s?1920:3e3>s?3e3:4320>s?4320:1960*Bm(s/1960))-s,10<s){e.timeoutHandle=Xa(xn.bind(null,e,nt,Bt),s);break}xn(e,nt,Bt);break;case 5:xn(e,nt,Bt);break;default:throw Error(c(329))}}}return rt(e,Te()),e.callbackNode===n?nu.bind(null,e):null}function Vi(e,t){var n=Rr;return e.current.memoizedState.isDehydrated&&(yn(e,t).flags|=256),e=zs(e,t),e!==2&&(t=nt,nt=n,t!==null&&Hi(t)),e}function Hi(e){nt===null?nt=e:nt.push.apply(nt,e)}function Om(e){for(var t=e;;){if(t.flags&16384){var n=t.updateQueue;if(n!==null&&(n=n.stores,n!==null))for(var s=0;s<n.length;s++){var a=n[s],o=a.getSnapshot;a=a.value;try{if(!xt(o(),a))return!1}catch{return!1}}}if(n=t.child,t.subtreeFlags&16384&&n!==null)n.return=t,t=n;else{if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return!0;t=t.return}t.sibling.return=t.return,t=t.sibling}}return!0}function nn(e,t){for(t&=~Oi,t&=~Ls,e.suspendedLanes|=t,e.pingedLanes&=~t,e=e.expirationTimes;0<t;){var n=31-yt(t),s=1<<n;e[n]=-1,t&=~s}}function ru(e){if((le&6)!==0)throw Error(c(327));Qn();var t=Gr(e,0);if((t&1)===0)return rt(e,Te()),null;var n=zs(e,t);if(e.tag!==0&&n===2){var s=ja(e);s!==0&&(t=s,n=Vi(e,s))}if(n===1)throw n=Lr,yn(e,0),nn(e,t),rt(e,Te()),n;if(n===6)throw Error(c(345));return e.finishedWork=e.current.alternate,e.finishedLanes=t,xn(e,nt,Bt),rt(e,Te()),null}function Gi(e,t){var n=le;le|=1;try{return e(t)}finally{le=n,le===0&&(qn=Te()+500,ds&&Qt())}}function vn(e){en!==null&&en.tag===0&&(le&6)===0&&Qn();var t=le;le|=1;var n=gt.transition,s=fe;try{if(gt.transition=null,fe=1,e)return e()}finally{fe=s,gt.transition=n,le=t,(le&6)===0&&Qt()}}function Ki(){dt=Kn.current,ke(Kn)}function yn(e,t){e.finishedWork=null,e.finishedLanes=0;var n=e.timeoutHandle;if(n!==-1&&(e.timeoutHandle=-1,gm(n)),Le!==null)for(n=Le.return;n!==null;){var s=n;switch(ni(s),s.tag){case 1:s=s.type.childContextTypes,s!=null&&cs();break;case 3:Vn(),ke(Ze),ke(Ge),fi();break;case 5:hi(s);break;case 4:Vn();break;case 13:ke(je);break;case 19:ke(je);break;case 10:li(s.type._context);break;case 22:case 23:Ki()}n=n.return}if(Oe=e,Le=e=rn(e.current,null),Ve=dt=t,De=0,Lr=null,Oi=Ls=gn=0,nt=Rr=null,hn!==null){for(t=0;t<hn.length;t++)if(n=hn[t],s=n.interleaved,s!==null){n.interleaved=null;var a=s.next,o=n.pending;if(o!==null){var u=o.next;o.next=a,s.next=u}n.pending=s}hn=null}return e}function su(e,t){do{var n=Le;try{if(oi(),ws.current=Ns,bs){for(var s=Se.memoizedState;s!==null;){var a=s.queue;a!==null&&(a.pending=null),s=s.next}bs=!1}if(fn=0,Be=Ae=Se=null,Cr=!1,_r=0,Bi.current=null,n===null||n.return===null){De=1,Lr=t,Le=null;break}e:{var o=e,u=n.return,h=n,f=t;if(t=Ve,h.flags|=32768,f!==null&&typeof f=="object"&&typeof f.then=="function"){var b=f,P=h,R=P.tag;if((P.mode&1)===0&&(R===0||R===11||R===15)){var E=P.alternate;E?(P.updateQueue=E.updateQueue,P.memoizedState=E.memoizedState,P.lanes=E.lanes):(P.updateQueue=null,P.memoizedState=null)}var U=Ec(u);if(U!==null){U.flags&=-257,Mc(U,u,h,o,t),U.mode&1&&Tc(o,b,t),t=U,f=b;var G=t.updateQueue;if(G===null){var K=new Set;K.add(f),t.updateQueue=K}else G.add(f);break e}else{if((t&1)===0){Tc(o,b,t),qi();break e}f=Error(c(426))}}else if(be&&h.mode&1){var Ee=Ec(u);if(Ee!==null){(Ee.flags&65536)===0&&(Ee.flags|=256),Mc(Ee,u,h,o,t),ai(Hn(f,h));break e}}o=f=Hn(f,h),De!==4&&(De=2),Rr===null?Rr=[o]:Rr.push(o),o=u;do{switch(o.tag){case 3:o.flags|=65536,t&=-t,o.lanes|=t;var x=Cc(o,f,t);Zl(o,x);break e;case 1:h=f;var v=o.type,w=o.stateNode;if((o.flags&128)===0&&(typeof v.getDerivedStateFromError=="function"||w!==null&&typeof w.componentDidCatch=="function"&&(Zt===null||!Zt.has(w)))){o.flags|=65536,t&=-t,o.lanes|=t;var F=_c(o,h,t);Zl(o,F);break e}}o=o.return}while(o!==null)}ou(n)}catch(Q){t=Q,Le===n&&n!==null&&(Le=n=n.return);continue}break}while(!0)}function au(){var e=Ps.current;return Ps.current=Ns,e===null?Ns:e}function qi(){(De===0||De===3||De===2)&&(De=4),Oe===null||(gn&268435455)===0&&(Ls&268435455)===0||nn(Oe,Ve)}function zs(e,t){var n=le;le|=2;var s=au();(Oe!==e||Ve!==t)&&(Bt=null,yn(e,t));do try{Wm();break}catch(a){su(e,a)}while(!0);if(oi(),le=n,Ps.current=s,Le!==null)throw Error(c(261));return Oe=null,Ve=0,De}function Wm(){for(;Le!==null;)iu(Le)}function Um(){for(;Le!==null&&!hd();)iu(Le)}function iu(e){var t=uu(e.alternate,e,dt);e.memoizedProps=e.pendingProps,t===null?ou(e):Le=t,Bi.current=null}function ou(e){var t=e;do{var n=t.alternate;if(e=t.return,(t.flags&32768)===0){if(n=Am(n,t,dt),n!==null){Le=n;return}}else{if(n=Dm(n,t),n!==null){n.flags&=32767,Le=n;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{De=6,Le=null;return}}if(t=t.sibling,t!==null){Le=t;return}Le=t=e}while(t!==null);De===0&&(De=5)}function xn(e,t,n){var s=fe,a=gt.transition;try{gt.transition=null,fe=1,$m(e,t,n,s)}finally{gt.transition=a,fe=s}return null}function $m(e,t,n,s){do Qn();while(en!==null);if((le&6)!==0)throw Error(c(327));n=e.finishedWork;var a=e.finishedLanes;if(n===null)return null;if(e.finishedWork=null,e.finishedLanes=0,n===e.current)throw Error(c(177));e.callbackNode=null,e.callbackPriority=0;var o=n.lanes|n.childLanes;if(jd(e,o),e===Oe&&(Le=Oe=null,Ve=0),(n.subtreeFlags&2064)===0&&(n.flags&2064)===0||As||(As=!0,du(Ur,function(){return Qn(),null})),o=(n.flags&15990)!==0,(n.subtreeFlags&15990)!==0||o){o=gt.transition,gt.transition=null;var u=fe;fe=1;var h=le;le|=4,Bi.current=null,Fm(e,n),Yc(n,e),cm(qa),Qr=!!Ka,qa=Ka=null,e.current=n,zm(n),pd(),le=h,fe=u,gt.transition=o}else e.current=n;if(As&&(As=!1,en=e,Ds=a),o=e.pendingLanes,o===0&&(Zt=null),vd(n.stateNode),rt(e,Te()),t!==null)for(s=e.onRecoverableError,n=0;n<t.length;n++)a=t[n],s(a.value,{componentStack:a.stack,digest:a.digest});if(Rs)throw Rs=!1,e=Ui,Ui=null,e;return(Ds&1)!==0&&e.tag!==0&&Qn(),o=e.pendingLanes,(o&1)!==0?e===$i?Ar++:(Ar=0,$i=e):Ar=0,Qt(),null}function Qn(){if(en!==null){var e=Qo(Ds),t=gt.transition,n=fe;try{if(gt.transition=null,fe=16>e?16:e,en===null)var s=!1;else{if(e=en,en=null,Ds=0,(le&6)!==0)throw Error(c(331));var a=le;for(le|=4,$=e.current;$!==null;){var o=$,u=o.child;if(($.flags&16)!==0){var h=o.deletions;if(h!==null){for(var f=0;f<h.length;f++){var b=h[f];for($=b;$!==null;){var P=$;switch(P.tag){case 0:case 11:case 15:Pr(8,P,o)}var R=P.child;if(R!==null)R.return=P,$=R;else for(;$!==null;){P=$;var E=P.sibling,U=P.return;if(Gc(P),P===b){$=null;break}if(E!==null){E.return=U,$=E;break}$=U}}}var G=o.alternate;if(G!==null){var K=G.child;if(K!==null){G.child=null;do{var Ee=K.sibling;K.sibling=null,K=Ee}while(K!==null)}}$=o}}if((o.subtreeFlags&2064)!==0&&u!==null)u.return=o,$=u;else e:for(;$!==null;){if(o=$,(o.flags&2048)!==0)switch(o.tag){case 0:case 11:case 15:Pr(9,o,o.return)}var x=o.sibling;if(x!==null){x.return=o.return,$=x;break e}$=o.return}}var v=e.current;for($=v;$!==null;){u=$;var w=u.child;if((u.subtreeFlags&2064)!==0&&w!==null)w.return=u,$=w;else e:for(u=v;$!==null;){if(h=$,(h.flags&2048)!==0)try{switch(h.tag){case 0:case 11:case 15:Ms(9,h)}}catch(Q){Ne(h,h.return,Q)}if(h===u){$=null;break e}var F=h.sibling;if(F!==null){F.return=h.return,$=F;break e}$=h.return}}if(le=a,Qt(),Ct&&typeof Ct.onPostCommitFiberRoot=="function")try{Ct.onPostCommitFiberRoot($r,e)}catch{}s=!0}return s}finally{fe=n,gt.transition=t}}return!1}function lu(e,t,n){t=Hn(n,t),t=Cc(e,t,1),e=Yt(e,t,1),t=Ye(),e!==null&&(sr(e,1,t),rt(e,t))}function Ne(e,t,n){if(e.tag===3)lu(e,e,n);else for(;t!==null;){if(t.tag===3){lu(t,e,n);break}else if(t.tag===1){var s=t.stateNode;if(typeof t.type.getDerivedStateFromError=="function"||typeof s.componentDidCatch=="function"&&(Zt===null||!Zt.has(s))){e=Hn(n,e),e=_c(t,e,1),t=Yt(t,e,1),e=Ye(),t!==null&&(sr(t,1,e),rt(t,e));break}}t=t.return}}function Vm(e,t,n){var s=e.pingCache;s!==null&&s.delete(t),t=Ye(),e.pingedLanes|=e.suspendedLanes&n,Oe===e&&(Ve&n)===n&&(De===4||De===3&&(Ve&130023424)===Ve&&500>Te()-Wi?yn(e,0):Oi|=n),rt(e,t)}function cu(e,t){t===0&&((e.mode&1)===0?t=1:(t=Hr,Hr<<=1,(Hr&130023424)===0&&(Hr=4194304)));var n=Ye();e=It(e,t),e!==null&&(sr(e,t,n),rt(e,n))}function Hm(e){var t=e.memoizedState,n=0;t!==null&&(n=t.retryLane),cu(e,n)}function Gm(e,t){var n=0;switch(e.tag){case 13:var s=e.stateNode,a=e.memoizedState;a!==null&&(n=a.retryLane);break;case 19:s=e.stateNode;break;default:throw Error(c(314))}s!==null&&s.delete(t),cu(e,n)}var uu;uu=function(e,t,n){if(e!==null)if(e.memoizedProps!==t.pendingProps||Ze.current)tt=!0;else{if((e.lanes&n)===0&&(t.flags&128)===0)return tt=!1,Rm(e,t,n);tt=(e.flags&131072)!==0}else tt=!1,be&&(t.flags&1048576)!==0&&$l(t,hs,t.index);switch(t.lanes=0,t.tag){case 2:var s=t.type;Ts(e,t),e=t.pendingProps;var a=Fn(t,Ge.current);$n(t,n),a=yi(null,t,s,e,a,n);var o=xi();return t.flags|=1,typeof a=="object"&&a!==null&&typeof a.render=="function"&&a.$$typeof===void 0?(t.tag=1,t.memoizedState=null,t.updateQueue=null,et(s)?(o=!0,us(t)):o=!1,t.memoizedState=a.state!==null&&a.state!==void 0?a.state:null,di(t),a.updater=Cs,t.stateNode=a,a._reactInternals=t,Ni(t,s,e,n),t=Ei(null,t,s,!0,o,n)):(t.tag=0,be&&o&&ti(t),Xe(null,t,a,n),t=t.child),t;case 16:s=t.elementType;e:{switch(Ts(e,t),e=t.pendingProps,a=s._init,s=a(s._payload),t.type=s,a=t.tag=qm(s),e=wt(s,e),a){case 0:t=Ti(null,t,s,e,n);break e;case 1:t=Ic(null,t,s,e,n);break e;case 11:t=Pc(null,t,s,e,n);break e;case 14:t=Lc(null,t,s,wt(s.type,e),n);break e}throw Error(c(306,s,""))}return t;case 0:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:wt(s,a),Ti(e,t,s,a,n);case 1:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:wt(s,a),Ic(e,t,s,a,n);case 3:e:{if(Fc(t),e===null)throw Error(c(387));s=t.pendingProps,o=t.memoizedState,a=o.element,Jl(e,t),xs(t,s,null,n);var u=t.memoizedState;if(s=u.element,o.isDehydrated)if(o={element:s,isDehydrated:!1,cache:u.cache,pendingSuspenseBoundaries:u.pendingSuspenseBoundaries,transitions:u.transitions},t.updateQueue.baseState=o,t.memoizedState=o,t.flags&256){a=Hn(Error(c(423)),t),t=zc(e,t,s,n,a);break e}else if(s!==a){a=Hn(Error(c(424)),t),t=zc(e,t,s,n,a);break e}else for(ut=Gt(t.stateNode.containerInfo.firstChild),ct=t,be=!0,kt=null,n=Xl(t,null,s,n),t.child=n;n;)n.flags=n.flags&-3|4096,n=n.sibling;else{if(On(),s===a){t=zt(e,t,n);break e}Xe(e,t,s,n)}t=t.child}return t;case 5:return tc(t),e===null&&si(t),s=t.type,a=t.pendingProps,o=e!==null?e.memoizedProps:null,u=a.children,Qa(s,a)?u=null:o!==null&&Qa(s,o)&&(t.flags|=32),Dc(e,t),Xe(e,t,u,n),t.child;case 6:return e===null&&si(t),null;case 13:return Bc(e,t,n);case 4:return mi(t,t.stateNode.containerInfo),s=t.pendingProps,e===null?t.child=Wn(t,null,s,n):Xe(e,t,s,n),t.child;case 11:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:wt(s,a),Pc(e,t,s,a,n);case 7:return Xe(e,t,t.pendingProps,n),t.child;case 8:return Xe(e,t,t.pendingProps.children,n),t.child;case 12:return Xe(e,t,t.pendingProps.children,n),t.child;case 10:e:{if(s=t.type._context,a=t.pendingProps,o=t.memoizedProps,u=a.value,ye(gs,s._currentValue),s._currentValue=u,o!==null)if(xt(o.value,u)){if(o.children===a.children&&!Ze.current){t=zt(e,t,n);break e}}else for(o=t.child,o!==null&&(o.return=t);o!==null;){var h=o.dependencies;if(h!==null){u=o.child;for(var f=h.firstContext;f!==null;){if(f.context===s){if(o.tag===1){f=Ft(-1,n&-n),f.tag=2;var b=o.updateQueue;if(b!==null){b=b.shared;var P=b.pending;P===null?f.next=f:(f.next=P.next,P.next=f),b.pending=f}}o.lanes|=n,f=o.alternate,f!==null&&(f.lanes|=n),ci(o.return,n,t),h.lanes|=n;break}f=f.next}}else if(o.tag===10)u=o.type===t.type?null:o.child;else if(o.tag===18){if(u=o.return,u===null)throw Error(c(341));u.lanes|=n,h=u.alternate,h!==null&&(h.lanes|=n),ci(u,n,t),u=o.sibling}else u=o.child;if(u!==null)u.return=o;else for(u=o;u!==null;){if(u===t){u=null;break}if(o=u.sibling,o!==null){o.return=u.return,u=o;break}u=u.return}o=u}Xe(e,t,a.children,n),t=t.child}return t;case 9:return a=t.type,s=t.pendingProps.children,$n(t,n),a=pt(a),s=s(a),t.flags|=1,Xe(e,t,s,n),t.child;case 14:return s=t.type,a=wt(s,t.pendingProps),a=wt(s.type,a),Lc(e,t,s,a,n);case 15:return Rc(e,t,t.type,t.pendingProps,n);case 17:return s=t.type,a=t.pendingProps,a=t.elementType===s?a:wt(s,a),Ts(e,t),t.tag=1,et(s)?(e=!0,us(t)):e=!1,$n(t,n),Sc(t,s,a),Ni(t,s,a,n),Ei(null,t,s,!0,e,n);case 19:return Wc(e,t,n);case 22:return Ac(e,t,n)}throw Error(c(156,t.tag))};function du(e,t){return Vo(e,t)}function Km(e,t,n,s){this.tag=e,this.key=n,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=t,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=s,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function vt(e,t,n,s){return new Km(e,t,n,s)}function Qi(e){return e=e.prototype,!(!e||!e.isReactComponent)}function qm(e){if(typeof e=="function")return Qi(e)?1:0;if(e!=null){if(e=e.$$typeof,e===_e)return 11;if(e===He)return 14}return 2}function rn(e,t){var n=e.alternate;return n===null?(n=vt(e.tag,t,e.key,e.mode),n.elementType=e.elementType,n.type=e.type,n.stateNode=e.stateNode,n.alternate=e,e.alternate=n):(n.pendingProps=t,n.type=e.type,n.flags=0,n.subtreeFlags=0,n.deletions=null),n.flags=e.flags&14680064,n.childLanes=e.childLanes,n.lanes=e.lanes,n.child=e.child,n.memoizedProps=e.memoizedProps,n.memoizedState=e.memoizedState,n.updateQueue=e.updateQueue,t=e.dependencies,n.dependencies=t===null?null:{lanes:t.lanes,firstContext:t.firstContext},n.sibling=e.sibling,n.index=e.index,n.ref=e.ref,n}function Bs(e,t,n,s,a,o){var u=2;if(s=e,typeof e=="function")Qi(e)&&(u=1);else if(typeof e=="string")u=5;else e:switch(e){case O:return kn(n.children,a,o,t);case ce:u=8,a|=8;break;case ge:return e=vt(12,n,t,a|2),e.elementType=ge,e.lanes=o,e;case ne:return e=vt(13,n,t,a),e.elementType=ne,e.lanes=o,e;case Pe:return e=vt(19,n,t,a),e.elementType=Pe,e.lanes=o,e;case he:return Os(n,a,o,t);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case Fe:u=10;break e;case Ce:u=9;break e;case _e:u=11;break e;case He:u=14;break e;case ze:u=16,s=null;break e}throw Error(c(130,e==null?e:typeof e,""))}return t=vt(u,n,t,a),t.elementType=e,t.type=s,t.lanes=o,t}function kn(e,t,n,s){return e=vt(7,e,s,t),e.lanes=n,e}function Os(e,t,n,s){return e=vt(22,e,s,t),e.elementType=he,e.lanes=n,e.stateNode={isHidden:!1},e}function Xi(e,t,n){return e=vt(6,e,null,t),e.lanes=n,e}function Yi(e,t,n){return t=vt(4,e.children!==null?e.children:[],e.key,t),t.lanes=n,t.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},t}function Qm(e,t,n,s,a){this.tag=t,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=Sa(0),this.expirationTimes=Sa(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=Sa(0),this.identifierPrefix=s,this.onRecoverableError=a,this.mutableSourceEagerHydrationData=null}function Ji(e,t,n,s,a,o,u,h,f){return e=new Qm(e,t,n,h,f),t===1?(t=1,o===!0&&(t|=8)):t=0,o=vt(3,null,null,t),e.current=o,o.stateNode=e,o.memoizedState={element:s,isDehydrated:n,cache:null,transitions:null,pendingSuspenseBoundaries:null},di(o),e}function Xm(e,t,n){var s=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:z,key:s==null?null:""+s,children:e,containerInfo:t,implementation:n}}function mu(e){if(!e)return qt;e=e._reactInternals;e:{if(ln(e)!==e||e.tag!==1)throw Error(c(170));var t=e;do{switch(t.tag){case 3:t=t.stateNode.context;break e;case 1:if(et(t.type)){t=t.stateNode.__reactInternalMemoizedMergedChildContext;break e}}t=t.return}while(t!==null);throw Error(c(171))}if(e.tag===1){var n=e.type;if(et(n))return Ol(e,n,t)}return t}function hu(e,t,n,s,a,o,u,h,f){return e=Ji(n,s,!0,e,a,o,u,h,f),e.context=mu(null),n=e.current,s=Ye(),a=tn(n),o=Ft(s,a),o.callback=t??null,Yt(n,o,a),e.current.lanes=a,sr(e,a,s),rt(e,s),e}function Ws(e,t,n,s){var a=t.current,o=Ye(),u=tn(a);return n=mu(n),t.context===null?t.context=n:t.pendingContext=n,t=Ft(o,u),t.payload={element:e},s=s===void 0?null:s,s!==null&&(t.callback=s),e=Yt(a,t,u),e!==null&&(St(e,a,u,o),ys(e,a,u)),u}function Us(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function pu(e,t){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var n=e.retryLane;e.retryLane=n!==0&&n<t?n:t}}function Zi(e,t){pu(e,t),(e=e.alternate)&&pu(e,t)}function Ym(){return null}var fu=typeof reportError=="function"?reportError:function(e){console.error(e)};function eo(e){this._internalRoot=e}$s.prototype.render=eo.prototype.render=function(e){var t=this._internalRoot;if(t===null)throw Error(c(409));Ws(e,t,null,null)},$s.prototype.unmount=eo.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var t=e.containerInfo;vn(function(){Ws(null,e,null,null)}),t[Lt]=null}};function $s(e){this._internalRoot=e}$s.prototype.unstable_scheduleHydration=function(e){if(e){var t=Jo();e={blockedOn:null,target:e,priority:t};for(var n=0;n<$t.length&&t!==0&&t<$t[n].priority;n++);$t.splice(n,0,e),n===0&&tl(e)}};function to(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function Vs(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function gu(){}function Jm(e,t,n,s,a){if(a){if(typeof s=="function"){var o=s;s=function(){var b=Us(u);o.call(b)}}var u=hu(t,s,e,0,null,!1,!1,"",gu);return e._reactRootContainer=u,e[Lt]=u.current,yr(e.nodeType===8?e.parentNode:e),vn(),u}for(;a=e.lastChild;)e.removeChild(a);if(typeof s=="function"){var h=s;s=function(){var b=Us(f);h.call(b)}}var f=Ji(e,0,!1,null,null,!1,!1,"",gu);return e._reactRootContainer=f,e[Lt]=f.current,yr(e.nodeType===8?e.parentNode:e),vn(function(){Ws(t,f,n,s)}),f}function Hs(e,t,n,s,a){var o=n._reactRootContainer;if(o){var u=o;if(typeof a=="function"){var h=a;a=function(){var f=Us(u);h.call(f)}}Ws(t,u,e,a)}else u=Jm(n,t,e,a,s);return Us(u)}Xo=function(e){switch(e.tag){case 3:var t=e.stateNode;if(t.current.memoizedState.isDehydrated){var n=rr(t.pendingLanes);n!==0&&(Na(t,n|1),rt(t,Te()),(le&6)===0&&(qn=Te()+500,Qt()))}break;case 13:vn(function(){var s=It(e,1);if(s!==null){var a=Ye();St(s,e,1,a)}}),Zi(e,1)}},Ca=function(e){if(e.tag===13){var t=It(e,134217728);if(t!==null){var n=Ye();St(t,e,134217728,n)}Zi(e,134217728)}},Yo=function(e){if(e.tag===13){var t=tn(e),n=It(e,t);if(n!==null){var s=Ye();St(n,e,t,s)}Zi(e,t)}},Jo=function(){return fe},Zo=function(e,t){var n=fe;try{return fe=e,t()}finally{fe=n}},ya=function(e,t,n){switch(t){case"input":if(ua(e,n),t=n.name,n.type==="radio"&&t!=null){for(n=e;n.parentNode;)n=n.parentNode;for(n=n.querySelectorAll("input[name="+JSON.stringify(""+t)+'][type="radio"]'),t=0;t<n.length;t++){var s=n[t];if(s!==e&&s.form===e.form){var a=ls(s);if(!a)throw Error(c(90));jo(s),ua(s,a)}}}break;case"textarea":To(e,n);break;case"select":t=n.value,t!=null&&Nn(e,!!n.multiple,t,!1)}},Fo=Gi,zo=vn;var Zm={usingClientEntryPoint:!1,Events:[wr,Dn,ls,Do,Io,Gi]},Dr={findFiberByHostInstance:cn,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},eh={bundleType:Dr.bundleType,version:Dr.version,rendererPackageName:Dr.rendererPackageName,rendererConfig:Dr.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:ee.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=Uo(e),e===null?null:e.stateNode},findFiberByHostInstance:Dr.findFiberByHostInstance||Ym,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Gs=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Gs.isDisabled&&Gs.supportsFiber)try{$r=Gs.inject(eh),Ct=Gs}catch{}}return st.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Zm,st.createPortal=function(e,t){var n=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!to(t))throw Error(c(200));return Xm(e,t,null,n)},st.createRoot=function(e,t){if(!to(e))throw Error(c(299));var n=!1,s="",a=fu;return t!=null&&(t.unstable_strictMode===!0&&(n=!0),t.identifierPrefix!==void 0&&(s=t.identifierPrefix),t.onRecoverableError!==void 0&&(a=t.onRecoverableError)),t=Ji(e,1,!1,null,null,n,!1,s,a),e[Lt]=t.current,yr(e.nodeType===8?e.parentNode:e),new eo(t)},st.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var t=e._reactInternals;if(t===void 0)throw typeof e.render=="function"?Error(c(188)):(e=Object.keys(e).join(","),Error(c(268,e)));return e=Uo(t),e=e===null?null:e.stateNode,e},st.flushSync=function(e){return vn(e)},st.hydrate=function(e,t,n){if(!Vs(t))throw Error(c(200));return Hs(null,e,t,!0,n)},st.hydrateRoot=function(e,t,n){if(!to(e))throw Error(c(405));var s=n!=null&&n.hydratedSources||null,a=!1,o="",u=fu;if(n!=null&&(n.unstable_strictMode===!0&&(a=!0),n.identifierPrefix!==void 0&&(o=n.identifierPrefix),n.onRecoverableError!==void 0&&(u=n.onRecoverableError)),t=hu(t,null,e,1,n??null,a,!1,o,u),e[Lt]=t.current,yr(e),s)for(e=0;e<s.length;e++)n=s[e],a=n._getVersion,a=a(n._source),t.mutableSourceEagerHydrationData==null?t.mutableSourceEagerHydrationData=[n,a]:t.mutableSourceEagerHydrationData.push(n,a);return new $s(t)},st.render=function(e,t,n){if(!Vs(t))throw Error(c(200));return Hs(null,e,t,!1,n)},st.unmountComponentAtNode=function(e){if(!Vs(e))throw Error(c(40));return e._reactRootContainer?(vn(function(){Hs(null,null,e,!1,function(){e._reactRootContainer=null,e[Lt]=null})}),!0):!1},st.unstable_batchedUpdates=Gi,st.unstable_renderSubtreeIntoContainer=function(e,t,n,s){if(!Vs(n))throw Error(c(200));if(e==null||e._reactInternals===void 0)throw Error(c(38));return Hs(e,t,n,!1,s)},st.version="18.3.1-next-f1338f8080-20240426",st}var Nu;function uh(){if(Nu)return so.exports;Nu=1;function i(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(i)}catch(l){console.error(l)}}return i(),so.exports=ch(),so.exports}var Cu;function dh(){if(Cu)return Ks;Cu=1;var i=uh();return Ks.createRoot=i.createRoot,Ks.hydrateRoot=i.hydrateRoot,Ks}var mh=dh();class hh extends Error{constructor(c,d){super(c);vu(this,"status");this.status=d}}async function Ie(i,l){const c=await fetch(i,{...l,credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json",...l==null?void 0:l.headers}}),d=await c.json().catch(()=>({}));if(!c.ok)throw new hh(d.error||c.statusText||"Request failed",c.status);return d}const fo=()=>Ie("/auth/status"),ph=()=>Ie("/api/config"),ea=()=>Ie("/api/botstats"),fh=()=>Ie("/api/team"),gh=i=>Ie(`/api/team/${i}`),go=()=>Ie("/api/staff/me"),vh=(i,l)=>Ie("/api/staff/profile",{method:"POST",headers:l?{"X-CSRF-Token":l}:void 0,body:JSON.stringify(i)}),yh=(i,l)=>Ie("/api/staff/global-profile",{method:"POST",headers:l?{"X-CSRF-Token":l}:void 0,body:JSON.stringify(i)}),xh=()=>Ie("/api/commands"),vo=()=>Ie("/api/guilds"),_u=()=>Ie("/api/me/overview"),kh=i=>Ie(`/api/guild/${i}/overview`),wh=i=>Ie(`/api/guild/${i}/levels`),Tu=i=>Ie(`/api/guild/${i}/config`),Eu=i=>Ie(`/api/guild/${i}/resources`);function sa(i,l,c,d){return Ie(`/api/guild/${i}/config/${l}`,{method:"POST",headers:d?{"X-CSRF-Token":d}:void 0,body:JSON.stringify(c)})}function bh(i,l,c){return Ie(`/api/guild/${i}/config/profile`,{method:"POST",headers:c?{"X-CSRF-Token":c}:void 0,body:JSON.stringify(l)})}function $u(i){return i.replace(/\/+$/,"")||"/"}function Mu(i=window.location.pathname){const l=$u(i);return l==="/commands"?"commands":l==="/docs"?"docs":l.startsWith("/docs/")?"docs-detail":l==="/dashboard/staff"||l==="/dashboard/staff/"?"staff":l==="/dashboard"||l.startsWith("/dashboard/")?"dashboard":l==="/team"?"team":l.startsWith("/team/")?"team-member":l==="/privacy"?"privacy":l==="/terms"?"terms":l==="/community"?"community":l==="/donate"||l.startsWith("/donate")?"donate":l==="/transcript"||l.startsWith("/transcript/")?"transcript":l==="/changelog"?"changelog":l.startsWith("/changelog/")?"changelog-detail":"home"}function Xn(i,l="overview"){return i?`/dashboard/${i}/${l}`:"/dashboard"}function yo(){return"/dashboard/servers"}function Pu(){const i=$u(window.location.pathname).split("/").filter(Boolean),l=["overview","leveling","moderation","server","ai","customization"];return i[1]==="servers"?{view:"servers",guildId:null,section:"overview"}:!i[1]||i[1]==="staff"?{view:"overview",guildId:null,section:"overview"}:{view:"guild",guildId:i[1]||null,section:l.includes(i[2])?i[2]:"overview"}}function oe(i){i.startsWith("/")&&(window.history.pushState({},"",i),window.dispatchEvent(new PopStateEvent("popstate")),window.scrollTo({top:0,behavior:"smooth"}))}function Vu({onNavigate:i}){return r.jsxs("a",{className:"brand",href:"/",onClick:l=>{l.preventDefault(),i?i():oe("/")},children:[r.jsx("span",{className:"brand-mark",children:"n"}),r.jsx("span",{children:"niko"})]})}function Nt(){return r.jsxs("footer",{className:"site-footer",children:[r.jsx(Vu,{}),r.jsx("span",{children:"Built for communities that care."}),r.jsxs("div",{children:[r.jsx("a",{href:"/changelog",onClick:i=>{i.preventDefault(),oe("/changelog")},children:"Changelog"}),r.jsx("a",{href:"/privacy",onClick:i=>{i.preventDefault(),oe("/privacy")},children:"Privacy"}),r.jsx("a",{href:"/terms",onClick:i=>{i.preventDefault(),oe("/terms")},children:"Terms"}),r.jsx("a",{href:"/community",onClick:i=>{i.preventDefault(),oe("/community")},children:"Community Policy"}),r.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"GitHub"})]})]})}/**
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
 */const Nh=i=>{for(const l in i)if(l.startsWith("aria-")||l==="role"||l==="title")return!0;return!1},Ch=_.createContext({}),_h=()=>_.useContext(Ch),Th=_.forwardRef(({color:i,size:l,strokeWidth:c,absoluteStrokeWidth:d,className:m="",children:p,iconNode:g,...T},k)=>{const{size:D=24,strokeWidth:N=2,absoluteStrokeWidth:C=!1,color:L="currentColor",className:I=""}=_h()??{},A=d??C?Number(c??N)*24/Number(l??D):c??N;return _.createElement("svg",{ref:k,...oo,width:l??D??oo.width,height:l??D??oo.height,stroke:i??L,strokeWidth:A,className:Hu("lucide",I,m),...!p&&!Nh(T)&&{"aria-hidden":"true"},...T},[...g.map(([B,j])=>_.createElement(B,j)),...Array.isArray(p)?p:[p]])});/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Je=(i,l)=>{const c=_.forwardRef(({className:d,...m},p)=>_.createElement(Th,{ref:p,iconNode:l,className:Hu(`lucide-${jh(Lu(i))}`,`lucide-${i}`,d),...m}));return c.displayName=Lu(i),c};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Eh=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]],Mh=Je("arrow-right",Eh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ph=[["path",{d:"M12 5v16",key:"1f6ucr"}],["path",{d:"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z",key:"1fyvmf"}]],Ru=Je("book-open",Ph);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Lh=[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],lo=Je("chart-column",Lh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Rh=[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]],Ah=Je("external-link",Rh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Dh=[["rect",{width:"7",height:"7",x:"3",y:"3",rx:"1",key:"1g98yp"}],["rect",{width:"7",height:"7",x:"14",y:"3",rx:"1",key:"6d4xhi"}],["rect",{width:"7",height:"7",x:"14",y:"14",rx:"1",key:"nxv5o0"}],["rect",{width:"7",height:"7",x:"3",y:"14",rx:"1",key:"1bb6yr"}]],xo=Je("layout-grid",Dh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ih=[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]],Fh=Je("lock-keyhole",Ih);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const zh=[["path",{d:"m16 17 5-5-5-5",key:"1bji2h"}],["path",{d:"M21 12H9",key:"dn1m92"}],["path",{d:"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4",key:"1uf3rs"}]],Bh=Je("log-out",zh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Oh=[["path",{d:"M4 5h16",key:"1tepv9"}],["path",{d:"M4 12h16",key:"1lakjw"}],["path",{d:"M4 19h16",key:"1djgab"}]],Wh=Je("menu",Oh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Uh=[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]],$h=Je("search",Uh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Vh=[["path",{d:"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915",key:"1i5ecw"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]],qs=Je("settings",Vh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Hh=[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}]],co=Je("shield",Hh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Gh=[["path",{d:"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",key:"1s2grr"}],["path",{d:"M20 2v4",key:"1rf3ol"}],["path",{d:"M22 4h-4",key:"gwowj6"}],["circle",{cx:"4",cy:"20",r:"2",key:"6kqj1y"}]],Qs=Je("sparkles",Gh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Kh=[["path",{d:"M12 19h8",key:"baeox8"}],["path",{d:"m4 17 6-6-6-6",key:"1yngyt"}]],qh=Je("terminal",Kh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Qh=[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["path",{d:"M16 3.128a4 4 0 0 1 0 7.744",key:"16gr8j"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}]],Au=Je("users",Qh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Xh=[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]],Yh=Je("x",Xh),Jh={arrow:Mh,grid:xo,terminal:qh,chart:lo,shield:co,spark:Qs,users:Au,settings:qs,book:Ru,external:Ah,menu:Wh,close:Yh,lock:Fh,logout:Bh,search:$h,doc:Ru,utility:qs,icon_home:xo,icon_settings:qs,icon_economy:lo,icon_leveling:lo,icon_moderation:co,icon_automod:co,icon_heart:Qs,icon_utility:qs,icon_bot:Au,icon_ai:Qs,icon_lightbulb:Qs};function q({name:i,size:l,className:c=""}){const d=Jh[i]||xo;return r.jsx(d,{className:`icon ${c}`.trim(),"aria-hidden":"true",focusable:"false",strokeWidth:1.8,style:l?{width:l,height:l}:void 0})}let Du=null,uo=null;function aa(){const[i,l]=_.useState(Du);return _.useEffect(()=>{uo||(uo=ph().then(c=>Du=c)),uo.then(l).catch(()=>{})},[]),i}const Iu=[{label:"Home",path:"/",page:"home"},{label:"Commands",path:"/commands",page:"commands"},{label:"Docs",path:"/docs",page:"docs"},{label:"Team",path:"/team",page:"team"},{label:"Changelog",path:"/changelog",page:"changelog"}];function Ue({page:i}){const l=aa(),c=i==="dashboard",[d,m]=_.useState(!1),p=g=>T=>{T.preventDefault(),m(!1),oe(g)};return r.jsxs("header",{className:`site-header${c?" dashboard-header":""}`,children:[r.jsx(Vu,{onNavigate:()=>m(!1)}),!c&&r.jsx("nav",{className:"site-nav","aria-label":"Main navigation",children:Iu.map(g=>r.jsx("a",{className:i===g.page?"active":"","aria-current":i===g.page?"page":void 0,href:g.path,onClick:p(g.path),children:g.label},g.path))}),r.jsx("div",{className:"header-actions",children:c?r.jsxs("div",{className:"dashboard-menu",children:[r.jsxs("button",{className:"button button-small button-muted dashboard-menu-trigger",type:"button","aria-expanded":d,"aria-controls":"dashboard-navigation-menu",onClick:()=>m(g=>!g),children:[r.jsx(q,{name:d?"close":"menu"}),r.jsx("span",{children:"Menu"})]}),d&&r.jsxs("nav",{id:"dashboard-navigation-menu",className:"dashboard-menu-popover","aria-label":"Dashboard navigation",children:[r.jsx("span",{className:"dashboard-menu-label",children:"Navigate"}),Iu.map(g=>r.jsx("a",{href:g.path,onClick:p(g.path),children:g.label},g.path)),r.jsx("a",{className:"dashboard-menu-current",href:"/dashboard","aria-current":"page",onClick:p("/dashboard"),children:"Dashboard"})]})]}):r.jsxs(r.Fragment,{children:[r.jsxs("a",{className:"button button-small button-muted dashboard-link",href:"/dashboard",onClick:p("/dashboard"),children:["Dashboard ",r.jsx(q,{name:"arrow"})]}),r.jsx("a",{className:"button button-small button-primary",href:(l==null?void 0:l.invite_url)||"#",target:"_blank",rel:"noreferrer",children:"Add to Discord"})]})})]})}const Fu=typeof navigator<"u"?(navigator.language||"en").slice(0,2):"en";function ko(i){const l=i.description;if(typeof l=="string")return l;if(l&&typeof l=="object"){const c=l;if(c[Fu])return c[Fu];if(c.en)return c.en;const d=Object.values(c).find(m=>typeof m=="string"&&m.length>0);if(d)return d}return"A Niko command for your server."}const Zh=[{value:"all",label:"All commands"},{value:"slash",label:"Slash"},{value:"prefix",label:"Prefix"},{value:"hybrid",label:"Hybrid"},{value:"context",label:"Context menus"}],ta={slash:"Slash command",prefix:"Prefix command",hybrid:"Hybrid command",context:"Context menu"};function bn(i){return i.type&&i.type in ta?i.type:"slash"}function ep(i){return i.context_type==="user"?"Right-click a user":"Right-click a message"}function Gu(i){const l=bn(i);return l==="slash"?r.jsxs("code",{children:["/",i.name]}):l==="prefix"?r.jsxs("code",{children:[".",i.name]}):l==="hybrid"?r.jsxs(r.Fragment,{children:[r.jsxs("code",{children:["/",i.name]}),r.jsx("span",{className:"command-or",children:"or"}),r.jsxs("code",{children:[".",i.name]})]}):r.jsxs("code",{className:"context-invocation",children:[ep(i)," · ",i.name]})}function zu(i){return i!=null&&i.length?i:["Not specified"]}function tp({command:i,onClose:l}){_.useEffect(()=>{const g=T=>{T.key==="Escape"&&l()};return document.addEventListener("keydown",g),()=>document.removeEventListener("keydown",g)},[l]);const c=i.parameters||[],d=i.subcommands||[],m=zu(i.aliases),p=zu(i.permissions);return r.jsx("div",{className:"command-dialog-backdrop",role:"presentation",onMouseDown:g=>{g.currentTarget===g.target&&l()},children:r.jsxs("section",{className:"command-dialog",role:"dialog","aria-modal":"true","aria-labelledby":"command-dialog-title",children:[r.jsxs("header",{className:"command-dialog-header",children:[r.jsxs("div",{children:[r.jsxs("div",{className:"command-dialog-kicker",children:[i.category," · ",ta[bn(i)]]}),r.jsx("h2",{id:"command-dialog-title",children:Gu(i)})]}),r.jsx("button",{className:"dialog-close",type:"button",onClick:l,"aria-label":"Close command details",title:"Close command details",children:r.jsx(q,{name:"close"})})]}),r.jsxs("div",{className:"command-dialog-body",children:[r.jsx("p",{className:"command-dialog-description",children:ko(i)}),r.jsxs("div",{className:"command-detail-grid",children:[r.jsxs("section",{className:"command-detail-section command-detail-wide",children:[r.jsx("h3",{children:"Usage"}),r.jsx("code",{className:"command-usage",children:i.usage||`${bn(i)==="context"?i.name:`/${i.name}`}`})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Permissions"}),r.jsx("ul",{className:"command-detail-list",children:p.map(g=>r.jsx("li",{children:g},g))})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Aliases"}),r.jsx("ul",{className:"command-detail-list",children:m.map(g=>r.jsx("li",{children:r.jsx("code",{children:g==="Not specified"?g:`.${g}`})},g))})]})]}),!!c.length&&r.jsxs("section",{className:"command-detail-section command-parameters",children:[r.jsx("h3",{children:"Parameters"}),r.jsx("div",{className:"command-parameter-list",children:c.map(g=>r.jsxs("div",{className:"command-parameter",children:[r.jsxs("div",{className:"command-parameter-title",children:[r.jsx("code",{children:g.name}),r.jsxs("span",{children:[g.required?"Required":"Optional"," · ",g.type]})]}),r.jsx("p",{children:g.description||"No description provided."})]},g.name))})]}),!!d.length&&r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Subcommands"}),r.jsx("div",{className:"subcommand-list",children:d.map(g=>r.jsxs("code",{children:[i.name," ",g]},g))})]})]}),r.jsxs("footer",{className:"command-dialog-footer",children:[r.jsx("span",{children:"Command registry details are generated from the live bot."}),r.jsx("button",{className:"button button-primary button-small",type:"button",onClick:l,children:"Done"})]})]})})}function np(){const[i,l]=_.useState([]),[c,d]=_.useState(null),[m,p]=_.useState(""),[g,T]=_.useState("all"),[k,D]=_.useState("all"),[N,C]=_.useState(!0),[L,I]=_.useState("");_.useEffect(()=>{xh().then(l).catch(()=>I("The command registry is unavailable right now.")).finally(()=>C(!1))},[]),_.useEffect(()=>{if(!c)return;const j=document.body.style.overflow;return document.body.style.overflow="hidden",()=>{document.body.style.overflow=j}},[c]);const A=_.useMemo(()=>["all",...Array.from(new Set(i.map(j=>j.category))).sort()],[i]),B=i.filter(j=>{const J=`${j.name} ${ko(j)} ${j.category} ${ta[bn(j)]} ${j.context_type||""} ${(j.aliases||[]).join(" ")}`.toLowerCase();return(k==="all"||bn(j)===k)&&(g==="all"||j.category===g)&&J.includes(m.trim().toLowerCase())});return r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"commands"}),r.jsxs("main",{className:"shell page-main",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Reference library"}),r.jsxs("h1",{children:["Everything Niko",r.jsx("br",{}),r.jsx("em",{children:"knows how to do."})]}),r.jsx("p",{children:"Browse slash, prefix, hybrid, and context commands from the live bot registry. Select any command for permissions, aliases, parameters, usage, and subcommands."})]}),r.jsxs("div",{className:"command-toolbar",children:[r.jsxs("label",{className:"search-field",children:[r.jsx("span",{"aria-hidden":"true",children:"⌕"}),r.jsx("input",{value:m,onChange:j=>p(j.target.value),placeholder:"Search commands","aria-label":"Search commands"})]}),r.jsxs("div",{className:"command-filters",children:[r.jsx("div",{className:"filter-list","aria-label":"Command types",children:Zh.map(j=>r.jsx("button",{type:"button",className:k===j.value?"filter active":"filter","aria-pressed":k===j.value,onClick:()=>D(j.value),children:j.label},j.value))}),r.jsx("div",{className:"filter-list","aria-label":"Command categories",children:A.map(j=>r.jsx("button",{type:"button",className:g===j?"filter active":"filter","aria-pressed":g===j,onClick:()=>T(j),children:j==="all"?"All categories":j},j))})]})]}),r.jsxs("div",{className:"command-meta",children:[r.jsx("strong",{children:N?"…":B.length})," commands ",r.jsx("span",{children:"·"})," live bot registry ",r.jsx("span",{children:"·"})," select a card for details"]}),L&&r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Could not load commands"}),r.jsx("span",{children:L})]}),r.jsxs("div",{className:"commands-grid",children:[B.map(j=>r.jsxs("button",{className:"command-card",type:"button",onClick:()=>d(j),"aria-label":`View details for ${j.name}`,children:[r.jsxs("span",{className:"command-card-head",children:[r.jsx("span",{className:"command-name",children:Gu(j)}),r.jsx("span",{className:"command-type",children:ta[bn(j)]})]}),r.jsx("span",{className:"command-card-description",children:ko(j)}),r.jsxs("span",{className:"command-card-footer",children:[r.jsx("span",{className:"category-tag",children:j.category}),r.jsxs("span",{className:"command-expand",children:[r.jsx("span",{children:"Details"}),r.jsx(q,{name:"arrow",size:14})]})]})]},`${bn(j)}-${j.context_type||""}-${j.category}-${j.name}`)),!N&&!L&&!B.length&&r.jsx("div",{className:"empty-state",children:"No commands match that search."})]})]}),r.jsx(Nt,{}),c&&r.jsx(tp,{command:c,onClose:()=>d(null)})]})}function Me(i){return i==null?"—":new Intl.NumberFormat("en-US",{notation:i>9999?"compact":"standard"}).format(i)}function Ku(i){return(i==null?void 0:i.global_name)||(i==null?void 0:i.username)||"there"}function qu(i){return i.split(/\s+/).map(l=>l[0]).join("").slice(0,2).toUpperCase()}function bo({guild:i,className:l="guild-avatar"}){return r.jsx("span",{className:l,"aria-hidden":"true",children:i.icon_url?r.jsx("img",{src:i.icon_url,alt:""}):i.name.slice(0,1).toUpperCase()})}function Qu({user:i,className:l="avatar"}){const c=i.avatar?`https://cdn.discordapp.com/avatars/${i.id}/${i.avatar}.${i.avatar.startsWith("a_")?"gif":"png"}?size=64`:null;return r.jsx("span",{className:l,"aria-hidden":"true",children:c?r.jsx("img",{src:c,alt:""}):qu(i.global_name||i.username||"Niko")})}function rp({name:i,avatarUrl:l,className:c="member-avatar"}){return r.jsx("span",{className:c,"aria-hidden":"true",children:l?r.jsx("img",{src:l,alt:""}):qu(i)})}const sp=[["overview","Overview","grid","At a glance"],["leveling","Leveling","spark","Reward participation"],["moderation","Moderation","shield","Keep things steady"],["server","Server","settings","Manage server features"],["ai","AI controls","settings","Shape Niko’s voice"],["customization","Customization","paint","Niko’s server identity"]];function Xu({user:i,guilds:l,selectedGuild:c,view:d,section:m,stats:p,onHome:g,onServers:T,onGuildChange:k,onSectionChange:D,onRefresh:N,refreshing:C,staffRole:L,children:I}){const A=l.filter(S=>S.installed!==!1),B=(S=!1)=>r.jsx("nav",{className:S?"dash-nav dash-nav-mobile":"dash-nav","aria-label":"Server settings",children:sp.map(([V,ee,re])=>r.jsxs("button",{className:d==="guild"&&m===V?"active":"","aria-current":d==="guild"&&m===V?"page":void 0,onClick:()=>D(V),children:[r.jsx(q,{name:re}),r.jsx("span",{children:ee})]},V))}),j=(S=!1)=>r.jsxs("nav",{className:S?"dash-nav dash-primary-nav dash-nav-mobile":"dash-nav dash-primary-nav","aria-label":"Dashboard",children:[r.jsxs("button",{className:d==="overview"?"active":"","aria-current":d==="overview"?"page":void 0,onClick:g,children:[r.jsx(q,{name:"grid"}),r.jsx("span",{children:"My overview"})]}),r.jsxs("button",{className:d==="servers"?"active":"","aria-current":d==="servers"?"page":void 0,onClick:T,children:[r.jsx(q,{name:"users"}),r.jsx("span",{children:"My servers"})]}),L&&r.jsxs("button",{onClick:()=>oe("/dashboard/staff"),children:[r.jsx(q,{name:"shield"}),r.jsx("span",{children:"Staff workspace"})]})]}),J=()=>r.jsxs("div",{className:"dash-top-actions",children:[d==="guild"?r.jsxs("label",{className:"guild-switcher",children:[r.jsx("span",{className:"sr-only",children:"Switch server"}),r.jsxs("select",{value:(c==null?void 0:c.id)||"",onChange:S=>{const V=A.find(ee=>ee.id===S.target.value);V&&k(V)},children:[r.jsx("option",{value:"",disabled:!0,children:"Switch server"}),A.map(S=>r.jsx("option",{value:S.id,children:S.name},S.id))]})]}):r.jsxs("button",{className:"button button-muted button-small top-action",onClick:T,children:[r.jsx(q,{name:"users"})," Browse servers"]}),r.jsxs("button",{className:"button button-muted button-small top-action refresh-action",onClick:N,disabled:C,"aria-label":"Refresh dashboard data",children:[r.jsx(q,{name:"spark"})," ",C?"Refreshing…":"Refresh data"]}),d==="guild"&&r.jsxs("span",{className:"connection-chip",children:[r.jsx("span",{className:"status-dot"})," Connected"]}),r.jsxs("div",{className:"user-pill",children:[r.jsx(Qu,{user:i}),r.jsx("span",{children:Ku(i)})]}),r.jsx("a",{className:"logout-button",href:"/auth/logout","aria-label":"Log out",title:"Log out",children:r.jsx(q,{name:"logout"})})]});return r.jsxs("div",{className:"dashboard-layout",children:[r.jsxs("aside",{className:"dash-sidebar",children:[r.jsx("div",{className:"dash-mobile-controls",children:J()}),r.jsxs("div",{className:"side-rail-heading",children:[r.jsx("span",{className:"side-label",children:"Workspace"}),r.jsxs("span",{className:"rail-status",children:[r.jsx("span",{className:"status-dot"})," Live"]})]}),j(),d==="guild"&&c&&r.jsxs(r.Fragment,{children:[r.jsx("div",{className:"side-label side-label-settings",children:"Current server"}),r.jsxs("div",{className:"side-guild",children:[r.jsx(bo,{guild:c}),r.jsxs("span",{children:[r.jsx("strong",{children:c.name}),r.jsx("small",{children:"Live configuration"})]}),r.jsx("span",{className:"guild-presence",title:"Niko is connected",children:r.jsx("span",{className:"status-dot"})})]}),r.jsxs("div",{className:"side-settings-caption",children:[r.jsx("span",{children:"Settings map"}),r.jsx("small",{children:"Pick a room to tune"})]}),B()]}),r.jsxs("div",{className:"sidebar-bottom",children:[r.jsxs("span",{className:"online-label",children:[r.jsx("span",{className:"status-dot"})," Niko is online"]}),r.jsxs("small",{children:[Me(p==null?void 0:p.guild_count)," connected servers · v",(p==null?void 0:p.version)||"1.0"]}),r.jsxs("a",{href:"/",onClick:S=>{S.preventDefault(),oe("/")},children:["Back to public site ",r.jsx(q,{name:"arrow"})]})]})]}),r.jsxs("div",{className:"dash-content",children:[r.jsx(Ue,{page:"dashboard"}),r.jsx("div",{className:"dash-contextbar",children:J()}),r.jsx("div",{className:"mobile-primary-bar",children:j(!0)}),d==="guild"&&r.jsx("div",{className:"mobile-section-bar",children:B(!0)}),r.jsx("main",{className:"dash-main",children:I})]})]})}function on({eyebrow:i,title:l,text:c}){return r.jsxs("div",{className:"dash-heading",children:[r.jsxs("div",{className:"heading-meta",children:[r.jsx("div",{className:"eyebrow",children:i}),r.jsx("span",{className:"heading-context",children:"NIKO / CONTROL ROOM"})]}),r.jsx("h2",{children:l}),r.jsx("p",{children:c})]})}function Pt({label:i,value:l,note:c,accent:d=""}){return r.jsxs("div",{className:`dash-stat ${d}`,children:[r.jsx("span",{children:i}),r.jsx("strong",{children:l}),r.jsx("small",{children:c})]})}function ap({user:i,overview:l,guilds:c,onServers:d,onManage:m}){const p=c.filter(g=>g.installed!==!1);return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Personal overview",title:"Your Niko snapshot.",text:"Keep an eye on your progress, then jump into a server when you’re ready to tune the room."}),r.jsxs("div",{className:"overview-intro",children:[r.jsxs("div",{className:"profile-card",children:[r.jsx(Qu,{user:i,className:"profile-avatar"}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Signed in as"}),r.jsx("h3",{children:Ku(i)}),r.jsx("p",{children:"Personal economy profile"})]})]}),r.jsxs("button",{className:"button button-primary",onClick:d,children:["Manage a server ",r.jsx(q,{name:"arrow"})]})]}),r.jsxs("div",{className:"dash-stats overview-stats",children:[r.jsx(Pt,{label:"Net worth",value:Me(l==null?void 0:l.net_worth),note:"Across your Niko profile",accent:"accent-orange"}),r.jsx(Pt,{label:"In your wallet",value:Me(l==null?void 0:l.balance),note:"Ready to spend",accent:"accent-violet"}),r.jsx(Pt,{label:"In your vault",value:Me(l==null?void 0:l.bank),note:"Saved for later",accent:"accent-blue"}),r.jsx(Pt,{label:"Current level",value:Me(l==null?void 0:l.level),note:l!=null&&l.job?`Working as a ${l.job}`:"Keep showing up",accent:"accent-green"})]}),r.jsxs("div",{className:"dash-columns overview-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Progress"}),r.jsx("h3",{children:"Your momentum"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:"spark"})})]}),r.jsxs("div",{className:"metric-list",children:[r.jsxs("div",{children:[r.jsx("span",{children:"Daily streak"}),r.jsxs("strong",{children:[Me(l==null?void 0:l.daily_streak)," ",r.jsx("small",{children:"days"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Achievements"}),r.jsxs("strong",{children:[Me(l==null?void 0:l.achievements)," ",r.jsx("small",{children:"unlocked"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Total earned"}),r.jsxs("strong",{children:[Me(l==null?void 0:l.total_earned)," ",r.jsx("small",{children:"coins"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Economy standing"}),r.jsxs("strong",{children:[l!=null&&l.economy_rank?`#${Me(l.economy_rank)}`:"—"," ",r.jsx("small",{children:l!=null&&l.economy_profiles?`of ${Me(l.economy_profiles)}`:""})]})]})]})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Quick access"}),r.jsx("h3",{children:"Your servers"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:"users"})})]}),r.jsxs("div",{className:"mini-server-list",children:[p.slice(0,4).map(g=>r.jsxs("button",{onClick:()=>m(g),children:[r.jsx(bo,{guild:g}),r.jsx("span",{children:g.name}),r.jsx(q,{name:"arrow"})]},g.id)),!p.length&&r.jsx("p",{className:"empty-state compact",children:"Add Niko to a server to start managing it."})]}),r.jsxs("button",{className:"text-link overview-link",onClick:d,children:["View all servers ",r.jsx(q,{name:"arrow"})]})]})]})]})}function Bu({guild:i,onManage:l}){const c=i.installed!==!1;return r.jsxs("article",{className:"server-card",children:[r.jsxs("div",{className:"server-card-heading",children:[r.jsx(bo,{guild:i,className:"server-avatar"}),r.jsx("span",{className:"server-status",children:c?"Niko is installed":"Ready to add"})]}),r.jsx("h3",{children:i.name}),r.jsx("p",{children:c?"Open the dashboard to manage Niko’s features and settings.":"You have permission to manage this server. Add Niko to unlock its controls."}),c?r.jsxs("button",{className:"button button-muted button-small",onClick:()=>l(i),children:["Open settings ",r.jsx(q,{name:"arrow"})]}):r.jsxs("a",{className:"button button-primary button-small",href:i.invite_url||"#",target:"_blank",rel:"noreferrer",children:["Add Niko ",r.jsx(q,{name:"external"})]})]})}function ip({guilds:i,onManage:l}){const c=i.filter(m=>m.installed!==!1),d=i.filter(m=>m.installed===!1);return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Servers",title:"Choose where to work.",text:"Manage servers with Niko already installed, or add Niko to another server you can administer."}),r.jsxs("div",{className:"server-summary",children:[r.jsxs("div",{children:[r.jsx("strong",{children:Me(c.length)}),r.jsx("span",{children:"Connected to Niko"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:Me(d.length)}),r.jsx("span",{children:"Ready to add"})]}),r.jsxs("div",{className:"server-summary-note",children:[r.jsx(q,{name:"shield"}),r.jsx("span",{children:"Only servers where you have Manage Server access are shown."})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Connected"}),r.jsx("h3",{children:"Manage a server"})]}),r.jsx("span",{className:"section-count",children:c.length})]}),r.jsxs("div",{className:"server-grid",children:[c.map(m=>r.jsx(Bu,{guild:m,onManage:l},m.id)),!c.length&&r.jsxs("div",{className:"empty-state",children:[r.jsx("strong",{children:"No connected servers yet."}),r.jsx("span",{children:"Add Niko below, then come back here to manage it."})]})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Available to you"}),r.jsx("h3",{children:"Add Niko to a server"})]}),r.jsx("span",{className:"section-count",children:d.length})]}),r.jsxs("div",{className:"server-grid",children:[d.map(m=>r.jsx(Bu,{guild:m,onManage:l},m.id)),!d.length&&r.jsx("div",{className:"server-note",children:"Niko is already installed in every server you can manage."})]})]})]})}function Yu({rows:i}){return r.jsxs("div",{className:"rank-list",children:[i.slice(0,5).map((l,c)=>r.jsxs("div",{className:"rank-row",children:[r.jsx("span",{className:`rank rank-${c+1}`,children:String(c+1).padStart(2,"0")}),r.jsxs("span",{className:"rank-user",children:[r.jsx(rp,{name:l.display_name||l.username||"Unknown member",avatarUrl:l.avatar_url}),r.jsxs("span",{children:[r.jsx("strong",{children:l.display_name||l.username||"Unknown member"}),l.username&&l.display_name&&r.jsxs("small",{children:["@",l.username]})]})]}),r.jsxs("strong",{children:["Level ",Me(l.level),r.jsxs("small",{children:[Me(l.xp)," xp"]})]})]},`${l.user_id}-${c}`)),!i.length&&r.jsx("div",{className:"empty-state compact",children:"No data recorded yet."})]})}function op({overview:i}){return r.jsxs(r.Fragment,{children:[r.jsxs("div",{className:"guild-welcome",children:[r.jsxs("div",{children:[r.jsx("span",{className:"welcome-mark",children:r.jsx(q,{name:"grid"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server pulse"}),r.jsx("strong",{children:"Here’s what needs your attention."})]})]}),r.jsxs("span",{className:"welcome-time",children:["LIVE SIGNALS ",r.jsx("span",{className:"status-dot"})]})]}),r.jsx(on,{eyebrow:"Overview",title:"A quick read on your room.",text:"The important signals, without making you hunt for them."}),r.jsxs("div",{className:"dash-stats guild-overview-stats",children:[r.jsx(Pt,{label:"Warnings logged",value:Me(i.moderation.warn_count),note:"For this server",accent:"accent-blue"}),r.jsx(Pt,{label:"Automod",value:i.moderation.automod_active?"Active":"Quiet",note:"Protection status",accent:"accent-green"}),r.jsx(Pt,{label:"Level leaders",value:Me(i.leveling.top.length),note:"Members with recorded XP",accent:"accent-violet"})]}),r.jsxs("div",{className:"dash-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Community energy"}),r.jsx("h3",{children:"Top XP"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:"spark"})})]}),r.jsx(Yu,{rows:i.leveling.top})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server controls"}),r.jsx("h3",{children:"Manage the room"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:"settings"})})]}),r.jsxs("div",{className:"server-controls-body",children:[r.jsx("p",{children:"Use Server settings for prefixes, welcome messages, logs, and ticket panels."}),r.jsxs("span",{className:"text-link",children:["Open server settings ",r.jsx(q,{name:"arrow"})]})]})]})]})]})}function lp({rows:i,config:l,resources:c,csrfToken:d,guildId:m}){var p,g,T;return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Leveling",title:"Momentum people can see.",text:"Track the members turning up, and tune the pace to fit your server."}),r.jsxs("div",{className:"dash-stats",children:[r.jsx(Pt,{label:"Top level",value:String(((p=i[0])==null?void 0:p.level)||0),note:((g=i[0])==null?void 0:g.display_name)||((T=i[0])==null?void 0:T.username)||"No members yet",accent:"accent-violet"}),r.jsx(Pt,{label:"XP multiplier",value:`${(l==null?void 0:l.leveling.xp_multiplier)||1}×`,note:(l==null?void 0:l.leveling.xp_enabled)===!1?"XP disabled":"Currently active",accent:"accent-blue"}),r.jsx(Pt,{label:"Cooldown",value:`${(l==null?void 0:l.leveling.xp_cooldown)||0}s`,note:"Between XP awards",accent:"accent-green"})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Leaderboard"}),r.jsx("h3",{children:"XP leaders"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:"spark"})})]}),r.jsx(Yu,{rows:i})]}),r.jsx(mp,{guildId:m,config:l,resources:c,csrfToken:d})]})}const ia={saving:!1,message:"",error:""};function it({label:i,hint:l,children:c}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:i}),c,l&&r.jsx("small",{children:l})]})}function cp(i,l){const c=l?String(l):"",d=(i==null?void 0:i.channels)||[];return!c||d.some(m=>m.id===c)?d:[{id:c,name:`Saved channel · ${c}`},...d]}function oa({icon:i,label:l,title:c,text:d}){return r.jsxs("div",{className:"settings-intro",children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(q,{name:i})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:l}),r.jsx("strong",{children:c}),r.jsx("p",{children:d})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]})}function Sn({label:i,title:l,detail:c,icon:d}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:i}),r.jsx("h3",{children:l}),c&&r.jsx("p",{children:c})]}),d&&r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:d})})]})}function la({state:i}){return r.jsxs("div",{className:"setting-footer",children:[i.error?r.jsx("span",{className:"form-error",role:"alert",children:i.error}):r.jsx("span",{role:"status",children:i.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:i.saving,children:i.saving?"Saving…":"Save changes"})]})}function up({guildId:i,config:l,csrfToken:c}){var C,L,I;const[d,m]=_.useState({}),[p,g]=_.useState(ia);_.useEffect(()=>{const A=(l==null?void 0:l.moderation)||{};m({automod:{...A.automod||{}},spam_threshold:A.spam_threshold??6,spam_interval:A.spam_interval??7,max_mentions:A.max_mentions??5,antinuke:{...A.antinuke||{}},antiraid:{...A.antiraid||{}},antiraid_ext:{...A.antiraid_ext||{}}})},[l]);const T=(A,B,j)=>m(J=>({...J,[A]:{...J[A],[B]:j}})),k=A=>{A.preventDefault(),g({saving:!0,message:"",error:""}),sa(i,"automod",d,c).then(B=>{const j=B.config||{};m({automod:{...j.automod||{}},spam_threshold:j.spam_threshold??6,spam_interval:j.spam_interval??7,max_mentions:j.max_mentions??5,antinuke:{...j.antinuke||{}},antiraid:{...j.antiraid||{}},antiraid_ext:{...j.antiraid_ext||{}}}),g({saving:!1,message:"Moderation settings saved to Niko.",error:""})}).catch(B=>g({saving:!1,message:"",error:B instanceof Error?B.message:"Could not save settings."}))},D=[["antispam","Anti-spam","Detect repeated messages"],["antilink","Invite links","Remove Discord invite links"],["badwords","Blocked words","Filter words from the server list"],["massmention","Mass mentions","Limit mention floods"],["antinuke","Anti-nuke","Protect channels and roles"],["antiraid","Join raid protection","React to sudden join waves"],["antiraid_ext","External app protection","Detect user-installed app abuse"]],N=D.filter(([A])=>{var B;return!!((B=d.automod)!=null&&B[A])}).length;return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Moderation",title:"Keep the room feeling good.",text:"Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration."}),r.jsx(oa,{icon:"shield",label:"Protection desk",title:`${N} of ${D.length} safeguards active`,text:"Start with the essentials, then tune thresholds below when you know the room’s rhythm."}),r.jsxs("form",{onSubmit:k,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Protection rules",title:"AutoMod modules",detail:"Toggle only the responses you want Niko to handle.",icon:"shield"}),r.jsx("div",{className:"setting-list",children:D.map(([A,B,j])=>{var J;return r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:B}),r.jsx("small",{children:j})]}),r.jsx("input",{type:"checkbox",checked:!!((J=d.automod)!=null&&J[A]),onChange:S=>T("automod",A,S.target.checked)}),r.jsx("i",{"aria-hidden":"true"})]},A)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Thresholds",title:"Choose when protection steps in",detail:"These limits apply across the server."}),r.jsxs("div",{className:"form-grid",children:[r.jsx(it,{label:"Spam messages",hint:"Messages inside the spam interval",children:r.jsx("input",{type:"number",min:"1",max:"100",value:d.spam_threshold??6,onChange:A=>m({...d,spam_threshold:A.target.value})})}),r.jsx(it,{label:"Spam interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:d.spam_interval??7,onChange:A=>m({...d,spam_interval:A.target.value})})}),r.jsx(it,{label:"Maximum mentions",children:r.jsx("input",{type:"number",min:"1",max:"100",value:d.max_mentions??5,onChange:A=>m({...d,max_mentions:A.target.value})})}),r.jsx(it,{label:"Anti-raid joins",hint:"Joins inside the join interval",children:r.jsx("input",{type:"number",min:"1",max:"1000",value:((C=d.antiraid)==null?void 0:C.join_threshold)??10,onChange:A=>T("antiraid","join_threshold",A.target.value)})}),r.jsx(it,{label:"Anti-raid interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:((L=d.antiraid)==null?void 0:L.join_interval)??10,onChange:A=>T("antiraid","join_interval",A.target.value)})}),r.jsx(it,{label:"Anti-raid action",children:r.jsxs("select",{value:((I=d.antiraid)==null?void 0:I.action)??"kick",onChange:A=>T("antiraid","action",A.target.value),children:[r.jsx("option",{value:"kick",children:"Kick"}),r.jsx("option",{value:"ban",children:"Ban"}),r.jsx("option",{value:"softban",children:"Soft-ban"}),r.jsx("option",{value:"slowmode",children:"Slowmode"}),r.jsx("option",{value:"lockdown",children:"Lockdown"})]})})]}),r.jsx(la,{state:p})]})]})]})}function dp({guildId:i,config:l,csrfToken:c}){const[d,m]=_.useState({personality:"cafe",enabled:!0,ai_actions_experiment:!1,better_context_experiment:!1}),[p,g]=_.useState(ia);_.useEffect(()=>{const k=(l==null?void 0:l.ai)||{};m({personality:k.personality||"cafe",enabled:k.enabled!=="False"&&k.enabled!==!1,ai_actions_experiment:k.ai_actions_experiment===!0||k.ai_actions_experiment==="True",better_context_experiment:k.better_context_experiment===!0||k.better_context_experiment==="True"})},[l]);const T=k=>{k.preventDefault(),g({saving:!0,message:"",error:""}),sa(i,"ai",d,c).then(D=>{const N=D.config||{};m({personality:N.personality==="normal"?"normal":"cafe",enabled:N.enabled!=="False"&&N.enabled!==!1,ai_actions_experiment:N.ai_actions_experiment===!0||N.ai_actions_experiment==="True",better_context_experiment:N.better_context_experiment===!0||N.better_context_experiment==="True"}),g({saving:!1,message:"AI settings saved to Niko.",error:""})}).catch(D=>g({saving:!1,message:"",error:D instanceof Error?D.message:"Could not save settings."}))};return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"AI controls",title:"Give Niko the right tone.",text:"AI is optional, configurable per server, and designed to stay out of the way when the room does not need it."}),r.jsx(oa,{icon:"settings",label:"Conversation desk",title:d.enabled?"Niko is ready to respond":"Niko is staying quiet",text:"Choose a voice that fits your community. You can change this without affecting other servers."}),r.jsxs("form",{onSubmit:T,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Conversation",title:"Core settings",detail:"Decide when Niko joins the conversation.",icon:"settings"}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable AI chat"}),r.jsx("small",{children:"Respond when Niko is mentioned"})]}),r.jsx("input",{type:"checkbox",checked:d.enabled,onChange:k=>m({...d,enabled:k.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"personality-options",children:[r.jsxs("button",{type:"button",className:d.personality==="cafe"?"personality active":"personality",onClick:()=>m({...d,personality:"cafe"}),children:[r.jsx("span",{className:"personality-mark",children:"n"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Café"}),r.jsx("small",{children:"Warm, playful, familiar"})]})]}),r.jsxs("button",{type:"button",className:d.personality==="normal"?"personality active":"personality",onClick:()=>m({...d,personality:"normal"}),children:[r.jsx("span",{className:"personality-mark",children:"—"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Normal"}),r.jsx("small",{children:"Clear and straightforward"})]})]})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Experiments",title:"Optional context",detail:"Try new capabilities when your team is ready."}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Better context"}),r.jsx("small",{children:"Use the last five channel messages"})]}),r.jsx("input",{type:"checkbox",checked:d.better_context_experiment,onChange:k=>m({...d,better_context_experiment:k.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"AI actions"}),r.jsx("small",{children:"Allow confirmed actions requested in chat"})]}),r.jsx("input",{type:"checkbox",checked:d.ai_actions_experiment,onChange:k=>m({...d,ai_actions_experiment:k.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsx(la,{state:p})]})]})]})}function mp({guildId:i,config:l,resources:c,csrfToken:d}){const m=(l==null?void 0:l.leveling)||{},[p,g]=_.useState({xp_enabled:!0,xp_multiplier:1,xp_cooldown:0,level_up_channel:"",level_up_message:""}),[T,k]=_.useState(ia);_.useEffect(()=>g({xp_enabled:m.xp_enabled!==!1,xp_multiplier:m.xp_multiplier??1,xp_cooldown:m.xp_cooldown??0,level_up_channel:m.level_up_channel?String(m.level_up_channel):"",level_up_message:m.level_up_message||""}),[l]);const D=C=>{C.preventDefault(),k({saving:!0,message:"",error:""}),sa(i,"leveling",p,d).then(L=>{const I=L.config||{};g({xp_enabled:I.xp_enabled!==!1,xp_multiplier:I.xp_multiplier??1,xp_cooldown:I.xp_cooldown??0,level_up_channel:I.level_up_channel?String(I.level_up_channel):"",level_up_message:I.level_up_message||""}),k({saving:!1,message:"Leveling settings saved to Niko.",error:""})}).catch(L=>k({saving:!1,message:"",error:L instanceof Error?L.message:"Could not save settings."}))},N=cp(c,p.level_up_channel);return r.jsxs(r.Fragment,{children:[r.jsx(oa,{icon:"spark",label:"Participation desk",title:p.xp_enabled?"XP is flowing":"XP is paused",text:"Set a pace that rewards regulars without turning every message into a transaction."}),r.jsx("form",{onSubmit:D,className:"settings-stack",children:r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Leveling settings",title:"Shape the pace",detail:"These controls apply to every member in this server.",icon:"spark"}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable XP"}),r.jsx("small",{children:"Track activity and award levels"})]}),r.jsx("input",{type:"checkbox",checked:p.xp_enabled,onChange:C=>g({...p,xp_enabled:C.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"form-grid",children:[r.jsx(it,{label:"XP multiplier",hint:"From 0.1× to 10×",children:r.jsx("input",{type:"number",min:"0.1",max:"10",step:"0.1",value:p.xp_multiplier,onChange:C=>g({...p,xp_multiplier:C.target.value})})}),r.jsx(it,{label:"Cooldown (seconds)",hint:"0 disables the cooldown",children:r.jsx("input",{type:"number",min:"0",max:"86400",value:p.xp_cooldown,onChange:C=>g({...p,xp_cooldown:C.target.value})})}),r.jsx(it,{label:"Level-up channel",children:r.jsxs("select",{value:p.level_up_channel,onChange:C=>g({...p,level_up_channel:C.target.value}),children:[r.jsx("option",{value:"",children:"Same channel"}),N.map(C=>r.jsxs("option",{value:C.id,children:["#",C.name]},C.id))]})}),r.jsx(it,{label:"Level-up message",hint:"Use {mention}, {level}, {name}, or {guild}",children:r.jsx("textarea",{rows:3,maxLength:1e3,value:p.level_up_message,onChange:C=>g({...p,level_up_message:C.target.value}),placeholder:"Leave blank for Niko's default message"})})]}),r.jsx(la,{state:T})]})})]})}function hp({guildId:i,config:l,csrfToken:c}){var D;const d=((D=l==null?void 0:l.server)==null?void 0:D.profile)||{},[m,p]=_.useState({display_name:d.display_name||"",bio:d.bio||"",avatar_url:d.avatar_url||"",banner_url:d.banner_url||""}),[g,T]=_.useState(ia);_.useEffect(()=>{var C;const N=((C=l==null?void 0:l.server)==null?void 0:C.profile)||{};p({display_name:N.display_name||"",bio:N.bio||"",avatar_url:N.avatar_url||"",banner_url:N.banner_url||""})},[l]);const k=N=>{N.preventDefault(),T({saving:!0,message:"",error:""}),bh(i,{display_name:m.display_name||null,bio:m.bio||null,avatar_url:m.avatar_url||null,banner_url:m.banner_url||null},c).then(C=>{const L=C.profile||{};p({display_name:L.display_name||"",bio:L.bio||"",avatar_url:L.avatar_url||"",banner_url:L.banner_url||""}),T({saving:!1,message:"Bot profile updated.",error:""})}).catch(C=>T({saving:!1,message:"",error:C instanceof Error?C.message:"Could not save profile."}))};return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Customization",title:"Niko's server presence.",text:"Change how Niko appears in this server. Display name, avatar, banner, and bio are all per-server."}),r.jsx(oa,{icon:"paint",label:"Identity desk",title:"Server-specific identity",text:"Each server can have its own Niko persona. Changes apply only to this server."}),r.jsxs("form",{onSubmit:k,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Display name",title:"How Niko appears",detail:"Set the name members see for Niko in this server. Leave blank to use the default.",icon:"settings"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(it,{label:"Display name",hint:"32 characters or fewer",children:r.jsx("input",{value:m.display_name,maxLength:32,onChange:N=>p({...m,display_name:N.target.value}),placeholder:"Niko"})}),r.jsx(it,{label:"Bio",hint:"190 characters or fewer",children:r.jsx("input",{value:m.bio,maxLength:190,onChange:N=>p({...m,bio:N.target.value}),placeholder:"A warm Discord companion"})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Sn,{label:"Server avatar & banner",title:"Visual identity",detail:"Provide HTTPS image URLs. Images are uploaded to Discord when saved.",icon:"paint"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(it,{label:"Avatar URL",hint:"Square image, 512×512 recommended",children:r.jsx("input",{type:"url",value:m.avatar_url,onChange:N=>p({...m,avatar_url:N.target.value}),placeholder:"https://cdn.example.com/avatar.png"})}),r.jsx(it,{label:"Banner URL",hint:"Wide image, 960×540 recommended",children:r.jsx("input",{type:"url",value:m.banner_url,onChange:N=>p({...m,banner_url:N.target.value}),placeholder:"https://cdn.example.com/banner.png"})})]}),r.jsx("p",{className:"form-hint",children:"Images are fetched, validated, and uploaded to Discord. Maximum 8 MB each. Supported formats: PNG, JPG, GIF."})]}),r.jsx(la,{state:g})]})]})}const pp={saving:!1,message:"",error:""};function at({label:i,hint:l,children:c}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:i}),c,l&&r.jsx("small",{children:l})]})}function Xs({label:i,title:l,detail:c,icon:d}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:i}),r.jsx("h3",{children:l}),r.jsx("p",{children:c})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(q,{name:d})})]})}function fp({state:i}){return r.jsxs("div",{className:"setting-footer",children:[i.error?r.jsx("span",{className:"form-error",role:"alert",children:i.error}):r.jsx("span",{role:"status",children:i.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:i.saving,children:i.saving?"Saving...":"Save server settings"})]})}const gp=[["moderation","Moderation"],["automod","AutoMod"],["messages","Messages"],["channels","Channels"],["members","Members"],["captcha","Captcha"],["invites","Invites"],["roles","Roles"],["server","Server"],["voice","Voice"]];function vp(i,l){var c;return l?((c=i==null?void 0:i.channels.find(d=>d.id===String(l)))==null?void 0:c.name)||`Saved channel · ${l}`:"Not set"}function Ys(i,l){const c=l?String(l):"",d=(i==null?void 0:i.channels)||[];return!c||d.some(m=>m.id===c)?d:[{id:c,name:`Saved channel · ${c}`},...d]}function Ou(i,l=[]){const c=(i==null?void 0:i.roles)||[],d=new Set(c.map(p=>p.id));return[...l.map(String).filter((p,g,T)=>p&&!d.has(p)&&T.indexOf(p)===g).map(p=>({id:p,name:`Unavailable role (${p})`})),...c]}function mo(i){var d,m;const l=(i==null?void 0:i.onboarding)||{},c=(i==null?void 0:i.tickets)||{};return{prefixes:((d=i==null?void 0:i.prefixes)!=null&&d.length?i.prefixes:["."]).join(`
`),welcome_channel:l.welcome_channel?String(l.welcome_channel):"",welcome_title:l.welcome_title||"",welcome_description:l.welcome_description||"",welcome_color:l.welcome_color===null||l.welcome_color===void 0?"5865F2":l.welcome_color.toString(16).padStart(6,"0"),welcome_image:l.welcome_image||"",rules_channel:l.rules_channel?String(l.rules_channel):"",rules_text:l.rules_text||"",rules_role_id:l.rules_role_id?String(l.rules_role_id):"",logging:Object.fromEntries(Object.entries((i==null?void 0:i.logging)||{}).map(([p,g])=>[p,g==null?"":String(g)])),disabled_logging:[...((m=i==null?void 0:i.logging)==null?void 0:m.disabled)||[]].map(String),panel_title:c.panel_title||"",panel_description:c.panel_description||"",panel_categories:(c.panel_categories||[]).join(`
`),panel_channel_id:c.panel_channel_id?String(c.panel_channel_id):"",support_roles:[...c.support_roles||[]].map(String)}}function yp({guildId:i,config:l,resources:c,csrfToken:d}){const[m,p]=_.useState(()=>mo(l==null?void 0:l.server)),[g,T]=_.useState(pp);_.useEffect(()=>{l!=null&&l.server&&p(mo(l.server))},[l]);const k=(S,V)=>p(ee=>({...ee,[S]:V})),D=(S,V)=>p(ee=>({...ee,logging:{...ee.logging,[S]:V}})),N=S=>p(V=>({...V,disabled_logging:V.disabled_logging.includes(S)?V.disabled_logging.filter(ee=>ee!==S):[...V.disabled_logging,S]})),C=S=>{S.preventDefault(),T({saving:!0,message:"",error:""});const V=m.prefixes.split(/\r?\n|,/).map(re=>re.trim()).filter(Boolean),ee=m.panel_categories.split(/\r?\n|,/).map(re=>re.trim()).filter(Boolean);sa(i,"server",{prefixes:V,onboarding:{welcome_channel:m.welcome_channel,welcome_title:m.welcome_title,welcome_description:m.welcome_description,welcome_color:m.welcome_color,welcome_image:m.welcome_image,rules_channel:m.rules_channel,rules_text:m.rules_text,rules_role_id:m.rules_role_id},logging:{...m.logging,disabled:m.disabled_logging},tickets:{panel_title:m.panel_title,panel_description:m.panel_description,panel_categories:ee,panel_channel_id:m.panel_channel_id,support_roles:m.support_roles}},d).then(re=>{p(mo(re.config)),T({saving:!1,message:"Server settings saved to Niko.",error:""})}).catch(re=>T({saving:!1,message:"",error:re instanceof Error?re.message:"Could not save server settings."}))},L=m.welcome_channel,I=m.panel_channel_id,A=Ys(c,m.welcome_channel),B=Ys(c,m.rules_channel),j=Ys(c,m.panel_channel_id),J=Ou(c,m.support_roles);return r.jsxs(r.Fragment,{children:[r.jsx(on,{eyebrow:"Server settings",title:"Make Niko fit your room.",text:"Manage the settings that shape how Niko behaves in this server. Economy balances remain global to each user and are not configured here."}),r.jsxs("div",{className:"settings-intro",children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(q,{name:"settings"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server control room"}),r.jsxs("strong",{children:[m.prefixes.split(/\r?\n|,/).filter(Boolean).length||0," command prefixes configured"]}),r.jsx("p",{children:"Welcome flows, log destinations, and ticket panels all live here."})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]}),r.jsxs("form",{onSubmit:C,className:"settings-stack server-settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Xs,{label:"Commands",title:"Prefixes",detail:"Use one prefix per line. Niko will respond to all of them.",icon:"terminal"}),r.jsx(at,{label:"Command prefixes",hint:"The default prefix is .",children:r.jsx("textarea",{rows:3,maxLength:200,value:m.prefixes,onChange:S=>k("prefixes",S.target.value),placeholder:".\\n!"})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Xs,{label:"Welcome flow",title:"Welcome and rules",detail:"Choose where new members see your welcome message and rules.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(at,{label:"Welcome channel",children:r.jsxs("select",{value:L,onChange:S=>k("welcome_channel",S.target.value),children:[r.jsx("option",{value:"",children:"Disabled"}),A.map(S=>r.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),r.jsx(at,{label:"Welcome title",children:r.jsx("input",{value:m.welcome_title,maxLength:200,onChange:S=>k("welcome_title",S.target.value),placeholder:"Welcome to the server"})}),r.jsx(at,{label:"Welcome message",hint:"Supports {user} and {name}",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:m.welcome_description,onChange:S=>k("welcome_description",S.target.value),placeholder:"Welcome {user}!"})}),r.jsx(at,{label:"Accent color",hint:"Hex color, for example 5865F2",children:r.jsx("input",{value:m.welcome_color,maxLength:7,onChange:S=>k("welcome_color",S.target.value),placeholder:"5865F2"})}),r.jsx(at,{label:"Welcome image URL",children:r.jsx("input",{type:"url",value:m.welcome_image,onChange:S=>k("welcome_image",S.target.value),placeholder:"https://..."})}),r.jsx(at,{label:"Rules channel",children:r.jsxs("select",{value:m.rules_channel,onChange:S=>k("rules_channel",S.target.value),children:[r.jsx("option",{value:"",children:"Not configured"}),B.map(S=>r.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),r.jsx(at,{label:"Rules text",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:m.rules_text,onChange:S=>k("rules_text",S.target.value),placeholder:"Write the rules members should acknowledge."})}),r.jsx(at,{label:"Role after rules acknowledgment",children:r.jsxs("select",{value:m.rules_role_id,onChange:S=>k("rules_role_id",S.target.value),children:[r.jsx("option",{value:"",children:"No role"}),Ou(c,m.rules_role_id?[m.rules_role_id]:[]).map(S=>r.jsxs("option",{value:S.id,children:["@",S.name]},S.id))]})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Xs,{label:"Audit trail",title:"Logging destinations",detail:"Pick a channel for each event type and disable categories you do not need.",icon:"book"}),r.jsx("div",{className:"server-logging-list",children:gp.map(([S,V])=>{const ee=Ys(c,m.logging[S]);return r.jsxs("div",{className:"server-logging-row",children:[r.jsxs("label",{className:"form-field",children:[r.jsxs("span",{className:"form-label",children:[V," logs"]}),r.jsxs("select",{value:String(m.logging[S]||""),onChange:re=>D(S,re.target.value),children:[r.jsx("option",{value:"",children:"Not set"}),ee.map(re=>r.jsxs("option",{value:re.id,children:["#",re.name]},re.id))]})]}),r.jsxs("label",{className:"setting-row compact-setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enabled"}),r.jsx("small",{children:vp(c,m.logging[S])})]}),r.jsx("input",{type:"checkbox",checked:!m.disabled_logging.includes(S),onChange:()=>N(S)}),r.jsx("i",{"aria-hidden":"true"})]})]},S)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Xs,{label:"Support desk",title:"Ticket panel",detail:"Configure the public panel and decide who can handle tickets.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(at,{label:"Panel title",children:r.jsx("input",{value:m.panel_title,maxLength:200,onChange:S=>k("panel_title",S.target.value),placeholder:"Open a Ticket"})}),r.jsx(at,{label:"Panel channel",children:r.jsxs("select",{value:I,onChange:S=>k("panel_channel_id",S.target.value),children:[r.jsx("option",{value:"",children:"Keep current panel channel"}),j.map(S=>r.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),r.jsx(at,{label:"Panel description",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:m.panel_description,onChange:S=>k("panel_description",S.target.value),placeholder:"Tell members what the ticket panel is for."})}),r.jsx(at,{label:"Ticket categories",hint:"One category per line",children:r.jsx("textarea",{rows:4,value:m.panel_categories,onChange:S=>k("panel_categories",S.target.value),placeholder:"General\\nSupport\\nReports"})}),r.jsx(at,{label:"Support roles",hint:"Hold Ctrl/Cmd to select more than one",children:r.jsx("select",{multiple:!0,value:m.support_roles,onChange:S=>k("support_roles",Array.from(S.target.selectedOptions,V=>V.value)),children:J.map(S=>r.jsxs("option",{value:S.id,children:["@",S.name]},S.id))})})]}),r.jsx("p",{className:"form-hint",children:"Saving panel settings updates the existing posted panel when Niko can find its saved message."})]}),r.jsx(fp,{state:g})]})]})}function xp({auth:i}){const l=aa();return r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"n"}),r.jsx("div",{className:"eyebrow",children:"Private workspace"}),r.jsxs("h1",{children:["Settle in, ",r.jsx("em",{children:"admin."})]}),r.jsx("p",{children:"Sign in with Discord to see your Niko profile and manage the servers you look after."}),i.oauth_available?r.jsxs("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard",children:[r.jsx(q,{name:"lock"})," Continue with Discord ",r.jsx(q,{name:"arrow"})]}):r.jsxs("div",{className:"notice warning",children:["Discord login is not configured yet. Add ",r.jsx("code",{children:"DISCORD_CLIENT_SECRET"})," to the environment and restart the bot."]}),!l&&r.jsx("p",{className:"form-hint",children:"The public bot configuration is still loading."}),r.jsx("a",{className:"back-link",href:"/",onClick:c=>{c.preventDefault(),oe("/")},children:"Return to public site"})]})})]})}function kp({section:i,guild:l,stats:c,csrfToken:d,refreshToken:m}){const[p,g]=_.useState(null),[T,k]=_.useState([]),[D,N]=_.useState(null),[C,L]=_.useState(null),[I,A]=_.useState(!0),[B,j]=_.useState("");return _.useEffect(()=>{A(!0),j(""),(i==="overview"?kh(l.id).then(g):i==="leveling"?Promise.all([wh(l.id),Tu(l.id),Eu(l.id)]).then(([S,V,ee])=>{k(S),N(V),L(ee)}):Promise.all([Tu(l.id),Eu(l.id)]).then(([S,V])=>{N(S),L(V)})).catch(S=>j(S instanceof Error?S.message:"This server could not be loaded.")).finally(()=>A(!1))},[l.id,i,m]),I?r.jsxs("div",{className:"section-loading section-skeleton",role:"status","aria-label":`Loading ${i}`,children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsxs("span",{children:["Loading ",i,"..."]})]}):B?r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Couldn’t load this page."}),r.jsx("span",{children:B}),r.jsx("button",{className:"button button-muted",onClick:()=>window.location.reload(),children:"Try again"})]}):i==="overview"&&p?r.jsx(op,{overview:p}):i==="leveling"?r.jsx(lp,{guildId:l.id,rows:T,config:D,resources:C,csrfToken:d}):i==="moderation"?r.jsx(up,{guildId:l.id,config:D,csrfToken:d}):i==="server"?r.jsx(yp,{guildId:l.id,config:D,resources:C,csrfToken:d}):i==="customization"?r.jsx(hp,{guildId:l.id,config:D,csrfToken:d}):r.jsx(dp,{guildId:l.id,config:D,csrfToken:d})}function wp(){return r.jsxs("div",{className:"section-loading section-skeleton dashboard-loading",role:"status",children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"Preparing your dashboard..."})]})}function bp(){aa();const[i,l]=_.useState(Pu),[c,d]=_.useState(null),[m,p]=_.useState(null),[g,T]=_.useState(null),[k,D]=_.useState([]),[N,C]=_.useState(null),[L,I]=_.useState(!0),[A,B]=_.useState(""),[j,J]=_.useState(0),[S,V]=_.useState(!1),[ee,re]=_.useState(null);if(_.useEffect(()=>{const ne=()=>l(Pu());return window.addEventListener("popstate",ne),()=>window.removeEventListener("popstate",ne)},[]),_.useEffect(()=>{I(!0),Promise.all([fo(),ea()]).then(([ne,Pe])=>(d(ne),p(Pe),ne.authenticated?Promise.all([_u(),vo(),go().catch(()=>null)]).then(([He,ze,he])=>{T(He),D(ze),re((he==null?void 0:he.role)||null)}):null)).catch(ne=>B(ne instanceof Error?ne.message:"Dashboard unavailable")).finally(()=>I(!1))},[]),_.useEffect(()=>{if(i.view!=="guild"){C(null);return}const ne=k.find(Pe=>Pe.id===i.guildId&&Pe.installed!==!1);ne?(C(ne),localStorage.setItem("niko-guild",ne.id)):i.guildId&&k.length&&oe(yo())},[k,i.guildId,i.view]),L||!c)return r.jsxs("div",{className:"dashboard-state",children:[r.jsx("div",{className:"loading-ring"}),r.jsx("p",{children:"Connecting to Niko…"})]});if(A)return r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Connection issue"}),r.jsxs("h1",{children:["Couldn’t load",r.jsx("br",{}),r.jsx("em",{children:"your workspace."})]}),r.jsx("p",{children:A}),r.jsxs("button",{className:"button button-primary",onClick:()=>window.location.reload(),children:["Try again ",r.jsx(q,{name:"arrow"})]})]})})]});if(!c.authenticated)return r.jsx(xp,{auth:c});const z=ne=>{ne.installed!==!1&&(localStorage.setItem("niko-guild",ne.id),oe(Xn(ne.id,i.section)))},O=ne=>{ne.installed!==!1&&(localStorage.setItem("niko-guild",ne.id),oe(Xn(ne.id,"overview")))},ce=ne=>{oe(N?Xn(N.id,ne):Xn())},ge=()=>oe(Xn()),Fe=()=>oe(yo()),Ce=async()=>{if(!S){V(!0);try{const[ne,Pe]=await Promise.all([fo(),ea()]);if(d(ne),p(Pe),ne.authenticated){const[He,ze,he]=await Promise.all([_u(),vo(),go().catch(()=>null)]);T(He),D(ze),re((he==null?void 0:he.role)||null)}J(He=>He+1),B("")}catch(ne){B(ne instanceof Error?ne.message:"Dashboard refresh failed")}finally{V(!1)}}};let _e;return i.view==="servers"?_e=r.jsx(ip,{guilds:k,onManage:O}):i.view==="guild"?_e=N?r.jsx(kp,{section:i.section,guild:N,stats:m,csrfToken:c.csrf_token,refreshToken:j},`${N.id}-${i.section}`):r.jsx(wp,{}):_e=r.jsx(ap,{user:c.user,overview:g,guilds:k,onServers:Fe,onManage:O}),r.jsx(Xu,{user:c.user,guilds:k,selectedGuild:N,view:i.view,section:i.section,stats:m,onHome:ge,onServers:Fe,onGuildChange:z,onSectionChange:ce,onRefresh:Ce,refreshing:S,staffRole:ee,children:_e})}function jp({value:i,onChange:l,placeholder:c="Search documentation...",onFocus:d,onBlur:m}){const[p,g]=_.useState(!1),T=_.useRef(null),[k,D]=_.useState(!1);_.useEffect(()=>{const A=B=>{var j;(B.metaKey||B.ctrlKey)&&B.key==="k"&&(B.preventDefault(),(j=T.current)==null||j.focus())};return document.addEventListener("keydown",A),()=>document.removeEventListener("keydown",A)},[]);const N=()=>{g(!0),D(!0),d==null||d()},C=()=>{g(!1),setTimeout(()=>D(!1),200),m==null||m()},L=A=>{l(A.target.value)},I=A=>{var B;A.key==="Escape"&&((B=T.current)==null||B.blur())};return r.jsxs("div",{className:`doc-search-bar ${k?"expanded":""}`,children:[r.jsxs("div",{className:"search-input-wrapper",children:[r.jsx(q,{name:"search",className:"search-icon"}),r.jsx("input",{ref:T,type:"text",value:i,onChange:L,onFocus:N,onBlur:C,onKeyDown:I,placeholder:c,className:"search-input","aria-label":"Search documentation"}),r.jsxs("kbd",{className:"search-shortcut",children:[r.jsx("span",{className:"shortcut-key",children:"⌘"}),"K"]})]}),r.jsxs("div",{className:"search-hint",children:["Press ",r.jsx("kbd",{children:"⌘K"})," to focus search"]})]})}function Sp({selectedCategory:i,onSelectCategory:l,sections:c,allCategoriesLabel:d="All Categories"}){return r.jsx("div",{className:"doc-filters",children:r.jsxs("div",{className:"filter-tabs",role:"tablist","aria-label":"Filter by category",children:[r.jsx("button",{role:"tab","aria-selected":i==="",className:`filter-tab ${i===""?"active":""}`,onClick:()=>l(""),children:d}),c.map(m=>r.jsxs("button",{role:"tab","aria-selected":i===m.id,className:`filter-tab ${i===m.id?"active":""}`,onClick:()=>l(m.id),children:[r.jsx(q,{name:m.icon,size:14}),r.jsx("span",{children:m.label})]},m.id))]})})}function ho({doc:i,variant:l="default"}){const c="page"in i?i.page:i,[d,m]=_.useState(!1),p=k=>{k.preventDefault(),oe(`/docs/${c.slug}`)},g=k=>{(k.key==="Enter"||k.key===" ")&&(k.preventDefault(),oe(`/docs/${c.slug}`))};if(l==="compact")return r.jsx("a",{href:`/docs/${c.slug}`,onClick:p,onKeyDown:g,className:"doc-card-compact",tabIndex:0,role:"button",children:r.jsxs("div",{className:"compact-content",children:[r.jsx("span",{className:"compact-title",children:c.title}),r.jsx("span",{className:"compact-excerpt",children:c.excerpt})]})});const T="highlights"in i?i.highlights:[];return r.jsx("article",{className:`doc-card ${l==="highlighted"?"highlighted":""}`,children:r.jsxs("div",{className:`doc-card-content ${d?"loaded":""}`,children:[r.jsxs("div",{className:"doc-card-header",children:[r.jsx("span",{className:"doc-category",children:c.category.replace(/-/g," ")}),r.jsxs("span",{className:"doc-order",children:["#",c.order]})]}),r.jsx("h3",{className:"doc-title",children:c.title}),r.jsx("p",{className:"doc-excerpt",children:c.excerpt}),T.length>0&&r.jsx("div",{className:"doc-highlights",children:T.slice(0,2).map((k,D)=>r.jsxs("p",{className:"highlight-snippet",children:[k.slice(0,150),k.length>150?"...":""]},D))}),r.jsxs("div",{className:"doc-card-footer",children:[r.jsx("div",{className:"doc-tags",children:c.tags.slice(0,3).map(k=>r.jsxs("span",{className:"doc-tag",children:["#",k]},k))}),r.jsxs("a",{href:`/docs/${c.slug}`,onClick:p,onKeyDown:g,className:"doc-read-more",children:["Read more ",r.jsx(q,{name:"arrow",size:14})]})]})]})})}const Re=[{slug:"welcome",title:"Welcome to Niko",category:"getting-started",excerpt:"New to Niko? Start here to understand what the bot can do for your server.",tags:["introduction","overview","beginner"],order:1,content:`
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
    `}];function Np(i){return Re.find(l=>l.slug===i)}const an=[{id:"getting-started",label:"Getting Started",description:"New to Niko? Start here.",icon:"icon_home",count:Re.filter(i=>i.category==="getting-started").length},{id:"setup",label:"Setup",description:"Configure Niko for your server.",icon:"icon_settings",count:Re.filter(i=>i.category==="setup").length},{id:"economy",label:"Economy",description:"Money, jobs, banking, and more.",icon:"icon_economy",count:Re.filter(i=>i.category==="economy").length},{id:"leveling",label:"Leveling",description:"XP, levels, and rankings.",icon:"icon_leveling",count:Re.filter(i=>i.category==="leveling").length},{id:"moderation",label:"Moderation",description:"Moderation tools and commands.",icon:"icon_moderation",count:Re.filter(i=>i.category==="moderation").length},{id:"automod",label:"AutoMod",description:"Automated moderation features.",icon:"icon_automod",count:Re.filter(i=>i.category==="automod").length},{id:"logging",label:"Logging",description:"Server event logging.",icon:"icon_settings",count:Re.filter(i=>i.category==="logging").length},{id:"social",label:"Social",description:"Community engagement features.",icon:"icon_heart",count:Re.filter(i=>i.category==="social").length},{id:"utility",label:"Utility",description:"Helpful tools and utilities.",icon:"icon_utility",count:Re.filter(i=>i.category==="utility").length},{id:"voice",label:"Voice",description:"Voice and music features.",icon:"icon_bot",count:Re.filter(i=>i.category==="voice").length},{id:"ai",label:"AI",description:"AI-powered features.",icon:"icon_ai",count:Re.filter(i=>i.category==="ai").length},{id:"dashboard",label:"Dashboard",description:"Web dashboard guides.",icon:"icon_settings",count:Re.filter(i=>i.category==="dashboard").length},{id:"tips",label:"Tips",description:"Tips and best practices.",icon:"icon_lightbulb",count:Re.filter(i=>i.category==="tips").length}];function Ju(){const[i,l]=_.useState({query:"",category:"",tags:[]}),c=_.useCallback(k=>{l(D=>({...D,query:k.toLowerCase(),tags:[]}))},[]),d=_.useCallback(k=>{l(D=>({...D,category:k,tags:[]}))},[]),m=_.useCallback(k=>{l(D=>{const N=D.tags.includes(k)?D.tags.filter(C=>C!==k):[...D.tags,k];return{...D,tags:N,query:""}})},[]),p=_.useCallback(()=>{l({query:"",category:"",tags:[]})},[]),g=_.useMemo(()=>{const{query:k,category:D,tags:N}=i;if(!k&&!D&&N.length===0)return Re.map(L=>({page:L,score:1,highlights:[]}));const C=[];for(const L of Re)if(!(D&&L.category!==D)&&!(N.length>0&&!N.some(I=>L.tags.includes(I))))if(k){const I=Cp(L,k);if(I===0)continue;const A=_p(L,k);C.push({page:L,score:I,highlights:A})}else C.push({page:L,score:1,highlights:[]});return C.sort((L,I)=>I.score!==L.score?I.score-L.score:L.page.order-I.page.order),C},[i]),T=i.query!==""||i.category!==""||i.tags.length>0;return{filters:i,setQuery:c,setCategory:d,toggleTag:m,clearFilters:p,results:g,hasActiveFilters:T,resultCount:g.length}}function Cp(i,l){let c=0;const d=l.toLowerCase();i.title.toLowerCase()===d?c+=100:i.title.toLowerCase().includes(d)&&(c+=50),i.excerpt.toLowerCase().includes(d)&&(c+=25),i.content.toLowerCase().includes(d)&&(c+=10);for(const m of i.tags)m.toLowerCase().includes(d)&&(c+=15);return i.category.toLowerCase().includes(d)&&(c+=5),c}function _p(i,l){const c=[],d=l.toLowerCase(),m=3;if(i.title.toLowerCase().includes(d)&&(c.push(i.title),c.length>=m)||i.excerpt.toLowerCase().includes(d)&&(c.push(i.excerpt),c.length>=m))return c;const p=i.content.split(`
`).filter(g=>g.trim());for(const g of p)if(g.toLowerCase().includes(d)){const T=g.replace(/#{1,6}\s?/g,"").trim();if(T.length>10&&(c.push(T),c.length>=m))break}return c}function Tp(){return _.useMemo(()=>{const l={};return Re.forEach(c=>{c.tags.forEach(d=>{l[d]=(l[d]||0)+1})}),Object.entries(l).map(([c,d])=>({tag:c,count:d})).sort((c,d)=>d.count-c.count)},[])}function Ep({slug:i}){var k,D;const{setCategory:l,clearFilters:c}=Ju();_.useEffect(()=>{window.location.hash!==`#/docs/${i}`&&window.history.replaceState(null,"",`#/docs/${i}`)},[i]);const d=Np(i);if(!d)return r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"docs"}),r.jsx("main",{className:"shell page-main docs-page",children:r.jsxs("div",{className:"docs-not-found",children:[r.jsx(q,{name:"doc",size:48,className:"not-found-icon"}),r.jsx("h1",{children:"Page Not Found"}),r.jsxs("p",{children:[`We couldn't find documentation for "`,i,'".']}),r.jsxs("div",{className:"not-found-actions",children:[r.jsx("button",{onClick:()=>oe("/docs"),children:"Browse all documentation"}),r.jsx("button",{onClick:()=>{oe("/docs"),c()},children:"Clear filters"})]})]})}),r.jsx(Nt,{})]});const m=N=>{const C=[],L=/(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*)/g;let I=0,A,B=0;for(;(A=L.exec(N))!==null;){A.index>I&&C.push(N.slice(I,A.index));const j=A[0];if(j.startsWith("`")&&j.endsWith("`")&&j.length>2)C.push(r.jsx("code",{className:"doc-inline-code",children:j.slice(1,-1)},B++));else if(j.startsWith("[")){const J=j.match(/^\[([^\]]+)\]\(([^)]+)\)$/);J?C.push(r.jsx("a",{href:J[2],target:"_blank",rel:"noreferrer",children:m(J[1])},B++)):C.push(j)}else j.startsWith("**")?C.push(r.jsx("strong",{children:m(j.slice(2,-2))},B++)):j.startsWith("*")?C.push(r.jsx("em",{children:m(j.slice(1,-1))},B++)):C.push(j);I=A.index+j.length}return I<N.length&&C.push(N.slice(I)),C},g=(N=>{const C=N.split(`
`),L=[];let I=0,A=null,B=[];const j=()=>{if(B.length===0)return;const S=A==="ol"?"ol":"ul";L.push(r.jsx(S,{className:`doc-content-list ${A==="ol"?"doc-content-list-ol":""}`,children:B.map((V,ee)=>r.jsx("li",{children:m(V)},ee))},`list-${L.length}`)),B=[],A=null},J=()=>{var ee;const S=L[L.length-1];_.isValidElement(S)&&((ee=S.props)==null?void 0:ee.className)==="doc-content-spacer"||L.push(r.jsx("div",{className:"doc-content-spacer"},`spacer-${L.length}`))};for(;I<C.length;){const V=C[I].trim();if(!V){j(),J(),I+=1;continue}if(V.startsWith("```")){j();const z=[];let O=I+1;for(;O<C.length&&C[O].trim()!=="```";)z.push(C[O]),O+=1;L.push(r.jsx("pre",{className:"doc-code-block",children:r.jsx("code",{children:z.join(`
`)})},`code-${I}`)),I=O+1;continue}if(V.startsWith("|")){j();const z=[];let O=I;for(;O<C.length&&C[O].trim().startsWith("|");){const Ce=C[O].trim().replace(/^\|/,"").replace(/\|$/,"").split("|").map(_e=>_e.trim());z.push(Ce),O+=1}const ce=z.length>1&&z[1].every(Ce=>/^:?-{2,}:?$/.test(Ce.replace(/\s+/g,""))),ge=z[0],Fe=ce?z.slice(2):z.slice(1);ge.length>1&&L.push(r.jsxs("table",{className:"doc-table",children:[r.jsx("thead",{children:r.jsx("tr",{children:ge.map((Ce,_e)=>r.jsx("th",{children:m(Ce)},_e))})}),r.jsx("tbody",{children:Fe.map((Ce,_e)=>r.jsx("tr",{children:Ce.map((ne,Pe)=>r.jsx("td",{children:m(ne)},Pe))},_e))})]},`table-${I}`)),I=O;continue}if(V.startsWith("### ")){j(),L.push(r.jsx("h4",{className:"doc-heading doc-heading-h4",children:V.slice(4)},`h-${I}`)),I+=1;continue}if(V.startsWith("## ")){j(),L.push(r.jsx("h3",{className:"doc-heading doc-heading-h3",children:V.slice(3)},`h-${I}`)),I+=1;continue}if(V.startsWith("# ")){j(),L.push(r.jsx("h2",{className:"doc-heading doc-heading-h2",children:V.slice(2)},`h-${I}`)),I+=1;continue}if(V.startsWith("> ")){j(),L.push(r.jsx("blockquote",{className:"doc-blockquote",children:m(V.slice(2))},`q-${I}`)),I+=1;continue}const ee=V.match(/^[-*]\s+(.*)$/);if(ee){A!=="ul"&&j(),A="ul",B.push(ee[1]),I+=1;continue}const re=V.match(/^\d+\.\s+(.*)$/);if(re){A!=="ol"&&j(),A="ol",B.push(re[1]),I+=1;continue}j(),L.push(r.jsx("p",{className:"doc-paragraph",children:m(V)},`p-${I}`)),I+=1}return j(),L})(d.content),T=g.filter(N=>_.isValidElement(N)&&(N.type==="h2"||N.type==="h3"));return r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page docs-detail-page",children:[r.jsx("div",{className:"docs-detail-back",children:r.jsxs("button",{onClick:()=>oe("/docs"),className:"back-button",children:[r.jsx(q,{name:"arrow",size:16}),"Back to Documentation"]})}),r.jsxs("header",{className:"doc-article-header",children:[r.jsxs("div",{className:"doc-article-meta",children:[r.jsx("span",{className:"doc-category-badge",children:((k=an.find(N=>N.id===d.category))==null?void 0:k.label)||d.category}),r.jsxs("span",{className:"doc-order-badge",children:["Article #",d.order]})]}),r.jsx("h1",{className:"doc-article-title",children:d.title}),r.jsx("p",{className:"doc-article-excerpt",children:d.excerpt}),r.jsx("div",{className:"doc-article-tags",children:d.tags.map(N=>r.jsxs("span",{className:"doc-tag-pill",children:["#",N]},N))})]}),r.jsx("article",{className:"doc-article-content",children:g}),r.jsx("footer",{className:"doc-article-footer",children:r.jsx("div",{className:"doc-nav-container",children:r.jsxs("div",{className:"doc-nav-col",children:[r.jsx("span",{className:"doc-nav-label",children:"Category"}),r.jsxs("button",{className:"doc-nav-link",onClick:()=>{l(d.category),oe("/docs")},children:[r.jsx(q,{name:"arrow",size:14}),"View all ",(D=an.find(N=>N.id===d.category))==null?void 0:D.label]})]})})}),T.length>0&&r.jsxs("aside",{className:"doc-toc",children:[r.jsxs("div",{className:"toc-title",children:[r.jsx(q,{name:"utility",size:16}),r.jsx("span",{children:"On this page"})]}),r.jsx("nav",{className:"toc-nav",children:T.map((N,C)=>{var I;const L=(I=N.props.className)==null?void 0:I.includes("doc-heading-h2");return r.jsx("a",{href:`#${L?"h2-":"h3-"}-${C}`,className:`toc-link ${L?"toc-h2":"toc-h3"}`,children:N.props.children},C)})})]})]}),r.jsx(Nt,{})]})}function Mp(){var ee,re;const[i,l]=_.useState(!1),[c,d]=_.useState(""),[m,p]=_.useState(!1),{filters:g,setQuery:T,setCategory:k,toggleTag:D,clearFilters:N,results:C,hasActiveFilters:L,resultCount:I}=Ju(),A=Tp();_.useEffect(()=>{const z=()=>{const O=window.location.hash.slice(1);if(O.startsWith("#/docs/")){const ce=O.replace("#/docs/",""),ge=Re.find(Fe=>Fe.slug===ce);ge&&(d(ge.category),k(ge.category))}};return z(),window.addEventListener("hashchange",z),()=>window.removeEventListener("hashchange",z)},[]);const B=()=>{p(!0)},j=z=>{d(z),k(z),l(!1)},J=()=>{g.query||p(!1)},S=z=>{oe(`/docs/${z}`),T(""),p(!1)},V=_.useMemo(()=>{const z={};return C.forEach(O=>{const ce=O.page.category;z[ce]||(z[ce]=[]),z[ce].push(O)}),z},[C]);return r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page",children:[r.jsx("div",{className:"docs-hero",children:r.jsxs("div",{className:"docs-hero-content",children:[r.jsx("div",{className:"eyebrow docs-eyebrow",children:"Documentation Center"}),r.jsxs("h1",{className:"docs-title",children:["Everything you need to know about",r.jsx("br",{}),r.jsx("span",{className:"title-accent",children:"using Niko"})]}),r.jsx("p",{className:"docs-subtitle",children:"Comprehensive guides, command references, and tips to help you get the most out of your server bot."})]})}),r.jsx("div",{className:`docs-search-section ${m?"active":""}`,children:r.jsxs("div",{className:"docs-search-container",children:[r.jsx(jp,{value:g.query,onChange:T,placeholder:"Search documentation, commands, guides...",onFocus:B,onBlur:J}),m&&g.query&&C.length>0&&r.jsxs("div",{className:"search-results-dropdown",children:[r.jsxs("div",{className:"search-results-header",children:[r.jsxs("span",{className:"results-count",children:[I," ",I===1?"result":"results"]}),r.jsx("button",{className:"clear-search-btn",onClick:()=>{T(""),N(),d("")},children:"Clear"})]}),r.jsx("div",{className:"search-results-list",children:C.slice(0,8).map((z,O)=>r.jsxs("button",{className:"search-result-item",onClick:()=>S(z.page.slug),onMouseEnter:()=>{},children:[r.jsx("div",{className:"result-icon",children:r.jsx(q,{name:"doc",size:18})}),r.jsxs("div",{className:"result-content",children:[r.jsx("div",{className:"result-title",children:z.page.title}),r.jsx("div",{className:"result-excerpt",children:z.page.excerpt}),z.highlights.length>0&&r.jsxs("div",{className:"result-highlight",children:[z.highlights[0].slice(0,100),"..."]})]}),r.jsx(q,{name:"arrow",size:14,className:"result-arrow"})]},z.page.slug))}),C.length>8&&r.jsx("div",{className:"search-results-footer",children:r.jsxs("span",{children:["Showing 8 of ",C.length," results. Browse all docs below."]})})]})]})}),r.jsxs("div",{className:"docs-mobile-nav",children:[r.jsx("button",{className:"mobile-menu-toggle",onClick:()=>l(!i),"aria-label":"Toggle documentation menu",children:r.jsx(q,{name:"utility",size:20})}),i&&r.jsxs("div",{className:"mobile-nav-panel",children:[r.jsxs("div",{className:"mobile-nav-header",children:[r.jsx("h3",{children:"Documentation"}),r.jsx("button",{className:"close-menu-btn",onClick:()=>l(!1),"aria-label":"Close menu",children:r.jsx(q,{name:"utility",size:16,className:"rotated"})})]}),r.jsx("div",{className:"mobile-nav-sections",children:an.map(z=>r.jsxs("button",{className:`mobile-nav-item ${c===z.id?"active":""}`,onClick:()=>{j(z.id)},children:[r.jsx(q,{name:z.icon,size:18}),r.jsx("span",{className:"mobile-section-label",children:z.label}),r.jsx("span",{className:"mobile-section-count",children:z.count})]},z.id))})]})]}),A.length>0&&!L&&r.jsxs("div",{className:"docs-tags-cloud",children:[r.jsxs("div",{className:"tags-cloud-title",children:[r.jsx(q,{name:"utility",size:16}),r.jsx("span",{children:"Popular Topics"})]}),r.jsx("div",{className:"tags-cloud-list",children:A.slice(0,15).map(({tag:z,count:O})=>r.jsxs("button",{className:"tag-cloud-item",onClick:()=>D(z),style:{fontSize:`${.75+Math.min(O/4,1)}rem`},children:["#",z,r.jsx("span",{className:"tag-count",children:O})]},z))})]}),r.jsx("div",{className:"docs-category-filters",children:r.jsx(Sp,{selectedCategory:g.category,onSelectCategory:j,sections:an})}),L&&r.jsxs("div",{className:"docs-results-header",children:[r.jsxs("div",{className:"results-info",children:[r.jsxs("span",{className:"results-count-large",children:[I," ",I===1?"article":"articles"]}),g.query&&r.jsxs("span",{className:"search-query-display",children:['for "',r.jsx("strong",{children:g.query}),'"']})]}),r.jsxs("button",{className:"clear-all-btn",onClick:()=>{N(),d("")},disabled:!L,children:[r.jsx(q,{name:"utility",size:14}),"Clear all filters"]})]}),r.jsx("div",{className:"docs-content",children:L?r.jsx("div",{className:"search-results-view",children:Object.entries(V).map(([z,O])=>{var ce;return r.jsxs("section",{className:"results-category",children:[r.jsx("h2",{className:"category-title",children:((ce=an.find(ge=>ge.id===z))==null?void 0:ce.label)||z}),r.jsx("div",{className:"category-results-grid",children:O.map(ge=>r.jsx(ho,{doc:ge,variant:"highlighted"},ge.page.slug))})]},z)})}):c?r.jsxs("div",{className:"category-view",children:[r.jsxs("div",{className:"category-header",children:[r.jsx("h2",{className:"category-page-title",children:((ee=an.find(z=>z.id===c))==null?void 0:ee.label)||c}),r.jsx("p",{className:"category-description",children:(re=an.find(z=>z.id===c))==null?void 0:re.description})]}),r.jsx("div",{className:"category-articles",children:Re.filter(z=>z.category===c).sort((z,O)=>z.order-O.order).map(z=>r.jsx(ho,{doc:z},z.slug))})]}):r.jsx("div",{className:"all-categories-view",children:an.map(z=>r.jsxs("section",{className:"docs-section",id:`section-${z.id}`,children:[r.jsxs("div",{className:"section-header",children:[r.jsx("div",{className:"section-icon",children:r.jsx(q,{name:z.icon,size:28})}),r.jsxs("div",{className:"section-info",children:[r.jsx("h2",{className:"section-title",children:z.label}),r.jsx("p",{className:"section-description",children:z.description})]}),r.jsx("span",{className:"section-count",children:z.count})]}),r.jsx("div",{className:"section-articles",children:Re.filter(O=>O.category===z.id).sort((O,ce)=>O.order-ce.order).map(O=>r.jsx(ho,{doc:O},O.slug))})]},z.id))})}),r.jsxs("div",{className:"docs-footer-note",children:[r.jsx(q,{name:"book",size:20}),r.jsxs("div",{children:[r.jsx("strong",{children:"Want more detail?"}),r.jsxs("p",{children:["The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in the"," ",r.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"docs/"})," ","folder."]})]})]})]}),r.jsx(Nt,{})]})}function Pp(){const i=aa(),[l,c]=_.useState(null);_.useEffect(()=>{ea().then(c).catch(()=>{})},[]);const d=[["spark","AI that remembers","Thoughtful conversation with a cozy personality and controls that respect your community."],["chart","A living economy","Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],["shield","Confident moderation","Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],["users","Community rituals","Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."]];return r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"home"}),r.jsxs("main",{children:[r.jsxs("section",{className:"hero shell",children:[r.jsxs("div",{className:"hero-copy",children:[r.jsxs("div",{className:"eyebrow",children:[r.jsx("span",{className:"status-dot"})," Discord companion · online"]}),r.jsxs("div",{className:"hero-identity",children:[r.jsx("span",{className:"hero-avatar",children:i!=null&&i.bot_avatar_url?r.jsx("img",{src:i.bot_avatar_url,alt:"Niko"}):"n"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Niko"}),r.jsx("small",{children:"Your server’s calm, capable co-pilot"})]})]}),r.jsxs("h1",{children:["Useful tools for a ",r.jsx("em",{children:"better server."})]}),r.jsx("p",{children:"Niko handles the everyday work of running a Discord community, so your moderators can focus on the people in it."}),r.jsxs("div",{className:"hero-buttons",children:[r.jsxs("a",{className:"button button-primary",href:(i==null?void 0:i.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Invite Niko ",r.jsx(q,{name:"arrow"})]}),r.jsx("a",{className:"button button-muted",href:"/commands",onClick:m=>{m.preventDefault(),oe("/commands")},children:"Explore commands"})]}),r.jsxs("div",{className:"stats-strip",children:[r.jsxs("div",{children:[r.jsx("strong",{children:Me(l==null?void 0:l.guild_count)}),r.jsx("span",{children:"servers"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:Me(l==null?void 0:l.user_count)}),r.jsx("span",{children:"members"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:Me(l==null?void 0:l.command_count)}),r.jsx("span",{children:"commands"})]})]})]}),r.jsx("div",{className:"hero-art","aria-label":"A preview of Niko's server workspace",children:r.jsxs("div",{className:"workspace-preview",children:[r.jsxs("div",{className:"workspace-preview-top",children:[r.jsxs("span",{className:"preview-dots",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"server workspace"}),r.jsxs("span",{className:"preview-status",children:[r.jsx("span",{className:"status-dot"})," live"]})]}),r.jsxs("div",{className:"preview-body",children:[r.jsxs("div",{className:"preview-sidebar",children:[r.jsx("span",{className:"preview-label",children:"NIKO"}),r.jsx("b",{children:"Overview"}),r.jsx("span",{children:"Economy"}),r.jsx("span",{children:"Leveling"}),r.jsx("span",{children:"Moderation"}),r.jsx("span",{children:"AI controls"})]}),r.jsxs("div",{className:"preview-main",children:[r.jsx("span",{className:"preview-label",children:"SERVER SNAPSHOT"}),r.jsx("strong",{children:"Everything in one place."}),r.jsxs("div",{className:"preview-stats",children:[r.jsxs("span",{children:[r.jsx("b",{children:Me(l==null?void 0:l.user_count)}),r.jsx("small",{children:"members"})]}),r.jsxs("span",{children:[r.jsx("b",{children:Me(l==null?void 0:l.command_count)}),r.jsx("small",{children:"commands"})]})]}),r.jsxs("div",{className:"preview-line",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]})]})]})]})})]}),r.jsxs("section",{className:"shell intro-section",children:[r.jsx("div",{className:"section-kicker",children:"Why Niko"}),r.jsxs("div",{className:"intro-grid",children:[r.jsxs("h2",{children:["The good kind of",r.jsx("br",{}),r.jsx("em",{children:"always-on."})]}),r.jsx("p",{children:"Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile."})]})]}),r.jsx("section",{className:"shell feature-grid",children:d.map(([m,p,g])=>r.jsxs("article",{className:"feature-card",children:[r.jsx("span",{className:"feature-icon",children:r.jsx(q,{name:m})}),r.jsx("h3",{children:p}),r.jsx("p",{children:g}),r.jsxs("a",{href:"/docs",onClick:T=>{T.preventDefault(),oe("/docs")},children:["Learn more ",r.jsx(q,{name:"arrow"})]})]},p))}),r.jsxs("section",{className:"shell callout",children:[r.jsxs("div",{children:[r.jsx("div",{className:"section-kicker",children:"Ready when you are"}),r.jsxs("h2",{children:["A calmer, cleverer home",r.jsx("br",{}),"for your community."]})]}),r.jsxs("a",{className:"button button-primary",href:(i==null?void 0:i.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Bring Niko in ",r.jsx(q,{name:"arrow"})]})]})]}),r.jsx(Nt,{})]})}const Lp=[{code:"USDT",label:"Tether"},{code:"ETH",label:"Ethereum"},{code:"BTC",label:"Bitcoin"},{code:"BNB",label:"BNB"},{code:"LTC",label:"Litecoin"},{code:"DOGE",label:"Dogecoin"},{code:"TRX",label:"TRON"},{code:"XMR",label:"Monero"}];function Rp(){const l=new URLSearchParams(window.location.search).get("token")||"",[c,d]=_.useState("5"),[m,p]=_.useState("USDT"),[g,T]=_.useState(!1),[k,D]=_.useState(""),[N,C]=_.useState(null),[L,I]=_.useState(null),[A,B]=_.useState(!1);_.useEffect(()=>{l||B(!0)},[l]),_.useEffect(()=>{if(!(N!=null&&N.status_url)||N.paid)return;const J=setInterval(async()=>{try{const S=await Ie(N.status_url);I(S),S.paid&&clearInterval(J)}catch{}},5e3);return()=>clearInterval(J)},[N]);const j=async J=>{J.preventDefault(),T(!0),D("");try{const S=await Ie("/api/donations/invoice",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:l,amount:parseFloat(c),currency:m})});C(S),S.error&&(D(S.error),C(null))}catch(S){D(S instanceof Error?S.message:"Could not create invoice.")}finally{T(!1)}};return A?r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Invalid donation link"}),r.jsxs("h1",{children:["This link is ",r.jsx("em",{children:"invalid."})]}),r.jsxs("p",{children:["The donation link is missing or has expired. Use the"," ",r.jsx("code",{children:"/donate"})," command in Discord to generate a new one."]}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>oe("/"),children:"Return home"})]})})]}):L!=null&&L.paid?r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"✓"}),r.jsx("div",{className:"eyebrow",children:"Payment confirmed"}),r.jsxs("h1",{children:["Thank you ",r.jsx("em",{children:"for supporting!"})]}),r.jsx("p",{children:"Your donation has been confirmed. You will receive the Supporter badge shortly."}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>oe("/"),children:"Return home"})]})})]}):r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"home"}),r.jsx("main",{className:"page-main",children:r.jsx("div",{className:"shell",children:r.jsxs("div",{className:"page-heading",style:{maxWidth:500,margin:"0 auto"},children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:15},children:"Support Niko"}),r.jsxs("h1",{children:["Keep Niko ",r.jsx("em",{children:"running."})]}),r.jsx("p",{style:{color:"var(--muted)",marginBottom:30},children:"Your donation helps cover hosting costs and keeps Niko running for all servers. Choose an amount and cryptocurrency below."}),N!=null&&N.pay_link?r.jsxs("div",{className:"dash-panel",style:{marginBottom:24},children:[r.jsx("div",{className:"panel-heading",children:r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Invoice created"}),r.jsx("h3",{children:"Complete your payment"})]})}),r.jsxs("p",{style:{color:"var(--muted)",fontSize:12,marginBottom:16},children:["Amount: ",r.jsxs("strong",{children:["$",parseFloat(c).toFixed(2)," USD"]})," in"," ",r.jsx("strong",{children:m})]}),r.jsxs("p",{style:{color:"var(--dim)",fontSize:10,marginBottom:16},children:["Track ID: ",r.jsx("code",{children:N.track_id})," · Expires in 60 minutes"]}),r.jsxs("a",{className:"button button-primary",href:N.pay_link,target:"_blank",rel:"noopener noreferrer",children:["Pay now ",r.jsx(q,{name:"arrow"})]}),r.jsx("p",{style:{color:"var(--dim)",fontSize:10,marginTop:12},children:"Payment will be confirmed automatically once the transaction is processed on-chain."})]}):r.jsxs("form",{onSubmit:j,className:"dash-panel",style:{marginBottom:24},children:[r.jsxs("div",{className:"form-grid",children:[r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Amount (USD)"}),r.jsx("input",{type:"number",min:"1",max:"10000",step:"0.01",value:c,onChange:J=>d(J.target.value)}),r.jsx("small",{children:"Minimum $1.00, maximum $10,000.00"})]}),r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Cryptocurrency"}),r.jsx("select",{value:m,onChange:J=>p(J.target.value),children:Lp.map(J=>r.jsxs("option",{value:J.code,children:[J.label," (",J.code,")"]},J.code))})]})]}),k&&r.jsx("p",{className:"form-error",style:{marginTop:12},role:"alert",children:k}),r.jsx("div",{style:{marginTop:16},children:r.jsx("button",{className:"button button-primary",type:"submit",disabled:g,children:g?"Creating invoice…":"Create invoice"})})]}),r.jsxs("div",{className:"docs-footer-note",style:{marginTop:20},children:[r.jsx("strong",{children:"How it works"}),r.jsx("p",{children:'1. Choose an amount and currency above · 2. Click "Pay now" to open the payment page · 3. Send crypto to the displayed address · 4. Payment is confirmed automatically once processed on-chain'})]})]})})})]})}const Ap={privacy:{title:"Privacy policy",intro:"Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",sections:[["Information we use","User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature."],["How it is used","Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],["Storage and retention","Data is stored by the server hosting Niko in local JSON and SQLite files. Economy, leveling, and configuration data remain until removed. AI conversation history is limited and can be cleared with /clearhistory."],["Third-party services","When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Music and external lookup features may contact their respective services."],["Your choices","Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."]]},terms:{title:"Terms of service",intro:"By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",sections:[["Permitted use","Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],["Availability","Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],["Moderation","The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],["AI content","AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],["Virtual items","In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],["Contact","Questions or concerns can be sent through the Niko support server."]]},community:{title:"Community policy",intro:"These community expectations apply to every server that uses Niko. By adding the bot to a server, the server's owners and administrators agree to uphold these standards.",sections:[["Purpose","Niko is a community companion for Discord servers of all kinds. To keep the platform safe for everyone, all servers using Niko must follow the expectations below in addition to Discord's Terms of Service and Community Guidelines."],["Discrimination and harassment","Servers must not permit or promote discrimination, harassment, or hate speech targeting people based on race, ethnicity, national origin, religion, disability, gender, gender identity or expression, sexual orientation, age, veteran status, or any other protected identity characteristic."],["Illegal and malicious content","Servers must not create, host, share, or distribute illegal or malicious content. This includes, but is not limited to: child sexual abuse material (CSAM), malware and other malicious software, gore or shock content, pirated media and/or software, content that facilitates violence or terrorism, scams and phishing, and any other content that is illegal under applicable law."],["Other prohibited conduct","Servers must not use Niko to facilitate doxxing, targeted harassment campaigns, sextortion, trafficking, or the sexualization of minors in any form."],["Enforcement and investigations","When a server is reported or flagged for potentially violating this policy, Niko will send a warning notice to the server. The notice is followed by an investigation by Niko staff. Servers that cooperate in good faith and are found not to be breaking the policies will not receive any further action."],["Obstruction of investigations","Banning, kicking, or otherwise removing the staff member(s) sent to investigate, or hiding, deleting, or tampering with potential evidence, is treated as an admission of guilt. Doing so will result in the server — and any users who are involved — being permanently blacklisted from further use of Niko, in addition to any other action the investigation warrants."],["Reporting","If you believe a server using Niko is violating this policy, report it through the Niko support server. Reports are reviewed by staff and handled confidentially."]]}};function po({type:i}){const l=Ap[i];return r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:i}),r.jsxs("main",{className:"shell page-main legal-page",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Niko legal"}),r.jsx("h1",{children:l.title}),r.jsx("p",{children:l.intro}),r.jsx("small",{children:"Effective date: 1 January 2025"})]}),r.jsx("div",{className:"legal-copy",children:l.sections.map(([c,d])=>r.jsxs("section",{children:[r.jsx("h2",{children:c}),r.jsx("p",{children:d})]},c))})]}),r.jsx(Nt,{})]})}const Dp=[{key:"txt",label:"TXT",icon:"📄"},{key:"html",label:"HTML",icon:"🌐"},{key:"csv",label:"CSV",icon:"📊"},{key:"json",label:"JSON",icon:"{ }"}],Zu=i=>typeof i!="number"||i<0||i>16777215?"":`#${i.toString(16).padStart(6,"0")}`,jn=i=>(i==null?void 0:i.url)||(i==null?void 0:i.proxy_url)||"",ed=i=>/\.(?:png|jpe?g|gif|webp|bmp|svg)(?:[?#]|$)/i.test(i)||i.startsWith("data:image/"),td=i=>/\.(?:mp4|webm|mov|m4v|ogg)(?:[?#]|$)/i.test(i)||i.startsWith("data:video/"),Ip=i=>i.url?i.url:i.id?`https://cdn.discordapp.com/stickers/${i.id}.${i.format_type===4?"gif":"png"}`:"";function Fp(i){var c;const l=jn(i);return l?(c=i==null?void 0:i.content_type)!=null&&c.startsWith("video/")?!0:td(l):!1}const Wu=new RegExp("(`[^`\\n]+`)|(\\[([^\\]\\n]+)\\]\\((https?:\\/\\/[^\\s)\\] ]+)\\))|(\\*\\*)|(?<!\\*)\\*(?!\\*)|(~~)","g"),zp=/(https?:\/\/[^\s<>)]+)/g,Uu={bold:"**",italic:"*",strike:"~~"},Bp=new Set(["t","T","d","D","f","F","R"]);function Op(i,l){if(!Number.isFinite(i)||!Bp.has(l))return null;const c=new Date(i*1e3);if(Number.isNaN(c.getTime()))return null;if(l==="R"){const m=i-Math.floor(Date.now()/1e3),p=Math.abs(m),g=p<60?"second":p<3600?"minute":p<86400?"hour":p<604800?"day":p<2592e3?"week":p<31536e3?"month":"year",T=g==="second"?1:g==="minute"?60:g==="hour"?3600:g==="day"?86400:g==="week"?604800:g==="month"?2592e3:31536e3;return new Intl.RelativeTimeFormat(void 0,{numeric:"always"}).format(Math.round(m/T),g)}const d={...l==="t"||l==="T"?{hour:"numeric",minute:"2-digit"}:{},...l==="T"?{second:"2-digit"}:{},...l==="d"?{year:"numeric",month:"2-digit",day:"2-digit"}:{},...l==="D"?{year:"numeric",month:"long",day:"numeric"}:{},...l==="f"?{year:"numeric",month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}:{},...l==="F"?{weekday:"long",year:"numeric",month:"long",day:"numeric",hour:"numeric",minute:"2-digit"}:{}};return new Intl.DateTimeFormat(void 0,d).format(c)}function Wp(i){const l=[];let c=0,d;const m=p=>{if(!p)return;const g=p.split(/(<a?:[A-Za-z0-9_~]+:\d+>|<t:-?\d+:[tTdDfFR]>)/g);for(const T of g){if(!T)continue;const k=T.match(/^<(a?):([A-Za-z0-9_~]+):(\d+)>$/);if(k){l.push({type:"emoji",name:k[2],id:k[3],animated:k[1]==="a"});continue}const D=T.match(/^<t:(-?\d+):([tTdDfFR])>$/);if(D){l.push({type:"timestamp",unix:Number(D[1]),style:D[2],raw:T});continue}const N=T.split(zp);for(let C=0;C<N.length;C++)N[C]&&(C%2===1?l.push({type:"link",text:N[C],url:N[C]}):l.push({type:"text",text:N[C]}))}};for(Wu.lastIndex=0;(d=Wu.exec(i))!==null;)d.index>c&&m(i.slice(c,d.index)),d[1]!==void 0?l.push({type:"code",text:d[1].slice(1,-1)}):d[2]!==void 0?l.push({type:"link",text:d[3],url:d[4]}):d[5]!==void 0?l.push({type:"marker",fmt:"bold"}):d[6]!==void 0?l.push({type:"marker",fmt:"italic"}):d[7]!==void 0&&l.push({type:"marker",fmt:"strike"}),c=d.index+d[0].length;return c<i.length&&m(i.slice(c)),l}function Up(i){const l=[],c=[],d=new Set,m=p=>{c.length>0?c[c.length-1].children.push(p):l.push(p)};for(const p of Wp(i))if(p.type==="text")m({kind:"text",text:p.text});else if(p.type==="code")m({kind:"code",text:p.text});else if(p.type==="link")m({kind:"link",text:p.text,url:p.url});else if(p.type==="emoji")m({kind:"emoji",name:p.name,id:p.id,animated:p.animated});else if(p.type==="timestamp")m({kind:"timestamp",unix:p.unix,style:p.style,raw:p.raw});else if(p.type==="marker")if(d.has(p.fmt)){const g=c.map(D=>D.fmt).lastIndexOf(p.fmt),T=c.splice(g);T.forEach(D=>d.delete(D.fmt));const k={kind:"fmt",fmt:p.fmt,children:[...T[0].children]};for(const D of T.slice(1))k.children.push({kind:"text",text:Uu[D.fmt]??""}),k.children.push(...D.children);m(k)}else c.push({fmt:p.fmt,children:[]}),d.add(p.fmt);if(c.length>0)for(const p of c){m({kind:"text",text:Uu[p.fmt]??""});for(const g of p.children)m(g)}return l}const nd=(i,l)=>i.map((c,d)=>{const m=`${l}-${d}`;switch(c.kind){case"text":return r.jsx("span",{children:c.text},m);case"code":return r.jsx("code",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:4,padding:"0 5px",color:"#f2b8c2",fontFamily:"monospace",fontSize:"0.92em"},children:c.text},m);case"emoji":return r.jsx("img",{src:`https://cdn.discordapp.com/emojis/${c.id}.${c.animated?"gif":"png"}`,alt:`:${c.name}:`,title:`:${c.name}:`,style:{width:22,height:22,objectFit:"contain",verticalAlign:"-0.35em",display:"inline-block"},onError:p=>{p.currentTarget.alt=`:${c.name}:`}},m);case"timestamp":{const p=Op(c.unix,c.style);return p?r.jsx("time",{dateTime:new Date(c.unix*1e3).toISOString(),title:c.raw,children:p},m):r.jsx("span",{children:c.raw},m)}case"link":return r.jsx("a",{href:c.url,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",textDecoration:"none"},onMouseEnter:p=>{p.currentTarget.style.textDecoration="underline"},onMouseLeave:p=>{p.currentTarget.style.textDecoration="none"},children:c.text},m);case"fmt":{const p={};return c.fmt==="bold"&&(p.fontWeight=700),c.fmt==="italic"&&(p.fontStyle="italic"),c.fmt==="strike"&&(p.textDecoration="line-through"),r.jsx("span",{style:p,children:nd(c.children,m)},m)}}}),Js=i=>nd(Up(i),"md");function wn({text:i,muted:l}){const c=i.split(`
`),d=[];return c.forEach((m,p)=>{const g=m.trimStart(),k=p===c.length-1?null:r.jsx("br",{},`br${p}`);g.startsWith("-# ")?d.push(r.jsxs("span",{style:{color:l?"#6d737a":"#949ba4",fontSize:12},children:[Js(g.slice(3)),k]},p)):/^#{1,4}\s/.test(g)?d.push(r.jsxs("span",{style:{color:"#f2f3f5",fontWeight:700,fontSize:16},children:[Js(g),k]},p)):g.startsWith("> ")?d.push(r.jsxs("span",{style:{display:"inline-block",color:"#b5bac1",borderLeft:"3px solid #4e5058",paddingLeft:8},children:[Js(g.slice(2)),k]},p)):g.startsWith("```")?d.push(r.jsxs("pre",{style:{background:"#2b2d31",border:"1px solid #3f4147",borderRadius:6,padding:"10px 12px",overflowX:"auto",whiteSpace:"pre-wrap",wordBreak:"break-word",fontFamily:"monospace",fontSize:12.5,color:"#dbdee1",margin:"2px 0"},children:[g.replace(/^```[a-zA-Z]*/,"").replace(/```$/,""),k]},p)):d.push(r.jsxs("span",{children:[Js(m),k]},p))}),r.jsx("span",{style:{whiteSpace:"pre-wrap",wordBreak:"break-word"},children:d})}function $p({embed:i}){const l=Zu(i.color)||"#5865f2",c=i.author,d=i.footer,m=jn(i.thumbnail),p=jn(i.image);return r.jsxs("div",{style:{display:"flex",gap:12,maxWidth:560,marginTop:8,background:"#2b2d31",border:"1px solid #3f4147",borderLeft:`4px solid ${l}`,borderRadius:6,padding:"10px 12px"},children:[r.jsxs("div",{style:{flex:1,minWidth:0},children:[(c==null?void 0:c.name)&&r.jsxs("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:4},children:[c.icon_url&&r.jsx("img",{src:c.icon_url||c.proxy_icon_url,alt:"",style:{width:18,height:18,borderRadius:"50%",verticalAlign:"-4px",marginRight:6}}),c.name]}),i.title&&r.jsx("div",{style:{color:"#00a8fc",fontWeight:600,margin:"2px 0 4px",fontSize:14},children:i.url?r.jsx("a",{href:i.url,target:"_blank",rel:"noopener noreferrer",style:{color:"inherit",textDecoration:"none"},children:r.jsx(wn,{text:i.title})}):r.jsx(wn,{text:i.title})}),i.description&&r.jsx("div",{style:{color:"#dbdee1",fontSize:13,lineHeight:1.5},children:r.jsx(wn,{text:i.description})}),i.fields&&i.fields.length>0&&r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:"6px 12px",marginTop:8},children:i.fields.map((g,T)=>r.jsxs("div",{style:{flex:g.inline?"0 1 45%":"1 1 100%",minWidth:0,marginBottom:4},children:[g.name&&r.jsx("div",{style:{color:"#f2f3f5",fontWeight:600,fontSize:13,marginBottom:2},children:r.jsx(wn,{text:g.name})}),g.value&&r.jsx("div",{style:{color:"#dbdee1",fontSize:13},children:r.jsx(wn,{text:g.value})})]},T))}),p&&r.jsx("a",{href:p,target:"_blank",rel:"noopener noreferrer",style:{display:"block",marginTop:8},children:r.jsx("img",{src:p,alt:"",style:{maxWidth:"100%",maxHeight:300,borderRadius:4,display:"block"},onError:g=>{g.currentTarget.style.display="none"}})}),((d==null?void 0:d.text)||i.timestamp)&&r.jsxs("div",{style:{display:"flex",alignItems:"center",gap:6,marginTop:6,color:"#949ba4",fontSize:11},children:[(d==null?void 0:d.icon_url)&&r.jsx("img",{src:d.icon_url||d.proxy_icon_url,alt:"",style:{width:16,height:16,borderRadius:"50%"}}),(d==null?void 0:d.text)&&r.jsx("span",{children:d.text}),i.timestamp&&r.jsx("span",{children:String(i.timestamp).replace("T"," ").replace("+00:00"," UTC")})]})]}),m&&r.jsx("a",{href:m,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:r.jsx("img",{src:m,alt:"",style:{width:80,height:80,borderRadius:6,objectFit:"cover"},onError:g=>{g.currentTarget.style.display="none"}})})]})}function Zs({component:i}){switch(i.type){case 17:{const l=Zu(i.accent_color);return r.jsxs("div",{style:{display:"flex",overflow:"hidden",maxWidth:560,marginTop:8,background:"#2b2d31",border:`1px solid ${l||"#3f4147"}`,borderRadius:12},children:[l&&r.jsx("div",{style:{flex:"0 0 4px",background:l}}),r.jsx("div",{style:{flex:1,minWidth:0,padding:"6px 12px 8px"},children:(i.components||[]).map((c,d)=>r.jsx(Zs,{component:c},d))})]})}case 1:return r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,margin:"6px 0"},children:(i.components||[]).map((l,c)=>r.jsx(Zs,{component:l},c))});case 2:{const l=i.emoji,c=`${(l==null?void 0:l.name)??""}${i.label?` ${i.label}`:""}`.trim();return i.style===5&&!!i.url?r.jsx("a",{href:i.url,target:"_blank",rel:"noopener noreferrer",style:{display:"inline-block",padding:"3px 14px",background:"#5865f2",borderRadius:4,color:"#fff",fontSize:13,fontWeight:600,textDecoration:"none"},children:c||"Button"}):r.jsx("span",{style:{display:"inline-block",padding:"3px 14px",background:"#4e5058",borderRadius:4,color:i.disabled?"#8a8e96":"#f2f3f5",fontSize:13,cursor:i.disabled?"not-allowed":"default",opacity:i.disabled?.55:1},children:c||"Button"})}case 9:{const l=[...i.components||[]];return i.accessory&&l.push(i.accessory),r.jsx("div",{style:{display:"flex",alignItems:"center",gap:10,margin:"4px 0"},children:l.map((c,d)=>r.jsx(Zs,{component:c},d))})}case 10:return r.jsx("div",{style:{color:"#dbdee1",fontSize:14,lineHeight:1.5,margin:"4px 0",wordBreak:"break-word"},children:r.jsx(wn,{text:i.content||""})});case 18:return r.jsx("div",{style:{color:"#f2f3f5",fontWeight:700,textTransform:"uppercase",letterSpacing:"0.04em",fontSize:12,margin:"4px 0"},children:i.content});case 14:return r.jsx("div",{style:{margin:i.divider===!1?"6px 0":"9px 0",...i.divider===!1?{}:{borderTop:"1px solid #3f4147"}}});case 11:{const l=jn(i.media);return l?r.jsx("a",{href:l,target:"_blank",rel:"noopener noreferrer",style:{flex:"0 0 auto"},children:r.jsx("img",{src:l,alt:i.description||"",style:{width:40,height:40,borderRadius:"50%",objectFit:"cover",display:"block"},onError:c=>{c.currentTarget.style.display="none"}})}):null}case 12:{const c=(i.items||[]).filter(d=>jn(d.media));return c.length===0?null:r.jsx("div",{style:{display:"grid",gridTemplateColumns:`repeat(auto-fill, minmax(${Math.min(220,Math.max(140,Math.floor(560/Math.max(1,c.length))))}px, 1fr))`,gap:6,margin:"6px 0"},children:c.map((d,m)=>{const p=jn(d.media),g=d.description;return Fp(d.media)?r.jsxs("figure",{style:{margin:0},children:[r.jsx("video",{src:p,controls:!0,preload:"metadata",style:{width:"100%",maxHeight:260,borderRadius:6,background:"#1e1f22"}}),g&&r.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:g})]},m):ed(p)?r.jsxs("figure",{style:{margin:0},children:[r.jsx("a",{href:p,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:r.jsx("img",{src:p,alt:g||"",style:{width:"100%",maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:T=>{T.currentTarget.style.display="none"}})}),g&&r.jsx("figcaption",{style:{color:"#949ba4",fontSize:11,marginTop:2},children:g})]},m):r.jsxs("a",{href:p,target:"_blank",rel:"noopener noreferrer",style:{display:"flex",alignItems:"center",gap:6,padding:"6px 10px",background:"#383a40",borderRadius:6,color:"#dbdee1",fontSize:12,textDecoration:"none"},children:["📎 ",g||"Attachment"]},m)})})}case 13:{const l=jn(i.media)||i.url||"";return l?r.jsxs("a",{href:l,target:"_blank",rel:"noopener noreferrer",style:{display:"block",margin:"4px 0",color:"#00a8fc",fontSize:12.5,textDecoration:"none"},children:["📎 ",i.label||"Attachment"]}):null}default:return null}}function Vp({components:i}){return r.jsx(r.Fragment,{children:i.map((l,c)=>r.jsx(Zs,{component:l},c))})}function Hp({text:i}){return r.jsx(wn,{text:i})}function Gp({msg:i}){const l=!!(i.attachments&&i.attachments.length>0||i.embeds&&i.embeds.length>0||i.components&&i.components.length>0||i.stickers&&i.stickers.length>0);return r.jsxs("div",{style:{padding:"10px 16px",borderBottom:"1px solid #2b2d31",fontSize:14,lineHeight:1.6},children:[r.jsxs("div",{style:{marginBottom:2},children:[r.jsx("span",{style:{color:"#949ba4",fontSize:11,fontFamily:"monospace"},children:i.timestamp})," ",r.jsx("span",{style:{color:"#f2f3f5",fontWeight:600},children:i.author})," ",r.jsxs("span",{style:{color:"#949ba4",fontSize:11},children:["(",i.author_id,")"]})]}),i.content?r.jsx("div",{style:{color:"#dbdee1"},children:r.jsx(Hp,{text:i.content})}):l?null:r.jsx("div",{style:{color:"#6d737a",fontStyle:"italic",fontSize:13},children:"Message content unavailable"}),i.attachments&&i.attachments.length>0&&r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:4},children:i.attachments.map((c,d)=>td(c)?r.jsx("video",{src:c,controls:!0,preload:"metadata",style:{maxWidth:360,maxHeight:260,borderRadius:6,background:"#1e1f22"}},d):ed(c)?r.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:r.jsx("img",{src:c,alt:"",style:{maxWidth:300,maxHeight:260,objectFit:"cover",borderRadius:6,display:"block",background:"#1e1f22"},onError:m=>{const p=m.currentTarget;p.style.display="none"}})},d):r.jsx("a",{href:c,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",fontSize:12,textDecoration:"none"},children:"📎 Attachment"},d))}),i.embeds&&i.embeds.length>0&&r.jsx(r.Fragment,{children:i.embeds.map((c,d)=>r.jsx($p,{embed:c},d))}),i.stickers&&i.stickers.length>0&&r.jsx("div",{style:{display:"flex",flexWrap:"wrap",gap:8,marginTop:8},children:i.stickers.map((c,d)=>{const m=Ip(c);return m?r.jsx("a",{href:m,target:"_blank",rel:"noopener noreferrer",style:{display:"block"},children:r.jsx("img",{src:m,alt:c.name||"Discord sticker",title:c.name||"Discord sticker",style:{width:160,maxWidth:"100%",maxHeight:160,objectFit:"contain",display:"block"}})},d):null})}),i.components&&i.components.length>0&&r.jsx(Vp,{components:i.components})]})}function Kp({transcriptId:i}){const[l,c]=_.useState(null),[d,m]=_.useState(!0),[p,g]=_.useState("");_.useEffect(()=>{m(!0),g(""),fetch(`/api/transcript/${i}`).then(k=>{if(!k.ok)throw new Error("Transcript not found");return k.json()}).then(k=>{c(k),m(!1)}).catch(k=>{g(k.message||"Failed to load transcript"),m(!1)})},[i]);const T=k=>{window.open(`/api/transcript/${i}/download?format=${k}`,"_blank")};return d?r.jsx("div",{className:"page-main",children:r.jsx("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:r.jsx("div",{style:{color:"var(--muted)",fontSize:14},children:"Loading transcript…"})})}):p||!l?r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:[r.jsx("h2",{style:{marginBottom:12},children:"Transcript not found"}),r.jsx("p",{style:{color:"var(--muted)"},children:p||"This transcript doesn't exist or has been deleted."})]})}):r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{maxWidth:800},children:[r.jsx("div",{style:{background:"var(--surface)",border:"1px solid var(--line)",borderRadius:8,padding:24,marginBottom:20},children:r.jsxs("div",{style:{display:"flex",alignItems:"flex-start",justifyContent:"space-between",gap:16,flexWrap:"wrap"},children:[r.jsxs("div",{children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:8},children:"Ticket Transcript"}),r.jsxs("h1",{style:{fontSize:24,letterSpacing:"-0.04em",margin:0},children:["#",l.channel_name]}),r.jsxs("div",{style:{color:"var(--muted)",fontSize:13,marginTop:6},children:[l.category," · ",l.message_count," messages · ",l.created_at]})]}),r.jsx("div",{style:{display:"flex",gap:8,flexWrap:"wrap"},children:Dp.map(k=>r.jsxs("button",{className:"button button-small button-muted",onClick:()=>T(k.key),style:{minWidth:70},children:[r.jsx("span",{children:k.icon}),r.jsx("span",{children:k.label})]},k.key))})]})}),r.jsxs("div",{style:{background:"#1e1f22",border:"1px solid #3f4147",borderRadius:8,overflow:"hidden"},children:[l.messages.map((k,D)=>r.jsx(Gp,{msg:k},D)),l.messages.length===0&&r.jsx("div",{style:{padding:40,textAlign:"center",color:"#949ba4"},children:"No messages in this transcript."})]}),r.jsxs("div",{style:{marginTop:16,padding:"12px 0",textAlign:"center",color:"var(--dim)",fontSize:12},children:["Transcript ID: ",r.jsx("code",{style:{fontFamily:"monospace"},children:i})]})]})})}const na=[{slug:"september-platform-updates",title:"September Platform Updates",date:"2026-09-21",version:"2.9.0",tags:["dashboard","ai","tickets","music","website"],summary:"A broad set of public improvements landed across Niko: richer ticket transcripts, a multimodal AI experiment, more reliable music playback, a redesigned dashboard experience, persistent giveaways and suggestions, and a refreshed public website with dynamic social previews.",highlights:[{title:"More Natural AI Conversations",description:"The new opt-in Multimodal Conversation experiment can understand image attachments and transcribe voice messages before generating a reply, while safely falling back to text when media processing is unavailable.",icon:"spark"},{title:"Richer Ticket Transcripts",description:"Transcript pages and HTML downloads now render Discord custom emojis, stickers, and dynamic timestamps such as <t:1788800225:f> in a more faithful format.",icon:"doc"},{title:"Dashboard & Website Refresh",description:"Dashboard navigation and mobile layouts were refined, documentation was expanded, and public routes now receive route-specific Open Graph cards generated during the build.",icon:"settings"},{title:"Reliable Long-Running Features",description:"Giveaways and suggestions now restore their state from the main database at startup, while music nodes are rescanned periodically to keep playback available.",icon:"utility"}],changes:[{category:"added",items:["Opt-in Multimodal Conversation AI experiment for image understanding and voice-message transcription","Official update notification system with a configurable server notification channel","Discord custom emoji and sticker rendering in ticket transcript pages and HTML downloads","Dynamic Discord timestamp rendering in ticket transcripts","Persistent suggestion configuration and voting buttons restored from the main database","Automatic hourly Lavalink node rescans with a hardcoded fallback node catalog","Additional economy SVG card API endpoints","Community Policy page on the public website","Route-specific Open Graph metadata and generated social preview cards"]},{category:"improved",items:["Dashboard navigation consistency and mobile layout","Dashboard page layout and visual polish","Music connection reliability, autoplay, Spotify playback, and node recovery","Giveaway persistence and startup restoration for MongoDB-backed data","Onboarding setup handling and configuration persistence","Poll command design and interaction flow","Ticket transcript HTML download formatting","Economy image-card font rendering, SVG output, and emoji support","Documentation pages and public website frontend"]},{category:"fixed",items:["Giveaways losing their live buttons after a restart or extended runtime","Suggestion buttons and configuration not surviving process restarts","Ticket transcript rendering for custom media and dynamic timestamps","Lavalink connection failures and stale music nodes","Broken SVG card and SVG endpoint output","Status panel polling noise and retired image-model defaults"]}],chart:{type:"metrics",title:"Release At a Glance",data:[{label:"Added",value:"9",detail:"new capabilities",color:"#66866f"},{label:"Improved",value:"9",detail:"upgraded systems",color:"#4a7fb5"},{label:"Fixed",value:"6",detail:"reliability issues",color:"#d96545"}]},commits:["ac102df Fixed the Open Graph image cards","33aaf12 Added dynamic Open Graph tags to the website","3153e28 Rebuilt the frontend","bab665e Added a new Lavalink node","ee44a5e Improved the music cog","bc61e34 Released the new Multimodal Conversation AI experiment","c46af7d Fixed the suggestion system persistence","25703ca Added a broadcast system for official updates and announcements","265bdb2 Added dynamic timestamp rendering inside ticket transcripts","d8005db Added custom emoji and sticker rendering to ticket transcripts","e561d84 Fixed the dashboards navbar","a0bab78 Improved the dashboards mobile layout","fb2f5aa Patched giveaway persistence for MongoDB compatibility","d77779e Fixed several dashboard flaws","b8e06a5 Improved the dashboard pages","3708207 Patched issues in the giveaway and onboarding cogs","d58bb37 Redesigned the poll command","bb523e3 Added a Community Policy page","5b34c7c Updated the documentation pages","3a52fc2 Added new economy card API endpoints","df3ea25 Fixed an issue in the SVG endpoints","39b7340 Fixed an error in the SVG cards","9e3483e Replaced HTML entities with valid XML numeric character references in economy cards"]},{slug:"economy-leveling-overhaul",title:"Economy Items, Leveling Cards & Subcommands",date:"2026-09-08",version:"2.8.0",tags:["economy","leveling","shop","image-cards"],summary:"The economy shop expanded with four new consumable items that affect gameplay — Rigged Coin, Streak Insurance, Double Down Token, and Lucky Horseshoe — plus daily streak milestone bonuses at 7, 14, 30, 60, and 90 days. The leveling system now renders rank cards and leaderboards as customizable image cards, and all leveling commands live under a single `/leveling` group with subcommands.",highlights:[{title:"New Shop Items",description:"Four new consumables: Rigged Coin (60/40 coinflip odds), Streak Insurance (protects daily streak for one missed day), Double Down Token (1.5x gambling payout), and Lucky Horseshoe (+10% work reward).",icon:"chart"},{title:"Leveling Image Cards",description:"Rank cards and the leaderboard now render as styled images with avatar, level, XP bar, and rank. Server admins can customize the card accent color and background gradient.",icon:"spark"},{title:"Leveling Subcommands",description:"All leveling commands reorganized under `/leveling` with `rank`, `leaderboard`, `panel`, and `config` subcommands. The leaderboard now has interactive pagination buttons.",icon:"settings"},{title:"Daily Streak Milestones",description:"Hitting 7, 14, 30, 60, or 90-day daily streaks now awards bonus items from the shop (Espresso Shots, Lockpicks, Lucky Charms, Rob Shields) along with a coin bonus.",icon:"utility"}],changes:[{category:"added",items:["Coinflip command with heads/tails call and double-or-nothing payout","Rigged Coin shop item — gives 60/40 coinflip odds for one use","Streak Insurance shop item — protects daily streak if you miss one day","Double Down Token shop item — next gambling win pays 1.5x","Lucky Horseshoe shop item — next work reward gets +10%","Daily streak milestone bonuses at 7/14/30/60/90 days with item rewards","Image card rendering for `/leveling rank` with customizable accent and background","Image card rendering for the leveling leaderboard","Inventory display as an image card in the shop command","Twemoji emoji rendering in economy card images","Pagination buttons (◀ ▶) on the leveling leaderboard","Card customization fields in the database: card_accent, card_bg_top, card_bg_bottom"]},{category:"improved",items:["Leveling commands restructured as `/leveling rank`, `leaderboard`, `panel`, `config` subcommands","Shop command visual layout with better font rendering on economy image cards","Crime and rob commands now check for gambling_boost effect for 1.5x payout","HTML download format for ticket transcripts","Dashboard UI refinements"]},{category:"fixed",items:["Command name conflicts between leveling and other cogs","Missing import in leveling cog after image card addition","Duplicate command alias in leveling system","Command name conflict in the gambling cog"]}],chart:{type:"bar",title:"New Shop Items & Their Effects",data:[{label:"Rigged Coin",value:3e3,color:"#c9a84c"},{label:"Streak Insurance",value:4e3,color:"#4a7fb5"},{label:"Double Down Token",value:5e3,color:"#d96545"},{label:"Lucky Horseshoe",value:2500,color:"#66866f"}]},commits:["41d86fb Expanded the gambling and economy system","bd6a09c Added image cards to the leveling system","5307bb1 Moved the leveling commands to the levels subcommand","dafd224 Added an image card to the inventory command","49fc83b Added emoji rendering to the shop command","0aca6ba Improved the shop command","30c9735 Added better font rendering to the economy system image cards","2b96835 Fixed a command name conflict","158ad8f Fixed a command name conflict in the gambling cog","d465598 Fixed a missing import","1f24ffb Fixed a duplicate command alias"]},{slug:"database-migration",title:"Database Migration to MongoDB",date:"2026-09-03",version:"2.7.0",tags:["database","mongodb","migration","infrastructure"],summary:"Every major system has been migrated from SQLite to MongoDB. The migration covered economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and the blacklist — with a custom interpreter that translates SQLite-style writes to MongoDB operations.",highlights:[{title:"Full MongoDB Migration",description:"Economy, leveling, moderation, tickets, birthdays, AFK, sticky messages, warns, mutes, and blacklist now all store data in MongoDB instead of SQLite.",icon:"settings"},{title:"Slash Command Sync Safeguard",description:"A new check prevents redundant Discord API calls when all commands are already registered, reducing rate-limit issues on startup.",icon:"utility"},{title:"Proxy Integration",description:"A new proxy manager reduces downtime on shared hosting environments by routing API requests through a proxy layer.",icon:"shield"}],changes:[{category:"migrated",items:["Economy system — balances, banks, jobs, achievements, inventory","Leveling system — XP, levels, role rewards, card customization","Moderation system — warnings, mutes, automod config","Ticket system — panels, transcripts, support roles","Birthday system — dates, channels, messages","AFK system — status, timestamps","Sticky messages — content, channels","Blacklist — users, words, filters"]},{category:"added",items:["MongoDB interpreter that translates SQLite-style writes to proper MongoDB operations","Proxy manager for shared hosting reliability","Slash command sync safeguard to prevent redundant API calls","Context menu command support in the sync utility"]},{category:"fixed",items:["MongoDB interpreter not translating all SQLite write patterns correctly","Economy interest calculation after migration","Birthday system data persistence","Several database connection issues across various cogs","Leveling database initialization issue"]}],chart:{type:"donut",title:"Systems Migrated to MongoDB",centerLabel:"8 systems",data:[{label:"Economy",value:1,color:"#d96545"},{label:"Leveling",value:1,color:"#66866f"},{label:"Moderation",value:1,color:"#4a7fb5"},{label:"Tickets",value:1,color:"#c9a84c"},{label:"Birthdays",value:1,color:"#b07cc6"},{label:"AFK",value:1,color:"#e0976e"},{label:"Sticky Msgs",value:1,color:"#7ca898"},{label:"Blacklist",value:1,color:"#8c918e"}]},commits:["c07f9b1 Fixed the MongoDB interpreter to properly translate all SQLite database writes","0d3aca5 Migrated the blacklist to the main database","954ebac Migrated the birthday system to the main database","5013d54 Migrated the warns and mutes to use the main database","f29c217 Migrated the afk system to the main database","5732b48 Migrated the sticky messages to use the main database","b0524f1 Migrated the ticket system to the main database","70e6d7a Fixed the sync util to support context commands and slash groups","2c01817 Added a safeguard to prevent slash command syncs when all commands are already present","121afcf Added a proxy integration to reduce downtime on shared hosting","9f2f1fd Fixed several database issues across various cogs"]},{slug:"ticket-system-transcripts",title:"Ticket Transcripts & VoiceMaster",date:"2026-09-03",version:"2.6.0",tags:["tickets","transcripts","voicemaster"],summary:"The ticket system gained a web-based transcript viewer that renders ticket conversations as styled HTML pages. The VoiceMaster was also improved with better reliability and database usage. Ticket transcripts can now be downloaded as HTML or viewed online.",highlights:[{title:"Web Transcript Viewer",description:"Ticket transcripts are now rendered as styled HTML pages that can be viewed online. The HTML download format was also improved for better readability.",icon:"doc"},{title:"VoiceMaster Reliability",description:"The VoiceMaster (temporary voice channels) was improved with better database usage and reliability fixes.",icon:"utility"},{title:"Donation Dashboard Page",description:"A new customization page in the dashboard lets server admins configure donation settings without using commands.",icon:"settings"}],changes:[{category:"added",items:["Web-based ticket transcript viewer with styled HTML output","Ticket transcript database table for storing transcripts online","Dashboard customization page for donation system settings"]},{category:"improved",items:["HTML download format for ticket transcripts","VoiceMaster reliability and database usage patterns","Ticket system persistence and data handling"]},{category:"fixed",items:["Ticket transcript pages rendering incorrectly","Ticket system data loss on restart","Ticket transcript generation issues","Ticket transcript page display bugs"]}],commits:["e953321 Added a new web transcript feature to the ticket system","aa0b73b Improved the donation system and added a customization page to the dashboard","3255385 Improved the html download format for the ticket transcripts","45f1fb0 Fixed the ticket system persistence","ef4e057 Added the ticket system database migrations","d4e0bc8 Fixed the ticket transcripts","4bf5e04 Fixed an issue with the ticket transcript pages","e8dbcb0 Improved the VoiceMaster reliability and improved the database usage"]},{slug:"roleplay-music-status",title:"Roleplay, Music & Status Rotation",date:"2026-09-05",version:"2.5.0",tags:["roleplay","music","status","social"],summary:"The roleplay cog was completely rewritten to use nekos.best API GIFs with CV2 layout messages and a persistent 'hug back' button. The music cog was restructured with a ghost queue feature and fixed autoplay/Spotify playback. A status message rotation system was added with a configurable timer.",highlights:[{title:"Roleplay Rewrite",description:"The roleplay cog now fetches SFW reaction GIFs from nekos.best, renders them in styled CV2 containers, and includes a 'hug back' button that persists across restarts. A single user context menu replaces individual action menus to stay under Discord's 15-command cap.",icon:"users"},{title:"Music Ghost Queue",description:"A new ghost queue feature lets songs be queued even when nothing is currently playing. Autoplay and Spotify playback were also fixed.",icon:"utility"},{title:"Status Rotation",description:"The bot now rotates through configurable status messages on a timer (default 30s interval), with activity types and a VR device presence.",icon:"spark"}],changes:[{category:"added",items:["Status message rotation with configurable interval and activity types","Persistent status panel command for the support server (owner only)","Roleplay block feature to prevent specific users from being targeted","Ghost queue feature — queue songs even when nothing is playing","User context menu for roleplay actions (replaces per-action menus)","YouTube channel name validation for notification system"]},{category:"improved",items:["Roleplay cog complete rewrite — nekos.best GIFs, CV2 layouts, persistent buttons","Social media notification emoji formatting (Bluesky, Reddit, TikTok, Twitch icons)","Music node connection system and autoplay reliability","Spotify playback quality","Music cog restructured with better error handling"]},{category:"fixed",items:["Status rotator startup errors and activity conflicts","on_ready event error handling and reliability","Lavalink connection bug","Roleplay prefix command handling","Bluesky and Reddit notification delivery issues"]}],commits:["0c58178 Redesigned the roleplay cog","6c4ee09 Fixed the roleplay prefix commands","f1f8591 Added a roleplay block feature","e01e3e4 Added status message rotation","5e63e1d Added a persistent status panel","ae7501a Restructured the music cog","526813e Added a new ghost queue feature to the music cog","6524da1 Improved the music node connection system, fixed the autoplay, and fixed the Spotify playback","4264677 Fixed a lavalink connection bug","d62ead8 Improved the social media notification system's emojis","0f0305d Improved the social media notification formatting","42069d4 Added proper channel name validation to the YouTube notification system"]},{slug:"moderation-logging-dashboard",title:"Logging, Moderation & Documentation",date:"2026-09-07",version:"2.4.0",tags:["logging","moderation","documentation","dashboard"],summary:"Logging got two major improvements: deleted message logs now show image attachments in a MediaGallery component, and the Member category now tracks avatar changes using a Section with Thumbnail accessory. The documentation page was fully rebuilt with search, filters, and a card-based layout.",highlights:[{title:"Image Attachments in Logs",description:"Deleted message logs now render attached images in a MediaGallery component inside the log container, so moderators can see what was posted without leaving Discord.",icon:"chart"},{title:"Avatar Change Tracking",description:"The Member logging category now detects avatar changes (global and server avatars) and displays them in a Section with a Thumbnail accessory showing the new avatar.",icon:"users"},{title:"Documentation Redesign",description:"The documentation page was rebuilt from scratch with a search bar, category filters, tag cloud, card-based layout, and individual article pages with table of contents.",icon:"doc"}],changes:[{category:"added",items:["Image attachments rendered in deleted message logs via MediaGallery","Avatar change detection in Member logging with Section + Thumbnail display","Startup economy cache that loads all users into memory for accurate leaderboards","Error handler for role menu post buttons","Full-text search with result highlighting in documentation","Category filters and tag cloud in documentation","Individual documentation article pages with table of contents"]},{category:"improved",items:["Logging system now supports media_urls, thumbnail_url, and files parameters","Commands page expanded with better organization","Dashboard UI refinements","Economy interest feature — skips malformed records with non-integer user IDs"]},{category:"fixed",items:["Logging command issues","Documentation command references","Status device detection issue","Status rotator conflicts between multiple status types","on_ready event reliability with proper error handling"]}],commits:["722a34f Added avatar updates to the logging cogs Member logs","1d82ea1 Moved file attachments inside the main log message for the deleted message logs","358d537 Added a startup economy cache to fix the leaderboard","566e0c4 Improved the dashboard","132bcbb Fully redesigned the documentation page","4f7a89a Improved the commands page","6d953b6 Fixed the logging command","a202687 Fixed some documentation issues","49d22ad Fixed the documentation command references","52de287 Added an error handler to the post role menu button"]},{slug:"website-launch-donation",title:"Website, Donation System & API",date:"2026-09-02",version:"2.3.0",tags:["website","donations","api"],summary:"The public website and documentation portal launched with a React + Vite frontend, documentation center with search, and a commands reference page. The donation system gained a dashboard customization page, and the Flask API backend was fixed to use proper database calls.",highlights:[{title:"Public Website",description:"A complete public website built with React and Vite featuring a landing page, documentation center, command reference, dashboard, and legal pages.",icon:"spark"},{title:"Documentation Center",description:"The documentation page was redesigned with a card-based layout, individual article pages, and a modern visual design matching the bot's aesthetic.",icon:"doc"},{title:"Donation Dashboard",description:"Server admins can now configure donation settings through a new dashboard page instead of relying solely on commands.",icon:"settings"}],changes:[{category:"added",items:["Public website with landing page, documentation center, and command reference","Donation system customization page in the dashboard","Ticket transcript viewer web page","Donate page with Oxapay integration"]},{category:"improved",items:["Flask API to use proper database calls instead of direct SQLite access","Website commands page with expanded details","Database layer reliability for production"]},{category:"fixed",items:["Flask API database call issues","Several database-related bugs across cogs","node_modules folder accidentally committed to repository"]}],commits:["132bcbb Fully redesigned the documentation page","aa0b73b Improved the donation system and added a customization page to the dashboard","bd5e3be Expanded the website's commands page","e266644 Fixed the flask API to use the proper database calls","e99ed47 Fixed several database related issues","c783514 Minor API fixes and improvements","0df4478 Added the node_modules folder to the gitignore file"]}];function qp(i){return na.find(l=>l.slug===i)}function Qp(){const i=new Set;return na.forEach(l=>l.tags.forEach(c=>i.add(c))),Array.from(i).sort()}function Xp(){const[i,l]=_.useState(""),c=Qp(),d=i?na.filter(m=>m.tags.includes(i)):na;return r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"home"}),r.jsxs("main",{className:"shell page-main changelog-page",children:[r.jsxs("div",{className:"changelog-hero",children:[r.jsxs("div",{className:"eyebrow",children:[r.jsx("span",{className:"status-dot"})," What's new"]}),r.jsxs("h1",{className:"changelog-title",children:["Changelog",r.jsx("br",{}),r.jsx("span",{className:"title-accent",children:"& updates"})]}),r.jsx("p",{className:"changelog-subtitle",children:"A record of every improvement, fix, and new feature added to Niko. Grouped by release for clarity."})]}),r.jsxs("div",{className:"changelog-tags",children:[r.jsx("button",{className:`changelog-tag-btn ${i===""?"active":""}`,onClick:()=>l(""),children:"All"}),c.slice(0,12).map(m=>r.jsx("button",{className:`changelog-tag-btn ${i===m?"active":""}`,onClick:()=>l(m),children:m},m))]}),r.jsx("div",{className:"changelog-timeline",children:d.map((m,p)=>r.jsxs("article",{className:"changelog-entry",children:[r.jsxs("div",{className:"changelog-entry-date-col",children:[r.jsx("div",{className:"changelog-date-dot"}),p<d.length-1&&r.jsx("div",{className:"changelog-date-line"})]}),r.jsxs("div",{className:"changelog-entry-card",children:[r.jsxs("div",{className:"changelog-entry-header",children:[r.jsxs("div",{className:"changelog-entry-meta",children:[r.jsx("time",{className:"changelog-entry-date",children:new Date(m.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),m.version&&r.jsxs("span",{className:"changelog-version",children:["v",m.version]})]}),r.jsx("h2",{className:"changelog-entry-title",children:m.title}),r.jsx("p",{className:"changelog-entry-summary",children:m.summary})]}),r.jsx("div",{className:"changelog-entry-highlights",children:m.highlights.slice(0,2).map(g=>r.jsxs("div",{className:"changelog-highlight-mini",children:[r.jsx("span",{className:"highlight-mini-icon",children:r.jsx(q,{name:g.icon,size:16})}),r.jsxs("div",{children:[r.jsx("strong",{children:g.title}),r.jsxs("p",{children:[g.description.slice(0,120),"..."]})]})]},g.title))}),r.jsx("div",{className:"changelog-entry-tags",children:m.tags.map(g=>r.jsx("span",{className:"changelog-tag",children:g},g))}),r.jsxs("button",{className:"changelog-read-more",onClick:()=>{oe(`/changelog/${m.slug}`)},children:["Read full release notes ",r.jsx(q,{name:"arrow",size:14})]})]})]},m.slug))}),d.length===0&&r.jsxs("div",{className:"changelog-empty",children:[r.jsx(q,{name:"doc",size:40}),r.jsx("p",{children:"No changelog entries match this filter."})]})]}),r.jsx(Nt,{})]})}function Yp({slug:i}){const l=qp(i);return l?r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"home"}),r.jsxs("main",{className:"shell page-main changelog-page changelog-detail",children:[r.jsx("div",{className:"changelog-back",children:r.jsxs("button",{onClick:()=>oe("/changelog"),className:"back-button",children:[r.jsx(q,{name:"arrow",size:16}),"Back to Changelog"]})}),r.jsxs("header",{className:"changelog-detail-header",children:[r.jsxs("div",{className:"changelog-detail-meta",children:[r.jsx("time",{children:new Date(l.date).toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"})}),l.version&&r.jsxs("span",{className:"changelog-version",children:["v",l.version]})]}),r.jsx("h1",{children:l.title}),r.jsx("p",{className:"changelog-detail-summary",children:l.summary}),r.jsx("div",{className:"changelog-detail-tags",children:l.tags.map(c=>r.jsx("span",{className:"changelog-tag",children:c},c))})]}),r.jsxs("section",{className:"changelog-highlights-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"Highlights"}),r.jsx("div",{className:"changelog-highlights-grid",children:l.highlights.map(c=>r.jsxs("div",{className:"changelog-highlight-card",children:[r.jsx("span",{className:"highlight-icon",children:r.jsx(q,{name:c.icon,size:22})}),r.jsx("h3",{children:c.title}),r.jsx("p",{children:c.description})]},c.title))})]}),l.chart&&r.jsx(Jp,{chart:l.chart}),r.jsxs("section",{className:"changelog-changes-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"All Changes"}),r.jsx("div",{className:"changelog-changes-grid",children:l.changes.map(c=>r.jsxs("div",{className:`changelog-change-group changelog-change-${c.category}`,children:[r.jsx("h3",{className:"change-group-title",children:r.jsx("span",{className:`change-badge change-badge-${c.category}`,children:c.category})}),r.jsx("ul",{children:c.items.map((d,m)=>r.jsx("li",{children:d},m))})]},c.category))})]}),l.commits.length>0&&r.jsxs("section",{className:"changelog-commits-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:"Commits"}),r.jsx("div",{className:"changelog-commits-list",children:l.commits.map(c=>{const[d,...m]=c.split(" ");return r.jsxs("div",{className:"changelog-commit",children:[r.jsx("code",{className:"commit-hash",children:d.slice(0,7)}),r.jsx("span",{className:"commit-msg",children:m.join(" ")})]},d)})})]}),r.jsx("nav",{className:"changelog-detail-nav",children:r.jsxs("button",{onClick:()=>oe("/changelog"),children:[r.jsx(q,{name:"arrow",size:14}),"All releases"]})})]}),r.jsx(Nt,{})]}):r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"home"}),r.jsx("main",{className:"shell page-main changelog-page",children:r.jsxs("div",{className:"changelog-not-found",children:[r.jsx(q,{name:"doc",size:48}),r.jsx("h1",{children:"Entry Not Found"}),r.jsxs("p",{children:[`We couldn't find a changelog entry for "`,i,'".']}),r.jsx("button",{onClick:()=>oe("/changelog"),children:"View all changelog entries"})]})}),r.jsx(Nt,{})]})}function Jp({chart:i}){return r.jsxs("section",{className:"changelog-chart-section",children:[r.jsx("h2",{className:"changelog-section-heading",children:i.title}),r.jsxs("div",{className:"changelog-chart-container",children:[i.type==="bar"&&r.jsx(Zp,{chart:i}),i.type==="pie"&&r.jsx(ef,{chart:i}),i.type==="donut"&&r.jsx(tf,{chart:i}),i.type==="line"&&r.jsx(nf,{chart:i}),i.type==="timeline"&&r.jsx(rf,{chart:i}),i.type==="comparison"&&r.jsx(af,{chart:i}),i.type==="metrics"&&r.jsx(sf,{chart:i})]})]})}function Zp({chart:i}){const l=Math.max(...i.data.map(c=>c.value));return r.jsx("div",{className:"chart-bar",children:i.data.map(c=>r.jsxs("div",{className:"chart-bar-row",children:[r.jsx("span",{className:"chart-bar-label",children:c.label}),r.jsxs("div",{className:"chart-bar-track",children:[r.jsx("div",{className:"chart-bar-fill",style:{width:`${c.value/l*100}%`,background:c.color||"var(--accent)"}}),r.jsx("span",{className:"chart-bar-value",children:c.value})]})]},c.label))})}function ef({chart:i}){const l=i.data.reduce((p,g)=>p+g.value,0);let c=0;const m=i.data.map(p=>{const g=c/l*360;c+=p.value;const T=c/l*360;return{...p,start:g,end:T}}).map(p=>{const g=p.start/360*100,T=p.end/360*100;return`${p.color||"#d96545"} ${g}% ${T}%`}).join(", ");return r.jsxs("div",{className:"chart-pie-wrapper",children:[r.jsx("div",{className:"chart-pie",style:{background:`conic-gradient(${m})`}}),r.jsx("div",{className:"chart-pie-legend",children:i.data.map(p=>r.jsxs("div",{className:"chart-legend-item",children:[r.jsx("span",{className:"chart-legend-dot",style:{background:p.color||"var(--accent)"}}),r.jsx("span",{className:"chart-legend-label",children:p.label})]},p.label))})]})}function tf({chart:i}){const l=i.data.reduce((d,m)=>d+m.value,0),c=i.data.reduce((d,m)=>{const p=d.current/l*100,g=(d.current+m.value)/l*100;return d.css+=`${m.color||"#d96545"} ${p}% ${g}%, `,d.current+=m.value,d},{css:"",current:0}).css.slice(0,-2);return r.jsxs("div",{className:"chart-donut-wrapper",children:[r.jsx("div",{className:"chart-donut",style:{background:`conic-gradient(${c})`},children:r.jsx("span",{children:i.centerLabel||l})}),r.jsx("div",{className:"chart-pie-legend",children:i.data.map(d=>r.jsxs("div",{className:"chart-legend-item",children:[r.jsx("span",{className:"chart-legend-dot",style:{background:d.color||"var(--accent)"}}),r.jsx("span",{className:"chart-legend-label",children:d.label})]},d.label))})]})}function nf({chart:i}){const l=Math.max(...i.data.map(d=>d.value),1),c=i.data.map((d,m)=>{const p=i.data.length===1?50:m/(i.data.length-1)*100,g=100-d.value/l*82-9;return`${p},${g}`}).join(" ");return r.jsxs("div",{className:"chart-line-wrapper",children:[r.jsxs("svg",{className:"chart-line",viewBox:"0 0 100 100",preserveAspectRatio:"none",role:"img","aria-label":i.title,children:[r.jsx("polyline",{points:c,fill:"none",stroke:"var(--accent)",strokeWidth:"3",vectorEffect:"non-scaling-stroke"}),i.data.map((d,m)=>{const p=i.data.length===1?50:m/(i.data.length-1)*100,g=100-d.value/l*82-9;return r.jsx("circle",{cx:p,cy:g,r:"3",fill:"var(--accent)",vectorEffect:"non-scaling-stroke"},d.label)})]}),r.jsx("div",{className:"chart-line-labels",children:i.data.map(d=>r.jsx("span",{children:d.label},d.label))})]})}function rf({chart:i}){const l=Math.max(...i.data.map(c=>c.value),1);return r.jsx("div",{className:"chart-timeline",children:i.data.map(c=>r.jsxs("div",{className:"chart-timeline-item",children:[r.jsx("div",{className:"chart-timeline-marker",style:{background:c.color||"var(--accent)"}}),r.jsxs("div",{className:"chart-timeline-content",children:[r.jsx("strong",{children:c.label}),r.jsx("div",{className:"chart-timeline-track",children:r.jsx("div",{className:"chart-timeline-fill",style:{width:`${c.value/l*100}%`,background:c.color||"var(--accent)"}})}),c.detail&&r.jsx("span",{children:c.detail})]})]},c.label))})}function sf({chart:i}){return r.jsx("div",{className:"chart-metrics",children:i.data.map(l=>r.jsxs("div",{className:"chart-metric",style:{borderTopColor:l.color||"var(--accent)"},children:[r.jsx("span",{className:"chart-metric-label",children:l.label}),r.jsx("strong",{children:l.value}),l.detail&&r.jsx("small",{children:l.detail})]},l.label))})}function af({chart:i}){const l=Math.max(...i.before.concat(i.after).map(d=>d.value),1),c=(d,m,p)=>r.jsxs("div",{className:"chart-comparison-col",children:[r.jsx("h4",{className:`comparison-label ${p}`,children:d}),m.map(g=>r.jsxs("div",{className:"chart-bar-row",children:[r.jsx("span",{className:"chart-bar-label",children:g.label}),r.jsxs("div",{className:"chart-bar-track",children:[r.jsx("div",{className:"chart-bar-fill",style:{width:`${g.value/l*100}%`,background:g.color||"var(--accent)"}}),r.jsx("span",{className:"chart-bar-value",children:g.value})]})]},g.label))]});return r.jsxs("div",{className:"chart-comparison",children:[c("Before",i.before,"comparison-before"),r.jsx("div",{className:"chart-comparison-divider",children:r.jsx(q,{name:"arrow",size:20})}),c("After",i.after,"comparison-after")]})}function ra(i){return i.avatar_url}function of(i){return`https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/svg/${Array.from(i).map(c=>c.codePointAt(0).toString(16)).join("-")}.svg`}function lf({emoji:i}){return i?i.kind==="custom"?r.jsx("img",{className:"presence-emoji",src:`https://cdn.discordapp.com/emojis/${i.value}.${i.animated?"gif":"png"}?size=18`,alt:i.name||"custom emoji"}):r.jsx("img",{className:"presence-emoji",src:of(i.value),alt:i.name||i.value}):null}function cf(i){return{playing:"Playing",listening:"Listening to",watching:"Watching",streaming:"Streaming",competing:"Competing in"}[i]||(i?`${i.charAt(0).toUpperCase()}${i.slice(1)}`:"Activity")}function uf({activity:i}){const l=i.kind==="spotify",c=l?"Listening on Spotify":cf(i.type),d=l?i.details||"Spotify":i.name,m=l?i.state:i.details,p=r.jsxs("span",{className:`activity-card activity-${i.kind}`,children:[i.image_url&&r.jsx("img",{className:"activity-art",src:i.image_url,alt:""}),r.jsxs("span",{className:"activity-copy",children:[r.jsx("strong",{children:c}),r.jsx("span",{children:d}),m&&r.jsx("small",{children:m})]})]});return i.url?r.jsx("a",{className:"presence-activity",href:i.url,target:"_blank",rel:"noreferrer",children:p}):r.jsx("span",{className:"presence-activity",children:p})}function rd(i){return i.status_label||{online:"Online",idle:"Idle",dnd:"Do Not Disturb",offline:"Offline"}[i.status||"offline"]||"Offline"}function sd({member:i}){const l=i.custom_status,c=i.activities||[],d=!!(l!=null&&l.text||l!=null&&l.emoji);return!d&&!c.length?null:r.jsxs("span",{className:"presence-stack",children:[d&&r.jsxs("span",{className:"presence-line",children:[r.jsx(lf,{emoji:l==null?void 0:l.emoji}),(l==null?void 0:l.text)||"Custom status"]}),c.length>0&&r.jsx("span",{className:"presence-line activity-list",children:c.map((m,p)=>r.jsx(uf,{activity:m},`${m.kind}-${m.name}-${p}`))})]})}const ad=`
.team-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:58px}.team-card{display:flex;flex-direction:column;min-width:0;min-height:286px;overflow:hidden;padding:0;color:var(--ink);text-align:left;background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow-soft)}.team-card:hover{border-color:#dfaa98;transform:translateY(-2px)}.team-card-art,.team-profile-banner{min-height:105px;background:linear-gradient(135deg,var(--callout),var(--surface-muted));background-size:cover;background-position:center}.team-card-body{display:flex;align-items:flex-start;flex:1;min-width:0;gap:14px;padding:18px}.team-card-body>div:last-child{min-width:0}.team-card h2,.team-card p{overflow-wrap:anywhere}.team-avatar,.team-profile-avatar{display:grid;place-items:center;flex:0 0 auto;overflow:hidden;color:#fffaf5;background:var(--accent);border-radius:50%;font-weight:800;object-fit:cover}.team-avatar{width:48px;height:48px;margin-top:-35px;border:3px solid var(--surface)}.team-role{color:var(--accent-dark);text-transform:uppercase;letter-spacing:.1em;font:700 9px "Space Mono",monospace}.team-card h2{margin:5px 0 6px;font-size:17px}.team-card p{margin:0 0 10px;color:var(--muted);font-size:11px;line-height:1.6}.team-status{color:var(--dim);font-size:10px}.presence-stack{display:block}.presence-line{display:flex;align-items:center;flex-wrap:wrap;gap:7px;margin-top:7px;color:var(--muted);font-size:10px}.presence-activity{display:inline-flex;align-items:center;gap:4px;color:inherit}.presence-activity:hover{text-decoration:none}.activity-card{display:flex;align-items:center;min-width:0;gap:8px;padding:7px 9px;background:var(--surface-muted);border:1px solid var(--line);border-radius:8px;text-align:left}.activity-art{width:30px;height:30px;flex:0 0 auto;border-radius:5px;object-fit:cover}.activity-copy{display:flex;min-width:0;flex-direction:column;gap:1px}.activity-copy strong{color:var(--accent-dark);font-size:9px;text-transform:uppercase;letter-spacing:.06em}.activity-copy span,.activity-copy small{overflow:hidden;max-width:210px;text-overflow:ellipsis;white-space:nowrap}.activity-copy span{color:var(--ink);font-size:10px}.activity-copy small{color:var(--dim);font-size:9px}.presence-emoji{width:18px;height:18px;object-fit:contain;vertical-align:middle}.is-online{color:var(--sage)}.team-profile-page{max-width:760px}.team-back{width:auto;margin:0 0 18px;border:0;background:transparent}.team-profile-banner{min-height:220px;border:1px solid var(--line);border-radius:14px 14px 0 0}.team-profile-card{padding:0 34px 38px;text-align:center;background:var(--surface);border:1px solid var(--line);border-top:0;border-radius:0 0 14px 14px;box-shadow:var(--shadow-soft)}.team-profile-avatar{width:100px;height:100px;margin:-50px auto 18px;border:5px solid var(--surface);font-size:32px}.team-profile-card h1{margin:8px 0 5px;font-size:34px;letter-spacing:-.07em}.team-profile-handle{color:var(--dim);font-size:11px}.team-profile-bio{max-width:560px;margin:27px auto 0;color:var(--muted);line-height:1.8}.team-activity{display:block;width:min(100%,560px);margin:20px auto 0;padding:12px;color:var(--muted);background:var(--surface-muted);border:1px solid var(--line);border-radius:12px;font-size:10px;text-align:left}.team-activity .presence-line{margin-top:0}.team-activity .activity-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));align-items:stretch}.team-activity .activity-card{height:100%;width:100%}@media(max-width:800px){.team-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.team-grid{grid-template-columns:1fr;margin-top:38px}.team-profile-card{padding-left:18px;padding-right:18px}.team-profile-banner{min-height:150px}}`;function df(){const[i,l]=_.useState([]);return _.useEffect(()=>{fh().then(l).catch(()=>l([]))},[]),r.jsxs(r.Fragment,{children:[r.jsx("style",{children:ad}),r.jsx(Ue,{page:"team"}),r.jsxs("main",{className:"shell page-main",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"The people behind Niko"}),r.jsx("h1",{children:"Meet the team."}),r.jsx("p",{children:"A small group of builders, moderators, and creative minds keeping Niko friendly, useful, and moving forward."})]}),r.jsxs("div",{className:"team-grid",children:[i.map(c=>r.jsxs("button",{className:"team-card",onClick:()=>oe(`/team/${c.id}`),children:[r.jsx("div",{className:"team-card-art",style:c.public_banner_url?{backgroundImage:`url(${c.public_banner_url})`}:void 0}),r.jsxs("div",{className:"team-card-body",children:[ra(c)?r.jsx("img",{className:"team-avatar",src:ra(c),alt:""}):r.jsx("span",{className:"team-avatar team-avatar-fallback",children:c.name.slice(0,1)}),r.jsxs("div",{children:[r.jsx("span",{className:"team-role",children:c.role_label}),r.jsx("h2",{children:c.name}),r.jsx("p",{children:c.bio||"Part of the Niko team."}),r.jsx("span",{className:`team-status status-${c.status||"offline"} ${c.status==="online"?"is-online":""}`,children:rd(c)}),r.jsx(sd,{member:c})]})]})]},c.id)),!i.length&&r.jsx("div",{className:"empty-state",children:"The team roster is being prepared."})]})]}),r.jsx(Nt,{})]})}function mf({id:i}){const[l,c]=_.useState(null),[d,m]=_.useState("");return _.useEffect(()=>{gh(i).then(c).catch(p=>m(p instanceof Error?p.message:"Team member not found."))},[i]),r.jsxs(r.Fragment,{children:[r.jsx("style",{children:ad}),r.jsx(Ue,{page:"team"}),r.jsx("main",{className:"shell page-main team-profile-page",children:d?r.jsx("div",{className:"empty-state",children:d}):l?r.jsxs(r.Fragment,{children:[r.jsx("button",{className:"back-link team-back",onClick:()=>oe("/team"),children:"← Back to team"}),r.jsx("div",{className:"team-profile-banner",style:l.public_banner_url?{backgroundImage:`url(${l.public_banner_url})`}:void 0}),r.jsxs("section",{className:"team-profile-card",children:[ra(l)?r.jsx("img",{className:"team-profile-avatar",src:ra(l),alt:""}):r.jsx("span",{className:"team-profile-avatar team-avatar-fallback",children:l.name.slice(0,1)}),r.jsx("div",{className:"team-role",children:l.role_label}),r.jsx("h1",{children:l.name}),r.jsxs("p",{className:"team-profile-handle",children:[l.username?`@${l.username}`:"Niko staff"," · ",r.jsx("span",{className:`status-${l.status||"offline"} ${l.status==="online"?"is-online":""}`,children:rd(l)})]}),r.jsx("p",{className:"team-profile-bio",children:l.bio||"This team member has not added an extended introduction yet."}),r.jsxs("div",{className:"team-activity",children:[r.jsx(sd,{member:l}),!l.custom_status&&!(l.activities||[]).length&&"No current activity"]})]})]}):r.jsx("div",{className:"section-loading",children:"Loading profile…"})}),r.jsx(Nt,{})]})}function hf(){const[i,l]=_.useState(null),[c,d]=_.useState(null),[m,p]=_.useState(null),[g,T]=_.useState([]),[k,D]=_.useState({public_bio:"",public_banner_url:"",public_visible:!0}),[N,C]=_.useState({avatar_url:"",banner_url:""}),[L,I]=_.useState(""),[A,B]=_.useState(""),[j,J]=_.useState(!1);if(_.useEffect(()=>{Promise.all([fo(),go(),ea(),vo()]).then(([O,ce,ge,Fe])=>{l(O),d(ce),p(ge),T(Fe);const Ce=ce.profile;D({public_bio:Ce.bio||"",public_banner_url:Ce.public_banner_url||"",public_visible:Ce.visible!==!1})}).catch(O=>B(O instanceof Error?O.message:"Staff access unavailable."))},[]),!i||!c&&!A)return r.jsxs("div",{className:"dashboard-state",children:[r.jsx("div",{className:"loading-ring"}),r.jsx("p",{children:"Checking staff access…"})]});if(A||!c||!i.authenticated)return r.jsxs(r.Fragment,{children:[r.jsx(Ue,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("div",{className:"eyebrow",children:"Staff workspace"}),r.jsx("h1",{children:"Private team area."}),r.jsx("p",{children:i!=null&&i.authenticated?A||"This area is only available to official Niko staff.":"Sign in with Discord to continue."}),!(i!=null&&i.authenticated)&&r.jsx("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard/staff",children:"Continue with Discord"}),r.jsx("button",{className:"back-link",onClick:()=>oe("/dashboard"),children:"Return to dashboard"})]})})]});const S=["owner","head_admin","graphic_designer"].includes(c.role),V=(O,ce)=>D(ge=>({...ge,[O]:ce})),ee=async()=>{if(!j){J(!0),B(""),I("");try{await vh(k,i.csrf_token),I("Your public team listing was saved.")}catch(O){B(O instanceof Error?O.message:"Could not save listing.")}finally{J(!1)}}},re=async()=>{B(""),I("");try{await yh(N,i.csrf_token),I("Niko's global profile was updated.")}catch(O){B(O instanceof Error?O.message:"Could not update global profile.")}},z=r.jsxs("div",{className:"staff-page",children:[r.jsxs("div",{className:"page-heading",children:[r.jsxs("div",{className:"eyebrow",children:["Staff workspace · ",c.role_label]}),r.jsx("h1",{children:"Shape your presence."}),r.jsx("p",{children:"Manage only the controls granted to your role. Support staff can maintain their public listing without touching global bot settings."})]}),r.jsxs("section",{className:"staff-panel",children:[r.jsx("div",{className:"panel-heading",children:r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Public listing"}),r.jsx("h2",{children:"How the team sees you"})]})}),r.jsxs("div",{className:"form-grid",children:[r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Banner URL"}),r.jsx("input",{value:k.public_banner_url,onChange:O=>V("public_banner_url",O.target.value),placeholder:"https://…"})]}),r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Extended introduction"}),r.jsx("textarea",{value:k.public_bio,onChange:O=>V("public_bio",O.target.value),maxLength:1200,placeholder:"Tell the community what you do…"})]})]}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Show me on the public Team page"}),r.jsx("small",{children:"Hide your listing without removing your staff access."})]}),r.jsx("input",{type:"checkbox",checked:k.public_visible,onChange:O=>V("public_visible",O.target.checked)}),r.jsx("i",{})]}),r.jsx("button",{type:"button",className:"button button-primary",onClick:ee,disabled:j,children:j?"Saving…":"Save public listing"})]}),S&&r.jsxs("section",{className:"staff-panel",children:[r.jsx("div",{className:"panel-heading",children:r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Graphic direction"}),r.jsx("h2",{children:"Global Niko profile"})]})}),r.jsx("p",{className:"form-hint",children:"Graphic Designers, Head Admins, and owners can update the bot-wide avatar and banner. Paste publicly reachable image URLs."}),r.jsxs("div",{className:"form-grid",children:[r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Bot avatar URL"}),r.jsx("input",{value:N.avatar_url,onChange:O=>C({...N,avatar_url:O.target.value})})]}),r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Bot banner URL"}),r.jsx("input",{value:N.banner_url,onChange:O=>C({...N,banner_url:O.target.value})})]})]}),r.jsx("button",{className:"button button-primary",onClick:re,children:"Update global profile"})]}),L&&r.jsx("div",{className:"notice",children:L}),A&&r.jsx("div",{className:"notice warning",children:A})]});return r.jsx(Xu,{user:i.user,guilds:g,selectedGuild:null,view:"overview",section:"overview",stats:m,staffRole:c.role,onHome:()=>oe(Xn()),onServers:()=>oe(yo()),onGuildChange:()=>{},onSectionChange:()=>{},onRefresh:()=>window.location.reload(),refreshing:!1,children:z})}function pf(){const[i,l]=_.useState(Mu);if(_.useEffect(()=>{const c=()=>l(Mu());return window.addEventListener("popstate",c),()=>window.removeEventListener("popstate",c)},[]),i==="commands")return r.jsx(np,{});if(i==="docs-detail"){const c=window.location.pathname.split("/"),d=c[c.length-1];return r.jsx(Ep,{slug:d})}if(i==="docs")return r.jsx(Mp,{});if(i==="staff")return r.jsx(hf,{});if(i==="dashboard")return r.jsx(bp,{});if(i==="team")return r.jsx(df,{});if(i==="team-member")return r.jsx(mf,{id:window.location.pathname.split("/").filter(Boolean)[1]||""});if(i==="privacy")return r.jsx(po,{type:"privacy"});if(i==="terms")return r.jsx(po,{type:"terms"});if(i==="community")return r.jsx(po,{type:"community"});if(i==="donate")return r.jsx(Rp,{});if(i==="transcript"){const d=window.location.pathname.split("/").filter(Boolean)[1]||"";return r.jsx(Kp,{transcriptId:d})}if(i==="changelog")return r.jsx(Xp,{});if(i==="changelog-detail"){const c=window.location.pathname.split("/"),d=c[c.length-1];return r.jsx(Yp,{slug:d})}return r.jsx(Pp,{})}mh.createRoot(document.getElementById("root")).render(r.jsx(_.StrictMode,{children:r.jsx(pf,{})}));
