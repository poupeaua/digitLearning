#!/usr/bin/env python3

"""
    File used to manage the arguments given by the user in the main function.
    As they are a lot of parameters possible it is better to decompose the code.
    Moreover, it will be easier to add and/or modify (the behaviour of) some
    parameters by creating a class to manage them.
"""

import sys
import numpy as np
from externalFunc import *
from squishingFunc import *

# unchanging values
SIZE_INPUT = 784 # 28 * 28 = 784 pixels
SIZE_OUTPUT = 10 # number of numbers between 0 and 9
SIZE_TRAINING = 60000
SIZE_TESTING = 10000
# you can choose the value for the following global constant
REPETITION_LIMIT = 1000
POSSIBLE_ARGS = ["-bs", "-sf", "-gdf", "-r", "-ls", "-ts"]
POSSIBLE_SQUISHING_FUNC = ["Sigmoid", "ReEU", "ReLU"]
POSSIBLE_GRAD_DESC_FACT_FUNC = ["NegPower{anyPosFloat}",
    "Constant{anyPosFloat}"]

class ArgsManager:
    """
        Class used to manage arguments.
    """

    def __init__(self, list_args):
        """
            Initialize a object ArgsManager.
        """
        # set the parameters to their default mode so that even when the user
        # do not ask for a special parameters it works all the same.
        # BEWARE : the neural network argument is required (not optional)
        self.neural_network = None
        self.batches_size = 1
        self.squishing_funcs = None
        self.grad_desc_factor = (NegPower, 1.3)
        self.repeat = 0
        self.learning_size = 60000
        self.testing_size = 10000

        # analyse the given arguments and set them in the class
        self.analyseArgs(list_args)

        # in case there was no choice for the squishing funcs in the arguments
        if self.squishing_funcs == None:
            nb_layer = len(self.neural_network)
            self.squishing_funcs = [(Sigmoid, InvSigmoid, DerSigmoid)] \
                    * (nb_layer-1)



    def analyseArgs(self, list_args):
        """
            Method used to analyse the inputs of the main function.
            Used to make sure that args are correct but also to assign them.
        """
        # ex ./main.py network/network1.txt => len(sys.argv) == 2
        nb_arg = len(list_args)

        # ------------- required parameter = neural network document ----------
        if nb_arg <= 1:
            # need at least ./main.py networks/{}.txt
            print("ERROR : There is no argument.")
            sys.exit(1)
        else:
            self.checkNeuralNetworkArg(list_args[1])

        # ---------------------- optional parameters --------------------------
        i = 2
        while i < nb_arg:
            curr_arg = sys.argv[i]
            if curr_arg in POSSIBLE_ARGS:
                try:
                    arg = sys.argv[i+1]
                except:
                    print("ERROR : There is no argument after", curr_arg, ".")
                    sys.exit(1)
            else:
                print("ERROR : The pre-parameter", curr_arg, "doesn't exist.")
                print("The existing ones are", POSSIBLE_ARGS)
                sys.exit(1)
            if curr_arg == "-bs":
                # Batches Size
                self.checkBatchesSizeArg(arg)
            elif curr_arg == "-sf":
                # Squishing Functions
                self.checkSquishingFunctionsArg(arg)
            elif curr_arg == "-gdf":
                # Gradient Descent Factor
                self.checkGradientDescentFactorArg(arg)
            elif curr_arg == "-r":
                # Repeat number
                self.checkRepeatArg(arg)
            elif curr_arg == "-ls":
                # Learning Size
                self.checkLearningSizeArg(arg)
            elif curr_arg == "-ts":
                # Testing size
                self.checkTestingSizeArg(arg)
            i += 2



    def checkNeuralNetworkArg(self, document):
        """
            Check the required argument neural network document.
        """
        try:
            document = open(document, "r")
        except IOError as details:
            print("ERROR : Cannot open", document, ".")
            print("Information about the error :", details)
            sys.exit(1)
        else:
            first_line = document.readline(1)
            if not first_line.isdigit() or int(first_line) <= 0:
                print("ERROR : The number of middle layer is equal to",
                    first_line, ".")
                print("It has to be a strictly positive integer.")
                sys.exit(1)
            else:
                len_layers = np.zeros(int(first_line) + 2)
            len_layers[0] = SIZE_INPUT
            index = 1
            for line in document:
                string = line[:-1]
                if string != "":
                    if not string.isdigit() or int(string) <= 0:
                        print("ERROR : The layer n°", index,
                            "is equal to", int(string), ".")
                        print("A layer must be a strictly positive integer.")
                        sys.exit(1)
                    else:
                        len_layers[index] = int(string)
                        index += 1
            len_layers[len(len_layers)-1] = SIZE_OUTPUT
            # set the attribute neural network to the len_layer
            self.neural_network = len_layers



    def checkBatchesSizeArg(self, arg):
        """
            Check the optional argument batch size.
        """
        if not arg.isdigit():
            print("ERROR : The batch size argument", arg, "is not a integer.")
            sys.exit(1)
        elif int(arg) <= 0:
            print("ERROR : The batch size argument", arg, "is not a strictly"
                " povitive integer.")
            sys.exit(1)
        elif int(arg) > SIZE_TRAINING:
            print("ERROR : The batch size argument", arg, "is greater than the"
                " size of the training data set equal to", SIZE_TRAINING,".")
            sys.exit(1)
        else:
            self.batches_size = int(arg)



    def checkSquishingFunctionsArg(self, arg):
        """
            Check the optional argument squishing functions.
        """
        # list of function associated to each layer
        nb_layer = len(self.neural_network)
        if arg == "Sigmoid":
            self.squishing_funcs = [(Sigmoid, InvSigmoid, DerSigmoid)] \
                * (nb_layer-1)
        elif arg == "ReEU":
            self.squishing_funcs = [(ReEU, InvReEU, DerReEU)] * (nb_layer-1)
        elif arg == "ReLU":
            self.squishing_funcs = [(ReLU, InvReLU, DerReLU)] * (nb_layer-2)
            # BEWARE : end with a function that squishes the number in [0, 1]
            self.squishing_funcs.append((ReEU, InvReEU, DerReEU))
        else:
            print("The given squishing function", arg, "doesn't correspond to"
                " any possible function :", POSSIBLE_SQUISHING_FUNC)
            sys.exit(1)



    def displayErrorGrad(self, str_name_func, str_value, function):
        """
            Used to simplify the code in the checkGradientDescentFactorArg
            function.
        """
        if not isfloat(str_value):
            print("ERROR : The value in the optional argument gradient "
                "descent factor for the", str_name_func, "function is",
                str_value,". It has to to be a float.")
            sys.exit(1)
        elif float(str_value) <= 0:
            print("ERROR : The value in the optional argument gradient "
                "descent factor for the", str_name_func, "function is",
                str_value, ". It has to to be a stricly positive float")
            sys.exit(1)
        else:
            self.grad_desc_factor = (function, float(str_value))



    def checkGradientDescentFactorArg(self, arg):
        """
            Check the optional argument gradient descent factor.
        """
        if arg[0:8] == "Constant":
            self.displayErrorGrad("Constant", arg[8:], Constant)
        elif arg[0:8] == "NegPower":
            self.displayErrorGrad("NegPower", arg[8:], NegPower)
        else:
            print("The given squishing function", arg, "doesn't correspond to"
                " any possible function :", POSSIBLE_GRAD_DESC_FACT_FUNC)
            sys.exit(1)



    def checkRepeatArg(self, arg):
        """
            Check the optional argument repeat.
        """
        if not arg.isdigit():
            print("ERROR : The repeat argument", arg, "is not a integer.")
            sys.exit(1)
        elif int(arg) <= 0:
            print("ERROR : The repeat argument", arg, "is not a strictly"
                " povitive integer.")
            sys.exit(1)
        elif int(arg) > REPETITION_LIMIT:
            print("ERROR : The repeat argument", arg, "is greater than the"
                " limit equal to", REPETITION_LIMIT, ".")
            sys.exit(1)
        else:
            self.repeat = int(arg)



    def checkLearningSizeArg(self, arg):
        """
            Check the optional argument learning size.
        """
        if not arg.isdigit():
            print("ERROR : The learning size argument", arg, "is not a integer."
                "")
            sys.exit(1)
        elif int(arg) <= 0:
            print("ERROR : The learning size argument", arg, "is not a strictly"
                " povitive integer.")
            sys.exit(1)
        elif int(arg) > SIZE_TRAINING:
            print("ERROR : The learning size argument", arg, "is greater than "
                "the size of the training data set equal to", SIZE_TRAINING,".")
            sys.exit(1)
        else:
            self.learning_size = int(arg)


    def checkTestingSizeArg(self, arg):
        """
            Check the optional argument testing size.
        """
        if not arg.isdigit():
            print("ERROR : The testing size argument", arg, "is not a integer."
                "")
            sys.exit(1)
        elif int(arg) <= 0:
            print("ERROR : The testing size argument", arg, "is not a strictly"
                " povitive integer.")
            sys.exit(1)
        elif int(arg) > SIZE_TESTING:
            print("ERROR : The testing size argument", arg, "is greater than"
                " the size of the training data set equal to", SIZE_TESTING,".")
            sys.exit(1)
        else:
            self.testing_size = int(arg)


    def display(self):
        """
            Method used to display all the argument given by the user.
            Mostly useful to debug and see whether or not the argument argument
            well identify.
        """
        print("The form of the Neural Network is ", self.neural_network)
        print("The size of a batch is", self.batches_size)
        print("The squishing functions for the first layer is",
            self.squishing_funcs[0])
        print("The squishing functions for the second to last layer is",
            self.squishing_funcs[len(self.neural_network)-2])
        print("The gradient descent factor function is",
            self.grad_desc_factor[0])
        print("The gradient descent factor value is",
            self.grad_desc_factor[1])
        print("The number of repetition in the training phase is", self.repeat)
        print("The size of the training data set used is", self.learning_size)
        print("The size of the testing data set used is", self.testing_size)
