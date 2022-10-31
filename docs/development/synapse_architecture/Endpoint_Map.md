## Endpoint map to Servlet or Resource
Additional endpoint bits are for potential load-balancing in reverse-proxy, usually(but not always) marked with ⬆️.

| Worker(*or notes*) | Servlet | Endpoint |
| --- | --- | --- |
| user_dir | [`UserDirectorySearchRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/user_directory.py#L32) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/user_directory/search$` |
| media_repository | [`MediaRepositoryResource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/media/v1/media_repository.py#L1049) | `^/_matrix/media/` |
| | [`PurgeMediaCacheRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/admin/media.py#L214) | `^/_synapse/admin/v1/purge_media_cache$` |
| | [`ListMediaInRoom`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/admin/media.py#L195) | `^/_synapse/admin/v1/room/.*/media.*$` |
| | [`QuarantineMediaInRoom`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/admin/media.py#L38) | ⬆️ <sub>^/_synapse/admin/v1/room/.\*/media/quarantine$</sub> |
| | | <sub>*Replaces: ^/_synapse/admin/v1/quarantine_media/.\*$*</sub> |
| | [`UserMediaRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/admin/media.py#L332)| `^/_synapse/admin/v1/user/.*/media.*$` |
| | [`QuarantineMediaByUser`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/admin/media.py#L69) | ⬆️  <sub>^/_synapse/admin/v1/user/.\*/media/quarantine$</sub> |
| | [`DeleteMediaByID`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/admin/media.py#L246) | `^/_synapse/admin/v1/media/.*$` |
| | [`DeleteMediaByDateSize`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/admin/media.py#L276) | ⬆️ <sub>^/_synapse/admin/v1/media/.\*/delete$</sub> |
| | [`QuarantineMediaByID`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/admin/media.py#L96) | ⬆️ <sub>^/_synapse/admin/v1/media/quarantine/.\*$</sub> |
| | [`UnquarantineMediaByID`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/admin/media.py#L125) | ⬆️ <sub>^/_synapse/admin/v1/media/unquarantine/.\*$</sub> |
| | [`ProtectMediaByID`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/admin/media.py#L151) | ⬆️ <sub>^/_synapse/admin/v1/media/protect/.\*$</sub> |
| | [`UnprotectMediaByID`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/admin/media.py#L173) | ⬆️ <sub>^/_synapse/admin/v1/media/unprotect/.\*$</sub> |
| synchrotron | [`SyncRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/sync.py#L52)| `^/_matrix/client/(r0\|v3\|unstable)/sync$` |
| | [`EventStreamRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/events.py#L33)| `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/events$` |
| | [`EventRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/events.py#L78) | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/events/(?P<event_id>[^/]*)$</sub> |
| | [`InitialSyncRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/initial_sync.py#L29) | `^/_matrix/client/(api/v1\|r0\|v3)/initialSync$` |
| | [`RoomInitialSyncRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L719) | *Deprecated:  `^/_matrix/client/(api/v1\|r0\|v3)/rooms/[^/]+/initialSync$`* |
| | <sub>*Note: see [`source`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L1403)*</sub> | ⬆️ <sub>Deprecated: ^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]*)/initialSync$</sub> |
| client_reader | [`PublicRoomListRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L437) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/publicRooms$` |
| | [`JoinedRoomMemberListRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L610) | *Deprecated: `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/.*/joined_members$`* |
| | | *Deprecated: ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/joined_members$</sub>* |
| | | Use: /members?membership=join? instead |
| | [`RoomEventContextServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L831) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/.*/context/.*$` |
| | | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/context/(?P<event_id>[^/]\*)$</sub> |
| | [`RoomMemberListRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L555) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/.*/members$` |
| | | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/members$</sub> |
| | [`RoomStateRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L697) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/.*/state$` |
| | | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/state$</sub> |
| | [`RoomStateEventRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L173) | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/state/(?P<event_type>[^/]\*)$</sub> |
| | | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/state/(?P<event_type>[^/]\*)/(?P<state_key>[^/]\*)$</sub> |
| | [`RoomHierarchyRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L1299) | `^/_matrix/client/v1/rooms/.*/hierarchy$` |
| | | ⬆️ <sub>^/_matrix/client/v1/rooms/(?P<room_id>[^/]*)/hierarchy$"</sub> |
| | [`RelationPaginationServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/relations.py#L34) | `^/_matrix/client/(v1\|unstable)/rooms/.*/relations/` |
| | | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/relations/(?P<parent_id>[^/]\*)(/(?P<relation_type>[^/]\*)(/(?P<event_type>[^/]\*))?)?$</sub> |
| | [`ThreadsServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/relations.py#L84) | `^/_matrix/client/v1/rooms/.*/threads$` |
| | | ⬆️ <sub>^/_matrix/client/v1/rooms/(?P<room_id>[^/]\*)/threads</sub> |
| | [`LoginRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/login.py#L73) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/login$` |
| | [`LoginTokenRequestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/login_token_request.py#L30) | ⬆️ <sub>^/_matrix/client/unstable/org.matrix.msc3882/login/token$</sub> |
| <sub>*Note: no 'api/v1' in source*</sub> | [`ThreepidRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L569) | `^/_matrix/client/(r0\|v3\|unstable)/account/3pid$` |
| | <sub>* Are these(3pid) all deprecated or just this one? See comment [here](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L587)*</sub> | |
| <sub>*Note: no 'api/v1' in source*</sub> | [`EmailThreepidRequestTokenRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L322) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/account/3pid/email/requestToken$</sub> |
| <sub>*Note: no 'api/v1' in source*</sub> | [`MsisdnThreepidRequestTokenRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L399) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/account/3pid/msisdn/requestToken$</sub> |
| <sub>*Note: no 'api/v1' in source*</sub> | [`ThreepidAddRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L629) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/account/3pid/add$</sub> |
| <sub>*Note: no 'api/v1' in source*</sub> | [`ThreepidBindRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L679) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/account/3pid/bind$</sub> |
| <sub>*Note: no 'api/v1' in source*</sub> | [`ThreepidUnbindRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L707) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/account/3pid/unbind$</sub> |
| <sub>*Note: no 'api/v1' in source*</sub> | [`ThreepidDeleteRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L742) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/account/3pid/delete$</sub> |
| <sub>*Note: no 'api/v1' in source*</sub> | [`WhoamiRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L825) | `^/_matrix/client/(r0\|v3\|unstable)/account/whoami$` |
| | [`VersionsRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/versions.py#L35) | `^/_matrix/client/versions$` |
| | [`VoipRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/voip.py#L30) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/voip/turnServer$` |
| | [`RegisterRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/register.py#L396) | `^/_matrix/client/(r0\|v3\|unstable)/register$` |
| | [`EmailRegisterRequestTokenRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/register.py#L72) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/register/email/requestToken$</sub> |
| | [`MsisdnRegisterRequestTokenRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/register.py#L159) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/register/msisdn/requestToken$</sub> |
| | [`UsernameAvailabilityRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/register.py#L305) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/register/available</sub> |
| | [`RegistrationTokenValidityRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/register.py#L352) | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/register/(?P<login_type>[^/]\*)/validity</sub> |
| | [`AuthRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/auth.py#L35) | `^/_matrix/client/(r0\|v3\|unstable)/auth/.*/fallback/web$` |
| | | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/auth/(?P<stagetype>[\w\.]\*)/fallback/web</sub> |
| | [`RoomMessageListRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L631) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/.*/messages$` |
| | | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/messages$</sub>
| | [`RoomEventServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L741) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/.*/event` |
| | | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/event/(?P<event_id>[^/]\*)$</sub> |
| | [`JoinedRoomsRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L1180) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/joined_rooms$` |
| <sup>*Note: no 'api/v1' in source*</sup> | [`RoomAliasListServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L1136) | `^/_matrix/client/(r0\|v3\|unstable/.*)/rooms/.*/aliases` |
| | | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable/.\*)/rooms/(?P<room_id>[^/]\*)/aliases$</sub> |
| | [`SearchRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L1161) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/search$` |
| event_creator | [`RoomRedactEventRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L1027) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/.*/redact` |
| | | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/redact/(?P<event_id>[^/]\*)</sub>
| | [`RoomSendEventRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L316) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/.*/send` |
| | | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/send/(?P<event_type>[^/]\*)</sub>
| | [`RoomMembershipRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L925) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/.*/(join\|invite\|leave\|ban\|unban\|kick)$` |
| | | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/(?P<membership_action>join\|invite\|leave\|ban\|unban\|kick)</sub> |
| | [`JoinRoomAliasServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L379)| `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/join/` |
| | | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/join/(?P<room_id>[^/]\*)</sub>
| | | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/profile/` |
| | [`ProfileRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/profile.py#L143) | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/profile/(?P<user_id>[^/]\*)</sub> |
| | [`ProfileDisplaynameRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/profile.py#L30) | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/profile/(?P<user_id>[^/]\*)/displayname</sub> |
| | [`ProfileAvatarURLRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/profile.py#L87) | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/profile/(?P<user_id>[^/]\*)/avatar_url</sub> |
| | [`RoomBatchSendEventRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room_batch.py#L42) | `^/_matrix/client/(v1\|unstable/org.matrix.msc2716)/rooms/.*/batch_send` |
| | | ⬆️ <sub>^/_matrix/client/unstable/org.matrix.msc2716/rooms/(?P<room_id>[^/]\*)/batch_send$</sub> |
| frontend_proxy | [`KeyUploadServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/app/generic_worker.py#L132) | `^/_matrix/client/(r0\|v3\|unstable)/keys/upload` |
| <sub>*Note: no 'api/v1' in source*</sub> | <sub>*See below in the master process section for the other version of this*</sub> | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/keys/upload(/(?P<device_id>[^/]+))?$</sub> |
| account_data | [`TagListServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/tags.py#L32)| `^/_matrix/client/(r0\|v3\|unstable)/.*/tags` |
| | | ⬆️ <sub>/_matrix/client/(r0\|v3\|unstable)/user/(?P<user_id>[^/]\*)/rooms/(?P<room_id>[^/]\*)/tags</sub> |
| | [`TagServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/tags.py#L56) | ⬆️ <sub>/_matrix/client/(r0\|v3\|unstable)/user/(?P<user_id>[^/]\*)/rooms/(?P<room_id>[^/]\*)/tags/(?P<tag>[^/]\*)</sub> |
| | [`AccountDataServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account_data.py#L32) | `^/_matrix/client/(r0\|v3\|unstable)/.*/account_data` |
| | | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/user/(?P<user_id>[^/]\*)/account_data/(?P<account_data_type>[^/]\*)</sub> |
| | [`RoomAccountDataServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account_data.py#L78) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/user/(?P<user_id>[^/]\*)/rooms/(?P<room_id>[^/]\*)/account_data/(?P<account_data_type>[^/]\*)</sub> |
| presence | | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/presence/` |
| | [`PresenceStatusRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/presence.py#L34) | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/presence/(?P<user_id>[^/]\*)/status</sub> |
| receipts | [`ReceiptRestServlet`]() | `^/_matrix/client/(r0\|v3\|unstable)/rooms/.*/receipt` |
| | | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/receipt/(?P<receipt_type>[^/]\*)/(?P<event_id>[^/]\*)$</sub> |
| | [`ReadMarkerRestServlet`]() | `^/_matrix/client/(r0\|v3\|unstable)/rooms/.*/read_markers` |
| | | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/read_markers$</sub> |
| to_device | [`SendToDeviceRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/sendtodevice.py#L34)| `^/_matrix/client/(r0\|v3\|unstable)/sendToDevice/` |
| | | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/sendToDevice/(?P<message_type>[^/]\*)/(?P<txn_id>[^/]\*)$</sub> |
| typing | [`RoomTypingRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L1079) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/.*/typing` |
| | | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/typing/(?P<user_id>[^/]\*)$</sub> |
| federation_reader | [`FederationEventServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L139) | `^/_matrix/federation/(v1\|v2)/event/` |
| <sub>*Note: most of these are 'v1' by default in source. Exceptions will be noted.*</sub> | | ⬆️ <sub>^/_matrix/federation/v1/event/(?P<event_id>[^/]\*)/?$</sub> |
| | [`FederationStateV1Servlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L153) | `^/_matrix/federation/(v1\|v2)/state/` |
| | | ⬆️ <sub>^/_matrix/federation/v1/state/(?P<room_id>[^/]\*)/?$</sub> |
| | [`FederationStateIdsServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L171) | `^/_matrix/federation/(v1\|v2)/state_ids/` |
| | | ⬆️ <sub>^/_matrix/federation/v1/state_ids/(?P<room_id>[^/]\*)/?$</sub> |
| | [`FederationBackfillServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L188) | `^/_matrix/federation/(v1\|v2)/backfill/` |
| | | ⬆️ <sub>^/_matrix/federation/v1/backfill/(?P<room_id>[^/]\*)/?$</sub> |
| | [`FederationGetMissingEventsServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L556) | `^/_matrix/federation/(v1\|v2)/get_missing_events/` |
| | | ⬆️ <sub>^/_matrix/federation/v1/get_missing_events/(?P<room_id>[^/]\*)$</sub> |
| | [`PublicRoomList`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/__init__.py#L80) | `^/_matrix/federation/v1/publicRooms` |
| | [`FederationQueryServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L247) | `^/_matrix/federation/(v1\|v2)/query/` |
| | | ⬆️ <sub>^/_matrix/federation/v1/query/(?P<query_type>[^/]\*)$</sub> |
| | [`FederationMakeJoinServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L263) | `^/_matrix/federation/(v1\|v2)/make_join/` |
| | | ⬆️ <sub>^/_matrix/federation/v1/make_join/(?P<room_id>[^/]\*)/(?P<user_id>[^/]\*)$</sub> |
| | [`FederationMakeLeaveServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L298) | `^/_matrix/federation/(v1\|v2)/make_leave/` |
| | | ⬆️ <sub>^/_matrix/federation/v1/make_leave/(?P<room_id>[^/]\*)/(?P<user_id>[^/]\*)$</sub> |
| | [`FederationV1SendJoinServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L396) | `^/_matrix/federation/(v1\|v2)/send_join/` |
| | | ⬆️ <sub>^/_matrix/federation/v1/send_join/(?P<room_id>[^/]\*)/(?P<event_id>[^/]\*)$</sub> |
| <sub>*Note: appears to be part of MSC3706, and needs a flag to enable 'partial join'.*</sub> | [`FederationV2SendJoinServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L413) | ⬆️ <sub>^/_matrix/federation/v2/send_join/(?P<room_id>[^/]\*)/(?P<event_id>[^/]\*)$</sub> |
| | [`FederationV1SendLeaveServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L313) | `^/_matrix/federation/(v1\|v2)/send_leave/` |
| | | ⬆️ <sub>^/_matrix/federation/v1/send_leave/(?P<room_id>[^/]\*)/(?P<event_id>[^/]\*)$</sub> |
| <sub>*Only difference between 'v1' and 'v2' was the return result.*</sub> | [`FederationV2SendLeaveServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L328) | ⬆️ <sub>^/_matrix/federation/v2/send_leave/(?P<room_id>[^/]\*)/(?P<event_id>[^/]\*)$</sub> |
| | [`FederationV1InviteServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L450) | `^/_matrix/federation/(v1\|v2)/invite/` |
| | | ⬆️ <sub>^/_matrix/federation/v1/invite/(?P<room_id>[^/]\*)/(?P<event_id>[^/]\*)$</sub> |
| <sub>*Based on comments in code, I think 'v1' is deprecated.*</sub> | [`FederationV2InviteServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L474) | ⬆️ <sub>^/_matrix/federation/v2/invite/(?P<room_id>[^/]\*)/(?P<event_id>[^/]\*)$</sub> |
| <sub>*This was removed in 1.12.0rc1 (2020-03-19), but is still in workers entrypoint*</sub>| | <sub>*Removed: ^/_matrix/federation/(v1\|v2)/query_auth/*</sub> |
| | [`FederationEventAuthServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L382) | `^/_matrix/federation/(v1\|v2)/event_auth/` |
| | | ⬆️ <sub>^/_matrix/federation/v1/event_auth/(?P<room_id>[^/]\*)/(?P<event_id>[^/]\*)$</sub> |
| | [`FederationThirdPartyInviteExchangeServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L510) | `^/_matrix/federation/(v1\|v2)/exchange_third_party_invite/` |
| | | ⬆️ <sub>^/_matrix/federation/v1/exchange_third_party_invite/(?P<room_id>[^/]\*)$</sub> |
| | [`FederationUserDevicesQueryServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L533) | `^/_matrix/federation/(v1\|v2)/user/devices/` |
| | | ⬆️ <sub>^/_matrix/federation/v1/user/devices/(?P<user_id>[^/]\*)$</sub> |
| <sub>*Removed in 1.61*</sub> | | <sub>*Removed: ^/_matrix/federation/(v1\|v2)/get_groups_publicised$*</sub> |
| | [`RemoteKey`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/key/v2/remote_key_resource.py#L40) | `^/_matrix/key/v2/query` |
| | | ⬆️ <sub>^/_matrix/key/v2/query/(?P<server>[^/]\*)(/(?P<key_id>[^/]\*))?$</sub> |
| | [`FederationRoomHierarchyServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L635) | `^/_matrix/federation/v1/hierarchy/` |
| <sub>*Marked safe for workers in docs*</sub> | | ⬆️ <sub>^/_matrix/federation/v1/hierarchy/(?P<room_id>[^/]\*)$</sub> |
| federation_inbound | [`FederationSendServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L71) | `^/_matrix/federation/(v1\|v2)/send/` |
| <sub>*Note: this is only 'v1' in source*</sub> | | ⬆️ <sub>^/_matrix/federation/v1/send/(?P<transaction_id>[^/]\*)/?$</sub> |
| master | [`RoomCreateRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L140) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/createRoom` |
| <sub>*This was labelled in comments as 'no workers'*</sub> | [`RoomForgetRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L895) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/.*/forget`
| | | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/forget</sub> |
| | [`TimestampLookupRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L1243) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable\|.*)/rooms/.*/timestamp_to_event$`
| | *<sub>Note: only 'unstable/org.matrix.msc3030' is described in source</sub>* | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable\|.\*)/rooms/(?P<room_id>[^/]\*)/timestamp_to_event$</sub> |
| | [`RoomSummaryRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room.py#L1334) | `^/_matrix/client/unstable/im.nheko.summary/rooms/.*/summary$` |
| | | ⬆️ <sub>^/_matrix/client/unstable/im.nheko.summary/rooms/(?P<room_identifier>[^/]\*)/summary$</sub> |
| | [`RefreshTokenServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/login.py#L538) | `^/_matrix/client/v1/refresh$` |
| | [`SsoRedirectServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/login.py#L585) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/login/(cas\|sso)/redirect$` |
| | <sub>*check this*</sub> | ⬆️ <sub>^/_matrix/client/(r0\|v3)/login/sso/redirect/(?P<idp_id>[A-Za-z0-9_.~-]+)$</sub> |
| | <sub>*and this, Patrick?*</sub>| ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/login/cas/redirect$</sub> |
| | [`CasTicketServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/login.py#L642) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/login/cas/ticket` |
| <sub>*Note: no 'api/v1' in source*</sub> | [`EmailPasswordRequestTokenRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L66) | `^/_matrix/client/(r0\|v3\|unstable)/account/password/email/requestToken$` |
| <sub>*Note: no 'api/v1' in source*</sub> | [`PasswordRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L140) | `^/_matrix/client/(r0\|v3\|unstable)/account/password$` |
| <sub>*Note: no 'api/v1' in source*</sub> | [`DeactivateAccountRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L276) | `^/_matrix/client/(r0\|v3\|unstable)/account/deactivate$` |
| <sub>*Note: no 'api/v1', 'r0' or 'v3' in source*</sub> | [`AddThreepidEmailSubmitTokenServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L470) | `^/_matrix/client/unstable/add_threepid/email/submit_token$` |
| <sub>*Note: no 'api/v1', 'r0' or 'v3' in source*</sub> | [`AddThreepidMsisdnSubmitTokenServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L528) | `^/_matrix/client/unstable/add_threepid/msisdn/submit_token$` |
| <sub>*Note: no 'api/v1', 'r0' or 'v3' in source*</sub> | [`AccountStatusRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account.py#L849) | `^/_matrix/client/unstable/org.matrix.msc3720/account_status$` |
| <sub>*Note: no 'api/v1' in source*</sub> | [`AccountValidityRenewServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account_validity.py#L33) | `^/_matrix/client/(r0\|v3\|unstable)/account_validity/renew$` |
| | [`AccountValiditySendMailServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/account_validity.py#L76) | `^/_matrix/client/(r0\|v3\|unstable)/account_validity/send_mail$` |
| | [`CapabilitiesRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/capabilities.py#L32) | `^/_matrix/client/(r0\|v3\|unstable)/capabilities$` |
| | [`DevicesRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/devices.py#L40) | `^/_matrix/client/(r0\|v3\|unstable)/devices$` |
| | [`DeviceRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/devices.py#L121) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/devices/(?P<device_id>[^/]\*)$</sub> |
| | [`DeleteDevicesRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/devices.py#L71) | `^/_matrix/client/(r0\|v3\|unstable)/delete_devices` |
| | [`DehydratedDeviceServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/devices.py#L218) | `^/_matrix/client/unstable/org.matrix.msc2697.v2/dehydrated_device` |
| | [`ClaimDehydratedDeviceServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/devices.py#L290) | `^/_matrix/client/unstable/org.matrix.msc2697.v2/dehydrated_device/claim` |
| | | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/directory/room$` |
| | [`ClientDirectoryServer`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/directory.py#L46)| ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/directory/room/(?P<room_alias>[^/]\*)$</sub> |
| | [`ClientDirectoryListServer`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/directory.py#L128) | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/directory/list/room/(?P<room_id>[^/]\*)$</sub> |
| | [`ClientAppserviceDirectoryListServer`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/directory.py#L161) | ⬆️ <sub>^/_matrix/client/(api/v1\|r0\|v3\|unstable)/directory/list/appservice/(?P<network_id>[^/]\*)/(?P<room_id>[^/]\*)$</sub> |
| | [`CreateFilterRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/filter.py#L70) | `^/_matrix/client/(r0\|v3\|unstable)/user/.*/filter` |
| | | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/user/(?P<user_id>[^/]\*)/filter$</sub> |
| | [`GetFilterRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/filter.py#L32) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/user/(?P<user_id>[^/]\*)/filter/(?P<filter_id>[^/]\*)</sub> |
| <sub>*This is the master process version. See above at 'frontend_proxy' for the other implementation used for workers*</sub>| [`KeyUploadServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/keys.py#L40) | `^/_matrix/client/(r0\|v3\|unstable)/keys/upload(/(?P<device_id>[^/]+))?$` |
| | [`KeyQueryServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/keys.py#L118) | `^/_matrix/client/(r0\|v3\|unstable)/keys/query$` |
| | [`KeyChangesServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/keys.py#L185) | `^/_matrix/client/(r0\|v3\|unstable)/keys/changes$` |
| | [`OneTimeKeyServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/keys.py#L225) | `^/_matrix/client/(r0\|v3\|unstable)/keys/claim$` |
| | [`SigningKeyUploadServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/keys.py#L259) | `^/_matrix/client/(v3\|unstable)/keys/device_signing/upload$` |
| | [`SignaturesUploadServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/keys.py#L297) | `^/_matrix/client/(r0\|v3\|unstable)/keys/signatures/upload$` |
| | [`KnockRoomAliasServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/knock.py#L39) | `^/_matrix/client/(r0\|v3\|unstable)/knock` |
| | | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/knock/(?P<room_identifier>[^/]*)</sub> |
| | [`LogoutRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/logout.py#L30) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/logout$` |
| | [`LogoutAllRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/logout.py#L55) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/logout/all$` |
| | [`UserMutualRoomsServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/mutual_rooms.py#L31) | `^/_matrix/client/unstable/uk.half-shot.msc2666/user/mutual_rooms/(?P<user_id>[^/]*)` |
| | [`NotificationsServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/notifications.py#L36) | `^/_matrix/client/(r0\|v3\|unstable)/notifications$` |
| <sub>*Appears to be part of SSO, but not listed in docs*</sub> | [`IdTokenServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/openid.py#L33) | `^/_matrix/client/(r0\|v3\|unstable)/user/(?P<user_id>[^/]*)/openid/request_token` |
| | [`PasswordPolicyServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/password_policy.py#L32) | `^/_matrix/client/(r0\|v3\|unstable)/password_policy$` |
| <sub>*Only GET requests can be serviced by workers*</sub> | [`PushRuleRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/push_rule.py#L41) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/(?P<path>pushrules/.*)$` |
| | [`PushersRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/pusher.py#L38) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/pushers$` |
| | [`PushersSetRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/pusher.py#L67) | `^/_matrix/client/(api/v1\|r0\|v3\|unstable)/pushers/set$` |
| | [`LegacyPushersRemoveRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/pusher.py#L151) | `^/_matrix/client/unstable/pushers/remove$` |
| | [`RegistrationSubmitTokenServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/register.py#L235) | `^/_matrix/client/unstable/registration/(?P<medium>[^/]*)/submit_token$` |
| | [`RendezvousServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/rendezvous.py#L30) | `^/_matrix/client/unstable/org.matrix.msc3886/rendezvous$` |
| | [`ReportEventRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/report_event.py#L33) | `^/_matrix/client/(r0\|v3\|unstable)/rooms/(?P<room_id>[^/]*)/report/(?P<event_id>[^/]*)$` |
| <sub>*Marked safe for workers in docs*</sub> | [`RoomKeysServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room_keys.py#L36) | `^/_matrix/client/(r0\|v3\|unstable)/room_keys/` |
| | | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/room_keys/keys(/(?P<room_id>[^/]+))?(/(?P<session_id>[^/]+))?$</sub> |
| <sub>*Marked safe for workers in docs*</sub> | [`RoomKeysNewVersionServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room_keys.py#L254) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/room_keys/version$</sub> |
| <sub>*Marked safe for workers in docs*</sub> | [`RoomKeysVersionServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room_keys.py#L303) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/room_keys/version(/(?P<version>[^/]+))?$</sub> |
| | [`RoomUpgradeRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/room_upgrade_rest_servlet.py#L38) | `^/_matrix/client/(r0\|v3\|unstable)/rooms/.*/upgrade$` |
| | | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/rooms/(?P<room_id>[^/]\*)/upgrade$</sub> |
| | | `^/_matrix/client/(r0\|v3\|unstable)/thirdparty/` |
| | [`ThirdPartyProtocolsServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/thirdparty.py#L32) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/thirdparty/protocols</sub> |
| | [`ThirdPartyProtocolServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/thirdparty.py#L48) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/thirdparty/protocol/(?P<protocol>[^/]+)$</sub> |
| | [`ThirdPartyUserServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/thirdparty.py#L71) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/thirdparty/user(/(?P<protocol>[^/]+))?$</sub> |
| | [`ThirdPartyLocationServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/thirdparty.py#L95) | ⬆️ <sub>^/_matrix/client/(r0\|v3\|unstable)/thirdparty/location(/(?P<protocol>[^/]+))?$</sub> |
| <sub>*This seems to always return a 403, is this deprecated?*</sub> | [`TokenRefreshRestServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/client/tokenrefresh.py#L29) | `^/_matrix/client/(r0\|v3\|unstable)/tokenrefresh` |
| | [`LocalKey`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/key/v2/local_key_resource.py#L33) | `^/_matrix/key/v2/server(/(?P<key_id>[^/]*))?$` |
| | [`PickIdpResource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/synapse/client/pick_idp.py#L31) | `/_synapse/client/pick_idp` |
| | [`pick_username_resource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/synapse/client/pick_username.py#L39) | `/_synapse/client/pick_username` |
| | [`AvailabilityCheckResource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/synapse/client/pick_username.py#L56) | `/_synapse/client/pick_username/account_details` |
| | [`AccountDetailsResource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/synapse/client/pick_username.py#L72) | `/_synapse/client/pick_username/check` |
| | [`NewUserConsentResource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/synapse/client/new_user_consent.py#L33) | `/_synapse/client/new_user_consent` |
| | [`SsoRegisterResource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/synapse/client/sso_register.py#L30) | `/_synapse/client/sso_register` |
| | [`UnsubscribeResource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/synapse/client/unsubscribe.py#L26) | `/_synapse/client/unsubscribe` |
| | [`OIDCResource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/synapse/client/oidc/__init__.py#L28) | `/_synapse/client/oidc` |
| | [`OIDCCallbackResource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/synapse/client/oidc/callback_resource.py#L27) | `/_synapse/client/oidc/callback` |
| | [`SAML2Resource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/synapse/client/saml2/__init__.py#L29) | `/_synapse/client/saml2` |
| | [`SAML2MetadataResource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/synapse/client/saml2/metadata_resource.py#L26) | `/_synapse/client/saml2/metadata.xml` |
| | [`SAML2ResponseResource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/synapse/client/saml2/response_resource.py#L27) | `/_synapse/client/saml2/authn_response` |
| <sub>*Gets mounted directly by homeserver.py@[L210](https://github.com/matrix-org/synapse/blob/develop/synapse/app/homeserver.py#L210)*</sub> | [`PasswordResetSubmitTokenResource`](https://github.com/matrix-org/synapse/blob/develop/synapse/rest/synapse/client/password_reset.py#L30) | `/_synapse/client/password_reset/email/submit_token` |
| | [`FederationTimestampLookupServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L207) | `^/_matrix/federation/unstable/org.matrix.msc3030/timestamp_to_event/` |
| <sub>*Not worker ready*</sub> | | ⬆️ <sub>^/_matrix/federation/unstable/org.matrix.msc3030/timestamp_to_event/(?P<room_id>[^/]\*)/?$</sub> |
| | [`FederationMakeKnockServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L345) | `^/_matrix/federation/v1/make_knock/` |
| <sub>*Note: not in docs*</sub> | | ⬆️ <sub>^/_matrix/federation/v1/make_knock/(?P<room_id>[^/]\*)/(?P<user_id>[^/]\*)$</sub> |
| | [`FederationV1SendKnockServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L367) | `^/_matrix/federation/v1/send_knock/` |
| <sub>*Note: not in docs*</sub> | | ⬆️ <sub>^/_matrix/federation/v1/send_knock/(?P<room_id>[^/]\*)/(?P<event_id>[^/]\*)$</sub> |
| <sub>*Note: not in docs*</sub> | [`FederationClientKeysQueryServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L524) | `^/_matrix/federation/v1/user/keys/query$` |
| <sub>*Note: not in docs*</sub> | [`FederationClientKeysClaimServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L546) | `^/_matrix/federation/v1/user/keys/claim$` |
| <sub>*Note: not in docs*</sub> | [`On3pidBindServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L581) | `^/_matrix/federation/v1/3pid/onbind$` |
| <sub>*Note: not in docs*</sub> | [`FederationVersionServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L613) | `^/_matrix/federation/v1/version$` |
| | [`RoomComplexityServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L661) | `^/_matrix/federation/unstable/rooms/.*/complexity` |
| <sub>*Note: not in docs*</sub> | | ⬆️ <sub>^/_matrix/federation/unstable/rooms/(?P<room_id>[^/]\*)/complexity$</sub> |
| <sub>*Note: not in docs*</sub> | [`FederationAccountStatusServlet`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/federation.py#L698) | `^/_matrix/federation/unstable/org.matrix.msc3720/query/account_status$` |
| <sub>*Note: not in docs*</sub> | [`OpenIdUserInfo`](https://github.com/matrix-org/synapse/blob/develop/synapse/federation/transport/server/__init__.py#L198) | `^/_matrix/federation/v1/openid/userinfo$` |
