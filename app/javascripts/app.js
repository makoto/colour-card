// Import the page's CSS. Webpack will know what to do with it.
// import "../stylesheets/app.scss";
import "../sass/styles.scss";

let logo = require("file-loader?name=assets/tcc-logo-large.svg!../assets/tcc-logo-large.svg");
let menu = require("file-loader?name=assets/menu-btn.svg!../assets/menu-btn.svg");
console.log('logo', logo);
console.log('menu', menu);

// import Vue from 'vue';

let bip39 = require('bip39');
let crypto = require('crypto');
let secp256k1 = require('secp256k1');
let salt, seed, publicKey, data;
let host = 'http://bb6ce398.ngrok.io/order';
let jquery = require('jquery');

var order = function(password){
  console.log('password', password);
  salt = crypto.randomBytes(16).toString('hex');
  seed = bip39.mnemonicToSeed(password, salt)
  // console.log('seed', seed.toString('hex'));
  publicKey = secp256k1.publicKeyCreate(seed.slice(0,32)).toString('hex');
  // console.log('publicKey', publicKey);
  data = {pubkey:publicKey, salt:salt};
  console.log('sending data', data);
  // jquery.post(host, data);
  return false;
}

window.addEventListener('load', function(){
  var app = new Vue({
    el: '#main',
    data: {
      message: 'Hello world!',
      password: null
    },
    methods: {
      order: function() {
        return order(this.password);
      }
    }
  })
})
