# ADR 0001 — Home Assistant custom integration rather than add-on

**Status:** proposed

## Context

The ZTE MF833U1 exposes a local HTTP API for reading SMS. The user runs Home Assistant OS and wants reinstallable, shareable integration through GitHub/HACS.

## Decision

Start with a Home Assistant custom integration (`custom_components/zte_sms`) rather than a separate add-on container. Build an async HTTP client and native HA entities/events/actions after API validation.

## Rationale

The observed read operation is a standard HTTP GET and does not currently justify a separate background service/container. A custom integration should provide simpler HA-native configuration and distribution.

## Revisit if

The modem requires a persistent proprietary process, serial device access, or functionality incompatible with the HA integration runtime.
