// Import the page's CSS. Webpack will know what to do with it.
// import "../stylesheets/app.scss";
import "../sass/styles.scss";

let logo = require("file-loader?name=assets/tcc-logo-large.svg!../assets/tcc-logo-large.svg");
let menu = require("file-loader?name=assets/menu-btn.svg!../assets/menu-btn.svg");
console.log('logo', logo);
console.log('menu', menu);

let bip39 = import('bip39');
let crypto = import('crypto');
let secp256k1 = import('secp256k1');
let password = 'hello world';
let salt, seed, publicKey, data;
let host = 'http://bb6ce398.ngrok.io/order';
let jquery = import('jquery');

crypto.then(function(c){
  return c.randomBytes(16)
}).then(function(r){
  salt = r.toString('hex');
  console.log('salt', salt);
  return bip39
}).then(function(b){
  return b.mnemonicToSeed(password, salt)
}).then(function(r){
  seed = r;
  console.log('seed', seed.toString('hex'));
  return secp256k1;
}).then(function(s){
  return s.publicKeyCreate(seed.slice(0,32))
}).then(function(r){
  publicKey = r.toString('hex');
  console.log('publicKey', publicKey);
  data = {pubkey:publicKey, salt:salt};
  console.log('sending data', data);
  return jquery;
}).then(function(j){
  // j.post(host, data);
})
