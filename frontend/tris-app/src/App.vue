<template>
  <div id="app">
    <!-- Title Screen -->
    <div v-if="showTitleScreen" class="title-screen">
      <h1 id="hello">HELLO</h1>
    </div>

    <!-- Name Input -->
    <div v-if="showNameInput">
      <input type="text" v-model="userName" placeholder="Enter your name">
      <button @click="submitName">Submit</button>
    </div>

    <!-- Yes/No Question -->
    <div v-if="showYesNo">
      <button @click="gameYes">Yes</button>
      <button @click="gameNo">No</button>
    </div>

    <!-- Introductory Page -->
    <div v-if="showIntro && !showTitleScreen" class="intro-section">
      <p class="welcome-text">Hello, {{ userName }}! Do you want to play a game?</p>
      <button class="start-button" @click="startGame">Start Game</button>
    </div>

    <!-- Game Page -->
    <div v-if="!showIntro && !showTitleScreen && !showYesNo && !showNameInput">
      <p v-if="!winner" class="turn-text">Current Turn: {{ currentPlayer }}</p>

      <!-- Tic-Tac-Toe Board -->
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
        <button class="restart-button" @click="restartGame('rematch')">Rematch!</button>
      </div>

      <!-- Quit Game Button -->
      <button class="quit-button" @click="quitGame('quit')">Quit Game</button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      userName: "",
      showTitleScreen: true,
      showIntro: false,
      showNameInput: false,
      showYesNo: false,
      gameStarted: false,
      board: Array(9).fill(""),
      currentPlayer: "",
      winner: null,
    };
  },
  mounted() {
    this.startTitleSequence();
  },
  methods: {
    async startTitleSequence() {
      // Show "HELLO" until pepper greets user
      setTimeout(async () => {
        // this.showTitleScreen = false;
        await this.greetUser();
      }, 2000);
    },

    async greetUser(){
      try {
        const response = await axios.get("https://fb77-78-211-91-149.ngrok-free.app/greet_user", {headers: {'ngrok-skip-browser-warning': 'true'}});
        document.getElementById("hello").innerText = response.data.message;
        console.log("aooo");
        this.showTitleScreen = false;
        this.showNameInput = true;
      } catch (error) {
        document.getElementById("hello").innerText = "ERRORE: " + error;
        console.error("Error greeting:", error);
      }
    },

    async submitName() {
      try {
        await axios.post("https://fb77-78-211-91-149.ngrok-free.app/get_username", { name: this.userName }, {headers: {'ngrok-skip-browser-warning': 'true'}});
        this.getYesNoResponse();
      }catch (error) {
      console.error("Error getting user name:", error);
      this.userName = "Player";
      this.getYesNoResponse();
      }
    },

    async getYesNoResponse() {
      try {
        const response = await axios.get("https://fb77-78-211-91-149.ngrok-free.app/get_yes_no", {headers: {'ngrok-skip-browser-warning': 'true'}});
        console.log(response.data);
        this.showNameInput = false;
        this.showYesNo = true;
      } catch (error) {
        console.error("Error getting yes/no response:", error);
      }
    },

    async gameYes() {
      await axios.post("https://fb77-78-211-91-149.ngrok-free.app/game_response", { response: "yes"} , {headers: {'ngrok-skip-browser-warning': 'true'}});
      this.startGame();
    },

    async gameNo(){
      await axios.post("https://fb77-78-211-91-149.ngrok-free.app/game_response", {response: "no"} , {headers: {'ngrok-skip-browser-warning': 'true'}});
      this.showYesNo = false;
      this.showIntro = true;
    },

    async startGame() {
      this.showIntro = false;
      this.showYesNo = false;
      const response = await axios.post("https://fb77-78-211-91-149.ngrok-free.app/start_game", {headers: {'ngrok-skip-browser-warning': 'true'}});
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
        const response = await axios.post("https://fb77-78-211-91-149.ngrok-free.app/update_board", {indice: index} , {headers: {'ngrok-skip-browser-warning': 'true'}});
        console.log(response.data);
        this.board = response.data.board;

        if (response.data.message === "Game over") {
          this.winner = response.data.winner;
          await axios.get("https://fb77-78-211-91-149.ngrok-free.app/play_again", {headers: {'ngrok-skip-browser-warning': 'true'}});
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
        const response = await axios.get("https://fb77-78-211-91-149.ngrok-free.app/get_robot_move", {headers: {'ngrok-skip-browser-warning': 'true'}});
        console.log(response.data);
        this.board = response.data.board;

        if (response.data.message === "Game over") {
          this.winner = response.data.winner;
          await axios.get("https://fb77-78-211-91-149.ngrok-free.app/play_again", {headers: {'ngrok-skip-browser-warning': 'true'}});
          return;  
        }

        this.currentPlayer = "X";
      } catch (error) {
        console.error("Error getting robot move:", error);
      }
    },

    async restartGame(input) {
      await axios.post("https://fb77-78-211-91-149.ngrok-free.app/restart_game", {input} , {headers: {'ngrok-skip-browser-warning': 'true'}});
      const response = await axios.post("https://fb77-78-211-91-149.ngrok-free.app/start_game", {headers: {'ngrok-skip-browser-warning': 'true'}});
      this.currentPlayer = response.data.first_player;
      this.board = Array(9).fill("");
      this.winner = null;
      this.gameStarted = true;

      if (this.currentPlayer === "O") {
        setTimeout(() => this.getRobotMove(), 1000);
      }
    }, 

    async quitGame(input) {
      await axios.post("https://fb77-78-211-91-149.ngrok-free.app/restart_game", {input} , {headers: {'ngrok-skip-browser-warning': 'true'}});
      this.showIntro = false;
      this.board = Array(9).fill("");
      this.winner = null;
      this.gameStarted = false;
      this.userName = "";
      this.showTitleScreen = true;
      this.startTitleSequence();
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

.title-screen {
  font-size: 50px;
  font-weight: bold;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

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

/* Current Turn text */
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

.winner-text {
  font-size: 24px;
  font-weight: bold;
  margin-top: 20px;
}

.game-over-section {
  margin-top: 20px;
}
</style>
