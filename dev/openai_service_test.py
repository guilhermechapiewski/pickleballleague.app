import sys
import os
import json
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.openai_service import OpenAIService

if __name__ == "__main__":
    num_rounds = 7
    player_list = "GC (80.00%/3.9), Lana (78.60%/4.9), Tammy I (75.00%/3.5), Juliano (73.30%/3.1), Lilly (66.70%/2.7), Emily (66.70%/2.2), Irina (57.10%/1.7), Fariba (57.10%/-0.4), Tammy J (53.80%/-0.3), Sveta (50.00%/1.2), Regina (50.00%/-1.2), Anne (50.00%/-2.5), Sung (42.90%/-1), Mojgan (42.90%/-1.6), Nancy (33.30%/-0.7), Boris (33.30%/-1.7), Roya (23.10%/-2.9), Aline (23.10%/-4.6)"

    print("Original player list:")
    print(player_list)

    players = player_list.split(', ')
    random.shuffle(players)
    player_list = ', '.join(players)

    print("Shuffled player list:")
    print(player_list)

    schedule = OpenAIService.create_schedule(num_rounds, player_list)
    print(json.dumps(schedule, indent=4))