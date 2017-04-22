import "../sass/styles.scss";

console.log('redeem');

async function run(){
  let bip39 = await import('bip39');
  let secp256k1 = await import("secp256k1");
  let util = require("ethereumjs-util");
  let mnemonic = 'cheap time globe subway hurry gas reopen dog draft burger barely joy';
  let entropy = await bip39.mnemonicToEntropy(mnemonic);
  let salt = entropy.slice(0, 16);
  let mfr_data = await bip39.mnemonicToSeed(mnemonic).slice(0, 32);
  let user_data = await bip39.mnemonicToSeed('foobar', salt).slice(0, 32);
  let privkey = await secp256k1.privateKeyTweakMul(user_data, mfr_data);
  let pubkey = await secp256k1.publicKeyCreate(privkey, false).slice(1);
  console.log(pubkey.length);
  console.log(pubkey.toString('hex'))
  var addr = util.pubToAddress(pubkey);
  console.log(addr.toString("hex"));
  // debugger;
}

run();
