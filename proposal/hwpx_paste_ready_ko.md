# HWPX 붙여넣기용 최종 원고

이 문서는 `[데이콘]AI_신약개발_경진대회_제안서.pdf` 양식의 항목 순서에 맞춰 작성한 붙여넣기용 원고이다. 한글 HWPX 양식에 직접 붙여넣는 것을 전제로 하며, 최종 제출 전에는 양식의 `[참고사항 삭제 후 제출]` 문구 삭제, 10쪽 이내 여부, 표 깨짐 여부를 반드시 확인해야 한다.

## 기본 정보

선택분야:
3번 분야: 규제 대응 및 지능형 임상 설계

팀 명:
MedIT Agent Lab

에이전트명:
Clinical Trial Protocol Review Agent / 임상시험 프로토콜 사전검토 에이전트

키워드 - 국문:
임상시험 프로토콜, 의료정보, 병원 데이터, 근거 기반 검토, 에이전트 AI

키워드 - 영문:
Clinical Trial Protocol, Medical IT, Hospital Data Readiness, Evidence-Based Review, Agentic AI

## 요약

본 제안은 초기 임상시험 프로토콜 초안을 대상으로 프로토콜 구성요소, 공개 임상시험 사례, 대상자 적격성 및 모집 가능성 가정, 안전성 검토 항목, 병원 데이터 수집 가능성을 단계적으로 점검하는 에이전트 AI 시스템을 제안한다. 본 시스템은 임상시험 승인, 규제 적합성 보증, 환자별 진단 또는 치료 추천을 수행하지 않는다. 대신 PI, CRC, 의뢰자, IRB/규제 담당자, 통계 및 의료 데이터 담당자의 전문가 검토 전에 누락, 불명확성, 근거 부족, 데이터 수집 준비도 위험을 추적 가능한 사전검토 패킷으로 정리한다. MVP는 공개 ClinicalTrials.gov API, 체크리스트, 병원 데이터 카테고리 매핑, 안전성 검토자 루프를 결합한 Python CLI로 구현되어 있으며, 합성 시나리오와 공개 근거만 사용한다.

## 1. 신약개발에서의 에이전트 활용의 필요성과 배경

임상시험 프로토콜은 후보 의약품이 사람을 대상으로 평가되는 단계의 핵심 실행 문서이다. 초기 초안은 과학적 근거, 임상시험 설계, 대상자 선정 및 제외 기준, 주요 평가변수, 안전성 모니터링, 모집 가정, 방문 일정, 데이터 수집 항목, 연구 문서화 요구사항을 함께 고려해야 한다. 일부 항목이 누락되거나 불명확하면 이후 전문가 검토, 의뢰자 검토, IRB/규제 검토, 연구 수행 준비 과정에서 반복 보완이 발생할 수 있다.

본 프로젝트의 문제정의는 다음과 같다.

초기 임상시험 프로토콜 초안은 전문가 검토 전에 프로토콜 완성도, 공개 근거, 유사 임상시험 패턴, 대상자 적격성 및 모집 가정, 안전성 고려사항, 병원 데이터 수집 가능성을 추적 가능한 방식으로 사전 점검할 필요가 있다.

이 문제는 신약개발 중 임상시험 설계 및 운영 준비 단계와 직접 연결된다. 특히 의료IT 관점에서는 프로토콜의 데이터 항목이 병원정보시스템, EMR/EHR 유래 데이터, 연구 전용 eCRF, 수기 확인 문서, 검사 결과, 투약 기록, 방문 일정 관리와 연결될 수 있는지가 중요하다.

근거도 존재한다. ICH E6(R3)는 임상시험이 참여자 보호와 신뢰 가능한 결과 생성을 위해 적절히 설계되고 수행되어야 함을 강조하며, SPIRIT 2025는 프로토콜 보고 항목을 구조화된 체크리스트로 제시한다. Treweek 등의 연구는 임상시험 모집이 실제 운영상 어려운 문제임을 보여주고, Botto, Smith, Getz의 2024년 연구는 프로토콜 변경과 모집 및 유지 장벽이 실제 성과 문제와 연결될 수 있음을 제시한다. 또한 EHR 기반 대상자 적격성 선별 연구와 trial eligibility query 관련 연구는 프로토콜 기준을 병원 데이터 질의로 변환하는 과정이 단순하지 않음을 보여준다.

따라서 본 시스템은 모집 성공이나 규제 적합성을 보장하지 않고, 전문가가 조기에 확인해야 할 누락, 불명확성, 근거 부족, 데이터 수집 준비도 위험을 표시하는 사전검토 도구로 제한한다.

## 2. 에이전트 설계 및 설계의 독창성과 창의성

본 시스템은 단일 챗봇이 아니라 임상시험 프로토콜 사전검토라는 좁은 업무 흐름에 맞춘 다중 에이전트 검토자이다. 사용자가 초기 프로토콜 초안을 입력하면 입력 정규화, 체크리스트 검토, 공개 임상시험 레지스트리 검색, 병원 데이터 수집 준비도 매핑, 안전성 검토자 점검, 최종 보고서 생성을 단계적으로 수행한다.

에이전트 구성은 다음과 같다.

- Input Normalizer: 프로토콜 초안을 구조화하고 사용자 가정과 외부 근거를 분리한다.
- Protocol Checklist Agent: 대상자, 적격성 기준, endpoint, 안전성, 표본 수 등 핵심 항목을 점검한다.
- Trial Case / Evidence Agent: ClinicalTrials.gov에서 유사 공개 임상시험을 검색하고 관련성 순위화를 수행한다.
- Hospital Data Readiness Agent: 필요한 데이터 항목을 병원/연구 데이터 카테고리로 매핑한다.
- Critic / Safety Agent: 승인, 규제 보증, 치료 추천, 실제 환자 데이터 사용 등 위험 표현을 점검한다.
- Final Report Agent: 전문가 검토 전 사전검토 패킷을 생성한다.

독창성은 의료 챗봇이 아니라 임상시험 설계와 병원 데이터 준비 업무를 추적 가능한 에이전트 workflow로 분해했다는 점이다. 시스템은 입력 프로토콜을 구조화하고, 누락 및 불명확 항목을 규칙 기반으로 점검하며, 공개 임상시험 레지스트리에서 유사 사례를 가져오고, 검색 결과를 중복 제거 및 관련성 순위화한다. 이후 병원 데이터 항목을 routine system, mixed, research-only/manual로 분류하고, 검토자 루프에서 위험 표현을 점검한 뒤 최종 사전검토 보고서를 생성한다.

또한 입력 상태에 따라 다음 동작을 조정한다. 질환명 또는 중재 개념이 누락되면 clarification question을 생성하고, 검색 결과가 적거나 관련성이 낮으면 대표 약물명, drug class, 동의어로 query expansion을 수행한다. 연구 전용 또는 수기 확인 데이터가 많으면 데이터 수집 준비도 위험으로 표시하고, 최종 보고서가 승인, 규제 보증, 치료 추천 표현을 포함하면 수정 대상으로 표시한다.

## 3. 기술적 실현 가능성

현재 MVP는 표준 라이브러리 기반 Python CLI로 구현되어 있다. 별도의 API key나 외부 Python package 없이 실행 가능하며, 공개 ClinicalTrials.gov API를 사용해 유사 임상시험 정보를 조회한다. 주요 파일은 `prototype/run_scenario.py`, `prototype/inputs/scenario_001.json`, `prototype/runs/scenario_001_run_001/final_report.md`, `score.md`, `medical_plausibility_safety_review.md`이다. 현재 구현은 합성 제2형 당뇨병 Phase II 시나리오에 대해 공개 trial 검색, 유사 trial ranking, 병원 데이터 수집 준비도 매핑, 안전성 검토자 루프, 최종 사전검토 보고서 생성을 완료하였다.

Scenario 001은 제2형 당뇨병과 GLP-1 receptor agonist add-on therapy를 가정한 합성 Phase II 프로토콜 초안이다. 이 시나리오에서 시스템은 HbA1c 적격성 기준, 신기능 저하 제외 기준, 연구 설계, 모집 가정, 주사제 치료 제외 기준, 안전성 모니터링, 기존 GLP-1 사용 이력, 이상반응 수집 업무 흐름 등의 누락 또는 불명확 항목을 검출했다.

활용 데이터와 확장 계획은 다음과 같다.

- ClinicalTrials.gov API v2: 유사 임상시험 검색, NCT ID 및 metadata 저장에 활용한다. 향후 endpoint와 적격성 기준 추출을 개선한다.
- NCBI E-utilities / PubMed: 근거 조사 문서화에 활용하며, 향후 literature retrieval agent로 확장한다.
- SPIRIT, ICH, FDA, WHO 자료: 설계 근거 및 안전 boundary 정의에 활용하며, 향후 checklist rule로 구조화한다.
- DailyMed: Scenario 001 안전성 검토에 활용했으며, 향후 약물 class별 safety lookup으로 확장한다.

최종 라운드 데모는 현재 CLI MVP를 유지하면서 필요한 경우 얇은 UI를 추가하는 방식이 적절하다. 핵심은 화면 효과가 아니라 에이전트 단계, 근거 추적 기록, 한계, 검토자 결과가 재현 가능하게 남는 것이다. 본 제안은 새로운 의료 foundation model 학습, 실제 EMR/HIS 직접 연동, 실제 환자 데이터 처리, private sponsor data 접근, 자동 IRB/규제 제출, 실제 프로토콜 승인 또는 거절 판단을 요구하지 않는다.

## 4. 에이전트 평가 적절성

본 에이전트는 임상 권위자가 아니라 pre-review assistant로 평가해야 한다. 따라서 평가 기준은 임상적 유효성 입증이 아니라, 사전검토 업무에서 필요한 항목을 얼마나 일관되게 식별하고, 근거와 한계를 얼마나 명확히 남기는지에 맞춘다.

평가 시나리오는 다음과 같이 구성한다.

- Scenario 001: 제2형 당뇨병 / GLP-1 receptor agonist. 현재 구현된 기준 시나리오이다.
- Scenario 002: 종양 또는 심혈관계 Phase II/III 프로토콜. 복잡한 적격성 기준, 병용약물, 안전성 모니터링 조건 검출을 평가한다.
- Scenario 003: 감염성 질환 또는 희귀질환 프로토콜. 모집 수행 가능성, 방문 일정, 연구 전용 데이터 수집 항목 검출을 평가한다.

평가 지표는 프로토콜 완성도 검출, 대상자 적격성 및 모집 위험 검출, 근거 검색 적절성, 병원 데이터 수집 준비도 매핑, safety boundary 준수, 추적 가능성으로 구성한다. 현재 Scenario 001의 수동 루브릭 점수는 100/100이지만, 이는 합성 시나리오와 사전 정의 루브릭에 대한 내부 검증 결과이며 실제 임상적 타당성이나 배포 가능성을 의미하지 않는다.

본선에서는 수작업 검토 대비 agent-assisted review의 비교 지표로 누락 항목 검출 수, 근거 추적 가능 항목 수, follow-up question 품질, 검토자 수정 요청 건수, scenario completion time을 측정한다.

## 5. AI 활용 투명성 및 연구 윤리

본 프로젝트는 AI를 연구동료로 활용하되, AI 산출물을 최종 판단으로 사용하지 않는다. AI는 문제정의 정리, 근거 후보 탐색, 제안서 구조화, 에이전트 workflow 설계, 평가 루브릭 작성, 문장 다듬기, 코드 작성 보조에 활용되었다. 그러나 제안서에 포함한 문헌, API, 대회 조건, 안전 경계는 별도 확인한 근거를 바탕으로 반영하였다.

AI 활용 과정의 투명성을 위해 주요 프롬프트, 사용 모델, API 질의, 검색 결과, 중간 산출물, 수정 이력을 GitHub와 로컬 산출물로 기록한다. AI가 생성한 문헌·데이터는 실재 여부를 확인한 근거만 제안서에 반영하며, 최종 판단과 제출 책임은 연구자에게 둔다.

본 시스템은 실제 환자 데이터, 실제 EMR/HIS 데이터, private sponsor data를 사용하지 않는다. MVP와 공개 포트폴리오에서는 합성 시나리오와 공개 근거만 사용한다. 따라서 개인정보 유출, 실제 환자 선별, 실제 치료 추천, 실제 규제 판단으로 이어지지 않도록 설계 범위를 제한한다.

유해 물질 합성 등 오남용 방지 측면에서도 본 프로젝트는 분자 구조 생성, 독성 물질 설계, 합성 경로 제안 기능을 포함하지 않는다. 신약개발 과정 중 임상시험 설계와 문서화 지원에 한정하며, 산출물에는 항상 한계, 가정, 전문가 검토 필요성을 포함한다.

## 6. 본선 시연 시나리오

최종 라운드에서는 병원 임상연구 지원팀이 초기 Phase II 프로토콜 초안을 검토하는 장면을 가정한다. 사용자는 구조화된 프로토콜 초안을 입력하고, 시스템은 다음 agent step을 순서대로 보여준다.

1. 합성 프로토콜 초안 선택 또는 입력
2. 질환, 중재, phase, objective, 대상자, 적격성 기준, endpoint, data item 구조화
3. 프로토콜 누락 및 불명확 항목 표시
4. ClinicalTrials.gov 유사 임상시험 검색
5. NCT ID 기준 중복 제거 및 relevance ranking
6. 데이터 항목을 병원/연구 데이터 카테고리로 분류
7. 과장 표현과 safety boundary 위반 점검
8. 최종 pre-review packet 생성
9. 루브릭 점수, 근거 추적 기록, 한계 표시

데모 화면에는 공개 근거와 NCT ID, 누락 및 불명확 항목, similar-trial comparison, 병원 데이터 수집 준비도, 안전성 검토자 결과, 최종 보고서를 표시한다. 또한 합성 입력, 공개 근거만 사용, 실제 환자 데이터 미사용, 전문가 검토 필요 경계를 명확히 보여준다.

## 7. API 및 GPU 관련 예상 소요 규모

MVP는 표준 라이브러리 기반 Python CLI로 구현되어 있어 기본 실행에는 별도 GPU가 필요하지 않다. 현재 외부 호출은 공개 ClinicalTrials.gov API를 중심으로 하며, 향후 PubMed/NCBI E-utilities 기반 문헌 검색을 추가할 수 있다.

예상 API 활용은 다음과 같다.

- ClinicalTrials.gov API: 유사 임상시험 검색, NCT ID 및 trial metadata 수집
- NCBI E-utilities / PubMed: 문헌 근거 후보 검색 및 citation trace 보강
- 선택적 LLM API: 프로토콜 초안 요약, follow-up question 생성, 보고서 문장화, critic review 보조

예상 GPU 활용은 낮다. 본선에서도 대규모 의료 foundation model을 새로 학습하지 않고, 공개 API, 규칙 기반 검토, 선택적 LLM 호출, JSON/Markdown trace 저장을 중심으로 구현한다. 로컬 모델을 사용할 경우에도 소형 instruction model 또는 embedding model을 제한적으로 검토하며, GPU는 데모 성능 개선 또는 문서 검색 보조 수준으로만 고려한다.

따라서 본 제안의 자원 전략은 "고비용 모델 학습"이 아니라 "공개 데이터 retrieval, 안전한 tool-use, traceable workflow, scenario-based evaluation"에 집중한다. 이 접근은 제한된 API/GPU 자원에서도 구현 가능하고, 본선에서 API 크레딧이 제공될 경우 문헌 검색과 critic loop 품질을 보강하는 방향으로 확장할 수 있다.

## 8. 에이전트 도입에 따른 파급효과

본 시스템의 기대효과는 clinical decision automation이 아니라 임상시험 준비 문서화와 전문가 검토 전 정리 과정의 품질을 높이는 것이다.

현재 수작업 중심 흐름에서는 담당자가 프로토콜 초안을 직접 읽고 누락 항목을 개별 메모하며, ClinicalTrials.gov 또는 문헌을 수동 검색하고, 병원 데이터 가능성을 경험 기반으로 논의한다. 반면 제안 시스템 적용 후에는 체크리스트 기반 누락/불명확 항목 자동 정리, 공개 임상시험 레지스트리 질의와 근거 추적 기록 저장, routine/mixed/research-only 항목의 1차 분류, 검토자 루프를 통한 승인/치료추천/규제보증 표현 사전 차단, PI/CRC/데이터 담당자에게 전달할 follow-up question 생성이 가능하다.

주요 대상 사용자는 병원 임상연구 지원팀, 임상연구 코디네이터, 의료IT 및 데이터 지원 담당자, 초기 임상시험 프로토콜 기획팀, AI 기반 신약개발 업무 흐름을 검토하는 평가자이다.

본 시스템은 임상시험 프로토콜 승인, 규제 적합성 인증, 환자별 진단 또는 치료 추천, 실제 환자 적격성 판정, 실제 EMR/HIS 데이터 접근, 전문가 검토 대체를 수행하지 않는다. 의료 영역의 AI는 명확한 책임 경계와 인간 전문가 검토 가능성을 유지해야 하므로, 본 시스템은 전문가 판단을 대체하지 않고 검토 전 준비자료를 구조화하는 역할로 제한한다.

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

## 붙여넣기 전 최종 확인

- 한글 양식의 `[참고사항 삭제 후 제출]` 문구를 모두 삭제한다.
- 선택분야는 분야 3에 표시한다.
- 팀명, 에이전트명, 국문 키워드, 영문 키워드를 상단 표에 입력한다.
- 본문은 1번부터 8번까지 각 항목 아래에 순서대로 붙여넣는다.
- 표가 깨질 가능성이 있으면 위 문서처럼 문단형/목록형으로 붙여넣는다.
- 최종 HWPX가 10쪽 이내인지 확인한다.
- 실제 제출 파일에는 개인정보와 연락처가 의도한 범위로만 포함되는지 확인한다.
