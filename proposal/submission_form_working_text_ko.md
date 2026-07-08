# 공식 제출 양식 작업본

이 문서는 `proposal/proposal_draft_ko.md`를 공식 제출 양식에 옮기기 쉽게 재구성한 작업본이다. 공개 GitHub에 남겨도 되는 수준의 내용만 포함하며, 실제 HWPX/HWP/PDF 제출 파일은 로컬에서 별도로 작성한다.

## 기본 정보

선택 분야:

- 3번 분야: 규제 대응 및 지능형 임상시험 설계

팀명:

- MedIT Agent Lab

에이전트명:

- Clinical Trial Protocol Review Agent
- 임상시험 프로토콜 사전검토 에이전트

국문 키워드:

- 임상시험 프로토콜
- 의료정보
- 병원 데이터
- 근거 기반 검토
- 에이전트 AI

영문 키워드:

- Clinical Trial Protocol
- Medical IT
- Hospital Data Readiness
- Evidence-Based Review
- Agentic AI

## 요약

본 제안은 초기 임상시험 프로토콜 초안을 대상으로 프로토콜 구성요소, 공개 임상시험 사례, 대상자 적격성 및 모집 가능성 가정, 안전성 검토 항목, 병원 데이터 수집 가능성을 단계적으로 점검하는 에이전트 AI 시스템을 제안한다. 본 시스템은 임상시험 승인, 규제 적합성 보증, 환자별 진단 또는 치료 추천을 수행하지 않는다. 대신 PI, CRC, 의뢰자, IRB/규제 담당자, 통계 및 의료 데이터 담당자의 전문가 검토 전에 누락, 불명확성, 근거 부족, 데이터 수집 준비도 위험을 추적 가능한 사전검토 패킷으로 정리한다.

현재 MVP는 공개 ClinicalTrials.gov API, 프로토콜 체크리스트, 병원 데이터 카테고리 매핑, 안전성 검토자 루프를 결합한 Python CLI 형태로 구현되어 있다. 입력과 산출물은 합성 시나리오와 공개 근거만 사용하며, JSON/Markdown 형태로 저장되어 GitHub에서 재현성과 검토 과정을 확인할 수 있다.

## 1. 신약개발 과정에서의 에이전트 활용 필요성 및 배경

임상시험 프로토콜은 후보 의약품이 사람을 대상으로 평가되는 단계에서 핵심적인 실행 문서이다. 초기 프로토콜 초안은 과학적 근거, 임상시험 설계, 대상자 선정 기준, 제외 기준, 주요 평가변수, 안전성 모니터링, 모집 가정, 방문 일정, 데이터 수집 항목, 연구 문서화 요구사항을 함께 고려해야 한다. 이 중 일부 항목이 누락되거나 불명확하면 이후 전문가 검토, 의뢰자 검토, IRB/규제 검토, 연구 수행 준비 과정에서 반복적인 보완 작업이 발생할 수 있다.

본 프로젝트의 문제정의는 다음과 같다.

> 초기 임상시험 프로토콜 초안은 전문가 검토 전에 프로토콜 완성도, 공개 근거, 유사 임상시험 패턴, 대상자 적격성 및 모집 가정, 안전성 고려사항, 병원 데이터 수집 가능성을 추적 가능한 방식으로 사전 점검할 필요가 있다.

이 문제는 신약개발 과정 중 임상시험 설계 및 운영 준비 단계와 직접 연결된다. 특히 의료IT 관점에서는 프로토콜의 데이터 항목이 병원정보시스템, EMR/EHR 유래 데이터, 연구 전용 eCRF, 수기 확인 문서, 검사 결과, 투약 기록, 방문 일정 관리 등과 연결될 수 있는지가 중요하다.

ICH E6(R3) Good Clinical Practice는 임상시험이 참여자 보호와 신뢰 가능한 결과 생성을 위해 적절히 설계되고 수행되어야 함을 강조한다. SPIRIT 2025는 프로토콜 보고를 위한 구조화된 체크리스트를 제공하며, 연구 배경, 목적, 대상자 선정 기준, 중재, 결과변수, 위해 및 안전성, 표본 수, 모집 계획 등이 체계적으로 포함되어야 함을 보여준다. 따라서 본 에이전트의 프로토콜 체크리스트 기능은 단순 문서 교정이 아니라, 인정된 프로토콜 보고 기대사항에 기반한 사전 점검 기능이다.

모집과 대상자 적격성도 실제 임상시험 운영에서 중요한 문제이다. Treweek 등의 연구는 무작위 임상시험 모집이 어렵고 모집 개선 전략의 근거 수준도 다양하다고 보고하였다. Botto, Smith, Getz의 2024년 연구는 프로토콜 변경과 모집 및 유지 장벽이 실제 성과 문제와 연결될 수 있음을 보여준다. 따라서 본 시스템은 모집 성공을 보장하는 것이 아니라, 초기 단계에서 모집 가정과 대상자 적격성 조건을 전문가가 검토해야 할 위험 항목으로 표시한다.

의료IT 측면에서도 이 문제는 현실적이다. EHR 기반 자동 대상자 적격성 선별 연구와 clinical trial eligibility query 관련 연구는 대상자 적격성 기준을 실제 데이터 질의나 구조화된 데이터 항목으로 변환하는 과정이 단순하지 않음을 보여준다. 구조화 데이터뿐 아니라 비정형 임상 서술, 시간 조건, 문맥 정보가 필요할 수 있으므로, 프로토콜의 데이터 수집 가능성과 병원 데이터 수집 준비도를 조기에 점검하는 기능은 실제 현장 문제와 연결된다.

## 2. 에이전트 설계, 독창성 및 창의성

본 시스템은 단일 챗봇이 아니라 임상시험 프로토콜 사전검토라는 좁은 업무 흐름에 맞춘 다중 에이전트 검토자이다. 사용자가 초기 프로토콜 초안을 입력하면, 에이전트는 입력 정규화, 체크리스트 검토, 공개 임상시험 레지스트리 검색, 병원 데이터 수집 준비도 매핑, 안전성 검토자 점검, 최종 보고서 생성을 단계적으로 수행한다.

| 역할 | 주요 기능 | 산출물 |
| --- | --- | --- |
| Input Normalizer | 프로토콜 초안을 구조화하고 사용자 가정과 외부 근거를 분리 | `normalized_input.json` |
| Protocol Checklist Agent | 질환, 중재, phase, 대상자, 적격성 기준, endpoint, 안전성, 표본 수 등 핵심 항목 점검 | `checklist_findings.json` |
| Trial Case / Evidence Agent | ClinicalTrials.gov에서 유사 공개 임상시험을 검색하고 관련성 순위화 수행 | `sources.json`, `sources_ranked.json` |
| Hospital Data Readiness Agent | 필요한 데이터 항목을 병원/연구 데이터 카테고리로 매핑 | `data_readiness.json`, `data_readiness_table.md` |
| Critic / Safety Agent | 승인, 규제 보증, 치료 추천, 실제 환자 데이터 사용 등 위험 표현 점검 | `critic_review.md` |
| Final Report Agent | 전문가 검토 전 pre-review packet 생성 | `final_report.md` |

본 제안의 독창성은 의료 챗봇을 만드는 것이 아니라, 임상시험 설계 및 병원 데이터 준비라는 좁은 고부가가치 업무 흐름을 에이전트 AI로 분해했다는 점이다. 시스템은 입력 프로토콜을 구조화하고, 누락 및 불명확 항목을 규칙 기반으로 점검하며, 공개 임상시험 레지스트리에서 유사 사례를 가져오고, 검색 결과를 중복 제거 및 관련성 순위화한 뒤, 병원 데이터 항목을 routine system, mixed, research-only/manual로 분류한다. 이후 검토자 루프로 위험 표현을 점검하고 최종 사전검토 보고서를 생성한다.

또한 본 시스템은 모든 입력에 대해 동일한 답변을 생성하지 않는다. 질환명 또는 중재 개념이 누락되면 clarification question을 생성하고, 검색 결과가 적거나 관련성이 낮으면 대표 약물명, drug class, 동의어로 query expansion을 수행한다. 데이터 항목이 research-only/manual에 가까우면 데이터 수집 준비도 위험으로 표시하고, 최종 보고서가 승인, 규제 보증, 치료 추천 표현을 포함하면 검토자 루프에서 수정 대상으로 표시한다.

## 3. 기술적 실현 가능성

현재 MVP는 표준 라이브러리 기반 Python CLI로 구현되어 있다. 별도의 API key나 외부 Python package 없이 실행 가능하며, 공개 ClinicalTrials.gov API를 사용해 유사 임상시험 정보를 조회한다.

현재 구현된 주요 파일은 다음과 같다.

- `prototype/run_scenario.py`
- `prototype/inputs/scenario_001.json`
- `prototype/runs/scenario_001_run_001/final_report.md`
- `prototype/runs/scenario_001_run_001/score.md`
- `prototype/runs/scenario_001_run_001/medical_plausibility_safety_review.md`

현재 Scenario 001은 제2형 당뇨병과 GLP-1 receptor agonist add-on therapy를 가정한 합성 Phase II 프로토콜 초안이다. 이 시나리오에서 시스템은 HbA1c 적격성 기준, 신기능 저하 제외 기준, 연구 설계, 모집 가정, 주사제 치료 제외 기준, 안전성 모니터링, 기존 GLP-1 사용 이력, 이상반응 수집 업무 흐름 등의 누락 또는 불명확 항목을 검출했다.

| 데이터/API | 현재 활용 | 향후 확장 |
| --- | --- | --- |
| ClinicalTrials.gov API v2 | 유사 임상시험 검색, NCT ID 및 trial metadata 저장 | 질의 확장, endpoint/적격성 기준 추출 개선 |
| NCBI E-utilities / PubMed | 근거 조사 문서화에 사용 | PubMed evidence retrieval agent로 확장 |
| SPIRIT, ICH, FDA, WHO 자료 | 설계 근거 및 안전 boundary 정의 | checklist rule로 구조화 |
| DailyMed | Scenario 001 안전성 검토에 사용 | 약물 class별 safety lookup 확장 |

최종 라운드 데모는 현재 CLI MVP를 유지하면서 필요한 경우 얇은 UI를 추가하는 방식이 적절하다. 핵심은 화려한 화면보다 에이전트 단계, 근거 추적 기록, 한계, 검토자 결과가 재현 가능하게 남는 것이다. MVP 단계에서는 외부 의존성을 최소화하고, 최종 라운드에서는 시각화가 필요한 부분만 UI로 감싼다.

본 제안은 새로운 의료 foundation model 학습, 실제 EMR/HIS 직접 연동, 실제 환자 데이터 처리, private sponsor data 접근, 자동 IRB/규제 제출, 실제 프로토콜 승인 또는 거절 판단을 요구하지 않는다. 따라서 제한된 자원 안에서도 공개 API, 로컬 규칙, Markdown/JSON 추적 기록, 합성 시나리오를 이용해 MVP와 포트폴리오 데모를 구현할 수 있다.

## 4. 에이전트 평가 계획

본 에이전트는 임상 권위자가 아니라 pre-review assistant로 평가해야 한다. 따라서 평가 기준은 임상적 유효성 입증이 아니라, 사전검토 업무에서 필요한 항목을 얼마나 일관되게 식별하고, 근거와 한계를 얼마나 명확히 남기는지에 맞춘다.

| 시나리오 | 도메인 | 목적 |
| --- | --- | --- |
| Scenario 001 | 제2형 당뇨병 / GLP-1 receptor agonist | 현재 구현된 기준 시나리오 |
| Scenario 002 | 종양 또는 심혈관계 Phase II/III 프로토콜 | 복잡한 적격성 기준, 병용약물, 안전성 모니터링 조건 검출 |
| Scenario 003 | 감염성 질환 또는 희귀질환 프로토콜 | 모집 수행 가능성, 방문 일정, 연구 전용 데이터 수집 항목 검출 |

평가 지표는 프로토콜 완성도 검출, 대상자 적격성 및 모집 위험 검출, 근거 검색 적절성, 병원 데이터 수집 준비도 매핑, safety boundary 준수, 추적 가능성으로 구성한다. 현재 Scenario 001의 수동 루브릭 점수는 100/100이다. 다만 이 점수는 합성 시나리오와 사전 정의 루브릭에 대한 내부 검증 결과이며, 실제 임상적 타당성이나 실제 배포 가능성을 의미하지 않는다.

## 5. 최종 라운드 데모 시나리오

최종 라운드에서는 병원 임상연구 지원팀이 초기 Phase II 프로토콜 초안을 검토하는 장면을 가정한다. 사용자는 구조화된 프로토콜 초안을 입력하고, 시스템은 agent step을 순서대로 보여준다.

데모 흐름은 다음과 같다.

1. 사용자가 합성 프로토콜 초안을 선택하거나 입력한다.
2. Input Normalizer가 질환, 중재, phase, objective, 대상자, 적격성 기준, endpoint, data item을 구조화한다.
3. Protocol Checklist Agent가 누락 및 불명확 항목을 표시한다.
4. Trial Case / Evidence Agent가 ClinicalTrials.gov에서 유사 임상시험을 검색한다.
5. 검색 결과를 NCT ID 기준으로 중복 제거하고 relevance ranking한다.
6. Hospital Data Readiness Agent가 데이터 항목을 병원/연구 데이터 카테고리로 분류한다.
7. Critic / Safety Agent가 과장 표현과 안전 boundary 위반을 점검한다.
8. Final Report Agent가 pre-review packet을 생성한다.
9. 시스템이 루브릭 점수, 근거 추적 기록, 한계를 함께 보여준다.

데모 화면에는 에이전트 업무 흐름 단계, 검색한 공개 근거와 NCT ID, 누락 및 불명확 항목 리스트, similar-trial comparison table, 병원 데이터 수집 준비도 표, 안전성 검토자 결과, 최종 pre-review report를 표시한다. 또한 합성 입력, 공개 근거만 사용, 실제 환자 데이터 미사용, 전문가 검토 필요 경계를 명확히 표시한다.

## 6. 기대효과, 윤리 및 적용 경계

본 시스템의 기대효과는 clinical decision automation이 아니라, 임상시험 준비 문서화와 전문가 검토 전 정리 과정의 품질을 높이는 것이다.

| 구분 | 현재 수작업 중심 흐름 | 제안 시스템 적용 후 흐름 |
| --- | --- | --- |
| 프로토콜 초안 검토 | 담당자가 문서를 직접 읽고 누락 항목을 개별 메모 | 체크리스트 기반 누락/불명확 항목 자동 정리 |
| 유사 임상시험 확인 | ClinicalTrials.gov 또는 문헌을 수동 검색 | 공개 임상시험 레지스트리 질의와 근거 추적 기록 자동 저장 |
| 병원 데이터 가능성 논의 | 회의 중 경험 기반으로 데이터 가능성 추정 | routine, mixed, research-only/manual 항목으로 1차 분류 |
| 안전성 및 한계 점검 | 담당자 경험에 의존 | 검토자 루프로 승인/치료추천/규제보증 표현 사전 차단 |
| 전문가 follow-up | 흩어진 메모를 바탕으로 질문 작성 | PI, CRC, 데이터 담당자에게 전달할 질문 목록 생성 |

주요 대상 사용자는 병원 임상연구 지원팀, 임상연구 코디네이터, 의료IT 및 데이터 지원 담당자, 초기 임상시험 프로토콜 기획팀, AI 기반 신약개발 업무 흐름을 검토하는 평가자이다.

본 시스템은 임상시험 프로토콜 승인, 규제 적합성 인증, 환자별 진단 또는 치료 추천, 실제 환자 적격성 판정, 실제 EMR/HIS 데이터 접근, 전문가 검토 대체를 수행하지 않는다. WHO의 AI for health ethics guidance와 FDA Clinical Decision Support Software guidance를 고려할 때, 의료 영역의 AI는 명확한 책임 경계와 인간 전문가 검토 가능성을 유지해야 한다. 따라서 본 시스템은 전문가 판단을 대체하지 않고, 검토 전 준비자료를 구조화하는 역할로 제한한다.

향후 확장은 Scenario 002와 Scenario 003 추가, PubMed/NCBI E-utilities 기반 evidence retrieval 추가, SPIRIT/ICH 기반 체크리스트 구조화, 재현성을 유지한 UI 추가 순서로 진행한다. 실제 병원 시스템 연동은 formal governance, IRB/기관 검토, privacy/security review, 전문가 검증 이후의 장기 과제로 둔다.

## 참고문헌

1. International Council for Harmonisation. ICH E6(R3) Good Clinical Practice, final guideline. Adopted 2025-01-06. URL: https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf
2. SPIRIT-CONSORT. SPIRIT 2025 protocol checklist and related materials. URL: https://www.consort-spirit.org/
3. ClinicalTrials.gov. ClinicalTrials.gov Data API documentation. URL: https://clinicaltrials.gov/data-api/about-api
4. National Center for Biotechnology Information. Entrez Programming Utilities Help. URL: https://www.ncbi.nlm.nih.gov/books/NBK25501/
5. Treweek S, Pitkethly M, Cook J, et al. Strategies to improve recruitment to randomised trials. Cochrane Database of Systematic Reviews. 2018. PMID: 29468635. DOI: 10.1002/14651858.MR000013.pub6
6. Botto E, Smith Z, Getz K. New Benchmarks on Protocol Amendment Experience in Oncology Clinical Trials. Therapeutic Innovation & Regulatory Science. 2024. PMID: 38530628. DOI: 10.1007/s43441-024-00629-2
7. Ni Y, Bermudez M, Kennebeck S, Liddy-Hicks S, Dexheimer J. A Real-Time Automated Patient Screening System for Clinical Trials Eligibility in an Emergency Department: Design and Evaluation. JMIR Medical Informatics. 2019. PMID: 31342909. DOI: 10.2196/14185
8. World Health Organization. Ethics and governance of artificial intelligence for health. 2021. URL: https://www.who.int/publications/i/item/9789240029200
9. U.S. Food and Drug Administration. Clinical Decision Support Software Guidance for Industry and FDA Staff. URL: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software

## 제출 전 확인 필요

- 공식 양식의 글자 수, 표 크기, 페이지 분량에 맞게 축약
- Mermaid 다이어그램을 이미지로 변환할지 결정
- HWPX/HWP 파일에 팀명, 에이전트명, 키워드, 본문이 올바르게 들어갔는지 확인
- 개인정보 또는 연락처가 GitHub에 커밋되지 않았는지 확인
- 최종 파일이 임상 승인, 규제 보증, 치료 추천을 암시하지 않는지 확인
