var Am=Object.defineProperty;var Dm=(o,u,c)=>u in o?Am(o,u,{enumerable:!0,configurable:!0,writable:!0,value:c}):o[u]=c;var ic=(o,u,c)=>Dm(o,typeof u!="symbol"?u+"":u,c);(function(){const u=document.createElement("link").relList;if(u&&u.supports&&u.supports("modulepreload"))return;for(const p of document.querySelectorAll('link[rel="modulepreload"]'))f(p);new MutationObserver(p=>{for(const S of p)if(S.type==="childList")for(const w of S.addedNodes)w.tagName==="LINK"&&w.rel==="modulepreload"&&f(w)}).observe(document,{childList:!0,subtree:!0});function c(p){const S={};return p.integrity&&(S.integrity=p.integrity),p.referrerPolicy&&(S.referrerPolicy=p.referrerPolicy),p.crossOrigin==="use-credentials"?S.credentials="include":p.crossOrigin==="anonymous"?S.credentials="omit":S.credentials="same-origin",S}function f(p){if(p.ep)return;p.ep=!0;const S=c(p);fetch(p.href,S)}})();var qa={exports:{}},Rr={},Ya={exports:{}},re={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var ac;function Im(){if(ac)return re;ac=1;var o=Symbol.for("react.element"),u=Symbol.for("react.portal"),c=Symbol.for("react.fragment"),f=Symbol.for("react.strict_mode"),p=Symbol.for("react.profiler"),S=Symbol.for("react.provider"),w=Symbol.for("react.context"),z=Symbol.for("react.forward_ref"),x=Symbol.for("react.suspense"),B=Symbol.for("react.memo"),b=Symbol.for("react.lazy"),C=Symbol.iterator;function M(g){return g===null||typeof g!="object"?null:(g=C&&g[C]||g["@@iterator"],typeof g=="function"?g:null)}var D={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},I=Object.assign,F={};function j(g,T,ne){this.props=g,this.context=T,this.refs=F,this.updater=ne||D}j.prototype.isReactComponent={},j.prototype.setState=function(g,T){if(typeof g!="object"&&typeof g!="function"&&g!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,g,T,"setState")},j.prototype.forceUpdate=function(g){this.updater.enqueueForceUpdate(this,g,"forceUpdate")};function W(){}W.prototype=j.prototype;function N(g,T,ne){this.props=g,this.context=T,this.refs=F,this.updater=ne||D}var Q=N.prototype=new W;Q.constructor=N,I(Q,j.prototype),Q.isPureReactComponent=!0;var te=Array.isArray,se=Object.prototype.hasOwnProperty,_={current:null},X={key:!0,ref:!0,__self:!0,__source:!0};function me(g,T,ne){var ie,oe={},le=null,pe=null;if(T!=null)for(ie in T.ref!==void 0&&(pe=T.ref),T.key!==void 0&&(le=""+T.key),T)se.call(T,ie)&&!X.hasOwnProperty(ie)&&(oe[ie]=T[ie]);var ce=arguments.length-2;if(ce===1)oe.children=ne;else if(1<ce){for(var ye=Array(ce),it=0;it<ce;it++)ye[it]=arguments[it+2];oe.children=ye}if(g&&g.defaultProps)for(ie in ce=g.defaultProps,ce)oe[ie]===void 0&&(oe[ie]=ce[ie]);return{$$typeof:o,type:g,key:le,ref:pe,props:oe,_owner:_.current}}function je(g,T){return{$$typeof:o,type:g.type,key:T,ref:g.ref,props:g.props,_owner:g._owner}}function rt(g){return typeof g=="object"&&g!==null&&g.$$typeof===o}function We(g){var T={"=":"=0",":":"=2"};return"$"+g.replace(/[=:]/g,function(ne){return T[ne]})}var ze=/\/+/g;function $e(g,T){return typeof g=="object"&&g!==null&&g.key!=null?We(""+g.key):T.toString(36)}function st(g,T,ne,ie,oe){var le=typeof g;(le==="undefined"||le==="boolean")&&(g=null);var pe=!1;if(g===null)pe=!0;else switch(le){case"string":case"number":pe=!0;break;case"object":switch(g.$$typeof){case o:case u:pe=!0}}if(pe)return pe=g,oe=oe(pe),g=ie===""?"."+$e(pe,0):ie,te(oe)?(ne="",g!=null&&(ne=g.replace(ze,"$&/")+"/"),st(oe,T,ne,"",function(it){return it})):oe!=null&&(rt(oe)&&(oe=je(oe,ne+(!oe.key||pe&&pe.key===oe.key?"":(""+oe.key).replace(ze,"$&/")+"/")+g)),T.push(oe)),1;if(pe=0,ie=ie===""?".":ie+":",te(g))for(var ce=0;ce<g.length;ce++){le=g[ce];var ye=ie+$e(le,ce);pe+=st(le,T,ne,ye,oe)}else if(ye=M(g),typeof ye=="function")for(g=ye.call(g),ce=0;!(le=g.next()).done;)le=le.value,ye=ie+$e(le,ce++),pe+=st(le,T,ne,ye,oe);else if(le==="object")throw T=String(g),Error("Objects are not valid as a React child (found: "+(T==="[object Object]"?"object with keys {"+Object.keys(g).join(", ")+"}":T)+"). If you meant to render a collection of children, use an array instead.");return pe}function Nt(g,T,ne){if(g==null)return g;var ie=[],oe=0;return st(g,ie,"","",function(le){return T.call(ne,le,oe++)}),ie}function Ge(g){if(g._status===-1){var T=g._result;T=T(),T.then(function(ne){(g._status===0||g._status===-1)&&(g._status=1,g._result=ne)},function(ne){(g._status===0||g._status===-1)&&(g._status=2,g._result=ne)}),g._status===-1&&(g._status=0,g._result=T)}if(g._status===1)return g._result.default;throw g._result}var Se={current:null},O={transition:null},J={ReactCurrentDispatcher:Se,ReactCurrentBatchConfig:O,ReactCurrentOwner:_};function V(){throw Error("act(...) is not supported in production builds of React.")}return re.Children={map:Nt,forEach:function(g,T,ne){Nt(g,function(){T.apply(this,arguments)},ne)},count:function(g){var T=0;return Nt(g,function(){T++}),T},toArray:function(g){return Nt(g,function(T){return T})||[]},only:function(g){if(!rt(g))throw Error("React.Children.only expected to receive a single React element child.");return g}},re.Component=j,re.Fragment=c,re.Profiler=p,re.PureComponent=N,re.StrictMode=f,re.Suspense=x,re.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=J,re.act=V,re.cloneElement=function(g,T,ne){if(g==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+g+".");var ie=I({},g.props),oe=g.key,le=g.ref,pe=g._owner;if(T!=null){if(T.ref!==void 0&&(le=T.ref,pe=_.current),T.key!==void 0&&(oe=""+T.key),g.type&&g.type.defaultProps)var ce=g.type.defaultProps;for(ye in T)se.call(T,ye)&&!X.hasOwnProperty(ye)&&(ie[ye]=T[ye]===void 0&&ce!==void 0?ce[ye]:T[ye])}var ye=arguments.length-2;if(ye===1)ie.children=ne;else if(1<ye){ce=Array(ye);for(var it=0;it<ye;it++)ce[it]=arguments[it+2];ie.children=ce}return{$$typeof:o,type:g.type,key:oe,ref:le,props:ie,_owner:pe}},re.createContext=function(g){return g={$$typeof:w,_currentValue:g,_currentValue2:g,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},g.Provider={$$typeof:S,_context:g},g.Consumer=g},re.createElement=me,re.createFactory=function(g){var T=me.bind(null,g);return T.type=g,T},re.createRef=function(){return{current:null}},re.forwardRef=function(g){return{$$typeof:z,render:g}},re.isValidElement=rt,re.lazy=function(g){return{$$typeof:b,_payload:{_status:-1,_result:g},_init:Ge}},re.memo=function(g,T){return{$$typeof:B,type:g,compare:T===void 0?null:T}},re.startTransition=function(g){var T=O.transition;O.transition={};try{g()}finally{O.transition=T}},re.unstable_act=V,re.useCallback=function(g,T){return Se.current.useCallback(g,T)},re.useContext=function(g){return Se.current.useContext(g)},re.useDebugValue=function(){},re.useDeferredValue=function(g){return Se.current.useDeferredValue(g)},re.useEffect=function(g,T){return Se.current.useEffect(g,T)},re.useId=function(){return Se.current.useId()},re.useImperativeHandle=function(g,T,ne){return Se.current.useImperativeHandle(g,T,ne)},re.useInsertionEffect=function(g,T){return Se.current.useInsertionEffect(g,T)},re.useLayoutEffect=function(g,T){return Se.current.useLayoutEffect(g,T)},re.useMemo=function(g,T){return Se.current.useMemo(g,T)},re.useReducer=function(g,T,ne){return Se.current.useReducer(g,T,ne)},re.useRef=function(g){return Se.current.useRef(g)},re.useState=function(g){return Se.current.useState(g)},re.useSyncExternalStore=function(g,T,ne){return Se.current.useSyncExternalStore(g,T,ne)},re.useTransition=function(){return Se.current.useTransition()},re.version="18.3.1",re}var oc;function lo(){return oc||(oc=1,Ya.exports=Im()),Ya.exports}/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var lc;function zm(){if(lc)return Rr;lc=1;var o=lo(),u=Symbol.for("react.element"),c=Symbol.for("react.fragment"),f=Object.prototype.hasOwnProperty,p=o.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,S={key:!0,ref:!0,__self:!0,__source:!0};function w(z,x,B){var b,C={},M=null,D=null;B!==void 0&&(M=""+B),x.key!==void 0&&(M=""+x.key),x.ref!==void 0&&(D=x.ref);for(b in x)f.call(x,b)&&!S.hasOwnProperty(b)&&(C[b]=x[b]);if(z&&z.defaultProps)for(b in x=z.defaultProps,x)C[b]===void 0&&(C[b]=x[b]);return{$$typeof:u,type:z,key:M,ref:D,props:C,_owner:p.current}}return Rr.Fragment=c,Rr.jsx=w,Rr.jsxs=w,Rr}var uc;function Fm(){return uc||(uc=1,qa.exports=zm()),qa.exports}var r=Fm(),R=lo(),Hs={},Ja={exports:{}},Je={},Za={exports:{}},eo={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var cc;function Bm(){return cc||(cc=1,(function(o){function u(O,J){var V=O.length;O.push(J);e:for(;0<V;){var g=V-1>>>1,T=O[g];if(0<p(T,J))O[g]=J,O[V]=T,V=g;else break e}}function c(O){return O.length===0?null:O[0]}function f(O){if(O.length===0)return null;var J=O[0],V=O.pop();if(V!==J){O[0]=V;e:for(var g=0,T=O.length,ne=T>>>1;g<ne;){var ie=2*(g+1)-1,oe=O[ie],le=ie+1,pe=O[le];if(0>p(oe,V))le<T&&0>p(pe,oe)?(O[g]=pe,O[le]=V,g=le):(O[g]=oe,O[ie]=V,g=ie);else if(le<T&&0>p(pe,V))O[g]=pe,O[le]=V,g=le;else break e}}return J}function p(O,J){var V=O.sortIndex-J.sortIndex;return V!==0?V:O.id-J.id}if(typeof performance=="object"&&typeof performance.now=="function"){var S=performance;o.unstable_now=function(){return S.now()}}else{var w=Date,z=w.now();o.unstable_now=function(){return w.now()-z}}var x=[],B=[],b=1,C=null,M=3,D=!1,I=!1,F=!1,j=typeof setTimeout=="function"?setTimeout:null,W=typeof clearTimeout=="function"?clearTimeout:null,N=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function Q(O){for(var J=c(B);J!==null;){if(J.callback===null)f(B);else if(J.startTime<=O)f(B),J.sortIndex=J.expirationTime,u(x,J);else break;J=c(B)}}function te(O){if(F=!1,Q(O),!I)if(c(x)!==null)I=!0,Ge(se);else{var J=c(B);J!==null&&Se(te,J.startTime-O)}}function se(O,J){I=!1,F&&(F=!1,W(me),me=-1),D=!0;var V=M;try{for(Q(J),C=c(x);C!==null&&(!(C.expirationTime>J)||O&&!We());){var g=C.callback;if(typeof g=="function"){C.callback=null,M=C.priorityLevel;var T=g(C.expirationTime<=J);J=o.unstable_now(),typeof T=="function"?C.callback=T:C===c(x)&&f(x),Q(J)}else f(x);C=c(x)}if(C!==null)var ne=!0;else{var ie=c(B);ie!==null&&Se(te,ie.startTime-J),ne=!1}return ne}finally{C=null,M=V,D=!1}}var _=!1,X=null,me=-1,je=5,rt=-1;function We(){return!(o.unstable_now()-rt<je)}function ze(){if(X!==null){var O=o.unstable_now();rt=O;var J=!0;try{J=X(!0,O)}finally{J?$e():(_=!1,X=null)}}else _=!1}var $e;if(typeof N=="function")$e=function(){N(ze)};else if(typeof MessageChannel<"u"){var st=new MessageChannel,Nt=st.port2;st.port1.onmessage=ze,$e=function(){Nt.postMessage(null)}}else $e=function(){j(ze,0)};function Ge(O){X=O,_||(_=!0,$e())}function Se(O,J){me=j(function(){O(o.unstable_now())},J)}o.unstable_IdlePriority=5,o.unstable_ImmediatePriority=1,o.unstable_LowPriority=4,o.unstable_NormalPriority=3,o.unstable_Profiling=null,o.unstable_UserBlockingPriority=2,o.unstable_cancelCallback=function(O){O.callback=null},o.unstable_continueExecution=function(){I||D||(I=!0,Ge(se))},o.unstable_forceFrameRate=function(O){0>O||125<O?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):je=0<O?Math.floor(1e3/O):5},o.unstable_getCurrentPriorityLevel=function(){return M},o.unstable_getFirstCallbackNode=function(){return c(x)},o.unstable_next=function(O){switch(M){case 1:case 2:case 3:var J=3;break;default:J=M}var V=M;M=J;try{return O()}finally{M=V}},o.unstable_pauseExecution=function(){},o.unstable_requestPaint=function(){},o.unstable_runWithPriority=function(O,J){switch(O){case 1:case 2:case 3:case 4:case 5:break;default:O=3}var V=M;M=O;try{return J()}finally{M=V}},o.unstable_scheduleCallback=function(O,J,V){var g=o.unstable_now();switch(typeof V=="object"&&V!==null?(V=V.delay,V=typeof V=="number"&&0<V?g+V:g):V=g,O){case 1:var T=-1;break;case 2:T=250;break;case 5:T=1073741823;break;case 4:T=1e4;break;default:T=5e3}return T=V+T,O={id:b++,callback:J,priorityLevel:O,startTime:V,expirationTime:T,sortIndex:-1},V>g?(O.sortIndex=V,u(B,O),c(x)===null&&O===c(B)&&(F?(W(me),me=-1):F=!0,Se(te,V-g))):(O.sortIndex=T,u(x,O),I||D||(I=!0,Ge(se))),O},o.unstable_shouldYield=We,o.unstable_wrapCallback=function(O){var J=M;return function(){var V=M;M=J;try{return O.apply(this,arguments)}finally{M=V}}}})(eo)),eo}var dc;function Om(){return dc||(dc=1,Za.exports=Bm()),Za.exports}/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var mc;function Um(){if(mc)return Je;mc=1;var o=lo(),u=Om();function c(e){for(var t="https://reactjs.org/docs/error-decoder.html?invariant="+e,n=1;n<arguments.length;n++)t+="&args[]="+encodeURIComponent(arguments[n]);return"Minified React error #"+e+"; visit "+t+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var f=new Set,p={};function S(e,t){w(e,t),w(e+"Capture",t)}function w(e,t){for(p[e]=t,e=0;e<t.length;e++)f.add(t[e])}var z=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),x=Object.prototype.hasOwnProperty,B=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,b={},C={};function M(e){return x.call(C,e)?!0:x.call(b,e)?!1:B.test(e)?C[e]=!0:(b[e]=!0,!1)}function D(e,t,n,s){if(n!==null&&n.type===0)return!1;switch(typeof t){case"function":case"symbol":return!0;case"boolean":return s?!1:n!==null?!n.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function I(e,t,n,s){if(t===null||typeof t>"u"||D(e,t,n,s))return!0;if(s)return!1;if(n!==null)switch(n.type){case 3:return!t;case 4:return t===!1;case 5:return isNaN(t);case 6:return isNaN(t)||1>t}return!1}function F(e,t,n,s,i,a,l){this.acceptsBooleans=t===2||t===3||t===4,this.attributeName=s,this.attributeNamespace=i,this.mustUseProperty=n,this.propertyName=e,this.type=t,this.sanitizeURL=a,this.removeEmptyString=l}var j={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){j[e]=new F(e,0,!1,e,null,!1,!1)}),[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var t=e[0];j[t]=new F(t,1,!1,e[1],null,!1,!1)}),["contentEditable","draggable","spellCheck","value"].forEach(function(e){j[e]=new F(e,2,!1,e.toLowerCase(),null,!1,!1)}),["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){j[e]=new F(e,2,!1,e,null,!1,!1)}),"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){j[e]=new F(e,3,!1,e.toLowerCase(),null,!1,!1)}),["checked","multiple","muted","selected"].forEach(function(e){j[e]=new F(e,3,!0,e,null,!1,!1)}),["capture","download"].forEach(function(e){j[e]=new F(e,4,!1,e,null,!1,!1)}),["cols","rows","size","span"].forEach(function(e){j[e]=new F(e,6,!1,e,null,!1,!1)}),["rowSpan","start"].forEach(function(e){j[e]=new F(e,5,!1,e.toLowerCase(),null,!1,!1)});var W=/[\-:]([a-z])/g;function N(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var t=e.replace(W,N);j[t]=new F(t,1,!1,e,null,!1,!1)}),"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var t=e.replace(W,N);j[t]=new F(t,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)}),["xml:base","xml:lang","xml:space"].forEach(function(e){var t=e.replace(W,N);j[t]=new F(t,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)}),["tabIndex","crossOrigin"].forEach(function(e){j[e]=new F(e,1,!1,e.toLowerCase(),null,!1,!1)}),j.xlinkHref=new F("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1),["src","href","action","formAction"].forEach(function(e){j[e]=new F(e,1,!1,e.toLowerCase(),null,!0,!0)});function Q(e,t,n,s){var i=j.hasOwnProperty(t)?j[t]:null;(i!==null?i.type!==0:s||!(2<t.length)||t[0]!=="o"&&t[0]!=="O"||t[1]!=="n"&&t[1]!=="N")&&(I(t,n,i,s)&&(n=null),s||i===null?M(t)&&(n===null?e.removeAttribute(t):e.setAttribute(t,""+n)):i.mustUseProperty?e[i.propertyName]=n===null?i.type===3?!1:"":n:(t=i.attributeName,s=i.attributeNamespace,n===null?e.removeAttribute(t):(i=i.type,n=i===3||i===4&&n===!0?"":""+n,s?e.setAttributeNS(s,t,n):e.setAttribute(t,n))))}var te=o.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,se=Symbol.for("react.element"),_=Symbol.for("react.portal"),X=Symbol.for("react.fragment"),me=Symbol.for("react.strict_mode"),je=Symbol.for("react.profiler"),rt=Symbol.for("react.provider"),We=Symbol.for("react.context"),ze=Symbol.for("react.forward_ref"),$e=Symbol.for("react.suspense"),st=Symbol.for("react.suspense_list"),Nt=Symbol.for("react.memo"),Ge=Symbol.for("react.lazy"),Se=Symbol.for("react.offscreen"),O=Symbol.iterator;function J(e){return e===null||typeof e!="object"?null:(e=O&&e[O]||e["@@iterator"],typeof e=="function"?e:null)}var V=Object.assign,g;function T(e){if(g===void 0)try{throw Error()}catch(n){var t=n.stack.trim().match(/\n( *(at )?)/);g=t&&t[1]||""}return`
`+g+e}var ne=!1;function ie(e,t){if(!e||ne)return"";ne=!0;var n=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(t)if(t=function(){throw Error()},Object.defineProperty(t.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(t,[])}catch(k){var s=k}Reflect.construct(e,[],t)}else{try{t.call()}catch(k){s=k}e.call(t.prototype)}else{try{throw Error()}catch(k){s=k}e()}}catch(k){if(k&&s&&typeof k.stack=="string"){for(var i=k.stack.split(`
`),a=s.stack.split(`
`),l=i.length-1,d=a.length-1;1<=l&&0<=d&&i[l]!==a[d];)d--;for(;1<=l&&0<=d;l--,d--)if(i[l]!==a[d]){if(l!==1||d!==1)do if(l--,d--,0>d||i[l]!==a[d]){var m=`
`+i[l].replace(" at new "," at ");return e.displayName&&m.includes("<anonymous>")&&(m=m.replace("<anonymous>",e.displayName)),m}while(1<=l&&0<=d);break}}}finally{ne=!1,Error.prepareStackTrace=n}return(e=e?e.displayName||e.name:"")?T(e):""}function oe(e){switch(e.tag){case 5:return T(e.type);case 16:return T("Lazy");case 13:return T("Suspense");case 19:return T("SuspenseList");case 0:case 2:case 15:return e=ie(e.type,!1),e;case 11:return e=ie(e.type.render,!1),e;case 1:return e=ie(e.type,!0),e;default:return""}}function le(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case X:return"Fragment";case _:return"Portal";case je:return"Profiler";case me:return"StrictMode";case $e:return"Suspense";case st:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case We:return(e.displayName||"Context")+".Consumer";case rt:return(e._context.displayName||"Context")+".Provider";case ze:var t=e.render;return e=e.displayName,e||(e=t.displayName||t.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case Nt:return t=e.displayName||null,t!==null?t:le(e.type)||"Memo";case Ge:t=e._payload,e=e._init;try{return le(e(t))}catch{}}return null}function pe(e){var t=e.type;switch(e.tag){case 24:return"Cache";case 9:return(t.displayName||"Context")+".Consumer";case 10:return(t._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=t.render,e=e.displayName||e.name||"",t.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return t;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return le(t);case 8:return t===me?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof t=="function")return t.displayName||t.name||null;if(typeof t=="string")return t}return null}function ce(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function ye(e){var t=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(t==="checkbox"||t==="radio")}function it(e){var t=ye(e)?"checked":"value",n=Object.getOwnPropertyDescriptor(e.constructor.prototype,t),s=""+e[t];if(!e.hasOwnProperty(t)&&typeof n<"u"&&typeof n.get=="function"&&typeof n.set=="function"){var i=n.get,a=n.set;return Object.defineProperty(e,t,{configurable:!0,get:function(){return i.call(this)},set:function(l){s=""+l,a.call(this,l)}}),Object.defineProperty(e,t,{enumerable:n.enumerable}),{getValue:function(){return s},setValue:function(l){s=""+l},stopTracking:function(){e._valueTracker=null,delete e[t]}}}}function Dr(e){e._valueTracker||(e._valueTracker=it(e))}function co(e){if(!e)return!1;var t=e._valueTracker;if(!t)return!0;var n=t.getValue(),s="";return e&&(s=ye(e)?e.checked?"true":"false":e.value),e=s,e!==n?(t.setValue(e),!0):!1}function Ir(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function ri(e,t){var n=t.checked;return V({},t,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:n??e._wrapperState.initialChecked})}function mo(e,t){var n=t.defaultValue==null?"":t.defaultValue,s=t.checked!=null?t.checked:t.defaultChecked;n=ce(t.value!=null?t.value:n),e._wrapperState={initialChecked:s,initialValue:n,controlled:t.type==="checkbox"||t.type==="radio"?t.checked!=null:t.value!=null}}function ho(e,t){t=t.checked,t!=null&&Q(e,"checked",t,!1)}function si(e,t){ho(e,t);var n=ce(t.value),s=t.type;if(n!=null)s==="number"?(n===0&&e.value===""||e.value!=n)&&(e.value=""+n):e.value!==""+n&&(e.value=""+n);else if(s==="submit"||s==="reset"){e.removeAttribute("value");return}t.hasOwnProperty("value")?ii(e,t.type,n):t.hasOwnProperty("defaultValue")&&ii(e,t.type,ce(t.defaultValue)),t.checked==null&&t.defaultChecked!=null&&(e.defaultChecked=!!t.defaultChecked)}function po(e,t,n){if(t.hasOwnProperty("value")||t.hasOwnProperty("defaultValue")){var s=t.type;if(!(s!=="submit"&&s!=="reset"||t.value!==void 0&&t.value!==null))return;t=""+e._wrapperState.initialValue,n||t===e.value||(e.value=t),e.defaultValue=t}n=e.name,n!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,n!==""&&(e.name=n)}function ii(e,t,n){(t!=="number"||Ir(e.ownerDocument)!==e)&&(n==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+n&&(e.defaultValue=""+n))}var Qn=Array.isArray;function jn(e,t,n,s){if(e=e.options,t){t={};for(var i=0;i<n.length;i++)t["$"+n[i]]=!0;for(n=0;n<e.length;n++)i=t.hasOwnProperty("$"+e[n].value),e[n].selected!==i&&(e[n].selected=i),i&&s&&(e[n].defaultSelected=!0)}else{for(n=""+ce(n),t=null,i=0;i<e.length;i++){if(e[i].value===n){e[i].selected=!0,s&&(e[i].defaultSelected=!0);return}t!==null||e[i].disabled||(t=e[i])}t!==null&&(t.selected=!0)}}function ai(e,t){if(t.dangerouslySetInnerHTML!=null)throw Error(c(91));return V({},t,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function fo(e,t){var n=t.value;if(n==null){if(n=t.children,t=t.defaultValue,n!=null){if(t!=null)throw Error(c(92));if(Qn(n)){if(1<n.length)throw Error(c(93));n=n[0]}t=n}t==null&&(t=""),n=t}e._wrapperState={initialValue:ce(n)}}function go(e,t){var n=ce(t.value),s=ce(t.defaultValue);n!=null&&(n=""+n,n!==e.value&&(e.value=n),t.defaultValue==null&&e.defaultValue!==n&&(e.defaultValue=n)),s!=null&&(e.defaultValue=""+s)}function vo(e){var t=e.textContent;t===e._wrapperState.initialValue&&t!==""&&t!==null&&(e.value=t)}function yo(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function oi(e,t){return e==null||e==="http://www.w3.org/1999/xhtml"?yo(t):e==="http://www.w3.org/2000/svg"&&t==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var zr,xo=(function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(t,n,s,i){MSApp.execUnsafeLocalFunction(function(){return e(t,n,s,i)})}:e})(function(e,t){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=t;else{for(zr=zr||document.createElement("div"),zr.innerHTML="<svg>"+t.valueOf().toString()+"</svg>",t=zr.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;t.firstChild;)e.appendChild(t.firstChild)}});function Xn(e,t){if(t){var n=e.firstChild;if(n&&n===e.lastChild&&n.nodeType===3){n.nodeValue=t;return}}e.textContent=t}var qn={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},Fc=["Webkit","ms","Moz","O"];Object.keys(qn).forEach(function(e){Fc.forEach(function(t){t=t+e.charAt(0).toUpperCase()+e.substring(1),qn[t]=qn[e]})});function ko(e,t,n){return t==null||typeof t=="boolean"||t===""?"":n||typeof t!="number"||t===0||qn.hasOwnProperty(e)&&qn[e]?(""+t).trim():t+"px"}function wo(e,t){e=e.style;for(var n in t)if(t.hasOwnProperty(n)){var s=n.indexOf("--")===0,i=ko(n,t[n],s);n==="float"&&(n="cssFloat"),s?e.setProperty(n,i):e[n]=i}}var Bc=V({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function li(e,t){if(t){if(Bc[e]&&(t.children!=null||t.dangerouslySetInnerHTML!=null))throw Error(c(137,e));if(t.dangerouslySetInnerHTML!=null){if(t.children!=null)throw Error(c(60));if(typeof t.dangerouslySetInnerHTML!="object"||!("__html"in t.dangerouslySetInnerHTML))throw Error(c(61))}if(t.style!=null&&typeof t.style!="object")throw Error(c(62))}}function ui(e,t){if(e.indexOf("-")===-1)return typeof t.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var ci=null;function di(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var mi=null,Sn=null,Nn=null;function jo(e){if(e=yr(e)){if(typeof mi!="function")throw Error(c(280));var t=e.stateNode;t&&(t=as(t),mi(e.stateNode,e.type,t))}}function So(e){Sn?Nn?Nn.push(e):Nn=[e]:Sn=e}function No(){if(Sn){var e=Sn,t=Nn;if(Nn=Sn=null,jo(e),t)for(e=0;e<t.length;e++)jo(t[e])}}function bo(e,t){return e(t)}function Co(){}var hi=!1;function _o(e,t,n){if(hi)return e(t,n);hi=!0;try{return bo(e,t,n)}finally{hi=!1,(Sn!==null||Nn!==null)&&(Co(),No())}}function Yn(e,t){var n=e.stateNode;if(n===null)return null;var s=as(n);if(s===null)return null;n=s[t];e:switch(t){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(s=!s.disabled)||(e=e.type,s=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!s;break e;default:e=!1}if(e)return null;if(n&&typeof n!="function")throw Error(c(231,t,typeof n));return n}var pi=!1;if(z)try{var Jn={};Object.defineProperty(Jn,"passive",{get:function(){pi=!0}}),window.addEventListener("test",Jn,Jn),window.removeEventListener("test",Jn,Jn)}catch{pi=!1}function Oc(e,t,n,s,i,a,l,d,m){var k=Array.prototype.slice.call(arguments,3);try{t.apply(n,k)}catch(P){this.onError(P)}}var Zn=!1,Fr=null,Br=!1,fi=null,Uc={onError:function(e){Zn=!0,Fr=e}};function Wc(e,t,n,s,i,a,l,d,m){Zn=!1,Fr=null,Oc.apply(Uc,arguments)}function $c(e,t,n,s,i,a,l,d,m){if(Wc.apply(this,arguments),Zn){if(Zn){var k=Fr;Zn=!1,Fr=null}else throw Error(c(198));Br||(Br=!0,fi=k)}}function on(e){var t=e,n=e;if(e.alternate)for(;t.return;)t=t.return;else{e=t;do t=e,(t.flags&4098)!==0&&(n=t.return),e=t.return;while(e)}return t.tag===3?n:null}function Eo(e){if(e.tag===13){var t=e.memoizedState;if(t===null&&(e=e.alternate,e!==null&&(t=e.memoizedState)),t!==null)return t.dehydrated}return null}function To(e){if(on(e)!==e)throw Error(c(188))}function Vc(e){var t=e.alternate;if(!t){if(t=on(e),t===null)throw Error(c(188));return t!==e?null:e}for(var n=e,s=t;;){var i=n.return;if(i===null)break;var a=i.alternate;if(a===null){if(s=i.return,s!==null){n=s;continue}break}if(i.child===a.child){for(a=i.child;a;){if(a===n)return To(i),e;if(a===s)return To(i),t;a=a.sibling}throw Error(c(188))}if(n.return!==s.return)n=i,s=a;else{for(var l=!1,d=i.child;d;){if(d===n){l=!0,n=i,s=a;break}if(d===s){l=!0,s=i,n=a;break}d=d.sibling}if(!l){for(d=a.child;d;){if(d===n){l=!0,n=a,s=i;break}if(d===s){l=!0,s=a,n=i;break}d=d.sibling}if(!l)throw Error(c(189))}}if(n.alternate!==s)throw Error(c(190))}if(n.tag!==3)throw Error(c(188));return n.stateNode.current===n?e:t}function Po(e){return e=Vc(e),e!==null?Mo(e):null}function Mo(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var t=Mo(e);if(t!==null)return t;e=e.sibling}return null}var Lo=u.unstable_scheduleCallback,Ro=u.unstable_cancelCallback,Hc=u.unstable_shouldYield,Gc=u.unstable_requestPaint,be=u.unstable_now,Kc=u.unstable_getCurrentPriorityLevel,gi=u.unstable_ImmediatePriority,Ao=u.unstable_UserBlockingPriority,Or=u.unstable_NormalPriority,Qc=u.unstable_LowPriority,Do=u.unstable_IdlePriority,Ur=null,bt=null;function Xc(e){if(bt&&typeof bt.onCommitFiberRoot=="function")try{bt.onCommitFiberRoot(Ur,e,void 0,(e.current.flags&128)===128)}catch{}}var gt=Math.clz32?Math.clz32:Jc,qc=Math.log,Yc=Math.LN2;function Jc(e){return e>>>=0,e===0?32:31-(qc(e)/Yc|0)|0}var Wr=64,$r=4194304;function er(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function Vr(e,t){var n=e.pendingLanes;if(n===0)return 0;var s=0,i=e.suspendedLanes,a=e.pingedLanes,l=n&268435455;if(l!==0){var d=l&~i;d!==0?s=er(d):(a&=l,a!==0&&(s=er(a)))}else l=n&~i,l!==0?s=er(l):a!==0&&(s=er(a));if(s===0)return 0;if(t!==0&&t!==s&&(t&i)===0&&(i=s&-s,a=t&-t,i>=a||i===16&&(a&4194240)!==0))return t;if((s&4)!==0&&(s|=n&16),t=e.entangledLanes,t!==0)for(e=e.entanglements,t&=s;0<t;)n=31-gt(t),i=1<<n,s|=e[n],t&=~i;return s}function Zc(e,t){switch(e){case 1:case 2:case 4:return t+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return t+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function ed(e,t){for(var n=e.suspendedLanes,s=e.pingedLanes,i=e.expirationTimes,a=e.pendingLanes;0<a;){var l=31-gt(a),d=1<<l,m=i[l];m===-1?((d&n)===0||(d&s)!==0)&&(i[l]=Zc(d,t)):m<=t&&(e.expiredLanes|=d),a&=~d}}function vi(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function Io(){var e=Wr;return Wr<<=1,(Wr&4194240)===0&&(Wr=64),e}function yi(e){for(var t=[],n=0;31>n;n++)t.push(e);return t}function tr(e,t,n){e.pendingLanes|=t,t!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,t=31-gt(t),e[t]=n}function td(e,t){var n=e.pendingLanes&~t;e.pendingLanes=t,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=t,e.mutableReadLanes&=t,e.entangledLanes&=t,t=e.entanglements;var s=e.eventTimes;for(e=e.expirationTimes;0<n;){var i=31-gt(n),a=1<<i;t[i]=0,s[i]=-1,e[i]=-1,n&=~a}}function xi(e,t){var n=e.entangledLanes|=t;for(e=e.entanglements;n;){var s=31-gt(n),i=1<<s;i&t|e[s]&t&&(e[s]|=t),n&=~i}}var de=0;function zo(e){return e&=-e,1<e?4<e?(e&268435455)!==0?16:536870912:4:1}var Fo,ki,Bo,Oo,Uo,wi=!1,Hr=[],Bt=null,Ot=null,Ut=null,nr=new Map,rr=new Map,Wt=[],nd="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function Wo(e,t){switch(e){case"focusin":case"focusout":Bt=null;break;case"dragenter":case"dragleave":Ot=null;break;case"mouseover":case"mouseout":Ut=null;break;case"pointerover":case"pointerout":nr.delete(t.pointerId);break;case"gotpointercapture":case"lostpointercapture":rr.delete(t.pointerId)}}function sr(e,t,n,s,i,a){return e===null||e.nativeEvent!==a?(e={blockedOn:t,domEventName:n,eventSystemFlags:s,nativeEvent:a,targetContainers:[i]},t!==null&&(t=yr(t),t!==null&&ki(t)),e):(e.eventSystemFlags|=s,t=e.targetContainers,i!==null&&t.indexOf(i)===-1&&t.push(i),e)}function rd(e,t,n,s,i){switch(t){case"focusin":return Bt=sr(Bt,e,t,n,s,i),!0;case"dragenter":return Ot=sr(Ot,e,t,n,s,i),!0;case"mouseover":return Ut=sr(Ut,e,t,n,s,i),!0;case"pointerover":var a=i.pointerId;return nr.set(a,sr(nr.get(a)||null,e,t,n,s,i)),!0;case"gotpointercapture":return a=i.pointerId,rr.set(a,sr(rr.get(a)||null,e,t,n,s,i)),!0}return!1}function $o(e){var t=ln(e.target);if(t!==null){var n=on(t);if(n!==null){if(t=n.tag,t===13){if(t=Eo(n),t!==null){e.blockedOn=t,Uo(e.priority,function(){Bo(n)});return}}else if(t===3&&n.stateNode.current.memoizedState.isDehydrated){e.blockedOn=n.tag===3?n.stateNode.containerInfo:null;return}}}e.blockedOn=null}function Gr(e){if(e.blockedOn!==null)return!1;for(var t=e.targetContainers;0<t.length;){var n=Si(e.domEventName,e.eventSystemFlags,t[0],e.nativeEvent);if(n===null){n=e.nativeEvent;var s=new n.constructor(n.type,n);ci=s,n.target.dispatchEvent(s),ci=null}else return t=yr(n),t!==null&&ki(t),e.blockedOn=n,!1;t.shift()}return!0}function Vo(e,t,n){Gr(e)&&n.delete(t)}function sd(){wi=!1,Bt!==null&&Gr(Bt)&&(Bt=null),Ot!==null&&Gr(Ot)&&(Ot=null),Ut!==null&&Gr(Ut)&&(Ut=null),nr.forEach(Vo),rr.forEach(Vo)}function ir(e,t){e.blockedOn===t&&(e.blockedOn=null,wi||(wi=!0,u.unstable_scheduleCallback(u.unstable_NormalPriority,sd)))}function ar(e){function t(i){return ir(i,e)}if(0<Hr.length){ir(Hr[0],e);for(var n=1;n<Hr.length;n++){var s=Hr[n];s.blockedOn===e&&(s.blockedOn=null)}}for(Bt!==null&&ir(Bt,e),Ot!==null&&ir(Ot,e),Ut!==null&&ir(Ut,e),nr.forEach(t),rr.forEach(t),n=0;n<Wt.length;n++)s=Wt[n],s.blockedOn===e&&(s.blockedOn=null);for(;0<Wt.length&&(n=Wt[0],n.blockedOn===null);)$o(n),n.blockedOn===null&&Wt.shift()}var bn=te.ReactCurrentBatchConfig,Kr=!0;function id(e,t,n,s){var i=de,a=bn.transition;bn.transition=null;try{de=1,ji(e,t,n,s)}finally{de=i,bn.transition=a}}function ad(e,t,n,s){var i=de,a=bn.transition;bn.transition=null;try{de=4,ji(e,t,n,s)}finally{de=i,bn.transition=a}}function ji(e,t,n,s){if(Kr){var i=Si(e,t,n,s);if(i===null)Oi(e,t,s,Qr,n),Wo(e,s);else if(rd(i,e,t,n,s))s.stopPropagation();else if(Wo(e,s),t&4&&-1<nd.indexOf(e)){for(;i!==null;){var a=yr(i);if(a!==null&&Fo(a),a=Si(e,t,n,s),a===null&&Oi(e,t,s,Qr,n),a===i)break;i=a}i!==null&&s.stopPropagation()}else Oi(e,t,s,null,n)}}var Qr=null;function Si(e,t,n,s){if(Qr=null,e=di(s),e=ln(e),e!==null)if(t=on(e),t===null)e=null;else if(n=t.tag,n===13){if(e=Eo(t),e!==null)return e;e=null}else if(n===3){if(t.stateNode.current.memoizedState.isDehydrated)return t.tag===3?t.stateNode.containerInfo:null;e=null}else t!==e&&(e=null);return Qr=e,null}function Ho(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(Kc()){case gi:return 1;case Ao:return 4;case Or:case Qc:return 16;case Do:return 536870912;default:return 16}default:return 16}}var $t=null,Ni=null,Xr=null;function Go(){if(Xr)return Xr;var e,t=Ni,n=t.length,s,i="value"in $t?$t.value:$t.textContent,a=i.length;for(e=0;e<n&&t[e]===i[e];e++);var l=n-e;for(s=1;s<=l&&t[n-s]===i[a-s];s++);return Xr=i.slice(e,1<s?1-s:void 0)}function qr(e){var t=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&t===13&&(e=13)):e=t,e===10&&(e=13),32<=e||e===13?e:0}function Yr(){return!0}function Ko(){return!1}function at(e){function t(n,s,i,a,l){this._reactName=n,this._targetInst=i,this.type=s,this.nativeEvent=a,this.target=l,this.currentTarget=null;for(var d in e)e.hasOwnProperty(d)&&(n=e[d],this[d]=n?n(a):a[d]);return this.isDefaultPrevented=(a.defaultPrevented!=null?a.defaultPrevented:a.returnValue===!1)?Yr:Ko,this.isPropagationStopped=Ko,this}return V(t.prototype,{preventDefault:function(){this.defaultPrevented=!0;var n=this.nativeEvent;n&&(n.preventDefault?n.preventDefault():typeof n.returnValue!="unknown"&&(n.returnValue=!1),this.isDefaultPrevented=Yr)},stopPropagation:function(){var n=this.nativeEvent;n&&(n.stopPropagation?n.stopPropagation():typeof n.cancelBubble!="unknown"&&(n.cancelBubble=!0),this.isPropagationStopped=Yr)},persist:function(){},isPersistent:Yr}),t}var Cn={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},bi=at(Cn),or=V({},Cn,{view:0,detail:0}),od=at(or),Ci,_i,lr,Jr=V({},or,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:Ti,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==lr&&(lr&&e.type==="mousemove"?(Ci=e.screenX-lr.screenX,_i=e.screenY-lr.screenY):_i=Ci=0,lr=e),Ci)},movementY:function(e){return"movementY"in e?e.movementY:_i}}),Qo=at(Jr),ld=V({},Jr,{dataTransfer:0}),ud=at(ld),cd=V({},or,{relatedTarget:0}),Ei=at(cd),dd=V({},Cn,{animationName:0,elapsedTime:0,pseudoElement:0}),md=at(dd),hd=V({},Cn,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),pd=at(hd),fd=V({},Cn,{data:0}),Xo=at(fd),gd={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},vd={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},yd={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function xd(e){var t=this.nativeEvent;return t.getModifierState?t.getModifierState(e):(e=yd[e])?!!t[e]:!1}function Ti(){return xd}var kd=V({},or,{key:function(e){if(e.key){var t=gd[e.key]||e.key;if(t!=="Unidentified")return t}return e.type==="keypress"?(e=qr(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?vd[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:Ti,charCode:function(e){return e.type==="keypress"?qr(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?qr(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),wd=at(kd),jd=V({},Jr,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),qo=at(jd),Sd=V({},or,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:Ti}),Nd=at(Sd),bd=V({},Cn,{propertyName:0,elapsedTime:0,pseudoElement:0}),Cd=at(bd),_d=V({},Jr,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),Ed=at(_d),Td=[9,13,27,32],Pi=z&&"CompositionEvent"in window,ur=null;z&&"documentMode"in document&&(ur=document.documentMode);var Pd=z&&"TextEvent"in window&&!ur,Yo=z&&(!Pi||ur&&8<ur&&11>=ur),Jo=" ",Zo=!1;function el(e,t){switch(e){case"keyup":return Td.indexOf(t.keyCode)!==-1;case"keydown":return t.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function tl(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var _n=!1;function Md(e,t){switch(e){case"compositionend":return tl(t);case"keypress":return t.which!==32?null:(Zo=!0,Jo);case"textInput":return e=t.data,e===Jo&&Zo?null:e;default:return null}}function Ld(e,t){if(_n)return e==="compositionend"||!Pi&&el(e,t)?(e=Go(),Xr=Ni=$t=null,_n=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(t.ctrlKey||t.altKey||t.metaKey)||t.ctrlKey&&t.altKey){if(t.char&&1<t.char.length)return t.char;if(t.which)return String.fromCharCode(t.which)}return null;case"compositionend":return Yo&&t.locale!=="ko"?null:t.data;default:return null}}var Rd={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function nl(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t==="input"?!!Rd[e.type]:t==="textarea"}function rl(e,t,n,s){So(s),t=rs(t,"onChange"),0<t.length&&(n=new bi("onChange","change",null,n,s),e.push({event:n,listeners:t}))}var cr=null,dr=null;function Ad(e){wl(e,0)}function Zr(e){var t=Ln(e);if(co(t))return e}function Dd(e,t){if(e==="change")return t}var sl=!1;if(z){var Mi;if(z){var Li="oninput"in document;if(!Li){var il=document.createElement("div");il.setAttribute("oninput","return;"),Li=typeof il.oninput=="function"}Mi=Li}else Mi=!1;sl=Mi&&(!document.documentMode||9<document.documentMode)}function al(){cr&&(cr.detachEvent("onpropertychange",ol),dr=cr=null)}function ol(e){if(e.propertyName==="value"&&Zr(dr)){var t=[];rl(t,dr,e,di(e)),_o(Ad,t)}}function Id(e,t,n){e==="focusin"?(al(),cr=t,dr=n,cr.attachEvent("onpropertychange",ol)):e==="focusout"&&al()}function zd(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return Zr(dr)}function Fd(e,t){if(e==="click")return Zr(t)}function Bd(e,t){if(e==="input"||e==="change")return Zr(t)}function Od(e,t){return e===t&&(e!==0||1/e===1/t)||e!==e&&t!==t}var vt=typeof Object.is=="function"?Object.is:Od;function mr(e,t){if(vt(e,t))return!0;if(typeof e!="object"||e===null||typeof t!="object"||t===null)return!1;var n=Object.keys(e),s=Object.keys(t);if(n.length!==s.length)return!1;for(s=0;s<n.length;s++){var i=n[s];if(!x.call(t,i)||!vt(e[i],t[i]))return!1}return!0}function ll(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function ul(e,t){var n=ll(e);e=0;for(var s;n;){if(n.nodeType===3){if(s=e+n.textContent.length,e<=t&&s>=t)return{node:n,offset:t-e};e=s}e:{for(;n;){if(n.nextSibling){n=n.nextSibling;break e}n=n.parentNode}n=void 0}n=ll(n)}}function cl(e,t){return e&&t?e===t?!0:e&&e.nodeType===3?!1:t&&t.nodeType===3?cl(e,t.parentNode):"contains"in e?e.contains(t):e.compareDocumentPosition?!!(e.compareDocumentPosition(t)&16):!1:!1}function dl(){for(var e=window,t=Ir();t instanceof e.HTMLIFrameElement;){try{var n=typeof t.contentWindow.location.href=="string"}catch{n=!1}if(n)e=t.contentWindow;else break;t=Ir(e.document)}return t}function Ri(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t&&(t==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||t==="textarea"||e.contentEditable==="true")}function Ud(e){var t=dl(),n=e.focusedElem,s=e.selectionRange;if(t!==n&&n&&n.ownerDocument&&cl(n.ownerDocument.documentElement,n)){if(s!==null&&Ri(n)){if(t=s.start,e=s.end,e===void 0&&(e=t),"selectionStart"in n)n.selectionStart=t,n.selectionEnd=Math.min(e,n.value.length);else if(e=(t=n.ownerDocument||document)&&t.defaultView||window,e.getSelection){e=e.getSelection();var i=n.textContent.length,a=Math.min(s.start,i);s=s.end===void 0?a:Math.min(s.end,i),!e.extend&&a>s&&(i=s,s=a,a=i),i=ul(n,a);var l=ul(n,s);i&&l&&(e.rangeCount!==1||e.anchorNode!==i.node||e.anchorOffset!==i.offset||e.focusNode!==l.node||e.focusOffset!==l.offset)&&(t=t.createRange(),t.setStart(i.node,i.offset),e.removeAllRanges(),a>s?(e.addRange(t),e.extend(l.node,l.offset)):(t.setEnd(l.node,l.offset),e.addRange(t)))}}for(t=[],e=n;e=e.parentNode;)e.nodeType===1&&t.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof n.focus=="function"&&n.focus(),n=0;n<t.length;n++)e=t[n],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var Wd=z&&"documentMode"in document&&11>=document.documentMode,En=null,Ai=null,hr=null,Di=!1;function ml(e,t,n){var s=n.window===n?n.document:n.nodeType===9?n:n.ownerDocument;Di||En==null||En!==Ir(s)||(s=En,"selectionStart"in s&&Ri(s)?s={start:s.selectionStart,end:s.selectionEnd}:(s=(s.ownerDocument&&s.ownerDocument.defaultView||window).getSelection(),s={anchorNode:s.anchorNode,anchorOffset:s.anchorOffset,focusNode:s.focusNode,focusOffset:s.focusOffset}),hr&&mr(hr,s)||(hr=s,s=rs(Ai,"onSelect"),0<s.length&&(t=new bi("onSelect","select",null,t,n),e.push({event:t,listeners:s}),t.target=En)))}function es(e,t){var n={};return n[e.toLowerCase()]=t.toLowerCase(),n["Webkit"+e]="webkit"+t,n["Moz"+e]="moz"+t,n}var Tn={animationend:es("Animation","AnimationEnd"),animationiteration:es("Animation","AnimationIteration"),animationstart:es("Animation","AnimationStart"),transitionend:es("Transition","TransitionEnd")},Ii={},hl={};z&&(hl=document.createElement("div").style,"AnimationEvent"in window||(delete Tn.animationend.animation,delete Tn.animationiteration.animation,delete Tn.animationstart.animation),"TransitionEvent"in window||delete Tn.transitionend.transition);function ts(e){if(Ii[e])return Ii[e];if(!Tn[e])return e;var t=Tn[e],n;for(n in t)if(t.hasOwnProperty(n)&&n in hl)return Ii[e]=t[n];return e}var pl=ts("animationend"),fl=ts("animationiteration"),gl=ts("animationstart"),vl=ts("transitionend"),yl=new Map,xl="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function Vt(e,t){yl.set(e,t),S(t,[e])}for(var zi=0;zi<xl.length;zi++){var Fi=xl[zi],$d=Fi.toLowerCase(),Vd=Fi[0].toUpperCase()+Fi.slice(1);Vt($d,"on"+Vd)}Vt(pl,"onAnimationEnd"),Vt(fl,"onAnimationIteration"),Vt(gl,"onAnimationStart"),Vt("dblclick","onDoubleClick"),Vt("focusin","onFocus"),Vt("focusout","onBlur"),Vt(vl,"onTransitionEnd"),w("onMouseEnter",["mouseout","mouseover"]),w("onMouseLeave",["mouseout","mouseover"]),w("onPointerEnter",["pointerout","pointerover"]),w("onPointerLeave",["pointerout","pointerover"]),S("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),S("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),S("onBeforeInput",["compositionend","keypress","textInput","paste"]),S("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),S("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),S("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var pr="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),Hd=new Set("cancel close invalid load scroll toggle".split(" ").concat(pr));function kl(e,t,n){var s=e.type||"unknown-event";e.currentTarget=n,$c(s,t,void 0,e),e.currentTarget=null}function wl(e,t){t=(t&4)!==0;for(var n=0;n<e.length;n++){var s=e[n],i=s.event;s=s.listeners;e:{var a=void 0;if(t)for(var l=s.length-1;0<=l;l--){var d=s[l],m=d.instance,k=d.currentTarget;if(d=d.listener,m!==a&&i.isPropagationStopped())break e;kl(i,d,k),a=m}else for(l=0;l<s.length;l++){if(d=s[l],m=d.instance,k=d.currentTarget,d=d.listener,m!==a&&i.isPropagationStopped())break e;kl(i,d,k),a=m}}}if(Br)throw e=fi,Br=!1,fi=null,e}function ge(e,t){var n=t[Gi];n===void 0&&(n=t[Gi]=new Set);var s=e+"__bubble";n.has(s)||(jl(t,e,2,!1),n.add(s))}function Bi(e,t,n){var s=0;t&&(s|=4),jl(n,e,s,t)}var ns="_reactListening"+Math.random().toString(36).slice(2);function fr(e){if(!e[ns]){e[ns]=!0,f.forEach(function(n){n!=="selectionchange"&&(Hd.has(n)||Bi(n,!1,e),Bi(n,!0,e))});var t=e.nodeType===9?e:e.ownerDocument;t===null||t[ns]||(t[ns]=!0,Bi("selectionchange",!1,t))}}function jl(e,t,n,s){switch(Ho(t)){case 1:var i=id;break;case 4:i=ad;break;default:i=ji}n=i.bind(null,t,n,e),i=void 0,!pi||t!=="touchstart"&&t!=="touchmove"&&t!=="wheel"||(i=!0),s?i!==void 0?e.addEventListener(t,n,{capture:!0,passive:i}):e.addEventListener(t,n,!0):i!==void 0?e.addEventListener(t,n,{passive:i}):e.addEventListener(t,n,!1)}function Oi(e,t,n,s,i){var a=s;if((t&1)===0&&(t&2)===0&&s!==null)e:for(;;){if(s===null)return;var l=s.tag;if(l===3||l===4){var d=s.stateNode.containerInfo;if(d===i||d.nodeType===8&&d.parentNode===i)break;if(l===4)for(l=s.return;l!==null;){var m=l.tag;if((m===3||m===4)&&(m=l.stateNode.containerInfo,m===i||m.nodeType===8&&m.parentNode===i))return;l=l.return}for(;d!==null;){if(l=ln(d),l===null)return;if(m=l.tag,m===5||m===6){s=a=l;continue e}d=d.parentNode}}s=s.return}_o(function(){var k=a,P=di(n),L=[];e:{var E=yl.get(e);if(E!==void 0){var U=bi,H=e;switch(e){case"keypress":if(qr(n)===0)break e;case"keydown":case"keyup":U=wd;break;case"focusin":H="focus",U=Ei;break;case"focusout":H="blur",U=Ei;break;case"beforeblur":case"afterblur":U=Ei;break;case"click":if(n.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":U=Qo;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":U=ud;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":U=Nd;break;case pl:case fl:case gl:U=md;break;case vl:U=Cd;break;case"scroll":U=od;break;case"wheel":U=Ed;break;case"copy":case"cut":case"paste":U=pd;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":U=qo}var G=(t&4)!==0,Ce=!G&&e==="scroll",v=G?E!==null?E+"Capture":null:E;G=[];for(var h=k,y;h!==null;){y=h;var A=y.stateNode;if(y.tag===5&&A!==null&&(y=A,v!==null&&(A=Yn(h,v),A!=null&&G.push(gr(h,A,y)))),Ce)break;h=h.return}0<G.length&&(E=new U(E,H,null,n,P),L.push({event:E,listeners:G}))}}if((t&7)===0){e:{if(E=e==="mouseover"||e==="pointerover",U=e==="mouseout"||e==="pointerout",E&&n!==ci&&(H=n.relatedTarget||n.fromElement)&&(ln(H)||H[Mt]))break e;if((U||E)&&(E=P.window===P?P:(E=P.ownerDocument)?E.defaultView||E.parentWindow:window,U?(H=n.relatedTarget||n.toElement,U=k,H=H?ln(H):null,H!==null&&(Ce=on(H),H!==Ce||H.tag!==5&&H.tag!==6)&&(H=null)):(U=null,H=k),U!==H)){if(G=Qo,A="onMouseLeave",v="onMouseEnter",h="mouse",(e==="pointerout"||e==="pointerover")&&(G=qo,A="onPointerLeave",v="onPointerEnter",h="pointer"),Ce=U==null?E:Ln(U),y=H==null?E:Ln(H),E=new G(A,h+"leave",U,n,P),E.target=Ce,E.relatedTarget=y,A=null,ln(P)===k&&(G=new G(v,h+"enter",H,n,P),G.target=y,G.relatedTarget=Ce,A=G),Ce=A,U&&H)t:{for(G=U,v=H,h=0,y=G;y;y=Pn(y))h++;for(y=0,A=v;A;A=Pn(A))y++;for(;0<h-y;)G=Pn(G),h--;for(;0<y-h;)v=Pn(v),y--;for(;h--;){if(G===v||v!==null&&G===v.alternate)break t;G=Pn(G),v=Pn(v)}G=null}else G=null;U!==null&&Sl(L,E,U,G,!1),H!==null&&Ce!==null&&Sl(L,Ce,H,G,!0)}}e:{if(E=k?Ln(k):window,U=E.nodeName&&E.nodeName.toLowerCase(),U==="select"||U==="input"&&E.type==="file")var K=Dd;else if(nl(E))if(sl)K=Bd;else{K=zd;var q=Id}else(U=E.nodeName)&&U.toLowerCase()==="input"&&(E.type==="checkbox"||E.type==="radio")&&(K=Fd);if(K&&(K=K(e,k))){rl(L,K,n,P);break e}q&&q(e,E,k),e==="focusout"&&(q=E._wrapperState)&&q.controlled&&E.type==="number"&&ii(E,"number",E.value)}switch(q=k?Ln(k):window,e){case"focusin":(nl(q)||q.contentEditable==="true")&&(En=q,Ai=k,hr=null);break;case"focusout":hr=Ai=En=null;break;case"mousedown":Di=!0;break;case"contextmenu":case"mouseup":case"dragend":Di=!1,ml(L,n,P);break;case"selectionchange":if(Wd)break;case"keydown":case"keyup":ml(L,n,P)}var Y;if(Pi)e:{switch(e){case"compositionstart":var ee="onCompositionStart";break e;case"compositionend":ee="onCompositionEnd";break e;case"compositionupdate":ee="onCompositionUpdate";break e}ee=void 0}else _n?el(e,n)&&(ee="onCompositionEnd"):e==="keydown"&&n.keyCode===229&&(ee="onCompositionStart");ee&&(Yo&&n.locale!=="ko"&&(_n||ee!=="onCompositionStart"?ee==="onCompositionEnd"&&_n&&(Y=Go()):($t=P,Ni="value"in $t?$t.value:$t.textContent,_n=!0)),q=rs(k,ee),0<q.length&&(ee=new Xo(ee,e,null,n,P),L.push({event:ee,listeners:q}),Y?ee.data=Y:(Y=tl(n),Y!==null&&(ee.data=Y)))),(Y=Pd?Md(e,n):Ld(e,n))&&(k=rs(k,"onBeforeInput"),0<k.length&&(P=new Xo("onBeforeInput","beforeinput",null,n,P),L.push({event:P,listeners:k}),P.data=Y))}wl(L,t)})}function gr(e,t,n){return{instance:e,listener:t,currentTarget:n}}function rs(e,t){for(var n=t+"Capture",s=[];e!==null;){var i=e,a=i.stateNode;i.tag===5&&a!==null&&(i=a,a=Yn(e,n),a!=null&&s.unshift(gr(e,a,i)),a=Yn(e,t),a!=null&&s.push(gr(e,a,i))),e=e.return}return s}function Pn(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function Sl(e,t,n,s,i){for(var a=t._reactName,l=[];n!==null&&n!==s;){var d=n,m=d.alternate,k=d.stateNode;if(m!==null&&m===s)break;d.tag===5&&k!==null&&(d=k,i?(m=Yn(n,a),m!=null&&l.unshift(gr(n,m,d))):i||(m=Yn(n,a),m!=null&&l.push(gr(n,m,d)))),n=n.return}l.length!==0&&e.push({event:t,listeners:l})}var Gd=/\r\n?/g,Kd=/\u0000|\uFFFD/g;function Nl(e){return(typeof e=="string"?e:""+e).replace(Gd,`
`).replace(Kd,"")}function ss(e,t,n){if(t=Nl(t),Nl(e)!==t&&n)throw Error(c(425))}function is(){}var Ui=null,Wi=null;function $i(e,t){return e==="textarea"||e==="noscript"||typeof t.children=="string"||typeof t.children=="number"||typeof t.dangerouslySetInnerHTML=="object"&&t.dangerouslySetInnerHTML!==null&&t.dangerouslySetInnerHTML.__html!=null}var Vi=typeof setTimeout=="function"?setTimeout:void 0,Qd=typeof clearTimeout=="function"?clearTimeout:void 0,bl=typeof Promise=="function"?Promise:void 0,Xd=typeof queueMicrotask=="function"?queueMicrotask:typeof bl<"u"?function(e){return bl.resolve(null).then(e).catch(qd)}:Vi;function qd(e){setTimeout(function(){throw e})}function Hi(e,t){var n=t,s=0;do{var i=n.nextSibling;if(e.removeChild(n),i&&i.nodeType===8)if(n=i.data,n==="/$"){if(s===0){e.removeChild(i),ar(t);return}s--}else n!=="$"&&n!=="$?"&&n!=="$!"||s++;n=i}while(n);ar(t)}function Ht(e){for(;e!=null;e=e.nextSibling){var t=e.nodeType;if(t===1||t===3)break;if(t===8){if(t=e.data,t==="$"||t==="$!"||t==="$?")break;if(t==="/$")return null}}return e}function Cl(e){e=e.previousSibling;for(var t=0;e;){if(e.nodeType===8){var n=e.data;if(n==="$"||n==="$!"||n==="$?"){if(t===0)return e;t--}else n==="/$"&&t++}e=e.previousSibling}return null}var Mn=Math.random().toString(36).slice(2),Ct="__reactFiber$"+Mn,vr="__reactProps$"+Mn,Mt="__reactContainer$"+Mn,Gi="__reactEvents$"+Mn,Yd="__reactListeners$"+Mn,Jd="__reactHandles$"+Mn;function ln(e){var t=e[Ct];if(t)return t;for(var n=e.parentNode;n;){if(t=n[Mt]||n[Ct]){if(n=t.alternate,t.child!==null||n!==null&&n.child!==null)for(e=Cl(e);e!==null;){if(n=e[Ct])return n;e=Cl(e)}return t}e=n,n=e.parentNode}return null}function yr(e){return e=e[Ct]||e[Mt],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function Ln(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(c(33))}function as(e){return e[vr]||null}var Ki=[],Rn=-1;function Gt(e){return{current:e}}function ve(e){0>Rn||(e.current=Ki[Rn],Ki[Rn]=null,Rn--)}function fe(e,t){Rn++,Ki[Rn]=e.current,e.current=t}var Kt={},Fe=Gt(Kt),Ke=Gt(!1),un=Kt;function An(e,t){var n=e.type.contextTypes;if(!n)return Kt;var s=e.stateNode;if(s&&s.__reactInternalMemoizedUnmaskedChildContext===t)return s.__reactInternalMemoizedMaskedChildContext;var i={},a;for(a in n)i[a]=t[a];return s&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=t,e.__reactInternalMemoizedMaskedChildContext=i),i}function Qe(e){return e=e.childContextTypes,e!=null}function os(){ve(Ke),ve(Fe)}function _l(e,t,n){if(Fe.current!==Kt)throw Error(c(168));fe(Fe,t),fe(Ke,n)}function El(e,t,n){var s=e.stateNode;if(t=t.childContextTypes,typeof s.getChildContext!="function")return n;s=s.getChildContext();for(var i in s)if(!(i in t))throw Error(c(108,pe(e)||"Unknown",i));return V({},n,s)}function ls(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||Kt,un=Fe.current,fe(Fe,e),fe(Ke,Ke.current),!0}function Tl(e,t,n){var s=e.stateNode;if(!s)throw Error(c(169));n?(e=El(e,t,un),s.__reactInternalMemoizedMergedChildContext=e,ve(Ke),ve(Fe),fe(Fe,e)):ve(Ke),fe(Ke,n)}var Lt=null,us=!1,Qi=!1;function Pl(e){Lt===null?Lt=[e]:Lt.push(e)}function Zd(e){us=!0,Pl(e)}function Qt(){if(!Qi&&Lt!==null){Qi=!0;var e=0,t=de;try{var n=Lt;for(de=1;e<n.length;e++){var s=n[e];do s=s(!0);while(s!==null)}Lt=null,us=!1}catch(i){throw Lt!==null&&(Lt=Lt.slice(e+1)),Lo(gi,Qt),i}finally{de=t,Qi=!1}}return null}var Dn=[],In=0,cs=null,ds=0,ct=[],dt=0,cn=null,Rt=1,At="";function dn(e,t){Dn[In++]=ds,Dn[In++]=cs,cs=e,ds=t}function Ml(e,t,n){ct[dt++]=Rt,ct[dt++]=At,ct[dt++]=cn,cn=e;var s=Rt;e=At;var i=32-gt(s)-1;s&=~(1<<i),n+=1;var a=32-gt(t)+i;if(30<a){var l=i-i%5;a=(s&(1<<l)-1).toString(32),s>>=l,i-=l,Rt=1<<32-gt(t)+i|n<<i|s,At=a+e}else Rt=1<<a|n<<i|s,At=e}function Xi(e){e.return!==null&&(dn(e,1),Ml(e,1,0))}function qi(e){for(;e===cs;)cs=Dn[--In],Dn[In]=null,ds=Dn[--In],Dn[In]=null;for(;e===cn;)cn=ct[--dt],ct[dt]=null,At=ct[--dt],ct[dt]=null,Rt=ct[--dt],ct[dt]=null}var ot=null,lt=null,xe=!1,yt=null;function Ll(e,t){var n=ft(5,null,null,0);n.elementType="DELETED",n.stateNode=t,n.return=e,t=e.deletions,t===null?(e.deletions=[n],e.flags|=16):t.push(n)}function Rl(e,t){switch(e.tag){case 5:var n=e.type;return t=t.nodeType!==1||n.toLowerCase()!==t.nodeName.toLowerCase()?null:t,t!==null?(e.stateNode=t,ot=e,lt=Ht(t.firstChild),!0):!1;case 6:return t=e.pendingProps===""||t.nodeType!==3?null:t,t!==null?(e.stateNode=t,ot=e,lt=null,!0):!1;case 13:return t=t.nodeType!==8?null:t,t!==null?(n=cn!==null?{id:Rt,overflow:At}:null,e.memoizedState={dehydrated:t,treeContext:n,retryLane:1073741824},n=ft(18,null,null,0),n.stateNode=t,n.return=e,e.child=n,ot=e,lt=null,!0):!1;default:return!1}}function Yi(e){return(e.mode&1)!==0&&(e.flags&128)===0}function Ji(e){if(xe){var t=lt;if(t){var n=t;if(!Rl(e,t)){if(Yi(e))throw Error(c(418));t=Ht(n.nextSibling);var s=ot;t&&Rl(e,t)?Ll(s,n):(e.flags=e.flags&-4097|2,xe=!1,ot=e)}}else{if(Yi(e))throw Error(c(418));e.flags=e.flags&-4097|2,xe=!1,ot=e}}}function Al(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;ot=e}function ms(e){if(e!==ot)return!1;if(!xe)return Al(e),xe=!0,!1;var t;if((t=e.tag!==3)&&!(t=e.tag!==5)&&(t=e.type,t=t!=="head"&&t!=="body"&&!$i(e.type,e.memoizedProps)),t&&(t=lt)){if(Yi(e))throw Dl(),Error(c(418));for(;t;)Ll(e,t),t=Ht(t.nextSibling)}if(Al(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(c(317));e:{for(e=e.nextSibling,t=0;e;){if(e.nodeType===8){var n=e.data;if(n==="/$"){if(t===0){lt=Ht(e.nextSibling);break e}t--}else n!=="$"&&n!=="$!"&&n!=="$?"||t++}e=e.nextSibling}lt=null}}else lt=ot?Ht(e.stateNode.nextSibling):null;return!0}function Dl(){for(var e=lt;e;)e=Ht(e.nextSibling)}function zn(){lt=ot=null,xe=!1}function Zi(e){yt===null?yt=[e]:yt.push(e)}var em=te.ReactCurrentBatchConfig;function xr(e,t,n){if(e=n.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(n._owner){if(n=n._owner,n){if(n.tag!==1)throw Error(c(309));var s=n.stateNode}if(!s)throw Error(c(147,e));var i=s,a=""+e;return t!==null&&t.ref!==null&&typeof t.ref=="function"&&t.ref._stringRef===a?t.ref:(t=function(l){var d=i.refs;l===null?delete d[a]:d[a]=l},t._stringRef=a,t)}if(typeof e!="string")throw Error(c(284));if(!n._owner)throw Error(c(290,e))}return e}function hs(e,t){throw e=Object.prototype.toString.call(t),Error(c(31,e==="[object Object]"?"object with keys {"+Object.keys(t).join(", ")+"}":e))}function Il(e){var t=e._init;return t(e._payload)}function zl(e){function t(v,h){if(e){var y=v.deletions;y===null?(v.deletions=[h],v.flags|=16):y.push(h)}}function n(v,h){if(!e)return null;for(;h!==null;)t(v,h),h=h.sibling;return null}function s(v,h){for(v=new Map;h!==null;)h.key!==null?v.set(h.key,h):v.set(h.index,h),h=h.sibling;return v}function i(v,h){return v=nn(v,h),v.index=0,v.sibling=null,v}function a(v,h,y){return v.index=y,e?(y=v.alternate,y!==null?(y=y.index,y<h?(v.flags|=2,h):y):(v.flags|=2,h)):(v.flags|=1048576,h)}function l(v){return e&&v.alternate===null&&(v.flags|=2),v}function d(v,h,y,A){return h===null||h.tag!==6?(h=Va(y,v.mode,A),h.return=v,h):(h=i(h,y),h.return=v,h)}function m(v,h,y,A){var K=y.type;return K===X?P(v,h,y.props.children,A,y.key):h!==null&&(h.elementType===K||typeof K=="object"&&K!==null&&K.$$typeof===Ge&&Il(K)===h.type)?(A=i(h,y.props),A.ref=xr(v,h,y),A.return=v,A):(A=zs(y.type,y.key,y.props,null,v.mode,A),A.ref=xr(v,h,y),A.return=v,A)}function k(v,h,y,A){return h===null||h.tag!==4||h.stateNode.containerInfo!==y.containerInfo||h.stateNode.implementation!==y.implementation?(h=Ha(y,v.mode,A),h.return=v,h):(h=i(h,y.children||[]),h.return=v,h)}function P(v,h,y,A,K){return h===null||h.tag!==7?(h=xn(y,v.mode,A,K),h.return=v,h):(h=i(h,y),h.return=v,h)}function L(v,h,y){if(typeof h=="string"&&h!==""||typeof h=="number")return h=Va(""+h,v.mode,y),h.return=v,h;if(typeof h=="object"&&h!==null){switch(h.$$typeof){case se:return y=zs(h.type,h.key,h.props,null,v.mode,y),y.ref=xr(v,null,h),y.return=v,y;case _:return h=Ha(h,v.mode,y),h.return=v,h;case Ge:var A=h._init;return L(v,A(h._payload),y)}if(Qn(h)||J(h))return h=xn(h,v.mode,y,null),h.return=v,h;hs(v,h)}return null}function E(v,h,y,A){var K=h!==null?h.key:null;if(typeof y=="string"&&y!==""||typeof y=="number")return K!==null?null:d(v,h,""+y,A);if(typeof y=="object"&&y!==null){switch(y.$$typeof){case se:return y.key===K?m(v,h,y,A):null;case _:return y.key===K?k(v,h,y,A):null;case Ge:return K=y._init,E(v,h,K(y._payload),A)}if(Qn(y)||J(y))return K!==null?null:P(v,h,y,A,null);hs(v,y)}return null}function U(v,h,y,A,K){if(typeof A=="string"&&A!==""||typeof A=="number")return v=v.get(y)||null,d(h,v,""+A,K);if(typeof A=="object"&&A!==null){switch(A.$$typeof){case se:return v=v.get(A.key===null?y:A.key)||null,m(h,v,A,K);case _:return v=v.get(A.key===null?y:A.key)||null,k(h,v,A,K);case Ge:var q=A._init;return U(v,h,y,q(A._payload),K)}if(Qn(A)||J(A))return v=v.get(y)||null,P(h,v,A,K,null);hs(h,A)}return null}function H(v,h,y,A){for(var K=null,q=null,Y=h,ee=h=0,Ae=null;Y!==null&&ee<y.length;ee++){Y.index>ee?(Ae=Y,Y=null):Ae=Y.sibling;var ue=E(v,Y,y[ee],A);if(ue===null){Y===null&&(Y=Ae);break}e&&Y&&ue.alternate===null&&t(v,Y),h=a(ue,h,ee),q===null?K=ue:q.sibling=ue,q=ue,Y=Ae}if(ee===y.length)return n(v,Y),xe&&dn(v,ee),K;if(Y===null){for(;ee<y.length;ee++)Y=L(v,y[ee],A),Y!==null&&(h=a(Y,h,ee),q===null?K=Y:q.sibling=Y,q=Y);return xe&&dn(v,ee),K}for(Y=s(v,Y);ee<y.length;ee++)Ae=U(Y,v,ee,y[ee],A),Ae!==null&&(e&&Ae.alternate!==null&&Y.delete(Ae.key===null?ee:Ae.key),h=a(Ae,h,ee),q===null?K=Ae:q.sibling=Ae,q=Ae);return e&&Y.forEach(function(rn){return t(v,rn)}),xe&&dn(v,ee),K}function G(v,h,y,A){var K=J(y);if(typeof K!="function")throw Error(c(150));if(y=K.call(y),y==null)throw Error(c(151));for(var q=K=null,Y=h,ee=h=0,Ae=null,ue=y.next();Y!==null&&!ue.done;ee++,ue=y.next()){Y.index>ee?(Ae=Y,Y=null):Ae=Y.sibling;var rn=E(v,Y,ue.value,A);if(rn===null){Y===null&&(Y=Ae);break}e&&Y&&rn.alternate===null&&t(v,Y),h=a(rn,h,ee),q===null?K=rn:q.sibling=rn,q=rn,Y=Ae}if(ue.done)return n(v,Y),xe&&dn(v,ee),K;if(Y===null){for(;!ue.done;ee++,ue=y.next())ue=L(v,ue.value,A),ue!==null&&(h=a(ue,h,ee),q===null?K=ue:q.sibling=ue,q=ue);return xe&&dn(v,ee),K}for(Y=s(v,Y);!ue.done;ee++,ue=y.next())ue=U(Y,v,ee,ue.value,A),ue!==null&&(e&&ue.alternate!==null&&Y.delete(ue.key===null?ee:ue.key),h=a(ue,h,ee),q===null?K=ue:q.sibling=ue,q=ue);return e&&Y.forEach(function(Rm){return t(v,Rm)}),xe&&dn(v,ee),K}function Ce(v,h,y,A){if(typeof y=="object"&&y!==null&&y.type===X&&y.key===null&&(y=y.props.children),typeof y=="object"&&y!==null){switch(y.$$typeof){case se:e:{for(var K=y.key,q=h;q!==null;){if(q.key===K){if(K=y.type,K===X){if(q.tag===7){n(v,q.sibling),h=i(q,y.props.children),h.return=v,v=h;break e}}else if(q.elementType===K||typeof K=="object"&&K!==null&&K.$$typeof===Ge&&Il(K)===q.type){n(v,q.sibling),h=i(q,y.props),h.ref=xr(v,q,y),h.return=v,v=h;break e}n(v,q);break}else t(v,q);q=q.sibling}y.type===X?(h=xn(y.props.children,v.mode,A,y.key),h.return=v,v=h):(A=zs(y.type,y.key,y.props,null,v.mode,A),A.ref=xr(v,h,y),A.return=v,v=A)}return l(v);case _:e:{for(q=y.key;h!==null;){if(h.key===q)if(h.tag===4&&h.stateNode.containerInfo===y.containerInfo&&h.stateNode.implementation===y.implementation){n(v,h.sibling),h=i(h,y.children||[]),h.return=v,v=h;break e}else{n(v,h);break}else t(v,h);h=h.sibling}h=Ha(y,v.mode,A),h.return=v,v=h}return l(v);case Ge:return q=y._init,Ce(v,h,q(y._payload),A)}if(Qn(y))return H(v,h,y,A);if(J(y))return G(v,h,y,A);hs(v,y)}return typeof y=="string"&&y!==""||typeof y=="number"?(y=""+y,h!==null&&h.tag===6?(n(v,h.sibling),h=i(h,y),h.return=v,v=h):(n(v,h),h=Va(y,v.mode,A),h.return=v,v=h),l(v)):n(v,h)}return Ce}var Fn=zl(!0),Fl=zl(!1),ps=Gt(null),fs=null,Bn=null,ea=null;function ta(){ea=Bn=fs=null}function na(e){var t=ps.current;ve(ps),e._currentValue=t}function ra(e,t,n){for(;e!==null;){var s=e.alternate;if((e.childLanes&t)!==t?(e.childLanes|=t,s!==null&&(s.childLanes|=t)):s!==null&&(s.childLanes&t)!==t&&(s.childLanes|=t),e===n)break;e=e.return}}function On(e,t){fs=e,ea=Bn=null,e=e.dependencies,e!==null&&e.firstContext!==null&&((e.lanes&t)!==0&&(Xe=!0),e.firstContext=null)}function mt(e){var t=e._currentValue;if(ea!==e)if(e={context:e,memoizedValue:t,next:null},Bn===null){if(fs===null)throw Error(c(308));Bn=e,fs.dependencies={lanes:0,firstContext:e}}else Bn=Bn.next=e;return t}var mn=null;function sa(e){mn===null?mn=[e]:mn.push(e)}function Bl(e,t,n,s){var i=t.interleaved;return i===null?(n.next=n,sa(t)):(n.next=i.next,i.next=n),t.interleaved=n,Dt(e,s)}function Dt(e,t){e.lanes|=t;var n=e.alternate;for(n!==null&&(n.lanes|=t),n=e,e=e.return;e!==null;)e.childLanes|=t,n=e.alternate,n!==null&&(n.childLanes|=t),n=e,e=e.return;return n.tag===3?n.stateNode:null}var Xt=!1;function ia(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function Ol(e,t){e=e.updateQueue,t.updateQueue===e&&(t.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function It(e,t){return{eventTime:e,lane:t,tag:0,payload:null,callback:null,next:null}}function qt(e,t,n){var s=e.updateQueue;if(s===null)return null;if(s=s.shared,(ae&2)!==0){var i=s.pending;return i===null?t.next=t:(t.next=i.next,i.next=t),s.pending=t,Dt(e,n)}return i=s.interleaved,i===null?(t.next=t,sa(s)):(t.next=i.next,i.next=t),s.interleaved=t,Dt(e,n)}function gs(e,t,n){if(t=t.updateQueue,t!==null&&(t=t.shared,(n&4194240)!==0)){var s=t.lanes;s&=e.pendingLanes,n|=s,t.lanes=n,xi(e,n)}}function Ul(e,t){var n=e.updateQueue,s=e.alternate;if(s!==null&&(s=s.updateQueue,n===s)){var i=null,a=null;if(n=n.firstBaseUpdate,n!==null){do{var l={eventTime:n.eventTime,lane:n.lane,tag:n.tag,payload:n.payload,callback:n.callback,next:null};a===null?i=a=l:a=a.next=l,n=n.next}while(n!==null);a===null?i=a=t:a=a.next=t}else i=a=t;n={baseState:s.baseState,firstBaseUpdate:i,lastBaseUpdate:a,shared:s.shared,effects:s.effects},e.updateQueue=n;return}e=n.lastBaseUpdate,e===null?n.firstBaseUpdate=t:e.next=t,n.lastBaseUpdate=t}function vs(e,t,n,s){var i=e.updateQueue;Xt=!1;var a=i.firstBaseUpdate,l=i.lastBaseUpdate,d=i.shared.pending;if(d!==null){i.shared.pending=null;var m=d,k=m.next;m.next=null,l===null?a=k:l.next=k,l=m;var P=e.alternate;P!==null&&(P=P.updateQueue,d=P.lastBaseUpdate,d!==l&&(d===null?P.firstBaseUpdate=k:d.next=k,P.lastBaseUpdate=m))}if(a!==null){var L=i.baseState;l=0,P=k=m=null,d=a;do{var E=d.lane,U=d.eventTime;if((s&E)===E){P!==null&&(P=P.next={eventTime:U,lane:0,tag:d.tag,payload:d.payload,callback:d.callback,next:null});e:{var H=e,G=d;switch(E=t,U=n,G.tag){case 1:if(H=G.payload,typeof H=="function"){L=H.call(U,L,E);break e}L=H;break e;case 3:H.flags=H.flags&-65537|128;case 0:if(H=G.payload,E=typeof H=="function"?H.call(U,L,E):H,E==null)break e;L=V({},L,E);break e;case 2:Xt=!0}}d.callback!==null&&d.lane!==0&&(e.flags|=64,E=i.effects,E===null?i.effects=[d]:E.push(d))}else U={eventTime:U,lane:E,tag:d.tag,payload:d.payload,callback:d.callback,next:null},P===null?(k=P=U,m=L):P=P.next=U,l|=E;if(d=d.next,d===null){if(d=i.shared.pending,d===null)break;E=d,d=E.next,E.next=null,i.lastBaseUpdate=E,i.shared.pending=null}}while(!0);if(P===null&&(m=L),i.baseState=m,i.firstBaseUpdate=k,i.lastBaseUpdate=P,t=i.shared.interleaved,t!==null){i=t;do l|=i.lane,i=i.next;while(i!==t)}else a===null&&(i.shared.lanes=0);fn|=l,e.lanes=l,e.memoizedState=L}}function Wl(e,t,n){if(e=t.effects,t.effects=null,e!==null)for(t=0;t<e.length;t++){var s=e[t],i=s.callback;if(i!==null){if(s.callback=null,s=n,typeof i!="function")throw Error(c(191,i));i.call(s)}}}var kr={},_t=Gt(kr),wr=Gt(kr),jr=Gt(kr);function hn(e){if(e===kr)throw Error(c(174));return e}function aa(e,t){switch(fe(jr,t),fe(wr,e),fe(_t,kr),e=t.nodeType,e){case 9:case 11:t=(t=t.documentElement)?t.namespaceURI:oi(null,"");break;default:e=e===8?t.parentNode:t,t=e.namespaceURI||null,e=e.tagName,t=oi(t,e)}ve(_t),fe(_t,t)}function Un(){ve(_t),ve(wr),ve(jr)}function $l(e){hn(jr.current);var t=hn(_t.current),n=oi(t,e.type);t!==n&&(fe(wr,e),fe(_t,n))}function oa(e){wr.current===e&&(ve(_t),ve(wr))}var ke=Gt(0);function ys(e){for(var t=e;t!==null;){if(t.tag===13){var n=t.memoizedState;if(n!==null&&(n=n.dehydrated,n===null||n.data==="$?"||n.data==="$!"))return t}else if(t.tag===19&&t.memoizedProps.revealOrder!==void 0){if((t.flags&128)!==0)return t}else if(t.child!==null){t.child.return=t,t=t.child;continue}if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return null;t=t.return}t.sibling.return=t.return,t=t.sibling}return null}var la=[];function ua(){for(var e=0;e<la.length;e++)la[e]._workInProgressVersionPrimary=null;la.length=0}var xs=te.ReactCurrentDispatcher,ca=te.ReactCurrentBatchConfig,pn=0,we=null,Te=null,Le=null,ks=!1,Sr=!1,Nr=0,tm=0;function Be(){throw Error(c(321))}function da(e,t){if(t===null)return!1;for(var n=0;n<t.length&&n<e.length;n++)if(!vt(e[n],t[n]))return!1;return!0}function ma(e,t,n,s,i,a){if(pn=a,we=t,t.memoizedState=null,t.updateQueue=null,t.lanes=0,xs.current=e===null||e.memoizedState===null?im:am,e=n(s,i),Sr){a=0;do{if(Sr=!1,Nr=0,25<=a)throw Error(c(301));a+=1,Le=Te=null,t.updateQueue=null,xs.current=om,e=n(s,i)}while(Sr)}if(xs.current=Ss,t=Te!==null&&Te.next!==null,pn=0,Le=Te=we=null,ks=!1,t)throw Error(c(300));return e}function ha(){var e=Nr!==0;return Nr=0,e}function Et(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return Le===null?we.memoizedState=Le=e:Le=Le.next=e,Le}function ht(){if(Te===null){var e=we.alternate;e=e!==null?e.memoizedState:null}else e=Te.next;var t=Le===null?we.memoizedState:Le.next;if(t!==null)Le=t,Te=e;else{if(e===null)throw Error(c(310));Te=e,e={memoizedState:Te.memoizedState,baseState:Te.baseState,baseQueue:Te.baseQueue,queue:Te.queue,next:null},Le===null?we.memoizedState=Le=e:Le=Le.next=e}return Le}function br(e,t){return typeof t=="function"?t(e):t}function pa(e){var t=ht(),n=t.queue;if(n===null)throw Error(c(311));n.lastRenderedReducer=e;var s=Te,i=s.baseQueue,a=n.pending;if(a!==null){if(i!==null){var l=i.next;i.next=a.next,a.next=l}s.baseQueue=i=a,n.pending=null}if(i!==null){a=i.next,s=s.baseState;var d=l=null,m=null,k=a;do{var P=k.lane;if((pn&P)===P)m!==null&&(m=m.next={lane:0,action:k.action,hasEagerState:k.hasEagerState,eagerState:k.eagerState,next:null}),s=k.hasEagerState?k.eagerState:e(s,k.action);else{var L={lane:P,action:k.action,hasEagerState:k.hasEagerState,eagerState:k.eagerState,next:null};m===null?(d=m=L,l=s):m=m.next=L,we.lanes|=P,fn|=P}k=k.next}while(k!==null&&k!==a);m===null?l=s:m.next=d,vt(s,t.memoizedState)||(Xe=!0),t.memoizedState=s,t.baseState=l,t.baseQueue=m,n.lastRenderedState=s}if(e=n.interleaved,e!==null){i=e;do a=i.lane,we.lanes|=a,fn|=a,i=i.next;while(i!==e)}else i===null&&(n.lanes=0);return[t.memoizedState,n.dispatch]}function fa(e){var t=ht(),n=t.queue;if(n===null)throw Error(c(311));n.lastRenderedReducer=e;var s=n.dispatch,i=n.pending,a=t.memoizedState;if(i!==null){n.pending=null;var l=i=i.next;do a=e(a,l.action),l=l.next;while(l!==i);vt(a,t.memoizedState)||(Xe=!0),t.memoizedState=a,t.baseQueue===null&&(t.baseState=a),n.lastRenderedState=a}return[a,s]}function Vl(){}function Hl(e,t){var n=we,s=ht(),i=t(),a=!vt(s.memoizedState,i);if(a&&(s.memoizedState=i,Xe=!0),s=s.queue,ga(Ql.bind(null,n,s,e),[e]),s.getSnapshot!==t||a||Le!==null&&Le.memoizedState.tag&1){if(n.flags|=2048,Cr(9,Kl.bind(null,n,s,i,t),void 0,null),Re===null)throw Error(c(349));(pn&30)!==0||Gl(n,t,i)}return i}function Gl(e,t,n){e.flags|=16384,e={getSnapshot:t,value:n},t=we.updateQueue,t===null?(t={lastEffect:null,stores:null},we.updateQueue=t,t.stores=[e]):(n=t.stores,n===null?t.stores=[e]:n.push(e))}function Kl(e,t,n,s){t.value=n,t.getSnapshot=s,Xl(t)&&ql(e)}function Ql(e,t,n){return n(function(){Xl(t)&&ql(e)})}function Xl(e){var t=e.getSnapshot;e=e.value;try{var n=t();return!vt(e,n)}catch{return!0}}function ql(e){var t=Dt(e,1);t!==null&&jt(t,e,1,-1)}function Yl(e){var t=Et();return typeof e=="function"&&(e=e()),t.memoizedState=t.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:br,lastRenderedState:e},t.queue=e,e=e.dispatch=sm.bind(null,we,e),[t.memoizedState,e]}function Cr(e,t,n,s){return e={tag:e,create:t,destroy:n,deps:s,next:null},t=we.updateQueue,t===null?(t={lastEffect:null,stores:null},we.updateQueue=t,t.lastEffect=e.next=e):(n=t.lastEffect,n===null?t.lastEffect=e.next=e:(s=n.next,n.next=e,e.next=s,t.lastEffect=e)),e}function Jl(){return ht().memoizedState}function ws(e,t,n,s){var i=Et();we.flags|=e,i.memoizedState=Cr(1|t,n,void 0,s===void 0?null:s)}function js(e,t,n,s){var i=ht();s=s===void 0?null:s;var a=void 0;if(Te!==null){var l=Te.memoizedState;if(a=l.destroy,s!==null&&da(s,l.deps)){i.memoizedState=Cr(t,n,a,s);return}}we.flags|=e,i.memoizedState=Cr(1|t,n,a,s)}function Zl(e,t){return ws(8390656,8,e,t)}function ga(e,t){return js(2048,8,e,t)}function eu(e,t){return js(4,2,e,t)}function tu(e,t){return js(4,4,e,t)}function nu(e,t){if(typeof t=="function")return e=e(),t(e),function(){t(null)};if(t!=null)return e=e(),t.current=e,function(){t.current=null}}function ru(e,t,n){return n=n!=null?n.concat([e]):null,js(4,4,nu.bind(null,t,e),n)}function va(){}function su(e,t){var n=ht();t=t===void 0?null:t;var s=n.memoizedState;return s!==null&&t!==null&&da(t,s[1])?s[0]:(n.memoizedState=[e,t],e)}function iu(e,t){var n=ht();t=t===void 0?null:t;var s=n.memoizedState;return s!==null&&t!==null&&da(t,s[1])?s[0]:(e=e(),n.memoizedState=[e,t],e)}function au(e,t,n){return(pn&21)===0?(e.baseState&&(e.baseState=!1,Xe=!0),e.memoizedState=n):(vt(n,t)||(n=Io(),we.lanes|=n,fn|=n,e.baseState=!0),t)}function nm(e,t){var n=de;de=n!==0&&4>n?n:4,e(!0);var s=ca.transition;ca.transition={};try{e(!1),t()}finally{de=n,ca.transition=s}}function ou(){return ht().memoizedState}function rm(e,t,n){var s=en(e);if(n={lane:s,action:n,hasEagerState:!1,eagerState:null,next:null},lu(e))uu(t,n);else if(n=Bl(e,t,n,s),n!==null){var i=He();jt(n,e,s,i),cu(n,t,s)}}function sm(e,t,n){var s=en(e),i={lane:s,action:n,hasEagerState:!1,eagerState:null,next:null};if(lu(e))uu(t,i);else{var a=e.alternate;if(e.lanes===0&&(a===null||a.lanes===0)&&(a=t.lastRenderedReducer,a!==null))try{var l=t.lastRenderedState,d=a(l,n);if(i.hasEagerState=!0,i.eagerState=d,vt(d,l)){var m=t.interleaved;m===null?(i.next=i,sa(t)):(i.next=m.next,m.next=i),t.interleaved=i;return}}catch{}finally{}n=Bl(e,t,i,s),n!==null&&(i=He(),jt(n,e,s,i),cu(n,t,s))}}function lu(e){var t=e.alternate;return e===we||t!==null&&t===we}function uu(e,t){Sr=ks=!0;var n=e.pending;n===null?t.next=t:(t.next=n.next,n.next=t),e.pending=t}function cu(e,t,n){if((n&4194240)!==0){var s=t.lanes;s&=e.pendingLanes,n|=s,t.lanes=n,xi(e,n)}}var Ss={readContext:mt,useCallback:Be,useContext:Be,useEffect:Be,useImperativeHandle:Be,useInsertionEffect:Be,useLayoutEffect:Be,useMemo:Be,useReducer:Be,useRef:Be,useState:Be,useDebugValue:Be,useDeferredValue:Be,useTransition:Be,useMutableSource:Be,useSyncExternalStore:Be,useId:Be,unstable_isNewReconciler:!1},im={readContext:mt,useCallback:function(e,t){return Et().memoizedState=[e,t===void 0?null:t],e},useContext:mt,useEffect:Zl,useImperativeHandle:function(e,t,n){return n=n!=null?n.concat([e]):null,ws(4194308,4,nu.bind(null,t,e),n)},useLayoutEffect:function(e,t){return ws(4194308,4,e,t)},useInsertionEffect:function(e,t){return ws(4,2,e,t)},useMemo:function(e,t){var n=Et();return t=t===void 0?null:t,e=e(),n.memoizedState=[e,t],e},useReducer:function(e,t,n){var s=Et();return t=n!==void 0?n(t):t,s.memoizedState=s.baseState=t,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:t},s.queue=e,e=e.dispatch=rm.bind(null,we,e),[s.memoizedState,e]},useRef:function(e){var t=Et();return e={current:e},t.memoizedState=e},useState:Yl,useDebugValue:va,useDeferredValue:function(e){return Et().memoizedState=e},useTransition:function(){var e=Yl(!1),t=e[0];return e=nm.bind(null,e[1]),Et().memoizedState=e,[t,e]},useMutableSource:function(){},useSyncExternalStore:function(e,t,n){var s=we,i=Et();if(xe){if(n===void 0)throw Error(c(407));n=n()}else{if(n=t(),Re===null)throw Error(c(349));(pn&30)!==0||Gl(s,t,n)}i.memoizedState=n;var a={value:n,getSnapshot:t};return i.queue=a,Zl(Ql.bind(null,s,a,e),[e]),s.flags|=2048,Cr(9,Kl.bind(null,s,a,n,t),void 0,null),n},useId:function(){var e=Et(),t=Re.identifierPrefix;if(xe){var n=At,s=Rt;n=(s&~(1<<32-gt(s)-1)).toString(32)+n,t=":"+t+"R"+n,n=Nr++,0<n&&(t+="H"+n.toString(32)),t+=":"}else n=tm++,t=":"+t+"r"+n.toString(32)+":";return e.memoizedState=t},unstable_isNewReconciler:!1},am={readContext:mt,useCallback:su,useContext:mt,useEffect:ga,useImperativeHandle:ru,useInsertionEffect:eu,useLayoutEffect:tu,useMemo:iu,useReducer:pa,useRef:Jl,useState:function(){return pa(br)},useDebugValue:va,useDeferredValue:function(e){var t=ht();return au(t,Te.memoizedState,e)},useTransition:function(){var e=pa(br)[0],t=ht().memoizedState;return[e,t]},useMutableSource:Vl,useSyncExternalStore:Hl,useId:ou,unstable_isNewReconciler:!1},om={readContext:mt,useCallback:su,useContext:mt,useEffect:ga,useImperativeHandle:ru,useInsertionEffect:eu,useLayoutEffect:tu,useMemo:iu,useReducer:fa,useRef:Jl,useState:function(){return fa(br)},useDebugValue:va,useDeferredValue:function(e){var t=ht();return Te===null?t.memoizedState=e:au(t,Te.memoizedState,e)},useTransition:function(){var e=fa(br)[0],t=ht().memoizedState;return[e,t]},useMutableSource:Vl,useSyncExternalStore:Hl,useId:ou,unstable_isNewReconciler:!1};function xt(e,t){if(e&&e.defaultProps){t=V({},t),e=e.defaultProps;for(var n in e)t[n]===void 0&&(t[n]=e[n]);return t}return t}function ya(e,t,n,s){t=e.memoizedState,n=n(s,t),n=n==null?t:V({},t,n),e.memoizedState=n,e.lanes===0&&(e.updateQueue.baseState=n)}var Ns={isMounted:function(e){return(e=e._reactInternals)?on(e)===e:!1},enqueueSetState:function(e,t,n){e=e._reactInternals;var s=He(),i=en(e),a=It(s,i);a.payload=t,n!=null&&(a.callback=n),t=qt(e,a,i),t!==null&&(jt(t,e,i,s),gs(t,e,i))},enqueueReplaceState:function(e,t,n){e=e._reactInternals;var s=He(),i=en(e),a=It(s,i);a.tag=1,a.payload=t,n!=null&&(a.callback=n),t=qt(e,a,i),t!==null&&(jt(t,e,i,s),gs(t,e,i))},enqueueForceUpdate:function(e,t){e=e._reactInternals;var n=He(),s=en(e),i=It(n,s);i.tag=2,t!=null&&(i.callback=t),t=qt(e,i,s),t!==null&&(jt(t,e,s,n),gs(t,e,s))}};function du(e,t,n,s,i,a,l){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(s,a,l):t.prototype&&t.prototype.isPureReactComponent?!mr(n,s)||!mr(i,a):!0}function mu(e,t,n){var s=!1,i=Kt,a=t.contextType;return typeof a=="object"&&a!==null?a=mt(a):(i=Qe(t)?un:Fe.current,s=t.contextTypes,a=(s=s!=null)?An(e,i):Kt),t=new t(n,a),e.memoizedState=t.state!==null&&t.state!==void 0?t.state:null,t.updater=Ns,e.stateNode=t,t._reactInternals=e,s&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=i,e.__reactInternalMemoizedMaskedChildContext=a),t}function hu(e,t,n,s){e=t.state,typeof t.componentWillReceiveProps=="function"&&t.componentWillReceiveProps(n,s),typeof t.UNSAFE_componentWillReceiveProps=="function"&&t.UNSAFE_componentWillReceiveProps(n,s),t.state!==e&&Ns.enqueueReplaceState(t,t.state,null)}function xa(e,t,n,s){var i=e.stateNode;i.props=n,i.state=e.memoizedState,i.refs={},ia(e);var a=t.contextType;typeof a=="object"&&a!==null?i.context=mt(a):(a=Qe(t)?un:Fe.current,i.context=An(e,a)),i.state=e.memoizedState,a=t.getDerivedStateFromProps,typeof a=="function"&&(ya(e,t,a,n),i.state=e.memoizedState),typeof t.getDerivedStateFromProps=="function"||typeof i.getSnapshotBeforeUpdate=="function"||typeof i.UNSAFE_componentWillMount!="function"&&typeof i.componentWillMount!="function"||(t=i.state,typeof i.componentWillMount=="function"&&i.componentWillMount(),typeof i.UNSAFE_componentWillMount=="function"&&i.UNSAFE_componentWillMount(),t!==i.state&&Ns.enqueueReplaceState(i,i.state,null),vs(e,n,i,s),i.state=e.memoizedState),typeof i.componentDidMount=="function"&&(e.flags|=4194308)}function Wn(e,t){try{var n="",s=t;do n+=oe(s),s=s.return;while(s);var i=n}catch(a){i=`
Error generating stack: `+a.message+`
`+a.stack}return{value:e,source:t,stack:i,digest:null}}function ka(e,t,n){return{value:e,source:null,stack:n??null,digest:t??null}}function wa(e,t){try{console.error(t.value)}catch(n){setTimeout(function(){throw n})}}var lm=typeof WeakMap=="function"?WeakMap:Map;function pu(e,t,n){n=It(-1,n),n.tag=3,n.payload={element:null};var s=t.value;return n.callback=function(){Ms||(Ms=!0,Ia=s),wa(e,t)},n}function fu(e,t,n){n=It(-1,n),n.tag=3;var s=e.type.getDerivedStateFromError;if(typeof s=="function"){var i=t.value;n.payload=function(){return s(i)},n.callback=function(){wa(e,t)}}var a=e.stateNode;return a!==null&&typeof a.componentDidCatch=="function"&&(n.callback=function(){wa(e,t),typeof s!="function"&&(Jt===null?Jt=new Set([this]):Jt.add(this));var l=t.stack;this.componentDidCatch(t.value,{componentStack:l!==null?l:""})}),n}function gu(e,t,n){var s=e.pingCache;if(s===null){s=e.pingCache=new lm;var i=new Set;s.set(t,i)}else i=s.get(t),i===void 0&&(i=new Set,s.set(t,i));i.has(n)||(i.add(n),e=jm.bind(null,e,t,n),t.then(e,e))}function vu(e){do{var t;if((t=e.tag===13)&&(t=e.memoizedState,t=t!==null?t.dehydrated!==null:!0),t)return e;e=e.return}while(e!==null);return null}function yu(e,t,n,s,i){return(e.mode&1)===0?(e===t?e.flags|=65536:(e.flags|=128,n.flags|=131072,n.flags&=-52805,n.tag===1&&(n.alternate===null?n.tag=17:(t=It(-1,1),t.tag=2,qt(n,t,1))),n.lanes|=1),e):(e.flags|=65536,e.lanes=i,e)}var um=te.ReactCurrentOwner,Xe=!1;function Ve(e,t,n,s){t.child=e===null?Fl(t,null,n,s):Fn(t,e.child,n,s)}function xu(e,t,n,s,i){n=n.render;var a=t.ref;return On(t,i),s=ma(e,t,n,s,a,i),n=ha(),e!==null&&!Xe?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~i,zt(e,t,i)):(xe&&n&&Xi(t),t.flags|=1,Ve(e,t,s,i),t.child)}function ku(e,t,n,s,i){if(e===null){var a=n.type;return typeof a=="function"&&!$a(a)&&a.defaultProps===void 0&&n.compare===null&&n.defaultProps===void 0?(t.tag=15,t.type=a,wu(e,t,a,s,i)):(e=zs(n.type,null,s,t,t.mode,i),e.ref=t.ref,e.return=t,t.child=e)}if(a=e.child,(e.lanes&i)===0){var l=a.memoizedProps;if(n=n.compare,n=n!==null?n:mr,n(l,s)&&e.ref===t.ref)return zt(e,t,i)}return t.flags|=1,e=nn(a,s),e.ref=t.ref,e.return=t,t.child=e}function wu(e,t,n,s,i){if(e!==null){var a=e.memoizedProps;if(mr(a,s)&&e.ref===t.ref)if(Xe=!1,t.pendingProps=s=a,(e.lanes&i)!==0)(e.flags&131072)!==0&&(Xe=!0);else return t.lanes=e.lanes,zt(e,t,i)}return ja(e,t,n,s,i)}function ju(e,t,n){var s=t.pendingProps,i=s.children,a=e!==null?e.memoizedState:null;if(s.mode==="hidden")if((t.mode&1)===0)t.memoizedState={baseLanes:0,cachePool:null,transitions:null},fe(Vn,ut),ut|=n;else{if((n&1073741824)===0)return e=a!==null?a.baseLanes|n:n,t.lanes=t.childLanes=1073741824,t.memoizedState={baseLanes:e,cachePool:null,transitions:null},t.updateQueue=null,fe(Vn,ut),ut|=e,null;t.memoizedState={baseLanes:0,cachePool:null,transitions:null},s=a!==null?a.baseLanes:n,fe(Vn,ut),ut|=s}else a!==null?(s=a.baseLanes|n,t.memoizedState=null):s=n,fe(Vn,ut),ut|=s;return Ve(e,t,i,n),t.child}function Su(e,t){var n=t.ref;(e===null&&n!==null||e!==null&&e.ref!==n)&&(t.flags|=512,t.flags|=2097152)}function ja(e,t,n,s,i){var a=Qe(n)?un:Fe.current;return a=An(t,a),On(t,i),n=ma(e,t,n,s,a,i),s=ha(),e!==null&&!Xe?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~i,zt(e,t,i)):(xe&&s&&Xi(t),t.flags|=1,Ve(e,t,n,i),t.child)}function Nu(e,t,n,s,i){if(Qe(n)){var a=!0;ls(t)}else a=!1;if(On(t,i),t.stateNode===null)Cs(e,t),mu(t,n,s),xa(t,n,s,i),s=!0;else if(e===null){var l=t.stateNode,d=t.memoizedProps;l.props=d;var m=l.context,k=n.contextType;typeof k=="object"&&k!==null?k=mt(k):(k=Qe(n)?un:Fe.current,k=An(t,k));var P=n.getDerivedStateFromProps,L=typeof P=="function"||typeof l.getSnapshotBeforeUpdate=="function";L||typeof l.UNSAFE_componentWillReceiveProps!="function"&&typeof l.componentWillReceiveProps!="function"||(d!==s||m!==k)&&hu(t,l,s,k),Xt=!1;var E=t.memoizedState;l.state=E,vs(t,s,l,i),m=t.memoizedState,d!==s||E!==m||Ke.current||Xt?(typeof P=="function"&&(ya(t,n,P,s),m=t.memoizedState),(d=Xt||du(t,n,d,s,E,m,k))?(L||typeof l.UNSAFE_componentWillMount!="function"&&typeof l.componentWillMount!="function"||(typeof l.componentWillMount=="function"&&l.componentWillMount(),typeof l.UNSAFE_componentWillMount=="function"&&l.UNSAFE_componentWillMount()),typeof l.componentDidMount=="function"&&(t.flags|=4194308)):(typeof l.componentDidMount=="function"&&(t.flags|=4194308),t.memoizedProps=s,t.memoizedState=m),l.props=s,l.state=m,l.context=k,s=d):(typeof l.componentDidMount=="function"&&(t.flags|=4194308),s=!1)}else{l=t.stateNode,Ol(e,t),d=t.memoizedProps,k=t.type===t.elementType?d:xt(t.type,d),l.props=k,L=t.pendingProps,E=l.context,m=n.contextType,typeof m=="object"&&m!==null?m=mt(m):(m=Qe(n)?un:Fe.current,m=An(t,m));var U=n.getDerivedStateFromProps;(P=typeof U=="function"||typeof l.getSnapshotBeforeUpdate=="function")||typeof l.UNSAFE_componentWillReceiveProps!="function"&&typeof l.componentWillReceiveProps!="function"||(d!==L||E!==m)&&hu(t,l,s,m),Xt=!1,E=t.memoizedState,l.state=E,vs(t,s,l,i);var H=t.memoizedState;d!==L||E!==H||Ke.current||Xt?(typeof U=="function"&&(ya(t,n,U,s),H=t.memoizedState),(k=Xt||du(t,n,k,s,E,H,m)||!1)?(P||typeof l.UNSAFE_componentWillUpdate!="function"&&typeof l.componentWillUpdate!="function"||(typeof l.componentWillUpdate=="function"&&l.componentWillUpdate(s,H,m),typeof l.UNSAFE_componentWillUpdate=="function"&&l.UNSAFE_componentWillUpdate(s,H,m)),typeof l.componentDidUpdate=="function"&&(t.flags|=4),typeof l.getSnapshotBeforeUpdate=="function"&&(t.flags|=1024)):(typeof l.componentDidUpdate!="function"||d===e.memoizedProps&&E===e.memoizedState||(t.flags|=4),typeof l.getSnapshotBeforeUpdate!="function"||d===e.memoizedProps&&E===e.memoizedState||(t.flags|=1024),t.memoizedProps=s,t.memoizedState=H),l.props=s,l.state=H,l.context=m,s=k):(typeof l.componentDidUpdate!="function"||d===e.memoizedProps&&E===e.memoizedState||(t.flags|=4),typeof l.getSnapshotBeforeUpdate!="function"||d===e.memoizedProps&&E===e.memoizedState||(t.flags|=1024),s=!1)}return Sa(e,t,n,s,a,i)}function Sa(e,t,n,s,i,a){Su(e,t);var l=(t.flags&128)!==0;if(!s&&!l)return i&&Tl(t,n,!1),zt(e,t,a);s=t.stateNode,um.current=t;var d=l&&typeof n.getDerivedStateFromError!="function"?null:s.render();return t.flags|=1,e!==null&&l?(t.child=Fn(t,e.child,null,a),t.child=Fn(t,null,d,a)):Ve(e,t,d,a),t.memoizedState=s.state,i&&Tl(t,n,!0),t.child}function bu(e){var t=e.stateNode;t.pendingContext?_l(e,t.pendingContext,t.pendingContext!==t.context):t.context&&_l(e,t.context,!1),aa(e,t.containerInfo)}function Cu(e,t,n,s,i){return zn(),Zi(i),t.flags|=256,Ve(e,t,n,s),t.child}var Na={dehydrated:null,treeContext:null,retryLane:0};function ba(e){return{baseLanes:e,cachePool:null,transitions:null}}function _u(e,t,n){var s=t.pendingProps,i=ke.current,a=!1,l=(t.flags&128)!==0,d;if((d=l)||(d=e!==null&&e.memoizedState===null?!1:(i&2)!==0),d?(a=!0,t.flags&=-129):(e===null||e.memoizedState!==null)&&(i|=1),fe(ke,i&1),e===null)return Ji(t),e=t.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?((t.mode&1)===0?t.lanes=1:e.data==="$!"?t.lanes=8:t.lanes=1073741824,null):(l=s.children,e=s.fallback,a?(s=t.mode,a=t.child,l={mode:"hidden",children:l},(s&1)===0&&a!==null?(a.childLanes=0,a.pendingProps=l):a=Fs(l,s,0,null),e=xn(e,s,n,null),a.return=t,e.return=t,a.sibling=e,t.child=a,t.child.memoizedState=ba(n),t.memoizedState=Na,e):Ca(t,l));if(i=e.memoizedState,i!==null&&(d=i.dehydrated,d!==null))return cm(e,t,l,s,d,i,n);if(a){a=s.fallback,l=t.mode,i=e.child,d=i.sibling;var m={mode:"hidden",children:s.children};return(l&1)===0&&t.child!==i?(s=t.child,s.childLanes=0,s.pendingProps=m,t.deletions=null):(s=nn(i,m),s.subtreeFlags=i.subtreeFlags&14680064),d!==null?a=nn(d,a):(a=xn(a,l,n,null),a.flags|=2),a.return=t,s.return=t,s.sibling=a,t.child=s,s=a,a=t.child,l=e.child.memoizedState,l=l===null?ba(n):{baseLanes:l.baseLanes|n,cachePool:null,transitions:l.transitions},a.memoizedState=l,a.childLanes=e.childLanes&~n,t.memoizedState=Na,s}return a=e.child,e=a.sibling,s=nn(a,{mode:"visible",children:s.children}),(t.mode&1)===0&&(s.lanes=n),s.return=t,s.sibling=null,e!==null&&(n=t.deletions,n===null?(t.deletions=[e],t.flags|=16):n.push(e)),t.child=s,t.memoizedState=null,s}function Ca(e,t){return t=Fs({mode:"visible",children:t},e.mode,0,null),t.return=e,e.child=t}function bs(e,t,n,s){return s!==null&&Zi(s),Fn(t,e.child,null,n),e=Ca(t,t.pendingProps.children),e.flags|=2,t.memoizedState=null,e}function cm(e,t,n,s,i,a,l){if(n)return t.flags&256?(t.flags&=-257,s=ka(Error(c(422))),bs(e,t,l,s)):t.memoizedState!==null?(t.child=e.child,t.flags|=128,null):(a=s.fallback,i=t.mode,s=Fs({mode:"visible",children:s.children},i,0,null),a=xn(a,i,l,null),a.flags|=2,s.return=t,a.return=t,s.sibling=a,t.child=s,(t.mode&1)!==0&&Fn(t,e.child,null,l),t.child.memoizedState=ba(l),t.memoizedState=Na,a);if((t.mode&1)===0)return bs(e,t,l,null);if(i.data==="$!"){if(s=i.nextSibling&&i.nextSibling.dataset,s)var d=s.dgst;return s=d,a=Error(c(419)),s=ka(a,s,void 0),bs(e,t,l,s)}if(d=(l&e.childLanes)!==0,Xe||d){if(s=Re,s!==null){switch(l&-l){case 4:i=2;break;case 16:i=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:i=32;break;case 536870912:i=268435456;break;default:i=0}i=(i&(s.suspendedLanes|l))!==0?0:i,i!==0&&i!==a.retryLane&&(a.retryLane=i,Dt(e,i),jt(s,e,i,-1))}return Wa(),s=ka(Error(c(421))),bs(e,t,l,s)}return i.data==="$?"?(t.flags|=128,t.child=e.child,t=Sm.bind(null,e),i._reactRetry=t,null):(e=a.treeContext,lt=Ht(i.nextSibling),ot=t,xe=!0,yt=null,e!==null&&(ct[dt++]=Rt,ct[dt++]=At,ct[dt++]=cn,Rt=e.id,At=e.overflow,cn=t),t=Ca(t,s.children),t.flags|=4096,t)}function Eu(e,t,n){e.lanes|=t;var s=e.alternate;s!==null&&(s.lanes|=t),ra(e.return,t,n)}function _a(e,t,n,s,i){var a=e.memoizedState;a===null?e.memoizedState={isBackwards:t,rendering:null,renderingStartTime:0,last:s,tail:n,tailMode:i}:(a.isBackwards=t,a.rendering=null,a.renderingStartTime=0,a.last=s,a.tail=n,a.tailMode=i)}function Tu(e,t,n){var s=t.pendingProps,i=s.revealOrder,a=s.tail;if(Ve(e,t,s.children,n),s=ke.current,(s&2)!==0)s=s&1|2,t.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=t.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Eu(e,n,t);else if(e.tag===19)Eu(e,n,t);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===t)break e;for(;e.sibling===null;){if(e.return===null||e.return===t)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}s&=1}if(fe(ke,s),(t.mode&1)===0)t.memoizedState=null;else switch(i){case"forwards":for(n=t.child,i=null;n!==null;)e=n.alternate,e!==null&&ys(e)===null&&(i=n),n=n.sibling;n=i,n===null?(i=t.child,t.child=null):(i=n.sibling,n.sibling=null),_a(t,!1,i,n,a);break;case"backwards":for(n=null,i=t.child,t.child=null;i!==null;){if(e=i.alternate,e!==null&&ys(e)===null){t.child=i;break}e=i.sibling,i.sibling=n,n=i,i=e}_a(t,!0,n,null,a);break;case"together":_a(t,!1,null,null,void 0);break;default:t.memoizedState=null}return t.child}function Cs(e,t){(t.mode&1)===0&&e!==null&&(e.alternate=null,t.alternate=null,t.flags|=2)}function zt(e,t,n){if(e!==null&&(t.dependencies=e.dependencies),fn|=t.lanes,(n&t.childLanes)===0)return null;if(e!==null&&t.child!==e.child)throw Error(c(153));if(t.child!==null){for(e=t.child,n=nn(e,e.pendingProps),t.child=n,n.return=t;e.sibling!==null;)e=e.sibling,n=n.sibling=nn(e,e.pendingProps),n.return=t;n.sibling=null}return t.child}function dm(e,t,n){switch(t.tag){case 3:bu(t),zn();break;case 5:$l(t);break;case 1:Qe(t.type)&&ls(t);break;case 4:aa(t,t.stateNode.containerInfo);break;case 10:var s=t.type._context,i=t.memoizedProps.value;fe(ps,s._currentValue),s._currentValue=i;break;case 13:if(s=t.memoizedState,s!==null)return s.dehydrated!==null?(fe(ke,ke.current&1),t.flags|=128,null):(n&t.child.childLanes)!==0?_u(e,t,n):(fe(ke,ke.current&1),e=zt(e,t,n),e!==null?e.sibling:null);fe(ke,ke.current&1);break;case 19:if(s=(n&t.childLanes)!==0,(e.flags&128)!==0){if(s)return Tu(e,t,n);t.flags|=128}if(i=t.memoizedState,i!==null&&(i.rendering=null,i.tail=null,i.lastEffect=null),fe(ke,ke.current),s)break;return null;case 22:case 23:return t.lanes=0,ju(e,t,n)}return zt(e,t,n)}var Pu,Ea,Mu,Lu;Pu=function(e,t){for(var n=t.child;n!==null;){if(n.tag===5||n.tag===6)e.appendChild(n.stateNode);else if(n.tag!==4&&n.child!==null){n.child.return=n,n=n.child;continue}if(n===t)break;for(;n.sibling===null;){if(n.return===null||n.return===t)return;n=n.return}n.sibling.return=n.return,n=n.sibling}},Ea=function(){},Mu=function(e,t,n,s){var i=e.memoizedProps;if(i!==s){e=t.stateNode,hn(_t.current);var a=null;switch(n){case"input":i=ri(e,i),s=ri(e,s),a=[];break;case"select":i=V({},i,{value:void 0}),s=V({},s,{value:void 0}),a=[];break;case"textarea":i=ai(e,i),s=ai(e,s),a=[];break;default:typeof i.onClick!="function"&&typeof s.onClick=="function"&&(e.onclick=is)}li(n,s);var l;n=null;for(k in i)if(!s.hasOwnProperty(k)&&i.hasOwnProperty(k)&&i[k]!=null)if(k==="style"){var d=i[k];for(l in d)d.hasOwnProperty(l)&&(n||(n={}),n[l]="")}else k!=="dangerouslySetInnerHTML"&&k!=="children"&&k!=="suppressContentEditableWarning"&&k!=="suppressHydrationWarning"&&k!=="autoFocus"&&(p.hasOwnProperty(k)?a||(a=[]):(a=a||[]).push(k,null));for(k in s){var m=s[k];if(d=i!=null?i[k]:void 0,s.hasOwnProperty(k)&&m!==d&&(m!=null||d!=null))if(k==="style")if(d){for(l in d)!d.hasOwnProperty(l)||m&&m.hasOwnProperty(l)||(n||(n={}),n[l]="");for(l in m)m.hasOwnProperty(l)&&d[l]!==m[l]&&(n||(n={}),n[l]=m[l])}else n||(a||(a=[]),a.push(k,n)),n=m;else k==="dangerouslySetInnerHTML"?(m=m?m.__html:void 0,d=d?d.__html:void 0,m!=null&&d!==m&&(a=a||[]).push(k,m)):k==="children"?typeof m!="string"&&typeof m!="number"||(a=a||[]).push(k,""+m):k!=="suppressContentEditableWarning"&&k!=="suppressHydrationWarning"&&(p.hasOwnProperty(k)?(m!=null&&k==="onScroll"&&ge("scroll",e),a||d===m||(a=[])):(a=a||[]).push(k,m))}n&&(a=a||[]).push("style",n);var k=a;(t.updateQueue=k)&&(t.flags|=4)}},Lu=function(e,t,n,s){n!==s&&(t.flags|=4)};function _r(e,t){if(!xe)switch(e.tailMode){case"hidden":t=e.tail;for(var n=null;t!==null;)t.alternate!==null&&(n=t),t=t.sibling;n===null?e.tail=null:n.sibling=null;break;case"collapsed":n=e.tail;for(var s=null;n!==null;)n.alternate!==null&&(s=n),n=n.sibling;s===null?t||e.tail===null?e.tail=null:e.tail.sibling=null:s.sibling=null}}function Oe(e){var t=e.alternate!==null&&e.alternate.child===e.child,n=0,s=0;if(t)for(var i=e.child;i!==null;)n|=i.lanes|i.childLanes,s|=i.subtreeFlags&14680064,s|=i.flags&14680064,i.return=e,i=i.sibling;else for(i=e.child;i!==null;)n|=i.lanes|i.childLanes,s|=i.subtreeFlags,s|=i.flags,i.return=e,i=i.sibling;return e.subtreeFlags|=s,e.childLanes=n,t}function mm(e,t,n){var s=t.pendingProps;switch(qi(t),t.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Oe(t),null;case 1:return Qe(t.type)&&os(),Oe(t),null;case 3:return s=t.stateNode,Un(),ve(Ke),ve(Fe),ua(),s.pendingContext&&(s.context=s.pendingContext,s.pendingContext=null),(e===null||e.child===null)&&(ms(t)?t.flags|=4:e===null||e.memoizedState.isDehydrated&&(t.flags&256)===0||(t.flags|=1024,yt!==null&&(Ba(yt),yt=null))),Ea(e,t),Oe(t),null;case 5:oa(t);var i=hn(jr.current);if(n=t.type,e!==null&&t.stateNode!=null)Mu(e,t,n,s,i),e.ref!==t.ref&&(t.flags|=512,t.flags|=2097152);else{if(!s){if(t.stateNode===null)throw Error(c(166));return Oe(t),null}if(e=hn(_t.current),ms(t)){s=t.stateNode,n=t.type;var a=t.memoizedProps;switch(s[Ct]=t,s[vr]=a,e=(t.mode&1)!==0,n){case"dialog":ge("cancel",s),ge("close",s);break;case"iframe":case"object":case"embed":ge("load",s);break;case"video":case"audio":for(i=0;i<pr.length;i++)ge(pr[i],s);break;case"source":ge("error",s);break;case"img":case"image":case"link":ge("error",s),ge("load",s);break;case"details":ge("toggle",s);break;case"input":mo(s,a),ge("invalid",s);break;case"select":s._wrapperState={wasMultiple:!!a.multiple},ge("invalid",s);break;case"textarea":fo(s,a),ge("invalid",s)}li(n,a),i=null;for(var l in a)if(a.hasOwnProperty(l)){var d=a[l];l==="children"?typeof d=="string"?s.textContent!==d&&(a.suppressHydrationWarning!==!0&&ss(s.textContent,d,e),i=["children",d]):typeof d=="number"&&s.textContent!==""+d&&(a.suppressHydrationWarning!==!0&&ss(s.textContent,d,e),i=["children",""+d]):p.hasOwnProperty(l)&&d!=null&&l==="onScroll"&&ge("scroll",s)}switch(n){case"input":Dr(s),po(s,a,!0);break;case"textarea":Dr(s),vo(s);break;case"select":case"option":break;default:typeof a.onClick=="function"&&(s.onclick=is)}s=i,t.updateQueue=s,s!==null&&(t.flags|=4)}else{l=i.nodeType===9?i:i.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=yo(n)),e==="http://www.w3.org/1999/xhtml"?n==="script"?(e=l.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof s.is=="string"?e=l.createElement(n,{is:s.is}):(e=l.createElement(n),n==="select"&&(l=e,s.multiple?l.multiple=!0:s.size&&(l.size=s.size))):e=l.createElementNS(e,n),e[Ct]=t,e[vr]=s,Pu(e,t,!1,!1),t.stateNode=e;e:{switch(l=ui(n,s),n){case"dialog":ge("cancel",e),ge("close",e),i=s;break;case"iframe":case"object":case"embed":ge("load",e),i=s;break;case"video":case"audio":for(i=0;i<pr.length;i++)ge(pr[i],e);i=s;break;case"source":ge("error",e),i=s;break;case"img":case"image":case"link":ge("error",e),ge("load",e),i=s;break;case"details":ge("toggle",e),i=s;break;case"input":mo(e,s),i=ri(e,s),ge("invalid",e);break;case"option":i=s;break;case"select":e._wrapperState={wasMultiple:!!s.multiple},i=V({},s,{value:void 0}),ge("invalid",e);break;case"textarea":fo(e,s),i=ai(e,s),ge("invalid",e);break;default:i=s}li(n,i),d=i;for(a in d)if(d.hasOwnProperty(a)){var m=d[a];a==="style"?wo(e,m):a==="dangerouslySetInnerHTML"?(m=m?m.__html:void 0,m!=null&&xo(e,m)):a==="children"?typeof m=="string"?(n!=="textarea"||m!=="")&&Xn(e,m):typeof m=="number"&&Xn(e,""+m):a!=="suppressContentEditableWarning"&&a!=="suppressHydrationWarning"&&a!=="autoFocus"&&(p.hasOwnProperty(a)?m!=null&&a==="onScroll"&&ge("scroll",e):m!=null&&Q(e,a,m,l))}switch(n){case"input":Dr(e),po(e,s,!1);break;case"textarea":Dr(e),vo(e);break;case"option":s.value!=null&&e.setAttribute("value",""+ce(s.value));break;case"select":e.multiple=!!s.multiple,a=s.value,a!=null?jn(e,!!s.multiple,a,!1):s.defaultValue!=null&&jn(e,!!s.multiple,s.defaultValue,!0);break;default:typeof i.onClick=="function"&&(e.onclick=is)}switch(n){case"button":case"input":case"select":case"textarea":s=!!s.autoFocus;break e;case"img":s=!0;break e;default:s=!1}}s&&(t.flags|=4)}t.ref!==null&&(t.flags|=512,t.flags|=2097152)}return Oe(t),null;case 6:if(e&&t.stateNode!=null)Lu(e,t,e.memoizedProps,s);else{if(typeof s!="string"&&t.stateNode===null)throw Error(c(166));if(n=hn(jr.current),hn(_t.current),ms(t)){if(s=t.stateNode,n=t.memoizedProps,s[Ct]=t,(a=s.nodeValue!==n)&&(e=ot,e!==null))switch(e.tag){case 3:ss(s.nodeValue,n,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&ss(s.nodeValue,n,(e.mode&1)!==0)}a&&(t.flags|=4)}else s=(n.nodeType===9?n:n.ownerDocument).createTextNode(s),s[Ct]=t,t.stateNode=s}return Oe(t),null;case 13:if(ve(ke),s=t.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(xe&&lt!==null&&(t.mode&1)!==0&&(t.flags&128)===0)Dl(),zn(),t.flags|=98560,a=!1;else if(a=ms(t),s!==null&&s.dehydrated!==null){if(e===null){if(!a)throw Error(c(318));if(a=t.memoizedState,a=a!==null?a.dehydrated:null,!a)throw Error(c(317));a[Ct]=t}else zn(),(t.flags&128)===0&&(t.memoizedState=null),t.flags|=4;Oe(t),a=!1}else yt!==null&&(Ba(yt),yt=null),a=!0;if(!a)return t.flags&65536?t:null}return(t.flags&128)!==0?(t.lanes=n,t):(s=s!==null,s!==(e!==null&&e.memoizedState!==null)&&s&&(t.child.flags|=8192,(t.mode&1)!==0&&(e===null||(ke.current&1)!==0?Pe===0&&(Pe=3):Wa())),t.updateQueue!==null&&(t.flags|=4),Oe(t),null);case 4:return Un(),Ea(e,t),e===null&&fr(t.stateNode.containerInfo),Oe(t),null;case 10:return na(t.type._context),Oe(t),null;case 17:return Qe(t.type)&&os(),Oe(t),null;case 19:if(ve(ke),a=t.memoizedState,a===null)return Oe(t),null;if(s=(t.flags&128)!==0,l=a.rendering,l===null)if(s)_r(a,!1);else{if(Pe!==0||e!==null&&(e.flags&128)!==0)for(e=t.child;e!==null;){if(l=ys(e),l!==null){for(t.flags|=128,_r(a,!1),s=l.updateQueue,s!==null&&(t.updateQueue=s,t.flags|=4),t.subtreeFlags=0,s=n,n=t.child;n!==null;)a=n,e=s,a.flags&=14680066,l=a.alternate,l===null?(a.childLanes=0,a.lanes=e,a.child=null,a.subtreeFlags=0,a.memoizedProps=null,a.memoizedState=null,a.updateQueue=null,a.dependencies=null,a.stateNode=null):(a.childLanes=l.childLanes,a.lanes=l.lanes,a.child=l.child,a.subtreeFlags=0,a.deletions=null,a.memoizedProps=l.memoizedProps,a.memoizedState=l.memoizedState,a.updateQueue=l.updateQueue,a.type=l.type,e=l.dependencies,a.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),n=n.sibling;return fe(ke,ke.current&1|2),t.child}e=e.sibling}a.tail!==null&&be()>Hn&&(t.flags|=128,s=!0,_r(a,!1),t.lanes=4194304)}else{if(!s)if(e=ys(l),e!==null){if(t.flags|=128,s=!0,n=e.updateQueue,n!==null&&(t.updateQueue=n,t.flags|=4),_r(a,!0),a.tail===null&&a.tailMode==="hidden"&&!l.alternate&&!xe)return Oe(t),null}else 2*be()-a.renderingStartTime>Hn&&n!==1073741824&&(t.flags|=128,s=!0,_r(a,!1),t.lanes=4194304);a.isBackwards?(l.sibling=t.child,t.child=l):(n=a.last,n!==null?n.sibling=l:t.child=l,a.last=l)}return a.tail!==null?(t=a.tail,a.rendering=t,a.tail=t.sibling,a.renderingStartTime=be(),t.sibling=null,n=ke.current,fe(ke,s?n&1|2:n&1),t):(Oe(t),null);case 22:case 23:return Ua(),s=t.memoizedState!==null,e!==null&&e.memoizedState!==null!==s&&(t.flags|=8192),s&&(t.mode&1)!==0?(ut&1073741824)!==0&&(Oe(t),t.subtreeFlags&6&&(t.flags|=8192)):Oe(t),null;case 24:return null;case 25:return null}throw Error(c(156,t.tag))}function hm(e,t){switch(qi(t),t.tag){case 1:return Qe(t.type)&&os(),e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 3:return Un(),ve(Ke),ve(Fe),ua(),e=t.flags,(e&65536)!==0&&(e&128)===0?(t.flags=e&-65537|128,t):null;case 5:return oa(t),null;case 13:if(ve(ke),e=t.memoizedState,e!==null&&e.dehydrated!==null){if(t.alternate===null)throw Error(c(340));zn()}return e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 19:return ve(ke),null;case 4:return Un(),null;case 10:return na(t.type._context),null;case 22:case 23:return Ua(),null;case 24:return null;default:return null}}var _s=!1,Ue=!1,pm=typeof WeakSet=="function"?WeakSet:Set,$=null;function $n(e,t){var n=e.ref;if(n!==null)if(typeof n=="function")try{n(null)}catch(s){Ne(e,t,s)}else n.current=null}function Ta(e,t,n){try{n()}catch(s){Ne(e,t,s)}}var Ru=!1;function fm(e,t){if(Ui=Kr,e=dl(),Ri(e)){if("selectionStart"in e)var n={start:e.selectionStart,end:e.selectionEnd};else e:{n=(n=e.ownerDocument)&&n.defaultView||window;var s=n.getSelection&&n.getSelection();if(s&&s.rangeCount!==0){n=s.anchorNode;var i=s.anchorOffset,a=s.focusNode;s=s.focusOffset;try{n.nodeType,a.nodeType}catch{n=null;break e}var l=0,d=-1,m=-1,k=0,P=0,L=e,E=null;t:for(;;){for(var U;L!==n||i!==0&&L.nodeType!==3||(d=l+i),L!==a||s!==0&&L.nodeType!==3||(m=l+s),L.nodeType===3&&(l+=L.nodeValue.length),(U=L.firstChild)!==null;)E=L,L=U;for(;;){if(L===e)break t;if(E===n&&++k===i&&(d=l),E===a&&++P===s&&(m=l),(U=L.nextSibling)!==null)break;L=E,E=L.parentNode}L=U}n=d===-1||m===-1?null:{start:d,end:m}}else n=null}n=n||{start:0,end:0}}else n=null;for(Wi={focusedElem:e,selectionRange:n},Kr=!1,$=t;$!==null;)if(t=$,e=t.child,(t.subtreeFlags&1028)!==0&&e!==null)e.return=t,$=e;else for(;$!==null;){t=$;try{var H=t.alternate;if((t.flags&1024)!==0)switch(t.tag){case 0:case 11:case 15:break;case 1:if(H!==null){var G=H.memoizedProps,Ce=H.memoizedState,v=t.stateNode,h=v.getSnapshotBeforeUpdate(t.elementType===t.type?G:xt(t.type,G),Ce);v.__reactInternalSnapshotBeforeUpdate=h}break;case 3:var y=t.stateNode.containerInfo;y.nodeType===1?y.textContent="":y.nodeType===9&&y.documentElement&&y.removeChild(y.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(c(163))}}catch(A){Ne(t,t.return,A)}if(e=t.sibling,e!==null){e.return=t.return,$=e;break}$=t.return}return H=Ru,Ru=!1,H}function Er(e,t,n){var s=t.updateQueue;if(s=s!==null?s.lastEffect:null,s!==null){var i=s=s.next;do{if((i.tag&e)===e){var a=i.destroy;i.destroy=void 0,a!==void 0&&Ta(t,n,a)}i=i.next}while(i!==s)}}function Es(e,t){if(t=t.updateQueue,t=t!==null?t.lastEffect:null,t!==null){var n=t=t.next;do{if((n.tag&e)===e){var s=n.create;n.destroy=s()}n=n.next}while(n!==t)}}function Pa(e){var t=e.ref;if(t!==null){var n=e.stateNode;switch(e.tag){case 5:e=n;break;default:e=n}typeof t=="function"?t(e):t.current=e}}function Au(e){var t=e.alternate;t!==null&&(e.alternate=null,Au(t)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(t=e.stateNode,t!==null&&(delete t[Ct],delete t[vr],delete t[Gi],delete t[Yd],delete t[Jd])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function Du(e){return e.tag===5||e.tag===3||e.tag===4}function Iu(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||Du(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Ma(e,t,n){var s=e.tag;if(s===5||s===6)e=e.stateNode,t?n.nodeType===8?n.parentNode.insertBefore(e,t):n.insertBefore(e,t):(n.nodeType===8?(t=n.parentNode,t.insertBefore(e,n)):(t=n,t.appendChild(e)),n=n._reactRootContainer,n!=null||t.onclick!==null||(t.onclick=is));else if(s!==4&&(e=e.child,e!==null))for(Ma(e,t,n),e=e.sibling;e!==null;)Ma(e,t,n),e=e.sibling}function La(e,t,n){var s=e.tag;if(s===5||s===6)e=e.stateNode,t?n.insertBefore(e,t):n.appendChild(e);else if(s!==4&&(e=e.child,e!==null))for(La(e,t,n),e=e.sibling;e!==null;)La(e,t,n),e=e.sibling}var De=null,kt=!1;function Yt(e,t,n){for(n=n.child;n!==null;)zu(e,t,n),n=n.sibling}function zu(e,t,n){if(bt&&typeof bt.onCommitFiberUnmount=="function")try{bt.onCommitFiberUnmount(Ur,n)}catch{}switch(n.tag){case 5:Ue||$n(n,t);case 6:var s=De,i=kt;De=null,Yt(e,t,n),De=s,kt=i,De!==null&&(kt?(e=De,n=n.stateNode,e.nodeType===8?e.parentNode.removeChild(n):e.removeChild(n)):De.removeChild(n.stateNode));break;case 18:De!==null&&(kt?(e=De,n=n.stateNode,e.nodeType===8?Hi(e.parentNode,n):e.nodeType===1&&Hi(e,n),ar(e)):Hi(De,n.stateNode));break;case 4:s=De,i=kt,De=n.stateNode.containerInfo,kt=!0,Yt(e,t,n),De=s,kt=i;break;case 0:case 11:case 14:case 15:if(!Ue&&(s=n.updateQueue,s!==null&&(s=s.lastEffect,s!==null))){i=s=s.next;do{var a=i,l=a.destroy;a=a.tag,l!==void 0&&((a&2)!==0||(a&4)!==0)&&Ta(n,t,l),i=i.next}while(i!==s)}Yt(e,t,n);break;case 1:if(!Ue&&($n(n,t),s=n.stateNode,typeof s.componentWillUnmount=="function"))try{s.props=n.memoizedProps,s.state=n.memoizedState,s.componentWillUnmount()}catch(d){Ne(n,t,d)}Yt(e,t,n);break;case 21:Yt(e,t,n);break;case 22:n.mode&1?(Ue=(s=Ue)||n.memoizedState!==null,Yt(e,t,n),Ue=s):Yt(e,t,n);break;default:Yt(e,t,n)}}function Fu(e){var t=e.updateQueue;if(t!==null){e.updateQueue=null;var n=e.stateNode;n===null&&(n=e.stateNode=new pm),t.forEach(function(s){var i=Nm.bind(null,e,s);n.has(s)||(n.add(s),s.then(i,i))})}}function wt(e,t){var n=t.deletions;if(n!==null)for(var s=0;s<n.length;s++){var i=n[s];try{var a=e,l=t,d=l;e:for(;d!==null;){switch(d.tag){case 5:De=d.stateNode,kt=!1;break e;case 3:De=d.stateNode.containerInfo,kt=!0;break e;case 4:De=d.stateNode.containerInfo,kt=!0;break e}d=d.return}if(De===null)throw Error(c(160));zu(a,l,i),De=null,kt=!1;var m=i.alternate;m!==null&&(m.return=null),i.return=null}catch(k){Ne(i,t,k)}}if(t.subtreeFlags&12854)for(t=t.child;t!==null;)Bu(t,e),t=t.sibling}function Bu(e,t){var n=e.alternate,s=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(wt(t,e),Tt(e),s&4){try{Er(3,e,e.return),Es(3,e)}catch(G){Ne(e,e.return,G)}try{Er(5,e,e.return)}catch(G){Ne(e,e.return,G)}}break;case 1:wt(t,e),Tt(e),s&512&&n!==null&&$n(n,n.return);break;case 5:if(wt(t,e),Tt(e),s&512&&n!==null&&$n(n,n.return),e.flags&32){var i=e.stateNode;try{Xn(i,"")}catch(G){Ne(e,e.return,G)}}if(s&4&&(i=e.stateNode,i!=null)){var a=e.memoizedProps,l=n!==null?n.memoizedProps:a,d=e.type,m=e.updateQueue;if(e.updateQueue=null,m!==null)try{d==="input"&&a.type==="radio"&&a.name!=null&&ho(i,a),ui(d,l);var k=ui(d,a);for(l=0;l<m.length;l+=2){var P=m[l],L=m[l+1];P==="style"?wo(i,L):P==="dangerouslySetInnerHTML"?xo(i,L):P==="children"?Xn(i,L):Q(i,P,L,k)}switch(d){case"input":si(i,a);break;case"textarea":go(i,a);break;case"select":var E=i._wrapperState.wasMultiple;i._wrapperState.wasMultiple=!!a.multiple;var U=a.value;U!=null?jn(i,!!a.multiple,U,!1):E!==!!a.multiple&&(a.defaultValue!=null?jn(i,!!a.multiple,a.defaultValue,!0):jn(i,!!a.multiple,a.multiple?[]:"",!1))}i[vr]=a}catch(G){Ne(e,e.return,G)}}break;case 6:if(wt(t,e),Tt(e),s&4){if(e.stateNode===null)throw Error(c(162));i=e.stateNode,a=e.memoizedProps;try{i.nodeValue=a}catch(G){Ne(e,e.return,G)}}break;case 3:if(wt(t,e),Tt(e),s&4&&n!==null&&n.memoizedState.isDehydrated)try{ar(t.containerInfo)}catch(G){Ne(e,e.return,G)}break;case 4:wt(t,e),Tt(e);break;case 13:wt(t,e),Tt(e),i=e.child,i.flags&8192&&(a=i.memoizedState!==null,i.stateNode.isHidden=a,!a||i.alternate!==null&&i.alternate.memoizedState!==null||(Da=be())),s&4&&Fu(e);break;case 22:if(P=n!==null&&n.memoizedState!==null,e.mode&1?(Ue=(k=Ue)||P,wt(t,e),Ue=k):wt(t,e),Tt(e),s&8192){if(k=e.memoizedState!==null,(e.stateNode.isHidden=k)&&!P&&(e.mode&1)!==0)for($=e,P=e.child;P!==null;){for(L=$=P;$!==null;){switch(E=$,U=E.child,E.tag){case 0:case 11:case 14:case 15:Er(4,E,E.return);break;case 1:$n(E,E.return);var H=E.stateNode;if(typeof H.componentWillUnmount=="function"){s=E,n=E.return;try{t=s,H.props=t.memoizedProps,H.state=t.memoizedState,H.componentWillUnmount()}catch(G){Ne(s,n,G)}}break;case 5:$n(E,E.return);break;case 22:if(E.memoizedState!==null){Wu(L);continue}}U!==null?(U.return=E,$=U):Wu(L)}P=P.sibling}e:for(P=null,L=e;;){if(L.tag===5){if(P===null){P=L;try{i=L.stateNode,k?(a=i.style,typeof a.setProperty=="function"?a.setProperty("display","none","important"):a.display="none"):(d=L.stateNode,m=L.memoizedProps.style,l=m!=null&&m.hasOwnProperty("display")?m.display:null,d.style.display=ko("display",l))}catch(G){Ne(e,e.return,G)}}}else if(L.tag===6){if(P===null)try{L.stateNode.nodeValue=k?"":L.memoizedProps}catch(G){Ne(e,e.return,G)}}else if((L.tag!==22&&L.tag!==23||L.memoizedState===null||L===e)&&L.child!==null){L.child.return=L,L=L.child;continue}if(L===e)break e;for(;L.sibling===null;){if(L.return===null||L.return===e)break e;P===L&&(P=null),L=L.return}P===L&&(P=null),L.sibling.return=L.return,L=L.sibling}}break;case 19:wt(t,e),Tt(e),s&4&&Fu(e);break;case 21:break;default:wt(t,e),Tt(e)}}function Tt(e){var t=e.flags;if(t&2){try{e:{for(var n=e.return;n!==null;){if(Du(n)){var s=n;break e}n=n.return}throw Error(c(160))}switch(s.tag){case 5:var i=s.stateNode;s.flags&32&&(Xn(i,""),s.flags&=-33);var a=Iu(e);La(e,a,i);break;case 3:case 4:var l=s.stateNode.containerInfo,d=Iu(e);Ma(e,d,l);break;default:throw Error(c(161))}}catch(m){Ne(e,e.return,m)}e.flags&=-3}t&4096&&(e.flags&=-4097)}function gm(e,t,n){$=e,Ou(e)}function Ou(e,t,n){for(var s=(e.mode&1)!==0;$!==null;){var i=$,a=i.child;if(i.tag===22&&s){var l=i.memoizedState!==null||_s;if(!l){var d=i.alternate,m=d!==null&&d.memoizedState!==null||Ue;d=_s;var k=Ue;if(_s=l,(Ue=m)&&!k)for($=i;$!==null;)l=$,m=l.child,l.tag===22&&l.memoizedState!==null?$u(i):m!==null?(m.return=l,$=m):$u(i);for(;a!==null;)$=a,Ou(a),a=a.sibling;$=i,_s=d,Ue=k}Uu(e)}else(i.subtreeFlags&8772)!==0&&a!==null?(a.return=i,$=a):Uu(e)}}function Uu(e){for(;$!==null;){var t=$;if((t.flags&8772)!==0){var n=t.alternate;try{if((t.flags&8772)!==0)switch(t.tag){case 0:case 11:case 15:Ue||Es(5,t);break;case 1:var s=t.stateNode;if(t.flags&4&&!Ue)if(n===null)s.componentDidMount();else{var i=t.elementType===t.type?n.memoizedProps:xt(t.type,n.memoizedProps);s.componentDidUpdate(i,n.memoizedState,s.__reactInternalSnapshotBeforeUpdate)}var a=t.updateQueue;a!==null&&Wl(t,a,s);break;case 3:var l=t.updateQueue;if(l!==null){if(n=null,t.child!==null)switch(t.child.tag){case 5:n=t.child.stateNode;break;case 1:n=t.child.stateNode}Wl(t,l,n)}break;case 5:var d=t.stateNode;if(n===null&&t.flags&4){n=d;var m=t.memoizedProps;switch(t.type){case"button":case"input":case"select":case"textarea":m.autoFocus&&n.focus();break;case"img":m.src&&(n.src=m.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(t.memoizedState===null){var k=t.alternate;if(k!==null){var P=k.memoizedState;if(P!==null){var L=P.dehydrated;L!==null&&ar(L)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(c(163))}Ue||t.flags&512&&Pa(t)}catch(E){Ne(t,t.return,E)}}if(t===e){$=null;break}if(n=t.sibling,n!==null){n.return=t.return,$=n;break}$=t.return}}function Wu(e){for(;$!==null;){var t=$;if(t===e){$=null;break}var n=t.sibling;if(n!==null){n.return=t.return,$=n;break}$=t.return}}function $u(e){for(;$!==null;){var t=$;try{switch(t.tag){case 0:case 11:case 15:var n=t.return;try{Es(4,t)}catch(m){Ne(t,n,m)}break;case 1:var s=t.stateNode;if(typeof s.componentDidMount=="function"){var i=t.return;try{s.componentDidMount()}catch(m){Ne(t,i,m)}}var a=t.return;try{Pa(t)}catch(m){Ne(t,a,m)}break;case 5:var l=t.return;try{Pa(t)}catch(m){Ne(t,l,m)}}}catch(m){Ne(t,t.return,m)}if(t===e){$=null;break}var d=t.sibling;if(d!==null){d.return=t.return,$=d;break}$=t.return}}var vm=Math.ceil,Ts=te.ReactCurrentDispatcher,Ra=te.ReactCurrentOwner,pt=te.ReactCurrentBatchConfig,ae=0,Re=null,_e=null,Ie=0,ut=0,Vn=Gt(0),Pe=0,Tr=null,fn=0,Ps=0,Aa=0,Pr=null,qe=null,Da=0,Hn=1/0,Ft=null,Ms=!1,Ia=null,Jt=null,Ls=!1,Zt=null,Rs=0,Mr=0,za=null,As=-1,Ds=0;function He(){return(ae&6)!==0?be():As!==-1?As:As=be()}function en(e){return(e.mode&1)===0?1:(ae&2)!==0&&Ie!==0?Ie&-Ie:em.transition!==null?(Ds===0&&(Ds=Io()),Ds):(e=de,e!==0||(e=window.event,e=e===void 0?16:Ho(e.type)),e)}function jt(e,t,n,s){if(50<Mr)throw Mr=0,za=null,Error(c(185));tr(e,n,s),((ae&2)===0||e!==Re)&&(e===Re&&((ae&2)===0&&(Ps|=n),Pe===4&&tn(e,Ie)),Ye(e,s),n===1&&ae===0&&(t.mode&1)===0&&(Hn=be()+500,us&&Qt()))}function Ye(e,t){var n=e.callbackNode;ed(e,t);var s=Vr(e,e===Re?Ie:0);if(s===0)n!==null&&Ro(n),e.callbackNode=null,e.callbackPriority=0;else if(t=s&-s,e.callbackPriority!==t){if(n!=null&&Ro(n),t===1)e.tag===0?Zd(Hu.bind(null,e)):Pl(Hu.bind(null,e)),Xd(function(){(ae&6)===0&&Qt()}),n=null;else{switch(zo(s)){case 1:n=gi;break;case 4:n=Ao;break;case 16:n=Or;break;case 536870912:n=Do;break;default:n=Or}n=Zu(n,Vu.bind(null,e))}e.callbackPriority=t,e.callbackNode=n}}function Vu(e,t){if(As=-1,Ds=0,(ae&6)!==0)throw Error(c(327));var n=e.callbackNode;if(Gn()&&e.callbackNode!==n)return null;var s=Vr(e,e===Re?Ie:0);if(s===0)return null;if((s&30)!==0||(s&e.expiredLanes)!==0||t)t=Is(e,s);else{t=s;var i=ae;ae|=2;var a=Ku();(Re!==e||Ie!==t)&&(Ft=null,Hn=be()+500,vn(e,t));do try{km();break}catch(d){Gu(e,d)}while(!0);ta(),Ts.current=a,ae=i,_e!==null?t=0:(Re=null,Ie=0,t=Pe)}if(t!==0){if(t===2&&(i=vi(e),i!==0&&(s=i,t=Fa(e,i))),t===1)throw n=Tr,vn(e,0),tn(e,s),Ye(e,be()),n;if(t===6)tn(e,s);else{if(i=e.current.alternate,(s&30)===0&&!ym(i)&&(t=Is(e,s),t===2&&(a=vi(e),a!==0&&(s=a,t=Fa(e,a))),t===1))throw n=Tr,vn(e,0),tn(e,s),Ye(e,be()),n;switch(e.finishedWork=i,e.finishedLanes=s,t){case 0:case 1:throw Error(c(345));case 2:yn(e,qe,Ft);break;case 3:if(tn(e,s),(s&130023424)===s&&(t=Da+500-be(),10<t)){if(Vr(e,0)!==0)break;if(i=e.suspendedLanes,(i&s)!==s){He(),e.pingedLanes|=e.suspendedLanes&i;break}e.timeoutHandle=Vi(yn.bind(null,e,qe,Ft),t);break}yn(e,qe,Ft);break;case 4:if(tn(e,s),(s&4194240)===s)break;for(t=e.eventTimes,i=-1;0<s;){var l=31-gt(s);a=1<<l,l=t[l],l>i&&(i=l),s&=~a}if(s=i,s=be()-s,s=(120>s?120:480>s?480:1080>s?1080:1920>s?1920:3e3>s?3e3:4320>s?4320:1960*vm(s/1960))-s,10<s){e.timeoutHandle=Vi(yn.bind(null,e,qe,Ft),s);break}yn(e,qe,Ft);break;case 5:yn(e,qe,Ft);break;default:throw Error(c(329))}}}return Ye(e,be()),e.callbackNode===n?Vu.bind(null,e):null}function Fa(e,t){var n=Pr;return e.current.memoizedState.isDehydrated&&(vn(e,t).flags|=256),e=Is(e,t),e!==2&&(t=qe,qe=n,t!==null&&Ba(t)),e}function Ba(e){qe===null?qe=e:qe.push.apply(qe,e)}function ym(e){for(var t=e;;){if(t.flags&16384){var n=t.updateQueue;if(n!==null&&(n=n.stores,n!==null))for(var s=0;s<n.length;s++){var i=n[s],a=i.getSnapshot;i=i.value;try{if(!vt(a(),i))return!1}catch{return!1}}}if(n=t.child,t.subtreeFlags&16384&&n!==null)n.return=t,t=n;else{if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return!0;t=t.return}t.sibling.return=t.return,t=t.sibling}}return!0}function tn(e,t){for(t&=~Aa,t&=~Ps,e.suspendedLanes|=t,e.pingedLanes&=~t,e=e.expirationTimes;0<t;){var n=31-gt(t),s=1<<n;e[n]=-1,t&=~s}}function Hu(e){if((ae&6)!==0)throw Error(c(327));Gn();var t=Vr(e,0);if((t&1)===0)return Ye(e,be()),null;var n=Is(e,t);if(e.tag!==0&&n===2){var s=vi(e);s!==0&&(t=s,n=Fa(e,s))}if(n===1)throw n=Tr,vn(e,0),tn(e,t),Ye(e,be()),n;if(n===6)throw Error(c(345));return e.finishedWork=e.current.alternate,e.finishedLanes=t,yn(e,qe,Ft),Ye(e,be()),null}function Oa(e,t){var n=ae;ae|=1;try{return e(t)}finally{ae=n,ae===0&&(Hn=be()+500,us&&Qt())}}function gn(e){Zt!==null&&Zt.tag===0&&(ae&6)===0&&Gn();var t=ae;ae|=1;var n=pt.transition,s=de;try{if(pt.transition=null,de=1,e)return e()}finally{de=s,pt.transition=n,ae=t,(ae&6)===0&&Qt()}}function Ua(){ut=Vn.current,ve(Vn)}function vn(e,t){e.finishedWork=null,e.finishedLanes=0;var n=e.timeoutHandle;if(n!==-1&&(e.timeoutHandle=-1,Qd(n)),_e!==null)for(n=_e.return;n!==null;){var s=n;switch(qi(s),s.tag){case 1:s=s.type.childContextTypes,s!=null&&os();break;case 3:Un(),ve(Ke),ve(Fe),ua();break;case 5:oa(s);break;case 4:Un();break;case 13:ve(ke);break;case 19:ve(ke);break;case 10:na(s.type._context);break;case 22:case 23:Ua()}n=n.return}if(Re=e,_e=e=nn(e.current,null),Ie=ut=t,Pe=0,Tr=null,Aa=Ps=fn=0,qe=Pr=null,mn!==null){for(t=0;t<mn.length;t++)if(n=mn[t],s=n.interleaved,s!==null){n.interleaved=null;var i=s.next,a=n.pending;if(a!==null){var l=a.next;a.next=i,s.next=l}n.pending=s}mn=null}return e}function Gu(e,t){do{var n=_e;try{if(ta(),xs.current=Ss,ks){for(var s=we.memoizedState;s!==null;){var i=s.queue;i!==null&&(i.pending=null),s=s.next}ks=!1}if(pn=0,Le=Te=we=null,Sr=!1,Nr=0,Ra.current=null,n===null||n.return===null){Pe=1,Tr=t,_e=null;break}e:{var a=e,l=n.return,d=n,m=t;if(t=Ie,d.flags|=32768,m!==null&&typeof m=="object"&&typeof m.then=="function"){var k=m,P=d,L=P.tag;if((P.mode&1)===0&&(L===0||L===11||L===15)){var E=P.alternate;E?(P.updateQueue=E.updateQueue,P.memoizedState=E.memoizedState,P.lanes=E.lanes):(P.updateQueue=null,P.memoizedState=null)}var U=vu(l);if(U!==null){U.flags&=-257,yu(U,l,d,a,t),U.mode&1&&gu(a,k,t),t=U,m=k;var H=t.updateQueue;if(H===null){var G=new Set;G.add(m),t.updateQueue=G}else H.add(m);break e}else{if((t&1)===0){gu(a,k,t),Wa();break e}m=Error(c(426))}}else if(xe&&d.mode&1){var Ce=vu(l);if(Ce!==null){(Ce.flags&65536)===0&&(Ce.flags|=256),yu(Ce,l,d,a,t),Zi(Wn(m,d));break e}}a=m=Wn(m,d),Pe!==4&&(Pe=2),Pr===null?Pr=[a]:Pr.push(a),a=l;do{switch(a.tag){case 3:a.flags|=65536,t&=-t,a.lanes|=t;var v=pu(a,m,t);Ul(a,v);break e;case 1:d=m;var h=a.type,y=a.stateNode;if((a.flags&128)===0&&(typeof h.getDerivedStateFromError=="function"||y!==null&&typeof y.componentDidCatch=="function"&&(Jt===null||!Jt.has(y)))){a.flags|=65536,t&=-t,a.lanes|=t;var A=fu(a,d,t);Ul(a,A);break e}}a=a.return}while(a!==null)}Xu(n)}catch(K){t=K,_e===n&&n!==null&&(_e=n=n.return);continue}break}while(!0)}function Ku(){var e=Ts.current;return Ts.current=Ss,e===null?Ss:e}function Wa(){(Pe===0||Pe===3||Pe===2)&&(Pe=4),Re===null||(fn&268435455)===0&&(Ps&268435455)===0||tn(Re,Ie)}function Is(e,t){var n=ae;ae|=2;var s=Ku();(Re!==e||Ie!==t)&&(Ft=null,vn(e,t));do try{xm();break}catch(i){Gu(e,i)}while(!0);if(ta(),ae=n,Ts.current=s,_e!==null)throw Error(c(261));return Re=null,Ie=0,Pe}function xm(){for(;_e!==null;)Qu(_e)}function km(){for(;_e!==null&&!Hc();)Qu(_e)}function Qu(e){var t=Ju(e.alternate,e,ut);e.memoizedProps=e.pendingProps,t===null?Xu(e):_e=t,Ra.current=null}function Xu(e){var t=e;do{var n=t.alternate;if(e=t.return,(t.flags&32768)===0){if(n=mm(n,t,ut),n!==null){_e=n;return}}else{if(n=hm(n,t),n!==null){n.flags&=32767,_e=n;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{Pe=6,_e=null;return}}if(t=t.sibling,t!==null){_e=t;return}_e=t=e}while(t!==null);Pe===0&&(Pe=5)}function yn(e,t,n){var s=de,i=pt.transition;try{pt.transition=null,de=1,wm(e,t,n,s)}finally{pt.transition=i,de=s}return null}function wm(e,t,n,s){do Gn();while(Zt!==null);if((ae&6)!==0)throw Error(c(327));n=e.finishedWork;var i=e.finishedLanes;if(n===null)return null;if(e.finishedWork=null,e.finishedLanes=0,n===e.current)throw Error(c(177));e.callbackNode=null,e.callbackPriority=0;var a=n.lanes|n.childLanes;if(td(e,a),e===Re&&(_e=Re=null,Ie=0),(n.subtreeFlags&2064)===0&&(n.flags&2064)===0||Ls||(Ls=!0,Zu(Or,function(){return Gn(),null})),a=(n.flags&15990)!==0,(n.subtreeFlags&15990)!==0||a){a=pt.transition,pt.transition=null;var l=de;de=1;var d=ae;ae|=4,Ra.current=null,fm(e,n),Bu(n,e),Ud(Wi),Kr=!!Ui,Wi=Ui=null,e.current=n,gm(n),Gc(),ae=d,de=l,pt.transition=a}else e.current=n;if(Ls&&(Ls=!1,Zt=e,Rs=i),a=e.pendingLanes,a===0&&(Jt=null),Xc(n.stateNode),Ye(e,be()),t!==null)for(s=e.onRecoverableError,n=0;n<t.length;n++)i=t[n],s(i.value,{componentStack:i.stack,digest:i.digest});if(Ms)throw Ms=!1,e=Ia,Ia=null,e;return(Rs&1)!==0&&e.tag!==0&&Gn(),a=e.pendingLanes,(a&1)!==0?e===za?Mr++:(Mr=0,za=e):Mr=0,Qt(),null}function Gn(){if(Zt!==null){var e=zo(Rs),t=pt.transition,n=de;try{if(pt.transition=null,de=16>e?16:e,Zt===null)var s=!1;else{if(e=Zt,Zt=null,Rs=0,(ae&6)!==0)throw Error(c(331));var i=ae;for(ae|=4,$=e.current;$!==null;){var a=$,l=a.child;if(($.flags&16)!==0){var d=a.deletions;if(d!==null){for(var m=0;m<d.length;m++){var k=d[m];for($=k;$!==null;){var P=$;switch(P.tag){case 0:case 11:case 15:Er(8,P,a)}var L=P.child;if(L!==null)L.return=P,$=L;else for(;$!==null;){P=$;var E=P.sibling,U=P.return;if(Au(P),P===k){$=null;break}if(E!==null){E.return=U,$=E;break}$=U}}}var H=a.alternate;if(H!==null){var G=H.child;if(G!==null){H.child=null;do{var Ce=G.sibling;G.sibling=null,G=Ce}while(G!==null)}}$=a}}if((a.subtreeFlags&2064)!==0&&l!==null)l.return=a,$=l;else e:for(;$!==null;){if(a=$,(a.flags&2048)!==0)switch(a.tag){case 0:case 11:case 15:Er(9,a,a.return)}var v=a.sibling;if(v!==null){v.return=a.return,$=v;break e}$=a.return}}var h=e.current;for($=h;$!==null;){l=$;var y=l.child;if((l.subtreeFlags&2064)!==0&&y!==null)y.return=l,$=y;else e:for(l=h;$!==null;){if(d=$,(d.flags&2048)!==0)try{switch(d.tag){case 0:case 11:case 15:Es(9,d)}}catch(K){Ne(d,d.return,K)}if(d===l){$=null;break e}var A=d.sibling;if(A!==null){A.return=d.return,$=A;break e}$=d.return}}if(ae=i,Qt(),bt&&typeof bt.onPostCommitFiberRoot=="function")try{bt.onPostCommitFiberRoot(Ur,e)}catch{}s=!0}return s}finally{de=n,pt.transition=t}}return!1}function qu(e,t,n){t=Wn(n,t),t=pu(e,t,1),e=qt(e,t,1),t=He(),e!==null&&(tr(e,1,t),Ye(e,t))}function Ne(e,t,n){if(e.tag===3)qu(e,e,n);else for(;t!==null;){if(t.tag===3){qu(t,e,n);break}else if(t.tag===1){var s=t.stateNode;if(typeof t.type.getDerivedStateFromError=="function"||typeof s.componentDidCatch=="function"&&(Jt===null||!Jt.has(s))){e=Wn(n,e),e=fu(t,e,1),t=qt(t,e,1),e=He(),t!==null&&(tr(t,1,e),Ye(t,e));break}}t=t.return}}function jm(e,t,n){var s=e.pingCache;s!==null&&s.delete(t),t=He(),e.pingedLanes|=e.suspendedLanes&n,Re===e&&(Ie&n)===n&&(Pe===4||Pe===3&&(Ie&130023424)===Ie&&500>be()-Da?vn(e,0):Aa|=n),Ye(e,t)}function Yu(e,t){t===0&&((e.mode&1)===0?t=1:(t=$r,$r<<=1,($r&130023424)===0&&($r=4194304)));var n=He();e=Dt(e,t),e!==null&&(tr(e,t,n),Ye(e,n))}function Sm(e){var t=e.memoizedState,n=0;t!==null&&(n=t.retryLane),Yu(e,n)}function Nm(e,t){var n=0;switch(e.tag){case 13:var s=e.stateNode,i=e.memoizedState;i!==null&&(n=i.retryLane);break;case 19:s=e.stateNode;break;default:throw Error(c(314))}s!==null&&s.delete(t),Yu(e,n)}var Ju;Ju=function(e,t,n){if(e!==null)if(e.memoizedProps!==t.pendingProps||Ke.current)Xe=!0;else{if((e.lanes&n)===0&&(t.flags&128)===0)return Xe=!1,dm(e,t,n);Xe=(e.flags&131072)!==0}else Xe=!1,xe&&(t.flags&1048576)!==0&&Ml(t,ds,t.index);switch(t.lanes=0,t.tag){case 2:var s=t.type;Cs(e,t),e=t.pendingProps;var i=An(t,Fe.current);On(t,n),i=ma(null,t,s,e,i,n);var a=ha();return t.flags|=1,typeof i=="object"&&i!==null&&typeof i.render=="function"&&i.$$typeof===void 0?(t.tag=1,t.memoizedState=null,t.updateQueue=null,Qe(s)?(a=!0,ls(t)):a=!1,t.memoizedState=i.state!==null&&i.state!==void 0?i.state:null,ia(t),i.updater=Ns,t.stateNode=i,i._reactInternals=t,xa(t,s,e,n),t=Sa(null,t,s,!0,a,n)):(t.tag=0,xe&&a&&Xi(t),Ve(null,t,i,n),t=t.child),t;case 16:s=t.elementType;e:{switch(Cs(e,t),e=t.pendingProps,i=s._init,s=i(s._payload),t.type=s,i=t.tag=Cm(s),e=xt(s,e),i){case 0:t=ja(null,t,s,e,n);break e;case 1:t=Nu(null,t,s,e,n);break e;case 11:t=xu(null,t,s,e,n);break e;case 14:t=ku(null,t,s,xt(s.type,e),n);break e}throw Error(c(306,s,""))}return t;case 0:return s=t.type,i=t.pendingProps,i=t.elementType===s?i:xt(s,i),ja(e,t,s,i,n);case 1:return s=t.type,i=t.pendingProps,i=t.elementType===s?i:xt(s,i),Nu(e,t,s,i,n);case 3:e:{if(bu(t),e===null)throw Error(c(387));s=t.pendingProps,a=t.memoizedState,i=a.element,Ol(e,t),vs(t,s,null,n);var l=t.memoizedState;if(s=l.element,a.isDehydrated)if(a={element:s,isDehydrated:!1,cache:l.cache,pendingSuspenseBoundaries:l.pendingSuspenseBoundaries,transitions:l.transitions},t.updateQueue.baseState=a,t.memoizedState=a,t.flags&256){i=Wn(Error(c(423)),t),t=Cu(e,t,s,n,i);break e}else if(s!==i){i=Wn(Error(c(424)),t),t=Cu(e,t,s,n,i);break e}else for(lt=Ht(t.stateNode.containerInfo.firstChild),ot=t,xe=!0,yt=null,n=Fl(t,null,s,n),t.child=n;n;)n.flags=n.flags&-3|4096,n=n.sibling;else{if(zn(),s===i){t=zt(e,t,n);break e}Ve(e,t,s,n)}t=t.child}return t;case 5:return $l(t),e===null&&Ji(t),s=t.type,i=t.pendingProps,a=e!==null?e.memoizedProps:null,l=i.children,$i(s,i)?l=null:a!==null&&$i(s,a)&&(t.flags|=32),Su(e,t),Ve(e,t,l,n),t.child;case 6:return e===null&&Ji(t),null;case 13:return _u(e,t,n);case 4:return aa(t,t.stateNode.containerInfo),s=t.pendingProps,e===null?t.child=Fn(t,null,s,n):Ve(e,t,s,n),t.child;case 11:return s=t.type,i=t.pendingProps,i=t.elementType===s?i:xt(s,i),xu(e,t,s,i,n);case 7:return Ve(e,t,t.pendingProps,n),t.child;case 8:return Ve(e,t,t.pendingProps.children,n),t.child;case 12:return Ve(e,t,t.pendingProps.children,n),t.child;case 10:e:{if(s=t.type._context,i=t.pendingProps,a=t.memoizedProps,l=i.value,fe(ps,s._currentValue),s._currentValue=l,a!==null)if(vt(a.value,l)){if(a.children===i.children&&!Ke.current){t=zt(e,t,n);break e}}else for(a=t.child,a!==null&&(a.return=t);a!==null;){var d=a.dependencies;if(d!==null){l=a.child;for(var m=d.firstContext;m!==null;){if(m.context===s){if(a.tag===1){m=It(-1,n&-n),m.tag=2;var k=a.updateQueue;if(k!==null){k=k.shared;var P=k.pending;P===null?m.next=m:(m.next=P.next,P.next=m),k.pending=m}}a.lanes|=n,m=a.alternate,m!==null&&(m.lanes|=n),ra(a.return,n,t),d.lanes|=n;break}m=m.next}}else if(a.tag===10)l=a.type===t.type?null:a.child;else if(a.tag===18){if(l=a.return,l===null)throw Error(c(341));l.lanes|=n,d=l.alternate,d!==null&&(d.lanes|=n),ra(l,n,t),l=a.sibling}else l=a.child;if(l!==null)l.return=a;else for(l=a;l!==null;){if(l===t){l=null;break}if(a=l.sibling,a!==null){a.return=l.return,l=a;break}l=l.return}a=l}Ve(e,t,i.children,n),t=t.child}return t;case 9:return i=t.type,s=t.pendingProps.children,On(t,n),i=mt(i),s=s(i),t.flags|=1,Ve(e,t,s,n),t.child;case 14:return s=t.type,i=xt(s,t.pendingProps),i=xt(s.type,i),ku(e,t,s,i,n);case 15:return wu(e,t,t.type,t.pendingProps,n);case 17:return s=t.type,i=t.pendingProps,i=t.elementType===s?i:xt(s,i),Cs(e,t),t.tag=1,Qe(s)?(e=!0,ls(t)):e=!1,On(t,n),mu(t,s,i),xa(t,s,i,n),Sa(null,t,s,!0,e,n);case 19:return Tu(e,t,n);case 22:return ju(e,t,n)}throw Error(c(156,t.tag))};function Zu(e,t){return Lo(e,t)}function bm(e,t,n,s){this.tag=e,this.key=n,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=t,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=s,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function ft(e,t,n,s){return new bm(e,t,n,s)}function $a(e){return e=e.prototype,!(!e||!e.isReactComponent)}function Cm(e){if(typeof e=="function")return $a(e)?1:0;if(e!=null){if(e=e.$$typeof,e===ze)return 11;if(e===Nt)return 14}return 2}function nn(e,t){var n=e.alternate;return n===null?(n=ft(e.tag,t,e.key,e.mode),n.elementType=e.elementType,n.type=e.type,n.stateNode=e.stateNode,n.alternate=e,e.alternate=n):(n.pendingProps=t,n.type=e.type,n.flags=0,n.subtreeFlags=0,n.deletions=null),n.flags=e.flags&14680064,n.childLanes=e.childLanes,n.lanes=e.lanes,n.child=e.child,n.memoizedProps=e.memoizedProps,n.memoizedState=e.memoizedState,n.updateQueue=e.updateQueue,t=e.dependencies,n.dependencies=t===null?null:{lanes:t.lanes,firstContext:t.firstContext},n.sibling=e.sibling,n.index=e.index,n.ref=e.ref,n}function zs(e,t,n,s,i,a){var l=2;if(s=e,typeof e=="function")$a(e)&&(l=1);else if(typeof e=="string")l=5;else e:switch(e){case X:return xn(n.children,i,a,t);case me:l=8,i|=8;break;case je:return e=ft(12,n,t,i|2),e.elementType=je,e.lanes=a,e;case $e:return e=ft(13,n,t,i),e.elementType=$e,e.lanes=a,e;case st:return e=ft(19,n,t,i),e.elementType=st,e.lanes=a,e;case Se:return Fs(n,i,a,t);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case rt:l=10;break e;case We:l=9;break e;case ze:l=11;break e;case Nt:l=14;break e;case Ge:l=16,s=null;break e}throw Error(c(130,e==null?e:typeof e,""))}return t=ft(l,n,t,i),t.elementType=e,t.type=s,t.lanes=a,t}function xn(e,t,n,s){return e=ft(7,e,s,t),e.lanes=n,e}function Fs(e,t,n,s){return e=ft(22,e,s,t),e.elementType=Se,e.lanes=n,e.stateNode={isHidden:!1},e}function Va(e,t,n){return e=ft(6,e,null,t),e.lanes=n,e}function Ha(e,t,n){return t=ft(4,e.children!==null?e.children:[],e.key,t),t.lanes=n,t.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},t}function _m(e,t,n,s,i){this.tag=t,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=yi(0),this.expirationTimes=yi(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=yi(0),this.identifierPrefix=s,this.onRecoverableError=i,this.mutableSourceEagerHydrationData=null}function Ga(e,t,n,s,i,a,l,d,m){return e=new _m(e,t,n,d,m),t===1?(t=1,a===!0&&(t|=8)):t=0,a=ft(3,null,null,t),e.current=a,a.stateNode=e,a.memoizedState={element:s,isDehydrated:n,cache:null,transitions:null,pendingSuspenseBoundaries:null},ia(a),e}function Em(e,t,n){var s=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:_,key:s==null?null:""+s,children:e,containerInfo:t,implementation:n}}function ec(e){if(!e)return Kt;e=e._reactInternals;e:{if(on(e)!==e||e.tag!==1)throw Error(c(170));var t=e;do{switch(t.tag){case 3:t=t.stateNode.context;break e;case 1:if(Qe(t.type)){t=t.stateNode.__reactInternalMemoizedMergedChildContext;break e}}t=t.return}while(t!==null);throw Error(c(171))}if(e.tag===1){var n=e.type;if(Qe(n))return El(e,n,t)}return t}function tc(e,t,n,s,i,a,l,d,m){return e=Ga(n,s,!0,e,i,a,l,d,m),e.context=ec(null),n=e.current,s=He(),i=en(n),a=It(s,i),a.callback=t??null,qt(n,a,i),e.current.lanes=i,tr(e,i,s),Ye(e,s),e}function Bs(e,t,n,s){var i=t.current,a=He(),l=en(i);return n=ec(n),t.context===null?t.context=n:t.pendingContext=n,t=It(a,l),t.payload={element:e},s=s===void 0?null:s,s!==null&&(t.callback=s),e=qt(i,t,l),e!==null&&(jt(e,i,l,a),gs(e,i,l)),l}function Os(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function nc(e,t){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var n=e.retryLane;e.retryLane=n!==0&&n<t?n:t}}function Ka(e,t){nc(e,t),(e=e.alternate)&&nc(e,t)}function Tm(){return null}var rc=typeof reportError=="function"?reportError:function(e){console.error(e)};function Qa(e){this._internalRoot=e}Us.prototype.render=Qa.prototype.render=function(e){var t=this._internalRoot;if(t===null)throw Error(c(409));Bs(e,t,null,null)},Us.prototype.unmount=Qa.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var t=e.containerInfo;gn(function(){Bs(null,e,null,null)}),t[Mt]=null}};function Us(e){this._internalRoot=e}Us.prototype.unstable_scheduleHydration=function(e){if(e){var t=Oo();e={blockedOn:null,target:e,priority:t};for(var n=0;n<Wt.length&&t!==0&&t<Wt[n].priority;n++);Wt.splice(n,0,e),n===0&&$o(e)}};function Xa(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function Ws(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function sc(){}function Pm(e,t,n,s,i){if(i){if(typeof s=="function"){var a=s;s=function(){var k=Os(l);a.call(k)}}var l=tc(t,s,e,0,null,!1,!1,"",sc);return e._reactRootContainer=l,e[Mt]=l.current,fr(e.nodeType===8?e.parentNode:e),gn(),l}for(;i=e.lastChild;)e.removeChild(i);if(typeof s=="function"){var d=s;s=function(){var k=Os(m);d.call(k)}}var m=Ga(e,0,!1,null,null,!1,!1,"",sc);return e._reactRootContainer=m,e[Mt]=m.current,fr(e.nodeType===8?e.parentNode:e),gn(function(){Bs(t,m,n,s)}),m}function $s(e,t,n,s,i){var a=n._reactRootContainer;if(a){var l=a;if(typeof i=="function"){var d=i;i=function(){var m=Os(l);d.call(m)}}Bs(t,l,e,i)}else l=Pm(n,t,e,i,s);return Os(l)}Fo=function(e){switch(e.tag){case 3:var t=e.stateNode;if(t.current.memoizedState.isDehydrated){var n=er(t.pendingLanes);n!==0&&(xi(t,n|1),Ye(t,be()),(ae&6)===0&&(Hn=be()+500,Qt()))}break;case 13:gn(function(){var s=Dt(e,1);if(s!==null){var i=He();jt(s,e,1,i)}}),Ka(e,1)}},ki=function(e){if(e.tag===13){var t=Dt(e,134217728);if(t!==null){var n=He();jt(t,e,134217728,n)}Ka(e,134217728)}},Bo=function(e){if(e.tag===13){var t=en(e),n=Dt(e,t);if(n!==null){var s=He();jt(n,e,t,s)}Ka(e,t)}},Oo=function(){return de},Uo=function(e,t){var n=de;try{return de=e,t()}finally{de=n}},mi=function(e,t,n){switch(t){case"input":if(si(e,n),t=n.name,n.type==="radio"&&t!=null){for(n=e;n.parentNode;)n=n.parentNode;for(n=n.querySelectorAll("input[name="+JSON.stringify(""+t)+'][type="radio"]'),t=0;t<n.length;t++){var s=n[t];if(s!==e&&s.form===e.form){var i=as(s);if(!i)throw Error(c(90));co(s),si(s,i)}}}break;case"textarea":go(e,n);break;case"select":t=n.value,t!=null&&jn(e,!!n.multiple,t,!1)}},bo=Oa,Co=gn;var Mm={usingClientEntryPoint:!1,Events:[yr,Ln,as,So,No,Oa]},Lr={findFiberByHostInstance:ln,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},Lm={bundleType:Lr.bundleType,version:Lr.version,rendererPackageName:Lr.rendererPackageName,rendererConfig:Lr.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:te.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=Po(e),e===null?null:e.stateNode},findFiberByHostInstance:Lr.findFiberByHostInstance||Tm,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Vs=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Vs.isDisabled&&Vs.supportsFiber)try{Ur=Vs.inject(Lm),bt=Vs}catch{}}return Je.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Mm,Je.createPortal=function(e,t){var n=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!Xa(t))throw Error(c(200));return Em(e,t,null,n)},Je.createRoot=function(e,t){if(!Xa(e))throw Error(c(299));var n=!1,s="",i=rc;return t!=null&&(t.unstable_strictMode===!0&&(n=!0),t.identifierPrefix!==void 0&&(s=t.identifierPrefix),t.onRecoverableError!==void 0&&(i=t.onRecoverableError)),t=Ga(e,1,!1,null,null,n,!1,s,i),e[Mt]=t.current,fr(e.nodeType===8?e.parentNode:e),new Qa(t)},Je.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var t=e._reactInternals;if(t===void 0)throw typeof e.render=="function"?Error(c(188)):(e=Object.keys(e).join(","),Error(c(268,e)));return e=Po(t),e=e===null?null:e.stateNode,e},Je.flushSync=function(e){return gn(e)},Je.hydrate=function(e,t,n){if(!Ws(t))throw Error(c(200));return $s(null,e,t,!0,n)},Je.hydrateRoot=function(e,t,n){if(!Xa(e))throw Error(c(405));var s=n!=null&&n.hydratedSources||null,i=!1,a="",l=rc;if(n!=null&&(n.unstable_strictMode===!0&&(i=!0),n.identifierPrefix!==void 0&&(a=n.identifierPrefix),n.onRecoverableError!==void 0&&(l=n.onRecoverableError)),t=tc(t,null,e,1,n??null,i,!1,a,l),e[Mt]=t.current,fr(e),s)for(e=0;e<s.length;e++)n=s[e],i=n._getVersion,i=i(n._source),t.mutableSourceEagerHydrationData==null?t.mutableSourceEagerHydrationData=[n,i]:t.mutableSourceEagerHydrationData.push(n,i);return new Us(t)},Je.render=function(e,t,n){if(!Ws(t))throw Error(c(200));return $s(null,e,t,!1,n)},Je.unmountComponentAtNode=function(e){if(!Ws(e))throw Error(c(40));return e._reactRootContainer?(gn(function(){$s(null,null,e,!1,function(){e._reactRootContainer=null,e[Mt]=null})}),!0):!1},Je.unstable_batchedUpdates=Oa,Je.unstable_renderSubtreeIntoContainer=function(e,t,n,s){if(!Ws(n))throw Error(c(200));if(e==null||e._reactInternals===void 0)throw Error(c(38));return $s(e,t,n,!1,s)},Je.version="18.3.1-next-f1338f8080-20240426",Je}var hc;function Wm(){if(hc)return Ja.exports;hc=1;function o(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(o)}catch(u){console.error(u)}}return o(),Ja.exports=Um(),Ja.exports}var pc;function $m(){if(pc)return Hs;pc=1;var o=Wm();return Hs.createRoot=o.createRoot,Hs.hydrateRoot=o.hydrateRoot,Hs}var Vm=$m();class Hm extends Error{constructor(c,f){super(c);ic(this,"status");this.status=f}}async function tt(o,u){const c=await fetch(o,{...u,credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json",...u==null?void 0:u.headers}}),f=await c.json().catch(()=>({}));if(!c.ok)throw new Hm(f.error||c.statusText||"Request failed",c.status);return f}const Gm=()=>tt("/auth/status"),Km=()=>tt("/api/config"),Pc=()=>tt("/api/botstats"),Qm=()=>tt("/api/commands"),Xm=()=>tt("/api/guilds"),qm=()=>tt("/api/me/overview"),Ym=o=>tt(`/api/guild/${o}/overview`),Jm=o=>tt(`/api/guild/${o}/levels`),fc=o=>tt(`/api/guild/${o}/config`),gc=o=>tt(`/api/guild/${o}/resources`);function Js(o,u,c,f){return tt(`/api/guild/${o}/config/${u}`,{method:"POST",headers:f?{"X-CSRF-Token":f}:void 0,body:JSON.stringify(c)})}function Zm(o,u,c){return tt(`/api/guild/${o}/config/profile`,{method:"POST",headers:c?{"X-CSRF-Token":c}:void 0,body:JSON.stringify(u)})}function Mc(o){return o.replace(/\/+$/,"")||"/"}function vc(o=window.location.pathname){const u=Mc(o);return u==="/commands"?"commands":u==="/docs"?"docs":u.startsWith("/docs/")?"docs-detail":u==="/dashboard"||u.startsWith("/dashboard/")?"dashboard":u==="/privacy"?"privacy":u==="/terms"?"terms":u==="/donate"||u.startsWith("/donate")?"donate":u==="/transcript"||u.startsWith("/transcript/")?"transcript":"home"}function Ar(o,u="overview"){return o?`/dashboard/${o}/${u}`:"/dashboard"}function yc(){return"/dashboard/servers"}function xc(){const o=Mc(window.location.pathname).split("/").filter(Boolean),u=["overview","leveling","moderation","server","ai","customization"];return o[1]==="servers"?{view:"servers",guildId:null,section:"overview"}:o[1]?{view:"guild",guildId:o[1]||null,section:u.includes(o[2])?o[2]:"overview"}:{view:"overview",guildId:null,section:"overview"}}function he(o){o.startsWith("/")&&(window.history.pushState({},"",o),window.dispatchEvent(new PopStateEvent("popstate")),window.scrollTo({top:0,behavior:"smooth"}))}function qs({onNavigate:o}){return r.jsxs("a",{className:"brand",href:"/",onClick:u=>{u.preventDefault(),o?o():he("/")},children:[r.jsx("span",{className:"brand-mark",children:"n"}),r.jsx("span",{children:"niko"})]})}function Kn(){return r.jsxs("footer",{className:"site-footer",children:[r.jsx(qs,{}),r.jsx("span",{children:"Built for communities that care."}),r.jsxs("div",{children:[r.jsx("a",{href:"/privacy",onClick:o=>{o.preventDefault(),he("/privacy")},children:"Privacy"}),r.jsx("a",{href:"/terms",onClick:o=>{o.preventDefault(),he("/terms")},children:"Terms"}),r.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"GitHub"})]})]})}/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Lc=(...o)=>o.filter((u,c,f)=>!!u&&u.trim()!==""&&f.indexOf(u)===c).join(" ").trim();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const eh=o=>o.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const th=o=>o.replace(/^([A-Z])|[\s-_]+(\w)/g,(u,c,f)=>f?f.toUpperCase():c.toLowerCase());/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kc=o=>{const u=th(o);return u.charAt(0).toUpperCase()+u.slice(1)};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var to={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const nh=o=>{for(const u in o)if(u.startsWith("aria-")||u==="role"||u==="title")return!0;return!1},rh=R.createContext({}),sh=()=>R.useContext(rh),ih=R.forwardRef(({color:o,size:u,strokeWidth:c,absoluteStrokeWidth:f,className:p="",children:S,iconNode:w,...z},x)=>{const{size:B=24,strokeWidth:b=2,absoluteStrokeWidth:C=!1,color:M="currentColor",className:D=""}=sh()??{},I=f??C?Number(c??b)*24/Number(u??B):c??b;return R.createElement("svg",{ref:x,...to,width:u??B??to.width,height:u??B??to.height,stroke:o??M,strokeWidth:I,className:Lc("lucide",D,p),...!S&&!nh(z)&&{"aria-hidden":"true"},...z},[...w.map(([F,j])=>R.createElement(F,j)),...Array.isArray(S)?S:[S]])});/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const nt=(o,u)=>{const c=R.forwardRef(({className:f,...p},S)=>R.createElement(ih,{ref:S,iconNode:u,className:Lc(`lucide-${eh(kc(o))}`,`lucide-${o}`,f),...p}));return c.displayName=kc(o),c};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ah=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]],oh=nt("arrow-right",ah);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const lh=[["path",{d:"M12 5v16",key:"1f6ucr"}],["path",{d:"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z",key:"1fyvmf"}]],wc=nt("book-open",lh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const uh=[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],no=nt("chart-column",uh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ch=[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]],dh=nt("external-link",ch);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const mh=[["rect",{width:"7",height:"7",x:"3",y:"3",rx:"1",key:"1g98yp"}],["rect",{width:"7",height:"7",x:"14",y:"3",rx:"1",key:"6d4xhi"}],["rect",{width:"7",height:"7",x:"14",y:"14",rx:"1",key:"nxv5o0"}],["rect",{width:"7",height:"7",x:"3",y:"14",rx:"1",key:"1bb6yr"}]],ao=nt("layout-grid",mh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const hh=[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]],ph=nt("lock-keyhole",hh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const fh=[["path",{d:"M4 5h16",key:"1tepv9"}],["path",{d:"M4 12h16",key:"1lakjw"}],["path",{d:"M4 19h16",key:"1djgab"}]],gh=nt("menu",fh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const vh=[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]],yh=nt("search",vh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const xh=[["path",{d:"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915",key:"1i5ecw"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]],Gs=nt("settings",xh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kh=[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}]],ro=nt("shield",kh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const wh=[["path",{d:"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",key:"1s2grr"}],["path",{d:"M20 2v4",key:"1rf3ol"}],["path",{d:"M22 4h-4",key:"gwowj6"}],["circle",{cx:"4",cy:"20",r:"2",key:"6kqj1y"}]],Ks=nt("sparkles",wh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jh=[["path",{d:"M12 19h8",key:"baeox8"}],["path",{d:"m4 17 6-6-6-6",key:"1yngyt"}]],Sh=nt("terminal",jh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Nh=[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["path",{d:"M16 3.128a4 4 0 0 1 0 7.744",key:"16gr8j"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}]],jc=nt("users",Nh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const bh=[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]],Ch=nt("x",bh),_h={arrow:oh,grid:ao,terminal:Sh,chart:no,shield:ro,spark:Ks,users:jc,settings:Gs,book:wc,external:dh,menu:gh,close:Ch,lock:ph,search:yh,doc:wc,utility:Gs,icon_home:ao,icon_settings:Gs,icon_economy:no,icon_leveling:no,icon_moderation:ro,icon_automod:ro,icon_heart:Ks,icon_utility:Gs,icon_bot:jc,icon_ai:Ks,icon_lightbulb:Ks};function Z({name:o,size:u,className:c=""}){const f=_h[o]||ao;return r.jsx(f,{className:`icon ${c}`.trim(),"aria-hidden":"true",focusable:"false",strokeWidth:1.8,style:u?{width:u,height:u}:void 0})}let Sc=null,so=null;function Zs(){const[o,u]=R.useState(Sc);return R.useEffect(()=>{so||(so=Km().then(c=>Sc=c)),so.then(u).catch(()=>{})},[]),o}function St({page:o}){const u=Zs();return r.jsxs("header",{className:"site-header",children:[r.jsx(qs,{}),r.jsxs("nav",{className:"site-nav","aria-label":"Main navigation",children:[r.jsx("a",{className:o==="home"?"active":"","aria-current":o==="home"?"page":void 0,href:"/",onClick:c=>{c.preventDefault(),he("/")},children:"Home"}),r.jsx("a",{className:o==="commands"?"active":"","aria-current":o==="commands"?"page":void 0,href:"/commands",onClick:c=>{c.preventDefault(),he("/commands")},children:"Commands"}),r.jsx("a",{className:o==="docs"?"active":"","aria-current":o==="docs"?"page":void 0,href:"/docs",onClick:c=>{c.preventDefault(),he("/docs")},children:"Docs"})]}),r.jsxs("div",{className:"header-actions",children:[r.jsxs("a",{className:"button button-small button-muted dashboard-link",href:"/dashboard",onClick:c=>{c.preventDefault(),he("/dashboard")},children:["Dashboard ",r.jsx(Z,{name:"arrow"})]}),r.jsx("a",{className:"button button-small button-primary",href:(u==null?void 0:u.invite_url)||"#",target:"_blank",rel:"noreferrer",children:"Add to Discord"})]})]})}const Eh=[{value:"all",label:"All commands"},{value:"slash",label:"Slash"},{value:"prefix",label:"Prefix"},{value:"hybrid",label:"Hybrid"},{value:"context",label:"Context menus"}],Ys={slash:"Slash command",prefix:"Prefix command",hybrid:"Hybrid command",context:"Context menu"};function kn(o){return o.type&&o.type in Ys?o.type:"slash"}function Th(o){return o.context_type==="user"?"Right-click a user":"Right-click a message"}function Rc(o){const u=kn(o);return u==="slash"?r.jsxs("code",{children:["/",o.name]}):u==="prefix"?r.jsxs("code",{children:[".",o.name]}):u==="hybrid"?r.jsxs(r.Fragment,{children:[r.jsxs("code",{children:["/",o.name]}),r.jsx("span",{className:"command-or",children:"or"}),r.jsxs("code",{children:[".",o.name]})]}):r.jsxs("code",{className:"context-invocation",children:[Th(o)," · ",o.name]})}function Nc(o){return o!=null&&o.length?o:["Not specified"]}function Ph({command:o,onClose:u}){R.useEffect(()=>{const w=z=>{z.key==="Escape"&&u()};return document.addEventListener("keydown",w),()=>document.removeEventListener("keydown",w)},[u]);const c=o.parameters||[],f=o.subcommands||[],p=Nc(o.aliases),S=Nc(o.permissions);return r.jsx("div",{className:"command-dialog-backdrop",role:"presentation",onMouseDown:w=>{w.currentTarget===w.target&&u()},children:r.jsxs("section",{className:"command-dialog",role:"dialog","aria-modal":"true","aria-labelledby":"command-dialog-title",children:[r.jsxs("header",{className:"command-dialog-header",children:[r.jsxs("div",{children:[r.jsxs("div",{className:"command-dialog-kicker",children:[o.category," · ",Ys[kn(o)]]}),r.jsx("h2",{id:"command-dialog-title",children:Rc(o)})]}),r.jsx("button",{className:"dialog-close",type:"button",onClick:u,"aria-label":"Close command details",title:"Close command details",children:r.jsx(Z,{name:"close"})})]}),r.jsxs("div",{className:"command-dialog-body",children:[r.jsx("p",{className:"command-dialog-description",children:o.description||"A Niko command for your server."}),r.jsxs("div",{className:"command-detail-grid",children:[r.jsxs("section",{className:"command-detail-section command-detail-wide",children:[r.jsx("h3",{children:"Usage"}),r.jsx("code",{className:"command-usage",children:o.usage||`${kn(o)==="context"?o.name:`/${o.name}`}`})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Permissions"}),r.jsx("ul",{className:"command-detail-list",children:S.map(w=>r.jsx("li",{children:w},w))})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Aliases"}),r.jsx("ul",{className:"command-detail-list",children:p.map(w=>r.jsx("li",{children:r.jsx("code",{children:w==="Not specified"?w:`.${w}`})},w))})]})]}),!!c.length&&r.jsxs("section",{className:"command-detail-section command-parameters",children:[r.jsx("h3",{children:"Parameters"}),r.jsx("div",{className:"command-parameter-list",children:c.map(w=>r.jsxs("div",{className:"command-parameter",children:[r.jsxs("div",{className:"command-parameter-title",children:[r.jsx("code",{children:w.name}),r.jsxs("span",{children:[w.required?"Required":"Optional"," · ",w.type]})]}),r.jsx("p",{children:w.description||"No description provided."})]},w.name))})]}),!!f.length&&r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Subcommands"}),r.jsx("div",{className:"subcommand-list",children:f.map(w=>r.jsxs("code",{children:[o.name," ",w]},w))})]})]}),r.jsxs("footer",{className:"command-dialog-footer",children:[r.jsx("span",{children:"Command registry details are generated from the live bot."}),r.jsx("button",{className:"button button-primary button-small",type:"button",onClick:u,children:"Done"})]})]})})}function Mh(){const[o,u]=R.useState([]),[c,f]=R.useState(null),[p,S]=R.useState(""),[w,z]=R.useState("all"),[x,B]=R.useState("all"),[b,C]=R.useState(!0),[M,D]=R.useState("");R.useEffect(()=>{Qm().then(u).catch(()=>D("The command registry is unavailable right now.")).finally(()=>C(!1))},[]),R.useEffect(()=>{if(!c)return;const j=document.body.style.overflow;return document.body.style.overflow="hidden",()=>{document.body.style.overflow=j}},[c]);const I=R.useMemo(()=>["all",...Array.from(new Set(o.map(j=>j.category))).sort()],[o]),F=o.filter(j=>{const W=`${j.name} ${j.description} ${j.category} ${Ys[kn(j)]} ${j.context_type||""} ${(j.aliases||[]).join(" ")}`.toLowerCase();return(x==="all"||kn(j)===x)&&(w==="all"||j.category===w)&&W.includes(p.trim().toLowerCase())});return r.jsxs(r.Fragment,{children:[r.jsx(St,{page:"commands"}),r.jsxs("main",{className:"shell page-main",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Reference library"}),r.jsxs("h1",{children:["Everything Niko",r.jsx("br",{}),r.jsx("em",{children:"knows how to do."})]}),r.jsx("p",{children:"Browse slash, prefix, hybrid, and context commands from the live bot registry. Select any command for permissions, aliases, parameters, usage, and subcommands."})]}),r.jsxs("div",{className:"command-toolbar",children:[r.jsxs("label",{className:"search-field",children:[r.jsx("span",{"aria-hidden":"true",children:"⌕"}),r.jsx("input",{value:p,onChange:j=>S(j.target.value),placeholder:"Search commands","aria-label":"Search commands"})]}),r.jsxs("div",{className:"command-filters",children:[r.jsx("div",{className:"filter-list","aria-label":"Command types",children:Eh.map(j=>r.jsx("button",{type:"button",className:x===j.value?"filter active":"filter","aria-pressed":x===j.value,onClick:()=>B(j.value),children:j.label},j.value))}),r.jsx("div",{className:"filter-list","aria-label":"Command categories",children:I.map(j=>r.jsx("button",{type:"button",className:w===j?"filter active":"filter","aria-pressed":w===j,onClick:()=>z(j),children:j==="all"?"All categories":j},j))})]})]}),r.jsxs("div",{className:"command-meta",children:[r.jsx("strong",{children:b?"…":F.length})," commands ",r.jsx("span",{children:"·"})," live bot registry ",r.jsx("span",{children:"·"})," select a card for details"]}),M&&r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Could not load commands"}),r.jsx("span",{children:M})]}),r.jsxs("div",{className:"commands-grid",children:[F.map(j=>r.jsxs("button",{className:"command-card",type:"button",onClick:()=>f(j),"aria-label":`View details for ${j.name}`,children:[r.jsxs("span",{className:"command-card-head",children:[r.jsx("span",{className:"command-name",children:Rc(j)}),r.jsx("span",{className:"command-type",children:Ys[kn(j)]})]}),r.jsx("span",{className:"command-card-description",children:j.description||"A Niko command for your server."}),r.jsxs("span",{className:"command-card-footer",children:[r.jsx("span",{className:"category-tag",children:j.category}),r.jsxs("span",{className:"command-expand",children:[r.jsx("span",{children:"Details"}),r.jsx(Z,{name:"arrow",size:14})]})]})]},`${kn(j)}-${j.context_type||""}-${j.category}-${j.name}`)),!b&&!M&&!F.length&&r.jsx("div",{className:"empty-state",children:"No commands match that search."})]})]}),r.jsx(Kn,{}),c&&r.jsx(Ph,{command:c,onClose:()=>f(null)})]})}function Ee(o){return o==null?"—":new Intl.NumberFormat("en-US",{notation:o>9999?"compact":"standard"}).format(o)}function oo(o){return(o==null?void 0:o.global_name)||(o==null?void 0:o.username)||"there"}function Ac(o){return o.split(/\s+/).map(u=>u[0]).join("").slice(0,2).toUpperCase()}function uo({guild:o,className:u="guild-avatar"}){return r.jsx("span",{className:u,"aria-hidden":"true",children:o.icon_url?r.jsx("img",{src:o.icon_url,alt:""}):o.name.slice(0,1).toUpperCase()})}function Dc({user:o,className:u="avatar"}){const c=o.avatar?`https://cdn.discordapp.com/avatars/${o.id}/${o.avatar}.${o.avatar.startsWith("a_")?"gif":"png"}?size=64`:null;return r.jsx("span",{className:u,"aria-hidden":"true",children:c?r.jsx("img",{src:c,alt:""}):Ac(o.global_name||o.username||"Niko")})}function Lh({name:o,avatarUrl:u,className:c="member-avatar"}){return r.jsx("span",{className:c,"aria-hidden":"true",children:u?r.jsx("img",{src:u,alt:""}):Ac(o)})}const bc=[["overview","Overview","grid","At a glance"],["leveling","Leveling","spark","Reward participation"],["moderation","Moderation","shield","Keep things steady"],["server","Server","settings","Manage server features"],["ai","AI controls","settings","Shape Niko’s voice"],["customization","Customization","paint","Niko’s server identity"]];function Rh({user:o,guilds:u,selectedGuild:c,view:f,section:p,stats:S,onHome:w,onServers:z,onGuildChange:x,onSectionChange:B,children:b}){var j;const C=u.filter(W=>W.installed!==!1),M=(W=!1)=>r.jsx("nav",{className:W?"dash-nav dash-nav-mobile":"dash-nav","aria-label":"Server settings",children:bc.map(([N,Q,te])=>r.jsxs("button",{className:f==="guild"&&p===N?"active":"","aria-current":f==="guild"&&p===N?"page":void 0,onClick:()=>B(N),children:[r.jsx(Z,{name:te}),r.jsx("span",{children:Q})]},N))}),D=(W=!1)=>r.jsxs("nav",{className:W?"dash-nav dash-primary-nav dash-nav-mobile":"dash-nav dash-primary-nav","aria-label":"Dashboard",children:[r.jsxs("button",{className:f==="overview"?"active":"","aria-current":f==="overview"?"page":void 0,onClick:w,children:[r.jsx(Z,{name:"grid"}),r.jsx("span",{children:"My overview"})]}),r.jsxs("button",{className:f==="servers"?"active":"","aria-current":f==="servers"?"page":void 0,onClick:z,children:[r.jsx(Z,{name:"users"}),r.jsx("span",{children:"My servers"})]})]}),I=f==="overview"?`Welcome, ${oo(o)}`:f==="servers"?"Your servers":(c==null?void 0:c.name)||"Server settings",F=f==="guild"?"Managing server":"Niko dashboard";return r.jsxs("div",{className:"dashboard-layout",children:[r.jsxs("aside",{className:"dash-sidebar",children:[r.jsx(qs,{onNavigate:w}),r.jsxs("div",{className:"side-rail-heading",children:[r.jsx("span",{className:"side-label",children:"Workspace"}),r.jsxs("span",{className:"rail-status",children:[r.jsx("span",{className:"status-dot"})," Live"]})]}),D(),f==="guild"&&c&&r.jsxs(r.Fragment,{children:[r.jsx("div",{className:"side-label side-label-settings",children:"Current server"}),r.jsxs("div",{className:"side-guild",children:[r.jsx(uo,{guild:c}),r.jsxs("span",{children:[r.jsx("strong",{children:c.name}),r.jsx("small",{children:"Live configuration"})]}),r.jsx("span",{className:"guild-presence",title:"Niko is connected",children:r.jsx("span",{className:"status-dot"})})]}),r.jsxs("div",{className:"side-settings-caption",children:[r.jsx("span",{children:"Settings map"}),r.jsx("small",{children:"Pick a room to tune"})]}),M()]}),f!=="guild"&&r.jsxs("div",{className:"side-rail-note",children:[r.jsx("span",{className:"panel-kicker",children:"Niko workspace"}),r.jsxs("strong",{children:["Make the useful",r.jsx("br",{}),"things easier to find."]}),r.jsx("small",{children:"Your servers and their live signals, in one quiet place."})]}),r.jsxs("div",{className:"sidebar-bottom",children:[r.jsxs("span",{className:"online-label",children:[r.jsx("span",{className:"status-dot"})," Niko is online"]}),r.jsxs("small",{children:[Ee(S==null?void 0:S.guild_count)," connected servers · v",(S==null?void 0:S.version)||"1.0"]}),r.jsxs("a",{href:"/",onClick:W=>{W.preventDefault(),he("/")},children:["Back to public site ",r.jsx(Z,{name:"arrow"})]})]})]}),r.jsxs("div",{className:"dash-content",children:[r.jsxs("header",{className:"dash-topbar",children:[r.jsxs("div",{className:"mobile-top-row",children:[r.jsx("span",{className:"mobile-brand",children:r.jsx(qs,{})}),r.jsxs("span",{className:"mobile-status",children:[r.jsx("span",{className:"status-dot"})," Online"]})]}),r.jsxs("div",{className:"dash-title",children:[r.jsxs("span",{className:"dash-overline",children:[F," ",r.jsx("span",{className:"dash-title-divider",children:"/"})," ",f==="guild"?(j=bc.find(([W])=>W===p))==null?void 0:j[1]:"Workspace"]}),r.jsx("h1",{children:I})]}),r.jsxs("div",{className:"dash-top-actions",children:[f==="guild"?r.jsxs("label",{className:"guild-switcher",children:[r.jsx("span",{className:"sr-only",children:"Switch server"}),r.jsxs("select",{value:(c==null?void 0:c.id)||"",onChange:W=>{const N=C.find(Q=>Q.id===W.target.value);N&&x(N)},children:[r.jsx("option",{value:"",disabled:!0,children:"Switch server"}),C.map(W=>r.jsx("option",{value:W.id,children:W.name},W.id))]})]}):r.jsxs("button",{className:"button button-muted button-small top-action",onClick:z,children:[r.jsx(Z,{name:"users"})," Browse servers"]}),f==="guild"&&r.jsxs("span",{className:"connection-chip",children:[r.jsx("span",{className:"status-dot"})," Connected"]}),r.jsxs("div",{className:"user-pill",children:[r.jsx(Dc,{user:o}),r.jsx("span",{children:oo(o)})]}),r.jsx("a",{className:"logout-link",href:"/auth/logout",children:"Log out"})]})]}),r.jsx("div",{className:"mobile-primary-bar",children:D(!0)}),f==="guild"&&r.jsx("div",{className:"mobile-section-bar",children:M(!0)}),r.jsx("main",{className:"dash-main",children:b})]})]})}function an({eyebrow:o,title:u,text:c}){return r.jsxs("div",{className:"dash-heading",children:[r.jsxs("div",{className:"heading-meta",children:[r.jsx("div",{className:"eyebrow",children:o}),r.jsx("span",{className:"heading-context",children:"NIKO / CONTROL ROOM"})]}),r.jsx("h2",{children:u}),r.jsx("p",{children:c})]})}function Pt({label:o,value:u,note:c,accent:f=""}){return r.jsxs("div",{className:`dash-stat ${f}`,children:[r.jsx("span",{children:o}),r.jsx("strong",{children:u}),r.jsx("small",{children:c})]})}function Ah({user:o,overview:u,guilds:c,onServers:f,onManage:p}){const S=c.filter(w=>w.installed!==!1);return r.jsxs(r.Fragment,{children:[r.jsx(an,{eyebrow:"Personal overview",title:"Your Niko snapshot.",text:"Keep an eye on your progress, then jump into a server when you’re ready to tune the room."}),r.jsxs("div",{className:"overview-intro",children:[r.jsxs("div",{className:"profile-card",children:[r.jsx(Dc,{user:o,className:"profile-avatar"}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Signed in as"}),r.jsx("h3",{children:oo(o)}),r.jsx("p",{children:"Personal economy profile"})]})]}),r.jsxs("button",{className:"button button-primary",onClick:f,children:["Manage a server ",r.jsx(Z,{name:"arrow"})]})]}),r.jsxs("div",{className:"dash-stats overview-stats",children:[r.jsx(Pt,{label:"Net worth",value:Ee(u==null?void 0:u.net_worth),note:"Across your Niko profile",accent:"accent-orange"}),r.jsx(Pt,{label:"In your wallet",value:Ee(u==null?void 0:u.balance),note:"Ready to spend",accent:"accent-violet"}),r.jsx(Pt,{label:"In your vault",value:Ee(u==null?void 0:u.bank),note:"Saved for later",accent:"accent-blue"}),r.jsx(Pt,{label:"Current level",value:Ee(u==null?void 0:u.level),note:u!=null&&u.job?`Working as a ${u.job}`:"Keep showing up",accent:"accent-green"})]}),r.jsxs("div",{className:"dash-columns overview-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Progress"}),r.jsx("h3",{children:"Your momentum"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(Z,{name:"spark"})})]}),r.jsxs("div",{className:"metric-list",children:[r.jsxs("div",{children:[r.jsx("span",{children:"Daily streak"}),r.jsxs("strong",{children:[Ee(u==null?void 0:u.daily_streak)," ",r.jsx("small",{children:"days"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Achievements"}),r.jsxs("strong",{children:[Ee(u==null?void 0:u.achievements)," ",r.jsx("small",{children:"unlocked"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Total earned"}),r.jsxs("strong",{children:[Ee(u==null?void 0:u.total_earned)," ",r.jsx("small",{children:"coins"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Economy standing"}),r.jsxs("strong",{children:[u!=null&&u.economy_rank?`#${Ee(u.economy_rank)}`:"—"," ",r.jsx("small",{children:u!=null&&u.economy_profiles?`of ${Ee(u.economy_profiles)}`:""})]})]})]})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Quick access"}),r.jsx("h3",{children:"Your servers"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(Z,{name:"users"})})]}),r.jsxs("div",{className:"mini-server-list",children:[S.slice(0,4).map(w=>r.jsxs("button",{onClick:()=>p(w),children:[r.jsx(uo,{guild:w}),r.jsx("span",{children:w.name}),r.jsx(Z,{name:"arrow"})]},w.id)),!S.length&&r.jsx("p",{className:"empty-state compact",children:"Add Niko to a server to start managing it."})]}),r.jsxs("button",{className:"text-link overview-link",onClick:f,children:["View all servers ",r.jsx(Z,{name:"arrow"})]})]})]})]})}function Cc({guild:o,onManage:u}){const c=o.installed!==!1;return r.jsxs("article",{className:"server-card",children:[r.jsxs("div",{className:"server-card-heading",children:[r.jsx(uo,{guild:o,className:"server-avatar"}),r.jsx("span",{className:"server-status",children:c?"Niko is installed":"Ready to add"})]}),r.jsx("h3",{children:o.name}),r.jsx("p",{children:c?"Open the dashboard to manage Niko’s features and settings.":"You have permission to manage this server. Add Niko to unlock its controls."}),c?r.jsxs("button",{className:"button button-muted button-small",onClick:()=>u(o),children:["Open settings ",r.jsx(Z,{name:"arrow"})]}):r.jsxs("a",{className:"button button-primary button-small",href:o.invite_url||"#",target:"_blank",rel:"noreferrer",children:["Add Niko ",r.jsx(Z,{name:"external"})]})]})}function Dh({guilds:o,onManage:u}){const c=o.filter(p=>p.installed!==!1),f=o.filter(p=>p.installed===!1);return r.jsxs(r.Fragment,{children:[r.jsx(an,{eyebrow:"Servers",title:"Choose where to work.",text:"Manage servers with Niko already installed, or add Niko to another server you can administer."}),r.jsxs("div",{className:"server-summary",children:[r.jsxs("div",{children:[r.jsx("strong",{children:Ee(c.length)}),r.jsx("span",{children:"Connected to Niko"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:Ee(f.length)}),r.jsx("span",{children:"Ready to add"})]}),r.jsxs("div",{className:"server-summary-note",children:[r.jsx(Z,{name:"shield"}),r.jsx("span",{children:"Only servers where you have Manage Server access are shown."})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Connected"}),r.jsx("h3",{children:"Manage a server"})]}),r.jsx("span",{className:"section-count",children:c.length})]}),r.jsxs("div",{className:"server-grid",children:[c.map(p=>r.jsx(Cc,{guild:p,onManage:u},p.id)),!c.length&&r.jsxs("div",{className:"empty-state",children:[r.jsx("strong",{children:"No connected servers yet."}),r.jsx("span",{children:"Add Niko below, then come back here to manage it."})]})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Available to you"}),r.jsx("h3",{children:"Add Niko to a server"})]}),r.jsx("span",{className:"section-count",children:f.length})]}),r.jsxs("div",{className:"server-grid",children:[f.map(p=>r.jsx(Cc,{guild:p,onManage:u},p.id)),!f.length&&r.jsx("div",{className:"server-note",children:"Niko is already installed in every server you can manage."})]})]})]})}function Ic({rows:o}){return r.jsxs("div",{className:"rank-list",children:[o.slice(0,5).map((u,c)=>r.jsxs("div",{className:"rank-row",children:[r.jsx("span",{className:`rank rank-${c+1}`,children:String(c+1).padStart(2,"0")}),r.jsxs("span",{className:"rank-user",children:[r.jsx(Lh,{name:u.display_name||u.username||"Unknown member",avatarUrl:u.avatar_url}),r.jsxs("span",{children:[r.jsx("strong",{children:u.display_name||u.username||"Unknown member"}),u.username&&u.display_name&&r.jsxs("small",{children:["@",u.username]})]})]}),r.jsxs("strong",{children:[Ee(u.xp),r.jsx("small",{children:" xp"})]})]},`${u.user_id}-${c}`)),!o.length&&r.jsx("div",{className:"empty-state compact",children:"No data recorded yet."})]})}function Ih({overview:o}){return r.jsxs(r.Fragment,{children:[r.jsxs("div",{className:"guild-welcome",children:[r.jsxs("div",{children:[r.jsx("span",{className:"welcome-mark",children:r.jsx(Z,{name:"grid"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server pulse"}),r.jsx("strong",{children:"Here’s what needs your attention."})]})]}),r.jsxs("span",{className:"welcome-time",children:["LIVE SIGNALS ",r.jsx("span",{className:"status-dot"})]})]}),r.jsx(an,{eyebrow:"Overview",title:"A quick read on your room.",text:"The important signals, without making you hunt for them."}),r.jsxs("div",{className:"dash-stats guild-overview-stats",children:[r.jsx(Pt,{label:"Warnings logged",value:Ee(o.moderation.warn_count),note:"For this server",accent:"accent-blue"}),r.jsx(Pt,{label:"Automod",value:o.moderation.automod_active?"Active":"Quiet",note:"Protection status",accent:"accent-green"}),r.jsx(Pt,{label:"Level leaders",value:Ee(o.leveling.top.length),note:"Members with recorded XP",accent:"accent-violet"})]}),r.jsxs("div",{className:"dash-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Community energy"}),r.jsx("h3",{children:"Top XP"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(Z,{name:"spark"})})]}),r.jsx(Ic,{rows:o.leveling.top})]}),r.jsx("section",{className:"dash-panel",children:r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server controls"}),r.jsx("h3",{children:"Manage the room"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(Z,{name:"settings"})}),r.jsx("p",{children:"Use Server settings for prefixes, welcome messages, logs, and ticket panels."})]})})]})]})}function zh({rows:o,config:u,resources:c,csrfToken:f,guildId:p}){var S,w,z;return r.jsxs(r.Fragment,{children:[r.jsx(an,{eyebrow:"Leveling",title:"Momentum people can see.",text:"Track the members turning up, and tune the pace to fit your server."}),r.jsxs("div",{className:"dash-stats",children:[r.jsx(Pt,{label:"Top level",value:String(((S=o[0])==null?void 0:S.level)||0),note:((w=o[0])==null?void 0:w.display_name)||((z=o[0])==null?void 0:z.username)||"No members yet",accent:"accent-violet"}),r.jsx(Pt,{label:"XP multiplier",value:`${(u==null?void 0:u.leveling.xp_multiplier)||1}×`,note:(u==null?void 0:u.leveling.xp_enabled)===!1?"XP disabled":"Currently active",accent:"accent-blue"}),r.jsx(Pt,{label:"Cooldown",value:`${(u==null?void 0:u.leveling.xp_cooldown)||0}s`,note:"Between XP awards",accent:"accent-green"})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Leaderboard"}),r.jsx("h3",{children:"XP leaders"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(Z,{name:"spark"})})]}),r.jsx(Ic,{rows:o})]}),r.jsx(Uh,{guildId:p,config:u,resources:c,csrfToken:f})]})}const ei={saving:!1,message:"",error:""};function et({label:o,hint:u,children:c}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:o}),c,u&&r.jsx("small",{children:u})]})}function Fh(o,u){const c=u?String(u):"",f=(o==null?void 0:o.channels)||[];return!c||f.some(p=>p.id===c)?f:[{id:c,name:`Unavailable channel (${c})`},...f]}function ti({icon:o,label:u,title:c,text:f}){return r.jsxs("div",{className:"settings-intro",children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(Z,{name:o})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:u}),r.jsx("strong",{children:c}),r.jsx("p",{children:f})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]})}function wn({label:o,title:u,detail:c,icon:f}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:o}),r.jsx("h3",{children:u}),c&&r.jsx("p",{children:c})]}),f&&r.jsx("span",{className:"panel-icon",children:r.jsx(Z,{name:f})})]})}function ni({state:o}){return r.jsxs("div",{className:"setting-footer",children:[o.error?r.jsx("span",{className:"form-error",role:"alert",children:o.error}):r.jsx("span",{role:"status",children:o.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:o.saving,children:o.saving?"Saving…":"Save changes"})]})}function Bh({guildId:o,config:u,csrfToken:c}){var C,M,D;const[f,p]=R.useState({}),[S,w]=R.useState(ei);R.useEffect(()=>{const I=(u==null?void 0:u.moderation)||{};p({automod:{...I.automod||{}},spam_threshold:I.spam_threshold??6,spam_interval:I.spam_interval??7,max_mentions:I.max_mentions??5,antinuke:{...I.antinuke||{}},antiraid:{...I.antiraid||{}},antiraid_ext:{...I.antiraid_ext||{}}})},[u]);const z=(I,F,j)=>p(W=>({...W,[I]:{...W[I],[F]:j}})),x=I=>{I.preventDefault(),w({saving:!0,message:"",error:""}),Js(o,"automod",f,c).then(F=>{const j=F.config||{};p({automod:{...j.automod||{}},spam_threshold:j.spam_threshold??6,spam_interval:j.spam_interval??7,max_mentions:j.max_mentions??5,antinuke:{...j.antinuke||{}},antiraid:{...j.antiraid||{}},antiraid_ext:{...j.antiraid_ext||{}}}),w({saving:!1,message:"Moderation settings saved to Niko.",error:""})}).catch(F=>w({saving:!1,message:"",error:F instanceof Error?F.message:"Could not save settings."}))},B=[["antispam","Anti-spam","Detect repeated messages"],["antilink","Invite links","Remove Discord invite links"],["badwords","Blocked words","Filter words from the server list"],["massmention","Mass mentions","Limit mention floods"],["antinuke","Anti-nuke","Protect channels and roles"],["antiraid","Join raid protection","React to sudden join waves"],["antiraid_ext","External app protection","Detect user-installed app abuse"]],b=B.filter(([I])=>{var F;return!!((F=f.automod)!=null&&F[I])}).length;return r.jsxs(r.Fragment,{children:[r.jsx(an,{eyebrow:"Moderation",title:"Keep the room feeling good.",text:"Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration."}),r.jsx(ti,{icon:"shield",label:"Protection desk",title:`${b} of ${B.length} safeguards active`,text:"Start with the essentials, then tune thresholds below when you know the room’s rhythm."}),r.jsxs("form",{onSubmit:x,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wn,{label:"Protection rules",title:"AutoMod modules",detail:"Toggle only the responses you want Niko to handle.",icon:"shield"}),r.jsx("div",{className:"setting-list",children:B.map(([I,F,j])=>{var W;return r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:F}),r.jsx("small",{children:j})]}),r.jsx("input",{type:"checkbox",checked:!!((W=f.automod)!=null&&W[I]),onChange:N=>z("automod",I,N.target.checked)}),r.jsx("i",{"aria-hidden":"true"})]},I)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wn,{label:"Thresholds",title:"Choose when protection steps in",detail:"These limits apply across the server."}),r.jsxs("div",{className:"form-grid",children:[r.jsx(et,{label:"Spam messages",hint:"Messages inside the spam interval",children:r.jsx("input",{type:"number",min:"1",max:"100",value:f.spam_threshold??6,onChange:I=>p({...f,spam_threshold:I.target.value})})}),r.jsx(et,{label:"Spam interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:f.spam_interval??7,onChange:I=>p({...f,spam_interval:I.target.value})})}),r.jsx(et,{label:"Maximum mentions",children:r.jsx("input",{type:"number",min:"1",max:"100",value:f.max_mentions??5,onChange:I=>p({...f,max_mentions:I.target.value})})}),r.jsx(et,{label:"Anti-raid joins",hint:"Joins inside the join interval",children:r.jsx("input",{type:"number",min:"1",max:"1000",value:((C=f.antiraid)==null?void 0:C.join_threshold)??10,onChange:I=>z("antiraid","join_threshold",I.target.value)})}),r.jsx(et,{label:"Anti-raid interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:((M=f.antiraid)==null?void 0:M.join_interval)??10,onChange:I=>z("antiraid","join_interval",I.target.value)})}),r.jsx(et,{label:"Anti-raid action",children:r.jsxs("select",{value:((D=f.antiraid)==null?void 0:D.action)??"kick",onChange:I=>z("antiraid","action",I.target.value),children:[r.jsx("option",{value:"kick",children:"Kick"}),r.jsx("option",{value:"ban",children:"Ban"}),r.jsx("option",{value:"softban",children:"Soft-ban"}),r.jsx("option",{value:"slowmode",children:"Slowmode"}),r.jsx("option",{value:"lockdown",children:"Lockdown"})]})})]}),r.jsx(ni,{state:S})]})]})]})}function Oh({guildId:o,config:u,csrfToken:c}){const[f,p]=R.useState({personality:"cafe",enabled:!0,ai_actions_experiment:!1,better_context_experiment:!1}),[S,w]=R.useState(ei);R.useEffect(()=>{const x=(u==null?void 0:u.ai)||{};p({personality:x.personality||"cafe",enabled:x.enabled!=="False"&&x.enabled!==!1,ai_actions_experiment:x.ai_actions_experiment===!0||x.ai_actions_experiment==="True",better_context_experiment:x.better_context_experiment===!0||x.better_context_experiment==="True"})},[u]);const z=x=>{x.preventDefault(),w({saving:!0,message:"",error:""}),Js(o,"ai",f,c).then(B=>{const b=B.config||{};p({personality:b.personality==="normal"?"normal":"cafe",enabled:b.enabled!=="False"&&b.enabled!==!1,ai_actions_experiment:b.ai_actions_experiment===!0||b.ai_actions_experiment==="True",better_context_experiment:b.better_context_experiment===!0||b.better_context_experiment==="True"}),w({saving:!1,message:"AI settings saved to Niko.",error:""})}).catch(B=>w({saving:!1,message:"",error:B instanceof Error?B.message:"Could not save settings."}))};return r.jsxs(r.Fragment,{children:[r.jsx(an,{eyebrow:"AI controls",title:"Give Niko the right tone.",text:"AI is optional, configurable per server, and designed to stay out of the way when the room does not need it."}),r.jsx(ti,{icon:"settings",label:"Conversation desk",title:f.enabled?"Niko is ready to respond":"Niko is staying quiet",text:"Choose a voice that fits your community. You can change this without affecting other servers."}),r.jsxs("form",{onSubmit:z,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wn,{label:"Conversation",title:"Core settings",detail:"Decide when Niko joins the conversation.",icon:"settings"}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable AI chat"}),r.jsx("small",{children:"Respond when Niko is mentioned"})]}),r.jsx("input",{type:"checkbox",checked:f.enabled,onChange:x=>p({...f,enabled:x.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"personality-options",children:[r.jsxs("button",{type:"button",className:f.personality==="cafe"?"personality active":"personality",onClick:()=>p({...f,personality:"cafe"}),children:[r.jsx("span",{className:"personality-mark",children:"n"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Café"}),r.jsx("small",{children:"Warm, playful, familiar"})]})]}),r.jsxs("button",{type:"button",className:f.personality==="normal"?"personality active":"personality",onClick:()=>p({...f,personality:"normal"}),children:[r.jsx("span",{className:"personality-mark",children:"—"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Normal"}),r.jsx("small",{children:"Clear and straightforward"})]})]})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wn,{label:"Experiments",title:"Optional context",detail:"Try new capabilities when your team is ready."}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Better context"}),r.jsx("small",{children:"Use the last five channel messages"})]}),r.jsx("input",{type:"checkbox",checked:f.better_context_experiment,onChange:x=>p({...f,better_context_experiment:x.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"AI actions"}),r.jsx("small",{children:"Allow confirmed actions requested in chat"})]}),r.jsx("input",{type:"checkbox",checked:f.ai_actions_experiment,onChange:x=>p({...f,ai_actions_experiment:x.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsx(ni,{state:S})]})]})]})}function Uh({guildId:o,config:u,resources:c,csrfToken:f}){const p=(u==null?void 0:u.leveling)||{},[S,w]=R.useState({xp_enabled:!0,xp_multiplier:1,xp_cooldown:0,level_up_channel:"",level_up_message:""}),[z,x]=R.useState(ei);R.useEffect(()=>w({xp_enabled:p.xp_enabled!==!1,xp_multiplier:p.xp_multiplier??1,xp_cooldown:p.xp_cooldown??0,level_up_channel:p.level_up_channel?String(p.level_up_channel):"",level_up_message:p.level_up_message||""}),[u]);const B=C=>{C.preventDefault(),x({saving:!0,message:"",error:""}),Js(o,"leveling",S,f).then(M=>{const D=M.config||{};w({xp_enabled:D.xp_enabled!==!1,xp_multiplier:D.xp_multiplier??1,xp_cooldown:D.xp_cooldown??0,level_up_channel:D.level_up_channel?String(D.level_up_channel):"",level_up_message:D.level_up_message||""}),x({saving:!1,message:"Leveling settings saved to Niko.",error:""})}).catch(M=>x({saving:!1,message:"",error:M instanceof Error?M.message:"Could not save settings."}))},b=Fh(c,S.level_up_channel);return r.jsxs(r.Fragment,{children:[r.jsx(ti,{icon:"spark",label:"Participation desk",title:S.xp_enabled?"XP is flowing":"XP is paused",text:"Set a pace that rewards regulars without turning every message into a transaction."}),r.jsx("form",{onSubmit:B,className:"settings-stack",children:r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wn,{label:"Leveling settings",title:"Shape the pace",detail:"These controls apply to every member in this server.",icon:"spark"}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable XP"}),r.jsx("small",{children:"Track activity and award levels"})]}),r.jsx("input",{type:"checkbox",checked:S.xp_enabled,onChange:C=>w({...S,xp_enabled:C.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"form-grid",children:[r.jsx(et,{label:"XP multiplier",hint:"From 0.1× to 10×",children:r.jsx("input",{type:"number",min:"0.1",max:"10",step:"0.1",value:S.xp_multiplier,onChange:C=>w({...S,xp_multiplier:C.target.value})})}),r.jsx(et,{label:"Cooldown (seconds)",hint:"0 disables the cooldown",children:r.jsx("input",{type:"number",min:"0",max:"86400",value:S.xp_cooldown,onChange:C=>w({...S,xp_cooldown:C.target.value})})}),r.jsx(et,{label:"Level-up channel",children:r.jsxs("select",{value:S.level_up_channel,onChange:C=>w({...S,level_up_channel:C.target.value}),children:[r.jsx("option",{value:"",children:"Same channel"}),b.map(C=>r.jsxs("option",{value:C.id,children:["#",C.name]},C.id))]})}),r.jsx(et,{label:"Level-up message",hint:"Use {mention}, {level}, {name}, or {guild}",children:r.jsx("textarea",{rows:3,maxLength:1e3,value:S.level_up_message,onChange:C=>w({...S,level_up_message:C.target.value}),placeholder:"Leave blank for Niko's default message"})})]}),r.jsx(ni,{state:z})]})})]})}function Wh({guildId:o,config:u,csrfToken:c}){var B;const f=((B=u==null?void 0:u.server)==null?void 0:B.profile)||{},[p,S]=R.useState({display_name:f.display_name||"",bio:f.bio||"",avatar_url:f.avatar_url||"",banner_url:f.banner_url||""}),[w,z]=R.useState(ei);R.useEffect(()=>{var C;const b=((C=u==null?void 0:u.server)==null?void 0:C.profile)||{};S({display_name:b.display_name||"",bio:b.bio||"",avatar_url:b.avatar_url||"",banner_url:b.banner_url||""})},[u]);const x=b=>{b.preventDefault(),z({saving:!0,message:"",error:""}),Zm(o,{display_name:p.display_name||null,bio:p.bio||null,avatar_url:p.avatar_url||null,banner_url:p.banner_url||null},c).then(C=>{const M=C.profile||{};S({display_name:M.display_name||"",bio:M.bio||"",avatar_url:M.avatar_url||"",banner_url:M.banner_url||""}),z({saving:!1,message:"Bot profile updated.",error:""})}).catch(C=>z({saving:!1,message:"",error:C instanceof Error?C.message:"Could not save profile."}))};return r.jsxs(r.Fragment,{children:[r.jsx(an,{eyebrow:"Customization",title:"Niko's server presence.",text:"Change how Niko appears in this server. Display name, avatar, banner, and bio are all per-server."}),r.jsx(ti,{icon:"paint",label:"Identity desk",title:"Server-specific identity",text:"Each server can have its own Niko persona. Changes apply only to this server."}),r.jsxs("form",{onSubmit:x,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wn,{label:"Display name",title:"How Niko appears",detail:"Set the name members see for Niko in this server. Leave blank to use the default.",icon:"settings"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(et,{label:"Display name",hint:"32 characters or fewer",children:r.jsx("input",{value:p.display_name,maxLength:32,onChange:b=>S({...p,display_name:b.target.value}),placeholder:"Niko"})}),r.jsx(et,{label:"Bio",hint:"190 characters or fewer",children:r.jsx("input",{value:p.bio,maxLength:190,onChange:b=>S({...p,bio:b.target.value}),placeholder:"A warm Discord companion"})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wn,{label:"Server avatar & banner",title:"Visual identity",detail:"Provide HTTPS image URLs. Images are uploaded to Discord when saved.",icon:"paint"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(et,{label:"Avatar URL",hint:"Square image, 512×512 recommended",children:r.jsx("input",{type:"url",value:p.avatar_url,onChange:b=>S({...p,avatar_url:b.target.value}),placeholder:"https://cdn.example.com/avatar.png"})}),r.jsx(et,{label:"Banner URL",hint:"Wide image, 960×540 recommended",children:r.jsx("input",{type:"url",value:p.banner_url,onChange:b=>S({...p,banner_url:b.target.value}),placeholder:"https://cdn.example.com/banner.png"})})]}),r.jsx("p",{className:"form-hint",children:"Images are fetched, validated, and uploaded to Discord. Maximum 8 MB each. Supported formats: PNG, JPG, GIF."})]}),r.jsx(ni,{state:w})]})]})}const $h={saving:!1,message:"",error:""};function Ze({label:o,hint:u,children:c}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:o}),c,u&&r.jsx("small",{children:u})]})}function Qs({label:o,title:u,detail:c,icon:f}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:o}),r.jsx("h3",{children:u}),r.jsx("p",{children:c})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(Z,{name:f})})]})}function Vh({state:o}){return r.jsxs("div",{className:"setting-footer",children:[o.error?r.jsx("span",{className:"form-error",role:"alert",children:o.error}):r.jsx("span",{role:"status",children:o.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:o.saving,children:o.saving?"Saving...":"Save server settings"})]})}const Hh=[["moderation","Moderation"],["automod","AutoMod"],["messages","Messages"],["channels","Channels"],["members","Members"],["captcha","Captcha"],["invites","Invites"],["roles","Roles"],["server","Server"],["voice","Voice"]];function Gh(o,u){var c;return u?((c=o==null?void 0:o.channels.find(f=>f.id===String(u)))==null?void 0:c.name)||`Channel ${u}`:"Not set"}function Xs(o,u){const c=u?String(u):"",f=(o==null?void 0:o.channels)||[];return!c||f.some(p=>p.id===c)?f:[{id:c,name:`Unavailable channel (${c})`},...f]}function _c(o,u=[]){const c=(o==null?void 0:o.roles)||[],f=new Set(c.map(S=>S.id));return[...u.map(String).filter((S,w,z)=>S&&!f.has(S)&&z.indexOf(S)===w).map(S=>({id:S,name:`Unavailable role (${S})`})),...c]}function Ec(o){var f,p;const u=(o==null?void 0:o.onboarding)||{},c=(o==null?void 0:o.tickets)||{};return{prefixes:((f=o==null?void 0:o.prefixes)!=null&&f.length?o.prefixes:["."]).join(`
`),welcome_channel:u.welcome_channel?String(u.welcome_channel):"",welcome_title:u.welcome_title||"",welcome_description:u.welcome_description||"",welcome_color:u.welcome_color===null||u.welcome_color===void 0?"5865F2":u.welcome_color.toString(16).padStart(6,"0"),welcome_image:u.welcome_image||"",rules_channel:u.rules_channel?String(u.rules_channel):"",rules_text:u.rules_text||"",rules_role_id:u.rules_role_id?String(u.rules_role_id):"",logging:Object.fromEntries(Object.entries((o==null?void 0:o.logging)||{}).map(([S,w])=>[S,w==null?"":String(w)])),disabled_logging:[...((p=o==null?void 0:o.logging)==null?void 0:p.disabled)||[]].map(String),panel_title:c.panel_title||"",panel_description:c.panel_description||"",panel_categories:(c.panel_categories||[]).join(`
`),panel_channel_id:c.panel_channel_id?String(c.panel_channel_id):"",support_roles:[...c.support_roles||[]].map(String)}}function Kh({guildId:o,config:u,resources:c,csrfToken:f}){const[p,S]=R.useState(()=>Ec(u==null?void 0:u.server)),[w,z]=R.useState($h),x=(N,Q)=>S(te=>({...te,[N]:Q})),B=(N,Q)=>S(te=>({...te,logging:{...te.logging,[N]:Q}})),b=N=>S(Q=>({...Q,disabled_logging:Q.disabled_logging.includes(N)?Q.disabled_logging.filter(te=>te!==N):[...Q.disabled_logging,N]})),C=N=>{N.preventDefault(),z({saving:!0,message:"",error:""});const Q=p.prefixes.split(/\r?\n|,/).map(se=>se.trim()).filter(Boolean),te=p.panel_categories.split(/\r?\n|,/).map(se=>se.trim()).filter(Boolean);Js(o,"server",{prefixes:Q,onboarding:{welcome_channel:p.welcome_channel,welcome_title:p.welcome_title,welcome_description:p.welcome_description,welcome_color:p.welcome_color,welcome_image:p.welcome_image,rules_channel:p.rules_channel,rules_text:p.rules_text,rules_role_id:p.rules_role_id},logging:{...p.logging,disabled:p.disabled_logging},tickets:{panel_title:p.panel_title,panel_description:p.panel_description,panel_categories:te,panel_channel_id:p.panel_channel_id,support_roles:p.support_roles}},f).then(se=>{S(Ec(se.config)),z({saving:!1,message:"Server settings saved to Niko.",error:""})}).catch(se=>z({saving:!1,message:"",error:se instanceof Error?se.message:"Could not save server settings."}))},M=p.welcome_channel,D=p.panel_channel_id,I=Xs(c,p.welcome_channel),F=Xs(c,p.rules_channel),j=Xs(c,p.panel_channel_id),W=_c(c,p.support_roles);return r.jsxs(r.Fragment,{children:[r.jsx(an,{eyebrow:"Server settings",title:"Make Niko fit your room.",text:"Manage the settings that shape how Niko behaves in this server. Economy balances remain global to each user and are not configured here."}),r.jsxs("div",{className:"settings-intro",children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(Z,{name:"settings"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server control room"}),r.jsxs("strong",{children:[p.prefixes.split(/\r?\n|,/).filter(Boolean).length||0," command prefixes configured"]}),r.jsx("p",{children:"Welcome flows, log destinations, and ticket panels all live here."})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]}),r.jsxs("form",{onSubmit:C,className:"settings-stack server-settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Qs,{label:"Commands",title:"Prefixes",detail:"Use one prefix per line. Niko will respond to all of them.",icon:"terminal"}),r.jsx(Ze,{label:"Command prefixes",hint:"The default prefix is .",children:r.jsx("textarea",{rows:3,maxLength:200,value:p.prefixes,onChange:N=>x("prefixes",N.target.value),placeholder:".\\n!"})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Qs,{label:"Welcome flow",title:"Welcome and rules",detail:"Choose where new members see your welcome message and rules.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(Ze,{label:"Welcome channel",children:r.jsxs("select",{value:M,onChange:N=>x("welcome_channel",N.target.value),children:[r.jsx("option",{value:"",children:"Disabled"}),I.map(N=>r.jsxs("option",{value:N.id,children:["#",N.name]},N.id))]})}),r.jsx(Ze,{label:"Welcome title",children:r.jsx("input",{value:p.welcome_title,maxLength:200,onChange:N=>x("welcome_title",N.target.value),placeholder:"Welcome to the server"})}),r.jsx(Ze,{label:"Welcome message",hint:"Supports {user} and {name}",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:p.welcome_description,onChange:N=>x("welcome_description",N.target.value),placeholder:"Welcome {user}!"})}),r.jsx(Ze,{label:"Accent color",hint:"Hex color, for example 5865F2",children:r.jsx("input",{value:p.welcome_color,maxLength:7,onChange:N=>x("welcome_color",N.target.value),placeholder:"5865F2"})}),r.jsx(Ze,{label:"Welcome image URL",children:r.jsx("input",{type:"url",value:p.welcome_image,onChange:N=>x("welcome_image",N.target.value),placeholder:"https://..."})}),r.jsx(Ze,{label:"Rules channel",children:r.jsxs("select",{value:p.rules_channel,onChange:N=>x("rules_channel",N.target.value),children:[r.jsx("option",{value:"",children:"Not configured"}),F.map(N=>r.jsxs("option",{value:N.id,children:["#",N.name]},N.id))]})}),r.jsx(Ze,{label:"Rules text",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:p.rules_text,onChange:N=>x("rules_text",N.target.value),placeholder:"Write the rules members should acknowledge."})}),r.jsx(Ze,{label:"Role after rules acknowledgment",children:r.jsxs("select",{value:p.rules_role_id,onChange:N=>x("rules_role_id",N.target.value),children:[r.jsx("option",{value:"",children:"No role"}),_c(c,p.rules_role_id?[p.rules_role_id]:[]).map(N=>r.jsxs("option",{value:N.id,children:["@",N.name]},N.id))]})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Qs,{label:"Audit trail",title:"Logging destinations",detail:"Pick a channel for each event type and disable categories you do not need.",icon:"book"}),r.jsx("div",{className:"server-logging-list",children:Hh.map(([N,Q])=>{const te=Xs(c,p.logging[N]);return r.jsxs("div",{className:"server-logging-row",children:[r.jsxs("label",{className:"form-field",children:[r.jsxs("span",{className:"form-label",children:[Q," logs"]}),r.jsxs("select",{value:String(p.logging[N]||""),onChange:se=>B(N,se.target.value),children:[r.jsx("option",{value:"",children:"Not set"}),te.map(se=>r.jsxs("option",{value:se.id,children:["#",se.name]},se.id))]})]}),r.jsxs("label",{className:"setting-row compact-setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enabled"}),r.jsx("small",{children:Gh(c,p.logging[N])})]}),r.jsx("input",{type:"checkbox",checked:!p.disabled_logging.includes(N),onChange:()=>b(N)}),r.jsx("i",{"aria-hidden":"true"})]})]},N)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Qs,{label:"Support desk",title:"Ticket panel",detail:"Configure the public panel and decide who can handle tickets.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(Ze,{label:"Panel title",children:r.jsx("input",{value:p.panel_title,maxLength:200,onChange:N=>x("panel_title",N.target.value),placeholder:"Open a Ticket"})}),r.jsx(Ze,{label:"Panel channel",children:r.jsxs("select",{value:D,onChange:N=>x("panel_channel_id",N.target.value),children:[r.jsx("option",{value:"",children:"Keep current panel channel"}),j.map(N=>r.jsxs("option",{value:N.id,children:["#",N.name]},N.id))]})}),r.jsx(Ze,{label:"Panel description",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:p.panel_description,onChange:N=>x("panel_description",N.target.value),placeholder:"Tell members what the ticket panel is for."})}),r.jsx(Ze,{label:"Ticket categories",hint:"One category per line",children:r.jsx("textarea",{rows:4,value:p.panel_categories,onChange:N=>x("panel_categories",N.target.value),placeholder:"General\\nSupport\\nReports"})}),r.jsx(Ze,{label:"Support roles",hint:"Hold Ctrl/Cmd to select more than one",children:r.jsx("select",{multiple:!0,value:p.support_roles,onChange:N=>x("support_roles",Array.from(N.target.selectedOptions,Q=>Q.value)),children:W.map(N=>r.jsxs("option",{value:N.id,children:["@",N.name]},N.id))})})]}),r.jsx("p",{className:"form-hint",children:"Saving panel settings updates the existing posted panel when Niko can find its saved message."})]}),r.jsx(Vh,{state:w})]})]})}function Qh({auth:o}){const u=Zs();return r.jsxs(r.Fragment,{children:[r.jsx(St,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"n"}),r.jsx("div",{className:"eyebrow",children:"Private workspace"}),r.jsxs("h1",{children:["Settle in, ",r.jsx("em",{children:"admin."})]}),r.jsx("p",{children:"Sign in with Discord to see your Niko profile and manage the servers you look after."}),o.oauth_available?r.jsxs("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard",children:[r.jsx(Z,{name:"lock"})," Continue with Discord ",r.jsx(Z,{name:"arrow"})]}):r.jsxs("div",{className:"notice warning",children:["Discord login is not configured yet. Add ",r.jsx("code",{children:"DISCORD_CLIENT_SECRET"})," to the environment and restart the bot."]}),!u&&r.jsx("p",{className:"form-hint",children:"The public bot configuration is still loading."}),r.jsx("a",{className:"back-link",href:"/",onClick:c=>{c.preventDefault(),he("/")},children:"Return to public site"})]})})]})}function Xh({section:o,guild:u,stats:c,csrfToken:f}){const[p,S]=R.useState(null),[w,z]=R.useState([]),[x,B]=R.useState(null),[b,C]=R.useState(null),[M,D]=R.useState(!0),[I,F]=R.useState("");return R.useEffect(()=>{D(!0),F(""),(o==="overview"?Ym(u.id).then(S):o==="leveling"?Promise.all([Jm(u.id),fc(u.id),gc(u.id)]).then(([W,N,Q])=>{z(W),B(N),C(Q)}):Promise.all([fc(u.id),gc(u.id)]).then(([W,N])=>{B(W),C(N)})).catch(W=>F(W instanceof Error?W.message:"This server could not be loaded.")).finally(()=>D(!1))},[u.id,o]),M?r.jsxs("div",{className:"section-loading section-skeleton",role:"status","aria-label":`Loading ${o}`,children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsxs("span",{children:["Loading ",o,"..."]})]}):I?r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Couldn’t load this page."}),r.jsx("span",{children:I}),r.jsx("button",{className:"button button-muted",onClick:()=>window.location.reload(),children:"Try again"})]}):o==="overview"&&p?r.jsx(Ih,{overview:p}):o==="leveling"?r.jsx(zh,{guildId:u.id,rows:w,config:x,resources:b,csrfToken:f}):o==="moderation"?r.jsx(Bh,{guildId:u.id,config:x,csrfToken:f}):o==="server"?r.jsx(Kh,{guildId:u.id,config:x,resources:b,csrfToken:f}):o==="customization"?r.jsx(Wh,{guildId:u.id,config:x,csrfToken:f}):r.jsx(Oh,{guildId:u.id,config:x,csrfToken:f})}function qh(){return r.jsxs("div",{className:"section-loading section-skeleton dashboard-loading",role:"status",children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"Preparing your dashboard..."})]})}function Yh(){Zs();const[o,u]=R.useState(xc),[c,f]=R.useState(null),[p,S]=R.useState(null),[w,z]=R.useState(null),[x,B]=R.useState([]),[b,C]=R.useState(null),[M,D]=R.useState(!0),[I,F]=R.useState("");if(R.useEffect(()=>{const _=()=>u(xc());return window.addEventListener("popstate",_),()=>window.removeEventListener("popstate",_)},[]),R.useEffect(()=>{D(!0),Promise.all([Gm(),Pc()]).then(([_,X])=>(f(_),S(X),_.authenticated?Promise.all([qm(),Xm()]).then(([me,je])=>{z(me),B(je)}):null)).catch(_=>F(_ instanceof Error?_.message:"Dashboard unavailable")).finally(()=>D(!1))},[]),R.useEffect(()=>{if(o.view!=="guild"){C(null);return}const _=x.find(X=>X.id===o.guildId&&X.installed!==!1);_?(C(_),localStorage.setItem("niko-guild",_.id)):o.guildId&&x.length&&he(yc())},[x,o.guildId,o.view]),M||!c)return r.jsxs("div",{className:"dashboard-state",children:[r.jsx("div",{className:"loading-ring"}),r.jsx("p",{children:"Connecting to Niko…"})]});if(I)return r.jsxs(r.Fragment,{children:[r.jsx(St,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Connection issue"}),r.jsxs("h1",{children:["Couldn’t load",r.jsx("br",{}),r.jsx("em",{children:"your workspace."})]}),r.jsx("p",{children:I}),r.jsxs("button",{className:"button button-primary",onClick:()=>window.location.reload(),children:["Try again ",r.jsx(Z,{name:"arrow"})]})]})})]});if(!c.authenticated)return r.jsx(Qh,{auth:c});const j=_=>{_.installed!==!1&&(localStorage.setItem("niko-guild",_.id),he(Ar(_.id,o.section)))},W=_=>{_.installed!==!1&&(localStorage.setItem("niko-guild",_.id),he(Ar(_.id,"overview")))},N=_=>{he(b?Ar(b.id,_):Ar())},Q=()=>he(Ar()),te=()=>he(yc());let se;return o.view==="servers"?se=r.jsx(Dh,{guilds:x,onManage:W}):o.view==="guild"?se=b?r.jsx(Xh,{section:o.section,guild:b,stats:p,csrfToken:c.csrf_token},`${b.id}-${o.section}`):r.jsx(qh,{}):se=r.jsx(Ah,{user:c.user,overview:w,guilds:x,onServers:te,onManage:W}),r.jsx(Rh,{user:c.user,guilds:x,selectedGuild:b,view:o.view,section:o.section,stats:p,onHome:Q,onServers:te,onGuildChange:j,onSectionChange:N,children:se})}function Jh({value:o,onChange:u,placeholder:c="Search documentation...",onFocus:f,onBlur:p}){const[S,w]=R.useState(!1),z=R.useRef(null),[x,B]=R.useState(!1);R.useEffect(()=>{const I=F=>{var j;(F.metaKey||F.ctrlKey)&&F.key==="k"&&(F.preventDefault(),(j=z.current)==null||j.focus())};return document.addEventListener("keydown",I),()=>document.removeEventListener("keydown",I)},[]);const b=()=>{w(!0),B(!0),f==null||f()},C=()=>{w(!1),setTimeout(()=>B(!1),200),p==null||p()},M=I=>{u(I.target.value)},D=I=>{var F;I.key==="Escape"&&((F=z.current)==null||F.blur())};return r.jsxs("div",{className:`doc-search-bar ${x?"expanded":""}`,children:[r.jsxs("div",{className:"search-input-wrapper",children:[r.jsx(Z,{name:"search",className:"search-icon"}),r.jsx("input",{ref:z,type:"text",value:o,onChange:M,onFocus:b,onBlur:C,onKeyDown:D,placeholder:c,className:"search-input","aria-label":"Search documentation"}),r.jsxs("kbd",{className:"search-shortcut",children:[r.jsx("span",{className:"shortcut-key",children:"⌘"}),"K"]})]}),r.jsxs("div",{className:"search-hint",children:["Press ",r.jsx("kbd",{children:"⌘K"})," to focus search"]})]})}function Zh({selectedCategory:o,onSelectCategory:u,sections:c,allCategoriesLabel:f="All Categories"}){return r.jsx("div",{className:"doc-filters",children:r.jsxs("div",{className:"filter-tabs",role:"tablist","aria-label":"Filter by category",children:[r.jsx("button",{role:"tab","aria-selected":o==="",className:`filter-tab ${o===""?"active":""}`,onClick:()=>u(""),children:f}),c.map(p=>r.jsxs("button",{role:"tab","aria-selected":o===p.id,className:`filter-tab ${o===p.id?"active":""}`,onClick:()=>u(p.id),children:[r.jsx(Z,{name:p.icon,size:14}),r.jsx("span",{children:p.label})]},p.id))]})})}function io({doc:o,variant:u="default"}){const c="page"in o?o.page:o,[f,p]=R.useState(!1),S=x=>{x.preventDefault(),he(`/docs/${c.slug}`)},w=x=>{(x.key==="Enter"||x.key===" ")&&(x.preventDefault(),he(`/docs/${c.slug}`))};if(u==="compact")return r.jsx("a",{href:`/docs/${c.slug}`,onClick:S,onKeyDown:w,className:"doc-card-compact",tabIndex:0,role:"button",children:r.jsxs("div",{className:"compact-content",children:[r.jsx("span",{className:"compact-title",children:c.title}),r.jsx("span",{className:"compact-excerpt",children:c.excerpt})]})});const z="highlights"in o?o.highlights:[];return r.jsx("article",{className:`doc-card ${u==="highlighted"?"highlighted":""}`,children:r.jsxs("div",{className:`doc-card-content ${f?"loaded":""}`,children:[r.jsxs("div",{className:"doc-card-header",children:[r.jsx("span",{className:"doc-category",children:c.category.replace(/-/g," ")}),r.jsxs("span",{className:"doc-order",children:["#",c.order]})]}),r.jsx("h3",{className:"doc-title",children:c.title}),r.jsx("p",{className:"doc-excerpt",children:c.excerpt}),z.length>0&&r.jsx("div",{className:"doc-highlights",children:z.slice(0,2).map((x,B)=>r.jsxs("p",{className:"highlight-snippet",children:[x.slice(0,150),x.length>150?"...":""]},B))}),r.jsxs("div",{className:"doc-card-footer",children:[r.jsx("div",{className:"doc-tags",children:c.tags.slice(0,3).map(x=>r.jsxs("span",{className:"doc-tag",children:["#",x]},x))}),r.jsxs("a",{href:`/docs/${c.slug}`,onClick:S,onKeyDown:w,className:"doc-read-more",children:["Read more ",r.jsx(Z,{name:"arrow",size:14})]})]})]})})}const Me=[{slug:"welcome",title:"Welcome to Niko",category:"getting-started",excerpt:"New to Niko? Start here to understand what the bot can do for your server.",tags:["introduction","overview","beginner"],order:1,content:`
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
    `},{slug:"server-configuration",title:"Server Configuration Basics",category:"setup",excerpt:"Learn the essentials of configuring Niko for your server.",tags:["configuration","settings","admin"],order:1,content:`
# Server Configuration Basics

Proper server configuration ensures Niko works the way you want. This guide covers the essential settings.

## Access Settings

There are two ways to configure Niko:

1. **Discord Commands**: Use commands like \`.automod\`, \`.logging\`, or \`.levelconfig\`
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
.levelconfig
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
    `},{slug:"tickets-guide",title:"Ticket System Guide",category:"setup",excerpt:"Set up a support ticket system with categories, support roles, and private ticket channels.",tags:["tickets","support","setup","admin"],order:3,content:`
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
    `},{slug:"tickets-transcripts",title:"Ticket Web Transcripts",category:"setup",excerpt:"Generate shareable web transcripts of your tickets and download them as TXT, HTML, CSV, or JSON.",tags:["tickets","transcripts","records","support"],order:4,content:`
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
.levelconfig toggle
\`\`\`

### Set XP Multiplier
Adjust how fast members level:

\`\`\`
.levelconfig multiplier <value>
\`\`\`

### Set Cooldown
Prevent XP spam with cooldowns:

\`\`\`
.levelconfig cooldown <seconds>
\`\`\`

### Level Up Channel
Choose where level-up announcements appear:

\`\`\`
.levelconfig levelupchannel <channel>
\`\`\`

### Custom Level Up Messages
Level-up announcements are posted in the configured channel.

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
.levelconfig levelrole <level> <role>
\`\`\`

## Leaderboards

View leveling leaderboards:

\`\`\`
.level-leaderboard
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
.levelconfig toggle
\`\`\`

When disabled, no XP is earned and level-up events don't fire.

### XP Multiplier
Adjust the rate at which members earn XP:

\`\`\`
.levelconfig multiplier <number>
\`\`\`

- \`1.0\` = Normal speed
- \`2.0\` = Double speed
- \`0.5\` = Half speed

### XP Cooldown
Set a cooldown between XP gains from messages:

\`\`\`
.levelconfig cooldown <seconds>
\`\`\`

Example: \`.levelconfig cooldown 60\` gives 60 seconds between XP from messages.

## Announcements

### Level Up Channel
Set where level-up notifications are sent:

\`\`\`
.levelconfig levelupchannel <channel>
\`\`\`

Placeholders in announcements:
- \`{user}\` - Username
- \`{level}\` - New level
- \`{guild}\` - Server name

## Level Roles

### Assigning Roles
Give roles when members reach certain levels:

\`\`\`
.levelconfig levelrole <level> <role mention or id>
\`\`\`

Example:
\`\`\`
.levelconfig levelrole 10 @Member
.levelconfig levelrole 50 @Regular
.levelconfig levelrole 100 @Veteran
\`\`\`

### Checking Progress
Members can check their stats:

\`\`\`
.level
.level @user
\`\`\`

## Resetting Leveling Data

To reset a member's leveling progress:

\`\`\`
.levelconfig resetuser <member>
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
/levelconfig toggle
\`\`\`

More leveling options (multiplier, cooldown, level-up channel, role rewards) live in \`.levelconfig\` or the dashboard.

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
- \`/levelconfig\` - Level settings
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
    `}];function ep(o){return Me.find(u=>u.slug===o)}const sn=[{id:"getting-started",label:"Getting Started",description:"New to Niko? Start here.",icon:"icon_home",count:Me.filter(o=>o.category==="getting-started").length},{id:"setup",label:"Setup",description:"Configure Niko for your server.",icon:"icon_settings",count:Me.filter(o=>o.category==="setup").length},{id:"economy",label:"Economy",description:"Money, jobs, banking, and more.",icon:"icon_economy",count:Me.filter(o=>o.category==="economy").length},{id:"leveling",label:"Leveling",description:"XP, levels, and rankings.",icon:"icon_leveling",count:Me.filter(o=>o.category==="leveling").length},{id:"moderation",label:"Moderation",description:"Moderation tools and commands.",icon:"icon_moderation",count:Me.filter(o=>o.category==="moderation").length},{id:"automod",label:"AutoMod",description:"Automated moderation features.",icon:"icon_automod",count:Me.filter(o=>o.category==="automod").length},{id:"social",label:"Social",description:"Community engagement features.",icon:"icon_heart",count:Me.filter(o=>o.category==="social").length},{id:"utility",label:"Utility",description:"Helpful tools and utilities.",icon:"icon_utility",count:Me.filter(o=>o.category==="utility").length},{id:"voice",label:"Voice",description:"Voice and music features.",icon:"icon_bot",count:Me.filter(o=>o.category==="voice").length},{id:"ai",label:"AI",description:"AI-powered features.",icon:"icon_ai",count:Me.filter(o=>o.category==="ai").length},{id:"dashboard",label:"Dashboard",description:"Web dashboard guides.",icon:"icon_settings",count:Me.filter(o=>o.category==="dashboard").length},{id:"tips",label:"Tips",description:"Tips and best practices.",icon:"icon_lightbulb",count:Me.filter(o=>o.category==="tips").length}];function zc(){const[o,u]=R.useState({query:"",category:"",tags:[]}),c=R.useCallback(x=>{u(B=>({...B,query:x.toLowerCase(),tags:[]}))},[]),f=R.useCallback(x=>{u(B=>({...B,category:x,tags:[]}))},[]),p=R.useCallback(x=>{u(B=>{const b=B.tags.includes(x)?B.tags.filter(C=>C!==x):[...B.tags,x];return{...B,tags:b,query:""}})},[]),S=R.useCallback(()=>{u({query:"",category:"",tags:[]})},[]),w=R.useMemo(()=>{const{query:x,category:B,tags:b}=o;if(!x&&!B&&b.length===0)return Me.map(M=>({page:M,score:1,highlights:[]}));const C=[];for(const M of Me)if(!(B&&M.category!==B)&&!(b.length>0&&!b.some(D=>M.tags.includes(D))))if(x){const D=tp(M,x);if(D===0)continue;const I=np(M,x);C.push({page:M,score:D,highlights:I})}else C.push({page:M,score:1,highlights:[]});return C.sort((M,D)=>D.score!==M.score?D.score-M.score:M.page.order-D.page.order),C},[o]),z=o.query!==""||o.category!==""||o.tags.length>0;return{filters:o,setQuery:c,setCategory:f,toggleTag:p,clearFilters:S,results:w,hasActiveFilters:z,resultCount:w.length}}function tp(o,u){let c=0;const f=u.toLowerCase();o.title.toLowerCase()===f?c+=100:o.title.toLowerCase().includes(f)&&(c+=50),o.excerpt.toLowerCase().includes(f)&&(c+=25),o.content.toLowerCase().includes(f)&&(c+=10);for(const p of o.tags)p.toLowerCase().includes(f)&&(c+=15);return o.category.toLowerCase().includes(f)&&(c+=5),c}function np(o,u){const c=[],f=u.toLowerCase(),p=3;if(o.title.toLowerCase().includes(f)&&(c.push(o.title),c.length>=p)||o.excerpt.toLowerCase().includes(f)&&(c.push(o.excerpt),c.length>=p))return c;const S=o.content.split(`
`).filter(w=>w.trim());for(const w of S)if(w.toLowerCase().includes(f)){const z=w.replace(/#{1,6}\s?/g,"").trim();if(z.length>10&&(c.push(z),c.length>=p))break}return c}function rp(){return R.useMemo(()=>{const u={};return Me.forEach(c=>{c.tags.forEach(f=>{u[f]=(u[f]||0)+1})}),Object.entries(u).map(([c,f])=>({tag:c,count:f})).sort((c,f)=>f.count-c.count)},[])}function sp({slug:o}){var x,B;const{setCategory:u,clearFilters:c}=zc();R.useEffect(()=>{window.location.hash!==`#/docs/${o}`&&window.history.replaceState(null,"",`#/docs/${o}`)},[o]);const f=ep(o);if(!f)return r.jsxs(r.Fragment,{children:[r.jsx(St,{page:"docs"}),r.jsx("main",{className:"shell page-main docs-page",children:r.jsxs("div",{className:"docs-not-found",children:[r.jsx(Z,{name:"doc",size:48,className:"not-found-icon"}),r.jsx("h1",{children:"Page Not Found"}),r.jsxs("p",{children:[`We couldn't find documentation for "`,o,'".']}),r.jsxs("div",{className:"not-found-actions",children:[r.jsx("button",{onClick:()=>he("/docs"),children:"Browse all documentation"}),r.jsx("button",{onClick:()=>{he("/docs"),c()},children:"Clear filters"})]})]})}),r.jsx(Kn,{})]});const p=b=>{const C=[],M=/(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*)/g;let D=0,I,F=0;for(;(I=M.exec(b))!==null;){I.index>D&&C.push(b.slice(D,I.index));const j=I[0];if(j.startsWith("`")&&j.endsWith("`")&&j.length>2)C.push(r.jsx("code",{className:"doc-inline-code",children:j.slice(1,-1)},F++));else if(j.startsWith("[")){const W=j.match(/^\[([^\]]+)\]\(([^)]+)\)$/);W?C.push(r.jsx("a",{href:W[2],target:"_blank",rel:"noreferrer",children:p(W[1])},F++)):C.push(j)}else j.startsWith("**")?C.push(r.jsx("strong",{children:p(j.slice(2,-2))},F++)):j.startsWith("*")?C.push(r.jsx("em",{children:p(j.slice(1,-1))},F++)):C.push(j);D=I.index+j.length}return D<b.length&&C.push(b.slice(D)),C},w=(b=>{const C=b.split(`
`),M=[];let D=0,I=null,F=[];const j=()=>{if(F.length===0)return;const N=I==="ol"?"ol":"ul";M.push(r.jsx(N,{className:`doc-content-list ${I==="ol"?"doc-content-list-ol":""}`,children:F.map((Q,te)=>r.jsx("li",{children:p(Q)},te))},`list-${M.length}`)),F=[],I=null},W=()=>{var te;const N=M[M.length-1];R.isValidElement(N)&&((te=N.props)==null?void 0:te.className)==="doc-content-spacer"||M.push(r.jsx("div",{className:"doc-content-spacer"},`spacer-${M.length}`))};for(;D<C.length;){const Q=C[D].trim();if(!Q){j(),W(),D+=1;continue}if(Q.startsWith("```")){j();const _=[];let X=D+1;for(;X<C.length&&C[X].trim()!=="```";)_.push(C[X]),X+=1;M.push(r.jsx("pre",{className:"doc-code-block",children:r.jsx("code",{children:_.join(`
`)})},`code-${D}`)),D=X+1;continue}if(Q.startsWith("|")){j();const _=[];let X=D;for(;X<C.length&&C[X].trim().startsWith("|");){const We=C[X].trim().replace(/^\|/,"").replace(/\|$/,"").split("|").map(ze=>ze.trim());_.push(We),X+=1}const me=_.length>1&&_[1].every(We=>/^:?-{2,}:?$/.test(We.replace(/\s+/g,""))),je=_[0],rt=me?_.slice(2):_.slice(1);je.length>1&&M.push(r.jsxs("table",{className:"doc-table",children:[r.jsx("thead",{children:r.jsx("tr",{children:je.map((We,ze)=>r.jsx("th",{children:p(We)},ze))})}),r.jsx("tbody",{children:rt.map((We,ze)=>r.jsx("tr",{children:We.map(($e,st)=>r.jsx("td",{children:p($e)},st))},ze))})]},`table-${D}`)),D=X;continue}if(Q.startsWith("### ")){j(),M.push(r.jsx("h4",{className:"doc-heading doc-heading-h4",children:Q.slice(4)},`h-${D}`)),D+=1;continue}if(Q.startsWith("## ")){j(),M.push(r.jsx("h3",{className:"doc-heading doc-heading-h3",children:Q.slice(3)},`h-${D}`)),D+=1;continue}if(Q.startsWith("# ")){j(),M.push(r.jsx("h2",{className:"doc-heading doc-heading-h2",children:Q.slice(2)},`h-${D}`)),D+=1;continue}if(Q.startsWith("> ")){j(),M.push(r.jsx("blockquote",{className:"doc-blockquote",children:p(Q.slice(2))},`q-${D}`)),D+=1;continue}const te=Q.match(/^[-*]\s+(.*)$/);if(te){I!=="ul"&&j(),I="ul",F.push(te[1]),D+=1;continue}const se=Q.match(/^\d+\.\s+(.*)$/);if(se){I!=="ol"&&j(),I="ol",F.push(se[1]),D+=1;continue}j(),M.push(r.jsx("p",{className:"doc-paragraph",children:p(Q)},`p-${D}`)),D+=1}return j(),M})(f.content),z=w.filter(b=>R.isValidElement(b)&&(b.type==="h2"||b.type==="h3"));return r.jsxs(r.Fragment,{children:[r.jsx(St,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page docs-detail-page",children:[r.jsx("div",{className:"docs-detail-back",children:r.jsxs("button",{onClick:()=>he("/docs"),className:"back-button",children:[r.jsx(Z,{name:"arrow",size:16}),"Back to Documentation"]})}),r.jsxs("header",{className:"doc-article-header",children:[r.jsxs("div",{className:"doc-article-meta",children:[r.jsx("span",{className:"doc-category-badge",children:((x=sn.find(b=>b.id===f.category))==null?void 0:x.label)||f.category}),r.jsxs("span",{className:"doc-order-badge",children:["Article #",f.order]})]}),r.jsx("h1",{className:"doc-article-title",children:f.title}),r.jsx("p",{className:"doc-article-excerpt",children:f.excerpt}),r.jsx("div",{className:"doc-article-tags",children:f.tags.map(b=>r.jsxs("span",{className:"doc-tag-pill",children:["#",b]},b))})]}),r.jsx("article",{className:"doc-article-content",children:w}),r.jsx("footer",{className:"doc-article-footer",children:r.jsx("div",{className:"doc-nav-container",children:r.jsxs("div",{className:"doc-nav-col",children:[r.jsx("span",{className:"doc-nav-label",children:"Category"}),r.jsxs("button",{className:"doc-nav-link",onClick:()=>{u(f.category),he("/docs")},children:[r.jsx(Z,{name:"arrow",size:14}),"View all ",(B=sn.find(b=>b.id===f.category))==null?void 0:B.label]})]})})}),z.length>0&&r.jsxs("aside",{className:"doc-toc",children:[r.jsxs("div",{className:"toc-title",children:[r.jsx(Z,{name:"utility",size:16}),r.jsx("span",{children:"On this page"})]}),r.jsx("nav",{className:"toc-nav",children:z.map((b,C)=>{var D;const M=(D=b.props.className)==null?void 0:D.includes("doc-heading-h2");return r.jsx("a",{href:`#${M?"h2-":"h3-"}-${C}`,className:`toc-link ${M?"toc-h2":"toc-h3"}`,children:b.props.children},C)})})]})]}),r.jsx(Kn,{})]})}function ip(){var te,se;const[o,u]=R.useState(!1),[c,f]=R.useState(""),[p,S]=R.useState(!1),{filters:w,setQuery:z,setCategory:x,toggleTag:B,clearFilters:b,results:C,hasActiveFilters:M,resultCount:D}=zc(),I=rp();R.useEffect(()=>{const _=()=>{const X=window.location.hash.slice(1);if(X.startsWith("#/docs/")){const me=X.replace("#/docs/",""),je=Me.find(rt=>rt.slug===me);je&&(f(je.category),x(je.category))}};return _(),window.addEventListener("hashchange",_),()=>window.removeEventListener("hashchange",_)},[]);const F=()=>{S(!0)},j=_=>{f(_),x(_),u(!1)},W=()=>{w.query||S(!1)},N=_=>{he(`/docs/${_}`),z(""),S(!1)},Q=R.useMemo(()=>{const _={};return C.forEach(X=>{const me=X.page.category;_[me]||(_[me]=[]),_[me].push(X)}),_},[C]);return r.jsxs(r.Fragment,{children:[r.jsx(St,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page",children:[r.jsx("div",{className:"docs-hero",children:r.jsxs("div",{className:"docs-hero-content",children:[r.jsx("div",{className:"eyebrow docs-eyebrow",children:"Documentation Center"}),r.jsxs("h1",{className:"docs-title",children:["Everything you need to know about",r.jsx("br",{}),r.jsx("span",{className:"title-accent",children:"using Niko"})]}),r.jsx("p",{className:"docs-subtitle",children:"Comprehensive guides, command references, and tips to help you get the most out of your server bot."})]})}),r.jsx("div",{className:`docs-search-section ${p?"active":""}`,children:r.jsxs("div",{className:"docs-search-container",children:[r.jsx(Jh,{value:w.query,onChange:z,placeholder:"Search documentation, commands, guides...",onFocus:F,onBlur:W}),p&&w.query&&C.length>0&&r.jsxs("div",{className:"search-results-dropdown",children:[r.jsxs("div",{className:"search-results-header",children:[r.jsxs("span",{className:"results-count",children:[D," ",D===1?"result":"results"]}),r.jsx("button",{className:"clear-search-btn",onClick:()=>{z(""),b(),f("")},children:"Clear"})]}),r.jsx("div",{className:"search-results-list",children:C.slice(0,8).map((_,X)=>r.jsxs("button",{className:"search-result-item",onClick:()=>N(_.page.slug),onMouseEnter:()=>{},children:[r.jsx("div",{className:"result-icon",children:r.jsx(Z,{name:"doc",size:18})}),r.jsxs("div",{className:"result-content",children:[r.jsx("div",{className:"result-title",children:_.page.title}),r.jsx("div",{className:"result-excerpt",children:_.page.excerpt}),_.highlights.length>0&&r.jsxs("div",{className:"result-highlight",children:[_.highlights[0].slice(0,100),"..."]})]}),r.jsx(Z,{name:"arrow",size:14,className:"result-arrow"})]},_.page.slug))}),C.length>8&&r.jsx("div",{className:"search-results-footer",children:r.jsxs("span",{children:["Showing 8 of ",C.length," results. Browse all docs below."]})})]})]})}),r.jsxs("div",{className:"docs-mobile-nav",children:[r.jsx("button",{className:"mobile-menu-toggle",onClick:()=>u(!o),"aria-label":"Toggle documentation menu",children:r.jsx(Z,{name:"utility",size:20})}),o&&r.jsxs("div",{className:"mobile-nav-panel",children:[r.jsxs("div",{className:"mobile-nav-header",children:[r.jsx("h3",{children:"Documentation"}),r.jsx("button",{className:"close-menu-btn",onClick:()=>u(!1),"aria-label":"Close menu",children:r.jsx(Z,{name:"utility",size:16,className:"rotated"})})]}),r.jsx("div",{className:"mobile-nav-sections",children:sn.map(_=>r.jsxs("button",{className:`mobile-nav-item ${c===_.id?"active":""}`,onClick:()=>{j(_.id)},children:[r.jsx(Z,{name:_.icon,size:18}),r.jsx("span",{className:"mobile-section-label",children:_.label}),r.jsx("span",{className:"mobile-section-count",children:_.count})]},_.id))})]})]}),I.length>0&&!M&&r.jsxs("div",{className:"docs-tags-cloud",children:[r.jsxs("div",{className:"tags-cloud-title",children:[r.jsx(Z,{name:"utility",size:16}),r.jsx("span",{children:"Popular Topics"})]}),r.jsx("div",{className:"tags-cloud-list",children:I.slice(0,15).map(({tag:_,count:X})=>r.jsxs("button",{className:"tag-cloud-item",onClick:()=>B(_),style:{fontSize:`${.75+Math.min(X/4,1)}rem`},children:["#",_,r.jsx("span",{className:"tag-count",children:X})]},_))})]}),r.jsx("div",{className:"docs-category-filters",children:r.jsx(Zh,{selectedCategory:w.category,onSelectCategory:j,sections:sn})}),M&&r.jsxs("div",{className:"docs-results-header",children:[r.jsxs("div",{className:"results-info",children:[r.jsxs("span",{className:"results-count-large",children:[D," ",D===1?"article":"articles"]}),w.query&&r.jsxs("span",{className:"search-query-display",children:['for "',r.jsx("strong",{children:w.query}),'"']})]}),r.jsxs("button",{className:"clear-all-btn",onClick:()=>{b(),f("")},disabled:!M,children:[r.jsx(Z,{name:"utility",size:14}),"Clear all filters"]})]}),r.jsx("div",{className:"docs-content",children:M?r.jsx("div",{className:"search-results-view",children:Object.entries(Q).map(([_,X])=>{var me;return r.jsxs("section",{className:"results-category",children:[r.jsx("h2",{className:"category-title",children:((me=sn.find(je=>je.id===_))==null?void 0:me.label)||_}),r.jsx("div",{className:"category-results-grid",children:X.map(je=>r.jsx(io,{doc:je,variant:"highlighted"},je.page.slug))})]},_)})}):c?r.jsxs("div",{className:"category-view",children:[r.jsxs("div",{className:"category-header",children:[r.jsx("h2",{className:"category-page-title",children:((te=sn.find(_=>_.id===c))==null?void 0:te.label)||c}),r.jsx("p",{className:"category-description",children:(se=sn.find(_=>_.id===c))==null?void 0:se.description})]}),r.jsx("div",{className:"category-articles",children:Me.filter(_=>_.category===c).sort((_,X)=>_.order-X.order).map(_=>r.jsx(io,{doc:_},_.slug))})]}):r.jsx("div",{className:"all-categories-view",children:sn.map(_=>r.jsxs("section",{className:"docs-section",id:`section-${_.id}`,children:[r.jsxs("div",{className:"section-header",children:[r.jsx("div",{className:"section-icon",children:r.jsx(Z,{name:_.icon,size:28})}),r.jsxs("div",{className:"section-info",children:[r.jsx("h2",{className:"section-title",children:_.label}),r.jsx("p",{className:"section-description",children:_.description})]}),r.jsx("span",{className:"section-count",children:_.count})]}),r.jsx("div",{className:"section-articles",children:Me.filter(X=>X.category===_.id).sort((X,me)=>X.order-me.order).map(X=>r.jsx(io,{doc:X},X.slug))})]},_.id))})}),r.jsxs("div",{className:"docs-footer-note",children:[r.jsx(Z,{name:"book",size:20}),r.jsxs("div",{children:[r.jsx("strong",{children:"Want more detail?"}),r.jsxs("p",{children:["The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in the"," ",r.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"docs/"})," ","folder."]})]})]})]}),r.jsx(Kn,{})]})}function ap(){const o=Zs(),[u,c]=R.useState(null);R.useEffect(()=>{Pc().then(c).catch(()=>{})},[]);const f=[["spark","AI that remembers","Thoughtful conversation with a cozy personality and controls that respect your community."],["chart","A living economy","Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],["shield","Confident moderation","Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],["users","Community rituals","Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."]];return r.jsxs(r.Fragment,{children:[r.jsx(St,{page:"home"}),r.jsxs("main",{children:[r.jsxs("section",{className:"hero shell",children:[r.jsxs("div",{className:"hero-copy",children:[r.jsxs("div",{className:"eyebrow",children:[r.jsx("span",{className:"status-dot"})," Discord companion · online"]}),r.jsxs("h1",{children:["Useful tools for a ",r.jsx("em",{children:"better server."})]}),r.jsx("p",{children:"Niko handles the everyday work of running a Discord community, so your moderators can focus on the people in it."}),r.jsxs("div",{className:"hero-buttons",children:[r.jsxs("a",{className:"button button-primary",href:(o==null?void 0:o.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Invite Niko ",r.jsx(Z,{name:"arrow"})]}),r.jsx("a",{className:"button button-muted",href:"/commands",onClick:p=>{p.preventDefault(),he("/commands")},children:"Explore commands"})]}),r.jsxs("div",{className:"stats-strip",children:[r.jsxs("div",{children:[r.jsx("strong",{children:Ee(u==null?void 0:u.guild_count)}),r.jsx("span",{children:"servers"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:Ee(u==null?void 0:u.user_count)}),r.jsx("span",{children:"members"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:Ee(u==null?void 0:u.command_count)}),r.jsx("span",{children:"commands"})]})]})]}),r.jsx("div",{className:"hero-art","aria-label":"A preview of Niko's server workspace",children:r.jsxs("div",{className:"workspace-preview",children:[r.jsxs("div",{className:"workspace-preview-top",children:[r.jsxs("span",{className:"preview-dots",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"server workspace"}),r.jsxs("span",{className:"preview-status",children:[r.jsx("span",{className:"status-dot"})," live"]})]}),r.jsxs("div",{className:"preview-body",children:[r.jsxs("div",{className:"preview-sidebar",children:[r.jsx("span",{className:"preview-label",children:"NIKO"}),r.jsx("b",{children:"Overview"}),r.jsx("span",{children:"Economy"}),r.jsx("span",{children:"Leveling"}),r.jsx("span",{children:"Moderation"}),r.jsx("span",{children:"AI controls"})]}),r.jsxs("div",{className:"preview-main",children:[r.jsx("span",{className:"preview-label",children:"SERVER SNAPSHOT"}),r.jsx("strong",{children:"Everything in one place."}),r.jsxs("div",{className:"preview-stats",children:[r.jsxs("span",{children:[r.jsx("b",{children:Ee(u==null?void 0:u.user_count)}),r.jsx("small",{children:"members"})]}),r.jsxs("span",{children:[r.jsx("b",{children:Ee(u==null?void 0:u.command_count)}),r.jsx("small",{children:"commands"})]})]}),r.jsxs("div",{className:"preview-line",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]})]})]})]})})]}),r.jsxs("section",{className:"shell intro-section",children:[r.jsx("div",{className:"section-kicker",children:"Why Niko"}),r.jsxs("div",{className:"intro-grid",children:[r.jsxs("h2",{children:["The good kind of",r.jsx("br",{}),r.jsx("em",{children:"always-on."})]}),r.jsx("p",{children:"Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile."})]})]}),r.jsx("section",{className:"shell feature-grid",children:f.map(([p,S,w])=>r.jsxs("article",{className:"feature-card",children:[r.jsx("span",{className:"feature-icon",children:r.jsx(Z,{name:p})}),r.jsx("h3",{children:S}),r.jsx("p",{children:w}),r.jsxs("a",{href:"/docs",onClick:z=>{z.preventDefault(),he("/docs")},children:["Learn more ",r.jsx(Z,{name:"arrow"})]})]},S))}),r.jsxs("section",{className:"shell callout",children:[r.jsxs("div",{children:[r.jsx("div",{className:"section-kicker",children:"Ready when you are"}),r.jsxs("h2",{children:["A calmer, cleverer home",r.jsx("br",{}),"for your community."]})]}),r.jsxs("a",{className:"button button-primary",href:(o==null?void 0:o.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Bring Niko in ",r.jsx(Z,{name:"arrow"})]})]})]}),r.jsx(Kn,{})]})}const op=[{code:"USDT",label:"Tether"},{code:"ETH",label:"Ethereum"},{code:"BTC",label:"Bitcoin"},{code:"BNB",label:"BNB"},{code:"LTC",label:"Litecoin"},{code:"DOGE",label:"Dogecoin"},{code:"TRX",label:"TRON"},{code:"XMR",label:"Monero"}];function lp(){const u=new URLSearchParams(window.location.search).get("token")||"",[c,f]=R.useState("5"),[p,S]=R.useState("USDT"),[w,z]=R.useState(!1),[x,B]=R.useState(""),[b,C]=R.useState(null),[M,D]=R.useState(null),[I,F]=R.useState(!1);R.useEffect(()=>{u||F(!0)},[u]),R.useEffect(()=>{if(!(b!=null&&b.status_url)||b.paid)return;const W=setInterval(async()=>{try{const N=await tt(b.status_url);D(N),N.paid&&clearInterval(W)}catch{}},5e3);return()=>clearInterval(W)},[b]);const j=async W=>{W.preventDefault(),z(!0),B("");try{const N=await tt("/api/donations/invoice",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:u,amount:parseFloat(c),currency:p})});C(N),N.error&&(B(N.error),C(null))}catch(N){B(N instanceof Error?N.message:"Could not create invoice.")}finally{z(!1)}};return I?r.jsxs(r.Fragment,{children:[r.jsx(St,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Invalid donation link"}),r.jsxs("h1",{children:["This link is ",r.jsx("em",{children:"invalid."})]}),r.jsxs("p",{children:["The donation link is missing or has expired. Use the"," ",r.jsx("code",{children:"/donate"})," command in Discord to generate a new one."]}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>he("/"),children:"Return home"})]})})]}):M!=null&&M.paid?r.jsxs(r.Fragment,{children:[r.jsx(St,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"✓"}),r.jsx("div",{className:"eyebrow",children:"Payment confirmed"}),r.jsxs("h1",{children:["Thank you ",r.jsx("em",{children:"for supporting!"})]}),r.jsx("p",{children:"Your donation has been confirmed. You will receive the Supporter badge shortly."}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>he("/"),children:"Return home"})]})})]}):r.jsxs(r.Fragment,{children:[r.jsx(St,{page:"home"}),r.jsx("main",{className:"page-main",children:r.jsx("div",{className:"shell",children:r.jsxs("div",{className:"page-heading",style:{maxWidth:500,margin:"0 auto"},children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:15},children:"Support Niko"}),r.jsxs("h1",{children:["Keep Niko ",r.jsx("em",{children:"running."})]}),r.jsx("p",{style:{color:"var(--muted)",marginBottom:30},children:"Your donation helps cover hosting costs and keeps Niko running for all servers. Choose an amount and cryptocurrency below."}),b!=null&&b.pay_link?r.jsxs("div",{className:"dash-panel",style:{marginBottom:24},children:[r.jsx("div",{className:"panel-heading",children:r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Invoice created"}),r.jsx("h3",{children:"Complete your payment"})]})}),r.jsxs("p",{style:{color:"var(--muted)",fontSize:12,marginBottom:16},children:["Amount: ",r.jsxs("strong",{children:["$",parseFloat(c).toFixed(2)," USD"]})," in"," ",r.jsx("strong",{children:p})]}),r.jsxs("p",{style:{color:"var(--dim)",fontSize:10,marginBottom:16},children:["Track ID: ",r.jsx("code",{children:b.track_id})," · Expires in 60 minutes"]}),r.jsxs("a",{className:"button button-primary",href:b.pay_link,target:"_blank",rel:"noopener noreferrer",children:["Pay now ",r.jsx(Z,{name:"arrow"})]}),r.jsx("p",{style:{color:"var(--dim)",fontSize:10,marginTop:12},children:"Payment will be confirmed automatically once the transaction is processed on-chain."})]}):r.jsxs("form",{onSubmit:j,className:"dash-panel",style:{marginBottom:24},children:[r.jsxs("div",{className:"form-grid",children:[r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Amount (USD)"}),r.jsx("input",{type:"number",min:"1",max:"10000",step:"0.01",value:c,onChange:W=>f(W.target.value)}),r.jsx("small",{children:"Minimum $1.00, maximum $10,000.00"})]}),r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Cryptocurrency"}),r.jsx("select",{value:p,onChange:W=>S(W.target.value),children:op.map(W=>r.jsxs("option",{value:W.code,children:[W.label," (",W.code,")"]},W.code))})]})]}),x&&r.jsx("p",{className:"form-error",style:{marginTop:12},role:"alert",children:x}),r.jsx("div",{style:{marginTop:16},children:r.jsx("button",{className:"button button-primary",type:"submit",disabled:w,children:w?"Creating invoice…":"Create invoice"})})]}),r.jsxs("div",{className:"docs-footer-note",style:{marginTop:20},children:[r.jsx("strong",{children:"How it works"}),r.jsx("p",{children:'1. Choose an amount and currency above · 2. Click "Pay now" to open the payment page · 3. Send crypto to the displayed address · 4. Payment is confirmed automatically once processed on-chain'})]})]})})})]})}const up={privacy:{title:"Privacy policy",intro:"Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",sections:[["Information we use","User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature."],["How it is used","Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],["Storage and retention","Data is stored by the server hosting Niko in local JSON and SQLite files. Economy, leveling, and configuration data remain until removed. AI conversation history is limited and can be cleared with /clearhistory."],["Third-party services","When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Music and external lookup features may contact their respective services."],["Your choices","Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."]]},terms:{title:"Terms of service",intro:"By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",sections:[["Permitted use","Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],["Availability","Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],["Moderation","The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],["AI content","AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],["Virtual items","In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],["Contact","Questions or concerns can be sent through the Niko support server."]]}};function Tc({type:o}){const u=up[o];return r.jsxs(r.Fragment,{children:[r.jsx(St,{page:o}),r.jsxs("main",{className:"shell page-main legal-page",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Niko legal"}),r.jsx("h1",{children:u.title}),r.jsx("p",{children:u.intro}),r.jsx("small",{children:"Effective date: 1 January 2025"})]}),r.jsx("div",{className:"legal-copy",children:u.sections.map(([c,f])=>r.jsxs("section",{children:[r.jsx("h2",{children:c}),r.jsx("p",{children:f})]},c))})]}),r.jsx(Kn,{})]})}const cp=[{key:"txt",label:"TXT",icon:"📄"},{key:"html",label:"HTML",icon:"🌐"},{key:"csv",label:"CSV",icon:"📊"},{key:"json",label:"JSON",icon:"{ }"}];function dp({transcriptId:o}){const[u,c]=R.useState(null),[f,p]=R.useState(!0),[S,w]=R.useState("");R.useEffect(()=>{p(!0),w(""),fetch(`/api/transcript/${o}`).then(x=>{if(!x.ok)throw new Error("Transcript not found");return x.json()}).then(x=>{c(x),p(!1)}).catch(x=>{w(x.message||"Failed to load transcript"),p(!1)})},[o]);const z=x=>{window.open(`/api/transcript/${o}/download?format=${x}`,"_blank")};return f?r.jsx("div",{className:"page-main",children:r.jsx("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:r.jsx("div",{style:{color:"var(--muted)",fontSize:14},children:"Loading transcript…"})})}):S||!u?r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:[r.jsx("h2",{style:{marginBottom:12},children:"Transcript not found"}),r.jsx("p",{style:{color:"var(--muted)"},children:S||"This transcript doesn't exist or has been deleted."})]})}):r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{maxWidth:800},children:[r.jsx("div",{style:{background:"var(--surface)",border:"1px solid var(--line)",borderRadius:8,padding:24,marginBottom:20},children:r.jsxs("div",{style:{display:"flex",alignItems:"flex-start",justifyContent:"space-between",gap:16,flexWrap:"wrap"},children:[r.jsxs("div",{children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:8},children:"Ticket Transcript"}),r.jsxs("h1",{style:{fontSize:24,letterSpacing:"-0.04em",margin:0},children:["#",u.channel_name]}),r.jsxs("div",{style:{color:"var(--muted)",fontSize:13,marginTop:6},children:[u.category," · ",u.message_count," messages · ",u.created_at]})]}),r.jsx("div",{style:{display:"flex",gap:8,flexWrap:"wrap"},children:cp.map(x=>r.jsxs("button",{className:"button button-small button-muted",onClick:()=>z(x.key),style:{minWidth:70},children:[r.jsx("span",{children:x.icon}),r.jsx("span",{children:x.label})]},x.key))})]})}),r.jsxs("div",{style:{background:"#1e1f22",border:"1px solid #3f4147",borderRadius:8,overflow:"hidden"},children:[u.messages.map((x,B)=>r.jsxs("div",{style:{padding:"10px 16px",borderBottom:"1px solid #2b2d31",fontSize:14,lineHeight:1.6},children:[r.jsx("span",{style:{color:"#949ba4",fontSize:11,fontFamily:"monospace"},children:x.timestamp})," ",r.jsx("span",{style:{color:"#f2f3f5",fontWeight:600},children:x.author})," ",r.jsxs("span",{style:{color:"#949ba4",fontSize:11},children:["(",x.author_id,")"]}),":"," ",r.jsx("span",{style:{color:"#dbdee1"},children:x.content}),x.attachments&&x.attachments.length>0&&r.jsx("div",{style:{marginTop:4},children:x.attachments.map((b,C)=>r.jsx("a",{href:b,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",fontSize:12,textDecoration:"none"},children:"📎 Attachment"},C))})]},B)),u.messages.length===0&&r.jsx("div",{style:{padding:40,textAlign:"center",color:"#949ba4"},children:"No messages in this transcript."})]}),r.jsxs("div",{style:{marginTop:16,padding:"12px 0",textAlign:"center",color:"var(--dim)",fontSize:12},children:["Transcript ID: ",r.jsx("code",{style:{fontFamily:"monospace"},children:o})]})]})})}function mp(){const[o,u]=R.useState(vc);if(R.useEffect(()=>{const c=()=>u(vc());return window.addEventListener("popstate",c),()=>window.removeEventListener("popstate",c)},[]),o==="commands")return r.jsx(Mh,{});if(o==="docs-detail"){const c=window.location.pathname.split("/"),f=c[c.length-1];return r.jsx(sp,{slug:f})}if(o==="docs")return r.jsx(ip,{});if(o==="dashboard")return r.jsx(Yh,{});if(o==="privacy")return r.jsx(Tc,{type:"privacy"});if(o==="terms")return r.jsx(Tc,{type:"terms"});if(o==="donate")return r.jsx(lp,{});if(o==="transcript"){const f=window.location.pathname.split("/").filter(Boolean)[1]||"";return r.jsx(dp,{transcriptId:f})}return r.jsx(ap,{})}Vm.createRoot(document.getElementById("root")).render(r.jsx(R.StrictMode,{children:r.jsx(mp,{})}));
