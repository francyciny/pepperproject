<template>
  <div id="app">
    <h1 class="title">Tic-Tac-Toe with Pepper</h1>

    <!-- Introductory Page -->
    <div v-if="showIntro" class="intro-section">
      <p class="welcome-text">Hello, {{ userName }}! Do you want to play a game?</p>
      <button class="start-button" @click="startGame">Start Game</button>
    </div>

    <!-- Game Page -->
    <div v-if="!showIntro">
      <p v-if="!winner" class="turn-text">Current Turn: {{ currentPlayer }}</p>

      <!-- Tic-Tac-Toe Board (Always Visible) -->
      <div v-if="gameStarted" class="board">
        <div v-for="(cell, index) in board" 
             :key="index" 
             class="cell" 
             @click="makeMove(index)">
          {{ cell }}
        </div>
      </div>

      <!-- Game Over Message -->
      <div v-if="winner" class="game-over-section">
        <p class="winner-text">
          {{ winner === "draw" ? "It's a draw!" : `Winner: ${winner}` }}
        </p>
        <button class="restart-button" @click="restartGame">Restart Game</button>
      </div>

      <!-- Quit Game Button -->
      <button class="quit-button" @click="quitGame">Quit Game</button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      userName: "Player",
      showIntro: true,
      gameStarted: false,
      board: Array(9).fill(""),
      currentPlayer: "",
      winner: null,
    };
  },
  methods: {
    async startGame() {
      this.showIntro = false;
      const response = await axios.post("http://127.0.0.1:8080/start_game");
      this.currentPlayer = response.data.first_player;
      this.board = Array(9).fill(""); 
      this.winner = null;
      this.gameStarted = true;

      if (this.currentPlayer === "O") {
        setTimeout(() => this.getRobotMove(), 1000);
      }
    },

    async makeMove(index) {
      if (this.board[index] !== "" || this.winner || this.currentPlayer !== "X") return;
      try {
        const response = await axios.post("http://127.0.0.1:8080/update_board", { index });
        this.board = response.data.board;

        if (response.data.message === "Game over") {
          this.winner = response.data.winner;
          return;  
        }

        this.currentPlayer = "O";
        setTimeout(() => this.getRobotMove(), 1000);
      } catch (error) {
        console.error("Invalid move:", error);
      }
    },

    async getRobotMove() {
      if (this.winner || this.currentPlayer !== "O") return;
      try {
        const response = await axios.get("http://127.0.0.1:8080/get_robot_move");
        this.board = response.data.board;

        if (response.data.message === "Game over") {
          this.winner = response.data.winner;
          return;  
        }

        this.currentPlayer = "X";
      } catch (error) {
        console.error("Error getting robot move:", error);
      }
    },

    async restartGame() {
      const response = await axios.post("http://127.0.0.1:8080/start_game");
      this.currentPlayer = response.data.first_player;
      this.board = Array(9).fill("");
      this.winner = null;
      this.gameStarted = true;

      if (this.currentPlayer === "O") {
        setTimeout(() => this.getRobotMove(), 1000);
      }
    },

    quitGame() {
      this.showIntro = true;
      this.board = Array(9).fill("");
      this.winner = null;
      this.gameStarted = false;
    },
  },
};
</script>

<style>
/* General Styles */
#app {
  text-align: center;
  font-family: Arial, sans-serif;
  margin-top: 50px;
}

/* Title */
.title {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 20px;
}

/* Intro Section */
.intro-section {
  margin-bottom: 30px;
}

.welcome-text {
  font-size: 20px;
  margin-bottom: 10px;
}

/* Buttons */
button {
  padding: 12px 20px;
  font-size: 18px;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  transition: 0.3s;
}

.start-button {
  background-color: #4CAF50;
  color: white;
}

.start-button:hover {
  background-color: #45a049;
}

.restart-button {
  background-color: #008CBA;
  color: white;
  margin-top: 20px;
}

.restart-button:hover {
  background-color: #007bb5;
}

.quit-button {
  background-color: #ff4c4c;
  color: white;
  margin-top: 20px;
}

.quit-button:hover {
  background-color: #e60000;
}

/* Turn Text */
.turn-text {
  font-size: 20px;
  margin-bottom: 15px;
}

/* Game Board */
.board {
  display: grid;
  grid-template-columns: repeat(3, 100px);
  grid-gap: 10px;
  justify-content: center;
  margin: 20px auto;
}

.cell {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  border: 2px solid black;
  cursor: pointer;
  background-color: #f9f9f9;
  transition: 0.3s;
}

.cell:hover {
  background-color: #e0e0e0;
}

/* Winner Text */
.winner-text {
  font-size: 24px;
  font-weight: bold;
  margin-top: 20px;
}

/* Game Over Section */
.game-over-section {
  margin-top: 20px;
}
</style>
