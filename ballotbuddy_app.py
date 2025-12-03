#!/usr/bin/env python3
"""
BallotBuddy – Georgia Voting Chatbot (Frontend + Backend in one file)

Run from terminal (macOS):

    cd ~/Documents      # or wherever this file lives
    source .venv/bin/activate
    export OPENAI_API_KEY="YOUR_NEW_KEY_HERE"
    PORT=5002 python3 ballotbuddy_app.py

Then open http://127.0.0.1:5002 in your browser.
"""

import os
import json
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

# ----------------- CONFIG -----------------

OPENAI_MODEL = "gpt-4.1-mini"  # change to another OpenAI model if you like

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = Flask(__name__)

# ----------------- FRONTEND (HTML + CSS + JS) -----------------

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <title>BallotBuddy – Georgia Voting Assistant</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {
      --bg: #05091a;
      --bg-elevated: #071021;
      --bg-panel: #050b1f;
      --bg-card: #070f24;
      --border-subtle: #111827;
      --accent: #4c8dff;
      --accent-soft: rgba(76, 141, 255, 0.12);
      --accent-strong: #4c8dff;
      --text-main: #e5e7eb;
      --text-muted: #9ca3af;
      --bubble-user: #2563eb;
      --bubble-user-text: #ffffff;
      --bubble-ai: #050b1f;
      --bubble-ai-border: #111827;
      --shadow-soft: 0 26px 80px rgba(0, 0, 0, 0.75);
    }

    [data-theme="light"] {
      --bg: #e5edf9;
      --bg-elevated: #ffffff;
      --bg-panel: #f5f6fb;
      --bg-card: #f3f6fd;
      --border-subtle: #d1d5db;
      --accent: #2563eb;
      --accent-soft: rgba(37, 99, 235, 0.1);
      --accent-strong: #2563eb;
      --text-main: #111827;
      --text-muted: #6b7280;
      --bubble-user: #2563eb;
      --bubble-user-text: #ffffff;
      --bubble-ai: #f9fafb;
      --bubble-ai-border: #e5e7eb;
      --shadow-soft: 0 26px 70px rgba(15, 23, 42, 0.18);
    }

    * { box-sizing:border-box; margin:0; padding:0; }

    body {
      min-height: 100vh;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(59, 130, 246, 0.32), transparent 55%),
        radial-gradient(circle at top right, rgba(244, 114, 182, 0.2), transparent 55%),
        var(--bg);
      color: var(--text-main);
      display:flex;
      justify-content:center;
      align-items:stretch;
    }

    .shell {
      width:100%;
      max-width:1260px;
      padding:18px 24px 26px;
      display:flex;
      flex-direction:column;
      gap:24px;
    }

    /* TOP BAR */

    .top-bar {
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:12px;
    }

    .top-left {
      display:flex;
      align-items:center;
      gap:10px;
    }

    .logo-circle {
      width:34px;
      height:34px;
      border-radius:999px;
      background:radial-gradient(circle at top left,#4c8dff,#22c55e);
      display:flex;
      align-items:center;
      justify-content:center;
      font-size:14px;
      font-weight:600;
      color:#f9fafb;
      box-shadow:0 0 0 2px rgba(3,7,18,0.8);
    }

    .brand-text {
      font-size:14px;
      color:var(--text-muted);
    }

    .top-right {
      display:flex;
      align-items:center;
      gap:10px;
    }

    .hotline-pill {
      border-radius:999px;
      border:1px solid var(--border-subtle);
      padding:6px 12px;
      font-size:12px;
      color:var(--text-muted);
      background:rgba(15,23,42,0.85);
      display:inline-flex;
      align-items:center;
      gap:4px;
    }

    [data-theme="light"] .hotline-pill {
      background:#111827;
      color:#e5e7eb;
    }

    .hotline-pill strong { color:#fbbf24; }

    .theme-toggle {
      border-radius:999px;
      border:1px solid var(--border-subtle);
      padding:6px 12px;
      font-size:12px;
      background:rgba(15,23,42,0.9);
      color:#e5e7eb;
      cursor:pointer;
      display:flex;
      align-items:center;
      gap:6px;
    }

    [data-theme="light"] .theme-toggle {
      background:#ffffff;
      color:#111827;
    }

    .avatar {
      width:32px;
      height:32px;
      border-radius:999px;
      background:radial-gradient(circle at top,#22c55e,#4c8dff);
      display:flex;
      align-items:center;
      justify-content:center;
      font-size:13px;
      font-weight:600;
      color:#f9fafb;
      box-shadow:0 0 0 2px rgba(3,7,18,0.8);
    }

    /* HERO */

    .hero-section {
      margin-top:40px;
      display:flex;
      flex-direction:column;
      align-items:center;
      gap:24px;
      text-align:center;
    }

    .hero-title {
      font-size:clamp(44px,6vw,56px);
      font-weight:800;
      letter-spacing:0.03em;
      background:linear-gradient(90deg,#60a5fa,#c4b5fd,#fb7185);
      -webkit-background-clip:text;
      background-clip:text;
      color:transparent;
    }

    .hero-tagline {
      font-size:15px;
      color:var(--text-muted);
    }

    .ask-bar {
      margin-top:10px;
      width:min(860px,100%);
      border-radius:999px;
      background:rgba(8,15,35,0.96);
      border:1px solid #020617;
      box-shadow:var(--shadow-soft);
      padding:10px 12px;
      display:flex;
      align-items:center;
      gap:10px;
    }

    [data-theme="light"] .ask-bar {
      background:#ffffff;
      border-color:#d1d5db;
    }

    .ask-bar-left-btn {
      width:34px;
      height:34px;
      border-radius:999px;
      border:1px solid #1f2937;
      background:rgba(15,23,42,0.9);
      color:#e5e7eb;
      display:flex;
      align-items:center;
      justify-content:center;
      font-size:18px;
      cursor:pointer;
    }

    [data-theme="light"] .ask-bar-left-btn {
      background:#f3f4f6;
      color:#111827;
      border-color:#e5e7eb;
    }

    .ask-input {
      flex:1;
      border:none;
      background:transparent;
      color:var(--text-main);
      font-size:15px;
      padding:6px 4px;
      outline:none;
    }

    .ask-input::placeholder { color:var(--text-muted); }

    .ask-icon-btn {
      width:34px;
      height:34px;
      border-radius:999px;
      border:1px solid #1f2937;
      background:rgba(15,23,42,0.95);
      color:#9ca3af;
      font-size:13px;
      display:flex;
      align-items:center;
      justify-content:center;
      cursor:pointer;
    }

    [data-theme="light"] .ask-icon-btn {
      background:#f3f4f6;
      border-color:#e5e7eb;
      color:#6b7280;
    }

    .ask-send-btn {
      border-radius:999px;
      border:none;
      background:linear-gradient(135deg,#4c8dff,#60a5fa);
      padding:9px 22px;
      font-size:14px;
      font-weight:600;
      color:#f9fafb;
      cursor:pointer;
      box-shadow:0 15px 35px rgba(37,99,235,0.75);
    }

    /* TOPIC CARDS */

    .section-label {
      margin-top:32px;
      font-size:14px;
      color:var(--text-muted);
    }

    .topics-row {
      margin-top:18px;
      width:min(980px,100%);
      display:grid;
      grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
      gap:18px;
    }

    .topic-card {
      background:var(--bg-card);
      border-radius:22px;
      border:1px solid #0b1120;
      padding:18px 18px 14px;
      box-shadow:0 18px 46px rgba(0,0,0,0.7);
      text-align:left;
      display:flex;
      flex-direction:column;
      justify-content:space-between;
      gap:10px;
      min-height:150px;
    }

    [data-theme="light"] .topic-card {
      border-color:#e5e7eb;
      box-shadow:0 16px 45px rgba(15,23,42,0.15);
    }

    .topic-icon { font-size:22px; margin-bottom:6px; }
    .topic-title { font-size:16px; font-weight:600; margin-bottom:4px; }
    .topic-subtitle { font-size:13px; color:var(--text-muted); }

    .topic-footer {
      margin-top:10px;
      display:flex;
      justify-content:flex-start;
    }

    .topic-btn {
      border-radius:999px;
      border:1px solid #1f2937;
      padding:6px 14px;
      font-size:13px;
      color:#e5e7eb;
      background:rgba(15,23,42,0.95);
      cursor:pointer;
      display:inline-flex;
      align-items:center;
      gap:6px;
    }

    [data-theme="light"] .topic-btn {
      background:#111827;
      border-color:#111827;
      color:#e5e7eb;
    }

    .topic-btn span { font-size:11px; }

    .topic-btn:hover {
      border-color:#4c8dff;
      color:#bfdbfe;
    }

    /* CHAT PAGE – Gemini-style layout */

    .chat-section {
      margin-top:40px;
      width:min(980px,100%);
      margin-left:auto;
      margin-right:auto;
      border-radius:24px;
      background:var(--bg-panel);
      border:1px solid #020617;
      box-shadow:0 26px 70px rgba(0,0,0,0.8);
      display:none;
      flex-direction:column;
      overflow:hidden;
    }

    [data-theme="light"] .chat-section {
      border-color:#d1d5db;
      box-shadow:0 24px 60px rgba(15,23,42,0.18);
    }

    .chat-header {
      padding:12px 18px;
      border-bottom:1px solid var(--border-subtle);
      display:flex;
      justify-content:space-between;
      align-items:center;
      font-size:13px;
      color:var(--text-muted);
      background:rgba(9,15,35,0.95);
    }

    [data-theme="light"] .chat-header {
      background:#111827;
      color:#e5e7eb;
    }

    .chat-header-left {
      display:flex;
      align-items:center;
      gap:8px;
      font-size:14px;
    }

    .chat-header-left strong { color:#f9fafb; }

    .chat-header-btn {
      border-radius:999px;
      border:1px solid var(--border-subtle);
      padding:6px 14px;
      font-size:12px;
      background:transparent;
      color:var(--text-main);
      cursor:pointer;
    }

    .chat-window {
      padding:24px 40px 24px;
      max-height:420px;
      overflow-y:auto;
      display:flex;
      flex-direction:column;
      gap:16px;
      background:var(--bg-panel);
    }

    .message-row {
      width:100%;
      display:flex;
      align-items:flex-start;
      gap:8px;
    }

    .message-row.user { justify-content:flex-end; }
    .message-row.ai { justify-content:flex-start; }

    .bubble {
      max-width:min(720px,100%);
      font-size:14px;
      padding:12px 16px;
      border-radius:18px;
      line-height:1.6;
      border:1px solid transparent;
      background:var(--bubble-ai);
      word-wrap:break-word;
      white-space:normal;
    }

    .message-row.user .bubble {
      background:var(--bubble-user);
      color:var(--bubble-user-text);
      border-color:transparent;
      border-radius:20px;
    }

    .message-row.ai .bubble {
      background:var(--bubble-ai);
      color:var(--text-main);
      border-color:var(--bubble-ai-border);
      border-radius:18px;
    }

    [data-theme="light"] .message-row.ai .bubble {
      border-color:var(--bubble-ai-border);
    }

    .bubble-meta {
      margin-top:10px;
      font-size:11px;
      color:var(--text-muted);
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:4px;
    }

    .sources {
      display:flex;
      flex-wrap:wrap;
      gap:4px;
    }

    .source-pill {
      border-radius:999px;
      border:1px solid #1f2937;
      padding:1px 6px;
      font-size:10px;
      color:var(--text-muted);
    }

    [data-theme="light"] .source-pill {
      border-color:#d1d5db;
      background:#f9fafb;
    }

    .source-pill a {
      color:#93c5fd;
      text-decoration:none;
    }

    .icon-btn {
      border-radius:999px;
      border:1px solid #1f2937;
      background:transparent;
      color:var(--text-muted);
      font-size:11px;
      padding:2px 8px;
      cursor:pointer;
      display:inline-flex;
      align-items:center;
      gap:4px;
    }

    [data-theme="light"] .icon-btn {
      border-color:#d1d5db;
    }

    .attached-files {
      margin:4px 40px 10px;
      display:flex;
      flex-wrap:wrap;
      gap:4px;
    }

    .file-chip {
      border-radius:999px;
      border:1px solid #1f2937;
      padding:2px 8px;
      font-size:11px;
      color:var(--text-muted);
      display:inline-flex;
      align-items:center;
      gap:4px;
      background:var(--bg-card);
    }

    [data-theme="light"] .file-chip {
      border-color:#d1d5db;
      background:#f3f4f6;
    }

    .file-chip button {
      border:none;
      background:transparent;
      color:inherit;
      cursor:pointer;
      font-size:12px;
    }

    .chat-bottom {
      border-top:1px solid var(--border-subtle);
      padding:10px 18px;
      background:var(--bg-panel);
    }

    .bottom-form {
      display:flex;
      align-items:center;
      gap:10px;
    }

    .bottom-input {
      flex:1;
      border:none;
      background:var(--bg-elevated);
      color:var(--text-main);
      font-size:14px;
      padding:8px 10px;
      border-radius:999px;
      outline:none;
      border:1px solid var(--border-subtle);
    }

    .bottom-input::placeholder { color:var(--text-muted); }

    .bottom-attach {
      width:32px;
      height:32px;
      border-radius:999px;
      border:1px solid #1f2937;
      background:var(--bg-elevated);
      display:flex;
      align-items:center;
      justify-content:center;
      color:#9ca3af;
      font-size:16px;
      cursor:pointer;
    }

    [data-theme="light"] .bottom-attach {
      border-color:#d1d5db;
      color:#6b7280;
    }

    .bottom-send {
      border-radius:999px;
      border:none;
      background:linear-gradient(135deg,#4c8dff,#60a5fa);
      padding:8px 18px;
      font-size:13px;
      color:#f9fafb;
      cursor:pointer;
      box-shadow:0 18px 40px rgba(37,99,235,0.7);
    }

    /* SETTINGS MODAL */

    .settings-fab {
      position:fixed;
      right:16px;
      bottom:16px;
      width:34px;
      height:34px;
      border-radius:999px;
      border:1px solid #111827;
      background:rgba(15,23,42,0.9);
      color:#9ca3af;
      display:flex;
      align-items:center;
      justify-content:center;
      cursor:pointer;
      font-size:16px;
      box-shadow:0 14px 40px rgba(0,0,0,0.9);
    }

    [data-theme="light"] .settings-fab {
      background:#111827;
      color:#e5e7eb;
      border-color:#111827;
    }

    .modal-backdrop {
      position:fixed;
      inset:0;
      background:rgba(0,0,0,0.55);
      display:none;
      align-items:center;
      justify-content:center;
      z-index:40;
    }

    .modal-backdrop.open { display:flex; }

    .modal {
      background:var(--bg-elevated);
      border-radius:14px;
      padding:14px 16px 12px;
      width:280px;
      border:1px solid var(--border-subtle);
    }

    .modal-header {
      display:flex;
      justify-content:space-between;
      align-items:center;
      margin-bottom:6px;
      font-size:14px;
      font-weight:500;
    }

    .modal-section {
      margin-top:8px;
      padding-top:8px;
      border-top:1px solid var(--border-subtle);
      font-size:13px;
    }

    .setting-row {
      display:flex;
      align-items:center;
      justify-content:space-between;
      margin-top:8px;
    }

    .setting-label { font-size:13px; }
    .setting-desc { font-size:11px; color:var(--text-muted); margin-top:2px; }

    .switch {
      position:relative;
      width:34px;
      height:18px;
      border-radius:999px;
      background:#4b5563;
      cursor:pointer;
    }

    .switch-handle {
      position:absolute;
      top:2px;
      left:2px;
      width:14px;
      height:14px;
      border-radius:999px;
      background:#f9fafb;
      transition:transform 0.18s ease-out;
    }

    .switch.on { background:var(--accent); }
    .switch.on .switch-handle { transform:translateX(14px); }

    .modal-footer {
      display:flex;
      justify-content:flex-end;
      margin-top:8px;
      padding-top:6px;
      border-top:1px solid var(--border-subtle);
    }

    .btn-small {
      border-radius:999px;
      border:1px solid var(--border-subtle);
      padding:4px 10px;
      font-size:12px;
      background:transparent;
      color:var(--text-main);
      cursor:pointer;
    }

    @media (max-width:768px){
      .shell{padding:10px 12px 18px;}
      .hero-section{margin-top:28px;}
      .topics-row{grid-template-columns:1fr 1fr;}
      .chat-window{max-height:360px; padding:18px 14px;}
      .bubble{max-width:100%;}
    }

    @media (max-width:520px){
      .topics-row{grid-template-columns:1fr;}
      .hero-title{font-size:38px;}
    }
  </style>
</head>
<body>
  <div class="shell">
    <header class="top-bar">
      <div class="top-left">
        <div class="logo-circle">BB</div>
        <div class="brand-text">BallotBuddy · Georgia voting answers</div>
      </div>
      <div class="top-right">
        <div class="hotline-pill">Need live help? <strong>866-OUR-VOTE</strong></div>
        <button class="theme-toggle" id="themeToggle">
          <span id="themeIcon">🌙</span><span id="themeLabel">Dark</span>
        </button>
        <div class="avatar">BB</div>
      </div>
    </header>

    <main>
      <!-- LANDING PAGE -->
      <section class="hero-section" id="landingView">
        <div>
          <div class="hero-title">BallotBuddy</div>
          <div class="hero-tagline">
            Trusted answers about voting in Georgia — registration, voter ID, early voting, absentee ballots, and more.
          </div>
        </div>

        <form class="ask-bar" id="topForm">
          <button type="button" class="ask-bar-left-btn attach-btn" title="Attach files">+</button>
          <input id="topInput" class="ask-input" type="text" autocomplete="off" placeholder="Ask BallotBuddy a question about Georgia voting" />
          <button type="button" class="ask-icon-btn" title="Location">📍</button>
          <button type="button" class="ask-icon-btn" title="Georgia resources">🅶</button>
          <button type="button" class="ask-icon-btn" title="Refine">✏️</button>
          <button type="submit" class="ask-send-btn">Send</button>
        </form>

        <div class="section-label">You may ask</div>
        <div class="topics-row">
          <article class="topic-card">
            <div>
              <div class="topic-icon">🧭</div>
              <div class="topic-title">First-time voter steps</div>
              <div class="topic-subtitle">Exactly what to do before and on Election Day.</div>
            </div>
            <div class="topic-footer">
              <button class="topic-btn ask-btn" data-question="What are the basic steps to vote for the first time in Georgia?">
                Ask this <span>↗</span>
              </button>
            </div>
          </article>

          <article class="topic-card">
            <div>
              <div class="topic-icon">🪪</div>
              <div class="topic-title">Georgia voter ID</div>
              <div class="topic-subtitle">Which IDs are accepted and how to get a free one.</div>
            </div>
            <div class="topic-footer">
              <button class="topic-btn ask-btn" data-question="What IDs are accepted to vote in Georgia, and how can I get a free voter ID?">
                Ask this <span>↗</span>
              </button>
            </div>
          </article>

          <article class="topic-card">
            <div>
              <div class="topic-icon">✉️</div>
              <div class="topic-title">Vote by mail</div>
              <div class="topic-subtitle">How absentee ballots work and how to track one.</div>
            </div>
            <div class="topic-footer">
              <button class="topic-btn ask-btn" data-question="How does absentee voting by mail work in Georgia, and how can I track my ballot?">
                Ask this <span>↗</span>
              </button>
            </div>
          </article>

          <article class="topic-card">
            <div>
              <div class="topic-icon">🛡️</div>
              <div class="topic-title">Problems at the polls</div>
              <div class="topic-subtitle">Your rights, provisional ballots, and 866-OUR-VOTE.</div>
            </div>
            <div class="topic-footer">
              <button class="topic-btn ask-btn" data-question="What should I do if I have a problem at my polling place in Georgia?">
                Ask this <span>↗</span>
              </button>
            </div>
          </article>
        </div>
      </section>

      <!-- CHAT / ANSWER PAGE -->
      <section class="chat-section" id="chatView">
        <header class="chat-header">
          <div class="chat-header-left">
            <strong>BallotBuddy</strong>
            <span>· Georgia voting conversation</span>
          </div>
          <div>
            <button class="chat-header-btn" id="newQuestionBtn">New question</button>
            <span style="margin-left:10px;">For urgent help call <strong>866-OUR-VOTE</strong></span>
          </div>
        </header>

        <div class="chat-window" id="chatWindow"></div>
        <div class="attached-files" id="attachedFiles"></div>

        <div class="chat-bottom">
          <form class="bottom-form" id="bottomForm">
            <button type="button" class="bottom-attach attach-btn" title="Attach files">+</button>
            <input id="bottomInput" class="bottom-input" type="text" autocomplete="off" placeholder="Ask a follow-up" />
            <button type="submit" class="bottom-send">Send</button>
          </form>
        </div>
      </section>
    </main>

    <div class="settings-fab" id="settingsIcon">⚙️</div>

    <div class="modal-backdrop" id="settingsModal">
      <div class="modal">
        <div class="modal-header">
          <span>Settings</span>
          <button class="btn-small" id="settingsClose">✕</button>
        </div>
        <div class="modal-section">
          <div class="setting-row">
            <div>
              <div class="setting-label">Theme</div>
              <div class="setting-desc">Toggle between dark and light mode.</div>
            </div>
            <div class="switch" id="themeSwitch">
              <div class="switch-handle"></div>
            </div>
          </div>
          <div class="setting-row">
            <div>
              <div class="setting-label">Auto-read answers aloud</div>
              <div class="setting-desc">Use your browser’s speaker for every reply.</div>
            </div>
            <div class="switch" id="ttsSwitch">
              <div class="switch-handle"></div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-small" id="settingsDone">Done</button>
        </div>
      </div>
    </div>
  </div>

  <script>
    const API_URL = "/api/chat";

    let messages = [];
    let pendingFiles = [];
    let autoTTS = false;
    let sending = false;

    const STATE_KEY = "ballotbuddy-ui-v5";

    const landingView = document.getElementById("landingView");
    const chatView = document.getElementById("chatView");
    const chatWindowEl = document.getElementById("chatWindow");
    const attachedFilesEl = document.getElementById("attachedFiles");

    const topForm = document.getElementById("topForm");
    const bottomForm = document.getElementById("bottomForm");
    const topInput = document.getElementById("topInput");
    const bottomInput = document.getElementById("bottomInput");
    const newQuestionBtn = document.getElementById("newQuestionBtn");

    // Hidden file input
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.multiple = true;
    fileInput.style.display = "none";
    document.body.appendChild(fileInput);

    // Theme toggle button
    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");
    const themeLabel = document.getElementById("themeLabel");

    const settingsIcon = document.getElementById("settingsIcon");
    const settingsModal = document.getElementById("settingsModal");
    const settingsClose = document.getElementById("settingsClose");
    const settingsDone = document.getElementById("settingsDone");
    const themeSwitch = document.getElementById("themeSwitch");
    const ttsSwitch = document.getElementById("ttsSwitch");

    // --- STATE PERSISTENCE (only theme + autoTTS, NOT messages) ---

    function saveState() {
      const theme = document.documentElement.getAttribute("data-theme") || "dark";
      const state = { autoTTS, theme };
      try { localStorage.setItem(STATE_KEY, JSON.stringify(state)); } catch (e) {}
    }

    function loadState() {
      try {
        const raw = localStorage.getItem(STATE_KEY);
        if (!raw) return;
        const s = JSON.parse(raw);
        autoTTS = !!s.autoTTS;
        const theme = s.theme || "dark";
        applyTheme(theme);
        updateSwitch(ttsSwitch, autoTTS);
      } catch (e) {}
    }

    function updateSwitch(el, on) {
      if (!el) return;
      if (on) el.classList.add("on"); else el.classList.remove("on");
    }

    function applyTheme(theme) {
      document.documentElement.setAttribute("data-theme", theme);
      const isLight = theme === "light";
      updateSwitch(themeSwitch, isLight);
      themeIcon.textContent = isLight ? "☀️" : "🌙";
      themeLabel.textContent = isLight ? "Light" : "Dark";
    }

    // --- RENDERING ---

    function formatMessageHtml(text) {
      if (!text) return "";
      const esc = text
        .replace(/&/g,"&amp;")
        .replace(/</g,"&lt;")
        .replace(/>/g,"&gt;");
      return esc.replace(/\n/g,"<br/>");
    }

    function renderMessages() {
      chatWindowEl.innerHTML = "";
      if (!messages.length) return;
      messages.forEach((m) => {
        const row = document.createElement("div");
        row.className = "message-row " + (m.role === "user" ? "user" : "ai");

        const bubble = document.createElement("div");
        bubble.className = "bubble";
        bubble.innerHTML = formatMessageHtml(m.content);
        row.appendChild(bubble);

        if (m.role === "assistant") {
          const meta = document.createElement("div");
          meta.className = "bubble-meta";

          const sourcesDiv = document.createElement("div");
          sourcesDiv.className = "sources";

          if (Array.isArray(m.sources) && m.sources.length) {
            m.sources.forEach(s => {
              const pill = document.createElement("span");
              pill.className = "source-pill";
              const a = document.createElement("a");
              a.href = s.url;
              a.target = "_blank";
              a.rel = "noopener noreferrer";
              a.textContent = s.name || "Source";
              pill.appendChild(a);
              sourcesDiv.appendChild(pill);
            });
          } else {
            const pill = document.createElement("span");
            pill.className = "source-pill";
            pill.textContent = "Official Georgia state election resources";
            sourcesDiv.appendChild(pill);
          }

          const actions = document.createElement("div");
          const speakBtn = document.createElement("button");
          speakBtn.className = "icon-btn";
          speakBtn.textContent = "🔊 Listen";
          speakBtn.addEventListener("click", () => speakText(m.content));
          actions.appendChild(speakBtn);

          meta.appendChild(sourcesDiv);
          meta.appendChild(actions);
          bubble.appendChild(meta);
        }

        chatWindowEl.appendChild(row);
      });
      chatWindowEl.scrollTop = chatWindowEl.scrollHeight;
    }

    function renderAttachedFiles() {
      attachedFilesEl.innerHTML = "";
      if (!pendingFiles.length) return;
      pendingFiles.forEach((f, i) => {
        const chip = document.createElement("div");
        chip.className = "file-chip";
        chip.textContent = f.name;
        const remove = document.createElement("button");
        remove.textContent = "✕";
        remove.addEventListener("click", () => {
          pendingFiles.splice(i, 1);
          renderAttachedFiles();
        });
        chip.appendChild(remove);
        attachedFilesEl.appendChild(chip);
      });
    }

    // --- VIEW SWITCHING ---

    function goToChatView() {
      landingView.style.display = "none";
      chatView.style.display = "flex";
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function goToLandingView() {
      messages = [];
      pendingFiles = [];
      renderMessages();
      renderAttachedFiles();
      chatView.style.display = "none";
      landingView.style.display = "flex";
      topInput.value = "";
      bottomInput.value = "";
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    newQuestionBtn.addEventListener("click", goToLandingView);

    // --- ATTACHMENTS ---

    document.querySelectorAll(".attach-btn").forEach(btn => {
      btn.addEventListener("click", () => fileInput.click());
    });

    fileInput.addEventListener("change", (e) => {
      pendingFiles = Array.from(e.target.files || []);
      renderAttachedFiles();
    });

    // --- TOPIC CARDS ---

    document.querySelectorAll(".ask-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const q = btn.dataset.question || "";
        topInput.value = q;
        topInput.focus();
      });
    });

    // --- FORMS ---

    function handleForm(form, input) {
      if (!form || !input) return;
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (sending) return;
        const text = input.value.trim();
        if (!text && !pendingFiles.length) return;

        messages.push({ role: "user", content: text });
        input.value = "";
        renderMessages();
        goToChatView();
        await sendToBackend();
      });
    }

    handleForm(topForm, topInput);
    handleForm(bottomForm, bottomInput);

    // --- BACKEND CALL ---

    async function sendToBackend() {
      sending = true;
      const typingMsg = { role: "assistant", content: "Thinking…", typing: true };
      messages.push(typingMsg);
      renderMessages();

      try {
        const formData = new FormData();
        formData.append("messages", JSON.stringify(messages.filter(m => !m.typing)));
        pendingFiles.forEach(f => formData.append("files", f));

        const res = await fetch(API_URL, { method: "POST", body: formData });
        const data = await res.json();

        const idx = messages.indexOf(typingMsg);
        if (idx !== -1) messages.splice(idx, 1);

        const assistantMsg = {
          role: "assistant",
          content: data.answer || "Sorry, I couldn’t generate a response.",
          sources: Array.isArray(data.sources) ? data.sources : []
        };
        messages.push(assistantMsg);
        pendingFiles = [];
        renderMessages();
        renderAttachedFiles();

        if (autoTTS) speakText(assistantMsg.content);
      } catch (err) {
        console.error(err);
        const idx = messages.indexOf(typingMsg);
        if (idx !== -1) messages.splice(idx, 1);
        messages.push({
          role: "assistant",
          content: "I’m having trouble reaching the BallotBuddy server right now. For urgent help with voting, you can call 866-OUR-VOTE."
        });
        renderMessages();
      } finally {
        sending = false;
      }
    }

    // --- TTS ---

    function speakText(text) {
      if (!("speechSynthesis" in window)) {
        alert("Your browser does not support speech synthesis.");
        return;
      }
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.rate = 1.0;
      u.pitch = 1.0;
      u.lang = "en-US";
      window.speechSynthesis.speak(u);
    }

    // --- SETTINGS / THEME ---

    function openSettings() { settingsModal.classList.add("open"); }
    function closeSettings() { settingsModal.classList.remove("open"); }

    settingsIcon.addEventListener("click", openSettings);
    settingsClose.addEventListener("click", closeSettings);
    settingsDone.addEventListener("click", closeSettings);
    settingsModal.addEventListener("click", (e) => {
      if (e.target === settingsModal) closeSettings();
    });

    themeSwitch.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      saveState();
    });

    ttsSwitch.addEventListener("click", () => {
      autoTTS = !autoTTS;
      updateSwitch(ttsSwitch, autoTTS);
      saveState();
    });

    themeToggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      saveState();
    });

    // Init
    loadState();
  </script>
</body>
</html>
"""

# ----------------- BACKEND CHAT ENDPOINT -----------------


@app.route("/")
def index():
    return render_template_string(INDEX_HTML)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Expects multipart/form-data:
      - messages: JSON list of {role: "user"/"assistant", content: str}
      - files: optional uploaded files (currently ignored, but available for future use)
    Returns:
      { "answer": str, "sources": [{ "name": str, "url": str }, ...] }
    """
    try:
        messages_raw = request.form.get("messages", "[]")
        user_messages = json.loads(messages_raw)
    except Exception:
        user_messages = []

    system_prompt = (
        "You are BallotBuddy, an AI assistant that ONLY answers questions "
        "about voting in the U.S. state of Georgia.\n\n"
        "STYLE:\n"
        "- Answer in clear, professional markdown.\n"
        "- Start with a short 1–2 sentence overview.\n"
        "- Then provide a numbered list of steps or key points.\n"
        "- Use bullets for sub-points and keep sentences concise.\n"
        "- Avoid giant paragraphs; break information into sections.\n\n"
        "CONTENT RULES:\n"
        "1. Answer only Georgia voting, elections, registration, voter ID, "
        "polling places, absentee/early voting, and related civic-process questions.\n"
        "2. Base your answers on information that can be sourced from accredited "
        "Georgia government websites, such as the Georgia Secretary of State "
        "Election Division (sos.ga.gov), the 'My Voter Page' portal (mvp.sos.ga.gov), "
        "and Georgia.gov.\n"
        "3. Always note that rules and dates can change and encourage the user to "
        "confirm details on official Georgia election websites.\n"
        "4. If the question is outside Georgia voting, politely refuse and say you "
        "only handle Georgia voting information.\n"
        "5. If you are unsure, say so and point the user to official Georgia "
        "election offices or the My Voter Page.\n"
    )

    chat_messages = [{"role": "system", "content": system_prompt}]
    for m in user_messages:
        if m.get("role") in ("user", "assistant"):
            chat_messages.append({"role": m["role"], "content": m.get("content", "")})

    try:
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=chat_messages,
            temperature=0.3,
        )
        answer_text = completion.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        return jsonify(
            {
                "answer": (
                    "I’m having trouble contacting the BallotBuddy model right now. "
                    "For urgent help with voting, please contact your local election office "
                    "or call the non-partisan voter hotline at 866-OUR-VOTE."
                ),
                "sources": [],
            }
        )

    # Provide a default set of official links
    sources = [
        {
            "name": "Georgia Secretary of State – Elections",
            "url": "https://sos.ga.gov/elections",
        },
        {
            "name": "Georgia My Voter Page (MVP)",
            "url": "https://mvp.sos.ga.gov/",
        },
        {
            "name": "Georgia DDS – Free Voter ID",
            "url": "https://dds.georgia.gov/voter-id",
        },
    ]

    return jsonify({"answer": answer_text, "sources": sources})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)

