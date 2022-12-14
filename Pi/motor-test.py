#!/usr/bin/env python 3
from Arduino import Arduino
import time

sent = False
reset = False
port = 0
angle = 0
motor = 0
received = ""

if (__name__ == '__main__'):
    while (not reset):
        try:
            arduino = Arduino(port, 9600, 10)
            
            if (arduino.IsConnected()):
                while (True):
                    try:
                        received = arduino.GetMessage(60)

                        if ("Finished" in received):
                            print(received + "\n")

                            if (not reset):
                                angle += 10

                                if (angle > 180):
                                    angle = 0
                                    motor += 1

                                    if (motor == 4):
                                        angle = 0
                                        motor = 0
                                        reset = True
                            else:
                                motor += 1

                                if (motor == 4):
                                    break

                            sent = False
                            received = ""
                        elif ("Arduino:" in received):
                            print(received)
                            received = ""
                        elif ("Error:" in received):
                            print(received)
                            received = ""
                            break
                        else:
                            if (arduino.IsConnected()):
                                print("Still connected. Waiting for response...")
                                time.sleep(1)
                            else:
                                arduino.Reconnect()

                        if (not sent):
                            if (reset):
                                sent = arduino.TurnMotor(motor, 0)
                            else:
                                sent = arduino.TurnMotor(motor, angle)
                    except OSError as error:
                        print(error)
                        break
        except OSError:
            print("Port " + str(port) + " not found...")
            port += 1

            if (port > 10):
                break
            else:
                print("Trying port " + str(port) + "...")
