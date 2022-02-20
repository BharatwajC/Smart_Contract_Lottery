# note when i am developing test each and every case
from brownie import network,config
from scripts.helpful_scripts import LinkToken,LOCAL_BLOCKCHAIN_ENVIRONMENT,get_account,get_contract,fund_with_link
from scripts.deploy import deploy_lottery
import pytest,time

def test_can_pick_winner():

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})

    #In unit we pretended chainlink by dummy chainlink request

    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0

    #brownie -s will print out whatever brownie is going to printout verbose

    
    