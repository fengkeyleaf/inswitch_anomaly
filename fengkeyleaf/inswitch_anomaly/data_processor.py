# -*- coding: utf-8 -*-

import logging
import os
import sys
import unittest
from typing import List, Iterator, Tuple, Callable, Dict, Any

import pandas
from pandas import DataFrame
from sklearn.tree import DecisionTreeClassifier

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.logging import my_logging
import fengkeyleaf.inswitch_anomaly as fkl_inswitch
from fengkeyleaf.io import (
    my_files,
    my_writer
)
from fengkeyleaf.inswitch_anomaly import (
    mapper,
    mix_make_ups,
    pkt_processor,
    sketch_write,
    tree,
    _tree_evaluator,
    filter as fkl_filter
)
from fengkeyleaf.my_pandas import my_dataframe
from fengkeyleaf import annotations

# parent-directory..
#     | --> original_data..
#     | --> mixed_data..
#     | --> preprocessed_data..
#     | --> sketches..
#     | --> trees..
#     | --> header ( optional )


# fengkeyleaf.data_processor.DataProcessor( "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/data", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv", None, None, 20 ).process( True )
# fengkeyleaf.data_processor.DataProcessor( "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/data", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/NUSW-NB15_features_name.csv", None, None, 20 ).process( True )
# fengkeyleaf.data_processor.DataProcessor( "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/data", None, None, None, 20 ).process( True )
# TODO: Mix different group of data sets.
# TODO: Config parameter in the constructor.
class DataProcessor:
    """
    Class to do the all tree processing steps:
    1) pkt processing;
    2) sketch processing;
    3) tree processing;
    """
    def __init__(
            self, da: str, h: str,
            dm: str = None, D: List[ str ] = None,
            is_writing_eval: bool = False, ia_not_balancing: bool = False,
            fn: Callable = None, ll: int = logging.INFO
    ) -> None:
        """

        @param da: Directory to the original data sets.
        @param h: Path to features(headers)
        @param dm: Directory to the synthesised data sets. No synthesised pkts added when dm is None or dm == ""
        @param D: List of directories to the processed data sets to test trees.
        @param is_writing_eval: To tell if to write evaluating results to a file
        @param fn: Function to filter input pkts.
        @param ll: logging level
        """
        # Logging setting
        # https://docs.python.org/3/library/logging.html#logging-levels
        self.l: logging.Logger = my_logging.get_logger( ll )
        self.l.debug( "da: " + str( da ) )
        self.l.debug( "h: " + str( h ) )
        self.l.debug( "dm: " + str( dm ) )
        self.l.debug( "D: " + str( D ) )

        # I/O
        assert da is not None
        self.da: str = da
        self.files: List[ str ] = my_files.get_files_in_dir( da )

        # # Initialize the three processors.
        self._init_sub_processors( da, h, dm, D, is_writing_eval, ia_not_balancing, fn, ll )

        # Evaluating setting.
        self._init_eval( D, is_writing_eval, ll )

    def _init_sub_processors(
            self, da: str, h: str,
            dm: str = None, D: List[ str ] = None,
            is_writing_eval: bool = False, ia_not_balancing: bool = False,
            fn: Callable = None, ll: int = logging.INFO
    ):
        self.pkt_processor: pkt_processor.PktProcessor = pkt_processor.PktProcessor(
            h,
            mix_make_ups.Mixer(
                dm,
                0 if dm is None or dm == "" else self.__get_original_relative_time( da, h ),
                ll
            ),
            fn,
            ll
        )
        self.sketch_processor: sketch_write.SketchWriter = sketch_write.SketchWriter(
            da + pkt_processor.PktProcessor.FOLDER_NAME,
            da,
            ia_not_balancing,
            -1,
            True,
            True,
            ll
        )
        self.tree: tree.Tree = tree.Tree(
            da + sketch_write.SketchWriter.SKETCH_FOLDER_NAME,
            da,
            h,
            D,
            is_writing_eval,
            ll
        )

    def _init_eval(
            self, D: List[ str ] = None,
            is_writing_eval: bool = False, ll: int = logging.INFO
    ):
        # Record accuracies computed by one data set as training set and the other as validation set.
        self.acc_rec: my_dataframe.Builder = my_dataframe.Builder( ll = ll )
        # Record sketch limitation optimization data.
        self.lim_opti_rec: my_dataframe.Builder = my_dataframe.Builder( ll = ll )

        self.e = _tree_evaluator.Evaluator( self.l, D, self.acc_rec, self.lim_opti_rec )
        self._is_writing: bool = is_writing_eval
        self.e.set_is_writing( is_writing_eval )

    def process(
            self, pro_config: Dict[ str, Any ],
            eval_config: Dict[ str, Any ], is_only_preprocessing: bool = False,
    ) -> None:
        """
        Process data sets and train trees. Start from beginning.
        1) Re-format csv data sets.
        2) Generate sketch csv files.
        3) Train a tree with the sketch files.
        @param pro_config:
        @param eval_config:
        @param is_only_preprocessing: True, only generate processed data sets.
        """
        T: List[ Tuple[ List[ str ], str, DecisionTreeClassifier, float, Dict[ str, Any ] ] ] = []

        # Avoid to iterate newly-added directories.

        for f in self.files:
            # Only pre-process pkts.
            if is_only_preprocessing:
                self.pkt_processor.process( f )
                continue

            # Data processing and ML training.
            ( t, sc, v ) = self._process( pro_config, eval_config, f )

            # Add test info for each tree model.
            T.append(
                (
                    # Dataset validation folder.
                    v,
                    # File path to the tree.
                    fkl_inswitch.get_output_file_path(
                        f, tree.Tree.FOLDER_NAME,
                        tree.Tree.SIGNATURE
                    ),
                    # Decision tree model.
                    t,
                    # Accuracy verifying by the training dataset.
                    sc,
                    # evaluation configs.
                    eval_config
                )
            )

        # Evaluate trees
        self.l.info( "All processes are done, evaluating trees......" )
        for t in T:
            self.e.evaluate( *t )

        # Write accuracy results
        if self._is_writing:
            self.acc_rec.to_csv( self.da + _tree_evaluator.Evaluator.ACCU_SIGNATURE )
            self.acc_rec.reset()

    def _process(
            self, pro_config: Dict[ str, Any ],
            eval_config: Dict[ str, Any ], fp: str
    ) -> Tuple[ DecisionTreeClassifier, float, List[ str ] ]:
        # Folder structure from starting processing from pre-processing.
        # Before processing:
        # BoT-loT/
        #     - original dataset file 1
        #     - original dataset file 2
        #     - original dataset file ....
        #     - original dataset file n-1
        #     - original dataset file n
        # After processing:
        # BoT-loT/
        #     - balanced_reformatted/
        #     - re-formatted/
        #     - sketches/
        #     - trees/
        #     - original dataset file 1
        #     - original dataset file 2
        #     - original dataset file ....
        #     - original dataset file n-1
        #     - original dataset file n
        if pro_config.get( fkl_inswitch.IS_FROM_PRE_PROCESS_STR ):
            self.l.info( "Start processing from pre-processing." )
            # Pre-process, sketching and training.
            ( t, sc ) = self.tree.process(
                fp,
                self.sketch_processor.process(
                    self.pkt_processor.process( fp ),
                    fp
                )
            )
            return (
                t, sc,
                my_files.get_files_in_dir( my_writer.get_dir( fp ) + pkt_processor.PktProcessor.FOLDER_NAME )
            )
        # Folder structure from starting processing from sketching.
        # Before processing:
        # BoT-loT/
        #     - pro-processed dataset file 1
        #     - pro-processed dataset file 2
        #     - pro-processed dataset file ......
        #     - pro-processed dataset file n-1
        #     - pro-processed dataset file n
        # After processing:
        # BoT-loT/
        #     - balanced_reformatted/
        #     - sketches/
        #     - trees/
        #     - pro-processed dataset file 1
        #     - pro-processed dataset file 2
        #     - pro-processed dataset file ......
        #     - pro-processed dataset file n-1
        #     - pro-processed dataset file n
        elif pro_config.get( fkl_inswitch.IS_FROM_SKETCH_STR ):
            self.l.info( "Start processing from sketching." )
            # Sketching and training.
            ( t, sc ) = self.tree.process(
                fp,
                self.sketch_processor.process(
                    pandas.read_csv( fp ),
                    fp
                )
            )
            return ( t, sc, self.files )
        # Folder structure from starting processing from trees.
        # BoT-loT/re-formatted/ is the validation dataset folder given by the user.
        # Before processing:
        # BoT-loT/
        #     - sketches/
        #         - sketching dataset file 1
        #         - sketching dataset file 2
        #         - sketching dataset file ,,,,,,
        #         - sketching dataset file n-1
        #         - sketching dataset file n
        #     -re-formatted/
        #         - pro-processed dataset file 1
        #         - pro-processed dataset file 2
        #         - pro-processed dataset file ......
        #         - pro-processed dataset file n-1
        #         - pro-processed dataset file n
        # After processing:
        # BoT-loT/
        #     - sketches/
        #         - sketching dataset file 1
        #         - sketching dataset file 2
        #         - sketching dataset file ,,,,,,
        #         - sketching dataset file n-1
        #         - sketching dataset file n
        #         - trees/
        #     -re-formatted/
        #         - pro-processed dataset file 1
        #         - pro-processed dataset file 2
        #         - pro-processed dataset file ......
        #         - pro-processed dataset file n-1
        #         - pro-processed dataset file n
        elif pro_config.get( fkl_inswitch.IS_FROM_TREE_STR ):
            self.l.info( "Start processing from trees." )
            # Training.
            ( t, sc ) = self.tree.process(
                fp,
                pandas.read_csv( fp )
            )
            return (
                t, sc,
                DataProcessor._get_eval_folder( eval_config, fp )
            )

        assert False
        return ( None, 0, [] )

    @staticmethod
    def _get_eval_folder( eval_config: Dict[ str, Any ], fp: str ) -> List[ str ]:
        if eval_config.get( fkl_inswitch.EVAL_FOLDER_STR ) is None:
            return my_files.get_files_in_dir( my_writer.get_dir( fp ) + pkt_processor.PktProcessor.FOLDER_NAME )

        return my_files.get_files_in_dir( eval_config.get( fkl_inswitch.EVAL_FOLDER_STR ) )

    # TODO: csvparaser.TIMESTAMP_STR could vary.
    def __get_original_relative_time( self, da: str, h: str ) -> float:
        """
        Relative Time to align all pkts in the original data sets in timestamp order.
        @param da: Directory to the original data sets.
        @param h: Path to features(headers)
        @return:
        """
        rt: float = sys.maxsize
        for s, d, F in os.walk( da ):
            for f in F:
                n: List = pandas.read_csv( h ).columns.values.tolist() if h is not None else None
                df: DataFrame = mapper.Mapper.mapping( pandas.read_csv( os.path.join( s, f ), names = n ) )
                for ( i, _ ) in df.iterrows():
                    rt = min( rt, df.loc[ i, fkl_inswitch.TIMESTAMP_STR ] )

        self.l.debug( "rt: " + str( rt ) )
        return rt

    # da = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/data"
    # h = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv"

    # da = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/data"

    # da = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/data"
    # h = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/NUSW-NB15_features_name.csv"

    # D = [ "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/sketches" ]
    # D = [ "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/sketches", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/original/sketches", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/original/sketches" ]
    # D = [ "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/processed/sketches", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/processed/sketches", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/processed/sketches" ]

    # fengkeyleaf.data_processor.DataProcessor( da, h, None, D, 10 ).train_trees()
    # TODO: merge into process() in this class or train() in the Tree class.
    @annotations.deprecated
    def train_trees( self ) -> None:
        """
        Train tree with given csv files. The sketch format should be range and leabel.
        """
        self.l.info( "Start processing from generating trees." )

        for fp in my_files.get_files_in_dir( self.tree.d ):
            with open(
                    fp, encoding = my_files.UTF8,
                    errors = my_files.BACK_SLASH_REPLACE
            ) as f:
                assert my_writer.get_extension( fp ).lower() == my_files.CSV_EXTENSION, fp
                self.tree.process(
                    self.tree.pd + "/" + my_writer.get_filename( fp ),
                    pandas.read_csv( f )
                )

        if self._is_writing:
            self.tree.acc_rec.to_csv( self.da + _tree_evaluator.Evaluator.ACCU_SIGNATURE )
            self.tree.acc_rec.reset()


class _Tester( unittest.TestCase ):
    is_writing: bool = True

    h1: str = "D:/networking/datasets/anomoaly_detection/data/BoT-IoT/UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv"
    da1: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/inswitch_anomaly/fengkeyleaf/inswitch_anomaly/_data_pro_test/tests"

    # @unittest.skip
    def test_bot_lot( self ):
        DataProcessor(
            _Tester.da1, _Tester.h1, None, None, _Tester.is_writing, fkl_filter.ipv4_filter, logging.DEBUG
        ).process()


if __name__ == '__main__':
    unittest.main()
