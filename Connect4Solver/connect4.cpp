#include <iostream>
#include <string>

// #include <pybind11/pybind11.h>

namespace py = pybind11;

const int WIDTH = 4;
const int HEIGHT = 3;
const int WIN_NUMBER = 2;

std::string WIN = "WIN";
std::string LOSE = "LOSE";
std::string TIE = "TIE";
std::string UNDECIDED = "UNDECIDED";

char PLAYER_1 = 'X';
char PLAYER_2 = 'O';
char EMPTY = '-';

std::string init_board(){
    std::string board (WIDTH*HEIGHT, EMPTY);
    return board;
}

PYBIND11_MODULE(cppc4, m) {
    m.def("init_board", &init_board, "Initialize board");
}
