import websocket
import time
import threading
import json
import pprint

# server side code scheme
# 't': # type
# {
#     't': code,
#     'd': data
# }
# type list -send
# 'gd':  # game data
# 'atw':  # add to waiting list
# 'qw':  # quit waiting
# 'sc':  # solicit
# 'gs':  # get solicitors
# 'ac':  # accept solicit
#
#

def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


class ConnectionManager:
    pass

class OnlineManager:
    def __init__(self, user_id, game_instance, multiplayer_instance):
        # websocket.enableTrace(True)
        self.status = 'hello'
        self.game_instance = game_instance
        self.multiplayer_instance = multiplayer_instance
        self.user_id = user_id
        self.opponent = None
        self.ws = websocket.WebSocketApp(
            f"ws://127.0.0.1:8000/ws",
            on_open=lambda ws: self.on_open(ws),
            on_message=lambda ws, msg: self.on_message(ws, msg),
            on_error=on_error,
            on_close=on_close,
        )
        self.is_running = False
        self.thread = threading.Thread(target=self.send_current_gd_thread, daemon=True)
        self.is_sending_current = False
        self.is_sending_current_json = False

    def on_open(self, ws):
        ws.send(self.user_id)

    def on_message(self, ws, message):
        try:
            raw_data = json.loads(message)  # 최상위 키가 하나 존재하는 딕셔너리 데이터
            print(raw_data)  # 디버그
        except json.JSONDecodeError:
            raw_data = None
            print('message not in json format')

        if raw_data is not None:
            self.parse_data(raw_data)

    def parse_data(self, raw_data):
        # type list -receive
        # 'go': 'opponent_game_over',
        # 'mc': 'match_complete',
        # 'gs': 'game_start',
        # 'sa': 'solicit_accepted',
        # 'sr': 'solicit_rejected',
        # 'lo': 'loser',
        # 'wi': 'winner'
        try:
            t = raw_data['t']
            d = raw_data['d']
        except KeyError:
            t = None
            d = None
            print(f'Cannot parse data:\n{raw_data=}')

        if self.status == 'in_game':
            pass
        else:
            if t == 'gd':  # 게임 데이터일때
                pass  # 멀티플레이어 인스턴스에 화면 업데이트
            elif t == 'sa':  # 대결 제안 수락됨
                pass  # 3초 후에 진행 안내
            elif t == 'sr':  # 대결 제안 거절됨
                pass  # 다시 대기 상태
            elif t == 'lo':  # 패배
                pass  # 패배 화면
            elif t == 'wi':  # 승리
                pass  # 패배 화면
            elif t == 'gs':  # 게임 시작됨
                pass  # 게임 시작
            elif t == 'go':  # 상대 게임 오버
                pass  # 상대 화면에 게임 오버 띄우기
            elif t == 'mc':  # 매치 끝남
                pass  #

    def run_forever(self):
        self.is_running = True
        self.ws.run_forever()

    def close(self):
        self.is_running = False
        self.ws.close()

    def send_json_req(self, req):
        self.ws.send(json.dumps(req))

    def waiting_list_add(self):
        req = {
            't': 'wla',
            'd': None
        }
        self.send_json_req(req)

    def waiting_list_remove(self):
        req = {
            't': 'wlr',
            'd': None
        }
        self.send_json_req(req)

    def solicit(self, waiter_id: str):
        req = {
            't': 'sc',
            'd': waiter_id
        }
        self.send_json_req(req)

    def solicit_cancel(self):
        pass

    def solicitee_accept(self, solicitor_id: str):
        req = {
            't': 'sa',
            'd': solicitor_id
        }
        self.send_json_req(req)

    def solicitee_reject(self, solicitor_id: str):
        pass

    def send_current_gd(self):
        current_dict = {
            't': 'gd',
            'd': {
                'id': self.user_id,
                'score': self.game_instance.score,
                'level': self.game_instance.level,
                'goal': self.game_instance.goal,
                'matrix': self.game_instance.board.temp_matrix,
                'next_mino_index': self.game_instance.next_mino.shape_index,
                'hold_mino_index': self.game_instance.hold_mino.shape_index
            }
        }
        self.send_json_req(current_dict)

    def send_current_gd_thread(self):
        while True:
            if self.game_instance.status == 'in_game':
                self.send_current_gd()
            time.sleep(0.1)  # 0.1초마다