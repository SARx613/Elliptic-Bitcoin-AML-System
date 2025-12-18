# control cd command behavior
alias cd..='cd ..'
alias ..='cd ..'
alias ...='cd ../../../'
alias ....='cd ../../../../'
alias .....='cd ../../../../'
alias .4='cd ../../../../'
alias .5='cd ../../../../..'
alias ll='ls -alsh'


# handy short cuts #
alias h='history'
alias j='jobs -l'

# vim stuff 
alias vi=vim
alias svi='sudo vi'
alias vis='vim "+set si"'
alias edit='vim'

# quickly list all TCP/UDP port on your server
alias ports='netstat -tulanp'

# shortcut  for iptables 
alias ipt='sudo /sbin/iptables'
alias iptlist='sudo /sbin/iptables -L -n -v --line-numbers'
alias iptlistin='sudo /sbin/iptables -L INPUT -n -v --line-numbers'
alias iptlistout='sudo /sbin/iptables -L OUTPUT -n -v --line-numbers'
alias iptlistfw='sudo /sbin/iptables -L FORWARD -n -v --line-numbers'
alias firewall=iptlist


# update on one command
alias update='sudo apt-get update && sudo apt-get upgrade'
alias apt-get="sudo apt-get"
alias updatey="sudo apt-get --yes"

# become root 
alias root='sudo -i'
alias su='sudo -i'

#
# system memory, cpu usage, and gpu memory info quickly
#

# pass options to free 
alias meminfo='free -m -l -t' 
# get top process eating memory
alias psmem='ps auxf | sort -nr -k 4'
alias psmem10='ps auxf | sort -nr -k 4 | head -10'
# get top process eating cpu 
alias pscpu='ps auxf | sort -nr -k 3'
alias pscpu10='ps auxf | sort -nr -k 3 | head -10'
# get server cpu info 
alias cpuinfo='lscpu'
# get GPU ram on desktop / laptop##
alias gpumeminfo='grep -i --color memory /var/log/Xorg.0.log'
# disk usage
alias df='df -H'
alias du='du -ch'
