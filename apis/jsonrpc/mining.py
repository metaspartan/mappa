from app import jsonrpc, node16Url
from flask import request
from struct import pack, unpack
from .client import requestJsonRPC

@jsonrpc.method('getdifficulty()')
def getDifficulty():
    response = requestJsonRPC(node16Url, "getdifficulty", [])
    if "error" in response and response["error"] is not None:
        raise ValueError(response["error"])
    else:
        return response["result"]

@jsonrpc.method('getwork(data=str)')
def getWork(data = None):
    if not request.get_json():
        raise ValueError(f'Requires JSON RPC, mime type is {request.mimetype}, should be application/json')
    minerAddress = request.get_json().get("address", None)
    response = requestJsonRPC(node16Url, "getwork", [] if data == None else [data])
    if "error" in response and response["error"] is not None:
        raise ValueError(response["error"])
    else: # node responded with success
        if data and minerAddress: # getwork submit with miner address
            dataBytes = bytes.fromhex(data)
            header = pack('<20I', *unpack('!20I', dataBytes[:80]))
            (version, prev, merkle, epoch, bits, nonce) = unpack('<I32s32s3I', header)
            mined = (1 << 48) * 999 // (bits * bits) + 1
            txResponse = requestJsonRPC(node16Url, "sendtoaddress", [minerAddress, mined])
            import json
            print(f'Send {mined} coin to {minerAddress}: {json.dumps(txResponse, indent=4)}')
        return response["result"]

@jsonrpc.method('getblocktemplate(capabilities=dict)')
def getBlockTemplate(capabilities = None):
    response = requestJsonRPC(node16Url, "getblocktemplate", [capabilities] if capabilities else [])
    if "error" in response and response["error"] != None:
        raise ValueError(response["error"])
    else:
        return response["result"]

@jsonrpc.method('submitblock(hexData=str, options=dict)')
def submitBlock(hexData, options = {}):
    response = requestJsonRPC(node16Url, "submitblock", [hexData, options])
    if "error" in response and response["error"] != None:
        raise ValueError(response["error"])
    else:
        return response["result"]
