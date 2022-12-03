#!/usr/bin/env python 3
import debugpy
debugpy.listen(5678)

import serial, time

sent = False
reset = False
port = 0
angle = 0
motor = 0
except_count = 0
waiting = 0
send = ""
received = ""

if (__name__ == '__main__'):
    while reset == False:
        try:
            arduino = serial.Serial("/dev/ttyACM" + str(port), 9600, timeout=1)
            time.sleep(1) #wait for serial to open

            if arduino.isOpen():
                print("{} connected!".format(arduino.port))
                while True:
                    try:
                        while (arduino.inWaiting == 0): pass
                        if arduino.inWaiting() > 0:
                            received = arduino.readline().decode('utf-8').rstrip()

                            if ("Finished" in received):
                                print(received + "\n")

                                if (reset == False):
                                    angle += 10

                                    if (angle > 180):
                                        angle = 0
                                        motor += 1

                                        if (motor == 6):
                                            angle = 0
                                            motor = 0
                                            reset = True
                                else:
                                    motor += 1

                                    if (motor == 6):
                                        break

                                sent = False
                                received = ""

                            elif ("Arduino:" in received):
                                print(received)
                                received = ""

                            if (sent == False):
                                if (reset == True):
                                    send = "<rotate:motor0" + str(motor) + ";0>"
                                    arduino.write(send.encode('utf-8'))
                                    print("Resetting motor " + str(motor))
                                else:
                                    send = "<rotate:motor0" + str(motor) + ";" + str(angle) + ">"
                                    arduino.write(send.encode('utf-8'))
                                    print("Sent: " + send.rstrip())

                                sent = True
                        elif (sent == True):
                            time.sleep(0.01)
                            waiting += 1
                            if (waiting == 1000):
                               print("Re-sending...")
                               arduino.flush()
                               send = "<rotate:motor0" + str(motor) + ";" + str(angle) + ">"
                               arduino.write(send.encode('utf-8'))
                               print("Sent: " + send.rstrip())
                               time.sleep(1)
                               waiting = 0
                    except serial.serialutil.SerialException:
                        print("No response from device.")

                        if (arduino.isOpen()):
                            print("Still connected. Waiting for response...")
                            time.sleep(1)
                        else:
                            print("Device not responding. Re-connecting...")
                            arduino.close()
                            print("Closed port...")
                            time.sleep(1)
                            arduino = serial.Serial("/dev/ttyACM" + str(port), 9600, timeout=1)
                            print("Re-opened port...")

                            if (arduino.isOpen()):
                                print("{} connected!".format(arduino.port))
                                except_count = 0
                            else:
                                except_count += 1
                                if (except_count == 5):
                                    print("Failed to re-connect.")
                                    break
                    except OSError:
                        print("Device not ready...")
                        arduino.close()
                        print("Closed port...")
                        port = 0
                        time.sleep(1)
                        arduino = serial.Serial("/dev/ttyACM" + str(port), 9600, timeout=1)
                        print("Re-opened port...")

                        if (arduino.isOpen()):
                            print("{} connected!".format(arduino.port))
                            except_count = 0
                        else:
                            except_count += 1
                            if (except_count == 5):
                                print("Failed to re-connect.")
                                break
        except OSError:
            print("Port " + str(port) + " not found...")
            port += 1

            if (port > 10):
                break
            else:
                print("Trying port " + str(port) + "...")
