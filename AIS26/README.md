# AIS26 Conference Archive

AI Summit Seoul 2026 컨퍼런스 기록 저장소입니다.

이 폴더에는 프로그램, 실시간 통역 전체본, 10분 단위 통역 조각, 오전 세션 요약본, 오후 세션 기록, 자동 저장 스크립트가 정리되어 있습니다.

## 먼저 볼 파일

| 파일 | 내용 |
| --- | --- |
| [`program.md`](./program.md) | 컨퍼런스 프로그램 |
| [`morning-session-summary_ko.md`](./morning-session-summary_ko.md) | 오전 세션 통합 요약 한글본 |
| [`morning-session-summary_en.md`](./morning-session-summary_en.md) | 오전 세션 통합 요약 영문본 |
| [`live-translation-10am.md`](./live-translation-10am.md) | 오전 실시간 통역 전체본 |
| [`afternoon-session/live-translation-afternoon.md`](./afternoon-session/live-translation-afternoon.md) | 오후 실시간 통역 전체본 |

## 요약 파일

| 파일 | 구간 | 설명 |
| --- | --- | --- |
| [`interim-summary_ko.md`](./interim-summary_ko.md) | 오전 초반-10:38 KST | 중간요약 1 한글본 |
| [`interim-summary_en.md`](./interim-summary_en.md) | 오전 초반-10:38 KST | 중간요약 1 영문본 |
| [`interim-summary-2_ko.md`](./interim-summary-2_ko.md) | 11:00-12:00 KST | 중간정리 2 한글본 |
| [`interim-summary-2_en.md`](./interim-summary-2_en.md) | 11:00-12:00 KST | 중간정리 2 영문본 |
| [`morning-session-summary_ko.md`](./morning-session-summary_ko.md) | 오전 전체 | 중간요약 1, 2를 묶은 오전 통합본 한글 |
| [`morning-session-summary_en.md`](./morning-session-summary_en.md) | 오전 전체 | 중간요약 1, 2를 묶은 오전 통합본 영문 |

## 실시간 통역 기록

| 파일/폴더 | 설명 |
| --- | --- |
| [`live-translation-10am.md`](./live-translation-10am.md) | 오전 세션 실시간 통역 전체 누적본 |
| [`chunks/`](./chunks/) | 오전 통역 내용을 10분 단위로 나눈 조각 파일 |
| [`chunks/latest-10min.md`](./chunks/latest-10min.md) | 오전 기준 마지막 10분 구간 |
| [`afternoon-session/`](./afternoon-session/) | 오전 자료와 분리한 오후 세션 전용 폴더 |
| [`afternoon-session/live-translation-afternoon.md`](./afternoon-session/live-translation-afternoon.md) | 오후 세션 실시간 통역 전체 누적본 |
| [`afternoon-session/chunks/`](./afternoon-session/chunks/) | 오후 통역 내용을 10분 단위로 나눌 조각 파일 |
| [`afternoon-session/chunks/latest-10min.md`](./afternoon-session/chunks/latest-10min.md) | 오후 기준 최신 10분 구간 |

## 스크립트

| 파일 | 설명 |
| --- | --- |
| [`script/livetr-capture-skill.md`](./script/livetr-capture-skill.md) | LiveTR 캡처와 GitHub 동기화 절차 문서 |
| [`script/livetr-capture.mjs`](./script/livetr-capture.mjs) | LiveTR WebSocket에서 실시간 통역 메시지를 캡처하는 Node.js 스크립트 |
| [`script/Sync-LiveTrToGitHub.ps1`](./script/Sync-LiveTrToGitHub.ps1) | 최신 통역본을 GitHub 저장소로 복사하고 10분 조각 파일을 생성, 푸시하는 PowerShell 스크립트 |

## 운영 방식

- LiveTR 원본 채팅방을 캡처해 실시간 통역본을 유지합니다.
- 오전 세션은 `live-translation-10am.md`와 `chunks/`에 저장했습니다.
- 오후 세션은 13:00 KST 이후 내용만 `afternoon-session/live-translation-afternoon.md`와 `afternoon-session/chunks/`에 저장합니다.
- 10분마다 최신 전체본과 10분 단위 조각 파일을 GitHub에 자동 푸시합니다.
- 발표 내용을 빠르게 파악하려면 요약본을 먼저 보고, 세부 발언 흐름은 실시간 통역본을 확인하면 됩니다.

## 공유용 추천 링크

- AIS26 폴더: <https://github.com/KevinFire2030/ax/tree/main/AIS26>
- 프로그램: <https://github.com/KevinFire2030/ax/blob/main/AIS26/program.md>
- 오전 세션 통합본 한글: <https://github.com/KevinFire2030/ax/blob/main/AIS26/morning-session-summary_ko.md>
- 오전 세션 통합본 영문: <https://github.com/KevinFire2030/ax/blob/main/AIS26/morning-session-summary_en.md>
- 오전 실시간 통역본: <https://github.com/KevinFire2030/ax/blob/main/AIS26/live-translation-10am.md>
- 오후 세션 폴더: <https://github.com/KevinFire2030/ax/tree/main/AIS26/afternoon-session>
- 오후 실시간 통역본: <https://github.com/KevinFire2030/ax/blob/main/AIS26/afternoon-session/live-translation-afternoon.md>
