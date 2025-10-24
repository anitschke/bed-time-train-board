from train_predictor import TrainPredictor
from datetime import datetime
import json
import os
import unittest


def mock_now_func(timeOfNow):
    return lambda : datetime.fromisoformat(timeOfNow).replace(tzinfo=None)

def load_test_schedule_json(file):
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_file_directory, 'testdata', 'schedules', file)
    with open(file_path, 'r') as file:
        return json.load(file)

class Test_analyze_data(unittest.TestCase):
    # xxx doc
    def test_simple(self):
        # Simple test with best case where we have both the schedule data and
        # prediction data for a train.
        mock_now = mock_now_func('2025-10-22T23:04:00-04:00')
        train_predictor = TrainPredictor(None, datetime, mock_now)

        data = load_test_schedule_json('simple.json')
        
        count = 1
        result = train_predictor._analyze_data(count, data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].direction, 0)
        self.assertEqual(result[0].time, "2025-10-22T23:04:53-04:00")

    def test_simple_sparse(self):
        # This is the same as test_simple but uses a sparse dataset. The MBTA
        # allows requesting a more minimal dataset. So this is the smallest
        # amount of data that I think we can get away with requesting at the
        # moment.
        mock_now = mock_now_func('2025-10-22T23:04:00-04:00')
        train_predictor = TrainPredictor(None, datetime, mock_now)

        data = load_test_schedule_json('simple_sparse.json')
        
        count = 1
        result = train_predictor._analyze_data(count, data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].direction, 0)
        self.assertEqual(result[0].time, "2025-10-22T23:04:53-04:00")
    
    def test_no_prediction_data(self):
        # When there is no prediction data in the JSON from the MBTA we should
        # fallback to using the schedule time
        mock_now = mock_now_func('2025-10-22T23:04:00-04:00')
        train_predictor = TrainPredictor(None, datetime, mock_now)

        data = load_test_schedule_json('simple_no_prediction.json')
        
        count = 1
        result = train_predictor._analyze_data(count, data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].direction, 0)
        self.assertEqual(result[0].time, "2025-10-22T23:06:00-04:00")

    def test_multiple_data_request_one_result(self):
        # There are multiple possible results that could be returned but only
        # one is requested
        mock_now = mock_now_func('2025-10-22T04:06:00-04:00')
        train_predictor = TrainPredictor(None, datetime, mock_now)

        data = load_test_schedule_json('multiple_results.json')
        
        count = 1
        result = train_predictor._analyze_data(count, data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].direction, 1)
        self.assertEqual(result[0].time, "2025-10-22T05:06:00-04:00")

    def test_multiple_data_request_more_results(self):
        # There are two possible results that could be returned but three are
        # requested
        mock_now = mock_now_func('2025-10-22T04:06:00-04:00')
        train_predictor = TrainPredictor(None, datetime, mock_now)

        data = load_test_schedule_json('multiple_results.json')
        
        count = 3
        result = train_predictor._analyze_data(count, data)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].direction, 1)
        self.assertEqual(result[0].time, "2025-10-22T05:06:00-04:00")
        self.assertEqual(result[1].direction, 0)
        self.assertEqual(result[1].time, "2025-10-22T06:06:00-04:00")
        self.assertEqual(result[2], None)

    def old_results_filtered(self):
        # There are multiple possible results that could be returned but only
        # one is requested
        mock_now = mock_now_func('2025-10-22T05:06:20-04:00')
        train_predictor = TrainPredictor(None, datetime, mock_now, filterResultsAfterSeconds=10)

        data = load_test_schedule_json('multiple_results.json')
        
        count = 3
        result = train_predictor._analyze_data(count, data)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].direction, 0)
        self.assertEqual(result[0].time, "2025-10-22T06:06:00-04:00")
        self.assertEqual(result[1], None)
        self.assertEqual(result[2], None)


    def test_data_array_empty(self):
        mock_now = mock_now_func('2025-10-22T23:04:00-04:00')
        train_predictor = TrainPredictor(None, datetime, mock_now)

        data = load_test_schedule_json('data_array_empty.json')
        
        count = 1
        result = train_predictor._analyze_data(count, data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], None)

    def test_no_data_property(self):
        mock_now = mock_now_func('2025-10-22T23:04:00-04:00')
        train_predictor = TrainPredictor(None, datetime, mock_now)

        data = load_test_schedule_json('no_data_property.json')
        
        count = 1
        result = train_predictor._analyze_data(count, data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], None)



if __name__ == '__main__':
    unittest.main()