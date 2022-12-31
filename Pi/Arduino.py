#!/usr/bin/env python 3
import serial, time

class Arduino:
    def __init__(self, port: int, baudrate: int, connectAttemptsFail: int):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.connectAttempts = 0
        self.connectAttemptsFail = connectAttemptsFail
        self.Connect()

    def Connect(self):
        self.connectAttempts += 1
        self.serial = serial.Serial("/dev/ttyACM" + str(self.port), self.baudrate, timeout = 1)
        time.sleep(1) #wait for serial to open

        if (self.IsConnected()):
            self.connectAttempts = 0
            print("Connected to Arduino on port {}".format(self.port))
            return True
        elif (self.connectAttempts <= self.connectAttemptsFail):
            print("Device not responding. Reconnecting...")
            self.Reconnect()
        else:
            print("Failed to reconnect!")
            return False

    def IsConnected(self):
        return self.serial.isOpen()

    def Reconnect(self):
        self.serial.close()
        print("Closed port {}.".format(self.port))
        time.sleep(1)
        return self.Connect()

    def GetMessage(self, timeout: int):
        waiting = 0

        while (True):
            try:
                if (timeout > 0 and waiting >= timeout):
                    return None
                elif (self.serial.inWaiting() > 0):
                    return self.serial.readline().decode('utf-8').rstrip()
                else:
                    waiting += 1
            except Exception as error:
                return error

    def SendMessage(self, message: str):
        while (True):
            try:
                self.serial.write(message.rstrip().encode('utf-8'))
                print("Pi: " + message.rstrip())
                return True
            except Exception as error:
                if (not self.IsConnected()):
                    print("Lost connection to Arduino. Reconnecting...")
                    self.Reconnect()
                else:
                    print(error)
                    return False

    def TurnMotor(self, motor: int, angle: int):
        try:
            message = "<rotate:motor"

            if (motor < 0 or motor > 15):
                raise Exception("Motor index must be 0-15")
            elif (motor < 10):
                message += "0" + str(motor) + ";"
            else:
                message += str(motor) + ";"
            
            if (angle < 0 or angle > 359):
                raise ValueError("Angle must be 0-359")
            else:
                message += str(angle) + ">"

            return self.SendMessage(message)
        except Exception as error:
            print(error.args)