from scripts.helpful_scripts import fund_with_link, get_account, get_contract
from brownie import Lottery, accounts,config,network
import time

 
def deploy_lottery():
    account = get_account()      #get_account(id = "freecodecamp-account")
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,                     #price feed address
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify",False)        # check verify key if aint present then False
         
        
    )        # Its going to get eth usd

    print("Deployed lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account}) 
    starting_tx.wait(1)
    print("The lottery is started")   


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 1000000      # in case of some difference
    tx = lottery.enter({"from":account, "value":value})
    tx.wait(1)
    print("you entered the lottery!")

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # Now our endLottery function calls this requestRandomness function
    # we need to have some amount to fund this requestToken contract

    #fund the contract  with LINK
    #then end the lottery 

    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)

    #from our end this all we need to do 
    # now chainlink node is gonna call fullfillrandomness so it takes time so

    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new winner!!")

    # Now there is no chainlink node responding if you try running right now
    # o/p: winner will 0x00000000000000000000000000000000



def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
