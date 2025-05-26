<template>
  <div id="app">
    <!-- Title Screen -->
    <div v-if="showTitleScreen" class="title-screen">
      <h1 id="hello" class="robot-title">HELLO</h1>
    </div>

    <!-- Name Input -->
    <div v-if="showNameInput" class="name-input-section">
      <input
        type="text"
        v-model="userName"
        class="name-input"
        placeholder="Enter your name"
        @keyup.enter="submitName"
      />
      <button class="restart-button" @click="submitName">Submit</button>
    </div>

    <!-- Yes/No Question -->
    <div v-if="showYesNo" class="yes-no-section">
      <button class="yes-button" @click="gameYes">Yes</button>
      <button class="no-button" @click="gameNo">No</button>
    </div>

    <!-- Introductory Page -->
    <div v-if="showIntro && !showTitleScreen" class="intro-section">
      <p class="welcome-text">Hello, {{ userName }}! Do you want to play a game?</p>
      <button class="start-button" @click="startGame">Start Game</button>
      <button class="quit-button" @click="quitGame('quit')">Quit</button>
    </div>

    <!-- Game Page -->
    <div v-if="!showIntro && !showTitleScreen && !showYesNo && !showNameInput" class="game-container">
      <p v-if="!winner" class="turn-text">Current Turn: {{ currentPlayer }}</p>

      <!-- Tic-Tac-Toe Board -->
      <div v-if="gameStarted" class="board">
        <div
          v-for="(cell, index) in board"
          :key="index"
          class="cell"
          @click="makeMove(index)"
        >
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
      <button class="quit-button" @click="pauseGame('pause')">Quit Game</button>
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
      nameSubmitted: true,
      pressedYes: true,
      pressedNo: true,
      moveMade: true,
      gameRestarted: true,
      gamePaused: true,
      gameQuit: true,
      board: Array(9).fill(""),
      currentPlayer: "",
      winner: null,
      url: "https://cf8c-82-145-104-146.ngrok-free.app" // Changes everytime a new tunnel is created
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
        const response = await axios.get(this.url +"/greet_user", {headers: {'ngrok-skip-browser-warning': 'true'}});
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
      if (this.nameSubmitted === true) {
        this.nameSubmitted = false;
        try {
          await axios.post(this.url +"/get_username", { name: this.userName }, {headers: {'ngrok-skip-browser-warning': 'true'}});
          this.getYesNoResponse();
          this.nameSubmitted = true;
        }catch (error) {
          if (error.response && error.response.data && error.response.data.error) {
            alert("Error: " + error.response.data.error);
          } else {
            alert("Unknown error occurred. Using default name.");
            this.userName = "Player";
            this.getYesNoResponse();
          }
          this.nameSubmitted = true;
        }
      }
    },

    async getYesNoResponse() {
      try {
        const response = await axios.get(this.url +"/get_yes_no", {headers: {'ngrok-skip-browser-warning': 'true'}});
        console.log(response.data);
        this.showNameInput = false;
        this.showYesNo = true;
      } catch (error) {
        console.error("Error getting yes/no response:", error);
      }
    },

    async gameYes() {
      if (this.pressedYes === true || this.pressedNo === true) {
        this.pressedYes = false;
        this.pressedNo = false;
        await axios.post(this.url +"/game_response", { response: "yes"} , {headers: {'ngrok-skip-browser-warning': 'true'}});
        this.startGame();
        this.pressedYes = true;
        this.pressedNo = true;
      }
    },

    async gameNo(){
      if (this.pressedYes === true || this.pressedNo === true) {
        this.pressedYes = false;
        this.pressedNo = false;
        await axios.post(this.url +"/game_response", {response: "no"} , {headers: {'ngrok-skip-browser-warning': 'true'}});
        this.showYesNo = false;
        this.showIntro = true;
        this.pressedYes = true;
        this.pressedNo = true;
      }
    },

    async startGame() {
      this.showIntro = false;
      this.showYesNo = false;
      const response = await axios.post(this.url +"/start_game", {headers: {'ngrok-skip-browser-warning': 'true'}});
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
      if (this.moveMade === true) {
        this.moveMade = false;
        try {
          const response = await axios.post(this.url +"/update_board", {indice: index} , {headers: {'ngrok-skip-browser-warning': 'true'}});
          console.log(response.data);
          this.board = response.data.board;

          if (response.data.message === "Game over") {
            this.winner = response.data.winner;
            console.log("Winner:", this.winner);
            await axios.post(this.url +"/announce_winner", {winner: this.winner} , {headers: {'ngrok-skip-browser-warning': 'true'}});
            await axios.get(this.url +"/play_again", {headers: {'ngrok-skip-browser-warning': 'true'}});
            this.moveMade = true;
            return;  
          }

          this.currentPlayer = "O";
          await axios.post(this.url +"/announce_turn", {player: this.currentPlayer} , {headers: {'ngrok-skip-browser-warning': 'true'}});
          this.moveMade = true;

          setTimeout(() => this.getRobotMove(), 1000);
        } catch (error) {
          console.error("Invalid move:", error);
        }
      }
    },

    async getRobotMove() {
      if (this.winner || this.currentPlayer !== "O") return;
      try {
        const response = await axios.get(this.url +"/get_robot_move", {headers: {'ngrok-skip-browser-warning': 'true'}});
        console.log(response.data);
        this.board = response.data.board;

        if (response.data.message === "Game over") {
          this.winner = response.data.winner;
          await axios.post(this.url +"/announce_winner", {winner: this.winner} , {headers: {'ngrok-skip-browser-warning': 'true'}});
          await axios.get(this.url +"/play_again", {headers: {'ngrok-skip-browser-warning': 'true'}});
          return;  
        }

        this.currentPlayer = "X";
        await axios.post(this.url +"/announce_turn", {player: this.currentPlayer} , {headers: {'ngrok-skip-browser-warning': 'true'}});

      } catch (error) {
        console.error("Error getting robot move:", error);
      }
    },

    async restartGame(input) {
      if (this.gameRestarted === true) {
        this.gameRestarted = false;
        await axios.post(this.url +"/restart_game", {input} , {headers: {'ngrok-skip-browser-warning': 'true'}});
        const response = await axios.post(this.url +"/start_game", {headers: {'ngrok-skip-browser-warning': 'true'}});
        this.currentPlayer = response.data.first_player;
        this.board = Array(9).fill("");
        this.winner = null;
        this.gameStarted = true;
        this.gameRestarted = true;
        if (this.currentPlayer === "O") {
          setTimeout(() => this.getRobotMove(), 1000);
        }
      }
    }, 

    async pauseGame(input) {
      if (this.gamePaused === true) {
        this.gamePaused = false;
        await axios.post(this.url +"/restart_game", {input} , {headers: {'ngrok-skip-browser-warning': 'true'}});
        this.showIntro = true;
        this.board = Array(9).fill("");
        this.winner = null;
        this.gameStarted = false;
        this.showTitleScreen = false;
        this.gamePaused = true;
      }
    },

    async quitGame(input) {
      if (this.gameQuit === true) {
        this.gameQuit = false;
        await axios.post(this.url +"/restart_game", {input} , {headers: {'ngrok-skip-browser-warning': 'true'}});
        this.showIntro = false;
        this.board = Array(9).fill("");
        this.winner = null;
        this.gameStarted = false;
        this.userName = "";
        this.showTitleScreen = true;
        this.gameQuit = true;
        //this.startTitleSequence();
      }
    },
  },
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

/* General Styles */
#app {
  text-align: center;
  font-family: Arial, sans-serif;
  margin: 0;
}

/* Title Screen */
.title-screen {
  height: 100vh;
  width: 100vw;
  background-color: #ffffff;
  color: #000000;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.robot-title {
  font-size: 12vw;
  font-family: 'Orbitron', monospace;
  font-weight: 900;
  text-shadow: 0 0 10px #00bbff, 0 0 20px #004cff;
  margin: 0;
  animation: pulseGlow 2s ease-in-out infinite;
}

@keyframes pulseGlow {
  0%, 100% {
    text-shadow: 0 0 10px #00bbff, 0 0 20px #004cff;
  }
  50% {
    text-shadow: 0 0 20px #00ffff, 0 0 30px #00ffff;
  }
}

/* Name Input Section */
.name-input-section {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.name-input {
  padding: 22px 25px;       
  font-size: 26px;          
  width: 360px;             
  margin-bottom: 20px;
  border: 2px solid #ccc;
  border-radius: 8px;
}

button {
  padding: 14px 25px;
  font-size: 20px;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  transition: 0.3s;
  margin: 10px;
}

/* Submit / Restart Button */
button.restart-button {
  background-color: #008CBA;
  color: white;
  padding: 22px 36px; /* increased padding */
  font-size: 28px;     /* increased font size */
}

button.restart-button:hover {
  background-color: #007bb5;
}

/* Yes/No Section */
.yes-no-section {
  display: flex;
  flex-direction: row;
  height: 100vh;
  width: 100vw;
}

.yes-button, .no-button {
  flex: 1;
  height: 100%;
  font-size: 32px;
  font-weight: bold;
  border-radius: 0;
  color: white;
  border: none;
  transition: background-color 0.3s ease;
}

.yes-button {
  background-color: #4CAF50;
}

.yes-button:hover {
  background-color: #45a049;
}

.no-button {
  background-color: #f44336;
}

.no-button:hover {
  background-color: #d32f2f;
}

/* Introductory Page */
.intro-section {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.welcome-text {
  font-size: 32px;
  margin-bottom: 40px;
  font-weight: bold;
}

.start-button,
.quit-button {
  font-size: 24px;
  padding: 18px 28px;
  margin: 10px;
}

.start-button {
  background-color: #4CAF50;
  color: white;
}

.start-button:hover {
  background-color: #45a049;
}

.quit-button {
  background-color: #ff4c4c;
  color: white;
  padding: 14px 25px;  /* smaller like old restart */
  font-size: 20px;
}

.quit-button:hover {
  background-color: #e60000;
}

/* Game Page */
.game-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  justify-content: center; 
  align-items: center;
}

/* Game Board */
.turn-text {
  font-size: 22px;
  margin-bottom: 15px;
}

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
  font-size: 28px;
  border: 2px solid black;
  cursor: pointer;
  background-color: #f9f9f9;
  transition: 0.3s;
}

.cell:hover {
  background-color: #e0e0e0;
}

/* Game Over */
.game-over-section {
  margin-top: 30px;
}

.winner-text {
  font-size: 34px;
  font-weight: bold;
  margin-top: 30px;
}
</style>

