// Vector Tapper Soda Shop Logic
// Fast-paced retro management sim game

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreDisplay = document.getElementById('scoreDisplay');
const livesDisplay = document.getElementById('livesDisplay');
const levelDisplay = document.getElementById('levelDisplay');

// Game constants
const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 600;
const BAR_WIDTH = 700;
const BAR_HEIGHT = 60;
const BAR_SPACING = 90;
const BAR_START_X = 50;
const BAR_START_Y = 80;
const CUSTOMER_WIDTH = 40;
const CUSTOMER_HEIGHT = 35;
const DRINK_WIDTH = 25;
const DRINK_HEIGHT = 20;
const MUG_WIDTH = 20;
const MUG_HEIGHT = 15;
const BARTENDER_WIDTH = 35;
const BARTENDER_HEIGHT = 50;
const DRINK_SPEED = 8;
const MUG_SPEED = 5;

// Game state
let gameState = 'menu'; // menu, playing, gameover
let score = 0;
let lives = 3;
let level = 1;
let currentBar = 0;
let customerSpawnTimer = 0;
let customerSpawnRate = 180;
let difficultyTimer = 0;

// Game objects
let customers = [[], [], [], []];
let drinks = [];
let emptyMugs = [];
let bartender = { x: BAR_START_X + BAR_WIDTH, y: 0 };

// Colors
const COLORS = {
    background: '#1a1a2e',
    bar: '#16213e',
    barEdge: '#0f3460',
    customer: '#e94560',
    customerOutline: '#c73e54',
    drink: '#f4a261',
    drinkFoam: '#ffffff',
    mug: '#8b7355',
    mugHandle: '#6b5345',
    bartender: '#4cc9f0',
    bartenderOutline: '#3ab0d8',
    text: '#ffffff',
    lives: '#e94560'
};

// Input handling
const keys = {};

document.addEventListener('keydown', (e) => {
    keys[e.code] = true;
    if (e.code === 'Space') {
        e.preventDefault();
        handleAction();
    }
    if (e.code === 'Enter') {
        e.preventDefault();
        if (gameState === 'menu' || gameState === 'gameover') {
            startGame();
        }
    }
});

document.addEventListener('keyup', (e) => {
    keys[e.code] = false;
});

function handleAction() {
    if (gameState !== 'playing') return;

    const barY = BAR_START_Y + currentBar * BAR_SPACING;
    drinks.push({
        x: BAR_START_X + BAR_WIDTH - BARTENDER_WIDTH,
        y: barY + BAR_HEIGHT / 2 - DRINK_HEIGHT / 2,
        bar: currentBar,
        velocity: DRINK_SPEED + level * 0.5
    });
}

function startGame() {
    gameState = 'playing';
    score = 0;
    lives = 3;
    level = 1;
    currentBar = 0;
    customerSpawnTimer = 0;
    customerSpawnRate = 180;
    difficultyTimer = 0;
    customers = [[], [], [], []];
    drinks = [];
    emptyMugs = [];
    updateBartenderPosition();
    updateUI();
}

function updateBartenderPosition() {
    bartender.y = BAR_START_Y + currentBar * BAR_SPACING + (BAR_HEIGHT - BARTENDER_HEIGHT) / 2;
}

function spawnCustomer() {
    const bar = Math.floor(Math.random() * 4);
    customers[bar].push({
        x: BAR_START_X - CUSTOMER_WIDTH,
        y: BAR_START_Y + bar * BAR_SPACING + (BAR_HEIGHT - CUSTOMER_HEIGHT) / 2,
        width: CUSTOMER_WIDTH,
        height: CUSTOMER_HEIGHT,
        velocity: 0.3 + level * 0.15,
        served: false,
        returningMug: false,
        mugReturnTimer: 0
    });
}

function update() {
    if (gameState !== 'playing') return;

    // Update bartender position
    if (keys['ArrowUp'] && currentBar > 0) {
        currentBar--;
        updateBartenderPosition();
    }
    if (keys['ArrowDown'] && currentBar < 3) {
        currentBar++;
        updateBartenderPosition();
    }

    // Spawn customers
    customerSpawnTimer++;
    if (customerSpawnTimer >= customerSpawnRate) {
        spawnCustomer();
        customerSpawnTimer = 0;
    }

    // Increase difficulty over time
    difficultyTimer++;
    if (difficultyTimer >= 600) {
        level++;
        difficultyTimer = 0;
        customerSpawnRate = Math.max(60, 180 - level * 15);
        updateUI();
    }

    // Update customers
    for (let bar = 0; bar < 4; bar++) {
        for (let i = customers[bar].length - 1; i >= 0; i--) {
            const customer = customers[bar][i];
            customer.x += customer.velocity;

            // Check if customer reached the end
            if (customer.x > BAR_START_X + BAR_WIDTH) {
                customers[bar].splice(i, 1);
                lives--;
                updateUI();
                if (lives <= 0) {
                    gameState = 'gameover';
                }
                continue;
            }

            // Check for returning mug
            if (customer.served && !customer.returningMug) {
                customer.mugReturnTimer++;
                if (customer.mugReturnTimer > 60) {
                    customer.returningMug = true;
                    emptyMugs.push({
                        x: customer.x + customer.width,
                        y: BAR_START_Y + bar * BAR_SPACING + (BAR_HEIGHT - MUG_HEIGHT) / 2,
                        bar: bar,
                        velocity: MUG_SPEED + level * 0.3
                    });
                }
            }
        }
    }

    // Update drinks
    for (let i = drinks.length - 1; i >= 0; i--) {
        const drink = drinks[i];
        drink.x -= drink.velocity;

        // Check if drink went off screen (miss)
        if (drink.x < BAR_START_X - DRINK_WIDTH) {
            drinks.splice(i, 1);
            lives--;
            updateUI();
            if (lives <= 0) {
                gameState = 'gameover';
            }
            continue;
        }

        // Check collision with customers
        const barCustomers = customers[drink.bar];
        for (let j = barCustomers.length - 1; j >= 0; j--) {
            const customer = barCustomers[j];
            if (!customer.served &&
                drink.x < customer.x + customer.width &&
                drink.x + DRINK_WIDTH > customer.x &&
                drink.y < customer.y + customer.height &&
                drink.y + DRINK_HEIGHT > customer.y) {

                // Serve the customer
                customer.served = true;
                customer.x -= 30; // Push back
                drinks.splice(i, 1);
                score += 100;
                updateUI();
                break;
            }
        }
    }

    // Update empty mugs
    for (let i = emptyMugs.length - 1; i >= 0; i--) {
        const mug = emptyMugs[i];
        mug.x += mug.velocity;

        // Check collision with bartender
        if (mug.bar === currentBar &&
            mug.x < bartender.x + BARTENDER_WIDTH &&
            mug.x + MUG_WIDTH > bartender.x &&
            mug.y < bartender.y + BARTENDER_HEIGHT &&
            mug.y + MUG_HEIGHT > bartender.y) {

            emptyMugs.splice(i, 1);
            score += 50;
            updateUI();
            continue;
        }

        // Check if mug went off screen (break)
        if (mug.x > BAR_START_X + BAR_WIDTH) {
            emptyMugs.splice(i, 1);
            lives--;
            updateUI();
            if (lives <= 0) {
                gameState = 'gameover';
            }
        }
    }
}

function drawBackground() {
    ctx.fillStyle = COLORS.background;
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    // Draw floor
    ctx.fillStyle = '#0f0f1e';
    ctx.fillRect(0, CANVAS_HEIGHT - 50, CANVAS_WIDTH, 50);

    // Draw wall pattern
    ctx.strokeStyle = '#252540';
    ctx.lineWidth = 1;
    for (let x = 0; x < CANVAS_WIDTH; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, CANVAS_HEIGHT - 50);
        ctx.stroke();
    }
    for (let y = 0; y < CANVAS_HEIGHT - 50; y += 40) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(CANVAS_WIDTH, y);
        ctx.stroke();
    }
}

function drawBars() {
    for (let i = 0; i < 4; i++) {
        const y = BAR_START_Y + i * BAR_SPACING;

        // Bar counter
        ctx.fillStyle = COLORS.bar;
        ctx.fillRect(BAR_START_X, y, BAR_WIDTH, BAR_HEIGHT);

        // Bar edge (right side - bartender area)
        ctx.fillStyle = COLORS.barEdge;
        ctx.fillRect(BAR_START_X + BAR_WIDTH - 10, y, 10, BAR_HEIGHT);

        // Bar highlight
        ctx.fillStyle = '#1e2a4a';
        ctx.fillRect(BAR_START_X, y, BAR_WIDTH, 3);

        // Bar shadow
        ctx.fillStyle = '#0d1828';
        ctx.fillRect(BAR_START_X, y + BAR_HEIGHT - 3, BAR_WIDTH, 3);
    }
}

function drawCustomers() {
    for (let bar = 0; bar < 4; bar++) {
        for (const customer of customers[bar]) {
            const x = customer.x;
            const y = customer.y;

            // Body
            ctx.fillStyle = customer.served ? '#4cc9f0' : COLORS.customer;
            ctx.strokeStyle = COLORS.customerOutline;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.roundRect(x, y, customer.width, customer.height, 5);
            ctx.fill();
            ctx.stroke();

            // Eyes
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(x + 12, y + 12, 5, 0, Math.PI * 2);
            ctx.arc(x + 28, y + 12, 5, 0, Math.PI * 2);
            ctx.fill();

            // Pupils
            ctx.fillStyle = '#000000';
            ctx.beginPath();
            ctx.arc(x + 13, y + 12, 2, 0, Math.PI * 2);
            ctx.arc(x + 29, y + 12, 2, 0, Math.PI * 2);
            ctx.fill();

            // Mouth
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 2;
            ctx.beginPath();
            if (customer.served) {
                ctx.arc(x + 20, y + 22, 5, 0, Math.PI);
            } else {
                ctx.arc(x + 20, y + 26, 5, Math.PI, 0);
            }
            ctx.stroke();

            // Thirst indicator (if not served)
            if (!customer.served) {
                ctx.fillStyle = '#e94560';
                ctx.font = 'bold 12px Arial';
                ctx.fillText('!', x + 17, y - 5);
            }
        }
    }
}

function drawDrinks() {
    for (const drink of drinks) {
        // Mug body
        ctx.fillStyle = COLORS.mug;
        ctx.strokeStyle = COLORS.mugHandle;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(drink.x, drink.y, DRINK_WIDTH, DRINK_HEIGHT, 3);
        ctx.fill();
        ctx.stroke();

        // Drink liquid
        ctx.fillStyle = COLORS.drink;
        ctx.beginPath();
        ctx.roundRect(drink.x + 2, drink.y + 2, DRINK_WIDTH - 4, DRINK_HEIGHT - 6, 2);
        ctx.fill();

        // Foam
        ctx.fillStyle = COLORS.drinkFoam;
        ctx.beginPath();
        ctx.ellipse(drink.x + DRINK_WIDTH / 2, drink.y + 4, DRINK_WIDTH / 2 - 3, 4, 0, 0, Math.PI * 2);
        ctx.fill();
    }
}

function drawEmptyMugs() {
    for (const mug of emptyMugs) {
        // Mug body
        ctx.fillStyle = COLORS.mug;
        ctx.strokeStyle = COLORS.mugHandle;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(mug.x, mug.y, MUG_WIDTH, MUG_HEIGHT, 3);
        ctx.fill();
        ctx.stroke();

        // Handle
        ctx.beginPath();
        ctx.arc(mug.x + MUG_WIDTH, mug.y + MUG_HEIGHT / 2, 5, -Math.PI / 2, Math.PI / 2);
        ctx.stroke();

        // Opening (empty)
        ctx.fillStyle = '#3a3028';
        ctx.beginPath();
        ctx.ellipse(mug.x + MUG_WIDTH / 2, mug.y + 3, MUG_WIDTH / 3, 2, 0, 0, Math.PI * 2);
        ctx.fill();
    }
}

function drawBartender() {
    const x = bartender.x;
    const y = bartender.y;

    // Body
    ctx.fillStyle = COLORS.bartender;
    ctx.strokeStyle = COLORS.bartenderOutline;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(x, y, BARTENDER_WIDTH, BARTENDER_HEIGHT, 5);
    ctx.fill();
    ctx.stroke();

    // Apron
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.roundRect(x + 5, y + 15, BARTENDER_WIDTH - 10, BARTENDER_HEIGHT - 20, 3);
    ctx.fill();

    // Head
    ctx.fillStyle = '#ffd4a3';
    ctx.beginPath();
    ctx.arc(x + BARTENDER_WIDTH / 2, y - 5, 12, 0, Math.PI * 2);
    ctx.fill();

    // Eyes
    ctx.fillStyle = '#000000';
    ctx.beginPath();
    ctx.arc(x + BARTENDER_WIDTH / 2 - 4, y - 7, 2, 0, Math.PI * 2);
    ctx.arc(x + BARTENDER_WIDTH / 2 + 4, y - 7, 2, 0, Math.PI * 2);
    ctx.fill();

    // Smile
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(x + BARTENDER_WIDTH / 2, y - 3, 4, 0, Math.PI);
    ctx.stroke();

    // Current bar indicator
    ctx.fillStyle = '#f4a261';
    ctx.font = 'bold 10px Arial';
    ctx.fillText('v', x + BARTENDER_WIDTH / 2 - 3, y - 20);
}

function drawMenu() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    ctx.fillStyle = COLORS.text;
    ctx.font = 'bold 48px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('SODA SHOP', CANVAS_WIDTH / 2, 150);

    ctx.font = '24px Arial';
    ctx.fillText('SERVE THIRSTY CUSTOMERS!', CANVAS_WIDTH / 2, 220);

    ctx.font = '18px Arial';
    ctx.fillText('UP/DOWN: Switch bars', CANVAS_WIDTH / 2, 300);
    ctx.fillText('SPACE: Pour drink', CANVAS_WIDTH / 2, 330);
    ctx.fillText('Catch empty mugs to earn bonus points!', CANVAS_WIDTH / 2, 360);

    ctx.font = '24px Arial';
    ctx.fillStyle = '#4cc9f0';
    ctx.fillText('Press ENTER to start', CANVAS_WIDTH / 2, 450);
}

function drawGameOver() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    ctx.fillStyle = '#e94560';
    ctx.font = 'bold 48px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', CANVAS_WIDTH / 2, 200);

    ctx.fillStyle = COLORS.text;
    ctx.font = '28px Arial';
    ctx.fillText(`Final Score: ${score}`, CANVAS_WIDTH / 2, 280);
    ctx.fillText(`Level Reached: ${level}`, CANVAS_WIDTH / 2, 330);

    ctx.font = '24px Arial';
    ctx.fillStyle = '#4cc9f0';
    ctx.fillText('Press ENTER to play again', CANVAS_WIDTH / 2, 420);
}

function updateUI() {
    scoreDisplay.textContent = `SCORE: ${score}`;
    livesDisplay.textContent = `LIVES: ${lives}`;
    levelDisplay.textContent = `LEVEL: ${level}`;
}

function draw() {
    drawBackground();
    drawBars();
    drawCustomers();
    drawDrinks();
    drawEmptyMugs();
    drawBartender();

    if (gameState === 'menu') {
        drawMenu();
    } else if (gameState === 'gameover') {
        drawGameOver();
    }
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

// Initialize
updateBartenderPosition();
updateUI();
gameLoop();
