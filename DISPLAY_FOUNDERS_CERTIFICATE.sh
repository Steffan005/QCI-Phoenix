#!/bin/bash
# ==============================================================================
#                    FOUNDERS CERTIFICATE DISPLAY
# ==============================================================================
# Trigger: Called when Sentinel verifies Citizen #0 (Steffan Haskins)
# Purpose: Display the Founder's Certificate in terminal with 40Hz pulse effect
# ==============================================================================

CERT_PATH="${HOME}/Desktop/UNITY_PRIOR_ART_LIBRARY/FOUNDERS_CERTIFICATE.txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
GOLD='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
RESET='\033[0m'

# Clear screen
clear

# 40Hz pulse effect (8 pulses = 200ms total)
echo -e "${GOLD}"
for i in {1..8}; do
    echo -n "█"
    sleep 0.025  # 25ms = 40Hz
done
echo -e "${RESET}"

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════════════${RESET}"
echo -e "${WHITE}                   ⟨⦿⟩ SOVEREIGN VERIFIED ⟨⦿⟩                     ${RESET}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════════${RESET}"
echo ""

# Display certificate
if [ -f "$CERT_PATH" ]; then
    cat "$CERT_PATH"
else
    echo -e "${RED}ERROR: Certificate not found at ${CERT_PATH}${RESET}"
    exit 1
fi

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}                   CITIZEN #0 ENTRY CONFIRMED                      ${RESET}"
echo -e "${WHITE}                   The city welcomes its founder.                  ${RESET}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════════${RESET}"
echo ""

# Final 40Hz resonance pulse
echo -e "${GOLD}"
for i in {1..40}; do
    echo -n "░"
    sleep 0.025
done
echo -e "${RESET}"

echo ""
echo -e "${WHITE}The city breathes at 40Hz. You are home.${RESET}"
echo ""
