---
date: 2026-03-18
title: "It never is just a button: concerns when running code in someone else's computer"
slug: concerns-when-running-code-in-someone-elses-computer
authors:
    - dodge
categories:
    - Tech
tags:
    - anonymity
    - fingerprinting
    - privacy
---

> — "There was a button", Holden said. "I pushed it."  
> — Jesus Christ. That really is how you go through life, isn't it?

## Introduction

Ever since JavaScript was introduced, we have had concerns with security issues leading to the current patchwork
of rules, headers and sandbox that browsers have had to implement reactively. After billions of dollars invested,
we have billions of devices running the best sandbox ever which is Chromium's V8. But will that ever be enough? Will
this cat and mouse game ever end? If not, why?

<!-- more -->

## POC - What's The Hello World of RCE vulnerabilities

![Albanian Virus Meme](./albanian-virus-meme.png)

In programming, we have the "Hello World" as the canonical example of a first working program. In electronics, the
equivalent is to make an LED blink. In the context of web security, what's the equivalent Remote Code Execution?

## MVP - Blink Bookmarklet

Have you heard of [bookmarklets](https://en.wikipedia.org/wiki/Bookmarklet)? If not, even better, I'd say. No need to
even look it up because, well, this is a demo post and I'll guide you through it. Honestly I'd even appreciate it
if you don't look it up just yet. Just drag this Hello World link to your bookmarks bar and add it as a new bookmark,
please:

<a href="javascript:(function()%7Balert(%60%5Cu%7B1F4A1%7D%20Hello%20World%20from%20%24%7Bwindow.location.origin%7D%60)%3B%7D)()%3B">📴 Hello World</a>

Like this:

![Add Bookmark screenshot](./bookmarklet-v0-add-bookmark.png)

Now click
