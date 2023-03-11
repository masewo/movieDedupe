import os
import re
import shutil
from pathlib import Path

from eitparser import EitList

base_dir = "F:/movie"
file_extensions_to_move = ["ts", "ts.ap", "ts.cuts", "ts.meta", "ts.sc", "eit"]
file_extensions_to_delete = ["ts", "ts.ap", "ts.cuts", "ts.meta", "ts.sc"]

movie_sizes = {}
movie_descriptions = {}
movies_to_keep = {}
movies_to_delete = []


def run():
    ts_counter = 0
    for file in os.listdir(base_dir):
        filename, file_extension = os.path.splitext(file)

        if file_extension == ".ts":
            ts_counter = ts_counter + 1
            if not Path(base_dir + "/" + filename + ".eit").exists():
                print("No eit file for: " + file)

        if file_extension != ".eit":
            continue

        if not Path(base_dir + "/" + filename + ".ts").exists():
            print("No ts file for: " + file)

        if "Barnaby" not in filename:
            print("This is not Barnaby: " + filename)

        shutil.copy(base_dir + "/" + file, base_dir + "/old_eit_files/" + filename + ".eit")

        eit_list = EitList(base_dir + "/" + file)
        movie_descriptions[filename] = eit_list.getEitShortDescription()

        file_stats = os.stat(base_dir + "/" + filename + ".ts")
        movie_sizes[filename] = file_stats.st_size

    for movie in movie_descriptions:
        description = movie_descriptions[movie]
        season, episode = get_season_and_episode(description)
        season_episode = "St." + season + " Ep." + episode

        if season_episode not in movies_to_keep:
            movies_to_keep[season_episode] = movie
        else:
            current_file_name = movies_to_keep[season_episode]
            current_file_size = movie_sizes[current_file_name]
            new_file_size = movie_sizes[movie]

            if new_file_size > current_file_size:
                movies_to_keep[season_episode] = movie
                movies_to_delete.append(base_dir + "/" + current_file_name)
            else:
                movies_to_delete.append(base_dir + "/" + movie)

    for season_episode in movies_to_keep:
        movie = movies_to_keep[season_episode]
        season, episode = get_season_and_episode(season_episode)

        dest_path = base_dir + "/Barnaby/St." + season + "/Ep." + episode

        if Path(dest_path).exists():
            existing_ts_file = ""
            for file in os.listdir(dest_path):
                filename, file_extension = os.path.splitext(file)
                if file_extension == ".ts":
                    existing_ts_file = dest_path + "/" + filename + ".ts"
                    break

            if existing_ts_file:
                file_stats = os.stat(existing_ts_file)
                movie_size = file_stats.st_size

                # already existing movie is bigger
                if movie_size > movie_sizes[movie]:
                    movies_to_delete.append(base_dir + "/" + movie)
                    continue
                else:
                    filename, _ = os.path.splitext(existing_ts_file)
                    movies_to_delete.append(filename)

        for extension in file_extensions_to_move:
            filename = base_dir + "/" + movie + "." + extension
            if Path(filename).exists():
                dst = dest_path + "/" + movie + "." + extension
                print("moving from " + filename + " to " + dst)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(filename, dst)
            else:
                print("this file to move does not exist: " + filename)

    for movie in movies_to_delete:
        for extension in file_extensions_to_delete:
            filename = movie + "." + extension
            if Path(filename).exists():
                print("deleting " + filename)
                os.remove(filename)
            else:
                print("this file to delete does not exist: " + filename)

    print(movies_to_keep)
    print(movies_to_delete)

    print(ts_counter)
    print(len(movie_descriptions))
    print(len(movie_sizes))
    print(len(movies_to_keep))
    print(len(movies_to_delete))


def get_season_and_episode(description):
    regex = re.search(r"^St\.(\d{1,2})\sEp\.(\d{1,2})", description)
    season = regex.group(1)
    episode = regex.group(2)
    return season, episode


if __name__ == '__main__':
    run()
