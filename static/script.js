let turn = "X";
let gameEnd = false;

function updateBoard(board) {
    for (let key in board) {
        $(`[data-cell=${key}]`).text(board[key]);
    }
}

function restartGame() {
    $.post("/restart", (data) => {
        updateBoard(data.board);
        turn = data.turn;
        gameEnd = data.game_end;
        $("#message").text("");
    });
}

function play(cell) {
    if (!gameEnd) {
        $.post("/play", { cell: cell }, (data) => {
            updateBoard(data.board);
            if (data.result) {
                $("#message").text(data.result);
                gameEnd = true;
            }
            turn = (turn === "X") ? "O" : "X";
        });
    }
}

$("#restart").click(restartGame);

$("td").click(function () {
    let cell = $(this).data("cell");
    play(cell);
});

$("#multiPlayer").click(function () {
    $.post("/mode", { mode: "multiPlayer" });
});

$("#singlePlayer").click(function () {
    $.post("/mode", { mode: "singlePlayer" });
});

$(document).ready(function () {
    restartGame();
});
