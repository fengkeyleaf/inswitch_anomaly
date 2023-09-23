# -*- coding: utf-8 -*-

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


# https://machinelearningmastery.com/develop-your-first-neural-network-with-pytorch-step-by-step/
class Neural:
    def __init__( self ):
        self.X = None
        self.y = None
        self.model = None
        self.loss_fn = None
        self.opti = None

    def load_data( self, f: str ):
        # load the dataset, split into input (X) and output (y) variables
        dataset = np.loadtxt( f, delimiter = ',' )
        X = dataset[ :, 0:8 ]
        y = dataset[ :, 8 ]

        self.X = torch.tensor( X, dtype = torch.float32 )
        self.y = torch.tensor( y, dtype = torch.float32 ).reshape( -1, 1 )

    def build_model( self ):
        self.model = nn.Sequential(
            nn.Linear( 8, 12 ),
            nn.ReLU(),
            nn.Linear( 12, 8 ),
            nn.ReLU(),
            nn.Linear( 8, 1 ),
            nn.Sigmoid()
        )

        print( self.model )
        print()

        self.loss_fn = nn.BCELoss()  # binary cross entropy
        # print( self.model.parameters() )
        # https://pytorch.org/docs/stable/generated/torch.optim.Adam.html#torch.optim.Adam
        # self.opti = optim.Adam( self.model.parameters(), lr = 0.001 )
        # https://pytorch.org/docs/stable/generated/torch.optim.SGD.html#torch.optim.SGD
        self.opti = optim.SGD( self.model.parameters(), lr = 0.001 )

    def training( self ):
        n_epochs = 1
        batch_size = 10

        # https://pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.parameters
        for epoch in range( n_epochs ):
            loss = None

            for i in range( 0, 10, batch_size ):
                self.opti.zero_grad()

                Xbatch = self.X[ i:i + batch_size ]
                y_pred = self.model( Xbatch )
                y_batch = self.y[ i:i + batch_size ]
                loss = self.loss_fn( y_pred, y_batch )
                loss.backward()

                self.opti.step()
                # with torch.no_grad():
                #     for p in self.model.parameters():
                #         print( p )
                #         print( "p.grad" )
                #         print( p.grad )
                #         # new_val = update_function( p, p.grad, loss, other_params )
                #         # p.copy_( new_val )
                #         pass

            print()
            print( f'Finished epoch {epoch}, latest loss {loss}' )


    def evaluate( self ):
        # compute accuracy (no_grad is optional)
        with torch.no_grad():
            y_pred = self.model( self.X )

        accuracy = ( y_pred.round() == self.y ).float().mean()
        print( f"Accuracy {accuracy}" )


if __name__ == '__main__':
    n = Neural()
    n.load_data( "./pima-indians-diabetes.data.csv" )
    n.build_model()
    n.training()
    n.evaluate()