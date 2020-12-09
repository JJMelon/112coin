# Project Description

My project is called 112Coin and it will be a simple implementation of a Proof of Stake (PoS) consensus-based blockchain cryptocurrency. 
The user will be assigned a randomly generated keypair when they first load the app, and can use this to send transaction messages to other 
local computer users which are controlled by the app’s AI algorithm. The user can also view their transactions and the blocks on the chain 
and they are also able to stake coins so that they may earn the reward from validating and confirming or ‘minting’ a block full of transactions. 

The AI controlling other local computer users will make some users stake coins and act as validators, and make all non-human users send random 
transactions to other users at random intervals, simulating an active cryptocurrency market. Some transactions may have invalid signatures or 
involve insufficient balances and the validating algorithm will exclude these. There will even be occasional times that minters 'cheat' the network
by creating fake transactions, and they will we accordingly punished by losing their stake.  

## Note: ## The Currency is Called 112Coin, and 0.01 112Coin = 1 kos

# How to run the project.

Simply unzip the directory and run main.py. A chain.db file will be created on the first run and 
stores all users and block data.

# Libraries that need to be installed

- For installing ecdsa, the cryptography module use:

"pip install ecdsa"

# A list of any shortcut commands that exist.

'm' -- mint a block from the current txs pool

'g' -- toggle on and off the AI transaction generation
