param([string]$group = "newGroup", [string]$file = "computer_group_members.txt", [string]$user = "wz3264", [String]$password = ""
#
# Created by John Singer, 2.9.15
# If anyone chooses to use this code, please credit it's creator, above.
#
#add-type @"
#     using System.Net;
#     using System.Security.Cryptography.X509Certificates;
#     public class TrustAllCertsPolicy : ICertificatePolicy {
#         public bool CheckValidationResult(
#             ServicePoint srvPoint, X509Certificate certificate,
#             WebRequest request, int certificateProblem) {
#             return true;
#         }
#     }
# "@ 
#[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy

# When invoked as the main program, figure out the cmdline parms, assign them to variables, 
# handle usage & help, and go get the prototype XML & names of the group-members from the 
# cmdline filename

    try {
        if ($group -eq "" -or $file -eq "") {
            write-debug "group: $group"
            Write-Debug "file: $file"
            exit -1
            }

        if ($user -eq "" -or $password -eq "") {
            write-debug "user: $user"
            Write-Debug "password: $password"
            exit -2
           }

# Using the endpoint names from the cmdline filename, substitute them into multiple copies 
# of the following 'stanza', leaving result in el
        $stanza = '<SearchComponentPropertyReference PropertyName="Computer Name" Comparison="Contains"><SearchText>%%computer</SearchText><Relevance>exists (computer name) whose (it as string as lowercase contains "%%computer" as lowercase)</Relevance></SearchComponentPropertyReference>'
        $el = ""
        $lines = Get-Content $file

        foreach ($computerName in $lines)
        {
             $el += $stanza.Replace("%%computer", $computerName.ToLower())
        }
# With the prototype XML from the indicated file, substitute the groupname, and multiple 
# 'stanzas', from above into the new-XML string
        $basexml = Get-Content ".\protoComputerGroup.xml"
        $newXml = $basexml.Replace('%%groupname', $group)
        $newXml = $newXml.Replace("%%miracle_happens_here", $el)

# If there are no cmdline arguments for username/password, just output the generated XML 
# to the console, otherwise 'push' group into IEM.
        if (-not $user -or -not $password) {
            write-host "\n", $newXml
            exit 0
            }

# Create variables to store the values consumed by the Invoke-WebRequest command.
#
        $username = $user
	    $b1a = "adhaytem0a."
	    $b1b = "ad."
	    $b2 = "csueast"
	    $b3 = "bay.edu"
        $baseurl = "https://" + $b1a + $b1b + $b2 + $b3 + ":52311/api"

        $EncodedAuthorization = [System.Text.Encoding]::UTF8.GetBytes($username + ':' + $password)
        $EncodedPassword = [System.Convert]::ToBase64String($EncodedAuthorization)
        $headers = @{"Authorization"="Basic $($EncodedPassword)"}

        $url = $baseurl + '/login'
        $r1 = Invoke-WebRequest -Uri $url -Method GET -Headers $headers -SkipCertificateCheck

        Write-Warning "----->>>>> Rest call to $($url) was $($r1.StatusDescription)"

# Having 'logged in', push the request to create a computergroup for the indicated operator.
#
        if ($r1.StatusCode -eq 200) {
            $url = $baseurl + '/computergroups/master'

# The next line uses the Invoke-WebRequest cmdlet from v2.0;  The result 
#     comes back as a string.
            $r2 = Invoke-WebRequest -Uri $url -Method POST -Headers $headers -Body $newXml -SkipCertificateCheck

# You could have used the Invoke-RestMethod cmdlet from v3.0, but if you do
#     the result comes back as a parsed XMl-structure, so you'd have to extract data from that:
#    $r2 = Invoke-RestMethod -Uri $url -Method GET -Headers $headers

            if ($r2.StatusCode -eq 200) {
                Write-Warning "Returned result was: $($r2.Content)" }
            else {
                Write-Warning "Error on action-request: $($r2.status)" }
            }
        }
    catch {
        write-host "Error detected"
        echo $_.Exception|format-list -force
        }
