console.log("Script loaded");
document.addEventListener('DOMContentLoaded', function() {
    const user_id = "{{ user_id }}"; // Получаем user_id из HTML
    const buttonBar = document.createElement('div');
    buttonBar.className = 'button-bar';
    buttonBar.innerHTML = `
        <button class="logo-button" onclick="inviteReferral()">
            <img src="/static/referral.png" alt="Пригласить реферала">
        </button>
        <button class="logo-button" onclick="subscribe('xcom')">
            <img src="/static/x1.png" alt="X.COM">
        </button>
        <button class="logo-button" onclick="subscribe('telegram')">
            <img src="/static/t.png" alt="Telegram">
        </button>
        <button class="logo-button" onclick="window.location.href='/static?user_id=${user_id}'">
            <img src="/static/Statistic.jpg" alt="Статистика">
        </button>
    `;
    document.body.appendChild(buttonBar);
});
