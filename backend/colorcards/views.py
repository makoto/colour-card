from bitmerchant.wallet.keys import PublicKey, PrivateKey
import cups
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from ecdsa import SigningKey
from ecdsa import VerifyingKey
from ecdsa import SECP256k1
import ethereum.keys
from mnemonic import Mnemonic
import os
import subprocess
from web3.main import to_checksum_address
import yaml

from .printer import CardPrinter


ACTUALLY_PRINT = True


mnemonic = Mnemonic('english')

formatter = yaml.load(open(os.path.join(os.path.dirname(__file__), 'colorcard.yaml')))
generator = CardPrinter(formatter)


def derive_address(public_key):
    """Derives an Ethereum address from a user's deserialized public key.

    Args:
      publick_key: A bitmerchant.wallet.keys.PublicKey instance
    Returns:
      A hex formatted Ethereum address.
    """
    return to_checksum_address(ethereum.keys.sha3(public_key.get_key().decode('hex')[1:])[12:].encode('hex'))


def derive_final_pubkey(user_pubkey, mfr_secret):
    """Derives a final public key from a user's public key and a manufacturer's secret data.

    Args:
      user_pubkey: bytes: A user's public key
      mfr_secret: bytes: A manufacturer's secret data
    Returns:
      address: bitmerchant.wallet.keys.PublicKey: A public key
    """
    verkey = user_pubkey._verifying_key
    mfr_secret_int = int(mfr_secret.encode('hex'), 16)
    final_pubkey = PublicKey(VerifyingKey.from_public_point(verkey.pubkey.point * mfr_secret_int, curve=SECP256k1))
    return final_pubkey


def create_mnemonic(salt):
    salt = salt.decode('hex')
    entropy = salt + os.urandom(16 - len(salt))
    return mnemonic.to_mnemonic(entropy)


def create_address(user_pubkey, mnem):
    mfr_data = Mnemonic.to_seed(mnem)
    final_pubkey = derive_final_pubkey(PublicKey.from_hex_key(user_pubkey), mfr_data[:32])
    return derive_address(final_pubkey)


def index(request):
    return render(request, 'templates/index.html', {})


@require_POST
@csrf_exempt
def order(request):
    print request.POST
    pubkey = request.POST['pubkey']
    salt = request.POST['salt']
    mnem = create_mnemonic(salt)
    address = create_address(pubkey, mnem)
    card = generator.generate({
        'mnemonic': mnem,
        'address': address,
        'name': request.POST['name'],
    })
    print_card('EVOLIS_Primacy', card)
    return redirect('/done')


def print_card(printerName, card):
    if ACTUALLY_PRINT:
        conn = cups.Connection()
        job = conn.createJob(printerName, 'ether.cards', {'GRibbonType': 'RC_YMCKO'})
        conn.startDocument(printerName, job, 'card.pdf', 'application/pdf', 1)
        conn.writeRequestData(card, len(card))
        conn.finishDocument(printerName)
    else:
        open('card.pdf', 'w').write(card)
        subprocess.call(["open", "card.pdf"])


def done(request):
    return render(request, 'templates/done.html', {})
