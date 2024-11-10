#!/bin/bash
sed -i "s/Dernière mise à jour : .*/Dernière mise à jour : $(date +'%d %B %Y')/" PROJECT_SUMMARY.md
