var Dm=Object.defineProperty;var Am=(a,u,c)=>u in a?Dm(a,u,{enumerable:!0,configurable:!0,writable:!0,value:c}):a[u]=c;var ic=(a,u,c)=>Am(a,typeof u!="symbol"?u+"":u,c);(function(){const u=document.createElement("link").relList;if(u&&u.supports&&u.supports("modulepreload"))return;for(const f of document.querySelectorAll('link[rel="modulepreload"]'))p(f);new MutationObserver(f=>{for(const j of f)if(j.type==="childList")for(const w of j.addedNodes)w.tagName==="LINK"&&w.rel==="modulepreload"&&p(w)}).observe(document,{childList:!0,subtree:!0});function c(f){const j={};return f.integrity&&(j.integrity=f.integrity),f.referrerPolicy&&(j.referrerPolicy=f.referrerPolicy),f.crossOrigin==="use-credentials"?j.credentials="include":f.crossOrigin==="anonymous"?j.credentials="omit":j.credentials="same-origin",j}function p(f){if(f.ep)return;f.ep=!0;const j=c(f);fetch(f.href,j)}})();var Yo={exports:{}},Rr={},Jo={exports:{}},ne={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var oc;function Im(){if(oc)return ne;oc=1;var a=Symbol.for("react.element"),u=Symbol.for("react.portal"),c=Symbol.for("react.fragment"),p=Symbol.for("react.strict_mode"),f=Symbol.for("react.profiler"),j=Symbol.for("react.provider"),w=Symbol.for("react.context"),z=Symbol.for("react.forward_ref"),y=Symbol.for("react.suspense"),F=Symbol.for("react.memo"),N=Symbol.for("react.lazy"),T=Symbol.iterator;function D(g){return g===null||typeof g!="object"?null:(g=T&&g[T]||g["@@iterator"],typeof g=="function"?g:null)}var K={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},I=Object.assign,A={};function E(g,_,ee){this.props=g,this.context=_,this.refs=A,this.updater=ee||K}E.prototype.isReactComponent={},E.prototype.setState=function(g,_){if(typeof g!="object"&&typeof g!="function"&&g!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,g,_,"setState")},E.prototype.forceUpdate=function(g){this.updater.enqueueForceUpdate(this,g,"forceUpdate")};function U(){}U.prototype=E.prototype;function S(g,_,ee){this.props=g,this.context=_,this.refs=A,this.updater=ee||K}var re=S.prototype=new U;re.constructor=S,I(re,E.prototype),re.isPureReactComponent=!0;var se=Array.isArray,ie=Object.prototype.hasOwnProperty,M={current:null},Z={key:!0,ref:!0,__self:!0,__source:!0};function fe(g,_,ee){var te,ae={},le=null,he=null;if(_!=null)for(te in _.ref!==void 0&&(he=_.ref),_.key!==void 0&&(le=""+_.key),_)ie.call(_,te)&&!Z.hasOwnProperty(te)&&(ae[te]=_[te]);var ce=arguments.length-2;if(ce===1)ae.children=ee;else if(1<ce){for(var ye=Array(ce),nn=0;nn<ce;nn++)ye[nn]=arguments[nn+2];ae.children=ye}if(g&&g.defaultProps)for(te in ce=g.defaultProps,ce)ae[te]===void 0&&(ae[te]=ce[te]);return{$$typeof:a,type:g,key:le,ref:he,props:ae,_owner:M.current}}function Ee(g,_){return{$$typeof:a,type:g.type,key:_,ref:g.ref,props:g.props,_owner:g._owner}}function hn(g){return typeof g=="object"&&g!==null&&g.$$typeof===a}function ot(g){var _={"=":"=0",":":"=2"};return"$"+g.replace(/[=:]/g,function(ee){return _[ee]})}var Sn=/\/+/g;function en(g,_){return typeof g=="object"&&g!==null&&g.key!=null?ot(""+g.key):_.toString(36)}function pn(g,_,ee,te,ae){var le=typeof g;(le==="undefined"||le==="boolean")&&(g=null);var he=!1;if(g===null)he=!0;else switch(le){case"string":case"number":he=!0;break;case"object":switch(g.$$typeof){case a:case u:he=!0}}if(he)return he=g,ae=ae(he),g=te===""?"."+en(he,0):te,se(ae)?(ee="",g!=null&&(ee=g.replace(Sn,"$&/")+"/"),pn(ae,_,ee,"",function(nn){return nn})):ae!=null&&(hn(ae)&&(ae=Ee(ae,ee+(!ae.key||he&&he.key===ae.key?"":(""+ae.key).replace(Sn,"$&/")+"/")+g)),_.push(ae)),1;if(he=0,te=te===""?".":te+":",se(g))for(var ce=0;ce<g.length;ce++){le=g[ce];var ye=te+en(le,ce);he+=pn(le,_,ee,ye,ae)}else if(ye=D(g),typeof ye=="function")for(g=ye.call(g),ce=0;!(le=g.next()).done;)le=le.value,ye=te+en(le,ce++),he+=pn(le,_,ee,ye,ae);else if(le==="object")throw _=String(g),Error("Objects are not valid as a React child (found: "+(_==="[object Object]"?"object with keys {"+Object.keys(g).join(", ")+"}":_)+"). If you meant to render a collection of children, use an array instead.");return he}function Nn(g,_,ee){if(g==null)return g;var te=[],ae=0;return pn(g,te,"","",function(le){return _.call(ee,le,ae++)}),te}function $e(g){if(g._status===-1){var _=g._result;_=_(),_.then(function(ee){(g._status===0||g._status===-1)&&(g._status=1,g._result=ee)},function(ee){(g._status===0||g._status===-1)&&(g._status=2,g._result=ee)}),g._status===-1&&(g._status=0,g._result=_)}if(g._status===1)return g._result.default;throw g._result}var je={current:null},O={transition:null},q={ReactCurrentDispatcher:je,ReactCurrentBatchConfig:O,ReactCurrentOwner:M};function $(){throw Error("act(...) is not supported in production builds of React.")}return ne.Children={map:Nn,forEach:function(g,_,ee){Nn(g,function(){_.apply(this,arguments)},ee)},count:function(g){var _=0;return Nn(g,function(){_++}),_},toArray:function(g){return Nn(g,function(_){return _})||[]},only:function(g){if(!hn(g))throw Error("React.Children.only expected to receive a single React element child.");return g}},ne.Component=E,ne.Fragment=c,ne.Profiler=f,ne.PureComponent=S,ne.StrictMode=p,ne.Suspense=y,ne.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=q,ne.act=$,ne.cloneElement=function(g,_,ee){if(g==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+g+".");var te=I({},g.props),ae=g.key,le=g.ref,he=g._owner;if(_!=null){if(_.ref!==void 0&&(le=_.ref,he=M.current),_.key!==void 0&&(ae=""+_.key),g.type&&g.type.defaultProps)var ce=g.type.defaultProps;for(ye in _)ie.call(_,ye)&&!Z.hasOwnProperty(ye)&&(te[ye]=_[ye]===void 0&&ce!==void 0?ce[ye]:_[ye])}var ye=arguments.length-2;if(ye===1)te.children=ee;else if(1<ye){ce=Array(ye);for(var nn=0;nn<ye;nn++)ce[nn]=arguments[nn+2];te.children=ce}return{$$typeof:a,type:g.type,key:ae,ref:le,props:te,_owner:he}},ne.createContext=function(g){return g={$$typeof:w,_currentValue:g,_currentValue2:g,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},g.Provider={$$typeof:j,_context:g},g.Consumer=g},ne.createElement=fe,ne.createFactory=function(g){var _=fe.bind(null,g);return _.type=g,_},ne.createRef=function(){return{current:null}},ne.forwardRef=function(g){return{$$typeof:z,render:g}},ne.isValidElement=hn,ne.lazy=function(g){return{$$typeof:N,_payload:{_status:-1,_result:g},_init:$e}},ne.memo=function(g,_){return{$$typeof:F,type:g,compare:_===void 0?null:_}},ne.startTransition=function(g){var _=O.transition;O.transition={};try{g()}finally{O.transition=_}},ne.unstable_act=$,ne.useCallback=function(g,_){return je.current.useCallback(g,_)},ne.useContext=function(g){return je.current.useContext(g)},ne.useDebugValue=function(){},ne.useDeferredValue=function(g){return je.current.useDeferredValue(g)},ne.useEffect=function(g,_){return je.current.useEffect(g,_)},ne.useId=function(){return je.current.useId()},ne.useImperativeHandle=function(g,_,ee){return je.current.useImperativeHandle(g,_,ee)},ne.useInsertionEffect=function(g,_){return je.current.useInsertionEffect(g,_)},ne.useLayoutEffect=function(g,_){return je.current.useLayoutEffect(g,_)},ne.useMemo=function(g,_){return je.current.useMemo(g,_)},ne.useReducer=function(g,_,ee){return je.current.useReducer(g,_,ee)},ne.useRef=function(g){return je.current.useRef(g)},ne.useState=function(g){return je.current.useState(g)},ne.useSyncExternalStore=function(g,_,ee){return je.current.useSyncExternalStore(g,_,ee)},ne.useTransition=function(){return je.current.useTransition()},ne.version="18.3.1",ne}var ac;function ua(){return ac||(ac=1,Jo.exports=Im()),Jo.exports}/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var lc;function zm(){if(lc)return Rr;lc=1;var a=ua(),u=Symbol.for("react.element"),c=Symbol.for("react.fragment"),p=Object.prototype.hasOwnProperty,f=a.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,j={key:!0,ref:!0,__self:!0,__source:!0};function w(z,y,F){var N,T={},D=null,K=null;F!==void 0&&(D=""+F),y.key!==void 0&&(D=""+y.key),y.ref!==void 0&&(K=y.ref);for(N in y)p.call(y,N)&&!j.hasOwnProperty(N)&&(T[N]=y[N]);if(z&&z.defaultProps)for(N in y=z.defaultProps,y)T[N]===void 0&&(T[N]=y[N]);return{$$typeof:u,type:z,key:D,ref:K,props:T,_owner:f.current}}return Rr.Fragment=c,Rr.jsx=w,Rr.jsxs=w,Rr}var uc;function Fm(){return uc||(uc=1,Yo.exports=zm()),Yo.exports}var r=Fm(),R=ua(),Hs={},Zo={exports:{}},Xe={},ea={exports:{}},na={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var cc;function Om(){return cc||(cc=1,(function(a){function u(O,q){var $=O.length;O.push(q);e:for(;0<$;){var g=$-1>>>1,_=O[g];if(0<f(_,q))O[g]=q,O[$]=_,$=g;else break e}}function c(O){return O.length===0?null:O[0]}function p(O){if(O.length===0)return null;var q=O[0],$=O.pop();if($!==q){O[0]=$;e:for(var g=0,_=O.length,ee=_>>>1;g<ee;){var te=2*(g+1)-1,ae=O[te],le=te+1,he=O[le];if(0>f(ae,$))le<_&&0>f(he,ae)?(O[g]=he,O[le]=$,g=le):(O[g]=ae,O[te]=$,g=te);else if(le<_&&0>f(he,$))O[g]=he,O[le]=$,g=le;else break e}}return q}function f(O,q){var $=O.sortIndex-q.sortIndex;return $!==0?$:O.id-q.id}if(typeof performance=="object"&&typeof performance.now=="function"){var j=performance;a.unstable_now=function(){return j.now()}}else{var w=Date,z=w.now();a.unstable_now=function(){return w.now()-z}}var y=[],F=[],N=1,T=null,D=3,K=!1,I=!1,A=!1,E=typeof setTimeout=="function"?setTimeout:null,U=typeof clearTimeout=="function"?clearTimeout:null,S=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function re(O){for(var q=c(F);q!==null;){if(q.callback===null)p(F);else if(q.startTime<=O)p(F),q.sortIndex=q.expirationTime,u(y,q);else break;q=c(F)}}function se(O){if(A=!1,re(O),!I)if(c(y)!==null)I=!0,$e(ie);else{var q=c(F);q!==null&&je(se,q.startTime-O)}}function ie(O,q){I=!1,A&&(A=!1,U(fe),fe=-1),K=!0;var $=D;try{for(re(q),T=c(y);T!==null&&(!(T.expirationTime>q)||O&&!ot());){var g=T.callback;if(typeof g=="function"){T.callback=null,D=T.priorityLevel;var _=g(T.expirationTime<=q);q=a.unstable_now(),typeof _=="function"?T.callback=_:T===c(y)&&p(y),re(q)}else p(y);T=c(y)}if(T!==null)var ee=!0;else{var te=c(F);te!==null&&je(se,te.startTime-q),ee=!1}return ee}finally{T=null,D=$,K=!1}}var M=!1,Z=null,fe=-1,Ee=5,hn=-1;function ot(){return!(a.unstable_now()-hn<Ee)}function Sn(){if(Z!==null){var O=a.unstable_now();hn=O;var q=!0;try{q=Z(!0,O)}finally{q?en():(M=!1,Z=null)}}else M=!1}var en;if(typeof S=="function")en=function(){S(Sn)};else if(typeof MessageChannel<"u"){var pn=new MessageChannel,Nn=pn.port2;pn.port1.onmessage=Sn,en=function(){Nn.postMessage(null)}}else en=function(){E(Sn,0)};function $e(O){Z=O,M||(M=!0,en())}function je(O,q){fe=E(function(){O(a.unstable_now())},q)}a.unstable_IdlePriority=5,a.unstable_ImmediatePriority=1,a.unstable_LowPriority=4,a.unstable_NormalPriority=3,a.unstable_Profiling=null,a.unstable_UserBlockingPriority=2,a.unstable_cancelCallback=function(O){O.callback=null},a.unstable_continueExecution=function(){I||K||(I=!0,$e(ie))},a.unstable_forceFrameRate=function(O){0>O||125<O?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):Ee=0<O?Math.floor(1e3/O):5},a.unstable_getCurrentPriorityLevel=function(){return D},a.unstable_getFirstCallbackNode=function(){return c(y)},a.unstable_next=function(O){switch(D){case 1:case 2:case 3:var q=3;break;default:q=D}var $=D;D=q;try{return O()}finally{D=$}},a.unstable_pauseExecution=function(){},a.unstable_requestPaint=function(){},a.unstable_runWithPriority=function(O,q){switch(O){case 1:case 2:case 3:case 4:case 5:break;default:O=3}var $=D;D=O;try{return q()}finally{D=$}},a.unstable_scheduleCallback=function(O,q,$){var g=a.unstable_now();switch(typeof $=="object"&&$!==null?($=$.delay,$=typeof $=="number"&&0<$?g+$:g):$=g,O){case 1:var _=-1;break;case 2:_=250;break;case 5:_=1073741823;break;case 4:_=1e4;break;default:_=5e3}return _=$+_,O={id:N++,callback:q,priorityLevel:O,startTime:$,expirationTime:_,sortIndex:-1},$>g?(O.sortIndex=$,u(F,O),c(y)===null&&O===c(F)&&(A?(U(fe),fe=-1):A=!0,je(se,$-g))):(O.sortIndex=_,u(y,O),I||K||(I=!0,$e(ie))),O},a.unstable_shouldYield=ot,a.unstable_wrapCallback=function(O){var q=D;return function(){var $=D;D=q;try{return O.apply(this,arguments)}finally{D=$}}}})(na)),na}var dc;function Bm(){return dc||(dc=1,ea.exports=Om()),ea.exports}/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var mc;function Um(){if(mc)return Xe;mc=1;var a=ua(),u=Bm();function c(e){for(var n="https://reactjs.org/docs/error-decoder.html?invariant="+e,t=1;t<arguments.length;t++)n+="&args[]="+encodeURIComponent(arguments[t]);return"Minified React error #"+e+"; visit "+n+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var p=new Set,f={};function j(e,n){w(e,n),w(e+"Capture",n)}function w(e,n){for(f[e]=n,e=0;e<n.length;e++)p.add(n[e])}var z=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),y=Object.prototype.hasOwnProperty,F=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,N={},T={};function D(e){return y.call(T,e)?!0:y.call(N,e)?!1:F.test(e)?T[e]=!0:(N[e]=!0,!1)}function K(e,n,t,s){if(t!==null&&t.type===0)return!1;switch(typeof n){case"function":case"symbol":return!0;case"boolean":return s?!1:t!==null?!t.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function I(e,n,t,s){if(n===null||typeof n>"u"||K(e,n,t,s))return!0;if(s)return!1;if(t!==null)switch(t.type){case 3:return!n;case 4:return n===!1;case 5:return isNaN(n);case 6:return isNaN(n)||1>n}return!1}function A(e,n,t,s,i,o,l){this.acceptsBooleans=n===2||n===3||n===4,this.attributeName=s,this.attributeNamespace=i,this.mustUseProperty=t,this.propertyName=e,this.type=n,this.sanitizeURL=o,this.removeEmptyString=l}var E={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){E[e]=new A(e,0,!1,e,null,!1,!1)}),[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var n=e[0];E[n]=new A(n,1,!1,e[1],null,!1,!1)}),["contentEditable","draggable","spellCheck","value"].forEach(function(e){E[e]=new A(e,2,!1,e.toLowerCase(),null,!1,!1)}),["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){E[e]=new A(e,2,!1,e,null,!1,!1)}),"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){E[e]=new A(e,3,!1,e.toLowerCase(),null,!1,!1)}),["checked","multiple","muted","selected"].forEach(function(e){E[e]=new A(e,3,!0,e,null,!1,!1)}),["capture","download"].forEach(function(e){E[e]=new A(e,4,!1,e,null,!1,!1)}),["cols","rows","size","span"].forEach(function(e){E[e]=new A(e,6,!1,e,null,!1,!1)}),["rowSpan","start"].forEach(function(e){E[e]=new A(e,5,!1,e.toLowerCase(),null,!1,!1)});var U=/[\-:]([a-z])/g;function S(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var n=e.replace(U,S);E[n]=new A(n,1,!1,e,null,!1,!1)}),"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var n=e.replace(U,S);E[n]=new A(n,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)}),["xml:base","xml:lang","xml:space"].forEach(function(e){var n=e.replace(U,S);E[n]=new A(n,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)}),["tabIndex","crossOrigin"].forEach(function(e){E[e]=new A(e,1,!1,e.toLowerCase(),null,!1,!1)}),E.xlinkHref=new A("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1),["src","href","action","formAction"].forEach(function(e){E[e]=new A(e,1,!1,e.toLowerCase(),null,!0,!0)});function re(e,n,t,s){var i=E.hasOwnProperty(n)?E[n]:null;(i!==null?i.type!==0:s||!(2<n.length)||n[0]!=="o"&&n[0]!=="O"||n[1]!=="n"&&n[1]!=="N")&&(I(n,t,i,s)&&(t=null),s||i===null?D(n)&&(t===null?e.removeAttribute(n):e.setAttribute(n,""+t)):i.mustUseProperty?e[i.propertyName]=t===null?i.type===3?!1:"":t:(n=i.attributeName,s=i.attributeNamespace,t===null?e.removeAttribute(n):(i=i.type,t=i===3||i===4&&t===!0?"":""+t,s?e.setAttributeNS(s,n,t):e.setAttribute(n,t))))}var se=a.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,ie=Symbol.for("react.element"),M=Symbol.for("react.portal"),Z=Symbol.for("react.fragment"),fe=Symbol.for("react.strict_mode"),Ee=Symbol.for("react.profiler"),hn=Symbol.for("react.provider"),ot=Symbol.for("react.context"),Sn=Symbol.for("react.forward_ref"),en=Symbol.for("react.suspense"),pn=Symbol.for("react.suspense_list"),Nn=Symbol.for("react.memo"),$e=Symbol.for("react.lazy"),je=Symbol.for("react.offscreen"),O=Symbol.iterator;function q(e){return e===null||typeof e!="object"?null:(e=O&&e[O]||e["@@iterator"],typeof e=="function"?e:null)}var $=Object.assign,g;function _(e){if(g===void 0)try{throw Error()}catch(t){var n=t.stack.trim().match(/\n( *(at )?)/);g=n&&n[1]||""}return`
`+g+e}var ee=!1;function te(e,n){if(!e||ee)return"";ee=!0;var t=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(n)if(n=function(){throw Error()},Object.defineProperty(n.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(n,[])}catch(k){var s=k}Reflect.construct(e,[],n)}else{try{n.call()}catch(k){s=k}e.call(n.prototype)}else{try{throw Error()}catch(k){s=k}e()}}catch(k){if(k&&s&&typeof k.stack=="string"){for(var i=k.stack.split(`
`),o=s.stack.split(`
`),l=i.length-1,d=o.length-1;1<=l&&0<=d&&i[l]!==o[d];)d--;for(;1<=l&&0<=d;l--,d--)if(i[l]!==o[d]){if(l!==1||d!==1)do if(l--,d--,0>d||i[l]!==o[d]){var m=`
`+i[l].replace(" at new "," at ");return e.displayName&&m.includes("<anonymous>")&&(m=m.replace("<anonymous>",e.displayName)),m}while(1<=l&&0<=d);break}}}finally{ee=!1,Error.prepareStackTrace=t}return(e=e?e.displayName||e.name:"")?_(e):""}function ae(e){switch(e.tag){case 5:return _(e.type);case 16:return _("Lazy");case 13:return _("Suspense");case 19:return _("SuspenseList");case 0:case 2:case 15:return e=te(e.type,!1),e;case 11:return e=te(e.type.render,!1),e;case 1:return e=te(e.type,!0),e;default:return""}}function le(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case Z:return"Fragment";case M:return"Portal";case Ee:return"Profiler";case fe:return"StrictMode";case en:return"Suspense";case pn:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case ot:return(e.displayName||"Context")+".Consumer";case hn:return(e._context.displayName||"Context")+".Provider";case Sn:var n=e.render;return e=e.displayName,e||(e=n.displayName||n.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case Nn:return n=e.displayName||null,n!==null?n:le(e.type)||"Memo";case $e:n=e._payload,e=e._init;try{return le(e(n))}catch{}}return null}function he(e){var n=e.type;switch(e.tag){case 24:return"Cache";case 9:return(n.displayName||"Context")+".Consumer";case 10:return(n._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=n.render,e=e.displayName||e.name||"",n.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return n;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return le(n);case 8:return n===fe?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof n=="function")return n.displayName||n.name||null;if(typeof n=="string")return n}return null}function ce(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function ye(e){var n=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(n==="checkbox"||n==="radio")}function nn(e){var n=ye(e)?"checked":"value",t=Object.getOwnPropertyDescriptor(e.constructor.prototype,n),s=""+e[n];if(!e.hasOwnProperty(n)&&typeof t<"u"&&typeof t.get=="function"&&typeof t.set=="function"){var i=t.get,o=t.set;return Object.defineProperty(e,n,{configurable:!0,get:function(){return i.call(this)},set:function(l){s=""+l,o.call(this,l)}}),Object.defineProperty(e,n,{enumerable:t.enumerable}),{getValue:function(){return s},setValue:function(l){s=""+l},stopTracking:function(){e._valueTracker=null,delete e[n]}}}}function Ar(e){e._valueTracker||(e._valueTracker=nn(e))}function da(e){if(!e)return!1;var n=e._valueTracker;if(!n)return!0;var t=n.getValue(),s="";return e&&(s=ye(e)?e.checked?"true":"false":e.value),e=s,e!==t?(n.setValue(e),!0):!1}function Ir(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function ri(e,n){var t=n.checked;return $({},n,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:t??e._wrapperState.initialChecked})}function ma(e,n){var t=n.defaultValue==null?"":n.defaultValue,s=n.checked!=null?n.checked:n.defaultChecked;t=ce(n.value!=null?n.value:t),e._wrapperState={initialChecked:s,initialValue:t,controlled:n.type==="checkbox"||n.type==="radio"?n.checked!=null:n.value!=null}}function ha(e,n){n=n.checked,n!=null&&re(e,"checked",n,!1)}function si(e,n){ha(e,n);var t=ce(n.value),s=n.type;if(t!=null)s==="number"?(t===0&&e.value===""||e.value!=t)&&(e.value=""+t):e.value!==""+t&&(e.value=""+t);else if(s==="submit"||s==="reset"){e.removeAttribute("value");return}n.hasOwnProperty("value")?ii(e,n.type,t):n.hasOwnProperty("defaultValue")&&ii(e,n.type,ce(n.defaultValue)),n.checked==null&&n.defaultChecked!=null&&(e.defaultChecked=!!n.defaultChecked)}function pa(e,n,t){if(n.hasOwnProperty("value")||n.hasOwnProperty("defaultValue")){var s=n.type;if(!(s!=="submit"&&s!=="reset"||n.value!==void 0&&n.value!==null))return;n=""+e._wrapperState.initialValue,t||n===e.value||(e.value=n),e.defaultValue=n}t=e.name,t!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,t!==""&&(e.name=t)}function ii(e,n,t){(n!=="number"||Ir(e.ownerDocument)!==e)&&(t==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+t&&(e.defaultValue=""+t))}var Qt=Array.isArray;function jt(e,n,t,s){if(e=e.options,n){n={};for(var i=0;i<t.length;i++)n["$"+t[i]]=!0;for(t=0;t<e.length;t++)i=n.hasOwnProperty("$"+e[t].value),e[t].selected!==i&&(e[t].selected=i),i&&s&&(e[t].defaultSelected=!0)}else{for(t=""+ce(t),n=null,i=0;i<e.length;i++){if(e[i].value===t){e[i].selected=!0,s&&(e[i].defaultSelected=!0);return}n!==null||e[i].disabled||(n=e[i])}n!==null&&(n.selected=!0)}}function oi(e,n){if(n.dangerouslySetInnerHTML!=null)throw Error(c(91));return $({},n,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function fa(e,n){var t=n.value;if(t==null){if(t=n.children,n=n.defaultValue,t!=null){if(n!=null)throw Error(c(92));if(Qt(t)){if(1<t.length)throw Error(c(93));t=t[0]}n=t}n==null&&(n=""),t=n}e._wrapperState={initialValue:ce(t)}}function ga(e,n){var t=ce(n.value),s=ce(n.defaultValue);t!=null&&(t=""+t,t!==e.value&&(e.value=t),n.defaultValue==null&&e.defaultValue!==t&&(e.defaultValue=t)),s!=null&&(e.defaultValue=""+s)}function va(e){var n=e.textContent;n===e._wrapperState.initialValue&&n!==""&&n!==null&&(e.value=n)}function ya(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function ai(e,n){return e==null||e==="http://www.w3.org/1999/xhtml"?ya(n):e==="http://www.w3.org/2000/svg"&&n==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var zr,xa=(function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(n,t,s,i){MSApp.execUnsafeLocalFunction(function(){return e(n,t,s,i)})}:e})(function(e,n){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=n;else{for(zr=zr||document.createElement("div"),zr.innerHTML="<svg>"+n.valueOf().toString()+"</svg>",n=zr.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;n.firstChild;)e.appendChild(n.firstChild)}});function Xt(e,n){if(n){var t=e.firstChild;if(t&&t===e.lastChild&&t.nodeType===3){t.nodeValue=n;return}}e.textContent=n}var qt={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},Fc=["Webkit","ms","Moz","O"];Object.keys(qt).forEach(function(e){Fc.forEach(function(n){n=n+e.charAt(0).toUpperCase()+e.substring(1),qt[n]=qt[e]})});function ka(e,n,t){return n==null||typeof n=="boolean"||n===""?"":t||typeof n!="number"||n===0||qt.hasOwnProperty(e)&&qt[e]?(""+n).trim():n+"px"}function wa(e,n){e=e.style;for(var t in n)if(n.hasOwnProperty(t)){var s=t.indexOf("--")===0,i=ka(t,n[t],s);t==="float"&&(t="cssFloat"),s?e.setProperty(t,i):e[t]=i}}var Oc=$({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function li(e,n){if(n){if(Oc[e]&&(n.children!=null||n.dangerouslySetInnerHTML!=null))throw Error(c(137,e));if(n.dangerouslySetInnerHTML!=null){if(n.children!=null)throw Error(c(60));if(typeof n.dangerouslySetInnerHTML!="object"||!("__html"in n.dangerouslySetInnerHTML))throw Error(c(61))}if(n.style!=null&&typeof n.style!="object")throw Error(c(62))}}function ui(e,n){if(e.indexOf("-")===-1)return typeof n.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var ci=null;function di(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var mi=null,St=null,Nt=null;function ja(e){if(e=yr(e)){if(typeof mi!="function")throw Error(c(280));var n=e.stateNode;n&&(n=os(n),mi(e.stateNode,e.type,n))}}function Sa(e){St?Nt?Nt.push(e):Nt=[e]:St=e}function Na(){if(St){var e=St,n=Nt;if(Nt=St=null,ja(e),n)for(e=0;e<n.length;e++)ja(n[e])}}function Ca(e,n){return e(n)}function _a(){}var hi=!1;function ba(e,n,t){if(hi)return e(n,t);hi=!0;try{return Ca(e,n,t)}finally{hi=!1,(St!==null||Nt!==null)&&(_a(),Na())}}function Yt(e,n){var t=e.stateNode;if(t===null)return null;var s=os(t);if(s===null)return null;t=s[n];e:switch(n){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(s=!s.disabled)||(e=e.type,s=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!s;break e;default:e=!1}if(e)return null;if(t&&typeof t!="function")throw Error(c(231,n,typeof t));return t}var pi=!1;if(z)try{var Jt={};Object.defineProperty(Jt,"passive",{get:function(){pi=!0}}),window.addEventListener("test",Jt,Jt),window.removeEventListener("test",Jt,Jt)}catch{pi=!1}function Bc(e,n,t,s,i,o,l,d,m){var k=Array.prototype.slice.call(arguments,3);try{n.apply(t,k)}catch(b){this.onError(b)}}var Zt=!1,Fr=null,Or=!1,fi=null,Uc={onError:function(e){Zt=!0,Fr=e}};function Wc(e,n,t,s,i,o,l,d,m){Zt=!1,Fr=null,Bc.apply(Uc,arguments)}function $c(e,n,t,s,i,o,l,d,m){if(Wc.apply(this,arguments),Zt){if(Zt){var k=Fr;Zt=!1,Fr=null}else throw Error(c(198));Or||(Or=!0,fi=k)}}function at(e){var n=e,t=e;if(e.alternate)for(;n.return;)n=n.return;else{e=n;do n=e,(n.flags&4098)!==0&&(t=n.return),e=n.return;while(e)}return n.tag===3?t:null}function Ea(e){if(e.tag===13){var n=e.memoizedState;if(n===null&&(e=e.alternate,e!==null&&(n=e.memoizedState)),n!==null)return n.dehydrated}return null}function Pa(e){if(at(e)!==e)throw Error(c(188))}function Vc(e){var n=e.alternate;if(!n){if(n=at(e),n===null)throw Error(c(188));return n!==e?null:e}for(var t=e,s=n;;){var i=t.return;if(i===null)break;var o=i.alternate;if(o===null){if(s=i.return,s!==null){t=s;continue}break}if(i.child===o.child){for(o=i.child;o;){if(o===t)return Pa(i),e;if(o===s)return Pa(i),n;o=o.sibling}throw Error(c(188))}if(t.return!==s.return)t=i,s=o;else{for(var l=!1,d=i.child;d;){if(d===t){l=!0,t=i,s=o;break}if(d===s){l=!0,s=i,t=o;break}d=d.sibling}if(!l){for(d=o.child;d;){if(d===t){l=!0,t=o,s=i;break}if(d===s){l=!0,s=o,t=i;break}d=d.sibling}if(!l)throw Error(c(189))}}if(t.alternate!==s)throw Error(c(190))}if(t.tag!==3)throw Error(c(188));return t.stateNode.current===t?e:n}function Ta(e){return e=Vc(e),e!==null?Ma(e):null}function Ma(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var n=Ma(e);if(n!==null)return n;e=e.sibling}return null}var La=u.unstable_scheduleCallback,Ra=u.unstable_cancelCallback,Hc=u.unstable_shouldYield,Gc=u.unstable_requestPaint,Ne=u.unstable_now,Kc=u.unstable_getCurrentPriorityLevel,gi=u.unstable_ImmediatePriority,Da=u.unstable_UserBlockingPriority,Br=u.unstable_NormalPriority,Qc=u.unstable_LowPriority,Aa=u.unstable_IdlePriority,Ur=null,Cn=null;function Xc(e){if(Cn&&typeof Cn.onCommitFiberRoot=="function")try{Cn.onCommitFiberRoot(Ur,e,void 0,(e.current.flags&128)===128)}catch{}}var fn=Math.clz32?Math.clz32:Jc,qc=Math.log,Yc=Math.LN2;function Jc(e){return e>>>=0,e===0?32:31-(qc(e)/Yc|0)|0}var Wr=64,$r=4194304;function er(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function Vr(e,n){var t=e.pendingLanes;if(t===0)return 0;var s=0,i=e.suspendedLanes,o=e.pingedLanes,l=t&268435455;if(l!==0){var d=l&~i;d!==0?s=er(d):(o&=l,o!==0&&(s=er(o)))}else l=t&~i,l!==0?s=er(l):o!==0&&(s=er(o));if(s===0)return 0;if(n!==0&&n!==s&&(n&i)===0&&(i=s&-s,o=n&-n,i>=o||i===16&&(o&4194240)!==0))return n;if((s&4)!==0&&(s|=t&16),n=e.entangledLanes,n!==0)for(e=e.entanglements,n&=s;0<n;)t=31-fn(n),i=1<<t,s|=e[t],n&=~i;return s}function Zc(e,n){switch(e){case 1:case 2:case 4:return n+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return n+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function ed(e,n){for(var t=e.suspendedLanes,s=e.pingedLanes,i=e.expirationTimes,o=e.pendingLanes;0<o;){var l=31-fn(o),d=1<<l,m=i[l];m===-1?((d&t)===0||(d&s)!==0)&&(i[l]=Zc(d,n)):m<=n&&(e.expiredLanes|=d),o&=~d}}function vi(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function Ia(){var e=Wr;return Wr<<=1,(Wr&4194240)===0&&(Wr=64),e}function yi(e){for(var n=[],t=0;31>t;t++)n.push(e);return n}function nr(e,n,t){e.pendingLanes|=n,n!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,n=31-fn(n),e[n]=t}function nd(e,n){var t=e.pendingLanes&~n;e.pendingLanes=n,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=n,e.mutableReadLanes&=n,e.entangledLanes&=n,n=e.entanglements;var s=e.eventTimes;for(e=e.expirationTimes;0<t;){var i=31-fn(t),o=1<<i;n[i]=0,s[i]=-1,e[i]=-1,t&=~o}}function xi(e,n){var t=e.entangledLanes|=n;for(e=e.entanglements;t;){var s=31-fn(t),i=1<<s;i&n|e[s]&n&&(e[s]|=n),t&=~i}}var de=0;function za(e){return e&=-e,1<e?4<e?(e&268435455)!==0?16:536870912:4:1}var Fa,ki,Oa,Ba,Ua,wi=!1,Hr=[],On=null,Bn=null,Un=null,tr=new Map,rr=new Map,Wn=[],td="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function Wa(e,n){switch(e){case"focusin":case"focusout":On=null;break;case"dragenter":case"dragleave":Bn=null;break;case"mouseover":case"mouseout":Un=null;break;case"pointerover":case"pointerout":tr.delete(n.pointerId);break;case"gotpointercapture":case"lostpointercapture":rr.delete(n.pointerId)}}function sr(e,n,t,s,i,o){return e===null||e.nativeEvent!==o?(e={blockedOn:n,domEventName:t,eventSystemFlags:s,nativeEvent:o,targetContainers:[i]},n!==null&&(n=yr(n),n!==null&&ki(n)),e):(e.eventSystemFlags|=s,n=e.targetContainers,i!==null&&n.indexOf(i)===-1&&n.push(i),e)}function rd(e,n,t,s,i){switch(n){case"focusin":return On=sr(On,e,n,t,s,i),!0;case"dragenter":return Bn=sr(Bn,e,n,t,s,i),!0;case"mouseover":return Un=sr(Un,e,n,t,s,i),!0;case"pointerover":var o=i.pointerId;return tr.set(o,sr(tr.get(o)||null,e,n,t,s,i)),!0;case"gotpointercapture":return o=i.pointerId,rr.set(o,sr(rr.get(o)||null,e,n,t,s,i)),!0}return!1}function $a(e){var n=lt(e.target);if(n!==null){var t=at(n);if(t!==null){if(n=t.tag,n===13){if(n=Ea(t),n!==null){e.blockedOn=n,Ua(e.priority,function(){Oa(t)});return}}else if(n===3&&t.stateNode.current.memoizedState.isDehydrated){e.blockedOn=t.tag===3?t.stateNode.containerInfo:null;return}}}e.blockedOn=null}function Gr(e){if(e.blockedOn!==null)return!1;for(var n=e.targetContainers;0<n.length;){var t=Si(e.domEventName,e.eventSystemFlags,n[0],e.nativeEvent);if(t===null){t=e.nativeEvent;var s=new t.constructor(t.type,t);ci=s,t.target.dispatchEvent(s),ci=null}else return n=yr(t),n!==null&&ki(n),e.blockedOn=t,!1;n.shift()}return!0}function Va(e,n,t){Gr(e)&&t.delete(n)}function sd(){wi=!1,On!==null&&Gr(On)&&(On=null),Bn!==null&&Gr(Bn)&&(Bn=null),Un!==null&&Gr(Un)&&(Un=null),tr.forEach(Va),rr.forEach(Va)}function ir(e,n){e.blockedOn===n&&(e.blockedOn=null,wi||(wi=!0,u.unstable_scheduleCallback(u.unstable_NormalPriority,sd)))}function or(e){function n(i){return ir(i,e)}if(0<Hr.length){ir(Hr[0],e);for(var t=1;t<Hr.length;t++){var s=Hr[t];s.blockedOn===e&&(s.blockedOn=null)}}for(On!==null&&ir(On,e),Bn!==null&&ir(Bn,e),Un!==null&&ir(Un,e),tr.forEach(n),rr.forEach(n),t=0;t<Wn.length;t++)s=Wn[t],s.blockedOn===e&&(s.blockedOn=null);for(;0<Wn.length&&(t=Wn[0],t.blockedOn===null);)$a(t),t.blockedOn===null&&Wn.shift()}var Ct=se.ReactCurrentBatchConfig,Kr=!0;function id(e,n,t,s){var i=de,o=Ct.transition;Ct.transition=null;try{de=1,ji(e,n,t,s)}finally{de=i,Ct.transition=o}}function od(e,n,t,s){var i=de,o=Ct.transition;Ct.transition=null;try{de=4,ji(e,n,t,s)}finally{de=i,Ct.transition=o}}function ji(e,n,t,s){if(Kr){var i=Si(e,n,t,s);if(i===null)Bi(e,n,s,Qr,t),Wa(e,s);else if(rd(i,e,n,t,s))s.stopPropagation();else if(Wa(e,s),n&4&&-1<td.indexOf(e)){for(;i!==null;){var o=yr(i);if(o!==null&&Fa(o),o=Si(e,n,t,s),o===null&&Bi(e,n,s,Qr,t),o===i)break;i=o}i!==null&&s.stopPropagation()}else Bi(e,n,s,null,t)}}var Qr=null;function Si(e,n,t,s){if(Qr=null,e=di(s),e=lt(e),e!==null)if(n=at(e),n===null)e=null;else if(t=n.tag,t===13){if(e=Ea(n),e!==null)return e;e=null}else if(t===3){if(n.stateNode.current.memoizedState.isDehydrated)return n.tag===3?n.stateNode.containerInfo:null;e=null}else n!==e&&(e=null);return Qr=e,null}function Ha(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(Kc()){case gi:return 1;case Da:return 4;case Br:case Qc:return 16;case Aa:return 536870912;default:return 16}default:return 16}}var $n=null,Ni=null,Xr=null;function Ga(){if(Xr)return Xr;var e,n=Ni,t=n.length,s,i="value"in $n?$n.value:$n.textContent,o=i.length;for(e=0;e<t&&n[e]===i[e];e++);var l=t-e;for(s=1;s<=l&&n[t-s]===i[o-s];s++);return Xr=i.slice(e,1<s?1-s:void 0)}function qr(e){var n=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&n===13&&(e=13)):e=n,e===10&&(e=13),32<=e||e===13?e:0}function Yr(){return!0}function Ka(){return!1}function tn(e){function n(t,s,i,o,l){this._reactName=t,this._targetInst=i,this.type=s,this.nativeEvent=o,this.target=l,this.currentTarget=null;for(var d in e)e.hasOwnProperty(d)&&(t=e[d],this[d]=t?t(o):o[d]);return this.isDefaultPrevented=(o.defaultPrevented!=null?o.defaultPrevented:o.returnValue===!1)?Yr:Ka,this.isPropagationStopped=Ka,this}return $(n.prototype,{preventDefault:function(){this.defaultPrevented=!0;var t=this.nativeEvent;t&&(t.preventDefault?t.preventDefault():typeof t.returnValue!="unknown"&&(t.returnValue=!1),this.isDefaultPrevented=Yr)},stopPropagation:function(){var t=this.nativeEvent;t&&(t.stopPropagation?t.stopPropagation():typeof t.cancelBubble!="unknown"&&(t.cancelBubble=!0),this.isPropagationStopped=Yr)},persist:function(){},isPersistent:Yr}),n}var _t={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},Ci=tn(_t),ar=$({},_t,{view:0,detail:0}),ad=tn(ar),_i,bi,lr,Jr=$({},ar,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:Pi,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==lr&&(lr&&e.type==="mousemove"?(_i=e.screenX-lr.screenX,bi=e.screenY-lr.screenY):bi=_i=0,lr=e),_i)},movementY:function(e){return"movementY"in e?e.movementY:bi}}),Qa=tn(Jr),ld=$({},Jr,{dataTransfer:0}),ud=tn(ld),cd=$({},ar,{relatedTarget:0}),Ei=tn(cd),dd=$({},_t,{animationName:0,elapsedTime:0,pseudoElement:0}),md=tn(dd),hd=$({},_t,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),pd=tn(hd),fd=$({},_t,{data:0}),Xa=tn(fd),gd={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},vd={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},yd={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function xd(e){var n=this.nativeEvent;return n.getModifierState?n.getModifierState(e):(e=yd[e])?!!n[e]:!1}function Pi(){return xd}var kd=$({},ar,{key:function(e){if(e.key){var n=gd[e.key]||e.key;if(n!=="Unidentified")return n}return e.type==="keypress"?(e=qr(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?vd[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:Pi,charCode:function(e){return e.type==="keypress"?qr(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?qr(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),wd=tn(kd),jd=$({},Jr,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),qa=tn(jd),Sd=$({},ar,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:Pi}),Nd=tn(Sd),Cd=$({},_t,{propertyName:0,elapsedTime:0,pseudoElement:0}),_d=tn(Cd),bd=$({},Jr,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),Ed=tn(bd),Pd=[9,13,27,32],Ti=z&&"CompositionEvent"in window,ur=null;z&&"documentMode"in document&&(ur=document.documentMode);var Td=z&&"TextEvent"in window&&!ur,Ya=z&&(!Ti||ur&&8<ur&&11>=ur),Ja=" ",Za=!1;function el(e,n){switch(e){case"keyup":return Pd.indexOf(n.keyCode)!==-1;case"keydown":return n.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function nl(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var bt=!1;function Md(e,n){switch(e){case"compositionend":return nl(n);case"keypress":return n.which!==32?null:(Za=!0,Ja);case"textInput":return e=n.data,e===Ja&&Za?null:e;default:return null}}function Ld(e,n){if(bt)return e==="compositionend"||!Ti&&el(e,n)?(e=Ga(),Xr=Ni=$n=null,bt=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(n.ctrlKey||n.altKey||n.metaKey)||n.ctrlKey&&n.altKey){if(n.char&&1<n.char.length)return n.char;if(n.which)return String.fromCharCode(n.which)}return null;case"compositionend":return Ya&&n.locale!=="ko"?null:n.data;default:return null}}var Rd={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function tl(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n==="input"?!!Rd[e.type]:n==="textarea"}function rl(e,n,t,s){Sa(s),n=rs(n,"onChange"),0<n.length&&(t=new Ci("onChange","change",null,t,s),e.push({event:t,listeners:n}))}var cr=null,dr=null;function Dd(e){wl(e,0)}function Zr(e){var n=Lt(e);if(da(n))return e}function Ad(e,n){if(e==="change")return n}var sl=!1;if(z){var Mi;if(z){var Li="oninput"in document;if(!Li){var il=document.createElement("div");il.setAttribute("oninput","return;"),Li=typeof il.oninput=="function"}Mi=Li}else Mi=!1;sl=Mi&&(!document.documentMode||9<document.documentMode)}function ol(){cr&&(cr.detachEvent("onpropertychange",al),dr=cr=null)}function al(e){if(e.propertyName==="value"&&Zr(dr)){var n=[];rl(n,dr,e,di(e)),ba(Dd,n)}}function Id(e,n,t){e==="focusin"?(ol(),cr=n,dr=t,cr.attachEvent("onpropertychange",al)):e==="focusout"&&ol()}function zd(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return Zr(dr)}function Fd(e,n){if(e==="click")return Zr(n)}function Od(e,n){if(e==="input"||e==="change")return Zr(n)}function Bd(e,n){return e===n&&(e!==0||1/e===1/n)||e!==e&&n!==n}var gn=typeof Object.is=="function"?Object.is:Bd;function mr(e,n){if(gn(e,n))return!0;if(typeof e!="object"||e===null||typeof n!="object"||n===null)return!1;var t=Object.keys(e),s=Object.keys(n);if(t.length!==s.length)return!1;for(s=0;s<t.length;s++){var i=t[s];if(!y.call(n,i)||!gn(e[i],n[i]))return!1}return!0}function ll(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function ul(e,n){var t=ll(e);e=0;for(var s;t;){if(t.nodeType===3){if(s=e+t.textContent.length,e<=n&&s>=n)return{node:t,offset:n-e};e=s}e:{for(;t;){if(t.nextSibling){t=t.nextSibling;break e}t=t.parentNode}t=void 0}t=ll(t)}}function cl(e,n){return e&&n?e===n?!0:e&&e.nodeType===3?!1:n&&n.nodeType===3?cl(e,n.parentNode):"contains"in e?e.contains(n):e.compareDocumentPosition?!!(e.compareDocumentPosition(n)&16):!1:!1}function dl(){for(var e=window,n=Ir();n instanceof e.HTMLIFrameElement;){try{var t=typeof n.contentWindow.location.href=="string"}catch{t=!1}if(t)e=n.contentWindow;else break;n=Ir(e.document)}return n}function Ri(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n&&(n==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||n==="textarea"||e.contentEditable==="true")}function Ud(e){var n=dl(),t=e.focusedElem,s=e.selectionRange;if(n!==t&&t&&t.ownerDocument&&cl(t.ownerDocument.documentElement,t)){if(s!==null&&Ri(t)){if(n=s.start,e=s.end,e===void 0&&(e=n),"selectionStart"in t)t.selectionStart=n,t.selectionEnd=Math.min(e,t.value.length);else if(e=(n=t.ownerDocument||document)&&n.defaultView||window,e.getSelection){e=e.getSelection();var i=t.textContent.length,o=Math.min(s.start,i);s=s.end===void 0?o:Math.min(s.end,i),!e.extend&&o>s&&(i=s,s=o,o=i),i=ul(t,o);var l=ul(t,s);i&&l&&(e.rangeCount!==1||e.anchorNode!==i.node||e.anchorOffset!==i.offset||e.focusNode!==l.node||e.focusOffset!==l.offset)&&(n=n.createRange(),n.setStart(i.node,i.offset),e.removeAllRanges(),o>s?(e.addRange(n),e.extend(l.node,l.offset)):(n.setEnd(l.node,l.offset),e.addRange(n)))}}for(n=[],e=t;e=e.parentNode;)e.nodeType===1&&n.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof t.focus=="function"&&t.focus(),t=0;t<n.length;t++)e=n[t],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var Wd=z&&"documentMode"in document&&11>=document.documentMode,Et=null,Di=null,hr=null,Ai=!1;function ml(e,n,t){var s=t.window===t?t.document:t.nodeType===9?t:t.ownerDocument;Ai||Et==null||Et!==Ir(s)||(s=Et,"selectionStart"in s&&Ri(s)?s={start:s.selectionStart,end:s.selectionEnd}:(s=(s.ownerDocument&&s.ownerDocument.defaultView||window).getSelection(),s={anchorNode:s.anchorNode,anchorOffset:s.anchorOffset,focusNode:s.focusNode,focusOffset:s.focusOffset}),hr&&mr(hr,s)||(hr=s,s=rs(Di,"onSelect"),0<s.length&&(n=new Ci("onSelect","select",null,n,t),e.push({event:n,listeners:s}),n.target=Et)))}function es(e,n){var t={};return t[e.toLowerCase()]=n.toLowerCase(),t["Webkit"+e]="webkit"+n,t["Moz"+e]="moz"+n,t}var Pt={animationend:es("Animation","AnimationEnd"),animationiteration:es("Animation","AnimationIteration"),animationstart:es("Animation","AnimationStart"),transitionend:es("Transition","TransitionEnd")},Ii={},hl={};z&&(hl=document.createElement("div").style,"AnimationEvent"in window||(delete Pt.animationend.animation,delete Pt.animationiteration.animation,delete Pt.animationstart.animation),"TransitionEvent"in window||delete Pt.transitionend.transition);function ns(e){if(Ii[e])return Ii[e];if(!Pt[e])return e;var n=Pt[e],t;for(t in n)if(n.hasOwnProperty(t)&&t in hl)return Ii[e]=n[t];return e}var pl=ns("animationend"),fl=ns("animationiteration"),gl=ns("animationstart"),vl=ns("transitionend"),yl=new Map,xl="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function Vn(e,n){yl.set(e,n),j(n,[e])}for(var zi=0;zi<xl.length;zi++){var Fi=xl[zi],$d=Fi.toLowerCase(),Vd=Fi[0].toUpperCase()+Fi.slice(1);Vn($d,"on"+Vd)}Vn(pl,"onAnimationEnd"),Vn(fl,"onAnimationIteration"),Vn(gl,"onAnimationStart"),Vn("dblclick","onDoubleClick"),Vn("focusin","onFocus"),Vn("focusout","onBlur"),Vn(vl,"onTransitionEnd"),w("onMouseEnter",["mouseout","mouseover"]),w("onMouseLeave",["mouseout","mouseover"]),w("onPointerEnter",["pointerout","pointerover"]),w("onPointerLeave",["pointerout","pointerover"]),j("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),j("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),j("onBeforeInput",["compositionend","keypress","textInput","paste"]),j("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),j("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),j("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var pr="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),Hd=new Set("cancel close invalid load scroll toggle".split(" ").concat(pr));function kl(e,n,t){var s=e.type||"unknown-event";e.currentTarget=t,$c(s,n,void 0,e),e.currentTarget=null}function wl(e,n){n=(n&4)!==0;for(var t=0;t<e.length;t++){var s=e[t],i=s.event;s=s.listeners;e:{var o=void 0;if(n)for(var l=s.length-1;0<=l;l--){var d=s[l],m=d.instance,k=d.currentTarget;if(d=d.listener,m!==o&&i.isPropagationStopped())break e;kl(i,d,k),o=m}else for(l=0;l<s.length;l++){if(d=s[l],m=d.instance,k=d.currentTarget,d=d.listener,m!==o&&i.isPropagationStopped())break e;kl(i,d,k),o=m}}}if(Or)throw e=fi,Or=!1,fi=null,e}function ge(e,n){var t=n[Gi];t===void 0&&(t=n[Gi]=new Set);var s=e+"__bubble";t.has(s)||(jl(n,e,2,!1),t.add(s))}function Oi(e,n,t){var s=0;n&&(s|=4),jl(t,e,s,n)}var ts="_reactListening"+Math.random().toString(36).slice(2);function fr(e){if(!e[ts]){e[ts]=!0,p.forEach(function(t){t!=="selectionchange"&&(Hd.has(t)||Oi(t,!1,e),Oi(t,!0,e))});var n=e.nodeType===9?e:e.ownerDocument;n===null||n[ts]||(n[ts]=!0,Oi("selectionchange",!1,n))}}function jl(e,n,t,s){switch(Ha(n)){case 1:var i=id;break;case 4:i=od;break;default:i=ji}t=i.bind(null,n,t,e),i=void 0,!pi||n!=="touchstart"&&n!=="touchmove"&&n!=="wheel"||(i=!0),s?i!==void 0?e.addEventListener(n,t,{capture:!0,passive:i}):e.addEventListener(n,t,!0):i!==void 0?e.addEventListener(n,t,{passive:i}):e.addEventListener(n,t,!1)}function Bi(e,n,t,s,i){var o=s;if((n&1)===0&&(n&2)===0&&s!==null)e:for(;;){if(s===null)return;var l=s.tag;if(l===3||l===4){var d=s.stateNode.containerInfo;if(d===i||d.nodeType===8&&d.parentNode===i)break;if(l===4)for(l=s.return;l!==null;){var m=l.tag;if((m===3||m===4)&&(m=l.stateNode.containerInfo,m===i||m.nodeType===8&&m.parentNode===i))return;l=l.return}for(;d!==null;){if(l=lt(d),l===null)return;if(m=l.tag,m===5||m===6){s=o=l;continue e}d=d.parentNode}}s=s.return}ba(function(){var k=o,b=di(t),P=[];e:{var C=yl.get(e);if(C!==void 0){var B=Ci,V=e;switch(e){case"keypress":if(qr(t)===0)break e;case"keydown":case"keyup":B=wd;break;case"focusin":V="focus",B=Ei;break;case"focusout":V="blur",B=Ei;break;case"beforeblur":case"afterblur":B=Ei;break;case"click":if(t.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":B=Qa;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":B=ud;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":B=Nd;break;case pl:case fl:case gl:B=md;break;case vl:B=_d;break;case"scroll":B=ad;break;case"wheel":B=Ed;break;case"copy":case"cut":case"paste":B=pd;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":B=qa}var H=(n&4)!==0,Ce=!H&&e==="scroll",v=H?C!==null?C+"Capture":null:C;H=[];for(var h=k,x;h!==null;){x=h;var L=x.stateNode;if(x.tag===5&&L!==null&&(x=L,v!==null&&(L=Yt(h,v),L!=null&&H.push(gr(h,L,x)))),Ce)break;h=h.return}0<H.length&&(C=new B(C,V,null,t,b),P.push({event:C,listeners:H}))}}if((n&7)===0){e:{if(C=e==="mouseover"||e==="pointerover",B=e==="mouseout"||e==="pointerout",C&&t!==ci&&(V=t.relatedTarget||t.fromElement)&&(lt(V)||V[Mn]))break e;if((B||C)&&(C=b.window===b?b:(C=b.ownerDocument)?C.defaultView||C.parentWindow:window,B?(V=t.relatedTarget||t.toElement,B=k,V=V?lt(V):null,V!==null&&(Ce=at(V),V!==Ce||V.tag!==5&&V.tag!==6)&&(V=null)):(B=null,V=k),B!==V)){if(H=Qa,L="onMouseLeave",v="onMouseEnter",h="mouse",(e==="pointerout"||e==="pointerover")&&(H=qa,L="onPointerLeave",v="onPointerEnter",h="pointer"),Ce=B==null?C:Lt(B),x=V==null?C:Lt(V),C=new H(L,h+"leave",B,t,b),C.target=Ce,C.relatedTarget=x,L=null,lt(b)===k&&(H=new H(v,h+"enter",V,t,b),H.target=x,H.relatedTarget=Ce,L=H),Ce=L,B&&V)n:{for(H=B,v=V,h=0,x=H;x;x=Tt(x))h++;for(x=0,L=v;L;L=Tt(L))x++;for(;0<h-x;)H=Tt(H),h--;for(;0<x-h;)v=Tt(v),x--;for(;h--;){if(H===v||v!==null&&H===v.alternate)break n;H=Tt(H),v=Tt(v)}H=null}else H=null;B!==null&&Sl(P,C,B,H,!1),V!==null&&Ce!==null&&Sl(P,Ce,V,H,!0)}}e:{if(C=k?Lt(k):window,B=C.nodeName&&C.nodeName.toLowerCase(),B==="select"||B==="input"&&C.type==="file")var G=Ad;else if(tl(C))if(sl)G=Od;else{G=zd;var Q=Id}else(B=C.nodeName)&&B.toLowerCase()==="input"&&(C.type==="checkbox"||C.type==="radio")&&(G=Fd);if(G&&(G=G(e,k))){rl(P,G,t,b);break e}Q&&Q(e,C,k),e==="focusout"&&(Q=C._wrapperState)&&Q.controlled&&C.type==="number"&&ii(C,"number",C.value)}switch(Q=k?Lt(k):window,e){case"focusin":(tl(Q)||Q.contentEditable==="true")&&(Et=Q,Di=k,hr=null);break;case"focusout":hr=Di=Et=null;break;case"mousedown":Ai=!0;break;case"contextmenu":case"mouseup":case"dragend":Ai=!1,ml(P,t,b);break;case"selectionchange":if(Wd)break;case"keydown":case"keyup":ml(P,t,b)}var X;if(Ti)e:{switch(e){case"compositionstart":var J="onCompositionStart";break e;case"compositionend":J="onCompositionEnd";break e;case"compositionupdate":J="onCompositionUpdate";break e}J=void 0}else bt?el(e,t)&&(J="onCompositionEnd"):e==="keydown"&&t.keyCode===229&&(J="onCompositionStart");J&&(Ya&&t.locale!=="ko"&&(bt||J!=="onCompositionStart"?J==="onCompositionEnd"&&bt&&(X=Ga()):($n=b,Ni="value"in $n?$n.value:$n.textContent,bt=!0)),Q=rs(k,J),0<Q.length&&(J=new Xa(J,e,null,t,b),P.push({event:J,listeners:Q}),X?J.data=X:(X=nl(t),X!==null&&(J.data=X)))),(X=Td?Md(e,t):Ld(e,t))&&(k=rs(k,"onBeforeInput"),0<k.length&&(b=new Xa("onBeforeInput","beforeinput",null,t,b),P.push({event:b,listeners:k}),b.data=X))}wl(P,n)})}function gr(e,n,t){return{instance:e,listener:n,currentTarget:t}}function rs(e,n){for(var t=n+"Capture",s=[];e!==null;){var i=e,o=i.stateNode;i.tag===5&&o!==null&&(i=o,o=Yt(e,t),o!=null&&s.unshift(gr(e,o,i)),o=Yt(e,n),o!=null&&s.push(gr(e,o,i))),e=e.return}return s}function Tt(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function Sl(e,n,t,s,i){for(var o=n._reactName,l=[];t!==null&&t!==s;){var d=t,m=d.alternate,k=d.stateNode;if(m!==null&&m===s)break;d.tag===5&&k!==null&&(d=k,i?(m=Yt(t,o),m!=null&&l.unshift(gr(t,m,d))):i||(m=Yt(t,o),m!=null&&l.push(gr(t,m,d)))),t=t.return}l.length!==0&&e.push({event:n,listeners:l})}var Gd=/\r\n?/g,Kd=/\u0000|\uFFFD/g;function Nl(e){return(typeof e=="string"?e:""+e).replace(Gd,`
`).replace(Kd,"")}function ss(e,n,t){if(n=Nl(n),Nl(e)!==n&&t)throw Error(c(425))}function is(){}var Ui=null,Wi=null;function $i(e,n){return e==="textarea"||e==="noscript"||typeof n.children=="string"||typeof n.children=="number"||typeof n.dangerouslySetInnerHTML=="object"&&n.dangerouslySetInnerHTML!==null&&n.dangerouslySetInnerHTML.__html!=null}var Vi=typeof setTimeout=="function"?setTimeout:void 0,Qd=typeof clearTimeout=="function"?clearTimeout:void 0,Cl=typeof Promise=="function"?Promise:void 0,Xd=typeof queueMicrotask=="function"?queueMicrotask:typeof Cl<"u"?function(e){return Cl.resolve(null).then(e).catch(qd)}:Vi;function qd(e){setTimeout(function(){throw e})}function Hi(e,n){var t=n,s=0;do{var i=t.nextSibling;if(e.removeChild(t),i&&i.nodeType===8)if(t=i.data,t==="/$"){if(s===0){e.removeChild(i),or(n);return}s--}else t!=="$"&&t!=="$?"&&t!=="$!"||s++;t=i}while(t);or(n)}function Hn(e){for(;e!=null;e=e.nextSibling){var n=e.nodeType;if(n===1||n===3)break;if(n===8){if(n=e.data,n==="$"||n==="$!"||n==="$?")break;if(n==="/$")return null}}return e}function _l(e){e=e.previousSibling;for(var n=0;e;){if(e.nodeType===8){var t=e.data;if(t==="$"||t==="$!"||t==="$?"){if(n===0)return e;n--}else t==="/$"&&n++}e=e.previousSibling}return null}var Mt=Math.random().toString(36).slice(2),_n="__reactFiber$"+Mt,vr="__reactProps$"+Mt,Mn="__reactContainer$"+Mt,Gi="__reactEvents$"+Mt,Yd="__reactListeners$"+Mt,Jd="__reactHandles$"+Mt;function lt(e){var n=e[_n];if(n)return n;for(var t=e.parentNode;t;){if(n=t[Mn]||t[_n]){if(t=n.alternate,n.child!==null||t!==null&&t.child!==null)for(e=_l(e);e!==null;){if(t=e[_n])return t;e=_l(e)}return n}e=t,t=e.parentNode}return null}function yr(e){return e=e[_n]||e[Mn],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function Lt(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(c(33))}function os(e){return e[vr]||null}var Ki=[],Rt=-1;function Gn(e){return{current:e}}function ve(e){0>Rt||(e.current=Ki[Rt],Ki[Rt]=null,Rt--)}function pe(e,n){Rt++,Ki[Rt]=e.current,e.current=n}var Kn={},ze=Gn(Kn),Ve=Gn(!1),ut=Kn;function Dt(e,n){var t=e.type.contextTypes;if(!t)return Kn;var s=e.stateNode;if(s&&s.__reactInternalMemoizedUnmaskedChildContext===n)return s.__reactInternalMemoizedMaskedChildContext;var i={},o;for(o in t)i[o]=n[o];return s&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=n,e.__reactInternalMemoizedMaskedChildContext=i),i}function He(e){return e=e.childContextTypes,e!=null}function as(){ve(Ve),ve(ze)}function bl(e,n,t){if(ze.current!==Kn)throw Error(c(168));pe(ze,n),pe(Ve,t)}function El(e,n,t){var s=e.stateNode;if(n=n.childContextTypes,typeof s.getChildContext!="function")return t;s=s.getChildContext();for(var i in s)if(!(i in n))throw Error(c(108,he(e)||"Unknown",i));return $({},t,s)}function ls(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||Kn,ut=ze.current,pe(ze,e),pe(Ve,Ve.current),!0}function Pl(e,n,t){var s=e.stateNode;if(!s)throw Error(c(169));t?(e=El(e,n,ut),s.__reactInternalMemoizedMergedChildContext=e,ve(Ve),ve(ze),pe(ze,e)):ve(Ve),pe(Ve,t)}var Ln=null,us=!1,Qi=!1;function Tl(e){Ln===null?Ln=[e]:Ln.push(e)}function Zd(e){us=!0,Tl(e)}function Qn(){if(!Qi&&Ln!==null){Qi=!0;var e=0,n=de;try{var t=Ln;for(de=1;e<t.length;e++){var s=t[e];do s=s(!0);while(s!==null)}Ln=null,us=!1}catch(i){throw Ln!==null&&(Ln=Ln.slice(e+1)),La(gi,Qn),i}finally{de=n,Qi=!1}}return null}var At=[],It=0,cs=null,ds=0,an=[],ln=0,ct=null,Rn=1,Dn="";function dt(e,n){At[It++]=ds,At[It++]=cs,cs=e,ds=n}function Ml(e,n,t){an[ln++]=Rn,an[ln++]=Dn,an[ln++]=ct,ct=e;var s=Rn;e=Dn;var i=32-fn(s)-1;s&=~(1<<i),t+=1;var o=32-fn(n)+i;if(30<o){var l=i-i%5;o=(s&(1<<l)-1).toString(32),s>>=l,i-=l,Rn=1<<32-fn(n)+i|t<<i|s,Dn=o+e}else Rn=1<<o|t<<i|s,Dn=e}function Xi(e){e.return!==null&&(dt(e,1),Ml(e,1,0))}function qi(e){for(;e===cs;)cs=At[--It],At[It]=null,ds=At[--It],At[It]=null;for(;e===ct;)ct=an[--ln],an[ln]=null,Dn=an[--ln],an[ln]=null,Rn=an[--ln],an[ln]=null}var rn=null,sn=null,xe=!1,vn=null;function Ll(e,n){var t=mn(5,null,null,0);t.elementType="DELETED",t.stateNode=n,t.return=e,n=e.deletions,n===null?(e.deletions=[t],e.flags|=16):n.push(t)}function Rl(e,n){switch(e.tag){case 5:var t=e.type;return n=n.nodeType!==1||t.toLowerCase()!==n.nodeName.toLowerCase()?null:n,n!==null?(e.stateNode=n,rn=e,sn=Hn(n.firstChild),!0):!1;case 6:return n=e.pendingProps===""||n.nodeType!==3?null:n,n!==null?(e.stateNode=n,rn=e,sn=null,!0):!1;case 13:return n=n.nodeType!==8?null:n,n!==null?(t=ct!==null?{id:Rn,overflow:Dn}:null,e.memoizedState={dehydrated:n,treeContext:t,retryLane:1073741824},t=mn(18,null,null,0),t.stateNode=n,t.return=e,e.child=t,rn=e,sn=null,!0):!1;default:return!1}}function Yi(e){return(e.mode&1)!==0&&(e.flags&128)===0}function Ji(e){if(xe){var n=sn;if(n){var t=n;if(!Rl(e,n)){if(Yi(e))throw Error(c(418));n=Hn(t.nextSibling);var s=rn;n&&Rl(e,n)?Ll(s,t):(e.flags=e.flags&-4097|2,xe=!1,rn=e)}}else{if(Yi(e))throw Error(c(418));e.flags=e.flags&-4097|2,xe=!1,rn=e}}}function Dl(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;rn=e}function ms(e){if(e!==rn)return!1;if(!xe)return Dl(e),xe=!0,!1;var n;if((n=e.tag!==3)&&!(n=e.tag!==5)&&(n=e.type,n=n!=="head"&&n!=="body"&&!$i(e.type,e.memoizedProps)),n&&(n=sn)){if(Yi(e))throw Al(),Error(c(418));for(;n;)Ll(e,n),n=Hn(n.nextSibling)}if(Dl(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(c(317));e:{for(e=e.nextSibling,n=0;e;){if(e.nodeType===8){var t=e.data;if(t==="/$"){if(n===0){sn=Hn(e.nextSibling);break e}n--}else t!=="$"&&t!=="$!"&&t!=="$?"||n++}e=e.nextSibling}sn=null}}else sn=rn?Hn(e.stateNode.nextSibling):null;return!0}function Al(){for(var e=sn;e;)e=Hn(e.nextSibling)}function zt(){sn=rn=null,xe=!1}function Zi(e){vn===null?vn=[e]:vn.push(e)}var em=se.ReactCurrentBatchConfig;function xr(e,n,t){if(e=t.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(t._owner){if(t=t._owner,t){if(t.tag!==1)throw Error(c(309));var s=t.stateNode}if(!s)throw Error(c(147,e));var i=s,o=""+e;return n!==null&&n.ref!==null&&typeof n.ref=="function"&&n.ref._stringRef===o?n.ref:(n=function(l){var d=i.refs;l===null?delete d[o]:d[o]=l},n._stringRef=o,n)}if(typeof e!="string")throw Error(c(284));if(!t._owner)throw Error(c(290,e))}return e}function hs(e,n){throw e=Object.prototype.toString.call(n),Error(c(31,e==="[object Object]"?"object with keys {"+Object.keys(n).join(", ")+"}":e))}function Il(e){var n=e._init;return n(e._payload)}function zl(e){function n(v,h){if(e){var x=v.deletions;x===null?(v.deletions=[h],v.flags|=16):x.push(h)}}function t(v,h){if(!e)return null;for(;h!==null;)n(v,h),h=h.sibling;return null}function s(v,h){for(v=new Map;h!==null;)h.key!==null?v.set(h.key,h):v.set(h.index,h),h=h.sibling;return v}function i(v,h){return v=tt(v,h),v.index=0,v.sibling=null,v}function o(v,h,x){return v.index=x,e?(x=v.alternate,x!==null?(x=x.index,x<h?(v.flags|=2,h):x):(v.flags|=2,h)):(v.flags|=1048576,h)}function l(v){return e&&v.alternate===null&&(v.flags|=2),v}function d(v,h,x,L){return h===null||h.tag!==6?(h=Ho(x,v.mode,L),h.return=v,h):(h=i(h,x),h.return=v,h)}function m(v,h,x,L){var G=x.type;return G===Z?b(v,h,x.props.children,L,x.key):h!==null&&(h.elementType===G||typeof G=="object"&&G!==null&&G.$$typeof===$e&&Il(G)===h.type)?(L=i(h,x.props),L.ref=xr(v,h,x),L.return=v,L):(L=zs(x.type,x.key,x.props,null,v.mode,L),L.ref=xr(v,h,x),L.return=v,L)}function k(v,h,x,L){return h===null||h.tag!==4||h.stateNode.containerInfo!==x.containerInfo||h.stateNode.implementation!==x.implementation?(h=Go(x,v.mode,L),h.return=v,h):(h=i(h,x.children||[]),h.return=v,h)}function b(v,h,x,L,G){return h===null||h.tag!==7?(h=xt(x,v.mode,L,G),h.return=v,h):(h=i(h,x),h.return=v,h)}function P(v,h,x){if(typeof h=="string"&&h!==""||typeof h=="number")return h=Ho(""+h,v.mode,x),h.return=v,h;if(typeof h=="object"&&h!==null){switch(h.$$typeof){case ie:return x=zs(h.type,h.key,h.props,null,v.mode,x),x.ref=xr(v,null,h),x.return=v,x;case M:return h=Go(h,v.mode,x),h.return=v,h;case $e:var L=h._init;return P(v,L(h._payload),x)}if(Qt(h)||q(h))return h=xt(h,v.mode,x,null),h.return=v,h;hs(v,h)}return null}function C(v,h,x,L){var G=h!==null?h.key:null;if(typeof x=="string"&&x!==""||typeof x=="number")return G!==null?null:d(v,h,""+x,L);if(typeof x=="object"&&x!==null){switch(x.$$typeof){case ie:return x.key===G?m(v,h,x,L):null;case M:return x.key===G?k(v,h,x,L):null;case $e:return G=x._init,C(v,h,G(x._payload),L)}if(Qt(x)||q(x))return G!==null?null:b(v,h,x,L,null);hs(v,x)}return null}function B(v,h,x,L,G){if(typeof L=="string"&&L!==""||typeof L=="number")return v=v.get(x)||null,d(h,v,""+L,G);if(typeof L=="object"&&L!==null){switch(L.$$typeof){case ie:return v=v.get(L.key===null?x:L.key)||null,m(h,v,L,G);case M:return v=v.get(L.key===null?x:L.key)||null,k(h,v,L,G);case $e:var Q=L._init;return B(v,h,x,Q(L._payload),G)}if(Qt(L)||q(L))return v=v.get(x)||null,b(h,v,L,G,null);hs(h,L)}return null}function V(v,h,x,L){for(var G=null,Q=null,X=h,J=h=0,De=null;X!==null&&J<x.length;J++){X.index>J?(De=X,X=null):De=X.sibling;var ue=C(v,X,x[J],L);if(ue===null){X===null&&(X=De);break}e&&X&&ue.alternate===null&&n(v,X),h=o(ue,h,J),Q===null?G=ue:Q.sibling=ue,Q=ue,X=De}if(J===x.length)return t(v,X),xe&&dt(v,J),G;if(X===null){for(;J<x.length;J++)X=P(v,x[J],L),X!==null&&(h=o(X,h,J),Q===null?G=X:Q.sibling=X,Q=X);return xe&&dt(v,J),G}for(X=s(v,X);J<x.length;J++)De=B(X,v,J,x[J],L),De!==null&&(e&&De.alternate!==null&&X.delete(De.key===null?J:De.key),h=o(De,h,J),Q===null?G=De:Q.sibling=De,Q=De);return e&&X.forEach(function(rt){return n(v,rt)}),xe&&dt(v,J),G}function H(v,h,x,L){var G=q(x);if(typeof G!="function")throw Error(c(150));if(x=G.call(x),x==null)throw Error(c(151));for(var Q=G=null,X=h,J=h=0,De=null,ue=x.next();X!==null&&!ue.done;J++,ue=x.next()){X.index>J?(De=X,X=null):De=X.sibling;var rt=C(v,X,ue.value,L);if(rt===null){X===null&&(X=De);break}e&&X&&rt.alternate===null&&n(v,X),h=o(rt,h,J),Q===null?G=rt:Q.sibling=rt,Q=rt,X=De}if(ue.done)return t(v,X),xe&&dt(v,J),G;if(X===null){for(;!ue.done;J++,ue=x.next())ue=P(v,ue.value,L),ue!==null&&(h=o(ue,h,J),Q===null?G=ue:Q.sibling=ue,Q=ue);return xe&&dt(v,J),G}for(X=s(v,X);!ue.done;J++,ue=x.next())ue=B(X,v,J,ue.value,L),ue!==null&&(e&&ue.alternate!==null&&X.delete(ue.key===null?J:ue.key),h=o(ue,h,J),Q===null?G=ue:Q.sibling=ue,Q=ue);return e&&X.forEach(function(Rm){return n(v,Rm)}),xe&&dt(v,J),G}function Ce(v,h,x,L){if(typeof x=="object"&&x!==null&&x.type===Z&&x.key===null&&(x=x.props.children),typeof x=="object"&&x!==null){switch(x.$$typeof){case ie:e:{for(var G=x.key,Q=h;Q!==null;){if(Q.key===G){if(G=x.type,G===Z){if(Q.tag===7){t(v,Q.sibling),h=i(Q,x.props.children),h.return=v,v=h;break e}}else if(Q.elementType===G||typeof G=="object"&&G!==null&&G.$$typeof===$e&&Il(G)===Q.type){t(v,Q.sibling),h=i(Q,x.props),h.ref=xr(v,Q,x),h.return=v,v=h;break e}t(v,Q);break}else n(v,Q);Q=Q.sibling}x.type===Z?(h=xt(x.props.children,v.mode,L,x.key),h.return=v,v=h):(L=zs(x.type,x.key,x.props,null,v.mode,L),L.ref=xr(v,h,x),L.return=v,v=L)}return l(v);case M:e:{for(Q=x.key;h!==null;){if(h.key===Q)if(h.tag===4&&h.stateNode.containerInfo===x.containerInfo&&h.stateNode.implementation===x.implementation){t(v,h.sibling),h=i(h,x.children||[]),h.return=v,v=h;break e}else{t(v,h);break}else n(v,h);h=h.sibling}h=Go(x,v.mode,L),h.return=v,v=h}return l(v);case $e:return Q=x._init,Ce(v,h,Q(x._payload),L)}if(Qt(x))return V(v,h,x,L);if(q(x))return H(v,h,x,L);hs(v,x)}return typeof x=="string"&&x!==""||typeof x=="number"?(x=""+x,h!==null&&h.tag===6?(t(v,h.sibling),h=i(h,x),h.return=v,v=h):(t(v,h),h=Ho(x,v.mode,L),h.return=v,v=h),l(v)):t(v,h)}return Ce}var Ft=zl(!0),Fl=zl(!1),ps=Gn(null),fs=null,Ot=null,eo=null;function no(){eo=Ot=fs=null}function to(e){var n=ps.current;ve(ps),e._currentValue=n}function ro(e,n,t){for(;e!==null;){var s=e.alternate;if((e.childLanes&n)!==n?(e.childLanes|=n,s!==null&&(s.childLanes|=n)):s!==null&&(s.childLanes&n)!==n&&(s.childLanes|=n),e===t)break;e=e.return}}function Bt(e,n){fs=e,eo=Ot=null,e=e.dependencies,e!==null&&e.firstContext!==null&&((e.lanes&n)!==0&&(Ge=!0),e.firstContext=null)}function un(e){var n=e._currentValue;if(eo!==e)if(e={context:e,memoizedValue:n,next:null},Ot===null){if(fs===null)throw Error(c(308));Ot=e,fs.dependencies={lanes:0,firstContext:e}}else Ot=Ot.next=e;return n}var mt=null;function so(e){mt===null?mt=[e]:mt.push(e)}function Ol(e,n,t,s){var i=n.interleaved;return i===null?(t.next=t,so(n)):(t.next=i.next,i.next=t),n.interleaved=t,An(e,s)}function An(e,n){e.lanes|=n;var t=e.alternate;for(t!==null&&(t.lanes|=n),t=e,e=e.return;e!==null;)e.childLanes|=n,t=e.alternate,t!==null&&(t.childLanes|=n),t=e,e=e.return;return t.tag===3?t.stateNode:null}var Xn=!1;function io(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function Bl(e,n){e=e.updateQueue,n.updateQueue===e&&(n.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function In(e,n){return{eventTime:e,lane:n,tag:0,payload:null,callback:null,next:null}}function qn(e,n,t){var s=e.updateQueue;if(s===null)return null;if(s=s.shared,(oe&2)!==0){var i=s.pending;return i===null?n.next=n:(n.next=i.next,i.next=n),s.pending=n,An(e,t)}return i=s.interleaved,i===null?(n.next=n,so(s)):(n.next=i.next,i.next=n),s.interleaved=n,An(e,t)}function gs(e,n,t){if(n=n.updateQueue,n!==null&&(n=n.shared,(t&4194240)!==0)){var s=n.lanes;s&=e.pendingLanes,t|=s,n.lanes=t,xi(e,t)}}function Ul(e,n){var t=e.updateQueue,s=e.alternate;if(s!==null&&(s=s.updateQueue,t===s)){var i=null,o=null;if(t=t.firstBaseUpdate,t!==null){do{var l={eventTime:t.eventTime,lane:t.lane,tag:t.tag,payload:t.payload,callback:t.callback,next:null};o===null?i=o=l:o=o.next=l,t=t.next}while(t!==null);o===null?i=o=n:o=o.next=n}else i=o=n;t={baseState:s.baseState,firstBaseUpdate:i,lastBaseUpdate:o,shared:s.shared,effects:s.effects},e.updateQueue=t;return}e=t.lastBaseUpdate,e===null?t.firstBaseUpdate=n:e.next=n,t.lastBaseUpdate=n}function vs(e,n,t,s){var i=e.updateQueue;Xn=!1;var o=i.firstBaseUpdate,l=i.lastBaseUpdate,d=i.shared.pending;if(d!==null){i.shared.pending=null;var m=d,k=m.next;m.next=null,l===null?o=k:l.next=k,l=m;var b=e.alternate;b!==null&&(b=b.updateQueue,d=b.lastBaseUpdate,d!==l&&(d===null?b.firstBaseUpdate=k:d.next=k,b.lastBaseUpdate=m))}if(o!==null){var P=i.baseState;l=0,b=k=m=null,d=o;do{var C=d.lane,B=d.eventTime;if((s&C)===C){b!==null&&(b=b.next={eventTime:B,lane:0,tag:d.tag,payload:d.payload,callback:d.callback,next:null});e:{var V=e,H=d;switch(C=n,B=t,H.tag){case 1:if(V=H.payload,typeof V=="function"){P=V.call(B,P,C);break e}P=V;break e;case 3:V.flags=V.flags&-65537|128;case 0:if(V=H.payload,C=typeof V=="function"?V.call(B,P,C):V,C==null)break e;P=$({},P,C);break e;case 2:Xn=!0}}d.callback!==null&&d.lane!==0&&(e.flags|=64,C=i.effects,C===null?i.effects=[d]:C.push(d))}else B={eventTime:B,lane:C,tag:d.tag,payload:d.payload,callback:d.callback,next:null},b===null?(k=b=B,m=P):b=b.next=B,l|=C;if(d=d.next,d===null){if(d=i.shared.pending,d===null)break;C=d,d=C.next,C.next=null,i.lastBaseUpdate=C,i.shared.pending=null}}while(!0);if(b===null&&(m=P),i.baseState=m,i.firstBaseUpdate=k,i.lastBaseUpdate=b,n=i.shared.interleaved,n!==null){i=n;do l|=i.lane,i=i.next;while(i!==n)}else o===null&&(i.shared.lanes=0);ft|=l,e.lanes=l,e.memoizedState=P}}function Wl(e,n,t){if(e=n.effects,n.effects=null,e!==null)for(n=0;n<e.length;n++){var s=e[n],i=s.callback;if(i!==null){if(s.callback=null,s=t,typeof i!="function")throw Error(c(191,i));i.call(s)}}}var kr={},bn=Gn(kr),wr=Gn(kr),jr=Gn(kr);function ht(e){if(e===kr)throw Error(c(174));return e}function oo(e,n){switch(pe(jr,n),pe(wr,e),pe(bn,kr),e=n.nodeType,e){case 9:case 11:n=(n=n.documentElement)?n.namespaceURI:ai(null,"");break;default:e=e===8?n.parentNode:n,n=e.namespaceURI||null,e=e.tagName,n=ai(n,e)}ve(bn),pe(bn,n)}function Ut(){ve(bn),ve(wr),ve(jr)}function $l(e){ht(jr.current);var n=ht(bn.current),t=ai(n,e.type);n!==t&&(pe(wr,e),pe(bn,t))}function ao(e){wr.current===e&&(ve(bn),ve(wr))}var ke=Gn(0);function ys(e){for(var n=e;n!==null;){if(n.tag===13){var t=n.memoizedState;if(t!==null&&(t=t.dehydrated,t===null||t.data==="$?"||t.data==="$!"))return n}else if(n.tag===19&&n.memoizedProps.revealOrder!==void 0){if((n.flags&128)!==0)return n}else if(n.child!==null){n.child.return=n,n=n.child;continue}if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return null;n=n.return}n.sibling.return=n.return,n=n.sibling}return null}var lo=[];function uo(){for(var e=0;e<lo.length;e++)lo[e]._workInProgressVersionPrimary=null;lo.length=0}var xs=se.ReactCurrentDispatcher,co=se.ReactCurrentBatchConfig,pt=0,we=null,Pe=null,Le=null,ks=!1,Sr=!1,Nr=0,nm=0;function Fe(){throw Error(c(321))}function mo(e,n){if(n===null)return!1;for(var t=0;t<n.length&&t<e.length;t++)if(!gn(e[t],n[t]))return!1;return!0}function ho(e,n,t,s,i,o){if(pt=o,we=n,n.memoizedState=null,n.updateQueue=null,n.lanes=0,xs.current=e===null||e.memoizedState===null?im:om,e=t(s,i),Sr){o=0;do{if(Sr=!1,Nr=0,25<=o)throw Error(c(301));o+=1,Le=Pe=null,n.updateQueue=null,xs.current=am,e=t(s,i)}while(Sr)}if(xs.current=Ss,n=Pe!==null&&Pe.next!==null,pt=0,Le=Pe=we=null,ks=!1,n)throw Error(c(300));return e}function po(){var e=Nr!==0;return Nr=0,e}function En(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return Le===null?we.memoizedState=Le=e:Le=Le.next=e,Le}function cn(){if(Pe===null){var e=we.alternate;e=e!==null?e.memoizedState:null}else e=Pe.next;var n=Le===null?we.memoizedState:Le.next;if(n!==null)Le=n,Pe=e;else{if(e===null)throw Error(c(310));Pe=e,e={memoizedState:Pe.memoizedState,baseState:Pe.baseState,baseQueue:Pe.baseQueue,queue:Pe.queue,next:null},Le===null?we.memoizedState=Le=e:Le=Le.next=e}return Le}function Cr(e,n){return typeof n=="function"?n(e):n}function fo(e){var n=cn(),t=n.queue;if(t===null)throw Error(c(311));t.lastRenderedReducer=e;var s=Pe,i=s.baseQueue,o=t.pending;if(o!==null){if(i!==null){var l=i.next;i.next=o.next,o.next=l}s.baseQueue=i=o,t.pending=null}if(i!==null){o=i.next,s=s.baseState;var d=l=null,m=null,k=o;do{var b=k.lane;if((pt&b)===b)m!==null&&(m=m.next={lane:0,action:k.action,hasEagerState:k.hasEagerState,eagerState:k.eagerState,next:null}),s=k.hasEagerState?k.eagerState:e(s,k.action);else{var P={lane:b,action:k.action,hasEagerState:k.hasEagerState,eagerState:k.eagerState,next:null};m===null?(d=m=P,l=s):m=m.next=P,we.lanes|=b,ft|=b}k=k.next}while(k!==null&&k!==o);m===null?l=s:m.next=d,gn(s,n.memoizedState)||(Ge=!0),n.memoizedState=s,n.baseState=l,n.baseQueue=m,t.lastRenderedState=s}if(e=t.interleaved,e!==null){i=e;do o=i.lane,we.lanes|=o,ft|=o,i=i.next;while(i!==e)}else i===null&&(t.lanes=0);return[n.memoizedState,t.dispatch]}function go(e){var n=cn(),t=n.queue;if(t===null)throw Error(c(311));t.lastRenderedReducer=e;var s=t.dispatch,i=t.pending,o=n.memoizedState;if(i!==null){t.pending=null;var l=i=i.next;do o=e(o,l.action),l=l.next;while(l!==i);gn(o,n.memoizedState)||(Ge=!0),n.memoizedState=o,n.baseQueue===null&&(n.baseState=o),t.lastRenderedState=o}return[o,s]}function Vl(){}function Hl(e,n){var t=we,s=cn(),i=n(),o=!gn(s.memoizedState,i);if(o&&(s.memoizedState=i,Ge=!0),s=s.queue,vo(Ql.bind(null,t,s,e),[e]),s.getSnapshot!==n||o||Le!==null&&Le.memoizedState.tag&1){if(t.flags|=2048,_r(9,Kl.bind(null,t,s,i,n),void 0,null),Re===null)throw Error(c(349));(pt&30)!==0||Gl(t,n,i)}return i}function Gl(e,n,t){e.flags|=16384,e={getSnapshot:n,value:t},n=we.updateQueue,n===null?(n={lastEffect:null,stores:null},we.updateQueue=n,n.stores=[e]):(t=n.stores,t===null?n.stores=[e]:t.push(e))}function Kl(e,n,t,s){n.value=t,n.getSnapshot=s,Xl(n)&&ql(e)}function Ql(e,n,t){return t(function(){Xl(n)&&ql(e)})}function Xl(e){var n=e.getSnapshot;e=e.value;try{var t=n();return!gn(e,t)}catch{return!0}}function ql(e){var n=An(e,1);n!==null&&wn(n,e,1,-1)}function Yl(e){var n=En();return typeof e=="function"&&(e=e()),n.memoizedState=n.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:Cr,lastRenderedState:e},n.queue=e,e=e.dispatch=sm.bind(null,we,e),[n.memoizedState,e]}function _r(e,n,t,s){return e={tag:e,create:n,destroy:t,deps:s,next:null},n=we.updateQueue,n===null?(n={lastEffect:null,stores:null},we.updateQueue=n,n.lastEffect=e.next=e):(t=n.lastEffect,t===null?n.lastEffect=e.next=e:(s=t.next,t.next=e,e.next=s,n.lastEffect=e)),e}function Jl(){return cn().memoizedState}function ws(e,n,t,s){var i=En();we.flags|=e,i.memoizedState=_r(1|n,t,void 0,s===void 0?null:s)}function js(e,n,t,s){var i=cn();s=s===void 0?null:s;var o=void 0;if(Pe!==null){var l=Pe.memoizedState;if(o=l.destroy,s!==null&&mo(s,l.deps)){i.memoizedState=_r(n,t,o,s);return}}we.flags|=e,i.memoizedState=_r(1|n,t,o,s)}function Zl(e,n){return ws(8390656,8,e,n)}function vo(e,n){return js(2048,8,e,n)}function eu(e,n){return js(4,2,e,n)}function nu(e,n){return js(4,4,e,n)}function tu(e,n){if(typeof n=="function")return e=e(),n(e),function(){n(null)};if(n!=null)return e=e(),n.current=e,function(){n.current=null}}function ru(e,n,t){return t=t!=null?t.concat([e]):null,js(4,4,tu.bind(null,n,e),t)}function yo(){}function su(e,n){var t=cn();n=n===void 0?null:n;var s=t.memoizedState;return s!==null&&n!==null&&mo(n,s[1])?s[0]:(t.memoizedState=[e,n],e)}function iu(e,n){var t=cn();n=n===void 0?null:n;var s=t.memoizedState;return s!==null&&n!==null&&mo(n,s[1])?s[0]:(e=e(),t.memoizedState=[e,n],e)}function ou(e,n,t){return(pt&21)===0?(e.baseState&&(e.baseState=!1,Ge=!0),e.memoizedState=t):(gn(t,n)||(t=Ia(),we.lanes|=t,ft|=t,e.baseState=!0),n)}function tm(e,n){var t=de;de=t!==0&&4>t?t:4,e(!0);var s=co.transition;co.transition={};try{e(!1),n()}finally{de=t,co.transition=s}}function au(){return cn().memoizedState}function rm(e,n,t){var s=et(e);if(t={lane:s,action:t,hasEagerState:!1,eagerState:null,next:null},lu(e))uu(n,t);else if(t=Ol(e,n,t,s),t!==null){var i=We();wn(t,e,s,i),cu(t,n,s)}}function sm(e,n,t){var s=et(e),i={lane:s,action:t,hasEagerState:!1,eagerState:null,next:null};if(lu(e))uu(n,i);else{var o=e.alternate;if(e.lanes===0&&(o===null||o.lanes===0)&&(o=n.lastRenderedReducer,o!==null))try{var l=n.lastRenderedState,d=o(l,t);if(i.hasEagerState=!0,i.eagerState=d,gn(d,l)){var m=n.interleaved;m===null?(i.next=i,so(n)):(i.next=m.next,m.next=i),n.interleaved=i;return}}catch{}finally{}t=Ol(e,n,i,s),t!==null&&(i=We(),wn(t,e,s,i),cu(t,n,s))}}function lu(e){var n=e.alternate;return e===we||n!==null&&n===we}function uu(e,n){Sr=ks=!0;var t=e.pending;t===null?n.next=n:(n.next=t.next,t.next=n),e.pending=n}function cu(e,n,t){if((t&4194240)!==0){var s=n.lanes;s&=e.pendingLanes,t|=s,n.lanes=t,xi(e,t)}}var Ss={readContext:un,useCallback:Fe,useContext:Fe,useEffect:Fe,useImperativeHandle:Fe,useInsertionEffect:Fe,useLayoutEffect:Fe,useMemo:Fe,useReducer:Fe,useRef:Fe,useState:Fe,useDebugValue:Fe,useDeferredValue:Fe,useTransition:Fe,useMutableSource:Fe,useSyncExternalStore:Fe,useId:Fe,unstable_isNewReconciler:!1},im={readContext:un,useCallback:function(e,n){return En().memoizedState=[e,n===void 0?null:n],e},useContext:un,useEffect:Zl,useImperativeHandle:function(e,n,t){return t=t!=null?t.concat([e]):null,ws(4194308,4,tu.bind(null,n,e),t)},useLayoutEffect:function(e,n){return ws(4194308,4,e,n)},useInsertionEffect:function(e,n){return ws(4,2,e,n)},useMemo:function(e,n){var t=En();return n=n===void 0?null:n,e=e(),t.memoizedState=[e,n],e},useReducer:function(e,n,t){var s=En();return n=t!==void 0?t(n):n,s.memoizedState=s.baseState=n,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:n},s.queue=e,e=e.dispatch=rm.bind(null,we,e),[s.memoizedState,e]},useRef:function(e){var n=En();return e={current:e},n.memoizedState=e},useState:Yl,useDebugValue:yo,useDeferredValue:function(e){return En().memoizedState=e},useTransition:function(){var e=Yl(!1),n=e[0];return e=tm.bind(null,e[1]),En().memoizedState=e,[n,e]},useMutableSource:function(){},useSyncExternalStore:function(e,n,t){var s=we,i=En();if(xe){if(t===void 0)throw Error(c(407));t=t()}else{if(t=n(),Re===null)throw Error(c(349));(pt&30)!==0||Gl(s,n,t)}i.memoizedState=t;var o={value:t,getSnapshot:n};return i.queue=o,Zl(Ql.bind(null,s,o,e),[e]),s.flags|=2048,_r(9,Kl.bind(null,s,o,t,n),void 0,null),t},useId:function(){var e=En(),n=Re.identifierPrefix;if(xe){var t=Dn,s=Rn;t=(s&~(1<<32-fn(s)-1)).toString(32)+t,n=":"+n+"R"+t,t=Nr++,0<t&&(n+="H"+t.toString(32)),n+=":"}else t=nm++,n=":"+n+"r"+t.toString(32)+":";return e.memoizedState=n},unstable_isNewReconciler:!1},om={readContext:un,useCallback:su,useContext:un,useEffect:vo,useImperativeHandle:ru,useInsertionEffect:eu,useLayoutEffect:nu,useMemo:iu,useReducer:fo,useRef:Jl,useState:function(){return fo(Cr)},useDebugValue:yo,useDeferredValue:function(e){var n=cn();return ou(n,Pe.memoizedState,e)},useTransition:function(){var e=fo(Cr)[0],n=cn().memoizedState;return[e,n]},useMutableSource:Vl,useSyncExternalStore:Hl,useId:au,unstable_isNewReconciler:!1},am={readContext:un,useCallback:su,useContext:un,useEffect:vo,useImperativeHandle:ru,useInsertionEffect:eu,useLayoutEffect:nu,useMemo:iu,useReducer:go,useRef:Jl,useState:function(){return go(Cr)},useDebugValue:yo,useDeferredValue:function(e){var n=cn();return Pe===null?n.memoizedState=e:ou(n,Pe.memoizedState,e)},useTransition:function(){var e=go(Cr)[0],n=cn().memoizedState;return[e,n]},useMutableSource:Vl,useSyncExternalStore:Hl,useId:au,unstable_isNewReconciler:!1};function yn(e,n){if(e&&e.defaultProps){n=$({},n),e=e.defaultProps;for(var t in e)n[t]===void 0&&(n[t]=e[t]);return n}return n}function xo(e,n,t,s){n=e.memoizedState,t=t(s,n),t=t==null?n:$({},n,t),e.memoizedState=t,e.lanes===0&&(e.updateQueue.baseState=t)}var Ns={isMounted:function(e){return(e=e._reactInternals)?at(e)===e:!1},enqueueSetState:function(e,n,t){e=e._reactInternals;var s=We(),i=et(e),o=In(s,i);o.payload=n,t!=null&&(o.callback=t),n=qn(e,o,i),n!==null&&(wn(n,e,i,s),gs(n,e,i))},enqueueReplaceState:function(e,n,t){e=e._reactInternals;var s=We(),i=et(e),o=In(s,i);o.tag=1,o.payload=n,t!=null&&(o.callback=t),n=qn(e,o,i),n!==null&&(wn(n,e,i,s),gs(n,e,i))},enqueueForceUpdate:function(e,n){e=e._reactInternals;var t=We(),s=et(e),i=In(t,s);i.tag=2,n!=null&&(i.callback=n),n=qn(e,i,s),n!==null&&(wn(n,e,s,t),gs(n,e,s))}};function du(e,n,t,s,i,o,l){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(s,o,l):n.prototype&&n.prototype.isPureReactComponent?!mr(t,s)||!mr(i,o):!0}function mu(e,n,t){var s=!1,i=Kn,o=n.contextType;return typeof o=="object"&&o!==null?o=un(o):(i=He(n)?ut:ze.current,s=n.contextTypes,o=(s=s!=null)?Dt(e,i):Kn),n=new n(t,o),e.memoizedState=n.state!==null&&n.state!==void 0?n.state:null,n.updater=Ns,e.stateNode=n,n._reactInternals=e,s&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=i,e.__reactInternalMemoizedMaskedChildContext=o),n}function hu(e,n,t,s){e=n.state,typeof n.componentWillReceiveProps=="function"&&n.componentWillReceiveProps(t,s),typeof n.UNSAFE_componentWillReceiveProps=="function"&&n.UNSAFE_componentWillReceiveProps(t,s),n.state!==e&&Ns.enqueueReplaceState(n,n.state,null)}function ko(e,n,t,s){var i=e.stateNode;i.props=t,i.state=e.memoizedState,i.refs={},io(e);var o=n.contextType;typeof o=="object"&&o!==null?i.context=un(o):(o=He(n)?ut:ze.current,i.context=Dt(e,o)),i.state=e.memoizedState,o=n.getDerivedStateFromProps,typeof o=="function"&&(xo(e,n,o,t),i.state=e.memoizedState),typeof n.getDerivedStateFromProps=="function"||typeof i.getSnapshotBeforeUpdate=="function"||typeof i.UNSAFE_componentWillMount!="function"&&typeof i.componentWillMount!="function"||(n=i.state,typeof i.componentWillMount=="function"&&i.componentWillMount(),typeof i.UNSAFE_componentWillMount=="function"&&i.UNSAFE_componentWillMount(),n!==i.state&&Ns.enqueueReplaceState(i,i.state,null),vs(e,t,i,s),i.state=e.memoizedState),typeof i.componentDidMount=="function"&&(e.flags|=4194308)}function Wt(e,n){try{var t="",s=n;do t+=ae(s),s=s.return;while(s);var i=t}catch(o){i=`
Error generating stack: `+o.message+`
`+o.stack}return{value:e,source:n,stack:i,digest:null}}function wo(e,n,t){return{value:e,source:null,stack:t??null,digest:n??null}}function jo(e,n){try{console.error(n.value)}catch(t){setTimeout(function(){throw t})}}var lm=typeof WeakMap=="function"?WeakMap:Map;function pu(e,n,t){t=In(-1,t),t.tag=3,t.payload={element:null};var s=n.value;return t.callback=function(){Ms||(Ms=!0,zo=s),jo(e,n)},t}function fu(e,n,t){t=In(-1,t),t.tag=3;var s=e.type.getDerivedStateFromError;if(typeof s=="function"){var i=n.value;t.payload=function(){return s(i)},t.callback=function(){jo(e,n)}}var o=e.stateNode;return o!==null&&typeof o.componentDidCatch=="function"&&(t.callback=function(){jo(e,n),typeof s!="function"&&(Jn===null?Jn=new Set([this]):Jn.add(this));var l=n.stack;this.componentDidCatch(n.value,{componentStack:l!==null?l:""})}),t}function gu(e,n,t){var s=e.pingCache;if(s===null){s=e.pingCache=new lm;var i=new Set;s.set(n,i)}else i=s.get(n),i===void 0&&(i=new Set,s.set(n,i));i.has(t)||(i.add(t),e=jm.bind(null,e,n,t),n.then(e,e))}function vu(e){do{var n;if((n=e.tag===13)&&(n=e.memoizedState,n=n!==null?n.dehydrated!==null:!0),n)return e;e=e.return}while(e!==null);return null}function yu(e,n,t,s,i){return(e.mode&1)===0?(e===n?e.flags|=65536:(e.flags|=128,t.flags|=131072,t.flags&=-52805,t.tag===1&&(t.alternate===null?t.tag=17:(n=In(-1,1),n.tag=2,qn(t,n,1))),t.lanes|=1),e):(e.flags|=65536,e.lanes=i,e)}var um=se.ReactCurrentOwner,Ge=!1;function Ue(e,n,t,s){n.child=e===null?Fl(n,null,t,s):Ft(n,e.child,t,s)}function xu(e,n,t,s,i){t=t.render;var o=n.ref;return Bt(n,i),s=ho(e,n,t,s,o,i),t=po(),e!==null&&!Ge?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~i,zn(e,n,i)):(xe&&t&&Xi(n),n.flags|=1,Ue(e,n,s,i),n.child)}function ku(e,n,t,s,i){if(e===null){var o=t.type;return typeof o=="function"&&!Vo(o)&&o.defaultProps===void 0&&t.compare===null&&t.defaultProps===void 0?(n.tag=15,n.type=o,wu(e,n,o,s,i)):(e=zs(t.type,null,s,n,n.mode,i),e.ref=n.ref,e.return=n,n.child=e)}if(o=e.child,(e.lanes&i)===0){var l=o.memoizedProps;if(t=t.compare,t=t!==null?t:mr,t(l,s)&&e.ref===n.ref)return zn(e,n,i)}return n.flags|=1,e=tt(o,s),e.ref=n.ref,e.return=n,n.child=e}function wu(e,n,t,s,i){if(e!==null){var o=e.memoizedProps;if(mr(o,s)&&e.ref===n.ref)if(Ge=!1,n.pendingProps=s=o,(e.lanes&i)!==0)(e.flags&131072)!==0&&(Ge=!0);else return n.lanes=e.lanes,zn(e,n,i)}return So(e,n,t,s,i)}function ju(e,n,t){var s=n.pendingProps,i=s.children,o=e!==null?e.memoizedState:null;if(s.mode==="hidden")if((n.mode&1)===0)n.memoizedState={baseLanes:0,cachePool:null,transitions:null},pe(Vt,on),on|=t;else{if((t&1073741824)===0)return e=o!==null?o.baseLanes|t:t,n.lanes=n.childLanes=1073741824,n.memoizedState={baseLanes:e,cachePool:null,transitions:null},n.updateQueue=null,pe(Vt,on),on|=e,null;n.memoizedState={baseLanes:0,cachePool:null,transitions:null},s=o!==null?o.baseLanes:t,pe(Vt,on),on|=s}else o!==null?(s=o.baseLanes|t,n.memoizedState=null):s=t,pe(Vt,on),on|=s;return Ue(e,n,i,t),n.child}function Su(e,n){var t=n.ref;(e===null&&t!==null||e!==null&&e.ref!==t)&&(n.flags|=512,n.flags|=2097152)}function So(e,n,t,s,i){var o=He(t)?ut:ze.current;return o=Dt(n,o),Bt(n,i),t=ho(e,n,t,s,o,i),s=po(),e!==null&&!Ge?(n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~i,zn(e,n,i)):(xe&&s&&Xi(n),n.flags|=1,Ue(e,n,t,i),n.child)}function Nu(e,n,t,s,i){if(He(t)){var o=!0;ls(n)}else o=!1;if(Bt(n,i),n.stateNode===null)_s(e,n),mu(n,t,s),ko(n,t,s,i),s=!0;else if(e===null){var l=n.stateNode,d=n.memoizedProps;l.props=d;var m=l.context,k=t.contextType;typeof k=="object"&&k!==null?k=un(k):(k=He(t)?ut:ze.current,k=Dt(n,k));var b=t.getDerivedStateFromProps,P=typeof b=="function"||typeof l.getSnapshotBeforeUpdate=="function";P||typeof l.UNSAFE_componentWillReceiveProps!="function"&&typeof l.componentWillReceiveProps!="function"||(d!==s||m!==k)&&hu(n,l,s,k),Xn=!1;var C=n.memoizedState;l.state=C,vs(n,s,l,i),m=n.memoizedState,d!==s||C!==m||Ve.current||Xn?(typeof b=="function"&&(xo(n,t,b,s),m=n.memoizedState),(d=Xn||du(n,t,d,s,C,m,k))?(P||typeof l.UNSAFE_componentWillMount!="function"&&typeof l.componentWillMount!="function"||(typeof l.componentWillMount=="function"&&l.componentWillMount(),typeof l.UNSAFE_componentWillMount=="function"&&l.UNSAFE_componentWillMount()),typeof l.componentDidMount=="function"&&(n.flags|=4194308)):(typeof l.componentDidMount=="function"&&(n.flags|=4194308),n.memoizedProps=s,n.memoizedState=m),l.props=s,l.state=m,l.context=k,s=d):(typeof l.componentDidMount=="function"&&(n.flags|=4194308),s=!1)}else{l=n.stateNode,Bl(e,n),d=n.memoizedProps,k=n.type===n.elementType?d:yn(n.type,d),l.props=k,P=n.pendingProps,C=l.context,m=t.contextType,typeof m=="object"&&m!==null?m=un(m):(m=He(t)?ut:ze.current,m=Dt(n,m));var B=t.getDerivedStateFromProps;(b=typeof B=="function"||typeof l.getSnapshotBeforeUpdate=="function")||typeof l.UNSAFE_componentWillReceiveProps!="function"&&typeof l.componentWillReceiveProps!="function"||(d!==P||C!==m)&&hu(n,l,s,m),Xn=!1,C=n.memoizedState,l.state=C,vs(n,s,l,i);var V=n.memoizedState;d!==P||C!==V||Ve.current||Xn?(typeof B=="function"&&(xo(n,t,B,s),V=n.memoizedState),(k=Xn||du(n,t,k,s,C,V,m)||!1)?(b||typeof l.UNSAFE_componentWillUpdate!="function"&&typeof l.componentWillUpdate!="function"||(typeof l.componentWillUpdate=="function"&&l.componentWillUpdate(s,V,m),typeof l.UNSAFE_componentWillUpdate=="function"&&l.UNSAFE_componentWillUpdate(s,V,m)),typeof l.componentDidUpdate=="function"&&(n.flags|=4),typeof l.getSnapshotBeforeUpdate=="function"&&(n.flags|=1024)):(typeof l.componentDidUpdate!="function"||d===e.memoizedProps&&C===e.memoizedState||(n.flags|=4),typeof l.getSnapshotBeforeUpdate!="function"||d===e.memoizedProps&&C===e.memoizedState||(n.flags|=1024),n.memoizedProps=s,n.memoizedState=V),l.props=s,l.state=V,l.context=m,s=k):(typeof l.componentDidUpdate!="function"||d===e.memoizedProps&&C===e.memoizedState||(n.flags|=4),typeof l.getSnapshotBeforeUpdate!="function"||d===e.memoizedProps&&C===e.memoizedState||(n.flags|=1024),s=!1)}return No(e,n,t,s,o,i)}function No(e,n,t,s,i,o){Su(e,n);var l=(n.flags&128)!==0;if(!s&&!l)return i&&Pl(n,t,!1),zn(e,n,o);s=n.stateNode,um.current=n;var d=l&&typeof t.getDerivedStateFromError!="function"?null:s.render();return n.flags|=1,e!==null&&l?(n.child=Ft(n,e.child,null,o),n.child=Ft(n,null,d,o)):Ue(e,n,d,o),n.memoizedState=s.state,i&&Pl(n,t,!0),n.child}function Cu(e){var n=e.stateNode;n.pendingContext?bl(e,n.pendingContext,n.pendingContext!==n.context):n.context&&bl(e,n.context,!1),oo(e,n.containerInfo)}function _u(e,n,t,s,i){return zt(),Zi(i),n.flags|=256,Ue(e,n,t,s),n.child}var Co={dehydrated:null,treeContext:null,retryLane:0};function _o(e){return{baseLanes:e,cachePool:null,transitions:null}}function bu(e,n,t){var s=n.pendingProps,i=ke.current,o=!1,l=(n.flags&128)!==0,d;if((d=l)||(d=e!==null&&e.memoizedState===null?!1:(i&2)!==0),d?(o=!0,n.flags&=-129):(e===null||e.memoizedState!==null)&&(i|=1),pe(ke,i&1),e===null)return Ji(n),e=n.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?((n.mode&1)===0?n.lanes=1:e.data==="$!"?n.lanes=8:n.lanes=1073741824,null):(l=s.children,e=s.fallback,o?(s=n.mode,o=n.child,l={mode:"hidden",children:l},(s&1)===0&&o!==null?(o.childLanes=0,o.pendingProps=l):o=Fs(l,s,0,null),e=xt(e,s,t,null),o.return=n,e.return=n,o.sibling=e,n.child=o,n.child.memoizedState=_o(t),n.memoizedState=Co,e):bo(n,l));if(i=e.memoizedState,i!==null&&(d=i.dehydrated,d!==null))return cm(e,n,l,s,d,i,t);if(o){o=s.fallback,l=n.mode,i=e.child,d=i.sibling;var m={mode:"hidden",children:s.children};return(l&1)===0&&n.child!==i?(s=n.child,s.childLanes=0,s.pendingProps=m,n.deletions=null):(s=tt(i,m),s.subtreeFlags=i.subtreeFlags&14680064),d!==null?o=tt(d,o):(o=xt(o,l,t,null),o.flags|=2),o.return=n,s.return=n,s.sibling=o,n.child=s,s=o,o=n.child,l=e.child.memoizedState,l=l===null?_o(t):{baseLanes:l.baseLanes|t,cachePool:null,transitions:l.transitions},o.memoizedState=l,o.childLanes=e.childLanes&~t,n.memoizedState=Co,s}return o=e.child,e=o.sibling,s=tt(o,{mode:"visible",children:s.children}),(n.mode&1)===0&&(s.lanes=t),s.return=n,s.sibling=null,e!==null&&(t=n.deletions,t===null?(n.deletions=[e],n.flags|=16):t.push(e)),n.child=s,n.memoizedState=null,s}function bo(e,n){return n=Fs({mode:"visible",children:n},e.mode,0,null),n.return=e,e.child=n}function Cs(e,n,t,s){return s!==null&&Zi(s),Ft(n,e.child,null,t),e=bo(n,n.pendingProps.children),e.flags|=2,n.memoizedState=null,e}function cm(e,n,t,s,i,o,l){if(t)return n.flags&256?(n.flags&=-257,s=wo(Error(c(422))),Cs(e,n,l,s)):n.memoizedState!==null?(n.child=e.child,n.flags|=128,null):(o=s.fallback,i=n.mode,s=Fs({mode:"visible",children:s.children},i,0,null),o=xt(o,i,l,null),o.flags|=2,s.return=n,o.return=n,s.sibling=o,n.child=s,(n.mode&1)!==0&&Ft(n,e.child,null,l),n.child.memoizedState=_o(l),n.memoizedState=Co,o);if((n.mode&1)===0)return Cs(e,n,l,null);if(i.data==="$!"){if(s=i.nextSibling&&i.nextSibling.dataset,s)var d=s.dgst;return s=d,o=Error(c(419)),s=wo(o,s,void 0),Cs(e,n,l,s)}if(d=(l&e.childLanes)!==0,Ge||d){if(s=Re,s!==null){switch(l&-l){case 4:i=2;break;case 16:i=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:i=32;break;case 536870912:i=268435456;break;default:i=0}i=(i&(s.suspendedLanes|l))!==0?0:i,i!==0&&i!==o.retryLane&&(o.retryLane=i,An(e,i),wn(s,e,i,-1))}return $o(),s=wo(Error(c(421))),Cs(e,n,l,s)}return i.data==="$?"?(n.flags|=128,n.child=e.child,n=Sm.bind(null,e),i._reactRetry=n,null):(e=o.treeContext,sn=Hn(i.nextSibling),rn=n,xe=!0,vn=null,e!==null&&(an[ln++]=Rn,an[ln++]=Dn,an[ln++]=ct,Rn=e.id,Dn=e.overflow,ct=n),n=bo(n,s.children),n.flags|=4096,n)}function Eu(e,n,t){e.lanes|=n;var s=e.alternate;s!==null&&(s.lanes|=n),ro(e.return,n,t)}function Eo(e,n,t,s,i){var o=e.memoizedState;o===null?e.memoizedState={isBackwards:n,rendering:null,renderingStartTime:0,last:s,tail:t,tailMode:i}:(o.isBackwards=n,o.rendering=null,o.renderingStartTime=0,o.last=s,o.tail=t,o.tailMode=i)}function Pu(e,n,t){var s=n.pendingProps,i=s.revealOrder,o=s.tail;if(Ue(e,n,s.children,t),s=ke.current,(s&2)!==0)s=s&1|2,n.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=n.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Eu(e,t,n);else if(e.tag===19)Eu(e,t,n);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===n)break e;for(;e.sibling===null;){if(e.return===null||e.return===n)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}s&=1}if(pe(ke,s),(n.mode&1)===0)n.memoizedState=null;else switch(i){case"forwards":for(t=n.child,i=null;t!==null;)e=t.alternate,e!==null&&ys(e)===null&&(i=t),t=t.sibling;t=i,t===null?(i=n.child,n.child=null):(i=t.sibling,t.sibling=null),Eo(n,!1,i,t,o);break;case"backwards":for(t=null,i=n.child,n.child=null;i!==null;){if(e=i.alternate,e!==null&&ys(e)===null){n.child=i;break}e=i.sibling,i.sibling=t,t=i,i=e}Eo(n,!0,t,null,o);break;case"together":Eo(n,!1,null,null,void 0);break;default:n.memoizedState=null}return n.child}function _s(e,n){(n.mode&1)===0&&e!==null&&(e.alternate=null,n.alternate=null,n.flags|=2)}function zn(e,n,t){if(e!==null&&(n.dependencies=e.dependencies),ft|=n.lanes,(t&n.childLanes)===0)return null;if(e!==null&&n.child!==e.child)throw Error(c(153));if(n.child!==null){for(e=n.child,t=tt(e,e.pendingProps),n.child=t,t.return=n;e.sibling!==null;)e=e.sibling,t=t.sibling=tt(e,e.pendingProps),t.return=n;t.sibling=null}return n.child}function dm(e,n,t){switch(n.tag){case 3:Cu(n),zt();break;case 5:$l(n);break;case 1:He(n.type)&&ls(n);break;case 4:oo(n,n.stateNode.containerInfo);break;case 10:var s=n.type._context,i=n.memoizedProps.value;pe(ps,s._currentValue),s._currentValue=i;break;case 13:if(s=n.memoizedState,s!==null)return s.dehydrated!==null?(pe(ke,ke.current&1),n.flags|=128,null):(t&n.child.childLanes)!==0?bu(e,n,t):(pe(ke,ke.current&1),e=zn(e,n,t),e!==null?e.sibling:null);pe(ke,ke.current&1);break;case 19:if(s=(t&n.childLanes)!==0,(e.flags&128)!==0){if(s)return Pu(e,n,t);n.flags|=128}if(i=n.memoizedState,i!==null&&(i.rendering=null,i.tail=null,i.lastEffect=null),pe(ke,ke.current),s)break;return null;case 22:case 23:return n.lanes=0,ju(e,n,t)}return zn(e,n,t)}var Tu,Po,Mu,Lu;Tu=function(e,n){for(var t=n.child;t!==null;){if(t.tag===5||t.tag===6)e.appendChild(t.stateNode);else if(t.tag!==4&&t.child!==null){t.child.return=t,t=t.child;continue}if(t===n)break;for(;t.sibling===null;){if(t.return===null||t.return===n)return;t=t.return}t.sibling.return=t.return,t=t.sibling}},Po=function(){},Mu=function(e,n,t,s){var i=e.memoizedProps;if(i!==s){e=n.stateNode,ht(bn.current);var o=null;switch(t){case"input":i=ri(e,i),s=ri(e,s),o=[];break;case"select":i=$({},i,{value:void 0}),s=$({},s,{value:void 0}),o=[];break;case"textarea":i=oi(e,i),s=oi(e,s),o=[];break;default:typeof i.onClick!="function"&&typeof s.onClick=="function"&&(e.onclick=is)}li(t,s);var l;t=null;for(k in i)if(!s.hasOwnProperty(k)&&i.hasOwnProperty(k)&&i[k]!=null)if(k==="style"){var d=i[k];for(l in d)d.hasOwnProperty(l)&&(t||(t={}),t[l]="")}else k!=="dangerouslySetInnerHTML"&&k!=="children"&&k!=="suppressContentEditableWarning"&&k!=="suppressHydrationWarning"&&k!=="autoFocus"&&(f.hasOwnProperty(k)?o||(o=[]):(o=o||[]).push(k,null));for(k in s){var m=s[k];if(d=i!=null?i[k]:void 0,s.hasOwnProperty(k)&&m!==d&&(m!=null||d!=null))if(k==="style")if(d){for(l in d)!d.hasOwnProperty(l)||m&&m.hasOwnProperty(l)||(t||(t={}),t[l]="");for(l in m)m.hasOwnProperty(l)&&d[l]!==m[l]&&(t||(t={}),t[l]=m[l])}else t||(o||(o=[]),o.push(k,t)),t=m;else k==="dangerouslySetInnerHTML"?(m=m?m.__html:void 0,d=d?d.__html:void 0,m!=null&&d!==m&&(o=o||[]).push(k,m)):k==="children"?typeof m!="string"&&typeof m!="number"||(o=o||[]).push(k,""+m):k!=="suppressContentEditableWarning"&&k!=="suppressHydrationWarning"&&(f.hasOwnProperty(k)?(m!=null&&k==="onScroll"&&ge("scroll",e),o||d===m||(o=[])):(o=o||[]).push(k,m))}t&&(o=o||[]).push("style",t);var k=o;(n.updateQueue=k)&&(n.flags|=4)}},Lu=function(e,n,t,s){t!==s&&(n.flags|=4)};function br(e,n){if(!xe)switch(e.tailMode){case"hidden":n=e.tail;for(var t=null;n!==null;)n.alternate!==null&&(t=n),n=n.sibling;t===null?e.tail=null:t.sibling=null;break;case"collapsed":t=e.tail;for(var s=null;t!==null;)t.alternate!==null&&(s=t),t=t.sibling;s===null?n||e.tail===null?e.tail=null:e.tail.sibling=null:s.sibling=null}}function Oe(e){var n=e.alternate!==null&&e.alternate.child===e.child,t=0,s=0;if(n)for(var i=e.child;i!==null;)t|=i.lanes|i.childLanes,s|=i.subtreeFlags&14680064,s|=i.flags&14680064,i.return=e,i=i.sibling;else for(i=e.child;i!==null;)t|=i.lanes|i.childLanes,s|=i.subtreeFlags,s|=i.flags,i.return=e,i=i.sibling;return e.subtreeFlags|=s,e.childLanes=t,n}function mm(e,n,t){var s=n.pendingProps;switch(qi(n),n.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Oe(n),null;case 1:return He(n.type)&&as(),Oe(n),null;case 3:return s=n.stateNode,Ut(),ve(Ve),ve(ze),uo(),s.pendingContext&&(s.context=s.pendingContext,s.pendingContext=null),(e===null||e.child===null)&&(ms(n)?n.flags|=4:e===null||e.memoizedState.isDehydrated&&(n.flags&256)===0||(n.flags|=1024,vn!==null&&(Bo(vn),vn=null))),Po(e,n),Oe(n),null;case 5:ao(n);var i=ht(jr.current);if(t=n.type,e!==null&&n.stateNode!=null)Mu(e,n,t,s,i),e.ref!==n.ref&&(n.flags|=512,n.flags|=2097152);else{if(!s){if(n.stateNode===null)throw Error(c(166));return Oe(n),null}if(e=ht(bn.current),ms(n)){s=n.stateNode,t=n.type;var o=n.memoizedProps;switch(s[_n]=n,s[vr]=o,e=(n.mode&1)!==0,t){case"dialog":ge("cancel",s),ge("close",s);break;case"iframe":case"object":case"embed":ge("load",s);break;case"video":case"audio":for(i=0;i<pr.length;i++)ge(pr[i],s);break;case"source":ge("error",s);break;case"img":case"image":case"link":ge("error",s),ge("load",s);break;case"details":ge("toggle",s);break;case"input":ma(s,o),ge("invalid",s);break;case"select":s._wrapperState={wasMultiple:!!o.multiple},ge("invalid",s);break;case"textarea":fa(s,o),ge("invalid",s)}li(t,o),i=null;for(var l in o)if(o.hasOwnProperty(l)){var d=o[l];l==="children"?typeof d=="string"?s.textContent!==d&&(o.suppressHydrationWarning!==!0&&ss(s.textContent,d,e),i=["children",d]):typeof d=="number"&&s.textContent!==""+d&&(o.suppressHydrationWarning!==!0&&ss(s.textContent,d,e),i=["children",""+d]):f.hasOwnProperty(l)&&d!=null&&l==="onScroll"&&ge("scroll",s)}switch(t){case"input":Ar(s),pa(s,o,!0);break;case"textarea":Ar(s),va(s);break;case"select":case"option":break;default:typeof o.onClick=="function"&&(s.onclick=is)}s=i,n.updateQueue=s,s!==null&&(n.flags|=4)}else{l=i.nodeType===9?i:i.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=ya(t)),e==="http://www.w3.org/1999/xhtml"?t==="script"?(e=l.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof s.is=="string"?e=l.createElement(t,{is:s.is}):(e=l.createElement(t),t==="select"&&(l=e,s.multiple?l.multiple=!0:s.size&&(l.size=s.size))):e=l.createElementNS(e,t),e[_n]=n,e[vr]=s,Tu(e,n,!1,!1),n.stateNode=e;e:{switch(l=ui(t,s),t){case"dialog":ge("cancel",e),ge("close",e),i=s;break;case"iframe":case"object":case"embed":ge("load",e),i=s;break;case"video":case"audio":for(i=0;i<pr.length;i++)ge(pr[i],e);i=s;break;case"source":ge("error",e),i=s;break;case"img":case"image":case"link":ge("error",e),ge("load",e),i=s;break;case"details":ge("toggle",e),i=s;break;case"input":ma(e,s),i=ri(e,s),ge("invalid",e);break;case"option":i=s;break;case"select":e._wrapperState={wasMultiple:!!s.multiple},i=$({},s,{value:void 0}),ge("invalid",e);break;case"textarea":fa(e,s),i=oi(e,s),ge("invalid",e);break;default:i=s}li(t,i),d=i;for(o in d)if(d.hasOwnProperty(o)){var m=d[o];o==="style"?wa(e,m):o==="dangerouslySetInnerHTML"?(m=m?m.__html:void 0,m!=null&&xa(e,m)):o==="children"?typeof m=="string"?(t!=="textarea"||m!=="")&&Xt(e,m):typeof m=="number"&&Xt(e,""+m):o!=="suppressContentEditableWarning"&&o!=="suppressHydrationWarning"&&o!=="autoFocus"&&(f.hasOwnProperty(o)?m!=null&&o==="onScroll"&&ge("scroll",e):m!=null&&re(e,o,m,l))}switch(t){case"input":Ar(e),pa(e,s,!1);break;case"textarea":Ar(e),va(e);break;case"option":s.value!=null&&e.setAttribute("value",""+ce(s.value));break;case"select":e.multiple=!!s.multiple,o=s.value,o!=null?jt(e,!!s.multiple,o,!1):s.defaultValue!=null&&jt(e,!!s.multiple,s.defaultValue,!0);break;default:typeof i.onClick=="function"&&(e.onclick=is)}switch(t){case"button":case"input":case"select":case"textarea":s=!!s.autoFocus;break e;case"img":s=!0;break e;default:s=!1}}s&&(n.flags|=4)}n.ref!==null&&(n.flags|=512,n.flags|=2097152)}return Oe(n),null;case 6:if(e&&n.stateNode!=null)Lu(e,n,e.memoizedProps,s);else{if(typeof s!="string"&&n.stateNode===null)throw Error(c(166));if(t=ht(jr.current),ht(bn.current),ms(n)){if(s=n.stateNode,t=n.memoizedProps,s[_n]=n,(o=s.nodeValue!==t)&&(e=rn,e!==null))switch(e.tag){case 3:ss(s.nodeValue,t,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&ss(s.nodeValue,t,(e.mode&1)!==0)}o&&(n.flags|=4)}else s=(t.nodeType===9?t:t.ownerDocument).createTextNode(s),s[_n]=n,n.stateNode=s}return Oe(n),null;case 13:if(ve(ke),s=n.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(xe&&sn!==null&&(n.mode&1)!==0&&(n.flags&128)===0)Al(),zt(),n.flags|=98560,o=!1;else if(o=ms(n),s!==null&&s.dehydrated!==null){if(e===null){if(!o)throw Error(c(318));if(o=n.memoizedState,o=o!==null?o.dehydrated:null,!o)throw Error(c(317));o[_n]=n}else zt(),(n.flags&128)===0&&(n.memoizedState=null),n.flags|=4;Oe(n),o=!1}else vn!==null&&(Bo(vn),vn=null),o=!0;if(!o)return n.flags&65536?n:null}return(n.flags&128)!==0?(n.lanes=t,n):(s=s!==null,s!==(e!==null&&e.memoizedState!==null)&&s&&(n.child.flags|=8192,(n.mode&1)!==0&&(e===null||(ke.current&1)!==0?Te===0&&(Te=3):$o())),n.updateQueue!==null&&(n.flags|=4),Oe(n),null);case 4:return Ut(),Po(e,n),e===null&&fr(n.stateNode.containerInfo),Oe(n),null;case 10:return to(n.type._context),Oe(n),null;case 17:return He(n.type)&&as(),Oe(n),null;case 19:if(ve(ke),o=n.memoizedState,o===null)return Oe(n),null;if(s=(n.flags&128)!==0,l=o.rendering,l===null)if(s)br(o,!1);else{if(Te!==0||e!==null&&(e.flags&128)!==0)for(e=n.child;e!==null;){if(l=ys(e),l!==null){for(n.flags|=128,br(o,!1),s=l.updateQueue,s!==null&&(n.updateQueue=s,n.flags|=4),n.subtreeFlags=0,s=t,t=n.child;t!==null;)o=t,e=s,o.flags&=14680066,l=o.alternate,l===null?(o.childLanes=0,o.lanes=e,o.child=null,o.subtreeFlags=0,o.memoizedProps=null,o.memoizedState=null,o.updateQueue=null,o.dependencies=null,o.stateNode=null):(o.childLanes=l.childLanes,o.lanes=l.lanes,o.child=l.child,o.subtreeFlags=0,o.deletions=null,o.memoizedProps=l.memoizedProps,o.memoizedState=l.memoizedState,o.updateQueue=l.updateQueue,o.type=l.type,e=l.dependencies,o.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),t=t.sibling;return pe(ke,ke.current&1|2),n.child}e=e.sibling}o.tail!==null&&Ne()>Ht&&(n.flags|=128,s=!0,br(o,!1),n.lanes=4194304)}else{if(!s)if(e=ys(l),e!==null){if(n.flags|=128,s=!0,t=e.updateQueue,t!==null&&(n.updateQueue=t,n.flags|=4),br(o,!0),o.tail===null&&o.tailMode==="hidden"&&!l.alternate&&!xe)return Oe(n),null}else 2*Ne()-o.renderingStartTime>Ht&&t!==1073741824&&(n.flags|=128,s=!0,br(o,!1),n.lanes=4194304);o.isBackwards?(l.sibling=n.child,n.child=l):(t=o.last,t!==null?t.sibling=l:n.child=l,o.last=l)}return o.tail!==null?(n=o.tail,o.rendering=n,o.tail=n.sibling,o.renderingStartTime=Ne(),n.sibling=null,t=ke.current,pe(ke,s?t&1|2:t&1),n):(Oe(n),null);case 22:case 23:return Wo(),s=n.memoizedState!==null,e!==null&&e.memoizedState!==null!==s&&(n.flags|=8192),s&&(n.mode&1)!==0?(on&1073741824)!==0&&(Oe(n),n.subtreeFlags&6&&(n.flags|=8192)):Oe(n),null;case 24:return null;case 25:return null}throw Error(c(156,n.tag))}function hm(e,n){switch(qi(n),n.tag){case 1:return He(n.type)&&as(),e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 3:return Ut(),ve(Ve),ve(ze),uo(),e=n.flags,(e&65536)!==0&&(e&128)===0?(n.flags=e&-65537|128,n):null;case 5:return ao(n),null;case 13:if(ve(ke),e=n.memoizedState,e!==null&&e.dehydrated!==null){if(n.alternate===null)throw Error(c(340));zt()}return e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 19:return ve(ke),null;case 4:return Ut(),null;case 10:return to(n.type._context),null;case 22:case 23:return Wo(),null;case 24:return null;default:return null}}var bs=!1,Be=!1,pm=typeof WeakSet=="function"?WeakSet:Set,W=null;function $t(e,n){var t=e.ref;if(t!==null)if(typeof t=="function")try{t(null)}catch(s){Se(e,n,s)}else t.current=null}function To(e,n,t){try{t()}catch(s){Se(e,n,s)}}var Ru=!1;function fm(e,n){if(Ui=Kr,e=dl(),Ri(e)){if("selectionStart"in e)var t={start:e.selectionStart,end:e.selectionEnd};else e:{t=(t=e.ownerDocument)&&t.defaultView||window;var s=t.getSelection&&t.getSelection();if(s&&s.rangeCount!==0){t=s.anchorNode;var i=s.anchorOffset,o=s.focusNode;s=s.focusOffset;try{t.nodeType,o.nodeType}catch{t=null;break e}var l=0,d=-1,m=-1,k=0,b=0,P=e,C=null;n:for(;;){for(var B;P!==t||i!==0&&P.nodeType!==3||(d=l+i),P!==o||s!==0&&P.nodeType!==3||(m=l+s),P.nodeType===3&&(l+=P.nodeValue.length),(B=P.firstChild)!==null;)C=P,P=B;for(;;){if(P===e)break n;if(C===t&&++k===i&&(d=l),C===o&&++b===s&&(m=l),(B=P.nextSibling)!==null)break;P=C,C=P.parentNode}P=B}t=d===-1||m===-1?null:{start:d,end:m}}else t=null}t=t||{start:0,end:0}}else t=null;for(Wi={focusedElem:e,selectionRange:t},Kr=!1,W=n;W!==null;)if(n=W,e=n.child,(n.subtreeFlags&1028)!==0&&e!==null)e.return=n,W=e;else for(;W!==null;){n=W;try{var V=n.alternate;if((n.flags&1024)!==0)switch(n.tag){case 0:case 11:case 15:break;case 1:if(V!==null){var H=V.memoizedProps,Ce=V.memoizedState,v=n.stateNode,h=v.getSnapshotBeforeUpdate(n.elementType===n.type?H:yn(n.type,H),Ce);v.__reactInternalSnapshotBeforeUpdate=h}break;case 3:var x=n.stateNode.containerInfo;x.nodeType===1?x.textContent="":x.nodeType===9&&x.documentElement&&x.removeChild(x.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(c(163))}}catch(L){Se(n,n.return,L)}if(e=n.sibling,e!==null){e.return=n.return,W=e;break}W=n.return}return V=Ru,Ru=!1,V}function Er(e,n,t){var s=n.updateQueue;if(s=s!==null?s.lastEffect:null,s!==null){var i=s=s.next;do{if((i.tag&e)===e){var o=i.destroy;i.destroy=void 0,o!==void 0&&To(n,t,o)}i=i.next}while(i!==s)}}function Es(e,n){if(n=n.updateQueue,n=n!==null?n.lastEffect:null,n!==null){var t=n=n.next;do{if((t.tag&e)===e){var s=t.create;t.destroy=s()}t=t.next}while(t!==n)}}function Mo(e){var n=e.ref;if(n!==null){var t=e.stateNode;switch(e.tag){case 5:e=t;break;default:e=t}typeof n=="function"?n(e):n.current=e}}function Du(e){var n=e.alternate;n!==null&&(e.alternate=null,Du(n)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(n=e.stateNode,n!==null&&(delete n[_n],delete n[vr],delete n[Gi],delete n[Yd],delete n[Jd])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function Au(e){return e.tag===5||e.tag===3||e.tag===4}function Iu(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||Au(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Lo(e,n,t){var s=e.tag;if(s===5||s===6)e=e.stateNode,n?t.nodeType===8?t.parentNode.insertBefore(e,n):t.insertBefore(e,n):(t.nodeType===8?(n=t.parentNode,n.insertBefore(e,t)):(n=t,n.appendChild(e)),t=t._reactRootContainer,t!=null||n.onclick!==null||(n.onclick=is));else if(s!==4&&(e=e.child,e!==null))for(Lo(e,n,t),e=e.sibling;e!==null;)Lo(e,n,t),e=e.sibling}function Ro(e,n,t){var s=e.tag;if(s===5||s===6)e=e.stateNode,n?t.insertBefore(e,n):t.appendChild(e);else if(s!==4&&(e=e.child,e!==null))for(Ro(e,n,t),e=e.sibling;e!==null;)Ro(e,n,t),e=e.sibling}var Ae=null,xn=!1;function Yn(e,n,t){for(t=t.child;t!==null;)zu(e,n,t),t=t.sibling}function zu(e,n,t){if(Cn&&typeof Cn.onCommitFiberUnmount=="function")try{Cn.onCommitFiberUnmount(Ur,t)}catch{}switch(t.tag){case 5:Be||$t(t,n);case 6:var s=Ae,i=xn;Ae=null,Yn(e,n,t),Ae=s,xn=i,Ae!==null&&(xn?(e=Ae,t=t.stateNode,e.nodeType===8?e.parentNode.removeChild(t):e.removeChild(t)):Ae.removeChild(t.stateNode));break;case 18:Ae!==null&&(xn?(e=Ae,t=t.stateNode,e.nodeType===8?Hi(e.parentNode,t):e.nodeType===1&&Hi(e,t),or(e)):Hi(Ae,t.stateNode));break;case 4:s=Ae,i=xn,Ae=t.stateNode.containerInfo,xn=!0,Yn(e,n,t),Ae=s,xn=i;break;case 0:case 11:case 14:case 15:if(!Be&&(s=t.updateQueue,s!==null&&(s=s.lastEffect,s!==null))){i=s=s.next;do{var o=i,l=o.destroy;o=o.tag,l!==void 0&&((o&2)!==0||(o&4)!==0)&&To(t,n,l),i=i.next}while(i!==s)}Yn(e,n,t);break;case 1:if(!Be&&($t(t,n),s=t.stateNode,typeof s.componentWillUnmount=="function"))try{s.props=t.memoizedProps,s.state=t.memoizedState,s.componentWillUnmount()}catch(d){Se(t,n,d)}Yn(e,n,t);break;case 21:Yn(e,n,t);break;case 22:t.mode&1?(Be=(s=Be)||t.memoizedState!==null,Yn(e,n,t),Be=s):Yn(e,n,t);break;default:Yn(e,n,t)}}function Fu(e){var n=e.updateQueue;if(n!==null){e.updateQueue=null;var t=e.stateNode;t===null&&(t=e.stateNode=new pm),n.forEach(function(s){var i=Nm.bind(null,e,s);t.has(s)||(t.add(s),s.then(i,i))})}}function kn(e,n){var t=n.deletions;if(t!==null)for(var s=0;s<t.length;s++){var i=t[s];try{var o=e,l=n,d=l;e:for(;d!==null;){switch(d.tag){case 5:Ae=d.stateNode,xn=!1;break e;case 3:Ae=d.stateNode.containerInfo,xn=!0;break e;case 4:Ae=d.stateNode.containerInfo,xn=!0;break e}d=d.return}if(Ae===null)throw Error(c(160));zu(o,l,i),Ae=null,xn=!1;var m=i.alternate;m!==null&&(m.return=null),i.return=null}catch(k){Se(i,n,k)}}if(n.subtreeFlags&12854)for(n=n.child;n!==null;)Ou(n,e),n=n.sibling}function Ou(e,n){var t=e.alternate,s=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(kn(n,e),Pn(e),s&4){try{Er(3,e,e.return),Es(3,e)}catch(H){Se(e,e.return,H)}try{Er(5,e,e.return)}catch(H){Se(e,e.return,H)}}break;case 1:kn(n,e),Pn(e),s&512&&t!==null&&$t(t,t.return);break;case 5:if(kn(n,e),Pn(e),s&512&&t!==null&&$t(t,t.return),e.flags&32){var i=e.stateNode;try{Xt(i,"")}catch(H){Se(e,e.return,H)}}if(s&4&&(i=e.stateNode,i!=null)){var o=e.memoizedProps,l=t!==null?t.memoizedProps:o,d=e.type,m=e.updateQueue;if(e.updateQueue=null,m!==null)try{d==="input"&&o.type==="radio"&&o.name!=null&&ha(i,o),ui(d,l);var k=ui(d,o);for(l=0;l<m.length;l+=2){var b=m[l],P=m[l+1];b==="style"?wa(i,P):b==="dangerouslySetInnerHTML"?xa(i,P):b==="children"?Xt(i,P):re(i,b,P,k)}switch(d){case"input":si(i,o);break;case"textarea":ga(i,o);break;case"select":var C=i._wrapperState.wasMultiple;i._wrapperState.wasMultiple=!!o.multiple;var B=o.value;B!=null?jt(i,!!o.multiple,B,!1):C!==!!o.multiple&&(o.defaultValue!=null?jt(i,!!o.multiple,o.defaultValue,!0):jt(i,!!o.multiple,o.multiple?[]:"",!1))}i[vr]=o}catch(H){Se(e,e.return,H)}}break;case 6:if(kn(n,e),Pn(e),s&4){if(e.stateNode===null)throw Error(c(162));i=e.stateNode,o=e.memoizedProps;try{i.nodeValue=o}catch(H){Se(e,e.return,H)}}break;case 3:if(kn(n,e),Pn(e),s&4&&t!==null&&t.memoizedState.isDehydrated)try{or(n.containerInfo)}catch(H){Se(e,e.return,H)}break;case 4:kn(n,e),Pn(e);break;case 13:kn(n,e),Pn(e),i=e.child,i.flags&8192&&(o=i.memoizedState!==null,i.stateNode.isHidden=o,!o||i.alternate!==null&&i.alternate.memoizedState!==null||(Io=Ne())),s&4&&Fu(e);break;case 22:if(b=t!==null&&t.memoizedState!==null,e.mode&1?(Be=(k=Be)||b,kn(n,e),Be=k):kn(n,e),Pn(e),s&8192){if(k=e.memoizedState!==null,(e.stateNode.isHidden=k)&&!b&&(e.mode&1)!==0)for(W=e,b=e.child;b!==null;){for(P=W=b;W!==null;){switch(C=W,B=C.child,C.tag){case 0:case 11:case 14:case 15:Er(4,C,C.return);break;case 1:$t(C,C.return);var V=C.stateNode;if(typeof V.componentWillUnmount=="function"){s=C,t=C.return;try{n=s,V.props=n.memoizedProps,V.state=n.memoizedState,V.componentWillUnmount()}catch(H){Se(s,t,H)}}break;case 5:$t(C,C.return);break;case 22:if(C.memoizedState!==null){Wu(P);continue}}B!==null?(B.return=C,W=B):Wu(P)}b=b.sibling}e:for(b=null,P=e;;){if(P.tag===5){if(b===null){b=P;try{i=P.stateNode,k?(o=i.style,typeof o.setProperty=="function"?o.setProperty("display","none","important"):o.display="none"):(d=P.stateNode,m=P.memoizedProps.style,l=m!=null&&m.hasOwnProperty("display")?m.display:null,d.style.display=ka("display",l))}catch(H){Se(e,e.return,H)}}}else if(P.tag===6){if(b===null)try{P.stateNode.nodeValue=k?"":P.memoizedProps}catch(H){Se(e,e.return,H)}}else if((P.tag!==22&&P.tag!==23||P.memoizedState===null||P===e)&&P.child!==null){P.child.return=P,P=P.child;continue}if(P===e)break e;for(;P.sibling===null;){if(P.return===null||P.return===e)break e;b===P&&(b=null),P=P.return}b===P&&(b=null),P.sibling.return=P.return,P=P.sibling}}break;case 19:kn(n,e),Pn(e),s&4&&Fu(e);break;case 21:break;default:kn(n,e),Pn(e)}}function Pn(e){var n=e.flags;if(n&2){try{e:{for(var t=e.return;t!==null;){if(Au(t)){var s=t;break e}t=t.return}throw Error(c(160))}switch(s.tag){case 5:var i=s.stateNode;s.flags&32&&(Xt(i,""),s.flags&=-33);var o=Iu(e);Ro(e,o,i);break;case 3:case 4:var l=s.stateNode.containerInfo,d=Iu(e);Lo(e,d,l);break;default:throw Error(c(161))}}catch(m){Se(e,e.return,m)}e.flags&=-3}n&4096&&(e.flags&=-4097)}function gm(e,n,t){W=e,Bu(e)}function Bu(e,n,t){for(var s=(e.mode&1)!==0;W!==null;){var i=W,o=i.child;if(i.tag===22&&s){var l=i.memoizedState!==null||bs;if(!l){var d=i.alternate,m=d!==null&&d.memoizedState!==null||Be;d=bs;var k=Be;if(bs=l,(Be=m)&&!k)for(W=i;W!==null;)l=W,m=l.child,l.tag===22&&l.memoizedState!==null?$u(i):m!==null?(m.return=l,W=m):$u(i);for(;o!==null;)W=o,Bu(o),o=o.sibling;W=i,bs=d,Be=k}Uu(e)}else(i.subtreeFlags&8772)!==0&&o!==null?(o.return=i,W=o):Uu(e)}}function Uu(e){for(;W!==null;){var n=W;if((n.flags&8772)!==0){var t=n.alternate;try{if((n.flags&8772)!==0)switch(n.tag){case 0:case 11:case 15:Be||Es(5,n);break;case 1:var s=n.stateNode;if(n.flags&4&&!Be)if(t===null)s.componentDidMount();else{var i=n.elementType===n.type?t.memoizedProps:yn(n.type,t.memoizedProps);s.componentDidUpdate(i,t.memoizedState,s.__reactInternalSnapshotBeforeUpdate)}var o=n.updateQueue;o!==null&&Wl(n,o,s);break;case 3:var l=n.updateQueue;if(l!==null){if(t=null,n.child!==null)switch(n.child.tag){case 5:t=n.child.stateNode;break;case 1:t=n.child.stateNode}Wl(n,l,t)}break;case 5:var d=n.stateNode;if(t===null&&n.flags&4){t=d;var m=n.memoizedProps;switch(n.type){case"button":case"input":case"select":case"textarea":m.autoFocus&&t.focus();break;case"img":m.src&&(t.src=m.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(n.memoizedState===null){var k=n.alternate;if(k!==null){var b=k.memoizedState;if(b!==null){var P=b.dehydrated;P!==null&&or(P)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(c(163))}Be||n.flags&512&&Mo(n)}catch(C){Se(n,n.return,C)}}if(n===e){W=null;break}if(t=n.sibling,t!==null){t.return=n.return,W=t;break}W=n.return}}function Wu(e){for(;W!==null;){var n=W;if(n===e){W=null;break}var t=n.sibling;if(t!==null){t.return=n.return,W=t;break}W=n.return}}function $u(e){for(;W!==null;){var n=W;try{switch(n.tag){case 0:case 11:case 15:var t=n.return;try{Es(4,n)}catch(m){Se(n,t,m)}break;case 1:var s=n.stateNode;if(typeof s.componentDidMount=="function"){var i=n.return;try{s.componentDidMount()}catch(m){Se(n,i,m)}}var o=n.return;try{Mo(n)}catch(m){Se(n,o,m)}break;case 5:var l=n.return;try{Mo(n)}catch(m){Se(n,l,m)}}}catch(m){Se(n,n.return,m)}if(n===e){W=null;break}var d=n.sibling;if(d!==null){d.return=n.return,W=d;break}W=n.return}}var vm=Math.ceil,Ps=se.ReactCurrentDispatcher,Do=se.ReactCurrentOwner,dn=se.ReactCurrentBatchConfig,oe=0,Re=null,_e=null,Ie=0,on=0,Vt=Gn(0),Te=0,Pr=null,ft=0,Ts=0,Ao=0,Tr=null,Ke=null,Io=0,Ht=1/0,Fn=null,Ms=!1,zo=null,Jn=null,Ls=!1,Zn=null,Rs=0,Mr=0,Fo=null,Ds=-1,As=0;function We(){return(oe&6)!==0?Ne():Ds!==-1?Ds:Ds=Ne()}function et(e){return(e.mode&1)===0?1:(oe&2)!==0&&Ie!==0?Ie&-Ie:em.transition!==null?(As===0&&(As=Ia()),As):(e=de,e!==0||(e=window.event,e=e===void 0?16:Ha(e.type)),e)}function wn(e,n,t,s){if(50<Mr)throw Mr=0,Fo=null,Error(c(185));nr(e,t,s),((oe&2)===0||e!==Re)&&(e===Re&&((oe&2)===0&&(Ts|=t),Te===4&&nt(e,Ie)),Qe(e,s),t===1&&oe===0&&(n.mode&1)===0&&(Ht=Ne()+500,us&&Qn()))}function Qe(e,n){var t=e.callbackNode;ed(e,n);var s=Vr(e,e===Re?Ie:0);if(s===0)t!==null&&Ra(t),e.callbackNode=null,e.callbackPriority=0;else if(n=s&-s,e.callbackPriority!==n){if(t!=null&&Ra(t),n===1)e.tag===0?Zd(Hu.bind(null,e)):Tl(Hu.bind(null,e)),Xd(function(){(oe&6)===0&&Qn()}),t=null;else{switch(za(s)){case 1:t=gi;break;case 4:t=Da;break;case 16:t=Br;break;case 536870912:t=Aa;break;default:t=Br}t=Zu(t,Vu.bind(null,e))}e.callbackPriority=n,e.callbackNode=t}}function Vu(e,n){if(Ds=-1,As=0,(oe&6)!==0)throw Error(c(327));var t=e.callbackNode;if(Gt()&&e.callbackNode!==t)return null;var s=Vr(e,e===Re?Ie:0);if(s===0)return null;if((s&30)!==0||(s&e.expiredLanes)!==0||n)n=Is(e,s);else{n=s;var i=oe;oe|=2;var o=Ku();(Re!==e||Ie!==n)&&(Fn=null,Ht=Ne()+500,vt(e,n));do try{km();break}catch(d){Gu(e,d)}while(!0);no(),Ps.current=o,oe=i,_e!==null?n=0:(Re=null,Ie=0,n=Te)}if(n!==0){if(n===2&&(i=vi(e),i!==0&&(s=i,n=Oo(e,i))),n===1)throw t=Pr,vt(e,0),nt(e,s),Qe(e,Ne()),t;if(n===6)nt(e,s);else{if(i=e.current.alternate,(s&30)===0&&!ym(i)&&(n=Is(e,s),n===2&&(o=vi(e),o!==0&&(s=o,n=Oo(e,o))),n===1))throw t=Pr,vt(e,0),nt(e,s),Qe(e,Ne()),t;switch(e.finishedWork=i,e.finishedLanes=s,n){case 0:case 1:throw Error(c(345));case 2:yt(e,Ke,Fn);break;case 3:if(nt(e,s),(s&130023424)===s&&(n=Io+500-Ne(),10<n)){if(Vr(e,0)!==0)break;if(i=e.suspendedLanes,(i&s)!==s){We(),e.pingedLanes|=e.suspendedLanes&i;break}e.timeoutHandle=Vi(yt.bind(null,e,Ke,Fn),n);break}yt(e,Ke,Fn);break;case 4:if(nt(e,s),(s&4194240)===s)break;for(n=e.eventTimes,i=-1;0<s;){var l=31-fn(s);o=1<<l,l=n[l],l>i&&(i=l),s&=~o}if(s=i,s=Ne()-s,s=(120>s?120:480>s?480:1080>s?1080:1920>s?1920:3e3>s?3e3:4320>s?4320:1960*vm(s/1960))-s,10<s){e.timeoutHandle=Vi(yt.bind(null,e,Ke,Fn),s);break}yt(e,Ke,Fn);break;case 5:yt(e,Ke,Fn);break;default:throw Error(c(329))}}}return Qe(e,Ne()),e.callbackNode===t?Vu.bind(null,e):null}function Oo(e,n){var t=Tr;return e.current.memoizedState.isDehydrated&&(vt(e,n).flags|=256),e=Is(e,n),e!==2&&(n=Ke,Ke=t,n!==null&&Bo(n)),e}function Bo(e){Ke===null?Ke=e:Ke.push.apply(Ke,e)}function ym(e){for(var n=e;;){if(n.flags&16384){var t=n.updateQueue;if(t!==null&&(t=t.stores,t!==null))for(var s=0;s<t.length;s++){var i=t[s],o=i.getSnapshot;i=i.value;try{if(!gn(o(),i))return!1}catch{return!1}}}if(t=n.child,n.subtreeFlags&16384&&t!==null)t.return=n,n=t;else{if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return!0;n=n.return}n.sibling.return=n.return,n=n.sibling}}return!0}function nt(e,n){for(n&=~Ao,n&=~Ts,e.suspendedLanes|=n,e.pingedLanes&=~n,e=e.expirationTimes;0<n;){var t=31-fn(n),s=1<<t;e[t]=-1,n&=~s}}function Hu(e){if((oe&6)!==0)throw Error(c(327));Gt();var n=Vr(e,0);if((n&1)===0)return Qe(e,Ne()),null;var t=Is(e,n);if(e.tag!==0&&t===2){var s=vi(e);s!==0&&(n=s,t=Oo(e,s))}if(t===1)throw t=Pr,vt(e,0),nt(e,n),Qe(e,Ne()),t;if(t===6)throw Error(c(345));return e.finishedWork=e.current.alternate,e.finishedLanes=n,yt(e,Ke,Fn),Qe(e,Ne()),null}function Uo(e,n){var t=oe;oe|=1;try{return e(n)}finally{oe=t,oe===0&&(Ht=Ne()+500,us&&Qn())}}function gt(e){Zn!==null&&Zn.tag===0&&(oe&6)===0&&Gt();var n=oe;oe|=1;var t=dn.transition,s=de;try{if(dn.transition=null,de=1,e)return e()}finally{de=s,dn.transition=t,oe=n,(oe&6)===0&&Qn()}}function Wo(){on=Vt.current,ve(Vt)}function vt(e,n){e.finishedWork=null,e.finishedLanes=0;var t=e.timeoutHandle;if(t!==-1&&(e.timeoutHandle=-1,Qd(t)),_e!==null)for(t=_e.return;t!==null;){var s=t;switch(qi(s),s.tag){case 1:s=s.type.childContextTypes,s!=null&&as();break;case 3:Ut(),ve(Ve),ve(ze),uo();break;case 5:ao(s);break;case 4:Ut();break;case 13:ve(ke);break;case 19:ve(ke);break;case 10:to(s.type._context);break;case 22:case 23:Wo()}t=t.return}if(Re=e,_e=e=tt(e.current,null),Ie=on=n,Te=0,Pr=null,Ao=Ts=ft=0,Ke=Tr=null,mt!==null){for(n=0;n<mt.length;n++)if(t=mt[n],s=t.interleaved,s!==null){t.interleaved=null;var i=s.next,o=t.pending;if(o!==null){var l=o.next;o.next=i,s.next=l}t.pending=s}mt=null}return e}function Gu(e,n){do{var t=_e;try{if(no(),xs.current=Ss,ks){for(var s=we.memoizedState;s!==null;){var i=s.queue;i!==null&&(i.pending=null),s=s.next}ks=!1}if(pt=0,Le=Pe=we=null,Sr=!1,Nr=0,Do.current=null,t===null||t.return===null){Te=1,Pr=n,_e=null;break}e:{var o=e,l=t.return,d=t,m=n;if(n=Ie,d.flags|=32768,m!==null&&typeof m=="object"&&typeof m.then=="function"){var k=m,b=d,P=b.tag;if((b.mode&1)===0&&(P===0||P===11||P===15)){var C=b.alternate;C?(b.updateQueue=C.updateQueue,b.memoizedState=C.memoizedState,b.lanes=C.lanes):(b.updateQueue=null,b.memoizedState=null)}var B=vu(l);if(B!==null){B.flags&=-257,yu(B,l,d,o,n),B.mode&1&&gu(o,k,n),n=B,m=k;var V=n.updateQueue;if(V===null){var H=new Set;H.add(m),n.updateQueue=H}else V.add(m);break e}else{if((n&1)===0){gu(o,k,n),$o();break e}m=Error(c(426))}}else if(xe&&d.mode&1){var Ce=vu(l);if(Ce!==null){(Ce.flags&65536)===0&&(Ce.flags|=256),yu(Ce,l,d,o,n),Zi(Wt(m,d));break e}}o=m=Wt(m,d),Te!==4&&(Te=2),Tr===null?Tr=[o]:Tr.push(o),o=l;do{switch(o.tag){case 3:o.flags|=65536,n&=-n,o.lanes|=n;var v=pu(o,m,n);Ul(o,v);break e;case 1:d=m;var h=o.type,x=o.stateNode;if((o.flags&128)===0&&(typeof h.getDerivedStateFromError=="function"||x!==null&&typeof x.componentDidCatch=="function"&&(Jn===null||!Jn.has(x)))){o.flags|=65536,n&=-n,o.lanes|=n;var L=fu(o,d,n);Ul(o,L);break e}}o=o.return}while(o!==null)}Xu(t)}catch(G){n=G,_e===t&&t!==null&&(_e=t=t.return);continue}break}while(!0)}function Ku(){var e=Ps.current;return Ps.current=Ss,e===null?Ss:e}function $o(){(Te===0||Te===3||Te===2)&&(Te=4),Re===null||(ft&268435455)===0&&(Ts&268435455)===0||nt(Re,Ie)}function Is(e,n){var t=oe;oe|=2;var s=Ku();(Re!==e||Ie!==n)&&(Fn=null,vt(e,n));do try{xm();break}catch(i){Gu(e,i)}while(!0);if(no(),oe=t,Ps.current=s,_e!==null)throw Error(c(261));return Re=null,Ie=0,Te}function xm(){for(;_e!==null;)Qu(_e)}function km(){for(;_e!==null&&!Hc();)Qu(_e)}function Qu(e){var n=Ju(e.alternate,e,on);e.memoizedProps=e.pendingProps,n===null?Xu(e):_e=n,Do.current=null}function Xu(e){var n=e;do{var t=n.alternate;if(e=n.return,(n.flags&32768)===0){if(t=mm(t,n,on),t!==null){_e=t;return}}else{if(t=hm(t,n),t!==null){t.flags&=32767,_e=t;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{Te=6,_e=null;return}}if(n=n.sibling,n!==null){_e=n;return}_e=n=e}while(n!==null);Te===0&&(Te=5)}function yt(e,n,t){var s=de,i=dn.transition;try{dn.transition=null,de=1,wm(e,n,t,s)}finally{dn.transition=i,de=s}return null}function wm(e,n,t,s){do Gt();while(Zn!==null);if((oe&6)!==0)throw Error(c(327));t=e.finishedWork;var i=e.finishedLanes;if(t===null)return null;if(e.finishedWork=null,e.finishedLanes=0,t===e.current)throw Error(c(177));e.callbackNode=null,e.callbackPriority=0;var o=t.lanes|t.childLanes;if(nd(e,o),e===Re&&(_e=Re=null,Ie=0),(t.subtreeFlags&2064)===0&&(t.flags&2064)===0||Ls||(Ls=!0,Zu(Br,function(){return Gt(),null})),o=(t.flags&15990)!==0,(t.subtreeFlags&15990)!==0||o){o=dn.transition,dn.transition=null;var l=de;de=1;var d=oe;oe|=4,Do.current=null,fm(e,t),Ou(t,e),Ud(Wi),Kr=!!Ui,Wi=Ui=null,e.current=t,gm(t),Gc(),oe=d,de=l,dn.transition=o}else e.current=t;if(Ls&&(Ls=!1,Zn=e,Rs=i),o=e.pendingLanes,o===0&&(Jn=null),Xc(t.stateNode),Qe(e,Ne()),n!==null)for(s=e.onRecoverableError,t=0;t<n.length;t++)i=n[t],s(i.value,{componentStack:i.stack,digest:i.digest});if(Ms)throw Ms=!1,e=zo,zo=null,e;return(Rs&1)!==0&&e.tag!==0&&Gt(),o=e.pendingLanes,(o&1)!==0?e===Fo?Mr++:(Mr=0,Fo=e):Mr=0,Qn(),null}function Gt(){if(Zn!==null){var e=za(Rs),n=dn.transition,t=de;try{if(dn.transition=null,de=16>e?16:e,Zn===null)var s=!1;else{if(e=Zn,Zn=null,Rs=0,(oe&6)!==0)throw Error(c(331));var i=oe;for(oe|=4,W=e.current;W!==null;){var o=W,l=o.child;if((W.flags&16)!==0){var d=o.deletions;if(d!==null){for(var m=0;m<d.length;m++){var k=d[m];for(W=k;W!==null;){var b=W;switch(b.tag){case 0:case 11:case 15:Er(8,b,o)}var P=b.child;if(P!==null)P.return=b,W=P;else for(;W!==null;){b=W;var C=b.sibling,B=b.return;if(Du(b),b===k){W=null;break}if(C!==null){C.return=B,W=C;break}W=B}}}var V=o.alternate;if(V!==null){var H=V.child;if(H!==null){V.child=null;do{var Ce=H.sibling;H.sibling=null,H=Ce}while(H!==null)}}W=o}}if((o.subtreeFlags&2064)!==0&&l!==null)l.return=o,W=l;else e:for(;W!==null;){if(o=W,(o.flags&2048)!==0)switch(o.tag){case 0:case 11:case 15:Er(9,o,o.return)}var v=o.sibling;if(v!==null){v.return=o.return,W=v;break e}W=o.return}}var h=e.current;for(W=h;W!==null;){l=W;var x=l.child;if((l.subtreeFlags&2064)!==0&&x!==null)x.return=l,W=x;else e:for(l=h;W!==null;){if(d=W,(d.flags&2048)!==0)try{switch(d.tag){case 0:case 11:case 15:Es(9,d)}}catch(G){Se(d,d.return,G)}if(d===l){W=null;break e}var L=d.sibling;if(L!==null){L.return=d.return,W=L;break e}W=d.return}}if(oe=i,Qn(),Cn&&typeof Cn.onPostCommitFiberRoot=="function")try{Cn.onPostCommitFiberRoot(Ur,e)}catch{}s=!0}return s}finally{de=t,dn.transition=n}}return!1}function qu(e,n,t){n=Wt(t,n),n=pu(e,n,1),e=qn(e,n,1),n=We(),e!==null&&(nr(e,1,n),Qe(e,n))}function Se(e,n,t){if(e.tag===3)qu(e,e,t);else for(;n!==null;){if(n.tag===3){qu(n,e,t);break}else if(n.tag===1){var s=n.stateNode;if(typeof n.type.getDerivedStateFromError=="function"||typeof s.componentDidCatch=="function"&&(Jn===null||!Jn.has(s))){e=Wt(t,e),e=fu(n,e,1),n=qn(n,e,1),e=We(),n!==null&&(nr(n,1,e),Qe(n,e));break}}n=n.return}}function jm(e,n,t){var s=e.pingCache;s!==null&&s.delete(n),n=We(),e.pingedLanes|=e.suspendedLanes&t,Re===e&&(Ie&t)===t&&(Te===4||Te===3&&(Ie&130023424)===Ie&&500>Ne()-Io?vt(e,0):Ao|=t),Qe(e,n)}function Yu(e,n){n===0&&((e.mode&1)===0?n=1:(n=$r,$r<<=1,($r&130023424)===0&&($r=4194304)));var t=We();e=An(e,n),e!==null&&(nr(e,n,t),Qe(e,t))}function Sm(e){var n=e.memoizedState,t=0;n!==null&&(t=n.retryLane),Yu(e,t)}function Nm(e,n){var t=0;switch(e.tag){case 13:var s=e.stateNode,i=e.memoizedState;i!==null&&(t=i.retryLane);break;case 19:s=e.stateNode;break;default:throw Error(c(314))}s!==null&&s.delete(n),Yu(e,t)}var Ju;Ju=function(e,n,t){if(e!==null)if(e.memoizedProps!==n.pendingProps||Ve.current)Ge=!0;else{if((e.lanes&t)===0&&(n.flags&128)===0)return Ge=!1,dm(e,n,t);Ge=(e.flags&131072)!==0}else Ge=!1,xe&&(n.flags&1048576)!==0&&Ml(n,ds,n.index);switch(n.lanes=0,n.tag){case 2:var s=n.type;_s(e,n),e=n.pendingProps;var i=Dt(n,ze.current);Bt(n,t),i=ho(null,n,s,e,i,t);var o=po();return n.flags|=1,typeof i=="object"&&i!==null&&typeof i.render=="function"&&i.$$typeof===void 0?(n.tag=1,n.memoizedState=null,n.updateQueue=null,He(s)?(o=!0,ls(n)):o=!1,n.memoizedState=i.state!==null&&i.state!==void 0?i.state:null,io(n),i.updater=Ns,n.stateNode=i,i._reactInternals=n,ko(n,s,e,t),n=No(null,n,s,!0,o,t)):(n.tag=0,xe&&o&&Xi(n),Ue(null,n,i,t),n=n.child),n;case 16:s=n.elementType;e:{switch(_s(e,n),e=n.pendingProps,i=s._init,s=i(s._payload),n.type=s,i=n.tag=_m(s),e=yn(s,e),i){case 0:n=So(null,n,s,e,t);break e;case 1:n=Nu(null,n,s,e,t);break e;case 11:n=xu(null,n,s,e,t);break e;case 14:n=ku(null,n,s,yn(s.type,e),t);break e}throw Error(c(306,s,""))}return n;case 0:return s=n.type,i=n.pendingProps,i=n.elementType===s?i:yn(s,i),So(e,n,s,i,t);case 1:return s=n.type,i=n.pendingProps,i=n.elementType===s?i:yn(s,i),Nu(e,n,s,i,t);case 3:e:{if(Cu(n),e===null)throw Error(c(387));s=n.pendingProps,o=n.memoizedState,i=o.element,Bl(e,n),vs(n,s,null,t);var l=n.memoizedState;if(s=l.element,o.isDehydrated)if(o={element:s,isDehydrated:!1,cache:l.cache,pendingSuspenseBoundaries:l.pendingSuspenseBoundaries,transitions:l.transitions},n.updateQueue.baseState=o,n.memoizedState=o,n.flags&256){i=Wt(Error(c(423)),n),n=_u(e,n,s,t,i);break e}else if(s!==i){i=Wt(Error(c(424)),n),n=_u(e,n,s,t,i);break e}else for(sn=Hn(n.stateNode.containerInfo.firstChild),rn=n,xe=!0,vn=null,t=Fl(n,null,s,t),n.child=t;t;)t.flags=t.flags&-3|4096,t=t.sibling;else{if(zt(),s===i){n=zn(e,n,t);break e}Ue(e,n,s,t)}n=n.child}return n;case 5:return $l(n),e===null&&Ji(n),s=n.type,i=n.pendingProps,o=e!==null?e.memoizedProps:null,l=i.children,$i(s,i)?l=null:o!==null&&$i(s,o)&&(n.flags|=32),Su(e,n),Ue(e,n,l,t),n.child;case 6:return e===null&&Ji(n),null;case 13:return bu(e,n,t);case 4:return oo(n,n.stateNode.containerInfo),s=n.pendingProps,e===null?n.child=Ft(n,null,s,t):Ue(e,n,s,t),n.child;case 11:return s=n.type,i=n.pendingProps,i=n.elementType===s?i:yn(s,i),xu(e,n,s,i,t);case 7:return Ue(e,n,n.pendingProps,t),n.child;case 8:return Ue(e,n,n.pendingProps.children,t),n.child;case 12:return Ue(e,n,n.pendingProps.children,t),n.child;case 10:e:{if(s=n.type._context,i=n.pendingProps,o=n.memoizedProps,l=i.value,pe(ps,s._currentValue),s._currentValue=l,o!==null)if(gn(o.value,l)){if(o.children===i.children&&!Ve.current){n=zn(e,n,t);break e}}else for(o=n.child,o!==null&&(o.return=n);o!==null;){var d=o.dependencies;if(d!==null){l=o.child;for(var m=d.firstContext;m!==null;){if(m.context===s){if(o.tag===1){m=In(-1,t&-t),m.tag=2;var k=o.updateQueue;if(k!==null){k=k.shared;var b=k.pending;b===null?m.next=m:(m.next=b.next,b.next=m),k.pending=m}}o.lanes|=t,m=o.alternate,m!==null&&(m.lanes|=t),ro(o.return,t,n),d.lanes|=t;break}m=m.next}}else if(o.tag===10)l=o.type===n.type?null:o.child;else if(o.tag===18){if(l=o.return,l===null)throw Error(c(341));l.lanes|=t,d=l.alternate,d!==null&&(d.lanes|=t),ro(l,t,n),l=o.sibling}else l=o.child;if(l!==null)l.return=o;else for(l=o;l!==null;){if(l===n){l=null;break}if(o=l.sibling,o!==null){o.return=l.return,l=o;break}l=l.return}o=l}Ue(e,n,i.children,t),n=n.child}return n;case 9:return i=n.type,s=n.pendingProps.children,Bt(n,t),i=un(i),s=s(i),n.flags|=1,Ue(e,n,s,t),n.child;case 14:return s=n.type,i=yn(s,n.pendingProps),i=yn(s.type,i),ku(e,n,s,i,t);case 15:return wu(e,n,n.type,n.pendingProps,t);case 17:return s=n.type,i=n.pendingProps,i=n.elementType===s?i:yn(s,i),_s(e,n),n.tag=1,He(s)?(e=!0,ls(n)):e=!1,Bt(n,t),mu(n,s,i),ko(n,s,i,t),No(null,n,s,!0,e,t);case 19:return Pu(e,n,t);case 22:return ju(e,n,t)}throw Error(c(156,n.tag))};function Zu(e,n){return La(e,n)}function Cm(e,n,t,s){this.tag=e,this.key=t,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=n,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=s,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function mn(e,n,t,s){return new Cm(e,n,t,s)}function Vo(e){return e=e.prototype,!(!e||!e.isReactComponent)}function _m(e){if(typeof e=="function")return Vo(e)?1:0;if(e!=null){if(e=e.$$typeof,e===Sn)return 11;if(e===Nn)return 14}return 2}function tt(e,n){var t=e.alternate;return t===null?(t=mn(e.tag,n,e.key,e.mode),t.elementType=e.elementType,t.type=e.type,t.stateNode=e.stateNode,t.alternate=e,e.alternate=t):(t.pendingProps=n,t.type=e.type,t.flags=0,t.subtreeFlags=0,t.deletions=null),t.flags=e.flags&14680064,t.childLanes=e.childLanes,t.lanes=e.lanes,t.child=e.child,t.memoizedProps=e.memoizedProps,t.memoizedState=e.memoizedState,t.updateQueue=e.updateQueue,n=e.dependencies,t.dependencies=n===null?null:{lanes:n.lanes,firstContext:n.firstContext},t.sibling=e.sibling,t.index=e.index,t.ref=e.ref,t}function zs(e,n,t,s,i,o){var l=2;if(s=e,typeof e=="function")Vo(e)&&(l=1);else if(typeof e=="string")l=5;else e:switch(e){case Z:return xt(t.children,i,o,n);case fe:l=8,i|=8;break;case Ee:return e=mn(12,t,n,i|2),e.elementType=Ee,e.lanes=o,e;case en:return e=mn(13,t,n,i),e.elementType=en,e.lanes=o,e;case pn:return e=mn(19,t,n,i),e.elementType=pn,e.lanes=o,e;case je:return Fs(t,i,o,n);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case hn:l=10;break e;case ot:l=9;break e;case Sn:l=11;break e;case Nn:l=14;break e;case $e:l=16,s=null;break e}throw Error(c(130,e==null?e:typeof e,""))}return n=mn(l,t,n,i),n.elementType=e,n.type=s,n.lanes=o,n}function xt(e,n,t,s){return e=mn(7,e,s,n),e.lanes=t,e}function Fs(e,n,t,s){return e=mn(22,e,s,n),e.elementType=je,e.lanes=t,e.stateNode={isHidden:!1},e}function Ho(e,n,t){return e=mn(6,e,null,n),e.lanes=t,e}function Go(e,n,t){return n=mn(4,e.children!==null?e.children:[],e.key,n),n.lanes=t,n.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},n}function bm(e,n,t,s,i){this.tag=n,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=yi(0),this.expirationTimes=yi(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=yi(0),this.identifierPrefix=s,this.onRecoverableError=i,this.mutableSourceEagerHydrationData=null}function Ko(e,n,t,s,i,o,l,d,m){return e=new bm(e,n,t,d,m),n===1?(n=1,o===!0&&(n|=8)):n=0,o=mn(3,null,null,n),e.current=o,o.stateNode=e,o.memoizedState={element:s,isDehydrated:t,cache:null,transitions:null,pendingSuspenseBoundaries:null},io(o),e}function Em(e,n,t){var s=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:M,key:s==null?null:""+s,children:e,containerInfo:n,implementation:t}}function ec(e){if(!e)return Kn;e=e._reactInternals;e:{if(at(e)!==e||e.tag!==1)throw Error(c(170));var n=e;do{switch(n.tag){case 3:n=n.stateNode.context;break e;case 1:if(He(n.type)){n=n.stateNode.__reactInternalMemoizedMergedChildContext;break e}}n=n.return}while(n!==null);throw Error(c(171))}if(e.tag===1){var t=e.type;if(He(t))return El(e,t,n)}return n}function nc(e,n,t,s,i,o,l,d,m){return e=Ko(t,s,!0,e,i,o,l,d,m),e.context=ec(null),t=e.current,s=We(),i=et(t),o=In(s,i),o.callback=n??null,qn(t,o,i),e.current.lanes=i,nr(e,i,s),Qe(e,s),e}function Os(e,n,t,s){var i=n.current,o=We(),l=et(i);return t=ec(t),n.context===null?n.context=t:n.pendingContext=t,n=In(o,l),n.payload={element:e},s=s===void 0?null:s,s!==null&&(n.callback=s),e=qn(i,n,l),e!==null&&(wn(e,i,l,o),gs(e,i,l)),l}function Bs(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function tc(e,n){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var t=e.retryLane;e.retryLane=t!==0&&t<n?t:n}}function Qo(e,n){tc(e,n),(e=e.alternate)&&tc(e,n)}function Pm(){return null}var rc=typeof reportError=="function"?reportError:function(e){console.error(e)};function Xo(e){this._internalRoot=e}Us.prototype.render=Xo.prototype.render=function(e){var n=this._internalRoot;if(n===null)throw Error(c(409));Os(e,n,null,null)},Us.prototype.unmount=Xo.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var n=e.containerInfo;gt(function(){Os(null,e,null,null)}),n[Mn]=null}};function Us(e){this._internalRoot=e}Us.prototype.unstable_scheduleHydration=function(e){if(e){var n=Ba();e={blockedOn:null,target:e,priority:n};for(var t=0;t<Wn.length&&n!==0&&n<Wn[t].priority;t++);Wn.splice(t,0,e),t===0&&$a(e)}};function qo(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function Ws(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function sc(){}function Tm(e,n,t,s,i){if(i){if(typeof s=="function"){var o=s;s=function(){var k=Bs(l);o.call(k)}}var l=nc(n,s,e,0,null,!1,!1,"",sc);return e._reactRootContainer=l,e[Mn]=l.current,fr(e.nodeType===8?e.parentNode:e),gt(),l}for(;i=e.lastChild;)e.removeChild(i);if(typeof s=="function"){var d=s;s=function(){var k=Bs(m);d.call(k)}}var m=Ko(e,0,!1,null,null,!1,!1,"",sc);return e._reactRootContainer=m,e[Mn]=m.current,fr(e.nodeType===8?e.parentNode:e),gt(function(){Os(n,m,t,s)}),m}function $s(e,n,t,s,i){var o=t._reactRootContainer;if(o){var l=o;if(typeof i=="function"){var d=i;i=function(){var m=Bs(l);d.call(m)}}Os(n,l,e,i)}else l=Tm(t,n,e,i,s);return Bs(l)}Fa=function(e){switch(e.tag){case 3:var n=e.stateNode;if(n.current.memoizedState.isDehydrated){var t=er(n.pendingLanes);t!==0&&(xi(n,t|1),Qe(n,Ne()),(oe&6)===0&&(Ht=Ne()+500,Qn()))}break;case 13:gt(function(){var s=An(e,1);if(s!==null){var i=We();wn(s,e,1,i)}}),Qo(e,1)}},ki=function(e){if(e.tag===13){var n=An(e,134217728);if(n!==null){var t=We();wn(n,e,134217728,t)}Qo(e,134217728)}},Oa=function(e){if(e.tag===13){var n=et(e),t=An(e,n);if(t!==null){var s=We();wn(t,e,n,s)}Qo(e,n)}},Ba=function(){return de},Ua=function(e,n){var t=de;try{return de=e,n()}finally{de=t}},mi=function(e,n,t){switch(n){case"input":if(si(e,t),n=t.name,t.type==="radio"&&n!=null){for(t=e;t.parentNode;)t=t.parentNode;for(t=t.querySelectorAll("input[name="+JSON.stringify(""+n)+'][type="radio"]'),n=0;n<t.length;n++){var s=t[n];if(s!==e&&s.form===e.form){var i=os(s);if(!i)throw Error(c(90));da(s),si(s,i)}}}break;case"textarea":ga(e,t);break;case"select":n=t.value,n!=null&&jt(e,!!t.multiple,n,!1)}},Ca=Uo,_a=gt;var Mm={usingClientEntryPoint:!1,Events:[yr,Lt,os,Sa,Na,Uo]},Lr={findFiberByHostInstance:lt,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},Lm={bundleType:Lr.bundleType,version:Lr.version,rendererPackageName:Lr.rendererPackageName,rendererConfig:Lr.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:se.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=Ta(e),e===null?null:e.stateNode},findFiberByHostInstance:Lr.findFiberByHostInstance||Pm,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Vs=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Vs.isDisabled&&Vs.supportsFiber)try{Ur=Vs.inject(Lm),Cn=Vs}catch{}}return Xe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Mm,Xe.createPortal=function(e,n){var t=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!qo(n))throw Error(c(200));return Em(e,n,null,t)},Xe.createRoot=function(e,n){if(!qo(e))throw Error(c(299));var t=!1,s="",i=rc;return n!=null&&(n.unstable_strictMode===!0&&(t=!0),n.identifierPrefix!==void 0&&(s=n.identifierPrefix),n.onRecoverableError!==void 0&&(i=n.onRecoverableError)),n=Ko(e,1,!1,null,null,t,!1,s,i),e[Mn]=n.current,fr(e.nodeType===8?e.parentNode:e),new Xo(n)},Xe.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var n=e._reactInternals;if(n===void 0)throw typeof e.render=="function"?Error(c(188)):(e=Object.keys(e).join(","),Error(c(268,e)));return e=Ta(n),e=e===null?null:e.stateNode,e},Xe.flushSync=function(e){return gt(e)},Xe.hydrate=function(e,n,t){if(!Ws(n))throw Error(c(200));return $s(null,e,n,!0,t)},Xe.hydrateRoot=function(e,n,t){if(!qo(e))throw Error(c(405));var s=t!=null&&t.hydratedSources||null,i=!1,o="",l=rc;if(t!=null&&(t.unstable_strictMode===!0&&(i=!0),t.identifierPrefix!==void 0&&(o=t.identifierPrefix),t.onRecoverableError!==void 0&&(l=t.onRecoverableError)),n=nc(n,null,e,1,t??null,i,!1,o,l),e[Mn]=n.current,fr(e),s)for(e=0;e<s.length;e++)t=s[e],i=t._getVersion,i=i(t._source),n.mutableSourceEagerHydrationData==null?n.mutableSourceEagerHydrationData=[t,i]:n.mutableSourceEagerHydrationData.push(t,i);return new Us(n)},Xe.render=function(e,n,t){if(!Ws(n))throw Error(c(200));return $s(null,e,n,!1,t)},Xe.unmountComponentAtNode=function(e){if(!Ws(e))throw Error(c(40));return e._reactRootContainer?(gt(function(){$s(null,null,e,!1,function(){e._reactRootContainer=null,e[Mn]=null})}),!0):!1},Xe.unstable_batchedUpdates=Uo,Xe.unstable_renderSubtreeIntoContainer=function(e,n,t,s){if(!Ws(t))throw Error(c(200));if(e==null||e._reactInternals===void 0)throw Error(c(38));return $s(e,n,t,!1,s)},Xe.version="18.3.1-next-f1338f8080-20240426",Xe}var hc;function Wm(){if(hc)return Zo.exports;hc=1;function a(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(a)}catch(u){console.error(u)}}return a(),Zo.exports=Um(),Zo.exports}var pc;function $m(){if(pc)return Hs;pc=1;var a=Wm();return Hs.createRoot=a.createRoot,Hs.hydrateRoot=a.hydrateRoot,Hs}var Vm=$m();class Hm extends Error{constructor(c,p){super(c);ic(this,"status");this.status=p}}async function Je(a,u){const c=await fetch(a,{...u,credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json",...u==null?void 0:u.headers}}),p=await c.json().catch(()=>({}));if(!c.ok)throw new Hm(p.error||c.statusText||"Request failed",c.status);return p}const Gm=()=>Je("/auth/status"),Km=()=>Je("/api/config"),Tc=()=>Je("/api/botstats"),Qm=()=>Je("/api/commands"),Xm=()=>Je("/api/guilds"),qm=()=>Je("/api/me/overview"),Ym=a=>Je(`/api/guild/${a}/overview`),Jm=a=>Je(`/api/guild/${a}/levels`),fc=a=>Je(`/api/guild/${a}/config`),gc=a=>Je(`/api/guild/${a}/resources`);function Js(a,u,c,p){return Je(`/api/guild/${a}/config/${u}`,{method:"POST",headers:p?{"X-CSRF-Token":p}:void 0,body:JSON.stringify(c)})}function Zm(a,u,c){return Je(`/api/guild/${a}/config/profile`,{method:"POST",headers:c?{"X-CSRF-Token":c}:void 0,body:JSON.stringify(u)})}function Mc(a){return a.replace(/\/+$/,"")||"/"}function vc(a=window.location.pathname){const u=Mc(a);return u==="/commands"?"commands":u==="/docs"?"docs":u.startsWith("/docs/")?"docs-detail":u==="/dashboard"||u.startsWith("/dashboard/")?"dashboard":u==="/privacy"?"privacy":u==="/terms"?"terms":u==="/donate"||u.startsWith("/donate")?"donate":u==="/transcript"||u.startsWith("/transcript/")?"transcript":"home"}function Dr(a,u="overview"){return a?`/dashboard/${a}/${u}`:"/dashboard"}function yc(){return"/dashboard/servers"}function xc(){const a=Mc(window.location.pathname).split("/").filter(Boolean),u=["overview","leveling","moderation","server","ai","customization"];return a[1]==="servers"?{view:"servers",guildId:null,section:"overview"}:a[1]?{view:"guild",guildId:a[1]||null,section:u.includes(a[2])?a[2]:"overview"}:{view:"overview",guildId:null,section:"overview"}}function me(a){a.startsWith("/")&&(window.history.pushState({},"",a),window.dispatchEvent(new PopStateEvent("popstate")),window.scrollTo({top:0,behavior:"smooth"}))}function qs({onNavigate:a}){return r.jsxs("a",{className:"brand",href:"/",onClick:u=>{u.preventDefault(),a?a():me("/")},children:[r.jsx("span",{className:"brand-mark",children:"n"}),r.jsx("span",{children:"niko"})]})}function Kt(){return r.jsxs("footer",{className:"site-footer",children:[r.jsx(qs,{}),r.jsx("span",{children:"Built for communities that care."}),r.jsxs("div",{children:[r.jsx("a",{href:"/privacy",onClick:a=>{a.preventDefault(),me("/privacy")},children:"Privacy"}),r.jsx("a",{href:"/terms",onClick:a=>{a.preventDefault(),me("/terms")},children:"Terms"}),r.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"GitHub"})]})]})}/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Lc=(...a)=>a.filter((u,c,p)=>!!u&&u.trim()!==""&&p.indexOf(u)===c).join(" ").trim();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const eh=a=>a.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase();/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const nh=a=>a.replace(/^([A-Z])|[\s-_]+(\w)/g,(u,c,p)=>p?p.toUpperCase():c.toLowerCase());/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kc=a=>{const u=nh(a);return u.charAt(0).toUpperCase()+u.slice(1)};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var ta={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const th=a=>{for(const u in a)if(u.startsWith("aria-")||u==="role"||u==="title")return!0;return!1},rh=R.createContext({}),sh=()=>R.useContext(rh),ih=R.forwardRef(({color:a,size:u,strokeWidth:c,absoluteStrokeWidth:p,className:f="",children:j,iconNode:w,...z},y)=>{const{size:F=24,strokeWidth:N=2,absoluteStrokeWidth:T=!1,color:D="currentColor",className:K=""}=sh()??{},I=p??T?Number(c??N)*24/Number(u??F):c??N;return R.createElement("svg",{ref:y,...ta,width:u??F??ta.width,height:u??F??ta.height,stroke:a??D,strokeWidth:I,className:Lc("lucide",K,f),...!j&&!th(z)&&{"aria-hidden":"true"},...z},[...w.map(([A,E])=>R.createElement(A,E)),...Array.isArray(j)?j:[j]])});/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ze=(a,u)=>{const c=R.forwardRef(({className:p,...f},j)=>R.createElement(ih,{ref:j,iconNode:u,className:Lc(`lucide-${eh(kc(a))}`,`lucide-${a}`,p),...f}));return c.displayName=kc(a),c};/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const oh=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]],ah=Ze("arrow-right",oh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const lh=[["path",{d:"M12 5v16",key:"1f6ucr"}],["path",{d:"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z",key:"1fyvmf"}]],wc=Ze("book-open",lh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const uh=[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],ra=Ze("chart-column",uh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ch=[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]],dh=Ze("external-link",ch);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const mh=[["rect",{width:"7",height:"7",x:"3",y:"3",rx:"1",key:"1g98yp"}],["rect",{width:"7",height:"7",x:"14",y:"3",rx:"1",key:"6d4xhi"}],["rect",{width:"7",height:"7",x:"14",y:"14",rx:"1",key:"nxv5o0"}],["rect",{width:"7",height:"7",x:"3",y:"14",rx:"1",key:"1bb6yr"}]],aa=Ze("layout-grid",mh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const hh=[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]],ph=Ze("lock-keyhole",hh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const fh=[["path",{d:"M4 5h16",key:"1tepv9"}],["path",{d:"M4 12h16",key:"1lakjw"}],["path",{d:"M4 19h16",key:"1djgab"}]],gh=Ze("menu",fh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const vh=[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]],yh=Ze("search",vh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const xh=[["path",{d:"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915",key:"1i5ecw"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]],Gs=Ze("settings",xh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kh=[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}]],sa=Ze("shield",kh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const wh=[["path",{d:"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",key:"1s2grr"}],["path",{d:"M20 2v4",key:"1rf3ol"}],["path",{d:"M22 4h-4",key:"gwowj6"}],["circle",{cx:"4",cy:"20",r:"2",key:"6kqj1y"}]],Ks=Ze("sparkles",wh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jh=[["path",{d:"M12 19h8",key:"baeox8"}],["path",{d:"m4 17 6-6-6-6",key:"1yngyt"}]],Sh=Ze("terminal",jh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Nh=[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["path",{d:"M16 3.128a4 4 0 0 1 0 7.744",key:"16gr8j"}],["path",{d:"M22 21v-2a4 4 0 0 0-3-3.87",key:"kshegd"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}]],jc=Ze("users",Nh);/**
 * @license lucide-react v1.39.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ch=[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]],_h=Ze("x",Ch),bh={arrow:ah,grid:aa,terminal:Sh,chart:ra,shield:sa,spark:Ks,users:jc,settings:Gs,book:wc,external:dh,menu:gh,close:_h,lock:ph,search:yh,doc:wc,utility:Gs,icon_home:aa,icon_settings:Gs,icon_economy:ra,icon_leveling:ra,icon_moderation:sa,icon_automod:sa,icon_heart:Ks,icon_utility:Gs,icon_bot:jc,icon_ai:Ks,icon_lightbulb:Ks};function Y({name:a,size:u,className:c=""}){const p=bh[a]||aa;return r.jsx(p,{className:`icon ${c}`.trim(),"aria-hidden":"true",focusable:"false",strokeWidth:1.8,style:u?{width:u,height:u}:void 0})}let Sc=null,ia=null;function Zs(){const[a,u]=R.useState(Sc);return R.useEffect(()=>{ia||(ia=Km().then(c=>Sc=c)),ia.then(u).catch(()=>{})},[]),a}function jn({page:a}){const u=Zs();return r.jsxs("header",{className:"site-header",children:[r.jsx(qs,{}),r.jsxs("nav",{className:"site-nav","aria-label":"Main navigation",children:[r.jsx("a",{className:a==="home"?"active":"","aria-current":a==="home"?"page":void 0,href:"/",onClick:c=>{c.preventDefault(),me("/")},children:"Home"}),r.jsx("a",{className:a==="commands"?"active":"","aria-current":a==="commands"?"page":void 0,href:"/commands",onClick:c=>{c.preventDefault(),me("/commands")},children:"Commands"}),r.jsx("a",{className:a==="docs"?"active":"","aria-current":a==="docs"?"page":void 0,href:"/docs",onClick:c=>{c.preventDefault(),me("/docs")},children:"Docs"})]}),r.jsxs("div",{className:"header-actions",children:[r.jsxs("a",{className:"button button-small button-muted dashboard-link",href:"/dashboard",onClick:c=>{c.preventDefault(),me("/dashboard")},children:["Dashboard ",r.jsx(Y,{name:"arrow"})]}),r.jsx("a",{className:"button button-small button-primary",href:(u==null?void 0:u.invite_url)||"#",target:"_blank",rel:"noreferrer",children:"Add to Discord"})]})]})}const Eh=[{value:"all",label:"All commands"},{value:"slash",label:"Slash"},{value:"prefix",label:"Prefix"},{value:"hybrid",label:"Hybrid"},{value:"context",label:"Context menus"}],Ys={slash:"Slash command",prefix:"Prefix command",hybrid:"Hybrid command",context:"Context menu"};function kt(a){return a.type&&a.type in Ys?a.type:"slash"}function Ph(a){return a.context_type==="user"?"Right-click a user":"Right-click a message"}function Rc(a){const u=kt(a);return u==="slash"?r.jsxs("code",{children:["/",a.name]}):u==="prefix"?r.jsxs("code",{children:[".",a.name]}):u==="hybrid"?r.jsxs(r.Fragment,{children:[r.jsxs("code",{children:["/",a.name]}),r.jsx("span",{className:"command-or",children:"or"}),r.jsxs("code",{children:[".",a.name]})]}):r.jsxs("code",{className:"context-invocation",children:[Ph(a)," · ",a.name]})}function Nc(a){return a!=null&&a.length?a:["Not specified"]}function Th({command:a,onClose:u}){R.useEffect(()=>{const w=z=>{z.key==="Escape"&&u()};return document.addEventListener("keydown",w),()=>document.removeEventListener("keydown",w)},[u]);const c=a.parameters||[],p=a.subcommands||[],f=Nc(a.aliases),j=Nc(a.permissions);return r.jsx("div",{className:"command-dialog-backdrop",role:"presentation",onMouseDown:w=>{w.currentTarget===w.target&&u()},children:r.jsxs("section",{className:"command-dialog",role:"dialog","aria-modal":"true","aria-labelledby":"command-dialog-title",children:[r.jsxs("header",{className:"command-dialog-header",children:[r.jsxs("div",{children:[r.jsxs("div",{className:"command-dialog-kicker",children:[a.category," · ",Ys[kt(a)]]}),r.jsx("h2",{id:"command-dialog-title",children:Rc(a)})]}),r.jsx("button",{className:"dialog-close",type:"button",onClick:u,"aria-label":"Close command details",title:"Close command details",children:r.jsx(Y,{name:"close"})})]}),r.jsxs("div",{className:"command-dialog-body",children:[r.jsx("p",{className:"command-dialog-description",children:a.description||"A Niko command for your server."}),r.jsxs("div",{className:"command-detail-grid",children:[r.jsxs("section",{className:"command-detail-section command-detail-wide",children:[r.jsx("h3",{children:"Usage"}),r.jsx("code",{className:"command-usage",children:a.usage||`${kt(a)==="context"?a.name:`/${a.name}`}`})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Permissions"}),r.jsx("ul",{className:"command-detail-list",children:j.map(w=>r.jsx("li",{children:w},w))})]}),r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Aliases"}),r.jsx("ul",{className:"command-detail-list",children:f.map(w=>r.jsx("li",{children:r.jsx("code",{children:w==="Not specified"?w:`.${w}`})},w))})]})]}),!!c.length&&r.jsxs("section",{className:"command-detail-section command-parameters",children:[r.jsx("h3",{children:"Parameters"}),r.jsx("div",{className:"command-parameter-list",children:c.map(w=>r.jsxs("div",{className:"command-parameter",children:[r.jsxs("div",{className:"command-parameter-title",children:[r.jsx("code",{children:w.name}),r.jsxs("span",{children:[w.required?"Required":"Optional"," · ",w.type]})]}),r.jsx("p",{children:w.description||"No description provided."})]},w.name))})]}),!!p.length&&r.jsxs("section",{className:"command-detail-section",children:[r.jsx("h3",{children:"Subcommands"}),r.jsx("div",{className:"subcommand-list",children:p.map(w=>r.jsxs("code",{children:[a.name," ",w]},w))})]})]}),r.jsxs("footer",{className:"command-dialog-footer",children:[r.jsx("span",{children:"Command registry details are generated from the live bot."}),r.jsx("button",{className:"button button-primary button-small",type:"button",onClick:u,children:"Done"})]})]})})}function Mh(){const[a,u]=R.useState([]),[c,p]=R.useState(null),[f,j]=R.useState(""),[w,z]=R.useState("all"),[y,F]=R.useState("all"),[N,T]=R.useState(!0),[D,K]=R.useState("");R.useEffect(()=>{Qm().then(u).catch(()=>K("The command registry is unavailable right now.")).finally(()=>T(!1))},[]),R.useEffect(()=>{if(!c)return;const E=document.body.style.overflow;return document.body.style.overflow="hidden",()=>{document.body.style.overflow=E}},[c]);const I=R.useMemo(()=>["all",...Array.from(new Set(a.map(E=>E.category))).sort()],[a]),A=a.filter(E=>{const U=`${E.name} ${E.description} ${E.category} ${Ys[kt(E)]} ${E.context_type||""} ${(E.aliases||[]).join(" ")}`.toLowerCase();return(y==="all"||kt(E)===y)&&(w==="all"||E.category===w)&&U.includes(f.trim().toLowerCase())});return r.jsxs(r.Fragment,{children:[r.jsx(jn,{page:"commands"}),r.jsxs("main",{className:"shell page-main",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Reference library"}),r.jsxs("h1",{children:["Everything Niko",r.jsx("br",{}),r.jsx("em",{children:"knows how to do."})]}),r.jsx("p",{children:"Browse slash, prefix, hybrid, and context commands from the live bot registry. Select any command for permissions, aliases, parameters, usage, and subcommands."})]}),r.jsxs("div",{className:"command-toolbar",children:[r.jsxs("label",{className:"search-field",children:[r.jsx("span",{"aria-hidden":"true",children:"⌕"}),r.jsx("input",{value:f,onChange:E=>j(E.target.value),placeholder:"Search commands","aria-label":"Search commands"})]}),r.jsxs("div",{className:"command-filters",children:[r.jsx("div",{className:"filter-list","aria-label":"Command types",children:Eh.map(E=>r.jsx("button",{type:"button",className:y===E.value?"filter active":"filter","aria-pressed":y===E.value,onClick:()=>F(E.value),children:E.label},E.value))}),r.jsx("div",{className:"filter-list","aria-label":"Command categories",children:I.map(E=>r.jsx("button",{type:"button",className:w===E?"filter active":"filter","aria-pressed":w===E,onClick:()=>z(E),children:E==="all"?"All categories":E},E))})]})]}),r.jsxs("div",{className:"command-meta",children:[r.jsx("strong",{children:N?"…":A.length})," commands ",r.jsx("span",{children:"·"})," live bot registry ",r.jsx("span",{children:"·"})," select a card for details"]}),D&&r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Could not load commands"}),r.jsx("span",{children:D})]}),r.jsxs("div",{className:"commands-grid",children:[A.map(E=>r.jsxs("button",{className:"command-card",type:"button",onClick:()=>p(E),"aria-label":`View details for ${E.name}`,children:[r.jsxs("span",{className:"command-card-head",children:[r.jsx("span",{className:"command-name",children:Rc(E)}),r.jsx("span",{className:"command-type",children:Ys[kt(E)]})]}),r.jsx("span",{className:"command-card-description",children:E.description||"A Niko command for your server."}),r.jsxs("span",{className:"command-card-footer",children:[r.jsx("span",{className:"category-tag",children:E.category}),r.jsxs("span",{className:"command-expand",children:[r.jsx("span",{children:"Details"}),r.jsx(Y,{name:"arrow",size:14})]})]})]},`${kt(E)}-${E.context_type||""}-${E.category}-${E.name}`)),!N&&!D&&!A.length&&r.jsx("div",{className:"empty-state",children:"No commands match that search."})]})]}),r.jsx(Kt,{}),c&&r.jsx(Th,{command:c,onClose:()=>p(null)})]})}function be(a){return a==null?"—":new Intl.NumberFormat("en-US",{notation:a>9999?"compact":"standard"}).format(a)}function la(a){return(a==null?void 0:a.global_name)||(a==null?void 0:a.username)||"there"}function Dc(a){return a.split(/\s+/).map(u=>u[0]).join("").slice(0,2).toUpperCase()}function ca({guild:a,className:u="guild-avatar"}){return r.jsx("span",{className:u,"aria-hidden":"true",children:a.icon_url?r.jsx("img",{src:a.icon_url,alt:""}):a.name.slice(0,1).toUpperCase()})}function Ac({user:a,className:u="avatar"}){const c=a.avatar?`https://cdn.discordapp.com/avatars/${a.id}/${a.avatar}.${a.avatar.startsWith("a_")?"gif":"png"}?size=64`:null;return r.jsx("span",{className:u,"aria-hidden":"true",children:c?r.jsx("img",{src:c,alt:""}):Dc(a.global_name||a.username||"Niko")})}function Lh({name:a,avatarUrl:u,className:c="member-avatar"}){return r.jsx("span",{className:c,"aria-hidden":"true",children:u?r.jsx("img",{src:u,alt:""}):Dc(a)})}const Cc=[["overview","Overview","grid","At a glance"],["leveling","Leveling","spark","Reward participation"],["moderation","Moderation","shield","Keep things steady"],["server","Server","settings","Manage server features"],["ai","AI controls","settings","Shape Niko’s voice"],["customization","Customization","paint","Niko’s server identity"]];function Rh({user:a,guilds:u,selectedGuild:c,view:p,section:f,stats:j,onHome:w,onServers:z,onGuildChange:y,onSectionChange:F,children:N}){var E;const T=u.filter(U=>U.installed!==!1),D=(U=!1)=>r.jsx("nav",{className:U?"dash-nav dash-nav-mobile":"dash-nav","aria-label":"Server settings",children:Cc.map(([S,re,se])=>r.jsxs("button",{className:p==="guild"&&f===S?"active":"","aria-current":p==="guild"&&f===S?"page":void 0,onClick:()=>F(S),children:[r.jsx(Y,{name:se}),r.jsx("span",{children:re})]},S))}),K=(U=!1)=>r.jsxs("nav",{className:U?"dash-nav dash-primary-nav dash-nav-mobile":"dash-nav dash-primary-nav","aria-label":"Dashboard",children:[r.jsxs("button",{className:p==="overview"?"active":"","aria-current":p==="overview"?"page":void 0,onClick:w,children:[r.jsx(Y,{name:"grid"}),r.jsx("span",{children:"My overview"})]}),r.jsxs("button",{className:p==="servers"?"active":"","aria-current":p==="servers"?"page":void 0,onClick:z,children:[r.jsx(Y,{name:"users"}),r.jsx("span",{children:"My servers"})]})]}),I=p==="overview"?`Welcome, ${la(a)}`:p==="servers"?"Your servers":(c==null?void 0:c.name)||"Server settings",A=p==="guild"?"Managing server":"Niko dashboard";return r.jsxs("div",{className:"dashboard-layout",children:[r.jsxs("aside",{className:"dash-sidebar",children:[r.jsx(qs,{onNavigate:w}),r.jsxs("div",{className:"side-rail-heading",children:[r.jsx("span",{className:"side-label",children:"Workspace"}),r.jsxs("span",{className:"rail-status",children:[r.jsx("span",{className:"status-dot"})," Live"]})]}),K(),p==="guild"&&c&&r.jsxs(r.Fragment,{children:[r.jsx("div",{className:"side-label side-label-settings",children:"Current server"}),r.jsxs("div",{className:"side-guild",children:[r.jsx(ca,{guild:c}),r.jsxs("span",{children:[r.jsx("strong",{children:c.name}),r.jsx("small",{children:"Live configuration"})]}),r.jsx("span",{className:"guild-presence",title:"Niko is connected",children:r.jsx("span",{className:"status-dot"})})]}),r.jsxs("div",{className:"side-settings-caption",children:[r.jsx("span",{children:"Settings map"}),r.jsx("small",{children:"Pick a room to tune"})]}),D()]}),p!=="guild"&&r.jsxs("div",{className:"side-rail-note",children:[r.jsx("span",{className:"panel-kicker",children:"Niko workspace"}),r.jsxs("strong",{children:["Make the useful",r.jsx("br",{}),"things easier to find."]}),r.jsx("small",{children:"Your servers and their live signals, in one quiet place."})]}),r.jsxs("div",{className:"sidebar-bottom",children:[r.jsxs("span",{className:"online-label",children:[r.jsx("span",{className:"status-dot"})," Niko is online"]}),r.jsxs("small",{children:[be(j==null?void 0:j.guild_count)," connected servers · v",(j==null?void 0:j.version)||"1.0"]}),r.jsxs("a",{href:"/",onClick:U=>{U.preventDefault(),me("/")},children:["Back to public site ",r.jsx(Y,{name:"arrow"})]})]})]}),r.jsxs("div",{className:"dash-content",children:[r.jsxs("header",{className:"dash-topbar",children:[r.jsxs("div",{className:"mobile-top-row",children:[r.jsx("span",{className:"mobile-brand",children:r.jsx(qs,{})}),r.jsxs("span",{className:"mobile-status",children:[r.jsx("span",{className:"status-dot"})," Online"]})]}),r.jsxs("div",{className:"dash-title",children:[r.jsxs("span",{className:"dash-overline",children:[A," ",r.jsx("span",{className:"dash-title-divider",children:"/"})," ",p==="guild"?(E=Cc.find(([U])=>U===f))==null?void 0:E[1]:"Workspace"]}),r.jsx("h1",{children:I})]}),r.jsxs("div",{className:"dash-top-actions",children:[p==="guild"?r.jsxs("label",{className:"guild-switcher",children:[r.jsx("span",{className:"sr-only",children:"Switch server"}),r.jsxs("select",{value:(c==null?void 0:c.id)||"",onChange:U=>{const S=T.find(re=>re.id===U.target.value);S&&y(S)},children:[r.jsx("option",{value:"",disabled:!0,children:"Switch server"}),T.map(U=>r.jsx("option",{value:U.id,children:U.name},U.id))]})]}):r.jsxs("button",{className:"button button-muted button-small top-action",onClick:z,children:[r.jsx(Y,{name:"users"})," Browse servers"]}),p==="guild"&&r.jsxs("span",{className:"connection-chip",children:[r.jsx("span",{className:"status-dot"})," Connected"]}),r.jsxs("div",{className:"user-pill",children:[r.jsx(Ac,{user:a}),r.jsx("span",{children:la(a)})]}),r.jsx("a",{className:"logout-link",href:"/auth/logout",children:"Log out"})]})]}),r.jsx("div",{className:"mobile-primary-bar",children:K(!0)}),p==="guild"&&r.jsx("div",{className:"mobile-section-bar",children:D(!0)}),r.jsx("main",{className:"dash-main",children:N})]})]})}function it({eyebrow:a,title:u,text:c}){return r.jsxs("div",{className:"dash-heading",children:[r.jsxs("div",{className:"heading-meta",children:[r.jsx("div",{className:"eyebrow",children:a}),r.jsx("span",{className:"heading-context",children:"NIKO / CONTROL ROOM"})]}),r.jsx("h2",{children:u}),r.jsx("p",{children:c})]})}function Tn({label:a,value:u,note:c,accent:p=""}){return r.jsxs("div",{className:`dash-stat ${p}`,children:[r.jsx("span",{children:a}),r.jsx("strong",{children:u}),r.jsx("small",{children:c})]})}function Dh({user:a,overview:u,guilds:c,onServers:p,onManage:f}){const j=c.filter(w=>w.installed!==!1);return r.jsxs(r.Fragment,{children:[r.jsx(it,{eyebrow:"Personal overview",title:"Your Niko snapshot.",text:"Keep an eye on your progress, then jump into a server when you’re ready to tune the room."}),r.jsxs("div",{className:"overview-intro",children:[r.jsxs("div",{className:"profile-card",children:[r.jsx(Ac,{user:a,className:"profile-avatar"}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Signed in as"}),r.jsx("h3",{children:la(a)}),r.jsx("p",{children:"Personal economy profile"})]})]}),r.jsxs("button",{className:"button button-primary",onClick:p,children:["Manage a server ",r.jsx(Y,{name:"arrow"})]})]}),r.jsxs("div",{className:"dash-stats overview-stats",children:[r.jsx(Tn,{label:"Net worth",value:be(u==null?void 0:u.net_worth),note:"Across your Niko profile",accent:"accent-orange"}),r.jsx(Tn,{label:"In your wallet",value:be(u==null?void 0:u.balance),note:"Ready to spend",accent:"accent-violet"}),r.jsx(Tn,{label:"In your vault",value:be(u==null?void 0:u.bank),note:"Saved for later",accent:"accent-blue"}),r.jsx(Tn,{label:"Current level",value:be(u==null?void 0:u.level),note:u!=null&&u.job?`Working as a ${u.job}`:"Keep showing up",accent:"accent-green"})]}),r.jsxs("div",{className:"dash-columns overview-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Progress"}),r.jsx("h3",{children:"Your momentum"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(Y,{name:"spark"})})]}),r.jsxs("div",{className:"metric-list",children:[r.jsxs("div",{children:[r.jsx("span",{children:"Daily streak"}),r.jsxs("strong",{children:[be(u==null?void 0:u.daily_streak)," ",r.jsx("small",{children:"days"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Achievements"}),r.jsxs("strong",{children:[be(u==null?void 0:u.achievements)," ",r.jsx("small",{children:"unlocked"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Total earned"}),r.jsxs("strong",{children:[be(u==null?void 0:u.total_earned)," ",r.jsx("small",{children:"coins"})]})]}),r.jsxs("div",{children:[r.jsx("span",{children:"Economy standing"}),r.jsxs("strong",{children:[u!=null&&u.economy_rank?`#${be(u.economy_rank)}`:"—"," ",r.jsx("small",{children:u!=null&&u.economy_profiles?`of ${be(u.economy_profiles)}`:""})]})]})]})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Quick access"}),r.jsx("h3",{children:"Your servers"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(Y,{name:"users"})})]}),r.jsxs("div",{className:"mini-server-list",children:[j.slice(0,4).map(w=>r.jsxs("button",{onClick:()=>f(w),children:[r.jsx(ca,{guild:w}),r.jsx("span",{children:w.name}),r.jsx(Y,{name:"arrow"})]},w.id)),!j.length&&r.jsx("p",{className:"empty-state compact",children:"Add Niko to a server to start managing it."})]}),r.jsxs("button",{className:"text-link overview-link",onClick:p,children:["View all servers ",r.jsx(Y,{name:"arrow"})]})]})]})]})}function _c({guild:a,onManage:u}){const c=a.installed!==!1;return r.jsxs("article",{className:"server-card",children:[r.jsxs("div",{className:"server-card-heading",children:[r.jsx(ca,{guild:a,className:"server-avatar"}),r.jsx("span",{className:"server-status",children:c?"Niko is installed":"Ready to add"})]}),r.jsx("h3",{children:a.name}),r.jsx("p",{children:c?"Open the dashboard to manage Niko’s features and settings.":"You have permission to manage this server. Add Niko to unlock its controls."}),c?r.jsxs("button",{className:"button button-muted button-small",onClick:()=>u(a),children:["Open settings ",r.jsx(Y,{name:"arrow"})]}):r.jsxs("a",{className:"button button-primary button-small",href:a.invite_url||"#",target:"_blank",rel:"noreferrer",children:["Add Niko ",r.jsx(Y,{name:"external"})]})]})}function Ah({guilds:a,onManage:u}){const c=a.filter(f=>f.installed!==!1),p=a.filter(f=>f.installed===!1);return r.jsxs(r.Fragment,{children:[r.jsx(it,{eyebrow:"Servers",title:"Choose where to work.",text:"Manage servers with Niko already installed, or add Niko to another server you can administer."}),r.jsxs("div",{className:"server-summary",children:[r.jsxs("div",{children:[r.jsx("strong",{children:be(c.length)}),r.jsx("span",{children:"Connected to Niko"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:be(p.length)}),r.jsx("span",{children:"Ready to add"})]}),r.jsxs("div",{className:"server-summary-note",children:[r.jsx(Y,{name:"shield"}),r.jsx("span",{children:"Only servers where you have Manage Server access are shown."})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Connected"}),r.jsx("h3",{children:"Manage a server"})]}),r.jsx("span",{className:"section-count",children:c.length})]}),r.jsxs("div",{className:"server-grid",children:[c.map(f=>r.jsx(_c,{guild:f,onManage:u},f.id)),!c.length&&r.jsxs("div",{className:"empty-state",children:[r.jsx("strong",{children:"No connected servers yet."}),r.jsx("span",{children:"Add Niko below, then come back here to manage it."})]})]})]}),r.jsxs("section",{className:"server-section",children:[r.jsxs("div",{className:"section-heading-row",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Available to you"}),r.jsx("h3",{children:"Add Niko to a server"})]}),r.jsx("span",{className:"section-count",children:p.length})]}),r.jsxs("div",{className:"server-grid",children:[p.map(f=>r.jsx(_c,{guild:f,onManage:u},f.id)),!p.length&&r.jsx("div",{className:"server-note",children:"Niko is already installed in every server you can manage."})]})]})]})}function Ic({rows:a}){return r.jsxs("div",{className:"rank-list",children:[a.slice(0,5).map((u,c)=>r.jsxs("div",{className:"rank-row",children:[r.jsx("span",{className:`rank rank-${c+1}`,children:String(c+1).padStart(2,"0")}),r.jsxs("span",{className:"rank-user",children:[r.jsx(Lh,{name:u.display_name||u.username||"Unknown member",avatarUrl:u.avatar_url}),r.jsxs("span",{children:[r.jsx("strong",{children:u.display_name||u.username||"Unknown member"}),u.username&&u.display_name&&r.jsxs("small",{children:["@",u.username]})]})]}),r.jsxs("strong",{children:[be(u.xp),r.jsx("small",{children:" xp"})]})]},`${u.user_id}-${c}`)),!a.length&&r.jsx("div",{className:"empty-state compact",children:"No data recorded yet."})]})}function Ih({overview:a}){return r.jsxs(r.Fragment,{children:[r.jsxs("div",{className:"guild-welcome",children:[r.jsxs("div",{children:[r.jsx("span",{className:"welcome-mark",children:r.jsx(Y,{name:"grid"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server pulse"}),r.jsx("strong",{children:"Here’s what needs your attention."})]})]}),r.jsxs("span",{className:"welcome-time",children:["LIVE SIGNALS ",r.jsx("span",{className:"status-dot"})]})]}),r.jsx(it,{eyebrow:"Overview",title:"A quick read on your room.",text:"The important signals, without making you hunt for them."}),r.jsxs("div",{className:"dash-stats guild-overview-stats",children:[r.jsx(Tn,{label:"Warnings logged",value:be(a.moderation.warn_count),note:"For this server",accent:"accent-blue"}),r.jsx(Tn,{label:"Automod",value:a.moderation.automod_active?"Active":"Quiet",note:"Protection status",accent:"accent-green"}),r.jsx(Tn,{label:"Level leaders",value:be(a.leveling.top.length),note:"Members with recorded XP",accent:"accent-violet"})]}),r.jsxs("div",{className:"dash-columns",children:[r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Community energy"}),r.jsx("h3",{children:"Top XP"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(Y,{name:"spark"})})]}),r.jsx(Ic,{rows:a.leveling.top})]}),r.jsx("section",{className:"dash-panel",children:r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server controls"}),r.jsx("h3",{children:"Manage the room"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(Y,{name:"settings"})}),r.jsx("p",{children:"Use Server settings for prefixes, welcome messages, logs, and ticket panels."})]})})]})]})}function zh({rows:a,config:u,resources:c,csrfToken:p,guildId:f}){var j,w,z;return r.jsxs(r.Fragment,{children:[r.jsx(it,{eyebrow:"Leveling",title:"Momentum people can see.",text:"Track the members turning up, and tune the pace to fit your server."}),r.jsxs("div",{className:"dash-stats",children:[r.jsx(Tn,{label:"Top level",value:String(((j=a[0])==null?void 0:j.level)||0),note:((w=a[0])==null?void 0:w.display_name)||((z=a[0])==null?void 0:z.username)||"No members yet",accent:"accent-violet"}),r.jsx(Tn,{label:"XP multiplier",value:`${(u==null?void 0:u.leveling.xp_multiplier)||1}×`,note:(u==null?void 0:u.leveling.xp_enabled)===!1?"XP disabled":"Currently active",accent:"accent-blue"}),r.jsx(Tn,{label:"Cooldown",value:`${(u==null?void 0:u.leveling.xp_cooldown)||0}s`,note:"Between XP awards",accent:"accent-green"})]}),r.jsxs("section",{className:"dash-panel",children:[r.jsxs("div",{className:"panel-heading",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Leaderboard"}),r.jsx("h3",{children:"XP leaders"})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(Y,{name:"spark"})})]}),r.jsx(Ic,{rows:a})]}),r.jsx(Uh,{guildId:f,config:u,resources:c,csrfToken:p})]})}const ei={saving:!1,message:"",error:""};function Ye({label:a,hint:u,children:c}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:a}),c,u&&r.jsx("small",{children:u})]})}function Fh(a,u){const c=u?String(u):"",p=(a==null?void 0:a.channels)||[];return!c||p.some(f=>f.id===c)?p:[{id:c,name:`Unavailable channel (${c})`},...p]}function ni({icon:a,label:u,title:c,text:p}){return r.jsxs("div",{className:"settings-intro",children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(Y,{name:a})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:u}),r.jsx("strong",{children:c}),r.jsx("p",{children:p})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]})}function wt({label:a,title:u,detail:c,icon:p}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:a}),r.jsx("h3",{children:u}),c&&r.jsx("p",{children:c})]}),p&&r.jsx("span",{className:"panel-icon",children:r.jsx(Y,{name:p})})]})}function ti({state:a}){return r.jsxs("div",{className:"setting-footer",children:[a.error?r.jsx("span",{className:"form-error",role:"alert",children:a.error}):r.jsx("span",{role:"status",children:a.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:a.saving,children:a.saving?"Saving…":"Save changes"})]})}function Oh({guildId:a,config:u,csrfToken:c}){var T,D,K;const[p,f]=R.useState({}),[j,w]=R.useState(ei);R.useEffect(()=>{const I=(u==null?void 0:u.moderation)||{};f({automod:{...I.automod||{}},spam_threshold:I.spam_threshold??6,spam_interval:I.spam_interval??7,max_mentions:I.max_mentions??5,antinuke:{...I.antinuke||{}},antiraid:{...I.antiraid||{}},antiraid_ext:{...I.antiraid_ext||{}}})},[u]);const z=(I,A,E)=>f(U=>({...U,[I]:{...U[I],[A]:E}})),y=I=>{I.preventDefault(),w({saving:!0,message:"",error:""}),Js(a,"automod",p,c).then(A=>{const E=A.config||{};f({automod:{...E.automod||{}},spam_threshold:E.spam_threshold??6,spam_interval:E.spam_interval??7,max_mentions:E.max_mentions??5,antinuke:{...E.antinuke||{}},antiraid:{...E.antiraid||{}},antiraid_ext:{...E.antiraid_ext||{}}}),w({saving:!1,message:"Moderation settings saved to Niko.",error:""})}).catch(A=>w({saving:!1,message:"",error:A instanceof Error?A.message:"Could not save settings."}))},F=[["antispam","Anti-spam","Detect repeated messages"],["antilink","Invite links","Remove Discord invite links"],["badwords","Blocked words","Filter words from the server list"],["massmention","Mass mentions","Limit mention floods"],["antinuke","Anti-nuke","Protect channels and roles"],["antiraid","Join raid protection","React to sudden join waves"],["antiraid_ext","External app protection","Detect user-installed app abuse"]],N=F.filter(([I])=>{var A;return!!((A=p.automod)!=null&&A[I])}).length;return r.jsxs(r.Fragment,{children:[r.jsx(it,{eyebrow:"Moderation",title:"Keep the room feeling good.",text:"Small, deliberate controls for the moments that need a little backup. Every change is saved to the bot's live configuration."}),r.jsx(ni,{icon:"shield",label:"Protection desk",title:`${N} of ${F.length} safeguards active`,text:"Start with the essentials, then tune thresholds below when you know the room’s rhythm."}),r.jsxs("form",{onSubmit:y,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wt,{label:"Protection rules",title:"AutoMod modules",detail:"Toggle only the responses you want Niko to handle.",icon:"shield"}),r.jsx("div",{className:"setting-list",children:F.map(([I,A,E])=>{var U;return r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:A}),r.jsx("small",{children:E})]}),r.jsx("input",{type:"checkbox",checked:!!((U=p.automod)!=null&&U[I]),onChange:S=>z("automod",I,S.target.checked)}),r.jsx("i",{"aria-hidden":"true"})]},I)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wt,{label:"Thresholds",title:"Choose when protection steps in",detail:"These limits apply across the server."}),r.jsxs("div",{className:"form-grid",children:[r.jsx(Ye,{label:"Spam messages",hint:"Messages inside the spam interval",children:r.jsx("input",{type:"number",min:"1",max:"100",value:p.spam_threshold??6,onChange:I=>f({...p,spam_threshold:I.target.value})})}),r.jsx(Ye,{label:"Spam interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:p.spam_interval??7,onChange:I=>f({...p,spam_interval:I.target.value})})}),r.jsx(Ye,{label:"Maximum mentions",children:r.jsx("input",{type:"number",min:"1",max:"100",value:p.max_mentions??5,onChange:I=>f({...p,max_mentions:I.target.value})})}),r.jsx(Ye,{label:"Anti-raid joins",hint:"Joins inside the join interval",children:r.jsx("input",{type:"number",min:"1",max:"1000",value:((T=p.antiraid)==null?void 0:T.join_threshold)??10,onChange:I=>z("antiraid","join_threshold",I.target.value)})}),r.jsx(Ye,{label:"Anti-raid interval (seconds)",children:r.jsx("input",{type:"number",min:"1",max:"3600",value:((D=p.antiraid)==null?void 0:D.join_interval)??10,onChange:I=>z("antiraid","join_interval",I.target.value)})}),r.jsx(Ye,{label:"Anti-raid action",children:r.jsxs("select",{value:((K=p.antiraid)==null?void 0:K.action)??"kick",onChange:I=>z("antiraid","action",I.target.value),children:[r.jsx("option",{value:"kick",children:"Kick"}),r.jsx("option",{value:"ban",children:"Ban"}),r.jsx("option",{value:"softban",children:"Soft-ban"}),r.jsx("option",{value:"slowmode",children:"Slowmode"}),r.jsx("option",{value:"lockdown",children:"Lockdown"})]})})]}),r.jsx(ti,{state:j})]})]})]})}function Bh({guildId:a,config:u,csrfToken:c}){const[p,f]=R.useState({personality:"cafe",enabled:!0,ai_actions_experiment:!1,better_context_experiment:!1}),[j,w]=R.useState(ei);R.useEffect(()=>{const y=(u==null?void 0:u.ai)||{};f({personality:y.personality||"cafe",enabled:y.enabled!=="False"&&y.enabled!==!1,ai_actions_experiment:y.ai_actions_experiment===!0||y.ai_actions_experiment==="True",better_context_experiment:y.better_context_experiment===!0||y.better_context_experiment==="True"})},[u]);const z=y=>{y.preventDefault(),w({saving:!0,message:"",error:""}),Js(a,"ai",p,c).then(F=>{const N=F.config||{};f({personality:N.personality==="normal"?"normal":"cafe",enabled:N.enabled!=="False"&&N.enabled!==!1,ai_actions_experiment:N.ai_actions_experiment===!0||N.ai_actions_experiment==="True",better_context_experiment:N.better_context_experiment===!0||N.better_context_experiment==="True"}),w({saving:!1,message:"AI settings saved to Niko.",error:""})}).catch(F=>w({saving:!1,message:"",error:F instanceof Error?F.message:"Could not save settings."}))};return r.jsxs(r.Fragment,{children:[r.jsx(it,{eyebrow:"AI controls",title:"Give Niko the right tone.",text:"AI is optional, configurable per server, and designed to stay out of the way when the room does not need it."}),r.jsx(ni,{icon:"settings",label:"Conversation desk",title:p.enabled?"Niko is ready to respond":"Niko is staying quiet",text:"Choose a voice that fits your community. You can change this without affecting other servers."}),r.jsxs("form",{onSubmit:z,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wt,{label:"Conversation",title:"Core settings",detail:"Decide when Niko joins the conversation.",icon:"settings"}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable AI chat"}),r.jsx("small",{children:"Respond when Niko is mentioned"})]}),r.jsx("input",{type:"checkbox",checked:p.enabled,onChange:y=>f({...p,enabled:y.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"personality-options",children:[r.jsxs("button",{type:"button",className:p.personality==="cafe"?"personality active":"personality",onClick:()=>f({...p,personality:"cafe"}),children:[r.jsx("span",{className:"personality-mark",children:"n"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Café"}),r.jsx("small",{children:"Warm, playful, familiar"})]})]}),r.jsxs("button",{type:"button",className:p.personality==="normal"?"personality active":"personality",onClick:()=>f({...p,personality:"normal"}),children:[r.jsx("span",{className:"personality-mark",children:"—"}),r.jsxs("span",{children:[r.jsx("strong",{children:"Normal"}),r.jsx("small",{children:"Clear and straightforward"})]})]})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wt,{label:"Experiments",title:"Optional context",detail:"Try new capabilities when your team is ready."}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Better context"}),r.jsx("small",{children:"Use the last five channel messages"})]}),r.jsx("input",{type:"checkbox",checked:p.better_context_experiment,onChange:y=>f({...p,better_context_experiment:y.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"AI actions"}),r.jsx("small",{children:"Allow confirmed actions requested in chat"})]}),r.jsx("input",{type:"checkbox",checked:p.ai_actions_experiment,onChange:y=>f({...p,ai_actions_experiment:y.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsx(ti,{state:j})]})]})]})}function Uh({guildId:a,config:u,resources:c,csrfToken:p}){const f=(u==null?void 0:u.leveling)||{},[j,w]=R.useState({xp_enabled:!0,xp_multiplier:1,xp_cooldown:0,level_up_channel:"",level_up_message:""}),[z,y]=R.useState(ei);R.useEffect(()=>w({xp_enabled:f.xp_enabled!==!1,xp_multiplier:f.xp_multiplier??1,xp_cooldown:f.xp_cooldown??0,level_up_channel:f.level_up_channel?String(f.level_up_channel):"",level_up_message:f.level_up_message||""}),[u]);const F=T=>{T.preventDefault(),y({saving:!0,message:"",error:""}),Js(a,"leveling",j,p).then(D=>{const K=D.config||{};w({xp_enabled:K.xp_enabled!==!1,xp_multiplier:K.xp_multiplier??1,xp_cooldown:K.xp_cooldown??0,level_up_channel:K.level_up_channel?String(K.level_up_channel):"",level_up_message:K.level_up_message||""}),y({saving:!1,message:"Leveling settings saved to Niko.",error:""})}).catch(D=>y({saving:!1,message:"",error:D instanceof Error?D.message:"Could not save settings."}))},N=Fh(c,j.level_up_channel);return r.jsxs(r.Fragment,{children:[r.jsx(ni,{icon:"spark",label:"Participation desk",title:j.xp_enabled?"XP is flowing":"XP is paused",text:"Set a pace that rewards regulars without turning every message into a transaction."}),r.jsx("form",{onSubmit:F,className:"settings-stack",children:r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wt,{label:"Leveling settings",title:"Shape the pace",detail:"These controls apply to every member in this server.",icon:"spark"}),r.jsxs("label",{className:"setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enable XP"}),r.jsx("small",{children:"Track activity and award levels"})]}),r.jsx("input",{type:"checkbox",checked:j.xp_enabled,onChange:T=>w({...j,xp_enabled:T.target.checked})}),r.jsx("i",{"aria-hidden":"true"})]}),r.jsxs("div",{className:"form-grid",children:[r.jsx(Ye,{label:"XP multiplier",hint:"From 0.1× to 10×",children:r.jsx("input",{type:"number",min:"0.1",max:"10",step:"0.1",value:j.xp_multiplier,onChange:T=>w({...j,xp_multiplier:T.target.value})})}),r.jsx(Ye,{label:"Cooldown (seconds)",hint:"0 disables the cooldown",children:r.jsx("input",{type:"number",min:"0",max:"86400",value:j.xp_cooldown,onChange:T=>w({...j,xp_cooldown:T.target.value})})}),r.jsx(Ye,{label:"Level-up channel",children:r.jsxs("select",{value:j.level_up_channel,onChange:T=>w({...j,level_up_channel:T.target.value}),children:[r.jsx("option",{value:"",children:"Same channel"}),N.map(T=>r.jsxs("option",{value:T.id,children:["#",T.name]},T.id))]})}),r.jsx(Ye,{label:"Level-up message",hint:"Use {mention}, {level}, {name}, or {guild}",children:r.jsx("textarea",{rows:3,maxLength:1e3,value:j.level_up_message,onChange:T=>w({...j,level_up_message:T.target.value}),placeholder:"Leave blank for Niko's default message"})})]}),r.jsx(ti,{state:z})]})})]})}function Wh({guildId:a,config:u,csrfToken:c}){var F;const p=((F=u==null?void 0:u.server)==null?void 0:F.profile)||{},[f,j]=R.useState({display_name:p.display_name||"",bio:p.bio||"",avatar_url:p.avatar_url||"",banner_url:p.banner_url||""}),[w,z]=R.useState(ei);R.useEffect(()=>{var T;const N=((T=u==null?void 0:u.server)==null?void 0:T.profile)||{};j({display_name:N.display_name||"",bio:N.bio||"",avatar_url:N.avatar_url||"",banner_url:N.banner_url||""})},[u]);const y=N=>{N.preventDefault(),z({saving:!0,message:"",error:""}),Zm(a,{display_name:f.display_name||null,bio:f.bio||null,avatar_url:f.avatar_url||null,banner_url:f.banner_url||null},c).then(T=>{const D=T.profile||{};j({display_name:D.display_name||"",bio:D.bio||"",avatar_url:D.avatar_url||"",banner_url:D.banner_url||""}),z({saving:!1,message:"Bot profile updated.",error:""})}).catch(T=>z({saving:!1,message:"",error:T instanceof Error?T.message:"Could not save profile."}))};return r.jsxs(r.Fragment,{children:[r.jsx(it,{eyebrow:"Customization",title:"Niko's server presence.",text:"Change how Niko appears in this server. Display name, avatar, banner, and bio are all per-server."}),r.jsx(ni,{icon:"paint",label:"Identity desk",title:"Server-specific identity",text:"Each server can have its own Niko persona. Changes apply only to this server."}),r.jsxs("form",{onSubmit:y,className:"settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wt,{label:"Display name",title:"How Niko appears",detail:"Set the name members see for Niko in this server. Leave blank to use the default.",icon:"settings"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(Ye,{label:"Display name",hint:"32 characters or fewer",children:r.jsx("input",{value:f.display_name,maxLength:32,onChange:N=>j({...f,display_name:N.target.value}),placeholder:"Niko"})}),r.jsx(Ye,{label:"Bio",hint:"190 characters or fewer",children:r.jsx("input",{value:f.bio,maxLength:190,onChange:N=>j({...f,bio:N.target.value}),placeholder:"A warm Discord companion"})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(wt,{label:"Server avatar & banner",title:"Visual identity",detail:"Provide HTTPS image URLs. Images are uploaded to Discord when saved.",icon:"paint"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(Ye,{label:"Avatar URL",hint:"Square image, 512×512 recommended",children:r.jsx("input",{type:"url",value:f.avatar_url,onChange:N=>j({...f,avatar_url:N.target.value}),placeholder:"https://cdn.example.com/avatar.png"})}),r.jsx(Ye,{label:"Banner URL",hint:"Wide image, 960×540 recommended",children:r.jsx("input",{type:"url",value:f.banner_url,onChange:N=>j({...f,banner_url:N.target.value}),placeholder:"https://cdn.example.com/banner.png"})})]}),r.jsx("p",{className:"form-hint",children:"Images are fetched, validated, and uploaded to Discord. Maximum 8 MB each. Supported formats: PNG, JPG, GIF."})]}),r.jsx(ti,{state:w})]})]})}const $h={saving:!1,message:"",error:""};function qe({label:a,hint:u,children:c}){return r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:a}),c,u&&r.jsx("small",{children:u})]})}function Qs({label:a,title:u,detail:c,icon:p}){return r.jsxs("div",{className:"panel-heading settings-section-title",children:[r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:a}),r.jsx("h3",{children:u}),r.jsx("p",{children:c})]}),r.jsx("span",{className:"panel-icon",children:r.jsx(Y,{name:p})})]})}function Vh({state:a}){return r.jsxs("div",{className:"setting-footer",children:[a.error?r.jsx("span",{className:"form-error",role:"alert",children:a.error}):r.jsx("span",{role:"status",children:a.message||"Changes apply to this server."}),r.jsx("button",{className:"button button-primary",type:"submit",disabled:a.saving,children:a.saving?"Saving...":"Save server settings"})]})}const Hh=[["moderation","Moderation"],["automod","AutoMod"],["messages","Messages"],["channels","Channels"],["members","Members"],["captcha","Captcha"],["invites","Invites"],["roles","Roles"],["server","Server"],["voice","Voice"]];function Gh(a,u){var c;return u?((c=a==null?void 0:a.channels.find(p=>p.id===String(u)))==null?void 0:c.name)||`Channel ${u}`:"Not set"}function Xs(a,u){const c=u?String(u):"",p=(a==null?void 0:a.channels)||[];return!c||p.some(f=>f.id===c)?p:[{id:c,name:`Unavailable channel (${c})`},...p]}function bc(a,u=[]){const c=(a==null?void 0:a.roles)||[],p=new Set(c.map(j=>j.id));return[...u.map(String).filter((j,w,z)=>j&&!p.has(j)&&z.indexOf(j)===w).map(j=>({id:j,name:`Unavailable role (${j})`})),...c]}function Ec(a){var p,f;const u=(a==null?void 0:a.onboarding)||{},c=(a==null?void 0:a.tickets)||{};return{prefixes:((p=a==null?void 0:a.prefixes)!=null&&p.length?a.prefixes:["."]).join(`
`),welcome_channel:u.welcome_channel?String(u.welcome_channel):"",welcome_title:u.welcome_title||"",welcome_description:u.welcome_description||"",welcome_color:u.welcome_color===null||u.welcome_color===void 0?"5865F2":u.welcome_color.toString(16).padStart(6,"0"),welcome_image:u.welcome_image||"",rules_channel:u.rules_channel?String(u.rules_channel):"",rules_text:u.rules_text||"",rules_role_id:u.rules_role_id?String(u.rules_role_id):"",logging:Object.fromEntries(Object.entries((a==null?void 0:a.logging)||{}).map(([j,w])=>[j,w==null?"":String(w)])),disabled_logging:[...((f=a==null?void 0:a.logging)==null?void 0:f.disabled)||[]].map(String),panel_title:c.panel_title||"",panel_description:c.panel_description||"",panel_categories:(c.panel_categories||[]).join(`
`),panel_channel_id:c.panel_channel_id?String(c.panel_channel_id):"",support_roles:[...c.support_roles||[]].map(String)}}function Kh({guildId:a,config:u,resources:c,csrfToken:p}){const[f,j]=R.useState(()=>Ec(u==null?void 0:u.server)),[w,z]=R.useState($h),y=(S,re)=>j(se=>({...se,[S]:re})),F=(S,re)=>j(se=>({...se,logging:{...se.logging,[S]:re}})),N=S=>j(re=>({...re,disabled_logging:re.disabled_logging.includes(S)?re.disabled_logging.filter(se=>se!==S):[...re.disabled_logging,S]})),T=S=>{S.preventDefault(),z({saving:!0,message:"",error:""});const re=f.prefixes.split(/\r?\n|,/).map(ie=>ie.trim()).filter(Boolean),se=f.panel_categories.split(/\r?\n|,/).map(ie=>ie.trim()).filter(Boolean);Js(a,"server",{prefixes:re,onboarding:{welcome_channel:f.welcome_channel,welcome_title:f.welcome_title,welcome_description:f.welcome_description,welcome_color:f.welcome_color,welcome_image:f.welcome_image,rules_channel:f.rules_channel,rules_text:f.rules_text,rules_role_id:f.rules_role_id},logging:{...f.logging,disabled:f.disabled_logging},tickets:{panel_title:f.panel_title,panel_description:f.panel_description,panel_categories:se,panel_channel_id:f.panel_channel_id,support_roles:f.support_roles}},p).then(ie=>{j(Ec(ie.config)),z({saving:!1,message:"Server settings saved to Niko.",error:""})}).catch(ie=>z({saving:!1,message:"",error:ie instanceof Error?ie.message:"Could not save server settings."}))},D=f.welcome_channel,K=f.panel_channel_id,I=Xs(c,f.welcome_channel),A=Xs(c,f.rules_channel),E=Xs(c,f.panel_channel_id),U=bc(c,f.support_roles);return r.jsxs(r.Fragment,{children:[r.jsx(it,{eyebrow:"Server settings",title:"Make Niko fit your room.",text:"Manage the settings that shape how Niko behaves in this server. Economy balances remain global to each user and are not configured here."}),r.jsxs("div",{className:"settings-intro",children:[r.jsx("span",{className:"settings-intro-icon",children:r.jsx(Y,{name:"settings"})}),r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Server control room"}),r.jsxs("strong",{children:[f.prefixes.split(/\r?\n|,/).filter(Boolean).length||0," command prefixes configured"]}),r.jsx("p",{children:"Welcome flows, log destinations, and ticket panels all live here."})]}),r.jsxs("span",{className:"settings-intro-state",children:[r.jsx("span",{className:"status-dot"})," Per server"]})]}),r.jsxs("form",{onSubmit:T,className:"settings-stack server-settings-stack",children:[r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Qs,{label:"Commands",title:"Prefixes",detail:"Use one prefix per line. Niko will respond to all of them.",icon:"terminal"}),r.jsx(qe,{label:"Command prefixes",hint:"The default prefix is .",children:r.jsx("textarea",{rows:3,maxLength:200,value:f.prefixes,onChange:S=>y("prefixes",S.target.value),placeholder:".\\n!"})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Qs,{label:"Welcome flow",title:"Welcome and rules",detail:"Choose where new members see your welcome message and rules.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(qe,{label:"Welcome channel",children:r.jsxs("select",{value:D,onChange:S=>y("welcome_channel",S.target.value),children:[r.jsx("option",{value:"",children:"Disabled"}),I.map(S=>r.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),r.jsx(qe,{label:"Welcome title",children:r.jsx("input",{value:f.welcome_title,maxLength:200,onChange:S=>y("welcome_title",S.target.value),placeholder:"Welcome to the server"})}),r.jsx(qe,{label:"Welcome message",hint:"Supports {user} and {name}",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:f.welcome_description,onChange:S=>y("welcome_description",S.target.value),placeholder:"Welcome {user}!"})}),r.jsx(qe,{label:"Accent color",hint:"Hex color, for example 5865F2",children:r.jsx("input",{value:f.welcome_color,maxLength:7,onChange:S=>y("welcome_color",S.target.value),placeholder:"5865F2"})}),r.jsx(qe,{label:"Welcome image URL",children:r.jsx("input",{type:"url",value:f.welcome_image,onChange:S=>y("welcome_image",S.target.value),placeholder:"https://..."})}),r.jsx(qe,{label:"Rules channel",children:r.jsxs("select",{value:f.rules_channel,onChange:S=>y("rules_channel",S.target.value),children:[r.jsx("option",{value:"",children:"Not configured"}),A.map(S=>r.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),r.jsx(qe,{label:"Rules text",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:f.rules_text,onChange:S=>y("rules_text",S.target.value),placeholder:"Write the rules members should acknowledge."})}),r.jsx(qe,{label:"Role after rules acknowledgment",children:r.jsxs("select",{value:f.rules_role_id,onChange:S=>y("rules_role_id",S.target.value),children:[r.jsx("option",{value:"",children:"No role"}),bc(c,f.rules_role_id?[f.rules_role_id]:[]).map(S=>r.jsxs("option",{value:S.id,children:["@",S.name]},S.id))]})})]})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Qs,{label:"Audit trail",title:"Logging destinations",detail:"Pick a channel for each event type and disable categories you do not need.",icon:"book"}),r.jsx("div",{className:"server-logging-list",children:Hh.map(([S,re])=>{const se=Xs(c,f.logging[S]);return r.jsxs("div",{className:"server-logging-row",children:[r.jsxs("label",{className:"form-field",children:[r.jsxs("span",{className:"form-label",children:[re," logs"]}),r.jsxs("select",{value:String(f.logging[S]||""),onChange:ie=>F(S,ie.target.value),children:[r.jsx("option",{value:"",children:"Not set"}),se.map(ie=>r.jsxs("option",{value:ie.id,children:["#",ie.name]},ie.id))]})]}),r.jsxs("label",{className:"setting-row compact-setting-row",children:[r.jsxs("span",{children:[r.jsx("strong",{children:"Enabled"}),r.jsx("small",{children:Gh(c,f.logging[S])})]}),r.jsx("input",{type:"checkbox",checked:!f.disabled_logging.includes(S),onChange:()=>N(S)}),r.jsx("i",{"aria-hidden":"true"})]})]},S)})})]}),r.jsxs("section",{className:"dash-panel settings-panel",children:[r.jsx(Qs,{label:"Support desk",title:"Ticket panel",detail:"Configure the public panel and decide who can handle tickets.",icon:"users"}),r.jsxs("div",{className:"form-grid",children:[r.jsx(qe,{label:"Panel title",children:r.jsx("input",{value:f.panel_title,maxLength:200,onChange:S=>y("panel_title",S.target.value),placeholder:"Open a Ticket"})}),r.jsx(qe,{label:"Panel channel",children:r.jsxs("select",{value:K,onChange:S=>y("panel_channel_id",S.target.value),children:[r.jsx("option",{value:"",children:"Keep current panel channel"}),E.map(S=>r.jsxs("option",{value:S.id,children:["#",S.name]},S.id))]})}),r.jsx(qe,{label:"Panel description",children:r.jsx("textarea",{rows:4,maxLength:2e3,value:f.panel_description,onChange:S=>y("panel_description",S.target.value),placeholder:"Tell members what the ticket panel is for."})}),r.jsx(qe,{label:"Ticket categories",hint:"One category per line",children:r.jsx("textarea",{rows:4,value:f.panel_categories,onChange:S=>y("panel_categories",S.target.value),placeholder:"General\\nSupport\\nReports"})}),r.jsx(qe,{label:"Support roles",hint:"Hold Ctrl/Cmd to select more than one",children:r.jsx("select",{multiple:!0,value:f.support_roles,onChange:S=>y("support_roles",Array.from(S.target.selectedOptions,re=>re.value)),children:U.map(S=>r.jsxs("option",{value:S.id,children:["@",S.name]},S.id))})})]}),r.jsx("p",{className:"form-hint",children:"Saving panel settings updates the existing posted panel when Niko can find its saved message."})]}),r.jsx(Vh,{state:w})]})]})}function Qh({auth:a}){const u=Zs();return r.jsxs(r.Fragment,{children:[r.jsx(jn,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"n"}),r.jsx("div",{className:"eyebrow",children:"Private workspace"}),r.jsxs("h1",{children:["Settle in, ",r.jsx("em",{children:"admin."})]}),r.jsx("p",{children:"Sign in with Discord to see your Niko profile and manage the servers you look after."}),a.oauth_available?r.jsxs("a",{className:"button button-primary full-width",href:"/auth/login?next=/dashboard",children:[r.jsx(Y,{name:"lock"})," Continue with Discord ",r.jsx(Y,{name:"arrow"})]}):r.jsxs("div",{className:"notice warning",children:["Discord login is not configured yet. Add ",r.jsx("code",{children:"DISCORD_CLIENT_SECRET"})," to the environment and restart the bot."]}),!u&&r.jsx("p",{className:"form-hint",children:"The public bot configuration is still loading."}),r.jsx("a",{className:"back-link",href:"/",onClick:c=>{c.preventDefault(),me("/")},children:"Return to public site"})]})})]})}function Xh({section:a,guild:u,stats:c,csrfToken:p}){const[f,j]=R.useState(null),[w,z]=R.useState([]),[y,F]=R.useState(null),[N,T]=R.useState(null),[D,K]=R.useState(!0),[I,A]=R.useState("");return R.useEffect(()=>{K(!0),A(""),(a==="overview"?Ym(u.id).then(j):a==="leveling"?Promise.all([Jm(u.id),fc(u.id),gc(u.id)]).then(([U,S,re])=>{z(U),F(S),T(re)}):Promise.all([fc(u.id),gc(u.id)]).then(([U,S])=>{F(U),T(S)})).catch(U=>A(U instanceof Error?U.message:"This server could not be loaded.")).finally(()=>K(!1))},[u.id,a]),D?r.jsxs("div",{className:"section-loading section-skeleton",role:"status","aria-label":`Loading ${a}`,children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsxs("span",{children:["Loading ",a,"..."]})]}):I?r.jsxs("div",{className:"inline-error",role:"alert",children:[r.jsx("strong",{children:"Couldn’t load this page."}),r.jsx("span",{children:I}),r.jsx("button",{className:"button button-muted",onClick:()=>window.location.reload(),children:"Try again"})]}):a==="overview"&&f?r.jsx(Ih,{overview:f}):a==="leveling"?r.jsx(zh,{guildId:u.id,rows:w,config:y,resources:N,csrfToken:p}):a==="moderation"?r.jsx(Oh,{guildId:u.id,config:y,csrfToken:p}):a==="server"?r.jsx(Kh,{guildId:u.id,config:y,resources:N,csrfToken:p}):a==="customization"?r.jsx(Wh,{guildId:u.id,config:y,csrfToken:p}):r.jsx(Bh,{guildId:u.id,config:y,csrfToken:p})}function qh(){return r.jsxs("div",{className:"section-loading section-skeleton dashboard-loading",role:"status",children:[r.jsx("div",{className:"skeleton-title"}),r.jsx("div",{className:"skeleton-copy"}),r.jsxs("div",{className:"skeleton-grid",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"Preparing your dashboard..."})]})}function Yh(){Zs();const[a,u]=R.useState(xc),[c,p]=R.useState(null),[f,j]=R.useState(null),[w,z]=R.useState(null),[y,F]=R.useState([]),[N,T]=R.useState(null),[D,K]=R.useState(!0),[I,A]=R.useState("");if(R.useEffect(()=>{const M=()=>u(xc());return window.addEventListener("popstate",M),()=>window.removeEventListener("popstate",M)},[]),R.useEffect(()=>{K(!0),Promise.all([Gm(),Tc()]).then(([M,Z])=>(p(M),j(Z),M.authenticated?Promise.all([qm(),Xm()]).then(([fe,Ee])=>{z(fe),F(Ee)}):null)).catch(M=>A(M instanceof Error?M.message:"Dashboard unavailable")).finally(()=>K(!1))},[]),R.useEffect(()=>{if(a.view!=="guild"){T(null);return}const M=y.find(Z=>Z.id===a.guildId&&Z.installed!==!1);M?(T(M),localStorage.setItem("niko-guild",M.id)):a.guildId&&y.length&&me(yc())},[y,a.guildId,a.view]),D||!c)return r.jsxs("div",{className:"dashboard-state",children:[r.jsx("div",{className:"loading-ring"}),r.jsx("p",{children:"Connecting to Niko…"})]});if(I)return r.jsxs(r.Fragment,{children:[r.jsx(jn,{page:"dashboard"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Connection issue"}),r.jsxs("h1",{children:["Couldn’t load",r.jsx("br",{}),r.jsx("em",{children:"your workspace."})]}),r.jsx("p",{children:I}),r.jsxs("button",{className:"button button-primary",onClick:()=>window.location.reload(),children:["Try again ",r.jsx(Y,{name:"arrow"})]})]})})]});if(!c.authenticated)return r.jsx(Qh,{auth:c});const E=M=>{M.installed!==!1&&(localStorage.setItem("niko-guild",M.id),me(Dr(M.id,a.section)))},U=M=>{M.installed!==!1&&(localStorage.setItem("niko-guild",M.id),me(Dr(M.id,"overview")))},S=M=>{me(N?Dr(N.id,M):Dr())},re=()=>me(Dr()),se=()=>me(yc());let ie;return a.view==="servers"?ie=r.jsx(Ah,{guilds:y,onManage:U}):a.view==="guild"?ie=N?r.jsx(Xh,{section:a.section,guild:N,stats:f,csrfToken:c.csrf_token},`${N.id}-${a.section}`):r.jsx(qh,{}):ie=r.jsx(Dh,{user:c.user,overview:w,guilds:y,onServers:se,onManage:U}),r.jsx(Rh,{user:c.user,guilds:y,selectedGuild:N,view:a.view,section:a.section,stats:f,onHome:re,onServers:se,onGuildChange:E,onSectionChange:S,children:ie})}function Jh({value:a,onChange:u,placeholder:c="Search documentation...",onFocus:p,onBlur:f}){const[j,w]=R.useState(!1),z=R.useRef(null),[y,F]=R.useState(!1);R.useEffect(()=>{const I=A=>{var E;(A.metaKey||A.ctrlKey)&&A.key==="k"&&(A.preventDefault(),(E=z.current)==null||E.focus())};return document.addEventListener("keydown",I),()=>document.removeEventListener("keydown",I)},[]);const N=()=>{w(!0),F(!0),p==null||p()},T=()=>{w(!1),setTimeout(()=>F(!1),200),f==null||f()},D=I=>{u(I.target.value)},K=I=>{var A;I.key==="Escape"&&((A=z.current)==null||A.blur())};return r.jsxs("div",{className:`doc-search-bar ${y?"expanded":""}`,children:[r.jsxs("div",{className:"search-input-wrapper",children:[r.jsx(Y,{name:"search",className:"search-icon"}),r.jsx("input",{ref:z,type:"text",value:a,onChange:D,onFocus:N,onBlur:T,onKeyDown:K,placeholder:c,className:"search-input","aria-label":"Search documentation"}),r.jsxs("kbd",{className:"search-shortcut",children:[r.jsx("span",{className:"shortcut-key",children:"⌘"}),"K"]})]}),r.jsxs("div",{className:"search-hint",children:["Press ",r.jsx("kbd",{children:"⌘K"})," to focus search"]})]})}function Zh({selectedCategory:a,onSelectCategory:u,sections:c,allCategoriesLabel:p="All Categories"}){return r.jsx("div",{className:"doc-filters",children:r.jsxs("div",{className:"filter-tabs",role:"tablist","aria-label":"Filter by category",children:[r.jsx("button",{role:"tab","aria-selected":a==="",className:`filter-tab ${a===""?"active":""}`,onClick:()=>u(""),children:p}),c.map(f=>r.jsxs("button",{role:"tab","aria-selected":a===f.id,className:`filter-tab ${a===f.id?"active":""}`,onClick:()=>u(f.id),children:[r.jsx(Y,{name:f.icon,size:14}),r.jsx("span",{children:f.label})]},f.id))]})})}function oa({doc:a,variant:u="default"}){const c="page"in a?a.page:a,[p,f]=R.useState(!1),j=y=>{y.preventDefault(),me(`/docs/${c.slug}`)},w=y=>{(y.key==="Enter"||y.key===" ")&&(y.preventDefault(),me(`/docs/${c.slug}`))};if(u==="compact")return r.jsx("a",{href:`/docs/${c.slug}`,onClick:j,onKeyDown:w,className:"doc-card-compact",tabIndex:0,role:"button",children:r.jsxs("div",{className:"compact-content",children:[r.jsx("span",{className:"compact-title",children:c.title}),r.jsx("span",{className:"compact-excerpt",children:c.excerpt})]})});const z="highlights"in a?a.highlights:[];return r.jsx("article",{className:`doc-card ${u==="highlighted"?"highlighted":""}`,children:r.jsxs("div",{className:`doc-card-content ${p?"loaded":""}`,children:[r.jsxs("div",{className:"doc-card-header",children:[r.jsx("span",{className:"doc-category",children:c.category.replace(/-/g," ")}),r.jsxs("span",{className:"doc-order",children:["#",c.order]})]}),r.jsx("h3",{className:"doc-title",children:c.title}),r.jsx("p",{className:"doc-excerpt",children:c.excerpt}),z.length>0&&r.jsx("div",{className:"doc-highlights",children:z.slice(0,2).map((y,F)=>r.jsxs("p",{className:"highlight-snippet",children:[y.slice(0,150),y.length>150?"...":""]},F))}),r.jsxs("div",{className:"doc-card-footer",children:[r.jsx("div",{className:"doc-tags",children:c.tags.slice(0,3).map(y=>r.jsxs("span",{className:"doc-tag",children:["#",y]},y))}),r.jsxs("a",{href:`/docs/${c.slug}`,onClick:j,onKeyDown:w,className:"doc-read-more",children:["Read more ",r.jsx(Y,{name:"arrow",size:14})]})]})]})})}const Me=[{slug:"welcome",title:"Welcome to Niko",category:"getting-started",excerpt:"New to Niko? Start here to understand what the bot can do for your server.",tags:["introduction","overview","beginner"],order:1,content:`
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
    `}];function ep(a){return Me.find(u=>u.slug===a)}const st=[{id:"getting-started",label:"Getting Started",description:"New to Niko? Start here.",icon:"icon_home",count:Me.filter(a=>a.category==="getting-started").length},{id:"setup",label:"Setup",description:"Configure Niko for your server.",icon:"icon_settings",count:Me.filter(a=>a.category==="setup").length},{id:"economy",label:"Economy",description:"Money, jobs, banking, and more.",icon:"icon_economy",count:Me.filter(a=>a.category==="economy").length},{id:"leveling",label:"Leveling",description:"XP, levels, and rankings.",icon:"icon_leveling",count:Me.filter(a=>a.category==="leveling").length},{id:"moderation",label:"Moderation",description:"Moderation tools and commands.",icon:"icon_moderation",count:Me.filter(a=>a.category==="moderation").length},{id:"automod",label:"AutoMod",description:"Automated moderation features.",icon:"icon_automod",count:Me.filter(a=>a.category==="automod").length},{id:"social",label:"Social",description:"Community engagement features.",icon:"icon_heart",count:Me.filter(a=>a.category==="social").length},{id:"utility",label:"Utility",description:"Helpful tools and utilities.",icon:"icon_utility",count:Me.filter(a=>a.category==="utility").length},{id:"voice",label:"Voice",description:"Voice and music features.",icon:"icon_bot",count:Me.filter(a=>a.category==="voice").length},{id:"ai",label:"AI",description:"AI-powered features.",icon:"icon_ai",count:Me.filter(a=>a.category==="ai").length},{id:"dashboard",label:"Dashboard",description:"Web dashboard guides.",icon:"icon_settings",count:Me.filter(a=>a.category==="dashboard").length},{id:"tips",label:"Tips",description:"Tips and best practices.",icon:"icon_lightbulb",count:Me.filter(a=>a.category==="tips").length}];function zc(){const[a,u]=R.useState({query:"",category:"",tags:[]}),c=R.useCallback(y=>{u(F=>({...F,query:y.toLowerCase(),tags:[]}))},[]),p=R.useCallback(y=>{u(F=>({...F,category:y,tags:[]}))},[]),f=R.useCallback(y=>{u(F=>{const N=F.tags.includes(y)?F.tags.filter(T=>T!==y):[...F.tags,y];return{...F,tags:N,query:""}})},[]),j=R.useCallback(()=>{u({query:"",category:"",tags:[]})},[]),w=R.useMemo(()=>{const{query:y,category:F,tags:N}=a;if(!y&&!F&&N.length===0)return Me.map(D=>({page:D,score:1,highlights:[]}));const T=[];for(const D of Me)if(!(F&&D.category!==F)&&!(N.length>0&&!N.some(K=>D.tags.includes(K))))if(y){const K=np(D,y);if(K===0)continue;const I=tp(D,y);T.push({page:D,score:K,highlights:I})}else T.push({page:D,score:1,highlights:[]});return T.sort((D,K)=>K.score!==D.score?K.score-D.score:D.page.order-K.page.order),T},[a]),z=a.query!==""||a.category!==""||a.tags.length>0;return{filters:a,setQuery:c,setCategory:p,toggleTag:f,clearFilters:j,results:w,hasActiveFilters:z,resultCount:w.length}}function np(a,u){let c=0;const p=u.toLowerCase();a.title.toLowerCase()===p?c+=100:a.title.toLowerCase().includes(p)&&(c+=50),a.excerpt.toLowerCase().includes(p)&&(c+=25),a.content.toLowerCase().includes(p)&&(c+=10);for(const f of a.tags)f.toLowerCase().includes(p)&&(c+=15);return a.category.toLowerCase().includes(p)&&(c+=5),c}function tp(a,u){const c=[],p=u.toLowerCase(),f=3;if(a.title.toLowerCase().includes(p)&&(c.push(a.title),c.length>=f)||a.excerpt.toLowerCase().includes(p)&&(c.push(a.excerpt),c.length>=f))return c;const j=a.content.split(`
`).filter(w=>w.trim());for(const w of j)if(w.toLowerCase().includes(p)){const z=w.replace(/#{1,6}\s?/g,"").trim();if(z.length>10&&(c.push(z),c.length>=f))break}return c}function rp(){return R.useMemo(()=>{const u={};return Me.forEach(c=>{c.tags.forEach(p=>{u[p]=(u[p]||0)+1})}),Object.entries(u).map(([c,p])=>({tag:c,count:p})).sort((c,p)=>p.count-c.count)},[])}function sp({slug:a}){var w,z;const{setCategory:u,clearFilters:c}=zc();R.useEffect(()=>{window.location.hash!==`#/docs/${a}`&&window.history.replaceState(null,"",`#/docs/${a}`)},[a]);const p=ep(a);if(!p)return r.jsxs(r.Fragment,{children:[r.jsx(jn,{page:"docs"}),r.jsx("main",{className:"shell page-main docs-page",children:r.jsxs("div",{className:"docs-not-found",children:[r.jsx(Y,{name:"doc",size:48,className:"not-found-icon"}),r.jsx("h1",{children:"Page Not Found"}),r.jsxs("p",{children:[`We couldn't find documentation for "`,a,'".']}),r.jsxs("div",{className:"not-found-actions",children:[r.jsx("button",{onClick:()=>me("/docs"),children:"Browse all documentation"}),r.jsx("button",{onClick:()=>{me("/docs"),c()},children:"Clear filters"})]})]})}),r.jsx(Kt,{})]});const j=(y=>{const F=y.split(`
`),N=[];let T=[];const D=()=>{T.length>0&&(N.push(r.jsx("ul",{className:"doc-content-list",children:T.map((K,I)=>r.jsx("li",{children:K},I))},`list-${N.length}`)),T=[])};return F.forEach((K,I)=>{const A=K.trim();if(!A){D(),N.push(r.jsx("div",{className:"doc-content-spacer"},I));return}if(A.startsWith("# ")){D(),N.push(r.jsx("h2",{className:"doc-heading doc-heading-h2",children:A.slice(2)},I));return}if(A.startsWith("## ")){D(),N.push(r.jsx("h3",{className:"doc-heading doc-heading-h3",children:A.slice(3)},I));return}if(A.startsWith("### ")){D(),N.push(r.jsx("h4",{className:"doc-heading doc-heading-h4",children:A.slice(4)},I));return}if(A.startsWith("> ")){D(),N.push(r.jsx("blockquote",{className:"doc-blockquote",children:A.slice(2)},I));return}if(A.startsWith("```")){D();const E=[];let U=I+1;for(;U<F.length&&F[U].trim()!=="```";)E.push(F[U]),U++;N.push(r.jsx("pre",{className:"doc-code-block",children:r.jsx("code",{children:E.join(`
`)})},I));return}if(A.startsWith("`")&&A.endsWith("`")&&A.length>2){D(),N.push(r.jsx("code",{className:"doc-inline-code",children:A.slice(1,-1)},I));return}if(A.startsWith("- ")||A.startsWith("* ")){T.push(A.slice(2));return}if(/^\d+\.\s/.test(A)){T.push(A.replace(/^\d+\.\s/,""));return}D(),N.push(r.jsx("p",{className:"doc-paragraph",children:A},I))}),D(),N})(p.content);return r.jsxs(r.Fragment,{children:[r.jsx(jn,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page docs-detail-page",children:[r.jsx("div",{className:"docs-detail-back",children:r.jsxs("button",{onClick:()=>me("/docs"),className:"back-button",children:[r.jsx(Y,{name:"arrow",size:16}),"Back to Documentation"]})}),r.jsxs("header",{className:"doc-article-header",children:[r.jsxs("div",{className:"doc-article-meta",children:[r.jsx("span",{className:"doc-category-badge",children:((w=st.find(y=>y.id===p.category))==null?void 0:w.label)||p.category}),r.jsxs("span",{className:"doc-order-badge",children:["Article #",p.order]})]}),r.jsx("h1",{className:"doc-article-title",children:p.title}),r.jsx("p",{className:"doc-article-excerpt",children:p.excerpt}),r.jsx("div",{className:"doc-article-tags",children:p.tags.map(y=>r.jsxs("span",{className:"doc-tag-pill",children:["#",y]},y))})]}),r.jsx("article",{className:"doc-article-content",children:j}),r.jsx("footer",{className:"doc-article-footer",children:r.jsx("div",{className:"doc-nav-container",children:r.jsxs("div",{className:"doc-nav-col",children:[r.jsx("span",{className:"doc-nav-label",children:"Category"}),r.jsxs("button",{className:"doc-nav-link",onClick:()=>{u(p.category),me("/docs")},children:[r.jsx(Y,{name:"arrow",size:14}),"View all ",(z=st.find(y=>y.id===p.category))==null?void 0:z.label]})]})})}),j.filter(y=>y.type==="h2"||y.type==="h3").length>0&&r.jsxs("aside",{className:"doc-toc",children:[r.jsxs("div",{className:"toc-title",children:[r.jsx(Y,{name:"utility",size:16}),r.jsx("span",{children:"On this page"})]}),r.jsx("nav",{className:"toc-nav",children:j.filter(y=>y.type==="h2"||y.type==="h3").map((y,F)=>{var T;const N=(T=y.props.className)==null?void 0:T.includes("doc-heading-h2");return r.jsx("a",{href:`#${N?"h2-":"h3-"}-${F}`,className:`toc-link ${N?"toc-h2":"toc-h3"}`,children:y.props.children},F)})})]})]}),r.jsx(Kt,{})]})}function ip(){var se,ie;const[a,u]=R.useState(!1),[c,p]=R.useState(""),[f,j]=R.useState(!1),{filters:w,setQuery:z,setCategory:y,toggleTag:F,clearFilters:N,results:T,hasActiveFilters:D,resultCount:K}=zc(),I=rp();R.useEffect(()=>{const M=()=>{const Z=window.location.hash.slice(1);if(Z.startsWith("#/docs/")){const fe=Z.replace("#/docs/",""),Ee=Me.find(hn=>hn.slug===fe);Ee&&(p(Ee.category),y(Ee.category))}};return M(),window.addEventListener("hashchange",M),()=>window.removeEventListener("hashchange",M)},[]);const A=()=>{j(!0)},E=M=>{p(M),y(M),u(!1)},U=()=>{w.query||j(!1)},S=M=>{me(`/docs/${M}`),z(""),j(!1)},re=R.useMemo(()=>{const M={};return T.forEach(Z=>{const fe=Z.page.category;M[fe]||(M[fe]=[]),M[fe].push(Z)}),M},[T]);return r.jsxs(r.Fragment,{children:[r.jsx(jn,{page:"docs"}),r.jsxs("main",{className:"shell page-main docs-page",children:[r.jsx("div",{className:"docs-hero",children:r.jsxs("div",{className:"docs-hero-content",children:[r.jsx("div",{className:"eyebrow docs-eyebrow",children:"Documentation Center"}),r.jsxs("h1",{className:"docs-title",children:["Everything you need to know about",r.jsx("br",{}),r.jsx("span",{className:"title-accent",children:"using Niko"})]}),r.jsx("p",{className:"docs-subtitle",children:"Comprehensive guides, command references, and tips to help you get the most out of your server bot."})]})}),r.jsx("div",{className:`docs-search-section ${f?"active":""}`,children:r.jsxs("div",{className:"docs-search-container",children:[r.jsx(Jh,{value:w.query,onChange:z,placeholder:"Search documentation, commands, guides...",onFocus:A,onBlur:U}),f&&w.query&&T.length>0&&r.jsxs("div",{className:"search-results-dropdown",children:[r.jsxs("div",{className:"search-results-header",children:[r.jsxs("span",{className:"results-count",children:[K," ",K===1?"result":"results"]}),r.jsx("button",{className:"clear-search-btn",onClick:()=>{z(""),N(),p("")},children:"Clear"})]}),r.jsx("div",{className:"search-results-list",children:T.slice(0,8).map((M,Z)=>r.jsxs("button",{className:"search-result-item",onClick:()=>S(M.page.slug),onMouseEnter:()=>{},children:[r.jsx("div",{className:"result-icon",children:r.jsx(Y,{name:"doc",size:18})}),r.jsxs("div",{className:"result-content",children:[r.jsx("div",{className:"result-title",children:M.page.title}),r.jsx("div",{className:"result-excerpt",children:M.page.excerpt}),M.highlights.length>0&&r.jsxs("div",{className:"result-highlight",children:[M.highlights[0].slice(0,100),"..."]})]}),r.jsx(Y,{name:"arrow",size:14,className:"result-arrow"})]},M.page.slug))}),T.length>8&&r.jsx("div",{className:"search-results-footer",children:r.jsxs("span",{children:["Showing 8 of ",T.length," results. Browse all docs below."]})})]})]})}),r.jsxs("div",{className:"docs-mobile-nav",children:[r.jsx("button",{className:"mobile-menu-toggle",onClick:()=>u(!a),"aria-label":"Toggle documentation menu",children:r.jsx(Y,{name:"utility",size:20})}),a&&r.jsxs("div",{className:"mobile-nav-panel",children:[r.jsxs("div",{className:"mobile-nav-header",children:[r.jsx("h3",{children:"Documentation"}),r.jsx("button",{className:"close-menu-btn",onClick:()=>u(!1),"aria-label":"Close menu",children:r.jsx(Y,{name:"utility",size:16,className:"rotated"})})]}),r.jsx("div",{className:"mobile-nav-sections",children:st.map(M=>r.jsxs("button",{className:`mobile-nav-item ${c===M.id?"active":""}`,onClick:()=>{E(M.id)},children:[r.jsx(Y,{name:M.icon,size:18}),r.jsx("span",{className:"mobile-section-label",children:M.label}),r.jsx("span",{className:"mobile-section-count",children:M.count})]},M.id))})]})]}),I.length>0&&!D&&r.jsxs("div",{className:"docs-tags-cloud",children:[r.jsxs("div",{className:"tags-cloud-title",children:[r.jsx(Y,{name:"utility",size:16}),r.jsx("span",{children:"Popular Topics"})]}),r.jsx("div",{className:"tags-cloud-list",children:I.slice(0,15).map(({tag:M,count:Z})=>r.jsxs("button",{className:"tag-cloud-item",onClick:()=>F(M),style:{fontSize:`${.75+Math.min(Z/4,1)}rem`},children:["#",M,r.jsx("span",{className:"tag-count",children:Z})]},M))})]}),r.jsx("div",{className:"docs-category-filters",children:r.jsx(Zh,{selectedCategory:w.category,onSelectCategory:E,sections:st})}),D&&r.jsxs("div",{className:"docs-results-header",children:[r.jsxs("div",{className:"results-info",children:[r.jsxs("span",{className:"results-count-large",children:[K," ",K===1?"article":"articles"]}),w.query&&r.jsxs("span",{className:"search-query-display",children:['for "',r.jsx("strong",{children:w.query}),'"']})]}),r.jsxs("button",{className:"clear-all-btn",onClick:()=>{N(),p("")},disabled:!D,children:[r.jsx(Y,{name:"utility",size:14}),"Clear all filters"]})]}),r.jsx("div",{className:"docs-content",children:D?r.jsx("div",{className:"search-results-view",children:Object.entries(re).map(([M,Z])=>{var fe;return r.jsxs("section",{className:"results-category",children:[r.jsx("h2",{className:"category-title",children:((fe=st.find(Ee=>Ee.id===M))==null?void 0:fe.label)||M}),r.jsx("div",{className:"category-results-grid",children:Z.map(Ee=>r.jsx(oa,{doc:Ee,variant:"highlighted"},Ee.page.slug))})]},M)})}):c?r.jsxs("div",{className:"category-view",children:[r.jsxs("div",{className:"category-header",children:[r.jsx("h2",{className:"category-page-title",children:((se=st.find(M=>M.id===c))==null?void 0:se.label)||c}),r.jsx("p",{className:"category-description",children:(ie=st.find(M=>M.id===c))==null?void 0:ie.description})]}),r.jsx("div",{className:"category-articles",children:Me.filter(M=>M.category===c).sort((M,Z)=>M.order-Z.order).map(M=>r.jsx(oa,{doc:M},M.slug))})]}):r.jsx("div",{className:"all-categories-view",children:st.map(M=>r.jsxs("section",{className:"docs-section",id:`section-${M.id}`,children:[r.jsxs("div",{className:"section-header",children:[r.jsx("div",{className:"section-icon",children:r.jsx(Y,{name:M.icon,size:28})}),r.jsxs("div",{className:"section-info",children:[r.jsx("h2",{className:"section-title",children:M.label}),r.jsx("p",{className:"section-description",children:M.description})]}),r.jsx("span",{className:"section-count",children:M.count})]}),r.jsx("div",{className:"section-articles",children:Me.filter(Z=>Z.category===M.id).sort((Z,fe)=>Z.order-fe.order).map(Z=>r.jsx(oa,{doc:Z},Z.slug))})]},M.id))})}),r.jsxs("div",{className:"docs-footer-note",children:[r.jsx(Y,{name:"book",size:20}),r.jsxs("div",{children:[r.jsx("strong",{children:"Want more detail?"}),r.jsxs("p",{children:["The repository includes setup, maintenance, intent verification, provider compatibility, and API documentation in the"," ",r.jsx("a",{href:"https://github.com/developer51709/Niko",target:"_blank",rel:"noreferrer",children:"docs/"})," ","folder."]})]})]})]}),r.jsx(Kt,{})]})}function op(){const a=Zs(),[u,c]=R.useState(null);R.useEffect(()=>{Tc().then(c).catch(()=>{})},[]);const p=[["spark","AI that remembers","Thoughtful conversation with a cozy personality and controls that respect your community."],["chart","A living economy","Jobs, banking, casino, shops, achievements, and leaderboards that give members a reason to return."],["shield","Confident moderation","Automod, anti-raid protection, warnings, and logs designed to keep the room welcoming."],["users","Community rituals","Giveaways, tickets, polls, birthdays, highlights, and tiny moments that make a server feel like home."]];return r.jsxs(r.Fragment,{children:[r.jsx(jn,{page:"home"}),r.jsxs("main",{children:[r.jsxs("section",{className:"hero shell",children:[r.jsxs("div",{className:"hero-copy",children:[r.jsxs("div",{className:"eyebrow",children:[r.jsx("span",{className:"status-dot"})," Discord companion · online"]}),r.jsxs("h1",{children:["Useful tools for a ",r.jsx("em",{children:"better server."})]}),r.jsx("p",{children:"Niko handles the everyday work of running a Discord community, so your moderators can focus on the people in it."}),r.jsxs("div",{className:"hero-buttons",children:[r.jsxs("a",{className:"button button-primary",href:(a==null?void 0:a.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Invite Niko ",r.jsx(Y,{name:"arrow"})]}),r.jsx("a",{className:"button button-muted",href:"/commands",onClick:f=>{f.preventDefault(),me("/commands")},children:"Explore commands"})]}),r.jsxs("div",{className:"stats-strip",children:[r.jsxs("div",{children:[r.jsx("strong",{children:be(u==null?void 0:u.guild_count)}),r.jsx("span",{children:"servers"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:be(u==null?void 0:u.user_count)}),r.jsx("span",{children:"members"})]}),r.jsxs("div",{children:[r.jsx("strong",{children:be(u==null?void 0:u.command_count)}),r.jsx("span",{children:"commands"})]})]})]}),r.jsx("div",{className:"hero-art","aria-label":"A preview of Niko's server workspace",children:r.jsxs("div",{className:"workspace-preview",children:[r.jsxs("div",{className:"workspace-preview-top",children:[r.jsxs("span",{className:"preview-dots",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]}),r.jsx("span",{children:"server workspace"}),r.jsxs("span",{className:"preview-status",children:[r.jsx("span",{className:"status-dot"})," live"]})]}),r.jsxs("div",{className:"preview-body",children:[r.jsxs("div",{className:"preview-sidebar",children:[r.jsx("span",{className:"preview-label",children:"NIKO"}),r.jsx("b",{children:"Overview"}),r.jsx("span",{children:"Economy"}),r.jsx("span",{children:"Leveling"}),r.jsx("span",{children:"Moderation"}),r.jsx("span",{children:"AI controls"})]}),r.jsxs("div",{className:"preview-main",children:[r.jsx("span",{className:"preview-label",children:"SERVER SNAPSHOT"}),r.jsx("strong",{children:"Everything in one place."}),r.jsxs("div",{className:"preview-stats",children:[r.jsxs("span",{children:[r.jsx("b",{children:be(u==null?void 0:u.user_count)}),r.jsx("small",{children:"members"})]}),r.jsxs("span",{children:[r.jsx("b",{children:be(u==null?void 0:u.command_count)}),r.jsx("small",{children:"commands"})]})]}),r.jsxs("div",{className:"preview-line",children:[r.jsx("i",{}),r.jsx("i",{}),r.jsx("i",{})]})]})]})]})})]}),r.jsxs("section",{className:"shell intro-section",children:[r.jsx("div",{className:"section-kicker",children:"Why Niko"}),r.jsxs("div",{className:"intro-grid",children:[r.jsxs("h2",{children:["The good kind of",r.jsx("br",{}),r.jsx("em",{children:"always-on."})]}),r.jsx("p",{children:"Not another noisy utility bot. Niko is a dependable layer for your server: easy to configure, satisfying to use, and quietly full of details that make members smile."})]})]}),r.jsx("section",{className:"shell feature-grid",children:p.map(([f,j,w])=>r.jsxs("article",{className:"feature-card",children:[r.jsx("span",{className:"feature-icon",children:r.jsx(Y,{name:f})}),r.jsx("h3",{children:j}),r.jsx("p",{children:w}),r.jsxs("a",{href:"/docs",onClick:z=>{z.preventDefault(),me("/docs")},children:["Learn more ",r.jsx(Y,{name:"arrow"})]})]},j))}),r.jsxs("section",{className:"shell callout",children:[r.jsxs("div",{children:[r.jsx("div",{className:"section-kicker",children:"Ready when you are"}),r.jsxs("h2",{children:["A calmer, cleverer home",r.jsx("br",{}),"for your community."]})]}),r.jsxs("a",{className:"button button-primary",href:(a==null?void 0:a.invite_url)||"#",target:"_blank",rel:"noreferrer",children:["Bring Niko in ",r.jsx(Y,{name:"arrow"})]})]})]}),r.jsx(Kt,{})]})}const ap=[{code:"USDT",label:"Tether"},{code:"ETH",label:"Ethereum"},{code:"BTC",label:"Bitcoin"},{code:"BNB",label:"BNB"},{code:"LTC",label:"Litecoin"},{code:"DOGE",label:"Dogecoin"},{code:"TRX",label:"TRON"},{code:"XMR",label:"Monero"}];function lp(){const u=new URLSearchParams(window.location.search).get("token")||"",[c,p]=R.useState("5"),[f,j]=R.useState("USDT"),[w,z]=R.useState(!1),[y,F]=R.useState(""),[N,T]=R.useState(null),[D,K]=R.useState(null),[I,A]=R.useState(!1);R.useEffect(()=>{u||A(!0)},[u]),R.useEffect(()=>{if(!(N!=null&&N.status_url)||N.paid)return;const U=setInterval(async()=>{try{const S=await Je(N.status_url);K(S),S.paid&&clearInterval(U)}catch{}},5e3);return()=>clearInterval(U)},[N]);const E=async U=>{U.preventDefault(),z(!0),F("");try{const S=await Je("/api/donations/invoice",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:u,amount:parseFloat(c),currency:f})});T(S),S.error&&(F(S.error),T(null))}catch(S){F(S instanceof Error?S.message:"Could not create invoice.")}finally{z(!1)}};return I?r.jsxs(r.Fragment,{children:[r.jsx(jn,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"!"}),r.jsx("div",{className:"eyebrow",children:"Invalid donation link"}),r.jsxs("h1",{children:["This link is ",r.jsx("em",{children:"invalid."})]}),r.jsxs("p",{children:["The donation link is missing or has expired. Use the"," ",r.jsx("code",{children:"/donate"})," command in Discord to generate a new one."]}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>me("/"),children:"Return home"})]})})]}):D!=null&&D.paid?r.jsxs(r.Fragment,{children:[r.jsx(jn,{page:"home"}),r.jsx("main",{className:"auth-page",children:r.jsxs("div",{className:"auth-card",style:{textAlign:"center"},children:[r.jsx("span",{className:"auth-mark",children:"✓"}),r.jsx("div",{className:"eyebrow",children:"Payment confirmed"}),r.jsxs("h1",{children:["Thank you ",r.jsx("em",{children:"for supporting!"})]}),r.jsx("p",{children:"Your donation has been confirmed. You will receive the Supporter badge shortly."}),r.jsx("button",{className:"button button-primary full-width",onClick:()=>me("/"),children:"Return home"})]})})]}):r.jsxs(r.Fragment,{children:[r.jsx(jn,{page:"home"}),r.jsx("main",{className:"page-main",children:r.jsx("div",{className:"shell",children:r.jsxs("div",{className:"page-heading",style:{maxWidth:500,margin:"0 auto"},children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:15},children:"Support Niko"}),r.jsxs("h1",{children:["Keep Niko ",r.jsx("em",{children:"running."})]}),r.jsx("p",{style:{color:"var(--muted)",marginBottom:30},children:"Your donation helps cover hosting costs and keeps Niko running for all servers. Choose an amount and cryptocurrency below."}),N!=null&&N.pay_link?r.jsxs("div",{className:"dash-panel",style:{marginBottom:24},children:[r.jsx("div",{className:"panel-heading",children:r.jsxs("div",{children:[r.jsx("span",{className:"panel-kicker",children:"Invoice created"}),r.jsx("h3",{children:"Complete your payment"})]})}),r.jsxs("p",{style:{color:"var(--muted)",fontSize:12,marginBottom:16},children:["Amount: ",r.jsxs("strong",{children:["$",parseFloat(c).toFixed(2)," USD"]})," in"," ",r.jsx("strong",{children:f})]}),r.jsxs("p",{style:{color:"var(--dim)",fontSize:10,marginBottom:16},children:["Track ID: ",r.jsx("code",{children:N.track_id})," · Expires in 60 minutes"]}),r.jsxs("a",{className:"button button-primary",href:N.pay_link,target:"_blank",rel:"noopener noreferrer",children:["Pay now ",r.jsx(Y,{name:"arrow"})]}),r.jsx("p",{style:{color:"var(--dim)",fontSize:10,marginTop:12},children:"Payment will be confirmed automatically once the transaction is processed on-chain."})]}):r.jsxs("form",{onSubmit:E,className:"dash-panel",style:{marginBottom:24},children:[r.jsxs("div",{className:"form-grid",children:[r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Amount (USD)"}),r.jsx("input",{type:"number",min:"1",max:"10000",step:"0.01",value:c,onChange:U=>p(U.target.value)}),r.jsx("small",{children:"Minimum $1.00, maximum $10,000.00"})]}),r.jsxs("label",{className:"form-field",children:[r.jsx("span",{className:"form-label",children:"Cryptocurrency"}),r.jsx("select",{value:f,onChange:U=>j(U.target.value),children:ap.map(U=>r.jsxs("option",{value:U.code,children:[U.label," (",U.code,")"]},U.code))})]})]}),y&&r.jsx("p",{className:"form-error",style:{marginTop:12},role:"alert",children:y}),r.jsx("div",{style:{marginTop:16},children:r.jsx("button",{className:"button button-primary",type:"submit",disabled:w,children:w?"Creating invoice…":"Create invoice"})})]}),r.jsxs("div",{className:"docs-footer-note",style:{marginTop:20},children:[r.jsx("strong",{children:"How it works"}),r.jsx("p",{children:'1. Choose an amount and currency above · 2. Click "Pay now" to open the payment page · 3. Send crypto to the displayed address · 4. Payment is confirmed automatically once processed on-chain'})]})]})})})]})}const up={privacy:{title:"Privacy policy",intro:"Niko stores only the information needed to provide its Discord features. This page is the public, human-readable version of the policy.",sections:[["Information we use","User IDs connect economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings. Server IDs keep per-server settings. Message content is processed in real time for AI, moderation, snipe, highlights, and leveling; short AI history is retained for the conversation feature."],["How it is used","Data is used only to operate Niko inside Discord. We do not sell, share, or transfer it for advertising."],["Storage and retention","Data is stored by the server hosting Niko in local JSON and SQLite files. Economy, leveling, and configuration data remain until removed. AI conversation history is limited and can be cleared with /clearhistory."],["Third-party services","When enabled, AI messages and limited context are sent to the configured AI provider to generate a reply. Provider privacy terms also apply. Music and external lookup features may contact their respective services."],["Your choices","Request deletion of data associated with your User ID by contacting the bot owner through the support server. Material changes are announced there."]]},terms:{title:"Terms of service",intro:"By using Niko in a Discord server, you agree to these terms, Discord’s Terms of Service, and Discord’s Community Guidelines.",sections:[["Permitted use","Use Niko for personal, non-commercial community features. Do not use it to harass, spam, harm, violate law, exploit, reverse-engineer, or disrupt the service."],["Availability","Niko is provided as-is without an uptime guarantee. Features may change, be restricted, or be removed without notice."],["Moderation","The operator may blacklist a user or server for abuse, exploitation, or a violation of these terms."],["AI content","AI replies can be inaccurate or unexpected. Verify important information independently; the operator is not liable for harm from generated content."],["Virtual items","In-bot currency and items have no real-world value and cannot be exchanged for money or goods. Balances may be reset."],["Contact","Questions or concerns can be sent through the Niko support server."]]}};function Pc({type:a}){const u=up[a];return r.jsxs(r.Fragment,{children:[r.jsx(jn,{page:a}),r.jsxs("main",{className:"shell page-main legal-page",children:[r.jsxs("div",{className:"page-heading",children:[r.jsx("div",{className:"eyebrow",children:"Niko legal"}),r.jsx("h1",{children:u.title}),r.jsx("p",{children:u.intro}),r.jsx("small",{children:"Effective date: 1 January 2025"})]}),r.jsx("div",{className:"legal-copy",children:u.sections.map(([c,p])=>r.jsxs("section",{children:[r.jsx("h2",{children:c}),r.jsx("p",{children:p})]},c))})]}),r.jsx(Kt,{})]})}const cp=[{key:"txt",label:"TXT",icon:"📄"},{key:"html",label:"HTML",icon:"🌐"},{key:"csv",label:"CSV",icon:"📊"},{key:"json",label:"JSON",icon:"{ }"}];function dp({transcriptId:a}){const[u,c]=R.useState(null),[p,f]=R.useState(!0),[j,w]=R.useState("");R.useEffect(()=>{f(!0),w(""),fetch(`/api/transcript/${a}`).then(y=>{if(!y.ok)throw new Error("Transcript not found");return y.json()}).then(y=>{c(y),f(!1)}).catch(y=>{w(y.message||"Failed to load transcript"),f(!1)})},[a]);const z=y=>{window.open(`/api/transcript/${a}/download?format=${y}`,"_blank")};return p?r.jsx("div",{className:"page-main",children:r.jsx("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:r.jsx("div",{style:{color:"var(--muted)",fontSize:14},children:"Loading transcript…"})})}):j||!u?r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{textAlign:"center",padding:"60px 20px"},children:[r.jsx("h2",{style:{marginBottom:12},children:"Transcript not found"}),r.jsx("p",{style:{color:"var(--muted)"},children:j||"This transcript doesn't exist or has been deleted."})]})}):r.jsx("div",{className:"page-main",children:r.jsxs("div",{className:"shell",style:{maxWidth:800},children:[r.jsx("div",{style:{background:"var(--surface)",border:"1px solid var(--line)",borderRadius:8,padding:24,marginBottom:20},children:r.jsxs("div",{style:{display:"flex",alignItems:"flex-start",justifyContent:"space-between",gap:16,flexWrap:"wrap"},children:[r.jsxs("div",{children:[r.jsx("div",{className:"eyebrow",style:{marginBottom:8},children:"Ticket Transcript"}),r.jsxs("h1",{style:{fontSize:24,letterSpacing:"-0.04em",margin:0},children:["#",u.channel_name]}),r.jsxs("div",{style:{color:"var(--muted)",fontSize:13,marginTop:6},children:[u.category," · ",u.message_count," messages · ",u.created_at]})]}),r.jsx("div",{style:{display:"flex",gap:8,flexWrap:"wrap"},children:cp.map(y=>r.jsxs("button",{className:"button button-small button-muted",onClick:()=>z(y.key),style:{minWidth:70},children:[r.jsx("span",{children:y.icon}),r.jsx("span",{children:y.label})]},y.key))})]})}),r.jsxs("div",{style:{background:"#1e1f22",border:"1px solid #3f4147",borderRadius:8,overflow:"hidden"},children:[u.messages.map((y,F)=>r.jsxs("div",{style:{padding:"10px 16px",borderBottom:"1px solid #2b2d31",fontSize:14,lineHeight:1.6},children:[r.jsx("span",{style:{color:"#949ba4",fontSize:11,fontFamily:"monospace"},children:y.timestamp})," ",r.jsx("span",{style:{color:"#f2f3f5",fontWeight:600},children:y.author})," ",r.jsxs("span",{style:{color:"#949ba4",fontSize:11},children:["(",y.author_id,")"]}),":"," ",r.jsx("span",{style:{color:"#dbdee1"},children:y.content}),y.attachments&&y.attachments.length>0&&r.jsx("div",{style:{marginTop:4},children:y.attachments.map((N,T)=>r.jsx("a",{href:N,target:"_blank",rel:"noopener noreferrer",style:{color:"#00a8fc",fontSize:12,textDecoration:"none"},children:"📎 Attachment"},T))})]},F)),u.messages.length===0&&r.jsx("div",{style:{padding:40,textAlign:"center",color:"#949ba4"},children:"No messages in this transcript."})]}),r.jsxs("div",{style:{marginTop:16,padding:"12px 0",textAlign:"center",color:"var(--dim)",fontSize:12},children:["Transcript ID: ",r.jsx("code",{style:{fontFamily:"monospace"},children:a})]})]})})}function mp(){const[a,u]=R.useState(vc);if(R.useEffect(()=>{const c=()=>u(vc());return window.addEventListener("popstate",c),()=>window.removeEventListener("popstate",c)},[]),a==="commands")return r.jsx(Mh,{});if(a==="docs-detail"){const c=window.location.pathname.split("/"),p=c[c.length-1];return r.jsx(sp,{slug:p})}if(a==="docs")return r.jsx(ip,{});if(a==="dashboard")return r.jsx(Yh,{});if(a==="privacy")return r.jsx(Pc,{type:"privacy"});if(a==="terms")return r.jsx(Pc,{type:"terms"});if(a==="donate")return r.jsx(lp,{});if(a==="transcript"){const p=window.location.pathname.split("/").filter(Boolean)[1]||"";return r.jsx(dp,{transcriptId:p})}return r.jsx(op,{})}Vm.createRoot(document.getElementById("root")).render(r.jsx(R.StrictMode,{children:r.jsx(mp,{})}));
