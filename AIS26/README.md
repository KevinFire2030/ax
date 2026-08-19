# AIS26 Conference Archive

AI Summit Seoul 2026 Day 1 오전 세션 기록 저장소입니다.

이 폴더에는 실시간 통역 전체본, 10분 단위 조각본, 오전 세션 요약본, 프로그램표, 그리고 LiveTR 캡처/동기화 스크립트가 함께 저장되어 있습니다.

## 먼저 볼 파일

| 파일 | 내용 |
| --- | --- |
| [`morning-session-summary_ko.md`](./morning-session-summary_ko.md) | 오전 세션 통합 요약 한글본 |
| [`morning-session-summary_en.md`](./morning-session-summary_en.md) | 오전 세션 통합 요약 영문본 |
| [`program.md`](./program.md) | 2026년 8월 19일 오전 컨퍼런스 일정표 |
| [`live-translation-10am.md`](./live-translation-10am.md) | LiveTR 실시간 통역 전체 누적본 |
| [`chunks/latest-10min.md`](./chunks/latest-10min.md) | 가장 최근 10분 구간 통역 내용 |

## 요약 파일

| 파일 | 구간 | 설명 |
| --- | --- | --- |
| [`interim-summary_ko.md`](./interim-summary_ko.md) | 오전 초반-10:38 KST | 중간요약 1 한글본 |
| [`interim-summary_en.md`](./interim-summary_en.md) | 오전 초반-10:38 KST | 중간요약 1 영문본 |
| [`interim-summary-2_ko.md`](./interim-summary-2_ko.md) | 11:00-12:00 KST | 중간정리 2 한글본 |
| [`interim-summary-2_en.md`](./interim-summary-2_en.md) | 11:00-12:00 KST | 중간정리 2 영문본 |
| [`morning-session-summary_ko.md`](./morning-session-summary_ko.md) | 오전 전체 | 중간요약 1, 2를 묶은 통합본 한글 |
| [`morning-session-summary_en.md`](./morning-session-summary_en.md) | 오전 전체 | 중간요약 1, 2를 묶은 통합본 영문 |

## 원문 통역 기록

| 파일/폴더 | 설명 |
| --- | --- |
| [`live-translation-10am.md`](./live-translation-10am.md) | LiveTR 채팅방에서 수집한 실시간 통역 전체 누적본 |
| [`chunks/`](./chunks/) | 전체 통역 내용을 10분 단위로 나눈 조각 파일 |
| [`chunks/README.md`](./chunks/README.md) | 10분 단위 조각 파일 목차 |
| [`chunks/latest-10min.md`](./chunks/latest-10min.md) | 가장 최근 10분 구간만 빠르게 확인하는 파일 |

## 10분 단위 조각 파일

`chunks/HHmm-HHmm.md` 형식으로 저장됩니다.

예시:

- [`chunks/0900-0910.md`](./chunks/0900-0910.md)
- [`chunks/1100-1110.md`](./chunks/1100-1110.md)
- [`chunks/1150-1200.md`](./chunks/1150-1200.md)
- [`chunks/1200-1210.md`](./chunks/1200-1210.md)

최근 내용을 빠르게 보려면 [`chunks/latest-10min.md`](./chunks/latest-10min.md)를 열면 됩니다.

## 스크립트

| 파일 | 설명 |
| --- | --- |
| [`script/livetr-capture-skill.md`](./script/livetr-capture-skill.md) | LiveTR 캡처와 GitHub 동기화 절차를 정리한 스킬 문서 |
| [`script/livetr-capture.mjs`](./script/livetr-capture.mjs) | LiveTR WebSocket에서 실시간 통역 메시지를 캡처하는 Node.js 스크립트 |
| [`script/Sync-LiveTrToGitHub.ps1`](./script/Sync-LiveTrToGitHub.ps1) | 최신 통역본을 GitHub 저장소에 복사하고 10분 조각 파일을 생성/푸시하는 PowerShell 스크립트 |

## 운영 방식

- LiveTR 원본 채팅방을 캡처해 전체 통역본을 유지합니다.
- 10분마다 최신 전체본과 10분 단위 조각 파일을 GitHub에 동기화합니다.
- 전체 내용을 보려면 `live-translation-10am.md`를 확인합니다.
- 최근 내용만 빠르게 보려면 `chunks/latest-10min.md`를 확인합니다.
- 발표 내용을 빠르게 파악하려면 `morning-session-summary_ko.md` 또는 `morning-session-summary_en.md`를 먼저 확인합니다.

## 공유용 추천 링크

- AIS26 폴더: <https://github.com/KevinFire2030/ax/tree/main/AIS26>
- 오전 세션 통합본 한글: <https://github.com/KevinFire2030/ax/blob/main/AIS26/morning-session-summary_ko.md>
- 오전 세션 통합본 영문: <https://github.com/KevinFire2030/ax/blob/main/AIS26/morning-session-summary_en.md>
- 전체 실시간 통역본: <https://github.com/KevinFire2030/ax/blob/main/AIS26/live-translation-10am.md>
- 10분 단위 조각 목차: <https://github.com/KevinFire2030/ax/tree/main/AIS26/chunks>
