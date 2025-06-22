---
applyTo: "**"
---

The venv has been created and activated. 
The library python-telegram-bot is now v 22.1. Your knowledge may not be updated so here is the change log of the library:

22.1

2025-05-15
Breaking Changes

    Drop backward compatibility for user_id in send_gift by updating the order of parameters. Please adapt your code accordingly or use keyword arguments. (#4692 by @Bibo-Joshi)

Deprecations

    This release comes with several deprecations, in line with our stability policy.

    This includes the following:

        Deprecated telegram.constants.StarTransactionsLimit.NANOSTAR_MIN_AMOUNT and telegram.constants.StarTransactionsLimit.NANOSTAR_MAX_AMOUNT. These members will be replaced by telegram.constants.NanostarLimit.MIN_AMOUNT and telegram.constants.NanostarLimit.MAX_AMOUNT.

        Deprecated the class telegram.constants.StarTransactions. Its only member telegram.constants.StarTransactions.NANOSTAR_VALUE will be replaced by telegram.constants.Nanostar.VALUE.

        Bot API 9.0 deprecated BusinessConnection.can_reply in favor of BusinessConnection.rights

        Bot API 9.0 deprecated ChatFullInfo.can_send_gift in favor of ChatFullInfo.accepted_gift_types.

        Bot API 9.0 introduced these new required fields to existing classes:

            TransactionPartnerUser.transaction_type

            ChatFullInfo.accepted_gift_types

        Passing these values as positional arguments is deprecated. We encourage you to use keyword arguments instead, as the the signature will be updated in a future release.

    These deprecations are backward compatible, but we strongly recommend to update your code to use the new members.

    (#4756 by @Bibo-Joshi closes #4754; #4757 by @Bibo-Joshi; #4759 by @Bibo-Joshi; #4763 by @aelkheir; #4766 by @Bibo-Joshi; #4769 by @aelkheir; #4773 by @aelkheir; #4781 by @aelkheir; #4782 by @Bibo-Joshi)

New Features

    Full Support for Bot API 9.0 (#4756 by @Bibo-Joshi closes #4754; #4757 by @Bibo-Joshi; #4759 by @Bibo-Joshi; #4763 by @aelkheir; #4766 by @Bibo-Joshi; #4769 by @aelkheir; #4773 by @aelkheir; #4781 by @aelkheir; #4782 by @Bibo-Joshi)

Bug Fixes

    Ensure execution of Bot.shutdown() even if Bot.get_me() fails in Bot.initialize() (#4733 by @Poolitzer)

    Fix Handling of Defaults for InputPaidMedia (#4761 by @ngrogolev closes #4753)

Other Changes

    Bump Version to v22.1 (#4791 by @Bibo-Joshi)

Documentation

    Documentation Improvements. Among others, add missing Returns field in User.get_profile_photos (#4730 by @Bibo-Joshi; #4740 by @aelkheir)

    Update AUTHORS.rst, Adding @aelkheir to Active Development Team (#4747 by @Bibo-Joshi)

    Clarify Documentation and Type Hints of InputMedia and InputPaidMedia. Note that the media parameter accepts only objects of type str and InputFile. The respective subclasses of Input(Paid)Media each accept a broader range of input type for the media parameter. (#4762 by @Bibo-Joshi)

Internal Changes

    Bump codecov/test-results-action from 1.0.2 to 1.1.0 (#4741 by @dependabot)

    Bump actions/setup-python from 5.4.0 to 5.5.0 (#4742 by @dependabot)

    Bump github/codeql-action from 3.28.10 to 3.28.13 (#4743 by @dependabot)

    Bump astral-sh/setup-uv from 5.3.1 to 5.4.1 (#4744 by @dependabot)

    Bump actions/download-artifact from 4.1.8 to 4.2.1 (#4745 by @dependabot)

    Reenable test_official Blocked by Debug Remnant (#4746 by @aelkheir)

    Bump pre-commit Hooks to Latest Versions (#4748 by @pre-commit-ci)

    Fine-tune chango and release workflows (#4758 by @Bibo-Joshi closes #4720)

    Bump codecov/codecov-action from 5.1.2 to 5.4.2 (#4775 by @dependabot)

    Bump actions/upload-artifact from 4.5.0 to 4.6.2 (#4776 by @dependabot)

    Bump stefanzweifel/git-auto-commit-action from 5.1.0 to 5.2.0 (#4777 by @dependabot)

    Bump github/codeql-action from 3.28.13 to 3.28.16 (#4778 by @dependabot)

    Bump actions/download-artifact from 4.2.1 to 4.3.0 (#4779 by @dependabot)

22.0

2025-03-15
Breaking Changes

    This release removes all functionality that was deprecated in v20.x. This is in line with our stability policy.

    This includes the following changes:

        Removed filters.CHAT (all messages have an associated chat) and filters.StatusUpdate.USER_SHARED (use filters.StatusUpdate.USERS_SHARED instead).

        Removed Defaults.disable_web_page_preview and Defaults.quote. Use Defaults.link_preview_options and Defaults.do_quote instead.

        Removed ApplicationBuilder.(get_updates_)proxy_url and HTTPXRequest.proxy_url. Use ApplicationBuilder.(get_updates_)proxy and HTTPXRequest.proxy instead.

        Removed the *_timeout arguments of Application.run_polling and Updater.start_webhook. Instead, specify the values via ApplicationBuilder.get_updates_*_timeout.

        Removed constants.InlineQueryLimit.MIN_SWITCH_PM_TEXT_LENGTH. Use constants.InlineQueryResultsButtonLimit.MAX_START_PARAMETER_LENGTH instead.

        Removed the argument quote of Message.reply_*. Use do_quote instead.

        Removed the superfluous EncryptedPassportElement.credentials without replacement.

        Changed attribute value of PassportFile.file_date from int to datetime.datetime. Make sure to adjust your code accordingly.

        Changed the attribute value of PassportElementErrors.file_hashes from list to tuple. Make sure to adjust your code accordingly.

        Make BaseRequest.read_timeout an abstract property. If you subclass BaseRequest, you need to implement this property.

        The default value for write_timeout now defaults to DEFAULT_NONE also for bot methods that send media. Previously, it was 20. If you subclass BaseRequest, make sure to use your desired write timeout if RequestData.multipart_data is set.

    (#4671 by @Bibo-Joshi closes #4659)

Documentation

    Add chango As Changelog Management Tool (#4672 by @Bibo-Joshi closes #4321)

Internal Changes

    Bump github/codeql-action from 3.28.8 to 3.28.10 (#4697 by @dependabot)

    Bump srvaroa/labeler from 1.12.0 to 1.13.0 (#4698 by @dependabot)

    Bump astral-sh/setup-uv from 5.2.2 to 5.3.1 (#4699 by @dependabot)

    Bump Bibo-Joshi/chango from 0.3.1 to 0.3.2 (#4700 by @dependabot)

    Bump pypa/gh-action-pypi-publish from 1.12.3 to 1.12.4 (#4701 by @dependabot)

    Bump pytest from 8.3.4 to 8.3.5 (#4709 by @dependabot)

    Bump sphinx from 8.1.3 to 8.2.3 (#4710 by @dependabot)

    Bump Bibo-Joshi/chango from 0.3.2 to 0.4.0 (#4712 by @Bibo-Joshi)

    Bump Version to v22.0 (#4719 by @Bibo-Joshi)

Version 21.11.1

Released 2025-03-01

This is the technical changelog for version 21.11. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Documentation Improvements

    Fix ReadTheDocs Build (#4695)

Version 21.11

Released 2025-03-01

This is the technical changelog for version 21.11. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Major Changes and New Features

    Full Support for Bot API 8.3 (#4676 closes #4677, #4682 by aelkheir, #4690 by aelkheir, #4691 by aelkheir)

    Make provider_token Argument Optional (#4689)

    Remove Deprecated InlineQueryResultArticle.hide_url (#4640 closes #4638)

    Accept datetime.timedelta Input in Bot Method Parameters (#4651)

    Extend Customization Support for Bot.base_(file_)url (#4632 closes #3355)

    Support allow_paid_broadcast in AIORateLimiter (#4627 closes #4578)

    Add BaseUpdateProcessor.current_concurrent_updates (#4626 closes #3984)

Minor Changes and Bug Fixes

    Add Bootstrapping Logic to Application.run_* (#4673 closes #4657)

    Fix a Bug in edit_user_star_subscription (#4681 by vavasik800)

    Simplify Handling of Empty Data in TelegramObject.de_json and Friends (#4617 closes #4614)

Documentation Improvements

    Documentation Improvements (#4641)

    Overhaul Admonition Insertion in Documentation (#4462 closes #4414)

Internal Changes

    Stabilize Linkcheck Test (#4693)

    Bump pre-commit Hooks to Latest Versions (#4643)

    Refactor Tests for TelegramObject Classes with Subclasses (#4654 closes #4652)

    Use Fine Grained Permissions for GitHub Actions Workflows (#4668)

Dependency Updates

    Bump actions/setup-python from 5.3.0 to 5.4.0 (#4665)

    Bump dependabot/fetch-metadata from 2.2.0 to 2.3.0 (#4666)

    Bump actions/stale from 9.0.0 to 9.1.0 (#4667)

    Bump astral-sh/setup-uv from 5.1.0 to 5.2.2 (#4664)

    Bump codecov/test-results-action from 1.0.1 to 1.0.2 (#4663)

Version 21.10

Released 2025-01-03

This is the technical changelog for version 21.10. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Major Changes

    Full Support for Bot API 8.2 (#4633)

    Bump apscheduler & Deprecate pytz Support (#4582)

New Features

    Add Parameter pattern to JobQueue.jobs() (#4613 closes #4544)

    Allow Input of Type Sticker for Several Methods (#4616 closes #4580)

Bug Fixes

    Ensure Forward Compatibility of Gift and Gifts (#4634 closes #4637)

Documentation Improvements & Internal Changes

    Use Custom Labels for dependabot PRs (#4621)

    Remove Redundant pylint Suppressions (#4628)

    Update Copyright to 2025 (#4631)

    Refactor Module Structure and Tests for Star Payments Classes (#4615 closes #4593)

    Unify datetime Imports (#4605 by cuevasrja closes #4577)

    Add Static Security Analysis of GitHub Actions Workflows (#4606)

Dependency Updates

    Bump astral-sh/setup-uv from 4.2.0 to 5.1.0 (#4625)

    Bump codecov/codecov-action from 5.1.1 to 5.1.2 (#4622)

    Bump actions/upload-artifact from 4.4.3 to 4.5.0 (#4623)

    Bump github/codeql-action from 3.27.9 to 3.28.0 (#4624)

Version 21.9

Released 2024-12-07

This is the technical changelog for version 21.9. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Major Changes

    Full Support for Bot API 8.1 (#4594 closes #4592)

Minor Changes

    Use MessageLimit.DEEP_LINK_LENGTH in helpers.create_deep_linked_url (#4597 by nemacysts)

    Allow Sequence Input for allowed_updates in Application and Updater Methods (#4589 by nemacysts)

Dependency Updates

    Update aiolimiter requirement from ~=1.1.0 to >=1.1,<1.3 (#4595)

    Bump pytest from 8.3.3 to 8.3.4 (#4596)

    Bump codecov/codecov-action from 4 to 5 (#4585)

    Bump pylint to v3.3.2 to Improve Python 3.13 Support (#4590 by nemacysts)

    Bump srvaroa/labeler from 1.11.1 to 1.12.0 (#4586)

Version 21.8

Released 2024-12-01

This is the technical changelog for version 21.8. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Major Changes

    Full Support for Bot API 8.0 (#4568, #4566 closes #4567, #4572, #4571, #4570, #4576, #4574)

Documentation Improvements

    Documentation Improvements (#4565 by Snehashish06, #4573)

Version 21.7

Released 2024-11-04

This is the technical changelog for version 21.7. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Major Changes

    Full Support for Bot API 7.11 (#4546 closes #4543)

    Add Message.reply_paid_media (#4551)

    Drop Support for Python 3.8 (#4398 by elpekenin)

Minor Changes

    Allow Sequence in Application.add_handlers (#4531 by roast-lord closes #4530)

    Improve Exception Handling in File.download_* (#4542)

    Use Stable Python 3.13 Release in Test Suite (#4535)

Documentation Improvements

    Documentation Improvements (#4536 by Ecode2, #4556)

    Fix Linkcheck Workflow (#4545)

    Use sphinx-build-compatibility to Keep Sphinx Compatibility (#4492)

Internal Changes

    Improve Test Instability Caused by Message Fixtures (#4507)

    Stabilize Some Flaky Tests (#4500)

    Reduce Creation of HTTP Clients in Tests (#4493)

    Update pytest-xdist Usage (#4491)

    Fix Failing Tests by Making Them Independent (#4494)

    Introduce Codecov’s Test Analysis (#4487)

    Maintenance Work on Bot Tests (#4489)

    Introduce conftest.py for File Related Tests (#4488)

    Update Issue Templates to Use Issue Types (#4553)

    Update Automation to Label Changes (#4552)

Dependency Updates

    Bump srvaroa/labeler from 1.11.0 to 1.11.1 (#4549)

    Bump sphinx from 8.0.2 to 8.1.3 (#4532)

    Bump sphinxcontrib-mermaid from 0.9.2 to 1.0.0 (#4529)

    Bump srvaroa/labeler from 1.10.1 to 1.11.0 (#4509)

    Bump Bibo-Joshi/pyright-type-completeness from 1.0.0 to 1.0.1 (#4510)

Version 21.6

Released 2024-09-19

This is the technical changelog for version 21.6. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
New Features

    Full Support for Bot API 7.10 (#4461 closes #4459, #4460, #4463 by aelkheir, #4464)

    Add Parameter httpx_kwargs to HTTPXRequest (#4451 closes #4424)

Minor Changes

    Improve Type Completeness (#4466)

Internal Changes

    Update Python 3.13 Test Suite to RC2 (#4471)

    Enforce the offline_bot Fixture in Test*WithoutRequest (#4465)

    Make Tests for telegram.ext Independent of Networking (#4454)

    Rename Testing Base Classes (#4453)

Dependency Updates

    Bump pytest from 8.3.2 to 8.3.3 (#4475)

Version 21.5

Released 2024-09-01

This is the technical changelog for version 21.5. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Major Changes

    Full Support for Bot API 7.9 (#4429)

    Full Support for Bot API 7.8 (#4408)

New Features

    Add MessageEntity.shift_entities and MessageEntity.concatenate (#4376 closes #4372)

    Add Parameter game_pattern to CallbackQueryHandler (#4353 by jainamoswal closes #4269)

    Add Parameter read_file_handle to InputFile (#4388 closes #4339)

Documentation Improvements

    Bugfix for “Available In” Admonitions (#4413)

    Documentation Improvements (#4400 closes #4446, #4448 by Palaptin)

    Document Return Types of RequestData Members (#4396)

    Add Introductory Paragraphs to Telegram Types Subsections (#4389 by mohdyusuf2312 closes #4380)

    Start Adapting to RTD Addons (#4386)

Minor and Internal Changes

    Remove Surplus Logging from Updater Network Loop (#4432 by MartinHjelmare)

    Add Internal Constants for Encodings (#4378 by elpekenin)

    Improve PyPI Automation (#4375 closes #4373)

    Update Test Suite to New Test Channel Setup (#4435)

    Improve Fixture Usage in test_message.py (#4431 by Palaptin)

    Update Python 3.13 Test Suite to RC1 (#4415)

    Bump ruff and Add New Rules (#4416)

Dependency Updates

    Update cachetools requirement from <5.5.0,>=5.3.3 to >=5.3.3,<5.6.0 (#4437)

    Bump sphinx from 7.4.7 to 8.0.2 and furo from 2024.7.18 to 2024.8.6 (#4412)

    Bump test-summary/action from 2.3 to 2.4 (#4410)

    Bump pytest from 8.2.2 to 8.3.2 (#4403)

    Bump dependabot/fetch-metadata from 2.1.0 to 2.2.0 (#4411)

    Update cachetools requirement from ~=5.3.3 to >=5.3.3,<5.5.0 (#4390)

    Bump sphinx from 7.3.7 to 7.4.7 (#4395)

    Bump furo from 2024.5.6 to 2024.7.18 (#4392)

Version 21.4

Released 2024-07-12

This is the technical changelog for version 21.4. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Major Changes

    Full Support for Bot API 7.5 (#4328, #4316, #4315, #4312 closes #4310, #4311)

    Full Support for Bot API 7.6 (#4333 closes #4331, #4344, #4341, #4334, #4335, #4351, #4342, #4348)

    Full Support for Bot API 7.7 (#4356 closes #4355)

    Drop python-telegram-bot-raw And Switch to pyproject.toml Based Packaging (#4288 closes #4129 and #4296)

    Deprecate Inclusion of successful_payment in Message.effective_attachment (#4365 closes #4350)

New Features

    Add Support for Python 3.13 Beta (#4253)

    Add filters.PAID_MEDIA (#4357)

    Log Received Data on Deserialization Errors (#4304)

    Add MessageEntity.adjust_message_entities_to_utf_16 Utility Function (#4323 by Antares0982 closes #4319)

    Make Argument bot of TelegramObject.de_json Optional (#4320)

Documentation Improvements

    Documentation Improvements (#4303 closes #4301)

    Restructure Readme (#4362)

    Fix Link-Check Workflow (#4332)

Internal Changes

    Automate PyPI Releases (#4364 closes #4318)

    Add mise-en-place to .gitignore (#4300)

    Use a Composite Action for Testing Type Completeness (#4367)

    Stabilize Some Concurrency Usages in Test Suite (#4360)

    Add a Test Case for MenuButton (#4363)

    Extend SuccessfulPayment Test (#4349)

    Small Fixes for test_stars.py (#4347)

    Use Python 3.13 Beta 3 in Test Suite (#4336)

Dependency Updates

    Bump ruff and Add New Rules (#4329)

    Bump pre-commit Hooks to Latest Versions (#4337)

    Add Lower Bound for flaky Dependency (#4322 by Palaptin)

    Bump pytest from 8.2.1 to 8.2.2 (#4294)

Version 21.3

Released 2024-06-07

This is the technical changelog for version 21.3. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Major Changes

    Full Support for Bot API 7.4 (#4286, #4276 closes #4275, #4285, #4283, #4280, #4278, #4279)

    Deprecate python-telegram-bot-raw (#4270)

    Remove Functionality Deprecated in Bot API 7.3 (#4266 closes #4244)

New Features

    Add Parameter chat_id to ChatMemberHandler (#4290 by uniquetrij closes #4287)

Documentation Improvements

    Documentation Improvements (#4264 closes #4240)

Internal Changes

    Add setuptools to requirements-dev.txt (#4282)

    Update Settings for pre-commit.ci (#4265)

Dependency Updates

    Bump pytest from 8.2.0 to 8.2.1 (#4272)

Version 21.2

Released 2024-05-20

This is the technical changelog for version 21.2. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Major Changes

    Full Support for Bot API 7.3 (#4246, #4260, #4243, #4248, #4242 closes #4236, #4247 by aelkheir)

    Remove Functionality Deprecated by Bot API 7.2 (#4245)

New Features

    Add Version to PTBDeprecationWarning (#4262 closes #4261)

    Handle Exceptions in building CallbackContext (#4222)

Bug Fixes

    Call Application.post_stop Only if Application.stop was called (#4211 closes #4210)

    Handle SystemExit raised in Handlers (#4157 closes #4155 and #4156)

    Make Birthdate.to_date Return a datetime.date Object (#4251)

Documentation Improvements

    Documentation Improvements (#4217)

Internal Changes

    Add New Rules to ruff Config (#4250)

    Adapt Test Suite to Changes in Error Messages (#4238)

Dependency Updates

    Bump furo from 2024.4.27 to 2024.5.6 (#4252)

    pre-commit autoupdate (#4239)

    Bump pytest from 8.1.1 to 8.2.0 (#4231)

    Bump dependabot/fetch-metadata from 2.0.0 to 2.1.0 (#4228)

    Bump pytest-asyncio from 0.21.1 to 0.21.2 (#4232)

    Bump pytest-xdist from 3.6.0 to 3.6.1 (#4233)

    Bump furo from 2024.1.29 to 2024.4.27 (#4230)

    Bump srvaroa/labeler from 1.10.0 to 1.10.1 (#4227)

    Bump pytest from 7.4.4 to 8.1.1 (#4218)

    Bump sphinx from 7.2.6 to 7.3.7 (#4215)

    Bump pytest-xdist from 3.5.0 to 3.6.0 (#4215)

Version 21.1.1

Released 2024-04-15

This is the technical changelog for version 21.1.1. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Bug Fixes

    Fix Bug With Parameter message_thread_id of Message.reply_* (#4207 closes #4205)

Minor Changes

    Remove Deprecation Warning in JobQueue.run_daily (#4206 by @Konano)

    Fix Annotation of EncryptedCredentials.decrypted_secret (#4199 by @marinelay closes #4198)

Version 21.1

Released 2024-04-12

This is the technical changelog for version 21.1. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Major Changes

    API 7.2 (#4180 closes #4179 and #4181, #4181)

    Make ChatAdministratorRights/ChatMemberAdministrator.can_*_stories Required (API 7.1) (#4192)

Minor Changes

    Refactor Debug logging in Bot to Improve Type Hinting (#4151 closes #4010)

New Features

    Make Message.reply_* Reply in the Same Topic by Default (#4170 by @aelkheir closes #4139)

    Accept Socket Objects for Webhooks (#4161 closes #4078)

    Add Update.effective_sender (#4168 by @aelkheir closes #4085)

Documentation Improvements

    Documentation Improvements (#4171, #4158 by @teslaedison)

Internal Changes

    Temporarily Mark Tests with get_sticker_set as XFAIL due to API 7.2 Update (#4190)

Dependency Updates

    pre-commit autoupdate (#4184)

    Bump dependabot/fetch-metadata from 1.6.0 to 2.0.0 (#4185)

Version 21.0.1

Released 2024-03-06

This is the technical changelog for version 21.0.1. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Bug Fixes

    Remove docs from Package (#4150)

Version 21.0

Released 2024-03-06

This is the technical changelog for version 21.0. More elaborate release notes can be found in the news channel @pythontelegrambotchannel.
Major Changes

    Remove Functionality Deprecated in API 7.0 (#4114 closes #4099)

    API 7.1 (#4118)

New Features

    Add Parameter media_write_timeout to HTTPXRequest and Method ApplicationBuilder.media_write_timeout (#4120 closes #3864)

    Handle Properties in TelegramObject.__setstate__ (#4134 closes #4111)

Bug Fixes

    Add Missing Slot to Updater (#4130 closes #4127)

Documentation Improvements

    Improve HTML Download of Documentation (#4146 closes #4050)

    Documentation Improvements (#4109, #4116)

    Update Copyright to 2024 (#4121 by @aelkheir closes #4041)

Internal Changes

    Apply pre-commit Checks More Widely (#4135)

    Refactor and Overhaul test_official (#4087 closes #3874)

    Run Unit Tests in PRs on Requirements Changes (#4144)

    Make Updater.stop Independent of CancelledError (#4126)

Dependency Updates

    Relax Upper Bound for httpx Dependency (#4148)

    Bump test-summary/action from 2.2 to 2.3 (#4142)

    Update cachetools requirement from ~=5.3.2 to ~=5.3.3 (#4141)

    Update httpx requirement from ~=0.26.0 to ~=0.27.0 (#4131)

