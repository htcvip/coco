#!python
# -*- coding: utf-8 -*-

import pyautogui
import time, traceback
import htc_utility
import htc_constant

# should sleep some seconds to prepare page

start_sleep = 10
pyautogui.PAUSE = 0.3
pyautogui.FAILSAFE = False
max_data_error_diff = 1000000
check_data_change_interval = 300000
last_count_down = -1
htc_utility.write_log("sleep %d seconds to capture" % (start_sleep))
time.sleep(start_sleep)


while True:
    (valid, count_down, master, slave) = htc_utility.do_cycle()
    if not valid:
        if count_down <= 0 and last_count_down <= 0:
            res = list(pyautogui.locateAllOnScreen(htc_constant.EnterPng))
            if len(res) > 0:
                htc_utility.write_log("has enter, click to enter game, and mouse move to origin")
                pyautogui.click(htc_constant.EnterClickPos["x"], htc_constant.EnterClickPos["y"])
                pyautogui.moveTo(10, 500)
        last_count_down = count_down
        continue


    htc_utility.write_log("count down=%d satisfy, master=%f, slave=%f, come to comput buy option" % (count_down, master, slave))
    if htc_constant.screenWidth == 2048:
        buy_option = htc_constant.strategy_full(master, slave)
    else:
        buy_option = htc_constant.strategy_positive(master, slave)

    if buy_option == 'master':
        pyautogui.click(htc_constant.MasterClickPos["x"], htc_constant.MasterClickPos["y"])
        pyautogui.click(htc_constant.ConfirmClickPos["x"], htc_constant.ConfirmClickPos["y"])
        htc_utility.write_log("set master, amount bet=%f %f, and sleep %d" % (
        master, slave, htc_constant.CountDownPos["result"]))
    elif buy_option == 'slave':
        pyautogui.click(htc_constant.SlaveClickPos["x"], htc_constant.SlaveClickPos["y"])
        pyautogui.click(htc_constant.ConfirmClickPos["x"], htc_constant.ConfirmClickPos["y"])
        htc_utility.write_log("set slave, amount bet=%f %f, and sleep %d" % (master, slave, htc_constant.CountDownPos["result"]))
    else:
        htc_utility.write_log("amount bet=%f %f, not satisfy condition, ignore" % (master, slave))

    time.sleep(5)
    (final_master, final_slave) = htc_utility.get_final_master_slave()
    htc_utility.write_log("get final master=%f, slave=%s" % (final_master, final_slave))
    # get final master, slave

    time.sleep(3)
    account_value = -1
    while True:
        tt = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        source = "./imgs/whole_%s.png" % (tt)
        im = pyautogui.screenshot(source)
        count_down = htc_utility.deal_count_down(source)
        if count_down <= 0:
            htc_utility.write_log("count_down=%d may be 结算中, continue to wait"%(count_down))
            htc_utility.clear(source, htc_constant.CountDownPos["pngName"], "", "")
            res = list(pyautogui.locateAllOnScreen(htc_constant.EnterPng))
            if len(res) > 0:
                htc_utility.write_log("has enter, click to enter game, and mouse move to origin")
                pyautogui.click(htc_constant.EnterClickPos["x"], htc_constant.EnterClickPos["y"])
                pyautogui.moveTo(10, 500)
            continue

        htc_utility.write_log("next count down=%d, come to get account value, and insert into sql" % (count_down))
        account_value = htc_utility.deal_account_value(source)
        htc_utility.clear_single_png(htc_constant.CountDownPos["pngName"])
        if account_value >= 0:
            htc_utility.write_log("get account value=%d" % (account_value))
        else:
            htc_utility.write_log("get account failed, value=%d" % (account_value))
            account_value = 0
        # snap, get count_down, if count_down > 0; get account_value;break
        # get account value
        break

    req = {
        "buy_option": buy_option,
        "set_master": master,
        "set_slave": slave,
        "actual_master": final_master,
        "actual_slave": final_slave,
        "last_account_value": htc_constant.last_account_value,
        "account_value": account_value
    }
    (code, id) = htc_utility.insert_coco_item(req)
    if code != htc_utility.error_success:
        htc_utility.write_log("insert info mysql failed")
    else:
        htc_utility.write_log("insert into mysql success, id=%d" % (id))
    htc_constant.last_account_value = account_value





