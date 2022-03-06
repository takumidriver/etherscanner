

import asyncio, sys

from pythclient.pythaccounts import PythPriceAccount, PythPriceStatus
from pythclient.solana import SolanaClient, SolanaPublicKey, SOLANA_DEVNET_HTTP_ENDPOINT, SOLANA_DEVNET_WS_ENDPOINT


async def get_price():
    # devnet DOGE/USD price account key (available on pyth.network website)
    account_key = SolanaPublicKey("HovQMDrbAgAYPCmHVSrezcSmkMtXSSUsLDFANExrZh2J")
    solana_client = SolanaClient(endpoint=SOLANA_DEVNET_HTTP_ENDPOINT, ws_endpoint=SOLANA_DEVNET_WS_ENDPOINT)
    price: PythPriceAccount = PythPriceAccount(account_key, solana_client)

    await price.update()

    price_status = price.aggregate_price_status
    if price_status == PythPriceStatus.TRADING:
        # Sample output: "DOGE/USD is 0.141455 ± 7.4e-05"
        return {
            'price': price.aggregate_price,
            'confidence': price.aggregate_price_confidence_interval
        }
    else:
        return (0, 0)

    await solana_client.close()
