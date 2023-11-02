from fengkeyleaf import evaulator

class _Test:
    def test1( self ):
        D = {
                 "result": {
                    "1": "",
                    "2": "",
                    "3": "",
                    "4": "",
                    "5": ""
                }
            }
        evaulator.Evaluator().evaluate( 
            "/home/p4/data/balanced_reformatted/UNSW_2018_IoT_Botnet_Dataset_1_balanced_reformatted.csv",
             D
        )
        print( D )

if __name__ == '__main__':
    _Test().test1()
